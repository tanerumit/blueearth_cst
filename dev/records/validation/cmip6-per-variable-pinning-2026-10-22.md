# CMIP6 per-variable pinning verification

Retained acceptance and performance evidence for t2610130703. Current behavior is documented in
[CMIP6 source readability](../../reference/wf2-cmip6-source-readability.md).

Candidate: commit 7228cf5d on fix/t2610130703, based on cf1519bb9fc9fb41473757ee09bcf18786bb8d18.
Date: 2026-10-22 Europe/Amsterdam. Source: session-1; runtime: compatible session-2 Pixi environment.
No dependency/environment changes. This record preserves the acceptance results after task closure;
it does not claim integration or publishing. Logs and local output names below refer to the original
session-1 scratch directory `.tmp/tasks/t2610130703/`, retained for coordinator review. Bulk outputs
and disposable probes are not committed. The record remains readable without that scratch directory.

All Python commands used this prefix from session-1:

```powershell
& "$runtime/.pixi/envs/default/python.exe" -B dev/scripts/session_runtime.py --runtime-root $runtime --
```

Here `$runtime` identifies the compatible, owner-maintained session-2 checkout; it is not an installation
instruction. Source imports and outputs were checked to remain in session-1.

## Checks

- `python -m pytest tests/test_series_identity.py tests/test_fetch_gcm_raw.py tests/test_resolution.py -q`:
  224 passed, 7 existing calendar/xarray warnings; `tests-final.log`.
- `python -m pytest tests/test_get_stats_climate_proj.py tests/test_get_change_climate_proj.py tests/test_get_change_climate_proj_summary.py tests/test_stage_cmip6.py -q`:
  58 passed; one process-pool test failed on sandbox named-pipe permissions, `consumer-tests.log`.
- `python -m pytest tests/test_stage_cmip6.py::test_the_worker_pool_round_trips_and_reports_every_failure -q`:
  1 passed outside sandbox, `process-test.log`. Combined consumer coverage: 59 passed, none skipped.
- Scoped `ruff check` and `ruff format --check` on the three changed modules and three changed test files:
  passed. `git diff --check`: passed.
- `python scripts/run_workflow.py analyze_projections --config .tmp/tasks/t2610130703/project_config_live.yml --project-dir .tmp/tasks/t2610130703/wf2-run --cores 2 --dry-run`:
  passed, 14 jobs planned, `wf2-dry-run.log`.
- Same WF2 command without `--dry-run`: passed after setting process-local `PYTHONUTF8=1`, 3:02,
  26/26 requested outputs, 2/2 model combinations resolved, `wf2-live-utf8.log`.
  Initial execution hit the existing Windows cp1252 output relay limitation (`wf2-live.log`);
  the successful invocation resumed the same task-owned root after delineation.
- `python .tmp/tasks/t2610130703/check-old-cache.py`: passed, `old-cache.log`.
  A disposable copy of a pre-existing GFDL historical raw slice retained its digest and SHA-256 bytes.
- `python .tmp/tasks/t2610130703/check-products.py`: passed, `products.log`.
  Four raw slices and four scalar series; 780 historical/1032 scenario months; schema 6, noleap;
  selected raw source paths and derived-series raw digests checked. Scalar files retain the existing
  source-inventory attribute, with the exact selected-path attribute owned by the raw artifact.

## Live source and numerical evidence

The July 29 index contains FIO pr gn/v20191209 and tas gn/v20191115. Both exact public GCS metadata URLs
returned HTTP 200 under normal user permissions. Sandbox proxy refusal was not source unavailability.
Live reads of both variables subsequently succeeded.

`python .tmp/tasks/t2610130703/live-check.py` reads the WGS84 rectangle (9.5, 0.3, 9.8, 0.6) with one-cell
buffering, historical 1950–2014. Its independent xarray Zarr reader selects the actual cell coordinates
and applies only source-unit conversion, without HydroMT or the production merge/selection functions.
All 4,680 values per variable per model matched exactly: maximum absolute error 0, both original and
revised fetchers. Before/after arrays also matched exactly. Test tolerance was rtol=1e-6, atol=1e-5.

| Source | Original uncached | Revised uncached | Revised cache |
|---|---:|---:|---:|
| TaiESM1 | 46.622 s | 48.700 s | 0.059 s |
| FIO-ESM-2-0 | 29.010 s | 41.782 s | 0.022 s |

Original reader: fetch module exported from cf1519bb9fc9fb41473757ee09bcf18786bb8d18,
activated with process-local `CMIP_BASELINE_READER=1`.
Separate `before-*.nc` outputs; see `before-benchmark.log` and `before-live-results.json`.
The first ordinary read is in `live-check.log`; successful FIO read in `live-check-final.log`.
Later invocations reused the ordinary file, so their `read_seconds` is a cache measurement, not a fresh read.
Single samples, differing network/cache state and concurrent work: no statistical speedup claim.
The split path adds separate opens and calendar validation and was slower in this measurement.

Early FIO trials exposed scalar height-coordinate differences; the final guard compares dimension
variables rather than auxiliary coordinate context. Regression coverage includes that valid case.
The live standalone process emitted upstream fsspec/aiohttp shutdown warnings after successful assertions
and exited 0; no upstream package was patched.

## Scope and limitations

No Snakefile edits, global schema bump, generated catalog/index edits, or environment mutations.
Ordinary identity/cache recipes are unchanged; only split-version sources gain per_variable_sources.
Rejections cover competing grids, shifted spatial/time coordinates, incompatible CRS/calendars,
and existing duplicate/empty-time guards. No regridding/interpolation is introduced.

WF2 used rapid periods with TaiESM1/FIO and a freshly delineated basin, not production outputs.
17 figures rendered; 2 explicitly skipped for one member/one future window. Figures were not visually
qualified because plotting behavior is unchanged. WF0/WF1/WF3/WF4, full-suite, installation and baseline
numerical qualification were not run or claimed. No stale fixture was used for numerical acceptance.
Integration, board closure and publishing are separate from the implementation verification above.
