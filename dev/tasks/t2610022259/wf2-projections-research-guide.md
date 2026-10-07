---
title: Regional climate projections — methods and communication research guide
lifecycle: temporary
created: 2026-10-07
updated: 2026-10-07
---

# Regional climate projections: methods and communication research guide

Build the starter suite around **paired model changes, seasonal conditions, visible ensemble membership,
and sensitivity of conclusions**. Use individual dots and simple intervals for the main regional messages.
Add daily extremes, warming levels and spatial diagnostics when their data requirements are met. Formal
uncertainty partitions, weighting and storylines answer additional questions and require separate
qualification.

This is the literature-backed operational companion to
[WF2 climate projections ideas](wf2-climate-projections-ideas.md). It covers that note's full inventory,
including ideas deferred from the accepted [starter suite](wf2-starter-suite-proposal.md). The existing
[lab brief](wf2-lab-suite-brief.md) remains the implementation authority. Recommendations here do not change
its approved windows, seasons, ensemble, phase boundaries or exclusions.

## 1. Evidence, scope and reading route

**Research date: 7 October 2026.** This is a targeted research synthesis, not a systematic review or a
claim to have identified every recent paper. Searches covered CMIP ensemble practice, regional projections,
user evaluation of climate graphics, seasonality, variability, warming levels, extremes, drought, compound
events, spatial processing and bottom-up assessment. Preference went to peer-reviewed methods, user studies,
recent reviews and assessment chapters. Published work through 2026 supplements the starter note's sources.

Bibliographic details and method claims were checked against publisher pages, accessible article text,
author/institutional repositories or indexed article extracts. Some IPCC and publisher full-text requests
were blocked; those entries rely on accessible assessment/search extracts or abstracts, as flagged in §12.
Figure captions were checked where figure numbers are given. Müller and Döll's Figure 5 was also inspected
as the publisher's downloadable image. Other exemplars are caption/text-verified, not a complete visual audit.
No climate data were analyzed and no regional findings are claimed here.

Practice labels used below:

- **Established:** widely used definitions or assessment practices; still subject to stated data limits.
- **Conditional:** published methods requiring target-specific assumptions and evaluation.
- **Emerging:** recent promising research, unsuitable as an automatic starter-suite default.
- **Suite recommendation:** a proposed operational or communication choice, distinguished from paper findings.

For an implementation reader, start with §3 and C0–C6 in §4. For report design, start with §2 and §10.
For additional data acquisition, use §5–§8. The bibliography in §12 identifies what each source contributes.

Coverage of the original ideas:

| Starter-note idea | Operational guidance here |
|---|---|
| Means, seasons, trajectories, variability | C1–C4 (§4) |
| Joint changes, scenarios and sensitivity | C5–C6 and paired-change view (§4) |
| Uncertainty sources, weights and partitions | §3 and §5 |
| Agreement, detectability and warming levels | C5 (§4) and §6 |
| Extremes, drought, compound events and processes | §7 |
| Spatial support, downscaling and bias adjustment | §8 |
| Visual communication and summary descriptions | §2 and §10 |
| Bottom-up overlays and physical storylines | §9 |

## 2. What the evidence supports about communication

There is no demonstrated universally best climate-projection graphic. Evidence favors choosing a graphic
for a specific comprehension task, then evaluating it with intended readers.

Bannister et al. compared ten presentations of the same ensemble outputs. Dot and box plots performed
well, whereas heat maps and radar plots were less effective in their tested tasks. That supports a dot-based
regional summary; it does not establish that all scientific heat maps are poor. [R05]

Daron et al. found that alternative displays affected interpretation of projected rainfall changes and
confidence in those interpretations. An attractive or preferred display is therefore insufficient evidence
of accurate understanding. Harold et al. provide complementary cognitive-design guidance. [R06] [R07]

Müller and Döll propose percentile boxes for participatory adaptation discussions. Their study provides
a useful local water-sector example, but its evaluation was small and context-specific. Their Figure 5
shows seasons, horizons and contributor counts. Adapt the layout while keeping scenarios separate and
displaying individual outcomes outside selected percentile bands. Their near-term scenario pooling and
tail omission should not become suite defaults. [R08]

**Suite recommendation:** provide three linked communication layers, all generated from the same results:

| Reader/task | Main product | Supporting detail |
|---|---|---|
| Broad audience | One message, dots/interval, agreement count | Plain explanation of spread and limits |
| Applied researcher | Seasonal and spatial comparisons | Membership, window and processing sensitivities |
| Academic/reviewer | Member/model results and estimands | Methods, provenance, diagnostics, assumptions |

Do not assign different facts to different audiences. Vary detail, explaining both uncertainty in numbers
and limitations of the underlying evidence. [R40]

## 3. Shared operational foundation

### 3.1 Define the quantity before computing it

Every result needs: region/support; variable; temporal resolution; aggregation period; reference and future
years or warming level; scenario; model/member population; statistic; processing variant; units; and status.
Store the identities of contributors, not just their count.

Keep these quantities separate:

1. **Modeled mean response:** average changes across members within a model, then summarize models.
2. **Individual simulated outcomes:** retain the range of member-level changes, with model-balanced weights.
3. **Year-to-year climate variation:** describe annual/seasonal values within each member's time window.
4. **Estimation uncertainty:** an interval derived under a specified sampling/error model.

An interval across models cannot substitute for the other three. CMIP is an ensemble of opportunity;
ensemble frequencies are not automatically calibrated probabilities. Current ensemble guidance and regional
assessment practice support explicit ensemble design and interpretation. [R01] [R04] [R13]

### 3.2 Form paired changes before ensemble reduction

For model `m`, member `r`, scenario `s` and period `k`, compute from its own paired series:

```text
ΔT = mean(T_future) − mean(T_reference)                  [°C]
ΔP_abs = mean(P_future) − mean(P_reference)              [mm/day]
ΔP_rel = 100 × (mean(P_future)/mean(P_reference) − 1)     [%]
```

For a seasonal mean precipitation rate, `mean(P) = sum(d_i P_i)/sum(d_i)`, where `d_i` is the native-calendar
month length. Also retain the precipitation integral `sum(d_i P_i)` when total water input is the question.
Rate changes and integral changes can differ when period lengths differ. Temperature uses a day-weighted
mean. Never obtain annual rainfall change by averaging twelve monthly percentages.

Reject incomplete aggregation periods or apply a declared completeness rule. Do not infer Gregorian day
counts from a decoded timestamp when the source calendar is `noleap`. State DJF's year convention and
whether its December must lie inside the analysis window. Record effective counts after exclusions.

Historical matching requires the actual reference-series identity. Matching member labels across scenarios
does not establish identical future internal variability. A baseline crossing the historical/SSP boundary
requires an explicit splice rule and scenario provenance.

### 3.3 Windows and model hierarchy

The approved lab uses 1985–2014 and complete 30-year future analysis windows, alongside simulation-aligned
windows; C4 uses analysis windows only. These are local decisions. AR6's 1995–2014 reference is a useful
comparison option, not a reason to silently replace the approved baseline. Report baseline sensitivity.
Longer windows reduce sampling noise while averaging over more climate evolution. [R02] [R03]

For C1–C6, average member-level changes within each model, then calculate the model median, range and
eligible quantiles with equal model weight. For means, this is straightforward. Averaging member SD ratios
is a summary of member ratios, not the SD of an ensemble-mean time series; preserve that distinction.

For an outcome distribution with `M` models and `R_m` members, a transparent reference is
`w_mr = 1/(M R_m)`. Equal-model weighting is not independence weighting. Institution is a useful initial
sensitivity grouping, but shared components cross institutional boundaries. [R13] [R14]

### 3.4 Status and denominator safeguards

- Keep unavailable, excluded, undefined and valid results distinct; retain reasons.
- Retain WF2's dry-reference precipitation guard and report absolute changes where percentages fail.
- Suppress SD/CV ratios when their reference denominator is zero or numerically unstable. Their guards
  need suitable units and tolerances; the mean-precipitation threshold cannot guard a temperature SD.
- Do not count a missing projection, non-reaching warming level or unobserved historical exceedance as zero.
- Show contributor counts on each panel, including changes in composition across time or space.

## 4. Monthly starter suite: C0–C6

### C0 — Evidence coverage

**Question:** Which evidence actually supports this result?

**Operationalize.** Create a model × scenario availability table with member counts, variables, periods,
calendar, grid, archive version, institution, and exclusion reasons. Derive a result-specific mask after
window/completeness checks. Preserve all-available and common-model subsets as named alternatives.
Common membership must mean the same identities, not merely equal counts. [R01]

**Figure recipe.** A coverage matrix with explicit counts and text/shape status markers. Use a neutral
missing-data symbol, a separate excluded marker, and a legend explaining both. Put long reasons in the
adjacent table. Add a small location map showing polygon and native grid support.

**Message template:** “This comparison uses {M} models and {R} realizations in both scenarios. {E} requested
combinations were unavailable. The geographic detail is limited by {grid/support}.”

**Qualification check:** every result's contributors can be reconstructed from the table. Download volume
and archive availability are acquisition facts, not evidence of scientific adequacy.

### C1 — Changes in mean conditions

**Question:** How much warmer, wetter or drier are annual and seasonal conditions?

**Operationalize.** Apply §3 per member and summarize model changes for scenario × horizon × season.
Retain ΔP in percent and absolute units. Calculate matched within-model scenario contrasts separately.
Show the historical climatology where an absolute impact threshold is discussed; model baseline bias may
matter even when a relative change is interpretable. [R04]

**Figure recipe.** Horizontal dot strips: one model response per dot; median marker; explicitly labeled
range and, where justified, IQR. Facet by season and variable. Keep zero visible and use shared axes across
comparable panels. Follow the approved lab's ten-model IQR heuristic while labeling it as a display choice,
not a scientifically proven sample-size threshold. Dots have direct user-study support. [R05]

For an adaptation workshop, trial a percentile-box variant with explicitly identified percentile edges
and individual tail points. Its meaning must be taught, rather than inferred from box width. [R08]

**Message template:** “For {region}, {scenario} projects a median {season} change of {Δ}, relative to
{reference}, in {future}. Included model responses span {low} to {high}; {n}/{M} indicate {direction}.
This span describes the included ensemble.”

**Qualification check:** paired model arithmetic reproduces the result table; no range is called a
confidence interval or the full range of possible climate change.

### C2 — Seasonal conditions and redistribution

**Question:** Does annual change hide a different seasonal distribution?

**Operationalize.** Calculate each member's reference/future monthly climatology and monthly changes.
For precipitation redistribution, calculate `f_k = P_total,k/P_total,annual` within each member and
period. Report `100 × (f_future − f_reference)` in **percentage points**, distinct from percent rainfall
change. Keep fixed local seasons separate from timing diagnostics. Dunning et al. demonstrate why rainfall
amount, intensity, frequency and season timing can give different messages. [R27]

**Figure recipe.** Two rows: absolute monthly conditions above, monthly changes below. Use separate
temperature/precipitation panels; reference dashed, future solid. Show model spread on **changes**, so
historical model offsets do not obscure the change signal. A companion seasonal-fraction plot communicates
redistribution. A season × horizon heat map can serve as a technical index if cells also carry numbers.

**Message template:** “Annual rainfall change masks {seasonal contrast}. {Season} supplies {a}% of annual
rainfall in the reference and {b}% in the future, a change of {b−a} percentage points.”

**Qualification check:** fractions sum to one where the denominator is valid. Monthly rainfall changes do
not establish changes in wet-day frequency, agricultural onset or storm intensity.

### C3 — Trajectories and calendar horizons

**Question:** How does the projected climate evolve, and when do scenarios separate?

**Operationalize.** Form annual anomalies against each member's fixed reference. Apply the declared running
mean to each member before model reduction. Record length and endpoint rule; report unavailable endpoints
rather than extrapolating. Track whether contributors change along the trajectory.

**Figure recipe.** Scenario-faceted panels with faint smoothed model traces, a median, a labeled descriptive
band and counts. Mark the actual horizon windows as horizontal spans. Provide annual unsmoothed values in
the technical view. Large-ensemble analysis motivates separating slow response and internal fluctuations;
smoothing alone does not fully estimate a forced response. [R09] [R10]

**Message template:** “These lines summarize {L}-year climate averages. Their spread compares simulated
long-term changes; it does not show the range of individual future years. Scenarios {separate/overlap}
under the displayed ensemble and window definition.”

**Qualification check:** no shortened endpoint windows are presented as full-length windows; scenario
differences are checked on common model support. Near-term overlap is not evidence that mitigation has
no longer-term effect.

### C4 — Interannual variability, distributions and persistence

**Question:** Does year-to-year variation change, beyond the shift in mean conditions?

**Operationalize.** Use complete annual/seasonal values in the analysis windows. Report undetrended SD,
within-window detrended SD, SD ratio and precipitation CV. Define CV as residual SD divided by the positive
**undetrended climatological mean**, not by the near-zero mean residual. Also report SD in physical units:
CV can rise because mean rainfall falls, even if SD does not rise. Pendergrass et al. provide a multiscale
precipitation-variability precedent. [R17]

The approved per-member linear detrend is a transparent descriptive starting point. Document SD divisor
and degrees of freedom. A trend removes part of low-frequency variation; changing the detrending method
can change the answer. Call the quantity “detrended interannual variation,” not an isolated internal-
variability component. With adequately large ensembles, estimate each model's forced trajectory across
members and examine deviations from it; test finite-member sensitivity. Recent work shows that even
performance-screened large ensembles can disagree about future variability. [R11] [R18]

**Figure recipe.** An SD-ratio dot plot with reference line at 1, paired reference/future empirical CDFs
of annual values, and separate within-model member strips. A quantile-change plot can show whether dry
years change differently from median years. Avoid smooth violins for short records. Add lag correlation
or run-duration panels only when persistence is an explicit question and record support is adequate.

**Message template:** “After removing a linear trend, simulated {season} rainfall SD changes by {Δ}.
This estimate varies with {members/detrending/window}. It describes variation in seasonal totals and
does not establish a change in daily storms.”

**Qualification check:** changing mean alone must not change residual SD; changing variance by a factor
of two must give an SD ratio of √2. Keep year-level quantiles distinct from model-level change quantiles.

### C5 — Agreement and scenario contrasts

**Question:** Which directions of change are shared, and how do named pathways differ?

**Operationalize.** Report `n_increase`, `n_decrease`, `n_small-change` and `M_valid`. Fix the small-change
band before viewing results and retain exact sign counts alongside it. Median-sign agreement uses all
valid models as its stated denominator. If the median is zero or there is no directional majority, report
that explicitly. Neutral models are neither missing nor agreement with a positive/negative sign.

For scenario contrasts, compute each common model's `change_s2 − change_s1`, then summarize those
contrasts. Do not subtract unrelated ensemble medians. Check member composition within paired models.

**Figure recipe.** An agreement matrix with counts printed in each cell and a companion direction-count
bar. Use categories and text, not a probability color scale. For scenario differences, use paired slope
plots or a dot plot of within-model differences.

The AR6 Atlas simple map method uses an 80% sign-agreement threshold. The advanced method additionally
requires a signal exceeding its internal-variability threshold in at least 66% of models; these are
separate tests. Do not call the lab's small-change heuristic that advanced method. [R02]

**Message template:** “{n}/{M} models project lower {season} rainfall; {p} project higher rainfall and
{z} lie within the declared small-change band. Agreement is an ensemble count, not the probability of
drying or an IPCC confidence assessment.”

**Qualification check:** a half-positive/half-negative ensemble cannot become “agreement” through rounding;
coverage and disagreement remain distinct.

### C6 — Membership, family and processing sensitivity

**Question:** Would another defensible analysis choice change the headline?

**Operationalize.** Recompute C1/C5 under leave-one-model-out, leave-one-institution-out, common versus
all-available membership, and approved aligned versus analysis windows. Add an independently documented
family grouping when available. Institution-only grouping misses cross-center code sharing. [R14]

For each headline, retain the original value, every alternative, counts, sign changes and decision-threshold
crossings. Later compare observation products or bias-adjustment variants on matched model/member inputs
(§8). Baseline and window effects should be varied separately where attribution matters.

**Figure recipe.** A horizontal sensitivity plot: original estimate/reference line, alternatives grouped
by choice, labels with counts. Highlight a sign or decision-threshold crossing. If many leave-one-out
values exist, show all in a companion panel and identify influential removals in the summary.

Optional local scaling `percent ΔP/local ΔT` needs a near-zero-temperature-change guard. Show the actual
paired ΔT–ΔP points first. This ratio is neither equilibrium climate sensitivity nor a global-warming-level
result, and may vary with season, horizon and pathway.

**Message template:** “The warming conclusion persists across tested memberships and windows. The
rainfall conclusion changes sign when {choice} changes; its direction is sensitive to that choice.”

**Qualification check:** label this a sensitivity experiment on the selected archive. Leave-one-out
results do not quantify all structural uncertainty. Ensemble-size convergence must be assessed for the
target quantity and acceptable error; a universal count is insufficient. [R12]

### Cross-component view — paired temperature and precipitation changes

Keep actual member/model pairs for every season, scenario and horizon. Draw ΔT against ΔP, with zero-rainfall-
change and selected system-threshold lines; facet by scenario or season and connect only the same identity
across horizons. Label counts and membership changes. Link the cloud to C1's marginal summaries and C6's
sensitivity results. A ΔT–ΔP centroid or two marginal medians need not correspond to any actual projection.

Show all dots before considering density contours. If contours are later used, identify weighting, density
estimation and bandwidth sensitivity; the surface remains an ensemble descriptor, not a calibrated joint
probability. Never assemble a hot–dry future from unrelated hot and dry marginal percentiles. The storyline
and coherent-field literature supports preserving physically meaningful combinations. [R35] [R34]

**Message template:** “The same models supply both temperature and rainfall changes. These pairs reveal
{association/disagreement}; the hot and dry ends of separate summaries need not occur together.”

## 5. Advanced ensemble interpretation

### 5.1 Uncertainty inventory and formal partitioning

**Established framework; conditional quantification.** Inventory internal variability, modeled response
differences, scenario dependence, finite-record error, ensemble dependence, processing differences and
unrepresented processes. Record what is estimable, only sensitivity-tested, or unquantified. [R04] [R09]

Single-member polynomial fits can confuse local internal variability with differences in modeled response.
Lehner et al. use multiple large ensembles to evaluate that problem. Their Figures 1–2 distinguish absolute
and fractional uncertainty; Figure 5 illustrates spatial-scale dependence. [R09]

**Operationalize.** Specify an estimand, then a replicated model × scenario × member design. Check balance,
missing cells and effective member support. Fit a documented hierarchical/variance model that retains
material interactions. Report absolute components in physical variance units and their fractions, with
sampling uncertainty. Treat the scenario component as conditional on the selected pathways and their
declared weights. Do not report unavailable components as zero.

**Figure recipe.** Within-model member strips next to model means first; component time series and stacked
fractions only after qualification. Absolute and fractional panels must share the analysis definition.

**Message template:** “This design estimates {components} conditional on {models/scenarios}. It does not
estimate {missing components}. A smaller fractional contribution need not mean smaller absolute uncertainty.”

The three five-member models in the recorded development ensemble can exercise member-level diagnostics;
they do not establish that a full local uncertainty partition is well supported. MMLEAv2 offers an
additional published large-ensemble resource, with coarser common-grid support that must be respected. [R11]

### 5.2 Sampling intervals

**Conditional.** Define the target interval before resampling. For finite-window means or quantiles,
resample blocks of complete years within a member, preserving joint variables and locations with the
same time indices. Account for reference and future sampling; share reference draws across comparisons
using a shared baseline. Check serial dependence and block-length sensitivity. [R38]

Strong trends violate stationary resampling assumptions. Use justified residual resampling or a specified
time-varying model, and verify interval coverage with controlled simulations. A bootstrap of years does
not create missing multidecadal variability or structural model uncertainty. A bootstrap of CMIP model
names is not automatically an inferential confidence interval.

**Figure recipe:** sampling intervals on individual estimates, visually distinct from ensemble spread.
Never put two unexplained uncertainty bands around one curve.

### 5.3 Performance and independence weighting

**Conditional.** Keep the transparent equal-model result as a reference. Evaluate target-relevant
historical processes, multiple observational products, weight concentration and withheld models/families.
Tune and test a weighting method such as ClimWIP using an explicit out-of-sample design. Retain weighted
and unweighted outcomes. Success for global temperature cannot validate local rainfall weighting. [R13] [R15]

CMIP6's high-sensitivity models motivate particular care in interpreting unweighted calendar-year warming.
Hausfather et al. discuss the problem; this is a published commentary rather than a local validation study.
Warming-level comparisons help separate warming magnitude and regional response, but retain pathway and
regional-pattern uncertainty. Do not remove a model just because it projects an inconvenient outcome. [R16]

**Figure recipe:** weights by model/family, weighted/unweighted dot summaries, and held-out diagnostics.
`1/sum(w²)` describes weight concentration; do not call it the number of physically independent models.

## 6. Warming levels, robustness and emergence

### 6.1 Global warming levels

**Established assessment framing; conditional extraction.** Acquire each model/member's global annual
surface-air-temperature trajectory with an area-weighted global definition and a documented 1850–1900
reference. Basin `tas` is not a substitute, and records beginning in 1950 cannot supply that reference.
Do not silently mix modeled global surface air temperature with a blended observed land/ocean metric.

Implement the first qualifying 20-year mean above each warming threshold and extract the matching local
20-year window. Store its start/end years and centering convention. Classify reached, not reached by the
end of available data, and insufficient data separately. Compare common contributors as well as
all available contributors. The AR6 Technical Summary provides the 20-year framing. [R03]

**Figure recipe:** local changes versus warming level, plus a separate scenario-conditioned arrival-window
plot with a visible not-reached category. State whether each summary conditions on reaching the level.

**Message template:** “At {G}°C of global warming, the contributing models project {local change}. This
level is reached at different times under different pathways; {n} available members do not reach it.”

Retain ascending, stabilized and descending/overshoot states separately. Roldán-Gómez et al. show regional
irreversibility in mean and extreme climate under overshoot pathways; the same global temperature need
not imply the same regional climate. [R33]

### 6.2 Map robustness

**Established display methods; data-dependent meaning.** Implement AR6 definitions exactly only if the
required inputs and noise assumptions are supplied. Its advanced classification distinguishes robust
signal, no robust signal and conflicting signal; add insufficient coverage as a separate suite status.
Simple sign agreement does not quantify noise. [R02]

**Figure recipe:** a change map and a companion classification/coverage map. If hatching is used, spell
out every category in the legend. Center signed-change color scales on zero, keep comparable limits, and
show native-grid resolution. Repeat summaries for the regional support actually used by the decision.

**Message template:** “Models agree on warming here. Rainfall changes show {weak signal/conflicting
directions}, under the stated method. Blank cells indicate missing support rather than no change.”

### 6.3 Time of emergence

**Conditional.** Define signal, baseline, smoothing length, noise distribution, threshold and persistence
rule before extraction. Noise must match the target statistic and spatial support: variability of a
20-year basin mean differs from annual cell SD. Use control segments or sufficiently large ensembles
with appropriate drift checks; disclose whether variability is assumed stationary. [R19]

**Figure recipe:** member/model crossing windows with distinct “not emerged by end” and “insufficient
data” categories, beside a signal/noise example. Keep censored non-emergence outcomes in the count;
an average crossing year among only emerged members is conditional and must be labeled.

**Message template:** “Under this detection rule, the modeled long-term change exceeds the specified
noise range in {window}. This is a statistical detectability result, not an adaptation deadline.”

## 7. Data-dependent hazard extensions

### 7.1 Daily extremes and fixed-threshold exposure

**Established indices; conditional impact interpretation.** Obtain daily precipitation and daily maximum/
minimum temperature as required. Start with a decision-relevant ETCCDI subset: Rx1day, Rx5day, CDD,
SDII, TXx, TNn and a specified warm-spell indicator. Pin definitions, wet-day threshold, missing-data
rules, run boundaries and percentile-reference implementation. Baseline percentile indices need the
prescribed treatment of in-base-period sampling artifacts. [R20] [R21]

For an initial annual product: Rx1day is the largest daily precipitation amount; Rx5day is the largest
five-day accumulated amount; CDD is the longest run with daily rainfall below 1 mm; SDII divides total
rainfall on wet days (at least 1 mm) by their count; TXx/TNn are the highest daily maximum/lowest daily
minimum temperature. WSDI counts days in runs of at least six consecutive days exceeding the historical
calendar-day 90th percentile of daily maximum temperature. Pin the exact percentile-window/bootstrap and
spell-boundary conventions from the [Climdex definitions](https://www.climdex.org/learn/indices/).

Calculate indices per member before ensemble reduction. Choose among three different questions:

- Model-relative historical thresholds: how conditions unusual in that model change.
- Observed/physical impact thresholds: how real-world exposure changes, requiring bias assessment.
- Future-relative thresholds: the unusual tail within the future climate, which does not measure change
  relative to historical exposure.

**Figure recipe:** an index-change dot panel with units and sample counts; an empirical CDF/exceedance
curve with a fixed historical threshold; a spell-duration distribution where sequencing matters.
Use “hottest day,” “largest five-day rainfall” and “longest dry spell” as plain labels beside index codes.

**Message template:** “The model's historical {threshold}-level rainfall is exceeded in {a} reference
years and {b} future years. This describes modeled exposure at {support}, not river-flood frequency.”

**Qualification check:** daily completeness, thresholds and calendars are verified; monthly data never
substitute for daily indices. Pooling annual maxima from different models must not be presented as one
homogeneous long record.

### 7.2 Extreme-event frequency and return levels

**Conditional.** Prefer empirical fixed-threshold frequencies when adequately sampled. Use GEV annual
maxima or GPD peaks over threshold when the question justifies tail inference. Check threshold stability,
declustering, fit diagnostics, return-level uncertainty and sensitivity to nonstationarity. Short records
do not justify precise distant return periods. Coles provides the statistical foundation. [R22]

For threshold exceedance, show future and reference frequency plus absolute difference. A ratio is
undefined when reference empirical frequency is zero; label it rather than adding an arbitrary count.
If a fitted model supplies a ratio, disclose the assumptions and uncertainty.

**Figure recipe:** return level versus return period with fit intervals, observed/simulated maxima, and
distinct reference/future curves. Alternatively show expected exceedance years out of 30. A nonstationary
“return period” must name the climate state or period to which it applies.

**Message template:** “The reference-period {event} becomes more frequent in these simulations. Its
estimated frequency depends on {fit/window}; {record length} limits tail precision.”

### 7.3 Drought and climatic water balance

**Established indices; conditional evaporative-demand estimates.** Start with precipitation accumulation
and SPI at decision-relevant scales, then add SPEI/P–PET when evaporative-demand inputs are defensible.
For SPI, document the precipitation distribution, zero mass, seasonal calibration and fit checks.
For SPEI, document the water-balance distribution and PET method. Fit each member's historical calendar-
month distributions and retain them when asking how exposure changes relative to historical climate.
Refitting future distributions answers a separately labeled future-relative question. [R23] [R24]

SPI/SPEI operationally transform an accumulated precipitation/water-balance value through the fitted
historical cumulative distribution and then the standard-normal inverse CDF. Calculate the accumulation
first, fit by ending calendar month, and retain the fit and its zero/tail treatment in the output. Guttman
provides an SPI calculation precedent; distribution fit remains a diagnostic obligation. [R42]

Use long enough calibration records and accumulation buffers across window boundaries. Define drought
threshold, event start/end, minimum duration, severity and handling of ongoing boundary events. Compare
precipitation-only and demand-sensitive outcomes. Temperature-only PET is a sensitivity option, not an
unqualified default. Milly and Dunne show how PET methodology can distort inferred drying. [R25]

**Figure recipe:** changes in drought months/years, duration and severity as dot panels; example event
timelines; paired SPI/SPEI results; affected-area fraction if spatial support permits.

**Message template:** “Dry conditions relative to the historical precipitation climate become {change}.
Including atmospheric demand produces {additional change}, sensitive to {PET method}. These indices
do not directly estimate runoff or groundwater drought.”

### 7.4 Compound hazards, spatial concurrence and sequencing

**Established typology; conditional statistical models.** Specify the impact mechanism first. Separate
preconditioned events, simultaneous multivariate events, successive events and spatial concurrence.
Zscheischler et al. provide this typology. [R26]

For a first hot–dry analysis, count jointly exceeded fixed historical thresholds in synchronous seasonal
values, retaining T/P pairs. Report both marginal and joint frequencies. Specify AND/OR logic and duration
before counting. For wet-antecedent/heavy-rain events, additional daily variables and lag definitions are
needed. Diagnose dependency changes; do not multiply marginal frequencies unless independence is justified.

**Figure recipe:** joint scatter with threshold quadrants and member identity, event timelines, and a
comparison of marginal versus joint frequency. For connected subcatchments, compute simultaneous event
area from each model's actual fields rather than combining independent local quantiles.

**Message template:** “Hot and dry {seasons} occur together in {a} reference and {b} future cases under
this definition. Changes in both individual hazards and their concurrence matter.”

Copulas and multivariate tail models are research options requiring adequate joint samples and validation.
Marginal bias adjustment alone does not validate dependence. [R32]

### 7.5 Season timing

**Conditional and region-specific.** Monthly data can characterize broad rainfall redistribution. Compute
dates/months at which the cumulative annual climatological rainfall fraction reaches declared levels,
using a suitable water year; disclose within-month interpolation. Call this a rainfall-fraction timing
metric, not meteorological or agricultural onset.

Daily onset/cessation needs a regionally justified definition, false-start handling and treatment of
unimodal/bimodal seasons. Dunning et al. provide an objective wet-season example for Africa; its definition
is not automatically suitable for other rainfall regimes. [R27]

**Figure recipe:** cumulative rainfall-fraction curves and onset/cessation interval strips. Use paired
season timelines for decision-makers. A circular centroid can fail to summarize two distinct wet seasons;
retain both cycles rather than forcing one date.

**Message template:** “A larger share of rainfall arrives later in the reporting year. This monthly
diagnostic cannot determine planting onset or the dates of individual rain events.”

### 7.6 Climate modes and teleconnections

**Conditional.** Acquire model-specific SST/pressure fields or verified indices. Diagnose historical
seasonal associations and future changes with sufficient members/record length. Detrend when the question
concerns variability rather than the forced change. Use appropriate dependence-aware intervals and control
multiple comparisons if scanning many lags, modes or locations. ENSO response involves changes in the
background climate and teleconnections as well as the index itself. [R28]

**Figure recipe:** reference/future lag-response curves; seasonal event composites; member estimates
within models. Separate a physical association from a causal claim.

**Message template:** “In these models, {mode} is associated with {regional seasonal conditions}; the
future association is {change}. Simulated future event dates are not synchronized with observations.”

Use the recent MMLEAv2/Climate Variability Diagnostics Package work as a diagnostic precedent. Observations
are one realization, so a single model member may look favorable or unfavorable by sampling alone. [R11]

### 7.7 Snow and evaporative demand

**Conditional and process-specific.** Add snowfall, snow storage and melt variables when snow is relevant;
use temperature-threshold diagnostics only as declared proxies. For evaporative demand, acquire radiation,
humidity, wind and pressure as needed for the chosen method. Keep potential/reference ET distinct from
actual ET, and atmospheric demand distinct from catchment water availability.

**Figure recipe:** monthly snowfall fraction/snow-water-equivalent curves; changes by elevation band when
the product actually resolves elevation; separate P, demand and P–demand panels. Climate inputs alone
cannot establish a streamflow response. Han et al.'s catchment analysis demonstrates that declining snow
does not imply one universal direction of streamflow-seasonality change. [R39]

**Message template:** “The climatic conditions favor {less snowfall/higher demand}. The resulting storage
and flow response requires a qualified hydrological analysis.”

## 8. Spatial support, regridding and processing choices

### 8.1 Catchments, subcatchments and national summaries

**Operationalize.** For integrated climate, compute native-grid polygon averages with cell/polygon
intersection-area weights and explicit land/missing-data masks. Where current WF2 uses an approximation,
retain that provenance and quantify sensitivity before claiming a more accurate support. Report native
cell sizes, number of contributing cells, polygon coverage and shared support among subcatchments.

Choose the statistic's order deliberately:

```text
extreme(area-average daily rainfall) ≠ area-average(extreme daily rainfall)
```

The first describes a basin-wide event; the second describes local extreme exposure across the basin.
Likewise, a national mean, fraction of land above a threshold, and population-weighted exposure are different
estimands. Population weighting requires an explicit population dataset and scenario/year.

For national/regional extremes, calculate area fractions separately for each coherent model field, then
summarize those fractions. Bevacqua et al. show that assembling spatial worst cases from different models
can exaggerate uncertainty. Their study is global and sector-specific; the transferable lesson is to
preserve coherent fields, not to import its numerical bounds into a catchment assessment. [R34]

**Figure recipe:** locator/native-grid map, regional-change small multiples, and subcatchment dot panels.
Use a within-model spatial-distribution view to explain heterogeneity. If subcatchments share a few coarse
cells, state that the available projections cannot resolve their differences; finer rendering adds
no evidence.

### 8.2 Common grids and matched processing experiments

For ensemble maps, choose a documented common grid/support, masks and coverage rules. Conservative
remapping is appropriate where preserving area integrals is the objective, but test mask and integral
behavior. It does not conserve every extreme or distributional property. Regrid-before-index and
index-before-regrid answer different questions. Jones provides the conservative-remapping foundation. [R29]

Bias adjustment and downscaling need a stated purpose. Raw relative changes may suffice for a mean-change
diagnostic; real-world absolute thresholds often require more local evaluation. Bias adjustment cannot
repair major process errors, and standard cross-validation alone may fail to reveal inappropriate use.
Retain physical/process diagnostics. [R30]

Where appropriate, compare a documented trend-preserving method such as ISIMIP3BASD with raw changes.
Validate changes in relevant quantiles and spatial/temporal properties; trend preservation is specific
to selected statistics. Multivariate methods such as MBCn address dependence but need their own target-
specific tests. Do not double-adjust an already adjusted product. [R31] [R32]

**Figure recipe:** matched raw/processed paired dots and historical/future distribution diagnostics.
Hold GCM, member, scenario, support and window fixed when varying observation product, RCM or adjustment
method. If they cannot be matched, report product differences without attributing them solely to processing.

**Message template:** “Regional change is {stable/sensitive} across these matched processing choices.
The fine output grid does not establish fine-scale forecast skill.”

## 9. Projection overlays, vulnerability and physical storylines

**Established bottom-up connection.** Specify system performance metrics and acceptable thresholds, explore
the climate exposure space independently, and map vulnerability before overlaying projections. Decision
scaling supplies the connection; projections inform the interpretation of independently identified
failure conditions. [R36] [R37]

**Operationalize.** Retain each model/member's paired ΔT/ΔP in the exposure axes' units, season, support
and reference period. If projection and stress-test baselines differ, recompute or explicitly transform
them before comparison. Plot out-of-domain points beyond the tested boundary; do not clip them onto it.
Label the stress-test grid, performance threshold, realization treatment and untested area.

**Figure recipe:** a performance response surface with an explicit failure boundary and scenario-faceted
projection points. Show one surface per adaptation option on common axes where comparison is the purpose.
If the stochastic response varies across realizations, identify which response statistic/criterion
defines the displayed failure region.

**Message template:** “The system fails its {criterion} under {conditions}. {n}/{M} included model
responses fall within that domain. This fraction is descriptive and is not a probability of system failure.”

Annual means omit changes in seasonality, variability, persistence and extremes. Show these as an adjacent
diagnostic or limitation; do not imply that a two-axis overlay represents the entire climate-risk space.
Changing stressor dimensions is a separate assessment-design decision.

**Physical storylines — conditional/emerging application.** Select a small set of physically coherent
model/member futures using regional process reasoning, not unrelated marginal percentiles. Explain the
circulation, seasonal or sequencing mechanism, then assess its implications. Shepherd et al. describe
storylines as conditional explorations without requiring prior probabilities. [R35]

**Figure recipe:** one card per storyline, with paired seasonal changes, a process diagram and its location
on the exposure surface. A selected adverse storyline is not “the worst possible future”; describe its
selection criterion and omitted mechanisms. Retain identities and joint fields. [R34]

## 10. Visual exemplars and broad-audience summaries

### 10.1 Published examples to examine

These are design precedents, not templates to copy unchanged. Follow the source's figure license before
reproducing an image. Figure identifiers below were checked against accessible text/captions.

| Source/example | What to learn | Adaptation for this suite |
|---|---|---|
| Bannister et al. [R05], ten formats | Accuracy and appeal can differ | Test dots against intervals |
| Daron et al. [R06], Fig. 2 | Same rainfall data, different readings | Explain ensemble counts explicitly |
| Müller & Döll [R08], Figs. 1, 4–6 | Percentile and seasonal explanation | Show tails; separate SSPs |
| Lehner et al. [R09], Figs. 1–2, 5 | Absolute/fractional uncertainty | Pair size and fraction |
| AR6 Atlas [R02], Box Atlas.1 | Agreement, noise, conflicting signal | Distinguish missing data |
| Lange [R31], Fig. 1 | Distribution/quantile-change preservation | Explain processing using paired CDFs |
| Bevacqua et al. [R34], Ext. Data Fig. 6 | Spatially incoherent tails | Retain coherent fields |
| Shepherd et al. [R35], Fig. 1 | Physical event sequence | Explain joint mechanisms |
| Fowler et al. [R37], graphical abstract | Projections in stress testing | Distinguish hazard and failure |

### 10.2 Build a regional findings page

**Suite recommendation:** use a report page with four parts:

1. **Three supported findings:** magnitude/direction, seasonal contrast, and sensitivity or unresolved issue.
2. **Main figure:** model dots/intervals for decision-relevant seasons, scenarios and horizons.
3. **Context figure:** trajectory, subcatchment comparison or threshold exposure, chosen by the question.
4. **Evidence footer:** reference/future years, spatial support, contributors, spread definition and limits.

The detailed diagnostics follow that page. A compact heat map can index many comparisons for researchers;
it should not be the only graphic explaining an important finding to a broad audience. This recommendation
balances scientific completeness with the task-specific visualization evidence in §2.

Use one consistent scenario color system. Reinforce color with facets, text or line style. Signed-change
maps need a perceptually suitable diverging scale; positive quantities need a sequential scale. Verify
color-vision accessibility and grayscale readability, particularly between similar SSP colors. Scientific
color-map guidance explains why rainbow and poorly chosen red–green maps can distort interpretation. [R41]

Keep geographic locator detail separate from change magnitudes. Never equate a pale or uncertain map cell
with “safe,” and do not use red as a risk class unless system consequences actually define that class.

### 10.3 Reusable caption and summary patterns

**Caption skeleton:**

> {Region/support}: {quantity} under {scenario(s)}, {future window/warming level} relative to {reference}.
> Dots are {model/member estimand}; {line/band} shows {median and specified descriptive interval}.
> {M} models and {R} realizations contribute. {Aggregation, weighting and smoothing definition}.
> The displayed spread {meaning}; {principal limitation}. Source: {dataset/version and results table}.

Use the approved lab's recoverable captions. A standalone export needs access to its caption and evidence
footer even if the presentation layout places them outside the image.

**Interpretation examples — illustrative wording, not findings from the study basin:**

- Magnitude: “Warming appears in all included models; its size varies across models and pathways.”
- Seasonality: “A small annual rainfall change can coexist with wetter winters and drier summers.”
- Variability: “Average conditions and the range of individual years change differently.”
- Agreement: “Models share the warming direction but disagree about the direction of rainfall change.”
- Spatial support: “This catchment-average estimate cannot distinguish these tributaries at the model grid.”
- Sensitivity: “Rainfall direction changes with the ensemble subset, so it remains an unsettled conclusion.”
- Decision context: “The vulnerability threshold is crossed under these tested conditions; projections
  help judge their plausibility but do not define the search boundary.”

With actual results, replace general statements by quantities, periods and counts. Avoid “most likely,”
“95% confidence,” “worst case,” and IPCC confidence language unless the corresponding method supports them.
Do not translate precipitation change directly into runoff, flood losses or water-supply reliability.

### 10.4 Evaluate comprehension before treating a layout as qualified

Ask representatives of all three audiences to use identical data in candidate layouts. Test whether they
can identify direction, magnitude, disagreement, interval meaning, geographic support and the conclusion
most sensitive to processing. Ask whether the display implies a forecast probability. Record accuracy,
misinterpretations and time as well as preference/confidence. Iterate and report participant/task limits.
This is a proposed suite evaluation protocol, informed by the user studies rather than a claim of
validated comprehension for the new suite. [R05] [R06] [R07]

For a future interactive explorer, link selections to the same downloadable tables, recompute membership
counts visibly, expose provenance in tooltips and retain readable static exports. Any API/frontend work
belongs in the platform's separate applications, not this workflow repository.

## 11. Operational sequence and acceptance evidence

The following sequence prioritizes scientific support, not permission to expand the current lab brief.

| Increment | Products | Evidence needed before interpreting |
|---|---|---|
| Monthly foundation | C0–C3, C5–C6 | Pairing, calendars, windows, membership, visual comprehension |
| Variability | C4, member strips | Detrending/denominator sensitivity, sufficient records |
| Broader framing | Warming levels, spatial support | Global baseline, coherent grids/fields, coverage |
| Hazard exposure | Daily indices, drought, compound events | Inputs, definitions, event sample adequacy |
| Advanced inference | Partitions, weights, emergence, storylines | Replication and validation |
| Decision connection | CST overlay | Compatible axes/baselines, qualified performance surface |

For each module, publish: results table, plotted-data table or exact linkage, figure, caption, contributor
identities, unavailable reasons, method settings, provenance and qualification status. A runnable prototype
and a successful real-data exercise are distinct from scientific qualification.

Acceptance checks to build into later implementation:

- Reconcile approved aligned-window means/SD with WF2's retained tables before deriving new summaries.
- Verify hand-computed calendar-weighted seasons, incomplete DJF handling and dry/zero-denominator behavior.
- Demonstrate that adding members to one model does not give that model more weight in a model summary.
- Demonstrate that missing scenarios/levels remain unavailable and change the stated contributor counts.
- Show that all plotted values and written counts can be regenerated from saved results.
- Check nonlinear spatial aggregation order using an event whose local maxima occur on different days.
- For inferential products, show simulation-based coverage or held-out validation matched to the claim.
- Retain at least one example where a conclusion changes sign under a legitimate sensitivity variant.

**Research judgment:** the highest-value next additions are seasonal redistribution, transparent variability
qualification, joint-change views and membership sensitivity. More polished quantile fans or complex
weighting should not outrun the data support. The recent CMIP review proposes a five-model initial minimum
but also favors target-specific assessment; neither five nor the lab's ten-model display heuristic proves
adequacy for regional tails, variability or independence. [R01] [R12]

## 12. Expanded academic references and evidence notes

Each identifier links directly to the publication or assessment. This bibliography extends, rather than
replaces, S1–S14 in the starter note. Short evidence notes identify the role of each source. “Extract” means
the synthesis relied on indexed/accessible extracts rather than a complete reading of that publication.

### Ensemble design, assessments and communication

- **R01.** Katzenberger, A., et al. (2026). *Developing Guidelines for working with Multi-Model Ensembles
  in CMIP*. Earth System Dynamics, 17, 495–532. [R01] Current review of selection, dependence, extremes,
  ensemble size, regridding and large ensembles. Full article sections consulted; recommendations remain
  context-dependent rather than universal adequacy rules.
- **R02.** Gutiérrez, J. M., et al. (2021). *Atlas*. In IPCC AR6 WGI, *Climate Change 2021: The Physical
  Science Basis*. [R02] Baselines, regional synthesis, warming-level views and Cross-Chapter Box Atlas.1
  robustness methods. Assessment extracts consulted; full-text requests were blocked.
- **R03.** Arias, P. A., et al. (2021). *Technical Summary*. IPCC AR6 WGI. [R03] Twenty-year warming-level
  framing and distinctions among map uncertainty methods. Assessment extracts consulted.
- **R04.** Doblas-Reyes, F. J., et al. (2021). *Linking Global to Regional Climate Change*. IPCC AR6 WGI,
  Chapter 10. [R04] Regional information, multiple evidence lines and construction/interpretation limits.
  Assessment extracts consulted; full-text request was blocked.
- **R05.** Bannister, H. J., Blackwell, P. G., Hyder, K., & Webb, T. J. (2021). *Improving the visual
  communication of environmental model projections*. Scientific Reports, 11, 19157. [R05] Empirical
  comparison of ten ensemble displays. Author-repository abstract and indexed paper extracts consulted.
- **R06.** Daron, J. D., Lorenz, S., Wolski, P., Blamey, R. C., & Jack, C. (2015). *Interpreting climate
  data visualisations to inform adaptation decisions*. Climate Risk Management, 10, 17–26. [R06]
  Climate-adaptation user study; Figure 2 compares displays of identical rainfall projection information.
  Repository abstract and published-paper extracts/captions consulted.
- **R07.** Harold, J., Lorenzoni, I., Shipley, T. F., & Coventry, K. R. (2016). *Cognitive and psychological
  science insights to improve climate change data visualization*. Nature Climate Change, 6, 1080–1089.
  [R07] Cognitive-design review. Accessible publisher sections and figure descriptions consulted.
- **R08.** Müller, L., & Döll, P. (2024). *Quantifying and communicating uncertain climate change hazards
  in participatory climate change adaptation processes*. Geoscience Communication, 7, 121–144. [R08]
  Local water-sector example, percentile boxes and stakeholder evaluation. Full text/captions consulted;
  Figure 5 image inspected. Its pooling, percentile truncation and evaluation limits need explicit review.

### Variability, dependence and inference

- **R09.** Lehner, F., et al. (2020). *Partitioning climate projection uncertainty with multiple large
  ensembles and CMIP5/6*. Earth System Dynamics, 11, 491–508. [R09] Multi-large-ensemble uncertainty
  decomposition; regional bias in single-realization fitting. Methods and figure captions consulted.
- **R10.** Deser, C. (2020). *“Certain Uncertainty”: The Role of Internal Climate Variability in Projections
  of Regional Climate Change and Risk Management*. Earth's Future, 8, e2020EF001854. [R10] Regional
  risk-management interpretation of internal variability. Publisher abstract/extracts consulted.
- **R11.** Maher, N., et al. (2025). *The updated Multi-Model Large Ensemble Archive and the Climate
  Variability Diagnostics Package: new tools for the study of climate variability and change*.
  Geoscientific Model Development, 18, 6341–6365. [R11] MMLEAv2 and CVDPv6; fairer model–observation
  comparisons and member diagnostics. Full abstract/introduction and archive description consulted.
- **R12.** Milinski, S., Maher, N., & Olonscheck, D. (2020). *How large does a large ensemble need to be?*
  Earth System Dynamics, 11, 885–901. [R12] Target/error-specific ensemble-size assessment. Published
  methods summary consulted; initial-condition examples should not be equated with independent CMIP models.
- **R13.** Abramowitz, G., et al. (2019). *ESD Reviews: Model dependence in multi-model climate ensembles:
  weighting, sub-selection and out-of-sample testing*. Earth System Dynamics, 10, 91–105. [R13]
  Dependence and evaluation of selection/weighting. Review sections consulted.
- **R14.** Kuma, P., Bender, F. A.-M., & Jönsson, A. R. (2023). *Climate Model Code Genealogy and Its
  Relation to Climate Feedbacks and Sensitivity*. Journal of Advances in Modeling Earth Systems,
  15, e2022MS003588. [R14] Component/genealogy dependence beyond institutions. Publisher extracts and
  the genealogy discussion reproduced in R01 consulted.
- **R15.** Brunner, L., et al. (2020). *Reduced global warming from CMIP6 projections when weighting models
  by performance and independence*. Earth System Dynamics, 11, 995–1012. [R15] ClimWIP application and
  testing; global-temperature case rather than validation of local precipitation weighting.
- **R16.** Hausfather, Z., Marvel, K., Schmidt, G. A., Nielsen-Gammon, J. W., & Zelinka, M. (2022).
  *Climate simulations: recognize the ‘hot model’ problem*. Nature, 605, 26–29. [R16] Published
  commentary on CMIP6 warming interpretation. Article extracts consulted; not an empirical local study.
- **R17.** Pendergrass, A. G., Knutti, R., Lehner, F., Deser, C., & Sanderson, B. M. (2017).
  *Precipitation variability increases in a warmer climate*. Scientific Reports, 7, 17966. [R17]
  Variability across temporal scales, distinct from mean change. Publisher abstract/extracts consulted.
- **R18.** Suarez-Gutierrez, L., & Maher, N. (2026). *Temperature variability projections remain uncertain
  after constraining them to best performing Large Ensembles of individual Climate Models*. Nature
  Communications, 17, 314. [R18] Historical variability screening need not resolve future disagreement.
  Publisher abstract/results extracts consulted. Online publication December 2025; 2026 volume citation.
- **R19.** Hawkins, E., & Sutton, R. (2012). *Time of emergence of climate signals*. Geophysical Research
  Letters, 39, L01702. [R19] Signal/noise emergence and modeled variability differences. Publisher
  abstract and author-repository paper extracts consulted.

### Extremes, drought and regional processes

- **R20.** Zhang, X., et al. (2011). *Indices for monitoring changes in extremes based on daily temperature
  and precipitation data*. WIREs Climate Change, 2, 851–870. [R20] Academic foundation for standard
  extreme indices; use the exact index definitions in implementation.
- **R21.** Sillmann, J., Kharin, V. V., Zwiers, F. W., Zhang, X., & Bronaugh, D. (2013). *Climate extremes
  indices in the CMIP5 multimodel ensemble: Part 2. Future climate projections*. Journal of Geophysical
  Research: Atmospheres, 118, 2473–2493. [R21] Global/regional projection-index example. Publisher
  abstract/method extracts consulted; CMIP5 examples are precedents, not CMIP6 regional findings.
- **R22.** Coles, S. (2001). *An Introduction to Statistical Modeling of Extreme Values*. Springer. [R22]
  GEV/GPD foundation and diagnostics; book metadata/description checked, not a complete book review.
- **R23.** Vicente-Serrano, S. M., Beguería, S., & López-Moreno, J. I. (2010). *A Multiscalar Drought Index
  Sensitive to Global Warming: The Standardized Precipitation Evapotranspiration Index*. Journal of
  Climate, 23, 1696–1718. [R23] SPEI foundation. Publisher abstract/method extracts consulted.
- **R24.** Beguería, S., Vicente-Serrano, S. M., Reig, F., & Latorre, B. (2014). *Standardized precipitation
  evapotranspiration index (SPEI) revisited: parameter fitting, evapotranspiration models, tools, datasets
  and drought monitoring*. International Journal of Climatology, 34, 3001–3023. [R24] Fitting and PET
  choices. Publisher abstract/extracts consulted.
- **R25.** Milly, P. C. D., & Dunne, K. A. (2016). *Potential evapotranspiration and continental drying*.
  Nature Climate Change, 6, 946–949. [R25] Methodological sensitivity of demand-based drying estimates.
  Publisher abstract and article extracts consulted.
- **R26.** Zscheischler, J., et al. (2020). *A typology of compound weather and climate events*.
  Nature Reviews Earth & Environment, 1, 333–347. [R26] Preconditioned, multivariate, temporal and spatial
  compounding; definition should follow the impact mechanism. Publisher text/abstract consulted.
- **R27.** Dunning, C. M., Black, E., & Allan, R. P. (2018). *Later Wet Seasons with More Intense Rainfall
  over Africa under Future Climate Change*. Journal of Climate, 31, 9719–9738. [R27] Regional season
  timing, intensity and frequency. Publisher methods/results extracts and institutional abstract consulted.
- **R28.** Cai, W., et al. (2021). *Changing El Niño–Southern Oscillation in a warming climate*.
  Nature Reviews Earth & Environment, 2, 628–644. [R28] ENSO processes and warming response; model-index
  diagnostics require additional data. Author/institutional abstract and published-paper extracts consulted.
- **R39.** Han, J., et al. (2024). *Streamflow seasonality in a snow-dwindling world*. Nature,
  629, 1075–1081. [R39] Catchment evidence qualifying simple snow/flow timing heuristics. Publisher
  abstract and indexed article extracts consulted; observational study, not a projection method.

### Processing, warming pathways and decision context

- **R29.** Jones, P. W. (1999). *First- and Second-Order Conservative Remapping Schemes for Grids in
  Spherical Coordinates*. Monthly Weather Review, 127, 2204–2210. [R29] Conservative spatial transfer
  foundation. Publisher method extracts consulted; conservation is not validation of extremes.
- **R30.** Maraun, D., et al. (2017). *Towards process-informed bias correction of climate change
  simulations*. Nature Climate Change, 7, 764–773. [R30] Bias-adjustment/process limits, including
  limits of ordinary cross-validation. Publisher/institutional abstract and paper extracts consulted.
- **R31.** Lange, S. (2019). *Trend-preserving bias adjustment and statistical downscaling with ISIMIP3BASD
  (v1.0)*. Geoscientific Model Development, 12, 3055–3070. [R31] Quantile-specific trend preservation
  and separating adjustment from downscaling. Article methods and Figure 1 caption consulted.
- **R32.** Cannon, A. J. (2018). *Multivariate quantile mapping bias correction: an N-dimensional probability
  density function transform for climate model simulations of multiple variables*. Climate Dynamics,
  50, 31–49. [R32] MBCn/dependence adjustment. Publisher abstract/method extracts consulted; online 2017,
  volume year 2018. Not a guarantee of future dependence accuracy.
- **R33.** Roldán-Gómez, P. J., De Luca, P., Bernardello, R., & Donat, M. G. (2025). *Regional irreversibility
  of mean and extreme surface air temperature and precipitation in CMIP6 overshoot scenarios associated
  with interhemispheric temperature asymmetries*. Earth System Dynamics, 16, 1–27. [R33] Regional
  pathway/history effects at similar warming. Published abstract and article sections consulted.
- **R34.** Bevacqua, E., Fischer, E., Sillmann, J., & Zscheischler, J. (2026). *Moderate global warming does
  not rule out extreme global climate outcomes*. Nature. [R34] Coherent spatial extremes and conditional
  adverse outcomes. Publisher methods/results and Extended Data Figure 6 descriptions consulted.
- **R35.** Shepherd, T. G., et al. (2018). *Storylines: an alternative approach to representing uncertainty
  in physical aspects of climate change*. Climatic Change, 151, 555–571. [R35] Conditional physical
  futures and event sequencing. Published text and Figure 1 description consulted.
- **R36.** Brown, C., Ghile, Y., Laverty, M., & Li, K. (2012). *Decision scaling: Linking bottom-up
  vulnerability analysis with climate projections in the water sector*. Water Resources Research,
  48, W09537. [R36] Projection connection to independent vulnerability exploration. Publisher article
  extracts consulted; bibliography also resolved through the climate-stress-testing skill.
- **R37.** Fowler, K. J. A., et al. (2024). *Climate stress testing for water systems: Review and guide
  for applications*. WIREs Water, 11, e1747. [R37] Current water-sector review of stressors, exposure
  spaces and practical choices. Published text and graphical-abstract description consulted.
- **R38.** Wilks, D. S. (1997). *Resampling Hypothesis Tests for Autocorrelated Fields*. Journal of
  Climate, 10, 65–82. [R38] Temporal/spatial dependence in resampling. Publisher abstract/method
  extracts consulted; foundation, not validation of a particular future-WF2 bootstrap.
- **R40.** van der Bles, A. M., et al. (2019). *Communicating uncertainty about facts, numbers and science*.
  Royal Society Open Science, 6, 181870. [R40] Review of direct uncertainty and uncertainty about the
  evidence. Published abstract/indexed paper extracts consulted.
- **R41.** Crameri, F., Shephard, G. E., & Heron, P. J. (2020). *The misuse of colour in science
  communication*. Nature Communications, 11, 5444. [R41] Perceptual uniformity and accessible scientific
  color maps. Publisher article sections and author-paper extracts consulted.
- **R42.** Guttman, N. B. (1999). *Accepting the Standardized Precipitation Index: A Calculation Algorithm*.
  JAWRA Journal of the American Water Resources Association, 35, 311–322. [R42] SPI calculation precedent and
  distribution-fitting choices. Published abstract/extracts consulted.

[R01]: https://doi.org/10.5194/esd-17-495-2026
[R02]: https://www.ipcc.ch/report/ar6/wg1/chapter/atlas/
[R03]: https://www.ipcc.ch/report/ar6/wg1/chapter/technical-summary/
[R04]: https://www.ipcc.ch/report/ar6/wg1/chapter/chapter-10/
[R05]: https://doi.org/10.1038/s41598-021-98290-4
[R06]: https://doi.org/10.1016/j.crm.2015.06.007
[R07]: https://doi.org/10.1038/nclimate3162
[R08]: https://doi.org/10.5194/gc-7-121-2024
[R09]: https://doi.org/10.5194/esd-11-491-2020
[R10]: https://doi.org/10.1029/2020EF001854
[R11]: https://doi.org/10.5194/gmd-18-6341-2025
[R12]: https://doi.org/10.5194/esd-11-885-2020
[R13]: https://doi.org/10.5194/esd-10-91-2019
[R14]: https://doi.org/10.1029/2022MS003588
[R15]: https://doi.org/10.5194/esd-11-995-2020
[R16]: https://www.nature.com/articles/d41586-022-01192-2
[R17]: https://doi.org/10.1038/s41598-017-17966-y
[R18]: https://doi.org/10.1038/s41467-025-67005-y
[R19]: https://doi.org/10.1029/2011GL050087
[R20]: https://doi.org/10.1002/wcc.147
[R21]: https://doi.org/10.1002/jgrd.50188
[R22]: https://doi.org/10.1007/978-1-4471-3675-0
[R23]: https://doi.org/10.1175/2009JCLI2909.1
[R24]: https://doi.org/10.1002/joc.3887
[R25]: https://doi.org/10.1038/nclimate3046
[R26]: https://doi.org/10.1038/s43017-020-0060-z
[R27]: https://doi.org/10.1175/JCLI-D-18-0102.1
[R28]: https://doi.org/10.1038/s43017-021-00199-z
[R29]: https://journals.ametsoc.org/view/journals/mwre/127/9/1520-0493_1999_127_2204_fasocr_2.0.co_2.xml
[R30]: https://doi.org/10.1038/nclimate3418
[R31]: https://doi.org/10.5194/gmd-12-3055-2019
[R32]: https://doi.org/10.1007/s00382-017-3580-6
[R33]: https://doi.org/10.5194/esd-16-1-2025
[R34]: https://doi.org/10.1038/s41586-026-10237-9
[R35]: https://doi.org/10.1007/s10584-018-2317-9
[R36]: https://doi.org/10.1029/2011WR011212
[R37]: https://doi.org/10.1002/wat2.1747
[R38]: https://journals.ametsoc.org/view/journals/clim/10/1/1520-0442_1997_010_0065_rhtfaf_2.0.co_2.xml
[R39]: https://doi.org/10.1038/s41586-024-07299-y
[R40]: https://doi.org/10.1098/rsos.181870
[R41]: https://doi.org/10.1038/s41467-020-19160-7
[R42]: https://doi.org/10.1111/j.1752-1688.1999.tb03592.x
