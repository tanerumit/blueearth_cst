---
title: Snakemake scheduler stalls mid-run on long WF2 fetch batches
type: todo-item
status: active
effort: 1
area: wf2
origin: t2610022259 P0 (2026-10-06)
queue: 3
doc: dev/tasks/t2610062309/diagnosis.md
created: 2026-10-06
updated: 2026-10-09
---

> [!note] Overview
> **What** — Twice in one 125-fetch WF2 run the scheduler stopped advancing: job logs complete, outputs written, no child processes, zero CPU, no further DONE rows.
> **Why** — A long unattended run (larger ensembles, e2e) silently hangs instead of finishing or failing; recovery needs kill, -- --unlock and -- --rerun-incomplete.
> **Effort** — Diagnosis first; main unknown is whether it is Snakemake's local executor on Windows, the benchmark/psutil patch, or the run-log heartbeat.

## Progress

- [x] Review original stalls and recent verification: the third stall also affected cached inputs.
- [x] Run two local 251-job, three-core probes with benchmarks and console hooks; both passed.
- [x] Validate main-first stack capture, including more than 100 threads and the owned launcher.
- [ ] Capture scheduler and worker stacks during a real cached-input recurrence; root cause is unconfirmed.
- [ ] Bisect one factor at a time after locating the blocking frame: cores, benchmarks, heartbeat.

Diagnosis and the opt-in capture recipe: [current evidence](t2610062309/diagnosis.md).
No production workaround or concurrency default was changed; serial recovery is not a verified fix.

## Evidence

- Stalls at about 21:46 and 22:42 on 2026-10-06, after about 60 jobs each, in project
  `C:/data/cmip6/gabon-ntoum-dev-ensemble`. Scheduler tails: [stall evidence](t2610062309/stall-evidence.md).
- The three jobs in flight had each written their outputs and per-job logs; Snakemake (python.exe under
  snakemake.exe) had no children and accrued no CPU over 10 s.
- Recovery that worked: stop the process tree, `run_workflow.py ... -- --unlock`, relaunch with
  `-- --rerun-incomplete`.
