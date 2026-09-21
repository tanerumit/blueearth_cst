# WF3/WF4 retained collections, responses and metrics

WF3, invoked through `scripts/run_workflows.py` or
`scripts/generate_scenarios.py`, publishes durable scenario collections. Its
owned launcher first prepares sources, freezes a content-derived plan, then
runs generation. Direct `snakemake -s generate_scenarios.smk` is refused.

The v2 collection reader validates the ready marker at
`scenarios/_engine/collections/<collection_id>/collection.json`; retained
series and provider products live at `scenarios/<collection_id>/`. WF4's v2
consumer is introduced in P6; until then it refuses a v2 collection.

WF4 `simulate_system.smk`, invoked through `scripts/simulate_system.py`,
publishes native responses and metric sets after it can consume a ready
collection:

| Handoff | Location beneath `project_dir` | Readiness marker |
|---|---|---|
| Generated forcing and creator archive | `scenarios/<collection_id>/` | `scenarios/_engine/collections/<collection_id>/collection.json` |
| Frozen simulation and native Wflow responses | `experiments/<experiment_name>/` | completed `config/simulation.json` and `responses/response_inventory.json` |
| Selected metrics and their unit membership | `experiments/<experiment_name>/results/metric_sets/<metric_set_id>/` | `metrics.json` |

The v2 collection retains `series/run_<id>.nc`, the scenario and perturbation
lookups, date-selection CSVs, diagnostic plots, installed generator YAML, and
the creator `config/run_record.yml` with exact config sources. Root and
perturbed generator netCDFs under `weathergenr/output/` are temporary.
Temporary model-grid forcing is removed after Wflow consumes it. Native
response CSVs, reader TOMLs and temporal evidence remain available for later
reduction.

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

WF3 publishes an immutable `scenario-request/2` pointer under
`scenarios/_engine/requests/<generation_request_id>/request.json`. The pointer
selects a frozen plan by byte digest; execution reads that pinned plan directly.
Ready reuse checks the creator's collection and archive without rewriting their
bytes. A missing or partial collection namespace requires a fresh project or
explicit repair. P6 adds WF4 selection of v2 collections from the ready marker;
the current WF4 runner refuses this marker until that consumer is integrated.

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
