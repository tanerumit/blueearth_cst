---
title: "Finish Wflow model revisions design"
type: todo-item
status: blocked
effort: 2
area: wf1
branch: feat/model-upgrading
created: 2026-09-28
updated: 2026-10-11
queue: 5
---

> [!note] Overview
> **What changes** — Record and land the accepted design for expert-edited Wflow model revisions in workflow 1 and their selection by workflow 4.
> **Why it matters** — The reviewed contract fixes model attribution, evaluation evidence, and experiment provenance before implementation is complete.
> **What it takes** — Resume the parked branch, reconcile the later simplified handoff with the reviewed contract,
> and verify against current `main` before approved landing.

## Progress

*Blocked on contract reconciliation and approved landing.*

- [x] Review the recipe/direct-edit design and approve G1/G2 in September 2026.
- [x] Commit the accepted contract and review archive on `feat/model-upgrading`.
- [ ] Reconcile the later simplified handoff and existing implementation against current `main`.
- [ ] Verify and land; retain necessary evidence before closing this item.

## Resume handoff — 2026-10-11

Preserve `feat/model-upgrading` at `ce23c3680cbb5f367abac5b60e801b228806c908` (56 unmerged commits).
It contains import/draft/seal/recovery, recipes, optional evaluation, WF4 selection, tests and
controlled demonstrations. No worktree holds it; do not discard it.

On return, read the branch versions of `dev/tasks/t2609281102/implementation-progress.md` and
`simplified-model-handoff-draft.md` first. The later owner direction imports an externally completed
native model into `models/hydrology/wflow/<model-name>/`, with toolbox records under
`models/_engine/wflow/<model-name>/` and explicit WF4 `hydrology_model` selection. Its exact contract
remains draft; code largely implements the earlier lifecycle.

Resume this existing branch through the managed session lifecycle. Compare with current `main`;
reconcile numbered experiments, prefixed run/group IDs, current schemas and plotting interfaces.
Classify reusable implementation versus superseded behavior and unrelated planning changes before
editing or merging. Revalidate contracts/execution; synthetic demonstrations do not establish fitness.

Branch evidence: `dev/reference/contracts/expert-model-revisions.md` and its sibling
`expert-model-revisions-review/`; task review checkpoint: `dev/tasks/t2609281102/status.md`.
