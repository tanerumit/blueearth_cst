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
- [x] Retire never-running and one-off tests — 27 R12 prototype cases, the R9 log-attribution falsifier, the HM-6b stub (`e0ae830b`).
- [x] Build a real retained v2 experiment and move the metric, carrier, inventory and R12 checkpoint tests onto it (`8aced8a0`, `ec381eca`, `74792797`).
- [x] Retire the v1 records with their tests and re-record the baseline metric set (`a8311a0a`, `fd1324c1`, `5dbd1381`, `b5d36810`); open a PR for the batch.
- [ ] Retire the migration-era guards per the rulings: the migrator with its tests and guide, the equivalence test, two R14 sweeps, the gridded-key guard.
- [ ] Cut runtime in the freshness, carrier and climate-figure files; settle the deselect marker; schedule a regular integration run.

## Refs

- [Assessment](t2610041227/assessment.md) — evidence, tiers and recommendations from 2026-10-04.
- Prior assessment: `git show c7992c6f^:dev/reviews/2026-08-11_test-suite-bloat-assessment.md`.
