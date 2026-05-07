from __future__ import annotations

import sys
import types
from datetime import datetime
from pathlib import Path

import numpy as np

sys.modules.setdefault("geopandas", types.SimpleNamespace())
sys.modules.setdefault("rasterio", types.SimpleNamespace())
sys.modules.setdefault("rasterio.windows", types.SimpleNamespace())
sys.modules.setdefault("xarray", types.SimpleNamespace(Dataset=object))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "dev" / "scripts"))
import stage_data  # noqa: E402


class _FakeArray:
    def __init__(self, dims, sizes, encoding=None):
        self.dims = tuple(dims)
        self.sizes = dict(sizes)
        self.encoding = dict(encoding or {})
        self.chunks = None


class _FakeDataset:
    def __init__(self):
        self.data_vars = {
            "tp": _FakeArray(
                ("time", "lat", "lon"),
                {"time": 800, "lat": 5, "lon": 7},
                {
                    "chunks": (1, 721, 1440),
                    "compressor": "source-compressor",
                    "_FillValue": np.float32(-9999),
                },
            ),
            "station_id": _FakeArray(("station",), {"station": 3}),
        }

    def __getitem__(self, name):
        return self.data_vars[name]

    def chunk(self, chunks):
        for array in self.data_vars.values():
            array.chunks = tuple(
                tuple(
                    chunks.get(dim, array.sizes[dim])
                    for _ in range(
                        array.sizes[dim] // chunks.get(dim, array.sizes[dim])
                    )
                )
                + (
                    (array.sizes[dim] % chunks.get(dim, array.sizes[dim]),)
                    if array.sizes[dim] % chunks.get(dim, array.sizes[dim])
                    else ()
                )
                for dim in array.dims
            )
        return self


def test_zarr_subset_write_plan_rechunks_daily_meteo_subset() -> None:
    rechunked, encoding = stage_data._zarr_subset_write_plan(_FakeDataset())

    assert rechunked["tp"].chunks == ((365, 365, 70), (5,), (7,))
    assert encoding["tp"]["chunks"] == (365, 5, 7)
    assert encoding["tp"]["compressor"] == "source-compressor"
    assert encoding["tp"]["_FillValue"] == np.float32(-9999)
    assert "station_id" not in encoding


def test_raster_output_profile_uses_tiling_for_larger_geotiffs() -> None:
    profile = {
        "driver": "GTiff",
        "height": 2000,
        "width": 3000,
        "transform": "old",
        "blockxsize": 512,
        "blockysize": 512,
    }

    out = stage_data._raster_output_profile(
        profile,
        height=600,
        width=700,
        transform="new",
    )

    assert out["height"] == 600
    assert out["width"] == 700
    assert out["transform"] == "new"
    assert out["compress"] == "deflate"
    assert out["tiled"] is True
    assert out["blockxsize"] == 256
    assert out["blockysize"] == 256


def test_raster_output_profile_keeps_tiny_geotiffs_striped() -> None:
    out = stage_data._raster_output_profile(
        {"driver": "GTiff"},
        height=12,
        width=20,
        transform="new",
    )

    assert out["tiled"] is False
    assert "blockxsize" not in out
    assert "blockysize" not in out


def test_validate_lonlat_crs_rejects_projected_crs() -> None:
    crs = types.SimpleNamespace(is_geographic=False, to_string=lambda: "EPSG:3857")

    try:
        stage_data._validate_lonlat_crs(crs, "raster", Path("source.tif"))
    except ValueError as exc:
        assert "bbox is lon/lat" in str(exc)
        assert "EPSG:3857" in str(exc)
    else:
        raise AssertionError("expected ValueError")


def test_validate_lonlat_crs_accepts_epsg_4326_string() -> None:
    stage_data._validate_lonlat_crs("EPSG:4326", "vector", Path("source.gpkg"))


def test_vector_read_kwargs_include_optional_columns() -> None:
    assert stage_data._vector_read_kwargs((1, 2, 3, 4), ["geometry", "id"]) == {
        "bbox": (1, 2, 3, 4),
        "columns": ["geometry", "id"],
    }


def test_raster_glob_workers_are_bounded_and_configurable() -> None:
    assert stage_data._raster_glob_workers({"workers": 2}, file_count=10) == 2
    assert stage_data._raster_glob_workers({}, file_count=10) == 4
    assert stage_data._raster_glob_workers({}, file_count=2) == 1


def test_completion_detail_appends_timestamp_and_elapsed_time() -> None:
    finished_at = datetime(2026, 5, 7, 12, 34, 56)

    assert stage_data._completion_detail("12.3 MB", finished_at, 1.24) == (
        "12.3 MB; completed: 12:34:56; elapsed: 1.2s"
    )


def test_completion_detail_handles_empty_detail() -> None:
    finished_at = datetime(2026, 5, 7, 12, 34, 56)

    assert stage_data._completion_detail("", finished_at, 61.0) == (
        "completed: 12:34:56; elapsed: 1m01s"
    )


def test_format_bytes_uses_readable_units() -> None:
    assert stage_data._format_bytes(0) == "0 B"
    assert stage_data._format_bytes(1_500) == "1.5 KB"
    assert stage_data._format_bytes(2_500_000) == "2.5 MB"
    assert stage_data._format_bytes(3_500_000_000) == "3.5 GB"


def test_total_output_bytes_sums_written_and_existing_results() -> None:
    results = [
        ("written", "a", "detail", 1_000),
        ("exists", "b", "detail", 2_000),
        ("skipped", "c", "detail", 4_000),
        ("failed", "d", "detail", 8_000),
    ]

    assert stage_data._total_output_bytes(results) == 3_000
