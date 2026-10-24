---
title: Rebuild deleted WF1 plot folders with a cheap existence check
type: todo-item
status: active
effort: 1
area: wf1
queue:
created: 2026-10-24
updated: 2026-10-24
---

> [!note] Overview
> **What changes** — When a WF1 plot folder is missing or empty, the next run redraws it; present folders add no checks.
> **Why it matters** — WF1 targets omit figures for speed, so a deleted plots folder was never rebuilt (dropped t2610241600).
> **What it takes** — Parse-time isdir/scandir per plot folder next to WF1_TERMINALS; prove with dry-runs on rapid outputs.

## Progress

- [ ] <first step>
