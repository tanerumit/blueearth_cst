---
title: "Configuring a project"
subtitle: "Choose basin inputs, periods and outputs"
---

Start with [Create your own case](new-case.md).
The starter contains `project_config.yml` and five `project_config_<workflow>.yml` files.
Give the project file to the runner with `--config`; it names the workflow settings files.
Keep the commented parameter help beside the YAML you edit.

## How paths are read

With `schema_version: 3`, file paths resolve beside the YAML that declares them.
Use `toolbox:config/...` for bundled resources and absolute paths for storage on another drive.
Workflow `config_path` is relative to the project file; inputs declared in a workflow file use that
file's directory. Paths inside HydroMT catalogs retain HydroMT's own semantics.
There is no environment-variable interpolation or search for a matching filename.
Schema 2 retains run-directory-relative paths; changing the version alone is not a path conversion.
See the [configuration reference](../technical-manual/configuration.md) for exact rules.

## Anatomy

### The project file

1. Set `project.project_dir` to an external output root and `project.catalog` to available data catalogs.
   Catalogs locate data; they do not install it. Check the basin and time coverage before execution.
2. Choose `basin.region`, `basin.resolution` and `basin.output_locations`.
   A grid spacing is a computational choice, not the resolution or accuracy of every source product.
3. Choose `climate.sources`, then `climate.selected` after reviewing candidate forcing.
   Selected forcing also conditions weather generation; the toolbox does no local calibration.
4. Set `climate.window` to inclusive calendar years. The weather generator needs at least 16 years.
   Choose the historical model run separately in the build-model file, within the available record.
5. Choose `model.outvars` before simulation so later indicators have their required responses.
6. In `workflows`, use unquoted `enabled: true` or `enabled: false` and each file's `config_path`.

For example, the workflow selection has this shape:

```yaml
workflows:
  analyze_climate:
    enabled: true
    config_path: project_config_analyze_climate.yml
  build_model:
    enabled: false
    config_path: project_config_build_model.yml
```

This is a fragment, not a complete case file. Use the maintained starter for all five workflow entries.

### Shared settings

Shared basin, forcing, model outputs and plotting choices belong in the project file.
Settings for one workflow belong in that workflow's file.
Use the [technical configuration reference](../technical-manual/configuration.md) for constraints,
defaults and exact meanings; the annotated starter is the copyable configuration source.

### Search for an outlet within an area

An approximate point can fall on an isolated drainage cell.
To search locally, HydroMT accepts a `subbasin` box ordered west, south, east, north:

```yaml
basin:
  region: "{'subbasin': [29.81375, 31.12208, 29.87375, 31.18208], 'uparea': 100}"
  sources:
    hydrography: merit_hydro_ihu
    basin_index: merit_hydro_ihu_index
```

Use a matching hydrography/index available in your catalog.
The box searches for outlets; upstream catchments can extend outside it and several rivers can select
several basins. It is distinct from the `bounds` argument limiting available hydrography.
Inspect the result before downstream runs. This search does not revise your output-location CSV.
Record any manual coordinate correction in case notes.

### Output locations

Provide `station_name`, longitude `x` and latitude `y` in decimal degrees.
Optional `location_role` is `control` (default) or `observation`.
Points must start in their declared parent basin and drain to its outlet.
Adjustment follows drainage to a river cell within `basin.delineation.snap_tolerance_m`;
it does not choose the nearest river across a divide. A point ending in a pit is refused.
Inspect reported original/resolved coordinates before changing tolerances.
See [input formats](../technical-manual/input-formats.md) for exact station IDs and observation matching.

### The per-workflow files

1. `project_config_analyze_climate.yml`: historical source diagnostics and coverage settings.
2. `project_config_build_model.yml`: model recipes, required `simulation_window` and optional observations.
   Select inclusive `start`/`end` years inside the historical climate record.
3. `project_config_analyze_projections.yml`: projection catalog, ensemble selections and reference/future windows.
4. `project_config_generate_scenarios.yml`: generated period, realizations, monthly perturbations and seed.
5. `project_config_simulate_system.yml`: experiment, operations, indicator sets and compute choices.

A disabled workflow may omit its `config_path` if it has no settings file; a supplied path must exist.
Use [workflow reference](../technical-manual/workflows.md) for each workflow's detailed contract.

## `enabled: false` skips the run, it does not clean up after it

Old results remain. Check their basin, forcing, model and scenario membership before later use.
WF1 and WF3 independently supply WF4; WF2 is an optional overlay and never drives WF3.

## Plot annotations

Set `plotting.annotation` in the project file to `none` (default), `caption` or `title`.
It changes annotations at the existing Python plot paths; labels/legends remain.
R/weathergenr plots keep their own settings.
Changes schedule affected plotting jobs without redefining scenario/simulation identity.
WF1's combined evaluation job also refreshes its indicators.

### Colour defaults

Toolbox-wide Python appearance lives in `config/plotting/colors.yml` and `style.yml`.
Read the [local plotting guide](../../config/plotting/README.md) before changing these shared files.
Restart an interactive plotting process after edits. Colour changes do not change scientific classification,
normalization or missing-value handling, and do not apply to R/weathergenr plots.

## Where the other configuration lives

- `config/catalogs/`: data-source catalogs.
- `config/defaults/`: live model/generator settings; changes affect runs.
- `config/plotting/`: toolbox-wide Python appearance.
- `config/templates/`: copyable starter/selection files.
- `config/advanced_settings.yml`: toolbox limits/defaults; normally leave it as supplied.

Pass your project file to the runner, never `config/advanced_settings.yml`.

## On Linux

Select a config/catalog whose data roots resolve on that machine, including the supplied `_linux.yml`
examples where appropriate. Windows setup instructions are not a Linux installation qualification.

## Naming an experiment

Use [experiment selection](running.md#select-resume-or-create-an-experiment) to preview, resume or allocate.
An omitted name begins with `stress_test_01`; a plain rerun selects the highest allocation in its family.
Use `--new-experiment` for changed scientific simulation inputs, not merely changed indicator choices.

## Next

- [Run the workflows](running.md) and inspect the preview.
- [Read outputs](outputs.md) and check their status/provenance.
