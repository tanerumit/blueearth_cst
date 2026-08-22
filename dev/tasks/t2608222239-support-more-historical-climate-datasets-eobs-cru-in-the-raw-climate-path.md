---
title: Support more historical climate datasets (eobs, cru) in the raw-climate path
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
> **What** — Extend the wf0/wf1 raw-climate path beyond era5, chirps and chirps_global. _SUPPORTED_SOURCES (analyze_climate.smk:120) refuses anything else at parse time, and build_model.smk:148 refuses eobs on the wf1 path specifically. Candidates named by the owner: eobs, cru.
> **Why** — R14's climate.sources makes a multi-dataset candidate set expressible in config, but the SHAPE is general while the supported SET is bounded and smaller. Without this the new config can name datasets the pipeline cannot extract, and the refusal arrives at parse time with no way forward. Capability work, deliberately kept out of the R14 register so the config milestone does not imply it ships datasets.
> **Effort** — large

## Progress

- [ ] <first step>
