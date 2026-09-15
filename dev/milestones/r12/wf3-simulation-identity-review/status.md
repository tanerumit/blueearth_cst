---
run: wf3-simulation-identity
target-repo: blueearth_cst
genre: workflow-spec
author-binding: cst-architect
started: 2026-09-06
variant: full
stage: closed-accepted
external-rounds-completed: 1
dispatches:
  opus: 6
  fable: 1
  codex-cst-architect: 5
  codex-model-validator: 1
  astra-model-validator: 1
  astra-external-review: 1
  astra-scoped-verification: 2
  astra-cst-architect: 1
gates:
  G1: approved 2026-09-09; v4 correction package, provisional GEV thresholds and explicit scientific validation criteria
  G2: approved 2026-09-10; final v6 including its documented domain-7 interval deferral
flags: [intake-in-place, methodology-emphasis, promoted-lean-to-full, domain-7-owner-ratified, adapter-scope-expanded, two-workflow-destination]
round-2:
  dispatched: waived
  triggers-checked: [mechanism-changed, rejected-blocking-major]
  fired: []
---

## Run configuration

**Current scope authority:** the frozen intake, R-1..R-6, the dated scope and
naming amendments below, and the owner simplification ruling of 2026-09-10.
V5 completed a scoped Astra review with approval; v6 has now been authored to
apply the owner's approved simplification and received scoped Astra approval.
Historical reviews describe only their named versions. The final owner approval below discharges G2 and accepts the documented domain-7 limitation.

**Current naming authority:** Simulate system behavior (`simulate_system.smk`),
scenario type (`scenario_type: stochastic`), `run_id`, and `unit_id` remain.
Collection and simulation fingerprints stay internal; neither `seed_id` nor
`simulation_set_id` is an approved rename. See the owner ruling below.

**Intake is NOT copied into this run dir.** It lives at
`dev/milestones/r12/simulation-identity-intake.md` — already committed at the
durable location, cited by `dev/roadmap.md` by that path, and it declares itself
frozen once a run opens. Two copies of a frozen 39 KB document is divergence risk
for no gain, and it already satisfies the stage-7 landing checklist item (a).
Every author and reviewer brief cites that path as `intake.md`.
Flag: `intake-in-place`.

**Stage 0 was discharged before the run opened.** The intake carries all four
stage-0 obligations — derived-artifact register, evidence register,
gate-materialization check, and the framework-feasibility probes (P1–P5). It is
not re-run.

**`domain-content: yes`** — set from the intake's § Genre mapping: *"It carries a
method component: whether a hydrological simulator is legitimately indifferent to
the provenance of its forcing, and what that indifference costs at the reduction.
That component is why the run needs a method-literate reviewer and not only a
repo-fit one."* Stage 1b is therefore mandatory, and the external brief carries
the domain-referee lens set.

**No seed.** The intake § Seeding rules it: a fresh draft from the intake plus two
named inputs (`wf3-experiment-v2-design-review-record.md`, and `design-v4.md`
§3.1/§5.1 at tag `archive/wf3-experiment-v2` as *input, not starting point*).

## Scope expansion — owner approval, 2026-09-09

Owner, verbatim, after the proposal to broaden R12 to simulator adapters while
retaining the stochastic generator and Wflow as the production implementations:

> yes, lets broaden to cover as you describe

The approved direction is **explicit adapters inside the existing WF3**:
scenario generation; simulator-owned forcing preparation, execution and native
output interpretation; a response-series interface for metrics; compatibility
validation; and synthetic substitution tests. The scope and revision handoff are
recorded in `scope-expansion-2026-09-09.md`. This approval authorizes the expanded
scope, not an unreviewed implementation or acceptance of a future design version.
R-1..R-6 remain in force. The existing `run_id` / `unit_id` distinction in v2
already addresses the neutral-name concern in the proposal; no new rename is
authorized by that concern alone.

**Run transition:** return from the paused external round to scope reconciliation.
External rounds completed remains zero. Next: author a self-contained successor
to v2, refresh the changed domain review, and present its concrete framing before
resuming external review. No previous review covers the adapter expansion.

**Dispatch:** one fresh `cst_architect` author for the bounded scope addendum,
using the registered Codex role (`gpt-5.6-sol`, high). Historical Opus/Fable counts
are preserved; this dispatch is counted separately. The former provider's tier
names are unavailable in this runtime. The driver owns status and reconciliation;
the author owns only the new addendum. No nested delegation.

**Workspace:** session-3, `feat/wp3-improvements`, advisory occupied slot.
Rebased the clean, local branch onto `main` on 2026-09-09 without conflicts;
`git diff --check` passed before editing. This is a deliberate feature branch;
the scope record is committed here and the unfinished design run remains open.

## Further scope expansion — two workflows, 2026-09-09

Owner, verbatim, after the proposal for two independently runnable workflows
with three logical stages and contract extraction before entry-point extraction:

> yes, lets expand it in this direction

**Approved destination:** scenario generation produces a durable scenario
collection; impact simulation consumes it independently and exposes metrics as
an independently targetable third stage. Metrics initially remain within impact
simulation, without a third workflow entry point. The earlier approval of
adapters inside one WF3 becomes the intermediate implementation step, rather
than the final architecture. The intake and v2 remain untouched historical inputs.

**New obligations:** readiness and identity of the scenario collection; paths,
retention, cleanup ownership, and stale-input detection; independent prerequisites;
retained response inputs for metrics-only execution; and migration of the runner,
config composition, workflow names, tests, and live user references. The wider
execution-control system remains out of scope, but these handoff requirements do
not. See addendum v2 §§3, 4.7, 7, and 8 for the concrete scope and falsifiers.

**Sequence:** specify the handoff and independent-execution contracts, establish
and test them within existing WF3, then extract the two entry points. No code,
entry-point name, or config schema is selected or changed by this scope record.
No production second backend or third metrics workflow is authorized.

**Run state:** scope approval is recorded; successor design and refreshed domain
review remain pending. External rounds completed remains zero. This bounded
follow-up updates the scope record inline; no additional author/reviewer dispatch
or completed review is claimed. Existing R-1..R-6 and their review history stand.

## Successor design authoring — 2026-09-09

Owner request:

> yes, lets create the successor design first

Dispatched a fresh registered `cst_architect` author for `design-v3.md`, using
`gpt-5.6-sol` (high), counted separately from the historical provider tiers.
The author owns only that successor file; the driver owns this record. The
input set is the frozen intake, v2, ledger and original review records, all gate
rulings above, and their incorporated scope/evidence artifacts. The first write
was a recoverable draft skeleton. No nested delegation or runtime edits.

This turn is the successor-draft stage. Domain and external reviews remain
pending; neither a review verdict nor design acceptance follows from producing
the draft. Driver reconciliation checks scope, prior-ruling coverage, citations,
and structural consistency before reporting the draft complete.

**Draft delivered:** `design-v3.md` specifies the durable scenario collection,
simulator-owned forcing preparation and response interpretation, independently
targetable metrics, identity and retention rules, and the two-entry-point
migration. Its implementation sequence establishes contracts inside WF3 before
extracting the successor workflows. Proposed names and schemas remain proposals.

Reconciliation addressed current R14 config and baseline facts, acyclic seed
migration, reconstruction of identities from retained metadata, metric-blind
run-id allocation, metrics-only prerequisites, and runner/handoff ownership.
Material proposals needing review include explicit unit-id capacity and refusing
same-intent partial collection reuse until cleanup. The P2b composition probe,
target-selection feasibility, substitution fixtures, numerical migration, and
domain-7 fit-uncertainty disposition remain open gates; no execution evidence is
claimed for them. All 31 prior finding IDs remain traceable in the successor.

This is a documentation-only deliverable. Structural checks passed: all 31 prior
finding IDs and GF-1 through GF-27 are present, code fences balance, and the draft
has no trailing whitespace. SHA-256 comparison confirmed all 13 other run
artifacts unchanged. `git diff --check` passed for the status update; the staged
check also covers the newly added draft before commit.

Only documentation checks apply;
no runtime tests, scientific runs, formal review verdict, or G2 acceptance are
claimed. Prior design versions, review records, ledger, probes, and scope addendum
remain unchanged.

## Successor workflow naming — 2026-09-09

Owner approved “Simulate system behavior” and requested the change. This name
describes long-term system behavior under perturbed climate scenarios and
accommodates future non-climate scenarios without implying discrete-event
impact assessment. The destination pair is **Generate scenarios → Simulate
system behavior**.

Updated the live v3 draft in place: `simulate_impacts.smk` → `simulate_system.smk`,
the corresponding workflow stanza, seed-config filename, and runner references;
`impact_run_id` / `impact_run.json` → `simulation_run_id` / `simulation_run.json`,
with matching proposed schema, environment, and error names. The registered
`impact_model` capability slot retains its canonical name and `not_applicable`
binding. This is a naming revision only; scope, contracts, and review gates stand.
No runtime files were changed. Earlier scope/design/review records are preserved.

## Owner emphasis directive — 2026-09-06

> *"The design-review-loop run shall primarily focus on methodology, scientific
> coherence and architectural design, rather than execution-related issues."*

Recorded here, not in the intake, which is frozen. What it changes:

- **Stage 1b carries the run's weight** and takes Fable's first claim, per the
  skill's tier rule.
- **The external brief's lens set is domain-referee first** — method validity,
  scientific coherence, architectural coherence of the three-stage decomposition
  — with repo-fit and execution mechanics explicitly de-prioritised.
- **A promotion to `full` spawns the architecture lens; the repo-fit lens is
  spawned only if a finding requires it**, with the reason logged.

What it does **not** change: the risk lens still runs, the external round still
runs, both gates stand, and the convergence/ledger/arbitration contract is
unaltered. It also does not waive the two *architectural* feasibility probes —
P1 and P2 decide whether the seam this design proposes can exist at all, which is
design feasibility, not execution polish. P3–P5 ride to the task brief.

## Role bindings

| Responsibility | Binding | Tier |
|---|---|---|
| Driver | interactive session | Opus |
| Author (draft, revisions, finalize) | `cst-architect` | Opus |
| Stage 1b — scientific & methodological soundness | `model-validator` + `claim-evaluation` | **Fable** |
| Stage 2 — risk & assumptions | `critical-thinker` | Opus |
| Stage 2 (on promotion) — architecture | `cst-architect` (fresh spawn, review mode) | Opus |
| Stage 2 (only if a finding requires) — repo fit | `python-engineer` review mode | Opus |
| External | headless `codex exec` (GPT), codex-cli 0.153.2 | — |

The domain lens is deliberately **not** `cst-architect` — that is the author
binding, and reusing it would collapse author and reviewer. `model-validator` is
the fit: intake gaps 4 and 6 (metric grain; the Class B GEV's record-length
estimator precondition) are estimator questions in its scope.

`claim-evaluation` is absent from this session's skill catalog and is resolved at
`~/workspace/brain/artifacts/skills/claim-evaluation/SKILL.md` — the domain-lens
brief names that path.

## Landing target

`dev/milestones/r12/wf3-simulation-identity-design.md`, matching the
`stress-test-lookup-*` sibling naming.

## Stage log

- [done] 0-intake — outputs: `dev/milestones/r12/simulation-identity-intake.md`
  (pre-existing, revision 2, commit `d50427e4`); run dir + `status.md`
- [done] 0b-probes-P1-P2 — `python-engineer`, Opus — outputs: `probe-p1-p2.md`.
  P1 **feasible with conditions, no checkpoint**; P2 **feasible with conditions,
  but `ruleorder` measured to FAIL and the two-column seam measured insufficient**.
  Two results bind the draft: the intake's 1→2 seam spec is falsified as written,
  and the in-file claim at `run_stress_test.smk:1015` is a false negative on a
  seeded dry-run. `probe-p1-p2.md` joins the author input set.
- [done] 1-draft — `cst-architect`, Opus — outputs: `design-v1.md` (1565 lines,
  11 sections, 10 alternatives). Structural checks pass. The draft reports four
  intake/repo defects; the driver verified two of them directly (see below).
- [done] 1b-domain-review — `model-validator` + `claim-evaluation`, **Fable** —
  outputs: `internal-review-domain.md`. Verdict **revise**: 1 blocking, 6 major,
  3 minor. Evidence register dispositioned E1..E20; **E12 and E13 contested**,
  E18/E19 `untestable as stated`.
  **PROMOTION lean -> full** fires here on the first `blocking` finding
  (`stage-contracts.md` § Default and full panels): external cap lifts to 2, and
  the stage-2 panel gains the architecture lens. Per the owner's emphasis
  directive the repo-fit lens is held back unless a finding requires it —
  `domain-5` (the baseline gate is structurally unable to check this change) is
  the candidate that may force it.
- [done] G1 — **approved 2026-09-07**. Framing, constraints and decision
  criteria stand as the intake declares them; the provisional alternative (the
  three-stage decomposition with a family-blind seam) is approved. All three
  framing-level domain findings ruled **with the lens** — R-1..R-4 below.
- [done] 2-internal-panel — `critical-thinker` (risk) + `cst-architect`
  (architecture), both Opus — outputs: `internal-review-risk.md` (revise; 6
  major, 5 minor), `internal-review-architecture.md` (revise; 7 major, 3 minor),
  `internal-review-index.md`. **31 findings across three lenses: 1 blocking, 19
  major, 11 minor.**
  The risk lens died on a session limit (HTTP 429, reset 12:00 Europe/Istanbul)
  **after** writing its complete file and before returning its summary — the
  write-then-mark case in `run-artifacts.md`. Artifact verified complete on disk
  (11 findings, closing section present, verdict consistent), so it was accepted
  rather than re-dispatched. No dispatch spent.
- [done] G1-return — **re-approved 2026-09-07**. Both scope-divergent points
  ruled: R-5 (`risk-6`/C-3) and R-6 (`risk-3`). No change to the selected
  alternative, so review continues rather than restarting.
- [done] 3-revision-r1 — `cst-architect`, Opus — outputs: `design-v2.md` (2668
  lines, from 1565), `ledger.md` (31/31 rows), `candidate-family-schema.md`.
  Split **30 accepted · 0 rejected · 1 deferred · 0 withdrawn**.
  **Driver structural checks PASS** (run, not taken on report): 31 rows, no ID
  missing or duplicated, all three severity divergences preserved unharmonised
  (`arch-6` major / `risk-11` minor; `arch-7` major / `risk-8` minor; `risk-1`
  major / `arch-8` minor), `## Alternatives considered` non-empty at 12 entries.
  **R-6 discharged: E18 CONFIRMED, not refuted** — so the run does NOT return to
  G1. The confirmation rests on different ground than the intake's: the intake
  argued raggedness, which a rectangular 6x3x2 GCM set defeats;
  `candidate-family-schema.md` §3 confirms it semantically instead — `st_id` is a
  foreign key into `stress_test_lookup.csv` and a `(ssp245, 2050)` pair has no
  row there without importing WF2's change-factor computation, and `rlz` is a
  common-random-numbers index, so spelling a GCM as `rlz` asserts a pairing that
  does not exist.
- [open] 4-external-r1 — `codex exec` (GPT), clean-room on `design-v2.md`.
  Brief instantiated as `review-brief.md` (contract half immutable; framing block
  filled at dispatch from R-1..R-6).
  - attempt 1 **BLOCKED 2026-09-07 ~17:35 Istanbul** — vendor quota refusal:
    *"You've hit your usage limit … try again at Sep 8th, 2026 12:53 AM."*
    **`codex exec` exited 0 and wrote no `-o` file**; caught by checking the
    artifact, not the exit status (see `observations.md`).
    Read-only intent held: `git status --short` shows only driver-owned files.
    This is `roles-and-recovery.md` § Failure modes, row 1 (`codex exec`
    unavailable) — **pause and report; the user chooses**. Not retried, because
    the refusal names a limit and a reset time, not a fault.
  - attempt 1 **FAILED 2026-09-07 00:17** — HTTP 429, session limit, reset
    03:30 Europe/Istanbul. Classified **resource exhaustion**, not retryable
    transport (`roles-and-recovery.md` § Classifying a failed spawn). Left a
    complete 889-byte section skeleton, zero content.
  - attempt 2 dispatched 04:09 Istanbul, **after the named reset time had
    passed** — so the rung's "wait for the limit to clear" is satisfied, not
    bypassed. Briefed to **resume the partial in place**: fill the existing
    skeleton, do not restructure it. See `observations.md`.

## Driver premise verification — 2026-09-07

Two of the draft's four reported input defects, checked against the repo before
they reach G1 as claims. Both **confirmed**, and both are **pre-existing
conditions, not regressions this design introduces**:

- **E13 mis-attributes the member naming pattern.** The intake's evidence
  register cites it as WG-2 at `weather-generator-seam.md:238-245`. Line 238 sits
  under `## WG-4 — generator output netCDFs` (heading at `:226`); WG-2 begins at
  `:110` and is the *perturbation grid*, whose artifact is
  `stress_test_lookup.csv` per the validator table at `:386`. The clause belongs
  to WG-4. Consequence: the intake's scope gap 7 ("three contract clauses
  change") is counting the wrong ones.
- **HM-7's contract document is stale against its own validator.**
  `hydrological-model-seam.md:310-319` pins "exactly seven columns, in this
  order: metric, location, st_id, rlz_id, temp_change, precip_change, value".
  `interchange_contracts.py:842` asserts five —
  `metric, location, st_id, rlz_id, value` — and its own docstring at `:843-850`
  narrates the axis columns being removed. The doc did not follow. **Independent
  of this design**, and live today.

Unverified as yet, carried to G1 as the draft's claims rather than the driver's:
the nine-clause recount (gap 7), and the seam-spec insufficiency (which
`probe-p1-p2.md` measured directly).

## Driver premise verification — domain-1 (blocking), 2026-09-07

Checked before the gate, because the owner rules on this one.

**The lens's premise is CONFIRMED in code.**

- The Class-C month is fixed **once, globally**, outside the member loop, from
  the `st_0` baseline: `export_wflow_results.py:361-364`
  (`if q_locations and 0 in runs:` -> `_category_month(baseline, "wet"/"dry")`).
  The design's stated reason for Class C's bundle grain — *"different
  realizations select different months"* — describes a mechanism **that does not
  exist in the code**.
- The Class-C value is `_month_mean(pooled, month, anchor)` over
  `pooled = pd.concat(per_rlz.values())` (`:431-441`), and `_month_mean` is
  `frame[frame.index.month == month].resample(anchor).mean().mean()`
  (`:173-175`) — filter to the month, mean per water year, mean over years.
- That is the same "annual statistic, then mean over years" structure the code
  itself cites to keep Class A per-realization: *"Linear in years, so the finer
  grain averages back to the pooled value exactly and nothing is lost"*
  (`:384-385`). For equal-length realizations on one calendar the pooled
  Class-C value is therefore exactly the mean of the per-realization values, so
  a **per-run grain both exists and is finer**.

**Pre-existing condition or regression?** Mixed, and the distinction matters at
the gate. The *behaviour* is pre-existing — Class C emits `POOLED_REALIZATION`
today (`:441`). What `design-v1.md` would add is the **justification**, pinned
into HM-7's normative surface and `unit_index` invariant 5, where an out-of-repo
consumer re-implements from it. So the design does not introduce a wrong number;
it would entrench a wrong reason and permanently discard recoverable
per-realization spread for two metrics.

## G1 — owner rulings (in progress)

### R-1 — Class C's month is fixed once, shared by every realization (2026-09-07)

Owner, verbatim:

> *"wetmonth shall be the same across all realizations (needs to be selected in
> advance). We shall not pool different calendar months together for this
> metric."*

**This is a ruling on semantics, and it settles the `reference` half of
`domain-1`.** It confirms that the behaviour in the code today
(`export_wflow_results.py:361-364` — `_category_month` called once, globally,
from the `st_0` baseline, before the member loop) is **correct and intended**,
and it forbids the alternative the design's prose asserts is happening
(`design-v1.md:588`: *"Class C pools because `idxmax()` selects one month and
different realizations select different ones"*). Under this ruling that sentence
does not merely mis-describe the code — it describes a method the owner has now
explicitly rejected.

Consequences that follow without further ruling:

- Class C's `reference` field is **required, not optional**, for this metric —
  it is what guarantees one shared month, and a family that registers no
  reference grouping may not carry a Class-C metric.
- The reference stays a **per-family registered grouping** (the `bundle_by`
  pattern at `design-v1.md:570-576`), so the baseline concept lives in
  `scenario_families.py` and **W3 is parameterized rather than settled**.
- A per-realization month selection is now a **design error**, not merely an
  unchosen alternative, and the design must say so.

Still open, and put back to the owner: whether the results file stores one row
per realization (`grain: run`) or one pooled row. The ruling makes per-run
values well-defined and exactly averaging back, so both remain constructible.

### R-2 — Class C stores per-realization rows (`grain: run`) — domain-1 ACCEPTED

Ruled 2026-09-07. The blocking finding is **accepted in full**. Class C is
declared `grain: run` with a required `reference`, not `grain: bundle`.

Rationale as put and ruled: R-1 makes the per-realization values well-defined and
exactly averaging back to the pooled value, so storing the finer grain loses
nothing and preserves per-realization spread — a reader can see whether the
wet-month response at a design point is consistent across realizations or driven
by one outlier draw. This is decision criterion D5 applied as the design itself
argues it for Class A.

Accepted cost: the results file gains rows for these two metrics, so **HM-7's
pinned surface and the baseline both move**. That cost was stated at the gate and
taken deliberately.

### R-3 — the paired-sampling property is DECLARED in the family registry — domain-2 ACCEPTED

Ruled 2026-09-07. `derived_from` is not only a DAG edge: in the stochastic family
it carries common random numbers (`run_stress_test.smk:1020` — every design point
perturbs the *same* realization's baseline draw), which makes contrasts between
design points paired rather than differences between independent samples.

The family registry gains a declared field for it, so a future family with an
empty `derived_from` produces an unpaired surface **that is marked as such**
rather than one that silently reads like the current one. Prose-only was offered
and declined.

### R-4 — `min_blocks` is expressed per return period — domain-3 ACCEPTED

Ruled 2026-09-07. The precondition becomes a required
**blocks-per-return-period ratio** — one constant per metric, but a statement
about the extrapolation rather than about the sample alone, so it distinguishes a
20-year level from a 200-year level fitted on the same block sample. Both periods
are already in scope (`RETURN_PERIOD_PEAK_YR`, `RETURN_PERIOD_LOW_YR`, imported
by the reduction module), so no new input is needed.

The design must therefore **pick the ratio**: Q7's calibration becomes a
precondition of this milestone rather than a follow-on question. Shipping the
absolute floor as a declared placeholder was offered and declined.

### Panel dispatch note — repo-fit lens HELD BACK

The promotion entitles the run to both the architecture and repo-fit lenses. Only
the architecture lens is spawned, per the owner's methodology-over-execution
directive. Reason logged: the one execution-instrument defect in play — `domain-5`
(`check_baseline.py:786-797,861-874` keys rows on every non-value column and so
structurally fails on a column-set change, leaving GF-9's *"no number moves"*
claim with no instrument) — is **already filed as a major finding** and is
binding on the author's revision. R-2 sharpens it rather than resolving it: the
results file now changes both its column set and its row count, so the author
owes a working comparison instrument either way. Spawn repo-fit only if the
architecture lens or the external round raises a second instrument-level defect.

### R-5 — W4 is DIRECTION, not a ruling; A3 must be re-argued on merits (risk-6 / C-3)

Ruled 2026-09-07 at the gate return. W4 sits under the intake's
`## Working direction — initial, NOT settled` heading and carries that weight —
it is a direction a design run may test and argue against, not a decision.

**Consequence for the revision:** the single mixed sequence **stays**, but §6's
rejection of alternative A3 (two id sequences) may not rest on *"W4 rules against
it"*. It must be rejected — or accepted — on its own merits. The deference is the
defect, not the conclusion.

What made this a gate question rather than author work: the draft **already
departs from W4 once, deliberately and with reasons** (§5.5.1, two column names
over one sequence). Treating W4 as binding in §6 and as advisory in §5.5.1 is
internally inconsistent whichever reading of W4 wins, and only the owner could say
which reading to standardise on.

### R-6 — E18 is settled BEFORE G2, as a milestone precondition (risk-3, domain-10)

Ruled 2026-09-07 at the gate return. E18 — *"a user-supplied or GCM-downscaled
scenario set is not expressible as `(rlz, st)`"* — is the premise the whole change
rests on, and the intake marks it **HYPOTHESIS — asserted, no artifact exists**.
As drafted it is first testable only after the migration's point of no cheap
return.

**Required before G2:** a **one-page candidate second-family schema**, written as
`candidate-family-schema.md` in the run dir, and *checked against the design's own
scenario-table schema*. It is not a second family and ships no producer — the
intake's non-goal stands. It is the cheapest artifact that can falsify E18, and
`domain-10` proposed exactly this instrument from the method side while `risk-3`
reached the timing question from the other.

If the check fails, the decomposition is in question and the run returns to G1 —
which is precisely why it is worth one page now rather than a migration later.

## Carried to G2 for ratification — `domain-7`

`domain-7` is a **major** finding filed `deferred`. `findings-and-closure.md`
§ Ledger rules admits `deferred` only for `minor`, so the row is out of grammar,
and § Convergence requires every `major` to be accepted-and-resolved, withdrawn
by its reviewer, or **adjudicated by the user**.

The author's text is not the problem — it is more accurate than any available
enum value. The finding is correct, the design states its position, and the
substantive gap (no fit uncertainty crosses the seam; after R-2 the residual is
Class B alone) is deliberately **not** closed. `accepted` would certify a fix
that does not exist.

**Therefore: the owner ratifies or overturns this at G2.** It is not a defect in
the revision and it does not block the external round. Recorded in
`observations.md` as a skill gap — the disposition enum has no honest slot for
"major, correct, deliberately not closed".

## Probes P3/P4/P5 — executed 2026-09-07, during the external-round pause

Output: `probe-p3-p4-p5.md`. Four claims moved off `[assumed]`; one premise
falsified.

| gate | was | now |
|---|---|---|
| GF-7 (hydromt key) | `[argued]` | **measured, holds** — hydromt 1.3.1 resolves a one-entry catalog keyed `run_0007` via both `get_source` and `get_rasterdataset`. Grammar limits measured: `[`/`]` break the URI resolver, `.` truncates the key; `run_<padded int>` is safe |
| GF-6 (a) | `[assumed]` | **measured, holds** — a changed `params:` value schedules, scalar and nested-dict alike |
| GF-6 (b) | `[assumed]` | **measured, and the trap is real** — a change to a module the `script:` imports does NOT schedule, because the `code` trigger stops at the script file. The design's source-digest fix was measured to close it, and to over-fire on comment-only edits |
| GF-8 (tree-check) | `[assumed]` | **measured, holds — for a different reason than §9 states.** No inventory rule names the member token, so every renamed per-run path classifies IDENTITY under existing directory prefixes; `build_project_tree_rules` needs no change *for the rename*. But the design's two NEW files (`config/scenario_table.csv`, `config/.scenario_table.sha256`) classify **UNMAPPED** and need rows at `semantic_tree_diff.py:462-488` in the same commit |

### FALSIFIED — rule 3.09 is no longer deaf, and three R12 documents say it is

**Driver-verified.** `prepare_stress_test_grid` (`run_stress_test.smk:874`) carries
`params:` at `:880`, including `stress_test_cfg = stress_test_cfg` at `:888`. It
was added by `b5052339` (2026-08-21, the R13 config split).

The claim it refutes was **true when recorded and went stale six days later**:
`stress-test-lookup-intake.md:141` (E5) verified *"`config = ancient(config_path)`,
and the rule carries no `params:`"* on **2026-08-15**. That fact then propagated
forward and is still asserted in:

- `simulation-identity-intake.md:388` — P4's entire rationale (*"the
  `ancient()`/no-`params:` trap is live in this workflow (rule 3.09 is deaf to
  `stress_test` edits)"*)
- `stress-test-lookup-design.md:1034`, `:1170`, `:2689`

**Consequence for this run:** GF-16 case (a) is **already closed in the tree**, so
the design must not claim to close it. Only case (b) — the function-body change —
remains open, and P4 measured both the trap and the fix for it. `arch-7` and
`risk-8` were filed against the stale premise; their *mechanism* concern survives
intact (case b), their *rule-3.09-has-no-params* framing does not.

This is the second stale in-repo fact this run has caught by executing rather than
reading — the first was `run_stress_test.smk:1015`'s CyclicGraphException claim.
Both were true when written.

### Not settled without a run

The real-rule differential on 3.09/3.16. The control dry-run schedules all 43 jobs
via a consistency-rule code trigger, and `--list-params-changes` is null on the
real tree both before and after a genuine `stress_test` edit. Cheapest sufficient
experiment: `--notemp --until prepare_stress_test_grid` on
`snake_config_baseline.yml`, twice — **minutes, no weathergenr, no Wflow**.
**Authorised by the driver** as comfortably inside the owner's cost boundary,
which was set against multi-hour `RLZ_NUM x ST_NUM` Wflow runs.

**EXECUTED — 9 seconds, exit 0, 2 jobs.** Both cases now measured on the real
rule, not merely on a standalone model:

- **GF-16 case (a) — CLOSED in the tree.** Editing `stress_test.temp.mean.max`
  in `test_case/snake_config_baseline_run_stress_test.yml` scheduled 3.09 and
  *only* 3.09 (`total 1`), sole reason *"params have changed since last
  execution: prepare_stress_test_grid"*, with `--list-params-changes` naming
  `stress_test_lookup.csv`. The clean dry-run immediately before was `total 0`.
  **The design must not claim to close this** — it inherits it from `b5052339`,
  and its only obligation is not to remove that param.
- **GF-16 case (b) — measured OPEN.** With the config back at its committed
  value so `params.stress_test_cfg` was byte-identical, editing the *body* of
  `snake_utils.stress_test_grid` — the module `prepare_cst_parameters.py:23`
  imports, and the grid arithmetic itself — yielded `total 0`. Snakemake's
  `code` trigger covers `prepare_cst_parameters.py` and stops there. This is the
  case the design's source digest exists to close, and it is now measured on the
  real rule rather than predicted from a model.

### Reported, not explained — an inconsistency the probe stopped on

`.snakemake/metadata/` holds 105 records, none decoding to `test_local` (verified
twice), yet `--list-changes code` names six `test_local` paths. Stopped after
three attempts under the no-progress circuit breaker and reported rather than
rationalised. It does not change any verdict above.

## Owner-approved terminology amendment — 2026-09-09

Owner: “OK. I agree with this plan. Can you update the terms that need to change?”

Applied to `design-v3.md`: keep Generate scenarios and Simulate system behavior;
define scenario collection, scenario, design point, realization, response series,
metric bundle, metric unit, and metric versus indicator value in §2.4. Distinguish
unperturbed generated forcing, historical forcing/WF1, metric references, and the
regression baseline without resolving the deferred `st_0` comparability question.

The collection-wide stage-2 object is a simulation: `simulation_run_id` becomes
`simulation_id`, `simulation_run.json` becomes `simulation.json`, schema version
`simulation-run/1` becomes `simulation/1`, and `SimulationRunFrozenError` becomes
`SimulationFrozenError`. All v3 schemas, fingerprint formulas, paths, and prose
follow these names. The prior naming entry remains historical evidence.
`run_id` remains a collection-scoped case handle assigned before execution;
`unit_id`, grain values, mixed sequencing, and scientific calculations are unchanged.
Execution attempt denotes an actual invocation or retry, without adding machinery.

This approves terminology only. V3 remains proposed and unreviewed, with the
existing domain-review and framing gates pending. No runtime implementation changed.

## Owner-approved scenario-type amendment — 2026-09-09

The owner prefers type over family for the `stochastic` classification.
Applied throughout the proposed v3 contract: `scenario_family` becomes
`scenario_type`; registry keys use `scenario_type`; payload, artifact-list, and
artifact-inventory identifiers use the `scenario_type_` prefix. Prose names
scenario types and describes the simulator as independent of scenario type.
The terminology table defines the classification and one-type-per-collection rule.
Classification semantics, production scope, and method remain unchanged.

Earlier design/review records and the cited `candidate-family-schema.md` filename
retain their historical wording. V3 remains proposed and unreviewed.

## Review resume — 2026-09-09

Owner requests the design-review-loop process on the terminology-updated v3.
Reconciled the file-backed run: v1/v2/v3, the original three internal reviews,
index, ledger, intake, scope addendum, and probes exist; no external verdict
artifact exists and external-rounds-completed remains zero. The next stage is
the refreshed domain review, then the revised G1 framing gate before external
round 1. Prior scope/naming approvals stand; they do not pre-approve findings
that this review has not yet produced.

- [interrupted] 1b-domain-review-v3 — registered `model_validator`, GPT-5.6 Sol (high),
  task `/root/model_validator_r12_domain_v3`; output ownership confined to
  `internal-review-domain-v3.md`; no nested delegation or design edits.
- Reviewed source: `design-v3.md` at commit `7e4f5031`, SHA-256
  `19C28793BDC52CB25FC678D414C05A64F2C9D1D11E1539D9E58C8098C61D2F01`.
- Runtime substitution: the historical Fable domain-lens tier is unavailable;
  the registered model-validator binding is used and counted separately from
  the preserved Opus/Fable history. Its review artifact is writable, other
  edits are prohibited by its brief; no read-only sandbox guarantee is claimed
  for this in-process writer. The external review has a separate enforced
  read-only preflight before dispatch.
- Driver remains in the occupied, pinned session-3 feature branch; no design
  edit, scientific run, completed external round, or acceptance is claimed.

### Scientific-review model ruling — 2026-09-09

Owner: “Lets use astra for the scientific and methodological evalulations,
since they have core importance for the steps after”. This selects Astra for
scientific/methodological evaluations for the remainder of this run and
supersedes the earlier tier fallback for those stages.

Interrupted the Sol reviewer before a verdict; the only file content was the
`IN_PROGRESS` placeholder. The attempted dispatch remains counted, not treated
as a completed review. No findings were carried into the fresh Astra review.

- [done] 1b-domain-review-v3 — `/root/model_validator_astra_r12_v3`,
  `gpt-6-astra`, high reasoning; resumes the placeholder at
  `internal-review-domain-v3.md`. The registered model-validator profile has a
  fixed Sol binding, so the generic runtime surface carries the full
  model-validator persona from `.codex/agents/model-validator.toml` with the
  explicitly requested Astra model. No role file is changed. The driver owns
  status and reconciliation; reviewer owns only its report. No nested delegation.

### Refreshed domain review completed — 2026-09-09

Astra delivered `internal-review-domain-v3.md`: **revise**, 0 blocking, 5 major,
2 minor, IDs `domain-v3-1` through `domain-v3-7`, against the unchanged v3 hash
recorded above. All E1–E20 premises are dispositioned; contested/untestable
premises link to findings and settling observations. One schema correction was
returned to the same reviewer before finalization: use `untestable as stated`
and trace each contested/untestable row to a finding. The final report preserves
its author's grades and is now immutable.

The driver checked the design/code premises for same-realization ancestry,
first-gauge selection, the provisional count gate, missing stage-3 environment,
and capacity in seed material. No scientific run or numeric equivalence claim
was made. `internal-review-index-v3.md` records every new finding, preserves the
old fit-interval question separately, and contains the proposed G1 correction
package. The previous index and ledger remain unchanged.

- [done] 1b-v3-index-and-structural-check — report verdict/version/counts, E1–E20
  coverage and finding traceability checked; design hash unchanged; all 27 GF
  identifiers present, alternatives nonempty, fences balanced; diff whitespace
  checked. Reviewer artifact and index exist before completion is marked.
- [open] G1-v3 — retain approved framing; rule on the proposed bounded v4 fixes
  and whether return-level screening thresholds require the proposed validation
  criterion or explicit limited-applicability acceptance. No implementation is
  requested by this gate. The historical Class-B interval deferral stays at G2.
- [pending] author revision and ledger dispositions — all seven new IDs await
  G1, then a fresh author; no ledger closure claimed.
- [pending] external-r1 — clean-room review after the revised framing/author
  steps, with scientific/methodological evaluation on Astra. External rounds
  completed remains zero; no external sandbox/auth check or dispatch is claimed.

Current review artifacts and status remain uncommitted at this human gate under
workflow-driver's commit-gate discipline; all content is saved in this worktree.

## G1-v3 ruling and v4 author dispatch — 2026-09-09

Owner: “yes, lets go for the  v4”. This approves the correction package presented
in `internal-review-index-v3.md` and the recommendation to retain provisional
GEV ratio/floor values while adding explicit scientific validation criteria.
It does not ratify the numbers as scientifically adequate, approve the historical
fit-interval deferral, or authorize a runtime implementation/scientific run.

- [done] G1-v3 — retain the two workflows, three stages, production stochastic
  scenario type/Wflow bindings, terminal CMIP overlay, and approved terminology.
  Address all seven `domain-v3-*` findings; distinguish minimum-sample screening,
  fit validity and scientific adequacy; specify a bounded validation plan before
  the provisional thresholds may be described as scientifically validated.
  No automatic ratio-2.0 substitution, estimator change, partial-year removal,
  or addition of fit intervals. The historical `domain-7` ruling remains at G2.
- [done] author-revision-v4 — fresh `cst_architect` on its registered
  GPT-5.6 Sol/high binding; owns only `design-v4.md` and append-only additions to
  `ledger.md`. First action copies v3 forward as a recoverable draft. Inputs are
  the frozen intake, v3, cumulative ledger, authoritative Astra review and this
  gate record, with read access to the repository. No nested delegation.
- Astra remains the binding for scientific/methodological evaluation of the
  resulting revision; authorship and evaluation are separate responsibilities.

The driver owns status and structural reconciliation, not design authorship.
V1/v2/v3 and all review artifacts remain unchanged. No commit before the run's
commit gate and no external review completion is claimed.

### External-review preparation during v4 authorship — 2026-09-09

Located codex-cli 0.153.2 at
`C:/Users/taner/AppData/Local/Programs/OpenAI/Codex/bin/codex.exe`; it was absent
from the restricted shell PATH but resolved in the approved host inspection.
The direct `codex sandbox` attempt required a named permission profile and ran
no probe. The actual `codex exec --sandbox read-only -c approval_policy=never`
preflight succeeded: banner reports read-only and approval never; design read
succeeded; shell write to `external-sandbox-probe.txt` was denied; that file
was not created. Evidence: `external-sandbox-preflight.md` and the two
`external-sandbox-preflight*.log` transcripts. The mechanical preflight used
GPT-5.6 Sol/low and is not a scientific evaluation or an external review round.

Prepared `external-review-r1-brief.md` from the immutable contract, refreshing
only round/task/framing content for v4 and excluding earlier review/ledger inputs.
The external scientific reviewer will use Astra under the owner's model ruling.
Because the v4 author uses Sol, this is model-family diversity within OpenAI,
not vendor diversity; the resolved brief states this explicitly. No review has
been dispatched yet and external-rounds-completed remains zero.

### V4 released and external round 1 dispatched — 2026-09-09

The author released `design-v4.md`, SHA-256
`5511344AE8D0EA818723734A986B119A80EE524DFEA61C397975613205B5AE55`,
2,067 lines. All seven v3-domain findings have new part-by-part ledger rows;
all are accepted, none rejected or deferred. Old ledger rows are unchanged.
The body budget rises to 2,100 lines with an explicit justification for the
new contracts. New scientific test-grid/tolerance numbers remain author proposals
awaiting Astra; no execution or methodological validation is asserted.

Driver checks: prior v3 and reviewer hashes unchanged; ledger +20/-0;
GF-1..GF-28 and all seven original IDs present; code fences balanced; author
in-progress markers removed; diff whitespace passed. Historical `domain-7`
fit-interval deferral remains for G2 ratification, not silently closed.

- [open] 4-external-r1-v4 — headless codex-cli 0.153.2, `gpt-6-astra`, high
  reasoning, read-only sandbox, approval never, ephemeral. Inputs confined to
  `external-review-r1-brief.md` and v4 plus necessary directly cited factual
  sources; previous review/index/ledger/status excluded. No nested delegation.
  Final output: `external-review-r1.md`; transcript: `external-review-r1.log`.
  External-rounds-completed remains zero until a valid final verdict exists.
  The single-vendor/model-family-diverse posture follows the owner's Astra
  choice and is explicit in the brief. Scientific run count remains zero.

### External round 1 / immediate convergence check — 2026-09-09

The headless Astra process exited 0 and produced `external-review-r1.md` with
`verdict: revise`, `doc_version: design-v4.md`, and `ext1-1` through `ext1-4`,
all **major** (0 blocking, 0 minor). This is the first completed external round.
The verdict and four complete findings are consistent; the reviewed v4 hash
remains `5511344AE8D0EA818723734A986B119A80EE524DFEA61C397975613205B5AE55`.
Post-run Git state has only authorized driver/author artifacts; no reviewer edits
are visible. The transcript confirms model gpt-6-astra, sandbox read-only and
approval never. The report is immutable.

- [done] 4-external-r1-v4 — output `external-review-r1.md`.
- [done] 5-convergence-r1 — **not converged**, checked before any design edit:
  verdict revise with four unresolved major findings. No acceptance or ledger
  closure claimed. The previous `domain-7` interval decision remains at G2.
- Driver premise checks: ext1-1 gives an analytic location-scale counterexample;
  current preparation has `data_sources`, `clim_source`, and `oro_path` inputs
  matching ext1-2; v4 §8.4 includes response/ref-month-dependent metric identity
  matching ext1-3's planning dependency; ext1-4 distinguishes complete unit
  membership from exact emitted metric/location/unit keys. Findings retain their
  filed grades; the author must disposition every suggested-fix part.
- [done] 6-revision-v5 — fresh cst-architect persona on gpt-6-astra/high.
  `ext1-1` faults the resolution of earlier `domain-v3-3`, so this is the loop's
  stronger-tier revision-on-re-raise step, consistent with the owner's Astra
  preference for scientific judgment. The runtime generic surface loads the
  full cst-architect role because its registered profile is fixed to Sol.
  Own only `design-v5.md` and new ledger rows; preserve v4 and review files.
  No nested delegation or code/scientific run. If a fix changes approved framing
  rather than filling the contract, report for G1 before proceeding.

After v5, check both round-2 triggers. No blocking finding exists in round 1;
if every major is accepted, use the required scoped Astra delta verification
rather than silently accepting v5 or automatically spending another full round.

### V5 release, round-2 trigger check and scoped verification — 2026-09-09

Author released `design-v5.md`, SHA-256
`4926E14D347448A358A45000F5845D9500561ECB5A38EC3F7FE8EEE6B1537C7B`,
2,376 lines, ceiling 2,400. All four external majors accepted part by part;
ledger is append-only (+18 this revision, +38 total vs HEAD); v4 unchanged.
The revision supplies a scale-normalized estimator benchmark and bounded policy
qualification, a complete preparation-context/ancillary inventory, two explicitly
scoped scheduling checkpoints, and exact expected result-key validation.
These remain proposed contracts and author-proposed scientific criteria.

- [done] 6-revision-v5 — outputs v5 and ext1-1..4 ledger rows. No rejection or
  framing change reported. GF-1..31, original finding coverage and released hash
  verified by driver; author additionally checked all five JSON examples and
  balanced fences. Captured exact `v4-v5.diff` for the reviewer.
- [done] round-2-trigger-check — **full round 2 WAIVED**. Trigger 1 absent:
  external round 1 had no blocking findings, so no blocking fix changed a
  mechanism. Trigger 2 absent: all four majors accepted, none rejected.
  New checkpoint mechanisms still require the scoped pass; the waiver is not
  approval or evidence of their execution.
- [done] scoped-verification-v5 — independent headless Astra/high, same enforced
  read-only/approval-never posture, input `scoped-review-v5-brief.md`, v4/v5,
  captured delta, external round-1 findings, and their new ledger dispositions.
  Output `scoped-review-v5.md`; transcript `scoped-review-v5.log`. This is the
  required delta check, not a second full external round. Model/vendor diversity
  is not claimed: author and verifier both use Astra under owner preference.
  No scientific execution or final convergence is claimed yet.

### Scoped verification complete / G2 package — 2026-09-09

The headless Astra verifier produced `scoped-review-v5.md` with **approve** for
`design-v5.md`, scoped to the v4-to-v5 delta. It verifies ext1-1..4 individually
as resolved at design stage and reports **no new findings**. The process exited
0; the captured diff matches the designs; no edits, tests or scientific runs
were made by the reviewer. V5 retains release hash
`4926E14D347448A358A45000F5845D9500561ECB5A38EC3F7FE8EEE6B1537C7B`.

- [done] scoped-verification-v5 — authoritative result `scoped-review-v5.md`.
- [done] pre-G2 structural check — valid verdict/version, all four original
  external IDs verified, unchanged reviewed v5, original versions and reviews
  retained, ledger additions cover all seven v3-domain and four external IDs
  part by part, no new findings or rejected blockers/majors, alternatives and
  GF-1..31 present, JSON examples/fences checked by author, diff whitespace
  passed. Full round 2 remains waived with both triggers absent.
- [open] G2-v5 — approve the reviewed design unchanged and explicitly ratify or
  overturn the historical `domain-7` Class-B fit-interval deferral. Its cost is
  unchanged: response-surface consumers cannot distinguish a gradient from
  estimator noise using intervals that the outputs do not carry. The driver
  does not withdraw or re-grade that historical major finding.

Review-path completion is established under the scoped-delta exception; full
ledger convergence still needs the owner's domain-7 ruling. Design approval
would not ratify provisional GEV values or numerical benchmark tolerances as
scientifically validated and would not authorize an implementation or model run.
GF-15 retains its separate prior-criteria approval and execution obligations;
benchmark success alone does not establish screening-policy validity.
P2b, operation/target enforcement, GF-29/GF-30 checkpoint composition, GF-31
preparation portability, GF-10 result integrity, GF-9 numerical migration,
GF-27/GF-28 seed/calendar preservation and stage validation remain empirical
implementation/scientific gates, not results of this prose review.

Nothing is staged or committed before G2/finalization. All run artifacts are
saved in this worktree, with raw transcripts retained under the run directory.
The maintained-current landing target remains the milestone design path already
recorded above; no promotion or cleanup has been performed.

## Owner simplification ruling — 2026-09-10

The owner asked whether to drop or hide collection_id and simulation_set_id,
proposing seed_id and model_setup/config alternatives. After the recommendation
to hide machine identities and retain internal provenance, the owner answered:
"yes, lets do that". This approves the following v6 change package (G1 amendment),
not final G2 acceptance or the domain-7 fit-interval deferral.

- Ordinary use exposes experiment_name, scientific generation settings (including
  the actual random seed), model/simulation settings, run_id, and unit_id.
- Collection and simulation fingerprints remain computed internal provenance for
  exact reuse, stale-result rejection, and reproducibility. They are not required
  user parameters. Keep existing internal schema names unless a change is needed
  for this simplification; do not rename collection_id to seed_id or simulation_id
  to simulation_set_id/model_config/model_setup.
- Ordinary flow is generate forcing, simulate system, calculate metrics. Resolve
  the matching generated collection automatically from this project's settings;
  no copying hashes, manifest paths, or required selector in the routine scaffold.
  Specify deterministic resolution/default behavior and actionable failures.
- Retain independent generation, direct simulation, metrics-only execution, and
  optional advanced manifest reuse. Defer convenience tooling for managing several
  collections. No new GCM producer or change to production stochastic scope.
- Preserve all scientific decisions, exact identities, readiness/content checks,
  planning checkpoints, ID capacity safety, and existing validation obligations.
  Present internal/advanced controls separately without silently changing them.
- Revise v5 into a self-contained v6, updating terminology, configuration, examples,
  summaries, and acceptance criteria consistently. Preserve v5 and past reviews.
  Add an owner-change traceability entry distinct from reviewer findings.

Execution: fresh cst-architect author (registered Sol role) owns design-v6.md and
append-only ledger entries. Driver owns this status and scoped review artifacts.
Astra will review the changed interface/default-resolution contract and verify
that scientific contracts remain intact before v6 returns to G2. This is a scoped
verification, not an additional completed external round.

### V6 review execution preparation

The installed headless CLI was rechecked on 2026-09-10: codex-cli 0.153.2,
matching the successful actual-exec read-only/approval-never preflight recorded
in external-sandbox-preflight.md. The restricted parent cannot list the host
installation directory; the host version probe succeeded. The review will use
the same executable, explicit --sandbox read-only and -c approval_policy=never;
its effective banner and post-run artifact state will be checked. No unsafe
review execution is authorized or needed.

### V6 author release and scoped verification — 2026-09-10

Author released design-v6.md, 2,443 lines, SHA-256
`8D16B78D488443F6A3160DC9D4E12B247DCD65179FAA87A9BAA1D72123394407`.
V5 remains byte-identical; owner-v6-interface is an owner change, not a finding.
Author checks passed: balanced fences, five JSON examples, GF-1..32 coverage,
ten capability slots, no partial markers/trailing whitespace, diff whitespace.
The 43-line budget exception preserves previously reviewed contracts.

Both full-round-2 triggers checked again: no blocking fix changed a mechanism,
and this owner revision rejects no blocking/major finding. Full round 2 remains
waived; historical domain-7 still requires G2 owner ratification. The material
interface delta receives a scoped Astra pass with scoped-review-v6-brief.md and
v5-v6.diff. No scientific/runtime gate has run. No commit or promotion authorized.

- [done] v6-author
- [in-progress] scoped-verification-v6 — headless Astra, high reasoning,
  enforced read-only/approval-never; review output pending.

V6 dispatch banner confirmed model gpt-6-astra, reasoning high, approval never,
sandbox read-only, correct worktree. Initial WebSocket HTTP 503 reconnects were
followed by successful tool execution reading the delta in the same process;
no reviewer re-dispatch or permission downgrade occurred. Driver independently
confirmed the cumulative ledger retains its entire pre-v6 prefix unchanged and
git diff --check passes. Review remains in progress.

### V6 scoped-review completion and G2 package — 2026-09-10

- [done] scoped-verification-v6 — scoped-review-v6.md gives verdict approve,
  doc_version design-v6.md, with zero blocking, major or minor delta findings.
  All five review questions passed. The model was Astra under the owner's
  scientific-evaluation preference; author was the registered Sol CST architect.
- [done] mechanical convergence check immediately on receipt — valid approval
  for the candidate, no new findings to disposition; unchanged historical
  domain-7 still prevents full ledger closure without its owner ruling.
- [done] pre-G2 checks — v1..v6 retained; nonempty alternatives and decision map;
  prior findings and their dispositions preserved; complete pre-v6 ledger prefix
  unchanged, with owner-v6-interface appended separately. Author's JSON/fence,
  capability-slot and GF-1..32 checks passed. Driver git diff --check passed.
- [done] isolation backstop — effective read-only/approval-never banner checked;
  final v5, v6 and ledger hashes match their pre-review values. Git status has
  only expected driver/author artifacts and the captured review; no runtime file
  changes. The review transcript and report are the review-window outputs.
- [open] G2-v6 — approve reviewed v6 and explicitly ratify or overturn the
  historical domain-7 Class-B fit-interval deferral. The 2026-09-10 yes approved
  simplification, not that separate methodological tradeoff.

Reviewed v6 SHA-256:
`8D16B78D488443F6A3160DC9D4E12B247DCD65179FAA87A9BAA1D72123394407`.
V6 remains unchanged after review; its author-time pending-review banner is
historical to the frozen candidate, and this status plus scoped-review-v6.md
record the subsequent approval. Full external round 2 remains waived; the two
completed scoped passes are not counted as full external rounds.

GF-32 default/advanced/retained-resolution fixtures are newly required empirical
checks. Prior P2b, GF-9, GF-15, GF-27..31 and model-validator handoffs remain
unexecuted. No scientific-policy validation, implementation, model run, commit,
promotion, or run-directory cleanup is claimed. All requested v6 design changes
and their scoped review are complete and saved in this worktree. Finalization
waits at G2; the maintained milestone landing target remains unchanged.

## Final owner approval — 2026-09-10

Owner, verbatim: "yes, I approve this final design."
This approves reviewed v6 unchanged, including its documented Class-B fit-interval
deferral, which the immediately preceding final response explicitly identified.
The driver records acceptance of that disclosed scope limitation; no reviewer
finding is withdrawn or downgraded, and no empirical validation is implied.
G2 is discharged. No new editorial or material design changes were requested.

Stage 7 authority: finalize the accepted design at
`dev/milestones/r12/wf3-simulation-identity-design.md`; lifecycle maintained-current,
revision history append-only. Preserve the reviewed v6 and review reports. The
final author may only update acceptance/lifecycle status, append the G2 revision
entry, reconcile resolved pending-G2 wording and repoint artifact citations.
All normative/scientific/interface content remains the reviewed v6 contract.

Archive source records verbatim in
`dev/milestones/r12/wf3-simulation-identity-review/`, preserving filenames. This
repository retains milestone audit evidence and forbids broad deletion without
specific confirmation: copy durable records; retain the closed working record
for existing historical references, without deleting/moving the source tree.
The frozen intake is already beside the accepted design and is not copied.
The driver adds the final status/ledger snapshots to the archive after completion.
Final author owns only the accepted design and copied archival md/diff artifacts;
driver owns status, ledger arbitration, roadmap and board bookkeeping. No nested
delegation, implementation, runtime execution, branch landing or push is authorized.

## Stage 7 completed — 2026-09-10

- [done] G2 — owner approved reviewed v6; domain-7 scope limitation ratified and
  recorded as an owner-adjudicated rejected major, not withdrawn or downgraded.
- [done] final-author — accepted maintained-current design at
  `dev/milestones/r12/wf3-simulation-identity-design.md`. Only acceptance metadata,
  lifecycle, durable citations, resolved G2 wording and acceptance log changed.
- [done] archive — all 29 source md/diff records copied verbatim to
  `dev/milestones/r12/wf3-simulation-identity-review/`; intake already lives beside
  the design. Closed working copies remain for historical citations and safe
  retention; no destructive source-tree pruning was performed.
- [done] derived planning — roadmap R12 rewritten from the accepted contract;
  milestone index updated; backlog t2609100916 and preparation task brief created.
  Current operational seams, rules, generated baseline and decision supersessions
  are assigned to implementation rather than prematurely describing unbuilt code.
  The old t2608082036 broad execution-platform obligations are explicitly abandoned
  as automatic R12 requirements in the roadmap. st_0 comparability remains separate.
- [done] structural checks — final author's 29/29 archive hash equality, durable
  citation existence, fence balance and no trailing whitespace; driver reviewed
  the entire finalization delta and git diff --check passed on tracked docs.
- [done] review-loop — one full external round plus two scoped Astra approvals;
  full round 2 waived with both triggers absent; final dispatch counts are above.

Accepted design SHA-256:
`6B322CA2DF27F25F78B4581D43AD85CCD664C478E35DE2751252BB6098CDF4DF`.
Reviewed v6 SHA-256 remains:
`8D16B78D488443F6A3160DC9D4E12B247DCD65179FAA87A9BAA1D72123394407`.
All scientific/runtime gates remain unexecuted. Design approval authorizes this
finalization, not model execution or implementation. Commit gate is released on
the pinned feature branch; merge/push/task-land were not requested.
