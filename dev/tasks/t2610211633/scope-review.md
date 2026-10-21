# Crop-water indicator scope review

Reviewed 21 October 2026 against toolbox `9887be49` in session-1. This is an inspection-based
assessment, not implementation approval or validation of Alexandria data. The original brief and both
sibling context documents were read; their formulas remain the proposed scientific specification.

Owner decision after review: backward compatibility with existing study cases is not required while
the toolbox is in development. Contract changes may require regeneration of development runs. Do not
implement legacy readers, migration machinery or historical-artifact compatibility for this task.

Further owner decisions: v1 calculates the proposed ET formulas using existing model AET and forcing
PET, with scientific limitations documented for later review. Every non-discharge variable uses the
current subcatchment-mean output convention. Matched unstressed ET, agricultural masks and revised
spatial weighting are follow-up topics, not prerequisites for v1. These decisions supersede the case
brief's stricter ET-compatibility and area-weighting conditions for this initial implementation.

## Recommendation

Proceed with the six methods as a hydroclimatic agricultural screening set, subject to the decisions
below. Four methods have winter/summer selections, giving ten declarations in total. Retain daily
positive climatic deficits, strict thresholds, signed net recharge, ratios of sums, complete periods,
period diagnostics and equal-member group reduction. The lean arithmetic and exclusions of crop
modelling, calibration, composite scores and new GIS processing are appropriate.

This is a cross-cutting WF4 extension followed by a set implementation. ERFA supplies the package,
registration, independent-check and publication pattern, but does not establish paired-input support.

## Findings and required changes to the assignment

1. **Calculate existing AET/PET and document its interpretation.** Wflow documents its forcing as
   reference evapotranspiration; vegetation coefficients, canopy fraction and evaporation components
   affect its use. Same run, dates and area are necessary but insufficient for compatibility.
   For v1, retain both proposed formulas: `100 * (1 - sum(AET)/sum(PET))` and counts of
   `AET/PET < 0.5` where `PET >= 1 mm/day`. Use existing model AET and forcing PET without a new
   denominator, crop correction or compatibility gate. Document these as screening proxies: differences
   can reflect vegetation and evaporation components as well as water availability. They are not
   calibrated crop stress or damage estimates. Preserve negative deficits and flag AET above PET.
   Revisit the scientific assumptions later; ordinary units, alignment and missing-data checks remain.
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

3. **Make PET production and the new retention contract explicit work.** PET is absent from both
   `model/setup_gauges_and_outputs.py` and `experiment/wflow_response_reader.py`; shared output codes
   and configuration/template consumers also need review. Prefer a verified native PET output on the
   same subcatchment support as P/AET for new runs. A forcing-file bridge is an alternative only with
   explicit immutable provenance, clock and aggregation contracts; its complexity is not free.
   `response_inventory.response_reader_revision()` hashes the native reader. Changing it currently
   refuses older retained experiments except a narrowly pinned historical exception. The owner accepts
   this break for development cases: update the contract directly, retain integrity checks and report
   which runs need regeneration. No legacy read path or migration is required. Do not silently rerun
   or overwrite existing simulations as part of indicator evaluation.

4. **Correct the blanket identity acceptance criterion.** Adding a standalone set should leave
   unrelated identities unchanged. Editing shared execution or native interpretation code legitimately
   changes dependent identities under the current contract. Require deliberate new identities where
   dependencies change. Historical artifact readability and identity continuity are not acceptance
   gates for this task; retain input provenance and deterministic identity for the new contracts.

5. **Use subcatchment means for all non-discharge inputs in v1.** Follow the existing `mean` reducer
   for P, PET, AET, recharge and other non-Q variables; Q remains an outlet/gauge series. Calculate
   indicators from daily subcatchment means, rather than averaging cell-level indicator results.
   Keep paired variables on the same subcatchment support. Document the current reducer and its
   spatial-representativeness limits; no agricultural mask, aquifer mask or new weighting scheme is
   required. Subcatchment means do not establish agricultural-area or aquifer-specific conditions.
   Revisit these choices later. Q reach interpretation remains separate: outlet drainage cannot
   establish irrigation-supply failure.

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

1. Resolve case bindings, Qcrit and paired-input/publication design using the settled v1 assumptions.
2. Implement PET retention and paired inputs; keep current single-input sets working on new contracts.
3. Implement six kernels, ten declarations, complete-period diagnostics and documented assumptions.
4. Run independent arithmetic and boundary checks, affected contract/publication regression checks,
   and a small indicator-only integration. Exercise native retention separately on an isolated case
   if output production changes. Report real case readiness separately from software readiness.

The brief's numerical examples and focused verification are suitable. Add tests for mismatched paired
locations/dates, secondary-input identity changes, Qcrit provenance changes, single-input sets on new
contracts and period-diagnostic export. Reuse ERFA's scoped preparation pattern so paired
frames and period partitions are not rebuilt per declaration. No broad hydrological rerun is needed
for arithmetic alone; output-path changes need their own bounded execution evidence.

No production series, active Alexandria configuration or numeric Qcrit was established by this review.
The case brief remains the source for formulas and regional settings, with the owner decisions above
overriding its ET-compatibility and spatial-weighting prerequisites for v1. Its
validation-reference path should be repository-relative `dev/reference/dev-validation.md`.
