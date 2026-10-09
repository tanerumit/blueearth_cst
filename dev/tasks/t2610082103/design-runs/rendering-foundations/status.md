---
run: rendering-foundations
target-repo: blueearth_cst
genre: decision-record
author-binding: cst-architect
started: 2026-10-10
variant: lean
stage: G2
external-rounds-completed: 1
allocation: "See allocation and execution record below"
dispatches: 5
gates:
  G1: approved 2026-10-10
  G2: pending
flags: [canonical-board-on-main, same-provider-review, allocation-revised-stage-3]
---

# Rendering foundations review state

Lifecycle: temporary run state; retain required decision evidence at task closure.
G1 uses the user's explicit approval of the saved landscape and plan, not a claim that a detailed draft
was already reviewed. Any material scope change returns to G1. G2 names exact reviewed design bytes.

## Settled framing

- Python rendering first; R/WF3 alignment is a later integration target.
- Develop a small internal Matplotlib core with a portable dependency boundary before packaging.
- Preserve scientific preparation, established plot styles and existing workflow products.
- First increment: common rendering fundamentals and bounded adoption by active WF0–WF2 callers.
- Prepared-input chart interfaces, map-reference production and external packaging follow separately.
- Stay on session-1/chore/minor-fixes for source work; no landing or push is authorized.

## Allocation and execution record

Frontier planner: default role, requested gpt-6-astra/high, fresh context; returned the eight-packet plan.
Effective model/effort are not exposed by the spawn result and remain unverified; generated role files
contain no explicit model/effort pins. Planner is planning-only. Coordinator owns final integration.
First-use allocation benchmark announced before worker dispatch; token costs/savings are undetermined.
Prior comparable diagnostics ledger absent. Maximum two concurrent workers, serial writers.

| Packet | Role | Requested model/effort | Fallback | Ceiling / dependencies |
|---|---|---|---|---|
| Draft | cst-architect | gpt-6-astra/high | 6.1-sol/high | One design; intake first |
| Domain, conditional | Domain specialist | gpt-6-astra/high | 6.1-sol/high | One review; currently waived |
| Risk | critical-thinker | gpt-6-astra/high | 6.1-sol/high | One review; draft first |
| Revision | Fresh cst-architect | gpt-6-luna/low | 6.1-sol/low | Mechanical unchanged v2; no findings |
| External | Headless reviewer | gpt-6.1-sol/high | Astra/high | One review; enforced read-only |
| Convergence/G2 | Coordinator | Current frontier session | Verified frontier | Exact revision approval |
| Baseline preflight | python-engineer | gpt-6.1-sol/medium | 6-sol/medium | Three scratch scripts; no source edits |
| Implementation | python-engineer | gpt-6.1-sol/medium | 6-sol/medium | 11 Python files + reference; G2 first |
| Diff/check review | Fresh python-engineer | gpt-6.1-sol/medium | Astra/high | One report; completed diff |

Fallback model names above abbreviate their live `gpt-` names. A fallback must meet the task's capability.
Reopen packets only for failed falsifiers or changed contracts. Diagnose tools/data before model escalation.
No nested delegation. The initial eight-file ceiling was increased before implementation to 11 Python
files plus plot-style.md: the architect found a necessary additional active subbasin caller. One baseline
preflight packet was added to materialize E7 while design authoring runs; it writes only its own scratch.
Neither change adds a source writer or expands the scientific scope. Export decoupling is a later packet.
Stage 3 allocation revised after empty risk findings: only byte-identical v1→v2 capture is required.
Use Luna/low for that mechanical operation, with no design judgments or content changes authorized.

## Stage log

- [done] 0-intake — intake.md; saved agreed landscape at main commit 1d635c47.
- [done] G1 framing — owner approved the plan on 2026-10-10; settled framing above.
- [done] 1b domain applicability — waived: this bounded extraction changes no scientific method,
  data treatment or uncertainty interpretation. If draft content does, route the domain review.
- [done] 1-draft — design-v1.md, 1,757 words; SHA256
  80602fda7fae0ad1932eb4d618f98de148b950e0090093c0aa9652afd6b1ffaf.
- [done] 2-internal-risk — approve design-v1; explicit empty findings in internal-review-risk.md.
  Required conflicts/closure recorded in internal-review-index.md; no ledger needed.
- [done] 3-revision-r1 — fresh author captured byte-identical design-v2.md; SHA256 matches v1.
  No findings or dispositions exist; no empty ledger created.
- [done] 4-external-r1 — approve design-v2.md; findings: []; observed gpt-6.1-sol/high,
  approval never, sandbox read-only. CLI reported 54,387 tokens.
- [done] 5-convergence-r1 — external approval names v2; both completed reviews have no findings.
  Explicit empty findings/disposition closure verified. No ledger, revision or second round required.
- [open] G2 — exact reviewed revision awaits owner approval; implementation remains unopened.
- [done] Baseline preflight — 167 PNGs: WF0 116, WF2 36, WF1 forcing 9 and evaluation/summaries 6.
  Commands succeeded after one scratch evaluation adapter correction; no production/source changes.
  86 WF0/WF2 retained-input hashes and 77 WF0 restored-table hashes, plus WF1 prepared-value evidence.
  Optional subbasins, missing/constant and multi-period supplemental acceptance remain pending.

## Observed dispatches and runtime preflight

- Planning-only bootstrap: gpt-6-astra/high, no writes, returned eight-packet allocation.
- Author draft: cst-architect, requested gpt-6-astra/high, fresh context, one scratch design artifact.
- Internal risk: critical-thinker, requested gpt-6-astra/high, fresh context, one findings artifact.
- Baseline preparation: python-engineer, requested gpt-6.1-sol/medium, fresh context, scratch-only writes.
- Headless permission preflight: gpt-6-luna/low, observed matching banner; approval never, sandbox
  read-only. Shell executed; an owned scratch sentinel write was denied; sentinel remained absent.
  CLI reported 21,559 tokens for this probe. This includes loaded context; no monetary savings inferred.
  Probe report/transcript retained in active scratch and will be captured with run evidence.
- Pixi environment probe: Python 3.12.13 and Matplotlib 3.11.0 imported successfully.
- Input inventory: rapid tree lacks WF0 prepared tables. Liberia retained source/comparison roots have
  tables and diagnostics metadata; Gabon lab CSVs exist. Baseline agent will prove renderer feasibility.

## Placement and provenance

Repository instructions require canonical task plans on main. This overrides the generic workflow-driver
default of storing run state in the implementation worktree. Canonical run:
`dev/tasks/t2610082103/design-runs/rendering-foundations/` in the primary checkout.
Authors write assigned scratch artifacts in session-1; the driver captures exact completed bytes into
the canonical run. Scratch is an active capture location, not the only durable home.

Installed review contract: brain-infrastructure commit c59c76091db310ad0d53ade07e42e49575057d11,
`artifacts/skills/design-review-loop/`. Installed tracked content had no local changes when inspected.
Consumed entry point and references: SKILL.md, stage-contracts.md, run-artifacts.md,
roles-and-recovery.md, evidence-and-gates.md, journey-and-sketch.md, external-review-brief.md,
findings-and-closure.md (references are below references/). Installed-byte hashes will be recorded in
this status before review dispatch. Role/model effective settings are unverified unless runtime reports them.

## Verification and approval limitations

Source inspection establishes sharing and current dependency directions; it does not establish visual
equivalence. Pre-change render baseline required before implementation. Retained input preflight pending.
Board check has eight pre-existing errors outside this task (two incomplete overview notes and two legacy
folders); current task only has a length warning. Saved plan/board commit passed git diff --check.
Internal/external design reviews and convergence completed without findings; G2 and implementation remain
pending. Detailed baseline evidence is retained as baseline-evidence.md; active images/probes remain in
session-1 task scratch until comparison is complete. No post-change acceptance is claimed.

## Allocation diagnostics — 2026-10-10, G2 handoff

Run/task: rendering-foundations / t2610082103. Workflow: lean design-review-loop, baseline preflight.
Planned packets: eight initial, one added baseline packet; domain packet waived as content-free of science.
Dispatched: one planning-only bootstrap plus five workers/reviews (draft, risk, mechanical revision,
baseline, external); one headless permission probe is counted separately.
Requested roles/models: cst-architect Astra/high then Luna/low mechanical capture; critical-thinker
Astra/high; python-engineer 6.1-sol/medium; external 6.1-sol/high. In-process effective settings unverified;
headless model/effort/isolation observed. Maximum two workers held; no concurrent source writers.
Measured CLI usage: Luna permission probe 21,559 tokens; Sol external review 54,387 tokens. Other usage,
monetary cost and savings undetermined. No comparable prior run; this record is a future baseline.
Planner overhead: one bounded planning dispatch, no model usage returned. Measured draft-to-handoff
interval: approximately 12 minutes (00:19–00:31 local), excluding initial intake and plan saving. Total
turn elapsed was not instrumented. Diagnostics captured
at handoff; this is not task completion. Rework: one evaluation-adapter signature correction; one explicit
scope expansion to include all active callers and conditional batch backend ownership. No review revisions
or model escalations. Main board commit initially rejected for dynamic scope, then passed with inspected
explicit pathspecs. Implementation has not started, awaiting exact design approval.

## Consumed contract byte identities

Pinned repository: brain-infrastructure, c59c76091db310ad0d53ade07e42e49575057d11.
Each installed file below matches its pinned Git blob; SHA256 hashes describe installed bytes.

```text
SKILL.md SHA256=d05a6677273450bda8c20151ff51e79f2777bd41d8ec5122646429bca48e0793
references/stage-contracts.md SHA256=8d27819b4734e166afe94d4c1963afe31a5ff783ba64da8d6d914fade670809e
references/run-artifacts.md SHA256=8b42b93bbf7cc8eecd7abaf4d0e384530491b09e835581ac2a703213dc0ce379
references/roles-and-recovery.md SHA256=946626b61a7b062bc5cd2c3f87810b5f5bae74d1cb9efd4deff96be6985a61d7
references/evidence-and-gates.md SHA256=da14f1cba3a2ffb482c8856000849c911d0e13e22fda76a5f3bc42d9d3cd3830
references/journey-and-sketch.md SHA256=c53f7ae05e2711db959b507f2ccb4ffe923d1facb92eea04a3c8c0740ae14022
references/external-review-brief.md SHA256=0d8a7a3ef805af02c74c0a97bf1dd1c2cfe20b2d1c59dcf1eb66f632613cfbcf
references/findings-and-closure.md SHA256=55f23a42ffc4ef1ad0cfbe38b87af54b49c1c652038bb51d726cb987b263dbc1
```

External round 1 dispatch components (frozen):
- design-v2.md SHA256=80602fda7fae0ad1932eb4d618f98de148b950e0090093c0aa9652afd6b1ffaf
- review-brief.md SHA256=6f9d66718dce57521b5a5494b8ca586fc3a082faa6f0c918089385346a4c27ad
- Settled framing supplied verbatim from this status in the brief; same-provider limitation explicit.
