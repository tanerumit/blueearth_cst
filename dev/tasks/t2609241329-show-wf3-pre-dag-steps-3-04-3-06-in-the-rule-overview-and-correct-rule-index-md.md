---
title: Show WF3 pre-DAG steps 3.04-3.06 in the rule overview and correct rule-index.md
type: todo-item
status: backlog
branch: wf3-improvements
effort: 1
area: wf3
origin: wf3 generation bundle (2026-09-24)
queue:
created: 2026-09-24
updated: 2026-09-24
---

> [!note] Overview
> **What** — The static-planning refactor moved 3.04 prepare_collection_sources, 3.05 initialize_scenario_collection and 3.06 prepare_weathergen_config into scripts/generate_scenarios.py (run_owned) ahead of snakemake, so the overview jumps 3.03 -> 3.07. Print them as overview rows marked as done before the DAG (numbers unchanged). Correct dev/reference/workflows/rule-index.md WF3 table to the code: rule names (after the t2609241251 rename), series/ not forcing/, and 3.11/3.12 gather steps as end-of-run handlers.
> **Why** — Domain experts read the overview as the pipeline; missing numbers look like skipped steps, and a stale rule-index is a defect per AGENTS.md.
> **Effort** — small

## Progress

- [ ] <first step>
