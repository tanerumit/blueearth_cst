---
title: Snakemake scheduler stalls mid-run on long WF2 fetch batches
type: todo-item
status: backlog
effort: 1
area: wf2
origin: t2610022259 P0 (2026-10-06)
queue:
created: 2026-10-06
updated: 2026-10-06
---

> [!note] Overview
> **What** — Twice in one 125-fetch WF2 run the scheduler stopped advancing: job logs complete, outputs written, no child processes, zero CPU, no further DONE rows.
> **Why** — A long unattended run (larger ensembles, e2e) silently hangs instead of finishing or failing; recovery needs kill, -- --unlock and -- --rerun-incomplete.
> **Effort** — Diagnosis first; main unknown is whether it is Snakemake's local executor on Windows, the benchmark/psutil patch, or the run-log heartbeat.

## Progress

- [ ] Reproduce on a long WF2 batch with a stack dump of the stalled scheduler (py-spy needs approval as a
      new dependency; `faulthandler` is the no-dependency alternative).
- [ ] Bisect: `--cores 1`, benchmarks off, heartbeat off.

## Evidence

- Stalls at about 21:46 and 22:42 on 2026-10-06, after about 60 jobs each, in project
  `C:/data/cmip6/gabon-ntoum-dev-ensemble`. Logs are in worktree `session-1`
  `.tmp/scratchpad/wf2-p0/run1-hung.err` and `run2-hung.err` (scratch; copy before cleanup).
- The three jobs in flight had each written their outputs and per-job logs; Snakemake (python.exe under
  snakemake.exe) had no children and accrued no CPU over 10 s.
- Recovery that worked: stop the process tree, `run_workflow.py ... -- --unlock`, relaunch with
  `-- --rerun-incomplete`.
