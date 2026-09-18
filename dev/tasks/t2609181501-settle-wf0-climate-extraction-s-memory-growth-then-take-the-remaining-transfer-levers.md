---
title: Settle wf0 climate extraction's memory growth, then take the remaining transfer levers
type: todo-item
status: active
branch: chore/test-cases
effort: 2
area: wf0 climate extraction
origin: t2609181316 gabon-ntoum-deltares slow era5 download
queue:
created: 2026-09-18
updated: 2026-09-18
---

> [!note] Overview
> **What** — Three follow-ups left by the 2026-09-18 investigation into a slow era5 extraction over the Deltares P: share. (A) is **settled and fixed**: the memory growth was the HDF5 chunk cache on the READ, not the streaming write, and bounding it cut peak RSS 7x at no cost in bytes or time. (B) is **half taken**: the chunk override now covers both branches, but the duplicate era5 read across two rules collides with the climate-store rule's documented one-input invariant and needs an owner decision. (C) is **ruled, and it inverted**: zarr ALONE takes 2.1x the bytes and 2.5x the time off the read, so the change is one `uri`, not three coupled ones.
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
- [ ] **(B2) The duplicate era5 read needs an owner decision, and it is the EXPENSIVE
      lever now, not the cheap one.** A project with both sources configured reads era5
      twice: once for its own store, once inside the chirps branch (~8.2 GB per 17-year
      run). Removing it means making an era5 store an INPUT of the chirps store.
      <br>The blocker is `climate_store_rule`'s own docstring: "**The input set is
      exactly one entry — the catalog — in both DAGs.** An asymmetric input set
      re-creates the wf1<->wf3 re-extraction oscillation (design P2(b) / ext1-02)."
      `tests/test_climate_store_contract.py` pins that equivalence, and wf0's generated
      0.04 splats `**_spec.inputs` verbatim, so a wf0-only edge is not available.
      <br>A SYMMETRIC version respects the invariant — every chirps store depends on an
      era5 store, in all three workflows — and the trade then becomes explicit: a
      chirps+era5 project saves 8.2 GB; a **chirps-only project pays ~1.4 GB more** (the
      era5 store carries `precip`, a seventh variable the chirps branch never reads) and
      gains a store directory for a source it never configured, which
      `prune_climate_store.py`, the freshness tests and the comparison-figure logic all
      then see. Not landed: the blast radius is three Snakefiles plus `shared/`, and the
      chirps-only regression is a real cost to accept on someone else's behalf.
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

## What is left

1. **(B2)** — owner decision on the symmetric era5-store dependency, with the
   chirps-only regression above as the thing to accept or refuse.
2. **(C)** — owner decision on the zarr repoint: a project-local catalog override layer
   plus a documented end-of-coverage at 2023-02-01, in exchange for halving the transfer
   of every era5 extraction.

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
