# Task Brief — P6 Simulation and metrics

### Context

Read `AGENTS.md`, [master brief](master-brief.md), [schema](../complete-run-output-schema.md) §§2, 7–8. P4/P5 supply the versioned collection consumed by WF4.

### Goal

Consolidate experiment machine records under one `_engine/` and publish user-facing responses and metric sets with the proposed filenames and columns.

### Non-goals

No Wflow-owned settings rename, model-physics change, altered metric definitions or old metric-CSV compatibility reader under D21.

### Allowed scope

Permitted: `blueearth_cst/experiment/simulation_record.py`, `response_inventory.py`, `metric_plan.py`, `downscale_climate_forcing.py`, the collection-reference reader in `scenario_collection.py`, `blueearth_cst/shared/cross_workflow_leaves.py`, `simulate_system.smk`, `scripts/simulate_system.py`, affected tests/docs. Re-measure actual consumers before edits. Forbidden: generated outputs and upstream Wflow/HydroMT.

### Required changes (checklist)

- [ ] Publish flat `_engine/simulation_intent.json` and `simulation.json`, with embedded frozen inputs and a completion marker after response verification.
- [ ] Keep Wflow run TOMLs in `run_settings/`, common temporal evidence once in `response_inventory.json`, and each native log under `output/_log/` with per-run attribution.
- [ ] Move metric machine records under experiment `_engine/metric_sets/<id>/`; keep `metric_run_lookup.csv` and `<token>_indicators.csv` under `results/metric_sets/<id>/`.
- [ ] Use headers `run_group_id,grain,run_id` and `metric,location,run_group_id,value`; align new config/intent capacity and width and metric-plan bundle fields with `run_group_id`, preserving padded values and allocation order.

### Commit plan

| Subject | Paths | Invariant |
|---|---|---|
| Version simulation records and paths | Writers, selectors, readers, tests/docs | Intent/readiness and response inventory stay jointly resolvable. |
| Version metric-set names and keys | Config, plan, writers, readers, tests/docs | Every proposed producer/consumer uses `run_group_id`; no mixed metric CSV schema. |

### Validation

Per edit: matching focused tests, CLI test for rule changes, Python lint/format. Falsifiers: intent-only experiment reads ready, missing or shared Wflow log, per-run temporal duplicates, broken `run_group_id` joins, or differing full IDs across metric result/engine siblings. Exercise metrics-only reads after temporary files are gone and old simulation readers outside D21. Run expensive gates at master boundary.

### Acceptance criteria

All new records resolve, logs attribute to runs, metric membership joins exactly, and no user-facing metric table uses `unit_id`.

### Output requirements

Report path/header examples, schema identity change, focused checks and numerical non-regression evidence.

### Task constraints

Honor the master brief's human gate and shared constraints. Preserve existing Wflow setting filenames.
