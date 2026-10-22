---
title: Configurable baseline Qcrit and retained temperature outputs
type: todo-item
status: active
effort: 1
area: toolbox
branch: feat/t2610221645
queue:
created: 2026-10-22
updated: 2026-10-22
---

> [!note] Overview
> **What changes** — Bundle configurable fixed historical Qcrit quantiles with end-to-end temperature output support; configure the Gabon rapid case after validation.
> **Why it matters** — Crop-water currently requires hand-prepared Q90 thresholds and model outputs cannot retain temperature.
> **What it takes** — Two coordinated features with configuration, provenance and consumer tests.

## Progress

- [x] Implement configurable baseline quantile rules for crop-water Qcrit.
- [x] Support temperature throughout model outputs and retained-response consumers.
- [x] Validate both features and update the Gabon rapid case when compatible.

## Work location

- Owner: session-3; branch: feat/t2610221645; implementation commit: `4ff35de7cb564ea58aefbc056a8dd01938ebd614`.
- Herdr: workspace wA (cst · s3), pane wA:p2; agent python-engineer-qcrit-temp.
- Next: close the landed task on the canonical board; no push is authorized.

## Completion evidence (2026-10-22)

- Toolbox implementation committed as `4ff35de7cb564ea58aefbc056a8dd01938ebd614` in session-3; its working tree is clean.
- Qcrit rule: `thresholds.baseline_quantile` in a crop-water registry override. Defaults remain
  Q90 exceedance (non-exceedance p=0.10), linear interpolation, complete May–October periods.
  Annual calendar-year references and alternate quantiles/methods are configurable. Preparation reads
  WF1 historical model output and retains source CSV/TOML digests, rule, years and coverage in identity.
  Explicit operational thresholds remain supported; scenarios never refit the reference.
- Temperature: semantic `temperature`, code/token `temp`, upstream `atmosphere_air__temperature`,
  degrees Celsius. Native reading, retained inventory, default annual mean, plots, glossary,
  starter comments and published workflow reference updated. Existing output defaults unchanged.
- Gabon scientific decision: user selected complete calendar years on 2026-10-22. Candidate uses
  historical model years 1995–2005, annual Q90 exceedance and linear interpolation. Low-flow day counts
  remain May–October; this assignment does not establish a Gabon crop calendar.
- External case: three labelled candidate files under
  `cst-cases:applications/gabon-ntoum-v2-rapid/`: `project_config_candidate.yml`,
  `project_config_simulate_system_candidate.yml`, `crop-water-candidate.yml`.
  Candidate adds temperature after the existing five outvars and uses an isolated candidate output root.
  Active configs unchanged; INSTRUCTIONS.md documents adoption and prerequisites. No case files staged.

### Verification

Environment: session-3 Pixi default, Python 3.12.13; Julia/Wflow from repository-managed Project/Manifest.
No environment or lockfile changes. Final implementation tree is the commit above.

```powershell
pixi run pytest tests/test_crop_water.py tests/test_baseline_qcrit.py tests/test_temperature_outputs.py tests/test_indicator_glossary.py tests/test_indicator_tables.py tests/test_indicator_sets.py tests/test_indicator_registry.py tests/test_setup_gauges_and_outputs.py tests/test_wflow_response_reader.py tests/test_crop_water_integration.py tests/test_partial_indicators.py tests/test_func_plot_signature.py tests/test_wf1_plot_outputs.py -q
```

- Integrated affected run: 249 passed, one stale count assertion failed (18 default definitions now,
  previously 17). Updated assertion and reran that exact test: 1 passed. No production change followed.
- Additional independent-module checks and temperature sum refusal: 38 passed via
  `pixi run pytest tests/test_temperature_outputs.py::test_temperature_default_refuses_depth_sums tests/test_indicators_module.py tests/test_indicators_definition.py -q`.
  Total distinct affected checks passing after focused reruns: 288.
- Strengthened WF1 output contract to include temperature plots; reran
  `pixi run pytest tests/test_wf1_plot_outputs.py::test_delete_all_output_removes_a_basavg_figure -q`:
  2 passed. WF4 CLI publication and dry-run covered by crop-water integration tests above.
- Scoped `ruff check`, `ruff format --check` (16 Python files), `python -m py_compile`,
  and `git diff --check`: passed.
- Isolated two-day Wflow execution from this lane's existing test_local model, adding temperature:
  passed, four locations with two finite daily degC values. Command:
  `pixi run python .tmp/tasks/t2610221645/temperature_smoke.py`.
  Input TOML and engine log retained under session-3 `.tmp/tasks/t2610221645/temperature-smoke/`.
  Source model and its historical output were read-only. This is an interface smoke check, not a
  new numerical baseline or a Gabon assessment.
- Annual and monthly temperature PNG previews generated from a controlled seasonal series and visually
  inspected: mean/degC labels, negative values preserved, no clipping. Previews/captions live beneath
  the same smoke directory's `plots/`.
- Active/candidate case composition and six-versus-five outputs checked with
  `pixi run python .tmp/tasks/t2610221645/verify_case.py`: passed. Candidate historical model output
  is absent, so its full DAG/execution was not attempted. No production case run was performed.
- Initial restricted CLI runs stalled in Snakemake source-cache `tempfile.mkdtemp`; py-spy identified
  that stack and an ordinary-versus-0700 directory probe confirmed the Windows token issue.
  Stopped only task-owned pytest trees; affected workflow checks passed under elevated execution.
  No package patch or cache-permission change was made.

### Review and retention

- No landing or pushing. Main advanced nine commits during this task; implementation was verified
  in the allocated lane without incorporating concurrent work. Reconcile integration before landing.
- Keep smoke inputs, log, plot previews and small validation scripts in lane-local task scratch until
  review/landing evidence is retained. Inaccessible private-directory probe is task-owned scratch;
  no unrelated caches or agent processes were changed.
- No remaining scientific decision blocks this implementation. Before Gabon use, inspect historical
  included/excluded years and locations (first annual period can be incomplete at interval-end labels),
  and assess whether the existing May–October counting season fits the intended screening question.

## Implementation scope

Use the python-engineer role in implement mode. Read the full role at
`BRAIN_INFRA_ROOT/artifacts/agents/python-engineer.md` and apply its bound skills.
One worker owns both features, their tests, affected templates and authoritative documentation.
Other sessions are active: preserve their edits and do not revert or integrate their branches.
Do not spawn further agents. Keep all toolbox implementation in session-3.

Qcrit: expose an explicit baseline quantile rule, defaulting to Q90 exceedance (p=0.10).
Support another requested quantile with unambiguous exceedance/non-exceedance semantics.
Derive fixed per-location thresholds from identified historical model discharge, never future scenarios
or the case's synthetic observations. Preserve baseline identity, years, period, quantile method and
coverage in calculation provenance. Retain support for explicit operational thresholds.
Inspect `prepare_baseline_qcrit` in the crop-water calculations module: it currently pools complete
May–October periods and hardcodes p=0.10. Its threshold schema also hardcodes the method string.
Make the reference period explicit; preserve the existing seasonal default for compatibility.
Do not silently impose a new seasonal convention on Gabon. Resolve case annual-versus-seasonal choice
with the user if required; implementation and tests can proceed independently.
Connect preparation to the owned workflow so users need not hand-copy threshold values.

Temperature: add the semantic output name `temperature` alongside discharge, precipitation, PET, AET
and recharge. Verify upstream Wflow standard name and units using authoritative documentation.
Audit model output setup, CSV codes, retained responses, unit/aggregation contracts, plots, default
indicators and glossary. Temperature needs state-variable reductions, never precipitation-style sums.
Preserve existing output behavior and the current five configured variables.

Target case: `cst-cases/applications/gabon-ntoum-v2-rapid/` under the user's workspace.
Its external configuration edits are authorized, but leave it runnable against main until the features
are landed, or provide a clearly labelled candidate config for session-3 validation.
Current case has all five workflows enabled; ERA5 1990–2020; model baseline 1995–2005;
future 2050–2060; selected sets default, flow_regime, eflow-erfa and crop-water.
The case and many unrelated changes are untracked/dirty in cst-cases: never stage them wholesale.
No production case run, landing or push is authorized by this assignment.

Read dev/reference/dev-validation.md before choosing checks. Test quantile convention, fixed thresholds
across scenarios, incomplete baseline coverage, invalid settings and provenance changes. Verify temperature
mapping and aggregation through affected consumers, with appropriate workflow contract/DAG checks.
Commit completed verified implementation in the session; maintain lane-local STATUS.md and this note.
Report commits, checks, unresolved decisions and limitations when ready for review.


## Authorized landing (2026-10-22)

The user explicitly requested merge and landing on main. The managed session tool rebased without
conflicts and landed the verified candidate as `7b22f7df1be890a1b52f6e4a3377e2fc4d1010f0`. The rebased implementation is `f6841501`;
candidate tip is `b68170fe`. All 288 affected checks passed freshly with no skips,
failures or errors. Committed-tree equivalence and candidate ancestry passed; session-3 was parked
and its merged branch deleted. No push occurred. Unrelated primary edits were preserved.

Durable decisions and verification evidence:
[Qcrit and temperature outputs](../records/validation/qcrit-temperature-outputs.md).
The lane-local JUnit report is `.tmp/tasks/t2610221645/landing-tests.xml`.
The former no-landing scope above is superseded only by this explicit landing authorization.
