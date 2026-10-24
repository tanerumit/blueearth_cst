---
title: Runner dry-run plans a full WF1 rebuild after a complete run
type: todo-item
status: backlog
effort: 1
area: wf1
queue:
created: 2026-10-24
updated: 2026-10-24
---

> [!note] Overview
> **What changes** — A dry-run through scripts/run_workflow.py after a completed WF1 run shows only the work a real run would do.
> **Why it matters** — It currently reports delineate_region inputs as changed and plans all 20 jobs, while the real run rebuilds nothing, so the preview misleads users and verification.
> **What it takes** — Find what differs between the runner's dry-run and execute invocations for delineate_region (likely staged config or archive paths) and align them.

## Progress

- [ ] <first step>
