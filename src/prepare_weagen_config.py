"""Assemble a weathergenr config YAML for a generate or stress-test run.

The config-assembly body was previously module-level code reading the
``snakemake`` global on import, which made it un-importable for unit tests.
R5 extracts it into named functions (``build_weagen_config`` /
``compute_nr_years``) above a nested ``__main__`` / ``globals()`` guard so the
year math is reachable without a live ``snakemake`` global. Behavior-neutral:
the same dict is assembled and written.
"""

import os
import math
import yaml


def read_yml(yml_path):
    """Read a yml file and return a dictionary."""
    with open(yml_path, "r") as stream:
        yml = yaml.load(stream, Loader=yaml.FullLoader)
    return yml


def compute_nr_years(middle_year, wflow_run_length):
    """Number of weagen years to generate.

    Spans from the end of the historical period (2010) to the wflow run window
    around the horizon (``middle_year`` ± ``wflow_run_length``/2), plus a 2-year
    pad. The ``2010`` and ``+2`` literals are the historical-end anchor and pad.
    """
    return math.ceil((middle_year + wflow_run_length / 2) - 2010 + 2)


def build_weagen_config(
    cftype,
    snake_config_path,
    output_path,
    nc_file_prefix,
    default_config_path=None,
    middle_year=None,
    sim_years=None,
    nc_file_suffix=None,
):
    """Assemble the weathergenr config dict for a ``generate`` or stress-test run.

    ``generate`` seeds the dict from the default weagen config and overrides the
    output path, historical start year, number of years (``compute_nr_years``),
    file prefix, and realization count. The stress-test branch (``cftype`` !=
    ``"generate"``) builds a minimal ``imposeClimateChanges`` block plus the
    ``temp``/``precip`` perturbation sections copied from the snake config; it
    carries **no** arithmetic.
    """
    yml_snake = read_yml(snake_config_path)

    if cftype == "generate":
        nr_years_weagen = compute_nr_years(middle_year, sim_years)
        # arguments from the default weagen config file
        yml_dict = read_yml(default_config_path)
        # add new arguments from snakemake and yml_snake (R01 sectioned schema)
        experiment_cfg = yml_snake["workflows"]["climate_experiment"]
        yml_add = {
            "output.path": output_path,
            "sim.year.start": 2010,
            "sim.year.num": nr_years_weagen,
            "nc.file.prefix": nc_file_prefix,
            "realizations_num": experiment_cfg["realizations_num"],
        }
        for k, v in yml_add.items():
            yml_dict["generateWeatherSeries"][k] = v
    else:  # stress test
        yml_dict = {
            "imposeClimateChanges": {
                "output.path": output_path,
                "nc.file.prefix": nc_file_prefix,
                "nc.file.suffix": nc_file_suffix,
            }
        }
        # arguments from yml_snake (R01 sectioned schema)
        stress_test_cfg = yml_snake["workflows"]["climate_experiment"]["stress_test"]
        yml_dict["temp"] = stress_test_cfg["temp"]
        yml_dict["precip"] = stress_test_cfg["precip"]

    return yml_dict


def write_weagen_config(yml_dict, weagen_config_path):
    """Write the assembled weagen config dict to ``weagen_config_path``."""
    if not os.path.isdir(os.path.dirname(weagen_config_path)):
        os.makedirs(os.path.dirname(weagen_config_path))
    with open(weagen_config_path, "w") as f:
        yaml.dump(yml_dict, f, default_flow_style=False, sort_keys=False)


if __name__ == "__main__":
    if "snakemake" in globals():
        sm = globals()["snakemake"]
        cftype = sm.params.cftype
        weagen_config = sm.output.weagen_config
        print(
            f"Preparing and writing the weather generator config file {weagen_config}"
        )
        if cftype == "generate":
            yml_dict = build_weagen_config(
                cftype=cftype,
                snake_config_path=sm.params.snake_config,
                output_path=sm.params.output_path,
                nc_file_prefix=sm.params.nc_file_prefix,
                default_config_path=sm.params.default_config,
                middle_year=sm.params.middle_year,
                sim_years=sm.params.sim_years,
            )
        else:  # stress test
            yml_dict = build_weagen_config(
                cftype=cftype,
                snake_config_path=sm.params.snake_config,
                output_path=sm.params.output_path,
                nc_file_prefix=sm.params.nc_file_prefix,
                nc_file_suffix=sm.params.nc_file_suffix,
            )
        write_weagen_config(yml_dict, weagen_config)
    else:
        raise ValueError("This script should be run from a snakemake environment")
