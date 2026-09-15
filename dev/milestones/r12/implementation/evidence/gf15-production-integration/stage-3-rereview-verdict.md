# Stage 3 re-review verdict — GF15 production integration, round 2

Reviewer: independent `model-validator`, blind to the implementing conversation,
dispatched at `f07c6e67` after the artifact changed. Round 1 is
[stage-3-verdict.md](stage-3-verdict.md).

## Verdict

**REJECTED — narrowly, and again against the record and the evidence bundle
rather than the run or the science.** No re-execution required.

What it **releases**: the estimator change itself, numerically settled on this
basin; the `shape_coverage` implementation as code; Stage 4's software gates,
the `.smk` output declaration (proved identity-free by execution), the
validation-map corrections and the frozenset fix; and Stage 4's decision to
withhold bounded Windows acceptance, which it called correct and *vindicated*.

What it **withholds**: acceptance of Stage 3 as recorded, plus everything round 1
withheld — Linux parity (outstanding by owner deferral, **not** counted against
Stage 3), actual-bundle applicability, low-flow accuracy, the §7.5 ruling, the
seal and the baseline.

The central executor claim was **confirmed, and more strongly than it was
asserted**: the reviewer reconstructed the reviewed revision `782941c1` and HEAD
as two separate package trees, ran both as separate processes through
`reduce_bundle`'s own recipe on the frozen inputs, and found 70 of 70 float64
return levels bit-identical and 70 of 70 evidence blocks equal apart from the
new field.

## Findings and their discharge

### MAJOR-A — the tracked evidence described the deleted artifact. **Fixed.**

The 10:30 re-run wrote its log to `metrics-run.log`, which `.gitignore:62:*.log`
swallows, so the tracked `metrics-run.txt` was still the 08:35 run — naming plan
`6ed13c05…` and the deleted set `7a0c4052…`. Verified and replaced with the real
log.

**This is the same defect twice.** The first Stage 3 commit lost its log the same
way. Renaming the file once fixed the symptom; the run script still wrote `.log`.
The generator now writes `.txt` directly, which is the actual fix.

The record's run window and its "8 added files" are corrected to the 10:30 run
and the true **9** added files, including **two** invocation records.

### MAJOR-B — the re-run reverted the LOW-2 remediation. **Fixed, with one part of the finding rejected.**

Confirmed and mine: the B+A commit overwrote the hand-corrected capture, so
`"R": ""` returned — the exact defect round 1's finding 7 raised — and the
provenance note was lost. Root cause: I corrected the stored *file* and never the
*script*, and `Get-Command R` returns an entry whose `Source` is empty, which
`if ($found)` treats as found. The script now tests the Source rather than the
entry, and emits the cleared/set variable lists so the note is regenerated rather
than hand-written.

**Rejected on the evidence:** the reviewer also concluded "there is no
environment capture for the run that produced the published artifact". There is.
`recorded_at_utc` is `2026-09-15T08:29:53Z` and the local offset is **+02:00**,
so that capture is `10:29:53` local — thirty seconds before the 10:30:23 run it
belongs to. The pairing is checkable in the committed history: round 1's capture
reads `06:34:10Z` against a log starting `08:34:57` local, the same offset. No
disclosure of a missing capture is needed, because none is missing.

### MAJOR-C — the three-sigma claim was wrong, and had reached shipped docs. **Fixed.**

Independently re-derived by Monte Carlo against the **shipped estimator**, 1200
draws per cell at n = 18, and the reviewer's numbers reproduce:

| True `c` | SD of fitted `c` | P(fitted lands outside [−0.2, +0.2]) |
|---|---|---|
| −0.2 | 0.214 | 0.494 |
| 0.0 | 0.194 | 0.302 |
| +0.2 | 0.192 | 0.492 |

So the sampling spread is ≈ 0.20, not the 0.15–0.2 quoted, and
`within_tested_range` has a **30–49 % false-outside rate by construction**. Of
the seven keys above |0.5|, only **four distinct fits** — all negative-`c`,
worst-case p ≤ 0.0083 — are inconsistent with the tested domain. The `+0.575`
pair sits at **p ≈ 0.036**, ordinary noise and the expected count over ~28
distinct fits.

This error ran in the executor's own favour: it made the disclosure sound
stronger, which is why it survived a first reading and why it is corrected in all
four places it reached, `docs/guide/outputs.qmd` included.

### MEDIUM-D — pseudo-replication, missed by two rounds of review. **Disclosed and boarded.**

Locations `101` and `1010` are the **same series**. Verified: identical
`fit.input.sample_sha256` in all 14 bundle/unit groups, identical published
values in all 140 of their `(metric, unit)` combinations — 140 of the 700 q rows
are exact copies — and **56 distinct samples behind 70 keys**.

Every headcount in this workstream was inflated by it. Corrected: **28 distinct
fits per statistic**, not 35; **16 distinct low-flow fits outside** the tested
range, not 21 keys; **5 distinct** above |0.5|, not 7; effective locations **4,
not 5**. No conclusion reverses — `q_return_level_10yr_max` still has zero fits
outside the tested domain — but its evidence base is narrower than the counts
implied, and the Spearman p-values treat duplicated rows as independent.

A basin-configuration property rather than a GF15 one, so boarded as
`t2609151118` rather than fixed inside an acceptance stage.

### MEDIUM-E — the pin did not test what it pinned. **Fixed, and the fix is mutation-tested.**

`test_shape_coverage_never_refuses_a_fit` called the helper directly and never
reached `reduce_bundle`, so the regression it exists to prevent — a guard added
at the call site — would have left it green.

Replaced with `test_reduce_bundle_publishes_an_out_of_domain_shape`, which
narrows the declared domain to a point and asserts the bundle still publishes.
**Verified by injecting the exact mutant**: a
`raise InvalidReturnLevelFit` on `within_tested_range is False` at
`metric_registry.py:579`. The new test fails on it; the old helper-only test
passes, confirming the reviewer's point precisely.

### LOW-F — two slips in the Stage 4 verdict. **Fixed.**

"3,813 tests" added `test-fast`'s passes to the contract tier's selections; the
logs give 3,728 deselected + 101 selected = **3,829** collected. And the
frozenset defect was called "pre-existing": true of GF15, false of `main` —
`868c4b7c` is branch-local, 31 commits back, so **this branch introduced it**,
and the honest framing is that the pre-push rung went unexercised here for 31
commits.

### LOW-G — the manual deletion was unrecorded. **Fixed.**

`immutability-check.json` computes `removed` against the snapshot and so is
structurally blind to a post-snapshot file, which is why the hand-deletion of
`7a0c4052…` and its plan appeared nowhere. Now recorded in the record, with that
blindness stated.

### LOW-H — `within_tested_range` is hull membership. **Documented.**

`min`/`max` over three discrete points means a fitted `−0.1` reports `true`
though `−0.1` was never generated. The docs now say so and point at
`tested_shapes_c`.

## The reviewer's judgement, reproduced

On the mechanism: option D correctly rejected; `None` correctly means
"unavailable" rather than "covered", confirmed against the legacy set;
`excess_beyond_tested_range` computed correctly; no caller can gate on it today.

On the interpretation, which it called the weak part: recording the distance
beats a bare boolean, but the distance is comparable to the estimator's own noise
across most of its range, so a consumer adopting "excess < 0.1 is fine" would be
reading almost nothing. The docs now carry the false-outside rate and the ≈ 0.6
threshold.

One latent fragility, noted not changed: `tested_domain.shapes_c` is symmetric
about zero, so a `c`-versus-ξ convention mismatch would be **undetectable today**
and would invert silently the moment the domain becomes asymmetric — i.e. under
option F.

## Reviewer's corrections to its own evidence

1. Its first probe built both revision trees with `git archive`, whose CRLF
   conversion made **both** fail a reader digest — tooling, not a defect;
   rebuilt by direct copy.
2. Monte Carlo draws were reduced to fit a timeout; at 400 draws p = 0.035 has
   SE ≈ 0.009, far from what a three-sigma claim needs, so MAJOR-C is robust to
   the reduction. My independent 1200-draw run confirms it.
3. It looked for the generator behind `run-environment.json` and found none
   tracked — correct: it is a session script under `.tmp`, which is why the
   stored file was the only thing round 1's fix could reach, and why the script
   fix now matters.

## What this verdict does not establish

Linux parity; actual-bundle applicability; that any low-flow return level is
accurate in either the near-zero or the outside-shape regime; the §7.5 ruling;
the standing baseline or the seal. A third pass has not yet seen these
corrections.

The reviewer wrote nothing outside its scratch, ran no Wflow, Julia, generation
or metrics run, committed nothing, and left the worktree clean.
