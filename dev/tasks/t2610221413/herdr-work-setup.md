# Herdr multi-agent work setup

## Suggested setup

Proposal dated 2026-10-22. This document recommends an operating arrangement; it does not authorize
agent launches, configuration changes, landing, or pushing. The intended reader is the repository owner
and the agent coordinating development. Start with one coordinator and up to two independent workers;
keep the third session available for review or an urgent isolated fix.

| Herdr space | Git location | Suggested responsibility |
|---|---|---|
| `blueearth_cst` | Primary `main` | Coordinate scope, board maintenance, review and approved integration. |
| `cst · s1` | `session-1` | First implementation task with one owning specialist. |
| `cst · s2` | `session-2` | Second independent implementation task with one owning specialist. |
| `cst · s3` | `session-3` | On-demand review, reproduction or an urgent isolated implementation. |

These are logical labels, not fixed Herdr IDs. Discover actual workspace and pane IDs at launch.
Keep workspaces permanent and agent assignments temporary. A session belongs to its current branch
and purpose, not permanently to a language, model or provider. Three available sessions are capacity,
not a target number of simultaneous agents. Multiple workers still require explicit authorization
under the shared routing policy.

For each active session, use an agent tab and a checks tab in the same worktree. Give the worker a
task name such as `ci-repair`; use the checks shell for tests, logs and inspection. The coordinator
should report the name, workspace/pane IDs, branch and worktree after dispatch. Background launches
should preserve the user's focus. Avoid competing commands against the same mutable run outputs.

## Relationship to git-workflow

The current [.git-workflow.yml](../../../.git-workflow.yml) uses `mode: slot`,
`slot_registry: advisory`, `isolation_landing: approval` and `auto_push: false`.
The three sessions are reusable worktrees with advisory occupancy. Calling them lanes in conversation
does not enable the atomic `mode: lane` contract.

Herdr supplies visibility and terminal organization. Git-workflow owns allocation, branch identity,
verification, integration and cleanup. A visible pane neither claims a session nor makes concurrent
writes safe. Use the established lifecycle in
[development workflow](../../reference/dev-task-and-session-workflow.md#worktree-coordination).

Atomic lane mode adds claims, scope enforcement, readiness pinned to a commit and controlled integration.
It remains an alternative requiring a separate policy decision and migration. Consider it if advisory
coordination repeatedly permits ownership collisions; visible panes alone do not justify that migration.

## Roles and allocation

Use the live registered role pool through `agent-routing`. Suggested matches are:

| Work | Role |
|---|---|
| Python implementation and regression tests | `python-engineer` |
| R implementation and tests | `r-developer` |
| Cross-workflow architecture and contracts | `cst-architect` |
| Scientific applicability and numerical evidence | `model-validator` |
| Independent challenge of a consequential design | `critical-thinker` |
| Analytical figure design | `dataviz-designer` |

Choose models and effort through the shared routing policy and explicit user preferences. GPT-6.1 Sol
at medium effort was the requested allocation for the CI repair example; this proposal does not turn
that choice into a mandatory default or a claim about comparative model performance.

Use a fresh reviewer when independence adds value, especially for cross-workflow or scientific changes.
A read-only reviewer can inspect a frozen commit without claiming a writing session. Give it the exact
commit and a read-only boundary; any tests must use isolated scratch and outputs. If it will make fixes,
allocate a writing session and sequence overlapping work. A reviewer need not occupy Session 3 simply
because that space exists.

## Operating sequence

1. The coordinator defines the objective, owned files, affected consumers and acceptance checks.
   Inspect current session occupancy and shared-file overlap before choosing a worker.
2. Allocate a clean available session through the managed `task-start` lifecycle from local `main`.
   Verify session identity before launch; never create a task branch manually to bypass allocation.
3. Inside Herdr, launch the worker in a visible pane using the shared `agent-routing` and `herdr`
   skills. Preserve the selected role contract, model/effort and assigned worktree. If launch fails,
   report the blocker rather than silently switching to an internal subagent.
4. Supply a bounded handoff: objective, source paths, ownership, dependencies, checks, write authority,
   commit policy and no nested delegation. Workers implement, verify and commit their own changes.
5. Workers maintain their local ignored `STATUS.md` at meaningful checkpoints. Durable task state
   belongs to the canonical board on main; the coordinator sequences shared board writes.
6. Return the commit, changed behavior, exact checks and evidence, remaining limitations and next action.
   The coordinator reconciles the result and requests any warranted independent review.
7. On explicit landing approval, follow the managed integration procedure and reuse valid evidence.
   Prove ancestry and committed-tree equivalence, then park the session and remove the merged branch
   through the lifecycle. Pushing remains a separate explicit decision.

Follow [validation policy](../../reference/dev-validation.md) for check selection and evidence reuse.
No extra full-suite gate is introduced by this proposal. Follow-ups stay in their occupied session
until switching or landing is authorized; an idle agent or completed test does not free the session.

## Coordination and recovery

- Parallelize independent changes. Shared configuration schemas, runners, workflow contracts and
  reference documents need explicit ownership or sequencing. Separate worktrees do not remove
  integration conflicts or isolate shared external project outputs.
- Only one coordinator performs primary-checkout Git operations. Primary maintenance remains limited
  to the allowed board/task paths outside authorized integration operations.
- Staged changes on primary block advisory landing. Identify their owner and disposition; preserve
  them rather than stashing, resetting or unstaging to force a merge.
- A launch timeout does not prove the worker never started. Inspect its pane and state before retrying.
  Do not launch a duplicate writer after losing contact with the first.
- Herdr's `idle` or `done` indicator is a navigation aid, not verification evidence. Read the return,
  inspect the branch and confirm the relevant checks before accepting completion.
- On interruption, retain the branch, local status and evidence. Resume the same worker when suitable;
  otherwise hand its exact worktree and recoverable state to a replacement after stopping the old writer.

## Tracking conveniences

Use task-based unique agent names. These example commands use a hypothetical `ci-repair` agent;
discover live names and IDs before invoking them and consult installed CLI help for current syntax.

```powershell
herdr agent list
herdr agent read ci-repair --source recent-unwrapped --lines 80
herdr agent focus ci-repair
herdr agent wait ci-repair --timeout 60000
```

Prefer targeted reads over repeatedly switching focus. Reuse a worker for related follow-ups; start
a fresh context for independent review. Keep task status and evidence in their existing repository
homes rather than creating a second Herdr-specific tracking system.

## Adoption and evaluation

Retaining one coordinator with one worker is the simpler option when work overlaps or task packaging
costs more than it saves. Two independent workers are the suggested normal ceiling, with a third used
deliberately when coordination and compute capacity permit. Permanent provider-specific lanes are
less flexible and are not recommended.

Trial one ordinary path: allocate, launch visibly, inspect progress, receive a tested commit, obtain
landing approval and park the session. Confirm that the user can locate the worker without asking
the coordinator, that its reported cwd/branch match its assignment, and that unrelated work survives.
Walk one failure path: a launch interruption or a staged-primary landing blocker must leave one
recoverable writer and preserved changes, with an explicit next action.

This proposal was checked for consistency with the current slot policy and existing Herdr guidance.
The complete arrangement has not yet been demonstrated in a fresh session. Adoption should update
the existing development workflow reference, keeping one authoritative home for operational rules.
