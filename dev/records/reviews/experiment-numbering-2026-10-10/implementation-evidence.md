# Experiment numbering implementation evidence

Branch: `feat/minor-improvements`, session-1. Implementation authorized 2026-10-10.
No landing, pushing, release, output migration or output deletion is authorized by this task.

## Decisions and delivered units

- P0: user accepted reservation lifecycle v3 after the single capped review. Acceptance is recorded in
  `design-runs/reservation-lifecycle/`; commit `2111cae7` records G2.
- P1: `3bea47b9` removes the scaffold's mandatory `active/` suffix. Companion case changes are
  `cdaad63` in cst-cases. Existing outputs and configured roots remain intact.
- P2: `ea125361` adds immutable numbered reservations, ledger high-water allocation, verified recovery
  and the Windows archive-lock contention fix. The library was inactive until runner integration.
- P3: `4e409685` integrates both runners, early guards, original-plan continuation and paired binding.
- P4: read-only inspection, current documentation and task-local acceptance are complete.

Plain runs select the highest allocation in a family regardless of completion. Only `--new-experiment`
advances numbering. Scientific request changes refuse before producers; compatible unfinished WF4
continues. Ready WF3 collections retain their original bound plan, including original create decisions.
Partial WF3 initialization/generation is diagnosed and preserved, without unsupported repair.
Metrics-only uses retained responses without requiring current generation, catalogs or native model.

## Focused evidence

Commands use this worktree's Pixi environment on Windows 11, Python 3.11, and external juliaup Julia.
Scratch evidence root: `.tmp/scratchpad/t2610032349/`. Elevated verification grants local P-drive
catalog access and the normal Windows token needed for the private-tempfile fixtures.

| Claim | Command / case | Result | Evidence relative to scratch root |
|---|---|---|---|
| Scaffold root / existing outputs | `pytest tests/test_create_case.py` | 16 passed | `create-case-tests-final.log` |
| Allocation, contention and publication recovery | `pytest tests/test_reservation.py` | 75 passed | `p2-candidate/check-activated-01.log` |
| Windows lock waits and timeout | `pytest tests/test_workflow_config_snapshot.py` | 14 passed | Focused P2 gate |
| Paired freeze, corruption, unknown archive, repeated recovery | `pytest tests/test_reservation_freeze.py` | 22 passed | `p2-candidate/check-freeze-final.log` |
| Early admission / retained metrics | `pytest tests/test_reservation_context.py` | 14 passed | `p2-candidate/check-context-final.log` |
| Bound original WF3 plan and incomplete initialization | `pytest tests/test_reservation_generation.py` | 7 passed | `generation-adapter-tests.log` |
| Name preview and retired unowned allocator | `pytest tests/test_experiment_allocation.py` | 9 passed | `helper-tests-final.log` |
| CLI byte preservation / templates / legacy grammar | `pytest tests/test_suggest_experiment_name.py` | 17 passed | `p2-candidate/check-suggest-final.log` |
| Final request capture and ownership registry | Request/context tests + registry assertion | 23 passed | `request-registry-final-tests.log` |
| Workflow entry points, consumers and configuration contracts | CLI/runner/metric/config/sweep tests | 263 passed | `integration-final-elevated.log` |
| Owned child termination after launcher death | `pytest tests/test_windows_job.py` | 1 passed, no skip | `windows-ownership-tests.log` |

P2 failpoints use real process exits at each durable publication boundary and repeat verified recovery
twice. Concurrent creators obtain distinct 01/02 allocations; exact-pin contention preserves one record.
Freeze cases validate actual retained v2 contracts, rather than mirroring the implementation's structure.
Context tests exercise the public runner and observe zero producer calls after incompatible requests.
The selector-mode test is a scoped policy unit with a stubbed already-validated binding lookup;
seeded generation continuation is additionally checked through real workflow execution.

## Scientific references and final candidate

Pre-change explicit reference: `reference/project`, seed 123, two realizations, a 2×2 perturbation grid
plus baseline, ten runs, 2046–2054, discharge/AET/recharge, three cores and `--notemp`.
WF1 builds the model; WF3 generates scenarios; WF4 executes all ten native runs and retained metrics.
WF0 and WF2 are omitted because no forcing choice, projection overlay or numerical method changes.
The complete explicit reference finished successfully; `reference/explicit-evidence.json` inventories
one collection, one retained simulation and 160 files. Its generator closure has 18 paths.

Pre-change automatic-seed reference adds a separate WF3-only request on identical prepared inputs:
resolved seed 2110822532, collection
`451bedccbb4c42951a220af930a0243b7b2ad7656399f73c767067a33bcef5af`.
`reference/auto-evidence.json` inventories both ready collections. Exact provider-inventory membership
and normalized source hashes are frozen in `reference/generation-code-inventory.json`.

The first candidate (`candidate/project`) completed all ten native simulations. Editing metric code
during its run changed the metric checkpoint digest; subsequent helper formatting also changed the
WF4 code closure. The guards refused continuation correctly. This root is diagnostic evidence only.
No frozen records were rewritten to bypass the guards.

Final acceptance uses a fresh root, `candidate-final/project`, seeded with 99 exact reference prepared
input files and no prior experiments or collections. WF1 is disabled because model inputs are copied
byte for byte; WF3/WF4 execute. Candidate config copies are under `candidate-final/config` and
`candidate-final/config-auto`. Numerical acceptance requires unchanged provider closure, seed resolution,
collection/revision/run IDs, every scenario's netCDF content, native CSV values and three metric tables.

The final explicit generation comparison passed: all 18 provider-inventory paths and hashes are
unchanged; seed 123, collection/revision and all ten scenario contents exactly match the reference.
Command: `python .tmp/scratchpad/t2610032349/compare_science.py
.tmp/scratchpad/t2610032349/candidate-final/project --generation-only`.
Evidence: `candidate-final/generation-compare.log` and `candidate-final/science-generation.json`.

Full explicit scientific comparison also passed: ten native CSV tables and all three retained metric
tables have exactly equal parsed values, columns, rows and types against the pre-change reference.
Evidence: `candidate-final/science-compare.log` and `candidate-final/science-explicit.json`.

The hard-parent-stop diagnostic preserved two completed staged CSVs and frozen reservation, plan,
intent and collection identities (`candidate-final/interruption.json`). It left an unfinished native
CSV. The first `--rerun-incomplete` attempt refused that file; Snakemake's ordinary failed-job cleanup
removed the unpublished partial output. The next retry succeeded, logged reuse of two staged members,
and launched only runs 03–10. No reservation-recovery action changed native responses.
This is not a claim of seamless hard-stop recovery at every boundary; native partial-output repair
remains outside the accepted implementation scope.

Copied staging probes (`staging-probes/observations.json`) confirm two existing limitations:
matching input markers reuse readable staged bytes after tampering, and restoration interruption leaves
one final output while the consumed member becomes pending on retry. Neither probe changes production
schemas or repairs outputs. Staging markers alone do not certify content integrity.

The initial non-elevated CLI/config checks were stopped after a diagnostic traceback showed Snakemake
spinning in Windows `tempfile.mkdtemp` permission retries. Their empty logs are not passes.
The same focused checks under the normal Windows token passed: 263 tests, no skips, 225.95 seconds.
`cli-trace.log` retains the environmental diagnosis; executable code was not changed to bypass it.

## Final acceptance additions

The final request/context/generation gate passed 30 tests in 45.95 seconds after the early-guard
ordering and unused-producer capture fixes. Additional acceptance checks passed: independent chosen
roots (including `active/`), one test; disabled-WF4 and retained metrics-only creation flags, three tests.
Touched Ruff checks passed; final `pixi run lint` and `pixi run format-check` passed (455 files formatted).
Formatting changes after the 30-test gate affect tests only.

The earlier 263-test CLI/configuration/consumer gate is reused for unaffected contracts. Subsequent
runtime changes only reorder admission comparison and omit unused producer inputs; those are covered
by the final 30-test gate and live changed-input/explicit-selector cases. Inspection changes have their
own 259-test gate. Documentation changes do not alter runtime inputs or numerical algorithms.

Live checks in `candidate-final/`:

- `auto-compare.log`: automatic seed 2110822532, both collection identities/revisions and all scenario
  contents match; the complete 18-file provider closure remains unchanged.
- `changed-complete-guard.log` and `changed-incomplete-guard.log`: changed perturbations refuse before
  producers, name the differing field, and recommend retained inputs or `--new-experiment`.
- `selected-complete-final.log`: selecting the same retained collection explicitly with WF3/WF1 disabled
  succeeds. All 86 previously existing experiment files remained byte-identical; nine metric files added.
- `new-experiment.log`: `--new-experiment` creates `stress_test_02`, reusing the unchanged collection.
  `science-02.log` proves all ten native tables and three metric tables equal the pre-change reference.
- `controlled-interruption.log`: creates `stress_test_03`; the Julia child is stopped after complete
  staged members and before batch restoration. Its verified julialauncher command names this task root.
  The runner remains alive, reports the expected failure and performs ordinary partial-output cleanup.
- `interruption-stress_test_03.json` captures four completed CSVs, each independently parsed and compared
  with the reference, plus reservation/intent/plan/collection hashes. A fifth member completed before the
  stop. `interrupted-children.json` records launcher/child ownership; no unrelated process was stopped.
- `controlled-resume.log`: plain retry selects the same `stress_test_03`, reuses five staged members,
  skips their native launches, executes only 06–10 and completes retained simulation and metrics.
  `controlled-resume-evidence.json` verifies all four protected CSVs are byte-identical after restoration,
  immutable bindings are unchanged and the real retained simulation reader accepts the final inventory.
- `science-03.log`: all ten native CSV tables and three metric tables exactly match the reference.
- `plain-final-noop.log`: a completed plain rerun selects 03, keeps its original ready WF3 binding and
  completes without rewriting any of 292 experiment/allocation files. `before-final-noop.json`,
  `after-final-noop.json` and `after-final-preview.json` have identical entries and hashes.
  `new-preview-final.log` advises `stress_test_04` without reserving it.

The supported interruption check passes independently of the hard-parent-stop diagnostic above.
It does not broaden the native partial-output or restoration contract.

Exact final focused commands (all pytest commands run with the normal Windows token):

```powershell
pixi run pytest tests/test_reservation_request.py tests/test_reservation_context.py tests/test_reservation_generation.py -q
pixi run pytest tests/test_reservation.py -k chosen_roots -q
pixi run pytest tests/test_reservation_context.py -k 'disabled_simulation or metrics_only' -q
pixi run python -m pytest tests/test_snapshot_project_tree.py tests/test_project_tree_inventory.py tests/test_semantic_tree_diff.py -q --basetemp .tmp/scratchpad/t2610032349/p2-candidate/pytest-inspection-01
pixi run lint
pixi run format-check
```

Inspection gate: 259 passed, no skips, 10.61 seconds. Current selection honors the inspected override
root and validates retained owners; historical maps are unchanged and unknown names/leaves stay unmapped.
The live snapshot mapped all new reservation and staging paths. Three pre-existing metric-set
`return_level_evidence.json` leaves remained unmapped; their exact paths are retained in
`p2-candidate/evidence.md` and `check-candidate-current-map.log`. No unrelated inventory expansion was made.
Documentation links: `pixi run pytest tests/test_activation_links.py -q`, 12 passed in 0.28 seconds.

Tested runtime commit: `4e409685`, built from the exact final verified source candidate. The following
P4 commit adds only the independently tested inspection scripts/tests, documentation and this evidence;
the primary task index records that commit after creation. No executable change follows these checks.
There are no file deletions, output migrations or native-response repairs in the delivered task.

Acceptance-matrix coverage, grouped by distinct check/input:

- First/default/custom/exact names, suffix grammar, gaps, tombstones, completed selection, legacy owners:
  `test_reservation.py` and `test_suggest_experiment_name.py`, synthetic owned roots in P2 fixtures.
- New flag with unchanged inputs: live 02/03; changed inputs: context public-runner test; note/pin errors:
  P2 invalid-flag and continuation tests. Independent output roots/`active/`: chosen-roots test.
- Changed complete/incomplete/pending requests: live complete/incomplete guards plus public-runner
  pending/resolved/bound cases. Producer call counts remain zero after refusal.
- Automatic seed and pending retry: real source/plan monotonic binding tests; automatic generation:
  matched pre-change/final WF3 roots. Partial initialization/generation refuses in adapter tests.
- Publication crashes and competing creators: real subprocess failpoints and ownership contention;
  paired intent/archive recovery: checked freeze fixtures, repeated recovery and corruption/link cases.
- Preview/DAG/validation: helper subprocess byte-preservation tests, final live rulegraph/dry-run and
  experiment-state inventories; all read-only selection uses the common resolver.
- Metrics-only and invalid operation flags: real retained v2 reader fixtures; unused current producer
  files/model are unavailable. Disabled WF4 plus creation refuses before allocation or producers.
- Derived metric regeneration and native integrity: final explicit-selector run plus metric-plan tests
  for missing/corrupt native responses. Resource/comment/metric changes: request projection tests.
- Native checkpoint reuse: controlled 03 interruption above; existing hard-stop/restoration limitations
  remain explicit. Folder scaffolding: 16 focused cases and companion cst-cases commit.

## Remaining batch gates and retention

The master brief defers shared-contract `test-full` and fresh all-five `test-e2e` to approved landing.
Task-local scientific checks do not discharge those batch gates. The stale baseline is not an oracle.
Keep reference, candidate, crash-fixture and test logs in this task's ignored scratch root until landing
verification and scientific comparison evidence have been retained. Native outputs are not committed.
Only verified task changes are committed; the lane remains occupied until the user approves landing.

## Retained original context and authorized landing

The [accepted design](accepted-design.md) retains its original header. Approval and capped review
identity are in the original status, recoverable through [original-context.json](original-context.json).
That identity stores repository, full commit, original parent, task ID, task-tree object and each report's
relative path separately. The pin remains reachable through ordinary merge ancestry. Retrieve a report
with `git show <task-tree>:<relative-path>`; archived variants additionally preserve exact Git and Windows
bytes. The Windows design variant matches the original G2 SHA256 exactly. No review was rewritten.

The [context archive](original-context.zip) retains directory context for all intra-task citations.
Its manifest records every member hash. Incoming live citations were searched before closure; only the
two closing notes and generated board depend on the removable task home. Existing host navigation:
`dev/reference/repo-layout.md`, linked from the root agent instructions.

User authorized merge and landing on 2026-10-10; pushing remains separate. Synchronization with main
adds its previously landed prefixed run IDs and separated run/group tables. Reservation validation now
accepts those exact prefixed IDs and rejects numeric legacy IDs under the current collection schema.
The inspection map combines verified retained owners with current group membership/metric filenames.
The all-five integration assertion expects the rapid family's fresh `experiment_rapid_01` identity.
These are compatibility adaptations to main's existing contracts; scientific algorithms are unchanged.

Combined gate results and the final landing candidate will be appended after verification.
