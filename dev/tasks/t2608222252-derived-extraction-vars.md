---
title: "Make climate extraction variables configurable"
type: todo-item
status: backlog
effort: 1
area: climate
origin: R14
queue:
created: 2026-08-22
updated: 2026-09-27
---

> [!note] Overview
> **What** — Climate extraction currently serves a fixed, model-oriented variable set. A future derived set would combine the selected model's forcing requirements, enabled workflows' requirements, and requested analysis variables.
> **Why** — Deriving requirements can avoid extracting unused variables while preserving the variables needed by each model and workflow; hard-coding a Wflow-only minimum would constrain future model support.
> **Effort** — Start when: A second model adapter is introduced, or a WF0-only use case demonstrates that extracting the fixed set has material cost.

## Progress

- [ ] Reassess once the start condition in Effort holds
