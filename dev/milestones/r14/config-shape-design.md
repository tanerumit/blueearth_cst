# R14 — Config shape: Design (DRAFT)

> **Status: DRAFT 2026-08-24** — authored directly by the driver at the owner's
> instruction. **The `design-review-loop` was explicitly waived for this
> milestone** (owner, 2026-08-24): no internal lens panel, no external
> cross-vendor round, no G1/G2 loop gates. The owner reviews this document
> directly and approves or returns it.
>
> **Lifecycle: `frozen-with-supersession`** on acceptance — a milestone
> snapshot, the same policy R13's design carries. Until then it is a living
> draft with an append-only revision log (§18).
>
> **Milestone:** R14 (config shape — sections, names, and the migration that
> lands them). Predecessor R13 (config tiers, ACCEPTED 2026-08-21) split the
> config by FILE; R14 reshapes it WITHIN that split.
>
> **Inputs, and the division of labour between them:**
> - `config-shape-scoping.md` — the argument. 85 indexed changes `C-01`..`C-85`,
>   policy rules `S1`–`S7` and `N1`–`N8`, nine questions all closed, with every
>   alternative and every owner ruling recorded against its evidence.
> - `config-shape-intake.md` — the contract. Settled framing, derived-artifact
>   register, a ten-row evidence register (`E1`–`E10`) verified against the
>   code, and the gate-materialization check.
>
> **This document is the SPECIFICATION.** It does not restate the argument. A
> reader asking *why* goes to the scoping document by `C-nn`; a reader asking
> *what to build* stays here.

**Size budget: 1,400 lines for the normative body.** Set against the two
closest accepted precedents — `r13/config-tiers-design.md` (3,419) and
`r12/stress-test-lookup-design.md` (2,946) — and deliberately below that range,
with the reason stated rather than left to be silently broken. Both precedents
carry their own rationale and grew across four review rounds by accretion. R14
has neither: the rationale lives in a 2,300-line scoping document that already
exists, and there are no review rounds. A design that re-argued `C-01`..`C-85`
would invert the reading order this repo depends on. If a revision would push
the body past the budget, relocate superseded text to §18 rather than stack.

---

## 1. Problem statement

R13 fixed *which file* a key lives in. Two questions are still answered by
history rather than by rule:

1. **Which section.** `shared:` names a RELATIONSHIP — "read by ≥2 workflows" —
   not a kind. One heading holds a basin geometry, a climate binding, a
   hydrological-year convention and a thread count.
2. **What a key is called.** One concept has several spellings:
   `starttime`/`endtime` against `historical_year_range: [a, b]` against
   `future_horizons.<n>: [a, b]`; `source` meaning both a catalog FILE and a
   catalog ENTRY; `horizontime_climate` naming a workflow rather than a value.

A third consequence follows from the first: the experiment guard's key list is
maintained by hand, because no section boundary distinguishes "changes the
numbers" from "changes only the wall-clock".

These are P3 and P4 of `dev/working/parameter-placement.md`, open since
2026-08-12.

## 2. Goals / Non-goals

### Goals

- **G1** Every section name states a KIND. No section names a relationship.
- **G2** One concept, one spelling, across all five files.
- **G3** A new parameter has exactly one obvious home (D4).
- **G4** The migration is mechanical, one-shot, and bounded — a single
  `schema_version` bump, one command, one migration note.
- **G5** The experiment guard's key list is DERIVED, not maintained.
- **G6** No number moves, except at the two rows explicitly ruled otherwise,
  each carrying a migration invariant.

### Non-goals

- Re-opening R13's tier split, path-reference composition, or the single
  `--configfile` CLI contract.
- Any change to `config/catalogs/*` or `config/defaults/*` internals. **This
  already caught one row** — `C-82`, withdrawn (`E3`).
- Changing what a workflow computes, beyond the two ruled exceptions (§11.4).
- Web/API accommodations.
- The two boarded number-movers, `t2608241413` and `t2608241414`.
- Adding climate datasets (`t2608222239`) or making the extraction set derived
  (`t2608222252`). The SHAPE is in scope; the capability is not.

## 3. Constraints (standing; restated)

| # | Constraint | Source |
|---|---|---|
| K1 | hydromt / hydromt_wflow / wflow / weathergenr vocabulary verbatim. No key inside `config/defaults/*` or a data catalog is renamed, moved or removed. | AGENTS.md hard constraint; S5 |
| K2 | R13 is ACCEPTED. Any change to `T1_TOP_LEVEL`, `SHARED_SEAM_KEYS`, `HOISTED_SECTIONS` or the composition invariant is a recorded AMENDMENT. | R13 D-9.5, D-10.4, D-8.1 |
| K3 | A key present-vs-absent moves `effective_config_digest`; `_frozen_differences`' key-union diff then refuses every already-run experiment. Acceptable only ONCE. | R13 composition invariant #2 |
| K4 | `climate.window` (extraction) and `simulation_window` (run) stay visibly separate after `N4`/`N8` make them look alike. | scoping §Constraints |
| K5 | `get_config` contract preserved: raise on missing required, default for optional. | AGENTS.md Conventions |
| K6 | `workflow.configfiles[0]` forwarded as `config_path` to downstream **Python** scripts. | R13 `E5` |
| K7 | No new dependencies without owner approval. | global |

## 4. Decision criteria

- **D1 — Answers P2 mechanically.** Four inert-or-partly-inert parameters found
  by hand, zero by machine. A shape that does not make `C-37` feasible has not
  solved the problem with consequences. **And `C-37` must fail CLOSED** (`E5`).
- **D2 — Preserves guard semantics.** Specifically the reason `_WF1_GUARDED`
  guards `shared` leaf-by-leaf while guarding `project` whole.
- **D3 — Migration is mechanical.** Every row a pure old-path → new-path
  rewrite, except the two ruled non-preserving, which need an explicit hook.
- **D4 — One obvious home** for a new parameter.

## 5. Settled framing (owner rulings — not reopened)

Recorded in the scoping document with evidence. This design specifies how they
land; it does not re-argue them.

| ruling | effect here |
|---|---|
| `S1`–`S7`, `N1`–`N8` adopted | §7, §8 |
| `N1` exempts the `n_` prefix; `N3` exempts `project_dir` (`Q-A`) | §8 |
| `Q-C` — counts take `n_`, not `_count` | §8 |
| `Q-E` — defaults placed by AUTHORITY, not one destination | §10.4 |
| `Q-F` — probed; `C-04` re-scoped; **S2's guard payoff does not survive as stated** | §9 |
| `Q-G` — RETIRED; `reporting:` leaves the config (`C-77`, `C-78`) | §7.5, §10.3 |
| `Q-H` — ONE `climate.selected` | §7.1 |
| `Q-I` — TWO variable keys, distinctly named | §7.6 |
| `C-85` ruled INTO the bundle | §12 |
| `C-69` and `N8` are not behaviour-preserving for some inputs | §11.4 |

## 6. Empirical premises

The intake's evidence register `E1`–`E10` is this design's premise set, cited
by ID rather than restated. The four that constrain a decision below:

- **`E1`/`E2`** — three identity mechanisms, not one; a WF1 snapshot does not
  carry WF3's sections. Governs §9.
- **`E4`** — three of seven baseline targets are config snapshots. Governs
  §14.2.
- **`E7`** — `advanced_settings.yml` is a three-way AUTHORITY split whose
  `defaults:` entries name their overriding key. Governs §10.4.
- **`E8`** — the `test_case/` seeds are tracked ONLY through the `.gitignore`
  un-ignore glob. Governs §12.2.

**Premise stability.** `E6` recorded a blast-radius figure that went stale by a
third in five days. Every count in this document is therefore dated and carries
its method; treat any count older than the implementation start as needing
re-measurement, not as a fact.

---

## 7. Target layout

Five files. T1 is the project file; T2 is one file per workflow; T3 (engine
configs) is unchanged by K1.

### 7.1 T1 — `project_config_<project>.yml`

```yaml
schema_version: 2                      # D-11.1

project:
  project_dir: /path/to/my_project     # keeps its name — Q-A
  catalog: config/catalogs/deltares_data.yml     # C-40

basin:
  region: "{'subbasin': [9.666, 0.4476], 'uparea': 100}"
  resolution: 0.00833333
  output_locations: null               # C-41 (was gauge_points)
  delineation:                         # C-42, C-13, C-14
    max_subbasins: 11
    river_uparea_km2: 32
    snap_tolerance_m: 10000
  sources:                             # C-15
    hydrography: merit_hydro_ihu
    basin_index: merit_hydro_index
    rivers: rivers_lin2019_v1
    lulc: vito
    lai: modis_lai
    soil: soilgrids

climate:                               # C-16, charter C-47
  sources: [era5, chirps]              # C-43
  selected: era5                       # C-44; null until WF0 is read
  window: {start: 1990, end: 2020}     # C-70 — water years, inclusive
  water_year_start: Jan                # C-53

model:                                 # engine boundary, Q-B
  outvars: ["river discharge", "actual evapotranspiration"]   # C-19

workflows:
  analyze_climate:     {enabled: true, config_path: ..._analyze_climate.yml}
  build_model:         {enabled: true, config_path: ..._build_model.yml}
  analyze_projections: {enabled: true, config_path: ..._analyze_projections.yml}
  run_stress_test:     {enabled: true, config_path: ..._run_stress_test.yml}
```

**D-7.1** `project.static_dir` is DELETED (`C-07`). `project.data_sources_climate`
moves to WF2's `catalog:` (`C-39`), which empties the group and lets
`data_sources` become the single leaf `project.catalog` (`C-40`).

**D-7.2** `shared:` ceases to exist. Its contents become `basin:`, `climate:`
and `model:` at T1 top level (`C-01`, `C-10`, `C-16`, `C-19`). `SHARED_SEAM_KEYS`
is re-derived from the new section names, not edited — see §10.2.

### 7.2 T2 — `_build_model.yml`

```yaml
engine:                                            # C-22
  build_config: config/defaults/wflow_build_model.yml
  waterbodies_config: config/defaults/wflow_update_waterbodies.yml
simulation_window: {start: 2000, end: 2020}        # C-71 — years, inclusive
observations:                                      # C-56
  river discharge: null                            # key from model.outvars
```

**D-7.3** `observations:` is a mapping KEYED BY VARIABLE, values drawn from
`model.outvars` verbatim. This buys a parse-time invariant: observations may
only be supplied for a variable the model was asked to output.

### 7.3 T2 — `_analyze_projections.yml`

```yaml
catalog: config/catalogs/cmip6_data.yml            # C-39
ensemble: cmip6                                    # C-25
models: [...]
scenarios: [ssp245, ssp585]
members:                                           # C-63
  preference: [r1i1p1f1]
  selection: first_available
  overrides: {}
variables:                                         # C-57 short form
  precip:                                          # bare key = registry-resolved
  temp:
reference_window: {start: 1985, end: 2014}         # C-59 — CALENDAR years, C-74
future_windows:                                    # C-60, C-61
  - {start: 2030, end: 2060}
  - {start: 2070, end: 2100, name: far}            # name optional
stats: [mean, median, std]                         # stays put — C-28 WITHDRAWN
```

**D-7.4** WF2's windows are CALENDAR years and are **trimmed**, not shifted
(`C-74`, `N8`'s two-mechanism table). `hydrological_year_bounds()` already
trims to complete water years one layer down; declaring water years here would
apply the offset twice.

**D-7.5** `relative_change:` dissolves (`C-66`): `min_denominator` becomes
per-variable registry metadata (`C-64`), `max_flagged_months` becomes
`advanced_settings.constraints.max_flagged_months` (`C-65`).

### 7.4 T2 — `_run_stress_test.yml`

```yaml
experiment_name: my_experiment
seed: auto                                         # arrives from C-51
n_realizations: 2                                  # C-29
weathergen_config: config/defaults/weathergen_config.yml   # C-81 — a PATH
simulation_window: {start: 2070, end: 2086}        # C-67 — years, inclusive
climate_perturbations:                             # C-68
  temp:
    n_levels: 2                                    # C-31; n_levels = step_num + 1
    trajectory: transient                          # C-32; enum, REQUIRED
    mean: {min: [...12], max: [...12]}
  precip:
    n_levels: 3
    trajectory: transient
    mean:     {min: [...12], max: [...12]}
    variance: {min: [...12], max: [...12]}
  spell_factors:                                   # C-33
    dry: [...12]
    wet: [...12]
compute:                                           # C-34; carved out by C-79
  batch_size: 4
  batch_size_max: 8
  disk_headroom_gb: null
```

**D-7.6** `run_historical` is DELETED and `st_0` is always produced (`C-69`).
`reporting:` is removed from the config surface entirely (`C-77`).

**D-7.7** `parallel` and `n_cores` are **absent by design.** `C-82` is
WITHDRAWN (`E3`): both live in `config/defaults/weathergen_config.yml`, which
K1 puts out of reach, and `C-81`'s path key already makes them reachable per
basin in the engine's own vocabulary. Promoting them would give one setting two
homes and require a precedence rule between our config and the engine's —
exactly the coupling S5 exists to prevent.

**D-7.8** `disk_headroom_gb` has **no template surface today** (`E5`). It is a
real key read by the Snakefile, undocumented. The migration adds it to the
template as a commented example with its unit and its relationship to
`advanced_settings.defaults.batch_disk_headroom_fraction`.

### 7.5 T2 — `_analyze_climate.yml`

A comment-only scaffold (`C-84`). It composes to `{}`, which is
indistinguishable in the composed document from an omitted `config_path`, so
the digest is identical either way — the decision is discoverability alone.

**D-7.9** The file and its `config_path` stanza travel together. An empty file
is legal; a MISSING file with `config_path` still declared is a hard parse-time
error. The template ships both and says so.

### 7.6 `C-48` is WITHDRAWN from R14 — a NEW decision requiring sign-off

`C-48` proposed a config surface for the ANALYSIS variable set. It has no home
that does not cost more than it buys, and this design declines to invent one.

The bind is three-sided and each side is load-bearing:

- **It is a two-workflow read**, verified 2026-08-24: `source_climate_vars` is
  imported by `analyze_climate.smk:18` AND `build_model.smk:17`. R13's seam
  rule (D-9.2/D-9.3, enforced by the loader) therefore forces it into T1. It
  cannot live in `_analyze_climate.yml`.
- **The `C-47` charter excludes it from `climate:`.** The charter's test is
  *"is this a fact about the basin's climate, or a use of it?"* — and which
  variables get plotted is squarely a use. Admitting it means amending an
  owner-ruled charter.
- **Its S2 class no longer has a section.** `C-48` was classed `reporting:`,
  and `C-77` removed that section.

The alternatives, and why each loses:

| option | why not |
|---|---|
| `climate.analysis_variables` in T1 | amends the `C-47` charter for one key, on the reading the charter exists to refuse |
| a new T1 `figures:` section | reintroduces a section S2 has no class for, one milestone after `C-77` removed the last one |
| duplicate in the WF0 and WF1 files | breaches R13's seam rule, refused at parse time today |

**D-7.10 `C-48` is withdrawn from the bundle and boarded.** It is the only row
in the register classed non-breaking and additive, so unlike every other row it
does **not** need the bundle and can land at any time. Deferring costs nothing:
the default stays in code, which is the status quo, and P1 is not made worse.
`C-49` (move the `CLIMATE_VARS` registry out of Python) is unaffected and stays
— it is a visibility fix, not a config surface, and it pairs with `C-57`.

> **Owner sign-off required.** This is a new decision, not a recorded ruling.
> The alternative is to amend the `C-47` charter and take
> `climate.analysis_variables`.

---

## 8. Naming policy as applied

`N1`–`N8` are adopted as written in the scoping document. Two exemptions are
named rather than implicit:

- **`N1`** exempts established domain terms and the `n_` count prefix.
- **`N3`** exempts `project_dir` (`Q-A`) — a term of art AGENTS.md's two-tier
  location rule is written around, at 826 occurrences across 95 tracked files
  (measured 2026-08-24, `git grep -o` outside `dev/`).

**D-8.1 `N6` supplies the PREFIX; the row chooses the NOUN.** `step_num` becomes
`n_levels`, not `n_steps`: the value is one less than the number of grid steps,
and a precise-looking prefix on a misleading noun is worse than the name it
replaces.

**D-8.2 `N8` — windows are inclusive integer YEARS**, with calendar resolution
at the engine seam. Two mechanisms, not interchangeable:

| mechanism | applies to | behaviour |
|---|---|---|
| **shift** | `climate.window`, WF1 and WF3 `simulation_window` | declared years ARE water years; bounds move to water-year boundaries |
| **trim** | WF2 `reference_window`, `future_windows` | declared years are CALENDAR; computation keeps complete water years inside them — already implemented |

**D-8.3** The years-to-ISO conversion becomes ONE shared seam function.
`forcing_window_years()` is deleted; `forcing_window()` becomes a pure
years-to-ISO formatter shared by WF1 and WF3 (`C-72`); `compute_nr_years()`
loses its `ceil` and derives from `simulation_window.end` (`C-73`). They are
not merged: a window and a series length are different questions.

---

## 9. Config identity — guard, freeze, digest

`E1` establishes that these are THREE mechanisms, and the scoping document had
been treating them as one. Specifying them separately is the correction.

### 9.1 The drift guard — `C-04` re-scoped

**D-9.1** `_WF1_GUARDED` is replaced by a derived rule:

> **Guard every key of the WF1 snapshot except the `workflows.*` `enabled`
> flags.**

No maintained tuple. Three properties make this correct rather than merely
shorter:

1. **The leaf-by-leaf exception has no remaining cause.** Today the guard takes
   `shared.basin` and `shared.wflow_outvars` leaf-by-leaf because
   `run_stress_test.smk:58` narrows *"to stay experiment-invariant"* — and the
   keys forcing that narrowing are `seed` and `julia_threads`, which `C-51` and
   `C-54` remove from T1. After R14 every T1 section is identity. **D2 is
   satisfied by removing the cause, not by asserting it away.**
2. **It closes a hole.** `climate:` becomes guarded. The climate record is what
   the model was forced with, and an edit to it is unguarded today.
3. **One structural exception remains.** The `workflows.*` stanzas carry
   `enabled`, and toggling a workflow does not change what the model was built
   from. This is a property of what a stanza *is*, not a list.

**D-9.2** `compute:` needs no guard carve-out. Per `E2`, a WF1 snapshot does not
carry WF3's sections at all, so `compute:` was never inside the guard. Any
design text implying otherwise is wrong.

### 9.2 The freeze and the digest — where the carve-out actually lives

**D-9.3** `compute:` is excluded from `CONFIG_PROJECTION` (`C-79`). This is
what takes the batch keys out of `effective_config_digest` and out of
`_frozen_differences`, so changing `batch_size` never invalidates a run.

**D-9.4 S2's payoff is stated honestly.** The experiment guard becomes
mechanical because R14 empties T1 of every non-identity key — `C-51`, `C-54`,
`C-55`, `C-77` — **not** because of the three-class split. S2's surviving
payoff is `C-79` alone. The design does not claim more.

**D-9.5** `experiment_name` remains outside S2's three classes: changing it
does not change an experiment's numbers, it starts a different experiment. One
key is not a fourth class; it is recorded as a known limit of the partition.

---

## 10. Loader and validation changes

### 10.1 The hoist mechanism retires

**D-10.1** `HOISTED_SECTIONS` is `{"run_stress_test": ("reporting",)}` — one
entry (`E9`), removed by `C-77`. It is **RETIRED**, not left empty (`C-78`), on
the precedent R13 set: `CROSS_WORKFLOW_READS` was retired when D-9.7 emptied
it, and the D-9.6 scan asserts a literal zero. An empty registry that can be
refilled cannot enforce shrink-only. **This amends R13 D-10.4 (K2).**

**D-10.2** Removed with it: `parse_surfaces` from the Snakefile imports and its
call site; `config_composition.py`'s reporting-specific refusals. **STAYS
explicitly:** `shared/surface_axes.py`, the HM-7 reference implementation. No
rule called it before this change either.

### 10.2 Seam enforcement re-derived

**D-10.3** `SHARED_SEAM_KEYS` is a flat set of NAMES, so it must be
**re-derived** from the new T1 section names, never edited row by row. Nesting
moves seam coverage from leaf to group, and a T2 file could then declare a bare
`window:` uncaught. `basin` already has that property, so this is a tolerated
pattern rather than a new hole — but the re-derivation must be explicit and
tested.

### 10.3 Parse-time refusals

**D-10.4** The loader refuses, with a message naming the fix:

| condition | message names |
|---|---|
| `schema_version` absent or `< 2` | the migration command (§11) |
| a retired key present (`static_dir`, `run_historical`, `stress_test:`, `reporting:`, …) | its new home, or that it is deleted |
| `climate.selected` unset and WF1 or WF3 enabled | the candidates and WF0's comparison output |
| `climate.selected` not a member of `climate.sources` | the member set |
| an `observations:` key not in `model.outvars` | the declared outvars |
| `trajectory:` missing on either axis | that there is no default, deliberately |
| a `config_path` declared but the file missing | that deleting the key gives the workflow no settings |

**D-10.5** `climate.selected` unset with only WF0 enabled is **valid**. "I have
candidates, I have not chosen yet" is a legitimate project state.

### 10.4 Defaults, placed by authority (`Q-E`)

**D-10.6** Three destinations, chosen by authority and scope:

| the default is | destination | example |
|---|---|---|
| toolbox-wide policy a project may override | `advanced_settings.defaults` | `C-36`'s six |
| a hard limit a project may not relax | `advanced_settings.constraints` | `max_flagged_months` (`C-65`) |
| an attribute of one ENTITY | that entity's registry | `min_denominator` (`C-64`) |

**D-10.7** `advanced_settings.yml`'s `defaults:` entries each NAME their
overriding key in a comment. Three of those comments name
`shared.julia_threads`, `shared.seed` and `shared.water_year_start` — moved or
deleted by `C-54`, `C-51`, `C-53` (`E7`). The comments and
`_ADVANCED_SETTINGS_SCHEMA` move in the same commit as the keys; the schema is
closed, so they cannot drift apart silently.

---

## 11. Migration

### 11.1 `schema_version: 2`

**D-11.1** The project file gains `schema_version: 2`. A v1 set is refused with
a message naming the migration command. The project config carries no version
key today, so the bundle is the moment this becomes possible (`C-05`).

### 11.2 The rewriter (`C-38`)

**D-11.2** `scripts/split_project_config.py` is extended (or a sibling added)
into a v1 → v2 rewriter **driven by the register**, so the mapping is data, not
code. It performs, in one pass: the key renames and regroups; the file renames
(§12); the `.gitignore` glob move; and the `schema_version` stamp.

**D-11.3 D3 holds for every row except two**, and the rewriter has an explicit
per-row hook for them — "mechanical, but tell the user what changed".

### 11.3 One bundle

**D-11.4** Everything except `C-35`, `C-37` and `C-83` lands in ONE bundle with
ONE `schema_version` bump. K3 is why: a key present-vs-absent moves the digest
and refuses every already-run experiment, and that cost is payable once.
`C-35` (de-duplicate `DEFAULT_ANCHOR`) and `C-83` (the `weagen` → `weathergen`
sweep) are non-breaking under every outcome and may land independently, before
or after.

### 11.4 The two rows that are NOT behaviour-preserving

**D-11.5** Both are recorded as per-row exceptions to G6, not hidden:

| row | input | what changes | rewriter behaviour |
|---|---|---|---|
| `C-69` | a v1 config with `run_historical: false` | the run GAINS `st_0` and with it `q_wettest_month_mean` / `q_driest_month_mean` — 2 of 11 q metrics | rewrite, and SAY SO for that value |
| `N8` | a project with `water_year_start != Jan` | old bounds are calendar, new are water-year; a 9-month shift on both ends for `Oct` | **REFUSE**, naming the window it will not rewrite |

No shipped config is affected in the losing direction: the `C-69` additions are
`baseline_linux`, `wf2_fast` and the fixture, all of which GAIN two metrics they
should have had. `water_year_start: Oct` ships only as a commented example, so
`N8`'s refusal is reachable but unexercised.

---

## 12. The `C-85` rename

### 12.1 Breadth — a NEW decision requiring sign-off

**D-12.1 Full breadth: the file prefix AND every identifier derived from it.**
`snake_config_fixture` becomes `project_config_fixture`, and so on.

Leaving the identifiers would recreate, inside the same milestone, the exact
defect it exists to remove: one thing spelled two ways, with the config file
called `project_config_rapid.yml` and the fixture that loads it called
`snake_config_fixture`. The cost is mechanical and the bundle is already paying
for a sweep of these files.

**Bounded by two rules**, because not every occurrence of the string is a
filename or an identifier:

- **Grep first, triage second.** Prose that describes "the snake config" in a
  sentence is rewritten only where it names a path or an identifier.
- **`dev/milestones/**` is NOT swept** — historical records, valuable because
  unedited, governed by `dev/reference/sealed-records.yml` and frozen by
  `tests/test_sealed_records.py`.

> **Owner sign-off required.** The recorded ruling put `C-85` in the bundle and
> left its breadth open. This is that decision.

### 12.2 The `.gitignore` trap

**D-12.2** `.gitignore:140-141` ignores `test_case/` wholesale and re-admits the
seeds through `!test_case/snake_config_*.yml` alone (`E8`). **The `git mv` and
the glob edit are ONE commit**, verified with `git ls-files test_case/` — not
`git status`, which is the command that lies here: it reports the old paths
deleted and never lists the new ones.

**D-12.3** Measured 2026-08-24 by `git grep -o` over tracked files outside
`dev/`: **301 occurrences across 76 files**. The 2026-08-19 figure was 221/68 —
stale by a third in five days, which is why D-12.4 exists.

**D-12.4** Re-measure at implementation start. Any count in this document older
than that is a premise, not a fact.

---

## 13. Templates and `test_case`

**D-13.1** All four templates are renamed and rewritten to the new shape, and a
**fifth is added**: the WF0 template that never existed (`C-84`), born as
`project_config.analyze_climate.template.yml` — the point of bundling `C-85` is
that this milestone does not ship a new file under the prefix it is retiring.

**D-13.2** All four `test_case/` sets (17 files) migrate via the rewriter
itself, which is also the rewriter's first real test.

**D-13.3** `tests/data/presplit/` gains a **v1 → v2 pair**, since it exists
precisely to test migration.

**D-13.4** Template comments state, for each key: what it does, its unit where
`N2` applies, and its default's location. Per the standing rule, they carry no
incident history.

---

## 14. Validation plan

### 14.1 The ladder for this milestone

| stage | gate | why this one |
|---|---|---|
| per-commit | `pytest tests/test_cli.py` | the parse-time gate; dry-runs all four entry points and is the only place a malformed defaults YAML surfaces |
| per-commit, Python touched | `pixi run lint`, `format-check` | standing |
| branch | `pixi run test-fast` | verified green in 99.6 s (`E10`) |
| **required, not optional** | `pixi run test-full` | R14 touches `shared/` and `script:` signatures — the `workflow_contract` / `process_isolation` tier's own trigger |
| tree shape | `semantic_tree_diff.py` | `C-67`/`C-71` change `params:`-threaded values and `C-61` renames WF2 figure directories |
| numbers | `check_baseline.py check` | §14.2 |
| rename | stale-spelling sweep | §14.3 |

### 14.2 The baseline, scoped correctly

**D-14.1** G6 is falsified by **the four DATA targets only**: the two CMIP6
change-factor CSVs, `q_indicators.csv`, and `run_default/output.csv`. The three
`snake_config_*.yml` snapshot targets WILL move — R14 renames their paths and
rewrites their contents by design — and are **re-recorded, not defended**
(`E4`). R13 set this precedent exactly: *"the split moved the two narrow config
snapshots, the hoist moved all three, and zero data targets moved in either"*
(`dev/LOG.md`, 2026-08-22).

**D-14.2** Run WF1 with `--notemp` when the run feeds `check_baseline.py`:
rule 1.14 declares `run_default/output.csv` as `temp()`, and it is a manifest
target, so without the flag the gate fails "target missing" and reads as a
defect.

**D-14.3 Resolve the baseline's provenance BEFORE G6 depends on it.** The gate
is 7/7 green today, but the fixture is UNTRACKED and shared by every branch, so
a pass may reflect another branch's code — and `t2608220920` is still open
against the indicator reference. Either R13's pass-2 re-record resolved it and
that note is stale, or the green is the shared-fixture artefact. **A falsifier
whose provenance is unknown is not a falsifier.**

### 14.3 The stale-spelling sweep, and `C-37`

**D-14.4** No sweep tool exists. The migration ships one: a grep per retired
spelling across tracked files outside `dev/milestones/**`, failing on any hit.

**D-14.5 `C-37` MUST FAIL CLOSED.** It asserts its ground truth is non-empty
before reporting anything. This is not hypothetical: the register re-measure of
2026-08-24 was itself run twice because the first pass's ground-truth
extraction silently returned zero keys and the check then reported *more*
problems while knowing *less*, with nothing in its output saying so (`E5`). A
checker that fails open makes a green run evidence of nothing — which is D1
turned on D1's own proposal.

---

## 15. Alternatives considered

Alternatives to individual rows live in the scoping document against their
`C-nn`. Recorded here are the alternatives to the DESIGN's own shape.

### 15.1 Land in phases rather than one bundle

**Rejected.** K3 is decisive: a key present-vs-absent moves the digest and
refuses every already-run experiment in every project. Two phases means paying
that twice for one reshape, and users migrating twice.

**It would become preferable if** the digest gained a key-set tolerance — then
phases would cost only the tooling, and the bundle's main argument would
evaporate. That is a real design option for a later milestone and is not
proposed here.

### 15.2 Keep `shared:` and rename within it

**Rejected.** It fixes G2 and leaves G1, G3 and G5 untouched, and G5 is the one
with consequences: the guard's list stays hand-maintained because no boundary
distinguishes identity from wall-clock.

**It would become preferable if** the rename cost proved to dominate — but the
measured blast radius says otherwise, since the file set is nearly identical
either way.

### 15.3 Derive the guard from S2's section membership

**Rejected on evidence, not preference.** This was the original `C-04`, and the
`Q-F` probe refuted its premise: `compute:` was never in the guard (`E1`,
`E2`). Deriving from the SNAPSHOT (D-9.1) achieves the same goal — no
maintained list — and is correct against the mechanism that actually exists.

**It would become preferable if** the guard were ever re-pointed at the
composed document rather than the WF1 snapshot. Nothing proposes that.

### 15.4 Amend the `C-47` charter to house `C-48`

**Rejected** (§7.6). The charter's test refuses a use; admitting one use makes
it a preference. Withdrawing a non-breaking, additive row costs nothing.

---

## 16. Consequences and risks

Falsifiable, with the observable named.

| # | Consequence | Observable |
|---|---|---|
| X1 | Every already-run experiment in every project is refused once, at migration | `_frozen_differences` reports a key-union diff on first post-migration run |
| X2 | A project with `water_year_start != Jan` cannot be migrated mechanically | the rewriter refuses, naming the window |
| X3 | Three configs GAIN two q metrics | `q_indicators.csv` for `baseline_linux`, `wf2_fast`, fixture gains `q_wettest_month_mean`, `q_driest_month_mean` |
| X4 | The three config-snapshot baseline targets move | `check_baseline.py check` reports 3 of 7 changed; the four data targets unchanged |
| X5 | WF2 figure directories change name | `semantic_tree_diff.py` reports a tree-shape change; rule 2.06 re-fires |
| X6 | Editing `batch_size` stops invalidating a run | change `batch_size`, re-run WF3, no frozen-experiment refusal |
| X7 | Renaming without the glob move silently untracks the seeds | `git ls-files test_case/` returns nothing for the new names |
| X8 | A project may no longer express a sub-annual window bound | a config with `1990-06-01` is refused at parse time |

**Residual risk, ranked.**

1. **The baseline's provenance (D-14.3).** The highest risk in the milestone,
   because G6 is the whole safety argument and its falsifier's status is
   unknown. Resolve first.
2. **`SHARED_SEAM_KEYS` re-derivation (D-10.3).** A flat name set against a
   nested layout; a missed name is an uncaught T2 declaration, which fails
   silently rather than loudly.
3. **Breadth of `C-85` (D-12.1).** 301 occurrences and growing; the count is
   already known stale once.
4. **`C-37` failing open (D-14.5).** Demonstrated once, in this milestone's own
   preparation.

---

## 17. Open questions

None blocking. Two decisions in this document are NEW rather than recorded
rulings and need owner sign-off before implementation:

1. **`C-48` withdrawn** (§7.6, D-7.10) — or the `C-47` charter is amended and
   `climate.analysis_variables` lands in T1.
2. **`C-85` full breadth** (§12.1, D-12.1) — filenames plus every derived
   identifier, or filenames only.

One item is a prerequisite rather than a question:

3. **Resolve the baseline's provenance** (D-14.3) before G6 leans on it.

---

## 18. Revision log

| version | date | change |
|---|---|---|
| v1 | 2026-08-24 | Initial draft. Authored directly by the driver; `design-review-loop` waived by the owner. Carries two new decisions (D-7.10, D-12.1) and one prerequisite (D-14.3). |
