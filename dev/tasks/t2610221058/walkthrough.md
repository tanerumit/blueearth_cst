# Ntoum WF2 export/import walkthrough (2026-10-22)

Toolbox: `feat/central-config` at `434b0ccb` (import) with export `6d5220e3`. Source:
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

Real launcher sequence (run, immediate rerun, `--forcerun plot_climate_projections`) on the rapid tree
was attempted 2026-10-22 and stopped after rule 2.01 stalled 29 min reading the P-drive basin index;
no production record was written (hard kill). Script: session-1 `.tmp/tasks/t2610221058/real/sequence.ps1`.
