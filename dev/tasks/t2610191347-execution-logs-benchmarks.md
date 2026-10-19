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
> **What changes** — Execution folders contain console transcripts, workflow logs and Markdown/TSV benchmarks.
> **Why it matters** — Retain attributable history without mixing old parts or confusing job time with elapsed time.
> **What it takes** — Invocation-owned paths, stream capture, grouped reports and integration checks.

## Progress

Next: After user-controlled landing, close this item on main.

- [x] Agree layout.
- [x] Retain grouped benchmarks/TSV.
- [x] Isolate parts/records.
- [x] Capture owned processes.
- [x] Verify failure/retry cases.
- [x] Document behavior.
- [x] Verify workflows; commit.

Implementation: `2ea2f063`, `feat/named-indicator-sets`, session-2. Ready for landing; no landing or push.
Historical outputs remain untouched. Configuration archives/resource traces retain their locations.
Child output is plain text. Pre-existing indicator prerequisite edits remain unstaged.

## Evidence

Pixi/Windows; this task's ignored `.tmp/` holds:

| Output | Passed checks |
|---|---|
| focused-final.log | 726: runner, WF3 launcher, inventory, rule logging/contracts |
| diagnostics-final.log | 54: invocation, merges, console, Windows ownership |
| standalone-final.log | 27: WF0–WF2 and WF4 launcher contracts |
| gather-adapter.log | 12: formatter and real Snakemake script execution |
| execution-final.log | 6: timestamp, retry, transcript edge cases |
| lint.log / format-check.log | `pixi run lint` / `pixi run format-check` |
| e2e-retry.log | All-five execution and artifact assertions |

CLI/DAG/header checks: 9 passed, 24 deselected; workflow declarations unchanged afterward.
All-five command: `tests.test_workflow_end_to_end._run_and_assert_all_five(..., local_inputs=True)`.
Output root in session-2:
`.tmp/pytest/run-f1b10932b9ac4182b0e2193112c5b288/test_all_five_workflows_run_fr0/project`.

Input: verified 358-file rapid-v3 source copy, resealed against current contracts at `.tmp/e2e-bundle/`.
A gather-preamble fix passed directly; the all-five retry reused freshly generated WF0 products
and regenerated WF1–WF4. e2e-local.log retains an earlier code-identity failure.
No numerical-equivalence claim.

Board check reports nine unrelated existing errors.
