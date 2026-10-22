# Walkthrough — add a named indicator set to an existing project

Worked example on `cst-cases` case `gabon-ntoum`, run 2026-10-17 with toolbox branch
`feat/named-indicator-sets` (session-2, fix `3f514807`). It shows how a user adds a custom indicator set to a
project that already has simulations, runs it, and checks the results.

## Setup choices

- `runs/gabon-ntoum` has never been run ("configured; not run"). Its sibling `runs/gabon-ntoum-review` (same
  basin and config, completed `simulation/3` experiment with 14 runs and one pre-change metric set) was
  copied to `runs/gabon-ntoum-sets-demo` so the review run stays untouched.
- A set can only choose among the 16 registered calculations (sealed design). For `q` and `gwr` the
  `default` set already computes all of them, so this example is a **curated, renamed subset**: authored
  entries give registered calculations their own key and title, and their numbers equal those definitions.
  Genuinely new statistics (e.g. a low-flow quantile, a 30-day minimum, annual-maximum recharge) need new
  registry methods in code.

## Step 1 — write the set file

Place it beside the project config. Start from `config/templates/indicator_set.template.yml`.

`applications/gabon-ntoum/indicator_sets/flow_regime.yml`:

```yaml
schema_version: 1
id: flow_regime
title: Ntoum flow regime
description: High-flow, low-flow and recharge indicators for the stress-test surfaces.
selection:
  indicators:
    # Registered definitions, by id.
    - definition: q_annual_mean
    - definition: q_baseflow_index
    # Authored discharge entries.
    - id: flood_peak_10yr
      title: 10-year flood peak
      description: GEV (L-moments) 10-year level of pooled annual maximum discharge.
      references: []
      calculation:
        method: pooled_return_level/1
        parameters: {kind: annual_max}
    - id: high_flow_p95
      title: High flow (annual 95th percentile)
      description: Water-year 0.95 non-exceedance discharge, a HIGH flow, averaged over years.
      references: []
      calculation:
        method: annual_summary/1
        parameters: {variable: q, statistic: p95}
    - id: low_flow_7day
      title: 7-day low flow
      description: Water-year minimum of the rolling 7-day mean discharge, averaged over years.
      references: []
      calculation:
        method: annual_rolling7_extreme/1
        parameters: {extreme: min}
    # Authored recharge entry.
    - id: recharge_depth
      title: Annual groundwater recharge
      description: Daily recharge depths summed per water year, averaged over years.
      references: []
      calculation:
        method: annual_summary/1
        parameters: {variable: gwr, statistic: sum}
```

Rules to remember:

- `id` must equal the name selected in the WF4 file.
- An authored `calculation` must match a registered method and its exact parameters. Anything else is
  refused with the allowed choices listed.
- Keep `references: []` unless you have a source to cite.

Registered methods and their allowed parameters:

| Method | Variable | Parameters |
|---|---|---|
| `annual_summary/1` | q | `statistic`: mean, max, min, p95 |
| | aet, gwr, precip | `statistic`: sum |
| | snow | `statistic`: max |
| | overland_flow | `statistic`: mean |
| `annual_rolling7_extreme/1` | q | `extreme`: min, max |
| `annual_min7_mean_ratio/1` | q | none (baseflow index) |
| `reference_month_mean/1` | q | `which`: wet, dry |
| `pooled_return_level/1` | q | `kind`: annual_max (10-year), rolling7_annual_min (2-year) |

## Step 2 — select the set in the WF4 file

In your own project, edit the existing WF4 file. The demo uses
`applications/gabon-ntoum/project_config_simulate_system_sets_demo.yml`:

```yaml
experiment_name: experiment

# Indicators only: reduce the retained responses, never start Wflow.
operations: [indicators]

# `default` keeps the standard set; `flow_regime` is defined beside this file.
indicator_sets: [default, flow_regime]
indicator_set_definitions:
  flow_regime: {config_path: indicator_sets/flow_regime.yml}
```

The demo also needed `project_config_sets_demo.yml`. It is identical to `project_config_review.yml` except
that `project_dir` points to the copy and the WF4 `config_path` points to the file above.

Notes:

- Use `operations: [simulations, indicators]` to simulate and reduce in one go.
- The legacy `operation:` / `metrics:` keys cannot be mixed with the new keys.

## Step 3 — dry run, then run

From the toolbox root:

```powershell
pixi run python scripts/simulate_system.py --config C:/Users/taner/workspace/cst-cases/applications/gabon-ntoum/project_config_sets_demo.yml --dry-run
pixi run python scripts/simulate_system.py --config C:/Users/taner/workspace/cst-cases/applications/gabon-ntoum/project_config_sets_demo.yml
```

- Named mode infers the target. Do not pass `--target`; it is refused in named mode.
- The dry run selected `experiment_01` (action `continue`) and planned two `prepare_indicator_plan`
  checkpoints, one per set request. The derive jobs appear only after the checkpoints run.
- The run took about 3 minutes:

```text
Metric set ready: 063cff964b5c…; 448 finite and 0 non-finite result estimates
Metric set ready: e87de17fd7d9…; 896 finite and 0 non-finite result estimates
Indicator set default current: metric set e87de17fd7d9, publication 86ae6f7ace9f → …\results\metric_sets\default
Indicator set flow_regime current: metric set 063cff964b5c, publication de3f50bf3cb2 → …\results\metric_sets\flow_regime
```

Each set completes independently. The runner exits nonzero unless every selected set is current.

## Step 4 — check the results

Readable outputs are in `runs/gabon-ntoum-sets-demo/experiments/experiment_01/results/metric_sets/`:

```text
default/        (standard set)
flow_regime/
  q_run_indicators.csv     q_group_indicators.csv
  gwr_run_indicators.csv   gwr_group_indicators.csv
  group_members.csv        group_metadata.csv
  indicators.csv           (the dictionary)
```

Machine records live in `_engine/metric_sets/names/flow_regime/`: `current.json`, `publications/`, and
`definitions/`, which holds a captured copy of the set file.

`indicators.csv` explains every metric. It has 25 columns, including method, parameters, output units,
grain, water-year block assignment and per-run block coverage. Summary for `flow_regime`:

| metric | grain | units | equivalent_definition | method / parameters |
|---|---|---|---|---|
| flood_peak_10yr | bundle | m3 s-1 | q_return_level_10yr_max | pooled_return_level/1, kind=annual_max |
| high_flow_p95 | run | m3 s-1 | q_mean_annual_p95 | annual_summary/1, statistic=p95; variable=q |
| low_flow_7day | run | m3 s-1 | q_mean_annual_7day_min | annual_rolling7_extreme/1, extreme=min |
| q_annual_mean | run | m3 s-1 | – | annual_summary/1, statistic=mean; variable=q |
| q_baseflow_index | run | 1 | – | annual_min7_mean_ratio/1 |
| recharge_depth | run | mm | gwr_annual_total | annual_summary/1, statistic=sum; variable=gwr |

Things to read in the dictionary:

- `flood_peak_10yr` is a bundle (design-group) metric. It appears only in the group table and has no
  run rows.
- `recharge_depth` is in mm as the mean water-year block depth. It is a mean annual depth only for
  complete, nonmissing water years; `block_coverage` shows which blocks are complete.
- `block_assignment` reads `YE-DEC (right-closed, right-labelled water-year blocks)` for a January water
  year.

Checks performed on the outputs:

| Check | Result |
|---|---|
| Every `flow_regime` value equals the `default` value of its equivalent definition | 448/448 rows equal (q run 224, q group 140, gwr run 56, gwr group 28) |
| New `default` (metric-set/4, new code) vs the review run's original `metric-set/3` (pre-change code) | all 6 table files byte-identical |

## Bug found and fixed during the walkthrough

**Symptom.** The Step 3 dry run first failed with `TypeError: 'NoneType' object does not support item
assignment` in `reservation_context.compare`.

**Cause.** A metrics-only dry run on an experiment that has a reservation compared the retained request
against no request. This affects legacy metrics-only and named indicators-only runs alike. Metrics-only
never captures a request, and the real run already skips that comparison.

**Fix.** Commit `3f514807` skips the comparison in the dry-run path too, with a regression test in
`tests/test_reservation_context.py`.

**Pre-existing.** The archived pre-change source fails the same way, so the bug was not introduced by
this branch.

## Left as is

- The `cst-cases` files are uncommitted for your review: the set file and the two `*_sets_demo.yml`
  configs. The run tree `runs/gabon-ntoum-sets-demo/` is git-ignored.
- `cst-cases` also has unrelated uncommitted deletions under `applications/colombia-chuzaco/`, which
  were not touched.
- `3f514807` changes runtime code, so landing the branch needs one more `test-fast` on its tip.
