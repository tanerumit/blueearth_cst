---
title: A CRLF checkout of pixi.lock re-keys every CMIP6 series
type: todo-item
status: backlog
effort: 1
area: projections / series identity
origin: R14 Gate 5
queue:
created: 2026-08-30
updated: 2026-08-30
---

> [!note] Overview
> **What** — REDUCER_HASH folds file_digest(pixi.lock) in as its env fingerprint, and that digest is taken over the WORKING-TREE bytes. A worktree checked out with CRLF endings hashes differently from one with LF, though git reports both clean and the content is identical modulo \r. Every cst_reducer_module_hash and the cst_series_digest derived from it then differ across worktrees of the same commit.
> **Why** — The series digest is the cache key for stage A. Two worktrees at the same commit re-derive every CMIP6 series instead of sharing, and a tree comparison between them reports ten provenance differences that look like a numerical change and are not. Found at R14 Gate 5, where it accounted for 10 of the 23 content differences (dev/milestones/r14/config-shape-gate5.md, row 7). Likely fix: normalize line endings before hashing, or hash the git blob rather than the working file.
> **Effort** — small

## Progress

- [ ] <first step>
