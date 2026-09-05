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

Option 2 looks like the smallest correct change and its own log row already
proves the target state is supported. Either way this is a rule-behaviour
change and takes the full ladder: `test-full`, plus a WF1 re-run against a
model that already has forcing, which is the case no fixture currently covers.

## Relation to t2609041718

That watch-item ruled the 1.07/1.08/1.09 split worth KEEPING, on failure
isolation, after measuring the redundant I/O at ~1.7 s per rule. This is new
evidence of a different kind: the split's cost is not only time, it duplicates
a large artifact and briefly falsifies the model config. It does not overturn
the ruling — the fix here is to stop those rules flushing forcing, not to merge
them — but the watch-item should cite this one.

## Progress

- [ ] Pick between options 1 and 2
- [ ] Add a regression test: build, then re-run 1.08 against a model that
      already has forcing, and assert the forcing directory holds exactly one
      netCDF and `path_forcing` still names it
- [ ] Land, then re-run WF1 twice in a row on the rapid config to confirm
- [ ] Cross-reference from `t2609041718`
