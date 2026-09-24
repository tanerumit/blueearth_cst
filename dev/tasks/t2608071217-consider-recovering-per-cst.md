---
title: One failing member re-runs its whole WF4 Wflow batch
type: todo-item
status: backlog
effort: 2
area: wf4 batching
origin: P3-3
queue: 1
created: 2026-08-07
updated: 2026-09-24
---

> [!note] Overview
> **What** — Recover per-cst persistence isolation under batching.
> **Why** — One failing cst takes down its whole batch by design, so a single bad member costs B members of work.
> **Effort** — Large and design-shaped: C5 is degraded deliberately, so this reopens an accepted trade-off.

## Progress

- [ ] <first step>

## Checked 2026-09-24

Still relevant, but the location moved: since the R12 split, batched Wflow
runs are WF4 rule 4.05 `run_wflow_batch_<n>` in
`blueearth_cst/experiment/rules/simulate_and_metrics.smk`, sized by
`batch_sizing.resolve_batch_size` with `batch_size_max` default 8. The Detail
below still says cst and rule 3.11. The C35 proposal (default B=1, batching
opt-in) was not adopted. Rule on C35 first: with B=1 this item disappears.
Folded in the watch item t2608071224, which pointed at CR-7 / F18 in
`dev/milestones/r09/wf3-change-requests.md` for the time economics.

## Refs

- Migrated from `dev/followups.md` on 2026-08-07, when the board replaced it. Prose below is that
  entry verbatim; it is the reproducible context, not a summary.

## Detail

**Consider recovering per-cst persistence isolation under batching.** C5 is
DEGRADED by design (blast radius `B`): one failing cst causes Snakemake to
delete the `B−1` completed sibling CSVs and re-run the whole batch, and rule
3.11 is blocked sweep-wide until it succeeds. Measured exactly as documented
(`dev/milestones/p33/batching-results.md` GN-4). §6.1 names the mechanism worth probing:
the `--keep-incomplete` ↔ `--keep-going` interaction (does `--keep-incomplete`
preserve successfully-written sibling CSVs across a failed batch job, and does
the sweep then re-run only the failed cst?), with **accept-the-degradation as
the explicit fallback** if the probe fails. Only worth doing if the blast
radius actually bites in practice.
