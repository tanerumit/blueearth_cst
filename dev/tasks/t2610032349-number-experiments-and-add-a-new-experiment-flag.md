---
title: Number experiments and add a new-experiment flag
type: todo-item
status: active
effort: 2
area: wf4
queue: 3
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
- [x] Review the reservation/binding contract against WF3 run-id work before implementation.
- [x] Implement shared name resolution, allocation history and atomic reservation; add focused tests.
- [x] Integrate both runners, input binding, previews, ownership and recovery diagnostics; add tests.
- [x] Verify interrupted runs, retained responses, metrics-only operations and read-only inspection.
- [x] Update live docs, templates and naming-helper behavior; execute required acceptance checks.

## Decisions

The [brief](t2610032349/task-brief.md) and
[retained evidence](../records/decisions/experiment-numbering-2026-10-10/implementation-evidence.md)
record agreed behavior and passing checks. Implementation landed; the output-folder task is closed.
This item's closure awaits explicit approval to remove the redundant readable review copy.
Automatic approval review rejected that deletion; the copy and original reviewed bytes remain intact.
No push occurred.
