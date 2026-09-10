---
title: Implement the accepted R12 workflow design
type: todo-item
status: active
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
> **Why** — P0 and P1 are accepted. All three P1 scientific handoffs and the combined software gate passed; durable handoffs follow in P2.
> **Effort** — large

## Progress

- [x] Reviewed v6 accepted by owner on 2026-09-10.
- [x] Prepare phased implementation briefs and map every GF-1..32 gate.
- [x] Inspect source/environment readiness and specify feasibility/baseline prerequisites.
- [x] Release P0 execution and recheck source/environment readiness on 2026-09-10.
- [x] Prove synthetic P2b composition in all three states, with dry-run and real execution.
- [x] Execute P0 synthetic feasibility tests and capture the fresh pre-change snapshot.
- [x] Obtain named model-validator acceptance of P0 comparison evidence before P1.
- [x] Complete P1 logical contracts and the three model-validator handoffs.
- [x] Start P2 with verified pure collection identity primitives.
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
- Owner approved the mandatory simulation runner on 2026-09-10. Target validation
  precedes one Snakemake invocation; direct generation remains supported. Evidence:
  `dev/milestones/r12/implementation/evidence/p0/operation-target-feasibility.md`.
  This Gate 3 decision is discharged; replacement probes and the fresh pre-change
  snapshot completed. No new scientific criteria or method change was approved.
- Runner/checkpoint evidence passed (29 tests, then 2 affected lifecycle tests);
  CLI 20 passed, lint and format-check passed. WF1 completed 20 jobs and WF3 41.
  The isolated manifest recorded and checked four targets; the snapshot inventory
  hashes 242 artifacts. Stop: named model-validator acceptance before P1.
  Handoff: `dev/milestones/r12/implementation/evidence/p0/prechange-snapshot.md`.

## Improvement candidate captured during P0

Implemented with owner approval in the canonical brain skill, v0.6.1,
commit `56e950c1`; the capture below records the original finding.

- Target: `snakemake` skill, `references/rule-design.md`, Outputs And Failure Semantics.
- Gap: its `update(...)` rule covers pre-job deletion and successful forced reuse,
  but does not distinguish failed-job cleanup or Snakemake's timestamp refresh.
- Proposed rule: verify preserved bytes both on successful reuse and on named
  refusal; `update(...)` alone does not establish failure retention. Put checks
  that must preserve existing published artifacts before job scheduling and do
  not infer a content rewrite from a timestamp refresh.
- Evidence: P0's forced checkpoint probe retained bytes while mtime changed;
  mismatch raised inside the publication job caused output cleanup. The fixture
  was corrected to refuse an already-corrupt publication in read-only preflight.
  This concerns any Snakemake workflow revalidating persistent outputs, not CST
  science. No skill files were edited.

## P1 started — 2026-09-10

- Named Astra model-validator accepted P0 after independent integrity/config/model
  checks; evidence contains the verdict and its scope limits.
- Added pure scenario-row enumeration and configured ancestry/completeness checks;
  13 tests passed, repository lint and formatting passed. No runtime integration yet.
- Production binding is held at the unit-provenance gate: generated and prepared
  forcing carry inconsistent physical-unit labels. The next bounded step is to
  trace current transforms and obtain reviewed effective-unit interpretation.
  Preserve native bytes; numeric conversion or unresolved physics needs a method
  decision. Details: `dev/milestones/r12/implementation/phase-1-contract-extraction.md`.

- Unit trace reviewed and accepted for the existing ERA5 binding; hold discharged.
  Integrated provider wrappers into rules 3.11/3.12 with unchanged R operations.
  Real-R rehearsal: 14/14 forcing files byte-identical to the accepted reference.
  Row/provider tests: 16 passed; neutral response tests: 15 passed; CLI: 20 passed.
  Generation handoff: `dev/milestones/r12/implementation/evidence/p1-generation-handoff.md`.
  Simulator/metrics remain pending; no complete P1 or GF-9 claim.

## P1 acceptance — 2026-09-10

- Generation checkpoint: `11ea019e`. Simulator and metric adapters now route
  current WF3 through explicit run records, neutral responses and declarations.
- All three named model-validator handoffs accepted. One real ERA5 preparation
  matches P0 scientifically and its native CSV is byte-identical; all 14 response
  arrays/times and 686 current table values match. CHIRPS interpretation is
  code-derived, and E-OBS retains the pre-existing WF1 refusal.
- Final `test-full`: 3,473 passed, 9 skipped, 1 xfailed in 720.17 s. Combined CLI:
  20 passed; final focused metric/reader/dummy checks: 17 passed. Lint/format pass.
- P1 acceptance gate passed. P2 durable collections, simulation/response records,
  metric sets and metrics-only operation remain. GF-15 benchmarking still needs
  its stated review/owner criteria gate; no benchmark or milestone-seal claim.

## P2 started — 2026-09-10

- Owner instructed continuation after P1 acceptance. Added collection-canon/1
  encoding/reading, confined paths, scenario semantics and intent/revision hashes.
- Focused identity/row/provider suite: 60 passed; lint, format-check and compilation
  passed. Read-only Python-engineer review found no actionable identity defects.
- This is a foundation checkpoint only: no ready collections or runtime wiring.
  Next is immutable collection storage and complete validation, then portable
  preparation and the source checkpoint. See
  `dev/milestones/r12/implementation/evidence/p2/identity-foundation.md`.
