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
