# Development workflow

Last updated: 2026-10-23

Shared procedures for developers and agents coordinating repository work. This reference owns task
admission, board location, worktree coordination, handoffs, and Herdr worker coordination. Placement and
scratch rules live in [dev-repository-layout.md](dev-repository-layout.md); preservation rules live in [dev-record-lifecycle.md](dev-record-lifecycle.md).

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
[dev-repository-layout.md](dev-repository-layout.md#dev).

Set `origin:` only from recorded lineage, using the IDs in [roadmap.md](../records/milestones/roadmap.md). If the source item's
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

Sessions expose main's canonical `dev/tasks/` through a directory junction and `dev/TODO.md` through a
file symbolic link. Edits through those paths change main immediately; they do not wait for a merge.
Git retains branch snapshots in its sparse index for history and merges. A worktree-local
`sparse.expectFilesOutsideOfPatterns` setting preserves that separation, and a generated, untracked
`dev/.gitignore` hides canonical additions from session staging. Never bypass this with `git add --sparse`,
disable sparse checkout, or reapply a different sparse layout while these links are installed.
The rest of `dev/`, including `records/` and the ledger snapshot, remains branch-local.

Primary-checkout maintenance is limited to `dev/tasks/`, `dev/TODO.md`, and `dev/LOG.md`. With
`core.hooksPath .githooks`, the pre-commit hook rejects changes to those paths on other branches,
including detached checkouts and renames out of those paths. The canonical-location rule applies even
when hooks are bypassed. Synchronization merges may import these paths unchanged from `main`;
the hook still rejects session edits to that imported task state.
References and developer scripts are edited in the session branch.

### One task, one locator

Use the configured `git-workflow` session lifecycle for allocation, identity checks, synchronization,
and landing. Root `AGENTS.md` and `.git-workflow.yml` identify the repository's active mode.

A modifying request permits a clean detached session to claim itself from the primary checkout with
`task-start --task <task> --session <name> --base main --no-launch`; never create the branch by hand.
At new-session entry, synchronize a clean local unpushed lane with `main` by rebase; published lanes
use merge unless rewriting is authorized. Resolve dirty state/conflicts without automatic stash/reset.
Do not repeat synchronization per follow-up. Stay in the occupied session until the user asks to
switch or land. Commit completed tasks with the checks selected by the validation reference;
completion does not authorize landing or pushing. After a verified merge, prove ancestry,
detach/free the lane, then delete its branch; on failure preserve the lane and branch for recovery.

Keep the note's `branch:` current. When tracked work needs a locator, maintain the following section in
the central note rather than creating a separate status file. Use logical checkout names and relative
paths; resolve actual roots with `git worktree list`.

```markdown
## Work location

- Owner: session-N; branch: <branch>; implementation commit: <SHA or uncommitted>.
- Implementation: session-N :: <repo-relative paths>.
- Coordination: main :: dev/tasks/<task-id>/ (when backing material is needed).
- Scratch: <owning checkout> :: <path following dev-repository-layout.md>.
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

### Lane status

Each worktree owns an ignored root `STATUS.md` for a quick view of its active work and next steps.
Read it on entry, then reconcile its context with the actual branch and working changes before relying
on it. Maintain it at meaningful checkpoints and handoffs. Include the lane and branch, an update
timestamp with timezone, current focus, relevant verification, blockers, and one concrete next action.
Keep it concise; omit task-board summaries, other lanes, and unrelated landed work.

When absent, copy [the lane status template](../templates/lane-status.md) to the current worktree's
`STATUS.md` and populate it from inspected state. When the lane starts a new task or branch, refresh its
context and remove obsolete work after retaining any needed evidence. Never seed, link, or copy a
populated status from another worktree. Ignored files survive branch switches, so check the context
even when the file already exists.

Status is local continuity, not durable evidence or task authority. Keep durable decisions and
verification evidence in their owning task records or committed documentation; Git owns branch state.
Status updates are not committed, landed, or pushed.

When adopting this policy in a checkout that still tracks `STATUS.md`, preserve that checkout's copy
outside the tracked path before merging the removal; restore it afterward and verify
`git check-ignore STATUS.md` succeeds and `git ls-files -- STATUS.md` is empty. Follow repository scratch
and retention rules for any backup. Do this separately in each owning lane; do not overwrite another
lane's status. Branches predating the policy may still track the file: preserve the local copy before
switching to one and reconcile any tracked-file collision explicitly.

### Local scratch and navigation

Follow [Task temporary material](dev-repository-layout.md#task-temporary-material) for scratch placement, evidence
retention, and safe cleanup. Tool state stays in its configured location.

For a new session, exclude its snapshots while clean, then preview and create the canonical board links.
Run these commands from a checkout containing the helper, setting the target root explicitly:

```powershell
pwsh -NoProfile -File dev/scripts/setup-board-view.ps1 -WorktreeRoot <session-root> -ExcludeSnapshots
pwsh -NoProfile -File dev/scripts/setup-board-view.ps1 -WorktreeRoot <session-root> -LinkCanonicalBoard -CheckOnly
pwsh -NoProfile -File dev/scripts/setup-board-view.ps1 -WorktreeRoot <session-root> -LinkCanonicalBoard
```

Link setup preserves preexisting ignored task scratch under the session's `.tmp/tasks/`; it refuses
conflicting destinations, unrelated links and custom sparse layouts. File symbolic links require Windows
Developer Mode or an elevated shell. Rerun setup after worktrees are added or recreated.
Optional Explorer shortcuts are managed by `setup-worktree-navigation.ps1` (preview by default, `-Apply`
to write). They include the canonical tasks and local scratch. See
[developer tools](../scripts/README.md#environment) for navigation flags.

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

Follow `git-workflow` and the session-entry rules above for synchronization timing. Do not background-sync
tracked folders or scratch.

## Herdr agent coordination

Applies when a coordinator runs visible worker agents in Herdr panes; the `herdr` and `agent-routing`
skills own CLI syntax and role choice. Herdr supplies visibility only. Allocation, branch identity,
verification, landing and cleanup stay with the rules above and `git-workflow`; a visible pane neither
claims a session nor makes concurrent writes safe. Multiple workers need explicit user authorization.

Vendor documentation defines the model and effort controls: Codex
[`/model`](https://learn.chatgpt.com/docs/developer-commands#set-the-active-model-with-model) and Claude Code
[model configuration](https://code.claude.com/docs/en/model-config). The launch details below are local
observations from Codex CLI 0.162.0 and Claude Code 2.1.308 on 2026-10-23, not documented guarantees;
re-check them after upgrades.

### Spaces and ownership

- Keep one workspace for the primary checkout (coordinator) and one per session worktree. Discover live
  workspace, pane and agent IDs each time; do not record them in guidance. Aliases and model menus change.
- Reuse the session's designated agents pane for its one writer and name the agent after the task, in
  lowercase. Keep the checks `pwsh` pane for tests, logs and inspection. Never create a worker
  opportunistically; start one only for an authorized assignment, in the background, without taking the
  user's focus.
- Before reusing a pane, establish who owns its occupant. Stop or replace a prior worker only with the
  coordinator's established ownership or the user's authority over that task; otherwise report it and ask.
  Preserve its branch and changes first. Never close or stop another task's agent, pane or the Herdr
  server on your own judgement. An idle probe you started that holds no work may be exited.

### Launch

1. Choose model and effort from scope and the runtime's live supported list, following `agent-routing`.
   Print one sentence naming role, model, effort and reason before launching. Cache or catalog absence
   does not prove a model is unavailable; the live picker decides.
2. Verify worktree allocation (`git worktree list`, branch, clean tree) and, separately, a clean agent
   context. An idle pane or clean tree does not prove a fresh conversation.
3. With the shell idle in the foreground of the existing pane, run
   `herdr agent start <name> --kind <kind> --pane <id> -- <args>`:
   - **Claude Code:** pass `--model` and `--effort` after `--`; the UI and `/status` show the resolved
     model ID and effort.
   - **Codex:** pass only `-C <session-root>` and `-m <model>` after `--`. A `-c` override such as
     `model_reasoning_effort` forces embedded mode, so the worker is not listed by shared-server thread
     discovery (Herdr tracking still works). Instead open `/model` in the idle fresh CLI and choose the
     model, which leads to the effort screen. There, `s` applies model and effort to this session only;
     Enter saves them as the default, so do not use it. `/daemon` should report a running server; leave
     it untouched.
4. Verify effective model, effort, worktree and branch in the fresh UI. The start response and Herdr
   metadata can show a stale conversation ID until the first turn.
5. Send a preflight-only turn: confirm no earlier task, report cwd and branch, and stop. Record the new
   conversation ID, different from the pane's previous one. For Codex, also confirm that shared-server
   thread discovery lists it with the correct cwd. Claude Code keeps its own interactive session; it is
   not a Codex thread, so check its ID in `/status`, and Herdr read/wait for completion.

A new unrelated task always gets a fresh conversation, never a resumed or forked one; carry over only
selected instructions and evidence. Related follow-ups keep the existing conversation. Do not change
global defaults, permissions or the server to make a launch work.

### Assignment, review and landing

- Send a bounded handoff: objective, sources, owned paths, checks, write authority, commit policy, no
  nested delegation. The worker maintains its ignored `STATUS.md`; the coordinator alone writes primary
  board and task records. Report role activation, requested versus observed settings, worktree and branch,
  agent name and pane, and conversation ID.
- `idle` and `done` are navigation aids. Read the return, inspect the branch and run or confirm the checks
  chosen under the [validation ladder](dev-validation.md) before accepting.
- Landing and pushing keep their explicit-approval policy; a finished worker does not free the session.
  After approval, land under `git-workflow`, prove ancestry, then park the session.

### Failure and timeout

A timed-out start, prompt or wait does not show the worker never ran. Inspect with `herdr agent list` and
`herdr agent read <name>`, then wait or continue the same worker. Never resubmit the assignment or start a
second writer while the first may be live. After an interruption, keep the branch, status and evidence;
resume the same worker, or stop it and hand its exact worktree to a replacement.

## Verification and closure

Use the [validation ladder](dev-validation.md) to choose checks and record exact commands, results,
and material limitations in the existing task evidence or completion report.

The board holds live work only. Before closing a task through `todo-board`, promote durable material
under [dev-record-lifecycle.md](dev-record-lifecycle.md), preserve evidence still needed by consumers, and clean
eligible task material under [dev-repository-layout.md](dev-repository-layout.md#task-temporary-material). Remove the closed
note and eligible sidecar through the board workflow; do not move closed notes into the live board.

Write closure entries using the [ledger rule](dev-record-lifecycle.md#closure-ledger-entries). Log shipped
features in root `CHANGELOG.md`, linking durable detail rather than transient task material.
