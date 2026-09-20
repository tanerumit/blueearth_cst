# Complete-run output tree and record schemas — current working proposal

- Status: working proposal — not an implementation brief or an implemented schema
- Date: 2026-09-20
- Inspected code: bb200682 (documentation follow-up; runtime code unchanged)
- Location: session-1, refactor/wf3-static-planning
- Lifecycle: temporary working document; revise in place, append revision history. Promote the accepted contract to dev/reference/ before closing the work.

## 1. What this document shows

This is a proposed output-project tree after a successful WF0–WF4 run, compared with the existing layout and generated metadata. “Output tree” means the contents of project_dir, not the Git worktree holding the toolbox.

The proposal brings together exact configuration archives, execution history, shared elevation data and the prospective WF3 static plan. It does not change the climate experiment, Wflow physics or metric definitions. WF2 remains a projection plausibility overlay; it does not supply generation scenarios.

Read §2–3 for the tree and plain-language decisions; §4–8 for schema comparisons; §9–11 for migration, unresolved choices and the outline of a future task brief. The detail is retained because the next reader needs to distinguish a renamed record from a changed scientific contract.

**Evidence boundary.** No new full run was executed for this document. The proposed writers do not exist yet. Current examples were inspected in session-1's test_case/test_local and test_case/test_rapid, alongside their writers. These are accumulated output trees, not evidence of one clean run at the inspected code revision. The local collection c3f88ea5c76f has a ready marker and 14 retained forcing entries; its experiment is named experiment. This inspection did not revalidate the forcing bytes or numerical results. Rapid supplies examples of WF0 records and wrapper invocation history. Its older retained collections do not have the artifact-local composed snapshot now written by current code.

Decision authority remains in [ADR 0011](../decisions/0011-preserve-config-sources-with-run-records.md). The static-planning boundary remains in [the WF3 intake](t2609191457-wf3-static-planning.md). This document is the single latest working output-schema proposal: what would a user find in a completed output project, and what would each record contain? Integrate future layout and schema proposals here rather than maintaining competing trees. ADRs, task notes and migration records retain decision history; this document does not silently turn their open proposals into approvals. New field names and version labels below are draft suggestions, not approved APIs.

The latest proposed tree incorporates a **seven-to-two reduction in collection JSON files** (§8), shared elevation (§7), exact source archives (§4), common invocation history (§5), static planning (§6), and relocation of frozen simulation documents into the experiment engine directory (§8.3). The seven-to-two mapping and exact simulation destination are recommendations, not recovered prior approvals. The decision/TODO reconciliation is included in §3.1.

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
│   ├── requests/<request-id>/
│   │   ├── request.json                      [changed: discovery pointer]
│   │   ├── plans/<plan-sha256>.json           [new: immutable execution plan]
│   │   ├── initializations/<invocation-id>.json [kept role; binding changes]
│   │   └── generation/                       [kept role; isolation unresolved]
│   └── collections/<collection-id>/
│       ├── run_record.yml                    [new: replaces composed snapshot]
│       ├── sources/
│       │   ├── project_config_rapid.yml
│       │   └── project_config_rapid_generate_scenarios.yml
│       ├── collection_intent.json            [changed: embeds five JSON sidecars]
│       ├── collection.json                   [changed binding; final ready marker]
│       ├── preparation_catalog.yml           [changed URI; retain HydroMT schema]
│       ├── scenario_table.csv                [kept]
│       ├── stress_test_lookup.csv            [kept]
│       └── forcing/run_<id>.nc                [kept]
├── experiments/<name>/
│   ├── config/
│   │   ├── run_record.yml                    [new: replaces composed snapshot]
│   │   └── sources/
│   │       ├── project_config_rapid.yml
│   │       └── project_config_rapid_simulate_system.yml
│   ├── _engine/
│   │   ├── simulation/                       [changed: proposed destination]
│   │   │   ├── simulation.json
│   │   │   ├── model_reference.yml
│   │   │   ├── simulator_settings.json
│   │   │   ├── simulation_environment.json
│   │   │   ├── simulator_adapter_code_inventory.json
│   │   │   └── response_request.json
│   │   ├── response_inventory.json           [kept]
│   │   └── metric_requests/<id>.json          [kept]
│   ├── hydrology/wflow/                      [kept]
│   └── results/metric_sets/<id>/             [kept]
├── logs/                                     [kept]
└── benchmarks/                               [kept]
~~~

Each sources/ also holds required custom catalogs and engine templates, preserving their original names and relative structure. The two-file examples are not a claim that all archives contain exactly two files. Unmodified toolbox files may instead be recoverable through recorded revision/blob identity.

New collections write two root JSON documents instead of seven; the five sidecar payloads become embedded intent sections, not discarded evidence. Request plans and initialization receipts are outside that count. New experiments keep the human-facing archive under config/ and group their frozen scientific documents under _engine/simulation/.

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
| D9 | Put frozen simulation documents together under _engine/simulation/; keep run_record.yml and sources/ under config/. | A user sees the readable configuration account separately from machine contracts. | Integrates t2609171500; exact destination is a recommendation |
| D10 | Preserve separate request and collection ownership, 12-character path prefixes and full digest identities. | Multiple requests can select one collection; short paths do not weaken identity checks. | Already landed in the post-R12 migration |

Three different hashes answer three different questions: did the source file's bytes change; did the declared configuration values change; did the scientific artifact's identity change? A comment edit changes the first. It must not, by itself, change the last. A new preparation contract or provider-code revision may legitimately change a new collection's identity; do not promise identical IDs across that migration.

### 3.1 Decision history and TODO reconciliation

The user's recollection that fewer scenario JSON files had been decided prompted a search of the TODO notes, ADRs, working notes, reviews, milestone documents, user docs and relevant Git history across local refs. **No explicit earlier approval to merge the collection sidecars was located.** This is a repository evidence limit, not a claim that the conversation never happened. D8 now makes a concrete consolidation proposal visible in the latest schema.

| Record | What it establishes | Effect on this schema |
|---|---|---|
| [Post-R12 migration](../milestones/post-r12/migration_scenario-tree.md), events 1–4; closed t2609152040/t2609152107 | scenarios/requests and scenarios/collections; request filename/schema rename; 12-character path segments with full digests retained | Already reflected in both trees. Grouping and naming did not remove collection JSONs. |
| [t2609152104](../tasks/t2609152104-separate-engine-bookkeeping-from-user-facing-artifacts-in-the-project-tree.md) versus migration event 6 | The live board says backlog and the note says changes 1/3 remain open; the migration records experiment/config-run engine bins and metric flattening as landed on 2026-09-16 | The checklist is stale. Treat final migration dispositions as evidence; do not reimplement its unchecked rows wholesale. |
| Same task, Change 3 | Scenario requests retain a directory because they hold request, receipts and generation artifacts; metric requests were flattened because each identity had one file | Keep request directories. Fewer folders is not fewer JSON records. |
| Same task, “Deliberately not proposed” | collection.json and collection_intent.json remain unmarked in the collection root | Preserve their distinct roles. This placement ruling does not prohibit embedding sidecars in the intent. |
| Migration event 6, declined rows | Collection preparation files were not moved: paths participate in identity; model engine bin was reversed; per-run logs stay beside responses | Do not revive declined moves. Shared elevation is now addressed through the later ADR and a versioned contract. |
| [t2609171500](../tasks/t2609171500-move-the-experiment-s-frozen-simulation-documents-into-engine.md) | Proposed moving the simulation family together; _engine/simulation versus _engine/config remained open | D9 selects _engine/simulation as the working recommendation, while leaving its acceptance and reader migration explicit. |
| [t2609191457](../tasks/t2609191457-make-wf3-planning-static-before-snakemake.md) | Active static-planning work; one authoritative immutable preflight plan | No approved JSON-file count. Avoid a second authoritative planning path. |
| [ADR 0011](../decisions/0011-preserve-config-sources-with-run-records.md) | Exact source archive and common invocation-history proposals; user-agreed shared elevation ownership | Integrated in §§4–7. Common invocation format may produce more files through child records even as it removes duplicate histories. |

The historical scenario naming migration approved a hard break and regeneration for its then-small known set of output trees. That dated ruling does not authorize deleting or rewriting today's sealed collections. The board itself has not been edited by this document; its outstanding dispositions need reconciliation before using it as an implementation checklist.

The closed scenario task was recovered with git show abe49967^:dev/tasks/t2609152040-regroup-the-scenario-trees-under-scenarios-and-rename-scenario-plans-to-requests.md. It explicitly rejected nesting collections under requests/experiments and merging request/product identities. Those ownership arguments still apply when scheduling becomes static.

### 3.2 Why `requests/` and `collections/` remain siblings

The recovered note considered the apparent simplification directly. Its accepted result was the current grouping under `scenarios/`, not a single merged identity or directory:

| Identity | Answers | Lifetime and location |
|---|---|---|
| `generation_request_id` | What was asked for from configuration, resolved inputs and provider settings? | Request-owned, replaceable discovery and execution records under `scenarios/requests/<request-id>/`. |
| `collection_id` | What scientifically meaningful scenario collection is intended? | Collection-owned immutable identity under `scenarios/collections/<collection-id>/`. |
| `collection_revision` | Which produced bytes make up the published collection? | Final inventory inside `collection.json`, known only after generation. |

The identities are not one-to-one. Two requests may differ in non-semantic details such as an absolute catalog path yet resolve to the same collection identity. Nesting the collection beneath either request would duplicate one immutable product or make another request reach sideways into the first request's directory. Flattening both kinds directly under `scenarios/` would erase whether a digest names an ask or a product and would mix safely replaceable request state with sealed collection state. Nesting scenarios under an experiment remains invalid because WF3 is model-independent and one collection can support multiple WF4 experiments.

The original note also relied on an ordering constraint: the request identity was available when the old checkpoint-shaped DAG was constructed, while the collection identity required staged source inventory and preparation context. Static WF3 preflight changes when the collection identity becomes available: the launcher can prepare sources and freeze an authoritative plan before constructing the generation DAG. That removes the checkpoint constraint, but it does **not** collapse the three identities, their many-to-one mapping or their different publication rules. `scenarios/requests/` therefore remains the home of request, plan, receipt and invocation-scoped generation state; `scenarios/collections/` remains the home of reusable scientific products.

The simplification retained by this proposal is consequently bounded:

- keep one semantic parent, `scenarios/`, with explicit `requests/` and `collections/` branches;
- consolidate collection provenance sidecars inside `collection_intent.json` as proposed by D8, without merging request and collection ownership;
- keep `collection.json` separate because publication of produced bytes occurs after the intent is frozen; and
- permit garbage collection of request-owned working state without making collection deletion appear safe.

This is an inherited architectural constraint, not a new approval of the draft `scenario-request/2` or `generation-plan/1` field contracts in §6.

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
rerun:
  project_source: project
  workflow: generate_scenarios
  path_policy: <agreed archive resolution policy>
  adjustments: []                       # explicit rerun changes, never edits to copies
~~~

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
      "path": "scenarios/collections/<id>/run_record.yml",
      "sha256": "<record file checksum>"
    }
  },
  "plan": {
    "path_base": "project_root",
    "path": "scenarios/requests/<request-id>/plans/<plan-sha256>.json",
    "sha256": "<plan file checksum>"
  },
  "artifacts": [
    {
      "kind": "scenario_collection",
      "id": "<full collection identity>",
      "path_base": "project_root",
      "path": "scenarios/collections/<id>/collection.json",
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

Preferred working separation: request.json becomes a discovery pointer; plans/<plan-sha256>.json is the immutable authority consumed by the generation DAG. A launcher resolves and pins one plan path and checksum, so another invocation replacing the pointer cannot redirect that DAG. Existing request readers must migrate together; retaining the filename does not imply schema compatibility.

Candidate pointer:

~~~json
{
  "schema_version": "scenario-request/2",
  "generation_request_id": "<full request identity>",
  "plan_path": "plans/<plan-sha256>.json",
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
| collection_revision | Existing ready revision for reuse; null for create | A new collection's forcing hashes are not yet knowable. |
| rows | Ordered row objects under the existing scenario-row contract | Fix run IDs, ancestors and perturbation mapping without redesigning their science. |
| outputs | Project-relative expected collection, forcing and preparation paths | Construct the generation DAG statically. |
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

Current preparation_context.json uses forcing-preparation/1. Its top-level fields are ancillary, catalog, forcing_elevation, generated_forcing_reader, pet_method and schema_version. The inspected elevation item has id, role, path, sha256, size_bytes and descriptor. Its path is collection-relative. preparation_catalog.yml contains the matching HydroMT elevation entry with that same local URI and the existing data adapter.

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

Recommend retaining preparation_catalog.yml beside the collection, with a relative URI that reaches the shared file from the catalog's location. The project-relative JSON reference and the catalog URI must resolve to the same checked bytes after project relocation. Verify actual HydroMT path resolution before accepting that choice; do not add CST-specific keys to HydroMT YAML or modify upstream code. Original machine paths can remain provenance, but must not be the only way the retained dependency is resolved.

This change affects more than a path in one JSON file. The consolidated intent binds its embedded preparation section by digest; that section binds the catalog and ancillary bytes. collection.json binds the intent and the completed outputs. Source inventory and provider code also contribute to identity. Specify coordinated reader/version and canonicalization changes before writing new collections. Existing scenario-collection/1 collections retain their local sidecars and data bytes. New consolidated/shared-reference collections require an explicit versioned dispatch contract; the exact collection version label remains open in §10.

Never edit the inspected sealed collection to demonstrate the proposed tree. Missing or modified shared data must cause a clear refusal before forcing preparation. Reusing a matching version verifies its checksum instead of replacing it. Standalone collection export would need an explicit bundling operation; the normal preservation unit is the project.

## 8. Consolidated scientific manifests and engine records

### 8.1 Collection JSONs: seven become two

Current count, inspected 2026-09-20: session-1/test_case/test_local/scenarios/collections/c3f88ea5c76f has seven root JSON files. scenario_collection.py's DOCUMENT_FILES mapping independently names the five provenance sidecars. The proposed fresh collection has two root JSON files; request plans, receipts and invocation history are outside this count. Re-measure before implementation.

| Existing file | Proposed location | Meaning retained |
|---|---|---|
| collection_intent.json | collection_intent.json | Frozen pre-generation identity, scenario semantics and expected rows. |
| generation_config.json | documents.generation_config inside the intent | Resolved generation settings and seed. |
| source_inventory.json | documents.source_inventory inside the intent | Original source inventory and byte identities; review roles/anchors for shared elevation. |
| provider_code_inventory.json | documents.provider_code inside the intent | Provider implementation inventory. |
| generation_environment.json | documents.environment inside the intent | Generation environment identity. |
| preparation_context.json | documents.preparation_context inside the intent | Forcing reader, PET and checked preparation dependencies (§7). |
| collection.json | collection.json | Final output inventory, revision and readiness, published last. |

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

Keep collection.json as a separate final record. It retains collection identity/revision, intent path/checksum, scenario-table reference, scenario-type artifacts, forcing entries with hashes/descriptors and ready status. Its existing preparation-context file reference becomes an explicitly versioned section reference to the checked intent, or is removed as redundant if all readers obtain preparation through the intent. The working recommendation is the latter: one authoritative embedded preparation object reached through the verified intent. Final strict field sets must be agreed before coding.

The five embedded sections retain the full evidence, not summaries. This reduces files, not necessarily bytes. A long environment inventory remains long inside the intent. The run_record.yml remains a readable source/config account and cannot substitute for scientific identity inputs.

### 8.2 Publication, identity and alternatives

An intent can be frozen before generation; the produced-byte inventory cannot. Keeping these two lifetimes separate preserves the existing claim and final-readiness distinction. Do not overwrite an intent to turn it into a success record. Missing collection.json still means the collection has not been published ready.

This is a coordinated schema migration. Current readers open named sidecars, enforce strict fields and hash their bytes. Specify canonicalization for each embedded document and the identity projection excluding self-referential fields. Prove whether pure packaging preserves identity under those functions. Do not assume matching parsed values guarantee matching digests; shared-data and provider-code changes may legitimately create new identities. Old sidecar-based collections remain readable and untouched.

| Alternative | Benefit | Tradeoff / when preferable |
|---|---|---|
| Keep seven JSONs | Smallest reader migration, components can be inspected independently | File clutter remains; preferable if compatibility risk outweighs ergonomics. |
| Two JSONs — working recommendation | Fewer files with clear intent versus completed-output boundary | Larger intent; coordinated initialization, publication and downstream-reader changes. |
| One collection JSON | Smallest visible count | Requires redesigning the pre-publication claim/state contract, or retaining another hidden intent anyway. Not selected here. |
| Move sidecars into _engine/ | Cleaner collection root | Same total count and path/identity migration. This is grouping, not consolidation. |

Keep preparation_catalog.yml as a separate HydroMT-native input. JSON consolidation does not authorize CST-specific catalog keys or changes in upstream HydroMT code.

### 8.3 Simulation documents: one machine-contract directory

Integrate t2609171500 by placing the frozen scientific document family together under experiments/<name>/_engine/simulation/. This is the recommended destination; the source task left _engine/config/ as an alternative. Both are separate from the readable config/run_record.yml and config/sources/ archive.

Move these six named files together: simulation.json, model_reference.yml, simulator_settings.json, simulation_environment.json, simulator_adapter_code_inventory.json and response_request.json. “Together” means the scientific family, not the entire old config/ directory including its human-facing snapshot. The current simulation manifest's four bare-filename sibling references remain valid when that family moves together.

The experiment-relative model.reference_path must change from config/model_reference.yml to _engine/simulation/model_reference.yml. Inventory every other stored and constructed path; do not infer safety from sibling references alone. New records use the new location; readers must still locate and validate existing retained simulations under the old contract. Keep response_inventory.json at the immediate _engine/ level: its ../ references to native artifacts already have the required depth. Moving it deeper can re-key metric identity.

This move does not consolidate simulation JSONs. It improves grouping while D8 reduces collection JSON count. Whether simulation identities stay unchanged must be checked against identity projections and path resolution, rather than promised from the tree alone. The older TODO's baseline target/cost assumptions also need remeasurement before implementation.

### 8.4 Other retained contracts

| File or family | What it proves / controls | Treatment |
|---|---|---|
| _engine/simulation/simulation.json | Today simulation/1: collection identity/revision/reference, model, settings, response request, environment, simulator/code, simulation_id, response_inventory_sha256 and experiment_name | Preserve meaning; version or adapt location resolution explicitly. Config archiving alone should not change scientific identity. |
| _engine/simulation/model_reference.yml and the four sibling JSON input documents | Frozen simulation inputs and requested responses | Preserve payload semantics; migrate the family and readers together. |
| _engine/response_inventory.json | response-inventory/1: native artifact checksums and series/time/unit/selector metadata | Keep path depth and scientific verification. This is not replaceable by invocation status. |
| _engine/metric_requests/*.json; results/metric_sets/*/metrics.json | Metric request and immutable metric-set identity/provenance | Retain. Metrics-only execution must not overwrite simulation creator provenance; exact source-archive ownership for later metric requests remains open. |
| metric_environment.json; return_level_benchmark.json; unit_index.csv; indicator tables | Metric environment and results | Retain independently identifiable metric sets. |
| spatial_catalog.yml; spatial_report.yml; projection summary provenance.json | Spatial and projection provenance | Retain; the historical engine-bin screen declined those generic relocations. |
| hydromt_build_config.yml; hydromt_update_waterbodies.yml; hydromt_data.yml; wflow_sbm.toml; retained per-run TOML/temporal JSON | Engine configuration and derived execution context | Stay beside their model/run. Use upstream formats verbatim. Temporary per-run HydroMT catalogs remain disposable under their existing rules. |

The local scientific JSON key inventories and current writers, rather than the old rule index, ground this comparison. Not every generated YAML or JSON needs consolidation; files used as upstream engine inputs have a different role from provenance sidecars.

## 9. Migration and alternatives

Write the new layouts for new executions/artifacts. Preserve old journals and invocation JSONs as legacy history; dispatch readers by schema and do not reinterpret old no_op values under the new semantics. Existing sealed collections and experiments remain byte-for-byte unchanged. Update snapshot readers, collection sidecar readers, simulation-location readers, declared Snakemake targets, tree inventories, fixtures and user documentation together. Baseline readers currently consume composed snapshots, so simply deleting the writer is not a complete migration.

For WF0–WF2, replacement of the latest archive must be coordinated with its matching record and any running reader. For WF3/WF4 reuse, no new source archive is inserted into an already sealed artifact. Invocation history records the new attempt and points to the original artifact. Whether metrics-only and failed-before-artifact invocations need separately retained source archives is unresolved; do not imply they already have full rerun coverage.

| Alternative | Benefit | Cost / when preferable |
|---|---|---|
| Retain composed_config.yml and add source copies | Lowest short-term reader migration cost | Continues two generated accounts. Useful as a temporary compatibility phase only if readers require it. |
| One project-wide config archive | Less repeated source storage | Later workflows can overwrite earlier provenance. Suitable only for a separately frozen coordinated run, not independent workflow execution. |
| Keep one append-only event journal | Rich transition history | Requires event reconstruction and coordination. Prefer it if intermediate transitions, beyond start/final state, are required. |
| Keep dynamic WF3 checkpoints | Preserves current cold-start invocation behavior | No fully resolved upfront generation DAG. Prefer if preserving that invocation contract is more valuable than static planning. |
| Keep ancillary data collection-local | Each collection carries its source elevation | Duplicates shared source data and conflicts with the agreed project-owned direction; useful for an explicit standalone export. |

## 10. Decisions still needed before a task brief

| Open item | Recommended starting point | Why it blocks implementation details |
|---|---|---|
| Exact schema versions and digest projections | Version the new record independently; preserve digest meanings | Avoid silently changing identity while renaming metadata fields. |
| Collection JSON consolidation | Two root JSONs; five complete provenance sections embedded in the intent | Requires accepted strict field sets, section canonicalization and old-sidecar reader dispatch. |
| Simulation machine-contract location | _engine/simulation/ for the six-file scientific family | The source task left this destination open; resolve stored paths and old-tree lookup together. |
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
6. **Simulation contract relocation.** Update experiment/simulation_record.py, scenario_collection.py collection-reference discovery, shared/cross_workflow_leaves.py, workflow leaves, retained readers and tree tests. Keep the human-facing archive in config/. Re-measure the old task’s baseline assumptions before deciding validation cost. Depends on the agreed §8.3 path/compatibility contract.
7. **Complete-run evidence.** Use an isolated rapid project after implementation; retain tree/schema comparison and scientific acceptance evidence. Depends on all units selected for the agreed scope.

These are candidate work packages, not a blanket authorization or a claim that each is one small patch. Before dispatch, remeasure readers/writers and produce bounded briefs with confirmed files and commands. Do not combine unrelated numerical fixes, change upstream HydroMT/Wflow internals, add resume semantics, prune old output trees or regenerate the comparison baseline as incidental cleanup.

Acceptance evidence to carry into those briefs:

| Claim | Observation that would disprove it / required check |
|---|---|
| Exact source recovery | Byte mismatch (including CRLF/comments), lost original basename, or missing loaded workflow/custom dependency. Test source copies and rerun with originals unavailable. |
| One matching archive | Interrupted or concurrent publication exposes mixed record/source checksums. Exercise failure points, not just a successful write. |
| Clear invocation history | Missing child linkage, a dry-run reported as work, or hard termination reported as success. Exercise direct, parent/child, startup failure, no-op and crash cases. |
| Stable scientific meaning | Comment-only edits alter scientific identity, row ordering/seeds change, or retained forcing differs beyond an agreed scientific comparison. Separate identity migration from numerical parity. |
| Reduced collection JSON count | A fresh collection still emits the five sidecars, embedded evidence is missing, tampering with an embedded section passes validation, or an old collection stops reading. Assert exactly the two agreed root JSONs and exercise all section readers. |
| Simulation grouping | A reference still points only to the old path, a retained old simulation cannot reopen, or response-inventory depth changes. Validate both locations and metrics-only reads. |
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
