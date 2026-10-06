---
title: Port the wf0-lab spatial map revisions to WF1
type: todo-item
status: backlog
effort: 2
area: wf1
origin: wf0-lab cst_maps (2026-10-06)
queue:
created: 2026-10-06
updated: 2026-10-06
---

> [!note] Overview
> **What** — Bring the Liberia map revisions from wf0-lab cst_maps (lab commits d5e8326..861b348) into blueearth_cst/shared: GlobCover legend fix, furniture placement, on-map keys, inset, river and point styling, and <variable>_basin file names for rule 1.11.
> **Why** — Rule 1.11 labels GlobCover land cover with Copernicus codes (code 40 evergreen forest shows as Cropland), and the reviewed layout reads better on any basin shape.
> **Effort** — Five staged commits; main unknown is whether shared-style changes also apply to the WF0/WF2 climate maps that draw through cartographic_map.

## Progress

Brief: [task-brief.md](t2610061951/task-brief.md).

- [x] GlobCover land-cover class table chosen by layer source (`cc834f8e`).
- [x] Placement, inset, keys and styling as `cartographic_map.PROFILES["spatial"]` (`5fa3909c`); default-path renders pixel-identical to main.
- [x] Rule 1.11 figures opt into the profile; subbasin palette, LAI classes, legend titles (`5684e04c`); Liberia renders match the lab set.
- [x] Rename rule 1.11 outputs to `<variable>_basin` with a migration note (`1a2bf137`).
- [ ] Merge gates on `feat/wf0-spatial-map-improvements` (session-3): test-fast, test-full, test-e2e.
- [ ] Land on main (owner approval).

## Decisions

- 2026-10-06, Gate 1 (taken without a pause on the owner's "do not stop"): the new style stays on rule 1.11's figures only. It is an opt-in profile (`profile="spatial"`); WF0 climate, WF2 projection and forcing maps keep today's defaults.
- The brief's separate parameter-refactor commit was folded into the profile design (4 commits instead of 5); the lab's constant rebinding survives only as the scoped `_Overrides` behind a named profile.
- Unknown land-cover sources draw unclassified with a warning rather than borrowing the Copernicus table.
- The rename's migration note lives in the task folder (`t2610061951/migration_spatial_map_names.md`): there is no milestone folder for it.
