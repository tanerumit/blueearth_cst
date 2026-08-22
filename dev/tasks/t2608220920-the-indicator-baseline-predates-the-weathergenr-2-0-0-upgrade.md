---
title: The indicator baseline predates the weathergenr 2.0.0 upgrade
type: todo-item
status: backlog
branch:
effort: 1
area: baseline / wf3
origin: R13 baseline pass 1 (2026-08-21)
queue:
created: 2026-08-22
updated: 2026-08-22
---

> [!note] Overview
> **What** — `dev/baseline/manifest.json`'s `q_indicators.csv` reference (`indicator_ref/74ed83c06b2e7e6c.csv`) was recorded 2026-08-16 under weathergenr **1.2.0**. `cf5daa0` completed the 1.2.0 -> 2.0.0 transition on 2026-08-17. Every WF3 run since draws different realizations, so `check_baseline check` has reported a 610/630-row indicator failure ever since — for a reason that is correct, expected, and nothing to do with whatever branch is being checked.
> **Why** — A falsifier that is permanently red stops being read. It also actively misleads: it consumed most of R13's pass-1 session, where the low-flow signature was first attributed to a hydrology change and R13 was briefly a suspect. Every milestone that re-records from here inherits an unattributable indicator move.
> **Effort** — small (one WF3 run + record), but it must be run from the PRIMARY

## The dating

| date | event |
|---|---|
| 2026-08-16 09:23 | `82b76a0` — manifest recorded, incl. the indicator ref table |
| 2026-08-17 18:49 | `cf5daa0` — weathergenr 1.2.0 -> 2.0.0 transition completed |
| 2026-08-18 | `t2608132341` — Wflow invocation changed in rules 1.14 and 3.15 |

`packageVersion('weathergenr')` now reports `2.0.0`.

## Why it is the generator and not the 08-18 Wflow change

`850fb17` (2026-08-18) changed how both rule 1.14 and rule 3.15 enter Wflow. The
exclusion does not rest on the two being "the same commit" — **they call the
same function.** Verified rather than assumed, because 1.14 and 3.15 did NOT
receive the same edit (1.14 moved from `-e "using Wflow; Wflow.run()"` to a new
driver file; 3.15 already had one and only gained a label):

- `blueearth_cst/model/run_wflow.jl` (1.14) calls
  `run_with_progress(Wflow, tomlpath; label="wflow")`
- `blueearth_cst/experiment/run_wflow_batch.jl` (3.15) calls
  `run_with_progress(Wflow, t; label=tag)`

Both resolve to `WflowProgress.run_with_progress` in
`blueearth_cst/shared/wflow_progress.jl`, which does `config =
Wflow.Config(tomlpath)` and then `Wflow.run(config)` inside a `with_logger`
that mirrors upstream's `Wflow.run(tomlpath)` clause for clause. The only
deviation is a tee'd frame logger riding alongside Wflow's file logger. Nothing
in it touches initial state, warm-up or routing.

So WF1's discharge — re-derived in pass 1 and reproducing the manifest exactly —
exercises the *same code* WF3 runs through. The seam is numerically inert, and
`cf5daa0` is the only remaining change that reaches WF3 and not WF1.

`cf5daa0` is behavioural, not a version bump: `relax_priority` -> `relax_order`
at both entry points, and its own message records the argument was **inert on
1.2.0 at both**. A previously-inert generator argument becoming live changes the
generated series.

## The signature, and the reading that misled

Mean absolute relative move: `q_driest_month_mean` 0.384, `q_baseflow_index`
0.317, `q_mean_annual_7day_min` 0.268 … `q_annual_mean` **0.014**. Uniform
across `st_id` and `rlz_id`; deterministic across three runs at different core
counts and batch compositions (byte-identical `63120f16…`).

"The mean barely moves while baseflow moves 32%, so this cannot be new
realizations" is the wrong expectation. Preserving monthly and annual means is
what a fitted stochastic generator is *for*; realized daily sequencing, and
therefore recession and low-flow behaviour, is what is free to move between
draws. Mean preserved + extremes moved **is** the re-drawn-realization
signature. Keep that here — it is the part that will be mis-read again.

## What to do

Re-record the indicator baseline from the primary, in a commit that names
`cf5daa0` as the cause and changes nothing else, so the move stays attributable.
Ideally before R13's pass-1 re-record, so R13 has a control in which zero data
targets move — see `dev/milestones/r13/baseline-pass-1-result.md` § The gate.

Related: [[t2608071201]] (re-records accepted without reading the diff),
[[t2608131718]].
