# WF3 retained collections, responses and metrics

R12 P2 keeps `run_stress_test.smk` and the existing project/workflow config
files. A normal `snakemake all -s run_stress_test.smk --configfile <project> -c 2`
now publishes three independently identified handoffs:

| Handoff | Location beneath `project_dir` | Readiness marker |
|---|---|---|
| Generated forcing and portable preparation inputs | `scenario_collections/<collection_id>/` | `collection.json` |
| Frozen simulation and native Wflow responses | `experiments/<experiment_name>/` | completed `config/simulation.json` and `responses/response_inventory.json` |
| Selected metrics and their unit membership | `experiments/<experiment_name>/results/metric_sets/<metric_set_id>/` | `metrics.json` |

The collection retains the scenario table, perturbation lookup, generated
forcing, effective-unit interpretation, reduced HydroMT catalog and ancillary
bytes. Preparation reads that retained closure. Temporary model-grid forcing
is still removed after Wflow consumes it. Native response CSVs, reader TOMLs
and temporal evidence remain available for later reduction.

Metric sets contain `<token>_indicators.csv`, `unit_index.csv`, definitions,
execution environment and complete result-key expectations. Class-C wet/dry
month metrics use one shared reference selection and retain one value per run.
Return-level estimator evidence is provisional operational evidence; its
benchmark status remains **not assessed**.

## Selection and invalidation

Without a selector, the source checkpoint resolves the exact project request
at `scenario_plans/<generation_request_id>/plan.json`. It validates current
source bytes, preparation, provider code and environment before reusing the
named collection. Other collections do not affect selection. Missing generated
prerequisites can be produced during this combined P2 workflow; a stale retained
plan refuses reuse rather than falling back to another collection.
The refusal names the exact `snakemake scenarios` command, with
`--forcerun prepare_collection_sources`, to rebuild that mutable plan.

For independent reuse, add only this mapping to the existing WF3 workflow file:

```yaml
scenario_collection:
  manifest_path: /path/to/scenario_collections/<collection_id>/collection.json
```

This mode validates the complete retained collection without opening its
original generation sources. Generation settings can be omitted; the current
stochastic carrier obtains its scheduling shape from the collection. The live
model and `simulation_window` remain simulation inputs. Never configure a
collection digest or a `latest` selector.

A changed collection, model, simulator adapter, environment or simulation
setting requires a new `experiment_name`. Existing native results are never
overwritten. Complete retained responses are validated before scheduling, and
their simulation producers are absent from the resulting DAG. An incomplete
publication is not a supported resume point.

Metrics have their own identity: changing metric selection, definitions,
reference selection or metric execution dependencies selects a new metric set,
without changing simulation identity. Ready sets are immutable; malformed,
partial or byte-changed sets refuse reuse.

## Metrics-only during P2

P2's operation/target gate is an implementation harness; the dedicated public
simulation runner and separate generation entry point are P3 work. To exercise
the current carrier's retained-only operation:

```console
pixi run python dev/milestones/r12/implementation/evidence/p2/current-carrier-runner.py --config <project> --operation metrics-only --target metrics --cores 2
```

The existing WF3 file needs `experiment_name`; optional `metrics` selects
registered variable tokens such as `[q, gwr]`. The project
`climate.water_year_start` supplies the reduction year anchor. The operation
reads frozen simulation/response provenance and its recorded collection; it
defines no generation, preparation or Wflow producers. Live model directories,
generation catalogs and other workflow files are unnecessary. Missing retained
requirements fail before execution. Supplied live generation/model/simulation
settings are reported as ignored. An optional manifest selector can only assert
the same retained collection identity and revision.

Allowed harness targets are `all` for `simulate-and-metrics`, or `metrics`/one
exact selected metric-set file for `metrics-only`. Mixed targets, Wflow targets,
unknown targets and files belonging to another metric set are rejected before
Snakemake launches.

## Retention

Collections are shared across experiments. The library's `list_collections`,
`collection_references` and explicit `delete_collection` operations in
`blueearth_cst.experiment.scenario_collection` report retained state and refuse
referenced deletion unless explicitly forced. No age-based eviction or automatic
cleanup is performed. Do not manually remove a referenced collection or edit
its manifest to repair a failed validation.

P2 retains the predecessor `seed: auto` behavior, which derives the seed from
the experiment name. Use the same explicit seed (or the unchanged default) when
demonstrating cross-experiment generation reuse. Capacity-free automatic seed
resolution and final runner/config migration remain P3 work.
