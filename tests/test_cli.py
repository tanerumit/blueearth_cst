"""Test some snake command line interface (CLI) for validity of snakefiles."""

import os
from os.path import join, dirname, realpath
from pathlib import Path
import subprocess

import yaml
import pytest

TESTDIR = dirname(realpath(__file__))
SNAKEDIR = join(TESTDIR, "..")

config_fn = join(TESTDIR, "snake_config_model_test.yml")

# Minimal valid GeoJSON standing in for the workflow-1 region output that
# climate_projections consumes as a cross-workflow input (see the fixture).
_MINIMAL_REGION_GEOJSON = (
    '{"type": "FeatureCollection", "features": [{"type": "Feature", '
    '"properties": {}, "geometry": {"type": "Polygon", "coordinates": '
    "[[[0, 0], [0, 1], [1, 1], [1, 0], [0, 0]]]}}]}"
)


def _dry_run(snakefile, cfg=config_fn):
    """Dry-run a Snakefile on a config; return the completed process.

    stdout/stderr are captured as text so callers can match on the DAG-build
    exception class name. Snakemake writes these diagnostics to stderr, but we
    match on the combined stream so a stream change does not silently break a
    ratchet assertion below.
    """
    os.chdir(SNAKEDIR)
    cmd = f"snakemake all -c 1 -s {snakefile} --configfile {cfg} --dry-run"
    return subprocess.run(cmd, shell=True, capture_output=True, text=True)


@pytest.fixture()
def config_with_staged_region(tmp_path):
    """Config whose project_dir is a temp dir pre-staged with region.geojson.

    climate_projections declares `{project_dir}/hydrology_model/staticgeoms/
    region.geojson` as an `ancient(...)` input produced by model_creation — a
    correct cross-workflow contract Snakemake will not satisfy on its own. To
    dry-run workflow 2 in isolation we stage a minimal valid region file under
    a **test-owned tmp project_dir** (never the tracked baseline dir) and point
    a copy of the test config at it. tmp_path is torn down by pytest.
    """
    with open(config_fn) as f:
        cfg = yaml.safe_load(f)
    cfg["project"]["project_dir"] = str(tmp_path).replace("\\", "/")

    region = tmp_path / "hydrology_model" / "staticgeoms" / "region.geojson"
    region.parent.mkdir(parents=True)
    region.write_text(_MINIMAL_REGION_GEOJSON, encoding="utf-8")

    cfg_path = tmp_path / "snake_config_staged.yml"
    cfg_path.write_text(yaml.safe_dump(cfg), encoding="utf-8")
    return cfg_path


def test_snakefile_cli_model_creation():
    """Workflow 1 dry-run builds a clean DAG on the test config."""
    result = _dry_run("Snakefile_model_creation")
    assert result.returncode == 0, (result.stdout or "") + (result.stderr or "")


def test_snakefile_cli_climate_projections(config_with_staged_region):
    """Workflow 2 dry-run builds a clean DAG once its WF1 region input is staged.

    climate_projections declares region.geojson (a model_creation output) as an
    `ancient(...)` input Snakemake will not build itself — correct behavior. R3
    stages it in a test-owned tmp project_dir (see the fixture) rather than
    weakening the contract; workflow 2's Snakefile is untouched (R4 territory).
    Was a MissingInputException ratchet pre-R3 (dev/followups.md).
    """
    result = _dry_run(
        "Snakefile_climate_projections", cfg=config_with_staged_region
    )
    assert result.returncode == 0, (result.stdout or "") + (result.stderr or "")


def test_climate_projections_declares_wf1_region_input():
    """Pin the fixture to the real contract it stands in for.

    The dry-run fixture stages `staticgeoms/region.geojson`; this guards that
    Snakefile_climate_projections still declares that exact workflow-1 output
    path as an input, so the fixture can never silently diverge from the
    cross-workflow contract.
    """
    text = Path(SNAKEDIR, "Snakefile_climate_projections").read_text()
    assert "staticgeoms/region.geojson" in text


# --- Known-failure ratchet (deferred to R5) ----------------------------------
#
# Snakefile_climate_experiment does NOT build a clean DAG on the test config: a
# CyclicGraphException at rule generate_climate_stress_test whose only fix is a
# wildcard/ruleorder edit inside that (R5-owned) Snakefile. Deferred to R5
# (dev/followups.md); the ratchet is retained here.
#
# Rather than a blanket `xfail(strict=True)` — which keeps "passing" on ANY
# failure and would mask a new/unrelated error — the test asserts the SPECIFIC
# known failure: a non-zero exit AND the exact DAG-build exception class.
#
# Ratchet semantics: when R5 fixes the cycle, the dry-run will succeed,
# `returncode != 0` will FAIL, and this test goes red. The fixer then converts
# it back to a plain `assert result.returncode == 0` success assertion.


def test_snakefile_cli_climate_experiment_known_cyclic_graph():
    """Workflow 3 dry-run fails with CyclicGraphException at the stress-test rule.

    climate_experiment trips a CyclicGraphException at rule
    generate_climate_stress_test. R3 followup (dev/followups.md).
    """
    result = _dry_run("Snakefile_climate_experiment")
    combined = (result.stdout or "") + (result.stderr or "")
    assert result.returncode != 0, combined
    assert "CyclicGraphException" in combined, combined
