# Legacy development migration: retained evidence context

Subsequent relocation: see [review retirement](review-retirement-2026-10-20.md) for the final homes
of the three historical holds and the active geographic task. Statements below describe the original migration.

Lifecycle: frozen-with-supersession after completion. Owner approved the per-file plan on 2026-10-09.
Migration completed on `chore/maintainance`; landed into `main` on 2026-10-09 following owner approval.
This record grants no landing or push authority.

## Original sources and approval

The migration covers 101 legacy files. The original repository is `blueearth_cst`; source commit
`a9fde6c55927768e370094baa98ae9614d259cd0` is already an ancestor of `main`.
Original parent: `dev`; directory: `working`; tree: `91b9006df3e4cd5c4838465cdd9c1834601657f2`.

[original-context.json](legacy-development-migration-2026-10-09/original-context.json) records all source
blob IDs and SHA256 values, approved destinations, archive comparisons, and exact historical citation
occurrences. Original text and relative directory context remain in that immutable Git tree.
Maintained navigation: `dev/README.md`, with an additional entry in the milestone index.

The approved plan is retained through commit `ebc53054709eaa21965dfb83e9d0852f3ded8c7b`:
original parent `dev/tasks`, identifier `t2610091518`, tree
`be325c9a53281404289ec2849e1bdc9c216ba95e`, relative files `migration.md` and `inventory.json`.
This historical identity is independent of task closure and contains no live task-folder dependency.

```powershell
git show 91b9006df3e4cd5c4838465cdd9c1834601657f2:design-runs/wf3-simulation-identity/status.md
git show be325c9a53281404289ec2849e1bdc9c216ba95e:migration.md
git cat-file blob <source-blob-from-context>
```

## Reading relocated snapshots

Historical reports keep their original Git bytes. Their dates, verdicts, numerical evidence limits,
commands, and relative links describe the original context, not the current checkout.
Resolve an old legacy path using the source entry in the context inventory. Resolve bare filenames
relative to that source's original directory in the pinned tree. Use the full pinned commit for
outside-directory sources. The exact occurrence records bind citations to their intended source blobs,
including the absolute worktree path in GF15's original external-review brief.

The old milestone and decision prefixes in archival counterparts remain historical spelling. Their
path-sweep relationship to the pinned sources is recorded separately; no universal byte equality is
claimed for those copies. No historical G2 identity or review verdict has been fabricated or amended.

If an outside source was already absent at the pin, this migration does not make it recoverable.
Old scratch-output pointers, external case paths, and live data stores have not been recertified.

## Retention and boundaries

The context record is cited by maintained navigation and remains necessary while historical reports
depend on it. Do not prune it as an uncited review. Existing R12 review archives remain unchanged.

The three held files stay unchanged: the sealed parameter-placement source, the R12 stress-axis source,
and the complete-run output schema awaiting reconciliation. Its stale implementation-status statements
are not promoted into current guidance.

Unresolved geographic findings remain visible in the relocated case diagnostic register. Relocation
does not close them or turn synthetic-observation exercises into model validation.

The old WF2 brief's no-title ruling has been superseded by current `dev/reference/plot-style.md` panel
titles and the newer WF2 suite. Preserve that history; do not restore the old visual rule.

## Execution and verification

Applied all 101 approved dispositions: 53 relocations, 45 retirements, and three unchanged holds.
Of the relocations, 50 retain historical evidence, two serve the existing sample-dataset task, and one
promotes the read-only Zarr geometry inspector into `dev/scripts/inspect_era5_zarr_geometry.py`.
The sample task brief changes only its design citation; the other 52 relocated files retain original blobs.

| Batch | Commit | Result |
|---|---|---|
| Sample task and original context | `21c81ac9` | Two task-owned files moved; context retained |
| Historical notes and inspector | `d166df9e` | 18 files moved |
| Output-schema evidence | `785d344f` | 33 files moved |
| Preserved duplicates and obsolete brief | `deeda577` | 45 files retired |
| Canonical board citations, on main | `c6cb38d9` | Live sample and WF0 citations repointed |

Deleted sources comprise 15 GF15 adapter review files, 29 simulation-identity review files, and the
superseded experiment-freeze repair brief. The context inventory lists every exact deleted path.
All 44 archive counterparts remain unchanged, and every original source is retrievable from the pin.
The obsolete GF15 working-directory attributes rule was removed. Byte-preserving attributes accompany
relocated historical evidence; historical relative links resolve in the original pinned context.

Verification candidate: `deeda577` on Windows 11, PowerShell 7, Pixi default environment.
No simulation input/config or project output root was used; this is a repository-placement change.

- `pixi run pytest tests/test_activation_links.py tests/test_sealed_records.py -q` passed all 38 tests
  after each batch. Final run used `--basetemp .tmp/scratchpad/legacy-migration/pytest-final` (0.53 s).
  Initial sandboxed runs failed on Windows temporary-directory permissions; the successful checks used
  a worktree-local temporary root with execution escalation.
- `pixi run ruff check dev/scripts/inspect_era5_zarr_geometry.py` and its Ruff format check passed.
- `pixi run python dev/scripts/inspect_era5_zarr_geometry.py --help` passed; live stores were not probed.
- `pixi run lint` passed. `pixi run format-check` passed: 432 files already formatted.
- The disposable final verifier checked all 101 original source blobs and SHA256 values, all 44 archive
  identities, all 34 recorded citation byte spans, all applied destinations, and the three unchanged holds.
  The only remaining tracked `dev/working` files are the three approved holds.
- `git diff --cached --check` passed for each batch. Board citation checks retained the pre-existing
  eight errors and 26 warnings, with no new issue set.

No full suite, workflow execution, baseline check, landing, or push was performed. Combined integration
gates remain due at approved landing under the repository validation ladder.

Open follow-up: triage the geographic register's unresolved findings against current case evidence before
admitting fixes. It has no matched active task; the migration task retains this handoff. The pre-existing
absent Quarto design citation is outside this migration and remains unresolved.

## Approved landing

Merged as `422afceba2aa8242c738801a04d4ae7a8cbb450e`; tested candidate
`83f38e1918e60ba59b0afdca45a53a0f16192931`, tree `34f87ee695b5e6c39f3d51817f0cf207404ce465`.
The merged tree matched the tested candidate exactly, with candidate and original approval ancestry proved.
The original migration commits remain reachable through the ancestry-preserving merge.

`pixi run test-fast`: 4013 passed, 17 skipped, one expected failure, 8645 warnings (241.38 s).
The gate recorder and executable verifier passed. Retained [gate identity](legacy-development-migration-2026-10-09/landing/gates.json)
is retained. Recover the compressed diagnostic log from commit `53d07f52` at
`dev/records/reviews/legacy-development-migration-2026-10-09/landing/test-fast.log.gz`.
Decompress it to recover the original log bytes and recorded SHA256; the JSON's original
absolute log path describes the execution location, rather than a permanent storage location.

The first test run passed but its evidence was refused because ancestry changed during execution.
The successful record came from a fresh run on the frozen candidate. The landing helper's automatic
rebase flattened the preservation merge and conflicted; that rebase was aborted, the exact verified
candidate was merged directly, and `task-land` completed its already-landed cleanup path.
Session-1 is detached and free; the merged local branch was deleted. No push was performed.

Geographic triage continues as backlog item `t2610091622`; the migration task can close independently.
