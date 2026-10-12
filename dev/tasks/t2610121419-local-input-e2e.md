---
title: Add local-input E2E tests for all five workflows
type: todo-item
status: backlog
effort: 2
area: validation
queue: 9
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

## Refs

- `tests/test_workflow_end_to_end.py`
- `dev/scripts/stage_cmip6.py`
- `dev/reference/validation-ladder.md`
- [Sample dataset bundle](t2608191733-ship-a-sample-dataset-bundle-so-a-user-needs-no-deltares-p-drive.md)
