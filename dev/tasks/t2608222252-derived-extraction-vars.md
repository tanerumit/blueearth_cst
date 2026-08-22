---
title: Make the climate extraction variable set derived and configurable
type: todo-item
status: backlog
effort: 2
area: wf0 / wf1 climate store
origin: R14
queue:
created: 2026-08-22
updated: 2026-08-22
---

> [!note] Overview
> **What** — Make the climate store's EXTRACTION variable set configurable, so a run does not download variables nothing consumes. Derived rather than declared: extract = union(selected model's forcing requirements, each enabled workflow's requirements, variables the user asked to analyse). Requires the model adapter to declare its own requirements, so it is coupled to the model-boundary work. Until it lands, R14's key refuses anything narrower than the current full set.
> **Why** — climate_store_rule carries no variable parameter at all, so the extraction set is fixed in code per source branch and built to serve WF1. A user running only WF0 to compare datasets still pays for the wflow forcing core. A declared list cannot be the fix - dropping radiation or pressure breaks PET and therefore the model - and a hardcoded mandatory core would encode wflow's requirements in our schema, which N7 forbids now that a second model is anticipated.
> **Effort** — large

## Progress

- [ ] <first step>
