# AGENTS.md

> **Canonical.** Author repository instructions here; Codex reads this file and `CLAUDE.md` imports it.

## Overview

BlueEarth Climate Stress Test is a Python/R/Julia Snakemake workflow engine; no API or frontend code.

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

Read `dev/reference/dev-validation.md` before planning verification, selecting gates, landing,
or pushing. It owns acceptance-to-check/input/output mapping, evidence reuse, config provenance,
`verify_landing.py`, and CI procedures. Execution success never replaces numerical/visual acceptance.

Use `git-workflow`'s configured session lifecycle. A modifying request permits a clean detached
session to claim itself with `task-start --task <task> --session <name> --base main --no-launch`
from the primary checkout; never create the branch by hand. The user controls switching and landing.
At new-session entry, synchronize a clean local unpushed lane with `main` by rebase; published lanes
use merge unless rewriting is authorized. Resolve dirty state/conflicts without automatic stash/reset.
Do not repeat synchronization per follow-up. Commit tasks with focused checks; select landing gates
from the unverified delta and affected consumers, retaining applicable evidence. Completion does not authorize
landing/pushing. After a verified merge, prove ancestry, detach/free the lane, then delete its branch;
on failure preserve the lane and branch for recovery.

| When | Required coverage |
|---|---|
| Iterating | Tests covering the change |
| Pre-commit | Regression/consumer checks; affected CLI/DAG checks for rule/input/script changes; scoped Ruff |
| Final Python batch | `pixi run lint` and `pixi run format-check` once |
| Land a batch | One `test-fast` on the integrated candidate, or reuse evidence; exempt-only diffs skip it |
| Additional software coverage | Affected contracts; local full for needed extra coverage, replacing fast |
| Several workflow handoffs or shared runtime behavior | All-five local or live E2E, or reuse evidence |
| Confined workflow behavior | Affected integration path/consumers; execution when outputs can change |
| Numeric output | Independent numerical check and affected consumers; baseline for whole-tree claims |
| Release or milestone | Verify candidate and delta coverage; labels alone add no tests |
| Push | Reuse landing evidence; check uncovered changes, run cheap hooks, and inspect CI |
| After push | Read the latest CI run, including both platforms |

Apply the reference's evidence-reuse contract: full covers fast on the same candidate/environment;
equivalent merges need tree-equality and ancestry proof. Missing or skipped required checks never pass.
Classify behavior and consumers, not directory names. A small follow-up invalidates only affected
claims; use reviewed delta evidence rather than repeating a preceding broad gate. Unknown or broad
impact escalates. Console changes affecting control flow, exit status or parsed output are behavioral.
Optimize verification for safety with the fewest sufficient tests and procedures. Add a test, gate,
receipt or review step only for a concrete risk not covered by existing evidence or a simpler check;
prefer extending or replacing an existing check. Do not turn a one-off diagnostic into a standing gate.
Focused checks suffice for task commits; do not pull landing gates forward into each task. Full covers
fast; E2E covers its affected workflow executions. Stop once required coverage is sound; repeat only
for invalidated evidence or a concrete diagnostic need. Keep rationale in existing task notes or the
completion report; this rule requires no new checklist, document or approval step.
The local E2E gate regenerates every downstream product from staged source inputs. Use focused fetching
tests for acquisition changes; opt into live E2E when verifying catalog availability, addressing,
windows, clipping or cache behavior. A release or milestone label alone does not require live fetching.
See `dev/reference/dev-validation.md` for bundle qualification and refresh.
Use policy-tooling tests only when changing that tooling or its contracts, not merely using its verifier.

Push exemption covers modifications only to `dev/tasks/**`, `dev/TODO.md`, `dev/LOG.md`, root
`AGENTS.md` and root `README.md`. Renames/deletions are never exempt. `dev/scripts/`, `dev/records/`,
`dev/reference/`, `config/templates/` and `docs/notebooks/` have test readers and remain gated.
Classify actual diff paths, not commit labels or earlier pushed batches; grep tests before adding
an exemption. For push, inspect `origin/main..main` and reuse valid landing evidence. Changed content
needs affected checks or a missing batch gate, not an automatic repeat. Read red/unread CI and diagnose
its failures; CI status alone does not invalidate matching local evidence. An exempt-only unpushed delta
needs only the Ruff pre-push hook. CI owns full software coverage on both platforms. Capture gate output
in a file, never pipe it through `tail`.

CI runs for `main` pushes and PRs, not backup branch pushes. Normal approved publishing goes to
`main`; use a PR when the change needs two-platform assurance before landing.
`gh` defaults to Deltares upstream here: explicitly select
`tanerumit/blueearth_cst`. Install local hooks with `core.hooksPath .githooks`.

Use rapid config for execution/DAG checks/renders; baseline config only when numbers are the point.
Never baseline-check the rapid tree. WF2-fast is restricted iteration with declared coverage loss.
The baseline manifest is stale after the P-drive/GlobCover switch: regenerate the revised baseline
and re-record before numerical gating. Each worktree's untracked baseline tree is independent;
inspect its provenance. WF1 retains native `run_default/output.csv`; rounded `output_q.csv`
is no substitute. The standing tree is not an R12 migration reference: use matched P0/GF-9 evidence.
Details and recovery prerequisites live in the validation reference.

For figure-only changes, render and publish PNG artifacts for visual inspection; no baseline,
full suite or render-byte comparisons. Search shared plotting callers and render all affected figures.
Changes to runtime/config contracts or non-figure consumers trigger broader gates. For confined
workflow execution, state affected consumers and omitted workflows; rapid must not silently narrow coverage.

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
