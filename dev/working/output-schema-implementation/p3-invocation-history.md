# Task Brief — P3 Invocation history

### Context

Read `AGENTS.md`, [master brief](master-brief.md), [schema](../complete-run-output-schema.md) §5. P1 defines references; P3 may proceed independently of P2 after coordinating shared entry points.

### Goal

Emit one common invocation JSON shape for direct workflow calls and parent/child launchers, distinguishing attempts from completed work.

### Non-goals

No new resume mechanism or scientific-run scheduling change.

### Allowed scope

Permitted: `scripts/run_workflows.py`, `scripts/simulate_system.py`, existing workflow journal/hooks and their direct tests/docs. Re-measure other launchers before claiming complete coverage. Forbidden: generated logs/output histories.

### Required changes (checklist)

- [ ] Implement the common parent/child invocation identity and linkage in schema §5.
- [ ] Record direct calls, dry-runs, no-ops, startup failures and normal completion with truthful state.
- [ ] Preserve old history interpretation where the schema requires it.

### Validation

Per edit: focused launcher/history tests. New tests must distinguish a child missing from its parent, a dry-run falsely marked productive, and a hard termination falsely marked success. Run `pytest tests/test_cli.py` if entry-point signatures or declared inputs change; Python lint/format before commit. Full end-to-end history is checked in P7.

### Acceptance criteria

Every recorded child is attributable to its parent and actual inputs; attempt state cannot be mistaken for scientific readiness.

### Output requirements

Report state transitions exercised and any termination case that cannot be proven locally.

### Task constraints

Honor the master brief's human gate and shared constraints. Do not infer success from mere process launch.
