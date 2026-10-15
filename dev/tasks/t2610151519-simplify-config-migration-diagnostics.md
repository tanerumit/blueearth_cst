---
title: Simplify obsolete config migration diagnostics
type: todo-item
status: backlog
effort: 1
area: config
queue: 10
created: 2026-10-15
updated: 2026-10-15
---

> [!note] Overview
> **What changes** — Remove unused migration metadata and simplify obsolete diagnostics while preserving
> current configuration validation.
> **Why it matters** — The converter is gone, but historical tables, verbose migration instructions, and
> stale placement advice remain in runtime code.
> **What it takes** — Estimated 2-4 hours including affected tests and DAG checks. Keep schema_version and
> retired-key rejection; exclude schema-validation redesign and retained-output compatibility changes.

## Progress

- [ ] Remove RELOCATED_KEYS and its dedicated assertions after confirming no production readers.
- [ ] Simplify migration-era commentary and diagnostics; point ordinary errors to current documentation.
- [ ] Correct WF2 water-year advice to climate.water_year_start.
- [ ] Update affected tests and documentation; retain schema_version and the 36-key retirement checks.
- [ ] Run focused config-loader, runner and affected DAG checks, plus required Python lint/format checks.

Scope excludes schema-validation redesign, target-alias removal and retained-output compatibility changes.
The converter scripts and mapping are already absent; the loader retains 36 retired-key entries.
Do not remove rejection coverage in the course of shortening migration instructions.
