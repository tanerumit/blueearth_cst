---
title: Drop the active output folder convention
type: todo-item
status: active
effort: 1
area: config
queue: 1
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
- [x] Remove `active` from defaults/previews — toolbox `3bea47b9`; 16 focused tests pass.
- [x] Update toolbox and case starter guidance — toolbox `3bea47b9`, cases `cdaad63`.
- [x] Preserve existing trees — fixture preservation/link guards pass; no production outputs changed.

## Decision

`active/` is an optional directory convention, not an automatic versioning mechanism. The user will manage
folder structure and choose a separate output directory when retaining another assessment version.
Do not introduce automatic archiving, variant promotion, or a replacement mandatory folder convention.

Verified on `feat/minor-improvements`, pending toolbox landing: outputs default to `runs/<slug>/`.
Related task: `t2610032349` addresses experiment naming within the chosen output root.
The [combined task brief](t2610032349/task-brief.md) assigns both changes, with separate acceptance.
Existing `active/` trees and user-selected paths remain valid. Keep this task open until landing.

Combined naming acceptance also verifies independent allocation in an explicitly chosen `active/`
root (focused test passed). Final task-local evidence is indexed by the combined brief.
