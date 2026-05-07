"""Inspect spatial_ref attributes in extract_historical.nc and rlz_*_cst_0.nc.

weathergenr's write_netcdf needs `x_dim` and `y_dim` attributes on the
template's `spatial_ref` variable. Confirm whether they're present in the
historical file (used as template by generate_weather), and whether they
get propagated to the realization output (used as template by
impose_climate_change).
"""
from pathlib import Path
from netCDF4 import Dataset

paths = [
    Path("examples/test_local/climate_historical/raw_data/extract_historical.nc"),
    Path("examples/test_local/climate_experiment/realization_1/rlz_1_cst_0.nc"),
    Path("examples/test_local/climate_experiment/realization_2/rlz_2_cst_0.nc"),
]

for p in paths:
    print(f"\n=== {p} ===")
    if not p.exists():
        print("  (not present)")
        continue
    with Dataset(p) as ds:
        print(f"  dims: {dict((d, len(ds.dimensions[d])) for d in ds.dimensions)}")
        if "spatial_ref" in ds.variables:
            attrs = ds.variables["spatial_ref"].ncattrs()
            print(f"  spatial_ref attrs: {attrs}")
            for a in attrs:
                v = ds.variables["spatial_ref"].getncattr(a)
                if isinstance(v, str) and len(v) > 80:
                    v = v[:80] + "..."
                print(f"    {a} = {v!r}")
        else:
            print("  no 'spatial_ref' variable")
