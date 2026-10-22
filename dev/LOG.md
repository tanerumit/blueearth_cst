# LOG

Closure ledger. One row per board item closed since the board was adopted
(2026-08-07). Earlier work is recoverable from the pre-board record at commit
`45e3a564`; this file is deliberately not backfilled with IDs the board never
issued.

Historical path citations are resolved by the
[reference transition map](records/migrations/dev-reference-transition-2026-10-20.md)
and its linked review-retirement and decision-history maps.

> **A row is at most three short sentences in plain language: what closed, why,
> and where anything durable now lives.** A finding worth keeping —
> a measurement, an owner ruling, a defect class, a tolerance — goes to its own
> home first (a `reference/` doc, a test, an ADR, a board note) and the row
> points there. The row is the index, not the storage; full rule and the
> retrofit procedure in `README.md` § The cap on `LOG.md` rows.
>
> Rows written before 2026-08-19 predate the cap and are shortened one at a
> time, only after grepping that the detail being dropped survives elsewhere.

| Closed | ID | Item | Area |
| ------ | -- | ---- | ---- |
| 2026-10-22 | t2609161642 | Scope R15: run workflows as one DAG [dropped] | workflows |
| 2026-10-22 | t2608181139 | Add forcing-selection evaluation to WF0 [dropped] | wf0  |
| 2026-10-22 | t2608210010 | Use official Deltares colours on docs site [dropped] | docs |
| 2026-10-22 | t2608222239 | Support more historical climate datasets [dropped] | climate |
| 2026-10-22 | t2608202351 | Publish the technical note as site chapters [dropped] | docs |
| 2026-10-22 | t2610062309 | Snakemake scheduler stalls mid-run on long WF2 fetch batches [dropped] | wf2  |
| 2026-10-22 | t2609171500 | Move frozen simulation documents into _engine [dropped] | layout |
| 2026-10-22 | t2608202148 | WF2 behaviour has no current documentation [dropped] | wf2  |
| 2026-10-22 | t2609162115 | weathergenr prints a raw glue expression [dropped] | upstream |
| 2026-10-15 | t2610121419 | Add local-input E2E tests for all five workflows | validation |
| 2026-10-15 | t2610032349 | Number experiments and add a new-experiment flag | wf4  |
| 2026-10-15 | t2610151519 | Simplify obsolete config migration diagnostics | config |
| 2026-10-10 | t2610101521 | Drop the active output folder convention | config |
| 2026-10-09 | t2610091518 | Review and migrate legacy development files | maintenance |
| 2026-10-09 | t2610091206 | Harden worktree coordination | dev  |
| 2026-10-08 | t2610070255 | WF2 monthly change factors ignore the configured water year | wf2  |
| 2026-10-07 | t2610071652 | WF2 suite landed (`3be724c5`); [records](records/reviews/wf2-suite-integration/README.md) | methods |
| 2026-10-07 | t2608071222 | R code has no tests | testing |
| 2026-10-06 | t2610061951 | Port the wf0-lab spatial map revisions to WF1 | wf1  |
| 2026-10-05 | t2610041227 | Trim the test suite by cost and lasting value | testing |
| 2026-10-05 | t2610042152 | Make a copied project tree reusable in another worktree | testing |
| 2026-10-03 | t2610011613 | Adopt a manual toolbox versioning policy | tooling |
| 2026-09-28 | t2608122022 | Verified October water years against rapid CMIP6 data: 14 complete years and changed annual factors in both models. The project sweep was descoped; results and limits are in `dev/reference/workflows/water-year-october-verification.md`. | wf2 projections / config |
| 2026-09-27 | t2608091006 | Standardize plotting across the toolbox with shared templates, then sweep the existing figures onto them | plotting |
| 2026-09-27 | t2608161450 | Verified CHIRPS daily values and corrected their precipitation label without scaling. WF0 reports WG-1 diffs and reads provenance from the store; evidence and limits are in `dev/reference/contracts/weather-generator-seam.md`. | wf0 / climate store |
| 2026-09-27 | t2609062317 | The shell-write scope backstop is inert in advisory mode — The advisory-mode scope limitation and revisit trigger remain in `dev/reference/task-lanes.md`. | tooling |
| 2026-09-27 | t2608202331 | Historical slow-import measurements; scanner attribution was inferred — Timings and uncertainty remain in `docs/env_setup_notes.md`. | environment / dev machine |
| 2026-09-27 | t2608121104 | pixi install reports success without repairing a missing console script — Diagnosis and PowerShell repair steps remain in `docs/env_setup_notes.md`. | environment |
| 2026-09-27 | t2608071229 | hydromt's `to_yml` silently strips `driver.options.preprocess` on a catalog round-trip — The serialization workaround remains pinned by `tests/test_prepare_climate_data_catalog.py` and `tests/test_fetch_gcm_raw.py`. | upstream / hydromt |
| 2026-09-27 | t2608071228 | dask cannot be stubbed at module level, because pandas imports it lazily and reads `dask.__spec__` — The `dask.__spec__` constraint and no-stub guidance remain in `dev/reference/validation-ladder.md`. | tests |
| 2026-09-27 | t2608071227 | The first test file to call `sys.modules.setdefault` decides the stub for every later file — Collection-order stub risks and fixture guidance remain in `dev/reference/validation-ladder.md` and `tests/test_extract_historical_climate.py`. | tests |
| 2026-09-27 | t2608071220 | A comment-only edit to a shared-rule script invalidates up to three whole workflows — The measured 42-job rerun remains in `dev/decisions/0005-adopt-ruff-format-in-two-stages.md`. | rerun triggers |
| 2026-09-27 | t2609041718 | WF1 writes the model three times, and the split is worth keeping — The cost measurement and keep-split ruling remain in `dev/reference/workflows/model_creation.md`. | wf1 / model build |
| 2026-09-27 | t2608071214 | Measure the hydrography read cost §8 adds to WF2 — The 384-cell measurement and scale limitation remain in `dev/decisions/0003-one-shared-region-artifact.md`. | spatial rules |
| 2026-09-27 | t2608171130 | Hoist the categorical palette out of compare_sources when a second caller appears — The one-caller category palette and hoist trigger remain in `compare_sources.py`. | wf0 / figures |
| 2026-09-27 | t2608132310 | Fold Julia box-drawing blocks into the tee's log grammar [dropped] | logging / console |
| 2026-09-27 | t2609171637a | The console's module column is unpadded, so the message column drifts [dropped] | console |
| 2026-09-27 | t2609171637b | Four non-console modules still hedge their plurals [dropped] | wording |
| 2026-09-27 | t2608200008 | Retrofit the remaining over-cap LOG.md rows, opportunistically [dropped] | dev records / ledger |
| 2026-09-27 | t2608242212 | Give the analysis variable set a config surface (R14 C-48) [dropped] | wf0 / wf1 climate figures |
| 2026-09-27 | t2609242252 | Refresh stale rule numbers in the five code-inventoried modules at the next identity change | workflows |
| 2026-09-27 | t2609152104 | Separate engine bookkeeping from user-facing artifacts in the project tree | project-tree |
| 2026-09-26 | t2609151346 | Qualify the isolated Linux environment and execute source-qualified GF15 parity. WSL2, the D7 wheel/source pins, fixed-tolerance controls and independent adapter-parity review passed; evidence is in `dev/milestones/r12/implementation/evidence/gf15-production-integration/linux-qualification/`. This does not establish a full Linux workflow run or method adequacy. | wf3 / platform |
| 2026-09-26 | t2608071208 | Diagnose the staging-harness stall that hangs tests/test_stage_data_incremental.py [dropped]. Owner closed the remaining investigation because the intermittent stall cannot be reproduced on demand; the local serialization fix and regression test remain. | test hygiene |
| 2026-09-25 | t2608151154 | st_0 is not method-comparable with the stress-test surface | wf3 / scenarios |
| 2026-09-25 | t2609171730 | 34 exception messages carry characters a cp1252 console cannot encode [dropped] | console / errors |
| 2026-09-25 | t2609172119 | Snakemake's error block keeps full-length paths that every other console row shortens | console / path tokens |
| 2026-09-25 | t2609070015 | Widen C-37 to the shipped seeds, and ask its mirror question | config / gates |
| 2026-09-25 | t2608112051 | WF2 can serve change factors computed for a window the config no longer asks for | wf2 projections |
| 2026-09-25 | t2608222155 | Slim the baseline run so gate re-records cost less | baseline / run cost |
| 2026-09-25 | t2608131304 | Implement the config-snapshot redesign — current-only run record replaces the write-only bundle | config / provenance |
| 2026-09-25 | t2608202308 | Two Snakemake-running test files carry no tier marker | testing / tiering |
| 2026-09-25 | t2608131718 | The baseline's two flat config copies are stale since 2026-08-12 [superseded] | baseline / test fixtures |
| 2026-09-25 | t2609241852a | WF4 runs write no per-run warm state: intended? | wf4  |
| 2026-09-25 | t2609181501 | Settle wf0 climate extraction's memory growth, then take the remaining transfer levers | wf0 climate extraction |
| 2026-09-25 | t2608071230 | Outlet stations are named by subcatchment ID, which is not a human-readable station name | naming |
| 2026-09-25 | t2609251515 | One location id space across all results (wflow_id) | results / locations |
| 2026-09-25 | t2609251254 | Make the heartbeat first-notice test deterministic | tests / flake |
| 2026-09-25 | t2608071218 | Make a code change to wf2's rule 2.04 actually re-trigger it | wf2  |
| 2026-09-25 | t2609251004 | WF3 scenario identity moves with unrelated code | wf3 / scenario identity |
| 2026-09-25 | t2608301524 | A CRLF checkout of pixi.lock re-keys every CMIP6 series | projections / series identity |
| 2026-09-25 | t2609242342 | Choose the WF4 batch count from a makespan model of run length and resources | wf4 batching |
| 2026-09-25 | t2609151118 | Locations 101 and 1010 are the same series in the P3 basin configuration | wf3  |
| 2026-09-25 | t2609151037 | export_wflow_results carries a second, unreachable return-level estimator | wf3  |
| 2026-09-25 | t2609171637 | Two interchange contract tests are not guarded against a pre-R14 fixture | tests / fixtures |
| 2026-09-25 | t2609241852 | HM-7 validator has no metric-set/2 version | tests |
| 2026-09-25 | t2609161500 | The julia_threads refusal names a key a project cannot set | config / error messages |
| 2026-09-24 | t2608071217 | One failing member re-runs its whole WF4 Wflow batch | wf4 batching |
| 2026-09-24 | t2609241942 | Rename WF4 rules to domain names, hide targets, renumber 4.01-4.10 | wf4  |
| 2026-09-24 | t2609241947 | Rename and renumber WF0-WF3 rules to domain names (screening 2026-09-24) | workflows |
| 2026-09-24 | t2608220915 | Rule 1.06 consumes river_attributes without declaring it, so nothing schedules 1.03 | wf1 / DAG |
| 2026-09-24 | t2609241822 | Interchange integration tests read the pre-successor WF4 layout | tests |
| 2026-09-24 | t2609241523 | test-full: 18 failures and 23 errors from launch guards in pre-launcher contract tests | tests |
| 2026-09-24 | t2608071213 | Define one label constant per rule, so a rename is a one-line edit | rule identifiers |
| 2026-09-24 | t2608241413 | The generated series is anchored to a hardcoded 2010 | wf3 / weather generator |
| 2026-09-24 | t2609241506 | Scenario collection identity changes on every re-extraction of the historical climate | wf3  |
| 2026-09-24 | t2608071224 | The per-cst persistence item below may already be answered by R9's CR-7 / F18 [superseded] | wf3  |
| 2026-09-24 | t2609191457 | Make WF3 planning static before Snakemake | wf3 scenarios |
| 2026-09-24 | t2609171940 | rule-index.md's WF3 section is wholly pre-R12, and AGENTS.md sends rule authors to it | docs / rule reference |
| 2026-09-24 | t2609241329 | Show WF3 pre-DAG steps 3.04-3.06 in the rule overview and correct rule-index.md | wf3  |
| 2026-09-24 | t2609241251 | Rename WF3 generation rules 3.03 and 3.07-3.10 to domain names | wf3  |
| 2026-09-24 | t2609241323 | Drop the WF3 retain copy step (3.09): write scenario series directly to the kept location | wf3  |
| 2026-09-17 | t2609151800a | Module deleted with `t2608290250`, on this watch-item's own trigger. | experiment / dead code |