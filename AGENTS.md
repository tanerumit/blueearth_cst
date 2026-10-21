# AGENTS.md

> **Canonical.** Author repository instructions here; Codex reads this file and `CLAUDE.md` imports it.

## Overview

BlueEarth Climate Stress Test is a Python/R/Julia Snakemake workflow engine; no API or frontend code.

Read this worktree's local `STATUS.md` first when orienting or resuming for a quick view of active work
and next steps. Maintain it at meaningful checkpoints and handoffs using `project-system`.
It is ignored, lane-specific state: never commit, share, or summarize other lanes or the task board in it.
For initialization, lane reuse, and durable evidence, follow
[lane status](dev/reference/dev-task-and-session-workflow.md#lane-status).

| Entry point | ID | Purpose |
|---|---|---|
| `analyze_climate.smk` | wf0 | Optional, model-free historical climate analysis |
| `build_model.smk` | wf1 | Build Wflow-SBM from global data; run historical forcing |
| `analyze_projections.smk` | wf2 | CMIP6 change factors as a plausibility overlay |
| `generate_scenarios.smk` | wf3 | Model-independent, durable scenario collections |
| `scripts/simulate_system.py` | wf4 | Validated simulation and immutable retained-response indicators |

Convenience order: wf0 → wf1 → wf2 → wf3 → wf4. WF1 and WF3 are independent prerequisites of WF4;
WF2 never drives generation. WF0 shares region/climate producers: run it first or omit it;
run it alone when selecting forcing. WF4 consumes explicit run IDs.

## Background

CST is bottom-up decision-scaling/DMDU: a stochastic weather generator perturbs local climate over
a temperature × precipitation grid. Never couple that experiment to selected GCM scenarios.
There is no local calibration, so historical forcing choice matters. Prefer robust, automated,
first-order basin assessment from global data over site-specific sophistication.
Read the 2025 technical note in References before changing what a workflow computes.

## Repo Map

- `blueearth_cst/`: Snakemake-invoked Python/R modules, not standalone CLIs. `scripts/`: user execution
  entry points. `dev/scripts/`: repository maintenance and test helpers, never run dependencies.
  Move shared code into the shipped package when a maintenance helper gains a run-path caller.
- `config/advanced_settings.yml` is read for every project, never passed as `--configfile`.
  Its schema is closed: update `_ADVANCED_SETTINGS_SCHEMA` with every new key.
- Project config sets live beside their project, with seeds under `test_case/`; no `config/workflows/`.
  The project file has closed `{enabled, config_path}` workflow stanzas, composed with per-workflow
  files by `blueearth_cst/shared/config_composition.py`. Only `config_path` resolves against the project
  file; other paths resolve from the run directory. Cross-workflow keys belong in the project file's
  owning `basin:`, `climate:`, `model:` section or top level, never in workflow files.
- `config/defaults/` changes runs; `config/templates/` contains scaffolds only. Keep
  the single `config/templates/example-basin/` configuration starter current in the same
  change as parameter/schema/default changes; `scripts/create_case.py` scaffolds external cases from this checkout.
  Do not maintain a second starter in `cst-cases`. Keep the
  `project_config_` prefix on new seed configs or Git's glob silently excludes them.
  `config/catalogs/cmip6_data.yml` and `cmip6_store_index.json` are generated; never hand-edit them.
- Real basin data and production `project_dir` outputs live outside this repository, referenced by
  absolute project paths. Untracked `test_case/test_local` is the development-only exception.
- `dev/`: plans, retained findings, conventions and helpers; not shipped. Task folders and board belong to `main`:
  edit notes there and render with `python dev/scripts/todoboard.py render`; commit board-only changes
  separately. Never hand-edit generated `dev/TODO.md`. Save task documents in main's `dev/tasks/<id>/`;
  session `dev/TODO.md` and `dev/tasks/` link to main after board-view setup. Never use `git add --sparse`
  to create session-local task documents. Temporary material stays local under `.tmp/tasks/<id-or-purpose>/`;
  see `dev/reference/dev-repository-layout.md` for placement and cleanup.
- `docs/site/`: published documentation; `docs/notebooks/`: source notebooks; `docs/references/`:
  upstream guides. Historical migration guides live in `dev/records/milestones/`.
  Do not mirror configs into docs. Full layout: `dev/reference/dev-repository-layout.md`.
- `dev/scripts/console.py` is vendored: fix upstream in `console-formatting`, then re-copy.
  Ignored `.claude/`, `.codex/`, `.agents/` directories are linked into worktrees; absence downgrades,
  rather than fails, activation.

## Key Commands

Use `pixi run` or `pixi shell` for commands. Setup: `docs/site/setup/install.md`.

```powershell
pixi run python scripts/run_workflows.py --help
pixi run pytest tests/test_cli.py
```

Validate a DAG with `--dry-run` before execution and after rule edits. Use the owned all-workflow
runner for WF3 (enable only WF3 in its project config for a confined run); WF4 requires
`scripts/simulate_system.py` or the all-workflow runner. Do not execute WF3/WF4 through bare Snakemake.
The runner's module docstring and `tests/test_run_workflows.py` own its argument contract.
`tree-check`, `dev/scripts/prune_series_cache.py`, and `dev/scripts/prune_climate_store.py`
are report-only until `--delete`. DAG rendering: `scripts/plot_workflow_dag.py`.
On Linux use `test_case/project_config_baseline_linux.yml`; its P-drive catalog also resolves
`/mnt/p` and `/p`. The auto-loaded `profiles/default/config.yaml` sets `quiet: reason`;
remove that setting when diagnosing why a job reran.

## Conventions

- Use `dev/reference/README.md` to find the current topic owner before changing guidance. Update that
  document in place; records provide historical evidence, not current instructions. Templates belong in
  `dev/templates/`. Follow `dev/reference/dev-record-lifecycle.md` for promotion and the simple reference format.
- Keep detailed guidance in one authoritative document. Elsewhere, use a pointer and a short explanation
  of when to read it; update the owning document instead of repeating its rules.
- Follow `dev/reference/dev-naming-conventions.md`; existing names are grandfathered. Contract renames need a
  migration note. Update every live old path/key/command reference, including docs and comments.
  Only records with a `SUPERSEDED` banner and entry in `dev/records/sealed-records.yml` are frozen;
  do not infer archival status from age.
- Snakefiles use `get_config(config, key, default, optional)`: raise for missing required keys;
  return defaults for optional ones. Forward `workflow.configfiles[0]` as `config_path` to R scripts.
- Register sources in `config/catalogs/*_data*.yml`, passed to HydroMT via `-d`; no hardcoded
  data paths in Snakefiles. Install and usage prose belongs in `docs/`.
- No silent coverage caps: report dropped top-N, sampling, or no-retry coverage.
- Read `log_row`'s docstring before writing console rows. Keep each row on one physical line;
  use `listed` to cap data-dependent lists.
- Python `script:` modules read `snakemake.input/output/params`, not `sys.argv`. R scripts use
  `Rscript --vanilla` and positional `commandArgs(trailingOnly=TRUE)`.
- netCDF is the R/Python/Julia interchange format. Mark intermediate per-realization netCDFs
  with `temp(...)` to bound disk use at large realization × scenario counts.

## Validation ladder — match the check to the blast radius

Before selecting checks, landing, or pushing, read `dev/reference/dev-validation.md`.
It owns the validation ladder, exemptions, evidence reuse, execution coverage, config provenance,
and CI procedures. Select coverage from changed behavior and affected consumers.

Use affected checks for commits and local landing; apply the batch gate before pushing or releasing.
Local main may contain undiscovered regressions pending that gate. Reuse applicable
evidence; stop when required coverage is sound. Execution success never replaces independent
numerical checks or visual inspection. Use rapid inputs for execution/DAG checks and renders;
consult the reference before making baseline claims.

## Session lifecycle

Use `git-workflow` and `dev/reference/dev-task-and-session-workflow.md` for session allocation,
synchronization, and cleanup. Stay in the occupied session across follow-ups. The user controls
switching and landing; completion does not authorize landing or pushing.

## Hard Constraints

- Julia is juliaup-managed and must be on `PATH`; never add it to Pixi (no conda-forge win-64 build).
- Never commit run outputs or hand-edit `pixi.lock` or `Manifest.toml`.
- No root cache directories. For isolated Ruff, set PowerShell `$env:RUFF_CACHE_DIR = '.tmp/ruff_cache'`.
- Use HydroMT/hydromt_wflow/Wflow standard names, schemas, catalogs and `setup_*` conventions verbatim.
  Do not re-engineer upstream data handling or physics. Read upstream docs to validate our configuration;
  flag upstream bugs or work around them in our code, never patch a vendored package.

## References

- `README.md`: workflow execution and pipeline; start here.
- `dev/reference/dev-task-and-session-workflow.md`: before board coordination, worktree handoff, or task closure.
- `dev/reference/dev-record-lifecycle.md`: before promoting, shortening, superseding, or deleting dev records.
- `dev/reference/dev-documentation.md`: before authoring or reviewing user guides,
  scientific-method pages, toolbox reference, or technical notes.
- `dev/reference/toolbox-plot-style.md`: before scientific plots/review pages; preserve defaults/exceptions and
  record newly approved styles. `dev/reference/dev-versioning.md`: before release/version decisions.
- `docs/references/cst-toolbox-technical-note-2025.md`: methodology; code/current references win on stale
  pipeline details, paths and artifacts.
- `dev/reference/dev-validation.md`: verification planning, affordability, unexpected gates and CI.
- `dev/reference/dev-repository-layout.md`, `dev/reference/dev-naming-conventions.md`: placement and naming decisions.
- `dev/reference/toolbox-workflow-map.md`: before adding/editing rules.
- `docs/site/setup/install.md`, `docs/site/setup/env-setup-notes.md`: Pixi/R/Julia setup problems.
- `docs/references/hydromt-user-guide/00-index.md`, `docs/references/hydromt-architecture.md`:
  model-build config, catalogs and regions.
- `docs/references/hydromt-wflow/` (`getting-started.md`, `user-guide.md`, `api.md`):
  plugin build/update/clip behavior and signatures.
- `docs/references/wflow-user-guide/00-index.md`: TOML, warm states and Wflow run configuration.
