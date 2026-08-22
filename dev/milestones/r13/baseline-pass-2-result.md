# R13 — pass 2 (hoisted state) result

Record of the hoist-phase falsifier pass, run from the primary checkout detached
at `0d256a41` (the branch tip, carrying commit 8's `wflow_outvars` hoist),
2026-08-22.

**Outcome: the hoist is placement, not value — at the config level AND the
artifact level.** Exactly the three `type: yaml` snapshots moved; zero data
targets moved.

## What `check_baseline.py check` reports

```
FAIL - 3 target(s) differ from manifest:
  config/runs/snake_config_build_model.yml                     68708d48 -> 3c5539cb
  config/runs/snake_config_analyze_projections.yml             1d7edd8b -> 18411a59
  experiments/experiment/config/snake_config_run_stress_test.yml  00ef44f7 -> 4ab6f772
```

Unchanged: both CMIP6 change-factor CSVs, the wf1 discharge series, and
`q_indicators.csv`. That is pass 2's acceptance exactly.

## Why this was a real test and not a formality

The hoist re-fired **the whole WF1 model chain**, not just the snapshot rule.
Rules that re-ran: 1.01, 1.06, 1.07, 1.08, **1.09 `declare_wflow_outputs`**,
1.10, 1.11, 1.12, 1.13, **1.14 `run_wflow`**, 1.14b, 1.15, 1.15b, 1.16, 1.17.

1.09 is the rule that actually reads `wflow_outvars`, and 1.14 is downstream of
it. So the wf1 discharge target was **regenerated through the moved key** and
came back identical. Had the hoist changed the value, or changed which outputs
Wflow declares, this is where it would have shown.

Stronger still, at the artifact level — checked against the recorded model
reference before anything was re-recorded:

| model input | result |
|---|---|
| `staticmaps.nc` | byte-identical |
| `wflow_sbm.toml` | byte-identical |
| `forcing/inmaps_historical.nc` | moved |

`wflow_sbm.toml` is where `wflow_outvars` lands. It is byte-identical after 1.09
re-ran through the hoisted key. **The hoist changed no model artifact at all.**

## The relocation-only diff

The discriminating check: WF3's composed document already carried
`wflow_outvars` (under `workflows.build_model`, since its projection covers that
section), so its expected diff is *relocation*, not *gain*. Diffed against the
pre-hoist snapshot preserved at
`.tmp/scratchpad/2026-08-22_0900/pass1-preserved/` (sha `cba29d7e`):

```diff
  shared:
+   wflow_outvars:
+   - river discharge
+   - groundwater recharge
    workflows:
      build_model:
-       wflow_outvars:
-       - river discharge
-       - groundwater recharge
```

Nothing else. Same value, same order, same list.

**The asymmetry is not the one predicted.** The runbook said WF1 and WF2 would
*gain* the key while WF3 relocated. Measured, it splits by whether the
workflow's projection OWNED the key:

| snapshot | diff | why |
|---|---|---|
| `build_model` | **relocation** | its projection names `workflows.build_model`, which held the key |
| `run_stress_test` | **relocation** | its projection covers `workflows.build_model` too |
| `analyze_projections` | **gain only** | its projection never covered the key |

So WF1 behaves like WF3, and WF2 is the odd one — which is the sensible reading,
since WF1 is the workflow that owned the key. Runbook corrected.

## `q_indicators` held, and that corroborates the pass-1 attribution

WF3 was re-run in full and its indicators did **not** move. Pass 1 attributed
their earlier drift to `cf5daa0` (weathergenr 1.2.0 -> 2.0.0). This pass holds
the generator fixed at 2.0.0 and the indicators hold with it — independent
support for that attribution, since nondeterminism or an R13 cause would have
moved them again here.

## The ModelDriftError, and why re-recording was justified

Rule 3.06 refused the experiment on `forcing/inmaps_historical.nc`, as in pass 1
— WF1 rewrote the forcing. The reference was re-recorded (`--forcerun
write_model_reference`), but **only after** the premise it rests on was
established rather than inherited from pass 1: `staticmaps.nc` and
`wflow_sbm.toml` byte-identical, the wf1 discharge still matching the manifest,
and the forcing the sole mover. On that evidence the forcing move is encoding,
not physics.

Re-recording before checking would have papered over exactly the defect this
pass exists to detect.

## Step 2 — the suite

    3053 passed, 8 skipped, 1 xfailed in 410.44s

Skips identical to pass 1's post-run list (five `temp() artifact absent`, three
`needs --run-integration`); no failures. The count rose from pass 1's 3044
because the hoist commit `e3c9cbb` adds exactly nine test functions — checked
against its own diff, not assumed.

## Step 5 — recorded

    recorded: 7 target(s) -> dev/baseline/manifest.json (7 total)
    OK - 7 target(s) match manifest.

The manifest diff is the three snapshot digests and the provenance block, and
**nothing else**: neither `indicator_ref/74ed83c06b2e7e6c.csv` nor
`discharge_ref/9baa48f90ceaf138.csv` changed a byte. So "zero data targets
moved" holds byte-exactly, not merely within the comparator's tolerance.

`recorded_by.dirty` is `false` here, where pass 1's was `true` from a checkout in
the same condition. That is an unplanned control for `t2608221010`: the flag
tracks whether a reference sidecar moved, not whether the tree was dirty.

**R13 is sealable.**
