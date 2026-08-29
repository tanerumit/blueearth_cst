Task Brief — P1b: the per-workflow (T2) key readers

### Context

Canonical ruleset: `AGENTS.md`. Design: `config-shape-design.md` §7.2–§7.5.
Program: `config-shape-master-brief.md`.

**This phase did not exist in the master brief's v2 phase table.** P1 found the
gap and the owner ruled it on 2026-08-25: the T2 key renames are owned by no
phase, and without them the bundle cannot be assembled at all. Added here rather
than folded into P4 for two dependency reasons, both load-bearing:

- **P2 is blocked today.** Its three rung-2 falsifiers each say *"build a model
  … run WF3"*, and WF3 cannot run against anything: a v1 config hits P1's
  `schema_version` refusal and a v2 config hits `KeyError: 'stress_test'`.
- **P4's rung 1 is vacuous without this.** *"dry-runs all four entry points
  against every migrated set"* is the cheapest proof P4's migrated configs
  parse, and it proves nothing if the readers still want v1 keys. The readers
  must PRECEDE P4, which is what rules out widening P4 to absorb them.

P1 moved the T1 reads only — `project:`, `basin:`, `climate:`, `model:`, which
is what `shared:` dissolved into. Everything below is what it left.

### Goal

Every runtime reader is on the v2 spelling, so a v2 config runs end to end and
the bundle becomes assemblable.

### Non-goals

- Rewriting any config file — P3 ships the rewriter, P4 runs it. **You do not
  hand-edit `test_case/*.yml` or `config/templates/**`.** Fill in the P1-owned
  probe fixture under `tests/data/v2/` instead.
- The guard, the freeze, and `compute:`'s exclusion from `CONFIG_PROJECTION` —
  P2. You REGROUP `compute:` in the config surface; P2 decides what the
  projection does with it.
- The `snake_config_` → `project_config_` file rename — P5.

### Allowed scope

- **Permitted:** `blueearth_cst/**`, the four `*.smk`, `tests/**` including
  `tests/data/v2/**`, and — for `C-54` only — `config/advanced_settings.yml`
  together with `_ADVANCED_SETTINGS_SCHEMA` in `snake_utils.py`.
- **Forbidden:** `config/defaults/**`, `config/catalogs/**` (`K1` — an
  AGENTS.md hard constraint; if you find yourself editing these, stop);
  `test_case/*.yml` and `config/templates/**` (P4 migrates those WITH the
  rewriter, and its falsifier is *"any difference is a hand-edit"*);
  `scripts/**`.

### Required changes (checklist)

The register rows, with the reader surface measured 2026-08-25 from
`feat/r14-p1-loader`. **Re-measure before starting** — P1 moved the T1 reads
underneath these counts, and the R14 register has already been stale twice.

| row | v1 spelling | v2 | note |
|---|---|---|---|
| `C-68` | `stress_test:` | `climate_perturbations:` | the largest single row |
| `C-31` | `step_num` | `n_levels` | **`n_levels` = `step_num` + 1**, not a rename |
| `C-32` | `transient_change: true` | `trajectory: transient` | enum, REQUIRED, no default (P1 already refuses a missing one) |
| `C-33` | `dry_spell_factor` / `wet_spell_factor` | `climate_perturbations.spell_factors.{dry,wet}` | |
| `C-67` | `horizontime_climate` + `run_length` | `simulation_window: {start, end}` | TWO keys become one; inclusive years |
| `C-69` | `run_historical` | deleted; `st_0` ALWAYS produced | **not behaviour-preserving** — see below |
| `C-29` | `realizations_num` | `n_realizations` | |
| `C-34` | flat `batch_size`, `batch_size_max`, `disk_headroom_gb` | under `compute:` | regroup only; P2 owns the projection |
| `C-22` | `model_build_config`, `waterbodies_config` | `engine.build_config`, `engine.waterbodies_config` | |
| `C-56` | `observations_timeseries` | `observations:`, a mapping KEYED BY VARIABLE from `model.outvars` | P1 already refuses a key that is not a declared outvar |
| `C-25` | `clim_project` | `ensemble` | |
| `C-59` | `historical_year_range` | `reference_window: {start, end}` | CALENDAR years, deliberately (`C-74`) — do NOT apply the water-year offset |
| `C-60`/`C-61` | `future_horizons` | `future_windows:`, a LIST of `{start, end, name}` | `C-61` also renames WF2's figure directories |
| `C-63` | `members: [r1i1p1f1]` | `members: {preference, selection, overrides}` | one read site: `analyze_projections.smk:131` |
| `C-57` | long-form `variables:` | short form, registry-resolved | one read site: `analyze_projections.smk:139` |
| `C-66` | `relative_change:` | dissolves | `min_denominator` → per-variable registry (`C-64`); `max_flagged_months` → `advanced_settings.constraints` (`C-65`) |
| `C-54` | — | `advanced_settings.runtime.julia_threads` | the half P1 left; see below |

**`C-54` is a COUPLED EDIT and the only reason `config/` is in scope.** P1
removed the project-level override, which is the behavioural half.
`config/advanced_settings.yml` has a CLOSED schema: move the key from
`defaults:` to `runtime:` and update `_ADVANCED_SETTINGS_SCHEMA` in the same
commit, or they drift silently. `DEFAULT_JULIA_THREADS` reads
`ADVANCED_SETTINGS["defaults"]["julia_threads"]` today.
`RETIRED_KEYS["T1.shared.julia_threads"]` already names the destination, so
until this lands that refusal names a key that does not exist — the sweep for
it is a grep for one literal.

**`C-69` is one of the two rows the design declares NOT behaviour-preserving**
(D-11.5). A project that had `run_historical: false` GAINS `st_0` and with it
`q_wettest_month_mean` / `q_driest_month_mean` — 2 of 11 q metrics. The shipped
`baseline_linux`, `wf2_fast` and the test fixture are all in the gaining
direction. Do not treat a changed indicator count here as a defect.

### Validation

- **Rung 1, while iterating:** only the tests covering the module you changed.
- **Rung 2 — fill in the probe fixture and make it prove something.**
  `tests/data/v2/` currently ships near-empty T2 bodies, deliberately, because
  P1 had not moved these reads. Fill them to design §7.2–§7.5 and move
  `analyze_projections` and `run_stress_test` from `V2_BLOCKED` to `V2_CLEAN`
  in `tests/test_v2_config_shape.py`. **That module is written to fail when you
  succeed** — `test_wf2_and_wf3_stop_at_the_first_t2_renamed_key` passes today
  BECAUSE the work is undone, so its red is your signal, not a regression.
- **Rung 3, per commit:** `pytest tests/test_cli.py`, plus `pixi run lint` and
  `pixi run format-check`.
- **Rung 4, at phase end:** `pixi run test-fast`, reconciled against
  `tests/data/r14_expected_red.txt` — a failure outside that list is yours.
  **Shrink the list as you go:** every reader you move takes nodes off it, and
  a stale entry fails `test_r14_expected_red.py` by design.
- **Rung 5, once:** `pixi run test-full`. Five of the touched files are in
  `shared/` (`interchange_contracts.py`, `snake_utils.py`, `surface_axes.py`,
  `statistics_heatmap.py`, `merge_logs.py`), which is the
  `workflow_contract` / `process_isolation` tier's own trigger under AGENTS.md.
- Do NOT run `check_baseline.py` or a real workflow. Those are Gate 5 costs and
  the master brief batches them deliberately.
- Redirect every gate to a FILE and read the tail; never pipe through `tail`.

### Falsifiers

- **"the readers are migrated"** — all four entry points dry-run clean against
  the filled-in `tests/data/v2/` set. This is P1's acceptance criterion, which
  P1 could only meet for WF0 and WF1.
- **"no v1 spelling survives on a run path"** — grep the tree for each row's v1
  key. Expected survivors, and ONLY these: `RETIRED_KEYS` in
  `config_composition.py` (the refusal literals, which must keep the old
  spellings to recognise them), P3's migration mapping, and the `presplit/`
  v1 fixtures. Anything else is a missed reader. `C-37`'s stale-spelling sweep
  is the mechanical successor and lands in P3 — use it if it exists by then.
- **"`n_levels` is not `step_num`"** — a config with `step_num: 1` must produce
  the SAME grid as one with `n_levels: 2`. Assert the member count, not the
  key.

### Acceptance criteria

- All four entry points dry-run clean against the v2 fixture set.
- `tests/data/r14_expected_red.txt` is reduced to only what P4 still owes.
- `advanced_settings.yml` and `_ADVANCED_SETTINGS_SCHEMA` agree, in one commit.

### Output requirements

State which rung caught what. **A rung that failed red and was fixed is the
informative record**; a log of terminal passes says nothing about which gate
earned its cost. P1's two worst defects were caught by no rung at all — an
unreachable third of its refusal table and a silently narrowed
`CONFIG_PROJECTION` — so if every gate is green first time, say so plainly
rather than presenting it as evidence of correctness.

### Task constraints

1. `get_config` contract preserved (`K5`): raise on missing required, return
   the default for optional.
2. `workflow.configfiles[0]` still forwarded as `config_path` (`K6`).
3. Do not touch `config/defaults/**` for any reason (`K1`).
4. `K3`: commit on the branch and stop. Nothing merges to `main` until the
   whole R14 bundle is green together.

---

*Added 2026-08-25 by owner ruling, on P1's finding that no phase owned these
rows. Board item `t2608251900` carries the measurement that prompted it.*
