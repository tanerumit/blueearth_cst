---
title: Make the heartbeat first-notice test deterministic
type: todo-item
status: backlog
effort: 1
area: tests / flake
origin: CI run 36123429933 (2026-09-25)
queue:
created: 2026-09-25
updated: 2026-09-25
---

> [!note] Overview
> **What** — Replace the real-clock sleep in tests/test_snake_utils.py::test_heartbeat_keeps_its_first_notice_prompt (0.13 s budget for a notice due at 0.10 s) with an injected clock or event wait.
> **Why** — It failed once on windows-latest CI on a slow runner and passed on re-run; an intermittent red on main hides real failures. Sibling backoff tests use the same real-clock pattern and may share the risk.
> **Effort** — small

## Progress

- [ ] <first step>
