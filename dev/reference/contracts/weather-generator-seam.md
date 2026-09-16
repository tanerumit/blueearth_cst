# Contract: weather-generator seam (WG-1 .. WG-6)

> **Genre:** dev-facing interchange contract. **Audience:** a future *swapper* —
> someone replacing `weathergenr` with an alternative weather generator, or the
> R6 model-flexibility work — read end-to-end. Not an end-user doc (hence `dev/`,
> not `docs/`; precedent `dev/reference/workflows/climate_experiment.md`).
> **Source of record:** `dev/milestones/p32b/interchange-contracts-design.md` (ACCEPTED
> 2026-07-24, §5.2 / §5.4 / §5.6 / §5.5). Every load-bearing fact below cites a
> Snakefile line, a script line, or an observed fixture artifact; do not add a
> contract fact that is not so grounded.

## Scope and method

The **weather-generator seam** is the point in `generate_scenarios.smk`
(wf3) where the stochastic weather generator could be swapped for an alternative
without re-architecting the rest of the pipeline. `weathergenr` (R) is the
current occupant, but **this contract is generator-agnostic**: it pins what wf3
hands *in* to the generator and expects *out* of it, not weathergenr's internals.

**Grounded in** the fixture tree `test_case/test_local` (era5 branch,
`test_case/project_config_baseline.yml`) inspected with xarray for
dims/coords/vars/units/attrs, and the wf3 rules + scripts. **CST-scope
disclaimer** (`AGENTS.md` Hard Constraints): a contract surface pins only what
OUR pipeline's producer guarantees or OUR consumer relies on; upstream tool
internals (hydromt catalog machinery, weathergenr's algorithm) are consumed
verbatim and are *not* re-specified here. The producer-side (R) surface (WG-3
config keys, WG-4 output shape) is derived **read-only** from
`blueearth_cst/weathergen/{global.R,generate_weather.R,impose_climate_change.R}`
— those files are never edited.

The provider binds pure scenario rows to the unchanged R generator operations.
WF3 publishes durable forcing and a portable preparation context. WF4 consumes
the collection through the Wflow adapter. Native metadata and effective units
are recorded separately; see the accepted
[unit trace](../../milestones/r12/implementation/evidence/p1-forcing-units.md).

**Fixture branch = era5.** Branch-specific facts (chirps precip-only, the chirps
orography sidecar) are documented from code and tagged **not fixture-verified
(no chirps fixture)** where no chirps fixture exists — never faked green.

**Contract-surface tiers** (design §5.1), applied per artifact below:

1. **Pinned (contract surface)** — a structural fact a swap MUST reproduce for
   the downstream consumer to work.
2. **Pinned-as-reliance** — OUR consumed subset of an upstream schema (e.g. the
   hydromt data-catalog schema); we pin the fields we emit/read, not the whole
   upstream schema.
3. **Deliberately unpinned** — internal detail (provenance attrs, encoding,
   machine-scoped paths) recorded as unpinned so the omission is auditably
   intentional, not an oversight.

Per-artifact schema (design §5.4): *artifact id · path pattern · producer rule ·
consumer rule(s) · dims · coords (dtype/units/calendar) · data_vars
(dtype/units) · CRS · time axis/calendar · naming pattern · temp() lifecycle ·
pinned surface · deliberately unpinned · validator*. Rendered as one subsection
per artifact (a literal 14-column table is illegible).

---

## WG-1 — historical climate extraction

- **path pattern:** `data/climate/historical/<key>/extract_historical.nc`, where
  `<key> = <clim_source>_<startYYYYMMDD>_<endYYYYMMDD>` (P3-1 keyed store).
- **producer:** rule `extract_historical_climate`
  (`blueearth_cst/climate_analysis/extract_historical_climate.py`) — ONE rule,
  declared identically in `generate_scenarios.smk` (3.02) and
  `build_model.smk` (1.04) from `snake_utils.climate_store_rule`
  (R07 B1). Its inputs are the data catalog and the project region artifact
  `spatial/geoms/region.geojson`; the extent is still model-free, but it is
  delineated once per project by rule `delineate_region` (ADR 0003) rather
  than per store key. The store records the extent it cut to in the
  extraction's own attributes (`region_bbox`, `region_geojson_sha256`,
  `region_source`).
- **consumer:** rule 3.07 `generate_weather_realizations` (weathergenr
  `generate_weather.R`), passed in as `climate_nc`.
- **dims:** `(time, latitude, longitude)`.
- **coords:** `time` — `datetime64[ns]`, daily, `calendar=proleptic_gregorian`;
  `latitude` / `longitude` — `float32`, `degrees_north` / `degrees_east`;
  `spatial_ref` — EPSG:4326 (WKT).
- **data_vars** (all `float32 (time, latitude, longitude)`): `precip`
  (`mm d**-1`); `temp` / `temp_min` / `temp_max` (**K** — see units note);
  `kin` / `kout` (`J m**-2`); `press_msl` (`Pa`).
- **CRS:** EPSG:4326 (global attr `crs=4326`, `category=meteo`).
- **time axis/calendar:** daily `proleptic_gregorian`.
- **naming pattern:** `<clim_source>_<start>_<end>/extract_historical.nc`.
- **temp() lifecycle:** not `temp()`; consumed via `ancient()` on the DAG.
- **pinned surface:** the dims, the coord axes + CRS, the seven variable names
  and their `float32` dtype. **Every WG-1 unit is under the `units` (plural)
  attr key** — fixture-verified, NOT `unit` singular (contrast HM-2, which
  carries wflow-native values under `unit` singular — see the
  hydrological-model seam doc). `crs=4326` / `category=meteo` global attrs.
- **deliberately unpinned:** provenance attrs (`paper_*`, `source_*`, `notes`);
  chunk/encoding.
- **validator:** `validate_wg1`.

**Branch note (not fixture-verified — no chirps fixture).** The era5 branch
writes all seven variables. The **chirps** branch writes `precip` from
chirps-native data and reprojects era5 `temp`/radiation/`press_msl` onto the
chirps grid; the chirps orography sidecar is a chirps-only input. These
chirps-only facts are documented from code and asserted only under a chirps
fixture — tagged **not fixture-verified (no chirps fixture)** in the validator
index.

**Units note (grounded — corrects the p32a °C assumption; design §5.2).** WG-1
`temp*` is in **Kelvin** (`long_name` + observed value, under the `units` plural
key): the extraction writes native era5 K. The Kelvin→°C conversion happens
inside the forcing build / downscale, so the °C value lands on the model-grid
forcing (HM-2 `temp.attrs['unit'] = 'degree C.'`, fixture-verified). **Units are
NOT pinned as a hard contract surface** on either artifact — wflow maps forcing
by variable NAME via the TOML `[input.forcing]` block (HM-2), never by the
netCDF unit attribute — so the K-vs-°C divergence is an **observed, documented
cross-seam fact**, asserted only **if the attr is present** (§5.5), not pinned as
a required property. This avoids over-constraining a swap with a property no
consumer reads while keeping the divergence honestly on the record.

## WG-2 — stress-test perturbation grid

- **path pattern:** `<collection>/stress_test_lookup.csv`, retained with the
  collection. Producer staging is under
  `scenarios/requests/<generation_request_id>/generation/config/`.
- **producer:** WF3 `prepare_stress_test_grid` and collection publication.
- **consumer:** the stochastic provider reads the scenario row's explicit
  `st_id`; reporting derives axes from the retained lookup. Simulation and
  metric identities never reconstruct membership from filenames.
- **shape:** a CSV with **header exactly**
  `st_id,month,temp_change,precip_change,precip_variance_change`, and
  **`12 × ST_NUM` rows** — twelve per member, `month ∈ 1..12`, members
  `1..ST_NUM`. The `(st_id, month)` grid is **complete and duplicate-free**, and
  rows are sorted by `(st_id, month)`.
- **semantics:** `temp_change` additive (°C); `precip_change` and
  `precip_variance_change` **percent**, not multipliers — `0.0` means no change,
  `-30.0` means a 0.7 factor. The multiplier convention survives only inside the
  generator: the R side reconstructs `1 + <col>/100` for **both** percent
  columns. The project config keeps its 12-element multiplier vectors; this is
  an artifact-unit rule, not a config-surface change.
- **precision:** the member levels are `float32` shortest-repr quantized (the
  grid the user asked for); the percent text is written at **`float64` shortest
  repr of the exact conversion**, so the reconstructed multiplier is within one
  `float64` ulp of the level. It is **not** bit-identical for every level, and
  cannot be made so — measured, 1,155 of 50,000 `float32` multipliers admit no
  `float64` percent that reconstructs them exactly under `1 + p/100`. A consumer
  may rely on the bound, not on exactness.
- **admissible multiplier domain: `multiplier ≥ 0.5`, with no upper bound.** This
  is the **precondition of the bound above**, not a caveat on it: the producer
  refuses a configuration declaring a precipitation mean or variance multiplier
  below `0.5` before the DAG is built, so every lookup this contract describes
  was written from admitted multipliers and the one-ulp bound holds over the
  whole table, unconditionally. Outside the domain it does not: at level
  `0.013596006` the specified conversion reconstructs `0.013596005999999883`,
  68 ulps out, because the percent's rounding scale stops shrinking with the
  level once `|percent|` crosses 64. There is deliberately **no ceiling** — the
  bound was measured to hold out to `1e6`, so an upper cap would refuse
  configurations the arithmetic serves correctly. A re-implementer needs the
  floor to *validate its own producer*; a consumer reading a lookup needs only
  the bound.
- **`st_id`:** the member id, **zero-padded** to a width derived from `ST_NUM`
  (C27: `01 … 12` at twelve points, unpadded below ten), **identical**
  to the scenario table stochastic block key. **Read it as a
  string** — `pd.read_csv` with no `dtype` returns `01` as `1` and every join
  silently misses. R readers pass `colClasses = c(st_id = "character")`.
  **Every `st_id` in one table has the same width**, which is what lets a
  consumer infer the join key's width from the table itself rather than needing
  `ST_NUM` passed alongside it. A table mixing widths is malformed.
- **The unperturbed scenario has NO lookup row.** The table covers members `1..ST_NUM` only. The empty scenario `st_id` is
  the reserved unperturbed baseline (naming.md §4): it has no parameters, is
  produced by generation rather than perturbation, and perturbation never runs
  for it. Its **absence is load-bearing**, not incidental — it is what makes
  "not on the surface" a structural fact rather than a convention, and an
  all-zero `st_0` row would be indistinguishable from an identity member's row
  while denoting a differently-processed climate (the raw generated series, not
  that series round-tripped through a perturbation that is not the identity at
  unit factors).
- **column vocabulary:** **closed**. A new perturbation parameter is a new
  COLUMN, and adding one requires a C28 ruling — the shape barrier is gone, the
  contract barrier is not. Refused at write time by
  `prepare_cst_parameters._KNOWN_AXES`.
- **Lifecycle:** the published lookup is retained in the collection inventory.
- **pinned surface:** the exact header and column order; the `12 × ST_NUM` row
  count with a complete, duplicate-free `(st_id, month)` grid; the
  `(st_id, month)` sort order; `st_id` as zero-padded TEXT at the scenario key's
  width, **one width for the whole table**; `st_0` ABSENT; the
  additive-vs-percent column semantics.
- **deliberately unpinned:** the numeric values themselves (they are the
  experiment), and the percent text's digit count beyond the `float64`
  shortest-repr rule.
- **validator:** `validate_wg2`.

## WG-3 — weathergenr config surface

- **path pattern:** `scenarios/requests/<generation_request_id>/generation/config/weathergen_config.yml` —
  **one file** since C29.
- **producer:** rule 3.06 `prepare_weathergen_config`
  (`blueearth_cst/experiment/prepare_weathergen_config.py`).
- **consumer:** rules 3.07 and 3.08 (both R side), which read the same file.
- **one config, not one per member (C29).** Do not reintroduce a per-member
  `weathergen_config_*.yml`: nothing in it varied except the output
  filename — split into prefix and suffix because `weathergenr::write_netcdf`
  takes them separately — and Snakemake already knew it as rule 3.08's own
  declared output, so the provider passes it to R. Its
  two `trajectory` flags moved into this file and are now pinned here. At
  RLZ_NUM=10, ST_NUM=88 the removal drops 880 YAMLs plus their logs and
  benchmark parts. The rest of what it carried — copies of the `stress_test`
  step counts and monthly min/max ranges — was never read (finding F6) and
  deliberately did **not** move: the values that perturb a run come from
  `stress_test_lookup.csv`.
- **Shape:** sections named for the current upstream functions:
  `generate_weather`, `apply_climate_perturbations`, and `write_netcdf`, plus
  `temp.transient_change` and `precip.transient_change`.
  `generate_weather.vars` is a list. The required consumed keys are pinned by
  `_WG3_SECTIONS` and `validate_wg3` in `interchange_contracts.py`.
- **pinned surface:** **the key set + types the R side reads** (derived
  read-only from `global.R` / `generate_weather.R`), NOT weathergenr's
  semantics. Upstream-spelled keys (`warm.signif.level`, `dot.case`) are
  preserved verbatim per naming.md §2 (YAML under an upstream schema).
- **temp() lifecycle:** not `temp()`.
- **deliberately unpinned:** comment layout, key order.
- **validator:** `validate_wg3`.

**Depth note (design OQ-6).** WG-3 pins the config *key set + types*, not value
*ranges* — a replacement generator may define its own config surface entirely, so
WG-3 is the *current* generator's contract, not a universal one.

## WG-4 — durable generated forcing

- **Path:** `<collection>/forcing/run_<run_id>.nc`, exactly one inventoried
  forcing artifact per scenario row, including unperturbed rows.
- **Producer:** WF3 provider generation/perturbation followed by
  `retain_scenario_forcing` and `publish_scenario_collection`.
- **Consumer:** WF4's preparation adapter. `run_id` is opaque, textual and
  zero-padded; ancestry and design keys come from `scenario_table.csv`.
- **Content:** the existing daily `(time, lat, lon)` raster with at least
  `precip` and `temp`, plus adapter-required variables. EPSG:4326 is carried
  through `spatial_ref`; global `crs`/`category` attributes are checked if
  present, not required. Effective units, calendar, endpoints and grid are
  inventoried by the forcing descriptor without rewriting native bytes.
- **Lifecycle:** durable. Temporary R staging is a producer implementation
  detail; consumers cannot delete published forcing, including unperturbed data.
- **Validation:** `validate_wg4` checks the raster subset; collection readers
  additionally verify complete membership, hashes and extracted descriptors.

## WG-5 — per-run HydroMT catalog

- **Path:** `<exp>/hydrology/wflow/config/run_<run_id>.yml`, one per evaluated run.
- **Producer/consumer:** WF4 `downscale_climate_realization`; the catalog points
  to retained collection forcing for that run.
- **Pinned emitted subset:** exactly one `run_<run_id>` entry containing `uri`,
  `driver.name: raster_xarray`, `driver.options.preprocess: harmonise_dims`,
  `driver.options.lock: false`, `metadata.crs: 4326`, `metadata.category: meteo`,
  and `data_type: RasterDataset`. HydroMT owns the schema and interpretation.
- **Lifecycle:** temporary, recreated only for preparation. Portability belongs
  to the collection's packaged preparation context, not the absolute `uri` in a
  temporary adapter catalog.
- **Validation:** `validate_wg5` validates each emitted entry;
  `validate_wg5_catalog_runs` checks the catalog map against the evaluated run
  set and requires each catalog to name its intended run only. These checks do
  not substitute for WG-4 or WG-6 content validation.

## WG-6 — prepared Wflow forcing (WF4)

- **Path:** `<exp>/hydrology/wflow/forcing/inmaps_run_<run_id>.nc`.
- **Producer:** WF4 `downscale_climate_realization`.
- **Consumer:** WF4 Wflow batches.
- **Content:** the model-grid forcing contract in [HM-2](hydrological-model-seam.md#hm-2--wflow-forcing-inmaps):
  daily `float32` `precip`, `pet`, `temp`, model grid and CRS. Preparation retains
  the existing calendar conversion, clipping and PET conventions; temporal
  records expose actual endpoints instead of silently repairing them.
- **Lifecycle:** temporary. Use the simulation runner with `-- --notemp` when
  retaining these files for an on-disk contract check.
- **Validation:** `validate_wg6`/`validate_hm2` plus the adapter's temporal record.

## Substitution and validation

A replacement generator implements the scenario-provider contract and publishes
a complete collection: scenario rows, forcing, effective descriptors, source and
environment identities, and portable preparation inputs. It must preserve
declared ancestry and scenario semantics. It does not change HydroMT or Wflow.

`blueearth_cst/shared/interchange_contracts.py` owns `validate_wg1` through
`validate_wg6` and `validate_wg5_catalog_runs`. Dataset validators accept parsed
datasets; the relational catalog validator requires the independent evaluated
run set. A missing temporary artifact is an unavailable check, not a pass.

```console
snakemake all -c 3 -s generate_scenarios.smk --configfile <project-config.yml>
python scripts/simulate_system.py --config <project-config.yml> --target all --cores 3 -- --notemp
```

Historical ERA5 captures and bounded source-branch preservation evidence are
recorded in [P2 acceptance](../../milestones/r12/implementation/evidence/p2/acceptance.md).
Those records establish their stated scope; they do not claim validation of an
arbitrary replacement generator or every possible forcing dataset.
