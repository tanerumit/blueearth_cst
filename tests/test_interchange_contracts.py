"""Two-layer tests for the interchange-contract validators (design §5.5).

- **Layer 1 — synthetic pass/fail, fixture-independent, ALWAYS executed.**
  Every validator ships a conforming in-memory object (report == []) and a
  deliberately broken one (report != []). No file I/O — objects are built
  directly here (the validators take parsed objects, never paths), so a
  fixtureless checkout (fresh clone, CI) still executes every validator's pass
  AND fail path. "Green" is never indistinguishable from "nothing checked".

- **Layer 2 — real-fixture integration, skipped VISIBLY when the fixture is
  absent.** Each case opens an artifact under the untracked ``test_case/test_local``
  tree and carries the repo fixture-absent guard (mirroring
  ``tests/test_store_region_bbox.py``): a module-level ``_FIXTURE_ABSENT``
  reason constant + ``@pytest.mark.skipif``. Absence is a NAMED, reported
  condition (read via ``pytest -rs``), never silence. The three temp() content
  validators (WG-4/WG-6/HM-6b) additionally skip with a documented reason when
  the temp artifact is absent (the default fixture state) — see the commit-4
  temp layer.

Source of record: ``dev/milestones/p32b/interchange-contracts-design.md`` §5.5 and the two
seam docs ``dev/reference/contracts/*-seam.md``.
"""

import os
from os.path import dirname, join, realpath

import pandas as pd
import pytest
import yaml

from blueearth_cst.shared import interchange_contracts as ic  # noqa: E402
from blueearth_cst.shared.snake_utils import (  # noqa: E402
    historical_window_bounds,
    slugify_window,
)

# --- Fixture location + the single named skip reason -----------------------

TESTDIR = dirname(realpath(__file__))
SNAKEDIR = join(TESTDIR, "..")
_FIXTURE = join(SNAKEDIR, "test_case", "test_local")
_EXP = join(_FIXTURE, "experiments", "experiment")

# Fixture sub-roots, named after the Snakefile path variables they mirror so a
# future tree move has ONE place to change here instead of a dozen literals.
#
#   _MODEL_DIR  <- basin_dir  = {project_dir}/models/hydrology/wflow
#   _STORE_ROOT <- store_dir  = {project_dir}/data/climate/historical/<key>
#   _WG_DIR     <- wg_dir     = {exp_dir}/climate/weathergenr
#   _RUNS_DIR   <- runs_dir   = {exp_dir}/hydrology/wflow
#
# R9 P2 moved every one of these and this file was NOT re-pointed. The staleness
# survived because the whole Layer-2 block is `skipif(not _fixture_present())`
# and the fixture is untracked: it is absent in every worktree and on CI, so 22
# dead paths sat green everywhere until the first post-R9 `pytest tests/` in the
# primary checkout (2026-08-05, 22 FileNotFoundError). R9's own gates --
# `semantic_tree_diff` and `check_baseline` -- validate the tree's SHAPE, not the
# code that reads it, so neither could have caught this. Keeping the roots here,
# derived and commented, is what makes the next move a one-line edit.
_MODEL_DIR = join(_FIXTURE, "models", "hydrology", "wflow")
_STORE_ROOT = join(_FIXTURE, "data", "climate", "historical")
_WG_DIR = join(_EXP, "climate", "weathergenr")
_RUNS_DIR = join(_EXP, "hydrology", "wflow")
# The generated climate catalog is PER MEMBER since 2026-08-18 -- rule 3.14
# writes its own one-entry file beside the member's TOML, and the single
# `config/catalogs/data_catalog_run_stress_test.yml` that rule 3.13 built over
# the whole sweep is gone with that rule. It is a `temp()` output, so like the
# other temp-backed contracts below these tests skip unless the tree came from a
# `--notemp` capture.


def _successor_artifacts():
    import json
    from pathlib import Path

    root = Path(_EXP)
    marker = root / "config/simulation.json"
    if not marker.exists() and (root / "results/q_indicators.csv").exists():
        pytest.skip(
            "standing fixture predates R12; GF9 successor run has not replaced it"
        )
    simulation = json.loads(marker.read_text(encoding="utf-8"))
    collection = Path(simulation["collection"]["manifest_path"]).parent
    scenarios = pd.read_csv(
        collection / "scenario_table.csv", dtype=str, keep_default_na=False
    )
    return root, collection, scenarios


def _evaluated_runs():
    _, _, scenarios = _successor_artifacts()
    return scenarios.loc[scenarios.evaluated == "true", "run_id"].tolist()


_FIXTURE_ABSENT = (
    "untracked test_case/test_local fixture tree not present "
    "(interchange-contract integration layer skipped)"
)


def _fixture_present() -> bool:
    return os.path.exists(_FIXTURE)


# --- the fixture's SCHEMA, which its presence does not imply ----------------
#
# `_fixture_present` answers "is there a tree here", and for sixteen of the
# seventeen cases below that is the whole question: they read the model dir,
# the climate store and the experiment dir, whose paths R14 did not move. The
# seventeenth reads a WF1 CONFIG SNAPSHOT, and R14 renamed that file
# (`snake_config_` -> `project_config_`, `C-85`) and the keys inside it. A tree
# written before R14 therefore passes `_fixture_present` and then raises
# `FileNotFoundError` on a file that is absent BY VERSION rather than missing.
#
# That is not hypothetical and it is not transient: the primary checkout's
# fixture is deliberately pre-R14 -- Gate 5 kept it as the counterfactual it
# compared the migrated tree against (`dev/milestones/r14/config-shape-gate5.md`)
# -- so it will stay that way, and refreshing it would destroy the reference.
# Guard the one schema-dependent case rather than widening `_fixture_present`,
# which would skip the sixteen that a pre-R14 tree still answers correctly.
_WF1_SNAPSHOT = join(_FIXTURE, "config", "runs", "build_model", "composed_config.yml")

_FIXTURE_PRE_R14 = (
    "test_case/test_local predates R14: no config/runs/"
    "build_model/composed_config.yml, so its v1 snapshot cannot answer a v2 key "
    "(the WG-1 store-key case is skipped; the rest of the layer still runs)"
)


def _wf1_snapshot_present() -> bool:
    return os.path.exists(_WF1_SNAPSHOT)


# --- the pre-P2 member-token guard -----------------------------------------
#
# R11 P2 renamed the member token `cst_` -> `st_` in filenames and catalog
# keys. The fixture is only regenerated when WF3 re-runs, which P2 does not do
# -- P3 owns the single re-run and re-record -- so it still carries `cst_`
# names. The Layer-2 cases below therefore assert the POST-rename path and skip
# on the SPECIFIC pre-rename shape: the old-token twin present exactly where
# the new-token artifact is missing. Never a bare existence guard, which is how
# R9-4 turned a wrong path into a silent pass (AGENTS.md); if NEITHER exists the
# helper returns the new path and the caller fails loudly, as it should.
_PRE_P2_MEMBER_TOKEN = (
    "fixture still carries the pre-P2 `cst_` member token; "
    "regenerated by P3's WF3 re-run"
)


# ===========================================================================
# Layer 1 — synthetic pass/fail (fixture-independent, always executed)
# ===========================================================================
#
# Objects are built with xarray/pandas in-memory. Each validator gets one
# conforming object (report == []) and one one-fault object (report != []).


def _wg1_good():
    import numpy as np
    import xarray as xr

    n = 3
    ds = xr.Dataset(
        {
            v: (
                ("time", "latitude", "longitude"),
                np.zeros((n, 2, 2), dtype="float32"),
                {"units": u},
            )
            for v, u in ic._WG1_VARS_UNITS.items()
        },
        coords={
            "time": pd.date_range("2000-01-01", periods=n),
            "latitude": np.array([1.0, 2.0], dtype="float32"),
            "longitude": np.array([1.0, 2.0], dtype="float32"),
            "spatial_ref": 0,
        },
        attrs={"crs": 4326, "category": "meteo"},
    )
    return ds


def test_wg1_synthetic_pass():
    assert ic.validate_wg1(_wg1_good()) == []


def test_wg1_synthetic_fail():
    ds = _wg1_good().drop_vars("precip")  # missing a pinned variable
    assert ic.validate_wg1(ds) != []


def _wg2_good(st_num=3, width=1):
    """A stress_test_lookup.csv as rule 3.09 writes it: 12 x ST_NUM rows, no st_0."""
    rows = []
    for member in range(1, st_num + 1):
        for month in range(1, 13):
            rows.append(
                {
                    "st_id": f"{member:0{width}d}",
                    "month": month,
                    "temp_change": 1.5 * member,
                    "precip_change": -30.0 + 10.0 * member,
                    "precip_variance_change": 0.0,
                }
            )
    return pd.DataFrame(rows)


def test_wg2_synthetic_pass():
    assert ic.validate_wg2(_wg2_good(), st_num=3) == []


def test_wg2_synthetic_fail():
    df = _wg2_good().iloc[:6]  # a truncated member, month domain broken
    assert ic.validate_wg2(df, st_num=3) != []


def test_wg2_refuses_an_st_0_row():
    """`st_0` has no row, and its absence is LOAD-BEARING rather than tidy.

    It is what makes "not on the surface" structural instead of conventional: a
    consumer joining results to the lookup finds no axis for the baseline and
    cannot place it on the surface by accident. An all-zero row would be
    indistinguishable from an identity member's while denoting a
    differently-processed climate.
    """
    df = _wg2_good(st_num=2)
    baseline = pd.DataFrame(
        [
            {
                "st_id": "0",
                "month": month,
                "temp_change": 0.0,
                "precip_change": 0.0,
                "precip_variance_change": 0.0,
            }
            for month in range(1, 13)
        ]
    )
    report = ic.validate_wg2(pd.concat([baseline, df], ignore_index=True), st_num=2)
    assert any("st_0" in line for line in report), report


def test_wg2_refuses_a_gap_in_the_month_grid():
    """A member missing a month is a SHORT vector on the R side, which recycles
    into a wrong answer rather than an error."""
    df = _wg2_good(st_num=2)
    gapped = df[~((df.st_id == "2") & (df.month == 7))]
    report = ic.validate_wg2(gapped, st_num=2)
    assert any("month domain" in line for line in report), report


def test_wg2_refuses_a_table_mixing_st_id_widths():
    """One width per table is what lets a consumer INFER the join key's width
    from the table itself rather than being told ST_NUM."""
    df = _wg2_good(st_num=2)
    df.loc[df.st_id == "1", "st_id"] = "01"
    report = ic.validate_wg2(df)
    assert any("width" in line for line in report), report


def test_wg2_refuses_a_truncated_member_set():
    """Without ST_NUM a validator can only check internal consistency, and a
    truncated table is internally consistent -- so the count is an argument."""
    df = _wg2_good(st_num=2)
    assert ic.validate_wg2(df) == []  # internally consistent
    assert ic.validate_wg2(df, st_num=3) != []  # ... but short of the declared grid


def _wg3_good():
    # One section per weathergenr function (renamed 2026-08-12, tracking 2.0.0
    # since 2026-08-17).
    cfg = {section: {k: 0 for k in keys} for section, keys in ic._WG3_SECTIONS.items()}
    # `vars` is type-pinned as a list, so the 0 placeholder will not do.
    cfg["generate_weather"]["vars"] = ["precip", "temp"]
    # C29 moved these here from the retired per-member config.
    cfg["temp"] = {"transient_change": True}
    cfg["precip"] = {"transient_change": True}
    return cfg


def test_wg3_synthetic_pass():
    assert ic.validate_wg3(_wg3_good()) == []


def test_wg3_synthetic_fail():
    cfg = _wg3_good()
    del cfg["generate_weather"]["seed"]  # a required key removed
    assert ic.validate_wg3(cfg) != []


def test_wg3_requires_vars_to_be_a_list():
    """A scalar reaches generate_weather as a length-1 vector and silently
    generates one variable, so the type is pinned, not just the presence."""
    cfg = _wg3_good()
    cfg["generate_weather"]["vars"] = "precip"
    diffs = ic.validate_wg3(cfg)
    assert diffs and any("generate_weather.vars" in d for d in diffs)


@pytest.mark.parametrize(
    "section",
    [
        "run_weather_generator",
        "generate_weather",
        "apply_climate_perturbations",
        "write_netcdf",
    ],
)
def test_wg3_requires_every_function_section(section):
    """Each section is one weathergenr function's argument set. A missing
    section means every one of its arguments reaches R as NULL."""
    cfg = _wg3_good()
    del cfg[section]
    diffs = ic.validate_wg3(cfg)
    assert diffs and any(section in d for d in diffs)


@pytest.mark.parametrize("section", ["temp", "precip"])
def test_wg3_requires_the_transient_flags(section):
    """C29: the shared config is now the ONLY carrier of these two flags.

    Rule 3.05 used to supply them per member. With that rule gone, an omission
    here reaches `impose_climate_change.R` as NULL and the perturbation silently
    takes whatever weathergenr defaults to -- so the contract has to pin them.
    """
    cfg = _wg3_good()
    del cfg[section]["transient_change"]
    diffs = ic.validate_wg3(cfg)
    assert diffs and any(f"{section}.transient_change" in d for d in diffs)


@pytest.mark.parametrize(
    "section,key",
    [
        ("generate_weather", "save_plots"),
        ("apply_climate_perturbations", "pet_method"),
        # The 1.2.0 rename surfaced these four the same way C34 surfaced the two
        # above: each was previously unreachable or hardcoded in the R.
        ("generate_weather", "warm_filter_bounds"),
        ("run_weather_generator", "eval_max_grids"),
        ("apply_climate_perturbations", "qm_fit_method"),
        ("apply_climate_perturbations", "diagnostic"),
        # Restored by the weathergenr 2.0.0 upgrade: 1.2.0's wrapper dropped it,
        # 2.0.0 renamed it to `relax_order` and forwards it.
        ("generate_weather", "relax_order"),
    ],
)
def test_wg3_requires_the_surfaced_arguments(section, key):
    """C34: an argument surfaced into the config must be PINNED there.

    The whole point of surfacing was that an unexamined default is not a choice.
    If the key can silently vanish from the generated config, the R reads NULL
    and weathergenr takes its own default again -- which is the state C34 exists
    to end, restored without anything noticing. `diagnostic` is the sharpest
    case: NULL there changes the RETURN SHAPE and rule 3.07 fails outright.
    """
    cfg = _wg3_good()
    del cfg[section][key]
    diffs = ic.validate_wg3(cfg)
    assert diffs and any(f"{section}.{key}" in d for d in diffs)


def _catalog_entry_good(uri="X:/rlz.nc"):
    return {
        "uri": uri,
        "driver": {
            "name": "raster_xarray",
            "options": {"preprocess": "harmonise_dims", "lock": False},
        },
        "metadata": {"crs": 4326, "category": "meteo"},
        "data_type": "RasterDataset",
    }


def _wg5_good(keys=("run_01", "run_02")):
    return {k: _catalog_entry_good() for k in keys}


def test_wg5_synthetic_pass():
    assert ic.validate_wg5(_wg5_good()) == []


def test_wg5_synthetic_fail():
    cfg = _wg5_good()
    cfg["run_02"]["driver"]["name"] = "wrong_driver"  # bad driver
    assert ic.validate_wg5(cfg) != []


def _hm1_good():
    import numpy as np
    import xarray as xr

    return xr.Dataset(
        {v: (("latitude", "longitude"), np.zeros((2, 2))) for v in ic._HM1_REFERENCED},
        coords={
            "latitude": np.array([1.0, 2.0], dtype="float64"),
            "longitude": np.array([1.0, 2.0], dtype="float64"),
            "spatial_ref": 0,
        },
    )


def test_hm1_synthetic_pass():
    assert ic.validate_hm1(_hm1_good()) == []


def test_hm1_synthetic_fail():
    ds = _hm1_good().drop_vars("outlets")  # a referenced name missing
    assert ic.validate_hm1(ds) != []


def _hm2_good():
    import numpy as np
    import xarray as xr

    n = 3
    ds = xr.Dataset(
        {
            "precip": (
                ("time", "latitude", "longitude"),
                np.zeros((n, 2, 2), dtype="float32"),
                {"units": "mm d**-1", "unit": "mm", "grid_mapping": "spatial_ref"},
            ),
            # pet: unit attr ABSENT on purpose — proves asserted-if-present
            # never blocks when the attr is missing.
            "pet": (
                ("time", "latitude", "longitude"),
                np.zeros((n, 2, 2), dtype="float32"),
                {"grid_mapping": "spatial_ref"},
            ),
            "temp": (
                ("time", "latitude", "longitude"),
                np.zeros((n, 2, 2), dtype="float32"),
                {"unit": "degree C.", "grid_mapping": "spatial_ref"},
            ),
        },
        coords={
            "time": pd.date_range("2000-01-01", periods=n),
            "latitude": np.array([1.0, 2.0], dtype="float64"),
            "longitude": np.array([1.0, 2.0], dtype="float64"),
            "spatial_ref": 0,
        },
    )
    return ds


def test_hm2_synthetic_pass():
    # A present-but-correct unit (precip) + an absent unit (pet) both pass.
    assert ic.validate_hm2(_hm2_good()) == []


def test_hm2_synthetic_fail():
    ds = _hm2_good()
    ds["temp"].attrs["unit"] = "kelvin"  # present-but-wrong unit attr
    assert ic.validate_hm2(ds) != []


def _hm3_good():
    import geopandas as gpd
    from shapely.geometry import Point, Polygon

    region = gpd.GeoDataFrame(
        {"geometry": [Polygon([(0, 0), (1, 0), (1, 1), (0, 1)])]}, crs="EPSG:4326"
    )
    outlets = gpd.GeoDataFrame({"geometry": [Point(0.5, 0.5)]}, crs="EPSG:4326")
    outlet_index = pd.DataFrame(
        {"station_name": ["a"], "subcatchment_id": [1], "x": [0.5], "y": [0.5]}
    )
    return region, outlets, outlet_index


def test_hm3_synthetic_pass():
    assert ic.validate_hm3(*_hm3_good()) == []


def test_hm3_synthetic_fail():
    region, outlets, outlet_index = _hm3_good()
    region = region.to_crs("EPSG:3857")  # wrong CRS
    assert ic.validate_hm3(region, outlets, outlet_index) != []


def _hm4_good():
    return {
        "dir_output": ".",
        "model": {"cold_start__flag": True},
        "time": {
            "calendar": "standard",
            "starttime": "2070-01-01T00:00:00",
            "endtime": "2090-12-31T00:00:00",
            "timestepsecs": 86400,
        },
        "state": {"path_input": "in.nc", "path_output": "out.nc"},
        "input": {
            "path_static": "staticmaps.nc",
            "path_forcing": "inmaps.nc",
            "forcing": {
                "atmosphere_water__precipitation_volume_flux": "precip",
                "land_surface_water__potential_evaporation_volume_flux": "pet",
                "atmosphere_air__temperature": "temp",
            },
        },
        "output": {
            "csv": {
                "path": "output.csv",
                "column": [{"header": "Q", "map": "outlets", "parameter": "q"}],
            }
        },
    }


def test_hm4_synthetic_pass():
    assert ic.validate_hm4(_hm4_good()) == []


def test_hm4_synthetic_fail():
    cfg = _hm4_good()
    del cfg["time"]["timestepsecs"]  # a pinned rewrite field missing
    assert ic.validate_hm4(cfg) != []


def _hm5_good():
    return pd.DataFrame({"time": ["2070-01-01"], "Q_130000086": [1.0]})


def test_hm5_synthetic_pass():
    assert ic.validate_hm5(_hm5_good()) == []


def test_hm5_synthetic_fail():
    df = pd.DataFrame({"Q_130000086": [1.0]})  # no time column
    assert ic.validate_hm5(df) != []


def _hm7_row(metric, unit, location="101", value=1.0):
    return {
        "metric": metric,
        "location": location,
        "unit_id": str(unit).zfill(2),
        "value": value,
    }


def _hm7_contract():
    from dataclasses import asdict

    from blueearth_cst.experiment.metric_registry import declarations
    from blueearth_cst.experiment.response_inventory import make_response_request

    scenarios = pd.DataFrame(
        [
            {"run_id": "01", "evaluated": "true", "st_id": ""},
            {"run_id": "02", "evaluated": "true", "st_id": "1"},
            {"run_id": "03", "evaluated": "false", "st_id": "1"},
        ]
    )
    units = pd.DataFrame(
        [
            {"unit_id": "01", "grain": "run", "member_run_id": "01"},
            {"unit_id": "02", "grain": "run", "member_run_id": "02"},
            {"unit_id": "04", "grain": "bundle", "member_run_id": "01"},
            {"unit_id": "05", "grain": "bundle", "member_run_id": "02"},
        ]
    )
    registry = [asdict(item) for item in declarations(["q"])]
    rows = [
        _hm7_row(metric["name"], unit)
        for metric in registry
        for unit in (["04", "05"] if metric["grain"] == "bundle" else ["01", "02"])
    ]
    response = make_response_request(
        ["01", "02"],
        [
            {
                "variable": "q",
                "locations": ["101"],
                "units": "m3 s-1",
                "calendar": "standard",
                "timestep": "1 days",
                "time_label": "interval_end",
                "start": "2000-01-02",
                "end": "2001-01-01",
                "missing_value": None,
            }
        ],
    )
    return {"q": pd.DataFrame(rows)}, dict(
        unit_index=units,
        scenario_table=scenarios,
        declarations=registry,
        locations={"q": ["101"]},
        lookup=_wg2_good(st_num=1),
        unit_id_capacity=99,
        response_request=response,
    )


def test_hm7_successor_contract_passes_with_run_and_bundle_grains():
    tables, contract = _hm7_contract()
    assert ic.validate_hm7(tables, **contract) == []


@pytest.mark.parametrize(
    "mutation",
    [
        "header",
        "duplicate",
        "missing_key",
        "unknown_unit",
        "numeric_unit",
        "mixed_width",
        "member_absent",
        "member_unevaluated",
        "mixed_grain",
        "wrong_run_membership",
        "extra_bundle",
        "missing_bundle",
        "bad_bundle_membership",
        "capacity",
        "wrong_grain",
        "missing_location",
        "unknown_metric",
        "wrong_token",
        "missing_baseline",
        "missing_lookup_member",
        "infinity",
        "bundle_nan",
    ],
)
def test_hm7_successor_refuses_independent_contract_divergence(mutation):
    tables, contract = _hm7_contract()
    table, units = tables["q"], contract["unit_index"]
    if mutation == "header":
        tables["q"] = table.rename(columns={"unit_id": "st_id"})
    elif mutation == "duplicate":
        tables["q"] = pd.concat([table, table.iloc[:1]], ignore_index=True)
    elif mutation == "missing_key":
        tables["q"] = table.iloc[1:]
    elif mutation == "unknown_unit":
        table.loc[0, "unit_id"] = "99"
    elif mutation == "numeric_unit":
        table["unit_id"] = table["unit_id"].astype(object)
        table.loc[0, "unit_id"] = 1
    elif mutation == "mixed_width":
        units.loc[0, "unit_id"] = "1"
    elif mutation in {"member_absent", "member_unevaluated"}:
        units.loc[2, "member_run_id"] = "99" if mutation == "member_absent" else "03"
    elif mutation == "mixed_grain":
        contract["unit_index"] = pd.concat(
            [
                units,
                pd.DataFrame(
                    [{"unit_id": "04", "grain": "run", "member_run_id": "01"}]
                ),
            ],
            ignore_index=True,
        )
    elif mutation == "wrong_run_membership":
        units.loc[0, "member_run_id"] = "02"
    elif mutation == "extra_bundle":
        contract["unit_index"] = pd.concat(
            [
                units,
                pd.DataFrame(
                    [{"unit_id": "06", "grain": "bundle", "member_run_id": "01"}]
                ),
            ],
            ignore_index=True,
        )
    elif mutation == "missing_bundle":
        contract["unit_index"] = units.iloc[:-1]
        tables["q"] = table[table.unit_id != "05"]
    elif mutation == "bad_bundle_membership":
        units.loc[2, "member_run_id"] = "02"
    elif mutation == "capacity":
        contract["unit_id_capacity"] = 4
    elif mutation == "wrong_grain":
        table.loc[0, "unit_id"] = "04"
    elif mutation == "missing_location":
        contract["locations"]["q"].append("102")
    elif mutation == "unknown_metric":
        table.loc[0, "metric"] = "q_made_up"
    elif mutation == "wrong_token":
        tables["aet"] = tables.pop("q")
    elif mutation == "missing_baseline":
        contract["scenario_table"].loc[0, "st_id"] = "1"
    elif mutation == "missing_lookup_member":
        contract["lookup"] = _wg2_good(st_num=2)
    elif mutation == "infinity":
        table.loc[0, "value"] = float("inf")
    elif mutation == "bundle_nan":
        table.loc[table.unit_id == "04", "value"] = float("nan")
    assert ic.validate_hm7(tables, **contract)


def test_hm7_native_run_nan_policy_is_preserved():
    tables, contract = _hm7_contract()
    tables["q"].loc[tables["q"].unit_id == "01", "value"] = float("nan")
    assert ic.validate_hm7(tables, **contract) == []


@pytest.mark.parametrize(
    "field,value",
    [
        ("units", "mm"),
        ("calendar", "noleap"),
        ("timestep", "2 days"),
        ("time_label", "interval_start"),
        ("end", "1999-01-01"),
    ],
)
def test_hm7_checks_retained_response_physical_basis(field, value):
    tables, contract = _hm7_contract()
    contract["response_request"]["variables"][0][field] = value
    assert any(
        "physical/time basis" in item for item in ic.validate_hm7(tables, **contract)
    )


def _gauge_identity_good():
    toml_cfg = {
        "output": {
            "csv": {
                "path": "output.csv",
                "column": [{"header": "Q", "map": "outlets", "parameter": "q"}],
            }
        }
    }
    output_rlz = pd.DataFrame({"time": ["2070-01-01"], "Q_130000086": [1.0]})
    # R11 CR-2: locations are ROWS now, so check 3 compares the `location` value
    # set rather than subtracting non-gauge columns out of a wide header.
    qstats = pd.DataFrame([_hm7_row("q_annual_mean", 1, location="130000086")])
    return toml_cfg, output_rlz, qstats


def test_gauge_identity_synthetic_pass():
    assert ic.validate_hm_gauge_column_identity(*_gauge_identity_good()) == []


def test_gauge_identity_synthetic_fail():
    toml_cfg, output_rlz, qstats = _gauge_identity_good()
    # Break exactly ONE member of the correlated set: change the q table's
    # location so check 3 fires while TOML + output_rlz still agree.
    qstats = pd.DataFrame([_hm7_row("q_annual_mean", 1, location="999999999")])
    assert ic.validate_hm_gauge_column_identity(toml_cfg, output_rlz, qstats) != []


# --- C28: st_id and the cached-copy consistency check ------------------------


def test_catalog_runs_validates_per_file_and_exact_evaluated_set():
    catalogs = {run: _wg5_good(keys=(f"run_{run}",)) for run in ("01", "03")}
    assert ic.validate_wg5_catalog_runs(catalogs, ["01", "03"]) == []
    catalogs["03"] = _wg5_good(keys=("run_01",))
    assert ic.validate_wg5_catalog_runs(catalogs, ["01", "03"])


def test_catalog_runs_refuses_missing_evaluated_run_and_legacy_selector():
    catalogs = {"01": _wg5_good(keys=("run_01",))}
    assert ic.validate_wg5_catalog_runs(catalogs, ["01", "03"])
    assert "no 'run_<run_id>'" in ic.validate_wg5(_wg5_good(keys=("rlz_1_st_0",)))[0]


def _wg4_good():
    import numpy as np
    import xarray as xr

    n = 3
    return xr.Dataset(
        {
            "precip": (("time", "lat", "lon"), np.zeros((n, 2, 2), dtype="float32")),
            "temp": (("time", "lat", "lon"), np.zeros((n, 2, 2), dtype="float32")),
        },
        coords={
            "time": pd.date_range("2070-01-01", periods=n),
            "lat": np.array([1.0, 2.0]),
            "lon": np.array([1.0, 2.0]),
            "spatial_ref": 0,
        },
        attrs={"crs": 4326, "category": "meteo"},
    )


def test_wg4_synthetic_pass():
    assert ic.validate_wg4(_wg4_good()) == []


def test_wg4_synthetic_fail():
    ds = _wg4_good().drop_vars("precip")  # missing a required variable
    assert ic.validate_wg4(ds) != []


def test_wg4_crs_category_absent_is_ok():
    """Empty global attrs must PASS — the real artifact's actual shape.

    Corrected 2026-07-25 on the first --notemp capture: the generator NC carries
    no global attrs at all. Its CRS lives in the spatial_ref coord (CF/rioxarray)
    and crs/category are catalog metadata that validate_wg5 pins. Requiring them
    here asserted the right values on the wrong surface.
    """
    ds = _wg4_good()
    ds.attrs = {}
    assert ic.validate_wg4(ds) == []


@pytest.mark.parametrize(
    "attrs",
    [
        {"crs": 3857},  # contradictory crs
        {"category": "hydro"},  # contradictory category
        {"crs": 4326, "category": "hydro"},  # one right, one wrong
    ],
)
def test_wg4_contradictory_crs_category_still_fails(attrs):
    """Asserted-if-present keeps its teeth: a PRESENT wrong value is a violation."""
    ds = _wg4_good()
    ds.attrs = attrs
    assert ic.validate_wg4(ds) != []


def test_wg6_synthetic_pass():
    # WG-6 shares HM-2's contract — reuse the conforming HM-2 object.
    assert ic.validate_wg6(_hm2_good()) == []


def test_wg6_synthetic_fail():
    ds = _hm2_good().drop_vars("pet")  # missing a required forcing variable
    assert ic.validate_wg6(ds) != []


def _hm6b_good():
    import numpy as np
    import xarray as xr

    return xr.Dataset(
        {"river_h": (("latitude", "longitude"), np.zeros((2, 2)))},
        coords={
            "latitude": np.array([1.0, 2.0]),
            "longitude": np.array([1.0, 2.0]),
        },
    )


def test_hm6b_synthetic_pass():
    assert ic.validate_hm6b(_hm6b_good()) == []


def test_hm6b_synthetic_fail():
    import xarray as xr

    ds = xr.Dataset()  # no grid axes, no state variables
    assert ic.validate_hm6b(ds) != []


# ===========================================================================
# Layer 2 — real-fixture integration (skipif _FIXTURE_ABSENT)
# ===========================================================================
#
# Each case opens a persisted fixture artifact and asserts the validator's
# report is empty. The 12 continuously-verified checks: 10 per-artifact
# (WG-1,2,3,5; HM-1,2,3,4,5,7) + 2 relational (gauge-identity — parametrized
# over the 12 (toml, output_rlz) pairs; catalog-grid).


def _open_ds(path):
    import xarray as xr

    return xr.open_dataset(path)


def _store_key() -> str:
    """Derive the historical-store key from the config the FIXTURE recorded.

    This was the literal ``era5_20000101_20201231`` until 2026-08-12, which
    pinned the test to one window rather than to the fixture. The 2026-08-10
    config trim (``endtime`` 2020-12-31 -> 2016-12-31) moved the store to
    ``era5_20000101_20161231``, and the test kept passing only because the
    superseded store was still lying on disk beside the live one. It failed the
    moment `prune_climate_store.py --delete` removed the orphan — on a fixture
    that was correct. Same lesson as the `_STORE_ROOT` block above: derive the
    location, never spell it.

    R14 moved both keys — `shared.clim_historical` -> `climate.selected`
    (`C-44`) and `shared.historical_window`'s ISO pair -> `climate.window`'s
    inclusive YEARS (`C-70`) — and this reader was missed, because the fixture
    it reads was still a v1 snapshot until the Gate 5 rebuild. It went through
    the migration green and failed the moment the fixture caught up. The
    conversion back to a day-resolution key goes through the same helper
    `climate_store_rule` uses, so this cannot become a second implementation of
    the key.
    """
    with open(_WF1_SNAPSHOT) as f:
        climate = yaml.safe_load(f)["climate"]
    _start, _end = historical_window_bounds(climate["window"])
    slug = slugify_window(_start.isoformat(), _end.isoformat())
    return f"{climate['selected']}_{slug}"


@pytest.mark.skipif(not _fixture_present(), reason=_FIXTURE_ABSENT)
@pytest.mark.skipif(not _wf1_snapshot_present(), reason=_FIXTURE_PRE_R14)
def test_wg1_integration():
    path = join(_STORE_ROOT, _store_key(), "extract_historical.nc")
    with _open_ds(path) as ds:
        assert ic.validate_wg1(ds) == []


_PRE_LOOKUP_GRID = (
    "fixture predates the stress-test lookup (per-member _work/st_<m>.csv); "
    "regenerated by the migration's WF3 re-run"
)


@pytest.mark.skipif(not _fixture_present(), reason=_FIXTURE_ABSENT)
def test_wg2_integration():
    _, collection, scenarios = _successor_artifacts()
    lookup = pd.read_csv(collection / "stress_test_lookup.csv", dtype={"st_id": str})
    assert ic.validate_wg2(lookup) == []
    assert set(scenarios.st_id) == set(lookup.st_id) | {""}


@pytest.mark.skipif(not _fixture_present(), reason=_FIXTURE_ABSENT)
def test_wg3_integration():
    import json
    from pathlib import Path

    _, collection, _ = _successor_artifacts()
    plans = [
        p
        for p in (Path(_FIXTURE) / "scenarios" / "requests").glob("*/request.json")
        if json.loads(p.read_text())["collection_id"] == collection.name
    ]
    assert plans, "no generation plan for the consumed collection"
    for plan in plans:
        cfg = yaml.safe_load(
            (plan.parent / "generation/config/weathergen_config.yml").read_text()
        )
        assert ic.validate_wg3(cfg) == []


@pytest.mark.skipif(not _fixture_present(), reason=_FIXTURE_ABSENT)
def test_wg5_integration():
    from pathlib import Path

    runs = _evaluated_runs()
    paths = [Path(_RUNS_DIR) / "config" / f"run_{run}.yml" for run in runs]
    if not any(p.exists() for p in paths):
        pytest.skip(_TEMP_ABSENT)
    for p in paths:
        assert ic.validate_wg5(yaml.safe_load(p.read_text())) == []


@pytest.mark.skipif(not _fixture_present(), reason=_FIXTURE_ABSENT)
def test_wg5_catalog_runs_integration():
    from pathlib import Path

    runs = _evaluated_runs()
    paths = {run: Path(_RUNS_DIR) / "config" / f"run_{run}.yml" for run in runs}
    if not any(p.exists() for p in paths.values()):
        pytest.skip(_TEMP_ABSENT)
    catalogs = {run: yaml.safe_load(p.read_text()) for run, p in paths.items()}
    assert ic.validate_wg5_catalog_runs(catalogs, runs) == []


@pytest.mark.skipif(not _fixture_present(), reason=_FIXTURE_ABSENT)
def test_hm1_integration():
    with _open_ds(join(_MODEL_DIR, "staticmaps.nc")) as ds:
        assert ic.validate_hm1(ds) == []


@pytest.mark.skipif(not _fixture_present(), reason=_FIXTURE_ABSENT)
def test_hm2_integration():
    path = join(_MODEL_DIR, "forcing", "inmaps_historical.nc")
    with _open_ds(path) as ds:
        assert ic.validate_hm2(ds) == []


@pytest.mark.skipif(not _fixture_present(), reason=_FIXTURE_ABSENT)
def test_hm3_integration():
    import geopandas as gpd

    geoms = join(_MODEL_DIR, "staticgeoms")
    region = gpd.read_file(join(geoms, "region.geojson"))
    outlets = gpd.read_file(join(geoms, "outlets.geojson"))
    outlet_index = pd.read_csv(join(geoms, "outlet_index.csv"))
    assert ic.validate_hm3(region, outlets, outlet_index) == []


@pytest.mark.skipif(not _fixture_present(), reason=_FIXTURE_ABSENT)
def test_hm4_integration():
    import tomllib
    from pathlib import Path

    for run in _evaluated_runs():
        path = Path(_RUNS_DIR) / "config" / f"run_{run}.toml"
        assert (
            ic.validate_hm4(tomllib.loads(path.read_text()), require_output_state=False)
            == []
        )


@pytest.mark.skipif(not _fixture_present(), reason=_FIXTURE_ABSENT)
def test_hm5_integration_wf4():
    from pathlib import Path

    for run in _evaluated_runs():
        assert (
            ic.validate_hm5(pd.read_csv(Path(_RUNS_DIR) / "output" / f"run_{run}.csv"))
            == []
        )


@pytest.mark.skipif(not _fixture_present(), reason=_FIXTURE_ABSENT)
def test_hm5_integration_wf1():
    """wf1's half of HM-5, which is temp() from 2026-08-10.

    Split from the wf3 case rather than guarded inside it: a `pytest.skip` in a
    combined test reports the WHOLE test as skipped, so the persisted wf3
    assertion would silently stop counting whenever the wf1 artifact was
    absent -- which is now the normal state after a run.

    This read was unguarded until the temp() change and passed only on a
    fixture still holding a pre-change `output.csv`; on a correct run it would
    have raised FileNotFoundError.
    """
    wf1_csv = join(_MODEL_DIR, "run_default", "output.csv")
    if not os.path.exists(wf1_csv):
        pytest.skip(_TEMP_ABSENT)
    assert ic.validate_hm5(pd.read_csv(wf1_csv)) == []


@pytest.mark.skipif(not _fixture_present(), reason=_FIXTURE_ABSENT)
def test_hm7_integration():
    import json

    from blueearth_cst.experiment.metric_plan import read_metric_set

    root, collection, scenarios = _successor_artifacts()
    markers = list((root / "results/metric_sets").glob("*/metrics.json"))
    assert markers, "completed successor fixture has no ready metric set"
    intent = json.loads((collection / "collection_intent.json").read_text())
    request = json.loads((root / "config/response_request.json").read_text())
    for marker in markers:
        manifest = read_metric_set(root, marker)
        tables = {
            item["token"]: pd.read_csv(
                marker.parent / item["path"], dtype={"unit_id": str, "location": str}
            )
            for item in manifest["indicator_tables"]
        }
        assert (
            ic.validate_hm7(
                tables,
                unit_index=pd.read_csv(marker.parent / "unit_index.csv", dtype=str),
                scenario_table=scenarios,
                declarations=manifest["declarations"],
                locations={
                    item["variable"]: item["locations"] for item in request["variables"]
                },
                lookup=pd.read_csv(
                    collection / "stress_test_lookup.csv", dtype={"st_id": str}
                ),
                unit_id_capacity=intent["unit_id_capacity"],
                response_request=request,
            )
            == []
        )


@pytest.mark.skipif(not _fixture_present(), reason=_FIXTURE_ABSENT)
def test_gauge_identity_integration():
    import tomllib
    from pathlib import Path

    root, _, _ = _successor_artifacts()
    tables = list((root / "results/metric_sets").glob("*/q_indicators.csv"))
    assert tables
    for run in _evaluated_runs():
        toml = Path(_RUNS_DIR) / "config" / f"run_{run}.toml"
        output = Path(_RUNS_DIR) / "output" / f"run_{run}.csv"
        for table in tables:
            assert (
                ic.validate_hm_gauge_column_identity(
                    tomllib.loads(toml.read_text()),
                    pd.read_csv(output),
                    pd.read_csv(table),
                )
                == []
            )


# --- temp() content integration cases — doubly skip-guarded (commit-4) ------
#
# Each carries BOTH the fixture-absent skipif (Layer-2 convention) AND a
# temp-absent runtime skip with the documented reason, since the temp()
# artifact is deleted after its consumer finishes and is absent on the default
# fixture. The ``--notemp`` capture procedure (both seam docs' validator
# indexes) un-skips these on disk without a design change.

_TEMP_ABSENT = "temp() artifact absent; capture via --notemp"

# Fixture temp() paths (present only after a --notemp capture run). R9 P2 also
# flattened the member naming here: the rlz_<r>/ directory level dissolved and
# the index went back into the stem, so these are `inmaps_rlz_1_st_1.nc`, not
# `rlz_1/forcing/inmaps_st_1.nc`. Unlike the persisted cases above these fail
# SILENTLY when stale -- the runtime `os.path.exists` guard reads a wrong path as
# "temp artifact absent" and skips, so a stale path here is indistinguishable
# from a normal run. That is why they are derived from the same roots. R11 P2's
# `cst_` -> `st_` rename is a second reason they read absent today; unlike the
# persisted cases it needs no `_member_artifact` guard, because these skip on
# the default fixture either way.


@pytest.mark.skipif(not _fixture_present(), reason=_FIXTURE_ABSENT)
def test_wg4_integration():
    _, collection, scenarios = _successor_artifacts()
    for run in scenarios.run_id:
        with _open_ds(collection / "forcing" / f"run_{run}.nc") as ds:
            assert ic.validate_wg4(ds) == []


@pytest.mark.skipif(not _fixture_present(), reason=_FIXTURE_ABSENT)
def test_wg6_integration():
    from pathlib import Path

    paths = [
        Path(_RUNS_DIR) / "forcing" / f"inmaps_run_{run}.nc"
        for run in _evaluated_runs()
    ]
    if not any(p.exists() for p in paths):
        pytest.skip(_TEMP_ABSENT)
    for path in paths:
        with _open_ds(path) as ds:
            assert ic.validate_wg6(ds) == []


@pytest.mark.skipif(not _fixture_present(), reason=_FIXTURE_ABSENT)
def test_hm6b_integration():
    from pathlib import Path

    paths = [
        Path(_RUNS_DIR) / "output" / f"outstates_run_{run}.nc"
        for run in _evaluated_runs()
    ]
    if not any(p.exists() for p in paths):
        pytest.skip(_TEMP_ABSENT)
    for path in paths:
        with _open_ds(path) as ds:
            assert ic.validate_hm6b(ds) == []
