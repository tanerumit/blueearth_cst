# Legacy development files: review and proposed migration

Lifecycle: temporary task evidence. Task: `t2610091518`. Reviewed 2026-10-09.
Status: owner approved on 2026-10-09; all 101 dispositions applied and verified. Landing remains pending.
Execution evidence: [retained migration record](../../records/reviews/legacy-development-migration-2026-10-09.md).

## Recommendation

Keep evidence selectively, preserve exact historical context, and move live material to its owning task.
Do not drain `dev/working/` with a blanket rename or delete its uncited contents by default.

| Proposed disposition | Files | Qualification |
|---|---:|---|
| Retire redundant or superseded files | 45 | 44 require verified retained review context first |
| Relocate retained evidence | 50 | Preserve historical content; repair editable incoming citations |
| Promote a developer inspector | 1 | Keep its bounded sampling and read-only behavior |
| Move into an existing live task | 2 | Sample-dataset task remains open |
| Hold at current paths | 3 | Sealed evidence, historical citations, or stale specification |
| Total | 101 | Every tracked legacy file has one inventory entry |

[inventory.json](inventory.json) specifies each exact source, proposed destination, reason, constraints,
incoming path citations, source blob, and applicable archive comparison. Directory destinations below
preserve each source basename unless the inventory explicitly names a replacement.

The inventory is an approval plan, not an executable deletion manifest. Preconditions must pass before
each action. It does not authorize landing, pushing, new tags, changes to frozen records, or scratch cleanup
outside this review's own output folder.

## Evidence and coverage

- Reviewed candidate: `3e42b8cf0fa383d423e8c28b4711b7067af760a4`, `chore/maintainance`, session-1.
- Original source pin: `a9fde6c55927768e370094baa98ae9614d259cd0`, already in `main` history.
- Original parent: `dev`; legacy directory: `working`; directory tree:
  `91b9006df3e4cd5c4838465cdd9c1834601657f2`.
- All 101 sources are unchanged between the source pin and the reviewed candidate.
- Worktree logical size: 2,615,238 bytes. This is not a disk-space recovery estimate.
- Environment: Windows, PowerShell 7.6.6, Pixi default environment, Python 3.12.13.
- Read every file's headings or script structure, then the relevant status, closure, evidence, or interface
  sections. This was a retention review, not a fresh scientific evaluation or line-by-line code review.
- Inspected a 2,079-file tracked text corpus, including sparse-excluded task notes recovered through Git.
  Checked full legacy paths, relative suffixes, and basename occurrences; generic names such as `design.md`
  and `README.md` require context and are not evidence of a dependency by themselves.
- `git grep` across tracked Git content found 28 exact-source citation lines outside the legacy pool.
  A broader legacy-root search found 67 lines, including policy statements and already-absent old paths.
- Retrieved and rehashed all 101 Git blobs. Every retrieved blob matched its Git object ID.
- External case outputs, P-drive stores, scratch logs named by old evidence, and off-repository shell/skill
  implementations were not re-executed or certified as still available.

Git retrieval, using a blob from the inventory:

```powershell
git cat-file blob <source-blob>
```

The whole original directory, including relative context, is recoverable through its tree object. Use
the pinned commit for references to files outside that directory. Preserve that context in the retained
evidence entry point before removing original reviews; a rewritten archive is not an exact-byte substitute.

## R12 review duplicates: 44 conditional retirement candidates

Sources:

- `design-runs/gf15-production-adapter/`: 15 files.
- `design-runs/wf3-simulation-identity/`: 29 files.

Every source has a same-basename counterpart in its existing R12 review archive:

- `dev/records/milestones/r12/gf15-production-adapter-review/`
- `dev/records/milestones/r12/wf3-simulation-identity-review/`

Of the 44 pairs, 25 match after CRLF/LF normalization and trailing-newline normalization. The remaining
19 match after additionally replacing `dev/milestones/` and `dev/decisions/` with their `dev/records/`
successors in the archive text. This establishes path-sweep duplication, not universal byte equality.
Source and archive blob IDs are recorded separately in the inventory.

Both runs are terminal: GF15 records G2 approval on 2026-09-14 and finalization; simulation identity records
G2 approval on 2026-09-10, accepted v6, and archival finalization. Do not resume either run or add retroactive
acceptance identities. Their accepted designs already exist outside the legacy pool.

Before retirement:

1. Add the verified original Git context to an appropriate existing retained R12 evidence entry point and
   link it from maintained navigation. Preserve the existing archives unchanged.
2. Resolve the archive's explicit references back into the original runs, including the absolute
   worktree path in GF15's `review-brief.md`, without rewriting immutable reports.
3. Repoint editable implementation references to the retained entry point or correct archived artifact.
4. Keep each run's original byte identities, gates, findings, and directory context recoverable.
5. Remove only the inventoried original files; remove the obsolete GF15 `.gitattributes` path rule together.

If any immutable citer cannot resolve through verified historical context, hold its source. The plan does
not treat an archive filename, a hash string, or a terminal status alone as sufficient preservation.

## Output-schema work: 33 files to retain

The 24-file `design-runs/output-schema-contract/` has no same-name archival bundle. It contains the
accepted P0 review, negative/failed reference attempts, successful clean references, predecessor WF4
comparison details, and P5 scientific-continuity and excluded-field evidence. Preserve these records.

Proposed destination:

```text
dev/records/milestones/post-r12/output-schema/review/<basename>
```

The nine files in `output-schema-implementation/` are phase briefs and a handoff. P7 explicitly links its
completion to the retained R12 P7 complete-run record; this is historical implementation evidence,
not nine new open tasks. Preserve the package together:

```text
dev/records/milestones/post-r12/output-schema/implementation/<basename>
```

Resolve relative references between these bundles and the schema before any move. Preserve immutable
reports and their original pinned context; use external maintained navigation for relocated evidence.
Moving the bundle is not permission to update its historical verdicts or to reproduce expensive runs.
Several reports cite old scratch locations; preserving their prose does not prove those raw outputs survive.

## Historical notes, probes, and live work: 20 files

| Source group | Files | Proposed treatment |
|---|---:|---|
| Climate-workflow split design | 1 | Retain as dated review evidence; fix the live WF0 task citation |
| WF3 trace and old rule reference | 2 | Retain as dated snapshots, not current workflow guidance |
| Shipped sample-dataset scope and brief | 2 | Move to the existing sample-dataset task sidecar |
| Experiment-freeze repair brief | 1 | Retire; task closed as superseded and original module deleted |
| Git-command proposal and worktree addendum | 2 | Retain dated review; implementation outside repo |
| WF0 transfer README and nine case probes | 10 | Retain the case measurement harness as dated evidence |
| ERA5 Zarr geometry inspector | 1 | Promote to `dev/scripts/inspect_era5_zarr_geometry.py` |
| Geographic robustness observations | 1 | Retain diagnostics; carry unresolved actions forward |

Exact destinations are in the inventory. The sample-dataset owner is `t2608191733`; its task remains open
and cites both source documents. The climate split's original implementation task closed, while the live
WF0 forcing-evaluation task still uses its design as background; the design is historical evidence rather
than a new draft for that follow-up.

The freeze brief's task `t2608290250` closed as superseded on 2026-09-17. Its old
`write_experiment_config.py` mechanism and 19 tests were deleted; the ledger already records the reason
and successor guarantee. No incoming citation to the brief's filename or path was found.

The transfer probes encode a Ntoum bbox, P-drive catalogs, dated scratch outputs, and, in `shipped.py`,
an absolute historical case path. They are useful measurement evidence, not portable general-purpose
utilities. Keep their original context; do not silently generalize the nine case scripts.
`inspect_zarr_geometry.py` is the stronger reusable candidate: it has a `--store` option, bounded metadata
and chunk sampling, and an optional read-only HydroMT probe. Promotion must preserve its reported bounds,
update current invocation documentation, and verify its CLI without launching the full benchmark.

The geographic register includes unresolved defects and interpretation limits. Relocation does not close
those actions or establish that the external cases are scientifically validated. Review current task
coverage before creating new follow-ups, and retain synthetic-observation warnings.

## Plotting evidence: one file to retain

`wf2-plot-standardization-task-brief.md` records adopted visual rulings, a retired prototype's archive tag,
numeric falsifiers, production checks, and the subsequent plot sweep. Move it to a dated retained review,
not into a new implementation task. Before migration, compare its still-current rulings with
`dev/reference/plot-style.md` and promote any missing current rule there without duplicating the whole brief.

## Three held files

1. `parameter-placement.md`: explicitly sealed at this path by `sealed-records.yml`. The registry explains
   why its R14 citations require it to stay. Code and tests also refer to its findings. Keep it unchanged.
2. `2026-08-15_wf3-scenario-generation-trace/stress-test-design-and-surface-axes.md`:
   R12 intake/design records cite it as source material. Keep it at its current path until dependencies have a
   verified preservation route; do not sweep their citations as if they were maintained documentation.
3. `complete-run-output-schema.md`: its declared destination is current reference, but its header says
   P1-P7 are unimplemented while the phase package records completion. It also cites an absent
   `t2609191457-wf3-static-planning.md`. Reconcile current contracts, implementation status, and references
   before promoting it to `dev/reference/complete-run-output-schema.md`. A plain move would make stale
   guidance look authoritative. Keep the accepted P0 bytes in pinned historical context.

## Proposed execution order

1. Move the two sample-dataset documents with their live-task citation updates. Preserve owner rulings.
2. Retain the small historical notes and measurement harness; promote the bounded Zarr inspector.
3. Relocate the complete output-schema review/implementation evidence with verified original context.
4. Establish retained context for the two already-archived R12 runs, then retire their 44 originals and
   the superseded freeze brief only after preservation checks pass.
5. Reconcile the current schema as a separate documentation change. Keep both historically pinned sources
   at their present paths unless a specific later preservation proposal is approved.

Use a separate commit for each coherent batch. Repair all editable callers and links in that batch.
Board edits remain separate on `main`; source/evidence migration stays on this session branch.

## Verification plan

| Claim | Check | Inputs / output root |
|---|---|---|
| All files classified once | Compare inventory sources with `git ls-files dev/working` | Pinned source set |
| Evidence recoverable | Retrieve source blobs and compare Git object IDs | Pinned directory context |
| Archive comparisons truthful | Normalize newlines and two path sweeps | 44 existing pairs |
| Task admission introduces no faults | Compare board-check issue sets | Review scratch root |
| Sealed material unchanged | `pixi run pytest tests/test_sealed_records.py` | Registry |
| Relative citations resolve | `pixi run pytest tests/test_activation_links.py` | Moved paths |
| Inspector still admits documented CLI | Touched-file Ruff checks and `--help` | No P-drive benchmark |
| No unexpected moves/deletions | Compare staged names with approved inventory | Each batch |

The citation check also searches exact paths, relative suffixes, and context-resolved basenames.

Review checks performed: exact 101-file enumeration, 101 blob retrieval/rehash checks, 44 archive comparisons,
tracked-content citation searches, board baseline comparison, and `git diff --check`.
Migration tests above are planned, not already run. No workflow, scientific baseline, or full suite was run:
this review changes no runtime code or numerical output.

Commands used for the source and citation checks:

```powershell
git ls-files dev/working
git diff --name-only a9fde6c55927768e370094baa98ae9614d259cd0 HEAD -- dev/working
git grep -n -I -F 'dev/working/' HEAD -- . ':!dev/working'
git grep -n -I -F -f .tmp/scratchpad/legacy-review/source-paths.txt HEAD -- . ':!dev/working'
git merge-base --is-ancestor a9fde6c55927768e370094baa98ae9614d259cd0 main
pixi run python dev/scripts/todoboard.py check --json
git diff --check
```

The exact-path grep pattern file was generated from `git ls-files dev/working`. Citation outputs and board
issue sets are retained in the inventory; disposable probes used `.tmp/scratchpad/legacy-review/`.
Blob checks used `git cat-file blob <id>` redirected to a scratch file and
`git hash-object --no-filters -- <file>` for every source. Both IDs matched in all 101 cases.

The board check reports eight errors and 26 warnings both before and after admission. The issue sets are
identical; the new review task has no findings. Existing errors concern Overview fields in two other notes
and non-ID task folders. They remain separate maintenance work.

## Additional findings outside the 101-file migration

The broader search found live references to an already-absent
`dev/working/2026-08-19_quarto-docs-site/design.md` in docs-site tasks,
`docs/site/_quarto.yml`, and `pixi.toml`.
Do not claim this migration fixes those missing sources; recover their actual historical identity separately.

The prior policy fixes remain intact. This review changes no ignore rules and grants no general authority
to prune `dev/records/`, external scientific artifacts, or other sessions' scratch.
