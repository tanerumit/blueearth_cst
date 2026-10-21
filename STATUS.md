# Project Status

**Updated:** 2026-10-21 11:39 Europe/Amsterdam (UTC+02:00)

**Context:** session-2 · `chore/fix-live-console-flush`

## Current session

- **Focus:** Validation-policy simplification is committed; this overview separates pending and landed work.
- **Resume here:** Await the next task or landing instruction; before landing, review `main..HEAD` and its
  affected-check evidence using the [validation reference](dev/reference/dev-validation.md).
- **Boundary:** Stay on this branch; switching, landing, and pushing require user instruction.

## Not yet on main

- **Committed — runtime fixes:** Heartbeat advancement and repeated WF0 provenance checks are fixed in
  `d69484f5` and `2949e718`, awaiting landing.
- **Committed — console presentation:** Shorter messages and paths plus full local timestamps are committed
  through `dccb51d5`, awaiting landing.
- **Committed — validation guidance:** Consolidated rules and the pre-publication batch gate are committed
  through `0c077d27`, awaiting landing.
- **Committed — status overview:** Initial adoption and this session-oriented structure await landing.
- **Uncommitted:** None; recheck Git before resuming.
- **Verification:** Documentation checks passed; runtime evidence still needs reconciliation against the
  pending batch, and the broad gate is due before pushing or releasing.

## Other active work

- **WF2 scheduler diagnosis:** The blocking frame remains unknown; capture production scheduler and worker
  stacks using the [diagnosis](dev/tasks/t2610062309/diagnosis.md).
- **Standalone plotting reuse:** Prove standalone use and scope packaging in the
  [plotting task](dev/tasks/t2610082103-shared-climate-plot-renderers.md).

## Recently landed

- **Shared plotting v1:** Landed on local main at `761c8e54`; standalone packaging remains separate.
- **Named indicator sets:** Landed on local main at `584c0704`; retain evidence and finish closure in the
  [task record](dev/tasks/t2610161523-integrate-multiple-metric-sets.md).

Git and the [task board](dev/TODO.md) own current state; this dated snapshot does not establish push status.
