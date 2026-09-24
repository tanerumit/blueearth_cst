---
title: Rename WF3 generation rules 3.07-3.10 to domain names
type: todo-item
status: backlog
branch: wf3-improvements
effort: 1
area: wf3
origin: wf3-improvements
queue:
created: 2026-09-24
updated: 2026-09-24
---

> [!note] Overview
> **What** — Rename generate_roots_v2 -> generate_weather_realizations, transform_member_v2 -> perturb_climate_realizations, retain_series_v2 -> store_scenario_series, publish_collection_v2 -> publish_scenario_collection. Keep numbers 3.07-3.10; add store_/publish_ to the naming.md 8b verb table; sweep live references (docs, rule-index, tests, log/benchmark names) and add a migration note. Held to bundle with other WF3 changes; settle 3.09's name together with removing the retain copy step.
> **Why** — The _v2 names describe code history, not the domain, so they are opaque to domain experts; the first two restore the pre-v2 rule names.
> **Effort** — small

## Progress

- [ ] <first step>
