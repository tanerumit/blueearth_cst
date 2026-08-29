Task Brief — P4: templates, `test_case` sets, and fixtures

### Context

Canonical ruleset: `AGENTS.md`. Design: `config-shape-design.md` §7, §13.
Program: `config-shape-master-brief.md`. **Depends on P3; released by Gate 3.**

- The target layout for all five files is design §7. Do not re-derive it from
  the register — §7 is the settled form.
- `config/templates/` ships four templates; WF0 has none. `C-84` adds the
  fifth.
- `disk_headroom_gb` is read by the Snakefile but appears in NO template and NO
  shipped config (`E5`). It is real and undocumented.

### Goal

Every shipped config and template is in the v2 shape, migrated BY the rewriter
rather than by hand — which makes this phase the rewriter's first real test.

### Non-goals

- Editing the rewriter (P3). If a config needs a hand-edit the rewriter cannot
  produce, that is a P3 defect — report it, do not patch around it.
- The file RENAME itself (P5).

### Allowed scope

- **Permitted:** `config/templates/**`, `test_case/*.yml`,
  `tests/snake_config_fixture.yml`, `tests/data/presplit/**`.
- **Forbidden:** `config/defaults/**`, `config/catalogs/**` (K1);
  `dev/milestones/**`; any `blueearth_cst/` module.

### Required changes (checklist)

1. Migrate all four `test_case/` sets (17 files) by running the P3 rewriter.
2. Migrate `tests/snake_config_fixture.yml` the same way.
3. Rewrite the four templates to the §7 shape, and **add the fifth**: the WF0
   template that never existed (`C-84`).
4. Add `disk_headroom_gb` to the WF3 template as a commented example with its
   unit and its relationship to
   `advanced_settings.defaults.batch_disk_headroom_fraction` (design D-7.8).
5. `_analyze_climate.yml` ships as a comment-only scaffold, and the template
   states that the file and its `config_path` stanza travel together — an empty
   file is legal, a MISSING file with `config_path` declared is a hard parse
   error (design D-7.9).
6. Template comments state, per key: what it does, its unit where `N2` applies,
   and where its default lives. **No incident history** — that is the standing
   rule for config comments.

### Validation

- Rung 1: `pytest tests/test_cli.py` — dry-runs all four entry points against
  every migrated set. This is the cheapest proof the shape parses.
- Rung 2: `pixi run test-fast`.
- Rung 3: a WF3 smoke run on `snake_config_rapid` (rapid is the config to
  WATCH EXECUTE; baseline is the config whose NUMBERS are the point).
- Rung 4 — **resolved-config equivalence across ALL FOUR sets** (design §14.3,
  finding `ext1-6`). `check_baseline` records from `snake_config_baseline`
  alone, so without this `rapid`, `baseline_linux` and `wf2_fast` have no
  numerical check whatsoever. For each set, compose the v1 and v2 documents and
  compare SEMANTICALLY at the two seams a difference would reach a number: the
  resolved value of every key a rule reads after defaults, and every
  `params:`-threaded value. Assert equality except at the declared
  non-preserving rows, which must differ in exactly the declared way. Cover the
  optional keys the sets exercise, not only the defaults.
- **Falsifier for "no config was hand-edited":** re-run the rewriter from the
  pre-migration commit and diff its output against the committed result. Any
  difference is a hand-edit, and a hand-edit means the rewriter cannot
  reproduce the migration a user will run.

### Acceptance criteria

- All 17 `test_case/` files, the fixture, and five templates are in v2 shape.
- The rewriter reproduces every one of them byte-for-byte from v1.
- `test_cli` green against every set.

### Output requirements

Report the falsifier's result explicitly — it is the only evidence that the
shipped configs and the user's migration path are the same thing.

### Task constraints

- Use `snake_config_rapid` for anything you want to watch EXECUTE. Never point
  `check_baseline.py` at the rapid tree; the baseline is recorded from
  `snake_config_baseline` and nothing else.
- Real basin data never enters this repository. `test_case/test_local` is the
  dev-only exemption.
