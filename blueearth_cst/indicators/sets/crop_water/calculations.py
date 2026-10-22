"""Complete-period crop-water screening reductions."""

from __future__ import annotations

from collections.abc import Sequence

import numpy as np
import pandas as pd

from blueearth_cst.indicators.contract import (
    DiagnosticTable,
    EvaluationContext,
    IndicatorDeclaration,
    IndicatorResult,
)
from blueearth_cst.indicators.series import (
    ResponseSeries,
    response_frame,
    validate_responses,
)


def _season(value: object) -> bool:
    """Expected winter or summer."""
    return value in ("winter", "summer")


def _positive(value: object) -> bool:
    """Expected a finite nonnegative daily threshold."""
    return isinstance(value, (int, float)) and np.isfinite(value) and value >= 0


def _fraction(value: object) -> bool:
    """Expected a finite fraction strictly between zero and one."""
    return isinstance(value, (int, float)) and np.isfinite(value) and 0 < value < 1


def _thresholds(value: object) -> bool:
    """Expected location-keyed Qcrit values with explicit baseline provenance."""
    return isinstance(value, dict) and all(
        isinstance(location, str)
        and isinstance(record, dict)
        and set(record)
        == {
            "value",
            "source_id",
            "years",
            "used_summers",
            "excluded_summers",
            "method",
            "units",
        }
        and _positive(record["value"])
        and isinstance(record["source_id"], str)
        and bool(record["source_id"])
        and isinstance(record["years"], list)
        and bool(record["years"])
        and isinstance(record["used_summers"], list)
        and bool(record["used_summers"])
        and isinstance(record["excluded_summers"], list)
        and record["method"] in ("linear p=0.10", "supplied operational")
        and record["units"] == "m3 s-1"
        for location, record in value.items()
    )


def _periods(
    index: pd.DatetimeIndex, season: str
) -> list[tuple[int, pd.Timestamp, pd.Timestamp]]:
    periods = []
    for year in range(index[0].year - 1, index[-1].year + 2):
        if season == "winter":
            start, end = pd.Timestamp(year - 1, 11, 1), pd.Timestamp(year, 5, 31)
        elif season == "summer":
            start, end = pd.Timestamp(year, 5, 1), pd.Timestamp(year, 10, 31)
        else:
            start, end = pd.Timestamp(year - 1, 10, 1), pd.Timestamp(year, 9, 30)
        if start <= index[-1] and end >= index[0]:
            periods.append((year, start, end))
    return periods


def _longest(flags: np.ndarray) -> int:
    best = current = 0
    for flag in flags:
        current = current + 1 if flag else 0
        best = max(best, current)
    return best


def prepare_baseline_qcrit(
    responses: Sequence[ResponseSeries], *, source_id: str, years: Sequence[int]
) -> dict[str, dict]:
    """Prepare fixed Q90-exceedance fallback from complete historical summers."""
    if not source_id or not years or any(type(year) is not int for year in years):
        raise ValueError("Qcrit requires source identity and explicit baseline years")
    validate_responses(responses, evaluated_runs={item.run_id for item in responses})
    if len({item.run_id for item in responses}) != 1 or any(
        (item.variable, item.units, item.time_label, item.timestep.total_seconds())
        != ("q", "m3 s-1", "interval_end", 86400)
        for item in responses
    ):
        raise ValueError("Qcrit baseline requires one daily interval-end Q run")
    frame = response_frame(responses)
    result = {}
    for location in frame:
        pooled, used, excluded = [], [], []
        for year in sorted(set(years)):
            labels = pd.date_range(f"{year}-05-01", f"{year}-10-31", freq="D")
            if labels.isin(frame.index).all():
                values = frame.loc[labels, location].to_numpy(dtype=float)
                if np.isfinite(values).all():
                    pooled.extend(values)
                    used.append(year)
                    continue
            excluded.append(year)
        if not pooled:
            raise ValueError(f"Qcrit has no complete baseline summer at {location}")
        result[location] = {
            "value": float(np.quantile(pooled, 0.10, method="linear")),
            "source_id": source_id,
            "years": list(sorted(set(years))),
            "used_summers": used,
            "excluded_summers": excluded,
            "method": "linear p=0.10",
            "units": "m3 s-1",
        }
    return result


def _calculate(
    indicator: IndicatorDeclaration,
    responses: Sequence[ResponseSeries],
    context: EvaluationContext,
    metric: str,
) -> IndicatorResult:
    parameters = indicator.calculation_parameters
    season = parameters.get("season", "annual")
    frames = {}
    for variable in {item.variable for item in indicator.requirements}:
        selected = [item for item in responses if item.variable == variable]
        key = ("crop-water", context.anchor, tuple(id(item) for item in selected))
        if key not in context.prepared:
            context.prepared[key] = response_frame(selected)
        frames[variable] = context.prepared[key]
    primary = frames[indicator.table_variable]
    if metric == "low_flow":
        missing_thresholds = set(primary) - set(parameters["thresholds"])
        if missing_thresholds:
            raise ValueError(f"missing fixed Qcrit for {sorted(missing_thresholds)}")
    values, rows, summary = {}, [], []
    for location in primary:
        valid_values = []
        counts = {"valid": 0, "invalid": 0, "edge": 0}
        for year, start, end in _periods(primary.index, season):
            block = {
                variable: frame.loc[start:end, location].to_numpy(dtype=float)
                for variable, frame in frames.items()
            }
            observed = len(next(iter(block.values())))
            expected = (end - start).days + 1
            missing = int(
                np.logical_or.reduce(
                    [np.isnan(values) for values in block.values()]
                ).sum()
            )
            status = (
                "edge" if observed != expected else "invalid" if missing else "valid"
            )
            value = np.nan
            eligible = excluded = above_pet = 0
            if status == "valid":
                p = block.get("precip")
                pet = block.get("pet")
                aet = block.get("aet")
                if metric == "climatic_deficit":
                    value = float(np.maximum(pet - p, 0).sum())
                elif metric == "dry_spell":
                    value = float(_longest(p < parameters["dry_day_mm"]))
                elif metric == "low_flow":
                    threshold = parameters["thresholds"].get(location)
                    if threshold is None:
                        raise ValueError(f"missing fixed Qcrit for {location}")
                    value = float((block["q"] < threshold["value"]).sum())
                elif metric == "recharge":
                    value = float(block["gwr"].sum())
                elif metric == "relative_et_deficit":
                    above_pet = int((aet > pet).sum())
                    if pet.sum() > 0:
                        value = float(100 * (1 - aet.sum() / pet.sum()))
                    else:
                        status = "invalid"
                elif metric == "et_limitation_days":
                    above_pet = int((aet > pet).sum())
                    eligible_mask = pet >= parameters["pet_min_mm"]
                    eligible = int(eligible_mask.sum())
                    excluded = observed - eligible
                    if eligible:
                        value = float(
                            (
                                (aet[eligible_mask] / pet[eligible_mask])
                                < parameters["ratio"]
                            ).sum()
                        )
                    else:
                        status = "invalid"
            counts[status] += 1
            if status == "valid":
                valid_values.append(value)
            rows.append(
                {
                    "run_id": responses[0].run_id,
                    "location_id": location,
                    "indicator": indicator.name,
                    "period": year,
                    "start_label": str(start.date()),
                    "end_label": str(end.date()),
                    "value": value,
                    "status": status,
                    "expected_days": expected,
                    "observed_days": observed,
                    "missing_days": missing,
                    "eligible_days": eligible,
                    "low_pet_excluded_days": excluded,
                    "aet_above_pet_days": above_pet,
                }
            )
        values[location] = float(np.mean(valid_values)) if valid_values else np.nan
        summary.append(
            {
                "run_id": responses[0].run_id,
                "location_id": location,
                "indicator": indicator.name,
                "valid_periods": counts["valid"],
                "invalid_periods": counts["invalid"],
                "edge_periods": counts["edge"],
                "effective_threshold": (
                    parameters["thresholds"][location]["value"]
                    if metric == "low_flow" and location in parameters["thresholds"]
                    else parameters.get("dry_day_mm", parameters.get("ratio", np.nan))
                ),
                "qcrit_zero_uninformative": bool(
                    metric == "low_flow"
                    and parameters["thresholds"][location]["value"] == 0
                ),
            }
        )
    return IndicatorResult(
        pd.Series(values),
        diagnostics=(
            DiagnosticTable("period_values", pd.DataFrame(rows)),
            DiagnosticTable("period_summary", pd.DataFrame(summary)),
        ),
    )


def climatic_deficit(indicator, responses, context):
    return _calculate(indicator, responses, context, "climatic_deficit")


def dry_spell(indicator, responses, context):
    return _calculate(indicator, responses, context, "dry_spell")


def low_flow(indicator, responses, context):
    return _calculate(indicator, responses, context, "low_flow")


def recharge(indicator, responses, context):
    return _calculate(indicator, responses, context, "recharge")


def relative_et_deficit(indicator, responses, context):
    return _calculate(indicator, responses, context, "relative_et_deficit")


def et_limitation_days(indicator, responses, context):
    return _calculate(indicator, responses, context, "et_limitation_days")


PARAMETERS = {
    climatic_deficit: {"season": _season},
    dry_spell: {"season": _season, "dry_day_mm": _positive},
    low_flow: {"season": ("summer",), "thresholds": _thresholds},
    recharge: {},
    relative_et_deficit: {"season": _season},
    et_limitation_days: {
        "season": _season,
        "pet_min_mm": _positive,
        "ratio": _fraction,
    },
}


def _qcrit_availability(parameters, locations):
    """Report absent fixed Qcrit; supplied records are validated by ``PARAMETERS``."""
    reason = "missing_parameter:thresholds"
    if not parameters["thresholds"]:
        return [(None, reason)]
    return [
        (location, reason)
        for location in locations or ()
        if location not in parameters["thresholds"]
    ]


AVAILABILITY = {low_flow: _qcrit_availability}
