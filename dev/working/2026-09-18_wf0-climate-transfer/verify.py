import warnings

import numpy as np
import xarray as xr

warnings.filterwarnings("ignore")


a = xr.open_dataset(r".tmp\scratchpad\2026-09-18_1316\out_nc_sync.nc")
b = xr.open_dataset(r".tmp\scratchpad\2026-09-18_1316\out_zarr_thr.nc")
print("same vars:", sorted(a.data_vars) == sorted(b.data_vars))
print("same time axis:", bool((a.time.values == b.time.values).all()))
ok = True
for v in sorted(a.data_vars):
    same = np.array_equal(a[v].values, b[v].values, equal_nan=True)
    d = float(np.nanmax(np.abs(a[v].values - b[v].values)))
    print(f"  {v:10s} bit-identical={same}  maxdiff={d:.6g}")
    ok &= same
print("ALL IDENTICAL:", ok)
