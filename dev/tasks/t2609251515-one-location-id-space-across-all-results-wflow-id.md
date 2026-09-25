---
title: One location id space across all results (wflow_id)
type: todo-item
status: active
effort: 1
area: results / locations
origin: gabon-ntoum-v3 review (2026-09-25)
queue:
created: 2026-09-25
updated: 2026-09-25
---

> [!note] Overview
> **What** — Key every derived result by the location registry's wflow_id (e.g. 1010): WF4 prefers the gauge column over a coincident outlet (reverse _PREFERRED_POINT_MAP in wflow_response_reader), relabels subcatchment outputs (aet/gwr 101..104) to each subbasin's primary wflow_id, and WF1's output_q/aet/gwr.csv get the same relabel with the duplicate outlet column dropped. Native Wflow CSVs keep their headers. Correct t2609151118's claim that outlet-wins matches WF1.
> **Why** — gabon-ntoum-v3 metric sets mix three id spaces (q: 101,1020,1030,1040; aet/gwr: 101..104) while WF1 figures use 1010..1040. User wants one consistent 4-digit set. Changes metric-set contents: needs a baseline re-record and a PR (reviewed data contract).
> **Effort** — small

## Progress

- [x] WF4 labels every series by wflow_id via shared/native_locations (a39d3044, e8ba712a)
- [x] WF1 output_q/aet/gwr.csv relabelled, duplicate outlet column dropped (7e18b5b5)
- [x] Rapid smoke: WF1 tables and WF4 q/aet/gwr metric sets all on 1010..1040
- [x] test_local regenerated, baseline re-recorded (only diff: q 101 -> 1010), contract integration tests green
- [ ] test-full, then PR
