# Task Brief — P2 Workflow archives

### Context

Read `AGENTS.md`, [master brief](master-brief.md), [schema](../complete-run-output-schema.md) §§2, 4–5 and 10. P0 sets archive/reader versions; P1 supplies the archive/reference writer.

### Goal

Adopt the artifact-local `config/run_record.yml` plus `sources/` pattern for WF0–WF2 and the relevant entry points without changing their scientific products.

### Non-goals

No WF3/WF4 contract migration or baseline re-record.

### Allowed scope

Permitted: `analyze_climate.smk`, `build_model.smk`, `analyze_projections.smk`, their archive writers/readers and matching tests/docs. Re-measure all declared outputs and launcher consumers first. Forbidden: generated project outputs and Wflow-owned settings filenames.

### Required changes (checklist)

- [ ] Introduce the mandatory pre-parse capture launcher and exact archive writer for the affected workflows; raw Snakemake must refuse new-schema emission rather than claim bytes it did not capture.
- [ ] Update declared outputs, live readers, baseline/tree inventories and documentation in the same runnable contract change.
- [ ] Update current archive consumers, declared outputs and baseline/test inventory expectations to `run-record/2` in a coordinated runnable change; no old archive dispatch is required.
- [ ] At each workflow's commit boundary, report the archive version it emits and the readers updated. Flag any standing baseline tree that must be regenerated under the explicit P0 baseline plan.

### Commit plan

| Subject | Paths | Invariant |
|---|---|---|
| Adopt each workflow's archive contract | Its Snakefile, writer, readers, tests/docs | No committed producer points at an unupdated consumer. |

### Validation

Per workflow edit: matching tests and `pytest tests/test_cli.py`; a missing declared input or stale archive path falsifies the DAG claim. Dry-run each affected entry point with the rapid config. At master landing, use the shared/signature gates once. Compare product bytes or scientific summaries where the writer path could affect results.

### Acceptance criteria

New runs show resolvable local archives; dry-runs build and scientific output meaning is unchanged. Existing output trees remain untouched but are outside the new reader contract.

### Output requirements

Report each workflow's updated paths, tests/dry-runs, and any untested data-dependent path.

### Task constraints

Honor the master brief's human gate and shared constraints; no alteration of Wflow model settings.
