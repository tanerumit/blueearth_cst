# R12 successor baseline — execution record

Date: 2026-09-15. Session `session-3`, branch `feat/wp3-improvements`.
Supersedes nothing; it discharges the first requirement of
[standing-seal-status.md](standing-seal-status.md).

## Why a separate root

`test_case/test_local` is **untracked and therefore shared by every branch**, so
regenerating it in place would change the baseline gate for every worktree before
the evidence had been judged. The successor run writes to
`test_case/test_successor` instead, through a tracked config set
(`test_case/project_config_successor*.yml`) that differs from the baseline set in
exactly two things — `project.project_dir` and the four `config_path` names —
verified by diff. Owner approved this shape on 2026-09-15.

## Why the standing fixture could not be repaired in place

`snapshot_project_tree.py` reported 280 paths, 205 recognized, **75 unmapped**.
The tool asks that each unmapped path be judged an orphan to prune or an
inventory gap to report. It is neither. Classified:

| Group | Count |
|---|---|
| `experiments/experiment/hydrology/wflow/…` | 42 |
| `experiments/experiment/climate/weathergenr/…` | 20 |
| Other `experiments/experiment/…` (results at experiment root, `snake_config_run_stress_test.yml`, run records) | 10 |
| `config/runs/snake_config_*.yml` | 2 |
| `logs/wf3_run_stress_test_experiment.log` | 1 |

All 75 are **pre-R12 output**: the old experiment name, the old layout, metrics
at the experiment root rather than in metric sets. The fixture is not partly
stale, it is wholly predecessor, so no pruning and no map amendment could repair
it. Only a fresh successor run can, which is what
[standing-seal-status.md](standing-seal-status.md) concluded and what this
record executes.

## What was NOT done, and why

**No value-by-value comparison between `test_local` and `test_successor`.** The
standing fixture records `horizontime_climate: 2078` — the seventeen-year window
retired on 2026-09-07 — while the successor config uses
`simulation_window: 2046–2054` and the `mid` horizon. A direct comparison would
conflate the R12 layout and ownership change with that scientific-config change,
and AGENTS.md rules it out explicitly: *"The standing tree is not an R12
migration reference … Use the separately captured fresh P0 reference and GF-9
crosswalk for R12 acceptance."*

The matched-settings old-to-new comparison **already exists and is signed**:
P3's [`gf9-direct-comparison.json`](p3/gf9-direct-comparison.json) crosswalks 686
old rows to 756 new with zero unmatched on either side, against immutable P0
under frozen scientific settings. That is the comparison the seal rests on.
Manufacturing a second one across two simultaneous changes would look like more
evidence and be worth less.

## Execution

Order per AGENTS.md: wf0 → wf3 → wf1 → wf4 → wf2. WF1 takes `--notemp` because
rule 1.14 declares wflow's `run_default/output.csv` as `temp()` and that file is
the manifest's discharge target; WF2 takes `--keep-going`.

| Stage | Exit | Minutes | Files before → after |
|---|---|---|---|
| wf0 `analyze_climate` | 0 | 1.4 | 188 → 188 (re-run no-op after the interrupted attempt) |
| wf3 `generate_scenarios` | 0 | 0.5 | 188 → 188 (no-op) |
| wf1 `build_model` | 0 | 2.5 | 188 → 194 |
| wf4 `simulate_system` | 0 | 9.2 | 194 → 296 |
| wf2 `analyze_projections` | 0 | 6.0 | 296 → 327 |

The first attempt reached 188 files (wf0 1.3 min 1→53, wf3 1.5 min 53→117, wf1
partial) before being killed; the relaunch resumed from there, which is why wf0
and wf3 show as no-ops and wf1 completes in 2.5 minutes.

**wf1 verified rather than assumed**: rule 1.14 `run_wflow` ran for 1:45 and
`models/hydrology/wflow/run_default/output.csv` survives at 1,209,535 bytes, so
`--notemp` preserved the manifest's discharge target.

**wf4 produced what the gate was missing**: exactly one retained metric plan
`ae7a346d…` and one metric set `d52a85b0…`, `status: ready`, 756 expected keys,
70 return-level evidence blocks — **all 70 carrying `shape_coverage`**, so the
owner's B+A ruling is present in the baseline itself and not only in the GF15
working copy.

### Two false signals, recorded because both nearly passed

**A no-op that reported success.** The first runner named its stage parameter
`$Args`, which collides with PowerShell's automatic argument array. It arrived
empty, so every stage ran a bare `pixi run --as-is`, which prints the task list
and **exits 0**. Five stages reported success in zero minutes having done
nothing. Only the implausible timings exposed it, and they were logged for
progress reporting rather than as a check. The script now fails a stage whose log
shows `Available tasks:` or contains no Snakemake progress marker at all, and
records file counts before and after each stage.

**A silent death that looked like work in progress.** The second attempt was
launched with `Start-Process` but no separate console, so the child stayed in the
session's process group and a console interrupt killed it three minutes into
wf1 — leaving no failure marker, a stale workdir lock and 69 incomplete markers.
Absence of a result read as work still running. The runner now launches into its
own hidden console, sweeps the lock for all five entry points before starting,
and passes `--rerun-incomplete` to wf1; the monitor watches the process itself
rather than only waiting for markers.

Both are the same failure class — *a missing signal read as a good one* — and
both are why this record states file deltas and durations rather than exit codes
alone.

## Gates

| Gate | Standing fixture | Successor tree |
|---|---|---|
| `snapshot_project_tree.py` | exit 1 — 280 paths, **75 unmapped** | exit 1 — 327 paths, 325 identity, **2 unmapped** |
| `resolve_metric_set_dir` | REFUSED: "requires exactly one retained metric plan, found 0" | resolves `…/metric_sets/d52a85b0…` |
| `check_baseline.py record` | — | **not run** — see below |

### The two remaining unmapped paths are inventory gaps, not orphans

The tool's own instruction is that an inventory gap means "stop and report it:
amending the map is an owner decision". Neither was amended.

**1. `experiments/{exp}/results/metric_sets/{digest}/return_level_benchmark.json`
— this one is mine.** `semantic_tree_diff.py:505` declares the metric-set leaves
as `metrics.json`, `metric_environment.json`, `unit_index.csv` and
`*_indicators.csv`. GF15 D5 added a fifth file to **every** metric set the
toolbox produces — the shipped benchmark report, copied in so a reader never
needs the installed asset — and no GF15 stage updated this inventory. None of
them ran a full-tree snapshot, so nothing could have caught it. The proposed
amendment is one `same_rx` line beside the existing four leaves.

**2. `data/climate/historical/climate_levels.json` — pre-existing, not GF15.**
`analyze_climate.smk:484` writes rule 0.04b's pooled scale at the historical
root, deliberately, because it pools across sources. The inventory rule at
`semantic_tree_diff.py:409` is `data/climate/historical/[^/]+/.*`, which requires
a path segment after `historical/` and so cannot match a file sitting directly
there — confirmed by matching both spellings against the pattern. The standing
fixture hides this: it carries the *retired* per-source sidecar at
`…/era5_…/plots/climate_levels.json`, which the map does cover and which
`climate_figures.py:819` records as removed on 2026-08-16.

## What this record does not establish

- **That the standing fixture has been replaced.** It has not. `test_case/test_local`
  is untouched and `dev/baseline/manifest.json` still describes it.
- **Numerical acceptance of the successor tree.** Producing a clean tree is not
  the same as accepting its values; the signed GF-9 crosswalk carries that claim
  under matched settings.
- **The milestone seal.** Separate, and no part of this infers it.
- **Anything about Linux.** Out of scope by owner ruling of 2026-09-15.
