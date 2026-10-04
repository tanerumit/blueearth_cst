"""End to end: all five workflows through the owned runner, from a fresh root.

Drives ``scripts/run_workflows.py`` -- the user's entry point -- over the rapid
config set, rewritten to write into a temporary project root, so no standing
tree under ``test_case/`` is touched and nothing carries over from an earlier
run. Each workflow's deliverable is then checked through the production
readers, not just for existence.

This replaces three per-workflow smoke tests that had drifted until none could
test anything (t2610041227): two pointed at pre-R9 paths, one force-rebuilt the
standing baseline tree, and one drove WF3 with bare Snakemake, which skips the
runner's pinned plan.

Opt-in and slow (tens of minutes): ``pixi run test-e2e``. It needs the local
data mirror the rapid catalogs name, juliaup-managed Julia, Rscript with
``weathergenr`` (``pixi run install``) and network access for WF2's CMIP6 reads,
and it skips by name when any of those is missing. CI cannot provide them, so
the validation ladder says when to run it locally.
"""

from __future__ import annotations

import shutil
import socket
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

pytestmark = pytest.mark.integration

REPO = Path(__file__).resolve().parents[1]
CONFIG = REPO / "test_case" / "project_config_rapid.yml"


def _catalog_root():
    """First data root the rapid project's first catalog declares, or None."""
    project = yaml.safe_load(CONFIG.read_text(encoding="utf-8"))
    catalogs = project["project"]["catalog"]
    first = catalogs[0] if isinstance(catalogs, list) else catalogs
    meta = (yaml.safe_load((REPO / first).read_text(encoding="utf-8")) or {}).get(
        "meta"
    ) or {}
    roots = meta.get("roots") or ([meta["root"]] if "root" in meta else [])
    return roots[0] if roots else None


def _weathergenr_available():
    if shutil.which("Rscript") is None:
        return False
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


def _gcs_reachable():
    try:
        socket.create_connection(("storage.googleapis.com", 443), timeout=5).close()
        return True
    except OSError:
        return False


def _skip_without_prerequisites():
    root = _catalog_root()
    if root is None or not Path(root).exists():
        pytest.skip(f"data mirror not found (catalog root: {root})")
    if shutil.which("julia") is None:
        pytest.skip("julia not on PATH (juliaup-managed Julia required)")
    if not _weathergenr_available():
        pytest.skip("weathergenr not loadable via Rscript (run `pixi run install`)")
    if not _gcs_reachable():
        pytest.skip("Google Cloud Storage (storage.googleapis.com:443) not reachable")


def _fresh_config_set(base: Path, project: Path) -> Path:
    """Copy the rapid config set beside ``base`` with ``project_dir`` redirected.

    Every ``config_path`` resolves against the project file's own directory, so
    the workflow files travel with it; every other path key resolves from the
    run directory, which stays the repository.
    """
    for source in sorted(CONFIG.parent.glob(f"{CONFIG.stem}*.yml")):
        shutil.copyfile(source, base / source.name)
    target = base / CONFIG.name
    document = yaml.safe_load(target.read_text(encoding="utf-8"))
    document["project"]["project_dir"] = project.as_posix()
    target.write_text(yaml.safe_dump(document, sort_keys=False), encoding="utf-8")
    return target


def _one(paths):
    found = sorted(paths)
    assert len(found) == 1, found
    return found[0]


def test_all_five_workflows_run_end_to_end_from_a_fresh_root(tmp_path):
    _skip_without_prerequisites()
    from blueearth_cst.experiment.metric_plan import read_metric_set
    from blueearth_cst.experiment.scenario_collection_v2 import read_collection_v2
    from blueearth_cst.experiment.simulation_record import read_simulation_v2

    project = tmp_path / "project"
    config = _fresh_config_set(tmp_path, project)
    log = tmp_path / "run_workflows.log"
    with log.open("w", encoding="utf-8") as handle:
        result = subprocess.run(
            [
                sys.executable,
                "scripts/run_workflows.py",
                "--config",
                str(config),
                "--project-dir",
                str(project),
                "--cores",
                "3",
            ],
            cwd=REPO,
            stdout=handle,
            stderr=subprocess.STDOUT,
            text=True,
            timeout=3 * 3600,
        )
    output = log.read_text(encoding="utf-8", errors="replace")
    assert result.returncode == 0, output[-6000:]

    # WF0 builds one historical store per compared source and compares them;
    # WF1 forces from the selected source's store and runs Wflow.
    historical = project / "data/climate/historical"
    selected = yaml.safe_load(config.read_text(encoding="utf-8"))["climate"]["selected"]
    assert _one(historical.glob(f"{selected}_*/extract_historical.nc"))
    assert (historical / "comparison/dataset_comparison.csv").stat().st_size > 0
    discharge = project / "models/hydrology/wflow/run_default/output_q.csv"
    assert discharge.stat().st_size > 0
    # WF2: the CMIP6 change factors.
    annual = project / "data/climate/projections/cmip6/summary"
    assert (annual / "cmip6_change_factors_annual.csv").stat().st_size > 0
    # WF3: one ready scenario collection, read back by the production reader.
    marker = _one(project.glob("scenarios/_engine/collections/*/collection.json"))
    assert read_collection_v2(marker)["status"] == "ready"
    # WF4: a ready simulation and one published, readable metric set.
    experiment = project / "experiments" / "experiment_rapid"
    assert read_simulation_v2(experiment)["status"] == "ready"
    metrics = _one(experiment.glob("_engine/metric_sets/*/metrics.json"))
    manifest = read_metric_set(experiment, metrics)
    tables = [experiment / item["file"]["path"] for item in manifest["tables"]]
    assert tables and all(path.stat().st_size > 0 for path in tables)
