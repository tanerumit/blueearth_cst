"""Test some snake command line interface (CLI) for validity of snakefiles."""

import os
from os.path import join, dirname, realpath
import subprocess
import pytest

TESTDIR = dirname(realpath(__file__))
SNAKEDIR = join(TESTDIR, "..")

config_fn = join(TESTDIR, "snake_config_model_test.yml")

# Snakefile_climate_projections and Snakefile_climate_experiment fail
# dry-run on the test config — climate_projections needs region.geojson
# from model_creation (cross-Snakefile dependency); climate_experiment
# trips a CyclicGraphException at rule generate_climate_stress_test.
# Both are pre-M2 failures and live in R3's territory (Snakefile cleanup,
# ruleorder). Tracked in dev/followups.md under R3.
_snakefiles = [
    "Snakefile_model_creation",
    pytest.param("Snakefile_climate_projections",
                 marks=pytest.mark.xfail(reason="R3 followup: missing input cross-Snakefile dep", strict=True)),
    pytest.param("Snakefile_climate_experiment",
                 marks=pytest.mark.xfail(reason="R3 followup: cyclic dependency at generate_climate_stress_test", strict=True)),
]


@pytest.mark.parametrize("snakefile", _snakefiles)
def test_snakefile_cli(snakefile):
    os.chdir(SNAKEDIR)
    cmd = f"snakemake all -c 1 -s {snakefile} --configfile {config_fn} --dry-run"
    result = subprocess.run(cmd, shell=True, capture_output=True)
    assert result.returncode == 0
