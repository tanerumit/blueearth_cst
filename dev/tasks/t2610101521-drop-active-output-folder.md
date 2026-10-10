---
title: Drop the active output folder convention
type: todo-item
status: backlog
effort: 1
area: config
queue: 8
created: 2026-10-10
updated: 2026-10-10
---

> [!note] Overview
> **What changes** — Drop the `active/` convention from scaffolding and guidance. Users choose their own
> `project.project_dir` or `--project-dir` and manage version folders themselves.
> **Why it matters** — User decision, 2026-10-10: `active/` adds unnecessary folder-management complexity.
> **What it takes** — Small: update scaffold defaults, focused tests and live docs; coordinate cst-cases guidance.

## Progress

- [ ] Remove the `active` suffix from `scripts/create_case.py` defaults and previews; update focused tests.
- [ ] Update `docs/site/guide/running.qmd` and cst-cases starter guidance to explain user-selected output paths.
- [ ] Preserve existing output trees and historical evidence paths; require no folder migration.

## Decision

`active/` is an optional directory convention, not an automatic versioning mechanism. The user will manage
folder structure and choose a separate output directory when retaining another assessment version.
Do not introduce automatic archiving, variant promotion, or a replacement mandatory folder convention.

Current implementation: `scripts/create_case.py` sets outputs to `runs/<slug>/active/`.
Related task: `t2610032349` addresses experiment naming separately; its `active_<date>` motivation may
need updating when the scaffold default changes.
