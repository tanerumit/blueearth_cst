---
title: Number experiments and add a new-experiment flag
type: todo-item
status: backlog
effort: 2
area: wf4
queue: 11
doc: dev/tasks/t2610032349/experiment-naming-plan.md
created: 2026-10-03
updated: 2026-10-10
---

> [!note] Overview
> **What changes** — Number experiments from `stress_test_01`; plain runs continue the highest number.
> `--new-experiment` explicitly creates another. Bind intended inputs early so changed scenarios cannot
> silently replace an interrupted experiment.
> **Why it matters** — Users need predictable creation, resumption and comparison without overwriting
> results or remembering dated folder names. Completion alone must never create another experiment.
> **What it takes** — Allocation and ownership records, shared runner integration, interruption and
> compatibility checks, focused tests and live docs. The expanded plan supersedes the two-commit estimate.

## Progress

- [x] Expand naming and recovery decisions — see the linked plan and acceptance matrix, 2026-10-10.
- [ ] Review the reservation/binding contract against WF3 run-id work before implementation.
- [ ] Implement shared name resolution, allocation history and atomic reservation; add focused tests.
- [ ] Integrate both runners, input binding, previews, ownership and recovery diagnostics; add tests.
- [ ] Verify interrupted runs, retained responses, metrics-only operations and read-only inspection.
- [ ] Update live docs, templates and naming-helper behavior; execute required acceptance checks.

## Decisions

The 2026-10-03 agreement remains: a plain run continues the highest numbered experiment, regardless
of completion; an explicit runner flag starts another. Existing dated folders remain unchanged.

The [expanded plan](t2610032349/experiment-naming-plan.md) records the selected behavior, compatibility,
failure cases and validation. Implementation remains in backlog; this update authorizes planning only.

The 2026-10-10 output-folder decision removes the `active/` scaffold convention separately. Numbering
works within any user-selected output root and does not version or archive the whole assessment.
