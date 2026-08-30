---
title: Give the stale-spelling sweep its remaining allowance classes
type: todo-item
status: backlog
effort: 1
area: config / naming
origin: R14 P6
queue: 2
created: 2026-08-29
updated: 2026-08-29
---

> [!note] Overview
> **What** — `dev/scripts/sweep_stale_spellings.py` exits 1 with 113
> unclassified hits, none of which is a defect. It needs allowance classes for
> the two populations that hold v1 spellings BY DESIGN.
> **Why** — A gate that is always red is a gate nobody runs, and this one is
> R14's rung-1 check. It is currently useful only when read by hand and filtered
> by path.
> **Effort** — Small. The classifier already has ten allowance classes with
> stated reasons; this is two or three more.

## What is actually in there

Measured 2026-08-29 at `bedadddd`, after P6 swept everything in its own scope.
The sweep is clean across `docs/`, `README.md`, `AGENTS.md` and
`dev/reference/`; what remains is all outside P6's permitted paths.

*(Re-measured 2026-08-30 at Gate 5, `66547c2d`: **117**, not 113, and `docs/`
is no longer clean — `docs/migration-config-tiers.md` contributes 4. It is
R13's migration record and holds v1 keys for the same reason
`config/migrations/v1_to_v2.yml` does, so it belongs in the first population
rather than being swept. One thing the sweep could not see at all: `AGENTS.md`
still described the shared tier as `shared:`, a heading R14 dissolved. The
token was a SECTION name, not a key, so no allowance class would have helped —
fixed in the Gate 5 follow-up commit, and worth remembering when choosing what the
classifier matches on.)*

| population | example | why it holds a v1 spelling |
|---|---|---|
| the migration machinery | `config/migrations/v1_to_v2.yml` (27), `scripts/migrate_project_config.py` (23), `config_composition.py`'s `RETIRED_KEYS` (20) | it exists to name v1 keys; a sweep that "fixed" these would delete the migration |
| tests of refusals | `test_config_composition.py` (14), `test_migrate_project_config.py` (12), `test_experiment_config.py` (14) | asserting that a v1 spelling is REFUSED requires writing it |
| `dev/scripts/` maps | `semantic_tree_diff.py` (4) and its 20-hit test | an OLD→NEW path map is half old paths by construction |
| function parameters | `projections/resolution.py` (13), `test_resolution.py` (27) | `clim_project` is a parameter name, not a config key — P1b's tier rule deliberately leaves locals and params alone |

That last row is the one worth a moment: it is not a stale spelling at all. The
sweep matches the token; the tier rule says a config-key READ moves and a
parameter does not. The classifier needs to be able to say "this is a Python
parameter" rather than being widened until it stops complaining.

## The trap this sweep would have caught, and did not

R14 produced the same defect **six times**: a blanket token rename rewriting the
OLD side of a rename record, so it reads `X -> X`. It hit `C-85`'s own mapping
row, two board notes, `naming.md`'s ad-hoc-contraction sentence, and two columns
of `rule-index.md`'s former-name table.

Every one was caught by a test or by reading the diff, never by the sweep —
which is the tool nominally responsible for exactly this. A class for
**"a line that records a rename"** would turn the most reliable defect of this
milestone into a mechanical check. That is probably worth more than the
allowance classes above.

## Links

- `dev/scripts/sweep_stale_spellings.py` — the classifier and its ten existing
  classes, each with a stated reason
- `dev/milestones/r14/config-shape-p6-docs.task.md` — names the sweep as P6's
  rung 1
