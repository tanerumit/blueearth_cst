```yaml
verdict: revise
doc_version: design-v1.md
findings:
  - id: dom-1
    severity: major
    section: "5. Numerical contracts (item 5) / 4. Figure contract"
    finding: >-
      The figures use a different change than the plausibility overlay. Figures show changes on a
      30-water-year window centred on the horizon, measured against a fixed 1985-2014 reference
      (lab core.py:258-260 `_windows`; core.py:111-114). The overlay CSV that CST-API consumes uses the
      configured windows instead. On P0 those are a 2000-2014 reference and a 2046-2054 horizon
      (design.md line 11 and section 5.5). So the folder `period-2036-2065/` and the
      `summary/*_change_factors_*.csv` from the same run report systematically different deltas for the
      same model, scenario and horizon. The design treats the fixed reference only as a "domain lens to
      confirm" and never says how a reader reconciles the two. The two constructions do not contradict
      each other: a 30-year reference and a 30-year future window are the right choice for variability
      and seasonal statistics. The gap is that the relationship is neither stated nor recorded.
    rationale: >-
      Observable consequence: on P0 the reference shifts 7.5 years earlier (centre 2007 to 1999.5), so
      the figure delta T exceeds the CSV delta T by roughly the warming over that interval (order
      0.1-0.3 degC in the tropics). A user who checks the cloud figure (F3.6b) against the overlay
      surface sees disagreeing numbers with no explanation. In CST the overlay must be measured against
      the stress-test zero point (the configured reference), so the figures, not the CSV, are the ones
      that drift from the decision context.
    suggested_fix: >-
      Record both window pairs, aligned and analysis, in analysis_record.json and in every
      period-folder caption. State "analysis-window changes; the overlay CSV uses <ref>/<horizon>". Use
      the configured reference_window as the analysis reference when it already spans at least 30 water
      years, and use 1985-2014 only otherwise; record which one was used. Optionally add the aligned
      per-model point to F3.6b as a hollow marker so the offset is visible.
  - id: dom-2
    severity: major
    section: "6. Robustness (analysis window leaves the series)"
    finding: >-
      Centring a 30-year window on the horizon makes standard end-of-century horizons unavailable. The
      AR6 long-term period 2081-2100 gives c=2090, which needs 2076-2105, past the 2100 end of most
      CMIP6 scenario runs. The design marks this `unavailable` and draws placeholders. So the most-used
      far horizon gets no seasonal, variability, agreement or cloud figures.
    rationale: >-
      Observable consequence: a user who configures the AR6 periods gets 10 placeholder figures for the
      far horizon. That is the horizon where plausibility matters most. Silent unavailability is avoided,
      but the method fails an ordinary configuration. The default template (2070-2100) escapes only by
      accident of its bounds.
    suggested_fix: >-
      Shift the window to fit inside the series rather than drop it: end at the last complete water
      year, so 2071-2100. Record the shift (requested versus used window) in analysis_record.json and in
      the caption. Declare it unavailable only when fewer than 30 water years exist at all.
  - id: dom-3
    severity: major
    section: "2. Module boundaries (C4 variability ratios) / 4. Figure contract (F3.5a, F3.5c)"
    finding: >-
      The variability ratios are shown without any sampling-noise reference. A member ratio of detrended
      SDs from two 30-value windows behaves roughly like sqrt(F) with about 28/28 degrees of freedom.
      Under no change, its central 90 % range is about 0.78-1.28 and the 95 % range about 0.73-1.38, and
      interannual autocorrelation (temperature persistence, ENSO) widens that further. The lab's own note
      shows that the choice of detrending method alone moves single-member ratios by up to +/-0.25 and
      flips 5 % of cells across 1 (variability.py:7-13). Neither F3.5a nor F3.5c, as designed, carries a
      null band, and the design does not declare the ratios to be noise-dominated.
    rationale: >-
      Observable consequence: whisker ranges of 0.7-1.4 across models and members will read as model
      disagreement or as projected variability change, when most of the spread is what stationary noise
      produces. That is an overconfident or misattributed uncertainty statement on a decision-facing
      figure.
    suggested_fix: >-
      Add a null reference band to F3.5a and F3.5c. The cheapest version is the F-distribution
      interval for n=30 with ddof matched to the detrended residuals (28 df). The data-driven version
      pairs ratios of two non-overlapping historical 30-year windows per member, which also absorbs
      autocorrelation. Record the band's method in analysis_record.json and say in the caption that
      ratios inside the band are indistinguishable from sampling noise.
  - id: dom-4
    severity: major
    section: "2. Module boundaries (C4 pooled member ratios, F3.5c) / 6. Robustness (single member per model)"
    finding: >-
      F3.5c pools member ratios across models. With 1-5 members per model, models with more members
      get proportionally more weight. Every other product in the design is equal-model-weighted
      (means.py:7-11 states members "are never pooled as if they were independent models"). The design
      gives no rationale for the exception and does not label it.
    rationale: >-
      Observable consequence: the F3.5c distribution is driven by the few 5-member models, which on P0
      cluster in a few code families. It can disagree in centre with F3.5a for reasons that are
      artefacts of ensemble composition, not climate. A reader comparing the two figures cannot tell.
    suggested_fix: >-
      Either weight each member 1/n_members(model), so the pooled histogram is equal-model, or keep the
      pooling and caption it explicitly. In that case, show per-model member counts and state that the
      figure samples internal variability within models and is not an ensemble distribution. Combine
      this with the null band from dom-3, which is the comparison F3.5c actually needs.
  - id: dom-5
    severity: major
    section: "5. Numerical contracts (item 4, dry-reference guard)"
    finding: >-
      The analysis table mixes two dry-reference rules, and the design's equivalence claim is wrong. The
      toolbox kernel compares each statistic's own reference value with the threshold
      (get_change_climate_proj.py:249-251, `flagged = hist_stat < threshold`). For the std statistic it
      therefore compares an SD with a 0.1 mm/day mean-rate threshold. The comparison is in the same unit
      but has a different meaning. The lab rule keys every statistic of a period on the reference MEAN
      (core.py:302-321). Section 5.4's claim that the two "differ only for a reference mean below
      0.1 mm/day" is false. They also differ wherever the reference SD is below 0.1 mm/day while the
      mean is above it, for example a reliably wet month with low interannual SD. There the toolbox nulls
      the std % change and the lab keeps it. The P0 evidence (23,800 rows all `ok`) is from one humid
      basin and does not support the general claim.
    rationale: >-
      Observable consequence: in one `changes.csv`, monthly rows (kernel rule) and seasonal rows (lab
      rule) can disagree on whether a std relative change exists for comparable conditions. On a
      semi-arid basin (any-model, any-basin requirement) dry-season months and seasons will be flagged
      inconsistently. Downstream counts (n_models in agreement and summary) then differ by period for
      a reason unrelated to climate. In addition, 0.1 mm/day is a weak guard for percentage change:
      references of 0.1-0.5 mm/day still yield % changes of several hundred.
    suggested_fix: >-
      Apply one rule to all analysis rows: per period, keyed on the reference mean, which is what the
      lab rule does. Post-process the kernel's analysis-slice output so the kernel and the aligned CSV
      stay unchanged. Document that the aligned CSV keeps the per-statistic rule. Correct the section
      5.4 claim, and add a synthetic dry-season test case.
  - id: dom-6
    severity: major
    section: "2. Module boundaries (sign agreement) / 4. Figure contract (F5.1)"
    finding: >-
      The sign agreement (k/n of models sharing the median's sign, agreement.py:44-69) has three gaps.
      It does not account for noise: a model whose 30-year mean change is inside its own internal
      variability counts as a vote. It treats the 13 models as independent, although the Kuma families
      are computed and then used only for display in F3.1. And the design does not fix how the
      "heuristic band" and the blue/red colouring are labelled. A k/n alone on a 2x2-cell basin does not
      separate "models agree on a change" from "models agree on noise".
    rationale: >-
      Observable consequence: for monthly precipitation on a small basin, 10/13 agreement can arise
      under no forced change once family duplicates are allowed for (effective n is well below 13).
      Colouring a cell blue or red by median sign with no noise criterion reads as AR6 "robust change"
      hatching, which this is not, so the overlay overstates confidence.
    suggested_fix: >-
      Show the number of families agreeing beside k/n (k_fam/n_fam). Label the table "sign agreement
      among models (not a likelihood statement)". Grey out or mark cells whose |median| is below the
      band, and declare the band values as heuristics in the caption. Optionally add the AR6 simple
      approach: the share of models whose change exceeds the inter-window SD of their historical 30-year
      means. Do not use calibrated likelihood language.
  - id: dom-7
    severity: major
    section: "9. Validation plan"
    finding: >-
      Parity with the lab is the only numerical oracle. It proves that the port is faithful. It cannot
      falsify any of the methods: detrending adequacy, ratio reduction, sign counting, window placement,
      or the dry guard. Known-answer tests are mentioned only as "sqrt(2) ratio, hand medians" (section 10,
      commit 3). No test exercises the statistical behaviour under a known null.
    rationale: >-
      Observable consequence: a methodological defect shared by lab and port (for example a ddof or
      label mismatch in detrending, a log-mean reduction error, or an off-by-one water year in the
      analysis window) passes every gate in the plan, because both sides compute the same wrong number.
    suggested_fix: >-
      Add synthetic known-answer tests. (a) Linear trend plus white noise: std_detrended recovers the
      noise SD within sampling error and std does not. (b) A stationary series in both windows: the
      median member ratio is about 1, and the 5-95 % spread matches the F-band from dom-3. (c) Null
      changes with symmetric noise: the sign-agreement fraction is about 0.5. (d) A non-January water
      year: exact window bounds. These are cheap and independent of the lab.
  - id: dom-8
    severity: minor
    section: "2. Module boundaries (C3 trajectories, F3.4)"
    finding: >-
      The unsmoothed annual trajectory band (median and min-max across model means of annual anomalies)
      mixes interannual variability with model spread. Its width also depends on how many members each
      model averages. Min-max grows with the number of models. AR6 Fig. 4.2 uses this style too, so the
      method is acceptable, but the caption must say what the band is.
    suggested_fix: >-
      Caption: "range across N models of annual anomalies (each the mean of its members); includes
      year-to-year variability, so it is wider than the spread of the forced response". Report the
      members per model in the record.
  - id: dom-9
    severity: minor
    section: "2. Module boundaries (member-to-model-to-ensemble reduction)"
    finding: >-
      The member-to-model-to-ensemble reduction with equal model weight, plus a median and min-max, and
      an IQR only from 10 or more models (means.py:7-11, 34, 113-133) is standard and defensible as
      ensemble spread. The 10-model floor is a declared heuristic. The design should carry the lab's
      wording ("ensemble spread, never a confidence interval") into the captions, and note that equal
      model weight still counts code-family duplicates as separate models.
  - id: dom-10
    severity: minor
    section: "2. Module boundaries (seasonal values, detrended SD)"
    finding: >-
      The method is sound as specified. OLS detrending within each 30-year window, ddof 0
      (core.py:237-245), is justified by the lab's quadratic and high-pass checks (variability.py:7-13).
      ddof cancels in the ratios. Geometric-mean reduction of ratios is the correct scale. The
      precipitation CV of period integrals, the month-length weighting, and the temperature SD in place
      of CV all hold. One check is missing: near horizons whose 30-year window starts before 2015 need
      the historical and scenario series joined for the FUTURE window as well (the lab joins them only
      for C3 trajectories, trajectories.py:76). The design does not say whether 2.05b does this.
    suggested_fix: >-
      State the join rule for analysis future windows that start before 2015 (join or unavailable) and
      add a test for a 2011-2040 style horizon.
  - id: dom-11
    severity: minor
    section: "6. Robustness (model not in Kuma et al. 2023)"
    finding: >-
      An `unlisted` family is a safe fallback, but it discards information that is cheap to recover.
      A new model from a listed institution (for example a new member of the CESM2 or MPI-ESM families)
      could take a provisional family from the institution match, flagged as inferred. Families serve
      display only today. If dom-6 adopts family counts, the fallback becomes material: count each
      unlisted model as its own family, which is conservative.
  - id: dom-12
    severity: minor
    section: "5. Numerical contracts (item 5)"
    finding: >-
      The agreement bands (temp 0.5 degC, precip 5 %, 0.1 mm/day; agreement.py:27) are basin-agnostic
      constants. For an arid basin, 0.1 mm/day may exceed the climatology of some months. They should
      be documented as display heuristics, not detection thresholds, and recorded in
      analysis_record.json (the design already lists them as module constants).
premise_dispositions:
  - premise: "Lab aligned change table reproduces the toolbox tables"
    disposition: supported
    note: "15,600 comparisons within 0.001 on 3-dp CSVs; it validates the aligned port only, not the analysis-window methods (dom-7)."
  - premise: "Baseline covers WF2 change-factor CSVs but no WF2 figure"
    disposition: contested
    note: "dev/scripts/check_baseline.py:313-330 lists three WF2 PNGs as FIGURE_KINDS targets (outside the default gate). The design's section 7 already says so; the register row should read 'no WF2 figure in the default gate'. Settled by running grep png on the manifest."
  - premise: "Baseline manifest is stale for the current config"
    disposition: supported
    note: ""
  - premise: "WF2 figure set is declared from one function"
    disposition: supported
    note: ""
  - premise: "WF0 layout tokens exist in the toolbox"
    disposition: supported
    note: "The design compares values (diagnostic_figures.py:25-81 vs wf0_lab/figures.py:36-58). Not re-verified by this lens; not a domain question."
  - premise: "Monthly change factors ignore a non-January water year"
    disposition: supported
    note: "Consistent with the design's section 5.3 reading of derive_change_factors.py:225-235; code reading, no run."
  - premise: "Lab suite runs in acceptable time on P0"
    disposition: untestable as stated
    note: "'Acceptable' has no budget and '1-3 min' was not timed. Settled by the design's section 9 benchmark row with a G1-agreed budget."
  - premise: "Kuma et al. (2023) families cover the P0 models"
    disposition: supported
    note: "Supported for P0 only. Coverage of other models is unknown and is handled by the fallback (dom-11)."
  - premise: "Temperature CV is replaced by SD ratio"
    disposition: supported
    note: "Correct: CV in degC depends on the zero point. In K, the CV ratio equals the SD ratio times T_ref/T_fut (about 1 % for a few degrees of warming), so the SD ratio is the right statistic."
```
