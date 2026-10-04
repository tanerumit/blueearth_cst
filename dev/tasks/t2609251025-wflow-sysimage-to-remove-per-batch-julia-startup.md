---
title: "Wflow sysimage to cut Julia startup"
type: todo-item
status: backlog
effort: 1
area: runtime
origin: t2608222155 owner ruling (2026-09-25)
queue:
created: 2026-09-25
updated: 2026-09-27
---

> [!note] Overview
> **What changes** — The first Wflow member in each Julia process has roughly 80 seconds of additional startup cost; a PackageCompiler sysimage might reduce it.
> **Why it matters** — Startup was measured as a material share of baseline runtime, while building and maintaining a Wflow-specific sysimage still needs design and cost validation.
> **What it takes** — Start when: A Julia/Wflow runtime upgrade or packaging change is planned, so the sysimage option can be assessed against that work.

## Progress

- [ ] Reassess once the start condition in Effort holds
