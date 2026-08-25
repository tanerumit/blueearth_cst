Task Brief — P6: migration note and documentation sweep

### Context

Canonical ruleset: `AGENTS.md`. Design: `config-shape-design.md`.
Program: `config-shape-master-brief.md`. **Runs last — it documents what P1–P5
landed.**

- AGENTS.md requires a migration note for a contract-surface rename, and R14 is
  two of them at once: every key spelling, and the file prefix.
- Precedent: `docs/migration-config-tiers.md` (R13) and
  `docs/migration-workflow-names.md` (the 2026-08-14 rename).
- **Keep configuration references current** is a standing rule: when a path,
  filename, config key or command moves, every live reference moves in the same
  commit. A stale path in a document someone reads to do their job is a defect.

### Goal

A user with a v1 project can migrate it by following one document, and no live
reference anywhere names a spelling R14 retired.

### Non-goals

- Any code or config change.
- Editing `dev/milestones/**` — sealed records stay as they are, with their
  errata recorded in the R14 documents rather than patched into them.

### Allowed scope

- **Permitted:** `docs/**`, `README.md`, `AGENTS.md`, `dev/reference/**`,
  `dev/roadmap.md`.
- **Forbidden:** `dev/milestones/**`; every module and config.

### Required changes (checklist)

1. Write the migration note: the full v1→v2 key map, the one command, the two
   non-preserving cases and what each does, and the file rename.
2. Sweep `docs/guide/configuration.qmd`, `quick-start.qmd`, `running.qmd`,
   `outputs.qmd` — each shows a `--configfile` command line.
3. Sweep `README.md` and `AGENTS.md`. **`AGENTS.md`'s Repo Map paragraph
   explains the `.gitignore` glob by name** and says "keep the `snake_config_`
   prefix on any new seed config" — that sentence is one of the occurrences
   this milestone invalidates.
4. `C-75`: sweep `docs/cst-toolbox-technical-note-2025.md` onto the
   `transient | constant` vocabulary `C-32` adopts, and correct its two
   documented defaults — the Annex's `transient` default (the code deliberately
   refuses a missing value) and its `Realizations_number: 3` (the code defaults
   to 1). Land this WITH `C-32`, not after: a note describing a config key that
   no longer exists is the stale-reference defect AGENTS.md names.
5. `dev/reference/naming.md`: `C-85` and the `N1`–`N8` policy discharge the
   grandfathering that file records. Update it.

### Validation

- Rung 1: the stale-spelling sweep from P3, green across `docs/`, `README.md`,
  `AGENTS.md`, `dev/reference/`.
- Rung 2: `pytest tests/test_sealed_records.py` — proves the sweep did not
  reach `dev/milestones/**`.
- **Falsifier for "no live reference is stale":** grep each retired spelling
  (`snake_config`, `shared.`, `clim_historical`, `horizontime_climate`,
  `run_historical`, `stress_test:`, `reporting:`, `step_num`,
  `transient_change`, `realizations_num`, `historical_year_range`,
  `future_horizons`, `gauge_points`, `static_dir`) across tracked files outside
  `dev/milestones/**`. Any hit that is not inside a migration note's
  before/after table is a defect.

### Acceptance criteria

- The migration note covers every register row a user's config can contain.
- The falsifier grep is clean.
- The technical note's trajectory vocabulary matches `C-32`.

### Output requirements

List every file touched and, for the technical note, quote the before/after of
the two corrected defaults.

### Task constraints

- Documentation is concise and close to the code. No generic tutorial material.
- Errata against sealed milestone records are recorded in the R14 documents,
  never patched into the record itself.
