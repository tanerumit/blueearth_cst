"""Stage a bbox subset of a remote data root to a local SSD.

What it does
------------
Mirrors the source directory tree under a local root, clipping each dataset
to a bbox so only a fraction of bytes lands locally. The matching data
catalog yaml then just needs its ``meta.root`` swapped to the local path.

Configuration
-------------
All knobs live in a YAML file (default: ``dev/scripts/stage_data.yml``):

    source_root: P:/wflow_global/hydromt
    target_root: C:/data/wflow_global/hydromt
    bbox: [8.5, -0.5, 11.0, 1.5]   # west, south, east, north
    datasets:
      - {name: vito,  type: raster,      path: landuse/vito/.../foo.tif}
      - {name: tiles, type: raster_glob, path: topography/.../30sec, pattern: "*.tif", workers: 4}
      - {name: idx,   type: vector,      path: topography/.../basin_index.gpkg,
         columns: [geometry, id]}
      - {name: era5,  type: zarr,        path: meteo/era5_daily.zarr}
      - {name: orog,  type: netcdf,      path: meteo/.../era5_orography_2018.nc}

Usage
-----
    python dev/scripts/stage_data.py
    python dev/scripts/stage_data.py --config dev/scripts/stage_data.yml
    python dev/scripts/stage_data.py --bbox 8 -1 12 2     # CLI overrides
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import sys
import traceback
from concurrent.futures import ThreadPoolExecutor, as_completed
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from time import perf_counter

# GDAL/SMB performance tuning. Set as defaults so a user-set env wins.
# Must be set BEFORE geopandas/rasterio import — GDAL reads these once at
# library init.
# - GDAL_CACHEMAX: raster block cache size (MB).
# - VSI_CACHE / VSI_CACHE_SIZE: read-side cache for any VSI handler.
# - GDAL_DISABLE_READDIR_ON_OPEN=EMPTY_DIR: skip the per-open directory scan
#   GDAL does looking for sidecars (.aux.xml, .ovr, etc.). Each scan is
#   another SMB round-trip; on a network drive this is the single biggest
#   per-file overhead reduction.
os.environ.setdefault("GDAL_CACHEMAX", "512")
os.environ.setdefault("VSI_CACHE", "TRUE")
os.environ.setdefault("VSI_CACHE_SIZE", "10000000")
os.environ.setdefault("GDAL_DISABLE_READDIR_ON_OPEN", "EMPTY_DIR")

import geopandas as gpd
import rasterio
import rasterio.windows
import xarray as xr
import yaml

try:
    from dask.diagnostics import ProgressBar  # type: ignore[import-untyped]
except ImportError:
    ProgressBar = None  # type: ignore[assignment]

try:
    from tqdm import tqdm  # type: ignore[import-untyped]
except ImportError:
    tqdm = None  # type: ignore[assignment]

# Make `console.py` importable when running from the repo root.
sys.path.insert(0, str(Path(__file__).resolve().parent))
from console import banner, bold, cyan, dim, fmt_path, green, pad, red, yellow  # noqa: E402

CONFIG_DEFAULT = Path(__file__).resolve().parent / "stage_data.yml"

# Outcome status names.
WRITTEN, EXISTS, SKIPPED, FAILED = "written", "exists", "skipped", "failed"

# (status, name, detail, size_bytes) per processed file/dataset.
_results: list[tuple[str, str, str, int]] = []
_run_started: float | None = None


def _print_entry(
    status: str,
    name: str,
    detail: str = "",
    *,
    size_bytes: int = 0,
) -> None:
    """Print a glyph-prefixed entry line and record it for the TOTAL recap."""
    glyph_color = {
        WRITTEN: ("+", green),
        EXISTS:  ("=", dim),
        SKIPPED: ("-", yellow),
        FAILED:  ("x", red),
    }[status]
    glyph, color = glyph_color
    print(f"    {color(glyph)} {name}")
    if detail:
        print(f"      {dim(detail)}")
    _results.append((status, name, detail, size_bytes))


def _remove(path: Path) -> None:
    if not path.exists():
        return
    if path.is_dir():
        shutil.rmtree(path, ignore_errors=True)
    else:
        try:
            path.unlink()
        except OSError:
            pass


def _path_size(path: Path) -> int:
    """Return file or directory size in bytes."""
    if not path.exists():
        return 0
    if path.is_file():
        return path.stat().st_size
    return sum(p.stat().st_size for p in path.rglob("*") if p.is_file())


@contextmanager
def _cleanup_on_error(dst: Path):
    """On failure, delete partial output so a re-run actually retries."""
    try:
        yield
    except Exception:
        _remove(dst)
        raise


def _zarr_complete(dst: Path) -> bool:
    if not dst.exists():
        return False
    return (dst / ".zmetadata").exists() or (dst / ".zgroup").exists()


# --- Per-output manifest -----------------------------------------------------
#
# Each staged output gets a sidecar JSON noting the parameters it was produced
# with (bbox, time_range, variables, source path).  Subsequent runs compare
# the current parameters to the stored manifest; if they differ, the cached
# output is treated as stale and re-staged.  This is what makes "skip if
# exists" actually safe across YAML edits.

MANIFEST_VERSION = 1
DEFAULT_RASTER_GLOB_WORKERS = 4
RASTER_TILE_SIZE = 256
RASTER_TILE_MIN_SIZE = 16


def _manifest_path(dst: Path) -> Path:
    # Zarr stores are directories; keep the manifest inside.  File outputs get
    # a sidecar next to them.
    if dst.suffix.lower() == ".zarr" or (dst.exists() and dst.is_dir()):
        return dst / ".stage.json"
    return dst.with_name(dst.name + ".stage.json")


def _read_manifest(dst: Path) -> dict | None:
    p = _manifest_path(dst)
    if not p.exists():
        return None
    try:
        return json.loads(p.read_text())
    except Exception:
        return None


def _write_manifest(dst: Path, fingerprint: dict) -> None:
    p = _manifest_path(dst)
    p.parent.mkdir(parents=True, exist_ok=True)
    payload = {"_manifest_version": MANIFEST_VERSION, **fingerprint}
    p.write_text(json.dumps(payload, indent=2, default=str))


def _is_fresh(dst: Path, fingerprint: dict, *, is_zarr: bool = False) -> bool:
    """Output exists, looks complete, and its manifest matches the fingerprint."""
    exists = _zarr_complete(dst) if is_zarr else dst.exists()
    if not exists:
        return False
    m = _read_manifest(dst)
    if m is None:
        return False
    return all(m.get(k) == v for k, v in fingerprint.items())


def _fingerprint(
    *,
    src: Path,
    bbox,
    time_range=None,
    variables=None,
    columns=None,
) -> dict:
    return {
        "src": str(src).replace("\\", "/"),
        "bbox": list(bbox),
        "time_range": list(time_range) if time_range else None,
        "variables": list(variables) if variables else None,
        "columns": list(columns) if columns else None,
    }


@contextmanager
def _dask_progress():
    """Context manager that shows a dask progress bar if dask is available."""
    if ProgressBar is None:
        yield
        return
    with ProgressBar():
        yield


def _format_elapsed(seconds: float) -> str:
    """Return a compact human-readable duration."""
    if seconds < 60:
        return f"{seconds:.1f}s"
    minutes, remaining = divmod(int(round(seconds)), 60)
    hours, minutes = divmod(minutes, 60)
    if hours:
        return f"{hours}h{minutes:02d}m{remaining:02d}s"
    return f"{minutes}m{remaining:02d}s"


def _format_bytes(size_bytes: int) -> str:
    """Return a compact human-readable byte size."""
    if size_bytes < 1_000:
        return f"{size_bytes} B"
    value = float(size_bytes)
    for unit in ("KB", "MB", "GB", "TB"):
        value /= 1_000
        if value < 1_000 or unit == "TB":
            return f"{value:.1f} {unit}"
    return f"{value:.1f} TB"


def _completion_detail(detail: str, finished_at: datetime, elapsed: float) -> str:
    """Append completion timestamp and elapsed time to a detail string."""
    suffix = (
        f"completed: {finished_at:%H:%M:%S}; "
        f"elapsed: {_format_elapsed(elapsed)}"
    )
    return f"{detail}; {suffix}" if detail else suffix


def _total_output_bytes(results) -> int:
    """Return bytes for outputs that were written or already fresh."""
    return sum(size for status, *_rest, size in results if status in (WRITTEN, EXISTS))


# --- Worker functions: each returns (status, detail). ---


def _validate_lonlat_crs(crs, kind: str, src: Path) -> None:
    """Raise if a lon/lat bbox is being applied to a projected dataset."""
    if crs is None:
        return
    if isinstance(crs, str):
        try:
            parsed_crs = rasterio.crs.CRS.from_user_input(crs)
        except Exception:
            parsed_crs = None
        if parsed_crs is not None:
            crs = parsed_crs
        elif crs.upper() in ("EPSG:4326", "OGC:CRS84", "WGS84", "WGS 84"):
            return
    is_geographic = getattr(crs, "is_geographic", None)
    if is_geographic:
        return
    crs_name = crs.to_string() if hasattr(crs, "to_string") else str(crs)
    raise ValueError(
        f"{kind} source {src} has CRS {crs_name}; bbox is lon/lat. "
        "Reproject the bbox or stage from a geographic source."
    )


def _raster_tile_size(size: int) -> int | None:
    """Return a GeoTIFF tile size for a clipped dimension."""
    if size < RASTER_TILE_MIN_SIZE:
        return None
    return min(
        RASTER_TILE_SIZE,
        (size // RASTER_TILE_MIN_SIZE) * RASTER_TILE_MIN_SIZE,
    )


def _raster_output_profile(profile: dict, *, height: int, width: int, transform) -> dict:
    """Return a clipped raster output profile with efficient GeoTIFF tiling."""
    out = profile.copy()
    out.pop("blockxsize", None)
    out.pop("blockysize", None)
    out.update(
        height=height,
        width=width,
        transform=transform,
        compress=out.get("compress") or "deflate",
    )
    if out.get("driver", "GTiff").lower() == "gtiff":
        blockxsize = _raster_tile_size(width)
        blockysize = _raster_tile_size(height)
        if blockxsize is not None and blockysize is not None:
            out.update(tiled=True, blockxsize=blockxsize, blockysize=blockysize)
        else:
            out.update(tiled=False)
    return out


# --- Filename-based tile pre-filter (raster_glob) ---
#
# Many global tiled rasters embed lat/lon corner info in the filename:
# MERIT/GMTED-style "n00e009_30sec.tif" or MODIS sinusoidal "h21v08.tif".
# When a known pattern matches we can skip files whose nominal bounds do
# not overlap the bbox, avoiding a slow SMB open per non-overlapping tile.
# Filenames that don't match any known pattern fall through to the slow
# (open-then-check) path safely.

_GEO_TILE_RE = re.compile(
    r"(?:^|[^a-zA-Z0-9])([ns])(\d{1,3})([ew])(\d{1,3})(?=[^a-zA-Z0-9]|$)",
    re.IGNORECASE,
)

_MODIS_RE = re.compile(
    r"(?:^|[^a-zA-Z0-9])h(\d{2})v(\d{2})(?=[^a-zA-Z0-9]|$)",
    re.IGNORECASE,
)


def _tile_bounds_from_name(name: str) -> tuple[float, float, float, float] | None:
    """Return (W, S, E, N) lon/lat bounds for a recognised tile filename.

    Returning None means "unknown pattern, fall back to opening the file".
    """
    m = _GEO_TILE_RE.search(name)
    if m:
        lat_hem, lat_deg, lon_hem, lon_deg = m.groups()
        lat_n_val, lon_n_val = int(lat_deg), int(lon_deg)
        if 0 <= lat_n_val <= 90 and 0 <= lon_n_val <= 180:
            lat = lat_n_val * (-1 if lat_hem.lower() == "s" else 1)
            lon = lon_n_val * (-1 if lon_hem.lower() == "w" else 1)
            # Tile labelled by SW corner; spans 1° unless we have other info.
            return float(lon), float(lat), float(lon + 1), float(lat + 1)

    m = _MODIS_RE.search(name)
    if m:
        v = int(m.group(2))
        if 0 <= v <= 17:
            lat_n = 90.0 - v * 10.0
            lat_s = lat_n - 10.0
            # Sinusoidal lon span varies with lat; use full lon for safety
            # (lat-only filter — still cuts most non-overlapping tiles).
            return -180.0, lat_s, 180.0, lat_n

    return None


def _bbox_overlap(a, b) -> bool:
    """True if two (W, S, E, N) bboxes overlap (touching edges = no overlap)."""
    aw, as_, ae, an = a
    bw, bs, be, bn = b
    return aw < be and ae > bw and as_ < bn and an > bs


def _vector_read_kwargs(bbox, columns=None) -> dict:
    """Return geopandas read_file kwargs for a clipped vector subset."""
    kwargs = {"bbox": bbox}
    if columns:
        kwargs["columns"] = list(columns)
    return kwargs


def _raster_glob_workers(entry: dict, *, file_count: int) -> int:
    """Return bounded worker count for independent raster-glob staging."""
    if file_count <= 5:
        return 1
    requested = entry.get("workers", DEFAULT_RASTER_GLOB_WORKERS)
    return max(1, min(int(requested), file_count))


def subset_raster(src: Path, dst: Path, bbox) -> tuple[str, str]:
    fp = _fingerprint(src=src, bbox=bbox)
    if _is_fresh(dst, fp):
        return EXISTS, f"{dst.stat().st_size / 1e6:.1f} MB"
    if dst.exists():
        _remove(dst)
        _remove(_manifest_path(dst))
    dst.parent.mkdir(parents=True, exist_ok=True)
    with _cleanup_on_error(dst):
        with rasterio.open(src) as ds:
            _validate_lonlat_crs(ds.crs, "raster", src)
            win = rasterio.windows.from_bounds(*bbox, transform=ds.transform)
            win = win.round_offsets().round_lengths()
            win = win.intersection(rasterio.windows.Window(0, 0, ds.width, ds.height))
            if win.width <= 0 or win.height <= 0:
                return SKIPPED, "no overlap"
            data = ds.read(window=win)
            profile = _raster_output_profile(
                ds.profile,
                height=int(win.height),
                width=int(win.width),
                transform=ds.window_transform(win),
            )
            with rasterio.open(dst, "w", **profile) as out:
                out.write(data)
    _write_manifest(dst, fp)
    return WRITTEN, f"{dst.stat().st_size / 1e6:.1f} MB"


def subset_vector(src: Path, dst: Path, bbox, *, columns=None) -> tuple[str, str]:
    fp = _fingerprint(src=src, bbox=bbox, columns=columns)
    if _is_fresh(dst, fp):
        return EXISTS, ""
    if dst.exists():
        _remove(dst)
        _remove(_manifest_path(dst))
    dst.parent.mkdir(parents=True, exist_ok=True)
    with _cleanup_on_error(dst):
        # Single open: bbox read first, validate CRS from the result. If the
        # CRS turns out projected, the bbox (lon/lat scale) will match no
        # features and the validation below raises before any write — so the
        # cost of the wasted query is bounded and no bad output is produced.
        gdf = gpd.read_file(src, **_vector_read_kwargs(bbox, columns))
        _validate_lonlat_crs(gdf.crs, "vector", src)
        if len(gdf) == 0:
            return SKIPPED, "no overlap"
        gdf.to_file(dst, driver="GPKG")
    _write_manifest(dst, fp)
    return WRITTEN, f"{len(gdf)} features"


def _spatial_dim(ds: xr.Dataset, candidates: tuple[str, ...]) -> str:
    for c in ds.coords:
        if c.lower() in candidates:
            return c
    raise KeyError(f"none of {candidates} found in coords {list(ds.coords)}")


def _spatial_slices(ds: xr.Dataset, bbox):
    lat = _spatial_dim(ds, ("lat", "latitude", "y"))
    lon = _spatial_dim(ds, ("lon", "longitude", "x"))
    w, s, e, n = bbox
    lat_desc = ds[lat].values[0] > ds[lat].values[-1]
    return lat, lon, (slice(n, s) if lat_desc else slice(s, n)), slice(w, e)


def _apply_time_range(ds: xr.Dataset, time_range) -> xr.Dataset:
    if not time_range:
        return ds
    tdim = next((d for d in ds.dims if d.lower() in ("time", "t")), None)
    if tdim is None:
        return ds
    start, end = time_range
    return ds.sel({tdim: slice(str(start), str(end))})


def _apply_variables(ds: xr.Dataset, variables) -> xr.Dataset:
    if not variables:
        return ds
    keep = [v for v in variables if v in ds.data_vars]
    return ds[keep] if keep else ds


ZARR_TIME_CHUNK = 365
# Only CF packing keys are carried from the source encoding; the source zarr
# codec objects are stripped separately (see `_strip_source_codecs`).
ZARR_ENCODING_KEYS = {
    "_FillValue",
    "add_offset",
    "dtype",
    "scale_factor",
}


def _zarr_subset_chunks(ds: xr.Dataset) -> dict[str, int]:
    """Return output chunk sizes suited to a clipped daily meteo subset."""
    chunks = {}
    for array in ds.data_vars.values():
        for dim in array.dims:
            dim_lower = dim.lower()
            if dim_lower in ("time", "t"):
                chunks[dim] = min(array.sizes[dim], ZARR_TIME_CHUNK)
            elif dim_lower in ("lat", "latitude", "y", "lon", "longitude", "x"):
                chunks[dim] = array.sizes[dim]
    return chunks


def _zarr_subset_encoding(ds: xr.Dataset, chunks: dict[str, int]) -> dict:
    """Build zarr encoding that preserves codecs but replaces source chunks."""
    encoding = {}
    for name, array in ds.data_vars.items():
        var_encoding = {
            key: value
            for key, value in array.encoding.items()
            if key in ZARR_ENCODING_KEYS
        }
        var_chunks = tuple(chunks[dim] for dim in array.dims if dim in chunks)
        if len(var_chunks) == len(array.dims) and var_chunks:
            var_encoding["chunks"] = var_chunks
        if var_encoding:
            encoding[name] = var_encoding
    return encoding


def _strip_source_codecs(ds: xr.Dataset) -> None:
    """Drop v2 numcodecs codec objects inherited from the source encoding.

    `xr.open_zarr` attaches the source `.encoding` (including a `numcodecs`
    `compressor`/`filters` for a zarr v2 store) to every variable *and*
    coordinate. On write, `to_zarr` reuses that per-variable encoding for any
    variable we do not override, so the v2 codec reaches the zarr 3.x writer and
    it raises "Expected a BytesBytesCodec. Got numcodecs.blosc.Blosc instead."
    Clearing these lets zarr 3 apply its own default compressor. Mutates in place.
    Both the v2 (`compressor`) and v3 (`compressors`, plural tuple) key spellings
    are dropped, along with `filters`, since either can carry legacy codecs.
    """
    for variable in ds.variables.values():
        for key in ("compressor", "compressors", "filters"):
            variable.encoding.pop(key, None)


def _zarr_subset_write_plan(ds: xr.Dataset) -> tuple[xr.Dataset, dict]:
    """Return a rechunked subset and matching zarr write encoding."""
    chunks = _zarr_subset_chunks(ds)
    rechunked = ds if not chunks else ds.chunk(chunks)
    _strip_source_codecs(rechunked)
    return rechunked, _zarr_subset_encoding(rechunked, chunks)


def subset_zarr(src: Path, dst: Path, bbox, *, time_range=None, variables=None) -> tuple[str, str]:
    fp = _fingerprint(src=src, bbox=bbox, time_range=time_range, variables=variables)
    if _is_fresh(dst, fp, is_zarr=True):
        return EXISTS, ""
    if dst.exists():
        _remove(dst)
    ds = xr.open_zarr(src, consolidated=True)
    ds = _apply_variables(ds, variables)
    lat, lon, lat_slice, lon_slice = _spatial_slices(ds, bbox)
    sub = ds.sel({lat: lat_slice, lon: lon_slice})
    sub = _apply_time_range(sub, time_range)
    sub, encoding = _zarr_subset_write_plan(sub)
    dst.parent.mkdir(parents=True, exist_ok=True)
    with _cleanup_on_error(dst), _dask_progress():
        sub.to_zarr(dst, mode="w", consolidated=True, encoding=encoding)
    _write_manifest(dst, fp)
    return WRITTEN, "x".join(f"{sub.sizes[d]}" for d in sub.sizes)


def subset_netcdf(
    src: Path,
    dst: Path,
    bbox,
    *,
    time_range=None,
    variables=None,
) -> tuple[str, str]:
    fp = _fingerprint(src=src, bbox=bbox, time_range=time_range, variables=variables)
    if _is_fresh(dst, fp):
        return EXISTS, ""
    if dst.exists():
        _remove(dst)
        _remove(_manifest_path(dst))
    ds = xr.open_dataset(src)
    ds = _apply_variables(ds, variables)
    lat, lon, lat_slice, lon_slice = _spatial_slices(ds, bbox)
    sub = ds.sel({lat: lat_slice, lon: lon_slice})
    sub = _apply_time_range(sub, time_range)
    dst.parent.mkdir(parents=True, exist_ok=True)
    with _cleanup_on_error(dst), _dask_progress():
        sub.to_netcdf(dst)
    _write_manifest(dst, fp)
    return WRITTEN, f"{dst.stat().st_size / 1e6:.1f} MB"


SUBSETTERS = {
    "raster": subset_raster,
    "vector": subset_vector,
    "zarr": subset_zarr,
    "netcdf": subset_netcdf,
}


def _worker_result(
    label: str,
    fn,
    src: Path,
    dst: Path,
    bbox,
    **kwargs,
) -> tuple[str, str, str, int]:
    """Run one staging worker and return a printable result tuple."""
    started = perf_counter()
    try:
        status, detail = fn(src, dst, bbox, **kwargs)
    except Exception as exc:
        status, detail = FAILED, str(exc).splitlines()[0][:80]
        sys.stderr.write(traceback.format_exc())
    detail = _completion_detail(detail, datetime.now(), perf_counter() - started)
    size_bytes = _path_size(dst) if status in (WRITTEN, EXISTS) else 0
    return status, label, detail, size_bytes


def _record_worker_result(
    status: str,
    label: str,
    detail: str,
    size_bytes: int,
    *,
    _verbose=True,
    _counts=None,
) -> None:
    """Record and optionally print one worker result."""
    if _counts is not None:
        _counts[status] = _counts.get(status, 0) + 1
    # In quiet mode (tqdm-driven loops) only break out of the bar for
    # failures and skipped entries — those are the lines a user needs to
    # see. Successful writes / existing files are summarised after the bar.
    if _verbose or status in (FAILED, SKIPPED):
        _print_entry(status, label, detail, size_bytes=size_bytes)
    else:
        # Still record for the TOTAL recap, just don't print per-line.
        _results.append((status, label, detail, size_bytes))


def _run_worker(
    label: str,
    fn,
    src: Path,
    dst: Path,
    bbox,
    *,
    _verbose=True,
    _counts=None,
    **kwargs,
) -> None:
    status, result_label, detail, size_bytes = _worker_result(
        label, fn, src, dst, bbox, **kwargs
    )
    _record_worker_result(
        status,
        result_label,
        detail,
        size_bytes,
        _verbose=_verbose,
        _counts=_counts,
    )


def _print_metadata(lines) -> None:
    """Print zero or more dim-styled metadata lines indented under a dataset header."""
    for line in lines:
        if line:
            print(f"      {dim(line)}")


def _fmt_bbox(w, s, e, n) -> str:
    return f"{w:.3f}..{e:.3f} lon, {s:.3f}..{n:.3f} lat"


def _describe_raster(src: Path) -> list[str]:
    try:
        with rasterio.open(src) as ds:
            res_x = abs(ds.transform.a)
            res_y = abs(ds.transform.e)
            crs = ds.crs.to_string() if ds.crs else "<none>"
            return [
                f"crs: {crs}   res: {res_x:.6g}° x {res_y:.6g}°   "
                f"size: {ds.width}x{ds.height}",
            ]
    except Exception as exc:
        return [f"(could not read raster metadata: {exc})"]


def _describe_vector(src: Path) -> list[str]:
    try:
        import pyogrio  # type: ignore[import-untyped]
        info = pyogrio.read_info(src)
        crs = info.get("crs") or "<none>"
        n = info.get("features")
        geom = info.get("geometry_type") or "?"
        bbox = info.get("total_bounds")
        bbox_str = _fmt_bbox(*bbox) if bbox is not None and len(bbox) == 4 else "?"
        return [
            f"crs: {crs}   geometry: {geom}   features: {n}",
            f"bounds: {bbox_str}",
        ]
    except Exception as exc:
        return [f"(could not read vector metadata: {exc})"]


def _describe_xarray(ds: xr.Dataset, *, time_range=None) -> list[str]:
    out = []
    try:
        lat_name = next((c for c in ds.coords if c.lower() in ("lat", "latitude", "y")), None)
        lon_name = next((c for c in ds.coords if c.lower() in ("lon", "longitude", "x")), None)
        time_name = next((c for c in ds.coords if c.lower() in ("time", "t")), None)

        spatial_bits = []
        if lat_name and lon_name:
            lat = ds[lat_name].values
            lon = ds[lon_name].values
            if lat.size > 1 and lon.size > 1:
                res_lat = abs(float(lat[1] - lat[0]))
                res_lon = abs(float(lon[1] - lon[0]))
                spatial_bits.append(
                    f"grid: {ds.sizes[lat_name]}x{ds.sizes[lon_name]} "
                    f"({lat_name}x{lon_name})   res: {res_lon:.4g}° x {res_lat:.4g}°"
                )
                spatial_bits.append(
                    f"extent: {float(min(lon)):.3f}..{float(max(lon)):.3f} lon, "
                    f"{float(min(lat)):.3f}..{float(max(lat)):.3f} lat"
                )
        out.extend(spatial_bits)

        if time_name and ds.sizes.get(time_name, 0) > 0:
            t = ds[time_name].values
            n = len(t)
            t0, t1 = str(t[0])[:10], str(t[-1])[:10]
            try:
                freq = xr.infer_freq(ds[time_name][:50]) or "?"
            except Exception:
                freq = "?"
            out.append(f"time: {t0} -> {t1}   ({n} steps, freq: {freq})")
            if time_range:
                out.append(f"time_range filter: {time_range[0]} -> {time_range[1]}")

        vars_ = list(ds.data_vars)
        sample = ", ".join(vars_[:8]) + (f", ... ({len(vars_)} total)" if len(vars_) > 8 else "")
        out.append(f"variables: {sample}")
    except Exception as exc:
        out.append(f"(could not read metadata: {exc})")
    return out


def _describe_zarr(src: Path, *, time_range=None) -> list[str]:
    try:
        ds = xr.open_zarr(src, consolidated=True)
        return _describe_xarray(ds, time_range=time_range)
    except Exception as exc:
        return [f"(could not open zarr: {exc})"]


def _describe_netcdf(src: Path, *, time_range=None) -> list[str]:
    try:
        ds = xr.open_dataset(src)
        return _describe_xarray(ds, time_range=time_range)
    except Exception as exc:
        return [f"(could not open netcdf: {exc})"]


def _stage_dataset(entry: dict, source_root: Path, target_root: Path, bbox) -> None:
    try:
        name = entry["name"]
        kind = entry["type"]
        rel = Path(entry["path"])
    except KeyError as exc:
        print(f"  {red('x')} <invalid entry>  missing key {exc}: {entry!r}")
        _results.append((FAILED, str(entry), f"missing key {exc}", 0))
        return

    src, dst = source_root / rel, target_root / rel
    dataset_started = perf_counter()
    print(f"  {cyan('▸')} {bold(name)}")

    if kind == "raster_glob":
        pattern = entry.get("pattern", "*.tif")
        if not src.exists():
            _print_entry(FAILED, name, f"source dir missing: {fmt_path(src)}")
            return
        all_files = sorted(src.glob(pattern))
        if not all_files:
            _print_entry(SKIPPED, name, f"no files match {pattern}")
            return

        # Filename-based pre-filter: drop tiles whose name-encoded bounds
        # cannot overlap the bbox without paying a per-file SMB open.
        # Filenames matching no known tile pattern fall through to the
        # slow path (open-then-check inside subset_raster).
        files = []
        prefiltered = 0
        for f in all_files:
            tb = _tile_bounds_from_name(f.name)
            if tb is not None and not _bbox_overlap(tb, bbox):
                prefiltered += 1
                continue
            files.append(f)
        if not files:
            _print_entry(
                SKIPPED, name, f"all {len(all_files)} tiles filtered out by bbox"
            )
            return

        suffix = f"   ({prefiltered} pre-filtered)" if prefiltered else ""
        _print_metadata([
            f"{len(all_files)} files matching {pattern}{suffix}   "
            f"sample: {files[0].name}"
        ])
        _print_metadata(_describe_raster(files[0]))
        # Emit per-file glyphs only on the slow path (verbose) or when there
        # are few files; otherwise let tqdm carry the progress signal and
        # only break out for failures/skips.
        workers = _raster_glob_workers(entry, file_count=len(files))
        verbose = workers == 1 and (tqdm is None or len(files) <= 5)
        progress_items = files if workers == 1 else range(len(files))
        bar = (
            tqdm(progress_items, desc=f"    {name}", unit="file", leave=False)
            if (tqdm and not verbose)
            else progress_items
        )
        counts = {WRITTEN: 0, EXISTS: 0, SKIPPED: 0, FAILED: 0}
        if workers == 1:
            for f in bar:
                _run_worker(
                    f.name, subset_raster, f, dst / f.name, bbox,
                    _verbose=verbose, _counts=counts,
                )
        else:
            with ThreadPoolExecutor(max_workers=workers) as executor:
                futures = [
                    executor.submit(
                        _worker_result,
                        f.name,
                        subset_raster,
                        f,
                        dst / f.name,
                        bbox,
                    )
                    for f in files
                ]
                for future, _ in zip(as_completed(futures), bar):
                    status, result_label, detail, size_bytes = future.result()
                    _record_worker_result(
                        status,
                        result_label,
                        detail,
                        size_bytes,
                        _verbose=False,
                        _counts=counts,
                    )
        if not verbose:
            summary = (
                f"{counts[WRITTEN]} written, {counts[EXISTS]} existing, "
                f"{counts[SKIPPED]} skipped, {counts[FAILED]} failed"
            )
            if workers > 1:
                summary = f"{summary}; workers: {workers}"
            summary = _completion_detail(
                summary,
                datetime.now(),
                perf_counter() - dataset_started,
            )
            print()
            print(f"    {green('+')} {pad(name, 44)}")
            print(f"      {dim(summary)}")
        return

    fn = SUBSETTERS.get(kind)
    if fn is None:
        _print_entry(FAILED, name, f"unknown type {kind!r}")
        return
    extra = {}
    if kind in ("zarr", "netcdf"):
        if "time_range" in entry:
            extra["time_range"] = entry["time_range"]
        if "variables" in entry:
            extra["variables"] = entry["variables"]
    elif kind == "vector" and "columns" in entry:
        extra["columns"] = entry["columns"]

    # Per-type metadata block under the header line.
    if kind == "raster":
        _print_metadata(_describe_raster(src))
    elif kind == "vector":
        _print_metadata(_describe_vector(src))
    elif kind == "zarr":
        _print_metadata(_describe_zarr(src, time_range=extra.get("time_range")))
    elif kind == "netcdf":
        _print_metadata(_describe_netcdf(src, time_range=extra.get("time_range")))

    _run_worker(rel.name, fn, src, dst, bbox, **extra)


def stage(cfg: dict) -> None:
    source_root = Path(cfg["source_root"])
    target_root = Path(cfg["target_root"])
    bbox = tuple(cfg["bbox"])
    datasets = cfg.get("datasets", [])
    if len(bbox) != 4:
        raise ValueError(f"bbox must have 4 values [W S E N], got {bbox}")

    print(banner("STAGE"))
    print(f"  {len(datasets)} dataset(s)")
    print()
    for entry in datasets:
        _stage_dataset(entry, source_root, target_root, bbox)
        print()


def load_config(path: Path) -> dict:
    if not path.exists():
        raise FileNotFoundError(f"config not found: {path}")
    with path.open() as f:
        cfg = yaml.safe_load(f) or {}
    for key in ("source_root", "target_root", "bbox", "datasets"):
        if key not in cfg:
            raise ValueError(f"config {path} missing required key '{key}'")
    return cfg


def _print_description() -> None:
    print(banner("DESCRIPTION"))
    print(
        "Stage a bbox-clipped subset of a remote data root onto local storage, "
        "mirroring the source tree so an existing data catalog can point to "
        "the local copy. Re-runs use per-output manifests to skip fresh "
        "outputs and restage stale ones."
    )
    print()


def _print_parameters(cfg: dict, config_path: Path) -> None:
    print(banner("PARAMETERS"))

    print(bold("inputs:"))
    rows = [
        ("config",      fmt_path(config_path)),
        ("source_root", fmt_path(cfg["source_root"])),
        ("target_root", fmt_path(cfg["target_root"])),
    ]
    for label, value in rows:
        print(f"  {pad(label, 12, dim)}  {value}")
    print()

    datasets = cfg.get("datasets", [])
    name_width = max((len(d.get("name", "?")) for d in datasets), default=0) + 2
    print(bold(f"datasets ({len(datasets)}):"))
    for d in datasets:
        name = d.get("name", "?")
        kind = d.get("type", "?")
        print(f"  {pad(name, name_width, cyan)}  {dim(kind)}")
    print()

    print(bold("flags:"))
    w, s, e, n = cfg["bbox"]
    print(
        f"  {pad('bbox', 12, dim)} "
        f"{pad(f'{w} {s} {e} {n}', 22, cyan)} "
        f"{dim('west south east north (lon/lat)')}"
    )
    print()


def _print_total() -> None:
    counts = {WRITTEN: 0, EXISTS: 0, SKIPPED: 0, FAILED: 0}
    for status, *_rest in _results:
        counts[status] = counts.get(status, 0) + 1

    print(banner("TOTAL"))
    pill = (
        f"{green(f'written: {counts[WRITTEN]}')}"
        f" {dim('·')} "
        f"{dim(f'existing: {counts[EXISTS]}')}"
        f" {dim('·')} "
        f"{yellow(f'skipped: {counts[SKIPPED]}')}"
        f" {dim('·')} "
        f"{red(f'failed: {counts[FAILED]}')}"
    )
    print(pill)
    elapsed = (
        _format_elapsed(perf_counter() - _run_started)
        if _run_started is not None
        else "?"
    )
    print(
        f"{dim('elapsed:')} {elapsed}"
        f" {dim('·')} "
        f"{dim('size:')} {_format_bytes(_total_output_bytes(_results))}"
    )

    total_ok = counts[WRITTEN] + counts[EXISTS]
    if counts[FAILED] == 0 and total_ok > 0:
        print()
        print(green(bold(f"OK — all {total_ok} dataset(s) staged successfully.")))
    elif counts[FAILED] == 0 and total_ok == 0:
        print()
        print(yellow(bold("nothing to do — no datasets matched.")))
    else:
        print()
        print(red(bold(f"FAILED — {counts[FAILED]} dataset(s) did not stage; see recap below.")))

    failures = [(n, d) for s, n, d, _size in _results if s == FAILED]
    if failures:
        print()
        print(f"{bold('failed')} ({len(failures)}):")
        for name, detail in failures:
            print(f"  {red('x')} {name}  {dim(detail)}")

    skips = [(n, d) for s, n, d, _size in _results if s == SKIPPED]
    if skips:
        print()
        print(f"{bold('skipped')} ({len(skips)}):")
        for name, detail in skips:
            print(f"  {yellow('-')} {name}  {dim(detail)}")


def main() -> None:
    global _run_started

    _run_started = perf_counter()
    p = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    p.add_argument("--config", type=Path, default=CONFIG_DEFAULT,
                   help=f"YAML config (default: {CONFIG_DEFAULT})")
    p.add_argument("--src", type=Path, help="override source_root from the config")
    p.add_argument("--dst", type=Path, help="override target_root from the config")
    p.add_argument("--bbox", nargs=4, type=float, metavar=("W", "S", "E", "N"),
                   help="override bbox from the config")
    args = p.parse_args()

    cfg = load_config(args.config)
    if args.src is not None:
        cfg["source_root"] = str(args.src)
    if args.dst is not None:
        cfg["target_root"] = str(args.dst)
    if args.bbox is not None:
        cfg["bbox"] = list(args.bbox)

    _print_description()
    _print_parameters(cfg, args.config)
    stage(cfg)
    _print_total()

    if any(s == FAILED for s, *_ in _results):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
