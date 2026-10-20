# Historical rule-numbering crosswalks

These tables preserve the numbers used by old citations. Current rules live in
[the rule index](../../../reference/workflows/rule-index.md).

## What changed

Dated translations for historical citations. Current WF3/WF4 numbering is in their tables below.

### Domain names and contiguous numbers — 2026-09-24

Every workflow was renamed and renumbered from `W.01`, and target rules lost
their numbers. The old → new table for all five workflows is in
[`migration_domain-rule-names.md`](../../milestones/post-r12/migration_domain-rule-names.md).
The older tables below use the names and numbers of their date.

### Renumbering — 2026-08-06 historical map

Read this table before interpreting any `W.NN` in a document written before
2026-08-06. 47 declarations: 18 in WF1, 10 in WF2, 19 in WF3. The `was`
column carries the old name too wherever the rename and the renumber coincide,
so one lookup answers both.


**WF1** — `build_model.smk`

| new | rule | was |
|---|---|---|
| 1.00 | `all` | 1.00 |
| 1.01 | pre-parse archive publication (launcher, no rule) | 1.01 `snapshot_config` |
| 1.02 | `delineate_region` | 1.01b |
| 1.03 | `delineate_spatial_units` | 1.01c |
| 1.04 | `extract_historical_climate` | 1.10 `extract_climate_grid` |
| 1.05 | `plot_climate_source` | 1.15 |
| 1.06 | `prepare_spatial_maps` | 1.02 |
| 1.07 | `build_wflow_model` | 1.03 |
| 1.08 | `add_reservoirs_lakes_glaciers` | 1.04 |
| 1.09 | `declare_wflow_outputs` | 1.05 `add_gauges_and_outputs` |
| 1.10 | `add_climate_forcing` | 1.08 `add_forcing` (+ 1.07, merged in) |
| 1.11 | `write_outlet_index` | 1.06 |
| 1.12 | `plot_basin_map` | 1.12 `plot_map` |
| 1.13 | `plot_forcing` | 1.13 |
| 1.14 | `run_wflow` | 1.09 |
| 1.15 | `plot_wflow_evaluation` | 1.11 `plot_results` |
| 1.16 | `gather_benchmarks` | 1.14 |
| 1.17 | `gather_logs` | 1.16 |

> **Two rules moved further than the previous draft of this table had them, and
> not because of the new rule.** `write_outlet_index` and `plot_basin_map` both
> declare `ancient(<model>/.model_final)`, and that sentinel is written by
> `add_climate_forcing` — so both are downstream of it, and the earlier map,
> which placed them at 1.07 and 1.10 against `add_climate_forcing` at 1.11, had
> two dependencies pointing high→low. The cause is ADR 0004, which moved the
> model root's terminal anchor onto the forcing rule after that map was drawn.
> `ancient()` is why it was easy to miss: it hides the rerun-trigger, not the
> edge.

**WF2** — `analyze_projections.smk`

| new | rule | was |
|---|---|---|
| 2.00 | `all` | 2.00 |
| 2.01 | pre-parse archive publication (launcher, no rule) | 2.03 `snapshot_config` |
| 2.02 | `delineate_region` | 2.03b |
| 2.03 | `delineate_spatial_units` | 2.03c |
| 2.04 | `fetch_gcm_slice` | 2.01 `fetch_gcm_raw` |
| 2.05 | `reduce_gcm_series` | 2.02 |
| 2.06 | `derive_change_factors` | 2.04 |
| 2.07 | `plot_gcm_timeseries` | 2.06 `plot_climate_proj_timeseries` |
| 2.08 | `gather_benchmarks` | 2.10 |
| 2.09 | `gather_logs` | 2.07 |

> **WF2's two gather rules swap relative order**, which is the one cell in this
> table that is a convention choice rather than a derivation. The two are
> parallel leaves — identical `input:` sets, neither consumes the other — so no
> dependency decides it. WF1 and WF3 both define benchmarks first; WF2 defined
> logs first, and nothing recorded why. Ruled 2026-08-06 to follow the other two
> workflows, so the three read alike and `gather_logs` is the last-numbered rule
> everywhere.

**WF3** — `run_stress_test.smk`

| new | rule | was |
|---|---|---|
| 3.00 | `all` | 3.00 |
| 3.01 | `check_project_consistency` | 3.00b |
| 3.02 | `snapshot_config` | 3.01 |
| 3.03 | `delineate_region` | 3.01b |
| 3.04 | `delineate_spatial_units` | 3.01f |
| 3.05 | `write_model_reference` | 3.01c |
| 3.06 | `check_model_reference` | 3.01d |
| 3.08 | `extract_historical_climate` | 3.02 `extract_climate_grid` |
| 3.09 | `prepare_stress_test_grid` | 3.03 `climate_stress_parameters` |
| 3.10 | `prepare_weathergen_config` | 3.04 `prepare_weagen_config` |
| 3.11 | `generate_weather_realizations` | 3.06 `generate_weather_realization` |
| 3.12 | `perturb_climate_realization` | 3.07 `generate_climate_stress_test` |
| 3.13 | `write_climate_data_catalog` | 3.08 `climate_data_catalog` |
| 3.14 | `downscale_climate_realization` | 3.09 |
| 3.15 | `run_wflow_batch_<b>` | 3.10 |
| 3.16 | `derive_wflow_indicators` | 3.11 |
| 3.17 | `gather_benchmarks` | 3.12 |
| 3.18 | `gather_logs` | 3.13 |

> **`3.01f` is gone, and that is what the renumber was for.** The vector rule
> answered to `3.01f` only because `3.01c`–`3.01e` were already taken, so a rule
> that belongs beside `delineate_region` sorted five letters away from it. It is
> now `3.04`, adjacent to `3.03` in all three workflows.

### Twelve renames

| rule | was |
|---|---|
| `declare_wflow_outputs` | `add_gauges_and_outputs` |
| `add_climate_forcing` | `add_forcing` |
| `extract_historical_climate` | `extract_climate_grid` |
| `plot_wflow_evaluation` | `plot_results` |
| `plot_basin_map` | `plot_map` |
| `fetch_gcm_slice` | `fetch_gcm_raw` |
| `plot_gcm_timeseries` | `plot_climate_proj_timeseries` |
| `prepare_stress_test_grid` | `climate_stress_parameters` |
| `prepare_weathergen_config` | `prepare_weagen_config` |
| `generate_weather_realizations` | `generate_weather_realization` |
| `perturb_climate_realization` | `generate_climate_stress_test` |
| `write_climate_data_catalog` | `climate_data_catalog` |


## R12 numbering crosswalk

| Former combined-WF3 rule | Successor |
|---|---|
| 3.03 region | 3.01 |
| 3.08 climate extraction | 3.02 |
| 3.09 perturbation lookup | 3.03 |
| 3.11 generation | 3.07 |
| 3.12 perturbation | 3.08 |
| 3.14 downscaling | 4.04 |
| 3.15 Wflow batches | 4.05 |
| 3.16 legacy table reduction | 4.08–4.10 retained indicator planning/publication |

See [workflow migration](../../milestones/r12/migration-workflow-names.md),
[post-R12 project-tree migration](../../milestones/post-r12/migration-project-tree.md),
[weather-generator seam](../../../reference/contracts/weather-generator-seam.md), and
[hydrological-model seam](../../../reference/contracts/hydrological-model-seam.md).
