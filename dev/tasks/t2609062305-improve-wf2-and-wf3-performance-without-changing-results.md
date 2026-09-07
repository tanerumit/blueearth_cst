---
title: Improve WF2 and WF3 performance without changing results
type: todo-item
status: active
branch: refactor/wf2-wf3-performance
effort: 2
area: wf2 / wf3 performance
origin: Owner implementation request 2026-09-06
queue:
created: 2026-09-06
updated: 2026-09-07
---

> [!note] Overview
> **What** — Remove redundant intermediate I/O and calculations; improve scheduler resource accounting while preserving scientific results.
> **Why** — Reduce repeated CPU, memory and disk work across ensemble members and projection horizons.
> **Effort** — large

## Progress

- [x] Implement six scoped performance changes in session-4.
- [x] Verify numerical equivalence and obtain GPT-5.6 review.
- [ ] Complete full regression and baseline gates, then integrate.

Evidence: `dev/reference/wf2-wf3-performance.md`.
