---
title: Adopt the shared plotting style in R/WF3 figures
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
> **What changes** — WF3 weathergenr figures follow the same style tokens and export conventions as the
> Python-rendered WF0–WF2 figures.
> **Why it matters** — WF3 figures are R-owned and outside the shared core, so their fonts, colours and
> sizes can drift from the rest of the toolbox.
> **What it takes** — Needs scoping: R reads the `config/plotting/*.yml` tokens directly, or WF3
> rendering moves to Python.

## Progress

- [ ] Inventory WF3 figures and their current style sources.
- [ ] Choose the adoption route with the owner.
- [ ] Implement and inspect the rendered figures.

Next: inventory the WF3 figures.
