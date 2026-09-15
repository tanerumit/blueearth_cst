# Independent scientific readiness verdict — GF15 Stage 1

**Accept Stage 1 readiness for `results/attempt-2` only.** Signed by model-validator
`/root/model_validator_gf15_readiness`, 2026-09-12T19:35:39.399709+00:00.
No unresolved blocking finding remains. This signature does not qualify the
candidate, reverse A/B failures, authorize Stage 2, integrate production, alter
screening, or seal R12. The original completed attempt remains unaccepted because
of MV-1; its bytes and source snapshot are retained.

The signed [machine record](signed-verdict.json) binds every source, environment,
input and control identity. Attempt SHA-256:
`f9ec75b802552aa4005f8545a24e10d6a98004d0d408408f55e20e3aebc44038`. Completion SHA-256:
`7cba09d4bf7af14a93b08e9deedff7b48dd5fe019cd1baf9e992a11bf651338c`. Any bound source/environment/control change
invalidates this acceptance. The independent evidence inventory is local to this
review envelope; it does not mutate the core receipt.

## Scientific contract assessment

D1/D2 are implemented faithfully: positive range normalization; unbiased
order-statistic PWMs with retained ties; named lmoments3 inversion; SciPy sign
c=-xi; finite-mean domain c>-1; the prescribed NumPy inverse and positive affine
mapping. The independent exact-rational PWM check on the existing tied control
differs by at most 5.56e-17. Truth is absent from the candidate interface; inspected
call-count and RNG/state tripwires verify one inversion and no fallback. A bad
probability revokes the shared baseline pair while preserving per-p diagnostics.
Sample support exclusion remains diagnostic.

The downloaded pinned wheel hashes correctly and all six recorded installed
Python sources match its members ([wheel verification](wheel-check.json)). The
allowlist matches exact built-in type/message, innermost installed code object,
module, source digest and raising line 1307/1342. Actual invalid-moment origin is
exercised; the nonconvergence positive is explicitly synthetic. Conversion,
wrong-origin/type/message, memory and adapter faults propagate and cannot obtain
a chunk completion receipt. No naturally observed nonconvergence is claimed.

D4 includes all 732 selected files/receipts plus the B preflight binding. The
mechanical checker rehashed every selected artifact. My separate streaming join
independently reconstructed both complete 144,000-key sets without evaluator
helpers: 144,000 A valid rows, 143,915 B accepted quantile rows. Null baseline is
distinct from translated zero; refused rows and predecessor status semantics are
retained. Truth/offset pairs agree. The core audit additionally verifies arrays,
chunk receipt counts/bindings, baseline offset conjunction and translated offsets.
Negative controls reject dropped/duplicate/corrupt keys and receipts. No retained
sample was refitted by this review.

D3's synthetic reducers preserve all-draw denominators, accepted-error cohorts,
linear quantiles, null zero-ratio relative errors, diagnostic .05, unchanged
thresholds, empty-cohort nulls and four acceptance categories. These are schema
controls; no candidate 144-cell performance summary has been produced.

D5's three population gates precede the frozen 19-row characterization. All
population errors are below their original 1e-5 limits; the tau(.2) overlap retains
population-gate precedence and no tau(-.2) branch row was added. Exact executed
source-line traces verify branch selection and pre-snap G. Oracle roots preserve
the fixed [-1,1] start, six upper doublings and 256-step budget, with 1e-40 brackets,
1e-35 root agreement and 1e-30 parameter agreement across 80/120 digits. Gamma is
independent of SciPy/lmoments3: recurrence to >=100, exact rational Bernoulli
coefficients and a first-omitted log-series term <=1e-60. The positive-real
remainder rule agrees with [NIST DLMF 5.11(ii)](https://dlmf.nist.gov/5.11#ii).
My separate Machin-pi calculation agrees to 1.53e-146; Gamma(1/2)^2 differs from
that pi by 5.73e-60; the .8-to-1.8 Gamma recurrence differs by 1.78e-148.

| Population c | abs shape error | abs location error | abs scale error | Gate |
|---|---:|---:|---:|---|
| -.2 | 1.227e-08 | 5.254e-09 | 1.619e-08 | pass |
| .2 | 1.913e-07 | 8.838e-08 | 1.201e-07 | pass |
| 0 | 0.000e+00 | 4.902e-09 | 0.000e+00 | pass |

D6 compares actual binary64 outputs with forward-CDF enclosures under identical
binary64 c/location/scale/p, separately in normalized and rounded physical
coordinates. Decimal ln/exp use neighboring representable values and signed
outward arithmetic, not assumed directed transcendental rounding or general
power; this matches the [Python Decimal contract](https://docs.python.org/3.12/library/decimal.html).
All 88 coordinate comparisons pass at both 80/120 digits. I independently checked
each recorded endpoint's forward-CDF sign at 150 digits, each tuple's bits, the
unmodified T=1e-10*M and width budget. The maximum normalized output-to-enclosure
error bound is 7.348850625363306e-16. The 150-digit scalar check is an additional
diagnostic; the accepted enclosures rest on the reviewed outward interval method.

MV-1 exposed a rounded endpoint c=60,loc=0,scale=60,p=.9,output=1: the quantile
gate passed but the optional probability residual raised on support-straddling
interval standardization. The original [counterexample](endpoint-finding.json)
is preserved. The engineer observed the regression red, then confined the repair
to an explicit conservative [0,1]-p diagnostic interval after unchanged quantile
and support-rounding gates. My repeated counterexample passes in attempt-2; its
full tuple, bounds and unresolved diagnostic status are in
[scientific probes](scientific-probes.json). No tolerance or estimator changed.

Fixed chunks exercise absent/exclusive namespace claims, single-writer refusal,
atomic receipts, identical-binding reuse, matching partial-payload recovery,
hash conflicts and inconsistent receipts. Numerical controls replay exactly;
the test transcript records two computed chunks and one reused chunk. The final
45-test transcript passes. I independently rehashed all 177 protected files and
the complete environment metadata at signature. This is local evidence handling,
not managed-root run-control conformance.

## Frozen branch characterization

All discrepancies below are against the independent oracle; location/scale
errors are divided by reference scale. The common 1e-5 reference line is retained.
All listed discrepancies fall below it. The snap rows' roughly 5e-6 shape errors
reflect the prescribed snap; rational and Newton discrepancies reflect the
unmodified library's approximation and stopping choices. Finite controls do not
bound error throughout a branch. Exact rows, constants and traces are hash-bound
in attempt-2/numerical-controls.json.

| Fixed input label | Observed branch | abs delta c | abs delta loc / scale | abs delta scale / scale |
|---|---|---:|---:|---:|
| positive_.50 | positive_rational | 1.247E-7 | 3.866E-8 | 2.659E-7 |
| positive_tau_.2 | positive_rational | 1.913E-7 | 8.838E-8 | 1.201E-7 |
| snap_tau_0 | positive_snap | 1.626E-17 | 4.902E-9 | 9.110E-19 |
| snap_tau_-.000005 | positive_snap | 5.000E-6 | 2.284E-6 | 4.619E-6 |
| snap_tau_.000005 | positive_snap | 5.000E-6 | 2.274E-6 | 4.619E-6 |
| snap_tau_-.00002 | positive_rational | 1.549E-7 | 7.061E-8 | 1.431E-7 |
| snap_tau_.00002 | positive_rational | 1.548E-7 | 7.058E-8 | 1.430E-7 |
| literal_-.000001 | nonpositive_rational | 2.262E-7 | 1.043E-7 | 1.183E-7 |
| literal_0 | nonpositive_rational | 2.262E-7 | 1.043E-7 | 1.183E-7 |
| literal_.000001 | positive_rational | 1.791E-7 | 8.262E-8 | 9.368E-8 |
| literal_-.30 | nonpositive_rational | 5.176E-9 | 2.219E-9 | 2.914E-10 |
| literal_-.799999 | nonpositive_rational | 3.133E-7 | 7.919E-8 | 3.210E-7 |
| literal_-.8 | nonpositive_rational | 3.134E-7 | 7.921E-8 | 3.211E-7 |
| literal_-.800001 | newton_rational | 3.042E-14 | 7.593E-15 | 3.164E-14 |
| literal_-.85 | newton_rational | 1.297E-15 | 3.759E-16 | 1.615E-15 |
| literal_-.969999 | newton_rational | 4.242E-12 | 3.966E-12 | 7.246E-12 |
| literal_-.97 | newton_alternate | 1.052E-11 | 9.855E-12 | 1.796E-11 |
| literal_-.970001 | newton_alternate | 1.052E-11 | 9.858E-12 | 1.797E-11 |
| literal_-.98 | newton_alternate | 1.860E-12 | 3.796E-12 | 3.364E-12 |

## Executed independent checks and limits

Interpreter: `.tmp/scratchpad/2026-09-11_0010/gf15-lmoments-readiness/venv/Scripts/python.exe`.
With `R=dev/milestones/r12/implementation/evidence/gf15-lmoments-readiness`, ran:

```text
python.exe -B R/independent-review.py --results R/results/attempt-2 --output R/results/independent/mechanical-review.json
python.exe -B R/results/independent/independent-probes.py --results R/results/attempt-2 --output R/results/independent/scientific-probes.json
```

Both passed. Source and wheel inspection, approved design/brief hash checks and
signature-time protected/environment rehashes also passed. Disposable logs are
under `.tmp/scratchpad/2026-09-11_0010/gf15-lmoments-readiness/validator/`.
Verification is rapid / numerical affected under the explicitly bounded D1–D6
contract. Production callers were searched in `blueearth_cst`, `scripts` and
root Snakefiles; none was found. Full suite, baseline, production workflow,
candidate matrix, holdout and bootstrap were deliberately not run.

This is implementation readiness on fixed synthetic controls. Numerical
reference uncertainty is bounded as above; parameter estimation, structural
misspecification, observations, nonstationarity and basin applicability are not
validated here. The retained matrix has 1,000 IID draws per generating shape/count
cell but derived probabilities/translations share draws; Monte Carlo uncertainty
and adaptive-selection optimism remain unquantified. No held-out replication or
statistical benchmark verdict follows. Stage 2 still requires separate authority
for 132,000 fits/144,000 quantiles, 144 unchanged cell gates, 120,000 translation
pairs and the complete branch histogram; Stage 3 must independently recompute
counts/errors/gates and issue qualification. A and B remain failed.
