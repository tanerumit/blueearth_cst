---
title: Adopt the shared plotting style in R/WF3 figures
type: todo-item
status: backlog
effort: 2
area: plotting
origin: t2610082103
queue:
created: 2026-10-24
updated: 2026-10-30
---

> [!note] Overview
> **What changes** — WF3 weathergenr figures follow the same style tokens and export conventions as the
> Python-rendered WF0–WF2 figures.
> **Why it matters** — WF3 figures are R-owned and outside the shared core, so their fonts, colours and
> sizes can drift from the rest of the toolbox.
> **What it takes** — Needs scoping: R reads the `config/plotting/*.yml` tokens directly, or WF3
> rendering moves to Python.

## Progress

- [x] Inventory the 15 maintained WF3 figures and their style sources.
- [x] Adopt the R adapter with shared YAML tokens and measured R/Python panel geometry.
- [x] Inspect and approve the figures; verify scientific equivalence and install the pinned API privately.

Implementation landed on main at `41af17de`, including the published immutable upstream source pin.
The former local implementation branch was deleted after ancestry and tree-equivalence checks.

## Evidence and operation

- [Retained integration evidence](../records/validation/weather-style-integration-2026-10-30.md).
- [Weather style](../reference/weather-diagnostic-style.md) and
  [panel contract](../reference/panel-layout-contract.md).
- Final checks: 120 affected Python tests, four WF2 DAG cases, private R installation/idempotence,
  same-version wrong-commit repair, API/source checks and scoped lint/format checks passed.
- Runtime owners should run `pixi run install-rdeps` before WF3 after updating; shared runtimes were
  preserved during private verification.
- Retain the approved figures/styled R objects while the comparison gallery needs them, and the private
  install library/logs until the runtime owner confirms installation.
- Reserved in session-2 on 2026-10-28; completed and landed 2026-10-30. No push performed.
