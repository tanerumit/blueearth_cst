# Internal review — RISK & ASSUMPTIONS lens

Target: `dev/working/design-runs/wf3-experiment-v2/design-v1.md` (design-v1.md, 1903 lines)
Reviewed under the G1 settled framing (4-stage skeleton, manifest+ledger sweep, Julia
pool, 3-layer drift guard, OQ-1 deferred entirely, OQ-4 fail-loud + `allow_partial`,
index ids, zero new deps). None of those are re-litigated below; every finding is about
how well the design implements them.

## Reading of the load-bearing assumptions

A1 (single writer) is delivered for `_state/` but **not** for the experiment tree —
the lock is claimed at sweep start, three stages too late (risk-6). A2 is verified
(`dev/contracts/hydrological-model-seam.md:217` — per-cst TOML keeps
`cold_start__flag = true`; `config/templates/wflow_sbm.toml:26` `reinit = true`). A3 is
verified at the call site (`blueearth_cst/weathergen/impose_climate_change.R:45-57`
passes no `seed`). A5/A6 are unremarkable. **A4 is the weakest and the design knows it,
but the falsifier it points at cannot discriminate** (risk-3, risk-4).

The single most damaging finding is not in the assumption list at all: the freshness
boundary `member_hash` covers the member's *outputs* and its *hydrology* inputs but
**none of its generation-side inputs** (risk-1). That converts the sweep's own
incrementality into a silent-wrong-science path.

## Traceability note

Every finding below cites the design line/section and, where a factual premise is
involved, the repo file:line that establishes it. Repo facts were read, not assumed;
no wflow / weathergenr / hydromt / pixi execution was performed.

---

```yaml
verdict: revise
doc_version: design-v1.md
findings:
  - id: risk-1
    severity: blocking
    section: "§5.1 member_hash / §7.3 the resume fold / §7.6 What forces full invalidation"
    finding: >-
      `member_hash` is defined (design:588-595) over
      `{member_id, rlz, cst, baseline, st_csv_digest, tavg, prcp, precip_variance,
      run_config_digest}`, and `run_config_digest` is enumerated as
      `horizontime_climate, run_length, clim_source, data_sources, base wflow_sbm.toml
      digest, staticmaps digest`. It therefore covers **no generation-side input**: not
      `master_seed`, not the derived `seed_r`, not the baseline
      `rlz_<n>_cst_0.nc` the member's perturb step actually reads, and not
      `config/templates/weathergen_config.yml` (whose `seed: 123` at line 17, and every
      other generator knob, changes the realizations). Consequently the §7.6 row
      "`master_seed` → every realization's seed changes ⇒ regeneration ⇒ **every member
      invalidates**" (design:1095) is false as specified. Trace the actual path: editing
      `master_seed` flips a `params:` value of 3.01 → manifest rewritten (new `seed_r`
      per realization, byte-identical `member_hash`es) → 3.05/3.06 regenerate the
      baseline NCs → `run_sweep`'s declared `rlz_nc` input changed, so Snakemake
      correctly re-enters the sweep rule → the runner folds the ledger and every member
      matches on all four reuse conditions (§5.5: `member_hash` match, terminal
      `succeeded`, artifacts present, digests verify) → **every member is SKIPPED** →
      `ledger_final.csv` is written and the reduce runs. The reuse predicate inspects
      the ledger's `outputs` object only (`{"result":…,"toml":…}`, design:631) — it
      checks the member's *outputs*, never its *inputs* — so a changed input under an
      unchanged `member_hash` is structurally invisible.
    rationale: >-
      Observable consequence: after any generation-affecting edit that is not also a
      hydrology edit, `indicators/Qstats.csv` and `response_long.csv` are published from
      member CSVs computed against the PREVIOUS realizations, while
      `weather_generator/output/rlz_*_cst_0.nc` on disk hold the NEW ones and
      `members.json` records the new seeds. The run's own provenance record asserts a
      pairing that never existed. Nothing fails, nothing warns, `sweep_status.py` reports
      all-done, and no gate in §8.2 covers it (GF-5 injects `run_length`, which *is* in
      `run_config_digest`). Re-seeding a stress test is routine CST practice, so this is
      a reachable operation, not a corner case. It also silently defeats G2 ("resume is
      measured, not asserted") and the §5.5 reusability contract the design claims to
      have adopted. The design already identified and solved exactly this class one
      paragraph earlier for `staticmaps.nc` / `wflow_sbm.toml` (design:596-607, "stale by
      construction") — it simply did not apply the same reasoning to the member's primary
      data input.
    suggested_fix: >-
      Stage ordering blocks the obvious fix (the manifest is written before the baselines
      exist), so put the check at sweep time: the runner digests each
      `rlz_<n>_cst_0.nc` once per invocation, records `baseline_digest` on every
      `succeeded` ledger row, and adds "recorded `baseline_digest` == live
      `baseline_digest`" as a fifth reuse condition in §5.5 / §7.3 step 5 (mismatch ⇒
      QUARANTINE, RUN). Independently, fold `seed_r` into `member_hash` and make
      `config/templates/weathergen_config.yml`'s content digest a `params:` value of
      3.01 and 3.05 (the `file_digest_or_absent` pattern already used at
      `Snakefile_climate_experiment:174-175`) — today it is passed only as a path string
      (`prepare_weagen_config.py:56, default_config_path`), so editing the template
      re-triggers nothing at all. Add a gate: GF-12 "change `master_seed`, re-invoke,
      require every member to re-run and every member CSV mtime to change".

  - id: risk-2
    severity: blocking
    section: "§9.4 OQ-4 — reduce with holes / §8.2 GF-7"
    finding: >-
      §9.4's `allow_partial` column states "`Qstats.csv`: grid with holes; the missing
      `(tavg, prcp)` rows simply absent". Read against the reduction that the design
      commits to keeping byte-stable (§4.4), this is wrong in both of its two possible
      sub-cases, and the fixture config makes the wrong one the default. Under
      `aggregate_rlz: true` — the value in
      `config/workflows/snake_config_model_test.yml:80` — the loop bound is `st_num`,
      not `len(csv_fns)`, and every output frame is pre-allocated with `st_num` rows
      (`export_wflow_results.py:99-108,131-147,153`), so a hole cannot manifest as a
      missing row. Instead: (a) if *some* realizations of `cst_m` are missing,
      `csv_fns_i` is shorter, `pd.concat` yields fewer years, the fabricated
      `pd.date_range` (`export_wflow_results.py:163-165`) is shorter, and the cell's
      statistics are computed over fewer realization-years while being written into a row
      that is indistinguishable from a complete one; (b) if *all* realizations of `cst_m`
      are missing, `csv_fns_i == []` and `pd.concat([])` raises
      `ValueError: No objects to concatenate` — a loud crash from a code path the design
      believes is a supported posture.
    rationale: >-
      Observable consequence in case (a): a response-surface cell is silently
      under-averaged. `indicators/completeness.csv` is per *member*, so a consumer
      reading `Qstats.csv` or `response_long.csv` cannot tell which `(tavg, prcp)` cell
      is degraded without a join the design does not specify — the exact "silently sparse
      response surface distorts the robustness judgment" failure that §9.4's own
      fail-loud default exists to prevent, reintroduced through the escape hatch the
      owner ratified. Case (b) means the ratified `allow_partial` branch has an unhandled
      exception path. GF-7's expected observation
      ("`sweep_completeness.csv` records 13 `succeeded` + 1 `failed`; `Qstats.csv` has 13
      rows per statistic") is wrong twice over and so cannot detect either sub-case: K is
      12 not 14 (risk-9), and under the fixture's `aggregate_rlz: true` `Qstats.csv` has
      6 rows per statistic regardless of how many members succeeded.
    suggested_fix: >-
      Make `allow_partial` cell-complete rather than member-complete: under
      `aggregate_rlz: true` a `cst_m` whose realization set is incomplete is DROPPED
      entirely (row absent, as §9.4 claims) and named in `indicators/completeness.csv`
      with `state=partial_cell`, and the empty-`csv_fns_i` branch raises a named error
      rather than a pandas `ValueError`. Restate GF-7's expected observation against
      K=12 / `aggregate_rlz: true` and add a sub-case that drops one of two realizations
      of a single `cst_m`.

  - id: risk-3
    severity: major
    section: "§12 C-7 / §9.6 migration parity strategy / §13 steps 0, 7"
    finding: >-
      C-7 — the only falsifier for A4, the design's own most-flagged assumption — is
      specified as `semantic_tree_diff.py --ref <reference> --cur test_case/test_local
      --no-path-map --tolerance 0` against the step-0 whole-tree snapshot. That
      comparison cannot come back clean after step 2 lands, for reasons independent of
      the `_state` registration §10b correctly identifies: step 2 is declared
      value-changing by construction (§9.5, new per-realization seeds), so every
      realization NC, every member CSV and both indicator tables differ from the step-0
      reference on purpose. §10b reasons carefully about one way a whole-tree
      tolerance-0 diff can never be clean and stops one cause short of the decisive one.
      A third cause is risk-11. Nothing in the design specifies the operand that would
      actually test warm-session identity — a *same-forcing* comparison (identical
      baseline NCs and identical WG-2 grid, pooled run vs per-process/`sweep_workers=1`
      run).
    rationale: >-
      Observable consequence: at §13 step 7 the C-7 gate will report a large diff, the
      diff will be attributed to the known generation re-baseline, and A4 will be
      *declared* verified at pool depth on the strength of a gate that was never capable
      of discriminating. §9.6's table calls the simulate leg "Identical, already
      measured … re-verified at pool depth (C-7)" — that re-verification does not exist.
      A4 is the assumption whose failure would corrupt every number the milestone
      produces, so an inoperative falsifier for it is the highest-leverage gate defect in
      the document.
    suggested_fix: >-
      Redefine C-7 as a paired same-input comparison, not a whole-tree diff: after step 4,
      with generation frozen, run the fixture sweep twice from the same baseline NCs —
      once with `sweep_workers=<K>` (one member per session, the cold-process reference)
      and once with `sweep_workers=1` (all K members in one session, maximum pool depth)
      — and require tolerance-0 identity on `hydrology_runs/*/output/cst_*.csv`. Retain
      the whole-tree diff separately as a *scoped* gate over the stages step 2 did not
      change.

  - id: risk-4
    severity: major
    section: "§2.2 A4 / §6.3 Worker lifecycle / §11.3 H2, H4 / §15.1 R-8"
    finding: >-
      Even repaired, the fixture gate has almost no discriminating power for A4 as
      stated. A4 says the pool "extends the warm session from `B` runs to the whole
      sweep". At fixture scale that extension is essentially nil: K=12
      (`realizations_num: 2`, ST_NUM=6 from `stress_test_grid`'s `(step_num+1)` product
      over temp=1/precip=2, `run_historical: false`), and `sweep_workers` defaults to
      `snakemake.threads` = 3 under the documented `-c 3`, so each Julia session serves
      ~4 members — the same depth P3-3 already measured at B=4
      (`dev/p33/batching-results.md:16,139`). Production depth is two orders of magnitude
      larger (RLZ_NUM×ST_NUM in the hundreds over p sessions). Two distinct properties
      are being extrapolated across that gap on fixture evidence: numerical identity
      (A4/C-7) and process stability (H4/C-5/R-8). The design specifies no worker
      recycling policy — a Julia session serves members until the queue empties — so
      accumulated `Wflow.run` state and Julia GC behaviour over ~200 sequential model
      loads are untested and unbounded, and the residual-risk table does not name
      worker-session memory growth at all.
    rationale: >-
      Observable consequence: the milestone can pass every gate in §8.2 and §12 and still
      OOM or diverge on the first production sweep — precisely the run that has no
      reference tree to diff against. The design is candid that at-scale *performance* is
      a model not a measurement (§15.3), but silently treats at-scale *correctness and
      stability* as settled by the fixture.
    suggested_fix: >-
      Run the identity and stability gates at `sweep_workers: 1` so one session carries
      all 12 members (3× the depth P3 measured, at no extra cost), state explicitly that
      fixture depth ≈ batch depth and that A4 at production depth remains open, and add
      an optional `worker_max_members` recycle bound (respawn the Julia worker after N
      members) as the pre-designed mitigation — cheap, zero-dependency, and it converts
      R-8 from a hope into a knob. Add production-depth re-verification of A4 to §15.3's
      known limitations with a named trigger.

  - id: risk-5
    severity: major
    section: "§9.4 allow_partial / §7.2 What Snakemake decides / §8.2 GF-7"
    finding: >-
      Under the ratified `allow_partial: true`, the sweep writes its sole declared output
      `ledger_final.csv` on an accepted-but-incomplete termination (§9.4). §7.2 (probe
      PR-2) establishes that with `ledger_final.csv` present and params/inputs unchanged,
      Snakemake reports `Nothing to be done` and the sweep rule "is not entered at all".
      Composing the two: once a partial sweep finalizes, re-invoking the workflow never
      retries the failed members. The holes are frozen until the user manually deletes
      `ledger_final.csv`, or forces the rule — a recovery step named nowhere in §7,
      §8.1 (F1's recovery text stops at "the sweep finalizes with the hole recorded"), or
      §9.4. GF-7 is a single invocation and cannot observe it.
    rationale: >-
      Observable consequence: a user runs with `allow_partial` to get a first look,
      fixes the cause of the failure, re-runs, and gets `Nothing to be done` plus the
      same incomplete response surface — with `sweep_completeness.csv` still naming the
      hole, so the artifacts disagree with the workflow's own "up to date" verdict. This
      directly contradicts G2 and is the resume semantics most likely to be exercised in
      practice, since `allow_partial` exists precisely for runs that are expected to be
      re-attempted.
    suggested_fix: >-
      Make the declared output's identity carry completeness: under `allow_partial`,
      either write `ledger_final.csv` only when the member set is complete and give the
      partial case a distinct declared output, or (simpler) have the sweep record the
      incomplete member set in a `params:`-visible digest so the next invocation
      re-triggers. Minimum viable: document the recovery command in §8.1 F1 and add
      GF-13 — "partial sweep, fix the fault, re-invoke, require the failed member to
      run".

  - id: risk-6
    severity: major
    section: "§6.6 The experiment lock / §8.2 GF-8 / §12 C-14"
    finding: >-
      The lock's stated purpose (design:953-957) is that "two worktrees pointed at one
      `project_dir` slip past Snakemake's lock entirely and would interleave writes into
      the same experiment tree". But `_state/sweep.lock` is created by `run_sweep.py`, so
      it is held only for stage 3. A concurrent invocation from a second worktree runs
      stages 1, 2 and 4 unguarded: 3.01 rewrites `members.json`, 3.05/3.06 rewrite the
      now-**persistent** `rlz_<n>_cst_0.nc` baselines, and 3.09 rewrites the indicator
      tables. If that second invocation carries any config edit (the realistic case — it
      is why a second worktree exists), it will rewrite the manifest and regenerate the
      baselines *while the first sweep is mid-flight*, truncating and rewriting the exact
      NC files the first sweep's perturb step is reading. Persisting the baselines (an
      approved anchor) is what makes this reachable: under v1 they were `temp()` and
      shorter-lived. GF-8's expected observation ("second fails within seconds") holds
      only in the steady state where everything upstream is already up to date.
    rationale: >-
      Observable consequence: torn NC reads (an R-level crash recorded as
      `stage=perturb`, i.e. misattributed to the member), or worse, a member perturbed
      from a half-written baseline that still opens. The first sweep then writes ledger
      rows and CSVs under a `member_hash` whose manifest no longer exists on disk. C-14's
      claim "two sweeps cannot interleave on one experiment" is true only of the sweep
      stage; the *experiment tree* — which is what the lock claims — is protected for
      part of the run.
    suggested_fix: >-
      Claim the lock in rule 3.01 (`build_members_manifest`) and release it in the reduce,
      or add a second lock at the same `_state/` path taken by the manifest builder and
      released by 3.09 — the `O_EXCL` primitive already chosen works unchanged. Extend
      GF-8 with the case that matters: start `SM` from worktree A, and while the sweep
      runs, invoke `SM` from worktree B with an edited config; require B to fail on the
      lock before writing any artifact, and require A's baselines and manifest to be
      byte-unchanged afterwards.

  - id: risk-7
    severity: major
    section: "§6.2 line protocol / §6.3 Health / §15.1 R-4"
    finding: >-
      §6.2 makes stdout the exclusive protocol channel and disposes of the other stream
      in one clause — "stderr is not part of the protocol; it is teed to the member's
      log" — leaving *drainage* unspecified. §6.3's Health row then deliberately declines
      any per-member wall-clock ceiling ("a hung worker [is] indistinguishable from a
      slow member"), and R-4 accepts the consequence. The composition is a hang class the
      design has no exit from: if the slot reads the worker's stdout with a blocking
      call while stderr is an undrained pipe, the Julia worker blocks on its first full
      stderr buffer (64 KB on Windows) mid-`Wflow.run` and never answers. Wflow is
      verbose over a ~35 s run, and today's driver already writes per-member status lines
      (`blueearth_cst/experiment/run_wflow_batch.jl:19,22`) which the redesign must move
      from stdout to stderr, adding to the volume. There is no heartbeat, no timeout, no
      gate, and F12's "all workers retire" recovery never fires because the worker has
      not exited.
    rationale: >-
      Observable consequence: the sweep hangs indefinitely with no diagnostic; the only
      recovery is a manual kill, which lands in F5 (in-flight members quarantined and
      re-run). At production scale on a hands-off run this is an overnight loss. This is
      a specification gap rather than a predicted implementation bug — but it is exactly
      the kind of gap a normative design exists to close, and the design's own choice to
      forgo a wall-clock ceiling removes the generic backstop that would otherwise
      contain it.
    suggested_fix: >-
      Add a normative line to §6.2: the worker's stderr is redirected to the member log
      file at spawn time (`stderr=<file handle>`), or drained by a dedicated reader
      thread — never left as an undrained `PIPE`. Add GF-12/GF-14: a stub worker that
      emits >1 MB to stderr before answering must not stall the sweep. Reconsider R-4
      with a *generous* ceiling (e.g. 20× the observed median `seconds.simulate`, derived
      from the ledger rather than configured) — the design's objection is to a
      wrongly-sized constant, which a data-derived bound is not.

  - id: risk-8
    severity: major
    section: "§5.2 sweep_completeness.csv / §5.3 Atomicity / §9.4"
    finding: >-
      Two facts compose badly. (1) The order of the two terminal writes —
      `sweep_completeness.csv` (undeclared) and `ledger_final.csv` (declared, the gate
      that unblocks the reduce) — is never stated normatively; §5.2 describes both
      independently. (2) `sweep_completeness.csv`'s columns are
      `member_id, state, attempts, stage, class, detail` — no `invocation_id`, no
      `member_hash`, no manifest digest, no timestamp. So it carries nothing that binds
      it to the sweep generation it describes. The identity-field gap is self-sufficient:
      no consumer — the reduce, `sweep_status.py`, or a human — can determine whether a
      given `sweep_completeness.csv` describes the sweep that produced the
      `ledger_final.csv` sitting beside it, and the design specifies no ordering that
      would make the pairing implicit.
      *Unverified sub-case, flagged as needing a probe rather than asserted:* if
      `ledger_final.csv` were written first and the process tree SIGKILLed before
      completeness landed, the next invocation might see the declared output present with
      unchanged params and report `Nothing to be done`, leaving the reduce reading a
      stale record. PR-6 (design:1537-1539) explicitly declined to measure post-kill
      blocking behaviour, and it observed `.snakemake/incomplete/<b64>` being recorded —
      the machinery that may instead demand `--rerun-incomplete`. Which of the two
      happens when the output *does* exist is not established by any probe in §11.2.
    rationale: >-
      Observable consequence: under `allow_partial`, `indicators/completeness.csv` — the
      artifact whose whole job is telling a scientist which cells are trustworthy —
      carries no field that ties it to the response surface published beside it, so a
      mismatch (however it arises) is undetectable by construction. This is the "stale
      manifest/ledger pair passes verification" case, and it exists because the
      completeness record is the one `_state/` artifact with no identity fields, in a
      design that otherwise stamps `invocation_id` and `member_hash` on every ledger row.
    suggested_fix: >-
      State the finalization order normatively: fsync all ledger rows → write
      `sweep_completeness.csv` atomically → write `ledger_final.csv` atomically, last
      statement before exit. Add `invocation_id` and the manifest's `config_digest` to
      `sweep_completeness.csv` (and to `indicators/completeness.csv`), and have the
      reduce hard-fail when the completeness record's `invocation_id` differs from the
      one carried by every row of its declared `ledger_final.csv`.

  - id: risk-9
    severity: major
    section: "§4.5 Job-count consequence / §8.2 GF-6, GF-7, GF-9 / §12 C-12"
    finding: >-
      The design's fixture arithmetic does not match the fixture it names. §4.5 states
      "fixture scale (`RLZ_NUM=2`, `ST_NUM=6`, `run_historical: true` ⇒ `K=14` members)",
      but `config/workflows/snake_config_model_test.yml:58,61,80` has
      `realizations_num: 2`, **`run_historical: false`** and `aggregate_rlz: true`, so
      `ST_START = 1` (`Snakefile_climate_experiment:55-56`) and **K = 12** — which is
      also the K `dev/p33/batching-results.md:100,182` measured against, and the K
      consistent with the 49/58 job counts §4.5 quotes from P3-3. The error propagates
      into three gate definitions (GF-6 "the 13 sibling CSVs"; GF-7 "13 `succeeded` + 1
      `failed`" and "13 rows per statistic"; and by extension GF-9's expectations) and
      into the v2 job count (`2+2` generate becomes correct only by coincidence).
    rationale: >-
      Observable consequence: GF-6 and GF-7's stated pass observations are unmeetable as
      written, so at execution time an implementer will either "correct" them ad hoc —
      exactly the drift the falsifier-before-code discipline exists to prevent — or read
      the mismatch as a real failure. It also means the design has not been checked
      against the fixture whose defaults drive three of its most consequential gates
      (`run_historical: false` also means the fixture has no `cst_0` members at all,
      which silently voids the §6.4 scheduling rule "`cst_0` baselines come first — the
      members most likely to expose a systematic failure early").
    suggested_fix: >-
      Recompute K, all gate observations and the job-count delta against the fixture as
      configured (K=12, no `cst_0` members, `aggregate_rlz: true`), or state explicitly
      that the gates run against a fixture variant with `run_historical: true` and pin
      that variant.

  - id: risk-10
    severity: major
    section: "§13 step 8 Performance floor check / §12 C-12 / §14.1"
    finding: >-
      Two independent problems with the floor. (a) **Measurement validity.** C-12's
      falsifier is "measured wall > 400.2 s" with command `Measure-Command { SM
      --forceall }`, but P3-3's 400.2 s is a K=12 full-sweep wall under the v1 stage
      shape (`dev/p33/batching-results.md:16,114`), whereas `--forceall` in v2 also
      re-runs a restructured generation stage (`RLZ_NUM` parallel jobs instead of one)
      and a restructured prepare stage. §13 step 8 correctly asks for the 3.08-stage
      makespan to be reported separately, then C-12 states the falsifier against the full
      wall — so the two disagree about what is being compared, and the honest operand
      (P3-3's 228.1 s 3.10-stage makespan, ibid:113) is never named as the floor. (b)
      **Gate placement.** §14.1 says batching "would become preferable if the pool's
      measured makespan lost to batching at fixture scale (C-12) — the floor check is
      precisely the decision point that would reinstate it". But §13 step 5 deletes the
      `run_wflow_batch_<b>` family (`Snakefile_climate_experiment:484-546`) and rejects
      the `batch_size*` keys, and the floor check is step 8. The stated go/no-go sits
      three steps past the point of no return.
    rationale: >-
      Observable consequence for (a): a pool that wins on the stage it changed can still
      "fail" C-12 on a wall it did not, or vice versa — the floor gate cannot honestly
      answer the question it exists to answer. Consequence for (b): if the floor is
      genuinely not met, "stop" at step 8 means reverting five landed steps including
      contract, validator and doc rewrites, so the realistic outcome is that the floor
      gets accepted rather than enforced. This is the design's own G7 and its own named
      reinstatement path, both undermined by sequencing.
    suggested_fix: >-
      Split C-12 into two stated comparands — sweep-stage makespan vs P3-3's 228.1 s (the
      binding one) and full-workflow wall vs 400.2 s (reported, not gated) — and move the
      floor measurement to the end of step 4, where the pool exists and the batch rules
      still do, so the comparison is same-tree and the revert is one step. Keep step 8 as
      the confirmation run.

  - id: risk-11
    severity: major
    section: "§4.2 change 3 (generator out_dir) / §10 contract-delta table"
    finding: >-
      §4.2 change 3 moves `weathergenr::generate_weather`'s `out_dir` to the
      per-realization `_work/rlz_<n>/`, relocating `sim_dates.csv` and
      `resampled_dates.csv`, and justifies it as "a documented relocation of a
      non-contract artifact". The exclusion note it cites
      (`dev/contracts/weather-generator-seam.md:255-258`) does say they are
      non-interchange — but it names them **at their current path**, and R07 explicitly
      *ruled* on that path: `dev/r07/migration_project-layout.md:194-195`, "exact —
      **`output/`, not `_work/`** (ruled: products of the generator)". §10's
      contract-delta table — whose stated purpose (G6) is that every delta is enumerated —
      has no row for either file. A third, smaller item rides along:
      `dev/scripts/semantic_tree_diff.py:357-360` carries an exact-file path-map rule
      rewriting them to `weather_generator/output/…`, asserted by
      `tests/test_semantic_tree_diff.py:621-622`; that mapping goes stale on the move and
      needs updating in step 6. It is *not* what drives the consequence below — C-7's
      command passes `--no-path-map` (design:1565), so the map is not applied there.
    rationale: >-
      Observable consequence, resting on the relocation alone and independent of the path
      map: the step-7 whole-tree tolerance-0 diff reports both files as `missing` under
      `weather_generator/output/` and `extra` under `_work/` — a third independent reason
      C-7 cannot come back clean (risk-3), and one §10b did not anticipate because it
      reasoned only about `_state/`. Separately and independently, the move reverses a
      recorded R07 ruling with no §10 row, which is the enumeration guarantee G6 claims.
      Secondarily, `resampled_dates.csv` is the record
      of which historical days each realization resampled; relocating it under a `_work/`
      prefix that reads as scratch, while reversing a recorded ruling, is a provenance
      regression the milestone would carry silently.
    suggested_fix: >-
      Keep the CSVs in `weather_generator/output/` with a per-realization suffix
      (`sim_dates_rlz_<n>.csv`), which removes the concurrent-write race §4.2 change 3 is
      actually solving without moving the artifact or contradicting R07. If the move
      stands, add a §10 row, update the seam doc's exclusion note, and update the path map
      and its test in the same commit as part of step 6.

  - id: risk-12
    severity: major
    section: "§4.4 export_wflow_results / §5.2 ledger_final.csv"
    finding: >-
      `ledger_final.csv` carries `result_sha256` per member and is the reduce's declared
      input, yet nothing in §4.4 or §9.4 says the reduce verifies it before reading the
      CSVs. The per-member CSVs are deliberately undeclared (§3.2), so Snakemake no
      longer tracks their mtimes either — the protection v1 had via rule 3.10's declared
      `csvs` output (`Snakefile_climate_experiment:533-535`) is removed and nothing
      replaces it at the consumption point. §5.3's digest-on-resume check runs at *sweep*
      entry, and §7.2 shows the sweep is not entered at all when `ledger_final.csv` is
      present and fresh.
    rationale: >-
      Observable consequence: a member CSV corrupted, truncated or hand-edited after a
      successful sweep is consumed silently by the reduce and published into
      `Qstats.csv` / `response_long.csv` / the baseline manifest. The design pays the
      full cost of computing and storing the digest and then does not spend it at the one
      place the corruption becomes user-visible. F8's recovery ("quarantine + re-run") is
      only reachable if the sweep runs, which in this scenario it does not — and F8 has
      no gate in §8.2 either (see risk-16).
    suggested_fix: >-
      One line in §4.4: the reduce recomputes each `result_sha256` from
      `ledger_final.csv` before reading, and hard-fails naming the diverged member (this
      is cheap — the CSVs are already being read). Add it to C-10's observation set and
      give F8 a gate (mutate one member CSV after a successful sweep, re-invoke, require
      a named failure rather than a silent republish).

  - id: risk-13
    severity: minor
    section: "§12 C-13 / §9.2 / §15.1 R-5"
    finding: >-
      C-13's claim is "`tools` drift is detectable after the fact"; its falsifier is "a
      completed sweep whose `run.tools` differs from the live environment **goes
      unreported**"; its command is "manifest vs `julia --version` / `packageVersion` at
      reduce time". But no rule, script or spec in the design performs that comparison —
      §5.1 states `tools` is "recorded, **not** enforced" and §9.2 relies on the mixture
      being "detectable after the fact". The falsifier's wording presumes an automatic
      report that the design does not specify anywhere.
    rationale: >-
      As written the falsifier cannot fail: a human can always compare two strings by
      hand, so "goes unreported" is never observed, and C-13 will be recorded as passing
      while R-5 (a sweep silently mixing engine versions across resumes) remains
      completely unmitigated. This is the clearest case in §12 of a falsifier that passes
      while its claim is materially false — and it matters because R-5's whole
      justification for skipping `environment_digest` rests on C-13 being a real trigger.
    suggested_fix: >-
      Make it mechanical and cheap: the sweep runner re-reads the four `tools` versions at
      start and appends a `tools_drift` warning row to `sweep_completeness.csv` (and the
      log) when any differs from `members.json`; C-13's falsifier becomes "inject a
      version mismatch, observe no warning row". Otherwise restate C-13 honestly as
      "`tools` is recorded so a mismatch is reconstructible by inspection" and drop the
      implication of automatic detection.

  - id: risk-14
    severity: minor
    section: "§12 C-16 / §9.6 Generate parity class"
    finding: >-
      C-16 claims the generation change is "distributionally equivalent, not merely
      different", falsified by "any per-variable annual mean/sd envelope falls outside
      the pre-change envelope". The fixture has `realizations_num: 2`
      (`config/workflows/snake_config_model_test.yml:58`), so both the before and after
      "envelopes" are constructed from n=2 draws of a stochastic generator.
    rationale: >-
      An envelope over two realizations has no statistical power: it will either pass
      trivially (a 2-point range is wide) or fail spuriously, and either outcome will be
      reported as a verdict on a value-changing re-baseline that then gets frozen into
      the baseline manifest at step 9. The design is otherwise rigorous about not
      claiming measured what is modelled; this falsifier claims a distributional verdict
      that its sample size cannot support.
    suggested_fix: >-
      Either run the characterization at an elevated `realizations_num` (20+, generation
      only, no sweep — cheap, since stage 2 is now independently parallel) or restate C-16
      as what n=2 can support: a sanity envelope, with the distributional claim explicitly
      deferred. Name the acceptance threshold rather than leaving "envelope" to the
      validator's judgment.

  - id: risk-15
    severity: minor
    section: "§13 step 1 falsifier vs §5.1 manifest schema"
    finding: >-
      Step 1's falsifier is "a test asserting `members.json` is byte-identical across two
      invocations with unchanged config". §5.1's schema puts `run.created_at`
      (`"2026-08-01T13:22:05Z"`) inside the manifest, and §5.1 also declares that the
      manifest's serialization *is* the canonicalization for `config_digest`. Two
      invocations cannot produce a byte-identical file containing a wall-clock stamp.
    rationale: >-
      The step-1 falsifier is unpassable as written, so it will be silently weakened at
      implementation time — and it is the only gate protecting manifest determinism, the
      property everything downstream of §5.1 assumes. Related: because `created_at`
      changes on every 3.01 execution, the manifest's mtime *and content* change on every
      re-run, which is what makes §7.3 step 6's no-op path load-bearing — the design says
      as much, but the two statements are not reconciled anywhere.
    suggested_fix: >-
      State the falsifier against the manifest minus `run.created_at` (or move
      `created_at` out of the digested body into a sidecar), and say explicitly which
      fields are excluded from the determinism assertion.

  - id: risk-16
    severity: minor
    section: "§8.2 failure-injection gate set / §8.1 F4, F8, F12 / §14 alternatives"
    finding: >-
      Three of the twelve failure modes §8.1 enumerates have no gate among the eleven:
      F4 (a **slot** process dies — GF-1 kills the Julia worker, which is the easier
      case, since the slot is the process that observes it), F8 (member CSV diverges from
      its recorded digest — the entry point to the whole quarantine machinery, and see
      risk-12), and F12 (all workers retire, e.g. Julia absent from `PATH` — the A5
      failure, which under `AGENTS.md`'s "Julia is not in the pixi env" is the single
      most likely environment failure this repo has). The most consequential *realistic*
      failure missing from the set is none of those, though: it is the
      generation-invalidation path of risk-1, which no gate exercises. Separately, §14's
      alternatives record omits Snakemake `service:` rules — the one construct that could
      have kept per-member DAG jobs while sharing a persistent worker — so a future reader
      cannot tell whether it was considered and rejected or simply not seen.
    rationale: >-
      Gate-set completeness is the design's own success criterion for §8; a failure mode
      enumerated in §8.1 with no row in §8.2 reads as covered when it is not. F12 in
      particular is cheap to gate (temporarily shadow `julia` on `PATH`) and its expected
      observation — hard failure with no partial `ledger_final.csv` — is the same
      discriminating observation GF-6 relies on.
    suggested_fix: >-
      Add gates for F4, F8, F12 and the risk-1 seed path; add a one-line §14 entry
      disposing of Snakemake `service:` rules (a `service:` job's lifetime is bound to its
      consuming jobs, so it cannot amortize across the whole sweep — state that, or
      whatever the real reason is).

  - id: risk-17
    severity: minor
    section: "§5.2 ledger schema / §5.4 the fold rule"
    finding: >-
      `ts` is specified as RFC 3339 UTC at **second** resolution, and §5.4's fold rule is
      "for each `member_id`, consider only rows whose `member_hash` equals the current
      manifest's; **take the last row**". Which ordering "last" refers to — file order or
      `ts` order — is never stated. Several member sub-steps are millisecond-scale
      (§6.6 steps 1, 5, 6), so a `claimed` and its terminal row can share a `ts`.
    rationale: >-
      If an implementer reads "last" as sort-by-`ts` (a natural reading for a record
      carrying timestamps), a same-second `claimed`/`succeeded` pair can fold to
      `claimed` ⇒ "interrupted" ⇒ the member's verified output is quarantined and
      re-run. Wasted work rather than wrong science, but it is a nondeterministic resume
      verdict in the component R-1 already flags as the milestone's highest risk, and it
      is free to close in the spec.
    suggested_fix: >-
      One normative sentence in §5.2: file order is authoritative for the fold; `ts` is
      descriptive only and must never be used for ordering. Cover it in step 4's fold unit
      tests with a same-`ts` pair.

  - id: risk-18
    severity: minor
    section: "§9.1 OQ-1 (under the G1 deferral) / §4.4 response_long.csv / §10 WG-2"
    finding: >-
      Reviewed under the ratified deferral (no call-site change; axis inert; field
      retained), three consistency items remain. (1) §9.1 bundles "**pass `verbose = TRUE`
      regardless of the branch**" into the deferred recommendation — but `verbose = TRUE`
      is the one change that is *not* value-changing: PR-1 established that weathergenr
      warns "Ignoring `precip_var_factor`" only when `verbose` is true, and our call site
      omits it (`blueearth_cst/weathergen/impose_climate_change.R:45-57`). Deferring it
      with the rest means the inert axis stays *silently* inert for another milestone.
      (2) `response_long.csv` — the new consumer-facing artifact, joining the baseline
      manifest per the G1 ruling — publishes `precip_variance` as a coordinate column
      beside `tavg` and `prcp`, with no field or doc marking it inert; a downstream
      analyst reading the response surface has no signal that varying it changed nothing.
      (3) `precip_variance` sits inside `member_hash` (§5.1), where it is both redundant
      (it is a column of `cst_<m>.csv`, already covered by `st_csv_digest`) and, while
      inert, a false-invalidation lever: editing `stress_test.precip.variance.{min,max}`
      forces a full re-sweep that provably cannot change a single output value.
    rationale: >-
      The stated reason for deferring rather than retiring is to keep the axis available
      for later activation, which is sound — but shipping it undocumented at the point of
      consumption converts "deferred" into "silently ignored", the failure §9.1 itself
      names as the worse one. The forward cost also compounds: `response_long.csv` enters
      the baseline manifest at step 9 carrying the inert column, so activating the axis
      later re-baselines an artifact that was pinned with a coordinate that meant nothing.
      Note the fixture cannot help — `snake_config_model_test.yml:75-77` has
      `variance.min == variance.max == 1.0`, so no gate in §8.2 or §12 touches the axis at
      all.
    suggested_fix: >-
      Carve `verbose = TRUE` out of the deferral (a warning-only, tolerance-0-safe change
      that makes the inertness observable at run time, and would satisfy the "stress-test
      tool that silently ignores a declared axis" objection at zero re-baseline cost), and
      annotate the inertness where it is consumed: a `response_long.csv` column note in
      §4.4, a line in the WG-2 seam doc, and a rejected-not-ignored validation message if
      a config sets `variance.min != variance.max`. Consider dropping `precip_variance`
      from `member_hash` while it is inert, or state explicitly that its presence is
      forward-compatibility and accept the false invalidation.

  - id: risk-19
    severity: minor
    section: "§6.6 the p × 1 disk claim / §1.2 G3 / §12 C-3"
    finding: >-
      G3 claims peak transient disk is `p × 1` member "**by construction** rather than by
      a tuned constant", and §6.6 derives it from the member's step-3/step-5 deletions.
      That derivation holds only within a completed member. A crash between step 2
      (perturb writes the WG-4 NC) and step 3's deletion, or between step 4 and step 5's
      deletions, leaves the WG-4 NC / WG-6 forcing / HM-6b state on disk with no ledger
      record and no owner: §7.3's resume fold quarantines *recorded outputs* and reports
      *orphan member results*, but nothing sweeps orphaned transients, and
      `prune_experiment_orphans.py` is scoped to member CSVs/TOMLs (§7.4). C-3's
      falsifier samples peak disk during clean runs, so it cannot observe accumulation
      across crash-resume cycles.
    rationale: >-
      Observable consequence: after N interrupted sweeps the experiment tree carries up
      to N×p stale transients — on a large basin these are the biggest files in the tree,
      and they are exactly the class whose unbounded growth `dev/followups.md` § Post-P3-3
      flagged as the binding constraint. Minor because it is recoverable and visible, but
      it means G3's "by construction" is a per-run property being stated as a tree
      invariant, and the gate that would catch it is scoped so it cannot.
    suggested_fix: >-
      Have the resume fold delete (or quarantine) the transient set for every member it
      classifies RUN, before re-claiming — the paths are derivable from `member_id`, so it
      is a few lines. Extend `prune_experiment_orphans.py` to the transient classes, and
      restate G3 as a per-invocation peak with the cross-invocation cleanup named.
```
