# WF3/WF4 retained collections, responses and metrics

WF3 `generate_scenarios.smk` publishes durable scenario collections. WF4
`simulate_system.smk`, invoked through `scripts/simulate_system.py`, consumes a
ready collection and publishes native responses and metric sets:

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

Return levels are fitted by `gf15-lmoments-c/1` and each set retains the
closed `return-level-validation/1` declaration plus the
`return_level_benchmark.json` its digest binds. The benchmark status is
**`reviewed_bounded`**: a bounded assessment on synthetic fixtures at the two
production probabilities, not independent or application validation. The
screening policy itself stays **`provisional_operational`** and unvalidated.
Sets published before this estimator retain the earlier
`{provisional_operational, not assessed}` record and stay readable unchanged;
they are never rewritten or relabelled.

## Selection and invalidation

Without a selector, simulation validates the exact project request at
`scenario_plans/<generation_request_id>/plan.json`, including current source
bytes, preparation, provider code and environment. Other collections do not
affect selection. Missing or stale state refuses simulation and names the direct
`generate_scenarios.smk` command required to produce a current collection.

For independent reuse, add only this mapping to the simulation workflow file:

```yaml
scenario_collection:
  manifest_path: /path/to/scenario_collections/<collection_id>/collection.json
```

This mode validates the complete retained collection without opening its
original generation sources. The generation file and its original inputs are unnecessary. The collection
provides scenario membership and its declared simulation window; the live model
remains required for simulation. Never configure a
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

## Metrics-only

Set `operation: metrics-only` in the simulation workflow file, then run:

```console
pixi run python scripts/simulate_system.py --config <project> --target metrics --cores 2
```

The simulation file needs `experiment_name`; optional `metrics` selects
registered variable tokens such as `[q, gwr]`. The project
`climate.water_year_start` supplies the reduction year anchor. The operation
reads frozen simulation/response provenance and its recorded collection; it
defines no generation, preparation or Wflow producers. Live model directories,
generation catalogs and other workflow files are unnecessary. Missing retained
requirements fail before execution. Supplied live generation/model/simulation
settings are reported as ignored. An optional manifest selector can only assert
the same retained collection identity and revision.

Allowed targets are `all` for `simulate-and-metrics`, or `metrics`/one
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

Migration pins every old explicit, default or automatic seed to its resolved
integer. New `seed: auto` is resolved from the versioned generation projection
and actual source content, before collection identity is constructed. Experiment
names, identifier capacity and storage locators do not select stochastic draws.
