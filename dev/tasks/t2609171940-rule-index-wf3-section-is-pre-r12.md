---
title: rule-index.md's WF3 section is wholly pre-R12, and AGENTS.md sends rule authors to it
type: todo-item
status: backlog
effort: 1
area: docs / rule reference
origin: t2608290250 dead-module deletion, 2026-09-17
queue: 1
created: 2026-09-17
updated: 2026-09-17
---

> [!note] Overview
> **What** — `dev/reference/workflows/rule-index.md` lists WF3's rules under
> their pre-R12 numbering. Not one number matches `generate_scenarios.smk`, and
> several named rules no longer exist at all.
> **Why it matters** — AGENTS.md names this file as the thing to "read when
> editing or adding a rule", and `dev/reference/sealed-records.yml` cites it as
> the **current truth** two other records defer to. A reader following either
> pointer is misled.
> **Effort** — small; the fix is mechanical once someone decides how far to take it.

## Measured 2026-09-17 on `518fb4e2`

| rule-index says | `generate_scenarios.smk` actually has |
|---|---|
| 3.01 `check_project_consistency` | 3.01 `delineate_region` |
| 3.02 `snapshot_config` | 3.02 `extract_historical_climate` |
| 3.03 `delineate_region` | 3.03 `prepare_stress_test_grid` |
| 3.04 `delineate_spatial_units` | 3.04 `prepare_collection_sources` |
| 3.05 `write_model_reference` | 3.05 `initialize_scenario_collection` |
| 3.06 `check_model_reference` | 3.06 `prepare_weathergen_config` |
| 3.08 `extract_historical_climate` | 3.07 `generate_weather_realizations` |
| 3.09 `prepare_stress_test_grid` | 3.08 `perturb_climate_realization` |
| 3.11 `generate_weather_realizations` | 3.09 `retain_scenario_forcing` |
| 3.12 `perturb_climate_realization` | 3.10 `publish_scenario_collection` |
| 3.13 `write_climate_data_catalog` | 3.11 `gather_logs` |
| 3.14 `downscale_climate_realization` | 3.12 `gather_benchmarks` |

Rules the index lists that are **gone**: `check_project_consistency` (no `.smk`
references it — recorded in the `t2608131807` LOG row),
`write_climate_data_catalog` (retired with rule 3.13),
`write_experiment_config` (its module deleted 2026-09-17, `t2608290250` — that
row is already removed, which is how this was found).
`downscale_climate_realization` still exists but is **WF4 rule 4.04**, not WF3.

## Why it survived

Nothing tests a reference document against the rules it describes. The row for
`write_experiment_config` was only noticed because deleting the module required
grepping for its name — otherwise a stale table reads exactly like a current
one. `tests/test_sealed_records.py` freezes the *registry*; it does not check
that a current-truth document is still true.

## Options

1. **Regenerate the WF3 section from the `.smk` files.** The rule id and name
   are already in each `rule_banner(...)` call, so this is extractable rather
   than transcribable. Worth checking WF0/WF1/WF2/WF4 at the same time — nobody
   has verified those either, and this note only measured WF3.
2. **Hand-correct WF3 only.** Cheaper, and leaves the same trap set for the next
   renumbering.
3. **Add a test that the index matches the rules.** The durable fix: parse the
   `rule_banner` ids out of each `.smk` and assert the index agrees. Makes the
   next R-milestone renumbering fail loudly instead of silently rotting the doc.

Option 1 plus 3. The "historic id" column is genuinely historical and should be
preserved as-is; only the current column is wrong.

## Related

- [[t2608290250]] — the deletion that exposed it.
- [[t2608071213]] ("define one label constant per rule, so a rename is a
  one-line edit") is the adjacent idea: the ids are currently repeated as string
  literals in every rule, which is what makes a renumbering cheap to do and
  expensive to propagate.
