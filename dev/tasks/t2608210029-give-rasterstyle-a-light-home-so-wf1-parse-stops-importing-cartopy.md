---
title: Give RasterStyle a light home so WF1 parse stops importing cartopy
type: todo-item
status: backlog
effort: 1
area: performance / workflow parse
origin: t2608202307 follow-up
queue:
created: 2026-08-21
updated: 2026-08-21
---

> [!note] Overview
> **What** — plot_spatial_maps builds five module-level RasterStyle constants, so it must import shared/cartographic_map (cartopy) at import time; build_model.smk imports it at PARSE time for figure_paths alone. Move RasterStyle to a light module both import, and defer the rest.
> **Why** — WF1's dry-run parse is 4.27s and pulls cartopy, geopandas, xarray and matplotlib; the other three workflows are now 1.6-2.7s and WF0 pulls no heavy library at all. t2608202307 could not do this: cartographic_map.py was outside its declared write scope, and the registry representation cannot change instead because tests read figure.style as a real RasterStyle (.label, _style_colormap).
> **Effort** — small

## Progress

- [ ] Give `RasterStyle` a light home both `cartographic_map.py` and
      `plot_spatial_maps.py` import; re-export from `cartographic_map` so no
      public name moves.
- [ ] Defer `_mask_nodata` / `plot_raster_map` into the drawing functions;
      source `RASTER_DPI` from `shared/plot_style.py`, which already owns it.

**Before starting, read t2608202307's "What ruff bought, and the hole it left".**
If this work adds a `if TYPE_CHECKING:` guard -- and deferring imports usually
forces one, because it strands the annotations -- note that F821 does NOT catch a
runtime use of a guarded name. `TC004` does, and is enabled repo-wide since
t2608210029b. Do not re-derive that the hard way.
