"""Direct owned WF3 invocations are recorded at every launch outcome."""

import json

import pytest

from scripts import generate_scenarios


@pytest.mark.parametrize("exit_code", [0, 9])
def test_direct_dry_run_records_terminal_invocation(tmp_path, monkeypatch, exit_code):
    config = tmp_path / "project_config.yml"
    config.write_text("project: {}\n", encoding="utf-8")
    project = tmp_path / "project"
    observed = []

    def fake_child(command, **kwargs):
        observed.append((command, kwargs))
        return exit_code

    monkeypatch.setattr(generate_scenarios, "run_project_child", fake_child)
    assert (
        generate_scenarios.main(
            [
                "--config",
                str(config),
                "--project-dir",
                str(project),
                "--cores",
                "2",
                "--",
                "--dry-run",
            ]
        )
        == exit_code
    )
    (path,) = (project / "config/runs/_engine/invocations").glob("*.json")
    record = json.loads(path.read_text(encoding="utf-8"))
    assert record["workflow"] == "generate_scenarios"
    assert record["contract_mode"] == "new_schema"
    assert record["mode"] == "dry_run"
    assert record["status"] == ("succeeded" if exit_code == 0 else "failed")
    assert record["exit_code"] == exit_code
    assert len(observed) == 1
    assert observed[0][1]["writing"] is False


def test_direct_launch_exception_is_terminal(tmp_path, monkeypatch):
    config = tmp_path / "project_config.yml"
    config.write_text("project: {}\n", encoding="utf-8")
    project = tmp_path / "project"

    def fail_child(*_args, **_kwargs):
        raise OSError("snakemake unavailable")

    monkeypatch.setattr(generate_scenarios, "run_project_child", fail_child)
    with pytest.raises(OSError, match="snakemake unavailable"):
        generate_scenarios.main(
            [
                "--config",
                str(config),
                "--project-dir",
                str(project),
                "--cores",
                "2",
                "--",
                "--dry-run",
            ]
        )
    (path,) = (project / "config/runs/_engine/invocations").glob("*.json")
    record = json.loads(path.read_text(encoding="utf-8"))
    assert record["status"] == "failed"
    assert record["error"]["type"] == "OSError"


def test_disabled_wf3_cannot_initialize_collection(tmp_path, monkeypatch):
    config = tmp_path / "project_config.yml"
    config.write_text("project: {}\n", encoding="utf-8")
    project = tmp_path / "project"
    calls = []
    monkeypatch.setattr(
        generate_scenarios,
        "run_project_child",
        lambda command, **_kwargs: calls.append(command) or 0,
    )
    monkeypatch.setattr(
        generate_scenarios,
        "compose_config",
        lambda *_args, **_kwargs: (
            {"workflows": {"generate_scenarios": {"enabled": False}}},
            {},
        ),
    )
    with pytest.raises(ValueError, match="WF3 is disabled"):
        generate_scenarios.main(
            [
                "--config",
                str(config),
                "--project-dir",
                str(project),
                "--cores",
                "2",
            ]
        )
    assert len(calls) == 1  # source preparation only; no generation child
    assert not (project / "scenarios").exists()
