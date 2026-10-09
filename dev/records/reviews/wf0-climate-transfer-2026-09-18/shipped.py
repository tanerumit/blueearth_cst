"""Measure the SHIPPED path: to_netcdf(compute=False) streamed synchronously."""

import json
import os
import sys
import time
import warnings

import psutil

warnings.filterwarnings("ignore")

# BEFORE the package import, and load-bearing: the primary worktree ships an
# editable install of `blueearth_cst`, so a bare run from a session worktree
# imports MAIN's copy and silently measures the wrong code.
sys.path.insert(0, os.getcwd())

from blueearth_cst.climate_analysis import (  # noqa: E402
    extract_historical_climate as ehc,
)

assert os.path.realpath(ehc.__file__).startswith(os.path.realpath(os.getcwd())), (
    f"imported {ehc.__file__}, not the worktree at {os.getcwd()}"
)
print("module:", ehc.__file__, flush=True)

proc = psutil.Process()
out = r".tmp\scratchpad\2026-09-18_1316\out_shipped.nc"
region = r"C:\Users\taner\workspace\cst-test-cases\runs\gabon-ntoum-deltares\data\spatial\geoms\region.geojson"

b0 = proc.io_counters().read_bytes
t0 = time.time()
ehc.prep_historical_climate(
    region_fn=region,
    fn_out=out,
    data_libs="config/catalogs/deltares_data_pdrive.yml",
    clim_source="era5",
    starttime="2000-01-01T00:00:00",
    endtime="2016-12-31T00:00:00",
)
dt = time.time() - t0
db = proc.io_counters().read_bytes - b0
print(
    json.dumps(
        {
            "read_GB": round(db / 1e9, 2),
            "minutes": round(dt / 60, 2),
            "MBps": round(db / 1e6 / dt, 1),
            "out_KB": round(os.path.getsize(out) / 1024),
        }
    )
)
