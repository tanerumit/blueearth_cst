# AGENTS.md

> **Canonical.** Single source of truth for every runtime. Codex reads this file
> directly; `CLAUDE.md` is a thin entry point that imports it (`@AGENTS.md`).
> Author repo instructions **here**, never only in `CLAUDE.md`.

## Overview

BlueEarth Climate Stress Test — a multi-language (Python + R + Julia) scientific
workflow toolbox stitched together by **Snakemake**. The three `Snakefile_*` files
at the repo root are the only entry points; there is no package CLI. Full
narrative in `README.rst`.

## Background

Method context that changes how code here should be edited (full rationale:
`docs/cst-toolbox-technical-note-2025.md`, §1):

- CST implements **bottom-up climate stress testing** (decision-scaling / DMDU):
  instead of running selected GCM scenarios through the system ("top-down"), it
  systematically perturbs local climate across a temperature × precipitation grid
  and maps where system performance degrades. Stress-test scenarios come from the
  stochastic weather generator, **not** from climate projections — never couple
  the experiment workflow to CMIP scenarios.
- CMIP6 output (workflow 2) is a **plausibility overlay only**: its change factors
  situate the perturbation grid in projection space; they never drive stress-test
  runs.
- Pipeline ↔ method: workflow 1 builds a distributed Wflow-SBM model from global
  datasets via hydromt and runs it once on historical forcing (rapid deployment,
  no local calibration); workflow 2 computes per-(model, scenario, horizon)
  monthly change factors from CMIP6; workflow 3 is the stress test proper —
  weathergenr generates `RLZ_NUM` stochastic realizations, each perturbed across
  `ST_NUM` temp/precip combinations (`cst_0` = unperturbed baseline), run through
  Wflow, and reduced to hydrological indicators (e.g. mean/max discharge, 7-day
  low flow) that form the response surface.
- This repo is the **workflow engine** of a three-part platform (BlueEarth-CST
  workflows + CST-API backend + CST-frontend GUI). No web/API code belongs here;
  the GUI drives these Snakefiles server-side.
- CST targets rapid, first-order basin assessments on global data — not detailed
  engineering design. Prefer robustness and automation over site-specific
  sophistication.

## Repo Map

- `Snakefile_model_creation` / `Snakefile_climate_projections` /
  `Snakefile_climate_experiment` — the three workflow entry points, run in that
  order.
- `src/*.py` — analysis/orchestration steps, invoked from Snakemake `script:`
  directives (not standalone CLIs).
- `src/weathergen/*.R` — R weather generator, invoked via `Rscript --vanilla`
  from Snakemake `shell:`.
- `config/` — `snake_config_*.yml` workflow configs + hydromt data-catalog
  YAMLs (`deltares_data*.yml`, `cmip6_data.yml`).
- `tests/` — `test_cli.py` is the cheap dry-run gate; `test_model_creation.py`
  is a heavy full build.
- Outputs land under `project_dir` (set in the config), **not** in the repo tree.

## Key Commands

Run everything inside `pixi shell`, or prefix each command with `pixi run`, so
`snakemake`, `python`, and `Rscript` resolve to the pixi env.

```bash
pixi install          # conda-forge + PyPI deps (Python stack, R toolchain, snakemake)
pixi run install      # + weathergenr (R, via remotes) and Julia env (Pkg.instantiate)

# Run the three workflows IN ORDER (climate_experiment needs model_creation artifacts):
snakemake all -c 3 -s Snakefile_model_creation      --configfile config/snake_config_model_test.yml
snakemake all -c 3 -s Snakefile_climate_projections --configfile config/snake_config_model_test.yml --keep-going
snakemake all -c 3 -s Snakefile_climate_experiment  --configfile config/snake_config_model_test.yml

snakemake ... --dry-run           # inspect the DAG before running or after editing rules
snakemake --unlock -s <Snakefile> --configfile <cfg>   # Snakemake locks the workdir on crash

pytest tests/test_cli.py          # cheapest sanity check: dry-runs all three Snakefiles
pytest tests/                     # full suite (test_model_creation.py is slow)
```

Use `config/*_linux.yml` config and catalog variants on Linux — data-catalog paths
differ from Windows. `run_snake_test.cmd` (Windows) and `run_snake_docker.sh`
(Linux/Docker) wrap the test config.

## Conventions

- Name new identifiers and files per `dev/conventions/naming.md` (snake_case,
  lowercase acronyms, `_path`/`_dir` for paths vs `_ds`/`_df`/`_cfg` for objects,
  three-tier domain-identifier exemptions). Existing names are grandfathered;
  rename a contract surface only with a migration note.
- Snakefiles are config-driven: each parses one `--configfile` YAML via a shared
  `get_config(config, key, default, optional)` helper. Adding a config key: mirror
  that helper's contract (raise on missing required, return default for optional).
- Each Snakefile obtains the `--configfile` path from `workflow.configfiles[0]`
  and forwards it (as `config_path`) to downstream R scripts — keep that
  forwarding pattern even though the Snakefile itself reads the parsed `config`.
- The `ruleorder:` directive in `Snakefile_climate_projections` is load-bearing;
  wildcard inference is ambiguous without it.
- Register new data sources in a `config/*_data*.yml` catalog and pass it to hydromt
  via `-d`. Never hardcode data paths in a Snakefile.
- [Python] Scripts run via `script:` read `snakemake.input/output/params` (a global
  Snakemake injects), not `sys.argv`. They are not runnable standalone.
- [R] Scripts run via `shell: Rscript --vanilla ...` take positional args parsed with
  `commandArgs(trailingOnly=TRUE)`.
- netCDF (`.nc`) is the interchange format across R/Python/Julia. Wrap intermediate
  per-realization netCDFs in `temp(...)` so they are deleted after consumers finish —
  omitting it explodes disk usage on large `RLZ_NUM × ST_NUM` runs.

## Workflow

- Before running or after editing any rule, `--dry-run` first to validate the DAG.
- After editing a Snakefile or a script signature, run `pytest tests/test_cli.py`.
- If a run crashed and re-running reports a locked directory, `--unlock` before
  retry.
- Keep edits surgical; follow the existing script/rule patterns before adding
  new structure.

## Hard Constraints

- **IMPORTANT: Julia is not in the pixi env** — it is juliaup-managed and must
  already be on `PATH` (conda-forge has no win-64 Julia build). Do not try to add it
  via pixi.
- Do not commit run outputs written under `project_dir`, or edit `pixi.lock` /
  `Manifest.toml` by hand.

## References

- `README.rst` — the overall pipeline and how the three workflows fit together;
  start here.
- `docs/cst-toolbox-technical-note-2025.md` — stress-test method and design
  rationale; read before changing *what* a workflow computes.
- `docs/env_setup_notes.md`, `docs/install.md` — read when pixi / R / Julia
  setup or env activation misbehaves.
- `docs/hydromt-user-guide/00-index.md`, `docs/hydromt-architecture.md` — read
  when editing model-build config, data catalogs, or region setup.
- `docs/hydromt-wflow/getting-started.md`, `docs/hydromt-wflow/user-guide.md`,
  `docs/hydromt-wflow/api.md` — read when a build/update/clip step touches the
  hydromt_wflow plugin (`api.md` for exact signatures).
- `docs/wflow-user-guide/00-index.md` — read when editing `wflow_sbm.toml`,
  warm states, or Wflow run config.
