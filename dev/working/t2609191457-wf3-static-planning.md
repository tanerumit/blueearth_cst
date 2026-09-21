# WF3 static planning intake

Status: planning intake — not an accepted design or implementation authorization  
Date: 2026-09-19  
Task: [t2609191457](../tasks/t2609191457-make-wf3-planning-static-before-snakemake.md)  
Inspected revision: `8a8b372dee97d2bf0d726975ac1cde3e460c3454`  
Lifecycle: temporary working document; revise in place with an append-only revision log. Promote the eventual accepted specification to the repository's durable reference/decision home before closure.

## Purpose and scope

Request type: **improve** WF3 orchestration. Resolve an authoritative, validated manifest before constructing the generation DAG so that scheduling and the opening console report use the same decisions. Preserve scientific outputs, content identity, strict reuse, and immutable publication. This intake records repository evidence and the decisions needed before a full specification; it neither implements the change nor establishes runtime guarantees.

The principal framing issue is the meaning of “before Snakemake.” A cold project lacks generated source bytes needed by today's identity and seed contracts. A side-effect-free planner cannot calculate those bytes by inspecting configuration. Static planning after explicit source preparation is feasible as a design direction; an exact, fully content-resolved plan before any preparation is not established by the current implementation.

## Capability scope

All repository bindings below are inspected at the immutable revision above. Runtime dependency revisions must later be recorded from the lock files and actual environment; this intake does not invent installed versions.

| Slot | Binding and responsibility | Proposed implementation/validation authority |
|---|---|---|
| `orchestrator` | Snakemake plus repository generation planner and launchers; affected | `python-engineer` implements; CST architect checks dependency and provenance contracts, focused workflow tests check execution |
| `data_adapter` | HydroMT through existing region/climate-store producers; boundary affected, algorithms preserved | `geospatial-data-analyst` assesses source interface; `model-validator` verifies prepared forcing dimensions, units, calendar, coverage and retained ancillary closure |
| `ensemble_generator` | weathergenr through existing R provider scripts; scheduling affected, algorithms preserved | `model-builder` exercises fixture generation; `model-validator` judges preserved seed, pairing, row semantics and forcing outputs |

`decision_framing`, `simulation_engine`, `system_model_validation`, `impact_model`, `performance_analysis`, `robustness_evaluation`, and `projection_overlay` are `not_applicable` to the implementation scope: this change produces a generation plan and scenario collection, not a new decision assessment, hydrological simulation, impact output, performance surface, robustness result or projection overlay. Forcing validation remains required above. Stochastic perturbations remain stress-test forcing; projections remain a terminal plausibility overlay and cannot select or drive generation.

## Current dependency map

Links identify source files; function and rule names identify the inspected seams.

| Boundary | Current behavior and dependencies | Source |
|---|---|---|
| Parse/configuration | `generation_configuration` composes scheduling settings and request path; `stochastic_rows` enumerates roots and descendants from counts and capacity. Rows are already known before execution. | [generation_plan.py](../../blueearth_cst/experiment/generation_plan.py), [scenario_rows.py](../../blueearth_cst/experiment/scenario_rows.py), [generate_scenarios.smk](../../generate_scenarios.smk) |
| Source production | 3.01 delineates region; 3.02 uses region/catalog inputs to produce `extract_historical.nc`, `basin_cells.csv`, and CHIRPS `orography.nc`. 3.03 writes the perturbation lookup. | [snake_utils.py](../../blueearth_cst/shared/snake_utils.py) `region_rule`/`climate_store_rule`; [extract_historical_climate.py](../../blueearth_cst/climate_analysis/extract_historical_climate.py); [prepare_cst_parameters.py](../../blueearth_cst/experiment/prepare_cst_parameters.py) |
| Source resolution checkpoint | `prepare_collection_sources` depends on historical store, basin cells, catalogs, generator template, lookup and conditional orography unless exact ready reuse was validated. `resolve_generation_plan` reads time coverage, source bytes, effective generator settings, provider code and environment, resolves seed and constructs collection intent. | [generation_plan.py](../../blueearth_cst/experiment/generation_plan.py), [collection_resolution.py](../../blueearth_cst/experiment/collection_resolution.py) |
| Portable closure | Preparation planning resolves native elevation adapters and retained catalog bytes; non-CHIRPS elevation comes from its catalog-resolved local source, not the CHIRPS sidecar. Actual ancillary bytes/descriptors must exist. | [prepare_climate_data_catalog.py](../../blueearth_cst/climate_analysis/prepare_climate_data_catalog.py) `resolve_preparation_payloads` |
| Initialization | 3.05 recomputes the live plan, rejects drift, then claims the collection and writes portable inputs plus a receipt tied to the invocation UUID. 3.06 writes generator config from the plan. | [scenario_provider.py](../../blueearth_cst/experiment/scenario_provider.py) `initialize_planned_collection`; [scenario_collection.py](../../blueearth_cst/experiment/scenario_collection.py) `initialize_collection_jobs` |
| Generation and retention | 3.07 generates all unperturbed roots; 3.08 transforms each derived row from its ancestor and lookup. Temporary provider netCDFs feed 3.09 immutable retained row payloads. | [generate_scenarios.smk](../../generate_scenarios.smk), [scenario_provider.py](../../blueearth_cst/experiment/scenario_provider.py) |
| Publication checkpoint | `_collection_publication_inputs` chooses request-only reuse or all retained forcing paths. `publish_scenario_collection` validates and publishes the marker; `_selected_collection` calls this second checkpoint for `all`, logs and benchmarks. Removing only the source checkpoint leaves dynamic expansion. | [generate_scenarios.smk](../../generate_scenarios.smk), [scenario_collection.py](../../blueearth_cst/experiment/scenario_collection.py) `publish_collection` |
| Entry points | Direct WF3 invocation is documented and exercised by CLI tests. `run_workflows.py` invokes WF3 as an ordinary Snakemake subprocess; only WF4 currently has a specialized launcher path. | [run_workflows.py](../../scripts/run_workflows.py) `build_command`; [test_cli.py](../../tests/test_cli.py), [test_run_workflows.py](../../tests/test_run_workflows.py) |

For R realizations and D design points, retained row count is R × (D + 1), including an unperturbed root per realization. That is not an exact scheduled-job count: reuse, existing intermediates, requested targets, force flags and Snakemake's freshness decisions change which jobs run.

## Pure planning, publication and ownership

The existing separation is useful but incomplete for an immutable preflight artifact:

- `generation_configuration` resolves scheduling information without reading generation source contents. `resolve_generation_plan` and `plan_collection` read and validate existing sources and construct intent without writing the collection.
- `write_scenario_request` validates canonical inputs and atomically **replaces** `request.json` under the configuration-derived request namespace. This is rebuildable scheduling state, not an immutable execution snapshot. Atomic replacement prevents a partial JSON read; it does not bind concurrent consumers to the same revision forever.
- Collection initialization creates the collection exclusively, refuses existing partial roots, writes payloads without replacement and issues an invocation receipt. The receipt binds request digest, intent digest, collection ID and invocation ID. Its documented contract explicitly excludes later-invocation recovery, leases or ownership transfer.
- Publication validates retained artifacts and writes `collection.json` last. Producer reuse verifies live inputs; portable consumer reading validates retained contents without requiring original sources. Preserve this distinction.

A proposed manifest needs separate semantic identity and invocation/scheduling fields. Freeze scenario rows, source/config/code/environment digests, selected full collection identity, expected paths and reuse decision without placing volatile invocation IDs into scientific identity. Determine whether immutable plan files plus a replaceable request pointer are appropriate, or whether existing request records can remain pointers consumed only through a pinned snapshot. Recheck stale inputs before execution; an immutable plan alone cannot freeze a mutable climate store.

A pure planner may return canonical bytes; an explicit persistence operation may publish those bytes atomically. Calling the entire command “side-effect-free” while it writes a manifest obscures the boundary. Dry-run must not hide extraction, initialization or collection publication. Define whether explicitly requested plan-file persistence is allowed in dry-run separately from scientific-output mutation.

No managed project run is proposed or started here. Run-control conformance, resource claims, fencing and namespace ownership are **not assessed or claimed** by this intake. If the subsequent design targets managed roots, apply `cst-run-control` and establish its required intent/namespace gates before `ready`; do not equate today's collection receipt with that full contract.

## Alternatives and recommendation

| Approach | Benefit | Cost / when preferable |
|---|---|---|
| **Explicit source preparation, then immutable plan and static generation DAG** (recommended for framing) | Preserves content-derived seed and identity; one shared planner can serve direct and all-workflow entry points; both generation checkpoints can be replaced with ordinary static dependencies. | Exact generation counts become available after preparation, not before a cold start. Requires an honest preparation command/phase and a documented missing-source dry-run result. |
| Retain current dynamic DAG | Preserves current one-invocation cold-start behavior and minimizes migration risk. | Cannot satisfy exact upfront downstream planning; preferable only if the owner values that invocation contract above exact planning. |
| Redesign execution paths/identity to schedule cold starts from config alone | Could make initial topology static with request-based staging paths and later content sealing. | Much broader identity, publication, reuse and migration problem; exact reuse choice still depends on unavailable bytes. Appropriate only with explicit acceptance of a wider task, not as a shortcut in this one. |

The recommended preparation phase is a bounded source-only target using the existing region, extraction and lookup producers, followed by a shared planner and static generation invocation. Its subgraph must be proven before extraction into a new entry point. This is distinct from merely wrapping today's two checkpoints: the durable validated manifest becomes authoritative, and the generation DAG no longer discovers its collection through either checkpoint. Exact command names and manifest schema remain undecided.

## Preserved semantics and unresolved framing

Preserve automatic versus explicit seed behavior, effective-generator seed projection, water-year and temporal coverage, realization pairing across design points, row order/IDs/capacity, provider-code and environment identity, source and preparation closure, temporary intermediate cleanup, and immutable retained outputs. Never alias the identity perturbation to an unperturbed root without a separately justified scientific change. Do not alter Wflow or couple WF3 to WF2.

Resolve these decisions before detailed implementation design:

1. Does “upfront” mean before the generation DAG after source preparation, or before any preparation? The owner's answer governs feasibility and scope.
2. Does direct `snakemake ... -s generate_scenarios.smk` remain a supported public entry point requiring a pre-existing manifest, or migrate to a launcher with an explicit missing-plan error? Both direct and all-workflow paths must use the same planner/validator.
3. What can cold-start dry-run report when no source bytes exist: source DAG plus an explicit blocked final plan, or refusal with a preparation instruction? Neither should silently claim exact full-run counts.
4. Does this task preserve current refusal of interrupted partial collections, or intentionally add resume? Recommend preserving refusal here; adding resume requires a separate ownership/state contract.
5. How is reuse fixed between planning and execution if another invocation publishes or mutates shared sources? Specify refusal/replan behavior, plan lifetime and source stability rather than silently changing a frozen execution branch.
6. Does “exact count” cover the final selected target DAG and its scheduled jobs under current flags, or a manifest's potential jobs? Recommend the former, with the manifest supplying authoritative decisions and Snakemake supplying the actual schedule.

## Bounded next steps and evidence gates

| Problem → change | Impact and affected stages | Proposed owner / acceptance evidence |
|---|---|---|
| Undefined source boundary → confirm framing and inventory source-only target | Establishes cold-start and dry-run contract; 3.01–3.04 | CST architect; complete source-only dry-run with generation inputs deliberately absent, no unintended generation jobs |
| Mutable request used as execution authority → specify versioned immutable snapshot, validation and pointer relationship | Stable scheduling under concurrent requests; planning/init/reuse | `python-engineer` after specification; canonicalization, stale-byte and concurrent-reader cases including preserved mtimes |
| Two checkpoints hide schedule → ordinary rules driven by validated plan | Complete generation DAG; 3.05–3.12 and `all` | `python-engineer`; fresh/prepared/reuse DAG job inventories, explicit targets and force/rerun flags; no checkpoint-dependent callbacks |
| Entrypoints differ → shared preflight contract and documented migration | Same decisions through direct and all-workflow invocation | `python-engineer`; focused CLI and runner contract tests, dry-run filesystem comparison |
| Refactor could weaken publication → preserve refusal and validation handoffs | Collection integrity and scientific parity | `model-builder` runs isolated fixture; `model-validator` returns acceptance against unchanged rows, seeds, forcing metadata and appropriate output comparisons; failure/reuse snapshots preserve retained bytes |

Start from existing [seed tests](../../tests/test_generation_seed_projection.py), [resolution tests](../../tests/test_collection_resolution.py), [provider tests](../../tests/test_scenario_provider.py), [collection tests](../../tests/test_scenario_collection.py) and [preparation tests](../../tests/test_collection_preparation.py). Add missing manifest-boundary coverage rather than assuming these tests prove the new design.

Empirical checks required later: cold versus prepared source states; missing/replaced plan; valid and corrupt ready collection; source/template/catalog/code/environment drift; simultaneous plan publication and competing initialization; failure before/after receipt and before final marker; successful forced reuse and refusal with retained-byte snapshots. `update(...)` alone does not prove retained outputs survive Snakemake failed-job cleanup. Execute a small real R/provider boundary smoke as well as dry-runs; parse success cannot check runtime script paths. Use isolated project outputs, never the comparison baseline as the run destination.

Validation performed for this intake: read-only source and existing-test inspection, document self-review. No workflow, extraction, model run, test suite or numerical comparison was executed. Source-only isolation, exact counts, runtime preservation, performance and concurrency remain unproven. Future modeling stages are not integrated until the named validation handoff returns.

## Revision log

- 2026-09-19 — Initial planning intake; identified both checkpoint boundaries, generated-source identity blocker, current claim/reuse contracts, alternatives and pending framing decisions.
