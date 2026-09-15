# GF15 accuracy policy — eightfold error limits

Status: owner-approved reassessment; qualification outcome is separate
Date: 2026-09-13
Decider: repository owner
Lifecycle: frozen-with-supersession after assessment

The owner selected **"8x"** after sensitivity checks reported 143/144 candidate C
cells passing at 6x and 144/144 at 8x. The preceding approved 3x policy failed
124/144. These observed outcomes informed this adaptive decision; this record
does not portray the new limits as selected before results were known.

[criteria.json](criteria.json), `gf15-accuracy-8x-v1`, controls this assessment.
Exactly four error-threshold fields change from original GF15, plus authority,
estimator and policy metadata. Explicit decimal literals avoid multiplication
roundoff at inclusive boundaries.

| Requirement | Original | Approved 8x |
|---|---:|---:|
| Absolute signed median scale error | 0.10 | 0.80 |
| Absolute signed median relative error | 0.10 | 0.80 |
| P90 absolute error, upper p=0.9, both coordinates | 0.50 | 4.00 |
| P90 absolute error, lower p=0.5, both coordinates | 0.25 | 2.00 |

Relative limits permit 80% absolute signed median error, 400% upper P90 error
and 200% lower P90 error. These are permissive owner-selected performance
targets, not demonstrated precision, uncertainty coverage or improved estimation.

All other original GF15 rules remain: 95% valid-fit floor over all 1,000 draws;
generating-scale normalization; unchanged accepted cohorts and linear quantiles;
relative qualification only at rho=0.5,2,10; diagnostic rho=0.05; undefined/null
zero relative error and baseline convention; unchanged translation acceptance
and 1e-6 paired scale-error gate; candidate C all-cell conjunction; original
readiness/reference and runtime validity controls. A/B remain diagnostics.

Keeping original or 3x limits preserves their signed failures. Sixfold limits
offer a smaller relaxation but the reported sensitivity still fails one cell.
Eightfold limits were explicitly selected; no further relaxation is implied.
The estimator, fits and evidence matrix do not change. Both original and 3x
assessments remain intact and are verified during this assessment.

This is a post-results adaptive policy check on signed Stage 3 development
summaries, with no fresh seed, holdout, refitting or estimator improvement.
Finite Monte Carlo uncertainty remains unquantified; shared draws make cell
counts dependent. No screening change, automatic production adoption, expanded
applicability claim or R12 seal follows from a passing result.

[scientific-handoff.md](scientific-handoff.md) gives the verified outcome,
regime diagnostics, limitations and reproduction commands. Sources are frozen
before final scoring, and signed result bindings retain the exact evidence.
