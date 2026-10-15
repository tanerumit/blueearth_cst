"""Publication summaries describe retained estimates without changing their values."""

import io
import sys

import pytest

from blueearth_cst.experiment.console_reporting import report_metric_set
from blueearth_cst.shared.run_log_core import _compact_log_line, _Tee, log_row


@pytest.mark.parametrize("tee", [False, True])
def test_legacy_console_folds_arrows_without_corrupting_utf8_log(monkeypatch, tee):
    data = io.BytesIO()
    live = io.TextIOWrapper(data, encoding="cp1252")
    log = io.StringIO()
    stream = _Tee(live, log) if tee else live
    with monkeypatch.context() as context:
        context.setattr(sys, "stdout", stream)
        log_row("Written → sample.csv", module="metrics")
        stream.flush()
        live.flush()
    assert b"Written -> sample.csv" in data.getvalue()
    if tee:
        assert "Written → sample.csv" in log.getvalue()


def test_metric_summary_counts_actual_finite_and_missing_estimates(tmp_path, capsys):
    table = tmp_path / "indicators.csv"
    payload = "metric,location,run_group_id,value\nmean,a,run_1,1.5\nmean,b,run_1,\nmean,c,run_1,nan\nmean,d,run_1,-2\n"
    table.write_text(payload, encoding="utf-8")
    manifest = {
        "metric_set_id": "selected",
        "engine_root": "_engine/metric_sets/selected",
        "tables": [{"file": {"path": table.name}}],
    }
    report_metric_set(tmp_path, manifest)
    assert "2 finite and 2 non-finite result estimates" in capsys.readouterr().out
    assert table.read_text(encoding="utf-8") == payload


@pytest.mark.parametrize(
    "module,current,proposed",
    [
        (
            "experiment",
            "Model reference matches the live model",
            "Live model matches the recorded experiment identity",
        ),
        (
            "metrics",
            "abcdef123456: 1 declaration over 2 result keys",
            "Metric set abcdef123456 planned: 1 metric declaration; 2 expected result keys",
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
