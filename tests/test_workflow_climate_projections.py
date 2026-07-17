"""End-to-end smoke test for the climate-projections workflow (workflow 2).

Like ``test_workflow_model_creation.py`` but for workflow 2: it runs
``snakemake all`` on ``Snakefile_climate_projections`` to completion and checks
that the CMIP6 change-factor summary is produced.

Workflow 2 reads CMIP6 monthly data from Google Cloud Storage (``gs://cmip6/...``
via gcsfs), so this needs internet access — it does not use the local data mirror
or Julia. It also depends on ``region.geojson`` from workflow 1 (an
``ancient(...)`` cross-Snakefile input that Snakemake will not build itself), so
run the model-creation workflow (or its smoke test) first.

Run it with::

    pixi run pytest tests/test_workflow_climate_projections.py --run-integration

Skipped by default, and self-skips if ``region.geojson`` is missing or GCS is
unreachable.
"""

import os
import socket
import subprocess
from os.path import join, dirname, realpath, exists, getsize

import yaml
import pytest

TESTDIR = dirname(realpath(__file__))
SNAKEDIR = join(TESTDIR, "..")

CONFIG = "config/snake_config_model_test.yml"

pytestmark = pytest.mark.integration


def _cfg(key):
    with open(join(SNAKEDIR, CONFIG)) as f:
        return yaml.safe_load(f)[key]


_PROJECT_DIR = _cfg("project_dir")
_CLIM_PROJECT = _cfg("clim_project")

REGION = join(SNAKEDIR, _PROJECT_DIR, "hydrology_model", "staticgeoms", "region.geojson")
SUMMARY_CSV = join(
    SNAKEDIR,
    _PROJECT_DIR,
    "climate_projections",
    _CLIM_PROJECT,
    "annual_change_scalar_stats_summary.csv",
)


def _gcs_reachable():
    try:
        socket.create_connection(("storage.googleapis.com", 443), timeout=5).close()
        return True
    except OSError:
        return False


@pytest.mark.skipif(
    not exists(REGION),
    reason=f"missing {REGION}; run the model-creation workflow first",
)
@pytest.mark.skipif(
    not _gcs_reachable(),
    reason="Google Cloud Storage (storage.googleapis.com:443) not reachable",
)
def test_climate_projections_end_to_end():
    """Force a full rebuild of workflow 2 and assert the change summary is produced."""
    os.chdir(SNAKEDIR)
    cmd = (
        f"snakemake all -c 1 -s Snakefile_climate_projections "
        f"--configfile {CONFIG} --forceall"
    )
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

    assert result.returncode == 0, (
        f"snakemake exited {result.returncode}\n"
        f"--- stderr (tail) ---\n{(result.stderr or '')[-4000:]}"
    )
    assert exists(SUMMARY_CSV), f"expected output not created: {SUMMARY_CSV}"
    assert getsize(SUMMARY_CSV) > 0, f"output is empty: {SUMMARY_CSV}"
