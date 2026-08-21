# R13 — Config modularization: Design (DRAFT v3)

> **Status: DRAFT v3** — v2 (revised against the internal three-lens panel:
> 52 findings, 5 blocking / 27 major / 20 minor) further revised against
> **external round 1** (4 major findings, `ext1-1..ext1-4`; verdict `revise`).
> Two of the four implement owner rulings recorded at gate-clarifications
> (S7 staging-emit, S8 narrow G4 — §5). Dispositions are in `ledger.md` beside
> this file; every finding ID is answered there, and the sections below carry
> the resolutions. Awaiting human gate **G2**.
> **Milestone:** R13 (config surface as the first modularization seam).
> R12 is taken by the open WF3 execution-model milestone (`dev/roadmap.md:1462`),
> so this work is R13 per the scope amendment. The accepted design lands at
> `dev/milestones/r13/`; the run directory keeps the `config-modularization` slug.
> **Genre:** decision-record (milestone design), per the repo's
> `dev/milestones/*/ *-design.md` house style.
> **Author role:** cst-architect. **Run:** `config-modularization`.
> **Scope authority:** `dev/working/design-runs/config-modularization/intake.md`
> — its five *Confirmed scoping rulings* and its *Scope amendment* are fixed
> anchors and are not reopened here. The G1 framing (path-referenced
> composition; naming Candidate A provisional; clean-break migration with a
> report-only split script) is settled; every finding below is resolved
> **inside** it.
> **Body: v2 measured 2719 lines**, against v1's 1341; r2's growth is confined
> to the four external findings' resolutions and their forced cross-references.
> A mid-revision header predicted
> 1500–1800; the finished count is the fact and replaces the prediction. The
> growth is nameable rather than accretive. Eight findings
> (`repofit-1/3/6/7/12`, `arch-19/20/21`, `risk-8`) converge on a single
> obligation — the design must name **every test module the split touches and
> give each an expected-result line** (§16.2) — and the panel additionally
> forced ten verified premises (N9–N18), nine new decisions and one reversal,
> each of which had to be argued rather than asserted. Superseded v1 prose was
> cut to pay for part of it: §14's candidate arguments are compressed now that
> Candidate A is provisionally ruled, and §10.4's retrigger argument is
> corrected down to its load-bearing sentence.
> This document is self-contained: a reviewer needs only this file plus the
> cited paths.

---

## 1. Problem statement

One `snake_config_*.yml` carries `project:` + `shared:` + all four
`workflows.<name>:` blocks. Every project copy and every shipped variant
therefore duplicates every workflow's parameters, including the workflows that
project will never run: `snake_config_wf2_fast.yml` exists solely to iterate WF2
and still carries full `analyze_climate`, `build_model` and `run_stress_test`
sections. The duplication is not only in the source tree — it is baked into each
project's own record, where the workflow-scoped snapshots are **byte-identical
whole-config copies**: the three that are baseline targets all carry SHA-256
`00ef44f7fef2…` in `dev/baseline/manifest.json` (N5). The single file is also
the coupling point that works hardest against workflow-as-module modularization,
while simultaneously doing one valuable job that must survive any split: forcing
cross-workflow keys into one place where they cannot disagree.

**Two v1 factual claims are corrected here** (`risk-13`, `risk-10`), because both
were load-bearing further down:

- v1 said the current file carries "a top-level `reporting:`". **It does not.**
  All four `test_case/snake_config_*.yml` and
  `config/templates/snake_config.template.yml` have top-level keys exactly
  `['project', 'shared', 'workflows']`; the only occurrence anywhere in shipped
  material is a **commented** example block at
  `config/templates/snake_config.template.yml:210` (`#reporting:`) (N9).
  `reporting:` is a documented-but-unused surface. §10.4 is rewritten on that
  footing, and §16.2 gates the hoist with a fixture that actually declares it.
- v1 said "three snapshots". There are **four** workflow-scoped config
  snapshots — three under `config/runs/` (`analyze_climate.smk:329,357`,
  `build_model.smk:452,486`, `analyze_projections.smk:752,848`) plus the
  experiment-scoped `experiments/<exp>/config/snake_config_run_stress_test.yml`.
  **Three of the four are baseline targets**; the wf0 snapshot is not (N10).
  "Three" is the count of *targets*, not of *files this change affects*, and §16
  says so wherever the number appears.

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
  produce identical DATA targets. The three config-snapshot baseline targets are
  the single declared exception (§16.3).
- **G4** — **narrowed by owner ruling** (S8, gate-clarification 2026-08-21,
  resolving `ext1-3`): the `--configfile` path contract (one T1 path, same
  flag), the wrapper invocation surface, and `config_path` forwarding to
  downstream scripts are unchanged. G4 claims nothing about the `--config`
  override surface: ad-hoc overrides of **workflow settings** are withdrawn,
  not preserved — v2 booked that as a deliberate behavior change while stating
  G4 broadly, which external round 1 correctly called a papered-over
  CLI-contract break. §8.5b carries the form-by-form migration mapping.
- **G5** — a mechanical, bounded migration for existing projects, with a
  parse-time error that names the migration document. **"Bounded" is now
  quantified rather than asserted**: §15.6 states the compute cost of the first
  post-migration run, which v1 booked nowhere (`risk-16`).
- **G6** — a workflow-naming recommendation with its full surface inventory
  (scope amendment §2), decidable by the owner at G2 without reopening anything
  else in this design.

### Non-goals

- Implementation. This design hands off as a `task-brief` after G2.
- Changing what any workflow computes, or any model-config semantics.
- Moving `constraints:` / `runtime:` into project space.
- Data-catalog redesign — `config/catalogs/` stays exactly as it is.
- Web GUI/API accommodations; CST-API and CST-frontend never constrain this repo.
- Splitting `config/advanced_settings.yml` into per-workflow FILES. Its interior
  organization is ruled in §13; **relocating any existing key inside it is
  removed from R13's scope** by D-13.4, because that move is not digest-neutral
  and would blunt §16's falsifier (`arch-11`).

## 3. Constraints (standing; restated)

- This repo is the workflow engine only. Nothing couples config design to the
  CST-API/GUI.
- Model configs stay hydromt / hydromt_wflow / wflow conventions verbatim.
- The `get_config` contract is preserved verbatim: present key returned as-is
  including `None`; absent + required raises `ValueError`; absent + optional
  returns the default (E1, re-verified at `snake_utils.py:595-627`).
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

Criterion 3's "CLI … unchanged" is read under the **narrowed G4** (S8, §2): the
`--configfile` contract, the wrapper, and the forwarding — not the `--config`
override surface, which is withdrawn for workflow settings by the same ruling
(§8.5b). The criteria themselves are the intake's and are not edited.

## 5. Settled framing (owner rulings — not reopened)

Restated so this document is self-contained. Sources: intake *Confirmed scoping
rulings* 1–5 and *Scope amendment* 1–3; **S7 and S8 were ruled at
gate-clarifications during external round 1** (`status.md`, 2026-08-20 and
2026-08-21) and carry the same standing.

| # | Ruling |
|---|---|
| **S1** | Three user-facing tiers: T1 project config (`project:` + `shared:` + per-workflow enable switches), T2 one config file per workflow, T3 model configs unchanged. |
| **S2** | Composition by **path reference** from T1, single `--configfile` CLI contract unchanged. CLI multi-configfile merge considered and rejected (§17.1). |
| **S3** | `config/advanced_settings.yml` stays a separate toolbox-level file. Its boundary is **authority**, not topic; `constraints:` and `runtime:` never move into user-editable files; workflow-specific entries are namespaced *inside* it as it grows. |
| **S4** | Shared-seam rule: any key read by more than one workflow lives in T1, never in a T2 file — **enforced by the loader**, not by convention. |
| **S5** | `shared.seed` and `shared.water_year_start` remain per-project overrides of `defaults:`; `min_historical_years` remains a constraint. Advanced per-workflow knobs a project may set live as optional keys in that workflow's T2 file. |
| **S6** | This is milestone **R13**. Workflow naming is in scope: candidates + one recommendation (§14); the choice itself is an owner ruling, provisionally Candidate A at G1 and final at G2. |
| **S7** | **Staging-emit** (ruled 2026-08-20, resolving `ext1-2`): `split_project_config.py` is strictly report-only against user files — it emits the proposed T1 + T2 into a staging directory plus a migration report, and application is an explicit user step outside the script. No `--write`, no in-place mutation, no opt-in mutation mode (§15.3). |
| **S8** | **Narrow G4** (ruled 2026-08-21, resolving `ext1-3`): G4 covers the `--configfile` path contract, the wrapper invocation, and `config_path` forwarding — nothing more. Ad-hoc `snakemake --config` overrides of workflow settings are **withdrawn**, not preserved: an override that bypasses the T2 file is exactly the shared-seam hole D-9.1 exists to close. Routing overrides into the composed T2 before validation was offered and declined (§8.5b, §17.4). |

Two questions the intake left **open** were decided in v1 and stand: where
top-level `reporting:` lives (§10.4 — the WF3 T2 file, hoisted) and backward
compatibility versus a clean break (§15.1 — clean break with a parse-time
migration error). This revision adds one decision of equal weight that v1 got
wrong by omission: **how a `config_path` resolves** (§8.4), which v1 answered by
analogy and which is unimplementable for an out-of-tree project as v1 stated it
(`repofit-2`). §8.4 is the one place this revision reverses a v1 decision, and it
is flagged **owner-visible** at G2.

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

### 6.2 Premises verified for v1, carried forward

| # | Premise | Citation | Why it matters |
|---|---|---|---|
| **N1** | `config_path` is a declared rule **input**, not merely a param, in **six** rules: `analyze_climate.smk:344`, `build_model.smk:467`, `build_model.smk:535`, `analyze_projections.smk:836`, `run_stress_test.smk:621`, `run_stress_test.smk:836` (under `ancient()`). | as cited | The source config file is a DAG edge. **v1 said "five" and listed six** (`arch-15`); the list was right, the count wrong. Two lenses independently re-derived the same six by grep. |
| **N2** | `prepare_weagen_config.py:89-91` re-reads the source config **from disk** and indexes `yml_snake["workflows"]["run_stress_test"]`. | as cited | One of the two consumers that would see a T1 file with no workflow settings in it. |
| **N3** | The project snapshot is a **verbatim byte copy**: `copy_config_files.py:222` `shutil.copyfile(...)`. `_RUNS_README` (`:60-93`) documents the resulting byte-identity as expected. | as cited | Under a split, one byte copy no longer captures what the run used. |
| **N4** | Path keys resolve against the **current working directory**, not against the config file: `test_case/snake_config_rapid.yml:17`; `build_model.smk:125-126`. | as cited | v1 used this to fix T2 resolution by consistency. §8.4 now records the limit of that argument: **no existing key references a sibling of the config file**, so N4 does not actually cover the T2 case (`repofit-2`). |
| **N5** | The three baseline-target config snapshots are byte-identical: `dev/baseline/manifest.json:9-30` records SHA-256 `00ef44f7…` for `config/runs/snake_config_analyze_projections.yml`, `config/runs/snake_config_build_model.yml`, and `experiments/experiment/config/snake_config_run_stress_test.yml`. | as cited, re-confirmed by direct load | Proves the snapshot duplication empirically, and pins which baseline targets this refactor may move (§16.3). |
| **N6** | The WF3 drift guard compares each guarded section against the snapshot of the workflow that **owns** it: `check_project_consistency.py:166-182`; the wf2 snapshot is read **only when it exists** (absent → unchecked and logged). | as cited | Determines what a composed snapshot must contain, per workflow. |
| **N7** | All four shipped seeds' `workflows.<name>` sections differ pairwise; `snake_config_baseline_linux.yml` differs in `project`, `shared` **and** `workflows`. | `python -c` diff, 2026-08-20 | The seed set has no free T2 sharing today, which bounds what criterion 2 may claim (§18). |
| **N8** | `prepare_cst_parameters.py:162-165` re-reads the source config from disk and indexes `yml["workflows"]["run_stress_test"]["stress_test"]`. | as cited | The second such consumer. |

### 6.3 New premises verified for this revision

Verified in this worktree on 2026-08-20 by direct read or execution. These are
the premises the panel's findings turn on, re-checked rather than accepted.

| # | Premise | Citation | Why it matters |
|---|---|---|---|
| **N9** | `reporting:` appears in **no** shipped config. `yaml.safe_load` over all four `test_case/snake_config_*.yml` and the template returns top-level `['project','shared','workflows']` in every case; the sole textual occurrence is `config/templates/snake_config.template.yml:210` → `#reporting:` (commented). | direct load + grep | Corrects §1 and §10.4, and makes the hoist a permanently-untested loader special case unless §16.2 adds a fixture (`risk-13`, `arch-16`). |
| **N10** | **Four** workflow-scoped snapshots exist, three of them baseline targets. Writers: `analyze_climate.smk:329,357`; `build_model.smk:452,486`; `analyze_projections.smk:752,848`; and the experiment-scoped WF3 path. `dev/baseline/manifest.json` has exactly **7** targets — 3 `type: yaml` snapshots (wf1, wf2, wf3-experiment), 2 `type: csv` change-factor tables, 1 `type: indicator`, 1 `type: discharge`. The **wf0 snapshot is not a target**. | grep over `*.smk` + `json.load` of the manifest | Settles conflict 3 of the review index: the file count is four, the target count is three, and §16.3's "exactly three" prediction **stands unchanged**. |
| **N11** | `dev/scripts/snapshot_project_tree.py` loads the config **raw** (`:219` `yaml.safe_load`) and derives run parameters at `:69-89`, reading `workflows.run_stress_test.experiment_name` with fallback `"experiment"` (`:84`) and `workflows.analyze_projections.clim_project` with fallback `"cmip6"` (`:87`). `pixi.toml:185` pins `tree-check` to `test_case/snake_config_baseline.yml`, whose values are `experiment_name: experiment` (`:61`) and `clim_project: cmip6` (`:40`). | direct read of all four files | **Settles conflict 1**: `risk-1`'s silent-masking mechanism is real and the pinned gate cannot detect it, because the seed's values equal the tool's fallbacks exactly. See §16.5. |
| **N12** | `run_record.yml`'s and `journal.jsonl`'s `configuration_inputs_sha256` **do agree today** for the same run, observed rather than argued: `build_model` run_record `4ec140e5…`/eff `1912b6b8…` matches a journal line carrying the same pair; `analyze_projections` run_record `30dfea76…`/eff `401dab0d…` likewise. | `yaml.safe_load` of both `run_record.yml` under `test_case/test_local/config/runs/` + a scan of `journal.jsonl` | Settles the premise `arch-4` self-flagged as argued-not-run. The equality is real, so registering T2 bytes on one side only **would** break it. `arch-4` stays major; its "drops to minor" condition did not trigger. |
| **N13** | `run_stress_test.smk:41` reads `config["workflows"]["run_stress_test"]`, while `guarded_sections` is constructed at `:332-335` and `CONFIG_PROJECTION` at `:362-366` — ~300 lines below. | direct read | Confirms `arch-1`: v1's "composition runs before any other module-level code" and "R(entry) is derived from the Snakefile's own declarations" cannot both hold without a hoist. §8.2 specifies it. |
| **N14** | `run_stress_test.smk:384-391` records that the wf2 **snapshot** is a params path rather than a mandatory input "because the projections overlay is optional and must not be force-required" — while `workflows.analyze_projections` is nonetheless inside `guarded_sections` (`:332-335`) and therefore inside `CONFIG_PROJECTION`, so the **section** is already hard-required at parse. | direct read | Bounds `arch-8` precisely: the split does not create a WF2 requirement, it would upgrade an existing *section* requirement into a *file* requirement. D-8.7 declines that upgrade. |
| **N15** | `compare_copied_config` (`dev/scripts/semantic_tree_diff.py:887-906`) parses both snapshots and requires **deep structural equality**; its docstring states that "an unmapped path, a changed non-path value, a missing/extra key — FAILs". | direct read | `arch-21`: this gate adjudicates snapshot CONTENT, not tree shape, so D-11.1 gives it a predictable failure that §16.4 must state in advance. |
| **N16** | `tests/conftest.py:136-145`'s `model_build_config` fixture calls `get_config(config["workflows"]["build_model"], "model_build_config", optional=False)` against a raw `yaml.safe_load` of the fixture config (`:113-118`), with no composition anywhere in the chain. | direct read | `arch-19`: the central shape change breaks a fixture in the one test layer AGENTS.md says skips rather than fails outside the primary checkout. |
| **N17** | 16 test modules reference `tests/snake_config_fixture.yml` directly; 20 index `["workflows"]` or build a `"workflows":` dict literal; the union of modules touching any shipped-config or config-shape surface is **45**. `tests/snake_config_fixture.yml` is itself inline-shaped (its `build_model` section carries `model_build_config`, `waterbodies_config`, `wflow_outvars`, `observations_timeseries`). | `rg -l` sweeps + `yaml.safe_load` | The measured base for §16.2's three-tier inventory. Confirms `repofit-1`: the clean break disables the design's own primary gate until the fixture is split. |
| **N18** | `tests/test_experiment_allocation.py:83,185-206` writes and reads `workflows.run_stress_test.experiment_name` through `runner.main` on a temp config. | direct read | **Named by no lens.** It breaks with `tests/test_suggest_experiment_name.py` under §12.3 and is added to §16.2 tier 1 — the concrete return on `risk-8`'s demand for an inventory rather than a sweep. |

## 7. Target layout — T1, T2, T3

### 7.1 D-7.1 — T1, the project config

One file, the sole `--configfile` target. Three top-level sections — and, by
D-9.5, **exactly** those three:

```yaml
# test_case/snake_config_rapid.yml  (the shipped seed shape)
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

workflows:                     # SHAPE CHANGES: each block is at most two keys
  analyze_climate:
    enabled: true              # no config_path: this workflow has no settings (D-8.7)
  build_model:
    enabled: true
    config_path: snake_config_rapid_build_model.yml
  analyze_projections:
    enabled: true
    config_path: snake_config_rapid_analyze_projections.yml
  run_stress_test:
    enabled: true
    config_path: snake_config_rapid_run_stress_test.yml
```

**The example paths changed in v2** (`repofit-5`). v1's canonical block pointed
every `config_path` at `config/workflows/<name>.yml` — a bin AGENTS.md rules out
by name ("There is **no `workflows/` bin**"), retired when the configs moved out
of `config/workflows/` in R06, and inconsistent with v1's own §7.4 and §15.3. It
also named a path inside the *toolbox* checkout, which is where AGENTS.md says
project configuration must never live. The block above is what the splitter
actually produces, resolved as §8.4 specifies. `snake_utils.py:858-860`'s
docstring carries the same stale `config/workflows/snake_config_*.yml` spelling
and is on §16.6's sweep list.

Each `workflows.<name>` block carries a **closed schema of at most two keys**:
`enabled` (required, must parse to a bool — E7's existing validation, unchanged)
and `config_path` (**optional**, per D-8.7; when present it must resolve). Any
third key is rejected at parse time. That closure is doing three jobs at once: it
is half the seam enforcement (§9), it is the migration detector (§15.2), and it
is what keeps a T1 from quietly growing back into today's file.

**The migration adds no key, anywhere.** The three optional `shared:` overrides
above are illustrative. `effective_config_document` digests the config *mapping*,
so a key that is **present** rather than absent changes the canonical JSON and
therefore `effective_config_digest`, even when the resolved value is identical
(E2's resolver-substitution path makes `seed: 123` and an omitted `seed` produce
the same run and different digests). Adding one during migration would break
§16.3's digest-equality test and, through `_frozen_differences`' key-union diff,
refuse every already-run experiment in the project. This is the same invariant
D-10.1 states for `enabled` / `config_path`, applied to `shared:`: **composition
moves keys between files; it never creates or drops one.** D-8.7 is what lets
that invariant hold for a section whose body is empty — an omitted `config_path`
adds nothing, where a pointer to an empty file would add a file.

`config_path` is named per `dev/reference/naming.md`'s `_path` rule for
path-valued keys. **Q1 is closed in favour of `config_path`** (§19), on
`repofit-11`'s reasoning: naming.md §3 makes `_path` mandatory for new code
holding a file-path string, the proposed alternative `workflow_config` reads as a
loaded mapping (`_cfg` territory) which is exactly what the key is not, and
`model_build_config` is a grandfathered spelling naming.md itself flags for this
class of rename (`naming.md:486`). Where the prose collision with the
Snakefile-local variable matters, this document renames the *variable* — §8.2's
snippet uses `t1_path`.

### 7.2 D-7.2 — T2, one file per workflow

A T2 file's **top level is the workflow's own section body** — today's
`workflows.<name>:` block with `enabled:` removed and two levels of indentation
stripped. Nothing is renamed and nothing changes meaning:

```yaml
# test_case/snake_config_rapid_build_model.yml
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
buys a redundant self-identification that the T1 reference already supplies.

Note that the values inside a T2 file keep resolving **CWD-relative**, exactly as
they do today — `model_build_config: config/defaults/…` above is a toolbox path
read from the repo root. Only the `config_path` key that *points at* a T2 file is
anchored differently (§8.4). That asymmetry is deliberate and argued there.

**One exception, declared:** the WF3 T2 file also carries a top-level
`reporting:` key, which the loader hoists back to `config["reporting"]` rather
than merging into `workflows.run_stress_test`. See D-10.4 — a two-entry closed
map in the loader, not a general mechanism, and now defended in both directions
(D-9.2 rejects `reporting:` in a non-owning T2 file; D-9.5 rejects it at T1's top
level).

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
| A real project's T2 | **beside T1**, `<t1_dir>/<t1_stem>_<name>.yml` — never under `project_dir` | `/basins/gabon/snake_config_gabon_build_model.yml` |

**The real-project row changed in v2** (`arch-9`). v1 recommended
`<project>/config/<name>.yml`, which in this repo reads as
`<project_dir>/config/` — the bin `copy_config_files.py:60-93` documents as
"Everything here is written by the run. Editing any of it changes nothing", and
the tree `dev/scripts/semantic_tree_diff.py:338-390` enumerates leaf by leaf. A
hand-authored SOURCE file there is an undeclared path, so `pixi run tree-check`
would fail — on the very gate §16 nominates to detect a leaked copy, producing a
false positive the design manufactured itself. **A T2 file must not live under
`project_dir`**, for the same source-versus-record reason §11.1 gives for comment
loss, and the recommended location is now the one the splitter actually produces.

The seed T2 pattern sits **inside** the E9 glob: `!test_case/snake_config_*.yml`
matches `snake_config_rapid_build_model.yml`, so the files are tracked with **no
`.gitignore` change**. **Demonstrated**, not inferred, and independently
reproduced by two lenses: `git check-ignore -q
test_case/snake_config_rapid_build_model.yml` exits 1 — not ignored — identically
to `test_case/snake_config_rapid.yml`, while `test_case/my_seed.yml` exits 0 and
`test_case/workflows/build_model.yml` exits 0. A `test_case/workflows/`
subdirectory is therefore rejected for the reason E9 records for the basin CSVs.

**But the tracking glob is not the only consumer of that glob shape**
(`repofit-3`, blocking). `tests/test_prepare_cst_parameters.py:364-378`
parametrizes over `glob.glob(REPO_ROOT/"test_case"/"snake_config_*.yml")` and
indexes `cfg["workflows"]["run_stress_test"]["stress_test"]`. Any T2 name that
`.gitignore` tracks, that glob also discovers — the two cannot be separated by
naming, because tracking *is* the glob. **Resolution: fix discovery, not the
name.** A T1 file is identified by a positive predicate — *its top level contains
a `workflows:` key* — and the test then reads `stress_test` from the **composed**
document via `compose_config`, which is a better test than reading raw YAML
because it exercises the same path a run takes. §16.2 carries the expected
result. Recorded alongside: `test_case/snake_config_baseline_build_model.yml` (a
seed T2 *source*) and `config/runs/snake_config_build_model.yml` (a composed
project *record*) now differ by one path segment, so **a bare
`snake_config_build_model` grep conflates two file classes with opposite
meanings** — §16.6's sweep must anchor on the directory, not the stem.

**Cost, stated plainly and now measured.** The shipped seed set grows from 4
files to 4 T1 files plus **up to 12** T2 files, not 16: three of the four seeds
and the template declare `analyze_climate: {enabled: ...}` and nothing else
(N7), so their wf0 body is empty — and under D-8.7 an empty body needs **no file
at all**, only an omitted `config_path`. v1's accounting booked four
content-free files as part of the cost and offered reconciliation as their
mitigation; reconciliation cannot reduce a file that is empty by construction
(`risk-14`), so D-8.7 removes them instead.

For the remaining files, N7 measured that no two current variants share a
workflow section verbatim, so the implementation cannot collapse them today
purely by inspection. The implementation brief must (a) reconcile the variants
where a difference is incidental rather than deliberate, and (b) point several T1
files at one shared T2 wherever they then agree.

**Sharing is ruled IN for the wf0/wf1/wf2 T2 files and OUT for the WF3 T2 file**
(`risk-5`). §12.3 makes `suggest_experiment_name.py` splice `experiment_name`
into the WF3 T2 file **in place**, and `experiment_name` is per-project by nature
(`rapid` sets `experiment_rapid`, `baseline` sets `experiment`). A WF3 T2 shared
between two T1 files would make naming one project's experiment silently
re-point the other's — after which a baseline run writes to `experiments/X/` and
the baseline target
`test_case/test_local/experiments/experiment/config/snake_config_run_stress_test.yml`
goes **missing**, so §16.3's falsifier reports a missing target rather than a
drift, on a change nobody made to the baseline config. Nothing at parse time can
see two T1 files pointing at one T2 (§8.4's duplicate check sees only within one
T1), so this is a rule the implementation brief states and a reviewer enforces —
not a check. §18 books the reduced file count with that constraint attached, not
without it.

## 8. Loader semantics

**Module placement changed in v2** (`repofit-9`). v1 put `compose_config`, three
seam checks, `SHARED_SEAM_KEYS`, `HOISTED_SECTIONS`, path resolution and six
error messages into `blueearth_cst/shared/snake_utils.py` — already 4658 lines,
and the single module AGENTS.md names in its write-set declaration rule as the
seam that makes two otherwise-unrelated tasks non-independent. Concentrating a
new contract surface in the highest-contention file in the repo raises the cost
of every concurrent slot for the life of the repo, for no cohesion gain a sibling
module would not also have — and `shared/` has clear topic-module precedent at
this size and contract weight (`interchange_contracts.py` 1338 lines,
`provenance.py` 686, `climate_window.py` 280).

> **All composition machinery lands in
> `blueearth_cst/shared/config_composition.py`**, imported directly by the four
> Snakefiles as they already import `interchange_contracts`. Nothing is
> re-exported from `snake_utils`, so there is one import path and no second
> spelling. §16.2's `tests/test_config_composition.py` then names its module,
> which is the repo's dominant test-naming pattern.

`get_config` stays exactly where it is and is untouched.

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
The panel's architecture lens re-derived this independently and could not
construct a case where a merged-dict reader sees a different value than it sees
today; that clearance stands.

Every deviation from shape preservation is therefore a design defect unless
explicitly listed. **Two are listed.**

1. *The narrowing.* For a single-entry-point invocation the merged `config`
   carries only the workflow sections that entry point requires (§8.3), so
   `config["workflows"]` may hold fewer than four **fully-populated** sections.
   §10.7 shows that no reader is affected.
2. *The binding.* The invariant is a statement about the mapping bound to the
   Snakefile-global name `config`, and **only** about that binding — see D-8.6.

One thing the invariant does **not** cover, and v1 implied it did: the invariant
holds for readers that go through the composed dict. Five tools, one conftest
fixture and the test suite's dominant config idiom do not (§12.0, §12.5). The
invariant is not weaker than v1 claimed — its *scope* was overstated.

### 8.2 D-8.2 — Where composition happens, and what it is handed

v1's snippet showed `compose_config(config, config_path, entry="build_model")` —
three arguments, none of which carries a projection — while §8.3 said `R(W)` is
computed "from the same `CONFIG_PROJECTION` / `guarded_sections` declarations the
Snakefile already maintains — passed in, not duplicated". **There was no channel
to pass them** (`arch-1`), and the ordering could not hold either: `R(entry)`
must be known before the first section read, but `run_stress_test.smk:41` reads
`config["workflows"]["run_stress_test"]` while `guarded_sections` is not
constructed until `:332` and `CONFIG_PROJECTION` until `:362-366` (N13). An
implementer facing that gap has two bad options — restate the workflow list
inside the loader, which §8.3 forbids by name, or restructure four Snakefiles in
a way v1 neither specifies nor budgets.

**D-8.5 — The composition contract, stated implementably.**

```python
# blueearth_cst/shared/config_composition.py

def compose_config(
    t1: Mapping[str, Any],          # the parsed --configfile mapping, post --config overrides
    t1_path: str | os.PathLike,     # workflow.configfiles[0]; the resolution anchor (D-8.4)
    entry: str,                     # the entry point's own workflow key
    declared_sections: Sequence[str],  # this Snakefile's CONFIG_PROJECTION literal
) -> tuple[dict[str, Any], dict[str, str]]:
    """Return (composed_config, workflow_config_paths)."""
```

- **`declared_sections`** is the channel `arch-1` found missing. It takes the
  Snakefile's own `CONFIG_PROJECTION` tuple — the maintained list of the sections
  this entry point reads. `R(entry)` is then
  `{entry} ∪ {s.split(".")[1] for s in declared_sections if s.startswith("workflows.")}`,
  derived, never restated. For WF3 that yields
  `{run_stress_test, build_model, analyze_projections}` because WF3's
  `CONFIG_PROJECTION` is itself derived from `guarded_sections`
  (`run_stress_test.smk:362-366`) — the drift protection that Snakefile comment
  argues for is preserved end to end, with the loader as one more consumer of the
  same literal rather than a second copy of it.
- **Returns a tuple**, so the second element is an explicit part of the contract
  rather than "a module-level side product the Snakefile also binds" (v1's
  wording, which specified no mechanism). `workflow_config_paths` maps each
  loaded workflow name to its resolved path (§8.4); it is what §10.3 declares as
  rule inputs, what §10.5 registers in `CONFIG_REFERENCES`, and what §11 hands to
  the snapshot writer.
- **Pure.** No I/O beyond reading the T2 files it is told to read; no global
  state; importable and callable outside Snakemake, which §12.0 depends on.

**The call site**, with the hoist stated:

```python
# every Snakefile, immediately after the configfile is known
t1_path = workflow.configfiles[0]           # renamed from config_path (§7.1, Q1)
config_path = t1_path                       # the forwarded name is UNCHANGED (E5, §12.4)

# HOISTED: config-independent literals, moved above the compose call.
guarded_sections = (...)                    # WF3 only, verbatim from :332-335
CONFIG_PROJECTION = (...)                   # verbatim, incl. WF3's derivation from the above

config, WORKFLOW_CONFIG_PATHS = compose_config(
    config, t1_path, entry="run_stress_test", declared_sections=CONFIG_PROJECTION,
)
```

The hoist is **mechanical**: `guarded_sections` and `CONFIG_PROJECTION` are
string literals (and, in WF3, a set expression over string literals) with no
config dependency at all, so moving them above line 41 changes no value. Two
obligations follow, and both are named rather than left to discovery:

- `tests/test_snapshot_config_rules.py:122-126` pins the exact
  `CONFIG_PROJECTION = ("project", "shared", "workflows.build_model")` literal
  per Snakefile, and `:129-141` pins that `run_stress_test.smk` contains
  `CONFIG_PROJECTION = tuple(sorted(` and `for section in guarded_sections`
  (`arch-20`). The hoist must carry the literals **verbatim**, including WF3's
  derivation expression — which is also §14.3's independent reason to leave those
  strings alone. §16.2 gives the module its expected-result line.
- Composition runs **before** any other module-level code that reads a section,
  so every existing parse-time refusal (`refuse_retired_experiment_keys`,
  `refuse_out_of_domain_multipliers`, `resolve_simulation_window`,
  `parse_surfaces`) sees the composed dict and needs no change.

### 8.3 D-8.3 — Which T2 files are loaded

**Not** "loaded iff `enabled: true`". WF3 reads two other workflows' sections
regardless of whether those workflows are enabled: `provenance.project_config`
raises `KeyError` at parse time when a declared projection path is absent
(`provenance.py:208-212`), and `run_stress_test.smk:537-540` reads the *meaning*
of `workflows.build_model.wflow_outvars` to derive the indicator tables before
the DAG is built. The rule is therefore:

> A workflow's T2 file is **loaded** for entry point `W` iff its workflow is in
> `R(W) = {W} ∪ {the workflows named in W's CONFIG_PROJECTION}`. Enablement does
> not enter into it.

| Entry point | `R(entry)` | Source |
|---|---|---|
| `analyze_climate` (wf0) | `{analyze_climate}` | `analyze_climate.smk:119` |
| `build_model` (wf1) | `{build_model}` | `build_model.smk:176` |
| `analyze_projections` (wf2) | `{analyze_projections}` | `analyze_projections.smk:57` |
| `run_stress_test` (wf3) | `{run_stress_test, build_model, analyze_projections}` | `run_stress_test.smk:332-335, 362-366` |

Workflows **outside** `R(entry)` have their T2 files neither resolved nor merged.
Their T1 stanza is still validated (D-9.1) and, from v2, their T2 file is still
*opened for a name-only duplicate check* where it resolves (D-9.3) — a read of
key names, never of values, so the narrowing in §8.1 is unaffected.

### D-8.7 — A declared-but-omitted `config_path` means `{}`

**New in v2.** It resolves three findings at once (`arch-8` major, `risk-14`
minor, `risk-15` minor) and it is the one place this design declines a
tightening that v1 introduced by accident.

> **`config_path` is optional in every `workflows.<name>` stanza.** When the key
> is **absent**, the workflow's section body is `{}` — exactly as if it pointed
> at an empty file, which §8.4 already accepts. When the key is **present**, the
> file must exist, parse, and be a mapping; anything else is a hard `ValueError`.

*The problem it fixes.* Under v1, `R(wf3)` made the `analyze_projections` T2
**file** a hard requirement of every WF3 run — a `ValueError` at parse, and once
D-10.3 landed, a rule-input surface too. That collides with a standing invariant
the design cites but never reconciles: `run_stress_test.smk:384-391` records that
the wf2 artifact is deliberately a params path rather than a mandatory input
"because the projections overlay is optional per the CST method and must not be
force-required" (N14). Today the WF2 obligation is *keep a stanza in a file you
already have*; under v1 it became *author and keep a separate file on disk for a
workflow you never run*. That is a real tightening of an explicitly protected
optionality — and it made v1's own headline benefit ("a project that never runs
WF0 needs no WF0 file at all") true for WF0 and false for WF2.

*Why omission is safe, in the order the argument actually runs.*

1. **The splitter always emits a `config_path` for a section that had content**
   (§15.3). Omission is therefore a *deliberate act* by a user editing T1, never
   a migration artifact. This is the durable half of the argument.
2. **The resulting behavior is identical to today's.** A composed
   `workflows.analyze_projections = {"enabled": false}` is byte-for-byte what a
   project that carries a minimal stanza produces today — a shape both
   `provenance.project_config` (the path exists, so no `KeyError`) and
   `guarded_sections_digest` already handle. Nothing new is possible.
3. **For an already-run project the drift guard also sees it.** Deleting a
   `config_path` changes `workflows.build_model` in the composed dict, which
   moves `guarded_sections_digest` and re-fires rule 3.01 against the recorded
   snapshot. This is genuine but **secondary and scoped**: with no wf1 snapshot on
   disk `file_digest_or_absent` returns `"ABSENT"` and nothing is compared, so it
   protects a project that has already run WF1 and not a fresh one.

*The residual, stated.* A user who deletes both a T2 file and its `config_path`
key for a workflow whose settings mattered gets that workflow's **defaults**, not
an error — `run_stress_test.smk:537-540` reads `wflow_outvars` with
`optional=True` and falls back to `DEFAULT_WFLOW_OUTVARS`. That is today's
behavior for an empty section, preserved deliberately rather than introduced. The
distinction the design leans on is that deleting a *file* while leaving the key is
a hard error (a typo cannot pass), whereas deleting the *key* is a two-step
edit that says what it means.

*Three consequences.* (a) `arch-8`'s tightening does not happen; the overlay's
config file is not mandatory. (b) `risk-14`'s four content-free wf0 files are not
created (§7.4). (c) `risk-15`'s migration advice inverts: step 3 of §15.5 now
says **delete the `config_path` key**, never "leave it pointing at a path that
does not exist" — a dangling path is precisely the hard error this rule keeps.

### 8.4 D-8.4 — Path resolution: anchored at the T1 file **(reversal; owner-visible)**

**This reverses v1.** v1 resolved a relative `config_path` against the current
working directory, argued from N4's consistency: every other path key in the same
file already resolves that way. `repofit-2` (blocking) showed the argument does
not reach this key and that the v1 rule is **unimplementable for the population
the migration exists to serve**.

*The defect.* AGENTS.md places a production `project_dir` — and with it the
project's own config, since "every shipped `--configfile` target lives beside the
project it writes into … which is how a real project is laid out too" — **outside
the repository tree**. §15.3's splitter writes T2 files beside T1. Under
CWD-relative resolution the splitter must then emit either an absolute path
(correct, but non-portable and unlike every worked example) or a relative one
that resolves against the repo root and therefore does not exist. It cannot emit
one that both resolves and matches the design's own examples. The defect is
invisible in every worked example because `<t1_dir>` for all four shipped seeds
is `test_case/`, which *is* under the repo root — so §8.4 and §15.3 coincide for
the seeds and for `test_cli`, and diverge only for real projects.

*The decision.*

> A `config_path` value is `os.path.expanduser`-ed, then, if still relative,
> resolved **against the directory containing T1**. Absolute paths are used as
> given. The resolved path is stored in `workflow_config_paths` as a
> CWD-relative path when one is computable, and as an absolute path otherwise.

*Why this key differs from every other path key, principledly.* N4's consistency
argument covers keys that reference an **external input** — a data catalog, a
basin CSV, a model-config default, an output root — whose natural anchor is the
invocation, and each of which the toolbox or the environment supplies.
`config_path` is the only key that references **a fragment of the config document
itself**: a file the same author wrote at the same time, shipped and moved as one
unit with T1. Anchoring a document's own fragments at the document is what makes
a project's config set relocatable, which is exactly the property a T1-plus-T2
layout needs and a single file got for free. No existing key tests the other
rule, because no existing key references a sibling of the config file
(`repofit-2` establishes this; N4 is corrected accordingly).

*The cost, stated because it is real.* A reader of T1 now sees two anchoring
rules three lines apart: `data_sources: config/catalogs/…` resolves from the
repo root, `config_path: snake_config_rapid_build_model.yml` resolves from T1's
directory. v1 rejected exactly this on the grounds that it "produces a support
question rather than a convenience", and that objection is not withdrawn — it is
outweighed. The mitigation is that the two are visually distinct in practice (a
`config_path` is a bare sibling filename; every other path key carries a
directory prefix) and that §8.4's error messages name the anchor explicitly.

*Alternative kept on the record.* Keep CWD-relative resolution and have the
splitter emit an **absolute** `config_path` whenever T1 is outside the CWD. It
works, requires no reversal, and is the smaller change. It was rejected because
it makes a project's config set non-relocatable and machine-specific — moving a
basin folder, or handing it to a colleague, breaks every reference — and because
it produces two different shapes of the same key depending on where the project
happens to sit, which is harder to document than two anchors.

> **Owner-visible at G2.** This is the one v1 decision reversed. If the owner
> prefers the alternative, §15.3's splitter and §16.2's path-resolution matrix
> change and nothing else in §§7–13 moves.

**Two mechanics, because they are where this goes wrong on this platform:**

- `workflow_config_paths` values must be resolvable by Snakemake from the
  **working directory**, since D-10.3 declares them as rule inputs. Hence the
  CWD-relative-when-computable rule above.
- On Windows `os.path.relpath` **raises `ValueError` across drives**. The rule is
  therefore "relative when computable, absolute otherwise", implemented as a
  caught `ValueError`, never as an assumption that a relative form exists. A
  project on `D:` driven from a checkout on `C:` is an ordinary case here.

**Failure behavior**, mirroring `get_config`'s fail-loud stance and
`run_workflows.py:270-274`'s existing message shape. Every message names the
resolved absolute path **and** the anchor it was resolved against:

| Condition | Behavior |
|---|---|
| `config_path` absent | **Accepted**: the section body is `{}` (D-8.7) |
| file not found | `ValueError` giving the resolved absolute path, the anchor directory, and the migration doc |
| file parses to something other than a mapping | `ValueError` naming the file |
| file is empty / parses to `None` | Accepted as `{}` |
| any key of `workflows.<name>` other than `enabled` / `config_path` | `ValueError` naming the key, the workflow, the T2 filename convention, the migration command, and `docs/migration-config-tiers.md` (§15.2) |
| a top-level T1 key other than `project` / `shared` / `workflows` | `ValueError` (D-9.5) |
| the same `config_path` referenced by two workflows **in one T1** | `ValueError`. Two workflows sharing one settings file would silently give each the other's keys, and the seam rule would have nothing to test against |

**The duplicate check compares `os.path.normcase(os.path.abspath(resolved))`**,
not the raw string (`risk-18`). A raw-string comparison is evaded by
`./build_model.yml` versus `build_model.yml`, a trailing separator, or a
case-only difference on Windows — and D-9.3 cannot substitute, because with one
file on disk there is only one file to compare. The repo has already paid for
this exact bug class one layer down: `copy_config_files.py:317-325` compares
destinations with `os.path.normcase(os.path.abspath(...))` rather than
`resolve()`, with a comment explaining that case-only differences "would collide
on a re-run and silently overwrite on a fresh one — the same file lost, but only
sometimes". Same comparison key, same reason. (`resolve()` is deliberately not
used, matching that precedent: it follows symlinks, and two deliberate symlinks
to one file are a user's choice rather than a typo.)

All of these raise at Snakefile parse time, before the DAG is built, so
`pytest tests/test_cli.py` is their gate — the same gate the repo's other
parse-time refusals already use (`run_stress_test.smk:518`, `:535`).

### 8.5 D-8.6 — The binding, and the `--config` passthrough

Two mechanisms sit *between* Snakemake and the composed dict. v1 named neither,
and each has a silent-failure mode (`arch-12`, `risk-9`, `risk-17`).

**(a) Composition must REBIND the Snakefile-global `config`.**

`check_project_consistency.py:225` takes its live config from `sm.config` — i.e.
Snakemake's `workflow.config` — not from the Snakefile's local name.
`workflow.config` returns `self.globals["config"]`
(`snakemake/workflow.py:1728-1729`) and the Snakefile is exec'd into
`self.globals` (`:1612`), so `config = compose_config(...)[0]` at module level
*does* reach every `script:` module. But that is a Snakemake implementation
detail, and nothing in v1 said the rebinding was load-bearing. §7.1's own Q1
anxiety about the `config_path` name is exactly the pressure that produces a
`composed = compose_config(...)` refactor — after which the drift guard compares
`{enabled, config_path}` against the snapshot's full `workflows.build_model` and
**every WF3 run fails at rule 3.01, after WF1 and WF2 have already run**, with a
message that blames project drift rather than the binding.

> **Invariant:** `compose_config`'s result is bound to the Snakefile-global name
> `config`, or the existing mapping is updated in place. Any other binding is a
> defect. Consumer of record: `check_project_consistency.py:225` via `sm.config`.

§16.2 gives `tests/test_config_composition.py` a case asserting the composed
shape is visible through `workflow.config`, so the invariant is checked rather
than documented.

**(b) `--config key=value` overrides apply to T1, before composition — and
workflow-setting overrides are WITHDRAWN (S8, owner ruling 2026-08-21).**

`scripts/plot_workflow_dag.py:50` documents `-- --config foo=bar` as a supported
passthrough and `scripts/run_workflows.py` sanitizes and records passthrough
`--config` overrides. Snakemake merges those into the config mapping before the
Snakefile body executes — hence before `compose_config` — and the merge is
**recursive for mapping values, replacing only leaves**
(`update_config`, `snakemake/utils.py:563-589`), a correction of v2, which said
an override of `workflows` "replaces the stanzas": a mapping-valued override
merges *into* them.

v2 called the resulting parse-time rejection of workflow-setting overrides
"correct and deliberate" while G4 still claimed the CLI contract unchanged.
External round 1 (`ext1-3`) correctly found that inconsistent, and the owner
ruled it at a gate-clarification: **narrow G4** (S8) rather than route overrides
into the composed T2 — a second write path into workflow settings is exactly
the shared-seam hole D-9.1 exists to close (§17.4). The withdrawal is the
clean-break posture (§15.1) applied to the one config surface that is not a
file.

**The migration mapping — every formerly supported override form, and where it
goes.** "Formerly supported" means: merged silently into the monolith today,
whatever it touched.

| Former form | After the split | Replacement |
|---|---|---|
| `--config workflows='{"<name>": {"<setting>": v}}'` — a workflow setting, recursively merged into that section | **parse-time rejection** (D-9.1: the stanza is closed to `{enabled, config_path}`) naming the key | edit the setting in that workflow's T2 file. For a one-off variant, copy the T2 file, edit the copy, and point the stanza's `config_path` at it — repointing is itself a T1-key override (row 3), so it can be done from the command line without editing any file |
| `--config workflows='{"<name>": {"enabled": true/false}}'` — toggling a workflow | **still valid** — `enabled` is T1-owned and inside the closed stanza | unchanged |
| `--config workflows='{"<name>": {"config_path": "<file>"}}'` — repointing a stanza at another T2 file | **valid by construction, new** — the override lands inside the closed stanza; the loader then resolves and validates the pointed file exactly as if T1 named it (§8.4, §9). This is the sanctioned ad-hoc path for workflow settings: the override *selects* a validated file rather than bypassing validation | n/a — this is the replacement |
| `--config project='{…}'` / `--config shared='{…}'` — T1-owned keys | **still valid** — merged into T1 before composition, then validated like any other T1 content (D-9.5, `SHARED_SEAM_KEYS`) | unchanged |
| `--config <new_top_level_key>=v` — e.g. the documented `--config foo=bar` | **parse-time rejection** (D-9.5: T1's top level is closed) | none — withdrawn. `plot_workflow_dag.py:50`'s usage example demonstrates this form and is updated in the docs sweep (§16.6) |

Two named surfaces need no code change and the implementer must not "fix" them:
`run_workflows.py`'s passthrough handling (`:46`, `:1061-1069`) **records**
sanitized `--config` overrides in the invocation manifest for disclosure and
never merges them itself — that recording is correct under S8 and stays,
including for a rejected invocation that never gets to run. And provenance is
unchanged in posture: an override — including a `config_path` repoint — is
excluded from the runner-side digest exactly as today ("the Snakefile snapshot
owns Snakemake's authoritative merged config"), while the composed snapshot
(D-11.1) and the T2-bytes digests (§10.5) record what actually loaded, so the
effective configuration of an overridden run is fully recorded even though T1's
on-disk `file_sha256` is not the override's witness.

The §15.2 migration error text must still **not attribute a rejected key to
the config file** unconditionally: when the offending key is not present in the
file as parsed from disk, the message says it arrived via `--config` — and,
under S8, points at this section's mapping rather than at the migration doc
alone. That is one extra read of the on-disk T1 in the error path only, and it
prevents the migration doc telling a user to fix a file that is already
correct.

## 9. Shared-seam enforcement (S4)

The rule is: *a key read by more than one workflow lives in T1, never in a T2
file*. Convention cannot enforce it — the intake's ruling 4 says so — and a full
key registry would be a second source of truth that drifts from the Snakefiles.
The mechanism is four closed checks, all at parse time, generalizing the in-repo
precedent of `_ADVANCED_SETTINGS_SCHEMA` (E2) — plus, from r2, the frozen
cross-workflow read contract and its test (D-9.6), which govern the one case
the parse-time checks cannot see.

**D-9.1 — Closed T1 workflow stanza, validated for every stanza that is
present.** `workflows.<name>` admits exactly `{enabled, config_path}` (§7.1).

The scope was undefined in v1 and the two readings give opposite outcomes
(`arch-5`): if closure were checked only for `R(entry)`, a project that split
`build_model` and left the other three inline would run WF1 clean — which is
precisely the "half-split configs become legal" defect §15.1 uses to reject the
dual-mode loader, arriving through this design's own door.

> **Rule, stated once and combined with D-8.7:** closure is validated for
> **every stanza present in T1**, whichever workflow it names. `config_path` is
> **optional for every workflow**; when present it must resolve, and an
> unresolvable one is a hard error. Absence of a whole stanza is not this
> check's business.

That last sentence is what keeps `tests/test_cli.py:110-131` green: it pops
`workflows.analyze_climate` **entirely** and asserts a WF1 dry-run still succeeds
with identical job counts — the additive-carve regression test. A popped stanza
is absent, not malformed, and `analyze_climate ∉ R(build_model)`, so nothing
fires. `run_workflows.py:282-314` remains the only place all four sections are
required, which is correct: that is a wrapper concern, and no `.smk` file reads
`enabled` at all (`grep -n enabled *.smk` returns nothing). §16.2 records the
expectation for that test explicitly, because an implementer who reads "validate
all four" without this sentence would break it.

**D-9.2 — Rejected-key set per T2 file.** `compose_config` rejects, in any T2
file, any top-level key that names a T1-owned section, a T1-owned shared key, or
a hoisted section it does not own:

```
REJECTED_IN_T2(name) = {"project", "shared", "workflows", "enabled"}
                       ∪ set(t1["shared"].keys())
                       ∪ SHARED_SEAM_KEYS
                       ∪ (⋃ HOISTED_SECTIONS.values()) − HOISTED_SECTIONS.get(name, ())
```

`SHARED_SEAM_KEYS` is the frozen set of names belonging to `shared:` whether or
not the current T1 declares them — `basin`, `historical_window`,
`clim_historical`, `seed`, `water_year_start`, `julia_threads`. It exists because
deriving from T1 alone has a hole: a T1 omitting the optional `shared.seed` would
not reject a `seed:` planted in a T2 file, which is the exact failure the rule is
written against. Adding a key to `shared:` means adding it here in the same
commit — the coupled-edit discipline `_ADVANCED_SETTINGS_SCHEMA` already imposes.

**The final term is new in v2** (`risk-4`). v1's rejection set did not contain
`reporting`, so a `reporting:` block written at the top level of
`build_model.yml` would be **accepted** and, by D-10.1's `{"enabled": ...,
**<T2 body>}` merge, land inside `config["workflows"]["build_model"]` — which is
one of the four `guarded_sections` and inside WF3's derived `CONFIG_PROJECTION`.
A caption edit in the wrong file would then silently enter
`guarded_sections_digest`, `effective_config_digest` and the wf1 snapshot the
drift guard compares against, producing a *"your model was built under different
settings"* refusal from rule 3.01 **for a change to a figure caption**. That is
precisely the outcome §10.4 says hoisting exists to prevent, reintroduced through
the unguarded direction. Deriving the rejection from the hoist map closes it
without a hand-maintained list: every hoisted name is rejected everywhere except
in its declared owner's file.

**D-9.3 — Cross-T2 multi-declaration check, over every T2 that resolves.** Any
top-level key name appearing in **two or more** T2 files is a hard error naming
the key and both files. This is the direction D-9.2 cannot see: a genuinely new
cross-workflow key, invented after this design lands, that nobody thought to add
to `SHARED_SEAM_KEYS`. Its first symptom is being written twice, and this check
turns that symptom into a parse-time failure whose message says what to do —
promote it to `shared:`.

**The scope widened in v2** (`risk-3`). v1 scoped the check to "all T2 files in
`R(entry)`", and per §8.3's own table three of the four entry points have
singleton `R(entry)` — so for WF0, WF1 and WF2 the check has exactly one file to
look at and **can never fire**. The pairs `analyze_climate`×`build_model`,
`analyze_climate`×`analyze_projections` and `build_model`×`analyze_projections`
were unreachable by any entry point, leaving a hole in decision criterion 1, the
design's central claim. The check now runs over **every T2 file declared in T1
that resolves**, not only `R(entry)`'s.

> **Tolerance clause, load-bearing:** a T2 file outside `R(entry)` that is
> **missing, unparseable, or not a mapping** is *skipped with a logged note*, not
> an error. Only files inside `R(entry)` are held to §8.4's failure table.

Without that clause a broken WF3 config would break a WF1 run, which is the
inverse of this milestone's goal — a workflow's own file must not be able to fail
another workflow's parse. The widened check reads **key names only** and merges
nothing, so §8.1's narrowing is preserved; the cost is up to three extra small
YAML parses at parse time, on the order of milliseconds.

**D-9.5 — T1's top level is closed to `{project, shared, workflows}`.** New in
v2 (`arch-6`). v1 closed the `workflows.<name>` stanzas but never T1's top level,
which broke D-15.2's completeness claim: a config whose only unmigrated element
is a top-level `reporting:` produces no extra key under any `workflows.<name>`,
so **nothing fires**, and the project runs with an undefined precedence between
two records of the same section — v1 never said whether the hoist overwrites,
merges, or refuses.

Closing the top level fixes both at once. It makes the migration detector
genuinely complete (§15.2), it makes D-9.2's `{"project","shared","workflows"}`
rejection set symmetric, and it turns the hoist-collision question into a
non-question: a leftover top-level `reporting:` is a parse error naming the key
and the migration doc, so there is no precedence rule to define. §15.3's splitter
moves the block (and §15.4 says what it does with the commented one), so a
migrated config never hits it.

**Coverage, honestly.** D-9.1 catches leaving a workflow key in T1. D-9.5 catches
leaving a non-workflow section in T1. D-9.3 catches duplicating a key across T2
files, now for every pair rather than three of six. D-9.2 catches planting a
shared or hoisted key in a T2 file. What none of them catches is a key read by
two workflows that appears in only *one* T2 file and is read across the section
boundary from there. v2 left that case "tracked in one maintained list"
(`guarded_sections`) with §19 Q2 open on whether the list should become a
checked contract — a known exception to S4, which external round 1 (`ext1-1`)
correctly refused. D-9.6 closes it.

**D-9.6 — The cross-workflow read inventory, and the frozen read contract**
*(new in r2; resolves `ext1-1`).*

**The inventory, measured rather than asserted** — every read of another
workflow's `workflows.<name>.*` in the four `.smk` files, `blueearth_cst/`, and
`scripts/`, from grep sweeps over `wflow_outvars`, `workflows.<name>`
spellings, `["workflows"]` indexing, and `.get("workflows"` chains, with every
hit read in context (this worktree, 2026-08-21). Three classes:

*Class 1 — cross-workflow VALUE reads: a setting stored in one workflow's
section, consumed by another to shape its behavior. Exactly ONE exists.*

| # | Reader | Key | Site |
|---|---|---|---|
| 1 | WF3 | `workflows.build_model.wflow_outvars` (`optional=True`, default `DEFAULT_WFLOW_OUTVARS`) | `run_stress_test.smk:537-540` — the single read site; `indicator_tables()` (`shared/indicator_tables.py:468`) and the export path (`experiment/export_wflow_results.py`) consume the **value passed on from it**, never the config |

*Class 2 — declared IDENTITY comparisons: whole sections read to be COMPARED
against the owning workflow's snapshot, never consumed as settings.*

| # | Reader | Sections | Site |
|---|---|---|---|
| 2 | WF3 drift-guard payload | `workflows.build_model`, `workflows.analyze_projections`, whole | `run_stress_test.smk:344-345`, declared at `:332-333`; compared section-scoped by `check_project_consistency.py:41-42` (`_WF1_GUARDED`, `_WF2_GUARDED`) |

These are not S4 value-sharing: the guard's entire job is to **refuse** a run
when another workflow's section changed under an already-built model, so an
edit to the WF1 T2 file is caught loudly at rule 3.01 — the opposite of the
silent coupling S4 exists to prevent. They stay declared, enumerated here, and
inside the D-9.6 test's allowlist.

*Class 3 — grep hits verified NOT cross-workflow, recorded so nobody re-derives
them:* `parse_spatial_config`'s second argument is each Snakefile's **own**
section or nothing (`analyze_climate.smk:61`, `build_model.smk:67`,
`analyze_projections.smk:294`, `run_stress_test.smk:252`; ADR 0003 §8b keeps
the shared rule's params a pure function of `project` + `shared.basin`);
`resolve_simulation_window(shared_cfg, my_cfg)` is WF1-only
(`build_model.smk:95`); `prepare_cst_parameters.py:186` and
`prepare_weagen_config.py:90` read WF3's own section from WF3 rules;
`run_workflows.py:291` reads T1 stanza level only (`enabled`, §12.1);
`suggest_experiment_name.py:284` and `plot_workflow_dag.py:116` are
single-section tool reads (§12.0, §12.3).

**The contract.** `blueearth_cst/shared/config_composition.py` declares

```python
#: Every sanctioned cross-workflow VALUE read: (reader, owner, key).
#: SHRINK-ONLY: an entry leaves this set by hoisting the key to T1 (S4);
#: nothing is ever added. A new multiply-read key goes to `shared:`.
CROSS_WORKFLOW_READS: frozenset[tuple[str, str, str]] = frozenset({
    ("run_stress_test", "build_model", "wflow_outvars"),
})
```

**The check.** `tests/test_config_composition.py` gains a static-scan case that
parses the four `.smk` files for `workflows`-section accesses naming a section
other than the file's own, and asserts the found set equals the declared one:
the Class-2 guard sites plus exactly the `CROSS_WORKFLOW_READS` value reads —
**completeness** (an undeclared cross-workflow read anywhere in the tree turns
the test red, with a message saying *promote the key to `shared:`, do not add
an entry*) and **minimality** (a declared triple with no live read is equally a
failure, so the set cannot drift stale). This is not the "drifting key
registry" §9's preamble rejects, for the same reason `shared/
cross_workflow_leaves.py`'s `LEAVES` is not one: the repo's own precedent,
`tests/test_cross_workflow_inputs.py`, keeps that cross-workflow **file** list
honest by proving it complete and minimal against the real DAG — D-9.6 is the
same shape one seam up, for config reads.

**Why the hoist is scheduled, not skipped — and not done in R13.** Hoisting
`wflow_outvars` to `shared:` is the S4-compliant end state and is committed to:
§19 Q7 schedules it **immediately after the R13 baseline re-record**, in the
same slot as Q6, and D-9.6's shrink-only rule plus the minimality check make
that removal the contract's only legal evolution. It does not land inside R13
for the `arch-11` reason that already defers D-13.4's relocations — a key
relocation shifts `effective_config_digest` for every entry point (`shared:` is
in all four projections) exactly when §16.3's falsifier must distinguish an
expected shift from a defect — **plus one this key adds**: `wflow_outvars`
would leave the guarded `workflows.build_model` section, so the guard contract
itself moves (`_WF1_GUARDED` at `check_project_consistency.py:41` must gain
`("shared", "wflow_outvars")`, and the pinned projection and derivation
literals at `test_snapshot_config_rules.py:122-141` move with it) — without
which the hoist would *weaken* the drift guard: a post-build `wflow_outvars`
edit would stop being refused at rule 3.01 and first surface mid-experiment as
`export_wflow_results`'s missing-column error (`:346`). A relocation that has
to move the guard is a series of its own, after the falsifier has done its job.

The enforcement boundary is therefore: **undeclared** cross-workflow sharing is
refused at parse time (D-9.1/9.2/9.3/9.5); the **declared** read set is a
frozen, checked, shrink-only contract (D-9.6) whose single entry carries a
scheduled hoist (Q7); and identity comparisons stay with the guard, enumerated.
Q2 is **closed** by this decision (§19).

## 10. Config identity under the split layout

The hardest part of this design, and the part D-8.1 does *not* answer on its own.
Everything that reads the in-memory `config` dict is safe by the composition
invariant. This section covers what is **not** an in-memory read of the composed
dict: a file's bytes, a DAG edge, a disk re-read, a section's key set, a
parse-time digest, and a second binding. v1 named four such places; the panel
found three more (`risk-2`/`arch-4`, `risk-9`/`arch-12`, and the §12.0 tools).

### 10.1 D-10.1 — What the merged workflow section contains

```
config["workflows"][name] = {"enabled": <T1 bool>, **<T2 body>}
```

`enabled` **is** merged back in, restoring today's section exactly.
`config_path` is **not** merged in; it is exposed only through
`workflow_config_paths`.

Both halves are load-bearing, and both are about the experiment freeze (E6.2).
`build_experiment_config` records `{"experiment_name", "run_stress_test":
dict(experiment_cfg)}` and `_frozen_differences` is a **key-union** diff
(`write_experiment_config.py:47-52,63-140`), so a key present in a recorded
`experiment.yml` and absent from the new document reads as *changed* and refuses
the experiment. Dropping `enabled` would therefore refuse **every already-run
experiment in every migrating project** — the failure mode `t2608072234`
recorded for key retirement. Adding `config_path` would do the mirror-image
damage, and would additionally make run identity depend on where a project
happens to store its files. Both lenses re-derived this independently and
confirmed it, including that `run_stress_test.smk:771` passes the whole merged
section as `experiment_cfg`.

**Corrected claim** (`arch-17`). v1 said `experiment.yml` written before and
after migration is "byte-identical for an unchanged experiment". The mechanism
supports only the weaker statement: `write_experiment_config.py:154` dumps with
`sort_keys=False`, so the bytes follow insertion order, and D-10.1 fixes
`enabled` first by construction. That happens to match all four seeds and the
template, but a project config placing `enabled` elsewhere in the block yields
different bytes after migration.

> **Restated:** `experiment.yml` is **value-identical** across migration, and
> byte-identical whenever `enabled` was the block's first key.

The consequence is nil and the reason is worth recording: `check_not_frozen`
compares parsed mappings, `_frozen_differences` is key-based, and `experiment.yml`
is a rule **output** only (`run_stress_test.smk:556,:773`, never an input), so at
worst rule 3.07 rewrites itself once. §15.5 step 4's "unaffected" leans on the
value-identity, which holds.

### 10.2 D-10.2 — The two in-memory digests are unchanged

- **`effective_config_digest`** (E6.1) digests
  `effective_config_document(config, ADVANCED_SETTINGS, CONFIG_PROJECTION)`, and
  `project_config` walks the projection paths through the merged dict. Same
  paths, same values, same canonical JSON, same SHA-256.
- **`guarded_sections_digest`** (E6.3, `run_stress_test.smk:340-352`) hashes
  `config.get("project")`, `config["shared"]["basin"]`,
  `config["workflows"]["build_model"]`,
  `config["workflows"]["analyze_projections"]` from the merged dict. Same values,
  same digest, same rerun-trigger behavior: editing WF1's settings still flips it
  and still re-runs rule 3.01, only now the edit happens in `build_model`'s T2
  file. `config_path` staying out of the merged section (D-10.1) is what keeps
  this digest experiment-invariant, which `run_stress_test.smk:329-331` requires.

Both are unchanged *by construction*, **holding `advanced_settings` fixed**. That
qualification is new and necessary (`arch-11`): `effective_config_document`
(`provenance.py:254-262`) folds the whole `advanced_settings` mapping into the
digested document **unprojected**, so any change to that file's *shape* moves
`effective_config_digest` for all four entry points. v1 scheduled exactly such a
change in §15.5 commit 6. D-13.4 removes it from R13's scope, which is what makes
the unqualified claim true again for this milestone; §16.3 states the
qualification anyway, because a property test that silently depends on an
unstated invariant is a gate you have to decide whether to believe.

No code in `provenance.py` or in the digest call sites is touched.

### 10.3 D-10.3 — T2 files become declared rule inputs

`config_path` is a declared **input** — not a param — in six rule bodies (N1).
Every T2 file loaded by an entry point is declared alongside it, in the same
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
declared input list does not churn on dict iteration order. `ancient()` over a
list is legal: `snakemake/io/__init__.py:972-982` recurses `flag()` over any
non-`not_iterable` value, so the flagged list is well-formed (verified).

**This is not tidiness.** The repo has already paid for the alternative once, at
this very rule family: `run_stress_test.smk:862-872` records that rule 3.10's
weathergen template "was a params-only read until 2026-08-05, so editing the
template changed nothing until something else forced a rerun". A T2 file left
undeclared reproduces that defect one level up: a user edits
`run_stress_test.yml`, Snakemake sees no changed input, and the experiment
re-uses stale realizations.

**The rerun-trigger rationale is corrected** (`arch-7` ≡ `risk-7`). v1 wrote that
1.06 and 3.09 "have no such params, which is why the input declaration is the
mechanism". That is true of 1.06 and **false of 3.09**, which declares
`config = ancient(config_path)` (`run_stress_test.smk:836`) and has no `params:`
block at all. An `ancient()` input is by construction not a rerun trigger — that
is the whole meaning of the flag — so `config_workflows = ancient(WF_CONFIG_PATHS)`
buys an existence edge and nothing else. The F7 analogy does not transfer: F7 was
a params-only read promoted to a **plain** declared input.

> **Per-rule truth.** For the four `snapshot_config` rules, `params.effective_config`
> already carries the composed values, so a T2 edit retriggers via params; the
> input declaration is belt-and-braces. For **1.06** the plain input **is** the
> trigger. For **3.09** the `ancient()` input is an **existence edge only**, and
> its actual rerun trigger arrives from D-10.6 — `stress_test_cfg` as a param,
> which Snakemake's params trigger does see (the same mechanism
> `run_stress_test.smk:325-327` relies on for the guard).

**D-10.3 and D-10.6 must therefore land in one commit**, which is why §15.7
commit 3 bundles them — now with the reason stated rather than implied. An
implementer who descopes D-10.6, or implements it as "hand the module the T2
path", gets exactly the F7 defect this decision is written against: a user edits
the stress-test settings, the grid values change, and 3.09 stays satisfied with a
stale `stress_test_lookup.csv`. D-10.6 is reframed accordingly: it is not only a
disk-read removal, it is what makes 3.09's rerun trigger exist at all — a rule
that today has none.

### 10.4 D-10.4 — `reporting:` lives in the WF3 T2 file, hoisted

`reporting:` is read in exactly one place — `run_stress_test.smk:530` →
`surface_axes.py:387` `config.get("reporting")` — so the seam rule does not force
it into T1. It goes into the WF3 T2 file as a top-level key of that file, and
`compose_config` **hoists** it back to `config["reporting"]` through a closed
map:

```
HOISTED_SECTIONS = {"run_stress_test": ("reporting",)}
```

Hoisting rather than nesting is what preserves D-8.1: `parse_surfaces(config)` is
untouched, and `reporting:` stays **outside** `config["workflows"]["run_stress_test"]`,
so it stays outside `CONFIG_PROJECTION`, outside the effective-config digest, and
outside the experiment freeze. That exclusion is deliberate today
(`run_stress_test.smk:526-529`: "a caption can be corrected without re-running
the experiment"), and nesting would silently revoke it — turning every caption
edit into a frozen-experiment refusal.

**Both directions are now guarded**, which v1 left open: D-9.2 rejects
`reporting:` in a non-owning T2 file (`risk-4`), and D-9.5 rejects it at T1's top
level (`arch-6`). There is consequently no hoist-collision precedence rule,
because a collision cannot be constructed.

**The factual framing is corrected** (`risk-13`, `arch-16`). v1 wrote: "Today
`reporting:`'s bytes live inside the single config file, which is a declared
input to rules 1.06 and 3.09 — so a caption edit already dirties a WF1 rule …
After the split those bytes live in the WF3 T2 file … A caption edit therefore
stops dirtying rule 1.06", and booked that as a benefit. **It describes a config
nobody has** (N9): `reporting:` exists in no shipped seed and no project config,
only as a commented template block. The mechanism is real and the conclusion
would hold for a config that used the key — but a benefit no user is currently
experiencing is not evidence for a design, so §18 no longer books it as a
positive. What survives is the placement rule and one sentence of consequence:
*if* a project declares `reporting:`, a caption edit dirties rule 3.09 and not
rule 1.06, which is correct and output-neutral either way.

Two obligations follow from `reporting:` being unused, and both are §16 rows
rather than assertions: the hoist would otherwise ship **exercised by nothing but
its own unit test**, and the splitter's `reporting:`-move branch would ship
untested. §16.2 adds a synthetic fixture declaring `reporting:` to both the
composition tests and the splitter round-trip gate.

**Not adopted:** `risk-13`'s alternative of adding `reporting:` to a shipped seed
or the template so `test_cli` covers it. A shipped seed's key set is inside
`effective_config_digest` and, for `snake_config_baseline.yml`, inside the three
baseline snapshot targets — so adding a key there would move a baseline target
for a test-coverage reason and blunt §16.3's falsifier in the same milestone that
depends on it. A synthetic fixture buys the identical coverage at no cost to the
falsifier.

**Runner-up, and the condition that flips it:** leaving `reporting:` at T1's top
level. Rejected because it keeps a WF3-only, user-facing post-processing concern
in the file every workflow reads. It becomes correct the moment a second workflow
reads `reporting:` — at which point S4 forces the move automatically and D-9.3
fires if anyone duplicates it instead.

### 10.5 D-10.5 — Both `configuration_inputs_sha256` paths, and `file_sha256(config_path)`

`source_config.{path, sha256}` in every `run_record.yml`
(`copy_config_files.py:449-452`) and the optional `source_config_sha256` field on
each journal line (`provenance.py:465,491-492`) hash **the file passed to
`--configfile`**. That is T1, and after the split T1 no longer contains the
workflow's settings — so on its own that field stops being a fingerprint of "what
this run was configured with".

**Decision: keep the field, keep its meaning, and cover the T2 bytes through the
existing referenced-inputs machinery — on BOTH paths.** v1 registered them on one
(`arch-4` major, `risk-2` major, filed independently by two lenses).

`configuration_inputs_sha256` is computed twice, by parallel construction:

| Path | Built from | Consumed by |
|---|---|---|
| **Parse-time** | each Snakefile's `CONFIG_REFERENCES` → `referenced_inputs_for_digest` → module-level `CONFIGURATION_INPUTS_DIGEST` (`build_model.smk:181-203`, `run_stress_test.smk:368-383`, and the wf0/wf2 equivalents) | rule x.01's `params:`, and **every journal line** |
| **Record-time** | `copy_config_files.__main__`'s `other_config_files` / `reference_roles` → `_snapshot_references` → `run_record.referenced_inputs` | `run_record.yml`'s `configuration_inputs_sha256` (`copy_config_files.py:457-459`) |

The two agree today because `_reference_identity` (`provenance.py:563-591`)
reduces both entry shapes to `sha256:<hash>` over the same file set. Both lenses
argued that equality from the code and both flagged that they had not run it.
**It is now observed** (N12): for the same `build_model` run, `run_record.yml`
carries `4ec140e5…` and a `journal.jsonl` line carries the identical pair; same
for `analyze_projections` at `30dfea76…`. Registering T2 bytes on one side only
would therefore make **the same run emit two values of a field with one name** —
in the very digest `_RUNS_README` points readers at for comparing runs.

The parse-time side is also the one that *matters* for retriggering.
`build_model.smk:190-192` says it outright: referenced files are "Hashed at parse
time so the digest below moves when one is edited IN PLACE — the recorded hash
alone would move without re-firing anything." Leaving T2 out reproduces exactly
the defect that comment records, for what becomes the most-edited config file in
the repo.

> **Decision, both halves in one commit:** each Snakefile's `CONFIG_REFERENCES`
> gains `("workflow_config_<name>", path)` for every entry in
> `WORKFLOW_CONFIG_PATHS`, and `copy_config_files.__main__` registers the same
> entries in `other_config_files` / `reference_roles`. **Both are derived from
> the one dict** `compose_config` returns, so they cannot diverge by
> construction, and the design states that the two reference sets must stay
> identical.

With that, each T2 file acquires — with **no schema change** — `sha256` and
`size_bytes` in `run_record.referenced_inputs`; `git_blob` when the toolbox can
give the file back (`_tracked_blob`, E3); and a contribution to
`configuration_inputs_sha256` on both paths, which is already documented as
covering "the bytes of every referenced catalog and template". The journal is
likewise not blind: `journal_event` writes `effective_config_sha256` and
`configuration_inputs_sha256` on **every** line (`provenance.py:478-492`), and
both move when a T2 file's values or bytes change.

Only the narrow, optional `source_config_sha256` narrows in meaning, and its
docstring gains one sentence saying so. `source_config.path` keeps pointing at T1
because that is the file a user re-runs with, which is the question that field
answers.

### 10.6 D-10.6 — Two disk re-reads must be redirected

Two modules bypass Snakemake's parsed `config` and re-read the source YAML from
disk. Both index `yml["workflows"]["run_stress_test"]`, which after the split is
not in the file they are handed:

| Module | Read | Reads |
|---|---|---|
| `prepare_weagen_config.py:89-91` | `read_yml(snake_config_path)` from `params.snake_config` (`run_stress_test.smk:888`) | `realizations_num`, `stress_test.{temp,precip}.transient_change` (N2) |
| `prepare_cst_parameters.py:162-165` | `open(config_fn)` from `input.config` (`run_stress_test.smk:836`) | `workflows.run_stress_test.stress_test` (N8) |

**Decision: pass the resolved section as params rather than re-plumbing a path.**
Rule 3.10 already hands `prepare_weagen_config` six explicit params — `seed`,
`water_year_start`, `dry_spell_factor`, `wet_spell_factor`, `middle_year`,
`sim_years` — several moved out of the template for exactly this reason
(`prepare_weagen_config.py:106-118`). Folding `realizations_num` and the two
transient flags in as params finishes a conversion already three-quarters done,
and the disk read disappears rather than being redirected. The same for
`prepare_cst_parameters`: it receives `stress_test_cfg` as a param and keeps
`input.config` only as the DAG edge D-10.3 requires. Per §10.3, this param is
**also 3.09's only real rerun trigger**, which is why the two decisions ship
together.

The alternative — hand each module the WF3 T2 path — was rejected because it
hard-codes the split into two leaf modules that have no business knowing about
it, and because it leaves each module re-deriving a section the Snakefile has
already composed and validated.

**The non-Snakemake branch is decided, not asserted away** (`risk-11`,
`arch-18`). v1 said only the `lookup_fn` default at
`prepare_cst_parameters.py:250-251` is taken outside Snakemake and "needs no
change". The same `else` branch (`:279`, `prep_cst_parameters(config_fn=sys.argv[1])`,
reached from `__main__` at `:289`) also runs `:162-165` and indexes
`yml["workflows"]["run_stress_test"]["stress_test"]` — a path that after the
split exists in **no single file a user could pass**. Under D-10.6 the Snakemake
branch stops passing a config path at all, so the CLI branch would be left
reading a shape nothing produces, failing with a `KeyError` on first direct
invocation after migration.

> **Decision: keep the direct-invocation branch, and give it a T1 path.** It
> calls `compose_config(safe_load(argv[1]), argv[1], entry="run_stress_test",
> declared_sections=...)` and takes `stress_test` from the composed section. The
> branch is a dev convenience with a small blast radius, but composing is a
> three-line change that keeps `python -m …` working against the same file a user
> hands Snakemake, which is the only spelling anyone would guess. Retiring it was
> the alternative; it was rejected because the module's `lookup_fn` fallback at
> `:250-251` exists to serve exactly that branch, and removing one without the
> other leaves dead code.

This is the second consumer that makes `compose_config`'s importability outside
Snakemake a requirement rather than a convenience (§12.0 is the first).

### 10.7 D-10.7 — The narrowing, `sm.config`, and why nothing else reads it

§8.1 records the narrowing: for a single-entry-point invocation,
`config["workflows"]` holds fully-populated bodies only for `R(entry)`. Nothing
is affected, and the reason is structural rather than lucky: **every reader of
another workflow's section is already declared**. WF0/WF1/WF2 read only their own
section (E1). WF3's cross-section reads are exactly `guarded_sections`, which
`R(wf3)` loads. `effective_config_digest` reads only `CONFIG_PROJECTION`.
`run_workflows.py` reads T1 alone and never composes (§12.1). A reader added
later that reaches into an unloaded section gets a `KeyError` at parse time —
loud, immediate, and gated by `test_cli` — which is the correct outcome, because
the fix is to declare the dependency in `CONFIG_PROJECTION` and thereby put it in
`R(entry)`.

**`sm.config` is the fifth access path**, and v1's claim to enumerate "the four
things that are not in-memory reads" missed it (`risk-9`, `arch-12`).
`check_project_consistency.py:225` receives `live_cfg=sm.config`, i.e.
Snakemake's `workflow.config`, not the Snakefile-local name. It is safe **because
of** D-8.6's rebinding invariant and only because of it; §16.2 checks it.

**Cyclic references are structurally impossible** and need no check: `workflows`
is in `REJECTED_IN_T2`, so a T2 file cannot reference further T2 files. There is
exactly one level of indirection by construction.

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

**The signature change, stated rather than implied.** `copy_config_files` today
takes `config=<path to the source file>` and copies it
(`tests/test_copy_config_files.py:57-60` calls it exactly that way). Writing a
composed document means the function must be **given the composed mapping**, not
only a path:

> `copy_config_files(..., config: str, composed_config: Mapping | None = None, ...)`
> — when `composed_config` is supplied, `config_out_path` is written by
> `yaml.safe_dump(composed_config, sort_keys=True)`; when it is `None` the
> existing `shutil.copyfile` behavior is retained for callers that have no
> composed document. `config` stays the **source path**, because
> `source_config.{path, sha256}` must keep hashing T1 (§10.5) and
> `run_header`/error messages must keep naming the file the user invoked.

The Snakefile passes `params.composed_config` from the same merged dict it hands
everything else. The two other destination classes `copy_config_files` handles —
catalog and template copies — are **untouched and still verbatim**, which is what
lets §16.2 carry the byte-equality assertion forward for them.

Consequences, each checkable:

- **The guard is unchanged.** `check_project_consistency.py:166-182` finds
  `project`, `shared.basin`, `workflows.build_model` in the wf1 snapshot and
  `workflows.analyze_projections` in the wf2 snapshot, because each entry point
  composes its own `R(entry)` (§8.3) and each guarded section is compared against
  the snapshot of the workflow that owns it (N6). Independently confirmed by the
  architecture lens against `_WF1_GUARDED` / `_WF2_GUARDED`
  (`check_project_consistency.py:180-181`). No code change, no path change.
- **The `ancient()` input contract is unchanged.** `run_stress_test.smk:392`
  builds the path and rule 3.01 keeps declaring it `ancient()` at `:600`, still
  pointing at `config/runs/snake_config_build_model.yml`; only its content shape
  changes, and `file_digest_or_absent` is content-agnostic
  (`run_stress_test.smk:602-606`).
- **The snapshots stop being byte-identical.** This is the point. **Four**
  snapshots are affected, three of which are baseline targets (N10) — v1 said
  "three" throughout, which is the target count, not the file count (`risk-10`).
  After this change each carries only the sections its workflow composed, so the
  WF1 snapshot no longer contains WF3's stress-test grid and vice versa.
  `_RUNS_README`'s section "Why the `snake_config_<workflow>.yml` files look
  identical" (`copy_config_files.py:76-93`) is **deleted and replaced** by a
  statement that each file is now the workflow-scoped view its name always
  promised. The README is generated by the module, so this is one string edit —
  and it must say **four**, since the bin holds four files.
- **The wf0 composed snapshot is intended.** Its `workflows` map holds only
  `analyze_climate`, and for three of the four seeds that section is
  `{enabled: true}` alone (N7, `risk-10`). A near-empty snapshot is the honest
  record of a workflow with no settings, and it is not a baseline target, so it
  moves nothing in §16.3.
- **Comments are lost.** A verbatim copy preserved the source file's comments; a
  `safe_dump` of the composed document does not. Accepted: this bin is explicitly
  "written by the run… editing any of it changes nothing", the run record is
  already `safe_dump`ed, and the source files remain the annotated artifact. This
  is the same trade `suggest_experiment_name.py` refuses for the *source* config
  (E4) and for the same reason — source versus record.

**The test that forbids this must be retired, deliberately** (`repofit-12`,
blocking). `tests/test_copy_config_files.py:51-67`
(`test_content_is_copied_verbatim`) asserts byte-equality between the snapshot
and the source, with the docstring *"A snapshot that mutates content would break
the drift guard, which compares digests of these files across workflows."*
D-11.1 falsifies that assertion by construction, and v1's §15.5 step 4 named no
test edit anywhere — so the commit that changes the snapshot's nature would go
red on both CI legs on a test encoding the opposite invariant.

The docstring's stated rationale is **wrong on the merits**, and the rebuttal has
to be made rather than left for an implementer to infer from a red assertion: the
guard compares *sections* by value (`check_project_consistency.py:150-184`), not
files by byte, and `file_digest_or_absent` is content-agnostic — it detects that
the snapshot changed, which is exactly what should happen when the configuration
changes.

> **Replacement invariant:** `yaml.safe_load(snapshot) == composed_config` — the
> snapshot round-trips to the composed mapping. The verbatim-copy assertions for
> the **catalog and template destinations** (`:64-67`) are carried forward
> unchanged, since D-11.2 does not touch them.

This test is also **the only gate in the suite that can see the snapshot's shape
without the `test_local` fixture**, which is why §16.5's ordering row matters:
retiring it without the replacement would leave the composed snapshot ungated on
every machine that has no freshly-run fixture.

### 11.2 D-11.2 — T2 files are recorded, not copied

The E3 predicate is "copy a referenced file into the project only when the
repository cannot reproduce it". A project's own T2 file lives outside the
checkout, so the predicate as written would copy it into
`<project_dir>/config/templates/`. That copy would be redundant: D-11.1 has
already archived the file's *content* inside the composed snapshot.

> T2 files are registered with role `workflow_config_<name>` and are
> **record-only**: `sha256`, `size_bytes`, and `git_blob` when tracked;
> `archived_path: null`; `recoverable: false` for an untracked project-authored
> file.

**This is a real branch in the reference machinery, not a call-site change**
(`arch-10`, `risk-12`, filed independently). v1 claimed "the registration reuses
`other_config_files` / `reference_roles` unchanged; only the destination is
`None`". That is not implementable against the code it targets:
`_snapshot_references` (`copy_config_files.py:258-306`) sorts on
`(str(dest_dir), str(config_file))` and then executes `destination_dir =
Path(dest_dir)` unconditionally in the copy branch — a `None` destination raises
`TypeError` there. The correction matters for §15.5's commit 4 and falsifies
v1's "touches nothing else" claim.

> **Specified:** a `RECORD_ONLY_ROLES = {"workflow_config"}` role prefix selects
> the record-only branch before `destination_dir` is constructed. The branch
> hashes the file, records `size_bytes`, attempts `_tracked_blob`, and appends
> the descriptor with `archived_path: null` — never touching `dest_dir`.

**And the entry shape needs one disambiguating field.** For a tracked file
`_tracked_blob` already yields record-only behavior; the new path exists solely
for the untracked project case, where the honest answer is
`recoverable: false, archived_path: null, sha256: <hash>`. That triple is a
**fourth entry shape**, and it is indistinguishable from the existing
pathless-identifier shape (`copy_config_files.py:277-287`) except by whether
`sha256` is present — so any reader treating
`recoverable=false and archived_path=null` as "logical identifier, nothing on
disk" would misread it. The descriptor therefore carries its role
(`workflow_config_<name>`) as it already does, and **`_RUNS_README` gains one
sentence** saying why this class of file is recorded but not archived: *its
content is inlined verbatim in the composed snapshot beside it.* That sentence
goes in the README, not only in this design, because the README is what a user
reading the bin actually has.

`ALWAYS_ARCHIVED_ROLES` (`output_locations`, `observations_timeseries`) keeps its
unconditional behavior; the collision guard at `copy_config_files.py:317-325` is
unaffected because a record-only entry claims no destination.

### 11.3 What `<project_dir>/config/templates/` holds

Unchanged in purpose and content: the bin for **verbatim snapshots of shipped
toolbox files the checkout cannot give back** (`copy_config_files.py:514-523`).
It receives `model_build_config` / `waterbodies_config` only when a project points
those keys at its own files, and it is normally empty (AGENTS.md, since
2026-08-13). D-11.2 keeps T2 files out of it, so the bin's meaning does not blur:
**shipped-toolbox snapshots**, never project-authored configs. No successor bin is
introduced — that would be a project-tree change, which is R9's territory.

## 12. Downstream consumers

**§12.0 is new in v2 and is the largest single correction the panel forced.** v1
inventoried the consumers that read the *composed* dict and treated the rest as
covered by D-8.1. Five tools, one conftest fixture and the test suite's dominant
config idiom do not read the composed dict at all.

### 12.0 Raw-T1 consumers — the complete inventory

A **raw-T1 consumer** is any code that `yaml.safe_load`s a `--configfile`/
`--config` target itself and indexes into it. Each is listed with its decision;
none was named in v1.

| Consumer | Reads | After the split, unfixed | Decision |
|---|---|---|---|
| `dev/scripts/snapshot_project_tree.py:69-89` (the `pixi run tree-check` gate) | `workflows.run_stress_test.experiment_name` (`:84`, fallback `"experiment"`), `workflows.analyze_projections.clim_project` (`:87`, fallback `"cmip6"`) | **fails SILENTLY** — falls back, and every project whose experiment is not literally named `experiment` gets its whole `experiments/<name>/` subtree reported as undeclared | **compose** |
| `dev/scripts/prune_series_cache.py:55-69` | `workflows.analyze_projections.{clim_project,models,scenarios,members}`, no fallbacks | `KeyError: 'clim_project'` — a `--delete`-capable maintenance tool stops working | **compose** |
| `scripts/plot_workflow_dag.py:116-121` | `workflows.run_stress_test.experiment_name` via a `.get()` chain | **fails SILENTLY** — `experiment` is `None`, the `if experiment:` branch is skipped, and every WF3 DAG render loses the experiment id from the filename AGENTS.md documents as `logs/dag/<project>_wf3_<experiment>_dag.png` | **compose** |
| `blueearth_cst/experiment/prepare_cst_parameters.py:279` (CLI branch) | `workflows.run_stress_test.stress_test` | `KeyError` on first direct invocation | **compose** (§10.6) |
| `scripts/suggest_experiment_name.py` (three reads) | `workflows.run_stress_test.experiment_name` | wrong-shape write that self-verifies green | **redirect to T2** (§12.3) |
| `tests/conftest.py:136-145` | `workflows.build_model.model_build_config` | `ValueError` at fixture setup | **compose** (§12.5) |

**Verified safe, so the inventory is closed rather than open-ended** — each reads
only `project`/`shared`: `dev/scripts/prune_climate_store.py:62,99`,
`dev/scripts/prune_config_snapshots.py:196`, `dev/scripts/region_bbox.py:105`,
`dev/scripts/scaffold_project_tree.py:82`. And
`blueearth_cst/experiment/allocate.py` reads no config at all — a grep for
`yaml|open(|config` returns one docstring line, so
`resolve_default_experiment_name` is not a raw-T1 consumer.

**D-12.0 — the tool-facing entry point.** The fix is not per-tool. Because
`compose_config` is a pure function of a parsed mapping plus a path (D-8.5), it
is importable and callable outside Snakemake, and
`blueearth_cst/shared/config_composition.py` exposes one convenience wrapper for
tools:

```python
def load_composed_config(t1_path, entry=None, declared_sections=None) -> dict:
    """Parse T1 and return the composed config. Tools pass entry=None."""
```

With `entry=None` and `declared_sections=None`, `R(entry)` is **every workflow
whose stanza declares a resolvable `config_path`** — "whatever section I index"
is the right scope for a tool that is not an entry point, and the tolerance
clause of D-9.3 applies, so a broken WF3 file does not break a `tree-check`. Each
of the four **compose** rows above becomes a two-line change: import it, call it
instead of `yaml.safe_load`.

**Why this is graded blocking by one lens and major by another, and why both rows
stand.** `risk-1` bundles the tools with a claim about the *gate*: §16 lists
`pixi run tree-check` with expected result "unchanged", so v1's validation plan
actively certifies a tool this design breaks. `arch-2` grades the same two tools
major on their own behavior. Both are correct at their own severity, and §16.5
carries the gate half.

**Conflict adjudication — does the `tree-check` gate survive?** The repo-fit lens
cleared the pixi surfaces ("`tree-check` … read no path the design moves") and
`risk-1` asserts the opposite. **Both statements are true and they answer
different questions**; the operative one is `risk-1`'s. Verified (N11):
`snapshot_project_tree.py:219` loads the config raw and `:69-89` reads the two
workflow keys with fallbacks `"experiment"` and `"cmip6"`; `pixi.toml:185` pins
the task to `test_case/snake_config_baseline.yml`; that seed's values are
`experiment_name: experiment` (`:61`) and `clim_project: cmip6` (`:40`) — **the
fallbacks exactly**. So no path moves (repo-fit is right) *and* the tool's meaning
changes while the pinned gate keeps passing (risk is right). This is the
"nothing fails, so nobody looks" class AGENTS.md records twice, arriving through
a declared gate. §16.5 changes the gate so it can fail.

### 12.1 `scripts/run_workflows.py` (E7) — no change required

`_enabled_flags` requires all four `workflows.<name>` sections to be present
mappings each carrying a bool `enabled` (`run_workflows.py:282-314`). Under D-7.1
each section is `{enabled: bool}` or `{enabled: bool, config_path: str}` — still
a mapping, still carrying a bool `enabled`, and the function does **not** reject
unknown keys, so both shapes pass unchanged (independently confirmed by the
repo-fit lens). `_project_dir` reads `project.project_dir` from T1, unchanged.
`build_command` passes the same single `--configfile` T1 path to every
invocation, unchanged. `missing_wf1_leaves` inspects the filesystem, unchanged.

The wrapper **never composes**: it reads T1 only, which is exactly right — enable
switches are a T1 concern by S1, and the wrapper's job is invocation, not
configuration. This is the clearest single piece of evidence that the enable
switches belong in T1: putting them in T2 would force the wrapper to resolve and
open four more files before it could decide what to run.

**Q4 (a `config_path` preflight) stays out of scope, and D-8.7 is why.**
`risk-15` argued the preflight is worth most exactly at migration, when every
project has four brand-new path references never resolved once. Under v1 that was
sharp: a dangling `config_path` on an enabled workflow surfaced at parse time
*during* the wrapper's fixed-order sequence, after earlier workflows had already
run. Under D-8.7 the migration no longer produces dangling paths — §15.5 step 3
says delete the **key**, and the splitter emits a path only for a section with
content — so the failure the preflight would front-load is now a typo rather than
an expected first-run state. Recorded as §19 Q4, unchanged in substance.

### 12.2 `blueearth_cst/shared/config_composition.py` and the four Snakefiles

Covered by §8. Restated here only for the consumer census: the four Snakefiles
each gain one hoist (§8.2), one compose call, `WORKFLOW_CONFIG_PATHS` in six
`input:` blocks (§10.3), and `("workflow_config_<name>", path)` entries in
`CONFIG_REFERENCES` (§10.5).

### 12.3 `scripts/suggest_experiment_name.py` (E4) — three reads, not one

The command keeps taking **T1** on the command line — that is the file a user
knows the name of, and it is the `--configfile` target. It resolves
`workflows.run_stress_test.config_path` from T1 and operates on **that** file.

**v1 specified one of the command's three config reads and understated the
second** (`arch-3`, `repofit-4`). The corrected inventory:

1. **The already-set refusal** (`suggest_experiment_name.py:283-294`) reads
   `doc["workflows"]["run_stress_test"]["experiment_name"]` from the T1 document
   loaded at the top of `main`. After the split that path is a closed two-key
   stanza, so `existing` is always `None`, **the refusal never fires**, and the
   command happily allocates and splices a second `experiment_name` over one a
   user has already pinned — minting an orphan `experiments/<id>/` and silently
   redirecting the experiment. This is a wrong-behavior path in the one command
   whose entire contract is refusing to overwrite. The read moves to the T2
   document's top-level key, resolved **before** the name is allocated, keeping
   the existing nothing-is-reserved ordering at `:296-300`.
2. **`_plan_edit`'s splice** (`:64-224`). v1 said "the plan's depth handling
   changes". The actual behavior is worse and silent: a T2 file has no
   `workflows:` key at all, so `_find(0, -1, "workflows")` (`:112`) returns
   `None` and `_plan_edit` takes the **append-whole-path-at-EOF** branch
   (`:113-128`), writing `workflows:\n  run_stress_test:\n    experiment_name:
   <name>` into the T2 file.
3. **The verifier** (`_write_experiment_name`, `:214-218`) builds its expectation
   as `expected.setdefault("workflows", {}).setdefault("run_stress_test",
   {})["experiment_name"] = name` — so the bogus nested write reloads to exactly
   `expected` and **PASSES**. The command reports success while the composed
   config has no `experiment_name` and WF3 silently falls back to the dated
   default.

> **Restated obligation:** `_plan_edit` plans a **top-level** key at column zero.
> The parent-block creation branches (`:113-128` and `:132-141`), the `_block_end`
> helper, the flow-style `ValueError` at `:93-96`, and the `after_comment`
> comment-run anchoring at `:148-163` (which keys on a comment inside the
> `run_stress_test:` block) are **retired**. The verifier's `setdefault` chain is
> **rewritten** to check the top-level key — not merely "reloads the T2 file".
> The error string at `:222` ("Set `workflows.run_stress_test.experiment_name`: …")
> and the `config` argument help at `:229` both name the nested path and change.

The text-splice approach (never `yaml.safe_dump`, so the file's comments survive)
does not change and must not. If `workflows.run_stress_test.config_path` is
absent or unreadable, the command fails with the same "nothing has been reserved"
posture it already takes.

Two test modules pin this behavior and both are named in §15.7 commit 5 and §16.2:
`tests/test_suggest_experiment_name.py` (9 `["workflows"]` references) and
**`tests/test_experiment_allocation.py:83,185-206`**, which writes and reads the
nested path through `runner.main` (N18). The second was named by **no lens**; it
surfaced only from the module inventory `risk-8` asked for, which is the concrete
argument for §16.2 existing at all.

### 12.4 `config_path` forwarding to Python scripts (E5) — contract preserved

`config_path = workflow.configfiles[0]` stays in all four Snakefiles (bound from
`t1_path`, §8.2), keeps meaning "the file passed to `--configfile`", and keeps
being forwarded as `config_snake` / `snake_config` params to
`copy_config_files.py` and `prepare_build_config.py`. `file_sha256(config_path)`
keeps hashing it (§10.5). The two modules that used the forwarded path to
**re-read settings** stop doing so (§10.6); the modules that use it as an
**identifier or an error-message subject** (`prepare_build_config.py:51`,
`run_header`) are untouched, and both are correct as-is because T1 is genuinely
the file the user invoked. `tests/test_snake_utils.py:2686-2745` pins
`run_header`'s row formatting with a T1 path string and needs **no change**
(§16.2).

The E5 two-configfile hazard — `config` reflecting a merge while `config_path`
reflects only the first file — is *avoided rather than managed* here, because
there is still exactly one `--configfile`. That is the operative argument for S2
over §17.1's alternative.

### 12.5 `simulation_window ⊂ historical_window` (E8) — now genuinely cross-file

`resolve_simulation_window(shared_cfg, model_cfg)` (`snake_utils.py:1322-1399`,
called at `build_model.smk:95`) compares
`workflows.build_model.simulation_window` against `shared.historical_window`. Its
**body, error-message shape and passthrough-when-absent behavior are unchanged**,
because by D-8.1 both mappings hold the same values they hold today.

What changes is where the two values were *authored*: the window is in WF1's T2
file, the record is in T1. This is the design's clearest demonstration that S4's
placement rule is correct rather than arbitrary — `historical_window` is read by
WF0, WF1 and WF3, so S4 puts it in T1, and D-9.2 refuses a `historical_window:`
planted in a T2 file rather than letting a project create two records that
disagree.

**v1's obligation was self-contradictory** (`arch-14`): it asserted the
"signature … unchanged" and then required that "the messages gain the resolved
file paths". The function receives two mappings and nothing else, so it cannot
name a file without a signature change.

> **Stated:** the signature becomes
> `resolve_simulation_window(shared_cfg, model_cfg, *, shared_source=None,
> model_source=None)`. Both default to `None`, so the existing message shape
> survives verbatim when they are absent — which is what keeps the change
> additive — and the Snakefile passes T1's path and the WF1 T2 path so a user
> with two files open is told which one to edit.

The message-shape tests are **two modules**, named rather than gestured at
(`repofit-13`): `tests/test_resolve_simulation_window.py` and
`tests/test_add_climate_forcing.py` (`:447-466`) — the only two in the suite that
reference `simulation_window`. Both are in §16.2 and §15.7 commit 5.

### 12.6 The test-fixture surface — the suite's dominant config idiom

**New in v2** (`repofit-1` blocking, `arch-19` major). This is the migration
item v1's effort estimate was missing entirely, and it is the largest one.

`tests/snake_config_fixture.yml` is a tracked, **inline-shaped** config — its
`build_model` section carries `model_build_config`, `waterbodies_config`,
`wflow_outvars`, `observations_timeseries` (N17) — and `tests/test_cli.py:18`
loads it as `config_fn`. Under the clean break (D-15.1) that fixture fails at
parse time on its first extra key, so **the gate §16 leans on hardest cannot run
at the commit where the loader is wired in**.

The cost is not the one file. **16 test modules reference the fixture directly**,
and the load-bearing idiom across the suite is:

```python
cfg = yaml.safe_load(FIXTURE.read_text())
cfg["workflows"][name][key] = ...          # mutate
tmp.write_text(yaml.safe_dump(cfg))        # one file
_dry_run("build_model.smk", cfg=str(tmp))  # run Snakemake against it
```

repeated in `test_cli.py:60-73`, `test_climate_store_contract.py:512,543,620`,
`test_climate_store_freshness.py`, `test_guard_invalidation.py:77,171`,
`test_cross_workflow_inputs.py`, `test_plot_climate_source.py:208-209`,
`test_compare_climate_sources.py:727`, `test_wf1_plot_outputs.py:179` and more.
Every one becomes a **two-file** mutation that must also write T2 files into
`tmp_path` and point `config_path` at them.

> **D-12.6 — one conftest helper, not 16 rewrites.**
>
> ```python
> # tests/conftest.py
> def write_config(tmp_path, cfg: Mapping, stem="snake_config") -> Path:
>     """Split a whole-config mapping into T1 + T2 files under tmp_path and
>     return the T1 path. The inverse of compose_config, for fixtures."""
> ```
>
> Every site that today does `safe_dump(cfg)` into `tmp_path` calls
> `write_config(tmp_path, cfg)` instead. The mutation idiom is **unchanged** —
> tests keep mutating one whole-config mapping — so the diff at each site stays
> small. **v2 first paired this with keeping `tests/snake_config_fixture.yml` a
> single inline-shaped file; D-12.6b below corrects that half.**

That last point needed one correction, which §16.2's inventory forced. v2
first decided the fixture "is not migrated to the split layout" — helper only,
so that no module would have to know about T2 files. That cannot hold: **7 of
the 14 remaining fixture consumers pass the fixture path straight to a Snakemake
run and never load it** (`test_build_model.py`, `test_log_rules_contract.py`,
`test_member_catalog_rule.py`, `test_prepare_spatial_maps_rule.py`,
`test_r01_config_readers.py`, `test_region_rule.py`, `test_spatial_units_rule.py`),
so under D-15.1 they fail at parse with no helper call site to change.

> **D-12.6b — the fixture IS split on disk**, into
> `tests/snake_config_fixture.yml` (T1) plus `tests/snake_config_fixture_<name>.yml`
> siblings — which is what `repofit-1`'s own fix contemplated ("and its T2
> siblings"). The 7 direct-pass modules then need **no edit at all**, and the 7
> mutating ones take two lines: `load_composed_config(CONFIG_FN)` to obtain the
> whole mapping, `write_config(tmp_path, cfg)` to write it back split.
> `write_config` keeps exactly the job D-12.6 gave it, so the mutation idiom
> every test uses is unchanged — and the fixture now exercises the production
> shape rather than a shape no run can have.

The helper's own correctness is gated by the round-trip property
`compose_config(write_config(cfg)) == cfg`, which is §16.1's cheapest new test
and the same property §15.4 requires of the splitter.

`tests/conftest.py:136-145`'s `model_build_config` fixture (N16) is the one
consumer that must **compose** rather than write: it reads
`config["workflows"]["build_model"]` from a raw load, so it calls
`load_composed_config` (D-12.0). It sits in the fixture layer AGENTS.md names as
"the one part of the suite that cannot fail in CI or in any worktree" — 15 of 31
skips measured 2026-08-07, and R9's 22 stale-path failures that every
branch-runnable gate missed. §16.5 gives it an ordering row for that reason.

## 13. Advanced settings — interior organization (S3)

`config/advanced_settings.yml` stays one toolbox-level file with three sections
split by **authority**: `constraints:` (no project config may relax),
`defaults:` (a project config may override), `runtime:` (external toolchain pins,
not overridable). None of that moves.

**D-13.1 — The placement rule, ruled now.** Namespace by workflow inside
`constraints:` and `defaults:`, one level deep, only where a setting is genuinely
workflow-scoped:

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

The split test is **who reads it**, applied identically to S4's: a setting read
by more than one workflow stays flat; a setting read by exactly one workflow goes
under that workflow's key. Today exactly one existing entry qualifies —
`batch_disk_headroom_fraction`, read only by WF3's batch sizing — and the other
four are genuinely cross-workflow (`water_year_start`'s own comment lists four
consumers across three workflows). `runtime:` is never namespaced: a toolchain
pin describes the environment, and namespacing it would invite two workflows to
pin different Julia versions, which `tests/test_julia_runtime.py` exists to
prevent.

**D-13.4 — But no existing key MOVES in R13.** New in v2, and it is the
reconciliation `arch-11` forces between §13 and §10.2/§16.3.

`effective_config_document` (`provenance.py:254-262`) folds the whole
`advanced_settings` mapping into the digested document **unprojected**. So
relocating `batch_disk_headroom_fraction` from `defaults:` to
`defaults.run_stress_test:` changes `effective_config_digest` for **all four
entry points**, including the seeds §16.3's digest-equality property test
compares. v1 asserted both digests "unchanged *by construction*" and scheduled
that move in §15.5 commit 6 — the two statements are true of the composition
change and **false of the milestone as v1 scoped it**.

One of them had to give. **The move gives; the rule survives.**

> R13 rules the placement policy (D-13.1) and applies it to **new** entries only.
> `batch_disk_headroom_fraction` stays at `defaults.batch_disk_headroom_fraction`
> for this milestone. Relocating it is a one-key follow-up whose whole cost is a
> digest shift, and it is tracked as §19 Q6.

Three reasons this is the right half to give. (a) §13's value to the owner is
*fixing the answer before the file grows*, which the rule does on its own —
moving one key today buys nothing. (b) §16.3's falsifier is the instrument that
certifies this refactor's output neutrality, and a same-milestone digest shift
would force it to distinguish "expected shift" from "defect" exactly when it must
not. (c) §13.3's own standard — "it would change what an explicit `null` does …
under a refactor that claims output neutrality" — is the same scrutiny applied
here and reaches the same verdict.

**Consequences of the deferral, recorded so the follow-up inherits them.**
`tests/test_batch_sizing.py:335` reads
`ADVANCED_SETTINGS["defaults"]["batch_disk_headroom_fraction"]` and `:343` pins
its validator's error path (`repofit-10`) — a **fourth** coupled consumer that
D-13.2's trio never named. Under D-13.4 it needs no change in R13; it is the
first thing the follow-up must edit, and D-13.2's coupled set is corrected to
name it. Likewise `repofit-10`'s second half — the `effective_config_sha256` /
`configuration_inputs_sha256` movement a user would see with no way to attribute
it — does not occur in R13 and is carried to the follow-up's own consequences
list.

**D-13.2 — The closed schema nests with the file, when the file nests.**
`_ADVANCED_SETTINGS_SCHEMA` (`snake_utils.py:869-879`) gains one nested level for
namespaced entries and keeps its closed-rejection semantics at every level: an
unknown section, an unknown workflow namespace, and an unknown key inside a
namespace are all rejected at parse time. **The coupled edit set is four, not
three**: the schema, the file, `tests/test_advanced_settings.py`, and
`tests/test_batch_sizing.py`. Under D-13.4 no such edit lands in R13; this
records the contract for the first one that does.

**D-13.3 — Both override mechanisms are preserved exactly, and neither is
unified.** E2 records two distinct paths from `defaults:` to a run — and v1's
closing paragraph introduced a **third** without specifying it (`arch-13`):

| # | Mechanism | Example | Behavior on an explicit `null` |
|---|---|---|---|
| 1 | Call-site default | `julia_threads` at `build_model.smk:102` | `julia_threads: null` **raises** at parse (`_positive_int(None)`) |
| 2 | Resolver substitution on `None` | `seed` (`snake_utils.py:1134-1151`), `water_year_start` (`:1167-1171`) | `seed: null` **falls back** to the default |
| 3 | **T2 optional key** (S5's `batch_size` shape) | `get_config(my_cfg, "batch_size", default=ADVANCED_SETTINGS[...])` in the owning Snakefile | `batch_size: null` is returned **as `None`** by `get_config`'s present-key rule, so the call site must handle it — i.e. it behaves like mechanism 1 |

Mechanism 3 is **mechanism 1 with the default sourced from advanced settings**,
which is why it needs no new machinery: `get_config` returns a present key as-is
including `None` (E1), and the call site validates. It reads from the workflow's
own T2 file and is a single-reader key, so D-9.2 does not reject it and D-9.3
cannot see it in two files. Unifying mechanisms 1 and 2 remains out of scope: it
would change what an explicit `null` does for at least one key, under a refactor
that claims output neutrality.

The override *keys* stay in `shared:` per S5 (`shared.seed`,
`shared.water_year_start`, `shared.julia_threads`) — they are read by more than
one workflow, so S4 places them in T1 independently of S5, and the two rulings
agree.

## 14. Workflow naming reconsideration (scope amendment S6)

The design **recommends**; the owner ruled Candidate A provisionally at G1 and
rules finally at G2. The panel found **no defect in the recommendation's
reasoning**, so this section is compressed relative to v1 (the candidate
arguments are settled; the surface inventory is what a G2 ruling actually needs).

### 14.1 What exists today

Two independent schemes, deliberately kept independent: **workflow names**
(`analyze_climate`, `build_model`, `analyze_projections`, `run_stress_test` —
verb-first, set 2026-08-14 with recorded rationale in
`docs/migration-workflow-names.md`, because the old names were nouns and two were
vague about what the workflow does), and **`wfN` ids** (`wf0`..`wf3`, used in
log/benchmark/DAG filenames and as the `W` digit of the `W.NN` rule scheme).
`dev/reference/naming.md` §9 is explicit that `W` is a workflow **id**, not a
position, which is why `wf0` was added as `0` rather than renumbering.

### 14.2 Candidates, and the recommendation

| Candidate | Shape | Verdict |
|---|---|---|
| **A — keep current names** | no change to any surface | **Recommended** |
| **B — module nouns** | `climate`, `model`, `projections`, `experiment` | Rejected now: reverts a six-day-old ruling by restoring precisely the noun forms it removed for vagueness, and makes `workflows.experiment.stress_test` read worse than the `workflows.run_stress_test.stress_test` the migration doc already ruled correct. *Would be preferable if* the toolbox became a registry of discovered modules, where the verb is redundant because "run the `model` module" is the invocation. |
| **C — id-prefixed names** | `wf0_analyze_climate` … | Rejected now: naming.md §9 keeps `W` an id precisely so it is free of position, and folding it into the config key freezes it into every project's config — inserting or renumbering a workflow would become a config-breaking change rather than a filename change. It buys sortable logs `logs/wf1_build_model.log` already provides. *Would be preferable if* the id and the name could disagree. |

**Three reasons for A, in order of weight.**

1. **No naming defect surfaced.** This design read every consumer of the workflow
   names — the four Snakefiles, `run_workflows.py`, `copy_config_files.py`,
   `check_project_consistency.py`, `provenance.py`, the snapshot paths, the
   baseline manifest — and none is confusing because of a name. The one oddity
   anyone reports (`workflows.run_stress_test.stress_test`) is explicitly ruled
   correct in the standing migration document. A rename with no defect behind it
   is churn.
2. **The coupling argument runs the wrong way.** "One break, not two" is a reason
   to *bundle* a rename that is independently justified — not a reason to rename.
   And §14.3 shows the rename touches a substantially **larger** surface than the
   config split, including four surfaces the split does not touch at all.
3. **The 2026-08-14 precedent argues against.** That rename rode along with
   *adding a fourth workflow*, which already forced edits to `WORKFLOW_ORDER`,
   `test_cli.py`, the DAG digit map, the symmetry tests, `check_baseline` and the
   template — "every file the rename touches". The config split forces edits to
   none of those five. The rider that justified the first rename does not exist
   for a second one.

**Name-scheme independence.** Whichever candidate wins, this design's T2 filename
scheme is unchanged in *form*: both families derive from the `workflows.<name>`
key by one transform (D-7.4). Nothing else in §§7–13 depends on the names — the
loader takes `R(entry)` from `declared_sections` (D-8.5), never from a hard-coded
list, and `SHARED_SEAM_KEYS` names `shared:` keys. **One qualification the panel
added and v1 could not have claimed**: that independence was an *intention* in v1
because `arch-1` showed there was no derivation channel; D-8.5 makes it a
mechanism.

### 14.3 Surface inventory for a rename (if the owner rules B or C)

| # | Surface | Notes |
|---|---|---|
| 1 | Four `*.smk` filenames | `-s` targets; `tests/test_cli.py` enumerates them |
| 2 | `workflows.<name>` T1 keys | breaking for every project config |
| 3 | **T2 filenames + `config_path` values** | introduced by this design; one transform (D-7.4) |
| 4 | `config/templates/snake_config.<name>.template.yml` | introduced by this design |
| 5 | `run_workflows.py`: `WORKFLOW_ORDER`, `SNAKEFILE`, `PER_WORKFLOW_FLAGS`, `LEAF_PRODUCER` | plus its error strings |
| 6 | `plot_workflow_dag.py` digit map; `logs/dag/<project>_wf<N>_dag.png` | |
| 7 | `logs/wfN_<name>.log`, `benchmarks/wfN_benchmarks_<exp>.md` | project-tree paths |
| 8 | `config/runs/snake_config_<name>.yml`, `config/runs/<name>/run_record.yml` | **the two that bite**: baseline-fingerprinted (N5) *and* `snake_config_build_model.yml` is a mandatory declared `ancient()` input of WF3's guard |
| 9 | `experiments/<exp>/config/snake_config_run_stress_test.yml` | same, experiment-scoped |
| 10 | `CONFIG_PROJECTION` / `guarded_sections` string literals; `check_project_consistency` guarded paths | run identity: a changed projection path string changes `effective_config_digest`. **Also pinned verbatim by `tests/test_snapshot_config_rules.py:122-126`** |
| 11 | `journal.jsonl` `workflow` field | old lines keep the old spelling — correct, per the 2026-08-14 precedent |
| 12 | `cross_workflow_leaves.py` / `cross_workflow_inputs.py` `LEAF_PRODUCER` | |
| 13 | pixi tasks `dag-wf*`, `run-workflows` | |
| 14 | Tests: `test_cli.py`, `test_run_workflows.py`, symmetry tests, `semantic_tree_diff` inventory, **plus every module in §16.2** | |
| 15 | `dev/baseline/manifest.json` target keys | **forces a baseline re-record for path reasons alone**, which destroys §16.3's falsifier |
| 16 | Docs: `README.md`, `AGENTS.md`, `docs/`, `naming.md` §9, `dev/reference/workflows/rule-index.md`, a successor to `docs/migration-workflow-names.md` | |

Row 15 is the decisive practical objection to bundling: §16.3's acceptance
criterion is "exactly three baseline targets move, all of them config snapshots".
A rename moves a dozen target **keys**, so the baseline can no longer distinguish
"the refactor was output-neutral" from "the refactor changed a number". **If the
owner rules for a rename, it must land as a separate commit series *after* the
config split has been baseline-verified** — which is the opposite of the
one-migration coupling argument, and should be said plainly at the gate.

## 15. Migration plan

Precedent and successor: `docs/migration-workflow-names.md` (2026-08-14). **Two**
documents are required, not one (`repofit-8`):

- `docs/migration-config-tiers.md` — the user-facing guide (naming.md marks this
  **Optional**, and it is written anyway because a clean break needs it).
- `dev/milestones/r13/migration_config-tiers.md` — the **internal rename record**,
  which `dev/reference/naming.md:205-266` marks **Required** for every rename in
  its list. Two entries fire here: "Checked-in example config keys (user-facing)"
  (`:223`) and "Test fixture paths read by `tests/conftest.py`,
  `dev/scripts/check_baseline.py`, or other scripts" (`:225-226`). It carries the
  old→new key-path table, the machinery to update, and the gate evidence. Note
  that naming.md's mandated `migration_<topic>.md` form **overrides** the repo's
  kebab-case filename rule (`:264-266`), so the underscore is correct.

v1 planned only the optional half, which would have left the R13 seal incomplete.

### 15.1 D-15.1 — Clean break, not backward compatibility

**Decided (G1, unchanged):** a config carrying settings inline under
`workflows.<name>` fails at parse time. There is no dual-mode loader and no
deprecation window.

The argument is the one the repo already made, six days ago, for the same class
of change: *"If you have a project config, it will fail at parse time until you
rename its three `workflows:` subsections. That is deliberate: the alternative —
renaming the files while freezing the keys — leaves a config surface that
disagrees with the thing it configures."* Here a dual-mode loader would cost
three specific things:

- **D-9.1 could not hold.** Seam enforcement in the T1→T2 direction *is* the
  closure of the `workflows.<name>` stanza. A loader that also accepts inline
  settings has no closed stanza to check, so S4 falls back to convention — which
  ruling 4 explicitly rejects.
- **Half-split configs become legal**, and a project could carry `wflow_outvars`
  in T1 and `simulation_window` in a T2 file with nothing objecting. (Note this
  is also the defect `arch-5` showed v1 admitting through its own door by leaving
  the closure's scope undefined; D-9.1 now closes it.)
- **The migration detector disappears.** Under a clean break, an unmigrated
  config produces a precise, actionable error (§15.2). Under dual mode it
  produces a silently-working run and an unmigrated project nobody notices — the
  same "nothing fails, so nobody looks" failure the vendored-console marker and
  the CI-unread incident both record.

The population this breaks is small and known: the shipped seed configs,
**`tests/snake_config_fixture.yml` and the 16 modules that consume it** (§12.6 —
v1 omitted this and it is the largest item), the owner's own projects, and the
CST-API backend, which constructs configs programmatically, is versioned
independently, and which standing policy says must never constrain a decision
here.

### 15.2 D-15.2 — The migration detector is the closed stanza plus the closed top level

Because `workflows.<name>` admits exactly `{enabled, config_path}` (D-9.1) **and
T1's top level admits exactly `{project, shared, workflows}` (D-9.5)**, an
unmigrated config fails on its **first** unexpected key with a message naming:
the offending key, the workflow it belongs to (where applicable), the T2 filename
convention, the migration command (§15.3), and `docs/migration-config-tiers.md`.
No separate detector, no version key, no schema-version negotiation.

The second clause is new and is what makes the claim true (`arch-6`): under v1
only the stanzas were closed, so a config whose sole unmigrated element was a
top-level `reporting:` produced **no** extra key under any `workflows.<name>` and
nothing fired.

The message attributes the key correctly rather than blaming the file
unconditionally: when the offending key is absent from T1 as parsed from disk, it
arrived via `--config` and the message says so (§8.5b).

It fires at Snakefile parse time, before the DAG, so `--dry-run` reports it and
`pytest tests/test_cli.py` gates it.

### 15.3 D-15.3 — `scripts/split_project_config.py`, report-only with staged output **(reworked in r2; owner ruling)**

A user-facing runner, so `scripts/` and not `dev/scripts/`. **The precedent is
`scripts/suggest_experiment_name.py`** — a user-facing, one-shot config editor
that is likewise not part of a run — not "what a user runs to drive the
pipeline", which a migration tool does not do (`repofit-14`-class correction
raised in the repo-fit appendix). AGENTS.md's O-23 rule splits by invocation
model, and a one-shot user-run config editor is the class `scripts/` already
holds.

**The v2 `--write` mode is withdrawn.** External round 1 (`ext1-2`) found it
contradicted the settled G1 posture — a report-only migration script — and the
owner ruled the interpretation at a gate-clarification (2026-08-20):
**STAGING-EMIT**. The script is strictly report-only *against user files*: it
emits the proposed T1 and T2 file contents into a staging directory alongside a
migration report, and application is an explicit user step outside the script.
There is no `--write`, no in-place mutation, no opt-in mutation mode.

```
python scripts/split_project_config.py <config.yml>                  # report + staged proposal
python scripts/split_project_config.py <config.yml> --staging <dir>  # override the staging dir
```

**The staging directory.** Default `<t1_dir>/config-split-staged/`, beside the
source file, so the proposal is inspectable next to what it replaces — for an
out-of-tree project that is the project's own folder, for a shipped seed it is a
subdirectory of `test_case/`, which the E9 tracking glob
(`!test_case/snake_config_*.yml`) does not reach, so staged files are never
accidentally tracked. The script **owns the staging directory wholesale**: it
deletes and recreates it on every run (it is the tool's namespace, never user
files), refuses to write anywhere outside it, and never reads staged content
back as input. Inside it land exactly three things:

- the proposed **T1**, under the source file's own filename;
- the proposed **T2 siblings**, under their production names
  (`<t1_stem>_<name>.yml`, D-7.4) — so application is a move, not a rename;
- `migration-report.md` — per-section disposition (split to which file; empty
  after dropping `enabled:` → no file and no `config_path` key, D-8.7), the
  `reporting:` move, any commented `#reporting:` found (reported, not moved —
  §15.4), any D-15.4a refusal with construct and line, the D-15.4b round-trip
  verdict against the staged pair, and the application step with its
  post-application check.

**It splits the file as TEXT, not through `yaml.safe_dump`** — E4's argument
applies unchanged and with more at stake: the shipped template carries ~110
comments, a real project's config carries the ones its author wrote, and this is
the first command a user runs against their file. The mechanical transform:
locate the `workflows:` block; for each `<name>:` subsection, take its body
including the comment lines preceding each key, dedent by four spaces, drop
`enabled:`, and write it to the staging directory as `<t1_stem>_<name>.yml`;
replace the subsection with the two-key stanza in the staged T1; move a
top-level `reporting:` block into the staged `run_stress_test` T2 file. **A
section whose body is empty after dropping `enabled:` produces no file and no
`config_path` key** (D-8.7).

**The `config_path` it emits.** The **bare relative filename**
(`snake_config_rapid_build_model.yml`), under §8.4's T1-anchored resolution —
correct whether T1 sits under the repo root or in an out-of-tree project folder
(the case `repofit-2` showed v1 could not express), and correct **inside the
staging directory itself**: the staged T1 and its siblings compose in place,
which is what lets D-15.4b verify the staged pair before anything is applied. It
also produces the shipped seed naming for free, landing inside the E9 tracking
glob with no `.gitignore` change once applied (D-7.4).

**The application step, stated as the user's.** Review the report and the staged
files; then move the T2 files beside the source config and replace the source
config with the staged T1 — an ordinary file operation the user performs and can
diff, not a script mode. The post-application check is a parse: any dry-run of
an enabled workflow (or `scripts/run_workflows.py --dry-run`) runs every
composition and seam check in §§8–9, so a mis-applied proposal fails loudly
before anything executes.

### 15.4 D-15.4 — What the splitter refuses, and what it verifies

**New in v2** (`risk-6`, `arch-16`). v1 booked the splitter's risk as "mangles a
comment block", severity medium, and gated it on five files the implementer
controls. Mangling a comment is cosmetic; **mangling a value is not** — and a
value changed by a dedent or a broken alias produces a config that parses and
runs, so for WF1/WF2 it silently produces different numbers under an
unchanged-looking config, and only WF3 fails loudly via the freeze. G3's
output-neutrality claim is what is at stake.

Two unexamined corruption paths:

- **YAML anchors, aliases and merge keys.** An anchor defined in `shared:` or in
  one workflow section and aliased inside another becomes an **undefined alias**
  once the sections are written to separate files — `yaml.safe_load` then raises
  `ComposerError` on the T2 file, which is the loud case. A `<<:` merge that
  resolves differently after the split changes **values silently**, which is not.
- **Block scalars.** A `|` or `>` scalar inside a workflow section is a silent
  corruption path all its own: dedent-by-four strips four spaces from the
  scalar's **content**, changing the string value with no structural symptom.

> **D-15.4a — Refuse, naming the construct.** If the source document contains
> `&`, `*` or `<<:` anywhere, or a block scalar inside a `workflows.<name>`
> subsection, the splitter **refuses to write** and reports which construct at
> which line. This is a short check and it converts an unbounded class of silent
> corruption into a stated non-support with a manual path.
>
> **D-15.4b — Verify the staged pair against the source, before reporting it
> applicable.** Every run composes the **staged** T1 (whose emitted
> `config_path` values resolve inside the staging directory, §15.3) and asserts
> the round trip `compose_config(staged_t1) == yaml.safe_load(source)`. On
> mismatch the report says **do not apply**, names the first differing path, and
> the script exits nonzero — the staged files are kept for diagnosis, marked by
> the report's verdict. The user's file is never touched either way.

v1's acceptance gate — the same round trip "for each shipped seed and for the
template" — covers five files the implementer controls, **none of which contains
an anchor or a block scalar**, while the user's own config got no verification
at all. Under staging-emit the exposure shrinks by construction — the worst
outcome is a staged proposal the report refuses, never a rewritten user file —
and D-15.4b closes the remaining gap: no proposal is reported applicable without
its round trip. The shipped-file gate stays as a permanent regression test
(§16.2).

**The gate set gains a synthetic fixture carrying `reporting:`** (`risk-13`,
`arch-16`), because no shipped seed or template declares it (N9), so without one
the splitter's reporting-move branch and the loader's hoist both ship exercised
by nothing. **And the splitter must handle the commented block**: the template's
`#reporting:` at `config/templates/snake_config.template.yml:210` will not match
a `reporting:` block matcher, so it would be stranded in T1 pointing users at a
placement the loader no longer honours — and, under D-9.5, at a placement that
now fails at parse if uncommented. **Decision:** the template's commented block
is **rewritten by hand into the WF3 T2 template** as part of the derived-artifact
regeneration, and the splitter **reports** (does not move) any commented
`#reporting:` it finds in a user's file, naming the T2 file it belongs in. A text
splitter that relocated comments it could not parse would be guessing.

If comment-preserving text splitting proves disproportionately expensive, the
fallback is a `safe_dump` split plus a printed warning that comments were dropped
and a pointer to the original file — the round-trip gate is unaffected either way.

### 15.5 Mechanical steps for an existing project

1. `python scripts/split_project_config.py <your-config.yml>` — read
   `migration-report.md` and inspect the staged proposal in
   `config-split-staged/` (§15.3). The report's D-15.4b verdict must say the
   round trip is clean before anything is applied.
2. **Apply the proposal — a user step, not a script mode**: move the staged T2
   files beside the config and replace the config with the staged T1. T1
   shrinks to `project:` + `shared:` + four short stanzas. A dry-run of any
   enabled workflow is the post-application check (§15.3).
3. For a workflow this project never runs and whose settings it does not need:
   **delete the T2 file *and* its `config_path` key**, leaving `enabled: false`
   alone in the stanza. Do **not** leave a `config_path` pointing at a path that
   does not exist — that is a hard parse error, deliberately (D-8.7). This is a
   correction of v1, which advised the dangling form.
   There is **no WF3 carve-out any more**: under D-8.7 a WF3 run does not require
   `build_model` and `analyze_projections` T2 *files*, only their stanzas — so the
   projections overlay stays optional exactly as the CST method requires (N14).
4. Re-run. Nothing under `project_dir` needs hand-migration:
   - the four config snapshots are **regenerated** with composed content on the
     next run of each workflow (D-11.1) — no path moves, so no `ls`-and-rename
     table like the 2026-08-14 migration needed;
   - `experiments/<exp>/config/experiment.yml` is **unaffected**: D-10.1 keeps
     the recorded section value-identical, so a completed experiment stays
     unfrozen-safe and does not need re-creating;
   - `config/runs/journal.jsonl` keeps its history; new lines carry the same
     `effective_config_sha256` an unmigrated run would have produced.
5. If WF3 has already run and the guard is armed, the first post-migration WF3
   run re-fires rule 3.01 and **passes**: a pre-migration wf1 snapshot is the
   whole config, hence a strict superset of what the guard reads, and once WF1
   re-runs the composed snapshot still carries `project`, `shared` and
   `workflows.build_model`.

### 15.6 D-15.5 — The first post-migration run re-computes the project **(owner-visible)**

**New in v2** (`risk-16`). §15.5 step 4 says "nothing under `project_dir` needs
hand-migration", which is true — and reads as "nothing re-runs", which is false.
v1 booked this cost nowhere, and it is a real charge against G5's "mechanical,
**bounded** migration".

**The cascade, link by link, each cited:**

1. Migration rewrites **T1's bytes**, and T1 is a **non-`ancient`** declared input
   of `prepare_spatial_maps` (`build_model.smk:535`). So the first post-migration
   WF1 run re-executes rule 1.06 and everything downstream of it.
2. WF1 rewrites `config/runs/snake_config_build_model.yml` with composed content,
   so `wf1_snapshot_digest = file_digest_or_absent(...)`
   (`run_stress_test.smk:392-394`) moves.
3. Rule 3.01 re-fires — §15.5 step 5 says so and treats it as benign because it
   *passes*. Passing is not the same as being free.
4. 3.01 rewrites `.project_consistency_ok`, which rules 3.09 and 3.10 declare
   **bare, not `ancient()`** (`run_stress_test.smk:837, 858`;
   `check_project_consistency.py:195-199` names the two consumer classes
   explicitly — "the four per-experiment roots (fresh sentinel)" versus the
   `ancient()` one).
5. 3.10 feeds 3.11, and the realization and stress-test cascade runs.

> **Consequence, stated plainly:** driven through `scripts/run_workflows.py` —
> the documented way to run the pipeline — **migrating a project with a completed
> experiment re-runs the entire stress test to produce identical results.** For a
> baseline-scale project that is the full WF1 build plus `RLZ_NUM × ST_NUM` Wflow
> runs.

This goes in §18's Negative list and in `docs/migration-config-tiers.md`, in the
user's own words, because a user who is not told will assume the pipeline is
broken.

**Is a shortcut acceptable?** The splitter's D-15.4b round trip **proves per
project** that the composed values are unchanged — precisely the condition
under which the re-run is pure waste. v2 answered with a bare, documented
`snakemake --touch`. External round 1 (`ext1-4`) faulted that answer, and the
fault is real: `--touch` changes **timestamps, not contents**, so a completed
experiment could keep whole-shape monolithic snapshots and stale configuration
records while Snakemake treats every product as current — a retained run record
claiming configuration inputs that no longer correspond to the on-disk T1/T2
set, and a §16.4 `semantic_tree_diff` reading `compare_copied_config` failures
indefinitely. The bare shortcut is **withdrawn** (§17.4).

> **Decision (r2): a bounded, records-first refresh sequence — documented,
> explicitly opt-in, never invoked by any tool.** Stated in
> `docs/migration-config-tiers.md` as four steps:
>
> 1. **Precondition, unchanged from v2:** the splitter's report shows a clean
>    D-15.4b round trip **and** no other config edit was made in the same pass.
>    The second half is a judgement about what else the user changed, which no
>    tool can verify — which is why no tool ever runs this sequence.
> 2. **Regenerate every configuration record BEFORE any timestamp moves.** For
>    each previously-run workflow, build its config-snapshot target alone —
>    rule 1.01-class rules read only source files and the in-memory config
>    (`build_model.smk:465-489`: T1, T3, gauge/observation sources; no
>    computed upstream), so each is a seconds-scale single-rule run. That
>    regenerates, with composed content, every snapshot this design says
>    changes shape: all **four** `config/runs/` snapshots where their workflow
>    has run (N10 — wf0's included), and for a project with a completed
>    experiment the experiment-scoped snapshot, whose target pulls rule 3.01
>    first (`run_stress_test.smk:617-635` declares the sentinel as input) — so
>    the drift guard **executes its real comparison** against the fresh wf1
>    snapshot rather than being touched past.
> 3. **Only then** `snakemake all --touch` per workflow, in wf order: every
>    configuration record is now genuinely current, so the touch reaches only
>    downstream computational products. A `temp()` intermediate already reaped
>    is not resurrected and stays absent; nothing consumes it (that is what
>    `temp()` meant).
> 4. **The machine-checked equivalence proof:** a final `--dry-run` per
>    workflow must schedule **nothing**. Together with step 1's round trip
>    (composed-post-split ≡ parsed-pre-split, per project) this is the pre/post
>    effective-configuration equivalence made checkable. Any scheduled job
>    means the precondition did not hold — the answer is the default full
>    re-run, never a second touch.

**What survives of `risk-16`'s resolution, and why the objection does not reach
it.** The cascade trace above, the plainly-stated cost, the §18 booking, the
opt-in stance and the no-tool-invokes-it rule all stand — `ext1-4` faulted none
of them. The faulted element was the *shortcut's ordering*: products marked
current while configuration records stayed stale. Step 2 removes that by
construction (every record this design names as changing shape is regenerated
before any touch), step 4 replaces "believed equivalent" with
"scheduled-empty, checked", and the guard is exercised rather than bypassed.

**Coherence with the baseline:** the maintainer's baseline project never takes
this sequence — §16.3's falsifier is evidence only because its data targets are
**recomputed** (§16.5(b)'s five-clause ordering stands, and the three-target
re-record happens after a real run, not a touch).

**Tested, not just documented:** `tests/test_migration_touch_refresh.py`
(§16.2, `workflow_contract` tier, `test-full` only) runs the sequence against a
migrated rapid-scale completed project and asserts: every snapshot carries
composed content, rule 3.01 really ran and passed, the final dry-run schedules
nothing, and the data targets are byte-identical to their pre-migration copies.

The conservative path — just re-run — stays the default and the recommendation
for any project whose numbers matter.

### 15.7 Commit sequencing

Each step independently runnable, per the design-document rule that a move must
never leave the tree un-runnable between commits. **Every test module each commit
necessarily edits is named**, which v1 did for none of them — the gap `arch-20`,
`repofit-1`, `repofit-6` and `repofit-12` each found from a different direction.

| # | Lands | Test modules edited in the same commit |
|---|---|---|
| 1 | `blueearth_cst/shared/config_composition.py`: `compose_config`, `load_composed_config`, the four seam checks, `SHARED_SEAM_KEYS`, `HOISTED_SECTIONS`, **`CROSS_WORKFLOW_READS` + the D-9.6 static scan**, path resolution, error surface. Not yet called by any Snakefile — **no behavior change** | **new** `tests/test_config_composition.py` |
| 2 | `scripts/split_project_config.py` (staging-emit, §15.3) + refusals (D-15.4a) + staged-pair round trip (D-15.4b) | **new** `tests/test_split_project_config.py`; **new** synthetic `reporting:` fixture |
| 3 | Migrate the four shipped seeds + the template + **`tests/snake_config_fixture.yml`'s consumers**; hoist the projection literals and wire `compose_config` into the four Snakefiles; add the T2 rule inputs (D-10.3); add `CONFIG_REFERENCES` entries (D-10.5); redirect the two disk re-reads (D-10.6). **One commit** — the loader, the configs it requires, and 3.09's only rerun trigger cannot land apart | `tests/conftest.py` (**`write_config` helper** + `model_build_config` fixture), `tests/test_cli.py`, `tests/test_snapshot_config_rules.py`, `tests/test_prepare_cst_parameters.py`, `tests/test_a1_acceptance.py`, `tests/test_gridded_outputs_removed.py`, `tests/test_prepare_weagen_config.py`, `tests/test_semantic_tree_diff.py`, the fixture's own T2 siblings, and the **7 mutating** fixture-consumer modules via the helper — the other 7 pass the path straight to a run and need no edit (§16.2 tier 2, D-12.6b) |
| 4 | Composed snapshot (D-11.1, incl. the `copy_config_files` signature) + record-only T2 registration (D-11.2) + `_RUNS_README` text | `tests/test_copy_config_files.py` (**retire `test_content_is_copied_verbatim`, add the round-trip invariant**), `tests/test_snapshot_project_tree.py`, `tests/test_interchange_contracts.py` (verify-only) |
| 5 | `suggest_experiment_name.py` (§12.3) + `resolve_simulation_window`'s optional source args (§12.5) + the four raw-T1 tool fixes (§12.0) | `tests/test_suggest_experiment_name.py`, **`tests/test_experiment_allocation.py`**, `tests/test_resolve_simulation_window.py`, `tests/test_add_climate_forcing.py`, `tests/test_plot_workflow_dag.py` |
| 6 | *(v1 had advanced-settings namespacing here. **Removed** by D-13.4 — no key moves in R13.)* | — |
| 7 | Docs sweep + `docs/migration-config-tiers.md` (incl. §15.6's records-first refresh sequence) + `dev/milestones/r13/migration_config-tiers.md`; CI expected-skip baseline note; **baseline re-record last**, after §16.3's falsifier has been read | **new** `tests/test_migration_touch_refresh.py` (`workflow_contract` tier; needs the full stack, so it lands with the migration doc it tests) |

One CI note belongs to whichever commit lands first: the documented
expected-skip/pass baseline (499/31/1 windows, 498/32/1 ubuntu) **shifts**, and
the pass/skip counts must be re-read with `-rs` rather than predicted here
(§16.5).

## 16. Validation plan

**This section is the largest single addition in v2.** Eight findings converge on
one obligation — `repofit-1`, `repofit-3`, `repofit-6`, `repofit-7`,
`repofit-12`, `arch-19`, `arch-20`, `arch-21` and `risk-8` — and the obligation
is not "add gates". It is: **name every test module the split touches and give
each one an expected result**, so that no gate in the table is one an operator
has to decide whether to believe. `risk-8` states the reason precisely: a grep
sweep cannot see a module that *constructs* the pre-split shape as a Python dict
literal, and nine modules do exactly that, so the tool changes meaning, its test
keeps building the old shape, and the suite stays green.

§16.1 is the gate table. §16.2 is the module inventory. §16.3 is the falsifier.
§16.4 gives the sibling gate its prediction. §16.5 is what must change and in
what order. §16.6 is the sweep that survives — narrowed to what a sweep is
actually good for.

### 16.1 The gate table

Mapped to the gates the intake verified runnable in this worktree. Every row
carries a falsifiable expected result.

| Gate | What it checks here | Expected result |
|---|---|---|
| `pytest tests/test_cli.py` | the parse gate: dry-runs all four entry points against the migrated seeds. Every composition error, every seam refusal (D-9.1/9.2/9.3/9.5), the D-8.7 optional matrix and the §15.2 migration error fire here | green; four DAGs resolve. **Prerequisite:** §16.2 tier 2 — the gate cannot run until `tests/snake_config_fixture.yml` is a valid T1 (`repofit-1`) |
| **new** `tests/test_config_composition.py` | `compose_config` unit surface: the `R(entry)` matrix (§8.3); path resolution (relative / absolute / `~` / missing / non-mapping / empty / **out-of-tree T1** / **cross-drive**); every §8.4 error; the duplicate-`config_path` refusal under `normcase(abspath(...))`; D-9.1/9.2/9.3/9.5; **the D-9.6 static scan** — the cross-workflow read set found in the four `.smk` files equals the declared contract (completeness + minimality); `enabled` merged and `config_path` **not** merged (D-10.1); the `reporting:` hoist (D-10.4); the D-8.7 omitted-key case; **the composed shape visible through `workflow.config`** (D-8.6a) | new tests, green |
| **new** `tests/test_split_project_config.py` | the splitter: D-15.4a refusals (`&`, `*`, `<<:`, block scalar in a workflow section) naming the construct and line; D-15.4b round trip of the **staged pair** against the source; the commented-`#reporting:` report-not-move branch; the empty-section no-file case; the staging-dir contract (owned, recreated, nothing written outside it); and the **source-untouched invariant** — the source file's bytes are asserted unchanged after every run, refusal paths included (§15.3, owner ruling) | new tests, green |
| **new** digest-equality property test | for each shipped seed: `effective_config_digest` and `guarded_sections_digest` computed from the pre-split config equal those computed from the composed post-split config. D-8.1 in executable form; permanent | equal. Holds `advanced_settings` fixed — see §16.3 |
| **new** freeze property test | an `experiment.yml` recorded pre-split plus a post-split composed config → `check_not_frozen` passes. Direct test of D-10.1 | passes |
| **new** round-trip tests | `compose_config(split(x)) == yaml.safe_load(x)` for the four seeds, the template, and the synthetic `reporting:` fixture; and `compose_config(write_config(cfg)) == cfg` for the conftest helper (D-12.6) | equal |
| **new** `tests/test_migration_touch_refresh.py` | §15.6's records-first refresh sequence, end to end on a migrated rapid-scale completed project (`workflow_contract` tier — `test-full` only) | composed snapshots present; rule 3.01 executed and passed; final `--dry-run` schedules nothing; data targets byte-identical |
| `pixi run lint` / `format-check` | CI gates, near-instant; the pre-push hook runs them too | green |
| `pixi run test-fast` | at the merge | green |
| `pixi run test-full` | **at the merge, not only at the push** — the branch touches all four Snakefiles and `blueearth_cst/shared/`, the paths AGENTS.md names as what the `workflow_contract` / `process_isolation` tier exists to guard. Redirect to a FILE; never pipe through `tail` | green. **From the primary checkout** — §16.5 |
| `pixi run tree-check` | **CHANGED, see §16.5.** Today it cannot fail on this design's defect (N11) | green — *after* the pin is moved off a config whose values equal the tool's fallbacks |
| `semantic_tree_diff.py` | **not shape-only.** `compare_copied_config` adjudicates snapshot CONTENT (N15) | a **predicted, enumerated FAIL** on three files and nothing else — §16.4 |
| **`check_baseline.py check`** | **the falsifier.** Primary checkout, `snake_config_baseline.yml`, WF1 with `--notemp` | **exactly three targets differ**, all three `type: yaml` config snapshots. **Zero data targets differ** — §16.3 |
| §16.6 sweep | stale spellings in docs and generated prose that no module inventory covers | no live reference to the pre-split shape |

**Not run, deliberately:** any figure gate. No `.png`/`.pdf` under `project_dir`
is consumed by a rule and this change touches no plotting code, so the
figure-revision ladder does not apply.

### 16.2 Every test module the split touches

**The inventory is measured, not sampled.** Union of six greps over `tests/`:
fixture references, `["workflows"]` indexing, `"workflows":` dict literals,
shipped-seed/template references, `config/runs/` snapshot names, and the
`simulation_window` / `ADVANCED_SETTINGS` / `historical_year_range` /
`"reporting"` surfaces. **45 existing modules**, which is exactly N17's
independently-derived count, **plus 3 new = 48** (the third,
`tests/test_migration_touch_refresh.py`, was added in r2 by `ext1-4`).
`tests/conftest.py` is inside the 45.

Tier 1 must change. Tier 2 changes mechanically or not at all. Tier 3 is
**verified no-change with the reason stated** — which is the half `risk-8`
insisted on, because "not on the list" and "checked and found safe" are the two
outcomes a sweep cannot tell apart.

**Tier 1 — modules the change necessarily edits (16 existing + 3 new).** The
commit column is §15.7's; this table and §15.7 must name the same set.

| Module | Commit | Why it breaks / changes | Expected result |
|---|---|---|---|
| **new** `tests/test_config_composition.py` | 1 | — | new, green. Full case list in §16.1, **including the D-8.6a assertion that the composed shape is visible through `workflow.config`** (§10.7) **and the D-9.6 static scan of the cross-workflow read set** (§9) |
| **new** `tests/test_split_project_config.py` | 2 | — | new, green (with the synthetic `reporting:` fixture; staged-emission cases per §16.1, including the source-untouched invariant) |
| **new** `tests/test_migration_touch_refresh.py` | 7 | — | new in r2 (`ext1-4`), `workflow_contract` tier, `test-full` only: runs §15.6's records-first refresh sequence on a migrated rapid-scale completed project — composed snapshots present, rule 3.01 really ran, final dry-run schedules nothing, data targets byte-identical |
| `tests/conftest.py` | 3 | `:136-145`'s `model_build_config` fixture reads `config["workflows"]["build_model"]` from a raw load (N16) → `ValueError` at setup; and the file gains `write_config` (D-12.6) | fixture composes via `load_composed_config`; helper added; green |
| `tests/test_cli.py` | 3 | `:18` loads the fixture as `config_fn`; `:60-73` mutates and dumps one file | green, **including `:110-131`** — the additive-carve test pops `workflows.analyze_climate` entirely and must still dry-run WF1 with identical job counts (D-9.1's "absence is not this check's business") |
| `tests/test_snapshot_config_rules.py` | 3 | `:122-126` pins the exact `CONFIG_PROJECTION` literals per Snakefile; `:129-141` pins WF3's `tuple(sorted(` derivation and `for section in guarded_sections`; `:178-193` pins `snapshot_config` params (`arch-20`) | green **with the literals carried verbatim through the §8.2 hoist**, and the derivation assertion at `:129-141` surviving; `:178-193` updated for `config_workflows` |
| `tests/test_prepare_cst_parameters.py` | 3 | `:364-378` globs `test_case/snake_config_*.yml` — which now matches T2 files — and indexes `workflows.run_stress_test.stress_test` (`repofit-3`, blocking) | green with discovery changed to the positive predicate *top level contains `workflows:`* and the value read from `compose_config`, not raw YAML |
| `tests/test_a1_acceptance.py` | 3 | `:119-130` and `:132-165` regex `historical_year_range:` out of the raw text of the template and of `snake_config_baseline.yml`; that key moves to the WF2 T2 file (`repofit-6`) | green with **both** regexes redirected to the T2 files — fixing only the template leaves the seed red |
| `tests/test_gridded_outputs_removed.py` | 3 | two obligations: its `seed_config` fixture (`:50-54`) loads `snake_config_wf2_fast.yml` whole and `_write` dumps it to one file; and `test_no_shipped_config_carries_a_gridded_key` rglobs `snake_config*.yml` over two roots with a `>= 5` emptiness guard | green. The rglob **survives and strengthens** — it now scans T1 *and* T2 files for the dead key, and `>= 5` still holds because the count only grows; the `roots` comment is updated to say so |
| `tests/test_prepare_weagen_config.py` | 3 | builds a `"workflows":` literal for a module that stops reading one (D-10.6) | green with the fixture rebuilt around the new params |
| `tests/test_semantic_tree_diff.py` | 3 | 4 `"workflows":` literals in the comparator fixtures; `compare_copied_config` now compares composed snapshots (N15) | green with the fixtures carrying workflow-scoped snapshots |
| `tests/test_copy_config_files.py` | 4 | `test_content_is_copied_verbatim` (`:51-67`) asserts byte-equality between snapshot and source — the invariant D-11.1 abolishes (`repofit-12`, blocking) | **retired** and replaced by `yaml.safe_load(snapshot) == composed_config`; the catalog/template verbatim assertions at `:64-67` **carried forward unchanged** |
| `tests/test_snapshot_project_tree.py` | 4 | a `"workflows":` literal feeding the tool §12.0 changes to compose | green against a T1-shaped literal, **plus a new case with a non-default `experiment_name`** — see §16.5 |
| `tests/test_interchange_contracts.py` | 4 | `:912-916` and `:1002-1006` open real `config/runs/` snapshots and index `snap["workflows"]["run_stress_test"]` (`repofit-7`) | **verify-only, no edit expected** — both survive D-11.1 by construction. But they cannot be *exercised* until `test_case/test_local` is re-run; §16.5 makes that an ordering constraint, not an assumption |
| `tests/test_suggest_experiment_name.py` | 5 | 8 `["workflows"]` references pinning the nested splice §12.3 retires | green against a **top-level** `experiment_name` in the T2 document; the `:222` error string and `:229` help text updated |
| `tests/test_experiment_allocation.py` | 5 | `:83,185-206` writes and reads the nested path through `runner.main` (N18) | green against the T2 top-level key. **Named by no lens** — it exists in this table only because the inventory was built rather than swept |
| `tests/test_resolve_simulation_window.py` | 5 | pins the message shape §12.5 extends (`repofit-13`) | green; existing messages **unchanged** when `shared_source`/`model_source` are absent, new cases for when they are passed |
| `tests/test_add_climate_forcing.py` | 5 | `:447-466`, the second and only other module referencing `simulation_window` | same |
| `tests/test_plot_workflow_dag.py` | 5 | 9 `"workflows":` literals — the largest single concentration in the suite — for a tool that silently drops the experiment id after the split | green, with at least one case where `experiment_name` is **not** the fallback so the silent-drop failure is detectable |

**Tier 2 — the fixture consumers (14 modules).**

`tests/snake_config_fixture.yml` is referenced by **16** modules; two of them
(`conftest.py`, `test_cli.py`) are already tier 1. The remaining 14 split by how
they use it, and the split decides the diff:

| Use | Modules | Expected result |
|---|---|---|
| **Pass the fixture path straight to a dry-run / rule check**, no mutation | `test_build_model.py`, `test_log_rules_contract.py`, `test_member_catalog_rule.py`, `test_prepare_spatial_maps_rule.py`, `test_r01_config_readers.py`, `test_region_rule.py`, `test_spatial_units_rule.py` | **green, zero diff** — see the D-12.6 correction below |
| **`safe_load` → mutate `cfg["workflows"][…]` → `safe_dump` to `tmp_path`** | `test_climate_store_contract.py` (6 sites), `test_wf1_plot_outputs.py` (3), `test_climate_store_freshness.py`, `test_compare_climate_sources.py`, `test_cross_workflow_inputs.py`, `test_guard_invalidation.py`, `test_plot_climate_source.py` | green with a **two-line** diff per site: `load_composed_config(CONFIG_FN)` to obtain the whole mapping, `write_config(tmp_path, cfg)` to write it back split. The mutation idiom itself is unchanged |

> **Correction to D-12.6, forced by this inventory.** §12.6 decided the fixture
> "is not migrated to the split layout" and would be split at write time by the
> helper alone. The inventory shows that cannot hold: **7 of the 14 modules pass
> the fixture path directly to a Snakemake run without ever loading it**, and
> under the clean break (D-15.1) a whole-shaped file is a parse error, so those
> 7 have no helper call site to change. `tests/snake_config_fixture.yml` is
> therefore **split on disk** into a T1 plus `tests/snake_config_fixture_<name>.yml`
> siblings — which is what `repofit-1`'s own fix says ("and its T2 siblings").
> The gain is that the 7 direct-pass modules need no edit at all, the fixture
> exercises the production shape, and `write_config` keeps exactly the job
> §12.6 gave it: turning one mutated whole-config mapping into a T1+T2 pair
> under `tmp_path`. Its round-trip property test is unchanged.

**The direct-pass / mutating split was verified with a wide pattern, not a
narrow grep** — every occurrence of each module's fixture constant, including
`read_text()`, `open(...)`, and any helper the constant is handed to. All seven
direct-pass modules hand the path to a Snakemake parse and nothing else:
`_parse_workflow(…, CONFIG_FN)` (`test_region_rule.py:128`,
`test_spatial_units_rule.py:257,365`, `test_member_catalog_rule.py:65`),
`api.ConfigSettings(configfiles=[CONFIG_FN])` (`test_log_rules_contract.py:102`),
`config=config_fn` (`test_build_model.py:36`), and `str(CONFIG)` as a script
param (`test_prepare_spatial_maps_rule.py:149`).

**One of the seven deserves naming rather than a zero-diff line.**
`tests/test_r01_config_readers.py:24` calls
`prep_cst_parameters(config_fn=CONFIG, lookup_fn=…)` — that is the
direct-invocation branch D-10.6 teaches to compose (§10.6, `risk-11`,
`arch-18`). It is zero-diff *and* it is the only module in the suite that
exercises that branch, so its expected result is green **as load-bearing
coverage for D-10.6**, not incidentally.

**Tier 3 — verified no change (15 modules).** Each was read, not assumed.

| Module | Why it survives | Expected result |
|---|---|---|
| `tests/test_run_workflows.py` | its 5 `["workflows"]` reads are the **run manifest**, not the config mapping (`:292,313,328,357-358`); §12.1 shows the wrapper's own config reads are unchanged | green, unchanged. A **false positive** of the grep — recorded so nobody re-derives it |
| `tests/test_shared_provenance.py` | its 3 index reads and 4 dict literals (`:29,142,172,184`) build **composed-shape** whole configs and feed them to the projection code, which D-8.1 preserves exactly | green, unchanged. Second false positive |
| `tests/test_check_project_consistency.py` | same: `:43` builds a whole config and `:95-154` mutate `workflows.build_model` / `workflows.analyze_projections` — the shape the guard receives from `sm.config` after composition (D-8.6a) | green, unchanged |
| `tests/test_project_tree_inventory.py` | enumerates `config/runs/snake_config_*.yml` and the experiment snapshot as **paths**; D-11.1 changes content, not paths, and D-11.2 adds no file to the tree | green, unchanged — **and it is the module that fails if D-11.2 leaks a copy** |
| `tests/test_snake_utils.py` | `:2690-2745` pins `run_header`'s row formatting with a T1 path string; §12.4 keeps `config_path` bound to T1 | green, unchanged. On `repofit-6`'s list, checked, no edit |
| `tests/test_surface_axes.py` | `:448-529` drive `parse_surfaces({"reporting": …})` on in-memory literals — exactly the path the hoist restores | green, unchanged; it is the coverage the hoist inherits, and the reason §16.2's synthetic fixture only has to cover *placement*, not parsing |
| `tests/test_store_region_bbox.py` | `:31` loads `snake_config_baseline.yml` but reads only `project.project_dir` and `shared.basin` — both stay in T1 | green after commit 3 migrates the seed |
| `tests/test_advanced_settings.py` | `_ADVANCED_SETTINGS_SCHEMA` is unchanged in R13 (D-13.4) | green, unchanged |
| `tests/test_batch_sizing.py` | `:335` reads `ADVANCED_SETTINGS["defaults"]["batch_disk_headroom_fraction"]`, `:343` pins its validator error path; D-13.4 moves no key | green, unchanged — **and it is the first module the §19 Q6 follow-up must edit** (`repofit-10`) |
| `tests/test_julia_runtime.py` | `runtime:` pins only; never namespaced (D-13.1) | green, unchanged |
| `tests/test_reference_window.py` | value-shape parsing of `historical_year_range`, no config file | green, unchanged |
| `tests/test_model_rebuild_cascade.py` | runs a real `snakemake all -c 1` against `test_case/test_local` via `snake_config_baseline.yml` (`:24`) | green after commit 3, **from the primary checkout only** — §16.5 |
| `tests/test_workflow_build_model.py` | `CONFIG = "test_case/snake_config_baseline.yml"`, `workflow_contract` tier | green after commit 3; only `test-full` runs it |
| `tests/test_workflow_analyze_projections.py` | same | same |
| `tests/test_workflow_run_stress_test.py` | same, plus one `["workflows"]` read of a composed-shape mapping | same |

**Acceptance item, not a sweep:** this table is the deliverable `risk-8` asked
for. A module that appears in neither §15.7 nor this table means the inventory
was rebuilt and disagreed — which is itself the finding.

### 16.3 The falsifier — `check_baseline.py check`

The manifest's target set was **enumerated, not sampled** (2026-08-20, this
worktree, `json.load(open('dev/baseline/manifest.json'))['targets']`): **seven**
targets — three `type: yaml` config snapshots
(`config/runs/snake_config_analyze_projections.yml`,
`config/runs/snake_config_build_model.yml`,
`experiments/experiment/config/snake_config_run_stress_test.yml`), two
`type: csv` CMIP6 change-factor tables, one `type: indicator`
`q_indicators.csv`, one `type: discharge` `run_default/output.csv`.

The enumeration matters because the prediction cannot be made from the three
snapshot paths alone: D-10.5 puts each T2 file's bytes into
`configuration_inputs_sha256`, so any manifested record embedding that digest
would move too. The candidate was `experiments/<exp>/results/run_metadata.json`,
which `WF3_TARGETS` declares — **and it is not a manifest target**.

> **Acceptance, falsifiably:** *exactly three targets differ, and all three are
> the `type: yaml` config snapshots. Zero data targets differ. A fourth
> differing target, or any differing target that is not one of the three
> snapshots, is a defect in this design or its implementation — not a
> re-record.* Read and report the check **before** re-recording.

**Conflict 3 of the review index is adjudicated here** (`risk-14` counted four
in-project config snapshots; the repo-fit lens verified the seven-target
enumeration and called the three-config prediction demonstrated). **Both are
right and they count different things.** There are **four** workflow-scoped
snapshot files — `analyze_climate.smk:329,357` writes
`config/runs/snake_config_analyze_climate.yml`, `build_model.smk:452,486`,
`analyze_projections.smk:752,848`, and `run_stress_test.smk:550,636` writes the
experiment-scoped one — and the wf0 file **is not a manifest target** (verified
by enumeration above). So: **four files change shape, three targets move**, and
the prediction stands unchanged. Wherever a number appears in this design it now
says which of the two it is (§1, §11.1, N10).

**One qualification, stated rather than assumed** (`arch-11`).
`effective_config_document` (`provenance.py:254-262`) folds the whole
`advanced_settings` mapping into the digested document **unprojected**, so any
change to that file's shape moves `effective_config_digest` for all four entry
points. D-13.4 removes every such change from R13's scope, which is what makes
the digest-equality property test and this falsifier mean what they say. The
property test **states the qualification in its own docstring** — a gate that
silently depends on an unstated invariant is a gate you have to decide whether
to believe.

The known thinness stands and is accepted: the manifest covers data targets, not
figures or staticmaps.

### 16.4 `semantic_tree_diff` — the sibling gate gets a prediction

`arch-21`: §16 of v1 treated `semantic_tree_diff.py` as shape-only ("if the tree
shape moved"), and D-11.1 correctly observes that no path moves — but
`compare_copied_config` (`dev/scripts/semantic_tree_diff.py:887-906`) adjudicates
**content**: it parses both snapshots, applies the directional path map to the
reference side, and requires **deep structural equality**, its docstring stating
that "an unmapped path, a changed non-path value, a missing/extra key — FAILs"
(N15). D-11.1 removes three of four `workflows.*` sections from each composed
snapshot, so a pre-change reference tree compared against a post-change live tree
FAILs — with no expected-result line anywhere in v1.

> **Prediction:** the **three** `compare_copied_config` comparisons FAIL on
> **missing `workflows.*` keys only** — each snapshot retaining exactly the
> sections its entry point's `R(entry)` composed (§8.3) — and on nothing else.
> `project`, `shared` and the retained workflow section compare clean, every
> path-valued key still maps, and **every other file in the tree compares
> clean**. Any other diff is a defect.

The whole-tree comparison needs the untracked `test_case/test_local`, so it is a
local gate like `check_baseline`, not a CI one, and it runs in the §16.5 order.

### 16.5 Gates that must CHANGE, and the order they run in

Four gates in v1's table were listed with an expected result they cannot deliver.

**(a) `pixi run tree-check` cannot fail on this defect, so the gate is
changed.** `pixi.toml:185` pins the task to `test_case/snake_config_baseline.yml`;
`snapshot_project_tree.py:219` loads the config raw and `:69-89` reads
`workflows.run_stress_test.experiment_name` (fallback `"experiment"`) and
`workflows.analyze_projections.clim_project` (fallback `"cmip6"`); that seed's
values are `experiment_name: experiment` (`:61`) and `clim_project: cmip6`
(`:40`) — **the fallbacks exactly** (N11). So the tool's meaning changes and the
pinned gate keeps passing. **This adjudicates conflict 1 of the review index**:
the repo-fit lens ("`tree-check` … read no path the design moves") and `risk-1`
("it breaks silently") answer different questions — *path moved* versus *shape
read* — and both are true; `risk-1`'s is the operative one, because the damage
is the silence.

> **Changed:** (i) `snapshot_project_tree.py` composes (D-12.0), and (ii)
> `tests/test_snapshot_project_tree.py` gains a case whose `experiment_name` is
> **not** `experiment`, so the fallback path is distinguishable from the read
> path. Expected result: green *because it composes*, not green because the
> pinned seed's values happen to equal the defaults.

**(b) The fixture-dependent layer must be exercised where it can fail**
(`repofit-7`, `arch-19`). AGENTS.md names this layer as "the one part of the
suite that cannot fail in CI or in any worktree" and records R9's 22 stale-path
failures, three of them silent skips. `tests/test_interchange_contracts.py`
(`:912-916`, `:1002-1006`) and `tests/conftest.py:136-145` sit in it. A branch
developed in a session slot can pass `test-full` green while the composed
snapshot is wrong, because the only tests that read a real snapshot **skipped**.

> **Ordering, and all five clauses of it:**
> 1. After §15.7 commit 4 lands, **re-run WF1 → WF2 → WF3 against
>    `snake_config_baseline.yml` from the PRIMARY checkout, WF1 with
>    `--notemp`** (the flag is mandatory: rule 1.14 declares wflow's
>    `run_default/output.csv` as `temp()`, and that file is the manifest's wf1
>    discharge target).
> 2. **Then** run `pixi run test-full` there, redirected to a file.
> 3. **Then** read `check_baseline.py check` (§16.3) and report it.
> 4. **Then**, and only then, re-record the baseline.
> 5. **State it plainly in the milestone record: a slot run of `test-full` is
>    not evidence about the composed snapshot, and the fixture-layer skip count
>    must be READ with `-rs`, never predicted.** The documented expected
>    baseline (499/31/1 windows, 498/32/1 ubuntu) shifts under this change, and
>    a predicted count is exactly the "nothing fails, so nobody looks" failure
>    this ordering exists to prevent.

**(c) Retiring `test_content_is_copied_verbatim` has an ordering constraint.**
It is the **only gate in the suite that can see the snapshot's shape without the
`test_local` fixture** (`repofit-12`). Retiring it without its replacement in the
same commit leaves the composed snapshot ungated on every machine that has no
freshly-run fixture — including both CI legs. The replacement invariant
(`yaml.safe_load(snapshot) == composed_config`) lands in the **same commit** as
D-11.1, never after it.

**(d) The `test_cli` prerequisite.** §16.1 names `test_cli` as the gate for every
parse-time refusal in this design, and `repofit-1` shows it is unrunnable until
`tests/snake_config_fixture.yml` is a valid T1. The fixture split (§16.2 tier 2)
is therefore part of commit 3, not a follow-up.

### 16.6 The sweep that survives, and what it is for

`risk-8` said "replace the spelling sweep with an inventory". §16.2 **adds** the
inventory and the sweep **stays**, narrowed — which is strictly stronger than
replacing it, and the reason is that the two cover disjoint ground: a module
inventory cannot see a stale path in a document, and a grep cannot see a dict
literal. The sweep is now scoped to prose and generated text only:

- `AGENTS.md` — the `config/` bin description and the Key Commands block;
- `README.md`; `config/templates/README.md`; `config/defaults/README.md`;
- `docs/` — every `snake_config_*.yml` reference and every `workflows:` nesting
  depth shown as guidance;
- `_RUNS_README` (`copy_config_files.py:60-93`) — the "Why the
  `snake_config_<workflow>.yml` files look identical" section is **deleted and
  replaced**, and the replacement must say **four**, the file count (§16.3);
- `snake_utils.py:858-860`'s docstring, which carries the retired
  `config/workflows/snake_config_*.yml` spelling (`repofit-5`);
- `scripts/plot_workflow_dag.py:50`'s usage example, which demonstrates the
  withdrawn `--config foo=bar` form (S8, §8.5b) — replaced by a form that
  survives, e.g. an `enabled` toggle or a `config_path` repoint;
- `dev/reference/naming.md` §9 and `dev/reference/workflows/rule-index.md`.

> **The sweep must anchor on the DIRECTORY, not the stem.** After D-7.4,
> `test_case/snake_config_baseline_build_model.yml` (a seed T2 **source**) and
> `config/runs/snake_config_build_model.yml` (a composed project **record**)
> differ by one path segment, so a bare `snake_config_build_model` grep
> conflates two file classes with opposite meanings (`repofit-3`).

## 17. Alternatives considered

Each carries its rejection rationale and, where one exists, the condition that
would flip it. The three top-level alternatives are unchanged in verdict from
v1; two of them gained a sharper argument from the panel, and §17.4 grew by nine
entries because the revision resolved that many choices in place.

### 17.1 CLI multi-configfile merge — rejected (S2, and independently)

Pass several `--configfile` arguments and let Snakemake merge them, instead of
referencing T2 files from T1.

*Why not:* four concrete disqualifiers, three of them recorded in the evidence.
(a) **Provenance goes actively wrong.** E5 pins the hazard: `config` reflects the
merge while `config_path` and `file_sha256(config_path)` reflect only the first
file — so `run_record.source_config.sha256` would silently describe a fraction of
the run. Under path reference it stays *narrow but true*, and D-10.5 covers the
rest through the referenced-inputs machinery **on both digest paths**, which N12
observed agreeing today. (b) **Only the first file is a DAG edge.** N1 shows
`config_path` is a declared rule input in **six** rules; `workflow.configfiles[0]`
is one path, so the other config files would be undeclared — reproducing the F7
stale-config defect (§10.3). (c) **S4 becomes unenforceable.** Snakemake's merge
is a silent order-dependent dict update: a `historical_window` in two files
produces no error, just a winner. D-9.2 and D-9.3 have no place to live — and
`risk-3` showed D-9.3 is precisely the check that must reach every pair, not
just the reachable ones. (d) **Wrapper and invocation churn:**
`build_command` (`run_workflows.py:371-386`) assembles one `--configfile`, and
every documented command line carries one.

*When it would be preferable:* if Snakemake reported per-key merge provenance and
declared every configfile as a workflow input. It does neither.

### 17.2 Status quo plus per-workflow template snippets — rejected

Keep one config file; ship four commented snippets under `config/templates/` that
a user pastes into the `workflows:` block.

*Why not:* it addresses only the authoring experience, and none of the criteria.
Duplication is untouched — the four per-project snapshots stay byte-identical
whole-config copies (N5, N10) and every variant still carries every workflow's
parameters. Nothing becomes enforceable, so S4 stays convention (criterion 1
fails outright). Nothing becomes shareable between variants (criterion 2). And a
snippet is a copy-paste aid, so the copies drift exactly as they drift today —
which is the confusion the owner named in the change request. It does not advance
modularization at all (criterion 5).

*When it would be preferable:* if the goal were purely ergonomic and the owner
had ruled *against* loader enforcement. Ruling 4 rules the other way.

### 17.3 Advanced settings folded into the workflow files — rejected (S3)

Dissolve `config/advanced_settings.yml` and move each of its entries into the
workflow file that reads it, as an "advanced" sub-section.

*Why not:* it dissolves the **authority** boundary, which is the file's entire
reason for existing. `constraints:` would become project-editable, so
`min_historical_years` — whose own comment says no project config may relax it,
because weathergenr's wavelet decomposition needs 16 annual observations —
becomes relaxable by editing a file the toolbox hands the user. `runtime:` is
worse: `julia_version` would be settable per workflow, while
`tests/test_julia_runtime.py` exists to assert that three files declare one
version. It also multiplies E2's two override mechanisms across four files — and
`arch-13` showed v1 had already introduced a **third** by accident, which §13.3
now tabulates rather than multiplies — and it has nowhere to put a genuinely
toolbox-wide default like `seed`, which four consumers across three workflows
read. §13 gets the ergonomic benefit — advanced settings visibly grouped by
workflow — without any of that, by namespacing *inside* the file.

*When it would be preferable:* if the toolbox stopped shipping hard constraints
and toolchain pins, i.e. if `advanced_settings.yml` were only defaults. It is not.

### 17.4 Considered and resolved in place

Recorded here so a reviewer can find them; each is argued at the section named.

*Carried from v1:*

- **The wrapped T2 shape** (`build_model:` at a T2 file's top level) — §7.2.
- **A verbatim T1 snapshot plus a guard that reads T2 files** — §11.1.
- **`reporting:` staying at T1's top level** — §10.4, with the condition that
  flips it (a second workflow reading `reporting:`).
- **A `test_case/workflows/` subdirectory** for the seed T2 files — §7.4;
  rejected by demonstration (`git check-ignore` exits 0 for it).
- **Handing the two disk-reading modules a T2 path** instead of params — §10.6.
- **A backward-compatible dual-mode loader** — §15.1.

*New in v2 — the panel forced each of these into the open:*

- **CWD-relative `config_path` with the splitter emitting an absolute path for
  an out-of-tree T1** — §8.4. It works and is the smaller change; rejected
  because it makes a project's config set non-relocatable and machine-specific,
  and produces two shapes of one key depending on where the project sits.
  **This is the alternative the owner may prefer at G2**, and §8.4 states
  exactly what changes if so.
- **Putting the loader in `blueearth_cst/shared/snake_utils.py`** — §8;
  rejected because it concentrates a new contract surface in the repo's
  highest-contention module (4658 lines, and the seam AGENTS.md's write-set rule
  names), for no cohesion gain a sibling topic module lacks (`repofit-9`).
- **Adding `reporting:` to a shipped seed or the template so `test_cli` covers
  the hoist** — §10.4; rejected because a shipped seed's key set is inside
  `effective_config_digest` and, for `snake_config_baseline.yml`, inside three
  baseline targets — it would move a target for a test-coverage reason and blunt
  §16.3's falsifier in the milestone that depends on it. A synthetic fixture buys
  identical coverage at no cost (`risk-13`).
- **Retiring `prepare_cst_parameters.py`'s direct-invocation branch** instead of
  teaching it to compose — §10.6; rejected because the `lookup_fn` fallback at
  `:250-251` exists to serve that branch, and removing one without the other
  leaves dead code (`risk-11`, `arch-18`).
- **Fixing the four raw-T1 tools one by one** instead of one importable
  `load_composed_config` — §12.0; rejected because the fix would be re-derived
  four times and the fifth consumer would miss it. D-12.0 makes each a two-line
  change (`risk-1`, `arch-2`).
- **Requiring a WF2 T2 file for every WF3 run** (v1's implicit position) —
  §8.7; rejected because it upgrades an explicitly-protected optionality — the
  projections overlay "must not be force-required" (N14) — from *keep a stanza*
  to *author and keep a file* (`arch-8`).
- **Migrating `tests/snake_config_fixture.yml` to the split layout versus
  keeping it whole** — §12.6 and §16.2. Resolved to the on-disk split, because
  7 of 14 consumers pass the path straight to a run and have no helper call site
  (`repofit-1`).
- **Relocating `batch_disk_headroom_fraction` in R13** — §13, D-13.4; rejected
  for this milestone because `effective_config_document` folds
  `advanced_settings` in unprojected, so the move shifts every entry point's
  digest exactly when §16.3's falsifier must distinguish "expected shift" from
  "defect" (`arch-11`). Tracked as §19 Q6.
- **Bundling a workflow rename with the config split** — §14.3 row 15; rejected
  because a rename moves a dozen baseline target **keys**, destroying the
  falsifier's ability to certify output neutrality. If the owner rules B or C,
  the rename lands as a separate series *after* baseline verification.

*Withdrawn or declined in r2 — each closed by an owner ruling or an external
finding:*

- **An opt-in `--write` mutation mode for the splitter** — §15.3; withdrawn by
  the S7 staging-emit ruling (`ext1-2`): report-only means report-only against
  user files, and an explicit mutation flag is still a mutation mode. The
  staged proposal plus a user-performed application replaces it.
- **Routing `--config` workflow-setting overrides into the composed T2 section
  before validation** — §8.5b; offered at the 2026-08-21 gate-clarification and
  **declined** (S8): a second write path into workflow settings is exactly the
  shared-seam hole D-9.1 exists to close. The overrides are withdrawn instead,
  with a form-by-form migration mapping (§8.5b).
- **Hoisting `workflows.build_model.wflow_outvars` to `shared:` inside R13** —
  §9 (D-9.6); deferred, not rejected: the relocation is the S4-compliant end
  state, but it shifts every entry point's digest and moves the guard contract
  (`_WF1_GUARDED`) exactly when §16.3's falsifier must distinguish "expected
  shift" from "defect" — the same `arch-11` principle that defers D-13.4's
  relocations. Scheduled as §19 Q7, immediately after the baseline re-record.
- **A bare `snakemake --touch` shortcut around the post-migration cascade** —
  §15.6; withdrawn (`ext1-4`): touching changes timestamps, not contents, so it
  could leave whole-shape snapshots and stale configuration records under
  products marked current. Replaced by the bounded records-first refresh
  sequence, which regenerates every configuration record before any timestamp
  moves and proves itself with a scheduled-empty dry-run.

## 18. Consequences and risks

### Owner-visible at G2 — five items, decidable without reopening anything else

| # | Item | Where | What the owner is being asked |
|---|---|---|---|
| **OV-1** | **`config_path` resolves against the T1 file, reversing v1's CWD-relative rule** | §8.4 | Accept the reversal, or take the recorded alternative (CWD-relative + an absolute path emitted by the splitter for an out-of-tree T1). If the alternative is preferred, §15.3's splitter and §16.1's path-resolution matrix change and **nothing in §§7–13 moves** |
| **OV-2** | **Migrating a project with a completed experiment re-runs the entire stress test to produce identical results** | §15.6 | Accept the cost as documented. The mitigation changed in r2 (`ext1-4`): the bare `--touch` shortcut is withdrawn; what is offered instead is the bounded **records-first refresh sequence** — every config snapshot and the consistency check regenerate before any timestamp moves, and a scheduled-empty dry-run is the equivalence proof — still opt-in, still never invoked by any tool, now tested (`tests/test_migration_touch_refresh.py`) |
| **OV-3** | **A WF3 run does not require a WF2 T2 file** | §8.7 (D-8.7) | Confirm that `config_path` is optional for every workflow, which keeps the projections overlay optional exactly as the CST method requires (N14). The alternative — v1's implicit position — makes an overlay file mandatory for every stress test |
| **OV-4** | **Workflow naming: Candidate A, final** | §14 | Confirm A. If B or C is ruled, §14.3 row 15 binds: the rename lands as a **separate commit series after** the config split has been baseline-verified, because a rename moves a dozen baseline target keys and destroys §16.3's falsifier |
| **OV-5** | **D-12.6b — `tests/snake_config_fixture.yml` is split on disk** | §12.6, §16.2 | Ratify a decision **minted by the completing author while writing §16.2**, not carried from a gate: the fixture becomes a T1 plus `snake_config_fixture_<name>.yml` siblings, because 7 of its 14 remaining consumers pass its path straight to a run and have no helper call site. The alternative is keeping it whole and having those 7 each materialize a split pair inside their own tests — a larger diff, no on-disk change. Ruling the other way changes **§12.6, §16.2 tier 2 and §15.7 commit 3, and nothing else**. It matters because `repofit-1` is **blocking** and its accepted disposition incorporates this decision |

### Positive

- Cross-workflow single-sourcing becomes **checkable** rather than
  conventional: four closed checks at parse time (D-9.1, D-9.2, D-9.3, D-9.5),
  gated by `test_cli`, plus the frozen shrink-only cross-workflow read contract
  with its completeness-and-minimality scan (D-9.6, closing §19 Q2). D-9.3 now
  reaches **every pair** of T2 files rather than the three of six an
  entry-point-scoped check could see (`risk-3`), D-9.5 closes T1's top level,
  which is what makes the migration detector complete (`arch-6`), and the one
  measured cross-workflow value read (`wflow_outvars`) carries a scheduled
  hoist (Q7) after which S4 holds with zero exceptions.
- The four per-project config snapshots stop being byte-identical whole-config
  copies (N5) and become the workflow-scoped views their filenames have always
  promised — closing a confusion `_RUNS_README` currently has to apologize for.
- A user editing one workflow opens a file containing that workflow's settings
  and nothing else; a project that never runs a workflow needs **no file for it
  at all** — and under D-8.7 that now holds for WF2 as well as WF0, which was
  the asymmetry `arch-8` found.
- Two modules stop re-reading the source YAML from disk (§10.6), removing a class
  of coupling that would have broken silently under any composition scheme — and
  the same change gives **rule 3.09 a rerun trigger it does not have today**
  (§10.3, the correction `arch-7`/`risk-7` forced).
- Each T2 file's bytes enter `configuration_inputs_sha256` on **both** the
  parse-time and record-time paths through the existing referenced-inputs
  machinery, with **no schema change** (§10.5). N12 observed the two agreeing
  today, so keeping them identical is a preserved invariant rather than a hoped
  one.
- The design now names every test module it touches (§16.2, 45 existing + 3 new)
  — a surface v1 left to a grep sweep, and the surface that produced N18, a
  breaking consumer no review lens found.

**Removed from v1's positive list:** *"a `reporting:` caption edit stops
dirtying WF1's rule 1.06"*. The mechanism is real, but N9 shows `reporting:`
appears in **no** shipped config and no project config — only as a commented
template block. A benefit no user is currently experiencing is not evidence for a
design (`risk-13`).

### Negative

- **The shipped seed set grows from 4 files to 4 T1 files plus up to 12 T2
  files** (§7.4). v1 said "up to 20"; D-8.7 removes the four content-free wf0
  files, which reconciliation could never have collapsed because they are empty
  by construction (`risk-14`). The owner's stated downside ("having to maintain
  more files") still arrives, in reduced form. The mitigation is real but
  prospective: N7 measured that no two current variants share a workflow section
  verbatim, so the implementation must first reconcile incidental differences and
  only then point several T1 files at one shared T2. **Sharing is ruled IN for
  wf0/wf1/wf2 and OUT for the WF3 T2 file** (`risk-5`) — a shared WF3 file would
  let `suggest_experiment_name.py` silently re-point another project's
  experiment. Criterion 2 is met on **snapshots** and on **per-file scope**; it
  is *not* met on total source bytes, and this design does not claim it is.
- **Migrating a project with a completed experiment re-runs the whole stress
  test** (§15.6, OV-2). Unbudgeted in v1 and a real charge against G5's
  "mechanical, **bounded** migration": rewriting T1's bytes re-fires rule 1.06,
  which moves the wf1 snapshot digest, which re-fires 3.01, which rewrites a
  sentinel that 3.09 and 3.10 declare **bare**, and the realization cascade runs.
- **The test-fixture rework is the largest single migration item**, and v1
  omitted it entirely: `tests/snake_config_fixture.yml` plus 16 consuming modules
  plus a conftest helper that does not exist today (§12.6, §16.2). Under D-12.6
  the diff is bounded — 7 modules unchanged, 7 taking two lines each — but the
  work is real and lands in one commit with the loader.
- Config snapshots lose their source comments (§11.1). Accepted — that bin is a
  record, not a source, and is documented as "written by the run".
- A clean break (§15.1) breaks every existing project config until it is
  migrated. Mitigated by a precise parse-time error naming the offending key and
  the migration doc, a migration script that **stages the proposed T1 + T2
  beside the user's config and verifies the staged pair against the source
  before reporting it applicable** (D-15.4b) — no tool ever rewrites the user's
  file (§15.3, owner ruling 2026-08-20) — and a precedent six days old.
- The reader now needs two files open to reason about one workflow's run — the
  cost of any decomposition — **and two path-anchoring rules three lines apart**
  in T1 (§8.4, OV-1). Mitigated by error messages naming both the resolved path
  and the anchor, and by the composed snapshot being a single-file view of what
  actually ran.
- `dev/baseline/manifest.json` must be re-recorded for **three** targets, a
  primary-checkout, no-other-session-live operation — and only after §16.3's
  check has been read and reported.
- **Ad-hoc `--config` overrides of workflow settings are withdrawn** (S8,
  narrowed G4 — an owner-ruled CLI-contract break, no longer described as
  "unchanged"): such an override is a parse-time rejection naming the key. The
  replacement is a T2 edit, or a command-line `config_path` repoint at an
  alternative T2 file; §8.5b carries the full form-by-form migration mapping,
  including the one documented example (`plot_workflow_dag.py:50`) that stops
  working.
- **Four** config snapshots change content shape, not three; the fourth (wf0) is
  not a baseline target (N10, `risk-10`), and `_RUNS_README` must say four.

### Neutral / must be planned for

- **Two** migration documents, not one (`repofit-8`): the user-facing
  `docs/migration-config-tiers.md` and the naming.md-mandated internal record
  `dev/milestones/r13/migration_config-tiers.md`, without which the R13 seal is
  incomplete.
- A migration script, and one docs sweep scoped to prose (§16.6).
- `_ADVANCED_SETTINGS_SCHEMA` gains a nested level **only when a namespaced
  entry is first added** — no such edit lands in R13 (D-13.4).
- `suggest_experiment_name.py` loses its parent-block creation branches, its
  `_block_end` helper, its comment-run anchoring and its flow-style refusal, and
  its verifier is rewritten (§12.3). This is a simplification, but it is not the
  "depth handling changes" v1 described.
- The wf0 composed snapshot is near-empty for three of four seeds, by design
  (§11.1).

### Residual risks

| Risk | Severity | Mitigation |
|---|---|---|
| A T2 file left undeclared as a rule input reproduces the F7 stale-config defect silently | high | D-10.3 declares it per rule, all six named by file:line; **and D-10.6 lands in the same commit**, because for rule 3.09 the `ancient()` input is an existence edge only and the param is the real trigger (§10.3) |
| The splitter mangles a **value** — not a comment — via an alias or a block scalar, producing a config that parses and runs with different numbers | high | D-15.4a refuses on `&`, `*`, `<<:` or a block scalar inside a workflow section, naming construct and line; D-15.4b round-trips the user's own file before rewriting it. v1 booked this as "mangles a comment block", medium |
| `SHARED_SEAM_KEYS` drifts from `shared:` as keys are added | medium | coupled-edit discipline plus a test asserting every `shared:` key in the shipped template appears in the set — the shape `tests/test_advanced_settings.py` already uses |
| A composition refactor rebinds the composed dict to a name other than `config`, and every WF3 run fails at rule 3.01 *after* WF1 and WF2 have run | medium | D-8.6's invariant is stated with its consumer of record (`check_project_consistency.py:225` via `sm.config`) and checked by a `workflow.config` assertion in `tests/test_config_composition.py` (`arch-12`, `risk-9`) |
| A fourth baseline target moves | high if it happens | §16.3 makes it a **defect**, not a re-record; the check is read and reported before any re-record |
| A branch passes `test-full` green in a session slot while the composed snapshot is wrong, because the only tests that read a real snapshot skipped | medium | §16.5(b)'s five-clause ordering: re-run the fixture from the primary checkout, then `test-full` there, then read the baseline, then re-record — and read the skip count with `-rs` rather than predicting it (`repofit-7`) |
| Two T1 files are pointed at one WF3 T2 file, and naming one project's experiment silently re-points the other's | medium | Nothing at parse time can see it (§8.4's duplicate check is within one T1). Stated as a rule in the implementation brief and enforced by a reviewer — this design does not claim a check it does not have (`risk-5`) |
| A future reader reaches into an unloaded workflow section | low | `KeyError` at parse time, gated by `test_cli`; the fix is to declare it in `CONFIG_PROJECTION`, which puts it in `R(entry)` (§10.7) |

## 19. Open questions

Reconciled against the panel, then against external round 1: two questions are
now **closed** (Q1 in v2; Q2 in r2 by D-9.6), two stand unchanged in substance,
one is the owner ruling OV-4, and two are tracked follow-ups (Q6 from the
panel; Q7 new in r2).

- **Q1 — key spelling. CLOSED in favour of `config_path`** (§7.1). v1 left it a
  reviewer call between `config_path` and `workflow_config`. `repofit-11`
  settled it on the repo's own rule: `dev/reference/naming.md` §3 makes `_path`
  mandatory for new code holding a file-path string, and `workflow_config` reads
  as a loaded mapping (`_cfg` territory), which is exactly what the key is not.
  The prose collision with the Snakefile-local variable is resolved by renaming
  the **variable** to `t1_path` (§8.2), not the key.
- **Q2 — should the declared cross-section read set become a checked
  contract? CLOSED in favour of the check, in r2** (D-9.6, resolving
  `ext1-1`). v2 weighed the cost of parsing the Snakefiles against what it
  buys; the external round settled the question the other way by showing what
  its absence costs — a known exception to S4. The read set is now the frozen,
  shrink-only `CROSS_WORKFLOW_READS` contract with a completeness-and-
  minimality static scan in `tests/test_config_composition.py`, on the
  `tests/test_cross_workflow_inputs.py` precedent. `guarded_sections` no longer
  carries enforcement weight alone; it keeps the guard's identity comparisons,
  enumerated in D-9.6's Class-2 table.
- **Q3 — should `split_project_config.py` be retired after the migration?** The
  prune tools are permanent; a migration tool arguably is not. Recommend keeping
  it one release cycle, then deleting it rather than carrying a map for its own
  sake — the repo's stated stance on migration maps.
- **Q4 — should `run_workflows.py` preflight the `config_path` values?**
  Deliberately out of scope (§12.1), **unchanged in substance**. `risk-15`
  argued the preflight is worth most exactly at migration, when every project
  has four brand-new path references never resolved once. D-8.7 removes that
  case: the splitter emits a path only for a section with content, and §15.5
  step 3 says delete the **key**, never leave a dangling path — so the failure
  the preflight would front-load is now a typo rather than an expected first-run
  state. It remains cheap and in the spirit of `_check_wf1_leaves`, and it still
  makes the wrapper resolve files it otherwise never opens.
- **Q5 — naming.** Now the owner ruling **OV-4** (§18). §14 recommends Candidate
  A. If B or C is ruled, §14.3 row 15 binds: the rename lands as a separate
  commit series *after* the config split is baseline-verified.
- **Q6 — NEW: when does `batch_disk_headroom_fraction` move to
  `defaults.run_stress_test:`?** D-13.4 rules the placement policy in R13 and
  applies it to **new** entries only, deferring every relocation, because
  `effective_config_document` folds `advanced_settings` in unprojected and the
  move would shift `effective_config_digest` for all four entry points exactly
  when §16.3's falsifier must distinguish an expected shift from a defect
  (`arch-11`). The follow-up is one key and carries three inherited obligations:
  the coupled edit set is **four** files — `_ADVANCED_SETTINGS_SCHEMA`
  (`snake_utils.py:869-879`), the settings file, `tests/test_advanced_settings.py`
  and **`tests/test_batch_sizing.py:335,343`** (`repofit-10`, a consumer
  D-13.2's original trio never named); the digest shift is user-visible in
  `effective_config_sha256` and `configuration_inputs_sha256` with no way to
  attribute it unless the migration note says so; and it must land **after** the
  R13 baseline has been re-recorded, never in the same series. **This is where
  `repofit-10`'s deferred half is tracked.**
- **Q7 — NEW in r2: the `wflow_outvars` hoist to `shared:`** (D-9.6, resolving
  `ext1-1`'s hoist half). Scheduled **immediately after the R13 baseline
  re-record**, in the same slot as Q6 and never in the same series, for the
  `arch-11` reason plus the guard-contract move D-9.6 states. The coupled-edit
  set, so the follow-up inherits obligations rather than rediscovering them:
  `build_model.smk:118` (read moves to `shared_cfg`),
  `run_stress_test.smk:537-540` (read moves; the `CROSS_WORKFLOW_READS` entry
  is **removed**, which D-9.6's minimality check forces in the same commit),
  `SHARED_SEAM_KEYS` gains `wflow_outvars` (and D-9.2's rejection set follows
  by construction), `_WF1_GUARDED` at `check_project_consistency.py:41` gains
  `("shared", "wflow_outvars")` so the drift guard keeps refusing a post-build
  edit, the pinned literals at `test_snapshot_config_rules.py:122-141`, the
  splitter/template guidance, and a migration note attributing the
  all-entry-point digest shift — after which S4 holds with **zero** exceptions
  and `CROSS_WORKFLOW_READS` is empty.

## 20. Revision log

| Version | Date | Change |
|---|---|---|
| v1 | 2026-08-20 | Initial draft for gate G1. Incorporates the intake's five confirmed scoping rulings and the post-stage-0 scope amendment (R13 milestone wiring; workflow-naming section). Decides the two questions the intake left open: `reporting:` moves to the WF3 T2 file with a loader hoist (§10.4); clean break rather than backward compatibility (§15.1). Adds empirical premises N1–N8. Sections 1–20, 1341 lines. |
| v2 | 2026-08-20 | Revised against the internal three-lens panel — **52 findings (5 blocking, 27 major, 20 minor), every one dispositioned in `ledger.md`**. Verified ten new premises N9–N18 by direct read or execution rather than argument, including the two the panel self-flagged as argued-not-run (N11, N12). Adds decisions D-8.5 (the composition contract, with `declared_sections` as the channel `arch-1` found missing), D-8.6 (the `config` rebinding invariant and the `--config` passthrough), D-8.7 (`config_path` optional, keeping the projections overlay optional), D-9.5 (T1's top level closed), D-12.0 (`load_composed_config` for the six raw-T1 consumers v1 never named), D-12.6 (the test-fixture surface, the largest omitted migration item), D-13.4 (no advanced-settings key moves in R13), D-15.4a/b (splitter refusals and a round trip against the user's own file), D-15.5 (the post-migration re-run cost). **Reverses one v1 decision**: `config_path` resolves against the T1 file, not the CWD (§8.4, `repofit-2`; owner-visible OV-1). **Relocates the loader** to `blueearth_cst/shared/config_composition.py`. **Corrects four factual claims**: six rules not five (N1/`arch-15`), four snapshots not three (N10/`risk-10`/`risk-14`), `reporting:` present in no shipped config (N9/`risk-13`), and rule 3.09's rerun trigger is a param, not an `ancient()` input (N13/`arch-7`≡`risk-7`). Adds §16.2's inventory of **every** test module the split touches (45 existing + 2 new), which produced N18 — a breaking consumer no lens found. Adjudicates all three index conflicts (§12.0, §16.3, §16.5a). **Authored across two spawns**: §§1–15 by the first, which ended on a session limit mid-§15.7; §§16–20 and `ledger.md` by the completion spawn, which also corrected D-12.6 (7 of 14 fixture consumers pass the path directly and have no helper call site), the §15.7 commit-3 test list, and the header's line budget. Awaiting G2. |
| v3 | 2026-08-21 | Revised against **external round 1** (`external-review-r1.md`, verdict `revise`, four major findings) — every disposition in `ledger.md`. **`ext1-1`**: §9 gains **D-9.6** — the cross-workflow read inventory as a measured deliverable (exactly one value read, `run_stress_test.smk:537-540` → `workflows.build_model.wflow_outvars`; two declared guard comparisons; false positives recorded), the frozen shrink-only `CROSS_WORKFLOW_READS` contract with a completeness-and-minimality static scan (on the `LEAVES`/`test_cross_workflow_inputs.py` precedent), §19 Q2 **closed**, and new **Q7** scheduling the `wflow_outvars` hoist immediately after the baseline re-record with its full coupled-edit set (incl. the `_WF1_GUARDED` move). **`ext1-2`** (owner ruling S7, 2026-08-20): §15.3–15.5 reworked to **staging-emit** — the splitter emits proposed T1+T2+report into a script-owned staging directory, application is a user step, `--write` withdrawn; D-15.4b verifies the staged pair; §16 gains the source-untouched invariant. **`ext1-3`** (owner ruling S8, 2026-08-21): G4 **narrowed** in §2 (`--configfile` path contract, wrapper invocation, `config_path` forwarding — nothing more); §8.5b reworked with the five-row override migration mapping (T2 edit or `config_path` repoint; `enabled`/`project`/`shared` survive; top-level and workflow-setting forms die at parse), a factual correction on `update_config`'s recursive merge, and design-level treatment of `run_workflows.py`'s disclosure recording and `plot_workflow_dag.py:50`'s example. **`ext1-4`**: the bare `--touch` shortcut is withdrawn; §15.6 defines the bounded **records-first refresh sequence** (regenerate all four snapshots + execute rule 3.01 before any touch; scheduled-empty dry-run as the equivalence proof), tested by new `tests/test_migration_touch_refresh.py` (§16.2 counts now 45+3=48). §5 records S7/S8; §17.4 records the withdrawn alternatives. New decision IDs: **D-9.6**; new tracked question: **Q7**. Awaiting G2 (round-2 trigger check first: D-9.6 and the refresh sequence are new mechanisms). |
