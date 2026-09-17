---
title: 34 exception messages carry characters a cp1252 console cannot encode
type: todo-item
status: backlog
effort: 1
area: console / errors
origin: console styling pass (2026-09-17)
queue:
created: 2026-09-17
updated: 2026-09-17
---

> [!note] Overview
> **What** — Em dashes and section signs in exception messages across projections/, shared/ and model/ -- series_identity.py, config_composition.py, grid_weights.py, cartographic_map.py, variable_spec.py, build_wflow_model.py and others. Found by dev/scripts scan while fixing the same fault in the WF2 resolution report.
> **Why** — sys.stderr.encoding is cp1252 whenever output is piped, which is how scripts/run_workflows.py and CI capture it -- verified on this machine. So raising one of these under a redirect can fail with UnicodeEncodeError WHILE reporting the original error, replacing a clear diagnosis with a confusing one. The console-row rule in log_row's docstring already forbids this for rows; exception messages were never swept.
> **Effort** — small

## Progress

- [ ] <first step>

> [!warning] `run_workflows` now reconfigures **stdout** — this item is unaffected
> The rail glyphs in the runner's opening block needed UTF-8, so `main()` calls
> `sys.stdout.reconfigure(encoding="utf-8")` (2026-09-17). That covers the
> RUNNER's own rows and nothing else: `sys.stderr` is untouched, and the
> children keep writing through the locale codec into the same file. The
> premise above therefore still holds exactly as written — do not read the
> reconfigure as a partial fix for this.
