---
title: Pin CMIP6 variables independently when versions differ
type: todo-item
status: backlog
effort: 1
area: wf2
queue: 6
created: 2026-10-13
updated: 2026-10-22
---

> [!note] Overview
> **What changes** — Pin each variable when precipitation and temperature versions differ; preserve the
> shared-pin path for ordinary fetches.
> **Why it matters** — Avoid ambiguous wildcard reads and misleading warnings; make selection deterministic.
> **What it takes** — Scoped fetch changes, compatibility checks, cache handling, and performance benchmarks.

## Progress

- [ ] Preserve the shared-pin read and cache-hit paths for ordinary fetches.
- [ ] Select the newest indexed version per variable on the same grid; keep multiple-grid choices explicit.
- [ ] Validate spatial and time compatibility, report selected versions, and test failure cases.
- [ ] Record selected source paths and invalidate affected old caches without unnecessary global rebuilds.
- [ ] Benchmark ordinary and differing-version sources; check values and document runtime effects.

## Context

Code inspection: `series_identity.pinned_uri` requires the newest `pr` and `tas` paths to match;
otherwise `fetch_gcm_raw` warns and uses the wildcard catalog read. Example:
`FIO-QLNM/FIO-ESM-2-0 historical r1i1p1f1` has `pr: gn/v20191209` and `tas: gn/v20191115`.
Expected runtime effects of per-variable reads are inferred, not measured.

## Refs

- `blueearth_cst/projections/series_identity.py`
- `blueearth_cst/projections/fetch_gcm_raw.py`
- `tests/test_fetch_gcm_raw.py`
- `dev/reference/dev-validation.md`
