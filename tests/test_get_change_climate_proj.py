"""Tests for get_change_climate_proj.py (workflow-2 change helpers).

Realizes the R4 §7 audit-evidence matrix for ``get_change_annual_clim_proj``
(rows U, C1-C3, H, V, P) plus unit tests for ``_to_str_tuple`` and
``get_change_clim_projections``.

Design contract: `dev/r04/climate-projections-design.md` §7.

Analytically-trivial synthetic inputs (constant fields) make every expected
value self-evident: a constant precip 10 -> 12 gives a multiplicative change
of (12-10)/10*100 = 20.0; a constant temp 5 -> 7 gives an additive change of
7-5 = 2.0, *regardless* of windowing, calendar, or hydrological-year start.

CALENDAR DEFECT (rows C1/C2): against today's code the cftime rows do not
merely mis-window — they RAISE ``TypeError``, because
``get_change_annual_clim_proj`` builds its slice bounds with
``pd.to_datetime(...)`` (pandas Timestamps) and applies them to a cftime index
(``.sel(time=slice(...))``), which xarray/pandas refuses to compare across
calendars. Every CMIP6 source is cftime-backed (see the ``cmip6
cftime.Datetime360Day`` note in get_stats_climate_proj.py), so this is a real
correctness defect on the production path, not a synthetic artefact. The rows
are wired strict-xfail and routed to a split task; the norm they assert is the
correct (calendar-invariant) 20.0 / 2.0 answer.
"""
import sys
from os.path import join, dirname, realpath

import numpy as np
import pandas as pd
import pytest
import xarray as xr

TESTDIR = dirname(realpath(__file__))
SNAKEDIR = join(TESTDIR, "..")
sys.path.insert(0, SNAKEDIR)

from src.get_change_climate_proj import (  # noqa: E402
    _to_str_tuple,
    get_change_annual_clim_proj,
    get_change_clim_projections,
)


# --------------------------------------------------------------------------- #
# Synthetic-dataset builders
# --------------------------------------------------------------------------- #
def _monthly_time(years, calendar=None):
    """A monthly ('MS') time index spanning `len(years)` full calendar years."""
    start = f"{years[0]}-01-01"
    n = len(years) * 12
    if calendar is None:
        return pd.date_range(start=start, periods=n, freq="MS")
    return xr.date_range(start=start, periods=n, freq="MS", use_cftime=True,
                         calendar=calendar)


def _make_time_ds(
    precip,
    temp,
    years,
    calendar=None,
    scenario="historical",
    members=("r1i1p1f1",),
    with_temp=True,
):
    """Constant-field hist/fut dataset mirroring stats_time-*.nc structure.

    Dims: time (monthly), scenario, member. Vars: precip (+ temp).
    """
    times = _monthly_time(years, calendar=calendar)
    members = list(members)
    shape = (len(times), 1, len(members))
    data_vars = {
        "precip": (("time", "scenario", "member"), np.full(shape, precip, float)),
    }
    if with_temp:
        data_vars["temp"] = (
            ("time", "scenario", "member"),
            np.full(shape, temp, float),
        )
    return xr.Dataset(
        data_vars,
        coords={"time": times, "scenario": [scenario], "member": members},
    )


# --------------------------------------------------------------------------- #
# Row U (PASS): core change formula on trivial constant fields
# --------------------------------------------------------------------------- #
def test_row_U_change_precip_multiplicative_temp_additive():
    """Row U: precip multiplicative (c-h)/h*100; temp additive c-h.

    hist precip==10, fut precip==12 -> (12-10)/10*100 = 20.0
    hist temp==5,    fut temp==7    -> 7-5           = 2.0
    Constant fields -> the annual stat over any windowing is exactly the
    constant, so the change is calendar/window invariant.
    """
    hist = _make_time_ds(10.0, 5.0, [1990, 1991, 1992])
    fut = _make_time_ds(12.0, 7.0, [2050, 2051, 2052])
    res = get_change_annual_clim_proj(hist, fut, stats=["mean"])

    assert float(res["precip"].values.ravel()[0]) == 20.0
    assert float(res["temp"].values.ravel()[0]) == 2.0
    # both variables survive when hist/fut share {precip, temp}
    assert set(res.data_vars) == {"precip", "temp"}


# --------------------------------------------------------------------------- #
# Rows C1-C3: calendar classes.
#   C3 (datetime64, proleptic Gregorian) PASSES today.
#   C1 (360_day) and C2 (noleap) RAISE TypeError today -> genuine calendar
#   defect -> strict-xfail, split to t260720c.
# --------------------------------------------------------------------------- #
def test_row_C3_gregorian_datetime64_change_invariant():
    """Row C3 (PASS): proleptic-Gregorian datetime64 index.

    Constant fields -> the calendar cannot change the answer: 20.0 / 2.0.
    Three full calendar years -> three hydrological years retained (Jan start).
    """
    hist = _make_time_ds(10.0, 5.0, [1990, 1991, 1992], calendar=None)
    fut = _make_time_ds(12.0, 7.0, [2050, 2051, 2052], calendar=None)
    res = get_change_annual_clim_proj(hist, fut, stats=["mean"])
    assert float(res["precip"].values.ravel()[0]) == 20.0
    assert float(res["temp"].values.ravel()[0]) == 2.0


@pytest.mark.xfail(
    strict=True,
    reason="row-C1 calendar defect: get_change_annual_clim_proj slices a "
    "cftime.Datetime360Day index with pd.to_datetime() Timestamps and raises "
    "TypeError (cross-calendar compare). Split to t260720c.",
)
def test_row_C1_cftime_360day_change_invariant():
    """Row C1 (strict-xfail): cftime.Datetime360Day (CMIP6-native) index.

    NORM: constant fields must yield the calendar-invariant 20.0 / 2.0.
    Today the code raises TypeError before computing anything, so this xfails.
    """
    hist = _make_time_ds(10.0, 5.0, [1990, 1991, 1992], calendar="360_day")
    fut = _make_time_ds(12.0, 7.0, [2050, 2051, 2052], calendar="360_day")
    res = get_change_annual_clim_proj(hist, fut, stats=["mean"])
    assert float(res["precip"].values.ravel()[0]) == 20.0
    assert float(res["temp"].values.ravel()[0]) == 2.0


@pytest.mark.xfail(
    strict=True,
    reason="row-C2 calendar defect: get_change_annual_clim_proj slices a "
    "cftime.DatetimeNoLeap index with pd.to_datetime() Timestamps and raises "
    "TypeError (cross-calendar compare). Split to t260720c.",
)
def test_row_C2_cftime_noleap_change_invariant():
    """Row C2 (strict-xfail): cftime.DatetimeNoLeap index.

    NORM: constant fields must yield the calendar-invariant 20.0 / 2.0.
    Today the code raises TypeError before computing anything, so this xfails.
    """
    hist = _make_time_ds(10.0, 5.0, [1990, 1991, 1992], calendar="noleap")
    fut = _make_time_ds(12.0, 7.0, [2050, 2051, 2052], calendar="noleap")
    res = get_change_annual_clim_proj(hist, fut, stats=["mean"])
    assert float(res["precip"].values.ravel()[0]) == 20.0
    assert float(res["temp"].values.ravel()[0]) == 2.0


# --------------------------------------------------------------------------- #
# Row H (PASS): non-January hydrological-year boundary
# --------------------------------------------------------------------------- #
def test_row_H_october_hydro_year_window_and_change():
    """Row H (PASS): start_month_hyd_year='Oct'.

    Four calendar years of monthly data -> three full Oct->Sep hydrological
    years are retained (1990-10..1991-09, 1991-10..1992-09, 1992-10..1993-09).
    Constant fields -> change is still 20.0 / 2.0.
    """
    hist = _make_time_ds(10.0, 5.0, [1990, 1991, 1992, 1993])
    fut = _make_time_ds(12.0, 7.0, [2050, 2051, 2052, 2053])
    res = get_change_annual_clim_proj(
        hist, fut, stats=["mean"], start_month_hyd_year="Oct"
    )
    assert float(res["precip"].values.ravel()[0]) == 20.0
    assert float(res["temp"].values.ravel()[0]) == 2.0


def test_row_H_january_control_matches_row_U():
    """Row H control: explicit 'Jan' reproduces the default (Row U) answer."""
    hist = _make_time_ds(10.0, 5.0, [1990, 1991, 1992, 1993])
    fut = _make_time_ds(12.0, 7.0, [2050, 2051, 2052, 2053])
    res = get_change_annual_clim_proj(
        hist, fut, stats=["mean"], start_month_hyd_year="Jan"
    )
    assert float(res["precip"].values.ravel()[0]) == 20.0
    assert float(res["temp"].values.ravel()[0]) == 2.0


# --------------------------------------------------------------------------- #
# Row V: asymmetric variables (hist has temp, clim does not)
#   Normative (strict-xfail): must fail loud with a ValueError.
#   Characterization (PASS today): result silently carries only precip.
# --------------------------------------------------------------------------- #
@pytest.mark.xfail(
    strict=True,
    reason="row-V variable-drop defect: asymmetric hist/clim variables are "
    "silently intersected instead of raising. Split to t260720a.",
)
def test_row_V_asymmetric_variables_should_raise():
    """Row V normative (ext3-1): asymmetric variable sets must raise ValueError
    naming the missing variable(s). Today intersection() drops silently -> no
    raise -> strict-xfail against the norm."""
    hist = _make_time_ds(10.0, 5.0, [1990, 1991, 1992], with_temp=True)
    clim = _make_time_ds(12.0, 7.0, [2050, 2051, 2052], with_temp=False)
    with pytest.raises(ValueError, match=r"asymmetric.*variables.*temp"):
        get_change_annual_clim_proj(hist, clim, stats=["mean"])


def test_row_V_char_result_carries_only_precip():
    """Row V characterization (PASS today): the current silent-drop behaviour
    yields a result with ONLY precip; temp is absent."""
    hist = _make_time_ds(10.0, 5.0, [1990, 1991, 1992], with_temp=True)
    clim = _make_time_ds(12.0, 7.0, [2050, 2051, 2052], with_temp=False)
    res = get_change_annual_clim_proj(hist, clim, stats=["mean"])
    assert set(res.data_vars) == {"precip"}
    assert "temp" not in res.data_vars


# --------------------------------------------------------------------------- #
# Row P: asymmetric members (hist has r1+r2, clim has r1)
#   Normative (strict-xfail): must fail loud with a ValueError.
#   Characterization (PASS today): result silently keeps only r1i1p1f1.
# --------------------------------------------------------------------------- #
@pytest.mark.xfail(
    strict=True,
    reason="row-P partial-member defect: asymmetric hist/clim members are "
    "silently inner-joined instead of raising. Split to t260720b.",
)
def test_row_P_asymmetric_members_should_raise():
    """Row P normative (ext3-1): an unshared member must raise ValueError
    naming the dropped member. Today the inner-join drops silently -> no raise
    -> strict-xfail against the norm."""
    hist = _make_time_ds(
        10.0, 5.0, [1990, 1991, 1992], members=("r1i1p1f1", "r2i1p1f1")
    )
    clim = _make_time_ds(12.0, 7.0, [2050, 2051, 2052], members=("r1i1p1f1",))
    with pytest.raises(ValueError, match=r"asymmetric.*members.*r2i1p1f1"):
        get_change_annual_clim_proj(hist, clim, stats=["mean"])


def test_row_P_char_result_keeps_only_shared_member():
    """Row P characterization (PASS today): the current silent inner-join
    yields a result whose member coord == ['r1i1p1f1']; r2i1p1f1 is dropped."""
    hist = _make_time_ds(
        10.0, 5.0, [1990, 1991, 1992], members=("r1i1p1f1", "r2i1p1f1")
    )
    clim = _make_time_ds(12.0, 7.0, [2050, 2051, 2052], members=("r1i1p1f1",))
    res = get_change_annual_clim_proj(hist, clim, stats=["mean"])
    members = [str(m) for m in np.atleast_1d(res["member"].values)]
    assert members == ["r1i1p1f1"]
    # value still trivially correct on the shared member
    assert float(res["precip"].values.ravel()[0]) == 20.0


# --------------------------------------------------------------------------- #
# Unit: _to_str_tuple (R01 list-vs-comma-string horizon parser)
# --------------------------------------------------------------------------- #
@pytest.mark.parametrize(
    "value, expected",
    [
        ([1980, 2010], ("1980", "2010")),      # R01 list form
        ("1980, 2010", ("1980", "2010")),      # legacy comma-separated string
        ([2030, 2060], ("2030", "2060")),
        (["1980", "2010"], ("1980", "2010")),  # already-str list
        ((1980, 2010), ("1980", "2010")),      # tuple input
    ],
)
def test_to_str_tuple_list_and_string(value, expected):
    assert _to_str_tuple(value) == expected


def test_to_str_tuple_empty_list():
    """Falsey/empty list -> empty tuple (no crash)."""
    assert _to_str_tuple([]) == ()


# --------------------------------------------------------------------------- #
# Unit: get_change_clim_projections (grid-branch multiplicative/additive)
# --------------------------------------------------------------------------- #
def _make_grid_ds(precip, temp, scenario="historical"):
    """A 12-month x 2x2 constant grid with a scenario dim (as the func selects
    scenario[0])."""
    shape = (12, 1, 2, 2)
    return xr.Dataset(
        {
            "precip": (("month", "scenario", "y", "x"), np.full(shape, precip, float)),
            "temp": (("month", "scenario", "y", "x"), np.full(shape, temp, float)),
        },
        coords={
            "month": np.arange(1, 13),
            "scenario": [scenario],
            "y": [0, 1],
            "x": [0, 1],
        },
    )


def test_get_change_clim_projections_grid_change():
    """Grid change: precip multiplicative, temp additive, constant fields.

    hist precip==10, clim precip==12 -> 20.0 everywhere.
    hist temp==5,    clim temp==7    -> 2.0 everywhere.
    """
    ds_hist = _make_grid_ds(10.0, 5.0)
    ds_clim = _make_grid_ds(12.0, 7.0)
    res = get_change_clim_projections(ds_hist, ds_clim)
    assert float(np.unique(res["precip"].values)[0]) == 20.0
    assert float(np.unique(res["temp"].values)[0]) == 2.0
    assert set(res.data_vars) == {"precip", "temp"}
