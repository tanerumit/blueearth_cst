---
title: Trim the test suite by cost and lasting value
type: todo-item
status: backlog
effort: 2
area: testing
queue: 6
doc:
created: 2026-10-04
updated: 2026-10-05
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
- [x] Land the batch with both CI legs green (PR #12, `9182b0b5`); re-record the full manifest from a fresh-root run (`95762b58`).
- [x] Retire the migration-era guards per the rulings, keeping the `save_grids` guard (`70fc6173`); cut runtime in the freshness, carrier and tamper files (`29c1ebcf`); add `pixi run test-e2e` (`d503d65d`).
- [x] Read CMIP6 anonymously (`1bd67a16`); retain return-level evidence (`da9f2e82`); port the notebook and `check_baseline` to v2 (`a2dbd0d7`).
- [ ] Re-seed `test_local` in session-1 and session-2 from the primary's re-recorded tree, then close.

## Refs

- [Assessment](../records/reviews/2026-10-04-test-suite-trim-assessment.md) — evidence, tiers and recommendations from 2026-10-04.
- Prior assessment: `git show c7992c6f^:dev/reviews/2026-08-11_test-suite-bloat-assessment.md`.
