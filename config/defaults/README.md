# Rule-read configs

**Referenced from a project config and read by a rule. Changing one changes a
run.** These are not templates — do not copy them, point a config at them (or at
your own edited copy elsewhere). Shared appearance defaults live separately in
`config/plotting/`.

| File | Consumer |
| --- | --- |
| `wflow_build_model.yml` | `build_model.smk` — default for `workflows.build_model.engine.build_config`; rule 1.05 `prepare_land_and_soil_maps` and rule 1.06 `build_wflow_model` |
| `wflow_update_waterbodies.yml` | `build_model.smk` — default for `workflows.build_model.engine.waterbodies_config`; rule 1.07 `add_reservoirs_lakes_glaciers` |
| `weathergen_config.yml` | `generate_scenarios.smk` — default for `weathergen_config`, read by planning step 3.06 `prepare_weather_generator_settings` and recorded in the generation plan |

The template's path is recorded in the generation plan. Editing it changes the plan and schedules
a new collection.

## Configuration snapshots in project outputs

`<project_dir>/config/templates/` holds verbatim archives of rule-read engine configuration files when
the workflow needs to copy them. Files recoverable from the toolbox are recorded in the run record
rather than copied. These generated records show which configuration a run used; they are not scaffolds
to edit. Change the source configuration when you want to change a run.
