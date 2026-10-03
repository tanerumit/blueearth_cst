---
title: WF0 starter suite proposal
lifecycle: temporary
created: 2026-10-03
updated: 2026-10-03
---

# WF0 starter suite proposal

Recommend six core diagnostic components for model-independent historical climate analysis and forcing-source comparison, plus a small optional view of joint warm and dry conditions. The suite prioritizes useful basin interpretation, established implementations, and room for later expansion.

Parent: [Scope conceptual workflow improvements](../t2610022259-conceptual-workflow-improvements.md). Candidate inventory: [WF0 climate analysis and visualization ideas](wf0-climate-analysis-ideas.md).

Execution handoffs: [Create the standalone lab](wf0-lab-setup-instructions.md), then [implement the starter suite](wf0-starter-suite-task-brief.md). These are future execution assignments; no lab setup or implementation has been performed here.

This is an initial recommendation, not an approved implementation specification. Saving it does not approve methods, configuration changes, or implementation work.

## Analysis scope and development data

The user clarified that the 2000–2016 record in the current configurations is a testing and development sample. Actual analyses will use longer historical records. The sample must not determine the product's analytical scope or be treated as the intended production record.

Accordingly, SPI and robust trend analysis belong in the starter suite. Their eligibility and interpretation depend on the actual supplied record: completeness, length, homogeneity, reference-period coverage, and diagnostic adequacy. A longer record improves the basis for inference but does not by itself establish adequacy.

The development sample can exercise calculation, plotting, and insufficient-data handling. Scientific verification of distribution fitting and trend uncertainty needs suitable longer records and controlled examples. Historical analysis coverage should be considered independently of the simulation window; the configuration mechanism remains an implementation decision.

## Recommended core suite

| Component | Initial methods | Main visualization | Value and implementation burden |
|---|---|---|---|
| 1. Data fitness and source agreement | Coverage and completeness by month/year; contributing-cell counts; common-period comparison of totals, wet-day frequency, intensity, and variability | Coverage heatmap and source-by-metric dot plots | Highest priority for interpreting forcing choices. Moderate effort; reuse metrics from the other components. |
| 2. Seasonality and rainfall timing | Monthly precipitation and temperature climatology; interannual variability; wet-day frequency versus intensity; dates reaching 25%, 50%, and 75% of annual rainfall | Seasonal curves with percentile ribbons and rainfall-timing plots | Explains differences in amount, occurrence, intensity, and timing. Low to moderate effort using existing aggregations. |
| 3. Anomalies and multiscale drought | Monthly anomalies; SPI-3, SPI-6, and SPI-12; drought duration and accumulated severity | Anomaly calendar, time × accumulation-scale SPI heatmap, and event summary | Makes persistent deficits visible at several relevant scales. Moderate effort, including fitting and reference-period checks. |
| 4. Rainfall extremes | Rx1day, Rx5day, SDII, and wet-day frequency | Annual small multiples and source comparisons | Compact standard subset derived from existing daily precipitation. Moderate effort, mainly conventions and missing-data handling. |
| 5. Sequencing and persistence | Wet/dry spell distributions, seasonal transition probabilities, longest dry spells, and deseasonalized monthly anomaly autocorrelation | Spell exceedance curves and compact lag plots | Captures information concealed by totals and supports eventual weather-generator evaluation. Moderate effort; share occurrence/spell calculations with component 4. |
| 6. Trends and change | Annual/seasonal Sen slopes, dependence-aware uncertainty, and start/end-period sensitivity | Slope-and-interval plots with supporting time series | Improves the existing descriptive trend capability. Moderate effort, with uncertainty treatment requiring more care than slope calculation. |

Use standard [Climdex definitions](https://www.climdex.org/learn/indices/) for rainfall indices, including the usual 1 mm/day wet-day threshold. Define handling of missing days, reporting-period boundaries, and spells crossing those boundaries before implementation. Rainfall-fraction dates describe seasonal timing; they do not establish monsoon onset.

For SPI, use a fixed, documented calibration period, check fits and zero-precipitation handling, and report unavailable outputs with reasons. A 30+ year calibration record is a sensible initial eligibility target informed by the [WMO SPI User Guide](https://www.droughtmanagement.info/literature/WMO_standardized_precipitation_index_user_guide_en_2012.pdf), followed by suitability checks. Define drought event onset, termination, and severity explicitly. Accumulated precipitation anomalies remain a descriptive fallback when SPI is unsuitable; do not assign them SPI categories or calibrated rarity claims.

For trends, implement Sen slopes together with justified dependence-aware uncertainty and period sensitivity. The current annual figures already show descriptive OLS slopes without significance claims. Replacing the slope estimator alone would provide limited benefit. Select and verify the uncertainty procedure during implementation design; neither ordinary independent resampling nor a default slope interval should be assumed to handle serial dependence. Avoid default significance maps.

## Optional compound climate view

Add a seasonal temperature–precipitation scatterplot using paired anomalies, with selected historical seasons labelled. Facet by season and retain the temperature and precipitation source identities, especially where temperature is borrowed from another forcing product.

This is the preferred inexpensive entry into compound-climate interpretation. Begin with observed joint conditions; event thresholds and empirical occurrence summaries can follow a defined basin question and adequate sample support. Do not infer joint return periods from the scatterplot. [Bevacqua et al. (2022)](https://www.nature.com/articles/s41558-022-01309-5) illustrates the relevance of concurrent hot and dry conditions and the substantial sampling uncertainty in their frequencies.

## Visualization and implementation approach

Most numerical methods above are established. Favor modern improvements through event diagnostics, joint-variable interpretation, and clearer displays of variability and uncertainty. A cosmetic refresh alone would add little analytical capability; a full research suite would add disproportionate methodological and maintenance burden.

Use heatmaps for timing and persistence, small multiples for indices and source comparisons, empirical curves for distributions, and percentile ribbons for seasonality. Clearly distinguish interannual percentile envelopes from confidence intervals. Preserve useful existing maps, annual series, and monthly distributions; avoid duplicating them with charts answering the same question.

Start with basin summaries and selected subbasins. Each component should expose reusable numeric results alongside static figures, with source, period, spatial support, calendar, units, reference period, and valid sample counts. Keep unsupported diagnostics visibly unavailable rather than silently dropping them. A web application or interactive dashboard is unnecessary for this first implementation.

The repository already declares xclim, SciPy, Matplotlib, and Seaborn. Reuse existing capabilities before adding dependencies or implementing standard indices manually. The [xclim indicator layer](https://xclim.readthedocs.io/en/stable/apidoc/xclim.core.html) provides input checks, missing-value handling, and output metadata; verify compatibility with the installed version and project conventions.

## Repository boundaries

- Current WF0 deliberately gives equal weight to cells intersecting the basin, matching the weather generator. Preserve and label that spatial support. The candidate inventory's fractional-area weighting suggestion requires a separate methodological and compatibility decision.
- An extreme index computed from the basin-average daily series differs from an average of cell-level indices. Name the selected quantity explicitly; the initial basin diagnostics should keep these interpretations distinct.
- WF0 and WF1 share source-plot machinery. Give new WF0 diagnostics explicit ownership and assess effects on WF1 before changing shared reductions or canonical figure outputs.
- Completeness checks should use expected calendar dates and explicit missing-value rules. Existing aggregation filters are not a substitute for a consistent diagnostic data-fitness policy.
- The [existing forcing-evaluation task](../t2608181139-give-wf0-its-forcing-selection-evaluation-layer-rules-0-07-0-09.md) retains observation comparison and Budyko screening. Resolve ownership of its overlapping SPI/dry-day/heat-day ideas before implementation. Its historical rule-number and configuration references need refreshing before use.
- Source agreement is not validation. Independent observations remain necessary to assess source accuracy. Climate diagnostics alone do not establish hydrological impacts.
- Reusable empirical metrics may later assess WF3 seasonality, extremes, and persistence. This does not change scenario-neutral CST or make projections drive generation.

## Delivery order and later extensions

Implement the six core components in three increments: fitness and seasonality; anomalies/SPI and rainfall extremes; sequencing and trends. Add the optional compound-climate panel when those shared calculations are available. These increments define delivery order, not a reason to exclude SPI or trends from the initial suite.

Prioritize later extensions as follows:

1. Spatial coherence and affected-area summaries where grid resolution supports meaningful spatial inference; physically justified climate-mode composites and multiyear variability where record coverage supports them.
2. SPEI and stronger P–PET interpretation after checking PET suitability. Source-grid PET is currently an approximate diagnostic.
3. Tmax/Tmin extremes when those variables are available; broader percentile-based rainfall indices once reference-period conventions are established.
4. Wavelets/coherence, EOF/PCA, long-memory inference, fitted extreme-value models, and copulas only for a defined analysis need with suitable data and validation.

Before implementation, resolve the analysis/reference-period configuration, diagnostic eligibility rules, seasonal and water-year conventions, drought/spell definitions, trend uncertainty method, and ownership of reusable metrics. These are focused design decisions; they do not reopen the clarified distinction between development fixtures and production analysis records.

## Evidence and status

Recommendations reflect inspection of the current WF0 Snakefile, climate_figures.py, compare_sources.py, plot_climate_source.py, grid_cells.py, extraction weighting contract, configurations, and declared dependencies, together with the linked method references. The proposal incorporates the user's clarification about development data. No workflow execution, numerical validation, or implementation is claimed.
