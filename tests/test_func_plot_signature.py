# -*- coding: utf-8 -*-
"""Unit tests for ``blueearth_cst/shared/func_plot_signature.py``.

The module had NO direct coverage until 2026-08-11
(`dev/records/reviews/2026-08-11_test-suite-bloat-assessment.md` §4), while being a
shared helper with three consumers — ``model/plot_results.py``,
``shared/plot_evaluation.py`` and ``shared/wflow_outputs.py``. That is the
profile AGENTS.md names as *"a contract surface with other callers"*: only its
rule wiring was pinned, never its arithmetic.

Two halves, and they are tested differently.

* ``compute_metrics`` writes ``performance_metrics.csv``, which the performance
  sheet RENDERS rather than recomputes — so the numbers here reach a deliverable
  unchecked by anything downstream. Tested as arithmetic: the perfect-fit
  identities, the sign convention of ``Pbias``, and the daily/monthly split
  actually discriminating (the whole reason the table has two rows per metric).
* ``plot_basavg`` is a figure, and a figure is verified by rendering it and
  looking at it (AGENTS.md, "Figures are terminal artifacts"). What is tested
  here is therefore STRUCTURE, not appearance — how many panels exist, in what
  order, under which resample rule. Every case below stands for the 2026-08-10
  defect recorded in the function's own docstring: the per-subcatchment series
  were drawn as one object, which was correct only by accident while a basin had
  exactly one subcatchment, and dispatched to ``pcolormesh`` at four.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import pytest
import xarray as xr
from matplotlib import pyplot as plt

from blueearth_cst.shared import func_plot_signature as fps
from blueearth_cst.shared.func_plot_signature import (
    compute_metrics,
    plot_basavg,
    rsquared,
)

#: Every figure test here asserts STRUCTURE, never the export resolution.
pytestmark = pytest.mark.usefixtures("fast_figure_dpi")

#: A CONSTANT observation is the only way to state a bias or an error exactly,
#: and it is degenerate for the variance-normalised metrics: ``skills`` divides
#: by ``nanstd(qobs) == 0`` and reports NSE/KGE as inf/nan. The tests that use a
#: flat observation assert on RMSE, Pbias and VE, never on those — so the
#: warning is a property of the fixture, not a finding. Scoped per test rather
#: than module-wide, so a real divide-by-zero elsewhere still surfaces.
_FLAT_OBS_DIVIDE = pytest.mark.filterwarnings(
    "ignore:(divide by zero|invalid value) encountered in scalar divide:RuntimeWarning"
)


def _daily(values, start="2001-01-01"):
    time = pd.date_range(start, periods=len(values), freq="D")
    return xr.DataArray(
        np.asarray(values, dtype="float64"), dims="time", coords={"time": time}
    )


# ---------------------------------------------------------------------------
# rsquared
# ---------------------------------------------------------------------------


def test_a_perfect_line_scores_one():
    x = np.arange(50, dtype="float64")
    assert rsquared(x, 3.0 * x + 7.0) == pytest.approx(1.0)


def test_the_score_is_the_SQUARE_so_an_inverse_relation_also_scores_one():
    """The trap: R^2 cannot tell a perfect fit from a perfect ANTI-fit.

    Anything using this to decide "is the simulation good" needs the sign from
    elsewhere. Pinned so the property is visible rather than surprising.
    """
    x = np.arange(50, dtype="float64")
    assert rsquared(x, -3.0 * x + 7.0) == pytest.approx(1.0)


def test_pure_noise_against_a_ramp_scores_near_zero():
    rng = np.random.default_rng(0)
    x = np.arange(500, dtype="float64")
    assert rsquared(x, rng.normal(size=500)) < 0.05


# ---------------------------------------------------------------------------
# compute_metrics — the table shape
# ---------------------------------------------------------------------------


@pytest.fixture
def two_years():
    """Two years of daily flow with a seasonal cycle."""
    return _daily(10.0 + 5.0 * np.sin(np.arange(730) / 30.0))


def test_the_table_is_seven_metrics_by_two_time_types(two_years):
    df = compute_metrics(two_years, two_years, "S1")

    assert df.index.names == ["metrics", "time_type"]
    assert list(df.index.get_level_values("metrics").unique()) == [
        "KGE",
        "NSE",
        "NSElog",
        "RMSE",
        "MSE",
        "Pbias",
        "VE",
    ]
    assert list(df.index.get_level_values("time_type").unique()) == [
        "daily",
        "monthly",
    ]
    assert df.shape == (14, 1)


def test_the_single_column_is_named_after_the_station(two_years):
    """The column name is how ``performance_metrics.csv`` identifies its station.

    A default of ``"station"`` would collide the moment a basin has more than
    one, so the caller's name must reach the frame unmodified.
    """
    assert compute_metrics(two_years, two_years, "outlet_101").columns.tolist() == [
        "outlet_101"
    ]
    assert compute_metrics(two_years, two_years).columns.tolist() == ["station"]


# ---------------------------------------------------------------------------
# compute_metrics — the arithmetic
# ---------------------------------------------------------------------------


def test_a_simulation_identical_to_the_observation_scores_perfectly(two_years):
    """The identities every one of the seven metrics must satisfy at qsim == qobs.

    Efficiencies go to 1, errors to 0. This is the single check that catches an
    argument-order swap in any of the fourteen ``skills`` calls, since every
    metric here is symmetric ONLY at a perfect fit.
    """
    df = compute_metrics(two_years, two_years, "S")[["S"]]

    for metric in ("KGE", "NSE", "NSElog", "VE"):
        assert df.loc[metric, "S"].tolist() == pytest.approx([1.0, 1.0])
    for metric in ("RMSE", "MSE", "Pbias"):
        assert df.loc[metric, "S"].tolist() == pytest.approx([0.0, 0.0])


@_FLAT_OBS_DIVIDE
def test_pbias_is_positive_when_the_simulation_over_predicts():
    """Sign convention, and it is the easy one to invert.

    A simulation 10% above the observation reports ``+10``. Reported the other
    way round, a wet bias would read as a dry one in every evaluation sheet.
    """
    obs = _daily(np.full(730, 10.0))
    sim = _daily(np.full(730, 11.0))

    df = compute_metrics(sim, obs, "S")
    assert df.loc[("Pbias", "daily"), "S"] == pytest.approx(10.0)
    assert df.loc[("Pbias", "monthly"), "S"] == pytest.approx(10.0)


@_FLAT_OBS_DIVIDE
def test_the_monthly_row_forgives_what_the_daily_row_punishes():
    """Why the table carries two time types rather than one.

    A simulation that alternates +5/-5 about a flat observation has the right
    monthly mean and the wrong daily value everywhere. If the monthly row were
    computed from the same series as the daily one — a resample dropped or
    applied to only one operand — the two would agree and the distinction the
    table exists to draw would be gone.
    """
    obs = _daily(np.full(730, 10.0))
    sim = _daily(10.0 + 5.0 * (-1.0) ** np.arange(730))

    df = compute_metrics(sim, obs, "S")
    daily, monthly = df.loc[("RMSE", "daily"), "S"], df.loc[("RMSE", "monthly"), "S"]

    assert daily == pytest.approx(5.0)
    assert monthly < 1.0
    assert df.loc[("VE", "daily"), "S"] < df.loc[("VE", "monthly"), "S"]


@_FLAT_OBS_DIVIDE
def test_both_operands_are_resampled_not_just_the_simulation():
    """A one-sided resample is invisible at a perfect fit and wrong everywhere else.

    Observation constant, simulation seasonal: if ``qobs`` were compared at daily
    resolution against a monthly ``qsim`` (or vice versa), xarray would align on
    time and the monthly row would collapse to a handful of points. Pinned by
    the count the monthly row is built from — 24 months over two years.
    """
    obs = _daily(np.full(730, 10.0))
    sim = _daily(10.0 + 5.0 * np.sin(np.arange(730) / 30.0))

    monthly_rmse = compute_metrics(sim, obs, "S").loc[("RMSE", "monthly"), "S"]
    expected = float(
        np.sqrt(
            ((sim.resample(time="ME").mean("time") - 10.0) ** 2).mean("time").values
        )
    )
    assert monthly_rmse == pytest.approx(expected, rel=1e-6)


def test_metrics_use_concurrent_nonnegative_finite_days_before_monthly_means():
    sim = _daily([99, 2, 4, 6, np.nan, 10, 0, 14], start="2001-01-30")
    obs = _daily([1, 2, 3, 4, -1, 0, 7, np.inf], start="2001-01-31").drop_sel(
        time="2001-02-02"
    )
    result = compute_metrics(sim, obs, "S")
    # Four pairs: obs[1,2,0,7],sim[2,4,0,14]. January has one pair;
    # February's three pairs average3/6. Independent daily/monthly MSE oracles
    # distinguish pairing-before-resampling from each series' available means.
    assert result.loc[("MSE", "daily"), "S"] == pytest.approx(13.5)
    assert result.loc[("RMSE", "daily"), "S"] == pytest.approx(np.sqrt(13.5))
    assert result.loc[("NSE", "daily"), "S"] == pytest.approx(-25 / 29)
    assert result.loc[("KGE", "daily"), "S"] == pytest.approx(1 - np.sqrt(2))
    assert result.loc[("MSE", "monthly"), "S"] == pytest.approx(5.0)
    assert result.loc[("NSE", "monthly"), "S"] == pytest.approx(-4.0)
    assert result.loc[("Pbias", "daily"), "S"] == pytest.approx(100.0)
    assert result.loc[("VE", "daily"), "S"] == pytest.approx(0.0)
    log_obs = np.log(np.array([1.0, 2.0, 0.0, 7.0]) + 1e-6)
    log_sim = np.log(np.array([2.0, 4.0, 0.0, 14.0]) + 1e-6)
    expected_log = (
        1 - ((log_sim - log_obs) ** 2).sum() / ((log_obs - log_obs.mean()) ** 2).sum()
    )
    assert result.loc[("NSElog", "daily"), "S"] == pytest.approx(expected_log)
    support = result.attrs["comparison_support"]
    assert support["paired_days"] == 4
    assert support["paired_months"] == 2
    assert support["observed"]["omitted_dates"] == 1


def test_metrics_handle_zero_denominators_and_no_concurrent_pairs():
    zero = _daily(np.zeros(45))
    result = compute_metrics(zero, zero, "S")
    for metric in ("RMSE", "MSE"):
        assert result.loc[metric, "S"].tolist() == pytest.approx([0.0, 0.0])
    for metric in ("KGE", "NSE", "NSElog", "Pbias", "VE"):
        assert result.loc[metric, "S"].isna().all()
    disjoint = compute_metrics(zero, _daily(np.ones(5), start="2002-01-01"), "S")
    assert disjoint["S"].isna().all()
    assert disjoint.attrs["comparison_support"]["paired_days"] == 0
    invalid = compute_metrics(
        _daily([1.0, np.inf, -1.0, 4.0]), _daily([1.0, 2.0, 3.0, 4.0]), "S"
    )
    assert invalid.loc[("MSE", "daily"), "S"] == pytest.approx(0.0)
    assert invalid.loc[("NSE", "daily"), "S"] == pytest.approx(1.0)
    assert invalid.attrs["comparison_support"]["paired_days"] == 2


# ---------------------------------------------------------------------------
# plot_basavg — structure
# ---------------------------------------------------------------------------


@pytest.fixture
def captured(monkeypatch):
    """Record ``(path, figure)`` for every save, without asserting on pixels.

    ``plot_basavg`` writes through the module-level ``save_figure`` binding and
    returns nothing, so the figure is only reachable at save time. Patching the
    binding avoids PNG writes; caption inventories still use the test directory.
    """
    saves: list[tuple[str, plt.Figure]] = []

    def _fake_save_figure(path, *args, **kwargs):
        saves.append((path, kwargs.get("fig") or plt.gcf()))

    monkeypatch.setattr(fps, "save_figure", _fake_save_figure)
    yield saves
    plt.close("all")


def _basavg(codes, indices=None, years=2, value=1.0):
    """A basin-average dataset in the shape hydromt writes it.

    ``<code>_subcatchment`` is hydromt's ``<header>_<mapname>`` naming for a csv
    output reduced over the ``subcatchment`` map, which is what
    ``code_from_variable`` recovers the PLOT_META key from.
    """
    time = pd.date_range("2001-01-01", periods=365 * years, freq="D")
    data = {}
    for code in codes:
        if indices is None:
            data[f"{code}_subcatchment"] = xr.DataArray(
                np.full(len(time), value), dims="time", coords={"time": time}
            )
        else:
            data[f"{code}_subcatchment"] = xr.DataArray(
                np.full((len(indices), len(time)), value),
                dims=("index", "time"),
                coords={"index": list(indices), "time": time},
            )
    return xr.Dataset(data)


def test_basin_and_optional_individual_inventory(captured, tmp_path):
    ds = _basavg(["gwr"], indices=[103, 101, 102])
    plot_basavg(
        ds, str(tmp_path), cell_counts={101: 1, 102: 2, 103: 3}, subbasin_plots=True
    )
    names = [Path(path).name for path, _ in captured]
    assert names == [
        f"wflow_gwr_{kind}_{support}.png"
        for support in ("basin_avg", "subbasin_101", "subbasin_102", "subbasin_103")
        for kind in ("annual_ts", "monthly_clim_band")
    ]
    assert all(len(fig.axes) == 1 for _, fig in captured)
    assert all("subbasins" in Path(path).parts for path, _ in captured[2:])
    assert (tmp_path / "_engine/figure_captions.json").exists()
    assert (tmp_path / "subbasins/_engine/figure_captions.json").exists()


def test_weighted_daily_support_is_fixed_and_complete():
    time = pd.date_range("2000-01-01", periods=3)
    series = xr.DataArray(
        [[2.0, 10.0], [4.0, np.nan], [-2.0, -10.0]],
        dims=("time", "index"),
        coords={"time": time, "index": [101, 102]},
    )
    daily, _, _ = fps._basavg_daily(series, {101: 1, 102: 3})
    assert daily.iloc[0] == pytest.approx(8.0)
    assert np.isnan(daily.iloc[1])  # Never renormalize onto the remaining zone.
    assert daily.iloc[2] == pytest.approx(-8.0)
    with pytest.raises(ValueError, match="require exact"):
        fps._basavg_daily(series)
    for weights in ({101: 1}, {101: 1, 102: 0}, {101: 1, 102: np.inf}):
        with pytest.raises(ValueError):
            fps._basavg_daily(series, weights)


def test_calendar_gaps_leap_amounts_and_completeness():
    time = pd.date_range("2000-01-01", "2000-12-31")
    daily = pd.Series(2.0, index=time).drop(pd.Timestamp("2000-02-29"))
    annual, cycle, info = fps._basavg_statistics(daily, "amount")
    assert annual.loc[2000] == pytest.approx(732.0)
    assert cycle.loc[2, "mean"] == pytest.approx(58.0)
    assert info["omitted_dates"] == 1
    # Four absent March dates exceed the per-month tolerance even though the
    # year as a whole has only five missing days.
    daily = daily.drop(pd.date_range("2000-03-01", periods=4))
    annual, cycle, _ = fps._basavg_statistics(daily, "amount")
    assert np.isnan(annual.loc[2000])
    assert np.isnan(cycle.loc[3, "mean"])
    # Sixteen missing days, never more than two per month, fail annual tolerance.
    removed = [
        pd.Timestamp(2000, month, day) for month in range(1, 9) for day in (3, 4)
    ]
    annual, cycle, _ = fps._basavg_statistics(
        pd.Series(2.0, index=time).drop(removed), "amount"
    )
    assert np.isnan(annual.loc[2000])
    assert cycle["mean"].notna().all()


def test_partial_periods_equal_year_month_weight_and_quantiles():
    time = pd.date_range("2001-01-02", "2005-12-31")
    daily = pd.Series(time.year - 2000, index=time, dtype=float)
    annual, cycle, info = fps._basavg_statistics(daily, "amount")
    assert np.isnan(annual.loc[2001])
    assert info["partial_years"] == [2001]
    assert info["partial_months"] == ["2001-01"]
    # February remains eligible in2001. Calendar-month years have equal weight.
    assert cycle.loc[2, "mean"] == pytest.approx((28 + 56 + 84 + 116 + 140) / 5)
    full = pd.date_range("2001-01-01", "2005-12-31")
    _, cycle, _ = fps._basavg_statistics(
        pd.Series(full.year - 2000, index=full, dtype=float), "amount"
    )
    assert cycle.loc[1, ["mean", "p10", "p90"]].values == pytest.approx(
        [93.0, 43.4, 142.6]
    )


def test_stock_rate_means_and_warmup_not_cut_twice(captured, tmp_path):
    time = pd.date_range("2001-01-02", "2002-12-31")
    daily = pd.Series(7.0, index=time)
    for kind in ("stock", "rate"):
        annual, cycle, _ = fps._basavg_statistics(daily, kind)
        assert annual.loc[2002] == pytest.approx(7.0)
        assert cycle["mean"].values == pytest.approx(np.full(12, 7.0))
    ds = xr.Dataset({"swe_subcatchment": ("time", daily.values)}, coords={"time": time})
    plot_basavg(ds, str(tmp_path), warmup_excluded=True)
    annual = captured[0][1].axes[0].lines[0]
    assert list(annual.get_xdata()) == [2001, 2002]
    assert annual.get_ydata()[1] == pytest.approx(7.0)
    assert captured[0][1].axes[0].get_ylabel() == "mm"
    assert Path(captured[0][0]).name == "wflow_snow_annual_ts_basin_avg.png"
    assert captured[1][1].axes[0].get_ylabel() == "mm"


def test_unsupported_variable_fails_loud(captured, tmp_path):
    with pytest.raises(KeyError):
        plot_basavg(_basavg(["not_a_wflow_output"]), str(tmp_path))


def test_caption_inventory_tracks_current_request(captured, tmp_path):
    import json

    weights = {101: 1, 102: 2}
    plot_basavg(
        _basavg(["aet", "gwr"], indices=[101, 102]),
        str(tmp_path),
        cell_counts=weights,
        subbasin_plots=True,
    )
    path = tmp_path / "_engine/figure_captions.json"
    inventory = json.loads(path.read_text(encoding="utf-8"))
    inventory["figures"]["unrelated.png"] = {
        "caption": "Retain another figure family's caption."
    }
    path.write_text(json.dumps(inventory), encoding="utf-8")
    plot_basavg(
        _basavg(["gwr"], indices=[101, 102]), str(tmp_path), cell_counts=weights
    )
    inventory = json.loads(path.read_text(encoding="utf-8"))
    assert set(inventory["figures"]) == {
        "unrelated.png",
        "wflow_gwr_annual_ts_basin_avg.png",
        "wflow_gwr_monthly_clim_band_basin_avg.png",
    }
    assert not any("aet" in name for name in inventory["produced_paths"])
    optional = json.loads(
        (tmp_path / "subbasins/_engine/figure_captions.json").read_text(
            encoding="utf-8"
        )
    )
    assert optional["figures"] == {}
