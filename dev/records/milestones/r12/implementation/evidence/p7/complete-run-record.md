# P7 complete-run acceptance record

P7 completed on the isolated rapid output root
`test_case/test_p7_complete_referencefixed`. This root was freshly created for
the final evidence run. Earlier `test_p7_complete_sealed` output is not P7
acceptance evidence because its immutable v2 metric marker carried malformed
result references; `c56d0fc0` corrected the writer and the final root was
rerun without modifying that earlier output.

## Fresh execution and records

```powershell
pixi run python scripts/run_workflows.py `
  --config .tmp\scratchpad\2026-10-01_1320\project_config_p7.yml `
  --project-dir test_case\test_p7_complete_referencefixed --cores 3

pixi run python scripts/simulate_system.py `
  --config .tmp\scratchpad\2026-10-01_1320\project_config_p7_metrics.yml `
  --project-dir test_case\test_p7_complete_referencefixed `
  --target metrics --cores 3
```

Both commands exited zero. The first completed WF0 through WF4. The
metrics-only DAG ran only 4.08 `prepare_metric_plan`, 4.09
`publish_metric_set`, and 4.10 `metrics`; it did not schedule a generation,
model, forcing-preparation, or native Wflow producer.

| Record or artifact | Fresh-path fact |
|---|---|
| Collection | `scenarios/_engine/collections/124b18ca34c2/collection.json`, `scenario-collection/2`, ready |
| Simulation intent | `experiments/experiment_rapid/_engine/simulation_intent.json`, `simulation-intent/1` |
| Ready simulation | `experiments/experiment_rapid/_engine/simulation.json`, `simulation/2`, ready |
| Response inventory | `experiments/experiment_rapid/_engine/response_inventory.json`, `response-inventory/2` |
| Metric request | `experiments/experiment_rapid/_engine/metric_requests/7d7bcc17b7a8.json`, `metric-request/2` |
| Metric set | `experiments/experiment_rapid/_engine/metric_sets/1b638e8b1eae/metrics.json`, `metric-set/2`, ready |
| Model reference | `experiments/experiment_rapid/_engine/model_reference.yml` |

The metric marker resolves its lookup and tables from the experiment root:
`results/metric_sets/1b638e8b1eae/`. Its lookup has
`run_group_id,grain,run_id`; the three indicator tables have
`metric,location,run_group_id,value` and contain 580 rows in total (40 AET,
40 GWR, and 500 discharge). The response inventory validates ten native
output CSV artifacts and 130 response series. Wflow retained ten native logs
at `hydrology/wflow/output/_log/run_01.log` through `run_10.log`.

The production readers successfully validated the fresh collection,
simulation, response inventory, and metric set. The only `.snakemake_timestamp`
files in the root are Snakemake directory sentinels under climate/model plot
directories; no `.partial` or ordinary temporary artifacts were retained.

## Scientific continuity

The P0 explicit-seed reference comparison passed against the fresh root:

```powershell
pixi run python .tmp\scratchpad\2026-09-21_1541\p5_scientific_compare.py `
  .tmp\scratchpad\2026-09-21_1541\prechange-wf3-reference\explicit-123-c-root\project `
  test_case\test_p7_complete_referencefixed
```

All ten forcing members and both 16,790-row date files were byte-identical.
Across each of the seven forcing variables, the comparator found zero
mismatches and zero maximum absolute and relative difference over 3,358,000
values. It also rejected both a changed forcing value and swapped member
association.

The independent predecessor WF4 comparison also passed:

```powershell
pixi run python .tmp\scratchpad\2026-09-21_1541\p6_scientific_compare.py `
  .tmp\scratchpad\2026-09-21_1541\prechange-wf4-reference\project `
  test_case\test_p7_complete_referencefixed
```

It rejected changed metric and native values plus swapped bundle membership,
then matched all 130 native response series (427,180 values) exactly and all
580 metric keys with maximum absolute difference `0.0`.

The dedicated automatic-seed/exclusion controls also passed:

```powershell
pixi run pytest `
  tests/test_scenario_collection_v2.py::test_wf4_only_evidence_does_not_enter_seed_or_collection_identity `
  tests/test_scenario_collection_v2.py::test_wf3_code_closure_ignores_wf4_only_source_bytes `
  tests/test_scenario_collection_v2.py::test_explicit_and_auto_requests_with_same_seed_share_collection_identity -q
```

These tests recompute `generation-seed-material/2` through the canonical
digest-to-31-bit formula, demonstrate that WF4 elevation/settings evidence
does not alter the automatic seed or collection identity, and mutate actual
WF4-only source files without changing the WF3 provider inventory.

## Implemented-fact correction

`simulation_intent.json` intentionally remains `simulation-intent/1`; P6's
implementation record previously labelled it `/2`. The P6 evidence table is
corrected here and no runtime schema change is implied.
