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
> **What it takes** — Extend PET retention and paired inputs; resolve ET compatibility and case bindings.

## Progress

Next: Agree the scope-review recommendations, starting with ET interpretation and reader compatibility.

- [x] Review the case brief against current WF4 — scope supported, integration gaps recorded in the review.
- [ ] Resolve PET/AET interpretation, spatial support, baseline Qcrit and active case inputs.
- [ ] Define paired-input and retained-reader compatibility contracts, including publication and identity.
- [ ] Add PET output/retention and the six methods with ten selections and period diagnostics.
- [ ] Verify independent arithmetic, affected consumers and a bounded retained-response integration.
- [ ] Document the set and configure the active Alexandria case when bindings are verified.

Review and task capture are complete. Implementation has not been authorized by the review request.
Keep the item in backlog until implementation is taken up; no simulations were run.

## Work location

- Owner: session-1; branch: `feat/t2610211633`; implementation: not started.
- Coordination: main :: `dev/tasks/t2610211633/`.
- Evidence: linked review; inspected toolbox revision `9887be49`.
- Next action: resolve review decisions; case series and active configuration remain unverified.

## Refs

- [Scope review](t2610211633/scope-review.md).
- [Case task brief](../../../cst-cases/_prep/egpyt-alexandria/crop-metrics/crop-water-indicator-set-task-brief.md).
- Related foundation: `t2610161523` (multiple metric sets).
