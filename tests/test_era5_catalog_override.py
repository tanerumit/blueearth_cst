"""Contracts for the project-owned Deltares ERA5 Zarr catalog override."""

from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
BASE_CATALOG = "config/catalogs/deltares_data.yml"
ERA5_OVERRIDE = "config/catalogs/deltares_era5_daily_zarr.yml"


def test_rapid_config_composes_original_base_then_era5_override():
    """The rapid project replaces ERA5 without moving unrelated sources."""
    project = yaml.safe_load(
        (ROOT / "test_case/project_config_rapid.yml").read_text(encoding="utf-8")
    )
    catalogs = project["project"]["catalog"]

    assert catalogs == [BASE_CATALOG, ERA5_OVERRIDE]

    base_sources = yaml.safe_load((ROOT / BASE_CATALOG).read_text(encoding="utf-8"))
    override = yaml.safe_load((ROOT / ERA5_OVERRIDE).read_text(encoding="utf-8"))
    era5 = override["era5"]
    composed_sources = {**base_sources, **override}

    assert set(composed_sources) == set(base_sources)
    for name in base_sources.keys() - {"era5", "meta"}:
        assert composed_sources[name] == base_sources[name]
    assert override["meta"]["roots"][0].lower() == "p:/wflow_global/hydromt"
    assert era5["uri"].endswith("meteo/era5_daily.zarr")
    assert era5["driver"] == {
        "name": "raster_xarray",
        "options": {"chunks": {}},
    }
    assert era5["metadata"]["extent"]["time_range"] == {
        "start": "1950-01-02",
        "end": "2023-02-01",
    }
