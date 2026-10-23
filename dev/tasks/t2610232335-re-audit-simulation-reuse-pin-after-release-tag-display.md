---
title: Re-audit simulation reuse pin after release-tag display
type: todo-item
status: active
effort: 1
area: experiment
origin: t2610082103 step 7 landing
queue:
created: 2026-10-23
updated: 2026-10-23
---

> [!note] Overview
> **What changes** — The simulation reuse bridge accepts the current inventory after 094bab3a, so test_simulation_reuse passes again
> **Why it matters** — Five reuse tests fail on main and block the next push; retained simulations cannot be reused across this non-scientific change
> **What it takes** — Small: audit the provenance.py diff, pin the new inventory, add a captured fixture

## Progress

- [ ] <first step>
