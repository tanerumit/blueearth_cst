# WF2 suite integration — design v4

> **Window contract superseded (2026-10-12).** The owner now requires diagnostics to use the configured
> reference/future calendar bounds, retaining only complete water years inside them. Recentring, extension,
> and reference fallback described below no longer apply. The seasonal minimum remains 27 observations.
> Current behavior: `docs/site/toolbox-reference/workflow-analyze-projections.qmd`. The original decisions
> and verification below are retained as historical evidence.


- **Status:** revised draft (design-review loop `wf2-suite-integration`, revision r3; G1 approved
  2026-10-07, G2 pending)
- **Genre:** decision record, milestone style (goal, what changes, alternatives, commit plan)
- **Task:** `t2610071652` · lane `feat/wf2-cmip6-improvements` (session-1) · **Date:** 2026-10-07
- **Lifecycle:** `maintained-current` until implementation lands; revision log append-only
- **Revisions:** v1 2026-10-07, first draft from `intake.md`; v2 2026-10-07, G1 rulings and internal panel
  (`internal-review-domain.md`, `internal-review-risk.md`) — see § 13; v3 2026-10-07, external round 1 and
  full-panel extension (`external-review-r1.md`, `internal-review-architecture.md`,
  `internal-review-repo-fit.md`) — see § 14

Paths without a root are relative to the session-1 worktree. `lab:` is `C:\Users\taner\workspace\wf0-lab`.
`P0` is the development ensemble run at `C:/data/cmip6/gabon-ntoum-dev-ensemble` (13 models, 25 members,
4 SSPs, one horizon `mid` 2046–2054, configured reference 2000–2014, January water year: lab `summary.json`
`settings`). "WY" is a water year, labelled — as `get_change_climate_proj.hydrological_year_bounds` does —
by the calendar year in which it **starts** (January start: WY = calendar year).

## Contents

1. [Overview, goal, scope](#1-overview-goal-scope)
2. [Module boundaries](#2-module-boundaries)
3. [Snakemake rules and config](#3-snakemake-rules-and-config)
4. [Figure contract](#4-figure-contract)
5. [Numerical contracts](#5-numerical-contracts)
6. [Robustness and availability](#6-robustness-and-availability)
7. [Identity and blast radius](#7-identity-and-blast-radius)
8. [Alternatives considered](#8-alternatives-considered)
9. [Validation plan](#9-validation-plan)
10. [Commit plan](#10-commit-plan)
11. [Tree and user-facing change inventory](#11-tree-and-user-facing-change-inventory)
12. [Assumptions and unknowns](#12-assumptions-and-unknowns)
13. [Revision log (v1 → v2)](#13-revision-log-v1--v2)
14. [Revision log (v2 → v3)](#14-revision-log-v2--v3)
15. [Revision log (v3 → v4)](#15-revision-log-v3--v4)

## 1. Overview, goal, scope

**Proposal.** Add one WF2 rule that turns the per-member basin series into **analysis tables** on a
30-water-year analysis window, and repoint the existing plot rule so it draws the owner-accepted figure set
from those tables. Change-factor arithmetic stays where it is: the analysis window calls the same
`get_change_{annual,monthly}_clim_proj` kernels on a different time slice, and only the genuinely new
arithmetic (seasons, detrended SD/CV, analysis-window placement) is added beside them in
`get_change_climate_proj.py`, without editing any existing function.

```
scalar/*.nc ─┬─► 2.05 derive_change_factors ──► summary/*_change_factors_{annual,monthly}.csv  (unchanged bytes)
             │          (no figure, no figure list)  composition.csv, provenance.json, report.md
             └─► 2.05b prepare_projection_analysis ──► analysis/*.csv, analysis/analysis_record.json
                                   │      (parallel to 2.05; does not read its outputs;
                                   │       decides final product availability from the data, § 6.1)
                                   ▼
                 2.06 plot_climate_projections ──► directory(plots/full-period/), directory(plots/period-<a>-<b>/),
                                                   plots/figure_captions.md, plots/_engine/figure_captions.json
                                                   (the JSON is the manifest of the PNGs actually written)
```

**Settled framing (owner rulings 2026-10-07, intake table, and G1 rulings in `status.md`).**

- *Analysis + figures* move into `blueearth_cst/projections`; **one calculator** — the analysis window
  extends `get_change_climate_proj`, it does not run beside it.
- *Lab style* for WF2 figures (captions outside the image, scenario key top-right, no model labels on the
  cloud, WF0 size classes). Revises the 2026-08-11 toolbox rulings for WF2 only.
- G1: analysis windows and their relation to the configured windows (§ 5.5), far-horizon shift (§ 5.6),
  no-change sampling band on the variability ratios (§ 5.7), equal-model weights for pooled member ratios
  (§ 5.8), family counts and small-change marker on agreement (§ 5.9), provisional family from institution
  (§ 6), no placeholder figures — unavailable products listed with reason (§ 6.1), combined cloud only
  with ≥ 2 horizons (§ 4), folders named by analysis-window years (§ 4), Kuma table vendored only if its
  licence permits (§ 6).
- Design doc + review loop, then commit-to-commit implementation on this lane.

**What the user gets.** The same change-factor CSVs (byte-identical), a new `analysis/` table folder with a
machine record of windows, methods and unavailable products, and up to 15 figures for one horizon (§ 4) in
place of today's five, with recoverable captions.

**Non-goals** (intake § Non-goals): dropped figures F3.5b, F3.6, F3.7, F3.8 as figures; daily extremes,
drought, warming levels, emergence, maps, weighting, partitioning; CST-API/frontend; fixing t2610070255;
WF0/WF1 figure conventions. CMIP6 stays a plausibility overlay (AGENTS.md § Background): nothing written here
is read by WF3/WF4.

## 2. Module boundaries

Owner per calculation. "Lab source" is the function whose behaviour is ported (not copied wholesale;
`lab:docs/wf2-integration-notes.md` § Candidates says the same).

| Calculation | Toolbox owner (new = N, extended = E) | Lab source |
|---|---|---|
| Analysis windows (future and reference), far-end shift, near-end join flag (§ 5.5–5.6) | E `get_change_climate_proj.analysis_windows` (pure, parse-time callable) | `core.analysis_window`, `core.window_bounds` (`lab:wf2_lab/core.py:111-183`) |
| Slicing a member's (joined) series to an analysis window | E `get_change_climate_proj.analysis_slice` | `core.window_bounds`, `trajectories.py:76` (join) |
| Annual + monthly mean/std on the analysis window | **existing** `get_change_annual_clim_proj`, `get_change_monthly_clim_proj`, called on the analysis slice | reconciled equivalent in `core.change_rows` |
| Seasonal values (DJF/MAM/JJA/SON), month-length weighted, season-year contract § 5.11; detrended SD (OLS in window, ddof 0); precip CV of period integrals | E `get_change_seasonal_clim_proj`, `detrended_std` | `core.period_values`, `core.detrended_std`, `core.statistics` (`core.py:203-255`) |
| Analysis dry-reference rule (one rule for all analysis rows, § 5.4) | N `projection_analysis.apply_dry_reference` (post-process) | `core.py:295-321` |
| Long per-member analysis table (status/reason per row) | N `projections/projection_analysis.py` `analysis_change_table` | `core.change_table` (shape and status vocabulary only) |
| Member→model reduction, ensemble summary with IQR floor (10 models) | N `projection_analysis.model_changes`, `ensemble_summary` | `means.py:93-133` |
| Sign agreement: model `k/n`, family `k_fam/n_fam`, small-change marker (§ 5.9) | N `projection_analysis.sign_agreement` | `agreement.py:44-69` (+ G1 additions) |
| C2 climatology + monthly change summaries | N `projection_analysis.climatology`, `monthly_change` | `seasonal.py:35-71` |
| C3 member anomalies vs own analysis-reference mean; per-model and ensemble range | N `projections/projection_trajectories.py` | `trajectories.py:64-141` |
| C4 variability: degenerate statuses (§ 5.12), member ratios, per-model geometric mean, equal-model pooled summary, per-panel no-change band (§ 5.7) | N `projection_analysis.member_ratios`, `model_ratios`, `ratio_summary`, `null_ratio_band` | `variability.py:50-100` (+ G1 weights, band) |
| C0 coverage / availability with Kuma et al. (2023) family (listed / provisional / own), institution, country | N `projections/projection_coverage.py`; data `projections/model_families.csv` (licence-gated, § 6) | `coverage.py:63-176` |
| Parse-time folder set: one folder per distinct analysis window (§ 4, § 6.1) | N `projection_figures.suite_folders` | `run.period_folder` |
| Run-time product availability from the data (§ 6.1) | N `projection_analysis.product_availability` (called by 2.05b only) | — (new) |
| Series identity assertion and calendar-agreement check, shared by 2.05 and 2.05b | N `projections/series_checks.py` (moved from `derive_change_factors.py:111-265`, arch-6) | — |
| Figure artists (lab style) | N `projections/projection_suite_figures.py` | `figures_wf2.py` (reference implementation) |
| Captions | N `projections/projection_captions.py` | `captions_wf2.caption` (+ G1 wording) |
| Figure file names inside the folders | N `projection_figures.SUITE_PRODUCTS` (product id → folder kind, file names) | `figures_wf2.py` names |
| Calendar month lengths | **existing** `calendar_weights` | lab mirrors it — not ported |

Rules for the split:

- **Additive only (stage-B hash discipline).** New functions in `get_change_climate_proj.py` may **call** a
  `STAGE_B_KERNEL` root (`analyze_projections.smk:512-522`; e.g. `hydrological_year_bounds`) but must not
  **edit** any root, any callee of a root, or any module constant a root references. `kernel_hash` follows
  callees and referenced constants (`series_identity.py:369-399`), so this keeps `STAGE_B_HASH` and rule
  2.05's inputs unchanged; new functions are not called by any root.
- The C3 smoothed fan is not drawn (report `lab:docs/wf2-suite-report.md:265-267`) and is **not ported**.
- Aligned-window rows are **not** recomputed in the new tables: they live in `summary/*_change_factors_*.csv`.
  Figures use the analysis window only; captions and the record name both window pairs (§ 5.5).

**Not ported, and their tables not written:** F3.5b (`c4_member_spread`), F3.6 scaling (`c6_scaling`),
F3.7/F3.8 sensitivity (`c6_sensitivity*`), paired contrasts (`c5_paired_contrasts`, `c5_contrast_summary`),
`c4_paired`, the C3 smoothed fan, the lab reconciliation table (replaced by the parity test, § 9), the tabbed
HTML page (§ 4). Adding any later is a separate, opt-in decision.

## 3. Snakemake rules and config

**New rule 2.05b `prepare_projection_analysis`** (naming.md §8b: `prepare_` = compute something a later rule
needs; §9: letter suffix, no renumbering).

| Field | Value |
|---|---|
| input | the same explicit `series_nc` list as 2.05 (historical + scenario per resolved point); `_STAGE_B_STAMP`. **Not** `composition.csv` or any other 2.05 output |
| params | `horizons`, `water_year_start`, `reference_window`, `points` (the `POINTS` records 2.05 receives), `variable_spec`, `min_reference`, `windows` (from `analysis_windows`, § 5.5–5.6), `table_names` |
| output | `analysis/` tables, declared individually: `coverage.csv`, `availability.csv` (one row per product × folder: `available`, `reason`), `changes.csv`, `model_changes.csv`, `change_summary.csv`, `sign_agreement.csv`, `climatology.csv`, `climatology_summary.csv`, `monthly_change_summary.csv`, `member_anomalies.csv`, `trajectory_range.csv`, `variability_member_ratios.csv`, `variability_model_ratios.csv`, `variability_summary.csv`, `analysis_record.json` |
| script | `blueearth_cst/projections/prepare_projection_analysis.py` |
| threads / resources | 1 / `mem_mb = 1024` |
| log / benchmark | `PREPARE_PROJECTION_ANALYSIS = RULES.logged("2.05b", "prepare_projection_analysis", summary=...)` |

Tables are always written (a table for an unavailable product holds its header and zero rows; the record
says why). Figures are not (§ 6.1). **Table key (arch-3):** every per-window table is keyed by
`window_id` (`<a>-<b>`, the analysis window's WY labels), never by horizon; each distinct window is computed
once. `analysis_record.json` carries `windows: [{window_id, horizons: [...], configured: {...per horizon},
requested, used, shifted, joined}]`, so two horizons sharing a window produce one set of rows and one folder.
`analysis_record.json` also holds: both window pairs per horizon (§ 5.5), reference-choice rule, methods (dry
rule, season-year contract, detrending, degenerate-variability rules, null-band definitions per panel,
weights, agreement bands as display heuristics), members per model, family source per model, and the
**final product availability** with reasons (§ 6.1), mirrored in `availability.csv`. 2.05b derives coverage
from `points` (the same `POINTS` records 2.05 turns into `composition.csv`), so it does not depend on 2.05 at
all. It reads the series with the identity assertion and calendar check that 2.05 uses; commit 1 moves both
helpers from the `script:` module `derive_change_factors.py:111-265` into a new library module
`projections/series_checks.py` and repoints 2.05 to them (arch-6). A new module, not `series_identity`, so
the move touches no module that `kernel_hash` or the stage-B / reducer kernels read; commit 1 records
`STAGE_B_HASH` and `REDUCER_HASH` before and after as the falsifier.

**Script-body convention (fit-6).** The two `script:` modules (`prepare_projection_analysis.py`, rewritten
`plot_proj_timeseries.py`) carry the repository's NOTE header and **no** `from __future__ import annotations`
(Snakemake prepends a preamble; `derive_change_factors.py:28-30`). Library modules may keep the import, as
`projection_figures.py:46` does.

**Console surface (fit-8).** 2.05b and 2.06 write summary rows through `log_row`: windows used (with shift or
join), product counts available / not produced, members unavailable. Data-sized lists (unavailable products,
members, shifted windows) are capped with `snake_utils.listed` (`snake_utils.py:939`) and the row points to
`analysis_record.json`, which holds the full list (no silent cap). Counts use `run_log_core.plural`
(`run_log_core.py:1840`); WF0's `diagnostic_figures.plural` is used only inside caption text (fit-7).

**Rule 2.05 `derive_change_factors`** — arithmetic unchanged. Loses `stats_change_plt`, the
`plot_change_summary` call (`derive_change_factors.py:535`) **and the `figure_names` param**
(`analyze_projections.smk:1197`): `report.md` points to `plots/figure_captions.md` (owned by 2.06) instead of
listing figures, so no future figure change re-runs the change-factor merge (risk-5). `combine_changes` stays
imported from `get_change_climate_proj_summary`, which keeps the hydromt `.raster` accessor registration
intact (`get_change_climate_proj.py:8-17`); an explicit `import hydromt` is added in
`derive_change_factors.py` **in commit 5b**, which edits that file anyway (fit-9). 2.05 re-runs on each commit
that edits its script (Snakemake's `code` trigger): commit 1 (helpers moved to `series_identity`) and commit
5b. Its CSVs must come out byte-identical each time (§ 5.1).

**Rule 2.06 `plot_climate_projections`** — keeps its name and number; becomes a pure renderer of
`analysis/*.csv` and `analysis_record.json`. Outputs (§ 6.1): `directory("plots/full-period")`, one
`directory("plots/period-<a>-<b>")` per entry of `suite_folders(...)`, `plots/figure_captions.md`,
`plots/_engine/figure_captions.json`, and `directory("plots/captioned")` when `captioned_figures` is true. It
draws exactly the products `availability.csv` marks available. Script stays `plot_proj_timeseries.py`,
rewritten as a thin driver over the new artist module. It no longer reads `scalar/*.nc` (figures render
tables, `analyze_projections.smk:1258-1262`). Figures are written with `snake_utils.save_figure`
(`snake_utils.py:1025`, console-logged) at `dpi=600, facecolor="white"`, the values WF0 passes
(`diagnostic_render.py:220-225`), so WF0 and WF2 PNGs share resolution (fit-7).

**Gather edges and terminal targets.** `gather_logs`/`gather_benchmarks` (`analyze_projections.smk:1324-1361`)
name `CHANGE_FACTOR_CLOUD_PLOT` and `ANNUAL_PRECIPITATION_PLOT`. Commit 4 adds `analysis/analysis_record.json`
(2.05b's terminal), so 2.05b is scheduled and its log merged. Commit 5a replaces `ANNUAL_PRECIPITATION_PLOT`
(2.06's old output) by `plots/_engine/figure_captions.json` (2.06's new terminal); `CHANGE_FACTOR_CLOUD_PLOT`
(2.05's output) stays until commit 5b retires it in favour of the annual CSV (arch-1, § 10).
`WF2_TARGETS` (`analyze_projections.smk:883-903`, which feeds `rule all` and `--delete-all-output`) names
every analysis table and `analysis_record.json` from commit 4, and the 2.06 directories, `figure_captions.md`
and `_engine/figure_captions.json` from commit 5a, replacing the `figure_*` entries built from
`WF2_FIGURE_PATHS` (fit-5).

**Retired figures:** `overview/annual-{precipitation,temperature}.png`, `overview/change-factor-cloud.png`,
`overview/change-factor-cloud-combined.png`, `windows/<h>/monthly-change-factors.png`. Content survives as
F3.4b, F3.6b and F3.3; aligned monthly numbers remain in the CSV. Retired code: `projection_plots.draw_*`,
`get_change_climate_proj_summary.plot_change_summary`, `plot_proj_timeseries.annual_series` /
`monthly_change_from_table` once no caller remains, `projection_figures.figure_relative_paths`,
`CLOUD_FACETED_PATH` and the Snakefile constants built from them (`analyze_projections.smk:352-367`), and
their tests: `tests/test_projection_plots.py` (deleted), `tests/test_projection_figures.py:67-126`
(replaced by `suite_folders` tests) and `tests/test_get_change_climate_proj_summary.py:127-162` (the cloud
test; its derived-combinations property moves to a `model_changes` / F3.6b artist test) (fit-2).

**Config.** The suite is **on by default** (it replaces the figure set). One optional workflow-file key,
mirroring WF0's `diagnostics.captioned_figures` (`climate_analysis/diagnostic_settings.py:12`):

```yaml
# project_config.analyze_projections.template.yml, REPORTING section
#captioned_figures: false    # also write plots/captioned/<folder>/<name>.png with the caption below the image
```

Read with `get_config(my_cfg, "captioned_figures", False, optional=True)`, type-checked as bool like
`subbasin_figures` (`analyze_climate.smk:309-311`). WF2-only, so it lives in the workflow file. No
`advanced_settings.yml` change: the 30-year length, the 1985–2014 fallback reference, the IQR floor, the null
band level, simulation count and seed, the season completeness minimum and the agreement bands are **named
module constants** (§ 5.10).

## 4. Figure contract

`projection_figures.suite_folders(horizons, water_year_start, reference_window)` is the single parse-time
source of the **folder set**; it calls `analysis_windows` (§ 5.5–5.6), the same function 2.05b receives the
result of, so folder names and computed windows cannot disagree. Which files appear inside a folder is decided
at run time by 2.05b (§ 6.1); `SUITE_PRODUCTS` fixes the file names a product may take. It replaces
`figure_relative_paths`, retired in commit 5b with its callers (§ 3, § 10).

- `full-period/` — the whole record (independent of horizon).
- `period-<a>-<b>/` — one folder per **distinct analysis window**, `<a>-<b>` its first and last WY label,
  e.g. P0 `mid` 2046–2054 → `period-2036-2065/`. Horizon names appear in captions and in the record, not in
  the path. **Two horizons resolving to the same analysis window** (for example 2071–2090 and 2081–2100, both
  shifted to 2071–2100) share one folder; its captions name both horizons and their configured windows. This
  replaces v1's parse-time refusal (`projection_figures.py:131-136` keeps refusing duplicate *configured*
  windows only), so no valid config is rejected.
- No development ids in filenames or on the image (`DEV_IDS` dropped).

| Id | Path under `plots/` | Count | Available when (decided by 2.05b from the data, § 6.1) |
|---|---|---|---|
| F3.1 | `full-period/availability.png` | 1 | ≥ 1 resolved member |
| F3.4 | `full-period/trajectory-{temperature,precipitation}.png` | 2 | per variable: ≥ 1 model with a member valid on the analysis reference |
| F3.4b | `full-period/annual-{temperature,precipitation}.png` | 2 | per variable: ≥ 1 member with a finite annual value |
| F3.2 | `period-<a>-<b>/change-{temperature,precipitation-pct,precipitation-abs}.png` | 3/window | per panel: ≥ 1 model with a mean-change-eligible row of that statistic (§ 5.12) |
| F3.3 | `period-<a>-<b>/seasonal-cycle-{temperature,precipitation}.png` | 2/window | per variable: ≥ 1 model with complete monthly climatologies |
| F3.5a | `period-<a>-<b>/variability-ratio-{temperature-sd,precipitation-cv}.png` | 2/window | per panel: ≥ 1 model with a variability-eligible ratio (§ 5.12) |
| F3.5c | `period-<a>-<b>/variability-member-ratios.png` | 1/window | ≥ 1 model with ≥ 2 variability-eligible member ratios (§ 5.12) |
| F3.6b | `period-<a>-<b>/change-factor-cloud.png` | 1/window | ≥ 1 model with both a temperature and a precipitation mean-change-eligible change (paired point, § 5.12) |
| F5.1 | `period-<a>-<b>/sign-agreement.png` | 1/window | ≥ 2 models with mean-change-eligible changes in some scenario (§ 5.12) |
| — | `full-period/change-factor-cloud-combined.png` | 0/1 | ≥ 2 distinct analysis windows with F3.6b available (G1) |

Counts are evaluated per scenario; a product is drawn when any scenario qualifies. All available: one window
15 figures; *n* windows 5 + 10·n + [n ≥ 2] (arch-4). Unavailable products are **not drawn**; they are listed
with reason in `availability.csv`, `analysis_record.json` and under "Not produced" in `figure_captions.md`
(G1: no placeholder figures).

**Captions.** Mirror WF0's contract (`climate_analysis/diagnostic_outputs.py:82-90`,
`diagnostic_render.py:221-261`): `plots/_engine/figure_captions.json` (path → caption, horizon(s), counts),
`plots/figure_captions.md` (human list plus "Not produced"), and with `captioned_figures: true` copies at
`plots/captioned/<folder>/<name>.png`. Counts appear only in captions and tables. Caption text is ported from
`captions_wf2.caption` with these obligatory additions:

| Figure(s) | Caption must state |
|---|---|
| every `period-*` figure | analysis future and reference windows; configured (overlay) windows; "the change-factor CSV uses the configured windows"; any far-end shift (requested → used) and any historical+scenario join (dom-1, dom-2, dom-10) |
| F3.2, F3.5a, F3.6b, F3.4 | "ensemble spread across N models (equal model weight), not a confidence interval; models from one code family count separately" (dom-9) |
| F3.4 | "range across N models of annual anomalies (each the mean of its members); includes year-to-year variability, so it is wider than the spread of the forced response" (dom-8) |
| F3.5a, F3.5c | the band's statistic, sampling unit and null model (§ 5.7 table): "90 % range of this ratio expected from sampling alone if variability did not change, assuming year-to-year white noise; autocorrelation widens it"; no "indistinguishable" inference; on F3.5a, the shaded band is the single-member band and each model marker is filled when outside its own m-member band; the pooled quantiles on F3.5c are ensemble spread and carry no band; overlapping windows named when present; F3.5c weights each eligible member 1/eligible-members-of-its-model; excluded degenerate ratios counted (dom-3, dom-4, ext1-1, ext1-3) |
| F5.1 | "sign agreement among models — a count, not a likelihood statement"; family counts; small-change marker and its band values as display heuristics (dom-6, dom-12) |
| F3.1 | which families are provisional (inferred from institution) or own-family (dom-11) |

**Tabbed HTML page: not included.** WF0 ships Markdown captions; a self-contained HTML page is a third
reporting surface with no consumer in this repo (`web-app-independence`); `report.md` links
`figure_captions.md`.

**Conventions revised for WF2 only** (2026-08-11 rulings, `projection_figures.py:29-46`):

| 2026-08-11 ruling | WF2 after this change |
|---|---|
| caveat via `fig.supxlabel(..., wrap=True)` | no in-figure caveat; caption outside the image |
| cloud annotates each point with its model name | no labels; circles, square axes |
| WF1 page spec (`cartographic_map._publication_rc()`, `series_figure_size`) | WF0 size classes and `STYLE` |
| no titles; `a)`/`b)` panel labels; scenario is the only visual encoding | **kept** |

**Tokens: reuse, no third copy.** WF2 imports `W_*`, `H_*`, `FS_*`, `LW_*`, `MM`, `INK`, `MUTED`, `STYLE`,
`tint`, `ygrid`, `new_fig`, `add_caption`, `plural` from `blueearth_cst.climate_analysis.diagnostic_figures`
(values match the lab: `diagnostic_figures.py:25-81` vs `lab:wf0_lab/figures.py:36-58`); WF0's `plural` is
used only in caption text, console rows use `run_log_core.plural` (§ 3). The scenario palette
`projection_plots.SCENARIO_COLORS` moves into `projection_figures`. The `projections → climate_analysis`
dependency is recorded in `rule-index.md` under 2.06, and `tests/test_projection_figures.py` gains a render
smoke test (one synthetic figure per artist), so a WF0 token edit that breaks WF2 fails a test (risk-8).
Alternative (extract to `shared/figure_tokens.py`) in § 8.

## 5. Numerical contracts

1. **Aligned change factors byte-identical.** `summary/cmip6_change_factors_{annual,monthly}.csv` before vs
   after, on rapid and on P0, plus a synthetic dry-reference case (§ 5.4) because neither real run has dry
   cells. Guaranteed structurally: no kernel root, callee or referenced constant changes (`STAGE_B_HASH`
   equal), 2.05's arithmetic path untouched. The CSVs carry no hash columns.
2. **Lab parity** for the tables whose method is unchanged — scope pinned in § 9.1 — within **1e-9 relative
   or 1e-12 absolute**; status, sign and count columns exactly. If float differences exceed it, the test
   reports the max deviation and the tolerance is revisited at G2, never silently widened.
3. **Water year (t2610070255).** 2.05b passes the configured `water_year_start` to the monthly kernel; 2.05
   keeps calling it without it (`derive_change_factors.py:250-257`). For a non-January water year, aligned
   monthly rows and analysis monthly rows use different year conventions; for January (P0, rapid) they
   coincide. Fixing t2610070255 later changes the aligned CSV and the baseline, not the analysis tables.
   Recorded in `analysis_record.json` `methods`.
4. **Dry-reference rule (dom-5, risk-2; conflict settled here).** The kernel flags each statistic by its
   **own** reference value (`get_change_climate_proj.py:249-251`, `flagged = hist_stat < threshold`); the lab
   flags every statistic of a period by the period's reference **mean** (`lab:wf2_lab/core.py:302-321`).
   v1's claim that they differ only below a 0.1 mm/day mean was false: they also differ where the reference
   mean is ≥ threshold but the reference SD is below it (a reliably wet month), where the kernel nulls the
   std % change and the lab keeps it.

   **Governing rule for all analysis rows: per period, keyed on the reference mean** (dom-5), with CV also
   undefined when the future mean is below threshold (lab rule). Reasons: (a) the threshold
   (`min_reference`, a precipitation *rate*) is a dryness criterion; comparing it with an SD mixes meanings
   and makes the flag depend on interannual variability rather than dryness; (b) CV rows, which have no
   kernel counterpart, must key on the mean anyway (CV is undefined as the mean approaches zero whatever the
   SD), so only the mean-keyed rule applies uniformly to annual, monthly, seasonal and CV rows; (c) one rule
   per period keeps `n_models` in agreement and summaries comparable across periods; (d) it is the rule the
   lab tables were reviewed with.

   **Mechanism (risk-2's constraint met):** the kernel is **not edited**. 2.05b calls it on the analysis
   slice, then `apply_dry_reference` re-derives every analysis row's flag from the period's reference mean
   (the kernel's `mean` reference companion, or the seasonal function's) and sets status `dry` (absolute
   change kept, relative dropped) accordingly, recomputing a std % change the kernel dropped only on SD
   grounds from the reference and future values it already returned. The aligned CSV keeps the kernel's
   per-statistic rule, documented in the record and in `rule-index.md`. risk-2's alternative (kernel rule
   everywhere) is not adopted: it cannot be applied to CV rows and keeps the meaning mismatch above. Test: a
   synthetic member whose month has reference mean 0.5 mm/day and reference SD 0.05 mm/day → analysis `std`
   row `ok` with a relative value; aligned CSV row flagged and **byte-identical** before/after the change; a
   month with mean 0.05 → both flagged.
5. **Analysis windows and relation to the overlay (dom-1).** Future window: 30 complete WY centred on the
   configured horizon (`c = floor((a+b)/2)`, WY `c-14 .. c+15`), subject to § 5.6. Reference window: the
   **configured `reference_window`** when it spans ≥ 30 complete WY (its last 30 WY are used), otherwise
   the constant `ANALYSIS_REFERENCE = 1985–2014`. Both pairs (aligned = configured, analysis = used) are in
   `analysis_record.json` per horizon and in every `period-*` caption, with "analysis-window changes; the
   overlay CSV uses <ref>/<horizon>". P0 (configured reference 2000–2014, 15 WY) uses 1985–2014; the default
   template (1985–2014, 30 WY) uses its configured reference.
6. **Window placement at data ends (dom-2, dom-10, risk-3).** Computed **at parse time** by
   `analysis_windows(horizons, water_year_start, reference_window)` from `ACQUISITION_WINDOWS`
   (`series_identity.py:97-100`: historical 1950-01-01–2014-12-31, scenario 2015-01-01–2100-12-31), using the
   WY convention of the root `hydrological_year_bounds` (called, never edited). Shared by
   `suite_folders` (parse time) and 2.05b (as its `windows` param).
   - *Far end:* if the centred window extends past the last complete WY of the scenario span, it is shifted
     earlier to end at that WY, keeping 30 WY. January: 2081–2100 → 2071–2100. October start: the last
     complete WY is WY 2099 (Oct 2099–Sep 2100), so the window is WY 2070–2099, folder `period-2070-2099`,
     caption "Oct 2070 – Sep 2100". Requested and used windows and `shifted: true` are recorded and
     captioned. Unavailable only if fewer than 30 complete WY exist in the combined span.
   - *Near end:* a future window starting before the scenario span (e.g. horizon 2015–2030 → 2008–2037) is
     **joined**: per member, the historical run of the same model and member id precedes the scenario run,
     after the calendar-agreement check 2.05 already applies (`derive_change_factors.py:199-216` today, moved
     to `series_checks` in commit 1 and called by both rules). A member without its historical run is
     unavailable for that window (recorded). Recorded as `joined: true` and captioned. A window that would
     start before 1950 shifts later symmetrically.
   - *Per-member data ends:* the window is never shifted per member. A member whose series does not cover the
     parse-time window (e.g. a run ending 2099, or a 360-day run ending 2099-12-30) is unavailable for that
     window with reason, found **at run time** by 2.05b; folder names and captions therefore always match the
     computed window. If this leaves a product without data it is "not produced", never an error (§ 6.1).
7. **No-change sampling band (dom-3 as ruled at G1; definition revised for ext1-1).** The band is kept on
   F3.5a and F3.5c, and is defined per statistic and sampling unit instead of one `sqrt(F(28,28))` everywhere.

   *Null model (stated, recorded, captioned).* Under no change, a member's annual (or season-year) values in
   the union of its reference and future windows are independent Gaussian draws with the member's own
   reference mean and detrended SD; each window is OLS-detrended separately, as the statistic is. The band is
   the central `NULL_BAND_LEVEL` (90 %) interval of the **exact statistic drawn**, computed by
   `null_ratio_band` with a seeded Monte Carlo (`NULL_SIMULATIONS = 20 000`, `NULL_SEED` constant, numpy
   `default_rng`; results cached per argument tuple). This one mechanism covers the three cases v2 missed:

   | Panel / element | Statistic | Sampling unit | Band |
   |---|---|---|---|
   | F3.5a temperature, shaded band | ratio of detrended SDs, future / reference | one member | MC on the window pair; when the windows are disjoint, equals `sqrt(((n_f-2)/n_f) / ((n_r-2)/n_r) · F(n_f-2, n_r-2))`, the ddof-0 normalisation factor that is 1 only when `n_f = n_r` (ext2-3) — the analytic value (scipy, already a declared dependency, `pixi.toml:35`) is the test oracle |
   | F3.5a precipitation, shaded band | ratio of CVs (detrended SD / mean) | one member | MC including mean-estimation noise; depends on the reference CV, so the drawn band uses the ensemble-median reference CV of that window and is labelled so |
   | F3.5a model markers | geometric mean of the model's m eligible member ratios | one model | MC of the **same statistic the table reports**: each of the m eligible members is simulated with its **own** reference mean, detrended SD, `n_reference`, `n_future` and window overlap (temperature: SD ratio; precipitation: CV ratio), and each draw takes the geometric mean of those m member ratios; no model-level CV is defined or assumed (ext2-1). The argument tuple is the sorted tuple of member parameters; stored as `null_lo`, `null_hi`, `outside_null` in `variability_model_ratios.csv`; marker filled when outside |
   | F3.5c member points | as F3.5a, per member | one member | the single-member band, drawn |
   | F3.5c / `variability_summary.csv` pooled quantiles | equal-model weighted quantiles | ensemble | **no band**: a spread, not a test; captioned as such |

   *Overlapping windows.* When the reference and future windows share WY (a joined near-term window, § 5.6,
   e.g. 2008–2037 against 1985–2014), the MC draws one series over the union, so shared years enter both
   statistics; the overlap length is recorded per window and named in the caption. Disjoint is the common
   case.

   The band remains a white-noise benchmark: autocorrelation widens the true null, which the caption states.
   Inferences are limited to "inside / outside the 90 % range expected from sampling alone under that model";
   the v2 caption claim "indistinguishable from sampling noise" is removed. Method, level, simulation count,
   seed, n per window and overlap are recorded. The data-driven variant (paired historical windows) stays
   deferred (§ 8).
8. **Equal-model weights for pooled member ratios (dom-4).** F3.5c and the pooled rows of
   `variability_summary.csv` weight each **eligible** member ratio (§ 5.12)
   `1 / eligible_members_in_its_model` (per scenario and window), so each model with ≥ 1 eligible member
   carries total weight 1; weighted quantiles on the log scale. Eligible and excluded members per model are
   recorded and captioned.
9. **Sign agreement (dom-6, dom-11, dom-12).** Per cell: `k/n` models whose model-mean change has the
   ensemble-median sign (lab); **plus** `k_fam/n_fam`, where a family's vote is the sign of its models'
   median change and it agrees when that matches the ensemble-median sign; models with no listed or
   provisional family count as their own family (conservative). **Small-change marker:** cells with
   |ensemble median| below the band (temp 0.5 °C, precip 5 %, 0.1 mm/day; `agreement.py:27`) are greyed and
   not coloured blue/red. The bands are recorded and captioned as display heuristics, not detection
   thresholds. No likelihood language. The AR6 "change exceeds internal variability" share is deferred (§ 8).
10. **Constants** (module level, named, docstrings): `ANALYSIS_LENGTH = 30`, `ANALYSIS_REFERENCE = (1985,
    2014)`, `MIN_MODELS_IQR = 10`, `NULL_BAND_LEVEL = 0.90`, `NULL_SIMULATIONS = 20_000`, `NULL_SEED`,
    `MIN_SEASON_YEARS = 27`, `ZERO_VARIABILITY_RTOL = 1e-12`, agreement bands as above.
11. **Season-year contract (ext1-4).** A season instance (DJF, MAM, JJA, SON) is **owned** by an analysis
    window only if all three of its months lie inside the window's month span (first month of WY `a` to last
    month of WY `b`). Seasonal calculations **never read months outside the window**; a season straddling an
    edge is dropped, not completed from outside. The instance is labelled by the calendar year of its middle
    month (DJF Dec 1985–Feb 1986 → 1986). Its value is the month-length-weighted **mean rate** for both
    variables (°C; mm/day for precipitation, so the § 5.4 dry rule and the absolute-change units are those
    of the annual and monthly rows; CV does not depend on the choice), using `calendar_weights` of the
    member's own calendar (standard, noleap, 360_day; leap Februaries 29 days). This matches the lab
    (`lab:wf2_lab/core.py:191-232`: in-window months only, `season_year = year + (month == 12)`, complete
    three-month groups, day-weighted level). An instance with any missing month is dropped. Resulting counts
    for a complete 30-WY window: January WY — DJF 29, MAM/JJA/SON 30; October WY — DJF/MAM/JJA 30, SON 29.
    These `n_reference`, `n_future` counts go into `changes.csv` and feed the null band's n. A season with
    fewer than `MIN_SEASON_YEARS` instances in either window gets status `insufficient_observations`. Annual
    and monthly rows are unaffected (the kernel already uses complete WY). Tests: § 9.2 "Seasons".
12. **Degenerate variability (ext1-3).** Evaluated per row after the dry rule, with no numerical floors
    inserted. "Zero" means `sd <= ZERO_VARIABILITY_RTOL * max(1, |mean|)` (detrended SD for the ratio rows).

    | Status | Condition | Kept | Dropped |
    |---|---|---|---|
    | `insufficient_observations` | fewer than 3 valid values in either window, or season count below § 5.11 | nothing | the row from every reduction |
    | `zero_reference_variability` | reference SD (or detrended SD) zero | means, absolute changes, absolute SD change | SD % change, CV and ratio |
    | `zero_future_variability` | future SD zero, reference SD positive | ratio `0` reported in the member table | the ratio from log-scale quantiles and geometric means; counted as `n_zero_future` |
    | `dry` (§ 5.4) | reference mean below `min_reference` | absolute change | relative change, CV |

    **Eligibility is per statistic (ext2-2).** Each member row carries two flags, written to `changes.csv`:

    - `mean_change_eligible` — true when the status is `ok`, `zero_reference_variability` or
      `zero_future_variability` and the mean change of that statistic is finite; for the relative
      precipitation change the § 5.4 dry rule also applies (`dry` keeps only the absolute change).
      Variability status never removes a mean change. Model mean changes (`model_changes.csv`),
      `change_summary.csv`, sign agreement, F3.2, F3.6b and F5.1 use these rows.
    - `variability_eligible` — true only for `ok` ratio rows. Only these enter `model_ratios`,
      `ratio_summary`, the weights (§ 5.8) and the null band; a model with no variability-eligible member
      drops out of that variability cell, and `n`, `n_zero_future` and the excluded count are reported per
      cell and in the captions.

    `insufficient_observations` rows are eligible for neither.

## 6. Robustness and availability

| Case | Behaviour |
|---|---|
| Model not in Kuma et al. (2023) table | if its institution (from the catalog entry, lab `inputs.institution_from_catalog_entry`) matches a listed institution with a single family → that family, flagged `provisional` (dom-11); otherwise its own family named after the model, flagged `own`. Country from the institution table or blank. Never raises. |
| Kuma table data | `projections/model_families.csv` (source_id, family, institution, country) from Zenodo 7920408 `models.csv`, with citation header, **only if the record's licence permits redistribution** (checked in commit 2; licence in the file header). Otherwise no vendored table: the 13 P0 mappings stay a code constant with citation, and every other model takes the institution fallback above. Placement (fit-10): commit 2 checks `dev/reference/repo-layout.md` and the `pyproject.toml` package-data settings; the file is read with `importlib.resources`, so it resolves from an installed package. It is reference data, not a run setting, so it does not go under `config/defaults/`. |
| Scenario with no resolved member | absent from `POINTS`, so absent from tables and figures; recorded. |
| Model missing a scenario | reductions use models present per cell; `n`, `n_fam` reported. |
| IQR with < 10 models | `iqr_shown = False`; whiskers and median only. |
| Window unavailable for a member (§ 5.6) | member rows `status = unavailable` with reason; models with no available member drop out of that window's reductions. |
| Analysis reference unavailable for a member | member dropped from C3 with reason (the lab raises, `trajectories.py:79-80`; changed). |
| Variable other than precip/temp | analysis covers precip and temp only; others recorded unavailable. |
| Constant or zero-variability series | statuses of § 5.12; never an error. |
| Corrupt or inconsistent input | identity assertion fails, calendar disagreement on a join, unreadable or wrongly shaped NetCDF, units not as `variable_spec`, a `POINTS` record without its series: **raise** in 2.05b with the member and reason. |

### 6.1 Declared vs written, without placeholders (risk-1, G1, ext1-2, arch-2)

**Where availability is decided.** Final product availability is decided **at run time in 2.05b**, after the
series are read and validated, by `projection_analysis.product_availability` applying the § 4 table to the
computed rows, reading `mean_change_eligible` for change products (F3.2, F3.6b, F5.1, combined cloud) and
`variability_eligible` for F3.5a and F3.5c (§ 5.12, ext2-2). Parse time decides only the **folder set**: `suite_folders` returns `full-period/` and one
`period-<a>-<b>/` per distinct analysis window that `analysis_windows` can place (§ 5.6; a window with fewer
than 30 complete WY in the acquisition span has no folder and is listed as unavailable).

Why not parse time (arch-2 option 1, rejected): several conditions depend on values, not spans — a valid
ratio after the dry and degenerate-variability rules (§ 5.4, § 5.12), a paired temperature/precipitation point
for F3.6b, an all-NaN or truncated member. Recording each member's data end in the series sidecars would move
only the span condition to parse time and still leave the value conditions to run time, so a parse-time
declaration would again need a "residue" failure path. One run-time decision covers all of them.

**Output boundary (Snakemake).** 2.06 declares owned `directory()` outputs, one per folder, plus the two
caption files; the captions JSON is the declared **manifest** of what was written:

```python
rule plot_climate_projections:  # 2.06
    input:  tables = ANALYSIS_TABLES, record = ANALYSIS_RECORD
    output:
        folders = [directory(f"{PLOTS}/{folder}") for folder in SUITE_FOLDERS],
        captions_md = f"{PLOTS}/figure_captions.md",
        captions_json = f"{PLOTS}/_engine/figure_captions.json",
        # + directory(f"{PLOTS}/captioned") when captioned_figures is true
```

This follows the repository's precedent for a run-time-sized figure set: WF0's `subbasins/` bin
(`analyze_climate.smk:424-446`) and WF1's station plots, whose comment records the same choice
(`build_model.smk:1051-1056`: "A directory() rather than a checkpoint … no rule reads these PNGs"). A
checkpoint is rejected for the same reason: no rule consumes a WF2 PNG, so DAG re-evaluation buys nothing,
and `rule all`, the gather edges and `--delete-all-output` keep a static list (the directories and the
manifest). 2.06 creates every owned folder itself (`mkdir(parents=True, exist_ok=True)`) before drawing, so a
folder with no available product exists and is empty whatever Snakemake does; its products are listed under
"Not produced". The manifest contract below counts PNGs only, so any marker file Snakemake keeps inside a
`directory()` output is outside it; commit 5a checks whether one is written and, if so, that the tree
inventory tolerates it as it does for WF0's `subbasins/`.

**Contract.** (1) Every PNG in an owned folder is a key of `_engine/figure_captions.json`, and every key is a
file: asserted by 2.06 before it exits and by the rapid-run test (§ 9.2). (2) Every product of
`SUITE_PRODUCTS` × folder is either a manifest key or a "Not produced" row with the reason from
`availability.csv`. (3) 2.06 never draws a product `availability.csv` marks unavailable, and an artist that
raises on an available product is a defect and fails the rule.

**Failure policy.** A legitimately empty optional product never aborts WF2: it is listed with its reason. Hard
failures remain for corrupt or inconsistent inputs (§ 6 last row) and for code defects. v2's "runtime residue
raises" rule is removed.

**Smoke configs** (both unit-tested on `product_availability` with synthetic tables, and run end to end):
rapid (2 models, 1 scenario, 1 member each, `test_case/project_config_rapid_analyze_projections.yml:8-14`)
draws 14 figures, F3.5c not produced; wf2_fast (1 model,
`project_config_wf2_fast_analyze_projections.yml:6-11`) draws 13, F3.5c and F5.1 not produced. A synthetic
ensemble with one runtime-unavailable product (one model's far-window members ending in 2099, another
degenerate) produces the remaining products and the listed one.

## 7. Identity and blast radius

- **WF3/WF4 run ids.** `repository_code_inventory` follows static imports from stage entry points
  (`experiment/content_identity.py:84-130`). No module under `experiment/`, `shared/` or `weathergen/` imports
  `blueearth_cst.projections`; this design edits nothing in `shared/` or `climate_analysis/`. WF3/WF4 do
  import `climate_analysis.prepare_climate_data_catalog` (`experiment/downscale_climate_forcing.py:11`,
  `experiment/rules/simulate_and_metrics.smk:13`, `wf4_ancillary_descriptor.py:342`), but that closure does
  not include `diagnostic_figures`, and `climate_analysis/__init__.py` is empty, so the WF0 tokens WF2 imports
  are outside WF3/WF4 identities (fit-11). Moving the identity helpers into the new `series_checks` (§ 3)
  touches a module WF2 alone imports; commit 1 diffs `repository_code_inventory` base vs head to confirm.
  Expected: identities unchanged. Falsifier in § 9. **Contract note:** with this change `diagnostic_figures`
  becomes a cross-workflow surface; any later edit to it takes the normal validation ladder, not the
  figure-only gate (AGENTS.md, "a shared helper edited in service of a plot").
- **Stage B cache.** `STAGE_B_HASH` unchanged under the additive-only rule (§ 2); `REDUCER_HASH` untouched.
- **Baseline manifest (risk-9).** The default gate covers the two CSVs (the byte-identity gate covers them
  better). `check_baseline.py:313-330` lists three retired PNGs as `FIGURE_KINDS` targets; replace them with
  `full-period/annual-precipitation.png` and `period-<a>-<b>/change-factor-cloud.png` (resolved for the
  baseline config). The manifest fingerprints are **not** re-recorded here: the manifest is already stale
  (AGENTS.md) and its re-record belongs to the pending regeneration; until then `--include-figures` reports
  the two new entries as unrecorded, which the commit message and `rule-index.md` note.
- **Tree inventory (fit-1).** `dev/scripts/semantic_tree_diff.py:449-450` classifies projection tiers from a
  fixed tuple (`raw`, `scalar`, `summary`, `plots`, plus `report.md` and `_engine/stage_b_settings.json`).
  Commit 4 adds the `analysis` tier there and `analysis/...` rows to the COVERED map of
  `tests/test_project_tree_inventory.py`; commit 5a/5b replace the `plots/overview/*` rows
  (`test_project_tree_inventory.py:129-133`) with `plots/full-period/…`, `plots/period-<a>-<b>/…`,
  `plots/figure_captions.md`, `plots/_engine/figure_captions.json` and `plots/captioned/`, at whatever grain
  the rule set uses (if `plots/` is already a whole-tier rule, only the COVERED rows change).
- **Retired files in existing trees (risk-10).** 2.06 does not delete files it does not own (its directories
  are new paths). The retired paths are listed in `workflow-analyze-projections.qmd` and in
  `figure_captions.md` ("retired in this version; safe to delete"); `semantic_tree_diff.py` reports them as
  predecessor paths in old trees, which is the intended signal.
- **Dry-runs.** `tests/test_cli.py` WF2 dry-runs see one more rule and new paths.
- **Other stale references fixed in the same commits** (fit-4, named targets):
  - `docs/site/toolbox-reference/workflow-analyze-projections.qmd` — rule table (lines 11-17) gains 2.05b,
    the mermaid DAG (line 30 onward) becomes 2.04 → 2.05b → 2.06 with 2.05 parallel, an `analysis/` outputs
    paragraph (commit 4); figure list by folder and the retired-path note (commit 5b).
  - `docs/guide/outputs.md` — the `data/climate/` line (line 15) names `analysis/` tables and the new
    `plots/` folders (commit 5b).
  - `dev/reference/workflows/rule-index.md` — the numbering table (:95-103), the stage DAG and its prose
    (:782-817: "2.06 reads 2.04's series, not 2.05" becomes "2.06 reads 2.05b's tables"; 2.05's
    `plots/overview` output removed), and the rule entries (:881-908, plus a new 2.05b entry). The DAG and
    the 2.05b entry land in commit 4, 2.06's inputs in 5a, the 2.05 output removal in 5b.
  - `dev/scripts/console_sample_specs.py:292-298` (WF2 targets already stale, `figures/`,
    `gcm-timeseries`) rewritten to the new paths with a 2.05b sample (commit 5b, fit-8).
  - `report.py:162-166`, `projection_figures.py` module docstring (commit 5b).

## 8. Alternatives considered

| Choice | Chosen | Alternative | Why not / when it would win |
|---|---|---|---|
| Port shape | Refactor: kernels reused, new modules by concern | Port lab modules as-is | Violates the one-calculator ruling; two windowing implementations would drift. |
| Calculation site | New rule 2.05b, parallel to 2.05 | Fold into 2.05 | 2.05 is the cache-guarded change-factor terminal; plot-table changes would re-run the merge. |
| Figure family | Replace | Extend (keep the five) | Owner reviewed the revised set as the set; no consumer of old paths (`web-app-independence`). |
| Default | On by default | Opt-in key | Replacement makes opt-in mean "no figures"; would win if § 9 timing shows material cost. |
| Tokens | Import from `diagnostic_figures` + smoke test | `shared/figure_tokens.py` | Edits WF0 and `shared/` for no gain now; wins when a third workflow needs them. |
| Unavailable products | Run-time availability in 2.05b; owned `directory()` folders + captions manifest; unavailable listed | Placeholder figures (v1) / parse-time availability (v2) / parse-time with data ends in sidecars (arch-2 opt. 1) / checkpoint | Placeholders ruled out at G1; parse time cannot see value conditions (§ 6.1); a checkpoint re-plans a DAG nothing downstream consumes (`build_model.smk:1051-1056`). |
| Null band | Per-panel MC under a stated white-noise null (exact statistic, overlap, m) | One `sqrt(F(28,28))` band everywhere (v2) / label as illustrative only | v2's band is wrong for CV, overlap and model means (ext1-1); illustrative-only would drop the G1-ruled band's meaning. |
| Analysis dry rule | Mean-keyed per period, post-process | Kernel per-statistic rule (risk-2) | Cannot cover CV rows; flags variability, not dryness (§ 5.4). |
| Analysis reference | Configured if ≥ 30 WY, else 1985–2014 | Always 1985–2014 (v1) / always configured | Fixed drifts from the stress-test zero point; configured-only gives 15-WY windows on P0. |
| Far horizon | Shift to fit the data end | Unavailable (v1) | Drops the most-used AR6 horizon. |
| Shared window | Merge folders | Refuse at parse time | Refusal rejects a valid config and blocks the overlay CSV too. |
| Null band source | White-noise MC | Paired historical windows per member | Absorbs autocorrelation, but needs a method review and two disjoint 30-WY historical windows; deferred. |
| Agreement noise | Small-change marker on the median | AR6 simple approach | Needs a per-model internal-variability estimate; deferred. |
| HTML page | Not included | Port `report_wf2` | No consumer; third reporting surface. |
| Cloud data | Analysis-window model means | Stage-B merge cloud | Lab-reviewed F3.6b uses the analysis window; keeps figures out of a `derive_` rule. |

## 9. Validation plan

**Pre-change snapshots (before commit 1)**, digests under `dev/tasks/t2610071652/evidence/`, data copies in
the worktree `.tmp/scratchpad/`: change-factor CSVs from rapid (re-run at the lane head; the 2026-09-16 copy
predates the lane's WF2 fixes) and P0 (+ sha256, already taken); lab `results/*.csv` at lab `7560e71`;
`STAGE_B_HASH`, `REDUCER_HASH`, WF3/WF4 inventory digests for rapid.

### 9.1 Lab-parity scope (risk-6)

Under parity on P0 (P0 triggers neither the configured-reference switch, a shift nor a join, has no dry cell
and no degenerate variability, and its seasonal convention matches the lab's, § 5.11, so dom-1, dom-2, dom-5,
ext1-3 and ext1-4 do not change these values). Rows are matched on the lab's horizon mapped to `window_id`
(arch-3); P0 has one horizon, so the mapping is one to one:

| Table | Columns under parity |
|---|---|
| `changes.csv` (analysis rows) | reference/future values, absolute and relative change, `n_reference`, `n_future`, status |
| `model_changes.csv`, `change_summary.csv` | all value columns; `iqr_shown` |
| `climatology.csv`, `climatology_summary.csv`, `monthly_change_summary.csv` | all |
| `member_anomalies.csv`, `trajectory_range.csv` | all |
| `variability_member_ratios.csv`, `variability_model_ratios.csv` | all (unweighted, per member / per model) |
| `sign_agreement.csv` | `k`, `n`, median and median sign only |
| `coverage.csv`, `availability.csv` | model, scenario, member counts; family for listed models |

**Excluded by name, with reason:** `variability_summary.csv` pooled rows (dom-4 weights); `sign_agreement.csv`
`k_fam`, `n_fam`, `small_change` (dom-6, new); family `provisional`/`own` flags (dom-11, new; none on P0);
`analysis_record.json` (new schema); new columns `window_id`, `horizons` (key), `null_lo`, `null_hi`,
`outside_null` (ext1-1), `n_eligible`, `n_excluded`, `n_zero_future` (ext1-3), and the new status values (none
occur on P0). Each excluded item is covered by a known-answer, null-band, degenerate or season test below. The
parity test maps columns by name and fails on an unmapped column, so an exclusion cannot be silent.

### 9.2 Checks

| Claim | Check | Falsifier |
|---|---|---|
| Aligned CSVs byte-identical | sha256 after the final WF2 run on rapid and P0; synthetic dry case (§ 5.4) | any digest differs |
| Stage B not invalidated | `STAGE_B_HASH` before/after every commit touching `get_change_climate_proj.py` | values differ |
| Lab parity | `tests/test_projection_analysis_parity.py` (local; skips without P0, reason printed) | value outside § 5.2; count/sign mismatch; unmapped column |
| Known answers (dom-7) | (a) linear trend + white noise: `std_detrended` recovers the noise SD within sampling error, `std` does not; (b) stationary series in both windows, many members: median member ratio ≈ 1 and the 5–95 % spread matches the § 5.7 band; (c) symmetric null changes: agreement fraction ≈ 0.5; (d) weighted pooling: a 5-member model at ratio 2 and a 1-member model at 0.5 → weighted median at geometric centre 1; (e) family counts on a hand-built 4-model/2-family case; (f) √2 ratio and hand medians | any outside stated tolerance |
| Null band per panel (ext1-1) | `null_ratio_band` coverage on independent simulated stationary series (different seed from `NULL_SEED`), 2 000 replicates each: temperature SD ratio disjoint at 30 vs 30 (equals scipy `sqrt(F(28,28))` quantiles within MC error 0.01) and at unequal counts 27 vs 29 (equals `sqrt(((27-2)/27)/((29-2)/29) · F(25,27))` quantiles within 0.01, and the uncorrected `sqrt(F(25,27))` is shown to fail, ext2-3); precipitation CV ratio at CV 0.1 and 0.4; overlapping windows (2008–2037 vs 1985–2014); model geometric mean m = 3 with **heterogeneous** members — precipitation CVs 0.1 / 0.25 / 0.4, different means and SDs, sample counts 30/30, 27/29 and one overlapping pair — simulated independently of `null_ratio_band` and reduced to the table's geometric mean, plus the same for temperature SDs with unequal counts (ext2-1); each case covers 90 % ± 2 % | coverage outside 88–92 %; analytic mismatch |
| Degenerate variability (ext1-3) | constant wet precipitation series; constant temperature series; zero future variability; a member with 2 valid years; weights recomputed over eligible members (5-member model with 2 zero-future members → weights 1/3) | infinity or NaN in a table; wrong status; ineligible ratio in a log summary; weights not summing to 1 per model |
| Mean change with constant reference (ext2-2) | member with a constant reference temperature series (and a constant wet precipitation series) and a nonzero future mean change: status `zero_reference_variability`, `mean_change_eligible` true, `variability_eligible` false; its change enters `model_changes.csv`, `change_summary.csv` and sign agreement; with an all-constant ensemble `product_availability` marks F3.2, F3.6b and F5.1 available and F3.5a/F3.5c unavailable; 2.06 renders the change figures with the member's point | mean change dropped; change product listed "Not produced"; ratio entering a variability reduction |
| Seasons (ext1-4) | hand-calculated cases with `length` overridden to 3 WY: January WY 2001–2003 → DJF instances labelled 2002, 2003 only (Jan–Feb 2001 and Dec 2003 unused); October WY 2001–2003 → DJF 2002, 2003, 2004 and SON 2002, 2003; Dec = 1, Jan = 2, Feb = 3 → standard non-leap 177/90, leap Feb 180/91, 360_day 2.0, noleap 177/90; one missing January drops that instance and decrements `n`; a value placed outside the window never changes a result | wrong label, count or value; any read outside the window |
| Windows (risk-3, dom-10) | unit cases: Jan `mid` 2046–2054 → 2036–2065; Jan 2081–2100 → 2071–2100 shifted; Oct 2081–2100 → WY 2070–2099; 2015–2030 → 2008–2037 joined; two horizons merging into one folder, with one set of rows keyed by `window_id` and `horizons` listing both (arch-3); configured reference of 30 WY used vs 15 WY → 1985–2014 | wrong bounds or flags |
| Dry rule (dom-5) | § 5.4 synthetic test | analysis std row flagged, or aligned row changed |
| Unlisted model degrades | synthetic `XYZ/FOO-1` with a listed and an unlisted institution | raise, missing row, wrong flag |
| Availability (risk-1, ext1-2) | `product_availability` unit tests for the rapid and wf2_fast compositions; `suite_folders` tests; WF2 dry-run lists exactly the § 6.1 folders | wrong set; extra or missing folder |
| Partial ensemble (ext1-2, arch-2) | synthetic run: one product runtime-unavailable (members ending 2099 on a shifted far window; degenerate ratios), others available | WF2 fails; product drawn; product missing from "Not produced" |
| Manifest contract (§ 6.1) | rapid WF2 run: PNGs in owned folders == JSON keys; `SUITE_PRODUCTS` × folders == keys ∪ "Not produced" | extra, missing or unlisted file |
| Corrupt input still fails | identity mismatch and unreadable NetCDF fixtures | 2.05b succeeds |
| WF3/WF4 identity unchanged | recompute inventory digests | differ |
| Run time | 2.05b + 2.06 benchmark rows on P0 in `wf2_benchmarks.md` | > 5 min combined (assumed budget, confirm at G2) |
| Figures match lab | render on P0, publish PNGs as an Artifact, owner visual check | owner rejects |

Gates per the AGENTS.md ladder (fit-3): focused tests per commit; `pytest tests/test_cli.py` on every commit
touching the Snakefile or a `script:` signature; `pixi run lint` and `pixi run format-check` on every Python
commit; before merging the batch, `pixi run test-fast`, then **`pixi run test-full`** (the batch changes
`script:` signatures: 2.05's outputs and params, 2.06's inputs and params, a new 2.05b `script:`) and
**`pixi run test-e2e`** (all five workflows through `scripts/run_workflows.py`; it is one task, there is no
per-workflow leg, `pixi.toml:160`). Skips in `test-e2e` are read and their reasons reported; a skip is not a
pass. Gates are redirected to a log file, never piped through `tail`.

## 10. Commit plan

Each commit is independently green: the Snakefile **parses and dry-runs** at every commit, its focused checks
pass, and any rule it adds is scheduled and run. arch-1: no commit changes a path grammar while a Snakefile
constant still indexes the old one. The new folder grammar is a **new** function (`suite_folders`);
`figure_relative_paths`, `CLOUD_FACETED_PATH` and the constants built from them
(`analyze_projections.smk:352-367`) stay intact until 5b deletes them together.

| # | Lands | Focused checks | Est. |
|---|---|---|---|
| 0 | Evidence snapshots (no code; rapid re-run at the lane head) | digests recorded | 45 min |
| 1 | `get_change_climate_proj`: `analysis_windows`, `analysis_slice` (with join), `get_change_seasonal_clim_proj` (season-year contract), `detrended_std` + unit, window and season tests; identity and calendar helpers moved into `series_checks`, 2.05 repointed | new tests; `test_get_change_climate_proj*.py`; `STAGE_B_HASH`, `REDUCER_HASH` equal; inventory diff; `test_cli.py`; rapid 2.05 re-run, CSVs byte-identical | 3 h |
| 2 | `projection_coverage.py` + family data (licence checked; vendored CSV or code constant) + provisional/own fallback + tests | unit tests incl. unlisted model | 1.5 h |
| 3 | `projection_analysis.py` (dry rule, degenerate statuses, reductions, agreement with families and marker, weighted pooling over eligible members, per-panel MC null band, `product_availability`), `projection_trajectories.py` + known-answer, null-band and degenerate tests | unit, known-answer, null-coverage tests | 4.5 h |
| 4 | Rule 2.05b + `prepare_projection_analysis.py` + `analysis_record.json` (window-keyed tables, availability); 2.05b terminal on the gather edges; tables and record in `WF2_TARGETS`; `analysis` tier in `semantic_tree_diff.py` and COVERED rows; rule-index 2.05b entry, numbering table and DAG; `workflow-analyze-projections.qmd` rule table, DAG, `analysis/` paragraph | `test_cli.py`; `test_project_tree_inventory.py`; dry-run lists 2.05b; rapid WF2 run executes 2.05b; parity test on P0; dry-reference byte test; lint | 3.5 h |
| 5a | `suite_folders` + `SUITE_PRODUCTS` (new; `figure_relative_paths` untouched), artists + captions modules (WF0 tokens, render smoke test), 2.06 repointed to tables with `directory()` outputs and the captions manifest, `captioned_figures` key + template; gather edge `ANNUAL_PRECIPITATION_PLOT` → `_engine/figure_captions.json`; `WF2_TARGETS` figure entries → 2.06 folders and caption files. 2.06's old outputs (`overview/annual-*.png`, `windows/*/monthly-change-factors.png`) stop being produced here; 2.05's cloud, `CHANGE_FACTOR_CLOUD_PLOT(S)` and its gather edge are untouched; rule-index 2.06 inputs | `test_projection_figures.py`, `test_cli.py`, tree inventory test, lint; rapid and wf2_fast runs with the manifest check; partial-ensemble test; render P0 and publish a PNG Artifact | 4.5 h |
| 5b | Retirement: 2.05 cloud and `figure_names` param, `import hydromt` in `derive_change_factors.py`, `report.md` link, cloud gather edge → annual CSV, `figure_relative_paths`, `CLOUD_FACETED_PATH`, smk:352-367 constants, `projection_plots.py` and dead functions; `- tests/test_projection_plots.py`, `~ tests/test_get_change_climate_proj_summary.py`, `~ tests/test_projection_figures.py`; tree inventory rows, `check_baseline` entries, console spec; `outputs.qmd`, rule-index 2.05 entry, retired-path note | `test_project_tree_inventory.py`, `test_projection_figures.py`, `test_get_change_climate_proj_summary.py`, `test_cli.py`, lint; `grep` finds no caller of retired names; rapid run: CSVs byte-identical | 2.5 h |
| 6 | Batch gates | byte-identity (rapid, P0, synthetic), identity digests, timing, `test-fast`, `test-full`, `test-e2e` (skip reasons read) | 3 h |

Between 5a and 5b, 2.05's old cloud (`overview/change-factor-cloud*.png`) coexists with the new folders for
one commit; it lives under `overview/`, outside every 2.06 directory, so nothing collides, and the commit
parses because every constant it indexes still exists.

## 11. Tree and user-facing change inventory

**Repository** (`+` added, `~` changed, `-` removed):

```
blueearth_cst/projections/
~ get_change_climate_proj.py        analysis windows/slice + seasonal/detrended functions (additive only)
~ derive_change_factors.py          no cloud, no figure_names; identity helpers moved out; explicit hydromt import
+ series_checks.py                  identity assertion and calendar-agreement helpers (moved, arch-6)
~ get_change_climate_proj_summary.py   plot_change_summary removed
~ projection_figures.py             suite_folders, SUITE_PRODUCTS; palette moved here; figure_relative_paths,
                                    CLOUD_FACETED_PATH removed
~ plot_proj_timeseries.py           thin renderer driver over analysis tables
~ report.py                         figure list replaced by a link to plots/figure_captions.md
- projection_plots.py               retired (draw_* replaced)
+ prepare_projection_analysis.py    script: of rule 2.05b
+ projection_analysis.py            change table, dry rule, degenerate statuses, reductions, agreement, C2,
                                    C4, per-panel null band, product_availability
+ projection_trajectories.py        C3 anomalies and range
+ projection_coverage.py            C0 coverage, availability, family fallback
+ projection_suite_figures.py       lab-style artists
+ projection_captions.py            caption text
+ model_families.csv                Kuma et al. (2023) families — only if the licence permits
~ analyze_projections.smk           rule 2.05b; 2.05 param/outputs; 2.06 directory() outputs + manifest;
                                    gather edges; WF2_TARGETS; captioned_figures; smk:352-367 constants removed
~ config/templates/project_config.analyze_projections.template.yml   captioned_figures comment
~ tests/test_projection_figures.py (suite_folders, render smoke), test_project_tree_inventory.py (COVERED rows)
~ tests/test_get_change_climate_proj_summary.py   cloud test removed; property moved to model_changes test
- tests/test_projection_plots.py
+ tests/test_projection_analysis.py, test_projection_windows.py, test_projection_analysis_parity.py,
  test_projection_null_band.py
~ dev/scripts/semantic_tree_diff.py  analysis tier (and plots/ folders if finer than the tier)
~ dev/reference/workflows/rule-index.md   :95-103 numbering, :782-817 DAG/prose, :881-908 entries + 2.05b
~ dev/scripts/check_baseline.py, dev/scripts/console_sample_specs.py (:292-298)
~ docs/site/toolbox-reference/workflow-analyze-projections.qmd   rule table, DAG, analysis/, figures, retired note
~ docs/guide/outputs.md        analysis/ tables and plots/ folders
```

**Generated** under `<project>/data/climate/projections/<ensemble>/`:

```
summary/…                            unchanged (CSV bytes identical)
report.md                            ~ links plots/figure_captions.md instead of listing figures
+ analysis/*.csv (always written; per-window tables keyed by window_id), analysis/analysis_record.json
plots/                               full-period/ and period-<a>-<b>/ are owned directory() outputs of 2.06
- overview/{annual-*,change-factor-cloud*}.png
- windows/<name>-<start>-<end>/monthly-change-factors.png
+ full-period/{availability,trajectory-*,annual-*}.png   [+ change-factor-cloud-combined.png if ≥ 2 windows]
+ period-<a>-<b>/{change-*,seasonal-cycle-*,variability-*,change-factor-cloud,sign-agreement}.png
                                     one folder per distinct analysis window; products drawn per § 6.1
                                     (run-time availability; a folder may be empty)
+ figure_captions.md (incl. "Not produced" and retired paths), _engine/figure_captions.json
+ captioned/<folder>/*.png           only with captioned_figures: true
```

| Change | Current | Proposed | Affected / migration |
|---|---|---|---|
| WF2 figure paths | `plots/overview/…`, `plots/windows/<h>/…` | `plots/full-period/…`, `plots/period-<a>-<b>/…` (analysis-window years) | old files remain; listed as retired in docs and `figure_captions.md` |
| Figure set | 5 (+1) | up to 15 for one window (5 + 10·n + [n ≥ 2] for n windows); unavailable products listed with reason, not drawn; never a WF2 failure | users; docs |
| Tree inventory | 4 projection tiers | + `analysis` tier; new `plots/` folders | `tree-check`, `semantic_tree_diff.py` |
| New tables | — | `analysis/*.csv`, `analysis_record.json` | addition |
| Captions | in-figure caveat | `figure_captions.md`/`.json`, optional captioned copies; both window pairs stated | users |
| `report.md` | lists figures | links `figure_captions.md` | users |
| Config | — | optional `captioned_figures` (default false) | none; existing configs valid |
| Commands | unchanged | unchanged | — |
| Change-factor CSVs | — | unchanged | CST-API unaffected |
| Baseline figure targets | 3 retired PNGs | 2 new PNGs, unrecorded until regeneration | `--include-figures` users |

## 12. Assumptions and unknowns

- **Unknown:** Kuma Zenodo record licence (resolved in commit 2; both branches specified, § 6).
- **Unknown:** P0 run time (budget 5 min assumed; confirm at G2).
- **Assumption:** float agreement at 1e-9 (§ 5.2); the falsifier reports, never widens silently.
- **Resolved:** scipy is a declared dependency (`pixi.toml:35`); used only as the analytic test oracle (§
  5.7).
- **Assumption:** `POINTS` at parse time lists exactly the members whose series 2.05b reads (the records 2.05
  uses); a `POINTS` record without its series is a corrupt input and raises (§ 6).
- **Assumption:** the MC null band (20 000 draws, cached per argument tuple) adds seconds, not minutes, to
  2.05b on P0; confirmed by the run-time row of § 9.2.
- **Assumption:** the lab's seasonal boundary convention matches § 5.11. Checked in commit 1 against
  `lab:wf2_lab/core.py:203-255`; if it differs, seasonal rows leave the § 9.1 parity scope by name and are
  covered by the hand-calculated tests.
- **To verify in commit 4:** the grain at which `semantic_tree_diff.py` and the COVERED map classify `plots/`
  (§ 7).
- Settled at G1 (not open): placeholders (none), combined cloud (≥ 2 windows), folder years (analysis
  window). Artist module name: `projection_suite_figures.py` (author's choice; no objection at G1).

## 13. Revision log (v1 → v2)

| Finding | Change in v2 |
|---|---|
| dom-1 | Analysis reference = configured `reference_window` if ≥ 30 WY, else 1985–2014; both window pairs in the record and every period caption (§ 5.5, § 4). Optional hollow aligned marker on F3.6b not adopted (figure set owner-reviewed). |
| dom-2 | Far-end shift to the last complete WY, 30 WY kept, recorded and captioned (§ 5.6). |
| dom-3 | Analytic no-change `sqrt(F(28,28))` 90 % band on F3.5a/F3.5c; method recorded and captioned (§ 5.7). |
| dom-4 | Pooled member ratios weighted 1/members-per-model (§ 5.8); known-answer test (d). |
| dom-5 | Single mean-keyed per-period dry rule for all analysis rows via post-process; v1's equivalence claim corrected; kernel untouched; synthetic test (§ 5.4). |
| dom-6 | Family counts, small-change marker, "count, not likelihood" wording on F5.1 (§ 5.9, § 4). |
| dom-7 | Known-answer tests (a)–(f) (§ 9.2). |
| dom-8 | Trajectory band caption wording; members per model recorded (§ 4). |
| dom-9 | "Ensemble spread, not a confidence interval; families count separately" caption (§ 4). |
| dom-10 | Near-end join rule with calendar check and unit test (§ 5.6, § 9.2). |
| dom-11 | Provisional family from institution, flagged; own family otherwise (§ 6). |
| dom-12 | Agreement bands recorded and captioned as display heuristics (§ 5.9). |
| risk-1 | Placeholders removed; parse-time `suite_availability`; undrawable products undeclared and listed; runtime residue raises (§ 6.1). |
| risk-2 | Kernel untouched; synthetic dry-reference byte test; its per-statistic rule choice not adopted (§ 5.4). |
| risk-3 | Parse-time windows shared by paths and 2.05b; Oct WY end case; join; no per-member shift; shared windows merge (§ 5.6, § 4). |
| risk-4 | 2.05b scheduled via the gather edges from commit 4; commit 5 split into 5a/5b (§ 10). |
| risk-5 | `figure_names` dropped from 2.05; `report.md` links captions; 2.05b no longer reads 2.05 outputs (§ 3). |
| risk-6 | Parity scope listed; method-changed items excluded by name and covered by known-answer tests (§ 9.1). |
| risk-7 | Additive-only rule: call roots, never edit roots, callees or referenced constants (§ 2). |
| risk-8 | Dependency recorded in rule-index; WF2 render smoke test (§ 4). |
| risk-9 | Baseline figure targets replaced; manifest re-record deferred to the pending regeneration (§ 7). |
| risk-10 | Retired paths listed in docs and `figure_captions.md`; tree retired list if one exists (§ 7). |

## 14. Revision log (v2 → v3)

Sources: `external-review-r1.md`, `internal-review-architecture.md`, `internal-review-repo-fit.md`;
conflict per `internal-review-index.md` "Conflicts (2)".

| Finding | Change in v3 |
|---|---|
| ext1-1 | Null band defined per panel: seeded MC of the exact statistic under a stated white-noise null; CV includes mean noise; overlapping windows simulated on the union; model markers tested against an m-member band; pooled quantiles carry no band; "indistinguishable" removed (§ 5.7, § 4, § 9.2). |
| ext1-2 | Availability decided at run time in 2.05b from validated data; 2.06 owns `directory()` folders plus a captions manifest; empty optional products listed, never fatal; corrupt inputs still raise (§ 6.1, § 6). |
| ext1-3 | Statuses `insufficient_observations`, `zero_reference_variability`, `zero_future_variability`; eligibility and weights over eligible members; no floors (§ 5.12, § 5.8). |
| ext1-4 | Season-year contract: ownership inside the window only, middle-month label, calendar weights, missing-month drop, counts and minimum; hand-calculated Jan/Oct DJF tests (§ 5.11, § 9.2). |
| arch-1 | New `suite_folders` beside an untouched `figure_relative_paths`; old constants retired together in 5b; 5a moves only 2.06's gather edge (§ 10, § 3). |
| arch-2 | Conflicts (2) settled with ext1-2: option 2 adopted (owned directories + manifest); option 1 rejected — value conditions are run-time only (§ 6.1, § 8). |
| arch-3 | Per-window tables keyed by `window_id`, each window computed once; `horizons` list in the record; merge test asserts keys (§ 3, § 9.2). |
| arch-4 | Count formula 5 + 10·n + [n ≥ 2] (§ 4, § 11). |
| arch-5 | Availability moved to `projection_analysis.product_availability` (run time); `projection_figures` keeps only folders and file names (§ 2). |
| arch-6 | Identity and calendar helpers moved to a new library module `series_checks`; both hashes and the inventory checked (§ 3, § 7, § 10). |
| fit-1 | `semantic_tree_diff.py` `analysis` tier and COVERED rows (§ 7, § 10, § 11). |
| fit-2 | Retired tests listed and handled in 5b (§ 3, § 10, § 11). |
| fit-3 | `test-full` and `test-e2e` (whole task) at batch merge; "WF2 leg" dropped (§ 9.2, § 10). |
| fit-4 | Named doc targets: `workflow-analyze-projections.qmd`, `guide/outputs.qmd`, rule-index :95-103, :782-817, :881-908 (§ 7, § 11). |
| fit-5 | Tables, record, folders and caption files in `WF2_TARGETS` (§ 3). |
| fit-6 | Script-body convention stated (§ 3). |
| fit-7 | `save_figure` at dpi 600, white face; `run_log_core.plural` for console rows (§ 3, § 4). |
| fit-8 | Console rows via `log_row` with `listed` caps; console spec rewritten in 5b (§ 3, § 7). |
| fit-9 | `import hydromt` moved to 5b; 2.05 re-run claim corrected (§ 3). |
| fit-10 | `model_families.csv` placement checked against repo-layout and package data; `importlib.resources` (§ 6). |
| fit-11 | § 7 identity wording made precise; `diagnostic_figures` becomes a normal-ladder surface (§ 7). |

## 15. Revision log (v3 → v4)

Source: `external-review-scoped-v3.md` (scoped verification pass). No other decision changed.

| Finding | Change in v4 |
|---|---|
| ext2-1 | Model-marker null band simulates each eligible member with its own reference mean, detrended SD, counts and overlap and reduces to the table's geometric mean; heterogeneous CV and count coverage tests (§ 5.7, § 9.2). |
| ext2-2 | Per-statistic eligibility (`mean_change_eligible`, `variability_eligible`); mean changes kept regardless of variability status; § 4 predicates and § 6.1 availability updated; constant-reference test through reduction, availability and rendering (§ 5.12, § 4, § 6.1, § 9.2). |
| ext2-3 | Disjoint ddof-0 identity corrected with factor ((n_f-2)/n_f)/((n_r-2)/n_r); 27 vs 29 oracle test (§ 5.7, § 9.2). |
