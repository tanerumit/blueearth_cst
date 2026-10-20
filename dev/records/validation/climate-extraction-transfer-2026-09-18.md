# Climate extraction transfer evidence — 2026-09-18

Historical Ntoum measurements from task `t2609181501`, condensed on 2026-10-20 without rerunning
the probes. Full source and harness recovery:

```text
git show 53d07f52:dev/records/reviews/wf0-climate-transfer-2026-09-18/README.md
```

The associated tracked scripts are recoverable from that directory at the same commit.
The README also names `inspect_zarr_geometry.py`, which was not present in the retained directory;
this summary does not establish recovery of that script or the original untracked logs.
No executable candidate hash was supplied by the source.

## Observed store and access

The live `P:\wflow_global\hydromt\meteo\era5_daily.zarr` was inspected read-only.
It was Zarr v2, consolidated, unsharded, with seven float32 WF0 arrays of shape
`(time, latitude, longitude) = (26694, 721, 1440)`.
Chunks were `(365, 103, 480)`, compressed with Blosc/Zstd level 3 and byte shuffle.
Full chunks were 68.8 MiB raw; sampled median compressed sizes ranged from
19.2 MiB (`tisr`) to 37.4 MiB (`tp`).

Coordinates were daily proleptic-Gregorian, 1950-01-02–2023-02-01, latitude 90 to −90
at −0.25°, longitude 0 to 359.75° at 0.25°; the catalog declared EPSG:4326.
Sampling covered exactly 27 deterministic keys per variable: first/middle/last on each axis.
Current compressed-byte totals summed the actual intersecting chunk files.

For Ntoum with the production two-cell buffer:

| Access | Evidence |
|---|---|
| 30 days | 239.2 MiB exact intersecting compressed chunks |
| 2000–2016 | 4312.9 MiB exact intersecting compressed chunks |
| Short live HydroMT probe | 244.0 MiB process reads, 18.49 s, 621.8 MiB peak RSS |
| Previously measured shipped 2000–2016 extraction | 4.53 GB, 3.53 min, 460 MB peak RSS |

The source reports the shipped Zarr extraction as bit-identical to netCDF.
The short probe is a single P-drive observation, not a general throughput benchmark.
Raw chunk-file bytes and process I/O counters are different measures; GB/MB above retain the
source's units rather than being silently converted to GiB/MiB.

## Candidate geometry estimates and limits

Candidate compressed-byte estimates were calibrated to access-specific measured current sums.
No candidate mirror was written; compression and speed benefits were not empirically established.

For `(365, 103, 240)`, modeled full compressed chunks were 9.6–18.7 MiB.
Ntoum and aligned 10°/40° windows halved modeled bytes without extra requests.
A 10° window crossing a new 60° longitude boundary instead needed two half-width chunks:
twice the requests, with modeled bytes equal to the original geometry.
Halving time helped the 30-day case but nearly doubled normal-window Ntoum requests,
126 to 245, with little byte saving. Halving latitude doubled requests for the aligned 10° case.
The balanced candidate produced modeled 4.7–9.2 MiB chunks while retaining the time-request cost.

The historical decision was to leave the live store unchanged and condition any future longitude
split on actual regional access envelopes. These estimates do not establish object-store performance,
the best geometry for another basin, or a present-day storage policy.

## Measurement qualifications

The probes exercised `DataCatalog.get_rasterdataset`. Direct xarray selection allowed dask to fuse
slicing into backend reads and concealed the behavior being investigated.
They checked module origins because an editable install could import the main checkout instead of
the worktree candidate. Comparing read/write paths with equivalent RSS instrumentation corrected
an initial attribution: observed memory growth belonged to reading, not uniquely to streaming writes.
These are limitations and corrections of this experiment, not new repository execution rules.
