---
title: Real-time scanning makes every Python import ~7x slower
type: watch-item
area: environment / dev machine
origin: test-runtime profiling (2026-08-20)
created: 2026-08-20
updated: 2026-09-04
---

> [!note] Overview
> **What** — Every Python import on this dev machine costs ~7x its normal per-module price, because the pixi prefix sits inside ESET's real-time scan surface. The fix is an exclusion, and **on 2026-09-04 the owner confirmed that permission is not obtainable**, so this is now a standing property of the machine rather than work.
> **Why** — It is most of the gap between this machine running the full suite in 59 minutes and CI running the same command in about 9. Anyone comparing a local timing against CI, or profiling a slow pipeline step, will re-derive this from scratch unless it is written down — and the diagnosis below is measured, not guessed.
> **Trigger** — Admin rights on ESET exclusions become available, IT policy changes, or the work moves to a machine without the scanner. Any of those converts this back to a `todo-item` under the same ID, and the exclusion paths and expected payoff are already recorded below.

## Cause: measured, 2026-08-20

`python -X importtime -c "import hydromt"`:

    3,173 modules imported
    15.2s cumulative
    4.79 ms per module   (normal is 0.3-1 ms)

Three signatures agree, and each rules something out:

1. **No warm-up.** Three consecutive fresh processes: 15.58s, 13.30s, 14.59s. The OS page cache does not help, so this is not disk IO.
2. **Cost is spread, not concentrated.** No module dominates by self-time; it is ~5 ms across a deep tree — `data_catalog` -> `adapters` -> `gis` -> `flw` -> `pyflwdir`, plus `geopandas`. That is per-file overhead, not one slow module.
3. **A real-time scanner is present.** `Get-CimInstance ... AntiVirusProduct` reports **ESET Security** alongside Defender, and `Get-MpComputerStatus` shows Defender's `RealTimeProtectionEnabled = False` — the two hand over, so ESET is doing the scanning. A scanner hooks each file OPEN and inspects above the page cache, which is exactly the constant, cache-immune per-file cost measured above.

`.pixi/envs/default` holds **94,661 files**, all inside that scan surface, and a fresh interpreter reopens thousands of them.

## What to exclude

The pixi prefix is the high-value one — it is the 94k files reopened on every interpreter start:

    <repo>/.pixi
    <repo>

Reading or setting ESET exclusions needs administrator rights, which is why this is filed rather than done. On a Windows 11 Enterprise machine the setting may be governed by IT policy, so treat it as an owner and IT decision.

## Expected payoff, and how to verify

| | now | if per-module drops to ~1 ms |
|---|---|---|
| WF2 dry-run parse | 19s | ~5s |
| `test_cli` (19 tests) | 147s | ~37s |
| `test-full` | 59 min | ~15 min |

Verify by re-running `python -X importtime -c "import hydromt"` and comparing the per-module figure, then re-timing the four dry-runs recorded in [[t2608202307]].

## Relationship to the other speed items

**Converted to a watch-item 2026-09-04.** The exclusion is unavailable: the
owner cannot obtain the permission, and on a Windows 11 Enterprise machine the
setting is IT-governed. Nothing below is retracted — the cause is measured and
still holds — but there is no action to take, so this stops being queued work
and becomes a fact to read when a local-vs-CI timing looks wrong.

**Consequence for [[t2609041718]]:** the per-process import cost is now
permanent, which roughly doubles what merging WF1 rules 1.07-1.09 would save.
That is recorded there; it does not by itself justify the merge.

This composes with [[t2608202307]] rather than replacing it. The scanner makes each import expensive; the parse-time import makes the Snakefiles pay for one they do not need. Fixing either helps; fixing both compounds. Nothing here affects CI, which already runs the same suite in about nine minutes.
