# Internal review — risk & assumptions (stage 1b)

> Lens: risk & assumptions. Run `wf3-simulation-identity`, milestone R12.
> Reviewed: `design-v1.md` (1565 lines) against the frozen intake, the executed
> P1/P2 probes, `internal-review-domain.md` (to avoid overlap), and the
> repository code. Read-only; the only file written is this one.
>
> The G1 settled framing (three-stage decomposition, family-blind seam, the
> constraints table, R-1..R-4) is taken as closed. No finding below asks for a
> ruling to be reversed. Findings the domain lens already owns — Class C's grain
> (R-2), `derived_from`'s pairing property (R-3), `min_blocks` calibration and
> its missing falsifier (R-4 / domain-3 / domain-4), GF-9's broken comparator
> (domain-5), and the E18 paper schema (domain-10) — are **cited where they
> interact with a finding here and are not re-filed**.

```yaml
verdict: revise
doc_version: design-v1.md
findings:
  - id: risk-1
    severity: major
    section: "5.5.3 The stale-lookup guard — settled (and 8.3 Rollback; 9 GF-12)"
    finding: >
      The stale-lookup analysis is conducted without reference to the guard the
      repository already has, and the new guard is built in the shape that
      repository explicitly rejected. `experiment.yml` records the resolved
      `workflows.run_stress_test` section and `check_not_frozen`
      (`blueearth_cst/experiment/write_experiment_config.py:191-239`) refuses any
      change to it once the experiment has produced results. `realizations_num`
      AND the perturbation grid are both inside that section — `my_cfg =
      config["workflows"]["run_stress_test"]` at `run_stress_test.smk:94` and
      `stress_test_cfg = my_cfg["stress_test"]` at `:186`, and
      `_frozen_differences` compares the nested mapping by value
      (`write_experiment_config.py:169-171`) — so for the only scenario family
      that exists, changing the scenario set in place is ALREADY refused. Three
      consequences the design does not price. (a) §5.5.3's claim that without the
      digest "W4's narrowing is not a narrowing but a removal" is unsupported:
      the in-place case it names is already contained, and the digest's only
      novel coverage for the stochastic family is a config edit after a run that
      failed before rule 3.18 wrote the merged log — precisely the case the
      freeze deliberately PERMITS, in terms: *"Freezing at creation would be a
      different and worse feature — it would forbid the legal case to make the
      illegal one easy"* (`write_experiment_config.py:13-17`). The digest is
      written by rule 3.09 and checked at parse time, so a run that dies at 3.12
      leaves it on disk and the user's legitimate fix meets a refusal the design
      states is "not silenceable by a flag". (b) The documented remedy does not
      clear the guard: §5.5.3 says "delete the experiment's run outputs" and
      §8.3 names `climate/`, `hydrology/` and `results/`, while the digest lives
      at `<exp>/config/.scenario_table.sha256` — following the instruction
      leaves the refusal standing, and if the user did get past it the freeze
      would refuse next with a different message. (c) A second false positive:
      the canonical serialization spans the family block, whose membership comes
      from `FAMILY_COLUMNS` in code, so editing the registry moves the digest
      with no scenario changed. GF-12's falsifier inherits all of this — "change
      `realizations_num`; re-run into the same experiment; assert a parse-time
      refusal" is satisfied by a tree in which the freeze would have refused
      anyway, so it cannot show the digest is load-bearing.
    rationale: >
      This is the mechanism that makes D3's narrowing safe and that §5.10.1 uses
      to dispose of C24 reason 2, so its standing is load-bearing for the
      supersession argument, not only for a runtime behaviour. As specified it
      adds a non-silenceable refusal whose only reachable new case in today's
      configuration is a false positive, and whose stated escape does not work.
    suggested_fix: >
      Key the digest check to the same success marker the freeze uses
      (`has_run_successfully`), so it cannot fire before an experiment has
      produced results; state the precedence between the two refusals and which
      message the user sees; add `<exp>/config/.scenario_table.sha256` to the
      remedy in §5.5.3 and to §8.3's deletion list; and restate §5.5.3's
      justification against the coverage the freeze does not give (a supplied
      table changing under an unchanged config section), which is the honest one.

  - id: risk-2
    severity: major
    section: "5.1.2 Schema — normative; 5.2.3 Seam schema; 5.6 rule 3.11; 5.7b WG-4 replacement"
    finding: >
      `forcing_uri` is normative contract text asserting a stage-2 capability
      that no rule in this design implements, and the design contradicts itself
      about it. §5.2.3 lists `forcing_uri` as a required seam column and states
      stage 2 uses it for "the forcing path for a supplied family". §5.6 defines
      rule 3.11's outputs as `ROOT_IDS` = run ids with empty `derived_from`
      **and** empty `forcing_uri`, and rule 3.12 covers only rows with a
      non-empty `derived_from`. So a row carrying a `forcing_uri` has no
      producer for `<wg>/output/run_<id>.nc` at all. §5.7b's WG-4 replacement
      then enumerates the producers exhaustively as "generated *ab initio* (rule
      3.11) or by transformation (rule 3.12)" — the supplied case is absent from
      the replacement clause that is supposed to pin it. §5.1.4 point 3 leaves
      the supplied table's bootstrap at "needs the same story or a documented
      pre-run generation step", which is a sketch, not a clause. Secondarily,
      and more arguably: the intake's non-goal bars "no config surface" for a
      second family, and a nullable accommodation column is defensible under
      that, but the exclusivity rule, the acyclicity/forest rule and the "a chain
      two deep" elaboration are machinery whose only consumer is the unbuilt
      family.
    rationale: >
      The contract documents are normative and are re-implemented from by
      out-of-repo consumers (C-7). Shipping a seam column with a declared
      stage-2 use and no producer means the first attempt to use it fails with a
      `MissingInputException` against a contract that promised it works. It also
      makes GF-11's "stage 2 references no family-block column" test pass while
      stage 2 references a core column it cannot honour, which is the same class
      of unstated invariant the design exists to remove.
    suggested_fix: >
      Either (a) delete `forcing_uri` from the universal core and record in §10
      that a supplied family will need a fourth core column plus an ingest rule,
      or (b) keep it and add the missing normative clauses: which rule produces
      `run_<id>.nc` for a `forcing_uri` row, that WG-4's producer enumeration
      includes it, and a validator that refuses a non-empty `forcing_uri` while
      no ingest rule exists.

  - id: risk-3
    severity: major
    section: "4. Decision criteria (the D1/P2 tension); 5.2.2; 8.2 Sequence; 9 GF-1"
    finding: >
      The design's single highest-consequence unmeasured claim is gated only
      AFTER the migration's point of no cheap return, although a cheap
      pre-commit measurement is available now. §4 states the stake in the
      design's own words: *"If that resolution is wrong, D1 is unsatisfiable at
      this seam and the seam must move."* The resolution is the composition of
      P2 mechanism (i-c) with mechanism (iv) driven by `derived_from`, which P2
      records as **NOT PROBED**. Its gate, GF-1, runs
      `tests/test_guard_invalidation.py` against the implemented workflow, so it
      cannot be executed until §8.2 step 1 — the one commit landing two new
      shared modules, six rule edits, the reducer rewrite, nine contract clauses,
      ADR 0009 and every test — has already landed. P2 built exactly the harness
      that would answer it (`.tmp/scratchpad/2026-09-06_probe/p2/`, six
      mechanisms × two states, plus a 500-id scaling Snakefile); adding a
      seventh mechanism whose input function and alternation are both driven by
      a `derived_from` table is scratch work of the same size as what has already
      been run. Note this is not domain-10's point: that finding is about E18's
      candidate family schema; this one is about the mechanical composition,
      which needs no second family to test.
    rationale: >
      A failed GF-1 after step 1 is not a revert, it is a redesign — §4 says the
      seam moves — and §8.3's rollback story ("one commit, so one revert") is
      written for a defect, not for a structural refutation. The design already
      knows that a seeded dry-run is a measured false negative here, so the
      failure would surface late and expensively.
    suggested_fix: >
      Make the (i-c)+(iv)+`derived_from` composition a probe (P2b) executed
      before §8.2 step 1, on the standalone model P2 already has, in both states
      and with an empty `DERIVED_FROM` (which also settles GF-2's assumed
      empty-alternation semantics). Keep GF-1 as the in-workflow gate; do not
      let it be the first observation.

  - id: risk-4
    severity: major
    section: "5.8 WG-5 replacement text (cross-artifact invariant)"
    finding: >
      The replacement WG-5 cross-artifact invariant is unsatisfiable under a
      shipped configuration. It states the entry-key set equals "every `run_id`
      in the scenario table with `evaluated: true`, **and every root run whose
      series a perturbed run derives from**". The per-run catalog is written by
      rule 3.14 as a `temp()` output beside that run's TOML
      (`run_stress_test.smk:1085-1088`), and 3.14 is pull-scheduled from rule
      3.15's demand for that run's forcing. Under `run_historical: false` the
      root run is `evaluated: false` by §5.1.5, so no 3.15 job requests it, no
      3.14 job fires for it, and no catalog entry exists — while the invariant
      demands one. The existing validator has the same assumption baked in
      differently (`interchange_contracts.py:1327-1331` expects
      `m in range(0, st_num + 1)` unconditionally, i.e. `ST_START = 0`), so the
      design is inheriting a latent defect and pinning it as normative text
      rather than removing it. This is a different artifact from domain-6, which
      concerns the metric `reference` unit; the two share only the
      `run_historical: false` trigger.
    rationale: >
      §5.8 presents the set equality as the improvement over the old "realization
      × cst grid" phrasing precisely because it is "checkable for any family".
      A relational validator that fails on a supported config option is worse
      than the phrasing it replaces, and it lands in a contract document that
      out-of-repo readers re-implement from.
    suggested_fix: >
      Drop the second clause: the entry-key set equals the `evaluated: true` run
      set, full stop. An unevaluated forcing ancestor has a `.nc` (rule 3.11) and
      no catalog, which is correct and is the same asymmetry §5.4.3 invariant 6
      already handles for the unit index. State that asymmetry once, in both
      places.

  - id: risk-5
    severity: major
    section: "5.1.2 (empty `st_id` on the baseline row); 5.4.1 (`same_design_point`)"
    finding: >
      The design makes `st_id` **empty** on the baseline row (§5.1.2, "not zero"),
      defines `bundle_by = same_design_point` as "equal `st_id`, any `rlz`"
      (§5.4.1), and never states whether the empty value is a valid grouping key.
      It has to be: today's reducer iterates `for st in members` with
      `members` including `st = 0` whenever `run_historical` is set, so the
      Class-B return levels are emitted for the baseline design point
      (`export_wflow_results.py:373-427`, and `if q_locations and 0 in runs` at
      `:362` for Class C). Under the new schema the baseline's bundle is keyed by
      the empty string. Nothing in the normative text says so, and the most
      likely concrete failure is quiet: `pandas.groupby` drops null keys by
      default, so a conforming implementation silently emits no baseline
      return-level rows. The design's own instrument would not catch it —
      domain-5 establishes that GF-9's `check_baseline.py` comparator fails
      structurally on the column change before comparing any number, so the
      "output-neutral" claim has no working detector for the missing rows.
      §5.4.3 invariant 6 would not catch it either: it checks the unit set
      against the minter's namespace, and if the minter never mints the empty-key
      bundle the namespace is short in the same way the table is.
    rationale: >
      This is the closest thing in my set to a wrong-results defect. It is a
      silent row drop on a `rule all` artifact the baseline fingerprints, in the
      exact configuration (`run_historical: true`) the shipped baseline config
      uses, introduced by a choice — empty rather than a reserved zero — that the
      design makes for an unrelated expressiveness reason.
    suggested_fix: >
      State normatively in §5.4.1 that the empty `st_id` is a grouping key like
      any other, that a grouping MUST NOT drop null keys, and that the minter
      mints a bundle for it; and add a GF row asserting that the baseline design
      point carries `return_level_*` rows under `run_historical: true`.

  - id: risk-6
    severity: major
    section: "6. Alternatives considered — A3 (two sequences); 5.5.2"
    finding: >
      A3 is the weakest rejection in §6, and it is the one alternative rejected
      by deference rather than by argument: *"Rejected because W4 rules against
      it… and because the design does not need it."* Three problems. (i) W4 is
      not a ruling. It sits under the intake's *"Working direction — initial, NOT
      settled"*, which states verbatim that a design run "may test these, argue
      against them, and bring back a different answer"; and "one mixed number
      space, not two" is the driver's own inference ("Applying W4 consistently"),
      not owner text. (ii) The design does not apply that deference consistently
      — §5.5.1 openly *refines* W4 on the column name, argues the refinement on
      its merits, and flags it as the one place it does not "do the literal
      simplest thing". A criterion that is argued against in one section and
      treated as dispositive in another is not doing work. (iii) A3 is the
      alternative that removes the coupling §5.5.2 has to apologise for, and the
      apology understates it: §5.5.2 says the minter "reads one integer to size a
      field", but the same section requires bundle ids to be ordered by
      `(bundle_by name, grouping key)`, so the minter must EVALUATE stage-3
      grouping functions over stage-1 rows. A stage-1 artifact whose id strings
      are a function of the stage-3 metric set is a direct cost against S1
      ("three stages, three contracts") — the settled constraint the design
      restates in §3 — and A3 pays it off.
    rationale: >
      §6's stated purpose is that a reviewer can see each alternative was weighed
      rather than missed. A3 is the alternative most directly implied by the
      design's own admitted cost (C-4) and the one where the reasoning is
      thinnest. The prompt asked which rejection was weakest against a criterion
      the design does not apply consistently; this is it. I am not asking for
      A3 to be adopted — the two-spellings objection in A2 largely carries over
      to a prefix — only that it be rejected on the same terms as everything else.
    suggested_fix: >
      Re-argue A3 on merits (what a prefixed or high-block bundle id would cost
      in readability, joins and the `unit_id` column's uniformity) rather than on
      W4's authority, and state the coupling accurately in §5.5.2: the minter
      evaluates stage-3 groupings over stage-1 rows, and that is the price of one
      width. Then C-4 can be judged for what it is.

  - id: risk-7
    severity: minor
    section: "5.5.2 One sequence, one width, and where it is minted"
    finding: >
      The minter's bundle order is specified as deterministic
      (`(bundle_by name, grouping key)`) and the run order is not: run ids are
      minted "in scenario-table order", and nothing defines scenario-table order.
      For the stochastic family the natural candidates — rlz-major (today's
      `_k_members` at `run_stress_test.smk:1120-1121`) and st-major — produce
      different `run_id ↔ (rlz, st_id)` mappings for the same config. The
      digest cannot detect the difference, because it is computed over whichever
      order was minted. Note this has no live-tree consequence: risk-1 establishes
      that the experiment freeze already prevents a set change in place, so no
      renumbering can land under an existing tree.
    rationale: >
      Two consequences survive. The `run_id` appears in six filenames that
      `dev/baseline/manifest.json` fingerprints, so an unpinned order is baseline
      churn on any refactor of `scenario_table()`; and the mapping is exactly the
      crosswalk domain-5's suggested GF-9 instrument depends on, which cannot be
      written against an unspecified order.
    suggested_fix: >
      Pin the order in §5.1.2 as a normative property of the scenario table
      (rlz-major, baseline row first per realization, matching today's
      `_k_members`), and say the minter follows it.

  - id: risk-8
    severity: minor
    section: "5.6 Rerun triggers; 9 GF-6"
    finding: >
      §5.6 claims that passing the grain declarations through `params:` gives
      rule 3.16 a rerun trigger on a grain change. It gives it one for half the
      change space. `bundle_by` is specified as "a named function, not a column",
      so what travels through `params:` is a name; changing WHICH grouping a
      metric names re-fires the rule, and changing what `same_design_point`
      COMPUTES does not, because the function body is code and the param string
      is unchanged. GF-6's falsifier ("edit a `bundle_by`") does not distinguish
      the two, so it can pass while the hazard it was written for is live.
    rationale: >
      The design invokes the `ancient()`/no-`params:` trap by name (rule 3.09's
      comment at `run_stress_test.smk:882-887`) as the reason this matters, then
      closes only the half that a string comparison reaches. P4 is unexecuted, so
      the gate is the only evidence, and as worded it is not evidence.
    suggested_fix: >
      Word GF-6 as two cases and say which one the design closes; for the other,
      either carry a digest of the grouping registry through `params:` or state
      plainly that a code change to a grouping requires a forced re-run, as is
      already true of the reducer itself.

  - id: risk-9
    severity: minor
    section: "Epistemic labelling (front matter), and throughout §§1, 5.4.1"
    finding: >
      The label taxonomy is not applied to its own definition. The front matter
      defines `[measured]` as "an executed observation, with the command or the
      probe row that produced it". Roughly a dozen claims are labelled
      `[measured — read the function]`, `[measured — read the constant]`,
      `[measured — read the three emit blocks]`, `[measured — grep -n over both
      contract files]` and, in §5.4.1, `[measured — the two docstrings state
      it]`. Reading a line of code, and a fortiori reading a docstring's
      methodological assertion, is a conclusion from cited code — the document's
      own definition of `[argued]`. It carries no command and no probe row.
    rationale: >
      The labels are the document's mechanism for telling a reader which claims
      rest on P1/P2 and which do not, and that distinction is what §7 and §10
      rely on when they price the design's own risk. Under the present usage a
      reader cannot separate "P2 ran six mechanisms twice" from "someone read
      line 79", and both underwrite §5.10.1's C24 supersession, which is the
      argument a future reader will re-check.
    suggested_fix: >
      Either add a fourth label (`[cited]` — verified by reading, reproducible by
      opening the file) or relabel code reads as `[argued]` and reserve
      `[measured]` for the P1/P2 rows and any command actually run. The current
      count of `[measured]` claims falls by roughly two thirds, which is the
      point.

  - id: risk-10
    severity: minor
    section: "5.7b (HM-2 / HM-4 / HM-5 / HM-6b); success criterion 'normative text, not sketch'"
    finding: >
      §5.7b identifies nine affected contract clauses and supplies replacement
      text for three of them (WG-4, WG-6) plus the three the intake named (WG-2,
      WG-5, HM-7). For HM-2, HM-4, HM-5 and HM-6b it supplies an instruction —
      "take the corresponding path substitutions from §5.3.2 and change in no
      other respect" — rather than a clause. The intake's success criterion is
      "all eight scope gaps closed in normative text, not sketch", and gap 7 is
      the contract-clause gap.
    rationale: >
      Small in effort and real in consequence: §8.2 step 1 requires every live
      reference fixed in one commit, and four of the nine targets reach the
      implementer as a derivation rather than as text to paste. It is also the
      only place where the design's own §5.7b finding (the intake undercounts)
      is left half-discharged.
    suggested_fix: >
      Write the four one-line replacement clauses out, and list the validator-index
      rows at `hydrological-model-seam.md:744-763` and `:792-795` as targets with
      their new spellings.

  - id: risk-11
    severity: minor
    section: "8.2 Sequence; 8.3 Rollback; D7"
    finding: >
      "One atomic commit" conflates two different atomicity requirements.
      `naming.md` §7 and `AGENTS.md`'s "grep the old spelling and fix every live
      reference in the same commit" are about reference atomicity — no state in
      which a live document names a path that no longer exists — which is
      satisfied by a branch squashed at merge, or by a sequence in which each
      commit is internally consistent. The design presents single-commit
      granularity as forced by D7 and derives its rollback story from it ("one
      commit, so one revert"), while §8.2 itself has three durable steps (the
      pre-record, the commit, the post-record) and §8.3 concedes step 3 is "the
      point of no cheap return".
    rationale: >
      The cost is reviewability and bisectability of the largest change in the
      milestone, and the rollback claim is weaker than it reads: a `git revert`
      restores the code, not the project tree (§8.3 correctly says the remedy is
      to delete and re-run), and a failed GF-1 (risk-3) is not revertible at all
      in the sense the section implies.
    suggested_fix: >
      State the requirement as reference atomicity and allow a squash-at-merge
      branch, so the reducer rewrite, the rule edits and the contract text can be
      reviewed separately; and separate "revert the code" from "restore the
      project tree" in §8.3 rather than presenting one revert as the whole story.
```

## What I checked and did not file

- **Whether the design honours the intake's non-goals.** With the exception of
  `forcing_uri` (risk-2), it does. No GCM producer, no downscaling path, no
  model-configuration column, no user-facing grain config, no `.smk` split, no
  workflow entry point added or removed. `FAMILY_COLUMNS` and the
  `scenario_family` column are not overreach: the intake's success criteria
  require family-specific columns to be labelled, and a code registry is the
  minimum way to make that checkable.

- **Whether §5.5.4 keeps `member_hash` out correctly.** It does, and the argument
  is sound: a table-grain digest is the minimal object for the freshness question
  this design has, and per-run digests without a ledger would ship half a
  resumability mechanism. The `t2608082036` split in §5.5.5 (identity subsumed,
  execution model not) is a defensible boundary and matches `dev/LOG.md:47`.

- **`ruleorder` / A4.** Rejected on a measurement; correctly out of the option
  set. A5 and A6 are rejected against W3 and against the family-blindness of the
  stage-2 path respectively, and both rejections apply criteria the design uses
  elsewhere. A9's checkpoint rejection is consistent with D6 and with P1.

- **The alternation constraint's mechanics.** `"|".join(DERIVED_FROM)` joins the
  dict's keys, which are the derived (perturbed) run ids — the correct set for
  rule 3.12's output constraint, matching P2 mechanism (i-c). Snakemake wraps a
  constraint as a named group, so an un-parenthesised alternation does not
  mis-anchor. The 3.14 digits-only constraint at width `W` and the 3.12
  alternation do not conflict, since the two rules produce different paths. The
  2.7 s / 490-alternative scaling result is real; I checked whether a realistic
  namespace could exceed the probe's 500 and concluded the margin is adequate for
  the shipped configs.

- **`ST_START` → `evaluated` equivalence (GF-4).** The pull-semantics argument is
  correct as far as the DAG goes: `<runs>/output/run_<id>.csv` is simply never
  requested for an unevaluated row, and rule 3.12 still declares the root `.nc` as
  an input. The problems that hang off `evaluated` are elsewhere — risk-4 here,
  domain-6 for the metric `reference` unit.

- **`index_width` and C27.** `W = index_width(len(runs) + len(bundles))` is
  well-defined; `index_width` raises on a non-positive count
  (`snake_utils.py:2137-2141`), which composes correctly with the empty-set
  refusal of §5.1.4. I also checked that the `check_not_frozen` reference in
  `index_width`'s docstring is live, not stale — it resolves to
  `write_experiment_config.check_not_frozen`.

- **`build_r09_path_map` staying frozen** (§8.2 step 2) is right, and the design
  is correct to say so explicitly.

- **C-7 (out-of-repo consumers break).** Declared certain and out of scope. That
  matches the standing owner position that no decision here is gated on whether
  CST-API or the frontend consumes an artifact by path or name, so it is not a
  finding.

- **Domain-lens overlap.** I re-derived domain-1 (Class C's grain) and domain-5
  (GF-9's comparator) independently and confirmed both against the code; they are
  cited above where risk-5 depends on them and are not re-filed. R-2, R-3 and R-4
  are treated as closed.
