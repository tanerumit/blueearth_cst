---
title: R14 - the T2 key renames, now owned by P1b
type: todo-item
status: active
effort: 5
area: config shape / R14
origin: R14 P1
queue:
created: 2026-08-25
updated: 2026-08-26
---

> [!note] Overview
> **RESOLVED 2026-08-25 — owner ruled a new phase, `P1b`.** The brief is
> `dev/milestones/r14/config-shape-p1b-readers.task.md`; the master brief is
> reissued at v3 with `P1 → P1b → P2` and `P1b → P4`. Both orderings are forced
> by other phases' own validation, not chosen: P2's rung-2 falsifiers need WF3
> to RUN, and P4's rung 1 is vacuous while the readers still want v1 keys —
> which is what ruled out widening P4 to absorb them. `C-54`'s
> `advanced_settings.runtime.julia_threads` destination is folded into the same
> phase, since it is a coupled edit with the closed `_ADVANCED_SETTINGS_SCHEMA`.
> This item stays open as the MEASUREMENT behind that ruling; close it when P1b
> lands.
>
> **What** — R14's per-workflow (T2) key renames had no owner in the master brief's phase table. P1 moved the T1 reads (`project:`, `basin:`, `climate:`, `model:` - what `shared:` dissolved into) and stopped there, because P1's permitted scope is `config_composition.py`, `snake_utils.py`, the four `*.smk` and `tests/`. The T2 renames - `C-22`, `C-25`, `C-29`, `C-31`, `C-32`, `C-33`, `C-56`, `C-59`, `C-60`, `C-66`, `C-67`, `C-68`, `C-69` - are ~280 sites across `blueearth_cst/experiment/`, `blueearth_cst/projections/` and `blueearth_cst/model/`. None of those three package directories is in ANY phase's permitted scope, and none of the sites is in a Snakefile.
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

> [!warning] The table above is WRONG in both directions. Corrected 2026-08-26
> by P1b, which its own brief told to re-measure before starting.
>
> The counts were taken with a `\b`-anchored pattern, which
> **undercounts** by excluding compound identifiers — `\bstress_test\b` does
> not match `stress_test_cfg`, the very spelling this table names in its own
> first column. Unanchored, `stress_test` is 106 occurrences, not 38.
>
> It **overcounts** at the same time, because most of those 106 are
> `run_stress_test` — the entry point and workflow name, which does not move —
> and 35 of `clim_project`'s are `clim_project_dir`, a derived output path.
>
> The number that mattered was never the occurrence count. It is the count of
> **config-key READS**, which is roughly 30 across the three workflows. The
> scope rule P1b settled on, checked against P1's own precedent
> (`build_model.smk:106` reads `climate.window` into a local still named
> `historical_window`): rename config key reads and the strings that name a key
> back to the user; leave locals, derived paths, `params:` names and rule input
> names alone. A sweep on the bare token would have flagged ~200 sites that
> must not change.
>
> Row-level corrections: `C-71` was ALREADY migrated by P1 and is not a P1b
> row. `C-63` has three read sites, not one. `C-57`'s single read site sits on
> top of a registry that does not exist, which is why it went to P1c.

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

- [x] Owner decides where this lands — 2026-08-25, a new phase `P1b` between
      P1 and P2, with `C-54`'s destination folded in.
- [x] Brief written: `dev/milestones/r14/config-shape-p1b-readers.task.md`.
- [x] Master brief reissued at v3 with the sequencing and the phase index.
- [x] P1b executed 2026-08-26 (four commits on `feat/r14-p1-loader`). All
      four entry points dry-run clean on v2; `V2_BLOCKED` retired; the
      declared-red list shrank 83 -> 73.
- [x] **P1c** landed 2026-08-29 (six commits). The registry is
      `blueearth_cst/shared/variable_registry.py`; `C-57`, `C-62`, `C-64`,
      `C-65` and `C-66` are all in. Gate 1's ruling and the three risks it
      recorded are at `dev/milestones/r14/config-shape-p1c-gate1.md`.
- [x] **Unowned, found by P1b** — fixed 2026-08-29, and the prediction was
      half right. `prune_series_cache` was broken in THREE places, not one:
      `clim_project` -> `ensemble`, the climate catalog's move, and `C-63`'s
      `members:` group, which it passed whole to a resolver expecting a list.
      `prune_climate_store` was broken too and nobody had predicted it. But
      `check_baseline.py`'s `CLIM_PROJECT` is a PINNED LITERAL describing the
      recorded baseline, not a config read, so it was never at risk.

## Links

- `dev/milestones/r14/config-shape-p1b-readers.task.md` - the phase that took it
- `dev/milestones/r14/config-shape-master-brief.md` - v3 phase table and sequencing
- `dev/milestones/r14/config-shape-design.md` §7.2-§7.4 - the target T2 shapes
- `tests/test_v2_config_shape.py` - the executable boundary marker
