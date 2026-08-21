# Intake — config-modularization design run

- Run: `config-modularization` · started 2026-08-20 · driver: interactive session (session-2 lane)
- Genre mapping: this is a refactor/architecture design (goal, what-changes,
  alternatives, migration) → recorded as `decision-record`, the nearest genre
  per the status-schema note.
- Ultimate goal (owner-stated): modularizing the toolbox; the config surface
  is the first seam.

## Change request (verbatim, owner, 2026-08-20)

> I would like to improve the design of my configuration files in the
> blueearth_cst. In the current state, roughly we have three tiers of configs:
>
> 1) snake_config.yml: this has project level and shared level configuration +
> workflow-level config parameters.
> 2) model config files, including for wflow: wflow_build_model.yml,
> wflow_update_waterbodies.yml
> 3) advanced_settings.yml, which has advanced configuration parameters that
> the standard user does not need to touch. In addition, we also have data
> catalog ymls at config\catalogs
>
> As my ultimate goal is modularizing the toolbox, I want to brainstorm with
> you on an improved structure. An alternative to the current scheme can be:
>
> 1. One project level config file for project and shared settings, also to
> switch workflows on and off.
> 2. A seperate config (yml) file for each workflow to control their own
> parameters in a seperate space.
> 3. Model specific configuration files (e.g., such as the ones we have for
> wflow).
>
> Advanced configuraton settings can be a sub-section in the relevant config
> files.
>
> A few benefits I can think of is: a) copying all parameters in all workflow
> config snapshots hence dublication - which is sometimes confusing. b) users
> only see/change the workflow settings they want to run - hence cleaner
> interface. On the other hand, the downside is having to maintain more files.

Follow-up rulings from the same dialogue:

> what about workflow or model-specific settings in the advanced_settings.yml?
> would those also go there?

> Yes, but seed, water_year_start, and min_historical_years can also be
> defined under the shared settings. Right?

## Problem

One `snake_config_*.yml` carries `project:` + `shared:` + all four
`workflows.<name>:` blocks. Every variant/project copy duplicates every
workflow's parameters, so copies drift invisibly and users confront settings
for workflows they do not run. The single file is also a coupling point that
works against workflow-as-module modularization — while simultaneously doing
one valuable job: forcing cross-workflow keys into one place.

## Confirmed scoping rulings (owner, 2026-08-20, this dialogue)

1. Adopt three user-facing tiers: (T1) one project config — `project:` +
   `shared:` + per-workflow enable switches; (T2) one config file per
   workflow; (T3) model configs (hydromt/wflow conventions, unchanged).
2. Composition by **path reference**: the project config points at each
   workflow's file (generalizing the existing `model_build_config:` pattern).
   Single `--configfile` CLI contract unchanged. CLI multi-configfile merge
   was considered and rejected (order-dependent merge, wrapper/GUI contract
   churn, `configfiles[0]` forwarding ambiguity).
3. `config/advanced_settings.yml` stays a separate toolbox-level file. Its
   boundary is **authority** (who may change it), not topic: `constraints:`
   and `runtime:` never move into user-editable files; workflow-specific
   entries are namespaced *inside* it as it grows. Folding advanced settings
   into workflow files was considered and rejected.
4. Shared-seam rule: any key read by more than one workflow lives in the
   project file, never in a workflow file — to be **enforced by the loader**,
   not by convention.
5. `shared.seed` and `shared.water_year_start` remain per-project overrides
   of `defaults:`; `min_historical_years` remains a constraint (not
   project-settable). Advanced per-workflow knobs a project may set (e.g.
   `batch_size`) live as optional keys in that workflow's file.

## Constraints

- This repo is the workflow engine only; nothing may couple config design to
  the CST-API/GUI (web-app independence is standing owner policy).
- Model configs stay hydromt / hydromt_wflow / wflow conventions verbatim.
- `get_config` contract preserved: raise on missing required, default for
  optional.
- `workflow.configfiles[0]` forwarding to R scripts preserved.
- Config identity must stay run-stable (Snakemake idempotence; WF3
  experiment freeze/digest) — no per-invocation variation.
- Existing projects need a mechanical migration path (precedent:
  `docs/migration-workflow-names.md`).
- New seed configs under `test_case/` must remain tracked (the
  `snake_config_` gitignore glob, or a deliberate gitignore change).
- No new dependencies without owner approval.

## Decision criteria

1. Single-sourcing of cross-workflow keys survives, enforceable at parse time.
2. Duplication across variant configs and per-project snapshots is eliminated
   or clearly reduced.
3. CLI, wrapper, and R-forwarding contracts unchanged.
4. Migration is mechanical and bounded; a pre/post project runs identically
   (baseline-neutral refactor).
5. The layout advances workflow-as-module modularization.

## Success criteria

An accepted decision-record design specifying: file layout and naming, loader
semantics (path resolution, required/optional, seam enforcement), validation
(incl. cross-file checks like simulation_window ⊂ historical_window),
snapshot and digest behavior, template/`test_case` restructuring, migration
plan, and validation gates — ready for `task-brief` handoff.

## Non-goals

- Implementation (separate task-brief after acceptance).
- Changing what any workflow computes, or any model-config semantics.
- Moving `constraints:`/`runtime:` into project space.
- Data-catalog redesign (`config/catalogs/` stays as is).
- Web GUI/API accommodations.

## Derived-artifact register

Author spawns are barred from touching these; each is regenerated from the
accepted design after G2, by the implementation task unless noted.

| Artifact | Regeneration |
|---|---|
| `config/templates/snake_config.template.yml` (+ any new per-workflow templates) | implementation |
| `test_case/snake_config_rapid.yml`, `_baseline.yml`, `_baseline_linux.yml`, `_wf2_fast.yml` | implementation |
| `config/defaults/README.md`, `config/templates/README.md`, `docs/` config references, `README.md`, `AGENTS.md` config sections | implementation (keep-references-current rule) |
| `dev/roadmap.md` status line | driver, at stage-7 landing |
| Board note under `dev/tasks/` | driver, once session-1's lane frees `dev/tasks` scope |
| Implementation `task-brief` | stage-7 handoff |

## Evidence register

Verified 2026-08-20 against this worktree (branch `docs/config-modularization`,
base 5363f53) by a read-only verification agent; driver spot-checked the
design-critical rows. Columns: premise / source / observation / precision /
reproduction / confidence.

| # | Premise | Source | Exact observation | Precision | Reproduction | Confidence |
|---|---|---|---|---|---|---|
| E1 | Each Snakefile reads only `project:` + `shared:` + its own `workflows.<name>:` | four `.smk` files; `blueearth_cst/shared/snake_utils.py:595-627` | **REFUTED for WF3, and a 4th top-level section exists.** `run_stress_test.smk:345-346` digests `workflows.build_model` + `workflows.analyze_projections` as opaque blobs; `:537-540` reads the *meaning* of `workflows.build_model.wflow_outvars` (own comment `:508-510` calls it the first such dependency); `provenance.py:208-212` raises `KeyError` at parse time if `workflows.analyze_projections` is absent. `run_stress_test.smk:530` → `surface_axes.py:387` reads top-level `reporting:`. WF0/1/2 read only their own sections. `get_config` contract as documented (present key returned as-is incl. `None`; absent+required raises; absent+optional returns default) | file:line reads | grep both `config["workflows"]` forms across `*.smk` | high |
| E2 | `advanced_settings.yml` closed-schema load + `shared.*` overrides | `snake_utils.py:861-1036` (load at import, `FileNotFoundError` if absent), schema `:870-879` | Two DISTINCT override mechanisms: call-site default (`julia_threads`, `build_model.smk:102`) vs resolver substitution on `None` (`seed` `:1134-1151`, `water_year_start` `:1167-1171`). Consequence: explicit `seed: null` falls back to the default, but `julia_threads: null` raises at parse (`_positive_int(None)`, `:886-892`). `seed: auto` → `zlib.crc32(name) % 2**31` (`:1111-1131`) | file:line reads | read `snake_utils.py` | high |
| E3 | Project snapshot records referenced configs by git blob id, copies only irrecoverable ones | `blueearth_cst/model/copy_config_files.py` (rule 1.01, `build_model.smk:463-489`) | Copy decision `:293-306`: tracked+clean blob → record `git_blob`, no copy; `_tracked_blob:351-383` returns None (→ copy) on any non-confident answer. Exception: `ALWAYS_ARCHIVED_ROLES = {output_locations, observations_timeseries}` (`:44`) are always copied to `config/basin_data/` | file:line reads | read module | high |
| E4 | `suggest_experiment_name.py` edits config as text | `scripts/suggest_experiment_name.py:21-27,64-224` | Line-based splice; `yaml.safe_load` only to read and verify; `safe_dump` absent from the file | file:line reads | grep safe_dump | high |
| E5 | `workflow.configfiles[0]` forwarded as `config_path` to R scripts | all four `.smk` (`analyze_climate.smk:47`, `build_model.smk:41`, `analyze_projections.smk:34`, `run_stress_test.smk:29`) | **Forwarded to PYTHON scripts, not R** (`build_model.smk:467`, `analyze_climate.smk:344`, `analyze_projections.smk:836`, `run_stress_test.smk:621,888`). The two R invocations (`run_stress_test.smk:944,982`) receive the *generated* `weathergen_config.yml`. Snakefile comments claiming R-forwarding (`build_model.smk:38-40`, `analyze_projections.smk:31-33`) are stale. Hazard noted: with two `--configfile` args, `config` reflects the merge but `config_path`/`file_sha256(config_path)` reflect only the first — evidence for the rejected multi-file alternative | file:line reads | grep config_path per smk | high |
| E6 | WF3 has one effective-config digest / experiment freeze | `shared/provenance.py`, `experiment/write_experiment_config.py`, `run_stress_test.smk` | THREE distinct mechanisms: (1) `effective_config_digest` (`provenance.py:266-280`, doc `:221-263`) over `project`, `shared`, `workflows.{analyze_projections,build_model,run_stress_test}` + advanced settings; excludes `reporting:` by construction (`run_stress_test.smk:526-529`); (2) experiment freeze = VALUE comparison vs recorded `experiment.yml`, covering only `{experiment_name, run_stress_test}` (`write_experiment_config.py:47-52,63-140`), armed after the first successful run; (3) drift-guard sha256 over 4 sections as a rule-3.01 rerun trigger (`run_stress_test.smk:340-352`); `config_path` deliberately not a guard param (`:330-331`). Nothing in `experiment/allocate.py` hashes config | file:line reads | grep digest/hashlib in experiment/ | high |
| E7 | Wrapper reads `workflows.<name>.enabled`, same `--configfile` for all | `scripts/run_workflows.py:282-314,371-386` | Missing/non-mapping/non-bool `enabled` are hard `ConfigError`s; all four sections required; one `config_path` reused per invocation; plus `_check_wf1_leaves` guard (`:352-368`) | file:line reads | read module | high |
| E8 | `simulation_window` ⊂ `historical_window` validated | `snake_utils.py:1322-1399`; called `build_model.smk:95` | Containment raise at `:1388-1398`; absent key → passthrough of `historical_window`; `MIN_HISTORICAL_YEARS` deliberately NOT applied to the simulation window (`:1347-1350`) | file:line reads | read function | high |
| E9 | `test_case/` seed configs tracked only via `snake_config_*` glob | `.gitignore:137-141` | `test_case/*` + `!test_case/snake_config_*.yml`; DEMONSTRATED via `git check-ignore`: `snake_config_new_seed.yml` not ignored; `my_seed.yml` ignored; `snake_config.yml` (no trailing underscore) ALSO ignored | demonstrated | `git check-ignore -v <name>` | high |
| E10 | In-repo precedent for config-referenced YAML parsed by our own code | `prepare_build_config.py:113-135`, `setup_reservoirs_lakes_glaciers.py:119` | `model_build_config` is read from the main config, parsed, cross-checked against `shared.basin.*` and re-emitted — a real precedent. `weathergen_config.yml` is NOT one: its path is hardcoded (`run_stress_test.smk:870,889`) | file:line reads | read modules | high |

**Constraint amendments following from E1/E5/E6** (facts, not design):

- Any per-workflow split must keep `workflows.build_model` and
  `workflows.analyze_projections` content resolvable from WF3's parse context
  (identity digests + `wflow_outvars` + the parse-time projection paths), and
  must state where top-level `reporting:` lives in the new layout.
- The preserved forwarding contract is `config_path` → downstream **Python**
  scripts (and `file_sha256(config_path)` provenance); the R-forwarding wording
  earlier in this intake's Constraints section and in Snakefile comments is
  stale.
- All three identity mechanisms in E6 must be specified against the new layout
  (what is hashed/compared when sections live in referenced files).

## Gate-materialization check

Verified runnable in this worktree, 2026-08-20:

- `pytest tests/test_cli.py` — **runnable** (file present); the parse-time gate:
  dry-runs all four entry points, the only place a malformed defaults YAML
  surfaces today.
- `pixi run test-fast` / `pixi run test-full` — **runnable** (pixi.toml:149,151).
- `pixi run tree-check` — **runnable** (pixi.toml:185, pinned to the baseline
  config).
- `check_baseline.py check` + `dev/baseline/manifest.json` — **runnable**;
  pre-change artifact EXISTS (manifest recorded; `test_case/test_local` fixture
  present, seed-refreshed at claim 2026-08-20). This is the no-drift gate: the
  config refactor claims output-neutrality, and the baseline is what falsifies
  that claim. **Thin** in the known, accepted way: covers data targets, not
  figures/staticmaps (recorded repo policy).
- Migration-shaped risk (schema rename): `test_cli` dry-runs cover parse; the
  fixture-dependent test layer exists in this worktree (seeded). A stale-path
  sweep (grep for old key spellings) is a cheap additional gate the design's
  migration plan should name.


## Scope amendment (owner, 2026-08-20, post-stage-0, pre-G1)

Owner request, verbatim:

> Can we wire the design-v1.md as a revision milestone, e.g., R12. I would
> like to also reconsider the naming of the workflows, which I believe can go
> into this bucket

Driver fact-check and resulting rulings:

1. **Milestone wiring — R13, not R12.** `dev/roadmap.md:1462` already assigns
   R12 to "WF3 execution model" (OPEN, G2 ratified 2026-08-08) and
   `dev/milestones/r12/` holds that milestone's live design chain. This work
   therefore becomes **R13**. Consequences: the accepted design lands at
   `dev/milestones/r13/` (per the "new milestones get a folder there" rule,
   `dev/README.md`); `dev/roadmap.md` gains an R13 entry at landing;
   `dev/milestones/README.md` gains its index row at seal. The run dir and
   task branch keep the `config-modularization` slug.
2. **Workflow naming is IN SCOPE.** The design must add a workflow-naming
   section that: (a) evaluates the current names (`analyze_climate` wf0,
   `build_model` wf1, `analyze_projections` wf2, `run_stress_test` wf3 — and
   the separate `wfN` id scheme, `dev/reference/naming.md` §9); (b) proposes
   2–3 candidate naming schemes with ONE recommendation and its rationale —
   including the legitimate option "keep the current names"; (c) accounts for
   every load-bearing surface a rename touches (the four `*.smk` filenames,
   the `workflows.<name>` config keys, the T2 per-workflow config filenames
   this same design introduces, `scripts/run_workflows.py`'s
   `WORKFLOW_ORDER`/`SNAKEFILE` map, log/DAG naming, docs, tests); and
   (d) weighs the cost honestly against the 2026-08-14 rename precedent
   (`docs/migration-workflow-names.md`) — a second rename six days after the
   first must buy something real, and the coupling argument (one combined
   migration with the config split, instead of two breaks) is the reason it is
   in this bucket at all.
3. **The naming CHOICE is an owner ruling.** The design recommends; the owner
   rules at G1 (provisional) and G2 (final). Reviewers press on the
   recommendation like any other decision.

Derived-artifact register additions (same bar: author spawns do not touch):

| Artifact | Regeneration |
|---|---|
| `dev/roadmap.md` R13 entry | driver, at stage-7 landing |
| `dev/milestones/README.md` index row | at milestone seal (post-implementation), not this run |
| `docs/migration-workflow-names.md` successor / extension | implementation, if a rename is ruled |
