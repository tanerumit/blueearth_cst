# Complete-run output tree and record schemas

- Status: working proposal — not an implementation brief or an implemented schema
- Date: 2026-09-20
- Inspected code: a76d4d65fb830cd6fb7db9f80eaa2b52f8a4787c
- Location: session-1, refactor/wf3-static-planning
- Lifecycle: temporary working document; revise in place, append revision history. Promote the accepted contract to dev/reference/ before closing the work.

## 1. What this document shows

This is a proposed output-project tree after a successful WF0–WF4 run, compared with the existing layout and generated metadata. “Output tree” means the contents of project_dir, not the Git worktree holding the toolbox.

The proposal brings together exact configuration archives, execution history, shared elevation data and the prospective WF3 static plan. It does not change the climate experiment, Wflow physics or metric definitions. WF2 remains a projection plausibility overlay; it does not supply generation scenarios.

Read §2–3 for the tree and plain-language decisions; §4–8 for schema comparisons; §9–11 for migration, unresolved choices and the outline of a future task brief. The detail is retained because the next reader needs to distinguish a renamed record from a changed scientific contract.

**Evidence boundary.** No new full run was executed for this document. The proposed writers do not exist yet. Current examples were inspected in session-1's test_case/test_local and test_case/test_rapid, alongside their writers. These are accumulated output trees, not evidence of one clean run at the inspected code revision. The local collection c3f88ea5c76f has a ready marker and 14 retained forcing entries; its experiment is named experiment. This inspection did not revalidate the forcing bytes or numerical results. Rapid supplies examples of WF0 records and wrapper invocation history. Its older retained collections do not have the artifact-local composed snapshot now written by current code.

Decision authority remains in [ADR 0011](../decisions/0011-preserve-config-sources-with-run-records.md). The static-planning boundary remains in [the WF3 intake](t2609191457-wf3-static-planning.md). This companion answers a different question: what would a user find in a completed output project, and what would each record contain? New field names and version labels below are draft suggestions, not approved APIs.

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

Legend: [new] introduced here; [changed] content or ownership changes; [kept] current scientific contract retained unless §7 requires a versioned change. A successful coordinated launch would normally leave a parent invocation and five child invocation records under the proposed launcher coverage. Source preparation belongs to the WF3 child's phases; it does not masquerade as a sixth workflow.

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
│       ├── collection_intent.json            [kept role; see §7]
│       ├── collection.json                   [kept role; see §7]
│       ├── generation_config.json            [kept]
│       ├── generation_environment.json       [kept]
│       ├── provider_code_inventory.json      [kept]
│       ├── source_inventory.json             [review role/path representation]
│       ├── preparation_context.json          [changed: shared-data reference]
│       ├── preparation_catalog.yml           [changed URI; retain HydroMT schema]
│       ├── scenario_table.csv                [kept]
│       ├── stress_test_lookup.csv            [kept]
│       └── forcing/run_<id>.nc                [kept]
├── experiments/<name>/
│   ├── config/
│   │   ├── run_record.yml                    [new: replaces composed snapshot]
│   │   ├── sources/
│   │   │   ├── project_config_rapid.yml
│   │   │   └── project_config_rapid_simulate_system.yml
│   │   └── ... scientific contract files     [kept: listed in §2.1 and §8]
│   ├── _engine/                              [kept]
│   ├── hydrology/wflow/                      [kept]
│   └── results/metric_sets/<id>/             [kept]
├── logs/                                     [kept]
└── benchmarks/                               [kept]
~~~

Each sources/ also holds required custom catalogs and engine templates, preserving their original names and relative structure. The two-file examples are not a claim that all archives contain exactly two files. Unmodified toolbox files may instead be recoverable through recorded revision/blob identity.

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

Three different hashes answer three different questions: did the source file's bytes change; did the declared configuration values change; did the scientific artifact's identity change? A comment edit changes the first. It must not, by itself, change the last. A new preparation contract or provider-code revision may legitimately change a new collection's identity; do not promise identical IDs across that migration.

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

Proposed separation: request.json becomes a discovery pointer; plans/<plan-sha256>.json is the immutable authority consumed by the generation DAG. A launcher resolves and pins one plan path and checksum, so another invocation replacing the pointer cannot redirect that DAG. Existing request readers must migrate together; retaining the filename does not imply schema compatibility.

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

## 7. Shared elevation: versioned preparation references

Current preparation_context.json uses forcing-preparation/1. Its top-level fields are ancillary, catalog, forcing_elevation, generated_forcing_reader, pet_method and schema_version. The inspected elevation item has id, role, path, sha256, size_bytes and descriptor. Its path is collection-relative. preparation_catalog.yml contains the matching HydroMT elevation entry with that same local URI and the existing data adapter.

Proposed forcing-preparation/2 changes the elevation reference anchor. Keep descriptors, units, data-adapter conversions and elevation selection semantics unchanged. Candidate item:

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

The size is from the inspected example, not a constraint. A content-hash directory is the recommended version scheme: retain the familiar original filename and keep different bytes at different paths. The alternative is a human-readable source version directory, preferable when the provider exposes stable, unambiguous versions; either way checksum verification is required.

Recommend retaining preparation_catalog.yml beside the collection, with a relative URI that reaches the shared file from the catalog's location. The project-relative JSON reference and the catalog URI must resolve to the same checked bytes after project relocation. Verify actual HydroMT path resolution before accepting that choice; do not add CST-specific keys to HydroMT YAML or modify upstream code. Original machine paths can remain provenance, but must not be the only way the retained dependency is resolved.

This change affects more than a path in one JSON file. collection_intent.json and collection.json bind the preparation context by digest; the context binds the catalog and ancillary bytes; source inventory and provider code contribute to identity. Specify coordinated reader/version and canonicalization changes before writing new collections. Existing scenario-collection/1 collections retain their local references and bytes. New shared-reference collections may need a new collection schema version; §10 records that decision rather than guessing it here.

Never edit the inspected sealed collection to demonstrate the proposed tree. Missing or modified shared data must cause a clear refusal before forcing preparation. Reusing a matching version verifies its checksum instead of replacing it. Standalone collection export would need an explicit bundling operation; the normal preservation unit is the project.

## 8. Scientific manifests and generated engine YAMLs that remain

| File or family | What it proves / controls | Treatment |
|---|---|---|
| collection_intent.json | Provider, seed/config/source/environment/preparation identity, row semantics and expected count; scenario-collection/1 today | Preserve purpose; coordinate new preparation references and versioning (§7). Do not add invocation timestamps to scientific identity. |
| collection.json | Ready collection: intent checksum, scenario table, forcing paths/descriptors/hashes, preparation reference, revision and status | Still published last after validation. A completed invocation is not a substitute. |
| generation_config.json; generation_environment.json; provider_code_inventory.json; source_inventory.json | Scientific generation settings and input/code/environment inventories | Retain. The human record cannot replace them. Review source-inventory path/role assumptions for shared elevation. |
| simulation.json | simulation/1: collection identity/revision/reference, model, settings, response request, environment, simulator/code, simulation_id, response_inventory_sha256, experiment_name | Retain strict schema unless preparation compatibility requires a reviewed change. Config archive alone should not alter it. |
| model_reference.yml; simulator_settings.json; simulation_environment.json; simulator_adapter_code_inventory.json; response_request.json | Frozen simulation inputs and requested responses | Retain existing contracts. |
| _engine/response_inventory.json | response-inventory/1: retained native artifact checksums and series/time/unit/selector metadata | Retain. This is more than bookkeeping and cannot be reconstructed from run status. |
| _engine/metric_requests/*.json; results/metric_sets/*/metrics.json | Metric request and immutable metric-set identity/provenance | Retain. A metrics-only invocation must not overwrite simulation creator provenance. Specify additional archive ownership if later metric requests need exact source recovery. |
| metric_environment.json; return_level_benchmark.json; unit_index.csv; indicator tables | Metric computation environment and results | Retain; metric sets stay independently identifiable. |
| spatial_catalog.yml; spatial_report.yml; projection summary provenance.json | Spatial and projection provenance | Retain; outside the archive/schema simplification. |
| hydromt_build_config.yml; hydromt_update_waterbodies.yml; hydromt_data.yml; wflow_sbm.toml; per-run YAML/TOML/temporal JSON | Engine configuration and derived execution context | Remain beside their model/run. They are not redundant composed snapshots. Use upstream formats verbatim. |

The local scientific JSON key inventories and writers, rather than the old rule index, were used for this comparison. Not every generated YAML or JSON needs a new schema. Moving all files with those suffixes into one metadata folder would break ownership and readers without simplifying the science.

## 9. Migration and alternatives

Write the new layouts for new executions/artifacts. Preserve old journals and invocation JSONs as legacy history; dispatch readers by schema and do not reinterpret old no_op values under the new semantics. Existing sealed collections and experiments remain byte-for-byte unchanged. Update snapshot readers, declared Snakemake targets, tree inventories, fixtures and user documentation together. Baseline readers currently consume composed snapshots, so simply deleting the writer is not a complete migration.

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
2. **WF0–WF2 and artifact-local adoption.** Wire the five workflow/launcher paths, with compatible readers and tests. Update declared outputs, baseline readers and output-tree inventory in the same runnable change. Depends on unit 1.
3. **Unified invocation history.** Update scripts/run_workflows.py, scripts/simulate_system.py and existing workflow journal hooks; add the agreed launcher coverage and parent/child ownership. Depends on the record-reference interface from unit 1, not on completed scientific runs.
4. **Shared ancillary contract.** Update climate_analysis/prepare_climate_data_catalog.py and experiment collection/preparation readers together. Establish backward compatibility before any new shared-reference collection is published. Depends on the decisions in §7, not necessarily the static planner.
5. **Static WF3 planning.** Update generate_scenarios.smk, experiment/generation_plan.py, collection_resolution.py, scenario_provider.py and scenario_collection.py plus the agreed entry point. Depends on frozen plan/invocation interfaces and the preparation contract it will validate.
6. **Complete-run evidence.** Use an isolated rapid project after implementation; retain tree/schema comparison and scientific acceptance evidence. Depends on all units selected for the agreed scope.

These are candidate work packages, not a blanket authorization or a claim that each is one small patch. Before dispatch, remeasure readers/writers and produce bounded briefs with confirmed files and commands. Do not combine unrelated numerical fixes, change upstream HydroMT/Wflow internals, add resume semantics, prune old output trees or regenerate the comparison baseline as incidental cleanup.

Acceptance evidence to carry into those briefs:

| Claim | Observation that would disprove it / required check |
|---|---|
| Exact source recovery | Byte mismatch (including CRLF/comments), lost original basename, or missing loaded workflow/custom dependency. Test source copies and rerun with originals unavailable. |
| One matching archive | Interrupted or concurrent publication exposes mixed record/source checksums. Exercise failure points, not just a successful write. |
| Clear invocation history | Missing child linkage, a dry-run reported as work, or hard termination reported as success. Exercise direct, parent/child, startup failure, no-op and crash cases. |
| Stable scientific meaning | Comment-only edits alter scientific identity, row ordering/seeds change, or retained forcing differs beyond an agreed scientific comparison. Separate identity migration from numerical parity. |
| Shared ancillary safety | Two collections copy the same version unnecessarily, changed bytes pass, old collections stop reading, or relocation breaks catalog resolution. Test all four. |
| Static generation scheduling | Either checkpoint still expands the generation DAG, live pointer replacement redirects execution, or cold dry-run silently produces scientific outputs. Inspect DAGs and filesystem differences. |
| Backward compatibility | Existing sealed output checksums change or legacy readers cannot load their schema. Snapshot retained files before/after reuse and refusal. |
| Complete-run tree | A fresh isolated WF0–WF4 run lacks a required record, reference cannot resolve, or temporary provider files are wrongly retained. Capture the actual tree and representative schemas after successful execution. |

During implementation, run focused tests for the changed surfaces. Apply tests/test_cli.py when rules/signatures/declared inputs change and the repository's lint/format checks for Python. At approved batch landing use the documented combined gates; shared/signature changes require the stated full-suite rung. Run numerical baseline comparisons only when their scope warrants them, using the baseline configuration and preserving its WF1 temporary discharge target with --notemp. Do not repeatedly run the full suite for each incremental edit. Exact new manifest/archive test commands belong in the finalized briefs once test files exist.

## 12. Sources and verification of this draft

Read-only evidence: current metadata files under session-1's test_case/test_local and test_case/test_rapid; current snapshot writers; generation_plan.py; scripts/run_workflows.py and scripts/simulate_system.py; ADR 0011 and the WF3 intake. Inspected output IDs identify examples, not fresh validation results.

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
