"""Merge a workflow's per-rule Snakemake benchmark TSVs into one file + TOTAL row.

Snakemake writes one benchmark TSV per rule (per job) under
``benchmarks/_parts/<W.NN_rule>[/…].tsv``. This gather step (one job per
workflow) collects that workflow's parts into a single
``benchmarks/wf<W>_benchmarks.tsv``, adds a ``rule`` column, and appends a
``TOTAL`` row, regenerated fresh each run. All three workflows share one
``benchmarks/_parts`` dir, so parts are filtered by the ``W.`` numbering prefix.
"""
import glob
import os

import pandas as pd

# How the TOTAL row aggregates each Snakemake benchmark column.
_SUM = ["s", "io_in", "io_out", "cpu_time"]          # additive across jobs
_MAX = ["max_rss", "max_vms", "max_uss", "max_pss"]  # peak across jobs
_MEAN = ["mean_load"]                                # average across jobs


def _hms(seconds):
    seconds = int(round(seconds))
    return f"{seconds // 3600}:{(seconds % 3600) // 60:02d}:{seconds % 60:02d}"


def merge_benchmarks(parts_dir, workflow_num, out_path):
    """Concatenate workflow ``workflow_num``'s benchmark parts + a TOTAL row."""
    prefix = f"{workflow_num}."
    tsvs = sorted(
        p
        for p in glob.glob(os.path.join(parts_dir, "**", "*.tsv"), recursive=True)
        if os.path.relpath(p, parts_dir).replace("\\", "/").split("/")[0].startswith(prefix)
    )
    parent = os.path.dirname(out_path)
    if parent:
        os.makedirs(parent, exist_ok=True)

    frames = []
    for path in tsvs:
        rule = os.path.splitext(os.path.relpath(path, parts_dir))[0].replace("\\", "/")
        df = pd.read_csv(path, sep="\t")
        df.insert(0, "rule", rule)
        frames.append(df)

    if not frames:  # no parts (e.g. nothing ran) — write just a header
        pd.DataFrame(columns=["rule", "s", "h:m:s"]).to_csv(out_path, sep="\t", index=False)
        return

    merged = pd.concat(frames, ignore_index=True)
    total = {"rule": "TOTAL"}
    for col in _SUM:
        if col in merged:
            total[col] = round(merged[col].sum(skipna=True), 4)
    for col in _MAX:
        if col in merged:
            total[col] = merged[col].max(skipna=True)
    for col in _MEAN:
        if col in merged:
            total[col] = round(merged[col].mean(skipna=True), 4)
    if "s" in total and "h:m:s" in merged.columns:
        total["h:m:s"] = _hms(total["s"])

    merged = pd.concat([merged, pd.DataFrame([total])], ignore_index=True)
    merged.to_csv(out_path, sep="\t", index=False)


if __name__ == "__main__":
    if "snakemake" in globals():
        sm = globals()["snakemake"]
        merge_benchmarks(sm.params.parts_dir, str(sm.params.workflow_num), sm.output[0])
