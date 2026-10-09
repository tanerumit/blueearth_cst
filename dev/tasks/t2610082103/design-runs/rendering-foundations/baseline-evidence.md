# Pre-change rendering baseline

Source candidate: 07288e94. Production inputs are read-only; generated outputs and logs stay here.

Scope: pre-change rendering feasibility, rapid, numerical unaffected. No tests or source edits.

Environment: Pixi default, Python 3.12.13 (conda-forge), Matplotlib 3.11.0, Agg backend; 600 dpi
production exports. `environment.log` records versions. Source hash inventories identify the exact
rendering modules captured while the source diff was empty; no tracked source edits were made here.

## Commands and results

Run from the session-1 worktree. The following commands were run, with output redirected to owned scratch:

```powershell
pixi run python .tmp/scratchpad/shared-rendering/baseline/render-baseline.py *> .tmp/scratchpad/shared-rendering/baseline/wf0-wf1.log
pixi run python .tmp/scratchpad/shared-rendering/baseline/render-wf2.py *> .tmp/scratchpad/shared-rendering/baseline/wf2.log
pixi run python .tmp/scratchpad/shared-rendering/baseline/inventory.py *> .tmp/scratchpad/shared-rendering/baseline/inventory.log
pixi run python .tmp/scratchpad/shared-rendering/baseline/inventory.py --evaluation *> .tmp/scratchpad/shared-rendering/baseline/evaluation.log
```

The first command completed successfully: WF0 CHIRPS 19, ERA5 21, comparison 18 ordinary PNGs,
each with a captioned copy (116 PNGs). WF1 forcing produced its nine canonical PNGs, separate captions,
and prepared annual/climatology CSVs plus map fields in `wf1/prepared/`.

The second command completed successfully: WF2 18 ordinary and 18 captioned PNGs, 13 models, one
future window (2036–2065), reference 1985–2014. Its retained suite omits the multi-period product;
the caption inventory records this explicitly. Four scenarios are retained, without model subsampling.
The existing lab adapter is reused with only its output root changed. It applies current preparation
functions to older retained tables: ensemble summaries, coverage family metadata, eligibility labels,
trajectory medians/ranges and the current availability contract. No statistics were invented or changed.
This is a retained-table adapter baseline, not proof that fresh WF2 production preparation is equivalent.

The evaluation command initially exposed an adapter signature error: the long metric table must be
unstacked on `time_type`, as the production caller does. The scratch adapter was corrected accordingly.
The corrected command completed successfully: one hydrograph, one performance sheet and four basin
annual/seasonal PNGs for recharge and evapotranspiration. Final total: 167 PNGs. `evaluation.log`
records the successful result; `png-inventory.json` was refreshed afterward.

## Input and prepared-value evidence

WF0 input roots are beneath:
`C:/Users/taner/workspace/cst-cases/runs/sp2-liberia/active/data/climate/historical/`.
The three roots are `chirps_20000101_20161231`, `era5_20000101_20161231` and `comparison`.
Their retained tables and diagnostics metadata are read-only. `diagnostic_render.load_result` is
adapted in the scratch process to read the retained source root while every output path points here.
All current chart registrations are rendered; maps use retained annual fields. WF0 maps omit optional
spatial overlays in this adapter; the future comparison must reuse this same omission.

WF2 inputs are CSVs at:
`C:/Users/taner/workspace/wf0-lab/outputs/wf2/gabon-ntoum-dev-ensemble/results/`.
The adapter checks that each consumed input's SHA256 remains unchanged after rendering.

WF1 forcing inputs come from local `test_case/test_rapid`: model `staticmaps.nc`,
`forcing/inmaps_historical.nc`, the ERA5 historical extraction and four `data/spatial/geoms/` overlays.
The production preparation and rendering APIs are called with January reporting years and the
selected historical extraction's exact native map frame. Prepared CSV hashes are in `inputs.json`.

`retained-input-hashes.json` records 86 WF0/WF2 retained input hashes.
`prepared-value-hashes.json` records 77 WF0 restored DataFrame/Series hashes using deterministic JSON,
ISO dates and 15-digit precision. These are software comparison fingerprints, not independent numerical
validation. `inputs.json` additionally identifies WF1 forcing sources and prepared CSVs.
`png-inventory.json` lists PNG paths, pixel sizes and raster DPI. Image bytes are not an acceptance oracle.
Source hashes are in `source-hashes.json` and `evaluation-source-hashes.json`.

The evaluation adapter uses real retained `output_q.csv`, `output_gwr.csv`, `output_aet.csv` and
`config/basin_data/observations_timeseries.csv`. Their provenance is accepted as retained rapid inputs,
without a claim that the observation table is independently validated field data. It selects station 1010,
removes the same first-year warm-up as production, pairs the common observation interval, and uses
native subcatchment cell-count weights for recharge and evapotranspiration basin summaries.
Its source/prepared hashes and weights are preserved in evaluation-specific JSON/CSV files.

## Inspection and omissions

Opened WF0 CHIRPS annual series, WF1 precipitation forcing map and station-1010 hydrograph:
all are readable.
The forcing map retains a broad historical source frame around the small model basin; preserve this
existing behavior for the extraction comparison. The remaining PNGs are inventory-checked but not
all visually inspected. This capture establishes runnable baselines; post-change appearance acceptance
requires corresponding renders and visual review.

No pytest, persistent tests, full suite, baseline manifest check, fresh workflow execution, numerical
model validation, commits, production writes or source changes were performed. The task's deliberate
budget is real-input render capture and prepared-value hashing, with numerical behavior unaffected.
Optional subbasins, missing/constant synthetic inputs, multi-period WF2 and denser 20+ model coverage are
reserved for post-design acceptance. Current WF2 already supplies four scenarios and 13 models.
This scratch evidence is retained for the parent shared-rendering task until post-change comparison.
