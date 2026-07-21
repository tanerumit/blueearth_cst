"""Tests for the per-workflow benchmark gather (src/merge_benchmarks.py).

The merged output is a Markdown table (per-rule parts stay TSV = Snakemake's
fixed benchmark format).
"""
import os
import sys

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
    out = tmp_path / "wf1_benchmarks.md"
    merge_benchmarks(str(parts), "1", str(out))

    md = out.read_text(encoding="utf-8")
    assert md.startswith("# wf1 benchmarks")
    assert "| rule" in md  # a Markdown table
    assert "1.03_create_model" in md and "1.09_run_wflow" in md
    assert "2.05_other_wf" not in md  # WF2 excluded
    # the TOTAL row carries the right aggregations (sum s/io/cpu, max mem, mean load)
    total_line = next(ln for ln in md.splitlines() if "TOTAL" in ln)
    for value in ("30.00", "26.00", "4.00", "200.00", "60.00"):
        assert value in total_line


def test_nested_wildcard_parts_get_relative_rule_label(tmp_path):
    parts = tmp_path / "_parts"
    _write(parts / "2.02_monthly_stats_hist" / "INM" / "GFDL.tsv", 5.0, 50.0, 0.0, 4.0, 40.0)
    out = tmp_path / "wf2_benchmarks.md"
    merge_benchmarks(str(parts), "2", str(out))
    assert "2.02_monthly_stats_hist/INM/GFDL" in out.read_text(encoding="utf-8")


def test_no_parts_writes_placeholder(tmp_path):
    out = tmp_path / "wf3_benchmarks.md"
    merge_benchmarks(str(tmp_path / "_parts"), "3", str(out))
    md = out.read_text(encoding="utf-8")
    assert md.startswith("# wf3 benchmarks")
    assert "no benchmark parts found" in md
