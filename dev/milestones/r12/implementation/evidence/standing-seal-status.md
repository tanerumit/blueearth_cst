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
