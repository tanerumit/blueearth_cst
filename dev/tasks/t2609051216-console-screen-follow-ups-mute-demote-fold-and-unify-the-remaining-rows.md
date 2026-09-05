---
title: "Console screen follow-ups: mute, demote, fold and unify the remaining rows"
type: todo-item
status: backlog
effort: 1
area: console / logging
origin: console screen 2026-09-05
queue:
created: 2026-09-05
updated: 2026-09-05
---

> [!note] Overview
> **What** — Twelve console-message improvements found by screening fresh WF1/WF2/WF3 console captures against the merged logs, after fruits 1-3 and 6 of that screen landed in f121e870 and cfadee4c.
> **Why** — The recent console work (short sentences, colour, muted repeats) left a set of small, independent items that each cost a row or a grammar clash on every run; none needs design.
> **Effort** — small

## Where it came from

A screen of the three workflows' console output on 2026-09-05, run as a
`--forceall` rapid pass of WF1, WF3 and WF2 with the console captured to
`.tmp/scratchpad/2026-09-05_1139/wf{1,2,3}.console` (session-1 worktree,
deletable) and read against the merged logs under `test_case/test_rapid/logs/`.
Four of its findings landed the same day (`f121e870`: counter on the banner
line, `[series ...]` on both lines of a WF2 job, no full stop after a hydromt
path; `cfadee4c`: the `output//` double slash on every weathergenr path row).
This item holds the rest. Every item is independent; land them in any order,
one commit each or a few per commit.

## Items

Ranked by rows saved per run, then by how visible the clash is.

1. **Mute hydromt's `-vv` chatter in rule 1.10.** `log - HydroMT version:
   1.3.1` prints three times, then `model - update: setup_*` and the
   `model - setup_*.param=value` dump (~20 rows). Add `("log", "HydroMT
   version")`, `("model", "update: ")` and `("model", "setup_")` to
   `_TEE_CONSOLE_MUTED` (`shared/snake_utils.py`); the log part keeps them.
   The `-vv` itself stays -- it is what puts the rows in the log.

2. **Demote two benign hydromt WARNINGs.** `forcing - WARNING - Write forcing
   skipped: dataset is empty` (1.07, 1.08, 1.09) and `states - WARNING - CRS
   not found in states data` (1.07-1.10) are the only yellow on a clean WF1
   build, and neither says anything a reader can act on. The mute table refuses
   warnings by design (`_muted_on_console`), so this is a NEW, explicit,
   enumerated demotion list: painted as body on the console, text unchanged in
   the log. Keep it to these two rows.

3. **Heartbeat rows in the row grammar.** `   ... 2.04_fetch_gcm_slice/<key>:
   still running, 2m00s elapsed` and `... done in 3m44s` (`_Heartbeat`,
   `snake_utils.py:2275`) have no stamp and no module column, name the rule by
   its log label, and use a fourth duration format (`_fmt_elapsed`). Render
   through `_log_row_text` under a `heartbeat` module, name the rule as
   `rule_id(number) name  [context]`, and format with `format_elapsed` so the
   `done in` row and the DONE line under it agree.

4. **One duration format.** DONE lines `0:03:46` (`format_elapsed`), bars
   `3:44 elapsed` (`progress.format_duration`), Julia `120.7 s`
   (`run_wflow.jl:48`, `run_wflow_batch.jl:66`), heartbeat `3m44s`. Pick
   `format_elapsed`'s `h:mm:ss` (it matches the benchmark tables) and route the
   Julia rows and the bar through it; delete `_fmt_elapsed`.

5. **WF2 `stats` rows repeat the 40-char series key four times in four lines**
   (RUN line, `reducing <file>`, `writing series to <file>`, bar label). One row
   `reducing -> series` and a bar labelled `series`
   — **landed with one deviation**: the bar keeps a short `<model> <scenario>`
   identity rather than a bare `series`. The code's own comment says the label
   is what separates reduce jobs interleaving under `-c 3`, which the screen
   did not have in view; the key still drops from four appearances to two
   (`projections/get_stats_climate_proj.py:335,454`).

6. **WF3 per-member weathergen rows without a member.** `Reading realization:`
   and `Saving perturbed netcdf to:` print as identical pairs under `-c 3`; the
   `io - NetCDF written:` row that follows already names the file. Drop the
   `Saving` row, add the member to `Reading`
   (`weathergen/impose_climate_change.R:34,178`).

7. **`plot_wflow_evaluation` splits its figure bundle.** `Plot evaluation
   figures for wflow_id N` before each station forces a `4 figures ->
   stations` flush per station; announce once and get one `16 figures` row.
   Same rule: `Plot basin average wflow outputs` is the only imperative-mood
   row on the console (`model/plot_results.py:353,422`).

8. **Figures announced three ways.** WF0/WF1 use the `save_figure` bundle;
   WF2 prints one `Wrote <file> (N traces per panel)` row per figure
   (`projections/plot_proj_timeseries.py:232,245`) and 2.06 writes its PNG
   under module `change` (`get_change_climate_proj_summary.py:169,181`); WF1's
   1.05 and 1.13 print the bundle rows AND a `Wrote 33 canonical climate
   figures (...)` row that restates them (`climate_analysis/climate_figures.py:993`).
   Route WF2 through `save_figure`, drop the restating row.
   — **landed, and the per-figure counts go with it**: `(N traces per panel)`
   and `(N points)` are no longer printed anywhere. They are recoverable from
   `composition.csv` and the `deriving change factors for N point(s) x N
   horizon(s)` row, both written by the same rules. The figures themselves are
   byte-identical — `save_figure` forwards the same `fig` and `dpi` the direct
   `savefig` calls used — so the figure-revision gate does not apply.

9. **Collapse the `Job stats:` table.** 22 lines on WF1 where every count is 1.
   Snakemake sends it as event `run_info`, so `_ConsoleHandler._render` can
   print one line (`20 jobs, 20 rules`) and show the table only when some
   count exceeds 1 (WF3).

10. **Silent rules.** 1.14b `export_wflow_tables` (`shared/tidy_wflow_table.py`)
    and 3.09 `prepare_stress_test_grid` write outputs and emit nothing, leaving
    empty sections in the merged log. One `wrote <path> (N rows)` row each, in
    3.16's grammar.

11. **Sentence case.** WF0/WF1 rows open capitalised (`Wrote region`), WF2/WF3
    Python rows open lowercase (`deriving`, `reducing`, `wrote`); counted
    2026-09-05: projections 19 lowercase vs 6 upper, experiment 6 vs 2, all other
    folders capitalised. Pick one (capitalised is the majority and what hydromt
    and the R rows do) and sweep. Cosmetic; last.

12. **`log_row` never flushes.** Off a terminal (CI, a redirect) a rule's rows
    arrive after its DONE line. A `sys.stdout.flush()` after the write.

## Not this item

- **Upstream weathergenr v2.0.0**, not this repo: `eval - Generated
  {format(length(plots): {out_dir}, big.mark = ',')} diagnostic plots.` is an
  unevaluated glue template (`evaluate_generator.R`); the FIT ASSESSMENT SUMMARY
  block is raw `cat()` with no stamp or module; `Template loaded:` and the
  170-char `NetCDF written: ... | vars=... | dims=... | grids=20` row print once
  per member (400 rows on a 10 x 20 grid). Needs a version bump; the local
  `~/workspace/weathergenr` checkout is a `wip` that differs from the installed tag.
- **Message semantics**: `short reference window: 14 years (2000-2014)` counts
  `end - start` (`projections/reference_window.py:102`), so the label reads as
  15 years; and 3.05 prints `models/hydrology/wflow` untokenised where the
  header promises `<model>`. Both are one-line clarifications, but they are
  about what the row CLAIMS, so decide them on their own.
- The `Writing geoms to` block appearing three times per WF1 build is
  `t2609041718` (a watch-item, ruled worth keeping).

## Progress

- [x] Items 1, 2, 9, 12 (console handler and tee -- one commit)
- [x] Items 3, 4 (durations and the heartbeat -- one commit)
- [x] Items 5, 6, 7, 8, 10 (per-rule rows)
- [ ] Item 11 (case sweep), last
