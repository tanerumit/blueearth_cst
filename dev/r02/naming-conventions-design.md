# R02 — Naming conventions (pre-R3) — design

**Date.** 2026-05-09.

## Goal

Single prescriptive style guide for naming identifiers and files
across the repo, delivered as `dev/conventions/naming.md`. Pure docs
addition. **No code refactoring in R2** — existing names are
grandfathered. R3+ apply the conventions when touching code; R6 may
do bulk file moves under the structural-refactor milestone.

The intent is: when a future workflow, agent, or contributor adds new
identifiers, the style guide tells them what to choose without re-
arguing the convention each time.

## Why now (and why before R3)

R3-R5 each refactor a workflow's scripts and add new identifiers
along the way (helper functions in `snake_utils.py`, new fixtures,
new wildcards, new config keys under R01's sectioned schema). Doing
those refactors against an undocumented convention means each
milestone has to re-decide naming on the fly — and the decisions
accumulate inconsistently. Locking the convention first lets R3-R5
inherit it.

This doc does not refactor existing names. It is the contract for
*new* code from R3 onward.

## Approach

Prescriptive style guide with `MUST` / `SHOULD` / `MAY` voice,
opinionated where the codebase is currently mixed and lenient where
external conventions take precedence. Two important framings:

1. **Local style vs upstream contract.** The local style guide does
   not apply to identifiers governed by external systems (Wflow
   variables, HydroMT data catalog keys, CMIP model IDs, weathergenr
   function names, CSDMS Standard Names, scientific variable names
   like `precip` / `temp` / `Qstats`). Those follow their upstream
   conventions even when they conflict with the local rules.
2. **Grandfathered today, applied tomorrow.** Existing names that
   don't conform stay as-is until the owning milestone refactors
   them. R2 itself produces zero code diffs.

## Decisions baked in (from brainstorming + R2 review)

| Topic                          | Decision                                                                |
| ------------------------------ | ----------------------------------------------------------------------- |
| Voice                          | `MUST` / `SHOULD` / `MAY`                                               |
| Universal case                 | snake_case for variables, functions, modules                            |
| Acronyms in identifiers        | Always lowercase (`cmip6_models`, `era5_orography`, `csdms_name`)       |
| True constants                 | `UPPER_SNAKE_CASE` for immutable lookups: `WFLOW_VARS`, `XDIMS`, `YDIMS`, `VOLATILE_NC_ATTRS` |
| Config-derived run settings    | lowercase snake_case for new code (`rlz_count`, `stress_test_count`, `data_sources_path`). Existing `RLZ_NUM`, `ST_NUM`, `DATA_SOURCES` grandfathered. |
| Python                         | PEP 8: snake_case, PascalCase classes, UPPER_SNAKE for true constants only |
| R                              | snake_case (not `dot.case`); aligns with tidyverse + weathergenr        |
| Snakemake rule names           | snake_case; verb_noun for action rules; noun-only acceptable for `rule all` |
| YAML keys (BlueEarth-owned)    | snake_case for BlueEarth-authored configs (snake config sections, generated catalogs) |
| YAML keys (upstream tools)     | preserve upstream spelling — e.g., weathergenr's `warm.signif.level`, HydroMT/Wflow parameter names |
| YAML booleans                  | lowercase `true` / `false` for BlueEarth-owned configs (existing `TRUE`/`FALSE` grandfathered) |
| Path-identifier suffix         | `_path` is canonical for new code; `_fn`, `_fid`, `_file` deprecated    |
| File names by class            | See "File naming by class" section below                                |

## Style guide outline (`dev/conventions/naming.md`)

The guide itself gets authored during R2 execution. Section list:

### 1. Universal rules

- snake_case for variables, functions, modules, files (MUST).
- Lowercase acronyms in identifiers (MUST).
- `UPPER_SNAKE_CASE` for true constants (MUST).
- Verbs for functions, nouns for variables / data (SHOULD).

### 2. Per-language

**Python**: PEP 8. snake_case for variables / functions / modules.
PascalCase for classes. UPPER_SNAKE_CASE for module-level constants.

**R**: snake_case (not `dot.case`). Aligns with tidyverse style guide
and the weathergenr package conventions. Verb-noun for functions
(`read_climate_data`, not `climate_data`).

**Snakemake**: rule names snake_case (MUST). Verb_noun for action
rules (`build_model`, `add_gauges`, `run_wflow`) (SHOULD). Noun-only
acceptable for non-action rules (`rule all`) (MAY).

**YAML**: snake_case keys for BlueEarth-owned configs. Group under
R01 sections: `project`, `shared`, `workflows.<name>`. Lowercase
booleans (`true` / `false`).

**YAML — upstream tool configs are exempt.** Configs consumed by
external tools preserve upstream key spelling even when it conflicts
with snake_case:

- `config/weathergen_config.yml` uses dotted keys (`warm.signif.level`,
  `warm.sample.num`, `knn.sample.num`, `evaluate.model`) per
  weathergenr conventions.
- HydroMT / Wflow build and update configs use upstream method names
  and parameter names.
- Data catalog source names and adapter fields follow HydroMT's
  schema.

These are external-API contracts; do not normalize.

### 3. Path-identifier suffix (`_path` canonical)

New code MUST use `_path` for variables holding file path strings:
`region_path`, `forcing_path`, `csv_path`. Deprecated suffixes still
present in the codebase (`_fn`, `_fid`, `_file`) are grandfathered;
do not rename existing usages without a migration note.

Document why `_path` was chosen: explicit, language-neutral, matches
Python's pathlib convention.

### 4. Snakemake wildcards (stable vocabulary)

Wildcards used across Snakefiles MUST come from this list:

| Wildcard      | Status                  | Meaning                                          |
| ------------- | ----------------------- | ------------------------------------------------ |
| `model`       | active                  | climate model id (CMIP6 model name)              |
| `scenario`    | active                  | climate scenario (`historical`, `ssp245`, ...)   |
| `horizon`     | active                  | future horizon name (`near`, `far`)              |
| `rlz_num`     | active                  | weather realization number (1..RLZ_NUM)          |
| `st_num`      | active                  | stress test combination number (0..ST_NUM)       |
| `member`      | reserved (CMIP ensemble)| ensemble member id (`r1i1p1f1`, ...). Currently config-only; will become a wildcard if ensemble per-member rules are added. |

Adding a new wildcard requires updating `dev/conventions/naming.md`
in the same commit. The current `st_num2` variant in
`Snakefile_climate_experiment` is a known inconsistency — fold into
`st_num` during R3-R5 Snakefile cleanup.

### 5. Suffix vocabulary — split paths from data objects

A suffix means EITHER a filesystem path OR a loaded object. Not both.
This is the single biggest readability improvement R3+ can make
incrementally.

**Paths (filesystem strings):**

| Suffix   | Use for                       | Example                                   |
| -------- | ----------------------------- | ----------------------------------------- |
| `_dir`   | directory path                | `project_dir`, `basin_dir`, `exp_dir`     |
| `_path`  | file path (any extension)     | `region_path`, `forcing_path`, `summary_path`, `catalog_path` |

**Loaded data objects:**

| Suffix   | Use for                       | Example                                   |
| -------- | ----------------------------- | ----------------------------------------- |
| `_ds`    | xarray Dataset                | `forcing_ds`, `change_ds`                 |
| `_df`    | pandas DataFrame              | `qstats_df`, `signature_df`               |
| `_gdf`   | geopandas GeoDataFrame        | `region_gdf`, `outlets_gdf`               |
| `_cfg`   | parsed config dict (R01)     | `project_cfg`, `shared_cfg`, `my_cfg`     |

**Snakemake input/output labels (grandfathered, not for new Python):**

| Suffix   | Status                                              | Example       |
| -------- | --------------------------------------------------- | ------------- |
| `_nc`    | Reserved for Snakemake `input:`/`output:` labels mirroring a netCDF product | `climate_nc`, `rlz_nc` |
| `_csv`   | Same, for CSV products                              | `st_csv`      |
| `_yml`   | Same, for YAML products                             | `weagen_config_yml` |
| `_png`   | Same, for PNG products                              | `output_png`, `precip_plt` |

In new Python code, prefer `_path` (for the path string) or `_ds`/`_df`
(for the loaded object) over the file-extension suffixes. The
extension suffixes are for Snakemake label hygiene only.

**Deprecated path suffixes (grandfathered; do not use in new code):**

| Suffix   | Replacement | Example of grandfathered usage              |
| -------- | ----------- | ------------------------------------------- |
| `_fn`    | `_path`     | `region_fn`, `csv_fn`                       |
| `_fid`   | `_path`     | `gauges_fid`, `region_fid`, `forcing_fid`   |
| `_file`  | `_path`     | `csv_file`                                  |

### 6. Domain identifiers — DO NOT normalize

The local style guide does NOT apply to:

- **Wflow output variables** (preserve upstream casing / phrasing,
  e.g. `actual evapotranspiration`, `groundwater recharge`).
- **HydroMT data catalog source names** (`era5`, `merit_hydro`,
  `cmip6_<model>_<scenario>_<member>`).
- **CMIP model IDs** (`NOAA-GFDL/GFDL-ESM4`, `INM/INM-CM5-0` —
  preserve hyphens, slashes, mixed case).
- **CSDMS Standard Names** (when consumed by hydromt_wflow's
  `setup_constant_pars`).
- **weathergenr R function names** (preserve upstream).
- **Scientific variable names** with cross-tool meaning: `precip`,
  `temp`, `Qstats`, `Tlow`, `Tpeak`.

Rationale: these are API contracts with external systems. Renaming
them locally breaks downstream tools or data catalog lookups.

### 7. Do not rename without migration note

The following surfaces have downstream / baseline / user contracts.
Any renaming requires a `dev/<milestone>/migration_<topic>.md` note
listing the old → new mapping:

- `rule all` output filenames (baseline manifest contract).
- Checked-in example config keys (user-facing).
- Data catalog source names in `config/*.yml` (catalog contract).
- Wflow / HydroMT / CMIP / weathergenr external identifiers.
- Test fixture paths referenced by `tests/conftest.py`,
  `dev/scripts/check_baseline.py`, or other scripts.

**Scientific abbreviations in user-facing output filenames are
allowed.** `Qstats.csv`, `Tlow`, `Tpeak`, `BFI`, return-period
`T2` / `T10` etc. are established domain vocabulary. They violate the
acronym-lowercase rule but are user-facing and well understood;
keep as-is.

### 8. File naming by class

Different file classes follow different conventions. The local style
guide does not unify these.

| File class                                  | Convention   | Examples                                                 |
| ------------------------------------------- | ------------ | -------------------------------------------------------- |
| Python modules / R scripts                  | snake_case   | `prepare_climate_data_catalog.py`, `generate_weather.R`  |
| Snakemake entry points                      | `Snakefile_<workflow>` (existing) | `Snakefile_model_creation`             |
| Markdown planning docs under `dev/`         | kebab-case   | `naming-conventions-design.md`, `modularity-contracts-plan.md` |
| Standard root-level files                   | upstream     | `CLAUDE.md`, `README.rst`, `Dockerfile`, `LICENSE`        |
| Config / data / catalog YAML                | tool contract | `snake_config_model_test.yml`, `deltares_data.yml` (rename only with migration note) |
| Generated outputs under `project_dir/`      | governed by owning workflow contract (R01) | varies                     |

The `kebab-case` rule for `dev/*.md` recognizes the dominant
convention already in use across milestone planning docs. Don't
rename existing dev docs.

### 9. Examples

Compact "instead of / use" table to anchor the rules. Keep the final
guide's table sparse so the doc stays under 250 lines.

| Instead of   | Use                       | Reason                                   |
| ------------ | ------------------------- | ---------------------------------------- |
| `config_fn`  | `config_path`             | Canonical path suffix.                   |
| `stats_nc` (when it's a path) | `stats_path` | Path/object distinction.                  |
| `stats_nc` (when it's a Dataset) | `stats_ds` | Path/object distinction.                  |
| `ST_NUM`     | `stress_test_count`       | Config-derived setting, not a true constant. |
| `RLZ_NUM`    | `rlz_count`               | Same.                                    |
| `st_num2`    | `st_num`                  | Stable wildcard vocabulary.              |
| `cmip6Models` | `cmip6_models`           | Lowercase acronym + snake_case.          |
| `TRUE` / `FALSE` (in BE-owned YAML) | `true` / `false` | Lowercase YAML booleans.            |

## Out of scope (what R2 does not deliver)

- Branch / commit / PR conventions (already in `dev/roadmap.md`).
- Output path conventions inside `project_dir` (in R01 workflow
  contract docs).
- Refactoring existing names to conform — explicitly grandfathered.
- Linter or CI enforcement — manual review for now. A future linter
  is a possible R3+ followup.
- Per-language style guides (e.g., function-length limits, comment
  conventions). Future `dev/conventions/python-style.md`,
  `dev/conventions/r-style.md` if needed.

## Verification

- `dev/conventions/naming.md` exists and is < 250 lines.
- `CLAUDE.md` has a one-line pointer to the naming doc.
- `pixi run pytest tests/` unchanged (no behavior change).
- No code files modified in R2.

## Migration notes for existing names

R2 writes the contract; it does not enforce it on existing code.
R3-R5 may opportunistically rename when refactoring nearby code.
R6 (structural refactor) may do bulk file / module moves with a
`MIGRATION.md` mapping per the existing roadmap.

The deprecated path suffixes (`_fn`, `_fid`, `_file`) are the most
visible non-conformance. The roadmap entry for R3 should note that
incidental renames from these to `_path` are acceptable under R3's
"shared helper" deliverable when touching the affected code.

## Risks and open questions

- **Style guide rot**: prescriptive guides drift if not enforced.
  Mitigation: R3-R5 commit messages reference `dev/conventions/
  naming.md` when adding new identifiers. A future linter would
  catch drift mechanically; defer until needed.
- **Domain-identifier boundary**: section 6's list will grow as new
  upstream tools enter scope (e.g., adding a different climate model
  family). Keep the list living; R3-R5 update it as new external
  identifiers appear.
- **Wildcard vocabulary growth**: section 4's table is small today.
  Future workflows may need new wildcards (e.g., a `member` wildcard
  for ensemble members). The "update naming.md in the same commit"
  rule keeps this honest.

## Tag

`r02-naming`. Sequenced after R01 seals (branch
`milestone/r02-naming` off `r01-contracts` tag).

## Estimated commits (~3)

1. `m02e: open naming-conventions milestone with design spec`
2. `m02e: add dev/conventions/naming.md + CLAUDE.md pointer`
3. `m02e: mark milestone sealed in roadmap` (+ tag `r02-naming`)

## Reference

- User review at `dev/r02/naming-conventions-review.md` (substantive
  review of the first design draft; surfaced the file-class table,
  the suffix path/object split, the YAML upstream exceptions, the
  examples table, and the lowercase-boolean policy). Supersedes the
  earlier blocker note that previously lived at
  `dev/conventions-review.md`.
- R01 sectioned config schema: `dev/r01/modularity-contracts-design.md`.

## Related but separate

- The outlet station naming decision in `dev/followups.md` (M2b
  carryover) affects output filenames and downstream interpretation.
  It's a behavioral / contract decision for R3, not a naming-guide
  decision.
