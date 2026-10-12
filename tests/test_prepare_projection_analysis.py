"""Declared-input and distinct-window contracts for the analysis producer."""

import json
from types import SimpleNamespace

import numpy as np
import pandas as pd
import pytest
import xarray as xr

from blueearth_cst.projections import prepare_projection_analysis as producer
from blueearth_cst.projections import projection_analysis as analysis
from blueearth_cst.projections import series_identity
from blueearth_cst.projections.get_change_climate_proj import analysis_windows


def _series(path, start, count, scenario, components, region):
    years = np.arange(count) // 12
    dataset = xr.Dataset(
        {
            "temp": ("time", 10 + np.sin(years), {"units": "degC"}),
            "precip": ("time", 2 + np.cos(years) / 10, {"units": "mm/day"}),
        },
        coords={"time": pd.date_range(start, periods=count, freq="MS")},
        attrs={
            "cst_calendar": "360_day",
            "cst_schema_version": series_identity.SCHEMA_VERSION,
            "cst_series_digest": series_identity.series_digest(components, region),
        },
    ).expand_dims(
        model=["TEST/M1"], member=["r1"], scenario=[scenario], clim_project=["cmip6"]
    )
    dataset.to_netcdf(path)


def test_shared_windows_compute_once_with_identity_checks(tmp_path):
    region = "analysis-producer-fixture"
    hist, fut = tmp_path / "hist.nc", tmp_path / "fut.nc"
    hist_components, fut_components = {"series": "hist"}, {"series": "fut"}
    _series(hist, "1950-01-01", 65 * 12, "historical", hist_components, region)
    _series(fut, "2015-01-01", 86 * 12, "ssp245", fut_components, region)
    point = {
        "model": "TEST/M1",
        "scenario": "ssp245",
        "member": "r1",
        "series_path_hist": str(hist),
        "series_path": str(fut),
        "digest_components_hist": hist_components,
        "digest_components_fut": fut_components,
        "reference_series_key": "hist",
        "series_key": "fut",
    }
    windows = analysis_windows(
        {"far1": (2081, 2100), "far2": (2081, 2100)}, reference_window=(2000, 2014)
    )
    tables, record = producer.prepare_tables([point], windows, region_fp=region)
    assert len(record["windows"]) == 1
    assert record["windows"][0]["horizons"] == ["far1", "far2"]
    assert (
        record["windows"][0]["horizon_windows"]["far1"]["requested"]
        == record["windows"][0]["horizon_windows"]["far2"]["requested"]
    )
    keys = [
        "model",
        "scenario",
        "member",
        "window_id",
        "period",
        "variable",
        "statistic",
        "quantity",
    ]
    assert not tables["changes"].duplicated(keys).any()
    assert tables["changes"].window_id.unique().tolist() == ["2081-2100"]
    assert record["reference"] == (2000, 2014)
    annual = tables["changes"].loc[tables["changes"].period == "annual"]
    assert set(annual.n_reference) == {15}
    assert set(annual.n_future) == {20}
    assert set(annual.status) == {"ok"}
    seasonal = tables["changes"].loc[
        tables["changes"].period.isin(["DJF", "MAM", "JJA", "SON"])
    ]
    assert set(seasonal.status) == {"ok"}
    assert record["methods"]["season_min_years"] == {
        "2081-2100": {"reference": 14, "future": 18}
    }
    assert tables["member_anomalies"].year.min() == 1950
    assert tables["member_anomalies"].year.max() == 2100
    assert len(tables["availability"]) == 19
    assert (
        not tables["availability"]
        .loc[
            tables["availability"].filename
            == "cmip6_precip_temp_annual_member_ratio_box_basin_avg.png",
            "available",
        ]
        .any()
    )
    assert record["methods"]["null_band"]["simulations"] == 20_000
    with pytest.raises(RuntimeError, match="digest"):
        producer.prepare_tables([point], windows, region_fp="different-region")


def test_undeclared_series_refused_before_output_mutation():
    sm = SimpleNamespace(
        params=SimpleNamespace(
            points=[{"series_path_hist": "hist.nc", "series_path": "fut.nc"}]
        ),
        input=SimpleNamespace(series_nc=["hist.nc", "fut.nc", "leftover.nc"]),
    )
    with pytest.raises(RuntimeError, match="series set differs"):
        producer.run(sm)


def test_display_bands_preserve_masks_and_equal_model_reference_cv():
    rows = []
    for model, cv, first in (("A", 0.1, 1985), ("A", 0.3, 1985), ("B", 0.8, 1988)):
        rows.append(
            {
                "model": model,
                "scenario": "ssp245",
                "window_id": "2036-2065",
                "variable": "precip",
                "statistic": "cv_detrended",
                "period": "annual",
                "reference_value": cv,
                "variability_eligible": True,
                "reference_years": json.dumps(list(range(first, 2015))),
                "future_years": json.dumps(list(range(2036, 2066))),
            }
        )
    bands = producer.display_null_bands(pd.DataFrame(rows))
    assert len(bands) == 2
    assert {len(band["reference_years"]) for band in bands} == {27, 30}
    assert all(band["reference_cv"] == pytest.approx(0.5) for band in bands)
    assert all(band["n_mask_strata"] == 2 for band in bands)
    assert all(band["n_valid"] + band["n_invalid"] == 20_000 for band in bands)


def test_model_ratio_summary_uses_log_middle_pair():
    common = dict.fromkeys(analysis.CELL, "test")
    models = pd.DataFrame(
        [
            {**common, "model": "A", "value": 0.5, "n_members": 1},
            {**common, "model": "B", "value": 2.0, "n_members": 1},
        ]
    )
    summary = producer._model_ratio_summary(models).iloc[0]
    assert summary["median"] == pytest.approx(1.0)
    assert summary["median"] != pytest.approx(1.25)
    assert (summary["min"], summary["max"]) == pytest.approx((0.5, 2.0))
    assert not summary.iqr_shown
