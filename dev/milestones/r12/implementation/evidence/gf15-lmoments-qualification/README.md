# GF15 L-moment Stage 2 bounded qualification

This evidence namespace executes the separately authorized Stage 2 matrix using
the exact independently accepted Stage 1 adapter. It provides observed mechanical
gate outcomes only; independent Stage 3 scientific acceptance remains pending.
Production, screening, environments, A/B evidence and frozen Stage 1 are unchanged.

## Commands and verification scope

Run from the worktree root in PowerShell. The isolated interpreter is the existing
Stage 1 environment; no installation is needed. Disposable logs and pytest files
live in the scratch directory shown below. Pixi CLI is unavailable; the installed
shared interpreter provides Ruff. Verification is rapid / numerical affected:
three focused evaluator tests plus the complete authorized matrix and mechanical
audit; no repository suite, baseline, bootstrap, holdout or production run.

```powershell
$StagePython = '.tmp/scratchpad/2026-09-11_0010/gf15-lmoments-readiness/venv/Scripts/python.exe'
$Qualification = 'dev/milestones/r12/implementation/evidence/gf15-lmoments-qualification'
$Scratch = '.tmp/scratchpad/2026-09-11_0010/gf15-lmoments-qualification'
& $StagePython -B -m pytest "$Qualification/test_qualification.py" -q -o "cache_dir=$Scratch/pytest-cache" --basetemp "$Scratch/final-test-tmp" *> "$Scratch/final-tests.log"
& '.pixi/envs/default/python.exe' -m ruff check $Qualification
& '.pixi/envs/default/python.exe' -m ruff format --check $Qualification
& $StagePython -B "$Qualification/qualify-lmoments.py" prepare --output "$Qualification/results"
& $StagePython -B "$Qualification/qualify-lmoments.py" run --output "$Qualification/results" *> "$Scratch/matrix-run.log"
```

`prepare` requires an absent results directory, verifies all signed Stage 1
bindings and effective runtime, and repeats the complete D4 audit: 732 selected
A/B files and receipts plus B preflight, all 12 original float64 arrays, and both
144,000-key populations including refused rows. It freezes source, environment,
unchanged A criteria bytes, complete input manifests and evaluator conventions
before any matrix fit. Stage 1 fixed population/branch/CDF controls are reused
only through their accepted signed hashes; they are not refitted here.

`run` rechecks that complete binding before fitting and after summaries. It uses
one writer and 240 deterministic 50-draw chunks. Each of the 12,000 original
draws receives one baseline fit requesting both probabilities and ten independent
translated fits, totaling 132,000 fits and 144,000 quantiles. Samples and offsets
come only from A, with no seed regeneration, clipping, retry or fallback.

## Retained evidence and resumability

`results/provenance.json`, `input-audit.json`, `environment.json` and exact
`criteria.json` bind execution. Each `chunks/c{i}-n{n}-{start}/fits.jsonl.gz`
contains 550 fit records with 600 nested quantile records. `adapter_record` retains
the exact adapter return: moments, normalized and physical parameters, sample
identity, normalization values, probability diagnostics, warnings, explicit and
exception-derived refusals, support and log-density diagnostics. Nonfinite
diagnostics are explicit strings; accepted errors must be finite. `branch`
repeats only the signed source-verified characterization predicates on recorded
t3; it does not alter the inversion. Pre-inversion refusals are separately counted.

Each chunk claims a writer exclusively and binds itself to provenance SHA-256.
Payload bytes are flushed before an atomic receipt. A matching valid receipt
permits exact reuse, with hashes and row counts checked again. A matching partial
payload may be recomputed; an unreceipted completed payload, partial receipt,
conflicting binding or competing writer refuses execution. A software exception
records `failure.json` and prevents a success receipt or automatic resume. A hard
process kill may leave a writer claim; it requires inspection, not automatic
lock removal. A completed attempt is immutable and refuses rerunning. This is
local evidence handling, not managed-root CST run-control conformance.

`individual-cells.json` preserves all 144 individual cells for each A/B/C.
A uses its original per-probability `valid`, B its fit-wide `accepted`, C its
shared baseline conjunction and scalar translated acceptance. Every valid rate
uses all 1,000 draws; conditional error counts are explicit. Scale errors divide
by A's generating scale (one), never fitted or range scale. Relative errors divide
by the absolute A true quantile, are null for baseline/zero ratio even if floating
rounding makes zero tiny, diagnostic at .05, and gated only at .5/2/10. Linear
median, median absolute and P90 absolute errors accompany unchanged gates and
signed passing margins; these margins are not uncertainty estimates.

`paired-keys.jsonl.gz` retains all 432,000 AB/AC/BC keyed comparisons including
four acceptance categories. `paired-cells.json` gives all 144 cells per pair,
their accepted-intersection draw IDs and denominators, and both estimators'
scale/relative errors on those same keys. Null baseline remains distinct from
translated zero; intersections never replace the individual gates.

`translation-pairs.jsonl.gz` retains all 120,000 C baseline/translated pairs with
unchanged-acceptance status, delta scale error, the unchanged 1e-6 gate and signed
margin when both accepted. Both-refused pairs have null numerical pass. The cell
gate preserves B's policy: at least 950 accepted pairs, unchanged acceptance for
every draw and zero accepted-pair numerical failures. `translation-cells.json`
reports all 120 cells. Statistical failures remain visible while execution
finishes every cell. `diagnostics.json` exhaustively counts all six branch/refusal
categories, warnings, support/log-density diagnostics and measured fit time.

`mechanical-audit.json` binds every core generated artifact, reverified chunk
receipts, canonical coverage and recomputed errors. Atomic `completion.json`
binds the audit and summary and records execution timing, counts and observed
gate conjunction. Completion is a mechanical execution record, not independent
qualification acceptance. The later root inventory may bind this envelope and
the parent's retained check logs without changing the core completion.

## Limits and Stage 3 handoff

Empirical medians, P90s and valid rates retain unquantified finite Monte Carlo
uncertainty. There are 1,000 independent retained IID GEV draws per shape/count
cell; probabilities, translations and method comparisons share draws and are
correlated. Exact replay and 120,000 translation pairs are not independent
accuracy replications. Adaptive reuse of the development matrix leaves selection
optimism and fresh-seed stability unknown. No uncertainty interval, screening
validity, real-bundle adequacy or basin/nonstationarity claim follows.

Stage 3 must independently recompute complete counts, joins, errors, individual
criteria, pair intersections, translation outcomes and branch coverage, then
issue a signed scientific verdict bound to the final completion identity. Any
criterion failure leaves this candidate failed and GF15 unresolved. No further
estimator search, criterion change, resampling, production integration or R12
seal is authorized by this run.

The accepted design's noncausal context concerns only the c=0 Gumbel location
submodel with known scale and shape: approximate efficient P90 absolute location
error 1.645/sqrt(n), not a finite-sample bound, candidate prediction or excuse for
failure. It says nothing about median bias, valid rates or c=-.2/.2.

| n | Reference | Baseline .50/.25 below? | rho=.5 .25/.125 below? | rho=2 1/.5 below? | rho=10 5/2.5 below? |
|---|---|---|---|---|---|
| 10 | .520 | yes / yes | yes / yes | no / yes | no / no |
| 18 | .388 | no / yes | yes / yes | no / no | no / no |
| 30 | .300 | no / yes | yes / yes | no / no | no / no |
| 60 | .212 | no / no | no / yes | no / no | no / no |
