## Verdict

verdict: revise  
doc_version: design-v3.md

## Findings

### ext2-1  [blocking]

- section: §6.6 Forcing lifecycle, the `p × 1` disk claim, and the lock
- finding: The fused member lifecycle has no `cst_0` branch. The manifest admits baseline members with `st_csv: null`, but §6.6 unconditionally writes a perturbation spec, invokes `impose_climate_change.R` with a stress CSV, and later deletes the WG-4 NC. Existing wf3 instead constrains perturbation to `cst >= 1` and passes `cst_0` directly from generation into downscaling.
- rationale: Any supported `run_historical: true` configuration will either fail when the perturbation script reads the null stress CSV or overwrite/delete the persistent baseline NC. The tracked K=12 fixture cannot expose this, so the workflow can pass every listed fixture gate while its historical branch is broken.
- suggested_fix: Specify a baseline lifecycle: for `baseline=true`, skip spec creation and perturbation, downscale the persistent baseline NC directly, record `inputs.st_csv=null`, and never delete that NC. Add a synthetic-manifest or separate-config gate exercising `cst_0` without changing the tracked fixture.

### ext2-2  [blocking]

- section: §5.2 Ledger schema — `ledger.jsonl`
- finding: `invocation_id` has incompatible scopes. Section 5.2 says it is minted by each `run_sweep` execution; §6.6 has `onstart` mint it earlier in the workflow lock and requires the runner to record the same value without defining the handoff; and finalization requires every `ledger_final.csv` row to match the current completeness record even though resumed sweeps reuse successes carrying earlier invocation IDs.
- rationale: Independently minted lock and runner IDs can make the runner reject every sweep. More importantly, after GF-2 or GF-13, `ledger_final.csv` naturally joins successes from multiple invocations; the specified identity check then hard-fails the reduce, defeating the headline hard-kill and partial-sweep resume paths.
- suggested_fix: Make the lock’s workflow invocation ID authoritative and explicitly have the runner adopt it. In `ledger_final.csv`, distinguish a uniform `finalization_invocation_id` from each member’s `succeeded_invocation_id`; validate completeness against the former. Extend GF-2 and GF-13 through successful reduction and assert the mixed-attempt provenance.

### ext2-3  [major]

- section: §4.4 Stage 4 — Reduce
- finding: `indicators/completeness.csv` is written only for an incomplete accepted run, but no mechanism removes it when a later retry reaches full completeness.
- rationale: After the designed partial→retry→complete sequence, the response surfaces become complete while the stale conditional file still reports missing cells from an earlier invocation. This leaves mutually inconsistent scientific products and can also contaminate tree comparisons even though the document claims the file is absent on every clean run.
- suggested_fix: On a full-completeness reduction, atomically remove any prior `indicators/completeness.csv`. Extend GF-13 to assert its absence after the successful retry.

### ext2-4  [major]

- section: §5.3 Atomicity, single writer, crash consistency
- finding: The corrupt-ledger recovery says to move `_state/` into its own child `_state/quarantine/<invocation_id>/`, excluding only `experiment.lock` and moving “everything else.” This recursively includes the quarantine directory and removes the declared `members.json`; it also leaves persistent member CSVs and TOMLs outside quarantine before starting a fresh ledger.
- rationale: The recovery command can fail while attempting a self-nested move, leave the workflow without its manifest sentinel, or overwrite the only surviving member artifacts during the forced full rerun. Thus GF-3 names a recovery lever whose preservation and restart semantics are not implementable as specified.
- suggested_fix: Define an explicit quarantine inventory. Preserve `experiment.lock`, `members.json`, and the quarantine root; move active ledger/finalization state and all current manifest-owned member outputs to a newly created quarantine generation before starting the fresh ledger. Add a gate that executes the recovery command to completion.

### ext2-5  [major]

- section: §7.4 Quarantine and orphans
- finding: Orphan deletion conflicts with the epoch-scoped legality check. A historical ledger row whose member is absent from the current manifest is legal only when it is a “known orphan,” while §7.4 defines orphans from artifacts on disk and permits the pruning tool to delete those artifacts without changing the append-only ledger.
- rationale: After the documented `prune_experiment_orphans.py --delete` action, the next fold can reclassify legitimate historical rows as corruption and refuse to start. GF-9 stops before pruning and therefore does not test this composition.
- suggested_fix: Define orphan ledger history independently of live artifact existence—for example, accept any schema-valid historical member generation absent from the current manifest—or append a durable tombstone before deletion. Add a resize→prune→reinvoke gate.

### ext2-6  [major]

- section: §4.2 Stage 2 — Generate
- finding: Publishing the per-realization date CSVs is specified only as `file.rename` into persistent destinations, with no checked overwrite or atomic-replacement rule. Those destinations already exist whenever generation reruns.
- rationale: On Windows, an existing destination can make the rename fail; if the return value is unchecked, the baseline NC may reflect the new seed while `sim_dates_rlz_<n>.csv` and `resampled_dates_rlz_<n>.csv` silently remain from the previous generation. If checked, routine regeneration fails instead.
- suggested_fix: Specify checked, cross-platform replacement semantics for the published CSVs and plots, preferably same-directory temporary publication followed by replacement. Gate a second generation with changed seeds on Windows and verify that every sidecar is replaced consistently.

### ext2-7  [major]

- section: §13 Step 8 — Performance floor confirmation
- finding: The repaired floor compares the correct scientific boundary, but still gates the architecture on one batch-first/pool-second timing pair with no repetition, counterbalancing, dispersion, or decision statistic.
- rationale: The pool leg systematically benefits from filesystem and OS-cache warming by the batch leg, while normal timing noise can independently reverse a strict `pool ≤ batch` comparison. The milestone can therefore retain or reject the architecture because of run order or noise rather than its performance, making the stop-and-review gate gameable despite the corrected boundary.
- suggested_fix: Predeclare a repeated, counterbalanced protocol—such as at least three AB/BA pairs—report all spans and dispersion, and gate on a stated robust statistic or uncertainty-aware margin rather than one wall-clock observation.