---
title: Fold rules 1.08 and 1.09 back into 1.07 so WF1 reads and writes the model once, not three times
type: todo-item
status: backlog
effort: 2
area: wf1 / model build
queue:
created: 2026-09-04
updated: 2026-09-04
---

> [!note] Overview
> **What** — Rules 1.07, 1.08 and 1.09 each open the Wflow model from disk, mutate it, and call the full hydromt `Model.write()` — which flushes *every* component regardless of what the rule touched. One WF1 build therefore deserializes and re-serializes `staticmaps.nc`, `wflow_sbm.toml` and all eight `staticgeoms/*.geojson` three times over. Call sites: `blueearth_cst/model/build_wflow_model.py:551`, `setup_reservoirs_lakes_glaciers.py:125`, `setup_gauges_and_outputs.py:140`.
> **Why** — Merging is the direction rule 1.08 already declares for itself (`build_model.smk:687` — *"temporary hydromt fix; can fold back into build_wflow_model when supported"*), with R10-1 as precedent. **But the payoff is much smaller than it looked** — measured 2026-09-04, the redundant I/O is ~1.7 s per rule, not the ~12 s the run log suggested; three quarters of each rule's process is `import hydromt`, which is [[t2608202331]]'s scanner problem, not this one's. Do [[t2608202331]] first. See "Step 2 answered" below.
> **Effort** — Large, and the work is not the merge itself but the rebuild-trigger scaffolding it disturbs. **Resolved 2026-09-04:** the upstream condition 1.08 defers to does not govern this path at all — see "Step 1 answered" below. 1.08 is mergeable now against our own code; 1.09 is the harder half and is not a build-step merge.

## Where it came from

A question about a WF1 run log on 2026-09-04: why the `Writing geoms to …` block
appears three times. It is not a reporting glitch — the files really are written
three times, by three different rules.

## Measurement — contended, treat as an upper bound (SUPERSEDED by step 2 below)

From the run log, wall-clock between a rule's `RUN` banner and its first hydromt
message (i.e. model deserialization):

| rule | `RUN` | first work | gap |
|---|---|---|---|
| 1.08 `add_reservoirs_lakes_glaciers` | 16:59:50 | 17:00:02 | ~12 s |
| 1.09 `declare_wflow_outputs` | 17:00:05 | 17:00:13 | ~8 s |

The write side is ~1 s per block by the same timestamps. `staticmaps.nc` is 204 K
in both `test_case/test_rapid` and `test_case/test_local`; the geoms are 1–12 K.

**These gaps are contended, not a clean measurement.** The run had other jobs in
flight (1.12 `plot_basin_map` finished 17:00:03, 1.05 `plot_climate_source` at
17:00:07), so the numbers are an upper bound on the round-trip, not its cost.
Re-measure with `-c 1` before treating ~20 s as the prize.

## Step 2 answered (2026-09-04) — measured, and the premise was wrong

The contended log gaps above are **not** deserialization. Decomposed directly
against a copy of the `test_case/test_rapid` model root, opened the way rule 1.08
opens it (`mode="r+"`, `data_libs=config/catalogs/deltares_data.yml`). Two
consecutive runs, cold then warm:

| stage | run 1 | run 2 |
|---|---|---|
| interpreter start → script body | 0.56 s | 0.46 s |
| **`import hydromt` + `hydromt_wflow`** | **6.74 s** | **6.48 s** |
| `WflowSbmModel(...)` + catalog parse | 0.26 s | 0.28 s |
| `staticmaps.data` materialize (45 vars) | 0.50 s | 0.50 s |
| `geoms.data` materialize (8 layers) | 0.05 s | 0.05 s |
| `mod.write()` full flush | 0.94 s | 0.88 s |
| total | 9.15 s | 8.75 s |

**~74% of each rule's process is the import.** The model round-trip this item was
opened about — read plus write — is ~1.7 s, and two of the three are redundant,
so the merge's actual I/O prize is **~3.4 s on this fixture, not ~20 s**.

Merging does also remove two process starts and two imports (~14 s here), but
that cost is not WF1's: it is [[t2608202331]], where the per-module import cost
on this machine is measured at 4.79 ms against a normal 0.3–1 ms because the
pixi prefix sits inside ESET's real-time scan surface. With that exclusion in
place the two saved imports are worth ~2 s, and this merge's whole prize falls to
roughly 5 s on the fixture.

**So [[t2608202331]] dominates this item and should go first** — it is
`effort: 1`, needs no code change, and pays out across every rule and the whole
test suite rather than three rules in WF1.

### Revised 2026-09-04 — the exclusion is unavailable, which roughly doubles this item

The owner cannot obtain permission for the ESET exclusion; [[t2608202331]] is
now a `watch-item`. The ~6.5 s import is therefore a **permanent** per-process
cost on this machine, and the arithmetic above inverts:

| | if the exclusion were possible | as things actually are |
|---|---|---|
| merging 1.08 into 1.07 | ~2 s | **~8.7 s** (0.5 s process + 6.5 s import + 1.7 s I/O) |
| merging 1.09 as well | ~5 s | **~17 s** |

**This still does not justify the merge on its own.** A WF1 build takes minutes,
so ~9 s is a small fraction of a one-off cost, and the R7-1 rework plus the six
`ancient(.model_final)` re-checks are the same size as before. What changed is
that the item is no longer *waiting* on anything — the "do the cheap thing first"
route is closed, so a future reader should weigh the merge on its own merits
rather than deferring to a prerequisite that will never land.

Where the import cost actually hurts is the test suite (59 min locally against
~9 in CI), and rule consolidation does nothing for that.

### The one thing that could revive this

The import cost is CONSTANT; the read and write SCALE with the grid. `staticmaps.nc`
is 204 K with 45 variables on this fixture. There is some basin size at which
2 × 1.7 s becomes 2 × something that matters and the merge pays for itself on
I/O alone. Finding it needs the probe pointed at a production model root — a
one-line change — not another fixture run. Until someone does that, this item is
**deferred on value, not blocked on capability**: the code path is understood and
mergeable (see step 1), it is simply not worth the R7-1 rework yet.

Probe: `.tmp/scratchpad/2026-09-04_1718/probe_roundtrip.py` in the `session-1`
worktree — scratch, so treat it as gone; the table above is the durable record
and the probe is ten lines to rewrite.

## Conditional writes were considered and rejected

The cheaper-looking fix — check the disk, skip the write when the content is
already there — does not work here, for two reasons that are worth recording so
it is not re-proposed:

1. **1.07's files are declared Snakemake `output:`** (`build_model.smk:656-664`:
   `staticmaps.nc`, `wflow_sbm.toml`, `region.geojson`, `outlets.geojson`,
   `hydromt_build_config.yml`). A script that runs but conditionally does not
   write a declared output leaves that file's mtime older than the job's inputs,
   so the next dry-run marks 1.07 out of date and it re-runs forever — the same
   self-retrigger class the `ancient()` + `.model_built` scaffolding exists to
   prevent (`build_model.smk:666-678`). A `touch` after the skip moves the mtime
   anyway and the downstream cascade fires identically, so it saves only bytes.
2. **The comparison is the write.** Knowing a geojson is unchanged means
   serializing it. Only a sidecar-hash scheme avoids that, and that is a new
   cache-invalidation surface in a file already bitten twice by trigger
   subtleties (the `params:`→`input:` gauge-id bug, `build_model.smk:205-214`;
   R7-1's toml-stripping, `build_model.smk:666-678`).

Rules 1.08 and 1.09 declare only a `.txt`, a `.yml` and sentinels, so *their*
geom writes are undeclared side effects and are skippable in principle — but
step 2 prices them at well under a second, against a new stale-write failure
mode. Not worth it on any reading.

## The constraint any merge has to satisfy

The R7-1 rebuild cascade. `wflow_sbm.toml` is created by 1.07 and updated in
place by 1.08–1.10, but only 1.07 declares it, so a re-fire of the build rule
alone used to leave the toml stripped of every section the later rules add. The
current chain is `.model_built` → 1.08 → `reservoirs_lakes_glaciers.txt` → 1.09
→ `.outputs_configured` → 1.10, with `ancient()` on `staticmaps.nc` in 1.08/1.09
so neither re-triggers on its own write. Collapsing the rules collapses that
chain; it has to be re-derived, not deleted. Full rationale in the comment at
`build_model.smk:666-678`, and the R10-1 precedent at `build_model.smk:754-764`.

ADR 0004's `.model_final` anchor exists because 1.08 rewrites the whole model
directory — six rules take `ancient(.model_final)` on that basis. A merge
changes which rule is the last writer, so every one of those reads needs
re-checking.

## Step 1 answered (2026-09-04) — the deferral condition is misdirected

`setup_reservoirs_lakes_glaciers.py:1-12` defers the merge to upstream: *"hydromt
1.3's `hydromt build` cannot tolerate per-method no-data … Removal trigger: fold
these methods back … once upstream hydromt handles per-method no-data gracefully
during build."* Installed today: hydromt 1.3.1, hydromt_wflow 1.0.2 — i.e. the
version named.

**But rule 1.07 does not use the `hydromt build` CLI.** `build_wflow_model.py`
runs the steps itself, in a Python loop we own:

```python
# _apply_parameter_steps, build_wflow_model.py:400-422
for name, configured in steps:
    ...
    getattr(model, name)(**call)
```

That is the same mechanic as `_run_waterbody_methods`
(`setup_reservoirs_lakes_glaciers.py:24-46`), which already wraps its
`getattr(mod, method)(**kwargs)` in `except (NoDataException, FileNotFoundError)`
and records `ok` / `skipped` per method. So per-method no-data tolerance during
build is **entirely within our own code** — no upstream change is required, and
the recorded removal trigger will never fire because it is watching the wrong
thing. (The claim about the CLI is not disproved here; it simply does not govern
this path. `hydromt update` *is* shelled out elsewhere in WF1 —
`add_climate_forcing.py:79-120` — which is probably where the belief came from.)

**The two real obstacles are local, and both are small:**

1. `_SUPPORTED_PARAMETER_STEPS` (`build_wflow_model.py:62-68`) is a closed
   allowlist of five methods; the three waterbody methods
   (`setup_reservoirs_simple_control`, `setup_reservoirs_no_control`,
   `setup_glaciers`, per `config/defaults/wflow_update_waterbodies.yml`) have to
   be added to it.
2. `_apply_parameter_steps` has no per-step exception handling. It needs the
   skip *and* the status record — `write_values_used`'s docstring is right that
   status is half the provenance, since a skipped method leaves no trace in the
   model and a values-only record would describe reservoirs that were never
   added.

**1.09 is the harder half, and it is not a build-step merge.** It calls no
`setup_*` parameter step: it does `mod.config.remove("output.csv.column")`, reads
`mod.staticmaps.data` back, and derives three `setup_config_output_timeseries`
calls from what it finds (`setup_gauges_and_outputs.py:59-131`). Merging it means
moving imperative post-build logic into the build module, not extending a
config-driven step list — and the `setup_config` family is *deliberately* outside
the allowlist (`build_wflow_model.py:32-36`: a `setup_config` entry in the
template would fail the build, which is why `logging.silent` is set in the base
config instead).

So the merge shape is **1.08 into 1.07 first** — that alone removes one full
read+write round-trip against obstacles we control — with 1.09 as a separate,
larger decision.

### Side finding: the docstring is stale

`setup_reservoirs_lakes_glaciers.py:1-12` states a rationale that does not hold
for the path it sits on, and its removal trigger points at an upstream event that
is irrelevant to it. Worth correcting whenever this module is next touched, even
if the merge itself is deferred — a wrong reason in a docstring is what kept this
deferred without anyone re-checking it.

## Scope guard

This is rule/DAG restructuring in our own code. It is **not** a licence to
re-engineer how hydromt writes components — per-component writers exist in v1
(`model.<component>.write()`, `docs/hydromt-wflow/user-guide.md:1260`), and using
them is fine, but the `setup_*` / build-config conventions stay verbatim.

## Progress

- [x] Establish whether hydromt_wflow v1 supports the reservoir / lake / glacier `setup_*` methods inside the build config — **answered 2026-09-04: the question was wrong.** 1.07 does not use the `hydromt build` CLI, so the deferral condition never applied; 1.08 is mergeable against two small local obstacles. See "Step 1 answered" above
- [x] Re-measure the read round-trip uncontended — **answered 2026-09-04: the premise was wrong.** The redundant I/O is ~3.4 s, not ~20 s; ~74% of each rule is `import hydromt`. See "Step 2 answered" above
- [ ] Re-run the probe against a production model root to find the basin size at which the I/O saving alone justifies the merge
- [ ] Merge 1.08 into 1.07: extend `_SUPPORTED_PARAMETER_STEPS`, add per-step no-data skip + status recording to `_apply_parameter_steps`, fold `hydromt_update_waterbodies.yml` provenance into the build's `values_used`
- [ ] Re-derive the R7-1 sentinel chain for the collapsed rule set
- [ ] Correct the stale rationale + removal trigger in `setup_reservoirs_lakes_glaciers.py:1-12` (do this even if the merge is deferred)
- [ ] Decide 1.09 separately — it is imperative post-build logic, not a build step
- [ ] Re-check the six `ancient(.model_final)` readers against the new last-writer
- [ ] Validate: `pytest tests/test_cli.py`, then `pixi run test-full` (rule and `script:` signatures move), then `check_baseline.py check` against `project_config_baseline.yml` with WF1 run `--notemp`
