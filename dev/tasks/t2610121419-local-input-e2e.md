---
title: Add local-input E2E tests for all five workflows
type: todo-item
status: active
effort: 2
area: validation
queue: 1
created: 2026-10-12
updated: 2026-10-12
---

> [!note] Overview
> **What changes** — Add a local-input E2E mode running all five workflows from staged data into fresh outputs.
> **Why it matters** — Repeated P-drive and network reads slow validation when acquisition code is unaffected.
> **What it takes** — Stage and validate inputs, preserve downstream coverage, and measure the actual speedup.

## Progress

- [ ] Profile the existing rapid E2E run and identify acquisition versus compute costs.
- [ ] Stage compatible CMIP6 raw slices first; retain normal reduction and change-factor computation.
- [ ] Stage historical climate and spatial sources with complete rapid-case coverage and local catalogs.
- [ ] Add bundle provenance, checksums and compatibility checks; fail without remote fallback.
- [ ] Add test-e2e-local using the owned runner, fresh outputs and shared deliverable assertions.
- [ ] Compare downstream outputs and timings against a matched acquisition-inclusive run.
- [ ] Cover fetching with focused tests; document local/live gate eligibility and bundle refresh.

## Scope and acceptance

Reuse source inputs only; regenerate extracts, models, scenarios and simulations. Keep the bundle
outside Git, preserving variables, units, calendars and spatial buffers.

Use local-input E2E for routine validation, with focused fetching tests when acquisition code changes.
Keep live acquisition opt-in for catalog, addressing, window, clipping and cache changes. Document
that unit tests cannot establish live data availability or detect every upstream format change.

Define release/milestone eligibility and update the ladder and repository instructions together.
Existing gates apply until that policy changes.

Speedup is inferred, not measured; Julia startup and simulation costs remain. Reuse sample-bundle
staging where appropriate.

## Current evidence

Staging prerequisite committed as `a52e398c`: preserve FlatGeobuf outputs and optionally retain empty
vector layers. Checks: 63 staging/incremental/CMIP tests passed; the remaining worker-pool test passed
with named-pipe access. `pixi run lint` and `pixi run format-check` passed. No local E2E mode exists yet.

The pinned catalog requires five FGB sources; the existing local mirror uses older GPKG paths.
Stage exact pinned sources with unchanged adapters, full 2000–2016 history and seven native ERA5
variables. Confirm reservoir overlap against the pinned FGB before claiming no remote JRC access.

All four existing CMIP raw slices match current catalog/index components and the fresh P-drive
delineation's polygon fingerprint (`be6ed1c802ba…`). They fail the standing rapid polygon fingerprint;
its symmetric-difference area is about 3.15e-15 degree². Preserve pinned source formats; do not restamp
caches or reuse generated regions. Recipe and coverage probes remain in task-owned scratch in session-1.

The fresh acquisition-inclusive profile started at `c438df08` and failed in WF0's CHIRPS extraction
with `RuntimeError: NetCDF: HDF error`; WF1–WF4 did not run. Region delineation took 18m29s; WF0 stopped
after 31m. This is partial timing evidence, not a successful E2E gate or measured speedup.
Next: diagnose the CHIRPS source read and stage the pinned local bundle, then repeat matched runs.

## Refs

- `tests/test_workflow_end_to_end.py`
- `dev/scripts/stage_cmip6.py`
- `dev/reference/validation-ladder.md`
- [Sample dataset bundle](t2608191733-ship-a-sample-dataset-bundle-so-a-user-needs-no-deltares-p-drive.md)
