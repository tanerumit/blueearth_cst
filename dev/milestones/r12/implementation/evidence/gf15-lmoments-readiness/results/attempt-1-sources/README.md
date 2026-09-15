# GF15 L-moment Stage 1 implementation readiness

Owner instruction **“continue to Stage 1”**, 2026-09-12, releases the accepted
readiness brief. This bundle implements that bounded stage. It does not qualify
the estimator or authorize Stage 2, production integration, baseline recording,
screening changes, or R12 sealing. A and normalized B remain failed.

Authored source is beside this file. `environment/` freezes the isolated runtime
and package recreation instructions. `results/` is an exclusively claimed core
attempt; its completion is conditional on independent scientific review.
`results/independent/` is reserved for the separate model-validator, whose signed
verdict is required before readiness integration. `independent-review.py` is an
independently coded **mechanical** checker, not that scientific verdict.

The five Python files have no run-path or production callers. Verification scope
is rapid, numerical claims affected, with the brief's explicit D1–D6 controls
overriding the default small test budget. No full suite or baseline is applicable.

## Reproduce from the repository root

Recreate the pinned environment first using [environment/README.md](environment/README.md).
The effective runtime is Python 3.12.13, NumPy 2.4.6, SciPy 1.18.0, lmoments3
1.0.8 and pytest 9.0.3. PyPI wheels in this isolated environment differ from the
predecessor's conda package builds; the predecessor lock is provenance, not the
new effective environment. The wheel/source identities are independently recorded.

```powershell
$Readiness = 'dev/milestones/r12/implementation/evidence/gf15-lmoments-readiness'
$Scratch = '.tmp/scratchpad/2026-09-11_0010/gf15-lmoments-readiness/worker'
$StagePython = '.tmp/scratchpad/2026-09-11_0010/gf15-lmoments-readiness/venv/Scripts/python.exe'

# Complete frozen fixed attempt: output and final scratch directories must be absent.
& $StagePython -B "$Readiness/check-readiness.py" run-fixed --output "$Readiness/results" --scratch "$Scratch/final-controls" *> "$Scratch/final-controls.log"

# Read-only mechanical verification; output must be absent.
& $StagePython -B "$Readiness/independent-review.py" --results "$Readiness/results" --output "$Scratch/mechanical-review.json" *> "$Scratch/mechanical-review.log"
```

Never rerun into an existing frozen output. An output collision is a refusal,
not permission to replace it. An interrupted attempt has a `failure.json` and
cannot acquire a success receipt. Fixed disposable chunk tests exercise exact
hash-bound reuse, matching-binding partial payload recovery, competing writer
refusal and inconsistent-receipt refusal. They assert no managed-root run-control
conformance. Source/environment changes invalidate a frozen completion's identity.

The final command verifies all predecessor selections, runs the complete focused
test suite, runs and exactly replays the numerical controls, rechecks protected
bytes and runtime/source identities, then atomically publishes `completion.json`.
Its receipt hashes core generated files; the driver's later outer inventory binds
the independent review envelope. Generated pytest work stays in scratch.

## Executable contract checks

These are the concrete replacements for every brief command placeholder. Set the
three PowerShell variables above. Each JSON output name is exclusive; choose a
new scratch name if a previous invocation already produced it.

| Contract | Focused command |
|---|---|
| D1 truth blindness, source fidelity, no RNG/fallback | `& $StagePython -B -m pytest "$Readiness/test_readiness.py" -v -k 'truth_blind or invalid_samples or conjunction' -o "cache_dir=$Scratch/pytest-cache"` |
| D2 fault boundary and baseline conjunction | `& $StagePython -B -m pytest "$Readiness/test_readiness.py" -v -k 'allowlist or unknown_fault or conjunction or overflow_warning' -o "cache_dir=$Scratch/pytest-cache" --basetemp "$Scratch/d2-controls"` |
| D3 frozen criteria and synthetic schema | `& $StagePython -B -m pytest "$Readiness/test_readiness.py" -v -k d3_synthetic -o "cache_dir=$Scratch/pytest-cache"` |
| D4 complete inventory/join audit | `& $StagePython -B "$Readiness/check-readiness.py" audit-inputs --output "$Scratch/input-audit-final.json"` |
| D5 original population, independent branch reference and precedence | `& $StagePython -B "$Readiness/check-readiness.py" numerical-controls --output "$Scratch/d5-d6-fixed.json"` |
| D6 same-float independent CDF controls | The preceding `numerical-controls` command emits both coordinates and both precision passes for every fixed case. Falsifiers: `& $StagePython -B -m pytest "$Readiness/test_readiness.py" -v -k 'quantile or forward_cdf or population_gate' -o "cache_dir=$Scratch/pytest-cache"` |
| D6 replay, immutable namespace and fault stop | `& $StagePython -B -m pytest "$Readiness/test_readiness.py" -v -s -k 'namespace or unknown_fault or truth_blind' -o "cache_dir=$Scratch/pytest-cache" --basetemp "$Scratch/replay-controls"` |
| Independent readiness review entry point | `& $StagePython -B "$Readiness/independent-review.py" --results "$Readiness/results" --output "$Scratch/mechanical-review.json"`; the independent model-validator then reviews equations, interval propagation, source origins, joins and limitations, and signs the core receipt identity under `results/independent/`. |

The final aggregate command executes all these contract families; the focused
commands are for iteration and inspection. Some tests intentionally inject faults
and assert that the relevant production control fails. A green test means the
fault was detected, not that the mutated calculation passed.

## Numerical implementation and retained evidence

The adapter's only public evaluator input is `fit_case(sample, probabilities)`.
It uses unbiased order-statistic sample moments, the pinned library inversion,
and the specified NumPy inverse. It preserves tied values and diagnostic sample
support exclusion, records warnings even on early refusal, and propagates unknown
faults. Exact built-in exception type/message, innermost code object/module,
installed file hash and raising line must all match the two allowed statements.
The nonconvergence classifier positive is explicitly synthetic, not an observed
natural sample failure. Branch evidence observes real source line execution and
the pre-snap G value without modifying estimator locals.

Independent constants come from [NIST DLMF](https://dlmf.nist.gov/3.12) and its
linked [pi](https://oeis.org/A000796/b000796.txt) and
[Euler](https://oeis.org/A001620/b001620.txt) digit tables. Gamma uses recurrence
to at least 100, exact rational Bernoulli coefficients and the positive-real
[Stirling remainder bound](https://dlmf.nist.gov/5.11). Its omitted-term target is
1e-60, stricter than the required 1e-40, to resolve cancellation near the Gumbel
controls; this changes no fitted estimator or scientific tolerance. Both 80- and
120-digit computations and their coefficients/bounds are retained. Shape roots
use outward signs and the fixed [-1,1], six-doubling, 256-step budget.

The CDF reference never evaluates the inverse expression. Its interval arithmetic
directs basic operations and takes adjacent Decimal values around correctly
rounded ln/exp outputs; it never uses general Decimal power. It independently
expands each side and bisects the forward log-CDF at 80/120 digits. Exact binary64
parameter/probability/output bits, unrounded enclosures, widths, normalized error
bounds, endpoint/rounding-cell diagnostics, probability residuals and separate
display-rounding allowances are recorded. Display allowances do not enlarge T.

Expected fixed coverage is three original population controls, 19 branch controls,
44 p/control combinations and 88 normalized/physical dual-precision comparisons
(176 individual precision passes per numerical run). Fixed physical controls use
the positive map a=7.25, s=3.5, with separately rounded parameters and output.
Population tolerances remain 1e-5; quantile tolerance remains 1e-10 times the
normalized magnitude. Characterization never overrides an original failed gate.

The complete D4 selection is 12 A arrays, 240 A chunks, 240 B chunks and 240 B
receipts; an additional B preflight file binds receipts. Both canonical 144,000-key
sets include refused rows and distinguish null baseline from translated zero.
A acceptance is its own per-p `valid`; B is its own fit-wide `accepted`. A samples
and offsets are loaded from A, never from B's copied original fields or a seed.
The audit freezes the sorted canonical-key-set hash and file manifests.

## Validation and failure record

Initial missing-module pytest collection was expected red setup evidence.
Behavioral discrimination additionally mutates sign, tuple, probability, output,
enclosure widths/overlap, original population recovery, warning retention,
canonical keys and receipts; unknown library/adapter faults must leave no receipt.
An early warning-retention defect was fixed and its old behavior is reintroduced
in a disposable test to prove detection. Two initial one-line population probes
had syntax errors; their logs were preserved and replaced by a readable scratch
script. No fit occurred in those failed commands. All iterative logs are in the
worker scratch directory, and final source hashes precede the complete final run.

Scoped source checks:

```powershell
& '.pixi/envs/default/python.exe' -m ruff check $Readiness
& '.pixi/envs/default/python.exe' -m ruff format --check $Readiness
git diff --check
git status --short
```

The Pixi executable is unavailable in this session. The parent runs the exact
documented task bodies through the installed interpreter: `python -m ruff check .`
and `python -m ruff format --check .`. The repo's Ruff configuration includes
these evidence scripts. No environment repair or full test suite is implied.

## Still deferred

Stage 2 requires separate authorization for all 132,000 candidate fits, 144,000
quantile rows, 144 cell summaries and 120,000 translation pairs, preserving every
original GF15 gate, acceptance category and pairwise accepted-key intersection.
The full candidate branch histogram and exhaustive translation behavior remain
unexecuted. Stage 3 independently recomputes counts, errors and gates and issues
the qualification verdict. Readiness establishes none of that finite-sample
accuracy, fresh-seed replication, screening validity or basin applicability.
The retained development matrix is adaptive selection data; Monte Carlo
uncertainty is unquantified and derived rows share draws. No no-network assertion
is made, no new draws are generated, and no full-matrix performance verdict is
reported here.
