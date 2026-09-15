# GF15 production Stage 3 — metrics comparison record

Date: 2026-09-15. Session `session-3`, branch `feat/wp3-improvements`, worktree
`C:/Users/taner/workspace/.worktrees/blueearth_cst/session-3`. Authority: the
[Stage 3 brief](../../gf15-production-stage-3.md), accepted design D1–D8, the
[Stage 2 record](stage-2-record.md) and the [E7 parity
verdict](e7-parity-verdict.md) (ACCEPTED, Windows) at `5cd2d8ce`.

**The comparison completed. It did not abort, and no key went unevaluated.**
Independent acceptance has not yet been given; this record is the executor's
account, not a verdict.

## Result in one table

| Claim | Outcome |
|---|---|
| Keys declared and compared | **756 of 756**, zero unevaluated |
| Non-return-level rows exactly equal | **686 of 686** |
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
all of it in `run-environment.json`. `PATH` was reduced to four Windows system
directories; `JULIA_PROJECT`, `JULIA_DEPOT_PATH`, `JULIAUP_HOME`, `R_HOME`,
`PIXI_IN_SHELL` and `CONDA_PREFIX` were removed.

This is the negative proof the brief asks for, not merely a restriction:

| Executable | Resolution under the run's PATH |
|---|---|
| `julia`, `juliaup` | unreachable |
| `wflow_cli` | unreachable |
| `R`, `Rscript` | unreachable |
| `pixi`, `snakemake`, `python` | unreachable |

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

Every non-return-level published value is string-identical between the sets. The
`gwr_indicators.csv` table is **bit-identical** to the old one
(`cea695df0af5af01f962e02582786547879baa6777d360a29ec5b4c9c5947472`), which is
the strongest available statement that the estimator change did not leak.

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

### The large relative changes are the declared-unvalidated regime

The five largest relative changes are all `q_return_level_2yr_7day_min` at
near-zero magnitudes — the largest, 331%, is `1.823e-04 → 7.857e-04`. In
absolute terms that is 5.9e-04 m³/s on a low-flow statistic.

This is **not a surprise and not a new finding**: the D4 declaration shipped with
this estimator states `relative_error_near_zero: "unvalidated"` and
`zero_relative: "undefined; null, never epsilon-divided"`. The comparison
lands exactly inside the regime the qualification already declares it does not
cover. Recorded here as the executor's read, for the reviewer to judge: the
10-year maximum — the statistic in the qualified regime — moves by at most 3.73%,
while the 7-day minimum near zero is where the change is large and where the
declaration says nothing is claimed.

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

- **Independent acceptance.** No model-validator verdict exists for Stage 3 yet.
  The executor does not self-approve a scientific comparison.
- **Linux.** Nothing was installed or executed on linux-64. D8 handoff 2/4
  cross-platform acceptance remains open by owner deferral of 2026-09-14.
- **Actual-bundle applicability.** Unchanged and unestablished. The 8x evidence
  is still a post-results development rescore under a relaxed retained-data
  policy.
- **Near-zero low-flow accuracy.** The comparison *locates* the large changes in
  the declared-unvalidated regime; it does not validate that regime, and nothing
  here should be read as doing so.
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

## Handoff

Dispatch the independent model-validator for the Stage 3 verdict: completeness
of the comparison, preservation of extraction, and whether the documented
estimator differences — in particular the near-zero low-flow behaviour — are
acceptable. Stage 4 then reconciles the validation map, documents the SciPy sign
convention (ξ = −c) where a manifest reader would see it, and settles whether
the legacy export helper should follow the estimator.
