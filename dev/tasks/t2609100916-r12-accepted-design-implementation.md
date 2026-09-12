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
updated: 2026-09-12
---

> [!note] Overview
> **What** — Implement the accepted design through the prepared feasibility/baseline, contract, durable-handoff and workflow-extraction phases.
> **Why** — P0 through P3 are accepted. Full normalized-B qualification completed and its independent audit passed, but scientific criteria failed: only 3/24 baseline accuracy cells pass, all six current n=18 cells fail, and translation has 30 numerical failures plus one validity change. An owner method ruling is required; R12 remains unsealed.
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
- [x] Verify adapter-backed collection claim, publication, reading and reuse.
- [x] Complete P2 production handoffs, exact resolution, metrics-only and scientific/software acceptance.
- [x] Complete P3 workflow/config/runner extraction and repeat final-entry-point gates.
- [x] Execute implementation only within authorized scope.
- [x] Obtain owner acceptance of the reviewed GF15 benchmark criteria on 2026-09-12.
- [x] Execute and review the approved GF15 benchmark: all 132,000 fits complete; scientific criteria failed.
- [x] Obtain owner approval for a bounded fitting-stability and sample-size investigation on 2026-09-12.
- [x] Complete the approved investigation: all 132,000 retained fits inspected, 186 exact traces, causes and limitations recorded.
- [x] Obtain owner approval for status-only and normalized-fitting candidates on the same 186 diagnostic cases on 2026-09-12.
- [x] Complete and review 372 candidate fits: A preserves raw results; B passes all 144 both-accepted translation pairs; both refuse six extreme fits.
- [x] Obtain owner approval for B-only full qualification on the original matrix on 2026-09-12.
- [x] Execute and independently assess B-only full qualification: 132,000 fits complete; audit passed, scientific qualification failed.
- [ ] Obtain any required method or production-integration ruling after full qualification.
- [ ] Complete the separately documented standing baseline/tree and milestone-seal gates.

## Refs

Full normalized qualification completed on 2026-09-12 in 36.1 minutes: 132,000
fits, 144,000 quantiles and 120,000 translation pairs. B accepts 131,922 fits and
refuses 78 optimizer-budget failures. All cells meet the 95% valid-fit criterion,
but only 3/24 baseline scale cells and 6/72 eligible scale-plus-relative cells
pass; all six `n=18` baseline cells fail. Translation outcomes are 119,899
numerical passes, 30 numerical failures, 70 both-refused pairs without numerical
proof and one validity change. Maximum both-accepted paired difference is
`4.5263e-6`, above the unchanged `1e-6` criterion; 106/120 translation cells pass.
The 186 embedded B cases replay exactly. The independent audit verifies every
fit, quantile, pair and cell decision; prior evidence and criteria remain exact.
See [full qualification handoff](../milestones/r12/implementation/evidence/gf15-normalized-qualification/scientific-handoff.md).
Normalization improves conditioning but does not establish accuracy adequacy.
No production integration, criterion change, screening change or seal follows.

Full normalized qualification released on 2026-09-12: owner replied "yes i approve"
to B-only execution of all 132,000 fits and 144,000 primary quantiles using the
original retained samples and unchanged criteria, with no production integration.
The bounded comparison is committed as `743a4d24`. New evidence belongs under
`evidence/gf15-normalized-qualification/`; all prior evidence remains immutable.
Refusals count against full draw denominators, and both-refused translation
pairs remain distinct from numerical-equivalence successes. No fallback,
optimizer retuning, screening change or criterion change is authorized.

Candidate comparison completed on 2026-09-12: each candidate ran the same 186
fits and 225 primary quantiles. A reproduced every original raw result and
passed 2/144 both-accepted translation comparisons; B passed 144/144, with maximum
paired scale-error difference `2.3892e-13`. Each refused six optimizer-budget
failures; the three both-refused witness pairs provide no numerical-equivalence
proof. Maximum accepted B estimate change was about 0.001597 generating-scale
units. See [candidate handoff](../milestones/r12/implementation/evidence/gf15-candidates/scientific-handoff.md).
The subset supports a full qualification attempt for B, not an adequacy claim.
No full matrix, production integration, criterion change or fallback was run.

Candidate study released on 2026-09-12: owner replied "yes I approve. proceed to
next step" to the status-only wrapper and normalized-fitting comparison on the
same 186 cases, with unchanged criteria and no production integration. The
approved normalization uses sample mean and population standard deviation
(`ddof=0`), followed by mapping fitted parameters and quantiles back. No fallback,
changed optimizer settings, new draws or full qualification matrix is included.
The investigation is committed as `0e1a85b9`; new evidence belongs under
`evidence/gf15-candidates/`.

Investigation completed on 2026-09-12: all 180 fixed-grid traces reported
optimizer convergence, while all six extreme-witness traces exhausted 600
function evaluations. The parameters and quantiles replay exactly; the current
parameter-only fitting interface conceals those termination failures. The
percentage-based initial simplex also changes under location translation.
All six `n=18` accuracy cells still fail after a descriptive exclusion of the
largest 1% of absolute errors; this is not a replacement acceptance test or a
complete decomposition of sampling and optimizer error. See the
[investigation handoff](../milestones/r12/implementation/evidence/gf15-investigation/scientific-handoff.md).
The next decision is a reviewed candidate-method study, not another approval of
the original benchmark or a production change inferred from this diagnosis.

Investigation released on 2026-09-12: owner replied "yes i approve it" to the
recommended bounded investigation with production behavior unchanged. The
failed benchmark is committed as `2c9a0a30` and remains immutable. New diagnostics
belong under `evidence/gf15-investigation/`; they examine the retained failure
witnesses, fitting behavior and finite-sample accuracy without executing a new
estimator qualification or changing scientific thresholds.

GF15 completed on 2026-09-12: all 144,000 quantile records and 132,000 fits
are retained. Independent review verified all cell decisions and 36 exact fit
replays. Only 3/24 baseline scale cells pass; all six current `n=18` cells fail.
Translation deviations exceed `1e-6` in 118,457/120,000 pairs; all fits remain
valid. See [scientific handoff](../milestones/r12/implementation/evidence/gf15/scientific-handoff.md).
This is the new blocker under accepted design section 7.5, not a request to
reapprove the original criteria. Production estimators, screening policy,
immutable metric sets and the standing baseline are unchanged.

Read-only [standing seal checks](../milestones/r12/implementation/evidence/standing-seal-status.md)
also confirm that the local legacy fixture is not a successor baseline: no
retained metric plan, two stale config snapshot paths and 75 unmapped paths.
Fresh P3 inventories/crosswalks remain accepted; R12 remains unsealed.

GF15 released on 2026-09-12: owner replied "yes i approve. Proceed to next step"
to the reviewed criteria linked in the P3 completion handoff. Master Gate 2 is
discharged for those exact criteria. P3 is committed as `868c4b7c`. The existing
Astra model-validator owns the bounded benchmark and its scientific report;
estimator changes and post-result criterion changes remain outside this approval.

P3 final execution update, 2026-09-12: both fresh generation interfaces passed
37/37 jobs and both simulation interfaces passed 25/25; physical offline metrics
passed three jobs. All 32 final reuse/refusal/selection checks passed. Astra
accepted GF9/GF27/GF28/GF31 scientific preservation. Both output inventories and
the notebook reader/analysis cells pass. Final lint/format pass; the final full
suite passed 3,705 tests, with 15 skipped and one expected failure. See
`dev/milestones/r12/implementation/evidence/p3/acceptance.md`. GF15 benchmark
criteria required owner acceptance under Master Gate 2; the approval above
clears that blocker. No milestone-seal claim. The session branch remains assigned to R12.

P3 started on 2026-09-11 under the owner's continuation instruction. Configuration
migration, successor entry points and operation isolation are being implemented.
The first generation smoke completed; 20 migrated CLI checks passed. These are
iteration checks, not GF-9 or final acceptance. Scratch and preserved P2 code:
`.tmp/scratchpad/2026-09-11_0010/`. The atomic landing remains uncommitted until
the final reference sweep, scientific handoffs and software gates pass.

P3 resumed on 2026-09-11. The old workflow/current seeds/template are retired in
the working diff; successor rules are fully numbered. Runtime targeted gate:
127 passed; config/runner gate: 287 passed with two scanner failures, both fixed
and verified by a 20-test rerun. Lint, format and compilation passed. The final
full suite is running. Guides, contract references, notebook and stage diagram
are being migrated with the runtime.

The development GF-9 comparator reports 616 exact Class-A/B rows and independent
Class-C publication/pooled-mean agreement. Its earlier Class-C failure compared
the mean of rounded publications with a rounded pooled mean; the corrected
comparison preserves the accepted raw mean relation and records the publication
rounding delta separately. Astra review confirmed this follows accepted criteria;
final fresh-run provenance and named scientific acceptance remain pending.

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

## P2 collection lifecycle — 2026-09-11

- Added fresh in-process collection claims, exclusive payload writes, atomic
  ready publication, complete generic stochastic inventory checks, mandatory
  descriptor extraction callbacks, portable consumer reads and explicit live-input
  producer reuse checks. Source planning and production readers remain unbound.
- Combined identity/collection/row/provider tests: 112 passed. Lint,
  format-check and compilation passed. Read-only Python-engineer review accepted
  the infrastructure scope after reproduced path-alias and driver-validation
  findings were fixed. No production or scientific acceptance is claimed.
- Evidence and retained-byte example:
  `dev/milestones/r12/implementation/evidence/p2/collection-lifecycle.md`.
- Next: bind real forcing/ancillary descriptor extraction and package the
  preparation closure for all supported sources, obtain the named scientific
  handoff, and implement source planning/resolution and current-WF3 integration.

## P2 acceptance — 2026-09-11

- Completed current-WF3 collection, frozen simulation/native response, metric-set
  and metrics-only integration. Exact project/explicit resolution, reference-aware
  retention, forced preservation and stale-plan repair have executable evidence.
- Current-carrier GF-29/GF-30, bounded GF-31 and GF-32 passed. Two complete
  experiments share one collection and simulation identity. Offline metrics-only
  produced a new set without live model/data/configs or Julia.
- Named scientific handoff accepted 14 exact forcing files, 126 exact native
  response series and all 756 metric keys, including independent Class-C checks.
- Final full suite: 3,657 passed, 9 skipped, 1 xfailed; final CLI: 20 passed;
  lint and formatting passed. No standing-baseline or GF-15 benchmark claim.
- Acceptance/evidence: `dev/milestones/r12/implementation/evidence/p2/acceptance.md`.
- Next phase is P3; its entry-point/config/runner migration remains unstarted.

## Improvement candidate captured during P2

Implemented with owner approval in the canonical brain skill, v0.7.0,
commit `bf032d70`. Agent-system status and reference word budgets passed;
the repository-wide strict check retained unrelated findings. The capture below
records the original finding; vendored project skills were not edited.

- Target: `python-discipline` skill, `references/hazards.md`, Data integrity.
- Gap: reserved output names can be bypassed by Windows case/trailing-dot/space
  aliases or an internal symlink even when lexical traversal is rejected.
- Proposed rule: compare resolved reserved paths using platform path equality;
  reject nonportable Windows aliases before writes and confine the ready marker
  itself before reading it. Add discriminating alias tests for immutable outputs.
- Evidence: tests reproduced marker creation through `COLLECTION.JSON` and an
  internal symlink, plus acceptance of trailing-dot/space and device-name paths;
  an external ready-marker symlink also bypassed the initial consumer check.
- Scope: applies to immutable manifests, lock files and other reserved outputs
  across filesystem-backed tools. No skill or role files changed.
