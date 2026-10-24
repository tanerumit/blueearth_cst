---
title: Isolate Snakemake state between parallel test workers
type: todo-item
status: backlog
effort: 1
area: tests
queue:
created: 2026-10-24
updated: 2026-10-24
---

> [!note] Overview
> **What changes** — Tests that invoke Snakemake no longer share the repository's `.snakemake` folder
> across pytest-xdist workers.
> **Why it matters** — On Windows, workers race on `.snakemake/iocache/latest.pkl` (`WinError 5`), so
> `test-fast` fails intermittently.
> **What it takes** — Find the test helpers that run Snakemake from the repository root and give each
> run its own directory.

## Progress

- [ ] Identify the Snakemake-invoking tests that use the repository as working directory.
- [ ] Give each run a per-test working or Snakemake state directory.
- [ ] Confirm with repeated `test-fast` runs.

Seen 2026-10-23 at main `8a515c00`:
`test_partial_indicators.py::test_cli_partial_run_succeeds_with_warning_and_strict_refuses[publication]`
failed in Snakemake `drop_iocache`, then passed alone and in the next full run at `de98a64a`.

Next: grep the test helpers for Snakemake invocations without an isolated `--directory`.
