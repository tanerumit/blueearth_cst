---
title: check_baseline record contaminates its own dirty provenance flag
type: todo-item
status: backlog
branch:
effort: 1
area: baseline / provenance
origin: R13 pass 1 re-record (2026-08-22)
created: 2026-08-22
updated: 2026-08-22
---

> [!note] Overview
> **What** — `cmd_record` writes the sidecar reference tables (`indicator_ref/*.csv`, `discharge_ref/*.csv`) while building `new_rows`, and only afterwards calls `git_provenance()` to fill `recorded_by`. Those sidecars are TRACKED, so `git status --porcelain` is already non-empty by then and `dirty` records `true` on a checkout that was clean.
> **Why** — The flag's own docstring says it means "the recorded artifacts were produced by code that matches no commit". It now means that *or* "a reference table moved", and the two are indistinguishable. It misfires precisely when a re-record changed values, which is the case the flag exists to annotate. A future reader sees `dirty: true` and cannot tell whether to trust the commit beside it.
> **Effort** — small

## Evidence

R13's pass-1 re-record, primary detached at `9cbb72a` with a clean tree.
`dev/baseline/manifest.json` came back with:

```json
"recorded_by": { "branch": "HEAD", "commit": "9cbb72aa40fb", "dirty": true }
```

The porcelain status at that moment contained only what `record` had itself
written:

```
 M dev/baseline/indicator_ref/74ed83c06b2e7e6c.csv
```

(The manifest is written *after* `git_provenance()`, so it is not the
contaminant — the sidecar is.)

## The ordering

`dev/scripts/check_baseline.py`:

- sidecars written during fingerprinting — `_write_reference_series` and the
  indicator sidecar's `sidecar.write_bytes(...)`
- `payload = {... "recorded_by": git_provenance() ...}`
- `args.manifest.write_text(...)`

So the contamination window is every sidecar whose content moved.

## Fix options

1. Capture `git_provenance()` **first**, before any fingerprinting, and carry it
   into the payload. Smallest change; also the most honest reading, since the
   question is "what was the checkout when the run happened".
2. Have `git_provenance()` ignore paths under `dev/baseline/` when computing
   `dirty`. Narrower but needs the exclusion kept in sync.

(1) is preferred. Note `branch: "HEAD"` on a detached checkout is correct and
intended — the docstring says a detached HEAD is handled best-effort — so leave
that alone.

Related: [[t2608071201]] (re-records accepted without reading the diff),
[[t2608220920]].
