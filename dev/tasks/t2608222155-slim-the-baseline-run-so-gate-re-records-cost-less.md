---
title: Slim the baseline run so gate re-records cost less
type: todo-item
status: backlog
effort: 2
area: baseline / run cost
origin: owner request, R14 branch opening (2026-08-22)
queue:
created: 2026-08-22
updated: 2026-08-23
---

> [!note] Overview
> **What** — Cut the wall-clock of a full `test_local` baseline run, then re-record `dev/baseline/manifest.json` from the slimmer config.
> **Why** — Every milestone seal and every numeric-output change pays a full baseline run; R14 will force a re-record anyway because it rewrites the config YAMLs the manifest fingerprints, so the slimming is free to land in front of it.
> **Effort** — large, and **the framing changed once it was measured**: the config knobs cap out at roughly 8% of the run. The cost is process startup, and the two levers that matter are not in `test_case/`.

## Measured cost profile

From `test_case/test_local/benchmarks/`, regenerated **2026-08-22** by the R13
baseline pass — current, not historical.

| workflow | rule-time | dominant rule |
|---|---|---|
| wf1 | 245.4 s | `1.14_run_wflow` **112.3 s** (46%) |
| wf2 | 23.5 s | `2.06` 15.3 + `2.07` 8.2 — negligible |
| wf3 | 995.7 s | `3.15_run_wflow` **615.2 s** (62%), `3.14_downscale` 196 s, `3.12_perturb` 133 s, `3.11_weathergen` 29 s |

Roughly 21 min of summed rule time; the wf3 leg ran 10:16:15 to 10:25:45, about
9.5 min wall at `-c 3`. That wf3 number is an **undercount** of a cold run:
`3.04_delineate_spatial_units` and `3.13_write_climate_data_catalog` were
already up to date and did not appear.

wf2 looks cheap because the climate store is warm — but the whole
`test_local/data/climate` tree is **21 MB**, so cold is not much worse either.
wf2 is genuinely not where the time is.

## The temporal knobs are not the lever — measured, not fitted

Rule 3.15's log prints a per-member time inside each batch, so no model fitting
is needed. Both trees, both windows:

| tree | window | first member of a batch | every later member in that batch |
|---|---|---|---|
| `test_local` | 17 yr | 103.6 / 106.2 / 104.4 s | 19.1-32.4 s, mean **26.2** (n=11) |
| `test_rapid` | 9 yr | 88.2 / 88.1 / 90.9 s | 19.8-23.4 s, mean **21.5** (n=7) |

Sources: `test_case/test_local/logs/wf3_run_stress_test_experiment.log:497-530`
and `test_case/test_rapid/logs/wf3_run_stress_test_experiment_rapid.log:415-433`.

Two things fall out.

**Halving the simulated window buys 18%, not 50%.** Warm per-member cost goes
26.2 s to 21.5 s. Solving the two points as `a + b x years` gives **a about
16 s of per-run fixed cost and b about 0.59 s per simulated year** — so a
17-year member spends about 10 s simulating and about 16 s starting up. Rapid
also writes *three* `wflow_outvars` against baseline's two, which makes its
runs slightly dearer, so 18% is if anything an over-estimate of the window
effect.

**The first member of a batch costs about 80 s more than the rest.** That is
Julia JIT plus the cold SBM path, paid once per batch. At 3 batches that is
about 240 s of pure startup inside wf3, plus another about 80 s in wf1's
standalone `1.14_run_wflow` — roughly **320 s, a quarter of the whole run,
spent on starting Julia**.

Consequence for `run_length` 16 to 8: about 11 x 4.7 s + 3 x 16 s = **about
100 s of rule-time, about 35 s of wall** at `-c 3`, where the wf3 sweep's wall
is the longest batch (about 218 s), not the 615 s sum. Real, but small.

Consequence for batch count: fewer batches would cut the 240 s, but batches are
what `-c 3` runs in parallel — one batch would take 443 s of wall against
today's 218 s. **Three batches at `-c 3` is already the right choice**; do not
"optimise" it.

This also contradicts `dev/reference/validation-ladder.md`, which claims rapid
costs "~2.6x less wflow time and ~1.7x less weather generation". Measured, it
is about 1.2x on wflow, and rapid's `3.11_generate_weather_realizations` is
*slower* (45.8 s against 29.0 s). That line needs correcting whatever else this
item decides.

## Where the time actually is — and both levers are outside `test_case/`

The baseline run is roughly 40 short jobs, each paying a fresh-process startup:
Julia JIT for the wflow rules, and a Python interpreter plus the hydromt/xarray
import tree for nearly everything else. `3.14_downscale` at about 14 s x 14 jobs
and `3.12_perturb` at about 11 s x 12 jobs are almost entirely that.

1. **[[t2608202331]] — ESET real-time scanning makes every Python import about
   7x slower on this machine.** `import hydromt` pulls 3,173 modules at 4.79 ms
   each; `.pixi/envs/default` holds 94,661 files, all inside the scan surface.
   This is most of the gap between 59 minutes and CI's 9 for the full suite,
   and it taxes every Python rule in every workflow. Needs an admin/IT
   exclusion, not a repo change. **This is the largest available win and it is
   already boarded** — pursue it before any config edit.
2. **A Wflow sysimage.** `dev/milestones/p33/performance-baseline.md` already
   scoped this: driving the per-process fixed cost toward zero was estimated at
   -39%, the best-ranked lever in that table. It would remove most of the 320 s
   above. It is a tooling change (PackageCompiler), needs owner sign-off as a
   new build step, and is not boarded yet.

Config slimming is the *third* lever, worth roughly 8% of the run. Do it
because the re-record is happening anyway, not because it is the answer.

## What the config change is worth, and when it pays

Two keys, both adopting rapid's values:

- `run_length` 16 to 8 in `project_config_baseline_run_stress_test.yml`
- `horizontime_climate` 2078 to 2050, which shortens the generated series from
  78 yr to 46 (`compute_nr_years` anchors at 2010, so the HORIZON sets series
  length, not `run_length`)

Costed against the measured per-member numbers above, with no sysimage and no
ESET exclusion — config knobs only:

| variant | what changes | `3.15` rule-time | total rule-time | wall |
|---|---|---|---|---|
| today | 14 members x 17 yr | 615 s | ~1264 s (21 min) | ~15 min |
| **(a) keep coverage** | `run_length` 8, horizon 2050 | 504 s | ~1150 s | **~14.5 min** (-35 s) |
| **(b) full rapid** | (a) + grid 2 x 3 to 2 x 2 | 418 s | ~970 s | **~13.5 min** (-90 s) |

(a) is the recommended variant; (b) additionally drops the three-level precip
axis the coverage floor below keeps. Rule-time falls further than wall (-110 s
and -300 s) because at `-c 3` the three batches run concurrently, so the wall
is the LONGEST BATCH, not the sum. Quote whichever you mean; they are not
interchangeable.

**Every rule except `3.15` is flat, so there is nothing else to win here.**
Per job, against a 41% shorter generated series and a 47% shorter window:

| rule | baseline (78 yr series, 17 yr window) | rapid (46 yr, 9 yr) |
|---|---|---|
| `3.12_perturb` | 11.08 s/job | 10.82 s/job — 2% cheaper |
| `3.14_downscale` | 14.61 s/job | 20.23 s/job — 38% SLOWER |
| `3.11_weathergen` | 29.0 s | 45.8 s — 58% slower |

The last two going the wrong way is partly a confound (rapid writes three
`wflow_outvars` to baseline's two, and the runs are five days apart), but the
reading is the same either way: no measured window-length saving exists outside
`3.15`. These are Python and R jobs whose cost is interpreter start plus the
hydromt/xarray import tree — which is what [[t2608202331]] attacks.

**Reality check against the end-to-end number.** Rapid's whole wf3 measured
944.3 s against baseline's 995.7 s; correcting for the two rules baseline's run
skipped (`3.04` 17.3 s, `3.13` 13.6 s) that is about 913 against 996 — **83 s,
8%** — and that is variant **(b)**, the full cut. So the end-to-end evidence
sits at the BOTTOM of the bottom-up range, not the top. Plan on 4-8%.

**Payback.** A re-record costs one full run (about 15 min) plus reading the
diff. At 35-90 s saved per gate, the slimming repays its own re-record after
**10 to 25 gates**. That is the argument for never doing this standalone: fold
the two keys into the re-record R14 forces anyway and the saving is free; do it
on its own and a gate is spent to save a minute.

Non-time cost, for the same reason: moving the horizon to 2050 changes which
CMIP6 horizon the WF2 change factors are computed for, so those manifest
targets move too — attribution noise in the same re-record where R14's own
changes land, on top of [[t2608220920]]'s generator move.

## Coverage floor — what must not be cut, and why

The ladder's own rule: *cheap, not narrow; a config that gives up coverage must
say which.*

- **The ST grid stays 2 x 3 + `st_0`.** `precip.step_num: 2` (three levels) is
  the only thing in either config that exercises the rectilinearity spacing
  check in `blueearth_cst/shared/surface_axes.py` (`RECTILINEARITY_RTOL`); at
  two levels it is trivially satisfied. Rapid's 2 x 2 grid does **not** cover
  this. Nothing in-repo renders a contour, so cutting it is *available* — it is
  just narrow rather than cheap, and this is the tree whose numbers get quoted.
  It would also save only 4 warm members, about 105 s of rule-time.
- **`run_historical: true` stays.** `st_0` is what the two class-C month
  indicators derive from; `false` silently drops 2 of 11 `q` metrics.
- **`realizations_num: 2` stays.** One realization runs no across-realization
  reduction.
- **`shared.historical_window` stays at 17 yr.** The floor is 16
  (`constraints.min_historical_years`), the extra year is deliberate margin,
  and at 0.59 s per simulated year the whole knob is worth under 1 s.
- **wf2 stays at 3 models x 2 scenarios.** 23.5 s and a 21 MB store; two or
  more models is required for the ensemble reduction. Near-free coverage.
- **Basin geometry (`uparea`, `resolution`) is out of scope**, and the numbers
  above say it would not pay: startup, not cell count, is the cost. It is also
  entangled with `gauge_points`, `observations_timeseries.csv` and the
  manifest's `Q_101` discharge target.

## Coupled edits and traps

- **`horizontime_climate` plus/minus `run_length`/2 must stay inside
  `future_horizons.far`** in `project_config_baseline_analyze_projections.yml`.
  That alignment is *computed independently of the key* (the file says so), so
  a missed edit misaligns silently. At 2078/16 the current `far: [2070, 2090]`
  contains 2070-2086; at horizon 2050 it does not.
- **Run WF1 with `--notemp` for the re-record.** Rule 1.14 declares
  `run_default/output.csv` as `temp()` and that file is the manifest's wf1
  discharge target; without the flag the gate fails "target missing" and reads
  as a defect.
- **The per-member WF3 forcing NCs are `temp()` and are gone**
  (`experiments/experiment/hydrology/wflow/forcing/` is empty). Any probe that
  wants to re-run one member has to regenerate its forcing first. `wf1`'s
  `models/hydrology/wflow/forcing/inmaps_historical.nc` (8.5 MB, 17 yr) is NOT
  temp and survives, so a one-knob `endtime` probe against the wf1 TOML is the
  runnable form if a further measurement is ever wanted.
- **The four `project_config_baseline_linux*.yml` are NOT baseline twins.** They
  point at `test_case/gabon`, use `resolution: 0.0062475`,
  `horizontime_climate: 2050`, `run_length: 20`, `run_historical: false`, and
  their header records that Linux end-to-end validation is deferred and "this
  file must parse cleanly". They do not feed the manifest and need no lockstep
  edit — though their drift from the windows variant is worth a separate look.
- **The re-record must run from the PRIMARY checkout**, not a lane
  (`dev/reference/task-lanes.md`: one `project_dir` driven from two checkouts
  gets two disagreeing `.snakemake` stores and two locks).
- `t2608221010` means the new provenance may read `dirty: true` spuriously.
  Expect it; do not chase it here.

## Doc surface

`dev/reference/validation-ladder.md` (its config table hard-codes "14 x 17",
"78 years", "17 calendar years", and the falsified "~2.6x / ~1.7x" claim),
`AGENTS.md` section Validation ladder, and the header comments in
`project_config_baseline*.yml`, which state their own values as reasons.

## What this discharges

- [[t2608220920]] — the indicator baseline predates the weathergenr 2.0.0
  upgrade. A re-record settles it, but note that item's ask: it wants the
  generator move landed as its own attributable commit *before* any other
  re-record, so the slimming does not absorb it silently.
- [[t2608131718]] — the baseline's two flat config copies are stale since
  2026-08-12.

Related: [[t2608131807]] (collapsing the per-workflow copies; its cost 3 is
this same re-record), [[t2608202331]] (the actual lever).

## Progress

- [ ] Owner decision on [[t2608202331]] — the ESET/pixi exclusion, worth far
      more than everything below
- [ ] Decide whether a Wflow sysimage is worth boarding (P3-3 ranked it -39%)
- [ ] Edit `run_length` and `horizontime_climate` plus the coupled
      `future_horizons.far` — **riding along with the re-record R14 forces**,
      not as a standalone gate; the payback is 10-25 gates otherwise
- [ ] Re-record from the primary, WF1 with `--notemp`
- [ ] Correct `dev/reference/validation-ladder.md` and `AGENTS.md`, including
      the falsified "~2.6x / ~1.7x" claim
