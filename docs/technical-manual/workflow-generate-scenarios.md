---
title: "WF3 — Generate scenarios"
format: html
---

`generate_scenarios.smk` builds a reusable collection of stochastic weather realizations across a configured
temperature–precipitation perturbation grid. Generation is independent of CMIP6 and of the Wflow model. Use
the owned `scripts/run_workflows.py` wrapper to prepare and claim the collection.

The run settings identify the historical climate data and period, requested scenario period, number of
weather realizations, climate perturbations, scenario series, and water-year start. Scenario series are
weather realizations under the configured climate perturbations, independent of emissions scenarios.

## Rules and wrapper steps

| Rule or wrapper step | Operation |
|---|---|
| `all` (target) | Collect the ready collection and execution records. |
| 3.01 `delineate_region` | Define the shared basin region. |
| 3.02 `extract_climate_datasets` | Extract the selected historical climate store. |
| 3.03 `prepare_perturbation_grid` | Stage the monthly perturbation lookup. |
| 3.04 `snapshot_generation_inputs` (wrapper step) | Freeze source inventory and generation plan. |
| 3.05 `claim_scenario_collection` (wrapper step) | Claim and initialize the collection. |
| 3.06 `prepare_weather_generator_settings` (wrapper step) | Write weather-generator input settings. |
| 3.07 `generate_weather_realizations` | Generate unperturbed series. |
| 3.08 `perturb_climate_realizations` | Generate the perturbed series by run. |
| 3.09 `publish_scenario_collection` | Validate and mark the collection ready. |
| 3.10 `gather_benchmarks` | Merge benchmark parts. |
| 3.11 `gather_logs` | Merge log parts. |

The `all` target waits for the ready collection and execution records. Wrapper steps 3.04–3.06 occur before
the generation DAG; they are not Snakemake rules.

Console completion and reuse messages report the number of scenario runs. Collection digests and
internal manifest paths remain in retained records rather than those messages.

When resuming an experiment from another checkout, keep WF3 enabled so the runner can validate and
reuse its ready collection under the current checkout's request path. The original generation plan
and seed remain unchanged. Changed generation inputs or settings still require a new experiment;
an incomplete collection cannot be repaired through this continuation path. A dry run does not
publish the new request pointer, so downstream WF4 previews may require one actual WF3 reuse first.

## Rule flow

The wrapper stages run before the generation DAG. Generation and perturbation fan out over realizations and
selected grid points.

## Configuration

The project file supplies `project.catalog`, the `basin` definition, and `climate.selected` and
`climate.window`. Its `workflows.generate_scenarios` stanza enables the workflow and points to its YAML file
through `config_path`.

The workflow file, `test_case/project_config_rapid_generate_scenarios.yml`, sets `n_realizations`,
`simulation_window.start` and `.end`, and `seed` (integer or `auto`). `climate_perturbations.temp` and
`.precip` define monthly `mean.min` and `.max`, `n_levels`, and `trajectory`; precipitation can also set
monthly `variance.min` and `.max`. `climate_perturbations.spell_factors.dry` and `.wet` modify spell lengths
without adding grid axes. The template at
`config/templates/example-basin/project_config_generate_scenarios.yml` also shows optional `unit_id_capacity`.

```text
n_realizations: 2
simulation_window: start, end
climate_perturbations:
  temp: n_levels, trajectory, mean.min/max (12 monthly values each)
  precip: n_levels, trajectory, mean.min/max, variance.min/max
  spell_factors: dry/wet (12 monthly values each)
seed: 123
```

This is a key map, not a copyable YAML file. Use the twelve monthly values in the workflow YAML or template
when configuring perturbations.

## Inputs

Inputs are historical climate data from the selected catalog source, the basin region, and the
weather-generator and perturbation settings. WF3 does not consume WF2 change factors or a Wflow model.

The wrapper freezes historical climate, basin cells, the generator template and source catalogs under
`scenarios/_engine/generation_inputs/<content-hash>/`. These snapshots are shared across collections.
Effective generator settings live in the collection data root at
`scenarios/_engine/data/<collection-id>/weathergenr/weather_generation_input.yml`.
Collections retain their recorded snapshot paths; do not move those files manually.

## Outputs

The ready collection retains generated and perturbed series, lookup tables and creator configuration.
Generation also writes logs and benchmarks. The wrapper refreshes a readable scenario export after
successful generation or reuse. [Retained handoffs](retained-handoffs.md#scenario-exports-and-lookups)
owns exact data/marker/export paths, integrity rules and lookup units.

## Field constraints and refusals

`n_realizations` (default 1) and axis `n_levels` are positive integers.
`simulation_window` gives inclusive start/end years; its start cannot precede the historical record's end
year. Temperature monthly bounds are additive degrees Celsius; precipitation mean/variance bounds are
positive multipliers, with 1 unchanged. Each bound has twelve values, January–December.
`trajectory` is required per axis: `constant` applies the change from the start; `transient` ramps it
through the run. Dry/wet spell factors are monthly multipliers and add no grid axis.
Omitted spell factors resolve from advanced defaults. `weathergen_config` can select a generator recipe;
the bundled default is `config/defaults/weathergen_config.yml`.

`seed` accepts a fixed integer or `auto`; omission uses the advanced default (123 in this revision).
The automatic choice derives the seed from climate-draw settings, sources
and generator code. `unit_id_capacity` must cover the required scenario/run-group namespace; omission uses
the generation planner's derived capacity. The unperturbed root for each realization is always retained.
Malformed monthly lists, incompatible source coverage, changed frozen identity and an unready collection
fail explicitly. A dry-run does not publish ready data.

Executable owners: `generate_scenarios.smk`, `scripts/run_workflows.py`,
`experiment/generation_plan.py`, `experiment/scenario_collection_v2.py`, `shared/wf3_science.py` and
`weathergen/read_member_grid.R`. Tests include `tests/test_generate_scenarios_launcher.py`,
`test_scenario_collection_v2.py` and `test_scenario_export.py`.
