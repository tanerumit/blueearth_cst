# Task Brief — P2 durable handoffs in current WF3

### Context

- Follow repository `AGENTS.md`, [master brief](master-brief.md), and accepted §§5.2, 5.4–5.7, 6.1–6.8, 8.2–8.6, 9.5 resolution rules, and 12.
- P1 is integrated. Current `run_stress_test.smk` remains the sole production entry point and comparison harness.
- Entry prerequisite: P0 proves supported checkpoint and mandatory-runner operation mechanics; GF-29/GF-30 still require actual implemented single-invocation behavior. P2 uses the test harness against current WF3; P3 ships the dedicated simulation runner.

### Goal

Materialize immutable scenario collections, simulation/response records, metric plans/sets, exact resolution, and metrics-only operation behind current WF3 so the handoffs are portable, validated, reusable, and stale-safe before file/config splitting.

### Non-goals

No new entry points, five-stanza config, runner order change, live-reference rename, old-WF3 retirement, general run-control/fencing/resume platform, or scientific-method change.

### Allowed scope

**Exact existing targets:** `run_stress_test.smk`; P1 modules; `blueearth_cst/experiment/downscale_climate_forcing.py`, `check_model_reference.py`, `write_model_reference.py`, `export_wflow_results.py`; `blueearth_cst/climate_analysis/prepare_climate_data_catalog.py`; `blueearth_cst/shared/model_digest.py`, `provenance.py`, `interchange_contracts.py`, `cross_workflow_leaves.py`; `dev/scripts/snapshot_project_tree.py`, `semantic_tree_diff.py`; narrow tests for these files.

**Proposed paths:** `blueearth_cst/experiment/content_identity.py`, `scenario_collection.py`, `collection_resolution.py`, `simulation_record.py`, `response_inventory.py`, `metric_plan.py`; `tests/test_scenario_collection.py`, `test_collection_resolution.py`, `test_simulation_record.py`, `test_response_inventory.py`, `test_metric_plan.py`, `test_metrics_only.py`, and portable preparation fixtures under `tests/data/`.

**Forbidden:** `generate_scenarios.smk`, `simulate_system.smk`, stanza/template/test-case split, runner migration, sealed records, standing baseline, or attempt/resume machinery.

### Required changes (checklist)

- [ ] Implement canonical identities and immutable payloads exactly as §§5.5–5.6, 6.2/6.7, 8.2–8.4a specify; every stored path is confined and every ready marker is written last atomically.
- [ ] Implement source-planning checkpoint, pure-row scheduling, collection initialization claim, durable forcing/preparation closure, exact ready reuse, partial refusal, and reference-aware explicit deletion/listing.
- [ ] Package `preparation_context.json`, reduced catalog, and every ancillary byte for CHIRPS, CHIRPS-global, non-CHIRPS orography, and E-OBS PET branches; no consumption fallback to live catalogs.
- [ ] Implement simulation freeze/identity, response request, response inventory, native reopening and full expected-series validation. Preserve batch resource/log visibility and current HydroMT/Wflow operations.
- [ ] Implement metric request/plan/final identity, immutable metric-set publication, long `unit_index.csv`, exact expected result keys, Class-C provenance, and validation declarations.
- [ ] Implement §6.8 metrics-only and the full operation/target matrix. `experiment_name` selects one recorded simulation; missing requirements never schedule Wflow.
- [ ] Implement deterministic project-plan versus explicit-manifest resolution with no directory scan, `latest`, fallback, or config-supplied digest.
- [ ] Prove forced-rerun output preservation, stale-plan refusal, digest invalidation, and no hidden mutation before P3.

### Commit plan

| Subject | Paths | Invariant preserved |
|---|---|---|
| `feat: publish immutable scenario collections` | identity/collection/resolution/preparation code, current WF3, tests | collection ready only after complete portable inventory; exact reuse cannot mutate bytes |
| `feat: persist simulation responses` | simulation/response records, Wflow adapter call sites, tests | one response entry per requested key; collection/model/settings changes cannot reuse stale responses |
| `feat: publish metric sets and metrics-only mode` | metric planner/set/operation code, current WF3, tests | final identity follows completed responses; metrics-only defines no simulator producer |

### Validation

- Per edit: proposed narrow tests and existing `pixi run pytest tests/test_downscale_climate_forcing.py tests/test_prepare_climate_data_catalog.py tests/test_interchange_contracts.py tests/test_export_wflow_results.py`.
- Per Python commit: lint/format; after each Snakefile/signature change: `pixi run pytest tests/test_cli.py`.
- Once per commit group: relevant GF-6..GF-7, GF-10, GF-12, GF-16..GF-18, GF-22..GF-24 tests from [validation-map](validation-map.md).
- Once before P3: run GF-29/GF-30 mechanism-equivalent fresh single-invocation evidence through the current-WF3 carrier and synthetic harness, without claiming successor-entry-point or migrated-runner coverage; run GF-32 multi-collection resolution fixtures and GF-31 portability comparison for every supported source branch. P3 must repeat GF-29/GF-30 through direct generation, the dedicated simulation runner and the all-workflow runner.
- Model-validator handoffs: collection completeness/pairing/calendar/units; forcing compatibility and Wflow completion/equivalence; response/metric coverage and estimator preconditions. Astra evaluates GF-31 against its already accepted criteria without a new approval gate.

### Acceptance criteria

All manifests/digests recompute from persisted state; ready artifacts are immutable and complete; two experiments reuse one collection; metrics-only works without live generation/model/Wflow and refuses incomplete retained state; current-carrier GF-29/GF-30 evidence and GF-31/GF-32 pass before P3, with final entry-point/runner GF-29/GF-30 still explicitly pending P3.

### Output requirements

Return manifest examples, identity inputs, invalidation observations, retained-byte accounting, narrow/CLI evidence, checkpoint traces, and signed validation handoffs under `dev/milestones/r12/implementation/evidence/p2/`.

### Task constraints

No silent retention cap, same-intent partial resume, normalized response copy unless separately justified, or broader execution-control platform. Routine configuration never exposes machine identities.

### Execution checkpoint — 2026-09-10

Owner instruction to continue R12 releases the next P2 increment after recorded
P1 acceptance. Pure `content_identity.py` implements collection-canon/1, strict
persisted JSON reading, confined artifact paths, semantic-row hashing, and the
two §8.2 identity projections. No production caller or scientific operation
changed. [Checkpoint evidence](evidence/p2/identity-foundation.md) records exact
checks and the read-only Python-engineer review.

Next: implement collection initialization/publication and full persisted-state
validation using these primitives, then portable preparation closure and the
source-planning checkpoint. The first checklist item remains open: identities
alone do not implement immutable payloads, ready-marker publication, or complete
validation. Production collection integration still requires its named scientific
handoff; simulation/response and metric-set persistence follow in order.
