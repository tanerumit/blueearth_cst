```yaml
verdict: revise
doc_version: design-v2.md
findings:
  - id: arch-1
    severity: major
    section: "10. Commit plan (5a/5b) and 3. Gather edges"
    finding: >-
      Commit 5a changes the path grammar of `figure_relative_paths` but keeps 2.05's old cloud and the
      old gather edges until 5b. Today all three are built from that same function's output:
      `ANNUAL_PRECIPITATION_PLOT = WF2_FIGURE_PATHS["overview/annual-precipitation.png"]`
      (analyze_projections.smk:357), `CHANGE_FACTOR_CLOUD_PLOTS` / `CHANGE_FACTOR_CLOUD_PLOT`
      (smk:360-365, `projection_figures.CLOUD_FACETED_PATH`), which feed 2.05's `stats_change_plt`
      (smk:1160), 2.06 (smk:1280) and `gather_logs`/`gather_benchmarks` (smk:1328-1329, 1351-1352). If the
      grammar returns only `full-period/` and `period-*` paths, these lookups fail when the Snakefile is
      parsed. Commit 5a also says "the old 2.06 figures move to 5b's deletion", which contradicts 2.06
      becoming a pure renderer of the new set in that commit. § 10 says the overlap "keeps 5a and 5b
      separately bisectable", but the design never says how the old paths are still produced in 5a.
    rationale: >-
      As written, commit 5a fails to parse (`KeyError`) or leaves a gather edge pointing at a path that
      no rule produces (`MissingInputException`). Either way it breaks § 10's rule that every commit is
      independently green, along with the `test_cli.py` gate listed for 5a.
    suggested_fix: >-
      In 5a, write the retired `overview/` paths as literal constants in the Snakefile, or keep a
      `legacy_relative_paths()` helper that 5b deletes, and keep the gather edges on 2.05's cloud only.
      Alternatively, move the gather-edge switch to 2.06's terminal into 5a. State which old 2.06 outputs
      (if any) survive 5a.
  - id: arch-2
    severity: major
    section: "6.1 Declared vs written; 5.6 Per-member data ends"
    finding: >-
      Availability is decided at parse time from `POINTS` and `ACQUISITION_WINDOWS` alone. Whether a
      member covers a window is only known at run time (§ 5.6: "a member whose series does not cover the
      parse-time window, e.g. a run ending 2099, is unavailable"). Some CMIP6 runs end in Dec 2099, and
      360-day calendars end on 2099-12-30, so the shifted far window 2071–2100 regularly loses whole
      models. If enough models drop out, a product that was declared at parse time (F5.1 needs ≥ 2 models,
      F3.5c needs a model with ≥ 2 members, per-window products need ≥ 1 model) cannot be drawn, and
      § 6.1 then says 2.05b "raises". That turns a predictable data property into a hard failure of the
      whole WF2 run. The "runtime residue" category is therefore not rare: § 5.6 creates it routinely,
      and it is in tension with the G1 framing that missing products are listed rather than fatal.
    rationale: >-
      Ensembles that are valid and fully acquired abort WF2 for any far horizon in which a few models end
      in 2099. The user then has to drop models from the config by hand, although the record is designed
      to report exactly this kind of unavailability.
    suggested_fix: >-
      Option 1: make parse-time availability use the data-end each member actually reports. The
      acquisition or series identity sidecars (`series_identity`, already read at parse time for
      `POINTS`) could carry it, so § 5.6 coverage becomes a parse-time fact.
      Option 2: give 2.06 a single owned output directory per window plus the captions JSON as terminal,
      and keep only the captions manifest as the declared contract (an owned `directory()` instead of a
      checkpoint).
      Either way, define which shortfalls are a parse-time "not produced" and which are a genuine error.
  - id: arch-3
    severity: major
    section: "4. Figure contract (shared folders) vs 3. 2.05b tables"
    finding: >-
      When two horizons resolve to one analysis window, they share one `period-<a>-<b>/` folder. The
      design does not say whether the per-window tables (`changes.csv`, `change_summary.csv`,
      `sign_agreement.csv` and so on) are keyed by horizon, by analysis window, or by both. It also does
      not say which horizon's rows a shared-folder figure draws. The two horizons' reference windows can
      differ only when they have different configured references, and the reference is global, so the
      rows are numerically duplicates. Without a stated key, however, either the tables duplicate rows,
      which risks figures that double-count, or 2.06 needs a de-duplication rule that is not specified.
      The F3.6b "one per window" cloud and the combined cloud ("≥ 2 distinct analysis windows") depend on
      the same choice.
    rationale: >-
      If the key is left implicit, the implementation can draw duplicated or mixed rows in shared-folder
      figures. The § 9.2 "two horizons merging into one folder" test checks bounds only, not table keys.
    suggested_fix: >-
      Key the analysis tables by `window_id` (`<a>-<b>`) and carry a `horizons` list in
      `analysis_record.json`. Compute each window once in 2.05b, and add a table-key assertion to the
      merge test.
  - id: arch-4
    severity: minor
    section: "4. Figure contract (count formula)"
    finding: >-
      "n windows 5 + 10·n + 1" gives 16 for n = 1, but the combined cloud is drawn only when n ≥ 2. The
      correct count is 5 + 10·n + [n ≥ 2], which matches the "one window 15" figure in the same
      sentence and in § 1.
  - id: arch-5
    severity: minor
    section: "2. Module boundaries / 6.1"
    finding: >-
      `suite_availability` lives in `projection_figures` (the figure contract) but also decides 2.05b's
      table and record content (it is passed as a param). Ownership is single, but the module name
      suggests a plotting concern. A brief docstring note, or placing it next to `analysis_windows`,
      would make it clear that the calculation rule depends on it. 2.05b also receives `availability` as a
      param, so any change to the availability logic re-runs 2.05b. That is acceptable, but should be
      stated.
  - id: arch-6
    severity: minor
    section: "3. Rule 2.05b"
    finding: >-
      2.05b reuses 2.05's identity assertion and calendar check "by calling" functions in
      `derive_change_factors.py`, which is a `script:` module (derive_change_factors.py:111-265 are plain
      functions, so importing them is feasible). Importing one `script:` module from another couples the
      two rule scripts. Promoting the two helpers into a library module such as `series_identity` would
      keep the boundary clean. This module is not a root of `STAGE_B_KERNEL`, so the move does not change
      the hash. Verify that before the move.
```
