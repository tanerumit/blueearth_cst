"""Neutral metric semantics, explicit references and operational refusals."""

from dataclasses import replace
from datetime import timedelta

import numpy as np
import pandas as pd
import pytest

from blueearth_cst.experiment.export_wflow_results import _return_level_from_blocks
from blueearth_cst.experiment.metric_registry import (
    DeclaredBundle,
    InsufficientReturnLevelBlocks,
    InvalidReturnLevelFit,
    declarations,
    metric_unit_index,
    reduce_bundle,
    reduce_run,
    resolve_month_reference,
)
from blueearth_cst.experiment.response_series import ResponseSeries
from blueearth_cst.experiment.scenario_provider import metric_groups
from blueearth_cst.experiment.scenario_rows import stochastic_rows


def responses():
    times = pd.date_range("2046-01-02", "2054-12-31")
    rng = np.random.default_rng(12)
    result = []
    for run in ("01", "08"):
        for ordinal, location in enumerate(("9", "2")):
            # Native-first gauge peaks in June; lexically first peaks in January.
            values = (
                1
                + rng.random(len(times))
                + np.where(times.month == (6 if ordinal == 0 else 1), 10, 0)
            )
            result.append(
                ResponseSeries(
                    run,
                    "q",
                    location,
                    ordinal,
                    times,
                    "standard",
                    timedelta(days=1),
                    "interval_end",
                    "m3 s-1",
                    values,
                    np.zeros(len(times), dtype=bool),
                )
            )
    return tuple(result)


def test_registry_grains_vocabulary_and_empty_design_bundle():
    registry = declarations(("q", "gwr"))
    assert len(registry) == 12
    assert all(
        item.implementation_revision and item.value_validity for item in registry
    )
    class_c = [item for item in registry if item.reference]
    assert {item.grain for item in class_c} == {"run"}
    assert {item.reference_location for item in class_c} == {"class_c_first_gauge"}
    rows = stochastic_rows(2, 6, unit_id_capacity=14)
    groups, reference, realizations = metric_groups(
        rows, n_realizations=2, st_num=6, unit_id_capacity=14
    )
    assert groups[""] == reference == ("01", "08")
    assert realizations["08"] == 2


def test_logical_unit_index_retains_empty_group_and_refuses_capacity():
    from blueearth_cst.experiment.scenario_rows import UnitNamespaceCapacityError

    runs = ("01", "02", "03")
    index = metric_unit_index(
        runs,
        ("01", "03"),
        (DeclaredBundle("same_design_point", "", ("03", "01")),),
        unit_id_capacity=10,
    )
    assert [(item.unit_id, item.grain, item.member_run_id) for item in index] == [
        ("01", "run", "01"),
        ("03", "run", "03"),
        ("04", "bundle", "01"),
        ("04", "bundle", "03"),
    ]
    with pytest.raises(UnitNamespaceCapacityError, match="minimum replacement=4"):
        metric_unit_index(
            ("1", "2", "3"),
            ("1", "3"),
            (DeclaredBundle("same_design_point", "", ("1", "3")),),
            unit_id_capacity=3,
        )
    with pytest.raises(ValueError, match="unique evaluated"):
        metric_unit_index(
            runs,
            ("01", "03"),
            (DeclaredBundle("same_design_point", "", ("01", "02")),),
            unit_id_capacity=10,
        )


def test_reference_uses_explicit_native_ordinal_and_is_order_invariant():
    series = responses()
    ref = resolve_month_reference(series, expected_run_ids=("01", "08"), which="wet")
    reverse = resolve_month_reference(
        tuple(reversed(series)), expected_run_ids=("08", "01"), which="wet"
    )
    assert ref == reverse
    assert (ref.reference_location_id, ref.month) == ("9", 6)
    metric = next(
        item for item in declarations(("q",)) if item.statistic == "wetmonth_mean"
    )
    values = reduce_run(metric, series[:2], anchor="YE-DEC", reference=ref)
    assert values["9"] > values["2"]
    with pytest.raises(ValueError, match="reference"):
        reduce_run(metric, series[:2], anchor="YE-DEC")
    incompatible = tuple(
        replace(item, location_ordinal=1 - item.location_ordinal)
        if item.run_id == "08"
        else item
        for item in series
    )
    with pytest.raises(ValueError, match="same first"):
        resolve_month_reference(
            incompatible, expected_run_ids=("01", "08"), which="wet"
        )


@pytest.mark.parametrize(
    "statistic,period,mode",
    [("return_level_max", 10, "max"), ("return_level_7day_min", 2, "min")],
)
def test_bundle_preserves_estimator_and_records_per_member_blocks(
    statistic, period, mode
):
    series = responses()
    metric = next(item for item in declarations(("q",)) if item.statistic == statistic)
    actual, evidence = reduce_bundle(
        metric, series, expected_run_ids=("01", "08"), anchor="YE-DEC"
    )
    frames = [
        pd.DataFrame(
            {item.location_id: item.values for item in series if item.run_id == run},
            index=series[0].time,
        )
        for run in ("01", "08")
    ]
    blocks = pd.concat(
        [
            frame.resample("YE-DEC").max()
            if mode == "max"
            else frame.rolling(7).mean().resample("YE-DEC").min()
            for frame in frames
        ],
        ignore_index=True,
    )
    expected = _return_level_from_blocks(blocks, period, mode)
    pd.testing.assert_series_equal(actual.sort_index(), expected.sort_index())
    assert {item.total for item in evidence} == {18}
    assert {item.required for item in evidence} == {10}
    assert all(
        [entry[1] for entry in item.member_counts] == [9, 9] for item in evidence
    )
    with pytest.raises(InsufficientReturnLevelBlocks, match="actual=9"):
        reduce_bundle(metric, series[:2], expected_run_ids=("01",), anchor="YE-DEC")
    constant = tuple(replace(item, values=np.ones(len(item.time))) for item in series)
    with pytest.raises(InvalidReturnLevelFit, match="constant sample"):
        reduce_bundle(metric, constant, expected_run_ids=("01", "08"), anchor="YE-DEC")


@pytest.mark.parametrize("field,value", [("units", "mm"), ("time_label", "instant")])
def test_metric_refuses_incompatible_response_metadata(field, value):
    metric = declarations(("q",))[0]
    series = [replace(item, **{field: value}) for item in responses()[:2]]
    with pytest.raises(ValueError, match="requirement"):
        reduce_run(metric, series, anchor="YE-DEC")


def test_reference_refuses_unevaluated_members_and_preserves_month_tie():
    series = responses()
    with pytest.raises(ValueError, match="not evaluated"):
        resolve_month_reference(series, expected_run_ids=("01",), which="wet")
    tied = tuple(
        replace(item, values=(item.time.day == 2).astype(float)) for item in series
    )
    reference = resolve_month_reference(
        tied, expected_run_ids=("01", "08"), which="wet"
    )
    assert reference.month == 1


@pytest.mark.parametrize("failure", ["exception", "nan_shape", "negative_scale"])
def test_invalid_estimator_result_refuses_without_fallback(monkeypatch, failure):
    import xarray as xr
    import xclim.indices.stats as stats

    def invalid_fit(*args, **kwargs):
        if failure == "exception":
            raise RuntimeError("estimator failed")
        return xr.DataArray(
            [
                np.nan if failure == "nan_shape" else 0.0,
                1.0,
                -1.0 if failure == "negative_scale" else 1.0,
            ],
            dims="dparams",
            coords={"dparams": ["c", "loc", "scale"]},
        )

    monkeypatch.setattr(stats, "fit", invalid_fit)
    metric = next(
        item for item in declarations(("q",)) if item.statistic == "return_level_max"
    )
    with pytest.raises(InvalidReturnLevelFit, match="xclim/SciPy GEV failure"):
        reduce_bundle(
            metric, responses(), expected_run_ids=("01", "08"), anchor="YE-DEC"
        )
