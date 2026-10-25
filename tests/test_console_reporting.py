"""Publication summaries describe retained estimates without changing their values."""

import io
import logging
import sys
from dataclasses import replace
from logging.handlers import QueueHandler, QueueListener
from queue import Queue

import pytest

from blueearth_cst.experiment import indicator_sets
from blueearth_cst.experiment.console_reporting import (
    _PlanStream,
    matching_sets,
    record_indicator_detail,
    report_indicator_set,
    result_counts,
)
from blueearth_cst.experiment.indicator_export import report_publication
from blueearth_cst.shared.run_log_core import _compact_log_line, _Tee, log_row


@pytest.mark.parametrize("tee", [False, True])
def test_legacy_console_folds_arrows_without_corrupting_utf8_log(monkeypatch, tee):
    data = io.BytesIO()
    live = io.TextIOWrapper(data, encoding="cp1252")
    log = io.StringIO()
    stream = _Tee(live, log) if tee else live
    with monkeypatch.context() as context:
        context.setattr(sys, "stdout", stream)
        log_row("Written → sample.csv", module="indicators")
        stream.flush()
        live.flush()
    assert b"Written -> sample.csv" in data.getvalue()
    if tee:
        assert "Written → sample.csv" in log.getvalue()


def test_indicator_details_survive_queued_cp1252_logging(
    tmp_path, monkeypatch, capsys, caplog
):
    """Snakemake's asynchronous file logger may use the Windows code page."""
    native_log = tmp_path / "snakemake.log"
    handler = logging.FileHandler(native_log, encoding="cp1252")
    queue = Queue()
    listener = QueueListener(queue, handler)
    logger = logging.getLogger("snakemake.logging")
    monkeypatch.setattr(logger, "handlers", [QueueHandler(queue)])
    # Use setLevel (through caplog) to clear decisions cached by earlier tests.
    caplog.set_level(logging.INFO, logger="snakemake.logging")
    monkeypatch.setattr(logger, "propagate", False)
    message = "Indicator set abc; manifest → C:/cases/café/水/indicators.json"
    listener.start()
    try:
        record_indicator_detail(tmp_path, message)
        report_indicator_set(
            tmp_path, {"indicator_set_id": "abc", "engine_root": "_engine/sets"}
        )
    finally:
        listener.stop()
        handler.close()
    captured = capsys.readouterr()
    assert "Logging error" not in captured.err
    assert "UnicodeEncodeError" not in captured.err
    assert r"\u2192" in native_log.read_text(encoding="cp1252")
    assert r"\u6c34" in native_log.read_text(encoding="cp1252")
    assert message in (tmp_path / "logs/wf4_indicators.log").read_text(encoding="utf-8")


def test_unwritable_detail_log_uses_encoding_safe_console_fallback(
    tmp_path, monkeypatch
):
    (tmp_path / "logs").write_text("blocks log directory", encoding="utf-8")
    data = io.BytesIO()
    live = io.TextIOWrapper(data, encoding="cp1252")
    with monkeypatch.context() as context:
        context.setattr(sys, "stdout", live)
        record_indicator_detail(tmp_path, "Manifest → café/水/indicators.json")
        live.flush()
    assert b"Indicator details: Manifest -> caf\xe9/" in data.getvalue()


def test_indicator_summary_counts_actual_finite_and_missing_estimates(tmp_path, capsys):
    table = tmp_path / "indicators.csv"
    payload = "indicator,location,run_group_id,value\nmean,a,run_1,1.5\nmean,b,run_1,\nmean,c,run_1,nan\nmean,d,run_1,-2\n"
    table.write_text(payload, encoding="utf-8")
    manifest = {
        "indicator_set_id": "selected",
        "engine_root": "_engine/indicator_sets/selected",
        "tables": [{"file": {"path": table.name}}],
    }
    assert result_counts(tmp_path, manifest) == (2, 2, 0)
    assert table.read_text(encoding="utf-8") == payload


def test_shared_calculations_keep_both_set_names_and_report_reuse(tmp_path, capsys):
    source = indicator_sets.legacy_selection({"operation": "indicators-only"}).sets[0]
    default = indicator_sets.resolve_set(source, ["gwr"])
    alias = replace(default, set_id="same_numbers")
    records = indicator_sets.calculation_records(default.indicators)
    sets = [default, alias]
    assert matching_sets(sets, {"calculations": records}) == sets
    manifest = {
        "indicator_set_id": "opaque",
        "engine_root": "_engine/indicators",
        "calculations": records,
    }
    report_indicator_set(tmp_path, manifest, sets, reused=True)
    output = capsys.readouterr().out
    assert "default: reusing calculated results" in output
    assert "same_numbers: reusing calculated results" in output
    assert "opaque" not in output


@pytest.mark.parametrize("producer", [False, True])
def test_planning_stream_keeps_warnings_and_detailed_log(
    caplog, tmp_path, monkeypatch, producer
):
    monkeypatch.setattr(
        logging.getLogger("snakemake.logging"), "handlers", [caplog.handler]
    )
    stream = io.StringIO()
    proxy = _PlanStream(stream, tmp_path)
    detail = "12:00:00 - indicators - Indicator set abc planned: 12 indicator declarations; 896 expected result keys\n"
    with caplog.at_level("INFO", logger="snakemake.logging"):
        if producer:
            monkeypatch.setattr(sys, "stdout", proxy)
            log_row("abc: 12 declarations over 896 result keys", module="indicators")
        else:
            proxy.write(detail)
        proxy.write("12:00:00 - indicators - WARNING - input coverage incomplete\n")
    assert "896 expected result keys" in caplog.text
    assert "896 expected result keys" in (
        tmp_path / "logs/wf4_indicators.log"
    ).read_text(encoding="utf-8")
    assert (
        stream.getvalue()
        == "12:00:00 - indicators - WARNING - input coverage incomplete\n"
    )


def test_publication_reports_saved_reused_missing_and_failed_results(
    tmp_path, capsys, monkeypatch, caplog
):
    console = io.StringIO()
    monkeypatch.setattr(
        logging.getLogger(), "handlers", [logging.StreamHandler(console)]
    )
    logger = logging.getLogger("snakemake.logging")
    monkeypatch.setattr(logger, "handlers", [])
    monkeypatch.setattr(logger, "propagate", True)
    caplog.set_level(logging.INFO, logger="snakemake.logging")
    outcomes = [
        {
            "set_id": "default",
            "status": "current",
            "indicator_set_id": "hidden1",
            "publication_id": "hidden2",
            "missing_results": 2,
            "available_results": 4,
        },
        {
            "set_id": "flow_regime",
            "status": "current",
            "indicator_set_id": "hidden3",
            "publication_id": "hidden4",
            "reused": True,
        },
        {
            "set_id": "failed_set",
            "status": "failed",
            "prior_publication_id": "hidden5",
            "reason": "MissingInput: daily discharge unavailable",
        },
        {
            "set_id": "new_set",
            "status": "failed",
            "prior_publication_id": None,
            "reason": "MissingInput: recharge unavailable",
        },
    ]
    assert report_publication(tmp_path, outcomes) is False
    output = capsys.readouterr().out
    assert "default: results saved" in output
    assert "2 results missing or invalid; 4 results available" in output
    assert "flow_regime: results unchanged; reusing saved results" in output
    assert "previous results kept; they have not been updated" in output
    assert "no saved results available" in output
    assert "daily discharge unavailable" in output
    assert "hidden" not in output
    assert console.getvalue() == ""
    assert "hidden1" in (tmp_path / "logs/wf4_indicators.log").read_text(
        encoding="utf-8"
    )


@pytest.mark.parametrize(
    "module,current,proposed",
    [
        (
            "experiment",
            "Model reference matches the live model",
            "Live model matches the recorded experiment identity",
        ),
        (
            "indicators",
            "abcdef123456: 1 declaration over 2 result keys",
            "Indicator set abcdef123456 planned: 1 indicator declaration; 2 expected result keys",
        ),
        (
            "responses",
            "Duplicate series on one model point, kept once: Q_2 as Q_1",
            "Duplicate series at the same model location will be used once: Q_2 as Q_1",
        ),
        (
            "wflow",
            "FAILED [2/3] Run run_002 batch=0  Missing native output",
            "FAILED run run_002 in batch 0 [2/3]: Missing native output",
        ),
    ],
)
def test_simulation_presentation_keeps_identity_and_failure_detail(
    module, current, proposed
):
    assert (
        _compact_log_line(f"12:34:56 - {module} - {current}\n")
        == f"12:34:56 - {module} - {proposed}\n"
    )
