# wf0 climate extraction — transfer and memory probes (2026-09-18)

Measurement harness behind task `t2609181501`. Read that note first; it carries the
results, the conclusions and the two traps. This file only says what each script does.

Run from a worktree root, with the pixi env's python. Each script reports bytes moved
(`psutil` io counters) alongside wall clock, because on a network store the byte count is
the thing that explains the clock.

| script | answers |
|---|---|
| `inspect_era5.py` | what the source's on-disk HDF5 chunking actually is |
| `chirpsbranch.py` | what the CHIRPS branch's separate era5 read costs (lever B) |
| `explore.py` | netCDF vs zarr x synchronous vs threads, one year each |
| `threads.py` | how the zarr read scales with dask worker count |
| `full.py` | the full 17-year window, eager read then write — `nc_sync` \| `zarr_thr` |
| `shipped.py` | the SHIPPED path (`to_netcdf(compute=False)` + synchronous compute) |
| `mem.py` | peak RSS of the shipped path, an eager read and a bare read (lever A) |
| `verify.py` | that two stores written by different paths are bit-identical |
| `procs.py` | whether processes sidestep the HDF5 lock that defeats threads |
| `inspect_zarr_geometry.py` | exact Zarr-v2 metadata and current-chunk bytes, plus calibrated candidate-geometry costs |

`mem.py` is the one that settled lever A, and it is the script to reach for
first: it drives the SHIPPED `prep_historical_climate` and separates the three
paths by intercepting `Dataset.to_netcdf` rather than by re-implementing the
read, so a difference it reports is a difference in the product. Its `ZARR=1`
knob repoints era5 at the zarr store and changes nothing else, which is how
lever C's store win was separated from its threading.

Two things these scripts encode deliberately, both of which produced a wrong answer first:

- They measure through `DataCatalog.get_rasterdataset`, not `xr.open_mfdataset` + `.sel`.
  The direct form lets dask fuse the slice into the backend read and hides the effect
  entirely.
- They `sys.path.insert(0, os.getcwd())` and assert on `module.__file__`, because the
  primary worktree ships an editable install of `blueearth_cst` and a bare run imports
  main's copy rather than the worktree's.

A third, learned on 2026-09-18: **compare paths inside ONE process, or not at
all.** The memory growth that opened lever A was read as a property of the
streaming write because the streaming write was the only path ever measured
with an RSS sampler attached. It was a property of the read, and three runs of
the same script with one argument changed said so in four minutes.

Bbox is hard-coded to Ntoum. A different basin changes the byte counts — and, for the
`longitude: 240` chunk-split question, can change the answer.

## Source-geometry decision

Recommendation #3 was evaluated against the exact live
`P:\wflow_global\hydromt\meteo\era5_daily.zarr`, read-only:

```powershell
pixi run python dev/working/2026-09-18_wf0-climate-transfer/inspect_zarr_geometry.py --probe-current
```

The script reports its sampling and bounds. It reads consolidated metadata,
samples exactly 27 deterministic keys per wf0 variable (first/middle/last on
each axis), sums the exact current chunk files intersecting every access, and
calibrates candidate byte estimates to those access-specific sums. Candidate
compression remains a model: no mirror was written.

The store is Zarr v2 with consolidated metadata and no sharding. All seven wf0
arrays are float32, `(time, latitude, longitude) =
(26694, 721, 1440)`, chunked `(365, 103, 480)`, and compressed with
Blosc/Zstd level 3 plus byte shuffle. Full current chunks are 68.8 MiB raw;
sampled median compressed sizes vary from 19.2 MiB (`tisr`) to 37.4 MiB
(`tp`). The coordinates are daily proleptic-Gregorian
1950-01-02..2023-02-01, latitude 90..-90 by -0.25, and longitude
0..359.75 by 0.25 (EPSG:4326 from the catalog).

For Ntoum plus the production two-cell buffer, exact current compressed bytes
are 239.2 MiB for 30 days and 4312.9 MiB for 2000-2016. The short live HydroMT
probe observed 244.0 MiB process reads, 18.49 s and 621.8 MiB peak RSS; it is a
single P-drive observation, not a network-throughput benchmark. The previously
measured shipped 2000-2016 run remains the normal-window timing:
4.53 GB, 3.53 min, 460 MB peak RSS, bit-identical to netCDF.

**Decision:** keep the live store unchanged, but use `(365, 103, 240)` for a
future immutable global or multi-region mirror whose expected envelopes mostly
fit within its 60-degree longitude boundaries. Halving longitude keeps the
year-aligned time chunks and places modeled full chunks at 9.6..18.7 MiB
compressed. Calibrated bytes halve without more requests for Ntoum and the
aligned 10-degree and 40-degree windows. A 10-degree window straddling a new
60-degree boundary instead reads two half-width chunks: requests double and
modeled bytes equal the current geometry. Halving time helps a 30-day read but
nearly doubles requests for 2000-2016 (126 to 245 at Ntoum) and saves little on
that normal window. Halving latitude crosses the aligned 10-degree window and
doubles its requests. The balanced candidate reaches 4.7..9.2 MiB chunks,
below the target for most variables, while also paying the time request cost.

Bounded selection rule: retain annual time chunks for normal CST windows. For a
fixed regional mirror, crop the store and align its longitude chunks to the
target envelope; for a global or multi-region mirror, use longitude 240 only
when expected envelopes mostly avoid the new 60-degree boundaries. If
sub-seasonal requests dominate, benchmark `(180, 103, 240)` against the real
storage protocol before choosing it; local/P-drive timing alone cannot
establish object-store or network performance.
