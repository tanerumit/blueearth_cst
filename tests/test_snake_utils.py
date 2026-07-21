"""Exact-equivalence tests for the shared get_config helper (R3 §3, §8).

Pins the semantics the four inline get_config copies (three Snakefiles +
conftest) had before they were collapsed into src/snake_utils.py, so the move
is provably identity-preserving rather than merely green on a smoke test.
"""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.snake_utils import (  # noqa: E402
    _compact_log_line,
    get_config,
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
    # a `.../<project>/logs/<rule>.log` path yields a header naming the project
    # and the rule-log id; the date lives here (dropped from each row).
    log = tmp_path / "gabon" / "logs" / "1.07_setup_runtime.log"
    with tee_to_log(log):
        print("body line")
    head = log.read_text(encoding="utf-8").splitlines()
    assert head[0].startswith("# BlueEarth-CST")
    assert "project: gabon" in head[0]
    assert "1.07_setup_runtime.log" in head[1] and "started" in head[1]
    assert "body line" in "\n".join(head)


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
