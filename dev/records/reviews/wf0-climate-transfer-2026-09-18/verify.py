"""Are two stores written by different paths the same data?

    python dev/working/2026-09-18_wf0-climate-transfer/verify.py [a.nc b.nc]

Defaults to the 2026-09-18 netCDF-vs-zarr pair.
"""

import sys
import warnings

import numpy as np
import xarray as xr

warnings.filterwarnings("ignore")


pair = sys.argv[1:3] or [
    r".tmp\scratchpad\2026-09-18_1316\out_nc_sync.nc",
    r".tmp\scratchpad\2026-09-18_1316\out_zarr_thr.nc",
]
a = xr.open_dataset(pair[0])
b = xr.open_dataset(pair[1])
print("same vars:", sorted(a.data_vars) == sorted(b.data_vars))
print("same time axis:", bool((a.time.values == b.time.values).all()))
ok = True
for v in sorted(a.data_vars):
    same = np.array_equal(a[v].values, b[v].values, equal_nan=True)
    d = float(np.nanmax(np.abs(a[v].values - b[v].values)))
    print(f"  {v:10s} bit-identical={same}  maxdiff={d:.6g}")
    ok &= same
print("ALL IDENTICAL:", ok)
