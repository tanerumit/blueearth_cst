# WF3 generation bundle — implementation plan

Bundle: origin `wf3 generation bundle (2026-09-24)`, branch `wf3-improvements`.
Items: `t2609241323` (3.09 copy step), `t2609241251` (rule renames),
`t2609241329` (overview rows 3.04–3.06 + rule-index), `t2609171940`
(rule-index pre-R12; folded into `t2609241329`), and the remainder of
`t2609191457` (static planning; the plan freeze landed in `c83ead70`).

## Dependencies and open decisions

- **Session-1 draft schema.** `refactor/wf3-static-planning` carries
  `dev/working/complete-run-output-schema.md` (docs only, unmerged). It keeps
  generator netCDFs `temp()` under `weathergenr/output/run_<id>.nc` and a
  separately retained `series/run_<id>.nc` "with different lifetimes". Step 1
  contradicts that: decide it with the schema, not against it.
- **Identity.** The plan's code inventory hashes `scenario_provider.py`,
  `generation_plan.py`, `prepare_*.py` and the `weathergen/*.R` scripts, not
  `generate_scenarios.smk`. A Snakefile-only rename keeps `collection_id`;
  step 1 (R/provider edits) yields a new collection by design. Verify both by
  re-planning `gabon-ntoum-v2` (`reuse_ready` expected after step 2 alone).
- **3.06 `prepare_weathergen_config`** runs in planning/initialization
  (`generation_plan.py` imports `build_weathergen_config`); confirm the exact
  call site before labelling the overview row.

## Order

Copy step first: whether 3.09 survives decides whether `store_` enters the
`naming.md` §8b verb table (no verb without a rule).

| Step | Commit | Lands | Est. |
|---|---|---|---|
| 1 | `refactor(wf3): write scenario series directly` | 3.07/3.08 write `series/run_<id>.nc`; roots stay non-temp (they are 3.08 ancestors); 3.09 removed; receipt `workspace_path` and `validate_provider_inputs(output_dir=…)` adjusted; tests | 3–4 h |
| 2 | `refactor(wf3): domain rule names` | 3.03 `prepare_perturbation_grid`, 3.07 `generate_weather_realizations`, 3.08 `perturb_climate_realizations`, 3.10 `publish_scenario_collection` (+3.09 `store_scenario_series` only if step 1 is rejected); `LOG_RULES`, banners, `tests/test_prepare_weathergen_config.py`, `dev/scripts/console_sample_specs.py`, `dev/reference/contracts/weather-generator-seam.md`, §8b verb table (`publish_`) and the singular `perturb_climate_realization` mention; migration note | 1–1.5 h |
| 3 | `feat(console): show WF3 pre-DAG steps` | Overview rows 3.04–3.06 in `shared/console_style.py` / WF3 banner, labelled as run before the DAG; on `--dry-run` they must not claim done. Remove the provisional `after checkpoint` state (check WF0–WF2/WF4 use first), add the migration note, prove exact counts for fresh and reuse runs; closes `t2609191457` | 2.5–3 h |
| 4 | `docs(rule-index): WF3 table matches code` | `rule-index.md` WF3 section; closes `t2609171940` | 30 min |

Sealed records (`dev/milestones/`, `dev/working/` design runs) are not swept;
check `dev/reference/sealed-records.yml` before touching any `dev/` file.

## Validation

| Step | Check |
|---|---|
| 1 | Focused provider/publication tests; `pytest tests/test_cli.py`; WF3 rapid run; series bytes/statistics equal to a pre-change run of the same plan seed; no `weathergenr/output/run_*.nc` left behind |
| 2 | `pytest tests/test_cli.py`; WF3 `--dry-run`; grep old names returns only sealed records; re-plan decision `reuse_ready` |
| 3 | Console tests for `console_style`; render the WF3 overview (real and dry-run) and inspect |
| 4 | none beyond review |
| Merge | `pixi run test-full` (step 3 touches `shared/`); PR per AGENTS.md for `shared/` changes |

Total: about 8–9 h of work, plus one rapid WF3 run and one `test-full`.
