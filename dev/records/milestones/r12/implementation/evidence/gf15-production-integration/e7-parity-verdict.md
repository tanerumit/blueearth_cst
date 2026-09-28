# E7 parity, refusal and diagnostic verdict — GF15 production Stage 2

Reviewer: independent `model-validator`, dispatched by the driver, blind to the
implementing conversation. Two rounds: **REJECTED** at `ebd85b88`, **ACCEPTED**
at `5cd2d8ce`. This is the gating artifact for Stage 3 under D8 handoff 2/4.

## Verdict

**ACCEPTED — Windows only.** Linux parity is **outstanding, not failed**:
nothing was installed or executed on linux-64, and D8 handoff 2/4 requires
source-qualified parity on every supported platform before integration. This
verdict cannot release cross-platform acceptance.

## Round 1 — REJECTED at `ebd85b88`

Every numerical field was already correct: 190 of 196 bit-compared pairs
identical, all 66 retained oracle references reproduced with no tolerance
touched, and 4000 randomized fits with zero accept/refuse disagreement. The six
divergences were all the same field, `warnings`, on one sample.

**F1 — MAJOR.** `_record_warnings` collected only in its `finally`, while
`refuse()` builds the `FitResult` *inside* the block, so every early refusal
carried `warnings=()` and `record()` serialized `"warnings": []`. D3 reserves
emptiness for "none occurred" and null for "unavailable", so this was an
affirmatively false record, not a missing one — and the erased warning was the
overflow that *explains* the refusal, in exactly the attempt logs D3 routes
failure diagnostics to and that Stage 3 reads to diagnose an aborted comparison.

It was asymmetric across refusal codes, which is worse than a uniform drop:
retained on the accepted and `quantile_conjunction` paths, dropped on
`invalid_range`, `nonfinite_normalization`, `invalid_moments`,
`invalid_parameters`, `invalid_physical_parameters` and
`allowlisted_library_exception`. Two refusals with the same discriminant carried
the field differently.

**It was a dropped control.** `test_readiness.py::test_overflow_warning_retention_discriminates`
exists for this exact regression and had no counterpart in the shipped suite,
which covered warnings only on the accepted and fault paths. The suite could not
catch a bug the frozen controls were written to catch. The reviewer called this a
fail rather than a note because the brief's acceptance criterion is "exact
fixed-tolerance parity, **refusal and diagnostic behavior**", and the design
requires scientific review before relaxing a retained control.

**F2 — LOW, against the record rather than the code.** `stage-2-record.md`
justified leaving the predecessor estimator in `_return_level_from_blocks` by
saying it "sits on the legacy `analyze_wflow_results` path", naming a live path
that does not exist in this tree.

## Round 2 — ACCEPTED at `5cd2d8ce`

Both findings cleared, and every round-1 pass re-confirmed.

| Harness | Round 1 | Round 2 |
|---|---|---|
| `parity.py` — 28 sample shapes × 7 probability sets, float64 bit patterns | 190/196 | **196/196**, warnings included |
| `controls.py` — retained oracle references | 3 population, 19 branch, 44 quantile, exact | unchanged, exact |
| `behaviour.py` — D3 codes, fault boundary, diagnostics, D4 coverage | 26/27 | **27/27** |
| `reduction.py` — extraction, decoupling, evidence, routing | 18/18 | 18/18 |
| `legacy.py` — D6 reads without lmoments3 | 5/5 | 5/5 |
| `endpoint.py` — 4000 randomized bounded-upper-tail fits | 0 mismatches, 1401 accepted-with-nonzero-diagnostics | identical |
| `hook.py` — containment and extraction | — | **18/18** |
| Owning tests, run by the reviewer | — | **195 passed**, exit 0 |

**The fix is numerically inert, established by execution.** `oldnew.py` extracted
the pre-fix module from `ebd85b88` and ran it against the fixed module over the
same 196-pair matrix: **0 numerical or accept/refuse differences, 6
warnings-only differences.** This was deliberately not settled by reading the
diff — reading the diff is how the original defect was missed.

**Hook containment.** With a caller's sentinel `showwarning` installed,
`warnings.showwarning` and `warnings.filters` are restored after a normal fit,
an in-block refusal, a `RuntimeError` propagating from `_diagnostics`, and an
`EstimatorSourceMismatch` from the source guard. Zero estimator warnings reach
the caller's hook. Nesting keeps inner and outer collectors separate.
Extraction matches the candidate for bare-string, instance and cross-category
warnings.

**`allowlisted_library_exception` is now covered by execution**, not inspection —
the reviewer patched `lmom_fit` to emit a warning and then invoke the real
`distr.gev._lmom_fit([0,0,0])`, confirming the refusal, line 1307 and the
retained warning.

## Mutants — what the controls actually discriminate

Rebuilt from the fixed source. This is the most useful thing the review
produced, and it is recorded because it bounds what the retained suite proves.

| Mutant | Retained numerical controls | Bit-parity vs frozen candidate |
|---|---|---|
| M1 quantile sign flip | **FAIL** (`SciPy mapping/sign control failed`) | FAIL |
| M5 `_quantile` × (1+1e-9) | **FAIL** (same control) | FAIL |
| M2 omitted scale map | blind | **FAIL** |
| M3 omitted loc offset | blind | **FAIL** |
| M6 physical back-map × (1+1e-9) in `fit_case` | blind | **FAIL** |
| M4 accepts c ≤ −1 | caught by the explicit-parameter-refusal control | — |

**M6 is the load-bearing case**: it changes the published metric value while
still returning `accepted`. `numerical_controls()` never calls `fit_case`, so it
is structurally blind to M2, M3 and M6 — only bit-parity against the frozen
candidate catches them. The retained controls gate the arithmetic kernel; they
do not gate the adapter's assembly of it.

Population-gate precedence is preserved: the retargeted mutant raises
`original population gate failed` before the characterization reference is
reached.

## The reviewer's corrections to its own round-1 evidence

Recorded rather than dropped, because an evidence file that cites a flawed probe
is exactly what a later reviewer should catch.

1. **`asym.py`'s `invalid_range` row was a flawed probe in both rounds.** It used
   a constant sample and injected the warning into `lmom_ratios`, which an
   `invalid_range` refusal never reaches, so it printed empty warnings before
   *and* after the fix and was never evidence either way. The asymmetry was real
   and the fix does address it, but the supporting evidence is `parity.py`'s six
   divergences plus the construction-site reading, now superseded by `hook.py`
   rows driven from a warning source genuinely upstream of each outcome.
2. **M4's pre-fix bit-parity failure was spurious** — it was the F1 warnings
   divergence, masking that the sample matrix never reaches `c ≤ -1`. Post-fix
   M4 is bit-identical, so it is now cleanly attributable to the retained
   explicit-parameter-refusal control alone. The fix removed a false catch and
   made the stated coverage boundary honest.

## Adversarial questions

**Is the frozen candidate a circular oracle?** Two separable tiers, neither
circular for its own claim. Production-vs-candidate is the right oracle for
"reproduces the assessed frozen candidate", because the candidate is literally
what the 8x qualification ran; it would be circular as evidence of numerical
*correctness*. Correctness rests on the independent tier — `reference_oracle.py`'s
high-precision Decimal population moments and CDF enclosures, and the 19 branch
plus 44 quantile bit-pattern references — which derive from neither
implementation and which production reproduced exactly.

**Two estimators on two paths.** Defensible under D2 and D8, and the
mixed-vintage risk is lower than the original record implied because the
predecessor helper is unreachable from any current run. Residual and uncovered
by tests: a detached four-column CSV remains estimator-ambiguous across
vintages — correctly carried as a disclosure mitigation, not a technical one.

**Does `ReturnLevelEvidence.parameters` change meaning?** Not inside the
repository: no in-repo code reads them semantically. D3 fixes the order
`(c, loc, scale)` and production complies. They do reach out-of-repo readers
through the published manifest.

**Refusal versus fault distinguishable only by message text?** No — distinct
types with distinct structure. No `except Exception` conversion survives in the
reduce path.

**Can a warning, diagnostic count or rounding artifact change an accepted
value?** No. `accepted` is computed before the diagnostics stage and never
re-read; the veto mutant left the estimate bit-identical; 1401 of 4000 accepted
fits carried nonzero counts without vetoing; and the warning mechanism itself is
now demonstrated inert.

## Non-blocking observation, carried to Stage 4

The sign convention for the published physical parameters — `c` is SciPy's, with
ξ = −c — is stated in the design and the adapter docstring but nowhere a
metric-manifest reader would see it. Worth one line of manifest documentation.
It blocks nothing here.

## What this verdict does not establish

- **Linux parity.** Not attempted, per the owner's deferral. Outstanding, not
  failed, and required before D8 handoff 2/4 cross-platform acceptance.
- **Numerical adequacy on real retained responses.** No fit ran against
  production responses; that is Stage 3's comparison.
- **Actual-bundle applicability.** Unchanged and unestablished; the 8x evidence
  remains a post-results development rescore under a relaxed retained-data
  policy, correctly declared `operational_screen_only` / `unvalidated` /
  `unestablished`.

Throughout both rounds the reviewer ran no `pixi run`, installed or modified no
environment, executed no Wflow, Julia, generation or metrics run, wrote to no
frozen evidence or snapshot, and committed nothing. Mutants were scratch copies;
`git status --porcelain` was empty at the end of each round.
