---
title: The shell-write scope backstop is inert in advisory mode
type: watch-item
area: tooling
origin: 2026-09-06 agent-hygiene audit
created: 2026-09-06
updated: 2026-09-06
---

> [!note] Overview
> **What** — The PostToolUse scope-backstop hook registered in .claude/settings.json returns 0 unconditionally in this repository: it requires slot_registry: atomic, and .git-workflow.yml sets advisory. There is no shell-write scope detection here on either runtime.
> **Why** — An audit reported this as a Claude/Codex asymmetry -- Claude registers the backstop, Codex does not. Wiring it into .codex/hooks.json would add a second no-op. The real state is that neither runtime has the coverage, and the reason is structural, not a wiring gap.
> **Trigger** — The repo moves back to slot_registry: atomic, OR the brain's git-workflow skill gains an advisory-mode scope source for the backstop to compare against.

## Detail

Recorded 2026-09-06 in place of a patch, because the patch an audit asked for
would have been a no-op. Kept as the record of *why* the obvious wiring fix is
wrong.

### What was reported

That shell-write coverage differs between runtimes: `.claude/settings.json`
registers `scope-backstop-hook` on `PostToolUse` for `Bash|PowerShell`, while
`.codex/hooks.json` registers only the `PreToolUse` native-edit guard and the
lane banners. Suggested fix: wire the supported Codex events to scope checking
and add primary-checkout change detection.

### What is actually true

The backstop is inert in this repository on **both** runtimes. From
`worktree-session.py`, `command_scope_backstop_hook`:

```python
repo_root = repository_root(cwd)
primary = primary_worktree_root(repo_root)
if read_slot_registry(primary) != "atomic" or repo_root == primary:
    return 0
```

`.git-workflow.yml` sets `slot_registry: advisory`, so the first clause returns
0 for every call, in every checkout — the primary skip the audit noticed is the
*second* clause and never even gets evaluated. Adding the hook to
`.codex/hooks.json` would register a second call site for a function that
returns 0 before doing anything.

### Why it cannot simply be wired up

The backstop is a DETECTOR, not a preventer: it compares the worktree against
`expected_paths` from the session's claim after the write has happened. In this
repo there is no such declaration to compare against. `expected_paths` is only
ever written by `task-start`/`task-scope` in **atomic** mode
(`worktree-session.py` lines 1580, 1652, 1815); the advisory-mode record
produced by `advisory_session_records` carries `session`, `state`, `task`,
`branch`, `worktree` — and no path scope at all. Lanes here are taken by hand:
`cd` to a free session worktree, branch from `origin/main`. Nothing declares a
scope, so there is nothing to check a write against.

So this is not a wiring gap that a hook registration closes. Either the repo
returns to `slot_registry: atomic` (which it deliberately left), or advisory
mode grows a scope source — and that logic lives in the brain's canonical
`git-workflow` skill, not here.

### What this repo does still have

- `PreToolUse` guard on native write tools, registered on **both** runtimes —
  the isolation floor (`worktree_policy: always`) is enforced where it can be.
- No shell-write detection, on either runtime, anywhere — including the primary
  checkout. Treat the `SessionStart` "INTEGRATION CHECKOUT" banner as the only
  thing standing between a shell command and an unguarded write to the primary.

Raised upstream as an improvement candidate against the `git-workflow` skill:
an advisory-mode scope source, and primary-checkout change detection that does
not depend on a claim.
