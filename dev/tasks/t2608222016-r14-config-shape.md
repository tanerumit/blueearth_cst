---
title: R14 config shape - naming, nesting and section policy
type: todo-item
status: active
branch: feat/r14-config-shape
effort: 2
area: config / schema
origin: R14
queue: 1
created: 2026-08-22
updated: 2026-08-22
---

> [!note] Overview
> **What** — Reshape the project config WITHIN R13's tier split: retire the shared: heading in favour of kind-named sections (basin, climate, model, method, compute), regroup by kind, and apply one naming policy. 38 indexed changes C-01..C-38 in dev/milestones/r14/config-shape-scoping.md.
> **Why** — R13 fixed which FILE a key lives in and left which SECTION, and what a key is called, decided by history. shared: names a relationship rather than a kind; one concept has several spellings; and the experiment guard's key list is hand-maintained because no boundary separates changes-the-numbers from changes-only-the-wall-clock.
> **Effort** — large

## Progress

- [ ] <first step>
