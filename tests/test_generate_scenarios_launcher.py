"""Direct owned WF3 invocations are recorded at every launch outcome."""

import json
import subprocess
import sys
from pathlib import Path

import pytest

from scripts import generate_scenarios


def test_source_phase_hides_console_chatter_only_on_success(capfd, monkeypatch):
    def noisy_child(_command, **_kwargs):
        # A genuine child process, not an in-process print: only a real OS-level
        # fd write proves the redirect (Python's own buffered streams do not
        # reliably observe a nested os.dup2 the way an inherited child fd does).
        subprocess.run(
            [sys.executable, "-c", "print('Using workflow specific profile ...')"],
            check=False,
        )
        return 0

    monkeypatch.setattr(generate_scenarios, "run_project_child", noisy_child)
    code = generate_scenarios._run_source_phase_quietly(
        ["snakemake", "--quiet", "all"], cwd=None, env={}
    )
    assert code == 0
    captured = capfd.readouterr()
    assert captured.out == ""
    assert captured.err == ""


def test_source_phase_never_silences_warnings_on_success(capfd, monkeypatch):
    def warning_child(_command, **_kwargs):
        subprocess.run(
            [
                sys.executable,
                "-c",
                "print('routine chatter'); print('WARNING: catalog lacks units')",
            ],
            check=False,
        )
        return 0

    monkeypatch.setattr(generate_scenarios, "run_project_child", warning_child)
    assert generate_scenarios._run_source_phase_quietly([], cwd=None, env={}) == 0
    captured = capfd.readouterr()
    assert "WARNING: catalog lacks units" in captured.err
    assert "routine chatter" not in captured.err


def test_in_process_writes_are_captured_and_errors_surface(capfd):
    with pytest.raises(RuntimeError, match="boom"):
        with generate_scenarios._captured_output():
            print("in-process chatter")
            raise RuntimeError("boom")
    assert "in-process chatter" in capfd.readouterr().err


def test_source_phase_replays_console_chatter_on_failure(capfd, monkeypatch):
    def noisy_failing_child(_command, **_kwargs):
        subprocess.run(
            [sys.executable, "-c", "print('Using workflow specific profile ...')"],
            check=False,
        )
        return 7

    monkeypatch.setattr(generate_scenarios, "run_project_child", noisy_failing_child)
    code = generate_scenarios._run_source_phase_quietly(
        ["snakemake", "--quiet", "all"], cwd=None, env={}
    )
    assert code == 7
    captured = capfd.readouterr()
    assert "Using workflow specific profile" in captured.err


def test_source_phase_replay_reaches_a_real_terminal_fd():
    """Regression: pytest's ``capfd`` masks a replay-ordering bug that a real
    console does not. ``capfd`` redirects fd 1/2 for the whole test process
    before it starts, so ``_run_source_phase_quietly``'s own nested dup2/restore
    cycle still lands its replay write on a descendant of that same pipe either
    way -- the two prior tests above pass whether the replay runs before or
    after the restore. Only a fresh, unwrapped interpreter distinguishes them:
    before the fix, the replay wrote into the already-discarded capture temp
    file instead of the real fd, so a genuine failure surfaced no diagnostic
    at all (the exact silent-exit symptom this regression guards against).
    """
    script = (
        "import subprocess, sys\n"
        "sys.path.insert(0, '.')\n"
        "from scripts import generate_scenarios\n"
        "def noisy_failing_child(_command, **_kwargs):\n"
        "    subprocess.run([sys.executable, '-c', \"print('boom')\"], check=False)\n"
        "    return 7\n"
        "generate_scenarios.run_project_child = noisy_failing_child\n"
        "code = generate_scenarios._run_source_phase_quietly(['snakemake'], cwd=None, env={})\n"
        "sys.exit(code)\n"
    )
    result = subprocess.run(
        [sys.executable, "-c", script],
        cwd=str(Path(__file__).resolve().parents[1]),
        capture_output=True,
        text=True,
    )
    assert result.returncode == 7
    assert "boom" in result.stderr


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
    assert calls[0][-2:] == ["--quiet", "all"]
    assert not (project / "scenarios").exists()
