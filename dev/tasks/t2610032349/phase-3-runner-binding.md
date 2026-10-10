# Task Brief — P3: Shared creation, binding and resumption

### Context

Read root `AGENTS.md`, [master brief](task-brief.md), P0-reviewed plan and P2 API.
The same experiment must resolve identically through both supported simulation runners.

### Goal

Integrate explicit creation and early immutable binding so interrupted experiments cannot acquire
different scenarios, while valid completed work remains reusable.

### Non-goals

No Wflow checkpoint engine, native-response replacement, model-copy subsystem or algorithm changes.

### Allowed scope

Permitted: `scripts/run_workflows.py`, `scripts/simulate_system.py`, `scripts/suggest_experiment_name.py`,
`scripts/plot_workflow_dag.py`, `blueearth_cst/shared/snake_utils.py`,
`blueearth_cst/experiment/simulation_runner.py`, `simulation_record.py`, collection/preflight helpers,
affected experiment rules and exclusively owned consumers assigned at P0. Tests: runner, record,
all-workflow, naming-helper, DAG and CLI cases plus reviewed new binding tests. P2 owns allocation core.

### Required changes (checklist)

- Carry one resolved name through the invocation; implement creation/note flags and conflict validation.
- Bind request/automatic seed at reservation and resolved collection/runs before simulation.
- Reject known mismatches before expensive producers; recheck actual input identity after producers.
- Preserve supported legacy schemas; metrics-only never creates. Preview/DAG/validation reserves nothing.
- Keep completed runs; expose supported incomplete-job recovery. Diagnose native corruption safely.
- Make the naming helper read-only; update every consumer affected by its retired mutation behavior.
- Print root/name/status/selection and actionable recovery using the console conventions.

### Commit plan

Switch shared resolution, runner consumers, rule contracts and tests together. Preserve legacy reads;
remove only confirmed unused code after the switch, in the same verified unit where feasible.

### Validation

Per edit, select the affected files from:

```powershell
pixi run python -m pytest tests/test_run_workflows.py tests/test_simulation_runner_v2.py tests/test_simulation_record_v2.py tests/test_suggest_experiment_name.py tests/test_plot_workflow_dag.py -q
```

Before a rule/signature/input commit: `pixi run python -m pytest tests/test_cli.py -q`, affected rapid DAG
dry run and touched Python Ruff checks. P4 owns the final shared-contract execution gates.
Add falsifiers for changed request accepted under C/I/P state, redrawn automatic seed, duplicate name
resolution, preview writes, forced native replacement and metrics-only allocation. Assert effective
inputs and before/after state, not merely exit codes. Resource/comments/metrics changes need controls.

### Acceptance criteria

Both entry points pass the plan's selection/binding cases. Changed inputs refuse without altering old
results; compatible incomplete work can recover. Seed and exact run identities survive interruption.
The helper no longer edits config; user source files remain unchanged throughout normal execution.

### Output requirements

Report behavior differences, exact checks, recovery examples and remaining blockers; update the index.

### Task constraints

Changed generation settings alone do not redefine WF4 when it explicitly consumes the original ready
collection with generation disabled. Apply existing code/environment compatibility checks.
