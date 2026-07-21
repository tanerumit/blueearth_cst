"""Tests for the portable tee wrapper (t260721a).

The contract that matters: the wrapper returns the *child's* exit code (a bare
``| tee`` returns tee's, masking failures on cmd.exe) and mirrors the child's
output into the log file. Child commands are ``python -c`` snippets so the tests
are OS-independent and need no hydromt/julia.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from src.snake_utils import run_and_tee
from src.run_logged import main


def test_run_and_tee_returns_child_exit_code(tmp_path):
    log = tmp_path / "fail.log"
    rc = run_and_tee(
        [sys.executable, "-c", "import sys; print('boom'); sys.exit(3)"], log
    )
    assert rc == 3  # the child's code, NOT tee's 0
    assert "boom" in log.read_text(encoding="utf-8")


def test_run_and_tee_success_writes_log(tmp_path):
    log = tmp_path / "ok.log"
    rc = run_and_tee([sys.executable, "-c", "print('hello world')"], log)
    assert rc == 0
    assert "hello world" in log.read_text(encoding="utf-8")


def test_run_and_tee_merges_stderr(tmp_path):
    log = tmp_path / "err.log"
    rc = run_and_tee(
        [sys.executable, "-c", "import sys; sys.stderr.write('to-stderr\\n')"], log
    )
    assert rc == 0
    assert "to-stderr" in log.read_text(encoding="utf-8")


def test_run_and_tee_creates_parent_dirs(tmp_path):
    log = tmp_path / "nested" / "deep" / "run.log"
    rc = run_and_tee([sys.executable, "-c", "print('ok')"], log)
    assert rc == 0
    assert log.exists()


def test_cli_requires_separator():
    assert main(["only-a-log.log"]) == 2


def test_cli_rejects_missing_command(tmp_path):
    assert main([str(tmp_path / "l.log"), "--"]) == 2


def test_cli_runs_command_and_returns_code(tmp_path):
    log = tmp_path / "cli.log"
    rc = main([str(log), "--", sys.executable, "-c", "import sys; sys.exit(5)"])
    assert rc == 5
