"""Tests for the per-workflow benchmark gather (src/merge_benchmarks.py)."""
import os
import sys

import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from src.merge_benchmarks import merge_benchmarks  # noqa: E402

_HEADER = "s\th:m:s\tmax_rss\tio_in\tcpu_time\tmean_load\n"


def _write(path, s, rss, io_in, cpu, load):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(_HEADER + f"{s}\t0:00:00\t{rss}\t{io_in}\t{cpu}\t{load}\n", encoding="utf-8")


def test_filters_by_workflow_prefix_and_appends_total(tmp_path):
    parts = tmp_path / "_parts"
    _write(parts / "1.03_create_model.tsv", 10.0, 100.0, 1.0, 8.0, 50.0)
    _write(parts / "1.09_run_wflow.tsv", 20.0, 200.0, 3.0, 18.0, 70.0)
    _write(parts / "2.05_other_wf.tsv", 99.0, 999.0, 9.0, 9.0, 9.0)  # must be excluded
    out = tmp_path / "wf1_benchmarks.tsv"
    merge_benchmarks(str(parts), "1", str(out))

    df = pd.read_csv(out, sep="\t")
    assert list(df["rule"]) == ["1.03_create_model", "1.09_run_wflow", "TOTAL"]
    total = df[df["rule"] == "TOTAL"].iloc[0]
    assert total["s"] == 30.0          # sum
    assert total["cpu_time"] == 26.0   # sum
    assert total["io_in"] == 4.0       # sum
    assert total["max_rss"] == 200.0   # max (peak)
    assert total["mean_load"] == 60.0  # mean


def test_nested_wildcard_parts_get_relative_rule_label(tmp_path):
    parts = tmp_path / "_parts"
    _write(parts / "2.02_monthly_stats_hist" / "INM" / "GFDL.tsv", 5.0, 50.0, 0.0, 4.0, 40.0)
    out = tmp_path / "wf2_benchmarks.tsv"
    merge_benchmarks(str(parts), "2", str(out))
    df = pd.read_csv(out, sep="\t")
    assert df.iloc[0]["rule"] == "2.02_monthly_stats_hist/INM/GFDL"


def test_no_parts_writes_header_only(tmp_path):
    out = tmp_path / "wf3_benchmarks.tsv"
    merge_benchmarks(str(tmp_path / "_parts"), "3", str(out))
    df = pd.read_csv(out, sep="\t")
    assert len(df) == 0 and "rule" in df.columns
