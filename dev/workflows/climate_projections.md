# Workflow: climate_projections

Contract for `Snakefile_climate_projections` (workflow 2). Format per
`dev/r01/modularity-contracts-design.md` §4, mirroring
`dev/workflows/model_creation.md` (R3's contract doc). Records **current**
behavior — R4's opening act, written before any code change, so it is the
baseline the R4 code commits are checked against, not a description of intended
change. Grounded in `Snakefile_climate_projections`,
`config/snake_config_model_test.yml`, and `config/cmip6_data.yml`.

Method note (`AGENTS.md`): workflow 2 is a **plausibility overlay only** — its
CMIP6 change factors situate the workflow-3 perturbation grid in projection
space; nothing in workflow 3 consumes them to drive stress-test runs.

## Owned config keys (`workflows.climate_projections.*`)

Read at `Snakefile_climate_projections` lines 23–33 via `get_config`:

- `clim_project` — CMIP archive tag (e.g. `cmip6`); prefixes catalog source names.
- `models` — CMIP6 model list (e.g. `NOAA-GFDL/GFDL-ESM4`, `INM/INM-CM4-8`).
- `scenarios` — SSP scenarios (e.g. `[ssp245, ssp585]`).
- `members` — ensemble members (e.g. `[r1i1p1f1]`).
- `variables` — climate variables (e.g. `[precip, temp]`; naming is contractual, see below).
- `start_month_hyd_year` — hydrological-year start month. Default `"Jan"`.
- `historical_year_range` — read into `time_horizon_hist`. Required (no default).
- `future_horizons` — mapping of horizon name → `[start, end]` (e.g. `far: [2070, 2090]`). Required.
- `save_grids` — gate for the gridded output branches. Default `False`.

`enabled:` is present in the config (`config/snake_config_model_test.yml` line
36) but is **not read** by the Snakefile — a known dormant key (operationalizing
it is R6, roadmap; non-goal here).

## Reads from `project`

Read at `Snakefile_climate_projections` lines 20–21:

- `project.project_dir` — output root
  (`clim_project_dir = {project_dir}/climate_projections/{clim_project}`).
- `project.data_sources_climate` — hydromt CMIP6 data catalog (read as
  `DATA_SOURCES`, e.g. `config/cmip6_data.yml`). **Divergence from workflow 1:**
  workflow 2 reads `data_sources_climate`, *not* `data_sources` — the two are
  distinct catalogs (deltares vs CMIP6), not a shared key.

## Input contract

- **Cross-workflow product** (from workflow 1): `{basin_dir}/staticgeoms/
  region.geojson`, consumed as `ancient(...)` by `monthly_stats_hist` /
  `monthly_stats_fut` (Snakefile lines 71, 90) — a clip mask, treated as
  never-stale so a rebuilt model does not force a workflow-2 rerun.
- **External CMIP6 catalog sources** required in `data_sources_climate`. Each
  script builds the source name `{clim_project}_{model}_{scenario}_{member}`
  (`get_stats_climate_proj.py` line 181), matching the
  `cmip6_{model}_{scenario}_{member}` entries in `config/cmip6_data.yml`. For
  the seed config: `cmip6_{model}_historical_r1i1p1f1` and
  `cmip6_{model}_{ssp245,ssp585}_r1i1p1f1` over the three models. A source
  absent from the catalog yields a dummy empty dataset, skipped at merge.

## Output contract (by role — not all are `rule all` targets)

**Direct `rule all` targets** (Snakefile lines 44–51, under `clim_project_dir`):

- `annual_change_scalar_stats_summary.nc`
- `annual_change_scalar_stats_summary.csv`
- `annual_change_scalar_stats_summary_mean.csv`
- `plots/projected_climate_statistics.png`
- `plots/precipitation_anomaly_projections_abs.png`
- `plots/temperature_anomaly_projections_abs.png`
- `{project_dir}/config/snake_config_climate_projections.yml` (verbatim snapshot)

**Intermediate `temp(...)` artifacts** (deleted after consumers finish; NOT
manifest targets — Snakefile lines 74, 93, 111):

- `historical_stats_time_{model}.nc`
- `stats_time-{model}_{scenario}.nc`
- `annual_change_scalar_stats-{model}_{scenario}_{horizon}.nc`

**Side-effect artifacts** (bookkeeping; no downstream reader):

- `gcm_timeseries.nc` — written by `plot_climate_proj_timeseries` but declared
  under the output label `timeseries_csv` (Snakefile line 154). The
  label/extension mismatch (`_csv` name, `.nc` file) is **known state**,
  documented here, not fixed in R4 unless the chain audit charters it.
- `{project_dir}/logs/2.NN_{rule}[/…].log`, `{project_dir}/benchmarks/2.NN_{rule}[/…].tsv`
  — ephemeral run artifacts once the R3 log/benchmark convention reaches this
  workflow (R4 code commits); gitignored, never fingerprinted or committed. The
  `2.NN_` prefix is the `W.NN` rule-numbering scheme (naming.md §9); wildcard
  rules keep their `{model}…` subdirectory under the numbered folder.

## Required variable naming + unit split

`get_stats_climate_proj.py` dispatches on the literal name `precip` vs
`else`-is-temp, resampling **precip with `.sum`** (monthly total) and **temp
with `.mean`** (monthly mean) — the multiplicative/additive split the whole
change-factor method depends on. A catalog naming its precip variable anything
other than `precip` would be silently treated as temp. The seed
`variables: [precip, temp]` is therefore the required naming, contractual here.

| Variable | Reducer over month | Change formula (downstream) | Unit         |
| -------- | ------------------ | --------------------------- | ------------ |
| `precip` | `.sum`             | multiplicative `(c−h)/h*100`| % change     |
| `temp`   | `.mean`            | additive `c−h`              | degC change  |

## `save_grids` gating

When `save_grids: False` (the seed default) the gridded branches in
`get_stats_climate_proj.py` / `get_change_climate_proj.py` /
`plot_proj_timeseries.py` are skipped and the grid-path params (`stats_nc_hist`
/ `stats_nc` grid netCDFs, `change_grids`) are never written — only the scalar
summary and time-series artifacts above are produced. `save_grids: True`
additionally emits the per-model grid netCDFs.

## Known metadata regression (documented, not fixed here)

`annual_change_scalar_stats_summary.nc` currently ships **empty CF `attrs`**
(`{}`) on `precip`/`temp`, a consequence of the M2b hydromt-1.3 regression
(`dev/followups.md` § R3+). Recorded so a reader of the sealed workflow does not
mistake the empty metadata for correct output — a documentation entry, not a fix.

## Downstream consumers

The merged summary `.nc`/`.csv` and the three response plots are **terminal for
workflow 2** — a plausibility overlay. Workflow 3
(`Snakefile_climate_experiment`) does **not** read them to drive stress-test
runs; stated explicitly so a future reader cannot mistake the change factors for
stress-test forcing.

## Chain-audit findings

_Reserved._ The `monthly_stats_hist → monthly_stats_fut → monthly_change`
change-factor audit (unit/calendar/missing-data) is produced by a later R4
commit (design §5); its findings table lands here or in `dev/r04/chain-audit.md`.
