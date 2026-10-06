Task Brief — Port the wf0-lab spatial map revisions to WF1

### Context

- Rules: `AGENTS.md` (validation ladder, figure gate, naming), `dev/reference/naming.md` §7–§8,
  `dev/reference/wf0-figure-filename-rule.md`.
- Source of the changes: `C:\Users\taner\workspace\wf0-lab`, package `cst_maps/`. It is a copy of
  `blueearth_cst/shared/{cartographic_map,plot_map,plot_spatial_maps,raster_style,plot_style}.py` taken at
  `70fc6173`, revised in lab commits `d5e8326..861b348`. Read it with
  `git -C <wf0-lab> diff d5e8326 861b348 -- cst_maps`. Lab-only files: `_shims.py`, `__main__.py`,
  `positron.py`.
- No upstream drift between `70fc6173` and `7704e7e2` in those five modules (2026-10-06,
  `git log 70fc6173..HEAD -- blueearth_cst/shared/<module>.py`). Re-check before starting; merge, do not
  overwrite, if it has moved.
- Reviewed renders: before = `wf0-lab/outputs/cst-maps/liberia/baseline/`, after =
  `wf0-lab/outputs/cst-maps/liberia/after/`, from the archived case
  `cst-cases/runs/archive/liberia-hydropower-outlet/data/spatial`. Reviewed page:
  https://claude.ai/artifact/93RY4iqWNBZxVYcUxs4hBx
- `cartographic_map.py` and `plot_style.py` are shared: `climate_analysis/climate_figures.py`,
  `projections/projection_figures.py`, `model/plot_map_forcing.py` and others draw through them.

### Goal

Rule 1.11's spatial map set renders as the reviewed lab "after" set, under the new file names, with every
other figure family unchanged unless Gate 1 extends a change to it.

### Non-goals

- The OpenFreeMap Positron background (`positron.py`, `mapbox-vector-tile`, network fetch). It stays a lab
  option; it would need a new-dependency approval.
- Soil-map palette or class revisions not yet made in the lab.
- The pre-existing lab test failure (`tests/test_spatial.py`); it belongs to the WF0 lab code.

### Allowed scope

- **Permitted:** `blueearth_cst/shared/{cartographic_map,plot_map,plot_spatial_maps}.py`, `build_model.smk`
  rule 1.11 outputs, tests covering these modules, `docs/` pages naming the map files, a migration note
  `dev/<milestone>/migration_spatial_map_names.md` (milestone folder: `<PLACEHOLDER>`).
- **Approval-gated (Gate 1):** any change that alters figures outside rule 1.11 — `plot_style.py`, and
  shared defaults in `cartographic_map.py` used by climate, projection or forcing maps.
- **Forbidden:** `config/basemap/` data, `pixi.toml` / `pixi.lock`, `test_case/` outputs.

### Required changes (checklist)

1. **GlobCover class table.** `land_cover_classes(layer)` picks the table from `layer.attrs["source"]`;
   GlobCover 2009 codes with the official legend colours; Copernicus table kept for its own data.
2. **Furniture placement.** Scale bar: preference `("lower left", "lower right")`, footprint
   collision-checked against basin plus gauges, south padding fallback with a printed note. Inset and
   on-map key: same rule for the upper corners, north padding. North arrow on the free upper side. Remove
   the corner-occupancy helpers this replaces.
3. **Inset.** On the map, flush corner, width 0.32 shrinking to 0.28 before padding; zoom target 0.12;
   ladder starting at 3°; red frame-extent rectangle, no basin fill; up to 8 cities (rank ≤ 4) whose
   labels fit. Kept only on `elevation_basin` and `subbasins`.
4. **Keys.** Thematic maps: no inset or side panel, key in an upper corner (fonts × 0.9, bar 30% of map
   height, sized by measuring it first). `elevation_basin`: side-panel colourbar, 40% high,
   bottom-aligned. No triangular colourbar ends. Bold key titles. Frameless legends with two-line labels,
   titled by quantity. "Unclassified" without codes. `vector_legend` defaults to `False`. `subbasins`: no
   key.
5. **Styling.** Rivers stepped by Strahler order (`RIVER_ORDER_STEPS`, order column `strord` or `order`),
   thin first, round caps. Points: purple `#6a3d9a` diamonds. Subbasins: Set3 minus grey, 60% opacity,
   neighbour-aware colours. LAI: levels 0–6 step 1, label "Mean leaf area index". Full-width maps scale
   text by the map-width ratio.
6. **Refactor, not copy.** The lab switches key size, fonts and layout width by temporarily rebinding
   module constants (`_Overrides`). Replace that with explicit parameters before landing.
7. **Rename outputs** per the table below, in `plot_spatial_maps.SPATIAL_MAP_FIGURES`, `plot_map`'s
   `elevation_basin.png`, rule 1.11's declared outputs, tests and docs; write the migration note.

| Old | New |
|---|---|
| `basin_area` | `elevation_basin` |
| `subbasin_delineation` | `subbasins` |
| `land_cover` | `land_cover_basin` |
| `leaf_area_index_annual_mean` | `lai_clim_basin` |
| `soil_<property>_topsoil` (6) | `soil_<property>_basin` |
| `soil_depth_to_bedrock` | `soil_depth_to_bedrock_basin` |

### Commit plan

| Commit | Paths | Invariant |
|---|---|---|
| 1. GlobCover legend fix | `plot_spatial_maps.py`, its test | Only `land_cover` changes; it is a correctness fix and lands alone |
| 2. Placement + inset | `cartographic_map.py`, tests | Scale bar, inset and key never intersect basin or gauges |
| 3. Keys and styling | `cartographic_map.py`, `plot_spatial_maps.py`, `plot_map.py`, tests | Rule 1.11 figures only, unless Gate 1 says otherwise |
| 4. Parameter refactor | `cartographic_map.py` | No render change against commit 3 |
| 5. Output rename | `plot_spatial_maps.py`, `plot_map.py`, `build_model.smk`, tests, docs, migration note | Declared outputs and writers match; no old name remains live |

### Validation

1. Narrow, per edit: `pytest tests/test_plot_spatial_maps.py` plus tests for `plot_map` and
   `cartographic_map` (`<PLACEHOLDER: list from git grep -l "cartographic_map\|plot_map" tests>`).
2. New tests: GlobCover code 40 maps to "Broadleaved evergreen forest", never "Cropland"; placement returns
   a clear corner or pads for a frame-filling synthetic basin, and the padding cap is reported; no
   triangular colourbar end (`extend == "neither"`).
3. Per commit touching a rule or signature: `pytest tests/test_cli.py`; `pixi run lint`,
   `pixi run format-check`.
4. Figure gate, per commit 1–3: render rule 1.11 on `test_case/project_config_rapid.yml` and on the
   Liberia archive (`dev/scripts/preview_spatial_maps.py --project-dir <case>`); publish the PNGs as an
   Artifact and compare with the lab "after" set. Falsifier: any visible difference not explained by the
   refactor.
5. Commit 4 falsifier: render before and after the refactor; a pixel difference disproves "no render
   change".
6. Commit 5 falsifier: `snakemake -s build_model.smk --configfile <cfg> --dry-run` passes, and
   `git grep -n "basin_area\|subbasin_delineation\|leaf_area_index_annual_mean\|_topsoil"` returns no live
   reference outside sealed records.
7. Before merging: `pixi run test-fast`; `pixi run test-full` (shared/ touched); `pixi run test-e2e`
   (rule 1.11 outputs changed).

### Acceptance criteria

- Rule 1.11 writes the 11 new file names and nothing under the old ones.
- Rendered Liberia maps match the lab "after" set visually.
- Climate, projection and forcing maps are unchanged unless Gate 1 approved a change.
- Rollback: revert the branch if test-e2e fails on rule 1.11 or a non-1.11 figure family changes without
  Gate 1.

### Output requirements

- Per commit: rungs run, what each caught, render Artifact link.
- Results delta: the land-cover map's labels change, a correctness fix; all other changes are presentation
  only; no numeric output changes.

### Task constraints

- Gate 1 — PAUSE before commit 3: the owner decides whether the style changes (no triangle ends, bold
  titles, river ramp, purple points, frameless legends) also apply to the WF0 climate, WF2 projection and
  forcing maps, or stay on rule 1.11's figures.
- Follow the repository's lane protocol; no push without an explicit request.
