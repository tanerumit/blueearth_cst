---
title: test_wg3_integration compares a full collection_id against a 12-hex directory name
type: todo-item
status: backlog
effort: 1
area: wf3 / interchange contracts
origin: post-R12
queue: 1
created: 2026-09-17
updated: 2026-09-17
---

> [!note] Overview
> **What** — `tests/test_interchange_contracts.py::test_wg3_integration` selects the
> generation request for the consumed collection with
> `json.loads(p.read_text())["collection_id"] == collection.name`. `collection_id`
> in `request.json` is the FULL 64-hex id; `collection.name` is the directory
> name, which is now the 12-hex `identity_segment(...)`. A prefix never equals the
> full value, so the list is always empty and the test fails
> `assert plans, "no generation plan for the consumed collection"`.
> **Why it was invisible** — the standing fixture was pre-R12, so
> `_successor_artifacts()` hit its `pytest.skip` and took the whole module with it.
> The comparison has presumably been wrong since the collection directory moved
> from `scenario_collections/<64-hex>/` to `scenarios/collections/<12-hex>/`.
> **Found** — 2026-09-17, first run of this module against a successor tree
> (93 passed, this one failed).

## Evidence

Regenerated fixture in the PRIMARY checkout, 2026-09-17:

```
collection dir                     3fe44c754c5c
request.json  collection_id        3fe44c754c5cb6bd47f2f98bb1f0497e52efc710143174b603a2d86bad29da0c
request dir                        a8c10a7f296b
```

The request IS the one for this collection — the directory name is a prefix of
the id it records. Only the equality is wrong.

## The decision this needs

Not "fix the test" on sight. The question is what `identity_segment` truncation
means for LOOKUP, and it has two defensible answers:

1. Compare against the full id, read from the collection manifest
   (`collection.json`) rather than reconstructed from the directory name.
   Treats the short segment as a display/path affordance only.
2. Match on prefix, making the short segment a legitimate key.

This is the same shape as the ruling already taken on 2026-09-15 when the
`benchmarks/wf[34]_benchmarks_*` inventory row was split: short hex is a SUBSET
of the longer grammar, so an equality or a glob written against one silently
accepts or rejects the other. That one needed an owner ruling; so does this.

Prefer (1) unless prefix lookup is wanted elsewhere — a prefix match invites
exactly the subset confusion the benchmark split was called to remove.

## Why it cannot be verified in an arbitrary worktree

The fix must be verified where the fixture is successor-shaped. As of
2026-09-17 that is the PRIMARY checkout and `session-3` only; every other
worktree still carries a pre-R12 `test_case/test_local` and will SKIP this
module rather than exercise the fix. Confirm
`test_case/test_local/experiments/experiment/config/simulation.json` exists
before trusting a green run here.

Related: [[t2608071201-r10-12]] (the model-reference drift guard and its
accepted re-record procedure), which is the other guard a fixture regeneration
trips.
