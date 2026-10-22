# Historical Qcrit and temperature output verification

Implementation: `4ff35de7` (task t2610221645), 2026-10-22. This record retains the numerical,
interface and case decisions needed after task closure. Current contracts live in the crop-water
set README, indicator glossary and published WF1/WF4 references.

## Decisions and limits

Qcrit defaults to linear Q90 exceedance (non-exceedance p=0.10) from complete May–October historical
periods. Rules also support annual calendar-year references, alternate quantiles and explicit
exceedance/nonexceedance semantics. Resolved values, source CSV/TOML digests, requested years,
periods, sample counts and coverage enter calculation identity. Operational thresholds remain valid.

The user selected complete calendar years for the Gabon candidate's 1995–2005 historical model
reference. The low-flow indicator still counts May–October days; no Gabon crop calendar was qualified.
Inspect excluded years before use, especially the first interval-end model year. Synthetic observations
and scenario discharge are not used for threshold preparation.

The external Gabon case has three labelled candidate files: `project_config_candidate.yml`,
`project_config_simulate_system_candidate.yml` and `crop-water-candidate.yml`, under
`cst-cases:applications/gabon-ntoum-v2-rapid/`. They preserve the original five outvars and append
temperature, using a separate candidate output root. Active case configs were preserved. Composition
passed; candidate historical output was absent, so no Gabon DAG or production execution was attempted.

## Software and numerical evidence

Environment: session-3 Pixi default, Python 3.12.13; repository-managed Julia/Wflow Project/Manifest.
No environment or lockfile changes. The affected integration check is:

```powershell
pixi run pytest tests/test_crop_water.py tests/test_baseline_qcrit.py tests/test_temperature_outputs.py tests/test_indicator_glossary.py tests/test_indicator_tables.py tests/test_indicator_sets.py tests/test_indicator_registry.py tests/test_setup_gauges_and_outputs.py tests/test_wflow_response_reader.py tests/test_crop_water_integration.py tests/test_partial_indicators.py tests/test_func_plot_signature.py tests/test_wf1_plot_outputs.py tests/test_indicators_module.py tests/test_indicators_definition.py -q
```

Before landing, 288 distinct affected checks passed across the integrated run and focused reruns.
The initial integrated run passed 249 checks and exposed one stale registry-count assertion; its
updated test passed separately. Additional independent-module checks and the temperature sum refusal
passed 38 checks. The strengthened WF1 temperature plot declaration check passed both variants.
Scoped Ruff, formatting (16 Python files), compilation and whitespace checks passed.

Coverage includes equivalent Q80 conventions, independent quantile/method expected values,
incomplete annual and seasonal periods, invalid settings, fixed thresholds across scenarios,
provenance changes, native temperature mapping/units, state reductions, retained inventory,
indicator publication, WF4 CLI execution/dry-run and WF1 output declaration contracts.

Restricted Windows CLI checks stalled in Snakemake source-cache `tempfile.mkdtemp`; py-spy and an
ordinary-versus-private directory probe identified the restricted-token issue. Only task-owned stalled
test processes were stopped. Workflow checks passed with normal cache access under elevated execution;
no package or cache-permission patch was applied.

## Engine and visual evidence

An isolated two-day Wflow execution read this lane's existing test_local model and emitted finite
temperature at four locations in degrees Celsius. Source model and historical output were preserved.
This qualifies the output binding, not basin model accuracy or a new numerical baseline.

Controlled seasonal-series annual and monthly PNG previews were generated and inspected: means and
degree-Celsius labels, negative values preserved, no clipping. No figure layout or style was changed.
The task-owned smoke script, input TOML, engine log and previews remain in lane-local
`.tmp/tasks/t2610221645/temperature-smoke/`; retain until integration evidence no longer needs them.
The regenerating script is `.tmp/tasks/t2610221645/temperature_smoke.py` in that lane.

Landing runs the affected check above on the synchronized candidate. Its JUnit report is retained at
`.tmp/tasks/t2610221645/landing-tests.xml` in the retained session worktree. The landing procedure
verifies committed-tree equivalence and candidate ancestry before parking that worktree.
