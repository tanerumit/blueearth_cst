---
title: "simulation.json cannot be a baseline target: it records an absolute path and a code fingerprint"
type: todo-item
status: backlog
effort: 1
area: baseline / manifest
origin: t2609171700 WF3+WF4 regeneration, 2026-09-17
queue: 1
created: 2026-09-17
updated: 2026-09-17
---

> [!note] Overview
> **What** — `TARGETS` carries `("simulate_system", "yaml", "{exp_dir}/config/simulation.json")`.
> That document records an ABSOLUTE PATH and a CODE FINGERPRINT, so it differs by
> worktree and by branch by construction. A manifest entry for it can only ever
> pass in the exact worktree, on the exact branch, that recorded it.
> **Why it matters** — every other checkout gets a `FAIL` that says nothing about
> whether any number moved. A gate that cannot pass is not a gate; it trains the
> reader to discount a real failure.
> **Effort** — small. The decision is what to do, not how.

## Evidence, measured 2026-09-17 after the WF3+WF4 regeneration

`check_baseline check` unscoped on `chore/post-r12@42943f9e`, against a tree
regenerated in this worktree from `project_config_baseline.yml`:

```
build_model            OK   - 2 target(s) match manifest
analyze_projections    OK   - 3 target(s) match manifest
generate_scenarios     NOT CHECKED - no targets in scope
simulate_system        FAIL - 1 target(s) differ      <- simulation.json
```

`simulate_system` has two targets. **`q_indicators.csv` MATCHED**; only
`simulation.json` differs. The numbers reproduced — this is a provenance
document disagreeing, not a result.

Diffing this worktree's `simulation.json` against the primary checkout's
successor tree: **7 of 20 leaf keys differ, and not one of them is a result.**

| key | why it differs |
|---|---|
| `collection.manifest_path` | **an absolute path containing the worktree name** |
| `collection.collection_id` | the collection was regenerated here |
| `collection.collection_revision` | as above |
| `model.model_digest` | this worktree's WF1 model is from Aug 29 |
| `simulator_adapter_code.sha256` | **the R12 code identity — this branch carries the console_style split, the primary does not** |
| `simulation_id` | derived from the above |
| `response_inventory_sha256` | derived from the above |

Two of these — the absolute path and the code fingerprint — are *designed* to
vary. The code fingerprint varying across branches is the R12 contract working
correctly, not a defect.

Note also that the manifest's recorded digest (`2c4f8f48…`) matches NEITHER
tree: not this one, and not the primary's either. Nothing on disk anywhere
satisfies this entry.

## The decision this needs

1. **Drop `simulation.json` from `TARGETS`.** The baseline manifest answers
   "did the numbers move"; this file answers "which inputs produced them", which
   is what the immutability guards and the drift check already enforce at run
   time (rule 4.02 `check_model_reference` passed cleanly in this very run).
   **Recommended** — it removes an entry that cannot pass rather than one that
   is merely inconvenient.
2. **Fingerprint a SUBSET of its keys** — the result-bearing ones — instead of
   the whole document. More faithful to the intent, but it needs someone to
   rule on which keys are result-bearing, and the honest answer may be "none of
   them, that is what `q_indicators.csv` is for".
3. **Keep it and accept a permanent FAIL.** Not recommended, for the reason in
   the overview.

Do not simply `record` the current value. That would make this worktree's
absolute path the new truth and move the failure to every other checkout.

## Related

- [[t2609171700]] — the regeneration that exposed this.
- The "recorded by another branch" warning in `check_baseline` fired on this run
  and was, for once, exactly right: the tree does carry another branch's code
  identity. That is evidence the warning earns its place, which
  [[t2609171700]] had left as an open question.
