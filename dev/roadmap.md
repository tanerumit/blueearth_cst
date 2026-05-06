# Fork Roadmap

Milestone plan for the personal fork of `blueearth_cst`. Branching mechanics
(base / milestone / exp / feat / pr layout, tagging, PR-back strategy) live
in `fork_milestone_experiment_workflow_guidance.md` — this document only
covers *what* each milestone delivers, not *how* the branches are arranged.

Milestones are **stacked**: each one builds on the previous tag.

```text
base/<start-point>
  └── milestone/01-replication-baseline   →  tag: m01-replication
        └── milestone/02-environment       →  tag: m02-environment
              └── milestone/03-orchestration →  tag: m03-orchestration
                    └── milestone/04-scripts  →  tag: m04-scripts
                          └── milestone/05-refactor →  tag: m05-refactor
```

---

## M1 — Replication baseline

**Goal.** Get all three Snakemake workflows running end-to-end on the test
config, on the existing conda environment, and capture their outputs as
regression fixtures for every later milestone.

**Deliverables.**
- All three workflows complete on `config/snake_config_model_test.yml`
  (Windows). Linux / Docker replication via
  `config/snake_config_model_test_linux.yml` is **deferred** — see
  "Deferred: Linux replication" at the end of this document.
- Test-data provenance documented in one bullet at the top of
  `dev/m01_setup.md`: where the test data lives, how a fresh clone gets
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
  a single `dev/m01_warnings.md`. Bucket assignment by stack-frame origin:
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

**Tolerance policy.**

- *Within M1* (same machine, same env): fingerprints must match exactly.
  If they don't, the run is genuinely nondeterministic — fix the seed or
  the source of jitter before tagging M1.
- *M2 onward* (env or library change): a netCDF summary statistic that
  shifts by less than `1e-9` relative may be accepted as numerical noise,
  and the manifest is updated. Anything larger requires a written
  justification (in `dev/mNN_baseline_diffs.md`) before the manifest is
  updated.
- Only M4 is allowed to *intentionally* change scientific output. Other
  milestones must preserve the manifest or document why a change is
  numerical noise rather than a behavioral regression.

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

## M2 — Environment & install

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

**Tag.** `m02-environment`.

---

## M3 — Workflow orchestration

**Goal.** Clean up the Snakemake layer — remove duplication and load-
bearing tricks — without changing what the underlying scripts do.

**Deliverables.**
- The duplicated `get_config(config, key, default, optional)` helper
  collapsed into one shared module at `src/snake_utils.py`, imported by
  all three Snakefiles.
- The `--configfile` re-parsing trick (Snakefiles re-read `sys.argv` to
  pass the config path to R scripts) replaced with a cleaner mechanism
  (e.g. `workflow.configfiles[0]`) and documented.
- The load-bearing `ruleorder:` directive in
  `Snakefile_climate_projections` either removed (by tightening wildcard
  patterns) or commented in-place with the reason it must stay.
- Per-rule `log:` and `benchmark:` directives on every non-trivial rule.

**Exit criteria.**
- `pytest tests/test_cli.py` (the dry-run sanity check) still passes for
  all three Snakefiles.
- Full M1 baseline re-run produces zero diffs.

**Out of scope.**
- Behavioral changes to scripts. Signature / arg changes are allowed where
  M3 deliverables require them, but scientific output must not change.
- Schema validation, DAG image commits, and OS-specific catalog dedup —
  considered and dropped as gold-plating. Catalog dedup belongs with the
  deferred Linux work; the others can be revisited later if needed.
- Any package / directory restructuring (M5).

**Tag.** `m03-orchestration`.

---

## M4 — Script improvements

**Goal.** Improve the analytical code itself — model building, climate
projection processing, stress-test design and execution — now that the
workflow scaffolding is reliable.

**Deliverables (scope to be locked at start of M4).** Candidates:
- The `setup_reservoirs_lakes_glaciers.py` "temporary hydromt fix"
  resolved upstream or properly encapsulated.
- `src/get_stats_climate_proj.py` reviewed for correctness, vectorization,
  and units handling.
- The R weathergen pipeline: cleaner argument parsing, fewer positional
  args, consistent logging.
- Stress-test grid construction (`ST_NUM = (temp.step_num + 1) *
  (precip.step_num + 1)`) extracted into a single tested helper instead of
  living in Snakefile expressions.
- Unit tests for the Python helpers under `src/`. Currently `tests/` is
  almost entirely workflow-level; add module-level coverage for the
  non-trivial pure functions.

**Exit criteria.**
- New unit tests added and passing.
- Where M4 changes the *intended* output (e.g. a corrected formula),
  the M1 baseline is updated *deliberately*, with a documented diff and
  rationale in `dev/m04_baseline_diffs.md`. Where M4 is meant to be
  behavior-preserving, the baseline still matches.

**Out of scope.**
- Repo-wide directory restructuring (deferred to M5).
- Any change to the orchestration layer (locked by M3).

**Tag.** `m04-scripts`.

---

## M5 — Structural refactor

**Goal.** Reorganize the repository so that source code, configuration,
data catalogs, generated outputs, and documentation are cleanly separated
and discoverable.

**Concrete pain points to address (lock list at start of M5).**
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
4. Data catalogs: OS-specific variants already collapsed in M3, but the
   directory layout under `config/catalogs/` should be settled here.
5. Output layout under `project_dir/` already mostly clean — leave alone
   unless a concrete pain point emerges.
6. Remaining top-level runners (`run_snake_test.cmd`,
   `run_snake_docker.sh`) folded into `dev/scripts/` (consistent with
   the pre-M1 move of `open_shell.bat`) or split into a new top-level
   `scripts/` if you decide production runners deserve a separate home.

**Exit criteria.**
- New layout documented in an updated CLAUDE.md and README.
- All three workflows still run and match the M4 baseline.
- `pytest tests/` passes.
- A `MIGRATION.md` (or section in the changelog) maps every moved file from
  old → new path so downstream forks can rebase.

**Out of scope.**
- Any further behavioral change.

**Tag.** `m05-refactor`.

---

## Cross-cutting principles

- **Every milestone ends with a tag.** Tags are the rollback points.
- **Every milestone preserves the M1 baseline** unless it is *intentionally*
  changing behavior (only M4 is allowed to). Where it changes, the diff
  is documented, not hidden.
- **Manifest updates are part of the merge.** Each milestone updates
  `dev/baseline/manifest.json` if (and only if) changes meet that
  milestone's tolerance / justification rules. No silent updates.
- **No milestone touches the next milestone's territory.** If you find
  yourself wanting to fix env issues during M3, write it down in
  `dev/m02_followups.md` and keep going.
- **PRs back to upstream** (if any) are prepared from `pr/<NN>-<topic>`
  branches per the existing fork workflow guide — not from milestone
  branches directly.

---

## Commit strategy

Branch and tag naming live in `fork_milestone_experiment_workflow_guidance.md`.
This section covers commit messages only.

**Subject format.** `m<NN>: <imperative subject, ≤72 chars>`. `m<NN>`
matches the milestone the commit belongs to. Examples:

- `m01: record baseline manifest for test config`
- `m02: replace environment.yml with pixi.toml`
- `m03: collapse get_config into src/snake_utils.py`
- `m04: fix off-by-one in stress-test grid expansion`

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
line (e.g. `m01-replication: workflows green on Windows test config`).

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
- **Unit-test scope in M4.** Python helpers only by default. R/Julia
  testing infrastructure is a separate decision, locked at M4 start.

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
M3 (e.g. `milestone/02b-linux-parity`) so that M3+ can assume both
platforms work. Renumber later milestones accordingly, or keep it as a
side branch tagged `m02b-linux-parity`.

**Until then.** All milestone exit criteria refer to Windows only.
Linux-specific files (`*_linux.yml`, `run_snake_docker.sh`, the
Dockerfile) must continue to build / parse but are not exercised end-to-
end. Don't delete them.
