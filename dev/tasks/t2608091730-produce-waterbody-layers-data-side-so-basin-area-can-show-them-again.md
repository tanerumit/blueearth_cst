---
title: Produce waterbody layers data-side so basin_area can show them again
type: todo-item
status: backlog
effort: 1
area: plotting
queue:
created: 2026-08-09
updated: 2026-08-21
---

> [!note] Overview
> **What** — `basin_area.png` is the study-area map: elevation, the basin outline, rivers and gauges. It draws no lakes, reservoirs or glaciers, because the only thing that produces those layers is rule 1.08 `add_reservoirs_lakes_glaciers`, which runs inside the wflow model build and writes into the model's own `staticgeoms/`. The figure was moved off the model onto the shared spatial foundation (`data/spatial/`, ADR 0007), and that foundation carries no waterbodies. Fix: add a data-side producer that clips the same three catalog sources (`hydro_reservoirs`, `hydro_lakes`, `rgi`) to the basin and writes them into `data/spatial/geoms/`, then have the figure draw them.
> **Why** — On a basin with a major reservoir, the study-area map is arguably the one figure that must show it, and today it silently would not. The obvious shortcut — letting rule 1.08 also write into `data/spatial/` — is WRONG and is why this is its own item: a model rule writing there makes the shared foundation model-dependent, so the figure could no longer be drawn before a model exists, which is the property ADR 0007 bought.
> **Effort** — Small now that the design is settled (2026-08-11 and 2026-08-12 rulings below): one new producer following the `rivers` precedent, plus a three-line dict edit on the figure side. Rule 1.08 is not touched at all, so the model build and the baseline cannot move.

## Progress

**Unblocked 2026-08-21 (`360f5cb`) — and the recorded cause was wrong.** This
note carried `status: blocked` on the premise that the three source datasets
were missing from this machine and that the item "unblocks when that data root
is restored". The local absence was real; the diagnosis was not. `hydro_lakes`,
`hydro_reservoirs` and `rgi` were **never entries in `dev/scripts/stage_data.yml`**
— the only `hydrography/` entry was `rivers_lin2019`, which is exactly why the
local data root held nothing else. Three missing entries, nothing to restore.

All three are present at `source_root` (`P:/wflow_global/hydromt`), confirmed by
direct listing on 2026-08-21 rather than inferred from the staging run:
`hydrography/lakes/lake-db.gpkg`, `hydrography/reservoirs/reservoir-db.gpkg` and
`hydrography/rgi/rgi.gpkg` (691 MB). That check matters more than it looks —
see the `rgi` paragraph below.

Staged against the configured bbox:

| source | staged | features | of |
| --- | --- | --- | --- |
| `hydro_lakes` | 136 KB | 34 | 1 420 891 |
| `hydro_reservoirs` | 104 KB | 1 | 6 797 |
| `rgi` | — | no overlap | 216 429 |

**The 2026-08-12 finding this note recorded still stands, and it is the reason
the producer must distinguish two failures.** hydromt logs the RESOLVED URI
before opening it, then treats a missing source file exactly like an empty
result: a WF1 run showed all three "Reading …" lines followed by
`Skipping method, as no data has been found` while the files were provably
absent. So a "Reading X from Y" line is not evidence that Y exists. See
`t2608121606` — that conflation is a defect in its own right, and it is why the
producer written here must **fail loudly on a missing SOURCE while writing an
empty layer for an empty RESULT**. What `360f5cb` changes is only the
attribution: the absence came from an unstaged source, not a lost data root.

- [x] Decide whether the figure shows physical or modelled waterbodies — owner ruling 2026-08-11: **physical, unfiltered**. Rule 1.08 keeps naming the catalog sources exactly as today and is not modified
- [x] Decide which rule owns the data-side producer — owner ruling 2026-08-12: **1.03 `delineate_spatial_units`**
- [x] Stage the three sources locally so a producer can be written and its figure looked at — `360f5cb`
- [ ] Write the producer: clip the three sources to `basins`, write `geoms/{reservoirs,lakes,glaciers}.geojson`, register them in `spatial_catalog.yml` beside the existing layers
- [ ] Add the three layers to `SPATIAL_MAP_LAYERS` in `shared/plot_map.py` — `plot_raster_map` already accepts all three keys and needs no change
- [ ] Verify by rendering `basin_area` and looking at it. **Confirm first that the staged reservoir falls inside the basin POLYGON** — it was staged against the configured bbox and the producer clips to `basins`, so a bbox hit is not yet a basin hit. If it does, this fixture is a real verification case for the reservoir layer; if it does not, the reservoir layer is in the same position as `rgi` below and the check needs another basin
- [ ] Correct ADR 0007's consequences, which still describe the rejected "1.08 consumes them" plan

## What this fixture can and cannot verify

**`rgi` returns no overlap, and that is correct and permanent for an equatorial
basin — verified, not assumed.** "No overlap" and "source absent" are precisely
the two states the hydromt finding above says are indistinguishable from the
log, and `subset_vector` writing no local file is consistent with both. So the
source was checked independently: `rgi.gpkg` is present and 691 MB at
`source_root`. The empty result is therefore a real empty RESULT, not a missing
SOURCE. `subset_vector` reports SKIPPED "no overlap" and writes no local file,
so **the glacier layer cannot be validated on this fixture however the producer
is written.** A green suite says nothing about it. Writing an empty
`glaciers.geojson` and drawing nothing is the expected outcome here, and the
producer must reach it through the empty-RESULT branch rather than the
missing-SOURCE branch — which is the distinction the paragraph above exists to
protect. Validating the glacier path needs a basin that has ice.

**The reservoir is the case this task was opened for.** The one staged
`hydro_reservoirs` feature is a 13.7 km² hydroelectric impoundment in Gabon,
220 Mcm at 16 m mean depth — exactly the "major reservoir the study-area map
must not silently omit" that the Why above is written against, subject to the
inside-the-polygon check in the box above.

## Which rule produces them — RULED 2026-08-12: 1.03

**`1.03 delineate_spatial_units`**, and the deciding argument is not the one this
section framed it on. Consistency-versus-read-cost was never a fair trade,
because the WF1-only option reproduces the exact failure mode this whole task
exists to remove: `data/spatial/geoms/` would hold a different layer set
depending on which workflow last wrote it, while the figure reads that directory
by name — so a WF2-first project silently draws a study-area map with no
waterbodies, which is where we came in.

Two facts settled it, both measured on 2026-08-12:

- **The blast radius is real.** `SPATIAL_UNITS = spatial_units_rule(...)` is
  defined in all three Snakefiles (`Snakefile_climate_projections:228`,
  `Snakefile_climate_experiment:198`, and WF1) and splatted into a rule in each,
  so producing waterbodies in 1.03 does produce them in WF2 and WF3.
- **The read cost had not been measurable, and that is now only half-fixed.** It
  was recorded here that no number should be quoted, because the sources were
  absent and the local `rivers` source is a 0.5 MB test extract, so 1.03's
  measured 33.4 s said nothing about three real global geopackages. Two of the
  three are now staged — but the staged copies are basin-clipped extracts
  (136 KB / 104 KB), NOT the global tables, so they still measure nothing about
  a global read. Expectation, explicitly not a measurement: the clips are
  geometry-filtered and index-accelerated, so cost scales with
  features-in-basin rather than file size. Confirm against `source_root` before
  anyone relies on it.

## Original framing — kept for the record

Not a free choice, because the obvious home is shared:

- **1.03 `delineate_spatial_units`** already does exactly this for rivers
  (`spatial/products.py:726`, `catalog.get_geodataframe(rivers_source, geom=basins)`)
  and already writes `data/spatial/geoms/`. But its inputs/params/outputs are
  splatted from one `SPATIAL_UNITS` definition into **2.03 and 3.04 as well**, so
  producing waterbodies here produces them in WF2 and WF3 too, and charges every
  workflow the catalog read.
- **1.06 `prepare_spatial_maps`** is WF1-only, which avoids that cost — but then
  `data/spatial/geoms/` holds a different set of layers depending on which
  workflow last wrote it, and the figure reads that directory by name.

Consistency probably wins over the read cost, but the cost has not been measured
and the WF2/WF3 blast radius has not been checked.

## Refs

- `dev/decisions/0007-draw-basin-area-from-the-spatial-foundation.md` — records the move and names this as its known cost. Its consequences still say the fix is to have 1.08 consume the layers; the 2026-08-11 ruling supersedes that, and the ADR needs the one-line correction listed above.
- `dev/scripts/stage_data.yml` — the three entries added by `360f5cb`, with their field inventories. No `columns` filter on any of them: `deltares_data.yml` applies `rename` and `unit_mult` to named fields, and a column list would be a hand-maintained second copy of that mapping.
- `blueearth_cst/shared/plot_map.py::load_spatial_basin_layers` — its docstring points here.
- **`lakes` is a stale name model-side.** hydromt_wflow 1.0.2 has no `lakes` geom: `setup_lakes` became `setup_reservoirs_no_control`, and the geoms it writes are `meta_reservoirs_no_control`, `meta_reservoirs_simple_control` and `glaciers`. Data-side the names come from the SOURCES instead (`hydro_lakes` → `lakes`, `hydro_reservoirs` → `reservoirs`, `rgi` → `glaciers`) and are physically meaningful — a further argument for drawing the figure from the foundation rather than from the model's vocabulary.
- Rule 1.08 does far more than emit vectors: it derives rating curves, storage curves and demand parameters onto `staticmaps.nc`. Leaving it untouched is what keeps this task off the baseline.
