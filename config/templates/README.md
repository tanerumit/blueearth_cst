# Config templates

**Scaffolds you copy. Nothing here is read by a running workflow.** Copy, fill
in, point a config at your copy.

The configs a rule actually *reads* live in **`config/defaults/`**. Until
2026-08-11 both kinds shared this directory, so its name described only half of
what it held; see `config/defaults/README.md`.

| File | Purpose |
| --- | --- |
| `project_config.template.yml` | The project file: what every workflow shares, and which workflows run. Start here. |
| `project_config.analyze_climate.template.yml` | wf0. Empty on purpose; it reads the project file. |
| `project_config.build_model.template.yml` | wf1: observations, run period, engine configs |
| `project_config.analyze_projections.template.yml` | wf2: models, scenarios, variables, windows |
| `project_config.run_stress_test.template.yml` | wf3: experiment, perturbation grid, compute |
| `output_locations_template.csv` | Header-only schema for output locations |
| `observed_daily_discharge_template.csv` | Header-only schema for observed discharge |
| `archive/` | Unmaintained single-workflow configs; see its own README |

The five YAML files are one set. Copy all five into your project folder and
pass the project file to `--configfile`; its `config_path:` lines name the other
four. A filled-in worked example is `test_case/project_config_rapid.yml` with
its siblings; `docs/guide/configuration.qmd` walks through the layout.

`wflow_sbm.reference.toml` sits here as a **reference copy only** — no Snakefile,
script or test reads it. Rule 1.07 has hydromt generate the project's own TOML
from hydromt_wflow's defaults. Treat this file as documentation, and expect it to
lag: measured 2026-08-10, it was 126 lines against the 149 a real build emitted.
The `.reference.` infix is there because the bare name `wflow_sbm.toml` read as a
build input, which is exactly what it is not.

**Rename after copying.** Layer names inside the model are derived from your
file's basename (`blueearth_cst/shared/gauges.py`), so a file still called
`output_locations_template.csv` yields layers named `output-locations-template`.
Drop the `_template` suffix when you copy.

---

# Why the template's defaults are what they are

The templates state what each key does. The reasoning behind the non-obvious
defaults lives here.

### `climate.window` — minimum 16 years

Enforced at parse time and again at extraction. weathergenr's wavelet
decomposition needs at least 16 annual observations, so a shorter record cannot
support a stress test at all. The floor is `constraints.min_historical_years` in
`config/advanced_settings.yml` and is **not** overridable per project.

The window is inclusive water years; the model's own run period
(`simulation_window` in the build_model file) may be shorter and must sit inside
it.

### `members.preference` — why four labels, not one

Not every model publishes `r1i1p1f1`. CNRM-\*, MIROC-ES2L, UKESM1-0-LL and
MCM-UA-1-0 use `f2`; HadGEM3-GC31-\* use `f3`; CanESM5-CanOE uses `p2f1`. Pinning
`r1i1p1f1` alone silently drops them — 38 of 45 usable models. A label a model
does not publish is simply skipped, because the catalog declares exactly what
exists.

The four shipped labels were chosen empirically over the generated catalog: they
reach 45 models across the tier-1 SSPs. Adding further physics variants (`p3f1`,
`p5f1`, `r1i1000p1f1`, …) reaches *fewer*, because they make a model's historical
and future member sets differ. When those differ, the change-factor stage raises
`asymmetric hist/clim members` rather than quietly using the intersection. With
this list that affects CAMS-CSM1-0, CanESM5, EC-Earth3 (ssp245), GISS-E2-1-G,
GISS-E2-1-H, IPSL-CM6A-LR (ssp434/460), MCM-UA-1-0 and NorESM2-LM (ssp245) — for
those, narrow `members.preference` to the one label the model shares across your
scenarios, or name it in `members.overrides`.

Per-model member counts: `dev/reference/workflows/wf2-cmip6-monthly-members.csv`.

### `models` — every CMIP6 model with a historical member

The template lists three. All 65 in the shipped catalog, as `Institution/Source`:

```
AS-RCEC/TaiESM1                 AWI/AWI-CM-1-1-MR               AWI/AWI-ESM-1-1-LR
BCC/BCC-CSM2-MR                 BCC/BCC-ESM1                    CAMS/CAMS-CSM1-0
CAS/CAS-ESM2-0                  CAS/FGOALS-f3-L                 CAS/FGOALS-g3
CCCR-IITM/IITM-ESM              CCCma/CanESM5                   CCCma/CanESM5-CanOE
CMCC/CMCC-CM2-HR4               CMCC/CMCC-CM2-SR5               CMCC/CMCC-ESM2
CNRM-CERFACS/CNRM-CM6-1         CNRM-CERFACS/CNRM-CM6-1-HR      CNRM-CERFACS/CNRM-ESM2-1
CSIRO/ACCESS-ESM1-5             CSIRO-ARCCSS/ACCESS-CM2         E3SM-Project/E3SM-1-0
E3SM-Project/E3SM-1-1           E3SM-Project/E3SM-1-1-ECA       EC-Earth-Consortium/EC-Earth3
EC-Earth-Consortium/EC-Earth3-AerChem                           EC-Earth-Consortium/EC-Earth3-CC
EC-Earth-Consortium/EC-Earth3-Veg                               EC-Earth-Consortium/EC-Earth3-Veg-LR
FIO-QLNM/FIO-ESM-2-0            HAMMOZ-Consortium/MPI-ESM-1-2-HAM
INM/INM-CM4-8                   INM/INM-CM5-0                   IPSL/IPSL-CM5A2-INCA
IPSL/IPSL-CM6A-LR               IPSL/IPSL-CM6A-LR-INCA          KIOST/KIOST-ESM
MIROC/MIROC-ES2H                MIROC/MIROC-ES2L                MIROC/MIROC6
MOHC/HadGEM3-GC31-LL            MOHC/HadGEM3-GC31-MM            MOHC/UKESM1-0-LL
MPI-M/ICON-ESM-LR               MPI-M/MPI-ESM1-2-HR             MPI-M/MPI-ESM1-2-LR
MRI/MRI-ESM2-0                  NASA-GISS/GISS-E2-1-G           NASA-GISS/GISS-E2-1-G-CC
NASA-GISS/GISS-E2-1-H           NASA-GISS/GISS-E2-2-H           NCAR/CESM2
NCAR/CESM2-FV2                  NCAR/CESM2-WACCM                NCAR/CESM2-WACCM-FV2
NCC/NorCPM1                     NCC/NorESM2-LM                  NCC/NorESM2-MM
NIMS-KMA/KACE-1-0-G             NIMS-KMA/UKESM1-0-LL            NOAA-GFDL/GFDL-CM4
NOAA-GFDL/GFDL-ESM4             NUIST/NESM3                     SNU/SAM0-UNICON
THU/CIESM                       UA/MCM-UA-1-0
```

The list is generated from the catalog; a model you add to
`config/catalogs/cmip6_data.yml` qualifies the same way.

### `reference_window` — why 1985–2014

Thirty years ending at the last year the CMIP6 historical experiment covers
(owner ruling OQ-4, 2026-07-29).

- 30 years is the WMO climatological normal, and the workflow warns below 20. A
  shorter reference makes every derived statistic noisier and the tail quantiles
  unsupportable — which is why those are opt-in via `stats:`.
- 2014 ends the historical experiment. Asking for more is not an error: the
  window is **clipped** to 2014 and the run says so on stderr. Scenario data is
  never spliced in to fill the gap, so the extra years simply do not arrive.
- The range is inclusive **calendar** years, unlike `climate.window` in the
  project file, which is water years. With the default `climate.water_year_start:
  Jan` the two coincide; any other start month trims the partial years at both
  ends one layer down. Every artifact reports the effective window and count
  beside the nominal one.

### `experiment_name` — why it is absent rather than set

Left unset, WF3 names the directory from the project's own name plus the date the
experiment was first created, and later runs **reuse** that directory rather than
minting today's date — which is what keeps incremental reruns idempotent. A
placeholder value in the template would instead put every project copied from it
into one shared `experiments/experiment/`.

To pin a deliberate name, run this once before the first climate-experiment run:

```console
pixi run python scripts/suggest_experiment_name.py <your config>
pixi run python scripts/suggest_experiment_name.py <your config> --name dry_scenario
```

It reserves the directory atomically, versions a generated collision to `_v2`,
and refuses to overwrite a name already set — which would strand a completed
experiment's outputs under a name nothing points at.

### `julia_threads` — a toolbox setting, not a project one

It lives in `config/advanced_settings.yml` under `runtime:` and has no
per-project override. Wflow parallelizes over grid **cells**, so raising it pays
on a large basin and does nothing on a small one. It is not Snakemake's
`--cores`: the two multiply, so keep `--cores N × julia_threads <= logical CPUs`.

### `compute.batch_size` / `compute.batch_size_max`

WF3 groups stress-test members into batches for the Wflow run. Disk is the
binding constraint on large sweeps, because concurrent batches are resident at
once — so `batch_size_max` (default 8) bounds the footprint, while an explicit
`batch_size` wins outright. Both fail at parse time, naming the offending key, if
set below 1. `compute.disk_headroom_gb` states an absolute disk budget; absent,
the toolbox keeps `defaults.batch_disk_headroom_fraction` of free disk
(`config/advanced_settings.yml`).

### `basin.sources.hydrography` / `basin.sources.basin_index`

Catalog **entry names**, not paths. They must match `setup_basemaps` in the
`engine.build_config` template, or rule 1.02 fails loudly naming both files and
both values.

---

# Observation inputs

The two CSV scaffolds above are the optional observation inputs of workflow 1
(`build_model.smk`). Copy them next to your basin data and point the
config at the copies by **absolute path** — real basin data lives in the project
folder, never in this repository (see `AGENTS.md` § Repo Map, the two-tier
`project_dir` rule).

Both inputs are optional. To run without them:

```yaml
# project file
basin:
  output_locations: null

# build_model file
observations:
```

**They work as a pair.** `observations` without `basin.output_locations` has
nothing to key against: the series columns are matched by resolved `wflow_id`,
and those ids only exist once output locations have driven the delineation.
`observations` is keyed by variable, and the variable must be one of
`model.outvars`; a series for a variable the model does not write is refused at
parse time.

## `output_locations_template.csv`

Output locations, **comma**-separated:

| Column | Meaning |
| --- | --- |
| `wflow_id` | optional integer station id; when supplied it must exactly match the deterministic ID generated from the resolved basin/subbasin hierarchy |
| `station_name` | free-text label used in figure titles and metric tables |
| `x`, `y` | longitude, latitude in EPSG:4326 |
| `location_role` | optional role: `control` (default) defines a subbasin; `observation` is tracked without controlling delineation |

### How `wflow_id` is built

```
wflow_id = basin_id*1000 + local_subbasin_number*10 + m
```

`m = 0` for the subbasin's own primary location and `1`–`9` for additional
points inside it. Basin 1 reads `1010, 1011, 1020, 1030…`; basin 2 reads
`2010, 2011, …`. Ids therefore group by basin, order by subbasin, and keep the
subbasin legible in the flat integer.

Both files are keyed by `wflow_id`, so the locations file's `wflow_id` column and
the discharge file's column headers must agree. Neither failure is silent: a
pinned `wflow_id` that does not match the resolved hierarchy stops preparation
with an explicit old-ID → resolved-ID crosswalk, and an observation header
carrying ids the registry does not know fails the WF1 header check by name.

The simplest way to obtain ids is to **omit the `wflow_id` column**, run WF1
once, and read the assigned ids out of `data/spatial/location_registry.csv` —
the column is optional, and pinning it is only worth doing when you need the ids
to stay fixed across rebuilds.

`location_code` (`B001-S01-L01`) is for reading; `wflow_id` is the integer for
joining and for scanning a CSV header.

## `observed_daily_discharge_template.csv`

Observed discharge, **semicolon**-separated — deliberately a different
separator from the locations file; both are read with explicit `sep=`
arguments, so keep each file's separator as shipped.

- First column `time`, ISO-8601 timestamps (`2000-01-01T00:00:00`).
- One further column per station, named by the resolved **`wflow_id`** value in
  `spatial/location_registry.csv` — not by `station_name`.
- Missing values: leave the field empty.

The shipped header (`time;1010;1020`) is illustrative — replace `1010` and `1020`
with your own `wflow_id` values and add one column per station. The two files
must be changed **together**. Before plotting, Workflow 1 checks the raw header
against `spatial/location_registry.csv`: duplicate or unknown IDs fail
explicitly, as does a missing series for any user-provided control or
observation location. Automatically generated outlets may be included but do
not require an observation series.

## What consumes these

The spatial-preparation phase reads output locations to control subbasin
delineation and writes `spatial/location_registry.csv`. The Wflow adapter then
uses that registry for gauge/output IDs; `plot_results.py` uses the same IDs for
observation joins. A configured path is a declared Snakemake input, so a typo
fails as a missing input instead of silently dropping observation outputs.

## Where they end up

Both files are snapshotted into `<project_dir>/config/basin_data/` by rule
1.01, alongside the run's config (`config/runs/`), catalogs (`config/catalogs/`)
and build templates (`config/templates/`). The bin is named for what it holds —
local, basin-scoped tabular inputs — not for observations alone: only one of the
two files is an observation, the other declares where the model reports. They are
referenced by **absolute path** from wherever you keep them, so without that
copy a finished project could not say what it was evaluated against — the
metrics table would cite gauges and observations that exist only on the machine
that ran it.
