# Task Brief — P2: Numbering and durable reservation

### Context

Read root `AGENTS.md`, [master brief](task-brief.md) and the P0-reviewed naming plan.
Existing `allocate.py` supports dated-name reuse and creation collision handling; preserve legacy reads.

### Goal

Implement reviewed selection, allocation history and atomic reservation without activating partial
runner behavior.

### Non-goals

No runner execution wiring, simulation changes, network-lock service or manual repair of old outputs.

### Allowed scope

Permitted: `blueearth_cst/experiment/allocate.py`, reviewed allocation-only package modules,
`tests/test_experiment_allocation.py`, `tests/test_validate_experiment_name.py` and allocation tests
assigned at P0. P3 owns runner and shared `snake_utils` integration. Generated records are test outputs.

### Required changes (checklist)

- Implement base/default/pin/legacy resolution, numeric ordering, `_100` growth and validation.
- Publish reviewed allocation history, high-water marks and reservation state with crash-safe ownership.
- Prevent deleted-number reuse, gap filling, accidental fallback and unknown-directory adoption.
- Test concurrent creators and exclusive ownership, including interrupted publication at each boundary.
- Provide a side-effect-free preview API and one explicit execution/reservation API for P3.

### Commit plan

Add the new API and tests while current callers remain runnable. P3 switches all owned consumers
together; only then remove newly unused legacy code that is not required for legacy reads.

### Validation

Per edit:

```powershell
pixi run python -m pytest tests/test_experiment_allocation.py tests/test_validate_experiment_name.py -q
```

Before commit: touched Python Ruff checks. New tests must falsify duplicate allocation, tombstone reuse,
lexicographic ordering, silent `_99` limits and preview mutation. Use synthetic roots and subprocess
contention/failure injection where appropriate; a mocked successful allocation proves no atomicity.

### Acceptance criteria

All naming-plan allocation cases pass; durable crashes recover deterministically; invalid ownership
fails loudly. Preview leaves allocation/experiment state unchanged. Current runners still work.

### Output requirements

Return interface, ownership/state evidence, exact focused checks and commit. Update the phase index.

### Task constraints

Use only P0-reviewed schema/paths. Do not activate an incomplete contract or weaken name constraints.
