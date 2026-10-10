# Reservation lifecycle consumer inventory

Status: stage-1 inventory, 2026-10-10; proposed ownership, not implementation evidence.
Contract: [design-v1.md](design-v1.md). This companion answers which consumers each phase must reconcile;
the design owns behavior, schemas and the generated tree. No duplicate normative schema is maintained here.

Inspected runtime checkout: `6998d0fd1f460a78934bc79aeb546c5184ba3af8`, session-1. Task plans were read
from the primary checkout because sparse checkout omits their physical files here. No session-3 contract
was imported. P1 is independently owned by the coordinator; entries below do not authorize overlapping edits.

## 1. Phase map

- P0: this design/inventory, independent domain/risk review, acceptance by the owner.
- P1: scaffold output-root change and its own guidance/checks; no experiment runtime changes.
- P2: inactive allocator/reservation library, schema and synthetic lifecycle tests.
- P3: activate both runners, generation callback and DAG consumers together; focused runtime checks.
- P4: live docs, templates, final consumer sweep and representative execution evidence.

P2 and P3 implementation belongs to python-engineer under the accepted contract. Model-builder exercises
the representative interrupted run; model-validator assesses retained-input/output equivalence.
The driver controls phase handoff, review gates and tracked task state.

## 2. Runtime producers and direct consumers

Path prefixes: `E/` = `blueearth_cst/experiment/`, `S/` = `blueearth_cst/shared/`, and
`R/` = `blueearth_cst/experiment/rules/`. Other paths are repository-relative.
A retained reader still needs its assigned phase's compatibility
check; being listed does not mean it must be edited.

| Path | Role and required action | Phase |
|---|---|---|
| `E/allocate.py` | Add inactive resolver/ledger API; preserve current callers until P3 | P2 |
| `E/reservation.py` | Proposed new closed request/transition/transaction module | P2 |
| `S/snake_utils.py` | Keep name grammar; integrate shared resolver and dated advice exports | P3 |
| `scripts/suggest_experiment_name.py` | Preview-only resolver; retire YAML edit/reserve modes | P3 |
| `scripts/run_workflows.py` | Reserve before WF0–WF4 producers; retain one lock/context | P3 |
| `scripts/simulate_system.py` | Same admission; ready collection; no duplicate resolution | P3 |
| `E/simulation_runner.py` | Shared flags/selection/targets and internal handoff | P3 |
| `scripts/generate_scenarios.py` | Optional owned callback before stochastic child; plan recovery | P3 |
| `E/generation_plan.py` | Reuse effective generator/seed logic and pinned plan APIs | P3 |
| `E/generation_publication.py` | Retain sole collection ownership; exercise callback seam | P3 |
| `E/collection_resolution.py` | Keep explicit manifest-only selector; validate ready leaf | P3 |
| `E/scenario_collection_v2.py` | Existing schema/identity authority; no numbering migration | P3 |
| `E/scenario_rows.py` | Keep producer-owned padded IDs, row order and membership | P3 |
| `E/content_identity.py` | Reuse existing helpers; no edit required without a demonstrated gap | P2 |
| `S/wf3_science.py` | Do not revive experiment-name-derived auto seed | P3 |
| `E/prepare_weathergen_config.py` | Share effective settings; no new generator defaults | P3 |
| `E/generation_sources.py` | Source semantics/interpretation remain authoritative | P3 |
| `E/simulation_record.py` | Keep schemas; make owned intent/archive gap recoverable | P3 |
| `E/response_inventory.py` | Retained native readiness/integrity authority | P3 |
| `E/batch_staging.py` | Verify actual partial reuse boundary; no assumed integrity | P3 |
| `E/run_wflow_batch.jl` | Existing staging producer; exercise, no planned code edits | P3 |
| `E/wflow_response_reader.py` | Existing native reader; retain validation requirements | P3 |
| `E/metric_plan.py` | Pass resolved name for metrics-only; no allocation | P3 |
| `E/check_project_consistency.py` | Legacy config comments/ownership; classify, retain guards | P3 |
| `E/write_model_reference.py` | Existing model fingerprint; final source of truth | P3 |
| `E/check_model_reference.py` | Retain immutable model-drift refusal | P3 |
| `E/wf4_ancillary_descriptor.py` | Retain exact forcing-preparation identity | P3 |
| `S/model_digest.py` | Existing model digest, never replace with metadata hash | P3 |
| `S/config_composition.py` | Source schemas; classified scientific projection; no rewrite | P3 |
| `S/cross_workflow_leaves.py` | Metrics-only leaves need the resolved experiment | P3 |
| `S/interchange_contracts.py` | Name grammar references; retain cross-language contracts | P3 |
| `S/workflow_config_snapshot.py` | Existing lock/archive recovery; use without nested lock | P3 |
| `S/workflow_archive_launch.py` | Existing capture/path anchors; preview stays non-producing | P3 |
| `S/invocation_history.py` | Record name/binding in plan; outcome separate from readiness | P3 |
| `S/windows_job.py` | Verify parent-death child cleanup before lock recovery claim | P3 |
| `S/provenance.py` | Existing toolbox/environment identity fallback | P2 |
| `blueearth_cst/model/copy_config_files.py` | Update helper comment; preserve archive semantics | P3 |
| `scripts/plot_workflow_dag.py` | Pure preview name for DAG filenames/captions | P3 |

## 3. Workflow, logging and inspection consumers

| Path | Action | Phase |
|---|---|---|
| `simulate_system.smk` | Validate runner handoff, maintain operation guard | P3 |
| `R/simulate_and_metrics.smk` | Consume exact name; bind before downscaling/native work | P3 |
| `R/metrics_only.smk` | Consume selected retained experiment; read-only admission | P3 |
| `generate_scenarios.smk` | Preserve source/generation separation; no experiment allocator in DAG | P3 |
| `build_model.smk` | Read effective model recipe for early classification; no new scientific rules | P3 |
| `analyze_climate.smk`, `analyze_projections.smk` | Unchanged; precede with admission | P3 |
| `scripts/run_workflow.py` | Verify WF4 cannot bypass its owned runner | P3 |
| `dev/scripts/scaffold_project_tree.py` | Resolve preview where current code reads raw experiment name | P4 |
| `dev/scripts/snapshot_project_tree.py` | Report resolved name; reconcile inventory | P4 |
| `dev/scripts/semantic_tree_diff.py` | Retain historical mappings; no rewrite of predecessor names | P4 |

WF4 log, benchmark, parts directories and headers derive from the one `experiment` value in the included
rules. They need no parallel allocator. The all-runner discovers log paths from workflow declarations;
do not reconstruct experiment names independently there. Existing `run_log_core`/console modules consume
the resulting paths only; no contract change is proposed for them.

## 4. Focused tests and fixtures

P2 owns `tests/test_experiment_allocation.py`, `tests/test_validate_experiment_name.py`,
and proposed `tests/test_experiment_reservation.py`. Include parser growth,
adoption/tombstone, transaction-boundary, alias rejection and independent-process ownership cases.

P3 owns the runtime compatibility checks in:

- `tests/test_snake_utils.py` for the shared resolver integration.
- `tests/test_simulation_runner_v2.py`, `tests/test_run_workflows.py`,
  `tests/test_suggest_experiment_name.py`.
- `tests/test_simulation_record_v2.py`, `tests/test_workflow_config_snapshot.py`,
  `tests/test_metric_plan_v2.py`.
- `tests/test_generation_plan_v2.py`, `tests/test_scenario_collection_v2.py`,
  `tests/test_climate_store_contract.py`.
- `tests/test_config_composition.py`, `tests/test_interchange_contracts.py`,
  `tests/test_reader_revision_message.py`.
- `tests/test_check_project_consistency.py`, `tests/test_plot_workflow_dag.py`, `tests/test_cli.py`.
- `tests/test_metric_plan.py`: inspect whether this is retained predecessor behavior; do not rename fixtures
  merely because they contain old names.

P3 reconciles producer-derived helpers `tests/_v2_experiment.py`, `tests/simulation_workflow_fixture.py`,
`tests/project_config_fixture_simulate_system.yml`, and
`tests/data/v2/project_config_v2_probe_simulate_system.yml`. Preserve intended legacy fixtures explicitly.
Changing every old name would remove compatibility coverage.

P4 checks `tests/test_snapshot_project_tree.py`, `tests/test_project_tree_inventory.py`, and any tests
reading the changed templates/docs. Final full/e2e gates belong to approved batch landing, not P0.
Detailed acceptance claims and reusable roots are in design section 8; no gate is reported as run here.

## 5. User documentation, configuration and independent P1 scope

P4 naming/command guidance consumers discovered by the search:

- `README.md`, `scripts/README.md`, `config/templates/README.md`.
- `config/templates/project_config.simulate_system.template.yml`.
- `docs/site/guide/configuration.qmd`, `docs/site/guide/running.qmd`.
- `docs/site/toolbox-reference/retained-handoffs.qmd`.
- `docs/site/toolbox-reference/workflow-simulate-system.qmd`.

P4 inspects all `test_case/project_config_*_simulate_system.yml` seeds to decide whether their explicit
values are intended legacy pins or new-family examples; no blanket rename. Keep `project_config_` prefixes.
`AGENTS.md` commands are updated only if affected. Sealed milestone/review records remain untouched;
consult `dev/reference/sealed-records.yml` before classifying an old reference as stale live guidance.

P1 owns `scripts/create_case.py`, its scaffold tests and case-root guidance from its assigned phase brief.
It removes the mandatory `active/` suffix in new scaffolds only. Existing configured roots stay valid.
The root coordinator is performing that work; reservation design makes no concurrent edits to those files.
The search's active-path match in `docs/site/guide/running.qmd` needs P1/P4 coordination, not two independent
edits. Runtime numbering always keys on resolved project root and does not infer a scaffold convention.

## 6. Inventory reproduction and limitations

Read-only searches completed during authoring:

```powershell
rg -n 'experiment_name|resolve_default_experiment_name|allocate_experiment' blueearth_cst scripts tests --files-with-matches
rg -n 'simulation_intent|archive_lock|seed_resolution' tests --files-with-matches
rg -n 'experiment_name|suggest_experiment_name|resolve_default_experiment_name' --glob '*.smk' --glob '*.py' dev/scripts
rg -n 'experiment_name|suggest_experiment_name|stress_test_01|_YYYYMMDD' docs/site config/templates scripts/README.md README.md --files-with-matches
rg -n 'active/|/active' scripts docs/site config/templates tests README.md --files-with-matches
```

Root Snakefiles and included `.smk` files were inspected separately; the first search does not cover root
Snakefiles. Search results containing comments or predecessor mappings were classified rather than
automatically assigned an edit. Repeat the sweep against the implementation candidate before P4 closure.
This is a static consumer inventory, not proof of every runtime dependency or filesystem behavior.
