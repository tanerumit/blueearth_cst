---
title: "WF4 — Simulate system"
format: html
---

`simulate_system.smk` runs Wflow-SBM for explicit runs from a ready WF3 collection, then reduces retained
native responses to named indicator sets. Invoke it through `scripts/simulate_system.py` or the all-workflow
runner. The wrapper validates selection before Snakemake and publishes named results afterward.

## Rules

| Rule | Operation |
|---|---|
| `all` | Collect the selected result targets |
| 4.01 `write_model_fingerprint` | Record the model reference |
| 4.02 `check_model_unchanged` | Verify the model against that reference |
| 4.03 `snapshot_simulation_inputs` | Freeze collection, model, settings and environment identity |
| 4.04 `downscale_scenario_series` | Prepare forcing per run |
| 4.05 `run_wflow_simulations_batch_<batch>` | Execute Julia batches and retain native responses |
| 4.06 `publish_wflow_outputs` | Validate and publish the response inventory |
| 4.07 `prepare_indicator_plan` | Resolve distinct numerical requests and targets |
| 4.08 `derive_system_indicators` | Produce immutable tables, coverage and ready marker |
| 4.09 `gather_logs` | Gather rule logs |
| 4.10 `gather_benchmarks` | Gather benchmark parts |

## Rule flow

Model verification and input snapshots precede forcing preparation and Wflow batches. Response publication
precedes indicator planning and reduction. `simulations_only` stops at responses;
`simulations_and_indicators` collects indicators. Indicators-only operations start from validated retained
responses and never launch Wflow. Independent batches/sets can continue under `--keep-going` when another
fails. A final successful verdict requires all requested publications to be current under the chosen
evaluation mode; completion of a batch is not that verdict.

## Configuration

The project owns `model.outvars`, basin/climate context and the workflow enablement/file path.
The WF4 file owns `experiment_name`, `scenario_collection`, `include_unperturbed`, operations, indicator
requests and `compute`. See [indicator requests](indicator-requests.md) for the exact request syntax.

Routine collection selection comes from the project's generation plan. The advanced
`scenario_collection` mapping accepts exactly `{manifest_path: <collection.json>}` and resolves that ready
collection's run inventory; it does not accept an arbitrary run-ID list. A pending project-generation seed
may be bound from a validated existing generation plan
with WF3 disabled; an already-bound seed is preserved. This does not regenerate scenarios.
The selected collection marker must lie within this project root; cross-project manifest paths are refused.

`include_unperturbed` defaults to `true`. With `false`, WF4 skips forcing/simulation for root reference
members; WF3 retains them for ancestry. Indicators requiring those references need them included.
Experiment naming and reuse rules are in [configuration](configuration.md#workflow-settings).

| `compute` field | Meaning and precedence |
|---|---|
| `julia_threads` | Positive threads per batch; overrides automatic basin-size selection |
| `max_parallel_batches` | Positive batch concurrency; resource constraints can reduce effective concurrency |
| `batch_size_max` | Optional positive cap on members per batch |
| `batch_size` | Explicit positive size overrides automatic sizing |
| `disk_headroom_gb` | Nonnegative absolute reserve; otherwise the advanced free-disk fraction applies |

The batching policy uses active model cells and memory/core/disk constraints. Automatic large-basin
choices are provisional rather than a performance guarantee. `scripts/calibrate_batching.py` measures a
case; [resource records](execution-and-provenance.md#wf4-resource-diagnostics) report what actually ran.

## Inputs

WF4 requires the completed WF1 model and an explicitly resolved ready collection/run selection. It does
not read WF2 projections. The response request freezes variables, ordered locations, units and daily time
interpretation before simulation. Changed model/input identity is refused; use a new experiment rather
than altering retained records. Indicator-only requests check retained variables and locations.

## Outputs

Native Wflow CSVs and their response inventory remain in the experiment. Immutable indicator sets retain
declarations, tables, group membership, coverage, return-level evidence and execution context.
Each selected set gets a readable `results/indicator_sets/<set-id>/` view. See
[retained handoffs](retained-handoffs.md) for exact paths, schemas, statuses and joins.

## Local calculation sets

The [extension chapter](indicator-extension.md) declares inclusion of the independent module and all five
canonical set READMEs. Crop-water preparation, ERFA defaults, flow-regime additions and flood qualification
limits stay in those local sources. The full `flood_risk` example set includes unsupported probabilities;
select an eligible 2- or 10-year declaration explicitly, as shown in [requests](indicator-requests.md).

## Integrity and numerical rechecking

See [inspection commands and limits](indicator-requests.md#integrity-and-numerical-rechecking).
Integrity inspection does not make stale results reusable; numerical rechecking has additional prerequisites.

Executable owners: `scripts/simulate_system.py`, `simulate_system.smk`, `experiment/collection_resolution.py`,
`indicator_sets.py`, `indicator_plan.py`, `indicator_export.py` and `response_inventory.py`.
Tests: `tests/test_indicator_sets.py`, `tests/test_partial_indicators.py` and
`tests/test_named_indicator_sets_workflow.py`.
