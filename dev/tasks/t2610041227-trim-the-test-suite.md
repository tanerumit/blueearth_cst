---
title: Trim the test suite by cost and lasting value
type: todo-item
status: backlog
branch: chore/test-trimming
effort: 2
area: testing
queue:
doc: dev/tasks/t2610041227/assessment.md
created: 2026-10-04
updated: 2026-10-04
---

> [!note] Overview
> **What changes** — Retire one-off and never-running tests, retire the unused v1 scenario and record code together with its tests, and cut the runtime of the few files that dominate the suite.
> **Why it matters** — The suite doubled to 4,216 items in eight weeks; about 2.5% of items take half the runtime, and the three slowest cheap-tier files set the floor the parallel fast gate cannot go below.
> **What it takes** — Large and mostly test-fixture refactoring; the main unknowns are four owner rulings on migration-era guards and confirming the v1 code is truly unreachable.

## Progress

- [x] Preliminary assessment and owner rulings — tiers, cost shares and rulings in the backing document.
- [x] Retire never-running and one-off tests — 27 R12 prototype cases, the R9 log-attribution falsifier, the HM-6b stub (`960bef79` on `chore/test-trimming`).
- [x] Build a real retained v2 experiment and move the metric, carrier, inventory and R12 checkpoint tests onto it (`178d09f8`, `7fb676c9`, `416c68cb`).
- [x] Retire the v1 records with their tests; re-record the baseline metric set (`47963863`, `c073e9b3`, `546339c3`, `f5b77fc8`, `83749402`).
- [ ] Open the PR for the batch, read both CI legs, land; then repeat the metrics-only re-record in every other worktree's `test_local`.
- [ ] Run a full baseline (WF3+WF4) and re-record: the collection and simulation ids moved too.
- [ ] Retire the migration-era guards per the rulings; cut runtime in the freshness, carrier and climate-figure files; schedule a regular integration run.

## Refs

- [Assessment](t2610041227/assessment.md) — evidence, tiers and recommendations from 2026-10-04.
- Prior assessment: `git show c7992c6f^:dev/reviews/2026-08-11_test-suite-bloat-assessment.md`.
