---
title: Choose the WF4 batch count from a makespan model of run length and resources
type: todo-item
status: backlog
effort: 2
area: wf4 batching
origin: batch-failure retry (2026-09-24)
queue:
created: 2026-09-24
updated: 2026-09-24
---

> [!note] Overview
> **What** — resolve_batch_size picks B from members/cores, a cap of 8 and disk. Replace the count choice with a cost model: per-batch Julia start-up (P3-3: ~92 s cold, ~35 s warm) plus per-member run time (~16 s + 0.59 s x simulated years, validation-ladder.md), LPT over the available slots, bounded by memory and disk; then split evenly (split_evenly, already shipped). dev/scripts/estimate_batch_makespan.py holds the model; move the shared part into the package, since a run path would call it.
> **Why** — One cap ignores simulation length and machine size: short runs want few big batches to amortise start-up, long runs on many cores want more batches to fill the slots.
> **Effort** — large

## Progress

- [ ] <first step>

## Probe and outcome (2026-09-25)

Baseline basin (257 active cells, 9 years), 12 logical CPUs, 12 members:

| Setup | Wall | Cold | Warm/member |
|---|---|---|---|
| 1 thread, one batch (4 members) | 97 s | 51 s | ~12 s |
| 2 threads, one batch | 156 s | 89 s | ~22 s |
| 4 threads, one batch | 129 s | 77 s | ~15 s |
| 2 x 1-thread batches at once | 124 s | 58 s | ~12.5 s |
| 3 x 1-thread batches at once | 142 s | 80 s | ~19 s |
| 6 x 1-thread batches at once | 173 s | 136 s | ~30 s |

Threads cost time on a small grid, and more than two Julia sessions at once
contend. The makespan model reduced to one rule -- one balanced batch per
slot -- with the thread count and the slot limit as regime settings
(`advanced_settings.batching`, project `compute.julia_threads` /
`compute.max_parallel_batches`) capped by cores and a memory estimate.
Large-basin values stay provisional until `scripts/calibrate_batching.py` is
run on one. A full WF4 run on the baseline took 3:23 in one 1-thread batch
(memory capped it at one with 3.2 GB free) against ~4:28 before.

