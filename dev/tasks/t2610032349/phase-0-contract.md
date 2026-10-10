# Task Brief — P0: Review ownership and record contracts

### Context

Read root `AGENTS.md`, [master brief](task-brief.md), [naming plan](experiment-naming-plan.md),
and `dev/reference/validation-ladder.md`. Behavior is specified; exact reservation schemas and crash
publication sequence remain unresolved. Treat the plan's proposed output tree as a proposal.

### Goal

Produce a reviewed, implementable contract and assign every consumer to one phase before changing code.

### Non-goals

No runtime implementation, upstream patches or adoption of unlanded WF3 changes.

### Allowed scope

Permitted: this task's plan, phase briefs, inventory/evidence and master index. Runtime files and other
worktrees are read-only. New behavior or changed authority boundaries require an owner decision.

### Required changes (checklist)

- Inventory allocator, runner, DAG/log, seed, provenance and lock consumers; compare against phase scopes.
- Read existing closed schemas and project ownership facilities. Specify pending/resolved binding,
  allocation history/tombstones, failure-boundary reconciliation and exclusive writer behavior.
- Resolve automatic seed persistence and explicit collection reuse against the live WF3 run-id contract.
- Verify proposed generated paths and legacy-read precedence; assign each changed path to one phase.
- Apply `design-document` and `design-review-loop` to architecture review. Revise the existing plan
  instead of creating a second normative design. Record accepted revision and remaining blockers.

### Validation

Run before drafting, then after scope revisions:

```powershell
rg -n 'experiment_name|resolve_default_experiment_name|allocate_experiment' blueearth_cst scripts tests
rg -n 'auto|seed|archive_lock|simulation_intent' blueearth_cst/experiment scripts
rg -n 'active/|/active' scripts docs/site config/templates tests README.md
```

Falsifier: a run-path reader or writer omitted from the ownership inventory, or a crash boundary with
no deterministic recovery rule. Check every discovered path and publication transition explicitly.
Validate relative links and the board after recording the design; no execution gate is owed yet.

### Acceptance criteria

Versioned schemas, state transitions, compatibility rules and phase ownership are implementable and
reviewed; no unresolved scientific/authority choice is disguised as an implementation detail.

### Output requirements

Update the existing plan and index with reviewed revision, inventory, review evidence and blockers.

### Task constraints

Do not infer the latest contract from another branch without explicit integration authority. Review
may refine implementation mechanics; substantive changes to recorded user behavior need a decision.
