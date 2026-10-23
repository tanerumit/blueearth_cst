---
title: Re-audit simulation reuse pin after release-tag display
type: todo-item
status: active
branch: fix/t2610232335
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

## Progress

- [x] Audit the `094bab3a` diff to `shared/provenance.py`: 29 added lines (display helper
  `toolbox_release_tag` and an `re` import); no existing function changed; no simulation caller.
- [x] Pin the new inventory, keep `12c0…` as `_BOUNDARY_TEMPERATURE`, accept older-to-newer
  transitions, and add the `094bab3a^` inventory fixture — `3755219c` on `fix/t2610232335`.
- [ ] Land on local main after owner approval.

Next: land `fix/t2610232335` when the owner says go; no push.

## Work location

- Owner: session-1; branch: fix/t2610232335; implementation commit: `3755219c`.
- Verification: `tests/test_simulation_reuse.py` 74 passed (8 new transition cases); repository lint
  and format-check pass; `git diff --check` clean. The fixture hashes to the previous pin `12c0…`.
- Next action: land on owner approval; blockers: none.
