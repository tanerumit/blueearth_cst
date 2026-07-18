# Naming conventions

Prescriptive style guide for naming identifiers and files in
`blueearth_cst`. `MUST` / `SHOULD` / `MAY` carry their usual normative
weight.

**Grandfathered today, applied tomorrow.** This guide governs *new* code
from R3 onward. Existing non-conforming names stay as-is until the
milestone that owns them refactors them — do not rename an identifier
just to conform. Renaming a *contract* surface (§7) needs a migration
note.

**Local style yields to external / established contracts.** Identifiers
governed by an upstream tool or an established BlueEarth contract follow
those contracts, not the rules here — see §6.

## 1. Universal rules

- snake_case for variables, functions, and modules (MUST). File names
  are governed by class — see §8, not this rule.
- Lowercase acronyms inside identifiers (MUST): `cmip6_models`,
  `era5_orography`, `csdms_name` — never `CMIP6Models`.
- `UPPER_SNAKE_CASE` only for true constants — fixed, non-config-derived
  values or lookup tables that are not reassigned or mutated at runtime
  (MUST). Config-derived run settings are lowercase (§9).
- Verbs for functions, nouns for variables and data (SHOULD).

## 2. Per language

**Python** — PEP 8: snake_case variables / functions / modules;
PascalCase classes; `UPPER_SNAKE_CASE` for module-level true constants
only.

**R** — snake_case, not `dot.case` (aligns with tidyverse and the
weathergenr package). Verb-noun functions (`read_climate_data`, not
`climate_data`).

**Snakemake** — rule names snake_case (MUST); `verb_noun` for action
rules (`build_model`, `add_gauges`, `run_wflow`) (SHOULD); noun-only is
acceptable for non-action rules like `rule all` (MAY).

**YAML** — discriminate by the *consuming contract*, never authorship or
whether the file is checked in vs. generated:

- BlueEarth-owned configs consumed locally — the R01 `project` /
  `shared` / `workflows.<name>` snake config — use snake_case keys and
  lowercase booleans `true` / `false` (MUST for new keys).
- Any YAML consumed under an upstream schema preserves the upstream
  spelling (MUST), **even when BlueEarth generates the file**:
  weathergenr (`warm.signif.level`), HydroMT / Wflow parameter names,
  and HydroMT data catalogs.

Existing `TRUE` / `FALSE` in BlueEarth configs are grandfathered.

## 3. Path-identifier suffix (`_path` canonical)

New code MUST use `_path` for a variable holding a file-path string:
`region_path`, `forcing_path`, `csv_path`. `_path` is explicit,
language-neutral, and works naturally with `pathlib.Path`. The deprecated
suffixes `_fn`, `_fid`, `_file` are grandfathered — do not use them in
new code, and rename an existing one only with a migration note.

## 4. Snakemake wildcards (stable vocabulary)

Wildcards used across Snakefiles MUST come from this list. Adding a new
wildcard requires updating this file in the same commit.

| Wildcard   | Status                   | Meaning                                                                 |
| ---------- | ------------------------ | ----------------------------------------------------------------------- |
| `model`    | active                   | climate model id (CMIP6 model name)                                     |
| `scenario` | active                   | climate scenario (`historical`, `ssp245`, …)                            |
| `horizon`  | active                   | future horizon name (`near`, `far`)                                     |
| `rlz_num`  | active                   | weather realization number (`1..rlz_count`)                             |
| `st_num`   | active                   | stress-test combination: `1..stress_test_count` perturbed; `0` = reserved unperturbed baseline (`cst_0`), run through Wflow only when `run_historical` sets `ST_START = 0` |
| `member`   | reserved (CMIP ensemble) | ensemble member id (`r1i1p1f1`, …). Config-only today; becomes a wildcard if per-member rules are added |

The `st_num2` variant in `Snakefile_climate_experiment` (it admits `0`
under `run_historical`, where `st_num` starts at `1`) is a known
inconsistency — fold into `st_num` during **R5** Snakefile cleanup (that
Snakefile is R5 territory).

## 5. Suffix vocabulary — path vs. object

A suffix means EITHER a filesystem path OR a loaded object, never both.
This is the single biggest readability win R3+ can make incrementally.

**Paths:** `_dir` (directory path — `project_dir`, `basin_dir`),
`_path` (file path, any extension — `region_path`, `catalog_path`).

**Loaded objects:** `_ds` (xarray Dataset), `_df` (pandas DataFrame),
`_gdf` (GeoDataFrame), `_cfg` (parsed config dict). `project_cfg`,
`shared_cfg`, and `my_cfg` are the blessed R01 idiom — `my_cfg` for a
Snakefile's own `workflows.<name>` section, uniform across all three
Snakefiles; use it, don't invent a per-workflow variant.

**Extension suffixes** (`_nc`, `_csv`, `_yml`, `_png`) are reserved for
Snakemake `input:` / `output:` labels that mirror a file product
(`climate_nc`, `st_csv`, `weathergen_config_yml`, `output_png`). New
Python code uses `_path` (the string) or `_ds` / `_df` (the object)
instead. Existing non-conforming labels (e.g. `precip_plt`) are
grandfathered.

**Deprecated path suffixes** (grandfathered; do not use in new code):
`_fn`, `_fid`, `_file` → `_path`.

## 6. Domain identifiers — three tiers

Domain identifiers carry different kinds of contract, so treat them in
three tiers rather than one flat "external" bucket. None are normalized
casually.

**Tier 1 — opaque upstream identifiers. Preserve verbatim; no local
rename path, not even a migration note.**

- Wflow / CSDMS variable names consumed by hydromt_wflow (e.g.
  `land_surface__evapotranspiration_volume_flux` in `setup_constant_pars`).
- HydroMT data-catalog *schema* — adapter fields and structure.
- CMIP model IDs (`NOAA-GFDL/GFDL-ESM4`, `INM/INM-CM5-0` — keep hyphens,
  slashes, mixed case).
- weathergenr R function names.

**Tier 2 — established BlueEarth contracts. Grandfather; rename only with
a migration note (§7).**

- User-facing output / config names: `Qstats`, `Tlow`, `Tpeak`.
- HydroMT data-catalog *source names* (`era5`, `merit_hydro`,
  `cmip6_<model>_<scenario>_<member>`) — BlueEarth-minted lookup keys
  that form a catalog-lookup contract. (Their schema is tier 1.)
- User-facing Wflow output *labels* mapped to CSDMS names in
  `setup_gauges_and_outputs.py` (`actual evapotranspiration`,
  `groundwater recharge`) — display names, not the upstream IDs.
- Cross-tool scientific variable names: `precip`, `temp`.

**Tier 3 — new locally owned scientific identifiers.** Follow local
style (§1) unless an explicit external schema dictates a spelling.

## 7. Rename only with a migration note

Renaming any of these requires a `dev/<milestone>/migration_<topic>.md`
note listing the old → new mapping:

- `rule all` output filenames (baseline manifest contract).
- Checked-in example config keys (user-facing).
- HydroMT data-catalog source names in `config/*.yml` (§6 tier 2).
- Test fixture paths read by `tests/conftest.py`,
  `dev/scripts/check_baseline.py`, or other scripts.

Tier-1 identifiers (§6) are not renameable at all, so they are omitted
here.

**Scientific abbreviations in user-facing output filenames are allowed**
even though they break the acronym-lowercase rule: `Qstats.csv`, `Tlow`,
`Tpeak`, return-period `T2` / `T10`, `BFI`. These are established domain
vocabulary; keep them.

## 8. File naming by class

Different file classes follow different conventions; this guide does not
unify them.

| File class                             | Convention                        | Examples                                             |
| -------------------------------------- | --------------------------------- | ---------------------------------------------------- |
| Python modules / R scripts             | snake_case                        | `prepare_climate_data_catalog.py`, `generate_weather.R` |
| Snakemake entry points                 | `Snakefile_<workflow>` (existing) | `Snakefile_model_creation`                           |
| Markdown planning docs under `dev/`    | kebab-case                        | `naming-conventions-design.md`                       |
| Standard root-level files              | upstream                          | `CLAUDE.md`, `README.rst`, `Dockerfile`, `LICENSE`   |
| Config / data / catalog YAML           | tool contract                     | `snake_config_model_test.yml`, `deltares_data.yml`   |
| Generated outputs under `project_dir/` | owning workflow contract (R01)    | varies                                               |

Don't rename existing `dev/` docs.

## 9. Examples

> **Illustrative future targets only.** This is not a rename list —
> existing identifiers are grandfathered until their owning milestone
> touches them.

| Instead of                          | Use                 | Reason                                       |
| ----------------------------------- | ------------------- | -------------------------------------------- |
| `config_fn`                         | `config_path`       | Canonical path suffix.                        |
| `stats_nc` (a path)                 | `stats_path`        | Path / object distinction.                    |
| `stats_nc` (a Dataset)              | `stats_ds`          | Path / object distinction.                    |
| `ST_NUM`                            | `stress_test_count` | Config-derived setting, not a true constant.  |
| `RLZ_NUM`                           | `rlz_count`         | Same.                                         |
| `st_num2`                           | `st_num`            | Stable wildcard vocabulary.                   |
| `cmip6Models`                       | `cmip6_models`      | Lowercase acronym + snake_case.               |
| `TRUE` / `FALSE` (BlueEarth YAML)   | `true` / `false`    | Lowercase YAML booleans.                      |
