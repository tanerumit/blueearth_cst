"""WF1 uses WF0 reporting-year, completeness and summary methods."""

import numpy as np
import pandas as pd
import pytest
import xarray as xr

from blueearth_cst.climate_analysis.diagnostic_maps import annual_fields
from blueearth_cst.model.forcing_figures import prepare_forcing


def _forcing(index, values):
    return xr.Dataset(
        {
            variable: (("time", "y", "x"), values.copy())
            for variable in ("precip", "temp", "pet")
        },
        coords={"time": index, "y": [5.0, 5.1], "x": [10.0, 10.1]},
    )


def test_cellwise_maps_match_wf0_with_gaps_and_non_january_years():
    index = pd.date_range("1999-11-01", "2003-11-30")
    values = np.ones((len(index), 2, 2))
    values[index.isin(pd.date_range("2001-01-01", periods=2)), 0, 0] = np.nan
    values[index.isin(pd.date_range("2002-01-01", periods=4)), 0, 1] = np.nan
    # Sixteen missing days, each month individually below the monthly limit.
    missing = pd.to_datetime(
        [f"2001-{month:02d}-{day:02d}" for month in range(2, 10) for day in (1, 2)]
    )
    values[index.isin(missing), 1, 0] = np.nan
    ds = _forcing(index, values).chunk({"time": 200})
    inside = xr.DataArray([[True, True], [True, False]], dims=("y", "x"))
    fields, results, years = prepare_forcing(ds, inside, 10)
    native = ds.where(inside).rename({"y": "latitude", "x": "longitude"})
    expected = annual_fields(
        native, 10, {"max_missing_days_month": 3, "max_missing_days_year": 15}
    )
    xr.testing.assert_allclose(fields, expected)
    assert years.tolist() == [2000, 2001, 2002]
    assert fields.precip_valid_years.values.tolist() == [[3, 2], [2, 0]]
    assert results["temp"]["annual"].index.tolist() == [2000, 2001, 2002]


def test_masked_daily_means_and_monthly_quantiles_preserve_forcing():
    index = pd.date_range("2001-01-01", "2003-12-31")
    values = np.broadcast_to(
        (index.year - 2000).to_numpy()[:, None, None], (len(index), 2, 2)
    ).copy()
    values[:, 1, :] = 999
    ds = _forcing(index, values)
    original = ds.copy(deep=True)
    inside = xr.DataArray([[True, True], [False, False]], dims=("y", "x"))
    _, results, _ = prepare_forcing(ds, inside, 1)
    january = results["precip"]["clim"].loc[1]
    assert january["mean"] == pytest.approx(62)
    assert january["p10"] == pytest.approx(37.2)
    assert january["p90"] == pytest.approx(86.8)
    assert results["temp"]["clim"].loc[1, "mean"] == pytest.approx(2)
    assert results["pet"]["annual"].total.tolist() == [365, 730, 1095]
    xr.testing.assert_identical(ds, original)


def test_annual_temperature_uses_sen_slope_instead_of_outlier_sensitive_ols():
    index = pd.date_range("2001-01-01", "2009-12-31")
    daily = (index.year - 2000).to_numpy(dtype=float)
    daily[index.year == 2008] = 100
    values = np.broadcast_to(daily[:, None, None], (len(index), 2, 2))
    ds = _forcing(index, values)
    inside = xr.DataArray(np.ones((2, 2), dtype=bool), dims=("y", "x"))
    _, results, _ = prepare_forcing(ds, inside, 1)
    trend = results["temp"]["trends"]["total"]
    assert trend["slope"] == pytest.approx(10)
    annual = results["temp"]["annual"].total
    assert np.polyfit(annual.index, annual.values, 1)[0] * 10 > 50
    assert trend["n"] == 9
