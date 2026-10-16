---
title: Integrate multiple metric sets
type: todo-item
status: active
effort: 2
area: wf4
queue:
created: 2026-10-16
updated: 2026-10-16
---

> [!note] Overview
> **What changes** — Select named indicator sets over shared responses and publish separate results.
> **Why it matters** — Users need reusable indicator definitions, separate results, and traceable calculations.
> **What it takes** — Review the design, then implement configuration, registry, and publication changes.

## Progress

G1 framing approved. All six Opus domain findings are incorporated in
[design v2](t2610161523/design-runs/named-indicator-sets/design-v2.md); unit interpretation awaits review.
Next: Independent Opus review of v2 is prepared; launch held by automatic approval review pending
explicit payload/destination confirmation. Final design approval remains pending.

- [x] Capture the agreed interface and remaining decisions in [the design](t2610161523/indicator-sets-design.md).
- [ ] Implement the agreed integration and update affected consumers and documentation.
- [ ] Verify default compatibility, independent set reuse, and failure recovery.

## Work location

- Coordination: main :: dev/tasks/t2610161523/.
- Implementation: not started; no session currently allocated.
- Task-ownership guard: landed at 307f1e65; all worktrees updated.
- Verification: 4497 passed, 29 skipped, 1 expected failure; evidence in .tmp/task-ownership-landing.json.

Review: [named indicator sets](t2610161523/design-runs/named-indicator-sets/status.md).
