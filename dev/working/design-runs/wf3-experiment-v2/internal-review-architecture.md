# Internal review — architecture & internal-consistency lens

Target: `dev/working/design-runs/wf3-experiment-v2/design-v1.md` (design-v1.md, 1903 lines, read in full).
Method: every factual premise verified against the repository at `docs/wf3-redesign` (file:line cited inline).
Framing settled at G1 (4 stages, ledger-driven sweep, Julia pool, per-realization generation, three-layer drift
guard, OQ-1 deferred, OQ-4 fail-loud + `allow_partial`, named `cst-run-control` subset, index-based member ids,
zero new dependencies) is taken as given and is **not** re-litigated; the review asks only whether the document
implements it consistently.

## Summary

The document is unusually strong on the things a workflow spec usually gets wrong: the declared-output rule
(§3.2, probe PR-4) is correct and load-bearing, the `cst-run-control` subset table (§5.5) states every skip, the
`--notemp` replacement (§10a) and the `_state/` exclusion from `semantic_tree_diff` (§10b) are exactly the two
"silently breaks a gate" traps this migration contains, and both were found. `dev/scripts/semantic_tree_diff.py:145`
and `dev/scripts/check_baseline.py:187-189` confirm §10b's premises verbatim.

Four defects are structural rather than editorial: the fixture arithmetic the whole gate set is written against is
wrong; the members manifest is specified to read an artifact produced by a rule that takes the manifest as its
input; `member_hash` cannot see the one change (`master_seed`) that §7.6 claims invalidates every member; and the
log-merge mechanism the per-member visibility goal (G4) depends on does not behave as §6.5 asserts. Each of these
has an observable consequence on the fixture, not just on paper.

A fifth blocking finding (arch-15) is about the ratified OQ-4 posture's *implementation*, not the ruling: under
the fixture's `aggregate_rlz: true`, a missing member does not produce the "grid with holes" §9.4 describes — it
produces an under-averaged cell, or a crash.

Checked and clean, stated so the panel can tell it was checked rather than skipped: the §13 step ordering (step 0's
pre-change captures precede every value change, each step's falsifier precedes its code, the single manifest
re-record is last, and the prune-before-snapshot rule is carried across from `AGENTS.md`'s `prune_series_cache.py`
clause); and the platform posture (no upstream hydromt/wflow/weathergenr patching — §9.1 explicitly declines both
the seed-passing change and the 3.07 Python port; no CST-API or frontend coupling anywhere; `scripts/run_workflows.py`
and the `workflows:` config section untouched per G8).

Verdict: **revise**. No finding challenges the architecture; they challenge specific claims the architecture rests on.

---

## Detail on the four blocking findings

**arch-1 — the fixture is `K=12`, not `K=14`.** Every tracked config sets `run_historical: false`
(`config/workflows/snake_config_model_test.yml:61`, `snake_config_model_test_linux.yml:55`,
`snake_config_dev_fast.yml:69`, `snake_config.template.yml:127`, `tests/snake_config_model_test.yml:62`), so
`ST_START = 1` (`Snakefile_climate_experiment:55-56`) and the fixture has no `cst_0` members at all. With
`realizations_num: 2` and `stress_test.temp.step_num: 1` / `precip.step_num: 2`, `stress_test_grid` gives
`ST_NUM = 2 × 3 = 6` (`blueearth_cst/shared/snake_utils.py:620-622`), hence `K = 2 × 6 = 12`. P3-3 says so
independently: "`K=12`, `p=3`" (`dev/p33/batching-results.md:100,182`) and the Snakefile's own note records "12
single-member batch rules" at `batch_size=1` (`Snakefile_climate_experiment:482`). The fixture also sets
`aggregate_rlz: true` (`:80`), and under aggregation `Qstats.csv` carries exactly `st_num = 6` rows per statistic
(`export_wflow_results.py:104,153`). So GF-6's "the 13 sibling CSVs", GF-7's "13 `succeeded` + 1 `failed`" and
"`Qstats.csv` has 13 rows per statistic", §7.5's banner example, C-3's "run at `K=14`", §13 step 0.4's "the 14
per-member CSVs" and §4.5's job-count comparison are all uncomputable on the named fixture. The two gates that
make the ratified OQ-4 ruling testable are the two that cannot be executed as written.

**arch-2 — the manifest reads what a downstream rule produces.** `member_hash` includes `st_csv_digest`, "the
content digest of the member's WG-2 file", and `tavg`/`prcp`/`precip_variance` are specified as "derived exactly
as the reduction derives them today" from `cst_<m>.csv` (§5.1). Those files are produced by
`climate_stress_parameters`, and §4.1 gives that rule `input.manifest = _state/members.json`. On a fresh
experiment the manifest rule runs first and the WG-2 files do not exist, so no `member_hash` is computable. The
values themselves are derivable from config (`prepare_cst_parameters.py` computes the grid from
`stress_test.*`), but the *digest* is not, and the digest is what §7.6's "one `cst_<m>.csv` edited → only that
column of members invalidates" row depends on.

**arch-3 — the seed is invisible to `member_hash`.** §5.1 fixes `member_hash` over
`{member_id, rlz, cst, baseline, st_csv_digest, tavg, prcp, precip_variance, run_config_digest}` with
`run_config_digest` covering `horizontime_climate`, `run_length`, `clim_source`, `data_sources`, the base
`wflow_sbm.toml` digest and the staticmaps digest. Neither the per-realization `seed`, nor `master_seed`, nor the
baseline NC's content digest appears. Change `master_seed`: stage 2 regenerates every `rlz_<n>_cst_0.nc` (its
config changed), the manifest is rewritten, Snakemake re-enters the sweep — and the runner's fold (§7.3 step 5)
finds `last = succeeded, artifacts present, digests OK` for every member and classifies all of them SKIP. The
reduce then builds the response surface from member CSVs produced under the *previous* realization set. §7.6's
row "`master_seed` → every realization's seed changes ⇒ regeneration ⇒ every member invalidates" is therefore
false, and the failure is silent — precisely risk R-1, unmitigated by the design that names it. Note this is the
same property that makes the adjacent row ("`realizations_num` increased ⇒ only the new members run") true, so
the fix is not free: `seed` is computable at manifest time and belongs in `member_hash`; the baseline NC digest
is not, and would need a sweep-start verification like drift layer 3.

**arch-4 — `merge_logs` will not merge the per-member parts.** §6.5 asserts "per-member parts merge with **no
change to `merge_logs`**, only a new label in `LOG_RULES`", and §4.3 gives rule `run_sweep` both a flat part
`_parts/3.08_run_sweep.log` (the rule's `log:`) and a member directory `_parts/3.08_run_sweep/rlz_<n>_cst_<m>.log`.
`merge_logs._members` short-circuits: `if os.path.isfile(<parts_dir>/<label>.log): return [(None, flat)]` and
only reaches the directory walk when that file is absent (`blueearth_cst/shared/merge_logs.py:106-111`). No rule
today has both shapes under one label, which is why the mechanism has never been exercised this way. Consequence:
the merged `wf3_climate_experiment.log` contains the orchestrator log only, every per-member log is silently
dropped, and because `_remove_parts` deletes only what it merged (`:139-141`), the member parts accumulate as
orphans and `logs/_parts/` never disappears. `merge_benchmarks` is fine — its recursive glob filtered on the
leading path segment picks up both shapes (`merge_benchmarks.py:55-59`) — so the design's generalization from one
gather to the other does not hold.

---

```yaml
verdict: revise
doc_version: design-v1.md
findings:
  - id: arch-1
    severity: blocking
    section: "§8.2 The failure-injection gate set / §4.5 Rule-inventory delta / §12"
    finding: >
      The design fixes fixture scale as "RLZ_NUM=2, ST_NUM=6, run_historical: true ⇒ K=14 members" (§4.5) and
      builds the gate set on it, but every tracked config sets run_historical: false
      (config/workflows/snake_config_model_test.yml:61; also _linux.yml:55, snake_config_dev_fast.yml:69,
      snake_config.template.yml:127, tests/snake_config_model_test.yml:62), so ST_START=1
      (Snakefile_climate_experiment:55-56) and K = 2 x 6 = 12 — the value P3-3 itself uses
      (dev/p33/batching-results.md:100,182) and the Snakefile records (Snakefile_climate_experiment:482,
      "12 single-member batch rules"). The fixture also sets aggregate_rlz: true
      (snake_config_model_test.yml:80), under which Qstats.csv has exactly st_num = 6 rows per statistic
      (export_wflow_results.py:104,153), not one row per member. Because the fixture has no cst_0 member, the
      §4.4 cst_0 asymmetry cannot be exercised on it either.
    rationale: >
      GF-6 ("the 13 sibling CSVs present and untouched"), GF-7 ("13 succeeded + 1 failed"; "Qstats.csv has 13
      rows per statistic"), §7.5's plan-banner example, C-3 ("run at K=14"), §13 step 0.4 ("the 14 per-member
      CSVs") and §4.5's 49-vs-13 job comparison all state expected observations that cannot occur on the named
      fixture. GF-6/GF-7 are the pair that makes the ratified OQ-4 posture testable, so as written the
      milestone's central behavioural gate cannot pass or fail meaningfully — an implementer would either
      silently change run_historical (changing the baseline slice) or record a false green.
    suggested_fix: >
      Recompute every fixture-scale number at K=12 with ST_START=1 and aggregate_rlz=true (11 siblings in GF-6;
      GF-7 as 11 succeeded + 1 failed with 5 of 6 grid rows populated), or state explicitly that the milestone
      flips the fixture to run_historical: true and price that as a baseline-manifest change in §13 step 9.
  - id: arch-2
    severity: blocking
    section: "§5.1 Manifest schema / §4.1 Stage 1 — Prepare"
    finding: >
      member_hash is defined over st_csv_digest, "the content digest of the member's WG-2 file", and the
      manifest's tavg/prcp/precip_variance are specified as month-1 values read from cst_<m>.csv exactly as
      export_wflow_results.py:196-198 reads them. But §4.1 makes climate_stress_parameters — the WG-2 producer
      (Snakefile_climate_experiment:318-330) — take input.manifest = _state/members.json, so rule 3.01 runs
      before the files it must digest exist.
    rationale: >
      On a fresh experiment the manifest rule cannot compute any member_hash, so the sweep has no freshness
      key and §7.6's "one cst_<m>.csv edited ⇒ only that column of members invalidates" cannot hold. On a
      re-run it would digest the *previous* run's WG-2 files, which is worse than failing: a stress-grid edit
      would be hashed one generation late. The scalars are derivable from config
      (prepare_cst_parameters.py derives the grid from stress_test.*), but the digest is not.
    suggested_fix: >
      Either move climate_stress_parameters ahead of the manifest rule and declare its st_csv_fns as an input
      of 3.01 (the guard sentinel chain then runs manifest-last), or drop st_csv_digest in favour of a digest
      over the stress_test config section, which the manifest rule already holds.
  - id: arch-3
    severity: blocking
    section: "§5.1 member_hash / §7.6 What forces full invalidation"
    finding: >
      member_hash covers {member_id, rlz, cst, baseline, st_csv_digest, tavg, prcp, precip_variance,
      run_config_digest}; run_config_digest covers horizontime_climate, run_length, clim_source, data_sources,
      the base wflow_sbm.toml digest and the staticmaps digest. The per-realization seed, master_seed, and the
      baseline NC's content digest are all absent, so §7.6's row "master_seed → every realization's seed
      changes ⇒ regeneration ⇒ every member invalidates" is not implementable by the stated hash.
    rationale: >
      Changing master_seed regenerates every rlz_<n>_cst_0.nc (stage 2's config changed) while leaving every
      member_hash byte-identical. The resume fold (§7.3 step 5) then reads "last = succeeded, artifacts
      present, digests OK" for all K members and skips the entire sweep, and the reduce publishes a response
      surface computed from member CSVs belonging to the previous realization set. This is a silent
      scientific error on a supported config edit — the exact realization of risk R-1, which the design rates
      High and mitigates only with unit tests of the fold, not with a trigger.
    suggested_fix: >
      Put the realization seed (available at manifest time) into member_hash, and add the baseline NC content
      digest to the sweep-start verification alongside the three drift digests (§7.1 layer 3), where it can be
      read after stage 2 has run.
  - id: arch-4
    severity: blocking
    section: "§6.5 Logging and benchmark capture"
    finding: >
      §6.5 claims per-member log parts "merge with no change to merge_logs, only a new label in LOG_RULES",
      while §4.3 gives run_sweep both a flat part (_parts/3.08_run_sweep.log, the rule's log:) and a member
      directory (_parts/3.08_run_sweep/rlz_<n>_cst_<m>.log). merge_logs._members returns the flat file and
      never inspects the directory when both exist (blueearth_cst/shared/merge_logs.py:106-111).
    rationale: >
      Every per-member log would be excluded from wf3_climate_experiment.log and, because _remove_parts
      deletes only merged paths (merge_logs.py:139-141), left behind as permanent orphans under logs/_parts/ —
      defeating goal G4 (per-member visibility) and the "one file left after a clean run" property the log
      layout was designed around (Snakefile_climate_experiment:182-196). The design generalizes from
      merge_benchmarks, which genuinely does handle both shapes via a recursive glob filtered on the leading
      path segment (merge_benchmarks.py:55-59); merge_logs does not.
    suggested_fix: >
      Choose one shape for the label: write the orchestrator log as
      _parts/3.08_run_sweep/_orchestrator.log inside the member directory (no merge_logs change, natural-sort
      places it first), or teach _members to union the flat file with the directory walk and say so in §6.5
      instead of claiming no change.
  - id: arch-5
    severity: major
    section: "§6.6 Forcing lifecycle / §10a The --notemp replacement"
    finding: >
      §6.6's member table deletes the WG-4 perturbed NC at step 3 (downscale) and the WG-6 forcing, HM-6b
      state and member spec at step 5 (verify); the sentence that follows says only "retain_member_artifacts:
      true suppresses step 5's deletions". §10a then claims the paths appearing under that flag are "exactly
      the ones the existing skip-guards already test for", which includes validate_wg4's perturbed NC at
      <exp>/weather_generator/output/rlz_<n>_cst_<m>.nc (dev/contracts/weather-generator-seam.md:312,383).
    rationale: >
      As written the flag does not retain the WG-4 perturbed NC, so validate_wg4's on-disk integration case
      stays permanently skipped after --notemp stops working — the "gate that would otherwise silently break"
      that §10a exists to prevent breaks anyway, and §13 step 7's "capture to un-skip the three temp
      validators" un-skips two.
    suggested_fix: >
      State that retain_member_artifacts suppresses the deletions in steps 3 and 5.
  - id: arch-6
    severity: major
    section: "§10a capture command / §8.2 GF-7 / §5.3 recovery command"
    finding: >
      Three operator commands pass run-time overrides as top-level --config keys —
      `--config retain_member_artifacts=true` (§10a), `--config allow_partial=true` (GF-7), and
      `snakemake … --config sweep_quarantine=1` (§5.3) — but all three keys are specified in §4.5 under
      workflows.climate_experiment and read through get_config(my_cfg, …), where
      my_cfg = config["workflows"]["climate_experiment"] (Snakefile_climate_experiment:30).
      Snakemake's --config writes config["<key>"] at the top level, which that read never sees.
    rationale: >
      The documented capture procedure, the allow_partial gate and the corrupt-ledger recovery command are all
      inoperative as written: they would run with the defaults and report a false green (GF-7 would exercise
      fail-loud, not allow_partial). This also matters for the R01 sectioned-schema convention, which the
      Snakefiles enforce uniformly.
    suggested_fix: >
      Either edit the fixture config for these runs, or specify in §4.5 that the three keys accept a top-level
      --config override with a stated precedence rule, and update all three commands accordingly.
  - id: arch-7
    severity: major
    section: "§2.4 Inputs and provenance / §5.1 Manifest schema"
    finding: >
      §2.4 lists config/templates/weathergen_config.yml as a result-affecting input and closes with "every
      result-affecting input above contributes to config_digest or is recorded by digest in the manifest". The
      manifest records only master_seed from that file (§4.2, §5.1). The template supplies every other
      generator parameter — knn.sample.num, warm.*, mc.*.quantile, dry/wet.spell.change, general.variables —
      which build_weagen_config copies verbatim into the per-realization config
      (prepare_weagen_config.py:57,67-68) and generate_weather.R passes straight to weathergenr
      (generate_weather.R:43-58). The template reaches the rule as a params *path string*, not an input.
    rationale: >
      Editing any of those values changes the generated realizations and therefore every downstream indicator,
      while firing no rerun trigger anywhere in the v2 freshness model: the manifest is unchanged, so
      prepare_weagen_config_rlz does not re-run, generation does not re-run, member_hash does not change, and
      the sweep skips everything. The gap exists in v1 too, but v1 never claimed the manifest answers "what
      was this built from"; v2 does, and centralizes freshness there.
    suggested_fix: >
      Record a template content digest in run.* and thread it as a params value of 3.01 and 3.05 on the same
      file_digest_or_absent pattern the guard already uses (Snakefile_climate_experiment:174-175); or narrow
      §2.4's provenance sentence to name the exception explicitly.
  - id: arch-8
    severity: major
    section: "§10 Contract-delta table / §13 Step 6"
    finding: >
      Several surfaces are dispositioned "verbatim" on the strength of validator-code stability while their
      contract documents pin producer/consumer *rule* identity that v2 retires: WG-2's consumer is "rule 3.07
      generate_climate_stress_test" (weather-generator-seam.md:116-117), WG-5's is "rule 3.09
      downscale_climate_realization" (:196), WG-6's is "rule 3.10 run_wflow" (:233), WG-4's producer is "rule
      3.06 (cst_0) / rule 3.07 (cst_m)" (:160) and its *pinned surface* explicitly includes "the DAG-globbed
      naming pattern (rule 3.08 expand; rule 3.09 wildcards)" (:167-173) — a property v2 removes, since the
      perturbed NCs cease to be DAG nodes. The bounded-substitution walkthrough (:284-289) names rules 3.04-3.07
      as what a replacement generator replaces and rules 3.02/3.08/3.09 as pinned boundaries. §13 step 6
      commits only to extending validate_wg3, replacing the two --notemp sections, and extending validate_hm7.
    rationale: >
      G6 requires "the contract docs updated with the milestone". As scoped, the seam docs would emerge from R9
      naming four rules that no longer exist and pinning a DAG-globbing property the pipeline no longer has,
      which is exactly the drift the contracts exist to prevent — and the walkthrough, the artifact a future
      generator-swapper reads end to end, would be actively misleading.
    suggested_fix: >
      Add a row to §10 for producer/consumer rule identity, and widen §13 step 6 to a full pass over both seam
      docs' producer/consumer/lifecycle/pinned-surface fields plus the WG-4 naming-pattern clause and the
      substitution walkthrough.
  - id: arch-9
    severity: major
    section: "§2.5 Delegated implementation ownership / §13 Migration and commit plan"
    finding: >
      Work enumerated in §4/§6/§13 is missing from the ownership table and from the migration steps. (a)
      §6.6 step 3 runs "downscale_climate_forcing.py's body, in-slot" and §9.6 classes that leg "Identical —
      same script body", but the module has no __name__ guard and reads the snakemake global at module top
      level by design (blueearth_cst/experiment/downscale_climate_forcing.py:11-19); it cannot be called
      in-process without a refactor into a callable whose signature the design does not specify and whose
      owner §2.5 does not name. (b) export_wflow_results.py (ledger-driven inputs + response_long.csv) and
      prepare_weagen_config.py (the three generate-branch keys) have no owner row. (c) The guard fusion
      breaks tests the plan never mentions: tests/test_climate_store_contract.py:339-347 asserts the guard
      rule's outputs are exactly ["guard_ok", "sentinel"] and that the guard_ok path ends with "/.guard_ok";
      tests/test_guard_invalidation.py:95-124 seeds and re-triggers the guard by targeting
      experiments/<exp>/.project_consistency_ok and asserts the .guard_ok file exists; and retiring
      batch_size/batch_size_max orphans dev/scripts/estimate_batch_makespan.py with
      tests/test_estimate_batch_makespan.py.
    rationale: >
      A brief generated from §2.5 would leave the single largest in-slot refactor unowned and unspecified, and
      §13 step 7's "pytest tests/" would fail on at least three modules with no step responsible for them.
      C-15 names only tests/test_check_project_consistency.py, so the design's own claim that "guard failure
      modes are unchanged" is checked against a strictly smaller surface than the change touches.
    suggested_fix: >
      Add rows to §2.5 for the downscale entry-point refactor (with its signature), the reduce rewrite and the
      weagen-config change; add an explicit test-migration item to §13 step 5/6 naming the three modules and
      the fate of estimate_batch_makespan.py.
  - id: arch-10
    severity: minor
    section: "§4.4 Stage 4 — Reduce / §10 Contract-delta table"
    finding: >
      analyze_wflow_results also writes one RT_<var>.csv per discharge variable into indicators_dir
      (export_wflow_results.py:300-315) as undeclared outputs. §3.1's stage-4 box lists "RT_*" among the
      reduce's products, but §4.4's output row, §10's HM-7 row, C-11's lossless-pivot claim and §13 step 9's
      expected manifest delta all omit them.
    rationale: >
      The milestone re-records the baseline and rewrites the reduce's input plumbing; leaving a class of
      existing product artifacts undispositioned is the kind of omission that reads as an oversight later, and
      C-10's "byte-identical when fed the same member CSVs" is stated for Qstats/basin only while the same run
      writes RT_* under a changed scenario-index path. Relatedly, §4.5 does not say whether rule all's
      WF3_TARGETS (Snakefile_climate_experiment:222-228) gains response_long.csv — G8 promises the entry
      contract is unchanged, and the target set is the user-visible half of it.
    suggested_fix: >
      State RT_*.csv's disposition (unchanged, still undeclared, covered by C-10's direct diff) in §4.4 and §10,
      and say explicitly whether response_long.csv joins WF3_TARGETS.
  - id: arch-11
    severity: minor
    section: "§6.5 Logging and benchmark capture"
    finding: >
      Both the whole-sweep rule benchmark (_parts/3.08_run_sweep.tsv) and the per-member benchmarks
      (_parts/3.08_run_sweep/*.tsv) are collected by merge_benchmarks' recursive glob
      (blueearth_cst/shared/merge_benchmarks.py:55-59), and its TOTAL row sums the s / io / cpu columns
      (:19,81-83).
    rationale: >
      wf3_benchmarks.md's TOTAL will roughly double-count the sweep's wall time, since the member rows and the
      job row measure the same work. v1 has no such overlap (3.10 contributes batch rows only), so this is a
      new reporting regression in the artifact §6.5 discusses.
    suggested_fix: >
      Note the double-count in §6.5, or emit the per-member timings only to the ledger and let the rule row be
      the sole benchmark part.
  - id: arch-12
    severity: minor
    section: "§5.2 Ledger schema / §7.4 Quarantine and orphans / §9.4 OQ-4"
    finding: >
      sweep_completeness.csv is specified as one row "for every member of the manifest" with columns
      member_id, state, attempts, stage, class, detail, "plus a trailing comment-free summary the reduce
      reads" (§5.2); §7.4 then adds rows with state=orphan for members that are by definition *not* in the
      manifest, and §9.4 introduces a further product artifact indicators/completeness.csv that appears in no
      output list, no contract row and no baseline discussion.
    rationale: >
      Three sections describe the same record with three different row populations, and a trailing
      heterogeneous summary row makes a CSV that a naive reader cannot parse. indicators/ is a product
      directory pinned by check_baseline (dev/scripts/check_baseline.py:187-189), so a new conditional file
      there needs an explicit disposition.
    suggested_fix: >
      Fix one row population (manifest members plus orphans, with state as the discriminator), replace the
      trailing summary with a sidecar or a separate JSON, and give indicators/completeness.csv a row in §10 and
      a line in §13 step 9.
  - id: arch-13
    severity: minor
    section: "§5.3 Crash-consistency / §5.4 Member state machine"
    finding: >
      §5.4 declares a state machine but §5.3's fold rule is "take the last row" for the current member_hash,
      and the crash-consistency table validates only line framing, JSON parseability, row schema and
      member_id membership. No rule checks transition legality, so an impossible history (succeeded followed
      by claimed with no intervening quarantine; two succeeded rows; a terminal row with no preceding claimed)
      folds to a valid state.
    rationale: >
      §8.1's escalation clause is worded as "any case where the manifest's recorded digests and the live files
      disagree in a way no legal member transition resolves", which presumes legality is evaluated somewhere;
      it is not. Given risk R-1 rates "a ledger bug silently skips a member" High, the cheapest detector for
      that bug class is the one the design omits.
    suggested_fix: >
      Add a fifth row to §5.3's table: a row sequence that violates §5.4's transitions is corruption, handled
      like a corrupt row; make it a unit-test case in §13 step 4.
  - id: arch-14
    severity: minor
    section: "§4.2 / §10 WG-3 row / §5.1 config_digest"
    finding: >
      Three smaller inconsistencies. (a) §4.2 and §10 describe the per-realization config as gaining "three
      added keys (rlz.index, seed, work.path)", but seed is an existing pinned WG-3 key
      (dev/contracts/weather-generator-seam.md:141) already read at generate_weather.R:57 and already present
      in the template — it is overridden per realization, not added; only rlz.index and work.path are new.
      (b) config_digest is described only as "canonical digest of the wf3-relevant config subset" and the
      subset is never enumerated, although §7.6's invalidation table depends on exactly which keys it covers.
      (c) Moving the generate config from weather_generator/config/ to weather_generator/_work/ leaves
      weather_generator/config/ with no producer; the design does not say whether the directory retires.
    rationale: >
      (a) would send validate_wg3's extension after the wrong key set; (b) leaves the freshness boundary
      unreviewable and unimplementable without a second decision; (c) leaves a directory in the R07 layout map
      unaccounted for.
    suggested_fix: >
      Say "two added keys plus a per-realization seed override"; enumerate config_digest's covered sections;
      state that weather_generator/config/ retires.
  - id: arch-15
    severity: blocking
    section: "§9.4 OQ-4 — reduce with holes / §8.2 GF-7"
    finding: >
      §9.4's allow_partial column states that under a partial sweep "Qstats.csv" is a "grid with holes; the
      missing (tavg, prcp) rows simply absent". Under the fixture's aggregate_rlz: true
      (config/workflows/snake_config_model_test.yml:80) the reduce cannot produce that shape.
      df_out_mean is pre-sized to st_num rows from the config param (export_wflow_results.py:104), the loop
      runs range(st_num) regardless of what is on disk (:153), and each row is built from
      csv_fns_i = [x for x in csv_fns if x.endswith("cst_<i+1>.csv")] concatenated with no count check
      (:162-171). A single missing member (rlz_2/cst_3) therefore yields a fully populated cst_3 row averaged
      over one realization instead of two; a whole missing cst index yields an empty list into pd.concat and a
      ValueError.
    rationale: >
      The hole surfaces as a silently under-averaged response-surface cell — exactly the distortion the
      ratified fail-loud default exists to prevent, now reachable through the escape hatch the same ruling
      approves. GF-7's expected observation ("Qstats.csv has N rows per statistic", "reduce prints a named
      warning") is unobservable, so the branch that the owner ruling made testable cannot be tested. This
      compounds arch-1 and arch-6, which already disable GF-7 for two independent reasons.
    suggested_fix: >
      Specify what allow_partial does under aggregation: either drop the row entirely (requires the reduce to
      size its frames from the completeness record rather than st_num) or emit it with a recorded realization
      count and a per-cell n in indicators/completeness.csv. Either way the reduce body is no longer
      "unchanged" (§4.4), and §9.6's "Reduce — Identical" parity class needs the qualifier "under full
      completeness".
  - id: arch-16
    severity: minor
    section: "§5.1 path convention / §4.4 Stage 4 — Reduce"
    finding: >
      §5.1 fixes "all artifact paths are relative to exp_dir" and §5.2 carries that convention into
      ledger_final.csv's result column, while §4.4 asserts analyze_wflow_results keeps its body. That body
      opens the paths directly (export_wflow_results.py:95,157,165) with the process CWD at the repo root, not
      exp_dir. endswith matching (:162) and realization_from_run_csv (:24) both survive relativization; the
      file open does not, and the design never names who rejoins exp_dir.
    rationale: >
      The reduce fails on its first read with a FileNotFoundError, on the milestone's central new data path.
    suggested_fix: >
      One sentence in §4.4: the reduce resolves ledger_final.csv's result column against exp_dir before
      calling analyze_wflow_results.
```
