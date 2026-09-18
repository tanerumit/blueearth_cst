import copy
import os
import time
import warnings

import dask
import hydromt
import psutil

warnings.filterwarnings("ignore")


print("cpu_count=", os.cpu_count())
proc = psutil.Process()
BBOX = [9.30, 0.30, 9.65, 0.65]
VARS = ["precip", "temp", "temp_min", "temp_max", "kin", "kout", "press_msl"]
BASE = hydromt.DataCatalog(
    data_libs=["config/catalogs/deltares_data_pdrive.yml"]
).to_dict()


def zarr_cat():
    d = copy.deepcopy(BASE)
    src = d["era5"]
    src["uri"] = "meteo/era5_daily.zarr"
    drv = src.setdefault("driver", {})
    if isinstance(drv, str):
        drv = {"name": drv}
        src["driver"] = drv
    drv["options"] = {"chunks": {}}
    return hydromt.DataCatalog().from_dict(d)


def run(nw, year):
    dc = zarr_cat()
    b0 = proc.io_counters().read_bytes
    t0 = time.time()
    with dask.config.set(scheduler="threads", num_workers=nw):
        dc.get_rasterdataset(
            "era5",
            bbox=BBOX,
            time_range=(f"{year}-01-02", f"{year}-12-31"),
            buffer=2,
            variables=VARS,
        ).compute()
    dt = time.time() - t0
    db = proc.io_counters().read_bytes - b0
    print(
        f"  workers={nw:3d}  {dt:6.1f} s  {db / 1e6 / dt:6.1f} MB/s  "
        f"read={db / 1e9:.2f} GB",
        flush=True,
    )
    return dt


for nw, yr in [(4, 2012), (8, 2013), (16, 2014), (32, 2015), (64, 2016)]:
    run(nw, yr)
