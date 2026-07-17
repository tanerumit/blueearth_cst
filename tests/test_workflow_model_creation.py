"""End-to-end smoke test for the model-creation workflow (workflow 1).

Unlike ``test_cli.py`` (which only ``--dry-run``s the DAG), this actually runs
``snakemake all`` on the small test basin: it builds the Wflow model with
hydromt, adds forcing, and runs Wflow.jl to completion, then checks that the
discharge output was produced. This is the check that would have caught the
data-catalog and Julia failures that a dry-run cannot see.

It is opt-in and slow. It needs:
  * the local Deltares data mirror referenced by ``config/deltares_data.yml``
  * juliaup-managed Julia 1.11.7 with the project instantiated (``pixi run install``)

Run it with::

    pixi run pytest tests/test_workflow_model_creation.py --run-integration

Skipped by default, and self-skips if the data mirror or Julia is absent.
"""

import os
import shutil
import subprocess
from os.path import join, dirname, realpath, exists, getsize

import yaml
import pytest

TESTDIR = dirname(realpath(__file__))
SNAKEDIR = join(TESTDIR, "..")

# The config that actually runs end-to-end (project_dir: examples/test,
# data_sources: the full config/deltares_data.yml mirror).
CONFIG = "config/snake_config_model_test.yml"
OUTPUT_CSV = join(
    SNAKEDIR, "examples", "test", "hydrology_model", "run_default", "output.csv"
)

pytestmark = pytest.mark.integration


def _catalog_root():
    """First data root declared by the config's data catalog, or None."""
    with open(join(SNAKEDIR, CONFIG)) as f:
        cfg = yaml.safe_load(f)
    with open(join(SNAKEDIR, cfg["data_sources"])) as f:
        cat = yaml.safe_load(f)
    meta = cat.get("meta", {}) or {}
    roots = meta.get("roots") or ([meta["root"]] if "root" in meta else [])
    return roots[0] if roots else None


_ROOT = _catalog_root()


@pytest.mark.skipif(
    _ROOT is None or not exists(_ROOT),
    reason=f"data mirror not found (catalog root: {_ROOT})",
)
@pytest.mark.skipif(
    shutil.which("julia") is None,
    reason="julia not on PATH (juliaup-managed Julia 1.11.7 required)",
)
def test_model_creation_end_to_end():
    """Force a full rebuild of workflow 1 and assert Wflow output is produced."""
    os.chdir(SNAKEDIR)
    cmd = (
        f"snakemake all -c 1 -s Snakefile_model_creation "
        f"--configfile {CONFIG} --forceall"
    )
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

    assert result.returncode == 0, (
        f"snakemake exited {result.returncode}\n"
        f"--- stderr (tail) ---\n{(result.stderr or '')[-4000:]}"
    )
    assert exists(OUTPUT_CSV), f"expected output not created: {OUTPUT_CSV}"
    assert getsize(OUTPUT_CSV) > 0, f"output is empty: {OUTPUT_CSV}"
