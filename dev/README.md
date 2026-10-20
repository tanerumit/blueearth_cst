# Development workspace

Start with [the current reference](reference/README.md) for development practices and toolbox design.
Developers and agents use the same guidance.

| Location | Purpose |
|---|---|
| [reference/](reference/README.md) | Current rules, architecture and contracts, maintained in place |
| `tasks/` and `TODO.md` | Active work and proposed changes; canonical board on main |
| [templates/](templates/README.md) | Reusable report/review templates and usage instructions |
| [records/](records/README.md) | Selected historical evidence and design context |
| `LOG.md` | Closure ledger pointing to retained outcomes |
| [scripts/](scripts/README.md) | Developer maintenance and verification tools |
| `baseline/` | Replication fingerprints and reference series |

`dev/TODO.md` and `dev/tasks/` link to main in configured sessions. References, templates and records
remain versioned with each branch's code. See [worktree coordination](reference/dev-task-and-session-workflow.md)
before setup or handoff.

Use [repository layout](reference/dev-repository-layout.md) for file placement and local scratch,
[record lifecycle](reference/dev-record-lifecycle.md) for retention, and
[validation ladder](reference/dev-validation.md) for checks.
User-facing documentation belongs in `docs/`.
