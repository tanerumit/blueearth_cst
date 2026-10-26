---
title: "Create your own case"
subtitle: "Prepare the basin, inputs and staged workflow choices"
---

Keep case configurations and production outputs outside the toolbox checkout.
The maintained starter is [example-basin](../../config/templates/example-basin/README.md).
It contains a project file, five workflow files and case-data placeholders; it does not supply the
external forcing and spatial datasets needed to run a basin assessment.

## Create an external case

1. Choose a cases directory with an `applications/` directory, an outlet and a case name.
   From the toolbox root, preview creation:

   ```powershell
   pixi run create-case my-basin --cases-root C:/path/to/cst-cases --longitude 12.5 --latitude -3 --purpose "First-order basin assessment" --dry-run
   ```

2. Review the reported case and output paths, then remove `--dry-run` to create the case.
   Existing cases are refused. The command neither runs workflows nor creates/modifies the output tree.
   Use `--catalog` to select a catalog available to you; its path may use `toolbox:`, a case-relative
   locator or an absolute path.
3. Open `applications/my-basin/project_config.yml` and its five workflow files.
   The scaffold inherits scientific settings and the upstream-area threshold from this checkout's starter.
   Review them for your basin; generated coordinates alone do not make an assessment ready.

The scaffolder creates `INSTRUCTIONS.md` with local commands and links to this checkout's documentation.
It records the toolbox version at creation so you can identify the matching guidance.
Keep access to that checkout when working offline. If you move it, use the recorded version to find the
matching documentation and update your local links; there is no assumed hosted manual or bundled data.

For manual setup, copy the entire starter directory to `applications/<basin>/` and follow its README.
A manual copy retains that README; a scaffolded case receives generated `INSTRUCTIONS.md` instead.
Both use the same maintained configuration starter. Do not maintain another starter in the cases repository.

## Review the case

1. Set `project.project_dir` to the intended external output directory.
   The scaffold uses `runs/my-basin/`. Review the resolved path in the preview before running.
2. Check `project.catalog`, spatial source names and geographic/time coverage.
   The starter expects `P:/wflow_global/hydromt`, with `rivers: hydro_rivers_lin` and `lulc: globcover`.
   Another catalog can require different entry names.
3. Review `basin.region`, its `uparea` threshold in km², grid resolution and `data/output_locations.csv`.
   Inspect the delineated geometry and resolved locations before interpreting results.
4. Review historical climate sources and coverage, then the separate historical model period.
   The weather generator requires at least 16 years; the model run period must fit the available forcing.
5. Choose the retained model variables and optional observations.
   Use the [input-format reference](../technical-manual/input-formats.md) for units and station matching.
   The observation starter contains a header only, not a measured record.
6. Review scenario periods, realizations, monthly perturbation ranges and trajectories.
   The small starter ensemble/grid is an example, not an assessment recommendation.
   Choose projection windows separately and align them deliberately for a like-period plausibility comparison.

See [configuration](configuration.md) for the settings to edit and their consequences.

## Run in stages

1. Run WF0 alone first. The starter enables only `analyze_climate`.
   Preview from the toolbox root:

   ```powershell
   $config = 'C:/path/to/cst-cases/applications/my-basin/project_config.yml'
   pixi run python scripts/run_workflows.py --config $config --cores 3 -- --dry-run
   ```

   Remove `-- --dry-run` to execute. Review source coverage/comparison before choosing `climate.selected`.
2. Disable WF0 before enabling downstream stages. Disabling a workflow leaves previous results in place.
3. Enable WF1 for the historical model and WF3 for independent generated climate series.
   WF2 is an optional projection overlay; it never drives WF3.
4. Enable WF4 after the model and scenario collection are ready.
   Choose indicators and required retained variables before simulation; missing response variables cannot
   be recovered by recalculating indicators alone.
5. Inspect the exact execution summary and outputs, then record meaningful findings/provenance in `notes.md`.
   Register the case in its application inventory after the workflows complete.

Use [running](running.md) for resuming, experiment selection and recovery;
[outputs](outputs.md) explains completion evidence and table reading.
