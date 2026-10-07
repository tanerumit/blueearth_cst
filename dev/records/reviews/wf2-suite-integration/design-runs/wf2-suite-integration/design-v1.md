# WF2 suite integration — design v1

- **Status:** draft (stage 1, design-review loop `wf2-suite-integration`; gates G1/G2 pending)
- **Genre:** decision record, milestone style (goal, what changes, alternatives, commit plan)
- **Task:** `t2610071652` · lane `feat/wf2-cmip6-improvements` (session-1) · **Date:** 2026-10-07
- **Lifecycle:** `maintained-current` until implementation lands; revision log append-only
- **Revisions:** v1 2026-10-07, first draft from `intake.md`

Paths without a root are relative to the session-1 worktree. `lab:` is `C:\Users\taner\workspace\wf0-lab`.
`P0` is the development ensemble run at `C:/data/cmip6/gabon-ntoum-dev-ensemble` (13 models, 25 members,
4 SSPs, one horizon `mid` 2046–2054, January water year: lab `summary.json` `settings`).

## Contents

1. [Overview, goal, scope](#1-overview-goal-scope)
2. [Module boundaries](#2-module-boundaries)
3. [Snakemake rules and config](#3-snakemake-rules-and-config)
4. [Figure contract](#4-figure-contract)
5. [Numerical contracts](#5-numerical-contracts)
6. [Robustness](#6-robustness)
7. [Identity and blast radius](#7-identity-and-blast-radius)
8. [Alternatives considered](#8-alternatives-considered)
9. [Validation plan](#9-validation-plan)
10. [Commit plan](#10-commit-plan)
11. [Tree and user-facing change inventory](#11-tree-and-user-facing-change-inventory)
12. [Assumptions, unknowns, open questions for G1](#12-assumptions-unknowns-open-questions-for-g1)

## 1. Overview, goal, scope

**Proposal.** Add one WF2 rule that turns the per-member basin series into **analysis tables** on a
30-water-year analysis window, and repoint the existing plot rule so it draws the owner-accepted 15-figure
set from those tables. Change-factor arithmetic stays where it is: the analysis window calls the same
`get_change_{annual,monthly}_clim_proj` kernels on a different time slice, and only the genuinely new
arithmetic (seasons, detrended SD/CV) is added beside them in `get_change_climate_proj.py`.

```
scalar/*.nc ──► 2.05 derive_change_factors ──► summary/*_change_factors_{annual,monthly}.csv  (unchanged bytes)
     │                    (no figure any more)    composition.csv, provenance.json, report.md
     └────────► 2.05b prepare_projection_analysis ──► analysis/*.csv  (new, analysis window + full record)
                                   │
                                   ▼
                 2.06 plot_climate_projections ──► plots/full-period/*.png, plots/period-<a>-<b>/*.png,
                                                   plots/figure_captions.md, plots/_engine/figure_captions.json
```

**Settled framing (owner rulings 2026-10-07, intake table).**

- *Analysis + figures* move into `blueearth_cst/projections`; **one calculator** — the analysis window
  extends `get_change_climate_proj`, it does not run beside it.
- *Lab style* for WF2 figures (captions outside the image, scenario key top-right, no model labels on the
  cloud, WF0 size classes). Revises the 2026-08-11 toolbox rulings for WF2 only.
- Design doc + review loop, then commit-to-commit implementation on this lane.

**What the user gets.** The same change-factor CSVs (byte-identical), a new `analysis/` table folder, and
the 15 accepted figures (§4) in place of today's five, with recoverable captions.

**Non-goals** (intake § Non-goals): dropped figures F3.5b, F3.6, F3.7, F3.8 as figures; daily extremes,
drought, warming levels, emergence, maps, weighting, partitioning; CST-API/frontend; fixing t2610070255;
WF0/WF1 figure conventions. CMIP6 stays a plausibility overlay (AGENTS.md § Background): nothing written here
is read by WF3/WF4.

## 2. Module boundaries

Owner per calculation. "Lab source" is the function whose behaviour is ported (not copied wholesale;
`lab:docs/wf2-integration-notes.md` § Candidates says the same).

| Calculation | Toolbox owner (new = N, extended = E) | Lab source |
|---|---|---|
| Analysis window bounds: 30 complete water years ending at the last WY inside `c-14..c+15`, `c=floor((a+b)/2)` | E `get_change_climate_proj.analysis_window`, `analysis_slice` | `core.analysis_window`, `core.window_bounds` (`lab:wf2_lab/core.py:111-183`) |
| Annual + monthly mean/std on the analysis window | **existing** `get_change_annual_clim_proj`, `get_change_monthly_clim_proj`, called on the analysis slice | reconciled equivalent in `core.change_rows` |
| Seasonal (DJF/MAM/JJA/SON) values, month-length weighted; detrended SD (OLS within window, ddof 0); precip CV of period integrals | E `get_change_climate_proj.get_change_seasonal_clim_proj`, `detrended_std` | `core.period_values`, `core.detrended_std`, `core.statistics` (`core.py:203-255`) |
| Long per-member analysis table (status/reason per row) | N `projections/projection_analysis.py` `analysis_change_table` | `core.change_table` (shape and status vocabulary only) |
| Member→model reduction, ensemble summary with IQR floor (10 models) | N `projection_analysis.model_changes`, `ensemble_summary` | `means.model_changes`, `ensemble_summary` (`means.py:93-133`) |
| Sign agreement (`k/n`, median sign, heuristic band) | N `projection_analysis.sign_agreement` | `agreement.sign_agreement` (`agreement.py:44-69`) |
| C2 climatology + monthly change summaries | N `projection_analysis.climatology`, `monthly_change` | `seasonal.py:35-71` |
| C3 member anomalies vs own 1985–2014 mean; per-model and ensemble range | N `projections/projection_trajectories.py` `member_anomalies`, `model_trajectories`, `trajectory_range` | `trajectories.member_anomalies`, `model_trajectories`, `fan` (`trajectories.py:64-141`) |
| C4 variability ratios: member ratios, per-model geometric mean, log-scale summary, pooled member ratios | N `projection_analysis.member_ratios`, `model_ratios`, `ratio_summary` | `variability.py:50-100` |
| C0 coverage / availability with Kuma et al. (2023) family, institution, country | N `projections/projection_coverage.py` `coverage_table`, `availability_table`; data `projections/model_families.csv` | `coverage.py:63-176`, `MODEL_FAMILIES`, `INSTITUTION_COUNTRIES` (`coverage.py:136-145`) |
| Figure artists (lab style) | N `projections/projection_suite_figures.py` (name open, G1-4) | `figures_wf2.py` (reference implementation) |
| Captions | N `projections/projection_captions.py` | `captions_wf2.caption` |
| Figure path contract | E `projection_figures.figure_relative_paths` (stays the single source) | `run.period_folder` |
| Calendar month lengths | **existing** `calendar_weights` | lab mirrors it (`inputs.same_month_lengths`) — not ported |

Rules for the split:

- Every new function in `get_change_climate_proj.py` is **additive** and is **not called** by any
  `STAGE_B_KERNEL` root (`analyze_projections.smk:512-522`). `kernel_hash` follows callees
  (`series_identity.py:369-399`), so `STAGE_B_HASH` and rule 2.05's inputs stay unchanged.
- The C3 smoothed fan (20-year running mean) is computed only if drawn; it is **not** drawn (report
  `lab:docs/wf2-suite-report.md:265-267`), so it is **not ported**. The trajectory figure uses unsmoothed
  annual anomalies.
- Aligned-window rows are **not** recomputed in the new tables: they already live in
  `summary/*_change_factors_*.csv`. Figures use the analysis window only (intake § revised figure set).

**Not ported, and their tables not written:** F3.5b (`c4_member_spread`), F3.6 scaling (`c6_scaling`),
F3.7/F3.8 sensitivity (`c6_sensitivity*`), paired contrasts (`c5_paired_contrasts`, `c5_contrast_summary`),
`c4_paired`, the C3 smoothed fan, the reconciliation table (a lab self-check against the toolbox, replaced by
the parity test in §9), the tabbed HTML page (§4). Writing an undeclared or unused table would breach the
"every output declared" rule; adding them later is a separate, opt-in decision.

## 3. Snakemake rules and config

**New rule 2.05b `prepare_projection_analysis`** (naming.md §8b: `prepare_` = compute something a later rule
needs; §9: letter suffix, no renumbering).

| Field | Value |
|---|---|
| input | the same explicit `series_nc` list as 2.05 (historical + scenario per resolved point); `composition_csv` (2.05 output); `_STAGE_B_STAMP` |
| params | `horizons`, `water_year_start`, `points` (the same records 2.05 receives), `variable_spec`, `min_reference`, `analysis_reference` (constant, §5), `table_names` |
| output | `analysis/` tables, declared individually (§11): `coverage.csv`, `availability.csv`, `changes.csv`, `model_changes.csv`, `change_summary.csv`, `sign_agreement.csv`, `climatology.csv`, `climatology_summary.csv`, `monthly_change_summary.csv`, `member_anomalies.csv`, `trajectory_range.csv`, `variability_member_ratios.csv`, `variability_model_ratios.csv`, `variability_summary.csv`, `analysis_record.json` (windows, methods, membership, unavailable products) |
| script | `blueearth_cst/projections/prepare_projection_analysis.py` |
| threads / resources | 1 / `mem_mb = 1024` (P0 series total is small; lab ran in ~1–3 min incl. figures, untimed) |
| log / benchmark | `PREPARE_PROJECTION_ANALYSIS = RULES.logged("2.05b", "prepare_projection_analysis", summary=...)` |

It reads the scalar series with the same identity assertion 2.05 uses (`series_identity.assert_series_identity`,
`derive_change_factors.py:150-160`), so a stale series cannot slip in.

**Rule 2.05 `derive_change_factors`** — arithmetic unchanged. Loses `stats_change_plt` and the
`plot_change_summary` call (`derive_change_factors.py:535`). `combine_changes` stays imported from
`get_change_climate_proj_summary`, which keeps the hydromt `.raster` accessor registration chain intact
(`get_change_climate_proj.py:8-17`); commit 1 adds an explicit `import hydromt` in
`derive_change_factors.py` anyway so the coupling is no longer incidental. Its `figure_names` param changes,
so **2.05 re-runs once** and `report.md` is rewritten with the new list (`report.py:162-166`); the CSVs must
come out byte-identical (§5).

**Rule 2.06 `plot_climate_projections`** — keeps its name and number; becomes a pure renderer of
`analysis/*.csv` (the cloud is drawn from `model_changes.csv`, not from the stage-B merge). Inputs: the declared analysis tables. Outputs:
every path of `figure_relative_paths`, `plots/figure_captions.md`, `plots/_engine/figure_captions.json`,
and captioned copies when opted in. Script stays `plot_proj_timeseries.py`, rewritten as a thin driver over the
new artist module. It no longer reads `scalar/*.nc` (2.05b owns all calculation; figures render tables, the
principle already stated at `analyze_projections.smk:1258-1262`).

**Gather edges.** `gather_logs` and `gather_benchmarks` (`analyze_projections.smk:1324-1361`) name
`CHANGE_FACTOR_CLOUD_PLOT` and `ANNUAL_PRECIPITATION_PLOT`; both are retargeted to
`plots/_engine/figure_captions.json` (2.06's terminal) and the annual CSV, so the 2.05b log part is merged
and not stranded.

**Retired figures:** `overview/annual-{precipitation,temperature}.png`, `overview/change-factor-cloud.png`,
`overview/change-factor-cloud-combined.png`, `windows/<h>/monthly-change-factors.png`. Their content survives
as F3.4b, F3.6b and F3.3. The monthly change-factor figure on the *aligned* window disappears; the aligned
monthly numbers remain in the CSV. Retired code: `projection_plots.draw_*`, `get_change_climate_proj_summary.plot_change_summary`,
`plot_proj_timeseries.annual_series`/`monthly_change_from_table` once no caller remains (delete per AGENTS
coding defaults).

**Config.** The suite is **on by default** (it replaces the figure set; there is no "old figures" mode). One
optional workflow-file key, mirroring WF0's `diagnostics.captioned_figures`
(`climate_analysis/diagnostic_settings.py:12`):

```yaml
# project_config.analyze_projections.template.yml, REPORTING section
#captioned_figures: false    # also write plots/captioned/<folder>/<name>.png with the caption below the image
```

Read with `get_config(my_cfg, "captioned_figures", False, optional=True)`, type-checked as bool like
`subbasin_figures` (`analyze_climate.smk:309-311`). It is a WF2-only key, so it lives in the workflow file,
not the project file (AGENTS.md § Repo Map). No `advanced_settings.yml` change: the 30-year length, the
1985–2014 analysis reference, the 10-model IQR floor and the agreement bands are **module constants** with
names and docstrings (§5); promoting any to config is a later, separate decision.

## 4. Figure contract

`projection_figures.figure_relative_paths(horizons)` stays the single source. Revised grammar:

- `full-period/` — the whole record (independent of horizon).
- `period-<a>-<b>/` — one folder **per horizon**, `<a>-<b>` the horizon's **analysis window** (what the
  figures show), e.g. P0 `mid` 2046–2054 → `period-2036-2065/`. The lab's single folder spanning all horizons
  (`lab:wf2_lab/run.py:92-96`) collides with several horizons and is not adopted. Two horizons with the same
  analysis window raise at parse time, like today's duplicate check (`projection_figures.py:131-136`).
  The horizon *name* appears in captions and in `analysis_record.json`, not in the path.
- No development ids in filenames or on the image (`DEV_IDS` dropped); ids remain only in this design and
  the lab report.

| Id | Path under `plots/` | Count |
|---|---|---|
| F3.1 | `full-period/availability.png` | 1 |
| F3.4 | `full-period/trajectory-{temperature,precipitation}.png` | 2 |
| F3.4b | `full-period/annual-{temperature,precipitation}.png` | 2 |
| F3.2 | `period-<a>-<b>/change-{temperature,precipitation-pct,precipitation-abs}.png` | 3/horizon |
| F3.3 | `period-<a>-<b>/seasonal-cycle-{temperature,precipitation}.png` | 2/horizon |
| F3.5a | `period-<a>-<b>/variability-ratio-{temperature-sd,precipitation-cv}.png` | 2/horizon |
| F3.5c | `period-<a>-<b>/variability-member-ratios.png` | 1/horizon |
| F3.6b | `period-<a>-<b>/change-factor-cloud.png` | 1/horizon |
| F5.1 | `period-<a>-<b>/sign-agreement.png` | 1/horizon |
| (cond.) | `full-period/change-factor-cloud-combined.png` — only with ≥ 2 horizons | 0/1 |

One horizon: 15 figures. *n* horizons: 5 + 10·n (+1). The combined cloud remains conditional as today
(`projection_figures.py:117-127`); the owner dropped it "for one horizon", which this preserves — confirm at G1.

**Captions.** Mirror WF0's existing contract rather than the lab's `figures/captions.json`
(`climate_analysis/diagnostic_outputs.py:82-90`, `diagnostic_render.py:221-261`):
`plots/_engine/figure_captions.json` (machine record: path → caption, horizon, counts),
`plots/figure_captions.md` (human list), and with `captioned_figures: true` copies at
`plots/captioned/<folder>/<name>.png`. Counts appear only in captions and tables (owner ruling, lab
`coverage.py:1-8`). Caption text is ported from `captions_wf2.caption`.

**Tabbed HTML page: not included.** WF0 ships Markdown captions, not HTML; a self-contained HTML page is a
third reporting surface with no consumer in this repo (the web app is separate, `web-app-independence`), and
`report.md` is already WF2's human entry point. `figure_captions.md` lists every figure with its caption.

**Conventions revised for WF2 only** (2026-08-11 rulings, `projection_figures.py:29-46`):

| 2026-08-11 ruling | WF2 after this change |
|---|---|
| caveat via `fig.supxlabel(..., wrap=True)` | no in-figure caveat; caption outside the image |
| cloud annotates each point with its model name | no labels; circles, square axes |
| WF1 page spec (`cartographic_map._publication_rc()`, `series_figure_size`) | WF0 size classes and `STYLE` |
| no titles; `a)`/`b)` panel labels; scenario is the only visual encoding | **kept** |

**Tokens: reuse, no third copy.** WF2 imports `W_*`, `H_*`, `FS_*`, `LW_*`, `MM`, `INK`, `MUTED`, `STYLE`,
`tint`, `ygrid`, `new_fig`, `add_caption`, `plural` from `blueearth_cst.climate_analysis.diagnostic_figures`.
Values match the lab exactly (`diagnostic_figures.py:25-81` vs `lab:wf0_lab/figures.py:36-58`; `new_fig`
bodies identical, `diagnostic_figures.py:253-266` vs `figures.py:196-201`). The scenario palette stays the
toolbox's `projection_plots.SCENARIO_COLORS` (the lab copied it as values, `figures_wf2.py` header), moved
into `projection_figures` when `projection_plots` is retired. Cost: a `projections → climate_analysis`
import. The alternative (extract tokens to `shared/figure_tokens.py`) is in §8.

## 5. Numerical contracts

1. **Aligned change factors byte-identical.** `summary/cmip6_change_factors_{annual,monthly}.csv` before
   vs after, on the fixture/rapid run and on P0. Guaranteed structurally: no kernel root or callee changes
   (`STAGE_B_HASH` equal before/after), 2.05's arithmetic path untouched. The CSVs carry no hash or digest
   columns (P0 header: `model,scenario,member,horizon,variable,statistic,reference_value,absolute_value,
   units,relative_value,relative_units,status,reference_window,horizon_window`).
2. **Analysis window reproduces the lab.** On P0, every `changes.csv` analysis row (annual, seasons, months ×
   `mean`, `std`, `std_detrended`, `cv_detrended`) matches lab `results/changes.csv` (`window_kind ==
   analysis`) within **1e-9 relative or 1e-12 absolute** for values both compute in float64, and every
   downstream table (`model_changes`, `change_summary`, `sign_agreement`, variability, anomalies) matches
   its lab counterpart to the same tolerance; sign/count columns exactly. Rationale: annual/monthly go through
   xarray kernels the lab reconciled at 0.001 only because the CSVs round to 3 dp; unrounded, residual
   differences are summation order. **Assumption:** float differences stay below 1e-9 relative; if not, the
   falsifier reports the max deviation and the tolerance is revisited at G2, never silently widened.
3. **Water year (t2610070255).** 2.05b passes the configured `water_year_start` to the monthly kernel;
   2.05 keeps calling it with the default `"Jan"` (`derive_change_factors.py:225-235`). Consequence: for a
   non-January water year, aligned monthly rows (CSV) and analysis monthly rows (`analysis/changes.csv`)
   use different year conventions. For January (P0, fixture) they coincide. Fixing t2610070255 later changes
   the aligned CSV and the baseline, not the analysis tables. Recorded in `analysis_record.json` `methods`.
4. **Dry-reference guard.** The toolbox flags per statistic by its own reference value (`get_change_monthly_clim_proj`,
   threshold from `min_reference`); the lab per period by the reference mean (`core.py:296-318`). 2.05b uses the
   toolbox rule for annual/monthly (it calls the kernel) and the lab rule for seasons/CV. They differ only
   for a reference mean below 0.1 mm/day, which P0 never reaches (lab `summary.json` `change_table`: 23,800
   rows, all `ok`). Flag for the domain lens.
5. **Constants** (module level, named): `ANALYSIS_LENGTH = 30`, `ANALYSIS_REFERENCE = (1985, 2014)`,
   `MIN_MODELS_IQR = 10`, agreement bands `temp 0.5 °C, precip 5 %, 0.1 mm/day` (`agreement.py:27`). The
   1985–2014 reference is independent of the configured `reference_window` (default template also
   1985–2014; P0 uses 2000–2014) — domain lens to confirm.

## 6. Robustness

| Case | Behaviour |
|---|---|
| Model not in Kuma et al. (2023) table | family `unlisted` in table and figure; institution from the catalog entry (`inputs.institution_from_catalog_entry`); country blank. Never raises. |
| Kuma table data | shipped as `projections/model_families.csv` (source_id, family, institution, country) from Zenodo 7920408 `models.csv`, with citation header. **Unknown:** the record's licence — check before vendoring; fallback: keep only the 13-model mapping in code. |
| Scenario with no resolved member | absent from tables; product per-scenario panels skip it; `analysis_record.json` lists it. |
| Model missing a scenario | reductions use the models present per cell; `sign_agreement` `n_models` reports the count. |
| IQR with < 10 models | `iqr_shown = False`; whiskers and median only (lab `means.ensemble_summary`). |
| Single member per model | F3.5c pools what exists; with < 2 members anywhere it is **unavailable** with reason. |
| Analysis window leaves the series (e.g. horizon 2081–2100 → 2076–2105 beyond 2100, acquisition span `series_identity.py:97-100`) | rows `status = unavailable` with reason; that horizon's figures follow the placeholder rule below. |
| Analysis reference unavailable for a member | member dropped from C3 with reason (the lab raises, `trajectories.py:79-80`; changed). |
| Variable other than precip/temp configured | analysis covers precip and temp only; others recorded unavailable "no analysis method for <var>". |
| Empty inputs for a product | product listed in `analysis_record.json` `unavailable_products` with reason; never drawn blank. |

**Declared-vs-written with unavailable products.** Snakemake needs every declared figure to exist. A product
that is unavailable at run time (data-dependent, unknown at parse time) is written as a figure stating
"unavailable: <reason>" on a blank canvas, and its caption says the same. The parse-time-knowable case
(combined cloud with one horizon) is simply not declared. Alternative — dynamic outputs via a checkpoint — is
rejected in §8. Open for G1.

## 7. Identity and blast radius

- **WF3/WF4 run ids.** `repository_code_inventory` follows static imports from the stage entry points
  (`experiment/content_identity.py:84-130`). No module under `experiment/`, `shared/` or `weathergen/` imports
  `blueearth_cst.projections` (grep, none), and this design edits nothing in `shared/` or
  `climate_analysis/` (it only imports `diagnostic_figures`, which WF3/WF4 never reach — they import only
  `climate_analysis.prepare_climate_data_catalog`). Expected: WF3/WF4 identities unchanged. Falsifier in §9.
- **Stage B cache.** `STAGE_B_HASH` unchanged (additive functions); `REDUCER_HASH` untouched.
- **Baseline manifest.** Covers the two CSVs (byte-identity gate covers them better) and, outside the
  default gate, three figure paths (`dev/scripts/check_baseline.py:313-330`) that this design retires —
  update those entries; `--include-figures` users see the change. Manifest is stale anyway (AGENTS.md).
- **Dry-runs.** `tests/test_cli.py` WF2 dry-runs see one more rule and new paths.
- **Tree inventory.** `tests/test_project_tree_inventory.py:131-134` lists retired paths — updated.
- **Other stale references to fix in the same commits:** `dev/reference/workflows/rule-index.md:881-908`
  (2.05 "renders one figure"; 2.06 "Eight PNGs", already stale), `dev/scripts/console_sample_specs.py:295`
  (pre-R12 path), `report.py:162-166` comment, `projection_figures.py` docstring.

## 8. Alternatives considered

| Choice | Chosen | Alternative | Why not / when it would win |
|---|---|---|---|
| Port shape | Refactor: kernels reused, new modules by concern | Port lab modules as-is (`core.change_table` beside the kernel) | Violates the one-calculator ruling; two windowing implementations would drift. Would win only if the kernel could not express seasons — it can be extended additively. |
| Calculation site | New rule 2.05b | Fold the suite into 2.05 | 2.05 is the cache-guarded terminal of change factors; adding figures-feeding work there re-runs the expensive merge on any plot-table change and mixes the baseline product with exploratory tables. |
| Figure family | Replace | Extend (keep the five, add 15) | Owner reviewed the revised set as the set; carry-overs F3.4b/F3.6b already replace the old overview and cloud; keeping both doubles the same facts under two names. Extend wins only if a consumer reads old paths — none outside this repo (`web-app-independence`). |
| Default | On by default | Opt-in suite key | Replacement makes opt-in mean "no figures"; cost is small (lab: minutes on P0, untimed). Would win if timing on a large ensemble shows a material cost — falsifier in §9. |
| Tokens | Import from `climate_analysis.diagnostic_figures` | Extract to `shared/figure_tokens.py` | Shared extraction edits WF0 code and `shared/`, triggering `test-full` and an identity check, for no behaviour gain now. Wins when a third workflow needs the tokens. |
| Unavailable products | Placeholder figure | Snakemake checkpoint with dynamic outputs | Checkpoints break the single-source static figure list that `rule all`, gather edges and the tree inventory rely on. |
| HTML page | Not included | Port `report_wf2` page | No consumer; third reporting surface. |
| Cloud data | Analysis-window model means | Keep the stage-B merge cloud (aligned, members) | Lab-reviewed F3.6b uses the analysis window and members averaged; drawing it from 2.05 would keep figures in a `derive_` rule. |

## 9. Validation plan

**Pre-change snapshots (before commit 1)**, under `dev/tasks/t2610071652/evidence/` (only the digests and
small files; data copies in the worktree `.tmp/scratchpad/`):

- `cmip6_change_factors_{annual,monthly}.csv` from the rapid run and from P0 (+ sha256).
- Lab `results/*.csv` for P0 at lab `7560e71`.
- `STAGE_B_HASH`, `REDUCER_HASH`, and WF3/WF4 `repository_code_inventory` digests for the rapid config.

| Claim | Check | Falsifier |
|---|---|---|
| Aligned CSVs byte-identical | sha256 after commit-final WF2 run on rapid and P0 | any digest differs |
| Stage B not invalidated by new functions | print `STAGE_B_HASH` before/after commit 1 | values differ |
| Analysis tables reproduce lab | `tests/test_projection_analysis_parity.py` (local, skips without P0, skip reason printed) comparing to the snapshot | any value outside §5.2 tolerance; any count/sign mismatch |
| Window rule | unit tests: Jan and Oct water years, horizon past 2100 → unavailable, `analysis_window(2046,2054) == (2036,2065)` | wrong bounds |
| Unlisted model degrades | synthetic composition with `XYZ/FOO-1` | raise, or missing row |
| Every declared output written, every written declared | `test_projection_figures.py` extended; WF2 run then compare `plots/` and `analysis/` listings to declarations | extra or missing file |
| Empty product → unavailable | constant-valued synthetic run (lab precedent) | blank figure without reason |
| WF3/WF4 identity unchanged | recompute inventory digests | differ |
| Acceptable run time | benchmark row of 2.05b and 2.06 on P0 in `wf2_benchmarks.md` | > 5 min combined (assumed budget; G1 to confirm) |
| Figures match lab | render on P0, publish PNGs as an Artifact, owner visual check (figure gate) | owner rejects |

Gates per AGENTS ladder: focused tests per commit; `pytest tests/test_cli.py` on commits touching the
Snakefile; `pixi run lint`, `format-check`; `test-fast` before merge; `test-full` not required (no `shared/`
or WF3 `script:` change) unless §7 falsifier fires; `test-e2e` WF2 leg before merge (rule behaviour changes).

## 10. Commit plan

| # | Lands | Focused checks | Est. |
|---|---|---|---|
| 0 | Evidence snapshots (no code) | digests recorded | 30 min |
| 1 | `get_change_climate_proj`: `analysis_window`, `analysis_slice`, `get_change_seasonal_clim_proj`, `detrended_std` + unit tests; explicit `import hydromt` in `derive_change_factors` | new unit tests; `test_get_change_climate_proj*.py`; `STAGE_B_HASH` equal | 2 h |
| 2 | `projection_coverage.py` + `model_families.csv` (licence checked) + tests | unit tests incl. unlisted model | 1.5 h |
| 3 | `projection_analysis.py`, `projection_trajectories.py` (tables) + tests | unit + known-answer tests (√2 ratio, hand medians) | 3 h |
| 4 | Rule 2.05b + `prepare_projection_analysis.py`; `analysis_record.json`; rule-index entry | `test_cli.py`; rapid WF2 run; parity test on P0 | 2.5 h |
| 5 | Artists + captions modules (lab style, WF0 tokens); `figure_relative_paths` revised; 2.06 repointed; 2.05 cloud removed; gather edges; config key + template; retired code deleted; tree inventory, `check_baseline` entries, console spec, docs | `test_projection_figures.py`, `test_project_tree_inventory.py`, `test_cli.py`, lint; render P0 and publish PNG Artifact | 4 h |
| 6 | Batch gates | byte-identity, identity digests, `test-fast`, `test-e2e` | 1.5 h |

## 11. Tree and user-facing change inventory

**Repository** (`+` added, `~` changed, `-` removed):

```
blueearth_cst/projections/
~ get_change_climate_proj.py        analysis window + seasonal/detrended functions (additive)
~ derive_change_factors.py          no cloud; explicit hydromt import
~ get_change_climate_proj_summary.py   plot_change_summary removed
~ projection_figures.py             new path grammar; palette moved here
~ plot_proj_timeseries.py           thin renderer driver over analysis tables
- projection_plots.py               retired (draw_* replaced)
+ prepare_projection_analysis.py    script: of rule 2.05b
+ projection_analysis.py            change table, reductions, agreement, C2, C4
+ projection_trajectories.py        C3 anomalies and range
+ projection_coverage.py            C0 coverage and availability
+ projection_suite_figures.py       lab-style artists
+ projection_captions.py            caption text
+ model_families.csv                Kuma et al. (2023) families
~ analyze_projections.smk           rule 2.05b; 2.05/2.06 outputs; gather edges; captioned_figures
~ config/templates/project_config.analyze_projections.template.yml   captioned_figures comment
~ tests/test_projection_figures.py, test_project_tree_inventory.py; + tests/test_projection_analysis*.py
~ dev/reference/workflows/rule-index.md, dev/scripts/check_baseline.py, dev/scripts/console_sample_specs.py
```

**Generated** under `<project>/data/climate/projections/<ensemble>/`:

```
summary/…                            unchanged (CSV bytes identical)
report.md                            ~ figure list
+ analysis/*.csv, analysis/analysis_record.json
plots/
- overview/{annual-*,change-factor-cloud*}.png
- windows/<name>-<start>-<end>/monthly-change-factors.png
+ full-period/{availability,trajectory-*,annual-*}.png  [+ change-factor-cloud-combined.png if ≥2 horizons]
+ period-<a>-<b>/{change-*,seasonal-cycle-*,variability-*,change-factor-cloud,sign-agreement}.png
+ figure_captions.md, _engine/figure_captions.json
+ captioned/<folder>/*.png           only with captioned_figures: true
```

| Change | Current | Proposed | Affected / migration |
|---|---|---|---|
| WF2 figure paths | `plots/overview/…`, `plots/windows/<h>/…` | `plots/full-period/…`, `plots/period-<a>-<b>/…` | readers of old paths; old files remain until `--delete-all-output` or manual removal — note in docs |
| Figure set | 5 (+1) | 15 per one horizon (+1) | users; docs figure list |
| New tables | — | `analysis/*.csv` | addition |
| Captions | in-figure caveat | `figure_captions.md`/`.json`, optional captioned copies | users |
| Config | — | optional `captioned_figures` (default false) | none; existing configs valid |
| Commands | unchanged | unchanged | — |
| Change-factor CSVs | — | unchanged | CST-API unaffected |

## 12. Assumptions, unknowns, open questions for G1

- **Open G1-1:** placeholder figure vs other handling for runtime-unavailable products (§6).
- **Open G1-2:** combined cloud with ≥ 2 horizons kept conditional (§4).
- **Open G1-3:** folder years = analysis window, horizon name only in captions (§4).
- **Open G1-4:** artist module name (`projection_suite_figures.py`).
- **Unknown:** Kuma Zenodo record licence (§6). P0 run time (intake: low confidence). Float agreement at
  1e-9 (§5.2).
- **Domain lens:** fixed 1985–2014 analysis reference independent of `reference_window`; mixed dry-guard
  rules (§5.4); SD ratio for temperature (intake evidence row).
