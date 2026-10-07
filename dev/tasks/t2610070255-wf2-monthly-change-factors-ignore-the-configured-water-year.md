---
title: WF2 monthly change factors ignore the configured water year
type: todo-item
status: backlog
effort: 1
area: wf2
origin: t2610022259 WF2 lab P2 (2026-10-07)
queue:
created: 2026-10-07
updated: 2026-10-07
---

> [!note] Overview
> **What** — derive_point_datasets passes water_year_start to the annual change function but not to get_change_monthly_clim_proj, so the monthly table always slices January-start years.
> **Why** — Value-neutral for January configs (every seed today); a non-January project gets monthly factors over different years than its annual factors and its stated window.
> **Effort** — Small: thread the argument, trim to the same complete water years, add a known-answer test; main unknown is whether the stage-B hash re-fires existing projects.

## Progress

- [ ] Thread `water_year_start` into `get_change_monthly_clim_proj` and slice the same complete water years as the annual path.
- [ ] Known-answer test with an October water year; confirm January configs stay byte-identical.
