---
run: wf3-simulation-identity
target-repo: blueearth_cst
genre: workflow-spec
author-binding: cst-architect
started: 2026-09-06
variant: full
stage: scope-expansion-recorded-awaiting-revision
external-rounds-completed: 0
dispatches:
  opus: 6
  fable: 1
  codex-cst-architect: 1
gates:
  G1: adapter and two-workflow scope expansions approved 2026-09-09; revised design and domain review pending
  G2: pending
flags: [intake-in-place, methodology-emphasis, promoted-lean-to-full, domain-7-needs-G2-ratification, adapter-scope-expanded, two-workflow-destination]
---

## Run configuration

**Current scope authority:** the frozen intake below, R-1..R-6 in this record,
and `scope-expansion-2026-09-09.md` (addendum v2). The owner approved broader
simulator-adapter boundaries and then two independently runnable workflows on
2026-09-09. The addendum supersedes the frozen intake's deferred workflow split;
R-1..R-6 remain in force. `design-v2.md` remains the latest authored design; it
has **not** incorporated this expansion. Do not resume external round 1 against
v2 as though it covered the expanded scope. The next author revision must
integrate the addendum and the P3/P4/P5 corrections recorded below, followed by
domain review of the changed contract before presenting the revised framing.
Prior reviews and ledger dispositions remain evidence about their named versions.

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
