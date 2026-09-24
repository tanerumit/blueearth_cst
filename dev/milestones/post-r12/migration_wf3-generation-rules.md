# Migration: WF3 generation rule names (2026-09-24)

WF3 generation bundle, board items `t2609241251` and `t2609241323`. Rule
numbers are unchanged; 3.09 is removed, not renumbered.

| # | Old | New |
|---|---|---|
| 3.03 | `prepare_stress_test_grid` | `prepare_perturbation_grid` |
| 3.07 | `generate_roots_v2` | `generate_weather_realizations` |
| 3.08 | `transform_member_v2` | `perturb_climate_realizations` |
| 3.09 | `retain_series_v2` | removed: 3.07/3.08 write `series/run_<id>.nc` directly |
| 3.10 | `publish_collection_v2` | `publish_scenario_collection` |

`publish_` joins the `naming.md` §8b verb table. No `store_` verb is added,
since no rule copies series any more.

## What changes for a user

- CLI targets: `--forcerun`, `--until` and similar flags take the new names.
- Log and benchmark part files are named after the rule, for example
  `logs/_parts/generate_scenarios/<plan>/3.07_generate_weather_realizations.log`.
  Files from earlier runs keep their old names.
- Collection identity is unaffected: the Snakefile is not part of the
  generation code inventory, so an existing ready collection is still reused.

## Updated references

`generate_scenarios.smk`, `tests/test_prepare_weathergen_config.py`,
`tests/test_project_tree_inventory.py`, `dev/scripts/console_sample_specs.py`,
`dev/reference/contracts/weather-generator-seam.md`, `dev/reference/naming.md`.
`dev/reference/workflows/rule-index.md` is corrected separately (`t2609241329`).
Sealed milestone and design records keep the names they were written with.
