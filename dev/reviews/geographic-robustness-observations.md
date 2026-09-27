# Geographic robustness test observations

Lifecycle: append-only. Record dated case runs, evidence, limitations, and subsequent dispositions without rewriting earlier findings. This is a manual test record, not a claim of scientific validation or a replacement for the task board.

## Recording convention

For each location, retain the toolbox revision, configuration and output roots, tested workflows, exact checks and outcomes, and remaining coverage. Classify observations as confirmed toolbox defects, configuration/data issues, improvement opportunities, or scientific limitations. Keep hypotheses explicit; a failed run alone does not establish its cause. Record fixes and rechecks as new entries. Run outputs and disposable diagnostics stay outside this tracked document.

## Liberia hydropower outlet — 2026-09-27

### Scope and starting state

- Toolbox revision: `32309c94`; session branch: `test/testing-experiments`.
- Configuration: `C:/Users/taner/workspace/cst-test-cases/liberia-hydropower-outlet/project_config.yml` and adjacent workflow files.
- Output root: `C:/Users/taner/workspace/cst-test-cases/runs/liberia-hydropower-outlet`.
- Supplied outlet: longitude -10.248, latitude 6.971, EPSG:4326; grid resolution 0.00833 degrees; `uparea: 100` is a delineation threshold, not a measured basin area.
- Historical forcing: ERA5 selected, CHIRPS precipitation comparison, requested 2000–2016. Scenario configuration: two realizations, two temperature levels by three precipitation levels plus the unperturbed baseline, 2040–2060; seed configured as `auto`.
- Purpose: exercise the existing toolbox at an external geographic location and identify portability, data, execution, and interpretation gaps. No observed discharge series is configured. No hydropower operation model or energy objective is defined; the case name alone does not make this a hydropower assessment.

### Evidence available before resuming

The WF0 log ends on 2026-09-27 at 01:49 after extraction, plotting and source comparison. Outputs include spatial geometries, a location registry, ERA5 and CHIRPS stores, and basin/subbasin comparison plots. This establishes artifact production; formal workflow completion remains to be checked through the owned runner. WF1–WF4 output directories and logs were absent at inspection.

Evidence: `logs/wf0_analyze_climate.log`, `data/spatial/location_registry.csv`, `data/climate/historical/comparison/dataset_comparison.{csv,md}`, and `config/runs/analyze_climate/run_record.yml`, relative to the output root.

### Initial observations

| ID | Classification | Observation and evidence | Disposition / next check |
|---|---|---|---|
| LIB-01 | Configuration/data issue; historical evidence | Case notes report that the initial WF0 attempt used missing P: catalog source names, corrected to `hydro_rivers_lin` and `globcover`. The current project config declares those names. The original failure has not been independently reproduced in this session. | Check WF1 against the same catalog; assess whether earlier source validation would make external-case setup clearer. No toolbox defect established. |
| LIB-02 | Scientific limitation / interpretation check | The registry maps the supplied outlet to `wflow_id=1010`, snapped to (-10.245833333487724, 6.970833333271244). Ten automatic outlets are also present. The log reports 322 river reaches and 11 locations. | Measure snap distance and basin drainage area; distinguish one supplied control point from ten generated locations. Geographic/site correctness remains unverified. |
| LIB-03 | Data coverage difference | ERA5 delivered 2000-01-02 through 2016-12-31; CHIRPS starts 2000-01-01. The WF0 log explicitly reports the missing first ERA5 day and uses the common interval for comparison. | Verify model forcing alignment and start-date handling. No silent truncation observed in WF0. |
| LIB-04 | Documentation / reporting opportunity | The external case's `notes.md` still reports WF0 extraction in progress, although later artifacts and logs show extraction and plot production. | Update the case run log after confirming completion. Consider a concise machine-readable workflow outcome/status summary if current run records do not expose it. |
| LIB-05 | Scientific limitation | No observed discharge is configured and the scenario set is small. A passing workflow run would demonstrate execution at this location, not hydrological skill, convergence, or hydropower performance. | Report robustness coverage and scientific limits separately. Expand geographic coverage through additional cases later. |
| LIB-06 | Reproducibility check | Generation uses `seed: auto`. | Capture the resolved seed and collection identity from the executed run; do not claim repeatable numeric comparisons from the configuration alone. |

### Session diagnostics

- `git status --short --branch`: clean at start, four commits ahead of local `main`.
- Direct `Get-CimInstance Win32_Process` previously returned access denied inside the Codex sandbox. A read-only query outside the sandbox succeeded. This is an execution-environment restriction, not evidence of a toolbox defect.
- Disposable session diagnostics: `.tmp/scratchpad/2026-09-27_0721/` in session-2; `.tmp` was confirmed ignored.

### Run continuation

Pending: confirm WF0 outcome, validate outlet/delineation, dry-run and execute WF1, then generate scenarios and simulate through the owned wrappers. Projection analysis remains an independent plausibility overlay and never supplies the generated stress scenarios.

### Continuation observations — 2026-09-27, morning

- Owned-wrapper WF0 and WF1 dry runs passed. The WF0 preview scheduled ten jobs, and WF1 initially nineteen, because `delineate_region` reported changed input provenance. The actual WF1 preparation subsequently scheduled only five jobs and reused the spatial/climate artifacts. This preview/execution difference is recorded for investigation; neither metadata cleanup nor reduced rerun triggers were used to suppress it.
- No live Python, Julia, Snakemake or Rscript processes were found in the elevated process check before the model launch. This check addresses concurrent writes to the shared external case root.
- WF1 preparation started through the owned wrapper with target `add_climate_forcing`, three cores, and `--notemp`. Scratch: `.tmp/scratchpad/2026-09-27_0721/wf1-prepare.log`. The first WF0 preview log is in `.tmp/scratchpad/2026-09-27_liberia/wf0-dryrun.log`; later diagnostics use the shared session scratch directory.

**LIB-07 — confirmed reporting defect: CHIRPS comparison metadata describes variables absent from the store.** The comparison CSV and Markdown say that temperature, radiation and pressure in the CHIRPS store come from ERA5. A direct `xarray.open_dataset` inspection of `data/climate/historical/chirps_20000101_20161231/extract_historical.nc` found only `precip`. The WF0 extraction log also describes retaining native precipitation only. `blueearth_cst/climate_analysis/compare_sources.py::_remarks` appends the ERA5-variable statement unconditionally for precipitation-only sources. This can mislead a forcing comparison. Recommended correction: describe variables actually present, and reserve the ERA5 augmentation statement for a store where augmentation has occurred. No source fix applied yet.

**LIB-08 — forcing sensitivity, not a defect.** Visual inspection of `comparison_precip_monthly_clim_line_basin_avg.png` shows CHIRPS wetter than ERA5 in July–September, with similar seasonal timing. This qualitative comparison is not a validation of either source. ERA5 remains the configured forcing for this execution test; no forcing selection decision for a real assessment is claimed.

### Synthetic observations — authorized fixture

The user explicitly requested synthetic observed discharge to test plotting and output artifacts. After the historical simulation produces discharge, create a deterministic fixture aligned to its timestamps and the supplied control outlet (`wflow_id=1010`), using the documented semicolon-delimited schema. Record the construction method, seed, units and source run. Synthetic scores must be interpreted solely as software test outputs; they cannot measure model skill. Keep the fixture clearly labeled in its filename and adjacent case notes. Exact fixture generation and plot checks are pending the historical output.

### WF1 coverage guard — 2026-09-27, 07:26

- Land/soil preparation, model parameterization, waterbodies and gauge/output setup succeeded. `add_climate_forcing` failed because the model's default simulation window was 2000-01-01 through 2016-12-31, outside the actual ERA5 store beginning 2000-01-02. Evidence: `wf1-prepare.log` in session scratch and `logs/_parts/1.09_add_climate_forcing.log` under the output root. No historical Wflow run had started.
- **LIB-03 disposition:** the model coverage guard works and prevents silent forcing truncation. The case-only workaround is an explicit model simulation window of 2001–2016 (16 complete years), excluding 2000 from the historical model run. Historical extraction remains 2000–2016 and the future scenario window remains 2040–2060. This is a configuration/data alignment issue, not evidence of an engine defect.
- **LIB-09 — workflow improvement opportunity:** the dry run passed, but actual stored forcing coverage was checked only after model preparation. Consider an early preflight comparing the effective model window with an existing store's time coverage, and suggesting the complete-year alternative. Do not weaken the guard or invent a missing climate day. The observation does not establish that the current year-only configuration should support daily endpoints.
- Basin area measured from the basin polygon with WGS84 geodesic area: 17,775.4118 km². Supplied-to-snapped outlet geodesic distance: 240.1295 m. This settles the size/distance checks in LIB-02; an independent check that this is the intended hydropower catchment remains outside the execution test.
- Environment observed outside the sandbox: HydroMT 1.3.1, hydromt_wflow 1.0.2, Snakemake 9.6.2, Julia 1.11.7. A sandbox-only import probe reported missing HydroMT despite successful execution outside the sandbox; that result is an environment-access issue and is not classified as a toolbox dependency defect.
- Model build emitted a warning that states data lacked a CRS and would be assigned the model CRS. No incorrect alignment has been demonstrated; retain it as a diagnostic observation rather than a confirmed defect.

### Resume and execution policy — 2026-09-27, 07:28

- A first attempt to activate the case's simulation window did not change the file because the text replacement assumed CRLF while the file used LF. The repeated coverage failure was an agent editing error, not a toolbox defect. The corrected file was inspected before retrying: active `simulation_window: {start: 2001, end: 2016}`. The owned runner then captured execution configuration `build_model/0d6364aa9989/`.
- **LIB-10 — observed rerun scope / optimization opportunity:** changing only the model simulation window scheduled all five model-preparation jobs again, including land/soil and model parameterization. Climate/spatial outputs were retained. Investigate whether individual preparation rules can depend on narrower configuration projections without compromising provenance; unnecessary work has not yet been established by a rule-by-rule dependency audit.
- The user authorized continuation through workflows without intermediate approvals. Routine future execution handoffs should use lower-tier models, low effort and narrow targets. Stop after three consecutive failures of the same blocker without new evidence; preserve logs and recoverable outputs.
- Synthetic fixture recipe prepared and syntax-checked with `pixi run python -m py_compile .tmp/scratchpad/2026-09-27_0721/create-synthetic-observations.py` (passed). Planned construction: outlet `1010`, two-day lag, multiplier 1.08, mean-one lognormal noise with sigma 0.12 and seed 27092026, missing every 97th row and 2008-07-01 through 2008-07-07. Retain source and fixture hashes in an adjacent JSON file. Generation still awaits the exported historical discharge table.

### WF0 outcome and WF1 preparation — 2026-09-27, 07:32

- The existing invocation history records the actual WF0 run as `succeeded`, exit code 0, ending 2026-09-26T23:49:33Z (2026-09-27 01:49 local). Thus WF0 completion is confirmed beyond artifact presence. Existing invocation JSON records under `config/runs/_engine/invocations/` already expose workflow outcomes; LIB-04 does not justify inventing a second status mechanism. A concise reader/view and an updated external case note may suffice. Dry-run records must be distinguished from actual execution when reading this history.
- Corrected WF1 preparation succeeded at 07:31:14 local, 3m37s elapsed. The log reports forcing added for 2001-01-01 through 2016-12-31 in `models/hydrology/wflow/forcing/inmaps_historical.nc`. This confirms the coverage workaround, not historical engine completion.
- Exact preparation command: `pixi run python scripts/run_workflow.py build_model --config C:/Users/taner/workspace/cst-test-cases/liberia-hydropower-outlet/project_config.yml --project-dir C:/Users/taner/workspace/cst-test-cases/runs/liberia-hydropower-outlet --cores 3 --target add_climate_forcing -- --notemp`; corrected attempt log: `.tmp/scratchpad/2026-09-27_0721/wf1-prepare-fixed.log`.

### Model structure and smoke — 2026-09-27, 07:33

- The generated forcing has 5,844 daily timestamps (2001-01-01 through 2016-12-31), on a 231 × 223 grid matching staticmaps. The model uses a cold start. A separate seven-day, single-thread smoke test was started using a scratch TOML and separate `run_smoke` outputs; the production TOML was retained. Structural probe evidence: `.tmp/scratchpad/2026-09-27_0721/model-structure.log`.
- **LIB-11 — confirmed inconsistent forcing metadata; cause not established:** generated `temp` and `pet` variables retain DEM/geopotential metadata (`standard_name=geopotential`, `long_name=mean land-surface elevation`, `units=m`) while their `unit` attributes identify temperature/PET units. This is contradictory descriptive metadata. It does not by itself establish incorrect numerical values or an engine conversion error. Investigate the local climate-transform/forcing writer and its upstream outputs; correct metadata in the toolbox's owned layer if required, never patch installed HydroMT/Wflow packages. No source change applied.

### Smoke success and plotting coverage — 2026-09-27, 07:35

- Seven-day single-thread engine smoke passed, exit code 0, engine elapsed 41s. Separate `models/hydrology/wflow/run_smoke/output.csv` was 5,130 bytes; states and logs were retained. Evidence: session scratch `wflow-smoke.{toml,log}`. Smoke output is diagnostic only and must not substitute for the historical production run.
- Full WF1 launched with the owned runner and `--notemp`; log `.tmp/scratchpad/2026-09-27_0721/wf1-historical.log`. Basin plotting produced 11 figures and forcing plotting 9 figures while historical simulation remained active. The outlet index identifies one supplied control station; this does not negate the registry's additional automatic outlets.
- **LIB-12 — confirmed categorical map coverage gap:** the GlobCover-backed raster carries codes `[110, 120, 130, 140, 160, 210]` absent from the active category style. `cartographic_map.py` emitted a RuntimeWarning and explicitly drew them as unclassified. This loses land-cover distinctions on the map but is not evidence that model parameterization failed. Check source-specific legend/style selection and the fraction of affected valid cells before proposing a correction. Evidence: the warning in `wf1-historical.log`; relevant artifact: `data/spatial/plots/`.
- The external `cst-test-cases` checkout already contains unrelated deleted/untracked case files, and the Liberia folder is untracked. Preserve all of that state. This session's tracked observations are committed only in the toolbox branch; external fixture/config changes remain local unless separately saved in their owning repository.

Visual follow-up for LIB-12: `land_cover.png` was rendered and inspected. Its footer identifies `globcover`, whereas `plot_spatial_maps.py::LAND_COVER_CLASSES` is documented as the CGLS-LC100 code/color table and assigned unconditionally to the land-cover figure. This establishes a source/style mismatch beyond the missing-code warning. Shared numeric codes could also receive misleading category names; verify those against the source's own mapping before quantifying mislabeling. The map's “Unclassified” legend reports the six missing codes, so that omission is visible rather than silently hidden.
