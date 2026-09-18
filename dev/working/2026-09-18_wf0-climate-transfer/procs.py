"""Can netCDF reads parallelise across PROCESSES, sidestepping the per-process
HDF5 lock? If so the speedup needs no zarr repoint and no coverage loss."""

import os
import sys
import time
import warnings

import psutil

warnings.filterwarnings("ignore")


sys.path.insert(0, os.getcwd())

BBOX = [9.30, 0.30, 9.65, 0.65]
VARS = ["precip", "temp", "temp_min", "temp_max", "kin", "kout", "press_msl"]
CAT = "config/catalogs/deltares_data_pdrive.yml"


def read_year(year):
    import warnings as w

    w.filterwarnings("ignore")

    import hydromt

    d = hydromt.DataCatalog(data_libs=[CAT]).to_dict()
    src = d["era5"]
    drv = src.setdefault("driver", {})
    if isinstance(drv, str):
        drv = {"name": drv}
        src["driver"] = drv
    drv.setdefault("options", {})["chunks"] = {}
    ds = (
        hydromt.DataCatalog()
        .from_dict(d)
        .get_rasterdataset(
            "era5",
            bbox=BBOX,
            time_range=(f"{year}-01-02", f"{year}-12-31"),
            buffer=2,
            variables=VARS,
        )
    )
    return ds.compute()


if __name__ == "__main__":
    from concurrent.futures import ProcessPoolExecutor

    years = list(range(2000, 2017))  # the real 17-year window
    for nproc in (6,):
        p = psutil.Process()
        t0 = time.time()
        with ProcessPoolExecutor(max_workers=nproc) as ex:
            list(ex.map(read_year, years))
        dt = time.time() - t0
        print(f"netcdf + {nproc} processes, 17 years: {dt / 60:.2f} min", flush=True)
