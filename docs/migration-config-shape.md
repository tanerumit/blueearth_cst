# Migrating a project config to `schema_version: 2`

R14 reshaped the project config. Two things changed at once, and both are
contract surfaces: **every key spelling**, and **the filename prefix**.

One command does the whole thing. You should not need to hand-edit anything, and
if you do, that is worth reporting rather than working around.

```bash
python scripts/migrate_project_config.py path/to/project_config.yml
```

It takes the **project file** — the one you pass to `--configfile`. It finds the
per-workflow files itself by following each `config_path:`, so you name one file
and it migrates the set.

Add `--dry-run` to see what it would do and write nothing.

## What it does to your files

The migration is **transactional**, because a config set half-migrated is worse
than one not migrated at all — it parses, and it means something different.

1. every file in the set is read and checked **before anything is written**;
2. the rewrite is staged in memory and validated through the real loader, so a
   set that would not parse is never written;
3. only then are the files replaced, all together;
4. your originals are kept beside them as `*.v1.bak`.

Comments are preserved and travel with their key. A comment you wrote next to
`horizontime_climate` ends up next to `simulation_window`.

## Two cases the migration does not preserve

Everything else is value-preserving: the same run, spelled differently. These
two are not, and both are deliberate.

### `run_historical: false` — your next run gains a member

The key is gone and the unperturbed baseline member `st_0` is now **always**
produced. If your project had `run_historical: false`, the migration warns and
proceeds; your next run gains `st_0` and the two indicators derived from it,
`q_wettest_month_mean` and `q_driest_month_mean` — 2 of the 11 q metrics.

It warns rather than refuses because that is the row's intended behaviour, and
refusing would block every such project from migrating at all. `run_historical:
true` says nothing: a signal that fires on every run is one nobody reads.

### A non-January `water_year_start` — **refused**

If your project sets `water_year_start` to anything but `Jan`, the migration
stops and tells you so, naming the window.

The reason is that v1's window bounds are CALENDAR dates and v2's are years
interpreted against the water year. For January the two coincide and the rewrite
is exact. For any other month **no year pair reproduces the old window**, so
there is nothing correct to emit.

This is the one place the tool refuses rather than guessing, and the alternative
is what makes it worth it: every downstream number would shift by up to a year,
under a config that looks migrated and validates cleanly.

## The file rename

`snake_config_*.yml` is now `project_config_*.yml`. The file configures the
**project**; Snakemake is one tool that happens to read it, which is the less
durable of the two facts.

For your own project there is no rule beyond "the set lives in one directory and
each `config_path:` resolves". The templates suggest:

```
project_config.yml
project_config_build_model.yml
project_config_analyze_projections.yml
project_config_run_stress_test.yml
```

with no project name in the filename — your directory already says which project
it is. (This repository's own `test_case/` seeds carry `_rapid`, `_baseline` and
`_wf2_fast` because they are several example sets sharing one directory.)

If you keep your configs inside this repository under `test_case/`, the
`project_config_` prefix is **load-bearing**: `.gitignore` un-ignores exactly
that glob, so a seed named anything else is silently untracked.

## What the loader does with a v1 config

It refuses it, by name, at parse time — before any rule runs.

`schema_version` is checked first, so a whole v1 set is rejected with one
message naming this document rather than with half a dozen confusing complaints
about individual keys. Every retired key also has its own refusal that says
where it went, so a partially hand-edited config is told exactly which key is
still v1.

Nothing is silently accepted and defaulted. That is the point of the closed
schema: under v1, a misspelled key was simply an absent key, and the run
proceeded on a default nobody chose.

## The key map

Generated from `config/migrations/v1_to_v2.yml`, which is what the rewriter
executes — so this table cannot drift from the behaviour it documents.

**"where"** is which file the key lives in: the project file, or one of the
per-workflow files. A destination in a different file names it in brackets.

| where | v1 | v2 | row | value |
|---|---|---|---|---|
| project file | `shared` | **deleted** | `C-01` |  |
| run_stress_test | _(new)_ | `compute` | `C-02` |  |
| project file | _(new)_ | `schema_version` | `C-05` |  |
| project file | `project.static_dir` | **deleted** | `C-07` |  |
| project file | `shared.basin` | `basin` | `C-10` |  |
| project file | `basin.automatic_subbasins` | `basin.delineation` | `C-13` |  |
| project file | `basin.automatic_subbasins.max_per_basin` | `basin.delineation.max_subbasins` | `C-13` |  |
| project file | `basin.river_uparea_km2` | `basin.delineation.river_uparea_km2` | `C-14` |  |
| project file | `basin.spatial_sources` | `basin.sources` | `C-15` |  |
| project file | `basin.hydrography` | `basin.sources.hydrography` | `C-15` |  |
| project file | `basin.basin_index` | `basin.sources.basin_index` | `C-15` |  |
| project file | _(new)_ | `climate` | `C-16` |  |
| project file | `shared.wflow_outvars` | `model.outvars` | `C-19` |  |
| build_model | `model_build_config` | `engine.build_config` | `C-22` |  |
| build_model | `waterbodies_config` | `engine.waterbodies_config` | `C-22` |  |
| analyze_projections | `clim_project` | `ensemble` | `C-25` |  |
| run_stress_test | `realizations_num` | `n_realizations` | `C-29` |  |
| run_stress_test | `stress_test.temp.step_num` | `climate_perturbations.temp.n_levels` | `C-31` | steps -> level COUNT (+1) |
| run_stress_test | `stress_test.precip.step_num` | `climate_perturbations.precip.n_levels` | `C-31` | steps -> level COUNT (+1) |
| run_stress_test | `stress_test.temp.transient_change` | `climate_perturbations.temp.trajectory` | `C-32` | boolean -> enum |
| run_stress_test | `stress_test.precip.transient_change` | `climate_perturbations.precip.trajectory` | `C-32` | boolean -> enum |
| run_stress_test | `stress_test.dry_spell_factor` | `climate_perturbations.spell_factors.dry` | `C-33` |  |
| run_stress_test | `stress_test.wet_spell_factor` | `climate_perturbations.spell_factors.wet` | `C-33` |  |
| run_stress_test | `batch_size` | `compute.batch_size` | `C-34` |  |
| run_stress_test | `batch_size_max` | `compute.batch_size_max` | `C-34` |  |
| run_stress_test | `disk_headroom_gb` | `compute.disk_headroom_gb` | `C-34` |  |
| project file | `project.data_sources_climate` | `catalog` (analyze_projections) | `C-39` |  |
| project file | `project.data_sources` | `project.catalog` | `C-40` |  |
| project file | `basin.gauge_points` | `basin.output_locations` | `C-41` |  |
| project file | `basin.gauge_snap_tolerance_m` | `basin.delineation.snap_tolerance_m` | `C-42` |  |
| analyze_climate | `candidate_sources` | `climate.sources` (project file) | `C-43` | unioned with the selected source |
| project file | `shared.clim_historical` | `climate.selected` | `C-44` |  |
| project file | `shared.seed` | `seed` (run_stress_test) | `C-51` |  |
| project file | `method` | **deleted** | `C-52` |  |
| project file | `shared.water_year_start` | `climate.water_year_start` | `C-53` |  |
| project file | `shared.julia_threads` | **deleted** | `C-54` |  |
| project file | `compute` | **deleted** | `C-55` |  |
| build_model | `observations_timeseries` | `observations` | `C-56` | scalar -> per-variable mapping |
| analyze_projections | `historical_year_range` | `reference_window` | `C-59` | `[a, b]` -> `{start, end}` |
| analyze_projections | `future_horizons` | `future_windows` | `C-60` | list -> named windows |
| analyze_projections | `relative_change.min_reference` | `relative_change.min_denominator` | `C-62` |  |
| analyze_projections | `members` | `members.preference` | `C-63` | list -> `{preference: [...]}` |
| analyze_projections | `member_selection` | `members.selection` | `C-63` |  |
| analyze_projections | `member_overrides` | `members.overrides` | `C-63` |  |
| analyze_projections | `relative_change` | **deleted** | `C-66` |  |
| run_stress_test | `horizontime_climate` | `simulation_window` | `C-67` | horizon + length -> `{start, end}` |
| run_stress_test | `run_length` | `simulation_window` | `C-67` | horizon + length -> `{start, end}` |
| run_stress_test | `stress_test` | `climate_perturbations` | `C-68` |  |
| run_stress_test | `run_historical` | **deleted** | `C-69` | see the warning above |
| project file | `shared.historical_window` | `climate.window` | `C-70` | ISO timestamp -> inclusive year |
| build_model | `simulation_window` | `simulation_window` | `C-71` | ISO timestamp -> inclusive year |
| any | `reporting` | **deleted** | `C-77` |  |
| run_stress_test | _(new)_ | `weathergen_config` | `C-81` |  |

### Two of these need a sentence each

**`C-31`, `step_num` → `n_levels`, is not a rename.** `step_num: 2` meant two
steps and produced **three** levels; `n_levels: 3` says three. The migration
adds one. The grid is unchanged; if you edit it later, mind which you are
counting.

**`C-67` folds two keys into one window, and the arithmetic is not what it
looks like.** `horizontime_climate: 2050` with `run_length: 8` did not run
2046–2053: the halves snapped `ceil` backwards and `round` forwards, giving
2046–2054 — **nine** calendar years. The migration emits the window the run
actually used, not the one the arithmetic appears to give.

## Things the tool cannot move for you

Seven register rows have destinations that are not config paths, so the rewriter
drops the key and something else supplies the value. Only two can affect you:

- **`min_reference`** (`C-62`/`C-64`) is per-variable metadata now. If you set a
  custom near-zero threshold, declare it as `min_denominator` inside that
  variable's own entry under `variables:`. The shipped default for `precip`
  (0.1 mm/day) is supplied by the toolbox and needs no config.
- **`max_flagged_months`** (`C-65`) became a toolbox constraint in
  `config/advanced_settings.yml`. It is no longer a per-project setting: it is
  the point at which a monthly relative product stops being reportable, which is
  a property of the method rather than of a basin. **If you set it to a
  non-default value, that value is not carried over** — change it there, with a
  reason you would write down.

The other five (`C-45`, `C-50`, `C-57`, `C-58`, `C-61`) are additions or
internal derivations with no key you could have set.

## Related

- `docs/migration-config-tiers.md` — R13's split into a project file plus one
  file per workflow. Superseded as a *tool*, but it is the only written record
  of what that split did, which this note builds on rather than repeats.
- `config/templates/` — copy these for a new project; the header explains the
  layout.
- `config/migrations/v1_to_v2.yml` — the mapping the rewriter executes, and the
  source of the table above.
