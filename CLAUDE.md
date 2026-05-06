# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Stack

This is a multi-language scientific workflow toolbox (BlueEarth Climate Stress Test):

- **Python** drives orchestration and analysis (`src/*.py`, called from Snakemake `script:` directives or as CLI tools).
- **R** runs the weather generator (`src/weathergen/*.R`), invoked via `Rscript --vanilla` from Snakemake `shell:` directives.
- **Julia** runs the Wflow.jl hydrological model, invoked via `julia --threads 4 -e "using Wflow; Wflow.run()" <toml>` from Snakemake `shell:` directives.
- **Snakemake** stitches everything together. The three `Snakefile_*` files at the repo root are the entry points — there is no Python package CLI.

The conda env name in `environment.yml` is `cst`, but the README's instructions assume the env is named `blueearth-cst`. Both names appear in scripts. Activate whichever was actually created locally.

## Common commands

All workflows take `--configfile config/snake_config_model_test.yml` (the canonical example config). Use `_linux.yml` variants on Linux because data catalog paths differ.

```bash
# Run the three workflows (run in this order — climate_experiment depends on artifacts from model_creation)
snakemake all -c 1 -s Snakefile_model_creation     --configfile config/snake_config_model_test.yml
snakemake all -c 1 -s Snakefile_climate_projections --configfile config/snake_config_model_test.yml --keep-going
snakemake all -c 1 -s Snakefile_climate_experiment  --configfile config/snake_config_model_test.yml

# Inspect a workflow without running (always do this first when modifying rules)
snakemake all -c 1 -s Snakefile_model_creation --configfile <cfg> --dry-run
snakemake -s Snakefile_model_creation --configfile <cfg> --dag | dot -Tpng > dag.png

# Snakemake locks the working dir on crash — unlock before re-running
snakemake --unlock -s Snakefile_model_creation --configfile <cfg>
```

`run_snake_test.cmd` (Windows) and `run_snake_docker.sh` (Linux/Docker) wrap these for the test config.

### Tests

```bash
pytest tests/                       # all tests
pytest tests/test_cli.py            # snakefile dry-run validity check
pytest tests/test_cli.py -k climate # one parametrized case
```

`tests/test_cli.py` runs `snakemake ... --dry-run` for each of the three Snakefiles against `tests/snake_config_model_test.yml` — this is the cheapest sanity check after editing a Snakefile or a script signature. `tests/test_model_creation.py` exercises the actual model build and is much heavier.

### Docker

Image builds the entire toolbox (Python env + Julia + Wflow + R weathergenr) into one container.

```bash
docker build -t cst-workflow:0.0.1 .
./run_snake_docker.sh   # runs all three workflows against the test config; expects /mnt/p/wflow_global/hydromt mounted
```

## Architecture

### Config-driven workflows

Each `Snakefile_*` parses one YAML config (`config/snake_config_*.yml`). All three Snakefiles re-implement the same `get_config(config, key, default, optional)` helper to read from that config — if you add a new config key, mirror the convention (raise on missing required keys, return default for optional). The Snakefiles also re-read the `--configfile` path from `sys.argv` so they can pass the path to downstream R scripts; do not break that pattern.

Outputs live under `project_dir` (set in the config). Within `project_dir`:
- `hydrology_model/` — Wflow model staticmaps, staticgeoms, run outputs.
- `climate_historical/` — extracted historical forcing.
- `climate_projections/<clim_project>/` — CMIP statistics and change factors.
- `climate_<experiment>/` — weather generator realizations and stress-test runs.
- `config/` — copies of the configs that produced this run (the `copy_config` rule snapshots them).
- `plots/` — final PNG outputs that act as `rule all` targets.

### The three workflows in pipeline order

1. **`Snakefile_model_creation`** — calls `hydromt build wflow` (shell) to produce `staticmaps.nc`, then patches it via `src/setup_reservoirs_lakes_glaciers.py` and `src/setup_gauges_and_outputs.py` (the reservoir step is a "temporary hydromt fix" — comment in the file). Runs Wflow once on historical forcing and produces baseline plots. Targets in `rule all` are PNGs under `plots/wflow_model_performance/`.

2. **`Snakefile_climate_projections`** — for each `(model, scenario, horizon)` triple from the config, computes monthly statistics (`monthly_stats_hist` → `monthly_stats_fut` → `monthly_change`) and merges them into a summary netCDF + CSVs + projection plots. The `ruleorder:` directive in this file is load-bearing — Snakemake's wildcard inference is otherwise ambiguous between these rules.

3. **`Snakefile_climate_experiment`** — generates `RLZ_NUM` weather realizations via the R weathergenr (`generate_weather.R`), then for each realization × stress-test combination (`ST_NUM = (temp.step_num + 1) * (precip.step_num + 1)`) imposes a climate change signal (`impose_climate_change.R`), downscales to wflow forcing, runs Wflow, and aggregates results. Combinatorial expansion lives in the `expand(...)` calls in `rule climate_data_catalog` and `rule export_wflow_results`. The `run_historical` flag toggles whether `cst_0` (the unperturbed realization) is also routed through the wflow runs (`ST_START = 0` vs `1`).

### How Snakemake invokes scripts

- Python: `script: "src/foo.py"` — Snakemake injects a `snakemake` global into the script. The scripts read `snakemake.input`, `snakemake.output`, `snakemake.params` rather than `sys.argv`. Don't try to run these as standalone CLIs.
- R: `shell: """Rscript --vanilla src/weathergen/foo.R <args>"""` — args are passed positionally; the R scripts parse them with `commandArgs(trailingOnly=TRUE)`.
- Julia/hydromt: invoked as `shell:` commands. `hydromt build wflow` and `hydromt update wflow` use the `-d` flag to point at a data catalog YAML; `julia ... Wflow.run()` takes a TOML path.

### Data catalogs

`config/deltares_data*.yml` and `config/cmip6_data.yml` are hydromt data catalog YAMLs. Linux variants (`*_linux.yml`) exist because the Deltares P-drive is mounted differently. The Snakefiles never hardcode data paths — they pass the catalog path through to hydromt via `-d`. When adding a new data source, register it in the catalog rather than referencing a path directly.

### Cross-language data flow

netCDF (`.nc`) is the lingua franca between R, Python, and Julia. Intermediate per-realization netCDFs are wrapped in `temp(...)` in the Snakefiles so they're cleaned up after consumers finish — keep that wrapper if you add new intermediate files in the same pattern, otherwise disk usage explodes for large `RLZ_NUM × ST_NUM` runs.
