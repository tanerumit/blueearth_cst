---
title: "R code has no tests"
type: todo-item
status: backlog
effort: 1
area: testing
queue: 22
created: 2026-08-07
updated: 2026-10-05
---

> [!note] Overview
> **What changes** — The R layer has no test infrastructure; Python helpers carry the coverage.
> **Why it matters** — Decided at the start of R5, not overlooked — but it means an R-side regression has no gate at all.
> **What it takes** — Nothing for now. Pick it up when the R code grows beyond the weather-generator wrappers, or when an R-side bug ships.

## Progress

- [ ] Check whether the condition in What it takes has happened

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
