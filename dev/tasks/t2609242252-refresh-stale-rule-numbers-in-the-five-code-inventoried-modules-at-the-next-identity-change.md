---
title: Refresh stale rule numbers in the five code-inventoried modules at the next identity change
type: todo-item
status: backlog
effort: 1
area: workflows
origin: rule naming bundle (2026-09-24)
queue:
created: 2026-09-24
updated: 2026-09-24
---

> [!note] Overview
> **What** — Comments in extract_historical_climate.py, downscale_climate_forcing.py, metric_plan.py, prepare_cst_parameters.py and prepare_weathergen_config.py still cite pre-2026-09-24 rule numbers and names. They were left byte-identical because their bytes feed collection, simulation, metric-plan and climate-store identities.
> **Why** — A comment-only edit would mint new identities; fold the refresh into the next change that moves those identities anyway.
> **Effort** — small

## Progress

- [x] 2026-09-25: downscale_climate_forcing.py, metric_plan.py,
      prepare_cst_parameters.py and prepare_weathergen_config.py refreshed, in
      the bundle whose other commits already move the collection, simulation
      and metric-plan identities.
- [ ] extract_historical_climate.py -- fingerprinted on its OWN bytes
      (`CLIMATE_STORE_SCRIPT`, `extraction_sha256`), so a comment edit forces a
      climate-store re-extraction nothing else in that bundle needed. Still
      waits for a change that moves the climate-store identity.
