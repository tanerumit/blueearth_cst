---
title: Improving repo-wide documentation and instructions
type: todo-item
status: active
effort: 2
area: docs
queue:
doc: dev/tasks/t2610211349/documentation-inventory-2026-10-26.md
created: 2026-10-21
updated: 2026-10-26
---

> [!note] Overview
> **What changes** — Improve repository documentation and instructions for users, developers, and agents.
> **Why it matters** — Scattered guidance and stale links obscure supported behavior and authoritative sources.
> **What it takes** — Agree priorities, revise guidance, and check links and examples; depth remains to be scoped.

## Progress

Next: Review document purposes, audience boundaries, and unintended repetition using the file inventory.

- [x] Map the documentation landscape — retained the structural review dated 2026-10-21.
- [x] Repair onboarding entry points — three source documents landed at `2945a397`; site build passed.
- [x] Inventory in-scope documentation by audience — 122 files; coverage and relative links checked.
- [ ] Review document purposes and boundaries; identify unintended repetition and redundancy.
- [ ] Audit selected guidance against current implementation and authoritative sources.
- [ ] Revise documentation and instructions, resolving stale references and duplication.
- [ ] Verify affected links, examples, and rendered pages as appropriate.

## First pass and work location

Owner-approved first pass: `README.md`, `docs/README.md`, and `docs/guide/quick-start.md`.
Audit the onboarding journey against implementation, repair stale guidance and links, and verify
commands, paths and examples. Necessary adjacent guide/index link corrections are included; broader
documentation and agent-instruction revisions remain unscoped.

- First pass complete: commit `1f5228f2`, landed on main at `2945a397`; session-2 is detached and free.
- Worker: `technical-writer-docs`; Herdr `cst · s2`, agents pane `w9:p1`.
- Explicit allocation: GPT-6 Sol, medium effort; bounded documentation repair with concrete checks.
- GPT-6.1 Sol was proposed but absent from the local CLI model catalog; GPT-6 Sol was selected instead.
- Fresh conversation: `01a1659a-f6fd-7ea0-bc81-44c130dfa535`; preflight confirmed no earlier user task.
- Model/effort verified in UI before assignment. The effort override selects embedded Codex mode;
  Herdr remains the tracking surface because shared-server discovery does not list this worker.
- Verification: worker reports `pixi run --frozen docs-build` passed on the final candidate.
- Coordinator confirmed commit ancestry and unchanged document contents between candidate and merge.
- Full workflow execution was not performed; examples require external data, network and compute.
- Owner-approved landing completed; broader documentation work remains open. Nothing was pushed.
- Scratch: session-2 :: `.tmp/tasks/t2610211349/`; no shared runtime or production output mutations.

## Inventory pass (2026-10-26)

Saved the scoped file register grouped by audience, with generated/external surfaces and embedded
documentation identified separately. Verified 122 unique entries against tracked paths and checked all
122 relative links. This pass does not assess content accuracy or decide consolidation.
Scope revised at owner request: exclude dev/tasks/, dev/reference/ (requested as dev/references/),
and dev/records/. The inventory is retained here as task evidence.

## Refs

- [Documentation inventory by audience](t2610211349/documentation-inventory-2026-10-26.md).
- [Documentation landscape review](t2610211349/documentation-review-2026-10-21.md).
- The initial review is an inventory, not a page-by-page accuracy audit.
