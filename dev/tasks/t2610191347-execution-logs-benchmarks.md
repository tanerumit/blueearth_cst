---
title: Retain logs and benchmark reports by execution
type: todo-item
status: backlog
effort: 2
area: runtime
queue:
created: 2026-10-19
updated: 2026-10-19
---

> [!note] Overview
> **What changes** — Execution folders retain transcripts, logs and Markdown/TSV benchmarks.
> **Why it matters** — Preserve execution history and distinguish job time from elapsed time.
> **What it takes** — Owned paths, capture, grouped reports and checks.

## Progress

Next: Retain evidence and finish archival; landed locally at `584c0704` on 2026-10-19.

- [x] Agree layout.
- [x] Retain grouped benchmarks/TSV.
- [x] Isolate parts/records.
- [x] Capture owned processes.
- [x] Verify failure/retry cases.
- [x] Document behavior.
- [x] Verify workflows; commit.

Implementation: `2ea2f063`; landed with `feat/named-indicator-sets` at `584c0704`. Session-2 is free.
Historical outputs preserved; configuration archives/resource traces unchanged.
Console follow-up: `0edf9ef9` restores live colours/progress; saved logs remain plain.

## Evidence

Pixi/Windows evidence in ignored `.tmp/`:

| Output | Passed checks |
|---|---|
| focused-final.log | 726: runner, WF3 launcher, inventory, rule logging/contracts |
| diagnostics-final.log | 54: invocation, merges, console, Windows ownership |
| standalone-final.log | 27: WF0–WF2 and WF4 launcher contracts |
| gather-adapter.log | 12: formatter and real Snakemake script execution |
| execution-final.log | 6: timestamp, retry, transcript edge cases |
| console-formatting-tests.log | 515: terminal/redirected capture, progress, logging, identity |
| console-launcher-tests.log | 82: all-workflow/WF3 launchers |
| console-lint.log / console-format-check.log | Lint/format passed |
| lint.log / format-check.log | `pixi run lint` / `pixi run format-check` |
| e2e-retry.log | All-five execution and artifact assertions |

CLI/DAG/header checks: 9 passed, 24 deselected; declarations unchanged.
Session-2 outputs:
`.tmp/pytest/run-f1b10932b9ac4182b0e2193112c5b288/test_all_five_workflows_run_fr0/project`.

Input: verified 358-file rapid-v3 source copy, resealed against current contracts at `.tmp/e2e-bundle/`.
All-five retry reused freshly generated WF0 products and regenerated WF1–WF4.
Console follow-up reuses this science evidence; its checks cover presentation and affected launchers.
No numerical-equivalence claim.

Board check reports nine unrelated existing errors.

Final landing: fresh all-five local execution and final software gate passed; execution logs and
benchmark artifacts passed assertions. Evidence: `t2610161523/.tmp/landing-20261019/`.
Task evidence remains intact pending archival. No push.
