---
title: "Drop the WF3 retain copy step (3.09): write scenario series directly to the kept location"
type: todo-item
status: backlog
branch: wf3-improvements
effort: 1
area: wf3
origin: wf3 generation bundle (2026-09-24)
queue:
created: 2026-09-24
updated: 2026-09-24
---

> [!note] Overview
> **What** — 3.07/3.08 write temp() run_{id}.nc under weathergenr/output and 3.09 copies each (14 jobs here) into series/. Have generation write straight into series/ (or move instead of copy) so every series is not written twice; publish_scenario_collection keeps validating before the ready marker. Decides 3.09's fate and therefore its name in t2609241251 -- land together.
> **Why** — Doubles disk writes and adds one job per member; cost grows with realizations x stress points.
> **Effort** — small

## Progress

- [ ] <first step>
