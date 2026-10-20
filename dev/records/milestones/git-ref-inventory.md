# Historical Git reference inventory

Retained from the development reference. This is a dated inventory, not an up-to-date list of Git refs.
Use `git tag` / `git branch -a` for the current state and the current Git conventions for policy.

## Durable branches

| Branch                           | Role                                                                                       |
| -------------------------------- | ------------------------------------------------------------------------------------------ |
| `main`                           | Moving trunk and GitHub default. All milestones merge here. The only branch that is pushed routinely. |
| `upstream-deltares`              | Frozen upstream Deltares state at fork-renaming time. **Never commit to it.**              |
| `base/v0.1.0-alpha`              | Frozen historical starting point of the fork.                                              |
| `milestone/01-replication`       | Sealed Phase 1 milestone (kept alive for late patches / PR prep).                          |
| `milestone/02-pixi-installation` | Sealed Phase 1 milestone.                                                                  |
| `milestone/02b-library-upgrades` | Sealed Phase 1 milestone.                                                                  |
| `milestone/02c-tests`            | Sealed Phase 1 milestone (local tip carries a late followups patch).                       |
| `milestone/r01-contracts`        | **Sealed** 2026-07-18 (tag `r01-contracts`) — R1 config-contract migration; merged to `main` 2026-07-18. Kept alive as a durable phase marker. |
| `milestone/r02-naming`           | **Sealed** 2026-07-19 (tag `r02-naming`) — R2 naming style guide; merged to `main` 2026-07-19. Kept alive as a durable phase marker. |
| `milestone/r03-model-builder`    | **Sealed** 2026-07-19 (tag `r03-model-builder`) — R3 workflow-1 cleanup; behavior-preserving (14/14). Merged to `main` 2026-07-19. Kept alive as a durable phase marker. |
| `milestone/r04-projections`      | **Sealed** 2026-07-20 (tag `r04-projections`) — R4 workflow-2 cleanup. Merged to `main`. Kept alive as a durable phase marker. |
| `milestone/r05-experiment`       | **Sealed** 2026-07-20 (tag `r05-experiment`) — R5 workflow-3 + weathergen cleanup. Merged to `main`. Kept alive as a durable phase marker. |
| `milestone/r06-refactor`         | **Sealed** 2026-07-23 (tag `r06-refactor`) — R6 structural refactor; behavior-preserving. Merged to `main`. Kept alive as a durable phase marker. |
| `milestone/p31-experiments`      | **Sealed** 2026-07-24 (tag `p31-experiments`) — P3-1 project/experiment structure. Merged to `main`. Kept alive as a durable phase marker. |
| `milestone/p32a-climate-analysis` | **Sealed** 2026-07-24 (tag `p32a-climate-analysis`) — P3-2a model-independent climate analysis. Merged to `main`. Kept alive as a durable phase marker. |
| `milestone/p32b-interchange-contracts` | **Sealed** 2026-07-24 (tag `p32b-interchange-contracts`) — P3-2b model-swap interchange contracts. Merged to `main`. Kept alive as a durable phase marker. |
| `milestone/p33-performance`      | **Sealed** 2026-07-25 (tag `p33-performance`) — P3-3 performance passes. Merged to `main`. Kept alive as a durable phase marker. |
| `milestone/r07-layout`           | **Sealed** 2026-07-29 (tag `r07-layout`) — R7 project layout; behaviour-preserving. Merged to `main`. Kept alive as a durable phase marker. |
| `milestone/r08-wf2-projections`  | **Sealed** 2026-07-31 (tag `r08-wf2-projections`) — R8 WF2 v2.0 GCM projections analysis. Merged to `main`. Kept alive as a durable phase marker. |
| `milestone/r09-project-tree`     | **Sealed** 2026-08-07 (tag `r09-project-tree`) — R9 project-tree migration; all five phases, landing gate nine of nine. Merged to `main`. Kept alive as a durable phase marker. |
| `milestone/r10-rule-naming`      | **Sealed** 2026-08-07 (tag `r10-rule-naming`) — R10 rule identifiers. Cut **retroactively** at `7164d83`, R10's completion point: the work ran on `fix/r09-followups` because it began as R9 followups and grew into the milestone, so this branch records where R10 finished rather than how it got there. Kept alive as a durable phase marker. |
| `milestone/r11-wf3-artifacts`    | **Sealed** 2026-08-08 (tag `r11-wf3-artifacts`) — R11 WF3 result tables and run identification. Cut at `94c5bea`, main's tip: P1 and P2 landed through task branches and P3 ran in the primary checkout (the run and the single baseline re-record require it), so like `r10` this branch records where the milestone finished rather than how it got there. Kept alive as a durable phase marker. |
| `origin/fao` (remote-only)       | Inherited upstream project branch (FAO / DCRM work, ~32 commits off-trunk). Not tracked locally; review before ever deleting. |

## Tags

Tags are permanent rollback points; they never move.

| Tag               | Date       | Meaning                                                                          |
| ----------------- | ---------- | -------------------------------------------------------------------------------- |
| `v0.1.0-alpha`    | 2024-09-26 | Upstream release state at the fork point (same commit as `base/v0.1.0-alpha`).    |
| `m01-replication` | 2026-05-07 | Phase 1 seal: replication baseline + fingerprint manifest.                        |
| `m02-pixi`        | 2026-05-07 | Phase 1 seal: pixi env + install.                                                 |
| `m02b-upgrades`   | 2026-05-08 | Phase 1 seal: hydromt/wflow/Python-stack library upgrades.                        |
| `v0.2.0-alpha`    | 2026-05-09 | Release: foundation phase sealed, Phase 2 designed.                               |
| `m02c-tests`      | 2026-07-17 | Phase 1 seal: unit-test coverage for 4 `src/` modules.                            |
| `pre-r01`         | 2026-07-18 | Checkpoint before R1: last flat-config-schema commit; green suite (47/3/2); all three workflow smoke tests verified. |
| `r01-contracts`   | 2026-07-18 | Phase 2 seal: sectioned config schema (project/shared/workflows); suite 51/3/2. Sealed on invariance-by-construction — M2b baseline left untouched (stale; see `dev/records/milestones/r01/baseline_diffs.md`). |
| `r02-naming`      | 2026-07-19 | Phase 2 seal: naming style guide (`dev/reference/naming.md`). Docs-only; existing names grandfathered; suite 51/3/2. |
| `r03-model-builder` | 2026-07-19 | Phase 2 seal: workflow-1 (model builder) cleanup — shared `snake_utils` (`get_config`/`tee_to_log`), per-rule log/benchmark, `outlet_index.csv`, gauges hardening, structured waterbodies sentinel. Behavior-preserving (14/14); suite 73/3/2. |
| `r04-projections` | 2026-07-20 | Phase 2 seal: workflow-2 (climate projections) cleanup, inheriting the R3 patterns. Contract doc `dev/records/milestones/r04/climate_projections.md`; 11 commits. |
| `r05-experiment`  | 2026-07-20 | Phase 2 seal: workflow-3 (climate experiment) + the R weathergen layer cleaned up, inheriting the R3/R4 patterns. Contract doc `dev/records/milestones/r05/climate_experiment.md`; 12 commits. |
| `r06-refactor`    | 2026-07-23 | Phase 2 seal: structural refactor — `src/` → `blueearth_cst/` package, `config/` three-bin split, runners → `scripts/`, `enabled:`-aware wrapper, `MIGRATION.md` (51 renames). Behavior-preserving (run-relative baseline + full-tree semantic diff clean). |
| `p31-experiments` | 2026-07-24 | Phase 3 seal: project/experiment structure. |
| `p32a-climate-analysis` | 2026-07-24 | Phase 3 seal: model-independent climate analysis. |
| `p32b-interchange-contracts` | 2026-07-24 | Phase 3 seal: model-swap interchange contracts. |
| `p33-performance` | 2026-07-25 | Phase 3 seal: performance passes; user-signed milestone gate. |
| `r07-layout`      | 2026-07-29 | Phase 4 seal: project layout — single climate store with a model-free shared producer, engine subtrees under `project_dir`, config split four ways, project-level `plots/` and `data/` retired. Behaviour-preserving (full-tree semantic diff clean, discharge bit-identical). |
| `r08-wf2-projections` | 2026-07-31 | Phase 5 seal: WF2 v2.0 GCM projections analysis; all seven §8 migration steps implemented. User migration note in `dev/records/milestones/r08/migration-wf2.md`. |
| `r09-project-tree` | 2026-08-07 | Phase 6 seal: generated project tree — six semantic roots, fan-out members keyed by filename, result tables renamed, pointer-derived model fingerprint with a drift guard, experiment freezing. Landing gate nine of nine; closing record `dev/records/milestones/r09/closing-record.md`. Work completed 2026-08-05; sealed two days later, which is why the seal is now a named step in the roadmap's cross-cutting principles. |
| `r10-rule-naming` | 2026-08-07 | Phase 7 seal: rule identifiers on one `<verb>_<noun>` scheme — twelve renames, `W.NN` renumbered to follow the DAG, `LOG_RULES` made a conformance test, and ADR 0003 §8–12's spatial-units split. Gates: suite 1526 from the primary, a full three-workflow run, `check_baseline` 8/8 after it, `tree-check` 186/0. Script modules deliberately not renamed. |
| `r11-wf3-artifacts` | 2026-08-08 | Phase 8 seal (R11 of R11–R12): WF3 result tables wide→long with one table per output variable, `cst_`→`st_` member identification with zero-padded ids, the stress-test design table and `st_id`, and `aggregate_rlz` retired as a hard error. Gates: suite 1707 from the primary, a full three-workflow run, exactly one baseline re-record with `check` green after it, `tree-check` 221/0. **The run found three defects nothing else could** — two indicators silently absent, a design table recording perturbations never applied, and a test that had asserted nothing since R9; see `dev/records/milestones/r11/phase-3-run-report.md`. |
| `archive/outputs-figures` | 2026-07-26 | Archive of `feat/outputs-figures` before deletion. Superseded by `refactor/plot-map-params` for the `plot_map.py` redesign: both were cut from `75eb4d6` and rewrote the same module independently, so they are alternatives, not composable. Preserved rather than merged because it also carries a `dev/baseline/manifest.json` predating the `ea5ac59` re-record, and merging would silently revert the baseline. |
| `archive/wf3-experiment-v2` | 2026-08-19 | Retired design branch; history at `531bcc6`. |
| `archive/wf3-stress-test-lookup` | 2026-08-19 | The `wf3-stress-test-lookup` design run (2026-08-15), 11,332 lines of scratch at `741e24d` — `design-v1..v4.md`, the three internal-review lenses, two external rounds, `ledger.md`, `review-brief.md`, `observations.md` and `status.md`. Accepted at G2; the durable outputs are `dev/records/milestones/r12/stress-test-lookup-{design,intake,review-record,task-brief}.md`, and the scratch is drained in this tag's child commit. Cut for the same reason as `archive/wf3-experiment-v2` above: a design run's per-round history should be citable by NAME, not by a sha someone has to dig for. |

The retired `docs/wf3-redesign` branch is preserved by `archive/wf3-experiment-v2`. G2 accepted its
design as architectural input; R12's stress-test lookup was implemented. The durable record is
`dev/records/milestones/r12/wf3-experiment-v2-design-review-record.md`; cite the tag for its history.

`r05-experiment`, `p31-experiments`, `p32a-climate-analysis`, and
`p32b-interchange-contracts` are **lightweight** tags; every other tag above is
annotated and carries a message.
