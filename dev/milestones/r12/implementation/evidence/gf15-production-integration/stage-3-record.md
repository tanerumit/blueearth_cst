# GF15 production Stage 3 — metrics comparison record

Date: 2026-09-15. Session `session-3`, branch `feat/wp3-improvements`, worktree
`C:/Users/taner/workspace/.worktrees/blueearth_cst/session-3`. Authority: the
[Stage 3 brief](../../gf15-production-stage-3.md), accepted design D1–D8, the
[Stage 2 record](stage-2-record.md) and the [E7 parity
verdict](e7-parity-verdict.md) (ACCEPTED, Windows) at `5cd2d8ce`.

**The comparison completed. It did not abort, and no key went unevaluated.**

The independent model-validator **REJECTED** this stage on 2026-09-15 and the
findings are recorded in [stage-3-verdict.md](stage-3-verdict.md). The rejection
is narrow: the reviewer re-derived the comparison independently — including
rebuilding every member sample and reproducing all 70 published values — and it
stands. What failed was this record's *explanation* of the results, plus a
credential that should never have been written to tracked evidence. Both are
corrected in place below, marked and dated, rather than silently replaced.

## Result in one table

| Claim | Outcome |
|---|---|
| Keys declared and compared | **756 of 756**, zero unevaluated |
| Non-return-level rows exactly equal | **686 of 686** (four significant digits; the estimator is structurally unreachable from them) |
| Return levels compared with float64 evidence | **70 of 70** |
| Member extraction and coverage preserved | **70 of 70** (`member_counts`, `required`, `total` identical) |
| Upstream bytes, requests and inventories fixed | **yes** — zero changed, added or removed |
| New identity predicted before the run | **yes** — dry probe and written plan agree |
| Frozen snapshot untouched | **yes** — 446 files, byte-identical to the retained project |
| Model / generation step ran | **no** |

## What was pinned before anything ran

The advisor's framing for this stage was that a comparison whose denominator is
ambiguous is unfalsifiable. Three things were therefore fixed first, in
`prerun-capture.json`.

**The baseline set.** Two retained sets exist. `49ca0158…` is the complete
`{q, gwr}` set for the frozen simulation `3a8c1fc6…`: 756 declared keys over
eleven q metrics and one gwr metric, both indicator tables present, status
`ready`, and the set Stage 1 inventoried. `d354a347…` is a **gwr-only** set —
56 keys, the single metric `gwr_annual_total`, no q table and **no
return-level evidence at all** — so it cannot be a baseline for this
comparison. It is named here and excluded on the record.

> A first draft justified the selection by calling `49ca0158…` "the only set
> the retained metrics-reuse invocation produced". That is false and is
> corrected in the evidence file: `p3-operations-dedicated-reuse/metrics-reuse.log`
> records `Nothing to be done (all requested files are present and up to date)`,
> so that invocation produced no set and **both** retained sets predate it. The
> selection rests on checkable set content instead.

**The collection anchor (`t2609140745`).** The retained
`experiments/p3_final/config/simulation.json` embeds exactly one absolute path,
`collection.manifest_path`, and it points into disposable `.tmp` scratch. That
record is immutable and was **not** rewritten. Instead the exposure was
insured: the 25-file, 67,547,392-byte collection subtree under `.tmp` was hashed
against the same subtree inside the frozen snapshot and found **byte-identical**,
so the snapshot can restore that exact path if scratch is swept. Had they
differed, this would have been a Stage 3 blocker to report, not to work around.

**The upstream bytes.** The collection, native responses, response inventory,
experiment config and the baseline set were hashed file-by-file into
`upstream-before.json` *before* the run — content, not a directory listing.

## The run

The working copy was created at
`…/working/p3-final-direct/` from the frozen snapshot. The snapshot itself was
never a write target.

Before launching, the dry probe `materialize_probe.py` composed the config,
observed the live metric environment and built the full plan **without writing
anything**, to answer where the new set would land:

| | |
|---|---|
| Predicted `metric_set_id` | `7a0c4052601bb68d6fe45cc9c404942ea34f1e7acb2709b14a1efea9c6a800c2` |
| Written `metric_set_id` | the same, confirmed from `plan.json` after the run |
| Destination under the working copy | yes |
| Collides with either existing set | no |
| Already exists | no |
| Declared keys | 756, equal to the baseline |

The plan is retained as `prospective-plan.json`, which is what makes "predicted
before the run" checkable rather than asserted.

### Ambient environment, set rather than inherited

The retained run captured no environment block, so its variables are **unknown,
not matched**. Stage 3 therefore set the environment deliberately and recorded
it in `run-environment.json`.

> **Redacted 2026-09-15, before any push.** The first version of that file dumped
> *every* ambient environment variable, which included live API credentials. The
> independent reviewer caught it. The dump is removed, the generator can no
> longer produce one, and the commit was rewritten — the values never left this
> machine and the branch has never been pushed. What the run's claims rest on is
> retained: the complete `PATH`, the resolution of each model-toolchain
> executable under it, and the exact invocation. `PATH` was reduced to four Windows system
directories; `JULIA_PROJECT`, `JULIA_DEPOT_PATH`, `JULIAUP_HOME`, `R_HOME`,
`PIXI_IN_SHELL` and `CONDA_PREFIX` were removed.

This is the negative proof the brief asks for, not merely a restriction:

| Executable | Resolution under the run's PATH |
|---|---|
| `julia`, `juliaup` | unreachable |
| `wflow_cli` | unreachable |
| `R`, `Rscript` | unreachable |
| `pixi`, `snakemake`, `python` | unreachable |

> **Corrected 2026-09-15.** The recorded `toolchain_resolution` originally
> carried `"R": ""` — an empty string — while the same file's note says a *null*
> entry means unreachable. The table above was therefore asserting marginally
> more than the evidence showed. The generator now normalizes every falsy
> resolution to null, and the stored file was corrected. Nothing turns on it:
> `Rscript` was already null, and no R rule appears in the executed DAG.

The interpreter is named absolutely and Snakemake is invoked as `-m snakemake`,
so neither needs `PATH`. Any model or generation step that tried to run would
have failed loudly rather than succeeding quietly.

```powershell
& "…/windows-environment-pypi/.pixi/envs/default/python.exe" `
  "…/session-3/scripts/simulate_system.py" `
  --config "…/materialized/project_config_gf15_metrics.yml" `
  --cores 3 --target metrics
```

Exit 0, three of three steps, 08:34:48 → 08:35:53. `.snakemake/locks` was
verified empty immediately before launch and no test suite ran in this worktree
during the run — the scheduling constraint carried out of the Stage 2 stall.

## Upstream was fixed, and the writes were confined

`immutability-check.json` re-hashed both trees after the run.

- The frozen snapshot is **byte-identical** to the retained `.tmp` project
  across all 446 files — nothing changed, nothing added, nothing removed.
- The working copy differs from the snapshot by exactly **8 added files and
  nothing modified or removed**: the new metric plan, the six files of the new
  metric set, and the runner's own invocation record.

That last file is an **operational log, recorded separately from the experiment
results** as the brief requires: `config/runs/invocations/simulation-50e3da6f….json`
is the runner's lifecycle record, not a metric artifact.

No native response, collection, simulation record or response inventory appears
under added or modified. This is the falsifier the brief names — a model
invocation or upstream hash drift — and it did not occur.

The two sets also agree on every shared identity input: `simulation_id`,
`collection_id`, `collection_revision`, `response_inventory`, `response_request`
and the declared key list are all equal. The comparison is therefore between
two estimators on one set of inputs, which is the only thing that makes the
differences attributable.

## The comparison

The comparator enumerates all 756 declared keys **before** comparing any of
them, so an abort could have named every key it failed to reach. It did not
abort; `unevaluated` is 0.

### Non-return-level rows — 686 of 686 exact

Every non-return-level published value is string-identical between the sets, and
`gwr_indicators.csv` is byte-identical to the old table
(`cea695df0af5af01f962e02582786547879baa6777d360a29ec5b4c9c5947472`).

**What that does and does not prove — corrected 2026-09-15.** An earlier version
called the byte-identical table "the strongest available statement that the
estimator change did not leak". It is not, and the claim overstated the
guarantee. `metric_plan` publishes `_format_value(np.float32(value))`: four
significant digits of a float32. String identity is therefore equality at four
significant digits, not bit-equal float64, and a sufficiently small change could
in principle hide under the rounding.

The strong statement comes from code-path separation instead, and it is checkable
in the source: `gev_lmoments.fit_case` is called from exactly one site,
`metric_registry.py:512`, inside the bundle reduction. Non-return-level metrics
are reduced by `reduce_run`, which never reaches it. The estimator cannot affect
them because it is never invoked for them — which is a structural guarantee
rather than a numerical observation.

Both tables keep the four-column shape and header `metric,location,unit_id,value`,
with unchanged row counts (700 q, 56 gwr).

### Return levels — 70 of 70 changed, as intended

All 70 return-level values moved. That is the point of the change, and **no
tolerance was applied or invented**; each is recorded with the float64
parameters from both manifests in `comparison.json`.

| Metric | n | Old value range | Rel. change min / median / max | Direction |
|---|---|---|---|---|
| `q_return_level_10yr_max` | 35 | 1.839 … 115.6 | 0.135% / 1.47% / **3.73%** | 27 higher, 8 lower |
| `q_return_level_2yr_7day_min` | 35 | 1.388e-05 … 0.01842 | 0.059% / 5.24% / **331.0%** | 24 higher, 11 lower |

Member extraction and coverage are preserved on every one: `member_counts`,
`required` and `total` are identical across all 70 keys. Every fit was
**accepted** — 70 of 70, with no refusal reason, no allowlisted exception, no
warning, and zero non-finite-density or outside-support diagnostics.

### What actually drives the large changes — corrected 2026-09-15

> **This section replaces a falsified one.** The first version of this record
> attributed the large moves to near-zero magnitude and rested the disposition on
> the D4 `relative_error_near_zero: "unvalidated"` caveat. The independent
> model-validator rejected that account, and re-deriving it from
> `comparison.json` confirms the rejection: **magnitude does not predict the
> moves.** The conclusion about the 10-year maximum survives; the reasoning
> behind the low-flow moves does not, and the original wording also omitted the
> finding that matters most. Both are corrected below.

Across the 35 low-flow keys, ranked correlation with the absolute relative
change:

| Predictor | Spearman ρ | p |
|---|---|---|
| \|old MLE shape `c`\| | **+0.754** | 1.7e-07 |
| log₁₀(old published magnitude) | +0.274 | 0.11 — not significant |

The six smallest-magnitude keys settle it directly. They span the whole range of
outcomes with no ordering by size:

| Key | Old magnitude | Move | Old MLE `c` |
|---|---|---|---|
| `1040` / `20` | 6.79e-05 | +0.06% | +0.075 |
| `1020` / `16` | 5.57e-05 | +0.93% | +0.210 |
| `1020` / `19` | 4.88e-05 | +1.37% | +0.285 |
| `1040` / `15` | 5.36e-05 | +15.06% | −1.498 |
| `1040` / `16` | 3.09e-05 | +29.78% | +1.073 |
| `1040` / `19` | 1.39e-05 | +32.56% | −0.523 |

**The driver is old-fit pathology.** The three largest movers carried old MLE
shapes `c` = −2.295, −2.320, −2.320 — SciPy's convention, so ξ ≈ **+2.3**: a
Fréchet fit with infinite mean and infinite variance. Five of the 70 old fits
have `c ≤ −1` and six have |`c`| > 1; the old range is [−2.320, +1.073]. The new
estimator refuses inverted `c ≤ −1` outright, and its fitted shapes across all 70
keys lie in [−0.909, +0.575].

These are also **p = 0.5 quantiles** — medians of the fitted distribution, not
tail draws. A 3x move at the median means the whole location/scale was distorted,
not that a tail was extrapolated differently.

So the honest statement is the opposite of the original one: at the
largest-moving keys the **old published values came from degenerate fits**, and
the change is an improvement there rather than an excursion into an untested
corner.

### A second, separate qualification gap — newly disclosed

The declaration's `tested_domain.shapes_c` is `[-0.2, 0.0, 0.2]`: the benchmark
measured accuracy only for data generated from those shapes, at counts
`[10, 18, 30, 60]` and probabilities `[0.9, 0.5]`. Every fit here uses 2 members
× 9 blocks = **18** usable values, a tested count, at a tested probability.

The two statistics part company on shape:

- **`q_return_level_10yr_max`** — all 35 fitted `c` lie in **[−0.069, +0.186]**,
  none outside [−0.2, 0.2]. That is comfortably consistent with a true shape
  inside the tested domain at a tested count, and it *strengthens* this record's
  claim that the 10-year maximum sits in the qualified regime, on an axis the
  original version never used.
- **`q_return_level_2yr_7day_min`** — fitted `c` reaches **−0.909 and +0.575**,
  with 7 of 35 above |0.5| in magnitude. At n = 18 the sampling spread of an
  L-moment shape estimate is roughly 0.15–0.2, so those sit three or more
  standard deviations from |ξ| ≤ 0.2 and are not plausibly draws from the
  generating domain the benchmark tested.

This is stated as an inference about the *generating* domain, not a headcount:
21 of 35 fitted `c` fall outside [−0.2, 0.2], but a fitted 0.28 at n = 18 is
consistent with a true 0.2, so the raw count alone would be rebuttable. The
three-sigma cases are not.

**Nothing in the code flags this.** The declaration carries no shape-coverage
field, and `metric_registry._covered_probability` bounds only the requested
*probability*, never the fitted shape. So `q_return_level_2yr_7day_min` publishes
with `status: ready` while a substantial share of its fits sit outside the shapes
the benchmark assessed. This is a qualification gap **distinct from** the
near-zero relative-error caveat, and it was absent from the first version of this
record. Whether the declaration should gain a shape-coverage field, or the
reducer a shape guard, is an open question for Stage 4 and the owner — not one
this record settles.

### What a consumer should take from this

In absolute terms the largest move is 1.823e-04 → 7.857e-04 m³/s, i.e. 0.18 →
0.79 L/s. As a flow that is physically negligible, and no in-repo consumer logs,
ratios or divides by a return level — the indicator tables are terminal
artifacts here — so the move does not propagate today.

But the useful conclusion is neither "it moved 3x, tolerate it" nor "it moved 3x,
distrust the new estimator". It is that **at those keys neither number is usable**:
the old one came from a degenerate fit, and the new one lies outside the shapes
the benchmark assessed. A low-flow return level whose fitted ξ is 0.6–0.9 from 18
values carries essentially no information. The right posture is to treat
`q_return_level_2yr_7day_min` as a screening flag rather than a magnitude —
which is what `application_scope: operational_screen_only` already says, and
which the shape gap now reinforces on a second, independent axis.

The 10-year maximum is a different matter and is fit for its declared purpose
under this change: shapes inside the tested domain, at a tested count, moving by
at most 3.73%. The median shape shift — +0.081 for the maximum, +0.215 for the
low flow — is the expected direction and size for MLE → L-moments at n = 18,
where the MLE shape estimator is badly biased and high-variance. Nothing in the
pattern carries a sign-error or normalization-error signature.

## The new set's identity and report

| Check | Outcome |
|---|---|
| `metric_set_id` matches its directory | yes |
| Status | `ready` |
| `return_level_benchmark.json` present in the payload | yes |
| Payload digest | `89905f1889a08177ff9225535a7a590b0081c76b2e6765e31e83390bee412b2c` |
| Matches the manifest's D5 reference | yes |
| Matches the shipped package asset byte for byte | yes |
| D6 reader dispatch (`read_metric_set`) on the produced artifact | accepted |
| Declaration | `gf15-accuracy-8x-v1`, `screening_policy_status: provisional_operational`, `benchmark_status: reviewed_bounded` |

The payload was checked against **both** the manifest reference and the package
asset, so a regenerated or drifted copy could not pass on self-consistency alone.

> An intermediate version of the comparator reported this row as failing. It was
> looking for the digest inside the D4 declaration; D5 puts it in the manifest's
> `return_level_benchmark` reference. The probe was wrong, not the artifact.
> Recorded because a corrected probe should be visible rather than quietly
> replaced.

## What this record does not establish

- **Independent acceptance.** The model-validator **REJECTED** this stage on
  2026-09-15. The rejection is narrow and does not touch the run: the comparison
  itself was re-derived independently and stands. See
  [stage-3-verdict.md](stage-3-verdict.md).
- **Linux.** Nothing was installed or executed on linux-64. D8 handoff 2/4
  cross-platform acceptance remains open by owner deferral of 2026-09-14.
- **Actual-bundle applicability.** Unchanged and unestablished. The 8x evidence
  is still a post-results development rescore under a relaxed retained-data
  policy.
- **Low-flow accuracy.** The comparison explains *why* the large changes
  happened — degenerate old fits — and discloses that many new low-flow fits sit
  outside the benchmark's tested shape domain. It validates neither regime, and
  nothing here should be read as doing so.
- **Whether the estimator should carry a shape guard.** The gap is disclosed, not
  resolved. That is an owner and Stage 4 question.
- **The standing baseline.** Not re-recorded, not refreshed, and not the check
  for this change.
- **An owner method ruling.** Design §7.5 still requires one after full
  qualification.

## Artifacts

Evidence, tracked, in `evidence/gf15-production-integration/stage-3/`:
`prerun-capture.json`, `upstream-before.json`, `materialization-probe.json`,
`prospective-plan.json`, `run-environment.json`, `metrics-run.txt`,
`comparison.json`, `immutability-check.json`.

Run outputs remain **outside Git**, under
`…/blueearth_cst-artifacts/r12/gf15-production-integration/working/p3-final-direct/`.
The frozen snapshot beside it stays immutable until independent acceptance.

## Open items this record hands to Stage 4

Two defects the reviewer found in code rather than in this record, neither of
which affects the comparison:

- **The legacy export path still fits xclim/SciPy MLE.**
  `export_wflow_results._return_level_from_blocks` is a second live return-level
  implementation. The reviewer's numbers change how this should be weighed: the
  two paths can differ by **3x** on the same statistic at the same location, so
  it is a correctness risk rather than a tidy-up. It remains unreachable from any
  current run and pinned by
  `test_legacy_export_helper_keeps_the_predecessor_estimator`.
- **`return_level_benchmark.json` is an undeclared rule output.**
  `publish_metric_set` declares the manifest, unit index, environment and the
  token tables; the report payload is written as a fifth file that Snakemake
  neither tracks nor cleans. A `--forcerun` or partial clean can therefore leave
  a manifest whose `return_level_benchmark.sha256` binds a file that is gone.

Stage 4 also reconciles the validation map, documents the SciPy sign convention
(ξ = −c) where a reader of the published parameters will meet it, and carries the
outstanding Linux parity and §7.5 owner ruling.
