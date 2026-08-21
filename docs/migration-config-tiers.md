# Migrating a project config to the tiered layout

Since R13 a project's configuration is a **set of files**, not one file: a
project file plus one file per workflow. This guide is for migrating a config
written before that change.

If you are starting a new project, copy `config/templates/` instead — its header
explains the layout — and skip to [What changed, and why](#what-changed-and-why).

## The short version

```bash
python scripts/split_project_config.py path/to/your_config.yml
```

It writes a **proposal** into `config-split-staged/` beside your config and
never touches the file you point it at. Read `migration-report.md`, apply the
proposal by hand, dry-run a workflow, and you are done.

## Step by step

### 1. Run the splitter

```bash
python scripts/split_project_config.py path/to/your_config.yml
# or, to stage somewhere else:
python scripts/split_project_config.py path/to/your_config.yml --staging /tmp/proposal
```

The staging directory holds the project file it proposes, the per-workflow files
it proposes, and `migration-report.md`. Nothing is applied and nothing of yours
is edited, moved or deleted.

**Read the report's verification verdict before anything else.** Every run
composes the staged files back together and compares the result to your original
config, key for key. The verdict is either:

- **CLEAN** — the proposal reconstructs your config exactly. Safe to apply.
- **DO NOT APPLY** — it does not, and the report names the first difference.
  The staged files are kept so you can look, but applying them would change what
  your workflows read. Please report it with your config.

The splitter **refuses** a config it cannot split safely rather than guessing:

| Construct | Why |
|---|---|
| YAML anchors (`&x`) and aliases (`*x`) | an anchor defined in one section and used in another becomes an undefined alias once the two are separate files |
| merge keys (`<<:`) | a merge that re-resolves after the split changes values with no symptom at all |
| a block scalar (`|`, `>`) inside a workflow section | the dedent would strip four spaces from the scalar's own *content*, changing the string |

If your config uses one of these, inline it first or split that section by hand.

### 2. Apply the proposal

This is an ordinary file operation you perform and can diff — there is no
`--write` mode:

1. Move the per-workflow files from `config-split-staged/` to sit **beside** your
   project config.
2. Replace your project config with the staged one.

Keep the whole set in one directory. A `config_path` is resolved relative to the
**project config's own directory**, not to where you run Snakemake from, so the
set moves as a unit and a colleague can run it unchanged.

### 3. Dry-run

```bash
snakemake all -c 1 -s build_model.smk --configfile path/to/your_config.yml --dry-run
```

Any dry-run of an enabled workflow runs every composition and consistency check,
so a mis-applied proposal fails loudly before anything executes.

### 4. For a workflow you never run

Delete its file **and** its `config_path` key, leaving `enabled: false` alone in
the stanza. Do **not** leave a `config_path` naming a file that is not there:
that is a hard parse error, deliberately, so a typo cannot pass as "no settings".

A WF3 run does not require `build_model` and `analyze_projections` **files** —
only their stanzas — so the projections overlay stays optional, exactly as the
CST method requires.

### 5. That is the whole migration

Nothing under `project_dir` needs hand-migrating, ever. Your existing outputs,
snapshots and records remain a truthful history of the runs that produced them
until the project's next intended execution, at which point:

- the config snapshots under `config/runs/` are regenerated with composed
  content — no path moves, so nothing to rename;
- `experiments/<name>/config/experiment.yml` is unaffected: the recorded section
  is value-identical across the migration, so a completed experiment stays
  usable and does not need re-creating;
- `config/runs/journal.jsonl` keeps its history, and new lines carry the same
  `effective_config_sha256` an unmigrated run would have produced;
- if WF3 has already run, its consistency guard re-fires once and passes.

You only need a re-run *before* your next planned one if you specifically want
freshly-shaped records — a records audit, a handoff archive.

## What changed, and why

### The layout

```yaml
# your_config.yml — the PROJECT file, the only --configfile target
project:
  project_dir: /basins/gabon
  ...

shared:                      # what more than one workflow reads
  basin: {...}
  historical_window: {...}
  clim_historical: era5

workflows:                   # at most two keys per stanza
  analyze_climate:
    enabled: true            # no config_path: this workflow has no settings
  build_model:
    enabled: true
    config_path: your_config_build_model.yml
  analyze_projections:
    enabled: true
    config_path: your_config_analyze_projections.yml
  run_stress_test:
    enabled: true
    config_path: your_config_run_stress_test.yml
```

```yaml
# your_config_build_model.yml — WF1's settings, at column zero
model_build_config: config/defaults/wflow_build_model.yml
simulation_window:
  starttime: "2010-01-01T00:00:00"
  endtime:   "2016-12-31T00:00:00"
```

A workflow file's top level is that workflow's own settings — the file you open
to change WF1 contains WF1's settings and nothing else. The loader merges the
set back into exactly the shape every rule already expected, so no workflow
computes anything different because of the split.

### The rule that decides where a key goes

**A key read by more than one workflow lives in the project file, never in a
workflow file.** That is what `shared:` is for. It is enforced at parse time
rather than left to convention: planting a `historical_window:` or a `basin:` in
a workflow file is refused, so a project cannot end up with two records of the
same thing that disagree.

### Two anchoring rules, three lines apart

This is the one genuinely confusing part, and it is deliberate:

```yaml
data_sources: config/catalogs/deltares_data.yml   # from where you RUN
config_path: your_config_build_model.yml          # from THIS file's directory
```

Every other path key names an **external input** — a catalog, a basin CSV, an
output root — whose natural anchor is the invocation. `config_path` is the only
key that names *a fragment of the config document itself*: a file you wrote at
the same time and move as one unit with the project file. Anchoring a document's
own fragments at the document is what makes a project's config set relocatable,
which a single file got for free.

In practice they look different: a `config_path` is a bare sibling filename;
every other path key carries a directory prefix. And every error message this
raises names the directory it resolved against.

## `--config` overrides

`--config` overrides still apply to the project file, before composition. What
you can and cannot override changed:

| Form | After the split |
|---|---|
| `--config workflows='{"<name>": {"enabled": false}}'` | **still works** — `enabled` is project-file-owned |
| `--config workflows='{"<name>": {"config_path": "other.yml"}}'` | **works, and is new** — repoint a stanza at a different settings file. This is the sanctioned ad-hoc path: the override *selects* a validated file rather than bypassing validation |
| `--config project='{…}'` / `--config shared='{…}'` | **still works** |
| `--config workflows='{"<name>": {"<setting>": v}}'` | **rejected** at parse time. Edit the setting in that workflow's file; for a one-off, copy the file, edit the copy, and repoint with the row above — which needs no file edit at all |
| `--config <new_top_level_key>=v` | **rejected** — the project file's top level is closed |
| `--config workflows.<name>.<setting>=value` | **rejected by Snakemake itself**, before any file is read, and always was: `parse_config` validates keys against an identifier pattern that admits no `.`, so this dies during argument processing with `Invalid config definition: Config entry must start with a valid identifier.` Use the mapping form above, or edit the file |
| `--config project.<leaf>=v` / `--config shared.<leaf>=v` | **same** — the dot never reaches the config. Use `--config shared='{"seed": 42}'` |

## Common errors

**`workflows.<name> declares key(s) [...]`** — that stanza still holds settings.
Run the splitter.

**`T1 project config declares top-level key(s) [...]`** — a section other than
`project` / `shared` / `workflows` is still at the top level. `reporting:`
belongs at the top level of the `run_stress_test` file; anything else belongs in
its workflow's file. Run the splitter.

**`config_path names a file that does not exist`** — the message gives the
resolved absolute path and the directory it was resolved against. Either the
file is not beside the project config, or the workflow needs no settings, in
which case delete the `config_path` key.

**`... declares [...] at its top level, but those names are owned outside a
single workflow`** — a shared key was planted in a workflow file. Move it to the
project file's `shared:` section.

## What is recorded

Each workflow's config snapshot under `<project_dir>/config/runs/` is now that
workflow's **composed** configuration rather than a copy of the file you passed.
It has no comments and its keys are sorted; both are deliberate, and the bin's
own `README.md` says so. Your workflow files are recorded in `run_record.yml`
with their `sha256` but are **not** archived into the project, because their
content is already inlined in the composed snapshot beside them.
