# DEVLOG: feat/wf2-cmip6-improvements

## Resume here

**Objective:** Implement the G2-approved WF2 starter-suite integration, task `t2610071652`.
**State:** Units 1/2 committed; unit 3 verified; unit 4 producer wiring is underway.
**Next action:** Commit unit 3 separately, then verify the rule 2.05b producer and tree inventory.
**Blocker:** Fresh-run gates remain pending: P-drive mirror unavailable; old rapid archive incompatible.

## Current contract and execution

- Accepted design: `dev/00-current-board-main/tasks/t2610071652/wf2-suite-integration-design.md`.
  The primary checkout has uncommitted finalization artifacts; preserve them and coordinate with its writer.
- Execute design section 10 in order, with one verified commit per unit. Keep this branch; landing and pushing
  require separate user instructions.
- Unit 1 owns additive analysis-window, slicing, seasonal and detrended helpers, extracted series checks,
  and their focused tests. Preserve Stage B/reducer hashes, workflow inventories and aligned CSV bytes.
- Owner ruling 2026-10-07: the October fallback reference uses WY labels `1984–2013`, matching the lab.
  Use 30 complete historical water years ending at the last complete WY of the fallback calendar span;
  do not join scenario data into the reference. Preserve all other accepted numerical contracts.
- Prior P0 change-factor and lab snapshots exist in `.tmp/scratchpad/t2610071652-snapshots/`.
  Its rapid snapshot dates from before this branch's WF2 fixes and does not satisfy the before-image gate.
- Owner ruling 2026-10-07: proceed with cached CMIP6 inputs; leave fresh-run gates pending.
  Cached-input comparisons must be labelled as such and do not count as fresh end-to-end passes.
- Owner ruling 2026-10-07: seasonal precipitation percentages use rates consistently. Document the lab's
  total-based percentage calculation as a parity exception; precipitation CV still uses integrals.
- Unit 2 uses the approved 13-model family/country constants. Exact cited Zenodo 7920408 licence could
  not be verified; no CSV is redistributed or substituted from another record. Metadata matches the lab.
  Unlisted models use a flagged single-family institution match, otherwise their own family.
- Coverage accepts resolver COMBINATIONS directly to preserve exclusions. With resolved POINTS alone,
  requested counts remain unknown; absence is not mislabelled as an unrequested run.
- Scratch logs/configs for a fresh rapid run are in `.tmp/scratchpad/wf2-suite-evidence/`.
  The scratch project config preserves rapid settings and points to a fresh matching project root.
- A local data tree exists, but it lacks the current catalog's `rivers_ge30m.fgb` and MERIT VRTs.
  Substituting its older catalog would change the evidence basis and has not been authorized.

## Current validation

- `pixi run python scripts/run_workflow.py analyze_projections --config test_case/project_config_rapid.yml
  --project-dir test_case/test_rapid --cores 3 --dry-run` — passed with host access; 15 jobs.
- The equivalent execution against `test_rapid` failed before jobs: incompatible existing run archive.
- Fresh-root execution with a matching scratch config reached rule 2.01 and failed opening the P-drive catalog:
  HydroMT reported `None of the specified roots were found`. No fresh CSV before-image was produced.
- Unit 1 passed 42 focused tests, 20 CLI tests, and 11 tests after the review corrections. Repository lint,
  format-check, compilation and whitespace checks passed. Full batch gates run at approved landing.
- Unit 2 passed all 5 focused tests, repository lint/format-check, compilation and whitespace checks.
- Unit 3 passed 16 focused tests, scoped lint/format/compilation and unchanged protected inventories.
  Root repository lint and format-check passed after formatting the concurrent unit 4 edits.
- Cached-value probing exposed a predecessor CSV defect: historical flags with no scenario dimension
  failed serialization. Companion broadcasting fixes it without changing the arithmetic kernels.
  The new regression failed before the fix; all 37 `test_change_factor_table.py` tests passed afterwards.
- Isolated archived-rapid before-image: 8 annual and 96 monthly rows, computed from committed Stage B source.
  Disposable copies use explicitly synthetic test identities because archived reducer metadata is stale;
  original cached NetCDFs are untouched. This tests numerical/serialization parity, not cache validity.
  Raw-byte SHA256 annual: `4984466e5f1ebd14f48e075f9573e83cf9567cc0d2c9f696e3c8ecff41a6f62a`;
  monthly: `706ab4593a9fd48ce4f793c51ba6147e1e6bdeb47abb7dc4289abcebab3f6864`.
  These replace the initial line-ending-normalized hashes produced by the environment hash helper.
- After extraction, the archived-input CSV hashes above match exactly. Stage B hash remains
  `a11fc4fbe4b92c37a623154a7a2f657c6f53790d14a8c1b577e153acc4a87fce`; reducer hash remains
  `942fa42db363742b5f3258cc386b7de7c7a1577973ec7a4a5936e8a6e3d7e71e`.
  WF3/WF4 repository inventories also match the pre-edit capture.
- Cached P0 comparison also passed: original and extracted Stage B reproduce the captured 600 annual
  and 7,200 monthly rows byte for byte. Raw SHA256 annual:
  `360d2512fce5f62a06b13f272c7e001f7e914b2b55701eacc38d6ddb6e11eea8`; monthly:
  `d41e232d6a5d80d8bfbce79b2f268d584ac9abaaf675effabc1fb432b97c0a9f`.
  Test-only copies have distinct per-series identities to keep reference caches isolated across models.
- Initial analysis-table comparison covers 11,900 absolute and 5,200 nonseasonal relative rows. Keys,
  counts and statuses match the lab; monthly mean/SD values exceed tolerance because archived scalar
  inputs are float32 while the lab reduces float64. Promote analysis slices only before kernel calls;
  keep the aligned arithmetic path unchanged. After correction all compared values match at the accepted
  tolerance (max absolute change difference 1.42e-14; relative difference 7.11e-14). The ruled seasonal
  precipitation percentage exception is excluded from this parity claim.
- Review found raw SD rows must use raw SD for zero-variability status: a linear trend has positive raw
  SD but zero detrended SD. Ratio rows use their own detrended rate/integral SD; a falsifier covers both.

## Integration plan state

Follow accepted design section 10. Numerical implementation uses one `python-engineer` thread, inherited
model/effort, with root responsible for reconciliation and scoped commits. Worker scope is one design unit
at a time; failed falsifiers or changed contracts reopen only the affected unit. No nested delegation.

| Unit | State | Evidence | Next action |
|---|---|---|---|
| 0 snapshots | Fresh gates deferred | Cached probe hashes above; P0/lab snapshots | Restore mirror before landing |
| 1 numerical helpers/checks | Done | `1672686c`; focused checks and invariants above | — |
| 2 coverage/families | Done | `7683ddb6`; 5 focused tests | — |
| 3 reductions/variability | Verified | 16 focused tests; P0 parity and identities | Commit separately |
| 4 analysis rule/tables | In progress | Independent inputs and table producer | Focused producer/CLI/DAG checks |
| 5a figures/captions | Not started | Design § 4 | Render and verify manifest |
| 5b retirement | Not started | Design § 10 | Remove retired callers together |
| 6 batch gates | Pending | Fresh execution unavailable | Run at approved landing |

## Historical branch record (retained)

The record below predates this branch's WF2 work.

**Timeline:**
- 2026-08-02 01:11 → Started

## Objective
Implement the master brief that splits Workflow 1 into an engine-neutral spatial
foundation and a Wflow-SBM build that consumes it.

## Pass Criteria
Phase 1 produces the documented spatial contract independently of Wflow, the
spatial-to-Wflow adapter proof passes Gate 1, Phase 2 consumes those products,
and all brief-specified tests, dry-runs, integration checks, and human gates are
completed before landing.

## Sessions

### 2026-08-02
**Done:**
- Created the canonical isolated worktree and feature branch from `main`.
- Confirmed the unmerged `feat/wf1-improvements` prerequisite overlaps the same
  Workflow 1 files and must be reconciled before implementation.
- Landed the validated prerequisite on `main` and rebased this branch onto it.
- Implemented the canonical `shared.basin.gauge_points` migration with explicit
  legacy conflict detection and validated spatial defaults.
- Implemented deterministic basin, subbasin, location-code, and `wflow_id`
  assignment with row-order invariance tests.
- Implemented model-neutral D8 hydrography/topography preparation, global-ceiling
  automatic fallback, gauge-controlled incremental subbasins, full contributing
  catchments, thematic-map resampling, the location registry, explicit vector
  products, and a portable HydroMT spatial catalog.
- Added the independently targetable `prepare_spatial_maps` rule with nine
  explicit outputs, tracked catalog/config/gauge inputs, log, and benchmark.
- Ran the spatial target against the local Gabon/Deltares sources. The written
  catalog and all entries reopen through HydroMT; topology, metadata, CRS,
  raster/vector/registry IDs, subbasin non-overlap, and catchment containment
  validate after write.
- Corrected three failures found by that integration run: decoded NetCDF nodata
  IDs, a one-cell analysis-grid border, and invalid self-touching polygons from
  raster vectorization.
- Completed the Gate 1 adapter proof using only P1 products and public
  HydroMT-Wflow APIs. The proof preserves the P1 grid and IDs and writes a
  reopenable Wflow model triplet without rerunning `setup_basemaps`.
- Passed Ruff, 45 focused spatial tests, 15 rule/DAG tests, the targeted
  one-job spatial dry-run, the 17-job Workflow 1 dry-run, and the full suite
  (1,004 passed, 31 skipped, 1 expected xfail).
- Received owner approval at Gate 1 and implemented the project-owned Wflow
  adapter. Rule 1.03 initializes the P1 grid/geometries/IDs, converts D8 to
  LDD, and runs only Wflow-owned parameter setup methods.
- Removed independent `setup_basemaps`/river-source configuration from the
  Wflow build template while retaining Wflow constants and soil pedotransfer.
- Rewired gauge/output and outlet-index steps to the resolved registry and
  added explicit pre-plot observation-header validation.
- Found and fixed automatic outlets below the Wflow river threshold by
  constraining fallback selection to the P1 river mask; the integration case
  now has five valid automatic outlets rather than twenty nominal cells.
- Completed a clean seven-rule P1→P2→Wflow run for 2000–2020. The primary
  discharge series has +0.015% mean bias, 1.48% mean-normalized RMSE, and
  0.99990 correlation against the pre-split run.
- Validated the actual Gabon observation header against a disposable
  latest-schema P1/P2 build: all four stations retain IDs 101–104.
- Extended the baseline discharge reader to select the primary outlet through
  `outlet_index.csv` when registry gauges add multiple Q columns.
- Passed the full suite (1,014 passed, 31 skipped, 1 expected xfail) and all
  three final DAG dry-runs (WF1 17 jobs, WF2 25, WF3 50).
- Confirmed the existing five-target Workflow 1 baseline still matches its
  manifest. The split discharge fails the strict per-timestep comparator on
  6,343/7,670 days.
- Received explicit owner approval for the documented material delta at Gate 2.
- Rebuilt the canonical relative Workflow 1 fixture from clean spatial/model
  outputs. A parallel build stalled while writing `staticmaps.nc`; after stopping
  only the identified Snakemake/build processes and unlocking the workdir, the
  serial `--rerun-incomplete` build completed all 17 jobs successfully.
- Corrected the stale baseline target from `forcing/plots/precip.png` to the
  actual `forcing/plots/forcing_precip_map.png` path and passed its focused
  validation batch (27 tests).
- Recorded only the five approved Workflow 1 baseline targets. The resulting
  manifest retains 14 total targets, and the post-record check confirms all five
  Workflow 1 targets match.
- Retired the renamed legacy `forcing/plots/precip.png` manifest entry that a
  scoped merge cannot infer is obsolete; the manifest now matches the 14-target
  table exactly.
- The unscoped checker is not runnable against this isolated WF1-only fixture:
  it correctly reports the nine absent WF2/WF3 outputs. Their retained manifest
  entries were not modified by the scoped record.
- Received explicit owner approval to land the branch at Gate 3.
- Rebased all six task commits onto the current local `main`. The only manual
  resolutions reconciled two moved `dev/records/milestones/` documentation paths; no
  behavioral code conflicted.
- Post-rebase validation passed the 94-test WF1/spatial/baseline landing batch
  and the five-target scoped baseline check. The broader suite passed 1,022
  tests; its 19 failures are fixture-dependent interchange checks for WF2/WF3
  files absent from this WF1-only worktree.

**Pending:**
- Apply the already-approved reusable Snakemake skill improvement only after the
  project task has landed.

**Issues / Notes:**
- The prerequisite `feat/wf1-improvements` work was merged to `main` before
  this branch was rebased, avoiding an overlapping Snakefile implementation.
- Successful Windows runs can still print the repository's known benign empty
  `Error in sys.excepthook` cascade during GDAL/rasterio interpreter shutdown;
  the rule exits zero and all declared outputs validate.
- The clean build is reliable at `-c 1`; concurrent NetCDF/HDF5 writes during
  model construction can contend on Windows, so the serial retry is the recorded
  baseline-generation path rather than evidence of a workflow dependency defect.
- Improvement candidate captured for the `snakemake` skill: document that a
  Python file used by `script:` must not rely on a leading
  `from __future__ import ...`, because Snakemake prepends generated code before
  the file and turns that import into a syntax error.
