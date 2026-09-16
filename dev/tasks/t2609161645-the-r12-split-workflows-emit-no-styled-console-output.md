---
title: The R12-split workflows emit no styled console output
type: todo-item
status: done
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

- [x] Restore the console apparatus (bd574db2)
- [x] Banner every rule, and restore two lost summaries (3f439854)
- [x] `log_row` at the aggregate points (d608e3c8)
- [x] Drop a wildcard's `_id` suffix on the finish line (762e81f2)
- [x] Verify on a live run, with and without the profile

> [!important] Root cause, found 2026-09-16 — a THIRD gap, prior to both below
> The two gaps this note counted are real, but they are downstream of one the
> note missed: `generate_scenarios.smk` and `simulate_system.smk` installed **no
> console apparatus at all**. No `install_console_style()`, no
> `onstart`/`onsuccess`/`onerror`, no `run_header`, no `run_summary`, no
> `declare_path_tokens`/`declare_project_root`, no `target_banner`. WF0, WF1 and
> WF2 carry all of it, and so did `run_stress_test.smk` at `868c4b7c^`.
>
> The R12 split (`868c4b7c`) carried the rule bodies into the two successor
> files but not the file scaffolding. Decision `0009` is silent on console, so
> this was an oversight, not a design call — which is also why
> `simulate_and_metrics.smk` kept its four rule-level banners: that is what
> copying rule bodies rather than files looks like.
>
> So the evidence above ("WF3 prints raw Snakemake scheduler output") is not a
> missing-banner symptom. The five banners WF3 did have were printing the whole
> time, unstyled, among un-suppressed default chatter, because no
> `_ConsoleHandler` was ever installed. **Restore before you add**: fixing the
> apparatus first is what made the remaining two gaps measurable.

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

> [!warning] Scope correction, 2026-09-16
> "WF3/WF4 emit nothing" is too strong. WF4's downscaling stage DOES print styled
> lines -- `16:58:38 - data_source - Reading scenarios/collections/.../run_09.nc`
> -- because that path logs through hydromt, and `simulate_and_metrics.smk` is
> fully bannered. The gap is narrower and precise: the two ENTRY-POINT Snakefiles
> R12 created, plus the eight R12 experiment modules. Fixing it is not "add
> logging to WF3/WF4".

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

## What landed

Four commits on `chore/post-r12`, in restore-then-add order:

| commit | lands |
|---|---|
| `bd574db2` | the apparatus, in all four files |
| `3f439854` | a banner on every rule; two `summary=` clauses the split dropped |
| `d608e3c8` | `log_row` in the R12 modules |
| `762e81f2` | `_console_wildcard_key` drops `_id`, as it already dropped `_num`/`_key` |

Every rule in both workflows is now bannered (13/13 and 3/3, plus 10/9 in
`simulate_and_metrics.smk` and 1/1 in `metrics_only.smk`).

WF4's three handlers live once at the bottom of `simulate_system.smk`, after the
`include:`, so both branches share one copy. `metrics_only.smk` therefore now
defines the five names that block reads; its log and benchmark names are `None`,
because that branch declares no `gather_logs`/`gather_benchmarks` rule.

`rule all`'s target list is a module-level constant, not an inline expression:
Snakemake's f-string preprocessor raises `UnboundLocalError: t1` on an f-string
inside a multi-line directive.

### The `log_row` rows go in the MODULES, not the Snakefiles

All seven instrumented functions are reachable only from a rule's `run:` body —
checked by call-site search; their only other callers are tests. That is the
whole constraint: WF3 and WF4 both resolve plans, read collections and validate
simulations at PARSE time, and a row on one of those paths fires before
`onstart` installs the style, printing unstyled and out of order on every
invocation including a dry-run. `warn_row` is the parse-time counterpart.

Aggregate points only. `retain_scenario_forcing` and `perturb_climate_realization`
fan out over `RLZ_NUM x ST_NUM` and already carry per-job context in their
banners; a row each is 400 copies of one sentence.

### A finding for whoever runs the rapid tree next

The scenario-request fingerprint includes `provider_code`, a content hash of
`blueearth_cst/`. **Any edit under that package invalidates a generated
collection**, so a code change alone moves the request id and WF3 regenerates.
This is the R12 identity contract working, not a defect — but it means a
console/logging change cannot be verified against a pre-existing rapid tree, and
it stranded two request/collection pairs under `test_case/test_rapid/scenarios/`
(`13cf306d1f65`, `241b2703f874`) while the code was still moving. Finish every
code edit BEFORE the live run, or `tree-check` picks up the orphans.

## Verified

`pytest tests/test_cli.py` after each Snakefile change — the dry-run over all
five entry points is what formats a new `message:` against real wildcard
namespaces, which is a RUN-time failure, not a parse-time one. Then
`--dry-run --forceall` on both entry points, and the 409-test module set for the
`log_row` commit.

The live runs the note demanded, on `project_config_rapid.yml`:

- WF3 full regeneration (0:01:43) — header, plan block, path-token legend,
  `RUN`/`DONE` with numbers and elapsed, per-member context on 3.08/3.09, target
  banner, one-line summary.
- WF4 full simulate-and-metrics (0:06:14) into a fresh experiment — same, plus
  the `experiment` and `operation` header rows.
- WF3 again with `--workflow-profile none`, which also exercised the REUSE row
  (`Reusing the retained collection ...; nothing to generate`).

The `_id` defect was found BY that first live run, not by a test: `RUN` printed
`[collection 967615227842 | run 07]` and `DONE` under it `[collection_id ... |
run_id ...]`. It predates the banners — WF4's 4.04 has written
`run {wildcards.run_id}` against a `[run_id 07]` finish line since the split.
