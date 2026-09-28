Task Brief — P1: loader, seam, and parse-time refusals

### Context

Canonical ruleset: `AGENTS.md`. Design: `config-shape-design.md` §10.
Program: `config-shape-master-brief.md`.

- `shared:` ceases to exist and becomes `basin:`, `climate:`, `model:` at T1
  top level (`C-01`, `C-10`, `C-16`, `C-19`).
- `HOISTED_SECTIONS` is `{"run_stress_test": ("reporting",)}` — one entry
  (`E9`) — and `C-77` removes its only user.
- `SHARED_SEAM_KEYS` is a flat set of NAMES, so nesting moves seam coverage
  from leaf to group; a T2 file could then declare a bare `window:` uncaught.

### Goal

The loader composes, validates and refuses against the new layout, and the
hoist mechanism is retired rather than left empty.

### Non-goals

- The guard and the digest (P2).
- Rewriting any config file (P4).

### Allowed scope

- **Permitted:** `blueearth_cst/shared/config_composition.py`,
  `blueearth_cst/shared/snake_utils.py`, the four `*.smk` where they read
  renamed keys, and `tests/` for the above.
- **Forbidden:** `config/defaults/**`, `config/catalogs/**` (K1);
  `dev/milestones/**`.

### Required changes (checklist)

1. `T1_TOP_LEVEL` accepts `basin`, `climate`, `model`; no longer `shared`.
2. **Re-DERIVE `SHARED_SEAM_KEYS`** from the new section names — do not edit it
   name by name (design D-10.3). Add a test that the derived set covers every
   T1 leaf a T2 file must not declare.
3. **RETIRE `HOISTED_SECTIONS`** (design D-10.1): remove the constant, its
   composition branch, and the T2 foreign-hoist rejection it feeds. The commit
   message records this as an amendment to accepted R13 decision D-10.4.
4. Remove `parse_surfaces` from the Snakefile imports and its call site.
   **Keep `blueearth_cst/shared/surface_axes.py`** — the HM-7 reference
   implementation, which no rule called before this change either.
5. Implement the parse-time refusals in design D-10.4's table, each naming its
   fix. `climate.selected` unset with only WF0 enabled stays VALID (D-10.5).

### Validation

- Rung 1: the tests covering the two modules changed.
- Rung 2: one new test per refusal row, asserting the MESSAGE names the fix,
  not merely that it raises.
- Rung 3: `pytest tests/test_cli.py` — dry-runs all four entry points and is
  the only place a malformed `config/defaults/*.yml` surfaces.
- Rung 4: `pixi run test-fast`.
- **Falsifier for "the hoist is retired, not emptied":** grep the tree for
  `HOISTED_SECTIONS`. A surviving definition, even an empty one, fails this
  phase — an empty registry that can be refilled cannot enforce shrink-only.
- **Falsifier for the seam re-derivation:** a T2 file declaring a bare
  `window:` must be REFUSED at parse time. Write that test before the code.

### Acceptance criteria

- All four entry points dry-run clean against a hand-written v2 config.
- Every refusal message names its fix.
- `HOISTED_SECTIONS` does not exist anywhere in the tree.

### Output requirements

State which rung caught what. A rung that failed red and was fixed is the
informative record; a log of terminal passes says nothing about which gate
earned its cost.

### Task constraints

- `get_config` contract preserved (K5): raise on missing required, return the
  default for optional.
- Do not touch `config/defaults/**` for any reason (K1).
