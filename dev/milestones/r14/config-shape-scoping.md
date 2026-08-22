# Scoping — R14 config shape (naming, nesting, sections)

- Run: `r14-config-shape` · started 2026-08-22 · driver: interactive session
  (primary checkout → `session-1` lane)
- **Status: SCOPING / preparation exercise.** Not a design, not accepted, no
  implementation authorized. The next artifact is an intake + design under the
  `design-review-loop`, on the R13 pattern (`dev/milestones/r13/`).
- Predecessor: **R13 config tiers** (ACCEPTED 2026-08-21). R13 split the
  monolithic project config into T1 + one file per workflow. R14 reshapes
  *within* that split: it moves and renames keys, and does not re-litigate the
  tier decision, the path-reference composition, or the single `--configfile`
  CLI contract.

## ID convention

| prefix | means | example |
|---|---|---|
| `S1`–`S7` | proposed **structure** policy rule | `S2` — three identity classes |
| `N1`–`N7` | proposed **naming** policy rule | `N4` — `{start, end}` windows |
| `C-01`–`C-58` | one proposed **change**, individually referable | `C-07` — delete `static_dir` |
| `Q-A`–`Q-I` | **open question**, blocks a change | `Q-A` — `project.dir` vs `project_dir` |

`C-nn` (hyphenated) is this milestone's namespace and is deliberately distinct
from the un-hyphenated `Cnn` finding IDs used in `dev/reviews/` records.

## Change request (verbatim, owner, 2026-08-22)

> A few question reg. config.ymls:
>
> Main config.yml:
>
> - does it make sense to remove the shared layer and place all the parameters
>   underneath within project?
>
> - static_dir: is it now safe to remove this parameter? Is anyone downstream
>   consuming it?
>
> - historical window shall go under climate i think, as this window describes
>   the raw climate data's extraction window.
>
> These are a few examples. I think we can first do a "free, brainstorm" level
> assessment of parameters, their naming, nesting structucture under the
> config.yml.

Follow-up, same dialogue:

> Can you open a new branch for R14 and consider this as a preparation
> exercise? Also, put everything in scoping document. assign an index/id to
> each change so I can refer easily later on

## Problem

R13 fixed *which file* a key lives in. It did not touch *which section*, or
*what a key is called*. Those two questions are still answered by history:

- `shared:` names a **relationship** ("read by ≥2 workflows"), not a kind, so it
  is a bag holding a basin geometry, a climate binding, a hydrological-year
  convention and a thread count under one heading.
- One concept has several spellings (`starttime`/`endtime` vs
  `historical_year_range: [a, b]` vs `future_horizons.<n>: [a, b]`; `source`
  meaning both a catalog FILE and a catalog ENTRY).
- The experiment guard's key list (`_WF1_GUARDED`) is maintained by hand
  because no section boundary distinguishes "changes the numbers" from "changes
  only the wall-clock".

These are P3 and P4 of `dev/working/parameter-placement.md` (DRAFT, 2026-08-12),
still open. This document is the live proposal that note's §5–§6 deferred.

## Relationship to prior records

| record | status | relationship |
|---|---|---|
| `dev/working/parameter-placement.md` | DRAFT, not agreed | Inventory (§1–§3) is measured and reused. Its **M1** = `C-07`, **M2** = `C-35`, **M3** = `C-36`, **M4** ≈ `C-10`…`C-15`. Its §6 cost columns are **stale**: written 2026-08-12, before R13 landed. Re-measure. |
| `dev/milestones/r13/config-tiers-design.md` | ACCEPTED 2026-08-21 | Owns `T1_TOP_LEVEL` (D-9.5), the seam checks (D-9.1/9.2/9.3/9.6), the composition invariant (D-8.1) and the `wflow_outvars` hoist (D-9.7). Every change here that moves a top-level section **amends** an accepted decision and cannot be a quiet edit. |
| `run_stress_test.smk:100` | live code comment | Cites M1 as the reason `static_dir` was not deleted outright. `C-07` is what discharges it. |

## Proposed policy — structure

**S1 — A section is a KIND, never a relationship.** A heading answers *what is
this about?* (`basin`, `climate`, `compute`), never *who reads it?* (`shared`).
Read-count decides which FILE a key lives in; kind decides which SECTION. The
two axes are orthogonal, and `shared:` collapses them into one heading.

**S2 — Three identity classes partition the whole surface, each with its own
section name.**

| class | section | changing it changes |
|---|---|---|
| identity | everything not named below | the **numbers** |
| performance | `compute:` | cost / wall-clock only |
| description | `reporting:` | how results are **described** only |

This is the load-bearing rule: it makes the experiment guard mechanical —
*guard everything except `compute:` and `reporting:`* — instead of maintaining
`_WF1_GUARDED` by hand. `reporting:` already has exactly this carve-out in WF3
("sits outside configuration identity … editing a caption does not trip the
experiment freeze"); S2 generalizes it and gives performance knobs the same
structural treatment.

**S3 — One section, one guard granularity.** A section never mixes an
experiment-invariant key with a free-to-change one. S2 is the enforcement.

**S4 — Nest only to disambiguate; maximum depth 3 from a file root.** A group of
one is not a group.

**S5 — Engine-native blocks are never regrouped.** hydromt / hydromt_wflow /
wflow / weathergenr vocabulary enters through a PATH key pointing at a file in
their own schema (AGENTS.md hard constraint). It never appears inline in our
sections, and no key of theirs is renamed by this milestone.

**S6 — A path key names a FILE; a binding names a CATALOG ENTRY.** They never
share a section. `project.catalogs.*` are files; `basin.sources.*` and
`climate.source` are entries inside those files.

**S7 — A section name is owned by exactly one tier.** A name is either T1-only,
or it stays nested under `workflows.<name>` and is never hoisted. Two workflow
files cannot both declare a section that composes to the document's top level.

S7 is not a preference; it is forced. `HOISTED_SECTIONS` (D-10.4) maps each
hoisted name to ONE owning workflow and lifts it to a single top-level
`config["reporting"]`, and `config_composition.py:306-323` puts every *foreign*
hoisted name into the T2 rejection set. `T1_TOP_LEVEL`'s own comment names the
failure this prevents: *"the project would run with an undefined precedence
between two records of the same section."* So a second workflow file declaring
`reporting:` is refused at parse time **today**, and `compute:` cannot appear in
both T1 and a workflow file without the same collision.

## Proposed policy — naming

**N1 — No new abbreviations.** `clim_historical` → `climate.source`. Exempt:
established domain terms (`lulc`, `lai`, `uparea`, `ssp`, `outvars`).

**N2 — Dimensional values carry their unit** unless a schema fixes it:
`snap_tolerance_m`, `river_uparea_km2`, `headroom_gb`.

**N3 — A key never repeats its own section.** Inside `climate:`,
`clim_historical` → `source`.

**N4 — A time span is `{start, end}` inside a `*_window:` group** — one spelling
in every file. Replaces `starttime`/`endtime` and both bare `[a, b]` year pairs.

**N5 — A name describes the VALUE, not the workflow that reads it.**
`horizontime_climate` → `horizon_year`; `clim_project` → `ensemble`.

**N6 — Counts use `_count`.** `realizations_num` → `realizations_count`,
`step_num` → `steps_count`. (Open: `_count` vs bare plural — `Q-C`.)

**N7 — A key in a shared section never names an ENGINE.** `model.outvars`, not
`wflow_outvars`. The toolbox is meant to stay flexible: wflow is the model
today, and another may demand a different set tomorrow, so a key two
workflows read must not carry the current engine in its own name. Engine
-specific *paths* are exempt inside a workflow file, because they point at
files written in the engine's schema (S5) — `engine.build_config` stays.

**Grandfathering.** `dev/reference/naming.md` grandfathers existing names and
requires a migration note to rename a contract surface. R14 *is* that migration
note: every rename below is deliberate and versioned, not opportunistic.

## Change register

Class: **NEW** (section introduced) · **RENAME** · **SEMANTIC** (a key's
MEANING changes, not only its path — see the non-goals amendment) · **REGROUP** (moves between
sections/files) · **DELETE** · **MECHANISM** (code, not a config key).
"Breaking" = an existing project config stops parsing or changes digest.

### Group A — sections and mechanism

| ID | change | rule | class | breaking |
|---|---|---|---|---|
| `C-01` | Retire `shared:` as a heading; promote its contents to top-level kind sections | S1 | REGROUP | yes |
| `C-02` | Introduce `compute:` — the section whose contents cannot change results | S2 | NEW | yes |
| `C-03` | Generalize `reporting:` from WF3-only to any workflow file | S2 | NEW | yes — **refused today; blocked on `Q-G`** |
| `C-04` | Replace hand-maintained `_WF1_GUARDED` with "guard everything except `compute:`/`reporting:`" | S2, S3 | MECHANISM | behavior-visible |
| `C-05` | Add `schema_version: 2` to the project file; refuse a v1 set with a message naming the migration command | — | NEW | yes (by design) |

### Group B — `project:`

| ID | change | rule | class | breaking |
|---|---|---|---|---|
| `C-06` | `project.project_dir` → `project.dir` | N3 | RENAME | yes — **blocked on `Q-A`** |
| `C-07` | **Delete `project.static_dir`** (= M1) | — | DELETE | yes |
| `C-08` | ~~`project.data_sources` → `project.catalogs.spatial`~~ — **superseded by `C-40`** | S6, N1 | RENAME | yes |
| `C-09` | ~~`project.data_sources_climate` → `project.catalogs.climate`~~ — **superseded by `C-39`** | S6, N1 | RENAME | yes |
| `C-39` | Move the climate catalog OUT of the project file: `project.data_sources_climate` → `catalog:` in `_analyze_projections.yml` | S1, S6 | REGROUP | yes |
| `C-40` | `project.data_sources` → `project.catalog` (single leaf, since `C-39` empties the group) | S4, S6, N1 | RENAME | yes |

**S7 constrains `C-02`, `C-03`, `C-28` and `C-34` together.** As drafted, this
document places `compute:` in both the project file (`C-21`) and the WF3 file
(`C-34`), and `reporting:` in both the WF2 file (`C-28`) and the WF3 file
(already there). Both collide with the closed hoist map. `Q-G` is the ruling
that resolves it; until then those four rows are proposals with a known
mechanical obstacle, not merely breaking changes.

`C-07` evidence: read only by `build_model.smk:89`, used only to build the two
fallback prefixes at `:163-164`; explicitly *not* read by WF3 since 2026-08-13
(`run_stress_test.smk:100`); never read by WF0 or WF2; can only ever be
`config`, because the paths it prefixes are in-repo toolbox files. What makes it
breaking is not consumption but **digest identity** — `config_composition.py`
invariant #2: a key present-vs-absent moves `effective_config_digest`, and
`_frozen_differences`' key-union diff then refuses every already-run experiment
in the project. `_WF1_GUARDED` also guards `"project"` **whole**.

`C-39` rests on the same guard defect as `C-07`, and is the stronger case of
the two. `data_sources_climate` is read by **WF2 alone**
(`analyze_projections.smk:70`), while `data_sources` is read by all four
(`analyze_climate.smk:83`, `build_model.smk:90`, `analyze_projections.smk:110`,
`run_stress_test.smk:107`). Because `_WF1_GUARDED` compares `project` whole,
repointing the CMIP6 catalog — a pure WF2 concern — today diverges a section
WF1 owns and refuses experiments built by a workflow that never read the key.
Moving it into the WF2 file puts it under `_WF2_GUARDED`, where the same edit
correctly refuses WF2's own snapshot and nothing else. It also reunites the
catalog with `ensemble: cmip6`, which is one decision split across two files
today. **Status: proposed, no owner ruling.** The counter-case is that a
future bias-correction or downscaling reader would have to move it back; that
is judged unlikely by design, since CMIP6 is a plausibility overlay here and
never drives a stress test.

### Group C — `basin:`

| ID | change | rule | class | breaking |
|---|---|---|---|---|
| `C-10` | `shared.basin` → top-level `basin:` | S1 | REGROUP | yes |
| `C-11` | ~~`basin.gauge_points` → `basin.gauges.points`~~ — **superseded by `C-41`** | S4 | REGROUP | yes |
| `C-12` | ~~`basin.gauge_snap_tolerance_m` → `basin.gauges.snap_tolerance_m`~~ — **superseded by `C-42`** | S4, N2 | REGROUP | yes |
| `C-41` | `basin.gauge_points` → **`basin.output_locations`** (flat leaf, no `gauges:` group) | N5 | RENAME | yes |
| `C-42` | `basin.gauge_snap_tolerance_m` → `basin.delineation.snap_tolerance_m` | S4, N2, N5 | REGROUP | yes |
| `C-13` | `basin.automatic_subbasins.max_per_basin` → `basin.delineation.max_subbasins` | S4 | REGROUP | yes |
| `C-14` | `basin.river_uparea_km2` → `basin.delineation.river_uparea_km2` | S4 | REGROUP | yes |
| `C-15` | `basin.spatial_sources.*` + `basin.hydrography` + `basin.basin_index` → `basin.sources.*` | S6 | REGROUP | yes |

`C-10`…`C-15` are M4 made concrete: `shared.basin` currently mixes three kinds
— the basin's DEFINITION (`region`, `resolution`), catalog BINDINGS
(`spatial_sources.*`, `hydrography`, `basin_index`) and delineation TOLERANCES
(`max_per_basin`, `gauge_snap_tolerance_m`, `river_uparea_km2`).

#### Conceptual correction — these points are not gauges (`C-41`, `C-42`)

**Ruled by the owner, 2026-08-22.** `gauge_points` names the wrong concept.
The file lists **points of interest**: locations where discharge is computed,
also used as outlets for subbasin-level calculations. Some are gauges; many
are not (a candidate dam site, say), and a basin may have none at all. Where a
gauge does exist, its record lives in `observations_timeseries.csv`, keyed by
`wflow_id` — so observation data is already decoupled from the point list.

The code says the same thing three ways, and only the config key dissents:

- `config/templates/output_locations_template.csv` carries a `location_role`
  column whose values are `control` | `observation`, **defaulting to
  `control`** (`spatial/products.py:310-324`), plus `automatic_outlet` for the
  delineation-generated rows (`observation_validation.py:66`). A gauge is the
  minority subtype, not the category.
- Every internal name is already `output_locations` / `output-locations`: the
  rule input (`snake_utils.py:1666`), the archived role
  (`copy_config_files.py:44`), the template filename, and the derived
  staticgeoms and column names (`shared/gauges.py:10`).
- The config key **used to be** `workflows.build_model.output_locations` and is
  still accepted as a legacy alias (`spatial/config.py:83-99`). `C-41` is
  therefore a REVERT, not new vocabulary.

`C-42` drops `gauge` for the same reason: the tolerance snaps *any* point onto
the river network, and it belongs with `max_subbasins` and `river_uparea_km2`,
since all three govern how the network and its outlets are resolved.

Unchanged, deliberately: `blueearth_cst/shared/gauges.py`, hydromt_wflow's
`setup_gauges`, and the `gauges_output-locations` staticgeoms layer. That is
engine vocabulary under S5 — R14 renames our key, never theirs.

Both rows are pure RENAMEs: no semantics move, no number moves, D3 holds. A
conceptual correction does not automatically breach the non-goals.

#### Why `sources` and not `data_sources` (`C-15`)

**Ruled by the owner, 2026-08-22.** The question was whether `basin.sources.*`
should be `basin.data_sources.*`, since that is the spelling the current config
uses.

hydromt's vocabulary is precise, and the vendored guide states it
(`docs/hydromt-user-guide/02-overview.md:359`):

> `-d, --data`: ... path to the local yaml **data catalog** file
> `-s, --source`: The **data source** to export

So the CATALOG is the file and a DATA SOURCE is a named entry inside it -
confirmed by `config/catalogs/deltares_data.yml`, whose top-level keys
(`basin_atlas_level12_v10:` and the rest) are those entries. Two consequences:

1. `basin.sources.rivers: rivers_lin2019_v1` genuinely *is* a data source in
   hydromt's sense, so `data_sources` would be engine-accurate.
2. Today's `data_sources: config/catalogs/deltares_data.yml` is the misnomer -
   it names a catalog, not a source. `C-40` already corrects it to
   `project.catalog`, which also matches hydromt's `-d`.

`data_sources` was rejected anyway, because that spelling currently means *the
catalog file*. Reusing it for *catalog entries* in the same migration gives one
name two meanings across the version boundary: a user reading a v1 config beside
a v2 one, or hand-migrating, sees `data_sources` in both and reads the wrong
thing. That is P3 inverted - one spelling, two concepts - which is worse than
the naming it would replace, and it is precisely the failure `C-38`'s mechanical
rewriter cannot protect a human reader from.

Nor is dropping `data_` a divergence from the engine: hydromt's own CLI flag is
the bare `--source` for exactly this value.

The resulting rule, which S6 already states and this note fixes the words for:
**`catalog` means the file, `source` means an entry, everywhere.** Hence
`project.catalog` (`C-40`), `basin.sources.*` (`C-15`) and `climate.source`
(`C-17`) - one kind, one spelling, in three sections.

### Group D — `climate:`

| ID | change | rule | class | breaking |
|---|---|---|---|---|
| `C-16` | Introduce top-level `climate:` | S1 | NEW | yes |
| `C-17` | `shared.clim_historical` → `climate.source` | N1, N3 | RENAME | yes |
| `C-18` | `shared.historical_window.{starttime,endtime}` → `climate.window.{start,end}` | N4 | RENAME | yes |
| `C-43` | New `climate.sources` — a flat LIST of candidate datasets with no privileged element. Absorbs `candidate_sources`, moving it T2 → T1 and widening its meaning from "extras besides the primary" to "the full candidate set" | S1, charter | **SEMANTIC** | yes |
| `C-44` | `shared.clim_historical` → `climate.selected`, with requiredness that varies by consumer (below) | N5 | **SEMANTIC** | yes |
| `C-45` | Retire `workflows.analyze_climate.candidate_sources`; refused at parse time, as `start_month_hyd_year` is | — | DELETE | yes |
| `C-46` | WF0 figure and comparison-table ordering follows `selected` when set, else declaration order | — | behavioural | no |
| `C-47` | Adopt the `climate:` CHARTER (below) as the section's definition in the template and `dev/reference/` | S1, N5 | NEW | no |
| `C-48` | Give the ANALYSIS variable set a config surface — selection from a registry, defaulting to today's `precip`/`temp`/`pet` | S2, P1 | NEW | no |
| `C-49` | Move the `CLIMATE_VARS` registry out of Python so the default is visible (extends `C-36`) | — | MECHANISM | no |
| `C-50` | Give the EXTRACTION set a config surface: derived, not declared. Designed now, behaviour deferred — narrower-than-default is REFUSED at parse time until it lands | S5, N7 | NEW | no |
| `C-53` | `shared.water_year_start` → `climate.water_year_start` (amends the `C-47` charter) | S1, charter | REGROUP | yes |

`C-16`–`C-18` are the owner's third question. `clim_historical` (the *what*) and
`historical_window` (the *how much*) are one concept in two sibling keys —
`shared.basin`'s complaint again. Caveat: `SHARED_SEAM_KEYS` is a **flat set of
names**, so nesting moves seam coverage from leaf to group and a T2 file could
then declare a bare `window:` uncaught. `basin` already has that property, so
this is a tolerated pattern rather than a new hole — but the seam set must be
re-derived, not merely edited.

#### The charter (`C-47`)

**Ruled by the owner, 2026-08-22**, answering "is `climate:` about forcing or
about analysis?"

> **`climate:` declares the project's historical climate RECORD** — which
> datasets represent this basin and over what period — **and the CONVENTIONS
> that record determines**. It never declares what a workflow *does* with the
> record.

*(The clause in bold was added 2026-08-22 with `C-53`. It widens the charter,
so it is worth checking the boundary still bites: WF1's `simulation_window`,
WF2's `historical_year_range` — bounded by CMIP6's 2014, not by our record —
WF3's `horizon_year` and WF0's figure choices all stay out. It also covers
`selected`, which was already sitting on the line as a DECISION rather than a
fact.)*

The question felt open only because the section had been named by its
CONSUMER, which is what N5 warns against. Named by what it IS, the ambiguity
disappears, and the charter yields a mechanical placement test for every
future key: *is this a fact about the basin's climate, or a use of it?* Facts
go in `climate:`; uses go in a workflow file. Exactly parallel to `basin:`,
where the geometry is a project fact and each workflow's use of the
delineation is not.

| stays in `climate:` (the record) | stays in a workflow file (a use) |
|---|---|
| `sources`, `window`, `selected` | WF0's figure and comparison choices |
| | WF1's `simulation_window` |
| | WF2's `historical_year_range` |
| | WF3's `horizon_year`, `run_length` |

**Moving `climate:` down into the workflow files was considered and
rejected.** It is not an R14 tweak: `historical_window` and `clim_historical`
are both in `SHARED_SEAM_KEYS`, so a workflow file declaring either is a parse
error TODAY (D-9.2/D-9.3) — reversing that amends an accepted R13 decision.
The reason holds on inspection: the climate store's path is
`data/climate/historical/<source>_<window>/`, written by WF1 and read by WF3,
so the shared value IS a filesystem key rather than a convention; and
`simulation_window` must sit inside `historical_window`
(`build_model.smk:741`); and WF2 reads the window to warn when its own
baseline stops aligning (`analyze_projections.smk:117`, `:180`). Split, two
files could disagree about what the record IS, and the failure would surface
as a missing store a whole workflow away from its cause.

Worth noting the seam rule produced three different answers across this
document — `C-39` pushes the climate catalog DOWN (single reader), `C-43`
pulls the candidate list UP (cross-workflow invariant), and the window stays
put. A rule that discriminates is doing work.

#### Many candidates, one selection (`C-43`–`C-46`)

**Ruled by the owner, 2026-08-22.** There is no logical primary/secondary
split among historical datasets: which one is better for a basin — more
reliable, better spatial coverage — is the question WF0 exists to ANSWER, so
the config must not presuppose it. `sources` is therefore a flat set, and
`selected` is the conclusion drawn from the evidence.

Resolution rules, chosen over a first-wins fallback:

1. `sources` has ONE entry → `selected` resolves to it. Not a fallback; there
   is no choice to make.
2. `selected` unset and only WF0 runs → **valid**, no error. WF0 never needed
   it: it analyses every source. "I have candidates, I have not chosen yet" is
   a legitimate project state and the config must be able to express it.
3. `selected` unset and WF1 or WF3 runs → **refused at parse time**, naming the
   candidates and pointing at WF0's comparison output.
4. `selected` must be a member of `sources`.

**A first-wins fallback was rejected**: it reinstates the primary this change
removes, with declaration ORDER now holding the privilege, invisibly. WF1
would force the model and WF3 condition the generator on a dataset nobody
chose, and the run record would name it as though someone had. CST does no
local calibration, so forcing choice is the dominant lever on the historical
run — the one decision that must not be inherited from YAML line order. Rule 3
stops the pipeline exactly where a human judgement is required, which matches
how this repo already behaves (unsupported sources are refused at parse time
rather than failing inside a generated rule).

**No new machinery is needed.** `analyze_climate.smk:229` reads
`enforce_min_years=(source == clim_source)`; substituting `selected` is the
whole change. With a selection, that source keeps the canonical spec, so the
store WF0 builds is the one WF1 reads. With none, no source is privileged and
every candidate relaxes the weathergenr floor — which binds later, at the
moment of commitment, because promoting a candidate flips the param and
re-extracts (`snake_utils.py:131-132`: `True` emits no param, `False` emits
one). That REMOVES WF0's primary asymmetry rather than adding a mechanism.
Selection is therefore cheap in disk and tooling — candidate stores already
land beside the project's own, not in an evaluation bin — and costs one
re-extraction, which is how the floor gets enforced rather than assumed.

Two details to carry into the design:

- **Absent and bare-null both read as unset** (the spelling `experiment_name`
  already handles). But R13's composition invariant #2 makes a key
  present-vs-absent move the digest, so two projects meaning the same thing
  would hash differently. The template should ship `selected:` present and
  null, so every project carries the key and the slot is visible.
- **The supported set is bounded and smaller than the ambition.**
  `_SUPPORTED_SOURCES = ("era5", "chirps", "chirps_global")`
  (`analyze_climate.smk:120`), and `build_model.smk:148` refuses `eobs` on the
  WF1 raw-climate path. `cru` and `eobs` do not exist today. The SHAPE is
  general; adding a dataset is a capability task on the board, and R14 must
  not imply it ships one.

Migration invariant: a v1 config with `clim_historical: era5` and no
candidates maps to `sources: [era5]` + `selected: era5`, which is
behaviourally identical — so D3 and success criterion 5 both survive despite
the SEMANTIC class.

#### Which variables (`C-48`–`C-50`)

THREE variable sets exist today and only separating them makes the question
answerable:

| set | contents | lives in | configurable |
|---|---|---|---|
| extraction | whatever the store pulls — precip, temp, radiation, pressure ... | fixed in code, per source branch | no |
| analysis | `precip`, `temp`, `pet` | `CLIMATE_VARS` (`climate_figures.py:83`) | no |
| comparison | `precip`, `temp` | `COMPARABLE_VARS` (`compare_sources.py:94`) | no |

`climate_store_rule` carries **no variable parameter at all** — the extraction
set is not merely unconfigured, it is not part of the store's identity.

**`C-48` — the analysis set.** A textbook P1/M3 case: a user-facing default
with no config surface, discoverable only by reading source. By S2 it is a
`reporting:` key rather than a `climate:` one, because which variables get drawn
cannot move a number — figures are terminal artifacts and dropping one drops a
table column. Depends on `Q-G` for where `reporting:` lives.

SELECTION from a registry, not DEFINITION. Each entry carries `label`, `unit`,
`style` and `how`, and the module is blunt about the last one: *"a summed
temperature is meaningless and a meaned rainfall understates by ~365x."*
Aggregation semantics do not belong in a user's YAML list; an unknown name is
refused at parse time, as the code already does. A genuinely new variable stays
a code change plus a board item.

**Hard constraint.** The honesty narrowing survives untouched.
`source_climate_vars` refuses to draw temperature for a precip-only source
because those values are ERA5's, regridded — the owner's ruling of 2026-08-16,
that a dataset missing a variable gets NO output for it rather than one silently
filled from another dataset. A configured list is INTERSECTED with what each
source honestly carries, never used to force a plot into existence.

**Naming.** WF2 already has a `variables:` mapping with a different schema
(`{source, canonical, units, change}`) that IS identity — it drives the change
factors. Two keys spelled `variables`, different shapes, different S2 classes,
is a P3 in the making. This one takes a distinguishing name.

**`C-50` — the extraction set.** *Owner, 2026-08-22: this should become
configurable, to avoid downloading variables nothing needs. Recorded here;
the extraction work itself is out of R14.*

DERIVED, not declared. A freely declared list can break WF1 — radiation and
pressure are extracted because PET is computed from them. A mandatory-core-plus
-additions shape was considered and rejected under N7: the core would encode
*wflow's* requirements in our schema, and a second model would mean editing
both. The correct source of truth is the model adapter DECLARING its own forcing
requirements, with

    extract = union(selected model's requirements,
                    each enabled workflow's requirements,
                    variables the user asked to analyse)

which serves the goal exactly: run WF0 alone and no model requirements enter the
union at all. That is the real saving, and it is workflow-dependent, which is
precisely why the store spec is fixed today — it is built to serve WF1.

**A dummy key was considered and rejected.** Shipping the key inert, with
behaviour to follow, is P2 shipped on purpose: `start_month_hyd_year` was read,
forwarded to rule 2.06 and never used; `relax_priority` is not forwarded;
`static_dir` was required and ignored. Four inert parameters, four found by
hand, zero by machine — and D1 asks whether a proposal answers P2 mechanically.
Here the failure would also be silent and QUANTITATIVE: a user writes a shorter
list, expects a smaller download, gets the full extraction, and nothing says so.

Instead, REFUSE rather than lie. The key exists in the schema from R14, so no
second migration, but only the current full set is accepted; anything narrower
is refused at parse time naming the board item. This is the repo's own idiom —
unsupported sources are refused at parse time, and `start_month_hyd_year` was
made a refusal rather than an ignore. It also keeps the SEMANTICS unfrozen,
which matters because they depend on a model boundary that does not exist yet.

### Group E — `model:`, `method:`, `compute:`

| ID | change | rule | class | breaking |
|---|---|---|---|---|
| `C-19` | `shared.wflow_outvars` → `model.outvars` | S1, N7 | REGROUP | yes |
| `C-20` | ~~`shared.seed`, `shared.water_year_start` → `method.*`~~ — **superseded by `C-51` and `C-53`** | S1, S3 | REGROUP | yes |
| `C-51` | `shared.seed` → `seed:` in `_run_stress_test.yml`; remove from `SHARED_SEAM_KEYS` (R13 amendment) | S1, seam | REGROUP | yes |
| `C-52` | Retire the `method:` section entirely — both its keys have real homes | S1, S4 | DELETE | yes |
| `C-21` | ~~`shared.julia_threads` → `compute.julia_threads`~~ — **superseded by `C-54`** | S2, S3 | REGROUP | yes |
| `C-54` | `shared.julia_threads` → `advanced_settings.runtime.julia_threads`; the project-level override is REMOVED | authority | DELETE | yes |
| `C-55` | T1 `compute:` dissolves — `compute:` becomes workflow-local only, nested under its own file and never hoisted | S4, S7 | DELETE | yes |

`C-21` was the clearest S3 case: `julia_threads` cannot change a number, and
flattening it into a guarded section (the owner's Q1 as literally posed) would
make a thread-count bump trip *"your model was built under different settings"*.
It is superseded, not withdrawn — the S3 reasoning stands, the key just leaves
the project surface entirely.

#### `julia_threads` leaves the project config — `C-54`, `C-55`

**Ruled by the owner, 2026-08-22:** it is a technical setup preference about
the Julia software, unlike every other key around it, and users will not
change it. Reserve it for `config/advanced_settings.yml` at the default of 4.

It lands under `runtime:`, NOT `defaults:`. That file's boundary is AUTHORITY
rather than topic: `defaults:` means a project may override, `runtime:` and
`constraints:` mean it may not. Since the point is removing the project-level
override, `defaults.julia_threads` would be defaulting for a key that no longer
exists. `runtime:` already holds `julia_version`, and a Julia version and its
thread count are the same kind of thing — how we invoke Julia.

**The dividend (`C-55`): T1 `compute:` dissolves.** `julia_threads` was its
only T1 member, so `compute:` now exists solely in the stress-test file
(`C-34`). That matters for S7: `Q-G` existed because `compute:` had been placed
in BOTH tiers, colliding with the closed hoist map. With T1's gone the
collision does too — a workflow-local `compute:` nested under its own file and
never hoisted satisfies S7 with no ruling required. **`Q-G` narrows to the
`reporting:` question alone.**

This is the same shape as `C-52`: a section that looked like a KIND turns out
to have held one key for want of a home, and removing the key removes the
section. Two of the draft's five new T1 sections have now dissolved that way,
which is worth watching — it is weak evidence that the draft over-sectioned.

Two things to carry forward. It is a user-facing REMOVAL, not a move: anyone
setting `shared.julia_threads` loses it, so the migration notes must point at
the new location rather than rewrite the key. And machine-dependence does not
argue against it — thread count multiplies against Snakemake's `-c N`, and
neither the project config (per-PROJECT, and a project moves between machines)
nor `advanced_settings.yml` was ever per-machine. If per-machine tuning becomes
a real need, `profiles/default/config.yaml` is where machine parallelism
already lives. `_ADVANCED_SETTINGS_SCHEMA` is closed, so the key and its schema
entry move in one commit.

#### `model:` is the engine boundary — `Q-B` resolved

**Ruled by the owner, 2026-08-22:** the toolbox aims to stay flexible. wflow
is the hydrological model today; another may later demand a different set of
forcing variables and a different build configuration.

That resolves `Q-B`. `model:` is not a group of one — it is the seat of the
MODEL BOUNDARY, where the engine is named and its cross-workflow declarations
live. And it upgrades `C-19` from a grouping preference to a correctness fix:
`wflow_outvars` hardcodes the engine into a key that WF1 and WF3 both read, so
swapping the model leaves a shared key lying in its own name. That is the
general case N7 now states.

The output tree already anticipates this: artifacts land under
`models/hydrology/wflow/`, namespaced by domain AND engine.

**Double-checked 2026-08-22 (owner): should `outvars` sit under build_model
instead, since its values are a wflow setting?** No — that is where it lived,
and R13 moved it OUT. `SHARED_SEAM_KEYS` records why: hoisted from
`workflows.build_model` by **D-9.7**, it was "the one sanctioned cross-workflow
value read — WF1 builds the model with it, WF3 derives its indicator tables
from it — and moving it here is what let `CROSS_WORKFLOW_READS` be emptied and
retired." Moving it back would reinstate that read against a D-9.6 scan which
now asserts literally ZERO of them (the registry that would have sanctioned one
was retired as unable to enforce shrink-only); it would be refused at parse
time today, since the key is in `SHARED_SEAM_KEYS`; and it would weaken the
experiment guard, which R13 extended with the `("shared", "wflow_outvars")`
leaf precisely so a post-build edit is caught here rather than surfacing
mid-experiment as a missing-column error a whole workflow away.

Placement follows READERS; the values being engine-native is why the key name
must not be (N7). `C-19` therefore stands: same tier, same meaning, a name that
survives an engine swap.

Model pluggability itself is NOT an R14 concern — it is an architectural
milestone of its own. What R14 owes it is not to paint it into a corner:
`N7`, `model:` as a real section, and refusing to bake a wflow-shaped variable
core into the config schema (`C-50`).

#### `method:` was a leftovers bag — `C-51`, `C-52`, `C-53`

**This document committed P4 in its own draft, and the correction is recorded
rather than quietly applied.** `seed` and `water_year_start` were grouped
under `method:` because neither fitted elsewhere — grouping by history, which
is the exact defect P4 names and `C-10`–`C-15` exist to fix. By the one
criterion this repo actually uses they are maximally unalike:

| key | readers |
|---|---|
| `seed` | `run_stress_test.smk:161` — **one** |
| `water_year_start` | `analyze_climate.smk:97`, `build_model.smk:81`, `analyze_projections.smk:162`, `run_stress_test.smk:166` — **four** |

`C-51` sends `seed` down to the workflow that runs the weather generator, by
the same seam rule as `C-39`. A second argument is nearly decisive on its own:
`resolve_seed(get_config(shared_cfg, "seed"), experiment)` derives `seed: auto`
from the EXPERIMENT NAME, which lives in the stress-test file — so the two
halves of one computation are split across two files today, and this reunites
them. It also honours the owner's point that the weather generator IS a model,
a stochastic one: its reproducibility knob belongs with the workflow that runs
it, not in a shared bag.

The counter-argument is that the template calls `seed` the seed for "every
stochastic step (TODAY: the weather generator)", so a second stochastic step
elsewhere would move it back. Accepted, because that failure is MECHANICALLY
DETECTED rather than silent: R13's D-9.6 static read scan asserts literally
zero cross-workflow value reads, so the day a second workflow reads it, the
scan fails.

`C-53` sends `water_year_start` UP into `climate:`. The test is not what uses
it but what DETERMINES it: change the selected dataset or the window and it
does not move; change BASIN and it does. `basin:` was the other candidate and
was rejected — that section is entirely spatial, and a reader looking for the
water year checks `climate:` first. The evidence for choosing it is literally
WF0's monthly climatology figures, so `window`, `selected` and
`water_year_start` become three decisions read off one figure set, in one
section. Their adjacency also makes a real coupling visible: an Oct water year
against a Jan–Dec window leaves partial years at both ends.

`C-52` then follows: with both keys housed, `method:` has no contents.

### Group F — `_build_model.yml`

| ID | change | rule | class | breaking |
|---|---|---|---|---|
| `C-22` | `model_build_config` / `waterbodies_config` → `engine.build_config` / `engine.waterbodies_config` | S4, S5, N3 | REGROUP | yes |
| `C-23` | ~~`observations_timeseries` → `observations.timeseries`~~ — **superseded by `C-56`** | S4 | REGROUP | yes |
| `C-56` | `observations_timeseries` → `observations:` as a mapping KEYED BY VARIABLE, in `model.outvars` vocabulary | N5, S4 | RENAME | yes |
| `C-24` | `simulation_window.{starttime,endtime}` → `simulation_window.{start,end}` | N4 | RENAME | yes |

#### Observations are keyed by VARIABLE — `C-56`

**Ruled by the owner, 2026-08-22.** `observations_timeseries` names the SHAPE
of the value (a timeseries) rather than its CONTENT (observed river
discharge), and the repo already disagrees with itself about it: the shipped
template is `observed_daily_discharge_template.csv` while the config key says
`observations_timeseries`. Two spellings, one thing — P3.

```yaml
observations:
  river discharge: <path>
```

The file's columns are STATIONS, not variables (`time;1010;1020`), so one file
is one variable across many gauges — which is exactly why the variable is the
right key. Values are drawn from `model.outvars` vocabulary verbatim, which
buys a parse-time INVARIANT: observations may only be supplied for a variable
the model was asked to output, because otherwise there is nothing to compare
against and the config expresses a wish rather than a fact. That is a
mechanical check of the kind D1 asks every proposal here to produce.

It also supersedes `C-23` properly rather than patching it: that row made
`observations:` a group of one and an S4 violation. A mapping keyed by
variable is not nesting for nesting's sake — it is a dictionary that happens
to hold one entry today.

A list of records (`- {variable: ..., path: ..., units: ...}`) was considered
and held in reserve: same idea with room for per-entry metadata, more verbose,
and nothing needs the metadata today. It is the upgrade path if units or
timestep ever have to be declared per file. A flat `observed_discharge:` was
rejected — it hardcodes the variable into the key, which is what N7 argues
against in spirit.

**A coupling to record.** `basin.output_locations` (T1) carries rows with
`location_role: observation`, and those rows name the `wflow_id` COLUMNS
inside this file; `shared/gauges.py:100` already warns that changing one means
changing the other. After R14 the two sit in DIFFERENT TIERS — the point list
in the project file, the observed data in WF1's. Correct by the readers rule
(`observations_timeseries` is WF1-only: `build_model.smk:166`, plus
`copy_config_files.py` archiving and `plot_results.py`), but a user can break
it in one file and only discover it from the other, so it belongs in the
template comment as well as here.

`simulation_window` stays in the WF1 file: it is read by `build_model.smk` only
(verified 2026-08-22), so it is correctly T2 despite reading like a shared
window.

#### Why `simulation_window` keeps its name

**Considered and rejected 2026-08-22 (owner):** it is really the *reference*
simulation window, but `reference_simulation_window` is too long.

Two disambiguations are available inside `_build_model.yml`, and only one is
live there:

- **"simulation"** separates it from `climate.window` — the RUN period versus
  the EXTRACTION period. That is the confusion users actually hit, and the
  template already spends four lines on it.
- **"reference"** separates it from the stress-test runs — but those live in
  `_run_stress_test.yml`, and their window is not even a declared key (it is
  derived from `horizon_year` +/- `run_length`/2). That distinction is not
  present at the point of reading.

The disambiguating word should resolve the confusion available where the reader
is standing. There is also a file-scope reading of N3: everything in
`_build_model.yml` IS the reference run, so "reference" in the key repeats the
file's own subject, exactly as `clim_historical` repeated its section's.

N4 fixes the suffix, so the shorter candidates were `reference_window` and
`run_window`. `reference_window` is no longer than the current name and becomes
the better choice IF WF3's run window ever becomes an explicit key, since both
distinctions would then go live at once — worth revisiting at that point, not
before. "Reference" goes in the template comment, where it can be a sentence
rather than a prefix. `C-24` (`starttime`/`endtime` -> `start`/`end`) is
unaffected either way.

**An adjacent P3, recorded so it is a known asymmetry rather than a future
discovery:** `simulation_window` (WF1, declared, a date span) and `run_length`
(WF3, declared, an integer of years) describe the same kind of thing — how long
the model runs — in two spellings and two shapes. Not unified now, because
WF3's window is deliberately derived rather than declared.

### Group G — `_analyze_projections.yml`

| ID | change | rule | class | breaking |
|---|---|---|---|---|
| `C-25` | `clim_project` → `ensemble` | N1, N5 | RENAME | yes |
| `C-26` | `historical_year_range: [a, b]` → `historical_window: {start, end}` | N4 | RENAME | yes |
| `C-27` | `future_horizons.<name>: [a, b]` → `future_horizons.<name>: {start, end}` | N4 | RENAME | yes |
| `C-28` | `stats`, `save_grids` → `reporting.{stats,save_grids}` | S2 | REGROUP | yes — **blocked on `Q-G`**: WF2 declaring `reporting:` is refused today |
| `C-57` | `variables:` gains a SHORT FORM — a bare key resolves through a registry; a name the registry lacks and that declares no spec is refused | P1 | **SEMANTIC** | no (additive) |
| `C-58` | `canonical` leaves the USER surface; it stays in the registry | P1 | RENAME | yes |

`C-25` also removes a live collision: `clim_project` reads as "the project's
climate" while meaning the projection ensemble family, next to a `project:`
section that means something else entirely.

#### The variable spec is rigorous and costly — `C-57`, `C-58`

**PROPOSED. The owner ruled the diagnosis, not yet the fix (2026-08-22):**
the four-field spec is rigorous but not user friendly.

What the two disputed fields actually do, measured:

- **`change` is ARITHMETIC, not plotting.** `change_factor_table.py:122` — it
  "decides whether `relative_value` is a percent or a ...". It is what makes
  precipitation a ratio and temperature a delta, so a wrong value MOVES
  NUMBERS. `variable_spec.py` exists because stage B used to branch on the
  literal string `"precip"`, so a new relative variable named anything else
  was differenced as a temperature, silently. Falsifier K7 pins it.
- **`canonical` does almost nothing.** Its only consumers are the display
  label `long_name`, its own validation, and one accessor — nothing branches
  on it. The module admits why: *"in v2.0 there is one source frequency
  (`Amon`) so it is the identity."* Most typing, least weight.

The proposed fix is a REGISTRY, not a retreat to bare names:

```yaml
variables:
  precip:                                                     # registry-resolved
  temp:
  windspeed: {source: sfcWind, units: m/s, change: absolute}   # not in the registry
```

A bare key means "use the registry entry" — the null-reads-as-unset idiom the
repo already uses for `experiment_name` and `climate.selected`. A name the
registry does not know and that declares no spec is REFUSED.

That preserves K7 and is stronger than today. The failure 5e fixed was an
unknown variable silently acquiring temperature semantics; refusal beats both
that and the current state, in which a user can still hand-type the wrong
`change:`. The actual defect 5e cured was semantics living in a branch buried
in the reducer — not the use of names as keys — and an explicit table keeps
that cure.

`C-58` keeps `canonical` in the registry, where it still feeds `long_name` and
stays ready for a second source frequency, without every project restating an
identity.

This PAIRS WITH `C-49`: `CLIMATE_VARS` and this projections spec are the same
pattern — a table of variable semantics that should be visible and NAMED
rather than restated per project. Both land wherever `Q-E` puts defaults, and
they should land together or the repo grows two conventions for one thing.

### Group H — `_run_stress_test.yml`

| ID | change | rule | class | breaking |
|---|---|---|---|---|
| `C-29` | `realizations_num` → `realizations_count` | N6 | RENAME | yes — **`Q-C`** |
| `C-30` | `horizontime_climate` → `horizon_year` | N1, N5 | RENAME | yes |
| `C-31` | `stress_test.<var>.step_num` → `steps_count` | N6 | RENAME | yes — **`Q-C`** |
| `C-32` | `stress_test.<var>.transient_change` → `transient` | N3 | RENAME | yes |
| `C-33` | `stress_test.{dry,wet}_spell_factor` → `stress_test.spell_factors.{dry,wet}` | S4 | REGROUP | yes |
| `C-34` | `batch_size`, `batch_size_max`, `disk_headroom_gb` → `compute.*` | S2, S3 | REGROUP | yes |

`C-33` keeps the existing rationale intact — the spell factors are not
perturbation axes and must not read as siblings of `temp:`/`precip:`; a named
`spell_factors:` group says that structurally instead of in a comment.
`C-34` is S2's second payoff: three WF3 keys that cannot change a number
currently sit inside the guarded, digested surface. Its section name is the one
`Q-G` must place: T1-only, or per-workflow and never hoisted.

### Group I — carried forward from `parameter-placement.md`

| ID | change | rule | class | breaking |
|---|---|---|---|---|
| `C-35` | De-duplicate `DEFAULT_ANCHOR` (defined twice: `metrics_definition.py:18`, `climate_figures.py:120`) (= M2) | — | MECHANISM | **no** |
| `C-36` | Move the config-key defaults out of Python (`DEFAULT_SPELL_FACTOR`, `DEFAULT_MAX_SUBBASINS_PER_BASIN`, `DEFAULT_GAUGE_SNAP_TOLERANCE_M`, `DEFAULT_HYDROGRAPHY`, `DEFAULT_BASIN_INDEX`, `DEFAULT_STATS`) (= M3) | — | MECHANISM | no — **blocked on `Q-E`** |
| `C-37` | A mechanical "declared keys ⊆ read keys" check (answers P2) | — | MECHANISM | no |
| `C-38` | Extend `scripts/split_project_config.py` (or a sibling) into a v1→v2 rewriter driven by the register above | — | MECHANISM | no |

`C-35` is the only change in this document that is unambiguously correct
regardless of how everything else resolves, and the only one that is
non-breaking and independently landable **today**.

## Proposed shape

### Project file (T1) — `snake_config_<project>.yml`

```yaml
schema_version: 2

project:
  dir: /path/to/my_project
  catalog: config/catalogs/deltares_data.yml

basin:
  region: "{'subbasin': [9.666, 0.4476], 'uparea': 100}"
  resolution: 0.00833333
  output_locations: null
  delineation:
    max_subbasins: 11
    river_uparea_km2: 32
    snap_tolerance_m: 10000
  sources:
    hydrography: merit_hydro_ihu
    basin_index: merit_hydro_index
    rivers: rivers_lin2019_v1
    lulc: vito
    lai: modis_lai
    soil: soilgrids

climate:
  sources: [era5, chirps]
  selected: era5   # null until WF0's comparison is read
  window: {start: "1990-01-01", end: "2020-12-31"}
  water_year_start: Jan

model:
  outvars: ["river discharge", "actual evapotranspiration"]

workflows:
  analyze_climate:     {enabled: true}
  build_model:         {enabled: true, config_path: ..._build_model.yml}
  analyze_projections: {enabled: true, config_path: ..._analyze_projections.yml}
  run_stress_test:     {enabled: true, config_path: ..._run_stress_test.yml}
```

### `_build_model.yml`

```yaml
engine:
  build_config: config/defaults/wflow_build_model.yml
  waterbodies_config: config/defaults/wflow_update_waterbodies.yml
simulation_window: {start: "2000-01-01", end: "2020-12-31"}
observations:
  river discharge: null    # key drawn from model.outvars
```

### `_analyze_projections.yml`

```yaml
catalog: config/catalogs/cmip6_data.yml
ensemble: cmip6
models: [...]
scenarios: [ssp245, ssp585]
members: [r1i1p1f1]
member_selection: first_available
member_overrides: {}
variables:
  precip:      # bare key = registry-resolved; declare a mapping only to override
  temp:
historical_window: {start: 1985, end: 2014}
future_horizons:
  near: {start: 2030, end: 2060}
  far:  {start: 2070, end: 2100}
relative_change: {min_reference: {precip: 0.1}, max_flagged_months: 3}
reporting:
  stats: [mean, median, std]
  save_grids: false
```

### `_run_stress_test.yml`

```yaml
experiment_name: my_experiment
seed: auto
realizations_count: 2
horizon_year: 2050
run_length: 20
run_historical: false
stress_test:
  temp:
    steps_count: 1
    transient: true
    mean: {min: [...12], max: [...12]}
  precip:
    steps_count: 2
    transient: true
    mean:     {min: [...12], max: [...12]}
    variance: {min: [...12], max: [...12]}
  spell_factors:
    dry: [...12]
    wet: [...12]
compute:
  batch_size: 4
  batch_size_max: 8
  disk_headroom_gb: null
reporting:
  surfaces:
    - id: jfm
      x: {variable: temp}
      y: {variable: precip, months: [1, 2, 3], statistic: mean}
```

### `_analyze_climate.yml`

```yaml
candidate_sources: [chirps]
```

## Open questions

| ID | question | blocks | current lean |
|---|---|---|---|
| `Q-A` | `project.dir` (N3) vs keeping `project_dir` | `C-06` | **Keep `project_dir`** as a named exemption — it is a term of art here (AGENTS.md's two-tier location rule, `warn_if_project_dir_in_repo`, every internal variable). |
| ~~`Q-B`~~ | ~~Is `model:` holding one leaf (`outvars`) an S4 violation?~~ **RESOLVED 2026-08-22**: `model:` is the engine boundary, not a group of one. See Group E. | `C-19` | — |
| `Q-I` | One variables key or two? `C-48` (analysis) and `C-50` (extraction) must not become one key whose meaning widens on upgrade — a project that set a short list for FIGURES would silently change what gets DOWNLOADED. Same cross-version meaning-swap `data_sources` was rejected for. | `C-48`, `C-50` | Lean TWO, distinctly named. Decide now even though only one ships. |
| `Q-C` | `_count` suffix vs bare plural (`realizations_count` vs `realizations`) | `C-29`, `C-31` | Undecided; `_count` is unambiguous, bare plural is shorter and YAML already distinguishes int from list. |
| ~~`Q-D`~~ | ~~Does `method:` earn a heading?~~ **RETIRED 2026-08-22**: the section is gone (`C-52`); both keys have real homes. | ~~`C-20`~~ | — |
| `Q-E` | Where does a config key's DEFAULT live: `config/advanced_settings.yml` (precedent, closed schema, already tested) or beside the key in the template? | `C-36` | **`advanced_settings`** — the only option with an existing enforcement mechanism, and the only one that could grow `C-37`. |
| `Q-F` | Does S2 actually permit `_WF1_GUARDED` to become "everything except `compute:`/`reporting:`"? | `C-04` | Unknown. **Needs a probe against the digest and freeze code before R14 promises it.** |
| `Q-H` | One `selected`, or one per consumer (`forcing` for WF1, `conditioning` for WF3)? | `C-44` | Lean ONE. CST does no local calibration, so the response surface is anchored on the historical run; letting the generator condition on a different record than the model was forced with decouples them silently. The genuine hybrid case is already met INSIDE a single store — the CHIRPS branch takes temperature, radiation and pressure from ERA5 and lapse-corrects them onto the CHIRPS grid. Splitting later is expensive, so record rather than default. |
| `Q-G` | **NARROWED 2026-08-22 by `C-55` — `compute:` is settled (workflow-local only), so this is now the `reporting:` question alone.** Under S7, how is `reporting:` placed? (a) T1-only — every workflow's performance/description keys move to the project file; (b) per-workflow and never hoisted — they nest under `workflows.<name>` and lose the freeze exemption that hoisting buys; (c) distinct names per tier. | `C-02`, `C-03`, `C-28`, `C-34` | Lean (a) for `compute:` (a thread count and a batch size are the same kind of knob and belong together), and **keep `reporting:` as it is** — WF3-owned and hoisted — since (b) would revoke the caption-edit exemption that is the whole reason it was hoisted. That makes `C-03` a no-op and `C-28` a rename onto a T1 `reporting:`. |

## Constraints

1. **AGENTS.md hard constraint (S5).** hydromt / hydromt_wflow / wflow /
   weathergenr vocabulary is used verbatim. No key inside `config/defaults/*`
   or a data catalog is renamed by this milestone.
2. **R13 is accepted.** Any change to `T1_TOP_LEVEL` (D-9.5), `SHARED_SEAM_KEYS`,
   `HOISTED_SECTIONS` or the composition invariant (D-8.1) is an **amendment to
   an accepted design**, recorded as such, not a quiet edit.
3. **Digest identity.** A key present-vs-absent — not merely re-valued — moves
   `effective_config_digest`. Every already-run experiment in every project is
   refused across this migration by construction. That is acceptable **only**
   if it happens once, which is the whole argument for bundling.
4. **Two homes for a window today.** `climate.window` (extraction) and
   `simulation_window` (model run) are necessarily separate and must stay
   visibly separate after N4 makes them look alike.
5. No change to what any workflow COMPUTES. If a number moves, the change is
   wrong.

## Decision criteria

- **D1 — Does it answer P2 mechanically?** The sharpest test inherited from
  `parameter-placement.md`: four inert-or-partly-inert parameters have been
  found by hand and zero by machine. A shape that does not make `C-37`
  feasible has not solved the problem that has real consequences.
- **D2 — Does it preserve guard semantics?** Specifically the reason
  `_WF1_GUARDED` guards `shared` leaf-by-leaf while guarding `project` whole.
- **D3 — Is the migration mechanical?** Every row of the register must be
  expressible as a pure old-path → new-path rewrite for `C-38`. A row needing
  human judgment is a design smell, not a migration step.
- **D4 — Does a new parameter now have exactly one obvious home?** The failure
  that started `parameter-placement.md` was three parameters placed by
  precedent because no rule existed.

## Success criteria

1. A user can find every knob that affects their basin, and see its default,
   without reading Python.
2. Every section name states a KIND; no section names a relationship.
3. The experiment guard's key list is DERIVED from section membership, not
   maintained by hand (`C-04`), or `Q-F` is answered and the reason recorded.
4. One command rewrites a complete v1 config set to v2 (`C-38`), and the
   `tests/data/presplit/` corpus is extended with a v1→v2 pair.
5. `pixi run test-full` green on both platforms; `check_baseline.py check`
   unchanged — a pure rename must not move a single number.

## Non-goals

- Re-opening R13's tier split, path-reference composition, or the single
  `--configfile` CLI contract.
- Any change to `config/catalogs/*`, `config/defaults/*` internals, or
  `advanced_settings.yml`'s authority boundary.
- Changing what a workflow computes. **Unamended.** If a number moves, the
  change is wrong.
- ~~Adding or removing a parameter's meaning.~~ **AMENDED 2026-08-22 (owner).**
  `C-43` and `C-45` widen `candidate_sources` into `climate.sources` and
  retire the old key, which the original wording forbade. Rather than land
  that separately and make users migrate twice, R14 admits meaning changes
  under the explicit **SEMANTIC** class. Two conditions hold for every such
  row: it must still be expressible as a mechanical rewrite (D3), and it must
  not move a number — success criterion 5 is scoped per-row, and every
  SEMANTIC row so far carries a migration invariant showing the v1 behaviour
  reproduced exactly. R13 was widened the same way, for the `wflow_outvars`
  hoist.
- Web/API concerns. The CST-API and frontend never constrain this repo, and no
  decision here is gated on whether they consume an artifact by name.

## Blast radius (re-measure before the design)

Post-R13 the surface is wider than `parameter-placement.md` §6 recorded:

- the four `*.smk` entry points and `blueearth_cst/shared/snake_utils.py`
- `blueearth_cst/shared/config_composition.py` — `T1_TOP_LEVEL`,
  `SHARED_SEAM_KEYS`, `HOISTED_SECTIONS`, the static read scan (D-9.6)
- `blueearth_cst/experiment/check_project_consistency.py` — `_WF1_GUARDED`,
  `_COPIED_CONFIG_PATH_MAP`
- `config/templates/snake_config*.template.yml` × 4
- `test_case/snake_config_*.yml` — **four multi-file sets** (baseline, baseline
  _linux, rapid, wf2_fast), 17 files
- `tests/snake_config_fixture.yml`, and `tests/data/presplit/**` (which exists
  precisely to test migration and must gain a v1→v2 pair)
- `scripts/split_project_config.py`, `scripts/plot_workflow_dag.py`
- `docs/guide/configuration.qmd`, `docs/migration-config-tiers.md`, `README.md`
- `dev/reference/workflows/*.md`, `dev/reference/naming.md`, `AGENTS.md`

## Packaging recommendation

Every change except `C-35`, `C-37` and `C-38` is breaking, and their costs are
almost entirely **shared** — one migration pass, one template rewrite, one
sweep of the fixture corpus. Landing `C-07` alone would pay the whole migration
cost for one dead key. Recommendation:

- **Now, independently:** `C-35` (non-breaking, correct under every outcome).
- **Probe before designing:** `Q-F` (`C-04`) and D3-feasibility for `C-38`.
- **One bundle, one `schema_version` bump:** everything else.

The project config carries no version key today (the `schema_version` hits
elsewhere in the tree belong to snapshot and series-identity artifacts), so the
bundle is also the moment `C-05` becomes possible.

## Next artifact

An intake + design under `design-review-loop`, on the R13 pattern:
`dev/milestones/r14/config-shape-intake.md` → `config-shape-design.md` →
review record. Not started; this document is the input to it.
