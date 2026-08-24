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
| `N1`–`N8` | proposed **naming** policy rule | `N4` — `{start, end}` windows |
| `C-01`–`C-85` | one proposed **change**, individually referable | `C-07` — delete `static_dir` |
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

**Amended 2026-08-24 by `C-77` and `C-79`.** `reporting:` leaves the config
surface entirely, so the description class has no section and no instances left
to generalize. What remains is a two-way split — identity and `compute:` — and
`C-79` is what gives `compute:` its carve-out, by excluding it from
`CONFIG_PROJECTION`. The two rows must be presented together, or S2's split has
no instances at all. That also makes `Q-F` the whole of the evidence for the
rule rather than one probe among several.

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
established domain terms (`lulc`, `lai`, `uparea`, `ssp`, `outvars`), and the
`n_` count prefix N6 adopts — added 2026-08-24 with the N6 rewrite, because on
a plain reading `n_` abbreviates "number of", and without the exemption two
policy rules would contradict each other two sections apart.

**N2 — Dimensional values carry their unit** unless a schema fixes it:
`snap_tolerance_m`, `river_uparea_km2`, `headroom_gb`.

**N3 — A key never repeats its own section.** Inside `climate:`,
`clim_historical` → `source`.

**N4 — A time span is `{start, end}` inside a `*_window:` group** — one spelling
in every file. Replaces `starttime`/`endtime` and both bare `[a, b]` year pairs.

**N5 — A name describes the VALUE, not the workflow that reads it.**
`horizontime_climate` → `horizon_year`; `clim_project` → `ensemble`.

**N6 — Counts take the `n_` prefix.** `realizations_num` → `n_realizations`,
`step_num` → `n_levels`. **Ruled by the owner, 2026-08-24**, replacing the
`_count` suffix this rule proposed until then: `_count` is not vocabulary the
owner uses, `n_` is the statistical idiom, and it reads as "number of" without
a suffix that has to be learned. `Q-C` is resolved by the same ruling.

Corroboration rather than the argument: `prepare_weagen_config.py:109` already
passes `"n_realizations": realizations_num` across the Python → R seam, so the
config and the generator stop spelling one quantity two ways. The reason is
deliberately NOT "match weathergenr" — N7 forbids a config key carrying the
current engine, and the generator may be replaced.

Rejected, with reasons, so they are not re-proposed:

| candidate | why not |
|---|---|
| `realizations` (bare plural) | terse, but a future list-valued `realizations:` collides, and the singular/plural cue carries the whole meaning |
| `realizations_num` (unchanged) | zero migration cost for this key only; the bundle is already paying for the sweep |
| `realization_num` | the repo spells member INDICES `rlz_ix` / `rlz_1`, so a singular reads as "which one", not "how many" |
| `realization_sample_num` | the sample-vs-population distinction is not live in this file |
| `ensemble_size` | `C-25` already claims `ensemble` for WF2's `clim_project`; two meanings of "ensemble" in one config set is the P3 this milestone removes |

N6 supplies the PREFIX; the noun is still the row's to choose. The second
example above is `n_levels` rather than `n_steps` for exactly that reason:
`C-31` rejects `n_steps` by name, because the value is one less than the number
of grid steps and a precise-looking prefix on a misleading noun is worse than
the name it replaces.

**N7 — A key in a shared section never names an ENGINE.** `model.outvars`, not
`wflow_outvars`. The toolbox is meant to stay flexible: wflow is the model
today, and another may demand a different set tomorrow, so a key two
workflows read must not carry the current engine in its own name. Engine
-specific *paths* are exempt inside a workflow file, because they point at
files written in the engine's schema (S5) — `engine.build_config` stays.

**N8 — A window is declared in YEARS; calendar resolution happens at the engine
seam.** A `*_window:` is `{start, end}` with integer years and BOTH ENDS
INCLUSIVE. No ISO datetime appears in a project config. Conversion to whatever
an engine wants — wflow's `starttime`/`endtime`, hydromt's time horizon —
happens at the seam that hands it over (S5), never in the user's file.

N4 fixes the SHAPE of a window; N8 fixes its TYPE and its calendar resolution.

**The years are WATER years, resolved through `climate.water_year_start`
(`C-53`).** With the default `Jan` a water year IS a calendar year, so the rule
is invisible to every project that does not set the key. With `Oct`,
`{start: 2040, end: 2050}` resolves to `2040-10-01 .. 2051-09-30` — eleven
complete water years, the same count `{2040, 2050}` gives as calendar years
today.

**Inclusive is load-bearing, not a detail.** An exclusive end would silently
shorten every existing window by a year: the baseline's `historical_window`
would fall from 17 years to 16, landing exactly ON the weathergenr floor
(`constraints.min_historical_years`) instead of one clear of it, and every
generated series would change. Inclusive is also the convention the WF2
template already documents (`historical_year_range: [1985, 2014]` — "inclusive,
clipped at 2014") and the one IPCC uses (1995–2014 is twenty years).

**A water year is labelled by the year it STARTS in.** The key is called
water_year_START and holds the start month, so labelling by start is the
internally consistent reading. Both labellings coincide under `Jan`, so this
only ever shows on a project that sets the key.

**Two mechanisms, and they are not interchangeable** — the distinction is what
keeps WF2 correct:

| mechanism | applies to | behaviour |
|---|---|---|
| **shift** | `climate.window`, WF1 `simulation_window`, WF3 `simulation_window` | the declared years ARE water years; bounds move to the water-year boundaries |
| **trim** | WF2 `reference_window`, `future_windows` | the declared years are CALENDAR; the computation keeps only the complete water years inside them — **already implemented**, see `C-74` |

Evidence the rule is affordable: every ISO bound in every shipped config —
twelve values across `historical_window` and `simulation_window` in five
configs and two templates — is `01-01` or `12-31` at `T00:00:00`. Not one
sub-annual bound exists. The datetime carries nothing the year does not.

Migration is byte-exact: `end: 2016` emits `"2016-12-31T00:00:00"`, the string
in the config today. Note that string is MIDNIGHT on 31 December, not
end-of-day; the converter reproduces it verbatim rather than "fixing" it, or a
number moves.

**Cost, recorded rather than hidden:** a project can no longer express a
sub-annual bound in its own config. Nothing shipped uses one, and the escape
hatch if a basin ever needs one is the engine's own config under S5.

**Second cost, RULED by the owner 2026-08-24: N8 is NOT number-preserving for a
project that sets `water_year_start`, and `C-38` refuses rather than rewriting
it silently.** Today `historical_window` and `simulation_window` are explicit
CALENDAR bounds, and `water_year_start` reaches only aggregation anchors and
weathergenr's `year_start_month` — never the extraction or run bounds. After
the **shift**, a project with `water_year_start: Oct` migrates
`{start: 2000, end: 2016}` to `2000-10-01 .. 2017-09-30`: a nine-month move on
both ends, reaching into a calendar year whose observed record may not exist.
That changes the extraction window, hence the generator input, hence every
number.

"Invisible to every project that does not set the key" is true and is not its
converse. `config/templates/snake_config.template.yml:91` ships
`#water_year_start: Oct` as a commented example, so this is a REACHABLE
configuration rather than a hypothetical.

There is no number-preserving migration for that case — the old bounds are
calendar and the new ones are water-year by construction. **Ruled: `C-38`
REFUSES when `water_year_start != Jan`**, naming the window it will not
rewrite, rather than migrating it silently. Such a project is migrated by hand,
with the owner deciding whether the shifted window is the one they want.

**This is the second row needing that treatment** (`C-69` is the first), which
makes it a FEATURE of the migrator rather than a special case: `C-38` needs a
per-row "mechanical, but tell the user what changed" hook, and the register
needs a column saying which rows use it.

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
| `C-03` | ~~Generalize `reporting:` from WF3-only to any workflow file~~ — **WITHDRAWN 2026-08-24** by `C-77`: there is nothing left to generalize | S2 | NEW | — |
| `C-04` | Replace hand-maintained `_WF1_GUARDED` with "guard everything except `compute:`/`reporting:`" — after `C-77` the exception list is `compute:` ALONE (`C-79`) | S2, S3 | MECHANISM | behavior-visible |
| `C-05` | Add `schema_version: 2` to the project file; refuse a v1 set with a message naming the migration command | — | NEW | yes (by design) |
| `C-78` | `HOISTED_SECTIONS` empties; retire the hoist mechanism (R13 D-10.4 amendment) | S7 | MECHANISM | no |
| `C-79` | Exclude `compute:` from `CONFIG_PROJECTION`, so performance keys leave configuration identity | S2 | MECHANISM | no |
| `C-85` | `snake_config_*.yml` → `project_config_*.yml` across the repo, `.gitignore` un-ignore glob included; **rides the bundle** | N5 | RENAME (file surface) | yes — **RULED 2026-08-24** |

### Group B — `project:`

| ID | change | rule | class | breaking |
|---|---|---|---|---|
| `C-06` | `project.project_dir` → `project.dir` | N3 | RENAME | yes — **blocked on `Q-A`** |
| `C-07` | **Delete `project.static_dir`** (= M1) | — | DELETE | yes |
| `C-08` | ~~`project.data_sources` → `project.catalogs.spatial`~~ — **superseded by `C-40`** | S6, N1 | RENAME | yes |
| `C-09` | ~~`project.data_sources_climate` → `project.catalogs.climate`~~ — **superseded by `C-39`** | S6, N1 | RENAME | yes |
| `C-39` | Move the climate catalog OUT of the project file: `project.data_sources_climate` → `catalog:` in `_analyze_projections.yml` | S1, S6 | REGROUP | yes |
| `C-40` | `project.data_sources` → `project.catalog` (single leaf, since `C-39` empties the group) | S4, S6, N1 | RENAME | yes |

**S7 constrained `C-02`, `C-03`, `C-28` and `C-34` together — DISCHARGED
2026-08-24.** As drafted, this document placed `compute:` in both the project
file (`C-21`) and the WF3 file (`C-34`), and `reporting:` in both the WF2 file
(`C-28`) and the WF3 file (already there). Both collided with the closed hoist
map. The collision is now gone from both ends rather than ruled on: `C-55`
dissolved T1 `compute:`, and `C-77` removes `reporting:` from the config
surface altogether — which withdraws `C-03` and `C-28` and empties
`HOISTED_SECTIONS` (`C-78`). `Q-G` is RETIRED; there is no question left for it
to answer. `C-02` survives and is unblocked.

#### The file is named after the program that reads it — `C-85`

**Ruled by the owner, 2026-08-24:** bundle the `snake_config_` →
`project_config_` rename into R14. It was boarded 2026-08-19
(`t2608191733a`, from the sample-dataset scoping) with a measured blast radius
and a rationale, but never ruled on; this is the ruling.

The rationale is N5 applied to a FILENAME rather than a key: *"Snakemake is one
tool this repo happens to use; what the file configures is the project — the
basin, the windows, the models, the experiment. `project_config_` says what the
file IS; `snake_config_` says which program reads it."* That is the same test
`C-19` applies to `wflow_outvars` and `C-25` to `clim_project`, one level up
the tree. The engine could change and the file would keep its meaning.

**Why it rides the bundle rather than landing beside it.** Both changes break
the same thing — a user's `--configfile` invocation — and this document's own
packaging argument is that a break of that kind is paid ONCE. Three specifics
make the bundling more than tidiness:

- `C-84` adds a template that does not exist yet
  (`snake_config.analyze_climate.template.yml`). Land R14 first and the
  milestone SHIPS A NEW FILE under the prefix it is retiring. Bundled, it is
  born as `project_config.analyze_climate.template.yml`.
- `C-38` is a v1→v2 rewriter over exactly the file set being renamed. Bundled,
  it renames and rewrites in one pass and is written once against final names.
  Split, it is written twice.
- The migration note is one note. `AGENTS.md` requires one for a
  contract-surface rename, R14 owes one anyway, and
  `docs/migration-workflow-names.md` is the precedent for both.

**The cost, recorded rather than hidden.** R14 is SCOPING and not accepted, so
this widens an unaccepted scope — the failure mode R13 met when arbitration
pulled the `wflow_outvars` hoist in and bought two baseline passes. It is
accepted here because `C-85` adds no register row that `C-38` must reason
about: it changes no key, no value and no digest input, so it cannot move a
number and cannot interact with any other row. It is breadth, not depth.

**The one thing this ruling does NOT settle**, and the design must: whether the
rename covers only the `snake_config_` FILE prefix or also the identifiers
carrying it (`snake_config_fixture`, fixture and variable names across 33 test
modules). Grep first, triage second — not every occurrence of the string is a
filename. The board note has carried that question open since 2026-08-19.

**The mechanical trap, which is why this cannot be done a file at a time.**
`.gitignore:130-131` ignores `test_case/` wholesale and re-admits the seeds
through `!test_case/snake_config_*.yml` alone. Rename the files without moving
the glob IN THE SAME COMMIT and they go untracked in silence: `git status`
reports the old paths deleted and never lists the new ones. Verify with
`git ls-files test_case/`, which is the command that does not lie here.
`AGENTS.md` already warns about this for NEW seed configs; a rename is the same
trap from the other side, and `AGENTS.md`'s own wording ("keep the
`snake_config_` prefix on any new seed config") is one of the 221 occurrences
this row updates.

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
| `C-18` | ~~`shared.historical_window.{starttime,endtime}` → `climate.window.{start,end}`~~ — **superseded by `C-70`**, which changes the TYPE as well as the spelling | N4 | RENAME | — |
| `C-43` | New `climate.sources` — a flat LIST of candidate datasets with no privileged element. Absorbs `candidate_sources`, moving it T2 → T1 and widening its meaning from "extras besides the primary" to "the full candidate set" | S1, charter | **SEMANTIC** | yes |
| `C-44` | `shared.clim_historical` → `climate.selected`, with requiredness that varies by consumer (below) | N5 | **SEMANTIC** | yes |
| `C-45` | Retire `workflows.analyze_climate.candidate_sources`; refused at parse time, as `start_month_hyd_year` is | — | DELETE | yes |
| `C-46` | WF0 figure and comparison-table ordering follows `selected` when set, else declaration order | — | behavioural | no |
| `C-47` | Adopt the `climate:` CHARTER (below) as the section's definition in the template and `dev/reference/` | S1, N5 | NEW | no |
| `C-48` | Give the ANALYSIS variable set a config surface — selection from a registry, defaulting to today's `precip`/`temp`/`pet` | S2, P1 | NEW | no |
| `C-49` | Move the `CLIMATE_VARS` registry out of Python so the default is visible (extends `C-36`) | — | MECHANISM | no |
| `C-50` | Give the EXTRACTION set a config surface: derived, not declared. Designed now, behaviour deferred — narrower-than-default is REFUSED at parse time until it lands | S5, N7 | NEW | no |
| `C-53` | `shared.water_year_start` → `climate.water_year_start` (amends the `C-47` charter) | S1, charter | REGROUP | yes |
| `C-70` | `shared.historical_window.{starttime,endtime}` ISO → `climate.window: {start, end}` years | N8 | **SEMANTIC** | yes |

`C-70` is filed HERE rather than in Group B because the `C-40`–`C-47` climate
charter has already moved `historical_window` into `climate:`; `C-18` is the
row it supersedes. The ROW is the same either way, but `C-38`'s rewriter reads
the register to learn which FILE a path lives in, so the group has to be the
one that owns the key.

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
| | WF3's `simulation_window` (was `horizon_year` + `run_length`; `C-67`) |

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

**`C-48` lost its destination 2026-08-24.** `C-77` removes `reporting:` from
the config surface entirely and `Q-G` is retired, so the sentence above no
longer resolves: the section this key was to live in does not exist, and there
is no open question that would place it. The S2 CLASSIFICATION is untouched —
which variables get drawn still cannot move a number — but the row now needs
its own destination ruling, which this walkthrough did not take. Recorded here
rather than decided; it is an input to the intake, not a row that quietly
changed.

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

*(And then RETIRES, 2026-08-24: `C-77` removes `reporting:` from the config
surface, so the narrowed question has nothing left to ask. The two halves of
`Q-G` were closed by two different rulings a day apart, neither of which
answered it as posed.)*

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
| `C-24` | ~~`simulation_window.{starttime,endtime}` → `{start, end}`~~ — **superseded by `C-71`**, which changes the TYPE as well as the spelling | N4 | RENAME | — |
| `C-71` | WF1 `simulation_window.{starttime,endtime}` ISO → `{start, end}` years | N8 | **SEMANTIC** | yes |

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

**Reversed 2026-08-24 by `C-67`.** WF3's window IS now declared, and takes the
same `simulation_window` spelling, so the asymmetry above closes rather than
being tolerated. The reasoning that kept the NAME survives the reversal intact
— see the `C-67` subsection under Group H, which explains why
`reference_window` still loses to `simulation_window` even though the second
disambiguation has gone live. `C-24` is superseded by `C-71`, which changes the
window's type as well as its spelling.

### Group G — `_analyze_projections.yml`

| ID | change | rule | class | breaking |
|---|---|---|---|---|
| `C-25` | `clim_project` → `ensemble` | N1, N5 | RENAME | yes |
| `C-26` | ~~`historical_year_range` → `historical_window`~~ — **superseded by `C-59`** | N4 | RENAME | yes |
| `C-27` | ~~`future_horizons.<name>: [a, b]` → `{start, end}`~~ — **superseded by `C-60`** | N4 | RENAME | yes |
| `C-59` | `historical_year_range: [a, b]` → `reference_window: {start, end}` | N4, N5 | RENAME | yes |
| `C-60` | `future_horizons.<name>: [a, b]` → `future_windows.<name>: {start, end}` | N4, N5 | RENAME | yes |
| `C-61` | `future_windows` becomes a LIST; the per-window name is OPTIONAL and defaults to `<start>-<end>` | N4 | **SEMANTIC** | yes |
| `C-62` | `relative_change.min_reference` → `relative_change.min_denominator` | N5 | RENAME | yes |
| `C-63` | Group the three member keys: `members` / `member_selection` / `member_overrides` → `members.{preference,selection,overrides}` | S4, P4 | **SEMANTIC** | yes |
| `C-64` | `min_denominator` moves INTO the variable registry as per-variable metadata (with `C-57`) | S1, authority | REGROUP | yes |
| `C-65` | `max_flagged_months` → `advanced_settings.constraints.max_flagged_months` | authority | DELETE | yes |
| `C-66` | `relative_change:` dissolves — both its keys have real homes | S4 | DELETE | yes |
| `C-28` | ~~`stats` → `reporting.stats`~~ — **WITHDRAWN 2026-08-24**: `C-77` removes the destination; `stats` stays at `workflows.analyze_projections.stats`. The `save_grids` erratum below still stands | S2 | REGROUP | — |
| `C-57` | `variables:` gains a SHORT FORM — a bare key resolves through a registry; a name the registry lacks and that declares no spec is refused | P1 | **SEMANTIC** | no (additive) |
| `C-58` | `canonical` leaves the USER surface; it stays in the registry | P1 | RENAME | yes |
| `C-74` | WF2's windows stay CALENDAR years — decision recorded, no change | — | (decision) | no |

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

#### What `relative_change` and `member_overrides` are — `C-62`, `C-63`

**PROPOSED.** The owner asked what these keys do; the rows below follow from
the answers rather than from a ruling.

**`relative_change` is the dry-month rule** (`dry_month.py`, design §5.6,
ruling A2) — a guard against dividing by a near-zero reference, because "a 0.2
mm/day reference January turns a trivial absolute change into a four-figure
percentage". `min_reference` is the threshold, strictly below which a month is
flagged; a flagged month emits NaN for the ratio but KEEPS the absolute change
with status `reference_below_threshold`, since the difference still carries
information. `max_flagged_months` (3) is where a dry season stops being normal
and the reader is told at combination level rather than by counting
footnotes. A `change: relative` variable outside the shipped set gets no
default and must supply its own.

`C-62` follows from `C-59`, and is a collision THIS DOCUMENT created: renaming
`historical_year_range` to `reference_window` puts `min_reference` in the same
file as a key about a reference WINDOW, so it now reads as "minimum reference
window". It is the divisor, so `min_denominator` says what it is.

**`member_overrides` replaces the global member preference for one model.**
`members` is an ORDERED PREFERENCE rather than a set, `member_selection:
first_available` takes at most one member per model, and an override lets a
model that publishes `f2` variants be handled beside models that publish `f1`
(`resolution.py`; both policy keys are optional, so no existing config moves).

`C-63` groups the three: they are one concept spread flat, which is the P4
pattern `basin.gauges` had. It also makes the ordered-preference semantics
VISIBLE — today that fact lives only in a code comment (t2608192107), which is
exactly the discoverability complaint P1 makes.

```yaml
members:
  preference: [r1i1p1f1, r1i1p1f2]
  selection: first_available
  overrides:
    MOHC/UKESM1-0-LL: [r1i1p1f2]
```

The asymmetry with plain-list `models:` and `scenarios:` is real but honest:
members carry a policy, those do not.

#### `relative_change` leaves the project surface — `C-64`–`C-66`

**Ruled by the owner, 2026-08-22:** it is an advanced setting, not something
to touch often. Agreed — but the two keys are different KINDS and go to
different places.

**`min_denominator` is per-variable metadata (`C-64`).** `dry_month.py` says
so: *"Keyed by the variable's canonical name, in its canonical units"*, and a
relative variable outside the shipped set gets NO default because *"falling
back to precipitation's 0.1 would apply a rainfall threshold to an unrelated
quantity in unrelated units."* That is an attribute of the variable, like
`units` and `change`, so it belongs in the `C-57` registry beside the
`change: relative` declaration that makes it necessary. It also strengthens
the guarantee: "a relative variable must carry a threshold" becomes checkable
when the REGISTRY is parsed rather than at DAG build.

Sending it to `advanced_settings.yml` instead was rejected for a specific
trap: adding a relative variable would then REQUIRE editing a tracked toolbox
file — not optional tuning but a hard prerequisite. That is the `C-54`
objection with its polarity flipped.

**`max_flagged_months` is a genuine advanced setting (`C-65`)**, and
`constraints.min_historical_years` is its exact precedent: both are "when does
the toolbox stop treating this as normal and say so". `constraints:`, not
`defaults:` — a project should not override it.

The cost of splitting them is that someone tuning the dry-month rule looks in
two places. Accepted: they are related by RULE, not by KIND, and
`advanced_settings.yml`'s top level is a closed AUTHORITY-based schema
(`constraints` / `defaults` / `runtime`), so a topic-shaped `relative_change:`
block there would break its own organising principle.

`C-66` follows. This is the third section in the document to dissolve after
`method:` (`C-52`) and T1 `compute:` (`C-55`), and the first outside T1 — each
time because the section was holding keys that had better homes rather than
naming a kind.

#### Erratum — `save_grids` does not exist (`C-28`)

**Owner, 2026-08-22:** `save_grids` sits oddly under `reporting:` — it is
about keeping raw data, not about reporting.

Correct, and more so than the objection assumed: **the key was removed in R08
(S8-08c) and is not part of the config surface at all.**
`gridded_outputs.py:7` lists it in `REMOVED_GRIDDED_KEYS`; `save_grids: true`
RAISES and `save_grids: false` warns as stale (`docs/migration-r08-wf2.md`).
The rejection message gives the reason, which is the owner's reasoning
reached independently: *"`raw/{series_key}.nc` is the basin slice on the
source grid and is ALWAYS written, so the gridded series was a near-duplicate
of it."* Raw is now always kept, so the switch had nothing left to switch.

**This is a defect in this register, not a misplacement.** `C-28` was seeded
from `parameter-placement.md`'s appendix, measured 2026-08-12, whose own
header says *"Re-measure rather than trust it."* That instruction was not
followed. The row is corrected in place rather than superseded, because it
was never valid.

**Action, before the intake:** RE-MEASURE the whole parameter inventory
against the code. The appendix seeded other rows in this document and at
least one of its keys no longer exists; the failure is systematic, not
isolated. The `Blast radius` section already says re-measure, but it means
FILES — this is about KEYS, and it is the more dangerous of the two, because
a stale file path fails loudly and a stale key silently proposes work on
something that is not there.

**`stats` survives, and stays reporting-class — on precedent, not
assertion.** It selects which ensemble statistics summarise an unchanged set
of change factors (`None` = the v2.0 default of mean, median, std). WF3's
`reporting.surfaces` already chooses which axes and statistics summarise an
experiment and is deliberately OUTSIDE configuration identity, so "which
summary is presented" is treated as reporting in this repo even when the
summary is numeric. `stats` is the same shape.

#### Reference and future windows — `C-59`, `C-60`

**Ruled by the owner, 2026-08-22.** `reference_window` fits the terminology
better than `historical_window`, and `future_windows` matches it.

`C-59` also corrects a defect THIS DOCUMENT introduced. `historical_window`
was a poor name for WF2: its baseline is bounded by the CMIP6 historical
experiment, which stops in 2014, while `climate.window` is the OBSERVED
record — two different "historical" periods, different sources, different
bounds, which `analyze_projections.smk:180` actively compares and warns about
when they stop aligning. `reference_window` names what the period is FOR (the
reference that change is computed against, the domain's own term) rather than
what era it sits in.

It closes a loop too. `reference_window` was considered for WF1's
`simulation_window` and rejected, because "reference" was not the live
distinction in that file. In WF2 it IS the live distinction — reference versus
future is what the workflow computes — so this is the better claim on the
name, and it settles the WF1 question permanently. The word appears in both
files' prose without ambiguity, because WF2 builds no model and WF1 computes
no change factors.

`C-60` gives N4 a clarification worth stating outright: **a window is a
PERIOD, a horizon is a YEAR.** Today `future_horizons` holds periods while
`horizontime_climate` holds a year, under one word. After `C-30` and `C-60`
the division is clean, and WF3 keeps `horizon_year` as the only surviving
"horizon". *(Cleaner still after 2026-08-24: `C-67` supersedes `C-30` and
deletes the key rather than renaming it, so NO "horizon" survives on the config
surface — WF3 declares a `simulation_window` like WF1. The clarification the
row makes stands; it simply no longer has an exception to carve out.)*
Different names also stop implying a coupling that does not
exist: WF3's forcing window is computed INDEPENDENTLY of `future_windows`,
and the two matching in a config is a convention the configs document, not a
mechanism.

#### Naming a future window is optional — `C-61`

**Ruled by the owner, 2026-08-22:** a user specifying four or five decades
should not have to invent a label for each. Pass the dates; the name is
derived. One less thing to think about.

This costs less than it looks, because the name is ALREADY decorative in the
path. `projection_figures.horizon_directory` returns
`<sanitized-name>-<start>-<end>`, and its docstring gives the reason: *"The
years are in the directory name, not only the horizon's label, because a
project that redefines `far` from 2070-2090 to 2060-2080 would otherwise
overwrite the old figure in place and leave nothing saying the window
moved."* Dropping the label turns `near-2030-2060` into `2030-2060`, which
preserves that disambiguation — it becomes the WHOLE identity rather than a
suffix — and the existing duplicate check still catches two identical
windows, which is the correct collision.

```yaml
future_windows:
  - {start: 2030, end: 2060}
  - {start: 2070, end: 2100, name: far}    # optional
```

A LIST rather than a mapping, so configured order is native rather than
resting on insertion order, which `figure_relative_paths` currently depends on
for its stable reading order.

**Considered and rejected:** `future_windows: ["2030-2060", "2070-2100"]`.
Terser, and `parse_horizon_period` already accepts that string form — but
`reference_window: {start, end}` sits three lines above in the same file, and
two spellings for one concept is the P3 this milestone keeps removing. N4
wins over terseness.

**Consequence to carry into the design:** WF2 figure directories change name,
and `WF2_FIGURE_RELATIVE_PATHS` is threaded into rule 2.06 as a `params:`
value, so the rule re-triggers. Expected for a renaming milestone, but it is a
TREE-SHAPE change — `semantic_tree_diff.py` territory, not just a config diff.

#### Why WF2's windows stay calendar — `C-74`

**Asked by the owner, 2026-08-24: which is consistent with IPCC?** Calendar,
and the toolbox already resolves the water year one layer down, which is the
stronger reason. This is the **trim** half of N8's two-mechanism table.

- IPCC/AR6 reference periods are calendar-year and inclusive — 1850–1900,
  1995–2014, 2021–2040 / 2041–2060 / 2081–2100 — and the CMIP6 historical
  experiment ends 2014-12-31, a calendar boundary. WF2's own template already
  encodes it: `historical_year_range: [1985, 2014]  # inclusive, clipped at 2014`.
- `wiki/methods/climate-projection-processing.md` names the hazard directly:
  *"calendar arithmetic on unconverted models — many CMIP runs use noleap or
  360-day calendars; monthly grouping before calendar reconciliation produces
  silently misaligned baselines."*
- **Decisive:** `get_change_climate_proj.hydrological_year_bounds()` already
  takes the calendar-sliced data and trims it to COMPLETE hydrological years
  using `water_year_start`, dropping a leading partial year; the EFFECTIVE
  window is then reported in the `reference_window` / `horizon_window` columns
  of `change_factor_table.py` so the annotation matches the numbers used.

WF2 therefore already runs "declare calendar, compute in water years". Making
its config declare water years would apply the offset TWICE. `C-74` records
this as a decision so it is not re-proposed as an oversight.

### Group H — `_run_stress_test.yml`

| ID | change | rule | class | breaking |
|---|---|---|---|---|
| `C-29` | `realizations_num` → `n_realizations` | N6 | RENAME | yes — **RULED 2026-08-24** (was `realizations_count`) |
| `C-30` | ~~`horizontime_climate` → `horizon_year`~~ — **superseded by `C-67`** | N1, N5 | RENAME | — |
| `C-31` | `stress_test.<var>.step_num` → `n_levels`, with `n_levels = step_num + 1` | N6 | **SEMANTIC** | yes — **RULED 2026-08-24** |
| `C-32` | `stress_test.<var>.transient_change` (boolean) → `trajectory: transient \| constant` (enum) | N3, N5 | **SEMANTIC** | yes — **RULED 2026-08-24** |
| `C-33` | `stress_test.{dry,wet}_spell_factor` → `spell_factors.{dry,wet}` | S4 | REGROUP | yes |
| `C-34` | `batch_size`, `batch_size_max`, `disk_headroom_gb` → `compute.*` | S2, S3 | REGROUP | yes — **RULED 2026-08-24** |
| `C-77` | `reporting:` leaves the project config surface entirely | scope | **DELETE** | yes — **RULED 2026-08-24** |
| `C-67` | `horizontime_climate` + `run_length` → `simulation_window: {start, end}` | N4, N8 | **SEMANTIC** | yes — **RULED 2026-08-24** |
| `C-68` | `stress_test:` → `climate_perturbations:` | N3 (file-scope) | RENAME | yes — **RULED 2026-08-24** |
| `C-69` | `run_historical` deleted; `st_0` is always produced | S2, P2 | **DELETE** | yes — **RULED 2026-08-24** |
| `C-81` | Add `weathergen_config:` — a PATH key for the generator's own config, mirroring WF1's two; the referenced file joins `CONFIG_REFERENCES` | S5 | NEW | yes — **RULED 2026-08-24** |
| `C-82` | `generate_weather.parallel`, `n_cores` → `compute:` | S2, S3 | REGROUP | yes — **RULED 2026-08-24** |

`C-33` keeps the existing rationale intact — the spell factors are not
perturbation axes and must not read as siblings of `temp:`/`precip:`; a named
`spell_factors:` group says that structurally instead of in a comment.
`C-34` is S2's second payoff: three WF3 keys that cannot change a number
currently sit inside the digested surface.

**Erratum on `C-34`, 2026-08-24.** The row originally said these keys "sit
inside the guarded, digested surface", and named its section as the one `Q-G`
must place. Digested yes — `CONFIG_PROJECTION` carries
`workflows.run_stress_test` whole (`run_stress_test.smk:61-65`), so a
`batch_size` edit moves `effective_config_digest`. Guarded NO: `_WF1_GUARDED`
names only `project`, `shared.basin`, `shared.wflow_outvars` and
`workflows.build_model`, never WF3. The S2 payoff is real but it is a DIGEST
payoff, not a guard one — which is exactly what `C-79` collects. And the
section needed no `Q-G` ruling in the end: `C-55` dissolved T1 `compute:`, so a
workflow-local `compute:`, nested under its own file and never hoisted,
satisfies S7 outright.

#### `experiment_name` and `seed` stay as they are — and `experiment_name` dents S2

**Ruled by the owner, 2026-08-24: both are fine.** `seed` still moves file
under `C-51`; only its spelling is settled.

Recorded because it is a hole in the load-bearing rule, not because the name is
interesting: **`experiment_name` belongs to none of S2's three classes.**
Changing it does not change the numbers of an experiment — it starts a
DIFFERENT experiment. It is not performance and it is not description. S2
catches it only because "identity" is defined as *everything not named below*,
which is the same residual-bag criticism S1 levels at `shared:`.

One key is not a reason to add a fourth class. It IS a reason to answer `Q-F`
with a probe rather than an argument: "guard everything except `compute:` and
`reporting:`" is a claim that S2 actually partitions the surface, and here is
one key it only appears to.

#### The step count is off by one from its own name — `C-31`

**Ruled by the owner, 2026-08-24: `n_levels`, as a SEMANTIC row.**
`stress_test_grid()`'s docstring: *"Per-axis step count is `step_num + 1`
(endpoints inclusive)"*. So baseline `precip.step_num: 2` with `min: 0.7` /
`max: 1.3` produces THREE levels — 0.7, 1.0, 1.3 — which is why `st_2` is the
identity member in the `t2608151154` measurement. Renaming it `n_steps` would
make a misleading name look precise.

`n_levels: 3` says three levels and means three. The migration invariant is
`n_levels = step_num + 1`, the grid is provably unchanged, and the `+ 1` leaves
`stress_test_grid()` rather than living on as arithmetic between the config and
the code. A user choosing a perturbation grid thinks in levels, and the
invariant is exactly the mechanical rewrite D3 asks for.

**Considered and rejected: `n_intervals`** — a pure RENAME with an identity
invariant, which keeps today's semantics and names them honestly. Cheaper as a
migration row, but it preserves the mental `+ 1` at every reading, and the
whole point of touching the key was that nobody performs that addition
reliably. The SEMANTIC row buys the fix outright.

This is the second SEMANTIC row in the milestone whose justification is that a
name and its value disagree; `C-61` was the first. Both are admitted under the
amended non-goal, and both carry an invariant showing the v1 behaviour
reproduced exactly.

#### The forcing window becomes a declared window — `C-67`, `C-72`, `C-73`

**Ruled by the owner, 2026-08-24.** `horizon_year` and `run_length` merge into
one declared `simulation_window: {start, end}`, the same spelling WF1 uses.

This reverses a position recorded 2026-08-22 ("not unified now, because WF3's
window is deliberately derived rather than declared"), and the reversal is
supported by what the code actually reads. `horizontime_climate` has exactly
three consumers and NOT ONE of them wants the midpoint:

| consumer | needs |
|---|---|
| `downscale_climate_forcing.py:78` → `forcing_window()` | the window |
| `batch_sizing.measure_member_footprint` → `forcing_window_years()` | the window |
| `prepare_weagen_config.compute_nr_years()` | the END only |

(`write_experiment_config.py:68` names the key in a docstring example, not a
read.)

**It deletes a documented foot-gun.** Today `start = H - ceil(L/2)` and
`end = H + round(L/2)`, so `forcing_window.py:31` has to warn that
`run_length: 8` at horizon 2050 gives 2046..2054 — NINE calendar years — and
`snake_config_rapid.yml` has to tell users to keep `run_length` even because
"7 and 8 both yield the same 9-year window and the odd value just misreports
itself." A declared window says 2070–2086 and runs 2070–2086.

**It also removes an inconsistency between two live functions.**
`compute_nr_years` uses `ceil(H + L/2)` while `forcing_window_years` uses
`round(L/2)`, so the two derive different implied end years for `run_length` in
{5, 9, 13, ...}. The fix is DELETION, not harmonization: with the window
declared there is only one derivation left.

The three functions become two (`C-72`, `C-73`):

| today | after |
|---|---|
| `forcing_window_years(H, L)` | **deleted** — the config declares it |
| `forcing_window(H, L)` → ISO pair | a pure years-to-ISO formatter, now SHARED with WF1 under `C-71` |
| `compute_nr_years(H, L)` | `n_years(end) = end - 2010 + 2`, no `ceil` |

They are NOT merged into one function: a window and a series length are
different questions, and fusing them would repeat the mistake `shared:` made.

**Migration invariant.** `{start: H - ceil(L/2), end: H + round(L/2)}`
reproduces the run window exactly. The generator's series length becomes
`end - 2010 + 2`, which differs by one year only for the odd `run_length`
values where the two functions already disagree — and **no shipped config uses
one** (baseline 16, baseline_linux 20, rapid 8, wf2_fast 20, fixture 10, all
even). Recorded as a per-row exception to success criterion 5 rather than
hidden.

**It settles the WF1 naming question permanently.** The 2026-08-22 record said
`reference_window` would become the better name for WF1 IF WF3's window ever
became explicit. It has — but `reference_window` now belongs to WF2's CMIP6
baseline (`C-59`), so moving WF1 onto it would create a genuine cross-file
collision between two different "reference" periods. `simulation_window` in
BOTH WF1 and WF3 is one spelling for one concept — the period the model runs —
disambiguated by the file the reader is standing in, which is the same test
that kept the name in the first place.

**One asymmetry survives and is deliberate:** WF1's window is a period of
OBSERVED record and WF3's is a period of GENERATED series. Same kind, same
spelling, different provenance; the file says which.

#### `transient_change` is a boolean where the method has a type — `C-32`

**Raised by the owner, 2026-08-24:** "this isn't the most elegant/user-facing
pick for the operation ... is the value applied over the full series? or
applied as a linear change per year?" **Ruled the same day:
`trajectory: transient | constant`.**

The note already specifies this, and specifies it as a TYPE rather than a flag
(`docs/cst-toolbox-technical-note-2025.md`, the Annex, *Workflows and Tasks*):

> `Change_step_type`: transient (default) or constant. The transient change
> applies change factors in a gradually increasing manner, starting from no
> change in the first analysis year. In contrast, the constant change applies
> the same change factors over the entire analysis period.

So the CONFIG diverged from the spec, not the other way round. This row is
SEMANTIC rather than a rename because the value's TYPE changes — boolean to
enum. Migration invariant: `true → transient`, `false → constant`, nothing else
moves.

**Why the key is not `Change_step_type`, `change_type` or anything with
"step".** `C-31` has just made `n_levels` the grid vocabulary, so a key
carrying "step" would now read as if it were about grid steps — the note's own
name became actively misleading the moment `C-31` landed. "change" is WF2's
word for change factors, and inside `climate_perturbations:` it restates the
section (N3). `trajectory` says what the value is about: how the perturbation
evolves across the run.

**Why an enum rather than a better-pointing boolean.** A boolean makes the
reader know which way `true` points, and it cannot grow a third profile without
a second boolean. The two values are the two alternatives the owner stated, and
the note names them.

**Considered and rejected:**

| candidate | why not |
|---|---|
| `trajectory: gradual \| immediate` | the note's OTHER wording (§1.3.1, "gradually over time or immediately from the start"); plainer for a non-specialist, but diverges from the generator's own `temp_transient` argument, so the seam would translate |
| `trajectory: ramp \| step` | crispest signal language, but "step" collides with `C-31`'s grid vocabulary |
| `ramp: true \| false` | keeps a boolean, just one that points the right way; inherits every problem above |

**Erratum, note vs code.** The Annex says `transient` is the DEFAULT. The code
deliberately refuses a missing value (`prepare_weagen_config.py:38`, "refusing
a silent default"), and the code is right: a silent default here moves numbers.
The note is the stale side. `C-32` keeps the refusal — `trajectory:` is
REQUIRED on both axes — and `C-75` corrects the note.

**An asymmetry inside one section, worth stating rather than discovering.**
`trajectory:` is refused when missing while `spell_factors` (`C-33`) default
silently to twelve 1.0s. That is defensible — the spell factors have an
identity value and `trajectory` has none — but it is undocumented today, and
`C-33`'s regroup is the moment to say so in the template.

#### `stress_test:` names the process, not the parameters — `C-68`

**Raised by the owner, 2026-08-24:** "stress test is the name for the entire
process. Here we are discussing the perturbation parameters." The same
file-scope reading of N3 that settled `simulation_window`: the section repeats
its own file's subject.

**Ruled by the owner, 2026-08-24: `climate_perturbations:`.**

- **`climate_perturbations:`** — chosen. The toolbox's own vocabulary
  ("perturbs local climate over a temperature × precipitation grid",
  AGENTS.md), and it correctly covers the section's NON-AXIS contents: the
  spell factors are perturbations that add no grid member, which is why
  `perturbation_grid:` would be wrong.
- `perturbations:` — rejected as terser but weaker: nothing else in the file is
  perturbed, so "climate" is not strictly disambiguating, but the section is
  read alongside a `climate:` section in the project file and the longer name
  says which subject it belongs to.
- `climate_change:` — **rejected on method grounds.** CST is scenario-neutral
  by construction: the grid is deliberately NOT a climate-change projection,
  and WF2 already owns change factors. Naming the grid `climate_change`
  misrepresents the method to the next reader.

#### What `run_historical` actually is, and why it goes — `C-69`

Asked by the owner, 2026-08-24: "is this a useful parameter or not?" **Ruled
the same day: delete it; `st_0` is always produced.**

It sets `ST_START = 0` (`run_stress_test.smk:204-205`), which admits member
`st_0`. That is **not** the historical record: `st_0` is the stochastically
GENERATED series over the same future window as every other member, with no
perturbation applied. WF1 already owns the historical run. The name is wrong
three ways — not historical, not a run toggle, and what it selects is a member.

**It is not a free knob: it silently governs 2 of 11 discharge metrics.**
`export_wflow_results.py:357` fixes the class-C month once from `st_0` — pick
the wettest and driest month from the baseline, then evaluate THAT month for
every member, so the surface shows how a given month responds rather than
conflating it with the month itself moving. With `run_historical: false`,
`wet_month` / `dry_month` stay `None` and `q_wettest_month_mean` /
`q_driest_month_mean` are never emitted.

That was a live defect at R11 P3 — `interchange_contracts.py:989`: *"a seed
config with `run_historical: false` dropped the st_0 baseline ... 180 rows and
two of eleven metrics gone, with this validator green."* The check that now
catches it, `validate_hm7`, is **test-time only** (`export_wflow_results.py:315`
— "its 'no rows' check is never invoked at run time"), so a real run still
loses them silently.

Two more facts pointing the same way:

- The shipped **template default is the lossy `false`**, as are
  `baseline_linux`, `wf2_fast` and the test fixture.
- `snake_config_rapid.yml:14` already tells users to set it true: *"st_0 is
  what the two class-C month indicators are derived FROM, so `false` drops 2 of
  11 q metrics with nothing reporting it."*

**Cost of always producing `st_0`:** one member in `ST_NUM + 1` — on the
baseline grid (2 temp × 3 precip = 6) that is 1 run in 7, ~14%.

**It is robust to how `t2608151154` resolves.** That item measured `st_0`
against the grid's identity member `st_2`: five of eleven q metrics move by a
factor, worst −69.7%. If it is resolved by re-anchoring the class-C month on
the identity member, `st_0`'s last job disappears and the toggle goes for the
opposite reason. **Both resolutions retire the boolean.**

**Considered and rejected**, both of which keep the knob:

- Rename to `baseline_member:` and add a run-time refusal. This is more
  machinery to preserve an option whose only effect is losing two indicators —
  a guard whose correct answer is always "yes, run it" is a knob that should
  not exist.
- Rename only. The silent loss stays a documented hazard rather than a guarded
  one, which is the state that produced the R11 P3 defect in the first place.

**Consequence for the migration.** `C-69` is a DELETE, so a v1 config carrying
`run_historical: true` migrates by dropping the key, and one carrying `false`
migrates by dropping it too — and that second case CHANGES WHAT THE RUN
PRODUCES, by adding `st_0` and with it the two class-C metrics. It is the one
row in this cluster where a mechanical rewrite is not behaviour-preserving, and
the migration tool must SAY SO for that value rather than rewrite silently. No
shipped config is affected in the direction that loses anything: the additions
are `baseline_linux`, `wf2_fast` and the fixture, all of which gain two metrics
they should have had.

#### `compute:` is real, and its keys belong outside run identity — `C-34`, `C-79`, `C-80`

**Asked by the owner, 2026-08-24:** is there a good reason to batch at all;
does the reasoning hold for both long and short runs; and would these settings
be better in `advanced_settings.yml`? **Ruled the same day:** keep `compute:`
where `C-34` puts it, and add `C-79` — the exclusion from `CONFIG_PROJECTION`
that makes the section mean something.

**Batching is justified, and measured.**
`dev/milestones/p33/batching-results.md` (2026-07-25, 12-member fixture): B=1
gives a 464 s stage makespan, B=4 gives 221–228 s, **−52%**. The record also
corrects the intuition the name invites: Julia process startup is `F ≈ 24 s`,
only ~21% of a run. The win is IN-SESSION warm-up of the Wflow run path — 92 s
cold, 35 s warm, a 0.38 ratio — which is why the same record notes a
PackageCompiler sysimage (which attacks `F` only) can never capture most of it.

**The reasoning is run-length dependent, and that was never measured —
`C-80`.** The saving per extra member in a session is the warm/cold difference,
~57 s, and it is a FIXED per-member cost while simulation time scales with the
run length. So a 10-year run gets a larger proportional win than a 20-year one
from the same B. The disk side moves the other way: `batch_sizing.py`
establishes that forcing bytes are a per-timestep constant of the MODEL, so
per-member footprint grows about linearly with run length while state size is
constant. **Longer runs make batching less valuable and more expensive at the
same time.**

The mechanism already half-handles this — the disk ceiling lowers B as the
footprint grows — but the decomposition was measured at ONE run length on ONE
fixture, so the dependence is an assumption. `C-80` records the probe rather
than letting R14 assert it.

**Why NOT `advanced_settings.yml`, which was the owner's first instinct.** The
instinct is right that these are not scientific setup; the destination is
wrong, and would make it worse. `effective_config_document()` takes
`advanced_settings` into the digest **whole and unprojected** — its own
docstring: *"These stay INSIDE the document: they are configuration ...
recorded nowhere else in a project tree."* Moving the batch keys there keeps
them in configuration identity and removes even the possibility of a carve-out.

The same docstring names the class these keys belong to: *"Execution-only
options such as **cores**, dry-run, and verbosity do not belong in this
document."* And `cores` is the other half of this very arithmetic — peak disk
is `p × B × per_member`, with `p` coming from `-c` at the command line and no
YAML at all. `batch_size` and `disk_headroom_gb` are the same KIND of quantity
as `-c`: properties of the machine, not of the project and not of the toolbox.
`disk_headroom_gb` in particular is a property of whatever disk the run is on,
and `advanced_settings.yml` is TRACKED — setting it there dirties a repo file
per machine.

`C-79` is therefore the row that makes `C-34` worth doing: with `compute:`
excluded from `CONFIG_PROJECTION`, the keys stay visible and documented where a
user looks for them, they leave the digest and the experiment freeze so
changing `batch_size` never invalidates a run, and a per-machine override via
the profile or `--config` needs no edit to a tracked file.

`C-79` is also the first concrete instance of the `Q-F` claim — "guard
everything except `compute:` and `reporting:`" — and with `C-77` removing
`reporting:`, it is now the ONLY instance. `Q-F`'s probe gets simpler and more
load-bearing at once.

#### `reporting:` leaves the config — `C-77`, `C-78`

**Ruled by the owner, 2026-08-24:** "I am not sure what shape I want for this
... let the user post-process from the tables. So, lets remove `reporting:`
from the config."

**Nothing in this repository draws a response surface, so no figure is lost.**
`shared/surface_axes.py`'s own docstring: *"This module is the REFERENCE
IMPLEMENTATION of HM-7, not its definition. **No rule in this repository calls
it**: WF3 ends at the reduction, and the consumers that actually draw a surface
are out-of-repo (CST-API, the frontend, csthelpers)."* In the Snakefile
`SURFACES = parse_surfaces(config)` is assigned at line 565 and **read
nowhere** — it exists as a parse-time refusal on behalf of those consumers.

That makes the ruling correct on the repo's own rules rather than merely
acceptable: `reporting:` is a config section this repo validates on behalf of
consumers it is explicitly forbidden to be coupled to — AGENTS.md, "no web/API
code belongs here", and the standing rule that the API and frontend never
constrain a decision here. Removing it removes a coupling that should not
exist.

**What goes:**

- the `reporting:` block in `_run_stress_test.yml` and in the template;
- `parse_surfaces` from the Snakefile's imports and its line 565
  (`warn_on_heterogeneous_design` STAYS — it is about the perturbation design,
  not reporting);
- `config_composition.py`'s reporting-specific refusals — the leftover
  top-level parse error and the T2 placement message.

**What STAYS, explicitly, so nobody tidies it away:** `shared/surface_axes.py`
itself. It is the HM-7 reference implementation and the seam contract
(`dev/reference/contracts/hydrological-model-seam.md`) is the definition. No
rule called it before this change either.

**`C-78` — the hoist mechanism empties.** `HOISTED_SECTIONS` is
`{"run_stress_test": ("reporting",)}` — one entry, and `C-77` removes it. R13
built the hoist for exactly this section, so this is an amendment to D-10.4,
not a quiet edit. With no users left it should be RETIRED rather than kept
empty, on the precedent R13 itself set: `CROSS_WORKFLOW_READS` was retired when
D-9.7 emptied it, and the D-9.6 scan now asserts a literal zero instead of
equality with a set. An empty registry that can be refilled cannot enforce
shrink-only; no registry can.

**Consequences elsewhere in the register, all simplifications:**

| row | effect |
|---|---|
| `Q-G` | **RETIRED.** `C-55` had already narrowed it to the `reporting:` question alone; there is no question left |
| `C-03` | **WITHDRAWN** — nothing to generalize |
| `C-28` | **WITHDRAWN** — no destination; WF2's `stats` stays at `workflows.analyze_projections.stats` |
| `C-02` | survives and is UNBLOCKED — `compute:` was the other half of `Q-G` and is settled |

**One thing to carry into the intake.** `reporting:` was the only section
outside `CONFIG_PROJECTION`, so its removal briefly leaves the digest covering
everything — until `C-79` lands. The two should be presented together, or S2's
three-class split has no instances at all.

#### The weather generator enters through a PATH, not through promoted keys — `C-81`, `C-82`

**Asked by the owner, 2026-08-24:** screen `run_weather_generator()`'s
parameters and propose which user-facing ones belong in
`_run_stress_test.yml`. **Ruled the same day: none of them — one path key
instead.**

**Most of the screen was already done, and R14 must not redo it.**
`dev/milestones/r11/c34-weathergenr-argument-decisions.md` (2026-08-08) carries
ONE RECORDED DECISION per unpassed weathergenr argument, and states the rule
this row obeys: *"not 'expose everything' — most upstream defaults are right,
and surfacing them would bloat every project config ... An unexamined default
is not a choice."* Promoting a key C34 declined would re-litigate a recorded
decision without new evidence.

C34 declined exactly the candidates a fresh screen surfaces, with reasons that
are methodological rather than clerical:

| key | C34 |
|---|---|
| `exaggerate_extremes`, `extreme_prob_threshold`, `extreme_k` | not surfaced — a real STRESS DIMENSION; needs a design-table column and a results column together |
| `precip_cap_mm_day` / `_floor_` / `_quantile` | declined — "uncapped is correct for a stress test: capping would silently truncate the very tail the experiment exists to probe" |
| `precip_intensity_threshold` | declined — `0` is what the current occurrence statistics already assume |
| `scale_var_with_mean`, `enforce_target_mean` | declined — both are what make the design table's axes mean what they say |
| `pet_method` | surfaced in the WEAGEN TEMPLATE only; F16's open half (PET is computed twice; is the first result used?) is unsettled |

**The gap C34 did not cover** is the keys we DO pass, which were never subject
to that discipline: `warm_signif`, `warm_pool_size`, `wet_q`, `extreme_q`,
`annual_knn_n`. Three carry "suggested" RANGES in their own comments
(0.80–0.95, 10,000–30,000, 100–120), which is the template admitting they are
judgment calls rather than constants. They live in a TRACKED repo file, so a
basin needing a different `wet_q` cannot express it without editing the
repository — the same objection that ruled `advanced_settings.yml` out as a
home for `disk_headroom_gb`.

**The structural finding — `C-81`.** WF1 lets a project supply its own engine
config; WF3 does not:

| workflow | engine config |
|---|---|
| WF1 | `model_build_config: config/defaults/wflow_build_model.yml`, `waterbodies_config: ...` — both CONFIG KEYS |
| WF3 | `config/defaults/weathergen_config.yml` — a hardcoded string literal in rule 3.10, **twice** (`input.default_config` and `params.default_config`) |

So `C-81` adds the missing key:

```yaml
# _run_stress_test.yml
weathergen_config: config/defaults/weathergen_config.yml   # path
```

This is S5's own mechanism — "engine vocabulary enters through a PATH key
pointing at a file in their own schema" — and it is what WF1 already does.
Every weathergenr argument becomes reachable per basin, in weathergenr's
vocabulary, checkable against `?generate_weather`, **without one engine key
entering our sections and without reopening any C34 decision**. It also removes
an asymmetry between two workflows that has no stated reason.

**The half that must land with it.** Rule 3.10 already declares the file as an
INPUT, so Snakemake re-triggers on a project's own copy — that was the F7 fix
of 2026-08-05, when it was params-only and template edits silently changed
nothing. But `CONFIG_REFERENCES`, which feeds `effective_config_digest`, lists
the workflow config files and the data catalogs, NOT `config/defaults/*`. With
a path key the referenced file must JOIN `CONFIG_REFERENCES`, or a project
could change its generator settings and the experiment digest would not move.

**`C-82` — the one genuine promotion**, into the section `C-34` creates:
`generate_weather.parallel` and `n_cores` are execution-only, exactly the class
`C-79` carves out of configuration identity. C34 declined `n_cores` because
*"a second parallelism knob belongs with `julia_threads` in
`advanced_settings.yml`"* — a destination `C-54`/`C-55` has since moved. The
reasoning survives and now points at `compute:`.

**Not promoted, deliberately: `pet_method`.** The highest-leverage scientific
knob here — Hargreaves PET goes as the square root of diurnal range, and the
template records upstream measuring +3.7% to +14.7% PET at +4 °C across a
plausible range of it — but surfacing a method whose result may be discarded
downstream advertises a choice with an ambiguous effect. It waits on F16.

**Two errata against the C34 record**, which is a milestone record and is
therefore corrected HERE rather than edited there:

1. Its "still open" list names three stress dimensions. **Spell length has
   since landed** — `dry_spell_factor` / `wet_spell_factor` moved into the
   project config on 2026-08-12, and `C-33` regroups them. Two remain
   (occurrence frequency, extreme intensification).
2. The `n_cores` destination moved, as above.

### Group I — carried forward from `parameter-placement.md`

| ID | change | rule | class | breaking |
|---|---|---|---|---|
| `C-35` | De-duplicate `DEFAULT_ANCHOR` (defined twice: `metrics_definition.py:18`, `climate_figures.py:120`) (= M2) | — | MECHANISM | **no** |
| `C-36` | Move the config-key defaults out of Python (`DEFAULT_SPELL_FACTOR`, `DEFAULT_MAX_SUBBASINS_PER_BASIN`, `DEFAULT_GAUGE_SNAP_TOLERANCE_M`, `DEFAULT_HYDROGRAPHY`, `DEFAULT_BASIN_INDEX`, `DEFAULT_STATS`) (= M3) | — | MECHANISM | no — **blocked on `Q-E`** |
| `C-37` | A mechanical "declared keys ⊆ read keys" check (answers P2) | — | MECHANISM | no |
| `C-38` | Extend `scripts/split_project_config.py` (or a sibling) into a v1→v2 rewriter driven by the register above | — | MECHANISM | no |
| `C-72` | `forcing_window_years()` deleted; `forcing_window()` becomes the shared years-to-ISO seam converter | — | MECHANISM | no |
| `C-73` | `compute_nr_years()` loses its `ceil`; derived from `simulation_window.end` | — | MECHANISM | no |
| `C-75` | Sweep the technical note onto one trajectory vocabulary and correct its stale defaults | — | MECHANISM (doc) | no |
| `C-76` | Record what the note's Annex is, and the three places it and the code never agreed | — | (finding) | no |
| `C-80` | PROBE: is the batching win run-length dependent? Measured at one run length only | — | (probe) | no |
| `C-83` | `weagen` → `weathergen` across the LIVE surface (`naming.md:176` already forbids the contraction); `dev/milestones/**` excluded | N1 | RENAME (code) | no |
| `C-84` | `_analyze_climate.yml` survives `C-45` as a comment-only scaffold; add the missing WF0 template — born as `project_config.analyze_climate.template.yml` under `C-85` | S7, convention | NEW (doc) | no — **RULED 2026-08-24** |

**Second erratum, same source (2026-08-22).** The appendix lists
`DEFAULT_MIN_REFERENCE` and `DEFAULT_MAX_FLAGGED_MONTHS` under "No config
surface, correctly constants". They DO back config keys —
`relative_change.min_reference` and `.max_flagged_months` — so both belong in
`C-36`'s list. Two errata from one source in two turns: the re-measure action
recorded under Group G is not optional.

`C-35` is the only change in this document that is unambiguously correct
regardless of how everything else resolves, and the only one that is
non-breaking and independently landable **today**.

#### The note carries two vocabularies for one concept — `C-75`

§1.3.1 *Screen 6 — Execute a Climate Stress Test* says "whether the changes
occur gradually over time or immediately from the start of the simulation"; the
Annex says "transient ... or constant". One concept, two spellings, in one
document — the same P3 this milestone removes from the configs. `C-75` sweeps
the note onto the `transient | constant` pair `C-32` adopts, and corrects the
documented default in the same pass.

`C-75` also carries the two stale defaults this walkthrough turned up: the
Annex's `transient` default (the code refuses a missing value, deliberately)
and its `Realizations_number: 3` (the code defaults to 1).

Non-breaking and doc-only, so it does not need the bundle. It should still land
WITH `C-32`, because a note describing a config key that no longer exists is
the stale-reference defect AGENTS.md names explicitly.

#### What the note's Annex is, and what it is not — `C-76`

Found 2026-08-24 while sourcing `C-32`. The Annex of
`docs/cst-toolbox-technical-note-2025.md` is in scope for this milestone and
easy to misread in BOTH directions, so both readings are recorded.

**It is about THIS repo.** The Annex heading is *BlueEarth CST Workflows —
Command-Line Functionality*, and it says "User inputs to each workflow are
provided through JSON-based YAML files". It is describing the config this
milestone reshapes, not the web application. By contrast §1.3.1 *Screen 6 —
Execute a Climate Stress Test* IS the web app, so its wording ("gradually over
time or immediately from the start") is FRONTEND copy and must not be cited as
a constraint on this repo — the standing rule is that CST-API and the frontend
never constrain decisions here.

**It is NOT a spec the code drifted from.** Checked, because the first draft of
this row asserted that and it does not survive:

| evidence | |
|---|---|
| repo's first commit | 2021-12-21 |
| `horizontime_climate` present in code | **2023-04-25** (`1860270b`) |
| the note added to the repo | **2026-07-16** (`5cad6bd8`, "wip") |
| `Starttime_experiment`, `Change_step_number` in code, ever | **never** — `git log -S` finds them only in the note's own commit |

So the code's spellings predate the note's arrival by three years, and the
Annex's parameter names have never existed in this repository. The two were
never aligned; there is no drift event.

**What it IS good for, and it is still worth having.** The Annex is an
independent description of the same tool by the same author, reaching — without
reference to the implementation — for a start/end analysis period, a count of
SCENARIOS rather than intervals, and a two-valued change type:

| the Annex writes | the code does | this cluster |
|---|---|---|
| `Starttime_experiment` / `Endtime_experiment`, "start year / end year of the analysis period" | `horizontime_climate` + `run_length`, a midpoint and a duration | `C-67` |
| `Change_step_number`, "number of temperature change scenarios ... to span the range" | `step_num`, an INTERVAL count, one less than the number of scenarios | `C-31` |
| `Change_step_type`, "transient (default) or constant" | `transient_change`, a required boolean | `C-32` |

That is corroboration about what reads naturally to a domain author, not
authority. **The three rows must be argued on their own merits**; the Annex is
a supporting citation showing a second, independent formulation landed on the
same shapes. Calling them "restorations" would overclaim and a reviewer could
puncture it in one `git log`.

**Erratum: `Realizations_number` default.** The Annex gives "(default value:
3)"; `run_stress_test.smk:179` defaults it to 1. `C-75` corrects the note.

#### `weagen` is a contraction the conventions already forbid — `C-83`

**Raised by the owner, 2026-08-24.** Not a new decision:
`dev/reference/naming.md:176` already names it — *"Ad-hoc contractions
(`weagen`, `proj`) are not"* established domain abbreviations. The code is
merely GRANDFATHERED, and R14 is the migration note that discharges the
grandfathering.

The repo already spells it correctly nearly everywhere — the package directory
is `blueearth_cst/weathergen/`, the default config is
`config/defaults/weathergen_config.yml`, and the rule is
`prepare_weathergen_config`. `weagen` is the stray, and the inconsistency is
visible on a single line: `run_stress_test.smk:965`, where the rule
`prepare_weathergen_config` runs the script `prepare_weagen_config.py`.

**Scope — the LIVE surface only:**

| file | what |
|---|---|
| `blueearth_cst/experiment/prepare_weagen_config.py` | the module FILE, plus `build_weagen_config` |
| `tests/test_prepare_weagen_config.py` | the test file |
| `run_stress_test.smk` | the `weagen_config` input/output name in rules 3.10, 3.11, 3.12 and the two R command lines |
| `blueearth_cst/weathergen/{generate_weather,impose_climate_change}.R` | the argument name |
| `blueearth_cst/experiment/downscale_climate_forcing.py`, `shared/interchange_contracts.py`, `config/defaults/weathergen_config.yml`, `test_case/snake_config_rapid.yml`, `tests/data/presplit/snake_config_rapid.yml` | comment and docstring references |
| `dev/reference/**`, `dev/roadmap.md`, `dev/working/**`, `dev/LOG.md` | live reference prose |

**Explicitly NOT swept: `dev/milestones/**`.** Those are historical records,
valuable because unedited, and AGENTS.md governs them through
`dev/reference/sealed-records.yml`. They hold the large majority of the 210
occurrences; renaming there would rewrite history to match a later convention.

**Not a config-key rename**, so it does not belong to the migration bundle and
`C-38` does not touch it: `weagen_config` is a rule input NAME and a module
path, not a user-facing key. It can land independently and non-breakingly at
any time, and it is the cheapest row in this cluster.

`proj`, named in the same sentence of `naming.md`, is NOT swept here. `C-25`
retires one instance (`clim_project` → `ensemble`); a general sweep needs its
own scoping and should be boarded rather than folded in.

#### `_analyze_climate.yml` survives `C-45` as an empty scaffold — `C-84`

**Raised by the owner, 2026-08-24:** `C-43`/`C-45` move `candidate_sources` up
into the T1 climate charter, which leaves `_analyze_climate.yml` holding
nothing. Keep the file as a convention for knobs WF0 may gain, or delete it?
**Ruled: keep it, and give it the template it never had.**

**R13 already supports this, deliberately.** `config_composition.py:392`:

```python
if loaded is None:
    # An empty file is a workflow with no settings, same as an omitted key.
    return _Probe(name, os.fspath(raw), resolved, "ok", {}, "")
```

A comment-only T2 file is legal and composes to `{}` — which is exactly what an
omitted `config_path` composes to under D-8.7. **The two are indistinguishable
in the composed document, so the digest is identical either way.** No mechanism
change, no `effective_config_digest` movement, no amendment to R13. The
decision is about discoverability alone, and R13's own comment shows the case
was foreseen rather than tolerated.

**The gap this exposes is the template, not the file.** `config/templates/`
ships `snake_config.{build_model,analyze_projections,run_stress_test}
.template.yml` plus the project template — **WF0 has none**. And only the rapid
set carries an `_analyze_climate.yml`; baseline, baseline_linux and wf2_fast
omit `config_path` entirely. After `C-45` the repo would have four workflows,
three templates, and one example that is inconsistent with the other three.

`C-84` therefore does two things:

1. Keep `_analyze_climate.yml` in the rapid set as a comment-only scaffold,
   saying what WF0 reads today (nothing beyond `climate:` in the project file)
   and where a future knob goes.
2. Add the missing WF0 template, so the four-file convention is uniform and a
   scaffolded project gets WF0's slot with the other three. Under `C-85` it is
   born as `config/templates/project_config.analyze_climate.template.yml` —
   the whole point of bundling the rename is that this milestone does not ship
   a brand-new file under the prefix it is retiring.

**One foot-gun to document in the template, because the asymmetry is sharp.**
An empty file is fine; a MISSING file with `config_path` still declared is a
hard parse-time error. The message already names the fix — *"To give this
workflow no settings at all, delete the `config_path` key"* — but a scaffold
invites deletion in a way an authored file does not, so the template should
ship the file and the stanza as a pair and say that they travel together.

**One caveat worth verifying in the design, not asserted here.**
`CONFIG_REFERENCES` digests each declared workflow config file by CONTENT, so
for the workflow that declares it, a comment edit in the scaffold moves
`configuration_inputs_digest` and re-fires that workflow's run record. Harmless
for WF0, which no other workflow's `R(entry)` includes — but it means comments
in a scaffold are not free in general, and a scaffold added to a workflow
inside WF3's projection would behave differently. Check before generalising the
pattern.

**Not a widening of R14.** `C-84` adds no key and changes no value: it is the
disposition of a file `C-45` empties, plus the template that was already
missing. Non-breaking, and it can land with the bundle or before it.

## Proposed shape

### Project file (T1) — `project_config_<project>.yml` (`C-85`)

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
  window: {start: 1990, end: 2020}   # C-70, water years, inclusive
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
simulation_window: {start: 2000, end: 2020}   # C-71, water years, inclusive
observations:
  river discharge: null    # key drawn from model.outvars
```

### `_analyze_projections.yml`

```yaml
catalog: config/catalogs/cmip6_data.yml
ensemble: cmip6
models: [...]
scenarios: [ssp245, ssp585]
members:                     # C-63 groups all three; the flat
  preference: [r1i1p1f1]     # member_selection / member_overrides are gone
  selection: first_available
  overrides: {}
variables:
  precip:      # bare key = registry-resolved; declare a mapping only to override
  temp:
reference_window: {start: 1985, end: 2014}
future_windows:
  - {start: 2030, end: 2060}
  - {start: 2070, end: 2100, name: far}   # name optional; defaults to 2070-2100
stats: [mean, median, std]                # C-28 WITHDRAWN; stays where it is
```

### `_run_stress_test.yml`

```yaml
experiment_name: my_experiment
seed: auto                       # arrives from C-51
n_realizations: 2
weathergen_config: config/defaults/weathergen_config.yml   # C-81, path
simulation_window: {start: 2070, end: 2086}     # C-67, water years, inclusive
climate_perturbations:                          # C-68
  temp:
    n_levels: 2                                 # C-31, was step_num: 1
    trajectory: transient                       # C-32, was transient_change
    mean: {min: [...12], max: [...12]}
  precip:
    n_levels: 3                                 # C-31, was step_num: 2
    trajectory: transient
    mean:     {min: [...12], max: [...12]}
    variance: {min: [...12], max: [...12]}
  spell_factors:
    dry: [...12]
    wet: [...12]
compute:                                        # C-34; excluded from
  batch_size: 4                                 # CONFIG_PROJECTION by C-79
  batch_size_max: 8
  disk_headroom_gb: null
  parallel: false                               # C-82, from the generator
  n_cores: null
```

`run_historical` is absent above: `C-69` deletes it. `reporting:` is absent:
`C-77` removes it.

### `_analyze_climate.yml`

```yaml
# C-84: a comment-only scaffold. WF0 reads nothing beyond `climate:` in the
# project file today; a future WF0-only knob goes here. The file and its
# `config_path` stanza travel together - deleting the file while the stanza
# stands is a hard parse-time error.
```

## Open questions

| ID | question | blocks | current lean |
|---|---|---|---|
| `Q-A` | `project.dir` (N3) vs keeping `project_dir` | `C-06` | **Keep `project_dir`** as a named exemption — it is a term of art here (AGENTS.md's two-tier location rule, `warn_if_project_dir_in_repo`, every internal variable). |
| ~~`Q-B`~~ | ~~Is `model:` holding one leaf (`outvars`) an S4 violation?~~ **RESOLVED 2026-08-22**: `model:` is the engine boundary, not a group of one. See Group E. | `C-19` | — |
| `Q-I` | One variables key or two? `C-48` (analysis) and `C-50` (extraction) must not become one key whose meaning widens on upgrade — a project that set a short list for FIGURES would silently change what gets DOWNLOADED. Same cross-version meaning-swap `data_sources` was rejected for. | `C-48`, `C-50` | Lean TWO, distinctly named. Decide now even though only one ships. |
| ~~`Q-C`~~ | ~~`_count` suffix vs bare plural~~ **RESOLVED 2026-08-24 (owner)**: neither. Counts take the `n_` prefix; see the N6 rewrite. | `C-29`, `C-31` | — |
| ~~`Q-D`~~ | ~~Does `method:` earn a heading?~~ **RETIRED 2026-08-22**: the section is gone (`C-52`); both keys have real homes. | ~~`C-20`~~ | — |
| `Q-E` | Where does a config key's DEFAULT live: `config/advanced_settings.yml` (precedent, closed schema, already tested) or beside the key in the template? | `C-36` | **`advanced_settings`** — the only option with an existing enforcement mechanism, and the only one that could grow `C-37`. |
| `Q-F` | Does S2 actually permit `_WF1_GUARDED` to become "everything except `compute:`"? (`reporting:` dropped out of the question 2026-08-24 with `C-77`.) | `C-04` | Unknown. **Needs a probe against the digest and freeze code before R14 promises it** — and it is now the only evidence for S2, not one probe among several. |
| `Q-H` | One `selected`, or one per consumer (`forcing` for WF1, `conditioning` for WF3)? | `C-44` | Lean ONE. CST does no local calibration, so the response surface is anchored on the historical run; letting the generator condition on a different record than the model was forced with decouples them silently. The genuine hybrid case is already met INSIDE a single store — the CHIRPS branch takes temperature, radiation and pressure from ERA5 and lapse-corrects them onto the CHIRPS grid. Splitting later is expensive, so record rather than default. |
| ~~`Q-G`~~ | ~~How is `reporting:` placed under S7?~~ **RETIRED 2026-08-24**: `C-55` narrowed it to `reporting:` alone, and `C-77` removes the section. | ~~`C-02`, `C-03`, `C-28`, `C-34`~~ | — |

`Q-F` is NOT resolved by any of this, and gets harder to defer: with `C-77` and
`C-79` landed, `compute:` becomes the ONLY section outside configuration
identity, so the entire S2 claim rests on that one probe.

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
- `config/templates/snake_config*.template.yml` × 4 (× 5 after `C-84`)
- `test_case/snake_config_*.yml` — **four multi-file sets** (baseline, baseline
  _linux, rapid, wf2_fast), 17 files
- `tests/snake_config_fixture.yml`, and `tests/data/presplit/**` (which exists
  precisely to test migration and must gain a v1→v2 pair)
- `scripts/split_project_config.py`, `scripts/plot_workflow_dag.py`
- `docs/guide/configuration.qmd`, `docs/migration-config-tiers.md`, `README.md`
- `dev/reference/workflows/*.md`, `dev/reference/naming.md`, `AGENTS.md`

**`C-85` widens this list by BREADTH, not by depth** (measured 2026-08-19,
re-measure before the design): 11 tracked files to rename, **221 occurrences
across 68 files outside `dev/`**, 771 repo-wide. The categories the key
migration does NOT already touch are `.gitignore`, `pixi.toml`, four
`scripts/`, the three `docs/notebooks/*.ipynb` (which carry banner SHAs — see
`t2608132100`), and 34 files under `tests/`. Four SEALED records name
`snake_config` in 11 places and stay stale on purpose
(`dev/reference/sealed-records.yml`, frozen by `tests/test_sealed_records.py`).
None of it can move a number, which is why it is affordable inside the bundle.

## Packaging recommendation

Every change except `C-35`, `C-37` and `C-38` is breaking, and their costs are
almost entirely **shared** — one migration pass, one template rewrite, one
sweep of the fixture corpus. Landing `C-07` alone would pay the whole migration
cost for one dead key. Recommendation:

- **Now, independently:** `C-35` (non-breaking, correct under every outcome).
  `C-83` may also land at any time — it is a code contraction sweep, touches no
  config key, and `C-38` never sees it.
- **Probe before designing:** `Q-F` (`C-04`) and D3-feasibility for `C-38`.
- **One bundle, one `schema_version` bump:** everything else, **`C-85`
  included** (ruled 2026-08-24). The file rename breaks the same
  `--configfile` invocation the key migration does, so bundling pays that break
  once; and it must precede nothing, because `C-84` would otherwise ship a new
  template under the retired prefix and `C-38` would be written twice.
  Sequencing inside the bundle: the `git mv` and the `.gitignore` glob move in
  ONE commit, verified with `git ls-files test_case/`.

The project config carries no version key today (the `schema_version` hits
elsewhere in the tree belong to snapshot and series-identity artifacts), so the
bundle is also the moment `C-05` becomes possible.

## Next artifact

An intake + design under `design-review-loop`, on the R13 pattern:
`dev/milestones/r14/config-shape-intake.md` → `config-shape-design.md` →
review record. Not started; this document is the input to it.

### To carry into the intake

Raised by the `_run_stress_test.yml` walkthrough of 2026-08-24, and easy to
lose because each item is a consequence of a row rather than a row itself:

- `C-70` and `C-71` widen `climate.water_year_start` (`C-53`) from a reporting
  and aggregation key into one that resolves EVERY window's calendar bounds.
  That is a real widening of its authority, and the intake should say so
  explicitly rather than let it arrive as a side effect of N8.
- `C-67` and `C-71` both change `params:`-threaded values, so rules re-trigger
  and the tree shape moves — `semantic_tree_diff.py` territory, the same
  consequence already recorded for `C-61`.
- `C-69` is the cluster's only row that is not behaviour-preserving for every
  input value; see its subsection under Group H. `C-38`'s rewriter needs a
  per-row hook for "mechanical, but tell the user what changed", which no
  earlier row required. N8's `water_year_start != Jan` refusal is the second
  user of that hook, which makes it a feature of the migrator rather than a
  special case.
- `C-77` and `C-79` must be presented together: until `C-79` lands, removing
  `reporting:` leaves the digest covering everything and S2's class split with
  no instances at all.
