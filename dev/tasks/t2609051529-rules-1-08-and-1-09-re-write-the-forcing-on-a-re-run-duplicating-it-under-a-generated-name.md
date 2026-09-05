---
title: Rules 1.08 and 1.09 re-write the forcing on a re-run, duplicating it under a generated name
type: todo-item
status: backlog
effort: 1
area: wf1 / model build
origin: console screen 2026-09-05
queue:
created: 2026-09-05
updated: 2026-09-05
---

> [!note] Overview
> **What** — On any WF1 re-run where the forcing netCDF already exists, rules 1.08 and 1.09 flush it again through the full hydromt Model.write(); the target exists and overwriting is off, so hydromt writes a DUPLICATE under a generated name and repoints input.path_forcing at it.
> **Why** — It leaves an undeclared multi-MB (production: multi-GB) duplicate in the model directory that nothing cleans up, and between rule 1.09 and rule 1.10 the model TOML points at a forcing file Snakemake does not track.
> **Effort** — small

## How it was found

Reported from a WF1 run on 2026-09-05 at 15:20, against the personal test
config (project dir `.tmp/test_run`). The console showed two alarming rows the
console work had just made legible:

```
15:20:18 - forcing - WARNING - Netcdf forcing file `<model>/forcing/inmaps_historical.nc` already exists and overwriting is not enabled. ...
15:20:18 - forcing - Writing file <model>/forcing/inmaps_extract_historical_extract_historicald_debruin_None_2010_2016.nc
```

and then, at rule 1.09, the same warning naming the GENERATED file.

## The mechanism, confirmed in code

1. Rules 1.08 (`setup_reservoirs_lakes_glaciers.py:129,138`) and 1.09
   (`setup_gauges_and_outputs.py:51,140`) open the model `mode="r+"` and call
   the full `mod.write()`, which flushes every component — forcing included.
2. On a re-run the forcing netCDF already exists and `input.path_forcing`
   names it, so the forcing component reads it back and writes it out again.
3. The target exists and overwriting is off, so
   `hydromt_wflow/components/forcing.py:182` warns and
   `_create_new_filename` invents
   `inmaps_<precip>_<temp>d_<pet_method>_<press>_<start>_<end>.nc`.
4. `forcing.py:265` then does
   `self.model.config.set("input.path_forcing", filepath.as_posix())` — so the
   model TOML is repointed at the duplicate.

Rule 1.10 later rewrites `inmaps_historical.nc` and repoints `path_forcing`
back, which is why a COMPLETE run ends with a correct TOML. Measured on
`.tmp/test_run`: `forcing/` held both files, 3.24 MB of duplicate beside
3.52 MB of the real one, and `path_forcing` was correct at rest.

## Why it is worth fixing

- **The duplicate is never cleaned.** It is not a declared output of any rule,
  so Snakemake will not remove it. On the rapid fixture it is 3 MB; forcing
  scales with basin area x run length, so on a production basin it is the
  largest single file the build writes, duplicated.
- **There is a window where the TOML is wrong.** Between rule 1.09 finishing
  and rule 1.10 rewriting the forcing, `input.path_forcing` names an undeclared
  file. A run that stops in that window — a failure, an interrupt, `--until`,
  or 1.10 judged up to date — leaves the model pointing at it.
- It is NOT a regression from the console work. `f214b75a`, the only recent
  commit touching rule 1.08, is comment-only. The console work merely made the
  rows readable enough to notice.

## Options

1. **Write only the components each rule changed.** 1.08 changes staticmaps,
   geoms and config; 1.09 changes config and staticmaps. Replacing the blanket
   `mod.write()` with the specific writers removes the forcing flush entirely.
   Needs care: under-writing a component is silent.
2. **Drop the forcing from the model object before `write()`**, so the flush
   finds nothing. Smaller diff, but relies on hydromt tolerating an emptied
   component — which is the same branch that already logs `Write forcing
   skipped: dataset is empty`, so it is a supported state.
3. **Do nothing and clean up after.** Rejected on sight: it leaves the TOML
   window open, which is the half that can affect a result.

## What was done: option 1, by replicating the plugin's sequence

Option 2 was tried first and abandoned. There is no PUBLIC way to empty the
component: `forcing.set()` refuses data without a `time` dimension
(`components/forcing.py:288`), and the only other route is assigning the
private `_data`.

Option 1 then hit its own wall. `hydromt`'s base `Model.write` takes a
`components` list, so naming everything except `forcing` would have been a
one-line fix -- but `WflowBaseModel` OVERRIDES `write` with a signature that
takes filenames only (`wflow_base.py:1716`), and that call raises `TypeError`.
Read the plugin's override, not the base class.

What landed is `blueearth_cst/shared/wflow_write.py`: the plugin's own write
sequence, step for step, minus `self.forcing.write(...)`, keeping its opening
`Write model data to <root>` row so the two rules are not silent. The cost is
that it must stay in step with the plugin, and drift would be SILENT -- a
component hydromt adds would just stop being written and the run would still
exit 0. `tests/test_wflow_write.py` closes that with a drift guard that parses
the plugin's own source and asserts its component writes are exactly ours plus
the forcing.

## Verification

`test-full`, plus the re-run case no fixture covers: a complete WF1 on the
rapid config, then `-f add_reservoirs_lakes_glaciers declare_wflow_outputs`
against the resulting model. Snakemake ran exactly those 2 jobs (rule 1.07 did
NOT re-run, which would have wiped the forcing and made the check vacuous).
Before: a 3.24 MB duplicate and a repointed TOML. After: `forcing/` holds only
`inmaps_historical.nc` and `path_forcing = "forcing/inmaps_historical.nc"`,
unchanged, with no `already exists and overwriting` row in the log.

WF3's rule 3.14 was checked for the same defect and is clean -- it writes
`mod.forcing.write(filename=...)` and `mod.config.write(...)` explicitly,
never a blanket `write()`.

## Relation to t2609041718

That watch-item ruled the 1.07/1.08/1.09 split worth KEEPING, on failure
isolation, after measuring the redundant I/O at ~1.7 s per rule. This is new
evidence of a different kind: the split's cost is not only time, it duplicates
a large artifact and briefly falsifies the model config. It does not overturn
the ruling — the fix here is to stop those rules flushing forcing, not to merge
them — but the watch-item should cite this one.

## Progress

- [x] Pick between options 1 and 2 — option 1, via a replicated sequence
- [x] Add a regression test — `tests/test_wflow_write.py`, including the drift
      guard against the plugin's own source
- [x] Land, then re-run 1.08 and 1.09 against a model that already has forcing
- [x] Check WF3 for the same defect — clean
- [x] Cross-reference from `t2609041718`
