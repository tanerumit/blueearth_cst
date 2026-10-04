---
title: "Finish Wflow model revisions design"
type: todo-item
status: blocked
effort: 2
area: wf1
branch: feat/model-upgrading
created: 2026-09-28
updated: 2026-09-30
---

> [!note] Overview
> **What changes** — Record and land the accepted design for expert-edited Wflow model revisions in workflow 1 and their selection by workflow 4.
> **Why it matters** — The reviewed contract fixes model attribution, evaluation evidence, and experiment provenance before implementation is complete.
> **What it takes** — Design and review are complete; the accepted contract and review archive are committed on `feat/model-upgrading` and await approved landing.

## Progress

*Blocked on landing the branch evidence. The G1 and G2 design gates are complete; implementation continues separately on `feat/model-upgrading`.*

- [x] Scope full model revisions with HydroMT recipes and direct model edits.
- [x] Draft and scientifically review version 1; approve the G1 framing on 2026-09-30.
- [x] Revise the design, run risk and independent review, and close the findings.
- [x] Approve version 3 at G2 and promote the accepted contract and review evidence on the feature branch.
- [ ] After approved landing, verify the contract and review archive on `main`, preserve any needed task-sidecar evidence, then close this design item.

## Refs

- Accepted contract on the branch: `dev/reference/contracts/expert-model-revisions.md`; retained review evidence: `dev/reference/contracts/expert-model-revisions-review/`.
- `dev/tasks/t2609281102/status.md` records the completed review stages; the newer version remains on the feature branch until landing.
- `dev/tasks/t2609281102/implementation-progress.md` tracks continuing implementation on the feature branch. Its unfinished work is distinct from this completed design review.
