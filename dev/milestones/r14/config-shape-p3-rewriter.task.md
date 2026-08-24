Task Brief — P3: the v1→v2 rewriter

### Context

Canonical ruleset: `AGENTS.md`. Design: `config-shape-design.md` §11.
Program: `config-shape-master-brief.md`.

- The register (`config-shape-scoping.md`, `C-01`..`C-85`) is the mapping. It
  is DATA, not code — the rewriter is driven by it so the two cannot drift.
- K3: a key present-vs-absent moves `effective_config_digest` and refuses every
  already-run experiment. That cost is payable ONCE, which is why everything
  lands as one bundle.
- Two rows are NOT behaviour-preserving and need an explicit per-row hook.

### Goal

One command rewrites a complete v1 config set to v2 — keys, files, glob and
`schema_version` — and tells the user what changed where a rewrite is not
behaviour-preserving.

### Non-goals

- Migrating the shipped `test_case/` sets (P4 — this rewriter does it).
- The `C-85` file rename's own commit discipline (P5 owns that).

### Allowed scope

- **Permitted:** `scripts/split_project_config.py` (extend) or a sibling,
  `tests/data/presplit/**`, `tests/` for the above.
- **Forbidden:** `config/defaults/**`, `config/catalogs/**`;
  `dev/milestones/**`.

### Required changes (checklist)

1. Extend `scripts/split_project_config.py` (or add a sibling) into a v1→v2
   rewriter **driven by the register**, performing in one pass: key renames and
   regroups, the file renames, the `.gitignore` glob move, and the
   `schema_version: 2` stamp.
2. Implement the two non-preserving hooks (design D-11.5):
   - **`C-69`** — a v1 config with `run_historical: false` is rewritten AND the
     user is told the run will now gain `st_0` and with it
     `q_wettest_month_mean` / `q_driest_month_mean`, 2 of 11 q metrics.
   - **`N8`** — a project with `water_year_start != Jan` is **REFUSED**, naming
     the window it will not rewrite. Old bounds are calendar, new are
     water-year; there is no number-preserving rewrite.
3. Ship the **stale-spelling sweep**: a grep per retired spelling across
   tracked files outside `dev/milestones/**`, failing on any hit. No such tool
   exists today.
4. Add a v1→v2 pair to `tests/data/presplit/`, which exists precisely to test
   migration.

### Commit plan

The rewriter is a contract rename: it breaks every consumer of the old key
spellings the moment it lands.

| subject | paths | invariant preserved |
|---|---|---|
| add the rewriter, register-driven, no callers yet | `scripts/`, `tests/data/presplit/` | tree still parses v1; nothing migrated yet |
| add the two non-preserving hooks + their fixtures | `scripts/`, `tests/` | refusal and warning paths covered before any real config moves |
| add the stale-spelling sweep | `scripts/` or `dev/scripts/` | sweep is green on a v1 tree; it has nothing to find yet |

### Validation

- Rung 1: unit tests over the register-driven mapping.
- Rung 2 — falsifiers, each built to fail:
  - **"the rewrite is byte-exact for the window conversion"** — `end: 2016`
    must emit `"2016-12-31T00:00:00"`, the string in the config today, MIDNIGHT
    on 31 December rather than end-of-day. Reproducing it verbatim is the
    point; "fixing" it moves a number.
  - **"`N8` refuses rather than shifting"** — a fixture with
    `water_year_start: Oct` must exit non-zero naming the window. A silent
    rewrite here is the failure mode.
  - **"the mapping cannot drift from the register"** — mutate one register row
    in a test fixture and assert the rewriter's behaviour changes with it.
- Rung 3: `pytest tests/test_cli.py`.
- Rung 4: `pixi run test-fast`.

### Acceptance criteria

- One command migrates a complete v1 set, verified on the `presplit/` pair.
- The `Oct` fixture is refused, not rewritten.
- The `false` → `st_0` case is rewritten AND reported.
- The stale-spelling sweep exists and runs.

### Output requirements

Show the rewriter's diff for ONE `test_case/` set and the `Oct` refusal
message. **PAUSE at Gate 3** before P4 migrates the other three.

### Task constraints

- The register is the source of truth. If a mapping is not derivable from it,
  the register is wrong — fix it there, not in the rewriter.
- Do not make `N8`'s refusal bypassable with a flag. A silent shift is exactly
  what the refusal exists to prevent.
