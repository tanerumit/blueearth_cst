---
title: WF3 and WF4 print the project root in two different spellings
type: todo-item
status: backlog
effort: 1
area: console / observability
origin: noticed while closing t2609161645, 2026-09-16
queue:
created: 2026-09-16
updated: 2026-09-16
---

> [!note] Overview
> **What** — Make WF3 and WF4 spell the project root the same way in the run
> header and the `rule all` target banner. WF3 prints it relative, WF4 absolute.
> **Why** — One `run_workflows.py` run prints one fact two ways, which is the
> exact inconsistency the console work exists to remove.
> **Effort** — small

## The evidence

Same tree, same afternoon, 2026-09-16:

```
WF3   20:48:29 - RUN  Rule 3.00: all  [test_case/test_rapid]
      project      test_case/test_rapid

WF4   21:13:56 - RUN  Rule 4.00: all  [C:/Users/taner/workspace/.worktrees/blueearth_cst/session-1/test_case/test_rapid]
      project       C:/Users/taner/workspace/.worktrees/blueearth_cst/session-1/test_case/test_rapid
```

Both are true. Neither is wrong on its own, and the absolute form is arguably
the better of the two — `target_banner`'s whole argument for putting the root in
brackets is that a reader must be able to reconstruct the full path. But a
single `run_workflows.py` run shows both, one workflow after the other.

## Cause

`generate_scenarios.smk` takes `project_dir` from `generation_configuration`,
which leaves the config's own relative `test_case/test_rapid` alone.
`simulate_and_metrics.smk` writes
`Path(project["project"]["project_dir"]).resolve().as_posix()`. The difference
predates the console work; it was invisible until WF4 gained a header and a
target banner (t2609161645, 2026-09-16) and had somewhere to print it.

## Watch for

- `project_dir` is not only printed — it is the root `_relativize_paths` and
  `target_banner` strip against, and `declare_project_root` publishes it to
  `CST_PROJECT_ROOT` for `log_row`. Changing which form a workflow HOLDS changes
  what gets stripped from every path in the run, not just the header row.
  Resolving at the point of DISPLAY is the smaller change than resolving at the
  point of definition.
- Check whether anything persists `project_dir` into an artifact whose identity
  is content-addressed before changing the held value — a relative-to-absolute
  switch there would move a fingerprint.
- Whichever form wins, both the header row and the `rule all` bracket must take
  it: they are the same fact two lines apart.

## Progress

- [ ] Decide which spelling wins (absolute reads better; relative matches the
      config the user typed)
- [ ] Apply it to the header row and the target banner together, in both
      workflows
