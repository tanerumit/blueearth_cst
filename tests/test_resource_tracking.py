"""Resource observations remain attributable and cannot replace run outcomes."""

import json
import subprocess
import sys
from pathlib import Path

import pytest

from blueearth_cst.shared import invocation_history, resource_tracking


def test_trace_tracks_child_and_retains_cpu_after_exit(tmp_path):
    monitor = resource_tracking.ResourceMonitor(tmp_path / "diagnostics", interval=60)
    monitor.start()
    child = subprocess.Popen(
        [
            sys.executable,
            "-u",
            "-c",
            "import sys; data=bytearray(16*1024*1024); sum(range(1000000)); "
            "print('ready', flush=True); sys.stdin.read()",
        ],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        text=True,
    )
    try:
        assert child.stdout.readline().strip() == "ready"
        monitor.mark("snakemake")
        monitor.sample()
        identity = next(key for key in monitor.processes if key[0] == child.pid)
        observed_cpu = monitor.processes[identity]["last"]["cpu_s"]
        child.communicate(timeout=10)
        monitor.mark("indicator_exports")
    finally:
        if child.poll() is None:
            child.kill()
            child.communicate()
        summary = monitor.finish()
    rows = [
        json.loads(line)
        for line in (monitor.directory / "resources.jsonl").read_text().splitlines()
    ]
    assert rows[0]["schema_version"] == "wf4-resources/1"
    assert rows[-1]["kind"] == "summary"
    assert summary["sampled_tree_cpu_s"] >= observed_cpu
    assert summary["sampled_peak_tree_rss_bytes"] >= 16 * 1024 * 1024
    assert summary["minimum_available_memory_bytes"] > 0
    assert [phase["name"] for phase in summary["phases"]] == [
        "preparation",
        "snakemake",
        "indicator_exports",
    ]
    assert all(phase["wall_s"] >= 0 for phase in summary["phases"])
    assert not any("command" in row for row in rows)
    assert any(row["kind"] == "process" and row["pid"] == child.pid for row in rows)


def test_unsupported_metrics_are_null_and_counted(tmp_path, monkeypatch):
    def denied():
        raise resource_tracking.psutil.AccessDenied()

    monkeypatch.setattr(resource_tracking.psutil, "cpu_freq", denied)
    monitor = resource_tracking.ResourceMonitor(tmp_path / "diagnostics", interval=60)
    monitor.start()
    summary = monitor.finish()
    rows = [
        json.loads(line)
        for line in (monitor.directory / "resources.jsonl").read_text().splitlines()
    ]
    assert all(
        row["cpu_frequency_mhz"] is None for row in rows if row["kind"] == "sample"
    )
    assert summary["measurement_errors"]["cpu_freq"] >= 1


@pytest.mark.parametrize("mode", ["execute", "dry_run"])
def test_invocation_finishes_tracking_even_on_workflow_failure(tmp_path, mode):
    path, record = invocation_history.start(
        tmp_path,
        workflow="simulate_system",
        entry_point="test",
        command=["test"],
        targets=["all"],
        mode=mode,
        contract_mode="test",
    )
    resource_tracking.phase(path, "snakemake")
    invocation_history.finish(path, record, exit_code=7)
    saved = json.loads(path.read_text())
    assert saved["exit_code"] == 7
    assert saved["status"] == "failed"
    assert path not in resource_tracking._MONITORS
    if mode == "execute":
        assert saved["resources"]["status"] == "finished"
        assert (
            Path(saved["resources"]["directory"]).joinpath("resources.jsonl").is_file()
        )
    else:
        assert "resources" not in saved


def test_tracking_failure_does_not_prevent_invocation(tmp_path, monkeypatch):
    def unavailable(*args, **kwargs):
        raise PermissionError("diagnostics denied")

    monkeypatch.setattr(resource_tracking, "ResourceMonitor", unavailable)
    with pytest.warns(UserWarning, match="resource tracking unavailable"):
        path, record = invocation_history.start(
            tmp_path,
            workflow="simulate_system",
            entry_point="test",
            command=[],
            targets=[],
            mode="execute",
            contract_mode="test",
        )
    invocation_history.finish(path, record, exit_code=0)
    assert record["status"] == "succeeded"
    assert record["resources"]["status"] == "unavailable"


def test_batch_decision_records_requested_threads_and_members(tmp_path, monkeypatch):
    monkeypatch.setenv(resource_tracking.DIRECTORY_ENV, str(tmp_path))
    resource_tracking.write_batch_decision(
        "0",
        {"plan": {"available_memory_bytes": 123}},
        threads=2,
        run_ids=["run_01", "run_02"],
    )
    (path,) = tmp_path.glob("batch-*.json")
    saved = json.loads(path.read_text())
    assert saved["plan"]["available_memory_bytes"] == 123
    assert saved["rule_requested_threads"] == 2
    assert saved["run_ids"] == ["run_01", "run_02"]
