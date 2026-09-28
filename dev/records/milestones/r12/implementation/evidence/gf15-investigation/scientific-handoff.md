# GF15 investigation: numerical instability and broad accuracy shortfall

**Signed assessment, 2026-09-12 — Astra model-validator
`/root/model_validator_p3`: the bounded investigation is complete.**
The failed GF15 benchmark remains failed. Production, estimator defaults,
scientific criteria, screening rules, baselines and existing metric sets are
unchanged. The next method decision belongs to the owner; this record does not
authorize a replacement estimator or the milestone seal.

## Ranked findings

1. **The largest witnessed errors are nonconverged results whose termination
   status was discarded.** All six extreme-witness fits exhausted the default
   600 function evaluations, while still returning the exact finite parameters
   and quantiles published by the original benchmark. The current parameters-only
   path cannot distinguish those failures from reported convergence.
2. **The default numerical path is not translation-equivariant, including cases
   that report convergence.** Its initial simplex changes geometry when location
   changes. The stopping conditions concern parameter and objective spreads,
   not a `1e-6` quantile-translation guarantee. Boundary-sensitive floating-point
   behavior is an additional observed issue. The investigation identifies these
   mechanisms but does not isolate their proportional contributions.
3. **Rare giant errors do not explain the broad precision failure.** All 21
   standardized P90 failures remain after a descriptive removal of each cell's
   largest ten absolute errors. Error decay with sample size and an analytical
   sampling-scale comparison support a substantial finite-sample component, but
   do not prove that every remaining error is intrinsic sampling variability.
   A controlled method comparison is still needed to separate that component
   from other fitting deficiencies.

## Scope, controls and provenance

Owner approval covered a bounded investigation after the failed benchmark.
[protocol.json](results/protocol.json) records the selection before execution.
Likelihood and parameter diagnostics use **all 132,000 unique retained fits**,
without refitting that matrix. Both baseline quantiles share one parameter fit;
the 12,000 baseline fits are counted once. Sampling diagnostics use all 24
original baseline quantile cells and all 1,000 draws in each.

The trace grid was fixed as draw IDs `{0,499,999}` in each shape/count cell:
one baseline fit and four translated fits (`p={.9,.5}`, `rho={0,10}`) per draw,
giving 180 fits. The three already retained extreme witnesses and their
baselines add six, for **186 traces**. This is a fixed diagnostic grid plus
purposive extremes, not a representative sample for estimating the failure rate
among 132,000 fits. No omitted trace, new random draw or full qualification
matrix is hidden in this count.

The observer intercepts `_minimize_neldermead`, forwards every existing argument
and setting unchanged, records each objective evaluation and the returned result
object, and returns that same object to the caller. It changes no start,
optimizer, tolerance, limit, callback, `full_output` or `retall` setting. All
186 parameter vectors and 225 scalar quantiles replay the original results
**exactly**. Every first simplex also matches the installed default construction.
Toy controls discriminate ordinary convergence from default-budget exhaustion;
a separate likelihood control checks the scalar objective and unsupported data.
[controls.json](results/controls.json) retains these results.

Vectorized retained-fit analysis took 8.67 seconds and tracing 3.47 seconds,
excluding imports/loading. The run completed successfully. The original GF15
inventory and all 276 files were checked before and after execution and remain
byte-exact. [provenance.json](results/provenance.json) binds this diagnostic's
sources and original environment record; [source-reconciliation.json](source-reconciliation.json)
additionally rehashes all 13 original runtime/estimator sources, including
SciPy's fitting infrastructure. All match. The coordinator independently checked
the original 276 hashes, every trace evaluation count against `nfev`, all statuses,
and all 24 original/trimmed P90 summaries without importing this harness.
The coordinator also independently checked all 132,000 diagnostic rows and
reconciled the fitted/truth likelihood and 444 nonfinite mapped-candidate counts.

To reproduce from the repository root into an absent disposable directory:

```powershell
pixi run --as-is python dev/milestones/r12/implementation/evidence/gf15-investigation/investigate-estimator.py --output .tmp/gf15-investigation-new *> .tmp/gf15-investigation-new.log
```

The script refuses an existing output directory and verifies the original GF15
inventory before and after execution. All source/runtime hashes remain available
for comparison; do not overwrite the retained investigation to rerun it.

## 1. Hidden termination failures in the extreme witnesses

| Selection | Fits | Reported success | Evaluation-limit failure | Iteration-limit failure |
|---|---:|---:|---:|---:|
| Predetermined diagnostic grid | 180 | 180 | 0 | 0 |
| Purposive extreme witnesses | 6 | 0 | 6 | 0 |

Every extreme trace reports status 1, `nfev=600`, and 335–348 iterations.
Final maximum coordinate spreads are 0.00901–0.12796 and objective spreads are
0.00400–0.12095, both larger than the default `1e-4` stopping tolerances.
These are not successful fits merely close to the stopping boundary.
[optimizer-traces.json](results/optimizer-traces.json) retains every status,
simplex and parameter vector; [optimizer-evaluations.jsonl.gz](results/optimizer-evaluations.jsonl.gz)
retains every objective evaluation.

The installed `rv_continuous.fit` calls `optimize.fmin(..., disp=0)` and receives
only parameters. The underlying failure status is discarded; the warnings that
would be emitted with display enabled are suppressed. This explains why the
original benchmark could record no exceptions or warnings for these six
nonconverged results. It does **not** establish that the other 131,994 retained
fits converged: their termination state was not traced. The parameters-only
interface and lack of global-optimum guarantee are documented by
[SciPy's fitting API](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.rv_continuous.fit.html);
[fmin](https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.fmin.html)
documents the exposed termination information.

Exposing and honoring termination status would address this observed acceptance
gap, but cannot by itself demonstrate adequate return-level precision or remove
translation differences in fits that already report success.

## 2. Translation changes numerical geometry and boundary behavior

The installed xclim start is shape 0.1, scale
`s=sqrt(6*sample_variance)/pi`, and location `sample_mean-0.57722*s`.
Its start approximately shifts with the sample. SciPy then constructs the
default simplex by multiplying each nonzero starting coordinate by 1.05 for
that coordinate's vertex (or using 0.00025 for a zero coordinate). Consequently
the location edge depends on the absolute starting location. A shift in data
location produces more than a shifted copy of the old simplex. This is directly
confirmed by the captured initial evaluations and the
[installed-version SciPy source](https://github.com/scipy/scipy/blob/v1.18.0/scipy/optimize/_optimize.py).
The installed xclim source hash is authoritative; its general fitting interface
is described in the [xclim source reference](https://xclim.readthedocs.io/en/stable/_modules/xclim/indices/stats.html).

For example, Gumbel `n=18`, draw 499 has baseline starting location 0.161740
and location edge +0.008087. Translating to `p=.9,rho=0` changes the starting
location to -2.088628 and the edge to -0.104431. Both fits report convergence,
but their paired quantile error differs by approximately `-1.04360e-4`, exceeding
the unchanged `1e-6` benchmark criterion. Their final objective spreads are
below `1e-7`, demonstrating that a small objective spread is not a quantile
agreement guarantee. This establishes a source of different optimization paths;
without a controlled intervention it does not prove this geometry is the sole
cause of every discrepancy.

Every one of the 132,000 retained fitted parameter vectors has finite public
log densities for its own sample. Every fitted negative log likelihood is no
worse than the true generating parameters' negative log likelihood. That
negative diagnostic is important: comparing only against generating truth
would not detect the giant fitted quantile errors.

Mapping baseline parameters by the known location shift creates **444/120,000
translated candidates with nonfinite public log density**, although the original
fits remain finite. These candidates are retained explicitly; they cannot be
used as feasible objective witnesses. Mathematically location-shifting is
invariant, but evaluation near a support boundary can be sensitive to floating
point arithmetic. In addition, the recorded direct algebraic support margin can
round to zero because its operation order differs from SciPy's standardization.
Neither fact is evidence that an original source fit violated its evaluated
support. Public log-density counts, rather than that rounded margin, determine
the stated feasibility result.

Among feasible mapped candidates, 59,461 have a lower raw negative log likelihood
than the returned translated fit. That count includes tiny numerical differences;
it is descriptive and carries no new significance threshold. Some differences
are substantial: the maximum finite gap is 9.0711 log-likelihood units. The prior
draw-819 witness has an available mapped candidate at NLL 8.21658 versus 12.23307
for the returned fit. Its nonconvergence is now observed directly. Parameter
ranges also become extreme at small counts: across the three baseline `n=10`
cells, fitted SciPy shapes extend from approximately -10.158 to +1.530 despite
generating shapes between -0.2 and +0.2. These observations motivate investigation
of conditioning and likelihood geometry, not an unreviewed shape constraint.
All records are retained in [retained-fit-diagnostics.jsonl.gz](results/retained-fit-diagnostics.jsonl.gz)
and [parameter-likelihood-summary.json](results/parameter-likelihood-summary.json).

## 3. Persistent accuracy failure beyond the extreme 1%

The following uses all original `n=18` cells. The diagnostic trim removes exactly
the ten largest absolute errors per cell, solely to test whether rare extremes
explain the P90 result. It is not a proposed data policy or qualification result.

| SciPy c | p | Original P90 absolute error | Diagnostic P90 after removing 10/1,000 | Original target |
|---:|---:|---:|---:|---:|
| -0.2 | .9 | 1.552862 | 1.529044 | 0.50 |
| -0.2 | .5 | 0.555620 | 0.540669 | 0.25 |
| 0.0 | .9 | 0.988074 | 0.965166 | 0.50 |
| 0.0 | .5 | 0.508723 | 0.501112 | 0.25 |
| 0.2 | .9 | 0.591765 | 0.569077 | 0.50 |
| 0.2 | .5 | 0.482711 | 0.464967 | 0.25 |

All six failures persist, as do all 21 original baseline P90 failures over the
full matrix. Rare extremes strongly distort squared-error summaries in some
`n=10` upper cells: heavy-tail RMSE is approximately `5.596e7` despite P90 error
2.484; Gumbel RMSE is approximately 11,413 despite P90 error 1.459. In both,
the largest 1% contributes over 99.99% of total squared error. The complete
[sample-size-accuracy.json](results/sample-size-accuracy.json) retains every cell,
robust quantile, maximum, error contribution and removed draw ID.

From `n=18` to `n=60`, observed P90 errors fall to approximately 50–58% of
their earlier values, close to the descriptive `sqrt(18/60)=0.548` sampling
scale. An additional known-density calculation uses
`sqrt(p*(1-p)/n)/f(q_p)` for the **asymptotic empirical-quantile standard error**,
with `f(q_p)=p*(-log(p))**(1-c)` at generating scale one. For `n=18,p=.5`,
the corresponding normal-approximation P90 absolute scale is 0.520–0.602,
compared with observed GEV-fit P90 errors 0.483–0.556. This is supportive context
for the broad spread, not a GEV-MLE bound, a finite-sample confidence interval,
a replacement estimator run or proof that the accuracy target is impossible.

Other suboptimal but reported-converged fits may remain after the diagnostic
trim. The current evidence cannot quantitatively partition sampling variability,
optimizer effects and likelihood behavior. The true-parameter likelihood check
also cannot make that partition. No threshold is loosened on this basis.

## Recommended next scope and owner acceptance questions

**Recommend an isolated candidate study before any production change:** first
make convergence/status observable, then isolate translation conditioning while
keeping the GEV likelihood. Reuse the same fixed 186 diagnostic cases and every
original comparator; preserve this investigation and the failed benchmark.

| Candidate or alternative | Purpose | Tradeoff and required decision |
|---|---|---|
| Status-only wrapper, same numerical path | Distinguish success from the witnessed evaluation-limit failures | Lowest numerical change; refusal behavior changes and must be reviewed. Does not solve accuracy or successful-fit translation errors. |
| Deterministic sample mean / population-standard-deviation normalization, then map parameters and quantiles back | Isolate sensitivity to location/scale conditioning while retaining the same GEV likelihood and current optimizer settings | Changes the numerical path; no accuracy or equivalence pass is assumed. Requires a fixed normalization rule and separate review. **Recommended first numerical candidate.** |
| Different tolerance or evaluation budget with the same local optimizer | Investigate stopping sensitivity | More cost and possibly more extreme likelihood searches; cannot be selected by repeatedly tuning to this failed result. Requires a separately specified candidate, not execution now. |
| Bounded/global fitting API | Explore local-search and explicit-status alternatives | Different optimizer, reviewed parameter bounds and RNG required; SciPy's newer `stats.fit` defaults to fixed location/scale unless bounds explicitly free them. Not a drop-in replacement. |
| PWM / L-moment method | Explore another estimation method's finite-sample behavior | Changes the scientific method and adds a currently absent `lmoments3` dependency; no assumed accuracy advantage or preservation claim. |

The newer [SciPy fitting API](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.fit.html)
documents its distinct bounds and optimizer contract. No alternative in the table
was executed during this investigation.

The immediate question for the owner is: **approve a status-only candidate plus
one normalization candidate on these same 186 diagnostic cases**, using sample
mean and population standard deviation (`ddof=0`), the unchanged GEV likelihood
and existing optimizer defaults, with no production integration, silent fallback,
changed tolerance or full qualification matrix yet?

The original GF15 accuracy and translation criteria remain unchanged under the
existing owner authorization; they need no renewed approval. A future revision
would require a new decision-purpose justification and reviewed record. This
186-case study could identify a candidate worth qualifying, but cannot qualify
a 1,000-draw cell. Before any later production integration, unsuccessful-
termination handling and the resulting metric-set identity/availability changes
would need a separate decision. That integration policy is not a prerequisite
for the bounded diagnostic study proposed here.

The candidate study is not authorized merely by completion of this investigation.
No screening-floor or blocks-per-return-period increase
is recommended alone. More samples may improve precision, but neither the
required count for untested systems nor observed-bundle applicability is
established here. If the owner instead revises an accuracy target, that needs a
new decision-purpose justification and reviewed criteria record; the original
failure cannot be relabeled as a pass.

This assessment applies only to the retained stationary IID GEV fixtures and
specified diagnostic traces. It adds no hydrological validation, observational
uncertainty, dependence assessment, nonstationary result, real-bundle interval or
screening-policy qualification. The original 1,000-draw cells retain Monte Carlo
sampling uncertainty, and the purposive traces cannot estimate its optimizer
failure frequency. GF15 adequacy and the milestone seal remain owner-gated.
