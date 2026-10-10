---
verdict: revise
doc_version: design-v2.md
findings:
  - id: fast-1
    severity: major
    section: "5.2 Existing WF3 seed algorithm and exact handoff; 5.4 Recovery; 8.2 Runner parity"
    finding: >-
      The pinned-plan continuation contract lacks the execution transition from a bound WF3 create plan
      to an already-created collection. A normal first invocation pins decision=create. After WF3
      completes and WF4 is interrupted, the next WF3-enabled invocation must retain that exact plan,
      but replaying initialize_generation with it refuses the existing collection namespace.
    rationale: >-
      generation_publication.py:416-418 rejects an existing record_root or data_root in
      its create branch. generation_plan.py:649-660 normally handles completion by
      constructing a different reuse_ready plan; v2 instead requires the exact bound immutable plan.
      The specified callback runs only after _plan_quietly has already selected a plan
      (scripts/generate_scenarios.py:126-132). Neither a
      documented override before that selection nor a ready-collection execution bypass is supplied.
      This leaves the central ordinary continuation journey dependent on an unstated adapter. For an
      incomplete namespace, _plan_quietly can fail even before the callback. Partial WF3 refusal is
      pre-existing; preserving a create plan without defining its replay transitions is the new gap.
    suggested_fix: >-
      Specify the bound-plan branch before ordinary candidate plan selection/initialization. Validate
      the recorded plan, current scientific request and sources. If its collection is ready, validate
      exact collection identity, creator and seed evidence, skip create initialization and stochastic
      execution, and bind/confirm resolution without replacing the pinned plan. State the disposition
      for a valid initialized-but-incomplete collection and for interrupted initialization separately;
      unsupported existing partial states may fail with an explicit diagnosis rather than acquiring
      repair authority. Add a cheap runner test for first create, completed WF3, interrupted WF4, and
      ordinary retry with WF3 still enabled; assert the same reservation/plan and no WF3 redraw. Also
      test the pre-callback partial-namespace refusal and a completed experiment's ordinary rerun.
  - id: fast-2
    severity: minor
    section: "5.2 Plan publication seam; 6 Integration; 8.3 Automatic-seed reference"
    finding: >-
      Exact cross-revision automatic-seed equality requires preserving the generator code inventory,
      but the implementation map assigns generation_plan.py to P3 without stating this constraint.
      That module is itself fingerprinted into the automatic seed, including non-scientific edits.
    rationale: >-
      generation_plan.py:423-437 includes content_sha256(settings['code']) in seed material.
      GENERATION_CODE_ENTRIES explicitly includes generation_plan.py, and repository_code_inventory
      hashes complete normalized source bytes. A read-only inventory probe found 18 entries, including
      that module. Splitting publish_plan_pointer inside this file would therefore violate section
      8.3's identical seed-material requirement even if the generator algorithm remained unchanged.
      The design is feasible if orchestration changes stay outside this inventory; a code-hash change
      cannot simply be listed among harmless provenance differences for the auto-seed comparison.
    suggested_fix: >-
      Pin and compare the complete generation provider inventory before runtime edits and require it
      unchanged for the accepted auto-seed no-drift claim. Implement the publication/callback adapter
      outside that inventory where feasible, reusing existing canonical publication functions. If an
      inventoried edit proves necessary, report the resulting acceptance conflict to the owner before
      implementation; do not alter seed identity rules, mask hashes or refresh the reference silently.
---

# Combined risk and implementation-feasibility review

Reviewed 2026-10-10 against design SHA256
`956AF067B4A3F46B0293C03A8082DF9E902D82170D29AA2DB7F94897313CED99`.
Runtime source HEAD: `3bea47b933035a25841b8f97c2022799ae111af1`.
Requested configuration: `gpt-6-astra/high`; effective exact model and effort are not independently
observable. Runtime instructions identify the GPT-6 family only. This is the sole combined review,
with no nested delegation, implementation edits, commits or scientific executions.

The architecture is proportionate to the agreed behavior. Durable allocation history is necessary for
deleted-number non-reuse. The existing archive publisher cannot atomically publish allocation history,
creation metadata and a later simulation intent together; a small creation redo recipe is justified.
The conditional paired-freeze recipe also addresses a concrete gap: `freeze_simulation_v2` publishes
intent before archive and its existing-intent branch immediately reads the archive. Existing archive
recovery should remain the archive owner. A new database or generalized transaction service is unnecessary.

The major finding concerns an ordinary supported journey, not a demand for broader recovery. G1's seed
timing, catalog coverage and explicit recovery authority remain settled. Address fast-1 in the bounded
revision; do not reopen those decisions or add native-output repair. G2 approval and implementation
acceptance remain separate. Unexecuted acceptance checks do not themselves make the specification invalid.

## Premise checks and retained strengths

- **Selection and user intent:** the design carries the naming plan's creation/continuation, pin,
  growth, tombstone, legacy precedence, metrics-only and preview rows. Retaining original frozen
  selection spelling avoids the existing full-intent canonical comparison failure. Public runner
  parity and read-only previews are explicit. Fast-1 identifies the missing operational transition
  behind the otherwise preserved continuation row.
- **Seed timing, E4/E5:** supported by source. `build_candidate_intent` snapshots prepared historical
  climate and basin cells before deriving the deterministic seed. The source child precedes planning
  in `generate_scenarios.run_owned`. Pending source state followed by binding before stochastic work
  preserves this dependency. Experiment number must remain absent from seed material. Fast-2 qualifies
  cross-revision equality without disputing D1.
- **Catalog coverage, domain-1/E11:** resolved by specification. Request-level ordered semantic catalogs
  cover WF1, WF3, WF4 and shared preparation independently of WF3 enablement. The stated anchor,
  precedence and before-consumer checks address the reviewed bypass. This is a conservative guard,
  so unrelated entry changes can refuse continuation as expressly documented. Mutation tests remain
  implementation evidence, not a reason to reopen the domain finding.
- **Ownership, E2/E3/E12:** source supports project-wide serialization and Windows job ownership.
  Source does not establish descendant termination before competing recovery. Section 8.5 retains the
  necessary observable lifetime gate and existing unsupported-platform refusal. This task need not
  add Linux writers or managed-run fencing.
- **Publication, E8/E14:** creation commit point, orphan evidence, missing allocations, collisions and
  paired-freeze refusal/recovery are explicit. Unknown occupants are preserved. Atomic directory rename
  is a local process-crash assumption whose boundary faults remain unexecuted; power loss is excluded.
- **Native reuse, E9/E10/domain-2:** resolved by specification. Source confirms input-only staging
  markers and incremental CSV restoration. The revised claim applies only after complete staging and
  before restoration, with independent bytes and engine-launch observations. Broader staging integrity
  limitations predate this proposal; they do not authorize native-response repair.
- **Reference, E13/domain-3:** capture recipe matches rapid seed 123, two realizations, 2046-2054 and
  three native output variables. Retention of engine-ready forcing is necessary because it is `temp()`;
  the runner admits `--notemp`. The separate auto generation case and exact decoded-value comparison
  make the claim testable subject to fast-2. Data, engines, disk capacity and deterministic execution
  have not been proven here. Those are explicit pre-P2 handoff obligations, not claimed successes.
- **Domain-4:** resolved by specification. Windows writer-lifetime evidence is separated from record
  fixtures; idempotent recovery and every durable publication boundary remain required observations.

## Verification and limits

Read intake, status, v2, ledger, inventory and the authoritative domain review; read the original naming
plan and master brief from the primary checkout. Applied canonical `claim-evaluation` and its
claim-and-inference reference. Inspected live seed/planning/publication, simulation freeze, archive,
Windows child ownership, rapid configuration and temporary-forcing contracts. No web claims were needed.

Read-only probe: `pixi run python -c` used `ast.literal_eval` to read `GENERATION_CODE_ENTRIES` and
`GENERATION_INVENTORY_EXCLUDED`, then called `repository_code_inventory(Path.cwd(), entries, excluded)`.
Result: 18 entries; `generation_plan.py` was included. Of additionally inspected potential targets,
`snake_utils.py`, `simulation_record.py` and `allocate.py` were absent. This is code-inventory evidence,
not a seed or scientific execution test. `git rev-parse HEAD` and `Get-FileHash .../design-v2.md`
established the identities above. Only this review artifact was modified.

Review artifact checks passed: frontmatter parsed with `yaml.safe_load`; required finding fields,
unique IDs, verdict and document version asserted; 110-character line limit checked;
`git diff --check -- dev/tasks/t2610032349/design-runs/reservation-lifecycle/combined-review-r1.md` passed.

No blocker was waived. Approval is withheld because fast-1 is major; a precise local transition fix and
the fast-2 implementation constraint can resolve the findings without another review round or broader scope.
