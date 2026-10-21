# Project status

Updated: 2026-10-21 11:22 Europe/Amsterdam (UTC+02:00)
Context: validation-policy follow-up on `chore/fix-live-console-flush`.

## Current objective

Maintain the bottom-up climate stress-test workflow while improving runtime reliability and reusable
plotting. This overview summarizes current work; the [task board](dev/TODO.md) and its linked notes
own task state. Reconcile this branch snapshot with the checkout and canonical board before resuming.

## Active work and next actions

- **Validation guidance:** consolidated in the [validation reference](dev/reference/dev-validation.md).
  The policy now selects affected paths before all-five execution, permits inspected prose exemptions,
  and reserves formal receipts for landing reuse. Next: apply it to the pending batch's actual delta.
- **Console/runtime follow-ups:** five commits after main's `25f6f41c` are committed locally on
  `chore/fix-live-console-flush` through `dccb51d5`. They address heartbeat advancement, repeated WF0
  provenance checks during figure export, and console wording/date-time/path display. Next: review
  the batch and its applicable validation evidence before owner-authorized landing.
- **Shared plotting:** internal v1 landed at `761c8e54`; standalone reuse and external packaging remain
  open. Next: prove standalone reuse and scope packaging in the
  [plotting task](dev/tasks/t2610082103-shared-climate-plot-renderers.md).
- **WF2 scheduler stalls:** local probes and stack-capture tooling passed; the production blocking
  frame is still unknown. Next: capture scheduler and worker stacks during a real stalled batch using
  the [diagnosis](dev/tasks/t2610062309/diagnosis.md).
- **Named indicator sets:** implementation landed locally at `584c0704`; task evidence and archival
  remain open. Next: retain needed evidence and finish archival through the
  [task record](dev/tasks/t2610161523-integrate-multiple-metric-sets.md).

## Blockers and constraints

Other blocked and queued work is listed on the [board](dev/TODO.md). This overview does not change
priorities or authorize execution, landing, or publishing.

- Keep scenario generation independent of GCM projections; see [repository instructions](AGENTS.md).
- Task coordination lives on main; implementation and this overview remain branch-versioned. See
  [task/session guidance](dev/reference/dev-task-and-session-workflow.md).

## Validation

- Validation-policy edits were checked for diff integrity, reference targets, reader impact, and
  consistency with the landing verifier, hook, CI configuration, and release guidance. They change
  guidance only; no workflow execution or scientific results were tested by this follow-up.
- Historical implementation checks and their limits remain in the linked task records. They do not
  establish that this branch's pending console/runtime batch has passed its landing gates; select
  those from the [validation reference](dev/reference/dev-validation.md).
