---
title: WF0 lab setup instructions
lifecycle: temporary
created: 2026-10-03
updated: 2026-10-03
---

# Task Brief — Create the WF0 lab sibling project

### Context

Execute in a fresh Windows/PowerShell session rooted at `C:/Users/taner/workspace/wf0-lab`, creating that directory if absent. Do not execute this assignment as modifications to a BlueEarth task lane. The lab is a standalone place to develop historical climate diagnostics before later integration into BlueEarth.

Read this brief first, then [the starter proposal](wf0-starter-suite-proposal.md) and [the suite implementation brief](wf0-starter-suite-task-brief.md). If the lab already exists, read its `AGENTS.md` and inspect its state before making changes. User/global instructions still apply; BlueEarth's repository-specific lane, workflow, and testing rules do not govern this sibling project.

Suggested executor: GPT-6 Luna, high effort. GPT-6.1 Sol, high effort is an alternative if environment or packaging issues prove difficult. This is a task-specific recommendation, not a benchmark result; see [official model guidance](https://developers.openai.com/api/docs/guides/model-selection).

### Goal

Create a small, independently runnable Python project with its own environment, lightweight instructions, and a synthetic NetCDF-to-figure smoke example. Leave scientific suite implementation to the separate brief.

### Non-goals

Implementing SPI, trends, or other scientific diagnostics; modifying or integrating with BlueEarth; copying its infrastructure; creating CI, remote repositories, PRs, releases, task boards, agent registries, run manifests, or a web application.

### Allowed scope

- **Permitted:** create and edit files under `C:/Users/taner/workspace/wf0-lab`; install the lab's own environment; initialize a local Git repository if absent; make a single verified setup checkpoint.
- **Read-only:** `C:/Users/taner/workspace/blueearth_cst`, this task bundle, and any explicitly supplied climate data.
- **Approval-gated:** replacing an existing project, downloading climate datasets, publishing/pushing, or changes outside the lab. Do not silently change the user's global Git, Python, Pixi, or agent configuration.
- Inspect existing paths before creating files. If a partial lab exists, reconcile it; never overwrite user work or nest a Git repository accidentally.

### Required changes (checklist)

1. Create the following minimal structure. These are proposed targets to create, not claims that the files already exist. Create other directories only when needed.

```text
wf0-lab/
    README.md
    AGENTS.md
    CLAUDE.md
    .gitignore
    .git-workflow.yml
    .testing-policy.yml
    pixi.toml
    pixi.lock
    wf0_lab/
        __init__.py
        smoke.py
    docs/
        setup-brief.md
        starter-suite-proposal.md
        starter-suite-brief.md
    examples/
        input-paths.example.yml
    outputs/                 # ignored; created by the smoke example
```

2. Create an independent, minimal Pixi environment for Windows. Use Python 3.12, NumPy, pandas, xarray, SciPy, xclim, Matplotlib, netCDF4, PyYAML, pytest, and ruff from conda-forge where available. Add optional packages only for a demonstrated need. Start from dependency names used by BlueEarth, not its entire manifest or lockfile. Do not install R, Julia, Wflow, HydroMT, Snakemake, GDAL, DVC, or the toolbox package. Let Pixi generate the lab lockfile. Consult the pixi-env skill if available for setup or solver problems.
3. Keep the importable package at `wf0_lab/`. Running modules with `pixi run python -m ...` from the lab root is sufficient initially; no packaging/distribution framework is required. Do not add the toolbox to `PYTHONPATH` or install it editable.
4. Create a deterministic `wf0_lab.smoke` entry point. It generates a tiny, explicitly synthetic daily precipitation/temperature dataset, writes it under `outputs/smoke/`, reopens it, checks value/coordinate round-trip, and saves a simple PNG. Report the artifact paths and dependency versions. Its plot is an environment demonstration, not a scientific climate analysis.
5. Write a short README with purpose, exact installation/smoke commands, proposed development sequence, and the distinction between synthetic/testing data and actual long historical records. Use ignored `examples/input-paths.local.yml` for real absolute paths; the tracked example uses explicit placeholders. No actual climate data path has been selected for this assignment.
6. Copy this brief, the proposal, and the suite brief into the three `docs/` destinations above for self-contained handoff. Update their relative links to the local copies. Replace links to other BlueEarth task notes with explicit read-only source paths where needed; record the original bundle location rather than copying the whole research archive. The lab's copy becomes its implementation/resume record; this original toolbox bundle remains read-only during lab execution.
7. Author concise local instructions using the project-instructions skill if available. `AGENTS.md` should specify:
   - The lab is for local exploration, with explicit numerical checks before scientific claims.
   - Inputs and all toolbox checkouts are read-only; calculations and plotting must work without toolbox imports.
   - Work directly on one local branch. Use milestone commits after verified components, not branches/PRs for every edit. No pushes, release rituals, automatic workflow runs, or toolbox test gates.
   - A figure-style edit needs a render and visual inspection; a numerical edit needs a targeted reference/invariant check. Run only affected checks during iteration.
   - No required task board, design-review orchestration, or subagent dispatch. Use the suite brief's small phase index for resumption. Pause only for genuine ambiguity affecting correctness, unavailable required inputs, or authority boundaries.
   - Generated data/figures go under ignored `outputs/`; scratch under ignored `.tmp/scratchpad/`; machine-local input paths are ignored.
   - Keep definitions near functions. Notebooks may explore, but reusable calculations live in modules.
   Use `CLAUDE.md` only as a thin `@AGENTS.md` entry point. Keep the instructions under about 80 lines; do not copy BlueEarth's AGENTS.md.
8. Configure the lab's Git workflow with `mode: trunk`, `worktree_policy: none`, and `auto_push: false`. This is a local single-branch project, not a linked BlueEarth worktree. If Git is absent, initialize local `main`; do not invent identity settings if commits lack an author.
9. Set `.testing-policy.yml` to `scope: rapid`, `numerical: default`. The explicit task policy is targeted local verification during development; expensive toolbox checks are outside this project. Escalate scientific evidence when outputs are used in a report or decision.
10. Ignore `.pixi/`, generated outputs, scratch, caches, notebook checkpoints, and machine-local configurations. Track source, instructions, examples, the environment manifest and generated lockfile. Do not vendor or symlink the toolbox's agent configuration or Git hooks.

### Validation

Run from the lab root after creating the named module:

```powershell
pixi install
pixi run python -m wf0_lab.smoke
git status --short
git diff --check
```

Run installation once after the final manifest change; repeat only for an environment defect. Run the smoke example once after final setup and again only after fixing a concrete failure. Inspect the PNG. A focused round-trip assertion in the smoke program is enough; do not scaffold a broad test suite for setup.

Verify independence with `pixi run python -c "import wf0_lab; print(wf0_lab.__file__)"` and inspect source imports using `rg -n 'blueearth_cst|snakemake|sys.path' wf0_lab`. A lab module resolving outside the lab, a toolbox runtime import, or a toolbox path injection falsifies the isolation claim. Scan hits require interpretation, not automatic deletion. Record toolbox Git status before and after as a coarse write check; this does not prove all external files are immutable.

### Acceptance criteria

- The smoke command works using the lab environment and produces a readable PNG plus a verified synthetic NetCDF round-trip.
- No toolbox run, dependency, file edit, or environment change is needed.
- Local instructions explicitly preserve the lightweight development policy.
- The suite brief and proposal are readable inside the lab with working local links.
- A verified setup checkpoint exists if Git identity permits it; otherwise leave work intact and report that precise blocker.

### Output requirements

Return the project path, commands actually run and outcomes, smoke image path, model/effort used if observable, checkpoint SHA, and any unresolved environmental limitation. Distinguish instructions created from commands executed. Do not claim that the scientific suite has been implemented.

### Task constraints

Proceed through setup without asking permission for each ordinary file or command. Respect sandbox approvals; an approval failure is not authorization to relocate the lab into BlueEarth. If a required package cannot be installed, preserve the scaffold and report the dependency failure rather than changing global environments. Do not start suite implementation automatically after finishing setup.

## Launch prompt

Paste into a new SOL or LUNA session with access to the workspace:

> Create the standalone sibling project by executing C:/Users/taner/workspace/blueearth_cst/dev/tasks/t2610022259/wf0-lab-setup-instructions.md. Target C:/Users/taner/workspace/wf0-lab. Use the brief's lightweight local workflow and keep BlueEarth and its data read-only. Complete setup and its smoke example, then stop before scientific suite implementation. Report actual checks and the setup checkpoint.
