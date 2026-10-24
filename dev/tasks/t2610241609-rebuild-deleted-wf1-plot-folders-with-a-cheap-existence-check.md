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

- [ ] Confirm `build_model.smk` edits do not change run-identity or staleness hashes.
- [ ] Request each plot folder only when it is missing or empty.
- [ ] Prove with dry-runs: present (no work), each folder deleted (its rule scheduled).
- [ ] Run the affected WF1 tests; land with owner approval.

Owner decision (2026-10-24): no per-figure fingerprinting or byte checks; a folder-level existence
check is acceptable. A single missing PNG in a non-empty folder is not detected.

Work location: session-1 :: `fix/t2610241609`.

Next: check whether `build_model.smk` is part of any identity or staleness hash.
