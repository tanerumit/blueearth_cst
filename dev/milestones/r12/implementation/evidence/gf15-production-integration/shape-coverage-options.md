# Shape-domain coverage for `q_return_level_2yr_7day_min` — options for owner ruling

Date: 2026-09-15. Raised by the Stage 3 model-validator (finding 3,
[stage-3-verdict.md](stage-3-verdict.md)) and confirmed by re-derivation. This
memo asks for a ruling; it does not take one.

**The question.** The shipped benchmark assessed accuracy only for data generated
from shapes `c ∈ {-0.2, 0.0, 0.2}`. In production, `q_return_level_2yr_7day_min`
fits land well outside that. Should anything in the code or the declaration
change, and if so, what?

## What is actually at stake

Re-derived from `stage-3/comparison.json`, all 70 return-level fits, n = 18
(2 members × 9 blocks) at every key:

| | `q_return_level_10yr_max` | `q_return_level_2yr_7day_min` |
|---|---|---|
| Fitted `c` range | **[−0.069, +0.186]** | **[−0.909, +0.575]** |
| Keys outside [−0.2, +0.2] | **0 of 35** | **21 of 35** |
| Keys with \|`c`\| > 0.5 | 0 | 7 |

The maximum is entirely inside the tested domain. The low flow is not, and the
excursion is **not localized** — the 21 affected keys span **all five locations**
and **all seven bundle units**:

| Location | 101 | 1010 | 1020 | 1030 | 1040 |
|---|---|---|---|---|---|
| Keys outside | 5 | 5 | 4 | 4 | 3 |

The seven cases beyond \|`c`\| > 0.5, which are the ones that cannot be explained
as sampling noise around a tested shape:

| Location | Unit | `c` | ξ = −`c` | Published value |
|---|---|---|---|---|
| 1040 | 15 | −0.909 | +0.909 | 6.164e-05 |
| 1020 | 15 | −0.620 | +0.620 | 7.857e-04 |
| 101 | 15 | −0.607 | +0.607 | 1.734e-03 |
| 1010 | 15 | −0.607 | +0.607 | 1.734e-03 |
| 1020 | 20 | −0.602 | +0.602 | 1.973e-04 |
| 101 | 19 | +0.575 | −0.575 | 1.441e-04 |
| 1010 | 19 | +0.575 | −0.575 | 1.441e-04 |

At n = 18 the sampling spread of an L-moment shape estimate is roughly 0.15–0.2,
so a fitted 0.28 is consistent with a true 0.2 and the raw "21 of 35" count is
rebuttable. These seven, at three or more standard deviations, are not.

## Three structural facts that constrain the options

These are the reason the obvious answer is the wrong one. Each was verified in
source, not assumed.

**1. A refusal destroys the whole metric set, not one key.**
`InvalidReturnLevelFit` is raised at `metric_registry.py:514` and is **caught
nowhere** in the package. It propagates out of `reduce_bundle`, out of
`publish_metric_set`, and aborts the run. So a hard shape guard would not
"suppress the low-flow statistic" — on this basin it would take down the entire
metric set, including all 686 non-return-level rows and all 35 fully-qualified
10-year maxima. The first of 21 offending keys ends the run.

**2. Shape coverage is a post-condition; probability coverage is a
pre-condition.** The existing analogue, `_covered_probability`, is called
*before* `fit_case` and gates the **request**: a caller asking for an untested
return period is refused without the estimator ever running, which is why it can
refuse cleanly. A shape is not known until the fit exists. Any shape check is
therefore a judgement on a **result**, and one computed from a noisy statistic.
They are not the same kind of guard and should not be given the same mechanism
by analogy.

**3. Any of these changes `metric_set_id`; they differ in how much else they
touch.**

> **Corrected 2026-09-15, after implementing option B.** The first version of
> this fact claimed that adding a field to the **evidence** "changes manifest
> bytes only" and used that as the argument for B over C. **That was wrong**,
> and executing B falsified it: the prospective `metric_set_id` moved from
> `7a0c4052…` to `7572a9a1…`.
>
> The claim was right about the data structure and wrong about the change.
> `metric_set_id` hashes `metric_definition_sha256`, which does **not** cover
> `return_level_evidence` — so the *field* is indeed identity-free. But the
> definition also carries each declaration's `implementation_revision` and a
> `code_inventory`, both of which digest the reducer source. Editing
> `metric_registry.py` to *produce* the field therefore moves the identity, by
> design: the mechanism exists precisely so a changed implementation cannot
> publish under an unchanged id. I reasoned about the payload and forgot the
> code that writes it.

What survives, and what the comparison between the options actually rests on:

- **B** changes `metric_set_id` via the reducer's `implementation_revision`, and
  nothing else. One 65-second re-run produces a clean artifact.
- **C** changes `metric_set_id` *as well*, for the same reason plus the
  declaration itself, **and** touches the closed 16-field set
  (`DECLARATION_FIELDS`), `build_declaration`, the closure check and the shipped
  asset's verification path.

So B remains strictly cheaper than C — the conclusion holds, and holds more
firmly than the original argument for it, since the original argument gave B an
advantage it does not have. Any option here reopens Stage 3's artifact and its
independent acceptance; none of them avoids that.

## Options

### A — Disclosure only. No code, no declaration change.

The gap is already recorded in [stage-3-record.md](stage-3-record.md) and the
verdict. Add one paragraph to `docs/guide/outputs.qmd` telling a reader that the
tested shape domain is narrow and that a fitted shape far outside it means the
number is a screening flag, not a magnitude.

*For:* zero identity churn; Stage 3's artifact keeps describing the shipped
configuration; `application_scope: operational_screen_only` arguably already
covers it. *Against:* nothing machine-readable. A downstream consumer reading
`metrics.json` still cannot tell an in-domain fit from a three-sigma one, and
the disclosure lives only where a human happens to read prose.

### B — Record shape-domain coverage per fit, in the evidence. Non-gating.

Add a boolean (or the tested range plus the fitted value) to
`ReturnLevelEvidence` / the fit record, so every published fit says whether its
shape falls inside the assessed domain. Nothing refuses.

*For:* the cheapest real improvement — it moves `metric_set_id` only through
the reducer's own revision digest, touching no schema or asset machinery (fact
3, as corrected); makes the disclosure machine-readable at the exact granularity the
problem has — per location, per unit; a reader can filter. *Against:* Stage 3 must be
re-run (65 s) and re-reviewed; asserts a boundary in data without asserting what
to do about it.

### C — Add a shape-coverage statement to the declaration.

Extend the closed declaration with an explicit field naming the assessed shape
range and the fact that fits outside it are unassessed.

*For:* puts the boundary in the same closed, digest-verified object as the rest
of the qualification, where D4/D5 readers already look. *Against:* changes
`metric_set_id` for every set, touches the closed-schema machinery and the
shipped asset's verification, and reopens Stage 3 acceptance. Largely duplicates
what B achieves at far higher cost, unless the boundary belongs in the
*qualification* rather than in the *result* — which is a real argument, since
`tested_domain` already lives there.

### D — Hard shape guard: refuse out-of-domain fits.

*For:* the strictest reading of "do not publish outside what was assessed".
*Against:* **on this basin it makes the entire metric set unproducible** (fact
1), including the fully-qualified 10-year maximum and every non-return-level
metric. It also gates on a statistic with SD ≈ 0.15–0.2 at n = 18, so it would
refuse fits whose true shape is inside the domain, and accept fits whose true
shape is outside — a guard that is both destructive and unreliable. Not
recommended in any form without a redesign of refusal granularity.

### E — Publish, but mark the row as out-of-domain in the table.

A fifth column, or a sentinel, on the indicator CSV.

*For:* travels with the detached CSV, which is the one artifact that currently
loses all provenance. *Against:* breaks the four-column contract the Stage 3
brief explicitly verifies and that `docs/guide/outputs.qmd` documents as an
interchange surface; changes every consumer. Disproportionate.

### F — Extend the benchmark to cover the observed shape range.

Re-qualify the estimator over shapes spanning roughly [−0.9, +0.6] at n = 18.

*For:* **the only option that actually closes the gap.** Everything above
documents or gates the boundary; only this moves it. *Against:* a full
qualification run, and it is squarely a §7.5 owner method question rather than an
integration task. Note the honest framing: the existing 8x evidence is already a
post-results development rescore, so widening the domain compounds a
pre-existing limitation rather than resolving it.

## Recommendation

**B now, A alongside it, F as the standing method question. Not C, D or E.**

B is the only change that improves machine-readability without touching
`metric_set_id`, and it records the boundary at the granularity the problem
actually has. A costs a paragraph and reaches the human reader. Together they
make the gap visible to both audiences for the price of one 65-second re-run.

C is defensible on the argument that `tested_domain` already lives in the
declaration — if that argument wins, it should be done *instead of* B, not as
well, and accepted as a full identity change with Stage 3 re-run and re-reviewed.

D should be rejected as specified. If the owner wants gating, the prerequisite is
a redesign that makes a refusal suppress one key rather than the whole set — a
separate piece of work, not a flag.

F is where the scientific answer lives, and it belongs with the §7.5 ruling that
is already outstanding rather than being decided here.

## What none of these options do

- None makes any low-flow return level **accurate**. The largest-moving values
  came from degenerate MLE fits and their replacements sit outside the assessed
  shapes; at those keys neither number is usable, and a fitted ξ of 0.6–0.9 from
  18 values carries essentially no information.
- None affects `q_return_level_10yr_max`, which fits entirely inside the tested
  domain at a tested count and is fit for its declared screening purpose.
- None discharges the outstanding **Linux parity** (D8 handoff 2/4) or the
  **§7.5 owner method ruling**.
- None changes `actual_bundle_applicability`, still `unestablished`.
