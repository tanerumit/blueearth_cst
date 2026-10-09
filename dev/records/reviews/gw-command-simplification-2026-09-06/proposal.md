# `gw` command simplification — proposal

**Date:** 2026-09-06 · **Status:** implemented — `help` gating, `work`, `temp`, `land`, `drop` · **Branch:** `chore/gw-shortcuts-improvements` (landed)

> One defect surfaced by the acceptance test — `git worktree remove` is not atomic — is written up in [`addendum-orphaned-worktree.md`](addendum-orphaned-worktree.md), together with its fix.

Where the code lives: `~/OneDrive - Stichting Deltares/Documents/PowerShell/profile.ps1`
(the `gw` function, `$GwVerbs` table, `GwWriteHelp`, `GwLaneContext`). Backend:
`~/workspace/brain/artifacts/skills/git-workflow/scripts/worktree-session.py`, reached
through the per-worktree symlink `.agents/skills/git-workflow/`.

---

## The problem, stated precisely

`gw help` lists **21 verbs in 5 groups**. This repository runs
`mode: slot` + `slot_registry: advisory` (`.git-workflow.yml`). Under advisory:

| Verb group | Live here? |
|---|---|
| `integration-*` (5 verbs) | **No.** The repo's own config comment says `integration_mode` "is inactive with an advisory registry" |
| `task-scope` | **No.** Advisory mode refuses the atomic-only scope declarations |
| `task-done` | Degraded to a reporting checkpoint — `task-land` re-derives everything it checks |
| `task-recover` | Mostly atomic-mode administration (`reopen` rotates a token that advisory never issues) |
| `check`, `sync`, `session-create` | Rare, setup-time |

So roughly **15 of 21 verbs are inert or setup-only in this repo**, and they are the
ones with the most intimidating names. The six that matter are buried among them.

Two further frictions, independent of verb count:

- **`task-land` only runs from the primary checkout**, so landing means remembering to
  hop worktrees first — the step most likely to be forgotten mid-flow.
- **There is no discard primitive at all.** The nearest verb,
  `task-recover --action release`, "requires a clean worktree and ancestry proof" —
  ancestry proof is exactly what an abandoned branch lacks, so it refuses precisely
  when you need it.

---

## Proposed surface

Four working verbs plus navigation. Everything else stays callable, just unlisted.

```
gw
  Worktrees and the git-workflow lifecycle for this repository.

Navigate
  gw                     roster: worktrees, branches, which sessions are free
  gw <name>              switch this shell to a worktree
  gw status              the roster plus each worktree's working-tree state

Work
  gw work <branch>       take a free session, branch off main, cd into it
  gw land [<branch>]     merge to main, delete the branch, free the session
  gw drop [<branch>]     abandon: discard the branch, free the session
  gw temp <name>         create a disposable provisioned worktree, cd into it

  gw help --all          the full lifecycle surface (tasks, integration, admin)
```

**8 visible names instead of 21.** Every one of the four stated needs is one verb.

### Mapping to what already exists

| New verb | Implemented as | New logic? |
|---|---|---|
| `gw work <branch>` | `task-start --task <name> --type <type> --no-launch` → `Set-Location` to the path it prints | thin wrapper |
| `gw land [<branch>]` | resolve the primary worktree, then `task-land <sel>` with `--cwd <primary>` | thin wrapper + the worktree hop |
| `gw drop [<branch>]` | **new** — detach the session worktree, `git branch -D <branch>` | genuinely new |
| `gw temp <name>` | existing `create` → `Set-Location` | thin wrapper |
| `gw status`, bare `gw` | **already done** — `GwResolveLane` prints `free` / `occupied` / `task` / `primary`; `-IncludeDirty` adds working-tree state | none |

Need #4 (check lane status) needs no work. It is already the bare `gw` roster.

All four are `Local = $true` entries in `$GwVerbs`, i.e. implemented in `profile.ps1`
alongside `cd` / `status` / `help`. **No change to `worktree-session.py` and no change
to the git-workflow skill.** That keeps the whole scheme in one file, keeps the
`$GwVerbs` ⊆ backend-argparse closure property intact, and leaves the atomic surface
untouched for any repo on `mode: lane`.

---

## The four verbs in detail

### `gw work <branch> [--session <name>] [--base <rev>]`

```powershell
gw work fix/gw-options          # first free session, branched off main
gw work fix/gw-options --session session-2
```

Argument is the branch you want, in the repo's usual `type/slug` form. Split on `/`:
the prefix must be one of the backend's closed type set
(`fix|feat|refactor|docs|test|chore`); the remainder is `--task`. A bare name with no
slash defaults to `--type chore`.

Then: `task-start --task <slug> --type <type> --no-launch [--session …]`, and
`Set-Location` to the path it prints.

**Why `--no-launch` is the right primitive.** It is advisory-only and documented as
"claim the session and print its path without starting a child process; for a session
that is already running and claiming capacity for itself" — which is exactly the
by-hand gesture (`cd session-N`, branch off `origin/main`, work there) that this repo
has settled into. `--base` resolves through the `trunk:` key, then `origin/HEAD`, and
is explicitly never the primary's `HEAD` — so "based on main by default" is already
correct behaviour, not something to add.

Failure modes worth surfacing rather than hiding: no free session (name which slots are
held and by which branch), branch already exists, dirty target worktree.

### `gw land [<branch>] [--verify "<cmd>"]`

```powershell
gw land                         # lands the branch of the worktree you're in
gw land fix/gw-options          # lands it from anywhere
```

Runs `task-land <sel>` — rebase onto trunk, `git merge --no-ff`, optional check,
ancestry proof, delete the branch, detach the session back to free.

**The addition worth making:** resolve the primary worktree from `git worktree list`
and invoke the backend with `--cwd <primary>` automatically. Today this is a manual
`gw <primary>` first, and forgetting it is the single most common stumble. `task-land`
never pushes, so this stays a local operation — pushing remains explicit, as
`.git-workflow.yml` sets `auto_push: false`.

With no argument and run from inside a session worktree, the branch is the current one.

### `gw drop [<branch>] [--force]`

```powershell
gw drop                         # abandon the current session's branch
gw drop chore/spike-x --force
```

No backend equivalent exists; this is new code and should be honest about that.
Behaviour:

1. Refuse if the worktree is dirty (uncommitted work is not what "drop" is for) —
   unless `--force`.
2. Count commits not reachable from trunk (`git rev-list --count trunk..<branch>`).
   If non-zero, **print the count and the subject lines and require `--force`.** A temp
   lane legitimately has commits you mean to throw away; a slip on the wrong branch
   does not.
3. Detach the session worktree (`git switch --detach`), then `git branch -D <branch>`.
4. For a worktree created by `gw temp`, also `git worktree remove` it.

The dropped commits stay recoverable until gc — see the correction under **Steps 3–4**,
which found the obvious "it's in the reflog" claim to be false. Say so in the
confirmation line.

### `gw temp <name>`

You confirmed a temporary lane means a **fresh disposable worktree**, not a throwaway
branch on an existing session. That is the existing `gw create`, plus `Set-Location`
into the result, plus `gw drop` as the exit.

One cost to keep visible: a new worktree pays `worktree_provision`
(`pixi install`, `pixi run install`) and copies `worktree_seed`
(`test_case/test_local`, `test_case/basin_map_fixture`) — minutes, not seconds. And the
seed inherits the *primary's* fixture age, so a fresh temp worktree can fail tests that
an older worktree passes. `gw temp` should print the provisioning step it is running
rather than appear to hang. `--no-provision` stays available for a docs-only spike.

---

## Help gating (ships independently)

`GwLaneContext` already computes `$ctx.Registry` from `.git-workflow.yml`. Add a
`Show` field to each `$GwVerbs` entry — `always`, `advisory`, `atomic`, `admin` —
and have `GwWriteHelp` filter on the detected registry unless `--all` is passed.

Under advisory the Tasks and Integration groups collapse to nothing visible; under
`mode: lane` the full surface returns automatically. Nothing is removed from the
dispatcher, so every existing name keeps working and every script keeps running.
`$GwRetired` is the existing precedent for demoting a name while still naming it, and
the unknown-command handler's prefix suggestion should search the *full* table so a
hidden verb is still discoverable by typing it.

This half needs no decisions from the sections above and could land first.

---

## Full mapping, old → new

| Today | Tomorrow |
|---|---|
| `gw task-start --task x --type fix --no-launch` then `gw cd …` | `gw work fix/x` |
| `gw <primary>` then `gw task-land x` | `gw land` |
| *(no equivalent)* | `gw drop` |
| `gw create --task x` then `gw cd x` | `gw temp x` |
| `gw` / `gw status` | unchanged |
| `gw task-status` | folded into `gw status` (already true) |
| `task-scope`, `task-done`, `task-recover`, `integration-*`, `session-create`, `sync`, `check` | hidden; `gw help --all` |

---

## Alternatives considered

**Do only the help gating.** Cheapest, zero risk, and fixes "too many" without fixing
"awkward". It leaves the two real frictions — the primary-checkout hop before landing,
and the missing discard — in place. Worth doing either way; not sufficient alone.

**Push the new verbs into `worktree-session.py`.** Then `gw work` works from Codex and
bash too, not just PowerShell. But `work` and `temp` must change the *calling shell's*
directory, which a Python child process cannot do — the same reason `cd` is already
profile-local. It would also mean editing the shared brain skill for what is currently
a one-person ergonomic preference. Revisit if a second runtime needs it.

**Rename the backend verbs instead of wrapping them.** Cleanest vocabulary, worst
blast radius: `task-*` names appear across `session-slots.md`, `SKILL.md`, the
lane-banner hook, and several memory entries. Wrapping costs one indirection and
breaks nothing.

---

## What this does not change

- `auto_push: false` — landing stays local; pushing stays a separate explicit act.
- Three session slots, advisory registry. This is a vocabulary change, not a mode change.
- The atomic (`mode: lane`) machinery, which stays intact and re-appears in help
  automatically for a repo configured that way.

---

## Implementation record

### Step 1 — help gating (landed 2026-09-06)

`profile.ps1` only; the file is unversioned, so the pre-edit copy is at
`.tmp/scratchpad/2026-09-06_gw/profile.ps1.bak` in the `gw-shortcuts-improvements`
worktree (OneDrive version history is the other fallback).

- Each `$GwVerbs` entry gained an optional `Show` field: `always` (default),
  `advisory`, `atomic`, `admin`. Assigned `admin` to `sync`, `check`,
  `session-create`, `task-recover`; `atomic` to `task-scope`, `task-done`, and all
  five `integration-*`.
- New `GwVisibleVerbs($Registry, $All)` filters the table.
- `GwWriteHelp` now takes `$All`, reads the registry from `GwLaneContext` on the
  current repository root (defaulting to `advisory` outside a repo), lists only
  visible verbs, and sizes the name column from that set — so the page narrows too.
- Footer names the count of hidden verbs and points at `gw help --all`.
- `gw help --all` / `-a` wired through the dispatcher; any other argument errors
  with `Usage: gw help [--all]`.

`Show` gates **the help page only**. Dispatch and tab-completion still read the full
table, so nothing became unreachable.

Verified in a `-NoProfile` child shell against this worktree:

| Check | Result |
|---|---|
| `gw help` under advisory | 10 verbs (was 21); Sessions and Integration groups gone |
| `gw help --all` | all 21, no footer |
| `GwVisibleVerbs 'atomic' $false` | 17 — atomic set back, `admin` still hidden |
| `gw help --nope` | `Usage: gw help [--all]` |
| `gw task-scope --help` (hidden) | reaches the backend's argparse — still dispatches |
| `TabExpansion2 'gw integration-h'` | completes `integration-hold` — still completes |

### Step 2 — `gw work` and `gw temp` (landed 2026-09-06)

`profile.ps1` only. Both are `Local = $true`, because each must `Set-Location` in
the *calling* shell — a Python child cannot, which is why `cd` already lives here.

- `GwBackend($root)` extracted from the dispatcher, so local verbs reach the backend
  through one candidate list instead of a second copy.
- `GwSplitBranch($branch, $types)` turns one argument into `--type` + `--task`:
  `fix/gw-options` → `--type fix --task gw-options`; a bare slug is a `chore`; an
  unknown prefix errors and names the closed set. `temp` additionally allows `lane`.
- `GwInvokeBackend` runs the backend against the **primary** worktree (`$worktrees[0]`)
  with stderr merged, returns text + exit code. Arguments after the branch pass
  through verbatim, so `--session`, `--base`, `--no-reseed`, `--dry-run` all work.
- `gw work` parses the advisory `task-start --no-launch` JSON record and cds to its
  `worktree`. `--dry-run` emits `action: would_allocate` with **no** `worktree` key,
  so it correctly does not move the shell.
- `gw temp` takes `create`'s last output line as the path and cds there if it is a
  directory. It prints a heads-up before provisioning, suppressed under
  `--no-provision` / `--dry-run`.
- `Work` group added to `$GwGroupOrder`; `work` is `Show = 'advisory'` because
  `--no-launch` is advisory-only. Examples line now shows `gw work fix/gw-options`.

**One defect found and fixed while testing.** `create` defaults `--base` to the
primary's `HEAD` — the trap `landing-merge.md` documents, where a detached primary
bases the new worktree on whatever is checked out. `task-start` resolves the trunk
itself; `GwTrunk` now gives `temp` the same order (the `trunk:` key, then
`origin/HEAD`), and an explicit `--base` still wins.

Verified in `-NoProfile` child shells:

| Check | Result |
|---|---|
| `gw work fix/gw-probe --no-reseed` | claimed session-2, branched off `main`, cd'd there, printed `→ session-2 · fix/gw-probe`; `git rev-parse` in the new shell confirmed the branch |
| `gw work … --dry-run` | prints the plan, shell does **not** move |
| `gw work` / `gw work bogus/thing` | usage line / `'bogus/' is not a branch type. Use one of: …` |
| `gw temp spike-x --dry-run` | `from origin/main` (was `from HEAD` before the fix); no cd |
| `gw temp spike-x --base HEAD --dry-run` | `from HEAD` — explicit base still wins |
| `gw temp feat/spike-y --dry-run` | `spike-y on new branch feat/spike-y` |
| `gw`, `gw task-status` | unchanged — the `GwBackend` refactor did not disturb dispatch |
| `gw w`⇥ | completes `work` |

**Probe cleanup, worth knowing for step 4.** Reverting the live `gw work` test took
three steps: detach session-2, `git branch -D fix/gw-probe`, and **delete the
`session-claim` file in session-2's git dir**. That third one is not obvious and a
stale claim makes the next `task-start` refuse the session. `gw drop` must remove it.

### Steps 3–4 — `gw land` and `gw drop` (landed 2026-09-06)

**Both verbs have two shapes, because the backend knows only one.** `task-land`
resolves through `advisory_session_records()`, which iterates
`read_session_slots(primary)` and nothing else — so a `gw temp` worktree is invisible
to it. A configured session delegates to the backend; a task worktree runs
`references/parallel-landing.md`'s linked-worktree procedure locally.

That reference is the authority for the local path, and its **ordering is what carries
the safety**, so it is transcribed rather than paraphrased:

1. Staged changes in the primary block the merge even without path overlap — named and
   refused up front. Unstaged and untracked files do **not** block; the merge attempt is
   their gate. Nothing is ever stashed or reset to clear the way.
2. Rebase immediately before the merge, so the branch is a strict descendant and the
   merge cannot conflict.
3. Merge `--no-ff` from the primary.
4. `--verify`, if given, runs in the primary. On failure: stop, merge NOT reverted, say so.
5. **`merge-base --is-ancestor` gates all cleanup — never the merge's exit code.** A merge
   that never receives its branch argument merges the branch's configured upstream, prints
   `Already up to date`, and exits 0 having done nothing; cleanup at that point discards
   the work.
6. Only then remove the worktree and delete the branch.

No recovery path is reimplemented. On any non-zero exit both verbs stop, state what the
repository now looks like, and name the command that finishes the job — advisory mode
already leaves recovery manual, and a second conflict-resolver in PowerShell is where
work would get lost.

`gw drop` is new code with no backend equivalent (`task-recover --action release` demands
ancestry proof, which an abandoned branch by definition lacks). It refuses a dirty
worktree, then lists the commits not on the trunk and refuses again, both overridable with
`--force`. On the session path it detaches the slot **and deletes the `session-claim`
file** — the requirement the step-2 probe turned up; left behind, it makes the next
`task-start` refuse the session as held. `create` never writes a claim, so its absence on a
temp worktree is normal, not an error.

**Windows-specific:** both verbs `Set-Location` to the primary *before* removing a
worktree. `git worktree remove` fails with a sharing violation when the directory is a
live process's cwd, and standing in the worktree you are landing is the normal case.

Verified in a scratch repository (six cases) and against the real repository (three):

| Check | Result |
|---|---|
| `gw land` from inside a task worktree | merged `--no-ff`, worktree removed, branch deleted, shell moved to the primary |
| `gw land` with a dirty task worktree | refused, worktree intact |
| `gw land` with **staged** changes in the primary | refused by name, branch survived |
| `gw land` with **unstaged** changes in the primary | landed, and reported the loose path it landed over |
| `gw land` with a detached primary | refused |
| `gw drop` with unlanded commits | listed them, refused; `--force` then dropped and freed the worktree |
| `gw drop <session-branch>` (real repo) | detached session-2, removed `session-claim`, deleted the branch; `gw work --session session-2` immediately reallocated it |
| `gw land <session-branch>` (real repo) | delegated to `task-land`, `LANDED`, slot parked, claim cleared, branch deleted, `target_sha` unmoved — **run from a different worktree, confirming the automatic primary hop** |
| arg handling | `--bogus`, bare `--verify`, `gw drop --verify`, unknown selector, branch-less session all refused with the usage line |

**Two corrections that came out of testing.**

- The drop message originally said the commits stay "in the reflog for ~90 days". They do
  not: deleting a branch takes its reflog with it, and removing a worktree takes its
  per-worktree HEAD log too, so `git reflog` finds nothing. Confirmed — the commits survive
  only as unreachable objects. The message now says
  `git fsck --unreachable, then git branch <name> <sha>`.
- `git worktree remove` **does** delete ignored files, `.pixi/` included. So landing a
  temp worktree succeeds without `--force`, but it also destroys that worktree's
  provisioned environment — the `pixi install` + `pixi run install` cost from `gw temp` is
  paid again next time. That is inherent to disposable worktrees, and the reason a session
  slot is the cheaper home for anything you will come back to.

**The cost of `temp` you were not shown when choosing it:** a disposable worktree sits
outside the `task-*` lifecycle entirely — no claim, no session record, invisible to
`task-status` and `task-land`. That invisibility is precisely why `land` and `drop` each
needed a second, local implementation.

## Suggested order

1. ~~Help gating + `Show` field.~~ **Done.**
2. ~~`gw work` and `gw temp` — thin wrappers over `task-start --no-launch` and `create`.~~ **Done.**
3. ~~`gw land` with the automatic primary-checkout hop.~~ **Done.**
4. ~~`gw drop` — new code, needs the confirmation semantics above to be right.~~ **Done.**
