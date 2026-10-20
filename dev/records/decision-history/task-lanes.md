# Historical rationale for reusable task lanes

This record explains the August 2026 choice; it supplies no current worktree commands or policy.
Use [dev-task-and-session-workflow.md](../../reference/dev-task-and-session-workflow.md)
and [dev-validation.md](../../reference/dev-validation.md) for present practice.

## Why the arrangement changed

Reusable worktrees amortized environment creation and fixture copying. The previous territorial split
between development metadata and pipeline work caused 37 of 162 inspected commits to cross both
territories, approximately 23%. A task-oriented allocation avoided a second worktree visit for changes
that combined code with its board or documentation update.

The old analysis also reported that 72–85% of each workflow's commits touched shared modules.
A workflow-based territory therefore did not reliably imply independent writes. Of 35 plot-related
commits, 15 also changed non-plot code. These were measurements of that historical commit sample,
not present-day ownership statistics or a permanent limit on the number of sessions.

The tradeoff was explicit: fixed territories reduced overlap by construction; reusable task lanes
needed coordination of actual paths and shared resources. Later session practices superseded the
record's allocator commands, mandatory per-task process launches and assumptions about slot purpose.

## Historical observations behind isolation and coverage

- On 2026-08-02, two checkout-local Snakemake metadata stores planned 12 versus two jobs for the same
  project. Independent checkout locks also did not serialize writes into one shared output project.
  This observation supports coordinating output ownership; it is not today's prohibition on running
  workflows from worktrees.
- On 2026-08-07, a fresh worktree reported 1567 passing tests and 31 skips; 15 skips were the absent
  fixture layer. A passing software run did not establish fixture-dependent coverage.
- The old setup distinguished Pixi environment creation from installing the R weather-generator
  dependency. The actual current environment and execution setup belongs to the setup documentation.

## Source and scope

Condensed on 2026-10-20. No measurements were repeated or infrastructure policy changed.
Recover the full account, including retired commands and sample-specific fixture sizes, with:

```powershell
git show 5fa77b34:dev/records/decisions/task-lanes.md
```

The source itself identified `AGENTS.md` at `46f9df2` as the origin of its initial long-form policy.
