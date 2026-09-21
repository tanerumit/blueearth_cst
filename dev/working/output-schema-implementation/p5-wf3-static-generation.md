# Task Brief — P5 WF3 static generation

### Context

Read `AGENTS.md`, [master brief](master-brief.md), [schema](../complete-run-output-schema.md) §§2–3, 6 and the WF3 intake linked there. P3/P4 settle invocation and collection interfaces first.

### Goal

Freeze the WF3 plan before building the generation DAG and write temporary generator members directly as `run_<id>.nc`.

### Non-goals

No retention of intermediate netCDFs, numerical weather-generation change or new resume semantics.

### Allowed scope

Permitted: `generate_scenarios.smk`, `blueearth_cst/experiment/generation_plan.py`, `collection_resolution.py`, `scenario_provider.py`, `scenario_collection.py`, `blueearth_cst/weathergen/generate_weather.R`, the perturbation writer's path binding, and matching tests/docs. Re-measure all `rlz_*_st_*` path consumers before editing. Forbidden: upstream `weathergenr` package and generated outputs.

### Required changes (checklist)

- [ ] Replace checkpoint-driven generation expansion with the agreed frozen, content-derived plan and explicit plan pinning.
- [ ] Make the R root writer write `run_<id>.nc` directly, not via a legacy-name write followed by rename. Align Snakemake `temp()` outputs, provider ancestor/member paths and perturbation output arguments to the same run IDs.
- [ ] Keep `weathergenr/output/` date-selection CSVs and `evaluation/plots/` diagnostics accounted for, while generator netCDFs remain temporary.
- [ ] Keep exact `weather_generation_input.yml` and creator `config/run_record.yml`/`sources/` references consistent.

### Commit plan

| Subject | Paths | Invariant |
|---|---|---|
| Switch generator member naming | R writer, Snakefile, provider, tests/docs | Declared outputs and actual R/perturbation paths agree atomically. |
| Freeze static generation plan | Plan, rule expansion, readers, tests/docs | A job always executes the plan digest it selected. |

### Validation

Per edit: focused provider and rule tests; parse touched R scripts, run `pytest tests/test_cli.py` for rule changes, and Python lint/format. A cold dry-run scheduling science, a live pointer replacing a frozen plan, or any `rlz_*_st_*.nc` member written by new WF3 falsifies the contract. Run an isolated rapid WF3 smoke check once after the phase; compare generated series scientifically against an agreed reference, not by filename alone.

### Acceptance criteria

Root and perturbed intermediates use `run_<id>.nc` directly and remain `temp()`; frozen plans control the DAG; retained `series/` is complete and verified.

### Output requirements

Report DAG and filesystem observations, R parse/test results, naming search, and numerical comparison or its explicit absence.

### Task constraints

Honor the master brief's human gate and shared constraints. Do not hand-edit weathergenr internals or preserve intermediates by accident.
