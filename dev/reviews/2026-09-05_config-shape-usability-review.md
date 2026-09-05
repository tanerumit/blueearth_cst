# Config shape after R13/R14 — usability and footprint review

Date: 2026-09-05. Reviewed at `main` 9cf54e18 (R14 sealed), against the live run
`session-1/.tmp/test_run/config/` made at 679f0fb6 from the untracked
`test_case/test.yml` set. Scope: the project-file + per-workflow-file layout,
the shipped templates and seeds, the loader (`config_composition.py`), the
run-side copies, and the documents a user is pointed to.

Two claims below were verified by probe rather than by reading
(`.tmp/scratchpad/2026-09-05_1300/`, session-2 worktree); they are marked.

## Verdict

The **shape** is right and should stay: one project file a domain user reads
top to bottom (`project / basin / climate / model / workflows`), one file per
workflow, and a loader that refuses every v1 spelling by name. The R14 design
delivered what it set out to.

The **surface a user actually touches is not yet at that standard.** The
mechanical rewriter (P3/P4) migrated the key spellings and kept every comment,
but a comment stays attached to the key that *preceded* it, so when a key
moved its comment did not. The result is that every template and most seeds
now carry comments that describe a different key, a retired key, or a retired
type. Three commented-out "options" in the project template would be silently
ignored if enabled, and one in each workflow template would be refused. The
supporting documents (`config/templates/README.md`, `config/defaults/README.md`,
`config/advanced_settings.yml` comments) are still written in v1.

None of this is a loader defect. It is a documentation-surface defect that a
domain expert meets on the first page, so it is the thing to fix first.

## 1. Is it user-oriented?

### What works

- **Kind sections, not a bag.** `basin:`, `climate:`, `model:` are the words a
  hydrologist would use. Dissolving `shared:` was the right call.
- **Windows as inclusive years** (`{start, end}`) instead of ISO timestamps.
- **One command to migrate, one message to refuse.** `schema_version` checked
  first; every retired key names its destination. The messages are good.
- **`climate.selected` may be unset while only WF0 runs** (D-10.5). This is
  the workflow's own logic expressed in the config, and it is exactly what a
  first-time user does.
- `docs/guide/configuration.qmd` is the best document in the set: short,
  current, and it explains the two path rules.

### Traps a domain user will hit

| # | Where | What | Verified |
|---|---|---|---|
| T1 | `project_config.template.yml`, `project:` | `#seed: auto`, `#water_year_start: Oct`, `#julia_threads: 4` are offered as project keys. Uncommented, all three are **accepted and read by nothing**: `seed` moved to the stress-test file (C-51), `water_year_start` to `climate:` (C-53), `julia_threads` to `advanced_settings` (C-54). A user who sets `water_year_start: Oct` here gets a January water year and no message. | probe |
| T2 | every workflow file | **No closed schema below the project file's top level.** A misspelled key (`n_realisations: 99`) is accepted and the run proceeds on the default (`n_realizations = 1`). `docs/migration-config-shape.md` says the opposite: "Nothing is silently accepted and defaulted. That is the point of the closed schema." Today that sentence is true only for `schema_version`, the T1 top level, the workflow stanza, and the retired-key table. | probe |
| T3 | `project_config.analyze_projections.template.yml` | `#relative_change:` is still offered. Uncommented it is **refused** (C-66 dissolved it). `reference_window` is annotated `[integer, integer]` (it is a mapping); `future_windows` is annotated "mapping: name -> [..]" (it is a list). The 65-model `models:` list is one 1,400-character line. | read |
| T4 | `project_config.run_stress_test.template.yml` | `#batch_size` / `#batch_size_max` are offered flat; uncommented they are **refused** (C-34 regrouped them under `compute:`). `compute:`, `seed:`, `weathergen_config:` (C-81) and `disk_headroom_gb` (D-7.8 promised a template surface) are absent. `trajectory: transient  # boolean`. | read |
| T5 | `project_config.build_model.template.yml` | `observations:` is annotated "path \| null — needs gauge_points" — it is a per-variable mapping now, and `gauge_points` is retired. The commented `simulation_window` example uses `starttime:` ISO timestamps, which is the v1 type C-71 replaced. Prose refers to `shared.historical_window`. | read |
| T6 | `project_config.template.yml` | The "How much climate record to EXTRACT" comment sits above `basin.output_locations`; it describes `climate.window`. The "list — any of: river discharge …" comment sits under `climate.selected`; it describes `model.outvars`. `climate.selected` is annotated "entry in data_sources" (retired name). `#hydrography` / `#basin_index` are indented under `resolution` rather than under `sources:`. | read |
| T7 | `project_config.template.yml` header vs body | Header lists four renames and says "copy them all"; the body's `workflows:` stanzas still point at `*.template.yml` names, and `analyze_climate` has no `config_path` at all — while a WF0 template ships "for discoverability" (D-7.9). A user cannot tell whether WF0's file is expected. | read |
| T8 | seeds | `project_config_rapid_build_model.yml`: "The model RUN period" comment sits under `observations:`. `project_config_wf2_fast.yml`: the "Kept discharge-only" comment sits under `climate.selected` (it is about `model.outvars`). All four project seeds carry a WF0 stanza comment citing `shared.clim_historical` and `candidate_sources`. The rapid header explains `horizontime_climate`, `run_length`, `run_historical` — all retired. `project_config_baseline_linux.yml` opens "R01 sectioned schema". | read |
| T9 | `config/templates/README.md` | The document the template points at for "why the defaults are what they are" is v1 throughout: `historical_window`, `historical_year_range`, `shared.water_year_start`, a YAML example with `shared.basin.gauge_points` and `observations_timeseries`, `model_build_config`. Same in `config/defaults/README.md` (`workflows.build_model.model_build_config`) and in `config/advanced_settings.yml` comments (`shared.seed`, `shared.water_year_start`), which name the override key a project "MAY" use — the wrong key, twice. | read |

Why the stale-spelling sweep is green anyway: it classifies hits, and comment
text in templates and seeds is evidently in an allowed class. That is the
right policy for `dev/` records and the wrong one for the files a user copies.

### Semantics worth one sentence each in the template

These are design choices, not defects, but a domain user needs them stated
beside the key rather than in a milestone record:

- `simulation_window` exists in **two** files with different meanings: WF1's is
  the historical model run (inside `climate.window`), WF3's is the future
  window the stress test is evaluated over. Same name, different decades.
- `climate.window` is inclusive **water** years; WF2's `reference_window` and
  `future_windows` are **calendar** years (C-74). Only the design says so.
- `basin.output_locations` also controls subbasin delineation (the reason the
  old `gauge_points` was renamed away is not the reason a user cares).
- `basin.region` is a Python dict inside a YAML string. It is hydromt's
  convention, so it stays, but the template should show the two other common
  forms (`{'bbox': [...]}`, `{'geom': path}`).
- `n_levels` counts levels, not steps (C-31); `n_levels: 2` with `min == max`
  is two identical members.

## 2. Footprint — what ships, what a run writes, what can go

### Inventory (tracked)

| Bin | Files | Note |
|---|---|---|
| `test_case/` seeds | 17 | four sets: rapid (5), baseline (4), baseline_linux (4), wf2_fast (4) |
| `config/templates/` live | 5 yml + 2 csv + 1 toml + README | |
| `config/templates/archive/` | 5 yml + README | v1, no `schema_version`; the loader refuses every one |
| `config/catalogs/` | 2 live + 1 generated + index; `archive/` 2 + README | |
| `config/defaults/` | 3 + README | |
| `config/migrations/` | 1 | |

### Inventory (per project, written by a run)

`config/runs/project_config_<wf>.yml` ×4, `config/runs/<wf>/run_record.yml`
×4, `journal.jsonl`, `invocations/*.json`, `README.md`, plus
`config/basin_data/` (2 csv). Each `run_record.yml` embeds `effective_config`,
which is the same projection, sorted the same way, as the composed
`project_config_<wf>.yml` beside it.

### Reduction options, ranked

1. **Drop the `engine:` block from every seed's build-model file and make it
   a commented-out optional in the template.** (Recommended.) `build_model.smk`
   already defaults both paths to the same `config/defaults/` files, so the
   block restates the default in all four sets. Three seed files shrink to
   `observations:` alone. Zero behaviour change; the composed digest changes,
   so the rapid/baseline fixtures re-record once.

2. **Retire the `baseline_linux` set (4 files) together with its catalog.**
   (Recommended.) The Linux catalog is in the hydromt **v0** catalog format
   (`path:` ×86, `kwargs:` ×73; the Windows one has `uri:` ×133 and one
   `kwargs:`), so it cannot load under the pinned `hydromt >=1.3`. The set
   passes `tests/test_cli.py` only because a dry run never opens the catalog.
   Its workflow files have also drifted from the baseline (a different model,
   different windows). Replace with one line in `docs/install.md`:
   `--config project.catalog=<your catalog>` overrides the project file, and
   overrides are validated like T1 content (D-8.6b). Touches
   `tests/test_cli.py`, `tests/test_snake_utils.py`,
   `tests/test_v1_v2_equivalence.py`, `snake_utils.py`, `run_snake_docker.sh`.

3. **Collapse `wf2_fast` to two files by sharing rapid's workflow files.**
   (Recommended over deleting it.) `config_path` may name any file in the
   directory, and the duplicate-path check is per set, so
   `project_config_wf2_fast.yml` can point `build_model` and `run_stress_test`
   at the rapid files and keep only its own `_analyze_projections.yml`. The
   rapid stress file's `experiment_name: experiment_rapid` lands under
   `test_case/test_dev`, so nothing collides. Saves 2 files and, more
   importantly, demonstrates the sharing pattern a real user with several
   experiments on one basin wants. Alternatively delete it outright: rapid
   already runs 2 models × 1 scenario, and wf2_fast's only saving is one model.

4. **One empty WF0 file, not two.** Keep the template (the discoverability
   argument holds once) and drop `test_case/project_config_rapid_analyze_climate.yml`,
   whose comment is stale anyway; the other three seeds already omit it. The
   project template must then decide: either every seed carries the WF0
   stanza with `config_path` or none does. Recommend none — the template's own
   "delete `config_path` and set `enabled: false`" rule already covers it.

5. **Delete `config/templates/archive/` and `config/catalogs/archive/`.**
   No test parses them, the loader refuses them, and git history keeps them.
   Their README already says "expect to reconcile"; since R14 that means
   rewriting from scratch, which is what they were kept to avoid. If a CMIP5 or
   ISIMIP3 run is wanted later, the place to record that is a task note.

6. **Run side: one record per workflow, not two.** (Later; a contract change.)
   `project_config_<wf>.yml` duplicates `run_record.yml`'s `effective_config`.
   The consumer is WF3's consistency guard (`LEAF_WF1_SNAPSHOT`), which could
   read the run record's `effective_config` instead. Saves four files per
   project and removes the "which of these two is the record" question the
   runs README currently spends a section answering. Touches
   `check_project_consistency.py`, `cross_workflow_leaves.py`, three
   Snakefiles, and the baseline tree shape.

After 1–5 the tracked count goes from 17 seeds + 5 archive to 10 seeds + 0,
and the templates stay at 5. The project-file + per-workflow-file layout is
untouched, which is what the owner asked to keep.

## 3. Documentation and code

- **`docs/guide/configuration.qmd`** is current. One gap: it should carry the
  two-files-two-windows sentence and the water-vs-calendar-year sentence above.
- **`docs/migration-config-shape.md`**: the "closed schema" paragraph overstates
  what the loader enforces (T2 above). Either soften it or close the schema.
- **`config/templates/README.md`** needs a v2 rewrite, not a sweep: the
  "why the defaults are what they are" sections are keyed by v1 names.
- **`config/defaults/README.md`** and **`config/advanced_settings.yml`**:
  five v1 key spellings in comments that name the per-project override.
- **`README.md`** §Configuration still says "Each workflow keeps its
  established current config copy" (pre-R13 phrasing) but is otherwise v2.
- **`config_composition.py`**: sound. Two notes. `RELOCATED_KEYS` is
  documented as "P3 owns the decision to absorb or retire"; P3 has landed, so
  the constant is now dead (its only recorded consumers retired with the split
  tool). And the module docstring still names the R13 design as source of
  record while the constants cite R14; one line fixes it.
- **Closing the T2 schema** (T2 above) is the one code change with user-facing
  value. The cheapest form is a per-workflow `frozenset` of accepted top-level
  names beside `T1_SHARED_SECTIONS`, checked in `_check_t2_names`, with the
  same shape of message the stanza closure already uses. `project:`'s leaves
  (`project_dir`, `catalog`) should close the same way, which is what turns T1
  from silent into refused.

## Recommended order

1. Rewrite the five templates by hand against §7 of the R14 design (the design
   text is correct; the templates are not). Fix T1, T3–T7 in the same pass.
2. Sweep the seed comments (T8) and the three READMEs / `advanced_settings`
   comments (T9). Add templates, seeds, `config/*.md` and `advanced_settings.yml`
   comment text to the stale-spelling sweep's *fail* set so this cannot recur.
3. Close the T2 and `project:` schemas (T2), then make the migration note's
   claim true.
4. Footprint options 1–5, one commit each, rapid fixture re-recorded once at
   the end.
5. Option 6 as its own small design note, since it moves a contract surface.
