# Intake — R14 config shape design run

- Run: `r14-config-shape` · started 2026-08-22 · intake materialized 2026-08-24
  · driver: interactive session (`session-1` lane, branch `feat/r14-config-shape`)
- Genre mapping: refactor/architecture design (goal, what-changes,
  alternatives, migration) → recorded as `decision-record`, the same mapping
  R13 used.
- Ultimate goal (owner-stated): modularizing the toolbox. R13 split the config
  by FILE; R14 reshapes it WITHIN that split.
- **Input:** `dev/milestones/r14/config-shape-scoping.md` — 85 indexed changes
  (`C-01`..`C-85`), seven structure rules, eight naming rules, and nine open
  questions, all now closed. This intake does not restate it; it carries what
  the design run needs and points at the rest.

## Change request (verbatim, owner, 2026-08-22)

> A few question reg. config.ymls:
>
> Main config.yml:
>
> - does it make sense to remove the shared layer and place all the parameters
>   underneath within project?
>
> - static_dir: is it now safe to remove this parameter? Is anyone downstream
>   consuming it?
>
> - historical window shall go under climate i think, as this window describes
>   the raw climate data's extraction window.
>
> These are a few examples. I think we can first do a "free, brainstorm" level
> assessment of parameters, their naming, nesting structucture under the
> config.yml.

Follow-up, same dialogue:

> Can you open a new branch for R14 and consider this as a preparation
> exercise? Also, put everything in scoping document. assign an index/id to
> each change so I can refer easily later on

The preparation exercise is complete. The scoping document is its output and
this run's input.

## Problem

R13 fixed *which file* a key lives in. It did not touch *which section*, or
*what a key is called*. Both are still answered by history:

- `shared:` names a RELATIONSHIP ("read by ≥2 workflows"), not a kind, so one
  heading holds a basin geometry, a climate binding, a hydrological-year
  convention and a thread count.
- One concept has several spellings — `starttime`/`endtime` vs
  `historical_year_range: [a, b]` vs `future_horizons.<n>: [a, b]`; `source`
  meaning both a catalog FILE and a catalog ENTRY.
- The experiment guard's key list is maintained by hand because no section
  boundary distinguishes "changes the numbers" from "changes only the
  wall-clock".

These are P3 and P4 of `dev/working/parameter-placement.md`, still open.

## Confirmed scoping rulings (owner, 2026-08-22 and 2026-08-24)

Settled framing. The design may not re-litigate these; it specifies how they
land. Each is recorded with its evidence in the scoping document.

**Structure and naming policy.** Seven structure rules `S1`–`S7` and eight
naming rules `N1`–`N8` are adopted, including `N8` (a window is declared in
inclusive integer YEARS, calendar resolution deferred to the engine seam) and
`N6` (counts take the `n_` prefix). `N1` and `N3` each carry one named
exemption: the `n_` prefix itself, and `project_dir`.

**The nine open questions are all closed** — `Q-B`, `Q-D` (2026-08-22); `Q-C`,
`Q-G` (2026-08-24, with the WF3 cluster); `Q-A`, `Q-E`, `Q-F`, `Q-H`, `Q-I`
(2026-08-24, in the closing walkthrough). Two changed a rule rather than
choosing between drafted options:

- **`Q-F` was settled by a PROBE, not a preference** (E1, E2 below). It
  re-scoped `C-04`, and it means **S2's headline payoff does not survive as
  stated**: the experiment guard becomes mechanical because R14 empties T1 of
  every non-identity key (`C-51`, `C-54`, `C-55`, `C-77`), NOT because of the
  three-class split. S2's surviving payoff is the digest carve-out (`C-79`)
  alone. The design must carry that claim honestly.
- **`Q-E` resolved by AUTHORITY, not by destination.** Defaults live in
  `advanced_settings.yml` when they are toolbox-wide policy, in the entity's
  own registry when they are per-entity metadata (`C-64`), and in
  `constraints:` when a project may not relax them (`C-65`).

**Scope inclusions ruled in.** `C-85` bundles the `snake_config_` →
`project_config_` file rename into R14's single migration window (ruled
2026-08-24). Its BREADTH — filenames only, or the identifiers carrying it —
is the design's to settle.

**Two rows are deliberately not behaviour-preserving**, and the migration tool
must say so per value rather than rewrite silently: `C-69` for a config that
set `run_historical: false`, and `N8` for a project that sets
`water_year_start != Jan`, where `C-38` REFUSES rather than shifting.

## Constraints

1. **AGENTS.md hard constraint (S5).** hydromt / hydromt_wflow / wflow /
   weathergenr vocabulary is used verbatim. No key inside `config/defaults/*`
   or a data catalog is renamed, moved, or removed by this milestone. **This
   constraint already caught one row** — `C-82`, withdrawn (E3).
2. **R13 is accepted.** Any change to `T1_TOP_LEVEL` (D-9.5),
   `SHARED_SEAM_KEYS`, `HOISTED_SECTIONS` (D-10.4) or the composition
   invariant (D-8.1) is an AMENDMENT to an accepted design, recorded as such.
   `C-78` retires `HOISTED_SECTIONS` outright and is the largest such
   amendment.
3. **Digest identity.** A key present-vs-absent — not merely re-valued — moves
   `effective_config_digest`, and `_frozen_differences`' key-union diff then
   refuses every already-run experiment in every project. Acceptable **only**
   if it happens once, which is the whole argument for one bundle.
4. **Two homes for a window.** `climate.window` (extraction) and
   `simulation_window` (model run) are necessarily separate and must stay
   visibly separate after `N4` and `N8` make them look alike.
5. **No change to what any workflow COMPUTES** — with the two per-row
   exceptions named under the scoping rulings above, each carrying a migration
   invariant.
6. `get_config` contract preserved; `workflow.configfiles[0]` forwarding
   preserved (to downstream **Python** scripts — the R-forwarding wording in
   older records is stale, R13 E5).
7. No new dependencies without owner approval.

## Decision criteria

- **D1 — Does it answer P2 mechanically?** Four inert-or-partly-inert
  parameters have been found by hand and zero by machine. A shape that does not
  make `C-37` feasible has not solved the problem with real consequences.
  **`C-37` must fail CLOSED** — see E5.
- **D2 — Does it preserve guard semantics?** Specifically the reason
  `_WF1_GUARDED` guards `shared` leaf-by-leaf while guarding `project` whole.
  The `Q-F` probe found that reason is removed by R14 itself; the design must
  show that rather than assume it.
- **D3 — Is the migration mechanical?** Every register row expressible as a
  pure old-path → new-path rewrite for `C-38`, except the two rows explicitly
  ruled non-preserving, which need the "mechanical, but tell the user what
  changed" hook.
- **D4 — Does a new parameter now have exactly one obvious home?**

## Success criteria

An accepted decision-record design specifying: the final section layout per
file, the naming policy as applied, loader and validation changes, the
`HOISTED_SECTIONS` retirement, the guard/freeze/digest specification against
the new layout, `schema_version: 2` and the v1 refusal, the `C-38` rewriter
including its two non-preserving hooks, the `C-85` rename breadth, template and
`test_case` restructuring, and the validation gates — ready for `task-brief`.

**Criterion 5 is scoped, not blanket** (E4, and it is the one this intake
corrects): `pixi run test-full` green on both platforms, and
`check_baseline.py check` showing **zero movement in the four DATA targets**.
The three `snake_config_*.yml` snapshot targets WILL move — R14 renames their
paths (`C-85`) and rewrites their contents by design — and are re-recorded, not
defended. R13 set this precedent exactly: *"the split moved the two narrow
config snapshots, the hoist moved all three, and zero data targets moved in
either"* (`dev/LOG.md`, 2026-08-22).

## Non-goals

- Re-opening R13's tier split, path-reference composition, or the single
  `--configfile` CLI contract.
- Any change to `config/catalogs/*` or `config/defaults/*` internals.
- Changing what a workflow computes, beyond the two ruled exceptions.
- Web/API accommodations. CST-API and the frontend never constrain this repo.
- The two boarded number-movers: `t2608241413` (the generated series anchored
  to a hardcoded 2010) and `t2608241414` (the two baseline WF3 configs
  diverged). Both move numbers and are out of R14 by construction.
- Adding climate datasets (`t2608222239`) or making the extraction set derived
  (`t2608222252`) — the SHAPE is in scope, the capability is not.

## Derived-artifact register

Author spawns are barred from touching these; each is regenerated from the
accepted design after G2, by the implementation task unless noted.

| Artifact | Regeneration |
|---|---|
| `config/templates/*.template.yml` × 4, **plus the new WF0 template** (`C-84`) | implementation |
| `test_case/` config sets × 4 (17 files), renamed under `C-85` | implementation |
| `.gitignore` un-ignore glob — **moves in the SAME commit as the rename** (E8) | implementation |
| `tests/snake_config_fixture.yml`, `tests/data/presplit/**` (gains a v1→v2 pair) | implementation |
| `config/advanced_settings.yml` + `_ADVANCED_SETTINGS_SCHEMA` — three `defaults:` comments name overriding keys that `C-51`/`C-53`/`C-54` move (E7) | implementation |
| `dev/baseline/manifest.json` — three config-snapshot targets re-recorded (E4) | implementation, after the bundle |
| `docs/guide/*.qmd`, `docs/migration-config-tiers.md`, `README.md`, `AGENTS.md` | implementation (keep-references-current) |
| A migration note, successor to `docs/migration-config-tiers.md` | implementation |
| `docs/cst-toolbox-technical-note-2025.md` (`C-75`) | implementation, lands with `C-32` |
| `dev/roadmap.md` R14 entry | driver, at stage-7 landing |
| `dev/milestones/README.md` index row | at milestone seal, not this run |
| Implementation `task-brief` | stage-7 handoff |

## Evidence register

Verified 2026-08-24 in this worktree (branch `feat/r14-config-shape`, at
`b19649a1`) by the driver, directly against the code. Columns: premise /
source / observation / precision / reproduction / confidence.

| # | Premise | Source | Exact observation | Precision | Reproduction | Confidence |
|---|---|---|---|---|---|---|
| E1 | S2's carve-out makes the experiment guard mechanical | `check_project_consistency.py:47-53,183-196`; `write_experiment_config.py:63-95`; `run_stress_test.smk:61-65` | **REFUTED as stated.** THREE mechanisms, not one: the drift GUARD compares live config vs the WF1/WF2 snapshots over `_WF1_GUARDED` = (`project`, `shared.basin`, `shared.wflow_outvars`, `workflows.build_model`); the experiment FREEZE (`_frozen_differences`) compares recorded `run_stress_test` keys; the DIGEST is `CONFIG_PROJECTION`. `compute:` sits in the latter two and **never the guard** | file:line reads | read the three modules | high |
| E2 | A WF1 snapshot could carry WF3's sections, so "guard everything" is expressible | `copy_config_files.py:89`; `config_composition.py:581-598` | **REFUTED.** *"a WF1 snapshot does not carry WF3's stress-test grid."* `compose_config` keeps every T1 key plus the entry's OWN workflow body; the other three get `{enabled: ...}` only (`merged[name] = section`). The composed doc is NOT projected to `declared_sections` — that tuple selects which T2 FILES load. Consequence: guarding `workflows` whole would compare bare enabled stanzas and refuse an experiment when a workflow is toggled | file:line reads | read `compose_config` | high |
| E3 | `generate_weather.parallel` / `n_cores` are project-config keys `C-82` may regroup | `config/defaults/weathergen_config.yml:39,81-82` | **REFUTED.** Both live inside the `generate_weather:` block of the ENGINE config file, which Constraint 1 puts out of reach. `C-82` WITHDRAWN 2026-08-24. `C-81`'s path key already makes them reachable per basin, so promoting them would give one setting two homes | file:line reads | `grep -n 'parallel\|n_cores' config/defaults/weathergen_config.yml` | high |
| E4 | `check_baseline.py check` is a clean falsifier for "no number moves" | `dev/baseline/manifest.json`; run 2026-08-24 | **RUNS AND PASSES TODAY: `OK - 7 target(s) match manifest`.** But **three of the seven targets are `snake_config_*.yml` snapshots** that `C-85` renames and every register row rewrites, so the gate CANNOT be green across R14 as a whole. Only the four data targets are the falsifier: two CMIP6 change-factor CSVs, `q_indicators.csv`, `run_default/output.csv`. It also warns: the fixture is UNTRACKED and shared by every branch, so a pass may reflect another branch's code | demonstrated | `pixi run python dev/scripts/check_baseline.py check` | high |
| E5 | The register's source keys exist | all 85 rows vs 104 config-file keys + 37 `get_config` keys | Swept 2026-08-24: **one substantive defect (E3)**; `disk_headroom_gb` (`C-34`) is read by the Snakefile but appears in NO template and NO shipped config; `C-52` retires a `method:` section this document drafted, never one that shipped. `C-45`'s cited `start_month_hyd_year` refusal verified live at `analyze_projections.smk:144-155`. **The first run of this sweep failed OPEN** — its ground-truth extraction returned zero keys and it then reported 19 flags, several artefacts, with nothing saying so | demonstrated | re-run with a non-empty ground-truth assertion | high |
| E6 | `C-85`'s blast radius is 221 occurrences / 68 files | board note `t2608191733a`, measured 2026-08-19 | **STALE, by a third, in five days.** Re-measured 2026-08-24 by `git grep` over tracked files outside `dev/`: `snake_config` = **301 occurrences / 76 files**; `project_dir` = **826 / 95**, which is why `Q-A` keeps the name. Counting method must be stated or the two are not comparable — the 2026-08-19 figure counts matches, ripgrep's default counts LINES | demonstrated | `git grep -o '<term>' -- ':!dev' \| wc -l` | high |
| E7 | `advanced_settings.yml` is a working home for `C-36`'s defaults | `config/advanced_settings.yml`; `snake_utils._ADVANCED_SETTINGS_SCHEMA` | CONFIRMED, and stronger than assumed: a three-way AUTHORITY split (`constraints:` / `defaults:` / `runtime:`), closed schema, unknown keys rejected at parse time, `tests/test_advanced_settings.py` enforcing. **Every `defaults:` entry already NAMES its overriding config key** — which is the discoverability `C-36` wants. Consequence: three of those comments name `shared.julia_threads`, `shared.seed`, `shared.water_year_start`, all moved or deleted by `C-54`/`C-51`/`C-53` | file:line reads | read the file and the schema | high |
| E8 | The `test_case/` seeds are tracked normally | `.gitignore:140-141` | `test_case/*` then `!test_case/snake_config_*.yml` — the seeds are tracked ONLY through that un-ignore glob. Renaming the files without moving the glob in the same commit makes them untracked in SILENCE: `git status` reports the old paths deleted and never lists the new ones. Verify with `git ls-files test_case/` | file:line read | `git check-ignore -v <name>` | high |
| E9 | `HOISTED_SECTIONS` is a general mechanism | `config_composition.py:122-134` | `{"run_stress_test": ("reporting",)}` — ONE entry, described in its own comment as *"A closed two-entry map, not a general mechanism."* `C-77` empties it, so `C-78` retires it on the precedent R13 set with `CROSS_WORKFLOW_READS` | file:line read | read the constant | high |
| E10 | `pixi run test-fast` is a usable branch gate | run 2026-08-24 | **RUNS GREEN: 2983 passed, 8 skipped, 1 xfailed, 99.6 s.** Skips are the three `--run-integration` workflows and five `temp()` artifacts needing `--notemp`; the xfail is the known hydromt 1.3 `to_yml` bug with an upstream reproducer | demonstrated | `pixi run test-fast` | high |

## Gate-materialization check

Verified runnable in this worktree, 2026-08-24. Every gate the plan cites can
execute **today**.

- `pytest tests/test_cli.py` — **runnable**; the parse-time gate that dry-runs
  all four entry points. The only place a malformed `config/defaults/*.yml`
  surfaces, and the cheapest check for a register row that breaks a rule's
  declared input.
- `pixi run test-fast` — **runnable and green** (E10). The local gate,
  including before a push.
- `pixi run test-contract` / `test-full` — **runnable** (`pixi.toml:152-153`).
  Required here rather than optional: R14 touches `shared/` and `script:`
  signatures, which is the `workflow_contract` / `process_isolation` tier's
  own trigger.
- `pixi run lint` / `format-check` — **runnable** (`pixi.toml:164,166`).
- `check_baseline.py check` — **runnable, currently 7/7 green**, with the
  scoping correction in E4 and criterion 5. **Pre-change snapshot EXISTS**
  (`dev/baseline/manifest.json`, recorded at `0d256a41`, clean). Two caveats
  the design must carry: the fixture is untracked and shared across branches,
  so a pass is weaker evidence than it looks; and `t2608220920` (the indicator
  reference predating the weathergenr 2.0.0 upgrade) is still `status:
  backlog` although the gate is green today — either R13's pass-2 re-record
  resolved it and the board note is stale, or the green is the shared-fixture
  artefact. **Resolve which before trusting this gate as R14's falsifier.**
- **Run WF1 with `--notemp` when the run feeds `check_baseline.py`** — rule
  1.14 declares wflow's `run_default/output.csv` as `temp()`, and that file is
  a manifest target, so without the flag the gate fails "target missing" and
  reads as a defect.
- `pixi run tree-check` — **runnable** (`pixi.toml:187`), pinned to the
  baseline config. Report-only until `--delete`.
- `semantic_tree_diff.py` — **runnable** (`dev/scripts/`). Needed here rather
  than optional: `C-67` and `C-71` change `params:`-threaded values and `C-61`
  renames WF2 figure directories, so the tree SHAPE moves.
- **Stale-spelling sweep** — no tool exists; the design's migration plan must
  name one. `C-85` alone is 301 occurrences across 76 files (E6), and the
  register renames dozens of keys. A grep-based sweep per retired spelling is
  the cheap gate, and `C-37` is its mechanical successor — which must fail
  CLOSED (E5).

## Open items the design must settle

Not questions being weighed — these are unfinished and no entry in the
scoping document's (now fully closed) question table would surface them.

1. **`C-48` has no destination.** It was to be a `reporting:` key placed by
   `Q-G`; `C-77` deleted the section and `Q-G` retired. Its S2 classification
   is untouched — which variables get drawn cannot move a number — but it has
   nowhere to live.
2. **`C-85`'s breadth**: the file prefix only, or the identifiers carrying it
   (`snake_config_fixture`, fixture and variable names across 33 test modules).
   Grep first, triage second — not every occurrence of the string is a
   filename.
3. **`C-37` must fail closed** (E5), and the design should say how it asserts
   its own ground truth.
4. **The baseline's provenance question** (E4 / gate check) — resolve before
   criterion 5 depends on it.
