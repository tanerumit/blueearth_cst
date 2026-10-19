"""Execution history remains attributable across retries and partial failures."""

import io
import json
import logging
import os
import re
import sys
from pathlib import Path

import pytest

from blueearth_cst.shared import execution_outputs as outputs
from blueearth_cst.shared import invocation_history
from blueearth_cst.shared.console_terminal import INTERACTIVE_ENV, terminal_environment
from blueearth_cst.shared.windows_job import _relay_chunks, run_project_child


def _start(root, **kwargs):
    return invocation_history.start(
        root,
        workflow=kwargs.pop("workflow", "build_model"),
        entry_point="test",
        command=["test"],
        targets=["all"],
        mode="execute",
        contract_mode="new_schema",
        **kwargs,
    )


def test_relay_keeps_split_unicode_and_redraws_without_doubling_newlines():
    stream = io.StringIO()
    _relay_chunks([b"caf\xc3", b"\xa9\r", b"\nwaiting\r", b"done\n"], stream)
    assert stream.getvalue() == "café\nwaiting\rdone\n"


@pytest.mark.parametrize("terminal", [False, True])
def test_terminal_detection_survives_a_nested_pipe(monkeypatch, terminal):
    class Sink(io.StringIO):
        def isatty(self):
            return terminal

    monkeypatch.delenv(INTERACTIVE_ENV, raising=False)
    monkeypatch.setattr(sys, "stdout", Sink())
    environment = terminal_environment()
    assert environment[INTERACTIVE_ENV] == ("1" if terminal else "0")
    for key, value in environment.items():
        monkeypatch.setenv(key, value)
    monkeypatch.setattr(sys, "stdout", io.StringIO())
    assert terminal_environment() == environment


@pytest.mark.parametrize("nested", [False, True])
@pytest.mark.parametrize("mode", ["terminal", "no_color", "redirected"])
def test_managed_children_keep_live_formatting_and_plain_logs(
    tmp_path, capsys, monkeypatch, nested, mode
):
    monkeypatch.setenv(INTERACTIVE_ENV, "0" if mode == "redirected" else "1")
    monkeypatch.setenv("COLUMNS", "117")
    if mode == "no_color":
        monkeypatch.setenv("NO_COLOR", "1")
    else:
        monkeypatch.delenv("NO_COLOR", raising=False)
    repo = str(Path(__file__).resolve().parents[1])
    code = (
        "import sys, logging; "
        "logger=logging.getLogger('probe'); "
        "logger.addHandler(logging.StreamHandler(sys.stderr)); "
        f"sys.path.insert(0, {repo!r}); "
        "from blueearth_cst.shared.run_log_core import tee_to_log; "
        "from blueearth_cst.shared.console_terminal import terminal_environment; "
        "print('columns=' + terminal_environment().get('COLUMNS', 'plain')); "
        "exec(\"with tee_to_log('rule.log'):\\n"
        "    logger.warning('12:00:00 - probe - WARNING - warmup')\\n"
        "    sys.stdout.write_redraw('\\\\rprogress 1')\\n"
        "    sys.stdout.write_redraw('\\\\rprogress 2')\\n"
        "    sys.stdout.write_redraw('\\\\n')\")"
    )
    if nested:
        code = (
            f"import os, sys; sys.path.insert(0, {repo!r}); from pathlib import Path; "
            "from blueearth_cst.shared.windows_job import run_project_child; "
            f"sys.exit(run_project_child([sys.executable, '-c', {code!r}], "
            "cwd=Path.cwd(), env=os.environ, writing=False))"
        )

    @outputs.capture_launch
    def launch():
        path, record = _start(tmp_path)
        result = run_project_child(
            [sys.executable, "-c", code],
            cwd=tmp_path,
            env={**os.environ, **outputs.environment(path, record)},
            writing=False,
        )
        assert result == 0
        return tmp_path / record["execution_directory"]

    directory = launch()
    live = capsys.readouterr().out
    transcript = (directory / "console.log").read_text(encoding="utf-8")
    rule = (tmp_path / "rule.log").read_text(encoding="utf-8")
    assert bool(re.search(r"\x1b\[[0-9;]*m", live)) == (mode == "terminal")
    assert ("progress 1" in live) == (mode != "redirected")
    if mode != "redirected":
        assert "columns=117" in live
    assert "progress 2" in transcript and "warmup" in transcript
    assert "progress 1" not in transcript
    assert "\x1b" not in transcript and "\r" not in transcript
    assert "WARNING - warmup" in rule and "\x1b" not in rule


def test_retry_directories_and_child_parts_are_isolated(tmp_path, monkeypatch):
    monkeypatch.setattr(invocation_history, "_now", lambda: "2026-10-19T12:00:00Z")
    first, parent = _start(tmp_path, workflow=None)
    assert parent["execution_directory"].startswith("logs/20261019T120000Z-")
    child_path, child = _start(tmp_path, parent_invocation_id=parent["invocation_id"])
    second, retry = _start(tmp_path, workflow=None)
    assert child["execution_directory"] == parent["execution_directory"]
    assert retry["execution_directory"] != parent["execution_directory"]
    for key, value in outputs.environment(child_path, child).items():
        monkeypatch.setenv(key, value)
    paths = outputs.workflow_paths(
        tmp_path, "wf1", "legacy.log", "legacy.md", "logs", "benchmarks"
    )
    assert Path(paths.log).parent == tmp_path / parent["execution_directory"]
    assert Path(paths.log).name == "wf1.log"
    assert child["invocation_id"] in paths.log_parts
    assert "_parts" in paths.benchmark_parts
    assert first != child_path != second


@pytest.mark.parametrize("nested", [False, True])
def test_transcript_streams_child_stdout_stderr_and_keeps_only_final_redraw(
    tmp_path, capsys, nested
):
    logger = logging.getLogger("test.execution_transcript")
    handler = logging.StreamHandler(sys.stderr)
    logger.addHandler(handler)
    original_stream = handler.stream
    streams = []

    @outputs.capture_launch
    def launch():
        path, record = _start(tmp_path)
        print("launcher start")
        streams.append(sys.stdout)
        logger.warning("bound console handler")
        code = (
            "import sys; print('child café'); print('child warning', file=sys.stderr)"
        )
        if nested:
            repo = str(Path(__file__).resolve().parents[1])
            code = (
                f"import os, sys; sys.path.insert(0, {repo!r}); from pathlib import Path; "
                "from blueearth_cst.shared.windows_job import run_project_child; "
                f"sys.exit(run_project_child([sys.executable, '-c', {code!r}], "
                "cwd=Path.cwd(), env=os.environ, writing=False))"
            )
        result = run_project_child(
            [sys.executable, "-c", code],
            cwd=tmp_path,
            env={**os.environ, **outputs.environment(path, record)},
            writing=False,
        )
        sys.stdout.write("\x1b[32mworking 1\rworking 2\rcomplete\x1b[0m\n")
        invocation_history.finish(path, record, exit_code=result)
        print("launcher end")
        return tmp_path / record["execution_directory"]

    try:
        directory = launch()
        assert handler.stream is original_stream
        # A handler created during execution can retain this proxy afterwards.
        streams[0].write("after capture\n")
    finally:
        logger.removeHandler(handler)
    transcript = (directory / "console.log").read_text(encoding="utf-8")
    assert "launcher start" in transcript and "launcher end" in transcript
    assert "child café\nchild warning\n" in transcript
    assert "bound console handler" in transcript
    assert "after capture" not in transcript
    assert "complete\n" in transcript
    assert "working 1" not in transcript and "\x1b" not in transcript
    assert "child café\nchild warning\n" in capsys.readouterr().out
    assert sys.stdout is not None


def test_failure_merges_only_owned_parts_and_preserves_them(tmp_path):
    path, record = _start(tmp_path)
    directory = tmp_path / record["execution_directory"]
    parts = directory / "_parts" / f"wf1-{record['invocation_id']}"
    log = parts / "logs/1.01_delineate_region.log"
    log.parent.mkdir(parents=True)
    log.write_text("12:00:00 - test - failure detail\n", encoding="utf-8")
    benchmark = parts / "benchmarks/1.01_delineate_region.tsv"
    benchmark.parent.mkdir()
    benchmark.write_text("s\tmax_rss\tcpu_time\n2.5\t100\t1\n", encoding="utf-8")
    stale = tmp_path / "logs/_parts/1.01_delineate_region.log"
    stale.parent.mkdir(parents=True)
    stale.write_text("previous attempt", encoding="utf-8")
    invocation_history.finish(path, record, exit_code=7)
    assert "failure detail" in (directory / "wf1.log").read_text()
    assert "previous attempt" not in (directory / "wf1.log").read_text()
    assert log.is_file() and benchmark.is_file() and stale.is_file()
    assert (directory / "wf1-benchmarks.tsv").is_file()
    assert "failed" in (directory / "wf1-benchmarks.md").read_text()
    assert json.loads(path.read_text())["artifacts"]


def test_unowned_parse_keeps_legacy_paths_and_rejects_foreign_execution(
    tmp_path, monkeypatch
):
    monkeypatch.delenv(outputs.DIRECTORY_ENV, raising=False)
    paths = outputs.workflow_paths(
        tmp_path, "wf0", "old.log", "old.md", "parts", "benchparts"
    )
    assert paths.log == f"{tmp_path}/logs/old.log"
    monkeypatch.setenv(outputs.DIRECTORY_ENV, str(tmp_path.parent / "other/logs/run"))
    with pytest.raises(ValueError, match="another project"):
        outputs.workflow_paths(
            tmp_path, "wf0", "old.log", "old.md", "parts", "benchparts"
        )
