# Test-suite trimming — preliminary assessment (2026-10-04)

Scope: `tests/` against three retirement criteria — (1) would not catch a real
bug the end-to-end layer misses, (2) written for one-time use, (3) expensive to
run. Preliminary: no code was changed.

Builds on the 2026-08-11 bloat assessment (deleted from `dev/reviews/` in
`c7992c6f`; read it with `git show c7992c6f^:dev/reviews/2026-08-11_test-suite-bloat-assessment.md`).
Its main cut, the R07/R09 project-tree path maps, is already executed.

## Evidence

One serial `pytest tests/ --durations=0 --junitxml` run in the session-2
worktree with `test_case/` fixtures present, plus collection counts, a
test-to-test import map and an AST body-hash duplicate scan. Result: 4,203
passed, 11 skipped, 1 xfailed, 1 failed. A concurrent pytest session in another
repository ran alongside, so per-item cost was roughly 1.8× August's; read the
figures below as shares and ranks, not durations.

| | 2026-08-11 | 2026-10-04 |
|---|---:|---:|
| Collected items | 2,037 | 4,216 |
| Test files | 114 | 195 |
| Test lines | 27k | 59k |

- **Duplication is still near zero.** Exact body matches are parametrize-style
  twins within one file; the v1/v2 file pairs share at most two near-duplicate
  bodies.
- **Cost is concentrated.** The 107 `workflow_contract` / `process_isolation`
  items are 2.5% of items and about 48% of summed runtime. The two
  `test_climate_store_freshness` tests alone are about 15%.
  `test_metric_plan`, `test_p2_current_carrier` and `test_climate_figures`
  take about 42% of the cheap tier.
- **Which gate a saving moves.** `test-fast` runs `-n auto --dist loadfile`, so
  its wall time is bounded below by the slowest single file: only the top
  cheap-tier files move it. CI and `test-full` run serially, so their savings
  add. `test-contract` is serial too.

## Prerequisite: what "end-to-end" means here

The three `--run-integration` tests (`test_workflow_build_model`,
`test_workflow_analyze_projections`, `test_workflow_run_stress_test`) are opt-in,
cannot run in CI, and one carried a stale assertion for weeks unnoticed.
`analyze_climate` has none. The end-to-end layer that actually runs is the
CI-run `workflow_contract` tier, `test_cli.py` dry-runs, and occasional real runs
plus `check_baseline.py`. Judge criterion 1 against that layer; any retirement
that leans on the integration tests needs a scheduled integration run first.

## Tier 1 — retire (one-off or never runs)

1. `test_r12_wf3_feasibility.py` — 29 items, about 16% of the expensive tier.
   Exercises prototype Snakefiles under `dev/records/milestones/r12/`
   (sealed; tag `r12-wf3-execution`); its docstring says it does not validate
   production WF3. Exception: production uses checkpoints
   (`snapshot_simulation_inputs`, `prepare_indicator_plan`), and
   `test_p2_current_carrier` stubs `run_project_child`, so nothing else
   dry-runs checkpoint reuse. Port the two
   `test_checkpoint_fresh_reuse_and_refusal` cases to the production
   Snakefiles, then retire the other 27.
2. Never-running skips: `test_interchange_contracts::test_hm6b_integration`
   (unconditional "retired" skip); two `test_wflow_log_attribution` tests that
   need an R09 run directory that no longer exists.

## Tier 2 — retire the v1 path, code and tests together

Conditional on a dead-code pass. Likely unreachable from Snakefiles,
`script:` targets and `scripts/`:

- `blueearth_cst/experiment/legacy_generation_plan.py` — no importer; named only
  in the `IDENTITY_COMPARISONS` allowlist in `shared/config_composition.py`.
- `blueearth_cst/experiment/legacy_scenario_provider.py` — imported only by the
  above and by tests.
- v1 writers `freeze_simulation`, `complete_simulation`,
  `publish_response_inventory` — production writes only v2
  (`experiment/rules/simulate_and_metrics.smk`).

Still live, so NOT retirable here: v1 `read_response_inventory` (called by
`metric_plan.py`, including an unconditional call in `_read_metric_set`), and
the `legacy_wf4_interim` / `_capture_legacy_wf3_attempt` paths in
`scripts/run_workflows.py`, which are labels on code that still runs.

Order matters. `test_metric_plan`, `test_p2_current_carrier`,
`test_response_inventory_v2`, `test_collection_resolution` and
`test_collection_preparation` import fixtures from `test_scenario_collection`,
`test_simulation_record`, `test_response_inventory` and
`test_wflow_response_reader`. First move the shared fixtures into one module
built on v2 producers — which is also where module-scoped fixtures cut the
`test-fast` floor — then retire the v1 code and its tests, including the
unmarked 45 s-class `test_collection_preparation::test_planned_publication_across_separate_workers`.

## Tier 3 — owner rulings

1. `test_v1_v2_equivalence.py` (6 tests + `tests/data/v1_split/`). After the
   migration it compares frozen v1 copies against today's composed shipped
   configs via the mapping; only a deliberate config edit can fail it, and it
   was re-edited three times after 2026-08-28 for exactly that. Loss: its
   docstring calls it the only numerical check on rapid, baseline_linux and
   wf2_fast. Recommendation: retire.
2. R14 sweep tests (`identity_rename`, `stale_spelling`, `unread_config_key`;
   about 50 cheap items). Recommendation: keep `unread_config_key` (a key with
   no reader is a real bug class end-to-end runs miss); retire the other two —
   one pins specimens from a single rename campaign, the other calls itself "a
   measurement until P4" and the loader already refuses retired spellings at
   parse time.
3. Migrator tests (`test_migrate_project_config`, `test_migration_mapping`; 74
   items). Keep while `scripts/migrate_project_config.py` ships (README,
   CHANGELOG, `docs/site/guide/migrating-project-config.qmd`); choose the
   release that retires migrator and tests together.
4. `test_gridded_outputs_removed` — August's watch-item; decide whether the
   removed `save_grids` key can still plausibly appear in a user config.

### Rulings (owner, 2026-10-04)

| Item | Ruling |
|---|---|
| 1. `test_v1_v2_equivalence.py` + `tests/data/v1_split/` | Retire. |
| 2. R14 sweeps | Keep `test_unread_config_key_sweep` (+ `test_sweep_common`); retire `test_identity_rename_sweep` and `test_stale_spelling_sweep` with their `dev/scripts/` tools. |
| 3. Migrator | Retire in this trim — against the keep-for-now recommendation. |
| 4. `test_gridded_outputs_removed` | Retire now, with its refusal code path. |

Consequences of rulings 3 and 4 that the implementation must carry:

- Removing `scripts/migrate_project_config.py` removes a shipped, documented
  CLI, so classify the release per `dev/reference/versioning.md` and add a
  CHANGELOG entry pointing v1 users at `v0.3.0` to migrate.
- Retire with it: `config/migrations/v1_to_v2.yml`, `test_migrate_project_config`,
  `test_migration_mapping`, `docs/site/guide/migrating-project-config.qmd`
  (and its README / CHANGELOG / site links), and the `ruamel.yaml` dependency
  that `pixi.toml` marks as migrator-only — regenerate `pixi.lock` with pixi,
  never by hand.
- Repoint the refusal messages that name the migrator
  (`scripts/run_workflows.py`, `blueearth_cst/experiment/simulation_runner.py`,
  `blueearth_cst/shared/config_composition.py`) to the `v0.3.0` route.
- Ruling 4: remove `blueearth_cst/projections/gridded_outputs.py` and its call
  in `analyze_projections.smk`; a `save_grids` / `save_gridded` key then falls
  to the generic unknown-key handling — confirm that path refuses or warns
  rather than silently ignoring it.
- Grep each retired spelling repo-wide and fix live references in the same
  commit (AGENTS.md convention); `dev/records/` stays unedited.

### Ruling on v1 records (owner, 2026-10-04)

**Retire v1 scenario-collection, simulation-record and response-inventory
support, code and tests together.** Evidence: v1 records were introduced on
2026-09-11 and superseded by v2 on 2026-09-22; `v0.2.0-alpha` predates both and
`v0.3.0` writes only v2 (`freeze_simulation_v2`, `publish_response_inventory_v2`,
`publish_simulation_v2`, `read_collection_v2`). Only pre-release experiments
from that window are affected. The coverage was inverted: `metric_plan`'s
expensive in-process tests all build a v1 experiment, while its production v2
branch was tested only through stubbed v2 readers.

**Fingerprint ruling (owner, 2026-10-04): edit `metric_plan.py` and re-record.**
`metric_plan.py` is code-inventoried into every metric request, so removing
its v1 branches mints new metric-set ids for every experiment (old sets stay
readable; a metrics-only re-run publishes a new set). Re-record the baseline
from a metrics-only run on `test_local` (values must be identical; only the
set id moves) and note the id change in the CHANGELOG.

**Identity scope, measured and ruled (owner, 2026-10-04): accept all moves.**
`repository_code_inventory` follows static imports, so the shared-module edits
moved the WF3 collection and WF4 simulation identities as well as the metric
set; only the climate store is unchanged. Existing collections and experiments
stay readable but are not reused: WF3 regenerates, and re-simulating an
existing experiment needs a new name. The standing baseline needs a full
WF3+WF4 re-run and re-record.

Sequence: (1) a real retained-v2-experiment fixture plus v2 end-to-end metric
tests; (2) port the `metric_plan`, carrier and R12 checkpoint tests onto it;
(3) remove the v1 branches and modules with their tests. Open a PR for the
batch, since it reaches `metric_plan` and `collection_resolution`.

## Tier 4 — cut runtime without deleting coverage

1. `test_climate_store_freshness` (about 15% of total) guards cross-workflow
   re-extraction oscillation, which a real run would only redo silently. Keep;
   run it at landing or nightly, or share one staged store and run fewer
   dry-runs per assertion.
2. Module-scoped fixtures in `test_metric_plan` and `test_p2_current_carrier`
   — the 16 carrier cases rebuild the same synthetic project with the launch
   stubbed.
3. `test_climate_figures` — three tests dominate; use smaller data or lower
   resolution, keep naming and contract assertions.
4. Settle the open marker question in `pyproject.toml`: `slow` versus the
   `workflow_contract` / `process_isolation` tiers as the deselect scheme.
   About 50 unmarked cheap-tier tests take 2 s or more.
5. Investigate unexpected unit-test costs: `test_stage_cmip6` worker pool,
   `test_fetch_gcm_raw::test_from_dict_honours_the_override_and_still_expands_the_member`.

## Tier 5 — keep

- Console-format tests (about 104 in `test_snake_utils`, plus `test_progress`,
  `test_plan_block`): end-to-end runs never assert console text, they cost a
  few percent of the cheap tier, and AGENTS.md treats console rows as a
  contract (`log_row`'s conventions). Trimming them is an owner question about
  maintenance cost, not a criterion-driven cut.
- `test_plot_map` arithmetic, the parametrized tables
  (`test_script_module_importability`, `test_project_tree_inventory`), the R8
  falsifiers, the `check_baseline` tests, `test_gev_lmoments`, `test_cli`.

## Expected effect

Tiers 1–3 remove about 2–3% of items but about 10% of serial runtime. Tiers 2
and 4 together could take a further quarter or more off serial runtime and
lower the `test-fast` floor.

## Incidental

`test_todoboard_wrapper::test_board_root_is_main_even_when_another_worktree_is_first`
failed on a clean `chore/test-trimming` in the session-2 worktree; it appears to
depend on the worktree path (inferred, not diagnosed).

## Findings from the v1 retirement (2026-10-04)

The v1 metric tests pinned four properties the v2 metric-set code does not
have. They were not ported as tests, because some may be deliberate v2 design;
each needs an owner decision before it becomes either a fix or a recorded
non-goal:

1. `_read_metric_set_v2` does not check table rows against the plan's expected
   result keys, so a table edited together with its manifest digests is read.
2. It does not refuse extra, unlisted tables, and it accepts a renamed engine
   marker file inside the right directory.
3. `_publish_metric_set_v2` does not re-check the live metric environment just
   before writing the marker (v1 did, after flushing payloads).
4. The v2 manifest does not retain the per-unit return-level evidence the v1
   manifest carried; `reduce_metric_plan`'s evidence is discarded.

**Ruled 2026-10-04 (owner).** v2 already validates tables against the
expected keys before writing, and at read time checks every file's SHA-256
and the manifest digest, so accidental corruption is caught. Gaps 1, 2 and 3
add protection only against a consistent forgery, or, for 3, against an
on-disk change after the code that computed the values was loaded:

| Gap | Ruling |
|---|---|
| 1. Row-vs-expected-key check on read | Non-goal: forgery-only. |
| 2a. Extra, unlisted tables accepted | Non-goal: forgery-only. |
| 2b. Renamed engine marker accepted | **Fix**: require `metrics.json`. A one-line check, bundled with 4. |
| 3. No late live-environment re-check | Non-goal: a late on-disk change does not alter loaded code, so it would refuse correct results. |
| 4. Return-level evidence discarded | **Fix**: retain it as a SHA-referenced engine artifact (block counts, fitted GEV parameters, fit and shape coverage, policies), verified on read, and tolerated as absent in sets published before the fix. |

4 and 2b ship as one batch before the next release. `metric_plan.py` is
code-inventoried, so the metric-set id moves once; re-record with a
metrics-only run.

## Outcomes since the v1 retirement (2026-10-04)

- **Tier 3** (landed `70fc6173`): the R14 stale-spelling and identity-rename
  sweeps, the v1 -> v2 equivalence test and the migrator are retired; the
  loader's refusals point at `v0.3.0`. The `save_grids` guard is **kept**,
  reversing that ruling: without it the loader silently accepts
  `save_gridded: true` (verified), so the ruling's precondition failed.
- **Tier 4** (landed `29c1ebcf`): freshness checks merged (142 s -> 100 s),
  the carrier matrix planned once per module (~97 s -> 47 s), the tamper tests
  share one published set (79 s -> 45 s), and the label-only `slow` marker is
  retired in favour of the contract tiers.
- **Integration run** (`1b9389a8`): one end-to-end test of all five workflows
  through `scripts/run_workflows.py` from a fresh root, `pixi run test-e2e`,
  and a ladder row saying when it is owed.
- **Slow unit tests**: both spent ~19 s in gcsfs credential discovery.
  `fetch_gcm_raw.with_read_overrides` now reads the public CMIP6 bucket
  anonymously, which also removes ~19 s per series from every WF2 fetch
  process.
- **Relocation defect** (t2610042152, landed `0bc65957`): a copied tree
  failed reuse at WF3 (the installed generator's absolute `out_dir`) and WF4
  (metric plans' absolute targets). Both checks now accept a root-only
  difference; the metric-set id moved once (`169fc1931781` -> `b7e1afe8dea5`,
  identical tables). Session worktrees were re-seeded by copy on 2026-10-05.
- **Metric-set gaps** (landed `da9f2e82`): return-level evidence is retained
  as `return_level_evidence.json`, and the reader accepts only `metrics.json`
  as the engine marker. Gaps 1-3 stay non-goals per the rulings above.
- **Cleanup** (landed `a2dbd0d7`): `check_baseline.py` reads only the v2
  metric-set layout, and a test that replaced `hydromt` in `sys.modules`
  process-wide no longer leaks into other files under xdist.

Also stale before this work: the source notebook
`docs/notebooks/Climate Stress Test.ipynb` read the v1 experiment layout
(`config/simulation.json`, `scenario_table.csv`, `stress_test_lookup.csv`),
which v0.3.0 already does not write. Ported to the v2 records in `5d7887ba`.

Correction: an earlier draft of this section said `docs/site/guide/outputs.qmd`
and `docs/site/scientific-approach/conventions-and-interpretation.qmd` still
used the metric-set/1 vocabulary. They did not; both already describe
`metric_run_lookup.csv` and `run_group_id`. Only the notebook was stale.
