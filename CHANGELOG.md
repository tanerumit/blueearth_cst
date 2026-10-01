# Changelog

Personal fork of `Deltares/blueearth_cst`. Release history follows
[Keep a Changelog](https://keepachangelog.com/) loosely.

Releases follow the [manual toolbox versioning policy](dev/reference/versioning.md):
Git release tags are authoritative; milestone tags are development checkpoints.
Milestone detail lives in `dev/roadmap.md` and `dev/records/milestones/`.

## [Unreleased]

These changes summarize development since `v0.2.0-alpha`; they do not declare
another release. Historical release entries below are unchanged.

### Breaking

- Reorganized the shipped code into `blueearth_cst/`, consolidated configuration
  and project output layouts, and renamed workflow rules. Existing scripts,
  rule targets, and output consumers need migration.
- Split project configuration into a project file and per-workflow files, with
  closed workflow stanzas and shared keys owned by the project file's `basin`,
  `climate`, and `model` sections or top level. See the
  [project-config migration guide](docs/site/guide/migrating-project-config.qmd).
- Reworked projections analysis around monthly GCM series. `save_grids` became
  `save_gridded`; variable declarations now specify canonical names and change
  semantics. Missing catalog models fail at DAG construction; unavailable
  scenario/member combinations are reported as skips. See the
  [R8 migration record](dev/records/milestones/r08/migration-wf2.md).
- Separated scenario generation (WF3) from system simulation and retained-response
  metrics (WF4). Scenario collections, explicit run IDs, immutable metric sets,
  and their output contracts replace the predecessor experiment layout. Use the
  owned workflow runners described in [README.md](README.md).
- Result locations now use the registry `wflow_id`; the baseline outlet changed
  from `101` to `1010`. Consumers must use registry identifiers.

### Added

- Model-independent historical climate analysis (WF0), forcing-readiness
  reporting, model interchange contracts, and expanded practitioner documentation.
- Projection annual and monthly change-factor tables, requested-combination
  status reporting, provenance and limitation reports, and reusable series
  caching with separate fetch and reduction steps.
- Durable scenario collections with generation-code identity, simulation batch
  recovery, batching calibration, and retained-response metric validation.
- Cross-platform CI, focused validation gates, and the manual toolbox release
  policy and checklist.

### Changed

- Projection spatial means use spherical cell-area weights; annual aggregation
  uses month lengths in each model's calendar. Reduction no longer rounds to
  two decimals; default statistics are mean, median, and standard deviation,
  with labelled, opt-in tail quantiles. Figures show individual combinations.
- Scenario identity follows generation code; downstream simulation changes do
  not invalidate generation. Simulation retains one discharge series per model
  cell and stages completed batch members for reuse after interruption.

### Fixed

- Projection reference windows include the final complete hydrological year
  (`1990–2010` includes 21 years). Model calendars are read from their stores,
  and reduction-kernel identity now invalidates stale cached arithmetic.
- The unperturbed scenario now passes through the same perturbation step as
  other scenarios. In the recorded baseline, affected low-flow results decreased
  by up to about 90%; the accepted baseline was re-recorded on 2026-09-25.
  See [AGENTS.md](AGENTS.md) for baseline configuration and provenance.
- Restored workflow log and benchmark gathering, corrected checkpoint lookups,
  and repaired Windows console capture during simulation preparation.

## [v0.2.0-alpha] — 2026-05-09

Foundation phase sealed; Phase 2 (workflow refactor) designed and
ready to execute. Substantial change since `v0.1.0-alpha` — minor
version bump reflects breaking library upgrades plus structural and
testing additions that make Phase 2 possible.

### Phase 1 (Foundation, sealed)

- **M01 — Replication baseline** (`m01-replication`): all three
  Snakemake workflows replicated end-to-end on the test config;
  baseline manifest at `dev/baseline/manifest.json`;
  `dev/scripts/check_baseline.py` with `record` / `check` subcommands.
- **M02 — Pixi env** (`m02-pixi`): pixi-driven Python + R + Julia env
  replacing conda + ad-hoc setup. Single declarative `pixi.toml`.
- **M02b — Library upgrades** (`m02b-upgrades`): hydromt 0.x → 1.3,
  hydromt_wflow 0.x → 1.0.2, Wflow.jl 0.7 → 1.0.2, Python stack caps
  lifted (numpy 2.x, xarray latest). Baseline re-recorded under the
  "intentional drift, document deltas" policy.
- **M02c — Test coverage** (`m02c-tests`): 32 new unit tests across 4
  `src/` modules plus 2 strict xfails for documented bugs (hydromt
  `to_yml` preprocess strip; `extract_climate_grid` silent truncation).
  Established the `sys.modules.setdefault` mocking pattern.

### Phase 2 (Refactor) — designed, not yet executed

- **R1 design** (`dev/records/milestones/r01/`): per-workflow modularity contracts.
  Sectioned config schema (`project` / `shared` / `workflows.<name>`),
  per-workflow contract docs, atomic migration plan including
  `src/` script updates and baseline-snapshot policy.
- **R2 design** (`dev/records/milestones/r02/`): prescriptive naming conventions style
  guide (snake_case, lowercase acronyms, `_path` canonical, suffix
  vocabulary split between paths and data objects, domain-identifier
  escape hatch, "do not rename without migration note" surfaces).

### Toolchain

- **Python 3.12 → 3.14.4**. The deprecated `Path(fn, resolve_path=True)`
  kwarg in `src/prepare_climate_data_catalog.py` was fixed (closes
  R3 followup early as prep for the cap bump).
- **Snakemake stays at 9.6.2**. Bump to 9.20 deferred — snakemake 9.7+
  requires `packaging<26` but the conda env pulls in `packaging==26.2`
  via another dep. Likely fixed in snakemake 9.21+.
- `datrie` pin removed (was redundant; modern snakemake doesn't need it
  as a hard conda dep).

### Repo structure

- Roadmap restructured into Phase 1 (sealed) / Phase 2 (active)
  sections with clear visual break.
- `dev/records/milestones/phase-1/{m01,m02,m02b,m02c}/` for sealed foundation milestones.
- `dev/records/milestones/r01/`, `dev/records/milestones/r02/` for active Phase 2 milestones.
- `dev/reference/` reserved for R2 output.
- Stale forward-looking M3-M6 references renamed to R3-R6 across docs,
  tests, and code comments.
- New tag prefix convention: `r##-<topic>` for Phase 2 (e.g.
  `r03-model-builder`); `m##-<topic>` preserved for sealed Phase 1.

### Testing

- Suite total: 45 passed, 4 xfailed. Unchanged through the entire
  toolchain bump and repo restructure (validates that the moves and
  text updates don't affect runtime behavior).

### Documentation

- README updated to reflect fork status, Python 3.14, Julia 1.11.x via
  juliaup, deferred Docker, and pointers to `dev/install.md` and
  `dev/roadmap.md`.
- New `CHANGELOG.md` (this file).

### Known issues / followups

- Test `xfail`s tracked in `dev/tasks/`:
  - hydromt `to_yml` preprocess strip — upstream hydromt issue.
  - `extract_climate_grid` silent truncation when staged source < requested window — fix in R3.
- Snakemake bump to 9.20 deferred until upstream relaxes the
  `packaging<26` constraint.
- Linux / Docker validation deferred (see "Deferred: Linux replication"
  in `dev/roadmap.md`).

## [v0.1.0-alpha] — base

Upstream starting point. Forked from `Deltares/blueearth_cst` at this
version. Branch `base/v0.1.0-alpha` preserves the exact starting
commit. All Phase 1 work in this fork builds on top of this baseline.
