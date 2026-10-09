# dev/

Development process and project record. Everything here supports building the
project; none of it ships. The lifecycle that fills these folders is the
`project-system` skill's workflow.

## Layout

Organised by **how long a thing stays true**, because that decides both where
it goes and when it may be deleted.

**Happening now** — small, churns constantly:

| Path | Holds |
|---|---|
| `tasks/` | **The board.** One note per open item — `todo-item` (work) or `watch-item` (true, tracked, no action intended). The source of truth |
| ↳ `origin:` | Which milestone the item fell out of, using `reference/roadmap.md`'s own IDs (`R10`, `P3-3`, `M02b`). Set it only from a **recorded** origin — the source item's ID, or the `followups.md` section it was migrated from. Leave it blank when the lineage would have to be inferred from prose, and say so in the note's `## Refs`: the Origin column is read when prioritising, so a guess there costs more than a gap |
| `TODO.md` | **Generated** view of `tasks/` — `todoboard render` writes it and the banner says do-not-edit. Never hand-edit it; edit the note |
| `LOG.md` | Closure ledger. One row per item the board has closed since 2026-08-07, **capped at three short sentences** — see the cap below |
| `working/` | Three held legacy sources; do not add files or folders |

Do not create `dev/drafts/` or add to `dev/working/`. Put substantial task
material in the owning live task's `tasks/<id>/` sidecar and link it from the
board note. At closure, promote material that a future reader needs into
`reference/` or `records/` and remove the task sidecar; otherwise let Git
history retain it. Existing `working/` paths remain until their citations and
owners can move together.

The `main` worktree is the canonical board. `dev/scripts/todoboard.py` targets
it even when invoked from a session worktree. Edit notes there, render the view,
and commit board changes on `main` separately from feature work. A task's
`branch:` field links unfinished implementation without copying its note into
the task branch. The repository wrapper refuses to use a different board root.
On Windows, open `.tmp/navigation/main-dev.lnk` to view main's live board in
File Explorer. Edit it through the wrapper or main's own `dev/tasks/` path.
Navigation setup below excludes a named session's tracked `TODO.md` and
`tasks/` through per-worktree sparse checkout. Main keeps the complete board;
the session index retains its snapshots for Git history and merges. Relative
`core.hooksPath: .githooks` keeps the post-checkout session identity warning.

**Stays true** — consulted while working, rewritten rarely and deliberately:

| Path | Holds |
|---|---|
| `reference/` | The rules and the phase narrative (`roadmap.md`): `naming.md`, `agent-activation.md`, `git-conventions.md`, `contracts/`, `workflows/` — see its `README.md` |

**Happened** — records of what was done, kept by identity:

| Path | Holds |
|---|---|
| `records/decisions/` | ADRs — **permanent**. Superseded ones stay with a pointer; evidence in a `<adr-slug>/` sibling folder |
| `records/milestones/` | Every milestone's design / plan / review / evidence docs — see its own `README.md` for the index |
| `tasks/2026-07-21_pre-r6-followups.md` | The one **pre-board** record: `tasks/` held closed-task records until 2026-08-07, when it became the open board. Bannered, kept, and ignored by the board's loader (it carries no `type:`) |

**Decays** — snapshots of a system that keeps moving:

| Path | Holds |
|---|---|
| `records/reviews/` | Process reviews and post-milestone self-check registers. **Prunable** — see the retention rule below |

**Pinned by code** — these paths are constructed in Python, so moving them is a
code change, not a documentation change:

| Path | Holds |
|---|---|
| `scripts/` | Developer scripts — inspect or maintain the repo, never part of a run (`scripts/README.md`). `check_baseline.py` derives the repo root from its own depth |
| `baseline/` | Replication baseline fingerprints and the discharge reference series; `MANIFEST_PATH_DEFAULT` hardcodes `dev/baseline/manifest.json` |

**Scratch lives outside `dev/`.** Disposable machine-local output goes in the
worktree-root `.tmp/` — task scratch under `scratchpad/<task-id-or-purpose>/`, tool state in named
subdirectories, and no loose files at its root. It contains probe output,
`scaffold_project_tree.py`'s default target (`.tmp/scaffold`), and any
`pytest --basetemp`. `dev/tmp/` was merged into it on 2026-08-02; there is no
second scratch location, and nothing in `dev/` is a place to park disposables.
The pytest and ruff caches were redirected into it on 2026-08-11
(`.tmp/pytest_cache`, `.tmp/ruff_cache`), set in `pyproject.toml`.

Shard `tasks/` or `records/reviews/` into `<year>/` subfolders only if a flat folder
ever grows unwieldy. Generated results, figures, and model outputs go in the
project-root `output/` (gitignored), not `dev/`. Create optional folders only
when first needed — and put new ones in the table above when you do.

## Worktree coordination

This is maintained-current guidance. Centralise task coordination on `main`; keep files whose
contents depend on a branch in that branch. Never mirror all of `dev/` or share a writable `.tmp/`.

| Content | Handling |
|---|---|
| Board notes, plans, handoffs, ledger | Main's `dev/`; use the board wrapper and current-board view |
| References, records, baseline manifests, developer scripts | Branch-local; integrate through Git |
| Code, tests, configuration, lockfiles | Branch-local; integrate through Git |
| Agent configuration | Existing configured shared links |
| Scratch, caches, environments, mutable outputs | Local to their owning worktree |
| Immutable input data | Shared external location when consumers cannot modify it |

The `main-dev.lnk` shortcut opens main's `dev/` without a traversable directory link inside a session.
Use branch-local references and scripts when changing its contracts. Local `tasks/` and `TODO.md`
snapshots should be excluded from session working directories; Git still retains them for merges.

Primary-checkout maintenance is limited to `dev/tasks/`, generated `dev/TODO.md` and `dev/LOG.md`.
References and developer scripts are branch-local implementation and integrate through Git. Native
edit guards accept the named file scopes as well as the task directory; board operations still use
the wrapper. If this policy blocks a board operation, revert its separate policy commit alone.

### One task, one locator

Allocate a session with `gw new` / `task-start`; that operation records its allocation. A hand-made
branch must be adopted before an agent starts: preview with `gw adopt`, then record the reviewed
identity with `gw adopt --confirm`. At entry, `gw check` / `session-check` must report `Session ok`.
Adoption records ownership; it does not resolve content conflicts or prove the implementation.

Keep the existing `branch:` field current. For work that needs tracking, add this compact section to
the central task note in a board-only commit on main; update it when ownership, location,
verification or the next action changes.
Do not duplicate it in a separate status file. Use logical checkout names and relative paths rather
than machine-specific absolute paths in tracked notes. Discover actual roots with `git worktree list`.

```markdown
## Work location

- Owner: session-N; branch: <branch>; implementation commit: <SHA or uncommitted>.
- Implementation: session-N :: <repo-relative paths>.
- Coordination: main :: dev/tasks/<task-id>/ (only if backing material is needed).
- Scratch: session-N :: .tmp/scratchpad/<task-id-or-purpose>/.
- Outputs: <configured project_dir; identify its owning checkout if relative>.
- Verification: <tested SHA, exact command, result, environment, input/config, output root>.
- Retention: <needed artifact, reason, event that permits cleanup>.
- Next action: <one concrete action>; blockers: <none or explicit condition>.
```

Assign one implementation owner at a time. If a task spans sessions, list each contributor's distinct
paths and artifacts here. Never create an independent task note in another checkout.

At handoff and approved landing, run `python dev/scripts/todoboard.py worktrees`; resolve or explain
every untracked or missing row. For a parked branch with no worktree, keep its note `status: blocked`
with `branch:` and explain the parking reason in Progress and Work location. The current CLI reports
that existing branch as missing and exits 1; this row is expected until the branch resumes or lands.
An absent branch or an unexplained ownership row still needs resolution.

### Local scratch and navigation

Put disposable task files under `.tmp/scratchpad/<task-id-or-purpose>/` in the owning worktree.
Leave tool caches in their configured `.tmp/` subdirectories. Keep the `.tmp/` root free of loose
files. Before cleaning a task folder, preserve needed evidence, check active writers and links,
and verify its exact containment; age and ignore status do not establish deletion authority.
Existing loose files require classification before moving or deleting them.

Preview Explorer navigation for every registered worktree; name each worktree before sparse exclusion:

```powershell
pwsh -NoProfile -File dev/scripts/setup-worktree-navigation.ps1
pwsh -NoProfile -File dev/scripts/setup-worktree-navigation.ps1 -Apply -ExcludeSnapshots -Worktree session-1
```

Each worktree gets ignored `.tmp/navigation/` shortcuts to main, the sessions, main's `dev/`, and
its own scratchpad. Pin that folder in Explorer Quick access. Shortcuts do not share file contents.
Rerun setup after worktrees are added or recreated. Without `-Worktree`, shortcut setup covers all
registered worktrees; sparse exclusion always requires explicit names. Preview makes no writes,
including when `-ExcludeSnapshots` is requested. Setup preflights every selected root before writing,
reports per-root failures, continues valid targets and exits nonzero if any failed. Snapshot exclusion
requires clean sessions and refuses custom sparse layouts. Stale shortcuts are reported and retained.
Use the updated session script until it has integrated into main.

Old branches may still recreate `dev/00-current-board-main/`. Confirm `Get-Item -Force` reports
`LinkType=Junction` with main's `dev/` as its target, then remove only that link from its owning session:

```powershell
cmd /c rmdir dev\00-current-board-main
```

This non-recursive command removes the junction itself. Never use `git clean` or recursive deletion
for junction removal.

### Handoff and synchronisation

1. Commit verified implementation in its owning branch; record unfinished work explicitly.
2. Update the central locator with the tested commit, results, decisions, next action and blockers.
3. Identify required untracked artifacts by source checkout, relative path, purpose and destination.
   Verify the destination before copying only those artifacts; compare hashes after transfer.
   Keep original evidence until the recipient confirms it is readable and sufficient.
4. The recipient verifies the branch and artifact locations before editing. Re-entering the same
   session is preferred; switching sessions or branches remains the user's decision.

At a new session's entry, synchronise a clean, local, unpushed branch with local `main` using the
existing Git workflow. Published branches use a merge unless rewriting is authorised. Dirty state
and conflicts require resolution first; do not automatically stash or reset. Synchronise again at
approved landing, not on every follow-up. Do not background-sync tracked folders or scratch.
At closure, promote required evidence to its retained home before removing completed scratch.

## Exceptions

`project-system`'s layout defines the `dev/` grammar; these entries sit outside
it on purpose. Run `brain status --layout --project .` from the brain
infrastructure checkout to check conformance.

| Path | Owner | Retention | Depends on |
|---|---|---|---|
| `dev/baseline/` | Replication validation | Frozen per baseline; replaced only by a recorded successor baseline | `dev/scripts/check_baseline.py` (`MANIFEST_PATH_DEFAULT`), `build_model.smk`, `analyze_projections.smk`, `config/advanced_settings.yml` |
| `dev/00-current-board-main/` | Old branch hooks | Legacy junction; remove locally as above | `.gitignore` |
| `dev/working/` | Repository owner | Frozen legacy; no new files; migrate folder by folder as citations move | `dev/reference/sealed-records.yml`, `.gitattributes` |

## The promotion rule

The [legacy migration record](records/reviews/legacy-development-migration-2026-10-09.md) retains the
original Git context and per-file destinations for the 2026-10-09 cleanup. Use it to resolve historical
citations after a legacy file moves; it is evidence navigation, not current workflow guidance.

**A cited note is a record, not a draft.** Before deleting anything from
`working/` at closure, grep the repo for its filename. If a test, module,
config, or tracked document cites it, it is source-of-record: promote it to the
milestone folder (or `tasks/` / `records/reviews/` / `records/decisions/`) and update every
citation in the same commit. Citations live in docstrings and prose, so
deleting one breaks provenance silently and no test fails.

This is not hypothetical. On 2026-08-02, 27 files were promoted out of
`working/` — eighteen to `records/milestones/r08/` alone — and eight of them were cited
by shipped modules, `analyze_projections.smk`, and `pixi.toml`.

Never let `working/` or `tmp/` hold the only copy of a primary source: `tmp/`
is gitignored and one `git clean -fdX` from gone.

## The retention rule

Among retained records, only `records/reviews/` is prunable. A process review or a post-milestone self-check is
a snapshot of a system that keeps moving, so the folder would otherwise
accumulate thousands of lines describing a repository that no longer exists.

A review may be deleted when **all three** hold:

1. **Nothing cites it** — including other reviews. Check with
   `git grep -l <filename>`, not intuition.
2. **Its items are dispositioned**, and anything carried forward has landed as
   a board note in `tasks/` or as a decision.
3. **Its durable output has left** — if the review produced skill or role
   candidates, those changes are committed in `brain`. The lesson's home is the
   skill; the review that prompted it is then spent.

`check_activation.check_links()` rejects new reference links into transient `tasks/` and prunable
`records/reviews/`. The two Phase A citations to `plot-improvements/verification.md` in `plot-style.md`
and `migration_plot_paths.md` are explicit retained exceptions. Before pruning that evidence, update
both citations and the checker's exception set together; the link check also requires the file to exist.

Delete whole files. **Do not collapse a register to its outcome summary** — that
rule was tried on 2026-08-02 and fails in practice, twice over: the post-R6
assessment is cited by 23 individual `O-` numbers from R7 docs, `roadmap.md`,
and `pyproject.toml`, and the post-R8 register's own summary states it is "a
derived overview, not a substitute". Citers reference the detail, not just the
path.

**Partial supersession means annotate, not delete.** A later revision often
supersedes only some sections — `wf2-v2-process-review-r2.md` replaces sections
1, 3 and 5 of its predecessor while 2, 4 and 6 stand. Put a banner in the
superseded file saying exactly which sections went and where; keep both.

### The one place a register WAS compressed — and what made it safe

`followups.md` was the exception. It no longer exists — the todo-board replaced
it on 2026-08-07 — but the rule it established governs the next register anyone
is tempted to compress, so it is kept rather than deleted with the file. (The
adoption's own working notes were drained on 2026-08-09 under the promotion rule
above: the board exists and the `watch-item` type shipped in the `todo-board`
skill, so the brief was spent. Recoverable from that commit if ever needed.)

On 2026-08-07 that file had reached 2,038 lines, roughly half of it items
already closed, because a closure note had grown into a post-mortem averaging
29 lines. The closed items were compressed into a brief archive; the open ones
became board notes later the same day. The archive was retired once its lessons
had durable homes. Recover a cited pre-board item by ID with
`git show 45e3a564:dev/followups-archive.md`.

That was allowed only because condition 3 above — **its durable output has
left** — was checked item by item and already held. Every reusable lesson in
those write-ups had been promoted at the time it was learned: the `ancient()`
trap to `dev/reference/workflows/rule-index.md`, the `tee_to_log` stream
boundary to `snake_utils._Tee`, the `LOG_RULES` literal constraint to
`tests/test_log_rules_contract.py`, the branch-shared-fixture hazard to
`check_baseline.py`. The long entries were duplicating guidance that already
lived somewhere it is actually read. Exactly one lesson was still unpromoted
(R9-4's) and it went into `AGENTS.md` as part of the sweep.

So the rule generalizes rather than contradicting the one above: **compress a
closure note only after its lesson has a home outside the backlog, and name the
commit the full text is recoverable from.** What is not allowed is compressing
first and hoping the detail was not load-bearing — which is the `records/reviews/`
failure this file already records. The other half of the safeguard: the item IDs
are cited from code, tests and Snakefiles, so the archive keeps every ID rather
than merging items away.

Do not prune retained records outside `records/reviews/`. `records/decisions/` and
`records/milestones/` preserve decisions and milestone evidence; `reference/` is maintained as the current system.
Live `tasks/` notes and sidecars follow the task-closure procedure above: promote needed material,
then remove the eligible task files through the board workflow. Legacy `working/` files follow the promotion
rule, with citations and owners migrated together. Neither procedure is routine record pruning.

### The cap on `LOG.md` rows — the same rule, applied before the fact

`LOG.md` is the next register anyone will be tempted to compress, so the rule
above is written into it up front rather than applied in a panic at 2,000 lines.

**A closure row is at most three short sentences in plain language: what closed,
why, and where anything durable now lives.** When a closure produced a finding
worth keeping — a measurement, an owner ruling, a defect class, a tolerance — it
goes to its own home *first* (a `reference/` doc, a test, an ADR, a board note),
and the row points there. The row is the index; it is not the storage.

This is the promotion rule pointed forwards. Compressing after the fact needs
condition 3 checked item by item; capping up front means the lesson is placed
while the author still knows what it was.

**The cap constrains the ROW, not the work.** A closure whose content *is* the
finding — `t2608152230` carries the `rtol` `1e-9` → `1e-6` ruling, a 0.0-ulp
reconstruction, and four false greens found by running a validation plan rather
than reading it — does not get three sentences by deleting two of those. It gets
three sentences because they already live somewhere a future reader will
actually hit. If there is nowhere to put a finding, that is the signal to make a
home for it, not to lengthen the row.

**Retrofitting is per-row and evidence-first.** Before shortening any existing
row, grep the detail you intend to drop and confirm it survives elsewhere;
`git grep` is the check, not memory. Worked example — `t2608132100`'s dropped
measurements (6.43 MB across 82 blob versions, the 7.1 MB push) survive in
`reviews/2026-08-13_fao-branch-assessment.md`, `scripts/notebook_outputs.py`,
`docs/notebooks/README.md` and `tests/test_notebook_outputs.py`, one of them a
test, so that row is safe to cut from 172 words to 62. A row whose detail
survives nowhere is not a row to compress; it is a lesson without a home.

Rows written before 2026-08-19 are grandfathered and shortened opportunistically
under the paragraph above — never in a sweep, which is the mode that loses things.

Why a cap at all: the register took 48 closures in its first twelve days at a
median of 172 words, which is `followups.md`'s trajectory (2,038 lines, closure
notes averaging 29 lines) with the same cause — a closure note growing into a
post-mortem because there was no other place to put one.

## Milestone records

`records/milestones/` holds one folder per milestone. **`milestones/README.md` is the
index** — folder, milestone, seal date and tag — and is the only place that list
is maintained.

Deliberately not repeated here. This paragraph used to enumerate the folders and
give a count, and both went stale: it still read `r01/..r08/` and "all sixteen"
after R9, R10 and R11 had sealed, so the file that points at the index disagreed
with the index. One list, one home.

Two naming facts a reader trips over, since they cannot be inferred from the
folder names: Phase 3's milestones are `p31/`, `p32a/`, `p32b/`, `p33/` because
`roadmap.md` identifies them as `P3-x` rather than `Rn`; and there is no `p32/`,
because P3-2 split in two.

Two rules govern them:

- **New milestones get a folder there, not at the `dev/` root.** The thirteen
  that were at the root moved into `records/milestones/` on 2026-08-02 — a path change
  only, no file renamed, split, or edited beyond the prefix.
- **A sealed milestone's contents are not refactored.** Filenames and internal
  grammar vary by era and stay as written; later milestones converge on
  `<topic>-design.md`, `<topic>-task-brief.md`, `migration_<topic>.md`, and
  friends. A milestone folder is also the default home for that milestone's
  promoted working notes.

## Working rules

- **Admit before you track.** Small work fully explained by its diff and Git
  history creates no task ID or record. Track only work that must stay visible
  beyond the current session.
- **The board holds live work only.** Move closed tasks to `tasks/` and drain
  their working notes — deleting the uncited ones, promoting the rest.
- **Handoffs are self-contained.** A note handed to another session or runtime
  states objective, state, decisions, location, validation, next action, and
  blockers.
- **Record exact validation** — the commands run and their outcomes.
- **Log shipped features in the root changelog** (`CHANGELOG.md`) — feature-level
  entries only, linking `records/decisions/` or `tasks/` for the detail. It lives at the
  project root, not in `dev/`.
