---
title: Rebuild deleted WF1 plot folders with a cheap existence check
type: todo-item
status: active
effort: 1
area: wf1
queue:
created: 2026-10-24
updated: 2026-10-24
---

> [!note] Overview
> **What changes** — When a WF1 plot folder is missing or empty, the next run redraws it. Present
> folders add no checks.
> **Why it matters** — WF1 targets omit figures on purpose, because per-figure change checks made runs
> very slow. As a result a deleted plots folder was never rebuilt (dropped t2610241600).
> **What it takes** — A parse-time `isdir`/`scandir` check per plot folder next to `WF1_TERMINALS`,
> proved with dry-runs on rapid outputs.

## Progress

- [x] Confirm `build_model.smk` edits do not change run-identity or staleness hashes — no inventory
  or digest reads Snakefiles; Snakemake's `code` trigger is per rule.
- [x] Request missing declared outputs of 1.11, 1.12 and 1.15 from `rule all` — `4d06a759`.
- [x] Prove with dry-runs on a fresh rapid WF1 run — see evidence below.
- [x] Run the affected WF1 tests — 750 passed after two contract-test updates.
- [ ] Land with owner approval.

Owner decision (2026-10-24): no per-figure fingerprinting or byte checks; a cheap existence check
is acceptable.

## Evidence (2026-10-24)

Fresh rapid WF1 at the branch (14 min 27 s, no errors), then bare `snakemake -n --rerun-triggers mtime`.
Present outputs: only `all` and the gather rules. Deleting `evaluation/plots/`, `stations/` or one
basin-average PNG schedules `plot_model_evaluation` (and `write_run_metadata`); one forcing PNG or
the forcing folder schedules `plot_model_forcing`; the spatial folder or `elevation_basin.png`
schedules `plot_basin_map`. Controls on the unmodified Snakefile: deleting `evaluation/plots/` or one
forcing PNG schedules nothing. Limits: a file removed inside the declared `stations/` directory, or
an emptied `stations/`, is not detected.

Contract tests: `_iofile_signature` compares input functions by name, and the parse-time banner
counts fixed targets; the console recounts resolved inputs at run time.

Runner dry-runs after a completed run report `delineate_region` "set of input files has changed"
with or without this change; the proof used bare mtime-only dry-runs instead.

Work location: session-1 :: `fix/t2610241609`; scratch session-1 :: `.tmp/scratchpad/t2610241609/`.

Next: owner approves landing.
