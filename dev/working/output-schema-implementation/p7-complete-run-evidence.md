# Task Brief — P7 Complete-run evidence

### Context

Read `AGENTS.md`, [master brief](master-brief.md), [schema](../complete-run-output-schema.md) §§2, 11. P1–P6 must be complete for the chosen migration scope.

### Goal

Demonstrate that one fresh isolated WF0–WF4 rapid run emits the proposed complete tree and that scientific behavior and legacy obligations hold.

### Non-goals

No incidental output pruning, baseline re-record, new schema design or upstream fixes.

### Allowed scope

Permitted: focused tests, tree/schema inventory tools, documentation corrections and an isolated rapid `project_dir` chosen under repository rules. Approval-gated: destructive replacement of any existing output tree. Forbidden: hand-editing run outputs or sealed baseline data.

### Required changes (checklist)

- [ ] Run all enabled stages against a fresh isolated rapid project and capture tree plus representative YAML/JSON/CSV schemas.
- [ ] Evaluate each relevant falsifier in schema §11, including references, old-output reading, temporary-file absence, lineage, metric joins and Wflow logs.
- [ ] Compare scientific results against the appropriate reference with stated tolerances; distinguish identity/path changes from numerical differences.
- [ ] Update the proposed schema to actual implemented facts, or record every deviation before claiming completion.

### Validation

Run narrow phase checks as needed for fixes. Run `pixi run test-fast` once at the approved landing boundary; run `pixi run test-full` once if `shared/` or a `script:` signature changed. Use the rapid config for execution. Run `check_baseline.py check` only if numerical outputs changed or a milestone seal is requested, against the baseline config with WF1 `--notemp`. A missing record, broken reference, unexpected retained intermediate or unexplained numerical difference falsifies completion.

### Acceptance criteria

Fresh tree and schemas match the accepted contract; required old readers work; no unexplained scientific delta remains. If the check fails, keep the branch and evidence for recovery rather than claiming success.

### Output requirements

Provide commands, results, captured tree/schema evidence, deviations, numerical comparison and residual risks.

### Task constraints

Honor the master brief's human gate and shared constraints. Do not infer completeness from accumulated `test_local` or `test_rapid` trees.
