# GF15 L-moment Stage 2 execution handoff

**The full authorized matrix completed; the observed mechanical GF15 conjunction
is false.** This is an executor handoff, not independent Stage 3 acceptance.
No estimator, gate, tolerance, input sample, environment or production surface
changed during the run. No matrix attempt failed or required resuming.

## Complete retained results

| Quantity | Observed |
|---|---:|
| Completed immutable chunks | 240 |
| Attempted / accepted candidate fits | 132,000 / 132,000 |
| Candidate quantiles | 144,000 |
| Individual summary cells per A, B and C | 144 each |
| Full AB, AC and BC keyed comparisons | 432,000 |
| C baseline/translated pairs | 120,000 |
| Both-accepted translation pairs | 120,000 |
| Changed-acceptance / both-refused pairs | 0 / 0 |
| Accepted-pair numerical failures | 0 |
| Translation cells passing | 120 / 120 |

Maximum absolute translation error delta is `5.88373794130348e-12`, below the
unchanged `1e-6` limit. Every C cell has valid rate 1.0 and 1,000 accepted draws.
Computational acceptance and affine consistency did not establish accuracy.

| Estimator | Accepted quantiles | Baseline scale cells passing | All scale cells passing | Eligible scale + relative cells passing |
|---|---:|---:|---:|---:|
| A original | 144,000 | 3 / 24 | 18 / 144 | 6 / 72 |
| B normalized | 143,915 | 3 / 24 | 18 / 144 | 6 / 72 |
| C L-moments | 144,000 | 3 / 24 | 18 / 144 | 6 / 72 |

Equal pass counts do not mean equal estimates or losses. Complete individual
errors, medians, median absolute errors, P90 absolute errors, denominators, gate
decisions and signed passing margins are in
[individual-cells.json](results/individual-cells.json). Pairwise accepted-key
intersections and both methods' errors on each intersection are fully retained
in [paired-cells.json](results/paired-cells.json) and the accompanying compressed
key records; none replaces an individual gate.

C's only passing baseline cells are c=.2 with (n,p)=(30,.9), (60,.9), (60,.5).
All six n=18 baseline cells fail. Their P90 absolute errors in generating-scale
units are .605117–1.412429 for p=.9 (limit .50), and .452288–.541554 for p=.5
(limit .25). These rounded ranges summarize the complete retained point results;
they are neither causal attribution nor Monte Carlo uncertainty bounds.

## Branches, diagnostics and timing

| Branch | Attempted fits |
|---|---:|
| Pre-inversion refusal | 0 |
| Positive snap | 11 |
| Positive rational, no snap | 113,256 |
| Nonpositive rational | 18,733 |
| Newton, rational start | 0 |
| Newton, alternate start | 0 |

There were no warnings, explicit refusals or exception-derived refusals. Sample
support exclusion and nonfinite log-density were recorded for 880 fits in each
coordinate system. These remain diagnostics under the accepted candidate policy;
they were not converted into refusals. Exact moments, parameters, normalization,
quantile diagnostics, source identity and support/log-density values remain in
every raw `adapter_record`. Finite Stage 1 controls cover the reached branches;
the histogram does not establish an error bound throughout a branch.

Measured total execution was 1,054.822 seconds (17.58 minutes). The fit-chunk phase,
including its initial binding/input recheck, took 993.528 seconds; summed chunk
times were 983.829 seconds and summed adapter-call times 943.101 seconds. The run
used one sequential writer and reused zero chunks. These are observed timings
for this environment and matrix, not a cross-method speed comparison.

## Identity and verification

| Bound object | SHA-256 |
|---|---|
| Frozen Stage 2 provenance | `3ef0f96b4b8865350d7e657a7303189d5c1b96ed8c1830b5ca4438ebfceaec3c` |
| Evaluator source | `c9e867df25eac96557c690d407ad7d37252c222f9675b43c093d711f33b6b379` |
| Completion | `e0586b299381114a9ff20e22bdf1dd9c1a8d670ed90fe210a4e4ae004ee34845` |
| Mechanical audit | `25bfff7aee0ee4026265ca728d751349d188967e5c1a3b4773aa08168322d600` |
| Qualification summary | `1f5084379d16e7f17aa732795c8ad81bed62437823d2d8d9efe525d8c3842b00` |

The complete D4 audit was repeated before fitting and after reduction: all 732
selected A/B files and receipts plus B preflight, both full 144,000-key sets,
all twelve arrays and all truth/offset bindings. The evaluator also rehashed
every C chunk receipt and recomputed candidate sample hashes, probability
membership, shared acceptance, errors, branch classification and canonical
coverage from retained records. Signed Stage 1 source/control/environment and
protected-file identities remained unchanged.

The three focused pytest tests pass. They cover error denominators, undefined
zero-relative errors, empty cohorts, numerical thresholds, all four translation
categories, the 950/949 translation-cell boundary, atomic receipts, exact resume,
partial recovery, competing writers, corrupted receipt counts and unexpected
fault stopping. A disposable mutation changing the all-draw denominator from
1,000 to 949 was detected by the error test; restoring the original reducer
passed. The initial missing-module failure is retained as setup evidence only.
Both authored modules compiled to scratch bytecode; scoped Ruff check and format
check passed. Exact commands and the unchanged run contract are in [README.md](README.md).
Validation logs and mutation source are retained in [execution-logs/](execution-logs/)
and the session scratch directory named there. The parent integration envelope
binds those selected logs, including the complete matrix execution transcript.

## Remaining independent Stage 3 work

Stage 3 requires separate release and a model-validator's independent recomputation
of counts, canonical joins, errors, conditional cohorts, all individual gates,
AB/AC/BC intersections, translation outcomes, branch coverage and provenance,
followed by a signed scientific verdict bound to the completion above. The observed
criterion failures must remain visible; no independent acceptance is claimed here.
GF15 remains unresolved, with no production integration or R12 seal.

Finite Monte Carlo uncertainty of medians, P90s and valid rates remains
unquantified. There are 1,000 independent retained draws per generating
shape/count cell, while probabilities, translations and method comparisons
share draws. The 120,000 translation pairs are not independent accuracy
replications. Reusing development draws makes selection adaptive; fresh-seed
stability and optimism remain unknown. No resampling, screening validation,
observational/structural adequacy, nonstationarity or basin applicability claim
follows. The accepted c=0 Gumbel location-submodel context table and its strict
limitations are carried in the README; they excuse none of the failed cells.
