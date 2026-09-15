# R12 standing baseline and tree status

Inspected 2026-09-12 at P3 commit `868c4b7c`, while the owner-approved GF15
benchmark proceeds. These are read-only checks of the local standing fixture,
not the fresh P0/P3 scientific reference. No fixture or baseline was changed.

| Command (prefix `pixi run --as-is python`) | Result |
|---|---|
| `dev/scripts/check_baseline.py check` | Exit 1: successor baseline resolver refuses zero retained metric plans. The legacy indicator table is not accepted as a successor baseline. |
| `dev/scripts/check_baseline.py check --workflow build_model --workflow analyze_projections` | Exit 1: two recorded `config/runs/project_config_*.yml` snapshots are missing. The fixture instead carries predecessor `snake_config_*.yml` names. No other target difference was reported in these selected slices. |
| `dev/scripts/snapshot_project_tree.py --config test_case/project_config_baseline.yml --project-dir test_case/test_local` | Exit 1: 280 paths, 205 recognized, 75 unmapped. The complete report identifies predecessor config snapshots and experiment-owned generation/simulation artifacts. |

Complete logs remain in the session scratch directory
`.tmp/scratchpad/2026-09-11_0010/` as `r12-standing-baseline-check.log`,
`r12-standing-baseline-unaffected.log`, and `r12-standing-tree.log`.

The manifest identifies its recording as `feat/r14-p1-loader@9bfdda5c036c`.
This local fixture does not match all recorded snapshot paths and still uses
the predecessor output layout. A self-comparison or path renaming alone would
not establish successor numerical acceptance. The repository also documents
that the standing manifest predates the current nine-year baseline config.

P3's fresh direct and all-runner inventories already passed with zero unmapped
paths, and its signed numerical crosswalks compare against immutable P0 under
matched scientific settings; see [P3 acceptance](p3/acceptance.md). Those results
remain valid, but do not convert the standing checks above into a pass.

Before sealing, establish a dedicated successor baseline from the current
baseline configuration, retain and explain the old-to-new identity/value
comparison, then update the standing references as warranted by that evidence.
Do not overwrite legacy evidence, widen the current inventory to admit retired
paths, or claim milestone sealing from the present fixture. GF15's scientific
result and any required owner method ruling remain separate prerequisites.

## DISCHARGED 2026-09-15

All three checks above now pass. The full record, including why the fixture
could not be repaired in place and what was deliberately not done, is
[successor-baseline-record.md](successor-baseline-record.md).

| Check | 2026-09-12 | 2026-09-15 |
|---|---|---|
| `check_baseline.py check` | exit 1 — "requires exactly one retained metric plan, found 0" | **exit 0 — OK, 7 targets match manifest** |
| `check_baseline.py check --workflow build_model --workflow analyze_projections` | exit 1 — two `project_config_*.yml` snapshots missing | **exit 0 — OK, 5 targets match manifest** |
| `snapshot_project_tree.py` | exit 1 — 280 paths, 75 unmapped | **exit 0 — MAP CLEAN, 326 paths, 0 unmapped** |

**How.** The fixture was not repaired, it was replaced. All 75 unmapped paths
were pre-R12 output, so pruning and map amendment were never available; a fresh
run was the only route. The pipeline was first proved end to end on a separate
root (`test_case/test_successor`) so the shared fixture stayed intact while the
evidence was judged, then `test_case/test_local` was regenerated from the
tracked seed `project_config_baseline.yml` and the manifest re-recorded from it.
**The predecessor tree was moved, not deleted** — 280 files, 82.1 MB, at
`blueearth_cst-artifacts/r12/predecessor-test_local-2026-09-15`.

**Two inventory gaps were found and amended on owner approval**, per the tool's
rule that amending the map is an owner decision:
`metric_sets/{digest}/return_level_benchmark.json`, added to every set by GF15
D5 and never declared, and `data/climate/historical/climate_levels.json`, which
rule 0.04b writes at the historical root above what the existing pattern could
match. Neither was an orphan. The amendment was checked for over-reach: the
predecessor tree still reports its 75 unmapped paths afterwards.

**The manifest now records the successor layout.** `recorded_by` moves from
`feat/r14-p1-loader@9bfdda5c` to `feat/wp3-improvements`, and its seven targets
include `experiments/experiment/config/simulation.json`, the R12 metric set
`a50d1a4f…` and the two `config/runs/project_config_*.yml` snapshots that
replaced the predecessor `snake_config_*.yml` pair. A new indicator reference
sidecar `indicator_ref/5ab0f374553a5aff.csv` was written; the predecessor's
`74ed83c06b2e7e6c.csv` is now tracked but unreferenced, left in place rather
than removed because `check_baseline.py:1176` cites it by name.

**Consequence for other branches, stated rather than discovered.**
`test_case/test_local` is untracked and shared by every worktree, so a branch
whose tracked manifest still describes the predecessor layout will now fail
`check_baseline check` against a successor tree. That is inherent to the
migration, not a defect, and the preserved predecessor tree is the recovery
path.

**Still separate, and not implied by any of the above:** the milestone seal, the
§7.5 owner method ruling, actual-bundle applicability, and Linux parity.
