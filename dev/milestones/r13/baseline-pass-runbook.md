# R13 — the two baseline passes

Operator runbook for the falsifier passes R13 cannot complete from a task lane.
The ordering is `config-tiers-design.md` §16.5(b); it runs **twice**, and the
hoist (commit 8) lands **between** the two.

> **From the PRIMARY checkout only.** A worktree's `test_case/test_local` is
> seeded from the primary and inherits its fixture *age*, so a baseline recorded
> from a lane makes fresh lanes fail tests the old worktree passes. This is the
> whole reason these steps are here rather than in the branch.

## Before you start

The branch is checked out in the task lane, so the primary cannot `switch` to
it — `fatal: already used by worktree`. **Detach at its tip instead.** A
detached checkout does not claim the branch ref, so the lane keeps it and the
primary gets the exact tree:

```powershell
cd ~/workspace/blueearth_cst
git status --short                 # must be clean; note the branch you are on
git branch --show-current          # <- write this down, you return to it after
git switch --detach feat/r13-config-tiers
git log --oneline -1               # expect the board commit at the tip
```

Nothing needs to be committed on the primary. The pass produces one tracked
file, `dev/baseline/manifest.json`; copy it back into the lane afterwards and
the lane commits it on the branch:

```powershell
# after the pass, from the primary
Copy-Item dev/baseline/manifest.json `
    ~/workspace/.worktrees/blueearth_cst/session-1/dev/baseline/manifest.json
git switch <the branch you noted>
```

Everything below runs inside `pixi shell`, or prefix each line with `pixi run`.

---

## Pass 1 — the split-only state

At this point `CROSS_WORKFLOW_READS` still carries its one entry. That is
deliberate: neutrality is validated **while the registry is populated**, so the
falsifier never has to attribute an unattributable shift.

### 1. Run the three workflows

Long. Detach them rather than running them in a foreground shell.

```powershell
$cfg = "test_case/snake_config_baseline.yml"

# WF1 — --notemp is MANDATORY. Rule 1.14 declares wflow's
# run_default/output.csv as temp(), and that file is the manifest's wf1
# discharge target: without the flag the gate fails "target missing" and
# reads as a defect. output_q.csv is NOT a substitute (rounded to 5 dp).
snakemake all -c 3 -s build_model.smk --configfile $cfg --notemp `
    *> .tmp/r13-wf1.log

snakemake all -c 3 -s analyze_projections.smk --configfile $cfg --keep-going `
    *> .tmp/r13-wf2.log

snakemake all -c 3 -s run_stress_test.smk --configfile $cfg `
    *> .tmp/r13-wf3.log
```

Read the tail of each log before moving on. **Read the tail, not the exit
code** — on 2026-08-21 all three of these produced only
`snakemake: error: argument --configfile/--configfiles: expected at least one
argument` because `$cfg` was empty in the shell they ran in, and the failure is
invisible unless you look.

**Rule 1.06 will fail first on any project whose spatial layer predates
`c6d35ba`**, with `NoDataException` on `data/spatial/geoms/river_attributes.
geojson`. That file is a declared output of rule 1.03 but is consumed by 1.06
through the spatial catalog at runtime and not declared as its input, so nothing
schedules 1.03. It reads like bad data and is a missing DAG edge. Until that is
fixed on `main`, force the producer first:

```powershell
snakemake -c 3 -s build_model.smk --configfile $cfg `
    --forcerun delineate_spatial_units --until delineate_spatial_units
```

This regenerates `rivers.geojson` to the new definition. Verified numerically
inert on the baseline fixture: `staticmaps.nc`, `wflow_sbm.toml`,
`locations.geojson` and `location_registry.csv` all stay byte-identical and the
wf1 discharge still matches.

Rule 3.06 will then refuse the experiment (`ModelDriftError`, forcing
`inmaps_historical.nc` moved) because WF1 rewrote the forcing. The move is
byte-level, not numeric — WF1's discharge is unchanged across it — so
re-recording the model reference is correct here.

### 2. Full suite, there, redirected to a file

```powershell
pixi run test-full -rs *> .tmp/r13-test-full-split.log
```

**Run this AFTER step 1, and check that you did.** On 2026-08-21 it was run
before the workflows and its six fixture skips were then misread as step 1
having failed. A `test-full` log older than the run tree is not evidence.

**Read the skip list, do not predict it.** Expect **9 -> 8 skips, and one more
pass**, measured 2026-08-22: only
`test_interchange_contracts.py:976` (the `weathergen_config.yml` fixture
predating weathergenr 2.0.0) resolves from a WF run.

The **five `temp() artifact absent` skips do NOT resolve** — they want WF3's
per-realization netCDFs, which are `temp()` and deleted unless WF3 also runs
with `--notemp`. Step 1 mandates the flag for WF1 only. Add it to the WF3 line
too if you want those five, and budget the disk for `RLZ_NUM x ST_NUM` members.
The three `needs --run-integration` skips are opt-in and never resolve here.

**These are NOT "the only tests that read a real config snapshot"** — an earlier
revision of this runbook said so and it is false, which matters because it made
a green suite look like it proved nothing about the composed snapshot. The
snapshot-reading coverage is:

```powershell
pixi run pytest tests/test_project_tree_inventory.py tests/test_snapshot_config_rules.py `
    tests/test_copy_config_files.py tests/test_check_project_consistency.py `
    tests/test_guard_invalidation.py -q -rs
```

166 tests, **zero skips**, all green against the freshly-run split tree on
2026-08-22. That is the composed snapshot's real coverage; run it explicitly
rather than inferring it from the full-suite skip list.

### 3. Read the falsifier

```powershell
python dev/scripts/check_baseline.py check
```

**Acceptance — CORRECTED 2026-08-22 after the pass was actually run.** The
original prediction below it was wrong in both directions; the evidence is in
`baseline-pass-1-result.md` and the corrected form is:

- **exactly two `type: yaml` targets differ:**
  - `test_case/test_local/config/runs/snake_config_build_model.yml`
  - `test_case/test_local/config/runs/snake_config_analyze_projections.yml`
- **the WF3 snapshot
  (`experiments/experiment/config/snake_config_run_stress_test.yml`) must NOT
  move**, and its staying at `00ef44f7…` is the split's WF3 neutrality proof
  rather than a failure to compose. WF3's `CONFIG_PROJECTION` is derived from
  `guarded_sections`, so R(run_stress_test) covers `build_model` and
  `analyze_projections` as well as its own section — every *populated* stanza of
  this config. Composition is an identity here, and because the snapshot is a
  dump of the very mapping WF3's rules read, equal digests mean WF3 reads
  value-identical config before and after the split. **If this one moves, that
  is the defect.**
- **the two CMIP6 change-factor CSVs and the wf1 discharge series must be
  unchanged.** These are the split's real output-neutrality test.
- **`q_indicators.csv` WILL differ, and it is not R13's.** The reference table
  was recorded 2026-08-16 under weathergenr 1.2.0; `cf5daa0` completed the
  1.2.0 -> 2.0.0 transition on 2026-08-17, and a different generator draws
  different realizations. Expect a low-flow-weighted shift (baseflow index and
  the driest-month/7-day-min metrics moving tens of percent while
  `q_annual_mean` moves ~1%) — that is the signature of re-drawn realizations,
  since preserving the mean is what a fitted generator does. Do **not** read it
  as evidence against the split.

The two yaml targets move because the snapshot stopped being a byte copy of the
project file and became the workflow's composed document (D-11.1). They shared
one hash (`00ef44f7…`) with each other and with WF3's precisely because all
three were identical whole-config copies; after this the two narrow ones differ
from each other and from WF3's, which is the change being made.

**A data target that moves for a reason you cannot name is a defect.** The
`q_indicators` shift above is named and dated; anything beyond it — and any move
at all in the change factors or the wf1 discharge — stops the pass.

### 4. `semantic_tree_diff`, if the tree shape moved

```powershell
python dev/scripts/semantic_tree_diff.py --help   # see §16.4 for the prediction
```

Expected: a **predicted, enumerated FAIL on the two moved snapshots and
nothing else** — `compare_copied_config` adjudicates snapshot CONTENT, so it is
not shape-only. (§16.4 says three; see the corrected acceptance above — WF3's
snapshot does not move in pass 1.)

### 5. Re-record, and only then

```powershell
python dev/scripts/check_baseline.py record
git add dev/baseline/manifest.json
```

Commit message should state the moved targets by name, and must say explicitly
that the `q_indicators.csv` move is `cf5daa0`'s weathergenr 2.0.0 upgrade and
not the split's — otherwise the manifest revision folds two unrelated causes
into one record with neither separately attributable, which is exactly what
`t2608071201` watches for.

**This step is gated.** See `baseline-pass-1-result.md` § The gate: recording
here bakes the generator's indicator change into the same revision as R13's
snapshot changes. The alternative is to re-record the indicator baseline on
`main` first, attributed to `cf5daa0`, so R13's pass has a control in which zero
data targets move. Do not record without that ruling.

---

## Commit 8 — the hoist

Only after pass 1's acceptance has been READ. One coupled commit:

- `wflow_outvars` moves from `workflows.build_model` to `shared:` in the four
  seeds, the template, and `tests/snake_config_fixture.yml`
- the two read sites move to the shared section (`build_model.smk`'s
  workflow-owned block, `run_stress_test.smk`'s `indicator_tables(...)` call)
- `SHARED_SEAM_KEYS` gains `wflow_outvars`, so D-9.2/D-9.3 reject a T2-planted
  copy by construction
- `RELOCATED_KEYS` is declared beside it, and the splitter emits the hoisted
  placement; D-15.4b's round trip becomes relocation-normalized, with a
  both-places-differing refusal
- `_WF1_GUARDED` in `check_project_consistency.py` gains
  `("shared", "wflow_outvars")` — **without this the hoist WEAKENS the guard**:
  a post-build edit would stop being refused at rule 3.01 and would first
  surface mid-experiment as `export_wflow_results`' missing-column error
- the pinned projection/derivation literals in `test_snapshot_config_rules.py`
  move with it
- `CROSS_WORKFLOW_READS` is emptied and retired; the D-9.6 scan's value-read
  assertion becomes a literal **zero**, which is what forecloses the
  registry-gaming construction permanently

---

## Pass 2 — the hoisted state

The identical five steps. The acceptance is **not** the same shape as pass 1's
corrected form — here **all three** `type: yaml` targets move, WF3's included,
because the hoist changes `shared:` and `shared` is in every entry point's
projection. Beyond the three, the same rule holds: no move in the change factors
or the wf1 discharge, and no *unnamed* move in `q_indicators.csv` (whether one
is expected at all depends on how the pass-1 gate was ruled).

The digests move again here, deliberately and expectedly: `shared:` is in every
entry point's projection, so `effective_config_digest` shifts for all four, and
`guarded_sections_digest` shifts with the guard contract. The shift is
**placement, not value** — both read sites read the same value with the same
default (`DEFAULT_WFLOW_OUTVARS`) — which is why zero data targets may move.

R13 is sealable only after this pass.

---

## What to paste back

For each pass: the tail of `check_baseline.py check`, the `test-full` summary
line, and the skip list. That is enough to say whether the acceptance held.
