# Naming Conventions Review

**Date.** 2026-05-09.

**Status.** Blocked: the requested source docs under `dev/conventions/`
are not present in this working tree.

## What I checked

- Listed `dev/conventions` recursively.
- Listed the repository files with `rg --files`.
- Searched `dev/`, `docs/`, `CLAUDE.md`, and `README.rst` for naming /
  identifier / filename convention references.

No files under `dev/conventions/` were found. The only convention material
currently visible is incidental:

- `dev/roadmap.md` has branch, tag, and commit-message conventions.
- `dev/m02c/test-coverage-design.md` and plan mention test file naming.
- `dev/followups.md` tracks an unresolved outlet station naming decision.
- HydroMT docs under `docs/` describe upstream data and architecture
  conventions, not this repo's prescriptive style guide.

## Review checklist for the missing guide

When `dev/conventions/` is available, review it against these repo-specific
surfaces.

### Repository files

- Root Snakefiles: current names are `Snakefile_model_creation`,
  `Snakefile_climate_projections`, `Snakefile_climate_experiment`.
- Python source files under `src/`: currently mostly verb-noun snake_case,
  e.g. `prepare_climate_data_catalog.py`, `setup_time_horizon.py`.
- R source files under `src/weathergen/`: currently snake_case verbs,
  e.g. `generate_weather.R`, `impose_climate_change.R`.
- Tests: currently `tests/test_<module>.py`.
- Dev milestone docs: currently `dev/m02d/modularity-contracts-design.md`,
  `dev/m02d/modularity-contracts-plan.md`, etc.
- Config files: currently mixed by workflow, catalog, platform, and example
  role under `config/`.

### Identifier classes

- Python functions and variables should consistently distinguish paths
  (`*_path` vs current mixed `*_fn`, `*_fid`, `*_file`).
- Snakemake wildcards should settle on short stable names such as `model`,
  `scenario`, `horizon`, `rlz`, `st`.
- Config keys should align with M02d's ownership model:
  `project.*`, `shared.*`, and `workflows.<name>.*`.
- Domain identifiers should preserve established external names where they
  are API contracts, e.g. Wflow variables, HydroMT catalog keys, CMIP model
  IDs, and R package function names.
- Acronyms need an explicit rule: either lowercase in Python identifiers
  (`rlz_num`, `st_num`) or preserved only when matching external interfaces.

### High-risk decisions to inspect

- Whether to rename existing files during M3-M6 or only apply the guide to
  new code until the structural refactor.
- Whether user-facing output filenames are allowed to change. They are part
  of the baseline and downstream user contract, so they need migration notes
  if renamed.
- Whether copied config snapshots and data catalog keys are governed by the
  guide. Some names are consumed by HydroMT/Wflow and should not be
  normalized just for local style.
- Whether the guide distinguishes code-internal identifiers from scientific
  variable names. Forcing names like `precip`, `temp`, `Qstats`, and
  Wflow/CSDMS names have scientific or upstream meaning.

## Preliminary suggestions

Until the guide is visible, I would avoid repo-wide renames. Use the guide
first as a contract for M3-M5 refactors, then do bulk file/module moves in
M6 when the roadmap already expects structural churn and migration mapping.

The guide should include an explicit "do not rename without migration note"
section for:

- `rule all` output filenames.
- Config keys in checked-in example configs.
- Data catalog source names.
- Wflow / HydroMT / CMIP / weathergenr external identifiers.
- Test fixture paths referenced by `tests/conftest.py` or baseline scripts.

## Needed input

Add or point me to the actual `dev/conventions/` files, then I can review
the guide itself and replace this blocker note with a substantive critique.

