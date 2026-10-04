"""Synthetic R12 checkpoint gates; these do not validate production WF3.

The rest of the R12 feasibility suite was retired with t2610041227. These two
cases stay because they are the only check that Snakemake keeps the checkpoint
behaviour the successor workflows rely on: an honest fresh dry-run, reuse under
`--forceall`, and refusal of a corrupt or byte-stale publication. Port them to
`simulate_system.smk` once a retained v2 experiment fixture exists, then delete
this file. The production `test_p2_current_carrier` fixture is a v1-layout
project and cannot drive a real metrics-only run.
"""

import json
import os
import re
import subprocess
import sys
from pathlib import Path

import pytest

pytestmark = pytest.mark.workflow_contract

FIXTURE = (
    Path(__file__).resolve().parents[1]
    / "dev/records/milestones/r12/implementation/feasibility/p2b.smk"
)


def _job_counts(output: str) -> dict[str, int]:
    """Read the complete first public CLI job table, including its total."""
    table = re.search(r"job\s+count\s*\n[- ]+\n(.*?)(?:\n\s*\n|$)", output, re.S)
    assert table, output
    return {
        name: int(count)
        for name, count in re.findall(r"^(\w+)\s+(\d+)\s*$", table[1], re.M)
    }


def _run_p0(tmp_path: Path, command: list[str], label: str) -> tuple[int, str]:
    """Retain a complete command/output pair for each bounded synthetic call."""
    environment = os.environ.copy()
    environment.pop("SNAKEMAKE_PROFILE", None)
    environment.pop("SNAKEMAKE_WORKFLOW_PROFILE", None)
    result = subprocess.run(
        command,
        cwd=tmp_path,
        env=environment,
        capture_output=True,
        text=True,
        timeout=120,
    )
    output = result.stdout + result.stderr
    (tmp_path / f"{label}.log").write_text(output, encoding="utf-8")
    (tmp_path / f"{label}-command.json").write_text(
        json.dumps(command, indent=2), encoding="utf-8"
    )
    return result.returncode, output


def _runner(*args: str) -> list[str]:
    """Build the supported synthetic simulation command."""
    return [sys.executable, str(FIXTURE.with_name("simulation-runner.py")), *args]


@pytest.mark.parametrize("kind", ["source", "metric"])
def test_checkpoint_fresh_reuse_and_refusal(tmp_path: Path, kind: str) -> None:
    """Single-call planning, honest dry-runs, forced reuse and stale-byte refusal."""
    if kind == "source":
        source = tmp_path / "raw/source.txt"
        source.parent.mkdir()
        source.write_text("synthetic forcing\n", encoding="utf-8")
        command = [
            sys.executable,
            "-m",
            "snakemake",
            "all",
            "--snakefile",
            str(FIXTURE.with_name("source-checkpoint.smk")),
            "--cores",
            "1",
            "--nocolor",
        ]
        identity_word = "collection"
        producers = {"all", "extract_source", "prepare_collection_sources"}
        plan_path = tmp_path / "planning/source.json"
    else:
        command = _runner()
        identity_word = "metric"
        producers = {"all", "simulate_response", "inventory_response", "plan_metrics"}
        plan_path = tmp_path / "planning/metric.json"
    code, output = _run_p0(tmp_path, [*command, "--dry-run"], "fresh-dry-run")
    assert code == 0, output
    assert f"P0_UNRESOLVED {identity_word} identity" in output
    assert "<TBD>" in output
    assert set(_job_counts(output)) == producers | {"total"}
    assert not plan_path.exists()
    code, output = _run_p0(tmp_path, command, "fresh-execute")
    assert code == 0, output
    assert set(
        re.findall(r"^(?:local)?(?:rule|checkpoint) (\w+):", output, re.M)
    ) == producers | {"publish_collection" if kind == "source" else "reduce_metric"}
    plan = json.loads(plan_path.read_text())
    ready = tmp_path / plan["target"]
    original = ready.read_bytes()
    code, output = _run_p0(tmp_path, [*command, "--forceall"], "forced-reuse")
    assert code == 0, output
    assert "P0_REUSED" in output
    assert ready.read_bytes() == original

    # A corrupt publication must survive refusal, rather than be silently repaired.
    ready.write_text('{"corrupt": true}', encoding="utf-8")
    corrupt = ready.read_bytes()
    code, output = _run_p0(tmp_path, [*command, "--forceall"], "forced-mismatch")
    assert code != 0, output
    assert "ImmutablePublicationMismatch" in output
    assert "Job stats:" not in output
    assert ready.read_bytes() == corrupt
    # Rebuildable plan loss must not remove the retained publication either.
    plan_path.unlink()
    code, output = _run_p0(tmp_path, [*command, "--forceall"], "missing-plan-mismatch")
    assert code != 0, output
    assert "ImmutablePublicationMismatch" in output
    assert ready.read_bytes() == corrupt
    ready.write_bytes(original)

    original_plan = plan_path.read_bytes()
    invalid_plan = {**plan, "id": "0" * 64}
    plan_path.write_text(json.dumps(invalid_plan), encoding="utf-8")
    code, output = _run_p0(tmp_path, command, "stale-plan")
    assert code != 0, output
    assert ("StaleSourcePlan" if kind == "source" else "StaleMetricPlan") in output
    assert "Job stats:" not in output
    assert ready.read_bytes() == original
    plan_path.write_bytes(original_plan)

    # Keep timestamps unchanged: the read-only preflight must detect byte staleness.
    changed = tmp_path / (
        "prepared/source.txt" if kind == "source" else "hydrology/wflow/output.csv"
    )
    old_stat = changed.stat()
    changed.write_bytes(changed.read_bytes() + b"changed\n")
    os.utime(changed, ns=(old_stat.st_atime_ns, old_stat.st_mtime_ns))
    for mode in ("dry-run", "execute"):
        invocation = [*command, "--dry-run"] if mode == "dry-run" else command
        code, output = _run_p0(tmp_path, invocation, f"stale-{mode}")
        assert code != 0, output
        assert (
            "StaleSourcePlan" if kind == "source" else "StaleResponseArtifact"
        ) in output
        assert "Job stats:" not in output
        assert ready.read_bytes() == original
