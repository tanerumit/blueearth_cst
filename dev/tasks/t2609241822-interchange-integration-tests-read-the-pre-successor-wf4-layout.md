---
title: Interchange integration tests read the pre-successor WF4 layout
type: todo-item
status: backlog
effort: 1
area: tests
origin: wf3 identity bundle (2026-09-24)
queue:
created: 2026-09-24
updated: 2026-09-24
---

> [!note] Overview
> **What** — 11 integration tests in tests/test_interchange_contracts.py (wg2-wg6, hm4-hm7, gauge identity) read test_case/test_local/experiments/experiment/config/simulation.json; current WF4 writes _engine/simulation.json. They passed only while test_local held an older tree and fail since its 2026-09-24 regeneration. Also: test_run_workflows::test_failure_console_carries_the_verdict_and_what_did_not_run asserts elapsed '0:00:0' (under 10 s) and fails under full-suite load.
> **Why** — test-full carries 12 extra red cases on every worktree whose test_local is current, hiding real regressions.
> **Effort** — small

## Progress

- [ ] <first step>
