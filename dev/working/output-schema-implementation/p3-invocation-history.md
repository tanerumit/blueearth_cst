# Task Brief — P3 Invocation history

### Context

Read `AGENTS.md`, [master brief](master-brief.md), [schema](../complete-run-output-schema.md) §§5 and 10. P0 settles launcher coverage and parent failures; P1 defines references. P3 may proceed independently of P2 after coordinating shared entry points.

### Goal

Emit one common invocation JSON shape for direct workflow calls and parent/child launchers, distinguishing attempts from completed work.

### Non-goals

No new resume mechanism or scientific-run scheduling change.

### Allowed scope

Permitted: `scripts/run_workflows.py`, `scripts/simulate_system.py`, existing workflow journal/hooks and their direct tests/docs. Re-measure other launchers before claiming complete coverage. Forbidden: generated logs/output histories.

### Required changes (checklist)

- [ ] Implement `invocation/2` parent/child identity and linkage in schema §§5 and 10.4.
- [ ] Record direct calls, dry-runs, no-ops, startup failures and normal completion with truthful state.
- [ ] Leave existing history files untouched; new history readers need only the common schema.
- [ ] Implement P0's mandatory launcher coverage for direct and orchestrated calls; raw Snakemake cannot claim new-schema archive or complete invocation history. Preserve an explicit runnable `legacy_wf3_interim` wrapper route through P3/P4, then hand its removal to P5.

### Validation

Per edit: focused launcher/history tests. New tests must distinguish a child missing from its parent, a dry-run falsely marked productive, a parent launch failure with no child, and a hard termination falsely marked success. Exercise an enabled-WF3 wrapper smoke on the interim route. Run `pytest tests/test_cli.py` if entry-point signatures or declared inputs change; Python lint/format before commit. Full end-to-end history is checked in P7.

### Acceptance criteria

Every recorded child is attributable to its parent and actual inputs; attempt state cannot be mistaken for scientific readiness.

### Output requirements

Report state transitions exercised and any termination case that cannot be proven locally.

### Task constraints

Honor the master brief's human gate and shared constraints. Do not infer success from mere process launch.
