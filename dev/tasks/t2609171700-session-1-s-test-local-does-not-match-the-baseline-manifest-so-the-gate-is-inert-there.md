---
title: session-1's test_local does not match the baseline manifest, so the gate is inert there
type: todo-item
status: backlog
effort: 1
area: baseline / dev tree
origin: found while renaming the config snapshots, 2026-09-17
queue:
created: 2026-09-17
updated: 2026-09-17
---

> [!done] The two REPORTING defects are fixed (2026-09-17); the TREE remains
> Problems 2 and 3 below are done. `check` is now three-valued: `0` the compared
> targets match, `1` the tree differs, `2` **nothing was compared**. An empty
> scope prints `NOT CHECKED` naming the scope and the figure exclusion, and a
> fixture the gate cannot resolve is a diagnosis on stderr instead of a
> traceback out of `main`. Covered by `tests/test_check_baseline_scope.py` and
> documented in the module docstring and `dev/reference/validation-ladder.md`.
>
> Fixing them changed two provenance tests that had asserted `rc == 0` while
> monkeypatching `TARGETS` to `[]` -- they were pinning "advisory does not
> change the verdict" against a check that compared nothing. They now assert
> the NOT-CHECKED code and, crucially, `rc != 1`; a new
> `test_a_warning_does_not_flip_a_real_pass` carries the original claim against
> a fixture with one real target, so the guarantee is still witnessed.
>
> **Problem 1, the divergent tree, is untouched and is why this item stays
> open.**

> [!note] Overview
> **What** — Restore a baseline-checkable `test_case/test_local` in `session-1`, and fix two ways `check_baseline` reports a non-check as something other than a failure.
> **Why** — `check_baseline` currently proves nothing in this worktree: two WF2 data targets differ, the WF4 targets are absent, and the unscoped check raises a traceback instead of failing.
> **Effort** — small for the two reporting defects; the tree restore is a long run.

## Measured 2026-09-17, on `chore/post-r12@3f4334aa`

| scope | result |
|---|---|
| `--workflow build_model` | `OK - 2 target(s) match manifest` |
| `--workflow analyze_projections` | **FAIL — 2 targets differ** (both `cmip6_change_factors_*.csv`) |
| `--workflow generate_scenarios` | `OK - 0 target(s) match manifest` |
| `--workflow simulate_system` | **Traceback** |
| no `--workflow` | **Traceback** |

So one scope passes, one honestly fails, and **two report something that is not
a check result at all**.

## Three separate problems

### 1. The WF2 data targets diverge (the real one)

```
cmip6_change_factors_annual.csv   c69d6e0c… vs manifest 1e61f97e…
cmip6_change_factors_monthly.csv  833353ea… vs manifest bab48eab…
```

Unrelated to the config-snapshot rename that found it — those are WF2 data
targets, and the rename touched no WF2 data rule. `test_case/test_local` is
**per-worktree** (verified 2026-09-15: six independent real directories, no
junction or symlink among them), so this is a property of `session-1`'s copy,
not of the branch. Other worktrees may or may not have it; nobody has checked.

The manifest was recorded by `feat/wp3-improvements@72553688 +dirty`, and
`check` already prints a warning saying a pass may mean the tree matches another
branch's code. That warning fires on every run and so has stopped carrying
information.

### 2. `OK - 0 target(s) match manifest` is a vacuous pass

`generate_scenarios` has no non-figure targets in `TARGETS`, so the scope
reports OK having compared nothing. A gate that prints OK over an empty set
violates the repo's own "no silent caps" rule — a tool that bounds its own
coverage must report what it dropped. **Zero targets should not be `OK`**; it
should say so, and probably exit non-zero.

### 3. The unscoped check raises instead of failing

```
ValueError: baseline requires exactly one retained metric plan, found 0;
select a dedicated baseline fixture (legacy tables are not a successor baseline)
```

`resolve_metric_set_dir` raises during target resolution, so `check_baseline.py
check` with no arguments — the form AGENTS.md's ladder tells you to run — dies
with a traceback rather than a FAIL. The message itself is good; the delivery
makes a missing-fixture condition look like a broken tool, and it takes the
whole run down including the scopes that would have reported cleanly.

## Not a problem, and worth recording because it looks like one

The two renamed snapshot entries **verify green against their untouched recorded
values.** `fingerprint_yaml` parses the document and hashes sorted-key JSON, so
the 2026-09-17 move changed the path and the byte layout but not the digest.

**A raw byte comparison of those files answers a different question.** During
this work a byte diff showed the old flat copies carrying the retired
`run_stress_test` key and that was read, wrongly, as "the manifest entries are
stale". They were not; the stale thing was the on-disk flat file the rename
orphaned. See `dev/baseline/provenance.md`.

## Options for the tree

1. **Re-seed from a worktree whose tree does match**, if one exists. Cheapest,
   and nobody has yet checked whether one does. Note the seeding hazard: a copy
   made before R12 carries a predecessor tree.
2. **Regenerate**: WF1 (`--notemp`, required — rule 1.14 declares
   `run_default/output.csv` as `temp()` and it is the manifest's wf1 discharge
   target), WF2, WF3, WF4 against `project_config_baseline.yml`, then
   `record` if the differences are accepted. R14's comparable rebuild took
   5m07s + 2m10s + 9m51s for three workflows.
3. **Accept and re-record** the two WF2 values without investigating. **Not
   recommended** — nobody has established *why* they differ, and recording makes
   an unexplained change the new truth.

## Progress

- [ ] Check whether any other worktree's `test_local` passes `check_baseline check`
- [ ] Decide between re-seed and regenerate
- [x] Fix the zero-target vacuous OK (report it, do not call it a pass)
- [x] Make a missing metric-set fixture a FAIL, not a traceback
- [ ] Re-check whether the recorded-by-another-branch warning still earns its place
