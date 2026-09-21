# Migration — the scenario tree moves, and digest directories get shorter

> Historical R12 migration guide. For a fresh output project, use the current
> launcher commands in [README.md](../README.md); WF0--WF2 now publish
> `config/runs/<workflow>/run_record.yml` with exact `sources/` archives.

Post-R12 changes the layout of generated project folders. **There is no
compatibility read path.** A project folder written before this change is not
readable by this code, and the workflows will report missing state rather than
silently ignoring it.

If you hold no project folder you care about, there is nothing to do. Run the
workflows and they write the new layout.

## What changed under `project_dir`

```
  scenario_plans/<64-hex>/plan.json
→ scenarios/requests/<12-hex>/request.json

  scenario_collections/<64-hex>/
→ scenarios/collections/<12-hex>/

  experiments/<name>/results/metric_plans/<64-hex>/plan.json
→ experiments/<name>/_engine/metric_requests/<12-hex>.json

  experiments/<name>/responses/response_inventory.json
→ experiments/<name>/_engine/response_inventory.json

  config/runs/journal.jsonl, config/runs/invocations/
→ config/runs/_engine/...

  models/hydrology/wflow/evaluation/run_metadata.json
→ models/hydrology/wflow/run_metadata.json

  experiments/<name>/results/metric_sets/<64-hex>/
→ experiments/<name>/results/metric_sets/<12-hex>/

  config/runs/project_config_<workflow>.yml
→ config/runs/<workflow>/composed_config.yml
```

**The last one landed later (2026-09-17) and is the only entry you must act on
separately.** Each workflow wrote two files describing the same run at two
different depths — the snapshot flat in the bin, the record one level down. They
now sit together, and the filename drops the workflow name because the directory
carries it.

This migration command applies only to outputs from its original release.
Fresh projects use the captured `run-record/2` archive and its source copies;
run WF1 through the launcher:

```console
python scripts/run_workflow.py build_model --config <project-config.yml> \
  --project-dir <project_dir> --cores 1
```

Keep predecessor output trees under their matching revision. The new reader
requires a fresh project root and does not rewrite those trees.

The same change gave `generate_scenarios` and `simulate_system` a
`composed_config.yml` they never had, at
`scenarios/collections/<id>/composed_config.yml` and
`experiments/<name>/config/composed_config.yml`. Those are **new files, not
moves**: no identity changes, no metric set is invalidated, and nothing needs
re-running. A collection or experiment produced before the change simply has
none — both are sealed, so one cannot be added after the fact.

Three separate things happened. Engine bookkeeping was **collected into an
`_engine/` bin per scope** — the files a workflow writes so it can refuse a stale
run, rather than anything you open. They were scattered at three depths beside
results; now each scope has one directory you learn to ignore once. Anything a
reader might legitimately open stayed put, including `basin_cells.csv`, the
projections `provenance.json`, and each run's `.log` beside its `.csv`.

The scenario trees were **grouped and renamed**:
they were two unlabelled siblings at the top of the project, and nothing in
either path said which held the ask and which held the product. And every
content-digest **directory name shortened to its first 12 characters**, because
64-hex names were the main reason a project folder read as machine output rather
than as results.

**The identities themselves did not change.** Every `collection_id`,
`generation_request_id`, `metric_request_id` and `metric_set_id` recorded
*inside* a document is still the complete 64-character SHA-256. Only the
directory name is short, and it is a prefix of the full value — so you can still
match a directory to its identity by eye.

Inside the request document, the schema is now `scenario-request/1` and the
self-digest field is `request_sha256`. If you have a script that reads
`plan.json` for `plan_sha256`, it wants `request.json` and `request_sha256`.
The **metric** plan is unaffected: `metric-plan/1` and its `plan_sha256` are
unchanged.

## What to do with an existing project folder

**Re-run generation.** This is the supported path and the only one that is
verified:

```console
snakemake all -c 3 -s generate_scenarios.smk --configfile <project-config.yml>
```

Everything under the scenario trees is reproducible from the config and the
staged sources, so a re-run rebuilds it. If simulation refuses with a missing or
stale request, it names the generation command you need.

**Moving the directories by hand is not supported.** The directory name must
equal the first 12 characters of the identity recorded inside, and the workflows
check that on read — a hand-moved tree that gets the name wrong fails at the
point of use rather than at the point of the move. If a re-run is genuinely too
expensive, treat the move as a one-off script that reads each identity out of
`collection.json` / `plan.json` and renames accordingly, and verify with a
`--dry-run` before trusting it.

## A prefix collision is an error, not a merge

Twelve hex characters is 48 bits, so two collections in one store sharing a
prefix is around a 1-in-10¹¹ event at realistic store sizes. It is nonetheless
checked rather than assumed: publishing into a directory already held by a
*different* full identity raises `SegmentCollision` and refuses. It will not
merge two collections into one directory, and it will not delete a same-prefix
stranger.

## Related

- [Workflow names migration](migration-workflow-names.md) — R12's split of
  `run_stress_test.smk`, whose artifact table this change updates.
- [Configuration shape migration](migration-config-shape.md) — R13's project
  config set. Unaffected by this change.
