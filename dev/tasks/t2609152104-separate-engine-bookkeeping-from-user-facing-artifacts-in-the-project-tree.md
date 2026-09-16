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

> [!done] Change 2 has LANDED; changes 1 and 3 remain
> Shipped 2026-09-16 with [[t2609152040]] and [[t2609152107]]. Note that
> [[t2609152107]] shortened every content-digest path segment to twelve
> characters, so the engine-bin paths sketched below are now
> `<12-hex>` rather than `<64-hex>`. That does not change this item's scope.

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

## Change 2 — rename `metric_plans` — DONE, landed with [[t2609152040]]

`results/metric_plans/` → `results/metric_requests/`. **Shipped on 2026-09-16 in
[[t2609152040]]'s migration**, on the owner's ruling, because it was never an
independent choice: renaming one side of the toolbox and not the other leaves two
words for one concept in opposite directions, which is worse than the
uniform-but-ambiguous `plan` it replaced. Rename both or neither, so both.

The DIRECTORY only. `plan.json`, the `metric-plan/1` schema and the metric-side
`plan_sha256` are untouched, because change 3 below renames that file anyway and
renaming it twice is churn.

Record: `dev/milestones/post-r12/migration_scenario-tree.md`, event 3.

## Change 3 — flatten it

Still open. Now reads `results/metric_requests/<id>/plan.json` after change 2
landed; the target `metric_requests/<metric_request_id>.json` is unchanged.

`results/metric_requests/<id>/plan.json` holds **exactly one file**, verified 2026-09-15
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

## Full-tree screen — 2026-09-15

Screened every family in the canonical fixture. **Three findings shape the result.**

**1. There are three dispositions, not one, and the dot prefix is the weakest.**
A file that is never written cannot clutter anything, so `temp()` beats a bin, and a
bin beats a rename — especially here, where a leading dot hides nothing on Windows.
Ordered by strength: *don't write it* (`temp()`), *collect it* (engine bin), *mark it*
(prefix).

**2. The repo already has two marker conventions and should not gain a third.**
A leading dot marks sentinel files (`.model_built`, `.guard_ok`,
`.model_reference_ok`). A leading underscore marks scratch bins (`logs/_parts/`,
`benchmarks/_parts/`). Both work. Any screen outcome should land in one of these, not
invent a new spelling.

**3. `simulate_system` declares only three `temp()` outputs**, all in
`experiment/rules/simulate_and_metrics.smk`: the model-reference sentinel, the per-run
forcing, and the per-run catalog. Everything else in the experiment tree persists,
including per-run warm states. AGENTS.md is explicit that omitting `temp()` on
per-realization netCDFs explodes disk on large grids, so the retention questions below were
the highest-value part of this screen. They are now ruled, and the answer is that
retention is deliberate throughout.

### Already correctly marked — no action

`models/.../.model_built`, `.outputs_configured`, `.model_final`,
`data/climate/historical/<KEY>/.guard_ok`, `experiments/<E>/.model_reference_ok`,
`logs/_parts/`, `benchmarks/_parts/`.

### Move to an engine bin

| family | what it is |
|---|---|
| `config/runs/journal.jsonl` | lifecycle journal, written outside any rule |
| `config/runs/invocations/<ts>.json` | per-invocation manifest |
| `data/climate/historical/<KEY>/basin_cells.csv` | the cell mask |
| `data/climate/projections/<CP>/summary/provenance.json` | provenance sidecar |
| `models/.../hydromt.log`, `hydromt_data.yml`, `hydromt_build_config.yml`, `hydromt_update_waterbodies.yml` | build machinery and its provenance |
| `models/.../run_default/outstate/outstates.nc` | warm state |
| `models/.../evaluation/run_metadata.json` | staleness sidecar |
| `experiments/<E>/responses/response_inventory.json` | already named in change 1 |
| `experiments/<E>/hydrology/wflow/output/run_<id>.log` | per-run simulator log |
| `scenario_collections/<id>/preparation_catalog.yml`, `ancillary/` | preparation inputs |
| `logs/dag/*.png`, `benchmarks/wf*_*.md` | diagnostics, dev-facing |

### Retention questions — RULED 2026-09-15 by tracing consumers

**Result: none of the five becomes `temp()`.** Every one is either re-read
downstream or was deliberately made persistent by a recorded decision. The
disk-blowup concern that motivated this section was unfounded, and the screen's
suspicion that the experiment tree retains carelessly is wrong. Retention here is
deliberate. What the trace did turn up is one stale inventory row.

| artifact | ruling | evidence |
|---|---|---|
| `outstates_run_<id>.nc` | **not produced at all** | see below |
| `run_<id>.toml`, `run_<id>.temporal.json` | **must persist** | re-opened on every metric run |
| `raw/*.nc`, `scalar/*.nc` | **keep, by prior decision** | promoted out of `temp()` on purpose |
| `data/spatial/hydrography.nc` | **keep** | cross-workflow input, not a seam scratch file |
| `run_<id>.csv` | **keep** | recorded artifact, digest re-verified |

**`outstates_run_<id>.nc` is never written by the current pipeline.**
`downscale_climate_forcing.py:376` pops `state.path_output` out of each per-run
TOML, and `write_states=False` is hardcoded at the only `measure_member_footprint`
call site. Contract HM-6b says so itself: "an unconsumed named sink — nothing
in-repo reads it", and "absent on the completed fixture". Confirmed absent on disk
in `session-3/test_case/test_local`, whose experiment output directory holds only
`run_NN.csv` and `run_NN.log`.

> [!bug] A stale row in the canonical inventory — FIXED 2026-09-15
> `tests/test_project_tree_inventory.py` carries
> `experiments/<E>/hydrology/wflow/output/outstates_run_001.nc` in its covered
> shapes. That fixture was taken from a clean run on 2026-08-06; the state output
> has since been suppressed. The row is now a shape no run produces. It makes the
> gate marginally permissive rather than wrong — undeclared-artifact detection is
> unaffected — but it has been dropped, with the reasoning left as a comment in its place.

**`run_<id>.toml` and `.temporal.json` are re-verified evidence, not publication
scratch.** `read_response_inventory` rebuilds each run's native selector — the CSV,
the TOML *and* the temporal JSON — out of the stored series entries, then re-runs
`build_response_inventory`, which opens the TOML with `tomllib` and re-reads the
temporal record, and refuses on any drift from what was stored. Every metric run
does this, `metrics_only.smk` included, since that entry point declares no producers
and recomputes from what is on disk.

**Correction to the screen above.** It called the asymmetry with the `temp()`
`run_<id>.yml` "unintended". That was wrong. The `.yml` is the hydromt data catalog
used only while downscaling, so it is correctly disposable; the other two are read
again on every later metric run. The asymmetry is the design working.

**`raw/` and `scalar/` were promoted out of `temp()` deliberately.**
`analyze_projections.smk:420` records it: the series files "stop being `temp()` and
become a persistent product, so they need an identity", and identity machinery was
built for exactly that. `raw/<key>.nc` is the basin slice on the source grid, which
is why a proposed extra gridded tier was rejected as a near-copy. They also cache
network fetches, so discarding them makes a re-run far more expensive.

**`hydrography.nc` is a cross-workflow input.** `shared/plot_map.py` reads the
elevation grid from it for the basin figure, and historical climate extraction uses
it as the downscaling DEM. "Seam intermediate" describes where it sits in the spatial
stage, not that it is disposable.

### Leave alone — reader-facing

`logs/wf*.log`, the materialized `config/runs/project_config_*.yml` and
`run_record.yml`, `config/runs/README.md`, `config/catalogs/`, `config/templates/`,
`config/basin_data/`, everything under `data/spatial/geoms/` and `plots/`,
`spatial_report.yml`, `location_registry.csv`, `extract_historical.nc`, the projection
`summary/` tables, `plots/` and `report.md`, `staticmaps.nc`, `wflow_sbm.toml`,
`staticgeoms/`, `inmaps_historical.nc`, `evaluation/performance_metrics.csv` and its
plots, `run_default/output_q.csv`, `results/metric_sets/<id>/*`, and the collection's
`scenario_table.csv`, `stress_test_lookup.csv` and `forcing/`.

### Deliberately not proposed

`collection.json` and `collection_intent.json` stay unmarked. They are a collection's
own manifest sitting inside its own directory, so a prefix would mark the directory's
purpose rather than distinguish anything within it. The whole tree relocates under
`scenarios/` in [[t2609152040]] regardless.

## Progress

- [x] Rule the five retention questions — done 2026-09-15; none becomes `temp()`
- [x] Drop the stale `outstates_run_001.nc` row from the tree fixture — done
      2026-09-15; `semantic_tree_diff`'s rule for it deliberately kept
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
