# GF15 scientific handoff: benchmark failed

**Signed verdict, 2026-09-12 — Astra model-validator
`/root/model_validator_p3`: the approved GF15 estimator benchmark is complete
and fails its unchanged criteria. An owner method ruling is required.**
This does not reverse the accepted P3 numerical-preservation result, but it
does not authorize estimator adequacy or the milestone seal. No production
estimator, tolerance, screening rule, baseline or ready metric set was changed.

## Evidence and verification

The owner approved the exact design section 7.5 matrix and reviewed P3
recommendation before execution; the coordinator recorded Master Gate 2.
[README.md](README.md) gives the formulas, sign conventions, reproduction
commands, evidence schema and applicability limits.
[criteria.json](results/criteria.json) fixes every cell and threshold.

All 12 base cells, 1,000 draws each, and all translated cases completed:
132,000 fits, 144,000 scalar quantile records, 144 summary cells and 120,000
paired translation comparisons. Four workers completed the matrix in 1,134.37
seconds (18.91 minutes). No draw, fit failure, warning or numerical deviation
was silently dropped. There were **zero fit refusals and zero fitting warnings**;
every cell therefore uses 1,000 valid fits for its conditional error summaries
and 1,000 draws for its validity denominator.

The computation used P3 commit `868c4b7cf6d2518c5ed0ba96f42338cd864e1ddd`, Python
3.12.13, NumPy 2.4.6, SciPy 1.18.0, xclim 0.60.0, xarray 2026.4.0 and pandas
3.0.3 on Windows. The exact estimator, installed fitting sources, environment,
design, criteria and benchmark script are bound in
[provenance.json](results/provenance.json); every recorded source hash remained
unchanged through completion. The benchmark script hash is
`d754c6f09d6f93a2e57e73c7d8a7f8e8d56bb749f3dc071ff0ca31ef9c13ba41`.

[Independent review](independent-review.json) verified all 262 result-file
hashes, complete row/cell coverage, every error and translation decision, all
refusal/deviation indexes, and all cell decisions from raw estimates using
separate order-statistic calculations. It independently regenerated all samples
and replayed 36 fixed fits / 48 scalar quantiles with exact parameter and value
agreement. The production-reducer parity and deliberately perturbed controls
passed, including numerical translation differences and changed fit validity.
Six additional fits replay the three largest distinct translation cases exactly
in [translation-outlier-review.json](translation-outlier-review.json).
The three diagnostic scripts pass scoped Ruff lint and format checks. These
checks validate the evidence, not the estimator's scientific performance.

## Results against the approved criteria

| Gate | Result |
|---|---:|
| Valid-fit rate at least 95% | 144/144 cells pass; 100% in every cell |
| Standardized scale-error criteria | **3/24 cells pass** |
| Scale and relative criteria at qualified ratios, before translation gate | **6/72 cells pass** |
| Translation consistency, all 1,000 pairs within `1e-6` and unchanged validity | **0/120 translated cells pass** |
| Qualified scale + relative + translation cells | **0/72 pass** |
| Complete approved benchmark | **Failed** |

The full [JSON matrix](results/matrix-results.json) and
[CSV matrix](results/matrix-results.csv) retain every cell, criterion and
denominator. The table below gives every standardized cell. Errors are divided
by **generating scale one**, never fitted scale. The targets are absolute median
signed error at most 0.10 and 90th-percentile absolute error at most 0.50 for
`p=.9` or 0.25 for `p=.5`. Display rounding does not enter decisions.

| SciPy c | n | p | Median signed | Median absolute | P90 absolute | Scale pass |
|---:|---:|---:|---:|---:|---:|:---:|
| -0.2 | 10 | .9 | -0.267273 | 0.975967 | 2.484132 | No |
| -0.2 | 10 | .5 | -0.010694 | 0.324162 | 0.777069 | No |
| -0.2 | 18 | .9 | -0.195819 | 0.701449 | 1.552862 | No |
| -0.2 | 18 | .5 | -0.019034 | 0.225553 | 0.555620 | No |
| -0.2 | 30 | .9 | -0.075800 | 0.473644 | 1.178265 | No |
| -0.2 | 30 | .5 | -0.008309 | 0.159225 | 0.402850 | No |
| -0.2 | 60 | .9 | -0.068322 | 0.346196 | 0.866600 | No |
| -0.2 | 60 | .5 | -0.000707 | 0.120855 | 0.277034 | No |
| 0.0 | 10 | .9 | -0.195477 | 0.610474 | 1.458729 | No |
| 0.0 | 10 | .5 | 0.021727 | 0.297322 | 0.803060 | No |
| 0.0 | 18 | .9 | -0.158787 | 0.424758 | 0.988074 | No |
| 0.0 | 18 | .5 | 0.002236 | 0.210807 | 0.508723 | No |
| 0.0 | 30 | .9 | -0.056080 | 0.322458 | 0.737717 | No |
| 0.0 | 30 | .5 | 0.000733 | 0.158422 | 0.390953 | No |
| 0.0 | 60 | .9 | -0.063713 | 0.230936 | 0.543651 | No |
| 0.0 | 60 | .5 | 0.005746 | 0.113191 | 0.276718 | No |
| 0.2 | 10 | .9 | -0.149626 | 0.357107 | 0.900431 | No |
| 0.2 | 10 | .5 | 0.037732 | 0.292616 | 0.706232 | No |
| 0.2 | 18 | .9 | -0.095702 | 0.258643 | 0.591765 | No |
| 0.2 | 18 | .5 | 0.021849 | 0.200037 | 0.482711 | No |
| 0.2 | 30 | .9 | -0.069537 | 0.202840 | 0.491533 | Yes |
| 0.2 | 30 | .5 | 0.016306 | 0.159798 | 0.375492 | No |
| 0.2 | 60 | .9 | -0.049167 | 0.139767 | 0.343151 | Yes |
| 0.2 | 60 | .5 | -0.008018 | 0.100151 | 0.247637 | Yes |

All six `n=10` and all six current-reference `n=18` standardized cells fail.
At `n=18`, upper P90 absolute scale error ranges from 0.591765 to 1.552862,
against 0.50; lower P90 ranges from 0.482711 to 0.555620, against 0.25. More
blocks improve these empirical errors, but `n=60` still fails both levels for
heavy-tail and Gumbel shapes. A count increase alone therefore has no general
qualification support from this matrix.

The six translated cells passing scale and relative accuracy alone all have
`c=.2`: upper `n=30` and `n=60`, and lower `n=60`, each at ratios 2 and 10.
None passes translation. No ratio-.5 cell passes both accuracy criteria.
There are 24,000 zero-ratio records with explicitly undefined relative error;
no epsilon denominator was used. Across the 24 near-zero ratio-.05 cells,
P90 absolute relative errors span 4.9557–49.6788 (approximately 496–4,968%).
These are mathematical sensitivity cases, not frequencies of real flow regimes.

## Translation failure magnitude and numerical failure regimes

**118,457/120,000 pairs (98.714%) exceed `1e-6`; there are zero validity changes.**
Every translated cell has 974–998 deviations out of 1,000. Across cells, median
absolute paired differences range from `2.96e-5` to `1.14e-4`, and their P90
values range from `7.03e-5` to `0.06313`. Many differences are small relative to
sampling error, but they still fail the approved numerical criterion. They
cannot all be dismissed as small numerical noise.

The largest paired difference is **2.562378049e9 generating-scale units**, for
heavy-tail `c=-.2`, `n=10`, `p=.9`, ratio 2, draw 662 (zero-based). The
standardized estimate is `1.730422350e9`; its translated estimate is
`4.292800398e9`. Both have finite parameters and positive scale. Their fitted
SciPy shapes are approximately -10.158 and -10.570, despite generating shape
-0.2. The exact replay verifies these are retained estimator results.

The next distinct large case, draw 819 at `c=-.2,n=10,p=.9,rho=.5`, changes
paired error by `-3.709274912e8`. Its translated fit has negative log likelihood
12.23307, whereas merely mapping the baseline parameters to the same translated
sample gives 8.21658. This is direct evidence that the returned translated fit
is inferior to an available parameter vector for that sample; returned finite
parameters are not a global-optimum certificate. The likelihood comparison is
descriptive, not a replacement fit or new refusal criterion. The three
outlier cases, complete samples, parameters, likelihoods and exact replays are
retained in the linked diagnostic. No optimizer or estimator was retuned.

## Applicability and recommended owner ruling

The benchmark measures finite-sample estimator variability against known
analytical GEV truth in stationary IID fixtures. The 1,000 draws per cell are
the Monte Carlo ensemble; its medians and empirical P90 error bounds are not
confidence intervals for observed return levels. Monte Carlo sampling
uncertainty of those summaries remains; no confidence correction was used to
alter the fixed decisions. There is no observational validation or held-out
hydrological skill claim. Dependence, nonstationarity, unknown real-bundle shape
and ratio, hydrological parameter/structural/observational uncertainty, and
scenario uncertainty are unassessed. Small-sample heavy-tail failures and
translation sensitivity further limit use of even operationally valid values.

**Recommend retaining this failed benchmark and holding adequacy/seal approval
for an owner method ruling.** The next bounded investigation should use these
fixed failure witnesses to examine likelihood behavior, numerical conditioning,
initialization and termination of the fitting path, then propose reviewed
method alternatives and a new qualification record. It must address both
sampling accuracy and translation behavior. A revised estimator or tolerance
requires a new reviewed method/criteria decision before execution; this failed
record must remain unchanged. Simply accepting the failed accuracy would require
an explicit owner revision of the adequacy gate and its stated application
limits, not a scientific pass from this reviewer.

No inference here ratifies or tightens `GEV_SCREENING_BLOCK_FLOOR=10` or
`blocks_per_return_period=1.0`; ratio 2.0, partial-year removal, new fit intervals
and new scientific defaults are not selected. The current production schema
only accepts `provisional_operational` / `not assessed`. This standalone record
changes the available scientific evidence, not existing manifest bytes. Any
owner-approved failed/reviewed benchmark annotation requires the identity-bearing
metadata follow-up in design section 7.5 and new metric sets; ready sets remain
immutable. Bounded P3 migration preservation stands, while GF15 adequacy and
the milestone seal remain pending the owner method ruling.
