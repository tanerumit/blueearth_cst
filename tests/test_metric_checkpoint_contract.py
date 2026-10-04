"""The production metric checkpoint under real Snakemake, over a retained v2 run.

`simulate_system.smk` plans metrics through `checkpoint prepare_indicator_plan`
and publishes an immutable set. These cases pin what a Snakemake upgrade or a
rule edit could quietly change, and what no unit test can see: a fresh dry-run
writes nothing, `--forceall` reuses the published set byte for byte, and a
byte-stale retained response is refused before anything is scheduled.
Metrics-only needs neither Julia nor a model build, so this runs on a bare
checkout; the publishing half is Windows-only because the harness refuses
project writers elsewhere. It replaces the R12 prototype checkpoint gates (t2610041227).
"""

import os
import re
import subprocess
import sys
from pathlib import Path

import pytest

from tests._v2_experiment import RUN_IDS, build_v2_experiment

pytestmark = pytest.mark.workflow_contract

REPO = Path(__file__).resolve().parents[1]


def _simulate(experiment, *extra):
    environment = os.environ.copy()
    environment.pop("SNAKEMAKE_PROFILE", None)
    environment.pop("SNAKEMAKE_WORKFLOW_PROFILE", None)
    result = subprocess.run(
        [
            sys.executable,
            str(REPO / "scripts/simulate_system.py"),
            "--config",
            str(experiment.config),
            "--target",
            "metrics",
            "--cores",
            "1",
            *extra,
        ],
        cwd=REPO,
        env=environment,
        capture_output=True,
        text=True,
        timeout=600,
    )
    return result.returncode, result.stdout + result.stderr


def _published(root):
    files = sorted(
        path
        for directory in ("_engine/metric_sets", "results/metric_sets")
        for path in (root / directory).rglob("*")
        if path.is_file()
    )
    return {path: path.read_bytes() for path in files}


def _tamper_keeping_timestamps(root):
    """Change a retained response in place without moving its mtime."""
    native = root / f"hydrology/wflow/output/run_{RUN_IDS[0]}.csv"
    stat = native.stat()
    native.write_bytes(native.read_bytes().replace(b",3\n", b",4\n"))
    os.utime(native, ns=(stat.st_atime_ns, stat.st_mtime_ns))


def test_a_dry_run_writes_nothing_and_a_stale_response_is_refused(tmp_path):
    """Both happen before any project writer is launched, so on every platform."""
    experiment = build_v2_experiment(tmp_path)
    root = experiment.root

    code, output = _simulate(experiment, "--dry-run")
    assert code == 0, output
    assert re.search(r"prepare_indicator_plan\s+1", output), output
    assert not (root / "_engine/metric_requests").exists()
    assert not (root / "_engine/metric_sets").exists()

    # Refused before any job is scheduled. A corrupt publication's refusal is
    # pinned in-process by test_metric_plan_v2, at a fraction of the cost.
    _tamper_keeping_timestamps(root)
    code, output = _simulate(experiment)
    assert code != 0, output
    assert "bytes differ" in output, output
    assert "Job stats:" not in output, output
    assert not (root / "_engine/metric_sets").exists()


@pytest.mark.skipif(
    os.name != "nt",
    reason="run_project_child refuses project writers off Windows: no verified "
    "lifetime guarantee for their descendants",
)
def test_a_published_set_is_reused_byte_for_byte_under_forceall(tmp_path):
    experiment = build_v2_experiment(tmp_path)
    root = experiment.root

    code, output = _simulate(experiment)
    assert code == 0, output
    published = _published(root)
    assert len(list((root / "_engine/metric_sets").glob("*/metrics.json"))) == 1
    assert any(path.name == "gwr_indicators.csv" for path in published)

    code, output = _simulate(experiment, "--forceall")
    assert code == 0, output
    assert _published(root) == published

    _tamper_keeping_timestamps(root)
    code, output = _simulate(experiment)
    assert code != 0, output
    assert _published(root) == published
