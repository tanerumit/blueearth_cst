---
title: Integrate multiple metric sets
type: todo-item
status: active
effort: 2
area: wf4
queue:
created: 2026-10-16
updated: 2026-10-17
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
Implementation 2026-10-17 on `feat/named-indicator-sets` (session-2): design steps 1-4 committed
(5c8aba2c, 88da969c, 64151d5a, fa6124da, bd539f24, b5488613), plus the YE anchor (0ef6cf07).
The O1-O6 oracle came from the archived pre-change source. P-drive reads stalled, so the rapid run
uses the local staged data bundle.
C4 (Jan and Oct) and the YE gate gave byte-identical tables and keys. C6 showed 0 of 64 legacy
branches differing. Named mode, named vs flat export, flat-export preservation and the O2 positive
checks all pass. Evidence: `.tmp/indicator-default-parity-prechange/index.md`.
A full run created by the candidate (named simulate path) reproduced the oracle tables. Legacy and
named dry runs both left WF4 up to date.
Open: model-validator acceptance of the oracle coverage; landing.

- [x] Review and seal [the design](t2610161523/design-runs/named-indicator-sets/design-v3.md).
- [x] Implement the agreed integration and update affected consumers and documentation.
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
