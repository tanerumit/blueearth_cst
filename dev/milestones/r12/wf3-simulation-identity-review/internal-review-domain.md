# Internal review — scientific & methodological soundness (stage 1b)

> Lens: domain referee. Run `wf3-simulation-identity`, milestone R12.
> Reviewed: `design-v1.md` (1565 lines), against the frozen intake, the executed
> P1/P2 probes, and the repository code. Skill applied: `claim-evaluation`.
> Read-only review; no design, intake, source, config or test file was edited.

```yaml
verdict: revise
doc_version: design-v1.md
findings:
  - id: domain-1
    severity: blocking
    section: "5.4.1 Grain becomes a declared property of the metric (scope gap 4)"
    finding: >
      Class C (`wetmonth_mean`, `drymonth_mean`) is declared `grain: bundle` on a
      premise the code refutes. §5.4.1 states that "for Classes B and C the finest
      grain that *exists* is the bundle" and that "Class C pools because
      `idxmax()` selects one month and different realizations select different
      ones". Neither clause is true of Class C. Once the month is fixed, the
      Class-C value is `_month_mean` = `frame[frame.index.month == month]
      .resample(anchor).mean().mean()` (`export_wflow_results.py:173-175`) over
      `pooled = pd.concat(per_rlz.values())` (`:437`) — the identical
      "annual statistic, then mean over years" structure the design and the code
      use to justify emitting Class A per realization ("realizations are
      equal-length, so per-realization values average back to the pooled value
      exactly", `export_wflow_results.py:384-385`). For equal-length realizations
      on one calendar the pooled Class-C value is exactly the mean of the
      per-realization values, so a per-run grain both exists and is finer. And the
      month is not selected per bundle or per realization at all: `_category_month`
      is called ONCE, outside the `for st in members` loop, from the `st_0`
      baseline (`:356-365`), so the stated selection mechanism does not exist in the
      code. The correct declaration is available inside the design's own vocabulary:
      `grain: run` with `reference: <unit>`, which is what the `reference` field was
      introduced for (§5.3.5).
    rationale: >
      This is the design's central new scientific contribution — grain as a
      declared, principled property rather than an emergent consequence of loop
      nesting — and it is wrong for one of the three classes. The consequence is
      not a wrong number today (the change is output-neutral) but three durable
      costs: (a) it pins a false estimator claim into HM-7's *pinned surface* and
      into `unit_index` invariant 5, both of which are normative contract text an
      out-of-repo consumer re-implements from; (b) it violates the design's own
      decision criterion D5 ("store the finest grain, derive every summary"),
      which it invokes two paragraphs earlier to justify Class A; (c) it
      permanently discards recoverable ensemble spread for two metrics on the
      response surface — with `grain: run` a reader can see whether the wet-month
      response at a design point is consistent across realizations, and under
      `grain: bundle` that information is destroyed at write time and cannot be
      recovered from the results file. Fixing it after implementation costs a
      contract change and a baseline re-record, which is precisely the class of
      thing the intake instructs be settled once.
    suggested_fix: >
      Declare Class C as `grain: run`, `reference: <the unit whose series fixes
      the month>`, `min_blocks: None`. Separate the two ideas the current
      declaration conflates: `bundle_by` means "this value is only defined over a
      set of runs" (true of Class B), `reference` means "this value depends on a
      parameter fixed from another unit" (true of Class C). State in §5.4.1 that
      sharing a reference is not pooling.

  - id: domain-2
    severity: major
    section: "5.2.2 Why the seam is four columns and not two — the P2 correction"
    finding: >
      `derived_from` is presented purely as a DAG dependency edge, but in the
      stochastic family it is also the carrier of a methodological property: rule
      3.12's input is `rlz_{rlz_num}_st_{ST_BASELINE}.nc`
      (`run_stress_test.smk:1020`), so every design point at realization *r* is
      perturbed from the *same* realization's baseline draw. That is common random
      numbers across design points, and it is what makes a response-surface
      difference between two design points a paired contrast rather than a
      difference between two independent samples. RR-4 named this ("the composite
      identity carried a *structural guarantee*"), the intake accepted it, and the
      design answers only the completeness half (§5.1.2) and never the pairing
      half. Stage 3's `bundle_by` declares which runs share a value but not that
      contrasts between bundles are paired; the seam is family-blind by
      construction, so a family whose `derived_from` column is uniformly empty
      would produce an unpaired surface carrying no marker that says so.
    rationale: >
      This is the direct answer to the review question "what does family-blindness
      cost at the reduction". The cost is not that stage 2 computes anything wrong
      — it does not — but that a property the surface's interpretation depends on
      travels as an unlabelled side effect of a column introduced for a DAG
      reason. Two families could share a metric name and a surface while one
      supports paired inference and the other does not, with nothing in any
      artifact recording the difference. That is the same defect class as the
      unstated record-length precondition the design rightly fixes in §5.4.4.
    suggested_fix: >
      State in §5.2.2 that `derived_from` carries a paired-sampling property for
      any family that populates it, and give the family registry a declared
      `pairing` property (paired across design points / independent / none) that
      stage 3 records beside the surface, so an unpaired family is reported rather
      than assumed comparable.

  - id: domain-3
    severity: major
    section: "5.4.4 Record length as a declared estimator precondition (scope gap 6, RR-3)"
    finding: >
      `min_blocks` is self-refuting on its own terms, in two independent ways.
      (a) §5.4.4 insists it is "a constant integer floor per metric, not a function
      of config… an absolute statement about the estimator", and then sets its
      value to "the block count the shipped baseline config produces, and no
      higher" — a number read off the fixture. A threshold whose provenance is the
      fixture is exactly the "documentation wearing a check's clothes" the same
      paragraph accuses the alternative of being; it also guarantees the check can
      never fire on any shipped config, which the design states as a feature
      (C-9, GF-9) but which means the mechanism ships untested against its own
      purpose. (b) An absolute block-count floor is the wrong *shape* of
      precondition for a return level. What governs whether a GEV return level is
      defensible is the block sample size relative to the return period being
      extrapolated, and both periods are already in scope
      (`RETURN_PERIOD_PEAK_YR`, `RETURN_PERIOD_LOW_YR`,
      `export_wflow_results.py` imports both). A declaration that omits the period
      cannot distinguish a 20-year level from a 200-year level fitted on the same
      sample. I am not asserting a particular literature floor — the finding is
      that the precondition's shape omits the extrapolation and its value's
      provenance is the fixture, so it is not the "absolute statement about the
      estimator" it claims to be.
    rationale: >
      The design correctly identifies (RR-3, scope gap 6) that record length is an
      unstated estimator precondition, and correctly argues that recording it as a
      column (A7) answers a decision question with a number. But the instrument it
      chooses does not implement the argument it makes for it. Shipping a
      precondition whose value is the fixture's own output entrenches the fixture
      as the standard, and the design defers the actual calibration to Q7 while
      shipping the mechanism as if it were principled.
    suggested_fix: >
      Either express the precondition as a function of the declared return period
      (e.g. a required blocks-per-return-period ratio, still a constant per
      metric), or state plainly in §5.4.4 that the shipped value is a placeholder
      with fixture provenance and no estimator standing, and that Q7 is a
      precondition of the milestone rather than a follow-on.

  - id: domain-4
    severity: major
    section: "9. Validation plan — claim → falsifier (D8)"
    finding: >
      `min_blocks` — the design's one genuinely new scientific mechanism — has no
      falsifier. D8 requires that "every claimed runtime property needs an
      observation that would falsify it", and §9 carries eleven GF rows for
      identity, DAG and contract properties and none that exercises a
      below-threshold refusal. GF-9 asserts the opposite (that no number moves and,
      by C-9, that the refusal is unreachable on any shipped config). So the
      declared behaviour "the reducer refuses rather than fitting below
      `min_blocks`, naming the metric, the unit, the required and the actual block
      count" is never observed.
    rationale: >
      A precondition that cannot be shown to fire is indistinguishable from a
      comment. This matters more than a normal missing test because the design
      argues in §5.4.4 that refusing is the toolbox's *methodological position* —
      that a metric is emitted at declared precision or not at all — and a position
      no gate ever exercises is a position the first real configuration change will
      discover.
    suggested_fix: >
      Add a GF row: a unit test invoking the reducer on a synthetic bundle whose
      block count is one below the declared `min_blocks`, asserting the refusal and
      the four facts its message must name.

  - id: domain-5
    severity: major
    section: "9. Validation plan — GF-9; 8.2 Sequence"
    finding: >
      GF-9 — "the rename is output-neutral: no number moves", the load-bearing
      safety claim for a nine-clause migration — is not executable as written.
      Its command is `check_baseline.py check` against step 0's recording, but the
      indicator comparator keys each row on *every non-value column*
      (`_indicator_key_columns`, `dev/scripts/check_baseline.py:786-787`) and
      structurally FAILs on a "column-set or column-order mismatch" and on an
      unequal row-key set before any numeric comparison
      (`:790-797`, `:861-874`). This design changes the indicator table's columns
      from `metric, location, st_id, rlz_id, value` to `metric, location, unit_id,
      value` and changes every row key with them, so the comparator returns a
      structural failure unconditionally — it cannot report "a difference beyond a
      path rename" because it cannot compare the two tables at all. §8.2's step 3
      then re-records the manifest from the post-change code, so the only surviving
      comparison is the new recording against itself.
    rationale: >
      The design's own risk table calls the migration output-neutral (C-9, GF-9)
      and uses that neutrality to justify setting `min_blocks` from the fixture and
      to justify a single atomic commit. The task asked whether §9's falsifiers do
      what they say; this one does not, and it is the one whose failure would go
      unnoticed. A nine-clause path-and-schema migration would ship with no working
      detector for a changed number.
    suggested_fix: >
      Specify a one-off crosswalk comparison as GF-9's actual instrument: join the
      pre-change table's `(st_id, rlz_id)` keys to the post-change `unit_id` via
      `unit_index.csv` plus the scenario table, and compare `value` under
      `INDICATOR_RTOL`. It is a throwaway script, but without it the claim is
      unfalsifiable and §8.2 should say so.

  - id: domain-6
    severity: major
    section: "5.1.5 `run_historical`, without a baseline concept; 5.3.5; 5.4.3 invariant 6"
    finding: >
      The declared `reference` unit and the `evaluated` column are mutually
      inconsistent under `run_historical: false`, and the design does not state the
      constraint that would reconcile them. §5.1.5 sets `evaluated` to
      `run_historical` for the baseline row, so no run CSV is produced for it;
      §5.3.5 makes the Class-C month a lookup of a declared `reference` unit, which
      requires that unit's simulated series; §5.4.3 invariant 6 requires the unit
      index to equal "every `evaluated: true` run, plus every bundle over them".
      With `run_historical: false` the reference unit is unevaluated, so the
      Class-C metrics are either uncomputable or the invariant is violated. The
      design never states that a declared `reference` unit MUST be
      `evaluated: true`. Today's code resolves this silently: `if q_locations and
      0 in runs:` (`export_wflow_results.py:362`) leaves `wet_month`/`dry_month` as
      `None` and the Class-C rows are simply never emitted, with no log line and no
      failure — so with `run_historical: false` two configured metrics vanish from
      the deliverable unannounced.
    rationale: >
      §5.1.5 adds explicit "no silent cap" language ("the run header MUST report
      `N scenarios, M simulated`") to the exact configuration that carries a live,
      unreported metric drop in the metric the design is specifying. Making the
      month lookup indirect (§5.3.5) without stating the evaluation precondition
      converts a silent omission into an ambiguity between two normative clauses.
    suggested_fix: >
      Add to §5.4.1: a metric declaring a `reference` requires that unit to be
      `evaluated: true`, refused at parse time in `scenario_index` alongside the
      other parse-time refusals of §5.6. Add the corresponding report line for the
      metrics that would otherwise be dropped.

  - id: domain-7
    severity: major
    section: "5.4.2 Results file — normative (W2); 5.4.4"
    finding: >
      Uncertainty is not carried across the stage-2 → stage-3 seam for the pooled
      estimator, and the results schema forecloses carrying it. `return_level_max`
      and `return_level_7day_min` are GEV quantiles fitted on a pooled block sample
      (`_return_level_from_blocks`, `export_wflow_results.py:225-253`) and are
      written as a bare `value`; the four-column header W2 fixes
      (`metric, location, unit_id, value`) has no slot for a fit interval, and the
      design's answer to estimator quality is `min_blocks`, a binary admissibility
      gate, not an interval. Once domain-1 is fixed the residual is Class B alone —
      Class A and Class C would carry per-run rows from which ensemble spread is
      recoverable — but for Class B nothing in the pipeline records how well the
      return level is determined, which is the quantity a response surface's user
      needs to know whether a gradient between two design points is signal.
    rationale: >
      In a bottom-up stress test the surface is read for where it crosses a
      performance threshold. A 100-year return level fitted on a pooled block
      sample carries sampling uncertainty comparable to the perturbation-induced
      differences the surface is drawn to show, and the toolbox currently reports
      neither an interval nor the sample size. Substituting a pass/fail gate for an
      interval is a defensible position but the design does not argue it as one; it
      argues it as an alternative to a `n_blocks` column (A7), which is a different
      question.
    suggested_fix: >
      State the position explicitly in §5.4.4 — the toolbox reports admissible
      point estimates and no fit uncertainty — and record it as an open question
      beside Q7, or admit an interval via the metric declaration rather than the
      results header (e.g. a companion metric name, which W2 already permits since
      `metric` is a free vocabulary). Do not grow the four-column header.

  - id: domain-8
    severity: minor
    section: "5.4.1 (the `reference` field); 5.3.5"
    finding: >
      The `reference` field is specified as "the unit whose value fixes a shared
      parameter for every other unit", which is incomplete for the parameter it is
      being introduced to carry. `_category_month` collapses the choice over
      locations as well as over units: it sums monthly flow, takes `idxmax()`, and
      returns `int(chosen.iloc[0])` — the FIRST gauge column
      (`export_wflow_results.py:159-170`), documented as preserving pre-R11
      behaviour under ruling Q5. So one gauge's wettest month is applied to every
      gauge in the basin. A re-implementer working from §5.4.1's normative text
      would reasonably compute the reference per location.
    rationale: >
      The design's stated purpose for the `reference` field is to make an
      implicit mechanism explicit. Making it explicit while omitting half the
      collapse leaves the surviving half implicit and, worse, invites a behaviour
      change during a migration whose headline claim is output-neutrality (GF-9).
    suggested_fix: >
      State in §5.4.1 that the reference parameter is resolved once per table, not
      per location, and cite Q5 as its authority.

  - id: domain-9
    severity: minor
    section: "5.1.2 Completeness (RR-4, decision criterion D8)"
    finding: >
      The completeness predicate is largely vacuous where it is declared and absent
      where it would be needed. `scenario_families.completeness("stochastic")`
      asserts that the non-baseline rows are "exactly the cross-product `rlz ×
      st_id` **over the observed values**". Over observed values the predicate
      detects raggedness but not uniform truncation: a table missing an entire
      realization, or an entire design point, has a smaller observed value set and
      still passes. For the `stochastic` family this is harmless because the table
      is a pure function of config (§5.1.4) and cannot be truncated; for a supplied
      family — the case RR-4 and D8 exist for — it is precisely the wrong
      formulation, and such a family declares no predicate anyway.
    rationale: >
      This is the design's answer to intake question 3 ("how does stage 1 make an
      incomplete scenario set detectable?"). As written the answer holds only where
      the question does not arise.
    suggested_fix: >
      Assert the cross-product against the *configured* axes (`RLZ_NUM`,
      `ST_NUM`) rather than the observed values, which is available at the minter
      for the stochastic family; and state that a supplied family must declare its
      expected cardinality or be reported as uncheckable.

  - id: domain-10
    severity: minor
    section: "7. Consequences and risks; 10. Open questions Q1"
    finding: >
      E18 and E19 — the motivating premise (a supplied or GCM-downscaled set is not
      expressible as `(rlz, st)`) and the overlay-coordinate premise — are recorded
      as hypotheses with no artifact and are not settleable by any observation in
      this repository. The design is honest about both (§7's "the risk this design
      is least able to retire", §5.4.5's "if it is false, this ruling costs
      nothing"), so this finding names the measurements rather than disputing the
      disclosure. E18 is settled by writing a paper schema for one candidate family
      — the columns a GCM-downscaled or user-supplied set would carry, and its
      `derived_from` population — and checking whether the core four columns and
      the `stochastic` family block accommodate it; that is a desk exercise, not a
      milestone, and it is also the only available test of domain-2 and of the
      §5.2.2 family-blindness argument. E19 is settled by the same exercise.
    rationale: >
      E18 is load-bearing for the whole change: §6 A10 concedes that without it the
      benefit reduces to three measured defects. A one-page candidate schema is
      cheap relative to a nine-clause contract migration and would convert the
      design's weakest premise from argued to checked.
    suggested_fix: >
      Add the candidate-family paper schema to the design as an appendix, or make
      it a G1 deliverable, before the migration commits.
```

## Premise dispositions

Dispositions are against the evidence register of
`dev/milestones/r12/simulation-identity-intake.md` (revision 2). Where a row is
`supported`, any finding attached to it lands on the design's **inference** from
the row, not on the row.

- **E1 — supported.** Verified at `export_wflow_results.py:79-92`: the regex is
  `^rlz_(\d+)_st_(\d+)$` and `member_from_run_csv` raises `ValueError` on a
  non-matching stem. The design's problem statement §1.1 is accurate.
- **E2 — supported.** `_k_members` is a flat cross-product comprehension at
  `run_stress_test.smk:1120-1121`; the generated batch rule carries no wildcards
  and keys its log by batch id.
- **E3 — supported.** Rule 3.12 still carries `{rlz_num}` / `{st_num}`
  (`run_stress_test.smk:1004-1026`); the flattening is true of the simulator rule
  only, as the row itself states.
- **E4 — supported.** Verified verbatim at `wf3-change-requests.md:640-646`: "two
  id spaces, not one… Run identity stays `(rlz, st)`", four reasons as recorded.
- **E5 — supported.** C24 reason 3 names batching "by realization via wildcard
  patterns"; the landed rule has none (E2). The expiry is real.
- **E6 — supported.** Logs and benchmarks are keyed `batch_{_b}`; the member span
  is a banner string.
- **E7 — supported.** `INDICATOR_COLUMNS = ("metric", "location", "st_id",
  "rlz_id", "value")` at `shared/indicator_tables.py:126-132`.
- **E8 — supported.** `POOLED_REALIZATION = 0` at `:133-136` with the inline
  fragility comment quoted accurately.
- **E9 — supported.** Two bundlings do coexist in one output: Class A per
  realization (`export_wflow_results.py:386-401`), Classes B and C with
  `POOLED_REALIZATION` (`:405-426`, `:431-444`). The row is a correct record of
  what the code does. **The design's inference from it is where domain-1 lands** —
  E9 establishes that two grains coexist, not that either grain is the finest one
  that exists.
- **E10 — supported, and the design preserves the reason rather than only the
  behaviour.** The docstring at `:40-46` and `_return_level_from_blocks`
  (`:225-253`) state that pooling is of the block SAMPLE, never a spliced series,
  because splicing manufactured 7-day flows occurring in no realization. §5.4.1
  restates this explicitly and correctly. Credit where due: this is the row the
  design handles best, and it is what makes domain-1 land harder — the design
  understood exactly why Class B must be pooled and then extended the reasoning to
  Class C, where it does not hold.
- **E11 — supported.** Verified at `export_wflow_results.py:356-365`: the month is
  fixed from `st_0` and evaluated for every member. Two facts the row records
  correctly and the design misuses: the selection happens ONCE, outside the member
  loop, and it collapses over locations to the first gauge column
  (`_category_month`, `:159-170`). Cross-reference domain-1 and domain-8.
- **E12 — contested.** As recorded ("the GEV fit's precision is a function of
  realization count") the premise is true only under an unstated condition: that
  the block count alone determines whether the fit is defensible. The quantity
  being estimated is a return level at a declared period, and the adequacy of a
  block sample is relative to that extrapolation, not absolute. The docstring the
  row cites (`:27-35`) says only that a one-realization fit is ill-conditioned and
  that pooling multiplies the sample — which is a correct statement about a
  direction, not about a threshold. The design converts the row into an absolute
  `min_blocks` floor, which is the step the condition does not license.
  Cross-reference domain-3.
- **E13 — contested, hard.** The member naming pattern is pinned in **WG-4**, not
  WG-2. Verified: `weather-generator-seam.md:226` is the WG-4 heading ("generator
  output netCDFs (baseline + perturbed)"), and the clause "naming pattern:
  `rlz_<n>_st_<m>.nc` — a DAG-globbed pattern" sits at `:238-244` inside it;
  WG-2 runs `:110-190` and pins the perturbation grid. The design found this
  independently (§5.7b, finding 2) and I confirm it. The consequence is the
  intake's undercount of affected contract clauses, which the design also reports.
- **E14 — supported.** WG-5 pins one catalog entry per member including `st_0`
  (`weather-generator-seam.md:260-284`).
- **E15 — supported.** C28 is recorded as provisional with a named revisit
  trigger; the design's §5.10.2 supersession argues the trigger honestly, and its
  observation that half of C28 was already undone by R11 is corroborated by
  `interchange_contracts.py:844-850` and `indicator_tables.py:116-124`.
- **E16 — supported.** `dev/LOG.md:47` records the drop on 2026-08-18 by owner
  ruling with eight surviving references, as the row states.
- **E17 — supported as structural arithmetic.** Labelled HYPOTHESIS in the intake,
  but a sequential index over a cross-product does renumber when either factor
  changes; no measurement is needed and none would add information. The design's
  handling (W4's narrowing plus the §5.5.3 digest guard) is the right response to
  it: it accepts the renumbering and makes the resulting staleness detectable.
- **E18 — untestable as stated, and load-bearing regardless of its label.** The
  row records a belief about a scenario family for which no artifact exists in
  this repository, and it is the change's motivating premise — §6 A10 concedes
  that without it the benefit reduces to three measured defects. The measurement
  that would settle it is not a run: it is a paper schema for one candidate
  family, checked against the §5.1.2 core and the family-block registry. See
  domain-10. The design discloses this honestly in §7, which is why the finding is
  minor rather than major.
- **E19 — untestable as stated, low consequence.** That plotting a GCM-derived run
  on the T × P plane requires its (ΔT, ΔP) is argued from the geometry of a
  response surface, not measured, and no such run exists. §5.4.5's ruling
  (coordinates are stage-1 columns, WF3 never derives them) is correct as a
  boundary statement and costs nothing if the premise is false, so the row's
  untestability does not propagate into a design defect. Settled by the same paper
  exercise as E18. See domain-10.
- **E20 — supported.** `member_hash` (a content digest, a machine freshness
  boundary) and a minted sequential index (a human-and-join handle) answer
  different questions, and §5.5.4's disposition — the idea survives at TABLE grain
  as `scenario_table_sha256`, per-run digests stay out until the execution model
  has a ledger — is sound and correctly reasoned. This is the strongest section of
  the design.

## Framing-level findings

These go to the owner at G1 rather than to the author, because each is a ruling
about method rather than about specification:

- **domain-1 (blocking)** — is the wet/dry month mean a bundle-grained metric or a
  run-grained metric with a shared reference? This decides what the results file
  contains, what HM-7 pins, and whether per-realization spread survives for two
  metrics. The design's stated reason for choosing "bundle" is refuted by the
  code; the owner should rule on the corrected reading before the contract is
  written.
- **domain-2 (major)** — should the common-random-numbers pairing that
  `derived_from` carries be a declared property of a family, or is a family-blind
  seam that admits unpaired families without a marker acceptable? This is the
  scenario-neutrality price the intake asked to have priced.
- **domain-3 (major)** — Q7 in the design's own open questions. Is a fixture-derived
  block floor an acceptable shipping value for a mechanism presented as an absolute
  estimator precondition, and should the precondition reference the return period?
  The design defers this; the deferral is itself the ruling the owner should make
  knowingly.

## What a domain referee would reject

The three-stage decomposition is right, and the seam is drawn in the right place.
A hydrological simulator genuinely is indifferent to the provenance of its
forcing, and stage 2 is a legitimate place to enforce that: the design's
`derived_from` argument (§5.2.2) is the strongest piece of reasoning in the
document — it replaces "which ids are baselines", whose meaning changes with the
family, with "which rows have a forcing ancestor", whose meaning does not, and it
is backed by a probe rather than by prose. §5.5.4's treatment of `member_hash`,
§5.4.3's long-shape unit index, and §5.10's reason-by-reason supersession of C24
are all better than they needed to be. The design is also unusually honest: it
labels its own weakest premise, reports three findings against its frozen inputs,
and names three unexecuted probes rather than claiming them.

What a referee rejects is the metric-grain declaration, which is the scientific
heart of the change. The design set out to replace an emergent grain with a
declared one, and the declaration it ships is wrong for a third of the classes:
Class C is labelled a pooled estimator when its value is exactly linear in the
realizations — by the identical argument the design uses one paragraph earlier to
keep Class A per-run — and the reason given for pooling it ("different
realizations select different months") describes a mechanism that is not in the
code, which fixes the month once, globally, from the baseline. That matters
because grain is being promoted from an accident of loop nesting into normative
contract text that out-of-repo consumers re-implement from, and because the wrong
answer destroys per-realization spread for two metrics permanently. It is
correctable inside the design's own vocabulary — `grain: run` plus `reference` —
which is why it is a blocking finding rather than a fatal one.

Two further things a referee would not let pass. First, the estimator precondition:
`min_blocks` is argued as an absolute property of the GEV and implemented as a
number copied off the fixture, with no reference to the return period being
extrapolated and no gate that ever exercises a refusal — so the one new scientific
mechanism ships both uncalibrated and unfalsified, in a design whose eighth
decision criterion is that every claimed runtime property have a falsifier.
Second, and independent of the science: GF-9, the claim that no number moves, is
not executable, because the baseline comparator keys rows on every non-value column
and structurally fails on a column-set change before it compares anything — so the
migration's central safety claim has no working instrument. Neither of those
invalidates the decomposition; both must be fixed before it ships.

Uncertainty across the seam: for Class A the design carries it (per-run rows
preserve ensemble spread), for Class C it discards recoverable spread through
domain-1, and for Class B it carries none at all and the four-column schema leaves
no slot. That last one is a defensible position — report admissible point
estimates, refuse below a precondition — but the design never argues it as a
position, and a response surface read for threshold crossings is exactly the
setting where the reader needs to know whether a gradient exceeds the estimator's
own noise.
