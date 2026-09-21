# Complete-run output tree and record schemas — P0 contract, design v3

- Status: P0 selected contract for review; G1 framing recorded, G2 owner acceptance pending; runtime implementation is not authorized
- Date: 2026-09-21
- Inspected code: a1a97ffeccea41eed3d1bf449d94f0487121f300; runtime source read only
- Location: session-2, refactor/workflow-layouts
- Lifecycle: temporary review artifact; revision history is append-only. After G2, integrate the accepted contract into the source proposal and ADR 0011, then promote the maintained-current specification to dev/reference/ before task closure. This review copy is not a competing permanent specification.

## 1. What this document shows

This is a proposed output-project tree after a successful WF0–WF4 run, compared with the existing layout and generated metadata. “Output tree” means the contents of project_dir, not the Git worktree holding the toolbox. The target contract describes fresh project outputs only.

The proposal brings together exact configuration archives, execution history, shared elevation data and the prospective WF3 static plan. It preserves the stochastic generation algorithm, Wflow physics and metric definitions. The new WF3-only automatic-seed projection can change numerical seeds and hence realizations; those changes must be distinguished from algorithmic differences using matched explicit-seed comparisons. WF2 remains a projection plausibility overlay; it does not supply generation scenarios.

Read §10 first for the selected normative P0 decisions and interfaces; §2–3 for the preserved tree and decision history; §4–8 for layout and payload rationale; §9 and §11 for alternatives and implementation validation. Section 10 controls the illustrative sketches in §§4–8. The detail is retained because the next reader needs to distinguish a renamed record from a changed scientific contract.

**Evidence boundary.** No new full run was executed for this document. The proposed writers do not exist yet. Current examples were inspected in session-1's test_case/test_local and test_case/test_rapid, alongside their writers. These are accumulated output trees, not evidence of one clean run at the inspected code revision. The local collection c3f88ea5c76f has a ready marker and 14 retained entries currently named forcing; its experiment is named experiment. This inspection did not revalidate the scenario-series bytes or numerical results. Rapid supplies examples of WF0 records and wrapper invocation history. Its older retained collections do not have the artifact-local composed snapshot now written by current code.

Decision authority remains in [ADR 0011](../../../decisions/0011-preserve-config-sources-with-run-records.md). The static-planning boundary remains in [the WF3 intake](../../t2609191457-wf3-static-planning.md). This document is the single latest working output-schema proposal: what would a user find in a completed output project, and what would each record contain? Integrate future layout and schema proposals here rather than maintaining competing trees. ADRs, task notes and migration records retain decision history; this document does not silently turn their open proposals into approvals. The selected names, versions and publication rules are fixed for this review in §10; they become implementation authority only after G2.

The selected tree incorporates a **seven-to-two reduction in collection JSON files** (§8), a collection-centred `scenarios/` layout with one scenario-level `_engine/` (§3.2), shared elevation (§7), exact source archives (§4), common invocation history (§5), static planning (§6), and consolidation of the simulation family under the experiment engine directory (§8.3). The seven-to-two collection mapping and simulation contract are selected P0 decisions pending G2, not recovered prior approvals. The decision/TODO reconciliation is included in §3.1.

**Review reading rule (2026-09-21).** Section 10 is normative for this v2 and settles the candidate ambiguities in §§2–8. Those sections preserve the layout, payload rationale and prior decision history; their abbreviated examples are not independent competing contracts. G2 remains pending. The owner first asked to preserve the current `seed: auto` calculation, then required strict WF3 independence when its elevation dependency was identified, and clarified that preserving the formula permits numeric seeds to change. The present seed material includes elevation and a code inventory containing WF4 preparation code, so its inputs must change to honor that boundary. Keep the canonical digest-to-integer method, define and version a WF3-only seed projection, and validate the expected identity and numerical effects. P4 remains additive until P5 can switch the WF3 producer and its consumers together.

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
│   │   │   ├── <workflow-invocation-id>.json  [new/common: one per child]
│   │   │   └── <invocation-id>/config/      [conditional: later/failed attempt archive, §10.4]
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
│       ├── generation_inputs/<full-sha256>/   [new: immutable generation input copies, §10.5]
│       │   └── <original-basename>
│       └── ancillary/era5/<content-sha256>/   [new: full content SHA-256]
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
│   │   ├── scenario_run_lookup.csv            [changed: one row per collection run]
│   │   ├── perturbation_lookup.csv            [changed: monthly changes by perturbation ID]
│   │   └── series/run_<id>.nc                  [changed: scenario time series, not forcing]
│   └── _engine/                              [new: one scenario-level machine-contract bin]
│       ├── requests/<request-id>/
│       │   ├── request.json                   [changed: discovery pointer]
│       │   ├── <plan-sha256>.json              [new: immutable execution plan]
│       │   └── initializations/<invocation-id>.json [kept role; binding changes]
│       └── collections/<collection-id>/
│           ├── collection_intent.json        [changed: embeds four WF3 sidecars]
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
│   │   │   ├── forcing_elevation_catalog.yml [new: retained WF4 HydroMT elevation binding]
│   │   │   ├── run_<id>.toml                  [changed: retained Wflow run settings]
│   │   │   ├── run_<id>.yml                   [temporary: HydroMT data catalog]
│   │   │   └── run_<id>.temporal.json         [temporary: per-run validation handoff]
│   │   ├── forcing/inmaps_run_<id>.nc         [temporary: Wflow-ready forcing]
│   │   └── output/
│   │       ├── run_<id>.csv                   [kept: retained native response]
│   │       └── _log/run_<id>.log              [changed: retained Wflow run log]
│   └── results/metric_sets/<id>/
│       ├── metric_run_lookup.csv             [changed: run_group_id membership]
│       └── <token>_indicators.csv            [changed: run_group_id join key]
├── logs/                                     [kept]
└── benchmarks/                               [kept]
~~~

Each sources/ also holds required custom catalogs and engine templates, preserving their original names and relative structure. The two-file examples are not a claim that all archives contain exactly two files. Unmodified toolbox files may instead be recoverable through recorded revision/blob identity.

New collections have two scientific JSON documents in `scenarios/_engine/collections/<collection-id>/` instead of seven in the old collection root; four WF3 sidecar payloads become embedded intent sections, while the legacy WF4 preparation context becomes experiment-owned evidence. Request plans and initialization receipts are outside that count. The user-facing collection groups exact creator configuration, a provider-specific `weathergenr/` integration subtree and provider-independent scenario products under `series/`. The archive belongs to the collection's creator; a later equivalent request records its own attempt without overwriting these sources. The large intermediate realization netCDFs remain temporary under the existing Snakemake contract, at `weathergenr/output/run_<id>.nc` while needed; they are not entries in the completed output tree. The same `run_id` identifies the temporary generator product and its retained `series/run_<id>.nc` counterpart, but the two paths have different lifetimes. The legacy `rlz_<n>_st_<n>.nc` filename is not part of the proposed output contract. `series/run_<id>.nc` denotes the current stochastic collection's retained climate time series, not Wflow-ready forcing or a mandatory folder for every future scenario type. WF4 owns any subsequent conversion or selection for a system model. New experiments keep the human-facing archive under `config/` and the frozen scientific records directly under `_engine/`.

The proposed `scenario_run_lookup.csv` is collection-owned, even when its runs are later selected by an experiment. It replaces the current `scenario_table.csv` and, for stochastic collections, has columns `run_id,evaluate,type,rlz,st_id`: omit the redundant `derived_from`, rename `evaluated` to `evaluate` and shorten `scenario_type` to `type` within this scenario-specific CSV. `evaluate=true` is an intended eligibility/selection flag, not evidence that WF4 simulation has occurred; completed evaluation is recorded by the experiment's responses and readiness records. Within each `rlz`, the unique row with empty `st_id` is the unperturbed root; every nonempty-`st_id` row in that realization derives from it. Thus `rlz` identifies the family, while `st_id` distinguishes its root from its perturbations. New validators must require exactly one root per realization and the configured realization × perturbation cross-product; this lineage rule applies to the stochastic provider, not arbitrarily to future providers. `perturbation_lookup.csv` replaces `stress_test_lookup.csv` as the collection's `st_id` × month lookup of temperature, precipitation and precipitation-variance changes. Version the CSV header, semantic digest and all readers; existing collections retain their original filename, columns and identity.

### 2.3 File-level changes in this proposal

These are proposed files for **new** outputs; current files and sealed collections keep their existing names and schemas.

| Current file | Proposed file | File-level change |
|---|---|---|
| `scenarios/collections/<id>/scenario_table.csv` | `scenarios/<id>/scenario_run_lookup.csv` | For stochastic collections, header changes from `run_id,derived_from,evaluated,scenario_type,rlz,st_id` to `run_id,evaluate,type,rlz,st_id`. Infer the root from the unique empty-`st_id` row in each `rlz`; `evaluate` declares intended eligibility, not completed simulation. |
| `scenarios/collections/<id>/stress_test_lookup.csv` | `scenarios/<id>/perturbation_lookup.csv` | Filename changes; monthly `st_id`–temperature/precipitation change columns and values remain as before. |
| Request `generation/output/rlz_<n>_st_<n>.nc` | Temporary `scenarios/<id>/weathergenr/output/run_<id>.nc` | Name both root and perturbed generator products by the corresponding scenario `run_id`; retain their `temp()` lifecycle. These files are absent from the completed output tree, unlike published `series/run_<id>.nc`. In the implementation batch, change the R root writer to write `run_<id>.nc` directly (not write the legacy name and rename it afterward), and align Snakemake declarations, provider inputs and the perturbation writer's output path. |
| Collection-local `preparation_catalog.yml` | `experiments/<name>/hydrology/wflow/run_settings/forcing_elevation_catalog.yml` | Move the checked HydroMT elevation binding to WF4; shared orography bytes remain under `data/climate/ancillary/`. Remove the WF4-only preparation dependency from new collection identity and bind it in simulation intent. |
| `experiments/<name>/results/metric_sets/<id>/unit_index.csv` | `experiments/<name>/results/metric_sets/<id>/metric_run_lookup.csv` | Rename `unit_id` to `run_group_id` and `member_run_id` to `run_id`; proposed header: `run_group_id,grain,run_id`. One group has either one run or multiple bundle members. |
| `experiments/<name>/results/metric_sets/<id>/<token>_indicators.csv` | Same filename under the proposed set root | Rename its `unit_id` join column to `run_group_id`; proposed header: `metric,location,run_group_id,value`. The key joins to `metric_run_lookup.csv`. |

The run-group rename is a cross-file contract, not just two CSV headers. In new WF3 configuration and `collection_intent.json`, rename `unit_id_capacity` to `run_group_id_capacity`; rename the derived intent field `unit_id_width` to `run_group_id_width`. In new metric-plan JSON and its readers, rename `bundle_unit_ids` to `bundle_run_group_ids` and any group-key `unit_id` field to `run_group_id`. Retain `run_id` for individual scenario runs and for the lookup's member-run column. Preserve the existing padded identifier values and allocation order: single-run groups use their run IDs, and bundle groups receive IDs after the complete run domain. These coordinated names require a versioned identity/reader change wherever the fields enter a digest; this is not a runtime change in this document.

New outputs stop writing composed_config.yml, journal.jsonl and the central config/catalogs, config/templates and config/generated archive destinations. A fresh tree has no collection-local ancillary/elevation directory under the new contract. CHIRPS extraction sidecars are not automatically relocated merely because the ERA5 source dependency moves.

## 3. Decisions in plain language

| ID | Direction | Why / practical consequence | Standing |
|---|---|---|---|
| D1 | Keep the original YAML files exactly as read, beside one generated run record. | The user keeps comments and filenames; the generated record explains the values that were loaded. | ADR 0011 proposal |
| D2 | Keep WF0–WF2's latest configuration account; keep WF3/WF4 accounts with their own artifacts. | A second collection must not overwrite the first collection's provenance. Reuse must not rewrite the creator's account. | ADR 0011 proposal |
| D3 | Use one invocation JSON format for all entry points. | A reader can distinguish an attempt, a dry-run, a no-op and a failed execution without joining unrelated log formats. | ADR 0011 proposal |
| D4 | Put forcing-source elevation in shared project data and bind it by checksum from WF4 experiments. | Experiments can share identical elevation bytes without making model-specific forcing preparation part of a WF3 collection. | User-agreed shared-data ownership; WF4 binding is the revised working proposal |
| D5 | Prepare sources first; freeze the WF3 plan before constructing its generation DAG. | Content-derived identities cannot be known before required source bytes exist. | WF3 intake recommendation; not yet accepted |
| D6 | Keep scientific manifests separate from the human-facing record. | A readable YAML account is not proof that a collection or simulation is complete. Existing strict readers remain meaningful. | Preserved boundary |
| D7 | Define one output schema for fresh project runs, without previous-output readers. | The toolkit is in development; compatibility adapters would add scope without serving a required use case. | Owner-directed 2026-09-21 correction |
| D8 | Embed the four WF3 collection provenance sidecars in collection_intent.json; retain collection.json separately. Move the legacy preparation context to WF4. | Seven collection JSONs become two, with distinct intent and readiness lifetimes and no model-specific collection dependency. | Revised working recommendation; versioned identities/readers required |
| D9 | Embed the five frozen simulation input documents in _engine/simulation_intent.json and publish a separate _engine/simulation.json completion marker; keep run_record.yml and sources/ under config/. | Exact scientific inputs remain verifiable while immutable intent and completed-output claims have separate lifetimes; a two-file family needs no dedicated folder. | Extends t2609171500; versioned reader and identity migration required |
| D10 | Preserve separate request and collection identities, 12-character path prefixes and full digests, but put their records in one `scenarios/_engine/` bin. | Multiple requests can select one user-facing collection without displaying two sibling user trees. | Identity and prefix rules landed post-R12; placement is this working proposal |
| D11 | Keep `config/` for the collection's user-level configuration account; put the resolved `weather_generation_input.yml` and generator products under `<provider>/`. | Exact `project_config_*` sources, the run record and provider-specific settings remain distinguishable without a generic `generated/` bin. | Owner-directed naming for the working layout; no Wflow filename change |
| D12 | Name retained WF3 climate time series `series/run_<id>.nc`, reserving `forcing/` for a system-model-ready input at the WF4 boundary. | Generated scenarios may need post-processing or may never become a model forcing. | Owner-directed semantic correction; path and manifest migration proposed |
| D13 | Rename the experiment's Wflow `config/` directory to `run_settings/`; retain per-run TOML, but retain common temporal evidence only in `response_inventory.json`. | Distinguishes generated Wflow run settings from user configuration and avoids one duplicate temporal JSON per run. | Owner-confirmed working layout; versioned selector migration required |
| D14 | Keep Wflow's per-run logs under `hydrology/wflow/output/_log/`, beside but separate from native response CSVs. | `output/` stays easy to scan for response data while preserving each Wflow diagnostic log and its run attribution. | Owner-confirmed working layout; update `logging.path_log` and create the directory before execution |
| D15 | Keep indicator tables and `metric_run_lookup.csv` under `results/metric_sets/<id>/`; group the marker and benchmark under the experiment's single `_engine/metric_sets/<id>/`, embedding `metric_environment.json` in `metrics.json`. | The lookup lets users see which runs or bundles underpin metrics, while machine provenance stays out of the result directory. | Owner-directed revision; cross-sibling binding and updated metric readers required, subject to D21 |
| D16 | Name the collection-level CSVs `scenario_run_lookup.csv` and `perturbation_lookup.csv`. | The first identifies each scenario run and its ancestry/perturbation in a reusable WF3 collection; the second identifies monthly climate changes for each perturbation ID. Neither is owned by one WF4 experiment. | Owner-directed naming intent; proposed filenames and versioned reader migration |
| D17 | Keep shared orography in project climate data, put its HydroMT `forcing_elevation_catalog.yml` binding and checked preparation settings in WF4, and exclude WF4 elevation and preparation code from WF3 seed and collection identity. | A WF4-only change cannot alter WF3 collection selection or automatic stochastic draws. | Owner-confirmed strict boundary; requires a new seed-material projection and identity change |
| D18 | Omit `derived_from` from new stochastic `scenario_run_lookup.csv` rows; infer their root from the unique empty-`st_id` row within the same `rlz`. | Avoids storing a duplicate parent ID while preserving checkable same-realization ancestry. | Owner-directed column simplification; new header/digest and current-reader update required |
| D19 | Rename proposed `evaluated` to `evaluate` in the stochastic run lookup. | The WF3 flag states intended evaluation eligibility; it does not report completed WF4 simulation. | Owner-directed tense correction; versioned column readers required |
| D20 | Shorten proposed `scenario_type` to `type` within `scenario_run_lookup.csv`. | The file's scenario context already disambiguates the column, while its value and validation remain unchanged. | Owner-directed column naming; versioned header/readers required |
| D21 | Use `run_group_id` in both `metric_run_lookup.csv` and `<token>_indicators.csv`, replacing `unit_id`. | The key identifies one run or a bundle of runs, not a measurement unit; the two tables retain an explicit join. | Owner-directed clean break now covered by D7 |
| D22 | Use `run_id` rather than `member_run_id` as the third `metric_run_lookup.csv` column. | Each lookup row already means that one scenario run belongs to the stated run group; the shorter name also matches the scenario run lookup. | Owner-directed column naming; proposed header is `run_group_id,grain,run_id` |

Three different hashes answer three different questions: did the source file's bytes change; did the declared configuration values change; did the scientific artifact's identity change? A comment edit changes the first. It must not, by itself, change the last. A new preparation contract or provider-code revision may legitimately change a new collection's identity; do not promise identical IDs across that migration.

The existing `generation-seed-material/1` hashes a source projection containing ancillary elevation and a provider-code inventory that includes `prepare_climate_data_catalog.py`; its canonical digest becomes an integer modulo `2**31 - 1`. The resolved seed enters the identity-bearing generation configuration. The owner's strict WF3 independence requirement therefore supersedes exact preservation of the v1 input projection. The target is a new, explicitly versioned WF3-only seed material: retain the canonical digest-to-integer method and the climate, basin, perturbation, generator-settings and true generator-code dependencies; exclude WF4 elevation bytes, HydroMT forcing-preparation settings and WF4-only code. P0 must enumerate the code inventory and canonical fields precisely. The current `generation_plan.py` also calls WF4 preparation code, so move that responsibility across the WF3/WF4 module boundary or establish a rigorously scoped generator-code inventory before claiming that a WF4-only edit leaves the seed and collection ID unchanged. The owner accepts that changing the seed material or inventoried generator code can change numeric automatic seeds. Test automatic seeds with two elevation versions and a WF4-only code/config change, and compare generated series under a matched explicit seed.

### 3.1 Decision history and TODO reconciliation

The user's recollection that fewer scenario JSON files had been decided prompted a search of the TODO notes, ADRs, working notes, reviews, milestone documents, user docs and relevant Git history across local refs. **No explicit earlier approval to merge the collection sidecars was located.** This is a repository evidence limit, not a claim that the conversation never happened. D8 now makes a concrete consolidation proposal visible in the latest schema.

| Record | What it establishes | Effect on this schema |
|---|---|---|
| [Post-R12 migration](../../../milestones/post-r12/migration_scenario-tree.md), events 1–4; closed t2609152040/t2609152107 | The existing `scenarios/requests` and `scenarios/collections` paths, request filename/schema rename, and 12-character path segments with full digests retained | Reflected in the existing tree. The new user-facing layout supersedes the path grouping, not the distinct identities or prefix rule. |
| [t2609152104](../../../tasks/t2609152104-separate-engine-bookkeeping-from-user-facing-artifacts-in-the-project-tree.md) versus migration event 6 | The live board says backlog and the note says changes 1/3 remain open; the migration records experiment/config-run engine bins and metric flattening as landed on 2026-09-16 | The checklist is stale. Treat final migration dispositions as evidence; do not reimplement its unchecked rows wholesale. |
| Same task, Change 3 | Scenario requests retained a directory because they held request, receipts and generation artifacts; metric requests were flattened because each identity had one file | Keep request directories for plan/receipt history, but move user-valued generation products to the selected collection. Fewer visible folders is not fewer records. |
| Same task, “Deliberately not proposed” | collection.json and collection_intent.json remained unmarked in the collection root | Preserve their distinct roles; moving both to the single scenario `_engine/` is a new proposal and needs versioned readers. |
| Migration event 6, declined rows | Collection preparation files were not moved: paths participate in identity; model engine bin was reversed; per-run logs stay beside responses | The new WF3/WF4 boundary deliberately revisits preparation ownership with versioned identity/readers; it does not retroactively change that migration decision or sealed collections. |
| [t2609171500](../../../tasks/t2609171500-move-the-experiment-s-frozen-simulation-documents-into-engine.md) | Proposed moving the simulation family together; _engine/simulation versus _engine/config remained open | D9 now consolidates the input documents and places the two simulation records directly under _engine/; acceptance and reader migration remain explicit. |
| [t2609191457](../../../tasks/t2609191457-make-wf3-planning-static-before-snakemake.md) | Active static-planning work; one authoritative immutable preflight plan | No approved JSON-file count. Avoid a second authoritative planning path. |
| [ADR 0011](../../../decisions/0011-preserve-config-sources-with-run-records.md) | Exact source archive and common invocation-history proposals; user-agreed shared elevation ownership | Integrated in §§4–7. Common invocation format may produce more files through child records even as it removes duplicate histories. |

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

The following is a schema sketch. Tokens such as <full composed mapping> deliberately stand for values, not literal production strings. The exact version registry and field additions are in §10.2.

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

Do not hash this path-bearing YAML wholesale into `collection_id`: its output directory contains the collection path, so that would create a self-reference and make relocation alter scientific identity. Use the explicit v2 semantic generator projection in §10.7 for identity, then checksum the exact emitted YAML as execution evidence in the run record.

Store the full loaded mapping once. A projection identifies which parts feed a configuration digest; it does not require another full copy of the values and does not claim every field was used by a rule. Preserve the existing digest computation until a separately reviewed change replaces it. Changing a record's container schema must not silently redefine its digest.

A record captures the settings loaded for this execution, even if the workflow later fails. Success belongs to the invocation record and, where applicable, the sealed scientific manifest. Capture source bytes at load time so an edit during execution cannot make the archive describe different inputs.

WF0–WF2 need a publication mechanism that makes the record and its sources one matching generation. Writing each file atomically is insufficient: a crash can still leave a new record beside old sources. The selected replace/recovery protocol is §10.3. WF3/WF4 create their archive before sealing and preserve it on reuse. A later reuse invocation points to the original archive and records its own supplied configuration hashes in its invocation record; it must not claim to be the original creator.

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

The parent uses the same envelope with workflow: null, its ordered requested workflow sequence and child IDs. Each child owns its own file. The parent records launch failures even when no child could start; it must not invent a child outcome. The parent launch-failure fields are fixed in §10.4.

Separate status (running, succeeded, failed) from mode (execute, dry_run) and work_performed (yes, no, unknown). A zero exit code does not establish that calculations ran. Missing completion after termination means unknown outcome; do not retrospectively label it failed without evidence. Optional references are null when failure precedes creation; collections are empty, never omitted (§10.2).

Atomic start/final updates avoid partial JSON. New invocation UUIDs preserve attempts. WF0–WF2 archive paths are replaceable, so their references must include a checksum; an older invocation may retain only a checksum after its configuration archive is replaced. This proposal does not add historical config retention. Do not report a mismatching latest archive as the older invocation's input.

**Coverage recommendation:** normal user entry points should have a launcher that starts the record before configuration validation and subprocess startup. New-schema WF0–2 production requires the pre-parse capture launcher; raw diagnostics have reduced coverage. Hooks cannot record failures that occur before those hooks run. The selected launchers and explicit reduced-coverage cases are in §10.4.

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
| documents | Selected creator WF3 source/config/code/environment objects | Equal intent.documents; candidate_intent carries current attempt evidence (§10.5). |
| candidate_intent, candidate_intent_sha256, candidate_identity_digests, creator_archive | Current candidate evidence and separately selected creator archive | Receipt binds both intent hashes; create/reuse equality rules are in §10.5. |
| source_inventory_sha256 | Existing inventory digest | Bind current candidate pinned input evidence and revalidate immutable bytes. |
| decision | create or reuse_ready | Freeze which execution branch was selected. |
| collection_revision | Existing ready revision for reuse; null for create | A new collection's scenario-product hashes are not yet knowable. |
| rows | Ordered row objects under the existing scenario-row contract | Fix run IDs, ancestors and perturbation mapping without redesigning their science. |
| outputs | Project-relative expected collection and scenario-series paths | Construct the generation DAG statically without WF4 preparation outputs. |
| path_base | project_root | Make the output-path anchor explicit. |
| counts | Retained row count and potential generation work only | Do not confuse these with Snakemake's actual scheduled jobs. |

Hash the canonical serialized plan bytes and put the checksum in the filename/pointer, not inside its own hashed content. Invocation UUID and timestamps belong in invocation history, not scientific identity. A receipt must bind the executing invocation to the pinned plan in addition to the existing ownership facts; its versioned schema is fixed in §10.5.

Recheck inputs and the selected collection state before initialization. If a competing invocation creates the collection after a create plan was frozen, refuse/replan; do not silently switch that plan to reuse. This proposal preserves refusal of interrupted partial collections. It does not establish resume, leases or managed run-control conformance.

The static plan is possible only after region/climate/lookup preparation and required generation-source bytes exist. WF4-only orography must not gate the WF3 plan. Cold-start dry-run must state that final content planning is unavailable; it must not extract data while claiming to be read-only. Both existing checkpoints, including publication-dependent expansion, must be addressed for the generation DAG to become static. Shared generation working directories still need an isolation/refusal policy for competing plans.

### 6.1 Why the selected contract retains a discovery pointer

A discovery pointer plus immutable plans adds a JSON layer. The current working tree retains it because default WF4 collection discovery needs an explicit route from the request to its selected collection. Section 10.5 retains it for request-to-collection discovery while removing it from execution authority.

An alternative is to pass one immutable authoritative plan path directly and omit the pointer. Prefer that if normal WF4 discovery can remain explicit and reliable without another mutable index. Either implementation must pin the executing plan's bytes; two independent planners or a mutable request as execution authority are not acceptable shortcuts.

Initialization receipts retain their invocation/ownership role until a replacement supplies equivalent checks. They cannot simply be put into scientific identity, which excludes invocation UUIDs. Plans and receipts are retained by default; cleanup is outside this migration (§10.5).

## 7. Shared elevation and WF4 preparation ownership

Current preparation_context.json uses forcing-preparation/1. Its top-level fields are ancillary, catalog, forcing_elevation, generated_forcing_reader, pet_method and schema_version. These are existing schema spellings, not a claim that the published WF3 series are already WF4 forcings; any replacement terminology needs a versioned contract rather than a cosmetic field rename. The inspected elevation item has id, role, path, sha256, size_bytes and descriptor. Its path is collection-relative. preparation_catalog.yml contains the matching HydroMT elevation entry with that same local URI and the existing data adapter.

In the new layout, the collection remains model-independent: neither Wflow's preparation context nor its elevation catalog belongs in `scenarios/<id>/` or the collection intent. WF4 selects the checked shared elevation when binding a collection to a model and records the elevation reference, HydroMT adapter, PET method and correction settings in its frozen `simulation_intent.json`. A candidate experiment-owned elevation reference is:

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

Retain the HydroMT-native elevation binding under `experiments/<name>/hydrology/wflow/run_settings/forcing_elevation_catalog.yml`. Its name says what it catalogs without fixing ERA5 as the only future climate source. WF4 reads this checked catalog, adds the selected scenario series and writes a temporary per-run catalog for Wflow preparation. The retained catalog and `simulation_intent.json` must agree on source path, checksum, adapter settings and relative-URI anchor; verify that a copied project still resolves to the same bytes. The shared orography file owns its bytes, while the experiment owns the Wflow-specific use of those bytes. Do not add CST-specific keys to HydroMT YAML or modify upstream code.

This changes scientific identity, not only a path. Today WF3's source projection, `collection_id` and collection revision bind the orography and preparation context even though weather generation does not consume them; that projection also affects the automatic seed. Remove direct and indirect WF4-only elevation/forcing-preparation inputs from the new WF3 seed and collection identity. Preserve every dependency required to prepare historical climate: CHIRPS/chirps_global extraction uses hydrography elevation and ERA5 orography to lapse-correct temp/temp_min/temp_max. That unchanged correction belongs to WF3 source preparation; its effect enters identity through historical_climate bytes, with its provenance retained in source evidence. Cold CHIRPS extraction requires those elevation dependencies; consumption of an already frozen, verified climate store does not require re-opening them. Only unneeded WF4 sidecar publication may become optional, never the source correction itself. Put checked elevation and preparation settings in the new simulation identity. The seed-material schema and collection identity must change together; identical numeric automatic seeds across that input change are not guaranteed. The selected schema labels are registered in §10.2.

Missing or modified WF4-only elevation refuses dependent WF4 preparation but does not invalidate WF3 with fixed verified source bytes. Missing CHIRPS source-preparation elevation can still refuse cold extraction. Reusing a matching version verifies its checksum instead of replacing it. Standalone experiment export must bundle its checked elevation dependency; the normal preservation unit is the project.

## 8. Consolidated scientific manifests and engine records

### 8.1 Collection JSONs: seven become two

Current count, inspected 2026-09-20: session-1/test_case/test_local/scenarios/collections/c3f88ea5c76f has seven root JSON files. scenario_collection.py's DOCUMENT_FILES mapping independently names the five legacy provenance sidecars. The proposed fresh collection has two scientific JSON files under its `scenarios/_engine/collections/<id>/` record directory, embedding four WF3 sidecars and moving preparation ownership to WF4; request plans, receipts and invocation history are outside this count. Re-measure before implementation.

| Existing file | Proposed location | Meaning retained |
|---|---|---|
| collection_intent.json | _engine/collections/<id>/collection_intent.json | Frozen pre-generation identity, scenario semantics and expected rows. |
| generation_config.json | documents.generation_config inside the intent | Resolved generation settings and seed. |
| source_inventory.json | documents.source_inventory inside the intent | Original generation-source inventory and byte identities; exclude WF4-only elevation. |
| provider_code_inventory.json | documents.provider_code inside the intent | Provider implementation inventory. |
| generation_environment.json | documents.environment inside the intent | Generation environment identity. |
| preparation_context.json | WF4 simulation intent and elevation catalog (§7) | Former collection-owned preparation evidence becomes experiment-owned in new outputs. |
| collection.json | _engine/collections/<id>/collection.json | Final output inventory, revision and readiness, published last. |

Abbreviated intent structure; exact fields and digest projections are fixed in §10.7:

~~~text
schema_version: <new collection-intent schema>
canonicalization_id: <declared canonicalization>
collection_id: <full scientific identity>
provider: <existing name and revision>
scenario_type: <existing value>
scenario_spec: <existing scenario specification>
scenario_semantics_sha256: <existing semantics digest>
run_count: <expected row count>
run_group_id_capacity: <existing capacity>
run_group_id_width: <existing width>
documents:
  generation_config: <complete former sidecar object>
  source_inventory: <complete former sidecar array>
  provider_code: <complete former sidecar array>
  environment: <complete former sidecar object>
document_digests:
  generation_config: <canonical embedded document checksum>
  source_inventory: <canonical embedded document checksum>
  provider_code: <canonical embedded document checksum>
  environment: <canonical embedded document checksum>
~~~

Keep collection.json as a separate final record. It retains collection identity/revision, intent path/checksum, scenario-run lookup reference, scenario-type artifacts, retained-series entries with hashes/descriptors and ready status. The current manifest calls those entries forcing; the new schema must version their paths and terms rather than treating the rename as identity-neutral. Remove its WF4 preparation-context reference in the new collection version; the experiment's frozen simulation intent owns that dependency. The new manifest location also requires an explicit project-relative reference to the sibling `scenarios/<collection-id>/` data root; never infer readiness from the data directory alone. Section 10.7 supplies the strict new envelope and projections.

The four embedded WF3 sections retain their full evidence, not summaries. This reduces files, not necessarily bytes. A long environment inventory remains long inside the intent. The run_record.yml remains a readable source/config account and cannot substitute for scientific identity inputs. The retained `sim_dates.csv` and `resampled_dates.csv` need explicit byte references in the final collection inventory or a separately checked provenance record; merely moving them under the collection would not make their evidentiary role verifiable. Evaluation plots are terminal diagnostics, not inputs to collection identity.

### 8.2 Publication, identity and alternatives

An intent can be frozen before generation; the produced-byte inventory cannot. Keeping these two lifetimes separate preserves the existing claim and final-readiness distinction. Do not overwrite an intent to turn it into a success record. Missing engine-side collection.json still means the collection has not been published ready, even if its sibling data directory exists. Publish the marker last, after checking the data-root path, expected files and hashes. Validation must refuse a marker without matching data and ignore orphaned data without a marker.

This is a coordinated schema migration. Current readers open named sidecars, enforce strict fields and hash their bytes. Specify canonicalization for each embedded document and the identity projection excluding self-referential fields. Prove whether pure packaging preserves identity under those functions. Do not assume matching parsed values guarantee matching digests; shared-data and provider-code changes may legitimately create new identities.

| Alternative | Benefit | Tradeoff / when preferable |
|---|---|---|
| Keep seven JSONs | Smallest reader migration, components can be inspected independently | File clutter remains; preferable if implementation risk outweighs ergonomics. |
| Two JSONs — working recommendation | Fewer files with clear intent versus completed-output boundary | Larger intent; coordinated initialization, publication and downstream-reader changes. |
| One collection JSON | Smallest visible count | Requires redesigning the pre-publication claim/state contract, or retaining another hidden intent anyway. Not selected here. |
| Keep the two JSONs beside the user-facing products | Easier standalone directory inspection | Exposes machine readiness contracts at the collection root; preferable if detached collection export is the primary use case. The working layout instead uses one scenario-level _engine/. |

Keep `forcing_elevation_catalog.yml` as a separate experiment-owned HydroMT-native input. JSON consolidation does not authorize CST-specific catalog keys or changes in upstream HydroMT code. Bind its checked path in the WF4 simulation intent; no collection-local preparation-catalog reader is required after the migration.

### 8.3 Simulation documents: two engine-side records

Integrate and extend t2609171500 by placing two scientific records directly under `experiments/<name>/_engine/`, separate from the readable `config/run_record.yml` and `config/sources/` archive. With only two simulation records, an additional `simulation/` level does not distinguish a useful ownership boundary; `_engine/` already groups this experiment's machine contracts. `simulation_intent.json` freezes the full contents of today's `model_reference.yml`, `simulator_settings.json`, `simulation_environment.json`, `simulator_adapter_code_inventory.json` and `response_request.json` as named sections, along with collection selection, simulator identity and `simulation_id`. The proposal reduces six simulation-family files to two; it does not discard the per-model-input hashes or any requested-response details. Wflow's own settings files and names are outside this consolidation.

Compute and retain separate canonical section digests for settings, adapter code, environment and response request so the accepted scientific identity projection remains auditable. Keep the model digest and its per-input evidence together in the embedded model-reference section. The complete intent is immutable once frozen; a same-identity reuse checks its bytes and referenced source identities rather than replacing it. A new schema must define section canonicalization and distinguish content digests from the old sidecar file checksums before claiming `simulation_id` continuity. Replace old `model.reference_path` and sibling-file references in current readers with checked intent sections; no old-simulation reader is required.

Publish `simulation.json` only after the matching `_engine/response_inventory.json` and retained native responses have been verified. During execution, the response-inventory producer reads the frozen intent without requiring that final marker. The marker binds the exact intent path/checksum, `simulation_id`, creator archive FileRef, response-inventory path/checksum and completed response claim; it cannot substitute for checking the inventory and files. An absent final marker means the simulation is not ready for metrics-only reuse, even if intent or native output exists. Keep `response_inventory.json` at the immediate `_engine/` level: its relative references to native artifacts already have the required depth, and moving it deeper can re-key metric identity. Invocations record failed or interrupted attempts separately; do not turn a partial intent into a success marker.

Current metric planning, response-inventory production and metric-set validation read `config/response_request.json` directly. They must read and verify the embedded section instead, and stored metric-set references must become checked section references rather than dangling file paths. Inventory every other stored and constructed path, update declared rule targets, and validate new experiments on fresh outputs. The older TODO's baseline target/cost assumptions need remeasurement before implementation.

### 8.4 Other retained contracts

| File or family | What it proves / controls | Treatment |
|---|---|---|
| _engine/simulation_intent.json | Frozen collection selection, model reference, settings, response request, environment, simulator/code and simulation identity | Embed the full five input-document payloads and preserve separately checked scientific section digests; immutable before native simulation. |
| _engine/simulation.json | Final completed-simulation marker, not the current mutable simulation/1 record | Publish last and bind the checked intent, creator archive and response inventory; a missing marker is not readiness. |
| _engine/response_inventory.json | response-inventory/2: native artifact checksums and series/time/unit/selector metadata | Keep path depth and scientific verification. This is not replaceable by invocation status. |
| _engine/metric_requests/*.json; _engine/metric_sets/*/metrics.json | Metric request and immutable metric-set identity/provenance | Retain separate request and published-set identities. Metrics-only execution must not overwrite simulation creator provenance; later metric attempts own invocation-local source archives (§10.4). |
| Metric environment; return_level_benchmark.json; metric_run_lookup.csv; indicator tables | Frozen metric environment, exact benchmark evidence, run/bundle mapping and results | Embed the environment in the set's marker; keep the benchmark in the matching experiment-engine set directory, with the lookup and indicator tables under `results/metric_sets/<id>/`. Current `unit_index.csv` is a legacy name, not a second proposed file. |
| spatial_catalog.yml; spatial_report.yml; projection summary provenance.json | Spatial and projection provenance | Retain; the historical engine-bin screen declined those generic relocations. |
| hydromt_build_config.yml; hydromt_update_waterbodies.yml; hydromt_data.yml; wflow_sbm.toml; retained per-run TOML | Engine configuration and derived execution context | Keep model files beside the model and per-run TOML under experiment `hydrology/wflow/run_settings/`. Use upstream formats verbatim. Temporary per-run HydroMT catalogs remain disposable under their existing rules. |

The local scientific JSON key inventories and current writers, rather than the old rule index, ground this comparison. Not every generated YAML or JSON needs consolidation; files used as upstream engine inputs have a different role from provenance sidecars.

### 8.5 Generated Wflow run settings and temporal evidence

The current `experiments/<name>/hydrology/wflow/config/` holds `run_<id>.toml`, `run_<id>.yml` and `run_<id>.temporal.json` for each run. These have different roles. Wflow executes the TOML and the response reader verifies it against retained native output, so keep each `run_<id>.toml` unchanged by name and content under `hydrology/wflow/run_settings/`. The `run_<id>.yml` is a per-run HydroMT data catalog already declared `temp()`; it may be written in that directory while preparing a run but is not a required retained product. Do not change its HydroMT schema or filename. The temporal JSON is CST validation evidence, not a Wflow setting. In the proposed tree, the annotated temporary entries show files that exist during execution, not a promise that they remain in a clean published output. The Wflow-ready `forcing/inmaps_run_<id>.nc` is likewise already declared temporary; the native `output/run_<id>.csv` and Wflow's per-run log are retained.

Today each TOML's `[logging] path_log` directs Wflow to `../output/run_<id>.log` relative to that TOML's directory. Point new TOMLs to `../output/_log/run_<id>.log` and create `_log/` before Wflow starts; do not move logs after execution or change their basenames. The settings-directory rename preserves the relative depth, but generated TOML output, forcing and model paths still need explicit validation. Preserve the existing per-member log attribution checks for new runs. The Wflow-native logs are distinct from the workflow's gathered logs under the project-level `logs/` directory.

Current publication requires every run's temporal evidence to match a single common value and embeds that value as `response_inventory.json`'s `temporal_preparation`. The checked baseline run 01 and run 14 files, and rapid run 01 and run 10 files, were byte-identical; this sampling supports the redundancy observation but is not a proof for all future inputs. The proposed new response-inventory schema retains the common temporal object once, while each run's actual prepared clock and transformation chain is still checked against its TOML and the common object before publication. Per-run temporal files can be temporary handoff artifacts and removed after successful publication; an implementation may instead pass equivalent checked evidence between preparation and publication without materializing them. Do not merely copy run 01's record to the others or omit per-run checks.

The current native selectors store each TOML and temporal file path and checksum. An inventory and metric-reader change must replace the temporal file references with the checked common section and update TOML paths for `run_settings/`. Keep failed or interrupted runs' temporary evidence recoverable until their publication/refusal outcome is known; normal Snakemake cleanup must not erase evidence needed to diagnose a partial run. This proposal changes retained file count, not Wflow's execution semantics or the native CSV response contract.

### 8.6 Metric-set results and machine contracts

Keep `results/metric_sets/<id>/` because one completed simulation already supports subsequent metrics-only requests, and changed metric definitions or environments produce new immutable sets without overwriting previous tables. Put the `<token>_indicators.csv` tables and `metric_run_lookup.csv` there: the latter exposes which `run_id` values belong to each `run_group_id` (a singleton run or a bundle) and lets users join the metric tables to their input runs. The proposed headers are `metric,location,run_group_id,value` and `run_group_id,grain,run_id`; preserve ID values and membership while making a clean break from the old `unit_id`/`member_run_id` columns. Group `metrics.json` and `return_level_benchmark.json` under the experiment's single `_engine/metric_sets/<id>/`. The matching full `metric_set_id` binds these two sibling directories; neither directory alone is a complete export. The benchmark remains exact retained validation evidence, not a derived summary.

Embed the full `metric_environment.json` payload as a named section of the new `_engine/metric_sets/<id>/metrics.json`, retaining its independently checked canonical digest in the `metric_set_id` projection. The marker remains the last published file and must verify the benchmark within its engine set directory and the unit index and every result table through explicit experiment-relative references confined to the matching result directory. Neither an orphaned result directory nor an engine record without its checked tables is a ready set. A project copy or standalone set export must carry both directories; discovery starts from checked markers, not a bare `results/` listing. Update current metric target construction, strict path checks, metric-set discovery and external consumers together. Embedding the environment removes one file, not its scientific evidence.

## 9. Migration and alternatives

Write the new layouts for fresh executions/artifacts. New runs target fresh project outputs so different schemas are not mixed. Update current snapshot readers, collection discovery and path-containment checks, simulation-location readers, declared Snakemake targets, tree inventories, fixtures and user documentation together. Baseline readers currently consume composed snapshots; plan the baseline tree/manifest transition explicitly rather than silently changing a writer or treating an old tree as new evidence. Do not rename Wflow-owned YAML/TOML files as part of the scenario layout or generated-input naming change.

For WF0–WF2, replacement of the latest archive must be coordinated with its matching record and any running reader. For WF3/WF4 reuse, no new source archive is inserted into an already sealed artifact. Invocation history records the new attempt and points to the original artifact. Metrics-only and failed-after-load attempts retain invocation-local archives under §10.4; failed parsing cannot claim a valid loaded configuration record.

| Alternative | Benefit | Cost / when preferable |
|---|---|---|
| Retain composed_config.yml and add source copies | Lowest short-term migration cost | Continues two generated accounts. Useful only as a short implementation bridge. |
| One project-wide config archive | Less repeated source storage | Later workflows can overwrite earlier provenance. Suitable only for a separately frozen coordinated run, not independent workflow execution. |
| Keep one append-only event journal | Rich transition history | Requires event reconstruction and coordination. Prefer it if intermediate transitions, beyond start/final state, are required. |
| Keep dynamic WF3 checkpoints | Preserves current cold-start invocation behavior | No fully resolved upfront generation DAG. Prefer if preserving that invocation contract is more valuable than static planning. |
| Retain every `run_<id>.temporal.json` | Existing strict selectors and partial-run diagnostics work unchanged | Duplicates the same checked evidence for every run. Prefer only as a short implementation bridge if inventory and reader changes cannot land together. |
| Keep metric-set JSONs beside indicator CSVs | No metric-set path migration or cross-sibling binding | Leaves machine provenance and the large benchmark report in the user-facing result directory; prefer if established external readers cannot migrate together. |
| Put a nested `_engine/` in each result set | Keeps all set files under one directory | Repeats machine bins in every set and conflicts with the preferred single experiment-level `_engine/`; preferable for independently moved set directories. |
| Embed the benchmark report in `metrics.json` | One JSON file per metric set | Inflates the ready marker with a large independently retained report and entangles its exact-byte validation with marker publication; prefer only if a single-file export requirement outweighs that separation. |
| Embed all simulation inputs in one mutable `simulation.json` | One fewer file than the proposed intent/marker pair | Rewrites a document that also carries frozen identity inputs when completion is recorded; prefer only if strict immutability of the input record is unnecessary. |
| Move all six existing simulation-family files without consolidation | Smallest payload-schema change | Retains five separate input sidecars and today's mixed input/completion record; prefer if section-reader migration cannot be delivered together. |
| Keep user-visible `scenarios/requests/` and `scenarios/collections/` | Smallest path migration; request-local working outputs remain co-located | Makes users navigate machine identities to find generation inputs, date products and diagnostics. Prefer if implementation cost outweighs the navigation improvement. |
| Put provider before collection ID: `scenarios/weathergenr/<id>/` | Browsing all collections from one provider is easy | Makes the primary collection path and lookup depend on provider; prefer only if provider-grouped navigation is the dominant user task. |
| Keep ancillary data collection-local | Each collection carries its source elevation | Duplicates shared source data and conflicts with the agreed project-owned direction; useful for an explicit standalone export. |

## 10. Selected P0 contract

Request type: **improve**. This section settles the master brief's choices for review; acceptance is G2, not the existence of this draft. Sections 2–9 explain the selected layout and retained payloads. Where their illustrative examples omit a field, this section supplies the complete boundary. No runtime implementation or run-control readiness is asserted.

### 10.1 Decision table, ownership and first emission

| Decision | Selected contract | Implementing phase / first production emission |
|---|---|---|
| P0-01 Exact sources and digest families | Capture bytes once at load; separate byte evidence, configuration projection and scientific identity. Closed, versioned projections below. | P1 library; P2 WF0–2; P5 WF3; P6 WF4 |
| P0-02 Coherent archive | Staged directory generation, serialized publication and reader protocol, durable transaction journal, deterministic recovery; never independent live file replacement. | P1; adoption P2/P5/P6 |
| P0-03 Rerun paths | Exact originals stay immutable; generated resolver overlay maps archived sources and explicit external relocations. No raw invocation of copied absolute YAML references is claimed portable. | P1 interface, P2/P5/P6 consumers |
| P0-04 Launch coverage | Supported launchers create common records before scientific configuration validation; explicit project root enables this. New-schema WF0–2 require pre-parse capture through the launcher; raw emission refuses. WF3 uses an explicit interim legacy route in P3/P4 and requires a pinned launcher plan from P5. | P2 capture launcher; P3 history; P5 WF3 switch |
| P0-05 Plans and ownership | Immutable content-addressed plan; replaceable discovery pointer; immutable per-invocation receipt; project-wide exclusive execution ownership on supported local filesystems. Partial scientific artifacts refuse reuse. | P3 ownership primitive, P4 validators, P5 first plan/receipt |
| P0-06 Seed and collection | generation-seed-material/2, unchanged SHA-256-to-integer formula; WF3-only code closure and scientific input projection. New collection/lookup schemas. | P4 additive fixtures, P5 first collection |
| P0-07 Elevation | Shared full-content-hash directory, project-relative reference, experiment-owned native HydroMT catalog and simulation identity binding. | P4 foundation, P6 first experiment binding |
| P0-08 Simulation and metrics | Immutable embedded simulation intent plus final marker; response-inventory/2 common temporal evidence; metric-set/2 paired engine/result roots and run_group_id. | P6 |
| P0-09 Clean break | Fresh project roots; new readers reject old versions. Existing artifacts are never rewritten. No output-compatibility dispatcher. | P2/P5/P6 respective boundary |
| P0-10 Scientific comparison | Capture clean WF3 reference before runtime edits and pin/capture a separate predecessor WF4 comparator before affected changes; exact matched-explicit-seed comparison; independent v2 auto-seed tests allow changed draws. | P0 WF3 capture and WF4 comparator pin; predecessor WF4 capture before affected implementation; P5/P6 comparisons; P7 integration |
| P0-11 Baseline | Old committed baseline remains a frozen reference until separately authorized replacement; updated readers must diagnose its old contract, never auto-record. | P2/P5/P6 readers; explicit post-P6 baseline transition |
| P0-12 Archive ownership of later attempts | Creator archive immutable; metrics-only and failed attempts retain invocation-local archives when loading succeeds. WF0–2 retain only their latest archive. | P3 lifecycle, P6 metrics-only |

Implementation roles are scoped: python-engineer owns Python interfaces and rules, r-developer owns direct R member naming at P5, model-builder executes the P0/P5/P7 fixtures, and model-validator returns scientific acceptance. The CST architect integrates contracts and returned evidence. These are handoff targets, not agents dispatched by this document.

All applicable bindings are anchored to repository revision a1a97ffeccea41eed3d1bf449d94f0487121f300 for the inspected behavior. Implementation revision and actual dependency revisions must be frozen in the resulting records; unavailable runtime revisions are a run-admission failure, not guessed version strings.

| Capability slot | Binding / immutable revision authority | Owner and validation authority |
|---|---|---|
| data_adapter | HydroMT/hydromt_wflow interfaces as used at the inspected revision; actual package revisions from recorded environment | python-engineer interfaces; model-builder runs; model-validator checks climate/model handoffs |
| ensemble_generator | weathergenr plus CST R provider; package RemoteSha/version and complete code inventory in intent | r-developer and model-builder; model-validator |
| simulation_engine | Wflow; actual Julia manifest tree hashes and executing version | model-builder; model-validator |
| system_model_validation | Existing historical/native-response validation at the inspected revision | model-validator; no new scientific acceptance threshold |
| performance_analysis | Existing retained-response indicator definitions/code at the inspected revision | python-engineer migrates contracts; model-validator checks numerical equivalence |
| projection_overlay | Existing WF2 projection products and pinned inputs; terminal plausibility overlay | python-engineer archive adoption; model-validator checks retained outputs |
| orchestrator | Existing Snakemake binding plus new static plan; exact runtime version and implementation inventory recorded | python-engineer; architect structural checks plus focused workflow tests |

decision_framing, impact_model and robustness_evaluation are not_applicable: this migration declares no new assessment framing, impact outputs or robustness scores. Projection products never select or drive generation; stochastic perturbations supply stress-test scenarios.

No scientific run is planned for a managed root by this document. cst-run-control conformance and namespace claim are **not assessed / not claimed**. The local exclusion protocol below is not fencing, distributed ownership, or managed-run conformance. Before implementation fixtures target a managed root, their run owner must apply that root's run-control contract and win its claim independently.

### 10.2 Types, versions and canonical digests

Notation: C(x) is the existing collection-canon/1 serializer: UTF-8, sorted object keys, compact separators, non-ASCII preserved, one final LF, ordered arrays, finite plain JSON values only, no duplicate keys. Its existing Python float representation, including 1.0 and -0.0, is retained. H(x) = lowercase SHA-256(C(x)); B(file) = SHA-256(exact file bytes). Full identities are 64 lowercase hex characters. Request/collection/metric path segments remain the first 12 characters with full-ID collision refusal; ancillary content directories use the full 64 characters.

A new record has exactly its declared fields, except explicitly named open payload maps. Missing optional scalar/object values are null, optional collections are empty arrays/maps, never omitted. Unknown schema versions or unclassified semantic fields fail closed. Cross-language conformance vectors must include floats, Unicode, empty lists and the final LF; JavaScript JSON serialization is not implicitly the canonicalizer.

Record/reference vocabulary:

~~~text
FileRef = {schema_version:"artifact-reference/1",
           path_base: enum(project_root,experiment_root,record_directory,request_directory),
           path: confined-relative-POSIX-path, sha256:Digest, size_bytes:nonnegative-int}
SectionRef = {schema_version:"section-reference/1", document:FileRef,
              section: declared-JSON-pointer, section_sha256:Digest}
LocalSectionRef = {schema_version:"local-section-reference/1",
                   section:"/temporal_preparation", section_sha256:Digest}
SourceEntry = {id, role, original_path, archived_path, path_base:"record_directory",
               sha256, size_bytes, recoverable, git_blob}
~~~

No stored FileRef contains an absolute path, dot segments, a drive, UNC authority, empty segment or symlink escape. Original paths are provenance locators, not executable FileRefs. Anchors are supplied by the validated owning record/root; a record cannot choose an arbitrary root. SectionRef verifies the whole document's B hash, then H of the named section; it never uses a section as a substitute for document validation. LocalSectionRef is permitted only in a response inventory native selector and refers to that same inventory. It has no path, document reference or whole-document hash. Validate the enclosing inventory digest first, then its permitted pointer and H of the named section. External SectionRef always retains its document FileRef; substituting a local reference across documents is refused. This avoids a self-hash fixed point. Path-bearing exact evidence is excluded from scientific identity unless explicitly included below.

Version registry and read/write boundary:

| Surface | Version | First emission |
|---|---|---|
| Run record / archive journal | run-record/2 / archive-transaction/1 | P1 fixtures; P2 production |
| References / invocation | artifact-reference/1, section-reference/1, local-section-reference/1 / invocation/1 | P1 fixtures / P3 production |
| Request payload / discovery pointer | generation-request/2 / scenario-request/2 | P5 |
| Immutable plan / initialization receipt | generation-plan/1 / generation-initialization/2 | P5 |
| Auto seed material | generation-seed-material/2 | P5 (P4 tests) |
| Collection intent and final marker | scenario-collection-intent/2 / scenario-collection/2 | P5 |
| Scenario lookup / perturbation lookup semantics | scenario-run-lookup/2 / perturbation-lookup/1 | P5 |
| Simulation intent / ready marker | simulation-intent/1 / simulation/2 | P6 |
| WF4 preparation / native response inventory | forcing-preparation/2 / response-inventory/2 | P6 |
| Reader semantics / response scientific projection | forcing-reader-identity/1 / response-inventory-identity/1 | P6 |
| Metric request / plan / final set | metric-request/2 / metric-plan/2 / metric-set/2 | P6 |
| CSV metric membership / table | metric-run-lookup/2 / indicator-table/2 | P6 |

CSV versions live in the enclosing plan/manifest, not an extra CSV comment row. Exact headers are those in §2; quoting, numeric values, padded IDs and allocation order retain predecessor behavior. Booleans parse strictly to true/false; rlz/st_id/run_id are strings preserving padding; empty st_id is the root. Semantic row digest is H of ordered typed row objects with run_id removed; the new keys are evaluate,type,rlz,st_id. Derive ancestry only after validating one root per rlz and the complete configured cross-product; no perturbed member, including a zero-change design point, aliases its root.

run-record/2 has the §4.2 keys plus archive_id and archive_schema_version:"source-archive/1". Its owner.kind additionally permits invocation. configuration_projection.digest_schema_version is 2, selecting the existing provenance EFFECTIVE_CONFIG_SCHEMA_VERSION=2 functions at the inspected revision; preserve their type-tagged canonical_data and input projection rather than substituting C. source hashes remain B. archive_id is H of {schema_version:"source-archive/1", workflow, invocation_id, source_files:[{id,role,archived_path,sha256,size_bytes}], loaded_config, advanced_settings, configuration_projection, referenced_inputs, generated_inputs, rerun}, with source_files sorted by id. It excludes archive_id, timestamps, absolute original locators, command and toolbox diagnostics. It identifies this archive generation, not scientific identity. Record B and source B are independently verified.

For each embedded document below store both full evidence and a named semantic projection when they differ. document_digests hash full embedded values; identity_digests hash the explicitly defined projection. Readers recompute both. This prevents conflating a path-bearing source inventory checksum with a scientific dependency checksum.

#### 10.2.1 Nested schema register (normative)

This register closes the nested objects used by §§10.2–10.7. A named profile versions an embedded payload without inserting a new key into that payload; the enclosing version selects the profile. This preserves arrays used by provider_revision and the separate predecessor configuration/model digest algorithms. A profile change requires an enclosing schema version change. P4/P6 implement these definitions; they do not decide missing classifications later.

Here text is nonempty string, integer excludes booleans, number is finite, Path is confined relative POSIX path, Locator is provenance-only string, and Value is recursively finite JSON (ordered arrays and string-keyed maps included). Map<K,V> allows arbitrary keys only in that named data namespace, never additional control fields. All shown keys are required. A named Maybe<T> is exactly {present:false,value:null} or {present:true,value:T}; it preserves a provider argument's absence separately from explicit null. Omitted upstream arguments must not become null at the R boundary. Other objects retain §10.2 null rules. Duplicate keys/set members refuse. Arrays preserve order except where explicitly sorted below; readers reject unsorted encodings of those sets.

| Profile / field | Exact shape, ordering and constraints |
|---|---|
| source-entry/1 — source_files | SourceEntry in §10.2: id/role/original_path/archived_path are text, sha256=B(captured bytes), size_bytes≥0, recoverable is boolean, git_blob is null or immutable blob ID. Sort by unique id. recoverable=true requires captured bytes or retrievable recorded blob. |
| archive-referenced-input/1 — referenced_inputs | [{id:text,role:text,original_path:Locator,source_id:null-or-text,sha256:Digest,size_bytes:integer≥0}], sorted by unique id. source_id names source_files when captured, otherwise null; external inputs require explicit relocation mapping. sha256 is B. |
| archive-generated-input/1 — generated_inputs | [{role:text,file:FileRef}], sorted by (role,file.path). Every FileRef has B and size_bytes; no future output is listed. §4.2 shorthand expands to this full form. |
| archive-rerun/1 — rerun | {project_source:text,workflow:text,path_policy:"captured-source-map/1",adjustments:[ResolverOverlay]}. project_source names captured project entry; adjustments is empty for original creation and exactly one overlay for rerun. |
| resolver-overlay/1 — ResolverOverlay | {schema_version:"resolver-overlay/1",source_record:FileRef,source_map:[{source_id:text,original_path:Locator,captured:FileRef}],project_root_mapping:{from:Locator,to:Locator},external_mappings:[{id:text,from:Locator,to:Locator,sha256:Digest,size_bytes:integer≥0}],overrides:Map<text,Value>,output_project_dir:Locator}. Sort source_map by source_id, external_mappings by id. source_record/captured use record_directory and retained predecessor/source paths. External hashes are B. Mappings/overrides are fully retained archive evidence. |
| code-inventory/1 — provider_code, simulator_adapter_code, metric code_inventory | [{path:repository-relative-Path,sha256:Digest}], unique and sorted by path using Unicode code-point order and '/' separators; sha256=B(source file). H of this exact array is the inventory digest. |
| stage-environment/1 — generation/simulation environment | {packages:Map<text,text>,locks:Map<text,Digest>}. packages holds actual runtime/version/build/RemoteSha/tree identity strings, using predecessor python/platform/python:/conda:/R:/julia: names. locks permits only installed-python-distribution-metadata, installed-conda-dependency-records and Manifest.toml. First two values are H of records below; Manifest.toml is B. Required executing packages cannot be unknown. An observed unavailable transitive distribution may retain literal not-installed only when not executed. |
| installed-records/1 — environment preimages | Python: Map<package,{version:text,metadata_sha256:Digest} or {status:"not-installed"}>; metadata_sha256=B(installed METADATA UTF-8 bytes). Conda: Map<package,{name:text,version:text,build:text,sha256:null-or-Digest,md5:null-or-32-lowercase-hex,depends:[text]}>. Preserve dependency-list order and nulls. |
| year-window/1 | {start:positive-integer,end:positive-integer}, end≥start. |
| perturbations/1 | {temp:{n_levels:positive-integer,trajectory:"transient" or "constant",mean:Range12},precip:{n_levels:positive-integer,trajectory:"transient" or "constant",mean:Range12,variance:Range12},spell_factors:{dry:Number12,wet:Number12}}. Range12={min:Number12,max:Number12}; Number12 is twelve finite numbers in Jan→Dec order. Resolve supported defaults once before projection (absent spell factors become twelve 1.0 values); retain supplied numeric types under C. |
| generation-settings/2 — request.settings | {n_realizations:positive-integer,simulation_window:year-window/1,climate_perturbations:perturbations/1,weathergen_config:Locator,seed:integer-or-"auto",run_group_id_capacity:positive-integer}. Resolve defaults before writing. request.source={catalogs:[Locator],climate:text,store:Locator}; preserve catalog precedence order. request.template is Locator; water_year_start is the validated three-letter month. |
| scenario-spec/1 | {scenario_type:"stochastic",n_realizations:positive-integer,n_design_points:positive-integer,unperturbed_per_realization:1,expected_run_count:positive-integer,simulation_window:year-window/1,pairing:"paired_across_design_points",row_order:"rlz-major/unperturbed-first/st-id-ascending"}. Counts obey the cross-product formula. |
| generation-config/2 — documents.generation_config | {seed:{requested:integer-or-"auto",resolved:integer},seed_resolution:{seed_request:integer-or-"auto",resolved_seed:integer,projection:generation-seed-material/2,projection_sha256:Digest,seed_resolution_id:Digest},run_group_id_capacity:positive-integer,weathergen:generator-arguments/1,climate_perturbations:perturbations/1}. Redundant seed/perturbation values must agree. generation-config-identity/2 takes window/count/month from the frozen scenario specification/resolved arguments, checked against seed material. No unresolved seed reaches an intent. |
| generation-source-inventory/2 — documents.source_inventory | {sources:[{role:text,original_path:Locator,file:FileRef,metadata:Map<text,Value>}],interpretation:{revision:text,variables:[{name:text,units:text}],calendar:text,time_label:"interval_end"}}. sources sorts by unique role; historical_climate and basin_cells are the two scientific pinned sources, generator_template/catalog_N are captured evidence (N follows catalog precedence). metadata is evidence only; no consumed setting may hide there. Variables sort by unique name. Seed/source identity extracts file.sha256/size_bytes for the two scientific roles. Plan source_inventory_sha256=H of this entire document. |
| generator-arguments/1 — weathergen | Exactly six sections and argument names in §10.6. Required values retain parsed finite JSON scalar/array/map types. Optional upstream arguments use Maybe<Value> below. Included scientific values, including nested arrays/maps, are retained in full in generator_settings; no recursive field dropping. |
| generation-plan-outputs/1 — outputs | {data_root:Path,record_root:Path,archive_root:Path,generator_input:Path,scenario_run_lookup:Path,perturbation_lookup:Path,series:[{run_id:text,path:Path}],temporary_members:[{run_id:text,path:Path}],date_products:[{role:"sim_dates" or "resampled_dates",path:Path}],diagnostic_root:Path}. All project_root anchored; series is a bijection in rows order, temporary_members lists root rows in that order, date_products is sim_dates then resampled_dates. Paths equal §2 tree derived from selected IDs; distinct outputs cannot alias. No future hashes are invented. |
| series-descriptor/1 | {source_calendar:text,timestep:text,time_label:text,start:text,end:text,spatial_representation_sha256:Digest,variables:[{name:text,units:text,missing_value:null-or-MissingEncoding}]}. Variables sort by name. MissingEncoding is a nonempty map allowing only _FillValue/missing_value; each is Value or {nonfinite:"nan" or "inf" or "-inf"}. Spatial digest is H({crs:null-or-text,spatial_ref:Map<text,Value>,dimensions:Map<text,integer≥0>,coordinates:Map<text,{dimensions:[text],dtype:text,values:Value,attributes:Map<text,Value>}>}); preserve dimension/value order. Physical attribute maps retain every value. |
| simulator/1 | {name:"wflow",revision:Digest}; revision=H({"julia:Wflow":environment.packages["julia:Wflow"]}), using actual immutable dependency revision. |
| model-reference/1 — documents.model_reference | {digest_version:1,model_path:Path,model_toml:Path,digest:Digest,inputs:Map<model-relative-Path,Digest>}. Input hashes are B. Model algorithm is SHA-256 of UTF-8 "cst-model-digest-v1\n" followed by sorted (path + "\n" + digest + "\n") entries. This is neither H(inputs) nor B(reference). model_digest equals verified digest. Relocation may change model_path, never input-relative keys. |
| simulation-settings/1 — documents.settings / identity_projections.settings | {simulation_window:year-window/1}. Current producer has no other scientific setting; resolution_mode/manifest locators belong to collection selection. Newly consumed knobs require profile/version extension. |
| response-request/1 — documents.response_request / identity_projections.response_request | {schema_version:"response-request/1",reader:{name:"wflow-csv",revision:Digest},run_ids:[text],variables:[{variable:text,locations:[text],units:text,calendar:text,timestep:text,time_label:text,start:text,end:text,missing_value:"NaN"}],expected_series:[[run_id,variable,location_id]]}. Unique run_ids sort numerically; variables retain declaration order, locations native output order. expected_series is exact ordered cross-product. Projection equals full request. reader.revision=H([{path,sha256}] in response_series.py,wflow_response_reader.py order), hashes B. Endpoints use predecessor parsed timestamp strings, pinned by canonical vectors. |
| temporal-preparation/1 | {source_calendar:text,prepared_forcing_calendar:"proleptic_gregorian",response_calendar:text,operations:[text],prepared_start:text,prepared_end:text,response_start:text,response_end:text,time_label:"interval_end"}. Ordered operations: optional cftime_to_datetime64 or hydromt_reader_to_datetime64 for noleap, then clip_to_configured_window,refresh_toml_endpoints. Check endpoints/response offset against every native clock. H of whole object is temporal_preparation_sha256. |
| metric-environment/1 | stage-environment/1 plus return_level_estimator:{estimator_id:text,package:"lmoments3",version:text,source_sha256:Map<relative-Path,Digest>}. Source hashes are B; entire environment uses H. |

Generator presence is fixed as well as values. Required keys are all §10.6 keys except generate_weather.plot_dpi/plot_device and write_netcdf.file_suffix/out_dir, which use Maybe<Value>. generate_weather.out_dir is null in embedded evidence and a checked absolute execution path in installed YAML; identity excludes it. generate_weather.seed is the resolved integer; n_cores is null or positive integer. Null precision/clamp values remain actual nulls. The explicitly open scientific argument Value payloads are hashed in full and checked against the pinned upstream argument domain; no native function argument is added by this serialization profile. Missing required arguments, unsupported values and unclassified fields refuse.

Forcing preparation has ancillary=[{id:text,role:"forcing_elevation",file:FileRef,descriptor:AncillaryDescriptor}], sorted by id; forcing_elevation={catalog_key:"elevation",artifact_id:text}; pet_method is resolved text. AncillaryDescriptor={crs:null-or-text,spatial_representation_sha256:Digest,variables:[{name:text,units:null-or-text,dimensions:[text],attributes:Map<text,Value>,missing_value:null-or-MissingEncoding,missing_count:integer≥0}]}, variables sorted by name. Full catalog is FileRef; projected catalog={elevation:{content:{role,sha256,size_bytes},reader:ReaderIdentity}}, using selected ancillary B and parsed retained native catalog.

ReaderIdentity is forcing-reader-identity/1 from §10.7 with exact nested shapes: driver={name:"raster_xarray",options:{chunks:Maybe<Map<dimension,positive-integer>>,lock:Maybe<boolean>,preprocess:Maybe<"harmonise_dims" or "round_latlon">}}; string driver expands with absent options. data_adapter is null or {rename:Map<text,text>,unit_mult:Map<text,number>,unit_add:Map<text,number>}, absent operations empty. metadata={crs:Maybe<text-or-integer>,nodata:Maybe<Value>,units:Maybe<text>}. unit_interpretation is null for elevation, otherwise {revision:text,variables:[{name,units}]} sorted by name. Native reader evidence retains uri/root, processing/category and cst_unit_interpretation.evidence; only those named fields are excluded. Unknown metadata/control keys refuse; physical descriptor attribute maps above remain complete. Current adapters support rename/unit_mult/unit_add only: newly consumed time conversion/preprocessing requires extension, never silent dropping. Projected ancillary entries={role,sha256,size_bytes,descriptor}, in matching id order; artifact_id resolves uniquely. All six §10.7 preparation document keys are required, with exactly these replacements.

Metric nested profiles:

~~~text
ResponseRequirement = {variable,units,timestep_seconds:positive-int,time_label,
 coverage,location_grain,missingness,calendars:[text]}
MetricDeclaration = {name,statistic,grain:"run"|"bundle",
 required_responses:ResponseRequirement,bundle_by:null|text,reference:null|text,
 reference_location:null|text,return_period:null|positive-int,
 blocks_per_return_period:null|number,implementation_revision:Digest,value_validity:text}
MonthReference = {run_ids:[text],reference_location_id:text,month:1..12,
 which:"wet"|"dry",counts:[[run_id,start,end,year_count,month_count]],
 selection_statistic:text,tie_rule:text}
ResolvedReferences = {} | {wet:MonthReference,dry:MonthReference}
RunGroupRow = {run_group_id:padded-decimal-string,grain:"run"|"bundle",run_id:text}
Groups = [{st_id:text-or-empty,run_ids:[text]}]
MetricDefinition = {declarations:[MetricDeclaration],grouping:text,reference:text,
 resolved_references:ResolvedReferences,water_year_anchor:text,
 code_inventory:code-inventory/1,return_level_validation:ReturnLevelValidation}
ReturnLevelValidation = {schema_version:"return-level-validation/1",
 estimator_id:"gf15-lmoments-c/1",policy_id:"gf15-accuracy-8x-v1",
 screening_ratio:1.0,screening_floor:10,
 screening_policy_status:"provisional_operational",benchmark_status:"reviewed_bounded",
 benchmark_record:{path:"return_level_benchmark.json",sha256:Digest},
 tested_domain:{shapes_c:[number],counts:[positive-int],probabilities:[number],
 ratios:[number],relative_qualified_ratios:[number],draws_per_base_cell:positive-int},
 criteria:BenchmarkCriteria,application_scope:"operational_screen_only",
 relative_error_near_zero:"unvalidated",actual_bundle_applicability:"unestablished",
 evidence_use:"post_results_development_rescore",screening_policy_validated:false,
 fit_uncertainty:"point_estimates_only"}
~~~

Unannotated declaration/requirement strings are text. Declarations follow token/registry order; calendars retain declaration order; counts follow numeric run order with nonnegative integer counts. Groups order is empty root then numeric st_id; membership is numeric run order. RunGroupRows preserve predecessor allocation/membership order. Reference tie_rule remains first label in ascending calendar-month order. BenchmarkCriteria is a closed literal equal to criteria in the shipped gf15-benchmark-report/1 asset at inspected revision, B=89905f1889a08177ff9225535a7a590b0081c76b2e6765e31e83390bee412b2c. Its recursive values/key set are fixed by that pin, not extensible. tested_domain equals the six named report fields with original array order. Copied report B must equal benchmark_record.sha256 and that pin; validate embedded source hashes/duplicated criteria. Changing policy requires a reviewed version. This source-asset pin asserts no new benchmark execution. return_level_validation_sha256=H(entire ReturnLevelValidation), never B(report); metric_definition_sha256=H(MetricDefinition). The report B is thus transitively bound and separately checked by FileRef.

metric-request/2 has exactly {schema_version,simulation_id,tokens,declarations,grouping,reference,water_year_anchor,code_inventory,metric_environment,return_level_validation}; types are above, tokens unique ordered text. metric_request_id=H(request). metric-plan/2 has exactly {schema_version,metric_request_id,request,response_inventory:FileRef,response_identity_sha256,resolved_references,run_groups,expected_result_keys,groups,bundle_run_group_ids,metric_definition,metric_definition_sha256,metric_environment_sha256,identity_projection,metric_set_id,targets,plan_sha256}. bundle_run_group_ids=Map<st_id,padded-decimal-string>; expected_result_keys is lexicographically sorted [metric,location,run_group_id] triples; targets={manifest:Path,metric_run_lookup:Path,return_level_benchmark:Path,tables:[{token,path:Path}]} anchored at experiment_root, tables in token order. plan_sha256=H(plan with only plan_sha256 removed). Projected reference equals resolved_references; groups/run_groups equal plan values. No environment sidecar target.

Full response-inventory/2 has exactly {schema_version,simulation_id,collection_id,collection_revision,model_digest,simulator,settings_sha256,response_request:SectionRef,temporal_preparation,temporal_preparation_sha256,artifacts,series,identity_projection,response_identity_sha256,response_inventory_sha256}. Full artifacts=[{run_id,file:FileRef}]; full series has the §10.7 scientific series fields but native_selector uses the three-field evidence form. Scientific artifacts derive FileRef.sha256/size_bytes. Clock/output_declarations have §10.7 keys; timestepsecs is positive integer and output_declarations retains TOML order. Never reorder artifacts after assigning series.artifact. response_request SectionRef permits only /documents/response_request in verified simulation intent.

H always hashes the named whole object/profile or explicit field-removal projection; B always hashes actual bytes. Embedded document_digests use H even when former sidecars used B. FileRef/source/generated/provider/native/benchmark hashes use B. No unspecified field is omitted during H. Archive loaded_config, advanced_settings and overrides are explicit complete Value maps; configuration_projection retains its recorded version-2 type-tagged algorithm, not C. Null/absence rules apply before hashing; do not normalize 1.0 to 1 or reorder scientific lists. Independent conformance vectors cover every profile, H/B preimage and null/absence branch, plus unknown-key refusal. Reproduction must not require predecessor readers.


#### Remaining identity and presence rules

The enclosing versions select all §10.2.1 profile IDs. A collection's document_digests has exactly generation_config,source_inventory,provider_code,environment; its identity_digests has those same four keys, with values defined in §10.7. Simulation document_digests has exactly model_reference,settings,environment,simulator_adapter_code,response_request,preparation; identity_digests has exactly settings,response_request,preparation. collection.resolution_mode permits only project-generation or explicit-manifest; run_ids equals verified request order. No document hash is implicitly substituted for its scientific projection.

Native reader evidence is the parsed finite JSON value of the retained HydroMT entry; the allowed control keys are data_type,driver,data_adapter,metadata,uri,root. Native optional presence is preserved in evidence and normalized with the explicit Maybe/null/empty-map rules only in ReaderIdentity. Its metadata permits crs,nodata,units,processing,category,cst_unit_interpretation; the last has exactly revision,evidence,variables (ordered [name,units] pairs). Only the stated descriptive/evidence keys are dropped from identity. This is an explicitly bounded evidence payload, not an arbitrary executable map. Extra keys require an explicit ruling and profile/version amendment. Ancillary attributes use the separately declared complete data maps.

scenario_semantics_sha256=H of rows with only run_id removed, retaining exact keys evaluate,type,rlz,st_id and row order. Perturbation lookup typed rows have exactly {st_id:padded-decimal-string,month:integer 1..12,temp_change:number,precip_change:number,precip_variance_change:number}, in numeric st_id then Jan→Dec order; these are the exact producer CSV headers. Preserve temperature deltas and precipitation percentage-change values; reconstruct provider multipliers as 1 + change/100 at the existing seam. Never reinterpret variance as a mean factor. The identity projection is this declared semantic form; the final lookup FileRef also checks original bytes with B. diagnostics sort by FileRef.path; provider_products order is sim_dates,resampled_dates,weather_generation_input. No optional retained scientific product may be omitted.

### 10.3 Source capture, publication transaction and rerun

Capture each project/workflow YAML, custom template and custom catalog into bytes once before parsing; parse that exact buffer. For WF0–2 this begins in scripts/run_workflow.py before Snakemake starts or receives --configfile. The launcher constructs a capture session, stages immutable copies and passes an immutable generated execution config to Snakemake, plus the validated capture-session reference. The generated config is derived only from the captured mapping; it is not an archived original. The source map retains each original resolved identity and original directory so workflow config_path still resolves against the original project file directory before mapping to captured files; other path keys preserve run-directory semantics. R config_path forwarding targets the corresponding captured execution config and uses that same resolver, never a live original. Rules creating new-schema products require this launch/capture context and refuse raw Snakemake emission before any scientific or archive write. Raw parse/dry-run diagnostics are allowed and are not an exact-capture execution. P1/P2 inject a comment-only edit between launcher capture and Snakemake parsing, and another before rule/R use: executed settings and archived original bytes must come from the captured buffers, or execution must refuse. Repeated loads of one resolved path in a launch use the same buffer. The actual downstream rule/R inputs must derive from this captured mapping or an immutable staged file of those bytes; no original-path reread after capture. Record actual overrides and the full loaded mapping. Reject a dependency that was loaded outside capture and cannot be proven to match the used bytes. Do not load unrelated workflow files. Built-in unmodified files may use exact Git revision/blob recovery; custom or dirty files must be copied.

Source placement preserves the original basename. For one filesystem volume, choose the common parent of loaded sources and retain relative paths below sources/. If that common parent is a drive root, or sources span volumes/shares, assign deterministic source-group IDs and use sources/<group-id>/<relative-path-from-group-root>; record every original-to-archive mapping. Collision handling is based on resolved canonical source identity, with case-insensitive collision refusal where applicable. Never flatten two same-basename files. A source reference that points outside the captured set remains an explicit external dependency.

Publication applies to the whole archive directory, including record and sources. It uses a staging sibling on the same filesystem and an archive-specific OS lock shared by all supported readers; writers take exclusive ownership. The broader project execution lock in §10.5 already serializes writers. There is one archive-transaction/1 journal under config/runs/_engine/archive-transactions/<owner-key>.json:

~~~text
{schema_version, transaction_id, owner, invocation_id,
 target, staged, previous, old_record_sha256:null|Digest,
 new_record_sha256:Digest, archive_id:Digest,
 state: enum(prepared,old_detached,new_installed,committed,rolled_back,unpublished)}
~~~

All paths are confined project-relative directory paths. Stage exact bytes, fsync written files, verify every entry and run record, then atomically persist the prepared journal before any live rename. Under the exclusive archive lock rename existing target to previous, persist old_detached; rename staged to target, persist new_installed; validate target and persist committed. Release the lock only after the final validation. No claim is made that two directory renames are one atomic operation. Readers use the same lock, recover/refuse an unfinished transaction, then validate one complete generation; they never read through a publication gap. A direct filesystem observer may see a temporarily absent target, never a sanctioned mixed archive. Unsupported network filesystem lock/rename behavior is refused.

Recovery, under the exclusive lock, examines bytes and journal rather than trusting the last recorded state:

| Observed state after interruption | Recovery |
|---|---|
| Target matches old, complete staged matches new | Validate old as current, persist terminal rolled_back; retain staged evidence and record abandonment in invocation diagnostics. |
| Target absent, previous matches old | Restore previous as target, validate old, then persist terminal rolled_back; preserve staging for diagnosis. |
| Target matches new and every source validates | Complete commit, even if journal lags the rename. |
| No previous target (first publication), complete staged, target absent | Expose no archive; persist terminal unpublished. A new invocation may publish a newly verified capture. |
| Target/previous/staged contradict recorded digests | Refuse, preserve all candidates and require explicit repair; never pick newest mtime. |

The terminal journal update is atomic and durable under the archive lock. committed requires target B=new_record_sha256 and complete sources; rolled_back requires target B=old_record_sha256 and complete old sources; unpublished requires old_record_sha256=null and target absent. A lagging journal after restoration can be recovered again from those same bytes and reaches the same terminal result. A second reader or recovery pass verifies this terminal predicate and does not treat it as unfinished work. If a terminal predicate fails, refuse corruption.

Before a new writer replaces the per-owner journal, it verifies the terminal predicate and moves that terminal journal atomically to archive-transactions/completed/<transaction-id>.json (exclusive destination). Staged/previous diagnostic paths are unique to transaction_id, stay owned by that completed journal and must never be reused or deleted by the next writer. A crash during this handoff leaves either the verified current terminal journal or its completed copy; absence of a current journal admits a new transaction after normal target validation. An unfinished or contradictory current journal never admits a writer. committed cleanup may remove redundant staging/previous only after validation and no reader; rolled_back/unpublished diagnostic cleanup requires a separately explicit retention decision. Test interruption→recovery→second reader→second recovery→new publication, preserving diagnostic bytes throughout.

Recovery repairs archive publication only, not a scientific run. Staging/previous directories and journals are bookkeeping, absent from the normal completed-tree sketch; cleanup occurs only after validated commit and no held reader, and does not become configuration history. Failed cleanup is reported and is harmless to correctness. Ready WF3/WF4 creator archives are never replaced. WF0–2 replacement intentionally makes older invocation references historical checksums, with explicit unavailable status if the latest archive no longer matches.

Rerun is a supported launcher operation using the record and archived mappings, not manual edits to original YAML. It selects only the owning workflow, applies recorded overrides, resolves workflow config_path against the original project-source directory then maps that resolved identity into the archive. Other paths retain the recorded run-directory semantics. Custom catalog/template dependencies resolve through the same mapping. Exact copied YAML remains byte-identical even when its original absolute paths cannot be used.

Before emitting a rerun overlay, copy the predecessor run_record.yml and its captured source archive byte-for-byte into the new archive staging directory at predecessor/<predecessor-archive-id>/. Preserve the predecessor archive's own relative source hierarchy; verify its run record and every required captured source against the predecessor record before installation. Copy an already nested predecessor evidence subtree as well, so its checked references remain closed; no symbolic links to the old project. This retained evidence is immutable and is not an execution config. In the new overlay, source_record is a FileRef with path_base:"record_directory" and path "predecessor/<predecessor-archive-id>/run_record.yml", anchored at the new run record. Its B hash equals the predecessor record's original B. Verification of that retained record anchors its own source mappings at its copied directory; its old product/output locators remain historical evidence, not dependencies on project A.

A rerun emits the closed resolver-overlay/1 defined in §10.2.1; it records this overlay under rerun.adjustments in the new archive. The new source map maps the predecessor's original identities to the captured copies in the new archive; every loaded original source is also represented by the new source_files entries. This selects retained predecessor evidence rather than an unconfined external FileRef. Test rerun A→fresh B, make A unavailable, relocate whole B→C, and verify source_record and source resolution without A. External scientific datasets still follow the explicit mapping rule below; the archive copy does not promise full dataset export. Project-contained paths relocate by preserved relative path. External files require an explicit new locator and expected original byte identity; missing/changed dependencies refuse reproducibility. Unmodified Git dependencies are materialized at the recorded blob when needed. No automatic search by basename and no silent fallback to the original absolute source path.

Generated execution YAML/TOML with absolute output paths is regenerated into the new fresh target from captured semantics and explicit relocation. The sealed predecessor's bytes stay unchanged. Path adjustments change execution evidence, not seed/scientific identity. A rerun that deliberately changes semantic settings or input bytes is a new scientific request and must say so. Independent movement of only a collection or only one metric-set sibling is unsupported; ordinary relocation preserves the whole project hierarchy.

### 10.4 Launch history and archive lifetime

Supported complete-history entry points are scripts/run_workflow.py (new, WF0–2), scripts/generate_scenarios.py (new, WF3), scripts/simulate_system.py and scripts/run_workflows.py. The latter three delegate to the same launcher/history library; there is one WF3 planner. Complete-history calls supply --project-dir before loading scientific configuration. The supplied root must equal the composed project root once validated; disagreement fails before work. Existing config-only syntax may remain a convenience, but if root discovery fails before a writable root is known its coverage is explicitly reduced and stderr/exit status are the only evidence. No project file can be promised before its directory is known or writable.

Start invocation/1 once argument syntax and journal location are known, before configuration validation, environment checks or subprocess launch. Root-level permission and argument-parser failures are inherently pre-record failures and are documented/tested. Dry-run writes invocation history only; it never creates source/scientific products, creator archives, receipts or pointers. work_performed is no for dry_run, yes only after a reported job actually executes, no for proven up-to-date, otherwise unknown. It excludes logging itself.

The §5.2 envelope additionally has requested_workflows:[], launch_failures:[], error:null|{phase,type,message}, and configuration.archive_state: enum(unavailable,invocation_local,creator,latest,historical_unavailable). All keys exist; nullable refs use null. Parent launch_failures items are {workflow,attempted_child_id,phase,error,exit_code}; a launch failure with no child record adds no fabricated child to children. Child items are {invocation_id,workflow,record:FileRef}; this reference is installed only after the child exists, then refreshed to final B when observed. During execution the parent may retain a start-record hash; readers report stale/live rather than falsely validating it against a final rewrite. A child writes only its own file. The parent records overall outcome and child linkage; it never copies scientific readiness into status.

Every file starts running with exit_code:null and ended_at_utc:null, then one atomic final update records succeeded/failed and observed exit status. Forced termination leaves running with unknown outcome. A parent killed before final linkage can be reconstructed by scanning child parent_invocation_id; this is discovery, not retroactive success attribution. No second journal is authoritative.

From P2, new-schema WF0–2 production output requires scripts/run_workflow.py or the common capture path used by scripts/run_workflows.py. Raw WF0–2 may parse/dry-run for diagnostics with reduced history coverage, but cannot emit new-schema archives or products; a hook after Snakemake parsing cannot establish exact original byte capture. P2 introduces the capture launcher and minimum ownership needed for it; P3 adds invocation/1 and parent/child history, without postponing capture until P3.

P3/P4 preserve a runnable, explicitly legacy WF3 route: run_workflows.py holds project ownership and launches the predecessor generate_scenarios.smk checkpoint path in a child under that ownership. The invocation envelope adds contract_mode: enum(new_schema,legacy_wf3_interim,legacy_wf4_interim); the interim WF3 child uses legacy_wf3_interim, captures attempt evidence in the invocation-local archive, records the actual command/outcome, and emits no generation-plan/1 or generation-initialization/2 claims. Legacy creator artifacts stay in the predecessor schema; its old snapshots do not masquerade as run-record/2. P4 is additive only. P3/P4 raw legacy WF3 execution is possible only through the ownership-aware adapter; unattended raw mutation refuses. At P5 the wrapper and WF3 producer/consumers switch together to scripts/generate_scenarios.py, new_schema, and the required plan/receipt; legacy WF3 production routes are removed. Raw WF3 source preparation may be dry-run independently, while all generation execution from P5 requires the validated pinned plan and owned launcher session. Raw WF4 always requires its launcher; the interim WF4 child uses legacy_wf4_interim until P6 and refuses new WF3 artifacts during P5. These phase-local routes are staging mechanics, not compatibility readers in the final contract.

Metrics-only, failed-after-load and equivalent-request attempts need their own exact configuration evidence. Use config/runs/_engine/invocations/<invocation-id>/config/{run_record.yml,sources/}. The flat <invocation-id>.json remains the history record. Successful WF3/WF4 creation promotes the captured archive into its artifact and the invocation refers there; reuse and metrics-only keep the invocation-local archive and separately reference the immutable creator archive. Failure before successful parsing records captured source hashes and error, but does not invent loaded_config or a valid run-record. WF0–2 successful latest-archive adoption drops any redundant staging archive; older input recovery is not promised.

### 10.5 Static plan, receipt, pointer and workspace exclusion

The supported local execution policy serializes all writing launches per resolved project root, including source preparation, WF0 shared sources, WF1, WF2, WF3 and WF4. The parent holds one OS lock and hands authenticated ownership to sequential children; children never reacquire it as unrelated writers. Another invocation records refusal rather than writing. Same request in another working directory is still the same project namespace. Concurrent distinct project roots are supported. Project lock ownership is an open OS handle scoped to the process tree; a metadata file with a PID is not proof of ownership. No automatic takeover based on timestamps or stale PID files. P3/P5 must test child lifetime after launcher death; if ownership cannot be retained until descendants finish on a platform, concurrent execution there is unsupported and must refuse. This is deliberately simpler than per-collection leases and does not claim distributed fencing.

Cold launcher execute: acquire ownership → source-only DAG → validate source inventory → construct immutable plan → initialize selected create/reuse action → construct ordinary static generation DAG → verify/publish. Source-only work may produce region, historical climate, basin cells and perturbation lookup, but must not require WF4-only elevation. Cold CHIRPS lapse correction remains required source preparation (§7), without importing a WF4 resolver. A source producer that currently emits an optional WF4 sidecar must allow WF3 to stop after its own required products. No source-only rule may import a required WF4 resolver. Cold dry-run reports the source DAG and “generation plan unavailable: required source bytes missing”; it reports no fabricated exact full-run count and returns a distinct non-success planning result. Prepared dry-run may construct the plan in memory and show the selected generation DAG without publishing it.

Closed request and plan keys:

~~~text
generation-request/2 = {schema_version, settings, provider_code, source,
                       water_year_start, template}
generation_request_id = H(request)
scenario-request/2 = {schema_version, generation_request_id,
                     plan_path, path_base:"request_directory", plan_sha256}
generation-plan/1 = {schema_version, canonicalization_id:"collection-canon/1",
 generation_request_id, request, request_sha256, collection_id, intent,
 intent_sha256, documents, candidate_intent, candidate_intent_sha256,
 candidate_identity_digests, creator_archive:null|FileRef,
 source_inventory_sha256, decision,
 collection_revision, rows, outputs, path_base:"project_root", counts}
generation-initialization/2 = {schema_version, invocation_id,
 generation_request_id, plan_sha256, collection_id, intent_sha256,
 candidate_intent_sha256, creator_archive:FileRef,
 decision, collection_revision, workspace_path, claim_token}
~~~

request retains resolved configuration, including locator differences, so multiple requests can identify the same collection. request_sha256 equals generation_request_id. Plan documents equal the four selected intent documents; readers compare full equality. candidate_intent is the complete intent from this request capture, candidate_intent_sha256=H(candidate_intent), and candidate_identity_digests equals its recomputed scientific digests. For create, intent=candidate_intent by full equality and creator_archive=null in the plan; the receipt binds the installed creator archive. For reuse_ready, validate the existing ready marker, full creator intent, archive and product revision, then set plan.intent/documents/intent_sha256/creator_archive to those verified creator values. Compare current candidate and creator scientific projections, identity digests, scenario_spec, scenario semantics, provider and ID-capacity choices exactly and independently recompute equal collection_id. Do not require full candidate/creator evidence equality: comment, locator and explicit-versus-auto differences remain current attempt evidence. Require full equality of plan.intent/documents with the stored creator intent/documents. The receipt binds intent_sha256 to the creator and candidate_intent_sha256 to the current attempt. Reuse revalidates that exact revision, writes only invocation-local candidate evidence and its receipt, and installs no archive, intent, generated YAML or products in the creator collection. Candidate generated_inputs never claims creator execution as a new execution. Test two evidence-distinct equivalent requests and verify truthful creator/candidate attribution and unchanged creator bytes. rows are ordered typed scenario lookup rows: {run_id:padded-decimal-string,evaluate:boolean,type:"stochastic",rlz:padded-decimal-string,st_id:padded-decimal-string-or-empty}; st_id empty identifies each root, with all rows evaluated under this binding. outputs is a closed map {data_root,record_root,archive_root,generator_input,scenario_run_lookup,perturbation_lookup,series,temporary_members,date_products,diagnostic_root}; the exact nested entries/order are in §10.2.1. counts is {run_count,root_count,perturbed_count}; these are potential work counts, not scheduled Snakemake jobs. Actual job counts come from the selected DAG/targets/flags.

Plan bytes are C(plan), plan_sha256 is B of those bytes, and filename is its full hash plus .json. The plan contains neither its own hash nor invocation/time/claim fields. Intent hash is H(intent). source_inventory_sha256 is H of the full current candidate source inventory, including original locator evidence and pinned scientific byte references; it is not the collection's semantic source digest. For create, collection_revision is null; for reuse_ready it is the verified published revision. Every declared captured/pinned file, including unchanged-mtime metadata, is checked against the pin before initialization. Copy historical_climate and basin_cells to real immutable project-owned snapshots under data/climate/generation_inputs/<full-byte-sha256>/<original-basename>, using a same-filesystem temporary file, byte hash/size verification and exclusive publication. No hardlink or symlink to the live original is allowed. Existing snapshots must verify and cannot be overwritten. Hash and describe the copied bytes, verify them against the declared source digest, and freeze those paths in the plan and provider execution YAML. R/Python read those snapshots, never the original external paths. Keep snapshots for rerun; no automatic garbage collection is introduced.

Snapshot directories belong to the launcher protocol and are read-only to ordinary source-updater processes; hold read-only snapshot access through consumption, recheck before provider read and at publication, and refuse readiness after a mismatch. The project OS lock excludes cooperating project launches only; it does not prevent external source edits. Those edits cannot redirect a copied input. Arbitrary privileged tampering with protected process inputs is outside this filesystem trust model. Inject original source replacement after initialization but before provider read, including unchanged mtime: consume the pinned prior bytes or refuse. Inject pinned-copy mutation: refuse with no ready marker. Changed originals may define a later candidate; this execution never refreshes its plan or snapshots in place.

Publish plans exclusively; matching bytes at an existing path are reusable, any mismatch is corruption. Replace request.json atomically only after the plan exists. Execution receives the exact plan path and digest as arguments and never reopens the pointer to decide work. The pointer serves only request-to-collection discovery, including WF4 default selection; discovery validates pointer→plan→ready marker and full identities. A pointer to an incomplete create plan is not a ready collection.

Under project ownership, create claims both engine record and data root using exclusive creation and full-ID checks. For create, initialization next renders and exclusively installs exact weather_generation_input.yml from the frozen plan, with pinned scientific-input paths and the selected output root. Verify its B hash and the semantic/argument/output equivalence below, finalize generated_inputs from those bytes, publish the complete creator archive and intent, then verify all three before emitting the receipt with its creator_archive FileRef. The generation DAG consumes the installed YAML; the old prepare_weathergen_config rule cannot rerender it afterwards. Failure after YAML installation or during archive publication must leave no receipt referencing unfinished evidence. Reuse follows the read-only branch above, without creator installation. claim_token is a random local invocation token, checked together with the held OS ownership; it is not an ordered fencing token. Receipt workspace_path equals the selected collection's provider subtree. Shared provider work is safe here because different launchers cannot write the project concurrently. Forced execution against reuse_ready has validation/no-op targets only; retained ready data are not outputs of a rule that could delete them during failure cleanup.

If a create plan sees a ready or partial collection that did not exist when planned, refuse and require a new planning invocation; never silently reinterpret create as reuse. If initialization fails halfway, retain partial evidence and refuse scientific restart into that partial namespace; use a fresh project or explicitly authorized repair. Existing ready artifacts are immutable under force/rerun flags. No resume, lease, replan-within-job, or automatic partial cleanup is introduced. Request plans/receipts remain retained by default; cleanup is outside this migration.

#### Installed provider-input equivalence (normative)

The exact installed weather_generation_input.yml must agree semantically with the selected create plan before any R provider call and again before collection publication. A B match alone is insufficient. Decode the same immutable bytes R will read with duplicate-key rejection; reject YAML tags/aliases/nonfinite values and ambiguous scalar coercions. Python and R must produce the same typed argument projection, including booleans, integer seeds, ordered arrays and absent-versus-null arguments. P5 fixtures compare both decoders. Do not rewrite the installed file after validation.

Define ProviderInputIdentity={schema_version:"provider-input-identity/1",generation_config:generation-config-identity/2,sources:[{role,sha256,size_bytes}],scenario_semantics_sha256,perturbation_rows_sha256}. Build generation_config from the decoded installed YAML's included fields and resolved seed, plus the frozen scenario specification and actual selected perturbation rows; require equality to the intent's generation_config projection. The injected start_year/n_years/n_realizations/year_start_month, spell factors and transient flags must match the plan and its perturbation specification; no independent defaults are resolved in R. perturbation_rows_sha256=H of typed rows in the frozen monthly lookup order; verify each per-design-point input against those rows.

Source paths are positional arguments in this provider binding, not native YAML fields. Build sources from the actual invocation's historical_climate/template input and basin_cells arguments, resolving to the plan's immutable snapshots and recomputing B/size. Perturbation calls likewise bind the verified root member, installed YAML, selected monthly factors, seed, and output member to the frozen row; a valid YAML cannot excuse a changed CLI source or member association. Require full equality of this observed ProviderInputIdentity with the object derived independently from plan/intent/source pins before each provider read and at publication. No CST-specific keys are inserted into weathergenr YAML.

Execution projection is separate: normalize the installed YAML's excluded arguments to generator-arguments/1, retaining Maybe presence; require equality to the frozen candidate's declared execution choices for create. Validate out_dir, prefix/suffix and direct output arguments against outputs and row/member mappings using resolved confined paths. Every root, temporary member, retained series/date product and diagnostic directory must belong to the selected collection; reject redirection, collisions and wrong member naming even if scientific identity is unchanged. Source bindings use verified bytes, never a pathname-only comparison. Reuse validates the creator's retained YAML against the creator intent/plan, never installs current-candidate execution settings over it.

Keep the observed YAML B in generated_inputs and require it to match the archive and final provider_products reference. Revalidation checks both B and semantic equality: initialization before receipt, immediately before provider consumption, and immediately before final publication. Mutation after an earlier check causes refusal/no ready marker; execution cannot repair or replan the file. Inject wrong seed, wrong source snapshot/CLI argument, altered included setting, changed month/realization count, perturbed lookup row and redirected output path. Even when all affected evidence B hashes are made internally consistent, semantic disagreement must refuse. This tests renderer/mapping defects independently of checksum integrity.

### 10.6 WF3-only seed material and module contract

The selected auto-seed equation is unchanged:

~~~text
material_digest = H(material_v2)
resolved_seed = integer(material_digest, base=16) mod (2^31 - 1)
~~~

Zero remains a possible result. Do not add one, truncate the digest, or substitute a language-native hash. Explicit seed uses the existing resolve_seed validation. Its request value and resolved value remain recorded. seed_resolution_id is H({seed_request,resolved_seed,projection,projection_sha256}) before adding that ID.

material_v2 has exactly these fields:

~~~text
{schema_version:"generation-seed-material/2", scenario_type:"stochastic",
 n_realizations, simulation_window:{start,end}, climate_perturbations,
 water_year_start, provider_revision,
 source_inventory_sha256, generator_settings}
~~~

source_inventory_sha256 = H of an array sorted by role containing exactly {role,sha256,size_bytes} for historical_climate and basin_cells. These are the pinned extracted bytes actually read by R (§10.5). CHIRPS source-preparation elevation may change historical_climate bytes; no invariance is claimed for that scientific source change. No separate WF4 elevation, forcing catalog, source location, raw template/catalog text, model setting, metric setting, invocation, output path, ID capacity or projection product enters it. climate_perturbations retains the complete validated WF3 perturbation specification; the effective monthly lookup is validated against it. generator_settings uses the existing closed include/exclude classification in generation_plan.py at the inspected revision, copied into a WF3-only module without changing its scientific field choices. Unknown top-level or nested settings fail until explicitly classified.

Included generator fields by section: generate_weather = vars,warm_var,warm_signif,warm_pool_size,warm_filter_bounds,relax_order,annual_knn_n,wet_q,extreme_q,start_year,n_years,n_realizations,year_start_month,dry_spell_factor,wet_spell_factor; apply_climate_perturbations = compute_pet,pet_method,qm_fit_method,scale_var_with_mean,enforce_target_mean,precip_intensity_threshold,precip_occurrence_transient,exaggerate_extremes,extreme_prob_threshold,extreme_k,precip_cap_mm_day,precip_floor_mm_day,precip_cap_quantile,diagnostic; write_netcdf = calendar,spatial_ref,signif_digits; temp and precip = transient_change; run_weather_generator has no included fields. The exhaustive excluded sets and their conditional acceptance are fixed in the matrix below; any observed scientific effect requires promotion or refusal before production. diagnostic must remain false. WF3 perturbation PET remains included because it affects generated values; WF4 PET/corrections are separately excluded. The two meanings must not be conflated.

The new module boundary is mandatory, not merely an inventory filter:

- generation_plan.py becomes WF3-only planning. Move resolve_preparation_payloads, elevation/catalog generation and every WF4 preparation call to a WF4-owned preparation module, with P6 as production caller.
- Split scenario_provider.py's metric_groups into a WF4 analysis/grouping module. Keep generator execution, row enumeration and publication on the WF3 side.
- Extract any mixed shared helpers reached by the generator inventory into pure modules containing only WF3 or genuinely common semantic primitives. The generator may import shared primitives; those modules must not import WF4. Logging/process helpers may be neutral. A helper edited to change WF4-only behavior belongs outside the inventoried closure.
- Do not hash the whole repository, whole environment lock, all Snakefiles, WF4 package inventory, or arbitrary AST fragments to repair the boundary. A whole inventoried generator-file edit may legitimately change the auto seed, including a source-code comment; user config comments are a separate byte/semantic distinction.

The declared provider-code root set is generation_plan.py, scenario_provider.py, prepare_weathergen_config.py, prepare_cst_parameters.py, and the four R files generate_weather.R, impose_climate_change.R, global.R, read_member_grid.R under blueearth_cst/weathergen/. Inventory the sorted unique repository-relative path/byte-SHA pairs for those roots and their complete static Python-import closure, including package initializers; enumerate R source/include dependencies explicitly. Extracted helper modules enter through that closure. prepare_climate_data_catalog.py and new WF4 modules are forbidden members, including indirect imports. Dynamic repository code loading not declared in this closure is refused. provider_revision = H(the resulting array). P4 must emit and inspect the concrete closure manifest before switching P5; transitive contamination is a failed P4 gate.

Collection semantic dependency projection is also WF3-only. Raw catalog/template bytes and locators remain in the full source evidence and creator archive but are not hashed into collection_id. Resolve every scientifically consumed WF3 catalog value into the closed interpretation object {revision,variables:[{name,units}],calendar,time_label}; sort variables by name, take the calendar from checked generated/source conventions and preserve the provider interval_end time label. Keep UnitInterpretation.evidence in full evidence, but use its resolved revision and physical variables in scientific identity. No arbitrary catalog metadata enters that object. Unclassified consumed fields refuse. WF4 elevation entries in the same catalog do not enter this object. Resolved generator settings replace raw template text in scientific identity.

Thus “catalog-only change” is not automatically harmless: comment/locator-only changes leave identity fixed if resolved bytes/settings match; changed interpreted units, calendar, generator settings or source bytes change the appropriate scientific digest. Source-preparation code changes can change prepared bytes; a no-change output preserves the generator's content dependency. Identity-bearing WF3 generator code changes can change auto seeds even when the refactor is mathematically equivalent. Numeric v1 auto-seed parity is explicitly not a gate.

#### Excluded-field acceptance matrix (normative)

Exclusion is a testable claim. P4 fixes the matrix below; P5 executes it with the actual pinned Python/R/provider environment and fixed source snapshots; P7 integrates only model-validator's returned acceptance. Use fresh isolated roots, the same explicit seed (123 reference where applicable), at least two realizations and multiple perturbation points including a distinct zero-change point. Run both base and changed arms; verify intended changed arguments actually reach the provider. Repeat parallel arms to expose schedule-sensitive RNG. No reuse/no-op may stand in for execution. New auto-seed material and collection_id must remain equal for an admitted excluded-only mutation; scientific fields/seed sensitivity are separate tests.

The scientific comparator requires exact decoded values (zero tolerance), coordinates and ordering, dimensions, masks, units/calendars, member-to-array associations, ordered scenario rows/reconstructed ancestry, and complete sim_dates/resampled_dates selections. Compare all generated variables and members, including temporary roots before cleanup. Decoded equality does not permit sorting away swapped members/dates. Documented container encoding bytes and terminal logs/figures may differ; retained series byte changes legitimately change collection_revision while collection_id remains fixed.

| Excluded field(s) — each is an individual case unless interaction specified | Mutations and required evidence |
|---|---|
| generate_weather.parallel; generate_weather.n_cores | false→true; true with 1, 2 and the fixture's supported maximum workers; null automatic core choice versus explicit counts; repeat each parallel combination. Also change n_cores with parallel=false to prove its claimed inactivity. All scientific outputs/date selections must be identical, not merely distributionally similar. Record actual worker count/runtime. |
| run_weather_generator.eval_max_grids | Two valid caps below/above fixture cell count. Generated series/date selections identical; report diagnostic coverage changes explicitly. |
| run_weather_generator.log_messages; generate_weather.verbose; apply_climate_perturbations.verbose; write_netcdf.verbose | Toggle each independently; scientific equality required. Account for newly emitted terminal logs without treating them as scientific products. |
| generate_weather.save_plots; generate_weather.plot_dpi; generate_weather.plot_device | Toggle plots, vary DPI, and compare omitted versus supported explicit device/DPI values. Ensure the plotting branch actually executes; test options jointly with save_plots=true. Scientific equality required, including later RNG/date selections. |
| write_netcdf.compression | At least two supported levels including uncompressed. Exact decoded equality and member/date associations; document permitted container-byte/size differences. No relaxation for rounding: signif_digits remains included. |
| generate_weather.out_dir; write_netcdf.out_dir; write_netcdf.file_prefix; write_netcdf.file_suffix | Relocate output root and vary supported naming choices through the approved row mapping; test absent/present branches where allowed. Reconstruct identical members without sorting away association errors. Provider-overridden arguments must either be refused before execution or proven not forwarded; mere presumed inactivity is insufficient. Output-path validation remains mandatory. |
| generate_weather.seed | This is excluded only from generator_settings to avoid duplicate/self-seed material; resolved_seed is explicitly included in generation_config identity. Compare auto versus explicit requests resolving to the same seed for equality; changing the resolved seed must change generation_config identity. Do not demand identity invariance for different seeds. |
| workflow enabled; run_group_id_capacity; seed request; template/catalog locators, comments and nested unit evidence | enabled=false performs no generation and cannot publish readiness (admission case, not numerical evidence). Capacity is excluded only from seed, explicitly included in collection_id: compare semantic member associations after stated ID mapping and expect changed collection_id. Same resolved seed across request spelling is invariant. Comment/locator/evidence-only mutations with identical parsed settings and verified source bytes must preserve decoded outputs and scientific identity. |
| original external source locator; WF4-only elevation/settings/code | Change locator while pinned bytes stay fixed; mutate WF4-only inputs/code outside WF3 closure. Require decoded equality and seed-material/collection identity invariance. CHIRPS source-preparation elevation is a sensitivity/refusal case, not an excluded WF4-only case. |

The exact excluded generator set is: run_weather_generator={eval_max_grids,log_messages}; generate_weather={parallel,n_cores,verbose,save_plots,plot_dpi,plot_device,seed,out_dir}; apply_climate_perturbations={verbose}; write_netcdf={compression,verbose,file_prefix,file_suffix,out_dir}; temp/precip={}. Every key has a row above. Record unsupported values/branches and refused cases explicitly; a skipped or unavailable mutation is unverified, never a pass. Run the interactions named above; any newly discovered interaction that changes scientific outputs is a failure even if each individual arm passed.

If an excluded field changes any decoded scientific content, promote it into generator_settings and therefore both seed-material and collection generation_config projections, including necessary interacting settings, before P5 new-schema production. Alternatively refuse that execution choice under this binding. A promotion is a material P0 contract amendment: update the closed include/exclude lists, version/conformance vectors, identity examples and evidence ledger and return it to design acceptance before production. Do not hide the difference with tolerance, seed compensation, normalization of members, or upstream patches. Unproven execution/encoding exclusions cannot admit production; the matrix is an acceptance gate, not a report-only test.

### 10.7 Collection, simulation and metric identity contracts

A collection intent has exactly the §8.1 fields, with schema_version:"scenario-collection-intent/2", plus identity_projections and identity_digests. documents has exactly generation_config,source_inventory,provider_code,environment. document_digests has the same keys. provider is {name:"weathergenr",revision:Digest}. scenario_type is stochastic for this binding. run_group_id_width is the decimal width of run_group_id_capacity. identity_projections contains generation_config and source_inventory; identity_digests contains their H values plus H(provider_code) and H(environment).

generation_config projection = {schema_version:"generation-config-identity/2", resolved_seed, generator_settings, climate_perturbations, simulation_window, n_realizations, water_year_start}. It excludes seed_request, seed-resolution provenance, presentation/parallel/output settings and paths; explicit versus auto with identical resolved scientific inputs can select one collection. source_inventory projection = {schema_version:"generation-sources-identity/2", sources:[{role,sha256,size_bytes} for historical_climate and basin_cells sorted by role], interpretation:{revision,variables:[{name,units}],calendar,time_label}}. generation environment is the actual WF3 Python/R dependency closure, with runtime versions and installed dependency-record digests; source-only HydroMT and WF4-only packages do not enter it unless actually executed by the generation binding.

~~~text
collection_id = H({
 schema_version:"scenario-collection-identity/2", scenario_spec,
 scenario_semantics_sha256,
 provider_name_and_revision:provider, run_group_id_capacity,
 generation_config_sha256:identity_digests.generation_config,
 source_inventory_sha256:identity_digests.source_inventory,
 provider_code_sha256:identity_digests.provider_code,
 environment_sha256:identity_digests.environment})
~~~

The final scenario-collection/2 marker has exactly {schema_version,canonicalization_id,status:"ready",collection_id,collection_revision,data_root,intent,archive,scenario_run_lookup,perturbation_lookup,series,provider_products,diagnostics}. data_root is project-relative scenarios/<12-id>; intent/archive/lookups/products are FileRefs. series is ordered {run_id,file:FileRef,descriptor} entries; provider_products is ordered {role,file:FileRef} for the retained date CSVs and generated input YAML; diagnostics is ordered FileRefs, possibly empty. No collection preparation field exists.

collection_revision = H({schema_version:"collection-revision/2",collection_id,scenario_semantics_sha256,scenario_run_lookup_sha256,perturbation_lookup_sha256,series:[{run_id,sha256,size_bytes,descriptor}],date_products:[{role,sha256,size_bytes}]}). Ordering follows scenario rows, then fixed sim_dates,resampled_dates role order. Exact intent/archive/generated YAML hashes are validated by the marker but excluded from this scientific produced-byte revision; otherwise absolute source/output locations would leak back into downstream identity. Diagnostic images are byte-accounted terminal evidence and excluded from scientific revision. Tampered intent/evidence still fails marker validation. Same semantic collection reused through another request preserves the original intent and archive without rewriting them.

simulation-intent/1 has exactly {schema_version,canonicalization_id,simulation_id,experiment_name,collection,simulator,documents,document_digests,identity_projections,identity_digests}. collection = {resolution_mode,manifest:FileRef,collection_id,collection_revision,run_ids}; documents = {model_reference,settings,environment,simulator_adapter_code,response_request,preparation}; all six use the exact versioned profiles in §10.2.1; preparation is WF4-owned. Each has H in document_digests. identity_projections = {settings,response_request,preparation}; identity_digests records their H. settings and response_request use the exact §10.2.1 profiles, without additional omissions. Closed classifiers refuse newly consumed fields. Model identity retains the existing model_digest algorithm and per-input hashes.

~~~text
simulation_id = H({
 schema_version:"simulation-identity/2",
 collection_id,collection_revision,run_ids,model_digest,
 simulator_name_and_revision:simulator,
 simulator_adapter_code_sha256:H(documents.simulator_adapter_code),
 settings_sha256:identity_digests.settings,
 simulation_response_request_sha256:identity_digests.response_request,
 environment_sha256:H(documents.environment),
 preparation_sha256:identity_digests.preparation})
simulation/2 = {schema_version,canonicalization_id,status:"ready",
               simulation_id,intent:FileRef,archive:FileRef,response_inventory:FileRef}
~~~

simulation/2.archive is a checked FileRef to the creator experiment config/run_record.yml, outside simulation_id. Before publishing or reading readiness, verify its B, creator owner/full simulation ID, archive_id, exact source closure and generated-input checksums. Missing sources, changed run-record bytes and same-scientific-ID archive substitution refuse readiness. Later attempts never replace that creator evidence. No invocation-history traversal is needed to establish this readiness edge.

The forcing-preparation/2 schema is: the preparation document has exactly {schema_version,ancillary,catalog,forcing_elevation,generated_forcing_reader,pet_method}. ancillary contains checked project-relative elevation FileRefs plus their descriptors; catalog is the retained HydroMT FileRef; the remaining resolved payloads have the exact §10.2.1 shapes and preserve their predecessor physical semantics. Its closed identity projection is {schema_version:"forcing-preparation-identity/2",ancillary,catalog,forcing_elevation,generated_forcing_reader,pet_method}. ancillary replaces locators by {role,sha256,size_bytes,descriptor}; catalog retains consumed parsed adapter/driver/unit-conversion/variable semantics, replacing its URI by the bound content digest. forcing_elevation keeps catalog_key/artifact_id; pet_method keeps its resolved value.

generated_forcing_reader is a closed forcing-reader-identity/1 object {schema_version,data_type,driver,data_adapter,metadata,unit_interpretation}. Retain all consumed driver/options/preprocessing and rename/unit_add/unit_mult/time conversion semantics; absent data_adapter is null. metadata retains consumed physical CRS/nodata/units under the explicit §10.2.1 nested schema. unit_interpretation has exactly {revision,variables}, with variables sorted by name as {name,units}. Lift these from metadata.cst_unit_interpretation and exclude its evidence string entirely, including embedded raw catalog hashes, locators and extraction-code hashes. metadata.processing/category are descriptive evidence, retained only in the full document. Every other nested field must be explicitly classified before production; unknown or newly consumed fields refuse. No broad metadata drop may discard a physical setting. Apply the same nested evidence exclusion to catalog semantics. Replace URI/root locators by checked content bindings, without hashing native YAML text. P6 implements the §10.2.1 classifiers and tests them against actual supported predecessor payloads before switching production.

Comments and relocation leave simulation identity fixed; changed elevation bytes or consumed preparation semantics change identity or refuse. The P6 fixture must use the real nested cst_unit_interpretation.evidence payload: catalog comment/location edits change full evidence hashes but preserve simulation_id; a unit/driver/preprocess/adapter/physical-metadata change changes the projection or refuses.

response-inventory/2 retains full artifact/series/time/unit evidence and adds simulation_id, temporal_preparation_sha256=H(temporal_preparation), identity_projection and response_identity_sha256. The closed native_selector keys are {column,toml:FileRef,temporal:LocalSectionRef}. temporal.section is exactly "/temporal_preparation"; its section_sha256 equals temporal_preparation_sha256. The TOML FileRef checks exact retained bytes. Validate the enclosing inventory digest first, then the permitted local pointer and section digest. No selector contains its own document hash. Verify every run’s actual clock, transformation chain, CSV and TOML before removing temporal handoff files.

The separate closed scientific projection is:

~~~text
response-inventory-identity/1 = {
 schema_version,simulation_id,collection_id,collection_revision,model_digest,
 simulator,settings_sha256,response_request_sha256,temporal_preparation,
 artifacts,series}
artifacts = ordered [{run_id,sha256,size_bytes}]
series = ordered [{run_id,variable,location_id,location_ordinal,artifact,
 units,calendar,timestep,time_label,start,end,missing_value,
 native_selector:{column,parameter,output_declarations,clock,temporal_preparation_sha256}}]
clock = {calendar,starttime,endtime,timestepsecs}
output_declarations = ordered [{header,parameter}]
~~~

settings_sha256 and response_request_sha256 use the simulation intent scientific projections, never full evidence hashes. Artifact order follows frozen request run order; series order remains (numeric run_id,variable,location_ordinal,location_id), with artifact as its checked array index. Resolve parameter and all matching output_declarations from actual TOML output.csv.column entries for the selected header and verify the response reader mapping. Preserve order and refuse inconsistent parameters. clock retains the parsed reader values using the request’s canonical timestamp normalization. temporal_preparation retains the full common calendar/conversion/coverage/time-label object. Native content, scientific selectors, reader revision through the response request, transformations and actual clock all remain bound. No new trimming or physical conversion is introduced.

identity_projection equals that object; response_identity_sha256=H(identity_projection). Recompute it from checked native files, parsed TOMLs, intent and temporal evidence. Exact TOML B/path, full response-request SectionRef document B and execution locators stay in full evidence and are excluded from scientific identity. Unknown consumed selector/TOML semantics refuse until classified. Native CSV bytes remain content dependencies, so relocation is not permission to change them.

response_inventory_sha256 remains H of the complete inventory with only response_inventory_sha256 removed. simulation/2 binds B of the final record. Neither full evidence hash nor outer marker hash enters metric scientific identity. Test two fresh rerun roots with identical native CSVs and semantics but regenerated path-bearing TOMLs: simulation_id, response_identity_sha256 and metric_set_id must match while TOML/full-inventory evidence hashes differ. Native value, selector, parameter, clock and transformation mutations change the projection or refuse. Canonical vectors and local-section tampering verify the acyclic reference graph.

metric-request/2 and metric-plan/2 have the exhaustive §10.2.1 shapes; request ID is H(the complete request). The plan retains resolved grouping, reference-month and metric-definition semantics with run_group_id membership. Its closed identity projection is {schema_version:"metric-set-identity/2",simulation_id,response_identity_sha256,metric_definition_sha256,metric_environment_sha256,groups,run_groups,reference,water_year_anchor,return_level_validation_sha256}. groups preserves ordered bundle membership; run_groups uses typed lookup rows; reference binds selected reference runs/month decisions. metric_set_id=H(that projection). Preserve the current resolver and tie rule. metric_definition binds tokens, declarations and inventoried implementation; benchmark declaration/report digests remain bound. The set’s response_inventory FileRef separately verifies full execution evidence.

metric-set/2 has exactly {schema_version,canonicalization_id,status:"ready",metric_set_id,simulation_id,identity_projection,response_inventory:FileRef,response_request:SectionRef,environment,environment_sha256,groups,run_groups,metric_run_lookup:FileRef,tables,return_level_benchmark:FileRef,result_root,engine_root}. tables is ordered {token,file:FileRef} for each requested indicator token. result_root and engine_root are experiment-relative paths to matching 12-ID directories. identity_projection must reproduce metric_set_id; environment_sha256=H(environment) must equal its projected digest. Benchmark B matches the declared validation report. All FileRefs and SectionRefs validate before publication; no unused environment sidecar is emitted.

P4/P6 must implement the strict nested profiles in §10.2.1 and their explicit projection classifiers, checking them against the named predecessor producers. This permits no silent field dropping: a newly observed scientific field not covered by these classifications is a material contract finding, returned before implementation continues. Versioned conformance fixtures must pair exact canonical bytes with expected digests; string placeholders in this design are never production values.

### 10.8 Elevation resolution and clean-output migration

Use data/climate/ancillary/era5/<full-content-sha256>/era5_orography_2018.nc for the current ERA5 binding. Other supported sources retain their registered source/name with the same content-directory policy. Download/copy into a same-directory temporary file, verify B and descriptor, then publish exclusively; an existing path is reusable only after exact verification. Two experiments can bind one file; distinct bytes have distinct directories. A missing WF4-only elevation refuses WF4 preparation and does not invalidate WF3 with verified fixed source bytes. Cold CHIRPS source preparation still needs its elevation and unchanged lapse correction (§7).

The experiment FileRef is project-relative. The HydroMT catalog URI is relative to the retained catalog directory: for the displayed ERA5 layout it is ../../../../../data/climate/ancillary/era5/<hash>/era5_orography_2018.nc. Native HydroMT syntax is used without extra CST keys. Its URI may contain parent segments because it is an upstream-native catalog, but the CST verifier resolves it against the explicit catalog parent, proves its target equals the confined project FileRef, and verifies bytes before use. Do not feed that URI to the FileRef lexical validator or resolve it against process cwd. Catalog and JSON references must still agree after whole-project relocation; test through the actual supported HydroMT reader at P6. If upstream does not honor this anchor as expected, stop with the empirical mismatch rather than silently changing absolute references.

Fresh roots only: before first writing phase, refuse recognized old output schemas or partial unknown collections/experiments at the chosen target. Existing baseline/local trees remain untouched and readable only with their matching predecessor revision. P3/P4 retain the tagged ownership-aware legacy WF3 route (§10.4); P4 validators stay additive. Fresh phase-test roots may contain the known predecessor artifacts deliberately emitted by that phase's interim route. That phase-specific allowlist does not admit arbitrary existing legacy trees or teach new-schema readers legacy compatibility. Final adoption uses a fresh root. P5 switches the WF3 producer, wrapper and readers atomically; pre-P6 WF4 refuses the new collection version explicitly. P6 completes adoption. Require an actual enabled-WF3 all-workflow execution smoke at P3 and P4 through the legacy child with truthful contract_mode/history. At P5 verify the new WF3 handoff and intentional WF4 refusal when enabled; at P6 execute the complete enabled sequence. Dry-run alone cannot satisfy these phase gates.

Reader transition inventory already identified, not exhaustive: shared/workflow_config_snapshot.py, tests/test_build_model.py, tests/test_copy_config_files.py, tests/test_interchange_contracts.py and tests/test_simulation_record.py consume composed snapshots. dev/scripts/check_baseline.py, dev/scripts/semantic_tree_diff.py and tests/test_project_tree_inventory.py also bind old filenames/tree meanings; experiment/shared readers bind the old CSV/header and simulation families. P2 updates archive expectations, P5 scenario contracts, P6 experiment/metric readers; remeasure all references including root Snakefiles before each switch.

Baseline transition is a separate explicit task after P6 and scientific comparison acceptance. Preserve dev/baseline/manifest.json and its old tree as read-only evidence. Run the baseline configuration into a new isolated successor root, with WF1 --notemp, verify the new contract and scientific comparison, create a candidate manifest at a separate path, and review its semantic/tree/numeric differences. Only an explicitly authorized promotion replaces the tracked manifest/baseline target; no check command records or rewrites missing/stale state. Until promotion, updated baseline tooling must fail with “baseline output schema predates this reader; explicit transition required,” and the branch reports that gate unavailable. P7's fresh rapid evidence does not substitute for a baseline-configuration run. No baseline regeneration is authorized by P0 acceptance alone.

### 10.9 Evidence, assumptions and acceptance

**Current P0 evidence status: incomplete; G2 is not satisfied.** The isolated predecessor WF3 dry-run passed after source-cache routing. The real automatic-seed run built seven jobs, completed 3.01 region delineation and 3.03 stress-test lookup, then stalled seven minutes in 3.02 after “saving to netCDF” and was stopped. Only a 75,747-byte extract_historical.nc remained; basin_cells.csv was absent. Explicit-seed 123 was not started because it shares that prerequisite. Neither reference has a completed collection, resolved seed, seed projection, retained series hash or numerical fingerprint. [prechange-reference-probes.md](prechange-reference-probes.md) retains commands and outcomes. Accumulated test_local/test_rapid trees cannot substitute.

Before G2, model-builder must return a completed clean WF3 reference with immutable code/environment pins, actual input/config hashes, isolated output root, command/exit records, resolved seed material/IDs, ordered rows/date selections and complete retained variable/coordinate fingerprints. Design-review agreement does not establish any runtime property.

| ID | Status at v3 | Evidence/result and required observation | Closure |
|---|---|---|---|
| E1 | Observed by source inspection | [Domain review](internal-review-domain.md) documents predecessor preparation calls, ancillary seed projection and inventoried WF4 code. | P0 inspection; P4 removal still untested |
| E2 | Hypothesis, unexecuted | Hold source bytes fixed for WF4-only elevation/config/code mutations. CHIRPS source-elevation change requires changed source evidence/bytes or refusal, without invariance. | P4/P7 |
| E3 | Hypothesis; reference incomplete | [Probes](prechange-reference-probes.md) show passed dry-run and stopped partial run, no parity. Complete WF3 and independent WF4 comparators below. | WF3 capture before G2; P5/P6/P7 comparisons |
| E4 | Hypothesis, unexecuted | Exact-buffer/pre-parse race, duplicate-basename, archive crash/terminal recovery and next-writer tests. | P1/P2 |
| E5 | Hypothesis, unexecuted | Cold/prepared/reuse/force DAG, pointer race, creator/candidate reuse, snapshot mutation and descendant-ownership tests. | P3/P5/P7 |
| E6 | Hypothesis, unexecuted | A→B rerun→relocated C with A absent; actual HydroMT read; source/archive/temporal tampering; path-neutral response fixtures. | P1/P4/P6/P7 |
| E7 | Selected policy supported; implementation unexecuted | Fresh-root reader sweeps/refusals and separately authorized baseline transition remain to run. | P2/P5/P6; later baseline promotion |
| E8 | Hypothesis, unexecuted | Installed YAML and actual provider arguments equal frozen scientific plan; deliberately self-consistent bad YAML/argument mappings refuse. | P5/P7 |
| E9 | Hypothesis, unexecuted | Every §10.6 excluded field passes its admitted mutation cases with exact decoded output/member/date equality; promote or refuse failures. | P4 specification; P5 execution/model-validator; P7 integration |

**Independent predecessor WF4 comparator.** WF3 generation evidence cannot establish Wflow-response or metric continuity. Before P1 runtime edits, pin an executable predecessor checkout at a1a97ffeccea41eed3d1bf449d94f0487121f300 plus actual installed Python/R/Julia environments, dependency revisions, source/catalog/config bytes, model inputs and WF4 preparation inputs. Lock files alone are insufficient. This pin/capture remains pending; no model or native output digest is asserted. Model-builder owns execution/capture; model-validator verifies matches and returns the numerical verdict.

Before P4 changes the collection/module boundary, execute the predecessor WF1/WF4/metrics path in an isolated comparison project using the clean predecessor explicit-seed 123 collection. Build or verify its model through pinned predecessor WF1, retain complete model inventory/model digest and warm state, and freeze that model for the successor comparison. Retain actual elevation, native catalog adapters/unit interpretation, PET/corrections, windows, calendar transformation, evaluated runs, native request, metric definitions and environment. Capture all native response CSVs, per-run TOMLs and temporal evidence, response inventory, lookup/group rows, reference-month decisions, benchmark report and every requested indicator table. Keep comparator outputs outside successor write targets. If capture fails, P4 and the numerical-continuity claim stop for repair or an explicit owner ruling; successor self-comparison cannot pass.

Map scenario members by (rlz,st_id,type,evaluate) to successor run_id, preserving each empty-st_id root and distinct zero-change perturbed member. Map responses by (mapped run_id,variable,location_id,location_ordinal) and time, checking physical parameter, clock, units/calendar and masks. Map predecessor unit_id/member_run_id to run_group_id/run_id using ordered members and grain; padded IDs, bundle order, metric token/location and actual reference runs/months must match. Capture the mapping explicitly, not by assuming renamed files imply equivalence.

For matched explicit seed on the same machine/environment, require exact decoded scenario arrays, coordinates, masks, units/calendars, date-selection CSVs, row order and reconstructed ancestry; absolute and relative tolerances are zero. Preserve member-to-array associations. NetCDF container differences require documented non-scientific encoding/path explanation. Compare native discharge and every other requested response and every requested metric against the independent predecessor capture with identical model/engine/preparation semantics. Require exact aligned values/fingerprints, masks and coverage. Report members/value counts, mismatch locations, maximum absolute differences and discrete failures. Inject one changed value and a swapped member to demonstrate comparator failure. Any nonzero tolerance returns to model-validator and the owner before acceptance.

For automatic seed, record actual v1 material/seed/output when available and test v2 against its own projection; numeric v1 parity is neither required nor predicted. WF4-only mutation invariance requires fixed verified WF3 source bytes. Scientific WF3 input/setting changes alter projected digests (integer modulo seeds can collide). Test user comments, relocation, nested unit evidence and WF4-only shared-catalog entries as invariants; consumed interpretation or CHIRPS lapse-correction changes are sensitivity/refusal cases. Rapid ERA5 does not exercise CHIRPS: a focused cold-source fixture must preserve the correction and a prepared-store fixture must work without WF4-only elevation.

P1/P2 gates cover exact pre-parse capture, recovery including terminal states and new-writer admission, duplicate basenames and rerun mapping. P3/P4 require runnable interim wrapper handoffs and ownership. P4 requires the concrete uncontaminated code closure, complete nested-schema canonical vectors, lineage and the exhaustive exclusion matrix. P5 requires installed-YAML/argument semantic equivalence and execution of that matrix, including repeated parallel/core mutations; model-validator returns exact decoded-output acceptance before P7 integration. P5 hands generated output to model-validator; P6 hands native responses/metrics plus their independent comparator to model-validator. P7 integrates only returned acceptance; structural passes are insufficient.

Remaining empirical risks include unverified excluded-setting equivalence (especially parallel RNG/core scheduling), Python/R YAML interpretation, and local filesystem lock/rename behavior, descendant ownership after launcher death, protected snapshot consumption, exact code closure, cold CHIRPS preparation, actual HydroMT relative-URI resolution, static cold/prepared/reuse/force DAGs, R member naming, the current extraction stall, predecessor WF4 environment/model/capture availability and baseline-transition cost. These are unexecuted checks, not permission to weaken policy. No material contract choice is knowingly unresolved; an unclassified consumed field or an unachievable platform guarantee returns as a contract finding.

Consequences: fresh outputs and changed identities; retained input copies add storage; embedded records preserve evidence; serialized project execution limits throughput; predecessor WF4 capture adds a required execution gate. Reruns still need explicitly mapped external datasets and pinned environments. Full dataset export, resume, distributed fencing, physics changes and new metric methods remain outside scope.

Alternatives in §9 remain relevant. A content-addressed archive store would suit historical WF0–2 recovery but exceeds latest-only retention. Per-collection leases improve throughput but do not protect shared preparation. Live-path prechecks reduce copied storage but cannot prove later consumed bytes. Full-inventory metric hashing is simpler but violates path neutrality. Dropping WF4 continuity would avoid comparator capture but requires an owner scope ruling and is not selected.

## 11. Outline for the eventual task brief

Objective: emit the agreed output tree and records in a fresh project, preserve accepted scientific behavior, and make each recorded execution traceable to its actual inputs.

Potential implementation units, with explicit dependencies:

1. **Record/archive contract and common writer.** Start with copy_config_files.py, shared/workflow_config_snapshot.py, shared/provenance.py and configuration composition. Establish pre-Snakemake capture/resolver handoff, retained predecessor rerun evidence and terminal recovery/next-writer admission before switching writers. Freeze executable predecessor WF4 inputs before P1 edits (§10.9).
2. **WF0–WF2 and artifact-local archive adoption.** Introduce the mandatory capture launcher and minimum ownership in P2; refuse raw new-schema emission. Wire the relevant workflow/launcher paths and current readers/tests. Update declared outputs, baseline readers and output-tree inventory in the same runnable change. Depends on unit 1.
3. **Unified invocation history.** Update scripts/run_workflows.py, scripts/simulate_system.py and existing workflow journal hooks; add launcher coverage and parent/child ownership. Keep the explicit legacy_wf3_interim route runnable through P3/P4; execute its enabled-WF3 wrapper smoke. Depends on unit 1, not the future P5 planner.
4. **Model-independent collection and shared elevation contract.** Require independent predecessor WF4 capture (§10.9) before starting. Keep P4 additive until P5 switches production. Update experiment/scenario_collection.py, collection_resolution.py, scenario_provider.py, generation_plan.py and content_identity.py with their current consumers. Embed four WF3 sidecars and remove WF4 preparation and elevation from collection identity. Coordinate with WF4's new elevation binding (§7); this is an identity change, not a packaging-only change.
5. **Static WF3 planning.** Switch wrapper/producer/readers together, remove legacy route, implement pinned scientific-input consumption and creator/candidate reuse, and install YAML before archive/receipt. Update generate_scenarios.smk, experiment/generation_plan.py, collection_resolution.py, scenario_provider.py and scenario_collection.py plus the agreed entry point. Depends on frozen plan/invocation interfaces and the preparation contract it will validate.
6. **Simulation and metric-set contract consolidation.** Update experiment/simulation_record.py, response_inventory.py, metric_plan.py, downscale_climate_forcing.py, scenario_collection.py collection-reference discovery, shared/cross_workflow_leaves.py, workflow leaves, current readers and tree tests. Embed the five simulation input payloads and the metric environment in their respective records, publish final markers after verification, retain common temporal evidence once and keep the human-facing archive in config/. Re-measure baseline assumptions before deciding validation cost. Depends on the agreed §§8.3, 8.5 and 8.6 contracts.
7. **Complete-run evidence.** Use an isolated rapid successor project; compare against the clean explicit-seed WF3 reference and independent pinned predecessor WF4 responses/metrics. Retain mappings, coverage, comparator perturbation failures and returned scientific acceptance. Depends on all units selected for the agreed scope.

These are candidate work packages, not a blanket authorization or a claim that each is one small patch. Before dispatch, remeasure readers/writers and produce bounded briefs with confirmed files and commands. Do not combine unrelated numerical fixes, change upstream HydroMT/Wflow internals or add resume semantics. Plan the baseline transition separately from incidental cleanup.

Acceptance evidence to carry into those briefs:

| Claim | Observation that would disprove it / required check |
|---|---|
| Exact source recovery | Byte mismatch (including CRLF/comments), lost original basename, or missing loaded workflow/custom dependency. Test pre-parse comment mutation, exact source copies and A→B rerun→relocated C with A unavailable. |
| One matching archive | Interrupted or concurrent publication exposes mixed record/source checksums. Exercise failure points, terminal rollback/unpublished outcomes and second-reader/recovery/next-writer admission with diagnostic evidence preserved. |
| Clear invocation history | Missing child linkage, a dry-run reported as work, or hard termination reported as success. Exercise direct, parent/child, startup failure, no-op and crash cases. |
| Stable scientific meaning | Comment-only edits alter scientific identity, a WF4-only change alters the new automatic seed or collection ID, row order changes, or retained scenario series differ under a matched explicit seed beyond the agreed tolerance. Check the new seed formula separately from numerical parity. |
| Reduced collection JSON count | A fresh collection still emits the four WF3 sidecars, embeds WF4 preparation, or omits generation evidence. Assert exactly two JSONs in its scenario engine record directory and exercise the new reader. |
| Scenario root/engine binding | A bare data directory is listed as ready, an orphaned marker passes, two requests duplicate one collection, or detached export omits its records. Test each and verify full-ID/short-segment correspondence. |
| Generated-input recovery | The weather-generation YAML is absent, differs from the run record's checksum, or a moved project silently reuses its old absolute output path. Validate exact bytes and relocation behavior. |
| Provider intermediates and diagnostics | Date-selection CSV bytes are unaccounted for, conditional figures disappear during relocation, or temporary realization netCDFs become silently durable. Check inventory/reference coverage and terminal-render handling. |
| WF3/WF4 product boundary | A WF3 `series/` artifact is called a ready model forcing, or a WF4 transformation silently changes the source series. Check collection byte identity and explicit downstream preparation/reference separately. |
| Stochastic run lineage | A realization lacks a unique empty-`st_id` root, a perturbed row has an unmatched realization or design point, or removing `derived_from` changes the intended ancestry. Validate the cross-product and compare reconstructed parent IDs against the pre-change reference. |
| Simulation intent and readiness | A response request or model-reference section loses data, section tampering passes, an intent-only experiment is treated as ready, the marker precedes its verified inventory, or response-inventory depth changes. Assert two simulation-family files for new runs; validate metrics-only reads. |
| Wflow run-setting retention | A TOML is missing or changed, a run with different clock/conversion passes common-temporal validation, or a new selector requires a removed temporal file. Check all run TOMLs and temporal evidence before publication, then metrics-only reading after temporary files are gone. |
| Wflow native-log attribution | A run writes beside the CSV, two concurrent runs share one log, or `_log/` is absent when Wflow opens its path. Check every generated `logging.path_log` and exercise a bounded concurrent run. |
| Metric-set grouping | A table or `metric_run_lookup.csv` lacks a checked reference, their `run_group_id` keys do not join, one group has no members or inconsistent grain, the two short-ID directories bind different full IDs, environment-section tampering passes, benchmark bytes are missing or differ, or an orphan is listed as ready. Validate the new contract, metrics-only reuse, paired export and external discovery. |
| Cross-file run-group naming | A new config, collection intent, metric plan, lookup, indicator table or reader mixes `unit_id` and `run_group_id`, changes padded values/allocation order, or confuses a group ID with a member `run_id`. Check each proposed producer, digest and consumer together. |
| Shared elevation and WF4 binding | A new collection ID changes solely with WF4 orography, a simulation omits its checked elevation/adapter, changed bytes pass, or relocation breaks the experiment catalog URI. Test all four with fixed WF3 source bytes, plus CHIRPS cold-source sensitivity/refusal and prepared-store reuse. |
| Static generation scheduling | Either checkpoint still expands the generation DAG, live pointer replacement redirects execution, or cold dry-run silently produces scientific outputs. Inspect DAGs and filesystem differences. |
| Complete-run tree | A fresh isolated WF0–WF4 run lacks a required record, reference cannot resolve, or temporary provider files are wrongly retained. Capture the actual tree and representative schemas after successful execution. |

During implementation, run focused tests for the changed surfaces. Apply tests/test_cli.py when rules/signatures/declared inputs change and the repository's lint/format checks for Python. At approved batch landing use the documented combined gates; shared/signature changes require the stated full-suite rung. Run numerical baseline comparisons only when their scope warrants them, using the baseline configuration and preserving its WF1 temporary discharge target with --notemp. Do not repeatedly run the full suite for each incremental edit. Exact new manifest/archive test commands belong in the finalized briefs once test files exist.

## 12. Sources and verification of this draft

Read-only evidence: current metadata files under session-1's test_case/test_local and test_case/test_rapid; current snapshot writers; generation_plan.py; scripts/run_workflows.py and scripts/simulate_system.py; ADR 0011, the WF3 intake, TODO/task notes, post-R12 migration event 6 and recovered closed scenario-tree task history. The repository search does not include external conversation transcripts, remote-only branches or other sessions’ uncommitted notes. Inspected output IDs identify examples, not fresh validation results.

Implementation references:

- [WF0–WF2 snapshot writer](../../../../blueearth_cst/model/copy_config_files.py)
- [Artifact-local snapshots](../../../../blueearth_cst/shared/workflow_config_snapshot.py)
- [Configuration provenance](../../../../blueearth_cst/shared/provenance.py)
- [Generation planning](../../../../blueearth_cst/experiment/generation_plan.py)
- [Collections and publication](../../../../blueearth_cst/experiment/scenario_collection.py)
- [Preparation catalogs](../../../../blueearth_cst/climate_analysis/prepare_climate_data_catalog.py)
- [All-workflow launcher](../../../../scripts/run_workflows.py)
- [Simulation launcher](../../../../scripts/simulate_system.py)

V1 document validation: all local Markdown link targets resolve from this review copy; all three fenced JSON examples parse; no trailing whitespace was found. Self-review reconciled the selected §10 contract with earlier candidate wording. Shell-based Git checks were unavailable in this author session (process launch denied); no workflow execution, test suite, full tree-conformance check or numerical validation is claimed.

V2 document validation: all local links in the design and ledger resolve; all three fenced JSON examples parse; no trailing whitespace; all 14 original finding IDs appear exactly once in the ledger; design-v1.md remains byte-identical to the initial read. Verification is structural only. No runtime tests, new reference run or scientific comparison was executed by this author.

V3 document validation: design-v2.md is byte-identical to the initial copy (SHA-256 d11bf4f2c05d1f24919fabc7e5ab8a201633e41526fa366c3335f31d0602ce61); ledger prefix is unchanged and each ext1-1/ext1-2/ext1-3 has exactly one disposition. All local links in v3/ledger resolve, all three JSON examples parse, and neither file has trailing whitespace. Sections 1–9 and 11 remain text-identical to v2; normative changes are confined to §10 plus title/verification/revision metadata. The benchmark pin was checked against the packaged asset bytes, with no benchmark execution. No runtime tests or scientific runs were performed; v3 convergence does not satisfy G2.

## Revision history

- **2026-09-21, v1:** Copied the latest proposal first, retained its agreed tree and rationale, and settled P0 decisions in §10 against the master/P1–P7 briefs, ADR 0011 and WF3 intake. G1 is recorded; G2 and clean-reference evidence remain pending. No runtime implementation or numerical validation was performed.

- **2026-09-21, v2:** Copied v1 before revision and accepted all 14 original internal findings in [ledger.md](ledger.md). Closed pre-parse launcher coverage, interim phase routes, pinned scientific consumption, creator/candidate reuse, terminal archive recovery, retained rerun evidence, simulation archive and local temporal-reference edges, nested unit-evidence exclusion and path-neutral metric response identity. Required an independent predecessor WF4 comparator. Updated the clean-reference status to the reported stopped extraction attempt; G2 and all scientific-continuity claims remain pending. No runtime code, predecessor design or implementation brief was changed.

- **2026-09-21, v3:** Accepted all three external-round-1 majors in [ledger.md](ledger.md): exhaustive versioned nested profiles and H/B/ordering/null rules, installed-YAML/provider-argument equivalence to the frozen plan, and excluded-field mutation acceptance with promotion/refusal for scientific effects. Clean break, WF3 independence, exact explicit-seed comparison and the unsatisfied G2 reference gate remain. No runtime code, implementation brief, predecessor design or original review was changed.
