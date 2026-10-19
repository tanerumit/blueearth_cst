# Structured metric registry implementation

Implementation owner: `blueearth_cst`, `feat/named-indicator-sets`, session-2.
Completed and committed: `68fe3a89ee20f33bdda33d0af3b7cc9ca59ca3d9` (2026-10-18).
Reference owner: Workbench assignment `t2610181131-wf4-metric-experiments`.
The structured-registry usability revision in that assignment's `brief.md` defines scope.
Workbench sources and retained executions were read-only throughout this implementation.

## Implementation

`blueearth_cst.metrics` owns neutral inputs, contracts, trusted installed-set discovery, parameter and
result validation, calculations and independent checking. Each of `default`, `flow_regime` and
`flood_risk` owns its registry, calculations, checks and README. New callable methods require no central
statistic or fictitious legacy equivalent. Fixed assumptions are declarations; the water-year anchor,
prepared reference and group membership remain explicit inputs. The legacy registry and GEV imports
delegate through compatibility adapters. `experiment/response_series.py` remains byte-identical to
preserve retained native-reader identity.

WF4 supports existing definitions/aliases plus trusted local selections. YAML remains declarative.
New `metric-set/5` publications retain execution context, assumptions once per contributing set, and
named local diagnostics. Existing `/3` and `/4` artifacts remain readable. Inspection uses saved
artifacts without current registries or original inputs; fresh rechecking requires matching execution
sources, definitions, inputs and dependency versions, and writes a new checker-attributed receipt.
Strict reuse checks remain in force. Hash consistency is not proof of authenticity.

The user explicitly chose to preserve existing qualification on 2026-10-18. The flood example declares
2/5/10/15/20-year levels, but shipped evidence covers only the 2- and 10-year probabilities. Unsupported
probabilities remain refused, and insufficient blocks retain their distinct screening exception.
The five-period set cannot claim a successful all-period qualified publication under current evidence.

Authoring fixtures demonstrate median and nonannual consecutive-above-threshold event duration, with
hand-built boundaries, empty/no-event behavior, named scalar-cell diagnostic tables, wrong-value and
wrong-diagnostic rejection, and explicit missing-check failures. This is an interface exercise, not
independent human usability evidence or scientific qualification of an event indicator.

## Numerical evidence

Task-owned scratch: `.tmp/structured-registry/` beside this report.
Pre-change source archive: `d41c75936c2883857e7dc997f0414b2749bd998f`, after synchronizing the clean
local lane with main's six task-record commits. It contains the named-set implementation from the
handoff; no branch was landed to begin the work.

`probe.py` evaluated the archived and revised reducers over the same retained daily discharge snapshot.
All 128 metric/location values match exactly, including the original default q suite and five optional
q statistics, across `YE-DEC` and `YE-SEP`. The snapshot has 7,304 retained daily values at each of four
locations, January 2, 2040 through December 31, 2059. Reference month selection explicitly uses 1040.

Prototype comparison covers 76 qualified available values at `rtol=1e-10, atol=1e-12`; maximum absolute
difference is `7.105427357601002e-15`. Twelve reference values at unsupported flood probabilities are
refused under the unchanged gate, following the user's explicit decision. Eight recharge entries
remain unavailable for this q-only input. Therefore this is not an 88-value production qualification
claim. A 25-year request reports `required=25, actual=20` before probability qualification.

| Reference | SHA-256 |
|---|---|
| `inputs/run-01-discharge.csv` | `7cb8b62d6b087dd5b0a7a91dc61dd5f67bbd2fb974532bb7d0bedb78cc734869` |
| Three-set prototype results | `c84ddd7a94676c45630c74b312d71e30a34586ba9c95598c0bc027c4282f1779` |

Commands used the existing session Pixi environment. `PYTHONPATH` and cwd isolated the archived run;
the revised run imported session-2. `before.json` and `after.json` retain values, input hashes,
tolerances, qualification refusals and the independent-check outcomes.

These single-member comparisons do not replace the run/group, native missingness, export, recovery
and cache regressions or the retained-response WF4 execution. The implementation/checkers share the
fitting library; their agreement does not independently validate lmoments3 or expand GF15 qualification.

## Verification and execution

- Final staged core gate: 220 passed, five platform-specific skips. This includes the strengthened
  extension fixture, rate output units, explicit missing-check failures and the fresh-process boundary.
- Consumer/evidence check: 151 passed, 11 skipped, covering inspection, interchange consumers,
  named exports, return-level declarations and extension fixtures. Skips identify the standing fixture's
  old archive/numeric-run-ID contracts; they are not current WF4 acceptance passes.
- Final publication/inspection/request checks: 29 passed. A subsequent historical-evidence filtering
  check passed and confirmed that a comparison report with the same publication binding is not counted
  as a historical numerical check.
- `pixi run lint` passed. `pixi run format-check` passed after formatting one new test file;
  subsequent edited Python files received scoped Ruff and formatting checks.
- Real old `metric-set/3` publication `5e08a572d6b4` passed integrity inspection without rewriting it.
- A disposable copy of the existing `ye_jan` matched-response project passed the supported WF4 dry run.
  It selects the default suite and a local flood subset containing only qualified 2/10-year calculations.
  WF0–WF3 and model simulation are omitted: this task changes retained-response metrics only.

The real indicators-only execution completed successfully. Its default publication contains 700 finite
estimates; all six q/aet/gwr run/group tables are byte-identical to the retained `/4` oracle. The separate
qualified flood job contains 40 finite estimates and published independently through the same runner.
Both publications passed fresh independent numerical rechecks, including local diagnostics. The final
inspection CLI also wrote a fresh receipt for the qualified flood publication.

| Publication | Immutable metric-set ID |
|---|---|
| Default | `a82185229472f36fa72818d5e7f6686ef6163f38250ba1ab11fedd812251de9e` |
| Qualified flood subset | `dba8b642b079ce2090a0d8bdda07a68fed08b82f2bf31caad69f1ef5eb86585a` |

The initial broad regression run began before source stabilization and encountered subprocess timeouts.
It was stopped; no full-suite pass is claimed. Both affected contracts passed isolated retries against
the final staged candidate: the dry-run/stale-input case (75.17 s) and the publication, export repair and
forced byte-preserving reuse case (238.31 s). Their receipts were verified against the committed tree;
no gates were rerun solely to produce a receipt. The existing task-board check has nine unrelated
baseline errors in other notes/folders; the generated board has no task-induced diff.

Recorded core command:

```powershell
pixi run pytest tests/test_metric_registry.py tests/test_indicator_sets.py tests/test_metrics_module.py tests/test_metrics_definition.py tests/test_indicator_tables.py tests/test_gev_lmoments.py tests/test_response_series.py -q
```

Other focused commands:

```powershell
pixi run pytest tests/test_metric_inspection.py tests/test_interchange_contracts.py tests/test_named_export.py tests/test_return_level_validation.py tests/test_metrics_module.py -q --durations=5
pixi run pytest tests/test_metric_inspection.py tests/test_metric_plan.py -q --durations=5
pixi run pytest tests/test_metric_checkpoint_contract.py::test_a_dry_run_writes_nothing_and_a_stale_response_is_refused -q
pixi run pytest tests/test_metric_checkpoint_contract.py::test_a_published_set_is_reused_byte_for_byte_under_forceall -q
```

Candidate-bound evidence lives in `core-gate.json` and `checkpoint-gate.json`; command output is in
`core-final.log`, `checkpoint-retry.log` and `checkpoint-reuse.log`. The actual project/config and runner
logs are in `execution-project.yml`, `execution-wf4.yml`, `dry-run.log` and `execution.log`.
`execution-verification.json` retains table parity and both recheck results; `flood-recheck-final.log`
retains the supported CLI's latest receipt. No run outputs or reference data were committed.

Next: the owner decides whether to land the completed branch. No landing, push, external review or
additional estimator qualification was performed.
