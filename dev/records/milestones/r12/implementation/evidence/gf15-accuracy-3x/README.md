# GF15 accuracy policy — threefold error limits

Status: accepted by owner for reassessment; qualification outcome is separate
Date: 2026-09-13
Decider: repository owner
Lifecycle: frozen-with-supersession after this assessment
Revisions: 2026-09-13 — owner selected threefold limits and requested evaluation.

## Context and decision

The original, normalized and L-moment estimators failed the original GF15
accuracy targets. The independently audited L-moment matrix is retained under
[`gf15-lmoments-assessment`](../gf15-lmoments-assessment/scientific-handoff.md).
The owner requested less strict accuracy requirements and then selected:
"lets tripple and check if that will be enough".

[`criteria.json`](criteria.json), policy `gf15-accuracy-3x-v1`, is the controlling
specification for this reassessment. It replaces the four error-threshold fields
for this named evaluation only; it does not rewrite the original criteria,
accepted estimator design, completed runs or signed failure verdicts.

| Requirement | Original | Revised |
|---|---:|---:|
| Absolute signed median scale error | 0.10 | 0.30 |
| P90 absolute scale error, upper | 0.50 | 1.50 |
| P90 absolute scale error, lower | 0.25 | 0.75 |
| Absolute signed median relative error | 10% | 30% |
| P90 absolute relative error, upper | 50% | 150% |
| P90 absolute relative error, lower | 25% | 75% |

Valid-fit rate remains at least 95% of all 1,000 draws per cell. Translation
requires unchanged acceptance and the original 1e-6 scale-error difference gate.
Relative gates still apply only at ratios 0.5, 2 and 10; 0.05 remains diagnostic,
zero remains undefined, and baseline relative errors retain their null convention.
All required cells must pass; no pooling or dropped cells is introduced.
The retained point estimates, accepted cohorts, linear quantiles and estimator
are unchanged. Scale errors use generating scale, not sample range or fitted scale.
Stage 1 numerical-reference tolerances and runtime validity checks do not change.

## Alternatives and consequences

Keeping the original policy preserves its stricter target but retains the known
qualification failure. Doubling the limits was also evaluated as a smaller
relaxation; the owner selected tripling. These are owner-selected performance
targets, not demonstrated precision guarantees or a claim that the estimator
improved. In particular, the revised upper relative P90 limit allows 150% error.

Selection occurs after observing the development data. Re-scoring these same
results is a conditional policy check, not fresh validation. Finite Monte Carlo
uncertainty remains unquantified; probabilities, translations and methods share
draws. No holdout, resampling, screening change, production adoption or R12 seal
follows automatically, even if the new conjunction passes.

## Validation and outcome

The model-validator verifies signed input identities, checks the exact threshold
delta, re-scores every retained cell and reports old/new gates and margins.
Candidate C determines the policy result; A/B may be reported as diagnostics.
Boundary/mutation checks must detect incorrect thresholds and cohort rules.
Execution reuses independently audited summaries and performs no new fits.

The [scientific handoff](scientific-handoff.md) records the executable command,
verification, complete outcome and remaining failures. Its assessment and the
generated manifests are bound by the final artifact inventory. No additional
threshold increase is authorized by a failure of this threefold policy.
