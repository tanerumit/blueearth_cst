import copy
import os
import sys
import time
import warnings

import dask
import hydromt
import psutil

warnings.filterwarnings("ignore")


mode = sys.argv[1]
proc = psutil.Process()
BBOX = [9.30, 0.30, 9.65, 0.65]
VARS = ["precip", "temp", "temp_min", "temp_max", "kin", "kout", "press_msl"]
BASE = hydromt.DataCatalog(
    data_libs=["config/catalogs/deltares_data_pdrive.yml"]
).to_dict()


def cat(backend):
    d = copy.deepcopy(BASE)
    src = d["era5"]
    drv = src.setdefault("driver", {})
    if isinstance(drv, str):
        drv = {"name": drv}
        src["driver"] = drv
    drv["options"] = {"chunks": {}}
    if backend == "zarr":
        src["uri"] = "meteo/era5_daily.zarr"
    return hydromt.DataCatalog().from_dict(d)


backend, sched, nw = {
    "nc_sync": ("nc", "synchronous", None),
    "zarr_thr": ("zarr", "threads", 32),
}[mode]

out = rf".tmp\scratchpad\2026-09-18_1316\out_{mode}.nc"
b0 = proc.io_counters().read_bytes
t0 = time.time()
cfg = {"scheduler": sched}
if nw:
    cfg["num_workers"] = nw
with dask.config.set(**cfg):
    ds = cat(backend).get_rasterdataset(
        "era5",
        bbox=BBOX,
        time_range=("2000-01-02", "2016-12-31"),
        buffer=2,
        variables=VARS,
    )
    ds = ds.compute()
t_read = time.time() - t0
b_read = proc.io_counters().read_bytes - b0
ds.to_netcdf(out, encoding={v: {"zlib": True} for v in ds.data_vars}, mode="w")
t_all = time.time() - t0

print(
    f"{mode:10s} read={b_read / 1e9:5.2f} GB  read_t={t_read / 60:5.2f} min  "
    f"total={t_all / 60:5.2f} min  {b_read / 1e6 / t_read:5.1f} MB/s  "
    f"out={os.path.getsize(out) / 1024:.0f} KB  "
    f"grid={ds.sizes['latitude']}x{ds.sizes['longitude']}x{ds.sizes['time']}"
)
