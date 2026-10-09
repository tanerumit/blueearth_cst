---
title: Harden worktree coordination
type: todo-item
status: active
branch: feat/worktree-policy-improvements
effort: 2
area: dev
queue: 1
created: 2026-10-09
updated: 2026-10-09
---

> [!note] Overview
> **What changes** — Retire traversable board junctions and make sparse navigation and maintenance safe.
> **Why it matters** — Sessions must not traverse main during cleanup or fail tests because board snapshots are excluded.
> **What it takes** — Update coordination scripts, policy, links and docs; verify without changing other sessions.

## Progress

- [x] Promote closed plot evidence verbatim and repoint links — main 8327babe.
- [ ] Reject reference links to transient task sidecars.
- [ ] Retire junction hooks and harden explicit navigation setup.
- [ ] Limit primary maintenance to board surfaces.
- [ ] Document ownership and repair wrapper/documentation drift.
- [ ] Verify falsifiers and final test-fast; retain evidence for approved landing.

## Work location

- Owner: session-1; branch: feat/worktree-policy-improvements; implementation: in progress.
- Implementation: session-1 :: dev/scripts/, tests/test_activation_links.py, coordination docs and policy.
- Coordination: main :: dev/tasks/t2610091206-worktree-coordination.md.
- Scratch: session-1 :: .tmp/scratchpad/worktree-coordination-r2/; retained through approved landing.
- Verification: Windows 11 / PowerShell 7 / Pixi; no run configs or scientific outputs.
- Next action: finish the authorized branch changes; landing and other-session changes require owner action.

| Claim | Check | Input / output |
|---|---|---|
| Durable links | Red/green synthetic test and check_links | Sparse session and main |
| Safe navigation | Preview snapshots and controlled invalid roots | Task scratch |
| Maintenance scope | guard-hook JSON decisions | Main paths from session |
| Ownership | todoboard worktrees | Live branches; explain existing rows |
| Final regression | pixi run test-fast | Session tip; task scratch log |

## Improvement candidates captured

- todo-board: parked linked branches report missing and force exit 1; no parked-state classification.
  Measured from reconcile() and the existing feat/model-upgrading row; the branch exists without a worktree.
