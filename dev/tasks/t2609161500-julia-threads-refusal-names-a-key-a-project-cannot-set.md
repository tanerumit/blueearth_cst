---
title: The julia_threads refusal names a key a project cannot set
type: todo-item
status: backlog
effort: 1
area: config / error messages
queue:
created: 2026-09-16
updated: 2026-09-16
---

> [!note] Overview
> **What** — `snake_utils._positive_int(value, "shared.julia_threads")` labels its
> refusal with `shared.julia_threads`. `C-54` REMOVED that override from the
> project config entirely: `config_composition.RETIRED_KEYS` records the
> destination as `advanced_settings.runtime.julia_threads`, with no project-level
> equivalent. So a user who trips this error is told to fix a key they cannot set
> anywhere.
> **Why** — Strictly worse than the `shared.seed` staleness fixed in
> `chore/seed-key-refresh` (commit `c916b934`). That one named a key that MOVED;
> this one names a key that was DELETED, so following the message leads nowhere.

## Detail

Same structural blind spot as the seed case: `dev/scripts/sweep_stale_spellings.py`
cannot catch either, because `julia_threads` sits in `surviving_leaves()` — it is
the live key name under `advanced_settings.runtime`, so a name-based sweep cannot
tell the dead project-level use from the live toolbox-level one. The sweep's own
docstring records this as structural and warns against reading a green sweep as
"no stale readers".

## Fix direction

Relabel to `advanced_settings.runtime.julia_threads`, and check whether the
project-level read path is still reachable at all — if `C-54` removed the override,
a refusal for a project-supplied value may itself be dead code.

Check the same question for the other `surviving_leaves()` entries
(`reporting`, `members`, `simulation_window`, `stress_test`), which are invisible
to the sweep for the same reason and were never audited by hand.
