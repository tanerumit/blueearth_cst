---
title: Widen C-37 to the shipped seeds, and ask its mirror question
type: todo-item
status: backlog
effort: 1
area: config / gates
origin: C-37 closure
queue: 2
created: 2026-09-07
updated: 2026-09-07
---

> [!note] Overview
> **What** — Extend the declared side of `sweep_unread_config_keys.py` from the five templates to the shipped `test_case/project_config_*.yml` seeds, and add the mirror check: a key a run READS that no template documents.
> **Why** — Measured 2026-09-07 at C-37's landing: the seeds carry 58 leaf names against the templates' 53, and 11 the templates do not declare. So a green C-37 run certifies the template surface only, which is a narrower claim than the note it closed was written to make.
> **Effort** — small

## Progress

- [ ] <first step>

## What the measurement found

The 11 seed leaves the templates do not declare split three ways:

| leaves | what they are | what it takes |
|---|---|---|
| `build_config`, `waterbodies_config` | real config keys, read, **undocumented in the build_model template** | the MIRROR check — a read key with no template entry |
| `source`, `canonical`, `units`, `change` | `VariableSpec` fields, read by **dataclass construction** | a reader form for dataclass fields; without it these four report unread while being read perfectly well |
| `name`, `dry`, `wet`, `river discharge` | user-CHOSEN names inside a mapping, plus an outvar value used as a key | a way to tell a declared key from a user-supplied one, or these become permanent noise |

The middle row is why this was not folded into `C-37` itself: widening the
declared side without the dataclass reader form first would ship a check that
reports four false alarms on its first run, which is how a gate gets switched
off (`D-14.4`'s argument, from the other direction).

The boundary is pinned by
`tests/test_unread_config_key_sweep.py::test_the_shipped_seeds_are_a_pinned_gap_not_silent_coverage`,
so a green C-37 run cannot be mistaken for coverage it does not have. That test
names `build_config` and `waterbodies_config` explicitly — if they gain template
entries, update `TEMPLATE_GLOB`'s boundary note rather than deleting the
assertion.

## Links

- `dev/scripts/sweep_unread_config_keys.py` — `TEMPLATE_GLOB`, whose comment
  carries the measurement
- `blueearth_cst/projections/variable_spec.py` — the dataclass whose fields are
  config keys
