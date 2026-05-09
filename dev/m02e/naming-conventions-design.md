# M02e — Naming conventions (pre-M3) — design

**Date.** 2026-05-09.

## Goal

Single prescriptive style guide for naming identifiers and files
across the repo, delivered as `dev/conventions/naming.md`. Pure docs
addition. **No code refactoring in M2e** — existing names are
grandfathered. M3+ apply the conventions when touching code; M6 may
do bulk file moves under the structural-refactor milestone.

The intent is: when a future workflow, agent, or contributor adds new
identifiers, the style guide tells them what to choose without re-
arguing the convention each time.

## Why now (and why before M3)

M3-M5 each refactor a workflow's scripts and add new identifiers
along the way (helper functions in `snake_utils.py`, new fixtures,
new wildcards, new config keys under M02d's sectioned schema). Doing
those refactors against an undocumented convention means each
milestone has to re-decide naming on the fly — and the decisions
accumulate inconsistently. Locking the convention first lets M3-M5
inherit it.

This doc does not refactor existing names. It is the contract for
*new* code from M3 onward.

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
   them. M2e itself produces zero code diffs.

## Decisions baked in (from brainstorming)

| Topic                          | Decision                                                                |
| ------------------------------ | ----------------------------------------------------------------------- |
| Voice                          | `MUST` / `SHOULD` / `MAY`                                               |
| Universal case                 | snake_case for variables, functions, modules, files                     |
| Acronyms in identifiers        | Always lowercase (`cmip6_models`, `era5_orography`, `csdms_name`)       |
| True constants                 | `UPPER_SNAKE_CASE` (`RLZ_NUM`, `ST_NUM`, `DATA_SOURCES`)                |
| Python                         | PEP 8: snake_case, PascalCase classes, UPPER constants                  |
| R                              | snake_case (not `dot.case`); aligns with tidyverse + weathergenr        |
| Snakemake rule names           | snake_case; verb_noun for action rules; noun-only acceptable for `rule all` |
| YAML keys                      | snake_case throughout                                                   |
| File names                     | snake_case for `.py` and `.R`; exceptions: `Snakefile_*`, `CLAUDE.md`, `README.*`, `Dockerfile`, `LICENSE` |
| Path-identifier suffix         | `_path` is canonical for new code; `_fn`, `_fid`, `_file` deprecated    |

## Style guide outline (`dev/conventions/naming.md`)

The guide itself gets authored during M2e execution. Section list:

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

**YAML**: snake_case keys. Group under M02d sections: `project`,
`shared`, `workflows.<name>`.

### 3. Path-identifier suffix (`_path` canonical)

New code MUST use `_path` for variables holding file path strings:
`region_path`, `forcing_path`, `csv_path`. Deprecated suffixes still
present in the codebase (`_fn`, `_fid`, `_file`) are grandfathered;
do not rename existing usages without a migration note.

Document why `_path` was chosen: explicit, language-neutral, matches
Python's pathlib convention.

### 4. Snakemake wildcards (stable vocabulary)

Wildcards used across Snakefiles MUST come from this list:

| Wildcard      | Meaning                                          |
| ------------- | ------------------------------------------------ |
| `model`       | climate model id (CMIP6 model name)              |
| `scenario`    | climate scenario (`historical`, `ssp245`, ...)   |
| `horizon`     | future horizon name (`near`, `far`)              |
| `rlz_num`     | weather realization number (1..RLZ_NUM)          |
| `st_num`      | stress test combination number (0..ST_NUM)       |

Adding a new wildcard requires updating `dev/conventions/naming.md`
in the same commit.

### 5. Established suffix vocabulary

| Suffix   | Meaning                            | Example                                   |
| -------- | ---------------------------------- | ----------------------------------------- |
| `_dir`   | directory path                     | `project_dir`, `basin_dir`, `exp_dir`     |
| `_path`  | file path (canonical)              | `region_path`, `forcing_path`             |
| `_nc`    | netCDF file path / dataset object  | `climate_nc`, `rlz_nc`                    |
| `_csv`   | CSV file path / DataFrame          | `st_csv`, `Qstats.csv`                    |
| `_yml`   | YAML file path / dict              | `weagen_config_yml`                       |
| `_png`   | PNG file path                      | `output_png`, `precip_plt`                |
| `_cfg`   | config dict (M02d sectioned)       | `project_cfg`, `shared_cfg`, `my_cfg`     |
| `_fn`    | DEPRECATED. Use `_path`            | (`region_fn`, `csv_fn` — grandfathered)   |
| `_fid`   | DEPRECATED. Use `_path`            | (`gauges_fid`, `region_fid` — grandfathered) |
| `_file`  | DEPRECATED. Use `_path`            | (`csv_file` — grandfathered)              |

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

## Out of scope (what M2e does not deliver)

- Branch / commit / PR conventions (already in `dev/roadmap.md`).
- Output path conventions inside `project_dir` (in M02d workflow
  contract docs).
- Refactoring existing names to conform — explicitly grandfathered.
- Linter or CI enforcement — manual review for now. A future linter
  is a possible M3+ followup.
- Per-language style guides (e.g., function-length limits, comment
  conventions). Future `dev/conventions/python-style.md`,
  `dev/conventions/r-style.md` if needed.

## Verification

- `dev/conventions/naming.md` exists and is < 250 lines.
- `CLAUDE.md` has a one-line pointer to the naming doc.
- `pixi run pytest tests/` unchanged (no behavior change).
- No code files modified in M2e.

## Migration notes for existing names

M2e writes the contract; it does not enforce it on existing code.
M3-M5 may opportunistically rename when refactoring nearby code.
M6 (structural refactor) may do bulk file / module moves with a
`MIGRATION.md` mapping per the existing roadmap.

The deprecated path suffixes (`_fn`, `_fid`, `_file`) are the most
visible non-conformance. The roadmap entry for M3 should note that
incidental renames from these to `_path` are acceptable under M3's
"shared helper" deliverable when touching the affected code.

## Risks and open questions

- **Style guide rot**: prescriptive guides drift if not enforced.
  Mitigation: M3-M5 commit messages reference `dev/conventions/
  naming.md` when adding new identifiers. A future linter would
  catch drift mechanically; defer until needed.
- **Domain-identifier boundary**: section 6's list will grow as new
  upstream tools enter scope (e.g., adding a different climate model
  family). Keep the list living; M3-M5 update it as new external
  identifiers appear.
- **Wildcard vocabulary growth**: section 4's table is small today.
  Future workflows may need new wildcards (e.g., a `member` wildcard
  for ensemble members). The "update naming.md in the same commit"
  rule keeps this honest.

## Tag

`m02e-naming`. Sequenced after M02d seals (branch
`milestone/02e-naming` off `m02d-contracts` tag).

## Estimated commits (~3)

1. `m02e: open naming-conventions milestone with design spec`
2. `m02e: add dev/conventions/naming.md + CLAUDE.md pointer`
3. `m02e: mark milestone sealed in roadmap` (+ tag `m02e-naming`)

## Reference

- User review at `dev/conventions-review.md` (pre-design feedback;
  surfaced sections 4, 6, 7 above plus the path-suffix decision).
- M02d sectioned config schema: `dev/m02d/modularity-contracts-design.md`.
