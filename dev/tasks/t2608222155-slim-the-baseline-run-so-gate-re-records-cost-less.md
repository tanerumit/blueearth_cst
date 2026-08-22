---
title: Slim the baseline run so gate re-records cost less
type: todo-item
status: backlog
effort: 2
area: baseline / run cost
origin: owner request, R14 branch opening (2026-08-22)
queue:
created: 2026-08-22
updated: 2026-08-22
---

> [!note] Overview
> **What** — Cut the wall-clock of a full `test_local` baseline run, then re-record `dev/baseline/manifest.json` from the slimmer config.
> **Why** — Every milestone seal and every numeric-output change pays a full baseline run; R14 will force a re-record anyway because it rewrites the config YAMLs the manifest fingerprints, so the slimming is free to land in front of it.
> **Effort** — large. Not because the edit is large — it is a handful of YAML keys — but because **the obvious lever is measurably not the lever** (below), so the first half of this item is a controlled measurement, not a config change.

## Measured cost profile

From `test_case/test_local/benchmarks/`, regenerated **2026-08-22** by the R13
baseline pass — current, not historical.

| workflow | rule-time | dominant rule |
|---|---|---|
| wf1 | 245.4 s | `1.14_run_wflow` **112.3 s** (46%) |
| wf2 | 23.5 s | `2.06` 15.3 + `2.07` 8.2 — negligible |
| wf3 | 995.7 s | `3.15_run_wflow` **615.2 s** (62%), `3.14_downscale` 196 s, `3.12_perturb` 133 s, `3.11_weathergen` 29 s |

Roughly 21 min of summed rule time; roughly 15 min wall at `-c 3`. That wf3
number is an **undercount** of a cold run: `3.04_delineate_spatial_units` and
`3.13_write_climate_data_catalog` were already up to date and did not appear.

wf2 looks cheap because the climate store is warm — but the whole
`test_local/data/climate` tree is **21 MB**, so cold is not much worse either.
wf2 is genuinely not where the time is.

## The obvious lever is falsified — read this before editing anything

The intuitive plan is "adopt rapid's temporal knobs: `run_length` 16 to 8,
`horizontime_climate` 2078 to 2050". Compare what the two configs actually
measured:

| | members | forcing window | `3.15_run_wflow` | wf3 TOTAL |
|---|---|---|---|---|
| `test_local` (baseline) | 14 = 2 rlz x (6 + st_0) | 17 yr (2070-2086) | 615.2 s | 995.7 s |
| `test_rapid` | 10 = 2 rlz x (4 + st_0) | 9 yr (2046-2054) | 516.2 s | 944.3 s |

Rapid runs **29% fewer members** at **47% shorter windows** and buys **16%**
off `3.15` and **5%** off the wf3 total. Per member: 44.0 s against 51.6 s.

The two other wf3 terms move the *wrong* way — rapid's
`3.11_generate_weather_realizations` is 45.8 s against baseline's 29.0 s, and
its `3.14_downscale` costs about 20 s/job against baseline's 14 s/job despite
the shorter window.

This says a large **fixed** per-Julia-session cost dominates, and both temporal
knobs move only the small variable remainder. Fitting `F` (per-session) and `S`
(per-member) against wf1's single-run 112.3 s and wf3's three-batch 615.2 s
gives **F about 84 s, S17 about 26 s**; feeding rapid's 516.2 s through the same
`F` gives **S9 about 26 s** — the per-member cost barely responds to window
length at all.

**Confound, stated rather than buried.** The rapid benchmarks are dated
**2026-08-17/18** and the baseline ones **2026-08-22**, on different days and
around the weathergenr 2.0.0 and Wflow-invocation changes. This is a
*cross-config, cross-date* comparison, not a controlled one, and the F/S split
is a two-point fit of an underdetermined model. It is strong enough to
**refuse the blind edit**; it is not strong enough to be quoted as a number.

It also contradicts `dev/reference/validation-ladder.md`, which claims rapid
costs "~2.6x less wflow time and ~1.7x less weather generation". Today's files
say about 1.2x, and *more* weather generation. That line needs correcting
whatever this item decides.

## Step 1 — the controlled measurement (do this first)

One knob, one tree, one sitting, `cpu_time` recorded alongside wall (the P3-3
lesson: the wall/cpu ratio is what caught the contaminated 2026-07-24 numbers,
`dev/milestones/p33/performance-baseline.md`).

Run a fresh Julia process against the `test_local` wf1 TOML twice — once at the
17-year window, once at 9 — with `dir_output` redirected to scratch so
`run_default/` is untouched. That isolates S's window-dependence with no
batching, no cross-date and no cross-config confound, and it settles whether
`run_length` is worth touching.

If S really is window-insensitive, the lever is **F times batch count**, not
window length: fewer, larger batches (`3.15` ran 3 batches for 14 members;
`batch_size_max` and `batch_disk_headroom_fraction` in
`config/advanced_settings.yml` are what bound B), and a shorter `run_length`
then helps only indirectly, by shrinking the `temp()` forcing/state footprint
that caps B.

## Coverage floor — what must not be cut, and why

The ladder's own rule: *cheap, not narrow; a config that gives up coverage must
say which.*

- **The ST grid stays 2 x 3 + `st_0`.** `precip.step_num: 2` (three levels) is
  the only thing in either config that exercises the rectilinearity spacing
  check in `blueearth_cst/shared/surface_axes.py` (`RECTILINEARITY_RTOL`); at
  two levels it is trivially satisfied. Rapid's 2 x 2 grid does **not** cover
  this. Nothing in-repo renders a contour, so cutting it is *available* — it is
  just narrow rather than cheap, and this is the tree whose numbers get quoted.
- **`run_historical: true` stays.** `st_0` is what the two class-C month
  indicators derive from; `false` silently drops 2 of 11 `q` metrics.
- **`realizations_num: 2` stays.** One realization runs no across-realization
  reduction.
- **`shared.historical_window` stays at 17 yr.** The floor is 16
  (`constraints.min_historical_years`), the extra year is deliberate margin,
  and the whole knob is worth about 7 s of wf1.
- **wf2 stays at 3 models x 2 scenarios.** 23.5 s and a 21 MB store; two or
  more models is required for the ensemble reduction. Near-free coverage.
- **Basin geometry (`uparea`, `resolution`) is out of scope.** It is the
  biggest remaining lever on wflow cost in principle, but F is
  cell-count-independent so the payoff is small, and `gauge_points`,
  `observations_timeseries.csv` and the manifest's `Q_101` discharge target are
  all tied to the current basin. Board it separately if it ever matters.

## Coupled edits and traps

- **`horizontime_climate` plus/minus `run_length`/2 must stay inside
  `future_horizons.far`** in `snake_config_baseline_analyze_projections.yml`.
  That alignment is *computed independently of the key* (the file says so), so
  a missed edit misaligns silently. At 2078/16 the current `far: [2070, 2090]`
  contains 2070-2086; at horizon 2050 it does not.
- **`compute_nr_years` anchors the generated series at 2010**, so the HORIZON
  sets series length, not `run_length`: 78 yr at 2078, 46 yr at 2050.
- **Run WF1 with `--notemp` for the re-record.** Rule 1.14 declares
  `run_default/output.csv` as `temp()` and that file is the manifest's wf1
  discharge target; without the flag the gate fails "target missing" and reads
  as a defect.
- **The four `snake_config_baseline_linux*.yml` are NOT baseline twins.** They
  point at `test_case/gabon`, use `resolution: 0.0062475`,
  `horizontime_climate: 2050`, `run_length: 20`, `run_historical: false`, and
  their header records that Linux end-to-end validation is deferred and "this
  file must parse cleanly". They do not feed the manifest and need no lockstep
  edit — though their drift from the windows variant is worth a separate look.
- **The re-record must run from the PRIMARY checkout**, not a lane.
- `t2608221010` means the new provenance may read `dirty: true` spuriously.
  Expect it; do not chase it here.

## Doc surface

`dev/reference/validation-ladder.md` (its config table hard-codes "14 x 17",
"78 years", "17 calendar years", and the falsified "~2.6x / ~1.7x" claim),
`AGENTS.md` section Validation ladder, and the header comments in
`snake_config_baseline*.yml`, which state their own values as reasons.

## What this discharges

- [[t2608220920]] — the indicator baseline predates the weathergenr 2.0.0
  upgrade. A re-record from a slimmer config settles it, but note that item's
  ask: it wants the generator move landed as its own attributable commit
  *before* any other re-record, so the slimming does not absorb it silently.
- [[t2608131718]] — the baseline's two flat config copies are stale since
  2026-08-12.

Related: [[t2608131807]] (collapsing the per-workflow copies; its cost 3 is
this same re-record).

## Progress

- [ ] Step 1 — controlled 17 yr against 9 yr S measurement, wall + `cpu_time`
- [ ] Decide the knob set from the measurement, not from rapid
- [ ] Edit `snake_config_baseline*.yml` plus the coupled `future_horizons.far`
- [ ] Re-record from the primary, WF1 with `--notemp`
- [ ] Correct `dev/reference/validation-ladder.md` and `AGENTS.md`
