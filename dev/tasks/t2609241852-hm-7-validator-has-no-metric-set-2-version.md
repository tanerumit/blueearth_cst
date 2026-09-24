---
title: HM-7 validator has no metric-set/2 version
type: todo-item
status: backlog
effort: 1
area: tests
origin: wf3 identity bundle (2026-09-24)
queue:
created: 2026-09-24
updated: 2026-09-24
---

> [!note] Overview
> **What** — validate_hm7 (tests/test_interchange_contracts.py Layer 1 + 2) checks the metric-set/1 shape: unit_index.csv, declarations, indicator_tables, response_request.json, an 'evaluated' column. Current WF4 writes metric-set/2 (long tables metric/location/run_group_id/value + metric_run_lookup.csv), checked only by _read_metric_set_v2. The Layer-2 case is a named skip on a /2 tree. Decide: port HM-7 to /2, or retire it in favour of the reader's integrity checks.
> **Why** — The interchange contract for metric sets is no longer independently checked against a real tree.
> **Effort** — small

## Progress

- [ ] <first step>
