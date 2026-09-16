---
title: Shorten content-digest path segments to a fixed prefix, keeping full digests as identities
type: todo-item
status: backlog
branch:
effort: 2
area: project-tree
queue:
created: 2026-09-15
updated: 2026-09-15
---

> [!note] Overview
> **What** — Use a fixed-length prefix of the content digest as the directory-name segment, while every identity field stored inside a document stays a complete SHA-256. Adds a write-time sibling-uniqueness check as the collision policy.
> **Why** — Owner request 2026-09-15, asked as a general rule. Sixty-four-character directory names dominate the project tree and are the main reason it reads as machine output rather than as results.
> **Effort** — large. Twenty-nine sites, and it changes a load-bearing invariant rather than moving files.

> [!info] Sequencing with [[t2609152040]] and [[t2609152104]]
> This is its own item and does not change the scope either of those already has.
> But it breaks existing project trees exactly as [[t2609152040]]'s ruled hard break
> does, so **if both are done, do them in one migration**. Shipping two breaking path
> changes separately doubles the regeneration cost for no benefit.

## Scope — content digests only

**In scope:** the 64-hex SHA-256 digests used as path segments. `collection_id`,
`generation_request_id`, `metric_request_id`, `metric_set_id`, `simulation_id`.

**Out of scope, and not assessed:** `invocation_id` is a 32-hex UUID, not a content
digest, so truncating it has different consequences and buys less. Run ids
(`run_001`), experiment names and board task ids are already short. The owner's
request was a general rule for the long ids; it is being read as the digests.

## No prior ruling exists — absent, not adverse

`content_identity._digest()` refuses anything but a complete lowercase SHA-256, and
its docstring says "require the complete, lowercase identity rather than a display
handle". **That governs identity fields inside documents, not path segments**, and
this proposal does not touch it. A search of the R12 identity design for a rationale
on path-segment length returned nothing. So there is no precedent to overturn here,
and none to lean on either.

## The proposed rule

1. **A stored identity field is always the complete digest.** `_digest()` keeps
   refusing anything shorter. No document changes.
2. **A path segment is the first N hex characters.** Proposed N = 12, following git's
   convention; 16 is free insurance if preferred.
3. **Uniqueness is enforced at write time, per parent directory.** Before publishing,
   refuse if a *different* full identity already occupies that prefix among siblings.
   A prefix collision becomes a loud failure, never a silent merge.

## What actually weakens, and what does not

Four places currently assert that a directory name equals an identity. They do **not**
weaken equally, and the split is the real answer to whether this is safe.

**Three lose almost nothing.** `metric_plan.py:797`, `scenario_collection.py:640` and
`check_baseline.py:427` each compare the directory name against an identity
*recomputed from inputs in the same breath*. They become prefix comparisons, and the
full identity is still verified against recomputed content a line or two away. These
are belt over braces.

**One is a genuine loss.** `scenario_collection.py:1011`, in the store-inspection
path, calls `_sha256(path.name, "collection directory")` — it validates that a
*discovered* directory name is a full digest, with nothing else to check it against.
Under truncation that degrades to a length and charset check on a prefix, so the
"a discovered directory is self-describing" property goes away. **The write-time
sibling-uniqueness check from rule 3 is what replaces it**, and this item is not worth
doing without that check.

## Sizing the collision risk honestly

**These parents accumulate by design, so the bound is not one.**
`scenario_collections/` has an explicit inspection path that iterates the whole store
and a `delete_collection` to prune it, so many collections is the intended state. The
four inventoried trees happen to hold one each today (see [[t2609152040]]), which is a
fact about current use, not a cap.

At a realistic upper bound of a few hundred entries per parent, twelve hex characters
is forty-eight bits and the birthday probability is on the order of 1e-11. The risk is
not the reason to choose N. The reason to choose N is how much of a digest a person
can hold in their eye while comparing two directory names, which argues for the
shorter end.

## Sites

Twenty-nine matches for the 64-hex constraint or length check, across eight files:

- [ ] `blueearth_cst/experiment/content_identity.py` — keep `_digest()` strict; add
      the path-segment helper and the sibling-uniqueness check here so there is one
      definition
- [ ] `blueearth_cst/experiment/scenario_collection.py` — includes the one genuine
      weakening at line 1011
- [ ] `blueearth_cst/experiment/simulation_record.py`
- [ ] `blueearth_cst/experiment/metric_plan.py`
- [ ] `blueearth_cst/experiment/collection_resolution.py`
- [ ] `generate_scenarios.smk`, `simulate_system.smk` — `wildcard_constraints` go from
      `[a-f0-9]{64}` to the chosen length
- [ ] `dev/scripts/check_baseline.py`, `dev/scripts/semantic_tree_diff.py`
- [ ] `tests/` — the canonical tree fixture, `test_sealed_records.py`, and the
      identity tests

## Progress — LANDED 2026-09-16 on `chore/post-r12`

- [x] Rule N, and rule whether this ships in [[t2609152040]]'s migration
- [x] Implement, with the sibling-uniqueness check landing **before or with** the
      truncation, never after
- [x] `pixi run test-full`, plus `check_baseline.py check` — this touches identity

**N = 12, and it needed no ruling.** `SHORT_DIGEST_CHARS` already stood at 12 in
`blueearth_cst/shared/provenance.py`, set by [[t2609151643]] for the WF3
run-record filenames, and its docstring already argues against a second length
constant. Reused rather than restated, so the directory name, the log filename,
the benchmark filename and `semantic_tree_diff`'s rows cannot drift apart.

**Bundled with [[t2609152040]]** on the owner's ruling of 2026-09-16 — one
migration, one regeneration of the four populated trees.

The sibling-uniqueness check landed FIRST, in its own commit (`9b6733a5`), ahead
of the truncation (`009ecc50`). `claim_identity_segment` raises `SegmentCollision`
on a prefix held by a different complete identity; `list_collections` now reads
the full identity out of `collection_intent.json` and checks the name is its
segment; `delete_collection` confirms the occupant before removing anything.

Two sites in this note's list turned out NOT to be path segments and are
unchanged: `simulation_record.py`'s `simulation_id` lives inside
`config/simulation.json`, and `invocation_id` was already out of scope.

Rename record: `dev/milestones/post-r12/migration_scenario-tree.md`.

## Refs

- [[t2609152040]] — the scenario-tree rename, whose hard-break ruling this should
  share a migration with.
- [[t2609152104]] — the audience separation. Independent of this: that one decides
  *where* engine state lives, this one decides *how long its names are*.
- `blueearth_cst/experiment/content_identity.py` — `_digest()`, and the natural home
  for the path-segment helper.
