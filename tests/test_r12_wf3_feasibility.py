"""Synthetic R12 feasibility gates; these do not validate production WF3."""

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
    / "dev/milestones/r12/implementation/feasibility/p2b.smk"
)


def _job_counts(output: str) -> dict[str, int]:
    """Read the complete first public CLI job table, including its total."""
    table = re.search(r"job\s+count\s*\n[- ]+\n(.*?)(?:\n\s*\n|$)", output, re.S)
    assert table, output
    return {
        name: int(count)
        for name, count in re.findall(r"^(\w+)\s+(\d+)\s*$", table[1], re.M)
    }


@pytest.mark.parametrize("state", ["resolvable", "missing", "no-derived"])
def test_p2b_alternation_and_ancestor_compose(tmp_path: Path, state: str) -> None:
    """Require the intended jobs and exact ancestor consumption in both modes."""
    environment = os.environ.copy()
    environment.pop("SNAKEMAKE_PROFILE", None)
    environment.pop("SNAKEMAKE_WORKFLOW_PROFILE", None)
    command = [
        sys.executable,
        "-m",
        "snakemake",
        "all",
        "--snakefile",
        str(FIXTURE),
        "--cores",
        "1",
        "--nocolor",
        "--config",
        f"state={state}",
    ]
    for mode in ("dry-run", "execute"):
        invocation = command + (["--dry-run"] if mode == "dry-run" else [])
        result = subprocess.run(
            invocation,
            cwd=tmp_path,
            env=environment,
            capture_output=True,
            text=True,
            timeout=120,
        )
        output = result.stdout + result.stderr
        (tmp_path / f"{mode}.log").write_text(output, encoding="utf-8")
        (tmp_path / f"{mode}-command.json").write_text(
            json.dumps(invocation, indent=2), encoding="utf-8"
        )
        if state == "missing":
            assert result.returncode != 0, output
            assert "MissingInputException" in output, output
            assert "rule transform_forcing" in output, output
            assert "forcing/root-" in output.replace("\\", "/"), output
            assert not list(tmp_path.glob("forcing/*.txt"))
            continue

        assert result.returncode == 0, output
        expected = {"all": 1, "produce_root": 2, "total": 3}
        if state == "resolvable":
            expected.update(transform_forcing=2, total=5)
        assert _job_counts(output) == expected, output
        if mode == "dry-run":
            assert not list(tmp_path.glob("forcing/*.txt"))

    if state == "missing":
        return
    expected_content = {
        "root-a.txt": "source:root-a\n",
        "root-b.txt": "source:root-b\n",
    }
    if state == "resolvable":
        expected_content.update(
            {
                "child-a.txt": "source:root-a\ntransform:child-a\n",
                "child-b.txt": "source:root-b\ntransform:child-b\n",
            }
        )
    assert {
        path.name: path.read_text(encoding="utf-8")
        for path in (tmp_path / "forcing").glob("*.txt")
    } == expected_content


@pytest.mark.parametrize(
    ("operation", "target", "expected_jobs"),
    [
        (
            "simulate-and-metrics",
            "all",
            {"all": 1, "simulate_response": 1, "reduce_metric": 1, "total": 3},
        ),
        ("metrics-only", "metrics", {"metrics": 1, "reduce_metric": 1, "total": 2}),
        # These successes are counterexamples, NOT accepted target behavior.
        (
            "simulate-and-metrics",
            "hydrology/wflow/output.csv",
            {"simulate_response": 1, "total": 1},
        ),
        ("simulate-and-metrics", "hydrology/wflow/output.csv", {}),
        ("metrics-only", "hydrology/wflow/output.csv", None),
    ],
)
def test_operation_conditional_rules_expose_target_bypass(
    tmp_path: Path,
    operation: str,
    target: str,
    expected_jobs: dict[str, int] | None,
) -> None:
    """Record why conditional rules fail the accepted parse-time target gate."""
    if operation == "metrics-only" or expected_jobs == {}:
        response = tmp_path / "hydrology/wflow/output.csv"
        response.parent.mkdir(parents=True)
        response.write_text("q\n1\n", encoding="utf-8")
    if operation == "metrics-only":
        retained = tmp_path / "retained"
        retained.mkdir()
        (retained / "inventory.json").write_text(
            json.dumps({"variables": ["q"], "artifact": "hydrology/wflow/output.csv"}),
            encoding="utf-8",
        )
    environment = os.environ.copy()
    environment.pop("SNAKEMAKE_PROFILE", None)
    environment.pop("SNAKEMAKE_WORKFLOW_PROFILE", None)
    for mode in ("dry-run", "execute"):
        command = [
            sys.executable,
            "-m",
            "snakemake",
            target,
            "--snakefile",
            str(FIXTURE.with_name("operation-target.smk")),
            "--cores",
            "1",
            "--nocolor",
            "--config",
            f"operation={operation}",
        ]
        if mode == "dry-run":
            command.append("--dry-run")
        result = subprocess.run(
            command,
            cwd=tmp_path,
            env=environment,
            capture_output=True,
            text=True,
            timeout=120,
        )
        output = result.stdout + result.stderr
        (tmp_path / f"{mode}.log").write_text(output, encoding="utf-8")
        (tmp_path / f"{mode}-command.json").write_text(
            json.dumps(command, indent=2), encoding="utf-8"
        )
        assert f"P0_PARSE_COMPLETE operation={operation}" in output
        if expected_jobs is None:
            assert result.returncode != 0, output
            assert "MissingRuleException" in output, output
            assert "No rule to produce hydrology/wflow/output.csv" in output
            continue
        assert result.returncode == 0, output
        if expected_jobs:
            assert _job_counts(output) == expected_jobs, output
        else:
            assert "Nothing to be done" in output, output
            assert "Job stats:" not in output, output

    metric = tmp_path / "metrics/selected/result.txt"
    if target == "hydrology/wflow/output.csv":
        assert not metric.exists()
    else:
        assert metric.read_text(encoding="utf-8") == "q\n1\n"
