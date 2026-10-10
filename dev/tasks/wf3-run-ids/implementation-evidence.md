# Run and group identity implementation

## Authority and contract

The user commissioned direct implementation on 2026-10-10 after synchronizing the pinned branch
`feat/wf3-run-ids` with local `main`. The separate design-review loop is waived for this implementation;
the task brief's naming, table separation, singleton membership and provenance requirements remain in scope.
No landing, push, external case migration or release is authorized.

Run IDs are prefixed strings. Group IDs are independently allocated from sorted declared grouping keys.
Both namespaces retain consistent padding within their owning context. Forcing and native response filenames
use the complete run ID once. Every selected variable has separate run and group tables, including header-only
tables when a scope has no applicable metrics. Shared membership and group metadata resolve each group to
its source runs and design point, including the unperturbed reference and singleton groups.

The new group-summary policy is an equal-weight mean of existing realization-level reductions for every
current run-grain registry entry. Member NaN propagates; unequal response lengths never change realization
weights. Wet/dry-month reductions share the existing fixed reference-month selection. Their new group means
replace the former pooled Class-C carrier and can differ under unequal record lengths or missingness.
Per-run calculations and return-level estimation from member-local annual blocks are preserved. Singleton
return-level groups still meet the same screening and validity rules. No generic averaging of return levels
or substitution with another statistic is permitted.

Old numeric-ID collections and mixed-ID metric sets are refused by revised schemas, rather than migrated
in place. Regenerate scenarios and simulate under a new experiment name; retain old roots for provenance.
Revisions: collection intent/marker `/3`, simulation intent `/2`, simulation marker `/3`, response request
`/2`, response inventory `/3`, metric request `/3` and metric-set marker `/3`. Historical `*_v2` Python
function names remain to avoid unrelated renames; their validators enforce the revised schemas.
Automatic seed material includes provider-code identity; ID producer edits can therefore change the
automatically resolved seed. Preserved calculations do not imply identical automatically regenerated samples.
Use fixed explicit seeds and matched native responses for numerical parity.

## Verification plan

| Claim | Check and falsifier | Input / reusable output |
|---|---|---|
| IDs survive CSV and resolve to files | Round-trip and staging tests; coercion or double prefix fails | Capacity boundaries |
| Groups use an independent namespace | Allocation test; changed run count renumbers groups | Same grouping keys |
| Membership and scope are exact | HM7 and reader tests; duplicates, bad references or swapped scope fail | Multi-member/singleton |
| Group summary is the intended estimand | Independent hand oracle; pooled weighting differs | Unequal lengths, NaN |
| Return-level method is preserved | Existing estimator and block-extraction tests | Identical native samples |
| Legacy artifacts fail clearly | Schema/resume tests; old formats cannot be accepted | Old and revised markers |
| Cross-workflow execution succeeds | Fresh all-five integration run | Rapid config, fresh root |
| Response surface joins without mixed filtering | Group/metadata/coordinate join and render inspection | Same integration outputs |

Development verification uses affected tests and touched-file Ruff checks. Shared-contract `test-full` and
final repository lint/format gates are due at approved batch landing, rather than per incremental edit.
The task also requires fresh all-five execution and visual acceptance. The standing baseline is stale;
it cannot certify this change. Synthetic independent oracles cover the changed scientific reduction.

## Environment and evidence

Starting implementation commit: `aecadec6`, based on local `main` at `c84ba6f8`.
Tested implementation commit: `8baf927cbc19c49ae0461196cd5ed1bb928a0b1e`.
Focused checks and fresh execution tested the frozen implementation tree captured by that commit.
The following evidence-only commit records its SHA; it changes no executable, configuration or test input.
Shared environment: `session-1/.pixi/envs/default`; Python 3.12.13, conda-forge, Windows.
Use `pixi run --manifest-path ../session-1/pixi.toml` from session-3; this preserves the session-3 working
directory. An unrestricted preflight confirmed the configured data mirror, `weathergenr` and GCS connectivity.
Logs and fresh-run evidence are under `.tmp/scratchpad/wf3-run-ids/` and task-owned pytest run directories.
The pre-existing `.tmp/scratchpad/agent-env-landing/` evidence belongs to another task and is retained.

An independent hand oracle passed on the new group reducer: realization means 2 and 10 over 365 and 730
days yield 6, while the deliberately wrong pooled-sample control yields 7.333333333333333. An all-NaN member
propagates NaN; a singleton returns its existing run reduction (2). Command:
`$env:PYTHONPATH = (Get-Location).Path; & ../session-1/.pixi/envs/default/python.exe .tmp/scratchpad/wf3-run-ids/group-oracle.py`.

During the fresh integration run's WF0 stage, final edits affected legacy HM7 refusal, prefixed-ID guards
in the generation provider and Python/Julia simulation adapters, and nearby documentation. These changes
do not affect WF0/WF1/WF2 and were frozen before WF3/WF4 resolved their code inventories. The final adapter
checks include actual Julia execution. Subsequent runtime edits invalidate dependent verification.

### Focused checks on the implementation tree

Commands use the shared manifest noted above; logs retain the exact invoked checks and diagnostics.
All results below are exit-zero passes. Overlapping suites are deliberately not summed.

| Log under `.tmp/scratchpad/wf3-run-ids/` | Result |
|---|---|
| `rows-tests.log` | 13 passed |
| `focused-v2.log` | 62 passed; registry and collection/simulation/metric contracts |
| `light-consumers.log` | 57 passed; scoped HM7 controls, naming and staging |
| `metric-plan-final.log` | 26 passed; stale schema, scope and rehashed corruption controls |
| `consumers-final.log` | 237 passed; 10 optional predecessor-tree checks skipped |
| `last-seams.log` | 50 passed; Julia parser, adapter, member catalog, downscale and neutral seams |
| `root-contract-checks.log` | 176 passed; CLI, glossary, baseline scope, semantic tree and surface axes |
| `root-ruff-final.log` | All lint checks passed; all 46 changed Python files formatted correctly |
| `final-doc-seam-unrestricted.log` | 98 passed; same 10 optional predecessor-tree skips |
| `catalog-message-final.log` | Corrected catalog diagnostic assertion passed |
| `r-parse.log` | R parse passed; existing Windows locale warnings |
| `group-oracle-final.log` | Independent unequal-length, NaN and singleton oracle passed |

The ten optional skips concern the standing `simulation/2` numeric-ID tree. They do not certify the new
format and are not substitutes for the mandatory fresh integration run. Legacy rejection and revised
schema behavior pass on fresh synthetic fixtures. No tracked files were deleted.

The final wording sweep corrected filename examples in the seam validators and naming reference.
Its first supplemental run exposed the old expected catalog-error text, then slowed in installed-library
access. The assertion was corrected and passed in isolation. Only that verified task-owned test process
was stopped; rerunning its three test files with environment access passed in 14.02 seconds. The failed
diagnostic log is retained, and the fresh integration process was not stopped or replaced.

Final seam command:
`pixi run --manifest-path ../session-1/pixi.toml python -m pytest tests/test_run_wflow_batch.py tests/test_simulator_adapter.py tests/test_member_catalog_rule.py tests/test_downscale_climate_forcing.py tests/test_neutral_simulator_seams.py -q`.

Root contract command:
`pixi run --manifest-path ../session-1/pixi.toml python -m pytest tests/test_cli.py tests/test_indicator_glossary.py tests/test_check_baseline_scope.py tests/test_semantic_tree_diff.py tests/test_surface_axes.py -x -q`.

Ruff command: resolve touched `.py` paths with `git diff --name-only -- '*.py'`, then run shared-environment
`ruff check <paths>` and `ruff format --check <paths>` with `RUFF_CACHE_DIR=.tmp/ruff_cache`.

### Results delta and migration

- Identifier/layout changes: opaque prefixed run IDs, independently numbered groups, complete run IDs
  once in filenames, separate scoped tables and explicit membership/perturbation joins.
- Preserved calculations: existing run reductions, fixed reference-month selection, pooled member-local
  annual blocks, return-level estimator/screening and four-significant-figure publication formatting.
- New summaries: equal-weight realization means for the reviewed run statistics; NaN propagation and
  explicit singleton behavior. Former pooled Class-C carriers may differ as described above.

Consumers read `group_id` from group tables and join `group_metadata.csv` directly to `st_id` in the
perturbation lookup. The reference helper now takes `group_metadata=`; its old numeric unit-index join
is removed. Read ID columns as text. Never infer scope by filtering a mixed numeric column.
Regenerate scenarios and use a new experiment name for predecessor artifacts; no migration rewrites
existing collections, experiments or baseline references.

### Fresh integration and output acceptance

Command:
`pixi run --manifest-path ../session-1/pixi.toml python -m pytest tests/test_workflow_end_to_end.py --run-integration -rs`.
Result: **1 passed, no skips, 2941.09 seconds** on 2026-10-10. This executes all five workflows
through the owned runner from a fresh rapid project root. Log: `e2e-test.log` in the task scratch folder.
WF2 reported two optional single-horizon plot products unavailable; no required workflow was skipped.

Reusable project root, relative to this worktree:

```text
.tmp/pytest/run-8f79ed159ed94bb1a354f59a1c15133a/test_all_five_workflows_run_en0/project
```

Inputs: copied rapid config set beside that root, explicit seed 123, two realizations, 2046–2054,
a 2 × 2 transient perturbation grid plus unperturbed reference. Config SHA-256 values:

```text
project_config_rapid.yml                       58fe84079118436d68f379616a0dc00fd2b1696fd20af9c17a9a5e946712090a
project_config_rapid_analyze_climate.yml       ce4d89ea93ab40f06ae233160ade6af5de144f5106fbc4a1802c4e28d0472950
project_config_rapid_analyze_projections.yml   80f044148273f897ffb17511c63f48ac919c5882b5b7ff1def58d47ced669017
project_config_rapid_build_model.yml           1c4fb9ee2c5c3f86d0d06dea006b2b95a863893f406ec8f662b55fa025f74a76
project_config_rapid_generate_scenarios.yml    8a02209f16507032bd03902a111ce97f12e0086d516e2ce2f1dec4fb959eff03
project_config_rapid_simulate_system.yml       82c612bc46e2f0d217feb27cc05824f3e215ea9f4f9a25e528868ea90bb33ad0
```

Collection: `bf1135d276af0d905e02b8aec1738cfb7007058d32eccfeafdb942792dc46048` (`scenario-collection/3`).
Metric set: `0a937ccc60efd39e2b946bdc0018cf6fd37879d76e24f03f51dacc06662272b7` (`metric-set/3`).
Production readers validated the collection, simulation, retained response inventory and metric set.
All ten forcing/native filenames equal their complete run IDs; no doubled prefix occurs.
All five groups resolve consistently through membership, scenario lookup and perturbation metadata.

| Variable | Run rows | Group rows | Independently checked group means |
|---|---|---|---|
| q | 360 | 220 | 180 |
| aet | 40 | 20 | 20 |
| gwr | 40 | 20 | 20 |

All 220 mean comparisons passed with NaN propagation, using the sum of each table's half-last-place
four-significant-digit bound and float32 quantization bound. This is a publication-rounding bound,
not a widened scientific tolerance. Return levels are group-only and remain covered by the independent
estimator/block tests; they are not compared to run means.

Inspection command, with `PYTHONPATH` set to this worktree and the shared environment active:
`python .tmp/scratchpad/wf3-run-ids/inspect-fresh-results.py <reusable-project-root>`.
Result: exit zero; `fresh-results-final.log` and `fresh-results.json` retain the detailed report.

Representative rows from the same fresh outputs:

```csv
metric,location,run_id,value
q_annual_mean,1010,run_01,10.52
q_annual_mean,1010,run_02,1.264
q_annual_mean,1010,run_03,20.23
```

```csv
metric,location,group_id,value
q_annual_mean,1010,group_01,10.49
q_annual_mean,1010,group_02,1.306
q_annual_mean,1010,group_03,20.14
```

`group_01` is the reference and contains `run_01,run_06`. `group_02` contains `run_02,run_07`
and joins to `st_id=1`; subsequent groups map in sorted design-key order.

The same outputs produced `group-surface.png` and `.svg` in task scratch. Visual inspection passed:
four distinct cells, all group labels and values legible, visible ticks, units and no clipping.
The figure uses declared transient endpoints (ΔT 0/3 °C; ΔP −30/+30%), with no interpolation.
Caption: equal-weight mean annual discharge at location 1010; the reference group is retained separately
at 10.49 m³ s⁻¹. These endpoint axes are not time means or stationary climate claims.

Task scratch logs, numerical reports, representative CSVs and the fresh project are retained for
approved landing and reuse of acceptance evidence. No generated project outputs are committed.
The prior task's scratch is preserved. The stale baseline remains explicitly unavailable as a numerical
certificate.

## Approved landing verification — 2026-10-10

Tested candidate: `a71dd6eaa07cf4cfb3bc3384eeae4324d6a036cd`.
Environment: Windows 11, Python 3.12.13, shared session-1 Pixi environment;
`pixi.lock` SHA256 `797afdad5a8f8c37dd62b2f1e2f88f3fea120c3fc53b7e7c792b860700a6782b`.
Every accepted gate ran with session-3 as its working directory.

The first correct-checkout full run found stale fixtures in exactly four test modules:
`test_check_baseline_indicator.py`, `test_metric_checkpoint_contract.py`,
`test_p2_current_carrier.py` and `test_project_tree_inventory.py`.
Commit `a71dd6ea` fixes their retired filenames, scoped targets and inventory expectations, adds both
run/group target coverage, and rejects predecessor tables under current metric-set roots.
No production code, configuration or scientific calculation changed after `8baf927c`.

| Check | Result |
|---|---|
| Focused fixtures | 216 passed |
| Full suite | 4133 passed, 27 skipped, 1 xfailed; 1099.28 s |
| Final lint | Passed |
| Final format | 445 files already formatted |
| All-five/numerical reuse | Passed; classified planning and four test-only deltas |

Exact check commands after environment/cache setup:

```text
python -m pytest tests/test_check_baseline_indicator.py tests/test_metric_checkpoint_contract.py tests/test_p2_current_carrier.py tests/test_project_tree_inventory.py -q
python -m pytest tests/
ruff check .
ruff format --check .
```

Reuse compares the candidate to `8baf927c`, excluding the classified planning paths and four test modules.

Python commands used `pixi run --manifest-path ../session-1/pixi.toml python` with an explicit command.
Ruff used the absolute executable in session-1's `.pixi/envs/default/Scripts/`.
`NUMBA_CACHE_DIR` and `RUFF_CACHE_DIR` pointed to session-3's corresponding `.tmp/` directories.
The repository's `dev/scripts/verify_landing.py record` wrapped each final gate and captured its command,
commit/tree, environment, result and log hash. Receipts and logs remain under
`.tmp/scratchpad/wf3-run-ids/landing-final-{full,lint,format,e2e-reuse}.{json,log}`.

The 27 full-suite skips comprise five Linux-only controls, ten predecessor standing-fixture interchange
cases, eleven unavailable local projection-parity cases and the separately executed integration test.
Fresh successor interchange and the required all-five execution passed in the retained acceptance run
above. The expected failure is the existing upstream HydroMT preprocessing round-trip defect.

All-five reuse hashes the original execution log, `fresh-results.json` and `group-oracle.json`.
The exact four test-only deltas do not occur on those execution or numerical-inspection paths.
Intervening main changes are task planning/evidence only. The final main synchronization preserves the
tested candidate's ancestry; its only additional path was the naming task's master brief.
Its original parent is `dev/tasks`, task ID `t2610032349`, and tree-relative path `task-brief.md`.
[Retained context](../../records/decisions/experiment-numbering-2026-10-10/implementation-evidence.md#closure-provenance)
records the original citer, target and exact source identities.
Landing permits precisely that Markdown path and this evidence document after the recorded gates.
No deletions or renames are permitted by the evidence verifier. The accepted full pass also covers
`test-fast`; a second fast suite is unnecessary.

An earlier Pixi named-task attempt used session-1's checkout rather than this candidate. Those receipts
and logs are explicitly excluded under `invalid-wrong-checkout-*`; no result from that attempt is used
for acceptance or landing. Explicit executable commands were then run in the correct checkout.
