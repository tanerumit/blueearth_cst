"""Function to update a wflow model and add reservoirs, lakes and glaciers."""
import os
from os.path import join
from pathlib import Path
from typing import Union

import yaml
from hydromt_wflow import WflowSbmModel
from hydromt.error import NoDataException


def update_wflow_waterbodies_glaciers(
    wflow_root: Union[str, Path],
    config_fn: Union[str, Path],
    data_catalog: Union[str, Path] = "deltares_data",
):
    """
    Update wflow model with reservoirs, lakes and glaciers.

    Write a file when everything is done for snakemake tracking.

    Parameters
    ----------
    wflow_root : Union[str, Path]
        Path to the wflow model root folder
    config_fn : Union[str, Path]
        Path to the config file for setup of reservoirs, lakes and glaciers
    data_catalog : str
        Name of the data catalog to use
    """

    mod = WflowSbmModel(wflow_root, mode="r+", data_libs=data_catalog)

    with open(config_fn, "r") as f:
        config = yaml.safe_load(f) or {}

    successful_methods = []
    failed_methods = []
    reasons = []

    for method, kwargs in config.items():
        kwargs = kwargs or {}
        try:
            getattr(mod, method)(**kwargs)
            successful_methods.append(method)
        except (NoDataException, FileNotFoundError) as error:
            failed_methods.append(method)
            reasons.append(error)

    if successful_methods:
        mod.write()
        mod.close()  # commits deferred staticmaps writes

    text_out = join(wflow_root, "staticgeoms", "reservoirs_lakes_glaciers.txt")
    with open(text_out, "w") as f:
        f.write(f"Successful methods: {successful_methods}\n")
        f.write(f"Failed methods: {failed_methods}\n")
        f.write(f"Reasons: {reasons}\n")


if __name__ == "__main__":
    if "snakemake" in globals():
        sm = globals()["snakemake"]
        update_wflow_waterbodies_glaciers(
            wflow_root=os.path.dirname(sm.input.basin_nc),
            data_catalog=sm.params.data_catalog,
            config_fn=sm.params.config,
        )
    else:
        update_wflow_waterbodies_glaciers(
            wflow_root=join(os.getcwd(), "examples", "my_project", "hydrology_model"),
            data_catalog="deltares_data",
            config_fn=join(os.getcwd(), "config", "wflow_update_waterbodies.yml"),
        )
