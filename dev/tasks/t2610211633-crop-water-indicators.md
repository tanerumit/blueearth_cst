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

*Blocked — Alexandria lacks verified historical Q, fixed Qcrit and WF1/WF3/WF4 bindings.*

Next: Verify case bindings and baseline years, derive location-keyed Qcrit, then run the case.
The active `wrt-egypt-v2` project currently has WF2 material only.

- [x] Revise brief and document the set and starter configuration.
- [x] Implement paired-input retention, publication and identity.
- [x] Add native PET, six methods, ten selections and period diagnostics.
- [x] Verify arithmetic, affected consumers, retained-response integration and native Wflow PET.
- [ ] Verify historical Q and active case bindings; derive fixed Qcrit.
- [x] Prepare Alexandria model outputs and crop-water selector (`cst-cases` `a94e353`).
- [ ] Fill Qcrit and run the Alexandria case.

V1 uses existing AET/reference PET and non-Q subcatchment means. Qcrit is the location-keyed
linear 0.10 quantile across complete historical summers; missing thresholds refuse evaluation.
Existing development runs require regeneration for PET retention.

Evidence: independent numerical checks, retained-response publication and named export,
affected pytest, Ruff and syntax checks, plus isolated Julia/Wflow PET output read at four
subcatchment IDs. Native-run evidence: session-1 `.tmp/tasks/crop-water-native/`.

## Work location

- Owner: session-1; branch: `feat/t2610211633`.
- Coordination: main :: `dev/tasks/t2610211633/`.

## Refs

- [Scope review](t2610211633/scope-review.md).
- [Case task brief](../../../cst-cases/_prep/egpyt-alexandria/crop-metrics/crop-water-indicator-set-task-brief.md).
- Related foundation: `t2610161523` (multiple metric sets).
