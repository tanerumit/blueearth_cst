---
title: Four non-console modules still hedge their plurals
type: watch-item
area: wording
origin: console styling pass (2026-09-17)
created: 2026-09-17
updated: 2026-09-17
---

> [!note] Overview
> **What** — report.py, config_composition.py, surface_axes.py and indicator_tables.py still write '{n} thing(s)'. The 2026-09-17 sweep replaced that with plural() across the 26 rows that reach the CONSOLE and stopped at these four.
> **Why** — They write a markdown report, raise exceptions, and build tables -- a different audience from a console row, and the convention in log_row's docstring is explicitly about rows. Sweeping them is defensible and was deliberately not bundled with a change already touching 17 files.
> **Trigger** — Someone is editing one of those four for another reason, or the convention is extended beyond console rows.
