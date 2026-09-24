# dev/scripts/

Tools that inspect or maintain the repository. None is part of a run: nothing
here is invoked by a Snakemake rule (those live in `blueearth_cst/`), and a run
never imports from `dev/`. One-off probes and migrations are removed once their
job is done; the 2026-09-24 sweep is recoverable from tag
`archive/dev-scripts-2026-09-24`.

## Libraries imported by tests

Contract surfaces, not scratch helpers: a bare-checkout CI run imports them on
both legs, so an import-time error fails the suite.

| File | Purpose |
|---|---|
| [`console.py`](console.py) | Vendored colour/glyph/banner helpers from the `console-formatting` skill. Fix defects upstream and re-copy. |
| [`cross_workflow_inputs.py`](cross_workflow_inputs.py) | The one definition of the WF1 leaves other workflows declare; proved complete and minimal by `tests/test_cross_workflow_inputs.py`. |
| [`semantic_tree_diff.py`](semantic_tree_diff.py) | Whole-tree comparator and the project-tree inventory (`build_project_tree_rules`). |
| [`sweep_common.py`](sweep_common.py) | Shared machinery for the report-only repository sweeps below. |

## Gates and board

| Script | What it does |
|---|---|
| [`check_baseline.py`](check_baseline.py) | `record` / `check` / `compare` fingerprints of the baseline targets in `dev/baseline/manifest.json`. Run WF1 with `--notemp` first. |
| [`snapshot_project_tree.py`](snapshot_project_tree.py) | Project-tree snapshot behind `pixi run tree-check`. |
| [`todoboard.py`](todoboard.py) | Locates and runs the `todoboard` CLI behind `dev/tasks/` and the generated `dev/TODO.md`. |

## Repository sweeps (report-only)

| Script | What it finds |
|---|---|
| [`sweep_stale_spellings.py`](sweep_stale_spellings.py) | Retired config spellings still live somewhere. |
| [`sweep_identity_renames.py`](sweep_identity_renames.py) | Rename records whose two sides became identical (`X -> X`). |
| [`sweep_unread_config_keys.py`](sweep_unread_config_keys.py) | Declared config keys no reader reads. |
| [`scan_console_encoding.py`](scan_console_encoding.py) | Non-ASCII in strings that reach a console (cp1252). |

## Environment

| Script | What it does |
|---|---|
| [`install_weathergenr.R`](install_weathergenr.R) | Idempotent install of `weathergenr` from GitHub; run by `pixi run install-rdeps`. |
| [`check_env.py`](check_env.py) | Whether a checkout can actually run the workflows (weathergenr, Julia, activation). |
| [`inspect_weathergenr.R`](inspect_weathergenr.R) | The installed weathergenr's exports and the signatures the workflow calls; run after an upgrade. |
| [`pixi_activate.bat`](pixi_activate.bat) | Activate the pixi env in a cmd shell. |
| [`check_activation.py`](check_activation.py) | Drift between `dev/reference/agent-activation.md` and the untracked agent manifest. |

## Data staging and catalogs

| Script | What it does |
|---|---|
| [`stage_data.py`](stage_data.py) + [`stage_data.yml`](stage_data.yml) | Mirror a bbox subset of a remote data root to local disk. |
| [`stage_cmip6.py`](stage_cmip6.py) + [`stage_cmip6.yml`](stage_cmip6.yml) | Stage CMIP6 slices for one region, digest-stamped so WF2's rule 2.04 hits its cache. |
| [`generate_cmip6_catalog.py`](generate_cmip6_catalog.py) | Regenerate `config/catalogs/cmip6_data.yml` from a live crawl of gs://cmip6. |
| [`probe_cmip6_grids.py`](probe_cmip6_grids.py) | Which CMIP6 models hydromt's raster accessor refuses (non-uniform grids). |
| [`list_era5_vars.py`](list_era5_vars.py) | Variables in the staged ERA5 zarr (metadata only). |
| [`sample_bundle.yml`](sample_bundle.yml) | Parameters for the planned sample-dataset bundle; input to a builder not yet written. |

## Project inspection and cleanup

| Script | What it does |
|---|---|
| [`rule_dag_levels.py`](rule_dag_levels.py) | A Snakefile's rules in DAG order with per-rule job counts; executes nothing. |
| [`region_bbox.py`](region_bbox.py) | Report, and optionally write, the project region's bounding box. |
| [`scaffold_project_tree.py`](scaffold_project_tree.py) + [`scaffold_extras.yml`](scaffold_extras.yml) | Dummy `project_dir` tree from the Snakefiles, for layout review. |
| [`prune_series_cache.py`](prune_series_cache.py) | Orphaned WF2 series; dry run unless `--delete`. |
| [`prune_climate_store.py`](prune_climate_store.py) | Orphaned historical-climate stores; dry run unless `--delete`. |
| [`estimate_batch_makespan.py`](estimate_batch_makespan.py) | LPT makespan estimate behind WF4's batch size; see board item `t2608071217`. |

## Figures and console

| Script | What it does |
|---|---|
| [`preview_basin_map.py`](preview_basin_map.py) | Render rule 1.12's basin map from a model on disk, with tunables overridden or swept. |
| [`preview_spatial_maps.py`](preview_spatial_maps.py) | Render the spatial-map family from a project on disk. |
| [`preview_plots.py`](preview_plots.py) | Render the toolbox's figure families from a project tree without running a workflow. |
| [`export_svg.py`](export_svg.py) | Lift an inline `<svg>` out of an HTML page into a standalone file. |
| [`render_console_sample.py`](render_console_sample.py) + [`console_sample_specs.py`](console_sample_specs.py) | A console transcript per workflow through the real handler. |

## Repository housekeeping

| Script | What it does |
|---|---|
| [`notebook_outputs.py`](notebook_outputs.py) | Keep rendered outputs out of tracked notebooks. |
| [`build_gf15_report.py`](build_gf15_report.py) | Package the frozen GF15 benchmark into its shipped report asset. |
