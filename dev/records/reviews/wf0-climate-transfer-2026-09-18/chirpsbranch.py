import copy
import time
import warnings

import dask
import hydromt
import psutil

warnings.filterwarnings("ignore")


proc = psutil.Process()
BBOX = [9.30, 0.30, 9.65, 0.65]
# what the chirps branch asks era5 for: six variables, no precip
VARS = ["temp", "temp_min", "temp_max", "kin", "kout", "press_msl"]
BASE = hydromt.DataCatalog(
    data_libs=["config/catalogs/deltares_data_pdrive.yml"]
).to_dict()


def cat(spec):
    d = copy.deepcopy(BASE)
    if spec is not None:
        src = d["era5"]
        drv = src.setdefault("driver", {})
        if isinstance(drv, str):
            drv = {"name": drv}
            src["driver"] = drv
        drv.setdefault("options", {})["chunks"] = spec
    return hydromt.DataCatalog().from_dict(d)


def run(label, spec, year):
    b0 = proc.io_counters().read_bytes
    t0 = time.time()
    with dask.config.set(scheduler="synchronous"):
        cat(spec).get_rasterdataset(
            "era5",
            bbox=BBOX,
            time_range=(f"{year}-01-02", f"{year}-12-31"),
            buffer=2,
            variables=VARS,
        ).compute()
    dt = time.time() - t0
    db = proc.io_counters().read_bytes - b0
    print(f"{label:28s} read={db / 1e9:5.2f} GB  {dt:6.1f} s", flush=True)


run("catalog as-is (lon 240)", None, 2002)
run("encoded {} (lon 480)", {}, 2003)
