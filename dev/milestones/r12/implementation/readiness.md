# R12 implementation readiness

Status: preparation completed; implementation and numerical runs not started.
Inspected 2026-09-10 in session-3 on `feat/wp3-improvements`.
Source commit: `dffa4625c9c1f01bd8a77e0d91ae1a0a8f3538e8`.
This is a dated operational inventory, not scientific acceptance. Recheck it
when execution starts. The [accepted design](../wf3-simulation-identity-design.md)
governs; archived draft assumptions do not override current repository facts.

## What can run today

| Check | Observed result | Limit of the evidence |
|---|---|---|
| `pixi run --as-is python dev/scripts/check_env.py` | **Passed**, exit 0; [captured output](environment-check.txt) | Checks console-script presence, queries the installed weathergenr version and Julia package status. It does not execute weather generation or Wflow. |
| `pixi run --as-is python dev/scripts/check_baseline.py record --help` | **Passed**, exit 0; [captured output](baseline-cli-check.txt) | Confirms imports and CLI availability; records no baseline and validates no model results. |
| Source comparison below | No changes to the selected runtime/config/test surfaces since the design's code baseline | Documentation/review/planning changed. This is not a numerical comparison. |
| Package metadata queried through the checkout's environment Python | Python 3.12.13; Snakemake 9.6.2; pytest 9.0.3; hydromt 1.3.1; hydromt-wflow 1.0.2 | Installed metadata alone does not establish runtime compatibility. |

The restricted tool shell did not expose Pixi or Julia on PATH. A host command
lookup found both; the actual checks above ran through the installed Pixi
executable. This was a shell-visibility issue, not a missing installation.
`pixi run --help` confirms `--as-is` means `--frozen` plus `--no-install`, so
these checks did not request dependency installation or lockfile updates.
The environment check reported weathergenr 2.0.0, matching
`dev/scripts/install_weathergenr.R`; Julia's project status contains Wflow.

Source reconciliation command, run from the repository root:

```powershell
git diff --stat 4e26c2394dd002f7dfb61b1943e002866c6ca4bf HEAD -- blueearth_cst run_stress_test.smk scripts config tests pixi.toml pyproject.toml
```

The command returned no differences. `git diff --name-only` over the same
revision interval without path restrictions showed only documentation and
planning records. Re-run both comparisons against the execution checkout.

## Baseline evidence that must be refreshed

The baseline config set now asks for `simulation_window: 2046–2054`, two
realizations and a 2 × 3 perturbation grid. The standing manifest still records
`feat/r14-p1-loader` at `9bfdda5c036c1ca0b428ffc28fe7487a37a37c53`, with seven
targets. `AGENTS.md` explicitly warns that its retained files and manifest agree
with each other while predating the current configuration.

Local inspection found `test_case/test_local` as a real directory, the retained
WF1 discharge `models/hydrology/wflow/run_default/output.csv`, and the old WF3
`experiments/experiment/results/q_indicators.csv`. The retained workflow snapshots
still use `snake_config_*.yml` names; the current-name build-model snapshot is
absent. `test_case/test_rapid` is absent. These observations establish presence
of old artifacts only; neither freshness nor ability to execute the current DAG
has been established. The catalog's local root exists, but its full source
inventory has not been validated.

Follow accepted §9.6 and §12.3:

1. Freeze the current composed baseline scientific settings, source/model/code
   and environment provenance, plus the resolved seed, before numerical edits.
2. Define separate pre-change and post-change output roots using the same
   scientific configuration. Keep generated outputs outside tracked repository
   content; use the documented dev exemption only deliberately.
3. Run the pre-change workflow and preserve the actual numerical outputs for
   crosswalk comparison. WF1 must use `--notemp` when retaining its discharge.
4. Store comparison manifests and their reference sidecars separately from
   `dev/baseline/manifest.json`. The existing recorder accepts `--project-dir`,
   `--manifest` and repeatable `--workflow`; the reference directory follows the
   supplied manifest location. Any restricted workflow coverage must be declared.
5. Implement GF-9's old/new identity and metric-row crosswalk. The standing
   recorder is not a substitute for that comparator. Update the standing baseline
   only after the identity comparison is accepted, as §9.6 specifies.

Concrete config/output paths for these fresh runs are a phase-0 deliverable;
the standard seed config must retain its `project_config_` prefix. No fresh-run
config, output root or reference manifest was created during this preparation.
Do not run `record` on the old local artifacts and call that a pre-change run.

## Existing checks versus missing R12 checks

These commands exist and are relevant; they were inspected, **not run**, during
this documentation task. Run them at the owning phase's boundary with activated
environment and full output captured to a file.

| Existing check | What it contributes |
|---|---|
| `pixi run pytest tests/test_cli.py` | Current entry-point DAG tests; stage-owned temporary fixtures are built by the tests. They do not prove the proposed entry points. |
| `pixi run pytest tests/test_config_composition.py tests/test_run_workflows.py` | Existing configuration composition and runner behavior. |
| `pixi run pytest tests/test_check_baseline_scope.py tests/test_check_baseline_provenance.py tests/test_check_baseline_discharge.py tests/test_check_baseline_indicator.py` | Existing recorder/comparator behavior on test fixtures, not a fresh project comparison. |
| `pixi run pytest tests/test_indicator_tables.py tests/test_interchange_contracts.py` | Current table and seam contracts to preserve/migrate. |
| `pixi run test-full` | Existing full non-integration test task; `--run-integration` is a separate opt-in in `tests/conftest.py`. A full-suite pass alone does not establish model-run acceptance. |

The proposed `generate_scenarios.smk` and `simulate_system.smk` do not yet exist.
Searches of `tests/`, `dev/scripts/`, `run_stress_test.smk` and `blueearth_cst/`
for `P2b`, `GF-29`, `GF-30`, `GF-32`, `metrics-only`, `scenario_collections` and
`collection_intent` found no matching implementation. A followed-link filename
search in the design/run/test trees found historical prose probes, not a runnable
P2b/checkpoint fixture. Thus the new gates are **not implemented**, rather than
failed or passed. [Validation map](validation-map.md) assigns their construction.

The first executable development task is a bounded, synthetic P2b fixture:
combine the row-derived wildcard alternation and ancestor input function in the
three states named by §5.2. It must pass **before landing 1**. Small fixtures for
target/operation enforcement and source/metric checkpoint composition can follow
without weather generation or Wflow. Their end-to-end GF-29/GF-30 counterparts
still require implementation and actual execution before entry-point extraction.

## Execution decisions and stop conditions

Preparation does not change the accepted science. Use Astra for the future
scientific/methodological evaluations. GF-15 numerical tolerance approval precedes
benchmark execution; a benchmark pass does not validate the provisional screening
policy. The accepted Class-B interval deferral remains a disclosed limitation.

Before the first numerical run, resolve fresh output locations and preserve the
pre-change evidence. The acceptance already given to the design need not be
requested again. A changed scientific method, an unsupported Snakemake mechanism
requiring a changed invocation contract, or an unexplained numerical difference
returns to its explicit design gate. Environment repair is needed only if a
subsequent actual check fails; this inspection identified no installation repair.
