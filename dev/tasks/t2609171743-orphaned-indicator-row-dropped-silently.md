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

Note the manifest DOES still hold the recorded reference table
(`ref_table` sidecar) for the old row, so a real comparison is still possible
without a re-run — that is the thing to do before any re-record.

## Related

- [[t2609171739]] — `simulation.json` cannot pass; the other half.
- [[t2609171320]] — the same subset-grammar hazard (12-hex vs 64-hex) in a test.
  Third instance of this shape; the first was the 2026-09-15 benchmark-row split.
