# WF3 v2.0 — Climate Experiment: ledger-driven sweep (DRAFT v1)

```
Status:     DRAFT v1 — authored for the design-review-loop run `wf3-experiment-v2`;
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
            Measured size of v1: ~1 880 lines, roughly 45 % of it tables,
            schemas, probe transcripts and gate definitions — the normative
            contract itself rather than prose.
Revisions:
  - 2026-08-01: initial draft (design-v1.md)
```

Scope authority: `dev/workflows/wf3-climate-experiment-v2-intake.md` (commit
`edc0689`). Its § Approved architecture is a **fixed anchor**: this design does
not re-litigate the 4-stage shape, the ledger-driven sweep, the persistent Julia
pool, or per-realization generation. Its OQ-1..OQ-7 are what this design settles
(§9). Run intake: `dev/working/design-runs/wf3-experiment-v2/intake.md`.

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
- **G3 — Peak transient disk = `p × 1` member's artifacts**, independent of sweep
  size, by construction rather than by a tuned constant.
- **G4 — Per-member visibility** — log, timing and status per member, replacing
  the batch-id granularity P3-3 accepted.
- **G5 — Cross-realization parallelism in generation**, with per-realization seeds
  recorded in an artifact.
- **G6 — The seam contracts hold**, with every delta enumerated (§10) and the
  contract docs updated *with* the milestone.
- **G7 — Performance floor:** not worse than P3-3 batching at fixture scale under
  a held `p × M` budget (§13 step 8); the at-scale advantage stated as a model from
  measured terms, never claimed as measured.
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
| `config/templates/weathergen_config.yml` | Tracked template | Seeds the per-realization generator config, including the master `seed` |

Provenance preservation: every result-affecting input above contributes to
`config_digest` or is recorded by digest in the manifest (§5.1), so the run's
own record answers "what was this built from" without consulting the DAG.

### 2.5 Delegated implementation ownership

This design is normative; it authors no code. Each migration step (§13) is handed
to its owner as a scoped brief, with the gate it must pass named. A stage whose
validation handoff has not returned is not integrated.

| Work | Owner role | Gate it must pass |
|---|---|---|
| `build_members_manifest.py`, `run_sweep.py`, `sweep_status.py`, `prune_experiment_orphans.py`, the Snakefile rewrite | `python-engineer` | §13 step-level falsifiers; `pytest tests/test_cli.py` |
| `wflow_worker.jl` (the line protocol, §6.2) | `python-engineer` (Julia surface is 30 lines, seeded by `run_wflow_batch.jl`) | C-6, GF-1 |
| `generate_weather.R` changes (§4.2) | `r-developer` | C-16, the perturb identity leg |
| Fixture sweeps, the `retain_member_artifacts` capture, the performance-floor run | `model-builder` | §13 steps 7–8 |
| Every parity/characterization verdict — generation distributional equivalence, HM-7 byte stability, the seam validator suite, the manifest re-record decision | `model-validator` | §9.6's per-stage table; C-7, C-10, C-11, C-15, C-16 |
| `response_long.csv` schema fitness for the response-surface consumer | `stress-test-analyst` | C-11 |

### 2.6 What this design deliberately does not decide

- The **science** of OQ-1 (`precip_variance` semantics) and the **posture** of
  OQ-4 (reduce with holes). Both are designed as provisional recommendations with
  both branches specified, flagged `[OWNER RULING — provisional]` for gate G1
  (§9.1, §9.4).
- Whether wf3's tidy long table joins the baseline manifest — recommended yes,
  §13 step 9, but it is a manifest-scope decision the owner signs off at the re-record.

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

## 4. Stage specifications

Rule numbering follows the repo convention (`W.NN` = workflow.step in definition
order, a reference aid, not execution order — `dev/conventions/naming.md`). v2
renumbers because the rule set changes shape; §4.5 is the crosswalk.

### 4.1 Stage 1 — Prepare

**3.01 `build_members_manifest`** *(new; absorbs 3.00b `check_project_consistency`)*

| | |
|---|---|
| input | `ancient(wf1_snapshot_path)` (mandatory, unchanged from 3.00b) |
| params | `guarded_sections`, `guarded_sections_digest`, `wf1_snapshot_digest`, `wf2_snapshot_path`, `wf2_snapshot_digest` (all unchanged from 3.00b), plus `config_digest`, `grid` (`rlz_num`, `st_num`, `st_start`), `master_seed`, `policy` |
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
| params | `cftype="generate"`, `snake_config=config_path`, `default_config=config/templates/weathergen_config.yml`, `output_path={wg_dir}/`, `work_path={wg_dir}/_work/rlz_{rlz_num}/`, `middle_year`, `sim_years`, `nc_file_prefix="rlz"`, `rlz_index={rlz_num}` |

`build_weagen_config`'s `generate` branch gains three keys under
`generateWeatherSeries`: `realizations_num: 1` (was `RLZ_NUM`), `rlz.index: <n>`,
and `seed: <derived>` read from the manifest, plus `work.path` (below). Every
other key is unchanged (`prepare_weagen_config.py:54-68`).

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
3. **The generator's own `out_dir` splits from the NC output dir.**
   `weathergenr::generate_weather(out_dir = …)` writes `sim_dates.csv`,
   `resampled_dates.csv` and four diagnostic PNGs; `weathergenr::write_netcdf(out_dir = …)`
   writes the realization NC. They are already independent arguments
   (`generate_weather.R:56` vs `:90`). With `RLZ_NUM` concurrent jobs a shared
   `out_dir` is a write race on the two date CSVs, so the generator's `out_dir`
   becomes the per-realization `work.path` (`_work/rlz_<n>/`) while the NC keeps
   its flat WG-4 path. Figures move to `plots/rlz_<n>/`.

   *Contract note:* the two date CSVs are explicitly **non-interchange**
   (weather-generator seam § Considered and excluded), so this is a documented
   relocation of a non-contract artifact, not a contract break.

**Seed derivation (OQ-5, §9.5).**
`seed_r = int.from_bytes(sha256(f"{master_seed}:rlz:{r}".encode("utf-8")).digest()[:4], "big") % (2**31 - 1)`
computed by the manifest builder and recorded per realization. `master_seed` is
the existing `generateWeatherSeries.seed` from the template config (WG-3 key,
unchanged). The experiment name is **excluded** from the derivation so the same
`master_seed` reproduces the same realizations in any experiment or project —
reproducibility over per-experiment independence (§14.9 records the rejected
alternative).

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
| input | `manifest`, `catalog`, `rlz_nc` (all baselines), `st_csv_fns` (all WG-2 files), `staticmaps = ancient({basin_dir}/staticmaps.nc)`, `data_sources` |
| output | `ledger_final = {exp_dir}/_state/ledger_final.csv` — **exactly one**, per §3.2 |
| params | `exp_dir`, `runs_dir`, `wg_dir`, `model_dir`, `clim_source`, `horizontime_climate`, `run_length`, `sweep_workers`, `wflow_threads`, `member_max_attempts`, `allow_partial`, `retain_member_artifacts`, `config_path` |
| threads | `workflow.cores` |
| log/benchmark | `_parts/3.08_run_sweep.{log,tsv}` (orchestrator); per-member parts under `_parts/3.08_run_sweep/rlz_<n>_cst_<m>.log` |
| script | `blueearth_cst/experiment/run_sweep.py` |

**Undeclared, runner-owned, deliberately invisible to the DAG:**
`_state/ledger.jsonl`, `_state/sweep_completeness.csv`, `_state/sweep.lock`,
`_state/quarantine/`, `_state/members/<member_id>/`,
`{runs_dir}/rlz_<n>/config/cst_<m>.toml` (HM-4, persistent),
`{runs_dir}/rlz_<n>/output/cst_<m>.csv` (HM-5, persistent), and the transients
(§6.6). §3.2 states why; §7.5 states what replaces the lost visibility.

Full runner specification: §6.

### 4.4 Stage 4 — Reduce

**3.09 `export_wflow_results`**

| | |
|---|---|
| input | `ledger_final = {exp_dir}/_state/ledger_final.csv`, `st_csv_fns` (unchanged); `_state/sweep_completeness.csv` read at runtime, existence transitive (§5) |
| output | `Qstats`, `basin` (unchanged) **+ `response_long = {indicators_dir}/response_long.csv`** |
| params | `indicators_dir`, `aggr_rlz`, `st_num`, `Tlow`, `Tpeak` (unchanged) |

The `expand()` over per-member CSVs
(`Snakefile_climate_experiment:552`) is replaced by the ledger: `ledger_final.csv`
lists exactly the members of the current manifest, each with its CSV path,
coordinates and content digest.

**HM-7 is byte-stable by construction.** `analyze_wflow_results` keeps its body:
the `Q_`-prefix gauge selection (`export_wflow_results.py:96`), the `basavg`
substring selection (`:97`), the `aggr_rlz` concatenation order, the per-statistic
rounding, and the `tavg`/`prcp` derivation
(`tavg = df_st["temp_mean"].iloc[0]`, `prcp = df_st["precip_mean"].iloc[0]*100-100`,
`:196-198`) are unchanged. Only how the CSV list is *obtained* changes, and the
ledger emits it in the same order the `expand()` produced (realization-major,
cst-minor) so the aggregation index arithmetic (`:162`) is untouched.

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
| `precip_variance` | float \| empty | the WG-2 variance factor (empty for `cst_0`); see OQ-1 (§9.1) |
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

**The long table is a lossless pivot, and that is its acceptance test**
(§12, C-11): re-pivoting `response_long.csv` must reproduce `Qstats.csv` and
`basin.csv` cell-for-cell. It is a *view*, never an independent computation — a
second computation path would be a second source of truth for the response
surface.

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
`run_historical: true` ⇒ `K=14` members): v1 runs 49 jobs at `B=4` (58 at `B=1`,
P3-3 headline); v2 runs **13 jobs** — `1+1+1+1` prepare, `2+2` generate,
`1+1` sweep, `1+1+1` reduce. The member count leaves the DAG entirely.

**Config keys added** (all optional, `get_config` contract — raise on missing
required, return the default for optional):

| key | default | meaning |
|---|---|---|
| `workflows.climate_experiment.sweep_workers` | `snakemake.threads` (= `-c N`) | `p`, the number of persistent Julia workers |
| `workflows.climate_experiment.wflow_threads` | `4` | `M`, `--threads` per worker (today's frozen value) |
| `workflows.climate_experiment.member_max_attempts` | `2` | attempts per member **within one invocation** (§5.4) |
| `workflows.climate_experiment.allow_partial` | `false` | OQ-4 posture (§9.4) |
| `workflows.climate_experiment.retain_member_artifacts` | `false` | keep per-member transients on disk (replaces `--notemp`, §10) |

**Config keys retired:** `batch_size`, `batch_size_max`
(`Snakefile_climate_experiment:501-519`). A config still carrying them is
**rejected with a named migration message**, not silently ignored — silence
would let a user believe they were still tuning the sweep.

## 5. Members manifest and per-member ledger

Two records, joined by `member_id`, mirroring `cst-run-control`'s immutable-intent
/ mutable-state split (§5.5):

| Record | Path | Mutability | Declared to Snakemake? |
|---|---|---|---|
| Members manifest | `{exp_dir}/_state/members.json` | Written once per manifest rule execution; immutable for the life of a sweep | **Yes** (output of 3.01, input of 3.05–3.08) |
| Ledger | `{exp_dir}/_state/ledger.jsonl` | Append-only during a sweep | **No** — must survive a failed job (§3.2) |
| Finalized ledger | `{exp_dir}/_state/ledger_final.csv` | Written once, atomically, at **accepted** sweep termination | **Yes** — the sole declared output; input of 3.09 |
| Completeness record | `{exp_dir}/_state/sweep_completeness.csv` | Written atomically on **every** terminal path, accepted or not | **No** — see the note below |

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
    "config_digest": "sha256:1f0c…",          // canonical digest of the wf3-relevant config subset
    "guarded_sections_digest": "sha256:9ab3…", // = today's rule-3.00b params digest
    "wf1_snapshot_digest": "sha256:44de…",
    "wf2_snapshot_digest": "ABSENT",           // file_digest_or_absent semantics
    "store_dir": "…/climate_historical/era5_19800101_20101231",
    "grid": { "rlz_num": 2, "st_num": 6, "st_start": 0 },
    "master_seed": 24610,
    "policy": {
      "member_max_attempts": 2,
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
- **`tavg` / `prcp` / `precip_variance` are the *annual scalars*** the response
  surface is indexed by, derived exactly as the reduction derives them today
  (`export_wflow_results.py:196-198`): month-1 values, `prcp` as
  `precip_mean * 100 − 100`. The **monthly** structure stays in WG-2's
  `cst_<m>.csv`, which the manifest points at and which stays a declared input of
  the reduce rule. The manifest does not duplicate the 12-row record; it indexes it.
- **`member_hash`** = `sha256` over the canonical JSON of
  `{member_id, rlz, cst, baseline, st_csv_digest, tavg, prcp, precip_variance,
    run_config_digest}`, where `run_config_digest` covers the result-affecting
  run parameters (`horizontime_climate`, `run_length`, `clim_source`,
  `data_sources`, the base `wflow_sbm.toml` digest, the staticmaps digest) and
  `st_csv_digest` is the content digest of the member's WG-2 file. This is the
  **member-level freshness boundary**: editing `run_length` changes every
  `member_hash`; editing one `cst_<m>.csv` changes only that column of members.

  **Two of those digests need a rerun-trigger, or they are stale by
  construction.** `wflow_sbm.toml` and `staticmaps.nc` are wf1 products; rule
  3.01 declares neither as an input and would not notice a rebuilt
  `hydrology_model/` under an unchanged wf1 config, leaving every `member_hash`
  stale and letting members skip against a model they were never run on. The
  repo already solves exactly this: `Snakefile_climate_experiment:174-175`
  threads `file_digest_or_absent(...)` through `params:` so a **content-only**
  change re-triggers past `ancient()`. Rule 3.01 therefore carries
  `wflow_toml_digest` and `staticmaps_digest` as params on the same pattern.
  *(The alternative — dropping both from `member_hash` — is rejected: a model
  rebuild genuinely invalidates every member.)*
- **`tools`** is *recorded, not enforced*. A Wflow or weathergenr version change
  does **not** invalidate members in v2.0. Rationale and the falsifier that would
  overturn it: §9.2 and §12 C-13. This is the single most consequential
  simplification against `cst-run-control`'s `environment_digest` condition.

### 5.2 Ledger schema — `ledger.jsonl`

One JSON object per line, UTF-8, LF, append-only, never rewritten in place.

| field | type | on which events | semantics |
|---|---|---|---|
| `ts` | str | all | RFC 3339 UTC, second resolution |
| `invocation_id` | str | all | uuid4, minted once per `run_sweep` execution |
| `member_id` | str | all | `rlz_<n>/cst_<m>` |
| `member_hash` | str | all | copied from the manifest; ties the row to a config generation |
| `event` | str | all | `claimed` \| `succeeded` \| `failed` \| `quarantined` |
| `attempt` | int | all | 1-based, scoped to `(member_id, member_hash, invocation_id)` |
| `worker_id` | int \| null | `claimed`, terminal | the slot that owns the member |
| `seconds` | object | terminal | `{"perturb": 3.9, "downscale": 11.2, "simulate": 34.8, "verify": 0.2}` |
| `outputs` | object | `succeeded` | `{"result": "sha256:…", "toml": "sha256:…"}` |
| `stage` | str \| null | `failed` | `perturb` \| `downscale` \| `simulate` \| `verify` — where it broke |
| `class` | str \| null | `failed` | `member` (deterministic, do not retry) \| `worker` (infrastructural, retryable) |
| `detail` | str \| null | `failed`, `quarantined` | one-line reason, newlines stripped |

Example (a member that lost its worker and succeeded on the retry):

```jsonl
{"ts":"2026-08-01T13:22:41Z","invocation_id":"7c1f…","member_id":"rlz_1/cst_3","member_hash":"sha256:7e02…","event":"claimed","attempt":1,"worker_id":2}
{"ts":"2026-08-01T13:23:19Z","invocation_id":"7c1f…","member_id":"rlz_1/cst_3","member_hash":"sha256:7e02…","event":"failed","attempt":1,"worker_id":2,"stage":"simulate","class":"worker","detail":"worker 2 exited with code 3221225477 before answering request 14"}
{"ts":"2026-08-01T13:23:21Z","invocation_id":"7c1f…","member_id":"rlz_1/cst_3","member_hash":"sha256:7e02…","event":"claimed","attempt":2,"worker_id":2}
{"ts":"2026-08-01T13:24:33Z","invocation_id":"7c1f…","member_id":"rlz_1/cst_3","member_hash":"sha256:7e02…","event":"succeeded","attempt":2,"worker_id":2,"seconds":{"perturb":3.9,"downscale":11.2,"simulate":34.8,"verify":0.2},"outputs":{"result":"sha256:0f1a…","toml":"sha256:bb90…"}}
```

**`ledger_final.csv`** — the reduce's declared input. Columns:
`member_id, rlz, cst, tavg, prcp, precip_variance, result, result_sha256,
seconds_total, attempts, invocation_id`. One row per member of the current
manifest that reached `succeeded`, ordered realization-major / cst-minor (the
`expand()` order §4.4 relies on). It is a **projection of manifest ⋈ ledger**,
carrying no fact not derivable from those two — so a lost `ledger_final.csv` is
always rebuildable.

**`sweep_completeness.csv`** — `member_id, state, attempts, stage, class, detail`
for **every** member of the manifest, including the succeeded ones, plus a
trailing comment-free summary the reduce reads: it is the machine-readable
completeness record OQ-4's `allow_partial` branch requires, and under the
fail-loud default it trivially reports all-succeeded.

### 5.3 Atomicity, single writer, crash consistency

**Single writer by construction, not by convention.** Only the orchestrator
*parent* process writes `_state/`. Slot processes never touch the ledger; they
report outcomes over a `multiprocessing.Queue` and the parent serializes them
(§6.1). Multi-writer interleaving is therefore not a hazard this design has to
mitigate — which is why no file locking, no compare-and-set and no fencing token
appears on the ledger write path.

**Whole-file artifacts** (`members.json`, `ledger_final.csv`,
`sweep_completeness.csv`): write to `<name>.tmp` in the *same directory*,
`flush()`, `os.fsync()`, close, then `os.replace()`. `os.replace` is atomic and
overwrites on both Windows and POSIX (`os.rename` does not overwrite on Windows —
that is the trap this rule exists to avoid). A crash leaves either the previous
complete file or none; never a half file.

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
| Any line parses but violates the row schema, or its `member_id` is not in the manifest and not a known orphan | **Corruption** | Hard error; refuse to proceed |
| A `succeeded` row whose recorded `result_sha256` no longer matches the file on disk | **Divergence** | Member reverts to pending; quarantine the file (§7.4) |

The hard-error path names the offending line number and prints the recovery
command: `snakemake … --config sweep_quarantine=1`, which moves `_state/` to
`_state/quarantine/<invocation_id>/` and starts a fresh ledger. Quarantine is
retention, never deletion (`cst-run-control` references/resume.md).

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
  `failed`, `quarantined`. Derived by folding the ledger, not stored.
- **The fold rule:** for each `member_id`, consider only rows whose `member_hash`
  equals the current manifest's; take the last row. `claimed` with no terminal
  successor ⇒ **interrupted** ⇒ treat as pending, and quarantine any partial
  output before re-claiming.
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
| `output_namespace` + atomic namespace claim | **ADOPTED, reduced** | `_state/sweep.lock` via `O_CREAT\|O_EXCL` (§6.6), experiment-scoped. No ancestor/descendant overlap algebra — experiments do not nest |
| Fencing token, token-checked publication | **ADAPTED** | `invocation_id` on every row makes a superseded writer's rows *identifiable*; it does not *prevent* their write. Accepted residual risk under A1 + the lock. **Named in §15 as residual risk R-3** |
| Content-addressed staging → seal → inventory CAS | **SKIPPED** | Would require intercepting Wflow's own output writes. Substituted by digest-on-record + digest-on-resume (§5.3), which catches the same corruption without owning the write path |
| State set `planned/ready/running/succeeded/failed/cancelled` | **ADOPTED at member granularity**, reduced (§5.4) | The run-level lifecycle is Snakemake's; the member-level one is ours |
| Every transition a single CAS against `state_revision` | **SKIPPED** | Single writer (A1) makes CAS vacuous. Substituted by append-only + fold |
| Append-only attempts, closed attempts never rewritten | **ADOPTED** | §5.2 |
| Checkpoint reusability — six conditions | **ADOPTED as four**: `member_hash` match, terminal event `succeeded`, artifacts present, digests verify | Skipped: `environment_digest` (see `tools`, §9.2 — a deliberate, falsifiable simplification); `stage_interface_version`; the `validation` record (next row) |
| `validation_authority` on each binding; a passing validation record required for `succeeded` | **SKIPPED** | The repo's validation authority is its validator suite (WG-1..6 / HM-1..7) and `check_baseline.py`, run as tests, not recorded per member. ADR 0022 itself records that validation records have "no normative collection" — adopting the field without the collection buys nothing |
| Quarantine before resume | **ADOPTED** | §7.4 |
| `resume_policy` + `max_attempts` | **ADOPTED as** `member_max_attempts` | §5.4 |
| Conformance levels + validity profiles | **SKIPPED** | Declaring a level implies validating against its profile; there is no second adopter to be conformant *with* |

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
    │  owns: lock, manifest, ledger, work set, scheduling, finalization
    │  mp.Queue(work)  ──▶                 ◀── mp.Queue(results)
    ├── slot 0  (python subprocess, spawn)                 imports hydromt ONCE
    │   └── julia worker 0  (persistent, --threads M)      loads Wflow ONCE
    ├── slot 1  (python subprocess)
    │   └── julia worker 1
    └── slot p−1 …
```

**Three levels, each amortizing a different fixed cost.**

- The **orchestrator** never imports hydromt and never blocks on a member. It is
  the single ledger writer (§5.3) and the only process that touches `_state/`.
- A **slot** is a persistent Python subprocess (`multiprocessing`, `spawn` start
  method — Windows has no other, and using it everywhere keeps the two platforms
  on one code path). It imports `hydromt_wflow` once and reuses that import for
  every member it handles. P3-3 measured 342–359 s of non-3.10 work over 43 rows,
  a large share of it 12 separate hydromt imports; amortizing them is a real
  second win beside the Julia one (§12, C-4 makes it falsifiable).
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

### 6.2 Orchestrator ↔ Julia worker line protocol

**Newline-delimited JSON over the worker's stdin/stdout, strict
request/response, one request in flight per worker.** stderr is not part of the
protocol; it is teed to the member's log. Probe PR-5 (§11.2) exercised exactly
this shape.

| Direction | Message | Fields |
|---|---|---|
| worker → orch (once, on start) | `ready` | `type`, `protocol` (int, `1`), `worker_id`, `pid`, `julia`, `wflow` (version string) |
| orch → worker | `run` | `type`, `request_id` (monotone int), `member_id`, `toml` (absolute path) |
| worker → orch | `result` | `type`, `request_id`, `member_id`, `status` (`ok` \| `error`), `seconds` (float), `error` (string, newlines stripped; present iff `status="error"`) |
| orch → worker | `shutdown` | `type` |
| worker → orch | `bye` | `type` |

Rules:

1. **Every message is one line, `flush`ed immediately.** Julia's stdout is
   block-buffered when redirected; the probe confirms an explicit `flush(stdout)`
   after each `println` is sufficient.
2. **The worker never writes a non-JSON line to stdout.** Wflow's own logging
   goes to stderr or its own log file; any stray stdout write would corrupt the
   stream. The worker redirects `Wflow.run`'s stdout into stderr for the duration
   of a member (`redirect_stdout(stderr) do … end`) so upstream print statements
   cannot break the protocol. **This is the protocol's sharpest edge and it is
   an implementation falsifier** (§12, C-6).
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
| **Spawn** | The slot spawns its worker **lazily** — on its first member, never at sweep start. A no-op resume must not pay `p × F ≈ 3 × 24 s` to discover it has nothing to do (§7.3, C-2) |
| **Handshake** | Wait for `ready` with a bounded timeout (default 300 s, config-free constant sized for a cold `using Wflow` on a loaded box). Timeout ⇒ kill, one respawn, then fail the sweep with a named message |
| **Health** | Liveness is the response itself. No heartbeat: a strict request/response protocol makes a hung worker indistinguishable from a slow member, and Wflow members legitimately run for minutes. A per-member wall-clock ceiling is **not** imposed in v2.0 — sized wrongly it kills good work (§15, R-4) |
| **Crash** | Worker exit before answering ⇒ the slot records `failed`/`class=worker` with the exit code, respawns once, and re-claims if `attempt < member_max_attempts`. Two consecutive spawn failures on one slot retire that slot; the sweep continues on the remaining workers with a warning, and fails only if all slots retire |
| **Drain** | When the work queue empties, the slot sends `shutdown`, waits for `bye` with a short timeout, then closes stdin and `wait()`s |
| **Shutdown on orchestrator failure** | The orchestrator's `finally` terminates every slot; each slot's `finally` closes its worker's stdin (rule 4 above) and, after a grace period, kills it. A `SIGKILL` of the orchestrator leaves workers to exit on stdin EOF |
| **Orphan sweep** | On start, if `_state/sweep.lock` exists but its recorded pid is not alive, the lock is **reported as stale and not auto-cleared** — clearing another process's claim on a liveness guess is exactly what `cst-run-control` refuses to infer from a timeout. The message names the recovery command |

### 6.4 Scheduling, `-c N` mapping, resource claims

**`-c N` mapping.** `run_sweep` declares `threads: workflow.cores`, so
`snakemake -c 3` gives the sweep job `threads == 3` and no sibling job runs
beside it — correct for a stage that owns the box. Then:

- `p = sweep_workers` config key, defaulting to `snakemake.threads`.
- `M = wflow_threads` config key, defaulting to `4` (today's frozen value).
- Total Julia thread demand is `p × M`, which **oversubscribes on purpose** and
  reproduces today's budget exactly: v1 runs 3 concurrent batch jobs each
  `--threads 4` (`Snakefile_climate_experiment:546`) on a 12-logical box.

**The performance-floor protocol depends on holding `p × M` fixed.** P3-3's
frozen triple is `-c 3, --threads 4`; a floor comparison run at any other product
is not a comparison. §13 step 8 states the protocol.

**Scheduling: greedy, longest-first, work-stealing by construction.** Members are
pushed onto one queue ordered so that (a) `cst_0` baselines come first — they are
inputs to nothing, but they are the members most likely to expose a systematic
failure early — and (b) the rest in realization-major order. Slots pull. There is
no static partition, so no LPT assignment is needed and no straggler is stranded
behind a partition boundary: this is precisely what batching could not do
(P3-3 estimator, `dev/scripts/estimate_batch_makespan.py`, whose whole subject is
the makespan cost of a *static* partition).

**Resource claims** are one line: an exclusive claim on
`{exp_dir}` for the sweep's duration, realized as `_state/sweep.lock` (§6.6). No
`shared_read`/`shared_write` algebra — the only shared mutable resource in reach
is the experiment tree itself, and it is claimed exclusively. The historical
store is a read-only input, which `cst-run-control` explicitly classifies as an
input rather than a shared resource.

### 6.5 Logging and benchmark capture

**Per member, not per batch** (G4). The runner writes:

| Artifact | Path | Content |
|---|---|---|
| Member log | `{exp_dir}/logs/_parts/3.08_run_sweep/rlz_<n>_cst_<m>.log` | the member's four sub-steps: the `Rscript` perturbation stdout/stderr, the downscale output, the worker's stderr for that member, the verification result |
| Orchestrator log | `{exp_dir}/logs/_parts/3.08_run_sweep.log` | the rule's `log:`; plan banner, per-member start/finish lines, worker lifecycle events, the finalization summary |
| Member benchmark | `{exp_dir}/benchmarks/_parts/3.08_run_sweep/rlz_<n>_cst_<m>.tsv` | Snakemake benchmark **format** (`s`, `h:m:s`, `max_rss`, … ), with `s`/`h:m:s` filled from the member's wall clock and the resource columns `NA` |
| Rule benchmark | `{exp_dir}/benchmarks/_parts/3.08_run_sweep.tsv` | Snakemake's own row for the whole sweep job |

`merge_logs` discovers a label's parts by listing that label's part directory
(`Snakefile_climate_experiment:190-196`) — the same mechanism that today absorbs
3.05/3.07/3.09's per-`(rlz, cst)` fan-out — so per-member parts merge with **no
change to `merge_logs`**, only a new label in `LOG_RULES`. Likewise
`merge_benchmarks` scans `_parts/3.*`, so per-member TSVs are picked up unchanged.

**Honesty note on the benchmark columns.** The `NA` resource columns are not a
regression: on Windows they are `NA` today unless `patch_psutil_windows_benchmark`
is active (`Snakefile_climate_experiment:14`), and that patch instruments
Snakemake's own job wrapper, which the runner's sub-steps do not go through. The
**authoritative** per-member timing is the ledger's `seconds` object, which is
finer than any benchmark row (four sub-steps, not one total) and is what §13 step 8's
floor check reads.

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

Step 3's deletion is what caps the co-resident set: the WG-4 NC and the WG-6
forcing never both persist past the downscale. So

> **Peak transient disk = `p × max(WG-4 NC, WG-6 forcing + HM-6b state)`** — a
> constant in `p`, independent of `RLZ_NUM × ST_NUM`.

At fixture scale that is `3 × ~10 MB ≈ 30 MB`, against P3-3's measured
`120.59 MB` peak at `B=4` (P4). The `dev/followups.md` § Post-P3-3 disk-aware
`batch_size` problem is **dissolved**: there is no `B`, and the ceiling no longer
scales with sweep size, so no per-run size estimate is needed at parse time.

`retain_member_artifacts: true` suppresses step 5's deletions. This is the
**replacement for `--notemp`** (§10): a Snakemake flag cannot suppress a delete
the runner performs, and three seam validators currently document `--notemp` as
their capture procedure.

**The experiment lock.** Before anything else the runner creates
`_state/sweep.lock` with `os.open(..., O_CREAT|O_EXCL|O_WRONLY)` and writes
`{invocation_id, pid, host, started_at, config_path}`. `O_EXCL` create is the
atomic primitive on both platforms. Held for the sweep, removed in `finally`.
Rationale: Snakemake's own workdir lock is scoped to the **repository checkout**,
and this repo's standing policy is `worktree_policy: always` with several
concurrent sessions — two worktrees pointed at one `project_dir` slip past
Snakemake's lock entirely and would interleave writes into the same experiment
tree. This is `cst-run-control`'s namespace claim at the depth the risk justifies.

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
sentinel rather than two artifacts. **Design note against the anchor:** the intake
reads as though 3.00b's mechanism is *replaced* by layer 3. Replacing it outright
would leave stages 1–2 (generation, an expensive stage) unguarded, and success
criterion 6 requires the 3.00b failure modes to still fail loud — so this design
reads "simplifies to" as *one artifact and one rule instead of two*, and adds
layer 3 on top. **Flagged for G1 as an interpretation, not a scope change.**

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

### 7.3 What the runner decides — the resume fold

On entry, before spawning any worker:

```
1. claim _state/sweep.lock                            (fail loud if held)
2. verify the three drift digests                     (§7.1 layer 3)
3. read members.json                                  (the immutable intent)
4. fold ledger.jsonl under the crash-consistency rules (§5.3)
5. per member, classify:
     no rows for this member_hash                     -> RUN
     last = succeeded, artifacts present, digests OK   -> SKIP
     last = succeeded, artifact missing or digest bad  -> QUARANTINE, RUN
     last = claimed (interrupted)                      -> QUARANTINE, RUN
     last = failed                                     -> RUN   (new invocation)
     member_hash differs from every ledger row         -> QUARANTINE, RUN
   members on disk not in the manifest                 -> ORPHAN: ignore + report
6. if the RUN set is empty: finalize and exit 0        (no worker is ever spawned)
7. else: spawn slots lazily and execute
```

Step 6 is load-bearing. The manifest is a declared `input:` of the sweep, so any
config edit rewrites it and fires the mtime trigger even when no member field
changed — Snakemake will re-enter the sweep rule for reasons that are not
member-relevant. That is accepted rather than engineered around (content-stable
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
  bakes the orphans in and the gate compares them instead of the live set.

### 7.5 `--dry-run` honesty, and what replaces the lost visibility

**Stated plainly: `--dry-run` cannot report pending members, and this design does
not pretend otherwise.** It reports at rule granularity — "run_sweep will run"
or "Nothing to be done" — because member state lives in a file Snakemake does not
track. That is a real loss against v1, where `--dry-run` listed every pending
`(rlz, cst)` job.

Three things replace it:

1. **`dev/scripts/sweep_status.py <exp_dir>`** — reads manifest + ledger and
   prints the member table (`done / pending / failed / quarantined / orphan`),
   with `--json` for machine use. This is strictly *more* informative than v1's
   dry-run, because it distinguishes failed from pending; it is *less* available,
   because it needs a manifest on disk.
2. **The sweep's plan banner**, printed before the first member and captured in
   the log: `K members: 11 done, 2 pending, 1 failed (rlz_1/cst_4: simulate)`.
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
| `stress_test.*.step_num` | `ST_NUM` changes ⇒ the `cst_<m>` → coordinate mapping changes ⇒ `st_csv_digest` changes for most members ⇒ mostly-full sweep. *(This is honest, not a defect: index-based member ids are not stable under a grid resize — §9.3 prices it)* |
| One `cst_<m>.csv` edited | Only that column of members invalidates |
| `master_seed` | Every realization's seed changes ⇒ regeneration ⇒ every member invalidates |
| `aggregate_rlz`, `Tlow`, `Tpeak` | **Reduce only.** No member invalidates; only 3.09 re-runs |
| `sweep_workers`, `wflow_threads`, `member_max_attempts`, `retain_member_artifacts` | Recorded in the manifest but **excluded from `member_hash`** — they are execution policy, not science. A worker-count change must not invalidate a sweep |

That last row is a deliberate asymmetry with `run.policy` being *inside*
`members.json`: the manifest records policy for provenance, and `member_hash`
covers only result-affecting fields.

## 8. Failure modes, recovery, and the failure-injection gate set

### 8.1 Failure modes and recovery

| # | Failure | Blast radius | Recovery |
|---|---|---|---|
| F1 | One member's Wflow run errors (`class=member`) | **1 member.** No sibling artifact is deleted — nothing sibling is a declared output (§3.2) | Fail-loud: the sweep does not write `ledger_final.csv`; the reduce is blocked. The failed member is named in the **surviving undeclared** `_state/sweep_completeness.csv` and in `ledger.jsonl`. Under `allow_partial`: the sweep finalizes with the hole recorded (§9.4) |
| F2 | The perturbation or downscale step errors | 1 member, `stage=perturb\|downscale` | as F1 |
| F3 | A Julia worker crashes mid-member | 1 member + 1 worker | member recorded `class=worker`; worker respawned; member re-claimed while `attempt < member_max_attempts` |
| F4 | A slot process dies | its in-flight member | parent observes the queue/sentinel closure, records `class=worker`, respawns the slot (worker included) |
| F5 | Orchestrator hard-killed | the in-flight `p` members | `ledger.jsonl` survives with every completed member (PR-6); re-invoke after `--unlock`; interrupted members quarantine and re-run |
| F6 | Torn final ledger line | none | dropped silently on read (§5.3) |
| F7 | Corrupted (non-final) ledger line | the sweep refuses to start | named line number + the quarantine command |
| F8 | A member CSV on disk diverges from its recorded digest | 1 member | quarantine + re-run |
| F9 | Drift injected between manifest and sweep | the whole sweep | hard failure naming the changed comparand (§7.1 layer 3) |
| F10 | Two sweeps on one experiment | none, if the lock holds | second invocation fails immediately naming the holder's pid/host/started_at |
| F11 | Stale lock (holder gone) | the sweep refuses to start | reported as stale, **not auto-cleared**; recovery command named (§6.3) |
| F12 | All workers retire (e.g. Julia missing) | the whole sweep | hard failure; no partial `ledger_final.csv` |

**Escalate to the user, do not auto-repair:** F7, F11, and any case where the
manifest's recorded digests and the live files disagree in a way no legal member
transition resolves.

### 8.2 The failure-injection gate set

Executable post-implementation; each names its command and the observation that
passes it. Fixture: `config/workflows/snake_config_model_test.yml` against
`test_case/test_local`. `SM` abbreviates
`pixi run snakemake -c 3 -s Snakefile_climate_experiment --configfile config/workflows/snake_config_model_test.yml`.

| Gate | Injection | Command | Expected observation |
|---|---|---|---|
| **GF-1** kill a worker mid-member | while the sweep runs, `Stop-Process -Id <julia pid> -Force` for one worker | `SM` (background) + PowerShell kill | ledger shows `failed`/`class=worker` then `claimed` attempt 2 then `succeeded` for that member; every other member unaffected; sweep exits 0; `semantic_tree_diff --tolerance 0` clean vs the reference tree |
| **GF-2** hard-kill the sweep | `Stop-Process -Id <snakemake pid> -Force` after ≥ 2 members complete | `SM`; then `SM --unlock`; then `SM` | second invocation runs **only** the members without a `succeeded` row; `sweep_status.py` before the re-run shows exactly that set; the two completed members' CSV mtimes are unchanged |
| **GF-3** corrupt a ledger row | append `{"member_id": "rlz_1/cst_2", "event":` (no newline) **and then** a valid row after it, making the broken line non-final | edit `_state/ledger.jsonl`, `SM` | sweep refuses to start; message names the line number and prints the `sweep_quarantine=1` command; **no member runs** |
| **GF-4** truncated tail | append `{"member_id": "rlz_1/cst_2"` with no trailing newline as the **final** line | edit, `SM` | line dropped silently; one log line records the truncation; the sweep proceeds normally |
| **GF-5** config change mid-sweep | edit `run_length` while the sweep runs, then let it finish and re-invoke | `SM`; edit; `SM` | first sweep completes against the manifest it read; second invocation rewrites the manifest (params trigger), every `member_hash` changes, every prior member is quarantined and re-run; `_state/quarantine/<id>/` holds the previous CSVs |
| **GF-6** member failure, fail-loud | temporary guard in `wflow_worker.jl` raising for one `member_id` when `CST_GF6_FAIL` matches (the P3-3 GN-4 method: data-level injection is unreachable because forcing and TOML are both runner-written) | `SM` | sweep exits nonzero; `ledger_final.csv` **absent**; `_state/sweep_completeness.csv` **present** and naming the failed member with `stage=simulate` — the discriminating observation for the undeclared-completeness decision (§5); `Qstats.csv` mtime unchanged; the 13 sibling CSVs **present and untouched** (contrast GN-4, where `B−1 = 3` siblings were deleted) |
| **GF-7** member failure, `allow_partial` | same guard, `--config allow_partial=true` | sweep exits 0; `sweep_completeness.csv` records 13 `succeeded` + 1 `failed`; `Qstats.csv` has 13 rows per statistic; `indicators/completeness.csv` present; reduce prints a named warning |
| **GF-8** concurrent sweep | start `SM` from a second worktree against the same `project_dir` | two shells | second fails within seconds with the lock holder's pid/host/started_at; the first is unaffected; ledger has no rows from the second `invocation_id` |
| **GF-9** orphan member | complete a sweep at `RLZ_NUM=2`, set `realizations_num: 1`, re-invoke | `SM` | rlz_2 CSVs untouched on disk; `sweep_completeness.csv` has `state=orphan` rows for them; `Qstats.csv` covers rlz_1 only; nothing is deleted |
| **GF-10** drift after manifest | run through 3.01, then edit the wf1 snapshot, then run the sweep | `SM --until build_members_manifest`; edit; `SM` | either the params trigger re-runs 3.01 and the guard fails loud, or the sweep's layer-3 check fails naming `wf1_snapshot_digest`; in no case does a member run |
| **GF-11** no-op resume cost | complete a sweep, re-invoke with an unrelated config comment change | `Measure-Command { SM }` | sweep rule re-enters and exits **without spawning any Julia process** (`julia` never appears in the process table); wall < 15 s (§12 C-2) |

GF-1..GF-5 and GF-8 are the intake's named injection classes; GF-6/GF-7 pair the
two OQ-4 branches so the owner ruling is testable either way; GF-9..GF-11 close
gaps this design introduced.

---

## 9. Open questions settled

### 9.1 OQ-1 — `precip_variance` semantics · **[OWNER RULING — provisional]**

**Evidence, now measured on the build that actually runs** (probe PR-1, §11.2):

- The installed package is `tanerumit/weathergenr` **v1.2.0**, `RemoteSha`
  `9f3d3189b692d9c6e94cf6f712ca5d1dd1b71cfa`, packaged 2026-07-17.
- `formals(apply_climate_perturbations)`: `scale_var_with_mean = TRUE`,
  `verbose = FALSE`.
- Body, read from the installed lazy-load database:
  `if (isTRUE(scale_var_with_mean)) { if (!is.null(precip_var_factor) &&
  isTRUE(verbose)) warning("Ignoring 'precip_var_factor' …"); var_mat_in <- mean_mat_in^2 }`.
- Our call site (`blueearth_cst/weathergen/impose_climate_change.R:45-57`) passes
  `precip_var_factor = cst_data$precip_variance` and passes neither
  `scale_var_with_mean` nor `verbose`.

**Conclusion: E1 is confirmed on the installed build.** The WG-2
`precip_variance` column never reaches the output, and the warning that would
have said so is suppressed because `verbose` defaults `FALSE`. P6 moves from
*hypothesis* to **measured**.

**Citation correction that must not propagate.** The intake's P6 row cites
`~/workspace/weathergenr/R/climate_perturbations.R`. That checkout is
`Deltares-research/weathergenr` at `master`, version **1.1.0.9000**, and it does
**not contain** the installed sha (`git merge-base --is-ancestor` → not a valid
commit). The two trees happen to agree on this function — verified line by line
(`R/climate_perturbations.R:107,360-366`) — but the reasoning was grounded in a
tree that is not what runs. Any future E1 claim must cite the installed lazy-load
database or `formals()`, not that checkout.

**There is now no factual uncertainty left — only the science call.** Two
branches, both fully specified so the ruling picks one without reopening the
schema:

| | **(a) Activate the axis** | **(b) Retire the axis** |
|---|---|---|
| Code change | pass `scale_var_with_mean = FALSE` (and `verbose = TRUE`) at the call site | drop `precip_var_factor` from the call |
| Science | variance perturbation becomes an independent axis; `precip_variance` min/max in config become live | variance-scales-with-mean is declared the intended science |
| WG-2 | header unchanged | header loses `precip_variance` → **`validate_wg2` changes**; `prepare_cst_parameters.py` drops a column |
| Manifest | `precip_variance` stays in the member tuple **and in `member_hash`** | field leaves the member tuple, `member_hash`, `ledger_final.csv`, and `response_long.csv` |
| Value impact | **every perturbed member changes value** → a full re-baseline | none — the current outputs already reflect variance = mean² |
| Config | `stress_test.precip.variance.{min,max}` stay meaningful | keys become dead and must be rejected, not ignored |

**Provisional recommendation: (a), activate the axis, and pass `verbose = TRUE`
regardless of the branch.** Reasoning: the config axis exists, `t260720a` was
fixed so the grid genuinely spans `variance.min..max` (P9), and a stress-test
tool that silently ignores a declared perturbation axis is the worse failure. But
this is a scientific call about what the CST perturbation domain *is*, and it
costs a full re-baseline, so it is the owner's.

**Design posture pending the ruling:** the manifest carries `precip_variance`
with the field present and marked provisional. Branch (b) removes a field; branch
(a) removes nothing. Designing for (a) therefore makes (b) a deletion rather than
a schema redesign.

**Adjacent finding, recorded and deliberately not acted on.** `seed` is a formal
of `apply_climate_perturbations` and our call site omits it (PR-1). Combined with
P8's measured bit-identical re-runs this *characterizes* the determinism the
design assumes (A3). Starting to pass a seed would be value-changing scope creep
outside the fixed anchor and is **not proposed**.

**Porting 3.07 to Python is rejected** (the OQ-1(b) half of the scoping intake):
a tolerance-0 parity gate against Gamma-QM with `mme` fit, transient ramps and a
PET recompute is high effort and high risk against a stage worth ~6 % of sweep
wall. The R step is invoked per member from the slot (§6.6 step 2), and the parity
question dissolves because the same R code runs on the same inputs.

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

### 9.4 OQ-4 — reduce with holes · **[OWNER RULING — provisional]**

**Provisional recommendation: fail loud by default, with an explicit
`allow_partial` escape hatch.** A silently sparse response surface distorts
exactly the robustness judgment CST exists to inform.

| | **fail-loud (default)** | **`allow_partial: true`** |
|---|---|---|
| Sweep terminal condition | every manifest member `succeeded` | ≥ 1 member `succeeded` |
| `ledger_final.csv` (declared) | written only on full completion | written, listing succeeded members only |
| `sweep_completeness.csv` (undeclared, survives failure) | written on every terminal path — all-`succeeded` on success, **the holes named** on failure | written; the holes named per member with `stage` and `class` |
| Reduce | blocked (its declared input is absent) | proceeds; emits `indicators/completeness.csv` beside the surfaces and prints a named warning |
| `Qstats.csv` | full grid | grid with holes; the missing `(tavg, prcp)` rows simply absent |
| Gate | GF-6 | GF-7 |

**Both branches keep `--dry-run` honest**, which is why the two declared outputs
are constant across branches (§4.3): `ledger_final.csv` exists **iff** the sweep
reached an *accepted* terminal state, and whether that state had holes is a fact
in `sweep_completeness.csv` — never something a reviewer has to infer from a
sentinel's existence.

Owner call needed on: the default, and whether `allow_partial` should additionally
require a minimum completeness fraction. **Recommendation: no fraction** — a
threshold invents a scientific criterion the repo has no basis for.

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
| Generate | **Value-changing, characterized statistically** | same generator, new seeds ⇒ distributional equivalence (per-variable annual mean/sd/quantile envelopes across realizations, before vs after), **never** byte identity |
| Perturb | **Identical** | same R code, same inputs ⇒ tolerance 0 on `rlz_<n>_cst_<m>.nc` when fed a **pre-change** baseline NC |
| Downscale | **Identical** | same script body, same inputs ⇒ tolerance 0 on the WG-6 forcing and the HM-4 TOML |
| Simulate | **Identical, already measured** (P3, GN-2) | warm-session ≡ cold-process byte identity; re-verified at pool depth (C-7) |
| Reduce | **Identical** | same reduction on the **same** member CSVs ⇒ `Qstats.csv`/`basin.csv` byte-identical to the step-0 capture |

The perturb/downscale/reduce legs are held identical by **feeding them
pre-change artifacts**, which is why §13 step 0's captures are a hard
prerequisite: without them these three legs cannot be proven, only asserted.

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
| **WG-2** `cst_<m>.csv` | **verbatim** *(conditional on OQ-1)* | path, header, 12-row domain, semantics all unchanged. New readers: the manifest builder (scalars) and the runner. Still a declared `input:` of the reduce | `validate_wg2` unchanged — **unless OQ-1 branch (b)**, which drops the `precip_variance` column and changes the pinned header |
| **WG-3** weathergenr config surface | **home** | `config/weathergen_config.yml` → per-realization `_work/weathergen_config_rlz_<n>.yml` with three added keys (`rlz.index`, `seed`, `work.path`) and `realizations_num: 1`. The per-member `weathergen_config_rlz_<n>_cst_<m>.yml` leaves disk for `_state/members/<id>/weagen.yml`, **transient** | **`validate_wg3` changes**: add the per-realization form and its three keys; the per-member fixture path moves and becomes capture-dependent. Continuously-verified status is retained for the per-rlz form |
| **WG-4** `rlz_<n>_cst_0.nc` (baseline) | **home** | lifecycle `temp()` → **persistent** | `validate_wg4` logic unchanged; the baseline case **upgrades** from skip-until-captured to continuously verified — a net gain |
| **WG-4** `rlz_<n>_cst_<m>.nc`, m ≥ 1 | **transient** | same path, same content; deleted by the runner after downscale instead of by Snakemake | logic unchanged; **capture procedure changes**: `--notemp` no longer works (§10a) |
| **WG-5** climate data catalog | **verbatim** | path, per-entry schema, and the entry-key grid (incl. `cst_0`) all unchanged; only the producer's `input:` set changes | `validate_wg5` and `validate_wg5_catalog_grid` unchanged, both still continuously verified |
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
| **HM-7+** `response_long.csv` | **new** | tidy long view of the two wide tables (§4.4) | **`validate_hm7` gains a case**; a new relational check that the long table re-pivots to the wide ones (C-11) |
| `validate_hm_gauge_column_identity` | **verbatim inputs** | all three inputs still persist | unchanged; **extended** to cover the long table's `column` values |

### 10a. The `--notemp` replacement (a gate that would otherwise silently break)

Three validators — `validate_wg4` (perturbed), `validate_wg6`, `validate_hm6b` —
document `--notemp` as their on-disk capture procedure, and three integration
tests carry runtime `pytest.skip("temp() artifact absent; capture via --notemp")`
guards keyed to it. **`--notemp` is a Snakemake flag; it cannot suppress a delete
the runner performs.** Without a replacement these three gates degrade from
"skip-until-captured" to "uncapturable", silently.

Replacement: the `retain_member_artifacts` config key (§4.5). Capture command:

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
   of §13 step 4 and by GF-2/GF-3 instead.
2. **`check_baseline.py`** — the wf3 manifest slice gains
   `indicators/response_long.csv` and gains **nothing from `_state/`**. Stated as
   an explicit negative because it is the kind of omission that reads as an
   oversight: `ledger_final.csv` carries `seconds_total` and `invocation_id` and
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
| P2 | `B=4` sweep 400.2 s vs `B=1` 619.9 s (−35.4 %), adverse ordering | The **performance floor** the pool must not fall below (§13 step 8) |
| P3 | Warm-session ≡ cold-process byte identity, 102 files, tolerance 0 | Assumption A4; re-verified at pool depth by C-7 |
| P4 | Peak `temp()` disk = `p × B × (forcing + state)`; 120.59 MB measured at the cap | Superseded by design: v2's ceiling is `p × 1`, independent of sweep size (§6.6) |
| P5 | `temp()` cascade: one intermediate target ⇒ 19 jobs / 247.7 s | Dissolved by persistent baselines (§4.2) and by §10a's cheap capture |
| P6 | `precip_var_factor` inert at our call site | **Upgraded to measured on the installed build** by PR-1; the intake's source citation is corrected (§9.1) |
| P7 | Realizations generated jointly from one seed | Grounds OQ-5's re-baseline (§9.5) |
| P8 | 3.07 perturbation deterministic in practice | Assumption A3; strengthened by PR-1's observation that `seed` is a formal and is omitted |
| P9 | `t260720a` fixed; the grid spans `variance.min..max` | Strengthens OQ-1 branch (a) (§9.1) |

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

### 11.3 Hypotheses this design carries (not probed; each has a falsifier)

| # | Hypothesis | Falsifier | Owner |
|---|---|---|---|
| H1 | `Wflow.run` does not write to stdout, or `redirect_stdout(stderr)` fully contains it | C-6 | implementation |
| H2 | Warm-session identity holds at pool depth (K members in one session, not B) | C-7 | implementation |
| H3 | The hydromt import amortizes usefully across members in one slot | C-4 | implementation |
| H4 | `multiprocessing` spawn + persistent Julia children is stable on Windows for a full sweep | C-5 | implementation |

---

## 12. Claim → falsifier table

Every runtime property this design claims, the observation that would falsify it,
and the command producing that observation. `SM` as in §8.2.

| # | Claim | Falsifier | Command |
|---|---|---|---|
| **C-1** | A failed member deletes no sibling artifact | any sibling CSV missing or mtime-changed after GF-6 | `SM` with the GF-6 guard; `Get-ChildItem hydrology_runs/*/output/cst_*.csv` before/after |
| **C-2** | A no-op resume costs one Python start and spawns no Julia | `julia` appears in the process table, or wall > 15 s | GF-11 (`Measure-Command { SM }` + process sampling) |
| **C-3** | Peak transient disk = `p × 1` member, independent of sweep size | peak exceeds `p × max(WG-4, WG-6+state)` at any sample, or grows with `K` | P3-3's GN-3 2 s sampler, run at `K=14` and again at a reduced `K` |
| **C-4** | Persistent Python slots amortize the hydromt import | mean per-member `seconds.downscale` after the first member is not materially below the first member's | ledger `seconds.downscale` distribution, first vs subsequent per slot |
| **C-5** | The pool completes a full fixture sweep without a slot or worker crash | any `class=worker` row in a clean run | ledger grep on a clean `SM` |
| **C-6** | The line protocol is not corrupted by Wflow's own output | any non-JSON line on a worker's stdout | worker stdout capture during a real member |
| **C-7** | Pool-depth warm sessions preserve byte identity (extends P3/GN-2) | any diff at tolerance 0 vs the per-process reference tree | `dev/scripts/semantic_tree_diff.py --ref <reference> --cur test_case/test_local --no-path-map --tolerance 0` — **valid only after `_state` joins `EXCLUDED_DIR_NAMES`** (§10b) |
| **C-8** | Resume runs only unfinished members | any member with a `succeeded` row re-executes (CSV mtime changes) | GF-2 |
| **C-9** | A corrupt ledger row quarantines rather than passes | the sweep proceeds and any member runs | GF-3 |
| **C-10** | `Qstats.csv` / `basin.csv` are byte-identical when fed the same member CSVs | any byte differs vs the step-0 capture | `dev/scripts/check_baseline.py check --workflow climate_experiment` + direct diff |
| **C-11** | `response_long.csv` is a lossless pivot of the two wide tables | re-pivot ≠ wide, in any cell | a pytest re-pivot test in `tests/test_export_wflow_results.py` |
| **C-12** | The performance floor holds: pool ≤ 400.2 s at fixture scale, `p × M = 12` | measured wall > 400.2 s under §13 step 8's protocol | `Measure-Command { SM --forceall }` |
| **C-13** | `tools` drift is detectable after the fact | a completed sweep whose `run.tools` differs from the live environment goes unreported | manifest vs `julia --version` / `packageVersion` at reduce time |
| **C-14** | Two sweeps cannot interleave on one experiment | both proceed and both append ledger rows | GF-8 |
| **C-15** | Guard failure modes are unchanged | any gate-2 a–h case changes verdict or message | `pytest tests/test_check_project_consistency.py` |
| **C-16** | The generation change is distributionally equivalent, not merely different | any per-variable annual mean/sd envelope falls outside the pre-change envelope | the §9.6 characterization script, before vs after |

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
   the 14 per-member CSVs, retained for the perturb / downscale / reduce identity
   legs (§9.6).
5. **Baseline check green** before touching anything:
   `check_baseline.py check --workflow climate_experiment` → OK.

### Step 1 — Manifest builder + guard fusion

*Falsifier first:* a test asserting `members.json` is byte-identical across two
invocations with unchanged config, and the existing guard gate-2 a–h cases
unchanged (C-15).
*Then:* `build_members_manifest.py`, rule 3.01, sentinel rewiring, `.guard_ok`
retirement. The sweep is untouched; the workflow still runs the v1 way.

### Step 2 — Per-realization generation

*Falsifier first:* the distributional characterization script (C-16), run against
the step-0 baselines to establish the *before* envelope while the old code still
exists.
*Then:* `prepare_weagen_config_rlz`, the three `generate_weather.R` changes, the
`{rlz_num}` wildcard. **Value-changing** — this is the documented re-baseline.

### Step 3 — Persistent baselines, WG-4 lifecycle

*Falsifier first:* a job-count assertion — re-materializing one perturbed member
must not re-run generation (v1: 19 jobs, P5).
*Then:* drop `temp()` from the baseline output. Verify the perturb identity leg
against the step-0 operands (tolerance 0).

### Step 4 — The sweep runner and worker pool (the milestone's core)

*Falsifier first:* unit tests for the ledger fold, the crash-consistency rules
(§5.3, all four rows), the state machine (§5.4), the lock, and the line protocol
against a **stub** worker. These run without Julia and without Wflow.
*Then:* `run_sweep.py`, `wflow_worker.jl`, `sweep_status.py`.
*Then:* a 2-member fixture sweep, followed by GF-1..GF-5, GF-8, GF-11.

**`sweep_status.py` lands in this step, not later** — it is the replacement for
the `--dry-run` visibility the step removes (§7.5).

### Step 5 — Retire the old rules; ledger-driven reduce; the long table

*Falsifier first:* the reduce identity leg — run the **new** reduce over the
**step-0** member CSVs and require `Qstats.csv`/`basin.csv` byte-identical
(C-10); plus the re-pivot test (C-11).
*Then:* delete 3.05/3.07/3.09/3.10-family, rewire 3.07 catalog inputs, rewrite
3.11 → 3.09, add `response_long.csv`, reject the retired `batch_size*` keys.

### Step 6 — Contracts, validators, tooling, docs

**Blocking sub-step, before the step-7 gates can mean anything (§10b):** add
`_state` to `EXCLUDED_DIR_NAMES` in `dev/scripts/semantic_tree_diff.py:145`, and
confirm the wf3 `check_baseline.py` slice takes `response_long.csv` and takes
**nothing** from `_state/`.

Then: `validate_wg3` extended; the two seam docs' `--notemp` sections replaced by
§10a's procedure; `validate_hm7` + gauge-column relational extended for the long
table; `dev/workflows/climate_experiment.md` rewritten; `dev/conventions/naming.md`
gains the member-id vocabulary; `AGENTS.md` Repo Map / Key Commands / `temp()`
convention line updated; `dev/followups.md` § Post-P3-3's two items closed as
superseded; `docs/migration-r09-wf3.md` written (R8 precedent).

### Step 7 — Full gate sweep

`pytest tests/`; `pytest tests/test_cli.py` (three Snakefile dry-runs);
`pytest tests/test_interchange_contracts.py -rs`; a `retain_member_artifacts=true`
capture to un-skip the three temp validators; whole-tree `semantic_tree_diff`
(C-7); GF-1..GF-11.

### Step 8 — Performance floor check

**Protocol, stated because the comparison is invalid without it:**

- Same box, AC online, `LoadPercentage` verified low, no sibling agent session —
  the P3-3 § Measurement conditions contract.
- **`p × M` held at `3 × 4 = 12`**, matching P3-3's frozen `-c 3, --threads 4`.
  Run `SM --forceall` with `sweep_workers=3`, `wflow_threads=4`.
- Compare against **400.2 s** (P2), and report the 3.08-stage makespan separately
  from the full sweep wall, as P3-3 does, since the upstream stages changed shape.
- Report the ledger's per-member `seconds.simulate` distribution as the direct
  measurement of `S_warm` at pool depth — the term the whole design rests on.
- **At-scale advantage is stated as a model** from measured `F`/`S_cold`/`S_warm`,
  never claimed as measured, unless a production-sized sweep is actually run
  (success criterion 8).

### Step 9 — One manifest re-record, then seal

`check_baseline.py record --workflow climate_experiment`, scoped to wf3's slice,
after the delta has been characterized (not before). Expected: `Qstats.csv` and
`basin.csv` change (generation is value-changing, §9.6), `response_long.csv` is
added, and **nothing from `_state/` enters the manifest** (§10b — the manifest
pins products, `_state/` holds provenance). Then the roadmap R9 section and the
status lines.

**Gates between steps:** step 0 is blocking. Steps 1–3 may land continuously.
**Step 4 is a stop-and-review point** — it is where incrementality leaves
Snakemake. Step 8 is a stop point if the floor is not met.

---

## 14. Alternatives considered

### 14.1 Keep P3-3 batching; tune it

Status quo: parse-time batch rules, LPT partition, `batch_size_max` clamp.
**Rejected** because three of the five §1.1 pains are structural to it: the
warm-session discount is bounded by `B` (P1), the blast radius is `B` by
construction (P3-3 GN-4), and the disk ceiling needs a parse-time estimate that
cannot exist (`dev/followups.md` § Post-P3-3). **Would become preferable if** the
pool's measured makespan lost to batching at fixture scale (C-12) — the floor
check is precisely the decision point that would reinstate it.

### 14.2 Snakemake checkpoints / dynamic rules for the sweep

Use a `checkpoint` to re-evaluate the DAG after the manifest exists, keeping one
job per member. **Rejected:** it solves *enumeration* (which members exist),
which is not a problem here — `RLZ_NUM × ST_NUM` is known at parse time — and
solves none of the three structural pains. It keeps one Julia process per member,
so `S_cold` is paid `K` times: strictly worse than the batching it would replace.
**Would become preferable if** the dominant cost were ever `F` rather than the
warm-up (it is not — P1 measured `F ≈ 24 s` against a 57 s warm-up discount).

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

---

## 15. Limitations, residual risk, and open items for G1

### 15.1 Residual risk

| # | Risk | Severity | Mitigation / posture |
|---|---|---|---|
| R-1 | Incrementality is now our code. A ledger bug can silently skip a member that should re-run | **High** | The state machine, the fold, and the crash rules are unit-testable without Julia (§13 step 4); GF-2/GF-3/GF-5 are the behavioural gates; `sweep_status.py` makes the fold's verdict inspectable |
| R-2 | `--dry-run` no longer shows pending members | Medium | Stated openly (§7.5); `sweep_status.py` is a required deliverable |
| R-3 | No true fencing. `invocation_id` identifies a superseded writer's rows but does not prevent them | Low under A1 | The `O_EXCL` lock is the real barrier; a writer that bypasses the lock is out of contract. `cst-run-control` records the same class of limitation |
| R-4 | No per-member wall-clock ceiling, so a genuinely hung Wflow run hangs the slot | Medium | Deliberate: a wrongly-sized timeout kills good work, and members legitimately run for minutes. Revisit with data from a production-sized sweep |
| R-5 | Dropping `environment_digest` lets a sweep mix engine versions | Medium | `run.tools` makes it detectable; C-13 is the falsifier that would promote `tools` into `member_hash` |
| R-6 | Undeclared writes (ledger, member CSVs) invert the repo's R07 B6 correction | Low | Justified structurally (§3.2) and compensated by §7.5; must be stated in `AGENTS.md`'s conventions so it does not read as an oversight |
| R-7 | The generation re-baseline breaks comparability with every existing experiment tree | **High, accepted** | Documented in `docs/migration-r09-wf3.md`; one manifest re-record; baseline-provenance stamping (R7-21) guards fixture sharing |
| R-8 | Windows `spawn` + persistent Julia children is unproven at sweep length | Medium | H4/C-5; §14.8 is the pre-designed fallback |
| R-9 | Protocol corruption by Wflow stdout | Medium | H1/C-6; `redirect_stdout(stderr)` is the designed containment, unverified with Wflow loaded |

### 15.2 Open items for gate G1

1. **OQ-1 `[OWNER RULING]`** — activate or retire the `precip_variance` axis
   (§9.1). Both branches specified; branch (a) costs a full re-baseline, branch
   (b) changes WG-2's pinned header. **No factual uncertainty remains.**
2. **OQ-4 `[OWNER RULING]`** — the reduce-with-holes posture and whether
   `allow_partial` should carry a completeness threshold (§9.4). Recommendation:
   fail-loud default, `allow_partial` escape, **no** threshold.
3. **The drift-guard reading** (§7.1). This design keeps 3.00b's comparator and
   its fail-loud behaviour, folded into the manifest rule, and *adds* the sweep's
   start-time verification — rather than replacing the guard with the latter.
   Flagged as an interpretation of the anchor, not a scope change.
4. **`response_long.csv` in the baseline manifest** — recommended yes (a 4th wf3
   target); confirm at the re-record (§13 step 9).
5. **Milestone id R9** — proposed in the scoping intake, to be confirmed.

### 15.3 Known limitations of the design as drafted

- Member ids are not stable under a stress-grid resize (§9.3).
- The design assumes single-machine execution throughout; no part of it is
  wrong under multi-machine execution, but several parts (the lock, the
  single-writer ledger, the `p × M` budget) would need replacement rather than
  extension.
- The at-scale performance advantage is a **model**, not a measurement, until a
  production-sized sweep runs (§13 step 8).
- H1–H4 (§11.3) are carried into implementation as falsifiers rather than
  settled here; three of them need Wflow loaded, which drafting could not do.

---

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
