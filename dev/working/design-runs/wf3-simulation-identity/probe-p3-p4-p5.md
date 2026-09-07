# Framework-feasibility probes P3, P4, P5 — wf3-simulation-identity

Run: wf3-simulation-identity | probed 2026-09-07 | commit `f4b24b6c`

## P3 — hydromt catalog key resolution (GF-7)

**Question** — Does hydromt resolve the per-run one-entry data catalog when its
entry key changes shape from `rlz_<r>_st_<m>` to `run_<id>`? Does anything in
hydromt or in our code constrain the key's grammar?

**Method** — Executed, standalone, no Snakemake:
`.tmp/scratchpad/2026-09-07_probe345/p3_catalog_key.py`. Per candidate stem: write a
weathergenr-shaped NetCDF (`longitude/latitude/time`, empty global attrs), build the
one-entry catalog through **our own** `prepare_clim_data_catalog` against a synthetic
project catalog with an `era5` entry, parse with
`DataCatalog(data_libs=[member, project])` in the rule's member-first order, then
`get_source(<key>)` and `get_rasterdataset(<key>)` — the read `setup_precip_forcing` does.

Where our code writes and reads the key:
- write — `blueearth_cst/climate_analysis/prepare_climate_data_catalog.py:56`,
  `name = os.path.basename(fn).split(".")[0]`; entry dumped at `:115-123`.
- caller — `blueearth_cst/experiment/downscale_climate_forcing.py:89-98`
  (`prepare_clim_data_catalog(..., fn_out=catalog_out)`, then member catalog
  prepended to `data_libs`).
- read — same file `:104` `climate_name = os.path.basename(Path(fn_in)).split(".")[0]`,
  used as `precip_fn=climate_name` (`:178`) and `temp_pet_fn=climate_name` (`:183`),
  which reach `DataCatalog.get_rasterdataset` **by key**.
- rule — `run_stress_test.smk:1086` declares the catalog output,
  `:1073` the input NC. Both stems are the same token, which is why the key follows
  the id rename for free.

**Result** (hydromt 1.3.1)

| stem | key written | `get_source` | `get_rasterdataset` |
|---|---|---|---|
| `run_0007` | `run_0007` | OK | OK (`precip/temp/pet`, EPSG:4326) |
| `rlz_001_st_00` (today) | `rlz_001_st_00` | OK | OK |
| `run-0007` | `run-0007` | OK | OK |
| `0007` (bare digits) | `0007` | OK | OK |
| `run.0007` | **`run`** — truncated | OK | OK |
| `run_0007_x[y]` | `run_0007_x[y]` | OK | **`NoDataException`** from the `convention` URI resolver |

Two grammar constraints, both measured and neither on `run_<id>`:
1. **A dot truncates the key** at the first `.` — but *symmetrically*, because
   writer (`:56`) and reader (`:104`) use the identical `split(".")[0]`, so lookup
   still succeeds. It silently collides if two runs share a pre-dot prefix.
2. **`[` / `]` break the read, not the key.** `get_source` resolved; the failure is
   hydromt's `convention_resolver` globbing the `uri`. So the constraint is on the
   **filename**, not on the catalog key.

**Verdict** — **feasible, measured.** hydromt 1.3.1 resolves a one-entry catalog
under a `run_0007` key end-to-end, including the actual raster read. The key is not
parsed, pattern-matched or namespaced by hydromt; it is a plain dict key. Bare
digits work, so even an unprefixed id would resolve.

**What this constrains in the design**

1. The key is **derived from the NC filename stem, not declared**. The design does
   not need a catalog-key change at all: rename `{wg_dir}/output/rlz_<r>_st_<m>.nc`
   to `run_<id>.nc` and the key follows. Nothing reads `rlz_`/`st_` out of the key.
2. **Keep `[`, `]` and `.` out of the run id.** `.` is a silent-collision hazard
   (`run.1` and `run.2` both key `run`); `[`/`]` fail at read time with a
   `NoDataException` that names a file that exists. `run_<zero-padded int>` is safe.
3. The one exception is the orography sidecar entry `f"{source_like}_orography"`
   (`prepare_climate_data_catalog.py:96`) — keyed by source, not run, so unaffected.
4. GF-7 needs **no rule-3.14 execution**: this exercised the same two functions the
   rule calls, with the same argument shapes.

## P4 — grain-declaration rerun triggers (GF-6, GF-16)

**Question** — Does a change to a metric's grain declaration re-fire the rules that
depend on it? Case (a) a `params:` **value** changes; case (b) a function **body**
changes with the param value unchanged; case (c) the same two questions for rule 3.09.

**Method** — Snakemake 9.6.2, default `--rerun-triggers`. Four standalone probes under
`.tmp/scratchpad/2026-09-07_probe345/`, each: seed a real run, mutate one thing, `-n`.

- `p4/` — `run:` rule, `params.bundle_by` read from `metrics.json`, body calls
  `grainlib.bundle_key()`. `P4_DIGEST=1` adds `grain_src_sha` = sha256 of `grainlib.py`.
  **The `p4/Snakefile` on disk is the later dict-param variant**: the harness was
  rewritten in place between the scalar cases (a)/(b)/(b′)/(b″) and the dict cases.
- `p4b/` — `script: main.py` rule; `main.py` imports `grainlib`. Isolates the **`code`**
  trigger's scope for the shape rule 3.16 actually has.
- `p4c/` — two rules on the same `cfg.yml`, one `ancient()`, one plain.

Real-rule side, read not run: rule 3.09 `run_stress_test.smk:875-899`; rule 3.16
`:1244-1284`; `stress_test_cfg = my_cfg["stress_test"]` at `:186`.

**Result**

| # | mutation | scheduled? | reason line |
|---|---|---|---|
| (a) | `params.bundle_by` `annual` → `seasonal` | **YES** | `params have changed since last execution` |
| (b) | `grainlib.bundle_key()` body changed, params unchanged | **NO** | `Nothing to be done` — and the real re-run also did nothing; `out.txt` kept the stale `annual` |
| (b′) | same body change, with `grain_src_sha` in `params:` | **YES** | `Params have changed ... before: 'b5f20cd8236e' now: '95edf3718c3c'` |
| (b″) | **comment-only** edit to `grainlib.py`, digest in `params:` | **YES** | digest moved `95edf3718c3c` → `597af8203c95` — the digest **over-fires** |
| code-1 | edit the `script:` file `main.py` itself | **YES** | `code has changed since last execution` |
| code-2 | edit `grainlib.py`, **imported by** `main.py` | **NO** | `Nothing to be done` |
| dict-1 | **dict-valued** param, nested value `1.2`→`1.3` (3.09's actual param *shape*) | **YES** | reason prints both mappings |
| dict-2 | same dict, **key order changed only**, content identical | **YES** — a false positive | reason prints two equal-content mappings |
| anc | edit an `ancient()` input's content and mtime | **NO** (the plain-input twin in the same run: YES) | `updated input files: with_plain` only |

**Verdict**

- **(a) — measured, works.** A declaration travelling through `params:` re-fires the
  rule on the next invocation. GF-6 case (a) is closed.
- **(b) — measured, the trap is real and silent.** `code-2` shows why: the **`code`
  trigger covers the `script:` file only, not the modules it imports** — exactly where
  3.16's grouping registry would live. Failure mode is `Nothing to be done` with a
  stale `q_indicators.csv`, no warning, exit 0.
- **(b′) — measured, the design's fix works.** A source digest in `params:` closes
  case (b). Cost, measured as (b″): it fires on any byte change, comments included, so
  a formatting-only commit reruns 3.16. The design should say so.
- **(c) — rule 3.09: the mechanism is present, and the design's premise about it is
  STALE.** `ancient()` is confirmed to suppress (probe `anc`), so the config *files*
  trigger nothing. But 3.09 **does carry a `params:`** today —
  `stress_test_cfg = stress_test_cfg` at `:888`, landed in `b5052339` (2026-08-21,
  R13 D-10.6), reading the resolved `my_cfg["stress_test"]` mapping from `:186`. By
  measurement (a), an edit that changes that resolved mapping therefore **does**
  schedule 3.09. The "deaf, no `params:`" record (`dev/milestones/r12/
  stress-test-lookup-intake.md:141` E5, verified 2026-08-15, citing `:819-821`)
  predates that commit and no longer describes the rule. **The live instance of the
  trap that GF-16 is built on does not exist any more.** What survives for 3.09 is
  case (b): a grain digest added to its `params:` behaves as (b′), and a change to
  any module `prepare_stress_test_grid`'s script imports is invisible unless digested.

**What this constrains in the design**

1. **The two GF-6 cases have different closures and must stay separated.** (a) is free
   once the declaration is in `params:`. (b) requires an explicit digest; nothing about
   passing declarations through `params:` closes it.
2. **Digest the module, not the script.** `code` already covers
   `export_wflow_results.py` and `prepare_stress_test_grid`'s script. The digest must
   cover the **grouping-registry module** — the imported one — or it adds nothing.
3. **State the over-fire.** A source digest fires on comments and whitespace. If that
   is unacceptable, the alternative is digesting a normalised form (e.g. the
   registry's resolved declaration mapping rather than its source bytes) — untested here.
4. **Correct the design's premise for 3.09 / GF-16.** §9's "same `ancient()` trap as
   GF-6" and `simulation-identity-intake.md:388`'s "rule 3.09 is deaf to `stress_test`
   edits" are both false against the current file. GF-16 should be re-worded to case
   (b) only; case (a) for 3.09 is already closed in the tree.
5. The **real-rule differential test could not be run** — see "Not settled".

## P5 — tree-check classification (GF-8)

**Question** — Does `pixi run tree-check` classify a renamed tree, and must
`build_project_tree_rules` be extended in the same commit?

**Method** — Read plus direct exercise; no pipeline run.
`pixi.toml:187` — `tree-check = python dev/scripts/snapshot_project_tree.py --config
test_case/snake_config_baseline.yml`; that driver builds its map from
`semantic_tree_diff.build_project_tree_rules` (`snapshot_project_tree.py:259`) and
exits 1 on any `UNMAPPED` (`:41`, `:279`). Probe
`.tmp/scratchpad/2026-09-07_probe345/p5_classify.py` imports the module, builds the
rules for `experiment` / `era5_20000101_20201231`, and runs `classify_path_map` over
every token-carrying WF3 path in both spellings.

**Result**

- **Code, not a snapshot.** `build_project_tree_rules`, `semantic_tree_diff.py:270-524`,
  builds 63 identity rules at call time from `experiment_name` / `dataset_key`.
- **No rule names the member token.** The only rules matching `rlz`/`st_` are
  `logs/wf3_run_stress_test_[a-z0-9_]+\.log` and the literal
  `experiments/<e>/config/stress_test_lookup.csv`. Every per-run artifact is covered
  by a **directory prefix** — `climate/weathergenr/output/`, `hydrology/wflow/`,
  `results/`, `logs/_parts/`, `benchmarks/_parts/` (`:332`, `:336`, `:462-512`).
- Classification, measured:

| path (per-run) | today `rlz_001_st_00` | renamed `run_0007` |
|---|---|---|
| `…/climate/weathergenr/output/<id>.nc` | IDENTITY | IDENTITY |
| `…/hydrology/wflow/forcing/inmaps_<id>.nc` | IDENTITY | IDENTITY |
| `…/hydrology/wflow/config/<id>.toml` and `.yml` | IDENTITY | IDENTITY |
| `…/hydrology/wflow/output/<id>.csv`, `outstates_<id>.nc` | IDENTITY | IDENTITY |
| `logs/_parts/<exp>/3.14_…/<id>.log` | IDENTITY | IDENTITY |
| `benchmarks/_parts/<exp>/3.14_…/<id>.tsv` | IDENTITY | IDENTITY |

- **The design's two NEW files are UNMAPPED**, measured:
  `experiments/<e>/config/scenario_table.csv` and
  `experiments/<e>/config/.scenario_table.sha256`. The experiment's `config/` is
  enumerated leaf by leaf (`:462-488`), deliberately, so a new leaf there fails the gate.
- **No dangling-declaration report.** The driver reports `UNMAPPED` only; there is no
  unused-rule report and no test asserting one, so a stale `rlz_*` row would be **inert
  and silent forever** — not "undeclared on every run".

**Verdict** — **GF-8 as worded is safe, but its stated reason is wrong.** The rename
survives tree-check not because the inventory understands the new id, but because it
never named the old one. `build_project_tree_rules` needs **no** change for the
rename. It needs **two rows added in the same commit** for the design's new artifacts.

**What this constrains in the design**

1. Add `config/scenario_table.csv` and `config/.scenario_table.sha256` to the `leaf`
   tuple at `semantic_tree_diff.py:462-488` in the commit that lands rule 3.09's second
   output. Measured, not predicted: both are UNMAPPED today.
2. **Do not add per-run rows for the renamed artifacts** — the prefixes already cover
   them, and a narrower row would be the over-specification the module's docstring
   (`:302-305`) warns against.
3. `tests/test_project_tree_inventory.py:207-209` hardcodes samples spelled
   `rlz_1_st_2.toml` / `.csv` / `.log`. They keep passing after the rename (prefix rules)
   but then assert a shape nothing produces — update them in the same commit.
4. **Split verdict:** the classifier is measured; whether a *real* post-change tree holds
   other undeclared paths is not, and still wants the completed run §9 names.

## Claims moved off [assumed]

| GF | was | now | evidence |
|---|---|---|---|
| **GF-7** | `[argued]`, P3 unexecuted | **measured, holds** — hydromt 1.3.1 resolves a one-entry catalog keyed `run_0007` through `get_source` *and* `get_rasterdataset`; the key is a plain dict key derived from the NC stem | `p3_catalog_key.py`, six stems; `prepare_climate_data_catalog.py:56`, `downscale_climate_forcing.py:104,178,183` |
| **GF-6 (a)** | `[assumed]`, P4 unexecuted | **measured, holds** — a changed `params:` value schedules the rule; also holds for a **dict**-valued param mutated at a nested key | `p4/`, cases (a), dict-1 |
| **GF-6 (b)** | `[assumed]` | **measured on both halves** — an imported module's body change does **not** schedule (`code` covers the `script:` file only); a source digest in `params:` **does** | `p4/` (b), (b′); `p4b/` code-1, code-2 |
| **GF-8** | `[assumed]` | **measured, holds — for a different reason than stated.** The rename classifies IDENTITY under existing directory prefixes; no inventory rule names the member token. But the design's two new `config/` leaves classify UNMAPPED and must be added in the same commit | `p5_classify.py`; `semantic_tree_diff.py:270-524` |
| **GF-16** | `[assumed]`, "same `ancient()` trap as GF-6" | **premise falsified; claim split, and BOTH halves now measured on the real rule (see Addendum).** Rule 3.09 carries `params: stress_test_cfg` since `b5052339` (2026-08-21), so case (a) is **already closed in the tree**; case (b) — a change to a module its script imports — remains open and needs the same digest as 3.16 | `run_stress_test.smk:888`; `dev/milestones/r12/stress-test-lookup-intake.md:141` (E5, 2026-08-15) predates it |

## Not settled, and what it would take

1. ~~**The real-rule differential for 3.09 and 3.16.**~~ **SETTLED for 3.09** by the
   authorised run — see the Addendum. The 3.16 half is still not run and is not worth
   authorising (mechanism measured; rule shape read at `:1244-1284`). The obstacles
   recorded below are what made the *cheap* route necessary, and are kept for the
   record.

   Two independent obstacles
   in this worktree, both measured:
   - the control dry-run schedules **all 43 jobs** — `check_project_consistency` reports
     `code has changed since last execution` and cascades — so no rule's scheduling is
     attributable to a `params:` edit;
   - `--list-params-changes` printed **nothing** both before and after a real edit to
     `stress_test.temp.mean.max` in `test_case/snake_config_baseline_run_stress_test.yml`
     (edit restored with `git checkout --`), while the same flag correctly named
     `out.txt` in the standalone harness. So it cannot serve as the differential either.

   **An unresolved inconsistency, reported rather than explained.** `.snakemake/metadata/`
   holds 105 records and **none of them decodes to a `test_local` path** — verified twice
   (all 105 base64 names decoded in Python with correct padding, zero decode failures;
   and a PowerShell recursive enumeration confirming 105 flat files, no nesting, no
   `dGVzdF9jYXNl*` name). Yet `--list-changes code` on the real workflow **does** name six
   `test_local` paths including `config/stress_test_lookup.csv`. In the standalone harness
   an absent record produces *neither* listing, for both `run:` and `script:` rules. I
   could not reconcile these in three attempts and stopped; the operational conclusion is
   unaffected, because both obstacles above are direct observations of the real tree.

   **Cheapest sufficient run:** `snakemake -c3 -s run_stress_test.smk --configfile
   test_case/snake_config_baseline.yml --notemp --until prepare_stress_test_grid` — 3.09
   plus its consistency/config upstream only, no weathergenr and no Wflow, so minutes not
   hours. Run it twice (clean, then with a `stress_test` edit) and it settles GF-16
   case (a) on the real rule, and incidentally resolves the inconsistency above. GF-6 on
   the real 3.16 needs the full sweep and is **not** worth authorising: the mechanism is
   measured, and the rule's `params:` / `script:` shape is read directly from `:1244-1284`.
2. **Whether a completed post-rename tree holds other undeclared paths** (GF-8's second
   half). Needs one completed WF3 run plus `pixi run tree-check`. Not authorised, not run.
3. **A normalised grain digest** — whether digesting the resolved declaration mapping
   instead of source bytes avoids the (b″) comment-only over-fire. Not tested.

## Incidental findings

- **Dict-valued `params:` are key-order sensitive.** Reordering keys with identical
  content re-fired the rule (`dict-2`). 3.09's `stress_test_cfg` is assembled by
  `config_composition.py` under R13; if that assembly's key order is not deterministic,
  3.09 re-fires on runs where nothing changed. Worth a separate check.
- **The `code` rerun trigger stops at the `script:` file.** A general hazard for every
  `script:` rule that imports `blueearth_cst/` helpers — not specific to this milestone.
- **A source digest in `params:` over-fires on comments and whitespace** (b″).
- **hydromt's URI resolver, not its catalog, constrains the id grammar**: `[` / `]` in a
  filename raise `NoDataException` naming a file that exists; a `.` silently truncates
  the catalog key (harmlessly today, because writer and reader share the same
  `split(".")[0]`).
- **A falsifier worded "dry-run and assert rule X is scheduled" is untestable against
  the seeded `test_local` today** — the consistency-rule code trigger schedules the
  whole DAG regardless. §9's GF-6/GF-16 gates need to name a *clean* tree, or to be
  worded against `--list-params-changes` on a tree the gate itself just built.

## Environment

- pixi 0.70.2; Snakemake 9.6.2 (default `--rerun-triggers`); hydromt 1.3.1;
  Python 3.12.13 (conda-forge), win-64.
- `profiles/default/config.yaml` auto-loaded (`quiet: reason`) for real-workflow
  invocations; the standalone Snakefiles ran from their scratch dirs with
  `--manifest-path` and no profile.
- Config: `test_case/snake_config_baseline.yml` (+ its `_run_stress_test.yml` sibling)
  against the seeded `test_case/test_local`. `snake_config_rapid.yml` not usable here
  (`test_case/test_rapid` unseeded — P1/P2 finding, unchanged).
- Scratch: `.tmp/scratchpad/2026-09-07_probe345/{p3,p4,p4b,p4c,p5_classify.py}` (gitignored).
- One tracked file was temporarily edited
  (`test_case/snake_config_baseline_run_stress_test.yml`, one `max:` line) and restored
  with `git checkout --`.
- Git status at finish: `?? dev/working/design-runs/wf3-simulation-identity/probe-p3-p4-p5.md`
  only — **no modifications to tracked files**.

## Addendum — P4 real-rule differential, executed 2026-09-07 (authorised)

The owner authorised the `--until prepare_stress_test_grid` run proposed in "Not
settled" #1. It was executed. Everything below is measured on the real rule 3.09.

**Method** — `pixi run snakemake -c3 -s run_stress_test.smk --configfile
test_case/snake_config_baseline.yml --notemp --until prepare_stress_test_grid`.
Dry-run first: **2 jobs** (3.01 `check_project_consistency`, 3.09). Real run: **9 s**
total, exit 0, both jobs done. Then three probes, each a dry-run of the same target:
(1) clean; (2) after editing `stress_test.temp.mean.max` `3.0`→`3.1` in
`test_case/snake_config_baseline_run_stress_test.yml`; (3) after a body edit to
`snake_utils.stress_test_grid` — the module 3.09's script
(`blueearth_cst/experiment/prepare_cst_parameters.py:23`) imports — with the config
back at its committed value, so `params.stress_test_cfg` is byte-identical.
Both tracked files restored with `git checkout --`.

**Result**

| probe | 3.09 scheduled? | reason | `--list-params-changes` |
|---|---|---|---|
| clean, immediately after the run | **NO** — `total 0` | — | nothing |
| `stress_test` config edit | **YES**, and it is the *only* job (`total 1`) | `params have changed since last execution: prepare_stress_test_grid` | names `test_case/test_local/experiments/experiment/config/stress_test_lookup.csv` |
| imported-module body edit, params unchanged | **NO** — `total 0` | — | (not queried) |

**GF-16, re-split as it should read**

- **GF-16 (a) — a declaration edit that changes the resolved `stress_test` mapping
  re-fires rule 3.09. ALREADY CLOSED IN THE TREE — measured, not assumed.** Closed by
  `params: stress_test_cfg = stress_test_cfg` (`run_stress_test.smk:888`, added in
  `b5052339`, 2026-08-21). **The design must not claim to close this**, and must not
  present it as a risk it mitigates; it inherits it. Its only obligation is not to
  remove that param. Falsifier, should anyone want to re-check: the run above.
- **GF-16 (b) — a change to a module rule 3.09's script IMPORTS does not re-fire it.
  OPEN, measured open.** `snake_utils.stress_test_grid` is exactly such a module, and
  it is the grid arithmetic. Snakemake's `code` trigger covers
  `prepare_cst_parameters.py` and stops there. **Falsifier for the design:** with a
  grain-declaration source digest in 3.09's `params:`, edit the grouping/enumeration
  module's body without touching the config, dry-run
  `--until prepare_stress_test_grid`, and assert 3.09 is scheduled. Today that same
  edit yields `total 0`.

**Provenance of the stale claim — true when recorded, stale six days later.**
`dev/milestones/r12/stress-test-lookup-intake.md:141` records E5 ("Rule 3.09 is deaf
to `stress_test` edits", citing `run_stress_test.smk:819-821`, `config = ancient(...)`
and no `params:`) as **Verified 2026-08-15**. It was correct on that date. `b5052339`
(2026-08-21) added the `params:` and invalidated it. The claim then propagated
forward into `stress-test-lookup-design.md:1034`, `:1170`, `:2689` and into
`simulation-identity-intake.md:388`, where it is the entire rationale for probe P4.
This is a **record that went stale**, not a document that was wrong — the distinction
matters, because the fix is a dated re-verification of E5 wherever it is cited, not a
correction of the milestone record (which is sealed and correct as of its date).

**On the `.snakemake/metadata/` inconsistency** — one line, added because the run
supplied it and no hunting was needed. After the run the store held **108** records,
of which **3** are keyed by the workdir-relative path `test_case/test_local/...`
(base64 prefix `dGVzdF9jYXNl`); before it, **0** of 105 were. So the store location
and key form the earlier scan used were right, and the scan's negative result stands.
The inconsistency — `--list-changes code` naming `test_local` paths that had no
record — is therefore unchanged and still unexplained. Left as reported.
