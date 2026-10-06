"""Canonical WF0 declaration, missing-data and table round-trip contracts."""

from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from blueearth_cst.climate_analysis.diagnostic_outputs import (
    TABLES,
    diagnostic_comparison_outputs,
    diagnostic_source_outputs,
)
from blueearth_cst.climate_analysis.diagnostic_render import load_result, render
from blueearth_cst.climate_analysis.diagnostic_settings import parse_settings
from blueearth_cst.climate_analysis.diagnostic_tables import compute, write_tables


def test_canonical_inventory_and_one_source_refusal():
    settings = parse_settings(None, {"start": 2000, "end": 2016}, ["era5", "chirps"])
    era5 = diagnostic_source_outputs("era5", "era5", settings)
    chirps = diagnostic_source_outputs("chirps", "chirps", settings)
    comparison = diagnostic_comparison_outputs(
        "comparison", ["era5", "chirps"], settings
    )
    assert [len(x["figures"]) for x in (era5, chirps, comparison)] == [21, 17, 17]
    assert all(
        p.endswith(".png")
        for x in (era5, chirps, comparison)
        for p in x["figures"].values()
    )
    assert "_engine/figure_captions.json" in era5["render"]["captions_json"].replace(
        "\\", "/"
    )
    with pytest.raises(ValueError, match="two sources"):
        diagnostic_comparison_outputs("comparison", ["era5"], settings)
    with pytest.raises(ValueError, match="registered"):
        parse_settings(
            {"subbasin_figures": True}, {"start": 2000, "end": 2016}, ["era5"]
        )


@pytest.mark.parametrize("kind", ["zero", "constant", "missing", "no_overlap"])
def test_unavailable_records_keep_table_headers_and_round_trip(tmp_path, kind):
    idx = pd.date_range("2000-01-01", "2005-12-31")
    p = np.zeros(len(idx)) if kind == "zero" else np.ones(len(idx))
    if kind == "missing":
        p[:] = np.nan
    daily = pd.DataFrame({"precip": p, "temp": np.nan}, index=idx)
    settings = parse_settings(None, {"start": 2000, "end": 2005}, ["chirps"])
    period = (1990, 1995) if kind == "no_overlap" else (2000, 2005)
    _, tables = compute(daily, settings, 1, period)
    assert set(tables) == set(TABLES)
    assert all(len(t.columns) for t in tables.values())
    paths = diagnostic_source_outputs(tmp_path, "chirps", settings)
    write_tables(paths, {"chirps": tables}, settings, 1, period, {})
    assert all(Path(paths["compute"][k]).is_file() for k in TABLES)
    loaded = load_result(paths["root"], "chirps")
    assert loaded["tclim"] is None
    if kind in {"missing", "no_overlap"}:
        paths["figures"].pop("map-precip")
        records = render(paths, settings, 1, ["chirps"], [paths["root"]])
        assert len(records) == 16
        assert all((Path(paths["root"]) / p).is_file() for p in records)
        series = next(r for p, r in records.items() if "annual_trend_ts" in p)
        assert series["availability"].startswith("Unavailable")
        assert "not scientifically qualified" in series["caption"]


def test_opt_in_subbasin_tables_pngs_and_caption_inventory(tmp_path):
    import json
    from types import SimpleNamespace

    from blueearth_cst.climate_analysis.diagnostic_subbasins import render_subbasins
    from blueearth_cst.climate_analysis.diagnostic_tables import write_json

    settings = parse_settings(
        {"captioned_figures": True}, {"start": 2000, "end": 2016}, ["era5", "chirps"]
    )
    settings["subbasin_figures"] = True
    folders = []
    idx = pd.date_range("2000-01-01", "2016-12-31")
    rng = np.random.default_rng(3)
    for source in ("era5", "chirps"):
        folder = tmp_path / source / "tables" / "subbasins"
        folders.append(str(folder))
        sub = folder / "subbasin_101"
        sub.mkdir(parents=True)
        frame = pd.DataFrame(
            {
                "precip": rng.gamma(0.6, 8, len(idx)),
                "temp": rng.normal(25, 2, len(idx)) if source == "era5" else np.nan,
            },
            index=idx,
        )
        frame.index.name = "date"
        frame.to_csv(sub / "daily_basin.csv")
        _, tables = compute(frame, settings, 1, (2000, 2016))
        for name in (
            "precip_climatology",
            "temp_climatology",
            "annual_indices",
            "trends",
        ):
            tables[name].to_csv(sub / f"{name}.csv", index=False)
    for sources in (["era5"], ["era5", "chirps"]):
        root = tmp_path / ("era5" if len(sources) == 1 else "comparison")
        write_json(
            root / "_engine" / "figure_captions.json",
            {"schema_version": 1, "figures": {}},
        )
        output = SimpleNamespace(
            subbasin_figures=str(root / "figures" / "subbasins"),
            captioned_subbasins=str(root / "figures" / "captioned" / "subbasins"),
            subbasin_tables=str(root / "tables" / "subbasins"),
        )
        sm = SimpleNamespace(
            params=SimpleNamespace(subbasin_table_dirs=folders[: len(sources)], m0=1),
            output=output,
        )
        render_subbasins(sm, settings, sources)
        records = json.loads((root / "_engine" / "figure_captions.json").read_text())[
            "figures"
        ]
        assert len(records) == (3 if len(sources) == 1 else 2)
        assert all(
            (root / path).is_file() and (root / r["captioned_path"]).is_file()
            for path, r in records.items()
        )
        assert (
            root / "tables" / "subbasins" / "subbasin_101" / "annual_indices.csv"
        ).is_file()


def test_exact_basin_mask_and_unresolved_temperature_units(tmp_path):
    import xarray as xr

    from blueearth_cst.climate_analysis.diagnostic_tables import daily_series

    ds = xr.Dataset(
        {
            "precip": (("time", "latitude", "longitude"), np.ones((3, 2, 2))),
            "temp": (("time", "latitude", "longitude"), np.full((3, 2, 2), 300.0)),
        },
        coords={
            "time": pd.date_range("2000-01-01", periods=3),
            "latitude": [0.0, 1.0],
            "longitude": [10.0, 11.0],
        },
    )
    ds.temp.attrs["units"] = "K"
    nc = tmp_path / "climate.nc"
    ds.to_netcdf(nc)
    cells = tmp_path / "basin_cells.csv"
    pd.DataFrame({"latitude": [0.0], "longitude": [10.0]}).to_csv(cells, index=False)
    frame, lineage = daily_series(nc, cells, "era5")
    assert frame.precip.eq(1.0).all() and frame.temp.isna().all()
    assert "unresolved" in lineage["warnings"][0]
    pd.DataFrame({"latitude": [0.0, 3.0], "longitude": [10.0, 10.0]}).to_csv(
        cells, index=False
    )
    with pytest.raises(ValueError, match="every declared cell"):
        daily_series(nc, cells, "era5")
