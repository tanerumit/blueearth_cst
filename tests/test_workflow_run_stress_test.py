"""Opt-in real generation and simulation smoke through the R12 entry points."""

import shutil
import subprocess
import sys
from os.path import dirname, exists, getsize, join, realpath
from pathlib import Path

import pytest
import yaml

TESTDIR = dirname(realpath(__file__))
SNAKEDIR = join(TESTDIR, "..")

CONFIG = "test_case/project_config_rapid.yml"

pytestmark = pytest.mark.integration


def _load_cfg():
    from blueearth_cst.shared.config_composition import load_composed_config

    return load_composed_config(join(SNAKEDIR, CONFIG))


def _catalog_root(cfg):
    """First data root declared by the config's data catalog, or None."""
    # R01 sectioned schema: data_sources lives under project.
    with open(join(SNAKEDIR, cfg["project"]["catalog"])) as f:
        cat = yaml.safe_load(f)
    meta = cat.get("meta", {}) or {}
    roots = meta.get("roots") or ([meta["root"]] if "root" in meta else [])
    return roots[0] if roots else None


def _weathergenr_available():
    """True if Rscript can load the weathergenr package."""
    result = subprocess.run(
        [
            "Rscript",
            "--vanilla",
            "-e",
            "quit(status=as.integer(!requireNamespace('weathergenr', quietly=TRUE)))",
        ],
        capture_output=True,
    )
    return result.returncode == 0


def test_generation_and_simulation_end_to_end():
    """Force a full rebuild of workflow 3 and assert the indicator tables are produced."""
    cfg = _load_cfg()
    # R01 sectioned schema: project_dir under project, experiment_name under
    # workflows.simulate_system.
    project_dir = cfg["project"]["project_dir"]
    experiment = cfg["workflows"]["simulate_system"]["experiment_name"]

    root = _catalog_root(cfg)
    if root is None or not exists(root):
        pytest.skip(f"data mirror not found (catalog root: {root})")

    region = join(
        SNAKEDIR,
        project_dir,
        "models",
        "hydrology",
        "wflow",
        "staticgeoms",
        "region.geojson",
    )
    if not exists(region):
        pytest.skip(f"missing {region}; run the model-creation workflow first")

    if shutil.which("julia") is None:
        pytest.skip("julia not on PATH (juliaup-managed Julia 1.11.7 required)")

    if shutil.which("Rscript") is None or not _weathergenr_available():
        pytest.skip("weathergenr not loadable via Rscript (run `pixi run install`)")

    commands = [
        [
            sys.executable,
            "-m",
            "snakemake",
            "all",
            "-c",
            "1",
            "-s",
            "generate_scenarios.smk",
            "--configfile",
            CONFIG,
        ],
        [
            sys.executable,
            "scripts/simulate_system.py",
            "--config",
            CONFIG,
            "--target",
            "all",
            "--cores",
            "1",
        ],
    ]
    for command in commands:
        result = subprocess.run(command, cwd=SNAKEDIR, capture_output=True, text=True)
        assert result.returncode == 0, (result.stdout or "") + (result.stderr or "")
    # One LONG table per output variable since R11 CR-2, and the seed config
    # declares `wflow_outvars: ["river discharge"]` -- so q_indicators.csv is
    # the whole expected set. `basin_indicators.csv` was asserted here until
    # 2026-08-09 (t2608082010); post-CR-2 nothing writes it, so this assertion
    # would have FAILED a real integration run. It never did, because the whole
    # case is --run-integration-gated and has not been run since. A stale
    # expectation behind an opt-in gate is invisible in exactly the way a stale
    # path behind an exists() guard is.
    sets = Path(
        SNAKEDIR, project_dir, "experiments", experiment, "results", "metric_sets"
    )
    tables = list(sets.glob("*/q_indicators.csv"))
    assert tables, f"no published metric table under {sets}"
    assert all(getsize(table) > 0 for table in tables)
