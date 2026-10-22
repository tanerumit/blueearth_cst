# Ntoum WF2 export/import walkthrough (2026-10-22)

Toolbox: `feat/central-config` at `381b5e39` (import) with export `94887b4d`. Source:
`cst-cases/runs/gabon-ntoum-v2-rapid` (read-only). Isolated destinations under session-1
`.tmp/tasks/t2610221058/wt/`; full console output in `wt/walkthrough.log`.

```console
pixi run python scripts/transfer_results.py export --project-dir C:/Users/taner/workspace/cst-cases/runs/gabon-ntoum-v2-rapid --output .tmp/tasks/t2610221058/wt/ntoum-wf2.zip
pixi run python scripts/transfer_results.py import .tmp/tasks/t2610221058/wt/ntoum-wf2.zip --project-dir .tmp/tasks/t2610221058/wt/a
pixi run python scripts/transfer_results.py import .tmp/tasks/t2610221058/wt/ntoum-wf2.zip --project-dir .tmp/tasks/t2610221058/wt/a
pixi run python scripts/transfer_results.py import .tmp/tasks/t2610221058/wt/ntoum-wf2.zip --project-dir .tmp/tasks/t2610221058/wt/b --config C:/Users/taner/workspace/cst-cases/applications/gabon-ntoum-v2-rapid/project_config.yml
```

| Step | Result |
|---|---|
| Export | 65 members, 5.08 MB; bundle id `2a7bcd03…` (identical to an earlier export: deterministic) |
| Attribution | `legacy-unattributed`: 56 product files, no production record (product predates it) |
| Configuration | One snapshot `34d1af1e…`, bound by both provenance digests |
| Historical paths | Only the snapshot's `run_record.yml` and `project_config.yml` name source paths |
| Import `a` (empty project) | Imported; region `unverified` (no destination region); configuration not compared |
| Import `a` again | `already_imported`, no change |
| Import `b` (Ntoum region copied, Ntoum app config) | Imported; region `verified`; no configuration differences |
| Byte check | Both destinations: 56 product files identical to source (SHA-256) |
| Usability | 17 CSV tables read with pandas (5193 rows); 17 PNG figures verify with Pillow |
| Destination config | No `config/analyze_projections/` created in either destination |
| Source integrity | 0 files under the Ntoum run root newer than the walkthrough start marker |

Source unavailability is exercised by `tests/test_result_import.py::test_round_trip_without_the_source`,
which deletes the source project before importing; the production Ntoum root was not removed.
Not exercised on Ntoum: production-record mode (needs a fresh launcher WF2 run; covered by
`tests/test_product_record.py` and `tests/test_result_bundle.py`).

## Real launcher sequence on the rapid tree

`scripts/run_workflow.py analyze_projections --config test_case/project_config_rapid.yml --project-dir
test_case/test_rapid --cores 2`, evidence in session-1 `.tmp/tasks/t2610221058/real/`. A first attempt
stalled 29 min in rule 2.01 on the P-drive basin index and was killed: no record was written; its stale
worktree-root Snakemake lock (only `test_rapid` paths) was removed before the retry.

| Run | Toolbox | Snakemake | Production record |
|---|---|---|---|
| 1 full | `96dcf2e0` | 13 jobs, exit 0 | `complete`; 48 files credited, logs retained; 8 unattributed |
| 2 plain | `96dcf2e0` | Up to date | Byte-identical: no-op |
| 3 `--forcerun plot_climate_projections` | `96dcf2e0` | 2.06 reran | Unchanged: identical PNGs looked like a no-op (defect) |
| 4 plain | `316252ab` | 2.05 reran | 5 summary/report files credited (4 identical rewrites) |
| 5 `--forcerun plot_climate_projections` | `316252ab` | 2.06 reran | 21 PNGs + 2 figure manifests credited; tables keep producer |
| 6 plain | `316252ab` | Up to date | Byte-identical: no-op |

Run 1's 8 unattributed files exposed the same defect: rule 2.05 rewrote three `summary/` CSVs
identically. Fix `316252ab` adds write-time comparison under the project lock. After it, the 5
unattributed files are the 4 retired `plots/overview/`/`plots/windows/` leftovers and the unchanged
`_engine/stage_b_settings.json`, all correctly uncredited.

Export of the rapid product: `production-record` mode, `complete`, 85 members, 2 configuration snapshots
(generations captured under different toolbox states). Import into an empty root published 66 product
files with region `unverified`.

Commit hashes above are the post-rebase equivalents (2026-10-22 rebase onto `main`); the runs used
the pre-rebase commits with identical tree content for these files.
