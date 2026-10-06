---
title: WF2 starter suite proposal
lifecycle: temporary
created: 2026-10-06
updated: 2026-10-06
---

# WF2 starter suite proposal

Recommend a coverage foundation plus six analysis components for CMIP6 projection analysis: changes in means,
seasonal conditions, trajectories, interannual variability, scenario agreement and model sensitivity. Every
component can be computed from artifacts WF2 already retains; the binding constraints are window length and
ensemble size, not missing data plumbing.

Parent: [Scope conceptual workflow improvements](../t2610022259-conceptual-workflow-improvements.md).
Candidate inventory: [WF2 climate projections ideas](wf2-climate-projections-ideas.md). Precedent: [WF0
starter suite proposal](wf0-starter-suite-proposal.md) and the closed `C:/Users/taner/workspace/wf0-lab`.

The owner accepted the suite and settled all six decisions below on 2026-10-06. This is still not an
implementation specification: lab work and later toolbox integration each need their own brief, and toolbox
configuration or output-contract changes remain gated at integration.

## Current WF2 foundation

Inspected 2026-10-06 on `feat/wf2-cmip6-improvements` (from `main` at `e11eaab8`), including the
`test_case/test_local` baseline render (3 models, SSP2-4.5/SSP5-8.5, reference 2000–2014, horizon `mid`
2046–2054).

**Retained data.** `scalar/` holds one monthly basin-average `precip`/`temp` series per (model, scenario,
member): historical 1950–2014, scenarios 2015–2100, native `noleap` calendar where the model uses it. `raw/`
holds the source-grid slices (2 × 2 cells for the baseline basin). `summary/composition.csv` records every
requested combination, its resolution status, reason, series keys and reference-year count.

**Tables.** `cmip6_change_factors_{annual,monthly}.csv` are long tables keyed by model, scenario, member,
horizon, (month,) variable and statistic (`mean`, `median`, `std`; quantiles opt-in and labelled by sample
size), with reference/future values, relative change and status. `report.md` already discloses reference
clipping, alignment with the historical window, the 20-year window floor, the spatial weighting approximation,
the dry-month rule and composition.

**Figures** (single-sourced by `projection_figures.figure_relative_paths`): two annual overviews, the faceted
change-factor cloud, the combined cloud for multi-horizon configs, and one monthly change-factor figure per
horizon.

**Catalog.** The generated CMIP6 catalog lists 67 models with 41–47 models per main SSP (126/245/370/585) and
about 30 (model, scenario) entries with ten or more members. Only monthly (`Amon`) `pr`/`tas` presence is
certified; no daily data and no guaranteed `tasmax`/`tasmin`.

### Assessment against the five topics

- **Changes in means.** The annual ΔT–ΔP cloud and the `mean` rows exist. Missing: seasonal aggregation,
  ensemble summaries per scenario × horizon, and a link between the same model's points under different SSPs.
- **Seasonal conditions.** The monthly figure draws one line per member over a 9-year horizon against a
  15-year reference, so sampling noise dominates: one SSP2-4.5 member shows October +45% and September −21%.
  There is no season view and no reference-versus-future climatology.
- **Interannual variability.** Only the tabled `std` (e.g. GFDL-ESM4 SSP2-4.5 precipitation −27%), computed on
  15 versus 9 annual values without detrending, so the forced trend inflates it. Not defensible as a result.
- **Scenario agreement.** Absent: no sign-agreement count and no paired scenario contrast.
- **Model sensitivity.** Absent: no leave-one-out or common-membership view. Two of the three baseline models
  share an institution (INM).

The annual overview's panel a mainly shows the inter-model offset in absolute rainfall (about 5 versus 9
mm/day); panel b's unsmoothed annual traces obscure the forced signal.

## Lessons carried over from WF0

1. **Development data do not set the analysis scope.** The WF0 2000–2016 record was clarified as a test
   sample. The WF2 seeds are equivalent: two or three models cannot meaningfully exercise agreement or
   sensitivity.
2. **Data fitness first.** WF0's coverage and completeness component was the most useful for interpretation;
   here it becomes a coverage and membership foundation shown beneath every later panel.
3. **Prototype in a standalone lab, then integrate through a separate brief** with a gate on the output
   contract. Report component status as prototype-tested, real-data exercised, or scientifically qualified.
4. **Results tables beside figures**, carrying counts, windows, units and "unavailable, with reason" entries.
5. **Accepted lab figure rules** (wf0-lab `docs/figure-rules.md`, current section;
   `docs/reusable-decisions.md` FIG-001–005): canvas by panel layout, 7/6 pt type, soft plot frame, `a)` panel
   labels, short legends, recoverable captions, and measured CVD checks. These conflict with some WF2
   conventions; see decision 5.

## Proposed starter suite

### Shared calculation core

Every component reads one long per-member change table. Extend the existing change-factor table shape with a
`period` column (annual, four seasons, month) and a `window_kind` column (simulation-aligned, analysis), and
add a detrended standard deviation under its own statistic label. Do not build a parallel calculator. Compute
seasonal and annual precipitation from day-weighted rates or totals with
`calendar_weights.month_length_weights`, never by averaging monthly percentages. Every figure is then an
ensemble reduction of that table.

Small-ensemble display rule: always show individual model/member points; add median and IQR only above a model
count threshold (start at about 10 as a lab heuristic). Call the result ensemble spread, never a confidence
interval. Scenario remains the colour channel; models are identified by annotation or position, not colour.

### C0 — Evidence coverage (foundation)

- **Methods.** Model × scenario × member matrix with resolved/excluded status, reasons, reference-year counts
  and institution.
- **Figure.** Coverage matrix; an "n models / n members" line beneath every later panel.
- **Effort.** Low; reads `composition.csv`.

### C1 — Changes in means

- **Methods.** Paired per-member ΔT (°C) and ΔP (% and mm/day), annual and four seasons, per scenario ×
  horizon. Changes are formed within each model/member before any ensemble reduction.
- **Figure.** Dot strips with every model, the median and the range; facets by season, colour by scenario.
- **Effort.** Low.

### C2 — Seasonal conditions

- **Methods.** Reference and future monthly climatologies per model; monthly change summarized as median and
  range with the individual points.
- **Figure.** Two-panel climatology; a monthly change band alongside the existing monthly figure.
- **Effort.** Low.

### C3 — Trajectories

- **Methods.** Annual anomalies against each model's own reference, smoothed with a declared running mean (for
  example 20 years); endpoints and smoothing length labelled.
- **Figure.** Scenario-faceted fan (median and model range) with faint smoothed individual traces. Complements
  the existing annual overview; the envelope of smoothed means is not annual weather variability.
- **Effort.** Low to moderate.

### C4 — Interannual variability

- **Methods.** Future/reference ratio of the detrended SD of annual and seasonal values; precipitation CV
  where meaningful; reference and future distributions. The forced-response removal is a declared choice with
  its own label. Requires the analysis windows (decision 1).
- **Figure.** Variability-ratio dot plot per model; paired reference/future distribution panels.
- **Effort.** Moderate, mainly the detrending choice and its verification.

### C5 — Scenario agreement

- **Methods.** Fraction of models agreeing with the sign of the ensemble median, with the denominator shown
  and a configurable "small change" band (a heuristic, not the AR6 Atlas method). Paired scenario contrasts on
  a common model set.
- **Figure.** Sign-agreement matrix (variable × period rows, scenario × horizon columns); slope plot linking
  each model across scenarios.
- **Effort.** Low.

### C6 — Model sensitivity

- **Primary reading: dependence of conclusions on ensemble membership.** Leave-one-model-out,
  leave-one-institution-out (institution is already in the model ID, a cheap family proxy), common versus all
  available models, and simulation-aligned versus analysis windows. Sensitivity dot plot for each headline
  median.
- **Secondary reading: local precipitation scaling.** Per-model %ΔP per °C of local ΔT, as a scatter across
  scenarios and horizons. Label it explicitly as neither a global-warming-level nor a climate-sensitivity
  result; global warming levels need global `tas`, which WF2 does not fetch.
- **Effort.** Moderate; mostly reruns of the same reductions.

### Delivery order

Three increments: C0, C1 and C5; then C2 and C3; then C4 and C6. The four existing figures stay unchanged; new
figures are additions, declared through `figure_relative_paths` so the rule outputs, tree inventory and
`check_baseline` stay consistent.

## Deferred, with reasons

- **Spatial coherence and robustness maps.** The baseline basin's raw slice is 2 × 2 cells; this needs a
  deliberately defined regional domain.
- **Daily extremes (ETCCDI).** The catalog certifies only monthly `pr`/`tas`.
- **Global warming levels.** Global `tas` is not fetched.
- **SPI on monthly model precipitation.** Feasible, reusing wf0-lab `spi` and its fit checks against each
  model's own historical calibration; the strongest candidate for the first extension.
- **Model-versus-observation fidelity.** WF2 dropped its observed-source dependency on 2026-08-13 (defect E);
  this would reintroduce a cross-workflow coupling.
- **Later research capabilities.** Uncertainty partitioning, performance/independence weighting, time of
  emergence, physical storylines, bias adjustment and the CST exposure-space overlay.

## Owner decisions (settled 2026-10-06)

The owner accepted the recommendation on every item.

1. **Analysis windows: adopted.** Add a 30-year analysis pair beside the simulation-aligned view: reference
   1985–2014, and 30 years centred on each horizon (2036–2065 for `mid` 2046–2054). C4 uses the analysis pair
   only; C1, C2, C5 and C6 report both window kinds. The aligned view remains the stress-test overlay input.
2. **Lab development ensemble: adopted.** About 12 models from at least 10 institutions ×
   SSP1-2.6/2-4.5/3-7.0/5-8.5, plus three models with five or more members to expose within-model spread.
   The lab picks the concrete list from the catalog against these criteria and records it, along with the
   fetch volume, before analysis begins.
3. **Seasons: adopted.** DJF/MAM/JJA/SON first; basin-defined wet/dry seasons as a configurable follow-up.
4. **Development home: option (b).** A `wf2_lab/` package in the existing wf0-lab, reusing its environment,
   figure tokens, caption mechanism and status ladder, so WF0 and WF2 share one visual language. A new sibling
   `wf2-lab` was not chosen.
5. **Captions: deferred to WF0 integration.** Decide once for both workflows there. Meanwhile the WF2 lab
   follows the accepted lab rule (caption-off by default, recoverable captions); existing WF2 figures keep
   their `supxlabel` caveat.
6. **Output paths: keep WF2's grammar.** New figures extend `overview/…` and `windows/<horizon>/…` through
   `figure_relative_paths`; alignment with WF0's four-field grammar is decided at integration.

## Evidence and status

Recommendations reflect inspection of `analyze_projections.smk`, `projection_figures.py`,
`projection_plots.py`, `get_change_climate_proj.py`, `calendar_weights.py`, the generated CMIP6 catalog, the
baseline and rapid seed configurations, and the `test_case/test_local` WF2 outputs and figures, together with
the wf0-lab integration notes, figure rules and reusable-decision register. No workflow execution, numerical
evaluation or implementation is claimed.
