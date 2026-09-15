# Task Brief — GF15 integration acceptance, Stage 4/4

### Context
Follow AGENTS.md, the [master brief](gf15-production-integration-brief.md), accepted D8 and the three prior handoffs.

### Goal
Reconcile software, provenance and scientific evidence into an explicit integration verdict.

Owner sequencing override, 2026-09-14: Windows-only evidence may receive a
bounded Windows verdict. Linux setup/parity stays deferred on the TODO checklist;
do not issue complete cross-platform acceptance until it is qualified.

### Non-goals
No milestone seal, successor baseline, new adequacy claim, merge or push.

### Allowed scope
Permitted: integration acceptance evidence and R12 task/master/validation-map updates. Approval-gated: failed or unavailable prerequisite and any scope change. Forbidden: editing prior verdicts, source evidence or tests to manufacture acceptance.

### Required changes (checklist)
- Check every design falsifier against executed evidence; retain E7 results and verdict separately for every platform.
- Confirm all original design findings implemented, portable report and compatibility checks passed, and comparison coverage complete.
- Run test-fast once at final integration; test-full once if shared/signature scope requires it. Read exact commands from pixi tasks, use qualified environment and retain full logs.
- Record accepted/failed/outstanding status without inferring seal or actual-bundle adequacy; update the tracked task board.

### Validation
Missing per-platform parity, surviving mutant, stale environment publication, broken old reader or incomplete comparison falsifies acceptance. Reconcile SHA bindings to the actual implementation; passing tests from another source version do not satisfy the gate.

### Acceptance criteria
Named independent reviewer/owner accepts complete Stage1-3 evidence and applicable software gates. Standing baseline/tree and milestone sealing remain separate.

### Output requirements
Concise integration verdict with exact evidence links, implementation commit, environment identities, coverage and remaining limitations.

### Task constraints
Coordinator cannot waive failed scientific gates or relabel a retained development rescore as independent validation.
