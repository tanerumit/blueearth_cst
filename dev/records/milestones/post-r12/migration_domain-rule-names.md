# Migration: domain rule names and contiguous numbers (2026-09-24)

Rule-naming bundle, board items `t2609241947` (WF0–WF3) and `t2609241942`
(WF4), on branch `workflow-rule-naming`. Rules are named for what they do in
the pipeline, numbered contiguously from `W.01`, and target rules carry no
number. Rule identities only: script modules, functions, `script:` paths and
the `metric_sets/` / `metric_requests/` folders keep their names.

## Old → new

`—` means the rule is a target and has no number. Unlisted rules keep their
name and number.

| Old # | Old name | New # | New name |
|---|---|---|---|
| 0.00 | `all` | — | `all` |
| 0.02 | `delineate_region` | 0.01 | `delineate_region` |
| 0.03 | `delineate_spatial_units` | 0.02 | `delineate_subbasins_and_rivers` |
| 0.04 | `extract_historical_climate_<source>` | 0.03 | `extract_climate_datasets_<source>` |
| 0.05 | `plot_climate_source_<source>` | 0.04 | `plot_climate_datasets_<source>` |
| 0.06 | `compare_climate_sources` | 0.05 | `compare_climate_datasets` |
| 0.10 | `gather_benchmarks` | 0.06 | `gather_benchmarks` |
| 0.11 | `gather_logs` | 0.07 | `gather_logs` |
| 1.00 | `all` | — | `all` |
| 1.02 | `delineate_region` | 1.01 | `delineate_region` |
| 1.03 | `delineate_spatial_units` | 1.02 | `delineate_subbasins_and_rivers` |
| 1.04 | `extract_historical_climate` | 1.03 | `extract_climate_datasets` |
| 1.05 | `plot_climate_source` | 1.04 | `plot_climate_datasets` |
| 1.06 | `prepare_spatial_maps` | 1.05 | `prepare_land_and_soil_maps` |
| 1.07 | `build_wflow_model` | 1.06 | `build_wflow_model` |
| 1.08 | `add_reservoirs_lakes_glaciers` | 1.07 | `add_reservoirs_lakes_glaciers` |
| 1.09 | `declare_wflow_outputs` | 1.08 | `declare_gauges_and_outputs` |
| 1.10 | `add_climate_forcing` | 1.09 | `add_climate_forcing` |
| 1.11 | `write_outlet_index` | 1.10 | `write_gauge_index` |
| 1.12 | `plot_basin_map` | 1.11 | `plot_basin_map` |
| 1.13 | `plot_forcing` | 1.12 | `plot_model_forcing` |
| 1.14 | `run_wflow` | 1.13 | `run_historical_simulation` |
| 1.14b | `export_wflow_tables` | 1.14 | `export_simulation_tables` |
| 1.15 | `plot_wflow_evaluation` | 1.15 | `plot_model_evaluation` |
| 1.15b | `write_run_metadata` | 1.16 | `write_run_metadata` |
| 1.16 | `gather_benchmarks` | 1.17 | `gather_benchmarks` |
| 1.17 | `gather_logs` | 1.18 | `gather_logs` |
| 2.00 | `all` | — | `all` |
| 2.02 | `delineate_region` | 2.01 | `delineate_region` |
| 2.03 | `delineate_spatial_units` | 2.02 | `delineate_subbasins_and_rivers` |
| 2.04 | `fetch_gcm_slice` | 2.03 | `fetch_cmip6_projections` |
| 2.05 | `reduce_gcm_series` | 2.04 | `reduce_to_basin_averages` |
| 2.06 | `derive_change_factors` | 2.05 | `derive_change_factors` |
| 2.07 | `plot_gcm_timeseries` | 2.06 | `plot_climate_projections` |
| 2.08 | `gather_benchmarks` | 2.07 | `gather_benchmarks` |
| 2.09 | `gather_logs` | 2.08 | `gather_logs` |
| 3.00 | `all` | — | `all` |
| 3.02 | `extract_historical_climate` | 3.02 | `extract_climate_datasets` |
| 3.04 | `prepare_collection_sources` | 3.04 | `snapshot_generation_inputs` (planning step) |
| 3.05 | `initialize_scenario_collection` | 3.05 | `claim_scenario_collection` (planning step) |
| 3.06 | `prepare_weathergen_config` | 3.06 | `prepare_weather_generator_settings` (planning step) |
| 3.10 | `publish_scenario_collection` | 3.09 | `publish_scenario_collection` |
| 3.11 | `gather_benchmarks` | 3.10 | `gather_benchmarks` |
| 3.12 | `gather_logs` | 3.11 | `gather_logs` |
| 4.00 | `all` | — | `all` |
| 4.01 | `write_model_reference` | 4.01 | `write_model_fingerprint` |
| 4.02 | `check_model_reference` | 4.02 | `check_model_unchanged` |
| 4.03 | `freeze_wflow_simulation` | 4.03 | `snapshot_simulation_inputs` |
| 4.04 | `downscale_climate_realization` | 4.04 | `downscale_scenario_series` |
| 4.05 | `run_wflow_batch_<b>` | 4.05 | `run_wflow_simulations_batch_<b>` |
| 4.06 | `publish_native_responses` | 4.06 | `publish_wflow_outputs` |
| 4.07 | `responses` | — | `simulations_only` |
| 4.08 | `prepare_metric_plan` | 4.07 | `prepare_indicator_plan` |
| 4.09 | `publish_metric_set` | 4.08 | `derive_system_indicators` |
| 4.10 | `metrics` | — | `simulations_and_indicators` |
| 4.11 | `gather_logs` | 4.09 | `gather_logs` |
| 4.12 | `gather_benchmarks` | 4.10 | `gather_benchmarks` |

`claim_` joins the `naming.md` §8b verb table, and `snapshot_` is widened to
cover freezing inputs as well as copying them.

## What changes for a user

- CLI targets: `--forcerun`, `--until` and similar flags take the new names.
  `scripts/simulate_system.py --target` (and `run_workflows.py
  --simulation-target`) still accept `responses` and `metrics` for one release
  and pass the new names to Snakemake.
- Log and benchmark part files take the new `<W.NN>_<name>` labels, for example
  `logs/_parts/1.13_run_historical_simulation.log`. Part directories from
  earlier runs keep their old labels and are merged by nothing; delete them.
- The console prints targets as `Target: <name>`, and the plan block leaves them
  out.
- Identities are unaffected. The files in the generation, simulation, metric
  and climate-store code inventories were left byte-identical, so existing
  collections, simulations and metric sets are reused.
- Rerun exposure on an existing project. Snakemake's `code` trigger hashes
  shell commands only (`snakemake/persistence.py`, `_code`), so neither a rule's
  new name nor the changed `run:`-body literal in 4.03 schedules a job. Script
  modules whose comments changed are compared by mtime, so rules calling them
  may re-run once, with unchanged outputs. What was measured: a WF1 dry run
  against `test_case/test_local` schedules every rule, but it does so
  identically on `main`, where `delineate_region` is already stale ("code has
  changed", "set of input files has changed"). That existing cascade hides any
  trigger this branch adds, so WF1 proves nothing either way. WF0, WF2, WF3 and
  WF4 were not dry-run against a real tree: this worktree's `test_local` lacks
  the current WF3 collection.

## Also in this bundle

`t2608220915`: rule 1.05 (`prepare_land_and_soil_maps`) now declares
`river_attributes.geojson` as an input, so a tree that predates it re-runs 1.02.

## Updated references

The five Snakefiles, `blueearth_cst/shared/console_style.py` (numberless
targets), `blueearth_cst/experiment/simulation_runner.py` (target aliases),
comments and docstrings across `blueearth_cst/`, tests,
`dev/scripts/console_sample_specs.py`, `dev/scripts/render_console_sample.py`,
`dev/reference/workflows/rule-index.md`, `dev/reference/naming.md`,
`dev/reference/contracts/`, `README.md`, `AGENTS.md`, `docs/` and the two
workflow notebooks.
