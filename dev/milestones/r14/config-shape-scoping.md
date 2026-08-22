# Scoping — R14 config shape (naming, nesting, sections)

- Run: `r14-config-shape` · started 2026-08-22 · driver: interactive session
  (primary checkout → `session-1` lane)
- **Status: SCOPING / preparation exercise.** Not a design, not accepted, no
  implementation authorized. The next artifact is an intake + design under the
  `design-review-loop`, on the R13 pattern (`dev/milestones/r13/`).
- Predecessor: **R13 config tiers** (ACCEPTED 2026-08-21). R13 split the
  monolithic project config into T1 + one file per workflow. R14 reshapes
  *within* that split: it moves and renames keys, and does not re-litigate the
  tier decision, the path-reference composition, or the single `--configfile`
  CLI contract.

## ID convention

| prefix | means | example |
|---|---|---|
| `S1`–`S6` | proposed **structure** policy rule | `S2` — three identity classes |
| `N1`–`N6` | proposed **naming** policy rule | `N4` — `{start, end}` windows |
| `C-01`–`C-38` | one proposed **change**, individually referable | `C-07` — delete `static_dir` |
| `Q-A`–`Q-F` | **open question**, blocks a change | `Q-A` — `project.dir` vs `project_dir` |

`C-nn` (hyphenated) is this milestone's namespace and is deliberately distinct
from the un-hyphenated `Cnn` finding IDs used in `dev/reviews/` records.

## Change request (verbatim, owner, 2026-08-22)

> A few question reg. config.ymls:
>
> Main config.yml:
>
> - does it make sense to remove the shared layer and place all the parameters
>   underneath within project?
>
> - static_dir: is it now safe to remove this parameter? Is anyone downstream
>   consuming it?
>
> - historical window shall go under climate i think, as this window describes
>   the raw climate data's extraction window.
>
> These are a few examples. I think we can first do a "free, brainstorm" level
> assessment of parameters, their naming, nesting structucture under the
> config.yml.

Follow-up, same dialogue:

> Can you open a new branch for R14 and consider this as a preparation
> exercise? Also, put everything in scoping document. assign an index/id to
> each change so I can refer easily later on

## Problem

R13 fixed *which file* a key lives in. It did not touch *which section*, or
*what a key is called*. Those two questions are still answered by history:

- `shared:` names a **relationship** ("read by ≥2 workflows"), not a kind, so it
  is a bag holding a basin geometry, a climate binding, a hydrological-year
  convention and a thread count under one heading.
- One concept has several spellings (`starttime`/`endtime` vs
  `historical_year_range: [a, b]` vs `future_horizons.<n>: [a, b]`; `source`
  meaning both a catalog FILE and a catalog ENTRY).
- The experiment guard's key list (`_WF1_GUARDED`) is maintained by hand
  because no section boundary distinguishes "changes the numbers" from "changes
  only the wall-clock".

These are P3 and P4 of `dev/working/parameter-placement.md` (DRAFT, 2026-08-12),
still open. This document is the live proposal that note's §5–§6 deferred.

## Relationship to prior records

| record | status | relationship |
|---|---|---|
| `dev/working/parameter-placement.md` | DRAFT, not agreed | Inventory (§1–§3) is measured and reused. Its **M1** = `C-07`, **M2** = `C-35`, **M3** = `C-36`, **M4** ≈ `C-10`…`C-15`. Its §6 cost columns are **stale**: written 2026-08-12, before R13 landed. Re-measure. |
| `dev/milestones/r13/config-tiers-design.md` | ACCEPTED 2026-08-21 | Owns `T1_TOP_LEVEL` (D-9.5), the seam checks (D-9.1/9.2/9.3/9.6), the composition invariant (D-8.1) and the `wflow_outvars` hoist (D-9.7). Every change here that moves a top-level section **amends** an accepted decision and cannot be a quiet edit. |
| `run_stress_test.smk:100` | live code comment | Cites M1 as the reason `static_dir` was not deleted outright. `C-07` is what discharges it. |

## Proposed policy — structure

**S1 — A section is a KIND, never a relationship.** A heading answers *what is
this about?* (`basin`, `climate`, `compute`), never *who reads it?* (`shared`).
Read-count decides which FILE a key lives in; kind decides which SECTION. The
two axes are orthogonal, and `shared:` collapses them into one heading.

**S2 — Three identity classes partition the whole surface, each with its own
section name.**

| class | section | changing it changes |
|---|---|---|
| identity | everything not named below | the **numbers** |
| performance | `compute:` | cost / wall-clock only |
| description | `reporting:` | how results are **described** only |

This is the load-bearing rule: it makes the experiment guard mechanical —
*guard everything except `compute:` and `reporting:`* — instead of maintaining
`_WF1_GUARDED` by hand. `reporting:` already has exactly this carve-out in WF3
("sits outside configuration identity … editing a caption does not trip the
experiment freeze"); S2 generalizes it and gives performance knobs the same
structural treatment.

**S3 — One section, one guard granularity.** A section never mixes an
experiment-invariant key with a free-to-change one. S2 is the enforcement.

**S4 — Nest only to disambiguate; maximum depth 3 from a file root.** A group of
one is not a group.

**S5 — Engine-native blocks are never regrouped.** hydromt / hydromt_wflow /
wflow / weathergenr vocabulary enters through a PATH key pointing at a file in
their own schema (AGENTS.md hard constraint). It never appears inline in our
sections, and no key of theirs is renamed by this milestone.

**S6 — A path key names a FILE; a binding names a CATALOG ENTRY.** They never
share a section. `project.catalogs.*` are files; `basin.sources.*` and
`climate.source` are entries inside those files.

## Proposed policy — naming

**N1 — No new abbreviations.** `clim_historical` → `climate.source`. Exempt:
established domain terms (`lulc`, `lai`, `uparea`, `ssp`, `outvars`).

**N2 — Dimensional values carry their unit** unless a schema fixes it:
`snap_tolerance_m`, `river_uparea_km2`, `headroom_gb`.

**N3 — A key never repeats its own section.** Inside `climate:`,
`clim_historical` → `source`.

**N4 — A time span is `{start, end}` inside a `*_window:` group** — one spelling
in every file. Replaces `starttime`/`endtime` and both bare `[a, b]` year pairs.

**N5 — A name describes the VALUE, not the workflow that reads it.**
`horizontime_climate` → `horizon_year`; `clim_project` → `ensemble`.

**N6 — Counts use `_count`.** `realizations_num` → `realizations_count`,
`step_num` → `steps_count`. (Open: `_count` vs bare plural — `Q-C`.)

**Grandfathering.** `dev/reference/naming.md` grandfathers existing names and
requires a migration note to rename a contract surface. R14 *is* that migration
note: every rename below is deliberate and versioned, not opportunistic.

## Change register

Class: **NEW** (section introduced) · **RENAME** · **REGROUP** (moves between
sections/files) · **DELETE** · **MECHANISM** (code, not a config key).
"Breaking" = an existing project config stops parsing or changes digest.

### Group A — sections and mechanism

| ID | change | rule | class | breaking |
|---|---|---|---|---|
| `C-01` | Retire `shared:` as a heading; promote its contents to top-level kind sections | S1 | REGROUP | yes |
| `C-02` | Introduce `compute:` — the section whose contents cannot change results | S2 | NEW | yes |
| `C-03` | Generalize `reporting:` from WF3-only to any workflow file | S2 | NEW | no (additive) |
| `C-04` | Replace hand-maintained `_WF1_GUARDED` with "guard everything except `compute:`/`reporting:`" | S2, S3 | MECHANISM | behavior-visible |
| `C-05` | Add `schema_version: 2` to the project file; refuse a v1 set with a message naming the migration command | — | NEW | yes (by design) |

### Group B — `project:`

| ID | change | rule | class | breaking |
|---|---|---|---|---|
| `C-06` | `project.project_dir` → `project.dir` | N3 | RENAME | yes — **blocked on `Q-A`** |
| `C-07` | **Delete `project.static_dir`** (= M1) | — | DELETE | yes |
| `C-08` | `project.data_sources` → `project.catalogs.spatial` | S6, N1 | RENAME | yes |
| `C-09` | `project.data_sources_climate` → `project.catalogs.climate` | S6, N1 | RENAME | yes |

`C-07` evidence: read only by `build_model.smk:89`, used only to build the two
fallback prefixes at `:163-164`; explicitly *not* read by WF3 since 2026-08-13
(`run_stress_test.smk:100`); never read by WF0 or WF2; can only ever be
`config`, because the paths it prefixes are in-repo toolbox files. What makes it
breaking is not consumption but **digest identity** — `config_composition.py`
invariant #2: a key present-vs-absent moves `effective_config_digest`, and
`_frozen_differences`' key-union diff then refuses every already-run experiment
in the project. `_WF1_GUARDED` also guards `"project"` **whole**.

### Group C — `basin:`

| ID | change | rule | class | breaking |
|---|---|---|---|---|
| `C-10` | `shared.basin` → top-level `basin:` | S1 | REGROUP | yes |
| `C-11` | `basin.gauge_points` → `basin.gauges.points` | S4 | REGROUP | yes |
| `C-12` | `basin.gauge_snap_tolerance_m` → `basin.gauges.snap_tolerance_m` | S4, N2 | REGROUP | yes |
| `C-13` | `basin.automatic_subbasins.max_per_basin` → `basin.delineation.max_subbasins` | S4 | REGROUP | yes |
| `C-14` | `basin.river_uparea_km2` → `basin.delineation.river_uparea_km2` | S4 | REGROUP | yes |
| `C-15` | `basin.spatial_sources.*` + `basin.hydrography` + `basin.basin_index` → `basin.sources.*` | S6 | REGROUP | yes |

`C-10`…`C-15` are M4 made concrete: `shared.basin` currently mixes three kinds
— the basin's DEFINITION (`region`, `resolution`), catalog BINDINGS
(`spatial_sources.*`, `hydrography`, `basin_index`) and delineation TOLERANCES
(`max_per_basin`, `gauge_snap_tolerance_m`, `river_uparea_km2`).

### Group D — `climate:`

| ID | change | rule | class | breaking |
|---|---|---|---|---|
| `C-16` | Introduce top-level `climate:` | S1 | NEW | yes |
| `C-17` | `shared.clim_historical` → `climate.source` | N1, N3 | RENAME | yes |
| `C-18` | `shared.historical_window.{starttime,endtime}` → `climate.window.{start,end}` | N4 | RENAME | yes |

`C-16`–`C-18` are the owner's third question. `clim_historical` (the *what*) and
`historical_window` (the *how much*) are one concept in two sibling keys —
`shared.basin`'s complaint again. Caveat: `SHARED_SEAM_KEYS` is a **flat set of
names**, so nesting moves seam coverage from leaf to group and a T2 file could
then declare a bare `window:` uncaught. `basin` already has that property, so
this is a tolerated pattern rather than a new hole — but the seam set must be
re-derived, not merely edited.

### Group E — `model:`, `method:`, `compute:`

| ID | change | rule | class | breaking |
|---|---|---|---|---|
| `C-19` | `shared.wflow_outvars` → `model.outvars` | S1 | REGROUP | yes — **see `Q-B`** |
| `C-20` | `shared.seed`, `shared.water_year_start` → `method.{seed,water_year_start}` | S1, S3 | REGROUP | yes — **see `Q-D`** |
| `C-21` | `shared.julia_threads` → `compute.julia_threads` | S2, S3 | REGROUP | yes |

`C-21` is the clearest S3 case: `julia_threads` cannot change a number, and
flattening it into a guarded section (the owner's Q1 as literally posed) would
make a thread-count bump trip *"your model was built under different settings"*.

### Group F — `_build_model.yml`

| ID | change | rule | class | breaking |
|---|---|---|---|---|
| `C-22` | `model_build_config` / `waterbodies_config` → `engine.build_config` / `engine.waterbodies_config` | S4, S5, N3 | REGROUP | yes |
| `C-23` | `observations_timeseries` → `observations.timeseries` | S4 | REGROUP | yes |
| `C-24` | `simulation_window.{starttime,endtime}` → `simulation_window.{start,end}` | N4 | RENAME | yes |

`simulation_window` stays in the WF1 file: it is read by `build_model.smk` only
(verified 2026-08-22), so it is correctly T2 despite reading like a shared
window.

### Group G — `_analyze_projections.yml`

| ID | change | rule | class | breaking |
|---|---|---|---|---|
| `C-25` | `clim_project` → `ensemble` | N1, N5 | RENAME | yes |
| `C-26` | `historical_year_range: [a, b]` → `historical_window: {start, end}` | N4 | RENAME | yes |
| `C-27` | `future_horizons.<name>: [a, b]` → `future_horizons.<name>: {start, end}` | N4 | RENAME | yes |
| `C-28` | `stats`, `save_grids` → `reporting.{stats,save_grids}` | S2 | REGROUP | yes |

`C-25` also removes a live collision: `clim_project` reads as "the project's
climate" while meaning the projection ensemble family, next to a `project:`
section that means something else entirely.

### Group H — `_run_stress_test.yml`

| ID | change | rule | class | breaking |
|---|---|---|---|---|
| `C-29` | `realizations_num` → `realizations_count` | N6 | RENAME | yes — **`Q-C`** |
| `C-30` | `horizontime_climate` → `horizon_year` | N1, N5 | RENAME | yes |
| `C-31` | `stress_test.<var>.step_num` → `steps_count` | N6 | RENAME | yes — **`Q-C`** |
| `C-32` | `stress_test.<var>.transient_change` → `transient` | N3 | RENAME | yes |
| `C-33` | `stress_test.{dry,wet}_spell_factor` → `stress_test.spell_factors.{dry,wet}` | S4 | REGROUP | yes |
| `C-34` | `batch_size`, `batch_size_max`, `disk_headroom_gb` → `compute.*` | S2, S3 | REGROUP | yes |

`C-33` keeps the existing rationale intact — the spell factors are not
perturbation axes and must not read as siblings of `temp:`/`precip:`; a named
`spell_factors:` group says that structurally instead of in a comment.
`C-34` is S2's second payoff: three WF3 keys that cannot change a number
currently sit inside the guarded, digested surface.

### Group I — carried forward from `parameter-placement.md`

| ID | change | rule | class | breaking |
|---|---|---|---|---|
| `C-35` | De-duplicate `DEFAULT_ANCHOR` (defined twice: `metrics_definition.py:18`, `climate_figures.py:120`) (= M2) | — | MECHANISM | **no** |
| `C-36` | Move the config-key defaults out of Python (`DEFAULT_SPELL_FACTOR`, `DEFAULT_MAX_SUBBASINS_PER_BASIN`, `DEFAULT_GAUGE_SNAP_TOLERANCE_M`, `DEFAULT_HYDROGRAPHY`, `DEFAULT_BASIN_INDEX`, `DEFAULT_STATS`) (= M3) | — | MECHANISM | no — **blocked on `Q-E`** |
| `C-37` | A mechanical "declared keys ⊆ read keys" check (answers P2) | — | MECHANISM | no |
| `C-38` | Extend `scripts/split_project_config.py` (or a sibling) into a v1→v2 rewriter driven by the register above | — | MECHANISM | no |

`C-35` is the only change in this document that is unambiguously correct
regardless of how everything else resolves, and the only one that is
non-breaking and independently landable **today**.

## Proposed shape

### Project file (T1) — `snake_config_<project>.yml`

```yaml
schema_version: 2

project:
  dir: /path/to/my_project
  catalogs:
    spatial: config/catalogs/deltares_data.yml
    climate: config/catalogs/cmip6_data.yml

basin:
  region: "{'subbasin': [9.666, 0.4476], 'uparea': 100}"
  resolution: 0.00833333
  gauges:
    points: null
    snap_tolerance_m: 10000
  delineation:
    max_subbasins: 11
    river_uparea_km2: 32
  sources:
    hydrography: merit_hydro_ihu
    basin_index: merit_hydro_index
    rivers: rivers_lin2019_v1
    lulc: vito
    lai: modis_lai
    soil: soilgrids

climate:
  source: era5
  window: {start: "1990-01-01", end: "2020-12-31"}

model:
  outvars: ["river discharge", "actual evapotranspiration"]

method:
  water_year_start: Jan
  seed: auto

compute:
  julia_threads: 4

workflows:
  analyze_climate:     {enabled: true}
  build_model:         {enabled: true, config_path: ..._build_model.yml}
  analyze_projections: {enabled: true, config_path: ..._analyze_projections.yml}
  run_stress_test:     {enabled: true, config_path: ..._run_stress_test.yml}
```

### `_build_model.yml`

```yaml
engine:
  build_config: config/defaults/wflow_build_model.yml
  waterbodies_config: config/defaults/wflow_update_waterbodies.yml
simulation_window: {start: "2000-01-01", end: "2020-12-31"}
observations:
  timeseries: null
```

### `_analyze_projections.yml`

```yaml
ensemble: cmip6
models: [...]
scenarios: [ssp245, ssp585]
members: [r1i1p1f1]
member_selection: first_available
member_overrides: {}
variables:
  precip: {source: precip, canonical: rate,  units: mm/day, change: relative}
  temp:   {source: temp,   canonical: state, units: degC,   change: absolute}
historical_window: {start: 1985, end: 2014}
future_horizons:
  near: {start: 2030, end: 2060}
  far:  {start: 2070, end: 2100}
relative_change: {min_reference: {precip: 0.1}, max_flagged_months: 3}
reporting:
  stats: [mean, median, std]
  save_grids: false
```

### `_run_stress_test.yml`

```yaml
experiment_name: my_experiment
realizations_count: 2
horizon_year: 2050
run_length: 20
run_historical: false
stress_test:
  temp:
    steps_count: 1
    transient: true
    mean: {min: [...12], max: [...12]}
  precip:
    steps_count: 2
    transient: true
    mean:     {min: [...12], max: [...12]}
    variance: {min: [...12], max: [...12]}
  spell_factors:
    dry: [...12]
    wet: [...12]
compute:
  batch_size: 4
  batch_size_max: 8
  disk_headroom_gb: null
reporting:
  surfaces:
    - id: jfm
      x: {variable: temp}
      y: {variable: precip, months: [1, 2, 3], statistic: mean}
```

### `_analyze_climate.yml`

```yaml
candidate_sources: [chirps]
```

## Open questions

| ID | question | blocks | current lean |
|---|---|---|---|
| `Q-A` | `project.dir` (N3) vs keeping `project_dir` | `C-06` | **Keep `project_dir`** as a named exemption — it is a term of art here (AGENTS.md's two-tier location rule, `warn_if_project_dir_in_repo`, every internal variable). |
| `Q-B` | Is `model:` holding one leaf (`outvars`) an S4 violation, or correct anticipation? | `C-19` | Undecided. Alternatives: a bare top-level `wflow_outvars:` leaf, or folding it into `climate:`/`method:` (both wrong by kind). |
| `Q-C` | `_count` suffix vs bare plural (`realizations_count` vs `realizations`) | `C-29`, `C-31` | Undecided; `_count` is unambiguous, bare plural is shorter and YAML already distinguishes int from list. |
| `Q-D` | Does `method:` earn a heading, or should `seed`/`water_year_start` be bare top-level leaves? | `C-20` | Lean heading — it is where a third method convention would go. |
| `Q-E` | Where does a config key's DEFAULT live: `config/advanced_settings.yml` (precedent, closed schema, already tested) or beside the key in the template? | `C-36` | **`advanced_settings`** — the only option with an existing enforcement mechanism, and the only one that could grow `C-37`. |
| `Q-F` | Does S2 actually permit `_WF1_GUARDED` to become "everything except `compute:`/`reporting:`"? | `C-04` | Unknown. **Needs a probe against the digest and freeze code before R14 promises it.** |

## Constraints

1. **AGENTS.md hard constraint (S5).** hydromt / hydromt_wflow / wflow /
   weathergenr vocabulary is used verbatim. No key inside `config/defaults/*`
   or a data catalog is renamed by this milestone.
2. **R13 is accepted.** Any change to `T1_TOP_LEVEL` (D-9.5), `SHARED_SEAM_KEYS`,
   `HOISTED_SECTIONS` or the composition invariant (D-8.1) is an **amendment to
   an accepted design**, recorded as such, not a quiet edit.
3. **Digest identity.** A key present-vs-absent — not merely re-valued — moves
   `effective_config_digest`. Every already-run experiment in every project is
   refused across this migration by construction. That is acceptable **only**
   if it happens once, which is the whole argument for bundling.
4. **Two homes for a window today.** `climate.window` (extraction) and
   `simulation_window` (model run) are necessarily separate and must stay
   visibly separate after N4 makes them look alike.
5. No change to what any workflow COMPUTES. If a number moves, the change is
   wrong.

## Decision criteria

- **D1 — Does it answer P2 mechanically?** The sharpest test inherited from
  `parameter-placement.md`: four inert-or-partly-inert parameters have been
  found by hand and zero by machine. A shape that does not make `C-37`
  feasible has not solved the problem that has real consequences.
- **D2 — Does it preserve guard semantics?** Specifically the reason
  `_WF1_GUARDED` guards `shared` leaf-by-leaf while guarding `project` whole.
- **D3 — Is the migration mechanical?** Every row of the register must be
  expressible as a pure old-path → new-path rewrite for `C-38`. A row needing
  human judgment is a design smell, not a migration step.
- **D4 — Does a new parameter now have exactly one obvious home?** The failure
  that started `parameter-placement.md` was three parameters placed by
  precedent because no rule existed.

## Success criteria

1. A user can find every knob that affects their basin, and see its default,
   without reading Python.
2. Every section name states a KIND; no section names a relationship.
3. The experiment guard's key list is DERIVED from section membership, not
   maintained by hand (`C-04`), or `Q-F` is answered and the reason recorded.
4. One command rewrites a complete v1 config set to v2 (`C-38`), and the
   `tests/data/presplit/` corpus is extended with a v1→v2 pair.
5. `pixi run test-full` green on both platforms; `check_baseline.py check`
   unchanged — a pure rename must not move a single number.

## Non-goals

- Re-opening R13's tier split, path-reference composition, or the single
  `--configfile` CLI contract.
- Any change to `config/catalogs/*`, `config/defaults/*` internals, or
  `advanced_settings.yml`'s authority boundary.
- Changing what a workflow computes, or adding/removing a parameter's meaning.
  Every register row is a MOVE or a RENAME except `C-07` (delete) and Group I.
- Web/API concerns. The CST-API and frontend never constrain this repo, and no
  decision here is gated on whether they consume an artifact by name.

## Blast radius (re-measure before the design)

Post-R13 the surface is wider than `parameter-placement.md` §6 recorded:

- the four `*.smk` entry points and `blueearth_cst/shared/snake_utils.py`
- `blueearth_cst/shared/config_composition.py` — `T1_TOP_LEVEL`,
  `SHARED_SEAM_KEYS`, `HOISTED_SECTIONS`, the static read scan (D-9.6)
- `blueearth_cst/experiment/check_project_consistency.py` — `_WF1_GUARDED`,
  `_COPIED_CONFIG_PATH_MAP`
- `config/templates/snake_config*.template.yml` × 4
- `test_case/snake_config_*.yml` — **four multi-file sets** (baseline, baseline
  _linux, rapid, wf2_fast), 17 files
- `tests/snake_config_fixture.yml`, and `tests/data/presplit/**` (which exists
  precisely to test migration and must gain a v1→v2 pair)
- `scripts/split_project_config.py`, `scripts/plot_workflow_dag.py`
- `docs/guide/configuration.qmd`, `docs/migration-config-tiers.md`, `README.md`
- `dev/reference/workflows/*.md`, `dev/reference/naming.md`, `AGENTS.md`

## Packaging recommendation

Every change except `C-35`, `C-37` and `C-38` is breaking, and their costs are
almost entirely **shared** — one migration pass, one template rewrite, one
sweep of the fixture corpus. Landing `C-07` alone would pay the whole migration
cost for one dead key. Recommendation:

- **Now, independently:** `C-35` (non-breaking, correct under every outcome).
- **Probe before designing:** `Q-F` (`C-04`) and D3-feasibility for `C-38`.
- **One bundle, one `schema_version` bump:** everything else.

The project config carries no version key today (the `schema_version` hits
elsewhere in the tree belong to snapshot and series-identity artifacts), so the
bundle is also the moment `C-05` becomes possible.

## Next artifact

An intake + design under `design-review-loop`, on the R13 pattern:
`dev/milestones/r14/config-shape-intake.md` → `config-shape-design.md` →
review record. Not started; this document is the input to it.
