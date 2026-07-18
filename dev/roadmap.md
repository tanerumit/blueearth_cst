# Fork Roadmap

Source of truth for the personal fork of `blueearth_cst`. Two phases:

**Phase 1 — Foundation (sealed 2026-05-08).** Replicated upstream,
formalized the pixi env, upgraded load-bearing libraries, and added
unit-test coverage. Four milestones, all tagged. Phase 1 dev artifacts
under `dev/phase-1/`.

**Phase 2 — Refactor (active).** Major overhaul of the workflow code,
config contracts, and repo structure. Six milestones running from R1
(modularity contracts) through R6 (structural refactor), in deliberate
single-purpose steps. Phase 2 dev artifacts under `dev/r##/`.

```text
Phase 1 — Foundation (sealed)
  base/<start-point>
  └── milestone/01-replication              →  tag: m01-replication
        └── milestone/02-pixi-installation  →  tag: m02-pixi
              └── milestone/02b-library-upgrades  →  tag: m02b-upgrades
                    └── milestone/02c-tests             →  tag: m02c-tests

Phase 2 — Refactor (active, branches from m02c-tests)
                          └── milestone/r01-contracts        →  tag: r01-contracts
                                └── milestone/r02-naming        →  tag: r02-naming
                                      └── milestone/r03-model-builder  →  tag: r03-model-builder
                                            └── milestone/r04-projections →  tag: r04-projections
                                                  └── milestone/r05-experiment →  tag: r05-experiment
                                                        └── milestone/r06-refactor →  tag: r06-refactor
```

Phase 2 is **vertical-by-workflow**: R3, R4, R5 each take one Snakemake
workflow end-to-end (orchestration plus the analytical scripts it
calls). R6 then does the cross-cutting structural refactor on top.

---

## Branching and tagging conventions

| Branch type   | Pattern                       | Purpose                                                                  |
| ------------- | ----------------------------- | ------------------------------------------------------------------------ |
| Frozen base   | `base/<start-point>`          | Historical starting point of the fork (e.g. `base/v0.1.0-alpha`).        |
| Phase 1 milestone | `milestone/<NN>-<topic>`  | Sealed; pattern preserved on existing branches (`milestone/02c-tests`).  |
| Phase 2 milestone | `milestone/r<NN>-<topic>` | Active; example `milestone/r01-contracts`, `milestone/r03-model-builder`. |
| Experiment    | `exp/r<NN>-<topic>`           | Messy trial branch off a Phase 2 milestone.                              |
| Feature       | `feat/r<NN>-<topic>`          | Cleaner implementation off a Phase 2 milestone, intended to be merged in. |
| Pull request  | `pr/<NN>-<topic>`             | Clean branch prepared for upstream review.                               |

**Tags.** Phase 1 tags use `m##-<topic>` and stay frozen
(`m01-replication`, `m02-pixi`, `m02b-upgrades`, `m02c-tests`). Phase 2
tags use `r##-<topic>` (`r01-contracts`, `r02-naming`,
`r03-model-builder`, `r04-projections`, `r05-experiment`,
`r06-refactor`). Tags are permanent rollback points; milestone branches
stay alive after their tag for late patches or PR prep.

**Stacked, not parallel.** Each milestone branches from the previous
milestone's tip (not from `base/`). Phase 2 starts from the
`m02c-tests` tag. R1, R2 are pre-workflow contracts and conventions
that R3-R5 inherit; R6 is the cross-cutting structural refactor.

**Remotes.**
- `origin` — your fork (`github.com/tanerumit/blueearth_cst`).
- `upstream` — the original Deltares repo
  (`github.com/Deltares/blueearth_cst`), fetch-only.

The branch `upstream-deltares` (formerly `main`) freezes the upstream
Deltares state the fork tracked at renaming time; never commit to it.
`main` is the moving trunk and the GitHub default branch.

**PRs back to upstream** go from `pr/<NN>-<topic>` branches, not
directly from milestone branches. One PR per milestone is the default;
only stack PRs when maintainers explicitly agree to review them in
series.

---

## Phase 1 — Foundation (summary)

Sealed 2026-05-08. All artifacts under `dev/phase-1/`; baseline
manifest at `dev/baseline/manifest.json`. The detailed scope and exit
criteria for each Phase 1 milestone live in the corresponding sealed
commits and `dev/phase-1/<milestone>/` docs; this section is a
reference summary only.

### M01 — Replication baseline (sealed 2026-05-07; tag `m01-replication`)

Got all three Snakemake workflows running end-to-end on the test
config and recorded baseline output fingerprints. Established the
fingerprint format (per-variable summary stats for netCDF; normalized
SHA256 for CSV/YAML; size-only for PNG with ±10% tolerance). Built
`dev/scripts/check_baseline.py` with `record` / `check` subcommands.
Artifacts: `dev/phase-1/m01/setup.md`, `dev/phase-1/m01/warnings.md`,
`dev/baseline/manifest.json`.

### M02 — Pixi env + install (sealed 2026-05-07; tag `m02-pixi`)

Replaced the conda + ad-hoc R + Julia setup with a single declarative
`pixi.toml`. weathergenr handled separately via `pixi run install` due
to a Mingw-w64 byte-compile issue with conda r-base on Windows.
Wflow.jl + Julia 1.11.x via juliaup outside pixi (conda-forge has no
win-64 Julia build). Artifacts: `dev/phase-1/m02/decisions.md`,
`pixi.toml`, `pixi.lock`.

### M02b — Library upgrades (sealed 2026-05-07; tag `m02b-upgrades`)

Bumped four load-bearing libraries: hydromt 0.x → 1.3, hydromt_wflow
0.x → 1.0, Wflow.jl 0.7 → 1.0.2, plus lifted Python stack caps
(numpy 2.x, xarray latest, python 3.12). Re-baselined the manifest
under the "intentional drift, document deltas" policy. Artifacts:
`dev/phase-1/m02b/audit.md`, `dev/phase-1/m02b/baseline_diffs.md`,
`dev/phase-1/m02b/handoff.md`.

### M02c — Test coverage (sealed 2026-05-08; tag `m02c-tests`)

Added unit-test coverage for four small, stable `src/` modules
(`metrics_definition`, `setup_time_horizon`,
`prepare_climate_data_catalog`, `extract_historical_climate`) with two
strict xfails for documented bugs. Established the
`sys.modules.setdefault` mocking pattern that R3-R5 inherit. Suite
state: 45 passed, 4 xfailed. Artifacts:
`dev/phase-1/m02c/test-coverage-design.md`,
`dev/phase-1/m02c/test-coverage-plan.md`.

---

## Phase 2 — Refactor (active)

Goal of Phase 2: clean up workflow internals, scripts, and config
contracts so the pipeline is maintainable and extensible. Six
milestones; deliberate pace; each milestone has a single coherent
purpose. R1 and R2 establish contracts that R3-R5 inherit; R3-R5 do
the actual workflow cleanup; R6 is the cross-cutting structural
refactor.

### R1 — Modularity contracts (sealed 2026-07-18)

**Status.** Sealed 2026-07-18 — three top-level config sections in place;
all 3 Snakefiles + 4 `src/` scripts + conftest + all three integration
tests read sectioned config; config path via `workflow.configfiles[0]`;
migration guide for user-local configs at
`dev/r01/local-config-migration.md`. Per-workflow contract docs deferred
to R3/R4/R5 (2026-07-17 amendment). Suite: 51 passed, 3 skipped, 2 xfailed
(the pre-R01 47 plus 4 focused R01 reader/normalization tests). Scientific
invariance established **by construction** (value-preservation on every
migrated leaf + identity-preserving list/string normalization + green
suite + clean dry-runs), **not** by a manifest re-record: Task 5 found the
M2b `dev/baseline/manifest.json` stale (recorded from an untracked 3-model
config while the canonical uses 8; plus model-independent drift), so it is
left untouched and a clean rebuild is deferred. Full rationale + evidence:
`dev/r01/baseline_diffs.md`.

**Goal.** Establish per-workflow config contracts so workflows can be
added, disabled, or replaced in the future without touching others.
Phase 2's foundation: formalize ownership boundaries before R3-R5
each refactor a workflow. Otherwise each refactor has to decide on
the fly which keys belong to which workflow, and the decisions
accumulate inconsistently.

**Scope.** Reorganize the snake config into three top-level sections
(`project`, `shared`, `workflows.<name>`); each Snakefile reads only
its own section + shared. The contract-doc *format* is specified in
the R1 design doc (§4); the per-workflow docs themselves are deferred
to R3–R5 (see amendment note below). `enabled:` flag in each workflow
section as a forward-compat marker (documentary today; operational
when R6 adds module composition or a wrapper script).

> **Amended 2026-07-17.** The three per-workflow contract docs
> (`dev/workflows/<name>.md`) are moved out of R1: each is written as
> the opening act of the milestone that refactors that workflow
> (R3 → model_creation, R4 → climate_projections, R5 →
> climate_experiment). Rationale: a contract doc written when its
> workflow is freshly in focus is better-informed, and R1 shrinks to
> mostly mechanical config migration.

**Approach.** Distinguish *contracts* (cheap to formalize, last
forever) from *structure* (expensive to change, defer until needed).
R1 invests in contracts. Structure stays as-is — still 3 separate
Snakefiles, still flat `src/`, no Snakemake module composition or
plugin registry.

**Exit criteria.**
- Three top-level config sections in place with a checked-in template
  at `config/snake_config.template.yml`.
- All three Snakefiles read sectioned config; old flat reads removed.
- `src/` scripts that read config directly (`prepare_cst_parameters`,
  `prepare_weagen_config`, `get_change_climate_proj`,
  `get_change_climate_proj_summary`) migrated.
- Three migrated config files committed (`tests/`, canonical, Linux).
- All three workflows run end-to-end on the migrated canonical config
  (verified 2026-07-18 into `examples/test_local`).
- Scientific invariance established by construction (value-preservation
  on every migrated leaf + identity-preserving list/string normalization
  + green suite + clean dry-runs). The planned manifest re-record was
  **not** performed: Task 5 exposed that the M2b
  `dev/baseline/manifest.json` is stale (recorded from an untracked
  3-model config while the canonical uses 8; plus model-independent
  drift), so it is left untouched and a clean rebuild is deferred to a
  dedicated task. Full rationale + evidence: `dev/r01/baseline_diffs.md`.
- `pytest tests/`: 51 passed, 3 skipped, 2 xfailed (the pre-R01 47 plus
  4 focused R01 reader/normalization tests; no pre-existing test changes
  outcome).

**Out of scope.** Per-workflow contract docs (deferred to the opening
act of R3/R4/R5, per the 2026-07-17 amendment above); operational
`enabled:` skip behavior (R6); pydantic / jsonschema validation;
cross-workflow data path decoupling (R6); Linux/Docker config rewrites
(deferred per Linux replication parking lot).

**Risks / open questions.**
- A renamed key the Snakefile still reads under its old name → silent
  default → baseline drift. Mitigation: per-Snakefile commit
  boundaries with dry-run between commits; baseline manifest catches
  any output drift.
- `workflow.configfiles[0]` requires `--configfile` on the CLI.
  Verify each invocation path during implementation. (Side benefit:
  this also delivers part of R3's "configfile mechanism" sub-item
  early — R3's roadmap entry below reflects that.)

**Tag.** `r01-contracts`. Full design lives in
`dev/r01/modularity-contracts-design.md`.

### R2 — Naming conventions (designed)

**Goal.** Single prescriptive style guide at `dev/conventions/naming.md`
for naming identifiers and files across the repo. Pure docs; no code
refactoring. R3+ apply the conventions when touching code; existing
names are grandfathered. R3-R5 add new identifiers along the way
(helper functions, fixtures, wildcards, config keys), and locking the
convention first prevents each milestone from re-deciding naming on
the fly.

**Scope.** `dev/conventions/naming.md` (< 250 lines, prescriptive
`MUST` / `SHOULD` / `MAY` voice) + a one-line pointer in `CLAUDE.md`.
Covers: universal case (snake_case, lowercase acronyms, true
constants), per-language rules (Python PEP 8, R snake_case not
dot.case, Snakemake snake_case rules, YAML snake_case keys), path-
identifier suffix (`_path` canonical; `_fn`/`_fid`/`_file` deprecated),
Snakemake wildcard vocabulary, suffix vocabulary split between paths
(`_path`) and data objects (`_ds`/`_df`/`_gdf`/`_cfg`), domain
identifiers that DO NOT get normalized (Wflow / HydroMT / CMIP /
CSDMS / weathergenr / scientific variable names), file naming by file
class (Python/R = snake_case; `dev/*.md` = kebab-case; etc.), and a
"do not rename without migration note" list.

**Timing (added 2026-07-17).** R2 is pure docs and deliberately light —
it must not become a scheduling gate. It may be drafted in parallel
with R1's tail or as R3's opening act; the only hard requirement is
that `dev/conventions/naming.md` is committed and tagged
(`r02-naming`) before R3's first *code* commit, so R3–R5 mint new
identifiers against a locked convention.

**Approach.** Prescriptive but lenient: opinionated where the codebase
is currently mixed, lenient where external conventions take
precedence. Two framings: (1) local style vs upstream contract —
local style does not apply to identifiers governed by external
systems; (2) grandfathered today, applied tomorrow — R2 itself
produces zero code diffs.

**Exit criteria.**
- `dev/conventions/naming.md` exists, < 250 lines, prescriptive.
- `CLAUDE.md` has a one-line pointer to the naming doc.
- `pixi run pytest tests/` unchanged (no behavior change).
- No code files modified in R2.

**Out of scope.** Branch / commit / PR conventions (in this roadmap);
output path conventions (in R1 contract docs); refactoring existing
names to conform (R3+); linter / CI enforcement; per-language style
guides (function lengths, comment conventions).

**Risks / open questions.**
- Style guide rot if not enforced. Mitigation: R3-R5 reference
  `dev/conventions/naming.md` in commit messages when adding new
  identifiers; future linter is a possible followup.
- Section 6 (domain identifiers) and section 4 (wildcard vocabulary)
  will grow as new tools / workflows enter scope. Doc is living.

**Tag.** `r02-naming`. Full design lives in
`dev/r02/naming-conventions-design.md`.

### R3 — Workflow 1: model builder

**Goal.** Clean up `Snakefile_model_creation` and the scripts it
calls — orchestration *and* analytical code. Establish the
cross-cutting Snakefile patterns that R4 and R5 inherit.

**Cross-cutting deliverables (done once here, reused by R4 and R5).**
- Collapse the duplicated `get_config(config, key, default, optional)`
  helper from all three Snakefiles into one shared module at
  `src/snake_utils.py`. Update all three Snakefiles to import from it.
  Behavior of R4/R5's Snakefiles unchanged; only the helper sourcing
  moves.
- ~~Replace the `--configfile` `sys.argv` re-parsing trick in all
  three Snakefiles with `workflow.configfiles[0]`.~~ **Done by R1.**

**Workflow-1 deliverables.**
- Opening act, before code changes: write
  `dev/workflows/model_creation.md` (contract doc deferred from R1;
  format in `dev/r01/modularity-contracts-design.md` §4).
- Any load-bearing `ruleorder:` in `Snakefile_model_creation` either
  tightened (preferred) or commented in-place with the reason.
- Per-rule `log:` and `benchmark:` directives on every non-trivial
  rule in this Snakefile.
- Resolve or properly encapsulate the "temporary hydromt fix" in
  `src/setup_reservoirs_lakes_glaciers.py` — either upstream the fix
  or isolate it with a comment that names the upstream issue and a
  removal trigger.
- Review `src/setup_gauges_and_outputs.py` for correctness,
  vectorization, and units handling.
- Add unit tests under `tests/` for the Python helpers in this
  workflow's scope.

**Exit criteria.**
- `pytest tests/test_cli.py` (dry-run sanity check) still passes for
  all three Snakefiles.
- The model-creation workflow runs end-to-end and matches its slice
  of the M1 baseline — preserved, or intentionally updated with a
  documented diff in `dev/r03/baseline_diffs.md`.
- New unit tests added and passing.
- `dev/workflows/model_creation.md` contract doc committed.

**Out of scope.**
- `Snakefile_climate_projections` content changes (R4) — except the
  shared helper import.
- `Snakefile_climate_experiment` content changes (R5) — same caveat.
- Repo-wide directory restructuring (R6).

**Tag.** `r03-model-builder`.

### R4 — Workflow 2: climate projections

**Goal.** Clean up `Snakefile_climate_projections` and the scripts it
calls. Inherit the patterns established in R3 (shared helper,
configfile mechanism, log/benchmark conventions).

**Deliverables.**
- Opening act, before code changes: write
  `dev/workflows/climate_projections.md` (contract doc deferred from
  R1; format in `dev/r01/modularity-contracts-design.md` §4).
- The load-bearing `ruleorder:` directive in
  `Snakefile_climate_projections` either tightened or commented
  in-place with the reason.
- Per-rule `log:` and `benchmark:` on every non-trivial rule in this
  Snakefile.
- Review `src/get_stats_climate_proj.py` for correctness,
  vectorization, and units handling.
- Audit the `monthly_stats_hist` → `monthly_stats_fut` →
  `monthly_change` chain end-to-end for unit consistency, calendar
  handling, and missing-data behavior.
- Add unit tests for the Python helpers in this workflow's scope.

**Exit criteria.**
- `pytest tests/test_cli.py` still passes.
- The projections workflow runs end-to-end and matches its slice of
  the M1 baseline — preserved, or intentionally updated with a
  documented diff in `dev/r04/baseline_diffs.md`.
- New unit tests added and passing.
- `dev/workflows/climate_projections.md` contract doc committed.

**Out of scope.**
- Workflow-1 or workflow-3 changes (other than shared helper
  inheritance).
- Repo-wide directory restructuring (R6).

**Tag.** `r04-projections`.

### R5 — Workflow 3: climate experiment

**Goal.** Clean up `Snakefile_climate_experiment` and the scripts it
calls — including the R weathergen layer. Inherit the patterns from
R3.

**Deliverables.**
- Opening act, before code changes: write
  `dev/workflows/climate_experiment.md` (contract doc deferred from
  R1; format in `dev/r01/modularity-contracts-design.md` §4).
- Per-rule `log:` and `benchmark:` on every non-trivial rule in this
  Snakefile.
- The R weathergen pipeline (`src/weathergen/*.R`): cleaner argument
  parsing, fewer positional args, consistent logging. Migration to
  the current weathergenr API is already done pre-M1; revisit any
  drift here.
- Stress-test grid construction (`ST_NUM = (temp.step_num + 1) *
  (precip.step_num + 1)`) extracted from Snakefile expressions into
  a single tested Python helper.
- Review `src/weathergen/impose_climate_change.R` and the
  downscaling rules.
- Add unit tests for Python helpers in this workflow. R testthat
  coverage is a separate decision, locked at start of R5.

**Exit criteria.**
- `pytest tests/test_cli.py` still passes.
- The experiment workflow runs end-to-end and matches its slice of
  the M1 baseline — preserved, or intentionally updated with a
  documented diff in `dev/r05/baseline_diffs.md`.
- New unit tests added and passing.
- `dev/workflows/climate_experiment.md` contract doc committed.

**Out of scope.**
- Workflow-1 or workflow-2 changes (other than shared helper
  inheritance).
- Repo-wide directory restructuring (R6).

**Tag.** `r05-experiment`.

### R6 — Structural refactor

**Goal.** Reorganize the repository so source code, configuration,
data catalogs, generated outputs, and documentation are cleanly
separated and discoverable. R3/R4/R5 already cleaned up *within* each
workflow; R6 sets the cross-cutting layout. R6 also operationalizes
the `enabled:` flag from R1 — workflows can be skipped from a single
config rather than by user discipline.

**Concrete pain points to address (lock list at start of R6).**
1. `src/` is flat — split into a package (`blueearth_cst/`) with
   submodules per workflow stage (model, projections, experiment,
   weathergen).
2. `config/` mixes canonical example configs with local / test
   variants and data catalogs. Split into `config/workflows/`,
   `config/catalogs/`, and keep `*_local.yml` patterns gitignored.
3. `dev/` and `docs/` boundaries — confirm conventions. `dev/` =
   planning, audits, and dev helpers (`dev/scripts/`); `docs/` =
   user-facing reference. Decide whether dev helpers stay under
   `dev/scripts/` or whether a top-level `scripts/` is introduced
   for production runners.
4. Data catalogs: OS-specific variants already collapsed in deferred
   Linux work, but the directory layout under `config/catalogs/`
   should be settled here.
5. Output layout under `project_dir/` already mostly clean — leave
   alone unless a concrete pain point emerges.
6. Remaining top-level runners (`run_snake_test.cmd`,
   `run_snake_docker.sh`) folded into `dev/scripts/` (consistent
   with the pre-M1 move of `open_shell.bat`) or split into a new
   top-level `scripts/` if you decide production runners deserve a
   separate home.
7. Operationalize `workflows.<name>.enabled` from R1 — either via
   Snakemake `module:` composition (one master Snakefile that
   conditionally includes per-workflow modules) or a wrapper script
   that orchestrates the three Snakefiles based on the flag.

**Exit criteria.**
- New layout documented in an updated CLAUDE.md and README.
- All three workflows still run and match the R5 baseline.
- `pytest tests/` passes.
- A `MIGRATION.md` (or section in the changelog) maps every moved
  file from old → new path so downstream forks can rebase.
- Setting `workflows.<name>.enabled: false` skips that workflow's
  outputs in a clean way.

**Out of scope.**
- Any further behavioral change beyond what `enabled` requires.

**Tag.** `r06-refactor`.

---

## Cross-cutting principles

- **Every milestone ends with a tag.** Tags are the rollback points.
- **Every milestone preserves the M1 baseline** unless it is
  *intentionally* changing behavior. R3, R4, R5 are each allowed to
  change their own workflow's slice of the manifest — with a
  documented diff. R1, R2, R6 must preserve, modulo numerical-noise
  tolerance.
- **Manifest updates are part of the merge.** Each milestone updates
  `dev/baseline/manifest.json` if (and only if) changes meet that
  milestone's tolerance / justification rules. No silent updates.
- **No milestone touches the next milestone's territory.** If you
  find yourself wanting to fix a workflow-2 issue while in R3, write
  it down in `dev/followups.md` (or `dev/r04/followups.md` once R4
  is open) and keep going.
- **PRs back to upstream** (if any) are prepared from
  `pr/<NN>-<topic>` branches per the existing fork workflow guide —
  not from milestone branches directly.

---

## Commit strategy

Branch and tag naming live in "Branching and tagging conventions"
above. This section covers commit messages only.

**Subject format.** `<prefix>: <imperative subject, ≤72 chars>`. The
`<prefix>` matches the milestone the commit belongs to:

- Phase 1 (sealed): `m01:`, `m02:`, `m02b:`, `m02c:` — historical
  prefix on existing commits, do not rewrite.
- Phase 2 (active): `r01:`, `r02:`, `r03:`, `r04:`, `r05:`, `r06:`.
- Repo housekeeping that doesn't belong to a milestone: `chore:`
  (e.g. updating this roadmap, `.gitignore`, fixing typos in
  unrelated docs).

Examples:

- `r01: migrate test config + 3 Snakefiles to sectioned schema`
- `r02: add dev/conventions/naming.md + CLAUDE.md pointer`
- `r03: collapse get_config into src/snake_utils.py`
- `r04: fix calendar handling in get_stats_climate_proj.py`
- `r05: extract stress-test grid into tested helper`
- `chore(dev): split roadmap into phase-1 / phase-2 sections`

**Body.** Optional. Include only when the *why* isn't obvious from
the diff. Wrap at ~72 chars. Don't restate what the diff shows.

**Granularity.** One logical change per commit. If the subject needs
the word "and", split it.

**Never commit.**
- Outputs under `project_dir/`.
- Files matching `*_local.yml` or other local-only configs.
- Secrets, credentials, large binary fixtures.
- Generated baselines other than `dev/baseline/manifest.json` itself.

If any of these slip in, update `.gitignore` first, then remove from
history if the commit hasn't been pushed.

**Merges and tags.** Default merge-commit messages are fine — don't
hand-craft them. Tag messages should restate the milestone goal in
one line (e.g. `r03-model-builder: model creation workflow + scripts
cleaned`).

---

## Minor open items

Small decisions that don't justify a section of their own. Resolve
in passing as the relevant milestone starts.

- **CI.** No GitHub Actions today. `check_baseline.py` is a natural
  fit once it exists. Deferred alongside the Linux work.
- **R testthat coverage.** Decided at the start of R5 — Python
  helpers only by default; adding R testing infrastructure is a
  separate call.
- **Linter for naming conventions.** R2 establishes the convention
  but does not enforce it. A future linter (ruff custom rule, or a
  small ad-hoc script) would mechanically catch drift. Add as an
  R3+ followup if drift becomes a real problem.

---

## Deferred: Linux replication

Currently parked because no Linux machine is available locally. Not
abandoned — to be picked up when a Linux box, WSL setup, or Deltares
P-drive mount becomes available.

**What this covers when reactivated.**
- Reproducing the M1 baseline on Linux using
  `config/snake_config_model_test_linux.yml`.
- Rebuilding the Docker image on top of the M2 env manager and
  validating `run_snake_docker.sh`.
- Confirming the M2 env file resolves cleanly on Linux (it was
  authored cross-platform during M2).
- Sorting out the Deltares P-drive mount
  (`/mnt/p/wflow_global/hydromt`): whether the baseline is captured
  natively or only inside the container.
- Collapsing the OS-specific data catalog split (`*_linux.yml`) into
  a single parameterized catalog or config selection.
- Once green, recording Linux-specific fingerprints alongside the
  Windows ones in `dev/baseline/` (separate manifest, not a
  replacement).

**Where it slots in.** Likely a small dedicated Phase 2 milestone
when picked up (`r0X-linux-parity` between two existing R milestones)
so that subsequent milestones can assume both platforms work.

**Until then.** All milestone exit criteria refer to Windows only.
Linux-specific files (`*_linux.yml`, `run_snake_docker.sh`, the
Dockerfile) must continue to build / parse but are not exercised
end-to-end. Don't delete them.
