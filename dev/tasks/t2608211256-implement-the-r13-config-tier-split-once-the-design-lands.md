---
title: Implement the R13 config tier split once the design lands
type: todo-item
status: blocked
branch: feat/config-modularization
effort: 2
area: config
origin: R13
queue:
created: 2026-08-21
updated: 2026-08-21
---

> [!note] Overview
> **What** — Split the monolithic project config into a T1 project file carrying closed {enabled, config_path} workflow stanzas plus per-workflow T2 files, composed by a shared loader so the in-memory config shape is unchanged. Ships a report-only split_project_config.py that emits proposed T1+T2 into a staging directory, migration docs, and the parse-time shared-seam checks (D-9.1).
> **Why** — The design is being reviewed in dev/working/design-runs/config-modularization/ (stage 6, revision r2, one external round done). Implementation is blocked until G2 approves design-vN and stage 7 lands it under dev/milestones/r13/. Boarding it now clears the debt logged in that run's observations.md, where the note was deferred because dev/tasks sat inside another lane's claim.
> **Effort** — large

## Progress

- [ ] <first step>
