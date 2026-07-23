"""Concatenate per-model rule logs into one merged log (WF2 gather step).

Workflow-2 rules run one job per ``{model}[/scenario/horizon]`` for parallel
safety, each writing its own part log under ``logs/_parts/<rule>/``. This gather
step (one job per rule) concatenates those parts into a single
``logs/<rule>.log``, regenerated fresh each run. Each part keeps its own header
(whose ``log:`` id names the model), so the merged file reads as clearly
delimited per-model sections.
"""
import os


def merge_logs(part_paths, out_path):
    """Write ``out_path`` as the concatenation of ``part_paths`` (in order).

    A short marker line heads the file; a missing part (should not happen once
    its job's output exists) is noted rather than silently skipped.
    """
    parent = os.path.dirname(out_path)
    if parent:
        os.makedirs(parent, exist_ok=True)
    name = os.path.splitext(os.path.basename(out_path))[0]
    with open(out_path, "w", encoding="utf-8") as out:
        out.write(f"# merged log: {name} ({len(part_paths)} per-model parts)\n\n")
        for part in part_paths:
            if os.path.exists(part):
                with open(part, encoding="utf-8", errors="replace") as f:
                    out.write(f.read())
            else:
                label = os.path.splitext(os.path.basename(part))[0]
                out.write(f"# (no log produced for {label})\n")
            out.write("\n")


if __name__ == "__main__":
    if "snakemake" in globals():
        sm = globals()["snakemake"]
        merge_logs(list(sm.params.parts), sm.output[0])
