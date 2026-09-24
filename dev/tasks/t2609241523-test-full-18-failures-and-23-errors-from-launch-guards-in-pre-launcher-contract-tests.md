---
title: "test-full: 18 failures and 23 errors from launch guards in pre-launcher contract tests"
type: todo-item
status: backlog
effort: 1
area: tests
origin: wf3 generation bundle (2026-09-24)
queue:
created: 2026-09-24
updated: 2026-09-24
---

> [!note] Overview
> **What** — On main 4bf33e8d and 07a5a125: tests/test_region_rule.py, test_spatial_units_rule.py, test_climate_store_contract.py, test_climate_source_plot_contract.py, test_climate_store_freshness.py, test_member_catalog_rule.py, test_wf1_plot_outputs.py and test_cross_workflow_inputs.py[wf3] invoke snakemake directly and hit 'requires scripts/run_workflow.py for pre-parse source capture' (WF0/WF1) or 'WF3 requires the owned source or generation phase'. Update the tests to run through the owned launchers or provide the capture context.
> **Why** — test-full is the gate for shared/ and script: changes; a standing red tier hides new failures.
> **Effort** — small

## Progress

- [ ] <first step>
