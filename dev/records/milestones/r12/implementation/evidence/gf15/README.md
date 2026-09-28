# GF15 estimator benchmark evidence

Owner authorization on 2026-09-12 covers the exact criteria in the accepted
[design section 7.5](../../../wf3-simulation-identity-design.md) and the
[reviewed recommendation](../p3/scientific-review-preparation.md#gf15-recommendation-for-the-owner-gate).
The coordinator records that approval under Master Gate 2. This is a bounded
estimator diagnostic; a correctly completed computation can fail its scientific
criteria. The [signed scientific verdict](scientific-handoff.md) records a
completed, failed benchmark requiring an owner method ruling.

## Reproduction

From the repository root, using the existing Pixi environment:

```powershell
pixi run --as-is python dev/milestones/r12/implementation/evidence/gf15/benchmark-estimator.py pilot --output .tmp/gf15-new-pilot --workers 4
pixi run --as-is python dev/milestones/r12/implementation/evidence/gf15/benchmark-estimator.py run --output .tmp/gf15-new-results --workers 4 *> .tmp/gf15-new-run.log
pixi run --as-is python dev/milestones/r12/implementation/evidence/gf15/review-retained-draws.py --results .tmp/gf15-new-results --output .tmp/gf15-new-review.json
```

Use absent output directories. The harness refuses to overwrite an existing
run. `summarize --output <completed-results>` recomputes summaries without
fitting again. It rewrites derived summaries and their inventory, so use a
disposable copy if checking an already retained record. A successful process
exit means execution completed; inspect `matrix-results.json` for scientific
pass/failure. Do not replace the approved criteria after observing results.

## Method and conventions

The matrix contains 12 base cells: SciPy GEV shape `c={-0.2,0,0.2}` and usable
block count `n={10,18,30,60}`. Each contains 1,000 deterministic IID draws. The
conventional extreme-value shape is `xi=-c`: negative SciPy `c` gives a heavy
upper tail; positive `c` gives a finite upper endpoint. Scale is one and base
location is zero. The independent inverse CDF is
`z_p=-expm1(c*log(-log(p)))/c`, with the Gumbel limit
`z_p=-log(-log(p))` at `c=0`. The formula is checked against
[SciPy's documented GEV convention](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.genextreme.html).

Each base cell uses `Generator(PCG64(SeedSequence([20260912, shape_index, n])))`,
where shape indices follow the order above. Uniform samples are transformed by
that analytical inverse CDF. No negative values are truncated, no endpoints are
clipped, and no draws are replaced. Retained `.npy` arrays preserve every base
sample. The independent reviewer regenerates them through SciPy's inverse CDF.

Every base draw is fitted once, then evaluated through two separate scalar
xclim `parametric_quantile` calls at `p=0.9` and `p=0.5`. This preserves the
installed upper-tail inverse-survival call rather than combining probabilities
into a different quantile call. The baseline fit can be shared because its
input and deterministic fitting call are identical. For each probability the
same sample is translated and actually refitted at each `rho={0,.05,.5,2,10}`,
using `mu=rho-z_p`. Thus `rho` is the true quantile divided by generating scale,
not the generating location, fitted scale or coefficient of variation.

The unchanged production path is xclim `fit(..., dist="genextreme")`, default
maximum likelihood, and scalar `parametric_quantile`; the installed source and
environment are hashed. The installed ML path initializes shape at 0.1,
location at sample mean minus `0.57722*sqrt(6*variance)/pi`, and scale at
`sqrt(6*variance)/pi`. Those are existing xclim choices and receive no overrides.
The ML path returns parameters without an optimizer success flag. Validity is
bounded to the production checks: nonconstant sample, no fitting exception,
finite parameters, positive scale and finite target quantile. Validity does not
certify a global likelihood optimum. The
[xclim fitting reference](https://xclim.readthedocs.io/en/stable/_modules/xclim/indices/stats.html)
describes the fitting interface; the hashed installed source is authoritative
for this execution. Controls verify exact parameter/quantile agreement against
the actual production `reduce_bundle` for both upper and lower metrics.

There are 132,000 fits and 144,000 quantile records: 12,000 baseline fits produce
24,000 records; 120,000 translated fits each produce one. Four worker processes
receive fixed fifty-draw chunks; scheduling cannot change the RNG streams.
Only empirical estimator performance in these stationary IID GEV fixtures is
assessed. The `p=0.5` level represents the median of annual seven-day minima,
not a rarer lower-tail probability. No hydrological time series, block
dependence, observed discharge regimes, calibration split, policy or climate
scenario is inferred from these mathematical fixtures.

## Retained records

- `results/criteria.json` locks the exact pre-execution matrix, formulas and
  criteria; `provenance.json` pins source bytes, versions and installed packages.
- `samples-*.npy` retain all base draws. `draws-*.jsonl.gz` retain every scalar
  estimate, fitted parameter, refusal, warning, error and translation decision.
  `draw` is zero-based within its shape/count cell. Baseline records have
  `ratio:null`; zero-ratio records have `relative_error:null` explicitly.
- `matrix-results.json` and `.csv` retain all 144 cells. Every fit refusal counts
  against its cell's 1,000 draws; error summaries state their valid-fit
  denominator. Quantiles use linear interpolation between order statistics.
- `fit-failures.jsonl.gz`, `fit-warnings.jsonl.gz`, and
  `translation-deviations.jsonl.gz` index every matching record without deleting
  it from the complete draw files. They may be valid empty gzip streams.
- `execution-progress.json` identifies every finished chunk and hash;
  `execution-completion.json` records total work and verifies source stability.
  `evidence-inventory.json` binds exact result bytes.
- `independent-review.json` checks every retained hash, error, translation
  decision, summary and pass/failure from the raw estimates. It uses separate
  standard-library order statistics and replays 36 fixed fits (48 quantiles).
- `translation-outlier-review.json` retains six exact replays from the three
  largest distinct observed translation cases, with complete sample values and
  descriptive likelihood checks. Reproduce with `review-translation-outliers.py
  --results <completed-results> --output <new-review.json>` through Pixi Python.

All gzip files use an empty embedded filename and `mtime=0`. File inventory
hashes are for exact bytes, not parsed JSON equivalence. The pilot is timing and
control evidence only; it is not substituted for any matrix draw or cell.

## Decision boundary

Scale-normalized error always uses generating scale one. The approved valid-fit
rate is at least 95%, absolute median signed scale error at most 0.10, and the
90th percentile of absolute scale error at most 0.50 for the upper level or
0.25 for the lower level. Every translated pair must preserve validity and have
absolute scale-error difference at most `1e-6`. Every deviation is retained.

Relative error is scale error divided by `abs(rho)` at nonzero ratio. Relative
criteria apply only at `.5,2,10`: absolute median signed error at most 10%, and
90th-percentile absolute error at most 50% upper / 25% lower. Both scale and
relative criteria are necessary, alongside the translation check. Zero is
undefined; `.05` is diagnostic and never enters a relative qualification claim.

The stochastic uncertainty examined is finite-sample estimation variability
under the known generating GEV. The reference is its analytical true quantile,
not observational validation or a predictive skill benchmark. Empirical error
quantiles are Monte Carlo summaries, not confidence intervals for a real fitted
bundle. Parameter, structural and observational uncertainty of a hydrological
model; scenario uncertainty; block dependence; nonstationarity; and the unknown
true ratio of any actual basin are outside scope. A 1,000-draw cell also has
Monte Carlo sampling uncertainty; its fixed acceptance thresholds are not
adjusted for that uncertainty.

Even a bounded benchmark pass cannot validate the operational screening floor
10 or blocks-per-return-period ratio 1.0. A failure requires an owner method
ruling before any adequacy/seal claim. No alternative estimator, ratio 2.0,
partial-year removal, interval estimation or numerical retuning is authorized
by this diagnostic. Existing production metric requests currently accept only
`provisional_operational` / `not assessed`; this standalone report changes no
ready manifest. A later owner-approved validation annotation would need the
identity-bearing schema follow-up described in design section 7.5 and new metric
sets. Existing sets and their evidence remain immutable.
