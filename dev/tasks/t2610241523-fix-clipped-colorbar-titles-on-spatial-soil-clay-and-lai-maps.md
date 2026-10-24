---
title: Fix clipped colorbar titles on spatial soil-clay and LAI maps
type: todo-item
status: backlog
effort: 1
area: plotting
origin: t2610082103
queue:
created: 2026-10-24
updated: 2026-10-24
---

> [!note] Overview
> **What changes** — WF1 spatial maps for soil clay and LAI show their full colorbar titles inside the
> saved figure.
> **Why it matters** — The titles are cropped in current renders, so the plotted quantity and units are
> partly unreadable.
> **What it takes** — A small layout fix in the spatial map renderer, verified by rendering the affected
> PNGs from rapid outputs.

## Progress

- [ ] Reproduce the clipping on rapid WF1 spatial maps.
- [ ] Fix the colorbar title layout without changing other maps.
- [ ] Publish the before/after renders for visual review.

Next: render the soil-clay and LAI maps from rapid outputs.
