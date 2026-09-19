# Validation ladder — tiering, configs, and CI

The ladder table lives in `AGENTS.md` § Validation ladder. This file holds what does not fit there: how the tiers are drawn, which config a run takes, and how to read CI.

## Tiering

`test-fast` deselects the `workflow_contract` and `process_isolation` markers. Those tests each spawn a fresh Python process and build a Snakemake DAG, so they cost around fifty times what an ordinary test costs: they are roughly 2% of the suite and the large majority of its runtime. Count them with
`pytest tests/ -m "workflow_contract or process_isolation" --collect-only -q` rather than trusting a number written here — it drifts every time a rule gains a contract test.

Run the whole cheap tier rather than hand-picking relevant files: selecting by judgment saves little and misses cross-module regressions.

`test-fast` runs its workers in parallel (`-n auto --dist loadfile`). Keep `loadfile`: it puts every test in a file on one worker, which is what contains module-level state — a test that stubs a library process-globally stays confined to its own file. `--dist load` distributes per test and would break that. The floor is the per-worker import cost, so adding cores past a point buys nothing.

`test-contract` stays serial. Those tests share a `project_dir` and take `.snakemake` locks, so parallelising them needs each group proved independent first.

**`test-fast` is the local gate, including before a push.** CI runs the unmarked `pytest tests/` on ubuntu and windows from the push itself, so a local `test-full` re-proves on one platform what CI is about to check on two, for roughly ten times the wall-clock of the cheap tier. What it buys is knowing before the push rather than a quarter of an hour after it — worth paying only when a bad push is expensive to undo.

Run `test-full` at batch landing when the combined diff touched `blueearth_cst/shared/` or a `script:` signature, and before a milestone seal. Individual tasks use focused checks and separate commits; do not repeat the full gate per task. Those are the cases where meeting a failure on two platforms at once costs more than the wait.

Between merges and the next push, a `workflow_contract` regression can sit on local `main` across several branches, so bisect across all of them. Reading the CI run after each push is what bounds that window.

State gate costs as orders of magnitude, never in seconds. The marker names and the test count are durable; the clock is not.

`.testing-policy.yml` pins `scope: rapid`, and `auto_push: false` keeps the push a deliberate decision.

## Which config to run

Default to `project_config_rapid.yml`. Reach for `project_config_baseline.yml` only when the run's numbers are the point.

| Config | `project_dir` | Run it for |
|---|---|---|
| `project_config_rapid.yml` | `test_case/test_rapid` | anything you want to watch EXECUTE — a rule you edited, a DAG check, a WF3 smoke run, a figure render |
| `project_config_baseline.yml` | `test_case/test_local` | recording or checking `dev/baseline/manifest.json`, `tree-check`, a milestone seal, any number you will quote |
| `project_config_wf2_fast.yml` | `test_case/test_dev` | WF2 code iteration only — 2 series, and it drops `st_0` |

**Rapid's advantage is the GRID, not the years.** Both configs now simulate nine years (2046–2054) and generate the same ~44-year series — `t2608222155` moved the baseline off 17 years around 2078 on 2026-09-07. What is left is 10 members against 14: rapid's 2 × 2 grid plus `st_0` against baseline's 2 × 3.

This paragraph claimed "~2.6× less wflow time and ~1.7× less weather generation" until that item MEASURED it, and both halves were wrong. Per-member wflow cost is about `16 s + 0.59 s × simulated years`, so a 17-year member spent about 10 s simulating and about 16 s starting up — the window was worth ~18%, not 50%, and the measured whole-workflow gap was about 1.2×. Weather generation went the other way entirely: rapid's `3.11_generate_weather_realizations` took 45.8 s against baseline's 29.0 s. **The cost here is process startup**, not simulated years: the first member of a batch costs about 80 s more than the rest (Julia JIT plus the cold SBM path), which at three batches plus wf1's standalone run is roughly 320 s — a quarter of the run — spent starting Julia.

To change the generated-series length, change the END of `simulation_window` rather than its start: `compute_nr_years` anchors the series at 2010, so it spans 2010 → `simulation_window.end`. (`C-67` folded the former `horizontime_climate` + `run_length`/2 into that one declared year.) Whatever you set must stay inside a `future_windows` entry in the analyze_projections file — the alignment is computed independently of both keys, so a missed edit misaligns silently.

Rapid is cheap, not narrow. It gets `st_0`, which is what the two class-C month indicators derive from — and since `C-69` every config does, so this is no longer a way a config can quietly give up 2 of 11 `q` metrics — and it keeps two CMIP6 models, since a one-model config never runs the ensemble reduction. A config that gives up coverage must say which, as `wf2_fast` does.

Record the baseline from `project_config_baseline.yml` and nothing else; never point `check_baseline.py` at the rapid tree.

`check` exits **0** (targets match), **1** (the tree differs) or **2** (*nothing
was compared* -- an empty scope, or a fixture it cannot resolve). Treat 2 as "no
evidence", never as a pass: `--workflow generate_scenarios` declares no
non-figure target, so it reaches 2 by construction.

**The baseline manifest is BEHIND the baseline config, on purpose (`t2608222155`).** On 2026-09-07 the baseline set moved to a nine-year `simulation_window` (2046-2054) and the matching `mid` horizon; `dev/baseline/manifest.json` was deliberately NOT re-recorded, because the saving is 4-8% and a re-record costs a full run that repays after 10 to 25 gates.

**The standing tree is not an R12 migration reference.** It still contains the pre-2026-09-07 run and its matching manifest. Re-execution changes the configured years and projection horizon; R12 also changes scenario/metric paths, keys and ownership. Use the separately captured fresh P0 reference and GF-9 crosswalk for R12 acceptance. Do not interpret agreement between the old standing tree and its old manifest as evidence about the current configuration, or re-record it before scientific acceptance.

## Read the CI run after you push

Install the pre-push hook once per clone — cloning does not install it:

```bash
git config core.hooksPath .githooks     # runs the two ruff checks, ~2 s
```

Read the run regardless. The hook cannot see platform-specific failures, and a green local suite is no evidence about the ubuntu leg — the only place linux-64 is exercised.

`gh` resolves to `upstream` (`Deltares/blueearth_cst`) in this clone, not `origin` (`tanerumit/blueearth_cst`, where CI runs), so a bare `gh run list` queries Deltares, exits 0 and prints nothing. Point it at origin once per clone:

```bash
gh repo set-default tanerumit/blueearth_cst   # writes remote.origin.gh-resolved
```

In a script that must not depend on local config, pass `--repo tanerumit/blueearth_cst` explicitly, or use the API:

```bash
# the latest run, whatever branch it was on
gh api "repos/tanerumit/blueearth_cst/actions/runs?per_page=1" \
  --jq '.workflow_runs[0] | "\(.head_sha[0:7]) \(.status) \(.conclusion)"'

# which STEP failed, per leg — separates a lint failure from a suite failure
gh api "repos/tanerumit/blueearth_cst/actions/runs/<id>/jobs" \
  --jq '.jobs[] | "\(.name) -> \(.conclusion): " +
        ([.steps[] | select(.conclusion=="failure") | .name] | join(", "))'
```

Do not filter by `head_sha=<short sha>`: the parameter needs the full 40-character value and silently matches nothing otherwise.
