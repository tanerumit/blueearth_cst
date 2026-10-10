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
> **What it takes** — Small: update scaffold defaults, focused tests and live docs; coordinate case guidance.

## Progress

- [x] Include in the combined implementation brief — see the link below, 2026-10-10.
- [ ] Remove `active` from `scripts/create_case.py` defaults/previews; update focused tests.
- [ ] Update `docs/site/guide/running.qmd` and case starter guidance for user-selected output paths.
- [ ] Preserve existing output trees and historical evidence paths; require no folder migration.

## Decision

`active/` is an optional directory convention, not an automatic versioning mechanism. The user will manage
folder structure and choose a separate output directory when retaining another assessment version.
Do not introduce automatic archiving, variant promotion, or a replacement mandatory folder convention.

Current implementation: `scripts/create_case.py` sets outputs to `runs/<slug>/active/`.
Related task: `t2610032349` addresses experiment naming within the chosen output root.
The [combined task brief](t2610032349/task-brief.md) assigns both changes, with separate acceptance.
New scaffolds will use `runs/<slug>/`; existing `active/` trees and user-selected paths remain valid.
