Task Brief — repair the experiment freeze so it actually fires (`t2608290250`)

### Context

Canonical ruleset: `AGENTS.md`. Board item: `t2608290250`. Found by R14 P2's
third rung-2 falsifier; the evidence and three unchosen options are in the board
note, and this brief does not repeat them.

The one-sentence version: **`check_not_frozen` returns early on every real run,
so an already-run experiment's configuration is not settled and never has been.**

The mechanism, because it decides the fix:

```python
# blueearth_cst/experiment/write_experiment_config.py
def check_not_frozen(run_marker, out_path, document):
    if not out_path.is_file() or not has_run_successfully(run_marker):
        return                      # <- always taken at rule time
```

`out_path` is rule 3.07's own declared `output:`. Snakemake removes a job's
declared outputs before running it, so the record the check exists to read is
gone by the time it looks. Probed 2026-08-29 by a temporary `log_row` as the
first statement of the script, reverted in the same session:

```text
02:49:06 - probe - PROBE prev_exists=False marker=True
```

The comparator itself is CORRECT. Called directly on the same two files it
refuses correctly and names the changed key. Nothing below asks you to change
`_frozen_differences`.

Two facts that constrain the options:

- **`run_marker` is available at parse time.** It is rule 3.18's output — WF3's
  last rule — so on a re-run the marker from the PREVIOUS run is on disk before
  any job starts. `has_run_successfully` was `True` in the probe for this reason.
- **`experiment.yml` is not read by any other rule.** Its only consumers are
  this module and `semantic_tree_diff.py`, so moving where it is written or read
  does not ripple.

### Goal

An experiment that has produced results refuses a configuration change, through
the rule, on a real run.

### Non-goals

- Changing what counts as a difference. `_frozen_differences` and
  `RETIRED_EXPERIMENT_KEYS` are correct and out of scope.
- The `C-79` exclusion (`_NOT_IDENTITY`). Landed in R14 and independently
  tested.
- Any other guard. The WF3 drift guard is a different mechanism with a different
  defect history.

### Allowed scope

- **Permitted:** `blueearth_cst/experiment/write_experiment_config.py`,
  `run_stress_test.smk`, `tests/**`.
- **Approval-gated:** a new artifact path under `experiments/<id>/config/` —
  released by Gate 1 only if it rules option 1.
- **Forbidden:** `dev/milestones/**`; `config/**`; any other workflow's
  Snakefile.

### Required changes (checklist)

0. **Gate 1 first.** The three options are not equivalent and item 1 depends on
   which is chosen.
1. Make the check read a record Snakemake has not just deleted.
2. Keep the two behaviours the current code gets right, both of which are easy
   to lose in a move:
   - an **unchanged** rewrite is allowed. Snakemake may re-run 3.07 for reasons
     unrelated to the config, and failing on its own bookkeeping would make the
     guard fire on itself;
   - a rewrite whose only differences are **registered retirements** is allowed,
     and the record migrates forward — the retired keys drop out on that write.
3. Do not let the repair reintroduce the `C-79` regression: `compute:` must stay
   out of the freeze document, and changing `batch_size` after a run must still
   be allowed.

### Validation

- **Rung 1:** `pytest tests/test_experiment_config.py`. Necessary and **not
  sufficient** — every test in it calls the function directly, with a record the
  test itself wrote and did not delete. That is a faithful test of the
  comparator and says nothing about the rule, which is exactly how this defect
  survived. Do not treat a green run here as evidence the repair works.
- **Rung 2 — the falsifier, and it MUST go through Snakemake.** Two runs, and
  the control is half the evidence:

  1. run WF3 to completion on `project_config_rapid.yml`;
  2. change `n_realizations`, re-run WF3. It must **REFUSE** with
     `ExperimentConfigFrozenError` naming `n_realizations`;
  3. change only `compute.batch_size` instead, re-run. It must **PASS**.

  Step 2 is the repair. Step 3 is `C-79`, and without it a repair that freezes
  everything looks identical to a repair that freezes the right things.

  **Report the observed exit codes and messages, not "the suite is green".**
  Before this work, step 2 is accepted — that acceptance is the bug, and it is
  what the run has to invert.

- **Rung 3:** `pytest tests/test_cli.py` — 3.07's `input:`/`output:` may move.
- **Rung 4, once at the end:** `pixi run test-full`.
- Add a regression test that would have caught the original defect. A unit test
  that deletes `out_path` before calling `check_not_frozen` is the cheap form
  and is worth having; it is not a substitute for rung 2, because the thing it
  simulates is precisely what nobody knew Snakemake did.

### Acceptance criteria

- Rung 2 observed as stated: refuses on `n_realizations`, passes on
  `compute.batch_size`.
- An unchanged re-run of 3.07 does not raise.
- A registered retirement still migrates the record forward.
- `test-full` green.

### Output requirements

State which option Gate 1 ruled and why the other two were rejected — the board
note lists costs, not a decision.

Report rung 2's two runs with their exit codes. **If any rung passed first time,
say so plainly**; a log of terminal passes is not evidence about a defect whose
whole nature was that the existing tests could not see it.

### Task constraints

- Do not weaken the comparator to make a test pass. If the repair requires a
  change to what counts as a difference, that is a finding to report, not an
  edit to make.
- `K3`-style bundling does not apply; this is independently landable.

### Human gates

1. **Gate 1 — before any implementation.** Choose the record's home. The board
   note states the three options; the trade-off worth deciding on is:

   - **a sidecar** the rule writes beside `experiment.yml` and reads next time.
     Cheapest, and it splits one fact across two files — a reader who opens
     `experiment.yml` to see what froze is looking at the wrong one.
   - **stop declaring `experiment.yml` as an output.** Restores the read, and
     loses the DAG edge that makes downstream rules wait for it. Check what
     actually depends on 3.07 before costing this.
   - **move the check to WF3 parse time**, beside R14's other loud refusals.
     Both files are readable there, which is confirmed. Two consequences to
     weigh: the refusal arrives before any job is scheduled, which is friendlier
     than failing mid-run; and it would also refuse a `--dry-run`, which is
     arguably right — you cannot dry-run a change you may not make — but is a
     behaviour change a user will notice.

   Option 3 looks closest to the intent. It is not obviously correct, and the
   dry-run consequence is the part to rule on.
