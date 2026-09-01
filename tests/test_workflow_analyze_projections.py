"""End-to-end smoke test for the climate-projections workflow (workflow 2).

Like ``test_workflow_build_model.py`` but for workflow 2: it runs
``snakemake all`` on ``analyze_projections.smk`` to completion and checks
that the CMIP6 change-factor summary is produced.

Workflow 2 reads CMIP6 monthly data from Google Cloud Storage (``gs://cmip6/...``
via gcsfs), so this needs internet access — it does not use the local data mirror
or Julia. It also depends on ``region.geojson`` from workflow 1 (an
``ancient(...)`` cross-Snakefile input that Snakemake will not build itself), so
run the model-creation workflow (or its smoke test) first.

Run it with::

    pixi run pytest tests/test_workflow_analyze_projections.py --run-integration

Skipped by default, and self-skips if ``region.geojson`` is missing or GCS is
unreachable.
"""

import os
import socket
import subprocess
from os.path import dirname, exists, getsize, join, realpath

import pytest
import yaml

TESTDIR = dirname(realpath(__file__))
SNAKEDIR = join(TESTDIR, "..")

CONFIG = "test_case/project_config_baseline.yml"

pytestmark = pytest.mark.integration


# Read lazily (inside the test), never at import time, so a migration cannot
# break collection of the whole suite.
#
# R13 split the project config into a SET, and R14 renamed the key: the ensemble
# no longer lives at `workflows.analyze_projections.clim_project` in the project
# file -- that stanza is now `{enabled, config_path}` -- but as `ensemble:`
# (`C-25`) at the top level of the WF2 file the stanza points at. Resolve through
# `config_path` rather than spelling the sibling filename, so the lookup follows
# the composition rule instead of a naming convention.
_PROJECT_PATHS = {
    "project_dir": ("project", "project_dir"),
}


def _cfg(key):
    config_path = join(SNAKEDIR, CONFIG)
    with open(config_path) as f:
        cfg = yaml.safe_load(f)
    if key == "ensemble":
        stanza = cfg["workflows"]["analyze_projections"]
        wf2_path = join(dirname(config_path), stanza["config_path"])
        with open(wf2_path) as f:
            return (yaml.safe_load(f) or {})["ensemble"]
    node = cfg
    for part in _PROJECT_PATHS[key]:
        node = node[part]
    return node


def _gcs_reachable():
    try:
        socket.create_connection(("storage.googleapis.com", 443), timeout=5).close()
        return True
    except OSError:
        return False


def test_analyze_projections_end_to_end():
    """Force a full rebuild of workflow 2 and assert the change summary is produced."""
    project_dir = _cfg("project_dir")
    clim_project = _cfg("ensemble")
    region = join(
        SNAKEDIR, project_dir, "hydrology_model", "staticgeoms", "region.geojson"
    )
    summary_csv = join(
        SNAKEDIR,
        project_dir,
        "analyze_projections",
        clim_project,
        "summary",
        "annual_change_scalar_stats_summary.csv",
    )
    if not exists(region):
        pytest.skip(f"missing {region}; run the model-creation workflow first")
    if not _gcs_reachable():
        pytest.skip("Google Cloud Storage (storage.googleapis.com:443) not reachable")

    os.chdir(SNAKEDIR)
    cmd = (
        f"snakemake all -c 1 -s analyze_projections.smk "
        f"--configfile {CONFIG} --forceall"
    )
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

    assert result.returncode == 0, (
        f"snakemake exited {result.returncode}\n"
        f"--- stderr (tail) ---\n{(result.stderr or '')[-4000:]}"
    )
    assert exists(summary_csv), f"expected output not created: {summary_csv}"
    assert getsize(summary_csv) > 0, f"output is empty: {summary_csv}"
