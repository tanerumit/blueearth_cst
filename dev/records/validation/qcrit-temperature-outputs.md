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

## Retained simulation compatibility audit

Task t2610221807 audited `76a2a874` against `90e8211a` before updating the compatibility pin.
The complete normalized inventory contains 22 sources. Only
`blueearth_cst/experiment/wflow_response_reader.py` changed, in `f6841501`: it adds
`temp -> (temp, atmosphere_air__temperature, degC)` and extends the PET subcatchment-mean
declaration guard to temperature. The PET error text is unchanged after interpolation.
All seven existing mappings, extraction, ordering, missing-value handling, time support,
units and response validation are unchanged. No numerical producer changed within this boundary.

The planner iterates the same mapping: without temperature declarations its output is unchanged;
previously unsupported temperature headers can now be planned. This does not authorize adding
outputs to an existing model. `model_file_set` includes the complete model TOML, and
`check_completed_simulation_inputs` freshly compares that model reference before applying the
source bridge. Full planning also hashes the response request independently. Adding a temperature
declaration therefore requires a new experiment; the source bridge substitutes only the code
digest for the final simulation identity comparison.

Accepted directed inventory pairs are the original pre-boundary inventory (`69dcf9de…`) to
the pre-temperature inventory (`fe2e4d92…`) or current inventory (`12c02734…`), plus
pre-temperature to current. Full digests remain in `simulation_reuse.py`. The old supported
pair is preserved explicitly. Unknown, mutated and duplicate inventories still fail closed,
as do changed response requirements, settings, environment, model, preparation or collection.
The captured pre-temperature inventory in `tests/data/simulation-code-before-temperature.json`
was reconstructed from the actual `76a2a874` Git source blobs with the production newline
normalization; its complete digest matches the previous audited pin.

A one-time old/new reader comparison executed the actual `76a2a874` reader and the current reader
against the same synthetic native CSV/TOML. All 14 series (seven legacy variables at two native
locations) matched exactly across values, NaN masks, coordinates and every metadata field; input
bytes were unchanged. The diagnostic and fixture remain in session-3 ::
`.tmp/tasks/t2610221807/`. This establishes implementation equivalence for the exercised seam,
not production-basin qualification. No historical production experiment was available for a fresh
reopen claim; retained-record coverage uses the existing migration fixture and captured source
inventories, and checks byte preservation through the actual completed-input consumer.

The original audit tripwire was reproduced failing before repair with actual digest `12c02734…`
against expected `fe2e4d92…`. Focused verification covers the complete simulation-reuse module,
native reader and temperature checks, all three directed transitions, independent response-identity
refusal, and refusal after adding a temperature declaration to a retained model.

```powershell
pixi run pytest tests/test_simulation_reuse.py tests/test_wflow_response_reader.py tests/test_temperature_outputs.py -q --junitxml=.tmp/tasks/t2610221807/focused-tests.xml
```

The initial focused run passed 77 checks in 55.33 seconds. After extending the retained-record
case to both historical inventories and checking temperature-output mutation refusal, the final
run passed **78 checks in 36.39 seconds**, with no skips or failures. JUnit is retained in
session-3 :: `.tmp/tasks/t2610221807/focused-tests.xml`.

`pixi run ruff check blueearth_cst/experiment/simulation_reuse.py tests/test_simulation_reuse.py`,
`pixi run ruff format --check blueearth_cst/experiment/simulation_reuse.py tests/test_simulation_reuse.py`,
`pixi run python -m py_compile blueearth_cst/experiment/simulation_reuse.py tests/test_simulation_reuse.py`
and `git diff --check` passed on the final Python files. Checks use the lane's Pixi default environment,
Python 3.12.13, with normal Windows permissions for pytest. No environment packages, cache permissions
or production case were changed. The prior integrated pre-push result (5067 passed, 30 skipped,
1 xfailed, three failures confined to this module) remains evidence for unchanged surfaces; this
focused run resolves those failures and is not a fresh whole-suite claim.
