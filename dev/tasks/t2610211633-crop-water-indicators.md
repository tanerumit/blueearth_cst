---
title: Add crop-water screening indicators to WF4
type: todo-item
status: backlog
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

Next: Execute the revised brief; inspect paired-input contracts and case bindings.

- [x] Review and revise the case brief — self-contained SOL medium handoff includes settled v1 scope.
- [x] Set v1 assumptions — use existing AET/PET and non-Q subcatchment means; document limitations.
- [ ] Resolve baseline Qcrit and active case inputs.
- [ ] Define paired-input and retention contracts, including publication and identity.
- [ ] Add PET output/retention and the six methods with ten selections and period diagnostics.
- [ ] Verify independent arithmetic, affected consumers and a bounded retained-response integration.
- [ ] Document the set and configure the active Alexandria case when bindings are verified.

Handoff ready; implementation not started. The revised brief owns the assignment.

No backward compatibility required: omit migration/legacy readers; development runs may need regeneration.
Keep single-input sets working and retain provenance/integrity checks.

V1 uses existing AET/PET and daily subcatchment means for all non-Q inputs before calculation.
Document ET and spatial limitations for later review; neither blocks v1.

## Work location

- Owner: session-1; branch: `feat/t2610211633`; implementation: not started.
- Coordination: main :: `dev/tasks/t2610211633/`.
- Evidence: linked review; inspected toolbox revision `9887be49`.

## Refs

- [Scope review](t2610211633/scope-review.md).
- [Case task brief](../../../cst-cases/_prep/egpyt-alexandria/crop-metrics/crop-water-indicator-set-task-brief.md).
- Related foundation: `t2610161523` (multiple metric sets).
