---
title: The console's module column is unpadded, so the message column drifts
type: watch-item
area: console
origin: console styling pass (2026-09-17)
created: 2026-09-17
updated: 2026-09-17
---

> [!note] Overview
> **What** — Every console row is HH:MM:SS - module - message, and the module field is not padded, so the message column moves with the module name -- 'plot' against 'weathergen' is six columns of drift on adjacent lines.
> **Why** — Deferred rather than dropped, on evidence gathered while planning: _log_row_text writes the rule LOG PARTS as well as the console, each part is written by a separate process so a running width cannot align across one run, and merge_logs never reparses rows so it would not fix it either. That forces a fixed width, and the module names run from 'cst' (3) to 'data_catalog' (12) -- a width fitting the longest puts eight dead columns on most rows. The benefit is one column aligning; the cost is every log line in the repo changing.
> **Trigger** — A reader complains about the drift, or the module vocabulary narrows enough that a fixed width stops being wasteful. tests/ splits rows as line.split(' - ', 2)[2], which survives padding, so the tests are not what blocks it.
