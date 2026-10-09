# Addendum — `git worktree remove` is not atomic

**Date:** 2026-09-06 · Follows `proposal.md`, steps 3–4.

Found by the acceptance test: landing `chore/gw-shortcuts-improvements` itself, from an
agent session standing inside that worktree.

## What happened

```
Merge made by the 'ort' strategy.
 .../proposal.md | 384 +++++++++++++++++++++
error: failed to delete 'C:/…/.worktrees/blueearth_cst/gw-shortcuts-improvements': Permission denied
WARNING: 'chore/gw-shortcuts-improvements' is merged into 'main', but its worktree was
kept, so the branch was not deleted …
```

The warning was **wrong about the state**. `git worktree remove` had already deregistered
the worktree; only the directory deletion failed. So afterwards:

- `main` carried the merge and the ancestry assertion passed ✔
- the worktree was gone from `git worktree list` ✔
- the directory was still on disk, now holding a stale `.git` file
- the branch still existed, because the wrapper returned early

That is a stranded state: the branch's worktree no longer exists as far as git is
concerned, so nothing was holding it, yet the wrapper had reported the opposite and given
advice (`gw land --force`) that would not have helped — `--force` governs modified and
untracked *content*, not a locked directory.

## Why the directory could not be deleted

On Windows a directory cannot be removed while any live process holds it as its current
directory. The agent session running the land had exactly that cwd, and the harness resets
it there on every tool call, so it could not step out of its own way. `gw land` already
does `Set-Location` to the primary before removing — but that moves *its* shell, not the
other processes standing in the same place.

This is not exotic. Landing the worktree you are working in is the normal end of a task.

## Fix

`GwRemoveWorktree($primary, $path, $force)` replaces the bare exit-code check in both
`gw land` and `gw drop`. On a non-zero exit it asks `git worktree list --porcelain`
what actually survived and returns one of three states:

| State | Meaning | What the verb does |
|---|---|---|
| `removed` | clean removal | continue to branch deletion |
| `orphaned` | deregistered, directory left behind | **continue to branch deletion**, then warn, naming the directory to delete later |
| `kept` | still registered, nothing happened | keep the branch, report, suggest `--force` |

The general rule: **`git worktree remove`'s exit code does not describe what survived.**
Ask git, the same way `parallel-landing.md` insists the merge's exit code does not prove
the branch landed and `merge-base --is-ancestor` must be asked instead. Two commands in
this procedure now, both with the same shape — the exit code reports the operation, not
the state.

## Manual finish, this once

The stranded state was resolved by hand: `git branch -d chore/gw-shortcuts-improvements`
(safe — the worktree was already deregistered, and ancestry had been proved). The orphaned
directory at `.worktrees/blueearth_cst/gw-shortcuts-improvements` survives this session and
can be deleted once nothing holds it:

```powershell
Remove-Item "$HOME\workspace\.worktrees\blueearth_cst\gw-shortcuts-improvements" -Recurse -Force
```

It is no longer a registered worktree, so no git command is needed — and `git worktree
prune` has nothing to do, since the registration is already gone.
