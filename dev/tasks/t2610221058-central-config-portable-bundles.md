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
  (`7a28671e`; identical rewrites `fd280b45`).
- [x] Implement portable export and validated import with conflict protection (`6d5220e3`, `434b0ccb`, `207f5620`).
- [x] Verify transfer, failure handling, and existing runner behavior; update authoritative documentation.
  Docs `0719c9be`; [walkthrough](t2610221058/walkthrough.md): Ntoum transfer and real rapid
  run/no-op/plot-rerun sequence passed. Batch gate (`test-fast`, lint, format-check) owed before push.

## Work location

- Owner: session-1; branch: `feat/central-config`.

## Refs

- [Design decisions](t2610221058/design.md); [walkthrough](t2610221058/walkthrough.md).
- [Task brief](t2610221058/task-brief.md).
- Origin: user discussion of transferring Ntoum WF2 results between machines; no milestone assigned.
