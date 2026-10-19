---
title: Retain logs and benchmark reports by execution
type: todo-item
status: active
effort: 2
area: runtime
queue:
created: 2026-10-19
updated: 2026-10-19
---

> [!note] Overview
> **What changes** — Each launcher execution retains its own console transcript, workflow logs, benchmark Markdown and raw TSV, linked from one summary.
> **Why it matters** — Shared workflow files overwrite execution history and can mix leftover parts; performance reports need attributable measurements.
> **What it takes** — Reuse invocation identities; isolate output paths, capture child console streams, update reports and test success, failure and reuse.

## Progress

Next: Integrate invocation-owned output paths and console capture, then verify launcher failure and reuse cases.

- [x] Agree flat execution layout and benchmark presentation with the user.
- [x] Implement benchmark grouping, retained TSV and Julia timing view — specialist checks passed.
- [ ] Isolate workflow log/benchmark parts and link outputs to canonical invocation records.
- [ ] Capture launcher and child console output while preserving Windows process ownership.
- [ ] Verify failures, interruptions, partial reruns, all workflow consumers and required batch gates.
- [ ] Update authoritative usage/layout documentation and commit the verified implementation separately.

## Contract and ownership

Use `logs/<UTC timestamp>-<short invocation ID>/` with summary.md, console.log, wfN.log,
wfN-benchmarks.md/tsv, optional wf4-indicators.log and invocation-owned `_parts/`.
Configuration archives and resource diagnostics keep their existing locations. Preserve historical outputs;
do not infer which old execution produced shared legacy logs. New attempt directories never mix old parts.

Root owns integration, launcher/stream handling, path migration and documentation. One Python specialist
owns merge_benchmarks.py and its tests; no additional agents are dispatched. Commit board notes on main;
implementation stays on feat/named-indicator-sets in session-2. No landing or push is authorized.
