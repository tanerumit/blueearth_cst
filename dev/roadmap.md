# Fork Roadmap

Source of truth for the personal fork of `blueearth_cst`: milestone scope,
deliverables, exit criteria, branching/tagging conventions, commit
discipline, and deferred work. Per-milestone detail (audits, plans, drift
reports, run logs) lives under `dev/m01/`, `dev/m02/`, `dev/m02b/`, etc.
Open M3+ items live in `dev/followups.md`.

Milestones are **stacked**: each one builds on the previous tag.

```text
base/<start-point>
  └── milestone/01-replication              →  tag: m01-replication
        └── milestone/02-pixi-installation  →  tag: m02-pixi
              └── milestone/02b-library-upgrades  →  tag: m02b-upgrades
                    └── milestone/02c-tests             →  tag: m02c-tests
                          └── milestone/02d-contracts       →  tag: m02d-contracts
                                └── milestone/03-model-builder  →  tag: m03-model-builder
                                      └── milestone/04-projections →  tag: m04-projections
                                            └── milestone/05-experiment →  tag: m05-experiment
                                                  └── milestone/06-refactor →  tag: m06-refactor
```

The structure is **vertical-by-workflow**: M3, M4, M5 each take one
Snakemake workflow end-to-end (orchestration *plus* the analytical scripts
it calls). M6 then does the cross-cutting structural refactor on top.

---

## Branching and tagging conventions

What this fork actually uses. Generic git workflow guidance is out of
scope.

| Branch type   | Pattern                       | Purpose                                                               |
| ------------- | ----------------------------- | --------------------------------------------------------------------- |
| Frozen base   | `base/<start-point>`          | Historical starting point of the fork (e.g. `base/v0.1.0-alpha`).     |
| Milestone     | `milestone/<NN>-<topic>`      | Stable checkpoint per milestone (e.g. `milestone/02b-library-upgrades`). |
| Experiment    | `exp/m<NN>-<topic>`           | Messy trial branch off a milestone.                                   |
| Feature       | `feat/m<NN>-<topic>`          | Cleaner implementation off a milestone, intended to be merged in.     |
| Pull request  | `pr/<NN>-<topic>`             | Clean branch prepared for upstream review.                            |

**Tags.** One per milestone, named after the milestone topic without the
`milestone/` prefix or numeric: `m01-replication`, `m02-pixi`,
`m02b-upgrades`, `m03-model-builder`, `m04-projections`, `m05-experiment`,
`m06-refactor`. Tags are permanent rollback points; milestone branches
stay alive after their tag for late patches or PR prep.

**Stacked, not parallel.** Each milestone branches from the previous
milestone's tip (not from `base/`). M2b, M2c, and M2d are
intra-milestone variants between M2 and M3 — library upgrades, pre-M3
test coverage, and modularity contracts respectively. All land before
the workflow refactors begin so that M3-M5 inherit a stable foundation.

**Remotes.**
- `origin` — your fork (`github.com/<you>/blueearth_cst`).
- `upstream` — the original Deltares repo
  (`github.com/Deltares/blueearth_cst`).

**PRs back to upstream** go from `pr/<NN>-<topic>` branches, not directly
from milestone branches. One PR per milestone is the default; only stack
PRs when maintainers explicitly agree to review them in series. PR target
branch follows the base — work started from `v0.1.0-alpha` likely targets
a maintenance branch for that release, not `upstream/main`.

---

## M1 — Replication baseline

**Status.** Sealed 2026-05-07. Tag `m01-replication` on `9765e56`.

**Goal.** Get all three Snakemake workflows running end-to-end on the test
config, on the existing conda environment, and capture their outputs as
regression fixtures for every later milestone.

**Deliverables.**
- All three workflows complete on `config/snake_config_model_test.yml`
  (Windows). Linux / Docker replication via
  `config/snake_config_model_test_linux.yml` is **deferred** — see
  "Deferred: Linux replication" at the end of this document.
- Test-data provenance documented in one bullet at the top of
  `dev/m01/setup.md`: where the test data lives, how a fresh clone gets
  it, and any external mounts or downloads required.
- A `dev/baseline/` directory containing `manifest.json` — a fingerprint
  of every artifact declared as a `rule all` target across the three
  Snakefiles. Per-realization Wflow outputs and intermediates are not
  fingerprinted. Format defined under "Baseline fingerprint format" below.
- A script `dev/scripts/check_baseline.py` with two subcommands:
  - `record` — walk a fresh run's `rule all` targets and write
    `manifest.json`.
  - `check` — recompute fingerprints from the current run and diff against
    the committed manifest. Exits non-zero on any mismatch; prints the
    offending variable / statistic so the failure is immediately useful.
- Triage of warnings emitted during a run, classified into three buckets in
  a single `dev/m01/warnings.md`. Bucket assignment by stack-frame origin:
  1. **Upstream** — frame originates inside any `site-packages/` or
     vendored third-party path (hydromt, xarray, R packages, Julia).
     Accept.
  2. **Config / data-catalog** — warning text references a config key or
     data-catalog entry. Fix in M1 if cheap.
  3. **Our-code** — frame originates in `src/`. Fix in M1.
- Resolved env-name confusion (`cst` vs `blueearth-cst`) — pick one,
  update README + scripts to match.

**Baseline fingerprint format.** Per artifact type:

- **netCDF (`*.nc`).** Open with `xarray`. Drop volatile attributes
  (`history`, `creation_date`, `Conventions` version strings, software
  version stamps). For each variable, record
  `{shape, dtype, count_non_nan, min, max, mean, std}` rounded to **10
  significant figures**. The full per-variable record is serialized as
  sorted JSON; the manifest stores both the JSON and a SHA256 of it for
  fast diffing.
- **CSV (`*.csv`).** Normalize line endings (`\r\n` → `\n`) and trim
  trailing whitespace, then SHA256 the bytes.
- **PNG (`*.png`).** Record `{exists: true, size_bytes: <int>}`. On
  comparison, accept any size within ±10% of the recorded value. Do not
  byte-hash — matplotlib / font / anti-aliasing drift would cause false
  positives, and plots are the weakest regression signal.

The full discipline (anti-patterns, helper-script shape, tolerance rules)
lives in the `pipeline-regression-testing` skill — load it whenever you
touch `check_baseline.py` or the manifest.

**Tolerance policy.**

- *Within M1* (same machine, same env): fingerprints must match exactly.
  If they don't, the run is genuinely nondeterministic — fix the seed or
  the source of jitter before tagging M1.
- *M2 onward* (env or library change): a netCDF summary statistic that
  shifts by less than `1e-9` relative may be accepted as numerical noise,
  and the manifest is updated. Anything larger requires a written
  justification (in `dev/mNN_baseline_diffs.md`) before the manifest is
  updated.
- M3, M4, M5 are each allowed to *intentionally* change scientific output
  for their own workflow's slice of the manifest. Each milestone owns the
  diff note for its slice. Other milestones must preserve the manifest or
  document why a change is numerical noise rather than a behavioral
  regression.

**Exit criteria.**
- `pytest tests/` passes.
- Each of the three workflows runs to completion with `--keep-going` *not*
  hiding failures (i.e. all expected outputs produced).
- `check_baseline.py check` reports zero diffs against a freshly committed
  manifest on a clean re-run.
- Buckets 2 and 3 from the warnings triage are empty.

**Out of scope.**
- Eliminating bucket-1 (upstream) warnings.
- Any environment-manager change.
- Any restructuring of `src/`, configs, or data catalogs.
- Touching script behavior beyond what is needed to remove our-code warnings.

**Risks / open questions.**
- Same-machine nondeterminism. The fingerprint format already absorbs
  cosmetic noise (history attrs, plot rendering); if a *value* fingerprint
  still flickers between identical reruns, treat it as a real bug — find
  the unseeded RNG, the threading nondeterminism, or the order-dependent
  reduction and fix it before tagging.

**Tag.** `m01-replication` once exit criteria are green.

---

## M2 — Pixi env + install

**Status.** Sealed 2026-05-07. Tag `m02-pixi` on `681b06b`.

**Goal.** Replace the current conda + ad-hoc R + Julia setup with a single
declarative environment that reproduces M1 outputs. Pixi is the working
hypothesis.

**Deliverables.**
- `pixi.toml` (or replacement) covering Python, R, and Julia dependencies.
- All R packages currently installed at runtime by scripts moved into the
  declarative env. Audit needed: grep `install.packages` and
  `remotes::install_github` across `src/weathergen/`.
- `weathergenr` (the Deltares R package) handled explicitly — either pinned
  to a commit/tag in the env, or vendored, with the choice justified in a
  short note.
- README install section rewritten end-to-end. Old conda instructions
  removed, not just commented out.
- The env file is authored cross-platform (no Windows-only packages) so
  the deferred Linux work doesn't have to redo it. Actual Linux/Docker
  validation is in the deferred section.
- M1 baseline re-run on the new env produces zero diffs (subject to the
  M2-onward tolerance policy).

**Exit criteria.**
- A fresh clone + single install command (`pixi install` or equivalent)
  produces a working env on Windows without manual steps. Linux validation
  is deferred (see end of document) but the env file should be authored
  cross-platform from the start.
- `pytest tests/` passes on the new env.
- All three workflows complete and match the M1 baseline.
- No script invokes `install.packages` or any other runtime install.

**Out of scope.**
- Workflow / Snakefile changes.
- Script logic changes beyond removing runtime installs.

**Risks / open questions.**
- Pixi's R coverage via conda-forge is good but not universal — the
  weathergenr install path is the most likely blocker. Validate this
  *before* migrating; if it fails, fall back to a hybrid (pixi for
  Python+Julia, scripted R install in a single setup step).
- Julia + Wflow versions are currently pinned by the Dockerfile only —
  surface those pins in the env file too.

**Tag.** `m02-pixi`.

---

## M2b — Library upgrades

**Status.** Sealed 2026-05-08 — all three workflows validated end-to-end
on a fresh `pixi install && pixi run install` clone (Windows). Tag
`m02b-upgrades` lives on `159e197` (baseline re-record); later commits
are dev-doc refinements only.

**Goal.** Upgrade the four load-bearing libraries to current stable
versions in one disciplined pass before any workflow-level cleanup
starts. Originally absent from the roadmap; inserted between M2 and M3
because library API/behaviour drift is exactly the kind of risk that
should land *before* M3-M5 start refactoring against an aging API.

**Scope.** Four libraries:
1. **hydromt** — currently `>=0.9.4`. Latest stable line is 1.x; major
   version bump with documented API breaks.
2. **hydromt_wflow** — currently `>=0.4.1,<0.6`. Lift the cap to the
   latest stable. Schema and API changes likely.
3. **Wflow.jl** — currently `0.8.1` pinned via `Manifest.toml`. May
   change scientific output.
4. **Python stack caps** — `numpy<2`, `xarray<=2024.3.0`, `zarr<3`,
   `tabulate==0.8.10`, `python<3.12`. Lift them where the upgraded
   hydromt/hydromt_wflow allows.

**Method.** Audit-first, not iterate-first.

1. Read each library's CHANGELOG / release notes between current pin
   and latest stable. List target versions, breaking changes that
   touch this repo, and code locations that need fixing. Output:
   `dev/m02b/audit.md`.
2. Bump versions in `pixi.toml` (refresh `pixi.lock`) and
   `Project.toml` (refresh `Manifest.toml`).
3. Apply the code fixes the audit identified.
4. Force-rerun all three workflows on the upgraded env.
5. Re-baseline `dev/baseline/manifest.json` against the new outputs.
   Document drift in `dev/m02b/baseline_diffs.md` per target →
   variable → statistic where notable. The new manifest is the
   contract for M3 onward.

**Drift policy.** Aggressive re-baseline. Any drift > 1e-9 from the
M1 baseline is *expected* — this milestone explicitly changes
scientific output. Document what shifted and by how much in the
diffs note; don't gate the milestone on understanding each one. M3,
M4, M5 then preserve the M2b baseline within their own slice or
own a documented diff for it.

**Exit criteria.**
- Fresh `pixi install && pixi run install` produces a working env on
  Windows with the bumped versions.
- All three workflows complete end-to-end on the upgraded env.
- `pytest tests/` exits 0 (preserved from M2 — 13 passed + 2 xfailed).
- `dev/baseline/manifest.json` re-recorded; `check_baseline.py check`
  reports zero diffs against itself (re-run determinism preserved).
- `dev/m02b/audit.md` and `dev/m02b/baseline_diffs.md` checked in.

**Out of scope.**
- Snakefile/workflow logic refactoring (M3, M4, M5).
- Repo-wide directory restructuring (M6).
- Lifting the deferred Linux/Docker validation (still deferred).

**Risks / open questions.**
- hydromt 0.x → 1.x is a documented breaking transition. The audit
  may surface enough breakage to suggest doing hydromt as one minor
  bump at a time rather than 0.9 → 1.x in one shot. Decision lands in
  the audit.
- Wflow.jl behaviour changes can shift discharge time series in ways
  that look like real signal. Not a regression; just a new baseline.
- Python<3.12 cap exists for a reason (likely a transitive dep);
  audit should identify it before we lift naively.

**Tag.** `m02b-upgrades`.

---

## M2c — Test coverage (pre-M3)

**Status.** Sealed 2026-05-08 — four new test files (32 new passing tests,
2 strict xfails for documented bugs). Suite total: 45 passed, 4 xfailed.

**Goal.** Establish unit-test infrastructure and convert documented bugs
into regression coverage before M3-M5 begin refactoring workflow scripts.
Inserted between M2b and M3 because writing tests for code about to be
refactored is wasted effort, but writing tests for *stable utilities*
that M3-M5 will depend on is not — and the resulting test pattern gives
M3-M5 a template to follow rather than re-inventing fixtures and mocking
in each milestone.

**Scope.** Five small, stable modules where bugs are already documented
and that M3-M5 are unlikely to substantially rewrite:
`prepare_climate_data_catalog.py`, `extract_historical_climate.py`,
`setup_time_horizon.py`, `prepare_build_config.py`,
`metrics_definition.py`. ~520 lines of source code total.

**Approach.** Replicate `tests/test_stage_data.py` — one test file per
source module, heavy deps stubbed via `sys.modules.setdefault`, inline
fixtures per file. Bug-driven `pytest.mark.xfail(strict=True)` tests for
documented issues that aren't fixed yet (three of them: hydromt `to_yml`
preprocess strip, `extract_climate_grid` silent truncation,
`extract_climate_grid` ignored config keys).

**Exit criteria.**
- Five new test files in `tests/`, one per target module.
- `pytest tests/` passes with the three new xfails marked `strict=True`.
- All existing tests still pass.
- M02c section in `dev/roadmap.md` flipped to `**Status.** Sealed <date>`.

**Out of scope.** Plotting modules, workflow-orchestration scripts that
M3-M5 will rewrite, R weathergenr testthat (parked at M5),
coverage-percentage targets, CI workflow setup.

**Risks / open questions.**
- If `extract_historical_climate.py`'s coupling to hydromt makes the
  `sys.modules` stub impractical, fall back to a tiny real netCDF
  fixture (~1 KB) under `tests/data/`. Decision in passing.
- xfail tests starting to pass accidentally are caught by
  `strict=True` — no silent decay.

**Tag.** `m02c-tests`. Full design lives in
`dev/m02c/test-coverage-design.md`.

---

## M2d — Modularity contracts (pre-M3)

**Goal.** Establish per-workflow config contracts so workflows can be
added, disabled, or replaced in the future without touching others.
Phase 1 of modularity — formalize boundaries without restructuring
code. Inserted between M2c and M3 because M3-M5 each refactor a
workflow's Snakefile and scripts; doing those refactors against a flat
single-namespace config means each milestone has to decide on the fly
which keys belong to which workflow. Locking the contract first lets
M3-M5 inherit it.

**Scope.** Reorganize the snake config into three top-level sections
(`project`, `shared`, `workflows.<name>`); each Snakefile reads only
its own section + shared. Per-workflow contract docs at
`dev/workflows/<name>.md` document owned config keys, input/output
contracts, and downstream consumers. `enabled:` flag in each workflow
section as a forward-compat marker (documentary today; operational
when M6+ adds module composition or a wrapper script).

**Approach.** Distinguish *contracts* (cheap to formalize, last
forever) from *structure* (expensive to change, defer until needed).
M02d invests in contracts. Structure stays as-is — still 3 separate
Snakefiles, still flat `src/`, no Snakemake module composition or
plugin registry. Migration affects three config files
(`tests/snake_config_model_test.yml`,
`config/snake_config_model_test.yml`,
`config/snake_config_model_test_linux.yml`); user-local `_local.yml`
files migrate manually via the documented mapping.

**Exit criteria.**
- Three top-level config sections in place with a checked-in template
  at `config/snake_config.template.yml`.
- Three contract docs under `dev/workflows/`.
- All three Snakefiles read sectioned config; old flat reads removed.
- Three migrated config files committed.
- All workflows still run end-to-end on the migrated test config.
- `check_baseline.py check` reports zero diff (config restructure is
  organizational only, no scientific change).
- `pytest tests/` unchanged: 45 passed, 4 xfailed.

**Out of scope.** Operational `enabled:` skip behavior (deferred to M6
structural refactor); pydantic/jsonschema validation (M3+); cross-
workflow data path decoupling (M6); Linux/Docker config rewrites
(deferred per Linux replication parking lot).

**Risks / open questions.**
- A renamed key the Snakefile still reads under its old name → silent
  default → baseline drift. Mitigation: per-Snakefile commit
  boundaries with baseline check between commits; baseline manifest
  catches any output drift.
- `workflow.configfiles[0]` requires `--configfile` on the CLI. Verify
  each invocation path during implementation. (Side benefit: this also
  delivers part of M3a's "configfile mechanism" sub-item early.)

**Tag.** `m02d-contracts`. Full design lives in
`dev/m02d/modularity-contracts-design.md`.

---

## M3 — Workflow 1: model builder

**Goal.** Clean up `Snakefile_model_creation` and the scripts it calls —
orchestration *and* analytical code. Establish the cross-cutting Snakefile
patterns that M4 and M5 inherit.

**Cross-cutting deliverables (done once here, reused by M4 and M5).**
- Collapse the duplicated `get_config(config, key, default, optional)`
  helper from all three Snakefiles into one shared module at
  `src/snake_utils.py`. Update *all three* Snakefiles to import from it.
  Behavior of M4/M5's Snakefiles unchanged; only the helper sourcing moves.
- Replace the `--configfile` `sys.argv` re-parsing trick in *all three*
  Snakefiles with a cleaner mechanism (e.g. `workflow.configfiles[0]`),
  documented in `src/snake_utils.py` so the next contributor can tell why.

**Workflow-1 deliverables.**
- Any load-bearing `ruleorder:` in `Snakefile_model_creation` either
  tightened (preferred) or commented in-place with the reason.
- Per-rule `log:` and `benchmark:` directives on every non-trivial rule
  in this Snakefile.
- Resolve or properly encapsulate the "temporary hydromt fix" in
  `src/setup_reservoirs_lakes_glaciers.py` — either upstream the fix or
  isolate it with a comment that names the upstream issue and a removal
  trigger.
- Review `src/setup_gauges_and_outputs.py` for correctness, vectorization,
  and units handling.
- Add unit tests under `tests/` for the Python helpers in this workflow's
  scope (currently `tests/` is workflow-level only).

**Exit criteria.**
- `pytest tests/test_cli.py` (dry-run sanity check) still passes for all
  three Snakefiles.
- The model-creation workflow runs end-to-end and matches its slice of
  the M1 baseline — preserved, or intentionally updated with a documented
  diff in `dev/m03_baseline_diffs.md`.
- New unit tests added and passing.

**Out of scope.**
- Snakefile_climate_projections content changes (M4) — except the shared
  helper import that comes with the cross-cutting deliverables.
- Snakefile_climate_experiment content changes (M5) — same caveat.
- Repo-wide directory restructuring (M6).

**Tag.** `m03-model-builder`.

---

## M4 — Workflow 2: climate projections

**Goal.** Clean up `Snakefile_climate_projections` and the scripts it
calls. Inherit the patterns established in M3 (shared helper, configfile
mechanism, log/benchmark conventions).

**Deliverables.**
- The load-bearing `ruleorder:` directive in
  `Snakefile_climate_projections` either tightened or commented in-place
  with the reason.
- Per-rule `log:` and `benchmark:` on every non-trivial rule in this
  Snakefile.
- Review `src/get_stats_climate_proj.py` for correctness, vectorization,
  and units handling.
- Audit the `monthly_stats_hist` → `monthly_stats_fut` → `monthly_change`
  chain end-to-end for unit consistency, calendar handling, and missing-
  data behavior.
- Add unit tests for the Python helpers in this workflow's scope.

**Exit criteria.**
- `pytest tests/test_cli.py` still passes.
- The projections workflow runs end-to-end and matches its slice of the
  M1 baseline — preserved, or intentionally updated with a documented
  diff in `dev/m04_baseline_diffs.md`.
- New unit tests added and passing.

**Out of scope.**
- Workflow-1 or workflow-3 changes (other than shared helper inheritance).
- Repo-wide directory restructuring (M6).

**Tag.** `m04-projections`.

---

## M5 — Workflow 3: climate experiment

**Goal.** Clean up `Snakefile_climate_experiment` and the scripts it
calls — including the R weathergen layer. Inherit the patterns from M3.

**Deliverables.**
- Per-rule `log:` and `benchmark:` on every non-trivial rule in this
  Snakefile.
- The R weathergen pipeline (`src/weathergen/*.R`): cleaner argument
  parsing, fewer positional args, consistent logging. Migration to the
  current weathergenr API is already done pre-M1; revisit any drift here.
- Stress-test grid construction (`ST_NUM = (temp.step_num + 1) *
  (precip.step_num + 1)`) extracted from Snakefile expressions into a
  single tested Python helper.
- Review `src/weathergen/impose_climate_change.R` and the downscaling
  rules.
- Add unit tests for Python helpers in this workflow. R testthat
  coverage is a separate decision, locked at start of M5.

**Exit criteria.**
- `pytest tests/test_cli.py` still passes.
- The experiment workflow runs end-to-end and matches its slice of the
  M1 baseline — preserved, or intentionally updated with a documented
  diff in `dev/m05_baseline_diffs.md`.
- New unit tests added and passing.

**Out of scope.**
- Workflow-1 or workflow-2 changes (other than shared helper inheritance).
- Repo-wide directory restructuring (M6).

**Tag.** `m05-experiment`.

---

## M6 — Structural refactor

**Goal.** Reorganize the repository so source code, configuration, data
catalogs, generated outputs, and documentation are cleanly separated and
discoverable. M3/M4/M5 already cleaned up *within* each workflow; M6 sets
the cross-cutting layout.

**Concrete pain points to address (lock list at start of M6).**
1. `src/` is flat — split into a package (`blueearth_cst/`) with submodules
   per workflow stage (model, projections, experiment, weathergen).
2. `config/` mixes canonical example configs with local / test variants and
   data catalogs. Split into `config/workflows/`, `config/catalogs/`, and
   keep `*_local.yml` patterns gitignored.
3. `dev/` and `docs/` boundaries — confirm conventions. `dev/` =
   planning, audits, and dev helpers (`dev/scripts/`); `docs/` =
   user-facing reference. Decide whether dev helpers stay under
   `dev/scripts/` or whether a top-level `scripts/` is introduced for
   production runners.
4. Data catalogs: OS-specific variants already collapsed in deferred
   Linux work, but the directory layout under `config/catalogs/` should
   be settled here.
5. Output layout under `project_dir/` already mostly clean — leave alone
   unless a concrete pain point emerges.
6. Remaining top-level runners (`run_snake_test.cmd`,
   `run_snake_docker.sh`) folded into `dev/scripts/` (consistent with
   the pre-M1 move of `open_shell.bat`) or split into a new top-level
   `scripts/` if you decide production runners deserve a separate home.

**Exit criteria.**
- New layout documented in an updated CLAUDE.md and README.
- All three workflows still run and match the M5 baseline.
- `pytest tests/` passes.
- A `MIGRATION.md` (or section in the changelog) maps every moved file
  from old → new path so downstream forks can rebase.

**Out of scope.**
- Any further behavioral change.

**Tag.** `m06-refactor`.

---

## Cross-cutting principles

- **Every milestone ends with a tag.** Tags are the rollback points.
- **Every milestone preserves the M1 baseline** unless it is *intentionally*
  changing behavior. M3, M4, M5 are each allowed to change their own
  workflow's slice of the manifest — with a documented diff. M2 and M6
  must preserve, modulo the M2-onward `1e-9` numerical-noise tolerance.
- **Manifest updates are part of the merge.** Each milestone updates
  `dev/baseline/manifest.json` if (and only if) changes meet that
  milestone's tolerance / justification rules. No silent updates.
- **No milestone touches the next milestone's territory.** If you find
  yourself wanting to fix a workflow-2 issue while in M3, write it down
  in `dev/m04_followups.md` and keep going.
- **PRs back to upstream** (if any) are prepared from `pr/<NN>-<topic>`
  branches per the existing fork workflow guide — not from milestone
  branches directly.

---

## Commit strategy

Branch and tag naming live in "Branching and tagging conventions" above.
This section covers commit messages only.

**Subject format.** `m<NN>: <imperative subject, ≤72 chars>`. `m<NN>`
matches the milestone the commit belongs to. Examples:

- `m01: record baseline manifest for test config`
- `m02: replace environment.yml with pixi.toml`
- `m03: collapse get_config into src/snake_utils.py`
- `m04: fix calendar handling in get_stats_climate_proj.py`
- `m05: extract stress-test grid into tested helper`

**Body.** Optional. Include only when the *why* isn't obvious from the
diff. Wrap at ~72 chars. Don't restate what the diff shows.

**Granularity.** One logical change per commit. If the subject needs
the word "and", split it.

**Pre-M1 / cross-cutting work.** Use `chore: <subject>` for repo
housekeeping that doesn't belong to any milestone (adding this roadmap,
`.gitignore` updates, fixing typos in unrelated docs). Once M1 starts,
prefer `m01:` over `chore:` whenever the commit touches M1 territory.

**Never commit.**
- Outputs under `project_dir/`.
- Files matching `*_local.yml` or other local-only configs.
- Secrets, credentials, large binary fixtures.
- Generated baselines other than `dev/baseline/manifest.json` itself.

If any of these slip in, update `.gitignore` first, then remove from
history if the commit hasn't been pushed.

**Merges and tags.** Default merge-commit messages are fine — don't
hand-craft them. Tag messages should restate the milestone goal in one
line (e.g. `m03-model-builder: model creation workflow + scripts cleaned`).

---

## Minor open items

Small decisions that don't justify a section of their own. Resolve in
passing as the relevant milestone starts.

- **Env name.** Pick `cst` or `blueearth-cst`. Decision lands in M1.
- **CI.** No GitHub Actions today. `check_baseline.py` is a natural fit
  once it exists. Deferred alongside the Linux work.
- **Wflow.jl pinning under pixi.** Needs a 1-hour spike at the start of
  M2 to confirm pixi can manage Julia + Wflow together; if not, fall back
  to a hybrid (pixi for Python+R, Project.toml for Julia).
- **R testthat coverage.** Decided at the start of M5 — Python helpers
  only by default; adding R testing infrastructure is a separate call.
- **`channel_priority: strict` in `environment.yml`.** Currently silently
  ignored by conda (not a valid env-file key). Either drop the line as a
  `chore:` cleanup or move the setting to `.condarc`. M2 makes the
  question moot.

---

## Deferred: Linux replication

Currently parked because no Linux machine is available locally. Not
abandoned — to be picked up when a Linux box, WSL setup, or Deltares
P-drive mount becomes available.

**What this covers when reactivated.**
- Reproducing the M1 baseline on Linux using
  `config/snake_config_model_test_linux.yml`.
- Rebuilding the Docker image on top of the M2 env manager and validating
  `run_snake_docker.sh`.
- Confirming the M2 env file resolves cleanly on Linux (it was authored
  cross-platform during M2).
- Sorting out the Deltares P-drive mount (`/mnt/p/wflow_global/hydromt`):
  whether the baseline is captured natively or only inside the container.
- Collapsing the OS-specific data catalog split (`*_linux.yml`) into a
  single parameterized catalog or config selection — moved here from M3
  because it can't be validated without Linux.
- Once green, recording Linux-specific fingerprints alongside the Windows
  ones in `dev/baseline/` (separate manifest, not a replacement).

**Where it slots in.** Likely a small dedicated milestone between M2 and
M3 (e.g. `milestone/02b-linux-parity`) so M3+ can assume both platforms
work. Renumber later milestones accordingly, or keep it as a side branch
tagged `m02b-linux-parity`.

**Until then.** All milestone exit criteria refer to Windows only.
Linux-specific files (`*_linux.yml`, `run_snake_docker.sh`, the
Dockerfile) must continue to build / parse but are not exercised end-to-
end. Don't delete them.
