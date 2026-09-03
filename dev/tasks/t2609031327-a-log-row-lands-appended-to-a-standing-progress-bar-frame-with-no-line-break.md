---
title: A log row lands appended to a standing progress-bar frame, with no line break
type: todo-item
status: active
branch: fix/console-bar-line-break
effort: 1
area: console
origin: owner report (2026-09-03)
queue:
created: 2026-09-03
updated: 2026-09-03
---

> [!note] Overview
> **What** — Every console writer that starts a new logical line resets the terminal line first (\r + erase), so a frame left standing by DaskProgress cannot be appended to.
> **Why** — run_and_tee already solves this with _pad_line_over; the _Tee / write_redraw path never adopted the convention, so a snakemake DONE row printed by the parent while another rule's bar is open lands on the bar's line.
> **Effort** — small

## Progress

- [ ] <first step>
