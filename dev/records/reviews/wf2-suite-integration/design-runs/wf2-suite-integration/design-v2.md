# WF2 suite integration — design v2

- **Status:** revised draft (design-review loop `wf2-suite-integration`, revision r1; G1 approved
  2026-10-07, G2 pending)
- **Genre:** decision record, milestone style (goal, what changes, alternatives, commit plan)
- **Task:** `t2610071652` · lane `feat/wf2-cmip6-improvements` (session-1) · **Date:** 2026-10-07
- **Lifecycle:** `maintained-current` until implementation lands; revision log append-only
- **Revisions:** v1 2026-10-07, first draft from `intake.md`; v2 2026-10-07, G1 rulings and internal panel
  (`internal-review-domain.md`, `internal-review-risk.md`) — see § 13

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
                                   │      (parallel to 2.05; does not read its outputs)
                                   ▼
                 2.06 plot_climate_projections ──► plots/full-period/*.png, plots/period-<a>-<b>/*.png,
                                                   plots/figure_captions.md, plots/_engine/figure_captions.json
```

**Settled framing (owner rulings 2026-10-07, intake table, and G1 rulings in `status.md`).**

- *Analysis + figures* move into `blueearth_cst/projections`; **one calculator** — the analysis window
  extends `get_change_climate_proj`, it does not run beside it.
- *Lab style* for WF2 figures (captions outside the image, scenario key top-right, no model labels on the
  cloud, WF0 size classes). Revises the 2026-08-11 toolbox rulings for WF2 only.
- G1: analysis windows and their relation to the configured windows (§ 5.5), far-horizon shift (§ 5.6),
  no-change sampling band on the variability ratios (§ 5.7), equal-model weights for pooled member ratios
  (§ 5.8), family counts and small-change marker on agreement (§ 5.9), provisional family from institution
  (§ 6), no placeholder figures (§ 6.1), combined cloud only with ≥ 2 horizons (§ 4), folders named by
  analysis-window years (§ 4), Kuma table vendored only if its licence permits (§ 6).
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
| Seasonal values (DJF/MAM/JJA/SON), month-length weighted; detrended SD (OLS in window, ddof 0); precip CV of period integrals | E `get_change_seasonal_clim_proj`, `detrended_std` | `core.period_values`, `core.detrended_std`, `core.statistics` (`core.py:203-255`) |
| Analysis dry-reference rule (one rule for all analysis rows, § 5.4) | N `projection_analysis.apply_dry_reference` (post-process) | `core.py:295-321` |
| Long per-member analysis table (status/reason per row) | N `projections/projection_analysis.py` `analysis_change_table` | `core.change_table` (shape and status vocabulary only) |
| Member→model reduction, ensemble summary with IQR floor (10 models) | N `projection_analysis.model_changes`, `ensemble_summary` | `means.py:93-133` |
| Sign agreement: model `k/n`, family `k_fam/n_fam`, small-change marker (§ 5.9) | N `projection_analysis.sign_agreement` | `agreement.py:44-69` (+ G1 additions) |
| C2 climatology + monthly change summaries | N `projection_analysis.climatology`, `monthly_change` | `seasonal.py:35-71` |
| C3 member anomalies vs own analysis-reference mean; per-model and ensemble range | N `projections/projection_trajectories.py` | `trajectories.py:64-141` |
| C4 variability: member ratios, per-model geometric mean, equal-model pooled summary, null band | N `projection_analysis.member_ratios`, `model_ratios`, `ratio_summary`, `null_ratio_band` | `variability.py:50-100` (+ G1 weights, band) |
| C0 coverage / availability with Kuma et al. (2023) family (listed / provisional / own), institution, country | N `projections/projection_coverage.py`; data `projections/model_families.csv` (licence-gated, § 6) | `coverage.py:63-176` |
| Parse-time suite availability (§ 6.1) | N `projection_figures.suite_availability` | — (new) |
| Figure artists (lab style) | N `projections/projection_suite_figures.py` | `figures_wf2.py` (reference implementation) |
| Captions | N `projections/projection_captions.py` | `captions_wf2.caption` (+ G1 wording) |
| Figure path contract | E `projection_figures.figure_relative_paths` (stays the single source) | `run.period_folder` |
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
| params | `horizons`, `water_year_start`, `reference_window`, `points` (the `POINTS` records 2.05 receives), `variable_spec`, `min_reference`, `availability` (from `suite_availability`, § 6.1), `table_names` |
| output | `analysis/` tables, declared individually: `coverage.csv`, `availability.csv`, `changes.csv`, `model_changes.csv`, `change_summary.csv`, `sign_agreement.csv`, `climatology.csv`, `climatology_summary.csv`, `monthly_change_summary.csv`, `member_anomalies.csv`, `trajectory_range.csv`, `variability_member_ratios.csv`, `variability_model_ratios.csv`, `variability_summary.csv`, `analysis_record.json` |
| script | `blueearth_cst/projections/prepare_projection_analysis.py` |
| threads / resources | 1 / `mem_mb = 1024` |
| log / benchmark | `PREPARE_PROJECTION_ANALYSIS = RULES.logged("2.05b", "prepare_projection_analysis", summary=...)` |

Tables are always written (a table for an unavailable product holds its header and zero rows; the record
says why). Figures are not (§ 6.1). `analysis_record.json` holds: both window pairs per horizon (§ 5.5),
requested vs used analysis window and shift flag (§ 5.6), join flag, reference-choice rule, methods (dry rule,
detrending, null band, weights, agreement bands as display heuristics), members per model, family source per
model, unavailable products and members with reasons. 2.05b derives coverage from `points` (the same
`POINTS` records 2.05 turns into `composition.csv`), so it does not depend on 2.05 at all. It reads the series
with 2.05's identity assertion (`series_identity.assert_series_identity`, `derive_change_factors.py:150-160`).

**Rule 2.05 `derive_change_factors`** — arithmetic unchanged. Loses `stats_change_plt`, the
`plot_change_summary` call (`derive_change_factors.py:535`) **and the `figure_names` param**
(`analyze_projections.smk:1197`): `report.md` points to `plots/figure_captions.md` (owned by 2.06) instead of
listing figures, so no future figure change re-runs the change-factor merge (risk-5). `combine_changes` stays
imported from `get_change_climate_proj_summary`, which keeps the hydromt `.raster` accessor registration
intact (`get_change_climate_proj.py:8-17`); an explicit `import hydromt` is added in
`derive_change_factors.py` so the coupling is no longer incidental. 2.05 re-runs **once**, at the commit that
drops its plot output and param; its CSVs must come out byte-identical (§ 5.1).

**Rule 2.06 `plot_climate_projections`** — keeps its name and number; becomes a pure renderer of
`analysis/*.csv` and `analysis_record.json`. Outputs: every path of `figure_relative_paths(..., availability)`,
`plots/figure_captions.md`, `plots/_engine/figure_captions.json`, and captioned copies when opted in. Script
stays `plot_proj_timeseries.py`, rewritten as a thin driver over the new artist module. It no longer reads
`scalar/*.nc` (figures render tables, `analyze_projections.smk:1258-1262`).

**Gather edges and terminal targets.** `gather_logs`/`gather_benchmarks` (`analyze_projections.smk:1324-1361`)
name `CHANGE_FACTOR_CLOUD_PLOT` and `ANNUAL_PRECIPITATION_PLOT`. From commit 4 they also name
`analysis/analysis_record.json` (2.05b's terminal), so 2.05b is scheduled and its log merged; from commit 5b
the two retired plot targets are replaced by `plots/_engine/figure_captions.json` (2.06's terminal) plus the
annual CSV.

**Retired figures:** `overview/annual-{precipitation,temperature}.png`, `overview/change-factor-cloud.png`,
`overview/change-factor-cloud-combined.png`, `windows/<h>/monthly-change-factors.png`. Content survives as F3.4b,
F3.6b and F3.3; aligned monthly numbers remain in the CSV. Retired code: `projection_plots.draw_*`,
`get_change_climate_proj_summary.plot_change_summary`, `plot_proj_timeseries.annual_series` /
`monthly_change_from_table` once no caller remains.

**Config.** The suite is **on by default** (it replaces the figure set). One optional workflow-file key,
mirroring WF0's `diagnostics.captioned_figures` (`climate_analysis/diagnostic_settings.py:12`):

```yaml
# project_config.analyze_projections.template.yml, REPORTING section
#captioned_figures: false    # also write plots/captioned/<folder>/<name>.png with the caption below the image
```

Read with `get_config(my_cfg, "captioned_figures", False, optional=True)`, type-checked as bool like
`subbasin_figures` (`analyze_climate.smk:309-311`). WF2-only, so it lives in the workflow file. No
`advanced_settings.yml` change: the 30-year length, the 1985–2014 fallback reference, the IQR floor, the null
band level and the agreement bands are **named module constants** (§ 5.10).

## 4. Figure contract

`projection_figures.figure_relative_paths(horizons, water_year_start, reference_window, availability)` stays
the single source; it calls `analysis_windows` (§ 5.5–5.6), the same function 2.05b uses, so folder names and
the computed windows cannot disagree.

- `full-period/` — the whole record (independent of horizon).
- `period-<a>-<b>/` — one folder per **distinct analysis window**, `<a>-<b>` its first and last WY label,
  e.g. P0 `mid` 2046–2054 → `period-2036-2065/`. Horizon names appear in captions and in the record, not in
  the path. **Two horizons resolving to the same analysis window** (for example 2071–2090 and 2081–2100, both
  shifted to 2071–2100) share one folder; its captions name both horizons and their configured windows. This
  replaces v1's parse-time refusal (`projection_figures.py:131-136` keeps refusing duplicate *configured*
  windows only), so no valid config is rejected.
- No development ids in filenames or on the image (`DEV_IDS` dropped).

| Id | Path under `plots/` | Count | Drawn when (§ 6.1) |
|---|---|---|---|
| F3.1 | `full-period/availability.png` | 1 | always |
| F3.4 | `full-period/trajectory-{temperature,precipitation}.png` | 2 | ≥ 1 model with the analysis reference |
| F3.4b | `full-period/annual-{temperature,precipitation}.png` | 2 | always |
| F3.2 | `period-<a>-<b>/change-{temperature,precipitation-pct,precipitation-abs}.png` | 3/window | window available |
| F3.3 | `period-<a>-<b>/seasonal-cycle-{temperature,precipitation}.png` | 2/window | window available |
| F3.5a | `period-<a>-<b>/variability-ratio-{temperature-sd,precipitation-cv}.png` | 2/window | window available |
| F3.5c | `period-<a>-<b>/variability-member-ratios.png` | 1/window | ≥ 1 model with ≥ 2 members in some scenario |
| F3.6b | `period-<a>-<b>/change-factor-cloud.png` | 1/window | window available |
| F5.1 | `period-<a>-<b>/sign-agreement.png` | 1/window | ≥ 2 models in some scenario |
| — | `full-period/change-factor-cloud-combined.png` | 0/1 | ≥ 2 distinct analysis windows (G1) |

All available: one window 15 figures; *n* windows 5 + 10·n + 1. Undrawable products are **not declared and
not drawn**; they are listed in `analysis_record.json` `unavailable_products` and in `figure_captions.md`
under "Not produced" with the reason (G1: no placeholder figures).

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
| F3.5a, F3.5c | the no-change band, method and level; ratios inside it are indistinguishable from sampling noise; the band is for a single member (model means of m members vary less); F3.5c weights each member 1/members-of-its-model (dom-3, dom-4) |
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
(values match the lab: `diagnostic_figures.py:25-81` vs `lab:wf0_lab/figures.py:36-58`). The scenario palette
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

   **Mechanism (risk-2's constraint met):** the kernel is **not edited**. 2.05b calls it on the analysis slice,
   then `apply_dry_reference` re-derives every analysis row's flag from the period's reference mean (the
   kernel's `mean` reference companion, or the seasonal function's) and sets status `dry` (absolute change
   kept, relative dropped) accordingly, recomputing a std % change the kernel dropped only on SD grounds from
   the reference and future values it already returned. The aligned CSV keeps the kernel's per-statistic
   rule, documented in the record and in `rule-index.md`. risk-2's alternative (kernel rule everywhere) is
   not adopted: it cannot be applied to CV rows and keeps the meaning mismatch above. Test: a synthetic member
   whose month has reference mean 0.5 mm/day and reference SD 0.05 mm/day → analysis `std` row `ok` with a
   relative value; aligned CSV row flagged and **byte-identical** before/after the change; a month with mean
   0.05 → both flagged.
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
   `figure_relative_paths` and 2.05b.
   - *Far end:* if the centred window extends past the last complete WY of the scenario span, it is shifted
     earlier to end at that WY, keeping 30 WY. January: 2081–2100 → 2071–2100. October start: the last
     complete WY is WY 2099 (Oct 2099–Sep 2100), so the window is WY 2070–2099, folder `period-2070-2099`,
     caption "Oct 2070 – Sep 2100". Requested and used windows and `shifted: true` are recorded and
     captioned. Unavailable only if fewer than 30 complete WY exist in the combined span.
   - *Near end:* a future window starting before the scenario span (e.g. horizon 2015–2030 → 2008–2037) is
     **joined**: per member, the historical run of the same model and member id precedes the scenario run,
     after the calendar-agreement check 2.05 already applies (`derive_change_factors.py:199-216`, reused by
     calling). A member without its historical run is unavailable for that window (recorded). Recorded as
     `joined: true` and captioned. A window that would start before 1950 shifts later symmetrically.
   - *Per-member data ends:* the window is never shifted per member. A member whose series does not cover the
     parse-time window (e.g. a run ending 2099) is unavailable for that window with reason; folder names and
     captions therefore always match the computed window.
7. **No-change sampling band (dom-3).** F3.5a and F3.5c carry the central 90 % interval of the ratio of two
   detrended SDs under no change: `sqrt(F)` with (28, 28) degrees of freedom for 30-WY windows (OLS
   detrending removes 2), ≈ 0.78–1.28. Quantiles come from scipy if it is already importable in the pixi env,
   otherwise from two tabulated constants for n = 30 — no new dependency either way (checked in commit 3). The
   band is for a single member ratio under white noise; autocorrelation widens it; the caption and record say
   so. Method, level and degrees of freedom are recorded. The data-driven variant is deferred (§ 8).
8. **Equal-model weights for pooled member ratios (dom-4).** F3.5c and the pooled rows of
   `variability_summary.csv` weight each member ratio `1 / members_in_its_model` (per scenario), so each model
   carries total weight 1; weighted quantiles on the log scale. Members per model are recorded and captioned.
9. **Sign agreement (dom-6, dom-11, dom-12).** Per cell: `k/n` models whose model-mean change has the
   ensemble-median sign (lab); **plus** `k_fam/n_fam`, where a family's vote is the sign of its models'
   median change and it agrees when that matches the ensemble-median sign; models with no listed or
   provisional family count as their own family (conservative). **Small-change marker:** cells with
   |ensemble median| below the band (temp 0.5 °C, precip 5 %, 0.1 mm/day; `agreement.py:27`) are greyed and
   not coloured blue/red. The bands are recorded and captioned as display heuristics, not detection
   thresholds. No likelihood language. The AR6 "change exceeds internal variability" share is deferred (§ 8).
10. **Constants** (module level, named, docstrings): `ANALYSIS_LENGTH = 30`, `ANALYSIS_REFERENCE = (1985,
    2014)`, `MIN_MODELS_IQR = 10`, `NULL_BAND_LEVEL = 0.90`, agreement bands as above.

## 6. Robustness and availability

| Case | Behaviour |
|---|---|
| Model not in Kuma et al. (2023) table | if its institution (from the catalog entry, lab `inputs.institution_from_catalog_entry`) matches a listed institution with a single family → that family, flagged `provisional` (dom-11); otherwise its own family named after the model, flagged `own`. Country from the institution table or blank. Never raises. |
| Kuma table data | `projections/model_families.csv` (source_id, family, institution, country) from Zenodo 7920408 `models.csv`, with citation header, **only if the record's licence permits redistribution** (checked in commit 2; licence in the file header). Otherwise no vendored table: the 13 P0 mappings stay a code constant with citation, and every other model takes the institution fallback above. |
| Scenario with no resolved member | absent from `POINTS`, so absent from tables and figures; recorded. |
| Model missing a scenario | reductions use models present per cell; `n`, `n_fam` reported. |
| IQR with < 10 models | `iqr_shown = False`; whiskers and median only. |
| Window unavailable for a member (§ 5.6) | member rows `status = unavailable` with reason; models with no available member drop out of that window's reductions. |
| Analysis reference unavailable for a member | member dropped from C3 with reason (the lab raises, `trajectories.py:79-80`; changed). |
| Variable other than precip/temp | analysis covers precip and temp only; others recorded unavailable. |

### 6.1 Declared vs written, without placeholders (risk-1, G1)

Availability is decided **at parse time** by `suite_availability(POINTS, horizons, water_year_start,
reference_window, variables)` from what the DAG already knows: `POINTS` gives (model, scenario, member)
(`analyze_projections.smk:728-730`), `ACQUISITION_WINDOWS` the spans, config the variables. Rules (counts per
scenario; a product is drawn when any scenario qualifies):

| Product | Requirement |
|---|---|
| per-window products F3.2, F3.3, F3.5a, F3.6b | window computable (§ 5.6) and ≥ 1 model |
| F3.5c | ≥ 1 model with ≥ 2 members (per model, not pooled) |
| F5.1 | ≥ 2 models |
| F3.4 | ≥ 1 model; analysis reference inside the historical span |
| combined cloud | ≥ 2 distinct analysis windows |

`figure_relative_paths` declares only available products; 2.05b writes the same availability (with reasons)
into `analysis_record.json`; 2.06 lists the rest under "Not produced". On the smoke configs: rapid (2 models,
1 scenario, 1 member each, `test_case/project_config_rapid_analyze_projections.yml:8-14`) draws 14 figures,
F3.5c not produced; wf2_fast (1 model, `project_config_wf2_fast_analyze_projections.yml:6-11`) draws 13,
F3.5c and F5.1 not produced. Both are unit-tested. **Runtime residue** (a parse-time-available product whose
data turn out empty, e.g. an all-NaN series or every member's run ending early) **raises** in 2.05b with the
product and reason, never writes a blank figure.

## 7. Identity and blast radius

- **WF3/WF4 run ids.** `repository_code_inventory` follows static imports from stage entry points
  (`experiment/content_identity.py:84-130`). No module under `experiment/`, `shared/` or `weathergen/` imports
  `blueearth_cst.projections`; this design edits nothing in `shared/` or `climate_analysis/` (it imports
  `diagnostic_figures`, which WF3/WF4 never reach). Expected: identities unchanged. Falsifier in § 9.
- **Stage B cache.** `STAGE_B_HASH` unchanged under the additive-only rule (§ 2); `REDUCER_HASH` untouched.
- **Baseline manifest (risk-9).** The default gate covers the two CSVs (the byte-identity gate covers them
  better). `check_baseline.py:313-330` lists three retired PNGs as `FIGURE_KINDS` targets; replace them with
  `full-period/annual-precipitation.png` and `period-<a>-<b>/change-factor-cloud.png` (resolved for the
  baseline config). The manifest fingerprints are **not** re-recorded here: the manifest is already stale
  (AGENTS.md) and its re-record belongs to the pending regeneration; until then `--include-figures` reports
  the two new entries as unrecorded, which the commit message and `rule-index.md` note.
- **Retired files in existing trees (risk-10).** 2.06 does not delete files it does not own. The retired paths
  are listed in the WF2 docs page and in `figure_captions.md` ("retired in this version; safe to delete"),
  and added to the tree inventory's retired list if `tests/test_project_tree_inventory.py` / `tree-check`
  carries one (verified in commit 5b; if not, the doc note is the whole remedy).
- **Dry-runs.** `tests/test_cli.py` WF2 dry-runs see one more rule and new paths.
- **Other stale references fixed in the same commits:** `dev/reference/workflows/rule-index.md:881-908`,
  `dev/scripts/console_sample_specs.py:295`, `report.py:162-166`, `projection_figures.py` docstring.

## 8. Alternatives considered

| Choice | Chosen | Alternative | Why not / when it would win |
|---|---|---|---|
| Port shape | Refactor: kernels reused, new modules by concern | Port lab modules as-is | Violates the one-calculator ruling; two windowing implementations would drift. |
| Calculation site | New rule 2.05b, parallel to 2.05 | Fold into 2.05 | 2.05 is the cache-guarded change-factor terminal; plot-table changes would re-run the merge. |
| Figure family | Replace | Extend (keep the five) | Owner reviewed the revised set as the set; no consumer of old paths (`web-app-independence`). |
| Default | On by default | Opt-in key | Replacement makes opt-in mean "no figures"; would win if § 9 timing shows material cost. |
| Tokens | Import from `diagnostic_figures` + smoke test | `shared/figure_tokens.py` | Edits WF0 and `shared/` for no gain now; wins when a third workflow needs them. |
| Unavailable products | Parse-time availability; undeclared, listed | Placeholder figures (v1) / checkpoint | Placeholders ruled out at G1; checkpoints break the static list `rule all`, gather edges and inventory use. |
| Analysis dry rule | Mean-keyed per period, post-process | Kernel per-statistic rule (risk-2) | Cannot cover CV rows; flags variability, not dryness (§ 5.4). |
| Analysis reference | Configured if ≥ 30 WY, else 1985–2014 | Always 1985–2014 (v1) / always configured | Fixed drifts from the stress-test zero point; configured-only gives 15-WY windows on P0. |
| Far horizon | Shift to fit the data end | Unavailable (v1) | Drops the most-used AR6 horizon. |
| Shared window | Merge folders | Refuse at parse time | Refusal rejects a valid config and blocks the overlay CSV too. |
| Null band | Analytic `sqrt(F)` | Paired historical windows per member | Absorbs autocorrelation, but needs a method review and two disjoint 30-WY historical windows; deferred. |
| Agreement noise | Small-change marker on the median | AR6 simple approach | Needs a per-model internal-variability estimate; deferred. |
| HTML page | Not included | Port `report_wf2` | No consumer; third reporting surface. |
| Cloud data | Analysis-window model means | Stage-B merge cloud | Lab-reviewed F3.6b uses the analysis window; keeps figures out of a `derive_` rule. |

## 9. Validation plan

**Pre-change snapshots (before commit 1)**, digests under `dev/tasks/t2610071652/evidence/`, data copies in
the worktree `.tmp/scratchpad/`: change-factor CSVs from rapid (re-run at the lane head; the 2026-09-16 copy
predates the lane's WF2 fixes) and P0 (+ sha256, already taken); lab `results/*.csv` at lab `7560e71`;
`STAGE_B_HASH`, `REDUCER_HASH`, WF3/WF4 inventory digests for rapid.

### 9.1 Lab-parity scope (risk-6)

Under parity on P0 (P0 triggers neither the configured-reference switch, a shift nor a join, and has no dry
cell, so dom-1, dom-2 and dom-5 do not change these values):

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
`analysis_record.json` (new schema). Each excluded item is covered by a known-answer test below. The parity
test maps columns by name and fails on an unmapped column, so an exclusion cannot be silent.

### 9.2 Checks

| Claim | Check | Falsifier |
|---|---|---|
| Aligned CSVs byte-identical | sha256 after the final WF2 run on rapid and P0; synthetic dry case (§ 5.4) | any digest differs |
| Stage B not invalidated | `STAGE_B_HASH` before/after every commit touching `get_change_climate_proj.py` | values differ |
| Lab parity | `tests/test_projection_analysis_parity.py` (local; skips without P0, reason printed) | value outside § 5.2; count/sign mismatch; unmapped column |
| Known answers (dom-7) | (a) linear trend + white noise: `std_detrended` recovers the noise SD within sampling error, `std` does not; (b) stationary series in both windows, many members: median member ratio ≈ 1 and the 5–95 % spread matches the § 5.7 band; (c) symmetric null changes: agreement fraction ≈ 0.5; (d) weighted pooling: a 5-member model at ratio 2 and a 1-member model at 0.5 → weighted median at geometric centre 1; (e) family counts on a hand-built 4-model/2-family case; (f) √2 ratio and hand medians | any outside stated tolerance |
| Windows (risk-3, dom-10) | unit cases: Jan `mid` 2046–2054 → 2036–2065; Jan 2081–2100 → 2071–2100 shifted; Oct 2081–2100 → WY 2070–2099; 2015–2030 → 2008–2037 joined; two horizons merging into one folder; configured reference of 30 WY used vs 15 WY → 1985–2014 | wrong bounds or flags |
| Dry rule (dom-5) | § 5.4 synthetic test | analysis std row flagged, or aligned row changed |
| Unlisted model degrades | synthetic `XYZ/FOO-1` with a listed and an unlisted institution | raise, missing row, wrong flag |
| Availability (risk-1) | `suite_availability` unit tests for the rapid and wf2_fast compositions; WF2 dry-run of both lists exactly the § 6.1 sets | extra or missing path |
| Every declared output written, every written declared | rapid WF2 run, compare `plots/`, `analysis/` to declarations | extra or missing file |
| Runtime residue raises | all-NaN synthetic member for an available product | blank figure or silent drop |
| WF3/WF4 identity unchanged | recompute inventory digests | differ |
| Run time | 2.05b + 2.06 benchmark rows on P0 in `wf2_benchmarks.md` | > 5 min combined (assumed budget, confirm at G2) |
| Figures match lab | render on P0, publish PNGs as an Artifact, owner visual check | owner rejects |

Gates per the AGENTS ladder: focused tests per commit; `pytest tests/test_cli.py` on commits touching the
Snakefile; `pixi run lint`, `format-check`; `test-fast` before merge; `test-full` not required (no `shared/`
or WF3/WF4 `script:` change) unless a § 7 falsifier fires; `test-e2e` WF2 leg before merge.

## 10. Commit plan

Each commit is independently green: its focused checks pass and any rule it adds is scheduled and run.

| # | Lands | Focused checks | Est. |
|---|---|---|---|
| 0 | Evidence snapshots (no code; rapid re-run at the lane head) | digests recorded | 45 min |
| 1 | `get_change_climate_proj`: `analysis_windows`, `analysis_slice` (with join), `get_change_seasonal_clim_proj`, `detrended_std` + unit and window tests; explicit `import hydromt` in `derive_change_factors` | new tests; `test_get_change_climate_proj*.py`; `STAGE_B_HASH` equal | 2.5 h |
| 2 | `projection_coverage.py` + family data (licence checked; vendored CSV or code constant) + provisional/own fallback + tests | unit tests incl. unlisted model | 1.5 h |
| 3 | `projection_analysis.py` (dry rule, reductions, agreement with families and marker, weighted pooling, null band), `projection_trajectories.py` + known-answer tests (a)–(f) | unit + known-answer tests; scipy-or-constant check | 3.5 h |
| 4 | `suite_availability`; rule 2.05b + `prepare_projection_analysis.py` + `analysis_record.json`; **2.05b terminal added to the gather edges**; rule-index entry | `test_cli.py`; dry-run lists 2.05b; rapid WF2 run executes 2.05b; parity test on P0; dry-reference byte test | 3 h |
| 5a | Path grammar (`figure_relative_paths` with availability), artists + captions modules (WF0 tokens, render smoke test), 2.06 repointed to tables, `captioned_figures` key + template. 2.05's old cloud and figure list are still produced; the old 2.06 figures move to 5b's deletion | `test_projection_figures.py`, `test_cli.py`, lint; rapid and wf2_fast runs; render P0 and publish a PNG Artifact | 4 h |
| 5b | Retirement: 2.05 cloud and `figure_names` param, `report.md` link, gather edges to 2.06's terminal, `projection_plots.py` and dead functions, tree inventory, `check_baseline` entries, console spec, docs (retired-path note) | `test_project_tree_inventory.py`, `test_cli.py`, lint; rapid run: 2.05 re-runs once, CSVs byte-identical | 2 h |
| 6 | Batch gates | byte-identity (rapid, P0, synthetic), identity digests, timing, `test-fast`, `test-e2e` | 1.5 h |

Commit 5a's transitional overlap (2.05's old cloud beside the new figures for one commit) keeps 5a and 5b
separately bisectable; old paths live in other folders (`overview/`), so nothing collides.

## 11. Tree and user-facing change inventory

**Repository** (`+` added, `~` changed, `-` removed):

```
blueearth_cst/projections/
~ get_change_climate_proj.py        analysis windows/slice + seasonal/detrended functions (additive only)
~ derive_change_factors.py          no cloud; explicit hydromt import
~ get_change_climate_proj_summary.py   plot_change_summary removed
~ projection_figures.py             availability + window-folder grammar; palette moved here
~ plot_proj_timeseries.py           thin renderer driver over analysis tables
~ report.py                         figure list replaced by a link to plots/figure_captions.md
- projection_plots.py               retired (draw_* replaced)
+ prepare_projection_analysis.py    script: of rule 2.05b
+ projection_analysis.py            change table, dry rule, reductions, agreement, C2, C4, null band
+ projection_trajectories.py        C3 anomalies and range
+ projection_coverage.py            C0 coverage, availability, family fallback
+ projection_suite_figures.py       lab-style artists
+ projection_captions.py            caption text
+ model_families.csv                Kuma et al. (2023) families — only if the licence permits
~ analyze_projections.smk           rule 2.05b; 2.05 param/outputs; 2.06 outputs; gather edges; captioned_figures
~ config/templates/project_config.analyze_projections.template.yml   captioned_figures comment
~ tests/test_projection_figures.py, test_project_tree_inventory.py
+ tests/test_projection_analysis.py, test_projection_windows.py, test_projection_analysis_parity.py
~ dev/reference/workflows/rule-index.md, dev/scripts/check_baseline.py, dev/scripts/console_sample_specs.py
~ docs/ WF2 figure list and retired-path note
```

**Generated** under `<project>/data/climate/projections/<ensemble>/`:

```
summary/…                            unchanged (CSV bytes identical)
report.md                            ~ links plots/figure_captions.md instead of listing figures
+ analysis/*.csv (always written), analysis/analysis_record.json
plots/
- overview/{annual-*,change-factor-cloud*}.png
- windows/<name>-<start>-<end>/monthly-change-factors.png
+ full-period/{availability,trajectory-*,annual-*}.png   [+ change-factor-cloud-combined.png if ≥ 2 windows]
+ period-<a>-<b>/{change-*,seasonal-cycle-*,variability-*,change-factor-cloud,sign-agreement}.png
                                     one folder per distinct analysis window; products drawn per § 6.1
+ figure_captions.md (incl. "Not produced" and retired paths), _engine/figure_captions.json
+ captioned/<folder>/*.png           only with captioned_figures: true
```

| Change | Current | Proposed | Affected / migration |
|---|---|---|---|
| WF2 figure paths | `plots/overview/…`, `plots/windows/<h>/…` | `plots/full-period/…`, `plots/period-<a>-<b>/…` (analysis-window years) | old files remain; listed as retired in docs and `figure_captions.md` |
| Figure set | 5 (+1) | up to 15 for one window (+1 with ≥ 2 windows); unavailable products listed, not drawn | users; docs |
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
- **Assumption:** scipy importable in the pixi env for F quantiles; otherwise tabulated constants (§ 5.7).
- **Assumption:** `POINTS` at parse time lists exactly the members whose series 2.05b reads (the records 2.05
  uses); a mismatch is runtime residue and raises (§ 6.1).
- **To verify in commit 5b:** whether the tree inventory / `tree-check` has a retired-paths list (§ 7).
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
