---
title: Separate engine bookkeeping from user-facing artifacts in the project tree
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
> **What** — Three related changes to project-tree ergonomics. (1) Collect content-addressed engine state into an engine bin per scope instead of leaving it beside results. (2) Rename `results/metric_plans/` for consistency with the scenario-side rename. (3) Flatten it, since it holds exactly one file per identity.
> **Why** — Owner request 2026-09-15, framed as user-friendliness. The project tree serves two audiences through one namespace: the engine, whose artifacts are content-addressed, immutable and named by 64-hex digests, and the reader, who wants a handful of tables and figures. Machinery currently sits beside results with no marker saying which is which.
> **Effort** — large, since it moves declared rule outputs and the canonical tree fixture.

> [!info] Relationship to [[t2609152040]]
> That item regroups `scenario_plans/` and `scenario_collections/` into `scenarios/`
> and renames the first to `requests/`. It is a **naming and grouping** change with an
> owner ruling already recorded. This item is the **audience separation**, and it is
> deliberately separable: either can land without the other. Where they overlap — the
> word `plan`, and where engine state belongs — this item defers to the ruling there.

## The reader's tree versus the engine's tree

Assessed 2026-09-15 against the canonical fixture in `tests/test_project_tree_inventory.py`.

Artifacts a reader opens: the metric tables under `results/metric_sets/<id>/`, the
figures under `data/`, `models/hydrology/wflow/evaluation/plots/`, the projections
`report.md`, the evaluation metrics, and the scenario table. Artifacts written purely
so the workflow can refuse a stale or mismatched run:

- `results/metric_plans/<id>/plan.json`
- `responses/response_inventory.json`
- `scenario_plans/<id>/plan.json` and `scenario_plans/<id>/initializations/`
- the dot-sentinels `.model_built`, `.outputs_configured`, `.model_final`,
  `.guard_ok`, `.model_reference_ok`

**The repo already has a convention for the second class and applied it inconsistently.**
Five dot-prefixed sentinels are in the canonical tree. A leading dot is this
repository's existing signal for engine state. The plan files and the response
inventory are the same category and simply never got the marker.

> [!warning] A leading dot hides nothing on Windows
> Explorer has no dot-hiding convention, and this is a Windows-primary project. So the
> benefit of a dot prefix here is *labelling*, not concealment, and grouping has to do
> the real work. That is why the recommendation below is a bin rather than a rename in
> place.

## Change 1 — an engine bin per scope

Collect the engine state of a scope into one directory the reader learns to ignore
once, instead of meeting it at three different depths.

```
experiments/<E>/
  .engine/
    metric_requests/<metric_request_id>.json
    response_inventory.json
  config/            # arguably reader-facing: what was run
  results/metric_sets/<metric_set_id>/...
  hydrology/wflow/...
```

**Alternatives considered.** Dot-prefixing in place, `results/.metric_requests/`, is
cheaper and leaves engine state scattered across depths; it was rejected because
grouping is the part that survives the Windows caveat. A curated index or report
pointing at reader-facing files was rejected *as a substitute* — it adds a surface
without reducing clutter — but it is **complementary**, and it is the only idea on the
table that also addresses the 64-hex directory names. Precedent exists:
`data/climate/projections/<CP>/report.md`. If both are wanted, do the bin first,
because an index is easier to write against a tree that has already split its
audiences.

**Open:** whether `config/` moves too. It holds `simulation.json`,
`model_reference.yml`, `response_request.json` and `simulator_settings.json`, which a
reader may legitimately open to answer "what did I run". Leaning: it stays.

## Change 2 — rename `metric_plans`

`results/metric_plans/` → `metric_requests/`, matching `scenario_plans/` →
`scenarios/requests/` in [[t2609152040]]. The identity inside is already
`metric_request_id` and the schema is `metric-plan/1`.

**This is a coupling, not an independent choice.** Renaming one side of the toolbox
and not the other leaves two words for one concept, in opposite directions, which is
worse than today's uniform-but-ambiguous `plan`. Rename both or neither.

## Change 3 — flatten it

`results/metric_plans/<id>/plan.json` holds **exactly one file**, verified 2026-09-15
in the code and on disk in `session-3/test_case/test_local`. Only two call sites build
the path. The directory is pure overhead.

Combined with change 2: `metric_requests/<metric_request_id>.json`. The `plan_` prefix
is redundant once the bin names what it holds.

**Do NOT make the scenario side symmetric.** `scenario_plans/<id>/` genuinely holds
four artifact families — the plan, the initialization receipts, and the weather
generator's config and output — so it keeps its directory. The rule is that shape
follows content: a lone file gets a filename, a family gets a directory. Today's
symmetry between the two is house style, not structure, and it is part of why the
metric side reads as though something is hidden in it.

**The argument against flattening**, recorded so it is not re-litigated: a directory
is a free extension point, and the scenario side shows siblings do sometimes appear.
Rejected because introducing a folder at the moment a sibling actually appears costs
one path literal and one glob, which is cheaper than carrying an empty container
against the possibility.

### Sites for change 3

- [ ] `blueearth_cst/experiment/metric_plan.py` — `write_metric_plan` (drops a
      `mkdir`) and `verify_metric_plan`
- [ ] `simulate_system.smk` — the `prepare_metric_plan` checkpoint output; the
      wildcard moves into the filename, and `wildcard_constraints` still applies
- [ ] `dev/scripts/check_baseline.py` — glob becomes `*.json`, **and see the trap below**
- [ ] `dev/scripts/semantic_tree_diff.py` — one regex
- [ ] `tests/test_project_tree_inventory.py`, `tests/test_check_baseline_scope.py`

> [!warning] One trap in `check_baseline.py`
> It identifies the plan by comparing `plans[0].parent.name` against the
> `metric_request_id` stored inside the file. That is an **identity assertion**, not
> path handling. Flattened it becomes a filename-stem check, so it must be rewritten
> rather than dropped.
>
> The atomic write is unaffected: `atomic_record` creates its temporary via
> `NamedTemporaryFile` with no extension, so a `*.json` glob will not see it.

## Progress

- [ ] Rule change 1's shape, and whether `config/` moves
- [ ] Rule changes 2 and 3 jointly with [[t2609152040]]'s open questions
- [ ] Implement, sweep references, update the canonical tree fixture
- [ ] `pixi run test-full` — this moves declared rule outputs and a `shared/` contract

## Refs

- [[t2609152040]] — the scenario-side regrouping and rename. Read its identity section
  before touching either plan surface: the plan-then-product split cannot be merged
  away, and `prepare_metric_plan` is a Snakemake **checkpoint** for exactly that
  reason.
- [[t2609152107]] — shortening the digest path segments. Independent of this item:
  that one decides how long the names are, this one decides where they live. It is
  also the only one of the three that addresses the 64-hex names directly, which the
  curated-index idea above was reaching for.
- `tests/test_project_tree_inventory.py` — the canonical tree. The reader-versus-engine
  split above is derived from it.
- `dev/reference/naming.md` — an internal rename record is required for every rename.
