---
title: Improving repo-wide documentation and instructions
type: todo-item
status: active
branch:
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

Next: Owner review of completed user-guide/technical-manual publications; scientific writing stays deferred.

P5/P6 accepted and landed at `0fda56af`. Complete HTML/PDF volumes and website verified; independent
reader review accepted after the starter calendar-year comment correction `86085ea2`. P6-02 duplicate
website appendix title is a deferred minor issue; PDF cross-volume section jumps remain reader-dependent.
See [P5 return](t2610211349/p5-return.md) and [P6 acceptance](t2610211349/p6-review.md).
Both publication branches are deleted and s1/s2 parked. Review artifacts remain in s1
`docs/site/_site/` and lane-local task scratch pending owner review; no push or deployment.
The broader task stays open for deferred scientific writing and any separately scoped instruction work.

V9 landed at `8963f661`; P4A/P4B reviewed and landed at `1e0cbd71`. Ten guide chapters and 16 manual
chapters are integrated. The 405 source-link/fragment checks, 44 scaffold/notebook tests, 101 contract
tests and 14 integrated pilot/documentation tests pass. P5/P6 completion above supersedes that stage's hold.
See the [P4A return](t2610211349/p4a-user-guide-return.md),
[P4B return](t2610211349/p4b-technical-manual-return.md) and execution log for scope and measurements.
Both source branches were deleted after guarded landing; s1/s2 are parked. S3 remains unrelated.
Scientific-approach writing remains deferred. The owner's subsequent "continue" commissions P5/P6.
P5 assembly and the fresh P6 review have now completed; their retained returns record actual checks.

Latest plain-language revision: `865803b2` in s2. Simplifies choices and removes development-only
compatibility/migration guidance from maintained documents. See the
[plain-language return](t2610211349/publishing-pilot-plain-language-return.md) for current review samples.

Editorial pilot revision: `bbf5fec6` in s2, retained without landing. Both formats use numbered steps and
reader conventions; implementation details remain in linked advanced material. See
[editorial return](t2610211349/publishing-pilot-editorial-return.md) for artifacts and verification.

- [x] Map the documentation landscape — retained the structural review dated 2026-10-21.
- [x] Repair onboarding entry points — three source documents landed at `2945a397`; site build passed.
- [x] Inventory in-scope documentation by audience — 55 files; coverage and relative links checked.
- [x] Review purposes and boundaries — 55-source map, independent critique and reconciled outlines retained.
- [x] Audit and revise commissioned guide/manual guidance — independent P6 acceptance, landed `0fda56af`.
- [x] Verify affected links, examples and rendered pages — retained P5/P6 evidence and bounded recheck.
- [ ] Revisit deferred scientific writing and separately scope any remaining instruction work.

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

Saved the scoped file register for the five selected audience groups: toolbox users, scientific explanation,
indicator users/extension authors, configuration users/maintainers, and developer/maintainer guidance.
Verified 55 unique entries against tracked paths and checked all relative links.
Excluded `.github/` and `CHANGELOG.md`, retaining the earlier directory exclusions. Other audience groups
and embedded documentation surfaces are outside the review scope; the inventory records the full boundary.
This pass does not assess content accuracy or decide consolidation.

## Landscape assessment (2026-10-26)

Retained the high-level assessment: central reader journeys, local instructions, and shared Markdown
sources for derived publications. Recommendations remain proposals; no restructuring was implemented.

## Execution planning (2026-10-26)

Saved the proposed stages, role/model allocations, ownership, handoffs and acceptance checks.
Added prospective efficiency/effectiveness tracking, including actual role and skill use, waits, usage,
checks and rework. No workers have been dispatched; implementation remains unstarted.
Original topology: cst-main coordinates; s1, s2 and s3 were proposed for medium-effort packets.
The later owner follow-up below supersedes this allocation and excludes s3.
Parallel lane execution is authorized where independent. cst-main alone commits and merges/lands;
user-facing and human decisions return to the owner. The plan records the coordinator handoff.

## P1–P2 execution (2026-10-26)

Owner authorized P1–P2 only, with a return of reviewed structure and decisions before pilot or migration.
Coordination-plan changes reviewed and committed on main at `58efe411`; whitespace checks passed.
cst-main owns shared evidence, acceptance and commits. P1 runs in s1 as `technical-writer-p1`, reading
current main and returning evidence without source edits. P2 uses fresh s2 context after P1 is accepted.
Both lanes were clean and detached; their startup conversations confirmed no prior task owner.
No implementation branches or source edits are needed for these evidence-only stages.
Execution measurements and permission-boundary status belong in the linked observations log.
P1's complete 55-file map and four collection outlines are retained and accepted for independent critique.
P2 was dispatched to `critical-thinker-p2` in s2 at medium effort. Owner expressly allowed review under
current runtime permissions; read-only instructions apply without a claim of enforced isolation.
P2 completed with three major findings and one minor clarification. The editorial lead accepted all four
and appended their dispositions to the same map. Source-link compatibility, generated case instructions
and the offline response-surface endpoint remain explicit owner choices. P3 and migration are not started.
Owner follow-up restricts this task to cst-main, s1 and s2; session-3 stays available for unrelated work.
The artifact-first dispatch improvement is separately authorized infrastructure maintenance, not approval
of the pending publication or migration choices.

## Work location

- Coordination/integration: cst-main :: `dev/tasks/t2610211349/`; only coordinator commits and lands.
- P4A owner: session-1, `docs/t2610211349-user-guide`; continuing technical-writer-p1, medium.
- P4B contributor: session-2, `docs/t2610211349-technical-manual`; fresh api-documenter-p4b, medium.
- Shared allocation base: `a4d79ea6`, including approved V9 landing `8963f661`.
- Implementation ownership and checks: [P4 packet](t2610211349/p4-content-assignments.md).
- Returns: lane-local `.tmp/tasks/t2610211349/p4a-return.md` and `p4b-return.md` respectively.
- Next: workers complete their disjoint packets; cst-main reviews the returns. No current blocker.
- Retention: preserve s2 P3 artifacts while the central review index links them. No cleanup yet.
- s3 is reserved for unrelated work. P4C is deferred; P5/P6 are not yet commissioned.

## Completed P3 work location

- Owner: session-2; branch: `feat/t2610211349-publishing-pilot`; implementation commit `bed0ae1e`.
- Implementation: session-2 :: publication pilot mechanics, manifest and isolated compatibility fixture.
- Coordination: main :: `dev/tasks/t2610211349/`.
- Scratch and outputs: session-2 :: `.tmp/tasks/t2610211349/p3/`.
- Verification: 14 affected tests, scoped Ruff, source integrity, refresh, link and visual checks pass.
- Retention: keep pilot outputs/evidence in s2 until owner review and a retention decision; no cleanup.
- Final outcome: V9 approved, committed as `fb9aca81`, landed at `8963f661`; pilot branch deleted.
- Specification: [frozen content](t2610211349/publishing-pilot-content-specification.md).
- Assignment: [P3 engineer packet](t2610211349/publishing-pilot-assignment.md).
- Return: [P3 evidence and limits](t2610211349/publishing-pilot-return.md).

## Refs

Owner structure decision (2026-10-26): approved the user-guide, technical-manual and scientific-approach
structure; focus the next writing tranche on the user guide and technical manual. Scientific-approach
writing (P4C) is deferred, with its outline and existing material retained. The owner selected 1A, 2A, 3A:
include bounded generated-case instruction reconciliation, retain initial tracked compatibility pages,
and limit the first publication to indicator-table interpretation, selection and extension. Supported
surface construction is deferred. The owner subsequently authorized P3 at medium effort in s2,
returning the pilot for review before migration. V9 is now approved and integrated; P4A/P4B are commissioned.
P4C remains deferred; P5/P6 are subsequent stages.

- [Proposed boundary map and outlines](t2610211349/documentation-boundary-map.md).
- [Independent boundary critique](t2610211349/documentation-boundary-critique.md).
- [Execution plan](t2610211349/documentation-execution-plan.md).
- [Workflow execution observations](t2610211349/workflow-execution-log.md).
- [Documentation landscape assessment](t2610211349/documentation-landscape-assessment-2026-10-26.md).
- [Documentation inventory by audience](t2610211349/documentation-inventory-2026-10-26.md).
- [Documentation landscape review](t2610211349/documentation-review-2026-10-21.md).
- The initial review is an inventory, not a page-by-page accuracy audit.
