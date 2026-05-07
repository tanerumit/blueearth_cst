"""Update a wflow model with downscaled climate forcing for one realization."""
import os
from pathlib import Path

import numpy as np

from hydromt_wflow import WflowSbmModel


# Snakemake parameters
config_out_fn = snakemake.output.toml
fn_out = Path(snakemake.output.nc)
fn_in = snakemake.input.nc
data_libs = snakemake.input.data_sources
model_root = snakemake.params.model_dir

precip_source = snakemake.params.clim_source

horizontime_climate = snakemake.params.horizontime_climate
wflow_run_length = snakemake.params.run_length
startyear = int(horizontime_climate - np.ceil(wflow_run_length / 2))
endyear = int(horizontime_climate + np.round(wflow_run_length / 2))
starttime = f"{startyear}-01-01T00:00:00"
endtime = f"{endyear}-12-31T00:00:00"

oro_source = f"{precip_source}_orography"
pet_method = "makkink" if precip_source == "eobs" else "debruin"

fn_in_path = Path(fn_in, resolve_path=True)
climate_name = os.path.basename(fn_in_path).split(".")[0]

config_out_fn = Path(config_out_fn)
config_out_root = os.path.dirname(config_out_fn)
config_out_name = os.path.basename(config_out_fn)

# Instantiate model in r+ on the source root, then redirect writes to the
# per-realization run directory by rebinding root.
mod = WflowSbmModel(root=model_root, mode="r+", data_libs=data_libs)

size = mod.staticmaps.data.raster.size
if size > 1e6:
    chunksize = 1
elif size > 2.5e5:
    chunksize = 30
elif size > 1e5:
    chunksize = 100
else:
    chunksize = 365

mod.setup_config(
    data={
        "time.calendar": "noleap",
        "time.starttime": starttime,
        "time.endtime": endtime,
        "time.timestepsecs": 86400,
        "state.path_input": os.path.join("..", "instate", "instates.nc"),
        "state.path_output": f"outstates_{climate_name}.nc",
        "input.path_static": os.path.join("..", "staticmaps.nc"),
        "input.path_forcing": os.path.relpath(fn_out.resolve(), Path(config_out_root).resolve()),
        "output.csv.path": f"output_{climate_name}.csv",
    }
)

mod.setup_precip_forcing(
    precip_fn=climate_name,
    precip_clim_fn=None,
    chunksize=chunksize,
)
mod.setup_temp_pet_forcing(
    temp_pet_fn=climate_name,
    press_correction=True,
    temp_correction=True,
    dem_forcing_fn=oro_source,
    pet_method=pet_method,
    chunksize=chunksize,
)

# weagen has off-by-one timestamps at the year boundaries; clip the forcing
# in place via the component's data.
forcing = mod.forcing.data
for var in list(forcing.data_vars):
    forcing[var] = forcing[var].sel(time=slice(starttime, endtime))

# Refresh starttime/endtime from the actual forcing axis (weagen quirk).
last_var = next(iter(forcing.data_vars))
times = forcing[last_var].time.values
mod.config.set("time.starttime", str(times[0])[:19])
mod.config.set("time.endtime", str(times[-1])[:19])

# Write forcing + per-realization toml to absolute paths so the model root
# (which is the source hydrology_model dir) doesn't have to be moved.
mod.forcing.write(filename=str(fn_out.resolve()))
mod.config.write(
    filename=config_out_name,
    config_root=Path(config_out_root).resolve(),
)
mod.close()  # commit any deferred writes
