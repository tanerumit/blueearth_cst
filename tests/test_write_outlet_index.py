"""Tests for src/write_outlet_index.py (R3 sections 4, 8).

Uses real geopandas/shapely (installed, not stubbed) to round-trip a tiny
outlets.geojson — no hydromt or model build involved.
"""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.write_outlet_index import build_outlet_index, write_outlet_index  # noqa: E402


def _tiny_outlets(path):
    import geopandas as gpd
    from shapely.geometry import Point

    gdf = gpd.GeoDataFrame(
        {"fid": [130000086, 5]},
        geometry=[Point(9.6625, 0.44583), Point(10.0, 1.0)],
        crs="EPSG:4326",
    )
    gdf.to_file(path, driver="GeoJSON")


def test_build_outlet_index_positional_naming(tmp_path):
    outlets = tmp_path / "outlets.geojson"
    _tiny_outlets(outlets)
    df = build_outlet_index(outlets)
    assert list(df["station_name"]) == ["wflow_1", "wflow_2"]
    assert list(df["subcatchment_id"]) == [130000086, 5]
    assert df["x"].tolist() == pytest.approx([9.6625, 10.0])
    assert df["y"].tolist() == pytest.approx([0.44583, 1.0])


def test_write_outlet_index_creates_csv(tmp_path):
    outlets = tmp_path / "outlets.geojson"
    _tiny_outlets(outlets)
    out = tmp_path / "sub" / "outlet_index.csv"  # parent does not exist yet
    write_outlet_index(outlets, out)
    header = out.read_text(encoding="utf-8").splitlines()[0]
    assert header == "station_name,subcatchment_id,x,y"
