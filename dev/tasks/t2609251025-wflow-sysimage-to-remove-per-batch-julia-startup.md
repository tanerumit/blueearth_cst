---
title: Wflow sysimage to remove per-batch Julia startup
type: todo-item
status: backlog
effort: 2
area: run cost / julia
origin: t2608222155 owner ruling (2026-09-25)
queue:
created: 2026-09-25
updated: 2026-09-25
---

> [!note] Overview
> **What** — Build a PackageCompiler sysimage for Wflow and point WF1/WF4 Julia invocations at it.
> **Why** — The first member of every batch costs ~80 s more than the rest (JIT + cold SBM path), about a quarter of a baseline run; P3-3 ranked driving per-process fixed cost to zero at -39%. Owner approved boarding 2026-09-25; the new build step still needs design sign-off.
> **Effort** — large

## Progress

- [ ] <first step>
