"""Function to update a wflow model and add gauges and outputs."""
import os
from os.path import join
from pathlib import Path
from typing import List, Union

from hydromt_wflow import WflowSbmModel


# Map user-facing semantic names to Wflow.jl 1.x CSDMS variable names.
# Mapping derived from
# .pixi/envs/default/Lib/site-packages/hydromt_wflow/version_upgrade.py.
WFLOW_VARS = {
    "river discharge": "river_water__volume_flow_rate",
    "precipitation": "atmosphere_water__precipitation_volume_flux",
    "overland flow": "land_surface_water__volume_flow_rate",
    "actual evapotranspiration": "land_surface__evapotranspiration_volume_flux",
    "groundwater recharge": "soil_water_saturated_zone_top__net_recharge_volume_flux",
    "snow": "snowpack_liquid_water__depth",
}


def update_wflow_gauges_outputs(
    wflow_root: Union[str, Path],
    data_catalog: Union[str, Path] = "deltares_data",
    gauges_fn: Union[str, Path, None] = None,
    outputs: List[str] = ["river discharge"],
):
    """
    Update wflow model with output and optionally gauges locations
    """
    mod = WflowSbmModel(wflow_root, mode="r+", data_libs=data_catalog)

    river_q_csdms = WFLOW_VARS["river discharge"]

    mod.setup_outlets(
        river_only=True,
        gauge_toml_header=["Q"],
        gauge_toml_param=[river_q_csdms],
    )

    if gauges_fn is not None and os.path.isfile(gauges_fn):
        mod.setup_gauges(
            gauges_fn=gauges_fn,
            snap_to_river=True,
            derive_subcatch=True,
            toml_output="csv",
            gauge_toml_header=["Q", "P"],
            gauge_toml_param=[
                river_q_csdms,
                WFLOW_VARS["precipitation"],
            ],
        )

    # Basin-average timeseries for any extra outputs (river discharge already
    # covered above for outlets/gauges).
    extras = [v for v in outputs if v != "river discharge" and v in WFLOW_VARS]
    if extras:
        mod.setup_config_output_timeseries(
            mapname="subcatchment",
            toml_output="csv",
            header=[f"{v}_basavg" for v in extras],
            param=[WFLOW_VARS[v] for v in extras],
            reducer=["mean"] * len(extras),
        )

    mod.write()
    # mod.close() commits deferred staticmaps writes — without it,
    # hydromt 1.x leaves the new variables in `staticmaps_<hash>.nc`
    # temp files instead of swapping them into the real file.
    mod.close()


if __name__ == "__main__":
    if "snakemake" in globals():
        sm = globals()["snakemake"]
        update_wflow_gauges_outputs(
            wflow_root=os.path.dirname(sm.input.basin_nc),
            data_catalog=sm.params.data_catalog,
            gauges_fn=sm.params.output_locs,
            outputs=sm.params.outputs,
        )
    else:
        update_wflow_gauges_outputs(
            wflow_root=join(os.getcwd(), "examples", "my_project", "hydrology_model"),
            data_catalog="deltares_data",
            gauges_fn=None,
            outputs=["river discharge"],
        )
