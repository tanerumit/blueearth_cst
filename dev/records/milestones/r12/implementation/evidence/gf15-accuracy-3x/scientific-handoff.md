# GF15 threefold accuracy-policy assessment

**Tripling the error limits is insufficient for the unchanged all-cell
conjunction.** Candidate C passes 23/24 baseline cells and 124/144 complete
individual gates under `gf15-accuracy-3x-v1`. At n=18 all six baseline cells pass,
but five relative-error cells fail. The signed original failed verdict remains
unchanged; this assessment authorizes no production integration or R12 seal.

Assessor: model-validator `/root/model_validator_gf15_3x`, 2026-09-13.
The owner selected these limits after seeing the results. This is a bounded
policy re-score of independently audited summaries, not independent out-of-sample
scientific validation, a new qualification experiment, or a waiver of the
original failure. The [signed verdict](results/signed-verdict.json) binds the
source, criteria, this handoff, signed inputs and all computed result files.

## Policy and evidence

The owner's instruction, “lets tripple and check if that will be enough,” is
recorded in [criteria.json](criteria.json) and [README.md](README.md). Exactly four
error-threshold fields change, plus policy/authority/estimator metadata:

| Criterion | Original | Owner-selected 3x |
|---|---:|---:|
| Absolute signed median, generating-scale units | .10 | .30 |
| Absolute signed median, relative to absolute truth | .10 | .30 |
| P90 absolute error, p=.9, both coordinates | .50 | 1.50 |
| P90 absolute error, p=.5, both coordinates | .25 | .75 |

The relative limits mean **30% absolute signed median error, 150% upper-quantile
P90 error and 75% lower-quantile P90 error**, relative to absolute generating
truth. They are owner-selected accuracy tolerances, not confidence levels or
numerical precision allowances. The changed passing counts are the intended
consequence of this policy change; no scientific statistic was recalculated or
rounded before gating. The .30 threshold is explicitly serialized as `0.3`,
not computed as floating-point `.1 * 3`.

The valid-rate floor remains .95 using all 1,000 draws. Scale error remains
estimate minus truth divided by generating scale one, and relative error divides
by absolute truth. Medians/P90s remain conditional on each estimator's accepted
cohort. The signed median is not the median absolute error. Baseline and rho=0
have null relative errors; rho=.05 is diagnostic; only rho=.5,2,10 is relatively
qualified. All-cell conjunction, translation acceptance consistency, the 1e-6
translation tolerance, readiness controls, candidate C, and A/B diagnostic status
are unchanged.

The re-scorer verifies the pinned Stage 3 root inventory and signed-verdict
hashes, rehashes all 25 inventory entries and nested result inventory entries,
checks every signed local binding, and reproduces all 432 original A/B/C cell
decisions and margins exactly before applying the new policy. The complete
144-cell key population per method is checked, including baseline-null versus
translated-zero distinction. Source/input bytes are frozen before final
re-scoring and rechecked afterward; the Stage 3 inventory is rehashed again.
No original file is written. The already signed audit supplies the retained-fit,
paired-row, cohort and source-control verification; those 132,000 fits and
432,000 paired rows are not re-audited or regenerated here.

## Outcomes and failure regimes

| Method / policy | Baseline scale /24 | All scale /144 | Eligible combined /72 | All combined /144 |
|---|---:|---:|---:|---:|
| A original policy | 3 | 18 | 6 | 15 |
| A 3x, diagnostic | 20 | 120 | 48 | 108 |
| B original policy | 3 | 18 | 6 | 15 |
| B 3x, diagnostic | 20 | 120 | 48 | 108 |
| C original policy | 3 | 18 | 6 | 15 |
| C 3x, assessed candidate | 23 | 138 | 55 | 124 |

A/B are the frozen predecessor comparators on the same draws; no new naive
benchmark was introduced. Known generating truth defines the absolute loss.
Predecessor rankings do not replace the candidate's required all-cell pass.

C has **20 failed cells**: six scale failures for one base `(c,n,p)` combination
across baseline and five translations, plus 14 relative-only failures. All C
valid rates are 1.0. The only failed baseline is SciPy **c=-.2, n=10, p=.9**:
signed median `-0.35484937287189733` exceeds the absolute .30 limit by
`0.05484937287189734`; P90 `1.9154722067006629` exceeds 1.50 by
`0.41547220670066287`. The same scale failures persist at rho=0,.05,.5,2,10
(exact separate floating values are retained). At rho=.5 that cell also fails
relative median and relative P90, with passing margins -0.409698746 and
-2.330944413 respectively. These translated failures share the baseline draws;
they are not six independent findings.

The table lists **every additional relative-only failure**. All are at rho=.5;
the numbers are passing margins (limit minus observed absolute statistic),
rounded here to nine decimals. Full precision, cell keys, and each failed
criterion are in [failures.json](results/failures.json).

| c | n | p | Relative median margin | Relative P90 margin |
|---|---:|---:|---:|---:|
| -.2 | 10 | .5 | .270107905 | -.735698561 |
| -.2 | 18 | .9 | -.145893932 | -1.324858105 |
| -.2 | 18 | .5 | .277334539 | -.333108561 |
| -.2 | 30 | .9 | .104531072 | -.677320611 |
| -.2 | 30 | .5 | .294268079 | -.056673060 |
| -.2 | 60 | .9 | .153382767 | -.165545741 |
| 0 | 10 | .9 | .043083686 | -1.177517588 |
| 0 | 10 | .5 | .299673887 | -.659385205 |
| 0 | 18 | .9 | .101713928 | -.375076614 |
| 0 | 18 | .5 | .295860384 | -.205344558 |
| 0 | 30 | .5 | .288339395 | -.003690627 |
| .2 | 10 | .9 | .208228891 | -.201356977 |
| .2 | 10 | .5 | .287815037 | -.473557803 |
| .2 | 18 | .5 | .293239287 | -.154576406 |

Thus every relative-only failure fails P90; c=-.2,n=18,p=.9 also fails median.
At n=18 C passes 6/6 baseline, 36/36 scale, 13/18 eligible combined and 31/36
all combined cells. Its five failures are the n=18 rows above. The narrowest
remaining relative P90 failure is c=0,n=30,p=.5: P90 .7536906265678875 versus
.75. Its .003690626567887545 excess remains a failure; no rounding or uncertainty
argument excuses it. [summary.json](results/summary.json) stratifies all methods
by n, p, c and rho and includes the n=18 subset;
[individual-cells.json](results/individual-cells.json) retains all 144 C cells
and all A/B diagnostic cells, unchanged statistics, new margins and gates.

All 120 translation cells retain their passing outcomes and unchanged
acceptance: 120,000 both-accepted pairs, zero numerical failures, maximum
absolute scale-error delta `5.88373794130348e-12` against the unchanged `1e-6`
limit. The [translation cells](results/translation-cells.json) retain the audited
records unchanged as decoded JSON. Translation stability does not establish
accuracy.

## Uncertainty and applicability

| Source | Quantification and limit |
|---|---|
| Parameter-estimation variability | Empirical accepted-draw signed medians and absolute-error P90s on 1,000 IID stationary GEV samples per c/n cell; no parameter intervals. |
| Finite Monte Carlo variation | 1,000 independent samples per base cell, with shared draws across p, translations and estimators; uncertainty of reported medians/P90s/rates is unquantified. |
| Adaptive selection | Both candidate choice and this relaxed policy use already observed development results; no temporal/spatial split, fresh seed, holdout or selection correction. |
| Numerical computation | Inherited signed fixed-control readiness evidence and unchanged translation bound; this re-score uses exact stored values without new numerical tolerances. |
| Structure and observations | No observed discharge, extraction uncertainty, serial dependence, nonstationarity, GEV misspecification or observational error is represented. |
| Scenario/internal climate variability | Neither quantified nor inferred from these IID fixtures. |

P90 is the empirical 90th percentile of absolute errors, not a 90% confidence
interval for accuracy. Point passing margins have no uncertainty coverage.
Replaying this retained matrix cannot shrink uncertainty about unrepresented
processes or remove adaptive-selection effects. The low-flow estimand remains
the median of annual seven-day minima without sign reversal; these fixtures do
not exercise its block extraction. No basin or screening applicability follows.

## Reproduction and verification

Run from the pinned worktree root with the existing isolated Python environment:

```powershell
$Assessment = 'dev/milestones/r12/implementation/evidence/gf15-accuracy-3x'
$StagePython = '.tmp/scratchpad/2026-09-11_0010/gf15-lmoments-readiness/venv/Scripts/python.exe'
$Scratch = '.tmp/scratchpad/2026-09-11_0010/gf15-accuracy-3x'
& $StagePython -B "$Assessment/check-rescore.py" *> "$Scratch/boundary.log"
& $StagePython -B "$Assessment/rescore.py" --output "$Assessment/results" *> "$Scratch/final-rescore.log"
```

Those are the final executed check/re-score commands. `results` must be absent;
for reproduction use a new absent scratch output directory and new log. Do not
delete signed results. `source-freeze.json` is the first output, before scoring;
the signed verdict and inventory are written after all checks pass. The script
requires normal Python assertion execution: do not pass `-O`.

Verification is rapid / numerical affected under the explicitly bounded task.
The caller search `rg -n 'gf15-accuracy-3x|rescore' blueearth_cst tests scripts`
found no production caller. One new narrow check was justified by new policy
reduction logic. It first failed before implementation existed; after
implementation, an actual disposable half-P90 reducer mutation failed with
`AssertionError`. The correct reducer passes inclusive and over-limit median,
P90 (both probabilities), 950/949 valid-count boundaries, relative eligibility
and null handling. All old decisions reproduce exactly. Scoped Ruff check,
format check and in-memory compilation passed. The durable
[verification record](verification/commands.md) retains commands, boundary,
mutation and static-check logs and the mutation runner; these are bound before
the final run. Scratch retains disposable development/mutant outputs. The parent
integration envelope retains the final execution transcript. No full suite, model workflow, new sample, new fit,
bootstrap or readiness rerun was performed because no production/numerical model
path changes and the authorization is a summary-only re-score.

Candidate C still fails the owner-selected threefold policy on the fixed matrix.
The successful n=18 baseline subset does not satisfy the full relative-error
contract. The original failure remains authoritative under its original limits,
and this additional failed assessment supports no integration, screening change,
further relaxation, estimator search or R12 seal. Population accuracy, fresh-seed
stability and real-system applicability remain unresolved beyond these fixtures.
