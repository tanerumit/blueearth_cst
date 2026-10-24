---
title: Runner dry-run plans a full WF1 rebuild after a complete run
type: todo-item
status: backlog
effort: 1
area: wf1
queue:
created: 2026-10-24
updated: 2026-10-24
---

> [!note] Overview
> **What changes** — A dry-run through `scripts/run_workflow.py` after a completed WF1 run shows only
> the work a real run would do.
> **Why it matters** — It reports `delineate_region` inputs as changed and plans all 20 jobs, while
> the real run rebuilds nothing, so the preview misleads users and verification.
> **What it takes** — Find what differs between the runner's dry-run and execute invocations for
> `delineate_region`, then align them.

## Progress

- [ ] Reproduce on a fresh rapid WF1 run and list `delineate_region`'s input set in both modes.
- [ ] Align the dry-run invocation (likely staged config or archive paths) with execution.
- [ ] Confirm a post-run runner dry-run reports nothing to do.

Observed 2026-10-24 during t2610241609 on main `4c51caf6`, with and without that change. After a
complete rapid WF1 run, `run_workflow.py build_model --dry-run` reported "set of input files has
changed since last execution: delineate_region" and planned 20 jobs. A bare `snakemake -n
--rerun-triggers mtime` planned none, and a real runner execution reran only the rules whose
outputs were missing.

Next: diff `delineate_region`'s inputs between a runner dry-run and an execute invocation.
