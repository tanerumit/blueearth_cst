Task Brief — P3: the v1→v2 rewriter

### Context

Canonical ruleset: `AGENTS.md`. Design: `config-shape-design.md` §11.
Program: `config-shape-master-brief.md`.

- The register (`config-shape-scoping.md`, `C-01`..`C-85`) is the ARGUMENT.
  The MAPPING is a separate normative artifact this phase ships — 85 rows of
  markdown table cannot be executed or checked for completeness (external
  finding `ext1-1`).
- K3: a key present-vs-absent moves `effective_config_digest` and refuses every
  already-run experiment. That cost is payable ONCE, which is why everything
  lands as one bundle.
- Two rows are NOT behaviour-preserving and need an explicit per-row hook.

### Goal

One command rewrites a complete v1 config set to v2 — keys, files, glob,
`schema_version` and the per-experiment records — transactionally, PRESERVING
COMMENTS, and tells the user what changed where a rewrite is not
behaviour-preserving.

**Build it as a SIBLING of `scripts/split_project_config.py`, never as an
extension.** That script's contract is report-only — "never edits, moves or
deletes the config you point it at ... There is no `--write` and no in-place
mode" — and D-11.2b requires atomic in-place replacement.

**Comments: use `ruamel.yaml`'s round-trip (D-11.8, ruled 2026-08-24).** A
`safe_dump` rewriter deletes 86 of the 109 lines in the shipped template and
every annotation a user wrote. `ruamel.yaml` 0.19.1 is already in the lock, but
via `dvc`/`gto`, so **declare it explicitly in `pixi.toml`** in the same commit
that first imports it — an undeclared transitive dependency under a
load-bearing migration tool vanishes the day an unrelated package drops it.
Keep the round-trip confined to this tool; nothing else should import it.

### Non-goals

- Migrating the shipped `test_case/` sets (P4 — this rewriter does it).
- The `C-85` file rename's own commit discipline (P5 owns that).

### Allowed scope

- **Permitted:** a NEW sibling script under `scripts/`, `config/migrations/**`
  (new), `tests/data/presplit/**`, `tests/` for the above, and the one-line
  `ruamel.yaml` declaration in `pixi.toml`.
- **Forbidden additionally:** `scripts/split_project_config.py` — do not modify
  R13's tool.
- **Forbidden:** `config/defaults/**`, `config/catalogs/**`;
  `dev/milestones/**`.

### Required changes (checklist)

1. **Ship the mapping as a NORMATIVE artifact first** — `config/migrations/
   v1_to_v2.yml`, per design D-11.2a, with `id`, `old_path`, `new_path`, `op`,
   `value_transform`, `on_collision`, `default_if_absent`, `exception_hook` per
   row. A register row with no mapping entry, or a mapping entry naming no
   register row, **fails the build**. The register's markdown table is the
   argument; this file is the specification.
2. Extend `scripts/split_project_config.py` (or add a sibling) into a v1→v2
   rewriter driven by that mapping: key renames and regroups, the file renames,
   the `.gitignore` glob move, the `schema_version: 2` stamp, and the
   experiment-record migration (item 4).
3. **Make it TRANSACTIONAL** (design D-11.2b): preflight read-only over the
   COMPLETE set — every file parsed, every mapping row resolved, every
   exception hook evaluated — aborting on any refusal or destination collision
   BEFORE a byte is written; then stage, validate the staged set against the
   loader, commit atomically, and keep `*.v1.bak`. Re-running on a complete v2
   set is a reported no-op; re-running on a PARTIAL set refuses and names the
   inconsistency.
4. **Migrate `experiment.yml` under `<project_dir>/experiments/*/` with the
   same mapping** (design §11.6). Without this, `_frozen_differences` diffs the
   whole renamed `run_stress_test` key set on EVERY attempt and every already-run
   experiment becomes permanently unrunnable — `RETIRED_EXPERIMENT_KEYS` does
   not rescue it, because its escape covers only keys that DISAPPEAR.
5. Implement the two non-preserving hooks (design D-11.5):
   - **`C-69`** — a v1 config with `run_historical: false` is rewritten AND the
     user is told the run will now gain `st_0` and with it
     `q_wettest_month_mean` / `q_driest_month_mean`, 2 of 11 q metrics.
   - **`N8`** — a project with `water_year_start != Jan` is **REFUSED**, naming
     the window it will not rewrite. Old bounds are calendar, new are
     water-year; there is no number-preserving rewrite.
6. Ship the **stale-spelling sweep** — and note it CLASSIFIES rather than
   greps (design D-14.4). Zero retired spellings in active config, code
   identifiers, command lines and live docs; an allowlist for the mapping, the
   `presplit/` v1 fixtures, the migration note's tables, refusal-message
   literals and this rewriter's own tests, each carrying a declared reason;
   **fails closed** on an unknown classification. "Fail on any hit" is
   unsatisfiable — your own mapping file would trip it.
7. Add a v1→v2 pair to `tests/data/presplit/`, which exists precisely to test
   migration.

### Commit plan

The rewriter is a contract rename: it breaks every consumer of the old key
spellings the moment it lands.

| subject | paths | invariant preserved |
|---|---|---|
| add `config/migrations/v1_to_v2.yml` + the register↔mapping completeness check | `config/migrations/`, `tests/` | the mapping is complete and traceable before anything consumes it |
| add the rewriter, mapping-driven, no callers yet | `scripts/`, `tests/data/presplit/` | tree still parses v1; nothing migrated yet |
| add the transactional wrapper (preflight → stage → validate → atomic commit) | `scripts/`, `tests/` | no partial write is reachable, proven by the mid-set refusal test |
| migrate `experiment.yml` records with the same mapping | `scripts/`, `tests/` | an untouched experiment yields an EMPTY `_frozen_differences` |
| add the two non-preserving hooks + their fixtures | `scripts/`, `tests/` | refusal and warning paths covered before any real config moves |
| add the stale-spelling sweep | `scripts/` or `dev/scripts/` | sweep is green on a v1 tree; it has nothing to find yet |

### Validation

- Rung 1: unit tests over the register-driven mapping.
- Rung 2 — falsifiers, each built to fail:
  - **"comments survive"** — migrate
    `config/templates/snake_config.template.yml` and assert its comment-line
    count is unchanged at **86** (D-14.9). A `safe_dump` regression passes every
    other check here while destroying four fifths of the file. Assert separately
    that a comment attached to a DELETED key (`static_dir`, `run_historical`)
    follows the declared rule rather than being silently reattached to a
    neighbour.
  - **"the rewrite is byte-exact for the window conversion"** — `end: 2016`
    must emit `"2016-12-31T00:00:00"`, the string in the config today, MIDNIGHT
    on 31 December rather than end-of-day. Reproducing it verbatim is the
    point; "fixing" it moves a number.
  - **"`N8` refuses rather than shifting"** — a fixture with
    `water_year_start: Oct` must exit non-zero naming the window. A silent
    rewrite here is the failure mode.
  - **"the mapping cannot drift from the register"** — the build fails when a
    register row has no mapping entry, and when a mapping entry names no
    register row. Test both directions.
  - **"a refusal mid-set leaves nothing written"** — point the rewriter at a
    set whose THIRD file trips `N8`, and assert the tree is byte-identical
    afterwards. This is D-11.2b's whole point and no unit test reaches it.
  - **"an untouched experiment still runs"** — migrate a project with a
    completed experiment, re-run WF3 changing nothing, assert
    `_frozen_differences` is EMPTY (design D-14.8).
- Rung 3: `pytest tests/test_cli.py`.
- Rung 4: `pixi run test-fast`.

### Acceptance criteria

- One command migrates a complete v1 set, verified on the `presplit/` pair.
- The `Oct` fixture is refused, not rewritten, AND no file is written.
- An untouched experiment survives migration with an empty `_frozen_differences`.
- The `false` → `st_0` case is rewritten AND reported.
- The stale-spelling sweep exists and runs.

### Output requirements

Show the rewriter's diff for ONE `test_case/` set and the `Oct` refusal
message. **PAUSE at Gate 3** before P4 migrates the other three.

### Task constraints

- The register is the source of truth for WHAT changes and why; the mapping
  file is the source of truth for HOW. If a mapping row is not derivable from a
  register row, the register is wrong — fix it there, not in the rewriter, and
  never encode a transformation the register does not justify.
- Do not make `N8`'s refusal bypassable with a flag. A silent shift is exactly
  what the refusal exists to prevent.
