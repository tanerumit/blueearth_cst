---
title: Central configuration and portable workflow bundles
type: todo-item
status: active
effort: 2
area: workflows
doc: dev/tasks/t2610221058/design.md
queue:
branch: feat/central-config
created: 2026-10-22
updated: 2026-10-22
---

> [!note] Overview
> **What changes** — Keep configuration central and add portable WF2 bundles with result-local diagnostics.
> **Why it matters** — Transfer results with provenance while keeping configuration easy to browse.
> **What it takes** — Estimated 4-7 days for WF2; runner resume and other workflows are separate scope.

## Progress

- [x] Capture agreed setup — linked brief preserves central configuration and explicit portable export/import.
- [x] Define the WF2 bundle, import compatibility rules, and diagnostic ownership ([design](t2610221058/design.md)).
- [x] Retain WF2 diagnostics beside outputs without losing successful-production attribution
  (`d31df42a`; identical rewrites `316252ab`).
- [x] Implement portable export and validated import with conflict protection (`94887b4d`, `381b5e39`, `96dcf2e0`).
- [x] Verify transfer, failure handling, and existing runner behavior; update authoritative documentation.
  Docs `98081bee`; [walkthrough](t2610221058/walkthrough.md): Ntoum transfer and real rapid
  run/no-op/plot-rerun sequence passed. Batch gate (`test-fast`, lint, format-check) owed before push.

## Work location

- Owner: session-1; branch: `feat/central-config`.

## Refs

- [Design decisions](t2610221058/design.md); [walkthrough](t2610221058/walkthrough.md).
- [Task brief](t2610221058/task-brief.md).
- Origin: user discussion of transferring Ntoum WF2 results between machines; no milestone assigned.
