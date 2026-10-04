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
> **What** — Retire one-off and never-running tests, retire the unused v1 scenario and record code together with its tests, and cut the runtime of the few files that dominate the suite.
> **Why** — The suite doubled to 4,216 items in eight weeks; about 2.5% of items take half the runtime, and the three slowest cheap-tier files set the floor the parallel fast gate cannot go below.
> **Effort** — Large and mostly test-fixture refactoring; the main unknowns are four owner rulings on migration-era guards and confirming the v1 code is truly unreachable.

## Progress

- [x] Preliminary assessment — tiers, measured cost shares and owner rulings in the backing document.
- [x] Rule on the four migration-era guards — retire equivalence test, two of three R14 sweeps, the migrator and the gridded-key guard; consequences listed in the assessment.
- [ ] Schedule a regular integration run before any retirement that leans on end-to-end coverage.
- [x] Retire never-running and one-off tests — 27 R12 prototype cases, the R9 log-attribution falsifier and the HM-6b stub (`e0ae830b` on `chore/test-trimming`).
- [ ] Port the two kept R12 checkpoint cases to `simulate_system.smk` once a retained v2 experiment fixture exists, then delete `test_r12_wf3_feasibility.py`.
- [ ] Confirm the v1 writers and legacy WF3 modules are unreachable, then move shared fixtures onto v2 producers.
- [ ] Retire the v1 code with its tests.
- [ ] Cut runtime in the freshness, metric-plan, carrier and climate-figure files; settle the deselect marker.

## Refs

- [Assessment](t2610041227/assessment.md) — evidence, tiers and recommendations from 2026-10-04.
- Prior assessment: `git show c7992c6f^:dev/reviews/2026-08-11_test-suite-bloat-assessment.md`.
