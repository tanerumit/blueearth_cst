# Task Brief — P5 WF3 static generation

### Context

Read `AGENTS.md`, [master brief](master-brief.md), [schema](../complete-run-output-schema.md) §§2–3, 6 and the WF3 intake linked there. P3/P4 settle invocation and collection interfaces first.

### Goal

Freeze the WF3 plan before building the generation DAG, make the coordinated default producer switch to P4's collection contract, and write temporary generator members directly as `run_<id>.nc`.

### Non-goals

No retention of intermediate netCDFs, numerical weather-generation change or new resume semantics.

### Allowed scope

Permitted: `generate_scenarios.smk`, `blueearth_cst/experiment/generation_plan.py`, `collection_resolution.py`, `scenario_provider.py`, `scenario_collection.py`, `blueearth_cst/weathergen/generate_weather.R`, the perturbation writer's path binding, and matching tests/docs. Re-measure all `rlz_*_st_*` path consumers before editing. Forbidden: upstream `weathergenr` package and generated outputs.

### Required changes (checklist)

- [ ] Replace checkpoint-driven generation expansion with the agreed frozen, content-derived plan and explicit plan pinning. Validate the selected digest at execution time; a mutable discovery pointer cannot redirect a pinned job.
- [ ] Switch all WF3 declarations, producers, publication paths and WF3 consumers to P4's new contract together. Emit the accepted creator `config/run_record.yml` and byte-preserved `sources/`; bind its exact generated-input checksum. Preserve the creator archive on ready reuse, and test missing originals and interrupted publication. P6 owns WF4 consumption; until then WF4 must refuse the new collection clearly rather than misread it.
- [ ] Make the R root writer write `run_<id>.nc` directly, not via a legacy-name write followed by rename. Align Snakemake `temp()` outputs, provider ancestor/member paths and perturbation output arguments to the same run IDs.
- [ ] Keep `weathergenr/output/` date-selection CSVs and `evaluation/plots/` diagnostics accounted for, while generator netCDFs remain temporary.
- [ ] Keep exact `weather_generation_input.yml` and creator `config/run_record.yml`/`sources/` references consistent. Verify installed YAML semantics and actual provider arguments against the frozen plan, including negative tests where YAML and arguments are mutually consistent but differ from the pin.

### Commit plan

| Subject | Paths | Invariant |
|---|---|---|
| Switch generator member naming | R writer, Snakefile, provider, tests/docs | Declared outputs and actual R/perturbation paths agree atomically. |
| Freeze static generation plan and adopt collection producer | Plan, rule expansion, creator archive, publication, WF3 readers, tests/docs | A job always executes the plan digest it selected; all WF3 paths use one schema version and pre-P6 WF4 refuses that version explicitly. |

### Validation

Per edit: focused provider and rule tests; parse touched R scripts, run `pytest tests/test_cli.py` for rule changes, and Python lint/format. A cold dry-run executing preparation or generation, a live pointer replacing a frozen plan, or any `rlz_*_st_*.nc` member written by new WF3 falsifies the contract. Inspect fresh/prepared/reuse DAGs with explicit targets and force/rerun flags. Exercise stale inputs even with preserved mtimes, competing initialization, failure before/after receipt, and failed-job cleanup without loss of ready bytes. Execute every admitted mutation case in §10.6's exclusion matrix, including repeated parallel/core cases; promote scientifically relevant fields or refuse unsupported modes. Run an isolated rapid WF3 R/provider smoke once after the phase; compare decoded series, dates, member associations and masks exactly against P0's matched explicit-123 reference. Model-validator must return acceptance before P7 integrates the result. Check that auto seeds follow the accepted WF3-only formula and recorded inputs; numeric parity with v1 is not an acceptance criterion.

### Acceptance criteria

Root and perturbed intermediates use `run_<id>.nc` directly and remain `temp()`; frozen plans control the DAG; retained `series/` is complete and verified.

### Output requirements

Report DAG and filesystem observations, R parse/test results, naming search, and numerical comparison or its explicit absence.

### Task constraints

Honor the master brief's human gate and shared constraints. Do not hand-edit weathergenr internals or preserve intermediates by accident.
