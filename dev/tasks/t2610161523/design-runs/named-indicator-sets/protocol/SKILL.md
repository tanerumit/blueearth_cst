---
name: design-review-loop
description: >
  Use when a complex change needs reviewed design before implementation.
  Trigger when the user
  says "design review loop", "reviewed design", "adversarial design review",
  "external design review", or "cross-vendor review", or a consequential
  architecture or cross-tool contract decision needs independent challenge.
  Reviewing or editing this skill itself does not start a design review run.
  Use design-exploration for ordinary assessment, design-document for drafting,
  and code-review for implementation diffs.
theme: workflows
version: v0.17.1
background:
  - knowledge:wiki/!meta/design-review-loop.md
---
# Design review loop

## Scope

Produce a decision-ready, independently reviewed design for a consequential
change. The interactive driver coordinates a file-backed run under
`workflow-driver`; an author owns design content, independent reviewers
challenge it, and the user decides framing at G1 and exact approval at G2.
`agent-routing` binds eligible roles and allocations. The loop is bounded by
a total work budget and finding admissibility, while scientific validity and
human approval remain hard requirements.

The role/skill boundary is explicit: this skill defines the review contract;
`agent-routing` alone binds role personas to stages.

Enter for an explicit reviewed-design request or when a consequential choice
about architecture, cross-tool contracts, or scientific validity needs independent
challenge before implementation. Identify the unresolved decision and the cost
of getting it wrong. Novelty, several affected files, or scientific subject matter
alone does not require this loop. Use direct exploration or drafting when existing
patterns and proportionate checks settle the choice. Entry criteria select a
procedure; host rules still govern dispatch authority and available reviewers.

## Non-Goals

- Use `design-exploration` for unsettled intent or existing-system assessment,
  interactively or non-interactively; it does not itself admit a review run.
- Use `design-document` for document genre and placement, `task-brief` for
  implementation handoff, and `code-review` for diffs.
- Use `workflow-driver` for execution, resume, and human gates; use
  `agent-routing` for persona and model selection.
- Design routine fixes, clear refactors, and single-module changes directly.

## Operating Rules

1. **Start with the decision.** At intake and G1, lead with the user outcome,
   ordinary end-to-end journey, choices, and the smallest useful alternative.
   Show consequential tradeoffs, complexity, migration, and any decision that
   could change the approach. Use files, names, and trees as evidence for those
   choices. Reuse established user intent; ask only unresolved questions.
   Return to G1 if problem, scope, constraints, or selected alternative changes.
2. **Keep independent scientific review.** When the design carries a method,
   data treatment, physical/statistical assumption, uncertainty, or validation
   claim, a domain reviewer applies `claim-evaluation` before G1. Present its
   framing findings there. A reviewer never edits the design or grades its
   own revision. Preserve raw reviewer outputs verbatim, exact reviewed
   versions, evidence premises, and conflicts.
3. **Budget all worker work.** Default maximum: six worker calls without
   domain content, seven with it. The normal path uses draft, risk and external
   initial reviews, one consolidated author revision, and at most one targeted
   verification; domain review adds one call. This normally leaves one call
   of headroom; at most one may recover the same incomplete or invalid stage.
   Count
   agent attempts, continuations, retry calls, separately spawned planners,
   agent-run probes, and focused added reviewers; labels and split stages do
   not reset the budget. A clean initial review may accept the unchanged
   draft. A full second external review requires explicit owner-approved
   continuation naming the unresolved design question, scope, and limit.
4. **Review the initial design once framing is approved.** Run the risk lens
   and a genuinely independent external review of the same candidate as the
   initial review cycle, with domain review already complete where required.
   Index their immutable findings and contradictions before author revision.
   Add a focused reviewer only for a named consequential question outside
   current competence, within authority and budget. Never promote to a whole
   architecture/repo-fit panel because a verdict fails to converge.
5. **Triage before revision.** Preserve reviewer severity and wording in raw
   files. Separately classify each finding as design issue, implementation
   obligation, duplicate, preference, or unsupported, with evidence and a
   consequence for the selected alternative, user journey, public contract,
   scientific validity, or material feasibility. A design issue must also
   explain why it cannot safely wait until implementation. Give implementation
   obligations acceptance checks. Send disputed consequential or scientific
   findings to the owner; do not silently lower their severity. Treat every
   `suggested_fix` as a proposal and satisfy the underlying requirement.
6. **Revise once, then verify only what remains uncertain.** Reuse the author
   for related revision work and disposition every original finding ID. The
   driver may make explicitly scoped deterministic formatting, schema, or
   owner-approved editorial-span corrections while preserving candidate and
   provenance controls. Use narrow deterministic checks for mechanical edits;
   spend a targeted reviewer call only on unresolved judgment. A failed
   targeted verification goes to owner choice, not another automatic loop.
   No revision is required when the original draft and ledger satisfy the gate.
7. **Stop at the budget or a consequential dispute.** Present the owner with
   the surviving issue and choices to continue with a bounded scope, narrow
   the design, accept an eligible risk, or stop. Never waive scientific
   validity or silently accept a disputed consequential finding. Owner
   arbitration controls rejected blocking findings and ratifies rejected
   major findings. G2 approves the exact reviewed bytes or exact authorized
   editorial spans; material change returns to review or G1.
8. **Carry evidence into implementation.** Probe framework behavior only when
   uncertainty could change the design choice. Set at most two named probes
   with stop conditions at intake; more need owner scope. For a failed
   deterministic check, allow one scoped mechanical repair and recheck;
   a repeated failure goes to the owner. Record a required pre-change
   baseline before implementation changes make it unrecoverable. Plan future
   validation gates without demanding that implementation-only tests run at
   design time. Stage 7 retains a falsifier for every claimed runtime property
   in the existing handoff record; a requested implementation brief carries it
   forward through `task-brief`. Keep run provenance and retained exact bytes per
   `references/run-artifacts.md`.

## Workflow

1. Apply entry criteria. At stage 0, record decision framing, journey, evidence
   register, domain flag, available work budget, and acceptance plan.
2. Draft stage 1, run stage 1b domain review when applicable, and present G1.
3. If G1 redirects framing, revise the candidate within the remaining budget
   before review. Then run stage 2 risk and stage 4 external review on the
   same current candidate. Triage findings before stage 3 revision.
4. Check the reviewed version at stage 5. If needed, make one consolidated
   revision and use narrow checks or one targeted verification. Route disputes
   and budget exhaustion to owner choice; then seek exact G2 approval.
5. Finalize at stage 7 without changing approved design decisions; retain
   falsifiers and implementation obligations in the existing design or run record.
   Use `task-brief` when the user or invoking workflow requests an assignment.
   Review approval alone does not authorize implementation.

## Verification

- Before G1, check decision alternatives, journey, domain review, and
  evidence register. Before G2, check finding triage, ledger closure, call
  counts, reviewed version identity, and any narrow verification.
- Preserve raw reviews, candidate versions, gate records, and digest-resolved
  bytes. Reconcile status and files before resume or retry.
- After editing this skill, use `skill-maintenance` to check the affected
  contract. Prose corrections need inspection and relevant deterministic
  checks; changes to gates or orchestration need behavioral evidence when
  inspection cannot establish their effect. Require an independent assessor
  when the user or governing workflow calls for one. These maintenance checks
  do not replace the independent reviews inside an admitted design run.
  `brain-agent-system` owns affected activation wiring.

## Output

Report the decision, selected alternative, gate state, accepted version or
surviving issues, worker-call count against budget, and next owner action.

## References

- `references/stage-contracts.md` — load before executing a stage.
- `references/journey-and-sketch.md` — load at intake, draft, or G1.
- `references/evidence-and-gates.md` — load at intake and stage 7.
- `references/roles-and-recovery.md` — load at run start or on failure.
- `references/findings-and-closure.md` — load for triage, ledger, and gates.
- `references/external-review-brief.md` — load before external dispatch.
- `references/run-artifacts.md` — load at run start, resume, or closure.
- `references/retention.md` — load at task closure or completed legacy resume.
