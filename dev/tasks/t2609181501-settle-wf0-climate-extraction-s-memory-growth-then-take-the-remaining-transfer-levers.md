---
title: Settle wf0 climate extraction's memory growth, then take the remaining transfer levers
type: todo-item
status: active
branch: feat/wf0-chirps-candidate
effort: 2
area: wf0 climate extraction
origin: t2609181316 slow ERA5 download
queue:
created: 2026-09-18
updated: 2026-09-18
---

> [!note] Overview
> **What** — Three follow-ups left by the 2026-09-18 investigation into a slow era5 extraction over the Deltares P: share. (A) is **settled and fixed**: the memory growth was the HDF5 chunk cache on the READ, not the streaming write, and bounding it cut peak RSS 7x at no cost in bytes or time. (B) is **taken**: both branches align reads to source chunks, and a comparison-only CHIRPS candidate no longer downloads or reprojects ERA5 fields it never plots. Selected CHIRPS stores retain the full hybrid needed by WF1/WF3. (C) is **implemented for rapid/dev**: a project-owned catalog loaded after the rapid config's original base replaces only `era5` with the daily Zarr source, while an explicit metadata guard refuses dates after 2023-02-01. The source-geometry follow-up is also settled: keep the live store unchanged and use `(365, 103, 240)` for a future aligned mirror.
> **Why** — Rule 0.04 moved 9.46 GB across the wire to write a 2.3 MB store. The amplification is structural and cannot go to zero, but the memory hazard is gone and the remaining byte lever is cheaper than it looked.
> **Effort** — large

## What landed

On `chore/test-cases`:

- `94b42e95` — `perf(wf0)`: the non-chirps branch asked for `chunks: "auto"`, which over a
  network store spans several on-disk chunks and drags every one of them across the wire.
  Now asks for the store's encoded chunking, spelled `{}`. Measured 3.85x fewer bytes.
- `c8e3beaf` — `docs(wf0)`: corrects that commit's claim that era5's `longitude: 240` costs
  a double decompression. It costs that only when a basin STRADDLES the split; Ntoum sits
  inside one half and reads the same 0.48 GB either way.
- **(A)** `_bounded_hdf5_chunk_cache`, a decorator on `prep_historical_climate` that caps
  netcdf-c's per-variable chunk cache at 1 MiB for the duration of the call and restores it
  after.
- **(B1)** `_align_chunks_to_store`, which hoists the `chunks: {}` override out of the
  `else` arm so the chirps branch's era5 read gets it too.

## The measured picture

Uncontended, full 2000-01-02..2016-12-31 window, Ntoum bbox. The first three rows are an
eager read then write; the last two are the SHIPPED path
(`to_netcdf(compute=False)` under the synchronous scheduler), measured end to end.
Every row produced the same store, checked variable by variable.

| configuration | transferred | time | peak RSS |
|---|---|---|---|
| netCDF + `"auto"` + synchronous (before) | ~36 GB | ~29 min | not sampled |
| netCDF + `{}` + synchronous | 9.46 GB | 8.6 min | not sampled |
| zarr + `{}` + 32 threads | 4.53 GB | 4.3 min | not sampled |
| **shipped, netCDF + bounded chunk cache** | **9.46 GB** | **8.8 min** | **435 MB** |
| **shipped, zarr + bounded chunk cache** | **4.53 GB** | **3.5 min** | **460 MB** |

**Do not quote the 46 min from the original run as the baseline.** chirps and era5 both
started 13:18:13 under `-c 3` and shared the link for 27 of those 47 minutes. The
uncontended before-figure is ~29 min.

**Why a 2.3 MB store costs gigabytes:** compressed chunked stores have a minimum
readable unit. Ntoum needs 25 grid cells; the smallest thing the era5 netCDF hands over
is one 250x480 chunk covering 120,000. Seven variables x 13 time-chunks/yr x 17 yr is a
~9.5 GB floor for this source however well the code behaves. Checked and ruled out: the
per-variable stores (`meteo/era5_daily/t2m/` etc.) carry the same 30x250x480 chunking,
so they offer nothing.

**The link runs at ~18-21 MB/s and ONE reader saturates it.** That single fact explains
every negative parallelism result below, and it is why the only levers that work are
ones that move FEWER BYTES.

## Progress

- [x] **(A) The memory growth is the HDF5 chunk cache, and it is bounded now.** The
      suspicion was that the shipped streaming graph accumulates and that an eager read
      with a size guard would be both faster and safer. It is not the graph. Over
      2000..2002, one process per path with an RSS sampler attached: shipped streaming
      peaked at **1578 MB**, an eager read at **1596 MB**, and a read with **no write at
      all** at **1570 MB**. The write is innocent, and the scheduler comment's claim
      that synchronous streaming "leaves peak memory unchanged" was right all along.
      <br>The growth is netcdf-c's per-VARIABLE chunk cache, 64 MiB by default
      (`netCDF4.get_chunk_cache()` -> 67108864, libnetcdf 4.10.1), held once per (file,
      variable). 21 pairs over 2000..2002 held 1.26 GB; 42 pairs over 2000..2005 held
      2.50 GB — 60 MB each, the four 30x250x480 chunks that fit under 64 MiB. Against a
      source stored as yearly files that makes resident memory a function of the WINDOW
      rather than of the basin, which is how a 2.3 MB store projected to ~7 GB resident.
      <br>`chunks: {}` makes the dask chunk the disk chunk, so every chunk is read once,
      sliced and dropped: the cache is pure cost. At 1 MiB, below one chunk, HDF5
      bypasses it. Over 2000..2005: same 3.34 GB, peak RSS **2811 -> 394 MB**, read
      marginally FASTER (2.90 min against 3.02).
- [x] **(A) The shipped-path measurement is finished.** Full 17-year window, shipped
      path, bounded cache: **9.46 GB, 8.76 min, peak RSS 435 MB, 2312 KB store** — and
      bit-identical to the pre-fix store over a matched window, all seven variables,
      maxdiff 0. The run the harness reaped under memory pressure is now explained
      rather than merely retried.
- [x] **(B1) Both branches now read at the store's own chunking.** The override lived in
      the `else` arm only, so the chirps branch read era5 for its other six variables at
      whatever the catalog declared — `longitude: 240` under
      `deltares_data_pdrive.yml`, which splits the stored 480-wide chunk. Ntoum sits
      inside one half and reads 0.48 GB either way, so this buys that basin no bytes: it
      removes a basin-dependent cliff and stops the two arms disagreeing about how to
      read the same source.
- [x] **(B2) Comparison-only CHIRPS no longer reads ERA5 at all.** The apparent
      cross-rule reuse problem came from giving every CHIRPS store the selected-source
      forcing contract. WF0 already plots and compares CHIRPS precipitation only; its
      borrowed ERA5 fields, DEM read, lapse correction and `orography.nc` were unused.
      `forcing_required=False` now marks only wf0's extra precipitation-only candidates,
      is recorded in rule params, and omits the forcing-only sidecar. Selected CHIRPS
      keeps the default full seven-variable hybrid for WF1/WF3. Promoting a candidate
      removes the flag, so Snakemake re-extracts under the full forcing contract instead
      of reusing the precipitation-only store.
- [x] **(C) Ruled: take zarr, drop the threading, and it is ONE change.** The 2026-09-18
      figure was zarr + 32 threads and read as three coupled changes, one of which
      depended on (A). Measured through the shipped path, synchronous, no threads:
      **4.53 GB in 3.53 min at 21.4 MB/s, peak RSS 460 MB, store bit-identical** to the
      netCDF-sourced one (all seven variables, maxdiff 0). That is FASTER than the
      threaded figure of 4.30 min — the threading was not helping, it was costing.
      <br>Processes do not help either, and this is the experiment `procs.py` was
      written for and never run: six processes over 2000..2005 moved the same 3.37 GB in
      **3.99 min at 14.1 MB/s**, against one process's 3.02 min at 18.4 MB/s. A single
      reader already saturates the link, so adding readers costs ~23%.
      <br>So (C) reduces to repointing era5's `uri` at `meteo/era5_daily.zarr`, and two
      costs survive: a project-local override layer against `deltares_data_pdrive.yml`,
      which is vendored upstream-verbatim and sha256-pinned by
      `tests/test_sealed_records.py`; and a coverage REGRESSION, since the zarr store
      ends 2023-02-01 against the netCDF's advertised 2023-11-30. Neither of them
      depends on (A) any more.
- [x] **(C) Stage 1 implemented without touching the sealed catalog.**
      `config/catalogs/deltares_era5_daily_zarr.yml` repeats the complete `era5`
      source because HydroMT composition replaces a source rather than deep-merging
      it. `project_config_rapid.yml` keeps its original `deltares_data.yml` base and
      loads this one-entry override second. HydroMT captures roots per source:
      composed-catalog inspection proved `era5` resolves to
      `P:\wflow_global\hydromt`, while `chirps`, `merit_hydro`, and
      `basin_atlas_level12_v10` retain the base catalog's `C:\data` root and all
      non-era5 source specs remain equal. The sealed P-drive catalog was not needed
      or touched. The Zarr driver remains
      `raster_xarray`, but its options block is replaced by only `chunks: {}`:
      netCDF-only `combine` and `parallel` never reach `open_zarr`.
      <br>The override advertises the measured 1950-01-02..2023-02-01 range, and
      extraction checks that contract before its first raster read. A request
      outside it now raises with the requested and available dates instead of
      accepting HydroMT's overlap. `project_config_baseline.yml` is unchanged:
      stage 1 does not move the numerical reference.
- [x] **(C3) Source chunk geometry measured and decided.** The exact live Zarr is
      v2, consolidated, unsharded, and EPSG:4326. Its seven wf0 float32 arrays all
      have shape `(26694, 721, 1440)`, chunk shape `(365, 103, 480)`, and
      Blosc/Zstd level-3 byte-shuffle compression. Coordinates are daily
      proleptic-Gregorian 1950-01-02..2023-02-01, latitude 90..-90 by -0.25,
      longitude 0..359.75 by 0.25. A deterministic 27-key sample per variable
      found 19.2..37.4 MiB median compressed full chunks (68.8 MiB raw); `tisr`
      had 9/27 absent all-fill keys, which the model treats deliberately.
      <br>Exact current intersection sums for Ntoum plus the production two-cell
      buffer were **239.2 MiB / 7 requests** for 30 days and
      **4312.9 MiB / 126 requests** for 2000-2016. A non-redundant short live
      HydroMT probe measured **244.0 MiB process reads, 18.49 s, 621.8 MiB peak
      RSS**. This agrees with chunk-file bytes; it is one P-drive observation,
      not a claim about network performance. The existing full shipped
      measurement remains **4.53 GB, 3.53 min, 460 MB RSS**, bit-identical to
      netCDF.
      <br>Candidate grid: current `(365,103,480)`, longitude-half
      `(365,103,240)`, latitude-half `(365,52,480)`, time-half
      `(180,103,480)`, and balanced `(180,103,240)`. Costs were modeled for
      Ntoum, aligned 10-degree and 40-degree windows, and a 10-degree window
      straddling a new 60-degree chunk boundary, over 30 days and 2000-2016.
      Per-variable bytes/cell were calibrated to each access's exact current
      sum. **Recommend `(365,103,240)` for a future immutable global or
      multi-region mirror whose expected envelopes mostly fit within its
      60-degree boundaries**: modeled chunks are 9.6..18.7 MiB compressed, and
      bytes halve without more requests for the aligned cases. The boundary
      stress case instead doubles requests and transfers the same modeled bytes
      as current. For a fixed regional mirror, crop and align longitude chunks
      to its target envelope. Time-half nearly doubles the normal Ntoum requests
      (126 -> 245) while saving little for the normal window; latitude-half
      doubles requests for the aligned 10-degree window; balanced falls mostly
      below the 8-32 MiB target and also pays the time request cost. Keep annual
      time chunks for normal CST windows. Only when sub-seasonal reads dominate
      should `(180,103,240)` be benchmarked against the intended storage
      protocol. No production rechunk workflow or dependency was added.

## What is left

1. **(C) residual constraint** — the rapid/dev ERA5 path cannot serve dates after
   2023-02-01. Keep the baseline/netCDF path for later 2023 dates, or wait for the
   Deltares Zarr store to be extended and then update the override metadata only
   after measuring the actual store coverage.

## Reproducing

Harness and raw logs: `dev/working/2026-09-18_wf0-climate-transfer/`, whose README says
what each script answers. Start with `mem.py` — it drives the SHIPPED
`prep_historical_climate` and separates streaming / eager / read-only by intercepting
`Dataset.to_netcdf`, so a difference it reports is a difference in the product. Run from
a worktree root with the pixi env's python.

Three traps, all of which cost time on 2026-09-18:

- **Measure through `get_rasterdataset`, never `open_mfdataset` + `.sel`.** The direct
  form shows the chunk specs within 4% of each other and reads as proof the chunking is
  irrelevant. It is not: slicing an opened dataset lets dask fuse the slice into the
  backend read. hydromt applies era5's `rename` and `unit_mult` between the read and the
  clip, and that elementwise layer blocks the fusion.
- **The primary worktree ships an editable install of `blueearth_cst`.** A bare
  `python script.py` under a session worktree imports MAIN's copy. `sys.path.insert(0,
  os.getcwd())` plus an assertion on `module.__file__` is the guard the scripts use.
- **A memory claim about one path is worth nothing until the other paths are sampled the
  same way.** The streaming write was suspected for a whole investigation because it was
  the only path anyone had attached an RSS sampler to. Three runs of one script with one
  argument changed cleared it in four minutes.

Exact geometry reproduction (read-only; no scratch store):

```powershell
pixi run python dev/working/2026-09-18_wf0-climate-transfer/inspect_zarr_geometry.py --probe-current
```

The script prints the deterministic 189-key sampling bound, all bbox/time
bounds, exact current compressed intersections, modeled candidates, and the
short live read caveat. It neither mutates P: nor writes a rechunked probe.
