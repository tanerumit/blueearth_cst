# Migration — config snapshots nest under their workflow, and WF3/WF4 gain one

`dev/reference/naming.md` §7 record. Landed 2026-09-17 on `chore/post-r12`.
Filed under `post-r12/` for the reason
[`migration_scenario-tree.md`](migration_scenario-tree.md) states: this branch
is follow-up work rather than a milestone, and §7 assumes a milestone folder
exists.

Origin: an owner review of `test_case/test_rapid` on 2026-09-17, which asked
three questions of the generated tree. Two of them are these two changes; the
third (the experiment's `config/` bin holding five machine-written JSON
documents) is boarded, not done — see
[`t2609171500`](../../tasks/t2609171500-move-the-experiment-s-frozen-simulation-documents-into-engine.md).

## Event 1 — the snapshot moves into the workflow's own directory

| before | after |
|---|---|
| `config/runs/project_config_analyze_climate.yml` | `config/runs/analyze_climate/composed_config.yml` |
| `config/runs/project_config_build_model.yml` | `config/runs/build_model/composed_config.yml` |
| `config/runs/project_config_analyze_projections.yml` | `config/runs/analyze_projections/composed_config.yml` |

Each workflow wrote two files that describe the same run and sat at two
different depths — the snapshot flat in the bin, the record one level down
under `<workflow>/`. They now sit together, and the filename drops the workflow
name because the directory already carries it.

**This was boarded as blocked and the block had expired.**
[`t2608131807`](../../tasks/t2608131807-collapsing-the-per-workflow-config-copies-is-blocked-by-wf3-s-ancient-input.md)
recorded three costs on 2026-08-13, and R12 dissolved two of them: no rule
declares the WF1 snapshot as an input any more (`cross_workflow_leaves.py` marks
`LEAF_WF1_SNAPSHOT` legacy and excludes it from `LEAVES`; no `.smk` references
`check_project_consistency`), so neither the `MissingInputException` migration
nor the loss of the cross-workflow drift comparison applies. That item is
updated rather than closed — it still holds the reasoning for keeping the
`runs/` bin itself, which this change preserves.

### What to do with an existing project folder

Re-run the workflow, or run its snapshot rule alone, which is cheap:

```console
snakemake <project_dir>/config/runs/build_model/composed_config.yml -c 1 \
  -s build_model.smk --configfile <project-config.yml>
```

The old flat file is **not** removed by the run. Delete it by hand once the new
one exists; nothing reads it.

### Baseline

`dev/baseline/manifest.json`'s two snapshot keys were renamed in place with
their recorded `sha256` values **left untouched**, and the reasoning is in
`dev/baseline/provenance.md`: the re-record could not be done from the worktree
that made the change. Its `test_case/test_local` already diverged from the
manifest on both `cmip6_change_factors_*.csv` data targets before this work
started, and its flat snapshot copies still carried the retired
`run_stress_test` key, so they were pre-R12 artifacts matching neither the
manifest nor a fresh write. Recording from that tree would have rebased the
baseline onto an unverified one.

**The next re-record from a matching tree fixes those two values**, with
`record --workflow build_model --workflow analyze_projections` (merges; does not
overwrite other workflows' rows).

## Event 2 — WF3 and WF4 gain a snapshot they never had

New files, nothing renamed:

| workflow | new path |
|---|---|
| `generate_scenarios` | `scenarios/collections/<id>/composed_config.yml` |
| `simulate_system` | `experiments/<name>/config/composed_config.yml` |

Not a §7 rename, recorded here because it completes the same surface: five
workflows now write a snapshot under one name, and a reader who found three
where they expected five was reading a defect in `config/runs/README.md`, which
claimed four files existed and named WF3's stress-test grid as an example. That
README is corrected in the same commit.

These two workflows are many-per-project and content-addressed, so a single
`config/runs/<workflow>/` slot would be claimed by whichever ran last. The
snapshot lives inside the artifact instead, where two collections mean two
snapshots, each true of its own.

### It changes no identity

`collection_id` and `simulation_id` hash digests and never path strings, and
neither `collection.json` nor `simulation.json` carries a directory listing. The
snapshot is named by neither, so **no existing metric set is invalidated and no
experiment needs re-running.** Recording the same fields *inside* those
documents would have been tidier and would have rewritten every retained
experiment's identity; `read_simulation` also compares the record's key set
against an exact expected set and would have refused the older shape.

### What it closes

Three things the digest documents did not carry: which source file the settings
came from and whether it has changed since; `operation:`, a WF4 config key that
reached no record at all; and a view in the source config's own format rather
than settings split across two JSON provenance documents.

It is a record, not a re-run button — the collection also depends on the staged
forcing and the generator template, which `source_inventory.json` pins by sha256
and the snapshot does not carry.

### What to do with an existing project folder

Nothing is broken without it. A collection or experiment produced before this
change has no `composed_config.yml` and cannot gain one: both are sealed, and
the writers refuse to add to a sealed artifact by design. New ones get it.

## Verification

- `tests/test_workflow_config_snapshot.py` — 11 tests over the new module,
  including the two properties that make the placement safe.
- A real WF3 run against a `seed: 4242` variant of `project_config_rapid.yml`
  minted collection `314211381d30` and wrote its `composed_config.yml`
  (`claiming 10 scenario row(s), 10 portable input(s)` — one more than before).
  The recorded `seed: 4242` and both source digests were read back from the
  written file.
- Both snapshot rules re-run against `project_config_baseline.yml` and wrote to
  the new paths.
