---
title: "Make climate extraction variables configurable"
type: todo-item
status: backlog
effort: 1
area: climate
origin: R14
queue: 14
created: 2026-08-22
updated: 2026-10-05
---

> [!note] Overview
> **What changes** — Climate extraction currently serves a fixed, model-oriented variable set. A future derived set would combine the selected model's forcing requirements, enabled workflows' requirements, and requested analysis variables.
> **Why it matters** — Deriving requirements can avoid extracting unused variables while preserving the variables needed by each model and workflow; hard-coding a Wflow-only minimum would constrain future model support.
> **What it takes** — Pick it up when a second model adapter arrives, or when a WF0-only use shows that extracting the fixed set of variables has a real cost.

## Progress

- [ ] Check whether the condition in What it takes has happened
