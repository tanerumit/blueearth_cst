# Geographic robustness observations

Working checklist: update items in place as fixes are verified. Git history retains the detailed run chronology. Checked items are resolved for this case; unchecked items remain open.

## Chuzaco, Colombia — started 2026-09-27

- Case: `C:/Users/taner/workspace/cst-cases/applications/colombia-chuzaco`; outputs: `C:/Users/taner/workspace/cst-cases/runs/colombia-chuzaco`. Toolbox `e836fb06`, session-2 / `test/case-studies`, three cores.
- Supplied region: `{'subbasin': [-73.73, 4.638], 'uparea': 30}`. Delineated WGS84 geodesic area 61.3490 km²; outlet snapped 107.7347 m. One subbasin, one river reach at the default 32 km² threshold, primary control `1010`.
- Current shipped templates retained: 1990–2020 climate/historical record, ERA5 selected, two realizations, 2 temperature × 3 precipitation levels plus baseline (14 runs), 2040–2060 scenario period, three CMIP6 models / two SSPs / near and far horizons, discharge/AET outputs, automatic compute sizing. No compact variant.
- **CHU-01 — Local coverage:** WF0 dry-run passed, actual default local catalog failed at basin-index selection (`NoDataException`). The local raster store contains small staged extracts. Required change: global P-drive Deltares catalog, its river/LULC names `hydro_rivers_lin`/`globcover`, and the shipped ERA5 Zarr override retaining the requested 1990–2020 record. Global delineation passed.
- **CHU-02 — CHIRPS geography:** P-drive `chirps` is Africa-only; failed bbox clipping for Colombia. Changed comparison source to supported `chirps_global`; ERA5 remains selected. No comparison source dropped.
- Synthetic fixture is independent artificial discharge, not measured data or a model-skill benchmark: 11,323 positive daily rows, 1990–2020, m³/s, seed 27092026, seasonal signal plus correlated lognormal variability. Formula and generator retained beside the CSV; registry `1010` matches its header. Synthetic input exercises evaluation metrics/plots only.
- Verification: all five corrected workflow configs passed `load_composed_config`; both WF0 dry-runs passed; PowerShell parser checks passed for generator/continuation; regenerating the synthetic CSV matched its recorded SHA-256. Hydrography raster is 13 × 9 cells; active model-cell count remains pending model construction. No toolbox code was changed, so no software suite or baseline comparison was run.
- **CHU-03 — Continuation launcher:** first detached supervisor did not wait for the existing process and was refused by `archive_lock` before workflow launch. Corrected supervisor waits on parent invocation `e0546c96fee44238a95e445e17438970`; no unlock or termination. Operational launcher issue; no toolbox fix claimed.
- At launch handoff: the original WF0 attempt was finishing its ERA5 netCDF write after the Africa-only CHIRPS failure. Hidden continuation PID is recorded in `run-evidence/continuation-status.json`; it waited for that invocation to finish, then executed the corrected full WF0–WF4 sequence and appended terminal workflow statuses to case `notes.md`. WF1–WF4 had not yet executed. The pinned worktree had to remain in place while the continuation ran.
- Evidence: `run-evidence/wf0-dry-run.log`, `wf0-pdrive-dry-run.log`, `wf0-to-wf4.log` (local failure), `wf0-to-wf4-pdrive.log` (Africa-only CHIRPS failure), `wf0-to-wf4-global.log` (launcher lock refusal), and `wf0-to-wf4-global-v2.log` (corrected continuation, completed successfully). Toolbox invocation records remain under `config/runs/_engine/invocations/`.
- Current status (2026-09-28): `continuation-status.json` reports `passed` (exit 0); the corrected log reports WF0–WF4 completed and parent invocation `b61b386ff4aa431ebca1d1d728951462` succeeded. Next inspect historical evaluation sheets, ready collection, retained responses, and complete discharge/AET metric tables. Pipeline completion alone is not scientific validation.

## Completed geographic areas — diagnostic register

Updated 2026-09-27. Completion refers to the recorded test scope, not scientific validation. `Not identified` means the area was reported by the user but its run folder has not been matched.

| Area / representative run | Basin area (km²) | Active model cells / raster size | Historical daily steps (forcing / response) | Scenario daily steps per run (forcing / response) | Coverage |
|---|---:|---|---|---|---|
| Ntoum, Gabon — `gabon-ntoum-v3`, 2026-09-25 | 219.7 | 257 / 16×24 | 6,210 / 6,209; 2000–2016 | 7,671 / 7,670; 2040–2060 | WF0–WF4 passed; 14 scenarios |
| Libreville + SP2 | Not identified | Not identified | Not identified | Not identified | Completed area reported by user; run identity/diagnostics pending |
| Liberia — `liberia-hydropower-outlet`, 2026-09-27 | 17,775.4 | 20,983 / 231×223 | 5,844 / 5,843; 2001–2016 | 1,096 / 1,095; 2040–2042 | WF0–WF3 and 14 simulations passed; AET/recharge metrics only |

Model resolution is approximately 0.008333° in both verified cases. Active cells count positive subcatchment-mask cells, not the rectangular raster. Areas are WGS84 geodesic polygon areas. Response rows start one day after forcing (interval-end convention). Each scenario set has two realizations × (2 temperature × 3 precipitation levels + baseline).

### Recorded workflow runtimes

Elapsed wall time; not sums of rule benchmarks. Both verified runs used three cores. These are observed executions, not controlled performance comparisons. Partial and cached runs are labelled; failed/no-op attempts are not folded into successful totals.

| Area | WF0 | WF1 | WF2 | WF3 | WF4 |
|---|---|---|---|---|---|
| Ntoum v3 | 2m41s | 2m35s | 4m59s | 1m41s | 7m25s |
| Libreville + SP2 | Not identified | Not identified | Not identified | Not identified | Not identified |
| Liberia | 1h58m53s | Preparation 3m41s + resumed run 12m17s | Cached repair rerun 46s | 2m43s | 48m38s through failed default metrics; compact metrics-only 1m09s |

- **Ntoum:** first recorded full pipeline invocation took 19m23s; later reuse invocations excluded. Source: `C:/Users/taner/workspace/cst-test-cases/runs/gabon-ntoum-v3/config/runs/_engine/invocations/`, parent `92fd71ea6c964c7ab450a7f11d2b6bea`; polygon and model mask under that output root.
- **Liberia:** WF1 historical engine alone 11m44s; WF4 engine batch alone 44m19s. WF2's earlier fetch/reduction attempt took 4m24s and failed at provenance; the 46s repair reused those sources. Runtime scopes are not interchangeable with a fresh end-to-end run.
- **Follow-up:** identify Libreville + SP2 output root and populate its diagnostics. For future cases record run date/revision, core count, reused inputs and metric coverage alongside timings.

## Liberia — current status (2026-09-27)

| Workflow / check | Result |
|---|---|
| WF0 historical climate | Passed; ERA5/CHIRPS comparison |
| WF1 historical model | Passed, 2001–2016; 5,843 daily rows at 11 locations |
| Synthetic observation plots | Passed; four outlet sheets inspected |
| WF2 projections | Passed after LIB-16 fix; 864 monthly / 72 annual rows, six figures |
| WF3 generation | Passed; 14 scenarios, 17 diagnostic figures |
| WF4 simulations | All 14 passed; retained inventory verified |
| WF4 metrics | AET/recharge passed: 308 finite results; discharge metrics incomplete (LIB-18) |

## Fixed / resolved

- [x] **LIB-01 — Catalog names:** corrected case sources to `hydro_rivers_lin` / `globcover`; model build passed. Configuration issue.
- [x] **LIB-03 — Missing ERA5 first day:** explicit model window 2001–2016 avoids missing 2000-01-01. Coverage guard retained; extraction remains 2000–2016.
- [x] **LIB-04 — Stale case status:** external case notes updated; existing invocation records already expose outcomes.
- [x] **LIB-06 — Reproducibility:** collection `4e097bef80e7`, seed `1026957974`, runs `01`–`14` recorded.
- [x] **LIB-16 — WF2 `KeyError: 'dataset'`:** resolve tidy `model` through composition; count each flagged month once across statistics. Commit `de00f1b0`; 57 focused tests and actual WF2 rerun passed.
- [x] **LIB-17 — WF4 longitude/grid rejection:** preflight now uses HydroMT's normal spatial selection and wrapping before the unchanged guard. Commit `3ea0fc77`; 19 focused tests, all downscales and simulations passed.

## Open defects

- [ ] **LIB-07 — CHIRPS remarks:** report claims ERA5 temperature/radiation/pressure are present, but store contains only precipitation. Make `compare_sources.py::_remarks` describe actual contents.
- [ ] **LIB-11 — Forcing metadata:** temperature/PET retain DEM descriptions and `units=m`, in historical and scenario forcing. Trace writer and correct attributes; incorrect numerical values or engine conversion are not established.
- [ ] **LIB-12 — Land-cover legend:** GlobCover raster receives CGLS-LC100 styles; codes 110/120/130/140/160/210 appear unclassified. Select source-specific styles; quantify affected cells and check shared-code labels.
- [ ] **LIB-15 — Scatter sample count:** outlet performance sheet shows 5,478 timestamps rather than 5,414 finite pairs. Count the pairs actually plotted; no metric-value error demonstrated.

## Improvements to investigate

- [ ] **LIB-09 — Earlier forcing coverage check:** detect missing dates before expensive model preparation, retaining the existing guard.
- [ ] **LIB-10 — Rerun scope:** window/observation changes schedule broader preparation work. Audit dependencies before narrowing them; unnecessary work is not yet proven.
- [ ] **LIB-13 — Map collisions:** scale bar overlaps outlet `1010`; nearby labels crowd. Use Liberia as a layout regression case.
- [ ] **LIB-14 — Redirected progress:** intermediate frames are deliberately suppressed off-terminal. Add a concise status/heartbeat option; quiet logs or zero-byte outputs alone must not trigger termination.
- [ ] **LIB-18 — Metric/window preflight:** default 10-year return level needs 10 annual blocks; compact test has six. Check this before simulation. Guard works; it must not be weakened.
- [ ] **Metric selection:** selection is by variable, so excluding the unsupported return level currently excludes all discharge metrics. Consider individual metric selection.
- [ ] **Plot provenance:** identify synthetic observations on exported sheets; clarify weather-generator figure units and colour meanings.
- [ ] **Calendar provenance:** document how HydroMT populates leap days during noleap-to-engine-calendar conversion; current record names the conversion only.

## Coverage gaps / interpretation

- [ ] **Discharge metrics:** native responses retained, but no discharge metric set published. Run a sufficiently long period or implement reviewed finer metric selection.
- [ ] **Full scenario period:** 2040–2060 definition preserved; only 2040–2042 executed. Long-period behaviour untested.
- [ ] **LIB-02 — Intended catchment:** measured area 17,775.4 km² and snap distance 240.1 m; independently confirm the intended hydropower catchment. Control ID `1010`, plus ten automatic outlets.
- **LIB-05 — Scientific scope:** software robustness test; no measured discharge, calibration, convergence assessment or hydropower operations model.
- **LIB-08 — Forcing sensitivity:** CHIRPS appears wetter than ERA5 in July–September; this does not validate either source. ERA5 remained selected.
- Weather-generator diagnostics sampled 25 of 38 basin cells; explicitly reported memory cap.
- Synthetic fixture: outlet `1010`, two-day lag, ×1.08 bias, lognormal noise σ=0.12, seed `27092026`, 68 missing values. Method, units and hashes are in its adjacent JSON; fit scores are testing outputs.

## Case and evidence

- Branch: `test/testing-experiments`; fixes committed, no landing/push.
- Case root: `C:/Users/taner/workspace/cst-test-cases/liberia-hydropower-outlet`.
- Output root: `C:/Users/taner/workspace/cst-test-cases/runs/liberia-hydropower-outlet`.
- Test configs: `project_config_testing.yml`; phase configs `project_config_testing_wf3.yml`, `project_config_testing_wf4.yml`, `project_config_testing_metrics.yml`.
- Completed experiment: `liberia_hydropower_outlet_20260927_gridfix`. Earlier failed frozen experiment preserved.
- Published compact metrics: `experiments/liberia_hydropower_outlet_20260927_gridfix/results/metric_sets/b4ef9a4c8399/`; AET/recharge each 154 finite rows, 14 groups × 11 locations. Request selects `[aet, gwr]`.
- Native responses: 14 CSVs, each 1,095 rows covering 2040-01-02–2042-12-31; inventory contains 462 q/AET/recharge series.
- Verification: focused regressions, lint/format checks, actual runs, inventory and finite-value checks passed. WF4 batch took 44m19s; compact metrics took 40s. No unrelated full suite/baseline rerun.
- Detailed records: output-root `config/runs/_engine/invocations/`, experiment `_engine/`, and `logs/_parts/`. Disposable session logs: `.tmp/scratchpad/2026-09-27_0721/` (`wf2-fixed-execute.log`, `wf4-gridfix-execute.log`, `wf4-compact-metrics-execute.log`).
