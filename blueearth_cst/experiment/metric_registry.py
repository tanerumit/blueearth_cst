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
        f"{number:0{width}d}" for number in range(1, len(all_run_ids) + 1)
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
    required = len(all_run_ids) + len(bundles)
    if required > unit_id_capacity:
        raise UnitNamespaceCapacityError(
            f"capacity={unit_id_capacity}, runs={len(all_run_ids)}, bundles={len(bundles)}, "
            f"required={required}, minimum replacement={required}"
        )
    result = [
        UnitIndexRow(run, "run", run) for run in sorted(evaluated_run_ids, key=int)
    ]
    for number, bundle in enumerate(
        sorted(bundles, key=lambda item: (item.bundle_by, item.canonical_key)),
        start=len(all_run_ids) + 1,
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
            UnitIndexRow(f"{number:0{width}d}", "bundle", run)
            for run in sorted(members, key=int)
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


def declarations(tokens: Sequence[str]) -> tuple[MetricDeclaration, ...]:
    """Declare selected metrics using the existing authoritative vocabulary."""
    digest = hashlib.sha256()
    for module in (Path(__file__), Path(md.__file__), Path(tables.__file__)):
        digest.update(module.read_bytes())
    revision = digest.hexdigest()
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
                )
            )
    return tuple(result)


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
    ordered = sorted(first, key=lambda item: int(item.run_id))
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


class InsufficientReturnLevelBlocks(ValueError):
    """Operational screening refused a location before fitting."""


def project_legacy_month(
    metric: MetricDeclaration,
    series: Sequence[ResponseSeries],
    *,
    reference: MonthReference,
    anchor: str,
) -> pd.Series:
    """Preserve P1's pooled Class-C table carrier until P2 changes result grain.

    Per-run scientific values come from reduce_run. This compatibility projection
    preserves the predecessor's pooling order and missing-value weighting exactly.
    It receives neutral responses and contains no native reader or scenario logic.
    """
    validate_requirement(metric, series)
    frames = []
    for run_id in sorted({item.run_id for item in series}, key=int):
        frame = response_frame([item for item in series if item.run_id == run_id])
        frames.append(frame[frame.index.month == reference.month])
    return pd.concat(frames).resample(anchor).mean().mean()


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
    values, evidence = {}, []
    for location in sorted(location_sets[0]):
        members = sorted(
            [item for item in series if item.location_id == location],
            key=lambda item: int(item.run_id),
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
            )
        )
    return pd.Series(values), tuple(evidence)
