# Development workflow

Shared procedures for developers and agents coordinating repository work. This reference owns task
admission, board location, worktree coordination, and handoffs. Placement and scratch rules live in
[repo-layout.md](repo-layout.md); preservation rules live in [record-lifecycle.md](record-lifecycle.md).

## Task admission and the board

Track work when a future reader needs its progress, unresolved decisions, or handoff. Small work fully
explained by its diff and Git history needs no task ID or separate record.

The `main` checkout owns `dev/tasks/`, generated `dev/TODO.md`, and `dev/LOG.md`. Use
`dev/scripts/todoboard.py`: it resolves the canonical board even when invoked from a session and refuses
a different board root. Edit notes in main, render the view, and commit board changes there separately.

```powershell
pixi run python dev/scripts/todoboard.py render
```

A board note is a `todo-item` for work or a `watch-item` for a condition worth tracking without current
action. A watch item carries the trigger that would turn it into work. Queue ordering is described in
[repo-layout.md](repo-layout.md#dev).

Set `origin:` only from recorded lineage, using the IDs in [roadmap.md](roadmap.md). If the source item's
ID or migration record does not establish an origin, leave it blank and explain the gap in `## Refs`.
Do not infer lineage from similar prose.

Substantial task documents belong in the live item's `dev/tasks/<id>/` sidecar on main, linked from its
note. `dev/drafts/` and `dev/working/` are retired locations; do not recreate them. The pre-board record
`dev/tasks/2026-07-21_pre-r6-followups.md` is a historical exception; it has no board `type:`.

## Worktree coordination

Centralize task coordination on main; keep branch-dependent implementation in its owning branch.
Never mirror all of `dev/` or share a writable `.tmp/`.

| Content | Handling |
|---|---|
| Board notes, task plans, handoffs, ledger | Main's `dev/`; use the board wrapper |
| References, retained records, baselines, developer scripts | Branch-local; integrate through Git |
| Code, tests, configuration, lockfiles | Branch-local; integrate through Git |
| Agent configuration | Existing configured shared links |
| Caches, environments, mutable outputs | Local to their owner; see the layout reference for scratch |
| Immutable input data | Shared external location when consumers cannot modify it |

Session working directories exclude tracked `tasks/` and `TODO.md` snapshots through sparse checkout;
Git retains their index entries for history and merges. Never bypass this with `git add --sparse`.
Resolve main with `git worktree list` or open `.tmp/navigation/main-dev.lnk`.

Primary-checkout maintenance is limited to `dev/tasks/`, `dev/TODO.md`, and `dev/LOG.md`. With
`core.hooksPath .githooks`, the pre-commit hook rejects changes to those paths on other branches,
including detached checkouts and renames out of those paths. The canonical-location rule applies even
when hooks are bypassed. References and developer scripts are edited in the session branch.

### One task, one locator

Use the configured `git-workflow` session lifecycle for allocation, identity checks, synchronization,
and landing. Root `AGENTS.md` and `.git-workflow.yml` identify the repository's active mode.

Keep the note's `branch:` current. When tracked work needs a locator, maintain the following section in
the central note rather than creating a separate status file. Use logical checkout names and relative
paths; resolve actual roots with `git worktree list`.

```markdown
## Work location

- Owner: session-N; branch: <branch>; implementation commit: <SHA or uncommitted>.
- Implementation: session-N :: <repo-relative paths>.
- Coordination: main :: dev/tasks/<task-id>/ (when backing material is needed).
- Scratch: <owning checkout> :: <path following repo-layout.md>.
- Outputs: <configured project_dir; identify its owning checkout if relative>.
- Verification: <tested SHA, command, result, environment, input/config, output root>.
- Retention: <needed artifact, reason, event that permits cleanup>.
- Next action: <one concrete action>; blockers: <none or explicit condition>.
```

Assign one implementation owner at a time. For work spanning sessions, list distinct contributor paths
and artifacts in that same note. At handoff and approved landing, run
`pixi run python dev/scripts/todoboard.py worktrees` and resolve or explain every missing or untracked row.
A parked branch without a worktree keeps `status: blocked` and its `branch:`, with the parking reason in
Progress and Work location. The current CLI reports that branch as missing and exits 1; explain the row
until the branch resumes or lands.

### Local scratch and navigation

Follow [Task temporary material](repo-layout.md#task-temporary-material) for scratch placement, evidence
retention, and safe cleanup. Tool state stays in its configured location.

Preview navigation before applying it; name each session selected for sparse exclusion:

```powershell
pwsh -NoProfile -File dev/scripts/setup-worktree-navigation.ps1
pwsh -NoProfile -File dev/scripts/setup-worktree-navigation.ps1 -Apply -ExcludeSnapshots -Worktree session-1
```

The script owns navigation flags and preflight behavior. See
[developer tools](../scripts/README.md#environment) for its operational summary.
Shortcuts under `.tmp/navigation/` do not share file contents. Rerun setup after worktrees are added or
recreated; sparse exclusion requires clean sessions and refuses custom sparse layouts.

Old branches may recreate `dev/00-current-board-main/`. Before removal, confirm `Get-Item -Force`
reports `LinkType=Junction` targeting main's `dev/`. Remove only the verified junction from its owning
session with the non-recursive command below; never use `git clean` or recursive deletion for this.

```powershell
cmd /c rmdir dev\00-current-board-main
```

### Handoff and synchronisation

1. Commit verified implementation in its owning branch; describe unfinished work explicitly.
2. Update the central locator with the tested commit, results, decisions, next action, and blockers.
3. Identify required untracked artifacts by source checkout, relative path, purpose, and destination.
   Verify the destination before transfer and compare hashes afterwards. Keep original evidence until
   the recipient confirms it is readable and sufficient.
4. The recipient verifies branch and artifact locations before editing. Prefer re-entering the same
   session; switching or landing remains the user's decision.

Follow `git-workflow` and root `AGENTS.md` for synchronization timing. Do not background-sync tracked
folders or scratch.

## Verification and closure

Use the [validation ladder](validation-ladder.md) to choose checks and record exact commands, results,
and material limitations in the existing task evidence or completion report.

The board holds live work only. Before closing a task through `todo-board`, promote durable material
under [record-lifecycle.md](record-lifecycle.md), preserve evidence still needed by consumers, and clean
eligible task material under [repo-layout.md](repo-layout.md#task-temporary-material). Remove the closed
note and eligible sidecar through the board workflow; do not move closed notes into the live board.

Write closure entries using the [ledger rule](record-lifecycle.md#closure-ledger-entries). Log shipped
features in root `CHANGELOG.md`, linking durable detail rather than transient task material.
