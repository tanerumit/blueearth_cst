---
title: "R code has no tests"
type: todo-item
status: active
effort: 1
area: testing
queue: 22
created: 2026-08-07
updated: 2026-10-07
---

> [!note] Overview
> **What changes** — The R layer has no test infrastructure; Python helpers carry the coverage.
> **Why it matters** — Decided at the start of R5, not overlooked — but it means an R-side regression has no gate at all.
> **What it takes** — Nothing for now. Pick it up when the R code grows beyond the weather-generator wrappers, or when an R-side bug ships.

## Progress

- [x] Check whether the condition in What it takes has happened — yes (2026-10-07): three R-side bugs
  shipped and were caught only by WF3 runs (`19283626`, `cfadee4c`, `a39c024b`). The entry was also
  stale: `test_r_scripts.py` (parse), `test_r_log_row.py` and `test_read_member_grid.py` already
  existed, on a pytest + `Rscript -e` pattern needing neither weathergenr nor testthat.
- [x] Extract the weathergen rules' inline decisions into `blueearth_cst/weathergen/member_helpers.R`
  and test them in `tests/test_weathergen_member_helpers.py` — `27c42da0` on `chore/maintainance`.
  Changes WF3 generation ids (the R files are in the generation identity); accepted by the owner.
- [x] Land — `f3a63dd5` on `main` (2026-10-07). `test-e2e` SKIPPED (P: mirror unreachable), so the
  owner accepted a narrower check instead: both scripts run from `main` and from the branch on the same
  `test_rapid` inputs and seed with real weathergenr 2.0.1, all four output netCDFs xarray-identical.
  `test-fast` green apart from a timing flake in `test_run_workflows.py` (passes alone). Re-run
  `test-e2e` the next time P: is mounted.

## Refs

- Migrated from `dev/followups.md` on 2026-08-07, when the board replaced it. Prose below is that
  entry verbatim; it is the reproducible context, not a summary.
- No `origin` recorded. It was migrated from the roadmap-carryover "Minor open items" section. The
  prose says the call was made at the start of R5, which dates the *ruling*, not an owning milestone
  for the work.

## Detail

**R testthat coverage.** Decided at the start of R5 — Python
helpers only by default; adding R testing infrastructure is a
separate call.
