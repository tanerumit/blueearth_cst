# Stage 3 metrics-comparison verdict — GF15 production integration

Reviewer: independent `model-validator`, dispatched by the driver, blind to the
implementing conversation. One round at `be857f47` (since rewritten — see
finding 1). This is the gating artifact for Stage 4 under D8.

## Verdict

**REJECTED — narrowly, and not against the run.**

The comparison itself passes and was re-derived independently, more strongly
than the executor had claimed. What failed is the third acceptance criterion:
*documented* estimator differences. The remedy was a record correction and a
disclosure, **not a re-run**, and the reviewer said so explicitly: "The
comparison itself stands and does not need re-running."

Two of the three criteria were met and independently re-derived:

- **Complete comparison** — 756 of 756, zero unevaluated, and zero surplus rows
  in either direction.
- **Preserved extraction** — verified far past the three fields the executor
  checked (below).

## Findings

### 1 — MAJOR. Live credentials in tracked evidence

`stage-3/run-environment.json` dumped the entire ambient environment, including
a Zotero API key (read and write) and a Claude Code messaging token.

This was the executor's defect: the run script serialized `Get-ChildItem Env:`
wholesale into evidence that was then committed.

**Remediated the same day, before any push.** The dump is removed, the generator
can no longer produce one, and commits `fdce5812`/`be857f47` were replaced by
`4745a8b3`. Verified: the branch has no remote counterpart, `git branch -r
--contains` was empty, the values appear in no other tracked file, and a scan of
all reachable history finds them absent. The old objects survive locally as
unreachable until garbage collection.

**The key rotation is the owner's action and is not discharged by this
remediation** — the credential was live in the working environment regardless of
Git.

What the file retains is what the run's claims actually rest on: the complete
`PATH`, the resolution of every model-toolchain executable under it, and the
exact invocation. The environment dump carried no evidentiary weight.

### 2 — MAJOR. The record's causal account was contradicted by its own data

The record attributed the 331% and 274% low-flow moves to near-zero magnitude and
rested the disposition on `relative_error_near_zero: "unvalidated"`.

Re-derived from `comparison.json` and confirmed:

| Predictor of \|relative change\|, 35 low-flow keys | Spearman ρ | p |
|---|---|---|
| \|old MLE shape `c`\| | **+0.754** | 1.7e-07 |
| log₁₀(old magnitude) | +0.274 | 0.11 (n.s.) |

The six smallest-magnitude keys move by +0.06%, +0.93%, +1.37%, +15.06%, +29.78%
and +32.56% — no ordering by size at all. The three largest movers carried old
MLE shapes `c` = −2.295, −2.320, −2.320, i.e. ξ ≈ +2.3: Fréchet fits with
infinite mean and variance, which the new estimator refuses outright. Five old
fits have `c ≤ −1`; the old range is [−2.320, +1.073] against the new
[−0.909, +0.575].

The reviewer's sharper point, which the record had missed entirely: these are
**p = 0.5 quantiles**, so a 3x move is the median of the fitted distribution
moving, not a tail extrapolation. At those keys the *old* values came from
degenerate fits, and the change is an improvement there.

Corrected in `stage-3-record.md` under "What actually drives the large changes".

### 3 — MAJOR. An undisclosed second qualification gap

The declaration's `tested_domain.shapes_c` is `[-0.2, 0.0, 0.2]`. Re-derived:

- `q_return_level_10yr_max` — all 35 fitted `c` in **[−0.069, +0.186]**, none
  outside the tested range. This *strengthens* the record's claim about the
  maximum on an axis it had never used.
- `q_return_level_2yr_7day_min` — fitted `c` reaches **−0.909 and +0.575**, 7 of
  35 above |0.5|. At n = 18 the sampling spread of an L-moment shape estimate is
  ~0.15–0.2, so these are three or more standard deviations from |ξ| ≤ 0.2.

No mechanism flags this: the declaration has no shape-coverage field, and
`_covered_probability` bounds only the requested probability. The low-flow
statistic publishes `status: ready` while a substantial share of its fits sit
outside the assessed shape domain — a gap **distinct from** the near-zero
caveat. Now disclosed in the record; whether the declaration gains a
shape-coverage field or the reducer a shape guard is an owner question.

### 4 — MEDIUM. Two live return-level implementations, now quantified

`export_wflow_results._return_level_from_blocks` still fits xclim/SciPy MLE. The
reviewer's numbers change the weighting: the two paths can differ by **3x** on
the same statistic at the same location, making this a correctness risk rather
than a tidy-up. It remains unreachable from any current run and pinned by test.
Carried to Stage 4.

### 5 — MEDIUM. `return_level_benchmark.json` is an undeclared rule output

Verified in source: `simulate_system.smk`'s `publish_metric_set` declares
`manifest`, `units`, `environment` and the token `tables`; `metric_plan.py`
writes the report payload as an additional file. Snakemake neither tracks nor
cleans it, so a `--forcerun` or partial clean can leave a manifest whose
`return_level_benchmark.sha256` binds a missing file. Carried to Stage 4.

### 6 — LOW. "Exactly equal" overstated the guarantee

`metric_plan` publishes `_format_value(np.float32(value))` — four significant
digits of a float32. String identity is equality at four significant digits, not
bit-equal float64, so the record's "bit-identical … strongest available
statement" was wrong about *why* it is strong. The real guarantee is code-path
separation: `gev_lmoments.fit_case` is called from exactly one site,
`metric_registry.py:512`, and `reduce_run` never reaches it. Corrected.

### 7 — LOW. Toolchain table asserted marginally more than its evidence

`"R": ""` where the file's own note reserves *null* for unreachable. Normalized
and corrected; nothing turns on it, as `Rscript` was already null and no R rule
appears in the DAG.

## What the reviewer re-derived independently

Recorded because it is the part that makes the rejection safe to act on — the
run does not need repeating.

- Tree hashes of all three trees: snapshot ≡ retained project across 446 files;
  working = snapshot + **exactly 8 added, 0 modified, 0 removed**.
- **mtimes**: all 446 pre-existing files carry the 08:29 copy stamp; nothing was
  rewritten in the 08:34:48–08:35:53 run window. The executor's check had not
  covered this.
- An independent comparator with keys enumerated before comparison: 756/756 both
  sides, identical key sets, zero published-not-declared and zero
  declared-not-published either way, 686 equal, 70 changed, zero unevaluated.
- **Extraction, properly.** Every member sample was rebuilt from the snapshot's
  `run_*.csv` through the reducer's own recipe. All 70 reproduce `member_counts`,
  `total` **and `fit.input.sample_sha256`** exactly — real proof the samples did
  not change, which the executor's three-field check could not have shown.
- **Arithmetic on all 70, not a spot-check.** `fit_case` on the reconstructed
  samples reproduces the published physical parameters at `atol=0, rtol=0`, and
  all 70 published values byte-for-byte after formatting.
- The old manifest's MLE parameters are recoverable from those same samples to
  ~1e-5, which is what establishes the old values came from MLE on identical data.
- Every headline statistic in the record reproduced exactly.
- `prospective-plan.json` is semantically identical to the written `plan.json` —
  same `metric_set_id`, same `plan_sha256`, all 756 keys. The prediction claim is
  fully verified.
- D6 reader accepts the legacy set, the new set and the gwr-only set.

**On "no model ran".** The reviewer judged the PATH argument the *weakest* leg —
it is not proof against an absolute invocation — but found the claim airtight on
three better ones the record had underplayed: the DAG contains exactly three
rules and no Wflow or generation rule; no config embeds an absolute toolchain
path; and every native response and collection file is byte- **and**
mtime-unchanged through the run window.

**Taken on trust:** that no other process touched the trees between the two
hashings; the Stage 2 E7 Windows verdict; `lmoments3` source digests beyond the
module's self-check.

## The reviewer's scientific position

Reproduced because it is more useful than the verdict line.

The 10-year maximum **is fit for its declared purpose** under this change:
shapes inside the tested domain, at a tested count, moving ≤ 3.73%. The median
shape shift (+0.081 for the maximum, +0.215 for the low flow) is the expected
direction and magnitude for MLE → L-moments at n = 18, where MLE's shape
estimator is badly biased. No sign-error or normalization-error signature.

For the low flow, the right consumer posture is neither "tolerate the 3x move"
nor "distrust the new estimator", but that **at those keys neither number is
usable** — the old one degenerate, the new one outside the assessed shapes. A
low-flow return level with fitted ξ of 0.6–0.9 from 18 values carries
essentially no information, and should be read as a screening flag rather than a
magnitude. That is what `application_scope: operational_screen_only` already
says; the shape gap reinforces it on a second axis.

**Does this block the estimator change?** The reviewer's answer: no. "The change
improves the worst cases and leaves the qualified statistic essentially intact.
What blocks is the record, not the science."

## The reviewer's corrections to its own evidence

Recorded rather than dropped, per the convention set in the E7 review.

1. A first pass recomputed the old MLE with a bare `scipy.stats.genextreme.fit`,
   matching the manifest parameters only to ~1e-5 and 37 of 70 published values.
   That is optimizer-tolerance divergence from xclim's call, **not** drift. The
   1e-5 parameter agreement is the load-bearing result.
2. The reviewer's relative-change figures (3.755% / 330.98%) compared recomputed
   float64 values against *rounded* published ones. Recomputing
   published-to-published reproduces the record's 3.729% / 330.99% exactly. The
   record's numbers were correct; the reviewer's pairing was looser.

## What this verdict does not establish

- **Linux parity.** Outstanding and unclaimed, per the owner's 2026-09-14
  deferral. Correctly not counted against Stage 3.
- **Actual-bundle applicability.** Unchanged.
- **That any low-flow return level is accurate**, in either the near-zero or the
  outside-shape regime.
- **The standing baseline**, the milestone seal, or the §7.5 owner method ruling.
- **Non-return-level metrics** beyond four-significant-digit published equality
  plus code-path separation.

The reviewer wrote to no frozen evidence or snapshot, ran no Wflow, Julia,
generation or metrics run, and committed nothing; its worktree was clean at the
end.
