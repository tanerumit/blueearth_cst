## Verdict
verdict: revise
doc_version: design-v3.md

## Regression

- ext1-1: re-raised as ext2-1
- ext1-2: resolved
- ext1-3: re-raised as ext2-2
- ext1-4: resolved

## Findings

### ext2-1  [major]

- section: 5.7 No-change sampling band; 9.2 Checks
- finding: The model-marker CV band simulates m independent members “at the model’s own reference CV,” but the plotted statistic combines eligible member ratios whose reference CVs can differ. No model-level CV definition or member-specific parameterization is supplied. A geometric mean of heterogeneous CV ratios does not generally have the same null distribution as m ratios generated at one common CV. The m = 3 coverage test does not explicitly exercise heterogeneous reference CVs.
- rationale: Model markers can be filled using a sampling benchmark that does not represent their statistic, leaving the model-summary part of ext1-1 unresolved.
- suggested_fix: Simulate each eligible member using its own reference mean, detrended SD, observation years and overlap, then compute the same model geometric mean used in the table. Add independent coverage tests with heterogeneous member CVs and sample counts.

### ext2-2  [major]

- section: 5.12 Degenerate variability; 4. Figure contract; 6.1 Declared vs written
- finding: Section 5.12 explicitly preserves mean changes from `zero_*` rows for F3.2 and F3.6b, but §4 requires an `ok` change row for those products, and §6.1 instructs availability to apply that table. The design does not specify statistic-specific statuses or eligibility that reconcile these instructions.
- rationale: A valid constant-temperature or constant-wet-precipitation member can retain a meaningful mean change yet be excluded from change figures and paired cloud points. An entirely constant ensemble can therefore have those products incorrectly reported as unavailable.
- suggested_fix: Define eligibility separately for mean changes and variability statistics. Keep valid mean-change rows eligible regardless of variability status, and update the availability predicates accordingly. Test a constant reference series with a nonzero future mean change through reduction, availability and rendering.

### ext2-3  [minor]

- section: 5.7 No-change sampling band
- finding: The claimed disjoint-window identity with `sqrt(F(n_f-2, n_r-2))` omits the normalization factor for SDs computed with ddof 0. For unequal sample counts, the ratio is distributed as `sqrt(((n_f-2)/n_f)/((n_r-2)/n_r) * F(n_f-2, n_r-2))`. Seasonal completeness permits unequal counts, although the existing 30-versus-30 test cannot expose this distinction.
- rationale: The stated analytic oracle is incorrect for unequal sample counts and could reject a correct Monte Carlo implementation.
- suggested_fix: Correct the formula and add a disjoint unequal-count oracle test, such as 27 versus 29 complete season instances.