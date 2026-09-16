---
title: The R12-split workflows emit no styled console output
type: todo-item
status: backlog
effort: 1
area: console / observability
origin: owner observation 2026-09-16
queue:
created: 2026-09-16
updated: 2026-09-16
---

> [!note] Overview
> **What** — Give generate_scenarios.smk and simulate_system.smk the same live console styling every other workflow has: a rule_banner on every rule, and log_row progress lines from the R12 experiment modules.
> **Why** — WF0/WF1/WF2 print 'HH:MM:SS - stage - message' lines and a banner per rule. WF3/WF4 print raw Snakemake scheduler chatter, so a user watching a run cannot tell what is happening. Owner observed it 2026-09-16.
> **Effort** — small

## Progress

- [ ] <first step>

## The evidence

Same run, `run_workflows.py` on `project_config_rapid.yml`, 2026-09-16.

WF0 — every step announces itself:

```
16:41:17 - config - Config snapshot -> config/runs/project_config_analyze_climate.yml
16:41:23 - levels - Pooled precip over 2 source(s): chirps, era5
16:41:35 - plot  - Reading store (chirps): <climate>/.../extract_historical.nc
```

WF3 — raw Snakemake scheduler output, and nothing else:

```
[Wed Sep 16 14:20:32 2026]
Finished jobid: 1 (Rule: prepare_collection_sources)
1 of 4 steps (25%) done
Updating checkpoint dependencies.
localrule prepare_weathergen_config:
    input: .../scenarios/requests/9c7e7d244734/request.json
```

## Two independent gaps, both measurable

**1. Missing rule banners.** `message: rule_banner(...)` is what replaces
Snakemake's `localrule <name>:` default. Counted 2026-09-16:

| Snakefile | rules | banners |
|---|---|---|
| `analyze_climate.smk` | 7 | 9 |
| `build_model.smk` | 20 | 19 |
| `analyze_projections.smk` | 10 | 9 |
| **`generate_scenarios.smk`** | **13** | **5** |
| **`simulate_system.smk`** | **3** | **0** |
| `experiment/rules/simulate_and_metrics.smk` | 4 | 4 |

The two files R12 created are the two that fall short. `simulate_and_metrics.smk`
is fully bannered, which shows the gap is not "WF4 has no banners" — it is
specific to the entry points.

**2. No `log_row` calls in the R12 modules.** `log_row` (`shared/snake_utils.py:3917`)
emits the `HH:MM:SS - stage - message` line. Twenty-nine modules call it. None of
these do:

```
scenario_provider  scenario_collection  collection_resolution  generation_plan
metric_plan        response_inventory   simulation_runner      simulation_record
```

So even a bannered WF3 rule says only that it started — never what it found, how
many scenarios it wrote, or which collection it reused. WF0's `plot`, `levels`
and `compare` stages all do.

## Not a vendored-console fix

AGENTS.md routes console DEFECTS to the `console-formatting` skill because
`dev/scripts/console.py` is vendored. This is not one of those: `rule_banner`
and `log_row` both live in `blueearth_cst/shared/snake_utils.py`, which is ours.
Fix in-repo; do not go upstream.

## Watch for

- `profiles/default/config.yaml` sets `quiet: reason`, which shapes what
  Snakemake itself prints. Check the banner change against that profile AND
  without it, since dropping the profile is the documented way to see why a job
  re-ran.
- Pick the `module=` stage labels deliberately — WF0 uses short stage words
  (`config`, `levels`, `plot`, `compare`, `extract`), not module names.

## Progress

- [ ] Banner every rule in `generate_scenarios.smk` (8 missing) and
      `simulate_system.smk` (3 missing)
- [ ] Add `log_row` progress lines to the R12 experiment modules, at the points a
      user wants: scenarios written, collection claimed or reused, responses
      inventoried, metric set published
- [ ] Verify against a live `run_workflows.py` run, not a test -- console output
      is only observable by executing
