# GF15 normalized candidate B: full qualification failed

**Signed scientific verdict — model-validator, 2026-09-12.** The approved full
candidate-B qualification completed correctly and failed the unchanged GF15
criteria. Normalization substantially improved translation behavior, but did
not qualify either full translation preservation or finite-sample accuracy.
Return the failed qualification to the owner for a method ruling under the
accepted design §7.5. Production integration and the GF15 adequacy/milestone
seal remain pending; no production or existing metric-set changes were made.

## Scope and execution

The owner authorized B-only qualification of the original 12 shape/count cells,
with 1,000 retained IID GEV samples per cell: SciPy c = −0.2, 0, +0.2
(conventional ξ = −c), n = 10, 18, 30, 60, p = 0.9 and 0.5, and translated
true-quantile/scale ratios 0, 0.05, 0.5, 2, 10. These are synthetic stationary
known-truth fixtures, separate from observations, calibration, and hydrological
validation. The original estimator results are the paired method reference;
analytical generating quantiles supply truth. No new samples or RNG draws were
used and no fitted case was filtered from the attempted denominators.

The runner imported the committed B `fit_case` unchanged: normalize by sample
mean and population standard deviation, use the same xclim GEV fit and optimizer
defaults, back-transform parameters and separate scalar xclim quantiles, then
apply the same explicit status/finiteness refusal policy. The baseline fit
requests both quantiles; its fit-level acceptance is shared by those two rows.
Unsuccessful fits retain their raw results without fallback.

Four processes completed 240 fixed chunks in **2,168.44 seconds (36.1 minutes)**:
132,000 fits, 144,000 scalar quantiles and 120,000 translated pairs. All 186
embedded previous B cases replayed exactly, including optimizer results and
quantiles. Frozen source and input hashes remained unchanged. Every final fit,
normalization constant, parameter vector, optimizer result/final simplex,
warning/refusal and scalar quantile is retained. Evaluation counts were checked;
full per-evaluation objective histories were not retained for this full matrix.

## Qualification and denominators

The original acceptance-rate threshold is 95% of all 1,000 attempts. Accuracy
summaries condition on accepted fits: absolute signed median scale error ≤0.10,
P90 absolute scale error ≤0.50 for p=0.9 and ≤0.25 for p=0.5. The same relative
limits apply at ratios 0.5, 2 and 10. At ratio zero, relative error is undefined; ratio
0.05 is diagnostic only. Translation requires unchanged acceptance on every
pair and absolute error difference ≤1e−6 on every both-accepted pair. Both-refused
pairs give **no numerical-equivalence proof**. They count against acceptance
rates and remain separate from numerical passes.

| Check | Result |
|---|---:|
| Accepted fits / attempted | 131,922 / 132,000 |
| Refused fits, all optimizer status 1 | 78 / 132,000 |
| Accepted / refused scalar quantiles | 143,915 / 85 |
| Estimator exceptions / recorded warnings | 0 / 0 |
| Baseline scale-accuracy cells passed | **3 / 24** |
| Eligible translated scale-and-relative cells passed | **6 / 72** |
| Translation/acceptance cells passed | **106 / 120** |
| Both-accepted numerical passes / failures | 119,899 / 30 |
| Both-refused pairs / changed-acceptance pairs | 70 / 1 |

All 144 cells exceed the 95% accepted-rate gate. The minimum is 995/1,000:
the c=−0.2, n=10 baseline and translated cells refuse five draws each. The c=0,
n=10 cells refuse two each. One additional c=+0.2, n=10, p=0.5, ratio=2 fit is
refused; its baseline was accepted. Status 1 means the unchanged function
evaluation budget was exhausted. Absence of warnings is not evidence of solver
success in this params-only fitting interface.

## Accuracy by regime

P90 absolute scale error below uses accepted estimates and generating scale=1.
The required limits are **0.50 upper / 0.25 lower**. The full signed medians,
denominators, maxima and all 144 strata remain in `results/matrix-results.json`.

| SciPy c | n | Accepted baseline fits | Upper P90 | Lower P90 |
|---:|---:|---:|---:|---:|
| −0.2 | 10 | 995 | 2.432023 | 0.775395 |
| −0.2 | 18 | 1,000 | 1.552639 | 0.557971 |
| −0.2 | 30 | 1,000 | 1.178188 | 0.402967 |
| −0.2 | 60 | 1,000 | 0.866691 | 0.277024 |
| 0 | 10 | 998 | 1.444639 | 0.803184 |
| 0 | 18 | 1,000 | 0.987904 | 0.508728 |
| 0 | 30 | 1,000 | 0.737941 | 0.390988 |
| 0 | 60 | 1,000 | 0.543662 | 0.276734 |
| +0.2 | 10 | 1,000 | 0.900400 | 0.727738 |
| +0.2 | 18 | 1,000 | 0.591746 | 0.483606 |
| +0.2 | 30 | 1,000 | **0.491455** | 0.375524 |
| +0.2 | 60 | 1,000 | **0.343158** | **0.247776** |

Every n=10 and n=18 baseline cell fails. At n=18 the upper signed medians are
−0.195853, −0.158905 and −0.095080 for c=−0.2, 0 and +0.2; lower medians are
−0.019065, +0.001124 and +0.022179. All six P90 criteria fail even though every
n=18 fit is accepted. The baseline pass pattern remains the same **3/24** as
the original unnormalized benchmark. The eligible scale-and-relative pattern
also remains **6/72**, from those three baseline families at ratios 2 and 10.
The heavy-tail upper criterion still fails at n=60. Raising the screening floor
alone is neither established as sufficient nor authorized by this evidence.

At ratio 0.05, accepted relative P90 errors range from 4.955525 to 48.640464
(approximately 496–4,864%). This is a retained near-zero diagnostic, not a
new qualification or screening rule. All zero-ratio relative errors remain
undefined. The largest accepted absolute scale error is 27.199679; optimizer
success does not guarantee an accurate quantile. The largest raw refused
estimate is approximately 1.496×10¹⁰ and was excluded only from accepted-error
summaries, never from attempted denominators or retained evidence.

## Numerical improvement and remaining failures

The original estimator had 118,457 paired numerical deviations out of 120,000.
B has 30 numerical failures among 119,929 both-accepted pairs, plus 70
both-refused and one changed-acceptance pair. The maximum accepted paired error
difference is **4.526265831×10⁻⁶**, above the unchanged 10⁻⁶ limit. All 14 failed
translation cells occur at n=10: four lower cells at c=−0.2, one upper and four
lower cells at c=0, and all five lower cells at c=+0.2. The changed-acceptance
witness is c=+0.2, n=10, draw 232, p=0.5, ratio=2 (fit 90561). Its tiny raw
error difference, −3.99308403×10⁻⁸, does not override the acceptance mismatch.
All 30 numeric failures and the mismatch are retained in
`scientific-diagnostics.json` and the complete paired ledger.

Some individual estimates changed substantially. For the c=−0.2, n=10,
draw 113 baseline (fit 1243), the upper estimate changed from 977,880.474248
to 14.014302 against truth 2.842137. The accepted B fit terminated with status 0
after 222 evaluations, yet its scale error remains 11.172165. The original full
benchmark did not capture that fit's optimizer status; it must not be inferred.
This is a large individual improvement, not evidence that the failed cell's
accuracy target has become adequate.

All 132,000 normalized-fit public log-density evaluations are finite. For
**974 accepted fits**, evaluation using the physically back-transformed
parameters has nonfinite log-density; none of the 78 refused fits has this
mapped diagnostic. For example, fit 122 has normalized NLL 11.751892 but mapped
physical NLL infinity from one observation. This exposes a numerical mapping/
support-boundary limitation consistent with the earlier conditioning findings;
this study does not isolate its cause further. It does not establish a support
violation in the normalized fitted sample. The approved B policy explicitly
treats likelihood mapping as diagnostic, so these fits have **not** been
retroactively refused or removed. Affine quantile back-transform arithmetic
was independently verified; that check does not imply finite mapped likelihood.

## Interpretation and owner decision

The ranked findings are: (1) the broad approved finite-sample accuracy target
still fails, including all six n=18 cells; (2) normalization removes most
translation deviations but does not meet the full unchanged translation/
acceptance gate; (3) status reporting exposes 78 unsuccessful fits, while
successful termination and affine quantile arithmetic leave mapped-likelihood
and accuracy limitations. The previous investigation's error decay and robust
summaries support a finite-sample contribution. Neither that study nor this
qualification decomposes all remaining error into intrinsic sampling variability
versus suboptimal converged fits. There is no claim that normalization alone, a
tighter solver tolerance, or more optimizer iterations would solve adequacy.

**Recommendation:** retain B as an unqualified diagnostic candidate and request
the owner's substantive method ruling under §7.5. Do not initiate another
numerical-tuning run by default. The owner can authorize a specified alternative
estimator study, with its dependencies and scientific tradeoffs reviewed, or
reconsider the intended accuracy claim using an explicit decision rationale.
An alternative estimator changes bias/variance and possibly dependencies;
revising the claim changes what the workflow promises. Neither is accomplished
by this failed benchmark. Existing criteria remain authorized and unchanged;
any proposed revision requires new justification. A separate later integration
decision would govern refusal behavior, schema/identity and new metric sets.

The unchanged production metric-plan schema still only accepts
`provisional_operational` / `not assessed`. This standalone result does not
alter immutable existing metric sets, qualify actual bundles, or amend the
already accepted P3 migration-preservation verdict. GF15 adequacy and milestone
seal remain pending the owner method ruling.

## Verification and limits

The coordinator's frozen `independent-review.py` independently verified all
132,000 fit IDs/statuses, 144,000 quantiles, 120,000 pairs and 144 cell summaries
against original samples/rows, using independent arithmetic and linear order
statistics without importing fitting helpers. Its audit passed. All three prior
artifact inventories and original numeric criteria remained exact. Analytical,
toy-optimizer, status, nonfinite-serialization, 2×10⁻⁶ perturbation and
both-refused/changed-acceptance controls discriminated correctly. Scoped and
repository lint/format checks passed; no production suite, workflow or baseline
rerun was needed for these diagnostic-only files.

The 1,000 draws per base cell quantify error under a fixed IID stationary GEV
generating family; their empirical quantiles have finite Monte Carlo uncertainty
and are not confidence bounds for a basin. Sampling and estimation uncertainty
are represented here; observational error, dependence, nonstationarity,
climate-scenario uncertainty, hydrological structural uncertainty and annual
block extraction are outside scope. The p=0.5 metric is the median of annual
seven-day minima, not a rare lower-tail quantile. Candidate B is **not qualified
for the approved GF15 accuracy claim**, and this study provides no new screening
floor, ratio threshold, production integration authority or actual-bundle
uncertainty interval.
