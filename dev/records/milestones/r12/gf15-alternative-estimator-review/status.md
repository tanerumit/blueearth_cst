---
run: gf15-alternative-estimator
target-repo: blueearth_cst
genre: method-spec
author-binding: cst_architect
started: 2026-09-12
variant: full
stage: closed
external-rounds-completed: 2
dispatches:
  opus: 0
  fable: 0
gates:
  G1: approved 2026-09-12
  G2: approved 2026-09-12
flags: [runtime-tier-substitution]
---

## Authority and framing

Owner authorized a reviewed alternative-estimator proposal on 2026-09-12.
Problem, unchanged GF15 criteria and no fitting/integration are settled scope.
On 2026-09-12 the owner replied "yes, continue" to selecting the specified
range-normalized sample-L-moment/PWM GEV candidate as the provisional direction
for remaining design review. G1 is approved, including the finite-mean domain
and diagnostic-only support policy in v1. The two minor domain clarifications
remain accepted for stage 3. No production or benchmark execution approval is
inferred from this proposal authorization.

## Allocation plan

Frontier allocation planned inline before worker dispatch. Legacy Opus/Fable
tiers are unavailable in the live runtime; use supported GPT-6 Astra at high
effort for substantive scientific tasks, with effective settings unverified
until returned. Legacy tier counts stay zero; actual dispatches are logged below,
not falsely reported as Opus/Fable calls. No measured cost comparison is available.

| Stage | Role / requested model | Ownership and dependency | Acceptance |
|---|---|---|---|
| 1 draft | cst_architect / gpt-6-astra high | Fresh author; design-v1.md only, after intake | Self-contained method spec, primary sources, serious alternatives, fixed criteria |
| 1b domain | model_validator / gpt-6-astra high | Fresh reviewer after v1; internal-review-domain.md only | Valid verdict, per-premise dispositions, falsifiable findings |
| G1 | Owner; driver presents | Concrete provisional selection and domain findings | Owner framing ruling |
| 2 risk | critical_thinker / gpt-6-astra high | After G1, internal-review-risk.md only | Valid risk review; no design edits |
| 3 revision | Fresh cst_architect / gpt-6-astra high | After reviews; next design version and ledger | Every finding dispositioned |
| 4 external | Headless reviewer, capability check deferred to this stage | Requires enforced read-only preflight; cross-vendor capability unverified | Named-version verdict and convergence checks |
| G2/finalize | Owner, then author/driver | Reviewed proposal only | Design acceptance is separate from execution/integration |

Driver owns independent premise/source checks, stage validation, gate records,
tracker updates and final Git integration. No nested delegation. Author and
reviewer have separate artifact ownership in the shared task worktree.

## Stage log

- [done] 0-intake — intake.md; owner request captured; domain content yes.
- [done] 1-draft — design-v1.md; proposed normalized L-moment/PWM GEV,
  no fitting or installation; all method-spec headings and alternatives present.
- [done] 1b-domain — internal-review-domain.md; approve, two minor findings,
  zero blocking/major; E1–E9 supported within their recorded limits.
- [done] pre-G1 ledger check — ledger.md accepts every part of domain-1 and
  domain-2 for the stage-3 revision; fixes are pending, reviewed v1 unchanged.
- [done] G1 — approved 2026-09-12; provisional candidate selected as specified
  in v1; numerical criteria unchanged, no execution/integration authorization.
- [done] 2-internal-panel — internal-review-risk.md (approve; risk-1 minor),
  internal-review-index.md preserves all three findings and scope disclosure.
- [done] 3-revision-r1 — frozen v2 and ledger resolve domain-1, domain-2 and risk-1.

## Actual dispatch log

- 2026-09-12 stage 1: `/root/cst_architect_gf15_proposal`, role cst_architect,
  requested gpt-6-astra / high, fresh context. Runtime returned agent identity;
  effective model/effort not separately reported. First-use methodological
  allocation observation: plan preceded dispatch; no comparable cost/usage
  baseline available, so savings undetermined.
- 2026-09-12 stage 1b: `/root/model_validator_gf15_design`, role model_validator,
  requested gpt-6-astra / high, fresh context. Runtime returned agent identity;
  effective model/effort not separately reported. Review owns only its artifact.
- 2026-09-12 pre-G1 ledger: `/root/cst_architect_gf15_ledger`, role cst_architect,
  requested gpt-6-astra / high, fresh context; bounded author-only ledger pass
  to satisfy pre-gate finding coverage while preserving reviewed v1. Effective
  settings not separately reported; no additional design or scientific work.
- 2026-09-12 stage 2: `/root/critical_thinker_gf15_risk`, role critical_thinker,
  requested gpt-6-astra / high, fresh context with v1 and settled G1 only;
  effective settings not separately reported.

## Driver reconciliation

- v1 has all eleven method-spec headings, explicit proposed status, lifecycle,
  alternatives, fixed criteria, validation/stop rules and unresolved scope;
  2,094 whitespace-delimited words by PowerShell Measure-Object.
- Source HEAD matches the v1 full commit identifier.
- Official PyPI 1.0.8 page independently confirms the proposed wheel filename
  and SHA-256. No wheel was installed or package fit executed.
- Installed xclim source independently confirms PWM requires an lmom_fit-capable
  distribution object; lock inspection finds only an optional lmoments3
  constraint, not a package installation. This remains an implementation gate.
- Official lmoments3 GEV source independently confirms named c/loc/scale output,
  disclosed Gumbel approximation and bounded iterative branch. Their runtime
  behavior in the pinned environment is untested.
- The Gumbel information illustration is algebraically consistent with the
  stated known-shape/scale location model and is explicitly asymptotic; it does
  not establish finite-sample impossibility under the conditional GF15 criteria.
- Domain reviewer independently confirmed equations, API/hash and controls.
  Two minor clarifications concern estimator-specific literature evidence and
  Monte Carlo precision; neither changes the provisional candidate or criteria.
- G1 decision requested: select the specific range-normalized sample-L-moment
  GEV candidate, including finite-mean domain and diagnostic-only support policy,
  as the provisional direction for remaining design review. Fixed criteria and
  proposal scope stay settled. Execution and installation remain future scope.
- Review convergence is not yet claimed: risk review, revision and external
  review follow G1; G2 and the workflow commit gate have not been reached.
- Pre-G1 structural validation passed: method-spec headings, named-version
  approve verdict without blocking/major findings, all nine premise dispositions,
  exact original-finding ledger coverage, pending G1 and zero external rounds.
  Validation used read-only PyYAML/Path inspection through the existing Pixi
  environment; no scientific computation or code test suite was run.
- The proposal, review and author ledger are saved locally. No files have been
  staged or committed; workflow finalization/commit remains after G2.
- Resume reconciliation: v1, domain review and ledger are present and recorded;
  same task branch and HEAD retained. Existing frontier allocation still applies;
  no completed stage is rerun. G1 approval releases risk review and revision.
- External capability preflight: codex is absent from PATH; authenticated Claude
  CLI is available. Use its headless adapter to preserve the intended
  cross-vendor review rather than substitute a same-vendor reviewer. CLI help
  confirms safe-mode, restricted mode, closed --tools selection, disabled skills,
  strict MCP selection and dontAsk/permission-prompts none. Sentinel preflight
  completed successfully with effective claude-opus-5 and exactly Glob/Grep/Read
  tools; no write, execution or agent tool was exposed. Sentinel unchanged.
  This is a runtime-adapter substitution, not a waiver of independent review
  or write isolation. Raw preflight is in the session scratch directory.

## External review launch blocker — 2026-09-12

Stage-3 author returned frozen design-v2.md (2,383 words) and append-only ledger
resolutions. Driver inspected the revision delta and original-finding coverage.
V2 SHA-256: `81459EB7EF43731FB259CA95A21EB075462BF0DFD566272A4D1A88A10C67A21A`.

Final preflight passed with effective claude-opus-5, exactly Read, Glob, Grep,
WebFetch and WebSearch, and permission mode dontAsk. This verifies tool isolation,
not authorization to export review content.

Automatic approval review rejected the external round-1 launch before execution:
continuing design review was not considered specific authorization to transmit
internal materials to Claude. No workaround attempted; no external verdict exists.
Explicit owner authorization for that destination and bounded materials is now
required. External rounds completed stays zero; G2 remains pending. No fits,
installation, production edits, staging or commits occurred.

## External review authorized and resumed — 2026-09-12

Owner explicitly authorized sharing the design, review brief and directly cited
repository evidence with Claude. The prior export blocker is discharged.
The same restricted read/web-only command was approved and launched for round 1.
Inputs are the frozen review brief and design-v2.md; prior reviews, ledger and
run metadata are excluded. Requested model: Claude Opus, high effort. Effective
model and tool exposure will be recorded from the completed stream. This is one
actual external dispatch; no completed verdict is claimed yet.

## Round 1 reconciliation and promotion — 2026-09-12

External review captured verbatim as external-review-r1.md. Verdict revise on
unchanged design-v2.md: ext1-1 through ext1-5 major; ext1-6 through ext1-8 minor;
zero blocking. Immediate mechanical convergence check: NOT CONVERGED. No design
edit was made before this check. Promote lean to full as required by the loop;
external cap becomes two. No external finding is silently regraded or accepted.

Actual external dispatch: Claude Opus requested, high effort; init reports
claude-opus-5, tools exactly Glob/Grep/Read/WebFetch/WebSearch, dontAsk. Successful
result, process exit 0. Post-run Git status has only existing tracker/run changes;
v2 hash remains 81459EB7EF43731FB259CA95A21EB075462BF0DFD566272A4D1A88A10C67A21A.
No write/execute/agent tool was exposed. Review did not fit or install anything.

Allocation update before full-panel dispatch: use GPT-6 Astra medium as explicitly
requested by owner. Architecture/internal consistency -> cst_architect; repo-fit
and evidence-schema feasibility -> python_engineer review mode. Disjoint review
artifacts, no nested delegation. Driver checks premises and scope conflicts before
author revision; ext1-1 and ext1-5 may admit scope-divergent responses, requiring
G1 return if confirmed. Neither scope expansion nor criterion change is inferred.
Actual agents: /root/cst_architect_gf15_full and /root/python_engineer_gf15_full;
requested gpt-6-astra / medium, fresh contexts; effective settings unreported.

## Full panel accepted as review evidence; revision released

Architecture and repo-fit each return revise with one major, respectively three
and four minor findings. The index preserves all external/internal IDs and
conflicts. No design framing change is authorized or needed to repair the
confirmed within-scope gaps. Retain deterministic fixed-matrix qualification,
explicit uncertainty limits and unchanged criteria. Additional bootstrap work
and causal attribution are not adopted. A rejection of any external major must
be explicit in the author ledger, then trigger second external review and owner
ratification by G2. Necessary scope expansion would return to G1 first.

Fresh author allocation: cst_architect, requested GPT-6 Astra medium per owner,
limited to design-v3.md and append-only ledger resolutions, no execution. Current
v2 stays frozen. Correct E6 serialization premise in new text only; prior evidence
and reviews remain immutable.

Driver independently rehashed A/B artifact inventories and original A criteria;
all match the repo-fit review anchors. Full-panel findings are proposal contract
gaps, not regressions in production. Pre-existing E6 wording is corrected in the
intake addendum; original scientific criteria remain semantically unchanged.
Stage-6 actual author: /root/cst_architect_gf15_v3, requested Astra medium, fresh
context. Round-2 brief prepared separately so round-1 dispatch input is retained.

## V3 reconciliation and round-2 trigger

Fresh author returned frozen v3 (4,148 words) and append-only ledger resolving
all 20 original IDs per part. Driver inspected the affected contracts and ledger.
V3 SHA-256 76F76252C06905EF2DA2FDF8EBBFDC80D946015C639A4202CF7394CB1254A34C;
ledger SHA-256 E9F3E64DDD0FA71A3A3EEC91603F882115170F1F2AEC3DC0D9A315533EFB861C.
V2 remains unchanged. No selected estimator, scientific criterion, support policy
or scope change; new readiness controls are explicitly prospective.

Round-2 trigger checked by driver: no blocking finding/fix exists; rejected-major
trigger FIRES for ext1-1, ext1-2, ext1-3 and ext1-5 (partial rejection included).
No waiver. Owner ratification of rejected majors remains due by G2. Dispatch
second/final full external review with review-brief-r2.md, frozen v3, ledger,
index, first external and full-panel reviews. Requested Claude Opus high through
the identical owner-authorized restricted adapter. No candidate execution.

## Round-2 launch rejection — 2026-09-12

Automatic approval review rejected the second launch before process creation.
Reason: revised design plus ledger, review index and prior review artifacts were
considered an expanded payload beyond the earlier design/brief/direct-evidence
permission. Owner's full explicit Claude authorization was provided, but review
still requires explicit authorization naming this added artifact set. No retry
or indirect workaround. Round 2 has not run; completed rounds remains one, and
no G2 convergence is claimed. The prepared v3/ledger/round-2 brief remain frozen.

Local structural verification passed: 11 genre headings, nonempty alternatives,
all 20 original finding IDs covered, v1/v2/v3 present, frozen v3 hash unchanged.
No code changed and no code suite was run. Prior review findings, criteria and
scientific evidence remain retained. No staging, commits, installs or fits.

## Expanded payload explicitly authorized; round 2 resumed

Owner replied yes to the explicit v3/ledger/index/all-prior-reviews/brief/direct-
evidence payload for Claude round 2. Automatic approval review accepted the same
restricted command. Process launched; second round is running, not completed.
The design and ledger hashes were rechecked and remain frozen. This permission
is for review, not estimator execution or production integration.

## Round 2 immediate convergence check

Verbatim external-review-r2.md returns revise on frozen v3: ext2-1 major,
ext2-2/ext2-3 minor, zero blocking. All ext1 resolutions accepted as defensible,
with new CDF control defect and two readiness clarifications. NOT CONVERGED;
check made before any design edit. Two-round cap reached: no third full review.
Driver verifies remaining premises before owner arbitration. V3 remains frozen.
Actual second dispatch: successful exit 0, effective claude-opus-5, exactly
Glob/Grep/Read/WebFetch/WebSearch, dontAsk; no write/execute tools exposed.

## Driver premise verification for cap arbitration

Ext2-1 is a regression introduced by v3's new D6 control, not a pre-existing
estimator defect. V3 requires an absolute probability tolerance 1e-10 on every
branch control. Independent analytical verification used only Python standard
library Decimal/math, not lmoments3, NumPy, retained draws or any fitting routine.
For fixed t3 values and l1=0/l2=1, solve the theoretical shape relation; calculate
Gamma by recurrence to >=200 and a ten-term Stirling expansion, round parameters
to float64, derive the high-precision target quantile, then test its nearest
float64 and immediate neighbors in the independent CDF. Decimal 80/100 precision
passes agree at every emitted float precision. These are theoretical feasibility
controls, not candidate runs or measured package behavior.

| t3 | Minimum probability residual among nearest float64 and neighbors | 1e-10 pass |
|---|---|---|
| -.85 | 3.413080096e-14 | yes |
| -.969999 | 5.283075759e-10 | no |
| -.97 | 2.798593988e-10 | no |
| -.970001 | 5.305828309e-10 | no |
| -.98 | 5.293578395e-9 | no |

The density-times-ulp scales are 1.47e-9 near -.97 and 1.68e-8 at -.98.
This confirms a robust-control defect. It does not prove that every actual
library-rounded parameter tuple fails: the unexecuted library's approximation
can change a quantile's position in the float grid. The reviewer's universal
wording is stronger than this bounded evidence, but the proposed control lacks
rounding allowance even for near-exact parameter values and should be repaired.
Scratch source/results: gf15-design-review/check-cdf-resolution.py and
cdf-resolution.json under .tmp/scratchpad/2026-09-11_0010/. No dependency installed.

Ext2-2: D5's tau(.2) branch control overlaps the original population shape control;
source inversion depends on t3 alone. This overlap was introduced by v3. D5 already
says failed original controls stop readiness, so precedence is implied; accept
explicit clarification without changing gates. The reviewer mentions tau(-.2)
although that value is not a duplicate branch-table entry; do not invent one.

Ext2-3: D5 leaves the lower bisection bracket unspecified, introduced with v3's
new oracle. Direct substitution gives tau(-1)=1; the endpoint is valid for the
mathematical bracket, while an accepted estimator must still have c>-1. Clarify
initial bracket, expansion and bounded failure. The oracle is for fixed controls,
not a new empirical per-fit root solver. No candidate algorithm change follows.

Recommended owner ruling: accept ext2-1's quantile-space alternative for a check
of the adapter's float64 output against an independently derived CDF reference,
retaining the existing scaled quantile tolerance; accept ext2-2/3 clarifications.
After approval, fresh author produces v4 confined to these IDs; driver scope-checks
and a scoped independent delta review must pass before G2. No third full external
round. No repair or G2 approval is inferred from export authorization.

Author ledger pass complete: all 23 unique IDs covered; ext2-1/2/3 proposed
repairs explicitly pending owner arbitration and later scoped review, not resolved.
Ledger SHA-256 D7401379A7DE876D1D63F25D0C293C4BC91EC8FAD634244AF6693A7267876EBC.
V3 unchanged. Structural/hash checks and git diff --check passed; no code suite
was run for this proposal-only work. Saved locally, uncommitted pending G2.

## Owner arbitration approved — 2026-09-12

Owner replied yes to the three concrete recommended repairs and subsequent
scoped verification. This is the binding stage-6a ruling, not G2 approval.

| ID | Owner ruling | Scope |
|---|---|---|
| ext2-1 major | Accepted, fix required | Quantile-space alternative for independent CDF check of adapter float64 output, retaining existing scaled quantile tolerance |
| ext2-2 minor | Accepted, fix required | Original population acceptance gates override overlapping descriptive branch diagnostics |
| ext2-3 minor | Accepted, fix required | Explicit mathematical oracle bracket, deterministic expansion and bounded failure |

Fresh author owns v4 and append-only ledger, confined to D5/D6 and forced revision
references. Requested GPT-6 Astra medium per owner. After driver scope/hash checks,
one independent scoped verification reviews the delta; no third full external
round. Estimator, fixed GF15 criteria and existing scientific scope remain unchanged.
No fitting, dependency installation or production integration is authorized.

## V4 frozen; scope check and independent verification

Fresh author /root/cst_architect_gf15_v4 returned v4 (4,847 words) and append-only
ext2 ledger resolutions under owner arbitration. Requested Astra medium; effective
model/effort not separately reported. V3 remains unchanged.
V4 SHA-256 90CE735AF1C15AFB964194C78A24F47ECC0BC7F62D315D0FE5D22F70F6792EE9;
ledger SHA-256 6E55373EB655AFF685368B8AA94324CDA224702B38820FA6B26E29B408A1693B.

Driver inspected every v3/v4 hunk: D5/D6 within Validation regime plus metadata
and the forced orchestrator version reference. No unrelated design change.
Independent scoped reviewer /root/model_validator_gf15_v4_delta (model_validator,
requested Astra medium, fresh context) owns scoped-review-v4.md. Scope ext2-1/2/3,
not a third full external round; bounded analytical feasibility probes permitted,
no candidate fitting, installation or production edits. G2 remains pending.

## Scoped verification approved; G2 ready

scoped-review-v4.md returns approve on design-v4.md, findings empty, explicitly
resolving ext2-1/2/3 at proposal level. Driver reconciled mathematical and scope
assessment: correct forward CDF/endpoints, same recorded float tuple, independent
bracketing, conservative enclosure budget and retained original gate precedence.
No version change follows the approval. V4 remains at its frozen hash.
Review SHA-256 1CBB2CA610DEADAB6DBB55D39C51B4998E8303DFF0B536A1565D68D947447E7D.

This reaches G2 through owner arbitration plus the required scoped pass, not a
third external round or an external approve verdict on all v4. External round 2
accepted ext1 dispositions as defensible; final owner approval also ratifies the
recorded rejected portions of ext1-1/2/3/5. No unresolved substantive finding or
arbitration repair remains at design level. Full numerical readiness, dependency
compatibility, reference implementation and actual qualification remain unexecuted.

Pre-G2 checks passed: all four versions retained; eleven headings and nonempty
alternatives; named-version scoped approval with empty findings; frozen v4 hash;
all original IDs retained in the author ledger. No fit/install/integration or
code test suite ran during the v4 revision. No staging or commit before G2.

Author appended ext2 verification closures, preserving all 23 IDs. Final pre-G2 ledger SHA-256: 79309DDEDEF85353658875331FEAC8A91FD0160960FAFA4A6ED69AAB4DFA27A8.

## G2 approved — 2026-09-12

Owner replied yes i approve to frozen v4 and its recorded resolutions, including
ratification of the recorded ext1 rejected portions. Design finalization and the
implementation brief are authorized. This does not release candidate execution.
Promote the complete run to dev/milestones/r12/gf15-alternative-estimator-review/
for R12 audit provenance, per dev/README.md promotion rule. Preserve all original
design/review/ledger bytes. Accepted design lives beside the archive; editorial
status/link relocation only. Prepare one bounded Stage 1 readiness brief from it.
## Stage 7 completed — accepted design and readiness brief

Accepted design: ../gf15-alternative-estimator-design.md. Next assignment:
../implementation/gf15-lmoments-readiness-brief.md, Stage 1 only, not started.
Author /root/cst_architect_gf15_finalize used requested Astra medium, fresh context;
effective settings unreported. Finalization changed only approval/lifecycle/version
metadata and links; Method through Uncertainty matches reviewed v4 verbatim.
All archived designs/reviews/ledger remain preserved. Full-run retention in this
milestone archive follows the repository audit/promotion convention; working run
was drained by a hash-verified move of all 18 documents.

Final runtime allocation summary: 11 fresh named-role GPT-6 Astra author/reviewer
dispatches across this run, plus 2 successful Claude external reviews (effective
claude-opus-5), with bounded author follow-ups. Legacy Opus/Fable spawn counters
remain zero because those legacy worker tiers were substituted; the actual
cross-vendor reviewer model is recorded above. Two rejected launch attempts and
read-only preflights are not completed review rounds. No measured token/cost
comparison is available. No third full external round was performed.

G1 and G2 approved; ext2 arbitration approved; scoped v4 review approved with no
findings. Design completion is via arbitration and scoped verification, not an
external whole-v4 approve verdict. All 23 IDs remain in the closed design ledger.
No estimator adequacy, implemented-control passage or production acceptance is
inferred. R12 remains unsealed; its task waits for Stage 1 execution authorization.

The brief materializes accepted D1-D6 as prospective falsifiers and honest command
placeholders to replace before readiness acceptance. Driver mechanically uses
snake_case for proposed importable helper/test filenames, preserving kebab-case
CLI filenames per project conventions. This is brief formatting, not a method
change. Master brief, validation map and task links now target durable records.
Finalization verification: 23 Markdown files passed local-link checks; accepted
Method-through-Uncertainty text matches archived v4; frozen v4 and ledger hashes
match; required design/brief headings and git diff --check passed. No stale working
run reference remains outside the historical archive. Board render passed using
its normal shared-Git-metadata lock. Test posture: rapid, numerical outputs
unaffected; no production code changed, so no code suite or baseline rerun.

Accepted design SHA-256 e88d4a75b4d0198cf5255d9fedcd83ce86c887d1038c0346fdd2ee228a00f6fe;
readiness brief SHA-256 ab6b7ed0443be116decfb0dff6d8e768f93f4be1c47aa4401a55e2bb6cc90321.
Scoped .gitattributes rules preserve reviewed mixed line endings and all recorded
byte digests, following the existing R12 evidence convention. Whitespace lint is
suppressed only for these verbatim/frozen documentation artifacts. Stage/index
byte verification precedes the documentation commit on feat/wp3-improvements;
no branch integration, push or milestone seal is part of this finalization.
