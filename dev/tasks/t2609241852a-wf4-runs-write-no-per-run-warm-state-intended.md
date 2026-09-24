---
title: "WF4 runs write no per-run warm state: intended?"
type: todo-item
status: backlog
effort: 1
area: wf4
origin: wf3 identity bundle (2026-09-24)
queue:
created: 2026-09-24
updated: 2026-09-24
---

> [!note] Overview
> **What** — HM-6b validated per-run outstates_run_*.nc; since the R12 generation/simulation split (868c4b7c) WF4 run TOMLs carry no [state] path_output and every run starts from WF1's instate/instates.nc. Confirm this was a deliberate simplification (then drop HM-6b) or restore per-run warm states.
> **Why** — A silently dropped output looks like a design choice only if someone decided it.
> **Effort** — small

## Progress

- [ ] <first step>
