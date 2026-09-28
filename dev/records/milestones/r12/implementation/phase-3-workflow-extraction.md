# Task Brief — P3 reference-atomic workflow extraction

**P3 migration accepted, 2026-09-12.** [Acceptance and evidence](evidence/p3/acceptance.md). GF15 benchmark adequacy and milestone sealing remain separate owner-gated work.

### Context

- Follow repository `AGENTS.md`, [master brief](master-brief.md), and accepted §§4.2 landing 3, 9, 11–13.
- P1/P2 and all pre-extraction blockers are integrated. Current WF3 is now only a comparison/migration carrier.
- This landing changes public commands, config names, output paths, workflow count, runner order, and live references atomically.

### Goal

Extract `wf3 generate_scenarios` and `wf4 simulate_system`, migrate configuration/runner/output tooling and every live reference, prove the old/new numerical crosswalk, then retire `run_stress_test.smk` and `workflows.run_stress_test` in the same landing.

### Non-goals

No compatibility wrapper, in-place output rename, third metrics workflow, provider/plugin expansion, projection dependency, baseline re-record before GF-9 acceptance, or edit to sealed historical records.

### Allowed scope

**Proposed paths:** root `generate_scenarios.smk`, `simulate_system.smk`; mandatory runner `scripts/simulate_system.py` and its two fixed rule modules; `config/templates/project_config.generate_scenarios.template.yml`, `project_config.simulate_system.template.yml`; per-seed `project_config_<seed>_generate_scenarios.yml` and `project_config_<seed>_simulate_system.yml`; GF-9 crosswalk tool/test; successor ADR at `dev/decisions/<NEXT_ADR_NUMBER>-<APPROVED_SLUG>.md`.

**Exact workflow/config/runner targets:** `run_stress_test.smk` (retire); `scripts/run_workflows.py`, `plot_workflow_dag.py`, `run_snake_docker.sh`, `run_snake_test.cmd`, `suggest_experiment_name.py`, `migrate_project_config.py`; `blueearth_cst/shared/config_composition.py`, `cross_workflow_leaves.py`; `pixi.toml`; `config/templates/project_config.template.yml`, `project_config.run_stress_test.template.yml`; current project config sets under `test_case/` for `rapid`, `baseline`, `baseline_linux`, `wf2_fast`; matching current `tests/project_config_fixture*.yml` and `tests/data/v2/project_config_v2_probe*.yml`. Legacy `tests/data/v1_split/` inputs retain their deliberate old shapes; update only migration/refusal expectations that consume them.

**Exact live reference targets from §9.6/current search:** `README.md`, `AGENTS.md`; `docs/migration-workflow-names.md`, `migration-config-shape.md`, `guide/configuration.qmd`, `guide/outputs.qmd`, `guide/quick-start.qmd`, `guide/running.qmd`, `notebooks/Climate Stress Test.ipynb`, `notebooks/README.md`; `dev/reference/workflows/rule-index.md`, `model_creation.md`, `wf3-stage-flow.svg`, `wf3-stage-flow.html`; `dev/reference/contracts/weather-generator-seam.md`, `hydrological-model-seam.md`; `dev/reference/naming.md`, `indicator-glossary.md`; `dev/decisions/index.md`; `blueearth_cst/shared/surface_axes.py`; baseline/tree tooling `dev/scripts/check_baseline.py`, `snapshot_project_tree.py`, `semantic_tree_diff.py`; live `dev/baseline/indicator_ref/74ed83c06b2e7e6c.csv` only after GF-9 acceptance.

**Forbidden historical evidence:** `dev/reference/workflows/climate_experiment.md`, sealed decision bodies, `dev/milestones/r12/premigration/`, `dev/milestones/r12/migration_stress-test-lookup.md`, and review/probe records remain verbatim. Supersession occurs through the new ADR/index and maintained-current references, never by rewriting history.

**Exact affected test families:** `tests/test_cli.py`, `test_config_composition.py`, `test_run_workflows.py`, `test_cross_workflow_inputs.py`, `test_project_tree_inventory.py`, `test_snapshot_project_tree.py`, `test_plot_workflow_dag.py`, `test_migrate_project_config.py`, `test_suggest_experiment_name.py`, `test_indicator_glossary.py`, `test_interchange_contracts.py`, `test_surface_axes.py`, `test_check_baseline_*.py`, and all files returned by re-running the old-spelling search in §9.6. Historical milestone/probe files remain excluded.

### Required changes (checklist)

- [x] Add the two selected Snakefiles and assign ids/rule prefixes `wf3/3.xx` and `wf4/4.xx`; generation has no model edge, simulation cannot produce a collection, and metrics remain an operation/target inside simulation.
- [x] Split every project file into five closed stanzas and workflow-owned files. Preserve ordinary-path resolution and `project_config_` prefix. Migrate old explicit/default/auto seeds to their old resolved integer; new `auto` uses the acyclic accepted projection.
- [x] Update runner order to `analyze_climate → generate_scenarios → build_model → simulate_system → analyze_projections`, with workflow-local preflights after relevant producers. The dedicated mandatory simulation runner shares target validation with the all-workflow runner; direct generation remains supported. Bare simulation Snakefile invocation no longer carries the target contract (owner-approved P0 Gate 3 ruling).
- [x] Replace fixed cross-workflow leaves by consumer/operation; preserve independent generation, model leaves for simulate mode, and retained-only leaves for metrics-only.
- [x] Replace all nine WG/HM clauses and live validators per §9.2; update output inventory for `scenario_plans/`, collection preparation artifacts, `results/metric_plans/`, simulation/response manifests, and metric sets.
- [x] Update every live §9.6 reference and executable example in one landing. Preserve C24/C25/C28 and all other sealed/historical files verbatim; add the successor ADR and maintained-current index/references required by repository rules.
- [x] Refuse old stanza/commands/keys with migration text. Do not leave half-renamed trees or an indefinite wrapper.
- [x] Implement and run GF-9 against separate fresh same-config pre/post roots. Record deterministic old `(rlz,st_id)`→`run_id` and pooled-sentinel→bundle mappings, two-way row coverage, Class-A/B tolerance, Class-C mean relation, two opposite-season gauges, and order-reversal invariance.
- [x] Only after GF-9 acceptance, update standing baseline ownership/targets if the milestone plan calls for it; record all justified drift. Never use the stale standing tree as GF-9's old side.

### Commit plan

| Subject | Paths | Invariant preserved |
|---|---|---|
| `feat!: split WF3 scenario generation and system simulation` | every permitted P3 path, including additions, all live rewrites, and old entry-point/template retirement | no commit exposes half-renamed entry points, stanzas, commands, references, output inventory, or contract names |

GF-9 evidence may be committed immediately before this atomic landing only if it references immutable pre/post run provenance and does not alter runtime. The landing itself remains one reference-atomic commit.

### Validation

- Per edit before squashing/landing: affected config/runner/reference tests; Python lint/format.
- After every Snakefile/config-shape edit: `pixi run pytest tests/test_cli.py`.
- Once on the final atomic tree: `pixi run pytest tests/test_config_composition.py tests/test_run_workflows.py tests/test_cross_workflow_inputs.py tests/test_project_tree_inventory.py tests/test_plot_workflow_dag.py` plus all P1/P2 successor tests.
- Once per entry point/mode: fresh direct dry-run and real rapid execution; final successor-entry-point and migrated-runner repetitions for GF-25/GF-29/GF-30/GF-32. After the complete rapid run, use the helper's required config and root together: `pixi run python dev/scripts/snapshot_project_tree.py --config <POSTCHANGE_CONFIG> --project-dir <POSTCHANGE_ROOT>`.
- Once under the accepted criteria, with Astra model validation of results: GF-9, GF-27, GF-28, and GF-31 comparisons. GF-15's proposed benchmark remains separately gated. Any unexplained Class-A/B change, Class-C mean mismatch, reference-order change, duplicate/lost row, seed/calendar drift, or preparation-value drift fails the landing.
- Once before merge: `pixi run test-full *> dev/milestones/r12/implementation/evidence/final/test-full.log`; before milestone seal, standing baseline/tree gates under current documented limitations.

### Acceptance criteria

Five stanzas compose; direct generation, the dedicated simulation runner and the all-workflow runner each honor the one-invocation contract; generation is model-independent; simulation cannot generate; metrics-only cannot simulate; projections remain terminal; all live old references refuse or are migrated; GF-1..GF-32 and signed stage handoffs pass; the old entry point/stanza/template are absent.

### Output requirements

Return the atomic diff, migration note/ADR, old/new path and id crosswalk, command logs, numerical delta record, live-spelling sweep, tree inventory, and signed stage-1/2/3 model-validator acceptance records under `dev/milestones/r12/implementation/evidence/p3/`.

### Task constraints

Use Astra for scientific/methodological evaluations. A failed accepted mechanism or unexplained numerical change triggers Master Gate 3; it does not authorize a hidden compatibility path, tolerance change, optimizer retuning, or scientific repair.
