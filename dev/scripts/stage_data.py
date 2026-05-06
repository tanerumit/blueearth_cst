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
      - {name: tiles, type: raster_glob, path: topography/.../30sec, pattern: "*.tif"}
      - {name: idx,   type: vector,      path: topography/.../basin_index.gpkg}
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
import shutil
import sys
import traceback
from contextlib import contextmanager
from pathlib import Path

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

# (status, name, detail) per processed file/dataset.
_results: list[tuple[str, str, str]] = []


def _print_entry(status: str, name: str, detail: str = "") -> None:
    """Print a glyph-prefixed entry line and record it for the TOTAL recap."""
    glyph_color = {
        WRITTEN: ("+", green),
        EXISTS:  ("=", dim),
        SKIPPED: ("-", yellow),
        FAILED:  ("x", red),
    }[status]
    glyph, color = glyph_color
    line = f"    {color(glyph)} {pad(name, 44)}  {dim(detail)}" if detail else f"    {color(glyph)} {name}"
    print(line)
    _results.append((status, name, detail))


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


def _fingerprint(*, src: Path, bbox, time_range=None, variables=None) -> dict:
    return {
        "src": str(src).replace("\\", "/"),
        "bbox": list(bbox),
        "time_range": list(time_range) if time_range else None,
        "variables": list(variables) if variables else None,
    }


@contextmanager
def _dask_progress():
    """Context manager that shows a dask progress bar if dask is available."""
    if ProgressBar is None:
        yield
        return
    with ProgressBar():
        yield


# --- Worker functions: each returns (status, detail). ---


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
            win = rasterio.windows.from_bounds(*bbox, transform=ds.transform)
            win = win.round_offsets().round_lengths()
            win = win.intersection(rasterio.windows.Window(0, 0, ds.width, ds.height))
            if win.width <= 0 or win.height <= 0:
                return SKIPPED, "no overlap"
            data = ds.read(window=win)
            profile = ds.profile.copy()
            profile.pop("blockxsize", None)
            profile.pop("blockysize", None)
            profile.update(
                height=int(win.height),
                width=int(win.width),
                transform=ds.window_transform(win),
                compress=profile.get("compress") or "deflate",
                tiled=False,
            )
            with rasterio.open(dst, "w", **profile) as out:
                out.write(data)
    _write_manifest(dst, fp)
    return WRITTEN, f"{dst.stat().st_size / 1e6:.1f} MB"


def subset_vector(src: Path, dst: Path, bbox) -> tuple[str, str]:
    fp = _fingerprint(src=src, bbox=bbox)
    if _is_fresh(dst, fp):
        return EXISTS, ""
    if dst.exists():
        _remove(dst)
        _remove(_manifest_path(dst))
    dst.parent.mkdir(parents=True, exist_ok=True)
    with _cleanup_on_error(dst):
        gdf = gpd.read_file(src, bbox=bbox)
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
    # Preserve the source's encoding (codec, chunking, fill_value) so writes
    # round-trip cleanly.  Earlier workarounds that cleared encoding + forced
    # uniform chunks were needed for zarr 3 only and corrupted variables whose
    # source chunking/dtype differed from the homogenised target.
    dst.parent.mkdir(parents=True, exist_ok=True)
    with _cleanup_on_error(dst), _dask_progress():
        # `safe_chunks=False`: the source's encoding["chunks"] (sized for the
        # global grid) does not align with our spatially-clipped dask chunks.
        # That alignment only matters for parallel multi-writer writes; our
        # write is a single dask compute so the check is a false positive.
        sub.to_zarr(dst, mode="w", consolidated=True, safe_chunks=False)
    _write_manifest(dst, fp)
    return WRITTEN, "x".join(f"{sub.sizes[d]}" for d in sub.sizes)


def subset_netcdf(src: Path, dst: Path, bbox, *, time_range=None, variables=None) -> tuple[str, str]:
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


def _run_worker(label: str, fn, src: Path, dst: Path, bbox, *, _verbose=True, _counts=None, **kwargs) -> None:
    try:
        status, detail = fn(src, dst, bbox, **kwargs)
    except Exception as exc:
        status, detail = FAILED, str(exc).splitlines()[0][:80]
        sys.stderr.write(traceback.format_exc())
    if _counts is not None:
        _counts[status] = _counts.get(status, 0) + 1
    # In quiet mode (tqdm-driven loops) only break out of the bar for
    # failures and skipped entries — those are the lines a user needs to
    # see. Successful writes / existing files are summarised after the bar.
    if _verbose or status in (FAILED, SKIPPED):
        _print_entry(status, label, detail)
    else:
        # Still record for the TOTAL recap, just don't print per-line.
        _results.append((status, label, detail))


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
            nodata = ds.nodata
            return [
                f"crs: {crs}   res: {res_x:.6g}° x {res_y:.6g}°   "
                f"size: {ds.width}x{ds.height}   bands: {ds.count}",
                f"dtype: {ds.dtypes[0]}   nodata: {nodata}   "
                f"bounds: {_fmt_bbox(*ds.bounds)}",
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
        _results.append((FAILED, str(entry), f"missing key {exc}"))
        return

    src, dst = source_root / rel, target_root / rel
    print(f"  {cyan('▸')} {bold(name)}  {dim(kind)}  {dim(fmt_path(src))}")

    if kind == "raster_glob":
        pattern = entry.get("pattern", "*.tif")
        if not src.exists():
            _print_entry(FAILED, name, f"source dir missing: {fmt_path(src)}")
            return
        files = sorted(src.glob(pattern))
        if not files:
            _print_entry(SKIPPED, name, f"no files match {pattern}")
            return
        _print_metadata([f"{len(files)} files matching {pattern}   sample: {files[0].name}"])
        _print_metadata(_describe_raster(files[0]))
        # Emit per-file glyphs only on the slow path (verbose) or when there
        # are few files; otherwise let tqdm carry the progress signal and
        # only break out for failures/skips.
        verbose = tqdm is None or len(files) <= 5
        bar = tqdm(files, desc=f"    {name}", unit="file", leave=False) if (tqdm and not verbose) else files
        counts = {WRITTEN: 0, EXISTS: 0, SKIPPED: 0, FAILED: 0}
        for f in bar:
            _run_worker(
                f.name, subset_raster, f, dst / f.name, bbox,
                _verbose=verbose, _counts=counts,
            )
        if not verbose:
            summary = (
                f"{counts[WRITTEN]} written, {counts[EXISTS]} existing, "
                f"{counts[SKIPPED]} skipped, {counts[FAILED]} failed"
            )
            print(f"    {green('+')} {pad(name, 44)}  {dim(summary)}")
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
    print("Stage a bbox-clipped subset of a remote data root onto local storage.")
    print()


def _print_parameters(cfg: dict, config_path: Path) -> None:
    print(banner("PARAMETERS"))
    print(bold("inputs:"))
    rows = [
        ("config",   fmt_path(config_path)),
        ("source_root", fmt_path(cfg["source_root"])),
        ("target_root", fmt_path(cfg["target_root"])),
        ("datasets", f"{len(cfg.get('datasets', []))} entries"),
    ]
    for label, value in rows:
        print(f"  {pad(label, 10, dim)}  {value}")
    print()
    print(bold("flags:"))
    w, s, e, n = cfg["bbox"]
    print(
        f"  {pad('bbox', 10, dim)} "
        f"{pad(f'{w} {s} {e} {n}', 22, cyan)} "
        f"{dim('west south east north (lon/lat)')}"
    )
    print()


def _print_total() -> None:
    counts = {WRITTEN: 0, EXISTS: 0, SKIPPED: 0, FAILED: 0}
    for status, _name, _detail in _results:
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

    failures = [(n, d) for s, n, d in _results if s == FAILED]
    if failures:
        print()
        print(f"{bold('failed')} ({len(failures)}):")
        for name, detail in failures:
            print(f"  {red('x')} {name}  {dim(detail)}")

    skips = [(n, d) for s, n, d in _results if s == SKIPPED]
    if skips:
        print()
        print(f"{bold('skipped')} ({len(skips)}):")
        for name, detail in skips:
            print(f"  {yellow('-')} {name}  {dim(detail)}")


def main() -> None:
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
