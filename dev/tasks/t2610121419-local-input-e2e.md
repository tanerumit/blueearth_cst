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
> **Why it matters** — Repeated remote acquisition slows validation when acquisition code is unaffected.
> **What it takes** — Stage and validate inputs, preserve downstream coverage, and measure the actual speedup.

## Progress

- [ ] Profile the existing rapid E2E run and identify acquisition versus compute costs.
- [ ] Stage compatible CMIP6 raw slices first; retain normal reduction and change-factor computation.
- [ ] Stage historical climate and spatial sources with complete rapid-case coverage and local catalogs.
- [ ] Add bundle provenance, checksums and compatibility checks; fail without remote fallback.
- [ ] Add test-e2e-local using the owned runner, fresh outputs and shared deliverable assertions.
- [ ] Compare downstream outputs and timings against a matched acquisition-inclusive run.
- [ ] Document coverage exclusions, bundle refresh and eligibility in the validation ladder.

## Scope and acceptance

Reuse source inputs only: regenerate historical extracts, the hydrological model, scenarios and
simulations. Keep the input bundle outside Git; preserve variables, units, calendars and sufficient spatial buffers.

The local gate is intended for changes that leave acquisition unaffected. Retain acquisition-inclusive
checks for source addressing, catalog adapters, acquisition windows, clipping and cache identity.
Retain the existing release and milestone gate initially.

The expected acquisition-related speedup is inferred from the current input dependencies, not measured
in this assessment. Julia startup and simulation costs remain. Reuse staging machinery from the related sample-bundle task where appropriate.

## Refs

- `tests/test_workflow_end_to_end.py`
- `dev/scripts/stage_cmip6.py`
- `dev/reference/validation-ladder.md`
- [Sample dataset bundle](t2608191733-ship-a-sample-dataset-bundle-so-a-user-needs-no-deltares-p-drive.md)
