---
title: "Make climate extraction variables configurable"
type: watch-item
area: wf0 / wf1 climate store
origin: R14
created: 2026-08-22
updated: 2026-09-27
---

> [!note] Overview
> **What** — Climate extraction currently serves a fixed, model-oriented variable set. A future derived set would combine the selected model's forcing requirements, enabled workflows' requirements, and requested analysis variables.
> **Why** — Deriving requirements can avoid extracting unused variables while preserving the variables needed by each model and workflow; hard-coding a Wflow-only minimum would constrain future model support.
> **Trigger** — A second model adapter is introduced, or a WF0-only use case demonstrates that extracting the fixed set has material cost.