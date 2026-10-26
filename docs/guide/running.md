---
title: "Running the workflows"
subtitle: "Preview, execute and resume your case"
---

Run commands from the toolbox root with its Pixi environment available.
Use the same checkout for repeat runs of a project and one active run per output directory.
The runners handle workflow preparation and record each attempt; do not bypass the owned WF3/WF4 runners.

## Create an external case

Follow [Create your own case](new-case.md) for scaffolding, data checks and staged workflow enablement.
The maintained starter is in this toolbox checkout, not a second cases-repository template.

## Run everything enabled in the project file

1. Select your project file and review which workflows have `enabled: true`.
   The runner uses WF0 → WF1 → WF2 → WF3 → WF4 for those enabled.
   WF1 and WF3 independently supply WF4; WF2 is optional context and never supplies generated scenarios.
   Run WF0 first or alone when choosing forcing.
2. Preview the enabled workflows:

   ```powershell
   pixi run python scripts/run_workflows.py --config <config> --cores 3 -- --dry-run
   ```

   Replace `<config>` with your project YAML. Check the resolved output root.
   Add `--project-dir <output-root>` to override it explicitly.
   A dry run may remain partial until upstream products/checkpoints exist.
3. Remove `-- --dry-run` to execute. The runner stops if a workflow fails.
4. Open the exact `summary.md` linked in the closing console output.
   Check outcomes and retained products before treating results as complete.

Disabled workflows leave their old results in place. Check that reused model, basin, forcing and
scenario products still match the case you intend to assess.

## Run one workflow

Enable the workflow in the project file, then use its individual runner. For example:

```powershell
pixi run python scripts/run_workflow.py build_model --config <config> --cores 3 --dry-run
```

Remove `--dry-run` after reviewing the plan.
Use `analyze_climate`, `analyze_projections`, `generate_scenarios` or `simulate_system` in place of
`build_model` for another workflow. This runner starts only the named workflow, not missing prerequisites.
WF3 supports target `all`; WF4 needs a ready model and scenario collection.
For confined WF3 work through the all-workflow runner, enable only WF3.

- `--config`: the project file naming shared choices and workflow files.
- `--project-dir`: optional output-root override.
- `--cores`: CPU budget; more concurrency can increase memory needs.
- `--target`: requested target; `all` is the usual choice.
- `--dry-run`: direct preview flag on the individual runner.

The all-workflow runner forwards options after `--`, including `-- --dry-run`.
The individual runner also forwards options after `--` to its owned runner.
Use [troubleshooting](troubleshooting.md#a-project-is-locked-or-a-run-was-interrupted) for incomplete jobs
and stale locks, after confirming that no run is active.

### Execution logs and benchmarks

Open `logs/<UTC timestamp>__<workflow scope>/summary.md` first.
It links the console transcript, workflow logs and any collected benchmarks.
Each attempt has a separate folder; dry runs and reused work need not have new benchmark samples.
For exact measurements and their limits, see [benchmarking](benchmarking.md).
The [execution reference](../technical-manual/execution-and-provenance.md) owns record/layout details.

## Run a project from one toolbox checkout

Different checkouts keep separate workflow state and can disagree about current outputs.
Continue a case from its selected checkout; do not run two copies against the same output root.

## Regenerate figures after visual changes

When only styling, titles or captions change, target the plotting rule using the same project config
and output root as the completed run. From the toolbox root, preview first:

```powershell
pixi run python scripts/run_workflow.py analyze_projections `
  --config C:/path/to/project.yml --project-dir C:/path/to/existing-run `
  --target plot_climate_projections --dry-run -- --force --notemp
```

Check the scheduled jobs, then remove `--dry-run` to render. `--force` reruns the selected target;
`--notemp` preserves temporary inputs. Avoid `--forceall`, which also forces upstream jobs.
Missing or stale inputs can still schedule upstream work: inspect the dry-run before proceeding.

Substitute the workflow and target below. Repeat `--target` to select several rules in one workflow.
Replace `<source>` with its configured ID, for example `plot_climate_diagnostics_era5`.

| Figures | Workflow | Target |
|---|---|---|
| WF0 source diagnostics | `analyze_climate` | `plot_climate_diagnostics_<source>` |
| WF0 comparison | `analyze_climate` | `plot_climate_comparison` |
| WF1 spatial maps | `build_model` | `plot_basin_map` |
| WF1 forcing | `build_model` | `plot_model_forcing` |
| WF1 evaluation | `build_model` | `plot_model_evaluation` |
| WF2 projections | `analyze_projections` | `plot_climate_projections` |

Retain the diagnostic tables/map fields, projection-analysis tables, forcing and spatial inputs.
WF1 retains `<model>/run_default/output.csv` by default, so evaluation and table exports can reuse
the full-precision native responses. Older projects where this file was deleted require one historical
simulation to restore it; rounded exported tables cannot replace it.

Currently, WF0 comparison recomputes its statistics from retained daily series, WF1 forcing recomputes
plotting summaries, and WF1 evaluation recomputes indicators. These are combined calculation/rendering
steps. Other listed targets reuse prepared products. Title and caption inventories are refreshed with
the figures. Set project-level `plotting.annotation` to `none`, `caption` or `title` to choose
the annotation at the existing plot paths; changing this parameter schedules the plotting jobs.

## Rebuild outputs for testing

To recreate results in an existing project directory, use `--rebuild`:

```powershell
# Preview the erasure plan without changing files or starting workflows.
pixi run python scripts/run_workflows.py --config <config> --rebuild -- --dry-run

# Display the plan and ask Continue? [y/N]: before erasing anything.
pixi run python scripts/run_workflows.py --config <config> --rebuild

# Confirm explicitly for an automated test run.
pixi run python scripts/run_workflows.py --config <config> --rebuild --yes
```

This is a **project-wide, permanent reset**, including outputs of disabled workflows.
It erases `data/spatial/`, `data/climate/`, `models/hydrology/wflow/`, `scenarios/`,
and `experiments/`. It also removes the active WF0–WF2 configuration captures,
their pending replacement state, and generated execution configs. Archive transaction journals for
erased scenario collections and experiments are also removed, including stale journals whose archives
are already missing. No backup is made.
The source configuration and seeds are unchanged; only enabled workflows run afterward.
All experiments and their allocation state are removed, so automatic numbering starts again.

Source configuration, referenced source datasets, unrelated project paths, logs, invocation history,
and historical configuration snapshots are preserved. Project-local extracted climate stores are
generated outputs and are erased; external source datasets and acquisition caches are untouched.
Keep custom files outside the generated namespaces: their contents are treated as output. A configured
input overlapping one of these namespaces, a linked path, repository metadata, or a changed plan causes
refusal before erasure.
The project execution lock remains held throughout reset and workflow execution.

Press Enter or answer anything other than `y` or `yes` to cancel. Non-interactive invocations require
`--yes`; `--yes` alone is invalid. The rebuild dry-run only previews erasure, rather than building the
Snakemake DAG against the old results. It writes no run records. A failure during erasure or subsequent
execution stops the run without rollback; the invocation record identifies whether reset completed.

For WF4, enable WF1 and WF3 as well, because their retained inputs will be erased. Include simulations
in WF4's operations; indicators-only cannot rebuild deleted model responses. `--rebuild` cannot combine
with `--new-experiment`, `--recover-reservation`, forwarded config/directory overrides, or bookkeeping
modes such as `--unlock`. Use `--new-experiment` instead when previous experiments should remain available.

## Select, resume or create an experiment

With no `experiment_name`, the first run reserves `stress_test_01`. A plain rerun
selects the highest allocated number, whether complete or interrupted. Unfinished simulations
continue there if their scientific inputs still match; intact completed outputs are reused.

For another experiment, pass the flag to either execution runner:

```bash
python scripts/run_workflows.py --config <config> --new-experiment --note "revised perturbation grid"
python scripts/simulate_system.py --config <config> --new-experiment --target all
```

Set `experiment_name: drought` to use the `drought_01`, `drought_02` family.
An exact name such as `drought_02` pins that identity and cannot combine with
`--new-experiment`. The flag creates an experiment; it does not force regeneration
of an unchanged ready scenario collection.

If scientific inputs changed and the flag was omitted, the runner refuses before
producers start, for both complete and interrupted numbered experiments. Notes,
resource settings and indicator choices do not redefine those scientific inputs.
Deleted allocations remain consumed; numbers are never automatically recycled.

`scripts/suggest_experiment_name.py <config>` and dry-runs only preview selection.
They neither reserve directories nor edit YAML. For an interrupted reservation
or paired intent/archive publication, `--recover-reservation` finishes only a
verified retained recipe. It cannot repair partial WF3 generation or missing or
corrupt native responses; retain that evidence for diagnosis.

Completed batch checkpoints can be reused after an ordinary failed run. A hard
stop while writing a native CSV or restoring a batch may leave partial outputs
that need diagnosis; reservation recovery does not repair those files.

To skip unperturbed realizations in WF4, set `include_unperturbed: false` in its
`project_config_simulate_system.yml` simulation file. The default is `true`. WF4 then prepares
forcing and simulates only perturbed members; WF3 keeps the complete collection.
Existing run IDs stay unchanged. Changing this switch requires `--new-experiment`.
Indicators are calculated only for simulated members and their design-point groups.
Indicators needing unperturbed reference runs (such as wet/dry reference-month indicators)
require `true`; otherwise select a set without them or use `operations: [simulations]`.
Indicators-only runs always use the retained simulation's members.

## Calculate different indicators from existing simulations

You can calculate different indicators from completed simulations without rerunning the model.
The selected experiment must have a completed `_engine/simulation.json` record, even for a dry run.

Open your case's simulation settings file: `project_config_simulate_system.yml` in the starter.
If your case uses another filename, find it under `workflows.simulate_system.config_path` in
`project_config.yml`. The rapid example uses `project_config_rapid_simulate_system.yml`.

1. Keep the existing `experiment_name`.
2. Set `operations: [indicators]`.
3. In `indicator_sets`, list the sets you want to calculate.

For example, if your completed experiment is `stress_test_01`, the relevant settings are:

```yaml
# project_config_simulate_system.yml
experiment_name: stress_test_01
operations: [indicators]
indicator_sets: [default]
```

Then run:

```bash
python scripts/simulate_system.py --config <config> --cores 3
```

The runner reads the retained model responses and writes each selected set to its own
`results/indicator_sets/<set-id>/` folder.
You do not need `--target`; the runner infers it.
You can also use the all-workflow runner with the other four workflows disabled.
See [Reading the outputs](outputs.md) for the result files.

An experiment is tied to its scenario collection, model, and simulation settings.
Use `--new-experiment` when those simulation inputs change.
For a fresh experiment, use `operations: [simulations, indicators]` to run the model before
calculating indicators.
Enabling other workflows does not change `operations: [indicators]` into a simulation request.

## Next

- [Choose indicators](indicators.md) and check required responses.
- [Read outputs](outputs.md) and retain their provenance.
