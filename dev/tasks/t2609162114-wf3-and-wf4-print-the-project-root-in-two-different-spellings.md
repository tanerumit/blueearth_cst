---
title: WF3 and WF4 print the project root in two different spellings
type: todo-item
status: done
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

## What landed

`f93b704e`. Neither spelling won outright: the root is absolutized for display
and then passed through `_relativize_paths` with NO project root, which is what
the `config` row beside it already did. A dev tree reads
`<repo>/test_case/test_rapid` -- SHORTER than the relative spelling it replaces,
and it says which of six worktrees it names. A production `project_dir` lives
outside the checkout, matches nothing and prints in full, which is correct:
there is no shared root to imply.

One new helper, `display_root`, called by both printers, so the two cannot drift
apart again by construction.

### `target_banner` keeps TWO variables for one directory, on purpose

`strip_root` is the form the CALLER passed; `display_root(...)` is what the
reader sees. They must not be collapsed. WF3 builds its targets as
`f"{project_dir}/logs/..."` from a relative config value, so an absolutized
strip root would match nothing, the strip would fail, and every WF3 target would
print LONGER than before the bracket existed. There is a comment in the code
saying this, because the two variables look redundant.

### Two warnings from this note, both checked and both negative

- **`declare_project_root` needed no change.** `_relativize_paths` already
  strips BOTH the absolute and the relative spelling of whatever root it is
  handed, so `log_row`'s shortening was never at risk. The class was already
  closed; only the display disagreed.
- **No fingerprint could move.** Every consumer of `project_dir` under
  `experiment/` calls `Path(...).resolve()` before use, so the held form never
  reaches a content-addressed document. The change is display-only in any case
  -- no Snakefile's held value was touched.

## Verified

`tests/test_snake_utils.py` 322 passed, `tests/test_cli.py` 20 passed, ruff
clean. Three new tests: that a relative-held and an absolute-held root produce
the SAME `project` row -- which IS the WF3/WF4 difference, at unit level; that a
project outside the repo is left whole; and that the bracket agrees with the
header row while targets still strip short, which is the regression the
two-variable split exists to prevent. Four existing expectations were updated to
the new spelling.

Live, same tree, which is the only way a console change is observable:

```
wf0   project  <repo>/test_case/test_rapid   RUN Rule 0.00: all  [<repo>/test_case/test_rapid]
wf3   project  <repo>/test_case/test_rapid   RUN Rule 3.00: all  [<repo>/test_case/test_rapid]
wf4   project  <repo>/test_case/test_rapid   RUN Rule 4.00: all  [<repo>/test_case/test_rapid]
```

`<data>` correctly stays absolute in the same header: it is outside the
checkout, and its location is the information.

## Cost paid, and a recurrence worth naming

Editing `shared/snake_utils.py` invalidated the rapid collection again -- the
request fingerprint hashes `blueearth_cst/` -- so WF3 regenerated and
`experiments/experiment_rapid` had to be rebuilt for the second time in one
session. This is the R12 identity contract, not a defect, and it is the standing
cost of ANY package edit. See the `t2609161645` row in `LOG.md`.
