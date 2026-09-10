---
title: Implement the accepted R12 workflow design
type: todo-item
status: blocked
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
- [x] Release P0 execution and recheck source/environment readiness on 2026-09-10.
- [x] Prove synthetic P2b composition in all three states, with dry-run and real execution.
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
  numerical comparison or model execution ran during preparation.

## P0 execution started — 2026-09-10

- Owner instruction to continue with the next logical step releases P0 execution
  (Master Gate 1). The first bounded increment is the synthetic P2b fixture;
  production extraction remains sequenced behind P0's feasibility and snapshot gates.
- Source comparison against the accepted design baseline is unchanged; `main`
  is already an ancestor of the execution checkout (`123e91b1`). Environment
  check passed again with weathergenr 2.0.0 and Wflow present.
- P2b passed; see `dev/milestones/r12/implementation/evidence/p0/p2b-feasibility.md`.
  The operation/target probe then reached **Master Gate 3**: direct Wflow targets
  bypass metrics in simulation mode. Producer omission works in metrics-only,
  but conditional rules do not enforce the accepted target-pair exclusivity.
- Awaiting owner ruling on the proposed mandatory simulation runner versus
  relaxing the direct-command target restriction. Evidence and concrete fallback:
  `dev/milestones/r12/implementation/evidence/p0/operation-target-feasibility.md`.
  Checkpoint probes and the fresh pre-change snapshot are held at this gate.
