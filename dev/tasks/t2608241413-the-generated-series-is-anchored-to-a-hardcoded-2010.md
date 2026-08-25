---
title: The generated series is anchored to a hardcoded 2010
type: todo-item
status: backlog
effort: 2
area: wf3 / weather generator
origin: R14
queue:
created: 2026-08-24
updated: 2026-08-24
---

> [!note] Overview
> **What** — prepare_weagen_config.py:34 computes n_years from a literal 2010, documented as "the end of the historical period", and :107 passes "start_year": 2010. No shipped project's historical window ends in 2010 - baseline 2016, baseline_linux / wf2_fast / fixture 2020. The anchor SHOULD derive from the end of the declared climate window (R14 C-70).
> **Why** — The anchor is wrong for every shipped config, so the generated series does not start where the historical record does. Changing it changes n_years, which changes the generated series, which moves numbers - so it needs its own baseline re-record and cannot ride R14's bundle, which is bound by success criterion 5 to move no number. Found during the R14 _run_stress_test.yml walkthrough, 2026-08-24, and deliberately kept out of the register.
> **Effort** — large

## Progress

- [ ] <first step>
