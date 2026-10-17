"""Metric declarations and reductions over neutral response series only."""

import hashlib
import math
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

from blueearth_cst.experiment import gev_lmoments
from blueearth_cst.experiment.response_series import (
    ResponseSeries,
    compatible_bundle,
    response_frame,
    validate_responses,
)
from blueearth_cst.shared import indicator_tables as tables
from blueearth_cst.shared import metrics_definition as md

GEV_SCREENING_BLOCK_FLOOR = 10
SCREENING_POLICY_STATUS = "provisional_operational"

# Reviewed run-reduction statistics that have equal-weight realization means.
# A newly declared statistic needs a deliberate group policy before publication.
GROUP_MEAN_STATISTICS = {
    "mean",
    "sum",
    "max",
    "min",
    "q95",
    "Q7day_max",
    "Q7day_min",
    "BaseFlowIndex",
    "wetmonth_mean",
    "drymonth_mean",
    "Q30day_max",
    "Q30day_min",
    "Q90day_min",
    "rise_rate",
    "fall_rate",
}


@dataclass(frozen=True)
class DeclaredBundle:
    """Provider-resolved membership with an explicit canonical grouping key."""

    bundle_by: str
    canonical_key: str
    member_run_ids: tuple[str, ...]


@dataclass(frozen=True)
class UnitIndexRow:
    """One logical row of the future three-column metric-unit index."""

    unit_id: str
    grain: str
    member_run_id: str


def metric_unit_index(
    all_run_ids: Sequence[str],
    evaluated_run_ids: Sequence[str],
    bundles: Sequence[DeclaredBundle],
    *,
    unit_id_capacity: int,
) -> tuple[UnitIndexRow, ...]:
    """Plan logical run/bundle membership without persisting a P2 artifact."""
    from blueearth_cst.experiment.scenario_rows import UnitNamespaceCapacityError

    if type(unit_id_capacity) is not int or unit_id_capacity < 1:
        raise ValueError("unit_id_capacity must be a positive integer")
    width = len(str(unit_id_capacity))
    if tuple(all_run_ids) != tuple(
        f"run_{number:0{width}d}" for number in range(1, len(all_run_ids) + 1)
    ):
        raise ValueError(
            "run ids must preserve the complete collection's order and width"
        )
    if (
        not evaluated_run_ids
        or len(set(evaluated_run_ids)) != len(evaluated_run_ids)
        or not set(evaluated_run_ids) <= set(all_run_ids)
    ):
        raise ValueError("evaluated run ids must be unique collection members")
    keys = [(bundle.bundle_by, bundle.canonical_key) for bundle in bundles]
    if len(set(keys)) != len(keys):
        raise ValueError("duplicate declared grouping key")
    required = max(len(all_run_ids), len(bundles))
    if required > unit_id_capacity:
        raise UnitNamespaceCapacityError(
            f"capacity={unit_id_capacity}, runs={len(all_run_ids)}, bundles={len(bundles)}, "
            f"required={required}, minimum replacement={required}"
        )
    result = [UnitIndexRow(run, "run", run) for run in sorted(evaluated_run_ids)]
    for number, bundle in enumerate(
        sorted(bundles, key=lambda item: (item.bundle_by, item.canonical_key)),
        start=1,
    ):
        members = bundle.member_run_ids
        if (
            not bundle.bundle_by
            or not members
            or len(set(members)) != len(members)
            or not set(members) <= set(evaluated_run_ids)
        ):
            raise ValueError("bundle must name unique evaluated members and a grouping")
        result.extend(
            UnitIndexRow(f"group_{number:0{width}d}", "bundle", run)
            for run in sorted(members)
        )
    return tuple(result)


@dataclass(frozen=True)
class ResponseRequirement:
    """Explicit physical and temporal requirements of a metric."""

    variable: str
    units: str
    timestep_seconds: int = 86400
    time_label: str = "interval_end"
    coverage: str = "entire retained response; preserve partial water years"
    location_grain: str = "location"
    missingness: str = "native NaN; preserve pandas skipna and rolling completeness"
    calendars: tuple[str, ...] = ("standard", "gregorian", "proleptic_gregorian")


@dataclass(frozen=True)
class MetricDeclaration:
    """Meaning of one existing output name, independent of native files."""

    name: str
    statistic: str
    grain: str
    required_responses: ResponseRequirement
    bundle_by: str | None
    reference: str | None
    reference_location: str | None
    return_period: int | None
    blocks_per_return_period: float | None
    implementation_revision: str
    value_validity: str
    group_reduction: str


def _revision() -> str:
    digest = hashlib.sha256()
    for module in (Path(__file__), Path(md.__file__), Path(tables.__file__)):
        digest.update(module.read_bytes())
    return digest.hexdigest()


def _run_declaration(name: str, statistic: str, revision: str) -> MetricDeclaration:
    return MetricDeclaration(
        name=name,
        statistic=statistic,
        grain="run",
        required_responses=ResponseRequirement("q", "m3 s-1"),
        bundle_by=None,
        reference=None,
        reference_location=None,
        return_period=None,
        blocks_per_return_period=None,
        implementation_revision=revision,
        value_validity="finite or native-reduction NaN; refuse infinity; no clipping",
        group_reduction="equal-weight-run-reductions-propagate-nan/1",
    )


def declarations(tokens: Sequence[str]) -> tuple[MetricDeclaration, ...]:
    """Declare selected metrics using the existing authoritative vocabulary."""
    revision = _revision()
    result = []
    for token in tokens:
        if token == "q":
            entries = tables.Q_METRIC_SUFFIXES.items()
            units = "m3 s-1"
        else:
            suffix, reduction = tables.BASIN_METRIC_SUFFIXES[token]
            entries = [(reduction, (suffix, "A"))]
            units = (
                "m3 s-1"
                if token == "overland_flow"
                else ("mm" if token == "snow" else "mm dt-1")
            )
        for statistic, (suffix, kind) in entries:
            period = None
            if kind == "B":
                period = (
                    tables.RETURN_PERIOD_PEAK_YR
                    if statistic == "return_level_max"
                    else tables.RETURN_PERIOD_LOW_YR
                )
            result.append(
                MetricDeclaration(
                    name=f"{token}_{suffix}",
                    statistic=statistic,
                    grain="bundle" if kind == "B" else "run",
                    required_responses=ResponseRequirement(token, units),
                    bundle_by="same_design_point" if kind == "B" else None,
                    reference="unperturbed_runs" if kind == "C" else None,
                    reference_location="class_c_first_gauge" if kind == "C" else None,
                    return_period=period,
                    blocks_per_return_period=1.0 if kind == "B" else None,
                    implementation_revision=revision,
                    value_validity=(
                        "finite required; reject invalid GEV fit; no clipping"
                        if kind == "B"
                        else "finite or native-reduction NaN; refuse infinity; no clipping"
                    ),
                    group_reduction=(
                        "pooled-member-local-blocks/1"
                        if kind == "B"
                        else "equal-weight-run-reductions-propagate-nan/1"
                    ),
                )
            )
    return tuple(result)


def optional_declarations() -> tuple[MetricDeclaration, ...]:
    """Declare the registered q metrics outside the ``current_default`` preset."""
    revision = _revision()
    return tuple(
        _run_declaration(name, statistic, revision)
        for statistic, (name, _, _) in OPTIONAL_Q_CALCULATIONS.items()
    )


#: Shared temporal semantics of every initial method (design v3, P2).
_TEMPORAL = (
    "daily interval_end labels binned directly without shifting to interval "
    "starts; the first label is starttime+step"
)
_PARTIAL = "partial edge blocks retained; each block weighted equally; no duration normalization"


@dataclass(frozen=True)
class MethodContract:
    """One registered calculation method: closed parameters and declared policies."""

    method_id: str
    parameters: dict[str, dict[str, tuple[str | int, ...]]]
    block_assignment: str
    partial_blocks: str
    missingness: str
    validity: str


#: Registered method vocabulary. ``parameters`` maps each response variable to
#: the closed choices of every required parameter; wrappers around existing
#: reductions only, so the whitelists span exactly the registered definitions.
METHODS = {
    "annual_summary/1": MethodContract(
        "annual_summary/1",
        {
            "q": {"statistic": ("mean", "max", "min", "p95")},
            "aet": {"statistic": ("sum",)},
            "gwr": {"statistic": ("sum",)},
            "precip": {"statistic": ("sum",)},
            "snow": {"statistic": ("max",)},
            "overland_flow": {"statistic": ("mean",)},
        },
        f"water-year blocks; {_TEMPORAL}",
        _PARTIAL,
        "sum skips NaN with min_count=0 (an all-missing block sums to 0); mean/max/min "
        "and quantile skip NaN and keep NaN for an all-missing block; the mean over "
        "blocks skips NaN blocks",
        "finite or native-reduction NaN; infinity refused; no clipping",
    ),
    "annual_rolling7_extreme/1": MethodContract(
        "annual_rolling7_extreme/1",
        {"q": {"extreme": ("min", "max")}},
        f"rolling 7-day mean over the whole member, then water-year blocks; {_TEMPORAL}; "
        "windows cross water-year boundaries but never member boundaries",
        _PARTIAL,
        "a rolling window needs seven nonmissing values; block extrema and the mean "
        "over blocks skip NaN",
        "finite or native-reduction NaN; infinity refused; no clipping",
    ),
    "annual_min7_mean_ratio/1": MethodContract(
        "annual_min7_mean_ratio/1",
        {"q": {}},
        f"annual minimum of the rolling 7-day mean over the annual mean; {_TEMPORAL}",
        _PARTIAL,
        "rolling windows need seven nonmissing values; 0/0 gives NaN for that block; "
        "the mean over blocks skips NaN",
        "infinite final value refused (a zero annual mean with a positive minimum); "
        "no clipping",
    ),
    "reference_month_mean/1": MethodContract(
        "reference_month_mean/1",
        {"q": {"which": ("wet", "dry")}},
        "fixed calendar month from pooled monthly SUMS of unperturbed evaluated members "
        "at the first native q location (not the highest/lowest daily mean rate; the "
        "choice depends on month length, member coverage and missingness; first month "
        f"on ties); that month's water-year means averaged; {_TEMPORAL}",
        _PARTIAL,
        "monthly selection sums skip NaN; block means and the mean over blocks skip NaN",
        "finite or native-reduction NaN; infinity refused; no clipping",
    ),
    "pooled_return_level/1": MethodContract(
        "pooled_return_level/1",
        {"q": {"kind": ("annual_max", "rolling7_annual_min")}},
        "member-local annual maxima or rolling 7-day annual minima pooled per design "
        f"group; L-moment GEV; fixed 10/2-year periods; {_TEMPORAL}",
        "partial member-local blocks retained; pooling weights each usable block equally",
        "nonfinite blocks dropped; at least max(ceil(T), 10) usable blocks",
        "finite required; invalid GEV fit and untested probabilities refused; no "
        "clipping; screening is provisional operational policy",
    ),
    "annual_rolling_extreme/1": MethodContract(
        "annual_rolling_extreme/1",
        {"q": {"window": (30, 90), "extreme": ("min", "max")}},
        "rolling WINDOW-day mean over the whole member, then water-year blocks; "
        f"{_TEMPORAL}; windows cross water-year boundaries but never member boundaries",
        _PARTIAL,
        "a rolling window needs WINDOW nonmissing values; block extrema and the "
        "mean over blocks skip NaN",
        "finite or native-reduction NaN; infinity refused; no clipping",
    ),
    "annual_daily_change/1": MethodContract(
        "annual_daily_change/1",
        {"q": {"direction": ("rise", "fall")}},
        "day-to-day differences over the whole member, each in its later day's "
        f"water-year block; {_TEMPORAL}; differences cross water-year boundaries "
        "but never member boundaries",
        _PARTIAL,
        "a difference needs both days nonmissing; zero changes are neither rises "
        "nor falls; a block without one is NaN; the mean over blocks skips NaN",
        "finite or native-reduction NaN; infinity refused; no clipping",
    ),
}

#: Registered definition id -> (method id, parameters, registry statistic).
#: Built from the existing vocabulary so ids and suffixes keep one owner.
_Q_CALCULATIONS = {
    "mean": ("annual_summary/1", {"variable": "q", "statistic": "mean"}),
    "max": ("annual_summary/1", {"variable": "q", "statistic": "max"}),
    "min": ("annual_summary/1", {"variable": "q", "statistic": "min"}),
    "q95": ("annual_summary/1", {"variable": "q", "statistic": "p95"}),
    "Q7day_max": ("annual_rolling7_extreme/1", {"extreme": "max"}),
    "Q7day_min": ("annual_rolling7_extreme/1", {"extreme": "min"}),
    "BaseFlowIndex": ("annual_min7_mean_ratio/1", {}),
    "wetmonth_mean": ("reference_month_mean/1", {"which": "wet"}),
    "drymonth_mean": ("reference_month_mean/1", {"which": "dry"}),
    "return_level_max": ("pooled_return_level/1", {"kind": "annual_max"}),
    "return_level_7day_min": ("pooled_return_level/1", {"kind": "rolling7_annual_min"}),
}
#: Registered q calculations OUTSIDE the ``current_default`` preset: a set file
#: selects them, but ``declarations()`` never expands them, so ``default`` keeps
#: its membership. IHA-style (eflowrisk amax30d, amin30d, amin90d,
#: mean_rate_rise, mean_rate_fall), averaged over water years rather than the
#: eflowrisk median. statistic -> (definition id, method, parameters).
OPTIONAL_Q_CALCULATIONS = {
    "Q30day_max": (
        "q_mean_annual_30day_max",
        "annual_rolling_extreme/1",
        {"window": 30, "extreme": "max"},
    ),
    "Q30day_min": (
        "q_mean_annual_30day_min",
        "annual_rolling_extreme/1",
        {"window": 30, "extreme": "min"},
    ),
    "Q90day_min": (
        "q_mean_annual_90day_min",
        "annual_rolling_extreme/1",
        {"window": 90, "extreme": "min"},
    ),
    "rise_rate": ("q_mean_rise_rate", "annual_daily_change/1", {"direction": "rise"}),
    "fall_rate": ("q_mean_fall_rate", "annual_daily_change/1", {"direction": "fall"}),
}
DEFINITIONS = (
    {
        tables.q_metric_name(statistic): (method, parameters, statistic)
        for statistic, (method, parameters) in _Q_CALCULATIONS.items()
    }
    | {
        tables.basin_metric_name(token): (
            "annual_summary/1",
            {"variable": token, "statistic": reduction},
            reduction,
        )
        for token, (_, reduction) in tables.BASIN_METRIC_SUFFIXES.items()
    }
    | {
        name: (method, parameters, statistic)
        for statistic, (name, method, parameters) in OPTIONAL_Q_CALCULATIONS.items()
    }
)

#: Readable registry title, description and citations per definition. Units and
#: policies come from declarations and METHODS, never from this text.
DEFINITION_TEXT = {
    "q_annual_mean": (
        "Mean annual discharge",
        "Water-year mean discharge averaged over years.",
    ),
    "q_mean_annual_max": (
        "Mean annual maximum discharge",
        "Water-year maximum daily discharge averaged over years.",
    ),
    "q_mean_annual_min": (
        "Mean annual minimum discharge",
        "Water-year minimum daily discharge averaged over years.",
    ),
    "q_mean_annual_p95": (
        "Mean annual 95th-percentile discharge",
        "Water-year 0.95 non-exceedance quantile (a HIGH flow, not conventional low-flow Q95) averaged over years.",
    ),
    "q_mean_annual_7day_max": (
        "Mean annual 7-day maximum discharge",
        "Water-year maximum of the rolling 7-day mean averaged over years.",
    ),
    "q_mean_annual_7day_min": (
        "Mean annual 7-day minimum discharge",
        "Water-year minimum of the rolling 7-day mean averaged over years.",
    ),
    "q_baseflow_index": (
        "Baseflow index",
        "Water-year ratio of the 7-day minimum to the annual mean, averaged over years.",
    ),
    "q_wettest_month_mean": (
        "Wettest-month mean discharge",
        "Mean discharge in the reference wet month (largest pooled monthly sum), averaged over years.",
    ),
    "q_driest_month_mean": (
        "Driest-month mean discharge",
        "Mean discharge in the reference dry month (smallest pooled monthly sum), averaged over years.",
    ),
    "q_return_level_10yr_max": (
        "10-year return level of annual maximum discharge",
        "GEV (L-moments) 10-year level of pooled member-local annual maxima.",
    ),
    "q_return_level_2yr_7day_min": (
        "2-year return level of annual 7-day minimum discharge",
        "GEV (L-moments) 2-year level of pooled member-local annual 7-day minima.",
    ),
    "aet_annual_total": (
        "Mean water-year actual evapotranspiration depth",
        "Daily depths summed per water-year block, averaged with equal block weight.",
    ),
    "gwr_annual_total": (
        "Mean water-year groundwater recharge depth",
        "Daily depths summed per water-year block, averaged with equal block weight.",
    ),
    "precip_annual_total": (
        "Mean water-year precipitation depth",
        "Daily depths summed per water-year block, averaged with equal block weight.",
    ),
    "snow_annual_max": (
        "Mean annual maximum snowpack liquid water depth",
        "Water-year maximum depth averaged over years.",
    ),
    "overland_flow_annual_mean": (
        "Mean annual overland flow",
        "Water-year mean overland flow averaged over years.",
    ),
    "q_mean_annual_30day_max": (
        "Mean annual 30-day maximum discharge",
        "Water-year maximum of the rolling 30-day mean averaged over years.",
    ),
    "q_mean_annual_30day_min": (
        "Mean annual 30-day minimum discharge",
        "Water-year minimum of the rolling 30-day mean averaged over years.",
    ),
    "q_mean_annual_90day_min": (
        "Mean annual 90-day minimum discharge",
        "Water-year minimum of the rolling 90-day mean averaged over years.",
    ),
    "q_mean_rise_rate": (
        "Mean rate of rise",
        "Water-year mean of positive day-to-day discharge changes, averaged over years.",
    ),
    "q_mean_fall_rate": (
        "Mean rate of fall",
        "Water-year mean magnitude of negative day-to-day discharge changes, averaged over years.",
    ),
}
#: Registry citations per definition. Empty until a source the repository
#: actually retains is cited; never filled from memory.
DEFINITION_REFERENCES: dict[str, tuple[str, ...]] = {}
if set(DEFINITION_TEXT) != set(DEFINITIONS):
    raise ValueError("DEFINITION_TEXT must cover exactly the registered definitions")


def output_units(declaration: MetricDeclaration) -> str:
    """Declared output units; never inferred from input units alone."""
    if declaration.statistic == "BaseFlowIndex":
        return "1"
    if declaration.statistic in {"rise_rate", "fall_rate"}:
        return "m3 s-1 d-1"
    if declaration.statistic == "sum":
        # Mean water-year block depth: mm per block, not a duration-normalized rate.
        return "mm"
    return declaration.required_responses.units


def quantity(declaration: MetricDeclaration) -> str:
    """The quantity a value measures, stated for the readable dictionary."""
    if declaration.statistic == "sum":
        return (
            "mean water-year block depth: daily mm dt-1 values summed within each "
            "block and averaged with equal block weight; mean annual depth only for "
            "complete nonmissing blocks; not a duration-normalized rate"
        )
    if declaration.statistic == "BaseFlowIndex":
        return "dimensionless ratio"
    if declaration.statistic in {"rise_rate", "fall_rate"}:
        return "mean over water years of the annual mean day-to-day change magnitude"
    if declaration.grain == "bundle":
        return f"{declaration.return_period}-year return level"
    return "mean over water years of an annual statistic"


def validate_calculation(method: str, parameters) -> tuple[str, dict]:
    """Validate an authored calculation; return its registered definition id.

    Parameters are closed: extras, omissions and values outside the method's
    whitelist are refused, with no implicit numerical defaults.
    """
    contract = METHODS.get(method)
    if contract is None:
        raise ValueError(
            f"unknown indicator method {method!r}; known: {sorted(METHODS)}"
        )
    if not isinstance(parameters, dict):
        raise ValueError(f"{method}: parameters must be a mapping")
    normalized = dict(sorted(parameters.items()))
    for definition, (registered, registered_parameters, _) in DEFINITIONS.items():
        if registered == method and normalized == dict(
            sorted(registered_parameters.items())
        ):
            return definition, normalized
    variables = sorted(contract.parameters)
    raise ValueError(
        f"{method}: unsupported parameters {normalized!r}; required keys and "
        f"choices per variable: { ({v: contract.parameters[v] for v in variables}) }"
    )


def declaration_for(definition: str) -> MetricDeclaration:
    """The authoritative declaration of one registered definition id."""
    if definition not in DEFINITIONS:
        raise ValueError(f"unknown registered indicator definition {definition!r}")
    optional = {item.name: item for item in optional_declarations()}
    if definition in optional:
        return optional[definition]
    token = next(
        token
        for token in ("q", *tables.BASIN_METRIC_SUFFIXES)
        if definition.startswith(f"{token}_")
        and any(item.name == definition for item in declarations([token]))
    )
    return next(item for item in declarations([token]) if item.name == definition)


def block_bins(anchor: str) -> str:
    """How a water-year anchor closes and labels its resample blocks."""
    if anchor.startswith("YS"):
        return "left-closed, left-labelled"
    return "right-closed, right-labelled"


def _block_interval(label: pd.Timestamp, anchor: str):
    """The calendar interval one resample block covers, for its label."""
    offset = pd.tseries.frequencies.to_offset(anchor)
    if anchor.startswith("YS"):
        return label, label + offset
    return label - offset, label


def series_coverage(item: ResponseSeries, anchor: str) -> dict:
    """Immutable per-series block coverage under the resolved water-year anchor.

    Derived from the retained index and missing mask, never from requested
    dates. A complete label block has every expected daily label of its
    Gregorian anchor interval (leap days included); it may still hold NaNs.
    """
    labels = pd.Series(item.missing, index=item.time)
    blocks = []
    for block_label, group in labels.resample(anchor):
        if group.empty:
            continue
        start, end = _block_interval(block_label, anchor)
        expected = int((end - start) / item.timestep)
        observed = len(group)
        missing = int(group.sum())
        blocks.append(
            {
                "block_label": str(block_label.date()),
                "first_label": str(group.index[0].date()),
                "last_label": str(group.index[-1].date()),
                "observed": observed,
                "expected": expected,
                "missing": missing,
                "all_missing": missing == observed,
            }
        )
    return {
        "run_id": item.run_id,
        "variable": item.variable,
        "location_id": item.location_id,
        "calendar": item.calendar,
        "timestep_seconds": int(item.timestep.total_seconds()),
        "time_label": item.time_label,
        "anchor": anchor,
        "block_bins": block_bins(anchor),
        "first_label": str(item.time[0].date()),
        "last_label": str(item.time[-1].date()),
        "blocks": blocks,
        "block_count": len(blocks),
        "complete_label_blocks": sum(b["observed"] == b["expected"] for b in blocks),
        "missing_total": sum(b["missing"] for b in blocks),
        "all_missing_blocks": sum(b["all_missing"] for b in blocks),
    }


def validate_requirement(
    metric: MetricDeclaration, series: Sequence[ResponseSeries]
) -> None:
    """Refuse metadata mismatches before a metric performs any reduction."""
    validate_responses(series, evaluated_runs={item.run_id for item in series})
    requirement = metric.required_responses
    for item in series:
        if (
            item.variable,
            item.units,
            item.timestep.total_seconds(),
            item.time_label,
        ) != (
            requirement.variable,
            requirement.units,
            requirement.timestep_seconds,
            requirement.time_label,
        ):
            raise ValueError(
                f"{metric.name}: incompatible response requirement at {item.key}"
            )


@dataclass(frozen=True)
class MonthReference:
    """Resolved Class-C reference; selection is never repeated per response."""

    run_ids: tuple[str, ...]
    reference_location_id: str
    month: int
    which: str
    counts: tuple[tuple[str, str, str, int, int], ...]
    selection_statistic: str = "monthly sum followed by argmax/argmin"
    tie_rule: str = "first label in ascending calendar-month order"


def resolve_month_reference(
    series: Sequence[ResponseSeries],
    *,
    expected_run_ids: Sequence[str],
    which: str,
) -> MonthReference:
    """Resolve the legacy first-native-gauge rule into an explicit location id."""
    if which not in {"wet", "dry"} or not expected_run_ids:
        raise ValueError(
            "Class-C reference requires nonempty explicit members and wet/dry selection"
        )
    if len(set(expected_run_ids)) != len(expected_run_ids):
        raise ValueError("Class-C reference has duplicate members")
    validate_responses(series, evaluated_runs=set(expected_run_ids))
    if any(
        (item.variable, item.units, item.time_label, item.timestep.total_seconds())
        != ("q", "m3 s-1", "interval_end", 86400)
        for item in series
    ):
        raise ValueError(
            "Class-C reference requires daily interval-end discharge responses"
        )
    if {item.run_id for item in series} != set(expected_run_ids):
        raise ValueError("Class-C reference membership is incomplete")
    locations = [
        {item.location_id for item in series if item.run_id == run}
        for run in expected_run_ids
    ]
    if any(observed != locations[0] for observed in locations):
        raise ValueError("Class-C reference location sets differ")
    for location in locations[0]:
        compatible_bundle([item for item in series if item.location_id == location])
    first = [
        item for item in series if item.variable == "q" and item.location_ordinal == 0
    ]
    if (
        len(first) != len(expected_run_ids)
        or len({item.location_id for item in first}) != 1
    ):
        raise ValueError(
            "Class-C reference needs the same first native q location in every member"
        )
    compatible_bundle(first)
    location = first[0].location_id
    ordered = sorted(first, key=lambda item: item.run_id)
    pooled = pd.concat([pd.Series(item.values, index=item.time) for item in ordered])
    monthly = pooled.groupby(pooled.index.month).sum()
    month = int(monthly.idxmax() if which == "wet" else monthly.idxmin())
    counts = tuple(
        (
            item.run_id,
            str(item.time[0]),
            str(item.time[-1]),
            int(item.time[~item.missing].year.nunique()),
            int(item.time[~item.missing].to_period("M").nunique()),
        )
        for item in ordered
    )
    return MonthReference(
        tuple(item.run_id for item in ordered), location, month, which, counts
    )


def _reduce_optional(frame: pd.DataFrame, statistic: str, anchor: str) -> pd.Series:
    """Evaluate one non-default q calculation (see OPTIONAL_Q_CALCULATIONS)."""
    _, method, parameters = OPTIONAL_Q_CALCULATIONS[statistic]
    if method == "annual_rolling_extreme/1":
        blocks = frame.rolling(parameters["window"]).mean().resample(anchor)
        return getattr(blocks, parameters["extreme"])().mean()
    change = frame.diff()
    if parameters["direction"] == "rise":
        change = change.where(change > 0)
    else:
        change = (-change).where(change < 0)
    return change.resample(anchor).mean().mean()


def reduce_run(
    metric: MetricDeclaration,
    series: Sequence[ResponseSeries],
    *,
    anchor: str,
    reference: MonthReference | None = None,
) -> pd.Series:
    """Evaluate one declared run-grain metric on location-labelled responses."""
    if metric.grain != "run":
        raise ValueError(f"{metric.name}: expected a run-grain declaration")
    validate_requirement(metric, series)
    frame = response_frame(series)
    statistic = metric.statistic
    if metric.reference is not None:
        which = "wet" if statistic == "wetmonth_mean" else "dry"
        if (
            reference is None
            or reference.which != which
            or reference.month not in range(1, 13)
        ):
            raise ValueError(
                f"{metric.name}: explicit resolved month reference required"
            )
        values = (
            frame[frame.index.month == reference.month].resample(anchor).mean().mean()
        )
    elif metric.required_responses.variable != "q":
        values = getattr(frame.resample(anchor), statistic)().mean()
    elif statistic in {"mean", "max", "min"}:
        values = getattr(frame.resample(anchor), statistic)().mean()
    elif statistic == "q95":
        values = frame.resample(anchor).quantile(0.95).mean()
    elif statistic in OPTIONAL_Q_CALCULATIONS:
        values = _reduce_optional(frame, statistic, anchor)
    else:
        reducer = {
            "Q7day_max": md.Q7d_maxyear,
            "Q7day_min": md.Q7d_min,
            "BaseFlowIndex": md.BFI,
        }[statistic]
        values = reducer(frame, anchor)
    if np.isinf(values.to_numpy()).any():
        raise ValueError(f"{metric.name}: infinite metric value")
    return values


def reduce_group_mean(
    metric: MetricDeclaration,
    series: Sequence[ResponseSeries],
    *,
    expected_run_ids: Sequence[str],
    anchor: str,
    reference: MonthReference | None = None,
) -> pd.Series:
    """Average run reductions with equal realization weights and NaN propagation.

    Member length never changes its weight. Class-C reductions use the same
    resolved reference month as their individual-run products. Return levels
    must use reduce_bundle, including for singleton groups.
    """
    if (
        metric.statistic not in GROUP_MEAN_STATISTICS
        or metric.group_reduction != "equal-weight-run-reductions-propagate-nan/1"
    ):
        raise ValueError(f"{metric.name}: no reviewed group mean policy")
    if not expected_run_ids or len(set(expected_run_ids)) != len(expected_run_ids):
        raise ValueError(f"{metric.name}: group needs unique evaluated members")
    if {item.run_id for item in series} != set(expected_run_ids):
        raise ValueError(f"{metric.name}: group membership differs from declaration")
    values = [
        reduce_run(
            metric,
            [item for item in series if item.run_id == run],
            anchor=anchor,
            reference=reference,
        )
        for run in expected_run_ids
    ]
    if any(set(value.index) != set(values[0].index) for value in values):
        raise ValueError(f"{metric.name}: group location sets differ")
    ordered = [value.reindex(values[0].index).to_numpy() for value in values]
    # np.mean deliberately propagates NaN; pandas' default skipna would give
    # invalid members zero weight and change the declared realization mean.
    return pd.Series(np.mean(np.stack(ordered), axis=0), index=values[0].index)


class InsufficientReturnLevelBlocks(ValueError):
    """Operational screening refused a location before fitting."""


class InvalidReturnLevelFit(ValueError):
    """The estimator refused this location; its structured record is attached.

    Only a refusal reaches this exception. An unexpected fault keeps its own
    traceback and propagates, because a fault silently converted into a refusal
    row would be indistinguishable from a location the estimator genuinely
    declined (D3).
    """

    def __init__(self, message: str, *, fit_result=None):
        super().__init__(message)
        self.fit_result = fit_result


class ReturnLevelProbabilityNotCovered(ValueError):
    """A requested probability lies outside the verified benchmark domain (D4).

    This is a configuration and evidence-contract fault, not an estimator
    refusal: it fires before the library is invoked and aborts publication.
    Changing a return period must not silently inherit a bounded declaration,
    so the domain is never clamped, substituted or expanded to accommodate it.
    """


#: Identifiers for the extraction rules D1 preserves, recorded per location so a
#: retained fit says which sampling produced it rather than leaving it implied.
EXTRACTION_POLICY = {
    "return_level_max": "member_local_annual_max/1",
    "return_level_7day_min": "member_local_rolling7_annual_min/1",
}
MISSINGNESS_POLICY = "drop_nonfinite_blocks/1"
PARTIAL_BLOCK_POLICY = "retain_partial_period_blocks/1"


@dataclass(frozen=True)
class ReturnLevelEvidence:
    """Usable-block counts, coverage and the retained fit for one location."""

    location_id: str
    member_counts: tuple[tuple[str, int, str, str], ...]
    total: int
    required: int
    parameters: tuple[float, ...]
    member_count: int = 0
    extraction_policy: str = ""
    missingness_policy: str = MISSINGNESS_POLICY
    partial_block_policy: str = PARTIAL_BLOCK_POLICY
    fit: dict | None = None
    shape_coverage: dict | None = None


def _declared_probabilities(validation) -> list:
    """Read the verified declaration's tested probabilities once per reduction.

    Resolved outside the per-location loop because building the declaration
    reads and re-verifies the whole shipped report; the membership check itself
    still runs before every individual fit.
    """
    from blueearth_cst.experiment import return_level_validation as rlv

    declaration = rlv.build_declaration() if validation is None else validation
    declared = declaration.get("tested_domain", {}).get("probabilities")
    if not isinstance(declared, list):
        raise ReturnLevelProbabilityNotCovered(
            "the retained return-level validation declares no tested probabilities"
        )
    return declared


def _declared_shapes(validation) -> list | None:
    """Read the declaration's tested shape values, or None if it states none.

    Unlike :func:`_declared_probabilities` this never raises. Shape coverage is
    reported, never enforced -- see :func:`_shape_coverage` for why.
    """
    from blueearth_cst.experiment import return_level_validation as rlv

    declaration = rlv.build_declaration() if validation is None else validation
    declared = declaration.get("tested_domain", {}).get("shapes_c")
    return declared if isinstance(declared, list) and declared else None


def _shape_coverage(shape: float, declared: list | None) -> dict | None:
    """Report whether a FITTED shape falls inside the assessed domain (D4).

    This is deliberately **not** a guard, and it is not the shape-shaped twin of
    :func:`_covered_probability`. Two reasons, both structural:

    A probability is a property of the REQUEST, known before any fit, so
    refusing an untested one costs nothing and is unambiguous. A shape is a
    property of the RESULT: it does not exist until the fit does, and at the
    block counts this reduction produces its sampling spread is comparable to
    the width of the tested domain itself. Gating on it would refuse fits whose
    true shape is inside the domain and admit fits whose true shape is outside.

    And a refusal here is not local. ``InvalidReturnLevelFit`` is caught nowhere
    in this package, so one refused fit aborts the whole metric set -- every
    other location, every other metric, including statistics that are fully
    inside the assessed domain. A reporting field costs a consumer nothing and
    keeps that blast radius at zero.

    ``excess`` is recorded alongside the boolean on purpose: a fitted shape just
    outside the tested range is consistent with a true shape inside it, so a
    consumer needs the distance to apply its own threshold rather than trusting
    a bare flag. ``None`` means the declaration states no tested shapes --
    unavailable, not "covered".
    """
    if declared is None:
        return None
    low, high = min(declared), max(declared)
    inside = low <= shape <= high
    return {
        "tested_shapes_c": list(declared),
        "tested_range_c": [low, high],
        "fitted_c": shape,
        "within_tested_range": inside,
        "excess_beyond_tested_range": 0.0
        if inside
        else min(abs(shape - low), abs(shape - high)),
    }


def _covered_probability(probability: float, declared: list) -> None:
    """Refuse a probability the verified benchmark domain does not cover (D4).

    Exact numeric membership, for the fixed .9 and .5 values the declaration
    names. No clamping, substitution or widening.
    """
    if not any(probability == value for value in declared):
        raise ReturnLevelProbabilityNotCovered(
            f"requested probability {probability!r} is outside the verified "
            f"benchmark domain {declared!r}; the declaration is bounded and is "
            "not expanded to cover a changed return period"
        )


def reduce_bundle(
    metric: MetricDeclaration,
    series: Sequence[ResponseSeries],
    *,
    expected_run_ids: Sequence[str],
    anchor: str,
    validation=None,
) -> tuple[pd.Series, tuple[ReturnLevelEvidence, ...]]:
    """Extract blocks within each member, screen and fit without splicing runs.

    `validation` is the verified return-level declaration whose tested domain
    bounds the probabilities that may be requested. The publication path passes
    the declaration retained in its plan; omitting it resolves the shipped one.
    """
    if (
        metric.grain != "bundle"
        or metric.return_period is None
        or metric.blocks_per_return_period is None
    ):
        raise ValueError(
            f"{metric.name}: expected an explicit return-level bundle declaration"
        )
    if not expected_run_ids or len(set(expected_run_ids)) != len(expected_run_ids):
        raise ValueError(f"{metric.name}: bundle needs unique evaluated members")
    if {item.run_id for item in series} != set(expected_run_ids):
        raise ValueError(
            f"{metric.name}: bundle membership differs from declared grouping"
        )
    validate_requirement(metric, series)
    by_run = {
        run_id: [item for item in series if item.run_id == run_id]
        for run_id in expected_run_ids
    }
    location_sets = [
        {item.location_id for item in members} for members in by_run.values()
    ]
    if any(locations != location_sets[0] for locations in location_sets):
        raise ValueError(f"{metric.name}: bundle location sets differ")
    required = max(
        math.ceil(metric.blocks_per_return_period * metric.return_period),
        GEV_SCREENING_BLOCK_FLOOR,
    )
    maximum = metric.statistic == "return_level_max"
    quantile = 1 - 1 / metric.return_period if maximum else 1 / metric.return_period
    declared = _declared_probabilities(validation)
    declared_shapes = _declared_shapes(validation)
    values, evidence = {}, []
    for location in sorted(location_sets[0]):
        members = sorted(
            [item for item in series if item.location_id == location],
            key=lambda item: item.run_id,
        )
        compatible_bundle(members)
        samples, counts = [], []
        for item in members:
            daily = pd.Series(item.values, index=item.time)
            blocks = (
                daily.resample(anchor).max()
                if maximum
                else daily.rolling(7).mean().resample(anchor).min()
            )
            usable = blocks.to_numpy(dtype="float64")
            usable = usable[np.isfinite(usable)]
            samples.append(usable)
            counts.append(
                (item.run_id, len(usable), str(item.time[0]), str(item.time[-1]))
            )
        sample = np.concatenate(samples)
        context = (
            f"metric={metric.name}, unit_members={tuple(expected_run_ids)}, location={location}, "
            f"T={metric.return_period}, required={required}, actual={len(sample)}, per_member={counts}"
        )
        if len(sample) < required:
            raise InsufficientReturnLevelBlocks(context)
        context += (
            f", sample_range={(float(sample.min()), float(sample.max()))}, "
            f"estimator={gev_lmoments.ESTIMATOR_ID}/"
            f"lmoments3-{gev_lmoments.DEPENDENCY_VERSION}, "
            f"implementation_revision={metric.implementation_revision}"
        )
        # A constant sample is no longer screened out here: it reaches the
        # adapter and comes back as a structured invalid_range refusal (D1).
        _covered_probability(quantile, declared)
        result = gev_lmoments.fit_case(sample, (quantile,))
        if not result.accepted:
            raise InvalidReturnLevelFit(
                f"{context}: estimator refused: {', '.join(result.refusal_reasons)}",
                fit_result=result,
            )
        value = result.value(quantile)
        parameters = result.physical_parameters
        values[location] = value
        evidence.append(
            ReturnLevelEvidence(
                location,
                tuple(counts),
                len(sample),
                required,
                tuple(parameters[name] for name in ("c", "loc", "scale")),
                member_count=len(members),
                extraction_policy=EXTRACTION_POLICY[metric.statistic],
                fit=result.record(),
                shape_coverage=_shape_coverage(parameters["c"], declared_shapes),
            )
        )
    return pd.Series(values), tuple(evidence)
