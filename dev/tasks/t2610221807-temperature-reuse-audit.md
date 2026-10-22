---
title: Audit temperature compatibility for retained simulation reuse
type: todo-item
status: active
effort: 1
area: toolbox
branch: fix/t2610221807
queue:
created: 2026-10-22
updated: 2026-10-22
---

> [!note] Overview
> **What changes** — Audit the temperature reader delta and restore only scientifically justified legacy simulation reuse.
> **Why it matters** — Three integrated pre-push tests fail because the audited source-boundary digest predates temperature support.
> **What it takes** — <how big the job is, and the main open question>

## Progress

- [ ] Audit the reader change and compatibility identity before changing any digest.
- [ ] Implement the justified repair and run focused regression checks.
- [ ] Land the verified repair, push main and monitor both CI platforms.

## Work location and assignment

- Owner: session-3; branch: fix/t2610221807; Herdr agents tab wA:t1, pane wA:p1.
- Role: python-engineer, implement mode; read the full canonical role and bound skills.
- No nested delegation. Other agents and user edits exist: preserve them.
- Implementation belongs in session-3; coordinator owns landing and push.

User authorized reopening Session 3 to repair the pre-push failure before the requested push and CI watch.
At main 90e8211a, the integrated normal-permission test-fast gate returned 5067 passed, 30 skipped,
1 xfailed and 3 failures, all in tests/test_simulation_reuse.py:
test_boundary_bridge_matches_audited_sources;
test_boundary_bridge_accepts_only_the_audited_transition[None];
test_completed_legacy_inventory_reuses_records_without_rewriting_bytes.
Expected _BOUNDARY_AFTER is fe2e4d92b48cbbca8a29ade215e55951dba5bfbf1417ff29ebde3845212f5cfa;
current inventory digest is 12c02734236bbb1d4fa0cf9b4538f815d0c9d196074432f11378b5baed3a1b76.
The only changed inventoried source since 76a2a874 is experiment/wflow_response_reader.py,
changed by f6841501 for temperature support. Audit actual old/new behavior and identity coverage;
do not blindly replace a hash or relax fail-closed scientific safeguards.
Retain evidence of whether existing-variable reads remain equivalent and changed model outputs are
still rejected appropriately. Add focused coverage only for uncovered risk. Update the authoritative
compatibility audit record and comments. Preserve previous supported reuse transitions if warranted.

Use existing tests and reuse the broad gate evidence for unchanged surfaces. Run the complete
simulation-reuse module plus affected response-reader/temperature checks and scoped lint/format.
Use elevated/normal Windows permissions for Snakemake tests: the restricted sandbox is confirmed to
hang at sourcecache.py -> tempfile.mkdtemp. Two fixture workers and WF4 children hit that stall in
the discarded initial gate; a full rerun with normal permissions completed with the three failures above.
Do not alter environment packages or cache permissions as a workaround.

Read AGENTS.md, dev/reference/dev-validation.md, and the full role at
BRAIN_INFRA_ROOT/artifacts/agents/python-engineer.md. Apply applicable scientific-workflows guidance
because this changes an audited compatibility fingerprint. Commit the verified scoped repair;
maintain lane-local STATUS.md and report commit, audit rationale, checks, and blockers here.
Do not land, push, or change the external Gabon case; coordinator handles integration.

## Session 3 audit and focused verification

- Audited `76a2a874` to `90e8211a`: all 22 inventoried sources checked against actual Git blobs;
  only `experiment/wflow_response_reader.py` changed. Temperature adds its native mapping and extends
  the PET declaration guard; seven existing mappings and read paths are equivalent.
- One-time comparison executed old/current readers on identical native fixture bytes: all 14 series
  (seven variables, two locations), values, NaN masks, coordinates and metadata matched exactly.
  No production legacy artifact was reopened; this is seam/migration coverage, not basin qualification.
- Exact directed pins preserve the previous supported transition and permit pre-boundary or
  pre-temperature inventories to current. Mutated/duplicate inventories and changed settings,
  environment or response requirements still refuse. Adding a temperature declaration to model TOML
  refuses through the fresh model reference for both historical inventories; retained bytes survive.
- Retained audit and commands/results: session-3 ::
  `dev/records/validation/qcrit-temperature-outputs.md`. Captured pre-temperature inventory:
  `tests/data/simulation-code-before-temperature.json` (actual normalized `76a2a874` source hashes).
- Reproduced the original audit-tripwire failure before repair. Initial focused run: 77 passed in
  55.33 s. Final run with both legacy model-output mutation cases: **78 passed in 36.39 s**, no skips:

```powershell
pixi run pytest tests/test_simulation_reuse.py tests/test_wflow_response_reader.py tests/test_temperature_outputs.py -q --junitxml=.tmp/tasks/t2610221807/focused-tests.xml
```

- Scoped Ruff lint/format, py_compile for both changed Python files, and `git diff --check` passed.
  Environment: session-3 Pixi default Python 3.12.13, normal Windows permissions for pytest; no package
  or permission changes. Existing integrated 5067-pass evidence is reused only for unchanged surfaces.
- Scratch: session-3 :: `.tmp/tasks/t2610221807/` contains audit script, synthetic native inputs and
  final JUnit. Retain until integration evidence no longer needs them.
- Blockers: none. Coordinator owns task-board commit/closure, landing, push and CI watch.


Implementation committed: 3c1afb77065ed2ea5ada8505233bf14f42bd02b5. Session-3 working tree is clean; ready for coordinator integration. No landing or push performed.
