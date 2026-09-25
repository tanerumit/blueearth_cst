---
title: Make a code change to wf2's rule 2.04 actually re-trigger it
type: todo-item
status: backlog
effort: 2
area: wf2
origin: R6
queue: 2
created: 2026-08-07
updated: 2026-09-01
---

> [!note] Overview
> **What** — Make a code change to wf2's rule 2.04 actually re-trigger it.
> **Why** — Snakemake's `code` trigger does not reach it, so a fix to that rule can land and never re-run — the output stays stale and looks current.
> **Effort** — Unknown: the cause was found in 2026-07 and the mechanism is understood, but the fix shape is not settled.

> [!done] Re-diagnosed and fixed 2026-09-25 (`maint/identity-and-baseline`)
> The 2026-07-25 explanation below (`temp()` on 2.04 + `ancient()` on 2.05) is
> obsolete: D9 removed both. The mechanism today, read from Snakemake 9.6.2:
> `persistence._code` hashes only `shell:` bodies, and a `script:` rule is
> re-queued when the script's **mtime** is newer than its outputs -- regardless
> of `--rerun-triggers`. So the job DID re-queue; the script then cache-hit on
> its own series digest, whose `REDUCER_HASH`/`STAGE_B_HASH` hashed only the
> hand-listed kernel functions. They had missed `intersection` (the very edit
> this note was filed for), `_spatial_dim`, `check_axis`, `_to_datetime_index`,
> `assert_weightable`, `canonical_kind`/`change_kind` and six module constants.
>
> Fix: `kernel_hash` follows the call graph from the listed roots into
> `blueearth_cst` (stop-set: logging/console modules) and hashes plain module
> constants; the member merge + units stamping moved out of `__main__` into the
> rooted `merge_member_series`. Both closures are pinned in
> `tests/test_series_identity.py`, with a cross-`PYTHONHASHSEED` check.
>
> **Known remaining gap:** the rest of the reduce script's `__main__` block
> (series attrs, netCDF encoding) is still unhashed -- metadata, not numbers.
> Keep arithmetic in rooted functions.

## Progress

- [x] Re-diagnose on Snakemake 9.6.2 and fix the kernel coverage

## Refs

- Migrated from `dev/followups.md` on 2026-08-07, when the board replaced it. Prose below is that
  entry verbatim; it is the reproducible context, not a summary.

## Detail

**Snakemake's `code` rerun-trigger does NOT reach wf2's rule 2.04.**
Discovered 2026-07-25 while trying to propagate the `intersection()` fix.
Rule 2.04 `monthly_change` names `get_change_climate_proj.py` directly as its
`script:`, so an edit to it should have re-run the rule — it did not, even
under an explicit `--rerun-triggers code`. Cause is structural: 2.04's output
is `temp()` (already reclaimed) and rule 2.05's inputs are wrapped in
`ancient(...)`, which tells Snakemake to ignore their timestamps; once 2.05's
outputs exist the whole 2.04 layer leaves the DAG, so there is no job whose
code hash could be compared. Same family as the P3-3 finding that
`--forcerun generate_weather_realization` does not cascade the wf3 sweep.
**Practical rule: after fixing computational code in this repo, `--dry-run`
first to confirm the affected rules are actually in the DAG, and reach for an
explicit `--forcerun <rule>` rather than trusting the code trigger.** Worth
considering whether the `ancient()` wrappers on 2.05's inputs are still
earning their keep, or whether they are over-broad insurance that now hides
real staleness.
