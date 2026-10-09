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
> **Why it matters** — Sessions must not traverse main during cleanup or fail tests because
> board snapshots are excluded.
> **What it takes** — Update coordination scripts, policy, links and docs;
> verify without changing other sessions.

## Progress

- [x] Promote closed plot evidence verbatim and repoint links — main 8327babe.
- [x] Reject unstable reference links — f0d4f31f; synthetic cases failed red, then passed.
- [x] Retire junction hooks and harden named navigation — 93a170cd; preview and controls passed.
- [x] Limit primary maintenance — afb1e3e4; candidate guard decisions passed; effective at landing.
- [x] Document ownership and repair wrapper drift — f85a0f36; focused checks passed.
- [x] Verify candidate f85a0f36 — test-fast passed; evidence retained through approved landing.

## Work location

- Owner: session-1; branch: feat/worktree-policy-improvements;
  implementation commit: f85a0f36; ready for landing.
- Implementation: session-1 :: dev/scripts/, tests/test_activation_links.py, coordination docs and policy.
- Coordination: main :: dev/tasks/t2610091206-worktree-coordination.md.
- Scratch: session-1 :: .tmp/scratchpad/worktree-coordination-r2/; retained through approved landing.
- Verification: f85a0f36; Windows 11 / PowerShell 7 / Pixi; see evidence below.
- Next action: owner approves landing and performs other-session cleanup; no landing or push executed.

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

## Verified candidate and evidence

Tested SHA: `f85a0f3697f2fbde07dab97c2ebed72907266c5f`; synchronized with main `d1f3b2e9` before final gates.
Scope `rapid`, numerical claims `unaffected`; no workflow configs or project outputs changed.
Environment: Windows 11; PowerShell 7.6.6; Python 3.12.13; Git 2.54.0.windows.1; Pixi 0.70.2.
The machine-readable gate record pins commit, tree, Python environment and pixi.lock identity.
Evidence root: session-1 :: `.tmp/scratchpad/worktree-coordination-r2/`.
Retain logs, probes and gate record through approved landing; the abandoned run was only read.

- Focused checks: `pixi run pytest tests/test_activation_links.py tests/test_todoboard_wrapper.py -q
  --basetemp=.tmp/scratchpad/worktree-coordination-r2/b56-fixtures` — 16 passed.
- F-links: B1's four existing/missing task/review cases failed before the fix (4 failed, 8 passed).
  The first sandbox run had fixture ACL errors; `b1-red-approved.log` holds the actual red proof.
  `python -B -c "import sys; sys.path.insert(0,'dev/scripts'); import check_activation as ca;
  print(ca.check_links())"` returns `[]` in sparse session-1 and main. The candidate checker also
  returns `[]` when pointed at main's reference tree (`links-final.log`).
- Link decision: only two inline reference citations reach reviews. Preserve Phase A's exact
  source/target pairs for plot verification, reject every new review link, and require both targets
  to exist. The retention rule blocks pruning until those citations and exceptions are updated.
  Moving the evidence again is outside this task's authority.
- F-junction: confirmed Junction -> main/dev; `cmd /c rmdir dev\00-current-board-main` removed
  only session-1's link. Rebase briefly ran main's old hook and recreated it; it was rechecked and
  removed again. Final `git clean -n -d -X` has no junction row; the ignored-files listing is empty.
  Same-branch `git switch feat/worktree-policy-improvements` exited 0, emitted the normal Git line
  and `Session ok` only, and recreated no junction (`same-branch-switch.log`).
- F-preview: `pwsh -NoProfile -File dev/scripts/setup-worktree-navigation.ps1` changed no status,
  navigation directory/file timestamp or shortcut hash in any of the four real worktrees.
  `preview-probe-final.log`, `preview-before.json` and `preview-after.json` retain the comparison.
  Scratch-only controls put a valid root first, then a dirty root: all targets were preflighted
  before writing; the dirty root stayed untouched, the valid root continued, sparse exclusion
  affected only its named target, stale shortcuts survived, and failures summarized with exit 1.
  Unnamed sparse exclusion failed before writing (`navigation-probe.log`).
- Own setup: `pwsh -NoProfile -File dev/scripts/setup-worktree-navigation.ps1 -Apply
  -ExcludeSnapshots -Worktree session-1` exited 0. No other real worktree was modified.
- F-guard: parser accepted `dev/tasks`, `dev/TODO.md`, `dev/LOG.md`. Candidate decisions were
  allow for task note/TODO/LOG and deny for todoboard.py/plot-style.md/run_workflow.py.
  `guard-probe.py` uses the unchanged upstream parser and guard with candidate maintenance scopes
  supplied for main; repository and target resolution remain real. Live main still permits the
  two dev implementation paths because B4 is unlanded (`guard-results.json`). Repeat live-main
  decisions at approved landing; this is candidate proof, not a claim that main already changed.
- F-ownership: `python -B dev/scripts/todoboard.py worktrees` exited 1 with the output below.
  Session-2 and detached session-3 have no tracked allocation; parked branches have no worktree.
  These unrelated rows remain unchanged. `session-check` reported `Session ok` (`session-check.log`).
- Wrapper: infrastructure fallback, BRAIN_INFRA_ROOT override, missing-bundle hint and refusal
  of a bad explicit TODOBOARD_SKILL_DIR passed (`wrapper-probe.log`).
- Final gates: `pixi run lint` passed; `pixi run format-check` passed (432 files formatted).
  `pixi run test-fast` — 4013 passed, 17 skipped, 1 xfailed, 8645 warnings in 290.04s (0:04:50).
  One run only, logged in `test-fast.log` and `gates.json`.
  `PYTEST_ADDOPTS=--basetemp=.tmp/scratchpad/worktree-coordination-r2/fast-fixtures` kept fixtures local.
  Skips: five Linux-only controls, eleven unavailable local P0/lab parity cases and one opt-in E2E
  case. The expected failure pins hydromt's known preprocess serialization defect; no task checks skipped.
  `test-full`, `test-e2e` and baselines are not owed for developer tooling and documentation.
- Deletion: `.githooks/post-merge` only; setup-board-view.ps1 retains sparse exclusion only.
  No junction creation or attrib logic remains; post-checkout retains session-check and `exit 0`.

```text
  tracked feat/worktree-policy-improvements — t2610091206
  worktree .
  untracked chore/tmp-cleanup
  worktree C:/Users/taner/workspace/.worktrees/blueearth_cst/session-2
  untracked (detached)
  worktree C:/Users/taner/workspace/.worktrees/blueearth_cst/session-3
  missing feat/model-upgrading — t2609281102
  missing feat/scope-shipped-sample-dataset — t2608191733
```

Board check already had seven errors in two unrelated notes and `wf0-lab-integration/`.
The updated note must add no structural errors; its retained evidence explains its length warning.

## Other-session commands — owner action only (Gate 2)

Both links were read-only verified as Junction -> main/dev. Recheck before removal; use the updated
session-1 script until landing. Sparse setup requires each target to be clean. Old branches' hooks
may recreate links on checkout until their hook changes are integrated.

```powershell
cmd /c rmdir "C:\Users\taner\workspace\.worktrees\blueearth_cst\session-2\dev\00-current-board-main"
cmd /c rmdir "C:\Users\taner\workspace\.worktrees\blueearth_cst\session-3\dev\00-current-board-main"
pwsh -NoProfile -File dev/scripts/setup-worktree-navigation.ps1 -Apply -ExcludeSnapshots -Worktree session-2
pwsh -NoProfile -File dev/scripts/setup-worktree-navigation.ps1 -Apply -ExcludeSnapshots -Worktree session-3
```

Navigation commands above run from session-1. Before each removal, `Get-Item -LiteralPath <link> -Force`
must still report Junction with main's `dev/` target. Never use recursive deletion or git clean.

## Additional improvement candidate captured

- git-workflow: guard-hook resolves a junction into main, then tells an already allocated session
  to start another task. Report lexical/resolved paths and direct implementation edits to the
  branch-local path. Measured with session-1/dev/00-current-board-main/scripts/todoboard.py before
  removing the junction; relevant across linked checkouts and shared-directory links. Placement:
  native edit-tool guard diagnostics. Upstream files were not modified during Phase B.

## Approved upstream follow-up

Implemented in infrastructure commit `8327ab3346757c748779cadb8b70fd957ecfbf94` after owner approval.
Canonical `infrastructure:artifacts/skills/git-workflow/` guard and hook guidance now report
lexical/resolved targets and direct an existing linked caller to a safe branch-local path.
Allow/deny decisions are unchanged. The fix is unreleased under manual cadence.

- Red/green: all four real-junction cases failed before the fix, then passed.
- Both test trees: `conda run --no-capture-output -n brain python -m pytest
  artifacts/skills/git-workflow/tests artifacts/skills/git-workflow/scripts/tests -q
  --import-mode=importlib` — 337 passed; the run also set task-local basetemp and cache_dir.
- Touched-file Ruff, compilation and infrastructure pre-commit covering tests passed.
- Installed fallback bundles were refreshed from the tested canonical guard and verified.
- Strict status still reports inbox and existing cached agent-audit findings; runtime is current.
- Evidence: infrastructure :: `.tmp/scratchpad/guard-link-diagnostics/` and session-1 ::
  `.tmp/scratchpad/guard-link-diagnostics/`; retain through approved source-task landing.
- No release, push or CST landing occurred. Skill prose was checked on disk; fresh-session
  instruction uptake was not tested with a same-session subagent.
