# Migration — separate scenario generation and system simulation

R12 replaces `run_stress_test.smk` with `generate_scenarios.smk` (wf3) and
`simulate_system.smk` (wf4). There is no compatibility wrapper. Simulation must
be invoked through `scripts/simulate_system.py` or `scripts/run_workflows.py`.

## Migrate configuration

```console
pixi run python scripts/migrate_project_config.py <project-config.yml>
```

The tool splits the old `workflows.run_stress_test` stanza into
`workflows.generate_scenarios` and `workflows.simulate_system`, writes their
settings beside the project file, and preserves the old resolved integer seed.
The schema remains version 2. An unmigrated stanza is refused with this migration
command. Legacy v1 inputs first receive the existing v1-to-v2 transformation;
its declared exceptions still apply. See [configuration migration](migration-config-shape.md).

Generation owns `n_realizations`, `simulation_window`, `climate_perturbations`,
`weathergen_config`, `seed` and `unit_id_capacity`. Simulation owns
`experiment_name`, `operation`, optional `scenario_collection.manifest_path`,
compute controls and metric selection. Shared keys remain in project-level
`basin`, `climate` and `model` sections. `config_path` is relative to the project
file; ordinary paths retain the working-directory anchor.

## Replace commands

```console
python scripts/run_workflows.py --config <wf3-only-project-config.yml> --project-dir <project-dir> --cores 3
python scripts/simulate_system.py --config <project-config.yml> --target all --cores 3
```

For generation alone, disable the other workflow stanzas in that project config.
The all-workflow runner uses analyze_climate → build_model → analyze_projections
→ generate_scenarios → simulate_system. This is a convenience sequence, not a
chain of scientific dependencies. Generation is model-independent; simulation
requires a ready collection and model. CMIP6 remains a terminal plausibility
overlay. WF0 is optional and should run first or alone for forcing selection.

For retained reduction, set `operation: metrics-only`, keep the existing
`experiment_name`, and use `--target simulations_and_indicators`. The all-workflow runner accepts
`--simulation-target simulations_and_indicators`; disable other stages for a retained-only run.
Default target `all` does not infer an operation. Mixed targets and simulation
targets in metrics-only mode are refused before Snakemake launches.

## Existing outputs

Nothing is renamed inside an existing project. Generate a new collection and
use a new experiment namespace. The old `(rlz, st_id)` keys are recorded in the
scenario table; portable readers use `run_id`, not filename parsing.

| Artifact | Current path under project_dir |
|---|---|
| Exact generation selection | `scenarios/requests/<generation_request_id>/request.json` |
| Ready collection | `scenarios/collections/<collection_id>/collection.json` |
| Durable generated forcing | `scenarios/collections/<collection_id>/forcing/run_<run_id>.nc` |
| Prepared model forcing | `experiments/<name>/hydrology/wflow/forcing/inmaps_run_<run_id>.nc` (temporary) |
| Native response | `experiments/<name>/hydrology/wflow/output/run_<run_id>.csv` |
| Native response inventory | `experiments/<name>/responses/response_inventory.json` |
| Metric set | `experiments/<name>/results/metric_sets/<metric_set_id>/metrics.json` |

Metric tables contain `metric,location,unit_id,value`. The accompanying
`unit_index.csv` maps run and bundle units to explicit scenario membership.
Class-C values are per run using the shared reference month; their bundle mean
has the accepted predecessor relation. Return-level fits remain provisional
operational results; GF-15 benchmark qualification is separately gated.

Missing or stale routine selection names the exact generation command; simulation
never rebuilds a collection or falls back to a different one. An explicit
`scenario_collection: {manifest_path: ...}` validates retained preparation inputs
without their original sources. See [retained handoffs](wf3-retained-handoffs.md)
and [ADR 0009](../dev/decisions/0009-split-scenario-generation-and-system-simulation.md).
