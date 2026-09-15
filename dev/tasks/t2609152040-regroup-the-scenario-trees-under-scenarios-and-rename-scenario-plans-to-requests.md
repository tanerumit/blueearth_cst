---
title: Regroup the scenario trees under scenarios/ and rename scenario_plans to requests
type: todo-item
status: backlog
branch: chore/scenario-tree-naming
effort: 2
area: project-tree
queue:
created: 2026-09-15
updated: 2026-09-15
---

> [!note] Overview
> **What** — Move `scenario_plans/` and `scenario_collections/` to `scenarios/requests/` and `scenarios/collections/` under the project tree. Directory layout only; no identity, digest or schema change is in approved scope.
> **Why** — Owner request 2026-09-15. Two sibling top-level trees of 64-hex directories, with nothing in either path saying which is the ask and which is the product, and `plan` already means something else one level down in `experiments/<id>/results/metric_plans/`.
> **Effort** — large, because the path literals participate in containment guards and every existing project tree becomes unreadable.

## Why the two trees cannot simply merge

Recorded here because the next reader will otherwise re-derive it, and because two
plausible-sounding simplifications are already ruled out by it.

The project carries **three identities, not two**, and they answer different questions.

| identity | over what | where |
|---|---|---|
| `generation_request_id` | the ask: workflow settings, provider code, resolved catalog paths, selected climate source, store dir, water year start, template path | directory name under `scenario_plans/` |
| `collection_id` | the meaning: scenario spec, scenario-semantics digest, provider name and revision, unit id capacity, plus content digests of generation config, source inventory, provider code, environment and preparation context | directory name under `scenario_collections/` |
| `collection_revision` | the product: the produced-byte inventory in declared order | field inside `collection.json` |

`content_identity.py` defines the second and third; the first is `content_sha256(request)`
in `collection_resolution.py`.

**Ordering is the binding constraint.** `generation_plan.py:156` computes the plan
path from config alone, so Snakemake can name `plan.json` at DAG-construction time.
The collection identity does not exist at that moment — it needs a hashed source
inventory and a preparation context, which require the sources to be staged first.
A plan therefore can never live at a collection-named path.

**The mapping is many-to-one on purpose.** Move a catalog to a different absolute
path, or change a setting carrying no semantic weight, and the request digest changes
while the collection identity does not. That is the reuse path through
`reuse_collection`. The reverse is pinned: one request digest binds to exactly one
collection, and `verify_scenario_plan` refuses when live source bytes drift from the
planned inventory.

**Mutability differs.** A collection is immutable once ready and raises
`ImmutableCollectionError` on rewrite. A plan is atomically replaced on every
invocation and its `generation/` subtree is scratch. Separate trees mean plans can be
wiped safely and collections never.

### Alternatives rejected

- **Embed scenarios under `experiments/<experiment_id>/`** (owner's opening proposal,
  2026-09-15). Rejected: it makes the model-independent artifact a child of a
  model-dependent one, inverting the WF3/WF4 dependency, and a second experiment on
  the same scenarios must then either duplicate the forcing netCDFs or reach sideways
  into a sibling experiment's directory. The one-collection-per-experiment premise is
  not true in general.
- **One directory per request, collection nested inside.** Same duplication objection.
- **Human-readable directory names.** The directory name *equals* the collection
  identity, asserted in two places plus the confined-path check. Not worth breaking.
- **A merged single digest.** Blocked by the ordering constraint above.

Note that the plan-then-product shape is not a one-off: experiments already pair
`results/metric_plans/<digest>/` with `results/metric_sets/<digest>/`. Keeping the
split preserves a symmetry the repo already repeats — which is the other half of why
`plan` is the wrong word here and `request` is the right one.

## Target layout

```
scenarios/
  requests/<generation_request_id>/
    plan.json
    initializations/<invocation_id>.json
    generation/config/weathergen_config.yml
    generation/output/resampled_dates.csv
  collections/<collection_id>/
    collection.json
    collection_intent.json
    scenario_table.csv
    stress_test_lookup.csv
    preparation_catalog.yml
    forcing/run_NNN.nc
    ancillary/dem/static.nc
```

`requests/` is chosen over `builds/`, `generations/` and `intents/` because the code
already uses that word: the digest field is `generation_request_id` and the schema
string is `generation-request/1`. `intents/` is actively wrong — the intent is a
distinct object inside the plan, and the collection identity is computed over it.

## The riskiest edit

`scenario_collection.py:924` builds `f"scenario_collections/{plan['collection_id']}"`,
passes it through `confined_path`, and then asserts the result equals the same
string joined onto the project root. `_initialization_path` does the same for
`scenario_plans/<request_id>/initializations/`. **These are path-containment guards,
not cosmetic string building.** Change the literal and the assertion in lockstep, in
one edit each, or the guard silently stops guarding.

## Compatibility

Every project tree written under the old paths becomes unreadable to the new code.
Decide and record which of these applies before starting:

- hard break plus regeneration, or
- a compat read path that accepts the old locations for one release.

Two complications for the hard-break option. `test_case/test_local` is **untracked and
shared across worktrees**, so the tree flips for every worktree at once and any branch
without this change starts failing against it. And `dev/baseline/manifest.json` plus
`dev/scripts/check_baseline.py` read into these trees, so a re-record may be owed —
AGENTS.md prices that at a full run.

`naming.md` distinguishes two artifacts here. An **internal rename record** at
`dev/<milestone>/migration_<topic>.md` is *required* for every rename, carrying the
old-to-new table, the machinery to update and the gate evidence. A **user-facing
guide** at `docs/migration-<milestone>.md` is optional and owed only if users must
act — which they must, if the hard-break option is taken and anyone holds an existing
project folder. `docs/migration-workflow-names.md` is the precedent for that guide.

## Reference sweep

AGENTS.md requires every live reference fixed in the same commit. Counted 2026-09-15,
excluding `dev/milestones/` and `dev/working/`:

- [ ] `generate_scenarios.smk`
- [ ] `blueearth_cst/experiment/scenario_collection.py` — includes both containment guards
- [ ] `blueearth_cst/experiment/collection_resolution.py`
- [ ] `blueearth_cst/experiment/generation_plan.py`
- [ ] `dev/scripts/semantic_tree_diff.py`
- [ ] `dev/scripts/check_baseline.py`
- [ ] `tests/test_project_tree_inventory.py` — the canonical tree fixture
- [ ] `tests/test_collection_resolution.py`
- [ ] `tests/test_interchange_contracts.py`
- [ ] `tests/test_check_baseline_scope.py`
- [ ] `README.md`
- [ ] `docs/wf3-retained-handoffs.md`
- [ ] `docs/migration-workflow-names.md`
- [ ] `dev/reference/workflows/rule-index.md`
- [ ] `dev/reference/contracts/weather-generator-seam.md`

## Progress

- [ ] Rule the two open questions below
- [ ] Rule the compatibility question above
- [ ] Move the trees and sweep the references
- [ ] Update the canonical tree fixture and re-run `pixi run test-full`
- [ ] Write the required internal rename record under `dev/<milestone>/`

> [!question] Open — NOT in approved scope
> The owner approved the **directory** rename on 2026-09-15. These were raised in
> the same discussion but not ruled on, and they are contract changes rather than
> moves:
>
> 1. **`plan.json` → `request.json`.** Leaving it means the path reads
>    `scenarios/requests/<id>/plan.json`, reintroducing the word one level down.
> 2. **`scenario-plan/1` → `scenario-request/1`** and **`plan_sha256` →
>    `request_sha256`.** `plan_sha256` is a self-referential digest over the plan
>    minus itself, and it is copied into the initialization receipts compared by
>    `_job_collection_claim`, so renaming it invalidates in-flight receipts. It is
>    also read by `check_baseline.py`.
>
> Doing the move without these is still a net improvement, just an inconsistent one.

## Refs

- `blueearth_cst/experiment/content_identity.py` — `collection_id`,
  `collection_revision`, `scenario_semantics_sha256`. The identity table above is
  derived from it.
- `blueearth_cst/experiment/collection_resolution.py` — `scenario_plan`,
  `write_scenario_plan`, `verify_scenario_plan`. The request-to-collection binding.
- `dev/reference/naming.md` — lowercase `snake_case` for locally minted directory
  names; migration-guide bar at §110.
- `docs/migration-workflow-names.md` — precedent for a user-facing rename guide.
