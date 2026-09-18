"""Peak RSS of the SHIPPED streaming write against an eager read, same window.

Lever (A) of `t2609181501`. Both modes run the SHIPPED
``prep_historical_climate`` so the graph, the catalog override, the dtype cast
and the metadata stamp are identical; `eager` differs only in that
``Dataset.to_netcdf(compute=False)`` is intercepted and the dataset is
materialized before the write, which is exactly the proposed change. Nothing in
`blueearth_cst/` is edited for the probe.

    python dev/working/2026-09-18_wf0-climate-transfer/mem.py <mode> <y0> <y1>

`mode` is `shipped`, `eager`, or `read` (the read alone, no write at all --
the control that says whether the write is involved). Set `FILE_CACHE` to an
integer to shrink xarray's open-file cache from its default 128, which is the
hypothesis that the growth is HDF5 per-file state held open by
`CachingFileManager` rather than anything dask retains.

Prints one JSON line per sample to `<scratch>/mem_<mode>_<y0>_<y1>.jsonl` and a
summary to stdout.
"""

import json
import os
import sys
import threading
import time
import warnings

import psutil

warnings.filterwarnings("ignore")

# BEFORE the package import, and load-bearing: the primary worktree ships an
# editable install of `blueearth_cst`, so a bare run from a session worktree
# imports MAIN's copy and silently measures the wrong code.
sys.path.insert(0, os.getcwd())

import xarray as xr  # noqa: E402

from blueearth_cst.climate_analysis import (  # noqa: E402
    extract_historical_climate as ehc,
)

assert os.path.realpath(ehc.__file__).startswith(os.path.realpath(os.getcwd())), (
    f"imported {ehc.__file__}, not the worktree at {os.getcwd()}"
)

BBOX = [9.30, 0.30, 9.65, 0.65]  # Ntoum, as in every other script here
SCRATCH = r".tmp\scratchpad\2026-09-18_1632"

MODE, Y0, Y1 = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])

_real_to_netcdf = xr.Dataset.to_netcdf


class _Done:
    """Stand-in for the Delayed the shipped path computes."""

    def compute(self):
        return None


def _eager_to_netcdf(self, *args, **kwargs):
    """Materialize first, then write in one go -- the proposed alternative."""
    if kwargs.pop("compute", True) is False:
        _real_to_netcdf(self.compute(), *args, **kwargs)
        return _Done()
    return _real_to_netcdf(self, *args, **kwargs)


def _no_write(self, *args, **kwargs):
    if kwargs.pop("compute", True) is False:
        self.compute()
        return _Done()
    self.compute()


if MODE == "eager":
    xr.Dataset.to_netcdf = _eager_to_netcdf
elif MODE == "read":
    xr.Dataset.to_netcdf = _no_write
elif MODE != "shipped":
    raise SystemExit(f"unknown mode {MODE!r}")

FILE_CACHE = os.environ.get("FILE_CACHE")
if FILE_CACHE:
    xr.set_options(file_cache_maxsize=int(FILE_CACHE))

# HDF5 keeps a per-VARIABLE chunk cache inside every open netCDF file, and
# `nc_set_chunk_cache` sets the default every file opened afterwards inherits.
# Set `CHUNK_CACHE` to a byte count to shrink it.
CHUNK_CACHE = os.environ.get("CHUNK_CACHE")
if CHUNK_CACHE:
    import netCDF4

    _, nelems, preemption = netCDF4.get_chunk_cache()
    netCDF4.set_chunk_cache(int(CHUNK_CACHE), nelems, preemption)

# Repoint era5 at the zarr store, changing NOTHING else -- the 2026-09-18 zarr
# figure was measured with 32 threads, and this is the control that says
# whether the win was the store or the threading. Hooked on
# `_align_chunks_to_store` because it is called once, before any read, and
# already takes and returns the catalog.
if os.environ.get("ZARR"):
    _real_align = ehc._align_chunks_to_store

    def _align_zarr(data_catalog, sources):
        as_dict = data_catalog.to_dict()
        src = as_dict["era5"]
        src["uri"] = "meteo/era5_daily.zarr"
        # `combine` and `parallel` are netCDF driver options `open_zarr`
        # rejects outright, so the option block is replaced rather than
        # extended. `_align_chunks_to_store` then puts `chunks: {}` back.
        drv = src.setdefault("driver", {})
        if isinstance(drv, str):
            drv = {"name": drv}
            src["driver"] = drv
        drv["options"] = {}
        return _real_align(ehc.hydromt.DataCatalog().from_dict(as_dict), sources)

    ehc._align_chunks_to_store = _align_zarr

proc = psutil.Process()
samples = []
stop = threading.Event()


def sample():
    b0 = proc.io_counters().read_bytes
    t0 = time.time()
    while not stop.wait(2.0):
        samples.append(
            {
                "s": round(time.time() - t0, 1),
                "read_GB": round((proc.io_counters().read_bytes - b0) / 1e9, 3),
                "rss_MB": round(proc.memory_info().rss / 1e6),
            }
        )


sampler = threading.Thread(target=sample, daemon=True)
STORE = "zarr" if os.environ.get("ZARR") else "netcdf"
out = os.path.join(SCRATCH, f"out_mem_{MODE}_{STORE}_{Y0}_{Y1}.nc")
log = os.path.join(SCRATCH, f"mem_{MODE}_{STORE}_{Y0}_{Y1}.jsonl")
os.makedirs(SCRATCH, exist_ok=True)

rss_start = proc.memory_info().rss
b_start = proc.io_counters().read_bytes
t_start = time.time()
sampler.start()
try:
    ehc.prep_historical_climate(
        region_fn=None,
        bbox=BBOX,
        fn_out=out,
        data_libs="config/catalogs/deltares_data_pdrive.yml",
        clim_source="era5",
        starttime=f"{Y0}-01-02T00:00:00",
        endtime=f"{Y1}-12-31T00:00:00",
        enforce_min_years=False,
    )
finally:
    stop.set()
    sampler.join()

dt = time.time() - t_start
db = proc.io_counters().read_bytes - b_start
peak = max([s["rss_MB"] for s in samples], default=round(rss_start / 1e6))
# After the write: what does NOT come back is a retention rather than a
# high-water mark, and the two call for different fixes.
settled = round(proc.memory_info().rss / 1e6)

with open(log, "w", encoding="utf-8") as fh:
    for s in samples:
        fh.write(json.dumps(s) + "\n")

summary = {
    "mode": MODE,
    "years": f"{Y0}-{Y1}",
    "read_GB": round(db / 1e9, 2),
    "minutes": round(dt / 60, 2),
    "MBps": round(db / 1e6 / dt, 1),
    "rss_start_MB": round(rss_start / 1e6),
    "rss_peak_MB": peak,
    "rss_settled_MB": settled,
    "out_KB": round(os.path.getsize(out) / 1024) if os.path.exists(out) else None,
    "file_cache": FILE_CACHE or "default",
    "chunk_cache": CHUNK_CACHE or "default",
    "store": STORE,
}
print(json.dumps(summary), flush=True)
