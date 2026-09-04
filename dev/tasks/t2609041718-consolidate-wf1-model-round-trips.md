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
> **Effort** — Large, and the work is not the merge itself but the rebuild-trigger scaffolding it disturbs. The open question is whether hydromt_wflow v1 yet supports the waterbody `setup_*` methods inside the build config, which is the condition 1.08's own header defers to.

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

## Scope guard

This is rule/DAG restructuring in our own code. It is **not** a licence to
re-engineer how hydromt writes components — per-component writers exist in v1
(`model.<component>.write()`, `docs/hydromt-wflow/user-guide.md:1260`), and using
them is fine, but the `setup_*` / build-config conventions stay verbatim.

## Progress

- [ ] Establish whether hydromt_wflow v1 supports the reservoir / lake / glacier `setup_*` methods inside the build config — this is the "when supported" condition 1.08's header defers to, and it decides whether 1.08 can merge at all or only 1.09 can
- [ ] Re-measure the read round-trip with `-c 1` on an uncontended run, and on a basin larger than the fixture, to confirm the prize is real
- [ ] Decide the merge shape (1.09 into 1.07 alone, or all three) and re-derive the R7-1 sentinel chain for it
- [ ] Re-check the six `ancient(.model_final)` readers against the new last-writer
- [ ] Validate: `pytest tests/test_cli.py`, then `pixi run test-full` (rule and `script:` signatures move), then `check_baseline.py check` against `project_config_baseline.yml` with WF1 run `--notemp`
