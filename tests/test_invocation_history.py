"""P3 common invocation states and launcher failure boundaries."""

import hashlib
import json
from pathlib import Path

import pytest

from blueearth_cst.shared import invocation_history, workflow_archive_launch
from scripts import run_workflows, simulate_system


def _records(root: Path) -> list[dict]:
    folder = root / "config/runs/_engine/invocations"
    return [
        json.loads(path.read_text(encoding="utf-8")) for path in folder.glob("*.json")
    ]


def test_direct_dry_run_is_a_nonproductive_attempt(tmp_path, monkeypatch):
    monkeypatch.setattr(workflow_archive_launch.subprocess, "call", lambda *_a, **_k: 0)
    result = workflow_archive_launch.run_workflow(
        "analyze_climate", tmp_path / "missing.yml", tmp_path / "project", dry_run=True
    )
    assert result == 0
    (record,) = _records(tmp_path / "project")
    assert record["schema_version"] == "invocation/1"
    assert record["parent_invocation_id"] is None
    assert record["mode"] == "dry_run"
    assert record["work_performed"] == "no"
    assert record["status"] == "succeeded"
    assert record["configuration"]["run_record"] is None


def test_unobserved_hard_termination_stays_running(tmp_path):
    path, record = invocation_history.start(
        tmp_path,
        workflow="generate_scenarios",
        entry_point="scripts/run_workflows.py",
        command=["snakemake"],
        targets=["all"],
        mode="execute",
        contract_mode="legacy_wf3_interim",
    )
    assert json.loads(path.read_text(encoding="utf-8"))["status"] == "running"
    assert record["ended_at_utc"] is None
    assert record["work_performed"] == "unknown"


def test_parent_capture_failure_records_no_fabricated_child(tmp_path, monkeypatch):
    config = tmp_path / "project_config_test.yml"
    root = tmp_path / "project"
    config.write_text(
        f"project:\n  project_dir: {root}\nworkflows:\n"
        + "".join(
            f"  {name}:\n    enabled: {'true' if name == 'analyze_climate' else 'false'}\n"
            for name in run_workflows.WORKFLOW_ORDER
        ),
        encoding="utf-8",
    )

    def refuse(*_args, **_kwargs):
        raise ValueError("pre-parse capture failed")

    monkeypatch.setattr(workflow_archive_launch, "prepare_workflow", refuse)
    with pytest.raises(ValueError, match="pre-parse capture failed"):
        run_workflows.run(str(config), cores=1, extra=[])
    (parent,) = _records(root)
    assert parent["workflow"] is None
    assert parent["status"] == "failed"
    assert parent["children"] == []
    assert parent["launch_failures"][0]["workflow"] == "analyze_climate"


def test_explicit_root_records_config_failure_before_child(tmp_path):
    root = tmp_path / "project"
    with pytest.raises(run_workflows.ConfigError):
        run_workflows.run(
            str(tmp_path / "missing.yml"), cores=1, extra=[], project_dir=root
        )
    (parent,) = _records(root)
    assert parent["status"] == "failed"
    assert parent["children"] == []
    assert parent["error"]["type"] == "ConfigError"


def test_simulation_explicit_root_records_startup_failure(tmp_path):
    root = tmp_path / "project"
    with pytest.raises((OSError, ValueError)):
        simulate_system.main(
            ["--config", str(tmp_path / "missing.yml"), "--project-dir", str(root)]
        )
    (record,) = _records(root)
    assert record["workflow"] == "simulate_system"
    assert record["status"] == "failed"
    assert record["children"] == []
    assert record["configuration"]["run_record"] is None


def test_interim_wf3_retains_exact_config_source_bytes(tmp_path):
    source = Path(__file__).resolve().parents[1] / "test_case/project_config_rapid.yml"
    digest = run_workflows._capture_legacy_wf3_attempt(source, tmp_path, "attempt")
    copied = list(
        (tmp_path / "config/runs/_engine/invocations/attempt/config/sources").rglob(
            source.name
        )
    )
    assert len(copied) == 1
    assert copied[0].read_bytes() == source.read_bytes()
    assert digest == hashlib.sha256(source.read_bytes()).hexdigest()
