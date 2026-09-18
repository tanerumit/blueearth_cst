"""Can netCDF reads parallelise across PROCESSES, sidestepping the per-process
HDF5 lock? If so the speedup needs no zarr repoint and no coverage loss.

    python dev/working/2026-09-18_wf0-climate-transfer/procs.py <nproc> <y0> <y1>

Compare the aggregate rate against a SINGLE-process read of the same window --
`mem.py read <y0> <y1>`, which measured 3.34 GB in 3.02 min (18.4 MB/s) over
2000..2005 on 2026-09-18. Threads are known not to help here (32.0 s against
29.1 s for one year): HDF5's lock serializes reads whatever the scheduler.
Processes have no such lock to share, so this is the experiment that separates
"the lock is the limit" from "the LINK is the limit".

Each worker reports its own bytes, because `psutil` io counters are per-process
and a parent sees nothing its children read.
"""

import os
import sys
import time
import warnings

warnings.filterwarnings("ignore")


sys.path.insert(0, os.getcwd())

BBOX = [9.30, 0.30, 9.65, 0.65]
VARS = ["precip", "temp", "temp_min", "temp_max", "kin", "kout", "press_msl"]
CAT = "config/catalogs/deltares_data_pdrive.yml"


def read_year(year):
    import warnings as w

    w.filterwarnings("ignore")

    import hydromt
    import netCDF4
    import psutil

    # Match what the shipped extraction now does, so the rate measured here is
    # the rate that path would see.
    size, nelems, preemption = netCDF4.get_chunk_cache()
    netCDF4.set_chunk_cache(min(size, 1 << 20), nelems, preemption)

    proc = psutil.Process()
    b0 = proc.io_counters().read_bytes
    t0 = time.time()

    d = hydromt.DataCatalog(data_libs=[CAT]).to_dict()
    src = d["era5"]
    drv = src.setdefault("driver", {})
    if isinstance(drv, str):
        drv = {"name": drv}
        src["driver"] = drv
    drv.setdefault("options", {})["chunks"] = {}
    (
        hydromt.DataCatalog()
        .from_dict(d)
        .get_rasterdataset(
            "era5",
            bbox=BBOX,
            time_range=(f"{year}-01-02", f"{year}-12-31"),
            buffer=2,
            variables=VARS,
        )
        .compute()
    )
    return proc.io_counters().read_bytes - b0, time.time() - t0


if __name__ == "__main__":
    from concurrent.futures import ProcessPoolExecutor

    nproc, y0, y1 = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3])
    years = list(range(y0, y1 + 1))
    t0 = time.time()
    with ProcessPoolExecutor(max_workers=nproc) as ex:
        results = list(ex.map(read_year, years))
    dt = time.time() - t0
    read = sum(b for b, _ in results)
    print(
        f"netcdf + {nproc} processes, {y0}..{y1} ({len(years)} yr): "
        f"read={read / 1e9:5.2f} GB  {dt / 60:5.2f} min  {read / 1e6 / dt:5.1f} MB/s",
        flush=True,
    )
