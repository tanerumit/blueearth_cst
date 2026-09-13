# GF15 production integration readiness

Status: assessment complete; production adapter design and implementation remain open
Date: 2026-09-13
Lifecycle: frozen-with-supersession
Revisions: 2026-09-13 — inspect production seams after owner instruction to move to the next step.

The eightfold policy qualifies candidate C on the retained synthetic matrix.
It does not make the current production reducer that candidate. Production
integration needs a reviewed adapter, an installed reproducible dependency,
and an evidence-bearing metric identity. The scientific recommendation and
applicability limits are in [scientific-assessment.md](scientific-assessment.md);
this companion records the implementation findings for the next executor.

## Measured current state

Inspected at commit `375729c3`; [inspection.json](inspection.json) is the
read-only runtime probe. No estimator fits or workflow runs were performed.

| Surface | Finding | Integration consequence |
|---|---|---|
| `blueearth_cst/experiment/metric_registry.py`, `reduce_bundle` | Calls xclim/SciPy GEV fitting and quantiles. Retains member-wise blocks, count screen and per-location parameters. | The production result is still the predecessor method. Adapt candidate C at this seam while preserving extraction and refusal behavior. |
| `metric_plan.py`, `current_metric_request` / `metric_request` | Emits only `status: provisional_operational`, `benchmark: not assessed`; runtime probe confirms other annotations are refused. | Pre-existing gap relative to accepted R12 section 7.5: reviewed evidence cannot currently be attached. Changing the estimator alone would leave provenance incomplete. |
| `metric_plan.py`, writer and reader | Copies the minimal validation object into definition and manifest; no benchmark report payload is written. | Design validation fields and a shipped immutable report with digest verification, copying, and read-back checks. Keep existing ready metric sets readable. |
| `content_identity.py`, `repository_code_inventory` | Follows static repository imports recursively; metric identity starts from `metric_plan.py`. | A statically imported shipped adapter can participate in code identity. Prove that changing its code or evidence changes the metric-set identity. |
| `metric_plan.py`, environment roots | Includes xclim, NumPy and SciPy; excludes lmoments3. | Add the selected dependency to the metric environment closure. Do not imply the isolated study environment equals production. |
| `pixi.toml`, `pixi.lock`, shared environment | No lmoments3 entry found; runtime metadata probe reports it absent. Pixi executable absent from PATH. | Resolve tooling and an isolated locked environment before production execution; never hand-edit the lock or install into the shared environment as a shortcut. |
| `tests/test_metric_registry.py` | Current assertions explicitly compare the predecessor estimator and inject failures through xclim. | Preserve those comparisons as historical evidence; replace live estimator expectations with independent candidate references and new fault injection. |

The source paths above are relative to the repository root. The source snapshot
is bound in [source-inventory.json](source-inventory.json). The missing full
validation declaration is an observed pre-existing implementation gap, not a
regression caused by the eightfold reassessment. Earlier accepted evidence is
preserved; this assessment does not relabel its execution results.

## Recommended bounded integration work

Prepare the separately reviewed adapter required by the
[accepted candidate design](../../../gf15-alternative-estimator-design.md).
That review must cover the production reducer and metric provenance together.
This document is reconnaissance and a review input, not an accepted adapter
design or an authorization to infer real-bundle adequacy.

1. Specify a shipped implementation of the fixed Stage 1 numerical method.
   Production must not import evidence or scratch code. Preserve normalization,
   finite-mean domain, stable inverse quantile and the precise exception/refusal
   distinction. Resolve the pinned-library source checks and diagnostic-only
   support policy explicitly. Avoid copying study-only raw arrays into ordinary
   metric manifests without a declared need.
2. Define the validation declaration and report packaging against R12 sections
   7.5 and 8.4: selected estimator and policy, exact tested domain and criteria,
   immutable report digest, adaptive reuse limitation, provisional screening,
   unvalidated near-zero relative error and unestablished actual-bundle
   applicability. The deployed record must distinguish C's bounded pass from
   predecessor A/B results and from original-policy failure.
3. Specify the compatibility behavior for existing `metric-set/1` artifacts.
   Reads must rely on their retained definitions, not the current estimator.
   New code, dependency or validation evidence must produce a new identity;
   no ready manifest is edited in place. Report tampering must be rejected.
4. Pin and solve the dependency through Pixi in an isolated environment for
   the declared Windows/Linux targets. Test production-environment parity
   against retained Stage 1 controls; package versions alone do not prove it.
5. Integrate the reviewed adapter and evidence using metrics-only execution on
   retained responses. Capture intentional old/new return-level differences,
   preserve collection/simulation identities and native responses, and keep
   non-return-level outputs unchanged where their inputs and formulas agree.
6. After that integration is accepted, establish the separate successor
   baseline/current-config comparison in [standing-seal-status.md](../standing-seal-status.md).

The exact adapter interface, validation schema and report asset location belong
to the reviewed design. They are intentionally not invented by this readiness
inspection. The existing pattern is sufficient for planning the seams, but the
cross-cutting contract change requires design review before implementation.

## Acceptance evidence to carry into that review

| Required property | Discriminating check |
|---|---|
| Production implements the assessed candidate | Independent retained Stage 1 reference controls agree in the proposed production environment; deliberately corrupting a quantile/domain decision fails the check. Do not use the production function itself as its oracle. |
| Extraction remains member-local | Retain existing annual/rolling, calendar, missingness and partial-year fixtures. A rolling window spanning member boundaries or reversed low-flow sign must fail. |
| Refusal and diagnostic policies survive adaptation | Required-minus-one, constant sample, non-finite inputs/parameters/quantiles and known versus unexpected library errors discriminate correct failure paths. No fallback and no ready metric row after a refused fit. |
| Evidence and estimator affect identity | Change adapter bytes, resolved dependency identity and policy/report bytes independently; each must change the new metric identity. Prior complete sets must still read. |
| Reports are portable and verified | Copy the report into the new metric set, remove access to its repository source, and read successfully; alter or remove the copied report and require rejection. |
| Metrics-only preserves upstream work | Make Wflow/generation unavailable and recompute from retained responses; collection, simulation and response digests must remain fixed. |

Existing owning tests are `tests/test_metric_registry.py`,
`tests/test_metric_plan.py`, `tests/test_content_identity.py`, and
`tests/test_export_wflow_results.py`; remeasure the final change scope before
choosing test commands. Run owning tests during implementation, repository Ruff
before its commit, and the documented full gate once at the final integration
boundary if shared code or a script signature changes. Baseline/tree gates are
required before sealing, not as a substitute for adapter verification.

## Checks performed for this assessment

The current planner probe was run with shared environment Python and assertions
enabled. It accepted the original annotation, rejected a reviewed annotation,
reported installed dependency availability, and listed the actual source
inventory. [inspect-integration.py](inspect-integration.py) reproduces it:

```powershell
$env:PYTHONPATH = (Get-Location).Path
.pixi/envs/default/python.exe -B dev/milestones/r12/implementation/evidence/gf15-production-applicability/inspect-integration.py
```

Rerun from the repository root and write output to a fresh scratch path, not over
this frozen report. No full-suite, baseline, holdout, real-basin or production
adapter validation is claimed by this inspection.
