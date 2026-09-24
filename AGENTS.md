# AGENTS.md

> **Canonical.** Single source of truth for every runtime. Codex reads this file directly; `CLAUDE.md` is a thin entry point that imports it (`@AGENTS.md`). Author repo instructions here, never only in `CLAUDE.md`.

## Overview

BlueEarth Climate Stress Test — a multi-language (Python + R + Julia) scientific workflow toolbox stitched together by Snakemake. Five root `*.smk` files define the workflows. Simulation requires `scripts/simulate_system.py` or the all-workflow runner to validate its operation and targets. Narrative: `README.md`.

| entry point | id | does |
|---|---|---|
| `analyze_climate.smk` | wf0 | the basin's historical climate — model-free, optional for the pipeline |
| `build_model.smk` | wf1 | builds the Wflow-SBM model, runs it on historical forcing |
| `analyze_projections.smk` | wf2 | CMIP6 change factors — a plausibility overlay |
| `generate_scenarios.smk` | wf3 | model-independent scenario collection generation |
| `simulate_system.smk` via `scripts/simulate_system.py` | wf4 | simulation and retained-response metrics |

Convenience order: wf0 → wf1 → wf2 → wf3 → wf4. Generation and model construction are independent prerequisites of simulation; projections are a plausibility overlay and never drive generation. WF0 is optional and shares region/climate producers: run it first or not at all, and run it ALONE when choosing forcing.

## Background

Method context that changes how code here should be edited (rationale: `docs/cst-toolbox-technical-note-2025.md` §1):

- CST is bottom-up stress testing (decision-scaling / DMDU): it perturbs local climate over a temperature × precipitation grid rather than running selected GCM scenarios. Stress-test scenarios come from the stochastic weather generator — never couple the experiment workflow to CMIP scenarios.
- CMIP6 output (wf2) is a plausibility overlay only. Its change factors situate the perturbation grid in projection space; they never drive a stress-test run.
- wf0 characterises historical climate without a model — the forcing-selection question, which matters because CST does no local calibration, so forcing choice is the dominant lever on the historical run. wf1 builds Wflow-SBM from global data via hydromt and runs it once. wf2 computes monthly change factors per (model, scenario, horizon). wf3 generates realizations and perturbed scenarios into a durable collection. wf4 consumes its explicit run ids, runs Wflow, and reduces retained native responses into immutable metric sets.
- This repo is the workflow engine of a three-part platform (workflows + CST-API + CST-frontend). No web/API code belongs here.
- CST targets rapid, first-order basin assessments on global data. Prefer robustness and automation over site-specific sophistication.

## Repo Map

Self-explanatory except for these. Full detail: `dev/reference/repo-layout.md`.

- `blueearth_cst/` — modules invoked from Snakemake `script:` (Python) or `Rscript --vanilla` `shell:` bodies (R); none is a standalone CLI. Split by stage (`model/`, `projections/`, `climate_analysis/`, `experiment/`), plus `shared/` for cross-cutting helpers and `weathergen/` for the R weather generator.
- `config/` — four bins plus `advanced_settings.yml`, which `snake_utils` reads once for every project and is not a `--configfile` target (closed schema: add a key to the file and to `_ADVANCED_SETTINGS_SCHEMA` together). There is **no `workflows/` bin** — every `--configfile` target lives beside the project it writes into, under `test_case/`. A project config is a SET of files since R13: a project file carrying closed `{enabled, config_path}` workflow stanzas plus one file per workflow beside it, composed by `blueearth_cst/shared/config_composition.py` into today's in-memory shape. A `config_path` resolves against the project file's own directory; every other path key still resolves from the run directory. A key read by more than one workflow belongs in the project file — under the kind section that owns it (`basin:`, `climate:`, `model:`) or at its top level — and is refused inside a workflow file at parse time (`docs/migration-config-shape.md`; R14 dissolved R13's `shared:` heading into those sections). The two-tier split: `config/defaults/` is read by rules, so changing one changes a run; `config/templates/` is only scaffolds you copy. `catalogs/` holds the hydromt `-d` targets, of which `cmip6_data.yml` and `cmip6_store_index.json` are generated — never hand-edit them. **Keep the `project_config_` prefix on any new seed config**; a name outside that glob is silently untracked. Real basin data lives in the project folder, referenced by absolute path, never in this repository.
- `dev/` — planning, audits, conventions, roadmap, baseline manifest, dev helpers. Not shipped. **Open work lives on the todo-board**: one note per item under `dev/tasks/`, closures in `dev/LOG.md`, and `dev/TODO.md` is generated (`python dev/scripts/todoboard.py render` — edit the note, not `TODO.md`).
- `docs/` — user-facing reference, including the vendored hydromt / wflow guides. Configs are not mirrored here; `config/` is the single source.
- Outputs land under `project_dir`. Production `project_dir` lives **outside the repository tree**; the untracked `test_case/test_local` is a dev-only exemption.

**Three homes for executables, split by INVOCATION MODEL** — not by audience: `blueearth_cst/` is executed by Snakemake, `scripts/` is what a user runs to execute the pipeline, `dev/scripts/` inspects or maintains the repository and is never part of a run. `dev/scripts/` also holds libraries `tests/` imports, so an import error there fails CI on a bare checkout. **When something in `dev/scripts/` acquires a run-path caller, move the shared part into the shipped package** rather than importing `dev/` from a run.

`dev/scripts/console.py` is VENDORED: fix console defects in the `console-formatting` skill upstream and re-copy, never here. The agent-config directories (`.claude/`, `.codex/`, `.agents/`) are gitignored per-user state, symlinked per skill into worktrees; their absence downgrades rather than fails.

## Key Commands

Run everything inside `pixi shell`, or prefix each command with `pixi run`.

```bash
pixi install          # conda-forge + PyPI deps
pixi run install      # + weathergenr (R, via remotes) and the Julia env

# The five workflows, in convenience order. project_config_rapid.yml is the DEFAULT config.
python scripts/run_workflow.py analyze_climate     --config test_case/project_config_rapid.yml --project-dir test_case/test_rapid --cores 3
python scripts/run_workflow.py build_model         --config test_case/project_config_rapid.yml --project-dir test_case/test_rapid --cores 3
python scripts/run_workflow.py analyze_projections --config test_case/project_config_rapid.yml --project-dir test_case/test_rapid --cores 3 --keep-going
# WF3 execution uses the owned wrapper; for WF3 alone, enable only generate_scenarios in the project config.
python scripts/run_workflows.py --config <wf3-only-project-config.yml> --project-dir <project-dir> --cores 3
python scripts/simulate_system.py --config test_case/project_config_rapid.yml --target all --cores 3

# Or drive all enabled workflows in fixed order. Contract: the module docstring,
# pinned clause-by-clause by tests/test_run_workflows.py.
pixi run python scripts/run_workflows.py --config test_case/project_config_rapid.yml --project-dir test_case/test_rapid

snakemake ... --dry-run     # validate the DAG before running and after editing a rule
snakemake --unlock -s <smk> --configfile <cfg>   # Snakemake locks the workdir on crash

pytest tests/test_cli.py    # cheapest sanity check: checks all five entry points
pytest tests/               # full suite (test_build_model.py is slow)
```

Inspection helpers, all report-only until `--delete`: `pixi run tree-check`, `dev/scripts/prune_series_cache.py`, `dev/scripts/prune_climate_store.py`. DAG render: `scripts/plot_workflow_dag.py -s <smk> --configfile <cfg>`.

Use `test_case/*_linux.yml` + `config/catalogs/*_linux.yml` on Linux — data-catalog paths differ from Windows. `profiles/default/config.yaml` auto-loads from the repo root and sets `quiet: reason`; drop it when you need to see *why* a job re-ran.

## Conventions

- Name new identifiers and files per `dev/reference/naming.md`. Existing names are grandfathered; rename a contract surface only with a migration note.
- Snakefiles are config-driven: each parses one `--configfile` YAML via a shared `get_config(config, key, default, optional)` helper. A new config key must mirror that contract (raise on missing required, return the default for optional).
- Each Snakefile takes the `--configfile` path from `workflow.configfiles[0]` and forwards it as `config_path` to downstream R scripts — keep that forwarding.
- Register new data sources in a `config/catalogs/*_data*.yml` catalog and pass it to hydromt via `-d`. Never hardcode data paths in a Snakefile.
- `dev/` vs `docs/`: design notes and one-off probes under `dev/` (planning, not shipped); install and usage docs under `docs/`.
- **Keep configuration references current.** When a path, filename, config key or command moves, grep the old spelling and fix every live reference in the same commit — `docs/`, `README.md`, this file, code comments. A stale path in a document someone reads to do their job is a defect, not a record. The one exception is `dev/` milestone and review records, which are valuable *because* they are unedited; those carry a `> SUPERSEDED …` banner and an entry in `dev/reference/sealed-records.yml`, which `tests/test_sealed_records.py` freezes. **That registry is the entire list** — read it rather than guessing from age.
- No silent caps: a tool that bounds its own coverage (top-N, sampling, no-retry) must report what it dropped.
- **Writing a console row? Read `log_row`'s docstring first.** It carries the six conventions a row has to satisfy — it states its subsystem once, a value never repeats its key, a count and its noun agree (`plural`), a warning leads with the fault, no article on a verb row, and a capital unless it opens with an identifier. One row is one line and is never wrapped; a list whose length the data decides is capped with `listed`.
- [Python] `script:` modules read `snakemake.input/output/params`, not `sys.argv`. [R] `Rscript --vanilla` scripts take positional args via `commandArgs(trailingOnly=TRUE)`.
- netCDF (`.nc`) is the interchange format across R/Python/Julia. Wrap intermediate per-realization netCDFs in `temp(...)` — omitting it explodes disk usage on large `RLZ_NUM × ST_NUM` runs.

## Validation ladder — match the check to the blast radius

Batch integration: the user controls lane allocation and switching. On a free lane, wait for the user to claim it or ask for allocation through `task-start`, which creates the branch and claims the lane together from current local `main`. Keep follow-up tasks on the claimed session branch until the user asks to switch or approves landing. Flag substantially unrelated work; the switching decision remains the user's.

At a new session's entry, rebase a clean, local, unpushed lane branch onto current local `main` before writing; use a merge for a published branch unless history rewriting is explicitly authorized. Dirty state or conflicts require resolution first, without automatic stash or reset. Do not repeat this synchronization for each conversational follow-up.

Complete each task with focused checks and a separate commit. Run the combined batch gates below after synchronizing with `main` at approved landing, rather than repeating them per task. Task completion does not authorize landing or pushing. After a verified merge, prove branch ancestry, detach and free the lane, then delete the merged branch. A failed gate or merge retains the lane and branch for recovery; pushing remains a separate explicit decision.

A task branch is isolated from `main` and cheap to revert, so spend validation time by blast radius. **Re-running the full suite after each incremental edit is the failure mode to avoid.** Measured costs and rationale: `dev/reference/validation-ladder.md`.

| When | Run |
|---|---|
| While iterating | Only the tests covering the file you changed. Nothing else. |
| Before a commit | `pytest tests/test_cli.py` if a Snakefile, a `script:` signature, or a rule's declared input changed — the only place a malformed `config/defaults/*.yml` surfaces. If you wrote Python, `pixi run lint` and `pixi run format-check`. |
| Before merging the branch | `pixi run test-fast` once. Skip it for a docs-, `dev/`- or config-scaffold-only branch. |
| **Before pushing to `origin`** | `pixi run test-fast` — the local gate. CI runs the whole suite on both platforms from the push, so running `test-full` here mostly re-proves what CI is about to check anyway, at roughly ten times the wall-clock. |
| **After a push** | **Read the run it triggered.** This is what makes the line above safe, and a green local suite is no evidence about the ubuntu leg. |
| Before merging a batch that touched `shared/` or a `script:` signature, or before a milestone seal | `pixi run test-full` — the `workflow_contract` and `process_isolation` tiers, which are the ones you would rather not first meet on two platforms at once. |
| Before a milestone seal / after touching numeric outputs | `check_baseline.py check`, plus `semantic_tree_diff.py` if the tree shape moved. |

**Redirect a gate to a FILE; never pipe it through `tail`** — a pipe discards the diagnosis of an intermittent failure while still printing the pass/fail line, so the run looks informative and is not. Write `pixi run test-contract > run.log 2>&1` and read the tail of the file.

**Reading CI:** `gh` resolves to the `upstream` (Deltares) remote in this clone and exits 0 printing nothing, which reads as "CI has never run". Fix it once per clone with `gh repo set-default tanerumit/blueearth_cst`, and install the ruff pre-push hook the same way: `git config core.hooksPath .githooks`.

**Push to `main`; a PR is the exception.** This is a solo repository and `main` is unprotected, so the ladder above IS the gate: `test-fast` locally, push, read the run. `ci.yml` triggers on `push: branches: [main]` and on `pull_request` and **on nothing else** — so a branch push runs no CI at all, and a branch pushed for safekeeping has been checked by nothing but the pre-push hook. Open a PR when you want both platforms green BEFORE the code lands: a change to a reviewed numerical contract, anything touching `shared/` or a `script:` signature, a milestone seal. Otherwise push straight to `main` and read the run. Note GitHub will not let you approve your own PR, so a required-review rule would strand you; if you ever want merge-on-green, make the two `tests (...)` checks REQUIRED and enable auto-merge, because auto-merge with nothing required merges instantly instead of waiting.

**Which config to run:** default to `project_config_rapid.yml` (`test_case/test_rapid`) for anything you want to watch EXECUTE — a rule you edited, a DAG check, a generation/simulation smoke run, a figure render. Use `project_config_baseline.yml` (`test_case/test_local`) when the run's NUMBERS are the point; the baseline is recorded from it and nothing else, so never point `check_baseline.py` at the rapid tree. `project_config_wf2_fast.yml` is WF2 code iteration only. Rapid is CHEAP, not NARROW — a config that gives up coverage must say which.

**The baseline manifest is CURRENT as of 2026-09-24.** Re-recorded after the WF3 identity bundle changed scenario collection ids and generated series (WF1 discharge and CMIP6 change factors unchanged); `check_baseline.py` now reads the `metric-request/2` layout. Before that: It was deliberately left behind the baseline config from 2026-09-07 (`t2608222155`, nine-year `simulation_window` 2046-2054 and the matching `mid` horizon) because a re-record costs a full run. R12's seal paid that cost: `test_case/test_local` was regenerated from `project_config_baseline.yml` in the successor layout and `dev/baseline/manifest.json` re-recorded from it, so a green `check_baseline check` again describes the configuration you are running.

**The standing tree is now the R12 SUCCESSOR tree (2026-09-15).** It was wholly predecessor until then -- all 75 paths `snapshot_project_tree.py` could not map were pre-R12 output -- so it was replaced rather than repaired, and the predecessor copy is preserved at `blueearth_cst-artifacts/r12/predecessor-test_local-2026-09-15`. **It is still not an R12 migration reference**, and never can be: the old and new trees differ by both the R12 path/key/ownership change and the 2026-09-07 config change, so any comparison between them conflates two variables. R12 acceptance rests on the separately captured fresh P0 reference and the signed GF-9 crosswalk, which compare under matched settings. Note for other worktrees: `test_case/test_local` is untracked and **per-worktree, not shared** — verified 2026-09-15, six independent real directories with no junction or symlink among them, and their contents already differ. `project_dir: test_case/test_local` resolves from the run directory, so each worktree writes its own. The hazard is real but it is a SEEDING one, not a sharing one: a worktree seeded by copy before R12 still holds a predecessor tree, and a branch whose manifest describes the predecessor layout will fail `check_baseline` against *that* copy until it merges R12 and the tree is regenerated. Re-seed or regenerate per worktree; fixing one does not fix the others.

**Run WF1 with `--notemp` when the run feeds `check_baseline.py`.** Rule 1.13 declares wflow's `run_default/output.csv` as `temp()`, and that file is the manifest's wf1 discharge target, so without the flag the gate fails "target missing" and reads as a defect. The rounded `output_q.csv` is not a substitute.

**Figures are terminal artifacts** — no rule consumes a `.png`/`.pdf`, so verify a figure-only change by rendering it and publishing the PNG as an Artifact for visual inspection, never with the baseline, the full suite, or a byte comparison of the render. But a shared helper edited in service of a plot (`shared/plot_style.py`, `shared/cartographic_map.py`, which rules 1.11 and 1.12 both draw through) is *a contract surface with other callers* and takes the normal ladder above.

## Hard Constraints

- **IMPORTANT: Julia is not in the pixi env** — it is juliaup-managed and must already be on `PATH` (conda-forge has no win-64 Julia build). Do not add it via pixi.
- Do not commit run outputs written under `project_dir`, or hand-edit `pixi.lock` or `Manifest.toml`.
- The repo root carries **no cache directory of any kind**, and `tests/test_cache_dir_hygiene.py` fails if one appears. `ruff check --isolated` is the one invocation that still writes one — run it as `RUFF_CACHE_DIR=.tmp/ruff_cache ruff check --isolated`.
- **IMPORTANT: stay within CST's automation scope** — this repo is the workflow engine only. Define config and setup (`config/defaults/wflow_build_model.yml`, data catalogs, `setup_*` blocks, `wflow_sbm.toml`-affecting steps) using hydromt / hydromt_wflow / Wflow conventions verbatim: CSDMS Standard Names, their YAML schema, their catalog format. Do not re-engineer how hydromt handles data, how `setup_*` methods work internally, or how Wflow parameterizes physics. Verification may *read* upstream docs to validate our config but must never patch upstream; a genuine hydromt/wflow bug is flagged upstream or worked around in our own code, never inside a vendored package.

## References

- `README.md` — the pipeline and how the five workflows fit together; start here.
- `docs/cst-toolbox-technical-note-2025.md` — the original 2025 note; read for method background and design rationale before changing *what* a workflow computes. Its only edit since is a two-line path sweep, so the method framing still holds, but pipeline details, paths and artifact names in it are often superseded — trust the code and `dev/reference/` where they disagree.
- `dev/reference/validation-ladder.md` — read when deciding whether a gate is affordable, or when a gate behaves unexpectedly.
- `dev/reference/repo-layout.md` — read when adding a file and unsure where it goes.
- `dev/reference/naming.md` — read when naming a new identifier, file, or rule.
- `dev/reference/workflows/rule-index.md` — read when editing or adding a rule.
- `docs/install.md`, `docs/env_setup_notes.md` — read when pixi / R / Julia setup or env activation misbehaves.
- `docs/hydromt-user-guide/00-index.md`, `docs/hydromt-architecture.md` — read when editing model-build config, data catalogs, or region setup.
- `docs/hydromt-wflow/getting-started.md`, `user-guide.md`, `api.md` — read when a build/update/clip step touches the hydromt_wflow plugin (`api.md` for signatures).
- `docs/wflow-user-guide/00-index.md` — read when editing `wflow_sbm.toml`, warm states, or Wflow run config.
