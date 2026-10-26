---
title: "Configuring a project"
subtitle: "Choose the basin, climate data, and stress-test settings"
---

The settings are stored in a project file and a separate file for each
workflow. Give the project file to a runner with `--config`; it names the other
files. A direct Snakemake command uses `--configfile` instead.

Start from `config/templates/example-basin/`, the single maintained starter.
Use the [case scaffolder](running.md#create-an-external-case) to set case paths
and outlet coordinates, or copy the whole directory and follow its README.
It contains `project_config.yml` plus five workflow files, including commented
examples of optional parameters. Keep the filenames so the `config_path` links
continue to work, or update those links if you rename the files.
`test_case/project_config_baseline.yml` is a filled-in worked example, and
`test_case/project_config_rapid.yml` is the same basin sized for a quick
end-to-end run.

::: {.callout-important}
## How paths are read

With **`schema_version: 3`**, file paths resolve beside the YAML that declares them.
For example, a case at `applications/my-basin/project_config.yml` can use
`project_dir: ../../runs/my-basin` and `output_locations: data/output_locations.csv`.
Moving the cases directory preserves these relationships. Keep assessment outputs outside the toolbox;
the in-repository `test_case/` locations are for development examples.

Use **`toolbox:config/...`** for bundled catalogs or engine settings. The prefix resolves against the
toolbox checkout running the workflow, independently of the case location. Absolute paths remain
supported for storage on another drive. Forward slashes work on Windows and Linux.

Workflow `config_path` remains relative to the project file. Observation paths, engine YAML,
projection catalogs, generator YAML, explicit scenario manifests, and custom indicator definitions
resolve beside their respective workflow file. A nested workflow file therefore has its own base.
HydroMT predefined catalog names, remote URLs, and paths *inside* catalogs retain HydroMT semantics.
No environment-variable interpolation or search for a matching filename is performed.
Input datasets are not installed with the toolbox. Check that the named
catalogs and their data locations are available to you before running.
:::

## Anatomy

### The project file

```yaml
schema_version: 3

project:
  project_dir: test_rapid
  catalog:
    - toolbox:config/catalogs/deltares_data.yml
    - toolbox:config/catalogs/deltares_era5_daily_zarr.yml

basin:
  region: "{'subbasin': [9.666, 0.4476], 'uparea': 100}"
  resolution: 0.00833
  output_locations: test_data/output_locations.csv

climate:
  selected: era5
  window: {start: 2000, end: 2016}
  sources: [era5, chirps]

model:
  outvars: ['river discharge', 'actual evapotranspiration', 'groundwater recharge']

workflows:
  analyze_climate:
    enabled: true
    config_path: project_config_rapid_analyze_climate.yml
  build_model:
    enabled: true
    config_path: project_config_rapid_build_model.yml
  analyze_projections:
    enabled: true
    config_path: project_config_rapid_analyze_projections.yml
  generate_scenarios:
    enabled: true
    config_path: project_config_rapid_generate_scenarios.yml
  simulate_system:
    enabled: true
    config_path: project_config_rapid_simulate_system.yml
```

Use `schema_version: 3` for paths relative to each declaring YAML file. Schema 2 resolves paths
relative to the run directory. Unknown schema versions are refused. Archives preserve exact source
YAML and resolved runtime paths. Moving a case configuration does not automatically relocate its
retained outputs or external datasets.

### Shared settings

- **`project.catalog`** names one or more HydroMT data catalogs. They tell the
  toolbox where to find climate, terrain, and other input datasets. The rapid
  example uses a second catalog to select its ERA5 source. Replace these
  example paths with catalogs available on your machine.
- **`basin.region`** is a HydroMT region specification. The example delineates
  the subbasin draining to a point at (9.666 °E, 0.4476 °N), near a location
  with 100 km² of upstream area.
- **`climate.window`** is **inclusive calendar years**, and it sizes the
  historical climate record. The weather generator requires at least 16 years;
  the rapid example uses 2000–2016, inclusive.
- **`climate.selected`** is the forcing dataset the model is driven with. Because
  the toolbox does no local calibration, review this choice carefully. The
  optional historical climate analysis helps compare candidate sources.
  **`climate.sources`** is the full candidate list it compares; `selected` must
  be one of them.
- **`climate.map_reference`** optionally sets historical map completeness. Defaults are three missing
  days per calendar month and fifteen per reporting year. `max_missing_days_month` accepts integers
  0–27; `max_missing_days_year` accepts nonnegative integers. Unknown keys, booleans and fractions are
  refused. Put this mapping in the project file, never a workflow file.

WF0's `diagnostics.max_missing_days_month` and `diagnostics.max_missing_days_year` must equal the shared
map policy. For custom tolerances, copy both values into `climate.map_reference`; a monthly value above
27 requires an explicit supported choice in both places. There is no automatic clamping. Changing WF0's
tolerances also affects its temporal diagnostics. WF1's model-forcing summaries keep the independent
default 3/15 policy; map captions distinguish this from a custom reference policy.

The project file holds the basin, climate source, and model output choices
shared across workflows. Settings specific to one workflow go in that
workflow's file.

### Search for an outlet within an area

An approximate outlet coordinate can fall on a small isolated drainage cell.
To select river outlets within a local search area, use HydroMT's bounding-box
form of `subbasin`, with coordinates ordered west, south, east, north:

```yaml
basin:
  region: "{'subbasin': [29.81375, 31.12208, 29.87375, 31.18208], 'uparea': 100}"
  sources:
    hydrography: merit_hydro_ihu
    basin_index: merit_hydro_ihu_index
```

This example selects outlets on streams with at least 100 km² of upstream
area. HydroMT delineates their upstream catchments, which can extend beyond
the search box. This differs from the optional `bounds` argument, which limits
the hydrography data used for delineation. An area intersecting several rivers
can select several basins; inspect the resulting basin geometry and output
locations before running the remaining workflows. Use a basin index matching
the selected hydrography and available in your data catalog.

Rule `delineate_region` warns when a search area selects outlets. HydroMT's
region parser returns the basin geometry without the selected outlet coordinates;
the warning therefore reports selection, not a measured coordinate change. A
search-area configuration contains no original point to compare. If point-based
delineation fails because the selected raster has fewer than two cells along an
axis, the rule reports the supplied region and suggests checking placement or
using a bounded search area.

The search area does not revise an existing `output_locations` CSV. Place its
points within the selected drainage network, using the resolved outlet for an
outlet point. Record any manual coordinate correction in the case's run notes.

### Output locations

`basin.output_locations` points to a CSV with `station_name`, `x` (longitude),
and `y` (latitude), in decimal degrees. The optional `location_role` column
accepts `control` (the default) or `observation`.

Each point must start within the active cells of a declared parent basin.
The toolbox follows its drainage path downstream to a river cell, subject to
`basin.delineation.snap_tolerance_m`; it does not move points to the
geometrically nearest river across a drainage divide. Both controls and
observations must drain to their assigned parent basin's outlet. Points in
different declared parent basins are supported.

Invalid points are rejected with their station names and original coordinates.
Check their placement against the source hydrography before changing the snap
tolerance. A point that reaches a pit without reaching a river is rejected.
Successful coordinate adjustments in the spatial-units rule emit a warning
with only the station name and adjusted longitude/latitude. This includes moving a point to its
model-cell centre even when no downstream movement is needed.

### The per-workflow files

Each workflow entry says whether to run it and where to find its settings:

```yaml
# project_config_rapid_build_model.yml
engine:
  build_config: config/defaults/wflow_build_model.yml
  waterbodies_config: config/defaults/wflow_update_waterbodies.yml
observations:
  river discharge: test_case/test_data/observations_timeseries.csv
simulation_window: {start: 2010, end: 2016}
```

`build_model.simulation_window` is required and must fit inside `climate.window`.
Choose the Wflow run period separately from the longer climate analysis record.
Set inclusive `start` and `end` years. Use the climate record's endpoints for the full record,
or select a shorter period.

Use unquoted `true` or `false` for `enabled:`.

You can omit `config_path:` when a workflow is disabled and has no settings
file. If you provide a path, the file must exist.

::: {.callout-warning}
## `enabled: false` skips the run, it does not clean up after it

Disabling a workflow leaves its previous results in place. Before using those
results in a later workflow, check that they belong to the same basin, climate
source, model, and settings you intend to use.
:::

## Plot annotations

Set the presentation of all Python workflow figures in the project file:

```yaml
plotting:
  annotation: none   # none | caption | title
```

`none` preserves the default appearance. `caption` adds the figure caption below the image;
`title` adds its title above. Axis labels, legends and panel labels remain in all modes.
R/weathergenr figures keep their own settings. The selected mode uses the existing PNG paths;
separate title and caption inventories remain available in every mode.

The setting is optional and defaults to `none`. It belongs in the project file, not a workflow file.
Changing it schedules affected plotting jobs without changing scenario or simulation identity.
WF1 evaluation also refreshes the indicators written by its combined evaluation/plotting job.

### Colour defaults

Python plots load `config/plotting/colors.yml` automatically from the toolbox checkout.
Edit this file to change the categorical cycle or named presets; no project-config key is needed.
The default cycle uses Expanded original, with Original blue (`#0D38E0`) and Terracotta (`#CC593D`)
first. ERA5/observed use blue and CHIRPS/simulated use Terracotta. The file also holds the existing
IPCC scenario colours, climate-map colormaps and precipitation-anomaly colormap.

`default_cycle` is an ordered mapping of colour names to quoted six-digit hex strings. `datasets` and
`evaluation` refer to those names; `scenarios` contains hex strings directly. `climate_maps` and
`precip_anomaly` contain Matplotlib colormap names. `historical_maps` contains the current WF0/WF1 custom
ramps and their under/over colours. These defaults apply to all projects using this
checkout. Restart an interactive Python session after editing the palette.

`config/plotting/style.yml` holds page width, export resolution, typography and shared chart/evaluation
appearance preferences. Both files are toolbox-wide; existing Python plotting adapters consume them.
See `config/plotting/README.md` for ownership and editing conventions.

Palette edits schedule WF0–WF2 plotting jobs without changing scenario or simulation identity.
The historical display-reference record also refreshes so cached map colours remain consistent.
WF1 evaluation also refreshes the indicators written by its combined evaluation/plotting job.
R/weathergenr figures keep their own palette. Colormap edits change colours only; classification,
normalization and missing-value handling remain defined by the plotting code.

## Where the other configuration lives

| Directory | What it is | Do you edit it? |
|---|---|---|
| `config/catalogs/` | HydroMT data catalogs — the `-d` targets | Yes, to register a data source |
| `config/defaults/` | Supplied model and weather-generator defaults | Only when you need to change those settings |
| `config/plotting/` | Shared palettes and appearance | Change toolbox-wide plotting defaults |
| `config/templates/` | Starting files for a new project | Copy them to your project settings directory |
| `config/advanced_settings.yml` | Toolbox-wide limits and defaults | Usually leave as supplied |

Pass your project file to the runner, not `config/advanced_settings.yml`.

::: {.callout-note}
## On Linux

Use the `*_linux.yml` variants of both the config set and the data catalog — the
data-catalog paths differ from Windows.
:::

## Naming an experiment

`experiment_name` in the simulation settings file is optional. If omitted, the
first experiment is `stress_test_01`. A custom base such as `dry_scenario` starts
at `dry_scenario_01`; a numbered name selects that exact experiment.

Preview selection without changing configuration or reserving a name:

```bash
pixi run python scripts/suggest_experiment_name.py <your project file> --name dry_scenario
```

Plain execution selects the highest allocated number in the chosen family.
Use `--new-experiment` on an execution runner to advance it. Changed collection,
model, or scientific settings require a new experiment; omission of the flag
refuses the request before producers run. See [running](running.md#select-resume-or-create-an-experiment).

## Next

- [Running the workflows](running.md) — run the whole project or selected workflows.
- [Reading the outputs](outputs.md) — what the run wrote, and whether it is
  still current.
