# Independent scientific qualification verdict — GF15 Stage 3/3

**The retained run is mechanically valid, but the L-moment candidate fails the
unchanged GF15 qualification. GF15 remains unresolved.** The independent audit
reproduces every retained individual and paired summary, margin, and gate exactly.
Only 3/24 candidate baseline cells, 18/144 scale cells and 6/72 eligible combined
scale/relative cells pass. All six n=18 baseline cells fail. No production
integration, screening change, additional estimator search or R12 seal follows.

Signed authority: model-validator `/root/model_validator_gf15_stage3`;
2026-09-13 owner authorization for independent assessment. The machine-readable
[signed verdict](signed-verdict.json) binds the exact source, runtime, input,
result and handoff digests. The assessed Stage 2 completion SHA-256 is
`e0586b299381114a9ff20e22bdf1dd9c1a8d670ed90fe210a4e4ae004ee34845`.

## Objective, scope and evidence integrity

The objective is deterministic qualification of the frozen range-normalized
unbiased sample PWM/L-moment GEV candidate on the accepted development matrix:
SciPy c=-.2,0,.2; n=10,18,30,60; 1,000 retained IID stationary GEV samples per
shape/count cell; generating location zero and scale one; probabilities .9/.5;
baseline and translated rho=0,.05,.5,2,10. The low-flow estimand remains the
median of annual seven-day minima without sign reversal. These fixtures contain
no discharge observations and do not exercise block extraction.

There is no calibration/validation split or held-out replication in this
authorized assessment. A and B are the frozen operational predecessor
comparators, using exactly the same draws. No fresh naive estimator benchmark
was introduced. Known generating truth defines the absolute qualification loss;
paired predecessor comparisons are diagnostic, not an alternative acceptance
criterion. This is a fixed-development-matrix verdict, not a population-accuracy
or out-of-sample model-validation claim.

The independent auditor imports no readiness or qualification implementation.
It rehashed all 749 Stage 2 files (748 entries plus inventory), the complete
Stage 1 inventory and signed source/control/environment bindings, 177 protected
files and all six recorded installed lmoments3 sources. It matched the selected
732 A/B files plus preflight to the accepted A/B inventory anchors, verified all
predecessor receipts and twelve `(1000,n)` finite float64 arrays, and reconstructed
all 144,000 canonical keys independently for each of A, B and C. Baseline null
remains distinct from translated zero. The canonical key digest matches the
signed input audit.

All 240 C chunk receipts and bindings agree with the provenance. The original
array row plus A.mu reproduces each candidate's supplied-sample hash and range
normalization. Probability membership, quantile-to-fit ownership and the shared
baseline conjunction are checked. A retains per-probability validity, B retains
fit-wide acceptance, and C retains shared baseline/scalar translated acceptance.
No refusal or accepted cohort was harmonized across methods. Accepted C rows
have finite parameters in the prescribed domain and finite recorded errors.

## Independently recomputed performance

Error is `(estimate - generating truth) / 1`, never divided by sample range or
fitted scale. Each cell uses all 1,000 draws for valid rate and conditions its
linear median, median absolute error and P90 absolute error on accepted rows.
Required valid rate is .95, absolute signed median at most .10, and P90 absolute
error at most .50 for p=.9 or .25 for p=.5. Relative errors divide by absolute
truth; baseline and rho=0 retain null relative errors, .05 is diagnostic, and
only .5/2/10 receive relative gates with the same median/P90 limits.

| Method | Accepted quantiles | Baseline scale pass | All scale pass | Eligible scale + relative pass |
|---|---:|---:|---:|---:|
| A original | 144,000 | 3/24 | 18/144 | 6/72 |
| B normalized | 143,915 | 3/24 | 18/144 | 6/72 |
| C L-moments | 144,000 | 3/24 | 18/144 | 6/72 |

Equal pass counts do not imply equal estimates or losses. The only passing C
baseline cells are c=.2 at (n,p)=(30,.9), (60,.9), (60,.5). Every baseline cell
at c=-.2 or c=0 fails. At c=.2, n=10/18 both probabilities and n=30,p=.5 fail.
The following n=18 table gives point results in generating-scale units. Every
row has 1,000 accepted draws and valid rate 1.0; all fail the P90 gate, and the
c=-.2,p=.9 cell also fails the median gate.

| c | p | Signed median | Median absolute | P90 absolute | P90 limit | P90 passing margin |
|---|---:|---:|---:|---:|---:|---:|
| -.2 | .9 | -.222947 | .636890 | 1.412429 | .50 | -.912429 |
| -.2 | .5 | -.011333 | .214148 | .541554 | .25 | -.291554 |
| 0 | .9 | -.099143 | .408109 | .937538 | .50 | -.437538 |
| 0 | .5 | -.002070 | .200896 | .477672 | .25 | -.227672 |
| .2 | .9 | -.014586 | .254355 | .605117 | .50 | -.105117 |
| .2 | .5 | .003380 | .192103 | .452288 | .25 | -.202288 |

The complete independently recomputed
[individual cells](results/individual-cells.json) retain every A/B/C failure,
all exact point summaries, denominators, relative diagnostics and signed margins.
No failed translated cell is omitted from that evidence. Among the passing
baseline cells, the c=.2,n=60,p=.5 P90 passing margin is only
.0018190173471566984; this is numerical proximity to the fixed criterion,
not a confidence interval or a replication guarantee.

All 432 AB/AC/BC comparison cells were recomputed with accepted-intersection
draw IDs and both methods' errors on those exact draws. All 432,000 keyed pair
records match independently reconstructed four-category comparisons. Full
individual gates remain separate. See
[paired cells](results/paired-cells.json) for all intersection denominators,
draw IDs and conditional errors; the original pair stream is bound through the
Stage 2 inventory. Intersections do not remove predecessor refusals from their
individual valid-rate denominators.

## Translation, branches and diagnostics

All 132,000 candidate fits and 144,000 quantile rows are accepted. All 120,000
baseline/translated pairs are both accepted with unchanged acceptance. There
are zero changed-acceptance pairs, zero both-refused pairs and zero numerical
failures. Maximum absolute scale-error delta is `5.88373794130348e-12`, versus
the unchanged `1e-6` limit. All 120 translation cells pass. Every pair and margin
was independently checked. The checker also explicitly preserves null numerical
pass for a synthetic both-refused pair; computational refusal is never a
numerical translation success. Translation consistency does not establish
quantile accuracy.

| Source-defined branch | Retained fit count |
|---|---:|
| Positive snap | 11 |
| Positive rational, no snap | 113,256 |
| Nonpositive rational | 18,733 |
| Newton, rational start | 0 |
| Newton, alternate start | 0 |
| Pre-inversion refusal | 0 |

All 132,000 classifications, pre-snap/rational G values and boolean predicates
match independent calculation from recorded t3 and the pinned installed
coefficients. Every reached branch appears in the signed Stage 1 characterization.
The signed readiness population gates and fixed branch/CDF controls retain their
original authority; they were rehashed, not rerun or extended. Finite controls
establish coverage of reached branches, not uniform numerical accuracy within
each branch.

There are zero warnings, explicit refusals or exception-derived refusals. In
each coordinate system, 880 fits have sample support exclusions and 880 have
nonfinite log-density entries. The auditor reconstructed support membership from
the supplied sample and recorded parameters, counted the nonfinite entries in
every retained log-density vector, and reproduced the aggregate diagnostics
exactly. [Diagnostic cases](results/diagnostic-cases.json) identifies every affected
fit and coordinate; normalized/physical rows describe the same assessment
records and are not independent replications. Their presence is retained as a
model-fit diagnostic under the accepted policy. No cause is inferred and no new
refusal criterion is imposed.

## Uncertainty and interpretation limits

| Source | Quantification or boundary |
|---|---|
| Finite Monte Carlo variation | 1,000 independent IID samples per shape/count cell; uncertainty of medians, P90s and valid rates is unquantified. Probabilities, translations and methods share draws. |
| Adaptive selection | The development matrix was reused to select the candidate. Selection optimism and fresh-seed stability remain unknown; no holdout or resampling was authorized or run. |
| Parameter estimation | Quantile-error distributions on the fixed draws include this candidate's estimation variability; no parameter posterior or confidence region was estimated. |
| Numerical reference | Signed Stage 1 parameter references agree across 80/120 digits within 1e-30; root brackets are at most 1e-40. CDF enclosure hull width is at most 2e-30 times normalized magnitude, versus unchanged 1e-10 quantile gates. These are fixed-control bounds, not matrix-wide or population bounds. |
| Observations and structure | No observational error, dependence, mixtures, nonstationarity, extraction error or GEV misspecification is represented by the IID fixtures. No basin applicability verdict follows. |
| Scenario/internal climate variability | Not sampled or quantified by this estimator assessment. |

All existing signed point margins are retained: rate minus .95, .10 minus
absolute signed median, and the probability-specific limit minus P90 absolute
error. They are not uncertainty estimates. Exact replay and 120,000 translation
pairs do not provide 120,000 independent accuracy replications. No bootstrap,
standard-error flag or interval-overlap rule was introduced; no uncertainty
argument waives a failed deterministic gate.

The accepted design requires this noncausal context: in the c=0 Gumbel
**location submodel with known scale and shape**, the regular efficient normal
approximation gives P90 absolute location error about `1.645/sqrt(n)` in
generating-scale units. The following table is carried unchanged from the
[accepted design](../../../gf15-alternative-estimator-design.md).

| n | Rounded reference | Baseline .50/.25 below reference? | rho=.5 implied .25/.125 below? | rho=2 implied 1/.5 below? | rho=10 implied 5/2.5 below? |
|---|---|---|---|---|---|
| 10 | .520 | yes / yes | yes / yes | no / yes | no / no |
| 18 | .388 | no / yes | yes / yes | no / no | no / no |
| 30 | .300 | no / yes | yes / yes | no / no | no / no |
| 60 | .212 | no / no | no / yes | no / no | no / no |

This illustration concerns absolute-error P90 only, not median bias or valid
rate. It applies only to that c=0 submodel, not c=-.2/.2, and is neither a
finite-sample bound for biased/conditionally accepted estimators nor a prediction
for this three-parameter candidate. It establishes no causal explanation or
attainability claim and excuses no failure. The candidate's failure does not
establish that the L-moment principle is generally unsuitable.

## Verification and handoff

The exact command and immutable-output contract are in [README.md](README.md).
The independent source is frozen before the final audit. Exact decoded equality
was used throughout, including floats and booleans; there was no tolerance
adjustment. All 432 individual/432 paired cells, all pair/translation rows,
counts, point margins, acceptance categories and gate results agree. An actual
corrupted reducer copy using denominator 949 was rejected before the final run;
duplicate-key and type/null mutation checks also discriminate. Scoped lint,
format and compile checks pass. No prior evidence inconsistency was found.

This candidate is unsuitable for adoption under the unchanged all-cell GF15
criteria on the retained matrix, despite complete computational acceptance and
successful translation checks. The run is reproducible evidence of fixed-matrix
failure; population accuracy, fresh-seed replication, adaptive-selection effects,
real-bundle suitability and screening adequacy remain unresolved. Structural
and observational uncertainty cannot be inferred from additional replay of these
same fixtures. Return this failed qualification to the owner; do not integrate,
retune, start another estimator, alter screening or seal R12 under this verdict.
