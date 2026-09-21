# Task Brief — P7 Complete-run evidence

### Context

Read `AGENTS.md`, [master brief](master-brief.md), [schema](../complete-run-output-schema.md) §§2, 11. P1–P6 must be complete for the chosen migration scope.

### Goal

Demonstrate that one fresh isolated WF0–WF4 rapid run emits the proposed complete tree and that scientific behavior meets the accepted comparison criteria.

### Non-goals

No incidental output pruning, baseline re-record, new schema design or upstream fixes.

### Allowed scope

Permitted: focused tests, tree/schema inventory tools, documentation corrections and an isolated rapid `project_dir` chosen under repository rules. Approval-gated: destructive replacement of any existing output tree. Forbidden: hand-editing run outputs or sealed baseline data.

### Required changes (checklist)

- [ ] Run all enabled stages against a fresh isolated rapid project and capture tree plus representative YAML/JSON/CSV schemas.
- [ ] Evaluate each relevant falsifier in schema §11, including references, temporary-file absence, lineage, metric joins and Wflow logs.
- [ ] Compare scientific results against the appropriate reference with stated tolerances; distinguish identity/path changes from numerical differences.
- [ ] Compare against [P0's clean pre-change WF3 reference](../design-runs/output-schema-contract/prechange-reference-retry.md) under explicit seed 123 with exact decoded values, coordinates, masks, calendar, dates and member lineage. Compare native responses and every requested metric against the separately captured independent predecessor WF4 comparator. Verify the new WF3-only automatic-seed formula and demonstrate that WF4-only elevation, settings and code changes leave its seed and collection identity unchanged; numeric parity with v1 is not required.
- [ ] Update the proposed schema to actual implemented facts, or record every deviation before claiming completion.

### Validation

Run narrow phase checks as needed for fixes. At approved batch landing, run `pixi run test-fast` once, and `pixi run test-full` once if `shared/` or a `script:` signature changed; do not run those gates per phase. Use the rapid config for execution, plus P0's separate automatic-seed fixture. Execute the accepted §10.9 negative comparator controls, including a changed value and swapped member. Run `check_baseline.py check` only under the separately planned baseline transition or milestone/numeric gate, against the baseline config with WF1 `--notemp`; do not use a predecessor-layout standing tree as new-schema evidence. A missing record, broken reference, unexpected retained intermediate or unexplained numerical difference falsifies completion.

### Acceptance criteria

Fresh tree and schemas match the accepted contract; no unexplained scientific delta remains. If the check fails, keep the branch and evidence for recovery rather than claiming success.

### Output requirements

Provide commands, results, captured tree/schema evidence, deviations, numerical comparison and residual risks.

### Task constraints

Honor the master brief's human gate and shared constraints. Do not infer completeness from accumulated `test_local` or `test_rapid` trees.
