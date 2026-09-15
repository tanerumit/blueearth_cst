"""Synthetic R12 feasibility gates; these do not validate production WF3."""

import hashlib
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


def _retained_fixture(tmp_path: Path) -> str:
    """Stage a synthetic inventory and independently calculate its metric target."""
    response = tmp_path / "hydrology/wflow/output.csv"
    response.parent.mkdir(parents=True, exist_ok=True)
    response.write_bytes(b"q\n1\n")
    inventory = {
        "artifact": "hydrology/wflow/output.csv",
        "variables": ["q"],
        "sha256": hashlib.sha256(response.read_bytes()).hexdigest(),
    }
    retained = tmp_path / "retained"
    retained.mkdir(exist_ok=True)
    (retained / "inventory.json").write_text(json.dumps(inventory), encoding="utf-8")
    metric_id = hashlib.sha256(
        json.dumps(
            {"response": inventory, "declaration": "synthetic-q-v1"}, sort_keys=True
        ).encode()
    ).hexdigest()
    return f"metrics/{metric_id}/metrics.json"


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


@pytest.mark.parametrize("operation", ["simulate-and-metrics", "metrics-only"])
@pytest.mark.parametrize(
    "target",
    ["default", "all", "metrics", "selected", "wrong", "wflow", "mixed", "unknown"],
)
def test_mandatory_runner_target_matrix(
    tmp_path: Path, operation: str, target: str
) -> None:
    """Actual target arguments cannot bypass the mandatory prelaunch boundary."""
    selected = "metrics/" + "a" * 64 + "/metrics.json"
    if operation == "metrics-only":
        selected = _retained_fixture(tmp_path)
    arguments = {
        "default": [],
        "all": ["all"],
        "metrics": ["metrics"],
        "selected": [selected],
        "wrong": ["metrics/" + "0" * 64 + "/metrics.json"],
        "wflow": ["hydrology/wflow/output.csv"],
        "mixed": ["all", "metrics"],
        "unknown": ["unrecognized"],
    }[target]
    allowed = (
        operation == "simulate-and-metrics" and target in {"default", "all"}
    ) or (operation == "metrics-only" and target in {"metrics", "selected"})
    for mode in ("dry-run", "execute"):
        command = _runner("--operation", operation)
        if arguments:
            command.extend(["--target", *arguments])
        if mode == "dry-run":
            command.append("--dry-run")
        code, output = _run_p0(tmp_path, command, mode)
        if not allowed:
            assert code != 0, output
            assert "UnsupportedOperationTarget" in output
            assert "supported pairs:" in output
            assert "P0_LAUNCH_SNAKEMAKE" not in output
            assert not (tmp_path / "planning").exists()
            continue
        assert code == 0, output
        assert output.count("P0_LAUNCH_SNAKEMAKE") == 1
        expected_rules = {"plan_metrics"}
        if target != "selected":
            expected_rules.add(
                "all" if operation == "simulate-and-metrics" else "metrics"
            )
        if operation == "simulate-and-metrics":
            expected_rules.update({"simulate_response", "inventory_response"})
        if mode == "execute" or target == "selected":
            expected_rules.add("reduce_metric")
        observed_rules = set(
            re.findall(r"^(?:local)?(?:rule|checkpoint) (\w+):", output, re.M)
        )
        assert observed_rules == expected_rules, output
        if operation == "metrics-only":
            assert "simulate_response" not in output
            assert "inventory_response" not in output
        else:
            assert "simulate_response" in output
            assert "inventory_response" in output
        assert "plan_metrics" in output
        if mode == "execute":
            plan = json.loads((tmp_path / "planning/metric.json").read_text())
            ready = json.loads((tmp_path / plan["target"]).read_text())
            assert ready["id"] == plan["id"]
            assert ready["fixture_value"] == "q\n1\n"


@pytest.mark.parametrize("missing", ["inventory", "variable", "artifact"])
def test_mandatory_runner_missing_response_refuses(
    tmp_path: Path, missing: str
) -> None:
    """Valid metrics target cannot admit simulation when retained state is incomplete."""
    _retained_fixture(tmp_path)
    inventory_path = tmp_path / "retained/inventory.json"
    if missing == "inventory":
        inventory_path.unlink()
    elif missing == "variable":
        inventory = json.loads(inventory_path.read_text())
        inventory["variables"] = []
        inventory_path.write_text(json.dumps(inventory), encoding="utf-8")
    else:
        (tmp_path / "hydrology/wflow/output.csv").unlink()
    for mode in ("dry-run", "execute"):
        command = _runner("--operation", "metrics-only", "--target", "metrics")
        if mode == "dry-run":
            command.append("--dry-run")
        code, output = _run_p0(tmp_path, command, mode)
        assert code != 0, output
        assert "MissingResponseRequirement" in output
        assert "simulate_response" not in output
        assert not (tmp_path / "planning").exists()


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
