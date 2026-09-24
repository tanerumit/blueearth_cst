---
title: Rename WF4 rules to domain names, hide targets, renumber 4.01-4.10
type: todo-item
status: backlog
branch: workflow-rule-naming
effort: 1
area: wf4
origin: wf4 naming bundle (2026-09-24)
queue:
created: 2026-09-24
updated: 2026-09-24
---

> [!note] Overview
> **What** — Agreed 2026-09-24. Steps: 4.01 write_model_reference -> write_model_fingerprint; 4.02 check_model_reference -> check_model_unchanged; 4.03 freeze_wflow_simulation -> snapshot_simulation_inputs; 4.04 downscale_climate_realization -> downscale_scenario_series; 4.05 run_wflow(_batch_N) -> run_wflow_simulations; 4.06 publish_native_responses -> publish_wflow_outputs; 4.07 prepare_metric_plan -> prepare_indicator_plan (was 4.08); 4.08 publish_metric_set -> derive_system_indicators (was 4.09); 4.09 gather_logs (was 4.11); 4.10 gather_benchmarks (was 4.12). Targets get no number and join _PLAN_EXCLUDED_RULES: responses -> simulations_only, metrics -> simulations_and_indicators (keep old names accepted by scripts/simulate_system.py --target for one release). Rule names only: metric_sets/ and metric_requests/ folders unchanged (board separately if wanted). Update simulate_system.py, tests, rule-index.md, console samples, naming.md (add snapshot_/derive_ use as needed), migration note incl. old log/benchmark part names; test-full.
> **Why** — WF4 names are mechanics ('freeze', 'native responses', 'metric plan'), and its targets appear as numbered steps; domain experts read the overview as the pipeline, as for WF3.
> **Effort** — small

## Progress

- [ ] <first step>
