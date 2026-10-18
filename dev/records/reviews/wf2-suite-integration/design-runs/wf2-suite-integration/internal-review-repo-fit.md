```yaml
verdict: revise
doc_version: design-v2.md
findings:
  - id: fit-1
    severity: major
    section: "7. Identity and blast radius / 11. Tree and user-facing change inventory"
    finding: >-
      The new generated tier `data/climate/projections/<ensemble>/analysis/` is not covered by the
      tree inventory. `build_project_tree_rules` classifies projection tiers from a fixed tuple
      (`dev/scripts/semantic_tree_diff.py:449-450`: raw, scalar, summary, plots, plus report.md and
      `_engine/stage_b_settings.json`). The design lists only `tests/test_project_tree_inventory.py`
      and frames the tree question as "whether a retired-paths list exists" (§ 7, § 12); it never
      names `semantic_tree_diff.py` or the `analysis/` tier.
    rationale: >-
      `tree-check` and `semantic_tree_diff.py` will report every `analysis/*` file as unclassified
      on the first rapid run, and `test_project_tree_inventory.py` COVERED (lines 129-132 still name
      `plots/overview/*`) cannot pass with the new tier unless the rule set changes too.
    suggested_fix: >-
      Add `semantic_tree_diff.py` to § 11 and to commit 4 (`analysis` tier), and to commit 5b
      (`plots/full-period/`, `plots/period-*/`, `plots/_engine/`, `plots/captioned/` if the rule is
      finer than `plots/`). Add `analysis/...` rows to the COVERED map in commit 4.
  - id: fit-2
    severity: major
    section: "10. Commit plan / 11. Tree and user-facing change inventory"
    finding: >-
      Two existing test files that exercise retired code are missing from the plan.
      `tests/test_projection_plots.py` tests `projection_plots.py`, which commit 5b deletes; and
      `tests/test_get_change_climate_proj_summary.py:127-162`
      (`test_the_cloud_draws_only_derived_combinations`) calls `plot_change_summary`, which 5b
      removes. Neither appears in § 11's `~`/`-` lists or in 5b's focused checks.
    rationale: >-
      If 5b runs only the listed checks, it will commit a tree where `pytest` fails at import or
      attribute lookup. The delete-what-you-made-unused rule also requires removing them in the
      same commit.
    suggested_fix: >-
      In 5b, list `- tests/test_projection_plots.py` and `~ tests/test_get_change_climate_proj_summary.py`
      (drop the cloud test, and move its derived-combinations property to a test of the new F3.6b
      artist or of `model_changes`). Add both files to 5b's focused checks.
  - id: fit-3
    severity: major
    section: "9.2 Checks (gates paragraph)"
    finding: >-
      § 9.2 says `test-full` is "not required (no `shared/` or WF3/WF4 `script:` change)". The
      AGENTS.md ladder row fires on any change to `shared/` **or a `script:` signature**, not only
      WF3/WF4 ones. This batch changes rule 2.05's declared outputs and params (`stats_change_plt`
      and `figure_names` removed, `analyze_projections.smk:1160,1197`), adds a new `script:` (2.05b),
      and replaces 2.06's inputs and params. The plan also says "`test-e2e` WF2 leg", but `test-e2e`
      is one task with no per-workflow leg (`pixi.toml:160`); the ladder requires the full task when
      a batch changes what a workflow runs.
    rationale: >-
      The `workflow_contract` and `process_isolation` tiers are skipped by `test-fast`. They are
      exactly what this batch's signature changes can break, so the merge would ship them unexercised
      on both platforms.
    suggested_fix: >-
      Commit 6: run `pixi run test-full` and `pixi run test-e2e` (all five workflows), with skip
      reasons read. Drop the "WF2 leg" wording.
  - id: fit-4
    severity: major
    section: "11. Tree and user-facing change inventory (docs row) / 7 (retired files)"
    finding: >-
      The doc targets are named loosely ("docs/ WF2 figure list", "the WF2 docs page"). No figure
      list exists. The live WF2 page is `docs/site/toolbox-reference/workflow-analyze-projections.qmd`,
      and its rule table (lines 11-17) and mermaid DAG (line 30) would lack 2.05b.
      `docs/guide/outputs.md` describes run products and would lack `analysis/`. In the
      rule-index the design cites only lines 881-908, but the numbering table at
      `dev/reference/workflows/rule-index.md:99-101` and the DAG at :782-799 ("2.06 reads 2.04's series,
      not 2.05") also describe 2.06's inputs, which this design changes.
    rationale: >-
      AGENTS.md "Keep configuration references current" makes stale rule tables and DAGs defects. As
      written, the retired-path note has no concrete home, and the rule-index DAG would describe the
      wrong inputs for 2.06.
    suggested_fix: >-
      Name the files in § 11: `workflow-analyze-projections.qmd` (2.05b row, DAG edge 2.04→2.05b→2.06,
      retired-path note, `analysis/` outputs), `guide/outputs.qmd` if it lists WF2 products, and
      rule-index :99-101 and :782-817 in addition to :881-908. Commit 4 (2.05b) and 5b (2.06
      inputs, retirements) each carry their own doc edits.
  - id: fit-5
    severity: minor
    section: "3. Snakemake rules and config (gather edges)"
    finding: >-
      `WF2_TARGETS` (`analyze_projections.smk:883-903`) feeds `rule all` and picks up figures
      automatically through `WF2_FIGURE_PATHS`. However, the `analysis/*.csv` tables and
      `analysis_record.json` reach the DAG only through the gather edges. The comment on that dict
      states the convention that terminal products are "demanded explicitly", and
      `--delete-all-output` relies on the same list. `plots/figure_captions.md` and
      `_engine/figure_captions.json` are also not targets.
    suggested_fix: >-
      Add `analysis_record` (or every table) and the two caption files to `WF2_TARGETS` in commits 4
      and 5a.
  - id: fit-6
    severity: minor
    section: "3. Snakemake rules and config / 2. Module boundaries"
    finding: >-
      The design is silent on the repo's script-body rule. Existing `script:` modules carry an explicit
      "no `from __future__ import annotations`" note (`derive_change_factors.py:28-30`,
      `fetch_gcm_raw.py:33-35`) because Snakemake prepends a preamble. The new
      `prepare_projection_analysis.py` and the rewritten `plot_proj_timeseries.py` must follow it.
      Library modules (`projection_analysis.py` and similar) may keep the import, like
      `projection_figures.py:46` does.
    suggested_fix: State the split in § 3 and copy the NOTE header into the new script.
  - id: fit-7
    severity: minor
    section: "4. Figure contract (captions, tokens)"
    finding: >-
      § 4 cites WF0's caption contract but does not say how WF2 saves figures. WF0's renderer calls
      `fig.savefig(..., dpi=600, facecolor="white")` directly (`diagnostic_render.py:220-225`).
      The shared `snake_utils.save_figure` (`snake_utils.py:1025`) logs the write through the console
      convention. The design also imports `plural` from `diagnostic_figures` (`:224`), which is a
      second `plural` beside `run_log_core.plural` (`:1840`), the one `log_row` conventions mean.
    suggested_fix: >-
      Pick one save path and dpi explicitly. Prefer `save_figure` unless WF0 parity of dpi is required.
      Use `run_log_core.plural` for console rows and the WF0 `plural` only inside caption text.
  - id: fit-8
    severity: minor
    section: "6.1 Declared vs written / 3 (2.05b log)"
    finding: >-
      The 2.05b console surface is unspecified. Unavailable products, unavailable members and
      shifted or joined windows are data-sized lists. AGENTS.md requires `log_row` conventions with
      `listed` caps (`snake_utils.py:939`) and forbids silent caps, so the record carries the full list
      and the log row the capped list. `console_sample_specs.py` also needs a 2.05b sample (its WF2
      targets at :292-298 are already stale, using `figures/` and `gcm-timeseries`).
    suggested_fix: >-
      Add one sentence to § 3: summary rows through `log_row`, with lists capped via `listed` and
      pointing to `analysis_record.json`. In 5b, rewrite the console sample targets to the new paths.
  - id: fit-9
    severity: minor
    section: "3. Snakemake rules and config (rule 2.05) / 10. Commit plan"
    finding: >-
      Commit 1 adds `import hydromt` to `derive_change_factors.py`. Snakemake's default `code`
      rerun trigger re-runs 2.05 on a script edit, so 2.05 re-runs at commit 1 as well as at 5b. That
      contradicts "2.05 re-runs once". The byte-identity check is still valid, but the claim and the
      timing estimate are off.
    suggested_fix: >-
      Move the import into 5b (the same file is already edited there), or reword the claim to "re-runs
      on each commit editing its script; CSVs byte-identical each time".
  - id: fit-10
    severity: minor
    section: "6. Robustness (Kuma table) / 11"
    finding: >-
      `blueearth_cst/projections/model_families.csv` would be the first data CSV inside a projections
      code package. The design does not check `dev/reference/repo-layout.md` placement, or whether
      package data is included by the build (`pyproject` package-data). Alternatively, a data source
      of this kind may belong under `config/` as a defaults file read by rules.
    suggested_fix: >-
      Confirm the placement against repo-layout.md in commit 2. Use `importlib.resources` for the read
      so the file resolves from an installed package.
  - id: fit-11
    severity: minor
    section: "7. Identity and blast radius"
    finding: >-
      The claim that WF3/WF4 never reach `climate_analysis` is loosely worded. WF3/WF4 do import
      `blueearth_cst.climate_analysis.prepare_climate_data_catalog`
      (`experiment/downscale_climate_forcing.py:11`, `experiment/rules/simulate_and_metrics.smk:13`,
      `wf4_ancillary_descriptor.py:342`). Its closure does not include `diagnostic_figures`, and
      `climate_analysis/__init__.py` is empty, so the conclusion holds. Still, § 7 should state it
      precisely, because the WF0 tokens now become a cross-workflow contract surface (AGENTS.md
      "shared helper edited in service of a plot").
    suggested_fix: >-
      Reword § 7 and note that any future edit to `diagnostic_figures` takes the normal ladder,
      not the figure-only gate.
```
