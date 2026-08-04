# Run intake — wf3-experiment-v2 (design-review-loop, full variant)

**Scope authority:** `dev/workflows/wf3-climate-experiment-v2-intake.md`
(committed `edc0689`, authored via `design-scoping` 2026-08-01 from the
owner-approved direction). That document's § Approved architecture is a fixed
anchor; its § Open questions OQ-1..OQ-7 are what this run's design must settle
(owner rulings marked there: OQ-1 precip_variance semantics, OQ-4
reduce-with-holes posture).

## Change request (normalized)

Ground-up redesign of `Snakefile_climate_experiment` (wf3): keep Snakemake as
the outer skeleton over 4 scientific stages (extract / generate / sweep /
reduce); move the inner `RLZ_NUM × ST_NUM` sweep out of the file-per-wildcard
DAG into a members-manifest + per-member ledger driven by a persistent Julia
worker pool (load Wflow once, pull members off a queue, build forcing on
demand per member, delete after use). Per-realization generation with explicit
seeds; baseline NCs not `temp()`. Reduce from the ledger; keep
`Qstats.csv`/`basin.csv`, add a tidy long format. Drift guard simplifies to
manifest-recorded wf1/wf2 snapshot digests verified by the sweep runner.
Direction ≈ the `cst-run-control` skill's contract, at a depth this design
must choose.

## Problem

See scoping intake § Why a ground-up redesign — five grounded pains: warm-up
(not startup) dominates and only a persistent pool captures it sweep-wide; the
parse-time batch construct's structural debt (batch-granular logs, C5 blast
radius B); the disk-aware batch-size problem unsolvable at parse time; 3.06's
all-realizations single job and its `temp()` cascade; baseline NCs as `temp()`
making every partial re-run pay full regeneration.

## Constraints

Scoping intake § Constraints, unchanged: CST automation scope (no upstream
re-engineering; E1 is a call-site decision), new dependencies owner-gated,
netCDF interchange, seam contracts as acceptance frame with an enumerated
delta table, web-app independence, worktree discipline, naming conventions
(member-id vocabulary is a new naming surface).

## Decision criteria (for G1 and the reviews)

1. Every OQ-1..OQ-7 resolved with evidence, or explicitly deferred to an owner
   ruling with the options priced; no silent defaults.
2. The sweep's resume/crash/fencing semantics are specified concretely enough
   to implement and to falsify (state machine + failure-injection gate set),
   since incrementality moves from Snakemake into our code.
3. Dependency footprint: prefer zero new packages; any ask surfaced explicitly.
4. Proportionality: ledger depth justified against a single-machine sweep
   (cst-run-control subset, not ceremony).
5. Migration honesty: per-stage parity/characterization plan with falsifiers
   written before code (R8 discipline); one manifest re-record.
6. Performance floor: not worse than P3-3 batching at fixture scale; at-scale
   advantage stated as a model from measured terms.

## Success criteria / non-goals

Scoping intake § Success criteria (9 items) and § Cut (YAGNI) / non-goals,
verbatim by reference.

## Evidence register

| # | Premise | Source | Exact observation | Precision | Reproduction | Confidence |
|---|---|---|---|---|---|---|
| P1 | Per-member fixed cost is small; warm-up dominates | `dev/p33/batching-results.md` | F≈24 s, S_cold≈92 s, S_warm≈35 s (fixture, i5-1335U) | n=1 per term, derived from per-cst `@elapsed` lines | rerun the two timed sweeps per that doc's § Reproduction | measured, single-sample |
| P2 | Batching B=4 sweep = 400.2 s vs B=1 619.9 s (−35.4 %) | same | frozen `-c 3, --threads 4`, `--forceall`; batched run second (adverse ordering) | n=1 | same | measured, single-sample |
| P3 | Warm-session ≡ cold-process output identity | same, GN-2 | 102 files byte-identical, tolerance 0 | exact | `semantic_tree_diff.py --tolerance 0` per-process vs batched trees | measured |
| P4 | Peak temp disk under batching = p×B×(forcing+state) | same, GN-3 | 120.59 MB peak vs 120.6 MB cap (saturated by construction on fixture) | 2 s sampling | GN-3 sampler | measured |
| P5 | `temp()` cascade: one intermediate target re-runs the generation chain | WG seam doc § capture procedure | 19 jobs / 247.7 s for three `rlz_1_cst_1` targets | n=1 | the `--notemp` targeted command in that doc | measured |
| P6 | `precip_var_factor` is ignored at the current call site (variance = mean²) | **INSTALLED build** `tanerumit/weathergenr` v1.2.0, RemoteSha 9f3d3189…, packaged 2026-07-17 (lazy-load DB read, stage-1 probe PR-1) + `blueearth_cst/weathergen/impose_climate_change.R` | installed `scale_var_with_mean` defaults TRUE → `var_mat_in <- mean_mat_in^2`, warning only under `verbose`; our call passes neither `scale_var_with_mean` nor `verbose` | code reading of the installed build | design-v1.md § 11.2 PR-1 | **MEASURED 2026-08-01** (settled at stage 1). Provenance correction: the checkout at `~/workspace/weathergenr` is a *different origin* (Deltares-research, v1.1.0.9000) that agrees on this function but is NOT what runs; the intake originally cited it |
| P7 | Realizations are generated jointly from one seed (per-rlz jobs cannot reproduce them) | `blueearth_cst/weathergen/generate_weather.R` | single `generate_weather(..., n_realizations=RLZ_NUM, seed=cfg)` call; realizations share one RNG stream | code reading | read the file | high (code-grounded) |
| P8 | 3.07 perturbation is deterministic in practice | R5 record (`dev/roadmap.md` § R5, commit 9) | seeded control-vs-control `rlz_1_cst_0.nc` and `rlz_1_cst_1.nc` bit-identical | exact | rerun the R5 characterization | measured (2026-07-20 env) |
| P9 | t260720a (variance max-reads-min) is fixed | `tests/test_prepare_cst_parameters.py::test_precip_variance_grid_uses_max_endpoint` | grid max endpoint = variance.max (1.5 in test) | exact | `pytest tests/test_prepare_cst_parameters.py` | verified in suite |

## Framework-feasibility probe candidates (stage 0/1)

Cheap probes the author may run during drafting (no wflow runs, no full R
generation); expensive ones become recorded hypotheses + falsifiers for the
task brief:

- **Sweep-rule freshness:** does the params rerun-trigger fire the sweep rule
  on a config-digest change, and does Snakemake leave the rule alone when its
  declared outputs exist and inputs are unchanged (the resume path)? Dry-run
  probe on a scratch Snakefile is sufficient.
- **Ledger-internal work invisible to `--dry-run`:** what does an honest
  dry-run report for a sweep rule whose member state lives in the ledger?
  (Design must state the answer, probe optional.)
- **Persistent Julia worker line-protocol:** a `julia` process reading TOML
  paths from stdin and answering on stdout, without Wflow loaded — protocol
  viability only (startup + echo loop). Wflow-loaded behaviour stays a
  task-brief falsifier.
- **Per-rlz `generate_weather` invocation:** verify from weathergenr code that
  `n_realizations = 1` + per-call seed + `file_suffix` naming supports one-job-
  per-realization output naming (code reading, no run).

## Gate materialization

| Gate | Status | Note |
|---|---|---|
| `pytest tests/` + `pytest tests/test_cli.py` (3 Snakefile dry-runs) | Runnable | CI covers the bare-checkout layer only |
| `check_baseline.py check --workflow climate_experiment` | Runnable, local-only | Thin: 3 wf3 targets (Qstats, basin, config snapshot); comparator is normalized-CSV sha |
| `semantic_tree_diff.py` whole-tree | **Needs pre-change reference snapshot** of the fixture experiment tree — create before the first implementation commit | Also needed per-stage: `--notemp` capture of generator NCs + per-member CSVs for parity legs |
| Interchange validators (`tests/test_interchange_contracts.py`) | Runnable; temp-artifact cases need a `--notemp` capture | Contract deltas will change some validators — the delta table decides which |
| Per-stage parity legs (perturb tolerance-0; generation characterization; reduce identity) | **Need pre-change artifacts** (seeded NCs, member CSVs) captured before implementation | R8 falsifier-before-code discipline |
| Failure-injection gates (kill worker mid-member; corrupt ledger row; config change mid-sweep) | Defined by this design; executable post-implementation | Design must name each gate's command + expected observation |
| Installed-weathergenr E1 check | **Runnable today** (DESCRIPTION RemoteSha or `formals()` query) | Settles P6 before G1 if run during drafting |

## Derived-artifact register (author spawns barred from touching these)

| Artifact | Regeneration after G2 |
|---|---|
| `dev/workflows/climate_experiment.md` (wf3 contract doc) | Rewrite from the accepted design at implementation |
| `dev/contracts/weather-generator-seam.md`, `dev/contracts/hydrological-model-seam.md` | Apply the design's contract-delta table; lands with the milestone |
| `dev/roadmap.md` | Add the R9 section after G2; status lines at seal |
| `dev/conventions/naming.md` | Register the member-id vocabulary |
| `AGENTS.md` (Repo Map / Key Commands / temp() convention line) | Update at implementation |
| `dev/baseline/manifest.json` | Re-record exactly once at implementation end |
| `dev/followups.md` § Post-P3-3 | Close/supersede the two items the design absorbs |
| Task brief (`dev/workflows/wf3-climate-experiment-v2-task-brief.md`) | Generate after G2 via `task-brief` with the claim→falsifier table |
| `docs/migration-r09-wf3.md` | Write at implementation (R8 precedent) |
| `dev/workflows/wf3-climate-experiment-v2-intake.md` (scoping intake) | Stays authoritative for scope; amend only by owner ruling at a gate |

## Genre mapping

`workflow-spec` (per `design-document`; R8 precedent
`dev/workflows/wf2-climate-analysis-v2-design.md`). Recorded here per the
status-manifest schema note.
