# Crop-water indicator scope review

Reviewed 21 October 2026 against toolbox `9887be49` in session-1. This is an inspection-based
assessment, not implementation approval or validation of Alexandria data. The original brief and both
sibling context documents were read; their formulas remain the proposed scientific specification.

## Recommendation

Proceed with the six methods as a hydroclimatic agricultural screening set, subject to the decisions
below. Four methods have winter/summer selections, giving ten declarations in total. Retain daily
positive climatic deficits, strict thresholds, signed net recharge, ratios of sums, complete periods,
period diagnostics and equal-member group reduction. The lean arithmetic and exclusions of crop
modelling, calibration, composite scores and new GIS processing are appropriate.

This is a cross-cutting WF4 extension followed by a set implementation. ERFA supplies the package,
registration, independent-check and publication pattern, but does not establish paired-input support.

## Findings and required changes to the assignment

1. **Separate reference PET from an unstressed counterpart of AET.** Wflow documents its forcing as
   reference evapotranspiration; vegetation coefficients, canopy fraction and evaporation components
   affect its use. Same run, dates and area are necessary but insufficient for compatibility.
   Verify the installed model version, configured coefficients and exact output components before
   calling the ratio evaporative limitation. If only reference PET is available, explicitly describe
   the result as an AET/reference-PET proxy, with vegetation as a confounder, or leave those metrics
   unavailable pending a matched denominator. Relabelling alone does not establish compatibility.
   Do not reconstruct a new PET inside the indicator or silently change the six formulas.
   Evidence: [Wflow evaporation documentation](https://deltares.github.io/Wflow.jl/stable/model_docs/land/landhydrology_sbm.html)
   and [HydroMT crop-factor documentation](https://deltares.github.io/hydromt_wflow/stable/user_guide/5_setup_methods/setup_lulcmaps.html).
   These describe upstream semantics; the case configuration has not been verified.

2. **Extend the full input-to-publication contract.** `indicators/contract.py` declares one requirement;
   `indicators/temporal.py` validates every supplied series against it. `experiment/indicator_plan.py`
   selects one variable for evaluation and derives locations from it. `indicator_sets.py` and
   `indicator_artifacts.py` also assume one variable, including exported table tokens. Specify required
   inputs separately from the output table/location identity. Validate pairs by run, location, dates,
   calendar, timestep, units and spatial support; never silently intersect unmatched locations/dates.
   Existing scalar diagnostics can hold period values without a new indicator engine.

3. **Make PET production and retained-reader compatibility explicit work.** PET is absent from both
   `model/setup_gauges_and_outputs.py` and `experiment/wflow_response_reader.py`; shared output codes
   and configuration/template consumers also need review. Prefer a verified native PET output on the
   same subcatchment support as P/AET for new runs. A forcing-file bridge is an alternative only with
   explicit immutable provenance, clock and aggregation contracts; its complexity is not free.
   `response_inventory.response_reader_revision()` hashes the native reader. Changing it currently
   refuses older retained experiments except a narrowly pinned historical exception. Define and test
   a versioned/compatible read path before modifying it. Do not weaken integrity checks globally.
   Distinguish older runs with unavailable PET from older runs that should remain usable for Q sets.

4. **Correct the blanket identity acceptance criterion.** Adding a standalone set should leave
   unrelated identities unchanged. Editing shared execution or native interpretation code legitimately
   changes dependent identities under the current contract. Require stable identities for genuinely
   unaffected code, deliberate new identities where dependencies change, and continued readability of
   historical published artifacts. Do not require false identity stability to satisfy this task.

5. **Treat spatial support as evidence, not a location label.** Current non-Q outputs use subcatchment
   `mean`; Q uses outlet/gauge samples. These are different supports. A basin mean is a useful first
   implementation if labelled honestly, but is not an agricultural-area mean. If existing reducer
   weights differ from the brief's fixed-area-weight requirement, document that limitation or scope
   the change explicitly. Record mask/map, reducer and weighting with P/PET/AET bindings. Keep recharge
   support and Q reach meaning separate; outlet drainage cannot establish irrigation-supply failure.

6. **Specify baseline-threshold and calendar details before coding.** The existing explicit reference
   facility selects wet/dry months from unperturbed runs; it is not a historical Qcrit estimator.
   Prefer a small case-preparation step producing a location-keyed numeric threshold with baseline
   source identity, years, eligible complete summers, quantile method and units. Include the resolved
   thresholds/provenance in calculation identity; no scenario refitting. Define how missing AET on a
   known low-PET day affects completeness (strict paired completeness is the simplest initial rule).
   Pin season membership to explicit daily interval labels, test boundary timestamps, and distinguish
   absent timestamps (currently rejected by series validation) from NaNs and excluded edge windows.
   Keep October recharge accounting explicit if the host project's water-year anchor differs.

## Delivery sequence and evidence

1. Resolve scientific bindings and the minimal paired-input/publication/compatibility design.
2. Implement PET retention and the compatible paired-input path, preserving existing single-input use.
3. Implement six kernels, ten declarations, complete-period diagnostics and documented assumptions.
4. Run independent arithmetic and boundary checks, affected contract/publication regression checks,
   and a small indicator-only integration. Exercise native retention separately on an isolated case
   if output production changes. Report real case readiness separately from software readiness.

The brief's numerical examples and focused verification are suitable. Add tests for mismatched paired
locations/dates, secondary-input identity changes, Qcrit provenance changes, old retained Q-only runs,
old published artifacts and period-diagnostic export. Reuse ERFA's scoped preparation pattern so paired
frames and period partitions are not rebuilt per declaration. No broad hydrological rerun is needed
for arithmetic alone; output-path changes need their own bounded execution evidence.

No production series, active Alexandria configuration or numeric Qcrit was established by this review.
The case brief remains the source for intended formulas and provisional regional settings. Its
validation-reference path should be repository-relative `dev/reference/dev-validation.md`.
