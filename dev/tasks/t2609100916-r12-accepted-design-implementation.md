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
updated: 2026-09-13
---

> [!note] Overview
> **What** — Implement the accepted design through the prepared feasibility/baseline, contract, durable-handoff and workflow-extraction phases.
> **Why** — The original and owner-selected threefold accuracy policies both fail. The revised policy passes 124/144 cells and all n=18 baseline cells, but leaves 20 failed cells. A further owner method decision is needed; production integration and milestone sealing remain open.
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
- [x] Obtain owner authorization for a reviewed alternative-estimator proposal on 2026-09-12.
- [x] Draft the L-moment/PWM GEV proposal and obtain scientific review: approve, two minor clarifications, no blocking/major findings.
- [x] Obtain G1 selection of the concrete provisional L-moment GEV estimator on 2026-09-12.
- [x] Complete remaining design reviews, revision and G2 on 2026-09-12.
- [x] Prepare and accept the alternative-estimator design with existing criteria fixed; preserve all review evidence.
- [x] Finalize the accepted design/review archive and prepare the bounded Stage 1 readiness brief.
- [x] Obtain Stage 1 execution authorization on 2026-09-12 ("continue to Stage 1").
- [x] Complete Stage 1 readiness and obtain independent acceptance of attempt-2 on 2026-09-12.
- [x] Obtain Stage 2 execution authorization on 2026-09-12 ("continue" after the Stage 1 completion handoff).
- [x] Execute the complete alternative Stage 2 matrix after separate release; mechanically complete, observed accuracy gates fail.
- [x] Obtain Stage 3 release on 2026-09-13 ("Yes, proceed to independent assessment").
- [x] Complete Stage 3 independent assessment on 2026-09-13: exact audit passed; candidate failed fixed-matrix qualification.
- [x] Obtain owner selection of threefold scale/relative error limits on 2026-09-13.
- [x] Complete the versioned threefold-policy reassessment: 124/144 cells pass; the all-cell conjunction remains false.
- [ ] Obtain any required method or production-integration ruling after full qualification.
- [ ] Complete the separately documented standing baseline/tree and milestone-seal gates.

## Refs

The [accepted alternative-estimator design](../milestones/r12/gf15-alternative-estimator-design.md)
was approved at G2 on 2026-09-12, including recorded finding dispositions. The
[archived review run](../milestones/r12/gf15-alternative-estimator-review/status.md)
preserves four design versions, two external reviews, the full internal panel,
all 23 finding IDs and approved scoped verification. The next assignment is
[Stage 1 readiness](../milestones/r12/implementation/gf15-lmoments-readiness-brief.md),
released for execution on 2026-09-12. Before this release, no alternative candidate fitting, installation
or production integration has occurred; R12 remains unsealed.

Alternative-estimator proposal authorized on 2026-09-12: owner requested
"continue with the recomended option" after the full-B failure was committed as
`85d0b8b6`. The active [review run](../milestones/r12/gf15-alternative-estimator-review/status.md)
prepares a method proposal with primary-source support, serious alternatives and
an explicit qualification plan. Proposal/review authorization does not approve
fitting, dependency installation, production integration or altered criteria.

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

## Stage 1 alternative-estimator readiness released — 2026-09-12

Owner instruction "continue to Stage 1" overrides the brief's pending execution
state and authorizes its isolated dependency installation, implementation, fixed
controls and complete predecessor audit. Full qualification remains separate.
Allocation planned before dispatch: driver owns environment/provenance and task
integration; python-engineer owns adapter/oracle/harness/tests/fixed evidence;
model-validator independently judges the frozen handoff. Requested Astra medium
honors the owner's pin; effective worker settings are not separately reported.
Scratch: .tmp/scratchpad/2026-09-11_0010/gf15-lmoments-readiness/. Shared Pixi,
production and prior evidence remain read-only. No baseline/seal work is released.

Stage 1 iteration evidence: pinned isolated environment installed and verified;
all three original population controls pass; the complete 732-file/receipt D4
audit reports both unique 144,000-key sets. First full fixed numerical controls
pass 19 branch rows and 88 dual-precision normalized/physical CDF comparisons.
These are executor iteration results, not final independent readiness acceptance.
Behavioral discrimination, immutable replay and the final frozen run follow.

The first frozen run passed 44 tests, the complete input audit and fixed numerical
controls, but independent review found a D6 endpoint-rounding counterexample:
an optional CDF diagnostic could reject a valid rounded quantile. That attempt
is not accepted. Preserve its evidence; repair diagnostic support handling and
run a new frozen attempt with a discriminating regression before signoff.

**Stage 1 accepted — 2026-09-12.** The [signed scientific handoff](../milestones/r12/implementation/evidence/gf15-lmoments-readiness/results/independent/scientific-handoff.md)
accepts attempt-2 after resolving the endpoint diagnostic defect. All 45 focused
tests, three population controls, 19 branch controls and 88 dual-precision
normalized/physical comparisons pass; fixed numerical replay is exact. Complete
732-file/receipt audits and independent joins verify 144,000 keys for each
predecessor. The validator independently checks all 88 enclosures at 150 digits.
All 177 protected files and six installed lmoments3 source files remain unchanged.
Repository Ruff lint/format and the additional independent probe's scoped checks
pass using shared Python equivalents because the Pixi CLI is unavailable.
Full suite, baseline and candidate matrix runs are outside this stage.

Attempt-2 completion SHA-256:
`7cba09d4bf7af14a93b08e9deedff7b48dd5fe019cd1baf9e992a11bf651338c`.
The [bundle](../milestones/r12/implementation/evidence/gf15-lmoments-readiness/README.md)
retains the original unaccepted attempt, source snapshot and red/green regression
logs. Next: owner release of the unchanged 132,000-fit / 144,000-quantile Stage 2
matrix, followed by the separate Stage 3 qualification assessment. Readiness
acceptance neither reverses A/B failures nor establishes candidate adequacy.

## Stage 2 full matrix released — 2026-09-12

Owner instruction "continue" after Stage 1 completion releases the stated next
step: one complete 132,000-fit / 144,000-quantile matrix under the accepted design.
The python-engineer owns the isolated qualification harness, raw evidence and
mechanical summaries; the driver owns provenance, status and integration.
Requested Astra medium honors the owner's pin; effective settings are unreported.
Stage 3 independent assessment, production integration and sealing remain separate.
Scratch: `.tmp/scratchpad/2026-09-11_0010/gf15-lmoments-qualification/`.
The accepted Stage 1 adapter/environment and all prior evidence remain frozen.

**Stage 2 complete — 2026-09-12.** All 240 chunks completed in 1,054.82 seconds
including reductions/audit: 132,000 accepted fits, 144,000 quantiles, 144 cells per
A/B/C, 432,000 paired comparison rows and 120,000 translation pairs. Candidate C
passes 3/24 baseline scale cells, 18/144 total scale cells and 6/72 eligible
scale-plus-relative cells; the observed gate conjunction is false. A/B retain
the same cell pass counts under their original acceptance semantics.
Every candidate translation pair is both accepted and passes; maximum absolute
scale-error difference is `5.88373794130348e-12` against `1e-6`.

No warnings or refusals occurred. Support/nonfinite-log-density diagnostics occur
in 880 fits in each coordinate and remain diagnostic under the accepted policy.
Branch counts: 11 positive snaps, 113,256 positive rational and 18,733 nonpositive
rational; neither Newton branch nor pre-inversion refusal was reached.
The [execution handoff](../milestones/r12/implementation/evidence/gf15-lmoments-qualification/execution-handoff.md)
and immutable raw records support the next independent assessment. Completion
SHA-256: `e0586b299381114a9ff20e22bdf1dd9c1a8d670ed90fe210a4e4ae004ee34845`.
Stage 3 remains unexecuted; no independent qualification acceptance, production
integration, new estimator search or milestone seal follows from Stage 2.

## Stage 3 independent assessment released — 2026-09-13

Owner instruction "Yes, proceed to independent assessment" releases a fresh
model-validator's recomputation and signed verdict on the frozen Stage 2 matrix.
The validator owns independent audit code and evidence under
`evidence/gf15-lmoments-assessment/`; the driver owns provenance, status and Git.
Requested Astra medium honors the owner's pin; effective runtime settings are
unreported. All prior evidence, estimator code, thresholds and production remain
read-only. No new fits, data, resampling, estimator search or integration is released.
Scratch: `.tmp/scratchpad/2026-09-11_0010/gf15-lmoments-assessment/`.

**Stage 3 complete — 2026-09-13.** The [signed independent handoff](../milestones/r12/implementation/evidence/gf15-lmoments-assessment/scientific-handoff.md)
confirms a mechanically valid run and failed candidate qualification. Independent
recomputation exactly matches all 132,000 fits / 144,000 quantile records, 432
individual cells, 432 paired cells, 432,000 comparison rows and 120,000 translations.
No numerical tolerance or gate waiver was used, and no new fit was executed.
Candidate accuracy passes 3/24 baseline cells, 18/144 scale cells and 6/72 eligible
combined cells; all six n=18 baseline cells fail. Every translation pair passes.

The final immutable audit took 40.89 seconds. A corrupted denominator was caught
by the independent checker. All 749 Stage 2 files, Stage 1 bindings, 732 selected
predecessor files plus preflight, 240 candidate receipts, 177 protected files and
six installed lmoments3 source files were verified. Parent repository Ruff checks
pass using the existing shared interpreter because the Pixi CLI is unavailable.
Signed verdict SHA-256:
`4580f25ddc7a1432735448a9976240c757c59d2ca3253ff5d162cbcadc0fe375`.

GF15 remains unresolved. The assessment is conditional on the adaptively reused
development matrix, with unquantified finite Monte Carlo uncertainty. It neither
establishes general estimator unsuitability nor excuses fixed-criterion failures.
Next is an owner method ruling; no additional estimator search, threshold change,
screening change, production integration or milestone seal is authorized.

## Threefold accuracy policy released — 2026-09-13

Owner selected "lets tripple and check if that will be enough" after comparing
twofold and threefold relaxation. [Policy gf15-accuracy-3x-v1](../milestones/r12/implementation/evidence/gf15-accuracy-3x/README.md)
sets absolute median error to 0.30 and upper/lower P90 absolute error to 1.50/0.75,
in both generating-scale and relative units. Validity, translation, cohorts,
ratio eligibility and the all-cell conjunction remain unchanged. A model-validator
re-scores the signed retained summaries without fitting. Original failures stay
frozen; the new policy is a post-results owner choice, not fresh validation.
Scratch: `.tmp/scratchpad/2026-09-11_0010/gf15-accuracy-3x/`.

**Threefold reassessment complete — 2026-09-13.** The [signed policy handoff](../milestones/r12/implementation/evidence/gf15-accuracy-3x/scientific-handoff.md)
confirms C passes 23/24 baseline cells, 138/144 scale cells, 55/72 eligible combined
cells and 124/144 overall cells. All six n=18 baseline cells pass; five n=18
relative-error cells still fail. The c=-0.2, n=10, p=0.9 baseline has absolute
median error 0.354849373 versus 0.30 and P90 1.915472207 versus 1.50. Its scale
failure repeats at five translations; 14 additional failures are relative-only,
all at rho=0.5. All 120,000 translation pairs remain passing.

The re-score verified signed inputs and exactly reproduced all 432 original
cell decisions before changing thresholds. Boundary checks, an actual corrupted
P90 reducer, compilation and Ruff checks passed. No new fits or baseline/full-suite
runs occurred. Signed verdict SHA-256:
`bbac4358ad2ca06eef68b4c583f1fce07fb2efac21539865d11f04a52f74b987`.
The original failed assessment remains intact. Tripling does not release
production integration or sealing, and no further relaxation is authorized.
