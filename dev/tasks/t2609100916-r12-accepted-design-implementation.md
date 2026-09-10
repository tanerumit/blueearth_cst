---
title: Implement the accepted R12 workflow design
type: todo-item
status: backlog
branch: feat/wp3-improvements
effort: 2
area: wf3
origin: R12
queue:
created: 2026-09-10
updated: 2026-09-10
---

> [!note] Overview
> **What** — Implement the accepted design through the prepared feasibility/baseline, contract, durable-handoff and workflow-extraction phases.
> **Why** — The reviewed design is accepted; runtime feasibility, numerical migration and scientific validation remain unexecuted.
> **Effort** — large

## Progress

- [x] Reviewed v6 accepted by owner on 2026-09-10.
- [x] Prepare phased implementation briefs and map every GF-1..32 gate.
- [x] Inspect source/environment readiness and specify feasibility/baseline prerequisites.
- [ ] Execute P0 synthetic feasibility tests and capture the fresh pre-change snapshot.
- [ ] Execute implementation only within subsequently authorized scope.

## Refs

- Accepted design: `dev/milestones/r12/wf3-simulation-identity-design.md`.
- Preparation handoff: `dev/milestones/r12/wf3-simulation-identity-task-brief.md`.
- Immutable review evidence: `dev/milestones/r12/wf3-simulation-identity-review/`.
- Class-B fit intervals remain a disclosed accepted limitation; review if an
  assessment needs uncertainty intervals to distinguish response gradients from
  estimator noise. GF-15's benchmark does not establish screening-policy validity.

## Preparation completed — 2026-09-10

- Master/phase index: `dev/milestones/r12/implementation/master-brief.md`.
- Readiness and raw check output: `dev/milestones/r12/implementation/readiness.md`.
- Gate ownership/falsifiers: `dev/milestones/r12/implementation/validation-map.md`.
- Environment check and baseline recorder help passed; no successor feasibility,
  numerical comparison or model execution has run. The implementation item stays
  in backlog; P0's P2b fixture is the first development task.
