# Complete-run output tree and record schemas — current working proposal

- Status: working proposal — not an implementation brief or an implemented schema
- Date: 2026-09-21
- Inspected code: bb200682 (documentation follow-up; runtime code unchanged)
- Location: session-1, refactor/wf3-static-planning
- Lifecycle: temporary working document; revise in place, append revision history. Promote the accepted contract to dev/reference/ before closing the work.

## 1. What this document shows

This is a proposed output-project tree after a successful WF0–WF4 run, compared with the existing layout and generated metadata. “Output tree” means the contents of project_dir, not the Git worktree holding the toolbox.

The proposal brings together exact configuration archives, execution history, shared elevation data and the prospective WF3 static plan. It does not change the climate experiment, Wflow physics or metric definitions. WF2 remains a projection plausibility overlay; it does not supply generation scenarios.

Read §2–3 for the tree and plain-language decisions; §4–8 for schema comparisons; §9–11 for migration, unresolved choices and the outline of a future task brief. The detail is retained because the next reader needs to distinguish a renamed record from a changed scientific contract.

**Evidence boundary.** No new full run was executed for this document. The proposed writers do not exist yet. Current examples were inspected in session-1's test_case/test_local and test_case/test_rapid, alongside their writers. These are accumulated output trees, not evidence of one clean run at the inspected code revision. The local collection c3f88ea5c76f has a ready marker and 14 retained entries currently named forcing; its experiment is named experiment. This inspection did not revalidate the scenario-series bytes or numerical results. Rapid supplies examples of WF0 records and wrapper invocation history. Its older retained collections do not have the artifact-local composed snapshot now written by current code.

Decision authority remains in [ADR 0011](../decisions/0011-preserve-config-sources-with-run-records.md). The static-planning boundary remains in [the WF3 intake](t2609191457-wf3-static-planning.md). This document is the single latest working output-schema proposal: what would a user find in a completed output project, and what would each record contain? Integrate future layout and schema proposals here rather than maintaining competing trees. ADRs, task notes and migration records retain decision history; this document does not silently turn their open proposals into approvals. New field names and version labels below are draft suggestions, not approved APIs.

The latest proposed tree incorporates a **seven-to-two reduction in collection JSON files** (§8), a collection-centred `scenarios/` layout with one scenario-level `_engine/` (§3.2), shared elevation (§7), exact source archives (§4), common invocation history (§5), static planning (§6), and consolidation of the simulation family under the experiment engine directory (§8.3). The seven-to-two collection mapping and simulation contract are working recommendations, not recovered prior approvals. The decision/TODO reconciliation is included in §3.1.

## 2. Existing and proposed output trees

### 2.1 Existing layout

This combines observed outputs with the current writers' contract. Angle-bracket names stand for actual workflow, collection, request or experiment identifiers. Repeated rows, time series, figures, logs and model internals are grouped; this is not an exhaustive file listing.

~~~text
<project_dir>/
├── config/
│   ├── runs/
│   │   ├── README.md
│   │   ├── analyze_climate/       # WF0; optional
│   │   │   ├── composed_config.yml
│   │   │   └── run_record.yml
│   │   ├── build_model/           # same two files
│   │   ├── analyze_projections/   # same two files
│   │   └── _engine/
│   │       ├── journal.jsonl
│   │       └── invocations/
│   │           ├── <timestamp-and-id>.json  # all-workflow wrapper
│   │           └── simulation-<id>.json    # simulation launcher
│   ├── basin_data/               # archived basin inputs, when configured
│   ├── catalogs/                 # conditional custom copies
│   ├── templates/                # conditional custom copies
│   └── generated/                # legacy destination; not always populated
├── data/
│   ├── spatial/                  # maps, geoms, registry, catalog, report, plots
│   └── climate/
│       ├── historical/<source_window>/
│       │   ├── extract_historical.nc
│       │   ├── basin_cells.csv
│       │   └── ...               # source-dependent sidecars and analyses
│       └── projections/cmip6/    # retained series, summaries and provenance
├── models/hydrology/wflow/
│   ├── hydromt_build_config.yml
│   ├── hydromt_update_waterbodies.yml
│   ├── hydromt_data.yml
│   ├── wflow_sbm.toml
│   └── ...                       # static maps, forcing, run_default, evaluation
├── scenarios/
│   ├── requests/<request-id>/
│   │   ├── request.json
│   │   ├── initializations/<invocation-id>.json
│   │   └── generation/           # provider config and working artifacts
│   └── collections/<collection-id>/
│       ├── composed_config.yml   # current writer; absent in older outputs
│       ├── collection_intent.json
│       ├── collection.json       # ready marker written last
│       ├── generation_config.json
│       ├── generation_environment.json
│       ├── provider_code_inventory.json
│       ├── source_inventory.json
│       ├── preparation_context.json
│       ├── preparation_catalog.yml
│       ├── ancillary/elevation/era5_orography_2018.nc
│       ├── scenario_table.csv
│       ├── stress_test_lookup.csv
│       └── forcing/run_<id>.nc
├── experiments/<name>/
│   ├── config/
│   │   ├── composed_config.yml
│   │   ├── simulation.json
│   │   ├── model_reference.yml
│   │   ├── simulator_settings.json
│   │   ├── simulation_environment.json
│   │   ├── simulator_adapter_code_inventory.json
│   │   └── response_request.json
│   ├── _engine/
│   │   ├── response_inventory.json
│   │   └── metric_requests/<id>.json
│   ├── hydrology/wflow/          # run configs and retained native responses
│   └── results/metric_sets/<id>/
│       ├── metrics.json
│       ├── metric_environment.json
│       ├── return_level_benchmark.json
│       ├── unit_index.csv
│       └── ...                   # indicator tables
├── logs/
└── benchmarks/
~~~

### 2.2 Proposed layout after a complete run

The example assumes all five workflows are enabled, one newly generated collection, one new experiment and one metric set. WF0 is optional in general. Multiple collections and metric sets repeat their own branches. Names use the rapid seed convention for illustration; no new collection ID is predicted.

Legend: [new] introduced here; [changed] content, packaging or ownership changes; [kept] current role/contract retained. This is the preferred working proposal, not a tree emitted by current code. A successful coordinated launch would normally leave a parent invocation and five child invocation records under the proposed launcher coverage. Source preparation belongs to the WF3 child's phases; it does not masquerade as a sixth workflow.

~~~text
<project_dir>/
├── config/
│   ├── runs/
│   │   ├── README.md                         [changed]
│   │   ├── _engine/invocations/
│   │   │   ├── <parent-id>.json              [changed: common schema]
│   │   │   └── <workflow-invocation-id>.json  [new/common: one per child]
│   │   ├── analyze_climate/
│   │   │   ├── run_record.yml                [changed: full loaded config]
│   │   │   └── sources/                      [new: original bytes/names]
│   │   │       ├── project_config_rapid.yml
│   │   │       └── project_config_rapid_analyze_climate.yml
│   │   ├── build_model/
│   │   │   ├── run_record.yml
│   │   │   └── sources/
│   │   │       ├── project_config_rapid.yml
│   │   │       └── project_config_rapid_build_model.yml
│   │   └── analyze_projections/
│   │       ├── run_record.yml
│   │       └── sources/
│   │           ├── project_config_rapid.yml
│   │           └── project_config_rapid_analyze_projections.yml
│   └── basin_data/                           [kept]
├── data/
│   ├── spatial/                              [kept]
│   └── climate/
│       ├── historical/                       [kept]
│       ├── projections/                      [kept]
│       └── ancillary/era5/<content-sha256>/   [new: candidate version scheme]
│           └── era5_orography_2018.nc
├── models/hydrology/wflow/                    [kept: engine configs stay here]
├── scenarios/
│   ├── <collection-id>/                       [changed: user-facing collection]
│   │   ├── config/                            [new: user-level configuration account]
│   │   │   ├── run_record.yml                 [new: replaces composed snapshot]
│   │   │   └── sources/                       [new: exact user-provided YAML bytes]
│   │   │       ├── project_config_rapid.yml
│   │   │       └── project_config_rapid_generate_scenarios.yml
│   │   ├── weathergenr/                       [new: provider integration]
│   │   │   ├── weather_generation_input.yml   [changed: resolved executable input]
│   │   │   ├── output/                        [changed: retained date-selection products]
│   │   │   │   ├── sim_dates.csv
│   │   │   │   └── resampled_dates.csv
│   │   │   └── evaluation/plots/              [changed: conditional generator diagnostics]
│   │   ├── preparation_catalog.yml           [changed URI; retain HydroMT schema]
│   │   ├── scenario_table.csv                 [kept]
│   │   ├── stress_test_lookup.csv             [kept]
│   │   └── series/run_<id>.nc                  [changed: scenario time series, not forcing]
│   └── _engine/                              [new: one scenario-level machine-contract bin]
│       ├── requests/<request-id>/
│       │   ├── request.json                   [changed: discovery pointer]
│       │   ├── <plan-sha256>.json              [new: immutable execution plan]
│       │   └── initializations/<invocation-id>.json [kept role; binding changes]
│       └── collections/<collection-id>/
│           ├── collection_intent.json        [changed: embeds five JSON sidecars]
│           └── collection.json               [changed binding; final ready marker]
├── experiments/<name>/
│   ├── config/
│   │   ├── run_record.yml                    [new: replaces composed snapshot]
│   │   └── sources/
│   │       ├── project_config_rapid.yml
│   │       └── project_config_rapid_simulate_system.yml
│   ├── _engine/
│   │   ├── simulation_intent.json            [new: frozen scientific inputs]
│   │   ├── simulation.json                   [changed: final readiness marker]
│   │   ├── response_inventory.json           [kept]
│   │   ├── metric_requests/<id>.json          [kept]
│   │   └── metric_sets/<id>/
│   │       ├── metrics.json                  [changed: ready marker; embeds environment]
│   │       └── return_level_benchmark.json  [moved: exact retained validation report]
│   ├── hydrology/wflow/
│   │   ├── run_settings/
│   │   │   ├── run_<id>.toml                  [changed: retained Wflow run settings]
│   │   │   ├── run_<id>.yml                   [temporary: HydroMT data catalog]
│   │   │   └── run_<id>.temporal.json         [temporary: per-run validation handoff]
│   │   ├── forcing/inmaps_run_<id>.nc         [temporary: Wflow-ready forcing]
│   │   └── output/
│   │       ├── run_<id>.csv                   [kept: retained native response]
│   │       └── _log/run_<id>.log              [changed: retained Wflow run log]
│   └── results/metric_sets/<id>/
│       ├── unit_index.csv                    [kept: run/bundle membership]
│       └── <token>_indicators.csv            [kept: user-facing metric tables]
├── logs/                                     [kept]
└── benchmarks/                               [kept]
~~~

Each sources/ also holds required custom catalogs and engine templates, preserving their original names and relative structure. The two-file examples are not a claim that all archives contain exactly two files. Unmodified toolbox files may instead be recoverable through recorded revision/blob identity.

New collections have two scientific JSON documents in `scenarios/_engine/collections/<collection-id>/` instead of seven in the old collection root; the five sidecar payloads become embedded intent sections, not discarded evidence. Request plans and initialization receipts are outside that count. The user-facing collection groups exact creator configuration, a provider-specific `weathergenr/` integration subtree and provider-independent scenario products under `series/`. The archive belongs to the collection's creator; a later equivalent request records its own attempt without overwriting these sources. The large intermediate realization netCDFs remain temporary under the existing Snakemake contract; their retention is not silently expanded by this layout. `series/run_<id>.nc` denotes the current stochastic collection's retained climate time series, not Wflow-ready forcing or a mandatory folder for every future scenario type. WF4 owns any subsequent conversion or selection for a system model. New experiments keep the human-facing archive under `config/` and the frozen scientific records directly under `_engine/`.

New outputs stop writing composed_config.yml, journal.jsonl and the central config/catalogs, config/templates and config/generated archive destinations. Existing copies are legacy data and are not deleted by this proposal. A fresh tree has no collection-local ancillary/elevation directory under the new contract. CHIRPS extraction sidecars are not automatically relocated merely because the ERA5 source dependency moves.

## 3. Decisions in plain language

| ID | Direction | Why / practical consequence | Standing |
|---|---|---|---|
| D1 | Keep the original YAML files exactly as read, beside one generated run record. | The user keeps comments and filenames; the generated record explains the values that were loaded. | ADR 0011 proposal |
| D2 | Keep WF0–WF2's latest configuration account; keep WF3/WF4 accounts with their own artifacts. | A second collection must not overwrite the first collection's provenance. Reuse must not rewrite the creator's account. | ADR 0011 proposal |
| D3 | Use one invocation JSON format for all entry points. | A reader can distinguish an attempt, a dry-run, a no-op and a failed execution without joining unrelated log formats. | ADR 0011 proposal |
| D4 | Put source elevation in shared project data and verify it by checksum. | Two collections can share identical elevation bytes. Copying the whole project preserves their dependencies. | User-agreed ownership; exact paths still proposed |
| D5 | Prepare sources first; freeze the WF3 plan before constructing its generation DAG. | Content-derived identities cannot be known before required source bytes exist. | WF3 intake recommendation; not yet accepted |
| D6 | Keep scientific manifests separate from the human-facing record. | A readable YAML account is not proof that a collection or simulation is complete. Existing strict readers remain meaningful. | Preserved boundary |
| D7 | Preserve older sealed outputs and read their old schemas. | A layout improvement must not rewrite the evidence of a previous assessment. | Required migration constraint |
| D8 | Embed the five collection provenance sidecars in collection_intent.json; retain collection.json separately. | Seven collection JSONs become two, while intent and completed outputs retain distinct lifetimes. | Current recommendation; no earlier approval of this mapping located |
| D9 | Embed the five frozen simulation input documents in _engine/simulation_intent.json and publish a separate _engine/simulation.json completion marker; keep run_record.yml and sources/ under config/. | Exact scientific inputs remain verifiable while immutable intent and completed-output claims have separate lifetimes; a two-file family needs no dedicated folder. | Extends t2609171500; versioned reader and identity migration required |
| D10 | Preserve separate request and collection identities, 12-character path prefixes and full digests, but put their records in one `scenarios/_engine/` bin. | Multiple requests can select one user-facing collection without displaying two sibling user trees. | Identity and prefix rules landed post-R12; placement is this working proposal |
| D11 | Keep `config/` for the collection's user-level configuration account; put the resolved `weather_generation_input.yml` and generator products under `<provider>/`. | Exact `project_config_*` sources, the run record and provider-specific settings remain distinguishable without a generic `generated/` bin. | Owner-directed naming for the working layout; no Wflow filename change |
| D12 | Name retained WF3 climate time series `series/run_<id>.nc`, reserving `forcing/` for a system-model-ready input at the WF4 boundary. | Generated scenarios may need post-processing or may never become a model forcing. | Owner-directed semantic correction; path and manifest migration proposed |
| D13 | Rename the experiment's Wflow `config/` directory to `run_settings/`; retain per-run TOML, but retain common temporal evidence only in `response_inventory.json`. | Distinguishes generated Wflow run settings from user configuration and avoids one duplicate temporal JSON per run. | Owner-confirmed working layout; versioned selector migration required |
| D14 | Keep Wflow's per-run logs under `hydrology/wflow/output/_log/`, beside but separate from native response CSVs. | `output/` stays easy to scan for response data while preserving each Wflow diagnostic log and its run attribution. | Owner-confirmed working layout; update `logging.path_log` and create the directory before execution |
| D15 | Keep indicator tables and `unit_index.csv` under `results/metric_sets/<id>/`; group the marker and benchmark under the experiment's single `_engine/metric_sets/<id>/`, embedding `metric_environment.json` in `metrics.json`. | The unit index lets users see which runs or bundles underpin metrics, while machine provenance stays out of the result directory. | Owner-directed revision; cross-sibling binding and versioned metric readers required |

Three different hashes answer three different questions: did the source file's bytes change; did the declared configuration values change; did the scientific artifact's identity change? A comment edit changes the first. It must not, by itself, change the last. A new preparation contract or provider-code revision may legitimately change a new collection's identity; do not promise identical IDs across that migration.

### 3.1 Decision history and TODO reconciliation

The user's recollection that fewer scenario JSON files had been decided prompted a search of the TODO notes, ADRs, working notes, reviews, milestone documents, user docs and relevant Git history across local refs. **No explicit earlier approval to merge the collection sidecars was located.** This is a repository evidence limit, not a claim that the conversation never happened. D8 now makes a concrete consolidation proposal visible in the latest schema.

| Record | What it establishes | Effect on this schema |
|---|---|---|
| [Post-R12 migration](../milestones/post-r12/migration_scenario-tree.md), events 1–4; closed t2609152040/t2609152107 | The existing `scenarios/requests` and `scenarios/collections` paths, request filename/schema rename, and 12-character path segments with full digests retained | Reflected in the existing tree. The new user-facing layout supersedes the path grouping, not the distinct identities or prefix rule. |
| [t2609152104](../tasks/t2609152104-separate-engine-bookkeeping-from-user-facing-artifacts-in-the-project-tree.md) versus migration event 6 | The live board says backlog and the note says changes 1/3 remain open; the migration records experiment/config-run engine bins and metric flattening as landed on 2026-09-16 | The checklist is stale. Treat final migration dispositions as evidence; do not reimplement its unchecked rows wholesale. |
| Same task, Change 3 | Scenario requests retained a directory because they held request, receipts and generation artifacts; metric requests were flattened because each identity had one file | Keep request directories for plan/receipt history, but move user-valued generation products to the selected collection. Fewer visible folders is not fewer records. |
| Same task, “Deliberately not proposed” | collection.json and collection_intent.json remained unmarked in the collection root | Preserve their distinct roles; moving both to the single scenario `_engine/` is a new proposal and needs versioned readers. |
| Migration event 6, declined rows | Collection preparation files were not moved: paths participate in identity; model engine bin was reversed; per-run logs stay beside responses | Do not revive declined moves. Shared elevation is now addressed through the later ADR and a versioned contract. |
| [t2609171500](../tasks/t2609171500-move-the-experiment-s-frozen-simulation-documents-into-engine.md) | Proposed moving the simulation family together; _engine/simulation versus _engine/config remained open | D9 now consolidates the input documents and places the two simulation records directly under _engine/; acceptance and reader migration remain explicit. |
| [t2609191457](../tasks/t2609191457-make-wf3-planning-static-before-snakemake.md) | Active static-planning work; one authoritative immutable preflight plan | No approved JSON-file count. Avoid a second authoritative planning path. |
| [ADR 0011](../decisions/0011-preserve-config-sources-with-run-records.md) | Exact source archive and common invocation-history proposals; user-agreed shared elevation ownership | Integrated in §§4–7. Common invocation format may produce more files through child records even as it removes duplicate histories. |

The historical scenario naming migration approved a hard break and regeneration for its then-small known set of output trees. That dated ruling does not authorize deleting or rewriting today's sealed collections. The board itself has not been edited by this document; its outstanding dispositions need reconciliation before using it as an implementation checklist.

The closed scenario task was recovered with git show abe49967^:dev/tasks/t2609152040-regroup-the-scenario-trees-under-scenarios-and-rename-scenario-plans-to-requests.md. It explicitly rejected nesting collections under requests/experiments and merging request/product identities. The new layout keeps those ownership arguments but revisits their user-facing placement.

### 3.2 One user-facing collection and one scenario engine bin

The recovered note established why a request cannot *own* a collection. Its existing two-tree placement is not a requirement to show those trees to users. The proposed layout makes `scenarios/<collection-id>/` the scientific object and keeps both identity classes as separate records under one `scenarios/_engine/`:

| Identity | Answers | Lifetime and location |
|---|---|---|
| `generation_request_id` | What was asked for from configuration, resolved inputs and provider settings? | Request-owned discovery, immutable plan and receipts under `scenarios/_engine/requests/<request-id>/`. |
| `collection_id` | What scientifically meaningful scenario collection is intended? | Immutable scientific data under `scenarios/<collection-id>/`, with its identity record under `scenarios/_engine/collections/<collection-id>/`. |
| `collection_revision` | Which produced bytes make up the published collection? | Final inventory inside the engine-side `collection.json`, known only after generation. |

The identities are not one-to-one. Two requests may differ in non-semantic details such as an absolute catalog path yet resolve to the same collection identity. Nesting the collection beneath either request would duplicate one immutable product or make another request reach sideways into the first request's directory. Putting request JSONs and scientific products together in each collection would repeat mutable request state when that collection is reused. Nesting scenarios under an experiment remains invalid because WF3 is model-independent and one collection can support multiple WF4 experiments.

The original note also relied on an ordering constraint: the request identity was available when the old checkpoint-shaped DAG was constructed, while the collection identity required staged source inventory and preparation context. Static WF3 preflight changes when the collection identity becomes available: the launcher can prepare sources and freeze an authoritative plan before constructing the generation DAG. That removes the checkpoint constraint, but it does **not** collapse the three identities, their many-to-one mapping or their different publication rules.

The placement changes are bounded:

- keep one user-facing `scenarios/<collection-id>/` for retained products and one `scenarios/_engine/` with separate request and collection records;
- keep `config/run_record.yml` and exact `config/sources/` as the collection's user-level configuration account, while `weathergenr/weather_generation_input.yml`, `weathergenr/output/` date-selection products and `weathergenr/evaluation/plots/` diagnostics form a provider-specific integration subtree rather than request bookkeeping;
- keep the published scenario time series under `series/` at the collection root, outside the provider subtree, so a WF4 consumer can find them without treating them as already prepared forcings;
- consolidate collection provenance sidecars inside the engine-side `collection_intent.json` as proposed by D8, while retaining `collection.json` as the final readiness marker; and
- let request-owned plans and receipts be cleaned up independently without implying that the collection data or its engine records may be deleted.

The engine-side ready marker must bind and validate the matching user-facing data root; the mere existence of `scenarios/<collection-id>/` is not readiness. A project copy retains both siblings, while a standalone collection export needs both the data directory and its engine-side records. Discovery must ignore reserved `_engine/` and validate the full identity behind each 12-character collection segment. Provider name and revision already contribute to `collection_id`; putting `<provider>/` before that ID would make collection lookup depend on a second path key. A different provider can own a different subtree inside its collection, while the collection-level scenario-product contract remains independent. This placement does not approve the draft `scenario-request/2` or `generation-plan/1` fields in §6.

## 4. Generated YAML: one run record and exact sources

### 4.1 Current versus proposed fields

| Current file / field | Meaning today | Proposed treatment |
|---|---|---|
| WF0–WF2 composed_config.yml | Bare composed project/workflow mapping | Move that mapping into run_record.yml as loaded_config. |
| WF0–WF2 run_record.yml | schema_version, workflow, toolbox, environment, source_config, projection, effective_config, advanced_settings, effective_config_sha256, configuration_inputs_sha256, referenced_inputs | Version the new schema; retain provenance and digest meanings. effective_config currently contains the declared projection, not a full parameter-consumption trace. |
| WF3/WF4 composed_config.yml | schema_version: 1, workflow, source_config, workflow_config (possibly null), effective_config (whole composed mapping) | Replace for new artifacts with the same run-record vocabulary as WF0–WF2. Do not confuse this effective_config with the projected field above. |
| referenced_inputs[].archived_path | Some custom files copied by role; workflow YAMLs usually not copied | Archive original filenames, add an explicit resolution anchor, retain role/checksum/recovery information. |
| Source YAML comments and formatting | Lost in generated YAML | Retain through byte copies in sources/, never YAML load/dump. |

### 4.2 Candidate run_record.yml

The following is a schema sketch. Tokens such as <full composed mapping> deliberately stand for values, not literal production strings. Proposed schema labels must be agreed before implementation.

~~~yaml
schema_version: run-record/2
workflow: generate_scenarios
invocation_id: <creator invocation UUID>
owner:
  kind: scenario_collection             # workflow | scenario_collection | simulation
  id: <full collection identity>        # workflow name for WF0-WF2
loaded_config: <full composed mapping, including applicable CLI overrides>
advanced_settings: <advanced settings mapping>
configuration_projection:
  paths: <current declared projection paths>
  effective_config_sha256: <digest under recorded existing algorithm>
  configuration_inputs_sha256: <digest under recorded existing algorithm>
  digest_schema_version: <existing provenance schema version>
toolbox: <existing code identity including dirty/unknown status>
environment: <lock hashes and available runtime identity>
invocation:
  entry_point: <actual launcher or Snakefile>
  command: [<executable>, <argument>, <argument>]
  targets: [all]
  working_directory: <original absolute run directory>
  overrides: <actual supplied overrides>
source_config: <source_files entry identifier for the project YAML>
workflow_config: <source_files entry identifier or null>
source_files:
  - id: project
    role: project_config
    original_path: <original absolute path>
    archived_path: sources/project_config_rapid.yml
    path_base: record_directory
    sha256: <source byte checksum>
    size_bytes: <integer>
    recoverable: <boolean>
    git_blob: <blob ID or null>
  - id: workflow
    role: workflow_config_generate_scenarios
    original_path: <original absolute path>
    archived_path: sources/project_config_rapid_generate_scenarios.yml
    path_base: record_directory
    sha256: <source byte checksum>
    size_bytes: <integer>
    recoverable: <boolean>
    git_blob: <blob ID or null>
referenced_inputs: <catalog/template/basin dependency entries with role and hashes>
generated_inputs:
  - role: weather_generation_input
    path_base: project_root
    path: scenarios/<collection-id>/weathergenr/weather_generation_input.yml
    sha256: <exact generated YAML byte checksum>
rerun:
  project_source: project
  workflow: generate_scenarios
  path_policy: <agreed archive resolution policy>
  adjustments: []                       # explicit rerun changes, never edits to copies
~~~

The `generated_inputs` entry binds the exact execution YAML separately from byte-preserved `source_files` and the loaded-config account. `weather_generation_input.yml` is assembled from user settings, defaults and derived values; its present-day `weathergen_config.yml` predecessor includes an absolute output directory. The `weathergenr/` subtree denotes the provider integration, not exclusive upstream ownership: the CST perturbation script also reads flags from this YAML. Archiving those bytes proves what ran but does not make that path portable. Specify path relocation/reconstruction for a rerun without editing the sealed original. This naming convention is scoped to WF3; Wflow settings YAMLs and established model filenames are not being renamed.

Do not hash this path-bearing YAML wholesale into `collection_id`: its output directory contains the collection path, so that would create a self-reference and make relocation alter scientific identity. Preserve the existing semantic projection of generator settings for identity, then checksum the exact emitted YAML as execution evidence in the run record.

Store the full loaded mapping once. A projection identifies which parts feed a configuration digest; it does not require another full copy of the values and does not claim every field was used by a rule. Preserve the existing digest computation until a separately reviewed change replaces it. Changing a record's container schema must not silently redefine its digest.

A record captures the settings loaded for this execution, even if the workflow later fails. Success belongs to the invocation record and, where applicable, the sealed scientific manifest. Capture source bytes at load time so an edit during execution cannot make the archive describe different inputs.

WF0–WF2 need a publication mechanism that makes the record and its sources one matching generation. Writing each file atomically is insufficient: a crash can still leave a new record beside old sources. The exact replace/recovery protocol is an open design item. WF3/WF4 create their archive before sealing and preserve it on reuse. A later reuse invocation points to the original archive and records its own supplied configuration hashes in its invocation record; it must not claim to be the original creator.

Rerunning still requires the recorded code, environment, working-directory context and external datasets. Sibling and nested source layouts can preserve relative references. Absolute config_path values, paths spanning drives and basename collisions need an explicit mapping/resolver; an exact copy alone is not a portable rerun. Do not load unrelated workflow YAMLs just to make a source archive look complete.

## 5. JSON execution history: one invocation record

### 5.1 Existing formats

| Existing record | Observed schema / fields | Limitation addressed |
|---|---|---|
| journal.jsonl | started/failed/success outcome events carrying invocation_id, ts, workflow and config/code digests | Hook-based work history; not complete launch coverage. |
| Wrapper <timestamp-and-id>.json | schema_version: 1; argv, cores, dry_run, effective_config, source_config, environment_files, git, runtime, extra_args, snakemake_config_overrides, workflows, status, exit_code, timestamps, no_op | Workflow results embedded in a different parent format. |
| simulation-<id>.json | simulation-invocation/1; config_path, operation, targets, status, exit_code, timestamps | Different format and provenance detail. |

### 5.2 Candidate common schema

This valid JSON example uses illustrative IDs/timestamps and placeholder hashes; it is not an executed-run report.

~~~json
{
  "schema_version": "invocation/1",
  "invocation_id": "<wf3-uuid>",
  "parent_invocation_id": "<parent-uuid>",
  "workflow": "generate_scenarios",
  "entry_point": "<agreed generation launcher>",
  "command": ["<executable>", "<arguments>"],
  "targets": ["all"],
  "working_directory": "<original run directory>",
  "mode": "execute",
  "work_performed": "yes",
  "status": "succeeded",
  "exit_code": 0,
  "started_at_utc": "<UTC timestamp>",
  "ended_at_utc": "<UTC timestamp>",
  "configuration": {
    "source_config_sha256": "<hash of project source bytes>",
    "effective_config_sha256": "<hash of declared projection>",
    "configuration_inputs_sha256": "<hash of configured dependencies>",
    "run_record": {
      "path_base": "project_root",
      "path": "scenarios/<id>/config/run_record.yml",
      "sha256": "<record file checksum>"
    }
  },
  "plan": {
    "path_base": "project_root",
    "path": "scenarios/_engine/requests/<request-id>/<plan-sha256>.json",
    "sha256": "<plan file checksum>"
  },
  "artifacts": [
    {
      "kind": "scenario_collection",
      "id": "<full collection identity>",
      "path_base": "project_root",
      "path": "scenarios/_engine/collections/<id>/collection.json",
      "sha256": "<sealed manifest checksum>"
    }
  ],
  "children": []
}
~~~

The parent uses the same envelope with workflow: null, its ordered requested workflow sequence and child IDs. Each child owns its own file. The parent records launch failures even when no child could start; it must not invent a child outcome. Final field definitions for the parent's launch-failure entries remain open.

Separate status (running, succeeded, failed) from mode (execute, dry_run) and work_performed (yes, no, unknown). A zero exit code does not establish that calculations ran. Missing completion after termination means unknown outcome; do not retrospectively label it failed without evidence. Optional run_record, plan and artifact references may be null or absent when failure precedes their creation; the final schema must choose one convention consistently.

Atomic start/final updates avoid partial JSON. New invocation UUIDs preserve attempts. WF0–WF2 archive paths are replaceable, so their references must include a checksum; an older invocation may retain only a checksum after its configuration archive is replaced. This proposal does not add historical config retention. Do not report a mismatching latest archive as the older invocation's input.

**Coverage recommendation:** normal user entry points should have a launcher that starts the record before configuration validation and subprocess startup. Raw Snakemake support either needs explicit reduced coverage or a required launcher migration. Hooks cannot record failures that occur before those hooks run. Launcher names and this compatibility choice remain open.

## 6. WF3 JSON plan: freeze execution decisions after source preparation

Today request.json is a replaceable scenario-request/1 document containing collection_id, generation_request_id, request, request_sha256, source_inventory, source_inventory_sha256, documents, intent, intent_sha256 and manifest_path. It embeds the resolved configuration/environment/source documents. The current initialization receipt records collection_id, intent_sha256, invocation_id and request_sha256.

Preferred working separation: `request.json` becomes a discovery pointer; `<plan-sha256>.json` sits directly in the request directory as the immutable authority consumed by the generation DAG. Use the full plan checksum in the filename. A request can retain multiple immutable plans, while `request.json` is the only replaceable JSON at that level; consumers must resolve an exact plan path rather than select one by glob. A launcher resolves and pins one plan path and checksum, so another invocation replacing the pointer cannot redirect that DAG. Initialization receipts remain under `initializations/`. Existing request readers must migrate together; retaining the filename does not imply schema compatibility.

Candidate pointer:

~~~json
{
  "schema_version": "scenario-request/2",
  "generation_request_id": "<full request identity>",
  "plan_path": "<plan-sha256>.json",
  "path_base": "request_directory",
  "plan_sha256": "<checksum of immutable plan bytes>"
}
~~~

Candidate plan field contract:

| Field | Type / contents | Purpose |
|---|---|---|
| schema_version | generation-plan/1 (proposed) | Reader dispatch. |
| generation_request_id, request, request_sha256 | Existing resolved request identity and object | Preserve current request meaning. |
| collection_id, intent, intent_sha256 | Full identity and existing intent object/checksum | One selected scientific identity. |
| documents | Existing resolved source/config/code/environment/preparation objects | Pin every dependency needed for initialization; do not require the mutable pointer to recover them. |
| source_inventory_sha256 | Existing inventory digest | Revalidate live producer inputs before writes. |
| decision | create or reuse_ready | Freeze which execution branch was selected. |
| collection_revision | Existing ready revision for reuse; null for create | A new collection's scenario-product hashes are not yet knowable. |
| rows | Ordered row objects under the existing scenario-row contract | Fix run IDs, ancestors and perturbation mapping without redesigning their science. |
| outputs | Project-relative expected collection, scenario-series and preparation paths | Construct the generation DAG statically. |
| path_base | project_root | Make the output-path anchor explicit. |
| counts | Retained row count and potential generation work only | Do not confuse these with Snakemake's actual scheduled jobs. |

Hash the canonical serialized plan bytes and put the checksum in the filename/pointer, not inside its own hashed content. Invocation UUID and timestamps belong in invocation history, not scientific identity. A receipt must bind the executing invocation to the pinned plan in addition to the existing ownership facts; its final versioned schema is still to be designed.

Recheck inputs and the selected collection state before initialization. If a competing invocation creates the collection after a create plan was frozen, refuse/replan; do not silently switch that plan to reuse. This proposal preserves refusal of interrupted partial collections. It does not establish resume, leases or managed run-control conformance.

The static plan is possible only after region/climate/lookup preparation and required ancillary bytes exist. Cold-start dry-run must state that final content planning is unavailable; it must not extract data while claiming to be read-only. Both existing checkpoints, including publication-dependent expansion, must be addressed for the generation DAG to become static. Shared generation working directories still need an isolation/refusal policy for competing plans.

### 6.1 Why the discovery pointer is still provisional

A discovery pointer plus immutable plans adds a JSON layer. The current working tree retains it because default WF4 collection discovery needs an explicit route from the request to its selected collection. Its necessity must be checked rather than assumed.

An alternative is to pass one immutable authoritative plan path directly and omit the pointer. Prefer that if normal WF4 discovery can remain explicit and reliable without another mutable index. Either implementation must pin the executing plan's bytes; two independent planners or a mutable request as execution authority are not acceptable shortcuts.

Initialization receipts retain their invocation/ownership role until a replacement supplies equivalent checks. They cannot simply be put into scientific identity, which excludes invocation UUIDs. Plan/receipt retention and cleanup remain open; fewer visible files does not authorize deletion of existing state.

## 7. Shared elevation: versioned preparation references

Current preparation_context.json uses forcing-preparation/1. Its top-level fields are ancillary, catalog, forcing_elevation, generated_forcing_reader, pet_method and schema_version. These are existing schema spellings, not a claim that the published WF3 series are already WF4 forcings; any replacement terminology needs a versioned contract rather than a cosmetic field rename. The inspected elevation item has id, role, path, sha256, size_bytes and descriptor. Its path is collection-relative. preparation_catalog.yml contains the matching HydroMT elevation entry with that same local URI and the existing data adapter.

In the new layout, the preparation context is embedded at collection_intent.json documents.preparation_context (§8), rather than written as preparation_context.json. Proposed forcing-preparation/2 changes the elevation reference anchor. Keep descriptors, units, data-adapter conversions and elevation selection semantics unchanged. Candidate item:

~~~json
{
  "id": "elevation",
  "role": "forcing_elevation",
  "path_base": "project_root",
  "path": "data/climate/ancillary/era5/<full-sha256>/era5_orography_2018.nc",
  "sha256": "<full-sha256>",
  "size_bytes": 10718,
  "descriptor": "<same descriptor object as the source bytes justify>"
}
~~~

The size is from the inspected example, not a constraint. A content-hash directory is the recommended version scheme: retain the familiar original filename and keep different bytes at different paths. The full-hash ancillary directory in the sketch is a new proposal, separate from the already-landed 12-character request/collection path convention; select its prefix/collision policy explicitly before implementation. The alternative is a human-readable source version directory, preferable when the provider exposes stable, unambiguous versions; either way checksum verification is required.

Recommend retaining preparation_catalog.yml at the user-facing collection root, with a relative URI that reaches the shared file from the catalog's location. The engine-side preparation-context reference can no longer assume this catalog is a sibling of collection_intent.json: declare its project-root or collection-data-root anchor explicitly and verify that it resolves to the same checked catalog bytes. The project-relative JSON reference and the catalog URI must resolve to the same checked elevation bytes after project relocation. Verify actual HydroMT path resolution before accepting that choice; do not add CST-specific keys to HydroMT YAML or modify upstream code. Original machine paths can remain provenance, but must not be the only way the retained dependency is resolved.

This change affects more than a path in one JSON file. The consolidated intent binds its embedded preparation section by digest; that section binds the catalog and ancillary bytes. collection.json binds the intent and the completed outputs. Source inventory and provider code also contribute to identity. Specify coordinated reader/version and canonicalization changes before writing new collections. Existing scenario-collection/1 collections retain their local sidecars and data bytes. New consolidated/shared-reference collections require an explicit versioned dispatch contract; the exact collection version label remains open in §10.

Never edit the inspected sealed collection to demonstrate the proposed tree. Missing or modified shared data must cause a clear refusal before any dependent scenario preparation. Reusing a matching version verifies its checksum instead of replacing it. Standalone collection export would need an explicit bundling operation; the normal preservation unit is the project.

## 8. Consolidated scientific manifests and engine records

### 8.1 Collection JSONs: seven become two

Current count, inspected 2026-09-20: session-1/test_case/test_local/scenarios/collections/c3f88ea5c76f has seven root JSON files. scenario_collection.py's DOCUMENT_FILES mapping independently names the five provenance sidecars. The proposed fresh collection has two scientific JSON files under its `scenarios/_engine/collections/<id>/` record directory and none at the user-facing collection root; request plans, receipts and invocation history are outside this count. Re-measure before implementation.

| Existing file | Proposed location | Meaning retained |
|---|---|---|
| collection_intent.json | _engine/collections/<id>/collection_intent.json | Frozen pre-generation identity, scenario semantics and expected rows. |
| generation_config.json | documents.generation_config inside the intent | Resolved generation settings and seed. |
| source_inventory.json | documents.source_inventory inside the intent | Original source inventory and byte identities; review roles/anchors for shared elevation. |
| provider_code_inventory.json | documents.provider_code inside the intent | Provider implementation inventory. |
| generation_environment.json | documents.environment inside the intent | Generation environment identity. |
| preparation_context.json | documents.preparation_context inside the intent | Existing reader, PET and checked preparation dependencies (§7); legacy forcing-named fields need versioned treatment. |
| collection.json | _engine/collections/<id>/collection.json | Final output inventory, revision and readiness, published last. |

Candidate intent structure, not a finalized executable schema:

~~~text
schema_version: <new collection-intent schema>
canonicalization_id: <declared canonicalization>
collection_id: <full scientific identity>
provider: <existing name and revision>
scenario_type: <existing value>
scenario_spec: <existing scenario specification>
scenario_semantics_sha256: <existing semantics digest>
run_count: <expected row count>
unit_id_capacity: <existing capacity>
unit_id_width: <existing width>
documents:
  generation_config: <complete former sidecar object>
  source_inventory: <complete former sidecar array>
  provider_code: <complete former sidecar array>
  environment: <complete former sidecar object>
  preparation_context: <complete object with shared-reference schema>
document_digests:
  generation_config: <canonical embedded document checksum>
  source_inventory: <canonical embedded document checksum>
  provider_code: <canonical embedded document checksum>
  environment: <canonical embedded document checksum>
  preparation_context: <canonical embedded document checksum>
~~~

Keep collection.json as a separate final record. It retains collection identity/revision, intent path/checksum, scenario-table reference, scenario-type artifacts, retained-series entries with hashes/descriptors and ready status. The current manifest calls those entries forcing; the new schema must version their paths and terms rather than treating the rename as identity-neutral. Its existing preparation-context file reference becomes an explicitly versioned section reference to the checked intent, or is removed as redundant if all readers obtain preparation through the intent. The working recommendation is the latter: one authoritative embedded preparation object reached through the verified intent. The new manifest location also requires an explicit project-relative reference to the sibling `scenarios/<collection-id>/` data root; never infer readiness from the data directory alone. Final strict field sets must be agreed before coding.

The five embedded sections retain the full evidence, not summaries. This reduces files, not necessarily bytes. A long environment inventory remains long inside the intent. The run_record.yml remains a readable source/config account and cannot substitute for scientific identity inputs. The retained `sim_dates.csv` and `resampled_dates.csv` need explicit byte references in the final collection inventory or a separately checked provenance record; merely moving them under the collection would not make their evidentiary role verifiable. Evaluation plots are terminal diagnostics, not inputs to collection identity.

### 8.2 Publication, identity and alternatives

An intent can be frozen before generation; the produced-byte inventory cannot. Keeping these two lifetimes separate preserves the existing claim and final-readiness distinction. Do not overwrite an intent to turn it into a success record. Missing engine-side collection.json still means the collection has not been published ready, even if its sibling data directory exists. Publish the marker last, after checking the data-root path, expected files and hashes. Validation must refuse a marker without matching data and ignore orphaned data without a marker.

This is a coordinated schema migration. Current readers open named sidecars, enforce strict fields and hash their bytes. Specify canonicalization for each embedded document and the identity projection excluding self-referential fields. Prove whether pure packaging preserves identity under those functions. Do not assume matching parsed values guarantee matching digests; shared-data and provider-code changes may legitimately create new identities. Old sidecar-based collections remain readable and untouched.

| Alternative | Benefit | Tradeoff / when preferable |
|---|---|---|
| Keep seven JSONs | Smallest reader migration, components can be inspected independently | File clutter remains; preferable if compatibility risk outweighs ergonomics. |
| Two JSONs — working recommendation | Fewer files with clear intent versus completed-output boundary | Larger intent; coordinated initialization, publication and downstream-reader changes. |
| One collection JSON | Smallest visible count | Requires redesigning the pre-publication claim/state contract, or retaining another hidden intent anyway. Not selected here. |
| Keep the two JSONs beside the user-facing products | Easier standalone directory inspection | Exposes machine readiness contracts at the collection root; preferable if detached collection export is the primary use case. The working layout instead uses one scenario-level _engine/. |

Keep preparation_catalog.yml as a separate HydroMT-native input. JSON consolidation does not authorize CST-specific catalog keys or changes in upstream HydroMT code.

### 8.3 Simulation documents: two engine-side records

Integrate and extend t2609171500 by placing two scientific records directly under `experiments/<name>/_engine/`, separate from the readable `config/run_record.yml` and `config/sources/` archive. With only two simulation records, an additional `simulation/` level does not distinguish a useful ownership boundary; `_engine/` already groups this experiment's machine contracts. `simulation_intent.json` freezes the full contents of today's `model_reference.yml`, `simulator_settings.json`, `simulation_environment.json`, `simulator_adapter_code_inventory.json` and `response_request.json` as named sections, along with collection selection, simulator identity and `simulation_id`. The proposal reduces six simulation-family files to two; it does not discard the per-model-input hashes or any requested-response details. Wflow's own settings files and names are outside this consolidation.

Compute and retain separate canonical section digests for settings, adapter code, environment and response request so the accepted scientific identity projection remains auditable. Keep the model digest and its per-input evidence together in the embedded model-reference section. The complete intent is immutable once frozen; a same-identity reuse checks its bytes and referenced source identities rather than replacing it. A new versioned schema must define section canonicalization and distinguish content digests from the old sidecar file checksums before claiming `simulation_id` continuity. Old `model.reference_path` and sibling-file references cannot simply be rebased: new readers use checked intent sections, while legacy readers continue to validate the retained `config/` files under their original schema.

Publish `simulation.json` only after the matching `_engine/response_inventory.json` and retained native responses have been verified. During execution, the response-inventory producer reads the frozen intent without requiring that final marker. The marker binds the exact intent path/checksum, `simulation_id`, response-inventory path/checksum and completed response claim; it cannot substitute for checking the inventory and files. An absent final marker means the simulation is not ready for metrics-only reuse, even if intent or native output exists. Keep `response_inventory.json` at the immediate `_engine/` level: its relative references to native artifacts already have the required depth, and moving it deeper can re-key metric identity. Invocations record failed or interrupted attempts separately; do not turn a partial intent into a success marker.

Current metric planning, response-inventory production and metric-set validation read `config/response_request.json` directly. They must read and verify the embedded section instead, and stored metric-set references must become versioned section references rather than dangling file paths. Inventory every other stored and constructed path, update declared rule targets, and validate old and new experiments separately. The older TODO's baseline target/cost assumptions need remeasurement before implementation.

### 8.4 Other retained contracts

| File or family | What it proves / controls | Treatment |
|---|---|---|
| _engine/simulation_intent.json | Frozen collection selection, model reference, settings, response request, environment, simulator/code and simulation identity | Embed the full five input-document payloads and preserve separately checked scientific section digests; immutable before native simulation. |
| _engine/simulation.json | Final completed-simulation marker, not the current mutable simulation/1 record | Publish last and bind the checked intent and response inventory; a missing marker is not readiness. |
| _engine/response_inventory.json | response-inventory/1: native artifact checksums and series/time/unit/selector metadata | Keep path depth and scientific verification. This is not replaceable by invocation status. |
| _engine/metric_requests/*.json; _engine/metric_sets/*/metrics.json | Metric request and immutable metric-set identity/provenance | Retain separate request and published-set identities. Metrics-only execution must not overwrite simulation creator provenance; exact source-archive ownership for later metric requests remains open. |
| Metric environment; return_level_benchmark.json; unit_index.csv; indicator tables | Frozen metric environment, exact benchmark evidence, run/bundle mapping and results | Embed the environment in the set's marker; keep the benchmark in the matching experiment-engine set directory, with unit index and indicator tables under `results/metric_sets/<id>/`. |
| spatial_catalog.yml; spatial_report.yml; projection summary provenance.json | Spatial and projection provenance | Retain; the historical engine-bin screen declined those generic relocations. |
| hydromt_build_config.yml; hydromt_update_waterbodies.yml; hydromt_data.yml; wflow_sbm.toml; retained per-run TOML | Engine configuration and derived execution context | Keep model files beside the model and per-run TOML under experiment `hydrology/wflow/run_settings/`. Use upstream formats verbatim. Temporary per-run HydroMT catalogs remain disposable under their existing rules. |

The local scientific JSON key inventories and current writers, rather than the old rule index, ground this comparison. Not every generated YAML or JSON needs consolidation; files used as upstream engine inputs have a different role from provenance sidecars.

### 8.5 Generated Wflow run settings and temporal evidence

The current `experiments/<name>/hydrology/wflow/config/` holds `run_<id>.toml`, `run_<id>.yml` and `run_<id>.temporal.json` for each run. These have different roles. Wflow executes the TOML and the response reader verifies it against retained native output, so keep each `run_<id>.toml` unchanged by name and content under `hydrology/wflow/run_settings/`. The `run_<id>.yml` is a per-run HydroMT data catalog already declared `temp()`; it may be written in that directory while preparing a run but is not a required retained product. Do not change its HydroMT schema or filename. The temporal JSON is CST validation evidence, not a Wflow setting. In the proposed tree, the annotated temporary entries show files that exist during execution, not a promise that they remain in a clean published output. The Wflow-ready `forcing/inmaps_run_<id>.nc` is likewise already declared temporary; the native `output/run_<id>.csv` and Wflow's per-run log are retained.

Today each TOML's `[logging] path_log` directs Wflow to `../output/run_<id>.log` relative to that TOML's directory. Point new TOMLs to `../output/_log/run_<id>.log` and create `_log/` before Wflow starts; do not move logs after execution or change their basenames. The settings-directory rename preserves the relative depth, but generated TOML output, forcing and model paths still need explicit validation. Preserve the existing per-member log attribution checks and legacy TOML paths for retained old experiments. The Wflow-native logs are distinct from the workflow's gathered logs under the project-level `logs/` directory.

Current publication requires every run's temporal evidence to match a single common value and embeds that value as `response_inventory.json`'s `temporal_preparation`. The checked baseline run 01 and run 14 files, and rapid run 01 and run 10 files, were byte-identical; this sampling supports the redundancy observation but is not a proof for all future inputs. The proposed new response-inventory schema retains the common temporal object once, while each run's actual prepared clock and transformation chain is still checked against its TOML and the common object before publication. Per-run temporal files can be temporary handoff artifacts and removed after successful publication; an implementation may instead pass equivalent checked evidence between preparation and publication without materializing them. Do not merely copy run 01's record to the others or omit per-run checks.

The current native selectors store each TOML and temporal file path and checksum. A versioned inventory and metric-reader change must replace the temporal file references with the checked common section, update TOML paths for `run_settings/`, and preserve legacy resolution for sealed experiments. Keep failed or interrupted runs' temporary evidence recoverable until their publication/refusal outcome is known; normal Snakemake cleanup must not erase evidence needed to diagnose a partial run. This proposal changes retained file count, not Wflow's execution semantics or the native CSV response contract.

### 8.6 Metric-set results and machine contracts

Keep `results/metric_sets/<id>/` because one completed simulation already supports subsequent metrics-only requests, and changed metric definitions or environments produce new immutable sets without overwriting previous tables. Put the `<token>_indicators.csv` tables and `unit_index.csv` there: the latter exposes which run IDs belong to each unit or bundle and helps users interpret the metric tables. Group `metrics.json` and `return_level_benchmark.json` under the experiment's single `_engine/metric_sets/<id>/`. The matching full `metric_set_id` binds these two sibling directories; neither directory alone is a complete export. The benchmark is exact retained validation evidence, not a derived summary: keep its original bytes separate so old sets remain verifiable without the installed benchmark asset.

Embed the full `metric_environment.json` payload as a named section of the new versioned `_engine/metric_sets/<id>/metrics.json`, retaining its independently checked canonical digest in the `metric_set_id` projection. The marker remains the last published file and must verify the benchmark within its engine set directory and the unit index and every result table through explicit experiment-relative references confined to the matching result directory. Neither an orphaned result directory nor an engine record without its checked tables is a ready set. A project copy or standalone set export must carry both directories; discovery starts from checked markers, not a bare `results/` listing. Current readers require result-root `metrics.json` and standalone environment and benchmark references; dispatch by schema so old sealed sets remain byte-for-byte unchanged. Update metric target construction, strict path checks, metric-set discovery and external consumers together. Embedding the environment removes one file, not its scientific evidence.

## 9. Migration and alternatives

Write the new layouts for new executions/artifacts. Preserve old journals and invocation JSONs as legacy history; dispatch readers by schema and do not reinterpret old no_op values under the new semantics. Existing sealed collections and experiments remain byte-for-byte unchanged. Update snapshot readers, collection sidecar readers, collection discovery and path-containment checks, simulation-location readers, declared Snakemake targets, tree inventories, fixtures and user documentation together. Baseline readers currently consume composed snapshots, so simply deleting the writer is not a complete migration. Do not rename existing Wflow YAML/TOML files as part of the scenario layout or generated-input naming change.

For WF0–WF2, replacement of the latest archive must be coordinated with its matching record and any running reader. For WF3/WF4 reuse, no new source archive is inserted into an already sealed artifact. Invocation history records the new attempt and points to the original artifact. Whether metrics-only and failed-before-artifact invocations need separately retained source archives is unresolved; do not imply they already have full rerun coverage.

| Alternative | Benefit | Cost / when preferable |
|---|---|---|
| Retain composed_config.yml and add source copies | Lowest short-term reader migration cost | Continues two generated accounts. Useful as a temporary compatibility phase only if readers require it. |
| One project-wide config archive | Less repeated source storage | Later workflows can overwrite earlier provenance. Suitable only for a separately frozen coordinated run, not independent workflow execution. |
| Keep one append-only event journal | Rich transition history | Requires event reconstruction and coordination. Prefer it if intermediate transitions, beyond start/final state, are required. |
| Keep dynamic WF3 checkpoints | Preserves current cold-start invocation behavior | No fully resolved upfront generation DAG. Prefer if preserving that invocation contract is more valuable than static planning. |
| Retain every `run_<id>.temporal.json` | Existing strict selectors and partial-run diagnostics work unchanged | Duplicates the same checked evidence for every run. Prefer as a compatibility phase if inventory/reader versioning cannot land together. |
| Keep metric-set JSONs beside indicator CSVs | No metric-set path migration or cross-sibling binding | Leaves machine provenance and the large benchmark report in the user-facing result directory; prefer if established external readers cannot migrate together. |
| Put a nested `_engine/` in each result set | Keeps all set files under one directory | Repeats machine bins in every set and conflicts with the preferred single experiment-level `_engine/`; preferable for independently moved set directories. |
| Embed the benchmark report in `metrics.json` | One JSON file per metric set | Inflates the ready marker with a large independently retained report and entangles its exact-byte validation with marker publication; prefer only if a single-file export requirement outweighs that separation. |
| Embed all simulation inputs in one mutable `simulation.json` | One fewer file than the proposed intent/marker pair | Rewrites a document that also carries frozen identity inputs when completion is recorded; prefer only if strict immutability of the input record is unnecessary. |
| Move all six existing simulation-family files without consolidation | Smallest payload-schema change | Retains five separate input sidecars and today's mixed input/completion record; prefer as a compatibility phase if section-reader migration cannot be delivered together. |
| Keep user-visible `scenarios/requests/` and `scenarios/collections/` | Smallest path migration; request-local working outputs remain co-located | Makes users navigate machine identities to find generation inputs, date products and diagnostics. Prefer if implementation cost outweighs the navigation improvement. |
| Put provider before collection ID: `scenarios/weathergenr/<id>/` | Browsing all collections from one provider is easy | Makes the primary collection path and lookup depend on provider; prefer only if provider-grouped navigation is the dominant user task. |
| Keep ancillary data collection-local | Each collection carries its source elevation | Duplicates shared source data and conflicts with the agreed project-owned direction; useful for an explicit standalone export. |

## 10. Decisions still needed before a task brief

| Open item | Recommended starting point | Why it blocks implementation details |
|---|---|---|
| Exact schema versions and digest projections | Version the new record independently; preserve digest meanings | Avoid silently changing identity while renaming metadata fields. |
| Collection JSON consolidation | Two JSONs in the scenario engine's collection-record directory; five complete provenance sections embedded in the intent | Requires accepted strict field sets, section canonicalization and old-sidecar reader dispatch. |
| Scenario record/data split | One `scenarios/_engine/` with separate request and collection records; one `scenarios/<id>/` scientific root | Stored relative paths, containment, discovery, publication and standalone export must recognize both siblings. |
| Provider-specific integration | `scenarios/<id>/weathergenr/` holds execution YAML, retained date CSVs and diagnostics; `series/` holds the published climate time series | Define provider-subtree readers and the versioned path/term migration from `forcing/`; keep currently temporary realization netCDFs temporary unless explicitly changed. |
| Simulation intent/marker contract | Two records directly under _engine/: immutable embedded-input intent and final completion marker | Set versioned strict fields, section digests and publication order; migrate all old file readers, stored references and declared targets together. |
| Wflow run settings and temporal evidence | `hydrology/wflow/run_settings/` for retained TOMLs; one common temporal object in the response inventory | Preserve per-run verification, update selector paths and hashes, and dispatch legacy inventories by schema. |
| Wflow native-log placement | `hydrology/wflow/output/_log/run_<id>.log` | Set each TOML's `logging.path_log`, create `_log/` before execution, and preserve one log per run without changing old experiments. |
| Metric-set contract placement | Indicator CSVs and `unit_index.csv` under `results/metric_sets/<id>/`; marker and exact benchmark under the single experiment `_engine/metric_sets/<id>/`; environment embedded in the marker | Bind both siblings by full identity and checked paths, version marker fields, retain section digest and benchmark bytes, and preserve root-marker legacy readers. |
| Record-plus-sources publication | Publish one coherent archive generation with explicit crash recovery | Independent atomic file writes can mix two runs. |
| Archive path mapping | Preserve relative structure; explicitly map absolute/multi-drive sources | Exact copies cannot silently redirect absolute YAML references. |
| Launcher coverage | Record all normal launches; document or retire raw-hook-only entry points | Parse failures, no-ops and dry-runs otherwise remain uneven. |
| WF3 “upfront” boundary | Source preparation, then immutable plan, then static DAG | A cold configuration cannot predict content hashes. |
| Plan concurrency and workspace ownership | Pin plan bytes; refuse conflicting create state; isolate or refuse shared working directories | Immutable plans alone do not make concurrent outputs safe. |
| Shared-data reference and catalog resolution | Project-relative JSON plus verified catalog-relative URI | Must survive project relocation and existing strict reader assumptions. |
| Collection version / identity migration | Explicit old/new reader dispatch; never rewrite old IDs | Preparation and provider-code changes can legitimately alter new identities. |
| Metrics-only / early-failure archive ownership | Preserve creator record; decide whether invocation-local sources are needed | A simulation's original archive cannot describe every later metric request. |

These are design choices, not permission to implement them. The source-archive and history changes can be scoped separately from WF3 static scheduling, provided their invocation/reference interfaces agree.

## 11. Outline for the eventual task brief

Objective: emit the agreed output tree and versioned records, preserve old-output readability and scientific behavior, and make each recorded execution traceable to its actual inputs.

Potential implementation units, with explicit dependencies:

1. **Record/archive contract and common writer.** Start with copy_config_files.py, shared/workflow_config_snapshot.py, shared/provenance.py and configuration composition. Establish byte capture, reference mapping and publication behavior before switching any writer.
2. **WF0–WF2 and artifact-local archive adoption.** Wire the five workflow/launcher paths, with compatible readers and tests. Update declared outputs, baseline readers and output-tree inventory in the same runnable change. Depends on unit 1.
3. **Unified invocation history.** Update scripts/run_workflows.py, scripts/simulate_system.py and existing workflow journal hooks; add the agreed launcher coverage and parent/child ownership. Depends on the record-reference interface from unit 1, not on completed scientific runs.
4. **Consolidated collection and shared ancillary contract.** Update experiment/scenario_collection.py, collection_resolution.py, scenario_provider.py, content_identity.py and climate_analysis/prepare_climate_data_catalog.py together with their consumers. Replace five sidecar files with embedded intent sections and establish old/new reader compatibility before publishing a new collection. Depends on §§7–8, not necessarily the static planner.
5. **Static WF3 planning.** Update generate_scenarios.smk, experiment/generation_plan.py, collection_resolution.py, scenario_provider.py and scenario_collection.py plus the agreed entry point. Depends on frozen plan/invocation interfaces and the preparation contract it will validate.
6. **Simulation and metric-set contract consolidation.** Update experiment/simulation_record.py, response_inventory.py, metric_plan.py, downscale_climate_forcing.py, scenario_collection.py collection-reference discovery, shared/cross_workflow_leaves.py, workflow leaves, retained readers and tree tests. Embed the five simulation input payloads and the metric environment in their respective records, publish final markers after verification, retain common temporal evidence once and keep the human-facing archive in config/. Re-measure the old task’s baseline assumptions before deciding validation cost. Depends on the agreed §§8.3, 8.5 and 8.6 schema/path/compatibility contracts.
7. **Complete-run evidence.** Use an isolated rapid project after implementation; retain tree/schema comparison and scientific acceptance evidence. Depends on all units selected for the agreed scope.

These are candidate work packages, not a blanket authorization or a claim that each is one small patch. Before dispatch, remeasure readers/writers and produce bounded briefs with confirmed files and commands. Do not combine unrelated numerical fixes, change upstream HydroMT/Wflow internals, add resume semantics, prune old output trees or regenerate the comparison baseline as incidental cleanup.

Acceptance evidence to carry into those briefs:

| Claim | Observation that would disprove it / required check |
|---|---|
| Exact source recovery | Byte mismatch (including CRLF/comments), lost original basename, or missing loaded workflow/custom dependency. Test source copies and rerun with originals unavailable. |
| One matching archive | Interrupted or concurrent publication exposes mixed record/source checksums. Exercise failure points, not just a successful write. |
| Clear invocation history | Missing child linkage, a dry-run reported as work, or hard termination reported as success. Exercise direct, parent/child, startup failure, no-op and crash cases. |
| Stable scientific meaning | Comment-only edits alter scientific identity, row ordering/seeds change, or retained scenario series differ beyond an agreed scientific comparison. Separate identity migration from numerical parity. |
| Reduced collection JSON count | A fresh collection still emits the five sidecars, embedded evidence is missing, tampering with an embedded section passes validation, or an old collection stops reading. Assert exactly two JSONs in its scenario engine record directory and exercise all section readers. |
| Scenario root/engine binding | A bare data directory is listed as ready, an orphaned marker passes, two requests duplicate one collection, or detached export omits its records. Test each and verify full-ID/short-segment correspondence. |
| Generated-input recovery | The weather-generation YAML is absent, differs from the run record's checksum, or a moved project silently reuses its old absolute output path. Validate exact bytes and relocation behavior. |
| Provider intermediates and diagnostics | Date-selection CSV bytes are unaccounted for, conditional figures disappear during relocation, or temporary realization netCDFs become silently durable. Check inventory/reference coverage and terminal-render handling. |
| WF3/WF4 product boundary | A WF3 `series/` artifact is called a ready model forcing, or a WF4 transformation silently changes the source series. Check collection byte identity and explicit downstream preparation/reference separately. |
| Simulation intent and readiness | A response request or model-reference section loses data, section tampering passes, an intent-only experiment is treated as ready, the marker precedes its verified inventory, an old simulation cannot reopen, or response-inventory depth changes. Assert two simulation-family files for new runs; validate old/new readers and metrics-only reads. |
| Wflow run-setting retention | A TOML is missing or changed, a run with different clock/conversion passes common-temporal validation, a new selector requires a removed temporal file, or an old inventory cannot reopen. Check all run TOMLs and temporal evidence before publication, then metrics-only reading after temporary files are gone. |
| Wflow native-log attribution | A run writes beside the CSV, two concurrent runs share one log, or `_log/` is absent when Wflow opens its path. Check every generated `logging.path_log` and exercise a bounded concurrent run. |
| Metric-set grouping | A table lacks a checked reference, the two short-ID directories bind different full IDs, environment-section tampering passes, benchmark bytes are missing or differ, an orphan is listed as ready, or a legacy root-marker set stops reading. Validate new and old sets, metrics-only reuse, paired export and external discovery. |
| Shared ancillary safety | Two collections copy the same version unnecessarily, changed bytes pass, old collections stop reading, or relocation breaks catalog resolution. Test all four. |
| Static generation scheduling | Either checkpoint still expands the generation DAG, live pointer replacement redirects execution, or cold dry-run silently produces scientific outputs. Inspect DAGs and filesystem differences. |
| Backward compatibility | Existing sealed output checksums change or legacy readers cannot load their schema. Snapshot retained files before/after reuse and refusal. |
| Complete-run tree | A fresh isolated WF0–WF4 run lacks a required record, reference cannot resolve, or temporary provider files are wrongly retained. Capture the actual tree and representative schemas after successful execution. |

During implementation, run focused tests for the changed surfaces. Apply tests/test_cli.py when rules/signatures/declared inputs change and the repository's lint/format checks for Python. At approved batch landing use the documented combined gates; shared/signature changes require the stated full-suite rung. Run numerical baseline comparisons only when their scope warrants them, using the baseline configuration and preserving its WF1 temporary discharge target with --notemp. Do not repeatedly run the full suite for each incremental edit. Exact new manifest/archive test commands belong in the finalized briefs once test files exist.

## 12. Sources and verification of this draft

Read-only evidence: current metadata files under session-1's test_case/test_local and test_case/test_rapid; current snapshot writers; generation_plan.py; scripts/run_workflows.py and scripts/simulate_system.py; ADR 0011, the WF3 intake, TODO/task notes, post-R12 migration event 6 and recovered closed scenario-tree task history. The repository search does not include external conversation transcripts, remote-only branches or other sessions’ uncommitted notes. Inspected output IDs identify examples, not fresh validation results.

Implementation references:

- [WF0–WF2 snapshot writer](../../blueearth_cst/model/copy_config_files.py)
- [Artifact-local snapshots](../../blueearth_cst/shared/workflow_config_snapshot.py)
- [Configuration provenance](../../blueearth_cst/shared/provenance.py)
- [Generation planning](../../blueearth_cst/experiment/generation_plan.py)
- [Collections and publication](../../blueearth_cst/experiment/scenario_collection.py)
- [Preparation catalogs](../../blueearth_cst/climate_analysis/prepare_climate_data_catalog.py)
- [All-workflow launcher](../../scripts/run_workflows.py)
- [Simulation launcher](../../scripts/simulate_system.py)

Draft validation: check Markdown links, parse JSON examples, check the diff for whitespace errors, and self-review current/proposed distinctions and cross-schema references. No workflow execution, test suite, full tree-conformance check or numerical validation is claimed by this document.

## Revision history

- 2026-09-20 — Initial complete-run tree comparison and candidate schemas. Consolidated the ADR's proposed archives/history and agreed shared-elevation ownership, related them to static WF3 planning, and listed unresolved decisions and future acceptance evidence.

- 2026-09-20 (scenario follow-up) — Audited scenario decisions and the TODO history; clarified that retaining scientific information does not settle the physical JSON layout.
- 2026-09-20 (single-schema consolidation) — Integrated the audit here at the owner’s request. Updated the preferred tree to two collection JSONs with embedded provenance and an experiment _engine/simulation directory; retained approval status, alternatives and migration constraints. Removed the uncommitted separate draft so this is the single current schema proposal.
- 2026-09-20 (`scenarios/` ownership follow-up) — Recovered and integrated the original request/collection merge analysis. Kept the two branches as siblings, distinguished request, collection and revision identities, and recorded that static preflight removes the old checkpoint timing constraint without removing many-to-one reuse or separate mutability.
- 2026-09-21 (collection-centred layout) — Revised the proposed scenario tree to a user-facing collection plus one `scenarios/_engine/` for distinct request and collection records. Grouped exact user configuration, resolved `weather_generation_input.yml`, date-selection products and weather-generator evaluation plots by role; left Wflow filenames unchanged and made cross-sibling readiness/portability checks explicit.
- 2026-09-21 (provider and scenario-product boundary) — Grouped weathergenr integration files beneath each collection rather than putting provider before collection ID. Renamed the proposed published WF3 `forcing/` branch to `series/`, reserving forcing terminology for model-specific WF4 preparation and recording the versioned legacy-field/path migration this requires.
- 2026-09-21 (flat request plans) — Placed full-hash immutable plan JSONs directly under each request directory, retaining the separate initialization receipts and exact plan pinning without a redundant `plans/` level.
- 2026-09-21 (simulation consolidation) — Replaced the proposed six-file simulation family with an immutable embedded-input `simulation_intent.json` and a separately published `simulation.json` readiness marker, both flat under the experiment's `_engine/`. Retained response inventory and metric requests independently, with explicit section-digest, legacy-reader and metrics-only migration requirements.
- 2026-09-21 (Wflow run settings) — Renamed the proposed experiment Wflow `config/` folder to `run_settings/`, kept per-run TOML names and Wflow settings unchanged, and proposed retaining common temporal evidence once in the response inventory after checking every run. Per-run HydroMT catalogs and temporal handoff records remain temporary, with versioned selector and legacy-reader migration required.
- 2026-09-21 (Wflow subtree overview) — Expanded the proposed experiment Wflow tree to show settings, temporary HydroMT/temporal preparation files, temporary prepared forcing, native response CSVs and run logs together; clarified that temporary entries are execution-time files rather than retained publication requirements.
- 2026-09-21 (Wflow native logs) — Kept each Wflow log but grouped it under `hydrology/wflow/output/_log/`, with direct per-run `logging.path_log` targeting, precreated directory and preserved concurrent-run attribution.
- 2026-09-21 (metric-set machine contracts) — Kept indicator CSVs at each immutable set root, moved its marker, exact benchmark report and unit index to a local `_engine/`, and embedded the full metric environment in the marker with its independent identity digest. Required versioned paths/readers and preserved legacy sets.
- 2026-09-21 (single experiment engine) — Moved the proposed metric-set machine contracts to `experiments/<name>/_engine/metric_sets/<id>/`, eliminating nested result-local `_engine/` folders. Added full-ID cross-sibling binding, checked result references and paired-export requirements.
- 2026-09-21 (metric-set unit index) — Kept `unit_index.csv` with the user-facing indicator tables under `results/metric_sets/<id>/` because it explains run and bundle membership; left only the marker and exact benchmark report under the experiment's `_engine/metric_sets/<id>/`.
