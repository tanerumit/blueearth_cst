---
title: Rule 1.06 consumes river_attributes without declaring it, so nothing schedules 1.03
type: todo-item
status: backlog
branch:
effort: 1
area: wf1 / DAG
origin: R13 baseline pass 1 (2026-08-21)
queue:
created: 2026-08-22
updated: 2026-08-22
---

> [!note] Overview
> **What** — Rule 1.06 `prepare_spatial_maps` reads `data/spatial/geoms/river_attributes.geojson` through the spatial catalog at runtime but does not name it in its `input:` block. The file IS a declared output of rule 1.03 `delineate_spatial_units` (`blueearth_cst/shared/snake_utils.py`, inside the outputs dict) yet appears in no `.smk` file at all, so no DAG edge demands it.
> **Why** — A rule runs only when a needed output is missing. On any project whose spatial layer predates `c6d35ba` (2026-08-17, which introduced the product) every *declared* output already exists, so Snakemake never schedules 1.03 and 1.06 dies with `hydromt.error.NoDataException: Resolver 'convention' found no files at data/spatial/geoms/river_attributes.geojson`. That reads as bad or missing DATA, not as a missing dependency, which is the expensive part.
> **Effort** — small

## Where it was found

Blocked step 1 of R13's baseline pass 1 on the primary checkout, 2026-08-21
22:27. Not R13's: the branch touches neither `blueearth_cst/spatial/products.py`
nor the relevant part of `snake_utils.py`. Full context in
`dev/milestones/r13/baseline-pass-1-result.md`.

## The fix

One line — add to rule 1.06's `input:` block in `build_model.smk`:

```python
river_attributes = SPATIAL_UNITS.outputs["river_attributes"],
```

Belongs on `main`, not on `feat/r13-config-tiers`.

## Workaround until then

```powershell
snakemake -c 3 -s build_model.smk --configfile $cfg `
    --forcerun delineate_spatial_units --until delineate_spatial_units
```

Recorded in `dev/milestones/r13/baseline-pass-runbook.md` step 1.

## Verified side effects of forcing 1.03

Regenerating the geoms moves `rivers.geojson` (`31235e95…` -> `9c35b9d1…`; the
new definition resolves to "3 reach(es) at 32 km2, reaching all 4 location(s)")
and adds the missing `river_attributes.geojson`. Everything else is
byte-identical: `basins`, `catchments`, `subbasins`, `locations`, `region`,
`location_registry.csv`. After a full WF1 rebuild through the changed network,
`staticmaps.nc` (`74246b97…`) and `wflow_sbm.toml` (`351c3ea0…`) are unchanged
and the wf1 discharge target still matches the baseline manifest. **The changed
river network reaches no number on this fixture** — worth re-checking on a basin
with a denser network before assuming it generalizes.

It does rewrite `forcing/inmaps_historical.nc`, which trips rule 3.06's
`ModelDriftError` on an existing experiment. Byte-level, not numeric.
