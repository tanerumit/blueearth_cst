# GF15 eightfold accuracy-policy assessment

**Candidate C passes the approved 8x fixed-matrix policy: 24/24 baseline,
72/72 eligible relative-plus-scale and 144/144 individual cells.** This is an
adaptive policy reassessment, not new validation or improved estimation. Original
and 3x failures remain authoritative under their respective criteria. No
automatic production adoption, screening change or R12 seal is authorized.

Assessor: model-validator `/root/model_validator_gf15_8x`, 2026-09-13.
Owner approval quote: **"8x"**, after observing 6x and 8x sensitivity results.
[README.md](README.md) records alternatives and consequences; the controlling
policy is [criteria.json](criteria.json), `gf15-accuracy-8x-v1`.

## Intended use and policy

Assess whether frozen range-normalized L-moment candidate C meets the newly
approved performance targets on the existing synthetic GEV development matrix.
The four error-threshold fields are absolute signed median scale and relative
limits 0.80, and P90 absolute scale and relative limits 4.00 at p=0.9 and 2.00
at p=0.5. Relative limits mean **80% median, 400% upper P90 and 200% lower P90**;
they are not confidence levels or precision guarantees. Signed median is not
median absolute error. Explicit decimal literals set the inclusive boundaries.

All other original rules remain unchanged: valid-fit rate at least 0.95 of
all 1,000 draws; generating-scale normalization; estimator-specific accepted
cohorts and linear quantiles; relative qualification at rho=0.5,2,10 only;
rho=0.05 diagnostic; baseline and zero relative summaries null; all-cell
conjunction; unchanged paired acceptance and 1e-6 translation scale-error gate;
readiness and runtime validity requirements. No new fitting occurs.

The changed verdict is an intended, scientifically material policy change:
loss statistics and estimator performance are unchanged. The owner knowingly
selected a more permissive target after results. This cannot establish accuracy
on independent data, and no held-out validation is claimed.

## Evidence integrity and outcomes

The reducer verifies pinned Stage 3 inventory and signed-verdict identities,
every listed artifact and signed local binding, and the nested result inventory.
It independently recomputes the full original margins/decisions for A/B/C,
checks all 144 keys per method, and reproduces their signed aggregate counts.
It also verifies the 3x root/result inventories and exactly reproduces every
3x rescored cell from the unchanged Stage 3 summaries. Both failed assessments
are preserved. All 432 cells, including baseline versus zero-ratio distinctions,
are retained; summaries are never pooled or rounded before gating.

The prior signed Stage 3 audit supplies fit-level/cohort/source verification;
its 132,000 fits and 432,000 paired rows are not regenerated or re-audited here.
The present operation checks summary policy reduction and evidence integrity.
Source/input bindings freeze before the final result computation and are checked
again afterward. The final signed verdict binds this handoff and all result
files; inventories use SHA-256 byte identities, not cryptographic identity signing.

| Method/policy | Baseline scale /24 | All scale /144 | Eligible combined /72 | All combined /144 |
|---|---:|---:|---:|---:|
| A original | 3 | 18 | 6 | 15 |
| A 3x diagnostic | 20 | 120 | 48 | 108 |
| A 8x diagnostic | 24 | 144 | 71 | 143 |
| B original | 3 | 18 | 6 | 15 |
| B 3x diagnostic | 20 | 120 | 48 | 108 |
| B 8x diagnostic | 24 | 144 | 71 | 143 |
| C original | 3 | 18 | 6 | 15 |
| C 3x | 23 | 138 | 55 | 124 |
| C 8x assessed candidate | 24 | 144 | 72 | 144 |

A/B are frozen predecessor comparators using the same draws. Generating truth
defines loss; there is no newly introduced naive benchmark or claim of meaningful
out-of-sample skill against one. Candidate C alone determines this policy verdict.

| Candidate C regime | Combined passes |
|---|---|
| SciPy c=-0.2, 0.0, 0.2 | 48/48 each |
| n=10,18,30,60 | 36/36 each |
| p=0.9,0.5 | 72/72 each |
| baseline; rho=0,0.05,0.5,2,10 | 24/24 each |

At n=18, C passes 6/6 baseline and 18/18 eligible combined cells. All C valid
rates are 1.0. The tightest qualified relative margins remain at
c=-0.2,n=10,p=0.9,rho=0.5: absolute signed median 0.7096987457437947 versus
0.80 (margin 0.09030125425620539), and P90 3.8309444134013266 versus 4.00
(margin 0.16905558659867337). Thus a pass still permits very large errors.
Diagnostic near-zero relative errors remain outside the qualification:
for example c=-0.2,n=10,p=0.5,rho=0.05 has relative P90 14.856985611770813.
No failure is hidden by treating that diagnostic population as qualified.

[summary.json](results/summary.json) stratifies every method by c,n,p,rho;
[individual-cells.json](results/individual-cells.json) retains every statistic,
margin and gate. [failures.json](results/failures.json) contains remaining A/B
diagnostic failures; candidate C has none under 8x. The original and 3x failure
regimes have not disappeared scientifically; only their policy classification
changes under 8x.

All 120 translation cells pass unchanged: 120,000 both-accepted pairs, zero
numerical failures, maximum absolute scale-error delta 5.88373794130348e-12
against 1e-6. Translation records are unchanged as decoded JSON; this stability
does not establish accuracy.

## Uncertainty and limits of applicability

| Source | Quantification and unresolved component |
|---|---|
| Parameter-estimation variability | Signed median and absolute-error P90 on 1,000 IID stationary GEV samples per c/n base cell; no parameter intervals. |
| Finite Monte Carlo variability | 12 base cells, 1,000 draws each; draws shared across probabilities, translations and methods. Sampling uncertainty in medians/P90s/rates remains unquantified. |
| Adaptive selection | Candidate and thresholds selected using already observed development data; no fresh seed, holdout, temporal/spatial split or selection adjustment. |
| Numerical computation | Inherited signed readiness controls and unchanged paired translation tolerance; no new numerical tolerance. |
| Structural and observational uncertainty | Real discharge, block extraction, dependence, nonstationarity, GEV misspecification and observational errors are not represented. |
| Climate scenario and internal variability | Not quantified by these IID synthetic fixtures. |

P90 is a 90th percentile of absolute errors, not a confidence interval for
accuracy. Passing margins carry no uncertainty coverage. More replay of this
same matrix cannot resolve structural uncertainty or adaptive selection. The
low-flow estimand is the median of annual seven-day minima without sign reversal;
these fixtures do not test its extraction or real-basin applicability.

## Reproduction and verification

Run from the worktree root, with assertions enabled (never `-O`):

```powershell
$Assessment = 'dev/milestones/r12/implementation/evidence/gf15-accuracy-8x'
$StagePython = '.tmp/scratchpad/2026-09-11_0010/gf15-lmoments-readiness/venv/Scripts/python.exe'
$Scratch = '.tmp/scratchpad/2026-09-11_0010/gf15-accuracy-8x'
& $StagePython -B "$Assessment/check-rescore.py" *> "$Assessment/verification/boundary.log"
& $StagePython -B "$Assessment/rescore.py" --output "$Assessment/results" *> "$Scratch/final-rescore.log"
```

These are the final boundary and scoring commands. Reproduction must use a new
absent output directory and separate log, preserving signed artifacts.
`source-freeze.json` is written first; signed verdict and result inventory last.
The parent integration envelope retains the final execution transcript, which
cannot be included in its own source freeze.

Verification: release decision / numerical affected, with the task's explicit
bounded evidence-only scope and repo dev-only ladder. Caller search
`rg -n 'gf15-accuracy-8x|check-rescore' blueearth_cst tests scripts` found no
production caller. The adapted checker first failed with absent implementation,
then passed inclusive/over-limit median and P90, 950/949 valid-count boundaries,
relative eligibility and null conventions. An actual half-P90 reducer mutation
is rejected with AssertionError. Scoped Ruff lint/format and in-memory compilation
pass. [verification/commands.md](verification/commands.md) records exact commands
and retained logs. No full suite, model workflow, fit, bootstrap, new sample,
readiness rerun or baseline comparison is needed for this summary-only task;
production code and numerical estimators are unchanged.

Candidate C satisfies the approved eightfold targets on this retained synthetic
matrix. This result does not overturn the original/3x failures, improve the
estimator, or qualify it for real hydrological decisions. Fresh-data stability,
Monte Carlo uncertainty, structural error and observed-system applicability
remain unresolved. Production adoption and R12 seal require separate decisions.
