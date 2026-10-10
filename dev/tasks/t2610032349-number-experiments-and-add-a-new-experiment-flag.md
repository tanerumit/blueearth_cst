---
title: Number experiments and add a new-experiment flag
type: todo-item
status: active
effort: 2
area: wf4
queue: 4
doc: dev/tasks/t2610032349/task-brief.md
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
- [x] Prepare combined implementation brief — naming plus removal of `active/`, 2026-10-10.
- [ ] Review the reservation/binding contract against WF3 run-id work before implementation.
- [ ] Implement shared name resolution, allocation history and atomic reservation; add focused tests.
- [ ] Integrate both runners, input binding, previews, ownership and recovery diagnostics; add tests.
- [ ] Verify interrupted runs, retained responses, metrics-only operations and read-only inspection.
- [ ] Update live docs, templates and naming-helper behavior; execute required acceptance checks.

## Decisions

The [plan](t2610032349/experiment-naming-plan.md) owns behavior, compatibility and acceptance cases.
Implementation authorized on `feat/minor-improvements`; reservation contract review is in progress.

Start with the [combined brief](t2610032349/task-brief.md); both task IDs remain open until landing.

P1: toolbox `3bea47b9`, cases `cdaad63`. Reservation review: task-owned
`design-runs/reservation-lifecycle/` on this branch.
