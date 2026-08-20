# R13 — Config modularization: Design (DRAFT v1)

> **Status: DRAFT v1** — not yet reviewed; awaiting human gate **G1**
> (framing approval). No ledger, no review record, no external round yet.
> **Milestone:** R13 (config surface as the first modularization seam).
> R12 is taken by the open WF3 execution-model milestone (`dev/roadmap.md:1462`),
> so this work is R13 per the scope amendment. The accepted design lands at
> `dev/milestones/r13/`; the run directory keeps the `config-modularization` slug.
> **Genre:** decision-record (milestone design), per the repo's
> `dev/milestones/*/ *-design.md` house style.
> **Author role:** cst-architect. **Run:** `config-modularization`.
> **Scope authority:** `dev/working/design-runs/config-modularization/intake.md`
> — its five *Confirmed scoping rulings* and its *Scope amendment* are fixed
> anchors and are not reopened here.
> **Structure precedent:** `dev/milestones/p33/performance-passes-design.md`
> (ACCEPTED 2026-07-24).
> **Body budget:** 1100–1400 lines, set from the measured house range of
> accepted designs in this repo (300–2946 lines, median ~1200; `wc -l
> dev/milestones/*/*-design.md`). A revision that would grow the body by
> accretion relocates superseded text into the review record instead.
> This document is self-contained: a reviewer needs only this file plus the
> cited paths.

---

## 1. Problem statement

One `snake_config_*.yml` carries `project:` + `shared:` + all four
`workflows.<name>:` blocks + a top-level `reporting:`. Every project copy and
every shipped variant therefore duplicates every workflow's parameters,
including the workflows that project will never run: `snake_config_wf2_fast.yml`
exists solely to iterate WF2 and still carries full `analyze_climate`,
`build_model` and `run_stress_test` sections. The duplication is not only in the
source tree — it is baked into each project's own record, where the three
snapshots `config/runs/snake_config_build_model.yml`,
`config/runs/snake_config_analyze_projections.yml` and
`experiments/<exp>/config/snake_config_run_stress_test.yml` are **byte-identical
whole-config copies**, all three carrying SHA-256 `00ef44f7fef2…` in
`dev/baseline/manifest.json:9-30` (N5). The single file is also the coupling
point that works hardest against workflow-as-module modularization, while
simultaneously doing one valuable job that must survive any split: forcing
cross-workflow keys into one place where they cannot disagree.

This design restructures that surface into a project config (T1) that references
one config file per workflow (T2) by path, leaves the model configs (T3)
untouched, keeps `config/advanced_settings.yml` a separate authority-bounded
toolbox file, and enforces the single-sourcing rule in the loader rather than by
convention.

## 2. Goals / Non-goals

### Goals

- **G1** — three user-facing tiers as ruled: T1 project config, T2 one file per
  workflow referenced by path, T3 model configs unchanged.
- **G2** — the shared-seam rule (`a key read by more than one workflow lives in
  T1`) enforced at parse time, so `pytest tests/test_cli.py` is its gate.
- **G3** — output neutrality: a pre-migration and post-migration project run
  produce identical DATA targets. The three config-snapshot targets are the
  single declared exception (§16).
- **G4** — the CLI, wrapper, and `config_path`-forwarding contracts unchanged.
- **G5** — a mechanical, bounded migration for existing projects, with a
  parse-time error that names the migration document.
- **G6** — a workflow-naming recommendation with its full surface inventory
  (scope amendment §2), decidable by the owner at G1/G2 without reopening
  anything else in this design.

### Non-goals

- Implementation. This design hands off as a `task-brief` after G2.
- Changing what any workflow computes, or any model-config semantics.
- Moving `constraints:` / `runtime:` into project space.
- Data-catalog redesign — `config/catalogs/` stays exactly as it is.
- Web GUI/API accommodations; CST-API and CST-frontend never constrain this repo.
- Splitting `config/advanced_settings.yml` into per-workflow FILES. Its interior
  organization is in scope (§13); its file identity is not.

## 3. Constraints (standing; restated)

- This repo is the workflow engine only. Nothing couples config design to the
  CST-API/GUI.
- Model configs stay hydromt / hydromt_wflow / wflow conventions verbatim.
- The `get_config` contract is preserved verbatim: present key returned as-is
  including `None`; absent + required raises `ValueError`; absent + optional
  returns the default (E1).
- `workflow.configfiles[0]` forwarding is preserved. The preserved contract is
  `config_path` → downstream **Python** scripts and `file_sha256(config_path)`
  provenance; the R-forwarding wording in the Snakefile comments is stale (E5).
- Config identity must stay run-stable — no per-invocation variation (Snakemake
  idempotence; the WF3 experiment freeze and drift guard).
- Existing projects need a mechanical migration path.
- New seed configs under `test_case/` must remain tracked: the
  `!test_case/snake_config_*.yml` glob, or a deliberate `.gitignore` change (E9).
- No new dependencies. This design adds none — PyYAML and `pathlib` are already
  the loader's whole toolkit.

## 4. Decision criteria

Carried verbatim from the intake; every decision below is answerable against them.

1. Single-sourcing of cross-workflow keys survives, enforceable at parse time.
2. Duplication across variant configs and per-project snapshots is eliminated or
   clearly reduced.
3. CLI, wrapper, and forwarding contracts unchanged.
4. Migration is mechanical and bounded; a pre/post project runs identically
   (baseline-neutral refactor).
5. The layout advances workflow-as-module modularization.

## 5. Settled framing (owner rulings — not reopened)

Restated so this document is self-contained. Sources: intake *Confirmed scoping
rulings* 1–5 and *Scope amendment* 1–3.

| # | Ruling |
|---|---|
| **S1** | Three user-facing tiers: T1 project config (`project:` + `shared:` + per-workflow enable switches), T2 one config file per workflow, T3 model configs unchanged. |
| **S2** | Composition by **path reference** from T1, single `--configfile` CLI contract unchanged. CLI multi-configfile merge considered and rejected (§17.1). |
| **S3** | `config/advanced_settings.yml` stays a separate toolbox-level file. Its boundary is **authority**, not topic; `constraints:` and `runtime:` never move into user-editable files; workflow-specific entries are namespaced *inside* it as it grows. |
| **S4** | Shared-seam rule: any key read by more than one workflow lives in T1, never in a T2 file — **enforced by the loader**, not by convention. |
| **S5** | `shared.seed` and `shared.water_year_start` remain per-project overrides of `defaults:`; `min_historical_years` remains a constraint. Advanced per-workflow knobs a project may set live as optional keys in that workflow's T2 file. |
| **S6** | This is milestone **R13**. Workflow naming is in scope: candidates + one recommendation (§14); the choice itself is an owner ruling at G1/G2. |

Two questions the intake leaves **open**, decided here and argued rather than
assumed: where top-level `reporting:` lives (§10.4, decided: the WF3 T2 file,
hoisted by the loader) and backward compatibility versus a clean break (§15.1,
decided: clean break with a parse-time migration error).

## 6. Empirical premises

### 6.1 Carried from the intake's evidence register

Cited by row; **not re-derived here**. E1 (per-Snakefile section reads, WF3's
cross-section reads, the `get_config` contract), E2 (advanced-settings closed
schema and the two distinct override mechanisms), E3 (snapshot records by git
blob id, copies only irrecoverable files, `ALWAYS_ARCHIVED_ROLES`), E4
(`suggest_experiment_name.py` edits config as TEXT), E5 (`config_path` forwarded
to Python, not R; the two-configfile hazard), E6 (the three config-identity
mechanisms), E7 (wrapper `enabled` validation), E8 (`simulation_window` ⊂
`historical_window`), E9 (the `test_case/` tracking glob, demonstrated), E10
(`model_build_config` as the in-repo path-reference precedent).

### 6.2 New premises verified for this design

Each verified in this worktree on 2026-08-20 by direct read; file:line given so
a reviewer can re-check without re-deriving.

| # | Premise | Citation | Why it matters |
|---|---|---|---|
| **N1** | `config_path` is a declared rule **input**, not merely a param, in five rules: `analyze_climate.smk:344` (`snapshot_config`), `build_model.smk:467` (`snapshot_config`), `build_model.smk:535` (`prepare_spatial_maps`), `analyze_projections.smk:836` (`snapshot_config`), `run_stress_test.smk:621` (`snapshot_config`), `run_stress_test.smk:836` (`prepare_stress_test_grid`, under `ancient()`). | as cited | The source config file is a DAG edge. If T2 files are not declared inputs wherever T1 is, editing a workflow's own config stops retriggering the rules that consume it. |
| **N2** | `prepare_weagen_config.py:89-91` re-reads the source config **from disk** (`read_yml(snake_config_path)`) and indexes `yml_snake["workflows"]["run_stress_test"]` for `realizations_num` and the two `stress_test.*.transient_change` flags — it does not use Snakemake's parsed `config`. The path arrives as `params: snake_config = config_path` (`run_stress_test.smk:888`). | as cited | The one consumer that would silently see a T1 file with no workflow settings in it. |
| **N3** | The project snapshot is a **verbatim byte copy** of the single source file: `copy_config_files.py:222` `shutil.copyfile(source_config_path, current_config_path)`. `_RUNS_README` (`copy_config_files.py:60-93`) documents the resulting byte-identity as expected and calls the per-workflow filename a promise the content does not keep. | as cited | Under a split, one byte copy no longer captures what the run used. |
| **N4** | Path keys resolve against the **current working directory** (the repo root under `pixi run`), not against the config file: `test_case/snake_config_rapid.yml:17` states it, and `build_model.smk:125-126` derives the model-config defaults as `f"{static_dir}/defaults/…"` with `static_dir: config`. | as cited | Fixes the T2 path-resolution rule by consistency rather than by preference. |
| **N5** | The three in-project config snapshots are byte-identical: `dev/baseline/manifest.json:9-30` records SHA-256 `00ef44f7fef2b9d2be44d5c64ec9bf0d7aedadff663bdbf4748ad6e053b88381` for all three of `config/runs/snake_config_analyze_projections.yml`, `config/runs/snake_config_build_model.yml`, and `experiments/experiment/config/snake_config_run_stress_test.yml`. They are `type: yaml` targets fingerprinted by sha256. | as cited | Proves the snapshot duplication empirically, and pins exactly which baseline targets this refactor may move (§16). |
| **N6** | The WF3 drift guard compares each guarded section against the snapshot of the workflow that **owns** it: `check_project_consistency.py:166-182` reads `project`, `shared.basin` and `workflows.build_model` from the wf1 snapshot, and `workflows.analyze_projections` from the wf2 snapshot **only when that snapshot exists** (absent → unchecked and logged). | as cited | Determines what a composed snapshot must contain, per workflow. |
| **N7** | Measured divergence across the four shipped seed configs: all four `workflows.<name>` sections differ between `snake_config_rapid.yml` and `snake_config_baseline.yml`; `snake_config_baseline_linux.yml` differs from `snake_config_baseline.yml` in `project`, `shared` **and** `workflows`. | `python -c` diff of the four `test_case/snake_config_*.yml`, 2026-08-20 | The seed set has no free T2 sharing today, which bounds what criterion 2 may honestly claim (§18). |
| **N8** | `prepare_cst_parameters.py:162-165` likewise re-reads the source config **from disk** (`open(config_fn)`) and indexes `yml["workflows"]["run_stress_test"]["stress_test"]`. The path arrives as `input.config` (`prepare_cst_parameters.py:265` ← `run_stress_test.smk:836`). Its `:250-251` fallback deriving `lookup_fn` from `os.path.dirname(config_fn)` is reached only outside Snakemake. | as cited | The second consumer that would see a T1 file with no workflow settings in it. |

## 7. Target layout — T1, T2, T3

### 7.1 D-7.1 — T1, the project config

One file, the sole `--configfile` target. Three top-level sections, unchanged in
name and meaning:

```yaml
project:                       # unchanged
  project_dir: test_case/test_rapid
  static_dir: config
  data_sources: config/catalogs/deltares_data.yml
  data_sources_climate: config/catalogs/cmip6_data.yml

shared:                        # unchanged, plus the cross-workflow keys S4 pulls up
  basin: {...}
  historical_window: {...}
  clim_historical: era5
  # OPTIONAL overrides of config/advanced_settings.yml `defaults:`, shown here
  # for SHAPE ONLY. None of the four shipped seeds sets them, and the migration
  # must add no key the source config did not have — see the note below.
  seed: 123
  water_year_start: Jan
  julia_threads: 4

workflows:                     # SHAPE CHANGES: each block is now exactly two keys
  analyze_climate:
    enabled: true
    config_path: config/workflows/analyze_climate.yml
  build_model:
    enabled: true
    config_path: config/workflows/build_model.yml
  analyze_projections:
    enabled: true
    config_path: config/workflows/analyze_projections.yml
  run_stress_test:
    enabled: true
    config_path: config/workflows/run_stress_test.yml
```

Each `workflows.<name>` block carries a **closed schema of exactly two keys**:
`enabled` (required, must parse to a bool — E7's existing validation, unchanged)
and `config_path` (required when the workflow is loaded; see §8.3). Any third key
is rejected at parse time. That closure is doing three jobs at once: it is half
the seam enforcement (§9), it is the migration detector (§15.2), and it is what
keeps a T1 from quietly growing back into today's file.

**The migration adds no key, anywhere.** The three optional `shared:` overrides
above are illustrative. `effective_config_document` digests the config *mapping*,
so a key that is **present** rather than absent changes the canonical JSON and
therefore `effective_config_digest`, even when the resolved value is identical
(E2's resolver-substitution path makes `seed: 123` and an omitted `seed` produce
the same run and different digests). Adding one during migration would break
§16's digest-equality test and, through `_frozen_differences`' key-union diff,
refuse every already-run experiment in the project. This is the same invariant
D-10.1 states for `enabled` / `config_path`, applied to `shared:`: **composition
moves keys between files; it never creates or drops one.**

`config_path` is named per `dev/reference/naming.md`'s `_path` rule for path-valued
keys. It collides in prose with the Snakefile-local Python variable `config_path`
(the `--configfile` path); §19 Q1 records the alternative spelling.

### 7.2 D-7.2 — T2, one file per workflow

A T2 file's **top level is the workflow's own section body** — today's
`workflows.<name>:` block with `enabled:` removed and two levels of indentation
stripped. Nothing is renamed and nothing changes meaning:

```yaml
# config/workflows/build_model.yml
model_build_config: config/defaults/wflow_build_model.yml
waterbodies_config: config/defaults/wflow_update_waterbodies.yml
wflow_outvars: ['river discharge', 'actual evapotranspiration', 'groundwater recharge']
observations_timeseries: test_case/test_data/observations_timeseries.csv
simulation_window:
  starttime: "2010-01-01T00:00:00"
  endtime:   "2016-12-31T00:00:00"
```

Bare rather than wrapped (`build_model:` at the T2 top level) because the bare
form is the whole point of the user-facing win: the file a user opens to change
WF1 contains WF1's settings at column zero and nothing else. The wrapped form
buys a redundant self-identification that the T1 reference already supplies, and
would make every key one level deeper than it is today for no reader's benefit.

**One exception, declared:** the WF3 T2 file also carries a top-level
`reporting:` key, which the loader hoists back to `config["reporting"]` rather
than merging into `workflows.run_stress_test`. See D-10.4 — it is a two-line
closed map in the loader, not a general mechanism.

### 7.3 D-7.3 — T3, model configs unchanged

`config/defaults/wflow_build_model.yml` and
`config/defaults/wflow_update_waterbodies.yml` are untouched in name, location,
content and semantics. They are already referenced by path from the workflow
section (`model_build_config:`, `waterbodies_config:`), which is precisely the
pattern S2 generalizes (E10), and they keep resolving through
`build_model.smk:125-126`'s `static_dir` fallback. `config/catalogs/` is
likewise untouched.

### 7.4 D-7.4 — Filenames, derived mechanically from the workflow key

Both shipped-file families derive from the `workflows.<name>` key by a single
transform, so any future workflow rename (§14) is one mechanical sweep rather
than a per-file judgement:

| Family | Pattern | Example |
|---|---|---|
| Shipped seed T1 | `test_case/snake_config_<variant>.yml` | `test_case/snake_config_rapid.yml` *(unchanged)* |
| Shipped seed T2 | `test_case/snake_config_<variant>_<name>.yml` | `test_case/snake_config_rapid_build_model.yml` |
| Shipped template T1 | `config/templates/snake_config.template.yml` *(unchanged path, rewritten content)* | — |
| Shipped template T2 | `config/templates/snake_config.<name>.template.yml` | `config/templates/snake_config.build_model.template.yml` |
| A real project's T2 | recommended `<project>/config/<name>.yml`; any path the project likes | — |

The seed T2 pattern sits **inside** the E9 glob: `!test_case/snake_config_*.yml`
matches `snake_config_rapid_build_model.yml`, so the files are tracked with **no
`.gitignore` change**. **Demonstrated**, not inferred (2026-08-20, this worktree):
`git check-ignore -q test_case/snake_config_rapid_build_model.yml` exits 1 — not
ignored — identically to the known-tracked `test_case/snake_config_rapid.yml`,
while `test_case/my_seed.yml` exits 0. This reproduces E9's method on the exact
new name. A `test_case/workflows/` subdirectory was rejected for the reason
E9 records for the basin CSVs: git cannot un-ignore a file whose parent directory
is excluded, so a subdirectory would cost three more `.gitignore` lines to buy
tidiness the flat form does not need.

**Cost, stated plainly:** the shipped seed set grows from 4 files to 4 T1 files
plus up to 16 T2 files. N7 measured that no two of the current variants share a
workflow section verbatim, so the implementation cannot collapse them today
purely by inspection. The implementation brief must (a) reconcile the variants
where a difference is incidental rather than deliberate, and (b) point several
T1 files at one shared T2 wherever they then agree — the reconciliation itself is
worth doing, since an incidental difference between two seed configs is exactly
the invisible drift this design exists to stop. §18 records the residual file
count as an accepted cost.

## 8. Loader semantics

All of this lands in `blueearth_cst/shared/snake_utils.py`, beside `get_config`
and the advanced-settings loader, and is exercised at Snakefile parse time.

### 8.1 D-8.1 — The composition invariant

> **The loader merges T1 and the loaded T2 files into a `config` dict whose
> shape is identical to today's.** `config["workflows"]["run_stress_test"]`,
> `config["shared"]["basin"]`, `config["reporting"]` and every other access path
> resolve exactly as they do now, to exactly the same values.

This single invariant is the backbone of the whole design. Because it holds,
`effective_config_digest` (E6.1), `guarded_sections_digest` (E6.3), the
experiment freeze (E6.2), `resolve_simulation_window(shared_cfg, model_cfg)`
(E8), `parse_surfaces(config)` and every `get_config(...)` call site are
unchanged **by construction** — same inputs, same outputs, same bytes hashed.
Criterion 4's output neutrality follows from it rather than being argued
mechanism by mechanism. §10 exists only to name the four places where something
other than the in-memory dict is at stake — a file's bytes, a DAG edge, or a
disk re-read — because those are the only places the invariant does not answer.

Every deviation from shape preservation is therefore a design defect unless
explicitly listed. Exactly one is listed, and it is a *narrowing*, not a
reshaping: for a single-entry-point invocation the merged `config` carries only
the workflow sections that entry point requires (§8.3), so `config["workflows"]`
may hold fewer than four sections. §10.5 shows that no reader is affected,
because every reader is already scoped by `CONFIG_PROJECTION` or by
`guarded_sections`.

### 8.2 D-8.2 — Where composition happens

Each Snakefile keeps its existing two lines and gains one:

```python
config_path = workflow.configfiles[0]          # unchanged (E5)
config = compose_config(config, config_path, entry="build_model")
```

`compose_config` is a pure function of (parsed T1 mapping, T1 path, entry
workflow name). It returns the merged mapping and, as a module-level side
product the Snakefile also binds, `WORKFLOW_CONFIG_PATHS: dict[str, str]` — the
resolved absolute-or-CWD-relative path of every T2 file it loaded. That dict is
what §10.2 declares as rule inputs and what §11 hands to the snapshot writer.

It runs **before** any other module-level code in the Snakefile, so every
existing parse-time refusal (`refuse_retired_experiment_keys`,
`refuse_out_of_domain_multipliers`, `resolve_simulation_window`,
`parse_surfaces`) sees the composed dict and needs no change.

### 8.3 D-8.3 — Which T2 files are required

**Not** "required iff `enabled: true`". WF3 reads two other workflows' sections
regardless of whether those workflows are enabled: `provenance.project_config`
raises `KeyError` at parse time when a declared projection path is absent
(`provenance.py:208-212`, cited by E1), and `run_stress_test.smk:537-540` reads
the *meaning* of `workflows.build_model.wflow_outvars` to derive the indicator
tables before the DAG is built. The rule is therefore:

> A T2 file is **required** for entry point `W` iff its workflow is in
> `R(W) = {W} ∪ {the workflows named in W's CONFIG_PROJECTION and
> guarded_sections}`. Enablement does not enter into it.

| Entry point | `R(entry)` | Source |
|---|---|---|
| `analyze_climate` (wf0) | `{analyze_climate}` | `analyze_climate.smk:119` |
| `build_model` (wf1) | `{build_model}` | `build_model.smk:176` |
| `analyze_projections` (wf2) | `{analyze_projections}` | `analyze_projections.smk:57` |
| `run_stress_test` (wf3) | `{run_stress_test, build_model, analyze_projections}` | `run_stress_test.smk:332-335, 362-366` |

`R(W)` is **derived, never restated.** `compose_config` computes it from the
same `CONFIG_PROJECTION` / `guarded_sections` declarations the Snakefile already
maintains — passed in, not duplicated — for exactly the reason
`run_stress_test.smk:355-361` gives for deriving `CONFIG_PROJECTION` from
`guarded_sections`: a restated list drifts the first time the original gains an
entry.

Workflows **outside** `R(entry)` are not loaded at all. Their T1 stanza must
still be present and well-formed (E7 requires all four sections with a bool
`enabled`, and the wrapper reads T1 only), but their `config_path` is neither
resolved nor read. A project that never runs WF0 therefore does not need a WF0
T2 file on disk — which is the "users only see the workflow settings they want
to run" benefit, made real rather than cosmetic.

### 8.4 D-8.4 — Path resolution

A `config_path` value is `os.path.expanduser`-ed, then, if still relative,
resolved **against the current working directory** — the repo root under
`pixi run`, which is where Snakemake is invoked. Absolute paths are used as
given.

This is not a preference: it is the rule every other path key in the same file
already follows (N4), including `project.data_sources`, `shared.basin.gauge_points`,
`workflows.build_model.model_build_config` and `project.project_dir`. Resolving
T2 paths relative to the T1 *file* would make two path keys sitting three lines
apart resolve against different roots, which is the kind of split that produces a
support question rather than a convenience. `expanduser` is a deliberate small
superset: a `~`-prefixed path cannot work at all today, so admitting it removes a
failure mode without changing any existing resolution.

**Failure behavior**, mirroring `get_config`'s fail-loud stance and
`run_workflows.py:270-274`'s existing message shape:

| Condition | Behavior |
|---|---|
| `config_path` absent for a workflow in `R(entry)` | `ValueError` naming `workflows.<name>.config_path` and the migration doc |
| file not found | `ValueError` giving the resolved absolute path and stating that a relative path resolves against the current directory |
| file parses to something other than a mapping | `ValueError` naming the file |
| file is empty / parses to `None` | Accepted as `{}`. A workflow whose keys are all optional (WF0, E-rapid comment) legitimately has an empty config, and rejecting it would force a placeholder key |
| any key of `workflows.<name>` other than `enabled` / `config_path` | `ValueError` naming the key and the migration doc (§15.2) |
| the same `config_path` referenced by two workflows | `ValueError`. Two workflows sharing one settings file would silently give each the other's keys, and the seam rule (§9) would then have nothing to test against |

All of these raise at Snakefile parse time, before the DAG is built, so
`pytest tests/test_cli.py` — which dry-runs all four entry points — is their
gate. That is the same gate the repo's other parse-time refusals already use
(`run_stress_test.smk:518`, `:535`).

## 9. Shared-seam enforcement (S4)

The rule is: *a key read by more than one workflow lives in T1, never in a T2
file*. Convention cannot enforce it — the intake's ruling 4 says so explicitly —
and a full key registry would be a second source of truth that drifts from the
Snakefiles. The mechanism is three closed checks, all at parse time, generalizing
the in-repo precedent of `_ADVANCED_SETTINGS_SCHEMA` (E2), which is closed
precisely so a typo fails loudly instead of silently keeping a built-in value.

**D-9.1 — Closed T1 workflow stanza.** `workflows.<name>` admits exactly
`{enabled, config_path}` (§7.1). This is the enforcement in the T1→T2 direction:
a workflow setting cannot be left in, or moved back into, T1.

**D-9.2 — Rejected-key set per T2 file.** `compose_config` rejects, in any T2
file, any top-level key that names a T1-owned section or a T1-owned shared key.
The rejected set is derived from T1 itself plus one small frozen list, not
hand-maintained per workflow:

```
REJECTED_IN_T2 = {"project", "shared", "workflows", "enabled"}
                 ∪ set(t1["shared"].keys())
                 ∪ SHARED_SEAM_KEYS
```

`SHARED_SEAM_KEYS` is the frozen set of names that belong to `shared:` whether or
not the current T1 happens to declare them — `basin`, `historical_window`,
`clim_historical`, `seed`, `water_year_start`, `julia_threads`. It exists because
deriving the set from T1 alone has a hole: a T1 that omits the optional
`shared.seed` would not reject a `seed:` planted in a T2 file, which is the exact
failure the rule is written against. Adding a key to `shared:` means adding it
here, in the same commit — the same coupled-edit discipline
`_ADVANCED_SETTINGS_SCHEMA` already imposes, and testable the same way.

**D-9.3 — Cross-T2 multi-declaration check.** After all T2 files in `R(entry)`
are loaded, any top-level key name appearing in **two or more** of them is a hard
error naming the key and both files. This is the direction D-9.2 cannot see: a
genuinely new cross-workflow key, invented after this design lands, that nobody
thought to add to `SHARED_SEAM_KEYS`. Its first symptom is being written twice,
and this check turns that symptom into a parse-time failure with a message that
says what to do — promote it to `shared:`.

The check is deliberately **name-based, not value-based**: two T2 files declaring
the same key with the *same* value is the more dangerous case, not the safer one,
because it will agree until the day someone edits one of them.

**Coverage, honestly.** D-9.1 catches leaving a workflow key in T1. D-9.3 catches
duplicating a key across T2 files. D-9.2 catches planting a shared key in a T2
file. What none of them catches is a key read by two workflows that appears in
only *one* T2 file and is read across the section boundary from there — which is
exactly the shape WF3's `workflows.build_model.wflow_outvars` read already has
(E1). That read is legal today and stays legal: it is mediated by
`guarded_sections`, which is a *declared* cross-section dependency and is what
makes `build_model`'s T2 file required for a WF3 run (§8.3). The enforcement
boundary is therefore: **undeclared** cross-workflow sharing is refused;
**declared** cross-section reads remain, tracked in one maintained list. §19 Q2
records whether that list should itself become a checked contract.

## 10. Config identity under the split layout

The hardest part of this design, and the part D-8.1 does *not* answer on its own.
Everything that reads the in-memory `config` dict is safe by the composition
invariant. This section covers the four things that are not in-memory reads: a
file's bytes, a DAG edge, a disk re-read, and a section's key set.

### 10.1 D-10.1 — What the merged workflow section contains

```
config["workflows"][name] = {"enabled": <T1 bool>, **<T2 body>}
```

`enabled` **is** merged back in, restoring today's section exactly.
`config_path` is **not** merged in; it is exposed only through
`WORKFLOW_CONFIG_PATHS`.

Both halves are load-bearing, and both are about the experiment freeze (E6.2).
`build_experiment_config` records `{"experiment_name", "run_stress_test":
dict(experiment_cfg)}` and `_frozen_differences` is a **key-union** diff
(`write_experiment_config.py:47-52,63-140`), so a key that is present in a
recorded `experiment.yml` and absent from the new document reads as *changed* and
refuses the experiment. Dropping `enabled` from the section would therefore
refuse **every already-run experiment in every migrating project** — the exact
failure mode `t2608072234` recorded for key retirement. Adding `config_path`
would do the mirror-image damage: the section would gain a key no recorded
`experiment.yml` has, refusing the same experiments, and would additionally make
run identity depend on where a project happens to store its files.

With this rule, `experiment.yml` written before migration and after migration are
**byte-identical for an unchanged experiment**, and the freeze needs no
migration, no registry entry, and no code change.

### 10.2 D-10.2 — The two in-memory digests are unchanged

- **`effective_config_digest`** (E6.1) digests
  `effective_config_document(config, ADVANCED_SETTINGS, CONFIG_PROJECTION)`, and
  `project_config` walks the projection paths through the merged dict. Same
  paths, same values, same canonical JSON, same SHA-256. Unchanged for all four
  entry points, including WF3, whose projection reaches into `workflows.build_model`
  and `workflows.analyze_projections` — both present in `R(wf3)` by §8.3.
- **`guarded_sections_digest`** (E6.3, `run_stress_test.smk:340-352`) hashes
  `config.get("project")`, `config["shared"]["basin"]`,
  `config["workflows"]["build_model"]`, `config["workflows"]["analyze_projections"]`
  from the merged dict. Same values, same digest, same rerun-trigger behavior:
  editing WF1's settings still flips it and still re-runs rule 3.01, only now the
  edit happens in `build_model`'s T2 file. `config_path` staying out of the merged
  section (D-10.1) is what keeps this digest experiment-invariant, which
  `run_stress_test.smk:329-331` requires because the guard's second output is
  shared across experiments.

Both are unchanged *by construction*, not by inspection. No code in
`provenance.py` or in the digest call sites is touched.

### 10.3 D-10.3 — T2 files become declared rule inputs

`config_path` is a declared **input** — not a param — in six rule bodies (N1).
Every T2 file loaded by an entry point must be declared alongside it, in the same
`input:` blocks, with the same `ancient()` qualification where the T1 path has one:

| Rule | Today | Adds |
|---|---|---|
| `analyze_climate.smk:344` `snapshot_config` | `config_snake = config_path` | `config_workflows = WF_CONFIG_PATHS` |
| `build_model.smk:467` `snapshot_config` | `config_snake = config_path` | `config_workflows = WF_CONFIG_PATHS` |
| `build_model.smk:535` `prepare_spatial_maps` | `config_snake = config_path` | `config_workflows = WF_CONFIG_PATHS` |
| `analyze_projections.smk:836` `snapshot_config` | `config_snake = config_path` | `config_workflows = WF_CONFIG_PATHS` |
| `run_stress_test.smk:621` `snapshot_config` | `config_snake = config_path` | `config_workflows = WF_CONFIG_PATHS` |
| `run_stress_test.smk:836` `prepare_stress_test_grid` | `config = ancient(config_path)` | `config_workflows = ancient(WF_CONFIG_PATHS)` |

`WF_CONFIG_PATHS` is `sorted(WORKFLOW_CONFIG_PATHS.values())` — sorted so the
declared input list does not churn on dict iteration order, which would look like
a rule change to Snakemake's own bookkeeping.

**This is not tidiness.** The repo has already paid for the alternative once, at
this very rule family: `run_stress_test.smk:862-872` records that rule 3.10's
weathergen template "was a params-only read until 2026-08-05, so editing the
template changed nothing until something else forced a rerun — 3.10 stayed
satisfied, its generated config stayed stale, and 3.11 kept generating
realizations from superseded settings. It propagated silently precisely BECAUSE
the generated config is properly declared." A T2 file left undeclared reproduces
that defect exactly, one level up: a user edits `run_stress_test.yml`, Snakemake
sees no changed input, and the experiment re-uses stale realizations. Declaring
the T2 files is the F7 fix applied prospectively.

Note the interaction with the rerun triggers already in place: for the
`snapshot_config` rules, `params.effective_config` already carries the composed
values, so a T2 edit would retrigger via params even without the input
declaration. `prepare_spatial_maps` (1.06) and `prepare_stress_test_grid` (3.09)
have no such params, which is why the input declaration is the mechanism rather
than a belt-and-braces addition.

### 10.4 D-10.4 — `reporting:` lives in the WF3 T2 file, hoisted

`reporting:` is read in exactly one place — `run_stress_test.smk:530` →
`surface_axes.py:387` `config.get("reporting")` — so the seam rule does not force
it into T1. It goes into the WF3 T2 file as a top-level key of that file, and
`compose_config` **hoists** it back to `config["reporting"]` through a closed
one-entry map:

```
HOISTED_SECTIONS = {"run_stress_test": ("reporting",)}
```

Hoisting rather than nesting is what preserves D-8.1: `parse_surfaces(config)` is
untouched, and — critically — `reporting:` stays **outside**
`config["workflows"]["run_stress_test"]`, so it stays outside `CONFIG_PROJECTION`,
outside the effective-config digest, and outside the experiment freeze. That
exclusion is deliberate today (`run_stress_test.smk:526-529`: "a caption can be
corrected without re-running the experiment"), and nesting `reporting:` inside the
workflow section would silently revoke it — turning every caption edit into a
frozen-experiment refusal.

**The retrigger surface narrows, and does not worsen.** Today `reporting:`'s
bytes live inside the single config file, which is a declared input to rules 1.06
and 3.09 (N1) — so a caption edit already dirties a WF1 rule, despite
`reporting:` being excluded from run identity. (`run_stress_test.smk:528-529`'s
"nothing declares it as a rule input, so no DAG edge … is created either" is
about the surface *declarations*, which no rule takes as an input file; it is not
a statement about the config file that carries them, which every one of the six
rules in §10.3 does declare.) After the split, those bytes live in the WF3 T2
file, which WF1 never loads and never declares (§8.3: `R(build_model) =
{build_model}`). A caption edit therefore stops dirtying rule 1.06 and continues
to dirty rule 3.09. Both behaviors are output-neutral — a re-run of 1.06 produces
identical bytes — so this is a strict improvement, and it is the second-order
benefit of the split that criterion 5 is actually about.

**Runner-up, and the condition that flips it:** leaving `reporting:` at T1's top
level. Rejected because it keeps a WF3-only, user-facing post-processing concern
in the file every workflow reads, which is the confusion this milestone exists to
end. It becomes correct the moment a second workflow reads `reporting:` — at
which point S4 forces the move automatically and D-9.3 fires if anyone tries to
duplicate it instead.

### 10.5 D-10.5 — `file_sha256(config_path)`: the one mechanism whose meaning changes

`source_config.{path, sha256}` in every `run_record.yml`
(`copy_config_files.py:449-452`) and the optional `source_config_sha256` field on
each journal line (`provenance.py:465,491-492`) hash **the file passed to
`--configfile`**. That is T1, and after the split T1 no longer contains the
workflow's settings — so on its own that field stops being a fingerprint of "what
this run was configured with".

**Decision: keep the field, keep its meaning, and cover the T2 bytes through the
existing referenced-inputs machinery.** Each loaded T2 file is registered in
`copy_config_files.__main__`'s `other_config_files` / `reference_roles` dicts
under role `workflow_config_<name>`, exactly as `model_build_config` and
`waterbodies_config` already are (`copy_config_files.py:546-549`, the E10
precedent). It therefore acquires, with **no schema change at all**:

- `sha256` of its bytes and `size_bytes`, in `run_record.referenced_inputs`;
- `git_blob` when the toolbox can give the file back (`_tracked_blob`, E3);
- and, because `referenced_inputs` feeds `configuration_inputs_digest`, its bytes
  move the run record's `configuration_inputs_sha256` — the digest
  `_RUNS_README` already tells readers to compare runs with, and which is already
  documented as covering "the bytes of every referenced catalog and template".

The journal is likewise not blind: `journal_event` already writes
`effective_config_sha256` and `configuration_inputs_sha256` on **every** line
(`provenance.py:478-492`), and both move when a T2 file's values or bytes change.
Only the narrow, optional `source_config_sha256` narrows in meaning, and its
docstring gains one sentence saying so.

`source_config.path` keeps pointing at T1 because that is the file a user re-runs
with, which is the question that field answers.

### 10.6 D-10.6 — Two disk re-reads must be redirected

Two modules bypass Snakemake's parsed `config` and re-read the source YAML from
disk. Both index `yml["workflows"]["run_stress_test"]`, which after the split is
not in the file they are handed:

| Module | Read | Reads |
|---|---|---|
| `prepare_weagen_config.py:89-91` | `read_yml(snake_config_path)` from `params.snake_config` (`run_stress_test.smk:888`) | `realizations_num`, `stress_test.{temp,precip}.transient_change` (N2) |
| `prepare_cst_parameters.py:162-165` | `open(config_fn)` from `input.config` (`prepare_cst_parameters.py:265` ← `run_stress_test.smk:836`) | `workflows.run_stress_test.stress_test` (N8) |

**Decision: pass the resolved section as params rather than re-plumbing a path.**
Rule 3.10 already hands `prepare_weagen_config` six explicit params — `seed`,
`water_year_start`, `dry_spell_factor`, `wet_spell_factor`, `middle_year`,
`sim_years` — several of which were moved out of the template for exactly this
reason (`prepare_weagen_config.py:106-118`). Folding `realizations_num` and the
two transient flags in as params finishes a conversion already three-quarters
done, and the disk read disappears rather than being redirected. The same for
`prepare_cst_parameters`: it receives `stress_test_cfg` as a param and keeps
`input.config` only as the DAG edge D-10.3 requires.

The alternative — hand each module the WF3 T2 path instead — was rejected because
it hard-codes the split into two leaf modules that have no business knowing about
it, and because it leaves each module re-deriving a section the Snakefile has
already composed and validated. Note `prepare_cst_parameters.py:250-251` also
derives a *default* `lookup_fn` from `os.path.dirname(config_fn)`; that path is
only taken outside Snakemake (`sys.argv[1]`), where the caller passes whatever
file it likes, so it needs no change.

### 10.7 The narrowing, and why nothing reads it

§8.1 records one deviation from shape identity: for a single-entry-point
invocation, `config["workflows"]` holds only `R(entry)`'s sections. Nothing is
affected, and the reason is structural rather than lucky: **every reader of
another workflow's section is already declared**. WF0/WF1/WF2 read only their own
section (E1). WF3's cross-section reads are exactly `guarded_sections`, which
`R(wf3)` loads. `effective_config_digest` reads only `CONFIG_PROJECTION`.
`run_workflows.py` reads T1 alone and never composes (§12.1). A reader added
later that reaches into an unloaded section gets a `KeyError` at parse time —
loud, immediate, and gated by `test_cli` — which is the correct outcome, because
the fix is to declare the dependency in `CONFIG_PROJECTION` / `guarded_sections`
and thereby put it in `R(entry)`.

## 11. Project snapshot machinery

### 11.1 D-11.1 — The snapshot becomes a composed document, not a byte copy

`copy_config_files.py:222` copies the source file verbatim (N3). Under the split
that copy is T1, which does not contain the workflow's settings — and WF3's drift
guard reads `workflows.build_model` **out of the wf1 snapshot** and
`workflows.analyze_projections` out of the wf2 snapshot (N6). A verbatim T1 copy
would leave the guard comparing against sections that are not there.

> **`snapshot_config` writes the COMPOSED config** — T1 plus the T2 sections this
> entry point loaded, inlined back under `workflows.<name>` exactly as the merged
> in-memory dict holds them — serialized with `yaml.safe_dump(..., sort_keys=True)`
> to the same path it writes today.

Consequences, each checkable:

- **The guard is unchanged.** `check_project_consistency.py:166-182` finds
  `project`, `shared.basin`, `workflows.build_model` in the wf1 snapshot and
  `workflows.analyze_projections` in the wf2 snapshot, because each entry point
  composes its own `R(entry)` (§8.3) and each guarded section is compared against
  the snapshot of the workflow that owns it (N6). No code change, no path change,
  no new file.
- **The `ancient()` input contract is unchanged.** `run_stress_test.smk:392`
  builds the path and rule 3.01 keeps declaring it `ancient()` at `:600`, still
  pointing at `config/runs/snake_config_build_model.yml`; only its content
  shape changes, and `file_digest_or_absent` is content-agnostic.
- **The three snapshots stop being byte-identical.** This is the point. N5 shows
  all three currently carry SHA-256 `00ef44f7fef2…`; after this change each
  carries only the sections its workflow composed, so the WF1 snapshot no longer
  contains WF3's stress-test grid and vice versa. `_RUNS_README`'s section "Why
  the `snake_config_<workflow>.yml` files look identical"
  (`copy_config_files.py:76-93`) is **deleted and replaced** by a statement that
  each file is now the workflow-scoped view its name always promised. The README
  is generated by the module, so this is one string edit.
- **Comments are lost.** A verbatim copy preserved the source file's comments; a
  `safe_dump` of the composed document does not. Accepted: this bin is explicitly
  "written by the run… editing any of it changes nothing", the run record is
  already `safe_dump`ed, and the source files remain the annotated artifact. This
  is the same trade `suggest_experiment_name.py` refuses for the *source* config
  (E4) and for the same reason — the distinction is source versus record, and
  this file is a record.
- **Three baseline targets move.** Exactly the three N5 names. §16 makes that the
  falsifiable acceptance statement.

### 11.2 D-11.2 — T2 files are recorded, not copied

The E3 predicate is "copy a referenced file into the project only when the
repository cannot reproduce it". A project's own T2 file lives outside the
checkout, so the predicate as written would copy it into
`<project_dir>/config/templates/`. That copy would be redundant: D-11.1 has
already archived the file's *content* inside the composed snapshot, verbatim in
substance.

> T2 files are registered with role `workflow_config_<name>` and are
> **record-only**: `sha256`, `size_bytes`, and `git_blob` when tracked;
> `archived_path: null`; `recoverable` keeping its existing meaning (the toolbox
> can give the file back). The registration reuses `other_config_files` /
> `reference_roles` unchanged; only the destination is `None`.

This is a narrow, stated extension of the predicate — *copy unless the content is
already archived in this project* — and it touches nothing else.
`ALWAYS_ARCHIVED_ROLES` (`output_locations`, `observations_timeseries`) keeps its
current unconditional behavior; the collision guard at
`copy_config_files.py:317-325` is unaffected because a record-only entry claims
no destination.

### 11.3 What `<project_dir>/config/templates/` holds

Unchanged in purpose and, in the common case, unchanged in content: it is the bin
for **verbatim snapshots of shipped toolbox files the checkout cannot give back**
(`copy_config_files.py:514-523`). It receives `model_build_config` /
`waterbodies_config` only when a project points those keys at its own files, and
it is normally empty (AGENTS.md, since 2026-08-13). D-11.2 keeps T2 files out of
it, so the bin's meaning does not blur: **shipped-toolbox snapshots**, never
project-authored configs. No successor bin is introduced — introducing one would
be a project-tree change, which is R9's territory and not this milestone's.

## 12. Downstream consumers

### 12.1 `scripts/run_workflows.py` (E7) — no change required

`_enabled_flags` requires all four `workflows.<name>` sections to be present
mappings each carrying a bool `enabled` (`run_workflows.py:282-314`). Under D-7.1
each section is `{enabled: bool, config_path: str}` — still a mapping, still
carrying a bool `enabled`, so `isinstance(workflows[name], dict)` and the bool
check both pass unchanged. `_project_dir` reads `project.project_dir` from T1,
unchanged. `build_command` passes the same single `--configfile` T1 path to every
invocation, unchanged. `missing_wf1_leaves` inspects the filesystem, unchanged.

The wrapper **never composes**: it reads T1 only, which is exactly right — enable
switches are a T1 concern by S1, and the wrapper's job is invocation, not
configuration. This is the clearest single piece of evidence that the enable
switches belong in T1 rather than in each T2 file: putting them in T2 would force
the wrapper to resolve and open four more files before it could decide what to
run, and would make a T2 file's absence a wrapper error rather than a workflow
one.

One optional improvement, **not required and not in this design's scope**: the
wrapper could validate that each enabled workflow's `config_path` resolves, and
fail before invoking anything, in the same spirit as `_check_wf1_leaves`. Recorded
as §19 Q4.

### 12.2 `scripts/suggest_experiment_name.py` (E4) — edits the WF3 T2 file

The command keeps taking **T1** on the command line — that is the file a user
knows the name of, and it is the `--configfile` target. It then resolves
`workflows.run_stress_test.config_path` from T1 and performs its text splice on
**that** file.

Two mechanical consequences for the implementation brief:

- `_plan_edit` (`suggest_experiment_name.py:64-224`) computes an indentation plan
  for a key nested two levels under `workflows:` → `run_stress_test:`. In a T2
  file `experiment_name` is a **top-level** key at column zero. The plan's depth
  handling changes; the text-splice approach (never `yaml.safe_dump`, so the
  file's ~110 comments survive) does not, and must not.
- The verification reload at the end reloads the T2 file and checks the top-level
  key, not the nested path.

If `workflows.run_stress_test.config_path` is absent or unreadable, the command
fails with the same "nothing has been reserved" posture it already takes for a
config it cannot edit — the plan is computed before the name is allocated
precisely so a failure leaves no orphaned `experiments/<id>/` behind.

### 12.3 `config_path` forwarding to Python scripts (E5) — contract preserved

`config_path = workflow.configfiles[0]` stays in all four Snakefiles, keeps
meaning "the file passed to `--configfile`", and keeps being forwarded as
`config_snake` / `snake_config` params to `copy_config_files.py` and
`prepare_build_config.py`. `file_sha256(config_path)` keeps hashing it (§10.5).
The two modules that used the forwarded path to **re-read settings** stop doing so
(§10.6); the modules that use it as an **identifier or an error-message subject**
(`prepare_build_config.py:51`, `run_header`) are untouched, and both are correct
as-is because T1 is genuinely the file the user invoked.

The E5 two-configfile hazard — `config` reflecting a merge while `config_path`
reflects only the first file — is *avoided rather than managed* here, because
there is still exactly one `--configfile`. That is the operative argument for S2
over §17.1's alternative.

### 12.4 `simulation_window ⊂ historical_window` (E8) — now genuinely cross-file

`resolve_simulation_window(shared_cfg, model_cfg)` (`snake_utils.py:1322-1399`,
called at `build_model.smk:95`) takes two mappings and compares
`workflows.build_model.simulation_window` against `shared.historical_window`. Its
**signature, body, error messages and passthrough-when-absent behavior are
unchanged**, because by D-8.1 both mappings hold the same values they hold today.

What changes is where the two values were *authored*: the window is in WF1's T2
file, the record is in T1. The validation is therefore now a genuine cross-file
check, and this is the design's clearest demonstration that S4's placement rule
is correct rather than arbitrary — `historical_window` is read by WF0, WF1 and
WF3, so S4 puts it in T1, and D-9.2 refuses a `historical_window:` planted in a
T2 file rather than letting a project create two records that disagree.

One implementation obligation: the `ValueError` messages name
`workflows.build_model.simulation_window` and `shared.historical_window`. Those
are the *logical* paths and stay correct, but a user now has two files open. The
messages gain the resolved file paths — one line each, no logic change — so the
error says which file to edit. The same applies to the message-shape tests in
`tests/`.

## 13. Advanced settings — interior organization (S3)

`config/advanced_settings.yml` stays one toolbox-level file with three sections
split by **authority**: `constraints:` (no project config may relax), `defaults:`
(a project config may override), `runtime:` (external toolchain pins, not
overridable). None of that moves. What this design settles is how the file is
organized *inside* as workflow-specific entries accumulate.

**D-13.1 — Namespace by workflow inside `constraints:` and `defaults:`, one level
deep, only where a setting is genuinely workflow-scoped.**

```yaml
constraints:
  min_historical_years: 16          # toolbox-wide: stays flat
defaults:
  seed: 123                         # toolbox-wide: stays flat
  water_year_start: Jan             # toolbox-wide: stays flat
  julia_threads: 4                  # toolbox-wide: stays flat
  run_stress_test:                  # workflow-scoped: namespaced
    batch_disk_headroom_fraction: 0.25
runtime:
  julia_version: "1.11.7"           # never namespaced: a toolchain pin is not per-workflow
```

The split test is **who reads it**, applied identically to S4's: a setting read by
more than one workflow stays flat; a setting read by exactly one workflow moves
under that workflow's key. Today exactly one entry qualifies —
`batch_disk_headroom_fraction`, read only by WF3's batch sizing — and the other
four are genuinely cross-workflow (`water_year_start`'s own comment lists four
consumers across three workflows). So the migration is one key, and the value of
the ruling is that it fixes the answer *before* the file grows, which is what the
owner asked.

`runtime:` is never namespaced: a toolchain pin describes the environment, not a
workflow, and namespacing it would invite two workflows to pin different Julia
versions — a thing `tests/test_julia_runtime.py` exists to prevent.

**D-13.2 — The closed schema nests with the file.** `_ADVANCED_SETTINGS_SCHEMA`
(`snake_utils.py:869-879`) gains one nested level for namespaced entries and keeps
its closed-rejection semantics at every level: an unknown section, an unknown
workflow namespace, and an unknown key inside a namespace are all rejected at
parse time. The schema, the file, and `tests/test_advanced_settings.py` continue
to be edited in one commit — the discipline E2 already imposes, now applied one
level deeper.

**D-13.3 — Both override mechanisms are preserved exactly, and neither is
unified.** E2 records two distinct paths from `defaults:` to a run:

| Mechanism | Example | Behavior on an explicit `null` |
|---|---|---|
| Call-site default | `julia_threads` at `build_model.smk:102` | `julia_threads: null` **raises** at parse (`_positive_int(None)`) |
| Resolver substitution on `None` | `seed` (`snake_utils.py:1134-1151`), `water_year_start` (`:1167-1171`) | `seed: null` **falls back** to the default |

Unifying them is out of scope and is not attempted here: it would change what an
explicit `null` does for at least one key, which is a behavior change under a
refactor that claims output neutrality. The override *keys* stay in `shared:` per
S5 (`shared.seed`, `shared.water_year_start`, `shared.julia_threads`) — they are
read by more than one workflow, so S4 places them in T1 independently of S5, and
the two rulings agree.

A **workflow-scoped** advanced knob a project may set — S5's `batch_size` example
— lives as an optional key in that workflow's **T2** file and overrides the
namespaced default. That composes correctly with §9: it is a single-reader key, so
D-9.2 does not reject it and D-9.3 cannot see it in two files.

## 14. Workflow naming reconsideration (scope amendment S6)

The design **recommends**; the owner rules at G1 (provisional) and G2 (final).

### 14.1 What exists today

Two independent schemes, deliberately kept independent:

- **Workflow names** — `analyze_climate`, `build_model`, `analyze_projections`,
  `run_stress_test`. Verb-first, set on 2026-08-14 alongside the addition of the
  fourth workflow, with recorded rationale (`docs/migration-workflow-names.md`,
  "Why"): the old names were nouns and two were vague about what the workflow
  does — `model_creation` also *runs* the model, `climate_projections` computes
  change factors that are an overlay and never a driver.
- **`wfN` ids** — `wf0`..`wf3`, used in log/benchmark/DAG filenames and as the
  `W` digit of the `W.NN` rule-reference scheme. `dev/reference/naming.md` §9 is
  explicit that `W` is a workflow **id**, not a position, which is why `wf0` was
  added as `0` rather than renumbering the other three.

### 14.2 Candidates

**Candidate A — keep the current names.** No change to any surface. The T2 files
this design introduces are named `snake_config_<variant>_<name>.yml` and
`snake_config.<name>.template.yml` from the existing keys (D-7.4).

**Candidate B — module nouns.** `climate`, `model`, `projections`, `experiment`:
one word each, reading as the four modules of a modular toolbox, which is the
milestone's stated direction. *Would be preferable if* the toolbox becomes a
registry of named modules where each workflow is discovered rather than invoked
by filename, and the verb becomes redundant because "run the `model` module" is
the invocation. *Rejected now:* it reverts a six-day-old ruling by restoring
precisely the noun forms that ruling removed for vagueness, and it makes
`workflows.experiment.stress_test` read worse than the
`workflows.run_stress_test.stress_test` the migration doc already ruled correct
("the workflow is named for what it does, the section for what it configures").

**Candidate C — id-prefixed names.** `wf0_analyze_climate` … `wf3_run_stress_test`,
folding the id into the name so the `.smk` file, the config key, the log prefix
and the rule digit are one token. *Would be preferable if* the id and the name
could disagree, or if a reader routinely had to translate between them. *Rejected
now:* naming.md §9 keeps `W` an id precisely so it is free of position, and
folding it into the config key freezes it into every project's config — inserting
a workflow, or renumbering, would then become a config-breaking change rather
than a filename change. It buys sortable logs that `logs/wf1_build_model.log`
already provides.

### 14.3 Recommendation — Candidate A, keep the current names

Three reasons, in order of weight.

1. **No naming defect surfaced.** This design read every consumer of the workflow
   names — the four Snakefiles, `run_workflows.py`, `copy_config_files.py`,
   `check_project_consistency.py`, `provenance.py`, the snapshot paths, the
   baseline manifest — and none of them is confusing because of a name. The one
   oddity anyone reports (`workflows.run_stress_test.stress_test`) is explicitly
   ruled correct in the standing migration document. A rename with no defect
   behind it is churn.
2. **The coupling argument runs the wrong way here.** "One break, not two" is a
   reason to *bundle* a rename that is independently justified — it is not a
   reason to rename. And the bundling is not free: §14.4 shows the rename touches
   a substantially **larger** surface than the config split does, including four
   surfaces the config split does not touch at all (the DAG digit map, log and
   benchmark filenames, the `config/runs/` snapshot paths, and the baseline
   manifest's target keys). Bundling would import that surface into a refactor
   whose whole claim is output neutrality.
3. **The 2026-08-14 precedent argues against, not for.** That rename's own
   rationale was that it rode along with adding a fourth workflow, "because adding
   one already forces edits to `run_workflows.py`'s `WORKFLOW_ORDER`,
   `test_cli.py`, `plot_workflow_dag.py`'s digit map, the shared-producer
   symmetry tests, `check_baseline` and the config template — every file the
   rename touches". The config split forces edits to none of those five. The
   rider that justified the first rename does not exist for a second one.

**Name-scheme independence.** Whichever candidate wins, this design's T2 filename
scheme is unchanged in *form*: both families derive from the `workflows.<name>`
key by one transform (D-7.4). Under Candidate A the seed files are
`snake_config_rapid_build_model.yml`; under Candidate C they are
`snake_config_rapid_wf1_build_model.yml`. Nothing else in §§7–13 depends on the
names — the loader takes `R(entry)` from the Snakefile's own declarations, never
from a hard-coded list of names, and `SHARED_SEAM_KEYS` names `shared:` keys, not
workflows. The single place a rename would reach into this design is the
migration script's output filenames (§15.3), which are the same one transform.

### 14.4 Surface inventory for a rename (if the owner rules B or C)

Every load-bearing surface, so the cost is visible at the gate rather than
discovered in implementation:

| # | Surface | Notes |
|---|---|---|
| 1 | Four `*.smk` filenames | `-s` targets; `tests/test_cli.py` enumerates them |
| 2 | `workflows.<name>` T1 keys | breaking for every project config |
| 3 | **T2 filenames + `config_path` values** | introduced by this design; one transform (D-7.4) |
| 4 | `config/templates/snake_config.<name>.template.yml` | introduced by this design |
| 5 | `run_workflows.py`: `WORKFLOW_ORDER`, `SNAKEFILE`, `PER_WORKFLOW_FLAGS`, `LEAF_PRODUCER` | plus its error strings |
| 6 | `plot_workflow_dag.py` digit map; `logs/dag/<project>_wf<N>_dag.png` | |
| 7 | `logs/wfN_<name>.log`, `benchmarks/wfN_benchmarks_<exp>.md` | project-tree paths |
| 8 | `config/runs/snake_config_<name>.yml`, `config/runs/<name>/run_record.yml` | **the two that bite**: baseline-fingerprinted (N5) *and* `snake_config_build_model.yml` is a mandatory declared `ancient()` input of WF3's guard. `_RUNS_README` states outright that "the name cannot be fixed by renaming the file" |
| 9 | `experiments/<exp>/config/snake_config_run_stress_test.yml` | same, experiment-scoped |
| 10 | `CONFIG_PROJECTION` / `guarded_sections` string literals; `check_project_consistency` guarded paths | run identity: a changed projection path string changes `effective_config_digest` |
| 11 | `journal.jsonl` `workflow` field | old lines keep the old spelling — correct, per the 2026-08-14 precedent |
| 12 | `cross_workflow_leaves.py` / `cross_workflow_inputs.py` `LEAF_PRODUCER` | |
| 13 | pixi tasks `dag-wf*`, `run-workflows` | |
| 14 | Tests: `test_cli.py`, `test_run_workflows.py`, shared-producer symmetry tests, `semantic_tree_diff` inventory | |
| 15 | `dev/baseline/manifest.json` target keys | **forces a baseline re-record for path reasons alone**, which destroys §16's falsifier for this milestone |
| 16 | Docs: `README.md`, `AGENTS.md` tables, `docs/`, `dev/reference/naming.md` §9, `dev/reference/workflows/rule-index.md`, and a successor to `docs/migration-workflow-names.md` | |

Row 15 is the decisive practical objection to bundling: §16's acceptance
criterion is "exactly three baseline targets move, all of them config snapshots".
A rename moves a dozen target **keys**, so the baseline can no longer distinguish
"the refactor was output-neutral" from "the refactor changed a number". If the
owner rules for a rename, it must therefore land as a **separate commit series
after** the config split has been baseline-verified — which is the opposite of
the one-migration coupling argument, and should be said plainly at the gate.

## 15. Migration plan

Precedent and successor: `docs/migration-workflow-names.md` (2026-08-14). The new
document is `docs/migration-config-tiers.md`, written in the same shape — what to
change in your config, what to change in your commands, what moves inside an
existing `project_dir`, and why.

### 15.1 D-15.1 — Clean break, not backward compatibility

**Decided:** a config carrying settings inline under `workflows.<name>` fails at
parse time. There is no dual-mode loader and no deprecation window.

The argument is the one the repo already made, six days ago, for the same class of
change: "*If you have a project config, it will fail at parse time until you
rename its three `workflows:` subsections. That is deliberate: the alternative —
renaming the files while freezing the keys — leaves a config surface that
disagrees with the thing it configures.*" The same holds here with more force,
because a dual-mode loader would cost three specific things:

- **D-9.1 could not hold.** Seam enforcement in the T1→T2 direction *is* the
  closure of the `workflows.<name>` stanza. A loader that also accepts inline
  settings has no closed stanza to check, so S4 falls back to convention — which
  the owner's ruling 4 explicitly rejects.
- **Half-split configs become legal**, and a project could carry `wflow_outvars`
  in T1 and `simulation_window` in a T2 file with nothing objecting. Every later
  question ("which file wins?", "which one does the digest see?") acquires two
  answers.
- **The migration detector disappears.** Under a clean break, an unmigrated
  config produces a precise, actionable error (§15.2). Under dual mode it
  produces a silently-working run and an unmigrated project that nobody notices —
  the same "nothing fails, so nobody looks" failure the vendored-console marker
  and the CI-unread incident both record.

The population this breaks is small and known: the shipped seed configs (migrated
in the same commit series), the owner's own projects, and the CST-API backend,
which constructs configs programmatically and is versioned independently — and
which this repo's standing policy says must never constrain a decision here
anyway.

### 15.2 D-15.2 — The migration detector is the closed stanza

Because `workflows.<name>` admits exactly `{enabled, config_path}` (D-7.1), an
unmigrated config fails on its **first** extra key with a message that names:
the offending key, the workflow it belongs to, the T2 filename convention, the
migration command (§15.3), and `docs/migration-config-tiers.md`. No separate
detector, no version key, no schema-version negotiation. It fires at Snakefile
parse time, before the DAG, so `--dry-run` reports it and `pytest tests/test_cli.py`
gates it.

### 15.3 D-15.3 — `scripts/split_project_config.py`, report-only by default

A user-facing runner, so `scripts/` and not `dev/scripts/` (AGENTS.md's
invocation-model rule: `scripts/` is what a user runs to drive the pipeline;
`dev/scripts/` is never part of a run and is not guaranteed to be in a user's
checkout).

```
python scripts/split_project_config.py <config.yml>            # reports, writes nothing
python scripts/split_project_config.py <config.yml> --write    # writes T1 + 4 T2 files
```

Report-only by default, `--write` explicit, mirroring `prune_series_cache.py` and
`prune_climate_store.py`.

**It splits the file as TEXT, not through `yaml.safe_dump`** — E4's argument
applies unchanged and with more at stake: the shipped template carries ~110
comments, a real project's config carries the ones its author wrote, and this is
the first command a user runs against their file. The mechanical transform:
locate the `workflows:` block; for each `<name>:` subsection, take its body
including the comment lines that precede each key, dedent by four spaces, drop
`enabled:`, and write it to `<t1_dir>/<t1_stem>_<name>.yml`; replace the
subsection in T1 with the two-key stanza; move a top-level `reporting:` block
into the `run_stress_test` T2 file.

Default output path `<t1_dir>/<t1_stem>_<name>.yml` is chosen because it produces
the shipped seed naming for free (`snake_config_rapid.yml` →
`snake_config_rapid_build_model.yml`), which lands inside the E9 tracking glob
with no `.gitignore` change (D-7.4), and because a project's T2 files beside its
T1 file is the layout least likely to break a relative path. `--outdir`
overrides it.

**Its own acceptance gate is a round trip:** for each shipped seed and for the
template, `compose_config(split(x))` must equal `yaml.safe_load(x)` exactly —
same keys, same values, same `None`s. That is a property test, it is cheap, and
it is the direct executable form of D-8.1. If comment-preserving text splitting
proves disproportionately expensive, the fallback is a `safe_dump` split plus a
printed warning that comments were dropped and a pointer to the original file —
the round-trip gate is unaffected either way.

### 15.4 Mechanical steps for an existing project

1. `python scripts/split_project_config.py <your-config.yml>` — read the report.
2. `--write` — four T2 files appear beside the config; T1 shrinks to `project:` +
   `shared:` + four two-key stanzas.
3. Delete the T2 files for workflows this project never runs, and leave their
   `config_path` pointing at a path that does not exist — **unless** the project
   runs WF3, in which case `build_model` and `analyze_projections` T2 files must
   exist even when disabled (§8.3). The parse error says so.
4. Re-run. Nothing under `project_dir` needs hand-migration:
   - the three config snapshots are **regenerated** with composed content on the
     next run of each workflow (D-11.1) — no path moves, so no `ls`-and-rename
     table like the 2026-08-14 migration needed;
   - `experiments/<exp>/config/experiment.yml` is **unaffected**: D-10.1 keeps the
     recorded section byte-identical, so a completed experiment stays unfrozen-safe
     and does not need re-creating;
   - `config/runs/journal.jsonl` keeps its history; new lines carry the same
     `effective_config_sha256` an unmigrated run would have produced.
5. If WF3 has already run and the guard is armed, the first post-migration WF3 run
   re-fires rule 3.01 (the wf1 snapshot's bytes changed, so
   `file_digest_or_absent` moves) and passes, because the composed wf1 snapshot
   carries the same `workflows.build_model` values the live config does.

### 15.5 Commit sequencing

Each step independently runnable, per the design-document rule that a move must
never leave the tree un-runnable between commits:

1. `compose_config` + seam checks + `WORKFLOW_CONFIG_PATHS`, with unit tests.
   Not yet called by any Snakefile — no behavior change.
2. `scripts/split_project_config.py` + its round-trip test.
3. Migrate the four shipped seeds and the template with the script; wire
   `compose_config` into the four Snakefiles; add the T2 rule inputs (D-10.3);
   redirect the two disk re-reads (D-10.6). **One commit** — the loader and the
   configs it requires cannot land apart.
4. Composed snapshot (D-11.1) + record-only T2 registration (D-11.2) +
   `_RUNS_README` text.
5. `suggest_experiment_name.py` (§12.2) + error-message file paths (§12.4).
6. Advanced-settings namespacing (§13) + schema nesting.
7. Docs sweep + `docs/migration-config-tiers.md`; baseline re-record last, after
   §16's falsifier has been read.

## 16. Validation plan

Mapped to the gates the intake verified runnable in this worktree.

| Gate | What it checks here | Expected result |
|---|---|---|
| `pytest tests/test_cli.py` | the parse gate: dry-runs all four entry points against the migrated seeds. Every composition error, every seam refusal, and the required/optional matrix (§8.3) fire here | green; four DAGs resolve |
| **new** `tests/test_config_composition.py` | `compose_config` unit surface: the `R(entry)` matrix; path resolution (relative/absolute/`~`/missing/non-mapping/empty); every §8.4 error; the D-9.1/9.2/9.3 refusals; `enabled` merged and `config_path` **not** merged (D-10.1); the `reporting:` hoist (D-10.4); duplicate-`config_path` refusal | new tests, green |
| **new** digest-equality property test | for each shipped seed: `effective_config_digest` and `guarded_sections_digest` computed from the pre-split config equal those computed from the composed post-split config. This is D-8.1 in executable form and stays permanently | equal |
| **new** freeze property test | an `experiment.yml` recorded pre-split + a post-split composed config → `check_not_frozen` passes. Direct test of D-10.1 | passes |
| **new** round-trip test for the splitter | `compose_config(split(x)) == yaml.safe_load(x)` for all four seeds and the template | equal |
| `pixi run lint` / `format-check` | CI gates, near-instant | green |
| `pixi run test-fast` | at the merge | green |
| `pixi run test-full` | **at the merge, not only at the push** — the branch touches all four Snakefiles and `blueearth_cst/shared/`, which AGENTS.md names as the paths the `workflow_contract` / `process_isolation` tier exists to guard. Redirect to a file; never pipe through `tail` | green |
| `pixi run tree-check` | the project tree holds nothing undeclared. A new file under `project_dir` means D-11.2 leaked a copy | unchanged |
| **`check_baseline.py check`** | **the falsifier.** Run from the primary checkout, `snake_config_baseline.yml`, WF1 with `--notemp` | **exactly three targets differ**, and all three are the `type: yaml` config snapshots N5 names. **Zero data targets differ.** |
| stale-spelling grep sweep | `workflows:` nesting depth in docs and tests; every `snake_config_*.yml` reference; `_RUNS_README`'s "look identical" section; AGENTS.md's `config/` and Key Commands sections; `README.md`; `config/templates/README.md`; `config/defaults/README.md` | no live reference to the pre-split shape |

**The manifest's full target set was enumerated, not sampled** (2026-08-20, this
worktree; `json.load(open('dev/baseline/manifest.json'))['targets']`): **seven**
targets — the three `type: yaml` config snapshots (N5), two `type: csv` CMIP6
change-factor tables, one `type: indicator` `q_indicators.csv`, and one
`type: discharge` `run_default/output.csv`. The enumeration matters because the
prediction cannot be made from the three snapshot paths alone: §10.5 puts each T2
file's bytes into `configuration_inputs_sha256`, so any manifested record
embedding that digest would move too. The candidate was
`experiments/<exp>/results/run_metadata.json`, which `WF3_TARGETS` declares —
**and it is not a manifest target**, so the prediction stands at three.

**The acceptance statement, falsifiably:** *a fourth differing baseline target, or
any differing target that is not one of the three config snapshots, is a defect in
this design or its implementation — not a re-record.* Re-record the baseline only
after that check has been read and reported. The known thinness stands and is
accepted: the manifest covers data targets, not figures or staticmaps.

**Not run, deliberately:** any figure gate. No `.png`/`.pdf` under `project_dir`
is consumed by a rule, and this change touches no plotting code.

## 17. Alternatives considered

### 17.1 CLI multi-configfile merge — rejected (S2, and independently)

Pass several `--configfile` arguments and let Snakemake merge them, instead of
referencing T2 files from T1.

*Why not:* four concrete disqualifiers, three of them recorded in the evidence.
(a) **Provenance goes actively wrong.** E5 pins the hazard: `config` reflects the
merge while `config_path` and `file_sha256(config_path)` reflect only the first
file — so `run_record.source_config.sha256` would silently describe a fraction of
the run. Under path reference it stays *narrow but true* (§10.5).
(b) **Only the first file is a DAG edge.** N1 shows `config_path` is a declared
rule input in six rules; `workflow.configfiles[0]` is one path, so the other
config files would be undeclared — reproducing the F7 stale-config defect
(§10.3). (c) **S4 becomes unenforceable.** Snakemake's merge is a silent
order-dependent dict update: a `historical_window` in two files produces no error,
just a winner. The loader-side checks D-9.2/D-9.3 have no place to live.
(d) **Wrapper and invocation churn:** `build_command` (`run_workflows.py:371-386`)
assembles one `--configfile`, and every documented command line carries one.

*When it would be preferable:* if Snakemake reported per-key merge provenance and
declared every configfile as a workflow input. It does neither.

### 17.2 Status quo plus per-workflow template snippets — rejected

Keep one config file; ship four commented snippets under `config/templates/` that
a user pastes into the `workflows:` block.

*Why not:* it addresses only the authoring experience, and none of the criteria.
Duplication is untouched — the three per-project snapshots stay byte-identical
(N5), and every variant still carries every workflow's parameters. Nothing becomes
enforceable, so S4 stays convention (criterion 1 fails outright). Nothing becomes
shareable between variants (criterion 2). And a snippet is a copy-paste aid, so
the copies drift exactly as they drift today — which is the confusion the owner
named in the change request. It does not advance modularization at all
(criterion 5).

*When it would be preferable:* if the goal were purely ergonomic and the owner had
ruled *against* loader enforcement. Ruling 4 rules the other way.

### 17.3 Advanced settings folded into the workflow files — rejected (S3)

Dissolve `config/advanced_settings.yml` and move each of its entries into the
workflow file that reads it, as an "advanced" sub-section.

*Why not:* it dissolves the **authority** boundary, which is the file's entire
reason for existing. `constraints:` would become project-editable, so
`min_historical_years` — whose own comment says no project config may relax it,
because weathergenr's wavelet decomposition needs 16 annual observations — becomes
relaxable by editing a file the toolbox hands the user. `runtime:` is worse:
`julia_version` would be settable per workflow, while `tests/test_julia_runtime.py`
exists to assert that three files declare one version. It also multiplies E2's two
override mechanisms across four files, and it has nowhere to put a genuinely
toolbox-wide default like `seed`, which four consumers across three workflows
read. §13 gets the ergonomic benefit — advanced settings visibly grouped by
workflow — without any of that, by namespacing *inside* the file.

*When it would be preferable:* if the toolbox stopped shipping hard constraints
and toolchain pins, i.e. if `advanced_settings.yml` were only defaults. It is not.

### 17.4 Considered and resolved in place

Recorded here so the reviewer can find them: the **wrapped T2 shape**
(`build_model:` at a T2 file's top level) — §7.2; **verbatim T1 snapshot plus a
guard that reads T2 files** — §11.1; **`reporting:` staying in T1** — §10.4;
**a `test_case/workflows/` subdirectory** for the seed T2 files — §7.4;
**handing the two disk-reading modules a T2 path** instead of params — §10.6;
**a backward-compatible dual-mode loader** — §15.1. Each carries its own
rejection rationale and, where one exists, the condition that would flip it.

## 18. Consequences and risks

### Positive

- Cross-workflow single-sourcing becomes **checkable at parse time** rather than
  conventional: three closed checks (D-9.1/9.2/9.3), gated by `test_cli`.
- The three per-project config snapshots stop being byte-identical whole-config
  copies (N5) and become the workflow-scoped views their filenames have always
  promised — closing a confusion `_RUNS_README` currently has to apologize for.
- A user editing one workflow opens a file containing that workflow's settings and
  nothing else; a project that never runs WF0 needs no WF0 file at all (§8.3).
- The spurious retrigger surface **narrows**: a `reporting:` caption edit stops
  dirtying WF1's rule 1.06 (§10.4).
- Two modules stop re-reading the source YAML from disk (§10.6), removing a class
  of coupling that would have broken silently under any composition scheme.
- Each T2 file's bytes enter `configuration_inputs_digest` through the existing
  referenced-inputs machinery, with **no schema change** (§10.5).

### Negative

- **The shipped seed set grows from 4 files to up to 20** (§7.4), and N7 shows no
  two current variants share a workflow section verbatim, so the immediate
  file-count effect is the owner's stated downside ("having to maintain more
  files") arriving in full. The mitigation is real but prospective: reconcile the
  incidental differences between variants during implementation, then point
  several T1 files at one shared T2. Criterion 2 is met on **snapshots** and on
  **per-file scope**; it is *not* met on total source bytes, and this design does
  not claim it is.
- Config snapshots lose their source comments (§11.1). Accepted — that bin is a
  record, not a source.
- A clean break (§15.1) breaks every existing project config until it is migrated.
  Mitigated by a precise parse-time error and a `--write` migration script, and
  precedented six days earlier.
- The reader now needs two files open to reason about one workflow's run — the
  cost of any decomposition. Mitigated by error messages carrying resolved file
  paths (§12.4) and by the composed snapshot being a single-file view of what
  actually ran.
- `dev/baseline/manifest.json` must be re-recorded for three targets, which is a
  primary-checkout, no-other-session-live operation.

### Neutral / must be planned for

- A migration document, a migration script, and one docs sweep.
- Advanced-settings schema gains one nested level (§13.2).
- `suggest_experiment_name.py`'s indentation planning changes depth (§12.2).

### Residual risks

| Risk | Severity | Mitigation |
|---|---|---|
| A T2 file left undeclared as a rule input reproduces the F7 stale-config defect silently | high | D-10.3 makes the declaration explicit per rule; the implementation brief lists all six rules by file:line |
| `SHARED_SEAM_KEYS` drifts from `shared:` as keys are added | medium | coupled-edit discipline + a test asserting every `shared:` key in the shipped template appears in the set — the same shape as `tests/test_advanced_settings.py` |
| The text splitter mangles a comment block in an unusual config layout | medium | report-only default; round-trip gate on values; `safe_dump` fallback with an explicit warning |
| A fourth baseline target moves | high if it happens | §16 makes it a **defect**, not a re-record — the check is read before the re-record |
| A future reader reaches into an unloaded workflow section | low | `KeyError` at parse time, gated by `test_cli`; the fix is to declare it in `CONFIG_PROJECTION` (§10.7) |

## 19. Open questions

- **Q1 — key spelling.** `workflows.<name>.config_path` follows naming.md's
  `_path` rule but collides in prose with the Snakefile-local `config_path`
  variable. Alternative: `workflow_config`, mirroring `model_build_config`.
  Reviewer call; no design consequence either way.
- **Q2 — should the declared cross-section read set become a checked contract?**
  §9 refuses *undeclared* cross-workflow sharing but leaves declared cross-section
  reads (WF3 → `workflows.build_model.wflow_outvars`) governed only by
  `guarded_sections`. A test asserting that every cross-section read in the
  Snakefiles is covered by that tuple would close the last gap — but writing it
  means parsing the Snakefiles, which may cost more than it buys.
- **Q3 — should `split_project_config.py` be retired after the migration?** The
  prune tools are permanent; a migration tool arguably is not. Recommend keeping
  it one release cycle, then deleting it rather than carrying a map for its own
  sake (the repo's stated stance on migration maps).
- **Q4 — should `run_workflows.py` preflight the `config_path` values?** Cheap and
  in the spirit of `_check_wf1_leaves`, but it makes the wrapper resolve config
  files it otherwise never opens. Deliberately out of scope here (§12.1).
- **Q5 — naming (owner ruling).** §14 recommends Candidate A. If B or C is ruled,
  §14.4 row 15 requires it to land as a separate series *after* the config split
  is baseline-verified.

## 20. Revision log

| Version | Date | Change |
|---|---|---|
| v1 | 2026-08-20 | Initial draft for gate G1. Incorporates the intake's five confirmed scoping rulings and the post-stage-0 scope amendment (R13 milestone wiring; workflow-naming section). Decides the two questions the intake left open: `reporting:` moves to the WF3 T2 file with a loader hoist (§10.4); clean break rather than backward compatibility (§15.1). Adds new empirical premises N1–N8. |
