"""Exact-equivalence tests for the shared get_config helper (R3 §3, §8).

Pins the semantics the four inline get_config copies (three Snakefiles +
conftest) had before they were collapsed into src/snake_utils.py, so the move
is provably identity-preserving rather than merely green on a smoke test.
"""

import os
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import re

from src.snake_utils import (  # noqa: E402
    _compact_log_line,
    _cr_overwrite,
    _log_path_parts,
    _relativize_paths,
    get_config,
    log_row,
    patch_psutil_windows_benchmark,
    rule_banner,
    save_figure,
    tee_to_log,
)


def test_missing_required_raises():
    with pytest.raises(ValueError):
        get_config({}, "absent", optional=False)


def test_missing_optional_returns_none_by_default():
    assert get_config({}, "absent") is None


def test_missing_optional_returns_explicit_default():
    assert get_config({}, "absent", default="fallback") == "fallback"


def test_present_key_returned():
    assert get_config({"k": 42}, "k") == 42


def test_present_required_key_returned():
    assert get_config({"k": "v"}, "k", optional=False) == "v"


def test_none_value_returned_not_treated_as_missing():
    # A key explicitly set to None returns None, not the default — the key IS
    # present. This is the subtle semantic the inline copies all shared.
    assert get_config({"k": None}, "k", default="fallback") is None


@pytest.mark.parametrize("falsey", [0, "", False, []])
def test_falsey_values_returned_as_is(falsey):
    result = get_config({"k": falsey}, "k", default="fallback")
    assert result == falsey and type(result) is type(falsey)


# --- _compact_log_line (hydromt format) --------------------------------------


def test_compact_shortens_timestamp_and_drops_dotted_name():
    line = (
        "2026-07-21 18:03:38,474 - hydromt.model.model - model - INFO - "
        "Initializing wflow_sbm model.\n"
    )
    # date + milliseconds dropped -> HH:MM:SS; dotted name dropped; module kept
    assert _compact_log_line(line) == (
        "18:03:38 - model - INFO - Initializing wflow_sbm model.\n"
    )


def test_compact_preserves_dashes_in_message():
    line = (
        "2026-07-21 18:03:20,505 - hydromt.model.model - model - INFO - "
        "setup_rivers.river_routing=kinematic - wave - x\n"
    )
    # message (with its own ' - ') is kept whole; only ts + dotted name change
    assert _compact_log_line(line) == (
        "18:03:20 - model - INFO - setup_rivers.river_routing=kinematic - wave - x\n"
    )


def test_compact_keeps_level_and_no_trailing_newline():
    line = (
        "2026-07-21 18:03:18,884 - hydromt.hydromt_wflow.workflows.basemaps"
        " - basemaps - WARNING - Model resolution mismatch"
    )  # no trailing newline
    assert _compact_log_line(line) == (
        "18:03:18 - basemaps - WARNING - Model resolution mismatch"
    )


@pytest.mark.parametrize(
    "line",
    [
        "[ Info: Wflow version v1.0.2\n",  # Julia log, no timestamp
        "Traceback (most recent call last):\n",  # traceback
        "just a plain print line\n",
        "",  # empty
    ],
)
def test_compact_passes_through_non_hydromt(line):
    assert _compact_log_line(line) == line


# --- save_figure -------------------------------------------------------------


def test_save_figure_writes_creates_parent_and_announces(tmp_path, capsys):
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    out = tmp_path / "plots" / "basin_area.png"  # parent does not exist yet
    plt.figure()
    plt.plot([0, 1], [0, 1])
    save_figure(str(out), dpi=50)
    assert out.exists()
    assert f"Saved figure: {out}" in capsys.readouterr().out


# --- log_row -----------------------------------------------------------------


def test_log_row_standard_format(capsys):
    log_row("hello world", module="plot")
    out = capsys.readouterr().out.strip()
    assert re.match(r"^\d{2}:\d{2}:\d{2} - plot - INFO - hello world$", out)


def test_log_row_row_survives_compaction_unchanged():
    # a log_row line is already compact -> the tee's _compact_log_line is a no-op
    row = "21:56:12 - plot - INFO - Saved figure: x.png\n"
    assert _compact_log_line(row) == row


# --- psutil benchmark shim ---------------------------------------------------


def test_patch_psutil_exposes_pss():
    # Snakemake's benchmark sampler reads meminfo.pss; on Windows psutil omits it
    # (only uss), which NAs every metric. The shim must expose pss (= uss proxy).
    if sys.platform != "win32":
        import pytest as _pytest

        _pytest.skip("Windows-only shim")
    import psutil

    patch_psutil_windows_benchmark()
    meminfo = psutil.Process().memory_full_info()
    assert hasattr(meminfo, "pss")
    assert meminfo.pss == meminfo.uss  # Windows proxy


# --- rule_banner (console header) --------------------------------------------


class _FakeTTY:
    def isatty(self):
        return True


def test_rule_banner_bold_on_tty(monkeypatch):
    monkeypatch.setattr(sys, "stderr", _FakeTTY())
    monkeypatch.delenv("NO_COLOR", raising=False)
    assert rule_banner("1.09", "run_wflow") == "\033[1;36m1.09  run_wflow\033[0m"


def test_rule_banner_plain_when_not_tty(monkeypatch):
    import io

    monkeypatch.setattr(sys, "stderr", io.StringIO())  # isatty() -> False
    monkeypatch.delenv("NO_COLOR", raising=False)
    out = rule_banner("1.09", "run_wflow")
    assert out == "1.09  run_wflow" and "\033" not in out  # no escape codes


def test_rule_banner_respects_no_color_env(monkeypatch):
    monkeypatch.setattr(sys, "stderr", _FakeTTY())
    monkeypatch.setenv("NO_COLOR", "1")
    assert rule_banner("2.04", "monthly_change") == "2.04  monthly_change"


# --- path relativization -----------------------------------------------------


def test_log_path_parts_project_root_and_id(tmp_path):
    lp = tmp_path / "gabon" / "logs" / "1.03_create_model.log"
    root, log_id = _log_path_parts(str(lp))
    assert root == os.path.normpath(str(tmp_path / "gabon"))
    assert log_id == "1.03_create_model.log"
    # wildcard sub-log: project root unchanged, id is the path below logs/
    lp2 = tmp_path / "gabon" / "logs" / "3.10_run_wflow" / "rlz_1_cst_1.log"
    root2, log_id2 = _log_path_parts(str(lp2))
    assert root2 == os.path.normpath(str(tmp_path / "gabon"))
    assert log_id2 == "3.10_run_wflow/rlz_1_cst_1.log"


def test_relativize_strips_project_root_both_separators():
    root = os.path.normpath("C:/TESTS/gabon")
    native = f"Writing geoms to {root}{os.sep}hydrology_model{os.sep}basins.geojson.\n"
    assert _relativize_paths(native, root) == (
        f"Writing geoms to hydrology_model{os.sep}basins.geojson.\n"
    )
    fwd_root = root.replace(os.sep, "/")
    forward = f"Writing config to {fwd_root}/hydrology_model/wflow_sbm.toml.\n"
    assert _relativize_paths(forward, root) == (
        "Writing config to hydrology_model/wflow_sbm.toml.\n"
    )


def test_relativize_leaves_out_of_project_paths_absolute():
    root = os.path.normpath("C:/TESTS/gabon")
    line = f"Reading data from {os.path.normpath('C:/data/wflow_global/x.tif')}\n"
    assert _relativize_paths(line, root) == line  # not under project -> untouched


def test_tee_to_log_relativizes_project_paths(tmp_path):
    proj = tmp_path / "gabon"
    log = proj / "logs" / "1.10_plot_results.log"
    abs_png = os.path.join(str(proj), "plots", "map.png")
    with tee_to_log(log):
        print(f"Saved figure: {abs_png}")
    text = log.read_text(encoding="utf-8")
    assert "Saved figure: " + os.path.join("plots", "map.png") in text
    assert abs_png not in text  # absolute project path relativized away


# --- tee_to_log (R3 §6) ------------------------------------------------------


def test_tee_to_log_writes_and_restores_streams(tmp_path):
    log = tmp_path / "sub" / "rule.log"  # parent does not exist yet
    out0, err0 = sys.stdout, sys.stderr
    with tee_to_log(log):
        print("hello-stdout")
        print("hello-stderr", file=sys.stderr)
    # streams restored to exactly what they were on entry
    assert sys.stdout is out0 and sys.stderr is err0
    text = log.read_text(encoding="utf-8")
    assert "hello-stdout" in text and "hello-stderr" in text


def test_tee_to_log_compacts_hydromt_format(tmp_path):
    log = tmp_path / "rule.log"
    with tee_to_log(log):
        # a hydromt-format record (as hydromt's Python API emits) and a plain line
        print(
            "2026-07-21 18:03:38,474 - hydromt.model.model - model - INFO - built"
        )
        print("plain progress line")
    text = log.read_text(encoding="utf-8")
    # the record row is exactly the compacted form: HH:MM:SS, no date/ms/name
    row = next(l for l in text.splitlines() if "INFO - built" in l)
    assert row == "18:03:38 - model - INFO - built"
    assert "hydromt.model.model" not in text  # dotted name dropped
    assert "plain progress line" in text  # non-hydromt line untouched


def test_tee_to_log_writes_project_header(tmp_path):
    # a `.../<project>/logs/<rule>.log` path yields a header naming the project,
    # the full project dir, and the rule-log id; the date lives here (dropped
    # from each row), followed by a blank line before the body.
    log = tmp_path / "gabon" / "logs" / "1.07_setup_runtime.log"
    with tee_to_log(log):
        print("body line")
    head = log.read_text(encoding="utf-8").splitlines()
    assert head[0].startswith("# BlueEarth-CST")
    assert "project: gabon" in head[0]
    assert head[1].startswith("# project dir:") and head[1].rstrip().endswith("gabon")
    assert "1.07_setup_runtime.log" in head[2] and "started" in head[2]
    assert head[3] == ""  # blank line separates header from body
    assert head[4] == "body line"


def test_tee_to_log_reraises_and_still_restores(tmp_path):
    log = tmp_path / "rule.log"
    out0, err0 = sys.stdout, sys.stderr
    with pytest.raises(RuntimeError, match="boom"):
        with tee_to_log(log):
            print("before-error")
            raise RuntimeError("boom")
    # exception propagated (not swallowed) AND streams restored in finally
    assert sys.stdout is out0 and sys.stderr is err0
    assert "before-error" in log.read_text(encoding="utf-8")


# --- carriage-return progress-bar collapse -----------------------------------


@pytest.mark.parametrize(
    "line, expected",
    [
        ("plain line", "plain line"),  # no CR: untouched
        ("\r[## ] 10%\r[####] 20%", "[####] 20%"),  # keep last redraw
        # dask ends a redrawn line with a bare CR before the newline; the empty
        # trailing segment must be dropped, not kept (else the bar blanks out).
        ("\r[#] 0%\r[####] 100% Completed | 7.08 s\r", "[####] 100% Completed | 7.08 s"),
        ("\r", ""),  # only a bare CR -> nothing visible
    ],
)
def test_cr_overwrite_keeps_last_nonempty_segment(line, expected):
    assert _cr_overwrite(line) == expected


def test_tee_to_log_collapses_progress_bar_to_final_line(tmp_path):
    log = tmp_path / "rule.log"
    with tee_to_log(log):
        # mimic dask's ProgressBar: many \r-redraws written as separate chunks,
        # the last ending "\r\n" (a bare \r right before the newline).
        for pct in (0, 42, 100):
            done = "#" * (pct // 10)
            state = "Completed" if pct == 100 else "In progress"
            sys.stdout.write(f"\r[{done:<10}] | {pct}% {state} | 7.08 s")
        sys.stdout.write("\r\n")
    body = [ln for ln in log.read_text(encoding="utf-8").splitlines() if "%" in ln]
    # exactly one progress line survives, and it is the final 100% redraw
    assert len(body) == 1
    assert "100% Completed" in body[0]
    # no intermediate redraw ("In progress" / "42%") leaked into the log
    assert "In progress" not in log.read_text(encoding="utf-8")
    assert "42%" not in body[0]


def test_tee_to_log_close_flushes_interrupted_bar(tmp_path):
    # a bar cut short (no final newline) must still land its last state in the log
    log = tmp_path / "rule.log"
    with tee_to_log(log):
        sys.stdout.write("\r[## ] 50% In progress")  # no trailing newline
    assert "50% In progress" in log.read_text(encoding="utf-8")
