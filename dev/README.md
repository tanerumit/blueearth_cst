# dev/

Development tools, current guidance, and project records. Nothing here ships with the workflow engine.
This README is the entry point for contributors; linked policies apply to developers and agents alike.

## Layout

| Path | Purpose |
|---|---|
| `tasks/` | Live board notes and task material, maintained in the `main` checkout |
| `TODO.md` | Generated board view; edit the notes, then render |
| `LOG.md` | Closure ledger linking to retained outcomes |
| [reference/](reference/README.md) | Current conventions, procedures, and workflow contracts |
| `records/decisions/` | Decisions and their supporting evidence |
| [records/milestones/](records/milestones/README.md) | Milestone designs, plans, and evidence |
| `records/reviews/` | Review snapshots, subject to the retention policy |
| [scripts/](scripts/README.md) | Repository maintenance and inspection tools |
| `baseline/` | Replication fingerprints and reference series |

The [repository layout](reference/repo-layout.md) explains placement across the whole repository,
including task scratch, tool state, and runtime outputs.

## Start here

- Find current work in main's `dev/TODO.md`; use the
  [development workflow](reference/development-workflow.md) when creating, handing off, or closing work.
- Find implementation conventions in the [reference index](reference/README.md).
- Choose verification using the [validation ladder](reference/validation-ladder.md).
- Before promoting, shortening, or deleting records, read the
  [record lifecycle](reference/record-lifecycle.md).

## Worktree coordination

The [development workflow](reference/development-workflow.md#worktree-coordination) owns board location,
branch ownership, navigation setup, and handoff procedures.

## Exceptions

These entries are deliberate exceptions to `project-system`'s development-folder layout.

| Path | Owner | Retention | Depends on |
|---|---|---|---|
| `baseline/` | Replication validation | Replace only with a recorded successor | `check_baseline.py` |
| `00-current-board-main/` | Old branch hooks | Remove the legacy junction locally | `.gitignore` |

The exception consumers are `dev/scripts/check_baseline.py` and root `.gitignore`.
Baseline paths also have workflow and config
consumers; inspect them before moving the directory. Legacy junction removal is documented in
[navigation setup](reference/development-workflow.md#local-scratch-and-navigation).

## The promotion rule

See [promotion](reference/record-lifecycle.md#promotion) for preserving cited material and updating its
consumers before task closure or legacy cleanup.
The [working-folder retirement record](records/reviews/working-folder-retirement-2026-10-20.md)
maps the final legacy sources to their retained homes.

## The retention rule

See [retention](reference/record-lifecycle.md#retention) for review deletion, partial supersession, and
[closure-ledger entries](reference/record-lifecycle.md#closure-ledger-entries).

## Milestone records

The [milestone index](records/milestones/README.md) owns the list of milestones and their seal dates.
The [record lifecycle](reference/record-lifecycle.md#milestone-records) owns their preservation rules.

## Working rules

See the [development workflow](reference/development-workflow.md) for task admission, coordination,
verification, and closure. Root [AGENTS.md](../AGENTS.md) routes agents to these same shared policies.
