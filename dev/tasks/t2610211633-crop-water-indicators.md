---
title: Add crop-water screening indicators to WF4
type: todo-item
status: blocked
effort: 2
area: wf4
queue:
branch: feat/t2610211633
doc: dev/tasks/t2610211633/scope-review.md
created: 2026-10-21
updated: 2026-10-21
---

> [!note] Overview
> **What changes** — Add six crop-water screening methods with ten seasonal or annual selections.
> **Why it matters** — Agricultural screening needs paired climate and model responses.
> **What it takes** — Extend PET retention and paired inputs; resolve case bindings and baseline Qcrit.

## Progress

*Blocked — WF1 source raster unreadable; no historical Q, Qcrit or ready model.*

Next: Restore P-drive hydrography, rerun WF1, apply case Q90, then prepare WF3/WF4.

- [x] Revise brief and document the set and starter configuration.
- [x] Implement paired-input retention, publication and identity.
- [x] Add native PET, six methods, ten selections and period diagnostics.
- [x] Verify arithmetic, affected consumers, retained-response integration and native Wflow PET.
- [ ] Verify historical Q and active case bindings; derive fixed Qcrit.
- [x] Prepare Alexandria outputs, selector and Q90 command (`cst-cases` `56ca48c`).
- [ ] Fill Qcrit and run the Alexandria case.

Qcrit trial policy: linear 0.10 quantile of complete 1985–2004 historical May–October
daily model Q, fixed at every native location. Missing thresholds refuse evaluation.

Evidence: toolbox checks and native PET run passed. Alexandria WF1 dry-run passed; rule 1.01
failed reading P-drive `30sec_uparea.tif`. See case notes; no Qcrit value was invented.

## Work location

- Owner: session-1; branch: `feat/t2610211633`.
- Coordination: main :: `dev/tasks/t2610211633/`.

## Refs

- [Scope review](t2610211633/scope-review.md).
- [Case task brief](../../../cst-cases/_prep/egpyt-alexandria/crop-metrics/crop-water-indicator-set-task-brief.md).
- Related foundation: `t2610161523` (multiple metric sets).
