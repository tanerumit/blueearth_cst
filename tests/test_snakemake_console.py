"""Early console filtering must preserve diagnostics, logs and exit status."""

import io
import logging
import subprocess
import sys
from pathlib import Path

import pytest

from blueearth_cst.shared import snakemake_console as console
from blueearth_cst.shared import windows_job


@pytest.mark.parametrize("level", [logging.INFO, logging.WARNING, logging.ERROR])
def test_startup_filter_preserves_raised_severity(level):
    record = logging.LogRecord("snakemake", level, "", 0, "Provided cores: 3", (), None)
    assert console._StartupFilter().filter(record) == (level != logging.INFO)


def test_profile_notice_split_writes_and_unterminated_errors():
    output = io.StringIO()
    stream = console._ProfileStream(output)
    stream.write("Using workflow specific profile profiles/default")
    stream.write(" for setting default command line arguments.\n")
    stream.write("WARNING: profile failed\nRuntimeError: incomplete")
    stream.flush()
    assert output.getvalue() == "WARNING: profile failed\nRuntimeError: incomplete"
    stream.active = False
    notice = "Using workflow specific profile x for setting default command line arguments.\n"
    stream.write(notice)
    assert output.getvalue().endswith(notice)


@pytest.mark.parametrize(
    "command", [["snakemake", "all"], [sys.executable, "-m", "snakemake", "all"]]
)
def test_owned_launcher_routes_both_snakemake_forms(monkeypatch, command):
    calls = []
    monkeypatch.setattr(
        windows_job, "run_owned_child", lambda cmd, **kwargs: calls.append(cmd) or 7
    )
    monkeypatch.setattr(
        windows_job.subprocess,
        "run",
        lambda cmd, **kwargs: calls.append(cmd) or subprocess.CompletedProcess(cmd, 7),
    )
    assert (
        windows_job.run_project_child(command, cwd=Path.cwd(), env={}, writing=False)
        == 7
    )
    assert calls == [[sys.executable, str(Path(console.__file__)), "all"]]


@pytest.mark.process_isolation
@pytest.mark.parametrize("fail", [False, True])
def test_real_startup_preserves_log_warnings_and_failures(tmp_path, fail):
    profile = tmp_path / "profiles/default"
    profile.mkdir(parents=True)
    (profile / "config.yaml").write_text("quiet: [reason]\n", encoding="utf-8")
    (tmp_path / "Snakefile").write_text(
        "from snakemake.logging import logger\n"
        "onstart:\n"
        "    logger.warning('Provided cores: 999')\n"
        "    logger.info('workflow diagnostic visible')\n"
        + ("    raise RuntimeError('startup failure visible')\n" if fail else "")
        + "rule all:\n    shell: 'echo CHILD_OUTPUT'\n",
        encoding="utf-8",
    )
    result = subprocess.run(
        [sys.executable, console.__file__, "all", "--cores", "1"],
        cwd=tmp_path,
        text=True,
        capture_output=True,
        timeout=90,
    )
    output = result.stdout + result.stderr
    assert result.returncode == (1 if fail else 0), output
    assert "Using workflow specific profile" not in output
    assert "Building DAG of jobs..." not in output
    assert "Provided cores: 1" not in output
    assert "Provided cores: 999" in output
    assert "workflow diagnostic visible" in output
    assert ("startup failure visible" if fail else "CHILD_OUTPUT") in output
    logs = list((tmp_path / ".snakemake/log").glob("*.log"))
    assert logs
    assert "Building DAG of jobs..." in logs[0].read_text(encoding="utf-8")


@pytest.mark.parametrize("flag", ["--dry-run", "--verbose"])
def test_diagnostic_modes_keep_native_streams(monkeypatch, flag):
    from snakemake import cli

    stderr = sys.stderr
    calls = []
    monkeypatch.setattr(sys, "argv", ["snakemake", flag])
    monkeypatch.setattr(cli, "main", lambda: calls.append(sys.stderr))
    console.main()
    assert calls == [stderr]
