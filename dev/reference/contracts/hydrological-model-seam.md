# Contract: hydrological-model seam (HM-1 .. HM-7)

> **Genre:** dev-facing interchange contract. **Audience:** a future *swapper* —
> someone replacing Wflow-SBM with an alternative hydrological engine, or the R6
> model-flexibility work — read end-to-end. Not an end-user doc (hence `dev/`,
> not `docs/`; precedent `dev/reference/workflows/climate_experiment.md`).
> **Source of record:** `dev/milestones/p32b/interchange-contracts-design.md` (ACCEPTED
> 2026-07-24, §5.3 / §5.4 / §5.6 / §5.5). Every load-bearing fact below cites a
> Snakefile line, a script line, or an observed fixture artifact; do not add a
> contract fact that is not so grounded.

## Scope and method

The **hydrological-model seam** spans `build_model.smk` (wf1 build) and
`simulate_system.smk` through its mandatory runner (wf4 run) — the point where the hydrological
engine could be swapped without re-architecting the pipeline. Wflow-SBM (built by
hydromt) is the current occupant, but **this contract is model-agnostic**: it
pins what the pipeline hands *in* (forcing + static grid + run config) and
expects *out* (discharge CSVs → response surface), not Wflow's physics.

**Grounded in** the fixture tree `test_case/test_local` (era5 branch,
`test_case/project_config_baseline.yml`) inspected with xarray, the base
vs per-cst `wflow_sbm.toml` diff, and the wf1/wf4 rules + scripts.

**CST-scope disclaimer (the governing constraint; `AGENTS.md` Hard
Constraints).** For `staticmaps.nc` and `wflow_sbm.toml` we pin **only the
names/fields OUR code and the run TOML reference** — this is *pinned-as-reliance*
on a consumed upstream schema, NOT a re-specification of the wflow static-grid
schema or the TOML physics parameterization. The remaining ~39 staticmaps
variables and the physics value blocks are labelled **"wflow schema, consumed
verbatim, unpinned"**. The validators *read* upstream artifacts to check OUR
reliance; they never assert upstream correctness. The numeric outlet id in a
gauge column (`Q_130000086`) is wflow's outlets-map cell value — its derivation
stays **wflow-owned**, recorded as reliance, never asserted (C3 boundary, HM-4→
HM-5→HM-7 invariant below).

**Fixture branch = era5.** Wflow-side contracts here are era5-grounded.

**Contract-surface tiers** (design §5.1): (1) **Pinned** — a structural fact a
swap MUST reproduce; (2) **Pinned-as-reliance** — OUR consumed/rewritten subset
of the upstream staticmaps/TOML schema; (3) **Deliberately unpinned** — internal
detail (physics blocks, state-variable schema, provenance attrs).

Per-artifact schema (design §5.4): *artifact id · path pattern · producer rule ·
consumer rule(s) · dims · coords · data_vars · CRS · time axis/calendar · naming
pattern · temp() lifecycle · pinned surface · deliberately unpinned · validator*.
Rendered one subsection per artifact.

---

## HM-1 — static grid (staticmaps.nc)

- **path pattern:** `models/hydrology/wflow/staticmaps.nc`.
- **producer:** rule 1.06 `build_wflow_model` (hydromt build).
- **consumers:** wf1 rules 1.07 / 1.08 / 1.03 / 1.15; wf4 rule 4.04
  (`WflowSbmModel(root)`).
- **coords:** `(latitude, longitude)` `float64` + `spatial_ref` EPSG:4326 +
  `GeoTransform`.
- **pinned surface (pinned-as-reliance — OUR-referenced names only):**
  `subcatchment` (zone raster — plot aggregation, P3-2a §5.2); `land_elevation`
  (`m` — parity DEM, `hydromt_wflow/naming.py:10`); plus the TOML-referenced
  `local_drain_direction`, `river_mask`, `outlets`, and the `[input.static]`
  name set the run resolves. **Grid definition** (the `(lat, lon)` axes +
  `GeoTransform`) is pinned as the **co-registration target forcing must match**.
- **temp() lifecycle:** not `temp()`.
- **deliberately unpinned:** the **~39 unpinned wflow vars** — the fixture
  `staticmaps.nc` has **44 data_vars total**, minus the pinned OUR-referenced set
  (`vegetation_*`, `soil_*`, `meta_*`, `river_*` beyond mask) — **wflow schema,
  consumed verbatim, unpinned** (design arch-6).
- **validator:** `validate_hm1`.

## HM-2 — Wflow forcing (inmaps)

- **path pattern:** `models/hydrology/wflow/forcing/inmaps_historical.nc` (wf1
  forcing); wf4 twin `<exp>/hydrology/wflow/forcing/inmaps_run_<run_id>.nc`
  (= WG-6 on the weather-generator seam). R07 B5 files the wf4 twin on the
  HYDROLOGY side because it is model-grid forcing, symmetric with the wf1
  path above.
- **producer → consumer:** rule 1.09 `add_climate_forcing` (hydromt update) → rule 1.13
  `run_wflow`; wf4 rule 4.04 → rule 4.05.
- **dims:** `(time, latitude, longitude)` on the **model grid** (`float64`
  lat/lon matching HM-1).
- **data_vars:** exactly `precip`, `pet`, `temp` — all `float32`, each
  `grid_mapping=spatial_ref`.
- **CRS / grid:** `spatial_ref` EPSG:4326 + `GeoTransform`.
- **time axis/calendar:** daily `proleptic_gregorian` (wf1). *(wf4 forcing axis
  is moved to `standard` — see HM-4.)*
- **pinned surface:** the dims, the model-grid `(lat, lon)`, and the **variable
  names** `precip` / `pet` / `temp` — the names are the consumer contract: they
  are the RHS values the TOML `[input.forcing]` block maps to (HM-4).
- **temp() lifecycle:** HM-2 wf1 `inmaps_historical.nc` — not `temp()`; the wf4
  twin (WG-6) — **`temp()`**, absent on the completed fixture.
- **UNITS NOT PINNED (design arch-2 / risk-4 / repo-3).** wflow is name-keyed, so
  no consumer reads the unit attr. **Observed attr layout** (recorded, asserted
  **only if present**): `precip` carries **both** `units='mm d**-1'` (plural) and
  `unit='mm'` (singular); `pet` `unit='mm'` (`units` absent); `temp`
  `unit='degree C.'` (`units` absent). The wflow-native values live under the
  `unit` **singular** key; the `units` plural key survives on `precip` only as an
  extraction leftover. Contrast WG-1, whose values are all under `units` plural.
- **deliberately unpinned:** **all forcing units** (`unit` / `units` attr
  values) — asserted-if-present, not required; `precip_fn` / `pet_method` /
  `temp_correction` provenance attrs.
- **validator:** `validate_hm2` (asserts unit attrs **only if present**, per the
  asserted-if-present semantics). Covers HM-2 wf1 `inmaps_historical.nc`
  (persists) and the WG-6 wf4 twin (temp(), skip-until-captured — see WG-6 /
  `validate_wg6` on the weather-generator seam).

## HM-3 — static vector geometries (staticgeoms)

- **path pattern:** `models/hydrology/wflow/staticgeoms/*` (`region.geojson`,
  `basins.geojson`, `outlets.geojson`, `rivers.geojson`, `outlet_index.csv`, …).
- **producer:** rule 1.06 side-effect + rules 1.08 / 1.10.
- **consumers:** wf1 plot rules; wf4 rule 3.08 (`region.geojson` via
  `ancient()`).
- **pinned surface (OUR-consumed vectors only):** `region.geojson` (basin extent
  polygon, EPSG:4326 — the wf4 extraction region + the `ancient()` DAG edge);
  `outlets.geojson` (gauge points → plots/outputs); `outlet_index.csv` (the
  `outlet position → subcatchment-ID` mapping, a `rule all` target). CRS
  EPSG:4326; geometry types (Polygon / Point).
- **temp() lifecycle:** not `temp()`.
- **deliberately unpinned:** the full attribute tables; the `basins` / `rivers` /
  `meta_*` layers we don't index.
- **validator:** `validate_hm3`.

### Which tree is authoritative — the six colliding basenames

`staticgeoms/` is **not** the authority on the basin. Six basenames exist in
both `data/spatial/geoms/` (ours, upstream of the build) and `staticgeoms/`
(hydromt's, written by `model.write()`), and **none of the six pairs holds the
same content**. Read the wrong one and the result is plausible rather than
obviously broken, which is what makes this worth writing down.

| basename | `data/spatial/geoms/` — AUTHORITATIVE for | `staticgeoms/` — AUTHORITATIVE for | relationship |
|---|---|---|---|
| `region` | the delineated basin | the model **grid extent** (a bounding box) | ours ⊆ theirs |
| `basins` | the basin as ONE polygon | hydromt's per-subbasin decomposition (`value` column) | same union area, different features |
| `rivers` | MERIT attributes (21 columns) | routing topology (`idx, idx_ds, pit, strord`) | different provenance |
| `subbasins` | — | — | true copy, either is correct |
| `catchments` | — | — | true copy, either is correct |
| `locations` | — | — | true copy, either is correct |

The `region` row is the one that surprises people, and it is not a defect on
either side: `GridComponent._region_data` returns `box(*self.bounds)`
(`hydromt/model/components/grid.py:269`, hydromt 1.3.1), so a rectangle is
hydromt's deliberate definition of "region" for a grid model. Both files are
hydromt products — ours comes from `parse_region_basin` via
`spatial/delineate_region.py`, theirs from `model.write()` — and `ours ⊆ theirs`
holds because the grid is built to circumscribe the delineated basin.

**Enforced, not merely documented.** `blueearth_cst/shared/spatial_geoms_parity.py`
asserts the RELATIONSHIP per layer — containment for `region`, tolerant
topological equality for the three copies, and explicit non-comparison for
`basins` / `rivers`, whose reasons it carries. It is a sibling of
`interchange_contracts` rather than a member: same `-> list[str]`,
parsed-objects-only, `-O`-safe invariants, but it pins a relationship BETWEEN
two trees rather than the shape of one artifact. `tests/test_spatial_geoms_parity.py`
runs it against the built fixture, which is what would notice a hydromt upgrade
that changed how the grid region is derived.

**Renaming is not the fix and is not available.** `staticgeoms/` is
hydromt_wflow's own output surface and off-limits by AGENTS.md's hard
constraint; renaming our side would touch `region_rule` / `spatial_units_rule`
in `snake_utils.py`, the seam most workflow commits already contend for. Board
item `t2608071203` (R9-1) records the full measurement and the options weighed.

## HM-4 — run configuration (wflow_sbm.toml)

- **path pattern:** `models/hydrology/wflow/wflow_sbm.toml` (base) and per-cst
  `<exp>/hydrology/wflow/config/run_<run_id>.toml`. The run TOMLs sit in
  their own `config/` directory beside `forcing/` and `output/`, so
  `input.path_forcing` is the sibling hop `../forcing/…` and
  `[state].path_output` / `[output.csv].path` are `../output/…`. `dir_output`
  stays `"."` and the hop rides in the pointers themselves
  (`snake_utils.member_pointer_base`). hydromt re-relativizes the absolute
  pointers on write -- none is hand-maintained.
- **producer:** tracked template / rule 4.04 rewrite.
- **consumer:** rule 1.13 `run_historical_simulation` / rule 4.05 `run_wflow_simulations` (`Wflow.run()`).
- **pinned surface (the TOML fields OUR code reads/rewrites — the wf4 rewrite
  sites, `downscale_climate_forcing.py:55-84` `setup_config`):**
  `[time].{calendar, starttime, endtime, timestepsecs}`, `dir_output`,
  `[state].{path_input, path_output}`, `[input].{path_static, path_forcing}`,
  `[output.csv].path`.
- **Rewrite-value facts (design arch-4, fixture-verified at
  `downscale_climate_forcing.py:55-84`):**
  - `time.timestepsecs = 86400`.
  - `time.calendar` rewritten to **`"standard"`** — distinct from the wf1 base +
    the HM-2 pin of `proleptic_gregorian`. The code comment (lines 57–61)
    grounds it: weathergenr writes `noleap`, and hydromt_wflow 1.x forcing
    validation would fail comparing `cftime.DatetimeNoLeap` vs
    `datetime.datetime`, so **both** the wf4 forcing time axis and the TOML are
    moved to `standard`.
  - `dir_output = "."` (flat, no `run_default/` subdir).
  - `state.path_output` is removed for WF4: its final state is unconsumed.
    `state.path_input` and `state.variables` remain for initialization.
    `validate_hm4(..., require_output_state=False)` validates this variant;
    WF1 retains the default requirement for a final-state pointer.
- **Also pinned (read-reliance):**
  - `[input.forcing]` — the block **keys are wflow CSDMS Standard Names** (e.g.
    `atmosphere_water__precipitation_volume_flux`,
    `land_surface_water__potential_evaporation_volume_flux`,
    `atmosphere_air__temperature`) and the **VALUES are the forcing netCDF
    variable names** `precip` / `pet` / `temp`. The tie to HM-2 is on the **RHS
    values**.
  - `[output.csv].column` entries `{header, map, parameter}` — drives HM-5 column
    identity.
  - `[model].cold_start__flag` (section verified against both the base and
    per-cst fixture TOMLs — the flag lives under `[model]`, not top-level).
- **temp() lifecycle:** not `temp()`.
- **deliberately unpinned:** all `[input.static]` physics value blocks, layer
  thicknesses, kinematic-wave params — **wflow physics, unpinned**.
- **validator:** `validate_hm4`.

## HM-5 — per-run discharge CSV (output.csv)

- **path pattern:** wf1 `models/hydrology/wflow/run_default/output.csv`; wf4
  `<exp>/hydrology/wflow/output/run_<run_id>.csv` — the realization index is
  in the file name, so one member is one filename in three flat directories (`config/`, `forcing/`,
  `output/`). This is the inverse of R07 B5.
- **producer:** rule 1.13 `run_historical_simulation` / rule 4.05 `run_wflow_simulations`.
- **consumers:** wf1 rule 1.15 plots; WF4 response inventory, then retained metric reduction.
- **pinned surface — column identity is config-driven, NOT a literal list:** a
  `time` index (ISO-8601, daily) + **one column per `[output.csv].column`
  entry**, named `<header>_<mapid>`. Fixture: `time,Q_130000086` (one gauge).
- **the single degree of freedom:** the gauge-column set flows **TOML
  `[output.csv].column` → `output_rlz` → q_indicators** as one degree of freedom — the
  key bounded-substitution invariant, checked end-to-end by
  `validate_hm_gauge_column_identity` (below).
- **Consumer-prefix reliance:** the Wflow response reader
  selects gauge columns by the **`Q_` prefix** and
  every other variable's columns by its `wflow_outputs.CODES` code plus a numeric
  subcatchment id (`subcatchment_columns`) — so the TOML `header` values are
  load-bearing **beyond mere identity**.

  **This reliance broke, undetected, and how it broke is the point.** 8bd51de
  (2026-08-10) changed the basin-average header from `<label>_basavg` to
  `<code>_<subcatchment>`; the consumer kept matching the retired spelling, found
  no column, and `continue`d — writing `aet_indicators.csv` and
  `recharge_indicators.csv` as a header and zero rows, with every rule green and
  nothing in any log. Three things had to fail together: the producer changed a
  header the consumer parses without either being a declared shared surface; the
  consumer treated "no column" as *skip* rather than *raise*; and
  `test_export_wflow_results.py`'s fixture wrote the `_basavg` header itself, so
  the unit suite agreed with the consumer and with nothing else. The matcher is
  keyed off `CODES` — the same table the model build writes the TOML from — and
  a requested variable with no matching column raised `MissingOutputColumnError`
  rather than emptying its table. That reducer was removed on 2026-09-25
  (t2609151037); WF4 now reduces the series its response inventory names. See also the `validate_hm7` note below: it has
  a "no rows" check that would have caught this, but is never invoked at run time.
- **temp() lifecycle:** SPLIT between wf1 and wf4. wf1 `output.csv` **is** `temp()`
  (rule 1.13): it is an intermediate feeding rule 1.14's derived per-variable
  tables and rule 1.15's metrics, and Snakemake drops it once both have run. A
  swapper must therefore treat the wf1 artifact as existing only *within* the
  run — `--notemp` is what materialises it, and the baseline procedure uses that
  flag for exactly this reason. The wf4 `output_rlz_*` CSVs still persist.
- **deliberately unpinned:** numeric discharge values (not a contract; they
  change per run).
- **validator:** `validate_hm5` (per-artifact column-identity); cross-file
  identity by the relational `validate_hm_gauge_column_identity`.

## HM-6a — wf1 warm state (persisted, no validator)

- **path pattern:** `models/hydrology/wflow/run_default/outstate/outstates.nc`.
- **producer → consumer:** rule 1.13 `run_historical_simulation` → **(nothing in-repo)**.
- **THIN — "named output sink, unconsumed."** Persisted on the fixture.
- **contract surface:** name + location only — which **HM-4 already pins** via
  `[state].path_output`. **No validator (design risk-1):** a standalone existence
  check would pad the green count without verifying an independent contract. Kept
  as a **doc row only**; existence guaranteed **transitively through HM-4**.
- **path derivation (design arch-3):** the on-disk path
  `run_default/outstate/outstates.nc` = base TOML `dir_output = "run_default"`
  **+** `[state].path_output = "outstate/outstates.nc"`. A swapper that changes
  `dir_output` moves this path with it.
- **temp() lifecycle:** not `temp()`.
- **deliberately unpinned:** the entire state-variable schema
  (`[state.variables]` — wflow-owned).
- **validator:** **none** (existence pinned transitively via HM-4).

## HM-6b — retired WF4 final-state output

WF4 no longer emits `outstates_rlz_<n>_st_<m>.nc`. The file was an unconsumed
temporary sink; removing `state.path_output` avoids writing it without changing
initialization or the simulation CSV. No cross-member state chaining exists.

`validate_hm6b` remains available for older captured state files, with its
synthetic schema checks. `--notemp` does not recreate this retired output.

## HM-7 — retained metric-set interchange

- **Path:** `<exp>/results/metric_sets/<short id>/<token>_indicators.csv` and
  `metric_run_lookup.csv`; the ready marker is
  `<exp>/_engine/metric_sets/<short id>/metrics.json` (`metric-set/2`), written
  last.
- **Producer:** `prepare_indicator_plan` resolves response-dependent declarations,
  units and references; `derive_system_indicators` publishes complete results.
- **Consumer:** terminal reporting, CST-API and notebooks. Readers validate
  `metrics.json` and its inventory before consuming tables
  (`metric_plan.read_metric_set`).
- **Header:** exactly `metric,location,run_group_id,value`; the lookup is
  exactly `run_group_id,grain,run_id`. IDs are text. `(metric, location,
  run_group_id)` keys are unique per table.
- **Membership:** the lookup equals the marker's `run_groups`. Grain `run` has
  exactly one group per collection run, named after it; grain `bundle` groups
  list their member runs. Every run belongs to the collection.
- **Coverage:** a table's locations equal the response inventory's locations
  for that variable, and each metric covers every location x every run group of
  its one grain. Metric names are not derivable independently of the tables in
  `/2`, so a whole missing metric is caught by the reader's digests, not here.
- **Values:** numeric; existing metric vocabulary, location spelling and
  publication precision stand. See [indicator glossary](../indicator-glossary.md).
- **Lifecycle:** immutable; `metrics.json` is published last. A changed metric
  request selects a new set without modifying native responses or prior sets.

`validate_hm7_v2` takes the marker, the parsed tables and lookup, the response
inventory's `series` and the collection's run ids. `validate_hm7` still
describes the retired `metric-set/1` surface (`unit_index.csv`, `unit_id`).

## HM-4 → HM-5 → HM-7 gauge-column identity

The model's `[output.csv].column` declarations determine native headers and
locations. The frozen independent response request determines the exact series
inventory; result tables cannot define their own expected locations. Native
header order determines the current first-gauge reference, and persisted ordinals
preserve it under reversed artifact or series enumeration. Empty response
families are refused. `validate_hm_gauge_column_identity` checks TOML/native
consistency; the response reader and metric-set validation carry it forward.

## HM-6 lifecycle

WF1 retains its warm-state output. The current simulation binding does not write
an unused per-run final state and does not chain states across scenarios.
`validate_hm6b` remains for captured historical states; `--notemp` cannot create
an output omitted by the binding. This pre-existing omission is preserved by
the R12 migration, as documented in the accepted P1/P2 evidence.

## Substitution and validation

A replacement simulator consumes a ready collection, implements its preparation
adapter, freezes model/settings/environment identity, and emits the declared
neutral responses with their retained inventory. Metrics-only reaches responses
through that inventory and cannot schedule the model or preparation code.
HydroMT/Wflow physics, schemas and parameter names remain upstream-owned.

`blueearth_cst/shared/interchange_contracts.py` owns the HM validators. HM-1/2/3
validate model grids, forcing and vectors; HM-4/5 validate the consumed TOML/native
surface. HM-6a has no state-schema validator. A missing temporary HM-2 artifact
means the on-disk check is unavailable, not successful.

```console
python scripts/simulate_system.py --config <project-config.yml> --target all --cores 3 -- --notemp
```

For retained-only reduction use `operation: metrics-only` and `--target simulations_and_indicators`.
Scientific preservation evidence and its source-branch limits are recorded in
[P2 acceptance](../../milestones/r12/implementation/evidence/p2/acceptance.md).
