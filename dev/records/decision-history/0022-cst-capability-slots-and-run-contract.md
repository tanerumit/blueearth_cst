---
title: "ADR 0022 — Capability slots and a scheduler-neutral CST run contract"
Status: historical (accepted under owner arbitration)
Date: 2026-07-28
Deciders: Ümit Taner
---

# ADR 0022 — Capability slots and a scheduler-neutral CST run contract

**Current project authority:** [toolbox-architecture.md](../../reference/toolbox-architecture.md).
The `cst-run-control` skill owns the operational schema and conformance specification.
This record preserves the architectural choice and its accepted limitations; it is not a second
implementation contract or evidence that existing toolbox launches conform.

The decision originated in the Brain ADR series, proposed 2026-07-26 and accepted 2026-07-28.
It was relocated from Brain commit `fdfda23c` on 2026-09-22; identifier 0022 retains that lineage.
Condensed 2026-10-20 without changing the accepted choice or evaluating runtime adoption.

## Context and decision

The architect's former fixed HydroMT/Wflow/Snakemake toolchain mixed stable scientific
responsibilities with replaceable implementations. Directory isolation alone also lacked durable
run identity, ownership and recovery semantics.

The owner chose capability slots covering scientific transformations and human judgements,
with explicit component revisions, execution owners and separate validation authorities.
An alternative engine would fill a slot rather than require redefining the architect's responsibility.
The decision added no new engine binding.

The run contract separated immutable intent from mutable execution state. It distinguished
configuration, scientific-design and complete execution-intent identities, with versioned canonical
serialization and conformance vectors to prevent language-specific digest disagreement.
Resolved configuration and source-file bytes were not interchangeable identities.

Applicability was explicitly locational: an owner-declared **managed project root** admitted only
conforming claimed namespaces, including manual launches. Runs elsewhere were unaffected.
Existing outputs needed import or removal before management was declared.
Two conformance profiles were chosen: `provenance` for recorded terminal outcomes without resume,
and `managed` for attempts, fenced publication and checkpoint-based recovery.
Both required namespace claims; the simpler profile was not the managed schema with fields omitted.

Detailed fields, transitions, digest participation, resource compatibility matrices and validity
profiles were assigned to `cst-run-control`, not retained as a second operational schema here.
The shared skill was chosen because builders, validators, analysts and adapter authors all mutate
or interpret these records; storing the protocol solely in an architect role would leave other
participants without its rules.

## Consequential design choices

These summarize historical rationale, not instructions overriding the operational skill.

- **Atomic overlapping-namespace exclusion:** checking whether a directory appeared unused could
  admit two writers. Claims covered equality and ancestor/descendant overlap in one operation.
  A flat allocation discipline allowed a simpler manual implementation; arbitrary hierarchy needed
  a registry capable of the overlap test. Case/Unicode comparison rules could not silently alter hashes.
- **Immutable objects and one publication operation:** rename-then-inventory and inventory-then-rename
  both left a race. The accepted correction used private staging, durable content-addressed objects
  and one token-checked inventory compare-and-set. Readers resolved current outputs through that
  inventory. An old executor could leave an unreferenced object but could not publish it as current.
- **Transitions as conditional units:** state revisions made all fields of a transition commit
  together. A failed conditional write required rereading, rather than blindly retrying.
  Abandoned attempts were closed explicitly; inactivity alone did not prove abandonment.
- **Validated reuse:** file existence was insufficient. Checkpoint eligibility included interface,
  graph, component/environment and dependency identity, completeness, output digests and the
  declared validation authority. A resumed DAG could reuse several checkpoints only as a consistent,
  non-overlapping frontier; invalidation propagated downstream.
- **Resource admission beyond pairwise checks:** three claims can exceed capacity while every pair
  fits. Capacity required aggregate admission at its authority. Mutable shared caches also needed
  explicit isolation/claims; two read-only consumers were not equivalent to concurrent readers/writers.
- **Cancellation retained attribution:** artifacts could not survive under a released namespace claim.
  Tombstones retained ownership pending verified disposition, with the lifecycle gap below acknowledged.
- **Declared scientific ordering:** typed edges separated stress-test drivers from projection overlays.
  Decision criteria preceded the experiment; response surfaces preceded overlays; robustness scoring
  consumed the surface, not projection-conditioned forcing. This checked declared dependencies,
  not actual execution reads.

Costs included hashing and environment inspection, typed-graph authoring, schema/vector maintenance
and real conditional-write/fencing machinery even for a manual managed adopter.
No scheduler, database, API, service role or storage implementation was selected.

## Known limitations accepted at arbitration

The owner explicitly retained five gaps instead of enlarging the design. These qualify its benefits
and must remain visible when citing the decision. Their current operational treatment belongs to the
skill and a conforming adapter, not to an assumed completion of this historical design.

1. **`ext2-3` — orphaned resource claims.** Admission had no complete reservation lifecycle.
   A failed attempt-start transition or process death could leave a claim with no compensation;
   success/failure transitions did not release attempt/stage claims as cancellation did.
   Capacity could remain consumed indefinitely. Reconciliation was neither defined nor authorized.
2. **`ext2-4` — terminal tombstone release gap.** Release required a disposition record in a
   cancelled final state, but no legal transition could write it because cancellation was terminal.
   An adopter faced forbidden terminal mutation or indefinitely retained clean tombstones.
   Succeeded-run claim release had a related omission.
3. **`ext2-5` — declarative bottom-up auditability only.** A component could consume an undeclared
   projection or mislabel it as system input while presenting a valid graph.
   Attribution after the fact was possible; prevention was not established.
   Execution-time dependency attestation was declined to keep manual adoption feasible.
4. **`ext2-6` — operational configuration can contaminate scientific identity.**
   `scientific_design_hash` included the whole resolved `config_hash`; paths, thread counts or other
   operational fields could re-enter despite excluding their separate top-level counterparts.
   Identical experiments were not guaranteed to group across different resolved configurations.
5. **`ext2-7` — no interoperable validation-record collection.** Validation authority was declared,
   but no normative collection/serialization or artifact/checkpoint coverage rule was supplied.
   Different adopters could agree on authorities while being unable to read each other's proof
   of successful validation, particularly for stages without reusable checkpoints.

No empirical concurrency, crash-recovery, cross-language or scientific-performance result was
established by acceptance of this document.

## Alternatives considered

**A minimal owner/path/hash manifest** was insufficient for safe resume or common service semantics.
Its useful subset became the provenance profile, still including digests, graph and namespace claim.
It would otherwise suit permanently isolated, non-resumable work.

**A dedicated operational role and shared scheduler** would provide queue/service ownership but
prematurely selected an operating architecture. It remained a separate scaling decision.
Requiring concurrency semantics was not selection of a scheduler implementation.

**Keeping the fixed HydroMT/Wflow/Snakemake architecture** would require role revisions whenever
an engine changed and leave impact-model responsibilities implicit.
That alternative would fit only a toolbox permanently defined by those exact components.

## Review and original-section recovery

The internal panel raised 21 findings: seven blocking, thirteen major and one minor.
External rounds each returned seven findings: round 1 had one blocking/six major; round 2 had
two blocking/five major. The second round did not converge.
Acceptance followed owner arbitration at the two-round cap, not an independent passing review.

`ext2-1` required token-atomic publication; `ext2-2` required overlap-aware namespace claims.
The owner required mechanism corrections for those two and accepted `ext2-3`–`ext2-7` with the
limitations above. Earlier review snapshots were cited in the source Brain repository as
`75c4262e`, `29eed794` and `08d44e6f`; their availability in this project is not assumed.

The complete local pre-condensation schema prose, transitions and findings ledger are recoverable:

```text
git show e9bbd72d:dev/records/decision-history/0022-cst-capability-slots-and-run-contract.md
```

| Original section | Historical subject / current destination |
|---|---|
| Capability slots | Stable responsibilities, bindings and validation authorities; operational skill |
| Manifest contract; Scientific design and the typed stage graph | Two records and declared ordering; skill |
| Resources; Checkpoints | Admission and reusable dependency closure; skill, with accepted gaps above |
| Identity, hashes, and namespaces | Canonical digests and overlap exclusion; skill |
| State, attempts, and resume | Conditional transitions, publication and reuse; skill |
| Adoption and validation | Owner-declared root applicability and separate profiles; project architecture |
| Role-contract changes; operational schema needs a skill | Shared protocol ownership rationale above |
| Consequences / Known limitations | Five arbitrated gaps preserved above |
| Review record / Verdicts / Arbitration / Findings ledger | Counts and disposition above; full rows at pin |

Finding groups remain recoverable without duplicating their operational resolutions:

| Original IDs | Concern |
|---|---|
| `risk-3`, `architecture-1`, `repo-fit-1` | Complete capability coverage |
| `risk-1`, `architecture-2`, `ext1-2`, `ext2-1`, `ext2-2` | Atomic ownership, transitions and publication |
| `risk-2`, `architecture-4`, `ext2-5` | Typed graph and limits of bottom-up enforcement |
| `repo-fit-2`, `risk-4`, `architecture-7` | Canonicalization and executable conformance vectors |
| `architecture-3`, `risk-9`, `ext2-6` | Scientific versus execution identity |
| `risk-5`, `risk-6`, `architecture-5`, `ext1-5`, `ext1-7` | Attempts, validation authority and reuse |
| `risk-7`, `architecture-6`, `ext1-3`, `ext1-4`, `ext2-3` | Shared-resource isolation and capacity |
| `risk-8`, `ext1-1` | Objective applicability and distinct conformance profiles |
| `ext1-6`, `ext2-4` | Cancellation attribution and release gap |
| `repo-fit-3`, `repo-fit-4`, `repo-fit-5` | Skill ownership, follow-on integration and durable citations |
| `ext2-7` | Missing interoperable validation-record collection |

The [migration map](../migrations/decision-history-transition-2026-10-20.md) resolves former paths.
This record's old role bindings and closeout commands describe the original Brain context;
they do not authorize changes to present project roles or establish runtime adoption.
