# Shared plotting batch landing verification

Task: t2610082103. The owner authorized a local merge to main on 2026-10-10.
No push or release is authorized. The approved local landing is complete.

## Candidate and environment

- Synchronized implementation candidate: `b5ff0b41e890f05c1c71ca0c3965e946ef29e231`.
- Final candidate after verified test/audit fixes: `c567854e9bb3e63a9570a50411b14a539dd049ca`.
- Target before landing: `c9ac28d7b81655a030b897e4c9b30f88ad0da271`.
- Branch: `refactor/t2610082103-shared-plotting`; source session: session-1.
- Windows 11, Pixi default environment, Python 3.12.13.
- Lock SHA256: `797afdad5a8f8c37dd62b2f1e2f88f3fea120c3fc53b7e7c792b860700a6782b`.

The synchronized implementation differs from the previously accepted `99939abf` only in task records.
The follow-up changes affect one model-free DAG fixture and the configuration-reader audit and its test.
They do not alter run-path scientific preparation, rendering, configuration or dependencies.

## Checks

- `pixi run lint`: pass; `pixi run format-check`: pass, 445 files.
- `pixi run pytest tests/test_plot_climate_source.py tests/test_unread_config_key_sweep.py -q`:
  30 passed in 45.61 seconds on the fixes; touched-file Ruff lint/format and `git diff --check` pass.
- First `pixi run test-full`: 4116 passed, 3 failed, 17 skipped, 1 xfailed in 26:03.
  Two local failures were corrected; the model rebuild case failed because P-drive roots disappeared.
- First `pixi run test-e2e`: failed in WF1 reading GlobCover after complete fresh WF0 execution.
  The raster strip returned fewer bytes than expected. The data mount then became unavailable.
- Read-only recovery probe: the restored file is 392327352 bytes; complete rows 31061 and 31062
  read successfully, each with 129600 values. No managed source was altered.
- Final `pixi run test-full`: 4120 passed, 17 skipped, 1 xfailed in 20:03; recorded by
  `verify_landing.py` in software-gates-v2.json. Evidence verification passes and the log has
  exactly one pytest session header.
- Final fresh `pixi run test-e2e`: 1 passed, 4137 deselected, no skips in 51:20; recorded in
  execution-gates-v2.json with all six rapid project/workflow configuration hashes.

The full-suite skips are five Linux-only controls, eleven unavailable local P0/lab comparisons and
the integration test dispatched separately by test-e2e. One strict upstream HydroMT xfail remains.
These are explicit coverage limits; they are not substitutes for the required all-five execution.

## Scientific and visual acceptance

The first fresh WF0 root is
`.tmp/pytest/run-7dcd6ef3955a4ac798895553597914fd/test_all_five_workflows_run_en0/project`.
Exact checks preserve 12 native arrays, 54 CSV tables and 51 temporal PNGs. Four map captions match
their shared reference ID and full frame. The model-validator inspected all four maps and seven
annual/monthly charts; support, completeness, units, periods and legends pass. The remaining 44
temporal images reuse exact-byte evidence. Earlier controlled caption/unavailable-scale cases remain
covered by the accepted map-reference evidence.

The final fresh all-five root is
`.tmp/pytest/run-4bf42bbc57744ddb8ec629e34230630c/test_all_five_workflows_run_en0/project`.
Final-root WF0 exact checks again preserve 12 native arrays, 54 tables and 51 temporal PNGs.
All four maps are byte-identical to the directly inspected first-run maps and all caption prose is
unchanged. Final reference `7863a5e4c8425ab4307e563e919ae11261c6f292077c95fb21ea0b762b74e724`
matches map caption frames and scale objects. Its identity change is confined to the ERA5 extraction
file hash and resulting preparation ID; both scientific field digests and code/catalog/environment
identity components are unchanged. File provenance therefore distinguishes scientifically equal
NetCDF encodings without changing the accepted scientific claim.

Fresh WF1 completed forcing and historical simulation. Its 2010-2016 window matches the retained
capture. Nine scientific arrays, six CSVs and six temporal PNGs are exact. The rebuilt latitude and
GeoTransform differ by at most `7.105427357601002e-15` degrees; only those representation components
are normalized for the array comparison, under an explicit `1e-12` degree guard. This is not full
dataset identity. The model-validator independently classified this difference as scientifically
immaterial (about 8e-10 metres and 8.5e-13 of a grid cell).

Fresh WF1 forcing figures pass. The validator opened 22 WF1 PNGs (nine forcing, five spatial,
eight evaluation) and all 17 WF2 PNGs. Soil-clay title cropping has direct retained-image evidence;
LAI title cropping is observed with unchanged renderer code, but no retained LAI image was found.
These spatial-layout limitations remain open; no new blocking scientific/rendering defect was found.
Seven caption manifests resolve all 93 records to nonempty figures with nonempty captions. The root
contains 129 PNGs; all 36 without caption records are listed in retained figure-inventory.json.
Conditional WF2 absences and inspection limits are explicit in the independent report.
The rapid projection case uses two models and one scenario; dense-ensemble legibility requires the
separately accepted controlled case. WF1 window comparisons must use matched input identities.

Full logs, probe scripts and generated outputs remain under session-1 scratch for landing recovery
and review. No stale baseline check or byte comparison of changed maps is used as acceptance.

## Landing outcome

Both gate records verify without rerunning checks. During execution, main advanced to `aab0a1da`
with 22 board-documentation paths only. Rebase produced `8d53f83b9c47675a3bcc5515d6cfd77df4b9a629`;
all runtime/configuration/test files are unchanged from tested `c567854e`. Exact intervening paths
were supplied to both verifier calls using `--allow-path`; no wildcard allowance was used.

`worktree-session.py task-land refactor/t2610082103-shared-plotting --verify <both evidence checks>`
merged to local main at `761c8e5455148df314bdd1729d7c65bafcc24a06`. Source ancestry and full committed
tree equality pass. The branch is deleted; session-1 is retained, detached and EMPTY. No push, release
or external package publication occurred. Later task-record maintenance is documentation only.

Original implementation and tested commits remain reachable through local internal verification refs:
`refs/verification/t2610082103/implementation-20261010` and
`refs/verification/t2610082103/tested-20261010`. These are evidence pins, not release tags.

See [software gate](landing-software-gates.json), [execution gate](landing-execution-gates.json) and
[independent acceptance](landing-scientific-visual-acceptance.md). The gate records retain log digests,
actual environment and input identities. Logs, probes, complete inventory and generated outputs stay
in session-1 scratch for this task's review and recovery; no run products are committed.


Task-record maintenance: board rendering passed; `todoboard.py check` reports eight pre-existing
structural errors in two other notes and two unrelated folders. None lies in a modified task path.
This plotting note has only a length warning; its linked evidence/history is retained. The full
board-check log remains in landing scratch. No unrelated board content was changed.
