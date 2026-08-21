# R13 — the two baseline passes

Operator runbook for the falsifier passes R13 cannot complete from a task lane.
The ordering is `config-tiers-design.md` §16.5(b); it runs **twice**, and the
hoist (commit 8) lands **between** the two.

> **From the PRIMARY checkout only.** A worktree's `test_case/test_local` is
> seeded from the primary and inherits its fixture *age*, so a baseline recorded
> from a lane makes fresh lanes fail tests the old worktree passes. This is the
> whole reason these steps are here rather than in the branch.

## Before you start

```powershell
cd ~/workspace/blueearth_cst
git checkout feat/r13-config-tiers          # or merge it to main first
git log --oneline -1                        # expect the docs commit at the tip
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

Read the tail of each log before moving on.

### 2. Full suite, there, redirected to a file

```powershell
pixi run test-full -rs *> .tmp/r13-test-full-split.log
```

**Read the skip list, do not predict it.** Six of the nine skips seen in the
lane are the fixture-dependent layer itself (`temp() artifact absent`, the
stale weathergen fixture). After step 1 those have a freshly-run project to
read, so they should now RUN — and they are the only tests in the suite that
read a real config snapshot. If they still skip, step 1 did not do what it
should have, and nothing downstream is evidence.

### 3. Read the falsifier

```powershell
python dev/scripts/check_baseline.py check
```

**Acceptance — exactly this, nothing else:**

- **exactly three targets differ**, and all three are `type: yaml` config
  snapshots:
  - `test_case/test_local/config/runs/snake_config_build_model.yml`
  - `test_case/test_local/config/runs/snake_config_analyze_projections.yml`
  - `test_case/test_local/experiments/experiment/config/snake_config_run_stress_test.yml`
- **zero data targets differ** — the two CMIP6 change-factor CSVs and the wf1
  discharge series must be unchanged.

The three yaml targets move because the snapshot stopped being a byte copy of
the project file and became the workflow's composed document (D-11.1). All
three currently share one hash (`00ef44f7…`) precisely because they were
identical whole-config copies; after this they differ from each other, which is
the change being made.

**A data target that moves is a defect, not an expected shift.** Stop and
report it — the whole output-neutrality claim of the split is that this cannot
happen.

### 4. `semantic_tree_diff`, if the tree shape moved

```powershell
python dev/scripts/semantic_tree_diff.py --help   # see §16.4 for the prediction
```

Expected: a **predicted, enumerated FAIL on those three files and nothing
else** — `compare_copied_config` adjudicates snapshot CONTENT, so it is not
shape-only.

### 5. Re-record, and only then

```powershell
python dev/scripts/check_baseline.py record
git add dev/baseline/manifest.json
```

Commit message should state the three moved targets by name and that zero data
targets moved.

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

The identical five steps. The acceptance is **the same shape**: exactly the
three `type: yaml` targets differ, zero data targets.

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
