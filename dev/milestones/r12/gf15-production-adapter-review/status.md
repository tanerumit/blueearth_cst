---
run: gf15-production-adapter
target-repo: blueearth_cst
genre: decision-record
author-binding: cst-architect
started: 2026-09-13
variant: full
stage: closed
external-rounds-completed: 1
round-2:
  dispatched: waived
  triggers-checked: [mechanism-changed, rejected-blocking-major]
  fired: []
dispatches:
  opus: 0
  fable: 0
gates:
  G1: approved 2026-09-13
  G2: approved 2026-09-14
flags: [user-model-pin, promoted-lean-to-full]
---

## Allocation and runtime

Planner/integrator: interactive GPT-6 Astra medium, preserving the user's pin.
Requested workers: GPT-6 Astra medium for all current stages; effective model
and effort unverified because the runtime does not report them. Opus/Fable are
not used; their counters remain zero. Actual requested-model dispatch counts
are recorded below, without inventing cost or usage measurements.

| Order | Deliverable | Role / requested model | Dependency and ownership | Acceptance |
|---|---|---|---|---|
| 1 | Concrete design-v1.md | cst_architect / GPT-6 Astra medium | Intake; owns design only; fresh context | Self-contained alternatives, interfaces, claims and executable falsifiers |
| 2 | internal-review-domain.md | model_validator / GPT-6 Astra medium | Completed v1; owns review only | Named-version verdict, stable findings, E1–E7 dispositions |
| 3 | G1 packet | Driver | Draft + domain review + prerequisite inspection | Structural checks, concrete owner decision; stop at G1 |
| 4 | Internal risk review | critical_thinker / GPT-6 Astra medium | v1 + settled G1; owns risk review only | Stable findings and consistent named-version verdict |
| 5 | Revised design-v2.md and ledger | cst_architect / GPT-6 Astra medium, fresh | Complete internal reviews/index + G1 | Every finding dispositioned, scope unchanged |
| 6 | External review readiness | Driver | Revised concrete draft | Resolve transport/isolation/vendor capability before external dispatch; return a real blocker if unresolved |

Risk lens and external review follow G1 only. External CLI is absent from PATH;
transport/authorization is a later unresolved prerequisite. No model-vendor
diversity or enforceable reviewer read-only sandbox is claimed for in-process
artifact-writing roles. Their writes are authorized only to their assigned
artifacts; frozen inputs are hash-checked by the driver.

Actual requested-model dispatches: GPT-6 Astra medium author x2, domain reviewer x1, risk reviewer x1; effective settings unverified. Claude transport preflight x1, effective claude-opus-5, high requested effort; no external review round yet.
No independent savings/cost comparison is available.

## Stage log

- [done] 0-intake — outputs: intake.md; source assessment d761a65b; domain-content yes.
- [done] 1-draft — design-v1.md; SHA256 d8fb9320061d42081093266dbb14004b198b0868c41bae991f26d7ebd6f090ba.
- [done] 1b-domain-review — internal-review-domain.md approves design-v1.md; 0 blocking, 0 major, 2 minor (domain-1, domain-2); E1–E6 supported, E7 remains an implementation prerequisite.
- [done] Gate prerequisite inspection — 71 existing tests collected in37.69s; exit0. No test execution or adapter validation claimed.
- [done] G1 structural verification — named-version approve verdict, both minor IDs ledgered, E1–E7 dispositions present, D1–D8 and three alternatives present, all42 recorded sources unchanged; log `.tmp/scratchpad/2026-09-11_0010/gf15-production-adapter/g1-check.log`.
- [done] G1 — owner "yes I approve option A" on2026-09-13; Option A provisional integration and both minor actions approved.
- [done] 2-internal-panel — risk approves v1 with risk-1 minor; domain/risk indexed in internal-review-index.md, no conflicts, no G1 return or promotion triggered.
- [done] 3-revision-r1 — design-v2.md SHA256 c83245ba06a412d5a38a00c138f7268e04da9a342d37e49c7f231440a32c5ef6; domain-1/domain-2/risk-1 accepted and resolved as wording/prerequisite/reporting contracts. E7 remains empirically outstanding; no scope change.
- [done] 4-external-r1 — external-review-r1.md, revise on design-v2.md: ext1-1 major, ext1-2/ext1-3 minor; captured verbatim after exit0.
- [done] 5-convergence-r1 — not converged; one major survives. Immediate full-panel promotion under workflow; external cap now2.
- [done] 2-full-panel-promotion — architecture-1 major; repo-1 major plus repo-2/repo-3 minor; all indexed with ext1 findings and driver premise checks.
- [done] 6-revision-r2 — design-v3.md SHA256 47508c9b6b124d4bd7e0424c1e66a0fb9e6755b4164ab69e50ef10a735eb86d0; all10 original findings accepted with per-part dispositions; G1 scope unchanged.
- [done] Round2 trigger check — no blocking findings, hence no blocking fix changed a mechanism; no blocking/major finding rejected. ext1-1 accepts the offered disclosure alternative (b); declining alternative (a) is not rejection of the finding. Round2 waived; new mechanisms require scoped verification.
- [done] 6-scoped-verification — scoped-review-v3.md approves exact design-v3.md, zero blocking/major/minor findings; verifies all10 resolutions and round2 waiver, changed mechanisms and evidence premises. Requested GPT-6 Astra medium; effective settings unverified. Scoped reviewer x1, in addition to previously recorded dispatch counts.
- [done] G2 — owner "yes I approve it" on2026-09-14 approves exact reviewed v3 for finalization and implementation handoff.
- [done] 7-finalize — accepted design in dev/milestones/r12/gf15-production-adapter-design.md; original review archive in gf15-production-adapter-review beside it; four-stage implementation brief created. D1-D8 exact text preserved. Requested GPT-6 Astra medium author x4 total; effective settings unverified.

## Gates

G1 approved 2026-09-13: Option A and both minor actions below. Scope is settled for later reviewers; downstream inconsistencies remain reviewable.
G2 approved 2026-09-14: exact reviewed v3 accepted. Prior pending-gate packets below are chronological history.

## Closure — 2026-09-14

Owner approved v3 with "yes I approve it". Finalization changes only accepted
status/lifecycle, historical gate wording and relocated citations; D1-D8 are
text-identical. The accepted design and four-stage implementation handoff are
durable R12 milestone artifacts. Preserve this run and its verbatim milestone
archive under R12's scientific audit convention; do not prune uncommitted
review history. The design loop is complete. Implementation Stage1 discovery
is separately in progress; no setup, parity or numerical implementation pass
is inferred. Design finalization is eligible for its scoped branch commit.

Final requested dispatch counts: GPT-6 Astra medium authors x4, domain x1,
risk x1, architecture x1, repo-fit x1, scoped verification x1; effective settings
unverified. One external review (reported claude-opus-5, high effort requested)
and one synthetic transport preflight. No second external round; waiver and
named-v3 verification retained above. The first finalizer task-name collision
created no dispatch; the fresh cst_architect_gf15_land_v3 completed finalization.

## G2 decision packet — 2026-09-13

Approve [design-v3.md](design-v3.md) as the provisional C production-integration
design. The [scoped verification](scoped-review-v3.md) names and hashes v3 and
approves with zero findings. All10 original findings have accepted, per-part
design resolutions. External round1 on v2 remains revise in the immutable
record; v3 reaches G2 through the explicitly waived round2 and independent
scoped verification, not a claimed full external approval of v3.

The revision adds live-environment freshness and probability-coverage checks,
structured constant refusals, and explicit detached-CSV disclosure; it preserves
the approved method, 8x criteria, source distribution and export surface.
Production/platform parity, isolated environment setup, a retained pre-change
snapshot and metrics-only comparison remain unexecuted implementation gates.
Actual-bundle adequacy remains unestablished; baseline and milestone seal remain
separate. Approval releases design finalization and the implementation handoff.

Driver reconciliation: all42 readiness source bindings and all177 protected
production/config/lock/baseline bindings unchanged; frozen v1/v2/v3, ledger and
external-review hashes verified. No production tests or fits ran during this
design revision. Run artifacts remain unstaged/uncommitted pending G2 and the
stage7 commit gate. Structural-check evidence is in session scratch
`gf15-production-adapter/g2-check.log`.

## G1 decision packet

Recommended: **A — provisional C integration**, retaining the fixed candidate
method and approved8x criteria, with complete packaged benchmark evidence and
new metric identity. Screening remains provisional; actual-bundle adequacy
remains unestablished. The alternative is suitable for review within that
limited scope, not accepted for production yet.

| Choice | Scope and consequence |
|---|---|
| A (recommended) | Review D1–D8: C adapter, precise refusal/fault boundary, report/schema/identity, legacy reads, isolated dependencies, pre-change snapshot and parity/metrics-only acceptance. |
| B | Retain predecessor numerics and repair truthful predecessor metadata; cannot inherit C's pass. |
| C | Require actual-bundle scientific validation before production use; expands data/use/validation scope and postpones integration. |

Minor findings presented for G1 ruling:

- domain-1: carry the exact raw/back-mapped linear-moment unbiasedness qualification into the next revision; no claim that random normalization or float64 recovery is unbiased/exact.
- domain-2: retain production/platform parity as outstanding; settle by frozen controls, exact acceptance/refusal checks and a failing wrong-result mutant before implementation acceptance.

Proposed G1 ruling: approve A as provisional framing and accept both minor
actions above. This releases the internal risk review and subsequent revision/
external review, not production execution. G2 remains the later design approval.
External CLI transport/isolation remains unresolved and is checked before its
dispatch; no fallback is authorized by this packet.

Post-G1 transport check: authenticated Claude CLI remains available. The prior
R12 run used this alternate runtime for the intended cross-vendor review when
Codex CLI was absent. New synthetic-sentinel preflight exited0: effective
claude-opus-5, exactly Glob/Grep/Read, dontAsk, no MCP/skills/plugins, unchanged
sentinel. Safe/restricted mode plus closed tool allowlist enforces no write or
execution tools. Scratch preflight-stream.jsonl records the full check. This
establishes transport/isolation, not review completion or expanded data-sharing
authorization; automatic approval review still evaluates the actual launch.

The exact reviewed v1 is unchanged. Collection verified 71 owning tests; no
tests executed. All42 production/readiness source-inventory entries are
unchanged. Run artifacts remain unstaged/uncommitted until the workflow's
commit gate; durable files preserve the current resume point in the stage log.

Immutable domain review SHA256:
`5cb8e137237d6aa912155ef390ae4815fbe26914bbd47bee418208b838e16b28`.
G1 approval question: approve option A as provisional framing and carry the two
minor actions above into the next revision/implementation handoff?

## External launch decision point — 2026-09-13

G1 approval was executed through risk review and v2 revision. All three internal
minor findings have accepted design dispositions; E7 production parity remains
an unexecuted acceptance prerequisite. Frozen v2 and review-brief.md form the
concrete proposed external-review payload; the directly cited repository sources
may be read narrowly for evidence. Prior review files, ledger, index, intake and
status are excluded from this clean-room round.

Automatic approval review rejected the launch before execution:

> This would export private repository design and cited evidence to an external Claude service; although the user authorized Claude review and continuation, the transcript does not specifically authorize sending this concrete sensitive payload to that destination.

No workaround or retry occurred. Required decision: explicitly authorize sending
this run's design-v2.md, review-brief.md and directly cited repository evidence
to Claude for the independent read-only review. Continue with the same closed
Glob/Grep/Read tools, dontAsk, no extensions or execution tools after approval.
Preflight success is not content-export authorization. External rounds completed
remains zero; G2 pending. No production/environment changes, fits, Git staging
or commits occurred. Resume here; do not repeat completed internal reviews.

## Concrete external payload authorized — 2026-09-13

Owner replied "yes, i explicitly authorize" to sending this design-v2.md,
review-brief.md and only directly cited repository evidence to Claude for
read-only external review. The prior export blocker is discharged. Resume
the same frozen round1 inputs with the verified closed tool allowlist.

Actual external round1 launched successfully after authorization; tracked
process session60126, transcript in session scratch external-r1-stream.jsonl.
One external dispatch started; completion count remains zero until a valid
verdict is captured. No internal review or revision was repeated.

## External round1 result and promotion

Effective reviewer claude-opus-5, requested high effort, tools exactly
Glob/Grep/Read, dontAsk and no extensions; exit0. Result is verbatim inside its
original Markdown fence; schema extraction ignores the outer display fence
without changing the artifact. Verdict revise, one major and two minor, named
v2. Convergence checked immediately before edits: false. Full promotion is
mandatory; architecture and repo-fit reviews use fresh contexts and settled G1.
No finding has been regraded or rejected by the driver. Requested new reviewers
are cst_architect and python_engineer, both GPT-6 Astra medium, each owning only
its review artifact. The author revision waits for both and the extended index.

Promotion reviews completed and index extended. Requested-model dispatch counts
now: author x3 (including v3), domain x1, risk x1, architecture x1, repo-fit x1,
all GPT-6 Astra medium; effective worker settings unverified. External actual
reviews x1 (effective claude-opus-5), synthetic preflight x1. Fresh v3 author
owns only design-v3.md and append-only ledger. Preserve all prior versions and
review text; no G1 scope change accepted. After revision, mechanically check
blocking-mechanism and rejected-blocking/major triggers before choosing round2
versus the mandatory scoped delta verification.
