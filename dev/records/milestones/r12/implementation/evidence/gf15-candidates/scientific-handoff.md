# GF15 candidates: normalization merits full qualification testing

**Signed bounded verdict, 2026-09-12 — Astra model-validator
`/root/model_validator_p3`: candidate B merits a full qualification attempt;
neither candidate is scientifically qualified by this study.** Candidate A
correctly exposes failed termination without changing raw numerical results.
Candidate B additionally resolves translation disagreement in every comparable
pair in this subset, but does not resolve the six witnessed optimizer failures.
The original failed benchmark remains failed; production, screening rules and
existing metric sets are unchanged.

## Approved scope and reproducibility

The owner explicitly approved these two candidates on the existing 186 cases.
There were **372 candidate fits**, **450 primary scalar quantiles**, and **147
attempted translation pairs per candidate**. The selection remains 180 fits from
draws `{0,499,999}` across the 12 shape/count cells, plus six purposive extreme
witness fits. Controls added no GEV fits. This is not a 1,000-draw-cell sample,
and its acceptance counts do not estimate population success rates.

- **A:** original input, xclim fitting path, starts and optimizer defaults;
  capture termination status and refuse unsuccessful fits diagnostically.
- **B:** normalize each input as `(sample-mean)/population_std`, using `ddof=0`;
  use the same xclim GEV likelihood and optimizer defaults; map location, scale
  and scalar quantiles back; apply the same explicit status handling.

Acceptance requires status 0 and optimizer success, plus the existing finite
parameter, positive scale and finite quantile checks. Every refused raw estimate,
parameter vector, status and warning remains retained. No fallback, tolerance,
iteration-budget, dependency or extra support-based refusal rule was introduced.
Scalar xclim quantile calls preserve the `p=.9` inverse-survival route. Error
normalization still uses **generating scale one**, not the candidate's sample
standard deviation or fitted scale.

[protocol.json](results/protocol.json) fixes the candidates, selection and
unchanged original criteria before execution. [provenance.json](results/provenance.json)
binds source/environment and both prior evidence inventories. All 276 original
GF15 files and all 16 investigation files, plus their inventory files, remain
byte-exact with no added files. Bytecode writes were disabled when reusing the
read-only capture helper. All bound runtime and diagnostic sources remained
unchanged through completion. The candidate fitting/comparison stage took
70.79 seconds, excluding initial loading.

To reproduce from the repository root into an absent disposable directory:

```powershell
pixi run --as-is python dev/milestones/r12/implementation/evidence/gf15-candidates/compare-candidates.py --output .tmp/gf15-candidates-new *> .tmp/gf15-candidates-new.log
```

## Results and denominators

| Measure | A: status only | B: normalization + status |
|---|---:|---:|
| Attempted fits | 186 | 186 |
| Accepted / refused fits | 180 / 6 | 180 / 6 |
| Raw scalar quantiles | 225 | 225 |
| Accepted / refused scalar quantiles | 216 / 9 | 216 / 9 |
| Attempted translation pairs | 147 | 147 |
| Both-accepted numerical comparisons | 144 | 144 |
| Within existing `1e-6` criterion | **2 / 144** | **144 / 144** |
| Numerical disagreement | 142 / 144 | 0 / 144 |
| Both-refused pairs, no numerical proof | 3 | 3 |
| Changed acceptance classification within pairs | 0 | 0 |

All 180 predetermined fits report successful termination in both candidates.
All six purposive witness fits report status 1 at the unchanged 600-evaluation
limit and are refused. There are no estimator exceptions or fitting warnings.
Both-refused pairs are **not counted as numerical-equivalence successes**.
[candidate-results.json](results/candidate-results.json) retains every case and
[paired-translations.json](results/paired-translations.json) every pair outcome.

For the 144 both-accepted pairs, median absolute translation error falls from
`3.83e-5` in A to `5.02e-15` in B; P90 falls from `1.45e-4` to `2.01e-14`;
the maximum falls from **0.00131284 to `2.3892e-13`**. A exactly reproduces every
original parameter, status and scalar quantile. B's maximum estimate change
from A across the 216 accepted quantiles is 0.00159667. These results support
improved numerical conditioning in this subset, not demonstrated improvement
of the full benchmark's broad sampling-accuracy shortfall.

B's affine mapping is internally consistent for accepted fits: the maximum
residual in `NLL_physical = NLL_normalized + n*log(sample_std)` is `4.27e-14`;
the maximum difference between its mapped scalar quantile and a quantile
computed from mapped parameters is `1.78e-15`. All normalized and physical
log densities are finite in this subset. These mapping checks are diagnostics,
not new acceptance criteria.

The refused outputs remain materially unstable. B's largest refused raw estimate
is approximately **188.9 million** generating-scale units, and one refused pair
still differs by **33.03 million**. Its other two refused pairs have small raw
differences, but neither is accepted as numerical proof. Refused B fits also
show larger affine likelihood residuals, up to `1.84e-6`. Normalization therefore
does not rescue failed optimization or make those raw values publishable.

## Verification and interpretation

Controls demonstrate that finite parameters with unsuccessful status are refused,
the analytical parameter/quantile/likelihood mapping is consistent, a `2e-6`
paired perturbation is detected, changed validity is recorded, and both-refused
pairs cannot count as numerical proof. Every original solver option is asserted
unchanged. Complete objective evaluations are retained in
[optimizer-evaluations.jsonl.gz](results/optimizer-evaluations.jsonl.gz).

The coordinator independently verified both old inventories, all 372 statuses
and evaluation counts, all 450 primary quantiles, A's exact original parity,
B's parameter/quantile back-transforms and all 294 pair outcomes without importing
the candidate helper. These checks passed. Scoped Ruff lint and format checks
also passed; raw logs and [validation.json](validation.json) retain that evidence.

[candidate-summary.json](results/candidate-summary.json) preserves descriptive
scale and relative errors separately by selection, shape, count, probability
and ratio, with raw and accepted-only denominators. Zero-ratio relative error
remains undefined. No error from a refused fit is silently removed from the raw
record. Conditional summaries are not passed off as unconditional precision,
and correlated translations of the same draw are not independent samples.

## Recommendation and remaining decision

**Recommend a B-only full qualification attempt using the unchanged original
matrix, retained draws and already approved criteria**, subject to owner approval
of that next execution scope. This would evaluate the fixed normalization and
status policy over all 12 base cells, 1,000 draws each, both probabilities and
all five ratios: 132,000 fits and 144,000 primary quantile records. A full rerun
of A is not needed merely to re-establish the raw parity already demonstrated.

The full attempt must count every refusal against its 1,000-draw denominator,
keep raw rejected results, report conditional error denominators, test acceptance
classification across translations and distinguish both-refused pairs from
numerical comparisons. No criterion needs renewed approval or retuning. This
study does not authorize that full matrix or production integration.

The next test may still fail: status reporting and conditioning are not an
established remedy for the original `n=18` accuracy failures. This purposive
subset contains only three predetermined draws per shape/count cell, omits most
ratio cases, and cannot establish valid-fit rates or reliable error quantiles
for those cells. There is no claim about dependent/nonstationary blocks,
observed-bundle applicability, hydrological skill, uncertainty intervals or a
scientifically justified screening floor. No floor or blocks-per-return-period
increase is inferred. If B fails full qualification, preserve that failure and
return to an owner method ruling; do not relabel the original benchmark or alter
its criteria. GF15 adequacy and the milestone seal remain pending.
