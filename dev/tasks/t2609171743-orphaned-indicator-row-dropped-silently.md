---
title: The baseline's indicator row is orphaned by the 12-hex metric-set rename, and the gate drops it silently
type: todo-item
status: backlog
effort: 1
area: baseline / manifest
origin: t2609171700 WF3+WF4 regeneration, 2026-09-17
queue: 1
created: 2026-09-17
updated: 2026-09-17
---

> [!warning] This is the more serious half of the 2026-09-17 finding
> [[t2609171739]] is a target that can never PASS. This is a target that is
> never COMPARED, and says nothing while it happens. Between them,
> `simulate_system`'s baseline scope is inert in both directions: the only
> entry it checks cannot pass, and the only entry that would tell you whether a
> NUMBER moved is dropped without a word.

> [!note] Overview
> **What** — `dev/baseline/manifest.json` keys its indicator row by the
> pre-shortening 64-hex metric-set path. `t2609152107` shortened every
> content-digest path segment to 12 characters, so the recorded key can no
> longer equal a resolved one. `main()` filters `rec_targets` to
> `p in in_scope_paths`, the row falls out, and **nothing reports the drop**.
> **Why it matters** — `q_indicators.csv` is the response surface. It is the
> one artifact whose difference would mean the science moved, and it is the one
> the gate is not looking at.
> **Effort** — small.

## Proved 2026-09-17, not inferred

```
RESOLVED in-scope paths for simulate_system:
    .../experiments/experiment/config/simulation.json
    .../experiments/experiment/results/metric_sets/b71ca72a2b13/q_indicators.csv

MANIFEST rows:
    .../experiments/experiment/config/simulation.json
    .../experiments/experiment/results/metric_sets/a50d1a4f6526a5e4...ab14/q_indicators.csv

rec_targets AFTER the in_scope filter: 1
   KEPT    .../config/simulation.json
   DROPPED .../metric_sets/a50d1a4f6526a5e4...ab14/q_indicators.csv
```

So `FAIL - 1 target(s) differ` is the whole truth about `simulate_system`: one
target compared, one silently discarded.

## Why the existing guards do not catch it

The gate has a rule for exactly this shape —

```python
for path in sorted(set(current) - set(rec_targets)):
    failures.append((path, ["target present but not in manifest"]))
```

— and it cannot fire here. Indicators are `REFERENCE_KINDS`, compared through
their tolerance comparators rather than fingerprints, so they never enter
`current`. The new `b71ca72a2b13` path is therefore absent from BOTH sides and
trips no rule. `check_indicator` iterates `rec_targets`, which no longer holds
the row, so its `"target missing on disk"` branch is never reached either.

This is a "no silent caps" violation in the repo's own terms: a tool that
bounds its own coverage must report what it dropped.

## Correction to the record

The `t2609171700` closure first said `q_indicators.csv` MATCHED a manifest
recorded on another branch, and read that as a strong reproducibility result.
**It is not true and was never measured.** The row was never compared. The
claim came from reading `FAIL - 1 target(s) differ` against a two-target scope
and assuming the other target passed — the same mistake shape as
[[t2609171320]], where an always-empty comprehension read as a passing
assertion. Corrected in `dev/LOG.md` the same day.

> [!done] Option 2 LANDED 2026-09-17 (`8170a020`); options 1 and 3 remain
> An orphaned row is now a named failure carrying the reason and the remedy,
> pinned by four tests in `tests/test_check_baseline_scope.py` — including one
> that the OLD segment length must still match (the case the check exists for)
> and one that another scope's staleness must not fail a scoped run.
>
> `simulate_system` now reports **FAIL - 2** rather than FAIL - 1: the orphan is
> visible instead of discarded. Nothing was re-recorded, and no comparison was
> restored — **the response surface is still unchecked**, which is what option 1
> is for.
>
> Found while implementing: `resolve()` is not self-consistent about path
> separators on Windows. `resolve_metric_set_dir` returns `Path.as_posix()`
> while every other template interpolates `project_dir` verbatim, so one
> manifest can carry both conventions. The matcher normalises both sides; a raw
> comparison passed on the repo's relative posix `project_dir` and did nothing
> on an absolute Windows one — the very shape of silent no-op this item is
> about. Worth a wider look at `resolve()` some day.

## Options

1. **Make the manifest's target keys RESOLVED-TEMPLATE-relative rather than
   literal paths** — store the row under its `TARGETS` template (or a stable
   logical key) and resolve at both record and check time. Fixes the whole
   class: any future identity rename stops orphaning rows. **Recommended.**
2. **Report unmatched manifest rows as a failure.** Narrow, and it belongs in
   regardless of option 1 — a recorded row that matches no in-scope path should
   be loud, not dropped. Cheapest real improvement; does not by itself restore
   the comparison.
3. **Re-record.** Restores a green gate and destroys the evidence, since the
   current tree's numbers would become the reference without anyone having
   compared them to the old ones. Not recommended alone; acceptable only after
   1 or 2, and after a deliberate comparison against the preserved reference
   table under `dev/baseline/`.

> [!done] The comparison was RUN, 2026-09-17: the numbers did not move
> `compare_indicator_table(reference, current)` over
> `dev/baseline/indicator_ref/5ab0f374553a5aff.csv` (recorded 2026-09-15 from
> the primary's R12-seal tree) against this worktree's freshly generated
> `metric_sets/b71ca72a2b13/q_indicators.csv`:
>
> ```
> ok: True
> 0/700 row(s) exceed tolerance across 55 group(s)
> max relative move = 0
> ```
>
> Not merely within tolerance — **exactly equal**. Identical key sets,
> 700/700 rows with `max abs difference = 0.0`, across 11 metrics x 5 locations
> x 21 unit_ids. The two files differ in bytes ONLY by line endings (the tracked
> sidecar is CRLF on checkout, the fresh output LF); normalise those and they are
> byte-identical.
>
> So the response surface reproduces across two worktrees, two branches and two
> independently generated collections. **This is the reproducibility result the
> `t2609171700` closure first claimed without measuring** — it turns out to have
> been true, but it was an assumption then and it is evidence now, and the
> difference matters.
>
> Note for whoever implements option 1 or 3: the CRLF/LF split means a `sha256`
> comparison of this target would FAIL spuriously on a Windows checkout. The
> parsed comparator is what makes it work, and the same hazard class as
> [[t2608301524]]. Do not "simplify" this target to a byte fingerprint.

## Do this FIRST, before any of the options

~~Nobody has ever compared this tree's `q_indicators.csv` to the recorded
reference.~~ **Done — see the callout above.** It cost nothing, needed no
re-run and no design decision, and it answered the question the gate could not:
the numbers did not move. That answer makes option 3 (re-record) safe on the
merits, where before it would have been recording an unexamined tree. It does
NOT make option 1 unnecessary: the next identity rename orphans the row again,
and the next person may not think to run this by hand.

## A constraint on the remedy, measured 2026-09-17

A **scoped** `record --workflow simulate_system` does NOT clear the orphan.
`cmd_record` prunes by resolved in-scope path, not by owning workflow, so a row
that no longer resolves is absent from `selected_paths` and survives the merge —
landing BESIDE the freshly recorded row. Only an **unscoped** `record`, which
overwrites `targets` wholesale, removes it. Both behaviours are now pinned by
tests. So the loud failure option 2 introduces is permanent until a full
re-record or a manual edit, which is the right trade but should be a known one.

## Related

- [[t2609171739]] — `simulation.json` cannot pass; the other half.
- [[t2609171320]] — the same subset-grammar hazard (12-hex vs 64-hex) in a test.
  Third instance of this shape; the first was the 2026-09-15 benchmark-row split.
