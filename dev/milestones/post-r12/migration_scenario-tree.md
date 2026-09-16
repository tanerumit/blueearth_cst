# Migration — the scenario tree, short digest path segments, and the WF0 plot scales

`dev/reference/naming.md` §7 record for the post-R12 project-tree work.
Landed 2026-09-16 on `chore/post-r12`. Five §7 events, boarded as
[`t2609152040`](../../tasks/t2609152040-regroup-the-scenario-trees-under-scenarios-and-rename-scenario-plans-to-requests.md)
and [`t2609152107`](../../tasks/t2609152107-shorten-content-digest-path-segments-to-a-fixed-prefix-keeping-full-digests-as-identities.md),
plus change 2 of
[`t2609152104`](../../tasks/t2609152104-separate-engine-bookkeeping-from-user-facing-artifacts-in-the-project-tree.md).
Event 5 is unboarded — a direct owner request on 2026-09-16, recorded here
because §7 obliges a note for a rule-identifier rename.

Filed under `post-r12/` rather than a milestone folder because this branch is
follow-up work, not a milestone: `dev/milestones/README.md`'s index has no row
for it, and writing into sealed `r12/` would misattribute a change R12 did not
make. §7 mandates `dev/<milestone>/migration_<topic>.md` and assumes a milestone
exists; this is the defensible reading when one does not.

**Events 1–4 shipped in ONE migration on the owner's ruling of 2026-09-16.**
Events 1 and 4 each break every existing project tree, and shipping them
separately would cost two regenerations of the same four trees for no benefit.

## Event 1 — the scenario directory pair

| old | new |
|---|---|
| `<project>/scenario_plans/<generation_request_id>/` | `<project>/scenarios/requests/<generation_request_id>/` |
| `<project>/scenario_collections/<collection_id>/` | `<project>/scenarios/collections/<collection_id>/` |

Two sibling top-level trees of 64-hex directories said nothing about which was
the ask and which was the product, and `plan` already meant something else one
level down. **They cannot merge**, and the reason is worth keeping: the request
path is computed from config alone at DAG-construction time
(`generation_plan.py`), so Snakemake can name it before any job runs, while the
collection identity does not exist until sources are staged and inventoried.
`requests/` is the code's own word — the field is `generation_request_id` and the
schema string is `generation-request/1`.

## Event 2 — the request document, schema and digest field

| kind | old | new |
|---|---|---|
| filename | `plan.json` | `request.json` |
| `schema_version` | `scenario-plan/1` | `scenario-request/1` |
| field | `plan_sha256` | `request_sha256` |
| functions | `scenario_plan`, `write_scenario_plan`, `verify_scenario_plan` | `scenario_request`, `write_scenario_request`, `verify_scenario_request` |
| plan key | `plan_path` | `request_path` |

Outside the note's approved scope until the owner extended it on 2026-09-16.
The argument is asymmetric cost: the compatibility ruling already regenerates
every tree, so the marginal cost now is zero and the cost later is a second
break.

**`request_sha256` does not move the digest; `schema_version` does.** The field
is computed over the document *before* it is added, so renaming the key changes
nothing. Bumping `schema_version` changes the hashed projection, and therefore
every value. Both are fine under a hard break, but they interact with the
riskiest line in the change:

```python
# scenario_collection.py, _job_collection_claim
expected = content_sha256({k: v for k, v in plan.items() if k != "request_sha256"})
```

That exclusion is **by key name**. Had it not moved in the same commit as the
field, the recomputation would have silently included the new key and every
initialization receipt would have failed to verify, with no path literal wrong
anywhere.

**The metric-side `plan_sha256` is a DIFFERENT object** (`metric-plan/1`, read by
`check_baseline.py`) and is deliberately untouched.

## Event 3 — the metric request directory

| old | new |
|---|---|
| `<exp>/results/metric_plans/<metric_request_id>/` | `<exp>/results/metric_requests/<metric_request_id>/` |

Folded in from `t2609152104` change 2, because renaming one side of the toolbox
and not the other leaves two words for one concept pointing in opposite
directions — worse than the uniform-but-ambiguous state it replaced. The
**directory only**: `plan.json`, the `metric-plan/1` schema and the metric
`plan_sha256` are unchanged, since `t2609152104` change 3 flattens this
directory to one file per identity and will rename that file anyway.

## Event 4 — content-digest path segments shorten to 12 characters

| identity | stored as | named as |
|---|---|---|
| `collection_id` | full SHA-256 | first 12 |
| `generation_request_id` | full SHA-256 | first 12 |
| `metric_request_id` | full SHA-256 | first 12 |
| `metric_set_id` | full SHA-256 | first 12 |

**N = 12 was not ruled in `t2609152107` and did not need to be.**
`SHORT_DIGEST_CHARS` already existed in `blueearth_cst/shared/provenance.py` at
12, set by `t2609151643` for the WF3 run-record filenames, and its docstring
already argues against a second length constant. Reused, not restated.

`simulation_id` is **not** a path segment — it lives inside
`experiments/<name>/config/simulation.json` — and `invocation_id` is a 32-hex
UUID rather than a content digest. Neither changes. Every *stored* identity
field is still the complete lowercase SHA-256: `content_identity._digest()` and
`scenario_collection._sha256()` refuse anything shorter, unchanged.

### What was lost, and what bought it back

Four places asserted that a directory name equals an identity. Three lose almost
nothing — `metric_plan.py`, `scenario_collection.py`'s manifest check and
`check_baseline.py` each recompute the full identity from content in the same
breath, so a prefix comparison is belt over braces.

The fourth was a real loss. `list_collections` validated that a *discovered*
directory name was a full digest, with nothing else to check it against. Twelve
characters cannot carry that proof. Two things replace it:

1. **`claim_identity_segment`** (`content_identity.py`) refuses to mint a
   segment already held by a **different** complete identity, raising
   `SegmentCollision`. Because the segment is a deterministic prefix, exactly one
   sibling can collide, so this is a single lookup rather than a scan.
2. **`list_collections` now reads the complete identity from
   `collection_intent.json`** and checks the directory name is that identity's
   segment; `delete_collection` confirms the occupant before removing anything.
   Deleting a same-prefix stranger is the one failure mode truncation
   introduces, and it is now refused rather than assumed away.

Collision probability at a realistic few hundred collections per store is on the
order of 1e-11. **That is not why 12 was chosen** — it was chosen for how much
of a digest a person can hold in their eye — and the uniqueness check is there
regardless.

## Event 5 — `climate_levels` becomes `shared_plot_scales`

Landed 2026-09-16 on owner request, separately from events 1-4: it touches WF0's
figure plumbing and nothing in the scenario trees. Recorded here because §7
requires a note for a **rule identifier** rename and this branch already owns
the reader.

| kind | old | new |
|---|---|---|
| rule | `derive_climate_levels` | `derive_plot_scales` |
| artifact | `data/climate/historical/climate_levels.json` | `.../shared_plot_scales.json` |
| module | `climate_analysis/climate_levels.py` | `climate_analysis/shared_plot_scales.py` |
| functions | `compute_` / `write_` / `read_climate_levels` | `*_plot_scales` |
| smk constant | `CLIMATE_LEVELS` | `PLOT_SCALES` |
| rule input key | `levels_json` | `scales_json` |
| test | `tests/test_climate_levels.py` | `tests/test_shared_plot_scales.py` |
| log / benchmark part | `0.04b_derive_climate_levels.{log,tsv}` | `0.04b_derive_plot_scales.{log,tsv}` |

**Why, precisely.** Not vagueness -- a COLLISION. In climate-risk work "levels"
means magnitudes: global warming levels, the vocabulary beside WF2's plausibility
overlay. The file holds matplotlib class boundaries and axis limits.

**Why `scales`.** The file holds two kinds of thing -- axis limits (`[min, max]`)
for the annual and monthly series, class breaks (seven values) for the map. A
name fitting one misdescribes the other. `shared` carries the reason it exists at
all: one scale across candidate sources, so separate figures can be read against
each other.

**Why not `config`.** Raised by the owner and rejected: `config` has a hard
meaning in this repo (a `--configfile` target, or `config/defaults/` read by
rules). This artifact is derived from data and rewritten every run, and calling
it config invites someone to hand-edit what a rule overwrites.

**`RasterStyle.levels` is NOT renamed.** That is matplotlib's own `BoundaryNorm`
vocabulary at the mechanism layer -- a §6 tier-1 identifier, adapted at a seam
rather than relocalised.

**Only the rule identifier obliged this note.** The artifact is not a `rule all`
output and appears zero times in `dev/baseline/manifest.json`, so no baseline
re-record is owed; verified by grep, not assumed.

**One consequence for existing project folders**, and it is smaller than events
1-4: a tree carrying `climate_levels.json` keeps an orphan under the old name
until WF0 re-runs. Nothing reads it, so it is stale output rather than a break.
`semantic_tree_diff.py` maps the new name, so `tree-check` reports the old one as
UNMAPPED -- which is the intended signal to prune it.

Gates: `pytest tests/test_cli.py tests/test_snake_utils.py
tests/test_climate_figures.py tests/test_compare_climate_sources.py` 389 passed;
`tests/test_shared_plot_scales.py` 8 passed; lint and format-check clean.

## Machinery updated in the same landing

`blueearth_cst/experiment/`: `content_identity.py` (new `identity_segment`,
`claim_identity_segment`, `SegmentCollision`), `collection_resolution.py`,
`scenario_collection.py` (both path-containment guards, changed in lockstep with
their assertions), `generation_plan.py`, `scenario_provider.py`,
`simulation_runner.py`, `metric_plan.py`.

Workflows: `generate_scenarios.smk`, `simulate_system.smk` — both
`wildcard_constraints` sets, the two `checkpoints.*.get()` calls, and the WF3
run-record key, which is now a read of the directory name rather than a slice of
the fingerprint.

Tools: `dev/scripts/semantic_tree_diff.py` (the canonical tree rules; `digest`
is now the same `_hex` the WF3 rows use), `dev/scripts/check_baseline.py`.

Docs: `README.md`, `docs/wf3-retained-handoffs.md`,
`docs/migration-workflow-names.md`, `dev/reference/workflows/rule-index.md`,
`dev/reference/contracts/weather-generator-seam.md`, and the user-facing
`docs/migration-post-r12.md`.

Tests: `test_content_identity.py`, `test_scenario_collection.py`,
`test_collection_resolution.py`, `test_collection_preparation.py`,
`test_project_tree_inventory.py` (the canonical fixture),
`test_interchange_contracts.py`, `test_check_baseline_scope.py`.

## Compatibility and gate evidence

**Hard break, no compatibility read path** — ruled 2026-09-15 on `t2609152040`
and unchanged by the widened scope. The surviving state was four small project
trees holding one collection each; nothing tracked points into them; each is
reproducible by a WF3 run. A second accepted spelling would have had to be
threaded through the two path-containment guards, which is exactly where it is
most dangerous.

**No baseline re-record is owed.** `dev/baseline/manifest.json` contains no
`scenario_` path, and `check_baseline.py` globs `*/plan.json` under the renamed
metric parent, so it follows the directory. Verified by grep, not inherited from
the note.

Gates run on the landing: `pytest tests/test_cli.py` (20 passed) after each of
the four commits that moved a declared rule output; `pixi run lint` and
`format-check` clean; `pixi run test-full` before the branch merges.
