# Example basin starter

This folder is a worked starting point for a new BlueEarth CST case. It shows
the current project-config layout and one example basin; its sparse stress-test
grid and two weather realizations need review before an assessment. Catalog
coverage and local data access also depend on your toolbox setup. The example
still requires access to the selected external datasets.

## Copy and configure

This is the toolbox-owned starter used by `scripts/create_case.py`. The
scaffolder reads this checkout's copy; `cst-cases` holds application configs
and run records. For commands, see the
[new-case guide](../../../docs/guide/running.md#create-an-external-case). It sets the case paths,
basin region and outlet, and starts fresh notes. Register the case in the
application inventory after the workflows complete.
Review the remaining choices below before running.

This directory is the single maintained configuration starter: `project_config.yml`
and one `project_config_<workflow>.yml` per workflow. Optional parameters are
documented beside the active settings in those files; background on the defaults
is in [the templates reference](../README.md).

For manual setup, copy this folder to `applications/<basin-kebab>/` in your
cases repository, then make
these edits before running:

1. In `project_config.yml`, set `project.project_dir` to `../../runs/<basin>/`
   or an absolute output path outside the toolbox checkout.
   No `active/` suffix is required. Choose a separate path for another assessment;
   existing output folders are not moved or archived. Create parent folders if needed.
2. Keep `basin.output_locations: data/output_locations.csv` for the copied case,
   or set a path to your own locations file.
3. Set `basin.region` to the outlet longitude and latitude and an appropriate
   `uparea` threshold. `uparea` is a model delineation threshold in km²; it is
   not a substitute for measured basin area. Check the delineated basin against
   your intended outlet.
4. Review `basin.resolution`, then verify every dataset in `project.catalog`
   covers the basin and period and is available at the locations configured in
   that catalog. Confirm the climate source names/aliases used by
   `climate.sources` and `climate.selected` resolve to the intended catalog
   datasets. Add or select catalog entries using toolbox catalog guidance.
5. Review `climate.sources`, `climate.selected`, and `climate.window` together.
   Select a forcing only after comparing the historical records where useful;
   this toolbox does no local calibration. The weather generator requires at
   least 16 years.
6. Set the required `simulation_window` in `project_config_build_model.yml`
   to the inclusive years Wflow should run, inside `climate.window`. Choose it
   separately from the longer climate record; the starter uses 2010–2016.
   Review `model.outvars` and the optional observations section.
   If you use observations, configure their
   file and verify station matching and units as described in
   [`data/README.md`](data/README.md).
7. Review `project_config_generate_scenarios.yml`: `simulation_window`,
   `n_realizations`, temperature and precipitation ranges, number of grid
   levels, and trajectories. The current example uses 2040–2060, 2
   realizations, 2 temperature levels (0 to +3 °C), and 3 precipitation levels
   (0.7 to 1.3 multipliers); the unperturbed baseline is included. This sparse
   grid and small ensemble are examples, not assessment recommendations.
8. Review `project_config_analyze_projections.yml`: catalog availability,
   selected models and scenarios, reference window (1985–2014), and future
   windows (2030–2060 and 2070–2100). These windows are independent of the
   scenario-generation window; align them deliberately when you want a
   comparable projection overlay.
9. Start a fresh case history in `notes.md`, and add the new case to the
   inventory after every workflow completes.

The starter uses schema 3. File paths resolve beside the YAML declaring them;
`toolbox:` locators select bundled resources. Keep case inputs under `data/` and
outputs under `../../runs/<basin>/`, or use absolute paths for external storage.

For a permanent output reset during testing, see
[rebuilding outputs](../../../docs/guide/running.md#rebuild-outputs-for-testing).
The runner previews the affected paths and asks for confirmation before erasing them.
See [path rules and schema-2 migration](../../../docs/guide/configuration.md#how-paths-are-read).
Run Pixi commands from the toolbox root.

## Run in stages

The starter enables only WF0 (`analyze_climate`). WF0 answers the historical
forcing-selection question and should be run alone. Review its comparison and
set `climate.selected` before proceeding.

From the `blueearth_cst` toolbox root, with its Pixi environment available, run
the enabled workflow:

```powershell
$CasesRoot = 'C:/path/to/cst-cases'
$CaseName = 'my-basin'
$config = Join-Path $CasesRoot "applications/$CaseName/project_config.yml"
$ProjectDir = Join-Path $CasesRoot "runs/$CaseName"

pixi run python scripts/run_workflows.py --config $config --project-dir $ProjectDir --cores 3 -- --dry-run
```

Replace the cases root and case name, then remove `-- --dry-run` to execute. The runner
executes enabled workflows in fixed order. To run one workflow, set its
`enabled: true` and all other workflow flags to `false`, then use the
corresponding command below:

```powershell
pixi run python scripts/run_workflow.py analyze_climate --config $config --project-dir $ProjectDir --cores 3
```

After WF0, disable `analyze_climate` before enabling downstream stages.
Disabling a workflow skips its future run; it does not remove results already
written. Enable WF1 (`build_model`) and WF3 (`generate_scenarios`) when ready.
WF2 (`analyze_projections`) is optional. WF3 is independent of WF2:
projections are a plausibility overlay and never drive scenario generation.
WF4 (`simulate_system`) consumes the model and generated collection, so enable
it only after both are ready. The owned runner executes enabled stages in
fixed order; for WF3 alone, disable every other workflow. WF4 alone uses its
dedicated simulation runner:

```powershell
pixi run python scripts/simulate_system.py --config C:/Users/<you>/workspace/cst-cases/applications/<basin-kebab>/project_config.yml --target all --cores 3
```

For downstream stages WF1–WF4 as appropriate, use the owned `run_workflows.py`
wrapper shown above; it invokes simulation through the dedicated runner.
Before executing a changed workflow, consult the toolbox's current
[configuration guide](https://github.com/tanerumit/blueearth_cst/blob/main/docs/guide/configuration.md)
and [running guide](https://github.com/tanerumit/blueearth_cst/blob/main/docs/guide/running.md).

## Files

- `project_config.yml` holds shared basin, climate, model-output, and enablement
  settings.
- `project_config_<workflow>.yml` holds settings for that workflow.
- `data/` holds case-specific sidecar data, described in
  [`data/README.md`](data/README.md).
- `notes.md` is a retained-run record template. Keep evidence under
  `runs/<basin>/` and summarize each retained run there.

The starter uses the toolbox's `config/catalogs/deltares_data_pdrive.yml` catalog
with data under `P:/wflow_global/hydromt`. Mount the Deltares P-drive before
running. Its basin source names are `rivers: hydro_rivers_lin` and
`lulc: globcover`; review these when selecting another catalog.
