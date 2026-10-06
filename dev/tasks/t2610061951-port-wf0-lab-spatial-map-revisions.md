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

- [ ] GlobCover land-cover class table chosen by layer source (correctness fix, lands alone).
- [ ] Scale bar, inset and on-map key placement with collision check and padding fallback.
- [ ] Gate 1: owner decides whether shared-style changes extend beyond rule 1.11's figures.
- [ ] Keys and styling (on-map keys, plain colourbar ends, bold titles, river ramp, points, subbasins, LAI).
- [ ] Replace the lab's constant-rebinding with explicit parameters (no render change).
- [ ] Rename rule 1.11 outputs to `<variable>_basin` with a migration note.
