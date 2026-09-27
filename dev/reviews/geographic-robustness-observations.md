# Geographic robustness observations

Working checklist: update items in place as fixes are verified. Git history retains the detailed run chronology. Checked items are resolved for this case; unchecked items remain open.

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
