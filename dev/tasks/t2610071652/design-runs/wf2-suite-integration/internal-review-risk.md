```yaml
verdict: revise
doc_version: design-v1.md
findings:
  - id: risk-1
    severity: major
    section: "6. Robustness / 4. Figure contract (unavailable products, G1 ruling)"
    finding: >
      G1 ruled "no placeholder figures; listed as unavailable with reason", but design-v1 declares every
      figure statically from figure_relative_paths(horizons) and relies on placeholders to satisfy
      Snakemake (§6 last paragraph, §8 "Unavailable products" row). Removing the placeholder without
      changing how outputs are declared fails the run with MissingOutputException whenever a product is
      unavailable. The rapid and wf2_fast configs make this immediate rather than hypothetical: rapid has
      2 models, 1 scenario, 1 member (test_case/project_config_rapid_analyze_projections.yml:8-14);
      wf2_fast has 1 model (project_config_wf2_fast_analyze_projections.yml:6-11). Depending on how
      "< 2 members anywhere" is read (§6), F3.5c is unavailable on both, and with one model the
      model-spread products degenerate.
    rationale: >
      If the static list is kept, the default (on) suite breaks the cheapest smoke configs that AGENTS.md
      tells you to run for any WF2 change. If a checkpoint is used instead, §8 already explains why that
      breaks rule all, the gather edges and the tree inventory.
    suggested_fix: >
      Decide availability at PARSE time from what the DAG already knows: POINTS/COMBINATIONS give models,
      members and scenarios per cell, the acquisition span is a constant (series_identity.py:97-100),
      and the variable list is config. figure_relative_paths then takes that availability and returns
      only the products that can be drawn; analysis_record.json lists the dropped ones with reasons.
      Data-dependent residue (for example an all-NaN series) should raise loudly rather than write a
      figure. Pin the member-count rule exactly (per model, or pooled across models) and test it on
      rapid and wf2_fast.
  - id: risk-2
    severity: major
    section: "5. Numerical contracts (§5.4 dry-reference; G1 dom-5)"
    finding: >
      dom-5 was accepted as a correctness fix: one dry-reference rule. The design states the "one
      calculator" claim and the byte-identical claim (§5.1) assuming the kernels do not change. Of the
      two obvious ways to apply dom-5, one breaks byte identity: moving the lab's per-period rule into
      get_change_monthly_clim_proj, or making the kernel the single rule by editing it. Either changes
      aligned monthly rows in dry cells, and an edit to get_change_annual_clim_proj, a STAGE_B root
      (analyze_projections.smk:512-518), would also move STAGE_B_HASH. The other way, applying the
      kernel's per-statistic rule in the new seasonal/CV code only, keeps both.
    rationale: >
      The byte-identity check runs on P0 and rapid only. P0 has no dry cells (all 23,800 rows "ok",
      §5.4), so an edit to the aligned rule would pass the falsifier and still change the numbers for an
      arid basin. That is a silent change to a published contract.
    suggested_fix: >
      State that dom-5 is implemented by applying the kernel's existing per-statistic rule (threshold from
      min_reference) inside get_change_seasonal_clim_proj / CV only, with the kernel untouched. Add a
      synthetic dry-reference test that compares aligned CSV rows before and after, because P0 cannot
      exercise this path.
  - id: risk-3
    severity: major
    section: "2. Module boundaries / 6. Robustness (analysis window placement; G1 dom-1, dom-2)"
    finding: >
      The window rule and the dom-2 shift are specified for the far end only. Three cases are not
      covered. (a) A near horizon whose ±15-year window crosses 2014/2015 (for example 2015-2030 gives
      2008-2037) needs the historical and scenario series concatenated. §2 says analysis_slice slices
      "the scenario series"; the calendar-agreement check (derive_change_factors.py:199-216) and the
      historical-run choice are not mentioned. (b) A window shifted to "fit the data end" under a
      non-January water year: scenario data end 2100-12 (series_identity.py:99), so an Oct-start year
      has its last complete WY ending Sep 2100. "2071-2100, 30 years" then depends on how the WY is
      labelled, and may hold only 29 complete years. (c) Per-model data ends: some CMIP6 scenario runs
      stop in 2099 or 2299, but the folder name period-<a>-<b> is fixed at parse time (§4). A
      runtime-shifted window can then disagree with the folder name and caption, and two far horizons
      shifted to the same window collide with the parse-time duplicate check (projection_figures.py:131-136),
      which rejects a valid config.
    rationale: >
      Each case gives either wrong years under a confident label or a parse-time refusal of a reasonable
      config. None of them shows up on P0 or rapid, which both have only `mid` 2046-2054 and a January
      water year.
    suggested_fix: >
      Compute the window, including the dom-2 shift, at parse time from the acquisition constants and
      water_year_start, using one function shared by figure_relative_paths and 2.05b. Treat member data
      that ends before the window as unavailable per member, never as a per-member shift. Specify the
      hist+scenario join, or rule it out with a reason. Decide whether two horizons that share a window
      are merged or refused. Add unit cases for an Oct WY at 2100, a window crossing 2014, and a
      collision after a shift.
  - id: risk-4
    severity: major
    section: "10. Commit plan"
    finding: >
      Commit 5 lands, all at once: the artists and captions modules, the path grammar, the 2.06 rewrite,
      removal of the 2.05 cloud, the gather edges, the config key, deletion of retired code, the tree
      inventory, check_baseline, the console spec and docs. Commit 4 adds 2.05b, but nothing consumes its
      outputs until commit 5. So unless rule all or a gather edge names them, the commit-4 "rapid WF2 run"
      does not execute 2.05b at all, and the parity test is the only thing that exercises it.
    rationale: >
      Commit 4 can pass while 2.05b is unscheduled. A defect in commit 5 then cannot be bisected among
      roughly ten surfaces. Each commit is not independently green as the plan claims.
    suggested_fix: >
      In commit 4, add the 2.05b outputs to rule all (or to the gather edge), and dry-run plus run rapid
      to show the job executes. Split commit 5 into (5a) path grammar, artists and captions with 2.06
      repointed, and (5b) retirement: the 2.05 cloud, projection_plots, gather edges, inventory and
      baseline entries.
  - id: risk-5
    severity: major
    section: "3. Snakemake rules and config (rule 2.05 figure_names)"
    finding: >
      2.05 keeps figure_names = WF2_FIGURE_RELATIVE_PATHS as a param (analyze_projections.smk:1197) so that
      report.md can list the figures. Under the new design the figure list depends on horizons, on
      parse-time availability (risk-1) and on the captioned_figures flag. Any change to the figure set
      changes 2.05's params, re-runs the change-factor merge and rewrites provenance/report. That
      invalidates 2.05b through its composition_csv input and then 2.06. The inverted ownership is a
      derive_ rule promising outputs of a later renderer.
    rationale: >
      Every future figure tweak re-runs the cache-guarded terminal that §8 says should be insulated from
      plot-table changes. That contradicts the design's own argument for a separate 2.05b. It also makes
      "2.05 re-runs once" an understatement.
    suggested_fix: >
      Drop figure_names from 2.05 params. Have report.md point to plots/figure_captions.md, which 2.06
      owns, or move the figure section of report.md to 2.06. Make 2.05b depend on the series and on
      composition only through a stable input, not on report outputs.
  - id: risk-6
    severity: major
    section: "9. Validation plan (parity with lab)"
    finding: >
      §5.2 and §9 require every downstream table to match lab results within 1e-9. The G1 rulings,
      however, intentionally change methods relative to the lab. dom-4 weights pooled member ratios by
      1/members-per-model, so variability_member_ratios and the F3.5c summary differ from the lab by
      design. dom-6 adds family counts and a small-change marker to sign_agreement. dom-11 adds
      provisional families to coverage. dom-1 may switch the reference. The parity test as written
      either fails or gets loosened ad hoc.
    rationale: >
      A parity gate that is expected to fail on some tables invites silent exclusions, and that is the
      opposite of the "never silently widened" promise in §5.2.
    suggested_fix: >
      List the tables and columns under lab parity explicitly. Exclude the ruling-changed ones (dom-4,
      dom-6, dom-11, and dom-1 where it is triggered) by name with the reason. Cover each changed table
      with the known-answer tests from dom-7 instead.
  - id: risk-7
    severity: minor
    section: "7. Identity and blast radius (STAGE_B_HASH)"
    finding: >
      "STAGE_B_HASH unchanged" holds only if no root or callee body changes. kernel_closure follows names
      in the roots' bytecode and hashes referenced module constants (series_identity.py kernel_closure,
      kernel_hash). hydrological_year_bounds is a root (analyze_projections.smk:512-518). Refactoring it
      so that analysis_window or the dom-2 shift can reuse it is the natural move, and it changes the
      hash, which forces re-derivation of every series. On P0 that is network-bound.
    rationale: >
      The commit-1 hash check catches it, but only after the edit. Stating the constraint up front avoids
      the rework.
    suggested_fix: >
      State as a rule that analysis_window and the new functions may CALL roots but must not edit them,
      and must not edit any constant that a root references.
  - id: risk-8
    severity: minor
    section: "4. Figure contract (tokens import)"
    finding: >
      Importing climate_analysis.diagnostic_figures from projections pulls in climate_analysis/__init__.py
      and matplotlib for WF2. The WF3/WF4 inventory follows package initializers
      (content_identity.py:112-117). The direction projections -> climate_analysis does not reach WF3/WF4
      today, but any later edit to diagnostic_figures made for WF0 would now silently restyle WF2 figures.
    rationale: >
      This is coupling without a test, and WF0 figure changes would carry an unflagged WF2 blast radius.
    suggested_fix: >
      Add a WF2 render smoke test to the WF0 figure-test path, or record the dependency in rule-index.md.
  - id: risk-9
    severity: minor
    section: "7. Identity and blast radius (baseline)"
    finding: >
      check_baseline.py:313-330 lists three retired PNG targets, and dev/baseline/manifest.json carries
      their fingerprints. Editing only check_baseline.py leaves --include-figures reporting the old
      entries as missing. The manifest is already stale (AGENTS.md), so it is unclear which record gets
      updated.
    rationale: >
      --include-figures then shows spurious misses that read as defects.
    suggested_fix: >
      Replace the three entries with one or two new stable paths: full-period/annual-precipitation.png
      and, if declared, period-<a>-<b>/change-factor-cloud.png. Note that the manifest re-record is
      deferred to the pending regeneration.
  - id: risk-10
    severity: minor
    section: "1. Overview / 11. inventory (old outputs)"
    finding: >
      Retired figures stay on disk in existing project trees (§11 says so). tree-check and
      test_project_tree_inventory treat undeclared files as findings, so every existing project shows
      stale-file noise after upgrade.
    rationale: >
      Users read the leftover overview/ PNGs as current.
    suggested_fix: >
      Have 2.06 or a doc note list the retired paths for deletion, or add them to the
      prune/tree-check known-retired list.
```

Notes outside the contract:

- I verified §5.3 against the code. 2.05 calls the monthly kernel without water_year_start
  (derive_change_factors.py:250-257), while annual uses it (:234-241).
- §2 is consistent with kernel_closure semantics: additive, uncalled functions do not enter STAGE_B_HASH.
- §7 is accepted subject to its own falsifier: there is no reverse import into experiment/.
