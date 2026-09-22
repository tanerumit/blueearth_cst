# Task Brief — P6 Simulation and metrics

### Context

Read `AGENTS.md`, [master brief](master-brief.md), [schema](../complete-run-output-schema.md) §§2, 7–8. P4/P5 supply the versioned collection consumed by WF4.

### Goal

Consolidate experiment machine records under one `_engine/` and publish user-facing responses and metric sets with the proposed filenames and columns.

### Non-goals

No Wflow-owned settings rename, model-physics change, altered metric definitions or pre-migration output readers.

### Allowed scope

Permitted: `blueearth_cst/experiment/simulation_record.py`, `response_inventory.py`, `metric_plan.py`, `downscale_climate_forcing.py`, the collection-reference reader in `scenario_collection.py`, `blueearth_cst/shared/cross_workflow_leaves.py`, `simulate_system.smk`, `scripts/simulate_system.py`, affected tests/docs. Re-measure actual consumers before edits. Forbidden: generated outputs and upstream Wflow/HydroMT.

### Required changes (checklist)

- [x] Publish `simulation/2` intent and readiness records as flat `_engine/simulation_intent.json` and `simulation.json`, with the accepted closed nested inputs, path-neutral response identity, and a completion marker after response verification. Require new-contract collections; P6 owns their first WF4 adoption.
- [x] Adopt P1's exact creator `config/run_record.yml` and `sources/` for new experiments. Preserve that archive during metrics-only work; record later metric attempts in invocation history. Apply P0's policy to failures before archive creation; require new-contract collections.
- [x] Keep Wflow run TOMLs in `run_settings/`, validate the accepted common temporal evidence once in `response_inventory.json` while retaining run-specific differences, and put each native log under `output/_log/` with per-run attribution. Include checked WF4 elevation/catalog binding in the simulation intent and verify it before forcing preparation.
- [x] Move `metric-set/2` machine records under experiment `_engine/metric_sets/<id>/`; keep `metric_run_lookup.csv` and `<token>_indicators.csv` under `results/metric_sets/<id>/`. Bind both short-ID directories to the same full ID and apply the accepted path-neutral digest projection.
- [x] Use headers `run_group_id,grain,run_id` and `metric,location,run_group_id,value`; align new config/intent capacity and width and metric-plan bundle fields with `run_group_id`, preserving padded values and allocation order.

### Commit plan

| Subject | Paths | Invariant |
|---|---|---|
| Version simulation records and paths | Writers, selectors, readers, tests/docs | Intent/readiness and response inventory stay jointly resolvable. |
| Version metric-set names and keys | Config, plan, writers, readers, tests/docs | Every proposed producer/consumer uses `run_group_id`; no mixed metric CSV schema. |

### Validation

Per edit: matching focused tests, CLI test for rule changes, Python lint/format. Falsifiers: intent-only experiment reads ready, missing or shared Wflow log, temporal differences accepted as common evidence, broken `run_group_id` joins, or differing full IDs across metric result/engine siblings. Exercise metrics-only reads of new-contract responses after temporary files are gone. Compare native responses and every requested metric with the independent pinned predecessor WF4 comparator; model-validator must return the numerical verdict. Run expensive gates at master boundary.

### Acceptance criteria

All new records resolve, logs attribute to runs, metric membership joins exactly, and no user-facing metric table uses `unit_id`.

### Output requirements

Report path/header examples, schema identity change, focused checks and numerical non-regression evidence.

### Completion record

P6 is complete subject to its phase commit. The implementation emits and reads
`simulation/2`, `response-inventory/2`, `metric-request/2`, `metric-plan/2`,
and `metric-set/2`, while retaining the predecessor readers and writers for
their dedicated fixtures. The metric reduction algorithms and allocation order
are unchanged; P7 owns the fresh-run numerical comparison against the pinned
predecessor comparator. Focused implementation evidence is
[`p6/implementation-record.md`](../../milestones/r12/implementation/evidence/p6/implementation-record.md).

### Task constraints

Honor the master brief's human gate and shared constraints. Preserve existing Wflow setting filenames.
