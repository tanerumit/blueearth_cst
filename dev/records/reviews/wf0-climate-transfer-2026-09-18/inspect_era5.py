import netCDF4 as nc

p = r"P:\wflow_global\hydromt\meteo\era5_daily\nc_merged\era5_2000_daily.nc"
d = nc.Dataset(p)
print("dims:", {k: len(v) for k, v in d.dimensions.items()})
for name, v in d.variables.items():
    print(
        name,
        v.dimensions,
        v.shape,
        v.dtype,
        "chunking=",
        v.chunking(),
        "filters=",
        v.filters(),
    )
