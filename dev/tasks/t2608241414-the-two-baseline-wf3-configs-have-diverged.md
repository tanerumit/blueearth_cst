---
title: The two baseline WF3 configs have diverged
type: todo-item
status: backlog
effort: 1
area: test_case / configs
origin: R14
queue:
created: 2026-08-24
updated: 2026-08-24
---

> [!note] Overview
> **What** — test_case/snake_config_baseline_run_stress_test.yml is horizontime_climate 2078 / run_length 16 / run_historical true; test_case/snake_config_baseline_linux_run_stress_test.yml is 2050 / 20 / false. Same "baseline" name, different experiment - and the false on Linux drops the two class-C month metrics (q_wettest_month_mean, q_driest_month_mean), so the Linux baseline reports 9 of 11 q metrics.
> **Why** — One name should mean one experiment. Today the platform decides which window is run and how many indicators come back, which makes any cross-platform comparison of baseline numbers unsound. Found during the R14 _run_stress_test.yml walkthrough, 2026-08-24; test_case/ was outside that lane's declared scope. R14 C-69 deletes run_historical and would fix the metric half as a side effect, but the window divergence is independent and needs a deliberate choice of which config is right.
> **Effort** — small

## Progress

- [ ] <first step>
