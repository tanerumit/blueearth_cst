---
title: Give the analysis variable set a config surface (R14 C-48)
type: todo-item
status: backlog
effort: 1
area: wf0 / wf1 climate figures
origin: R14
queue:
created: 2026-08-24
updated: 2026-08-24
---

> [!note] Overview
> **What** — C-48 proposed a config surface for the ANALYSIS variable set (CLIMATE_VARS, climate_figures.py:83), selecting from a registry and defaulting to today's precip/temp/pet. Withdrawn from R14 2026-08-24 (design D-7.10): source_climate_vars is imported by BOTH analyze_climate.smk:18 and build_model.smk:17, so it is a two-workflow read and R13's seam rule forces it into T1 - where the C-47 charter excludes it as a USE of the climate record rather than a fact about it. Its S2 class (reporting) lost its section to C-77.
> **Why** — It is a textbook P1 case: a user-facing default discoverable only by reading source. It is also the ONLY register row classed non-breaking and additive, so unlike every other R14 row it does not need the migration bundle and can land at any time. Landing it needs one of: amend the C-47 charter to admit a use, or introduce a T1 section S2 has a class for. Neither is R14's to decide under a waived review loop.
> **Effort** — small

## Progress

- [ ] <first step>
