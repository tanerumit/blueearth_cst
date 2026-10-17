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

Design sealed at the owner's request on 2026-10-16:
[final design v3](t2610161523/design-runs/named-indicator-sets/design-v3.md).
All domain and external findings are resolved in the design or mapped to implementation acceptance.
Authored definitions are retained; coverage and units are explicit. Exact seal and review limitations
are in [status](t2610161523/design-runs/named-indicator-sets/status.md#final-seal--2026-10-16).
Next: When implementation is authorized, capture the O1-O6 pre-change oracle before editing runtime code.

- [x] Review and seal [the design](t2610161523/design-runs/named-indicator-sets/design-v3.md).
- [ ] Implement the agreed integration and update affected consumers and documentation.
- [ ] Verify default compatibility, independent set reuse, and failure recovery.

## Work location

- Coordination: main :: dev/tasks/t2610161523/.
- Implementation: started 2026-10-17 in session-2 on `feat/named-indicator-sets`.
- Pre-change oracle: `.tmp/indicator-default-parity-prechange/` here (archived source at f1faac2b,
  runtime-identical to 791fd1f). No retained metric-set/3 tree existed (all local WF4 trees were
  simulation/2), so the owner chose a fresh rapid WF1+WF3+WF4 run into that evidence root.
- Task-ownership guard: landed at 307f1e65; all worktrees updated.
- Verification: 4497 passed, 29 skipped, 1 expected failure; evidence in .tmp/task-ownership-landing.json.

Review: [named indicator sets](t2610161523/design-runs/named-indicator-sets/status.md).
