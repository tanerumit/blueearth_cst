---
title: WF2 climate projections analysis and uncertainty ideas
lifecycle: temporary
created: 2026-10-02
updated: 2026-10-02
---

# WF2 climate projections analysis and uncertainty ideas

Research note for [Scope conceptual workflow improvements](../t2610022259-conceptual-workflow-improvements.md), prepared 2026-10-02. Companion: [WF0 climate analysis ideas](wf0-climate-analysis-ideas.md).

Status: candidate scientific methods and visualizations, not an approved design or implementation assignment. Recommendations below are a synthesis of the cited literature and repository inspection. No projection run or numerical evaluation was performed. Promote retained conclusions before closing the parent task.

## 1. Purpose and recommendation

Build a modular suite answering four questions:

1. What changes in climate magnitude, seasonality, variability and extremes are projected?
2. How do these changes depend on scenario, time horizon, warming level and spatial support?
3. Which conclusions are shared across models, and which depend on ensemble membership, internal variability or processing choices?
4. How do the projected changes sit within the independently constructed CST exposure space?

Prioritize transparent seasonal and ensemble diagnostics before elaborate uncertainty models. Retain projections as a plausibility overlay: they do not select the weather-generator experiments or delimit the vulnerability search. Decision scaling provides the methodological connection [S13].

Keep three distinct products visible: individual model/member outcomes; summaries conditional on a specified ensemble and scenario; and sensitivity or uncertainty estimates with their assumptions. A CMIP ensemble is not a random, independent sample of all possible climates. Its percentiles do not automatically constitute calibrated probabilities or bound total uncertainty [S1, S4].

## 2. Current WF2 foundation and constraints

Inspected in the primary checkout at commit 8e4a4faf:

- analyze_projections.smk, projection_figures.py and projection_plots.py: annual precipitation/temperature overviews, paired change-factor clouds, and monthly change-factor figures per horizon already exist.
- get_stats_climate_proj.py and the generated CMIP6 catalog: the present pr/tas inputs use monthly Amon data. Monthly series can describe interannual variations in monthly climate; they cannot recover daily heatwaves, wet-day frequency or Rx1day.
- get_change_climate_proj.py: mean, median and standard-deviation statistics already exist, with opt-in quantiles labeled by sample size. Expanding uncertainty interpretation should build on these rather than duplicate them.
- resolution.py, reference_window.py, dry_month.py and report.py: WF2 already records unresolved combinations, reference-window clipping/alignment and dry-month safeguards. The current reference uses historical experiments ending in 2014; it clips rather than silently splicing a scenario into the reference.
- Raw source-grid basin slices are retained. Former derived gridded-output options were removed; spatial diagnostics would need deliberate derivation from retained raw data, not revival of an obsolete configuration switch.
- The rapid seed requests two models and SSP2-4.5; the baseline seed requests three models and SSP2-4.5/SSP5-8.5. Both prefer r1i1p1f1, use 2000–2014 as reference and 2046–2054 as the future window. Actual resolved membership must come from the run composition record.

These are development configurations, not an adequate default research ensemble. A 15-year reference and nine-year future period yield noisy local change estimates, especially for precipitation variability and tails. Two baseline models are from the same modeling center; report lineage and test dependence rather than treating three names as three independent samples.

Recommend longer analysis windows, normally exploring 20- and 30-year summaries where coverage allows. Keep the exact simulation-aligned window as a separate decision-context view. A longer window reduces sampling noise but averages over a changing climate; neither length is universally correct.

A 1995–2014 historical baseline is one useful AR6-compatible option. A 1991–2020 baseline crosses the historical/scenario boundary and therefore requires an explicit methodological decision outside today's clipping contract. Local anomaly baselines and the 1850–1900 baseline for global warming levels serve different purposes [S2, S7].

## 3. Core suite using monthly data

| Question | Candidate analysis | Recommended visualization | Conditions |
|---|---|---|---|
| What data support each result? | Model × scenario × member × variable × period availability; valid years; exclusions and lineage | Coverage matrix; contributor counts beneath every panel | Show requested, resolved and excluded combinations, with reasons. |
| How much do mean conditions change? | Each member's temperature difference, precipitation absolute difference and relative change; annual and seasonal summaries | Individual points with median/IQR; scenario–horizon interval plots | Calculate paired changes within a model/member before ensemble reduction. Ratios of ensemble means answer a different question. |
| Does the seasonal cycle change? | Monthly changes; fixed local wet/dry seasons; seasonal contribution to annual rainfall; seasonal temperature contrast | Monthly change curves; season × horizon heatmap; reference/future climatology panels | Preserve seasons across comparison periods. Explicitly distinguish changes in season timing from changes within fixed seasons. |
| How do trajectories develop? | Annual anomalies and prespecified running means; model-specific trajectories | Scenario-faceted fan charts with faint individual traces | Label smoothing length, endpoints and ensemble composition. An envelope of smoothed means is not annual weather variability. |
| Does interannual variability change? | SD/IQR changes, precipitation CV where meaningful, quantile shifts and anomaly persistence | Reference/future distribution panels; variability-ratio plots; lag profiles | Report both total variability and variability after a documented forced-response removal where feasible. Trends can inflate SD. |
| Are temperature and precipitation changes coupled? | Retain paired changes by model/member, season, scenario and horizon | Delta-T versus delta-P clouds; connected horizon trajectories; seasonal facets | Do not combine marginal hot and dry quantiles into an invented joint projection. Density contours require much more than two or three models. |
| How do scenarios differ? | Within-model contrasts across available scenarios; compare on common membership | Paired slope plots; distributions of scenario differences | A matched member label is not proof of identical future internal variability. Scenario differences remain noisy. |
| How sensitive are conclusions? | Alternative reference/window lengths, common versus all-available models, leave-one-model/family-out summaries | Sensitivity dot plots; sign-stability matrix; membership counts | Call this sensitivity of the selected analysis, not a complete uncertainty distribution. |

Use temperature differences in degrees; precipitation differences in mm/day or period totals plus percent changes. Compute seasonal/annual precipitation changes from properly weighted totals or rates, not an unweighted average of monthly percentages. Preserve native-calendar day weights and complete water-year conventions.

Retain the existing dry-reference guard: show absolute changes where relative changes are unreportable. A ratio is meaningful only for an appropriate quantity and denominator; do not automatically reuse a mean-change convention for every variability statistic.

For small ensembles, show every point and the range. Smooth violins and elaborate quantile fans imply unsupported distributional detail. With richer ensembles, show median, IQR and explicitly labeled outer percentiles as descriptive summaries, including counts and weighting.

## 4. Quantifying uncertainty without conflating sources

### 4.1 An uncertainty inventory

| Source | What can estimate or probe it? | Useful display | What it does not establish |
|---|---|---|---|
| Internal climate variability | Multiple initial-condition members of the same model/forcing; suitable large ensembles; control-run segments as a baseline alternative | Member distributions within each model; scale-dependent variability intervals | One selected member cannot cleanly separate forced response from internal variability. Control variability need not equal future variability. |
| Differences in modeled forced response | Across-model comparisons of member-averaged responses, with residual finite-member uncertainty | Model means with within-model intervals | With one member, between-model spread includes internal variability. |
| Scenario dependence | Scenario contrasts on a common model set and time horizon | Separate scenario panels and paired differences | Scenario frequency in the archive is not scenario probability. |
| Finite-record estimation | Dependence-aware block resampling or model-based sampling within reference/future records | Interval on each estimated change; sensitivity to block/window length | Resampling does not create missing climate modes or estimate structural model error. |
| Ensemble composition/dependence | Common-support comparisons; leave-family-out sensitivity; justified weighting | Unweighted/family-sensitive results; weight concentration plot | Many related models do not provide equivalent independent evidence. |
| Observations, downscaling and bias adjustment | Matched GCM/member experiments varying observation product, RCM or adjustment method | Paired processing differences; GCM × method matrices | Differences among unmatched products cannot be attributed solely to processing. |
| Unrepresented processes and deep uncertainty | Process evidence, alternative physical storylines, external assessments | Explicit evidence gaps and storyline panels | A selected ensemble's min–max is not a bound on physically possible outcomes. |

The first three categories follow the conventional projection-uncertainty framework [S1, S3, S14]. The additional rows are recommended explicitly for this workflow because users may otherwise read the ensemble range as comprehensive.

### 4.2 Ensemble hierarchy and weighting

As a transparent reference, assign equal total weight to each model within each scenario; if retaining multiple members, divide that model's weight among its members. For forced-response summaries, summarize members within model first, then summarize model responses. For the distribution of individual simulated outcomes, retain member spread under model-balanced weights. These are different estimands and must have different labels.

Equal-model weighting still ignores family dependence. Compare it with a documented family-aware sensitivity analysis. Performance-and-independence methods such as ClimWIP are optional: select diagnostics related to the target process, examine sensitivity to observations and tuning, and test out of sample or with held-out model families. Global-temperature weighting results cannot simply be transferred to local precipitation extremes [S4, S5].

If weights are used, show them and their concentration. The index 1/sum(w^2) measures concentration for normalized weights, not the number of physically independent climate models. Do not remove inconvenient high-warming or dry models solely because they are outliers; assess physical credibility and show selection sensitivity.

### 4.3 Formal partitioning: a later capability

With a sufficiently replicated model × scenario × initial-condition design, estimate components using a documented hierarchical model or variance decomposition, retaining relevant interactions and finite-member effects. Use balanced subsets where feasible; explain the missing-cell assumptions for unbalanced designs.

Display absolute variance components in squared physical units alongside fractional contributions. Scenario components depend on the scenarios and weights chosen for the calculation, not on known probabilities of societal futures. Present residual/interaction components rather than forcing everything into three clean bins.

Hawkins–Sutton-style fitting is an established starting point, but smoothing a single realization can assign internal variability to forced response. Lehner et al. show why this can bias regional partitions and why multiple large ensembles are valuable [S3, S14]. For today's small seeds, use an uncertainty inventory and sensitivity analysis; mark unavailable components as not estimable, not zero.

### 4.4 Sampling intervals and language

Resample suitable blocks of complete years within each model/member and period, preserving seasonality and joint variables/locations. Estimate uncertainty in the reference as well as the future; use a shared reference draw across horizon comparisons when that reference is shared. Where a strong forced trajectory invalidates stationarity, resample suitable residuals or use a specified time-varying model. Vary block length and disclose poor support for long dependence.

These are proposed inferential approaches, not a claim that a particular bootstrap is validated for WF2. Simulation checks and model assumptions must be selected during later scoping.

Use distinct labels for:

- Ensemble spread: descriptive differences among included projections.
- Sampling interval: estimation uncertainty under a specified resampling/error model.
- Within-model member spread: simulated internal variability conditional on that model.
- Scenario contrast: difference conditional on named forcing pathways.

Avoid a generic “95% confidence band” around an ensemble median.

## 5. Robustness, detectability and warming-level views

### Agreement and robustness

Compute the fraction of model-level changes with the same sign, report the denominator and test sensitivity to weak changes, family dependence and membership. Agreement is not the probability that the sign is correct, nor automatically a calibrated IPCC confidence statement.

For regional maps, distinguish robust change, weak signal, conflicting signs and insufficient coverage. The AR6 Atlas offers a simple sign-agreement display and a stronger method incorporating internal variability; implement its exact definitions only when its inputs are available [S2]. Three agreeing models should remain visibly a three-model result.

### Time of emergence

Optionally define emergence as a prespecified smoothed forced signal exceeding a baseline-noise threshold and satisfying a declared persistence criterion. Show the distribution across models/members and sensitivity to noise definition, smoothing and reference period [S6].

Noise must match the statistic: a 20-year mean requires the variability of comparable means, not annual SD. Report “not emerged within available period” separately from missing/insufficient data, and retain it when summarizing crossing times. Emergence is not a deadline for adaptation or a prediction of a particular observed year.

### Global warming levels

Complement calendar horizons with regional changes at selected global warming levels, using each model/member's global annual temperature trajectory and an explicit crossing/window rule. This requires additional global data; basin temperature cannot stand in for global warming. A documented 20-year crossing convention is one established option [S7].

Show local change versus warming level, arrival-time distributions conditional on scenario, and contributing-model counts. Compare all available contributors with a common subset. Never count non-reaching members as zero change or silently drop them from arrival-time summaries. Rising, stabilized and post-overshoot climates at the same global temperature can differ; label pathway and crossing direction.

Warming-level framing helps distinguish global warming magnitude from regional response, but it does not eliminate regional model uncertainty or make all pathways interchangeable.

## 6. Data-dependent extensions

| Extension | Recommended methods and figures | Required additions and limits |
|---|---|---|
| Daily extremes | ETCCDI subset: Rx1day/Rx5day, wet-day intensity, CDD/CWD, TXx/TNn, percentile exceedances and warm spells; change-by-index panels and seasonal distributions [S8] | Daily precipitation and, for relevant heat indices, Tmax/Tmin. Monthly tas/pr cannot supply them. |
| Extreme-event frequency | Change in occurrence of a fixed historical threshold; optional GEV/GPD fits; return-level and frequency-ratio plots | Long enough event samples, declustering/threshold checks and fit uncertainty. Zero sampled historical exceedances make empirical ratios undefined. Use the probability difference as an additional summary. |
| Drought and climatic water balance | SPI across accumulation scales; SPEI and P–PET where PET is defensible; duration/severity and affected-area changes | Longer monthly records and additional PET inputs/method assessment. Hold historical standardization fixed when asking about change relative to historical climate [S11]. Refit future distributions only for a separately labeled future-relative question. |
| Compound events and sequencing | Hot–dry and wet-antecedent/heavy-rain occurrence; changes in spatial concurrence; event timelines and joint plots | Joint time series with consistent processing. Bias adjustment of marginal distributions alone does not establish correct dependence. |
| Season timing | Rainfall-fraction dates from monthly data; daily onset/cessation and season length when available | Regional onset definitions and sensitivity checks; monthly data cannot resolve individual rain-event onset. |
| Climate-mode influence | Compare historical/future seasonal associations and event composites for geographically relevant modes | SST/pressure fields or verified model-specific indices, longer records and multiple members. Future ENSO event dates are not synchronized with observations or other models. |
| Snow and evaporative demand | Snowfall/rainfall partition, freezing conditions and demand-related changes | Additional variables and defensible process definitions. Air temperature alone is inadequate evidence for changes in snow storage or actual evapotranspiration. |

Fixed historical thresholds reveal changing exposure to historically unusual conditions. Future-relative percentiles answer a different question. Historical model-relative thresholds are useful for relative change, but real-world absolute impact thresholds require careful treatment of baseline bias. For drought, compare SPI and SPEI to expose the role of evaporative demand, without interpreting either directly as runoff drought.

## 7. Spatial scale and processing choices

Retain native-grid basin/subbasin reductions for integrated quantities. Add a surrounding regional domain only where it answers an explicit context question. A coarse GCM cannot resolve detailed within-basin or elevation structure; finer rendering is not downscaling.

For ensemble maps, use a documented common support, appropriate regridding and contributor counts. A conservative remapping is a candidate for area-integrated precipitation, with coverage/mask checks. The chosen order matters: calculating a daily extreme after regridding differs from regridding an extreme-index field. State which estimand the map represents.

Do not conflate cell-level changes with basin-average changes or average local maxima occurring on different days into a coherent basin event. Show area fractions exceeding a threshold and basin/subbasin contrasts where resolution permits.

Maintain raw and processed products as identifiable alternatives. Bias adjustment can improve selected historical statistics but cannot repair missing physics or guarantee future accuracy [S9]. Trend-preserving approaches such as ISIMIP3BASD are useful options when their assumptions fit; “trend preserving” refers to specified statistics, not every joint property [S10]. Never double-adjust an already adjusted product. Use matched experiments to assess sensitivity to observational reference, adjustment method and downscaling.

## 8. A concise visualization suite

Proposed report sequence:

1. Evidence coverage: availability matrix, model/member counts, windows and exclusions.
2. Seasonal change: monthly/seasonal changes with points and descriptive intervals.
3. Trajectory and horizon comparison: smoothed series plus consistent horizon summaries.
4. Joint climate change: paired temperature–precipitation clouds, including season-specific views.
5. Uncertainty: within/between-model displays where identifiable; membership/window sensitivity elsewhere.
6. Spatial coherence: regional/subbasin changes with coverage and qualified robustness.
7. Optional extremes/drought: compact index changes and event-oriented summaries.
8. Decision context: projection points on the independently defined CST exposure space.

Keep scenario colors consistent with the current WF2 family. Use facets and annotations for other dimensions rather than introducing an unreadable model/member legend. Respect existing figure conventions during later implementation; changes to those conventions are separate decisions.

An optional interactive explorer could link scenario, horizon/warming level, season, spatial support and model selection. Tooltips should expose identity and provenance; exclusions should update counts visibly. This is a product concept, not authorization to add frontend/API code to this workflow repository. Static exports and tabular results should remain reproducible and interpretable alone.

Every interval needs its population and meaning. Shared axes/reference periods enable comparison; diverging maps should center on zero change. Do not hide disagreement by plotting only an ensemble mean, and do not present a dense cloud as a probability density by default.

## 9. Connecting to CST and physical storylines

Retain each paired projection in the same units, reference period, spatial support and season as the corresponding exposure axes. Mark points outside the tested domain; do not clip them onto its boundary. Fractions of included models in a vulnerability region are descriptive ensemble fractions, not system-failure probabilities.

Annual delta-T/delta-P points cannot represent all changes in seasonality, variability, persistence or extremes. Flag these omitted dimensions when interpreting the overlay. New stressor dimensions would be a separate conceptual decision for the scenario-neutral experiment.

As a complementary research option, select a few physically coherent storylines grounded in modeled circulation or regional process differences, retaining actual multivariable combinations. A hot–dry corner assembled from unrelated marginal percentiles is not automatically physically coherent. Storylines explore conditional consequences without assigning unsupported probabilities [S12].

## 10. Priorities, practice status and next decisions

Recommended sequence:

1. Immediate conceptual priority: clarify estimands and interval labels; show coverage; seasonal changes; paired clouds; common-membership and window sensitivity.
2. Broader analysis ensemble: expand model/scenario coverage and record lengths; add selected initial-condition ensembles. Choose coverage by question and convergence/sensitivity, not a universal model-count rule.
3. Data-dependent diagnostics: daily extremes, drought, spatial summaries and global warming levels.
4. Advanced inference: uncertainty partitioning, tested performance/dependence weighting, emergence and physical storylines.

Established practice includes paired change factors, explicit baselines/calendars, standard extreme indices, scenario-conditioned summaries, and large-ensemble analysis. Weighting, hierarchical partitions, emergence and bias adjustment are established research tools whose validity remains target- and data-dependent. Automated emergent constraints, learned downscalers, causal teleconnection discovery, or calibrated joint-tail probabilities require separate research justification; they are not recommended defaults.

Open decisions for the parent task:

- Which basin decisions and seasons should WF2 explain?
- Which estimands matter: forced response, individual realized future climate, threshold exposure, or all three?
- Which analysis/reference windows should coexist with the simulation-aligned view?
- What model-family, scenario and initial-condition coverage is affordable?
- Which daily/global/additional-variable data justify acquisition?
- Is bias adjustment needed for absolute thresholds, or are raw-model relative changes sufficient?
- Which diagnostics remain descriptive, and which justify formal inference?
- Which uncertainties are unquantifiable with the available archive, and how will the report say so?

Acceptance of this conceptual work would be a prioritized methods/data/visualization scope with explicit limitations, followed by separate implementation tasks. No method choice or data expansion is approved by this note.

## 11. Sources and evidence trail

Sources consulted 2026-10-02. Links below support the stated methods; proposed WF2 priorities, layouts and defaults are recommendations rather than findings from these papers. Web abstracts/search extracts supported some sources where full publisher pages were unavailable.

- **S1.** [IPCC AR6 WGI, Chapter 10: Linking Global to Regional Climate Change](https://www.ipcc.ch/report/ar6/wg1/chapter/chapter-10/) — uncertainty sources and regional interpretation.
- **S2.** [IPCC AR6 WGI Atlas, Cross-Chapter Box Atlas.1](https://www.ipcc.ch/report/ar6/wg1/chapter/atlas/) — ensemble-map robustness and agreement.
- **S3.** [Lehner et al. (2020), Partitioning climate projection uncertainty with multiple large ensembles and CMIP5/6](https://esd.copernicus.org/articles/11/491/2020/) — separation of internal variability and modeled response; limitations of single-member fitting.
- **S4.** [Abramowitz et al. (2019), Model dependence in multi-model climate ensembles: weighting, sub-selection and out-of-sample testing](https://esd.copernicus.org/articles/10/91/2019/) — dependence and evaluation of weighting.
- **S5.** [Brunner et al. (2020), Reduced global warming from CMIP6 projections when weighting models by performance and independence](https://esd.copernicus.org/articles/11/995/2020/) — ClimWIP and perfect-model testing; global-temperature application.
- **S6.** [Hawkins and Sutton (2012), Time of emergence of climate signals](https://doi.org/10.1029/2011GL050087) — signal/noise and emergence.
- **S7.** [IPCC AR6 WGI Technical Summary](https://www.ipcc.ch/report/ar6/wg1/chapter/technical-summary/) — warming-level crossing convention and pathway/overshoot qualifications.
- **S8.** [Climdex index definitions](https://www.climdex.org/learn/indices/) — standardized temperature/precipitation extreme indices.
- **S9.** [Maraun et al. (2017), Towards process-informed bias correction of climate change simulations](https://www.nature.com/articles/nclimate3418) — bias-adjustment limitations.
- **S10.** [Lange (2019), Trend-preserving bias adjustment and statistical downscaling with ISIMIP3BASD](https://gmd.copernicus.org/articles/12/3055/2019/) — specific adjustment and evaluation approach.
- **S11.** [High-resolution downscaled CMIP6 drought projections for Australia (2025)](https://hess.copernicus.org/articles/29/4689/2025/index.html) — applied example of historical calibration retained for future SPI/SPEI; not a universal endorsement of its ensemble or processing choices.
- **S12.** [Shepherd et al. (2018), Storylines: an alternative approach to representing uncertainty in physical aspects of climate change](https://doi.org/10.1007/s10584-018-2317-9) — physically coherent conditional futures.
- **S13.** [Brown et al. (2012), Decision scaling: Linking bottom-up vulnerability analysis with climate projections in the water sector](https://doi.org/10.1029/2011WR011212) — connection to CST, resolved through the climate-stress-testing skill bibliography.
- **S14.** [Hawkins and Sutton (2009), The Potential to Narrow Uncertainty in Regional Climate Predictions](https://doi.org/10.1175/2009BAMS2607.1) — original uncertainty partitioning framework.

On-demand background consulted: the brain knowledge-base projection-processing synthesis and its source trail, including C:/Users/taner/workspace/brain/sources/methods/uncertainty-partition-update-lehner-2020.md. This note is an independent task synthesis; no archive content was copied into the repository.
