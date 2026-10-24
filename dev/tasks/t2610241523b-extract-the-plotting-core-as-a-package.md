---
title: Extract the plotting core as a package
type: todo-item
status: backlog
effort: 2
area: plotting
origin: t2610082103
queue:
created: 2026-10-24
updated: 2026-10-24
---

> [!note] Overview
> **What changes** — `blueearth_cst/plotting` ships as a separate numpy + matplotlib distribution with a
> documented public API.
> **Why it matters** — Other hydrology and climate tools could reuse CST's figure style; until then the
> core imports only from a CST checkout.
> **What it takes** — Gated: start only when a named second, non-CST use case adopts the core and confirms
> the candidate API in the [packaging scope](t2610241523b/packaging-scope.md).

## Progress

- [ ] Confirm the second use case and the API it needs.
- [ ] Close the known gaps in the packaging scope: map literals, `NEUTRAL` exercise, core API tests.
- [ ] Choose the name and layout, then extract; the owner approves any release.

Next: wait for the extraction trigger; do not start without a second use case.
