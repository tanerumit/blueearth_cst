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
> **Why** — The read is the expensive half and it is pure overhead: on the 2026-09-04 run log, rule 1.08 sat ~12 s between its `RUN` banner and its first hydromt message, and 1.09 ~8 s, before either did any work. On the fixture that is seconds; on a production basin the model grows and the round-trip scales with it. Merging is also the direction rule 1.08 already declares for itself (`build_model.smk:687` — *"temporary hydromt fix; can fold back into build_wflow_model when supported"*), with R10-1 as precedent for the repo doing exactly this merge.
> **Effort** — Large, and the work is not the merge itself but the rebuild-trigger scaffolding it disturbs. **Resolved 2026-09-04:** the upstream condition 1.08 defers to does not govern this path at all — see "Step 1 answered" below. 1.08 is mergeable now against our own code; 1.09 is the harder half and is not a build-step merge.

## Where it came from

A question about a WF1 run log on 2026-09-04: why the `Writing geoms to …` block
appears three times. It is not a reporting glitch — the files really are written
three times, by three different rules.

## Measurement — contended, treat as an upper bound

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
geom writes are undeclared side effects and are skippable in principle — worth
~1–2 s, against a new stale-write failure mode. Not worth it on its own; the
round-trip is the target.

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
- [ ] Re-measure the read round-trip with `-c 1` on an uncontended run, and on a basin larger than the fixture, to confirm the prize is real
- [ ] Merge 1.08 into 1.07: extend `_SUPPORTED_PARAMETER_STEPS`, add per-step no-data skip + status recording to `_apply_parameter_steps`, fold `hydromt_update_waterbodies.yml` provenance into the build's `values_used`
- [ ] Re-derive the R7-1 sentinel chain for the collapsed rule set
- [ ] Correct the stale rationale + removal trigger in `setup_reservoirs_lakes_glaciers.py:1-12` (do this even if the merge is deferred)
- [ ] Decide 1.09 separately — it is imperative post-build logic, not a build step
- [ ] Re-check the six `ancient(.model_final)` readers against the new last-writer
- [ ] Validate: `pytest tests/test_cli.py`, then `pixi run test-full` (rule and `script:` signatures move), then `check_baseline.py check` against `project_config_baseline.yml` with WF1 run `--notemp`
