import copy
import time
import warnings

import dask
import hydromt
import psutil

warnings.filterwarnings("ignore")


proc = psutil.Process()
BBOX = [9.30, 0.30, 9.65, 0.65]
CAT = "config/catalogs/deltares_data_pdrive.yml"
VARS = ["precip", "temp", "temp_min", "temp_max", "kin", "kout", "press_msl"]
BASE = hydromt.DataCatalog(data_libs=[CAT]).to_dict()


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
        drv["options"] = {"chunks": {}}
    return hydromt.DataCatalog().from_dict(d)


def run(label, backend, sched, year):
    dc = cat(backend)
    tr = (f"{year}-01-02", f"{year}-12-31")
    b0 = proc.io_counters().read_bytes
    t0 = time.time()
    with dask.config.set(scheduler=sched):
        ds = dc.get_rasterdataset(
            "era5", bbox=BBOX, time_range=tr, buffer=2, variables=VARS
        )
        ds = ds.compute()
    dt = time.time() - t0
    db = proc.io_counters().read_bytes - b0
    mb = sum(v.nbytes for v in ds.data_vars.values()) / 1e6
    print(
        f"{label:22s} read={db / 1e9:6.2f} GB  {dt:6.1f} s  "
        f"{db / 1e6 / dt:6.1f} MB/s  in-mem={mb:.1f} MB",
        flush=True,
    )
    return db, dt


r = {}
r["nc/sync"] = run("netcdf + synchronous", "nc", "synchronous", 2008)
r["nc/thr"] = run("netcdf + threads", "nc", "threads", 2009)
r["zarr/sync"] = run("zarr   + synchronous", "zarr", "synchronous", 2010)
r["zarr/thr"] = run("zarr   + threads", "zarr", "threads", 2011)

print("\n-- vs netcdf/synchronous, one year --")
for k, (b, t) in r.items():
    print(
        f"{k:10s} bytes {r['nc/sync'][0] / b:5.2f}x   time {r['nc/sync'][1] / t:5.2f}x"
    )
