# Post-R6 assessment — observation register

Live register of observations from the owner's own assessment and testing of the
repo **after the R6 structural refactor**. Opened 2026-07-25 against `3c8c2a9`
(`main`). Each row is one observation, from intake through triage to disposition.

**Scope and boundary.** This file owns the owner's post-R6 assessment
observations only. Items that survive triage and belong to a later milestone are
promoted to [`../followups.md`](../followups.md); items needing tracked,
multi-session work get a [`../TODO.md`](../TODO.md) row. Either way the
**Disposition** column keeps the pointer, so nothing lives in two registers. The
pre-existing `## Post-R6` entries already in `followups.md` (surfaced 2026-07-23
during R6 milestone validation) stay where they are — do not re-log them here.

**How to add a row.**

1. Append an index row with the next `O-nn` ID; record `Created`, `Rev` (short
   sha the observation was made against), and `Status: open`.
2. Add a matching detail block below with the exact command, configfile, and
   observed-vs-expected — enough for a future session to confirm the issue still
   applies before acting on it.
3. On any status change, update `Updated` and, once routed, `Disposition`.

**Status vocabulary:** `open` (logged, not yet triaged) · `triaged` (cause
understood, routed) · `fixed` (landed; put the sha in Disposition) ·
`wontfix` (accepted as-is, with a reason) · `not-reproducible` (does not
reproduce under current pins) · `by-design` (expected behaviour, not a defect).

**Kind:** `defect` · `regression` (worked before R6, broken after) ·
`docs` · `usability` · `performance` · `question` (needs a decision, not a fix).

---

## Index

| ID | Observation | Area | Kind | Severity | Created | Updated | Rev | Status | Disposition |
|---|---|---|---|---|---|---|---|---|---|
| O-01 | `basin_area.png` is weak as a figure: unreadable basemap, misleading DEM ramp, no scale bar / graticule / area | wf1 | usability | medium | 2026-07-25 | 2026-07-25 | `75eb4d6` | fixed | `e917a8e` — baseline re-recorded with it |
| O-02 | rule 1.12 `plot_map` needs **internet** at run time to produce `basin_area.png` | wf1 | defect | medium | 2026-07-25 | 2026-07-25 | `75eb4d6` | fixed | `e917a8e` — tile fetch removed |
| O-03 | lakes / reservoirs / glaciers appear **twice** in the `basin_area.png` legend | wf1 | defect | low | 2026-07-25 | 2026-07-25 | `75eb4d6` | fixed | `e917a8e` — legend de-duplicated by label |

Area labels are free-form; keep to the repo's vocabulary where one fits:
`wf1`/`model`, `wf2`/`projections`, `wf3`/`experiment`, `weathergen`, `shared`,
`config`, `tests`, `ci`, `env`, `docs`, `dev-tooling`.

Severity: `high` (blocks a workflow or produces wrong numbers) · `medium`
(works but wrong/awkward in a way users will hit) · `low` (cosmetic, noise,
wording).

---

## Details

### O-01 — `basin_area.png` is weak as a published figure

- **Created:** 2026-07-25 · **Rev:** `75eb4d6` · **Status:** fixed
- **Command:**
  ```powershell
  pixi run snakemake all -c 3 -s Snakefile_model_creation --configfile config/workflows/snake_config_model_test.yml
  # target: {project_dir}/plots/wflow_model_performance/basin_area.png  (rule 1.12 plot_map)
  ```
- **Observed:** seven distinct weaknesses in `blueearth_cst/shared/plot_map.py`:
  1. `cimgt.QuadtreeTiles()` at a hardcoded `zoom_level=10` renders as a grey
     blur over a ~0.2° basin — no context, competes with the DEM (see O-02 for
     the network side of this).
  2. DEM ramp `terrain[0.25:1]` starts at saturated green, read as vegetation
     rather than low elevation; a lowland basin becomes one flat green slab.
  3. `vmax` at the 0.98 quantile clipped the top cells to **white**, visually
     identical to masked no-data.
  4. No scale bar, no north arrow, and no basin area — on a figure named
     `basin_area.png`.
  5. Axis labels were raw decimal degrees, not a formatted graticule.
  6. Fixed `figsize=(10, 8)` regardless of basin aspect ratio → large dead
     margins; legend sat on top of the basin.
  7. `plt.style.use("seaborn-v0_8-whitegrid")` mutated global matplotlib state,
     leaking into any figure drawn later in the same interpreter.
- **Expected:** a self-contained, publication-usable basin map.
- **Notes:** predates R6 — the module dates from 2022 and R3 only wrapped it in
  a guarded function. Fixed by redesign on `feat/outputs-figures`: YlOrBr
  sequential ramp on the full data range with an explicit bad-value colour,
  neutral backdrop, geodesic scale bar, north arrow, formatted graticule,
  aspect-derived canvas, legend moved below the map, area in the title, styling
  confined to an `rc_context`. Baseline re-recorded (one line: `basin_area.png`
  286022 → 134828 bytes, 52.9% drift, intended — the drop is the removed raster
  tiles). Area label cross-checked against the model's own `meta_upstream_area`
  max: 219.54 km² computed vs 219.83 km² — 0.13%.

  Implementation note worth keeping: on a cartopy `GeoAxes` carrying a
  gridliner, matplotlib title auto-positioning resolves to `NaN` and the title
  **silently never renders**. An explicit `y=` on `set_title` is required.

### O-02 — rule 1.12 `plot_map` required internet at run time

- **Created:** 2026-07-25 · **Rev:** `75eb4d6` · **Status:** fixed
- **Observed:** `plot_map.py` called `ax.add_image(cimgt.QuadtreeTiles(), 10)`,
  which fetches map tiles over the network on every run. Workflow 1 otherwise
  runs entirely from local catalogs, so this was the only rule with a hidden
  runtime network dependency — and an offline or firewalled run would fail (or
  hang) in a rule that produces nothing but a plot.
- **Expected:** wf1 completes offline from local data.
- **Notes:** independent of the redesign request but fixed by it, since the
  basemap was dropped. Removing it also makes the figure deterministic — tile
  servers can change their imagery between runs.

### O-03 — duplicate waterbody entries in the `basin_area.png` legend

- **Created:** 2026-07-25 · **Rev:** `75eb4d6` · **Status:** fixed
- **Observed:** on a basin carrying lakes / reservoirs / glaciers, each appeared
  **twice** in the legend. The code passed `label=` into
  `geoms[...].plot(**kwargs)` *and* appended a manual `mpatches.Patch(**kwargs)`
  as a workaround for geopandas#660; current geopandas registers polygon
  handles itself, so the workaround now double-counts.
- **Expected:** one legend entry per layer.
- **Notes:** pre-existing, and **invisible in `examples/test_local`** — that
  fixture has no lakes/reservoirs/glaciers and `output_locations: None`, so
  those branches are no-ops in every local render. Found by injecting synthetic
  waterbody + gauge layers into `mod.geoms.data` and re-rendering. Fixed by
  de-duplicating legend handles by label.

  **Standing caveat for future figure work:** the fixture cannot exercise the
  waterbody, gauge-marker, or `station_name` annotation paths. Any change to
  those branches needs a synthetic-geoms render to count as verified.

---

## Closure

When the assessment pass is done: promote surviving items to `followups.md` /
`TODO.md`, fill every `Disposition` cell, and add a short outcome summary at the
top of this section (what was checked, what held, what did not). This file then
stays as the durable record of the pass — it is a `dev/reviews/` artifact, not a
working note, so it is not deleted at closure.
