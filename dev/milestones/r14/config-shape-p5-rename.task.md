Task Brief — P5: the `snake_config_` → `project_config_` rename (`C-85`)

### Context

Canonical ruleset: `AGENTS.md`. Design: `config-shape-design.md` §12.
Program: `config-shape-master-brief.md`. **Depends on P4; released by Gate 1's
breadth ruling and gated at Gate 4.**

- Snakemake is one tool this repo happens to use; the file configures the
  PROJECT. `project_config_` says what the file is, `snake_config_` says which
  program reads it — the less durable fact. This is `N5` applied to a filename.
- Measured 2026-08-24 by `git grep -o` over tracked files outside `dev/`:
  **301 occurrences across 76 files**. The 2026-08-19 figure was 221/68 —
  stale by a third in five days.
- Implementation reference, including the full file-by-file checklist:
  `dev/tasks/t2608191733a-rename-snake-config-yml-to-project-config-yml-repo-wide.md`.

### Goal

One atomic rename of the file prefix and every identifier derived from it, with
the seeds still tracked afterwards.

### Non-goals

- Any content change to a config file (P4 did that).
- Sweeping `dev/milestones/**`.

### Allowed scope

- **Permitted:** `.gitignore`, `config/templates/**`, `test_case/*.yml`,
  `tests/**`, `pixi.toml`, `scripts/**`, the four `*.smk`, `blueearth_cst/**`
  comment and docstring references, `docs/**`, `README.md`, `AGENTS.md`,
  `dev/reference/**`, `dev/working/**`, `dev/LOG.md`.
- **Forbidden:** `dev/milestones/**` — sealed records, frozen by
  `tests/test_sealed_records.py`. They hold the large majority of occurrences
  and renaming there rewrites history to match a later convention.

### Required changes (checklist)

1. **Re-measure first.** The counts above are five days old and already known
   to drift. `git grep -c 'snake_config' -- ':!dev/milestones'`.
2. Rename the 11 tracked files (`git mv`).
3. Move the `.gitignore` un-ignore glob in the SAME commit:
   `!test_case/snake_config_*.yml` → `!test_case/project_config_*.yml`.
4. Rename every DERIVED identifier — `snake_config_fixture` →
   `project_config_fixture`, and equivalents across the 33 test modules
   (breadth ruled at Gate 1, design D-12.1).
5. Update `pixi.toml` tasks, `scripts/run_snake_test.cmd`,
   `scripts/run_snake_docker.sh`, `scripts/run_workflows.py`,
   `scripts/suggest_experiment_name.py`.
6. **Grep first, triage second.** Prose describing "the snake config" in a
   sentence is rewritten only where it names a path or an identifier.

### Commit plan

A bare `git mv` breaks every reference the instant it lands, and the glob's
failure mode is SILENT.

| subject | paths | invariant preserved |
|---|---|---|
| **one atomic commit**: `git mv` + `.gitignore` glob + every reference rewrite | all permitted paths | the seeds stay TRACKED, and no commit exists in which a reference points at a moved file |

There is no staged landing here. A transitional shim is not available — a
gitignore glob cannot match two prefixes without re-admitting files the ignore
exists to exclude.

### Validation

- **Falsifier for "the seeds are still tracked", and it is the whole point of
  Gate 4:** `git ls-files test_case/` must list every renamed seed. Run it
  BEFORE committing. **Do not use `git status`** — it is the command that lies
  here: it reports the old paths as deleted and never lists the new ones, so a
  silently-untracked rename looks like a clean rename.
- Rung 1: `pytest tests/test_cli.py`.
- Rung 2: `pytest tests/test_sealed_records.py` — proves `dev/milestones/**`
  was not swept.
- Rung 3: `pixi run test-fast`.
- Rung 4: the stale-spelling sweep from P3, which must now be GREEN on
  `snake_config` outside `dev/milestones/**`.

### Acceptance criteria

- `git ls-files test_case/` lists every renamed seed.
- `tests/test_sealed_records.py` green.
- No occurrence of `snake_config` outside `dev/milestones/**` and sealed
  records.
- The three `docs/notebooks/*.ipynb` carry banner SHAs — editing them may
  re-open `t2608132100`. Report if so rather than silently re-rendering.

### Output requirements

Paste the `git ls-files test_case/` output at Gate 4, before the commit exists.

### Task constraints

- One commit. If it is too large to review, that is the cost of the glob's
  failure mode, not a reason to split it.
- Never sweep `dev/milestones/**`.
