# WF3 v2.0 — Climate Experiment: ledger-driven sweep (DRAFT v4)

```
Status:     DRAFT v4 — authored for the design-review-loop run `wf3-experiment-v2`;
            not accepted, not admitted to a milestone, no implementation authorised
Date:       2026-08-01
Run slug:   wf3-experiment-v2
Genre:      workflow-spec (design-document skill; R8 precedent
            dev/workflows/wf2-climate-analysis-v2-design.md)
Milestone:  R9 (proposed)
Authors:    tanerumit (with Claude Code, cst-architect)
Supersedes: none
Body budget: The binding rule, declared at creation: **review rounds relocate and
            replace, never add.** Any revision that would grow the body moves the
            text it supersedes into the run's review record
            (`dev/working/design-runs/wf3-experiment-v2/`) in the same edit, and
            the ACCEPTED body must not exceed v1's size. R8 reached 2 761 lines
            by accretion across four rounds; that is the failure mode this rule
            exists to prevent.
            Measured size of v1: 1 903 lines, roughly 45 % of it tables,
            schemas, probe transcripts and gate definitions — the normative
            contract itself rather than prose. v2 = 2 969 lines: relocation
            (§9.1/§9.4/§15.2 rewritten, superseded text left readable in the
            append-only `design-v1.md`) did not cover 52 dispositions.
            v3 = 3 195 lines: the six external findings were fixed by in-place
            mechanism replacement, +7.6 % net. v4 = 3 420 lines: the seven
            round-cap-arbitrated findings (ext2-1..ext2-7) fixed, again in
            place, +6.9 % net. The overage and the compression order are
            stated in §17, for G2.
Revisions:
  - 2026-08-01: initial draft (design-v1.md)
  - 2026-08-01: revision r1 (design-v2.md) — 52 internal-panel findings
    dispositioned; see §17 and `ledger.md`
  - 2026-08-01: revision r2 (design-v3.md) — external round 1 (ext1-1..ext1-6)
    dispositioned; five faulted v2 mechanisms replaced; see §17 and `ledger.md`
  - 2026-08-01: revision r3 (design-v4.md) — external round 2 (ext2-1..ext2-7)
    dispositioned under owner arbitration of 2026-08-01 (round cap reached; all
    seven accepted, fix required); see §17 and `ledger.md`
```

Scope authority: `dev/workflows/wf3-climate-experiment-v2-intake.md` (commit
`edc0689`). Its § Approved architecture is a **fixed anchor**: this design does
not re-litigate the 4-stage shape, the ledger-driven sweep, the persistent Julia
pool, or per-realization generation. Its OQ-1..OQ-7 are what this design settles
(§9). Run intake: `dev/working/design-runs/wf3-experiment-v2/intake.md`.

**Gate G1 rulings (2026-08-01) are settled framing throughout this document, not
open questions.** OQ-1 `precip_variance`: **deferred entirely** — the axis stays
inert this milestone, no `scale_var_with_mean` change, the field is retained in
every schema, and `verbose = TRUE` at the R call site is the one carved-out,
value-neutral change (§9.1). Drift guard: the three-layer reading is ratified
(§7.1). OQ-4: fail-loud default plus `allow_partial`, **no** completeness
threshold (§9.4). `response_long.csv` joins the baseline manifest. Milestone id
**R9**.

**Fixture arithmetic.** Every fixture-scale number in this document is computed
against `config/workflows/snake_config_model_test.yml` **as tracked**:
`realizations_num: 2`, `run_historical: false` ⇒ `ST_START = 1`
(`Snakefile_climate_experiment:55-56`), `stress_test.temp.step_num: 1` /
`precip.step_num: 2` ⇒ `ST_NUM = 2 × 3 = 6`
(`blueearth_cst/shared/snake_utils.py:620-622`), and `aggregate_rlz: true`.
Therefore **K = 2 × 6 = 12 members, none of them `cst_0`**, and `Qstats.csv`
carries **6 rows per statistic** (one per `cst` index), not one row per member.
This is the K `dev/p33/batching-results.md:100,182` measured against. The
milestone does **not** flip the fixture (G1 gate-return ruling).

---

## 1. Problem and goals

### 1.1 The problem, compressed

The inner `RLZ_NUM × ST_NUM` sweep has outgrown the file-per-wildcard DAG. Five
grounded pains (full statement in the scoping intake § Why a ground-up redesign;
evidence rows P1–P5 in §11):

1. **The cost is session warm-up, not process startup** (P1). `F ≈ 24 s`,
   `S_cold ≈ 92 s`, `S_warm ≈ 35 s`. A persistent worker captures the
   `S_cold → S_warm` discount for *every* member; LPT batching captures it only
   within a batch.
2. **The batch construct carries structural debt.** `Snakefile_climate_experiment:524-546`
   is a parse-time loop generating anonymous `run_wflow_batch_<b>` rules; logs and
   benchmarks are keyed by batch id, and C5 failure isolation is degraded to batch
   granularity (P3-3 GN-4: one failed member deletes `B−1` sibling CSVs).
3. **The disk-aware batch-size default is unsolvable at parse time**
   (`dev/followups.md` § Post-P3-3): the estimate needs forcing sizes that do not
   exist when the rules are built.
4. **Rule 3.06 writes all realizations in one job**
   (`Snakefile_climate_experiment:379-391`), so any re-run touching a `temp()`
   intermediate cascades through it into every batch (P5: 19 jobs / 247.7 s to
   materialise three `rlz_1_cst_1` targets).
5. **Baseline NCs are `temp()`** (`:385`), which makes that cascade structural.

### 1.2 Goals

- **G1 — Blast radius = 1 member.** A failing member costs itself only; completed
  sibling indicators survive on disk and are not recomputed.
- **G2 — Resume is measured, not asserted.** A hard-killed sweep re-invokes and
  runs only unfinished members, with a coherent, auditable attempt history.
- **G3 — Peak transient disk = `p × 1` member's artifacts within one
  invocation**, independent of sweep size, by construction rather than by a tuned
  constant. Across invocations the property is not free: the resume fold's
  transient cleanup is what keeps it true after an interrupted sweep (§6.6).
- **G4 — Per-member visibility** — log, timing and status per member, replacing
  the batch-id granularity P3-3 accepted.
- **G5 — Cross-realization parallelism in generation**, with per-realization seeds
  recorded in an artifact.
- **G6 — The seam contracts hold**, with every delta enumerated (§10) and the
  contract docs updated *with* the milestone.
- **G7 — Performance floor:** not worse than P3-3 batching **across the same
  scientific boundary** — from a tree with prepare, generation and the catalog
  complete to all `K` member CSVs present — at fixture scale under a held `p × M`
  budget, both legs measured in the same tree as **≥ 3 counterbalanced AB/BA
  pairs**, gated on the **median** pool-vs-batch comparison with all spans and
  dispersion reported (§13 step 8); the at-scale advantage stated as a model
  from measured terms, never claimed as measured.
- **G8 — Entry contract unchanged.** `snakemake all -s Snakefile_climate_experiment
  --configfile …` works as before; `run_workflows.py`'s wrapper contract and the
  `workflows:` config section are untouched.

### 1.3 Non-goals

Verbatim by reference: scoping intake § Cut (YAGNI) / non-goals. Restated only
where this design brushes them: no weathergenr / hydromt / Wflow internal
changes; no CMIP coupling of the experiment; no multi-node execution; no
PackageCompiler sysimage; no new runtime dependency (§2.3).

---

## 2. Scope, fixed anchors, and assumptions

### 2.1 Fixed anchors (not re-litigated here)

| Anchor | Source |
|---|---|
| Snakemake stays the outer skeleton over 4 scientific stages | intake § Approved architecture |
| The inner sweep leaves the file-per-wildcard DAG for manifest + ledger | idem |
| A persistent Julia worker pool loads Wflow once | idem |
| Generation is one job per realization with explicit seeds; baseline NCs not `temp()` | idem |
| Reduce is ledger-driven; `Qstats.csv` / `basin.csv` survive; a tidy long table is added | idem |
| The drift guard's mechanism folds into the manifest's recorded digests | idem (see §7.1 for how this design honours it) |
| The keyed historical store (R07 B1) is untouched | idem |

### 2.2 Assumptions

- **A1 — Single machine, single writer.** The sweep runs as one Snakemake job on
  one box. Every ledger write comes from one process by construction (§6.3). No
  distributed coordination is designed for; the experiment-scoped lock (§6.6)
  exists to make a *violated* assumption fail loud, not to support concurrency.
- **A2 — Members are independent.** No cross-member state chaining exists today:
  every per-cst TOML carries `cold_start__flag = true` and declares no `instates`
  input (hydrological-model seam § Considered and corrected). The sweep may
  therefore schedule members in any order.
- **A3 — Perturbation is deterministic at our call site** (P8, and §9.1's probe:
  `seed` is a formal of `apply_climate_perturbations` and the call site omits it,
  with no active stochastic branch). Re-running a member reproduces its forcing.
- **A4 — Warm-session ≡ cold-process output identity** (P3): 102 files
  byte-identical at tolerance 0. The pool extends the warm session from `B` runs
  to the whole sweep; this design assumes the identity extends with it and makes
  that an explicit falsifiable claim (§12, C-7), not a settled fact.
  **Scope limit, stated because the fixture cannot close it.** At fixture scale
  `K = 12` and the default `p = 3`, so each Julia session serves ~4 members —
  the *same* depth P3-3 already measured at `B = 4`
  (`dev/p33/batching-results.md:16,139`). The fixture therefore adds no session
  depth at the default. C-7 is consequently specified at `sweep_workers: 1` in
  **both** of its legs, with session depth varied by `worker_max_members` alone —
  `1` (a fresh Julia session per member, the cold-process reference) against `0`
  (one session carries all 12 members, 3× P3's depth) — so depth is the *only*
  variable (§9.6), and **A4 at production depth — hundreds of members per
  session — remains open**,
  with the recycling bound of §6.3 as its pre-designed mitigation and a named
  re-verification trigger in §15.3.
- **A5 — Julia is juliaup-managed and on `PATH`** (`AGENTS.md` Hard Constraints);
  the worker is launched exactly as rule 3.10 launches the batch driver today.
- **A6 — Wflow's per-member outputs are written directly by Wflow** to the paths
  the TOML names. The runner never rewrites them; it verifies and records them.

### 2.3 Dependency footprint

**Zero new packages.** The orchestrator uses only the Python standard library
(`multiprocessing`, `subprocess`, `json`, `hashlib`, `os`, `pathlib`, `uuid`)
plus what `blueearth_cst` already imports; the worker uses Julia `Base` plus the
already-required `Wflow`. JSON over stdin/stdout is chosen partly for this
reason (§6.2, and §14.4 for the rejected alternatives that would have cost a
dependency). No owner dependency ask is raised by this design.

### 2.4 Inputs and provenance

| Input | Provenance | How this design uses it |
|---|---|---|
| `config/workflows/snake_config_*.yml` (`workflows.climate_experiment` + `shared` + `project`) | User-authored; forwarded as `config_path` to R scripts (repo convention) | The freshness boundary: canonicalised into `config_digest` and per-member `member_hash` (§5.1) |
| `<project_dir>/config/runs/snake_config_model_creation.yml` | wf1 snapshot, written by wf1's `copy_config` | Drift comparand; its digest is recorded in the manifest and re-verified at sweep start (§7.1) |
| `<project_dir>/config/runs/snake_config_climate_projections.yml` | wf2 snapshot; **optional** (the overlay is optional per the CST method) | Same, `ABSENT` when missing (`file_digest_or_absent`) |
| `climate_historical/<key>/extract_historical.nc` | Rule `extract_climate_grid`, declared identically in wf1 (1.10) and wf3 (3.02) from `climate_store_spec` | WG-1 input to generation; untouched |
| `hydrology_model/{staticmaps.nc, wflow_sbm.toml, instate/}` | wf1 | Read by the per-member forcing build; untouched |
| `config/catalogs/*_data*.yml` | Tracked catalogs | hydromt `-d` input; untouched |
| `config/templates/weathergen_config.yml` | Tracked template | Supplies **every** generator parameter (`knn.sample.num`, `warm.*`, `mc.*.quantile`, dry/wet spell change, `general.variables`), copied verbatim into the per-realization config (`prepare_weagen_config.py:57,67-68`) and passed straight to weathergenr (`generate_weather.R:43-58`). Recorded as `run.weagen_template_digest` and threaded as a `params:` value of 3.01 and 3.05 |

Provenance preservation: every result-affecting input above contributes to
`config_digest` or is recorded by digest in the manifest (§5.1), so the run's
own record answers "what was this built from" without consulting the DAG.
**That sentence is load-bearing and v1 did not honour it**: v1 recorded only
`master_seed` out of the generator template, so editing `knn.sample.num` changed
every realization while firing no rerun-trigger anywhere. The template's content
digest now sits in `member_hash` (§5.1), which closes the gap at the same layer
as the rest of the freshness boundary rather than by exception.

### 2.5 Delegated implementation ownership

This design is normative; it authors no code. Each migration step (§13) is handed
to its owner as a scoped brief, with the gate it must pass named. A stage whose
validation handoff has not returned is not integrated.

| Work | Owner role | Gate it must pass |
|---|---|---|
| `build_members_manifest.py`, `run_sweep.py`, `sweep_slot.py`, `scripts/sweep_status.py`, `dev/scripts/prune_experiment_orphans.py`, the Snakefile rewrite | `python-engineer` | §13 step-level falsifiers; `pytest tests/test_cli.py` |
| **`downscale_climate_forcing.py` entry-point extraction** — `run_downscale(cst_nc, catalog, toml_out, forcing_out, log_path, **params) -> None`, a pure callable with no module-level `snakemake` read and no top-level side effects; the existing `script:` entry becomes a guarded `if __name__ == "__main__": if "snakemake" in globals():` shim over it (the shape R5 already applied to `prepare_weagen_config.py`) | `python-engineer` | §13 step 4a: tolerance-0 identity of the WG-6 forcing and HM-4 TOML, extraction commit alone, before any sweep code |
| **`prepare_climate_data_catalog.py`** — entry list derived from the manifest grid instead of `sm.input.cst_nc` / `sm.input.rlz_nc` (`:132-133`); a **script** change, not only an `input:` change | `python-engineer` | `validate_wg5_catalog_grid` unchanged |
| **`export_wflow_results.py` rewrite** — ledger-driven CSV list, `exp_dir` path rejoin, digest verification, completeness-aware framing under `aggregate_rlz`, `response_long.csv` | `python-engineer` | C-10, C-11, GF-7 |
| **`prepare_weagen_config.py`** — the generate-branch keys (`realizations_num: 1`, `rlz.index`, `work.path`, per-realization `seed` override) | `python-engineer` | `validate_wg3` extended |
| **Test migration** — `tests/test_guard_invalidation.py` (sentinel target), `tests/test_climate_store_contract.py:339-347` (guard `output:` shape), `tests/test_check_baseline_scope.py:86-95,147,180` (cardinality 3→4, 14→15), `tests/test_workflow_climate_experiment.py:9,28` (docstring job counts), and the fate of `dev/scripts/estimate_batch_makespan.py` + `tests/test_estimate_batch_makespan.py` | `python-engineer` | `pytest tests/` green at §13 step 7 |
| `wflow_worker.jl` (the line protocol and per-member log redirection, §6.2) | `python-engineer` (Julia surface is ~40 lines, seeded by `run_wflow_batch.jl`) | C-6, GF-1, GF-14, GF-20 |
| `generate_weather.R` changes (§4.2, incl. the checked `publish_file` replacement semantics), `impose_climate_change.R`'s `verbose = TRUE` (§9.1) | `r-developer` | C-16, C-27/GF-24 (checked sidecar publication), the perturb identity leg |
| Fixture sweeps, the `retain_member_artifacts` capture, the performance-floor run | `model-builder` | §13 steps 7–8 |
| Every parity/characterization verdict — generation distributional equivalence, HM-7 byte stability, the seam validator suite, the manifest re-record decision | `model-validator` | §9.6's per-stage table; C-7, C-10, C-11, C-15, C-16 |
| `response_long.csv` schema fitness for the response-surface consumer | `stress-test-analyst` | C-11 |

### 2.6 What this design deliberately does not decide

Nothing is left open for G1 — every item v1 flagged was ruled (see the header).
What remains genuinely undecided, and is *not* this milestone's to decide:

- **Whether the `precip_variance` axis should be activated at all.** OQ-1 is
  deferred entirely; the axis ships inert and loudly documented (§9.1). The
  activation decision, its full re-baseline, and the schema consequences are the
  named followup **R9-F1** (§15.3).
- **Whether the `cst_0` asymmetry in the reduction is desirable.** §4.4
  reproduces it exactly because the long table is a view; changing it is a
  separate scientific call.
- **A production-depth verdict on A4.** The fixture cannot reach it (§2.2);
  §15.3 names the trigger.

---

## 3. Architecture

### 3.1 The four stages

```
STAGE 1  PREPARE            STAGE 2  GENERATE        STAGE 3  SWEEP            STAGE 4  REDUCE
─────────────────────       ──────────────────       ────────────────────      ─────────────────
build_members_manifest ──┐  prepare_weagen_          climate_data_catalog ─┐   export_wflow_
  (guard + manifest)     ├─▶  config_rlz {r}  ──┐      (WG-5, unchanged)   ├──▶  results
copy_config              │  generate_weather_    ├──▶                      │     (Qstats, basin,
extract_climate_grid ────┤    realization {r} ───┘  run_sweep ─────────────┘      RT_*, long)
climate_stress_params ───┘    → rlz_<r>_cst_0.nc     ONE rule, p workers        gather_benchmarks
                              (NOT temp)             → _state/ledger_final.csv  gather_logs
```

- **Stage 1 Prepare** — config snapshot, the shared historical store, the WG-2
  perturbation grid, and the **members manifest**, which also carries the drift
  guard (§7.1). Everything here is cheap and deterministic from config.
- **Stage 2 Generate** — one job per realization, explicit per-realization seed,
  persistent baseline NC. Fans out over `RLZ_NUM`.
- **Stage 3 Sweep** — one Snakemake rule over the whole `RLZ × CST` member set,
  driven by manifest + ledger, executed by a Python orchestrator over `p`
  persistent Julia workers. Per member: perturb → downscale → simulate → verify →
  record → delete transients.
- **Stage 4 Reduce** — the response surface, read from the ledger rather than
  from an `expand()` over per-member CSVs.

### 3.2 The ownership split — what Snakemake keeps, what the runner takes

This is the whole trade, stated once (scoping intake § The stated tradeoff).

| Concern | v1 owner | v2 owner | Mechanism |
|---|---|---|---|
| Stage sequencing, config parse, `--configfile` contract | Snakemake | **Snakemake** | unchanged |
| Whether the sweep runs at all | Snakemake | **Snakemake** | `ledger_final.csv` missing, or a params/input change (§7.2, probe PR-2/PR-3) |
| Which *members* run | Snakemake (one job per member) | **Runner** | ledger fold vs manifest (§7.3) |
| Member-level incrementality after a crash | Snakemake | **Runner** | append-only ledger + digest verification (§5.2) |
| Transient deletion | Snakemake `temp()` | **Runner** | delete-after-use inside the member (§6.6) |
| Failure blast radius | Snakemake (per job / per batch) | **Runner** | per-member try/record; nothing sibling is deleted (§8) |
| `--dry-run` visibility of pending work | Snakemake | **Neither** — honestly | rule granularity only; a status command replaces it (§7.5) |
| Stale-output deletion | Snakemake | **Runner** | quarantine, not delete (§7.4) |
| Concurrency safety | Snakemake workdir lock | **Both** | plus an experiment-scoped lock (§6.6) |

**The single structural rule that makes this work** (probe PR-4, §11.2):
*Snakemake deletes the declared outputs of a failed job, and only those.* The
sweep rule therefore declares **exactly one** output — the finalized ledger,
written last — and every artifact whose survival a resume depends on
(`ledger.jsonl`, the per-member CSVs, the per-member TOMLs) is **undeclared**.
Declaring the per-member CSVs as sweep outputs would make the blast radius the
*entire sweep* — strictly worse than the batching it replaces. This inverts the
repo's R07 B6 correction (which made an undeclared *read* declared); the
justification is that these are undeclared *writes* whose declaration is
actively harmful, and §7.5 supplies the visibility that declaration would
otherwise have provided.

**The reduce's *reads* become undeclared too, and that is a constraint, not a
preference.** R07 B6 declared `st_csv_fns` precisely because an undeclared
runtime read is invisible to `--dry-run` (`Snakefile_climate_experiment:553-557`).
Under v2 the per-member CSVs have **no producing rule**, so declaring them as
inputs of 3.09 raises `MissingInputException` on every fresh run — declaration is
not available, not merely unattractive. What replaces it: `ledger_final.csv` *is*
declared and enumerates exactly those paths with their digests, and §4.4 verifies
each digest before reading (so an undeclared read is a *verified* read, which the
declared read never was). `st_csv_fns` stays declared; only the member CSVs move.

## 4. Stage specifications

Rule numbering follows the repo convention (`W.NN` = workflow.step in definition
order, a reference aid, not execution order — `dev/conventions/naming.md`). v2
renumbers because the rule set changes shape; §4.5 is the crosswalk.

### 4.1 Stage 1 — Prepare

**3.01 `build_members_manifest`** *(new; absorbs 3.00b `check_project_consistency`)*

| | |
|---|---|
| input | `ancient(wf1_snapshot_path)` (mandatory, unchanged from 3.00b) |
| params | `guarded_sections`, `guarded_sections_digest`, `wf1_snapshot_digest`, `wf2_snapshot_path`, `wf2_snapshot_digest` (all unchanged from 3.00b), plus `config_digest`, `stress_test` section, `grid` (`rlz_num`, `st_num`, `st_start`), `master_seed`, `weagen_template_digest`, `wflow_toml_digest`, `staticmaps_digest`, `policy` |
| output | `{exp_dir}/_state/members.json` |
| script | `blueearth_cst/experiment/build_members_manifest.py` |
| log/benchmark | `_parts/3.01_build_members_manifest.{log,tsv}` |

Behaviour: call `check_project_consistency.compare_project_consistency(live_cfg,
wf1_snapshot_path, wf2_snapshot_path)` **unchanged** — the pure comparator, its
guarded key set, and its failure messages are retained verbatim
(`blueearth_cst/experiment/check_project_consistency.py:142-184`). On divergence:
raise, write nothing. On pass: write the manifest atomically (§5.3).

`members.json` **replaces `.project_consistency_ok` as the sentinel**: it is the
fresh input of every downstream per-experiment rule, so a guarded-section change
flips `guarded_sections_digest`, re-runs the manifest rule, rewrites the
manifest, and re-runs everything downstream — the same rerun-trigger chain 3.00b
has today (`Snakefile_climate_experiment:143-163`), with one artifact instead of
two.

`{store_dir}/.guard_ok` **retires**. It has had no DAG consumer since R07
(`Snakefile_climate_experiment:296-301`) and no validator; keeping a
cross-experiment artifact alive purely as a receipt is unjustified once the
manifest records the same digests per experiment. *Migration note: existing
`.guard_ok` files are orphaned, not deleted, by this change.*

**Named test breakage this rule causes** (all four run on a bare checkout, so
each turns CI red at the step that lands the change — §13 step 1 owns them):
`tests/test_climate_store_contract.py:339-347` asserts the guard rule's outputs
are exactly `["guard_ok", "sentinel"]` and that the `guard_ok` path ends with
`/.guard_ok`; `tests/test_guard_invalidation.py:95-124` targets
`experiments/<exp>/.project_consistency_ok` by **path** and executes the rule for
its i–l and 2c–2h cases. The sentinel becomes `_state/members.json` and the
outputs become a single output, so both files need their *plumbing* assertions
rewritten. Their **contract** assertions — the guard's verdict and its message
for each case — must be preserved unchanged and are what C-15 now covers (§12).

**3.02 `copy_config`** — unchanged except `input.consistency_ok` →
`input.manifest = {exp_dir}/_state/members.json`.

**3.03 `extract_climate_grid`** — **unchanged**, splatted from
`climate_store_spec` (the one-producer contract with wf1 rule 1.10;
`tests/test_climate_store_contract.py` fails on any difference).

**3.04 `climate_stress_parameters`** — unchanged (WG-2 producer,
`prepare_cst_parameters.py`), except `consistency_ok` → `manifest`.

### 4.2 Stage 2 — Generate

**3.05 `prepare_weagen_config_rlz`** *(replaces 3.04 `prepare_weagen_config`; wildcard `{rlz_num}`)*

| | |
|---|---|
| input | `manifest = {exp_dir}/_state/members.json` |
| output | `{wg_dir}/_work/weathergen_config_rlz_{rlz_num}.yml` |
| params | `cftype="generate"`, `snake_config=config_path`, `default_config=config/templates/weathergen_config.yml`, `weagen_template_digest`, `output_path={wg_dir}/`, `work_path={wg_dir}/_work/rlz_{rlz_num}/`, `middle_year`, `sim_years`, `nc_file_prefix="rlz"`, `rlz_index={rlz_num}` |

`build_weagen_config`'s `generate` branch gains **two new keys** under
`generateWeatherSeries` — `rlz.index: <n>` and `work.path` — plus **two
overrides of existing keys**: `realizations_num: 1` (was `RLZ_NUM`) and `seed:
<seed_r>` read from the manifest. `seed` is *not* new: it is an already-pinned
WG-3 key (`dev/contracts/weather-generator-seam.md:141`), already read at
`generate_weather.R:57` and already present in the template — calling it "added"
would send `validate_wg3`'s extension after the wrong key set. Every other key is
unchanged (`prepare_weagen_config.py:54-68`).

`weather_generator/config/` **retires**: its only producer was the v1
`prepare_weagen_config` pair, and both per-realization and per-member configs
now live under `_work/` (the latter as a runner transient). The directory is
removed from the R07 layout map in §13 step 6; existing directories are orphaned,
not deleted.

*The retired sibling:* **3.05 `prepare_weagen_config_st`** (the per-`(rlz, cst)`
config, `Snakefile_climate_experiment:359-376`) has no successor rule — the
member's perturbation config becomes a runner-written transient (§6.6, WG-3
delta in §10).

**3.06 `generate_weather_realization`** *(wildcard `{rlz_num}`)*

| | |
|---|---|
| input | `climate_nc = ancient({store_dir}/extract_historical.nc)`, `weagen_config = {wg_dir}/_work/weathergen_config_rlz_{rlz_num}.yml` |
| output | `{wg_dir}/output/rlz_{rlz_num}_cst_0.nc` — **not `temp()`** |
| shell | `run_logged … Rscript --vanilla blueearth_cst/weathergen/generate_weather.R {input.climate_nc} {input.weagen_config}` |
| wildcard_constraints | `rlz_num=r"\d+"` |

Three changes to `generate_weather.R`, all on our side of the seam:

1. **The realization index is read from the config, not from the loop counter.**
   Today the loop `for (n in 1:historical_realizations_num)` supplies both the
   RNG stream position and the file suffix (`generate_weather.R:76-102`). With
   `n_realizations = 1` the loop counter is always 1, so the suffix must come
   from `generateWeatherSeries$rlz.index`. `file_suffix <- paste0(rlz_index, "_cst_0")`.
2. **The `spatial_ref` workaround block's glob uses `rlz_index`** — the pattern
   `paste0("_", n, "_cst_0\\.nc$")` (`:117`) becomes `paste0("_", rlz_index,
   "_cst_0\\.nc$")`. The block itself stays until the upstream fix lands
   (`AGENTS.md` Hard Constraints; `dev/followups.md` § R5).
3. **The generator's scratch `out_dir` splits from the published output dir,
   without moving the published artifacts.**
   `weathergenr::generate_weather(out_dir = …)` writes `sim_dates.csv`,
   `resampled_dates.csv` and four diagnostic PNGs; `weathergenr::write_netcdf(out_dir = …)`
   writes the realization NC. They are already independent arguments
   (`generate_weather.R:56` vs `:90`). With `RLZ_NUM` concurrent jobs a shared
   `out_dir` is a write race on the two date CSVs — the problem this change
   exists to solve. Resolution, in two moves:

   - `generate_weather(out_dir = work.path)` — the per-realization
     `_work/rlz_<n>/`, so the concurrent writes cannot collide;
   - **our wrapper then publishes** the two CSVs to their R07 home under
     realization-suffixed names: `weather_generator/output/sim_dates_rlz_<n>.csv`
     and `weather_generator/output/resampled_dates_rlz_<n>.csv`. Figures publish
     to `plots/rlz_<n>/`.

   *Why the publish step and not a plain relocation.* R07 **ruled** on these two
   paths — `dev/r07/migration_project-layout.md:194-195`: "exact — **`output/`,
   not `_work/`** (ruled: products of the generator)". Leaving them in `_work/`
   would reverse a recorded ruling, hide `resampled_dates.csv` (the record of
   which historical days each realization resampled) behind a prefix that reads
   as scratch, and make both files show as `missing`/`extra` in a whole-tree
   diff. The publish is on our side of the seam (in `generate_weather.R`, no
   upstream change); the file names change because the flat names cannot carry
   a realization index. §10 carries a row for each, and §13 step 6 updates
   `dev/scripts/semantic_tree_diff.py:357-360`'s exact-file path-map rule and
   its assertion at `tests/test_semantic_tree_diff.py:621-622` **in the same
   commit**.

   **Publication is checked replacement, never a bare `file.rename` — and the
   pre-existing figures block comes under the same rule.** The destinations
   exist on every regeneration, and on Windows `file.rename` onto an existing
   destination fails; unchecked, the baseline NC would reflect the new seed
   while `sim_dates_rlz_<n>.csv` / `resampled_dates_rlz_<n>.csv` silently kept
   the previous generation's content — a torn published state in the artifact
   that records which historical days were resampled. Normative mechanism: one
   helper in `generate_weather.R`, `publish_file(src, dest)`, used for **every**
   published sidecar:

   1. if `dest` exists, `file.remove(dest)`; on `FALSE`, `stop()` with a named
      message (`"[generate_weather] publish failed: cannot remove <dest>"`,
      naming the likely holder — "close any process reading the file"), the
      R-side analogue of §5.3's `AtomicReplaceError`;
   2. `file.rename(src, dest)`; on `FALSE`, the same named `stop()` citing
      `src` and `dest`.

   Base R has no `os.replace` equivalent and the zero-new-dependency rule
   (§2.3) forecloses one, so the remove+rename pair is not atomic — but every
   step is **checked**, which is the accepted branch: the failure mode changes
   from a *silent stale sidecar* to a loud named error. A crash between the two
   steps leaves the destination absent and the source still in `_work/`; the
   nonzero `Rscript` exit fails the rule, Snakemake deletes the declared NC
   output (PR-4), and the re-run regenerates everything — no half-published
   state survives into a consuming run. **The figures block at
   `generate_weather.R:68-73`** — today an unchecked `file.rename` loop over
   the four diagnostic PNGs — is rewritten onto the same helper with
   destination `plots/rlz_<n>/<fig>`; a *missing source* figure remains a
   legitimate state (each upstream `ggsave` sits in its own `tryCatch`, so the
   helper is invoked only when the source exists), while a *failed publish* of
   an existing source becomes loud. Gate: GF-24 (second generation with changed
   seeds on Windows replaces every sidecar consistently); claim: C-27.

   *Contract note:* the two date CSVs are explicitly **non-interchange**
   (weather-generator seam § Considered and excluded) — but they are named there
   at their current path, so the exclusion note is amended with the new names.

**Seed derivation (OQ-5, §9.5).**
`seed_r = int.from_bytes(sha256(f"{master_seed}:rlz:{r}".encode("utf-8")).digest()[:4], "big") % (2**31 - 1)`
computed by the manifest builder and recorded per realization.

**`master_seed` gets a home in the sectioned config.**
`workflows.climate_experiment.master_seed`, optional on the `get_config`
contract, defaulting to `generateWeatherSeries.seed` in
`config/templates/weathergen_config.yml:17`. v1 took it from the template alone,
which made §7.6's "user-facing invalidation lever" a *tracked-repo* edit shared
by every project on the checkout — two projects could not differ, and re-seeding
a stress test would dirty the toolbox source. The manifest records the effective
value and its provenance (`config` | `template_default`). The experiment name is
**excluded** from the derivation so the same `master_seed` reproduces the same
realizations in any experiment or project — reproducibility over per-experiment
independence (§14.9 records the rejected alternative).

### 4.3 Stage 3 — Sweep

**3.07 `climate_data_catalog`** *(was 3.08; WG-5 producer)*

| | |
|---|---|
| input | `manifest`, `rlz_nc = [{wg_dir}/output/rlz_<r>_cst_0.nc for r in 1..RLZ_NUM]` |
| output | `{exp_dir}/data_catalog_climate_experiment.yml` |
| params | `data_sources`, `clim_source`, `oro_path` (unchanged) |

**The catalog's content is unchanged** — one entry per `rlz_<n>_cst_<m>` for
`n ∈ 1..RLZ_NUM`, `m ∈ 0..ST_NUM`, exactly the grid
`validate_wg5_catalog_grid` checks. Only the rule's **input set** changes: the
perturbed NCs no longer exist as DAG nodes, so the entry list is derived from the
manifest's grid instead of from an `expand()` over files
(`Snakefile_climate_experiment:422-423`). hydromt resolves only the entry it is
asked for (`precip_fn=climate_name`, `downscale_climate_forcing.py:105`), so
entries whose file is not currently on disk are inert.

**3.08 `run_sweep`** *(replaces 3.05, 3.07, 3.09 and the `run_wflow_batch_<b>` family)*

| | |
|---|---|
| input | `manifest`, `catalog`, `rlz_nc` (all baselines), `st_csv_fns` (all WG-2 files), `data_sources` |
| output | `ledger_final = {exp_dir}/_state/ledger_final.csv` — **exactly one**, per §3.2 |
| params | `exp_dir`, `runs_dir`, `wg_dir`, `model_dir`, `clim_source`, `horizontime_climate`, `run_length`, `staticmaps_digest`, `wflow_toml_digest`, `incomplete_digest`, plus the resolved runtime overrides (`sweep_workers`, `wflow_threads`, `member_max_attempts`, `worker_max_members`, `allow_partial`, `retain_member_artifacts`, `sweep_quarantine`), and `config_path` |
| threads | `_cores` (the **existing guarded binding**, see below) |
| log/benchmark | `_parts/3.08_run_sweep/_orchestrator.log`; `_parts/3.08_run_sweep.tsv` |
| shell | `python -u "{run_logged}" "{log}" -- python -m blueearth_cst.experiment.run_sweep --manifest … --config-path … --exp-dir … <resolved overrides>` |

**`threads:` must not be `workflow.cores`.** `workflow.cores` **raises** when
cores are unset (`snakemake/workflow.py:583-593`; the default local executor
leaves `args.cores = None`, `cli.py:1942-1948`), and rule directives evaluate at
**parse** time — so a bare `snakemake --unlock -s Snakefile_climate_experiment
--configfile …`, the exact command `AGENTS.md` § Key Commands documents and the
exact command F5/GF-2 depend on after a crash, would fail on wf3. So would any
`--dry-run` without `-c`. The Snakefile already carries the guard
(`Snakefile_climate_experiment:486-489`, `int(workflow.cores) if workflow.cores
else 1`); v2 reuses that `_cores` binding, and the sweep's parallelism **degrades
to 1** rather than raising when cores are unset.

**No `staticmaps` DAG edge.** v1 declared `staticmaps = ancient({basin_dir}/staticmaps.nc)`.
`ancient()` suppresses the mtime trigger, not the *existence requirement*, and no
wf3 rule produces `staticmaps.nc`; `tests/test_cli.py`'s `config_with_staged_region`
fixture stages only `staticgeoms/region.geojson` and the wf1 config snapshot
(`:64-70`), while `test_snakefile_cli_climate_experiment` (`:214-230`) asserts
`returncode == 0` on it. The edge would raise `MissingInputException` and turn
**both CI legs red**. It is dropped: the freshness signal is carried by
`staticmaps_digest` as a `params:` value (§5.1), which is the mechanism that
actually re-triggers, and the DAG edge added nothing it does not.

**Runtime overrides are resolved in the Snakefile, not in the runner.** Five
keys must be settable per-invocation for the documented capture procedure (§10a),
the `allow_partial` gate (GF-7), the corrupt-ledger recovery (§5.3), and C-7's
paired identity legs (§9.6): `retain_member_artifacts`, `allow_partial`,
`sweep_quarantine`, `sweep_workers`, `worker_max_members`. Snakemake's
`--config k=v` writes `config["k"]` at the **top level**, which
`get_config(my_cfg, …)` — `my_cfg = config["workflows"]["climate_experiment"]`
(`Snakefile_climate_experiment:30`) — never sees, so v1's three commands were
inoperative and would have reported a false green. v2 adds one helper,
`get_override(config, my_cfg, key, default)`, with a **stated precedence: a
top-level `--config` value wins over the section value, which wins over the
default**; it is pinned by a unit test in §13 step 4. The Snakefile resolves the
override *and passes the resolved value on the runner's command line* — the
orchestrator re-reads `config_path` from disk for everything else and therefore
could never see an in-memory `--config` value on its own. The argument list is
deliberately short and fixed; the rest of the run parameters reach the runner
through `members.json`, on the repo's `config_path`-forwarding convention.

**Why `shell:` and not `script:`.** Snakemake does not import a `script:` module:
it writes preamble+source to a generated temp file under `.snakemake/scripts/`
and runs *that* as a subprocess (`snakemake/script/__init__.py:634-645`), with
the preamble rebinding `__file__` (`:778-786`). `multiprocessing`'s `spawn` start
method records `sys.modules['__main__'].__file__` and each child calls
`_fixup_main_from_path`, so **every slot would re-execute the orchestrator module
top level** under `__mp_main__` — paying its imports `p` times (directly against
§6.1's cost model) and making correctness depend on a guard the sibling module in
the same package does not use. A `shell:` rule through `run_logged.py` — exactly
what `Snakefile_climate_experiment:546` already does for a long-lived Julia child
— sidesteps `__main__` entirely and gives the orchestrator log the same
header/relativization/UTF-8/exit-code handling every other tee'd rule gets
(`:21-25`). Two invariants ride with it and are normative:

1. `run_sweep.py` has **no module-level side effects** and a guarded
   `if __name__ == "__main__":` entry; its imports are standard-library only.
2. The **slot body lives in a separate importable module**,
   `blueearth_cst/experiment/sweep_slot.py`, which is what the spawned children
   import — so the hydromt import happens once per slot, deliberately, rather
   than once per orchestrator re-execution, accidentally. Import-cheapness also
   lets §13 step 4's Julia-free unit tests avoid `sys.modules.setdefault` stubs
   and the collection-order pollution recorded in `dev/followups.md` § R3+.

**Undeclared, runner-owned, deliberately invisible to the DAG:**
`_state/ledger.jsonl`, `_state/sweep_completeness.csv`, `_state/sweep_summary.json`,
`_state/sweep_incomplete.json`, `_state/experiment.lock`, `_state/quarantine/`,
`_state/members/<member_id>/`,
`{runs_dir}/rlz_<n>/config/cst_<m>.toml` (HM-4, persistent),
`{runs_dir}/rlz_<n>/output/cst_<m>.csv` (HM-5, persistent), and the transients
(§6.6). §3.2 states why; §7.5 states what replaces the lost visibility.

Full runner specification: §6.

### 4.4 Stage 4 — Reduce

**3.09 `export_wflow_results`**

| | |
|---|---|
| input | `ledger_final = {exp_dir}/_state/ledger_final.csv`, `st_csv_fns` (unchanged); `_state/sweep_completeness.csv` read at runtime, existence transitive (§5) |
| output | `Qstats`, `basin` (unchanged) **+ `response_long = {indicators_dir}/response_long.csv`**; `RT_<var>.csv` and (conditionally) `completeness.csv` remain **undeclared** |
| params | `indicators_dir`, `exp_dir`, `aggr_rlz`, `st_num`, `Tlow`, `Tpeak` |

The `expand()` over per-member CSVs
(`Snakefile_climate_experiment:552`) is replaced by the ledger: `ledger_final.csv`
lists exactly the members of the current manifest that succeeded, each with its
CSV path, coordinates and content digest.

**Four changes to the reduce's plumbing, none to its statistics.** v1 claimed the
body was untouched; three of these say otherwise, and saying so is the point —
`analyze_wflow_results` is now specified work with an owner (§2.5), not an
assertion of stability.

1. **Paths are rejoined against `exp_dir`.** §5.1 fixes all recorded artifact
   paths as *relative to `exp_dir`*; `analyze_wflow_results` opens them directly
   (`export_wflow_results.py:95,157,165`) with the process CWD at the repo root.
   `endswith` matching (`:162`) and `realization_from_run_csv` (`:24`) both
   survive relativization; the `open` does not. The caller resolves each
   `ledger_final.result` against `exp_dir` before handing the list over — one
   line, on the milestone's central new data path.
2. **Digests are verified before reading — whenever the reduce runs.** For each
   row, recompute `sha256` of the CSV and hard-fail naming the diverged
   `member_id` on mismatch. The design pays for the digest at record time; this
   is where it is spent. **The honest scope of the check, stated because v2
   overclaimed it:** after a *clean* sweep, an ordinary re-invocation runs
   neither the sweep (declared output present, params unchanged — §7.2) nor the
   reduce (its declared inputs and outputs are all present and fresh), so
   *nothing* executes and post-completion corruption of an undeclared member CSV
   goes unobserved on that command. This check therefore fires on every path
   where the reduce actually executes — a partial-sweep retry (§7.2), any
   manifest-driven re-entry, a `--forcerun`, or a rebuilt `ledger_final.csv` —
   and refuses to publish a surface derived from a diverged CSV. **On-demand
   integrity is a separate, explicit command:** `scripts/sweep_status.py
   <exp_dir> --verify` (§7.5), which recomputes every digest `ledger_final.csv`
   records and exits nonzero naming each diverged member. The repair lever, which
   the `--verify` failure message prints: delete
   `{exp_dir}/_state/ledger_final.csv` and re-invoke — the sweep re-enters (its
   declared output is absent), reuse condition 4 fails for exactly the diverged
   member(s), and they quarantine and re-run (§5.5). GF-15 exercises all of this;
   the priced-and-rejected alternative (live digests in the reduce's parse-time
   freshness) is §14.14.
3. **Frames are sized from the succeeded set, not from `st_num`** — see the
   `allow_partial` specification below.
4. **`response_long.csv` is emitted** as a lossless pivot of the two wide tables.

**HM-7 stays byte-stable under full completeness.** Every statistic path is
unchanged: the `Q_`-prefix gauge selection (`export_wflow_results.py:96`), the
`basavg` substring selection (`:97`), the `aggr_rlz` concatenation order, the
per-statistic rounding, and the `tavg`/`prcp` derivation
(`tavg = df_st["temp_mean"].iloc[0]`, `prcp = df_st["precip_mean"].iloc[0]*100-100`,
`:196-198`). The ledger emits the CSV list in the same order the `expand()`
produced (realization-major, cst-minor) so the aggregation index arithmetic
(`:162`) is untouched. C-10 pins this and remains a **full-grid** byte-identity
check; the `allow_partial` path gets its own falsifier (C-17), never C-10.

**`allow_partial` under `aggregate_rlz` — the shape a hole actually takes.**
Under the fixture's `aggregate_rlz: true` the v1 body **cannot express** the
"grid with holes" §9.4 described, in either sub-case: `df_out_mean` /
`df_out_basavg` are pre-allocated `np.zeros((st_num, …))`
(`export_wflow_results.py:103-107,137-141`) and the loop runs `range(st_num)`
regardless of what is on disk (`:153`), selecting
`csv_fns_i = [x for x in csv_fns if x.endswith(f"cst_{i+1}.csv")]` (`:161-162`).
So a *partially* missing `cst_m` (some realizations absent) yields a **fully
populated row silently averaged over fewer realization-years** — indistinguishable
from a complete cell — and a *wholly* missing `cst_m` yields `pd.concat([])` →
`ValueError: No objects to concatenate`, or, absent the raise, a zero row that
reports `0.0` indicators for an unrun cell. All three shapes are real; all three
are the distortion the fail-loud default exists to prevent, reachable through the
escape hatch that same ruling approves.

Specification, replacing them:

| | Rule |
|---|---|
| Cell completeness | Under `aggregate_rlz: true`, a `cst_m` is **complete** iff all `RLZ_NUM` of its members are `succeeded`. Under `aggregate_rlz: false`, completeness is per member |
| Incomplete cell | **Dropped entirely** — the row is absent from `Qstats.csv`, `basin.csv`, `RT_*.csv` and `response_long.csv`. Frames are sized from the *complete* set, never from `st_num` |
| Record | `indicators/completeness.csv` names every dropped cell with `cst`, `state=partial_cell` \| `missing_cell`, `n_expected`, `n_present`, and the member ids that are missing; every **retained** cell carries its `n` so a consumer can join per-cell realization counts to the surface |
| Empty group | A `cst_m` selected with zero CSVs raises a **named** `IncompleteCellError` naming the cell, never a bare pandas `ValueError` |
| Fail-loud default | Unreachable: the reduce's declared input is absent, so it never runs. `completeness.csv` is **not** written |
| Full-completeness cleanup | A reduction that runs at **full completeness deletes any prior `indicators/completeness.csv`** (`Path.unlink(missing_ok=True)` — a single atomic remove) immediately before publishing its surfaces. Without it, the designed partial→retry→complete sequence (§7.2, GF-13) would leave a stale record from an earlier invocation beside complete surfaces — mutually inconsistent scientific products, and a contaminant in tree comparisons that claim the file absent on every clean run. GF-13's final observation asserts the absence; C-17's falsifier covers survival |
| Ordering | The retained cells keep their `cst` order, so a partial surface is a subset of the full one, never a re-indexed one |

Dropping rather than zero-filling or under-averaging is what makes "the missing
`(tavg, prcp)` rows simply absent" true rather than aspirational, and it is the
only shape a consumer can detect without a join. §9.6's Reduce parity class
therefore reads **"Identical *under full completeness*"**.

**The gauge-column reliance is preserved deliberately.** HM-5 → HM-7 keeps its
single degree of freedom and the hard-coded `Q_` prefix; changing it is out of
scope and would break `validate_hm_gauge_column_identity`.

**`response_long.csv` — the tidy long format.**

| column | type | semantics |
|---|---|---|
| `member_id` | str | `rlz_<n>/cst_<m>`; `"agg/cst_<m>"` when `aggregate_rlz: true` |
| `rlz` | int \| `"all"` | realization index, `"all"` under aggregation |
| `cst` | int | stress-test index. `cst_0` rows exist **iff `aggregate_rlz: false`** — see the asymmetry note below |
| `tavg` | float | additive °C, exactly as `Qstats.csv` |
| `prcp` | float | precipitation change in %, exactly as `Qstats.csv` |
| `precip_variance` | float \| empty | the WG-2 variance factor (empty for `cst_0`). **INERT this milestone** — see the note below and §9.1 |
| `family` | str | `discharge` \| `basin_average` |
| `statistic` | str | `mean`, `max`, `min`, `q95`, `returninterval`, `Q7day_max`, `wetmonth_mean`, `returninternval_min_7day`, `Q7day_min`, `drymonth_mean`, `BaseFlowIndex` (discharge); `annual_max` \| `annual_sum` (basin average) |
| `column` | str | the HM-5 column name (`Q_130000086`, `snow_basavg`) |
| `value` | float | the value, **identically rounded** to its wide-table cell |

Example rows:

```csv
member_id,rlz,cst,tavg,prcp,precip_variance,family,statistic,column,value
agg/cst_1,all,1,0.0,-30.0,1.0,discharge,mean,Q_130000086,4.21
agg/cst_1,all,1,0.0,-30.0,1.0,basin_average,annual_sum,actual_evapotranspiration_basavg,612.4
```

**`precip_variance` is published inert, and says so where it is consumed.** The
column is a *coordinate* of the response surface beside `tavg` and `prcp`, but
under the G1 deferral varying it changes nothing: the installed weathergenr
scales variance with the mean and ignores `precip_var_factor` (§9.1, P6
MEASURED). An analyst reading `response_long.csv` must not have to know that.
Three annotations carry it, all landing in §13 step 6:

- the **column note in this document's schema table above** (`INERT this
  milestone`), which `dev/workflows/climate_experiment.md` reproduces verbatim
  when it is rewritten, plus the same statement in `docs/migration-r09-wf3.md`
  under a § OQ-1 heading that §9.1 points at. *An in-file `#` comment line was
  considered and **rejected**: `check_baseline.py:319` compares CSV targets with
  a bare `pd.read_csv(path)` and no `comment=` argument, so a leading `#` line
  would be parsed as the header row and the normalized-CSV sha would pin a
  malformed table — and `response_long.csv` joins the manifest at §13 step 9.
  The same hazard applies to any downstream `pd.read_csv`;*
- the same statement in the WG-2 row of the weather-generator seam doc;
- a **warning at manifest-build time** when
  `stress_test.precip.variance.min != variance.max`, naming the inertness and
  followup **R9-F1**, because that is the only config shape whose author
  plainly expects the axis to do something.

The column stays in the schema — retention is what makes later activation cheap
(G1) — and it enters the baseline manifest at §13 step 9 carrying this note, so
the eventual activation re-baselines an artifact that was pinned *honestly*
rather than silently.

**The `cst_0` asymmetry, inherited verbatim from the existing reduction.** Under
`aggregate_rlz: true` the loop runs `st_num` times with `st_nb = i + 1`
(`export_wflow_results.py:153,161-162`), so the baseline CSVs are in `csv_fns`
but **no `cst_0` row is ever emitted**. Under `aggregate_rlz: false` the loop
runs `len(csv_fns)` times and the `st_nb == "0"` branch (`:192-194`) emits
`cst_0` with `tavg = 0, prcp = 0`. The long table reproduces this asymmetry
exactly — it is a view, and a view that "fixed" the asymmetry would stop being a
lossless pivot and would silently disagree with `Qstats.csv`. Whether the
asymmetry is *desirable* is a separate question, out of scope for this
milestone; it is recorded here so C-11 is written against the real behaviour.
*(On the tracked fixture `ST_START = 1`, so there are no `cst_0` members and the
asymmetry cannot be exercised there — it needs a `run_historical: true`
variant. GF-21's **untracked scratch config variant** (§8.2) is exactly that,
created to exercise the baseline member lifecycle (§6.6); its `aggregate_rlz:
true` run also observes this asymmetry as specified — baseline CSVs consumed,
no `cst_0` row emitted. The tracked fixture itself is not changed.)*

**The long table is a lossless pivot, and that is its acceptance test**
(§12, C-11): re-pivoting `response_long.csv` must reproduce `Qstats.csv` and
`basin.csv`. It is a *view*, never an independent computation — a second
computation path would be a second source of truth for the response surface.
**The comparison is parsed-value equality at the declared rounding, not byte
equality of cells.** `Qstats.csv` is not a float table: its frames are created
`dtype="str"` and filled by
`np.concatenate([["mean"], cst_stat, df.values.round(2)])`
(`export_wflow_results.py:103-119,205-239`), so every cell is numpy's
*stringification* of a rounded float. A float-typed long table round-tripped
through pandas agrees in the common case and diverges on formatting edge cases
(trailing zeros, exponent forms) — a "cell-for-cell" byte check would fire as a
false regression on formatting. C-11 therefore compares `float(cell)` at the
declared rounding; the string formatting itself is **not** claimed as contract.

**RT_\*.csv keep their current disposition: undeclared, unchanged, ungated by
the manifest.** `analyze_wflow_results` writes one `RT_<var>.csv` per discharge
variable into `indicators_dir` (`export_wflow_results.py:300-315`) as undeclared
outputs. v2 changes only their *inputs* (the same member CSVs, obtained from the
ledger), so they are covered by C-10's direct diff alongside the two wide tables,
and they follow the same cell-drop rule under `allow_partial`. They do **not**
join the baseline manifest — the wf3 slice grows by exactly one target
(`response_long.csv`, §13 step 9).

**`WF3_TARGETS` gains `response_long.csv`.** Rule `all`'s target set
(`Snakefile_climate_experiment:222-228`) is the user-visible half of the entry
contract G8 promises to keep, so an added product belongs in it; adding a target
is additive and breaks no invocation. `RT_*.csv` and `completeness.csv` stay out
(undeclared and conditional respectively).

**3.10 `gather_benchmarks`, 3.11 `gather_logs`** — unchanged scripts; `LOG_RULES`
becomes the v2 label list. Both keep the final indicators as `input:`, which is
what schedules them last.

### 4.5 Rule-inventory delta

| v1 rule | v2 disposition |
|---|---|
| 3.00b `check_project_consistency` | **absorbed** into 3.01 `build_members_manifest`; comparator retained verbatim; `.guard_ok` retires |
| 3.01 `copy_config` | kept; sentinel input becomes the manifest |
| 3.02 `extract_climate_grid` | **unchanged** (shared producer) |
| 3.03 `climate_stress_parameters` | kept (WG-2); sentinel input becomes the manifest |
| 3.04 `prepare_weagen_config` | → 3.05 `prepare_weagen_config_rlz`, now per-realization |
| 3.05 `prepare_weagen_config_st` | **retired**; becomes a runner-written member spec |
| 3.06 `generate_weather_realization` (all realizations, `temp()`) | → 3.06, one job per realization, output persistent |
| 3.07 `generate_climate_stress_test` | **retired as a rule**; the same `Rscript` invocation moves inside the member (§6.6) |
| 3.08 `climate_data_catalog` | → 3.07; content unchanged, input set changes |
| 3.09 `downscale_climate_realization` | **retired as a rule**; the same script body runs inside the member |
| 3.10 `run_wflow_batch_<b>` (K/B anonymous rules) | **retired**; replaced by 3.08 `run_sweep` |
| 3.11 `export_wflow_results` | → 3.09; ledger-driven; gains `response_long.csv` |
| 3.12 `gather_benchmarks` | → 3.10 |
| 3.13 `gather_logs` | → 3.11 |

**Job-count consequence at fixture scale** (`RLZ_NUM=2`, `ST_NUM=6`,
`run_historical: false` ⇒ `ST_START=1` ⇒ **`K=12` members**): v1 runs 49 jobs at
`B=4` and 58 at `B=1` (P3-3 headline, both measured at this same `K=12`); v2 runs
**13 jobs** — `1+1+1+1` prepare, `2+2` generate, `1+1` sweep, `1+1+1` reduce.
The v2 count is independent of `K` by construction: the member count leaves the
DAG entirely, which is the whole point. `tests/test_workflow_climate_experiment.py:9,28`
pins the v1 numbers ("12 Wflow runs", "56 jobs under `--forceall`") in its
docstring and needs updating at §13 step 6 — it is integration-gated, so neither
CI nor §13 step 7's `pytest tests/` would catch the drift.

**Config keys added** (all optional, `get_config` contract — raise on missing
required, return the default for optional):

| key | default | meaning |
|---|---|---|
| `workflows.climate_experiment.sweep_workers` | `_cores` (= `-c N`, degrading to 1) | `p`, the number of persistent Julia workers; `--config` overridable (§9.6 C-7) |
| `workflows.climate_experiment.wflow_threads` | `4` | `M`, `--threads` per worker (today's frozen value) |
| `workflows.climate_experiment.member_max_attempts` | `2` | attempts per member **within one invocation** (§5.4) |
| `workflows.climate_experiment.worker_max_members` | `0` (= unbounded) | recycle a Julia worker after N members (§6.3); `--config` overridable (§9.6 C-7) |
| `workflows.climate_experiment.master_seed` | the template's `generateWeatherSeries.seed` | the generation seed root (§4.2) |
| `workflows.climate_experiment.allow_partial` | `false` | OQ-4 posture (§9.4); `--config` overridable |
| `workflows.climate_experiment.retain_member_artifacts` | `false` | keep per-member transients on disk (replaces `--notemp`, §10); `--config` overridable |
| *(no section home)* `sweep_quarantine` | `0` | top-level `--config` only: the corrupt-ledger recovery (§5.3) |

**Config keys retired:** `batch_size`, `batch_size_max`
(`Snakefile_climate_experiment:501-519`). A config still carrying them is
**rejected with a named migration message**, not silently ignored — silence
would let a user believe they were still tuning the sweep.

**Rejection needs a mechanism, because the repo has none.** `get_config`
(`blueearth_cst/shared/snake_utils.py:122-154`) has only present / optional /
required semantics; no code anywhere in this repository rejects a retired key,
including the R01 sectioned-schema migration, and the sole parse-time key
validator is the local `_positive_batch_key`
(`Snakefile_climate_experiment:501-508`). Without a stated mechanism the intended
behaviour lands as a silent ignore — the exact failure the rule exists to
prevent. Specification: a small **parse-time** helper in the Snakefile,
`_reject_retired_keys(my_cfg, {"batch_size": <msg>, "batch_size_max": <msg>})`,
mirroring `_positive_batch_key`'s shape (raise naming the offending key and the
migration), pinned by a unit test in §13 step 5. **Stated consequence:** a
parse-time raise also blocks `--unlock` and `--dry-run` until the config is
edited. That is accepted — a config carrying a retired sweep-tuning key is a
config whose author's mental model is wrong, and the edit is one line — but it is
a *choice*, not an accident, and the message says exactly which line to delete.

## 5. Members manifest and per-member ledger

Two records, joined by `member_id`, mirroring `cst-run-control`'s immutable-intent
/ mutable-state split (§5.5):

| Record | Path | Mutability | Declared to Snakemake? |
|---|---|---|---|
| Members manifest | `{exp_dir}/_state/members.json` | Written once per manifest rule execution; immutable for the life of a sweep | **Yes** (output of 3.01, input of 3.05–3.08) |
| Ledger | `{exp_dir}/_state/ledger.jsonl` | Append-only during a sweep | **No** — must survive a failed job (§3.2) |
| Finalized ledger | `{exp_dir}/_state/ledger_final.csv` | Written once, atomically, at **accepted** sweep termination | **Yes** — the sole declared output; input of 3.09 |
| Completeness record | `{exp_dir}/_state/sweep_completeness.csv` | Written atomically on **every** terminal path, accepted or not | **No** — see the note below |
| Summary sidecar | `{exp_dir}/_state/sweep_summary.json` | Written with the completeness record | **No** — carries the aggregate counts and the run identity that a CSV row population cannot |
| Incompleteness marker | `{exp_dir}/_state/sweep_incomplete.json` | Written on an **accepted-but-incomplete** termination; **deleted** on a complete one | **No**, but its digest is a `params:` value of 3.08 (§7.2) |

**Why the completeness record is undeclared.** It exists precisely to name which
member failed, and PR-4 establishes that Snakemake removes a failed job's
declared outputs. A declared completeness record would therefore be deleted on
exactly the path it exists to document. It is undeclared, written on every
terminal path, and survives. The reduce reaches it as a runtime read whose
existence is guaranteed **transitively** through its declared `ledger_final.csv`
edge — the same "pinned transitively" pattern HM-6a already uses on this seam.

`_state/` is a new directory under the experiment root. It is runner state, not a
product: nothing in `indicators/` derives its *format* from it.

### 5.1 Manifest schema — `members.json`

JSON, UTF-8, `sort_keys=True`, `ensure_ascii=False`, `indent=2`, LF newlines,
trailing newline. That serialization *is* the canonicalization for
`config_digest` and `member_hash` (§5.3 states why a named external
canonicalization was not adopted).

```jsonc
{
  "schema_version": "wf3-members/1",
  "run": {
    "experiment": "experiment",
    "created_at": "2026-08-01T13:22:05Z",
    "config_path": "config/workflows/snake_config_model_test.yml",
    "config_digest": "sha256:1f0c…",          // see the enumeration below
    "guarded_sections_digest": "sha256:9ab3…", // = today's rule-3.00b params digest
    "wf1_snapshot_digest": "sha256:44de…",
    "wf2_snapshot_digest": "ABSENT",           // file_digest_or_absent semantics
    "weagen_template_digest": "sha256:c7e1…",  // config/templates/weathergen_config.yml
    "wflow_toml_digest": "sha256:5d20…",
    "staticmaps_digest": "sha256:e9aa…",       // CHUNKED read — see the note below
    "st_params_digest": "sha256:31bb…",        // canonical digest of the stress_test config section
    "store_dir": "…/climate_historical/era5_19800101_20101231",
    "grid": { "rlz_num": 2, "st_num": 6, "st_start": 1 },
    "master_seed": 24610,
    "master_seed_source": "template_default",  // "config" | "template_default"
    "policy": {
      "member_max_attempts": 2,
      "worker_max_members": 0,
      "allow_partial": false,
      "retain_member_artifacts": false,
      "sweep_workers": 3,
      "wflow_threads": 4
    },
    "tools": {
      "julia": "1.11.7",
      "wflow": "1.0.1",
      "weathergenr": "1.2.0+9f3d3189b692d9c6e94cf6f712ca5d1dd1b71cfa",
      "hydromt_wflow": "1.0.0"
    }
  },
  "realizations": [
    { "rlz": 1, "seed": 1583920117, "baseline_nc": "weather_generator/output/rlz_1_cst_0.nc" },
    { "rlz": 2, "seed":  902441365, "baseline_nc": "weather_generator/output/rlz_2_cst_0.nc" }
  ],
  "members": [
    {
      // shown for schema completeness only: the tracked fixture has
      // run_historical: false ⇒ st_start = 1 ⇒ NO cst_0 members exist on it.
      "member_id": "rlz_1/cst_0",
      "rlz": 1, "cst": 0, "baseline": true,
      "st_csv": null,
      "tavg": 0.0, "prcp": 0.0, "precip_variance": null,
      "toml":   "hydrology_runs/rlz_1/config/cst_0.toml",
      "result": "hydrology_runs/rlz_1/output/cst_0.csv",
      "member_hash": "sha256:c41b…"
    },
    {
      "member_id": "rlz_1/cst_1",
      "rlz": 1, "cst": 1, "baseline": false,
      "st_csv": "weather_generator/_work/cst_1.csv",
      "tavg": 0.0, "prcp": -30.0, "precip_variance": 1.0,
      "toml":   "hydrology_runs/rlz_1/config/cst_1.toml",
      "result": "hydrology_runs/rlz_1/output/cst_1.csv",
      "member_hash": "sha256:7e02…"
    }
  ]
}
```

Field notes:

- **All artifact paths are relative to `exp_dir`.** Absolute machine-scoped paths
  in a recorded artifact are the WG-5 `uri` mistake (weather-generator seam,
  deliberately-unpinned note); the manifest does not repeat it.
- **`baseline: true` members** (`cst_0`; admitted only under
  `run_historical: true`, so none exist on the tracked fixture) carry
  `st_csv: null` and `precip_variance: null`. They are first-class manifest
  members with the full member tuple and a `member_hash`, but the sweep
  executes them through the **baseline branch** of the member lifecycle (§6.6):
  no spec write, no perturb, downscale directly from the persistent baseline NC
  named by `realizations[].baseline_nc` — which is stage 2's product and is
  **never** deleted by any member step, deletion set, or resume-fold cleanup.
- **`tavg` / `prcp` / `precip_variance` are the *annual scalars*** the response
  surface is indexed by, derived exactly as the reduction derives them today
  (`export_wflow_results.py:196-198`): month-1 values, `prcp` as
  `precip_mean * 100 − 100`. The **monthly** structure stays in WG-2's
  `cst_<m>.csv`, which the manifest points at and which stays a declared input of
  the reduce rule. The manifest does not duplicate the 12-row record; it indexes it.
- **`config_digest` covers, exactly:** the parsed `project` section, the parsed
  `shared` section, and the parsed `workflows.climate_experiment` section, in the
  §5.1 canonical serialization. Nothing else — not `workflows.model_creation`,
  not `workflows.climate_projections` (those reach the record through
  `guarded_sections_digest`), and not the `workflows:` enablement flags. It is a
  *provenance* field, not a freshness lever: the freshness boundary is
  `member_hash`, and §7.6's invalidation table is written against that.

- **`member_hash`** = `sha256` over the canonical JSON of
  `{member_id, rlz, cst, baseline, seed_r, weagen_template_digest,
    st_params_digest, tavg, prcp, precip_variance, run_config_digest}`, where
  `run_config_digest` covers the result-affecting run parameters
  (`horizontime_climate`, `run_length`, `clim_source`, `data_sources`, the base
  `wflow_sbm.toml` digest, the staticmaps digest). This is the **member-level
  freshness boundary**, and every one of its terms is computable by rule 3.01
  from config and from wf1 products that already exist when it runs.

  **Three terms changed from v1, and the change is one mechanism, not three
  patches.** v1's `member_hash` covered the member's *hydrology* inputs and its
  *outputs* and **no generation-side input at all** — not the seed, not the
  generator template, and not the baseline NC the member's perturb step actually
  reads. Traced end to end, that made the §7.6 row "`master_seed` → every member
  invalidates" **false**: editing `master_seed` rewrote the manifest with new
  seeds but byte-identical `member_hash`es, regenerated every baseline NC,
  re-entered the sweep on the changed `rlz_nc` input, and then found every member
  reusable — because the reuse predicate inspected the member's *outputs* only.
  The sweep would skip everything and the reduce would publish a response surface
  computed against the **previous** realizations while `members.json` recorded
  the new seeds. Nothing fails, nothing warns. Re-seeding a stress test is
  routine CST practice, so this was a reachable operation. The repair has two
  halves, and both are needed:

  | Term | Layer | Catches |
  |---|---|---|
  | `seed_r` | `member_hash` (manifest time) | any `master_seed` edit, and any per-realization seed change |
  | `weagen_template_digest` | `member_hash` (manifest time) | any edit to `config/templates/weathergen_config.yml` — the file that supplies every other generator knob (§2.4) |
  | `st_params_digest` | `member_hash` (manifest time) | any edit to the `stress_test` config section, which is what *produces* the WG-2 grid |
  | `inputs.baseline`, `inputs.st_csv`, `inputs.weagen_template` | **recorded on every `succeeded` ledger row; verified at sweep start** (§5.5 condition 5) | a baseline NC or WG-2 file whose bytes changed with no config change at all — regeneration for any reason, a torn write, a hand edit, a different generator build |

  **Why `st_params_digest` and not v1's `st_csv_digest`.** v1 defined
  `member_hash` over "the content digest of the member's WG-2 file" while §4.1
  makes `climate_stress_parameters` — the WG-2 **producer**
  (`Snakefile_climate_experiment:318-330`) — take the manifest as its *input*. So
  rule 3.01 runs before the files it must digest exist: on a fresh experiment no
  `member_hash` is computable at all, and on a re-run it would digest the
  *previous* generation's WG-2 files, hashing a stress-grid edit one generation
  late — worse than failing. The stage order is not the thing to change (moving
  the WG-2 producer ahead of the manifest would run it *unguarded*, since the
  manifest is the guard sentinel). Instead the hash keys on the **config section
  the WG-2 files are derived from**, which the manifest rule already holds, and
  the *file's* bytes are covered one layer down by the recorded-input digest.
  Per-column granularity survives: a stress-grid edit changes each member's
  `tavg`/`prcp` scalars too, so only the affected column's hashes move.

  **`wflow_sbm.toml` and `staticmaps.nc` need a rerun-trigger, or they are stale
  by construction.** Both are wf1 products; rule 3.01 declares neither as an
  input and would not notice a rebuilt `hydrology_model/` under an unchanged wf1
  config, leaving every `member_hash` stale and letting members skip against a
  model they were never run on. The repo already solves exactly this:
  `Snakefile_climate_experiment:174-175` threads `file_digest_or_absent(...)`
  through `params:` so a **content-only** change re-triggers past `ancient()`.
  Rule 3.01 carries `wflow_toml_digest` and `staticmaps_digest` on that pattern.
  *(The alternative — dropping both from `member_hash` — is rejected: a model
  rebuild genuinely invalidates every member.)*

  **`staticmaps_digest` must be chunked.** `file_digest_or_absent`
  (`snake_utils.py:177-181`) slurps the whole file with one `f.read()` and runs
  at Snakefile **parse** time — on every invocation, including `--dry-run` and
  `--unlock`. Its current callers are small YAML snapshots; `staticmaps.nc` on a
  real basin is not, and the 152 KB fixture hides it completely. v2 adds a
  chunked sibling (`file_digest_or_absent(path, chunk=1 << 20)`, same `ABSENT`
  sentinel, same return type) and uses it for the grid. Semantics are unchanged;
  only the memory profile is.

- **`precip_variance` stays in the member tuple and inside `member_hash` while
  the axis is inert** — forward compatibility, per the G1 retention ruling.
  **Accepted, named cost:** editing `stress_test.precip.variance.{min,max}`
  forces a full re-sweep that provably cannot change a single output value
  (§9.1). Dropping the field from the hash would not remove that, since
  `st_params_digest` covers the same config keys, and carving them out would put
  a special case inside the freshness boundary to serve a temporary state.
  Removing both is part of followup **R9-F1** when the axis activates.
- **`tools`** is *recorded, not enforced*. A Wflow or weathergenr version change
  does **not** invalidate members in v2.0. Rationale and the falsifier that would
  overturn it: §9.2 and §12 C-13. This is the single most consequential
  simplification against `cst-run-control`'s `environment_digest` condition.

### 5.2 Ledger schema — `ledger.jsonl`

One JSON object per line, UTF-8, LF, append-only, never rewritten in place.

| field | type | on which events | semantics |
|---|---|---|---|
| `ts` | str | all | RFC 3339 UTC, second resolution. **Descriptive only** — see the ordering rule below |
| `invocation_id` | str | all | uuid4 — the **workflow** invocation id, minted exactly once per workflow by the `onstart` lock handler and **adopted** by `run_sweep` from `_state/experiment.lock` (§6.6). The runner never mints its own |
| `member_id` | str | all | `rlz_<n>/cst_<m>` |
| `member_hash` | str | all | ties the row to a config generation. On `claimed`/`succeeded`/`failed` rows: the current manifest's hash for this member. **On `quarantined` rows: the hash of the rows being superseded** — the hash the quarantined outputs were recorded under — so the row *closes* the sub-sequence it belongs to (§5.3); on a hash-change quarantine, `detail` names both hashes |
| `event` | str | all | `claimed` \| `succeeded` \| `failed` \| `quarantined` |
| `attempt` | int | all | 1-based, scoped to `(member_id, member_hash, invocation_id)` |
| `worker_id` | int \| null | `claimed`, terminal | the slot that owns the member |
| `seconds` | object | terminal | `{"perturb": 3.9, "downscale": 11.2, "simulate": 34.8, "verify": 0.2}`. Baseline members **omit `perturb`** — the step never ran (§6.6 baseline branch) |
| `outputs` | object | `succeeded` | `{"result": "sha256:…", "toml": "sha256:…"}` |
| `inputs` | object | `succeeded` | `{"baseline": "sha256:…", "st_csv": "sha256:…" \| null, "weagen_template": "sha256:…" \| null}` — the digests of the files this member was **actually computed from**, so reuse can check its *inputs* and not only its outputs (§5.5 condition 5). Baseline members record `st_csv: null` **and** `weagen_template: null` — neither file participates in the baseline branch (§6.6); a recorded `null` is *defined-absent*, not missing data |
| `stage` | str \| null | `failed` | `perturb` \| `downscale` \| `simulate` \| `verify` — where it broke |
| `class` | str \| null | `failed` | `member` (deterministic, do not retry) \| `worker` (infrastructural, retryable) |
| `detail` | str \| null | `failed`, `quarantined` | one-line reason, newlines stripped. On `quarantined` rows, one of the enumerated causes: `hash change: <old>→<new>` \| `input digest mismatch: <input>` \| `output digest mismatch` \| `output missing` \| `interrupted` — the cause set §5.4's two invalidation clauses distinguish after the fact |

Example (a member that lost its worker and succeeded on the retry):

```jsonl
{"ts":"2026-08-01T13:22:41Z","invocation_id":"7c1f…","member_id":"rlz_1/cst_3","member_hash":"sha256:7e02…","event":"claimed","attempt":1,"worker_id":2}
{"ts":"2026-08-01T13:23:19Z","invocation_id":"7c1f…","member_id":"rlz_1/cst_3","member_hash":"sha256:7e02…","event":"failed","attempt":1,"worker_id":2,"stage":"simulate","class":"worker","detail":"worker 2 exited with code 3221225477 before answering request 14"}
{"ts":"2026-08-01T13:23:21Z","invocation_id":"7c1f…","member_id":"rlz_1/cst_3","member_hash":"sha256:7e02…","event":"claimed","attempt":2,"worker_id":2}
{"ts":"2026-08-01T13:24:33Z","invocation_id":"7c1f…","member_id":"rlz_1/cst_3","member_hash":"sha256:7e02…","event":"succeeded","attempt":2,"worker_id":2,"seconds":{"perturb":3.9,"downscale":11.2,"simulate":34.8,"verify":0.2},"outputs":{"result":"sha256:0f1a…","toml":"sha256:bb90…"}}
```

**`ledger_final.csv`** — the reduce's declared input. Columns:
`member_id, rlz, cst, tavg, prcp, precip_variance, result, result_sha256,
seconds_total, attempts, succeeded_invocation_id, finalization_invocation_id`.
One row per member of the current manifest that reached `succeeded`, ordered
realization-major / cst-minor (the `expand()` order §4.4 relies on). **The two
invocation columns carry different facts and must not be conflated** (their
conflation is exactly what made resumed sweeps un-reducible):
`succeeded_invocation_id` is per-member — the invocation whose `succeeded` row
the fold selected, so a resumed sweep (GF-2) or a partial-then-retried one
(GF-13) *naturally carries mixed values*, and that mixture is provenance, not
an error; `finalization_invocation_id` is **uniform** — the invocation that
performed this finalization, identical in every row and equal to the value in
`sweep_completeness.csv` / `sweep_summary.json` written in the same
finalization sequence. It is a **projection of manifest ⋈ ledger**, carrying
no fact not derivable from those two — so a lost `ledger_final.csv` is always
rebuildable.

**`sweep_completeness.csv`** — one **homogeneous** row population, one parseable
CSV. Columns:
`invocation_id, config_digest, member_id, state, attempts, stage, class, detail`.

- **Row population, fixed:** every member of the current manifest (succeeded ones
  included), **plus** every orphan found on disk, with `state` as the
  discriminator (`succeeded` | `failed` | `quarantined` | `pending` | `orphan`).
  v1 described this record three times with three different populations; this is
  the single one.
- **No trailing summary row.** A heterogeneous last line makes a CSV a naive
  reader cannot parse. Aggregate counts move to `_state/sweep_summary.json`
  (`{invocation_id, config_digest, manifest_created_at, counts:{…}, accepted,
  allow_partial, tools_drift:[…]}`), which is what the reduce reads.
- **Identity fields are mandatory.** v1's record carried no `invocation_id`, no
  `config_digest`, no timestamp — nothing binding it to the sweep generation it
  describes, in a design that stamps `invocation_id` and `member_hash` on every
  ledger row. The consequence lands on the one artifact whose entire job is
  telling a scientist which cells are trustworthy: a completeness record could
  not be shown to describe the response surface published beside it. The reduce
  **hard-fails** when the completeness record's `invocation_id` differs from
  `ledger_final.csv`'s uniform **`finalization_invocation_id`** — and validates
  against **that column only, never against the per-member
  `succeeded_invocation_id`**, so a resumed or retried sweep whose successes
  span multiple invocations passes the identity check by construction (the
  check binds the *finalization generation*, which is what the completeness
  record describes; member provenance is deliberately mixed). GF-2 and GF-13
  carry this through a successful reduction (C-24). The same two fields
  propagate to `indicators/completeness.csv`.

**Finalization order, normative.** These writes happen in exactly this sequence,
and the last statement before exit is the declared output:

1. `flush()` + `fsync()` every ledger row (already done per row, §5.3);
2. write `_state/sweep_completeness.csv` atomically;
3. write `_state/sweep_summary.json` atomically;
4. write or delete `_state/sweep_incomplete.json` (§7.2);
5. write `_state/ledger_final.csv` atomically — **last**.

Ordering matters because `ledger_final.csv` is the declared output and therefore
the gate that unblocks the reduce: written last, a kill at any point leaves the
reduce blocked rather than reading a completeness record from a different
generation. v1 stated both writes independently and fixed no order.

**Fold ordering, normative.** §5.4's fold rule says "take the last row". **File
order is authoritative; `ts` must never be used for ordering.** `ts` is
second-resolution while several member sub-steps are millisecond-scale (§6.6
steps 1, 5, 6), so a `claimed` and its terminal row can share a `ts` — and an
implementer who reads "last" as sort-by-`ts` would fold a same-second
`claimed`/`succeeded` pair to `claimed`, declare the member interrupted, and
quarantine a verified output. That is wasted work rather than wrong science, but
it is a *nondeterministic* resume verdict in the component R-1 rates highest, and
it costs one sentence to close. §13 step 4's fold unit tests carry a same-`ts`
pair as a named case.

### 5.3 Atomicity, single writer, crash consistency

**Single writer by construction, not by convention.** Only the orchestrator
*parent* process writes `_state/` **during the sweep**. Slot processes never
touch the ledger; they report outcomes over their per-slot `multiprocessing.Pipe`
connections and the parent serializes them (§6.1). Multi-writer interleaving is therefore not a
hazard this design has to mitigate — which is why no file locking, no
compare-and-set and no fencing token appears on the ledger write path. *One
amendment against v1:* `_state/experiment.lock` is written by the **Snakemake
main process** in its `onstart` handler and removed in `onsuccess`/`onerror`
(§6.6), because the lock must outlive any single rule. It is the one `_state/`
path the orchestrator does not own, it is create-exclusive and delete-only, and
nothing else reads or writes it during a sweep.

**Whole-file artifacts** (`members.json`, `ledger_final.csv`,
`sweep_completeness.csv`, `sweep_summary.json`, `sweep_incomplete.json`): write
to `<name>.tmp` in the *same directory*, `flush()`, `os.fsync()`, close, then
`os.replace()`. `os.replace` is atomic and overwrites on both Windows and POSIX
(`os.rename` does not overwrite on Windows — that is the trap this rule exists to
avoid). A crash leaves either the previous complete file or none; never a half
file.

**Windows: `os.replace` over a file another process holds open raises
`PermissionError`**, and this design deliberately creates such a reader —
`scripts/sweep_status.py` is a first-class *concurrent* reader of exactly these
files (§7.5), as are editors and AV scanners. POSIX has no equivalent failure, so
the hazard is invisible on Linux and lands on the dev platform, in exactly the
situation the status command exists for. Every whole-file write therefore carries
a **bounded retry**: 5 attempts, 200 ms apart, then a named
`AtomicReplaceError` stating the path, the holder-agnostic cause and the
remedy ("close any process reading `_state/`"). Readers are correspondingly
specified to open, read fully, and close — never to hold a handle across a
sweep.

**The ledger** is append-only: one `write(json.dumps(row, sort_keys=True) + "\n")`
followed by `flush()` and `os.fsync()`, per row. No rename, because a rename-based
scheme would rewrite the whole ledger on every member and lose the append-only
audit property that `cst-run-control` asks for.

**Crash-consistency semantics on read** — the rule that makes a non-atomic append
safe, and the rule the "corrupt ledger row" gate discriminates:

| Observation | Interpretation | Action |
|---|---|---|
| Final line has no trailing `\n` | **Truncated tail** — a crash mid-append | Drop the line silently; log one line noting the truncation |
| Any line (including the last complete one) fails JSON parse | **Corruption** | Hard error; refuse to proceed |
| Any line parses but violates the row schema | **Corruption** | Hard error; refuse to proceed |
| A **schema-valid** row (or sub-sequence) whose `member_id` is absent from the current manifest | **Legal history** — a superseded member generation (grid resize, `realizations_num` reduction), regardless of whether its artifacts still exist on disk | Excluded from the fold's current-state verdicts; still subject to the epoch legality rules below within its own `(member_id, member_hash)` sub-sequence; counted in the orphan report *only* when artifacts exist (§7.4) |
| A `succeeded` row whose recorded `result_sha256` no longer matches the file on disk | **Divergence** | Member reverts to pending; quarantine the file (§7.4) |
| A row **sequence** for one `member_id` that violates the **epoch-scoped** legality rules below | **Corruption** | Hard error, handled exactly like a corrupt row: named `member_id`, named line numbers, the quarantine command |

**Transition legality is epoch-scoped, because the design's own repair paths
legitimately produce repeated success.** A `succeeded → quarantined → claimed →
succeeded` history is *correct behaviour* — it is exactly what a GF-12
invalidation or an F8 repair leaves behind — so v2's flat "two `succeeded` rows"
rule condemned the histories §5.4 and §7.3 are specified to produce. The rules,
normative:

- **Scope.** Legality is evaluated per `(member_id, member_hash)` sub-sequence,
  in file order, over the *whole* ledger (not only the current hash — corruption
  detection must cover superseded generations too).
- **Epoch.** An *execution epoch* is a maximal run of such a sub-sequence's rows
  containing no `quarantined` row; each `quarantined` row **closes** the current
  epoch (it carries the hash of the rows it supersedes, §5.2). `quarantined` is
  an intervention row: it is legal anywhere, may repeat (a re-fold that finds the
  outputs already moved appends nothing, but a repeated row is not corruption),
  and is exempt from the claimed-precedence rule.
- **Legal epoch shape.** Zero or more `claimed → failed` attempt pairs, then at
  most one `claimed → succeeded`, then nothing until the epoch closes or the
  sequence ends. A dangling `claimed` (no terminal successor) is legal — it is
  the interrupted state.
- **Illegal (= corruption), the unit-test set of §13 step 4:**
  1. a `succeeded` or `failed` row with no open `claimed` in its epoch;
  2. any `claimed`/`succeeded`/`failed` row after a `succeeded` **in the same
     epoch** — equivalently, two `succeeded` rows for one
     `(member_id, member_hash)` with **no intervening `quarantined`**;
  3. a `claimed` row while another `claimed` in the same epoch is unresolved
     (the double-claim shape — in-run, the parent never assigns a member twice,
     and every resume quarantines an interrupted member before re-claiming).

  **Deliberately absent from the illegal set: an out-of-manifest `member_id`.**
  Ledger-history legality is **decoupled from live artifact existence**: a
  schema-valid sub-sequence for a member the current manifest no longer names
  is *legal history* (the table above), whether or not
  `prune_experiment_orphans.py --delete` has since removed its artifacts —
  history in an append-only record must not become corruption because a
  documented maintenance action ran (§7.4). v3 coupled the two ("not a known
  orphan", defined from disk), so the documented resize→prune sequence made the
  next fold refuse to start. GF-23 gates the composition; C-26 is the claim.
- **Legal histories the tests must accept**, both named because v2's rule
  rejected them: *(a) same-hash repair* — `claimed → succeeded →
  quarantined(detail=output digest mismatch, same hash) → claimed → succeeded`;
  *(b) changed-hash invalidation* — `claimed → succeeded` under hash A,
  `quarantined` carrying hash A with `detail=hash change: A→B`, then
  `claimed → succeeded` under hash B.

§5.4 declares the state machine; this is its detector. A fold that only "takes
the last row" evaluates **no** transition legality, so an impossible history
folds to a perfectly valid state — and §8.1's escalation clause ("no legal member
transition resolves") presumes legality is evaluated *somewhere*. Given R-1 ("a
ledger bug silently skips a member") is rated High, epoch-scoped legality is the
cheapest available detector for that bug class that does not also condemn the
repair histories the design itself specifies.

The hard-error path names the offending line number and prints the recovery
command: `snakemake … --config sweep_quarantine=1` (a **top-level** `--config`
key, resolved per §4.3). The recovery is an **explicit inventory, not a "move
everything" rule** — v3's "everything else under `_state/` moves" was not
implementable: it recursively included the quarantine directory in its own
move, removed the declared `members.json` sentinel mid-workflow, and left the
persistent member CSVs/TOMLs in place for the forced full rerun to overwrite.
Normative, executed by the runner before any other action of that invocation:

1. **Create the quarantine generation** `_state/quarantine/<invocation_id>/`
   (the *adopted* workflow invocation id, §6.6).
2. **Preserve in place, never moved:** `_state/experiment.lock` (held by the
   running workflow; its release handler must find it at the claimed path),
   `_state/members.json` (the declared manifest sentinel — removing it
   mid-workflow would orphan every downstream rule's input), and the
   quarantine root `_state/quarantine/` itself (a directory is never moved
   into its own child).
3. **Move into the generation dir — active ledger and finalization state:**
   `ledger.jsonl`, `ledger_final.csv`, `sweep_completeness.csv`,
   `sweep_summary.json`, `sweep_incomplete.json` (whichever exist), and
   `_state/members/` (the member spec dirs).
4. **Move into the generation dir — every current manifest-owned member
   output**, under `member_products/<member_id>/` preserving relative paths:
   each manifest member's HM-4 TOML and HM-5 CSV, plus any surviving
   transients (WG-4 perturbed NCs, WG-6 forcings, HM-6b states). The fresh
   ledger implies a full rerun; without this move the rerun overwrites the
   only surviving copies of the artifacts the corrupt ledger can no longer
   vouch for. **The persistent baseline NCs (`rlz_<n>_cst_0.nc`) do not
   move** — they are stage-2 products owned by generation, not member
   outputs (§6.6 baseline branch).
5. **Start a fresh ledger** (empty `ledger.jsonl`) and proceed.

Quarantine is retention, never deletion (`cst-run-control`
references/resume.md). GF-22 executes this command to completion; C-25 is the
claim.

**Per-member CSVs are not atomic** — Wflow writes them directly (A6). Mitigation:
a member is recorded `succeeded` only after the worker returns `ok` **and** the
CSV exists, parses with a `time` index and ≥ 1 row, and its `sha256` is recorded.
A torn CSV therefore never reads as done, on this run or on a resume.

### 5.4 Member state machine

```
                    ┌──────────────── (member_hash changed) ────────────────┐
                    ▼                                                       │
  pending ──claim──▶ claimed ──ok+verified──▶ succeeded ────────────────────┘
     ▲                  │  │
     │                  │  └──error(class=member)──▶ failed  (terminal for this invocation)
     │                  │
     │                  └──error(class=worker) / interrupted──┐
     │                                                        ▼
     └───────────── attempt < member_max_attempts ─────── (re-claim)
                              else ──▶ failed

  any state ──(quarantine)──▶ quarantined ──▶ pending
```

- **States:** `pending` (implicit — no terminal row), `claimed`, `succeeded`,
  `failed`, `quarantined`. Derived by folding the ledger, not stored. Legality of
  a row *sequence* is epoch-scoped (§5.3): every `(quarantine)` edge in the
  diagram closes an epoch, and repeated success across a `quarantined` boundary
  is the designed repair history, never corruption.
- **The fold rule:** for each `member_id`, consider only rows whose `member_hash`
  equals the current manifest's; take the last row **in file order** (§5.2).
  `claimed` with no terminal successor ⇒ **interrupted** ⇒ treat as pending, and
  quarantine any partial output before re-claiming.
- **Attempt counting** is scoped to `(member_id, member_hash, invocation_id)`:
  `attempt = 1 + count(claimed rows in this invocation)`. `member_max_attempts`
  (default 2) bounds retries **within one invocation**; a new invocation always
  re-attempts a non-`succeeded` member. This is deliberate: within a run, an
  auto-retry only makes sense for `class=worker`; across runs, the user has
  changed something, and refusing to retry would be surprising. The full history
  survives in the append-only ledger regardless.
- **`class=member` is never retried inside an invocation.** A Wflow error on
  deterministic inputs (A3) will reproduce; retrying only burns a warm worker.
- **A member whose `member_hash` changed is `pending` again**, and its recorded
  outputs are quarantined before re-execution — the config-invalidation path
  (§7.3).
- **A member whose recorded `inputs` digests no longer match the live inputs is
  `pending` again**, on the same terms. This is the parallel clause for the
  layer `member_hash` cannot reach: bytes that changed on disk with no config
  change (§5.1, §5.5 condition 5). Same quarantine, same re-execution; the
  ledger's `quarantined` row records `detail="input digest mismatch: baseline"`
  so the two causes are distinguishable after the fact.

### 5.5 `cst-run-control` mapping (OQ-2 — the named subset)

The contract is service-grade machinery for a single-machine sweep. The rule
applied: **adopt the vocabulary and semantics that carry the risk; skip the
distributed-coordination layer; record the mapping so a future conforming adapter
is a lift, not a rewrite** (scoping intake OQ-2 recommendation, accepted).

| `cst-run-control` element | Disposition | Realization / reason |
|---|---|---|
| Two records: immutable intent, mutable state (`SKILL.md` operating rules) | **ADOPTED** | `members.json` (frozen when written) / `ledger.jsonl` |
| Intent frozen at first `ready` | **ADOPTED, adapted** | The manifest is immutable for the life of a sweep; Snakemake's params trigger, not a state transition, is what re-writes it |
| `run_id` | **ADAPTED** | Run identity is `(project_dir, experiment)`; per-execution identity is `invocation_id`. No globally unique opaque id — nothing outside this repo consumes one |
| `config_hash`, `intent_hash` | **ADOPTED, reduced** | `config_digest` + per-member `member_hash` |
| `scientific_design_hash` | **SKIPPED** | Would require separating scientific design from configuration; the repo has one config document and the split would be arbitrary (this is ADR 0022's own recorded "configuration leakage" limitation, unavoidable here) |
| `canonicalization_id` = `cst-canon/1` + conformance vectors | **SKIPPED** | Digests are exchanged with no other adopter. The canonicalization is stated in §5.1 and pinned by a unit test instead. **Lift point:** re-canonicalize under `cst-canon/1` and the digests change; nothing else does |
| 10 capability slots with revisions/owners/validation authorities | **SKIPPED**, partially substituted | Every slot binding is this repository at one commit. `run.tools` records the four version facts that actually vary (julia, wflow, weathergenr, hydromt_wflow). Proportionality (decision criterion 4): a 10-slot table restating "this repo" in every row is ceremony |
| Typed `stage_graph` + six ordering rules | **SKIPPED** | Snakemake's DAG *is* the stage graph. A second declaration would be a second source of truth that can silently disagree with the first |
| `output_namespace` + atomic namespace claim | **ADOPTED, reduced** | `_state/experiment.lock` via `O_CREAT\|O_EXCL`, claimed in `onstart` for the **whole workflow** (§6.6), experiment-scoped. No ancestor/descendant overlap algebra — experiments do not nest |
| Fencing token, token-checked publication | **ADAPTED** | `invocation_id` on every row makes a superseded writer's rows *identifiable*; it does not *prevent* their write. Accepted residual risk under A1 + the lock. **Named in §15 as residual risk R-3** |
| Content-addressed staging → seal → inventory CAS | **SKIPPED** | Would require intercepting Wflow's own output writes. Substituted by digest-on-record + digest-on-resume (§5.3), which catches the same corruption without owning the write path |
| State set `planned/ready/running/succeeded/failed/cancelled` | **ADOPTED at member granularity**, reduced (§5.4) | The run-level lifecycle is Snakemake's; the member-level one is ours |
| Every transition a single CAS against `state_revision` | **SKIPPED** | Single writer (A1) makes CAS vacuous. Substituted by append-only + fold |
| Append-only attempts, closed attempts never rewritten | **ADOPTED** | §5.2 |
| Checkpoint reusability — six conditions | **ADOPTED as five** (see below) | Skipped: `environment_digest` (see `tools`, §9.2 — a deliberate, falsifiable simplification); `stage_interface_version`; the `validation` record (next row) |
| `validation_authority` on each binding; a passing validation record required for `succeeded` | **SKIPPED** | The repo's validation authority is its validator suite (WG-1..6 / HM-1..7) and `check_baseline.py`, run as tests, not recorded per member. ADR 0022 itself records that validation records have "no normative collection" — adopting the field without the collection buys nothing |
| Quarantine before resume | **ADOPTED** | §7.4 |
| `resume_policy` + `max_attempts` | **ADOPTED as** `member_max_attempts` | §5.4 |
| Conformance levels + validity profiles | **SKIPPED** | Declaring a level implies validating against its profile; there is no second adopter to be conformant *with* |

**The five reusability conditions, in full.** A member is SKIPPED on resume iff
**all five** hold; any failure ⇒ QUARANTINE, RUN (§7.3):

| # | Condition | Reads |
|---|---|---|
| 1 | The row's `member_hash` equals the current manifest's for that `member_id` | manifest |
| 2 | The member's last row (file order) is `succeeded` | ledger |
| 3 | Every recorded output artifact exists | disk |
| 4 | Every recorded **output** digest (`outputs.result`, `outputs.toml`) verifies | disk |
| 5 | Every recorded **input** digest (`inputs.baseline`, `inputs.st_csv`, `inputs.weagen_template`) matches the live file, digested once per invocation at sweep start. A recorded `null` (the baseline branch's `st_csv` and `weagen_template`, §5.2) is *defined-absent*: it participates in no comparison and can neither pass nor fail the condition | disk |

Condition 5 is v2's addition and it is what makes the reuse predicate a statement
about *the member*, rather than about the member's outputs. v1's four conditions
inspected the `outputs` object only, so a changed input under an unchanged
`member_hash` was **structurally invisible** — see §5.1 for the trace. Cost: one
digest per baseline NC and per WG-2 file per invocation (`RLZ_NUM + ST_NUM`
files, not `K`), computed before any worker spawns, so a no-op resume still pays
no `using Wflow` (C-2 holds).

**Net:** roughly the intent/state split, digests, the state-and-attempt machine,
quarantine, and the namespace claim are in; the distributed-coordination layer,
the slot table, the typed stage graph, and the conformance apparatus are out.
Every skip above is a *stated* skip, which is the thing that makes the later lift
mechanical.

## 6. Worker pool and sweep runner

### 6.1 Process topology

```
snakemake job "run_sweep"
└── orchestrator  (python, blueearth_cst/experiment/run_sweep.py)     ← SOLE ledger writer
    │  owns: lock, manifest, ledger, pending set, ASSIGNMENT TABLE
    │        (slot_id → member_id), scheduling, finalization
    │  per-slot duplex mp.Pipe (assign/ack/result/stop) + process sentinel
    ├── slot 0  (python subprocess, spawn)                 imports hydromt ONCE
    │   └── julia worker 0  (persistent, --threads M)      loads Wflow ONCE
    ├── slot 1  (python subprocess)
    │   └── julia worker 1
    └── slot p−1 …
```

**Three levels, each amortizing a different fixed cost.**

- The **orchestrator** (`run_sweep.py`) never imports hydromt and never blocks on
  a member. It is the single ledger writer (§5.3) and, during the sweep, the only
  process that touches `_state/`. It is launched by a `shell:` rule through
  `run_logged.py`, **not** as a `script:` module, and it is import-cheap by
  construction — both are normative and §4.3 states why (a `script:` module plus
  `spawn` re-executes the module top level in every child).
- A **slot** is a persistent Python subprocess (`multiprocessing`, `spawn` start
  method — Windows has no other, and using it everywhere keeps the two platforms
  on one code path) whose body is the separate importable module
  `blueearth_cst/experiment/sweep_slot.py`. It imports `hydromt_wflow` once and
  reuses that import for every member it handles. P3-3 measured 342–359 s of
  non-3.10 work over 43 rows, a large share of it 12 separate hydromt imports;
  amortizing them is a real second win beside the Julia one (§12, C-4 makes it
  falsifiable). The slot calls `run_downscale(...)` — the extracted callable of
  §2.5 — never a module whose top level reads a `snakemake` global.
- A **Julia worker** is a persistent `julia +1.11.7 --project=. --threads M`
  process running `blueearth_cst/experiment/wflow_worker.jl`, which loads
  `Wflow` once and then serves one request at a time. It is
  `run_wflow_batch.jl`'s loop turned inside out: the same `Wflow.run(toml)` under
  the same per-member try/catch, reading its member list from stdin instead of
  from `ARGS`.

**Why the pool boundary is here (OQ-7, §9.7).** The orchestrator owns scheduling
*and* the ledger, so the single-writer property is structural rather than
enforced. Pushing the queue into Julia (`Distributed.jl`) would put scheduling on
the far side of the single-writer boundary and grow the Julia surface this repo
maintains (§14.4).

**Parent-owned assignment — the scheduling contract.** v2 put the members on a
shared pull queue, and that topology had an unrecoverable blind spot: a slot
could dequeue a member and die before any report reached the parent, and the
parent — observing only a dead process — could not tell *which* member had
vanished from the queue, despite F4 promising it would retry exactly that
member. v3 removes the shared queue entirely. **The parent assigns; slots never
take.** A member leaves the pending set only by a parent action whose durable
record precedes the dispatch, so at every instant the parent can name every
in-flight member from its own records. Transport is one duplex
`multiprocessing.Pipe` per slot plus the slot's process sentinel —
`Connection.send` writes into the OS pipe from the sending process with no
feeder thread, so a message fully sent survives its sender's death (the property
`mp.Queue`, whose feeder thread can lose buffered items with a dying process,
does not give).

Messages (pickled dicts over the per-slot pipe):

| Direction | Message | Fields | When |
|---|---|---|---|
| slot → parent | `ready` | `slot_id` | after spawn-time imports complete, and after every terminal report |
| parent → slot | `assign` | `member_id`, `attempt`, the member's spec (paths, params) | only to a slot that is `ready` and has no open assignment |
| slot → parent | `ack` | `slot_id`, `member_id` | the slot's first action on receipt, before the perturb step. **Diagnostic only** — it timestamps receipt in the orchestrator log; no recovery decision depends on it (GF-19 proves that) |
| slot → parent | `result` | `slot_id`, `member_id`, `status` (`succeeded` \| `failed`), `stage`, `class`, `seconds`, `outputs`/`inputs` digests, `detail` | the member's terminal report |
| parent → slot | `stop` | — | pending set empty; the slot drains its worker (`shutdown`/`bye`, §6.2) and exits 0 |

**The assignment sequence, with its state writes in order:**

1. A slot reports `ready`. The parent pops the head of the pending deque
   (ordering per §6.4).
2. The parent **appends and fsyncs the `claimed` ledger row** (`member_id`,
   `member_hash`, `attempt`, `worker_id = slot_id`) and records the assignment
   in its in-memory table `slot_id → (member_id, attempt)` — **before** any
   message is sent. Claim-before-dispatch is normative: the ledger row is the
   durable record of the assignment, and the table is its in-run index.
3. The parent sends `assign` on that slot's pipe.
4. The slot sends `ack`, runs the member (§6.6), and sends `result`.
5. The parent appends the terminal row, clears the table entry, and the slot is
   `ready` again.

**The event loop and dead-slot recovery.** The parent blocks on
`multiprocessing.connection.wait([conn_0..conn_{p-1}] + [sentinel_0..sentinel_{p-1}])`.
When a slot's **sentinel** fires, the parent first **drains that slot's pipe**
of any fully-delivered messages (a `result` sent before death is processed
normally), then consults the assignment table: if the slot's entry is still
open, the parent knows exactly which member was in flight — it appends
`failed`/`class=worker` for **that recorded member** (`detail` naming the slot
and its exit code), requeues it while `attempt < member_max_attempts`, and
respawns the slot. No reconciliation pass, no inference from disk: the answer
was written down before the work was handed out.

**Crash windows, enumerated:**

| # | Window | Outcome |
|---|---|---|
| W1 | parent appends `claimed`, dies before sending `assign` | next invocation's fold sees `claimed` with no terminal ⇒ interrupted ⇒ quarantine + re-run (§7.3) |
| W2 | `assign` sent; slot dies before `ack`, mid-member, or before `result` | sentinel + open table entry ⇒ the recorded member is failed/`class=worker`, requeued, slot respawned — one recovery path for the whole window, which is why `ack` carries no recovery weight |
| W3 | slot sends `result` fully, dies before the parent reads it | the message is in the OS pipe and is drained at sentinel handling; folds normally. A *partially written* `result` (death mid-`send`) raises on `recv` and collapses to W2 — the member re-runs; deterministic inputs (A3) make the repeat safe, and the ledger records both attempts |
| W4 | the v2 dequeue-and-die window | **structurally gone** — there is no shared queue; a member leaves `pending` only via step 2's fsync'd `claimed` row |

GF-16 (slot killed mid-member) and GF-19 (slot killed in the `assign`→`ack`
window) gate the two halves of W2; C-21 is the claim.

### 6.2 Orchestrator ↔ Julia worker line protocol

**Newline-delimited JSON over the worker's stdin/stdout, strict
request/response, one request in flight per worker.** Probe PR-5 (§11.2)
exercised exactly this shape.

**Every worker stream is a file, never an undrained pipe — and member output is
routed per member, not per spawn.** Two rules compose here, and v2 conflated
them. The *anti-hang* rule: if the slot reads the worker's stdout with a
blocking call while stderr is an undrained `PIPE`, the Julia worker blocks on
its first full stderr buffer (64 KB on Windows) mid-`Wflow.run` and **never
answers** — no heartbeat, no timeout, and F12's "all workers retire" never
fires, because the worker has not exited. Wflow is verbose over a ~35 s run, so
the buffer fills in normal operation. The *attribution* rule, which v2 broke by
satisfying the first one with a single spawn-time handle: a persistent worker
serves many members, so a handle fixed at spawn writes **every later member's
Wflow output into the first member's log** — G4's per-member visibility would be
false for all but one member per session. The mechanism, normative on both
counts:

- **At spawn**, the slot opens the per-worker lifecycle log
  `logs/_parts/3.08_run_sweep/_worker_<id>.log` and passes that **file handle**
  as the worker's `stderr` (`stderr=<handle>`). Handshake output, Julia warnings
  *between* members, and any crash backtrace outside a member window land there
  — attributed to the worker, which is what they belong to. No stream is ever an
  undrained `PIPE`, so the hang class stays closed.
- **Per member**, the `run` message carries the member's `log` path (absolute).
  The worker opens it in append mode and redirects **both stdout and stderr** at
  the fd level around that member's run —
  `redirect_stdout(logio) do redirect_stderr(logio) do Wflow.run(toml) end end`
  — then flushes, closes, and writes the `result` line on the **restored**
  protocol stdout. Julia's `redirect_*` on an `IOStream` swaps the OS-level
  descriptor, so even native-code output mid-`Wflow.run` (including a fatal
  backtrace) lands in the *right member's* log.
- **One writer at a time on the member log.** The slot writes the perturb and
  downscale output and **closes its handle before sending `run`**; the worker
  appends the simulate output and closes before answering; the slot then appends
  the verify result. Sequential handoff, never concurrent — a Windows
  file-sharing conflict is impossible by construction.

GF-14 gates the anti-hang half (a stub worker flooding > 1 MB to stderr must not
stall — the flood lands in `_worker_<id>.log` or the member log, whichever
window it falls in); **GF-20 gates the attribution half** (two sequential
members on one worker, strict log separation); C-22 is the claim.

**The pipes are UTF-8 with an explicit error policy.** Julia writes UTF-8;
Python text-mode pipes default to the *locale* codec, which is cp1252 on this dev
box — and `.github/workflows/ci.yml` names cp1252/CRLF/file-locking as the
Windows defect class this repo owns, while `Snakefile_climate_experiment:21-25`
records that `run_logged.py` exists partly to do "UTF-8/exit-code handling" for
exactly these R and Julia children. Left unpinned, a Wflow error string carrying
a non-cp1252 character raises `UnicodeDecodeError` **in the orchestrator's
reader** — the decode fails on the very message the failure path exists to carry,
and the member is recorded `class=worker` with a decode traceback instead of the
real error. Normative: `encoding="utf-8", errors="replace"` on the worker's
stdin/stdout/stderr handles **and** on the per-member `Rscript` capture. CRLF
needs no handling — `json.loads` tolerates a trailing `\r`.

| Direction | Message | Fields |
|---|---|---|
| worker → orch (once, on start) | `ready` | `type`, `protocol` (int, `1`), `worker_id`, `pid`, `julia`, `wflow` (version string) |
| orch → worker | `run` | `type`, `request_id` (monotone int), `member_id`, `toml` (absolute path), `log` (absolute path — the member log the worker redirects into for this member) |
| worker → orch | `result` | `type`, `request_id`, `member_id`, `status` (`ok` \| `error`), `seconds` (float), `error` (string, newlines stripped; present iff `status="error"`) |
| orch → worker | `shutdown` | `type` |
| worker → orch | `bye` | `type` |

Rules:

1. **Every message is one line, `flush`ed immediately.** Julia's stdout is
   block-buffered when redirected; the probe confirms an explicit `flush(stdout)`
   after each `println` is sufficient.
2. **The worker never writes a non-JSON line to stdout.** For the duration of a
   member, both stdout and stderr are redirected at the fd level into the
   member's log (the mechanism above), and the `result` line is written only
   after the streams are restored — so no `Wflow.run` print statement can reach
   the protocol stream even in principle. Between members, the worker's only
   stdout writes are protocol lines; everything else goes to its spawn-time
   stderr, the worker log. **This is the protocol's sharpest edge and it is an
   implementation falsifier** (§12, C-6).
3. **`protocol` is checked on handshake.** A mismatch is a hard failure with a
   named message, not a best-effort continue.
4. **EOF on stdin is an implicit `shutdown`.** `eachline(stdin)` terminates and
   the worker exits 0 — so killing the orchestrator cannot leave orphan workers
   waiting forever.
5. **`request_id` correlates**; because only one request is in flight, a mismatch
   is a protocol violation (respawn the worker, mark the member `class=worker`),
   not a routing problem.
6. **The worker never touches the ledger, the lock, or any `_state/` path.**

Probe transcript (§11.2, PR-5) — the exact shape above, Wflow not loaded:

```
{"type":"ready","worker_id":1,"pid":5324}
{"type":"result","status":"ok","echo":"{\"type\":\"run\",\"member_id\":\"rlz_1/cst_3\"}","seconds":0.003}
{"type":"result","status":"error","echo":"{\"type\":\"run\",\"member_id\":\"FAIL_case\"}","seconds":0.0}
{"type":"bye"}
```

### 6.3 Worker lifecycle

| Phase | Behaviour |
|---|---|
| **Spawn** | The slot spawns its worker **lazily** — on its first member, never at sweep start. A no-op resume must not pay `p × F ≈ 3 × 24 s` to discover it has nothing to do (§7.3, C-2). The worker's `stderr` at spawn is the per-worker lifecycle log `_worker_<id>.log` (§6.2) — a file handle, never a `PIPE` |
| **Handshake** | Wait for `ready` with a bounded timeout (default 300 s, config-free constant sized for a cold `using Wflow` on a loaded box). Timeout ⇒ kill, one respawn, then fail the sweep with a named message |
| **Health** | Liveness is the response itself. No heartbeat: a strict request/response protocol makes a hung worker indistinguishable from a slow member, and Wflow members legitimately run for minutes. A per-member wall-clock ceiling is **not** imposed in v2.0 — sized wrongly it kills good work (§15, R-4). The hang class this leaves open is *bounded* instead by §6.2's stderr rule, which removes the only mechanism by which a healthy worker was known to be able to block forever |
| **Crash** | Worker exit before answering ⇒ the slot records `failed`/`class=worker` with the exit code, respawns once, and re-claims if `attempt < member_max_attempts`. Two consecutive spawn failures on one slot retire that slot; the sweep continues on the remaining workers with a warning, and fails only if all slots retire (F12, gated by GF-17) |
| **Recycle** | `worker_max_members` (default `0` = unbounded): after serving N members a worker is sent `shutdown` and respawned, with the slot's Python process untouched. Cost when it fires is one `F ≈ 24 s`; benefit is a hard bound on accumulated `Wflow.run` state and Julia GC growth across a long session. It exists because the fixture **cannot** exercise pool depth (§2.2): each session serves ~4 members there, while a production sweep serves hundreds, and neither A4's numerical identity nor H4's process stability has evidence at that depth. Shipping the knob pre-designed converts R-8 from a hope into a setting the first production sweep can turn |
| **Drain** | When the pending set empties, the parent sends `stop` to each slot as it reports `ready` (§6.1); the slot sends its worker `shutdown`, waits for `bye` with a short timeout, then closes stdin, `wait()`s, and exits 0 |
| **Shutdown on orchestrator failure** | The orchestrator's `finally` terminates every slot; each slot's `finally` closes its worker's stdin (rule 4 above) and, after a grace period, kills it. A `SIGKILL` of the orchestrator leaves workers to exit on stdin EOF |

### 6.4 Scheduling, `-c N` mapping, resource claims

**`-c N` mapping.** `run_sweep` declares `threads: _cores` — the Snakefile's
**existing guarded binding** (`Snakefile_climate_experiment:486-489`), never the
raw `workflow.cores`, which raises at parse time when cores are unset and would
break `--unlock` and bare `--dry-run` (§4.3). With `snakemake -c 3` the sweep job
gets `threads == 3` and no sibling job runs beside it — correct for a stage that
owns the box; with no `-c`, `_cores` is 1 and the sweep degrades to a single
worker instead of failing. Then:

- `p = sweep_workers` config key, defaulting to `_cores`.
- `M = wflow_threads` config key, defaulting to `4` (today's frozen value).
- Total Julia thread demand is `p × M`, which **oversubscribes on purpose** and
  reproduces today's budget exactly: v1 runs 3 concurrent batch jobs each
  `--threads 4` (`Snakefile_climate_experiment:546`) on a 12-logical box.

**The performance-floor protocol depends on holding `p × M` fixed.** P3-3's
frozen triple is `-c 3, --threads 4`; a floor comparison run at any other product
is not a comparison. §13 step 8 states the protocol. **The `p × M` budget binds
the *floor check only*.** The identity gate (C-7) deliberately runs **both** legs
at `sweep_workers = 1` and varies `worker_max_members` (1 vs 0) — session depth,
the variable it is testing, with concurrency and oversubscription held fixed
(§9.6); those runs make no performance claim and are not compared against P3-3.

**Scheduling: greedy, parent-pushed, work-stealing-equivalent by construction.**
The parent holds one pending deque ordered so that (a) `cst_0` baselines come
first — they are inputs to nothing, but they are the members most likely to
expose a systematic failure early — and (b) the rest in realization-major order.
*(Rule (a) is inert on the tracked fixture, which has `ST_START = 1` and
therefore no `cst_0` members; it applies only to a `run_historical: true`
configuration.)* The parent assigns the head of the deque to each slot that
reports `ready` (§6.1's claim-before-dispatch sequence). There is no static
partition, so no LPT assignment is needed and no straggler is stranded behind a
partition boundary — the same greedy property v2's shared queue gave, now with a
recorded owner for every in-flight member: this is precisely what batching could
not do (P3-3 estimator, `dev/scripts/estimate_batch_makespan.py`, whose whole
subject is the makespan cost of a *static* partition).

**Resource claims** are one line: an exclusive claim on
`{exp_dir}` for the **whole workflow's** duration, realized as
`_state/experiment.lock` (§6.6). No
`shared_read`/`shared_write` algebra — the only shared mutable resource in reach
is the experiment tree itself, and it is claimed exclusively. The historical
store is a read-only input, which `cst-run-control` explicitly classifies as an
input rather than a shared resource.

### 6.5 Logging and benchmark capture

**Per member, not per batch** (G4). The runner writes:

| Artifact | Path | Content |
|---|---|---|
| Member log | `{exp_dir}/logs/_parts/3.08_run_sweep/rlz_<n>_cst_<m>.log` | the member's four sub-steps: the `Rscript` perturbation stdout/stderr (including §9.1's `verbose = TRUE` inertness warning), the downscale output, the simulate step's stdout+stderr — **appended by the worker itself** via the `log` path in the `run` message (§6.2), so it is this member's output whatever worker session served it — and the verification result. Written sequentially, one holder at a time (§6.2) |
| Worker lifecycle log | `{exp_dir}/logs/_parts/3.08_run_sweep/_worker_<id>.log` — the worker's spawn-time `stderr` (§6.2) | handshake output, between-member Julia warnings, crash backtraces outside a member window. Picked up by `merge_logs`' directory walk like any part; `_natural_key` sorts `_orchestrator` → `_worker_<id>` → `rlz_…`, so the lifecycle logs read as front matter |
| Orchestrator log | `{exp_dir}/logs/_parts/3.08_run_sweep/_orchestrator.log` — **inside the member directory**, and it is the rule's `log:` | plan banner, per-member assignment/ack/finish lines (§6.1), worker lifecycle events, the finalization summary |
| Rule benchmark | `{exp_dir}/benchmarks/_parts/3.08_run_sweep.tsv` | Snakemake's own row for the whole sweep job — **the only benchmark part 3.08 writes** |

**One label, one shape — otherwise every per-member log is silently dropped.**
`merge_logs._members` tests the flat `<label>.log` **first and returns early**:

```python
flat = os.path.join(parts_dir, f"{label}.log")
if os.path.isfile(flat):
    return [(None, flat)]
```

(`blueearth_cst/shared/merge_logs.py:106-108`.) v1 wrote *both*
`_parts/3.08_run_sweep.log` (the rule's `log:`) and
`_parts/3.08_run_sweep/<member>.log`, and asserted they would merge with no
change to `merge_logs`. They would not: no label in any of the three workflows
has both forms today, 3.08 would have been the first, and the directory walk is
never reached when the flat file exists. Every per-member log would be excluded
from `wf3_climate_experiment.log`; and because dropped paths never enter
`merged`, `_remove_parts` (`:139-141`) would never delete them, so
`_parts/3.08_run_sweep/` grows without bound and the documented "one file in
`logs/` after a clean run" invariant (`Snakefile_climate_experiment:182-188`)
breaks. That is a silent loss of exactly the per-member visibility G4 exists to
deliver. v2 therefore gives the label **one** shape: the orchestrator log moves
*inside* the part directory as `_orchestrator.log`. `_natural_key`
(`merge_logs.py:64-71`) sorts `"_orchestrator"` before `"rlz_…"`, so it merges
first and reads as the section header it is. No change to shared code, one new
label in `LOG_RULES`. The alternatives — two labels, or teaching `_members` to
union both — are rejected: the first splits one rule's output across two merged
sections, the second changes cross-workflow shared code and needs its own test
for a problem a path choice solves.

**Per-member benchmark TSVs are dropped; the ledger is the per-member record.**
v1 wrote both `_parts/3.08_run_sweep.tsv` (the job) and
`_parts/3.08_run_sweep/*.tsv` (the members), and `merge_benchmarks`' recursive
glob (`blueearth_cst/shared/merge_benchmarks.py:55-59`) genuinely absorbs both —
which is the problem: its `TOTAL` row sums the `s`/`io`/`cpu` columns
(`:19,81-83`), so the sweep's wall time would be counted **twice**, once as the
job row and once as the members that constitute it. v1 has no such overlap (3.10
contributes batch rows only), so this would be a new reporting regression in the
very artifact §6.5 exists to discuss. Since the ledger's `seconds` object is
already finer than a benchmark row (four sub-steps, not one total) and is
**authoritative** for §13 step 8's floor check, the member TSVs buy nothing and
are not written. `merge_benchmarks` is untouched.

**Honesty note on the remaining benchmark columns.** The `NA` resource columns on
the job row are not a regression: on Windows they are `NA` today unless
`patch_psutil_windows_benchmark` is active
(`Snakefile_climate_experiment:14`), and that patch instruments Snakemake's own
job wrapper, which the runner's sub-steps do not go through.

### 6.6 Forcing lifecycle, the `p × 1` disk claim, and the lock

**One member, start to finish** (the fusion of today's 3.05 + 3.07 + 3.09 + 3.10):

| # | Step | Writes | Deletes | Cost class |
|---|---|---|---|---|
| 1 | Write the member spec | `_state/members/rlz_<n>/cst_<m>/weagen.yml` (the retired 3.05's payload) | — | ms |
| 2 | **perturb** — `Rscript --vanilla blueearth_cst/weathergen/impose_climate_change.R <baseline_nc> <weagen.yml> <cst_m.csv>` | `weather_generator/output/rlz_<n>_cst_<m>.nc` (WG-4, path unchanged) | — | ~6 % of sweep wall (OQ-1 §9.1) |
| 3 | **downscale** — `downscale_climate_forcing.py`'s body, in-slot | `hydrology_runs/rlz_<n>/forcing/inmaps_cst_<m>.nc` (WG-6), `hydrology_runs/rlz_<n>/config/cst_<m>.toml` (HM-4, **persistent**) | the WG-4 NC from step 2 | tens of s |
| 4 | **simulate** — `{"type":"run", …}` to the slot's worker | `hydrology_runs/rlz_<n>/output/cst_<m>.csv` (HM-5, **persistent**), `outstates_cst_<m>.nc` (HM-6b) | — | `S_warm ≈ 35 s` |
| 5 | **verify** — CSV exists, parses, ≥ 1 row; digest it | — | the WG-6 forcing, the HM-6b state, the member spec dir | ms |
| 6 | **record** — the slot returns the outcome; the parent appends the ledger row | `_state/ledger.jsonl` | — | ms |

**The baseline branch (`baseline: true` / `st_csv: null`), normative.** The
table above is the *perturbed*-member lifecycle. Manifest members with
`baseline: true` — the `cst_0` members a `run_historical: true` configuration
admits; the tracked fixture has none — take a distinct branch, mirroring what
the retired rules already did (rule 3.07 constrains perturbation to
`st_num >= 1`, `Snakefile_climate_experiment:403-404`, and rule 3.09
downscales `cst_0` **directly from generation's output**):

- **Steps 1 and 2 are skipped entirely.** No member spec is written
  (`_state/members/<id>/` is never created for a baseline member) and
  `impose_climate_change.R` is never invoked — there is no stress CSV to read
  (`st_csv: null`) and nothing to perturb.
- **Step 3 downscales the persistent baseline NC directly** —
  `weather_generator/output/rlz_<n>_cst_0.nc`, the manifest's
  `realizations[].baseline_nc` — and its "delete the WG-4 NC from step 2"
  action is **vacuous by construction**: no step-2 output exists, and the
  baseline NC is *not* a member transient. Steps 4–6 are unchanged, producing
  `cst_0.toml` / `cst_0.csv` on the same paths.
- **The baseline NC is never deleted at any lifecycle point** — not by step 3,
  not by step 5, not by the resume fold's RUN-set transient cleanup (§7.3 step
  8), and not by the quarantine inventory (§5.3). It is stage 2's persistent
  product (an approved anchor, §2.1) and a declared input of rules 3.07/3.08;
  a baseline member's **transient set is exactly `{WG-6 forcing, HM-6b
  state}`**, nothing else.
- **The ledger records the branch honestly:** `inputs.st_csv = null`,
  `inputs.weagen_template = null` (defined-absent, §5.2/§5.5), and `seconds`
  omits `perturb`.
- `retain_member_artifacts: true` suppresses the step-5 deletions as for any
  member; for a baseline member step 3 has nothing to suppress.

Gate: **GF-21** exercises this branch end-to-end on an untracked scratch
config variant without touching the tracked fixture (§8.2); claim **C-23**.
Without the branch, any supported `run_historical: true` run either fails
reading the null stress CSV or destroys the persistent baseline NC — while
every fixture-scale gate stays green, because the fixture cannot reach the
branch.

Step 3's deletion is what caps the co-resident set: the WG-4 NC and the WG-6
forcing never both persist past the downscale. So

> **Peak transient disk = `p × max(WG-4 NC, WG-6 forcing + HM-6b state)`** — a
> constant in `p`, independent of `RLZ_NUM × ST_NUM`.

At fixture scale that is `3 × ~10 MB ≈ 30 MB`, against P3-3's measured
`120.59 MB` peak at `B=4` (P4). The `dev/followups.md` § Post-P3-3 disk-aware
`batch_size` problem is **dissolved**: there is no `B`, and the ceiling no longer
scales with sweep size, so no per-run size estimate is needed at parse time.

**G3 is a per-invocation peak, not a tree invariant — and the difference needs a
sweeper.** The derivation above holds *within a completed member*. A crash
between step 2 and step 3's deletion, or between step 4 and step 5's, leaves the
WG-4 NC / WG-6 forcing / HM-6b state on disk with **no ledger record and no
owner**: §7.3's fold quarantines *recorded* outputs and reports *orphan member
results*, and `prune_experiment_orphans.py` is scoped to member CSVs and TOMLs
(§7.4). After N interrupted sweeps a tree therefore carries up to `N × p` stale
transients — on a large basin the biggest files in the tree, and exactly the
class `dev/followups.md` § Post-P3-3 flagged as the binding constraint. C-3
samples peak disk during *clean* runs, so it cannot observe the accumulation.
Two closures, both cheap:

- **The resume fold deletes the member's transient set for every member it
  classifies RUN, before re-claiming.** The paths are all derivable from
  `member_id` (§6.6's table), so this is a few lines and it makes the ceiling
  self-healing across crash/resume cycles.
- **`prune_experiment_orphans.py` covers the transient classes too** (WG-4
  perturbed NCs, WG-6 forcings, HM-6b states, `_state/members/<id>/` spec dirs)
  in addition to member CSVs and TOMLs, under the same report-by-default,
  `--delete`-is-an-owner-action rule.

G3 is restated accordingly: **peak transient disk within one invocation is
`p × 1` member by construction; across invocations the fold's cleanup is what
keeps it there.**

`retain_member_artifacts: true` suppresses the deletions in **step 3 *and* step
5**. Both matter: step 3 deletes the WG-4 perturbed NC, which is precisely
`validate_wg4`'s on-disk integration operand
(`dev/contracts/weather-generator-seam.md:312,383`). v1 named step 5 only, which
would have left that validator's case permanently skipped after `--notemp` stops
working — the "gate that would otherwise silently break" §10a exists to prevent,
breaking anyway — and §13 step 7's "capture to un-skip the three temp validators"
would have un-skipped two. This is the **replacement for `--notemp`** (§10): a
Snakemake flag cannot suppress a delete the runner performs.

**The experiment lock, claimed for the whole workflow.** v1 claimed
`_state/sweep.lock` inside `run_sweep.py` — that is, at **stage 3**, three stages
too late for the property the lock's own rationale claims. A concurrent
invocation from a second worktree would run stages 1, 2 and 4 entirely
unguarded: 3.01 rewrites `members.json`, 3.05/3.06 rewrite the now-**persistent**
baseline NCs, and 3.09 rewrites the indicator tables. If that second invocation
carries a config edit — the realistic case, since it is why a second worktree
exists — it regenerates the baselines *while the first sweep's perturb step is
reading them*, giving torn NC reads recorded as `stage=perturb` (i.e.
misattributed to the member), or a member perturbed from a half-written baseline
that still opens. Persisting the baselines, an approved anchor, is what makes
this reachable; under v1 they were `temp()` and shorter-lived.

v2 therefore has **one** lock, `_state/experiment.lock`, claimed for the whole
workflow:

| | |
|---|---|
| Claimed | Snakemake's `onstart:` handler, before any job runs |
| Released | `onsuccess:` and `onerror:` |
| Primitive | `os.open(..., O_CREAT\|O_EXCL\|O_WRONLY)` — atomic on both platforms |
| Contents | `{invocation_id, pid, pid_create_time, host, started_at, config_path, experiment}` |
| On conflict | `onstart` raises with the holder's pid/host/started_at; **no job runs** (PR-7) |

The handler set is the right home because it runs in the **Snakemake main
process** — the one process alive for the entire workflow, so its pid is a
meaningful liveness token. PR-7 (§11.2) probe-verified all three properties this
rests on: `onstart` does not run on `--dry-run`; a raise in `onstart` aborts
before any job executes; and neither `onsuccess` nor `onerror` runs when
`onstart` itself raised — so a process that *failed* to claim the lock can never
release someone else's.

**The lock-minted `invocation_id` is authoritative, and the handoff to the
runner is defined, not implied.** `onstart` mints the uuid4 exactly once and
writes it into the lock's JSON contents (the table above). `run_sweep.py`, as
its first action (§7.3 step 1), **reads `_state/experiment.lock` and adopts
its `invocation_id`** for every ledger row, quarantine generation, and
finalization artifact it writes — the runner never mints an id of its own,
which is what removes v3's incompatible scopes (a lock id and an independently
minted runner id could disagree, making the runner reject every sweep). **If
the lock is absent or unparseable at that read**, the runner hard-fails with a
named error (`ExperimentLockMissingError`: the sweep must run under the
workflow whose `onstart` claims the lock; an absent lock means either
out-of-workflow execution or a mid-run deletion, and neither is a state to
continue from) — it never falls back to minting. The runner performs no other
lock verification: creation, conflict detection, release, and stale-clearing
all belong to the handlers and to `--clear-lock` below.

Rationale, unchanged: Snakemake's own workdir lock is scoped to the **repository
checkout**, and this repo's standing policy is `worktree_policy: always` with
several concurrent sessions — two worktrees pointed at one `project_dir` slip
past Snakemake's lock entirely and would interleave writes into the same
experiment tree. This is `cst-run-control`'s namespace claim at the depth the
risk justifies.

**Stale-lock liveness, and the recovery command that v1 never named.** A hard
kill leaves the lock behind by construction — the release handlers never run. v1
then refused to auto-clear a lock whose pid was dead, and told the user "the
message names the recovery command" without naming one, so F5's hard-kill
recovery landed straight in F11's refusal and GF-2 — the **only** gate for G2,
the milestone's headline claim — could not reach its stated observation. v2:

1. **Liveness is pid *plus* process creation time.** Pid alone is a weak test on
   Windows, where pid reuse is routine; the recorded `pid_create_time` is the
   tiebreak. The holder is provably gone when the pid is dead, **or** alive with
   a different creation time.
2. **A provably-gone holder is auto-cleared**, with one log line recording what
   was cleared and why. This is not "inferring liveness from a timeout" — the
   thing `cst-run-control` refuses — it is a positive observation that the
   recorded process no longer exists.
3. **Anything else is refused**, naming the holder and the explicit override:
   `python scripts/sweep_status.py <exp_dir> --clear-lock`, which prints the lock
   record, requires the holder to be non-live, and removes it. That is the
   command §6.3, F11 and GF-2 all now name.

**One recovery block, because three findings land here.** After a hard kill the
documented sequence is exactly:

```powershell
# 1. Snakemake's own workdir lock (repository-scoped). Works with no -c only
#    because rule 3.08 uses the guarded _cores binding, not workflow.cores (§4.3).
pixi run snakemake --unlock -s Snakefile_climate_experiment --configfile <cfg>
# 2. The experiment lock (project-scoped). Usually unnecessary: step 3 auto-clears
#    it when the recorded holder is provably gone. Needed only if it refuses.
pixi run python scripts/sweep_status.py <exp_dir> --clear-lock
# 3. Resume. Only members without a succeeded row run.
pixi run snakemake all -c 3 -s Snakefile_climate_experiment --configfile <cfg>
```

---

## 7. Resume and freshness

### 7.1 The drift guard, post-fusion

Three layers, in execution order:

1. **Parse time** — the guarded-section digest is a `params:` value of 3.01
   (unchanged mechanism, `Snakefile_climate_experiment:143-163`). An in-place
   edit to any guarded value re-runs the manifest rule and, through the manifest,
   everything downstream.
2. **Manifest time** — 3.01 runs `compare_project_consistency` and refuses to
   write the manifest on divergence. Because the manifest is the sentinel every
   downstream rule takes as input, a failed guard blocks the whole workflow, as
   `.project_consistency_ok` does today. **The 3.00b failure modes still fail
   loud** (success criterion 6), with the same messages.
3. **Sweep time** — the runner re-verifies `wf1_snapshot_digest`,
   `wf2_snapshot_digest` and `guarded_sections_digest` against the live files
   *before claiming any member*. This closes the window the DAG cannot see: a
   snapshot edited *after* the manifest was written but *before* the sweep ran.
   Divergence here is a hard failure naming the changed comparand.

Layer 3 is the intake's "the sweep runner verifies them at start"; layers 1–2 are
the retained 3.00b mechanism, folded into the manifest rule so there is one
sentinel rather than two artifacts. **This three-layer reading was RATIFIED at
G1**; it is settled framing, not an open interpretation. (The reason it needed
ruling: replacing 3.00b outright with layer 3 would leave stages 1–2 —
generation, the expensive stage — unguarded, and success criterion 6 requires the
3.00b failure modes to still fail loud.)

**A fourth, member-scoped check runs in the same pass** and is not part of the
drift guard, but shares its position: the runner digests each baseline
`rlz_<n>_cst_0.nc`, each `cst_<m>.csv` and the generator template **once**, and
those digests feed §5.5's reuse condition 5. Drift layers 1–3 protect *the
project's identity*; condition 5 protects *each member's inputs*. Both are
sweep-start, both are cheap, and neither substitutes for the other.

### 7.2 What Snakemake decides (probe-grounded)

Probes PR-2 / PR-3 (§11.2) pin the two cases:

| Situation | Snakemake's decision | Probe |
|---|---|---|
| `ledger_final.csv` present, params and inputs unchanged | `Nothing to be done (all requested files are present and up to date).` — the sweep rule is not entered at all | PR-2 |
| A params value changed (any digest in §5.1) | `reason: params have changed since last execution: sweep` — the rule re-runs | PR-3 |
| A rule failed | Snakemake removes the **declared** outputs of the failed job only; the undeclared `ledger.jsonl` survives | PR-4 |
| Hard kill (`SIGKILL`) mid-sweep | `ledger_final.csv` never written; `.snakemake/incomplete/<b64 path>` recorded; `.snakemake/locks/` left in place; `ledger.jsonl` intact with every fsync'd row | PR-6 |
| Re-invocation after a hard kill | `reason: output files have to be generated: sweep` — clean, no `--rerun-incomplete` demanded. A **real** (non-dry) invocation needs `--unlock` first, which `AGENTS.md` § Workflow already documents | PR-6 |

**The consequence:** Snakemake's freshness is *coarse* — the sweep either runs or
does not. Member-level incrementality lives entirely in §7.3. A resume is a
re-invocation of a sweep rule that Snakemake believes has never completed, which
is exactly true.

**And it composes badly with `allow_partial`, unless the declared output's
freshness carries completeness.** Compose row 1 with §9.4: once a partial sweep
*finalizes*, `ledger_final.csv` exists and params are unchanged, so re-invoking
reports `Nothing to be done` and **never retries the failed members**. The holes
freeze until the user manually deletes the declared output or forces the rule —
a recovery step v1 named nowhere. The user story is the common one:
`allow_partial` exists precisely for runs expected to be re-attempted, so a
scientist takes a first look, fixes the fault, re-runs, and gets the same
incomplete surface plus a workflow claiming it is up to date, while
`sweep_completeness.csv` still names the hole. That directly contradicts G2.

The fix keeps the declared-output set constant (which is what keeps `--dry-run`
honest) and puts completeness into the rule's **freshness** instead:

| | |
|---|---|
| Artifact | `_state/sweep_incomplete.json` — `{invocation_id, incomplete: [member_id, …]}` |
| Written | on an accepted-but-incomplete termination, with a **fresh `invocation_id` every time** |
| Deleted | on a complete termination |
| Wired | `params.incomplete_digest = file_digest_or_absent({exp_dir}/_state/sweep_incomplete.json)` on rule 3.08 |

Behaviour, which terminates by construction: a complete sweep leaves the marker
absent, so the param reads `ABSENT` on every subsequent invocation and the rule
stays quiet. A partial sweep leaves a marker whose digest differs from the
previous invocation's — because the `invocation_id` inside it is fresh — so the
**next** invocation always re-enters the rule and the runner re-runs exactly the
non-`succeeded` members, whether or not the previous attempt's failure set was
identical. Once the sweep completes, the marker's deletion flips the param back
to `ABSENT`, which re-enters the rule **once** more; that pass is a no-op resume
(§7.3 step 6, ~15 s by C-2) and then the state is stable.

Two second-order effects, stated so an implementer does not read them as bugs:
(1) that single extra no-op re-entry after the first complete run; (2)
`ledger_final.csv` is rewritten on every partial invocation, so 3.09 re-runs each
time — which is **correct**, because the surface genuinely changed. GF-13 gates
the whole loop.

### 7.3 What the runner decides — the resume fold

On entry, before spawning any worker:

```
1. read _state/experiment.lock and ADOPT its invocation_id  (minted in onstart, §6.6;
   absent/unparseable -> ExperimentLockMissingError, never mint a fallback)
2. verify the three drift digests                          (§7.1 layer 3)
3. read members.json                                       (the immutable intent)
4. digest the live inputs ONCE: each baseline rlz_<n>_cst_0.nc,
   each cst_<m>.csv, the generator template          (RLZ_NUM + ST_NUM + 1 files)
5. re-read the four `tools` versions; warn per drift        (§9.2, C-13)
6. fold ledger.jsonl under the crash-consistency rules      (§5.3, incl. transition legality)
7. per member, classify:
     no rows for this member_hash                          -> RUN
     last = succeeded AND all five reuse conditions hold    -> SKIP        (§5.5)
     last = succeeded, artifact missing or OUTPUT digest bad-> QUARANTINE, RUN
     last = succeeded, INPUT digest mismatch (step 4)       -> QUARANTINE, RUN
     last = claimed (interrupted)                           -> QUARANTINE, RUN
     last = failed                                          -> RUN   (new invocation)
     member_hash differs from every ledger row              -> QUARANTINE, RUN
   members on disk not in the manifest                      -> ORPHAN: ignore + report
8. for every member classified RUN: delete its transient set (§6.6; for a
   baseline member that is {WG-6 forcing, HM-6b state} ONLY — the persistent
   baseline NC is never in any transient set) before re-claiming
9. if the RUN set is empty: finalize and exit 0             (no worker is ever spawned)
10. else: spawn slots lazily and execute
```

Step 4 is what makes the sweep's incrementality a statement about members rather
than about their outputs (§5.5); step 8 is what keeps G3's disk ceiling true
across crash/resume cycles (§6.6). Both run before any worker spawns, so C-2's
no-op cost claim is unaffected — they are `RLZ_NUM + ST_NUM + 1` digests and a
directory scan, not a `using Wflow`.

Step 9 is load-bearing. The manifest is a declared `input:` of the sweep, so any
config edit **that changes a parsed value covered by `config_digest`** rewrites
it and fires the mtime trigger even when no member field changed — Snakemake will
re-enter the sweep rule for reasons that are not member-relevant. (A comment-only
edit changes no parsed value and therefore re-enters nothing; GF-11's injection is
specified accordingly.) The re-entry is accepted rather than engineered around
(content-stable
writes are the clever option and the fragile one), **on the condition that the
no-op path costs one Python start and no `using Wflow`**. §12, C-2 makes that a
falsifiable claim with a number.

### 7.4 Quarantine and orphans

**Quarantine is retention.** Superseded or unverifiable member artifacts move to
`_state/quarantine/<invocation_id>/<member_id>/` (preserving the relative path),
never `unlink`. A ledger `quarantined` row records what moved and why. This is
`cst-run-control` references/resume.md's quarantine-before-resume, at member
granularity.

**Orphans** — member CSVs/TOMLs on disk that no manifest member claims, typically
from a reduced `RLZ_NUM` or `ST_NUM`. Under v1 they were harmless because the
reduce's `expand()` never named them. Under a ledger-driven reduce the policy
becomes ours and must be explicit:

- Orphans are **ignored** by the sweep and the reduce — never consumed, never
  counted, never silently folded into a response surface.
- Orphans are **reported**: a count in the sweep log and one row per orphan in
  `sweep_completeness.csv` with `state=orphan`.
- Orphans are **never auto-deleted.** A `dev/scripts/prune_experiment_orphans.py`
  (reporting by default, `--delete` an explicit owner action) mirrors
  `dev/scripts/prune_series_cache.py`, and inherits its hard ordering rule from
  `AGENTS.md`: **it must run before any reference snapshot**, or the snapshot
  bakes the orphans in and the gate compares them instead of the live set. Its
  scope covers **member products** (CSVs, TOMLs) **and transients** (WG-4
  perturbed NCs, WG-6 forcings, HM-6b states, `_state/members/<id>/` spec dirs),
  per §6.6 — the transient classes are the large ones on a real basin.
- **Pruning never rewrites history, and history never depends on pruning.**
  `--delete` removes *artifacts*; the append-only ledger is untouched, and the
  legality of the deleted members' historical rows is **independent of live
  artifact existence** (§5.3's legal-history rule): a schema-valid
  sub-sequence for a member absent from the current manifest is legal whether
  its artifacts survive or were pruned. "Orphan" in *this* section is a
  disk-reporting category (an artifact with no manifest owner), not a legality
  predicate — after pruning, the completeness record simply carries no
  `state=orphan` rows, and the next invocation folds cleanly. GF-23 gates the
  full resize→prune→reinvoke composition; C-26 is the claim.
- **`dev/scripts/` is the right home for this one** and `scripts/` is the right
  home for `sweep_status.py`. `AGENTS.md` splits the three homes by *invocation
  model*: `dev/scripts/` "inspects or maintains the **repository** and is never
  part of a run"; `scripts/` is "what a user runs". Pruning mirrors
  `prune_series_cache.py` exactly; a status command a user runs against their own
  `project_dir` mid-run does not (§7.5).

### 7.5 `--dry-run` honesty, and what replaces the lost visibility

**Stated plainly: `--dry-run` cannot report pending members, and this design does
not pretend otherwise.** It reports at rule granularity — "run_sweep will run"
or "Nothing to be done" — because member state lives in a file Snakemake does not
track. That is a real loss against v1, where `--dry-run` listed every pending
`(rlz, cst)` job.

Three things replace it:

1. **`scripts/sweep_status.py <exp_dir>`** — reads manifest + ledger and prints
   the member table (`done / pending / failed / quarantined / orphan`), with
   `--json` for machine use, `--clear-lock` for the stale-lock recovery (§6.6),
   and **`--verify`** — the explicit integrity command (§4.4): recompute the
   `sha256` of every output `ledger_final.csv` records (falling back to the
   folded ledger when no finalized sweep exists), exit nonzero naming each
   diverged member with its recorded and live digests, and print the repair
   lever (`delete {exp_dir}/_state/ledger_final.csv and re-invoke`). Read-only;
   it moves nothing. It lives in `scripts/`, not `dev/scripts/`: `AGENTS.md`'s three-homes
   split (O-23) is by invocation model, and this is the one artifact whose whole
   purpose is to be run by a *user* against their own `project_dir` mid-run.
   Misfiling it under `dev/scripts/` would make the compensation for the removed
   DAG visibility less discoverable to the audience it exists for. It is strictly
   *more* informative than v1's dry-run, because it distinguishes failed from
   pending; it is *less* available, because it needs a manifest on disk. It opens,
   reads and closes — it never holds a handle across a sweep (§5.3).
2. **The sweep's plan banner**, printed before the first member and captured in
   the log: `12 members: 9 done, 2 pending, 1 failed (rlz_1/cst_4: simulate)`.
3. **The completeness record** (§5.2), which persists the same information for
   the reduce and for any downstream consumer.

**The honest summary for a reviewer:** the DAG loses per-member visibility and
gains a first-class status command; the trade is stated, not hidden, and
`sweep_status.py` is a *required* deliverable of the milestone, not a nice-to-have
(§13, step 4).

### 7.6 What forces full invalidation

| Change | Effect |
|---|---|
| Any guarded section (`project`, `shared.basin`, `workflows.model_creation`, `workflows.climate_projections`) | Guard fails or manifest rewrites; per repo policy the experiment must be re-run against the correct project |
| `run_length`, `horizontime_climate`, `clim_historical`, `data_sources`, the base `wflow_sbm.toml`, `staticmaps.nc` | `run_config_digest` changes ⇒ **every** `member_hash` changes ⇒ full sweep, all prior members quarantined |
| `realizations_num` increased | New realizations generate; existing `member_hash`es unchanged ⇒ **only the new members run** |
| `realizations_num` decreased | Surplus members become orphans (§7.4) |
| Any `stress_test.*` key (incl. `step_num`, `precip.variance.*`) | `st_params_digest` changes and most members' `tavg`/`prcp` scalars change ⇒ mostly-full sweep. *(Honest, not a defect: index-based member ids are not stable under a grid resize — §9.3 prices it. For the inert variance keys specifically, §5.1 names the false invalidation as an accepted cost of the OQ-1 deferral)* |
| One `cst_<m>.csv` **file** edited on disk, with no config change | Hand-editing a generated WG-2 file is **out of contract** — the file is derived from `stress_test.*`. It is nonetheless caught: the recorded `inputs.st_csv` digest mismatches at sweep start, so exactly that column of members quarantines and re-runs (§5.5 condition 5). The *config*-driven path is the row above |
| `master_seed`, or any key in `config/templates/weathergen_config.yml` | `seed_r` / `weagen_template_digest` change ⇒ **every** `member_hash` changes ⇒ regeneration **and** a full sweep, with every prior member quarantined. *(v1 asserted this row while `member_hash` could not see either input — the trace and the repair are in §5.1. GF-12 is its gate.)* |
| A baseline `rlz_<n>_cst_0.nc` whose bytes change with no config change | Not visible to any hash — caught by `inputs.baseline` at sweep start: that realization's members quarantine and re-run |
| `aggregate_rlz`, `Tlow`, `Tpeak` | **Reduce only.** No member invalidates; only 3.09 re-runs |
| `sweep_workers`, `wflow_threads`, `member_max_attempts`, `worker_max_members`, `retain_member_artifacts`, `allow_partial` | Recorded in the manifest but **excluded from `member_hash`** — they are execution policy, not science. A worker-count change must not invalidate a sweep |

That last row is a deliberate asymmetry with `run.policy` being *inside*
`members.json`: the manifest records policy for provenance, and `member_hash`
covers only result-affecting fields.

## 8. Failure modes, recovery, and the failure-injection gate set

### 8.1 Failure modes and recovery

| # | Failure | Blast radius | Recovery |
|---|---|---|---|
| F1 | One member's Wflow run errors (`class=member`) | **1 member.** No sibling artifact is deleted — nothing sibling is a declared output (§3.2) | Fail-loud: the sweep does not write `ledger_final.csv`; the reduce is blocked. The failed member is named in the **surviving undeclared** `_state/sweep_completeness.csv` and in `ledger.jsonl`. Fix the cause and re-invoke — the sweep re-enters (its declared output is absent) and runs only the non-`succeeded` members. Under `allow_partial`: the sweep finalizes with the hole recorded (§9.4), writes `_state/sweep_incomplete.json`, and the **next** invocation re-enters on the changed `incomplete_digest` param and retries the hole (§7.2). No manual deletion of `ledger_final.csv` is required in either branch |
| F2 | The perturbation or downscale step errors | 1 member, `stage=perturb\|downscale` | as F1 |
| F3 | A Julia worker crashes mid-member | 1 member + 1 worker | member recorded `class=worker`; worker respawned; member re-claimed while `attempt < member_max_attempts` |
| F4 | A slot process dies | its in-flight member | the parent's sentinel fires; it drains the slot's pipe (a fully-sent `result` still counts), then reads the in-flight member **from its own assignment table** — recorded, with the `claimed` row fsync'd, before dispatch (§6.1) — records `failed`/`class=worker` for that member, requeues it within `member_max_attempts`, and respawns the slot (worker included). No inference, no hang, no lost member: W2/W3 in §6.1's window table |
| F5 | Orchestrator hard-killed | the in-flight `p` members | `ledger.jsonl` survives with every completed member (PR-6); follow §6.6's three-line recovery block (`--unlock`; the experiment lock auto-clears, or `--clear-lock`; re-invoke); interrupted members quarantine and re-run |
| F6 | Torn final ledger line | none | dropped silently on read (§5.3) |
| F7 | Corrupted (non-final) ledger line, **or an illegal transition sequence** | the sweep refuses to start | named line number(s) + the quarantine command |
| F8 | A member CSV on disk diverges from its recorded digest | 1 member | Three detection points, each tied to something actually executing: **(1)** any sweep re-entry — reuse condition 4 fails, quarantine + re-run (§5.5); **(2)** any reduce execution — digest verification before reading, hard-fail naming the member (§4.4); **(3)** on demand — `sweep_status.py --verify` (§7.5). **Stated honestly: after a clean sweep, an ordinary re-invocation runs neither the sweep nor the reduce (§7.2), so it detects nothing** — the narrowed claim GF-15 now gates. Repair: delete `_state/ledger_final.csv` and re-invoke; exactly the diverged member(s) quarantine and re-run |
| F9 | Drift injected between manifest and sweep | the whole sweep | hard failure naming the changed comparand (§7.1 layer 3) |
| F10 | Two workflows on one experiment | none, if the lock holds | the second invocation's `onstart` fails **before any job runs**, naming the holder's pid/host/started_at (§6.6) |
| F11 | Stale lock (holder gone) | none, when liveness is provable | auto-cleared when the recorded pid is dead **or** alive with a different creation time, with a log line; otherwise refused, naming `scripts/sweep_status.py <exp_dir> --clear-lock` (§6.6) |
| F12 | All workers retire (e.g. Julia missing from `PATH`) | the whole sweep | hard failure; no partial `ledger_final.csv`; the message names Julia and `AGENTS.md`'s juliaup constraint |

**Escalate to the user, do not auto-repair:** F7, a refused (non-provable) F11,
and any case where the manifest's recorded digests and the live files disagree in
a way no legal member transition resolves — legality being evaluated by §5.3's
final (transition-legality) crash-consistency row, which is what makes that
clause operative rather than rhetorical.

### 8.2 The failure-injection gate set

Executable post-implementation; each names its command and the observation that
passes it. Fixture: `config/workflows/snake_config_model_test.yml` against
`test_case/test_local`, **as tracked**: `K = 12`, no `cst_0` members,
`aggregate_rlz: true` ⇒ `Qstats.csv` carries **6 rows per statistic** (one per
`cst` index), whatever `K` is. Every count below is computed against that; v1's
`K = 14` arithmetic assumed `run_historical: true`, which no tracked config sets,
and made GF-6 and GF-7 — the pair that makes the ratified OQ-4 posture testable —
unmeetable as written. `SM` abbreviates
`pixi run snakemake -c 3 -s Snakefile_climate_experiment --configfile config/workflows/snake_config_model_test.yml`.

| Gate | Injection | Command | Expected observation |
|---|---|---|---|
| **GF-1** kill a worker mid-member | while the sweep runs, `Stop-Process -Id <julia pid> -Force` for one worker | `SM` (background) + PowerShell kill | ledger shows `failed`/`class=worker` then `claimed` attempt 2 then `succeeded` for that member; every other member unaffected; sweep exits 0; `semantic_tree_diff --tolerance 0` clean vs the reference tree |
| **GF-2** hard-kill the sweep | after ≥ 2 members complete, a **process-tree** kill: `taskkill /T /F /PID <snakemake pid>`. A bare `Stop-Process -Id <snakemake pid> -Force` does **not** cascade — Windows has no process groups and the orchestrator is a child (`script/__init__.py:857+`) — so it would leave the orchestrator, its `p` slots and the Julia workers running, and the surviving `finally` would tidy up: the gate would not produce the state it is written to produce | `SM`; `taskkill /T /F`; `SM --unlock`; `scripts/sweep_status.py <exp>` (expect: the experiment lock reported stale-and-cleared, or `--clear-lock` named); `SM` | the `--unlock` succeeds **with no `-c`** (the `_cores` fix, §4.3); the stale `_state/experiment.lock` is auto-cleared because its recorded pid+creation-time is provably gone, with one log line; the second invocation runs **only** the members without a `succeeded` row; `sweep_status.py` before the re-run shows exactly that set; the two completed members' CSV mtimes are unchanged. **Extended through successful reduction (C-24):** the second invocation completes the sweep **and the reduce**; `ledger_final.csv` carries **at least two distinct `succeeded_invocation_id` values** (the pre-kill members keep the first invocation's id — mixed-attempt provenance survives finalization, never uniformized) and a **uniform `finalization_invocation_id`** equal to the second invocation's lock id; the reduce's completeness identity check passes against that column and `Qstats.csv` is published with 6 rows per statistic. Falsified by a reduce hard-fail on the mixed rows or by collapsed provenance |
| **GF-3** corrupt a ledger row | append `{"member_id": "rlz_1/cst_2", "event":` (no newline) **and then** a valid row after it, making the broken line non-final | edit `_state/ledger.jsonl`, `SM` | sweep refuses to start; message names the line number and prints the `sweep_quarantine=1` command; **no member runs** |
| **GF-4** truncated tail | append `{"member_id": "rlz_1/cst_2"` with no trailing newline as the **final** line | edit, `SM` | line dropped silently; one log line records the truncation; the sweep proceeds normally |
| **GF-5** config change mid-sweep | edit `run_length` while the sweep runs, then let it finish and re-invoke | `SM`; edit; `SM` | first sweep completes against the manifest it read; second invocation rewrites the manifest (params trigger), every `member_hash` changes, every prior member is quarantined and re-run; `_state/quarantine/<id>/` holds the previous CSVs |
| **GF-6** member failure, fail-loud | temporary guard in `wflow_worker.jl` raising for one `member_id` when `CST_GF6_FAIL` matches (the P3-3 GN-4 method: data-level injection is unreachable because forcing and TOML are both runner-written) | `SM` | sweep exits nonzero; `ledger_final.csv` **absent**; `_state/sweep_completeness.csv` **present** and naming the failed member with `stage=simulate` — the discriminating observation for the undeclared-completeness decision (§5); `Qstats.csv` mtime unchanged; the **11** sibling CSVs present and untouched (contrast GN-4, where `B−1 = 3` siblings were deleted) |
| **GF-7** member failure, `allow_partial` | same guard, `--config allow_partial=true` (top-level, resolved per §4.3 — v1's command reached no key at all and would have exercised **fail-loud**, reporting a false green). Two sub-cases: **(a)** fail one member of `cst_3`, leaving `rlz_2/cst_3` succeeded, so the cell is *partial*; **(b)** fail both members of `cst_3`, so the cell is *missing* | `SM` | sweep exits 0; `sweep_completeness.csv` has 12 manifest rows — 11 `succeeded` + 1 `failed` in (a), 10 + 2 in (b) — each carrying `invocation_id` and `config_digest`; `Qstats.csv` has **5 rows per statistic** in **both** sub-cases (the `cst_3` cell is dropped entirely: never under-averaged, never zero-filled, never a `pd.concat([])` crash); `indicators/completeness.csv` present, naming `cst_3` with `state=partial_cell` (a) / `missing_cell` (b) and `n_present`/`n_expected`; reduce prints a named warning; `response_long.csv` has no `cst_3` rows |
| **GF-8** concurrent workflow | start `SM` from a second worktree against the same `project_dir`, **at any stage** — including while the first is still in stage 1 or 2, with an edited config | two shells | the second fails in its `onstart`, **before any job runs**, naming the holder's pid/host/started_at; the first is unaffected; `members.json` and every baseline NC are byte-unchanged afterwards; the ledger has no rows from the second `invocation_id`. *(Strictly stronger than v1's gate, which claimed the lock at stage 3 and left stages 1, 2 and 4 unguarded — §6.6)* |
| **GF-9** orphan member | complete a sweep at `RLZ_NUM=2`, set `realizations_num: 1`, re-invoke | `SM` | the **6** rlz_2 CSVs untouched on disk; `sweep_completeness.csv` has 6 manifest rows plus **6** `state=orphan` rows; `Qstats.csv` covers rlz_1 only; nothing is deleted |
| **GF-10** drift after manifest | run through 3.01, then edit the wf1 snapshot, then run the sweep | `SM --until build_members_manifest`; edit; `SM` | either the params trigger re-runs 3.01 and the guard fails loud, or the sweep's layer-3 check fails naming `wf1_snapshot_digest`; in no case does a member run |
| **GF-11** no-op resume cost | complete a sweep, then re-invoke after changing an **execution-policy** key — `sweep_workers: 3 → 2`. *Not* a comment change: since §5.1 fixes `config_digest` over the **parsed** sections, a comment alters no parsed value, 3.01 does not re-run, `members.json` is byte- and mtime-unchanged, and Snakemake reports `Nothing to be done` — the rule would never be entered and the gate could observe nothing. A policy key changes `config_digest`, so 3.01 re-runs and rewrites the manifest, which fires 3.08's input trigger | `Measure-Command { SM }` | the sweep rule **re-enters** and exits **without spawning any Julia process** (`julia` never appears in the process table); all 12 members classify SKIP — which also validates §7.6's row excluding execution policy from `member_hash`; wall < 15 s (§12 C-2). The five reuse conditions, including §7.3 step 4's input digests, are all evaluated inside that budget |
| **GF-12** generation-side invalidation | complete a sweep, then change `workflows.climate_experiment.master_seed` and re-invoke; repeat with an edit to any key of `config/templates/weathergen_config.yml` | `SM`; edit; `SM` | **every** `member_hash` changes; generation re-runs; **all 12** member CSV mtimes change; `_state/quarantine/<id>/` holds the 12 previous CSVs; `Qstats.csv` changes. Falsified if any member is SKIPPED. *This gate exists because v1's `member_hash` could see neither input and would have skipped all 12 — the highest-consequence silent-science path in the document (§5.1)* |
| **GF-13** partial sweep, fix, retry | run GF-7(a) to a partial finalization; remove the injection guard; re-invoke with **no** config change | `SM --config allow_partial=true`; remove guard; `SM --config allow_partial=true` | the second invocation **re-enters** the sweep rule (`reason: params have changed`, `incomplete_digest`), runs exactly the previously-failed member, writes a complete `ledger_final.csv` and **deletes** `_state/sweep_incomplete.json`; `Qstats.csv` regains its 6th row. **Extended through the successful retry's reduction:** `ledger_final.csv` carries **mixed provenance** — 11 members with the first invocation's `succeeded_invocation_id`, 1 with the second's — under a **uniform `finalization_invocation_id`** (second invocation), and the reduce's identity check passes against the latter (C-24); **and `indicators/completeness.csv` is ABSENT** after this full-completeness reduction — the partial invocation's stale record is removed, not left beside complete surfaces (§4.4, C-17). Falsified by `Nothing to be done`, by a reduce hard-fail on the mixed rows, or by a surviving `completeness.csv`. A third invocation is a no-op resume (§7.2) |
| **GF-14** worker stderr flood | a stub `wflow_worker.jl` that writes > 1 MB to stderr before answering its first `run` | `SM` with the stub | the sweep completes and no worker blocks; the flood lands in `_worker_<id>.log` (before the first member's redirect window) or in the member log (inside it) — in a *file* either way. Falsified by a hang — which is what an undrained `PIPE` produces at the 64 KB Windows buffer (§6.2) |
| **GF-15** member CSV divergence after a clean sweep (F8) | mutate one byte of `hydrology_runs/rlz_1/output/cst_2.csv` after a clean sweep | four commands, in sequence | **(i)** `SM` → `Nothing to be done` — the *expected* observation: nothing executes, so nothing detects (§7.2, the narrowed F8 claim stated rather than wished away); **(ii)** `pixi run python scripts/sweep_status.py <exp_dir> --verify` → exit nonzero naming `rlz_1/cst_2` with recorded vs live digest, and the repair lever printed; **(iii)** `SM --forcerun export_wflow_results` → the reduce hard-fails naming `rlz_1/cst_2`; Snakemake then removes the reduce's declared outputs (PR-4) — fail-loud, not loss: a surface derived from an untrusted member is itself untrusted; **(iv)** `Remove-Item <exp_dir>/_state/ledger_final.csv; SM` → the sweep re-enters, quarantines and re-runs **exactly** `rlz_1/cst_2`, the reduce rebuilds, `check_baseline.py check` green. Falsified by a silent republish at (iii), a silent pass at (ii), or any sibling re-running at (iv) |
| **GF-16** slot process dies (F4) | while the sweep runs, `Stop-Process -Force` on one *slot* Python pid — not the Julia worker, which is GF-1's easier case | `SM` (background) + PowerShell kill | the orchestrator names the lost member **from its assignment table** (the orchestrator log line cites the recorded assignment, not a disk scan), records it `failed`/`class=worker`, respawns the slot **and** its worker, re-claims within `member_max_attempts`, and the sweep exits 0; sibling members unaffected |
| **GF-17** Julia unavailable (F12) | shadow `julia` on `PATH` with a shim that exits 127 | `SM` under the shadowed `PATH` | every slot retires after two spawn failures; the sweep fails hard naming Julia and `AGENTS.md`'s juliaup constraint; `ledger_final.csv` **absent** — the same discriminating observation GF-6 relies on. Cheap, and it gates the single most likely environment failure this repo has |
| **GF-18** `tools` drift is reported (C-13) | complete a sweep; edit `run.tools.wflow` in `members.json` to a different version; re-invoke | `SM` | a `tools_drift` entry appears in `_state/sweep_summary.json` and a warning line in the orchestrator log names the differing key. Falsified by silence |
| **GF-19** slot killed between `assign` and `ack` (F4's narrowest window) | test hook `CST_GF19_ACK_DELAY=<member_id>` makes the slot sleep 10 s before acking that member (the GF-6 guard pattern); kill the slot pid inside the window | `SM` (background) with the hook + PowerShell kill | identical recovery to GF-16 — the parent names the member from the recorded assignment (`claimed` row + table, both written **before** dispatch, §6.1), records `failed`/`class=worker`, requeues, respawns; ledger shows `claimed`(1) → `failed`(1) → `claimed`(2) → `succeeded`(2). Falsified by a hang, a lost member (no terminal row), or the wrong member requeued — the outcomes the v2 shared queue could not exclude |
| **GF-20** per-member log separation on a shared worker (C-22) | none — a clean sweep at `--config sweep_workers=1 worker_max_members=0`, one worker serving all 12 members | `SM` + a grep over `logs/_parts/3.08_run_sweep/rlz_*_cst_*.log` | every member log contains its **own** member's simulate output (its TOML path / Wflow banner) and **no other member's**; `_worker_0.log` holds only handshake and between-member output. Falsified by the v2 defect — later members' Wflow output in the first member's log — or any cross-contamination |
| **GF-21** baseline member lifecycle (`cst_0`, C-23) | none — an **untracked scratch config variant**, the tracked fixture untouched: copy `config/workflows/snake_config_model_test.yml` to `dev/tmp/gf21_config.yml` with exactly two edits — `run_historical: true` and a distinct `experiment_name` (`experiment_gf21`) — so it targets a **fresh experiment tree** under the same `project_dir`. `ST_START = 0` ⇒ **K = 2 × 7 = 14**, including the two baseline members `rlz_<n>/cst_0` | `SMg` = the `SM` command with `--configfile dev/tmp/gf21_config.yml`; then `sweep_status.py`, digest checks, `SMg` again | `members.json` carries both baseline members with `baseline: true` / `st_csv: null`; the sweep exits 0 with **no perturb invocation for either baseline member** (no `Rscript … impose_climate_change.R` line in either `cst_0` member log; `_state/members/rlz_<n>/cst_0/` never created); their `succeeded` rows record `inputs.st_csv = null`, `inputs.weagen_template = null`, and `seconds` without `perturb`; **`weather_generator/output/rlz_<n>_cst_0.nc` is byte-unchanged after the sweep** (digest before == after — never deleted, never rewritten); `cst_0.toml`/`cst_0.csv` present; the reduce completes and, under `aggregate_rlz: true`, emits **no `cst_0` row** (the inherited §4.4 asymmetry, observed as specified); a second `SMg` is a no-op resume — both baseline members SKIP on the five conditions with their nulls defined-absent. Falsified by a perturb invocation for a baseline member, a failure reading the null `st_csv`, or a deleted/rewritten baseline NC |
| **GF-22** corrupt-ledger recovery executes to completion (C-25) | after a clean 12-member sweep, inject GF-3's corrupt row into `_state/ledger.jsonl` | `SM --config sweep_quarantine=1`; inventory checks; let the rerun finish | the recovery command **runs to completion**: `_state/quarantine/<invocation_id>/` (the adopting invocation's id) holds the old ledger, every finalization artifact, `_state/members/`, and all 12 member CSVs+TOMLs under `member_products/<member_id>/` with relative paths preserved; `_state/experiment.lock` and `_state/members.json` are **untouched in place**; the quarantine root is not nested into itself; the baseline NCs did not move; a fresh ledger starts, all 12 members re-run, the sweep and reduce complete, exit 0. Falsified by a self-nested move error, a removed `members.json`, or a rerun overwriting un-quarantined member outputs |
| **GF-23** resize → prune → reinvoke (C-26) | complete a sweep at `RLZ_NUM=2`; set `realizations_num: 1`; re-invoke (GF-9's state: 6 `state=orphan` rows, rlz_2 artifacts on disk); then `pixi run python dev/scripts/prune_experiment_orphans.py <exp_dir> --delete` | `SM`; edit; `SM`; prune `--delete`; `SM` | the post-prune invocation **starts and folds cleanly**: the rlz_2 ledger rows are legal history (schema-valid, absent from the current manifest — §5.3), *not* corruption, artifacts gone or not; the 6 rlz_1 members SKIP (no-op resume); `sweep_completeness.csv` has 6 manifest rows and **zero** `state=orphan` rows (nothing on disk to report); exit 0. Falsified by a refusal naming the rlz_2 rows as corruption — the v3 composition defect |
| **GF-24** checked sidecar replacement on regeneration (C-27) | on Windows (the dev platform): after a clean generation, record digests of `weather_generator/output/{sim_dates,resampled_dates}_rlz_1.csv` and the `plots/rlz_1/` PNGs; change `master_seed`; re-invoke so generation re-runs. Sub-case (b): repeat with `sim_dates_rlz_1.csv` held open by a second process during the publish | `SM`; digest; edit seed; `SM`; digest again | **(a)** every published sidecar — both date CSVs and every diagnostic PNG present in the run — is **replaced consistently**: no destination retains first-generation bytes beside a second-generation baseline NC; **(b)** with a destination held open, the publish **fails loud** with the named `publish_file` error (`[generate_weather] publish failed: …`) and a nonzero rule exit — never a silent `FALSE` leaving a stale sidecar. Falsified by any stale sidecar after (a) or a silent success in (b) |

**Failure-mode → gate coverage.** §8.1 enumerates twelve failure modes and
gate-set completeness is §8's own success criterion, so the mapping is stated
rather than implied. v1 left F4, F8 and F12 with no gate at all, and the
highest-consequence realistic failure — the generation-invalidation path — had
none either; a failure mode enumerated in §8.1 with no row in §8.2 reads as
covered when it is not.

| F | Gate | F | Gate |
|---|---|---|---|
| F1 | GF-6 (fail-loud), GF-7 (`allow_partial`), GF-13 (retry) | F7 | GF-3 (refusal), GF-22 (the recovery executes) |
| F2 | **no dedicated gate, stated:** identical recording and blast-radius path to F1, differing only in the `stage` value; GF-6 exercises the mechanism | F8 | GF-15 |
| F3 | GF-1 | F9 | GF-10 |
| F4 | GF-16, GF-19 | F10 | GF-8 |
| F5 | GF-2 | F11 | GF-2 (the stale lock is precisely the state GF-2 lands in) |
| F6 | GF-4 | F12 | GF-17 |

Non-F gates: GF-5 (config change mid-sweep), GF-9 (orphans), GF-11 (no-op resume
cost), GF-12 (generation-side invalidation), GF-14 (stderr drainage), GF-18
(`tools` drift), GF-20 (per-member log separation — G4's gate), GF-21 (baseline
member lifecycle, on its own scratch config variant), GF-23 (orphan pruning ×
ledger legality), GF-24 (checked sidecar replacement — a stage-2 gate).
GF-1..GF-5 and GF-8 are the intake's named injection classes;
GF-6/GF-7 pair the two OQ-4 branches so the ratified posture is testable on both
sides.

---

## 9. Open questions settled

### 9.1 OQ-1 — `precip_variance` semantics · **DEFERRED ENTIRELY (G1, settled)**

**The ruling, first, because an implementer must never read this section as
authority to change behaviour.** Gate G1 deferred OQ-1 in full. This milestone
makes **no** `scale_var_with_mean` change and **no** change to what any number
comes out as. The `precip_variance` axis ships **inert**: the WG-2 column is
produced, carried through the manifest, the ledger and `response_long.csv`, and
ignored by the generator. Every schema **retains** the field, so later activation
is a value change rather than a schema redesign. Activation is the named followup
**R9-F1** (§15.3), owned separately.

**One carve-out, ruled at gate-return: pass `verbose = TRUE` at the R call
site.** `blueearth_cst/weathergen/impose_climate_change.R:45-57` currently passes
`precip_var_factor` and neither `scale_var_with_mean` nor `verbose`. Adding
`verbose = TRUE` is the one change in the vicinity that is **not** value-changing
— it only un-suppresses weathergenr's own `"Ignoring 'precip_var_factor'"`
warning — and without it the axis stays *silently* inert for another milestone,
which is the failure this section exists to prevent. **Where it surfaces:** the
perturb step runs in-slot per member (§6.6 step 2), so the warning lands in
`logs/_parts/3.08_run_sweep/rlz_<n>_cst_<m>.log` and, after merge, in
`wf3_climate_experiment.log` — once per perturbed member, in the run's own record.
Tolerance-0 safe: no output byte changes, so it crosses no parity leg.

**Evidence, measured on the build that actually runs** (probe PR-1, §11.2):

- installed package = `tanerumit/weathergenr` **v1.2.0**, `RemoteSha`
  `9f3d3189b692d9c6e94cf6f712ca5d1dd1b71cfa`, packaged 2026-07-17;
- `formals(apply_climate_perturbations)`: `scale_var_with_mean = TRUE`,
  `verbose = FALSE`;
- body, read from the installed lazy-load database:
  `if (isTRUE(scale_var_with_mean)) { if (!is.null(precip_var_factor) &&
  isTRUE(verbose)) warning("Ignoring 'precip_var_factor' ..."); var_mat_in <- mean_mat_in^2 }`.

**Conclusion: E1 is confirmed on the installed build**, and P6 moves from
*hypothesis* to **measured**. The WG-2 `precip_variance` column never reaches the
output, and the warning that would have said so is suppressed by the `verbose`
default — which is exactly why the carve-out is worth its one line.

**Citation correction that must not propagate.** The intake's P6 row cited
`~/workspace/weathergenr/R/climate_perturbations.R`. That checkout is
`Deltares-research/weathergenr` at `master`, version **1.1.0.9000**, and does
**not contain** the installed sha (`git merge-base --is-ancestor` -> not a valid
commit). The two trees happen to agree on this function, verified line by line
(`R/climate_perturbations.R:107,360-366`), but the reasoning was grounded in a
tree that is not what runs. Any future E1 claim must cite the installed lazy-load
database or `formals()`, never that checkout.

**Where the inertness is documented, so "deferred" does not become "silently
ignored".** All three land in §13 step 6, and §4.4 specifies the wording:

| Surface | Annotation |
|---|---|
| `response_long.csv`'s documented schema | the column note in §4.4, reproduced in `dev/workflows/climate_experiment.md` and `docs/migration-r09-wf3.md` § OQ-1. **No in-file comment line** — §4.4 records why (`check_baseline.py:319` reads CSV targets with a bare `pd.read_csv`) |
| WG-2 seam-doc row | the same statement beside the pinned header |
| Manifest build | a **warning** (not a rejection) when `stress_test.precip.variance.min != variance.max`, naming R9-F1 |

*Rejected sub-option:* **rejecting** such a config. That would be a scope change
the deferral does not authorise — it breaks configs that legitimately declare a
range today and would have to be reversed on activation. A warning delivers the
same signal at zero contract cost. *(The tracked fixture has
`variance.min == variance.max == 1.0`, `snake_config_model_test.yml:75-77`, so no
gate in §8.2 or §12 touches the axis at all — which is itself part of why the
inertness has to be documented rather than gated.)*

**Cost of retention, named and accepted.** `precip_variance` stays inside
`member_hash` via the member tuple and `st_params_digest`, so editing
`stress_test.precip.variance.{min,max}` forces a full re-sweep that provably
cannot change one output value (§5.1). Carving the keys out would put a special
case inside the freshness boundary to serve a temporary state; R9-F1 removes both
the carve-out need and the inertness together.

**Adjacent finding, recorded and deliberately not acted on.** `seed` is also a
formal of `apply_climate_perturbations` and our call site omits it (PR-1).
Combined with P8's measured bit-identical re-runs this *characterizes* the
determinism the design assumes (A3). Starting to pass a seed would be
value-changing scope creep outside the fixed anchor and is **not proposed**.

**Porting 3.07 to Python is rejected** (the OQ-1(b) half of the scoping intake):
a tolerance-0 parity gate against Gamma-QM with `mme` fit, transient ramps and a
PET recompute is high effort and high risk against a stage worth ~6 % of sweep
wall. The R step is invoked per member from the slot (§6.6 step 2), and the
parity question dissolves because the same R code runs on the same inputs.

### 9.2 OQ-2 — ledger contract depth

**Resolved: a named subset of `cst-run-control`**, tabulated row by row in §5.5
with a reason for every skip. In: the two-record split, digests, the state and
attempt machine, append-only attempts, quarantine-before-resume, the namespace
claim. Out: canonicalization vectors, the capability-slot table, the typed stage
graph, content-addressed publication, fencing tokens as enforcement, conformance
levels.

**The one simplification worth arguing about** is dropping
`environment_digest` from checkpoint reusability. A Wflow or hydromt upgrade
therefore does **not** invalidate completed members; a sweep can silently mix
members produced under two engine versions. Mitigations: `run.tools` records the
versions, so the mixture is *detectable* after the fact; and `pixi.lock` is CI-
enforced (`AGENTS.md`), so an unnoticed engine change is already an unusual event
in this repo. The falsifier that would overturn the call is C-13 (§12): if a
`tools` mismatch between the manifest and the live environment is ever observed
in a completed sweep, promote `tools` into `member_hash`.

**"Detectable" now means *mechanically reported*, not *reconstructible by
inspection*.** v1 claimed "`tools` drift is detectable after the fact" and
falsified it with "a mismatch **goes unreported**" — while specifying no rule,
script or step that performs the comparison. As written that falsifier could
never fail (a human can always compare two strings by hand), so C-13 would have
been recorded as passing while R-5 stayed completely unmitigated — and R-5's
whole justification for skipping `environment_digest` rests on C-13 being a
*real* trigger. v2 makes it mechanical and free: **the sweep runner re-reads the
four `tools` versions at start** (§7.3 step 5) and, for each that differs from
`members.json`, appends a `tools_drift` entry to `_state/sweep_summary.json` and
a warning line to the orchestrator log naming the key, the recorded value and the
live one. It does **not** block: recording, not enforcing, is the ruled posture.
C-13's falsifier becomes "inject a version mismatch and observe **no** warning",
which is GF-18 — an observation that can actually fail.

**Alternatives:** full adoption and repo-local-from-scratch, both rejected in
§14.5 / §14.6.

### 9.3 OQ-3 — member naming

**Resolved: index-based, `member_id = "rlz_<n>/cst_<m>"`**, with `cst_0` the
reserved unperturbed baseline (`dev/conventions/naming.md` §4, unchanged). Every
on-disk path keeps today's shape — `hydrology_runs/rlz_<n>/{config,forcing,output}/cst_<m>.*`
— so HM-4, HM-5, HM-6b and WG-6 path patterns are untouched by this milestone.
Coordinates live in the manifest and in `response_long.csv`.

`member_id` uses `/` rather than `_` as the separator so it is simultaneously the
relative path prefix and the log/benchmark part-name stem (rendered
`rlz_<n>_cst_<m>` in filenames). It is registered in `dev/conventions/naming.md`
as a new vocabulary at implementation (derived-artifact register).

**Priced honestly:** index-based ids are **not stable under a grid resize**. A
change to `stress_test.temp.step_num` re-maps every `cst_<m>` to a different
`(ΔT, ΔP)` pair, which is why §7.6 lists it as near-full invalidation. Coordinate-
bearing ids would survive a resize; §14.3 records why they were still rejected.

### 9.4 OQ-4 — reduce with holes · **RATIFIED (G1, settled)**

**Ruled: fail loud by default, with an explicit `allow_partial` escape hatch, and
NO minimum-completeness threshold.** A silently sparse response surface distorts
exactly the robustness judgment CST exists to inform; a threshold would invent a
scientific criterion the repo has no basis for.

| | **fail-loud (default)** | **`allow_partial: true`** |
|---|---|---|
| Sweep terminal condition | every manifest member `succeeded` | at least one member `succeeded` |
| `ledger_final.csv` (declared) | written only on full completion | written, listing succeeded members only |
| `sweep_completeness.csv` (undeclared, survives failure) | written on every terminal path — all-`succeeded` on success, **the holes named** on failure | written; the holes named per member with `stage` and `class`, carrying `invocation_id` + `config_digest` (§5.2) |
| `sweep_incomplete.json` | absent | **written**, with a fresh `invocation_id`, so the next invocation re-enters and retries (§7.2) |
| Reduce | blocked (its declared input is absent) | proceeds; emits `indicators/completeness.csv` beside the surfaces and prints a named warning. A later **full-completeness** reduction removes that file again (§4.4, GF-13) |
| `Qstats.csv` / `basin.csv` / `RT_*.csv` / `response_long.csv` | full grid | **incomplete cells dropped entirely** — the row is absent, not under-averaged and not zero-filled (§4.4) |
| Gate | GF-6 | GF-7 (both sub-cases), GF-13 |

**"Grid with holes" is a claim about the reduce, and the reduce had to change to
make it true.** v1 asserted the hole shape while also asserting the reduction
"keeps its body". Under the fixture's `aggregate_rlz: true` those two statements
are incompatible: the frames are pre-allocated at `st_num` rows and the loop runs
`range(st_num)` regardless of what is on disk, so a hole surfaces as a silently
under-averaged cell, a zero row, or a `pd.concat([])` `ValueError` — every one of
them the distortion the fail-loud default exists to prevent, reintroduced through
the escape hatch the same ruling approves. §4.4 specifies the replacement:
completeness is evaluated **per response-surface cell**, incomplete cells are
dropped, frames are sized from the complete set, and an empty group raises a
named `IncompleteCellError`. §9.6's Reduce parity class is correspondingly
qualified **"Identical under full completeness"**, and C-10 stays a full-grid
byte-identity check while the partial path gets its own falsifier, C-17.

**Both branches keep `--dry-run` honest**, which is why the *declared* output set
is constant across them (§4.3): `ledger_final.csv` exists **iff** the sweep
reached an *accepted* terminal state, and whether that state had holes is a fact
in `sweep_completeness.csv` — never something a reviewer infers from a sentinel's
existence. Completeness reaches the rule's *freshness* through the undeclared
marker instead (§7.2), which is what keeps a partial sweep retryable without
making the declared-output set conditional.

### 9.5 OQ-5 — per-realization generation and seed reproducibility

**Resolved.** E2 stands: `generate_weather` is called once with one config seed
and `n_realizations = RLZ_NUM` (`generate_weather.R:39-59`), so all realizations
draw from one RNG stream and **per-realization jobs cannot reproduce today's
realizations**. Stage 2 is value-changing by construction; that is a documented
re-baseline (§9.6), not a defect.

Scheme: `seed_r = sha256(f"{master_seed}:rlz:{r}")[:4] mod (2^31 − 1)`, computed
in the manifest builder, recorded in `members.json`, injected into the
per-realization WG-3 config (§4.2). Properties: deterministic, recorded,
independent of the experiment name and of `RLZ_NUM` (adding realizations does not
perturb existing seeds — the property that makes §7.6's "only the new members run"
row true).

**Per-call output naming verified from the code**, not assumed: `generate_weather`
takes `n_realizations` and `seed` as arguments and `write_netcdf` takes
`file_prefix` / `file_suffix` independently (`generate_weather.R:39-59, 91-102`),
so a per-realization invocation names its own output — provided the realization
index reaches the suffix from the config rather than the loop counter, which is
the change §4.2 specifies. The one hazard the code reading found is the shared
`out_dir` for `sim_dates.csv` / `resampled_dates.csv` under concurrent jobs;
§4.2 change 3 resolves it.

### 9.6 OQ-6 — migration parity strategy and the baseline manifest

**Resolved: R8 discipline — per-stage falsifiers written before code, no
end-to-end value identity claimed.** Stage by stage:

| Stage | Parity class | Falsifier |
|---|---|---|
| Prepare (manifest, guard, WG-2, store) | **Identical** | guard gate-2 a–h tests unchanged; `cst_<m>.csv` byte-identical; store untouched |
| Generate | **Value-changing, characterized statistically** | same generator, new seeds ⇒ distributional plausibility at the stated threshold (C-16), **never** byte identity |
| Perturb | **Identical** | same R code, same inputs ⇒ tolerance 0 on `rlz_<n>_cst_<m>.nc` when fed a **pre-change** baseline NC. (`verbose = TRUE`, §9.1, adds a warning line to stderr and changes no output byte) |
| Downscale | **Identical, once extracted** | same script body, same inputs ⇒ tolerance 0 on the WG-6 forcing and the HM-4 TOML. **The body does not exist in callable form yet**: `downscale_climate_forcing.py:11-25` reads the `snakemake` global at module top level with no function and no guard, so "the same script body, in-slot" requires the §2.5 extraction *before* this leg has anything to run against. §13 step 4a lands the extraction alone, and this leg is that step's own falsifier |
| Simulate | **Identical at batch depth (measured, P3/GN-2); open at production depth** | the paired same-input comparison of C-7 — **not** a whole-tree diff (see below) |
| Reduce | **Identical under full completeness** | the **new** reduce over the **step-0** member CSVs ⇒ `Qstats.csv`/`basin.csv`/`RT_*.csv` byte-identical to the step-0 capture (C-10). The `allow_partial` path is a *different* claim with its own falsifier (C-17) |

The perturb/downscale/reduce legs are held identical by **feeding them
pre-change artifacts**, which is why §13 step 0's captures are a hard
prerequisite: without them these three legs cannot be proven, only asserted.

**The simulate leg needs a same-input comparison, because a whole-tree diff
cannot answer it.** v1 pointed C-7 at a tolerance-0 `semantic_tree_diff` against
the step-0 whole-tree snapshot and described the leg as "already measured …
re-verified at pool depth". That re-verification did not exist. After step 2
lands, the tree differs from the step-0 reference **on purpose**: generation is
declared value-changing (new per-realization seeds), so every realization NC,
every member CSV and both indicator tables differ. §10b identifies one reason a
whole-tree tolerance-0 diff can never come back clean (the `_state/` timestamps);
the re-baseline is the decisive second, and §4.2's date-CSV rename is a third. The
gate would report a large diff, the diff would be attributed to the known
re-baseline, and A4 — the assumption whose failure corrupts every number the
milestone produces — would be *declared* verified on a gate that was never capable
of discriminating.

C-7 is therefore redefined as a **paired, same-input comparison**, and the
whole-tree diff is retained separately at reduced scope. **Two properties v2's
operand pair lacked are now explicit: a forcing mechanism, and a single varied
variable.** v2 compared runs at `sweep_workers` 12 vs 1 — but execution-policy
keys are excluded from `member_hash` **by design** (§7.6, the row GF-11
verifies), so changing `sweep_workers` alone re-enters the sweep and *skips
every member*: both "runs" would have read back the same previously generated
CSVs and A4 would have been verified by comparing a file with itself. And had
the runs been forced, `p = 12` vs `p = 1` varies concurrency and
oversubscription alongside session depth, confounding the one variable the gate
exists to isolate.

| | Operand |
|---|---|
| **C-7 (binding)** | After step 4, generation frozen (baseline NCs, WG-2 grid and catalog on disk, identical for both legs). Both legs at `sweep_workers: 1`; **session depth is varied by `worker_max_members` alone.** **Leg A (fresh-session reference):** `SM --config sweep_workers=1 worker_max_members=1` — the recycle bound (§6.3) retires the worker after every member, so each member runs in its own Julia session through the *same* slot code path; then **capture** `hydrology_runs/*/output/cst_*.csv` to a holding directory outside the tree (e.g. `dev/tmp/c7_legA/`). **State reset**, with no workflow running: `Remove-Item <exp_dir>/_state, <exp_dir>/hydrology_runs -Recurse -Force` — the ledger and every member artifact go; generation outputs and the catalog stay. **Leg B (full depth):** `SM --config sweep_workers=1 worker_max_members=0` — one session serves all 12 members (3× P3's measured depth); capture to `dev/tmp/c7_legB/`. **Compare the two captures:** `semantic_tree_diff --tolerance 0` legA vs legB. **Execution is forced by state absence, not by any hash change**: the reset removes the ledger, so the fold classifies all 12 members RUN in each leg while every `member_hash` stays identical across legs — GF-11's skip semantics are untouched, and the comparison is same-input by construction. Only session depth varies, so a diff means session depth changed a result |
| **C-7s (scoped whole-tree, reported)** | `semantic_tree_diff` at tolerance 0 restricted to the stages step 2 did **not** change: the WG-2 grid (`weather_generator/_work/cst_*.csv`), the historical store, and the wf1 config snapshot. It runs **after** §13 step 6's path-map update, since the date-CSV rename is in the map. It makes no claim about generation, the sweep or the indicators |
| **Budget note** | the held `p x M = 12` protocol binds the **floor check only** (§13 step 8). C-7's two runs vary depth deliberately and make no performance claim |

**Baseline manifest: re-recorded exactly once**, at the end (§13 step 9). wf3's slice
grows from 3 targets to 4 (`response_long.csv`) — recommended, owner-confirmed at
the record. Baseline-provenance stamping (R7-21) already guards the
fixture-sharing risk.

### 9.7 OQ-7 — pool boundary

**Resolved: Python orchestrator over warm Julia workers** (§6.1), with a third
level the scoping intake did not name: **persistent Python slots** that amortize
the hydromt import as well. `run_wflow_batch.jl` is the seed of the worker loop —
the same `Wflow.run(t)` inside the same per-member `try/catch`, reading stdin
instead of `ARGS`, and reporting structured JSON instead of `BATCH-RUN OK` lines.

Rejected: a Julia-side queue (§14.4). Rejected: threads instead of slot processes
(§14.7). Rejected: a fresh subprocess per member with no persistent Python layer
(§14.8).

---

## 10. Contract-delta table (WG-1..WG-6 / HM-1..HM-7)

Dispositions: **verbatim** (no change), **home** (moves or changes producer),
**transient** (becomes runner-owned and deleted), **new**.

| Surface | Disposition | What changes | Validator impact |
|---|---|---|---|
| **WG-1** `extract_historical.nc` | **verbatim** | nothing; rule 3.03 is the unchanged shared producer | `validate_wg1` unchanged |
| **WG-2** `cst_<m>.csv` | **verbatim** *(unconditional — OQ-1 is deferred)* | path, header (incl. the now-inert `precip_variance` column), 12-row domain and semantics all unchanged. New readers: the manifest builder (scalars) and the runner. Still a declared `input:` of the reduce. Its digest is recorded per member as `inputs.st_csv` and verified on resume (§5.5) | `validate_wg2` **unchanged**. Doc delta only: the seam row gains the inertness statement (§9.1) |
| **WG-3** weathergenr config surface | **home** | `config/weathergen_config.yml` → per-realization `_work/weathergen_config_rlz_<n>.yml` with **two added keys** (`rlz.index`, `work.path`) plus **two overrides of existing keys** (`realizations_num: 1`, per-realization `seed`). `seed` is an already-pinned WG-3 key (`weather-generator-seam.md:141`), *not* an addition. The per-member `weathergen_config_rlz_<n>_cst_<m>.yml` leaves disk for `_state/members/<id>/weagen.yml`, **transient**. `weather_generator/config/` retires | **`validate_wg3` changes**: add the per-realization form and its two new keys, and the per-realization `seed` override; the per-member fixture path moves and becomes capture-dependent. Continuously-verified status is retained for the per-rlz form |
| **WG-3+** `sim_dates.csv`, `resampled_dates.csv` | **home (rename, same directory)** | `weather_generator/output/{sim_dates,resampled_dates}.csv` → `…_rlz_<n>.csv`, published by our wrapper — via the **checked `publish_file` replacement** (§4.2; GF-24, C-27) — after the generator writes them to the per-realization `_work/` scratch (§4.2 change 3). They stay in `output/`, honouring R07's ruling (`dev/r07/migration_project-layout.md:194-195`); only the names gain a realization index, which the concurrent-write race makes unavoidable | Non-interchange, so no validator. **Tooling delta:** `dev/scripts/semantic_tree_diff.py:357-360`'s exact-file path-map rule and its assertion at `tests/test_semantic_tree_diff.py:621-622` update in the same commit (§13 step 6); the seam doc's exclusion note is amended to the new names |
| **WG-3+** generator diagnostic PNGs | **home** | `plots/` → `plots/rlz_<n>/`, same reason; the pre-existing unchecked `file.rename` loop (`generate_weather.R:68-73`) is rewritten onto the same checked `publish_file` helper (§4.2; GF-24, C-27) | none |
| **WG-4** `rlz_<n>_cst_0.nc` (baseline) | **home** | lifecycle `temp()` → **persistent** | `validate_wg4` logic unchanged; the baseline case **upgrades** from skip-until-captured to continuously verified — a net gain |
| **WG-4** `rlz_<n>_cst_<m>.nc`, m ≥ 1 | **transient** | same path, same content; deleted by the runner after downscale instead of by Snakemake | logic unchanged; **capture procedure changes**: `--notemp` no longer works (§10a) |
| **WG-5** climate data catalog | **verbatim** | path, per-entry schema, and the entry-key grid (incl. `cst_0`) all unchanged. **The producer's *script* changes too, not only its `input:` set**: `prepare_climate_data_catalog.py:132-133` derives its entry list from `sm.input.cst_nc` / `sm.input.rlz_nc`, so a manifest-derived list is a code change with an owner (§2.5) | `validate_wg5` and `validate_wg5_catalog_grid` unchanged, both still continuously verified |
| **WG-6** `inmaps_cst_<m>.nc` | **transient** | same path, same content; runner-deleted | logic unchanged; capture procedure changes (§10a) |
| **HM-1** `staticmaps.nc` | **verbatim** | untouched | unchanged |
| **HM-2** wf1 forcing | **verbatim** | untouched | unchanged |
| **HM-2** wf3 twin (= WG-6) | **transient** | as WG-6 | as WG-6 |
| **HM-3** staticgeoms | **verbatim** | untouched | unchanged |
| **HM-4** per-cst TOML | **verbatim** | `hydrology_runs/rlz_<n>/config/cst_<m>.toml`, same rewrite fields, **still persistent** (a deliberate choice: it is cheap and it keeps `validate_hm4` in the continuously-verified class) | `validate_hm4` unchanged |
| **HM-5** per-member CSV | **verbatim** | same path, same column identity, **still persistent**. Newly digest-recorded by the runner | `validate_hm5` unchanged |
| **HM-6a** wf1 warm state | **verbatim** | untouched | none (existence pinned via HM-4) |
| **HM-6b** wf3 warm state | **transient** | same path; runner-deleted after verify | logic unchanged; capture procedure changes (§10a) |
| **HM-7** `Qstats.csv` / `basin.csv` | **verbatim** | byte-stable requirement; the `Q_` prefix and `basavg` reliance retained deliberately | `validate_hm7` unchanged for these two |
| **HM-7** `RT_<var>.csv` | **verbatim** | one per discharge variable, written undeclared into `indicators_dir` (`export_wflow_results.py:300-315`). Same content from the same member CSVs; obtained via the ledger, subject to the same cell-drop rule under `allow_partial`. **Not** in the baseline manifest, **not** in `WF3_TARGETS` (§4.4) | none; covered by C-10's direct diff |
| **HM-7+** `response_long.csv` | **new** | tidy long view of the two wide tables (§4.4), carrying an inert-`precip_variance` header note (§9.1). **Joins the baseline manifest** (G1) and `WF3_TARGETS` | **`validate_hm7` gains a case**; a new relational check that the long table re-pivots to the wide ones at parsed-value equality (C-11) |
| **HM-7+** `indicators/completeness.csv` | **new, conditional** | written **only** on the `allow_partial` path, and **removed by any later full-completeness reduction** (§4.4, GF-13) so the partial→retry→complete sequence never leaves it stale beside complete surfaces; per-cell `state`, `n_present`/`n_expected`, missing member ids, plus `invocation_id` + `config_digest` (§5.2). `indicators/` is pinned by `check_baseline.py:187-189`, so a conditional file there needs an explicit disposition: **it does not join the manifest** (it is absent on every clean run, which would make the slice non-deterministic) | none; its content is gated by GF-7, its removal by GF-13 |
| **Producer/consumer rule identity** across both seam docs | **home** | The seam docs pin *rule* identity that v2 retires: WG-2's consumer "rule 3.07 `generate_climate_stress_test`" (`weather-generator-seam.md:116-117`), WG-5's "rule 3.09 `downscale_climate_realization`" (`:196`), WG-6's "rule 3.10 `run_wflow`" (`:233`), WG-4's producer "rule 3.06 / rule 3.07" (`:160`), and WG-4's **pinned surface** explicitly including "the DAG-globbed naming pattern (rule 3.08 expand; rule 3.09 wildcards)" (`:167-173`) — a property v2 removes outright, since the perturbed NCs cease to be DAG nodes. The bounded-substitution walkthrough (`:284-289`) names rules 3.04–3.07 as what a replacement generator replaces and 3.02/3.08/3.09 as pinned boundaries | **§13 step 6 does a full pass** over both docs' producer / consumer / lifecycle / pinned-surface fields, the WG-4 naming-pattern clause, and the walkthrough. Without it R9 ships seam docs naming four rules that do not exist and pinning a DAG property the pipeline no longer has — exactly the drift the contracts exist to prevent, in the artifact a future generator-swapper reads end to end |
| `validate_hm_gauge_column_identity` | **verbatim inputs** | all three inputs still persist | unchanged; **extended** to cover the long table's `column` values |

### 10a. The `--notemp` replacement (a gate that would otherwise silently break)

Three validators — `validate_wg4` (perturbed), `validate_wg6`, `validate_hm6b` —
document `--notemp` as their on-disk capture procedure, and three integration
tests carry runtime `pytest.skip("temp() artifact absent; capture via --notemp")`
guards keyed to it. **`--notemp` is a Snakemake flag; it cannot suppress a delete
the runner performs.** Without a replacement these three gates degrade from
"skip-until-captured" to "uncapturable", silently.

Replacement: the `retain_member_artifacts` config key (§4.5), which suppresses
the deletions in **step 3 and step 5** of §6.6 — step 3 is the one that holds the
WG-4 perturbed NC, `validate_wg4`'s operand. Capture command (the `--config` key
is top-level and is resolved by §4.3's precedence rule; v1's command reached no
key at all):

```bash
snakemake all -c 3 -s Snakefile_climate_experiment \
  --configfile config/workflows/snake_config_model_test.yml \
  --config retain_member_artifacts=true
```

Paths that then appear are **exactly the ones the existing skip-guards already
test for** — the artifact paths do not move — so the guards resolve automatically
and no test code changes. What must change is the **prose in both seam docs**
(the `--notemp` capture-procedure sections) and the restore instruction:
re-running without the flag no longer restores the temp-deleted state, because
Snakemake never knew about these files. Restore becomes an explicit delete of the
retained set, scripted alongside `prune_experiment_orphans.py`.

**Bonus:** the capture becomes *cheap*. P5 measured 19 jobs / 247.7 s to capture
three `rlz_1_cst_1` artifacts, because asking for one intermediate re-ran 3.06
(all realizations) and every 3.07. With persistent baselines and a ledger-driven
sweep, a capture of one member is one member's work.

### 10b. `_state/` and the comparison tooling (or C-7 and C-10 cannot pass)

`_state/` is **nondeterministic by design**: `created_at`, `ts`,
`invocation_id` (uuid4), `pid`, `host`, `worker_id` and every `seconds` value
change on every run. It lands inside the experiment tree, which is the tree
`dev/scripts/semantic_tree_diff.py` compares. Left unregistered, a whole-tree
diff at tolerance 0 could **never** come back clean — not because a value
changed, but because this design added timestamped files to the compared set.
That would silently convert C-7 from a gate into a permanent red light.

The mechanism already exists and already handles exactly this class:
`EXCLUDED_DIR_NAMES = frozenset({"logs", "benchmarks", ".snakemake"})`
(`dev/scripts/semantic_tree_diff.py:145`), whose comment reads "non-deterministic
wall times / timestamps / snakemake metadata — never byte-diffed".

**Required registrations, both landing in §13 step 6:**

1. **`semantic_tree_diff.py`** — add `_state` to `EXCLUDED_DIR_NAMES`. One line,
   same rationale as the three existing members. Consequence: the ledger and the
   manifest are **not** covered by the tolerance-0 gate, which is correct — they
   are run records, not products, and their *content* is gated by the unit tests
   of §13 step 4 and by GF-2/GF-3 instead. **Two more edits in the same file and
   commit:** the exact-file path-map rule at `:357-360` for the two date CSVs,
   which §4.2 renames (with its assertion at
   `tests/test_semantic_tree_diff.py:621-622`), and the now-dead allowlist entry
   for `experiments/{experiment_name}/.project_consistency_ok` at `:201` plus its
   explanatory comment at `:381`, both orphaned when the sentinel retires.
   *Registration alone is not sufficient for C-7*: even a fully registered
   whole-tree diff cannot be clean after the step-2 re-baseline, which is why C-7
   is a paired same-input comparison and only C-7s is a tree diff (§9.6).
2. **`check_baseline.py`** — the wf3 manifest slice gains
   `indicators/response_long.csv` and gains **nothing from `_state/`**. Stated as
   an explicit negative because it is the kind of omission that reads as an
   oversight: `ledger_final.csv` carries `seconds_total` and the two invocation
   columns (`succeeded_invocation_id`, `finalization_invocation_id`, §5.2) and
   would make the manifest fail on every run. The manifest pins **products**;
   `_state/` holds **provenance**.

Anything under `_state/` that a reviewer would want byte-compared belongs in a
product artifact instead — which is why `response_long.csv` is a product and
`ledger_final.csv` is not.

## 11. Evidence

### 11.1 Carried-forward register (from the run intake)

| # | Premise | Status in this design |
|---|---|---|
| P1 | `F ≈ 24 s`, `S_cold ≈ 92 s`, `S_warm ≈ 35 s` (measured, n=1) | Grounds the pool: the pool captures `S_cold → S_warm` for every member, not per batch (§1.1, §6.1) |
| P2 | `B=4` sweep 400.2 s vs `B=1` 619.9 s (−35.4 %), adverse ordering; 3.10-stage makespan 228.1 s at B=4; **~156 s modeled upstream (perturb+downscale) work** (`dev/p33/batching-results.md:113-114`), all at `K=12`, `p=3` | **Context for the performance floor, no longer a binding comparand.** The 228.1 s figure measures the *simulate-only* stage, while rule 3.08 fuses perturb + downscale + simulate — gating on it would charge the pool ~156 s of work the comparand never performed. The binding floor is a **same-tree, same-boundary span** measured at step 4 (§13 step 8, C-12); the 400.2 s full wall stays reported-only (v2 restructures generation and prepare) |
| P3 | Warm-session ≡ cold-process byte identity, 102 files, tolerance 0, at `B=4` depth | Assumption A4 at **batch** depth. C-7 re-tests it at `worker_max_members: 0` vs `1`, both legs `sweep_workers: 1` (one 12-member session vs fresh per-member sessions, §9.6); production depth stays open (§2.2, §15.3) |
| P4 | Peak `temp()` disk = `p × B × (forcing + state)`; 120.59 MB measured at the cap | Superseded by design: v2's ceiling is `p × 1`, independent of sweep size (§6.6) |
| P5 | `temp()` cascade: one intermediate target ⇒ 19 jobs / 247.7 s | Dissolved by persistent baselines (§4.2) and by §10a's cheap capture |
| P6 | `precip_var_factor` inert at our call site | **Upgraded to measured on the installed build** by PR-1; the intake's source citation is corrected. Under the G1 deferral this is what the milestone *documents* rather than what it fixes (§9.1) |
| P7 | Realizations generated jointly from one seed | Grounds OQ-5's re-baseline (§9.5) |
| P8 | 3.07 perturbation deterministic in practice | Assumption A3; strengthened by PR-1's observation that `seed` is a formal and is omitted |
| P9 | `t260720a` fixed; the grid spans `variance.min..max` | Establishes that the grid the WG-2 file carries is well-formed — so the axis is inert *downstream* of a correct grid, not because the grid was broken. Bears on R9-F1's activation, not on this milestone (§9.1) |

### 11.2 Probes run during drafting

All read-only. No wflow run, no weather generation, no hydromt extraction, no
`pixi install`. Scratch under `dev/tmp/` (gitignored via `dev/tmp/*` +
`!dev/tmp/.gitkeep`, `.gitignore:153-154`).

**PR-1 — installed weathergenr, E1 settlement.** *(settles P6; §9.1)*

```bash
cat C:/Users/taner/workspace/blueearth_cst/.pixi/envs/default/Lib/R/library/weathergenr/DESCRIPTION
cd C:/Users/taner/workspace/weathergenr && git log -1 && grep -E '^Version' DESCRIPTION
# and, reading the INSTALLED lazy-load DB without loading the namespace:
Rscript.exe --vanilla --default-packages=NULL -e '
  lib <- ".../Lib/R/library/weathergenr"; e <- new.env()
  lazyLoad(file.path(lib,"R","weathergenr"), envir=e)
  f <- formals(e$apply_climate_perturbations)
  cat(deparse(f$scale_var_with_mean), deparse(f$verbose))
  cat(grep("scale_var_with_mean|var_mat_in|precip_var_factor",
           deparse(body(e$apply_climate_perturbations)), value=TRUE), sep="\n")'
```

*(`Rscript.exe` invoked directly from the primary checkout's env with
`PATH` prepended by `<env>/Library/bin` and `<env>/Lib/R/bin/x64`; **not** via
`pixi run`, so no lock check and no re-solve risk.)*

Observations: installed = `tanerumit/weathergenr` v1.2.0, `RemoteSha 9f3d3189…`,
`Packaged: 2026-07-17`. Local checkout = `Deltares-research/weathergenr` master,
v1.1.0.9000, and the installed sha is **not a valid commit** there.
`scale_var_with_mean = TRUE`, `verbose = FALSE`, and the body ignores
`precip_var_factor` under that default, warning only when `verbose`. The two
trees agree on the function (`R/climate_perturbations.R:107,360-366`).

**PR-2 — sweep-rule freshness, the resume path.** Scratch Snakefile at
`dev/tmp/sweepprobe/Snakefile`: one rule with a `params.config_digest` and one
declared output.

```bash
PROBE_DIGEST=aaa111 snakemake -c 1            # run once
PROBE_DIGEST=aaa111 snakemake -c 1 --dry-run  # observe
```
→ `Nothing to be done (all requested files are present and up to date).`

**PR-3 — params rerun-trigger fires on a digest change.** Same tree:

```bash
PROBE_DIGEST=bbb222 snakemake -c 1 --dry-run
```
→ `reason: params have changed since last execution: sweep`, 2 jobs queued,
plus the "triggered by provenance information" note. Confirms the digest params
are a working invalidation lever for a sweep rule (the same mechanism 3.00b uses
today, now carrying the whole sweep's freshness).

**PR-4 — failure deletes declared outputs only.** `dev/tmp/failprobe/`: a rule
that writes an **undeclared** `out/ledger.jsonl` and a **declared**
`out/ledger_final.csv`, then raises.

Observations: `Removing output files of failed job sweep since they might be
corrupted:` — `out/ledger_final.csv` gone, `out/ledger.jsonl` **present**.
This is the structural rule §3.2 is built on.

**PR-5 — Julia worker line-protocol viability.** `dev/tmp/worker_probe.jl`, a
stdin/stdout echo loop with **no Wflow loaded**; `julia --startup-file=no` (1.11.7
via juliaup, on `PATH`). Three lines in, four out; transcript in §6.2. Confirms:
handshake-on-start, one-line-per-message with explicit `flush(stdout)`, an
error path that does not terminate the loop, and graceful `shutdown`/`bye`.
`eachline(stdin)` also terminates on EOF, which is the orphan-avoidance property
§6.3 rule 4 relies on. **Not probed:** behaviour with `Wflow` loaded, i.e.
whether `Wflow.run` writes to stdout — a task-brief falsifier (C-6).

**PR-6 — hard-kill resume.** `dev/tmp/killprobe/`: a rule that fsyncs two ledger
rows, then sleeps, then writes the declared `out/ledger_final.csv`. Started, then
`Stop-Process -Id <pid> -Force` on the running job.

Observations after the kill:
- `out/ledger.jsonl` **intact**, both rows complete;
- `out/ledger_final.csv` **absent**;
- `.snakemake/incomplete/b3V0L2xlZGdlcl9maW5hbC5jc3Y=` present (base64 of the
  output path);
- `.snakemake/locks/{0.input.lock, 0.output.lock}` left behind.

Re-invocation `--dry-run` reports
`reason: output files have to be generated: sweep` — clean, and **no
`--rerun-incomplete` is demanded**, because the output never existed. `--unlock`
clears the locks (`Unlocked working directory.`), matching `AGENTS.md` § Workflow.

*Precision note:* the lock **files** were observed; that a real (non-dry)
invocation is *blocked* by them is asserted from Snakemake semantics and the
repo's own documented `--unlock` step, **not** re-measured here.

**PR-7 — `onstart` / `onsuccess` / `onerror` semantics.** *(new in v2; the
experiment lock of §6.6 rests on all three observations, and no Snakefile in this
repo uses these handlers today, so none of it could be read off the tree.)*
`dev/tmp/lockprobe/`: a two-rule Snakefile whose handlers write marker files, with
the raise and the job failure switched by environment variables. Executable: the
primary checkout's `.pixi/envs/default/Scripts/snakemake.exe` (Snakemake 9.6.2),
invoked directly — no `pixi run`, so no lock check and no re-solve risk.

| Case | Command | Observation |
|---|---|---|
| dry-run | `snakemake -c 1 --dry-run` | **no `onstart` marker** — the handler does not run, so `--dry-run` never claims a lock |
| clean run | `snakemake -c 1` | `onstart` then `onsuccess`; no `onerror` |
| job fails | `PROBE_JOB_FAIL=1 snakemake -c 1` | `onstart` then **`onerror`**; the lock is released on the failure path |
| `onstart` raises | `PROBE_ONSTART_RAISE=1 snakemake -c 1` | `RuntimeError in file "…/Snakefile", line 7` naming the message; **`out/` never created — no job ran**; and **neither `onsuccess` nor `onerror` marker appears** |

The fourth row is the load-bearing one twice over: a workflow that fails to claim
the lock aborts **before stage 1**, and it can never release a lock it did not
claim, because no release handler fires. The third row supplies the release path
for ordinary failures. **Not probed:** behaviour under `--keep-going` with a
partially failed DAG (wf3 is not invoked with `--keep-going`), and whether a
`KeyboardInterrupt` reaches `onerror` — the latter is why §6.6 still needs the
pid + creation-time stale-lock rule rather than trusting the handler.

### 11.3 Hypotheses this design carries (not probed; each has a falsifier)

| # | Hypothesis | Falsifier | Owner |
|---|---|---|---|
| H1 | The per-member fd-level redirection (§6.2) fully contains `Wflow.run`'s stdout/stderr, and the restored protocol stdout carries only JSON lines | C-6 | implementation |
| H2 | Warm-session identity holds at pool depth (K members in one session, not B) | C-7 | implementation |
| H3 | The hydromt import amortizes usefully across members in one slot | C-4 | implementation |
| H4 | `multiprocessing` spawn + persistent Julia children is stable on Windows for a full sweep | C-5 | implementation |
| H5 | A Julia session stays numerically identical and memory-stable across **production** depth (hundreds of members), not only the 12 the fixture can reach | C-7's full-depth leg (`worker_max_members: 0`, §9.6) bounds it from below only; the real falsifier is the first production sweep (§15.3 names the trigger). `worker_max_members` is the pre-designed mitigation | implementation / first production run |

---

## 12. Claim → falsifier table

Every runtime property this design claims, the observation that would falsify it,
and the command producing that observation. `SM` as in §8.2.

| # | Claim | Falsifier | Command |
|---|---|---|---|
| **C-1** | A failed member deletes no sibling artifact | any sibling CSV missing or mtime-changed after GF-6 | `SM` with the GF-6 guard; `Get-ChildItem hydrology_runs/*/output/cst_*.csv` before/after |
| **C-2** | A no-op resume costs one Python start and spawns no Julia | `julia` appears in the process table, or wall > 15 s | GF-11 (`Measure-Command { SM }` + process sampling) |
| **C-3** | Peak transient disk = `p x 1` member **within one invocation**, independent of sweep size; across invocations the fold's transient cleanup keeps it there (§6.6) | peak exceeds `p x max(WG-4, WG-6+state)` at any sample, or grows with `K`; **or** a tree carries stale transients after two interrupted-then-resumed sweeps | P3-3's GN-3 2 s sampler, run at `K=12` and again at a reduced `K`; plus a kill-resume-kill-resume cycle followed by a transient inventory |
| **C-4** | Persistent Python slots amortize the hydromt import | mean per-member `seconds.downscale` after the first member is not materially below the first member's | ledger `seconds.downscale` distribution, first vs subsequent per slot |
| **C-5** | The pool completes a full fixture sweep without a slot or worker crash | any `class=worker` row in a clean run | ledger grep on a clean `SM` |
| **C-6** | The line protocol is not corrupted by Wflow's own output | any non-JSON line on a worker's stdout | worker stdout capture during a real member |
| **C-7** | Session depth does not change results: 12 members in ONE Julia session are byte-identical to the same 12 members each run in a fresh session | any diff at tolerance 0 between the two **captured** result sets | the paired protocol of §9.6: both legs `sweep_workers: 1`, `worker_max_members: 1` vs `0`, execution forced by the named state reset between legs (never by a hash change), both captures taken before comparison, `semantic_tree_diff --tolerance 0` legA vs legB. **Not** a whole-tree diff — see C-7s |
| **C-7s** | The stages step 2 did **not** change are byte-unchanged | any diff at tolerance 0 over the WG-2 grid, the historical store, or the wf1 config snapshot | `dev/scripts/semantic_tree_diff.py --tolerance 0` scoped to those paths, run **after** §13 step 6's path-map update, and **valid only after `_state` joins `EXCLUDED_DIR_NAMES`** (§10b). Reported, not a proxy for C-7 |
| **C-8** | Resume runs only unfinished members | any member with a `succeeded` row re-executes (CSV mtime changes) | GF-2 |
| **C-9** | A corrupt ledger row quarantines rather than passes | the sweep proceeds and any member runs | GF-3 |
| **C-10** | `Qstats.csv` / `basin.csv` / `RT_*.csv` are byte-identical when fed the same member CSVs, **under full completeness**, and a diverged member CSV is refused rather than republished **whenever the reduce executes** (after a clean sweep, an ordinary re-invocation executes nothing and detects nothing — §4.4, F8) | any byte differs vs the step-0 capture; or a mutated member CSV is consumed silently by an executing reduce; or `--verify` passes on a diverged tree | `dev/scripts/check_baseline.py check --workflow climate_experiment` + direct diff; GF-15 (all four observations) for the refusal half |
| **C-11** | `response_long.csv` is a lossless pivot of the two wide tables | re-pivot != wide at **parsed-value** equality, at the declared rounding, in any cell (string formatting is explicitly not contract, §4.4) | a pytest re-pivot test in `tests/test_export_wflow_results.py` |
| **C-12** | The performance floor holds at fixture scale under a held `p x M = 12`, **across the same scientific boundary** — from a tree with prepare, generation and catalog complete to all 12 member CSVs present: **(binding)** over **>= 3 counterbalanced AB/BA pairs** (batch-first and pool-first alternating, §13 step 8), the **median** pool boundary span is <= the **median** batch boundary span, all legs measured in the same step-4 tree under the same conditions; **(reported, not gated)** every individual span, the per-leg dispersion (min/median/max), component timings per §13 step 8, plus P3-3's 228.1 s / 400.2 s as historical context | median pool boundary span > median batch boundary span over the predeclared pairs | §13 step 4's counterbalanced floor protocol (pool and batch rules both present, same tree); re-confirmed at step 8. A single pair is no longer admissible: one batch-first observation hands the pool leg the OS-cache warming and lets ordinary timing noise decide a stop-and-review gate (ext2-7). 228.1 s is no longer the gate: it measures simulate only, while 3.08 fuses perturb + downscale + simulate — gating on it would charge the pool ~156 s of work absent from the comparand (P2) |
| **C-13** | `tools` drift is **mechanically reported**, not merely reconstructible | inject a version mismatch and observe **no** `tools_drift` entry in `_state/sweep_summary.json` and no warning line | GF-18 |
| **C-14** | Two workflows cannot interleave on one experiment, **at any stage** | both proceed; or the second writes any artifact (manifest, baseline NC, indicator table) before failing | GF-8 |
| **C-15** | Guard failure modes are unchanged | any gate-2 a–h case changes verdict or message | `pytest tests/test_check_project_consistency.py` **and** `pytest tests/test_guard_invalidation.py` — the latter's *contract* assertions (verdict + message per case) must hold unchanged; its *plumbing* assertions (the `.project_consistency_ok` target path) are expected to change and are not part of the claim (§4.1) |
| **C-16** | The generation re-baseline is distributionally **plausible** at the stated threshold — not a distributional equivalence proof, which n=2 cannot support | any per-variable annual mean falls outside +/-2 SE of the pre-change mean, or any annual-sd ratio falls outside [0.8, 1.25] | the §9.6 characterization script over the fixture's `realizations_num: 2`, before vs after. **Stated limitation:** two draws of a stochastic generator give an envelope with no statistical power; the acceptance thresholds above are what n=2 *can* carry, and the genuine distributional verdict is deferred to followup **R9-F2** (an elevated-`realizations_num` characterization, generation-only, §15.3) |
| **C-17** | Under `allow_partial`, an incomplete response-surface cell is **absent**, never under-averaged, zero-filled, or a crash; and a later **full-completeness** reduction removes any prior `indicators/completeness.csv` (§4.4) | any `Qstats.csv`/`basin.csv` row exists for a cell whose realization set is incomplete; or `pd.concat([])` raises; or `indicators/completeness.csv` omits the dropped cell; or a stale `completeness.csv` survives a full-completeness reduction | GF-7, both sub-cases; GF-13's final observation for the removal half |
| **C-18** | A generation-side input change invalidates every member | any member is SKIPPED after a `master_seed` or generator-template edit | GF-12 |
| **C-19** | A partial sweep is retryable without manual intervention | the invocation after a partial finalization reports `Nothing to be done` | GF-13 |
| **C-20** | The experiment lock covers the whole workflow, and a stale one is recoverable by a named command | a second workflow writes any artifact before failing; or a hard-killed run has no documented exit | GF-8, GF-2 |
| **C-21** | The parent can always name a dead slot's in-flight member from its own records — the fsync'd `claimed` row and the assignment table, both written before dispatch (§6.1) | any slot death that hangs the sweep, loses a member (no terminal ledger row), or requeues a member other than the recorded one | GF-16, GF-19 |
| **C-22** | Per-member logs are strictly separated on a shared worker: each member's simulate output lands in its own log, whatever session served it | any member log containing another member's simulate output; or simulate output accumulating in the first member's log (the v2 defect) | GF-20 |
| **C-23** | A baseline member (`baseline: true` / `st_csv: null`) runs the §6.6 baseline branch: no spec write, no perturb invocation, downscale directly from the persistent baseline NC, `inputs.st_csv = null` recorded, and the baseline NC never deleted or rewritten at any lifecycle point | a perturb invocation for a `cst_0` member; a failure reading the null stress CSV; the baseline NC deleted, moved, or byte-changed by the sweep, the resume fold, or the quarantine inventory; or a baseline member failing to SKIP on a no-op resume | GF-21 (scratch `run_historical: true` config variant) |
| **C-24** | Mixed-attempt provenance survives finalization and reduction: `ledger_final.csv` distinguishes per-member `succeeded_invocation_id` from the uniform `finalization_invocation_id`, and the reduce's completeness identity check validates against the **latter only** — a resumed or partial-then-retried sweep reduces cleanly | the reduce hard-fails on a `ledger_final.csv` whose successes span invocations; or finalization overwrites the per-member ids with a uniform value; or the identity check reads the per-member column | GF-2 and GF-13, both extended through successful reduction |
| **C-25** | The corrupt-ledger recovery (`sweep_quarantine=1`) is executable to completion as specified: the explicit inventory moves ledger/finalization state and every current manifest-owned member output into a fresh quarantine generation while `experiment.lock`, `members.json`, and the quarantine root stay in place | the recovery errors (e.g. a self-nested move); `members.json` or the lock is moved or removed; the quarantine root nests into itself; or the forced full rerun overwrites member outputs that were never quarantined | GF-22 |
| **C-26** | Orphan ledger history is legal independently of live artifacts: a schema-valid sub-sequence for a member absent from the current manifest folds as legal history whether its artifacts exist or were pruned | a post-`--delete` invocation refuses to start naming historical rows as corruption | GF-23 |
| **C-27** | Stage 2's published sidecars (the two per-realization date CSVs and the diagnostic PNGs) are replaced by **checked** publication on every regeneration — a failed replace is a named loud error, never a silent stale file | any sidecar retaining previous-generation content beside a regenerated baseline NC; or a `FALSE` return from remove/rename continuing silently | GF-24, both sub-cases |

---

## 13. Migration and commit plan

R8 discipline: **each step's falsifier is written before its code**, and the
manifest is re-recorded exactly once, at the end. Commit prefix `r09:`.
Implementation runs in its own worktree (`worktree_policy: always`); pushes stay
a separate explicit decision.

### Step 0 — Pre-change captures (blocking; no code)

Nothing downstream can be *proven* without these. Order matters.

1. **Prune first.** Run the orphan report over the fixture experiment tree and
   resolve anything it names. `AGENTS.md`'s rule for `prune_series_cache.py`
   applies identically: pruning must precede the snapshot, or the snapshot bakes
   orphans in and every later comparison compares them.
2. **Whole-tree reference snapshot** of `test_case/test_local` for
   `dev/scripts/semantic_tree_diff.py` (the intake's gate-materialization table
   lists this as *needed*, not available).
3. **`--notemp` capture** of the WG-4 perturbed NCs, WG-6 forcing and HM-6b states
   — the **last** time `--notemp` can produce them (§10a). Retain them outside the
   fixture as the parity operands for steps 3 and 5.
4. **Seeded per-member operands:** the pre-change `rlz_<n>_cst_0.nc` baselines and
   the **12** per-member CSVs, retained for the perturb / downscale / reduce
   identity legs (§9.6).
5. **Baseline check green** before touching anything:
   `check_baseline.py check --workflow climate_experiment` → OK.

### Step 1 — Manifest builder + guard fusion

*Falsifier first:* a determinism test asserting `members.json` is byte-identical
across two invocations with unchanged config **after removing `run.created_at`**,
and the existing guard gate-2 a–h cases unchanged (C-15). The exclusion is
necessary and is stated rather than discovered: `run.created_at` is a wall-clock
stamp inside the manifest, so two invocations *cannot* produce a byte-identical
file, and v1's falsifier as written was unpassable — which means it would have
been quietly weakened at implementation time, on the only gate protecting
manifest determinism. **Exactly one field is excluded**, `run.created_at`;
everything else, including every digest and every member row, is asserted
byte-stable. (`created_at` changing on every 3.01 execution is also why §7.3's
no-op path is load-bearing: the manifest's content and mtime change on every
re-run by design, and step 9 absorbs it.)
*Then:* `build_members_manifest.py`, rule 3.01, sentinel rewiring, `.guard_ok`
retirement, `master_seed`'s config home, the chunked digest helper, and the
**test migration** for `tests/test_guard_invalidation.py` and
`tests/test_climate_store_contract.py:339-347` (§4.1). The sweep is untouched;
the workflow still runs the v1 way.

### Step 2 — Per-realization generation

*Falsifier first:* the characterization script (C-16), run against the step-0
baselines to establish the *before* statistics while the old code still exists,
with the acceptance thresholds stated in C-16 rather than left to the validator's
judgment.
*Then:* `prepare_weagen_config_rlz`, the three `generate_weather.R` changes
(including the **checked `publish_file` publication** of the date CSVs and
figures, §4.2), the `{rlz_num}` wildcard. GF-24 (C-27) is runnable from this
step — it needs only generation, not the sweep.
**Value-changing** — this is the documented re-baseline.

### Step 3 — Persistent baselines, WG-4 lifecycle

*Falsifier first:* a job-count assertion — re-materializing one perturbed member
must not re-run generation (v1: 19 jobs, P5).
*Then:* drop `temp()` from the baseline output. Verify the perturb identity leg
against the step-0 operands (tolerance 0).

### Step 4a — Extract the downscale entry point (separately verifiable, no sweep code)

*Falsifier first:* run the **existing** rule 3.09 through the extracted callable
and require tolerance-0 identity on the WG-6 forcing and the HM-4 TOML against
the step-0 capture.
*Then:* `run_downscale(...)` per §2.5, with the `script:` entry reduced to a
guarded shim. Nothing else changes; the v1 workflow still runs.

This is its own step because the module reads the `snakemake` global at **module
top level** with no function and no guard (`downscale_climate_forcing.py:11-25`,
per its own comment), so "`downscale_climate_forcing.py`'s body, in-slot" is not
callable and §9.6's Downscale parity leg has nothing to run against until the
extraction lands. R5 did exactly this once for `prepare_weagen_config.py` — that
module's docstring records the shape to copy. Burying it inside step 4 would put
an unscoped refactor of a hydromt-touching module inside the milestone's core
step.

### Step 4 — The sweep runner and worker pool (the milestone's core)

*Falsifier first:* unit tests, all Julia-free and Wflow-free, for: the ledger
fold (including a **same-`ts` `claimed`/`succeeded` pair**, §5.2); the
crash-consistency rules (§5.3, **all five rows** — the four illegal sequences
**and both named legal repair histories**, same-hash repair and changed-hash
invalidation, which must fold cleanly rather than raise); the state machine
(§5.4, both the `member_hash` and the input-digest invalidation clauses); the
five reuse conditions (§5.5); the **assignment protocol** (§6.1:
claim-before-dispatch ordering, dead-slot recovery from the assignment table
with a fully-sent result drained first, a partially-sent result collapsing to
W2, `ack` carrying no recovery weight); the `get_override` precedence rule
(§4.3); the `os.replace` bounded retry (§5.3); the lock's pid + creation-time
liveness (§6.6); and the line protocol against a **stub** worker, including
GF-14's stderr flood and the per-member `log` routing of §6.2.
*Then:* `run_sweep.py`, `sweep_slot.py`, `wflow_worker.jl`,
`scripts/sweep_status.py` (with `--verify`, §7.5), and the
`onstart`/`onsuccess`/`onerror` lock handlers.
*Then:* a 2-member fixture sweep, followed by GF-1..GF-5, GF-8, GF-11, GF-14,
GF-16, GF-17, GF-19, GF-20.

**`sweep_status.py` lands in this step, not later** — it is the replacement for
the `--dry-run` visibility the step removes (§7.5), GF-2's recovery sequence
names it, and GF-15 needs its `--verify`.

**The performance floor is measured at the END of this step, not at step 8.**
§14.1 names the floor as the decision point that would reinstate batching — but
step 5 *deletes* the `run_wflow_batch_<b>` family and rejects the `batch_size*`
keys, so a floor measured at step 8 sits three steps past the point of no return,
where "stop" means reverting five landed steps including contract, validator and
doc rewrites. The realistic outcome of that ordering is that the floor gets
*accepted* rather than enforced. Measured here, the pool and the batch rules
exist in **one tree**, the comparison is same-tree, and the revert is one step.
The **full counterbalanced protocol** — ≥ 3 AB/BA pairs, median gate — runs
here; protocol and comparands: §13 step 8, which becomes the confirmation run.

### Step 5 — Retire the old rules; ledger-driven reduce; the long table

*Falsifier first:* the reduce identity leg — run the **new** reduce over the
**step-0** member CSVs and require `Qstats.csv`/`basin.csv`/`RT_*.csv`
byte-identical (C-10); the re-pivot test at parsed-value equality (C-11); the
digest-refusal test (GF-15); the cell-drop tests for both `allow_partial`
sub-cases (C-17); and a unit test pinning `_reject_retired_keys`.
**One retention hazard inside this deletion, named because it silently
reintroduces repo-fit-2's failure.** The guarded `_cores` binding sits *inside*
the batch block (`Snakefile_climate_experiment:482-519`: `_k_members` → `_cores`
→ `_positive_batch_key` → `batch_size` → `_batches` → the rule loop). Rule 3.08
declares `threads: _cores`, so deleting the block wholesale takes `_cores` with
it and turns the sweep rule into a parse-time `NameError`. **`_cores` is retained
and relocated** above the rule set; `_k_members`, `_positive_batch_key`,
`batch_size`, `batch_size_max` and `_batches` go.

*Then:* delete 3.05/3.07/3.09/3.10-family, rewire 3.07 catalog inputs **and
`prepare_climate_data_catalog.py`'s entry-list derivation** (a script change,
§10 WG-5), rewrite 3.11 → 3.09 per §4.4's four plumbing changes, add
`response_long.csv` to the outputs and to `WF3_TARGETS`, and reject the retired
`batch_size*` keys.

### Step 6 — Contracts, validators, tooling, docs

**Blocking sub-step, before the step-7 gates can mean anything (§10b):** in
`dev/scripts/semantic_tree_diff.py` — add `_state` to `EXCLUDED_DIR_NAMES`
(`:145`), update the exact-file path-map rule for the renamed date CSVs
(`:357-360`) together with `tests/test_semantic_tree_diff.py:621-622`, and remove
the dead `.project_consistency_ok` allowlist entry (`:201`) and its comment
(`:381`). Then confirm the wf3 `check_baseline.py` slice takes
`response_long.csv` and takes **nothing** from `_state/`.

Then, the full inventory — v1's list omitted the last five and each is something
the milestone actively invalidates:

| Item | Change |
|---|---|
| `validate_wg3` | per-realization form, its two new keys, the `seed` override |
| Both seam docs' `--notemp` sections | replaced by §10a's `retain_member_artifacts` procedure and its restore instruction |
| **Both seam docs, full pass** | producer/consumer/lifecycle/pinned-surface fields, the WG-4 DAG-globbing clause, and the bounded-substitution walkthrough — every retired rule identity (§10) |
| `validate_hm7` + gauge-column relational | extended for the long table |
| `dev/workflows/climate_experiment.md` | rewritten |
| `dev/conventions/naming.md` | gains the member-id vocabulary; **and `:77-84`'s `st_num` paragraph**, which names `downscale_climate_realization`, `run_wflow` and `generate_climate_stress_test` — three rules this design deletes |
| `AGENTS.md` | Repo Map / Key Commands / the `temp()` convention line, plus the undeclared-writes convention (R-6) so it does not read as an oversight |
| `dev/followups.md` § Post-P3-3 | the two items closed as superseded; **R9-F1 and R9-F2 opened** (§15.3) |
| `docs/migration-r09-wf3.md` | written (R8 precedent), carrying the OQ-1 inertness statement §9.1 points at |
| `dev/scripts/estimate_batch_makespan.py` + `tests/test_estimate_batch_makespan.py` | **Retained**, not retired: §6.4 cites the estimator as the argument for why a static partition strands stragglers, and §14.1 needs it if the floor check ever reinstates batching. Its docstring gains one line stating it describes a *retired* lever and is kept as P3-3 evidence |
| `tests/test_workflow_climate_experiment.py:9,28` | docstring job counts ("12 Wflow runs", "56 jobs under `--forceall`") updated to v2's 13 jobs. Integration-gated, so nothing in step 7 would catch this drift |
| `weather_generator/config/` | removed from the R07 layout map (§4.2) |

### Step 7 — Full gate sweep

`pytest tests/`; `pytest tests/test_cli.py` (three Snakefile dry-runs);
`pytest tests/test_interchange_contracts.py -rs`; a `retain_member_artifacts=true`
capture to un-skip **all three** temp validators (§6.6 suppresses the step-3 and
step-5 deletions, so `validate_wg4`'s perturbed-NC case is genuinely reachable);
the paired identity run (C-7, §9.6's reset protocol) and the scoped tree diff
(C-7s); GF-1..GF-24 (GF-21 on its scratch config variant, §8.2).

### Step 8 — Performance floor confirmation

The **binding** measurement happened at the end of step 4, where the revert is
one step (see there). Step 8 re-runs it on the finished tree.

**Protocol, stated because the comparison is invalid without it.** v2 gated the
3.08 makespan against P3-3's 228.1 s 3.10-stage makespan — **not like-for-like**:
3.08 performs perturbation, downscaling *and* simulation, while 228.1 s measures
simulation only, with the P3-3 record assigning ~156 s to the upstream work
(`dev/p33/batching-results.md:113-114`). That gate could fail a correct fused
implementation for carrying work its comparand never performed — inviting
implementers to game the timing boundary — or, symmetrically, could not
establish G7 against batching at all. v3 fixed the boundary but still gated on
**one** batch-first/pool-second timing pair: the pool leg systematically
inherits filesystem and OS-cache warming from the batch leg, and ordinary
timing noise can independently reverse a strict single-observation comparison
— so a stop-and-review gate could retain or reject the architecture on run
order or noise. The floor is therefore measured **across one scientific
boundary, both legs in the same step-4 tree** where the batch rules still
exist, **as a repeated, counterbalanced protocol**:

- **Boundary:** start = a tree with prepare, generation (persistent baselines),
  WG-2 grid and catalog complete; end = all 12 member CSVs present. This is the
  span the pool replaces, whichever rules implement it.
- Same box, AC online, `LoadPercentage` verified low, no sibling agent session —
  the P3-3 § Measurement conditions contract. **`p × M` held at `3 × 4 = 12`**
  in both legs. (This budget binds the floor check only; C-7's identity runs
  deliberately vary depth.)
- **Batch leg:** delete the member-scoped artifacts (member CSVs, TOMLs,
  forcing, outstates, per-`(rlz,cst)` weagen configs; the perturbed NCs are
  `temp()` and already absent), then `SM <the 12 member CSV paths>` at `-c 3,
  --threads 4` — Snakemake runs exactly 3.05_st + 3.07 + 3.09 + 3.10, stopping
  at the CSVs. The invocation wall is the batch boundary span.
- **Pool leg:** delete the same set plus `_state/`, then
  `SM <exp_dir>/_state/ledger_final.csv` with `sweep_workers=3,
  wflow_threads=4` — runs 3.01 (ms-scale, rides along and is reported) and
  3.08. The invocation wall is the pool boundary span. Snakemake parse overhead
  is present in both legs equally.
- **Repetition and counterbalancing, predeclared:** **at least 3 AB/BA pairs**
  — pair 1 batch-first (A→B), pair 2 pool-first (B→A), pair 3 batch-first,
  alternating strictly, each leg preceded by its own deletion reset so every
  leg re-executes the full boundary span. Counterbalancing is what removes the
  systematic filesystem/OS-cache warming advantage the second leg of any pair
  inherits; repetition is what keeps one noisy wall-clock draw from deciding
  the gate. More pairs may be added (odd or even count, alternation kept); the
  count is declared **before** the first pair runs, never after seeing spans.
- **The gate: median pool span ≤ median batch span**, medians taken over all
  runs of each leg across the pairs. Nothing else is binding. **Every
  individual span and the per-leg dispersion (min / median / max) are
  reported** alongside the verdict, so a reviewer can see whether the medians
  sit clear of the spread or the gate rode on a knife edge — a near-tie at
  visibly overlapping dispersions is reported as such to the stop-and-review
  discussion, not silently passed.
- **Component timings reported separately**, so the span verdict is
  decomposable: pool = the ledger's per-member
  `seconds.{perturb,downscale,simulate}` (with `seconds.simulate` the direct
  measurement of `S_warm` at pool depth — the term the whole design rests on);
  batch = the per-rule benchmark rows for 3.07/3.09/3.10. P3-3's 228.1 s and
  400.2 s figures are reported beside them as historical context, gating
  nothing.
- **At-scale advantage is stated as a model** from measured `F`/`S_cold`/`S_warm`,
  never claimed as measured, unless a production-sized sweep is actually run
  (success criterion 8).

### Step 9 — One manifest re-record, then seal

`check_baseline.py record --workflow climate_experiment`, scoped to wf3's slice,
after the delta has been characterized (not before). Expected: `Qstats.csv` and
`basin.csv` change (generation is value-changing, §9.6), `response_long.csv` is
added (as a plain CSV with no comment lines — §4.4 states why), and **nothing
from `_state/` enters the manifest** (§10b — the manifest pins products,
`_state/` holds provenance). `RT_*.csv` and `indicators/completeness.csv` stay
out (§10).

**Named test breakage this step causes:** `tests/test_check_baseline_scope.py`
pins the exact per-workflow cardinality
`{"model_creation": 5, "climate_projections": 6, "climate_experiment": 3}`
(`:86-95`) and asserts `len(targets) == 14` (`:147`, `:180`). The 4th wf3 target
makes those **4** and **15**. The file runs on a bare checkout, so both CI legs go
red at the step that lands the change unless it is updated here.

Then the roadmap R9 section, the status lines, and `dev/followups.md`'s R9-F1 /
R9-F2 entries.

**Gates between steps:** step 0 is blocking. Steps 1–3 and 4a may land
continuously. **Step 4 is a stop-and-review point** — it is where incrementality
leaves Snakemake, and it is where the binding floor measurement now sits, so it
is also the last point at which reinstating batching (§14.1) costs one revert.
Step 8 confirms.

---

## 14. Alternatives considered

### 14.1 Keep P3-3 batching; tune it

Status quo: parse-time batch rules, LPT partition, `batch_size_max` clamp.
**Rejected** because three of the five §1.1 pains are structural to it: the
warm-session discount is bounded by `B` (P1), the blast radius is `B` by
construction (P3-3 GN-4), and the disk ceiling needs a parse-time estimate that
cannot exist (`dev/followups.md` § Post-P3-3). **Would become preferable if** the
pool's **median** same-boundary span, over C-12's counterbalanced pairs, lost to
batching at fixture scale —
the floor check is precisely the decision point that would reinstate it, which is
why §13 moves the binding measurement to the **end of step 4**, while the batch
rules still exist and the revert is one step.

### 14.2 Snakemake checkpoints / dynamic rules for the sweep

Use a `checkpoint` to re-evaluate the DAG after the manifest exists, keeping one
job per member. **Rejected:** it solves *enumeration* (which members exist),
which is not a problem here — `RLZ_NUM × ST_NUM` is known at parse time — and
solves none of the three structural pains. It keeps one Julia process per member,
so `S_cold` is paid `K` times: strictly worse than the batching it would replace.
**Would become preferable if** the dominant cost were ever `F` rather than the
warm-up (it is not — P1 measured `F ≈ 24 s` against a 57 s warm-up discount).

### 14.2a Snakemake `service:` rules

Declare the Julia worker pool as a `service:` job and keep one DAG job per
member, so members stay visible to `--dry-run` while sharing a warm process.
**Rejected:** a `service:` job's lifetime is bound to the jobs that consume it —
Snakemake starts it for its consumers and terminates it when they finish — so it
amortizes within a consumer group, not across the whole sweep, which is the same
bound batching already has. It also leaves every member a declared-output job, so
PR-4's blast-radius problem (§14.11) returns in full, and it does not address
per-member incrementality after a crash. Recorded here because it is the one
construct that could plausibly have kept per-member DAG jobs *and* a persistent
worker, and a future reader must be able to tell it was considered rather than
missed. **Would become preferable if** Snakemake ever bound a service's lifetime
to the workflow rather than to its consumers.

### 14.3 Coordinate-bearing member ids (`t+2.0_p0.85`)

**Rejected:** floats in path segments invite formatting and precision drift
(`0.85` vs `0.850` vs `8.5e-1`), the ids would be unstable across a config that
changes only the number of decimal places, and the manifest exists precisely to
be the id → coordinate record. **Would become preferable if** member ids ever had
to be stable across a grid resize — which §9.3 records as the genuine cost of the
index-based choice.

### 14.4 A Julia-side queue (`Distributed.jl`)

Workers pull from a Julia-side queue; the Python side hands over the member list
once. **Rejected:** it puts scheduling on the far side of the single-writer
boundary — the ledger is Python's and the queue would be Julia's, so every
member's outcome would cross the boundary twice, and the crash semantics would
have to be reimplemented in the language with the smaller surface in this repo.
It also grows the Julia code this repo maintains beyond a 30-line loop.
**Would become preferable if** the pool ever spanned machines, where
`Distributed.jl`'s transport would earn its complexity.

### 14.5 Adopt `cst-run-control` in full

**Rejected on proportionality** (decision criterion 4). The full contract's
distributed-coordination layer — compare-and-set on `state_revision`, fencing
tokens, content-addressed staging with inventory CAS, conformance vectors,
validity profiles — exists to coordinate multiple executors against a shared
namespace. This sweep has one executor by construction (A1). Adopting it would
also require intercepting Wflow's own output writes to route them through a
staging/seal path, which the CST-scope constraint puts out of bounds.
**Would become preferable if** the CST-API backend ever executed sweeps against
a shared project root — at which point §5.5's row-by-row mapping makes the lift
mechanical rather than a rewrite.

### 14.6 A repo-local design owing nothing to `cst-run-control`

**Rejected:** the concepts that carry the risk here (immutable intent vs mutable
state, append-only attempts, quarantine before resume, digest-verified reuse) are
exactly the ones the contract already names well. Inventing local vocabulary for
them would cost the future adapter and buy nothing.

### 14.7 Threads instead of slot processes

Run the `p` member pipelines as Python threads in the orchestrator. **Rejected:**
`hydromt_wflow` / `xarray` / `rasterio` concurrency safety in one interpreter is
not something this repo has evidence for, a segfault in one thread takes the
ledger writer with it, and the GIL makes the (real, non-trivial) Python-side work
of the downscale contend. Slot processes give crash isolation for free.
**Would become preferable if** slot-process memory footprint (`p` hydromt
imports) ever became the binding constraint.

### 14.8 A fresh subprocess per member, no persistent Python layer

Orchestrator spawns a short-lived Python process per member, keeping only the
Julia workers persistent. **Rejected:** it pays a full Python + hydromt import
per member, which P3-3's 342–359 s of non-3.10 work suggests is material.
**Retained as the fallback** if H4 fails — it is a strictly simpler topology and
loses only the C-4 win.

### 14.9 Seed derivation including the experiment name

`sha256(f"{master_seed}:{experiment}:rlz:{r}")` would give sibling experiments in
one project independent realizations. **Rejected:** it makes renaming an
experiment silently change its results, which is a worse property than two
experiments sharing a realization set — and sharing is arguably *desirable*,
since it makes cross-experiment comparison a controlled one.

### 14.10 Keep 3.06's joint generation

Retain one job emitting all realizations, changing only the sweep. **Rejected:**
it preserves pain 4 (no cross-realization parallelism) and pain 5 (the `temp()`
cascade) and would leave the `--notemp` capture as expensive as P5 measured. Its
one virtue — no re-baseline — is real but is a one-time cost against a permanent
structural one.

### 14.11 Declare the per-member CSVs as sweep outputs

The "obvious" way to keep Snakemake's freshness. **Rejected on probe evidence**
(PR-4): Snakemake removes a failed job's declared outputs, so one failing member
would delete all `K−1` completed sibling CSVs — blast radius = the whole sweep,
strictly worse than batching's `B`. This is the single most important rejected
alternative in the document.

### 14.12 SQLite instead of append-only JSONL for the ledger

**Rejected:** it would buy transactional multi-writer semantics this design does
not need (A1), cost the human-readable audit trail (`ledger.jsonl` is greppable
and diffable), and add a binary artifact to a tree whose comparison tooling
(`semantic_tree_diff.py`) is text- and netCDF-oriented. It is in the standard
library, so the dependency argument does not apply — this is a legibility call.

### 14.13 PackageCompiler sysimage

**Rejected, carried forward from P3-3's adjudication:** it attacks `F ≈ 24 s`,
which is not where the cost is, and at measured terms the estimator puts it at
−19 % against batching's −52 %. The pool makes the case weaker still: `F` is paid
`p` times per *sweep*, not per member.

### 14.14 Live member-CSV digests in the reduce's parse-time freshness

Thread a digest over the result files `ledger_final.csv` lists through the
reduce rule's `params:`, so post-completion corruption of an undeclared member
CSV re-triggers the reduce on an ordinary re-invocation (the mechanism ext1-4
offered as its first branch). **Rejected on price:** the digest must be computed
at Snakefile **parse** time on *every* invocation of *any* command — `--dry-run`
and `--unlock` included — over `K` member CSVs, reintroducing `K`-scaling into
exactly the path §4.5 removed it from and breaking C-2's cheap-no-op contract at
production scale; and the detection it buys still fires only when the user next
invokes the workflow, which is precisely when `sweep_status.py --verify` is
available at zero standing cost. The narrowed claim plus the explicit command
(§4.4, F8, GF-15) delivers the same detection, priced where it is used.
**Would become preferable if** the reduce's inputs ever became mutable by a
process outside this workflow's contract as a matter of course, rather than as
the out-of-contract corruption F8 models.

---

## 15. Limitations, residual risk, and open items for G1

### 15.1 Residual risk

| # | Risk | Severity | Mitigation / posture |
|---|---|---|---|
| R-1 | Incrementality is now our code. A ledger bug can silently skip a member that should re-run | **High** | The state machine, the fold, and the crash rules are unit-testable without Julia (§13 step 4); GF-2/GF-3/GF-5 are the behavioural gates; `sweep_status.py` makes the fold's verdict inspectable |
| R-2 | `--dry-run` no longer shows pending members | Medium | Stated openly (§7.5); `sweep_status.py` is a required deliverable |
| R-3 | No true fencing. `invocation_id` identifies a superseded writer's rows but does not prevent them | Low under A1 | The `O_EXCL` lock is the real barrier; a writer that bypasses the lock is out of contract. `cst-run-control` records the same class of limitation |
| R-4 | No per-member wall-clock ceiling, so a genuinely hung Wflow run hangs the slot | Medium | **Deliberate, and re-affirmed in v2 after review pressure.** A wrongly-sized timeout kills good work, and members legitimately run for minutes; a *kill* path on the milestone's riskiest new component is itself a risk, and a data-derived ceiling still needs a warm-up window in which it does not apply. What v2 *does* do is remove the one mechanism by which a **healthy** worker was known to be able to block forever: §6.2's stderr-drainage rule, gated by GF-14. What remains uncovered is a genuinely wedged `Wflow.run` — visible in the orchestrator log as a member with no finish line, recoverable by kill + resume (F5), and revisited with data from a production-sized sweep. **Flagged for G2 as a rejected review part** (risk-7's third suggested fix) |
| R-10 | Session depth at production scale is untested for both numerical identity (A4) and memory stability (H5) | **High, structurally unclosable on the fixture** | §2.2 states the gap; C-7 tests 3x P3's depth, which is all 12 members can give; `worker_max_members` ships as the pre-designed knob; §15.3 names the re-verification trigger |
| R-5 | Dropping `environment_digest` lets a sweep mix engine versions | Medium | `run.tools` makes it detectable; C-13 is the falsifier that would promote `tools` into `member_hash` |
| R-6 | Undeclared writes (ledger, member CSVs) invert the repo's R07 B6 correction | Low | Justified structurally (§3.2) and compensated by §7.5; must be stated in `AGENTS.md`'s conventions so it does not read as an oversight |
| R-7 | The generation re-baseline breaks comparability with every existing experiment tree | **High, accepted** | Documented in `docs/migration-r09-wf3.md`; one manifest re-record; baseline-provenance stamping (R7-21) guards fixture sharing |
| R-8 | Windows `spawn` + persistent Julia children is unproven at sweep length | Medium | H4/C-5; §14.8 is the pre-designed fallback |
| R-9 | Protocol corruption by Wflow stdout | Medium | H1/C-6; `redirect_stdout(stderr)` is the designed containment, unverified with Wflow loaded |

### 15.2 Gate G1 rulings, and what they closed

Every item v1 carried into G1 was ruled on 2026-08-01. Recorded here so a fresh
reader sees the settled state rather than an open list:

| Item | Ruling | Where it lives in this document |
|---|---|---|
| OQ-1 `precip_variance` | **DEFERRED ENTIRELY.** No `scale_var_with_mean` change; axis inert; field retained in every schema; `verbose = TRUE` carved out at gate-return as value-neutral | §9.1 (rewritten), §4.4, §5.1, §10 WG-2 |
| OQ-4 reduce posture | Fail-loud default + `allow_partial`; **no** completeness threshold | §9.4 (rewritten), §4.4, GF-6/GF-7/GF-13 |
| Drift guard | Three-layer reading **ratified** | §7.1 |
| `response_long.csv` in the baseline manifest | **Yes**, at the single re-record | §10b, §13 step 9 |
| Milestone id | **R9**, prefix `r09:`, home `dev/workflows/` | §13 |
| Fixture arithmetic (gate-return) | **Recompute at K=12**; the fixture is not flipped | header, §4.5, §8.2 |

### 15.3 Known limitations, and the two named followups

- **R9-F1 — activate or retire the `precip_variance` axis.** The axis ships inert
  and documented (§9.1). Activation is value-changing (a full re-baseline of
  `Qstats.csv`, `basin.csv`, `RT_*.csv` and `response_long.csv`), and it also
  removes the false-invalidation cost §5.1 names. Tracked in `dev/followups.md`
  at §13 step 6; owner-scoped, not this milestone's.
- **R9-F2 — an elevated-`realizations_num` generation characterization.** C-16's
  acceptance thresholds are what n=2 can carry; a genuine distributional verdict
  on the re-baseline needs 20+ realizations, generation-only (cheap now that
  stage 2 is independently parallel, but not free, and it is not on the critical
  path of any gate). Tracked with R9-F1.
- **A4/H5 at production depth.** The fixture gives 12 members per session at
  most; production gives hundreds. **Named trigger:** the first production-sized
  sweep re-runs C-7's paired comparison on a subset of its own members and
  reports the ledger's `seconds.simulate` and worker RSS trend; if either moves,
  `worker_max_members` is the first lever.
- Member ids are not stable under a stress-grid resize (§9.3).
- The design assumes single-machine execution throughout; no part of it is wrong
  under multi-machine execution, but several parts (the lock, the single-writer
  ledger, the `p x M` budget) would need replacement rather than extension.
- The at-scale performance advantage is a **model**, not a measurement, until a
  production-sized sweep runs (§13 step 8).
- H1–H5 (§11.3) are carried into implementation as falsifiers rather than settled
  here; three of them need Wflow loaded, which drafting could not do.
- `--dry-run` cannot report pending members (§7.5), and no mechanism recovers
  that inside Snakemake — `scripts/sweep_status.py` compensates, it does not
  restore.


## 16. References

**Scope and process**
- `dev/workflows/wf3-climate-experiment-v2-intake.md` — scoping intake (scope authority)
- `dev/working/design-runs/wf3-experiment-v2/intake.md` — run intake, evidence register, gate materialization, derived-artifact register
- `dev/workflows/wf2-climate-analysis-v2-design.md` — R8 genre precedent

**Current implementation**
- `Snakefile_climate_experiment` — the v1 workflow (rule numbering cited throughout)
- `blueearth_cst/experiment/{run_wflow_batch.jl, prepare_cst_parameters.py, prepare_weagen_config.py, downscale_climate_forcing.py, export_wflow_results.py, check_project_consistency.py}`
- `blueearth_cst/weathergen/{generate_weather.R, impose_climate_change.R}`
- `blueearth_cst/shared/snake_utils.py` — `climate_store_spec`, `stress_test_grid`, `get_config`, `file_digest_or_absent`

**Evidence**
- `dev/p33/batching-results.md` — P1–P4, GN-1..4, the estimator, the measurement-conditions contract
- `dev/followups.md` § Post-P3-3 — the two items this design absorbs
- `dev/p31/experiment-structure-design.md` §3/§3a/§3b/§3d — the drift-guard mechanism

**Contracts**
- `dev/contracts/weather-generator-seam.md` — WG-1..WG-6
- `dev/contracts/hydrological-model-seam.md` — HM-1..HM-7
- `dev/conventions/naming.md` — naming, `cst_0` reservation

**Run-control**
- `~/workspace/brain/artifacts/skills/cst-run-control/SKILL.md` and
  `references/{manifest-schema.md, state-transitions.md, resume.md}` — the contract §5.5 subsets

**Upstream (read-only)**
- installed `weathergenr` v1.2.0 @ `9f3d3189…` — the E1 authority (§9.1)
- `~/workspace/weathergenr/R/climate_perturbations.R` — corroborating, **not** the installed build

---

## 17. Revision log

| Date | Revision | Change |
|---|---|---|
| 2026-08-01 | v1 | Initial draft. Settles OQ-1..OQ-7 (OQ-1 and OQ-4 as provisional owner rulings). Six probes run during drafting (PR-1..PR-6); P6 upgraded from hypothesis to measured on the installed build, with the intake's source citation corrected. Architecture: 4 stages, 12 rules, one declared sweep output, manifest + append-only ledger, three-level process topology, `p × 1` disk ceiling. |
| 2026-08-01 | **v2** (revision r1) | All 52 internal-panel findings dispositioned (`ledger.md`). **No architectural change** — every fix is to a claim the architecture rested on. See below. |
| 2026-08-01 | **v3** (revision r2) | External round 1 dispositioned: ext1-1..ext1-6 (`ledger.md`). Five of the six fault v2 *mechanisms* (the resolutions of risk-7, arch-13, risk-12, risk-3, risk-10); each is **replaced in place**, not patched. See the table below. |
| 2026-08-01 | **v4** (revision r3) | External round 2 dispositioned under **owner arbitration 2026-08-01** (round cap reached; all seven of ext2-1..ext2-7 accepted, fix required — `ledger.md`, `status.md` arbitration entry). Four fault compositions of r2 fixes (ext2-2..ext2-5). See the table below. |

**What v2 changed, and which findings drove it.** The architecture of §3 is
untouched; eight of the twelve changes below repair a *claim* the design made
about the repository or about its own mechanisms.

| # | Change | Driven by |
|---|---|---|
| 1 | **Fixture arithmetic recomputed at K=12** throughout — no `cst_0` members, `aggregate_rlz: true`, 6 grid rows per statistic. Header, §4.5, §6.4, §7.5, §8.2 (GF-6/7/9/12), §12 C-3, §13 step 0. The fixture is **not** flipped | arch-1 (B), risk-9 (M), G1 gate-return |
| 2 | **One coherent freshness mechanism.** `member_hash` gains `seed_r`, `weagen_template_digest` and `st_params_digest` (replacing the uncomputable `st_csv_digest`); reuse gains a **fifth condition** over recorded *input* digests verified at sweep start. §5.1, §5.2, §5.4, §5.5, §7.1, §7.3, §7.6, GF-12, C-18 | risk-1 (B), arch-3 (B), arch-2 (B), arch-7 (M), repo-fit-10 (m) |
| 3 | **`allow_partial` is cell-complete.** Incomplete response-surface cells are **dropped**, never under-averaged, zero-filled or crashed; the reduce sizes frames from the succeeded set; `IncompleteCellError`; per-cell `n`. §4.4, §9.4, §9.6, GF-7 (two sub-cases), C-17 | arch-15 (B), risk-2 (B), repo-fit-6 (M), risk-5 (M) |
| 4 | **One experiment lock for the whole workflow**, claimed in `onstart` and released in `onsuccess`/`onerror`, with pid + creation-time liveness, auto-clear when provably gone, and a **named** recovery command. Probe **PR-7** added. §5.3, §6.6, §8.1 F10/F11, GF-2, GF-8, C-20 | risk-6 (M), repo-fit-1 (B), repo-fit-14 (m) |
| 5 | **Rule 3.08 becomes a `shell:` rule** through `run_logged.py` with an import-cheap guarded orchestrator and a separate slot module; `threads: _cores` not `workflow.cores`; the `staticmaps` DAG edge dropped; a stated `--config` override precedence. §4.3, §6.1, §6.4 | repo-fit-8 (M), repo-fit-2 (M), repo-fit-3 (M), arch-6 (M) |
| 6 | **Log/benchmark layout corrected**: one shape per label (`_orchestrator.log` inside the part dir), per-member benchmark TSVs dropped in favour of the ledger. §6.5 | arch-4 (B), repo-fit-4 (M), arch-11 (m) |
| 7 | **C-7 redefined as a paired same-input comparison** (`sweep_workers` 12 vs 1); the whole-tree diff retained separately and scoped as C-7s; A4's production-depth gap stated; `worker_max_members` added. §2.2, §6.3, §9.6, §11.3 H5, §15.1 R-10 | risk-3 (M), risk-4 (M) |
| 8 | **Partial sweeps are retryable** via an undeclared `sweep_incomplete.json` whose digest is a `params:` value; second-order effects stated. §5, §7.2, §8.1 F1, GF-13, C-19 | risk-5 (M) |
| 9 | **The floor's binding comparand is the 228.1 s sweep-stage makespan**, and the measurement moves to the end of step 4 where the batch rules still exist. §13 steps 4/8, §14.1, C-12 | risk-10 (M) |
| 10 | **§9.1 rewritten to the G1 deferral** — the "activate" recommendation is gone; inertness documented at three consumption points; `verbose = TRUE` carved out with its log destination named. Stale OQ-1 sites cleared in §2.6, §4.4, §5.1, §10, §11.1, §15.2 | risk-18 (m), repo-fit-13 (m), G1 + gate-return |
| 11 | **Gate set completed and mapped**: GF-12..GF-18 added, F→GF coverage table with a stated "no gate, reason" cell; `service:` rules dispositioned in §14.2a | risk-16 (m), risk-12 (M), risk-13 (m), risk-7 (M) |
| 12 | **Unowned work given owners and steps**: the downscale extraction as its own step 4a, `prepare_climate_data_catalog.py`, the reduce rewrite, the weagen-config change, and five named test-migration items across steps 1, 5, 6 and 9 | arch-9 (M), repo-fit-5 (M), repo-fit-7 (M), repo-fit-13 (m) |

Smaller but normative, each closing one finding: finalization order and
completeness identity fields (risk-8); transition legality as a crash-consistency
row (arch-13); file order authoritative for the fold (risk-17); reduce digest
verification (risk-12); `os.replace` bounded retry and UTF-8 pipes (repo-fit-14,
repo-fit-17); chunked `staticmaps` digest (repo-fit-15); `retain_member_artifacts`
covering step 3 (arch-5); `RT_*` and `WF3_TARGETS` dispositioned (arch-10);
completeness-record row population unified with a JSON sidecar (arch-12);
`config_digest` enumerated, WG-3 key count corrected, `weather_generator/config/`
retired (arch-14); `exp_dir` path rejoin in the reduce (arch-16); C-11 as
parsed-value equality (repo-fit-12); `sweep_status.py` moved to `scripts/`
(repo-fit-9); retired-key rejection given a mechanism (repo-fit-11); the
undeclared-read constraint stated (repo-fit-16); the date CSVs kept in `output/`
under R07's ruling with per-realization names (risk-11); `tools` drift made
mechanical (risk-13); orphan transients swept by the fold (risk-19); C-16 restated
to what n=2 supports with R9-F2 named (risk-14); manifest determinism asserted
minus `run.created_at` (risk-15).

**One review part was rejected rather than adopted**, and it is flagged for G2:
risk-7's third suggested fix, a data-derived per-member wall-clock ceiling. The
finding's core defect — the stderr-drainage hang — is closed normatively in §6.2
and gated by GF-14. The ceiling itself is declined for the reasons stated at
§15.1 R-4: it adds a kill path to the milestone's riskiest new component, and the
hang class it would backstop no longer has a known mechanism.

**What v3 changed, and which external findings drove it.** The architecture of
§3 is again untouched; every change replaces a v2 mechanism the external round
showed could not deliver its own claim.

| # | Change | Driven by |
|---|---|---|
| 1 | **Parent-owned assignment replaces the shared pull queue.** Per-slot duplex pipes + process sentinels; `ready`/`assign`/`ack`/`result`/`stop`; the `claimed` row fsync'd **before** dispatch; an assignment table (`slot_id → member_id`) that names any dead slot's in-flight member; four crash windows enumerated, the dequeue-and-die window structurally gone. §6.1, §5.3, §6.3 Drain, §6.4, §8.1 F4, GF-16 restated, **GF-19**, **C-21**, §13 step 4 | ext1-1 (B) |
| 2 | **Per-member log routing.** Spawn-time stderr becomes the per-worker lifecycle log `_worker_<id>.log`; the `run` message carries the member's `log` path and the worker redirects stdout+stderr at fd level around `Wflow.run` into it, answering on the restored protocol stdout; sequential single-writer handoff on the member log. §6.2, §6.3 Spawn, §6.5, GF-14 restated, **GF-20**, **C-22**, H1. The risk-7 part-3 rejection (no wall-clock ceiling) **stands**: no stream is ever an undrained pipe under the new routing | ext1-2 (M) |
| 3 | **Epoch-scoped transition legality.** Legality per `(member_id, member_hash)` sub-sequence; `quarantined` rows close epochs and carry the superseded hash; repeated success illegal only *without* an intervening `quarantined`; both legal repair histories named as passing unit tests. §5.2, §5.3, §5.4, §13 step 4 | ext1-3 (M) |
| 4 | **F8's detection claim narrowed to what executes**, and an explicit integrity command added. The reduce-time digest check fires whenever the reduce runs; an ordinary re-invocation after a clean sweep runs nothing and detects nothing — stated, and gated as such; `sweep_status.py --verify` + the `ledger_final.csv` deletion repair lever; GF-15 rewritten as a four-observation sequence; the parse-time-digest alternative priced and rejected. §4.4, §7.5, §8.1 F8, GF-15, C-10, **§14.14** | ext1-4 (M) |
| 5 | **C-7's legs isolated and forced.** Both legs `sweep_workers: 1`; depth varied by `worker_max_members` 1 vs 0; execution forced by a named state reset between legs, never by a hash change (GF-11's skip semantics intact); both captures taken before comparison; `sweep_workers`/`worker_max_members` join the `--config` override set. §2.2, §4.3, §4.5, §6.4, §9.6, §12 C-7, §11.1 P3, H5 | ext1-5 (M) |
| 6 | **The floor compares one scientific boundary.** Both legs measured in the step-4 tree from prepare/generation/catalog-ready to all 12 member CSVs (batch leg = forced 3.05_st+3.07+3.09+3.10; pool leg = 3.08); gate = pool span ≤ batch span; component timings reported; 228.1 s / 400.2 s demoted to context. G7, §11.1 P2, §12 C-12, §13 step 8, §14.1 | ext1-6 (M) |

**What v4 changed, and which arbitrated findings drove it.** The architecture
of §3 is again untouched. The external round cap (2) was reached at
convergence-r2; the owner arbitrated all seven surviving findings as ACCEPTED,
FIX REQUIRED (2026-08-01), and every change below implements the arbitrated
ruling — the arbitration record in `status.md` carries reviewer authority.

| # | Change | Driven by |
|---|---|---|
| 1 | **Baseline member lifecycle specified.** `baseline: true` / `st_csv: null` members skip spec-write and perturb entirely, downscale the persistent baseline NC directly (mirroring retired rules 3.07's `st_num >= 1` constraint and 3.09's direct `cst_0` pass-through), record `inputs.st_csv = null` / `inputs.weagen_template = null` (defined-absent in reuse condition 5) and `seconds` without `perturb`; the baseline NC is excluded from every deletion set — member steps, resume-fold cleanup, quarantine inventory. §5.1, §5.2, §5.5, §6.6 (baseline branch), §7.3 step 8, §4.4 asymmetry note; **GF-21** (untracked scratch `run_historical: true` config variant, tracked fixture unchanged), **C-23** | ext2-1 (B), owner arbitration 2026-08-01 |
| 2 | **The lock-minted `invocation_id` is authoritative; finalization vs member provenance split.** `onstart` mints once; `run_sweep` **adopts** from `_state/experiment.lock` (absent ⇒ named `ExperimentLockMissingError`, never a fallback mint). `ledger_final.csv` splits per-member `succeeded_invocation_id` from uniform `finalization_invocation_id`; the completeness identity check validates against the latter only, so resumed/retried sweeps with mixed-invocation successes reduce cleanly. §5.2, §6.6, §7.3 step 1, §10b; GF-2 and GF-13 extended through successful reduction; **C-24** | ext2-2 (B), owner arbitration 2026-08-01 |
| 3 | **Stale completeness removed on full-completeness reduce.** A full-completeness reduction deletes any prior `indicators/completeness.csv` (atomic single remove) before publishing; GF-13's final observation asserts absence; C-17 extended. §4.4, §8.2 | ext2-3 (M), owner arbitration 2026-08-01 |
| 4 | **Quarantine recovery as an explicit inventory.** Preserve in place: `experiment.lock`, `members.json`, the quarantine root; move: active ledger/finalization state, `_state/members/`, and every current manifest-owned member output (under `member_products/<member_id>/`); baseline NCs never move; fresh ledger last. §5.3; **GF-22** executes the recovery to completion; **C-25** | ext2-4 (M), owner arbitration 2026-08-01 |
| 5 | **Orphan ledger history decoupled from live artifacts.** A schema-valid sub-sequence for a member absent from the current manifest is legal history whether or not `prune --delete` removed its artifacts (the decoupling branch of the ruling; no tombstones needed); the out-of-manifest illegality clause is removed and §7.4 states pruning never rewrites history. §5.3, §7.4, §8.1 row reference; **GF-23** (resize→prune→reinvoke), **C-26** | ext2-5 (M), owner arbitration 2026-08-01 |
| 6 | **Checked publication for stage-2 sidecars, both surfaces.** One `publish_file(src, dest)` helper — checked remove + checked rename, named loud error on `FALSE` (the "checked rename with a named error" branch; base R has no atomic overwrite and §2.3 forecloses a dependency) — for the two per-realization date CSVs **and** the pre-existing unchecked figures loop (`generate_weather.R:68-73`), publishing to `output/…_rlz_<n>.csv` and `plots/rlz_<n>/`. §4.2, §10 (both WG-3+ rows), §2.5, §13 step 2; **GF-24** (changed-seed regeneration on Windows + held-open destination), **C-27** | ext2-6 (M), owner arbitration 2026-08-01 |
| 7 | **The floor protocol is repeated and counterbalanced.** ≥ 3 predeclared AB/BA pairs (batch-first / pool-first alternating) at the same v3 scientific boundary, every span and per-leg dispersion reported, **gate on the median** pool-vs-batch comparison; component timings still reported. G7, §12 C-12, §13 steps 4/8, §14.1 | ext2-7 (M), owner arbitration 2026-08-01 |

**Body budget — stated, not absorbed.** v1 = 1 903 lines; v2 = 2 969;
v3 = 3 195 (+7.6 % over v2); **v4 = 3 420 (+7.0 % over v3)**. v3's six
mechanisms were rewritten *in place*
(the faulted §6.1/§6.2 topology and stderr paragraphs, §5.3's legality rules,
§9.6's C-7 operand, §13 step 8's protocol, §4.4's F8 claim replace their v2
text, readable in the append-only `design-v2.md`), but a complete assignment
protocol and an epoch-scoped legality specification are net-new normative
surface that one-clause rules could not carry — that gap is what the external
round faulted. v4's growth is the same class: the baseline branch, the
quarantine inventory, the invocation-id split, the checked-publication helper
and four new gates are arbitrated normative surface, replacing text where any
existed (§5.3's recovery, §13 step 8's protocol) and adding where v3 had a
hole (§6.6's baseline branch). The growth remains concentrated in contract,
not prose. **This is a G2 item.** If the accepted body must meet v1's size,
the compressible surfaces in order are: §17's three change tables (~110
lines, their job ends at G2), §5.5's 20-row mapping table, §11.2's probe
transcripts, and §14's fifteen alternatives. Compressing anything in §5, §6.1,
§8.2 or §12 would delete contract.
