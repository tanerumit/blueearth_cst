Task Brief — P7: the one independently landable row (`C-83`)

### Context

Canonical ruleset: `AGENTS.md`. Design: `config-shape-design.md` §11.3.
Program: `config-shape-master-brief.md`.

ONE register row is non-breaking under every outcome and touches no config key,
so it does not need the bundle and may land before, during or after it.

**`C-35` was the other, and it is WITHDRAWN 2026-08-25.** Its de-duplication was
already done on 2026-08-13: `metrics_definition.py` does not exist, and the
constant is single-sourced as `DEFAULT_WATER_YEAR_ANCHOR` in
`snake_utils.py:1203`. Do not go looking for `DEFAULT_ANCHOR` — the only hit in
the tree is a comment recording its own replacement.

### Goal

Land `C-83` without touching the migration.

### Non-goals

- Any config key, any template, any `test_case/` file.
- The `snake_config_` prefix (that is `C-85`, P5 — a different rename).

### Allowed scope

- **Permitted:** `blueearth_cst/**`, `tests/**`, `run_stress_test.smk`,
  `config/defaults/weathergen_config.yml` **comments only**,
  `dev/reference/**`, `dev/roadmap.md`, `dev/working/**`, `dev/LOG.md`.
- **Forbidden:** `dev/milestones/**`; any config KEY (K1 — a comment
  mentioning `weagen` may be reworded, a key may not be renamed).

### Required changes (checklist)

**`C-83` — `weagen` → `weathergen` across the LIVE surface.**
`dev/reference/naming.md:176` already names `weagen` as an ad-hoc contraction
that is not an established abbreviation; the code is merely grandfathered, and
R14 is the migration note that discharges it. The inconsistency is visible on
one line: `run_stress_test.smk:965`, where the rule `prepare_weathergen_config`
runs the script `prepare_weagen_config.py`.

Scope, live surface only:

| target | what |
|---|---|
| `blueearth_cst/experiment/prepare_weagen_config.py` | the module FILE, plus `build_weagen_config` |
| `tests/test_prepare_weagen_config.py` | the test file |
| `run_stress_test.smk` | the `weagen_config` input/output name in rules 3.10, 3.11, 3.12 and the two R command lines |
| `blueearth_cst/weathergen/{generate_weather,impose_climate_change}.R` | the argument name |
| `downscale_climate_forcing.py`, `shared/interchange_contracts.py`, `config/defaults/weathergen_config.yml`, the rapid configs | comment and docstring references |
| `dev/reference/**`, `dev/roadmap.md`, `dev/working/**`, `dev/LOG.md` | live reference prose |

**NOT swept: `dev/milestones/**`** — historical records, holding the large
majority of the 210 occurrences.

`proj`, named in the same sentence of `naming.md`, is **not** swept here. A
general sweep needs its own scoping and should be boarded.

### Commit plan

`C-83` is a module rename: the import breaks the instant the file moves.

| subject | paths | invariant preserved |
|---|---|---|
| `C-83` atomic: `git mv` the module and test + rewrite every import, rule name and R argument | `blueearth_cst/`, `tests/`, `run_stress_test.smk`, `*.R` | no commit exists in which an import names a moved module |

### Validation

- Rung 1: the tests covering each changed module.
- Rung 2: `pytest tests/test_cli.py` — the rule input/output rename touches
  three rules, so the DAG must still build.
- Rung 3: `pixi run test-fast`.
- **Falsifier for "`C-83` changes no config key":** `git diff` must show no
  change to any YAML key NAME. A comment or a value may move; a key may not.
  If one does, `C-83` has become a bundle row and must stop.

### Acceptance criteria

- No `weagen` outside `dev/milestones/**`.
- `test-fast` green, and the diff touches no config key name.

### Output requirements

State which rung caught what, and confirm the `C-83` falsifier explicitly.

### Task constraints

- These rows must stay independent of the bundle. If either acquires a
  dependency on a migration row, stop and report — that dependency is the
  defect, not the sequencing.
