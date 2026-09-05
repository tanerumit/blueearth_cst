---
title: Restore a rules overview at the start of each workflow, keyed on rule ids
type: todo-item
status: backlog
effort: 1
area: console
origin: console screen 2026-09-05
queue:
created: 2026-09-05
updated: 2026-09-05
---

> [!note] Overview
> **What** — One block after the run header listing every rule of the workflow by id, with a gutter mark on the ones that will run, last-run durations, fan-out counts and summary clauses.
> **Why** — A skipped rule prints nothing, so a re-run's console cannot say whether the workflow has 6 rules or 19 -- information that exists nowhere else once Snakemake's Job stats table was collapsed.
> **Effort** — small

## The problem this solves

Snakemake's `Job stats:` table was collapsed to one line on 2026-09-05
(`d9b0de36`), on the argument that it was 22 lines on a fresh WF1 where every
count was 1 and every rule name was about to scroll past on a RUN line.

That argument holds for a FRESH run and inverts on a re-run. Measured on the
rapid fixture the same day:

```
build_model.smk declares          19 rules
a completed WF1 re-run has         6 to do
the other                         13 print NOTHING
```

A skipped rule emits no console line at all, so today's console shows six RUN
lines and gives a reader no way to tell whether this workflow has six rules or
nineteen, nor which thirteen were already satisfied. **That is the information
the block carries that the RUN lines structurally cannot**, and it is what the
design is anchored on -- not on re-listing names.

## Agreed shape (owner ruling, 2026-09-05)

Full ledger with a gutter mark, plus all three extras. Rejected: a compact
plan listing only what runs (loses the shape of the workflow), a status word
column instead of the gutter, and per-rule target outputs (`target_banner`
already reports those at the end of a run).

```
  plan -- 19 rules, 6 to run, 13 up to date        est 0:00:22

  >  1.01   snapshot_config
     1.02   delineate_region                0:00:31
     1.03   delineate_spatial_units         0:00:14
     1.04   extract_historical_climate      0:00:16  clip global climate to the basin
     1.05   plot_climate_source             0:01:02
     ...
  >  1.11   write_outlet_index
     ...
     1.14   run_wflow                       0:01:42  run the hydrological model
     1.14b  export_wflow_tables             0:00:03
     1.15   plot_wflow_evaluation           0:00:34
  >  1.15b  write_run_metadata
  >  1.16   gather_benchmarks
  >  1.17   gather_logs
```

Rows that will run carry a `>` gutter; rows already satisfied are ANSI-dimmed
AND lack the mark, so the distinction survives a pipe, a redirect and CI where
the dim does not. Times are what each rule took on the LAST run.

WF3's fan-out rules carry their count, which is the single biggest driver of
how long that workflow takes:

```
  >  3.12   perturb_climate_realization  x8    0:00:31 each
  >  3.14   downscale_climate_realization x10  0:01:04 each
```

## Where the data comes from -- no new bookkeeping

| field | source |
|---|---|
| number, name, summary | `workflow.rules`, each rule's `.message`, which IS `rule_banner()`'s output |
| will-run, fan-out count | Snakemake's `run_info` record (what `_run_info_line` already parses) |
| last-run duration | `benchmarks/wf<N>_benchmarks.md`, already keyed `1.14_run_wflow` |

The three keys agree already; none of them needs a new declaration beside a
rule.

**`RuleRegistry` is NOT the source.** It exists in `snake_utils.py` and no
Snakefile uses one -- WF3 still carries a hand-maintained `LOG_RULES` literal.
Adopting it across four entry points is a separate project and must not be
folded in here.

## Implementation sketch

Render inside `_ConsoleHandler` at `run_info`, not in `run_header`: only
`run_info` has the counts, and the handler is where the ANSI and fail-open
discipline already lives. Ordering is right -- the header prints from
`onstart`, `run_info` arrives after it.

`install_console_style()` grows an optional `workflow=` argument (it takes none
today, deliberately). That is a `shared/` signature change, so each of the four
Snakefiles changes one line in its `onstart:`.

## Traps, all confirmed in the current source

1. **`.message` is the UNFORMATTED template.** `rule_banner("2.04",
   "fetch_gcm_slice", "series {wildcards.series_key}", ...)` leaves a literal
   `{wildcards.series_key}` in the string. Strip the context bracket; never try
   to format it.
2. **Numbers are not unique.** WF0 builds `extract_historical_climate_{_source}`
   and `plot_climate_source_{_source}` in a Python loop, so several Rule
   objects share one number. Group by number.
3. **Sort is plain lexicographic.** `1.14`, `1.14b`, `1.15b` order correctly as
   strings; do not write a version parser.
4. **ASCII only.** A Windows console defaults to cp1252 and raises
   `UnicodeEncodeError` on typographic characters -- `rule_banner`'s docstring
   records this. No box-drawing, no arrows, no check marks: `>`, `--`, `x8`.
5. **Fail open.** A run must never die for a banner. Same discipline as
   `_run_info_line`, which returns Snakemake's own text when its parse yields
   nothing.
6. **No prior benchmark table** (a first run, or a new project) means no
   durations and no estimate. The column and the `est` clause disappear rather
   than printing zeros.

## Verification -- note the dry-run gap

`onstart:` does NOT fire on `--dry-run` (probed 2026-09-05: no header, no
restyle, and Snakemake's raw `Job stats:` prints twice). So
`pytest tests/test_cli.py`, which dry-runs all four entry points, **cannot see
this block at all**. The ladder here is:

- unit tests on the renderer, fed a fake `workflow.rules` and a `run_info`
  record -- this is where the traps above are pinned;
- `pixi run test-full`, because `shared/` and a signature change;
- one REAL rapid run per workflow, since that is the only thing that exercises
  the `onstart` path. WF0 is the one that matters most -- it is the only
  workflow with duplicate rule numbers.

## Progress

- [ ] Renderer + unit tests, including the WF0 duplicate-number case
- [ ] `install_console_style(workflow=...)` and the four `onstart:` call sites
- [ ] Benchmark-table lookup, degrading cleanly with no prior run
- [ ] `test-full`, then one real rapid run per workflow
