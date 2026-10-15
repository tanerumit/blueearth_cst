# Local-input all-workflow E2E qualification — 2026-10-15

The rapid local-input gate was qualified against an acquisition-inclusive run on Windows in
`session-1`, using the implementation tree `26f3ed06207a55579fab5e2789d944bb2d690c1e`
(`fb777b5e` before synchronization with later board commits). Both runs used fresh project roots,
the owned all-workflow runner and shared deliverable assertions. No baseline numerical claim is made.

The local source bundle was `C:/data/blueearth-cst-e2e/rapid-v3`. Its `bundle.json` SHA-256 was
`cfcc2dda3078a05131c7a1487e00db56bc078cbd1394a53b5500c712f0663a5e`. The seal inventories
97 HydroMT source outputs and four CMIP6 raw slices, including the native 1999-12-31 CHIRPS day
needed for the full 2000–2016 extracted window. The four raw slices share the local polygon fingerprint
`d08443021d9f4a5c375e9c0b566a3a6ada05f985927a0f16a85f22d4728f1d0c`; the live polygon
fingerprint was `be6ed1c802bad992751209df2e713fb105cf68b1fdaa0ab64549e3e34a7cefa1`.
Their symmetric-difference area was `3.15e-15` degree², about `1.77e-13` of basin area.

| Gate | Result | Duration |
|---|---:|---:|
| `pixi run test-e2e` | passed | 47m47s |
| `pixi run test-e2e-local` | passed | 16m19s |

The fresh output roots were:

```text
.tmp/pytest/run-13f565092236446db27bae0186dc1406/test_all_five_workflows_run_en0/project
.tmp/pytest/run-6e0b3fefa8cb4fd2805d92691bd2deaa/test_all_five_workflows_run_fr0/project
```

| Workflow | Live | Local |
|---|---:|---:|
| WF0 climate | 16m29s | 3m32s |
| WF1 model | 9m35s | 3m21s |
| WF2 projections | 3m54s | 0m59s |
| WF3 scenarios | 1m56s | 0m56s |
| WF4 simulation and metrics | 12m56s | 5m35s |

The observed end-to-end speedup was 2.9×, or 66% less elapsed time. The runs were consecutive;
warm operating-system, Pixi and Julia caches also contributed, so the full difference is not
attributable to source staging. Live WF0 ERA5 and CHIRPS extraction alone took 6m21s and 8m40s;
local source reads completed much faster. The local WF2 reused all four raw slices without fetching.

Independent output comparison found numerically identical ERA5 and CHIRPS historical extracts,
annual CMIP6 change factors, and all ten scenario series. Historical discharge differed by at most
`1e-5` in three rounded CSV columns. Among six retained indicator tables, one AET annual total was
`1084` locally versus `1085` live (`run_07`, location `1030`), and one discharge annual p95 was
`5.534` versus `5.533` (`group_02`, location `1010`). All other compared indicator values matched.
This is close numerical agreement, not byte identity; separately staged spatial inputs produced
different model and response identity digests.

Focused fetch, bundle, runner, CMIP staging and catalog-root tests passed: 201 tests. `pixi run lint`,
`pixi run format-check`, and `git diff --check` passed on the implementation. The first live attempt
failed at a CHIRPS HDF read; the successful live run used `HDF5_USE_FILE_LOCKING=FALSE`. The earlier
local bundle omitted the CHIRPS boundary day and yielded only 16 common reporting years. The sealed
bundle above and the shared E2E assertions now require all 17 years and 6210 extracted days.
