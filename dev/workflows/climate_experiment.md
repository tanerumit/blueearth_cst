# Workflow: climate_experiment

Contract for `Snakefile_climate_experiment` (workflow 3). Format per
`dev/r01/modularity-contracts-design.md` §4, mirroring
`dev/workflows/model_creation.md` and `dev/workflows/climate_projections.md`.
Records **current** behavior — R5's opening act, written before any code change,
so it is the baseline the R5 code commits are checked against, not a description
of intended change. Grounded in `Snakefile_climate_experiment`,
`config/snake_config_model_test.yml`, `src/*.py`, and `src/weathergen/*.R`.

Method note (`AGENTS.md`): workflow 3 is the **stress test proper**. Its
scenarios come from the **weathergenr** stochastic weather generator, **not**
from CMIP projections — never couple this workflow to workflow 2's change
factors. `RLZ_NUM` realizations × `ST_NUM` temp/precip perturbations; `cst_0` =
the unperturbed baseline (run through Wflow only when `run_historical` sets
`ST_START = 0`); reduced to the Qstats hydrological indicators.

## Owned config keys (`workflows.climate_experiment.*`)

Read at `Snakefile_climate_experiment` lines 19–41 via `get_config`:

- `experiment_name` — read as `experiment`; drives `exp_dir =
  {project_dir}/climate_{experiment}`. Required.
- `realizations_num` — number of stochastic realizations (→ `RLZ_NUM`). Default 1.
- `stress_test.temp.step_num`, `stress_test.precip.step_num` — per-axis
  perturbation step counts; `ST_NUM = (temp.step_num+1)*(precip.step_num+1)`.
- `run_historical` — when true, `ST_START = 0` so `cst_0` is run through Wflow;
  when false, `ST_START = 1`. Default `false`.
- `horizontime_climate` — climate horizon (mid) year. Required.
- `run_length` — Wflow run length in years (→ `wflow_run_length`). Default 20.
- `aggregate_rlz` — aggregate realizations per stress test. Default `true`.
- `Tlow`, `Tpeak` — return periods (years) for low/high flow indicators.
  Defaults 2 / 10.

The deeper `stress_test.{temp,precip}.{mean,variance,transient_change}` structure
is read by `src/prepare_cst_parameters.py` (lines 31–56) and
`src/prepare_weagen_config.py` (lines 54–56): `mean.{min,max}` and
`variance.{min,max}` are 12-month vectors that seed the per-stress-test
`np.linspace` grids; `transient_change` is a per-axis boolean forwarded to the R
perturbation layer.

`enabled:` is present in the config (line 52) but is **not read** by the
Snakefile — a known dormant key (operationalizing it is R6; non-goal here).

## Reads from `project`

Read at `Snakefile_climate_experiment` lines 21–23:

- `project.project_dir` — output root.
- `project.static_dir` — location of template configs.
- `project.data_sources` — hydromt deltares data-catalog YAML (→ `DATA_SOURCES`).
  **Divergence from workflow 2:** workflow 3 reads `data_sources` (deltares), not
  workflow 2's `data_sources_climate` (CMIP6) — distinct catalogs, not a shared key.

## Reads from `shared`

Read at `Snakefile_climate_experiment` line 39:

- `shared.clim_historical` — historical climate source (→ `clim_source`, e.g. `era5`).

**Known gap (documented, not fixed here):** the config carries
`shared.historical_window.{starttime,endtime}` (config lines 21–23) but the
Snakefile **never reads it** — the historical extraction dates are **hardcoded**
in `src/extract_historical_climate.py` (lines 156–157,
`2000-01-01`/`2020-12-31`). The seed window is byte-identical to those hardcoded
strings, so current output is unaffected. (Wired through in R5 commit 6 as a
chartered output-neutral fix; recorded here as current state.)

## Input contract

- **Cross-workflow product** (from workflow 1): `{basin_dir}/staticgeoms/
  region.geojson`, consumed as `ancient(...)` by `extract_climate_grid`
  (Snakefile line 68); and the built Wflow model root `{basin_dir}` /
  `{basin_dir}/staticmaps.nc`, consumed by `downscale_climate_realization`
  (`WflowSbmModel(root=model_root)`, `downscale_climate_forcing.py` line 38).
- **External data catalog**: `DATA_SOURCES` (deltares catalog YAML) plus the
  run-time `data_catalog_climate_experiment.yml` built by `climate_data_catalog`
  (line 141).
- **The `--configfile` YAML** itself, forwarded to scripts as `config_path`.

## Output contract (by role — not all are `rule all` targets)

**Direct `rule all` targets** (Snakefile lines 47–51). **These 3 are the manifest
slice** (`dev/scripts/check_baseline.py` TARGETS lines 70–72):

- `{exp_dir}/model_results/Qstats.csv` (normalized-content CSV hash)
- `{exp_dir}/model_results/basin.csv` (normalized-content CSV hash)
- `{project_dir}/config/snake_config_climate_experiment.yml` (verbatim snapshot)

**Non-temp but non-manifest side products:**

- per-run Wflow output CSVs `output_rlz_{rlz_num}_cst_{st_num2}.csv` (line 170)
  and per-run TOMLs `wflow_sbm_rlz_..._cst_{st_num2}.toml` (line 155),
- per-stress-test parameter CSVs `cst_{st_num}.csv` (line 82),
- weagen config YAMLs (lines 89, 104), the `data_catalog_climate_experiment.yml`
  (line 141), and the extra `RT_{var}.csv` files `export_wflow_results.py`
  writes (line 280).

**Intermediate `temp(...)` artifacts** (deleted after consumers finish; NOT
manifest targets):

- `rlz_{rlz_num}_cst_0.nc` (line 120), `rlz_..._cst_{st_num}.nc` (line 131),
  `inmaps_rlz_..._cst_{st_num2}.nc` (line 154), `outstates_rlz_...nc` (line 171).
- `extract_historical.nc` (line 73) — NOT `temp`, but consumed as `ancient(...)`
  (line 117), so grandfathered-stale.

**Side-effect artifacts:** `{project_dir}/logs/3.NN_{rule}[/…].log`,
`{project_dir}/benchmarks/_parts/3.NN_{rule}[/…].tsv` (per-rule benchmarks under
`_parts/`; `gather_benchmarks` merges WF3's into one `benchmarks/wf3_benchmarks.md`
(Markdown table, `rule` column + `TOTAL` row)) — ephemeral once the R3
log/benchmark convention reaches this workflow (R5 code commits); gitignored,
never fingerprinted or committed. The `3.NN_` prefix is the `W.NN`
rule-numbering scheme (naming.md §9); wildcard rules keep their
`rlz_{rlz_num}_cst_{st_num}` name under the numbered subdirectory.

## Gate-coverage honesty

A clean `check_baseline check --workflow climate_experiment` proves only the **two
reduced summary CSVs** + the config snapshot unchanged — **not** that every
per-realization forcing, perturbed netCDF, or raw discharge CSV is, since those
are all `temp`/non-manifest. The gate is a necessary regression tripwire, not a
proof of scientific invariance for the intermediates.

## Known state flagged (not fixed by this doc)

- The `historical_window` config-key gap (above) — extraction dates hardcoded.
- The `st_num2` wildcard variant in the downstream rules
  (`downscale_climate_realization`, `run_wflow`, `export_wflow_results`) admits
  `0` under `run_historical`, where `st_num` starts at `1`. Flagged as a known
  inconsistency by `dev/conventions/naming.md` §4; folded into `st_num` during R5.

## Downstream consumers

Terminal for the platform: `Qstats.csv`/`basin.csv` (and the `RT_*.csv` response
tables) are the stress-test response surface consumed by the CST-API/GUI, not by
another Snakefile in this repo.
