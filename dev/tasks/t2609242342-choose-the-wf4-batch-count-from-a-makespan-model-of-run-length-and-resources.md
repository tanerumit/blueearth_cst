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
