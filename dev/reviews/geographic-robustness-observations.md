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

**LIB-13 — visual layout issue:** in the inspected `land_cover.png`, the lower-left scale bar and its 25 km tick label overlap the supplied outlet marker/label near `1010`; nearby outlet labels are also crowded. This makes the main control point harder to read on this elongated basin. Record this case as a collision/layout regression example for future map tests. No map-layout source change applied.

### Historical interruption and corrected diagnosis — 2026-09-27, 07:45

The first full historical attempt was stopped at 07:44:58 after 616.4s wall time because no live progress was visible and the discharge/log files remained zero bytes. Termination then flushed a progress row at **81.1%**, ETA 2m23s. The simulation had been advancing. The lack of visible output did not establish a hang, and the agent-imposed ten-minute visibility bound interrupted useful work. Prepared forcing/model artifacts were retained; no exported full discharge table was produced.

**LIB-14 — confirmed progress-visibility gap; buffering cause inferred:** under the owned historical wrapper, intermediate progress was not visible during this attempt, while a direct seven-day smoke exposed progress and completed. Progress became visible when the historical child was stopped. The relay consumes raw frames, so missing literal frame lines cannot establish which engine stage was active. Determine the buffering/relay cause before proposing a fix. A zero-byte native output file is not a reliable no-progress test for this engine. Evidence: `wf1-historical.log`, including the delayed 81.1% row; comparison: `wflow-smoke.log`.

New progress evidence justifies one retry with a twenty-minute wall-clock bound, avoiding another stop based solely on output size or absent raw progress frames. The retry is delegated as a single command execution to `model-builder`, requested model `gpt-6-sol`, low effort, with no source/config edits. Subsequent phases remain pending that result.

Source follow-up for LIB-14: `run_log_core.py::run_and_tee` deliberately suppresses intermediate progress frames off a terminal (`stream_frames` false) and emits the finished bar as an ordinary row. The historical command was redirected to a file, whereas the direct smoke log retained raw frames. Consequently, “buffering bug” is not an established diagnosis. The confirmed gap is monitorability of redirected long runs; a periodic status snapshot or explicit nonterminal progress option could address it without flooding logs. A future timeout must account for this output contract and a realistic period-dependent runtime.

### Bounded future-simulation variant — 2026-09-27, 07:53

The measured historical runtime implies several hours for the full template's fourteen 21-year future runs. For this manual functionality exercise, a separate continuation variant was created, preserving the original project/generation files:

- `liberia-hydropower-outlet/project_config_testing.yml`: WF0/WF1 disabled because executed separately; WF2/WF3/WF4 enabled.
- `liberia-hydropower-outlet/project_config_testing_generate_scenarios.yml`: generation/simulation period 2040–2042, retaining both realizations, all six perturbation combinations and the unperturbed baseline (expected fourteen scenario runs).
- All other case inputs and original projection settings remain as declared. No toolbox source or global runtime setting was changed.
- Coverage explicitly omitted by this variant: eighteen future years, 2043–2060, and their long-period numerical/trajectory behavior. This variant cannot validate the original 21-year study period. The historical model run still covers 2001–2016.
- Creation used `.tmp/scratchpad/2026-09-27_0721/create-testing-variant.py`, which parsed and checked the written settings, refused existing target files, and preserved YAML comments. Command: `pixi run python .tmp/scratchpad/2026-09-27_0721/create-testing-variant.py` (passed).

This is a time budget for workflow/plot coverage, not a scientific sufficiency claim. The full-period definition remains available for a later longer test.

### Historical success and synthetic fixture — 2026-09-27, 08:00

- Full WF1 retry succeeded, exit 0, in 737.54s wall time. The historical simulation benchmark reports 703.95s wall time and 1,648.61 CPU seconds. Evidence: `.tmp/scratchpad/2026-09-27_0721/wf1-historical-retry.log` and the WF1 benchmark artifacts. This supersedes the interrupted attempt as the executed result.
- `models/hydrology/wflow/run_default/output_q.csv`: 633,259 bytes, 5,843 rows, 2001-01-02 through 2016-12-31; columns `time,1010,1020,1030,1040,1050,1060,1070,1080,1090,1100,1110`. Wflow's output begins after its initial timestamp; it has one fewer daily output than the forcing input. No unexpected truncation is inferred from that difference.
- Without observations, evaluation produced two basin-average figures and eleven station hydrographs; the metrics CSV contained no metrics, as explicitly reported in the log.
- Synthetic fixture created: `liberia-hydropower-outlet/data/synthetic-observed-discharge.csv`, with adjacent `.json` provenance. It has 5,843 timestamps, 68 missing observations, outlet `1010`, units m³/s, seed 27092026, and the deterministic lag/bias/noise method described above. Source hash: `04ebf8c6762197a746d8c8bdc0784cd9cf51a8fadad43adf0aaee79e7a88c9dc`; fixture hash: `24a820373037409904e54063e8de6a118a352429bd5b6e140be24c6b7c3062f1`. NumPy 2.4.6. The case observations key was set to the fixture's absolute path with a synthetic-test comment.
- The synthetic evaluation preview passed but scheduled ten jobs from changed `delineate_region` input provenance. Physical basin, forcing, simulation window and engine settings were unchanged by adding observations. A focused evaluation rerun was launched through the owned wrapper with `--target plot_model_evaluation -- --notemp --allowed-rules plot_model_evaluation`, retaining the completed historical responses and exposing observation joins/signatures/metrics. This is a plotting check, not an end-to-end rerun of the new observation configuration.

### Synthetic evaluation outcome and visual QA — 2026-09-27, 08:03

- Focused evaluation passed, exit 0, 26s wrapper elapsed. It rendered the observation-dependent hydrograph, performance, high-flow and low-flow sheets for `1010`; the other ten locations correctly reported no observations and rendered hydrographs only. Metrics include all seven metrics at daily and monthly scale (fourteen values), with no blank values in the displayed table. These synthetic-fit scores are software-test outputs only.
- Rendered and inspected `evaluation/plots/stations/hydrograph_1010.png`, `performance_1010.png`, `signatures_peaks_1010.png`, and `signatures_lows_1010.png`. Sheets have readable identities, legends, axes and panel layouts; the warm-up exclusion is visible as 2002–2016. The fixture exercises missing observations and the user-control ID join. No performance-sheet table clipping was observed in these renders.
- **LIB-15 — confirmed scatter sample-count reporting defect:** `performance_1010.png` labels the daily scatter `n = 5,478`, the total simulated evaluation timestamps. The synthetic observations contain missing values, so fewer finite pairs are plotted and used for R². `plot_evaluation.py` displays `simulated.time.size` while `r_squared` explicitly filters non-finite pairs. The scatter sample count should describe the actual paired sample (verified below), or explicitly identify total timestamps instead. The figure's R² and metric values have not been shown incorrect by this count defect.
- The plot legend still uses the generic “observed” label. Synthetic provenance is explicit in the fixture filename, its JSON, the case config comment and this record; the images themselves have no synthetic-data caption. A dataset-label/provenance caption would improve reuse of synthetic plot fixtures without changing station IDs or physical setup.

LIB-15 paired-count check: over the plotted period starting 2002-01-02 there are 5,478 timestamps, **5,414 finite observed pairs**, and 64 missing observations (the simulated source is finite). The figure's `n` overstates its paired sample by 64. A sandbox-only Pandas import initially failed; the same read-only Pixi probe outside the sandbox passed. That import failure is environment access, not a package regression.

WF2 continuation: the owned-wrapper dry run passed with 25 jobs and nine model×experiment fetch/reduction pairs (historical plus two SSPs for each of three models). Execution began unchanged at 08:03:38, using the testing project file and the original projection settings. Evidence: `.tmp/scratchpad/2026-09-27_0721/wf2-{dryrun,execute}.log`.

### Projection failure and independent generation continuation — 2026-09-27

- WF2 exited 1 after 4m24s. All nine source fetches and basin reductions succeeded; raw and scalar NetCDFs remain for CMCC-ESM2, INM-CM5-0 and GFDL-ESM4, each historical/SSP245/SSP585, member r1i1p1f1. Source logs identify noleap temperature calendars. The reference resolves to 29 complete hydrological years within 1985–2014 and differs from the local 2000–2016 historical climate window; this difference is explicit configuration, not an extraction failure.
- **LIB-16 — confirmed fatal dry-month provenance schema defect:** rule 2.05, `derive_change_factors.py:636`, indexes `row["dataset"]` when counting flagged monthly rows. The tidy table schema uses `model` after the documented dataset/institution collapse. This branch is reached by the Liberia data and raises `KeyError: 'dataset'`. The rule computed 864 monthly and 72 annual rows and two cloud plots before failing; Snakemake removed its declared tables and cloud plots, and downstream rule 2.06 did not execute. No final projection tables/plots survive. A repair must reconcile flagged-month provenance identity with the current tidy schema and include a regression exercising at least one flagged month. No source change or unchanged retry applied.
- Evidence: `wf2-execute.log` and the external project log `logs/_parts/2.05_derive_change_factors.log`. Retained source files permit a later focused consumer rerun without fetching the ensemble again.
- Generation proceeds independently using adjacent `project_config_testing_wf3.yml`, with only WF3 enabled and the previously disclosed 2040–2042 test variant. Its owned-runner dry run passed. The runner accepts forwarded dry-run flags after `--`; the first syntax attempt without that separator was rejected before execution, then corrected. This is an invocation correction, not a workflow defect.

### Generation success and simulation handoff — 2026-09-27

- WF3 passed, exit 0, 08:09:49–08:12:31 (2m43s wrapper, 2m04s generation phase). Eighteen generation jobs completed: one generation, fourteen perturbations, publication and two log/benchmark gathers. Collection short ID `4e097bef80e7`, full ID `4e097bef80e7a4a939104bda948a75a5032c00813c2d8347579ccb2be4ed3899`, resolved seed **1026957974**, run IDs `01`–`14`. Ready marker and `read_collection_v2` validation passed. LIB-06 seed capture is resolved for this collection.
- All fourteen retained scenario NetCDFs passed structural and finite-value checks: 11×12 stored grid, 10,220 daily noleap timestamps, 2016-01-01–2043-12-31, finite precipitation/temperature fields and nonnegative precipitation. The generator's buffered coverage includes the requested 2040–2042 simulation window; it is not the simulation window itself. Generation sampled 38 basin cells; all 132 stored grid cells were populated. Five source leap days were dropped for the noleap convention.
- Seventeen diagnostic PNGs were produced under `scenarios/4e097bef80e7/weathergenr/evaluation/plots`. Visually inspected `monthly_cycle.png` and `daily_mean.png`: readable panels, no apparent clipping. Their captions/axes could better identify units and explain the colour encodings; the annual-cycle sheet has coloured realizations and a black comparison curve without an explicit legend. These are presentation opportunities, not demonstrated numerical defects.
- Diagnostic evaluation explicitly capped coverage at **25 of 38 basin cells** for memory control and standardized the comparison to 2001–2016 versus generated 2023–2038. Startup R locale warnings and a no-testable-spectral-peak warning occurred without preventing publication. No claim of scientific adequacy follows from these execution checks.
- WF4 owned-runner dry run passed: 22 initial jobs, fourteen downscales and one automatic fourteen-member batch; checkpoint completion may expand the metric DAG. Simulation execution is the next authorized phase. Evidence: session scratch `wf3-execute.log` and `wf4-dryrun.log`.

### Simulation blocker and stopping disposition — 2026-09-27

- WF4 actual execution failed, exit 1, approximately 44s (08:14:46–08:15:31). Model fingerprint matched the live model and the input snapshot completed. The first concurrent downscaling jobs for runs `05`, `06` and `07` failed before any Wflow scenario run or retained-response metric calculation. These are three jobs in one failed invocation, not three retry attempts.
- **LIB-17 — confirmed ancillary-grid rejection; longitude-normalization cause strongly indicated:** `simulator_adapter.py::validate_ancillary_grid` rejected the physical elevation raster loaded by `downscale_climate_forcing.py::prepare_model_forcing`. The ERA5 ancillary artifact `data/climate/ancillary/era5/77aa8f51a556/era5_orography_2018.nc` has WGS84 bounds `(-0.125, -90.125, 359.875, 90.125)`, whereas Liberia scenario coordinates use negative longitude. The unnormalized global raster fails HydroMT's aligned-covering-grid predicate. A global raster on a different longitude convention is not evidence that physical elevation is absent over Liberia. Investigate normalization through the documented catalog/preparation boundary before this strict check; preserve the compatibility guard and never patch installed HydroMT/Wflow packages. A focused regression should cover a western-hemisphere basin and the corresponding wrapped elevation grid. No source fix or repeat execution applied.
- WF4 warned that duplicate native response `Q_101` mapped to `1010` was retained once. This was explicitly reported and did not cause the downscaling failure; no additional defect established.
- Evidence: scratch `wf4-execute.log`; external `logs/_parts/simulate_system/liberia_hydropower_outlet_20260927/4.04_downscale_scenario_series/run_{05,06,07}.log`. Experiment namespace `liberia_hydropower_outlet_20260927` retains its pinned input snapshot for diagnosis. Generated collection, historical model/forcing, synthetic fixture and successful evaluation plots remain available.
- Stop unchanged retries at these deterministic blockers. WF2 requires the LIB-16 schema repair; WF4 requires LIB-17 preparation/grid investigation. The test has **not** completed end-to-end scenario simulation, response metrics or any response-surface plotting. Repair and focused rerun are follow-up work on this same pinned branch. No toolbox source edits, landing or push occurred in this exercise.

### Latest outcome for review

| Coverage | Outcome |
|---|---|
| WF0 historical climate | Passed; ERA5/CHIRPS comparison retained |
| WF1 historical Wflow, 2001–2016 | Passed; 5,843 daily response rows at 11 locations |
| Synthetic observation evaluation | Passed; four outlet sheets rendered and inspected; LIB-15 count-label bug recorded |
| WF2 projection sources | Nine combinations fetched/reduced; final tables/plots blocked by LIB-16 |
| WF3 compact generation | Passed; ready collection `4e097bef80e7`, fourteen runs, seed `1026957974`, seventeen diagnostic PNGs |
| WF4 scenarios/metrics | Dry run passed; actual downscaling blocked by LIB-17 before engine execution |

The compact scenario test covers 2040–2042, retaining the full configured grid and realizations. The original 2040–2060 definition remains preserved; 2043–2060 and long-period behavior are untested. Historical synthetic-fit metrics are plotting fixtures, not model validation. Validation for this documentation-only work: `git diff --check`; no unrelated full-suite or baseline run.
