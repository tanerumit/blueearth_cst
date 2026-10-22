# WF4 historical Qcrit preflight handoff

Date: 2026-10-22. Owner: session-2, `fix/wf4-q90-preflight`; base: `a0a8fbb1`.
The implementation and this evidence travel in the same commit; the lane's ignored `STATUS.md`
records its final SHA. Retain this record for review and integration.

Python engineer, implement mode; no delegation. Applied Python discipline, testing policy,
bug diagnosis, console formatting, scientific workflows, scientific software documentation,
Git workflow and project system guidance.

## Follow-up: inline configuration

The follow-up to `f19445c2` supports flat inline `indicator_sets` entries and optional standalone flat
files. Registered defaults are inherited; `enabled: false` validates the entry but removes its inputs
and historical preparation. Empty enabled sets, unknown names, contradictory season/window parameters,
duplicate set ids and duplicate WF4 YAML keys fail explicitly. The default preset retains its
response-driven scope. Existing selectors, nested files, snapshots and explicit baseline bindings remain
supported. Omitted historical bindings use the project's WF1 model and artifact-digest source identity.

Verification on Windows in the existing Pixi environment:

```powershell
pixi run pytest tests/test_indicator_sets.py tests/test_baseline_qcrit.py tests/test_crop_water.py tests/test_run_workflows.py tests/test_simulation_runner_v2.py tests/test_indicators_module.py -q --durations=5
pixi run pytest tests/test_indicator_sets.py tests/test_baseline_qcrit.py tests/test_run_workflows.py tests/test_simulation_runner_v2.py tests/test_indicator_plan_v2.py -q --durations=5
pixi run pytest tests/test_indicator_plan_v2.py::test_simulations_only_does_not_resolve_indicator_requirements -q
pixi run pytest tests/test_config_composition.py -q --durations=5
pixi run pytest tests/test_crop_water_integration.py tests/test_named_indicator_sets_workflow.py tests/test_partial_indicators.py -xq --durations=5
```

- Initial core run: 244 passed in 103.96 seconds.
- Expanded final run: 245 passed, one old mock signature failed in 402.28 seconds. The mock was updated
  to accept the earlier `prepare_baseline` keyword; its isolated regression then passed in 23.68 seconds.
- Composition: 134 passed in 11.47 seconds, including the native Snakemake configuration smoke.
- Three inline documentation/starter examples parsed and resolved statically. Scoped Ruff checks,
  formatting, compilation and whitespace checks passed. No site rendering or production runs.
- Native CLI verification: 19 passed in 668.01 seconds. An initial attempt correctly refused
  publication because source edits occurred during the run; final CLI verification freezes executable
  sources. Sandbox composition stalls were stopped and rerun with normal permissions.

The final logs are retained under `.tmp/tasks/wf4-q90-preflight/inline-*.log` through owner review.
Original numerical checks below still cover the unchanged Q90 formula and period exclusions.

## Follow-up: Windows Snakemake permission policy

Inline configuration is committed as `fb1ce693`. The subsequent user-authorized permissions follow-up
adds a bounded `dev/scripts/check_snakemake_access.py` diagnostic and updates the owning validation
reference and AGENTS routing. It makes normal user permissions the up-front execution policy for
Windows checks invoking Snakemake. It does not change the sandbox, grant blanket approval, modify ACLs,
patch dependencies or run a model. Project-instructions, project-reference-docs and Snakemake guidance
were applied in addition to the Python/testing guidance.

```powershell
pixi run python dev/scripts/check_snakemake_access.py
```

Under the restricted token, the diagnostic exits 2 after its 15-second child timeout with recovery
guidance. Under normal user permissions, the same diagnostic exits 0 in about 3 seconds after an actual
Snakemake temporary-cache directory and file round-trip. The child cleans up its own successful probe;
`subprocess.run` stops and waits for a timed-out child. The restricted transcript is retained as
`.tmp/tasks/wf4-q90-preflight/cache-probe-restricted.log`. Scoped Ruff, formatting, compilation and
whitespace checks pass. This establishes the diagnostic's two observed outcomes, not future-session
instruction adoption or a change to upstream Snakemake's retry behavior.

## Result and boundaries

- Startup validates authored WF4 selections and Qcrit settings without opening historical output.
  Static declarations mark unresolved historical parameters and refuse calculation-record creation.
- Historical preparation happens at the WF4 boundary, after enabled upstream execution; direct WF4
  uses the same checked preparation path. Missing CSV/TOML inputs name their path and required WF1
  historical simulation. Parameter-only failures no longer prescribe `model.outvars` changes.
- A combined dry-run with WF1 enabled leaves Q90 preparation pending when its inputs are absent.
  It inspects upstream graphs as available and explicitly leaves the data-dependent WF4 DAG uninspected.
  Existing malformed inputs still fail. It creates no substitute thresholds or calculation identity.
- Omitted years and `years: all` discover historical calendar years. Explicit lists retain their
  numerical selection. Requested/discovered years, selection mode and location-specific coverage enter
  derived provenance. Incomplete/nonfinite periods remain excluded; no usable period remains an error.
- Q90 exceedance remains non-exceedance p=0.10; summer semantics, model-root resolution and fixed
  thresholds across scenarios remain unchanged. The minimal supported example omits redundant defaults.
  Existing explicit threshold records remain readable; newly derived provenance changes indicator identity.

## Verification

Windows, existing session Pixi environment; no dependency changes. Test outputs remain under the
lane's ignored `.tmp/pytest/`; logs are under `.tmp/tasks/wf4-q90-preflight/`, retained through review
and landing. No external cases or production run outputs were modified.

```powershell
pixi run pytest tests/test_baseline_qcrit.py tests/test_crop_water.py tests/test_indicator_sets.py tests/test_run_workflows.py tests/test_simulation_runner_v2.py -q --durations=5
```

210 passed in 96.14 seconds. The subsequent expanded `pixi run pytest tests/test_crop_water.py -q`
passed 29 tests in 2.53 seconds, covering both summer and annual all/explicit-year selection,
partial edges, leap-year sample counts and independent location exclusions.

The final focused runner/threshold/selection regressions passed 17 tests in 27.25 seconds.
They exercise startup rejection of malformed rules, ordering through simulated upstream children,
pending combined dry-runs, direct execution/dry-run missing CSV/TOML errors, corrupt TOML refusal,
year-selection identity and distinct response/parameter remedies.

Scoped `ruff check`, `ruff format --check`, `python -m py_compile` and `git diff --check` passed.
Read-only static validation of the Ntoum rapid case and the minimal documented YAML example passed
without preparing historical output.
No Snakefile changed. Documentation was checked against the code and minimal example; no site render,
production simulation, numerical baseline qualification or cross-platform claim is made.

```powershell
pixi run pytest tests/test_crop_water_integration.py tests/test_named_indicator_sets_workflow.py tests/test_partial_indicators.py -xq --durations=5
```

18 passed in 314.02 seconds. This serial run used normal permissions, with `TMP` and `TEMP` directed
to `.tmp/tasks/wf4-q90-preflight/native-temp/`. It covers actual synthetic indicator publication,
named sets, retained-response reuse, strict/partial availability and WF4 dry-run graphs.
Earlier sandbox attempts stalled before workflow loading and were stopped. A bounded diagnostic
trace localized the stall to `tempfile.mkdtemp` in Snakemake's existing source-cache initialization;
the normal-permission run passed without code or dependency changes for that environment issue.
The diagnostic stack is retained in the task's `startup-trace.log`.

## Handoff

The lane is verified and ready for owner review. The containing commit is the implementation/evidence
revision; the ignored lane status and completion report record its SHA. Do not land or push without
the owner's instruction. The production case configuration and run directory remain untouched.
