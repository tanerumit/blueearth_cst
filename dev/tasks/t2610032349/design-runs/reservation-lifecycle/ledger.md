# Reservation lifecycle findings ledger

Append-only. Original findings: [domain review](internal-review-domain.md), immutable review of v1.
2026-10-10 revision: G1-approved framing and owner fast-track ruling from `status.md` govern this response.
Accepted means the design incorporates the finding; empirical implementation gates remain open.

| ID | Round | Severity | Disposition | Resolution or rationale | Doc version |
|---|---|---|---|---|---|
| domain-1 | Domain | major | accepted | [All parts below](#domain-1) | design-v2.md |
| domain-2 | Domain | minor | accepted | [All parts below](#domain-2) | design-v2.md |
| domain-3 | Domain | minor | accepted | [All parts below](#domain-3) | design-v2.md |
| domain-4 | Domain | minor | accepted | [All parts below](#domain-4) | design-v2.md |

## domain-1

- Accepted independent coverage: request-level `input_catalogs` replaces the WF3-only catalog field in
  [section 4.3](design-v2.md#43-reservation-and-early-request). It is present for WF4 with WF3 disabled,
  WF1 construction, WF3 preparation and shared WF0/WF2 input production. Separate projection catalogs
  stay excluded. Metrics-only retains existing retained-response admission.
- Accepted conservative ordered projection: full effective project catalogs retain precedence and
  upstream path/anchor semantics; comments and mapping order are excluded. Original dependency bytes
  remain captured in the transaction. One request-level field avoids competing model/generation copies.
- Accepted early producer refusal and during-invocation checks in
  [section 5.1](design-v2.md#51-admission-before-producers). Active consumers cannot read a different
  catalog from the admitted capture.
- Accepted each proposed mutation case in [section 8.2](design-v2.md#82-claim-to-check-plan): pending
  explicit-manifest/WF3-off elevation and reader/unit changes, WF1 model/forcing changes, and compatible
  comment/mapping-order edits. Also check precedence and anchor changes and dependency coverage.
- Evidence: review's WF4 chain `simulate_and_metrics.smk:75` → `wf4_ancillary_descriptor.py:332` →
  `prepare_climate_data_catalog.py:191`, and WF1 `build_model.smk:90,637,685`. Revision read-only `rg`
  confirmed project catalogs also feed WF0 and WF2 shared preparation. No mutation test has run.

## domain-2

- Accepted bounded claim: [section 2.2](design-v2.md#22-compatibility-and-recovery) separates validated
  immutable retained responses from intermediate staging and states the preservation limit beside the
  user-facing promise. E10 no longer asserts all-crash-boundary survival.
- Accepted valid-member evidence:
  [section 8.4](design-v2.md#84-bounded-interruption-evidence-and-staging-limits)
  specifies full staged completion before restoration, reader checks, pre-interruption CSV inventory and
  hashes, and observed member launch/completion records. Input-only `.ok` is expressly insufficient for
  integrity; probe evidence adds no production checksum schema.
- Accepted preservation and non-re-execution tests: identical completed-member bytes after retry,
  absence of a second engine launch, final inventory validation, and exact final native-value comparison
  against the uninterrupted candidate. Unfinished members use existing restart controls.
- Accepted separate disposition of restoration interruption and readable staged tampering: diagnostic
  probes on copies record outcomes; these remain existing unsupported staging limitations unless
  separately established. Promised-boundary or immutable-response failures block acceptance. No native
  repair scope or permission is added.
- Evidence: review's `batch_staging.py:62–110` input-only markers and individual moves; v1 E9 caveat.
  No interruption, tampering or engine-launch observation has been executed for this revision.

## domain-3

- Accepted explicit cross-revision no-drift claim and mandatory pre-P2/P3 reference in
  [section 8.3](design-v2.md#83-mandatory-matched-reference-and-no-drift-acceptance). Missing reference
  blocks runtime handoff; equal identity digests cannot discharge numerical agreement.
- Accepted feasible capture recipe: redirected rapid WF1/WF3/WF4 execution, prepared source/model
  inventories, full producer-owned run population, explicit seed 123, actual engine/environment settings,
  realized collection and downscaled forcing, native responses and immutable records. A separate auto
  generation reference tests D1 using identical prepared sources; it adds no native run obligation.
- Accepted declared comparison population: every selected rapid member, all emitted native times and
  configured variables, forcing arrays, coordinates, units/calendars, missingness and exact values.
  Auto comparison covers all collection series and seed material; its native exclusion is explicit.
  Reuse matching final e2e output; mismatched inputs cannot count as paired evidence.
- Accepted exact same-environment agreement or investigation: no opportunistic tolerance or reference
  refresh; report all exclusions, counts and numerical deltas, and require model-validator's verdict.
- Accepted separation of interrupted/uninterrupted checks in section 8.4 from cross-revision comparison.
- Evidence: `project_config_rapid_generate_scenarios.yml` specifies seed 123, two realizations and
  2046–2054; project config supplies three native output variables. Coordinator reports data-path and
  Julia-alias presence only; this does not demonstrate executable readiness. No reference or numerical
  delta has been captured, and no runtime implementation is authorized by this ledger itself.

## domain-4

- Accepted empirical gates: [section 5.4](design-v2.md#54-crash-and-recovery-matrix) removes the inference
  from lock acquisition alone to descendant inactivity. E12/E14 remain open until implementation probes.
- Accepted Windows lifetime observation in
  [section 8.5](design-v2.md#85-ownership-and-filesystem-evidence-by-platform): forced parent death,
  observed live writing descendants/grandchildren, competing recovery acquisition and no writes after
  ownership. A slow-writing case avoids vacuous success; failure blocks recovery support.
- Accepted complete durable-boundary coverage: creation, seed/pointer and paired-freeze fault injection,
  exact authoritative outcomes, repeated idempotent recovery, and preservation on refusal. Process-crash
  tests do not claim power-loss or network-filesystem guarantees.
- Accepted platform separation: Windows writer evidence is distinct from Linux synthetic record tests;
  the existing unsupported-platform writing refusal remains required and tested. No Linux workflow
  recovery claim or new cross-platform writer is introduced.
- Evidence: review's `windows_job.py:55–118` Windows mechanism and `121–135` unsupported writer refusal.
  Source inspection alone does not satisfy E12/E14. No lifetime or filesystem fault probe has run here.

## Revision verification and remaining authority

This author changed only v2 and this ledger, preserving reviewed v1, inventory, reviews and gate state.
Requested configuration is `gpt-6-astra/high` per allocation; the runtime declares GPT-6 family, with exact
effective model and reasoning effort not independently observable. No nested delegation or runtime edits.
One remaining combined review and G2 exact-byte approval belong to the driver/owner. No finding is
rejected or deferred; no new architecture decision is requested. Execution evidence remains outstanding.

## Capped combined-review revision — 2026-10-10

Source: [combined-review-r1.md](combined-review-r1.md), verdict `revise` on v2. The owner capped review
at this one combined round. The following dispositions mean incorporated into the proposed v3 contract;
they do not establish reviewer convergence, owner ratification or passed implementation acceptance.
The driver source-checks the bounded delta; the owner must ratify it at the pending final gate.

| ID | Round | Severity | Disposition | Resolution or rationale | Doc version |
|---|---|---|---|---|---|
| fast-1 | Combined r1 | major | accepted | [All parts below](#fast-1) | design-v3.md |
| fast-2 | Combined r1 | minor | accepted | [All parts below](#fast-2) | design-v3.md |

## fast-1

- Accepted execution branch before ordinary selection/initialization in
  [section 5.2](design-v3.md#52-existing-wf3-seed-algorithm-and-exact-handoff): after prerequisite source
  preparation, a bound reservation bypasses `_plan_quietly`, reads its immutable plan and validates the
  current scientific request and prepared sources. The unbound callback retains its original timing.
- Accepted ready reuse without plan replacement: existing collection/creator/archive and installed
  generator checks must establish matching collection identity, seed evidence and retained resolution.
  Skip create initialization and stochastic execution, bind/confirm resolution and continue WF4 while
  preserving the pinned plan, digest and seed, including its original `decision: create`.
- Accepted separate incomplete-state dispositions in section 5.2 and
  [section 5.4](design-v3.md#54-crash-and-recovery-matrix): valid initialized-but-incomplete WF3 and
  interrupted initialization each refuse with a distinct diagnosis before ordinary planning/callbacks.
  Both preserve their namespace/evidence and grant no repair or partial-generation resumption authority.
  Initialization is allowed only for an uninitialized bound create plan; lost initialized/resolved/reuse
  data cannot be silently recreated. Stale pointer reconciliation cannot override these state checks.
- Accepted all requested cheap cases in [section 8.2](design-v3.md#82-claim-to-check-plan): first create,
  completed WF3, interrupted WF4, ordinary WF3-enabled retry, and completed-experiment ordinary rerun.
  Assert unchanged reservation/plan/seed, validated ready handoff and no second initialization/redraw.
  Separate partial-namespace fixtures assert diagnosed pre-callback refusal and preserved evidence;
  source/creator mismatch and stale pointer cases also exercise the bound branch.
- Evidence: driver confirmed `initialize_generation` refuses existing create namespaces and receipt
  replay; `select_generation_plan` switches a ready collection to a different `reuse_ready` plan.
  Author read these functions and `run_owned` ordering at runtime HEAD `3bea47b9`. Existing
  `read_collection_v2`, creator/archive checks and `validate_installed_generator` supply the validation
  surfaces; no new collection publisher is specified. These source facts are not retry test results.

## fast-2

- Accepted full provider pin/compare in
  [section 8.3](design-v3.md#83-mandatory-matched-reference-and-no-drift-acceptance): preserve complete
  inventory membership and normalized source hashes, including transitive imports and
  `generation_plan.py`. Compare the candidate inventory before automatic-seed generation; provider
  hashes are excluded from the otherwise permitted provenance differences.
- Accepted adapter placement in [section 6](design-v3.md#6-integration-and-capability-map) and section
  5.2: keep orchestration/publication changes in planned reservation/runner files outside that inventory;
  check its import closure remains unchanged. Use existing canonical helpers and `atomic_record` for
  immutable plan publication, bind its reference, then call unchanged `publish_plan_pointer` with those
  exact plan bytes. Do not split/edit that function in the inventoried source to insert a callback.
- Accepted inventory-map clarification: P3 provider entries mean reuse/exercise, not source-edit
  permission. Section 3's consumer-inventory link points to this constraint; the immutable earlier
  inventory is preserved. No new repository file family or architecture is added.
- Accepted conflict escalation: if an inventoried edit is necessary, stop before implementation and
  report the auto-seed acceptance conflict to the owner. Do not mask hashes, alter seed identity or
  inventory exclusions, or silently refresh the reference. No such conflict was established by this
  bounded design revision; runtime feasibility and equality remain implementation gates.
- Evidence: authoritative review found 18 provider entries including `generation_plan.py`; driver
  confirmed its bytes enter seed material and captured the inventory under the pre-change reference.
  Author inspected unchanged `publish_plan_pointer` and its canonical helpers: the adapter can publish
  the immutable object before binding and then reuse that function for pointer publication without an
  inventoried edit. No code, seed computation or reference execution was changed by this author.

## V3 authority and verification limits

Only `design-v3.md` and this append-only ledger were edited. V3 changes are confined to fast-1/fast-2,
their tests, required inventory cross-references, gate wording and revision log. Prior reviewed bytes,
status, inventory and the running pre-change reference remain untouched. Effective exact model/effort
remain unverified; runtime instructions identify the GPT-6 family only. No nested delegation occurred.
The sole combined verdict remains `revise` on v2; v3 has no reviewer verdict. Owner ratification at G2,
the driver's scoped source/delta check and all implementation/scientific evidence remain outstanding.
