---
title: Settle wf0 climate extraction's memory growth, then take the remaining transfer levers
type: todo-item
status: backlog
branch: chore/test-cases
effort: 2
area: wf0 climate extraction
origin: t2609181316 gabon-ntoum-deltares slow era5 download
queue:
created: 2026-09-18
updated: 2026-09-18
---

> [!note] Overview
> **What** — Three follow-ups left by the 2026-09-18 investigation into a slow era5 extraction over the Deltares P: share. (A) The SHIPPED write path's resident memory grows 1:1 with bytes read; measure it to completion and decide whether the eager read the code currently rejects is in fact both faster and safer. (B) The chirps branch reads era5 from P: a second time, ~8.2 GB per 17-year run, near-duplicating the era5 store. (C) zarr + threads halves the transfer again, at the cost of three coupled changes. A is a possible defect; B is the largest remaining saving; C is the least attractive.
> **Why** — Rule 0.04 moved 9.46 GB across the wire to write a 2.3 MB store, and that is AFTER the fix that landed. The amplification is structural and cannot go to zero, but A may be a real memory hazard on a large basin and B is pure duplicate traffic that needs no new machinery.
> **Effort** — large

## What already landed (on `chore/test-cases`, unpushed)

- `94b42e95` — `perf(wf0)`: the non-chirps branch asked for `chunks: "auto"`, which over a network store spans several on-disk chunks and drags every one of them across the wire. Now asks for the store's encoded chunking, spelled `{}`. Measured 3.85x fewer bytes through `get_rasterdataset`.
- `c8e3beaf` — `docs(wf0)`: corrects that commit's claim that era5's `longitude: 240` costs a double decompression. It costs that only when a basin STRADDLES the split; Ntoum sits inside one half and reads the same 0.48 GB either way.

## The measured picture

Uncontended, full 2000-01-02..2016-12-31 window, Ntoum bbox, eager read then write.
Every row produced a **byte-identical** 2309 KB store (all seven variables checked).

| configuration | transferred | time |
|---|---|---|
| netCDF + `"auto"` + synchronous (before) | ~36 GB | ~29 min |
| netCDF + `{}` + synchronous (**now**) | 9.46 GB | 8.6 min |
| zarr + `{}` + 32 threads | 4.53 GB | 4.3 min |

**Do not quote the 46 min from the original run as the baseline.** chirps and era5 both
started 13:18:13 under `-c 3` and shared the link for 27 of those 47 minutes. The
uncontended before-figure is ~29 min.

**Why a 2.3 MB store costs gigabytes:** compressed chunked stores have a minimum
readable unit. Ntoum needs 25 grid cells; the smallest thing the era5 netCDF hands over
is one 250x480 chunk covering 120,000. Seven variables x 13 time-chunks/yr x 17 yr is a
~9.5 GB floor for this source however well the code behaves. Checked and ruled out: the
per-variable stores (`meteo/era5_daily/t2m/` etc.) carry the same 30x250x480 chunking,
so they offer nothing.

## Progress

- [ ] **(A) Finish the shipped-path measurement.** Everything in the table above was
      measured as `get_rasterdataset(...).compute()` then `to_netcdf` — an eager read.
      The shipped code does `to_netcdf(compute=False)` then `delayed_obj.compute()`,
      interleaving read and write in ONE synchronous graph. That is a different graph and
      it has not been measured to completion. Read rate matched the eager path
      (~17-18.5 MB/s), so ~9.5 min is the projection, unconfirmed.
- [ ] **(A) Decide on eager-vs-streaming.** Across seven samples the shipped path's RSS
      tracked bytes read almost exactly — 2.33 GB read / 2150 MB RSS, rising linearly to
      3.86 GB / 3680 MB — projecting ~9 GB RSS for a 5x5-cell basin. That inverts the
      rationale in `extract_historical_climate.py`'s scheduler comment, which rejects an
      eager `.load()` because "eager would trade a deadlock for an OOM on a large basin"
      while claiming synchronous streaming leaves "peak memory unchanged". The eager path
      materialized 4.3 MB. If the growth is real, eager-with-a-size-guard is plausibly
      both faster and safer, and the comment needs rewriting either way.
      *The run was stopped by the harness on system-wide memory pressure before it
      finished, so the reap cannot be attributed to this process — but the RSS samples are
      direct measurements and stand on their own.*
- [ ] **(B) Stop reading era5 twice.** The `chunks` override lives only in the `else`
      branch. The chirps branch calls `_read_source(data_catalog, "era5", ...)` for six
      variables with no override at all — measured 0.48 GB/yr, ~8.2 GB per 17-year run,
      against the era5 store's own 9.46 GB. Any project with both sources configured
      (this one: `Pooled precip over 2 sources: chirps, era5`) pays both. Needs a rule
      dependency that exists only when era5 is among the configured sources, so it is a
      design change, not a patch. Largest remaining lever; needs no zarr and no threading.
- [ ] **(C) Rule on zarr + threads.** 2.1x bytes and 2.0x time, output verified
      bit-identical. Three coupled changes, and each is a real cost: a project-local
      override layer against `deltares_data_pdrive.yml`, which is vendored
      upstream-verbatim and sha256-pinned by `tests/test_sealed_records.py`; a coverage
      REGRESSION, since `meteo/era5_daily.zarr` ends 2023-02-01 against the netCDF's
      advertised 2023-11-30; and threading, which is safe only if read and write are
      separated into different graphs — i.e. it depends on (A) landing first.
      Note netCDF + threads buys nothing (32.0 s vs 29.1 s): HDF5's lock serializes reads
      whatever the scheduler. Processes would sidestep it and were never tested — that is
      the cheap experiment that could deliver (C)'s win with none of (C)'s costs.

## Reproducing

Harness and raw logs: `dev/working/2026-09-18_wf0-climate-transfer/`. Run from a worktree
root with the pixi env's python; each script prints bytes read via `psutil` io counters
alongside wall clock.

Two traps that cost time on 2026-09-18, both worth reading before re-measuring:

- **Measure through `get_rasterdataset`, never `open_mfdataset` + `.sel`.** The direct
  form shows the chunk specs within 4% of each other and reads as proof the chunking is
  irrelevant. It is not: slicing an opened dataset lets dask fuse the slice into the
  backend read. hydromt applies era5's `rename` and `unit_mult` between the read and the
  clip, and that elementwise layer blocks the fusion.
- **The primary worktree ships an editable install of `blueearth_cst`.** A bare
  `python script.py` under a session worktree imports MAIN's copy. `sys.path.insert(0,
  os.getcwd())` plus an assertion on `module.__file__` is the guard the scripts use.
