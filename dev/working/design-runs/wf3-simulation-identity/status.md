---
run: wf3-simulation-identity
target-repo: blueearth_cst
genre: workflow-spec
author-binding: cst-architect
started: 2026-09-06
variant: full
stage: G1
external-rounds-completed: 0
dispatches:
  opus: 2
  fable: 1
gates:
  G1: pending
  G2: pending
flags: [intake-in-place, methodology-emphasis, promoted-lean-to-full]
---

## Run configuration

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
- [open] G1 — human gate, framing. Three framing-level findings go to the owner:
  domain-1 (blocking), domain-2, domain-3.
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
