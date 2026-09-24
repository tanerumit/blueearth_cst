---
title: Rename and renumber WF0-WF3 rules to domain names (screening 2026-09-24)
type: todo-item
status: backlog
branch: wf3-improvements
effort: 1
area: workflows
origin: wf4 naming bundle (2026-09-24)
queue:
created: 2026-09-24
updated: 2026-09-24
---

> [!note] Overview
> **What** — Agreed per workflow; bundle with the WF4 item. WF0: targets hidden (all unnumbered); 0.01 delineate_region; 0.02 delineate_spatial_units -> delineate_subbasins_and_rivers (shared: also renames WF1/WF2's rule); 0.03 extract_historical_climate(_<dataset>) -> extract_climate_datasets(_<dataset>) (also WF1 1.03 and WF3 3.02); 0.04 plot_climate_source -> plot_climate_datasets; 0.05 compare_climate_sources -> compare_climate_datasets; 0.06 gather_benchmarks; 0.07 gather_logs. Reserved 0.07-0.09 band dropped; evaluation rules (t2608181139) get numbers when built. WF1-WF3: see sections below as agreed.
> **Why** — Rule names and numbers are the pipeline overview domain experts read; gaps and internal wording read as missing or opaque steps.
> **Effort** — small

## Progress

- [ ] <first step>

## WF1 (agreed 2026-09-24)

`all` hidden. 1.01 delineate_region; 1.02 delineate_subbasins_and_rivers;
1.03 extract_climate_datasets; 1.04 plot_climate_datasets (was plot_climate_source);
1.05 prepare_land_and_soil_maps (was prepare_spatial_maps); 1.06 build_wflow_model;
1.07 add_reservoirs_lakes_glaciers; 1.08 declare_gauges_and_outputs (was
declare_wflow_outputs); 1.09 add_climate_forcing; 1.10 write_gauge_index (was
write_outlet_index); 1.11 plot_basin_map; 1.12 plot_model_forcing (was plot_forcing);
1.13 run_historical_simulation (was run_wflow); 1.14 export_simulation_tables (was
1.14b export_wflow_tables); 1.15 plot_model_evaluation (was plot_wflow_evaluation);
1.16 write_run_metadata (was 1.15b); 1.17 gather_benchmarks; 1.18 gather_logs.

## WF2 (agreed 2026-09-24)

`all` hidden. 2.01 delineate_region; 2.02 delineate_subbasins_and_rivers;
2.03 fetch_cmip6_projections (was fetch_gcm_slice); 2.04 reduce_to_basin_averages
(was reduce_gcm_series); 2.05 derive_change_factors; 2.06 plot_climate_projections
(was plot_gcm_timeseries); 2.07 gather_benchmarks; 2.08 gather_logs.

## WF3 (agreed 2026-09-24)

`all` hidden. 3.01 delineate_region; 3.02 extract_climate_datasets (was
extract_historical_climate); 3.03 prepare_perturbation_grid; planning steps:
3.04 snapshot_generation_inputs (was prepare_collection_sources), 3.05
claim_scenario_collection (was initialize_scenario_collection; adds verb claim_ to
naming.md 8b), 3.06 prepare_weather_generator_settings (was prepare_weathergen_config);
3.07 generate_weather_realizations; 3.08 perturb_climate_realizations;
3.09 publish_scenario_collection (was 3.10); 3.10 gather_benchmarks (was 3.11);
3.11 gather_logs (was 3.12).

## Shared across workflows

Targets (`all`, WF4's two) join _PLAN_EXCLUDED_RULES and get no number. Update
naming.md 8b verbs (claim_, snapshot_ use), rule-index.md, console samples, tests,
scripts/simulate_system.py targets, and one migration note listing old -> new names
and the renamed log/benchmark part files. Land with the WF4 item; test-full once.
