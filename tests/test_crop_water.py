"""Crop-water numerical and paired-response contracts."""

from dataclasses import replace
from datetime import timedelta

import numpy as np
import pandas as pd
import pytest

from blueearth_cst.indicators import loader
from blueearth_cst.indicators.series import ResponseSeries
from blueearth_cst.indicators.sets.crop_water.calculations import prepare_baseline_qcrit

TIME = pd.date_range("2023-10-01", "2024-10-31", freq="D")


def _series(variable, values, *, location="basin", time=TIME):
    values = np.asarray(values, dtype=float)
    return ResponseSeries(
        run_id="historical",
        variable=variable,
        location_id=location,
        location_ordinal=0,
        time=time,
        calendar="standard",
        timestep=timedelta(days=1),
        time_label="interval_end",
        units="m3 s-1" if variable == "q" else "mm dt-1",
        values=values,
        missing=np.isnan(values),
    )


def _inputs():
    size = len(TIME)
    return {
        "precip": _series("precip", np.full(size, 2.0)),
        "pet": _series("pet", np.full(size, 3.0)),
        "aet": _series("aet", np.full(size, 1.0)),
        "q": _series("q", np.full(size, 1.0)),
        "gwr": _series("gwr", np.full(size, 2.0)),
    }


def _declaration(name):
    indicator = next(
        item for item in loader.declarations("crop-water") if item.name == name
    )
    if name == "summer_low_flow_days":
        record = {
            "value": 2.0,
            "source_id": "historical-run",
            "years": [2024],
            "used_summers": [2024],
            "excluded_summers": [],
            "method": "linear p=0.10",
            "units": "m3 s-1",
        }
        indicator = replace(
            indicator,
            calculation_parameters={
                "season": "summer",
                "thresholds": {"basin": record},
            },
        )
    return indicator


def _evaluate(name, inputs):
    declaration = _declaration(name)
    responses = [inputs[item.variable] for item in declaration.requirements]
    result = loader.evaluate(declaration, responses, anchor="YE-SEP")
    loader.check(declaration, responses, result, anchor="YE-SEP")
    return result


def test_all_ten_selections_and_complete_period_values():
    inputs = _inputs()
    assert len(loader.declarations("crop-water")) == 10
    for name in (
        "winter_climatic_deficit",
        "summer_climatic_deficit",
        "winter_longest_dry_spell",
        "summer_longest_dry_spell",
        "winter_relative_et_deficit",
        "summer_relative_et_deficit",
        "winter_et_limitation_days",
        "summer_et_limitation_days",
        "summer_low_flow_days",
        "annual_recharge",
    ):
        result = _evaluate(name, inputs)
        periods = next(
            table.data for table in result.diagnostics if table.name == "period_values"
        )
        assert (periods.status == "valid").sum() == 1
        assert result.values["basin"] == pytest.approx(
            periods.loc[periods.status == "valid", "value"].iloc[0]
        )
    assert _evaluate("winter_relative_et_deficit", inputs).values[
        "basin"
    ] == pytest.approx(200 / 3)
    assert _evaluate("summer_et_limitation_days", inputs).values["basin"] == 184
    assert _evaluate("summer_low_flow_days", inputs).values["basin"] == 184
    assert _evaluate("annual_recharge", inputs).values["basin"] == 732


def test_paired_dates_and_locations_are_refused():
    inputs = _inputs()
    inputs["pet"] = _series("pet", np.full(len(TIME), 3.0), location="other")
    with pytest.raises(ValueError, match="paired location"):
        _evaluate("summer_climatic_deficit", inputs)
    inputs["pet"] = _series(
        "pet", np.full(len(TIME), 3.0), time=TIME + pd.Timedelta(days=1)
    )
    with pytest.raises(ValueError, match="paired response support"):
        _evaluate("summer_climatic_deficit", inputs)


def test_missing_aet_on_low_pet_day_invalidates_whole_season():
    inputs = _inputs()
    day = TIME.get_loc(pd.Timestamp("2024-06-01"))
    pet = inputs["pet"].values.copy()
    aet = inputs["aet"].values.copy()
    pet[day] = 0.5
    aet[day] = np.nan
    inputs["pet"] = _series("pet", pet)
    inputs["aet"] = _series("aet", aet)
    result = _evaluate("summer_et_limitation_days", inputs)
    assert np.isnan(result.values["basin"])
    periods = next(
        table.data for table in result.diagnostics if table.name == "period_values"
    )
    assert "invalid" in periods.status.to_list()


def test_signed_recharge_and_positive_daily_deficit():
    inputs = _inputs()
    p = inputs["precip"].values.copy()
    pet = inputs["pet"].values.copy()
    p[TIME.get_loc("2024-06-01")] = 10
    pet[TIME.get_loc("2024-06-01")] = 5
    inputs["precip"] = _series("precip", p)
    inputs["pet"] = _series("pet", pet)
    assert _evaluate("summer_climatic_deficit", inputs).values["basin"] == 183
    r = inputs["gwr"].values.copy()
    r[TIME.get_loc("2024-06-01")] = -1
    inputs["gwr"] = _series("gwr", r)
    assert _evaluate("annual_recharge", inputs).values["basin"] == 729


def test_strict_dry_run_and_et_boundaries():
    inputs = _inputs()
    p = inputs["precip"].values.copy()
    for date, value in zip(
        pd.date_range("2024-06-01", periods=6),
        (0, 0.9, 1, 0, 0, 0),
        strict=True,
    ):
        p[TIME.get_loc(date)] = value
    inputs["precip"] = _series("precip", p)
    assert _evaluate("summer_longest_dry_spell", inputs).values["basin"] == 3

    pet = inputs["pet"].values.copy()
    aet = inputs["aet"].values.copy()
    summer = (TIME >= "2024-05-01") & (TIME <= "2024-10-31")
    pet[summer] = 0.5
    aet[summer] = 0.0
    first, second = TIME.get_loc("2024-06-01"), TIME.get_loc("2024-06-02")
    pet[[first, second]] = [1.0, 2.0]
    aet[[first, second]] = [0.5, 0.8]
    inputs["pet"] = _series("pet", pet)
    inputs["aet"] = _series("aet", aet)
    result = _evaluate("summer_et_limitation_days", inputs)
    assert result.values["basin"] == 1
    periods = next(
        table.data for table in result.diagnostics if table.name == "period_values"
    )
    valid = periods.loc[periods.status == "valid"].iloc[0]
    assert valid.eligible_days == 2
    assert valid.low_pet_excluded_days == 182
    assert _evaluate("summer_relative_et_deficit", inputs).values[
        "basin"
    ] == pytest.approx(100 * (1 - 1.3 / (182 * 0.5 + 3)))


def test_zero_pet_sum_is_undefined_and_aet_above_pet_is_retained():
    inputs = _inputs()
    pet = inputs["pet"].values.copy()
    aet = inputs["aet"].values.copy()
    summer = (TIME >= "2024-05-01") & (TIME <= "2024-10-31")
    pet[summer] = 0
    inputs["pet"] = _series("pet", pet)
    assert np.isnan(_evaluate("summer_relative_et_deficit", inputs).values["basin"])
    pet[summer] = 1
    aet[summer] = 2
    inputs["pet"] = _series("pet", pet)
    inputs["aet"] = _series("aet", aet)
    result = _evaluate("summer_relative_et_deficit", inputs)
    assert result.values["basin"] == -100
    periods = next(
        table.data for table in result.diagnostics if table.name == "period_values"
    )
    assert periods.loc[periods.status == "valid", "aet_above_pet_days"].iloc[0] == 184


def test_crop_group_mean_propagates_undefined_member():
    inputs = _inputs()
    declaration = _declaration("summer_relative_et_deficit")
    first = [inputs[item.variable] for item in declaration.requirements]
    second = [replace(item, run_id="second") for item in first]
    aet = second[0].values.copy()
    aet[TIME.get_loc("2024-06-01")] = np.nan
    second[0] = replace(second[0], values=aet, missing=np.isnan(aet))
    result = loader.evaluate(
        declaration,
        [*first, *second],
        anchor="YE-SEP",
        group=True,
        expected_run_ids=["historical", "second"],
    )
    assert np.isnan(result.values["basin"])
    assert result.statuses["basin"] == "undefined"


def test_baseline_qcrit_uses_only_complete_summers_and_records_provenance():
    q = np.full(len(TIME), 2.0)
    summer = (TIME >= "2024-05-01") & (TIME <= "2024-10-31")
    q[summer] = np.arange(summer.sum())
    threshold = prepare_baseline_qcrit(
        [_series("q", q)], source_id="historical-id", years=[2023, 2024]
    )["basin"]
    assert threshold["used_summers"] == [2024]
    assert threshold["excluded_summers"] == [2023]
    assert threshold["value"] == pytest.approx(18.3)
