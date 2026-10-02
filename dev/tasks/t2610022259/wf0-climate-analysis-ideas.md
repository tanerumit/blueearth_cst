---
title: WF0 climate analysis and visualization ideas
lifecycle: temporary
created: 2026-10-02
updated: 2026-10-02
---

# WF0 climate analysis and visualization ideas

Research captured from the 2026-10-02 discussion. Parent: [Scope conceptual workflow improvements](../t2610022259-conceptual-workflow-improvements.md).

These are candidate methods and visualization options, not an approved design or implementation assignment. Preserve useful conclusions in their appropriate maintained home before closing the parent task.

## Purpose and current context

Expand WF0 into a modular, model-independent historical climate diagnostics suite. Its organizing question is: which features of historical climate matter for this basin, how do they vary across scales, and how confidently do available datasets represent them?

The inspected workflow already supports climatological maps, annual series, monthly distributions, and candidate-source comparisons at basin/subbasin scales. Inspection was of the parked session snapshot, not a fresh audit of main; verify these observations during scoping. Relevant entry points are analyze_climate.smk and blueearth_cst/climate_analysis/{climate_figures,plot_climate_source,compare_sources}.py.

The inspected rapid and baseline configs both use 2000–2016. That period supports descriptive diagnostics but provides limited evidence for trends, ENSO relationships and especially decadal variability or long memory. Seek longer reasonably homogeneous analysis records independently of the simulation window. Source-grid PET is currently labeled an approximate diagnostic: review its suitability before using it for SPEI or evaporative-demand trends.

ENSO-related variability is distinct from statistical long-term persistence. The former concerns a physical climate mode and its local associations; the latter concerns slowly decaying dependence across timescales.

## Core diagnostic candidates

| Component | Methods | Visualization options | Scientific conditions |
|---|---|---|---|
| Data fitness and source agreement | Completeness by month/year; valid-area coverage; common-period comparisons of means, quantiles, wet-day frequency and variability | Coverage heatmap; source-by-metric dot plots; monthly differences; Q–Q plots | Agreement is not validation; products can share observations and assumptions. |
| Seasonal climate and water balance | Monthly/pentad climatology; interannual quantile envelopes; rainfall occurrence versus wet-day intensity; seasonal P–PET; dates reaching selected fractions of annual rainfall | Seasonal curves with percentile ribbons; year × month anomalies; cumulative-rainfall curves; water-balance panels | Rainfall-fraction dates describe timing; an onset claim needs a regional definition. |
| Variability across timescales | Standard deviation/IQR at monthly, seasonal and annual scales; precipitation CV where meaningful; variability of 2-, 5- and 10-year averages | Variability versus aggregation scale; annual anomalies; seasonal-total distributions | Overlapping averages are dependent. Avoid CV for Celsius temperature and near-zero precipitation means. |
| Trends and distributional change | Sen slopes; dependence-adjusted uncertainty; seasonal Kendall where appropriate; quantile regression | Effect sizes with confidence intervals; seasonal trend matrix; trend maps; start/end-year sensitivity | Period trends do not establish attribution or extrapolation. |
| Daily precipitation extremes | Rx1day, Rx5day, wet-day frequency, SDII, R95pTOT/R99pTOT, CDD/CWD and relevant threshold counts | Index series; seasonal distributions; maps; duration–magnitude event plots | Preserve standard definitions, fixed thresholds/reference periods and spell-boundary conventions. |
| Temperature extremes | TXx, TNn, TX90p/TN90p, warm-spell duration, frost days and locally relevant thresholds | Exceedance calendars; duration plots; index series; seasonal percentile curves | Tmax/Tmin indices cannot be computed from daily mean temperature. |
| Multiscale drought | SPI at 1/3/6/12/24 months; SPEI where PET is suitable; duration, severity and recovery | Time × accumulation-scale heatmap; drought timeline; severity–duration scatter; affected area | Meteorological/climatic drought is distinct from hydrological drought. Check distribution fits and short-record limitations. |
| Sequencing and short-term persistence | Wet/dry transition probabilities; empirical spell lengths; seasonal anomaly ACF; extreme-event clustering | Spell survival curves; lag × season heatmap; comparison with simple Markov models | Remove the seasonal cycle for anomaly persistence. Pooled statistics can hide seasonal structure. |

Use a selective ETCCDI/Climdex subset [1], including the prescribed bootstrap conventions for applicable percentile-based indices. Trend outputs should emphasize magnitudes and uncertainty. Ordinary Mann–Kendall assumes independence; the Hamed–Rao adjustment [2], suitable block resampling, or explicit error models are alternatives whose assumptions need checking.

SPI [3] isolates precipitation deficits. SPEI [4] incorporates evaporative demand through accumulated P–PET; compare it with SPI and assess PET sensitivity rather than treating either as universal.

## Climate-mode and teleconnection module

Select indices based on basin geography and physical rationale, rather than searching all indices and lags for the strongest correlation.

| Question | Method | Visualization |
|---|---|---|
| Seasonal association | Prespecified seasonal correlations with physically motivated lags | Season × lag heatmap with uncertainty and sample size |
| Phase dependence | El Niño/La Niña/neutral composites of totals, wet-day occurrence, spells and extremes | Composite maps; distributions by phase; difference intervals |
| Event evolution | Align local anomalies around mode development and decay | Event-aligned curves and uncertainty ribbons |
| Temporal stability | Nonoverlapping-period comparisons; descriptive rolling estimates | Association through time, with uncertainty |
| Multiple drivers | Prespecified multivariable regression or partial associations | Coefficient plots and temporally blocked validation summaries |

Resample whole ENSO events or appropriate year blocks, not individual months. Prolonged episodes do not provide independent monthly replicates. Association does not demonstrate causation or prediction; predictive claims require temporally blocked out-of-sample evaluation.

NOAA CPC adopted RONI in February 2026 [5]. Retain the index definition, source and version; compare with conventional Niño-3.4/ONI when historical comparability matters. Consider NAO, IOD, SAM or other modes only where justified.

## Low-frequency variability and long memory

| Level | Method | Visualization | Proposed use |
|---|---|---|---|
| Dependence | Deseasonalized ACF; short-memory models; observed multiyear variability | ACF; variance versus timescale | Routine diagnostic |
| Frequency structure | Multitaper spectrum with background-noise comparison | Spectrum with uncertainty | Optional established method |
| Changing frequency structure | Morlet wavelet analysis | Power, global spectrum and cone of influence | Optional exploratory analysis |
| Changing teleconnection | Wavelet coherence between local climate and an index | Coherence, phase and edge masking | Advanced exploratory analysis |
| Long-memory inference | Compare short-memory, trend/change-point and long-memory alternatives; support with DFA, aggregation scaling or suitable Hurst estimators | Scaling curves with simulation envelopes; model comparison | Research extension |

Wavelets require explicit edge treatment and appropriate null-model significance [6, 7]. Coherence does not demonstrate causality. A Hurst map should not be a default output: apparent scaling may reflect trends, shifts, short-memory behavior or finite samples. A straight DFA fit is not sufficient evidence of long memory [8]. Examine whether the interpretation survives plausible alternative models.

## Temporal and spatial scale choices

Offer calendar years, water years and locally relevant seasons. Distinguish accumulation scale from reporting frequency: monthly SPI-12 values are highly overlapping, not independent observations.

Spatial supports should be named explicitly:

- Native grid cells: local climatology, trends and extreme indices.
- Subbasins: contrasting or synchronous tributary-region anomalies.
- Whole basin: integrated climate inputs and water availability.
- Elevation bands/climatic zones: terrain-linked seasonality and warming where resolved.
- Larger regional domain: context for coherent variability and teleconnections.

An index of a spatial average differs from a spatial average of local indices. The maximum daily basin-average precipitation describes one coherent basin event; the area-weighted average of cell maxima can combine events from different days. Keep these estimands separate and retain area/fractional-cell weighting.

Add affected-area curves and duration–area–severity summaries for drought, heat and heavy rain. Analyze subbasin anomaly correlations, simultaneous events and correlation versus separation distance.

Regional EOF/PCA is optional where the domain resolves enough spatial variability. Show area-weighted loadings, principal components and explained variance; assess domain and standardization sensitivity. EOFs are statistical patterns, not automatically physical modes [9]. One- or two-cell basins do not support detailed spatial inference; interpolation adds no information.

## Selective extensions

### Extreme-value frequency analysis

Compare GEV block maxima and generalized Pareto peaks over threshold (POT). Block maxima are simpler but discard events; POT uses more events but requires threshold selection and declustering. Show empirical positions, return-level uncertainty, fit diagnostics and threshold sensitivity.

Start with stationary fits. Covariate-dependent models require record support and physical rationale; describe their return levels as conditional on covariates. Avoid presenting uncertain long-period extrapolation as a dependable design value [10].

### Compound and sequential events

Begin with empirical joint occurrence: hot–dry periods, heavy rain after wet antecedent conditions, and spatially widespread drought. Use joint-distribution plots, timelines and affected-area summaries. Specify simultaneous AND/OR exceedance or event sequencing before reporting probability. Copulas and multivariate extreme-value models are later options, guided by a clear compound-event definition [11].

## Scientific safeguards

1. Separate analysis-record length from the simulation window; use common overlap for source comparisons and longer individual records where appropriate.
2. Fix anomaly/threshold reference periods. Use 1991–2020 where supported; label alternatives. A 30-year normal is a convention, not proof of adequate inferential power [12].
3. Retain variable, calendar, aggregation, spatial-support and reference-period definitions with each result.
4. Investigate apparent discontinuities against station/product metadata before interpreting climate shifts or applying homogenization.
5. Address serial dependence and multiplicity. Map effect sizes and uncertainty; use suitable false-discovery-rate or field-level procedures when displaying significance [13].
6. Display source, dates, spatial support, temporal scale and valid sample size. Distinguish interannual percentile envelopes from confidence intervals.
7. Do not infer hydrological impacts from climate indices alone, or treat correlated source products as independent truth.
8. Treat insufficient data as a reason to withhold or qualify inference, rather than silently compute every configured diagnostic.

## Proposed priorities and open decisions

1. Core: coverage, seasonality, source disagreement, anomalies, daily extremes, SPI, spells and dependence-aware trends.
2. Basin interpretation: spatial coherence, affected area, relevant climate-mode composites and defensible SPEI.
3. Research extensions: spectra/wavelets, extreme-value fits, regional EOFs, compound-event models and long-memory comparison.

Most core methods are established; automated nonstationary and multivariate analyses require case-specific checks. General causal discovery or definitive long-memory inference from short records is not a justified default.

Potential downstream use: the same empirical diagnostics could later assess whether WF3 reproduces seasonality, spells, spatial coherence, drought duration and multiyear variability. This is a candidate connection, not a change to the bottom-up CST method or a coupling to CMIP-driven generation.

Next scoping decisions: target basin questions; available variables and observational reference data; historical coverage; PET method; supported scales; default versus advanced modules; acceptable runtime; output/report format.

Coordinate with [the existing forcing-selection evaluation task](../t2608181139-give-wf0-its-forcing-selection-evaluation-layer-rules-0-07-0-09.md), which owns observation comparison and Budyko screening and already mentions optional SPI/dry-day/heat-day indices. Preserve its identity; resolve overlap before implementation. The new task captures conceptual scope rather than replacing that work.

## Sources

Research links retained from the discussion; recheck definitions and product versions when scoping implementation.

1. [Climdex/ETCCDI index definitions](https://www.climdex.org/learn/indices/).
2. [Hamed and Rao (1998), modified Mann–Kendall for autocorrelated data](https://doi.org/10.1016/S0022-1694(97)00125-X).
3. [WMO (2012), Standardized Precipitation Index User Guide](https://digitalcommons.unl.edu/droughtfacpub/209/).
4. [Vicente-Serrano et al. (2010), SPEI](https://journals.ametsoc.org/view/journals/clim/23/7/2009jcli2909.1.xml).
5. [NOAA CPC (2026), adoption of RONI](https://www.cpc.ncep.noaa.gov/products/analysis_monitoring/enso/roni/announcement.php).
6. [Torrence and Compo (1998), practical guide to wavelet analysis](https://psl.noaa.gov/people/gilbert.p.compo/Torrence_compo1998.pdf).
7. [Grinsted et al. (2004), cross-wavelet and wavelet coherence](https://npg.copernicus.org/articles/11/561/2004/).
8. [Maraun, Rust and Timmer (2004), interpreting DFA results](https://npg.copernicus.org/articles/11/495/2004/).
9. [NCAR Climate Data Guide, EOF and rotated EOF analysis](https://climatedataguide.ucar.edu/climate-tools/empirical-orthogonal-function-eof-analysis-and-rotated-eof-analysis).
10. [Slater et al. (2021), nonstationary weather and water extremes](https://hess.copernicus.org/articles/25/3897/2021/).
11. [Zscheischler et al. (2020), compound-event typology](https://www.nature.com/articles/s43017-020-0060-z).
12. [WMO climatological normals](https://wmo.int/wmo-climatological-normals).
13. [Wilks (2016), multiplicity and significance stippling](https://barnes.atmos.colostate.edu/COURSES/AT655_S17/references/Wilks_2016_BAMS.pdf).
