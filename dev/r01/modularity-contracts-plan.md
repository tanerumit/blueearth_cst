# R01 Modularity Contracts Implementation Plan

> **For agentic workers:** Steps use checkbox (`- [ ]`) syntax for tracking. Implement task-by-task and check off as you go. Do not skip the verification commands — they are the contract that catches migration drift.

**Goal:** Reorganize the flat snake config into `project` / `shared` / `workflows.<name>` top-level sections, write per-workflow contract docs, update all 3 Snakefiles to read sectioned config. Code structure unchanged. End state: zero baseline diff, tests unchanged.

**Architecture:** One config template + 3 contract docs (no code). One atomic commit migrates the test config + all 3 Snakefiles together (Task 3). Two follow-up commits migrate the canonical example configs (Task 4–5). Final verification commit re-runs all workflows and seals the milestone.

**Tech Stack:** YAML schema, Snakemake `workflow` global, pytest, pixi env, existing `dev/scripts/check_baseline.py`.

**Branch:** `milestone/r01-contracts` (already on it; off `m02c-tests` tag).

**Spec:** `dev/r01/modularity-contracts-design.md`. Read it first if you haven't.

---

## Pre-task setup

### Step 0.1: Verify branch and clean tree

- [ ] Run: `git branch --show-current` → expect `milestone/r01-contracts`
- [ ] Run: `git status --short` → expect empty output. (This plan file should already be committed before execution starts; if you see it as untracked, commit it first.)

### Step 0.2: Verify baseline test suite passes

- [ ] Run: `pixi run pytest tests/ 2>&1 | tail -3`
- [ ] Expect: `45 passed, 4 xfailed`

### Step 0.3: Verify baseline manifest is current

- [ ] Run: `pixi run python dev/scripts/check_baseline.py check 2>&1 | tail -10` — only if you have the test workflows already run; otherwise skip and rely on Task 7 final check
- [ ] If skipping: note the manifest reference is `dev/baseline/manifest.json` from the M2b contract

---

## Task 1: Add config template + schema convention

**Files:**
- Create: `config/snake_config.template.yml`

**Purpose:** A checked-in canonical schema example. Anyone authoring a new project config copies this template and edits values. Shows the exact section structure R01 locks in.

### Step 1.1: Create the template

- [ ] Write `config/snake_config.template.yml` with this content:

```yaml
# Snake config template for blueearth_cst (R01 schema).
#
# Three top-level sections:
#   project:        paths and external resources (every workflow reads)
#   shared:         cross-workflow scientific knobs (≥2 workflows read)
#   workflows.<n>:  per-workflow opts (only that workflow reads)
#
# Each workflows.<name> section has an `enabled:` flag (documentary in
# R01; will become operational at R6+ structural refactor).
#
# Per-workflow contract docs at dev/workflows/<name>.md describe owned
# keys, input contract, and output contract.

project:
  # Output root for this run
  project_dir: examples/test
  # Static config dir (templates referenced by workflows)
  static_dir: config
  # Hydromt data catalog (era5, merit_hydro, etc.)
  data_sources: config/deltares_data.yml
  # Hydromt data catalog for CMIP6 (climate projections workflow)
  data_sources_climate: config/cmip6_data.yml

shared:
  basin:
    # hydromt region spec (string with dict syntax — see hydromt docs)
    region: "{'subbasin': [9.666, 0.4476], 'uparea': 100}"
    # Grid resolution in degrees (≥ source hydrography res, e.g. merit_hydro_ihu = 0.00833)
    resolution: 0.00833
  historical_window:
    # ISO datetime strings — wflow forcing window
    starttime: "2000-01-01T00:00:00"
    endtime: "2005-12-31T00:00:00"
  # Historical climate source (must exist in project.data_sources catalog)
  clim_historical: era5
  # Wflow output variables to save
  wflow_outvars: ['river discharge']

workflows:
  model_creation:
    enabled: true
    # Hydromt build config template
    model_build_config: config/wflow_build_model.yml
    # Hydromt update config for waterbodies (optional; defaults below)
    waterbodies_config: config/wflow_update_waterbodies.yml
    # Optional: csv with three cols (station_ID, x, y); None defaults to wflow outlets
    output_locations: None
    # Optional: csv with observed discharge timeseries per station
    observations_timeseries: None

  climate_projections:
    enabled: true
    clim_project: cmip6
    models:
      - NOAA-GFDL/GFDL-ESM4
      - INM/INM-CM5-0
      - CMCC/CMCC-ESM2
    scenarios: [ssp245, ssp585]
    members: [r1i1p1f1]
    variables: [precip, temp]
    start_month_hyd_year: Jan
    # CMIP6 monthly stats historical year range (different precision than
    # shared.historical_window — that one uses ISO datetimes for wflow forcing)
    historical_year_range: [1980, 2010]
    future_horizons:
      near: [2030, 2060]
      far:  [2070, 2100]
    # Save gridded outputs in addition to basin averages
    save_grids: false

  climate_experiment:
    enabled: true
    experiment_name: experiment
    realizations_num: 2
    # Future midpoint year for the climate experiment
    horizontime_climate: 2050
    # Length of future run in years
    run_length: 20
    # Run historical (cst_0) realization through wflow as well
    run_historical: false
    stress_test:
      temp:
        step_num: 1
        transient_change: true
        mean:
          min: [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
          max: [3.0, 3.0, 3.0, 3.0, 3.0, 3.0, 3.0, 3.0, 3.0, 3.0, 3.0, 3.0]
      precip:
        step_num: 2
        transient_change: true
        mean:
          min: [0.7, 0.7, 0.7, 0.7, 0.7, 0.7, 0.7, 0.7, 0.7, 0.7, 0.7, 0.7]
          max: [1.3, 1.3, 1.3, 1.3, 1.3, 1.3, 1.3, 1.3, 1.3, 1.3, 1.3, 1.3]
        variance:
          min: [1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0]
          max: [1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0]
    # Drought / flood return periods (years)
    Tlow: 2
    Tpeak: 10
    # Aggregate realizations before computing statistics
    aggregate_rlz: true
```

### Step 1.2: Verify YAML parses

- [ ] Run: `pixi run python -c "import yaml; yaml.safe_load(open('config/snake_config.template.yml'))"`
- [ ] Expect: no output (clean parse)

### Step 1.3: Commit

- [ ] Run:
```
git add config/snake_config.template.yml
git commit -m "$(cat <<'EOF'
m02d: add canonical sectioned config template

config/snake_config.template.yml is the R01 schema in checked-in form:
project / shared / workflows.<name> sections, with the enabled: flag
on each workflow as a forward-compat marker. Anyone authoring a new
project config copies this template and edits values.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 2: Write contract docs for the three workflows

**Files:**
- Create: `dev/workflows/model_creation.md`
- Create: `dev/workflows/climate_projections.md`
- Create: `dev/workflows/climate_experiment.md`

**Purpose:** Per-workflow contracts. Each doc declares owned config keys, input/output contracts, downstream consumers. The modularity contract per the R01 spec.

### Step 2.1: Create dev/workflows/model_creation.md

- [ ] Write:

```markdown
# Workflow: model_creation

Builds a Wflow.jl hydrological model for the configured basin: hydromt
build → reservoirs/lakes/glaciers patch → gauges → forcing → wflow
historical run → diagnostic plots.

Snakefile: `Snakefile_model_creation`.

## Owned config keys

Under `workflows.model_creation`:
- `enabled: bool` — forward-compat flag (documentary in R01).
- `model_build_config: path` — hydromt build YAML template (required).
- `waterbodies_config: path` — hydromt update YAML for reservoirs/lakes/glaciers (optional).
- `output_locations: path|None` — csv with observation station coords (cols: station_ID, x, y). None → use wflow outlets.
- `observations_timeseries: path|None` — csv with observed discharge per station.

## Reads from `shared`

- `shared.basin.region` — hydromt region spec.
- `shared.basin.resolution` — grid resolution in degrees.
- `shared.historical_window.starttime` / `.endtime` — wflow forcing window.
- `shared.clim_historical` — climate source name in data_sources catalog.
- `shared.wflow_outvars` — list of wflow output variables to save.

## Reads from `project`

- `project.project_dir` — output root.
- `project.static_dir` — static config dir.
- `project.data_sources` — hydromt data catalog YAML.

## Input contract (external)

The hydromt data catalog (`project.data_sources`) must define:
- `era5` (or whatever `shared.clim_historical` names) — for forcing.
- `merit_hydro` (or `merit_hydro_ihu`) — for hydrography.
- Reservoir / lake / glacier sources referenced by `waterbodies_config`.

## Output contract

### Formal end targets (`rule all` → tracked by baseline manifest)

Under `{project_dir}/`:
- `plots/wflow_model_performance/hydro_wflow_1.png`
- `plots/wflow_model_performance/basin_area.png`
- `plots/wflow_model_performance/precip.png`
- `config/snake_config_model_creation.yml` — snapshot of config used.

### Important intermediates (consumed by other workflows; not in `rule all`)

- `hydrology_model/staticmaps.nc` — wflow static grid.
- `hydrology_model/staticgeoms/region.geojson` — basin polygon (consumed by climate_projections + climate_experiment).
- `hydrology_model/staticgeoms/outlets.geojson` — gauge points.
- `hydrology_model/wflow_sbm.toml` — wflow run config (consumed by climate_experiment).
- `climate_historical/wflow_data/inmaps_historical.nc` — extracted forcing.
- `hydrology_model/run_default/output.csv` — historical run discharge.

## Downstream consumers (informational)

- `climate_projections` reads `staticgeoms/region.geojson`.
- `climate_experiment` reads `staticgeoms/region.geojson`, `wflow_sbm.toml`, and the model dir.

## Notes

- The "temporary hydromt fix" in `src/setup_reservoirs_lakes_glaciers.py` is a known R3 followup.
- Outlet station naming convention (`subcatchment IDs` vs `1..N` rebuild) is undecided — see `dev/followups.md` M2b carryover.
```

### Step 2.2: Create dev/workflows/climate_projections.md

- [ ] Write:

```markdown
# Workflow: climate_projections

Computes monthly statistics over historical and future CMIP6 datasets,
derives change factors per (model × scenario × horizon), and merges
them into a summary netCDF + csvs + plots.

Snakefile: `Snakefile_climate_projections`.

## Owned config keys

Under `workflows.climate_projections`:
- `enabled: bool` — forward-compat flag.
- `clim_project: str` — e.g. `"cmip6"`.
- `models: list[str]` — CMIP6 model identifiers.
- `scenarios: list[str]` — e.g. `[ssp245, ssp585]`.
- `members: list[str]` — ensemble members, e.g. `[r1i1p1f1]`.
- `variables: list[str]` — e.g. `[precip, temp]`.
- `start_month_hyd_year: str` — first month of hydrological year.
- `historical_year_range: [int, int]` — CMIP6 historical window for monthly stats. Distinct from `shared.historical_window` (different precision: years vs ISO datetimes).
- `future_horizons: dict[str, [int, int]]` — e.g. `{near: [2030, 2060], far: [2070, 2100]}`.
- `save_grids: bool` — save gridded outputs alongside basin averages.

## Reads from `shared`

None directly. The historical window for projections (`historical_year_range`) is its own key because it operates at year-pair precision rather than the ISO datetime precision of `shared.historical_window`.

## Reads from `project`

- `project.project_dir`.
- `project.data_sources_climate` — separate from `project.data_sources` because CMIP6 is its own catalog.

## Input contract (external)

- `project.data_sources_climate` catalog must define entries matching `cmip6_<model>_<scenario>_<member>` for every (model, scenario, member) tuple.
- `{project_dir}/hydrology_model/staticgeoms/region.geojson` (produced by `model_creation`) — required input. If running `climate_projections` standalone, the user provides this externally.

## Output contract

### Formal end targets (`rule all` → tracked by baseline manifest)

Under `{project_dir}/climate_projections/{clim_project}/`:
- `annual_change_scalar_stats_summary.nc` — final merged.
- `annual_change_scalar_stats_summary.csv`
- `annual_change_scalar_stats_summary_mean.csv`
- `plots/projected_climate_statistics.png`
- `plots/precipitation_anomaly_projections_abs.png`
- `plots/temperature_anomaly_projections_abs.png`

Plus `{project_dir}/config/snake_config_climate_projections.yml`.

### Important intermediates (per model × scenario × horizon)

- `historical_stats_time_<model>.nc` (per model, marked `temp()`).
- `stats_time-<model>_<scenario>.nc` (per model × scenario, `temp()`).
- `annual_change_scalar_stats-<model>_<scenario>_<horizon>.nc` (`temp()`).
- `gcm_timeseries.nc` — produced by `plot_climate_proj_timeseries`, not in `rule all`.

## Downstream consumers (informational)

- None today. `climate_experiment` does not consume projection outputs directly (it uses the weather generator with historical data + user-defined stress factors).

## Notes

- `monthly_change_scalar_merge` loses CMIP6 variable attrs under hydromt 1.3 (M2b followup).
- `Snakefile_climate_projections` has a `ruleorder:` directive that disambiguates wildcard inference.
```

### Step 2.3: Create dev/workflows/climate_experiment.md

- [ ] Write:

```markdown
# Workflow: climate_experiment

Generates RLZ_NUM weather realizations via the R weathergenr, applies
stress-test perturbations (ST_NUM combinations of temp × precip steps),
runs Wflow on each, and aggregates results into Qstats / basin csvs.

Snakefile: `Snakefile_climate_experiment`.

## Owned config keys

Under `workflows.climate_experiment`:
- `enabled: bool` — forward-compat flag.
- `experiment_name: str` — names the output dir (`climate_<experiment_name>`).
- `realizations_num: int` — number of stochastic realizations (RLZ_NUM).
- `horizontime_climate: int` — future midpoint year.
- `run_length: int` — future run length in years.
- `run_historical: bool` — also run cst_0 (unperturbed) through wflow.
- `stress_test.temp.step_num: int` — number of temp perturbation steps.
- `stress_test.temp.transient_change: bool`.
- `stress_test.temp.mean.min` / `.max: list[float]` — 12 monthly values.
- `stress_test.precip.step_num: int` — number of precip perturbation steps.
- `stress_test.precip.transient_change: bool`.
- `stress_test.precip.mean.min` / `.max: list[float]` — 12 monthly values.
- `stress_test.precip.variance.min` / `.max: list[float]` — 12 monthly values.
- `Tlow: int` — drought return period (years).
- `Tpeak: int` — flood return period (years).
- `aggregate_rlz: bool` — aggregate realizations before computing statistics.

The combinatorial `ST_NUM = (temp.step_num + 1) × (precip.step_num + 1)`.

## Reads from `shared`

- `shared.clim_historical` — climate source for weathergen historical reference.

## Reads from `project`

- `project.project_dir`.
- `project.static_dir`.
- `project.data_sources` — for hydromt forcing extraction.

## Input contract (external)

- `{project_dir}/hydrology_model/wflow_sbm.toml` (from `model_creation`).
- `{project_dir}/hydrology_model/staticgeoms/region.geojson` (from `model_creation`).
- `{project_dir}/climate_historical/raw_data/extract_historical.nc` — produced internally by `extract_climate_grid` rule.
- weathergenr R package installed (handled by pixi at install time).
- juliaup-managed Julia 1.11.x with Wflow.jl instantiated.

## Output contract

### Formal end targets (`rule all` → tracked by baseline manifest)

Under `{project_dir}/climate_<experiment_name>/`:
- `model_results/Qstats.csv` — discharge statistics.
- `model_results/basin.csv` — basin-aggregated results.

Plus `{project_dir}/config/snake_config_climate_experiment.yml` snapshot.

### Important intermediates

- `realization_<rlz>/rlz_<rlz>_cst_0.nc` (weather realizations, `temp()`).
- `realization_<rlz>/rlz_<rlz>_cst_<st>.nc` (stress test perturbations, `temp()`).
- `data_catalog_climate_experiment.yml` — hydromt catalog of generated NCs.

## Downstream consumers (informational)

- None today (this is the leaf workflow).

## Notes

- `extract_climate_grid` silent truncation when staged data is shorter than requested window — R3 followup.
- `extract_climate_grid` ignores `historical_window.starttime/endtime` (currently hardcoded in script) — R5 followup.
- `weathergenr::write_netcdf` `spatial_ref` attr propagation issue — R5 followup with workaround in `generate_weather.R`.
- weathergenr's 16-year wavelet minimum is enforced in `wavelet_cwt.R` with a cryptic error — R5 weathergenr issue.
```

### Step 2.4: Verify all 3 docs exist

- [ ] Run: `ls dev/workflows/`
- [ ] Expect: `model_creation.md  climate_projections.md  climate_experiment.md`

### Step 2.5: Commit

- [ ] Run:
```
git add dev/workflows/
git commit -m "$(cat <<'EOF'
m02d: add per-workflow contract docs (dev/workflows/)

Three docs documenting each workflow's owned config keys, input/output
contracts, downstream consumers, and known issues. The modularity
contract: when adding workflow #4, write its contract doc; when
replacing a workflow's internals, preserve the output contract.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 3: Atomic migration of test config + all 3 Snakefiles

**Files:**
- Modify: `tests/snake_config_model_test.yml`
- Modify: `tests/conftest.py` (fixtures read config keys directly — must update in lockstep)
- Modify: `Snakefile_model_creation`
- Modify: `Snakefile_climate_projections`
- Modify: `Snakefile_climate_experiment`

**Purpose:** This is the load-bearing commit of R01. The test config and all three Snakefiles flip from flat to sectioned in one atomic step. After this commit, `pytest tests/` passes against sectioned config; before, it doesn't.

**Why atomic:** Several keys are read by multiple Snakefiles (`project_dir`, `data_sources`, `clim_historical`, etc.). A staged migration would need either dual-key fallback logic in the Snakefiles (extra code to remove later) or a hybrid config that's hard to reason about. Atomic is simpler.

**Risk:** A renamed key the Snakefile still reads under its old name → silent default. Mitigation: dry-run all 3 Snakefiles before committing.

### Step 3.1: Rewrite tests/snake_config_model_test.yml

- [ ] Write the full new content (replaces existing 112 lines):

```yaml
# Test config for blueearth_cst — R01 sectioned schema.
# Used by tests/test_cli.py (Snakefile dry-runs) and any pytest cases
# that load a real config via tests/conftest.py.

project:
  project_dir: tests/test_project
  static_dir: config
  data_sources: tests/data/tests_data_catalog.yml
  data_sources_climate: config/cmip6_data.yml

shared:
  basin:
    region: "{'subbasin': [9.738, 0.4212], 'uparea': 70}"
    resolution: 0.0062475
  historical_window:
    starttime: "2015-01-01T00:00:00"
    endtime: "2020-12-31T00:00:00"
  clim_historical: era5
  wflow_outvars:
    - river discharge
    - precipitation
    - overland flow
    - actual evapotranspiration
    - groundwater recharge
    - snow

workflows:
  model_creation:
    enabled: true
    model_build_config: config/wflow_build_model.yml
    waterbodies_config: config/wflow_update_waterbodies.yml
    output_locations: tests/data/observations/output-locations-test.csv
    observations_timeseries: tests/data/observations/observations_timeseries_test.csv

  climate_projections:
    enabled: true
    clim_project: cmip6
    models:
      - NOAA-GFDL/GFDL-ESM4
      - INM/INM-CM5-0
    scenarios: [ssp245, ssp585]
    members: [r1i1p1f1]
    variables: [precip, temp]
    start_month_hyd_year: Jan
    historical_year_range: [2000, 2010]
    future_horizons:
      near: [2050, 2060]
      far:  [2090, 2100]
    save_grids: false

  climate_experiment:
    enabled: true
    experiment_name: experiment
    realizations_num: 2
    horizontime_climate: 2050
    run_length: 10
    run_historical: false
    stress_test:
      temp:
        step_num: 1
        transient_change: true
        mean:
          min: [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
          max: [3.0, 3.0, 3.0, 3.0, 3.0, 3.0, 3.0, 3.0, 3.0, 3.0, 3.0, 3.0]
      precip:
        step_num: 1
        transient_change: true
        mean:
          min: [0.7, 0.7, 0.7, 0.7, 0.7, 0.7, 0.7, 0.7, 0.7, 0.7, 0.7, 0.7]
          max: [1.3, 1.3, 1.3, 1.3, 1.3, 1.3, 1.3, 1.3, 1.3, 1.3, 1.3, 1.3]
        variance:
          min: [1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0]
          max: [1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0]
    Tlow: 2
    Tpeak: 10
    aggregate_rlz: true
```

Note: `historical_year_range: [2000, 2010]` becomes a list (not the comma-separated string `"2000, 2010"` from the flat config). Snakefiles need to handle this — see Snakefile updates below.

### Step 3.2: Rewrite Snakefile_model_creation top-of-file (lines 1-44)

- [ ] Replace lines 1–44 of `Snakefile_model_creation` (the imports, sys.argv hack, get_config def, and config-reading block) with this:

```python
import sys

# read path of the config file (passed via --configfile) so scripts can find it
args = sys.argv
config_path = args[args.index("--configfile") + 1]

# Function to get argument from config file and return default value if not found.
# Required keys raise on missing; optional keys return default.
def get_config(config, arg, default=None, optional=True):
    """Read a config key with optional default; raises on missing required keys."""
    if arg in config:
        return config[arg]
    elif optional:
        return default
    else:
        raise ValueError(f"Argument {arg} not found in config")

# R01 schema — three top-level sections. Read each into a local dict.
project_cfg = config["project"]
shared_cfg = config["shared"]
my_cfg = config["workflows"]["model_creation"]

# Project — paths and external resources
project_dir = get_config(project_cfg, "project_dir", optional=False)
static_dir = get_config(project_cfg, "static_dir", optional=False)
DATA_SOURCES = get_config(project_cfg, "data_sources", optional=False)

# Shared — multi-workflow scientific knobs
model_region = get_config(shared_cfg["basin"], "region", optional=False)
model_resolution = get_config(shared_cfg["basin"], "resolution", 0.00833333)
wflow_outvars = get_config(shared_cfg, "wflow_outvars", ['river discharge'])

# Workflow-owned
model_build_config = get_config(my_cfg, "model_build_config", f"{static_dir}/wflow_build_model.yml")
waterbodies_config = get_config(my_cfg, "waterbodies_config", f"{static_dir}/wflow_update_waterbodies.yml")
output_locations = get_config(my_cfg, "output_locations", None)
observations_timeseries = get_config(my_cfg, "observations_timeseries", None)

basin_dir = f"{project_dir}/hydrology_model"
```

### Step 3.3: Update Snakefile_model_creation `setup_runtime` rule params (line 124-126)

- [ ] In `Snakefile_model_creation`, find this block (around line 117-128):

```python
rule setup_runtime:
    input:
        gauges_fid = f"{basin_dir}/staticgeoms/outlets.geojson"
    output:
        forcing_yml = f"{project_dir}/config/wflow_build_forcing_historical.yml"
    params:
        starttime = get_config(config, "starttime", optional=False),
        endtime = get_config(config, "endtime", optional=False),
        clim_source = get_config(config, "clim_historical", optional=False),
        basin_dir = basin_dir,
    script: "src/setup_time_horizon.py"
```

- [ ] Replace the `params:` block with:

```python
    params:
        starttime = get_config(shared_cfg["historical_window"], "starttime", optional=False),
        endtime = get_config(shared_cfg["historical_window"], "endtime", optional=False),
        clim_source = get_config(shared_cfg, "clim_historical", optional=False),
        basin_dir = basin_dir,
```

### Step 3.4: Rewrite Snakefile_climate_projections top-of-file (lines 1-48)

- [ ] Replace lines 1–48 of `Snakefile_climate_projections` with:

```python
import itertools
import sys

# read path of the config file (passed via --configfile) so scripts can find it
args = sys.argv
config_path = args[args.index("--configfile") + 1]

# Function to get argument from config file and return default value if not found.
def get_config(config, arg, default=None, optional=True):
    """Read a config key with optional default; raises on missing required keys."""
    if arg in config:
        return config[arg]
    elif optional:
        return default
    else:
        raise ValueError(f"Argument {arg} not found in config")

# R01 schema
project_cfg = config["project"]
my_cfg = config["workflows"]["climate_projections"]

project_dir = get_config(project_cfg, "project_dir", optional=False)
DATA_SOURCES = get_config(project_cfg, "data_sources_climate", optional=False)

clim_project = get_config(my_cfg, "clim_project", optional=False)
models = get_config(my_cfg, "models", optional=False)
scenarios = get_config(my_cfg, "scenarios", optional=False)
members = get_config(my_cfg, "members", optional=False)
variables = get_config(my_cfg, "variables", optional=False)

start_month_hyd_year = get_config(my_cfg, "start_month_hyd_year", "Jan")
time_horizon_hist = get_config(my_cfg, "historical_year_range", optional=False)
future_horizons = get_config(my_cfg, "future_horizons", optional=False)

save_grids = get_config(my_cfg, "save_grids", False)

basin_dir = f"{project_dir}/hydrology_model"
clim_project_dir = f"{project_dir}/climate_projections/{clim_project}"

### Dictionary elements from the config based on wildcards
def get_horizon(wildcards):
    return config["workflows"]["climate_projections"]["future_horizons"][wildcards.horizon]
```

Note: `get_horizon` updated to navigate the new path.

### Step 3.5: Rewrite Snakefile_climate_experiment top-of-file (lines 1-53)

- [ ] Replace lines 1–53 of `Snakefile_climate_experiment` with:

```python
import sys
import numpy as np

# read path of the config file (passed via --configfile) so scripts can find it
args = sys.argv
config_path = args[args.index("--configfile") + 1]

# Function to get argument from config file and return default value if not found.
def get_config(config, arg, default=None, optional=True):
    """Read a config key with optional default; raises on missing required keys."""
    if arg in config:
        return config[arg]
    elif optional:
        return default
    else:
        raise ValueError(f"Argument {arg} not found in config")

# R01 schema
project_cfg = config["project"]
shared_cfg = config["shared"]
my_cfg = config["workflows"]["climate_experiment"]

project_dir = get_config(project_cfg, "project_dir", optional=False)
static_dir = get_config(project_cfg, "static_dir", optional=False)
DATA_SOURCES = get_config(project_cfg, "data_sources", optional=False)

experiment = get_config(my_cfg, "experiment_name", optional=False)
RLZ_NUM = get_config(my_cfg, "realizations_num", 1)

# Stress test step counts live under stress_test.<temp|precip>.step_num
stress_test_cfg = my_cfg["stress_test"]
ST_NUM = (
    get_config(stress_test_cfg["temp"], "step_num", 1) + 1
) * (
    get_config(stress_test_cfg["precip"], "step_num", 1) + 1
)

run_hist = get_config(my_cfg, "run_historical", False)
ST_START = 0 if run_hist else 1

clim_source = get_config(shared_cfg, "clim_historical", optional=False)
horizontime_climate = get_config(my_cfg, "horizontime_climate", optional=False)
wflow_run_length = get_config(my_cfg, "run_length", 20)

basin_dir = f"{project_dir}/hydrology_model"
exp_dir = f"{project_dir}/climate_{experiment}"
```

### Step 3.6: Update Snakefile_climate_experiment `export_wflow_results` rule params

- [ ] In `Snakefile_climate_experiment`, find the `params:` block in `rule export_wflow_results` (around line 191-196):

```python
    params:
        exp_dir = exp_dir,
        aggr_rlz = get_config(config, 'aggregate_rlz', True),
        st_num = ST_NUM,
        Tlow = get_config(config,"Tlow", 2),
        Tpeak = get_config(config,"Tpeak", 10),
```

- [ ] Replace with:

```python
    params:
        exp_dir = exp_dir,
        aggr_rlz = get_config(my_cfg, "aggregate_rlz", True),
        st_num = ST_NUM,
        Tlow = get_config(my_cfg, "Tlow", 2),
        Tpeak = get_config(my_cfg, "Tpeak", 10),
```

### Step 3.6b: Update tests/conftest.py fixtures

The fixtures `project_dir`, `data_sources`, and `model_build_config` in `tests/conftest.py` read config keys directly via `get_config(config, ...)`. They break after the config is sectioned unless updated.

- [ ] In `tests/conftest.py`, find this block (lines 38-67):

```python
@pytest.fixture()
def project_dir(config):
    """Return project directory"""
    project_dir = get_config(config, "project_dir", optional=False)
    project_dir = join(SNAKEDIR, project_dir)
    return project_dir


@pytest.fixture()
def data_sources(config):
    """Return data sources"""
    data_sources = get_config(config, "data_sources", optional=False)
    data_sources = join(SNAKEDIR, data_sources)
    return data_sources


@pytest.fixture()
def model_build_config(config):
    """Return model build config"""
    model_build_config = get_config(config, "model_build_config", optional=False)
    model_build_config = join(SNAKEDIR, model_build_config)
    return model_build_config
```

- [ ] Replace with:

```python
@pytest.fixture()
def project_dir(config):
    """Return project directory"""
    project_dir = get_config(config["project"], "project_dir", optional=False)
    project_dir = join(SNAKEDIR, project_dir)
    return project_dir


@pytest.fixture()
def data_sources(config):
    """Return data sources"""
    data_sources = get_config(config["project"], "data_sources", optional=False)
    data_sources = join(SNAKEDIR, data_sources)
    return data_sources


@pytest.fixture()
def model_build_config(config):
    """Return model build config"""
    model_build_config = get_config(
        config["workflows"]["model_creation"], "model_build_config", optional=False
    )
    model_build_config = join(SNAKEDIR, model_build_config)
    return model_build_config
```

### Step 3.7: Verify Python syntax of all 3 Snakefiles

- [ ] Run: `pixi run python -c "import ast; [ast.parse(open(f'Snakefile_{n}').read()) for n in ['model_creation', 'climate_projections', 'climate_experiment']]"`
- [ ] Expect: no output (clean parse)

### Step 3.8: Verify each Snakefile dry-runs against the new tests config

- [ ] Run: `pixi run snakemake all -c 1 -s Snakefile_model_creation --configfile tests/snake_config_model_test.yml --dry-run 2>&1 | tail -10`
- [ ] Expect: `Job stats:` table + dry-run summary, no Python errors
- [ ] Run: `pixi run snakemake all -c 1 -s Snakefile_climate_projections --configfile tests/snake_config_model_test.yml --dry-run 2>&1 | tail -10`
- [ ] Expect: `MissingInputException` for region.geojson (existing xfail behavior, NOT a Python error). If you see `KeyError`, a config key is wrong.
- [ ] Run: `pixi run snakemake all -c 1 -s Snakefile_climate_experiment --configfile tests/snake_config_model_test.yml --dry-run 2>&1 | tail -10`
- [ ] Expect: `CyclicGraphException` (existing xfail behavior, NOT a Python error).

### Step 3.9: Run full pytest suite

- [ ] Run: `pixi run pytest tests/ 2>&1 | tail -3`
- [ ] Expect: `45 passed, 4 xfailed` (unchanged from baseline)
- [ ] If counts differ: a config key migration is wrong. Diff the failures and trace back to the migration mapping in `dev/r01/modularity-contracts-design.md`.

### Step 3.10: Commit the atomic migration

- [ ] Run:
```
git add tests/snake_config_model_test.yml tests/conftest.py Snakefile_model_creation Snakefile_climate_projections Snakefile_climate_experiment
git commit -m "$(cat <<'EOF'
m02d: migrate test config + conftest + all 3 Snakefiles to sectioned schema (atomic)

Atomic migration: tests/snake_config_model_test.yml flips to the R01
schema (project / shared / workflows.<name>); tests/conftest.py
fixtures (project_dir, data_sources, model_build_config) follow the
new key paths; and all three Snakefiles update their config-key reads
in lockstep. After this commit, pytest passes against sectioned
config; before, it does not.

Why atomic: several keys (project_dir, data_sources, clim_historical)
are read by multiple Snakefiles; a staged migration would need dual-
key fallback logic. One commit is simpler and easier to revert.

Verification:
- python -c ast parse on all 3 Snakefiles → clean
- snakemake --dry-run on each → expected results (1 pass, 2 xfails)
- pytest tests/ → 45 passed, 4 xfailed (unchanged from baseline)

Note: src/ scripts that read the snake config directly (prepare_cst_
parameters.py, prepare_weagen_config.py, get_change_climate_proj.py)
will fail at runtime against the new schema. Task 3a fixes those.
Snakefile dry-run does NOT execute scripts so it cannot catch this.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 3a: Update direct config-file readers in src/

**Files:**
- Modify: `src/prepare_cst_parameters.py`
- Modify: `src/prepare_weagen_config.py`
- Modify: `src/get_change_climate_proj.py`

**Purpose:** Three scripts parse `config_path` directly (or receive params whose format changed) and break against the sectioned schema. Snakefile dry-run does not execute Python scripts, so Task 3's verification did NOT catch these. They must be migrated before any full workflow run.

**Risk:** Without this task, Task 7's full workflow run fails at runtime inside the scripts.

### Step 3a.1: Update src/prepare_cst_parameters.py

The script opens `config_path` and reads `yml["temp"]` / `yml["precip"]`. Under R01 those live under `yml["workflows"]["climate_experiment"]["stress_test"]`.

- [ ] In `src/prepare_cst_parameters.py`, find the block at lines 27-41:

```python
    # Read the yaml config
    with open(config_fn, "r") as stream:
        yml = yaml.load(stream, Loader=yaml.FullLoader)

    # Temperature change attributes
    delta_temp_mean_min = yml["temp"]["mean"]["min"]
    delta_temp_mean_max = yml["temp"]["mean"]["max"]
    temp_step_num = yml["temp"]["step_num"] + 1

    # Precip change attributes
    delta_precip_mean_min = yml["precip"]["mean"]["min"]
    delta_precip_mean_max = yml["precip"]["mean"]["max"]
    delta_precip_variance_min = yml["precip"]["variance"]["min"]
    delta_precip_variance_max = yml["precip"]["variance"]["min"]
    precip_step_num = yml["precip"]["step_num"] + 1
```

- [ ] Replace with:

```python
    # Read the yaml config (R01 sectioned schema)
    with open(config_fn, "r") as stream:
        yml = yaml.load(stream, Loader=yaml.FullLoader)

    stress_test_cfg = yml["workflows"]["climate_experiment"]["stress_test"]

    # Temperature change attributes
    delta_temp_mean_min = stress_test_cfg["temp"]["mean"]["min"]
    delta_temp_mean_max = stress_test_cfg["temp"]["mean"]["max"]
    temp_step_num = stress_test_cfg["temp"]["step_num"] + 1

    # Precip change attributes
    delta_precip_mean_min = stress_test_cfg["precip"]["mean"]["min"]
    delta_precip_mean_max = stress_test_cfg["precip"]["mean"]["max"]
    delta_precip_variance_min = stress_test_cfg["precip"]["variance"]["min"]
    delta_precip_variance_max = stress_test_cfg["precip"]["variance"]["min"]
    precip_step_num = stress_test_cfg["precip"]["step_num"] + 1
```

Note: line 40 `delta_precip_variance_max = yml["precip"]["variance"]["min"]` reads `min` for the max — preserved verbatim because it's an existing pre-R01 bug, not within R01's scope to fix.

### Step 3a.2: Update src/prepare_weagen_config.py

The script reads `yml_snake["realizations_num"]`, `yml_snake["temp"]`, and `yml_snake["precip"]` from the snake config. All three move under sectioned paths.

- [ ] In `src/prepare_weagen_config.py`, find lines 32-54 (the two yml_dict construction blocks):

```python
    # arguments from the default weagen config file
    yml_dict = read_yml(snakemake.params.default_config)
    # add new arguments from snakemake and yml_snake
    yml_add = {
        "output.path": snakemake.params.output_path,
        "sim.year.start": 2010,
        "sim.year.num": nr_years_weagen,
        "nc.file.prefix": snakemake.params.nc_file_prefix,
        "realizations_num": yml_snake["realizations_num"],
    }
    for k, v in yml_add.items():
        yml_dict["generateWeatherSeries"][k] = v

else:  # stress test
    # new arguments
    yml_dict = {
        "imposeClimateChanges": {
            "output.path": snakemake.params.output_path,
            "nc.file.prefix": snakemake.params.nc_file_prefix,
            "nc.file.suffix": snakemake.params.nc_file_suffix,
        }
    }
    # arguments from yml_snake
    yml_dict["temp"] = yml_snake["temp"]
    yml_dict["precip"] = yml_snake["precip"]
```

- [ ] Replace with:

```python
    # arguments from the default weagen config file
    yml_dict = read_yml(snakemake.params.default_config)
    # add new arguments from snakemake and yml_snake (R01 sectioned schema)
    experiment_cfg = yml_snake["workflows"]["climate_experiment"]
    yml_add = {
        "output.path": snakemake.params.output_path,
        "sim.year.start": 2010,
        "sim.year.num": nr_years_weagen,
        "nc.file.prefix": snakemake.params.nc_file_prefix,
        "realizations_num": experiment_cfg["realizations_num"],
    }
    for k, v in yml_add.items():
        yml_dict["generateWeatherSeries"][k] = v

else:  # stress test
    # new arguments
    yml_dict = {
        "imposeClimateChanges": {
            "output.path": snakemake.params.output_path,
            "nc.file.prefix": snakemake.params.nc_file_prefix,
            "nc.file.suffix": snakemake.params.nc_file_suffix,
        }
    }
    # arguments from yml_snake (R01 sectioned schema)
    stress_test_cfg = yml_snake["workflows"]["climate_experiment"]["stress_test"]
    yml_dict["temp"] = stress_test_cfg["temp"]
    yml_dict["precip"] = stress_test_cfg["precip"]
```

### Step 3a.3: Update src/get_change_climate_proj.py

The script receives `time_horizon_hist` and `time_horizon_fut` as Snakemake params and calls `.split(", ")` on them. After R01 those values are lists (`[1980, 2010]`), not comma-separated strings (`"1980, 2010"`). The `.split` call raises `AttributeError` on a list.

- [ ] In `src/get_change_climate_proj.py`, find lines 189-193:

```python
# Time tuples for comparison hist-fut
time_tuple_hist = snakemake.params.time_horizon_hist
time_tuple_hist = tuple(map(str, time_tuple_hist.split(", ")))
time_tuple_fut = snakemake.params.time_horizon_fut
time_tuple_fut = tuple(map(str, time_tuple_fut.split(", ")))
```

- [ ] Replace with:

```python
# Time tuples for comparison hist-fut.
# R01 schema delivers these as lists ([1980, 2010]). Pre-R01 configs
# delivered them as comma-separated strings ("1980, 2010"). Accept both.
def _to_str_tuple(value):
    if isinstance(value, str):
        return tuple(map(str, value.split(", ")))
    return tuple(map(str, value))

time_tuple_hist = _to_str_tuple(snakemake.params.time_horizon_hist)
time_tuple_fut = _to_str_tuple(snakemake.params.time_horizon_fut)
```

### Step 3a.4: Verify Python syntax

- [ ] Run: `pixi run python -c "import ast; [ast.parse(open(p).read()) for p in ['src/prepare_cst_parameters.py', 'src/prepare_weagen_config.py', 'src/get_change_climate_proj.py']]"`
- [ ] Expect: no output

### Step 3a.5: Run pytest to confirm no regressions

- [ ] Run: `pixi run pytest tests/ 2>&1 | tail -3`
- [ ] Expect: `45 passed, 4 xfailed` (unchanged — these scripts aren't directly unit-tested)

### Step 3a.6: Commit

- [ ] Run:
```
git add src/prepare_cst_parameters.py src/prepare_weagen_config.py src/get_change_climate_proj.py
git commit -m "$(cat <<'EOF'
m02d: migrate src/ scripts that read snake config directly

Three scripts parse the snake config (or receive params whose format
changed under R01) and break against the sectioned schema:

- prepare_cst_parameters.py: yml["temp"]/["precip"] →
  yml["workflows"]["climate_experiment"]["stress_test"]["temp"]/...
- prepare_weagen_config.py: yml_snake["realizations_num"]/["temp"]/
  ["precip"] → workflows.climate_experiment paths.
- get_change_climate_proj.py: time_horizon_hist/_fut now come in as
  lists (was comma-separated strings); accept both formats via a
  small _to_str_tuple helper.

Snakefile dry-run did NOT catch these because dry-run does not
execute Python scripts. The fix is required before any full workflow
run can succeed.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 3b: Mechanical flat-key audit

**Purpose:** Catch any old flat key references that escaped the migration. Quick `rg` sweep over all the files that might still reference flat keys.

### Step 3b.1: Grep for legacy flat-key access patterns

- [ ] Run:
```
pixi run python -c "
import subprocess
patterns = [
    r'config\[.project_dir.\]',
    r'config\[.data_sources.\]',
    r'config\[.data_sources_climate.\]',
    r'config\[.model_region.\]',
    r'config\[.model_resolution.\]',
    r'config\[.starttime.\]',
    r'config\[.endtime.\]',
    r'config\[.historical.\]',
    r'config\[.clim_historical.\]',
    r'config\[.experiment_name.\]',
    r'config\[.realizations_num.\]',
    r'config\[.future_horizons.\]',
    r'config\[.models.\]',
    r'config\[.scenarios.\]',
    r'yml\[.temp.\]',
    r'yml\[.precip.\]',
    r'yml_snake\[.temp.\]',
    r'yml_snake\[.precip.\]',
    r'yml_snake\[.realizations_num.\]',
    r\"get_config\(config, ['\\\"](?:project_dir|data_sources|model_region|starttime|endtime|historical|clim_historical|temp|precip|realizations_num|future_horizons|models|scenarios)['\\\"]\",
]
for p in patterns:
    r = subprocess.run(['rg', '-n', p, 'Snakefile_model_creation', 'Snakefile_climate_projections', 'Snakefile_climate_experiment', 'src/', 'tests/', 'dev/scripts/'], capture_output=True, text=True)
    if r.stdout:
        print(f'PATTERN: {p}')
        print(r.stdout)
"
```
- [ ] Expect: no output. Each non-empty pattern means a flat-key reference survived.
- [ ] If hits found: human review — some matches may be legitimate (local variable named `temp` or `precip` referring to a Python value, not a config key). Trace each hit to confirm.

### Step 3b.2: Note in plan tracker (no commit if no hits)

- [ ] If no hits: nothing to commit. Audit confirms migration completeness.
- [ ] If hits found: fix in a small commit `m02d: fix straggler flat-key reads (audit)`.

---

## Task 4: Migrate config/snake_config_model_test.yml (canonical example)

**Files:**
- Modify: `config/snake_config_model_test.yml`

**Purpose:** The canonical example config for non-test runs. The Snakefiles are already sectioned; this just brings the example config in line.

**No risk to tests.** `tests/test_cli.py` uses `tests/snake_config_model_test.yml` (already migrated). This file is for human use.

### Step 4.1: Rewrite config/snake_config_model_test.yml

- [ ] Replace the entire file with:

```yaml
# Canonical example config for blueearth_cst — R01 sectioned schema.
# This is the "small bbox, light models" example used to verify the
# stack works on a fresh install. Mirror this structure in your own
# project configs.
#
# For a clean template see config/snake_config.template.yml.

project:
  project_dir: examples/test
  static_dir: config
  data_sources: config/deltares_data.yml
  data_sources_climate: config/cmip6_data.yml

shared:
  basin:
    region: "{'subbasin': [9.666, 0.4476], 'uparea': 100}"
    resolution: 0.00833
  historical_window:
    starttime: "2000-01-01T00:00:00"
    endtime: "2005-12-31T00:00:00"
  clim_historical: era5
  wflow_outvars: ['river discharge']

workflows:
  model_creation:
    enabled: true
    model_build_config: config/wflow_build_model.yml
    waterbodies_config: config/wflow_update_waterbodies.yml
    output_locations: None
    observations_timeseries: None

  climate_projections:
    enabled: true
    clim_project: cmip6
    models:
      - NOAA-GFDL/GFDL-ESM4
      - INM/INM-CM4-8
      - INM/INM-CM5-0
      - NIMS-KMA/KACE-1-0-G
      - NCC/NorESM2-MM
      - NCC/NorESM2-LM
      - CMCC/CMCC-CM2-SR5
      - CMCC/CMCC-ESM2
    scenarios: [ssp245, ssp585]
    members: [r1i1p1f1]
    variables: [precip, temp]
    start_month_hyd_year: Jan
    historical_year_range: [1980, 2010]
    future_horizons:
      near: [2030, 2060]
      far:  [2070, 2100]
    save_grids: false

  climate_experiment:
    enabled: true
    experiment_name: experiment
    realizations_num: 2
    horizontime_climate: 2050
    run_length: 20
    run_historical: false
    stress_test:
      temp:
        step_num: 1
        transient_change: true
        mean:
          min: [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
          max: [3.0, 3.0, 3.0, 3.0, 3.0, 3.0, 3.0, 3.0, 3.0, 3.0, 3.0, 3.0]
      precip:
        step_num: 2
        transient_change: true
        mean:
          min: [0.7, 0.7, 0.7, 0.7, 0.7, 0.7, 0.7, 0.7, 0.7, 0.7, 0.7, 0.7]
          max: [1.3, 1.3, 1.3, 1.3, 1.3, 1.3, 1.3, 1.3, 1.3, 1.3, 1.3, 1.3]
        variance:
          min: [1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0]
          max: [1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0]
    Tlow: 2
    Tpeak: 10
    aggregate_rlz: true
```

### Step 4.2: Verify YAML parses

- [ ] Run: `pixi run python -c "import yaml; yaml.safe_load(open('config/snake_config_model_test.yml'))"`
- [ ] Expect: clean parse

### Step 4.3: Verify all 3 Snakefiles dry-run against this config

- [ ] Run: `pixi run snakemake all -c 1 -s Snakefile_model_creation --configfile config/snake_config_model_test.yml --dry-run 2>&1 | tail -10`
- [ ] Expect: dry-run summary, no Python errors. (May still error on missing data files since this points at deltares_data.yml — that's fine, we only need config parsing to succeed.)

### Step 4.4: Commit

- [ ] Run:
```
git add config/snake_config_model_test.yml
git commit -m "$(cat <<'EOF'
m02d: migrate canonical example config to sectioned schema

config/snake_config_model_test.yml flipped to the R01 schema. This is
the human-facing example config (the test variant lives at
tests/snake_config_model_test.yml and migrated in the previous commit).
The Snakefiles are already sectioned; this aligns the example.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 5: Migrate config/snake_config_model_test_linux.yml

**Files:**
- Modify: `config/snake_config_model_test_linux.yml`

**Purpose:** Linux variant of the canonical example. Same migration shape, different paths.

**Note:** Linux validation is deferred per `dev/roadmap.md` "Deferred: Linux replication". This file must continue to *parse cleanly* but isn't end-to-end validated.

### Step 5.1: Read current Linux config

- [ ] Run: `cat config/snake_config_model_test_linux.yml | head -120`
- [ ] Note any keys that differ from `config/snake_config_model_test.yml` (likely path differences only)

### Step 5.2: Rewrite preserving Linux-specific values

- [ ] Apply the same sectioning as Task 4.1, but preserve any Linux-specific paths verbatim. Concrete pattern:
  - Anywhere the original Linux config had `data_sources: config/deltares_data_linux.yml` (or similar Linux-specific path), keep that exact value but place it under `project.data_sources`.
  - Any `/mnt/...` or `${P_DRIVE}` paths from the original go in their Linux locations under the new sections.
  - All other structure mirrors `config/snake_config_model_test.yml`.

### Step 5.3: Verify YAML parses

- [ ] Run: `pixi run python -c "import yaml; yaml.safe_load(open('config/snake_config_model_test_linux.yml'))"`
- [ ] Expect: clean parse

### Step 5.4: Commit

- [ ] Run:
```
git add config/snake_config_model_test_linux.yml
git commit -m "$(cat <<'EOF'
m02d: migrate Linux example config to sectioned schema

Same migration as the Windows canonical, preserving Linux-specific
paths (data_sources_linux, mounted P drive locations). Linux end-to-end
validation is still deferred per the roadmap; this file just needs to
parse cleanly.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 6: Add user-facing migration guide for _local.yml configs

**Files:**
- Create: `dev/r01/local-config-migration.md`

**Purpose:** `_local.yml` configs are gitignored per-machine. The user (or any contributor with their own local config) needs a documented mapping to migrate manually.

### Step 6.1: Create the migration guide

- [ ] Write `dev/r01/local-config-migration.md`:

```markdown
# Migrating a local snake config to R01 sectioned schema

If you have a `*_local.yml` config (gitignored, per-machine), it still
uses the old flat schema after R01 lands. Migrate it manually using
the mapping below. The Snakefiles read sectioned config only after
R01, so old configs will fail with `KeyError`.

## Mapping table

| Old (flat) key                    | New (sectioned) location                                     |
| --------------------------------- | ------------------------------------------------------------ |
| `project_dir`                     | `project.project_dir`                                        |
| `static_dir`                      | `project.static_dir`                                         |
| `data_sources`                    | `project.data_sources`                                       |
| `data_sources_climate`            | `project.data_sources_climate`                               |
| `model_region`                    | `shared.basin.region`                                        |
| `model_resolution`                | `shared.basin.resolution`                                    |
| `starttime` (ISO datetime)        | `shared.historical_window.starttime`                         |
| `endtime` (ISO datetime)          | `shared.historical_window.endtime`                           |
| `clim_historical`                 | `shared.clim_historical`                                     |
| `wflow_outvars`                   | `shared.wflow_outvars`                                       |
| `model_build_config`              | `workflows.model_creation.model_build_config`                |
| `output_locations`                | `workflows.model_creation.output_locations`                  |
| `observations_timeseries`         | `workflows.model_creation.observations_timeseries`           |
| `clim_project`                    | `workflows.climate_projections.clim_project`                 |
| `models`                          | `workflows.climate_projections.models`                       |
| `scenarios`                       | `workflows.climate_projections.scenarios`                    |
| `members`                         | `workflows.climate_projections.members`                      |
| `variables`                       | `workflows.climate_projections.variables`                    |
| `start_month_hyd_year`            | `workflows.climate_projections.start_month_hyd_year`         |
| `historical: 1980, 2010` (str)    | `workflows.climate_projections.historical_year_range: [1980, 2010]` (list) |
| `future_horizons`                 | `workflows.climate_projections.future_horizons`              |
| `save_grids`                      | `workflows.climate_projections.save_grids`                   |
| `experiment_name`                 | `workflows.climate_experiment.experiment_name`               |
| `realizations_num`                | `workflows.climate_experiment.realizations_num`              |
| `horizontime_climate`             | `workflows.climate_experiment.horizontime_climate`           |
| `run_length`                      | `workflows.climate_experiment.run_length`                    |
| `run_historical`                  | `workflows.climate_experiment.run_historical`                |
| `temp.*`                          | `workflows.climate_experiment.stress_test.temp.*`            |
| `precip.*`                        | `workflows.climate_experiment.stress_test.precip.*`          |
| `Tlow`                            | `workflows.climate_experiment.Tlow`                          |
| `Tpeak`                           | `workflows.climate_experiment.Tpeak`                         |
| `aggregate_rlz`                   | `workflows.climate_experiment.aggregate_rlz`                 |

## New keys (no old equivalent)

For each workflow, add `enabled: true` (forward-compat marker;
documentary in R01). Default `true` for all three workflows.

## Format change for `historical`

The old flat config used `historical: 1980, 2010` — a string of two
comma-separated integers. The new key is
`workflows.climate_projections.historical_year_range: [1980, 2010]` — a
YAML list of two integers. Update the type when migrating.

## Verification

After migrating your local config, dry-run all 3 Snakefiles to catch
typos:

```bash
pixi run snakemake all -c 1 -s Snakefile_model_creation     --configfile <your_local_config.yml> --dry-run
pixi run snakemake all -c 1 -s Snakefile_climate_projections --configfile <your_local_config.yml> --dry-run
pixi run snakemake all -c 1 -s Snakefile_climate_experiment  --configfile <your_local_config.yml> --dry-run
```

Any `KeyError` in the dry-run output means a key wasn't migrated —
trace it via the table above.

## Reference

For a clean sectioned config, see:
- `config/snake_config.template.yml` (annotated template)
- `config/snake_config_model_test.yml` (working example, tiny bbox)
- `tests/snake_config_model_test.yml` (test fixture)
```

### Step 6.2: Commit

- [ ] Run:
```
git add dev/r01/local-config-migration.md
git commit -m "$(cat <<'EOF'
m02d: add migration guide for user-local configs

Per-machine *_local.yml configs are gitignored and must be migrated
manually. dev/r01/local-config-migration.md provides the full
old→new key mapping table plus the format change for historical
year_range (string → list).

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 7: Final verification, seal, and tag

**Files:**
- Create: `dev/r01/baseline_diffs.md` (documents expected config-snapshot drift)
- Modify: `dev/baseline/manifest.json` (re-recorded with new config-yaml hashes)
- Modify: `dev/roadmap.md` (status line)

**Purpose:** Three independent verifications, an expected diff documentation, then seal + tag.

**Critical context:** `dev/scripts/check_baseline.py` includes the copied snake-config YAMLs as manifest targets (lines 58, 66, 70). After R01, those YAML hashes change because the schema changed. This is **expected organizational drift, not scientific drift** — the netCDF / CSV / PNG hashes remain identical. Document in `dev/r01/baseline_diffs.md` and re-record the manifest.

`check_baseline.py` defaults to `PROJECT_DIR_DEFAULT = "examples/test_local"`. Every verification command in this task passes `--project-dir` explicitly so the run dir and check dir match.

### Step 7.1: Verification A — pytest suite

- [ ] Run: `pixi run pytest tests/ -v 2>&1 | tail -10`
- [ ] Expect: `45 passed, 4 xfailed` (same as baseline — config restructure must not change test outcomes)

### Step 7.2: Verification B — parse + dry-run for all three workflows

- [ ] Run (each separately):
```
pixi run snakemake all -c 1 -s Snakefile_model_creation     --configfile tests/snake_config_model_test.yml --dry-run 2>&1 | tail -5
pixi run snakemake all -c 1 -s Snakefile_climate_projections --configfile tests/snake_config_model_test.yml --dry-run 2>&1 | tail -5
pixi run snakemake all -c 1 -s Snakefile_climate_experiment  --configfile tests/snake_config_model_test.yml --dry-run 2>&1 | tail -5
```
- [ ] Expect: model_creation parses cleanly + dry-run summary; climate_projections fails with `MissingInputException` on region.geojson (existing xfail); climate_experiment fails with `CyclicGraphException` (existing xfail). **No `KeyError` or `AttributeError`** — those would mean a config migration is wrong.

### Step 7.3: Verification C — full workflow + scientific baseline

Run all three workflows end-to-end against the test config, then check the scientific targets only.

- [ ] Choose the project_dir: the test config writes to `tests/test_project`. Use that.
- [ ] Run: `pixi run snakemake all -c 1 -s Snakefile_model_creation --configfile tests/snake_config_model_test.yml 2>&1 | tail -20`
- [ ] Expect: `<N> of <N> steps (100%) done`. Check `tests/test_project/hydrology_model/staticmaps.nc` exists.
- [ ] (Optional, if you have CMIP6 access via cmip6_data.yml) Run: same for `Snakefile_climate_projections`. Skip if CMIP6 isn't accessible from your env.
- [ ] (Optional) Same for `Snakefile_climate_experiment`.
- [ ] Run: `pixi run python dev/scripts/check_baseline.py check --project-dir tests/test_project 2>&1 | tail -30`

**Expected output:** the three scientific PNG / netCDF / CSV targets match the manifest fingerprints; the three copied-config YAML targets report mismatches (their hashes have changed).

If scientific targets show diffs: a config migration changed numerical output. Most likely cause: a value retyped during YAML rewrite changed precision (e.g., `0.00833` vs `0.00833333`), or `historical_year_range` migration introduced an off-by-one. Trace via the failing artifact's variable name back to the script that produced it.

### Step 7.4: Document the expected config-snapshot drift

- [ ] Create `dev/r01/baseline_diffs.md` with this content:

```markdown
# R01 baseline diffs

**Date.** 2026-05-09.

## Summary

Three baseline-manifest entries change as a result of R01's config
schema migration. None reflect scientific drift — they are purely the
result of `src/copy_config_files.py` writing the new sectioned YAML
(instead of the old flat YAML) into `{project_dir}/config/` per
workflow's `rule copy_config`.

## Affected manifest entries

| Target template                                                            | Reason                              |
| -------------------------------------------------------------------------- | ----------------------------------- |
| `{project_dir}/config/snake_config_model_creation.yml`                     | Sectioned schema → different bytes  |
| `{project_dir}/config/snake_config_climate_projections.yml`                | Sectioned schema → different bytes  |
| `{project_dir}/config/snake_config_climate_experiment.yml`                 | Sectioned schema → different bytes  |

These three YAMLs are full copies of the input snake config (whatever
the user passed via `--configfile`). R01 changes the input config
shape, so the copied output also changes shape. The hash diff is
deterministic.

## Scientific targets (unchanged)

All netCDF / CSV / PNG manifest targets match the M2b baseline
exactly. Specifically:

- `{project_dir}/plots/wflow_model_performance/{hydro_wflow_1,basin_area,precip}.png`
- `{clim_project_dir}/annual_change_scalar_stats_summary.{nc,csv}`
- `{clim_project_dir}/annual_change_scalar_stats_summary_mean.csv`
- `{clim_project_dir}/plots/{projected_climate_statistics,precipitation_anomaly_projections_abs,temperature_anomaly_projections_abs}.png`
- `{exp_dir}/model_results/{Qstats,basin}.csv`

## Action

`dev/baseline/manifest.json` re-recorded against the new config-yaml
hashes via:

```bash
pixi run python dev/scripts/check_baseline.py record --project-dir tests/test_project
```

The new manifest is the R01 contract. R3+ milestones are bound by
the new manifest.
```

### Step 7.5: Re-record the manifest

- [ ] Run: `pixi run python dev/scripts/check_baseline.py record --project-dir tests/test_project 2>&1 | tail -10`
- [ ] Verify: `git diff dev/baseline/manifest.json` shows changes only in the three `snake_config_<workflow>.yml` entries (their `sha256` and `payload` change). Other entries unchanged.

### Step 7.6: Run baseline check one more time to confirm zero diff

- [ ] Run: `pixi run python dev/scripts/check_baseline.py check --project-dir tests/test_project 2>&1 | tail -10`
- [ ] Expect: all targets verified, zero diff. (Now passes because the manifest holds the new YAML hashes.)

### Step 7.7: Edit roadmap.md to seal R1

- [ ] In `dev/roadmap.md`, find:

```markdown
## R1 — Modularity contracts (pre-R3)

**Goal.** Establish per-workflow config contracts so workflows can be
```

- [ ] Insert a status line between heading and goal:

```markdown
## R1 — Modularity contracts (pre-R3)

**Status.** Sealed YYYY-MM-DD — three top-level config sections in
place; three contract docs under dev/workflows/; all 3 Snakefiles +
3 src/ scripts read sectioned config; migration guide for user-local
configs at dev/r01/local-config-migration.md. Suite: 45 passed, 4
xfailed. Scientific baseline: zero diff. Config-snapshot YAML hashes
re-baselined per dev/r01/baseline_diffs.md (organizational drift,
not scientific).

**Goal.** Establish per-workflow config contracts so workflows can be
```

Replace `YYYY-MM-DD` with today's date.

### Step 7.8: Add an R3 roadmap note (configfile mechanism already done)

R3's roadmap section currently lists `workflow.configfiles[0]` as a deliverable. R01 delivers it. Mark accordingly so R3 doesn't redo it.

- [ ] In `dev/roadmap.md`, find the R3 section's "Cross-cutting deliverables" block:

```markdown
**Cross-cutting deliverables (done once here, reused by R4 and R5).**
- Collapse the duplicated `get_config(config, key, default, optional)`
  helper from all three Snakefiles into one shared module at
  `src/snake_utils.py`. Update *all three* Snakefiles to import from it.
  Behavior of R4/R5's Snakefiles unchanged; only the helper sourcing moves.
- Replace the `--configfile` `sys.argv` re-parsing trick in *all three*
  Snakefiles with a cleaner mechanism (e.g. `workflow.configfiles[0]`),
  documented in `src/snake_utils.py` so the next contributor can tell why.
```

- [ ] Replace with:

```markdown
**Cross-cutting deliverables (done once here, reused by R4 and R5).**
- Collapse the duplicated `get_config(config, key, default, optional)`
  helper from all three Snakefiles into one shared module at
  `src/snake_utils.py`. Update *all three* Snakefiles to import from it.
  Behavior of R4/R5's Snakefiles unchanged; only the helper sourcing moves.
- ~~Replace the `--configfile` `sys.argv` re-parsing trick in all three
  Snakefiles with `workflow.configfiles[0]`.~~ **Done by R01.**
```

### Step 7.9: Commit roadmap update + baseline_diffs + manifest

- [ ] Run:
```
git add dev/roadmap.md dev/r01/baseline_diffs.md dev/baseline/manifest.json
git commit -m "$(cat <<'EOF'
m02d: mark milestone sealed in roadmap; re-baseline config snapshots

Three sectioned config sections, three contract docs, three migrated
config files, three updated Snakefiles, three updated src/ scripts.
Pattern established for R3-R5 to inherit.

Scientific baseline preserved exactly. Config-snapshot YAML hashes
re-recorded as expected organizational drift (not scientific) per
dev/r01/baseline_diffs.md. The new manifest is the R01 contract.

Marks R3's configfile mechanism deliverable as already-done by R01
to prevent rework.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

### Step 7.10: Tag the milestone

- [ ] Run: `git tag -a r01-contracts -m "r01-contracts: per-workflow config contracts"`
- [ ] Verify: `git tag -l "m0*"` should now include `r01-contracts`

### Step 7.11: Report

- [ ] Summarize to the user:
  - Branch `milestone/r01-contracts` complete, tagged `r01-contracts`.
  - Suite: `45 passed, 4 xfailed` (unchanged).
  - Baseline check: zero diff.
  - Files added: 1 template + 3 contract docs + 1 migration guide.
  - Files modified: 3 configs + 3 Snakefiles + roadmap.

---

## Notes for the executing engineer

- **The Step 3.10 commit is the load-bearing one.** Everything before it (template + contract docs) is additive; everything after it (canonical config + Linux config) is downstream of the Snakefiles already being sectioned. If Step 3.10 lands cleanly, the rest is mechanical.
- **If you discover a config key I missed** (the migration mapping in `dev/r01/modularity-contracts-design.md` and Task 6's table is what the Snakefiles depend on), stop and surface it. Don't silently extend the mapping — the user reviewed the design with the documented mapping.
- **The `historical_year_range` format change** is intentional. Old: `"1980, 2010"` (a string). New: `[1980, 2010]` (a list). Snakefile_climate_projections's `time_horizon_hist` variable now receives a list. If downstream Python code in `src/get_change_climate_proj.py` or similar parses it as a string, that's a separate bug to flag (not fix in R01).
- **Don't migrate `*_local.yml` files automatically.** They're gitignored. Task 6's guide is what the user follows manually.
- **The `enabled: true` flag is documentary in R01.** Don't add Snakefile-side logic that respects it; that's R6+ work.

## Quick reference: file inventory

| File | Action |
|---|---|
| `config/snake_config.template.yml` | Create (Task 1) |
| `dev/workflows/model_creation.md` | Create (Task 2) |
| `dev/workflows/climate_projections.md` | Create (Task 2) |
| `dev/workflows/climate_experiment.md` | Create (Task 2) |
| `tests/snake_config_model_test.yml` | Modify (Task 3) |
| `tests/conftest.py` | Modify (Task 3) |
| `Snakefile_model_creation` | Modify (Task 3) |
| `Snakefile_climate_projections` | Modify (Task 3) |
| `Snakefile_climate_experiment` | Modify (Task 3) |
| `src/prepare_cst_parameters.py` | Modify (Task 3a) |
| `src/prepare_weagen_config.py` | Modify (Task 3a) |
| `src/get_change_climate_proj.py` | Modify (Task 3a) |
| `config/snake_config_model_test.yml` | Modify (Task 4) |
| `config/snake_config_model_test_linux.yml` | Modify (Task 5) |
| `dev/r01/local-config-migration.md` | Create (Task 6) |
| `dev/r01/baseline_diffs.md` | Create (Task 7) |
| `dev/baseline/manifest.json` | Modify (Task 7) |
| `dev/roadmap.md` | Modify (Task 7) |

## Quick reference: expected commit count

9 commits + 1 tag:
1. Template (Task 1)
2. Contract docs (Task 2)
3. Atomic migration: tests config + conftest + 3 Snakefiles (Task 3)
3a. src/ direct config readers (Task 3a)
3b. Audit fixes (Task 3b — only if hits)
4. Canonical example config (Task 4)
5. Linux example config (Task 5)
6. Local-config migration guide (Task 6)
7. Seal: roadmap + baseline_diffs + re-recorded manifest (Task 7.9)
8. Tag `r01-contracts` (Task 7.10)
