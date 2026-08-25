---
title: R14 - the T2 key renames are unowned, and the bundle cannot go green without them
type: todo-item
status: blocked
effort: 5
area: config shape / R14
origin: R14 P1
queue:
created: 2026-08-25
updated: 2026-08-25
---

> [!note] Overview
> **What** — R14's per-workflow (T2) key renames have no owner in the master brief's phase table. P1 moved the T1 reads (`project:`, `basin:`, `climate:`, `model:` - what `shared:` dissolved into) and stopped there, because P1's permitted scope is `config_composition.py`, `snake_utils.py`, the four `*.smk` and `tests/`. The T2 renames - `C-22`, `C-25`, `C-29`, `C-31`, `C-32`, `C-33`, `C-56`, `C-59`, `C-60`, `C-66`, `C-67`, `C-68`, `C-69` - are ~280 sites across `blueearth_cst/experiment/`, `blueearth_cst/projections/` and `blueearth_cst/model/`. None of those three package directories is in ANY phase's permitted scope, and none of the sites is in a Snakefile.
> **Why** — This blocks Gate 5. Until the T2 reads move, no entry point runs a v2 config: WF2 stops at `clim_project` (`C-25`) and WF3 at `stress_test` (`C-68`), both at parse time. `K3` says the bundle merges as one green whole, so an unowned body of work between P4 and Gate 5 means the bundle can never be assembled. It is a gap in the phase table, not in any phase's execution.
> **Effort** — large; comparable to P3 or P4, and it interlocks with both.

## Evidence

Measured 2026-08-25 from `feat/r14-p1-loader`, by occurrence across `*.smk` and
`blueearth_cst/**/*.py`:

| v1 key | -> v2 | row | sites |
|---|---|---|---|
| `clim_project` | `ensemble` | `C-25` | 86 |
| `stress_test` (`stress_test_cfg`) | `climate_perturbations` | `C-68` | 38 |
| `step_num` | `n_levels` (= step_num + 1) | `C-31` | 35 |
| `run_length` | folded into `simulation_window` | `C-67` | 22 |
| `transient_change: true` | `trajectory: transient` | `C-32` | 17 |
| `horizontime_climate` | folded into `simulation_window` | `C-67` | 16 |
| `waterbodies_config` | `engine.waterbodies_config` | `C-22` | 11 |
| `model_build_config` | `engine.build_config` | `C-22` | 9 |
| `observations_timeseries` | `observations:` keyed by variable | `C-56` | 9 |
| `dry_spell_factor` / `wet_spell_factor` | `climate_perturbations.spell_factors.{dry,wet}` | `C-33` | 18 |
| `future_horizons` | `future_windows` | `C-60` | 8 |
| `realizations_num` | `n_realizations` | `C-29` | 7 |
| `run_historical` | deleted; `st_0` always produced | `C-69` | 7 |
| `relative_change` | dissolved | `C-66` | 5 |
| `historical_year_range` | `reference_window` | `C-59` | 3 |

`tests/test_v2_config_shape.py::test_wf2_and_wf3_stop_at_the_first_t2_renamed_key`
is the executable form of this: it passes BECAUSE the work is not done, and
fails the moment it is - at which point the entry point moves into `V2_CLEAN`
in the same module and that case is deleted.

## Also unowned, and it belongs here

`C-54`'s destination. P1 removed the project-level `shared.julia_threads`
override, which is the behavioural half. The register sends the toolbox setting
to `advanced_settings.runtime.julia_threads`, a `defaults:` -> `runtime:`
regroup inside `config/advanced_settings.yml` that must land in the same commit
as `_ADVANCED_SETTINGS_SCHEMA` (the schema is closed, which is what stops them
drifting). `config/advanced_settings.yml` is in no phase's permitted scope
either. Until it moves, `DEFAULT_JULIA_THREADS` still reads
`ADVANCED_SETTINGS["defaults"]["julia_threads"]` and every refusal message
naming `advanced_settings.runtime.julia_threads` names a key that does not
exist yet.

`RETIRED_KEYS` in `config_composition.py` carries that string, so the sweep for
it is a grep for one literal.

## Progress

- [ ] Owner decides where this lands: a new phase between P4 and P5, a widening
      of P4's scope, or a separate milestone after the bundle.
- [ ] Whoever takes it: the T2 renames and `C-54`'s regroup travel together
      with P4's config migration, because a migrated config and an unmigrated
      reader fail on each other.

## Links

- `dev/milestones/r14/config-shape-master-brief.md` - the phase table with the gap
- `dev/milestones/r14/config-shape-design.md` §7.2-§7.4 - the target T2 shapes
- `tests/test_v2_config_shape.py` - the executable boundary marker
