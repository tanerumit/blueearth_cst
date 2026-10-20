# Task Brief — Readable run IDs and separate run/group metric tables

### Context

Governing rules: `AGENTS.md` and `dev/reference/dev-validation.md`.
Date: 2026-10-10. Lifecycle: temporary task brief. Branch: `feat/wf3-run-ids`.

- The user approved prefixed run IDs, independent `group_01` IDs, separate metric tables,
  and explicit membership for every group, including single-member groups.
- WF3 owns the run inventory; WF4 currently allocates pooled metric IDs after the run count.
  This is one coordinated WF3-to-WF4 contract change, not a filename-only edit.
- The inspected Liberia example has run IDs `01`–`14` and group IDs `15`–`21`.
  Group `15` contains runs `01` and `08`; return-level metrics use pooled groups.
  Evidence: `q_indicators.csv` and `metric_run_lookup.csv` in metric set `f957a342312c`
  of experiment `active_20261009` under the user's external `sp2-liberia` case.
- Group-level summaries of existing run metrics are new numerical products. Illustrative
  averages discussed with the user do not constitute a reviewed policy for every metric.
- Board registration is pending: the canonical board on `main` contained unrelated dirty
  changes at authoring. This backing brief does not create a branch-local board note.

### Goal

Make identifiers readable in CSV tools and provide separate, consistently keyed outputs for
individual-run analysis and group-level response surfaces. Preserve explicit provenance and
existing calculations while defining any new group summaries deliberately.

### Non-goals

Change weather generation, perturbation design, Wflow physics, or existing return-level estimators;
build API/frontend features; rename unrelated identifiers; edit external case outputs in place.
Writing this brief does not authorize implementation, landing, pushing, or a release.

### Allowed scope

**Permitted when implementation is commissioned:** the run identity and metric-output contract,
its direct producers/consumers, focused tests, and current documentation. Initial inspection targets:

- `blueearth_cst/experiment/scenario_rows.py`, `scenario_collection_v2.py`,
  `generation_plan.py`, `content_identity.py`, `metric_groups.py`, `metric_registry.py`,
  and `metric_plan.py`.
- `blueearth_cst/shared/interchange_contracts.py`; simulation inventory, publication,
  checkpoint, runner, and metric readers found by the dependency search.
- `generate_scenarios.smk`, `simulate_system.smk`, and their owned wrappers where affected.
- Corresponding tests and configuration/schema references if their contracts change.

This is an initial map, not a complete ownership claim. Re-measure before implementation:

```powershell
rg -n 'run_group_id|metric_run_lookup|unit_id_capacity|run_group_id_capacity' blueearth_cst scripts tests config docs
rg -n 'run_id|run_\{|_indicators\.csv' .
```

**Decision-gated:** scientific reduction rules for newly added group summaries and the treatment
of existing collections/metric sets. Resolve these in a reviewed design before implementing them.

**Forbidden:** hand-editing generated catalogs, lockfiles, retained case outputs, sealed records,
or upstream packages. External API/frontend changes require a separate handoff.

### Required changes (checklist)

- [ ] Establish the reviewed contract and migration policy using `design-review-loop` before code
  changes. Carry the agreed schema below into the design; resolve calculation and compatibility
  choices without reopening naming decisions. Register the task on the canonical board when safe.
- [ ] Use opaque string run IDs such as `run_01` everywhere: collection inventory, simulation
  references, metric rows, manifests, and memberships. Apply consistent numeric suffix padding
  within a collection. Form filenames from `<run_id>.<extension>` so existing basenames such as
  `run_01.nc` remain natural and never become `run_run_01.nc`. Remove integer parsing assumptions.
- [ ] Allocate `group_01`, `group_02`, etc. independently of run count and selected metrics.
  Define deterministic ordering from declared grouping keys. Freeze exact membership in the
  owning artifact. IDs are locally scoped; matching labels across collections do not prove
  matching data. Changing membership must change the owning content identity.
- [ ] Emit separate run and group indicator tables per applicable variable, plus one shared
  membership table. Group identity and membership must not disappear when only one run belongs
  to a group. Validate unique metric/location/ID keys, valid references, and duplicate-free
  membership. Decide and document empty-table behavior for metric selections lacking one scope.
- [ ] Define a group reduction for every metric intended for response surfaces. Candidate policy:
  equal-weight mean of realization-level summaries for annual mean and baseflow index; preserve
  pooled-sample estimation for return levels. Review the complete metric registry, missing-data
  rules, unequal sample lengths, minimum samples, validity outcomes, and singleton behavior.
  Never silently average all metrics or substitute a different calculation for one-member groups.
- [ ] Supply a documented group-to-perturbation-coordinate join for plotting. Reuse existing
  metadata where sufficient; otherwise define a minimal group metadata product. Include reference
  or unperturbed groups explicitly. The response-surface input must not require mixed-ID filtering.
- [ ] Update every affected reader, validator, identity projection, checkpoint, example, and live
  document together. Version changed schemas and specify old-artifact handling. Demonstrate that
  old outputs cannot be silently interpreted as new ones or reused under stale content identities.

Agreed table shapes, illustrated with synthetic values:

**`q_run_indicators.csv`**

```csv
metric,location,run_id,value
q_annual_mean,1010,run_01,500
q_annual_mean,1010,run_02,460
q_annual_mean,1010,run_03,350
```

**`q_group_indicators.csv`**

```csv
metric,location,group_id,value
q_annual_mean,1010,group_01,480
q_annual_mean,1010,group_02,350
q_return_level_10yr_max,1010,group_01,1800
q_return_level_10yr_max,1010,group_02,1250
```

**`group_members.csv`** — shared across variable-specific metric tables:

```csv
group_id,run_id
group_01,run_01
group_01,run_02
group_02,run_03
```

Annual means above illustrate the proposed equal-weight reduction. Return levels are illustrative,
not derivable from the displayed annual means. Group metadata is an additional join requirement;
its filename and schema are to be resolved in design, not implied by these three tables.

### Commit plan

Keep contract changes atomic with their callers and tests: prefixed run IDs with all inventory,
filename, and simulation consumers; split metric products with their writers, readers, validators,
and schema identities. A staged compatibility approach is acceptable only if each commit remains
usable and its transition is documented. Commit the brief separately from implementation.

### Validation

Follow the live ladder and map each claim to its falsifier. Record tested SHA, environment, input
identity, commands, results, and reusable output roots in this task's implementation evidence.

| Claim | Check / falsifier | Input and reusable output |
|---|---|---|
| Text IDs survive CSV | Round-trip tests; numeric coercion fails | Prefix and padding cases |
| IDs resolve to files | Generation/runner tests; doubled prefix fails | Small collection; fresh rapid |
| Groups ignore run count | Allocation test; renumbering fails | Same keys, extra runs |
| Membership is exact | HM7 tests; accepted bad reference fails | Two-member and singleton groups |
| Summaries are correct | Hand oracle; wrong weight/validity fails | Unequal lengths; missing data |
| Estimates are preserved | Mapped comparison; changed estimate fails | Identical native samples |
| Surfaces join directly | Join/render; missing or duplicate point fails | Same fresh rapid outputs |
| Stale artifacts fail | Resume tests; silent old-schema acceptance fails | Legacy and changed membership |

Focused starting command, expanded only for the discovered dependency surface:

```powershell
pixi run pytest tests/test_scenario_rows.py tests/test_scenario_collection_v2.py tests/test_generation_plan_v2.py tests/test_metric_registry.py tests/test_metric_plan_v2.py tests/test_hm7_v2.py tests/test_simulation_runner_v2.py
```

Run affected tests during iteration and Ruff lint/format checks on touched Python before commits.
Run `pixi run pytest tests/test_cli.py` when rule inputs, Snakefiles, or script signatures change.
At final implementation batch landing, run `pixi run lint`, `pixi run format-check`, and
`pixi run test-full` once on the synchronized candidate. This cross-workflow contract also owes
one fresh `pixi run test-e2e` with no required skips; reuse its rapid outputs for inventory,
join, render, and applicable numerical acceptance instead of another full execution.

Redirect gates to files under `.tmp/scratchpad/wf3-run-ids/`; retain needed evidence before cleanup.
The standing numerical baseline is documented as stale. Do not claim a passing baseline gate
until the reference has been regenerated under its own prescribed configuration and authority.
Use matched-input independent checks for this change; resolve any owed baseline gate explicitly.

### Acceptance criteria

- Run IDs are text-prefixed throughout; group numbering never starts at `k + 1`.
- Each variable's run and group tables have the specified separate schemas and correct coverage.
- Single-member groups remain present, with declared calculation and validity behavior.
- Membership and perturbation metadata resolve without ambiguity in their owning context.
- Group products cover the reviewed surface metrics; existing metrics retain their numerical meaning.
- Compatibility policy, schema versions, identity changes, and consumer migration are documented.
- Required checks pass, numerical differences are explained, and affected renders are inspected.
  Failed references, ambiguous legacy interpretation, or unexplained numerical changes block landing.

### Output requirements

Deliver the reviewed design, coordinated implementation, focused tests, migration/usage guidance,
and evidence. Include a results delta separating identifier/layout changes, preserved calculations,
and newly introduced group summaries. Provide representative CSVs and a group-level surface render.

### Task constraints

Remain in the pinned session/branch until the user authorizes switching or landing. Preserve the
canonical board on `main` and unrelated work. No automatic in-place migration of existing outputs.
The user commissioned direct implementation on 2026-10-10, waiving the separate design-review loop.
Implementation decisions and verification results are recorded in
[implementation-evidence.md](implementation-evidence.md), including explicit old-artifact handling.
