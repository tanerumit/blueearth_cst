---
title: "Running the workflows"
subtitle: "Run a whole assessment or one workflow at a time"
---

Run all enabled workflows with `scripts/run_workflows.py`. To run one workflow,
use `scripts/run_workflow.py <workflow_name>`. Scenario generation and simulation
delegate to their dedicated runners.

The runners hide routine Snakemake startup chatter during execution. Warnings,
errors and workflow diagnostics remain visible, and Snakemake's log files retain
the full record. Dry runs and `--verbose` keep native startup output.
Routine map-extent padding notes are omitted; map-overlap warnings remain visible.
WF4 reports checking, calculating and saving indicators by their selected set names.
Its final summary links each set's results, identifies reused results, and reports
missing or invalid values. If one set fails, it states whether earlier results
remain available. Internal request and publication identities remain in the
retained manifests and the execution's `wf4-indicators.log`.

| Workflow | What it does |
|---|---|---|
| Historical climate (`analyze_climate`) | Compare climate data sources before choosing the forcing for the model; optional |
| Model (`build_model`) | Build Wflow-SBM and run it with historical climate data |
| Projections (`analyze_projections`) | Calculate CMIP6 changes to compare with the stress-test range |
| Scenarios (`generate_scenarios`) | Generate climate series for the chosen perturbations |
| Simulation (`simulate_system`) | Run the model with those series and calculate indicators |

The runner uses this order: historical climate → model → projections → scenarios
→ simulation. Model building and scenario generation are both needed before
simulation. Historical climate analysis is optional. CMIP6 projections provide
context for the tested changes and never supply the generated scenarios.

## Create an external case

For a new external case, create its configuration set from the cases repository's
`templates/example-basin/` starter. From the toolbox root:

```powershell
pixi run create-case my-basin --cases-root C:/path/to/cst-cases --longitude 12.5 --latitude -3 --purpose "First-order basin assessment" --dry-run
```

The starter defaults to `config/catalogs/deltares_data_pdrive.yml` and
data under `P:/wflow_global/hydromt`; mount the Deltares P-drive before
running. Its basin sources use `rivers: hydro_rivers_lin` and
`lulc: globcover`. The scaffold inherits the catalog and source settings
from the cases repository's template.

Remove `--dry-run` after reviewing the preview. The command creates
`applications/my-basin/`, sets absolute input and output paths, replaces the
outlet coordinates, and starts fresh `configured; not run` case notes. It
preserves the template's scientific settings and starts with historical climate
analysis alone. The template's `basin.region` upstream-area threshold (`uparea`,
km²) is retained; review it for the outlet before running. Register the case in
the application inventory after the workflows complete. Use `--catalog` to override the
template's data catalog with a
toolbox-relative or absolute path. Review catalog coverage and climate/scenario
settings before running. Existing applications are refused;
outputs under `runs/my-basin/` are neither created nor modified.

The scaffold uses `runs/my-basin/` as its output root. Choose another path in
`project.project_dir` or with `--project-dir` when retaining a separate assessment.
Existing paths, including `active/` folders, remain valid and are not moved or archived.

Each scaffolded YAML file starts with a commented title, filename, project name,
creation timestamp (local time with UTC offset), and controlling workflow ID and name.
The project file identifies shared settings and workflow enablement. Workflow labels
follow `workflows.*.config_path`, including custom filenames. All files and
`INSTRUCTIONS.md` share one creation timestamp; existing case files are not updated.

Parameters also receive short definitions and `Input:` or `Options:` hints, drawn from
the toolbox's maintained configuration templates. Existing explanations and settings
are preserved. Custom parameters without template help receive a basic YAML type hint.

Read the generated `INSTRUCTIONS.md` for preview and execution commands and
a guide to the output folders. After
selecting forcing, disable historical climate analysis before enabling downstream
workflows. The scaffold does not run workflows or commit files.

## Run everything enabled in the project file

```bash
pixi shell
python scripts/run_workflows.py --config test_case/project_config_rapid.yml --project-dir test_case/test_rapid --cores 3
```

The runner follows the `enabled:` choices in the project file and stops if a
workflow fails. It records the result of each attempt under
`<project_dir>/config/_engine/invocations/`, including checks and failed
runs. Set `enabled: false` for a workflow you want to skip. Check that any
earlier results used by a later workflow still match your current project
settings.

Historical climate, model building, and projections reuse completed steps when
their consumed settings and dependency contents are unchanged. You can rename
or move project/workflow configuration files, update their `config_path` links,
or enable other workflows without rebuilding those steps. Paths to scientific
data must still resolve to the same inputs. Each launch archives the original
configuration files and paths separately from the stable execution view.
Changing relevant settings or dependency contents still invalidates affected
work. Existing runs may rebuild once after upgrading to this execution-view
format; subsequent equivalent configurations reuse the staged inputs.

To preview the enabled workflows, add `-- --dry-run` to the command. A dry run
may show only part of a workflow until inputs from an earlier step exist.

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

Rule 0.05 was renamed from `compare_climate_diagnostics` to `plot_climate_comparison`.
Update saved `--target` commands; log and benchmark parts use the new name. Output data and figure
paths are unchanged. Historical log parts are retained under their original names.

Retain the diagnostic tables/map fields, projection-analysis tables, forcing and spatial inputs.
WF1 evaluation also needs `<model>/run_default/output.csv`; a missing file can require another
historical simulation. Use `--notemp` on the original model run to retain it.

Currently, WF0 comparison recomputes its statistics from retained daily series, WF1 forcing recomputes
plotting summaries, and WF1 evaluation recomputes indicators. These are combined calculation/rendering
steps. Other listed targets reuse prepared products. Title and caption inventories are refreshed with
the figures. Set project-level `plotting.annotation` to `none`, `caption` or `title` to choose
the annotation at the existing plot paths; changing this parameter schedules the plotting jobs.

## Run one workflow

From the toolbox root, after `pixi shell`, use the individual runner for any
workflow. Enable the selected workflow in the project config:

```bash
python scripts/run_workflow.py analyze_climate --config test_case/project_config_rapid.yml --project-dir test_case/test_rapid --cores 3
python scripts/run_workflow.py build_model --config test_case/project_config_rapid.yml --project-dir test_case/test_rapid --cores 3
python scripts/run_workflow.py analyze_projections --config test_case/project_config_rapid.yml --project-dir test_case/test_rapid --cores 3 --keep-going
python scripts/run_workflow.py generate_scenarios --config test_case/project_config_rapid.yml --project-dir test_case/test_rapid --cores 3
python scripts/run_workflow.py simulate_system --config test_case/project_config_rapid.yml --project-dir test_case/test_rapid --target all --cores 3
```

The individual runner launches only the named workflow; it does not run missing
prerequisites. WF3 delegates to the generation runner and supports only target
`all`. WF4 delegates to the simulation runner and needs a ready model and scenario
collection. The dedicated runners remain available.

The flags most users need are:

| Flag | Effect |
|---|---|
| `--config` | project file with basin and workflow settings |
| `--project-dir` | directory where this project writes its results |
| `--cores` | CPU budget for the run |
| `--target` | simulation outputs to produce; `all` is the usual choice |
| `--dry-run` | show planned steps without running them |

The all-workflow runner passes options after `--` to each enabled workflow.
For example, `-- --dry-run` checks each workflow. The individual runner accepts
`--dry-run` directly for all five workflows and forwards options after `--` to
the selected owned runner.

If Snakemake reports that the directory is locked after an interrupted run,
first make sure no other process is using the project. Then clear the lock for
the affected workflow, for example:

```bash
snakemake --unlock -s build_model.smk --configfile test_case/project_config_rapid.yml
```

If a run exhausts memory, lower `--cores` and rerun it. Larger basins and longer
scenario collections need more memory and disk space; timings and resource use
are recorded with the execution logs described below.

### Execution logs and benchmarks

Every supported launcher attempt gets a new directory, including dry runs and startup failures
when the project root is known:

```text
logs/<UTC timestamp>-<short invocation ID>/
  summary.md
  console.log
  wf0.log ... wf4.log
  wf0-benchmarks.md ... wf4-benchmarks.md
  wf0-benchmarks.tsv ... wf4-benchmarks.tsv
  wf4-indicators.log
  _parts/
```

Open `summary.md` first. It links the canonical invocation records, workflow logs, benchmarks and
resource diagnostics. `console.log` retains launcher and child output in observed order, without
terminal colours or repeated progress redraws. Workflow logs retain the detailed rule/member view.
Only collected outputs appear: dry runs and reused steps need not produce rule logs or benchmarks.
Missing measurements are not zero costs, and unknown reuse remains labelled unknown.

Managed launches merge rule logs and benchmarks when the invocation finishes. These diagnostic files
are not required DAG targets, so a fresh execution folder does not schedule gather rules when all
scientific outputs are up to date. Direct Snakemake runs retain their gather targets.

Initial runner preparation messages use two-space indentation without timestamps or module labels,
including elapsed-time updates such as `  Workflow preparation 0:00:15 elapsed`.

WF4 retains an experiment's original simulation identity and provenance when only execution-diagnostic
code changes. Scientific input or simulation-code changes still require a new experiment. A refusal
before workflow execution skips indicator publication; partial job failures still allow completed
indicator sets to publish independently.

Benchmark Markdown starts with the recorded workflow elapsed time and a table grouped by rule:
job/sample counts, summed job time, median, slowest job and peak individual-job RAM. Expand the
individual-job section for CPU and I/O measurements; the adjacent TSV retains precise samples.
Summed job durations can overlap and are not workflow elapsed time. Peak job RAM is not concurrent
workflow memory. WF4 reports available Julia load, compilation and later-member timings separately.

Each workflow's `_parts/` namespace belongs to its child invocation; WF3 source and generation
phases share that child. Successful gathers remove their merged parts; failures retain partial
logs and benchmark fragments. Retrying creates another execution directory and never merges old
parts. Previously written top-level workflow logs and `benchmarks/` reports remain historical;
they are not reassigned to new executions.

Configuration archives keep their existing locations under `config/`; resource traces remain under
`config/_engine/invocations/`. Removing an execution's diagnostic folder does not remove its
configuration provenance or scientific outputs.

The all-workflow console includes the selected experiment and its action in the
opening settings, describes subbasin outlets with their upstream-area threshold
in km², and distinguishes disabled workflows from pending ones. Long settings
and command paths wrap within the terminal width; redirected output uses 100 columns.

On color-capable terminals, launcher and workflow rows retain their colour scheme and animated
progress bars while console capture is active. Warning rows use orange without a `WARNING` column.
Redirected output stays plain; `NO_COLOR` disables colours while retaining terminal progress updates.
Saved transcripts omit terminal colours and repeated redraws; detailed workflow logs retain warning levels.
Coordinate adjustments share one heading, followed by each location's original and resolved coordinates.

The final summary totals the toolbox warning rows counted during this invocation
and lists the contributing workflows. WF3's total includes its source and generation
phases. The `commands` row points to a `.commands.txt` receipt beside the invocation
record. Copy its location-setting line and one workflow block to rerun through the
supported runner using the current configuration and experiment selection. The receipt
preserves complete arguments and uses PowerShell
continuations on Windows or shell continuations elsewhere. Credential-like values
are redacted; replace those placeholders before use. Hard-wrapped display paths
are for reading and must not be pasted as commands.

When a job fails, the console prints a prominent `FAILED` block naming its rule
(with the toolbox rule ID when available), Snakemake job ID, and individual log
paths alongside the original error details. Concurrent failures and
failed grouped jobs identify each affected job. The closing workflow summary
also points to the retained log parts. Errors before any job starts retain
Snakemake's original diagnosis.

::: {.callout-note}
## Run a project from one toolbox checkout

Use the same toolbox checkout for repeat runs of a project. Running one project
from two copies of the toolbox can give conflicting decisions about which
results need to be refreshed.
:::

## Select, resume or create an experiment

With no `experiment_name`, the first run reserves `stress_test_01`. A plain rerun
selects the highest allocated number, whether complete or interrupted. Compatible
unfinished simulations continue there; intact completed outputs are reused.

For another experiment, pass the flag to either execution runner:

```bash
python scripts/run_workflows.py --config <config> --new-experiment --note "revised perturbation grid"
python scripts/simulate_system.py --config <config> --new-experiment --target all
```

Set `experiment_name: drought` to use the `drought_01`, `drought_02` family.
An exact name such as `drought_02` pins that identity and cannot combine with
`--new-experiment`. Existing owned dated or unnumbered names remain explicit
legacy selections. The flag creates an experiment; it does not force regeneration
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
`simulate_system` configuration file. The default is `true`. WF4 then prepares
forcing and simulates only perturbed members; WF3 keeps the complete collection.
Existing run IDs stay unchanged. Changing this switch requires `--new-experiment`.
Indicators are calculated only for simulated members and their design-point groups.
Indicators needing unperturbed reference runs (such as wet/dry reference-month indicators)
require `true`; otherwise select a set without them or use `operations: [simulations]`.
Indicators-only runs always use the retained simulation's members.

## Calculate different indicators from existing simulations

An experiment is tied to its scenario collection, model, and simulation
settings. Use `--new-experiment` for changed simulation inputs.

To calculate different indicators from completed simulations, set
`operations: [indicators]` in the simulation settings file, keep the existing
`experiment_name`, and list the sets to publish in `indicator_sets`:

```bash
python scripts/simulate_system.py --config <config> --cores 3
```

The selected experiment must have a completed `_engine/simulation.json` record.
This prerequisite also applies to dry runs. For a fresh experiment, use
`operations: [simulations, indicators]` to run the model before calculating indicators;
enabling the other workflows does not override an indicators-only selection.

This reads the retained model responses and publishes each selected set to its
own `results/indicator_sets/<set-id>/` folder without rerunning the model. The
all-workflow runner does the same when the other four workflows are disabled.
No `--target` is needed; the runner infers it. The legacy `operation:
indicators-only` setting still works for one release with `--target
simulations_and_indicators`. See [Reading the outputs](outputs.md) for the
result files.

## Next

- [Reading the outputs](outputs.md) — what the run wrote, and how to tell
  whether it is still current.
