# Stall evidence (2026-10-06)

Last scheduler rows before each stall, copied from the session-1 scratch logs. In both cases the
in-flight jobs had already written their outputs and per-job logs (21:44-21:46 and 22:41-22:42), while
Snakemake had no child processes and accrued no CPU.

## Stall 1 (run started 21:15, 256 jobs)

```text
21:43:33 - DONE Rule 2.03: fetch_cmip6_projections  [series cmip6_NCAR_CESM2_historical_r1i1p1f1]  0:01:00  [job 113/256]
21:43:33 - RUN  Rule 2.04: reduce_to_basin_averages  [CESM2 historical r1i1p1f1]
21:43:41 - DONE Rule 2.04: reduce_to_basin_averages  [series cmip6_NCAR_CESM2_historical_r1i1p1f1]  0:00:08  [job 114/256]
21:43:41 - RUN  Rule 2.03: fetch_cmip6_projections  [MPI-ESM1-2-LR ssp126 r5i1p1f1]
21:44:05 - DONE Rule 2.03: fetch_cmip6_projections  [series cmip6_AWI_AWI-CM-1-1-MR_ssp585_r1i1p1f1]  0:01:21  [job 115/256]
21:44:05 - RUN  Rule 2.04: reduce_to_basin_averages  [AWI-CM-1-1-MR ssp585 r1i1p1f1]
21:44:16 - DONE Rule 2.04: reduce_to_basin_averages  [series cmip6_AWI_AWI-CM-1-1-MR_ssp585_r1i1p1f1]  0:00:10  [job 116/256]
21:44:16 - RUN  Rule 2.03: fetch_cmip6_projections  [CanESM5 ssp370 r12i1p1f1]
```

## Stall 2 (resumed run started 22:06, 140 jobs)

```text
22:40:35 - DONE Rule 2.04: reduce_to_basin_averages  [series cmip6_CMCC_CMCC-ESM2_ssp370_r1i1p1f1]  0:00:18  [job 118/140]
22:40:35 - RUN  Rule 2.03: fetch_cmip6_projections  [CanESM5 ssp585 r12i1p1f1]
22:40:39 - DONE Rule 2.03: fetch_cmip6_projections  [series cmip6_MPI-M_MPI-ESM1-2-LR_ssp245_r5i1p1f1]  0:01:32  [job 119/140]
22:40:39 - RUN  Rule 2.04: reduce_to_basin_averages  [MPI-ESM1-2-LR ssp245 r5i1p1f1]
22:40:57 - DONE Rule 2.04: reduce_to_basin_averages  [series cmip6_MPI-M_MPI-ESM1-2-LR_ssp245_r5i1p1f1]  0:00:18  [job 120/140]
22:40:57 - RUN  Rule 2.03: fetch_cmip6_projections  [MPI-ESM1-2-LR historical r1i1p1f1]
22:41:18 - DONE Rule 2.03: fetch_cmip6_projections  [series cmip6_MPI-M_MPI-ESM1-2-LR_ssp126_r3i1p1f1]  0:01:37  [job 121/140]
22:41:18 - RUN  Rule 2.04: reduce_to_basin_averages  [MPI-ESM1-2-LR ssp126 r3i1p1f1]
```
