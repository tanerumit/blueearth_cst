# GF15 L-moment independent assessment — Stage 3/3

This namespace contains an independent retained-data audit and scientific verdict.
The auditor imports NumPy and standard-library modules only. It neither imports
the Stage 2 evaluator/reducers nor calls an estimator. All predecessor, readiness,
qualification, installed-source and protected production bytes are read-only.

The owner authorized independent assessment on 2026-09-13. Verification is
rapid / numerical affected under the complete bounded audit contract. The new
auditor has no production caller. Full repository tests, numerical baselines,
production workflows, fresh data, holdout, resampling and new fits are outside
this assessment. No environment was changed.

## Reproduction

Run from the pinned worktree root in PowerShell with the existing isolated
Python 3.12.13 environment (NumPy 2.4.6, SciPy 1.18.0, lmoments3 1.0.8):

```powershell
$Assessment = 'dev/milestones/r12/implementation/evidence/gf15-lmoments-assessment'
$StagePython = '.tmp/scratchpad/2026-09-11_0010/gf15-lmoments-readiness/venv/Scripts/python.exe'
$Scratch = '.tmp/scratchpad/2026-09-11_0010/gf15-lmoments-assessment'
& $StagePython -B "$Assessment/audit-retained.py" --output "$Assessment/results" *> "$Scratch/final-audit.log"
```

That is the executed final command. `results` must be absent: it is immutable
after execution and a second invocation there refuses. For reproduction, supply
a new absent scratch output directory and a new log filename. Do not delete or
overwrite the signed results to rerun. The script creates its source/environment
freeze before the audit and verifies source identity again before completion.
`source-freeze.json` was written before the final run. The final signed verdict
binds source, environment, inputs, independently recomputed results and handoff.
The parent adds the outer integration envelope and root artifact inventory.

## Audit coverage and comparison policy

All 748 Stage 2 inventory entries plus the root inventory are rehashed. The
complete signed Stage 1 inventory, source/control/environment bindings, all
177 protected files and six installed lmoments3 sources are checked. The complete
732 selected A/B files plus preflight are independently matched to their anchored
inventories, including all receipts, arrays and canonical key populations.
Every C chunk receipt and all 132,000 retained fit records are checked. Physical
sample hashes are reconstructed from the original array row plus A's offset.

The auditor independently reduces all A/B/C individual cells and AB/AC/BC
intersection cells; checks every one of 432,000 pair rows and 120,000 translation
rows; and reconstructs branch predicates from recorded t3 and pinned source
coefficients. It checks stored support counts directly from retained parameters
and samples, and nonfinite log-density counts from the recorded density vectors.
It does not refit parameters or introduce a new likelihood refusal policy.

Comparison is exact decoded equality, including floating values, nulls and gate
booleans. Booleans cannot alias numbers. There is no comparison tolerance, no
rounding before a gate, and no waiver. Statistical summaries use NumPy linear
quantiles, generating scale one and explicit accepted cohorts. All valid rates
retain the 1,000-draw denominator; intersections cannot replace individual gates.

## Discrimination and development record

The checker rejects wrong error denominators, null/zero confusion, boolean/number
aliases and duplicate keys. Its reducer explicitly checks the 949/1,000 boundary
and its translation helper preserves nonnumeric both-refused pairs. An actual
disposable copy of the auditor changed `rate = len(selected) / 1000` to `/ 949`;
the check rejected it with `('949 valid denominator', 1.0, 0.949)`. The mutated
source and failure transcript are retained in `assessment-logs/`. The original
auditor then passed the complete final audit. Scoped Ruff check/format and compile
checks are retained alongside the audit transcript.

Two scratch-probe failures corrected the new auditor's schema assumptions before
source freeze: B retains numeric diagnostic errors even for refused fits, while
its paired rows correctly null them; A translated truth is the exact configured
rho, rather than the rounded floating sum of offset and baseline truth. These
are checker development history, not Stage 2 defects. Scratch probe logs remain
in the session scratch path above; no prior evidence was repaired or reclassified.

See [scientific-handoff.md](scientific-handoff.md) and
[signed-verdict.json](signed-verdict.json) for the bounded verdict.
