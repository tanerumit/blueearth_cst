# Migration — named WF4 indicator sets and metric-set/4

`dev/reference/naming.md` §7 record for the named-indicator-sets work, boarded as
[`t2610161523`](../../../tasks/t2610161523-integrate-multiple-metric-sets.md). Contract source: the sealed
design v3 under that task's `design-runs/named-indicator-sets/`. Filed under `post-r12/` for the reason
given in `migration_scenario-tree.md`: this is follow-up work, not a milestone.

## Event 1 — WF4 operation selection

| old (legacy, accepted for one feature release) | new |
|---|---|
| `operation: simulate-and-metrics` + `--target all` | `operations: [simulations, indicators]`, `indicator_sets: [default]` |
| `operation: simulate-and-metrics` + `--target simulations_only` (alias `responses`) | `operations: [simulations]` |
| `operation: metrics-only` + `--target simulations_and_indicators` (alias `metrics`) | `operations: [indicators]`, `indicator_sets: [default]` |
| `metrics: [q, gwr]` token filter | a custom set selecting registered definitions |

The named interface infers its target; an explicit `--target` is refused. Legacy mode keeps its explicit
target rules and its observed `metrics`/`model.outvars` precedence per branch (null and empty values
behave as before, including refusals). New and legacy keys cannot be mixed. Nothing rewrites a config
automatically. Removing the legacy keys needs an explicit follow-up decision and a
`RETIRED_EXPERIMENT_KEYS`-style registration at that time. Set selection is analysis intent: it never
enters simulation identity.

## Event 2 — metric records: /3 to /4

| record | old | new |
|---|---|---|
| request | `metric-request/3` (tokens) | `metric-request/4` (canonically sorted calculation records: metric key, method, parameters, registered calculation) |
| identity | `metric-set-identity/3` | `metric-set-identity/4` |
| marker | `metric-set/3` | `metric-set/4`, adding `calculations` and `coverage_evidence` |

New writes use /4 with new identities; /3 sets remain readable with their original validator, including
legacy `results/metric_sets/<digest>/` result roots. A /4 set always keeps its data under
`_engine/metric_sets/<id>/data/`. No old manifest is rewritten and no old identity is aliased.
The known-stale baseline is not regenerated to disguise this migration; `check_baseline` reads /3 and /4.

## Event 3 — readable exports: flat to named

| old | new |
|---|---|
| `results/metric_sets/*.csv` | `results/metric_sets/<set-id>/` (tables, lookups, `indicators.csv`) |
| `_engine/metric_sets/current.json` (`metric-export/1`) | `_engine/metric_sets/names/<set-id>/current.json` (`named-metric-current/1`) with immutable `publications/<id>.json` (`named-metric-export/1`) and captured `definitions/<sha256>.yml` |

Legacy mode publishes the named `default` export too; the flat export is no longer refreshed. An existing
flat export and its pointer are reported once per run and preserved byte for byte; delete them only by a
separate, explicit cleanup. A set id that collides with a legacy result root or an unowned folder is
refused with contents preserved.

## Event 4 — annual-total units

`aet_annual_total`, `gwr_annual_total` and `precip_annual_total` keep their names and arithmetic. Their
unit is now stated as **mm** (mean water-year block depth); the 2026-08-08 mm/yr reading holds only for
complete, nonmissing water-year blocks. `indicators.csv` reports each set's block coverage so a reader can
tell. No value changes.

## Consumers updated in the same change

Both runners and their help, the WF4 Snakefiles, `config/templates/` (WF4 template and the new
`indicator_set.template.yml`), the four `test_case/project_config_*_simulate_system.yml` seeds, HM-7,
`check_baseline`, `semantic_tree_diff`, `create_case`, the WF4 reference, outputs, quick-start, running and
retained-handoff pages, `dev/reference/repo-layout.md` and `indicator-glossary.md`.
