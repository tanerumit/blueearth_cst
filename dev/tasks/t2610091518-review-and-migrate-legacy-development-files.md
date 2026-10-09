---
title: Review and migrate legacy development files
type: todo-item
status: active
branch: chore/maintainance
effort: 1
area: maintenance
queue: 1
created: 2026-10-09
updated: 2026-10-09
---

> [!note] Overview
> **What changes** — Classify all 101 legacy files and produce a citation-aware migration plan before approved moves.
> **Why it matters** — Legacy working files mix active task material, retained evidence and exploratory scripts.
> **What it takes** — Review contents, copies, citations and retention constraints; apply approved placement changes and preserve original evidence.

## Progress

- [x] Inventory all 101 files, including sparse-excluded citations — complete; exact blobs verified.
- [x] Classify contents, archival copies and retention constraints — 101 dispositions recorded.
- [x] Commit the per-file migration plan on chore/maintainance — ebc53054.
- [x] Obtain approval for exact moves and deletions - approved 2026-10-09.
- [x] Apply approved batches with citation fixes and focused checks - 53 moved, 45 retired, three held.

## Refs

Review and exact per-file plan: commit `ebc53054` on `chore/maintainance`, under
`dev/tasks/t2610091518/`. Migration is complete on chore/maintainance; landing remains pending owner approval.

## Migration handoff

- [ ] Approve landing, run the integration gates, and close this migration task.
- [ ] Triage unresolved geographic findings against current evidence and existing task coverage.

Retained evidence: commit `deeda577` plus the completed record at
`dev/records/reviews/legacy-development-migration-2026-10-09.md` on the task branch.
All 101 original blobs, 44 archive counterparts and 34 citation occurrences were verified.
Focused link/sealed tests passed (38); repository lint and format checks passed.
The three held sources remain unchanged. No landing or push was performed.
