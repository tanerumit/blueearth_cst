Task Brief — P2: guard, freeze, and digest under the new layout

### Context

Canonical ruleset: `AGENTS.md`. Design: `config-shape-design.md` §9.
Program: `config-shape-master-brief.md`. **Depends on P1.**

> [!note] **Unblocked 2026-08-28.** The phase's real blocking edge was P4,
> not P1b; P4 has landed and is green on both CI legs, so the three rung-2
> falsifiers below can each be run as stated. Ruling:
> `config-shape-p2-sequencing-decision.md`. **The WF1 snapshot in
> `test_case/test_rapid` is still the pre-migration v1 document, so re-run
> WF1 before running any falsifier** -- a refusal against a stale snapshot
> says nothing about the guard.

- `E1`/`E2` established these are THREE mechanisms, not one, and the scoping
  document had been treating them as one.
- **A WF1 snapshot does not carry WF3's sections** (`copy_config_files.py:89`,
  confirmed in `compose_config`). `compute:` was therefore never inside the
  drift guard, and carving it out there is a no-op.
- **`D-9.6` is established: the three-site asymmetry is an OVERSIGHT, not a
  protective narrowing** (2026-08-28). The design left this open because
  the two answers give different targets. The evidence is the hoist's own
  commit: `git log -S wflow_outvars` names `e3c9cbbf` for
  `check_project_consistency.py` and does NOT name it for
  `run_stress_test.smk` -- R13 moved the key out of `workflows.build_model`,
  added it to site (1), and left sites (2) and (3) covering it only through
  the container it had just left. Site (1)'s comment argues at length for
  guarding the leaf and gives no reason to exclude it from the rerun
  trigger. The invariance constraint at `run_stress_test.smk:44` is also
  satisfied: `build_experiment_config` emits `{experiment_name,
  run_stress_test}` and nothing else, so no experiment overlay can reach a
  T1 key and every T1 section is experiment-invariant by construction.
  **P2 closes it rather than preserving it.**
- The keys that forced today's leaf-by-leaf narrowing — `seed`,
  `julia_threads` — are removed from T1 by `C-51` and `C-54`, so the exception
  has no remaining cause.

### Goal

The guard's key list is DERIVED rather than maintained, and `compute:` leaves
configuration identity where it actually lives: the digest and the freeze.

### Non-goals

- Re-pointing the guard at the composed document rather than the snapshot.
- Any change to what the freeze compares, beyond the `compute:` exclusion.

### Allowed scope

- **Permitted:** `blueearth_cst/experiment/check_project_consistency.py`,
  `blueearth_cst/experiment/write_experiment_config.py`, the
  `CONFIG_PROJECTION` tuples in the four `*.smk`, and `tests/` for the above.
- **Forbidden:** `config/defaults/**`; `dev/milestones/**`.

### Required changes (checklist)

1. Replace `_WF1_GUARDED` with the derived rule: **guard every key of the WF1
   snapshot except the `workflows.*` `enabled` flags** (design D-9.1).
2. Exclude `compute:` from `CONFIG_PROJECTION` (`C-79`, design D-9.3), so
   `batch_size` leaves `effective_config_digest` and `_frozen_differences`.
3. Delete any comment or docstring claiming the guard carves out `compute:`.
   It never did (design D-9.2).

### Validation

- Rung 1: the tests covering the two modules changed.
- Rung 2 — three falsifiers, each an experiment built to fail:
  - **"the guard now covers `climate:`"** — build a model, edit
    `climate.selected`, run WF3. It must REFUSE. Today it does not; this is
    the hole the derived rule closes.
  - **"toggling a workflow does not refuse"** — build a model, set
    `workflows.analyze_projections.enabled: false`, run WF3. It must PASS.
    This is the one structural exception; without it the derived rule is wrong.
  - **"`batch_size` no longer invalidates a run"** — run WF3 to completion,
    change `compute.batch_size`, re-run. No frozen-experiment refusal.
- Rung 3: `pixi run test-full` — this phase touches `shared/` and a `script:`
  signature, which is the `workflow_contract` / `process_isolation` tier's own
  trigger. Run ONCE at the end of the phase, not per commit.

### Acceptance criteria

- No hand-maintained guarded-section tuple remains in the tree.
- All three falsifiers behave exactly as stated above.
- `pixi run test-full` green.

### Output requirements

Report each falsifier's OBSERVED behaviour, not just that the suite passed. A
passing suite is evidence the code does what its tests say; only these three
experiments are evidence about the properties this phase claims — and two of
them assert an absence, which no test suite reaches.

### Task constraints

- The guard reads the SNAPSHOT, not the composed document. Do not change that.
- Do not weaken D2. The leaf-by-leaf exception is removed because R14 removed
  its cause, and the commit message must say so.
