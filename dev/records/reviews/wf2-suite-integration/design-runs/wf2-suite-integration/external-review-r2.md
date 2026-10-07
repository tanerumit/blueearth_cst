## Verdict
verdict: revise
doc_version: design-v4.md

## Findings

### ext3-1  [major]
- section: 5.12 Degenerate variability; 4. Figure contract; 6.1 Declared vs written
- finding: The eligibility correction resolves ext2-2 for constant series, but leaves dry-reference absolute precipitation changes contradictory. Section 5.4 and the §5.12 status table preserve absolute changes for `dry` rows. However, `mean_change_eligible` is explicitly true only for `ok`, `zero_reference_variability` and `zero_future_variability`. F3.2, model reductions and agreement then require that flag. The parenthetical statement that “dry keeps only the absolute change” does not reconcile the exhaustive eligibility predicate.
- rationale: An implementation following the predicate drops valid absolute precipitation changes from dry-reference members. An ensemble consisting of such members can have its absolute-change figure incorrectly listed as unavailable, despite retaining finite absolute changes in the member table. The constant-reference regression test does not exercise this case.
- suggested_fix: Define eligibility separately for absolute and relative mean changes, or key it explicitly by the statistic and units. A finite absolute mean change must remain eligible when the reference is dry; its relative counterpart must be ineligible. Add a dry-reference case through model reduction, availability, agreement and rendering.

### ext3-2  [major]
- section: 5.7 No-change sampling band; 5.11 Season-year contract; 9.2 Checks
- finding: The revised model-marker simulation addresses heterogeneous member parameters, but its specified inputs still contain counts and window overlap rather than the actual observation years and missing-year masks. Section 5.11 permits missing seasonal instances. Counts and overlap length alone do not determine the sampling distribution after separate OLS detrending: the retained time coordinates determine each regression projection, and the identities of shared observations determine dependence between the two residual statistics.
- rationale: Two eligible members can have identical reference/future counts and nominal window overlap yet require different null distributions because their missing years occur at different positions. Simulating contiguous observations or sharing every nominally overlapping year therefore benchmarks a different statistic from the reported ratio. The proposed unequal-count tests can pass while missing-season model markers receive incorrect `outside_null` classifications.
- suggested_fix: Pass each member’s actual retained reference and future year coordinates to `null_ratio_band`. Simulate over their union, select observations using the original masks, and apply the same time coordinates and detrending procedure as the table calculation. Include those coordinates in the cache key. Add coverage tests with internal missing years, including overlapping windows whose nominal overlap differs from their shared retained observations.