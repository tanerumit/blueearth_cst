---
title: "ADR 0022 — Use capability slots and a scheduler-agnostic resumable CST run contract"
Status: accepted
Date: 2026-07-26
Deciders: Ümit Taner
Supersedes: none
Revisions:
  - 2026-09-09: added a section reading guide; run-contract semantics and existing anchors unchanged.
  - 2026-07-26: initial proposed design following owner selection of the scheduler-agnostic resumable-contract alternative.
  - 2026-07-28: revision r1 answering the internal review panel; renumbered to ADR 0022 after the original reservation lapsed to unrelated work.
  - 2026-07-28: revision r2 answering external review round 1 (findings ext1-1 … ext1-7).
  - 2026-07-28: accepted at gate G2 under arbitration authority; landed as this record. The external round cap (2) was reached, so the owner's rulings stand in for the reviewer verdict the cap forecloses.
  - 2026-07-28: revision r3 applying owner arbitration of external review round 2 (findings ext2-1 … ext2-7). Publication is made token-atomic through content-addressed objects and a single inventory compare-and-set, namespace claims exclude overlapping namespaces, the bottom-up claim is narrowed to declarative auditability, and five arbitrated findings are recorded as known limitations rather than closed by mechanism.
---

<!--
Relocated from the brain knowledge repository on 2026-09-22.
Source: brain @ fdfda23c, path dev/decisions/0022-cst-capability-slots-and-run-contract.md
ADR number 0022 belongs to the brain series and is retired there; it is NOT a
number in this project's dev/decisions/ series (0001-0010). Renumbering into
that series is pending. Relative links in "Related" below resolved from the
brain's dev/decisions/ and do not resolve here; several were already stale
after ADR 0023 moved artifacts/ to the brain-infrastructure repository.
-->

ADR 0022 — Use capability slots and a scheduler-agnostic resumable CST run contract

**Reading guide.** For the architectural choice, read Context, the opening of
Decision, and [Alternatives considered](#alternatives-considered). For a specific
contract, start with [Capability slots](#capability-slots),
[Manifest contract](#manifest-contract), [Identity, hashes, and namespaces](#identity-hashes-and-namespaces),
[State, attempts, and resume](#state-attempts-and-resume), or
[Adoption and validation](#adoption-and-validation). Read the full relevant
contract and [Consequences](#consequences) before implementing or auditing it.
[Review record](#review-record) is historical evidence, not a routine prerequisite.
The length preserves the standalone run contract; this guide does not replace it.

### Context

The `cst-architect` role owns CST workflow design and multi-user run planning, but
its core rule currently fixes HydroMT, Wflow, Snakemake, and climate projections
as the tool chain. That confuses stable architectural responsibilities with
today's implementation. A different simulation or impact engine would require a
role-contract edit rather than a new binding to a known responsibility.

Concurrent runs are presently separated only by working directory and output
path. There is no durable contract for identity, immutable intent, ownership,
input/config integrity, execution state, attempts, resource use, collision
detection, or resumption. This is adequate for manually coordinated single-user
work but is not auditable or safe as basin runs become concurrent.

The contract must remain implementation-neutral: a manual workspace, the current
Snakemake workflows, and a future service must be able to adopt it without
changing its semantics. It must also preserve bottom-up CST: stochastic weather
is perturbed across a scenario-neutral stress-test domain and run through the
system; climate-projection products only overlay plausibility on the response
surface and never select or drive stress-test runs.

### Decision

We will define CST architecture through stable **capability slots** and require
every run targeting a managed project root — not merely every run an operator
judges to be concurrent — to carry a two-part, scheduler-agnostic manifest:
immutable run intent plus mutable execution state. The contract governs planning,
validation, namespace claiming, active-writer exclusion, attempts, and resume.

The contract is scheduler-agnostic but not mechanism-free. It prescribes
**semantics** that every adopter must realize — atomic compare-and-set on
namespace claims and state transitions, a fencing token that bounds a single
active writer, a canonical serialization for digests, and a typed stage graph
that carries the bottom-up invariant. It does **not** prescribe how those
semantics are realized: no scheduler, storage engine, lock implementation,
database, API, or frontend is named. A directory rename, a POSIX `O_EXCL` file
creation, a database transaction, or a service-side conditional write are all
conforming realizations of the same compare-and-set.

#### Capability slots

CST architecture is described by a **stage-capability model**: a fixed set of
stable slots covering every result-affecting transformation from decision framing
through robustness evaluation, plus the optional plausibility overlay. Every run
plan names, for each applicable slot, a **component identity** (an executable
artifact or a documented procedure) with an **immutable revision**, a
configuration reference, and a **delegated owner** role.

Slots describe **both** executable components and human handoffs, and every slot
row must supply both halves. Where the capability is executed by software, the
component identity is the package/container/commit and its immutable revision.
Where the capability is a judgement exercised by a role, the component identity is
the governing procedure document (a skill or reference) and its version, and the
delegated owner is the accountable role. Neither half is optional: a slot with a
revision but no owner leaves the scientific difference between two runs
unaccountable, and a slot with an owner but no revision leaves it unreproducible.

| Stable slot | Responsibility | Current binding (component + revision) | Delegated owner |
| --- | --- | --- | --- |
| `decision_framing` | Fix decision context, performance indicators, acceptance thresholds, and the scenario-neutral perturbation domain **before** any run executes | `climate-stress-testing` + `robustness-metrics` procedures, at their recorded skill versions | `cst-architect` |
| `data_adapter` | Resolve source data and construct engine-ready model/input artifacts | HydroMT with `hydromt_wflow` where Wflow-specific, at pinned package revisions | `model-builder`, with gridded/vector prep by `geospatial-data-analyst` |
| `ensemble_generator` | Generate stochastic realizations and systematic temperature × precipitation perturbations across the scenario-neutral domain | `weathergenr`, at a pinned package revision | `model-builder` |
| `simulation_engine` | Execute the physical system model | Wflow, at a pinned engine revision | `model-builder` |
| `system_model_validation` | Judge simulated system behaviour against observations, benchmarks, and the declared acceptance criteria | `hydro-model-validation` procedure, at its recorded skill version | `model-validator` |
| `impact_model` | Transform hazards/system outputs into impact (damage, service, cost) outcomes | `not_applicable` — reason: the current hydrological CST evaluates hydrological performance indicators directly and declares no impact outputs | — |
| `performance_analysis` | Reduce system/impact outputs to performance indicators and construct response/exposure surfaces and vulnerability-domain maps | analysis code at a pinned commit, governed by `hydro-indicators` | `stress-test-analyst` |
| `robustness_evaluation` | Score the option × scenario matrix under the named robustness metric and acceptance logic | `robustness-metrics` procedure at its recorded version, plus analysis code at a pinned commit | `stress-test-analyst`, against the metric and acceptance logic named by `cst-architect` |
| `projection_overlay` | Prepare projection change factors and overlay plausibility onto an already-constructed response surface | optional; `climate-projections` ensemble products at fixed dataset revisions, or `not_applicable` when no overlay is declared | `stress-test-analyst` |
| `orchestrator` | Materialize dependencies, sequence stages, enforce the transition contract, and report execution progress | Snakemake, at a pinned workflow revision | `cst-architect`, with rule implementation by `python-engineer` |

A binding fills a slot; it does not redefine the slot. `not_applicable` must
include a reason and is valid only when the run's declared outputs do not require
that capability — `impact_model` above is the worked example. Conditional
HydroMT, hydromt-wflow, Wflow, Snakemake, weathergenr, and climate-projections
knowledge remains available to the architect for the current bindings, while
implementation stays with the delegated owners named above. Adding a future
engine means binding it to an existing slot, not extending the slot set; this ADR
adds no new engine binding.

Execution ownership and checkpoint-validation authority are **distinct halves of
a binding**. The *Delegated owner* column names who executes a capability; it
never implies who may validate its outputs. Every `capability_binding` therefore
additionally declares a `validation_authority` — the identity whose
`validator_id` a checkpoint's or artifact's `validation` record must carry to be
authorized. The mapping is normative, not inferred: where the stage graph
declares a validation stage covering a slot's outputs, the validation authority
is that validation stage's delegated owner — for `simulation_engine`, the
`system_model_validation` slot's owner, `model-validator` — so the
`model-builder` who executes a simulation is never the authority that validates
it. For every slot without a covering validation stage, the binding names either
an accountable role with a recorded procedure and version or an automated
validator with a recorded identity and procedure version. Because authority is
read from the intent's declared binding rather than derived from execution
ownership, every conforming implementation accepts and rejects the same
checkpoints.

Projection processing is deliberately **not** the ensemble-generator binding and
has its own terminal-position slot: projection change factors are optional
provenance-linked overlay inputs consumed only after response-surface
construction. The stage graph below, not the slot table, is what makes that
ordering declaratively auditable.

#### Manifest contract

The manifest has two separately serializable records joined by `run_id`.
`run-intent` becomes immutable when its state first enters `ready`;
`run-state` is the only execution-mutable record.

| Record | Minimum fields and semantics |
| --- | --- |
| `run-intent` | `schema_version`; `canonicalization_id`; globally unique, opaque `run_id`; computed `intent_hash` and `scientific_design_hash`; optional `parent_run_id`; `project_id`; `basin_id`; stable `owner_id`; declared `conformance` level (*Conformance levels*); `created_at`; `capability_bindings` for every slot of the stage-capability model, each naming its `validation_authority`; resolved `config_hash`; typed `inputs`, each with an `input_hash` and an `input_role`; exclusive `output_namespace`; `scientific_design` including its `stage_graph`; `resource_request`; and `resume_policy` |
| `run-state` | `schema_version`; matching `run_id` and `intent_hash`; monotonic `state_revision`; bounded `state`; monotonic `attempt`; `updated_at`; optional `executor_id` and `fencing_token`; actual `resource_allocation`; held `resource_claims`; append-only `attempts`; `checkpoints`; a produced-output inventory recording, per artifact, its digest and the level-specific publication record defined under *Conformance levels* — at `managed`, the `attempt` and `fencing_token` that published it; and structured `failure` when applicable |

`schema_version` selects this contract's field, digest, and transition semantics;
`project_id` and `basin_id` are stable identifiers from their owning systems,
not display labels. Timestamps are UTC RFC 3339 values. `parent_run_id` records
lineage for an explicit fork or rerun and never authorizes output reuse by
itself.

##### Scientific design and the typed stage graph

`scientific_design` is a nested, separately hashable record carrying the
perturbation domain, realization design, indicator and threshold definitions,
acceptance references, the overlay specification, a `bottom_up: true` assertion,
and a **typed `stage_graph`**. The boolean is retained as a declaration of intent,
but validation no longer rests on it: the graph is what is checked, and the
boolean must be corroborated by the graph.

The `stage_graph` declares nodes and typed edges:

- Each node carries a stable `stage_id` from the capability-slot vocabulary, a
  `stage_interface_version`, the `capability_binding` that executes it, and its
  declared input and output artifact types. The graph itself carries a
  `stage_graph_version`.
- Every input reference carries an `input_role` from a closed vocabulary:
  `system_input`, `stress_test_driver`, `evaluation_reference`,
  `decision_parameter`, or `overlay_input`. One artifact may not carry two roles
  within a single run.
- Each edge is typed by the `input_role` it satisfies, so the graph — not a label
  attached to an artifact — records how each product is consumed, and every input
  a stage consumes must be **declared** as a typed edge. The graph is the run's
  own claim about its execution, checked structurally rather than observed at
  execution time.

Required ordering, checked as **reachability over the declared graph**:

1. `decision_framing` has no incoming edge from any executed stage: indicators,
   thresholds, and the scenario-neutral perturbation domain are fixed before
   execution.
2. `ensemble_generator` accepts only `system_input` and `decision_parameter`
   edges. Every `stress_test_driver` artifact must be reachable from
   `ensemble_generator` and from no other producer.
3. `simulation_engine` and `impact_model` consume only `stress_test_driver`,
   `system_input`, and `decision_parameter` edges.
4. `performance_analysis` precedes `projection_overlay`: the response/exposure
   surface is a declared output of `performance_analysis` and a declared input of
   `projection_overlay`, and `robustness_evaluation` consumes the surface rather
   than the overlay.
5. An `overlay_input` artifact may appear **only** on edges terminating at
   `projection_overlay`. Any other consumer of an `overlay_input` artifact is
   rejected — including `performance_analysis`, so the response surface itself
   cannot be projection-conditioned, and `robustness_evaluation`, which consumes
   the surface rather than the overlay.
6. `projection_overlay` is terminal with respect to the stress test. There is
   **no directed path** from `projection_overlay`, or from any node consuming an
   `overlay_input` artifact, to `decision_framing`, `ensemble_generator`,
   `simulation_engine`, or `impact_model`.

Rules 5 and 6 are the machine-checkable form of the projection-overlay boundary
**as declared**. Rule 5 confines the artifact to a single legitimate consumer;
rule 6 closes the indirect route through any intermediate node. A run whose
declared graph routes a projection product into perturbation selection fails
validation, because the routed artifact must be declared as a typed edge and any
path from an overlay artifact into a driver-producing stage is rejected.

What this establishes is **declarative auditability, not execution-time
enforcement**, and this ADR claims no more. Validation checks the declared graph,
not the bytes a component actually read: a run that consumes a projection product
it omitted from its graph, or that types an overlay artifact as `system_input`,
can still present a structurally valid graph carrying `bottom_up: true`. That is
a false declaration — attributable after the fact to the declaring role, at a
specific artifact on a specific edge, which is a substantial advance over an
unfalsifiable global boolean, but it is not an observation of execution. The
stronger alternative, requiring every adapter to emit an execution-time
consumed-dependency attestation keyed by stage and artifact digest, was weighed
and rejected: it would raise the adapter floor past what a manual workspace can
meet and so exclude the very adopters this contract must keep conformant. The
residual exposure is recorded under *Consequences* → known limitations.

##### Resources

`resource_request` expresses node-local demand in portable quantities (CPU count,
memory bytes, optional wall-time seconds and accelerator count) plus a list of
`shared_resources`. A shared resource is a record, not a bare key:

| Field | Semantics |
| --- | --- |
| `resource_id` | Namespaced stable identifier `<authority>/<name>` (for example `project:rhine/forcing-cache`). Names are comparable only within an authority. |
| `access_mode` | `shared_read`, `shared_write`, or `exclusive`. |
| `quantity`, `unit` | Requested amount and unit where the resource is capacity-limited; omitted for purely exclusive resources. |
| `capacity_authority` | Where total capacity is declared, so oversubscription is decidable rather than a matter of opinion. |
| `claim_scope` | `run`, `attempt`, or a `stage_id` — the interval over which the claim is held. |

Access-mode compatibility for two concurrent claims on the same `resource_id`
is a **complete matrix** — no pair is left undefined:

| | `shared_read` | `shared_write` | `exclusive` |
| --- | --- | --- | --- |
| `shared_read` | compatible | conflict¹ | conflict |
| `shared_write` | conflict¹ | conflict¹ | conflict |
| `exclusive` | conflict | conflict | conflict |

¹ Compatible **only** when the resource's authority explicitly provides the
requisite isolation — snapshot or transactional read semantics for
`shared_read` × `shared_write`, transactional or serialized write coordination
for `shared_write` × `shared_write` — and each benefiting claim records the
granted isolation and its authority reference. By default `shared_write`
conflicts with `shared_read`: a mutable cache being modified while another run
reads it is a conflict, not permitted concurrency, because the reader would
otherwise observe a changing resource or mixed versions with no contract
violation. `shared_read` × `shared_read` is the only unconditionally compatible
pair; `exclusive` admits no exception.

Capacity is an **aggregate** property, never a pairwise one: three claims can
exceed a declared capacity even when no pair does, so no pairwise predicate can
decide admission. Admission of a capacity-bearing claim is therefore one atomic
compare-and-set at the `capacity_authority` over its current holder set and
declared capacity: the claim is admitted only if the summed `quantity` of live
claims plus the request remains within capacity, evaluated atomically with
respect to concurrent admissions — the same primitive class as the namespace
claim. Validity requires the aggregate quantity of all live claims for each
`resource_id` to remain within its declared capacity. Mode conflicts are
mechanically detectable from two manifests alone; capacity admission is
decidable only at the authority, which is why it is the authority's CAS and
never a manifest comparison. Acquisition ordering,
queueing, and release stay adopter mechanisms; `run-state.resource_claims`
records what the current attempt actually holds, together with the
`fencing_token` that authorizes it. A read-only input cache is an input, not a
shared resource; a mutable cache is a `shared_write` resource and must be
claimed.

`resource_allocation` records what an executor actually supplied. `owner_id`
denotes accountable run ownership; `executor_id` denotes the human or service
performing the current attempt. Neither implies a queue or scheduler.

##### Checkpoints

`resume_policy` is one of `never`, `restart_attempt`, or
`from_valid_checkpoint`, with a positive `max_attempts`.

A checkpoint is a record carrying: `checkpoint_id`; the completed `stage_id` with
its `stage_interface_version` and the `stage_graph_version` under which it ran;
the `source_attempt` that produced it; the producing `capability_binding`
revision **and** an `environment_digest` over the resolved runtime environment
including transitive dependencies; a complete `dependency_closure` — every
intent-resolved input digest and upstream checkpoint the stage actually consumed;
output digests; a `completeness` status (`complete` or `partial`); and a
`validation` record naming the validating authority (`validator_id`), the
procedure and its version, and the outcome.

A checkpoint is reusable only when **all** of the following hold:
`stage_graph_version` and `stage_interface_version` match the current intent;
every entry of `dependency_closure` recomputes against the immutable intent or
against an already-reusable upstream checkpoint; the producing binding revision
and `environment_digest` match the intent's bindings; `completeness` is
`complete`; the referenced artifacts still validate against their digests; and
the `validation` record carries a passing outcome whose `validator_id` matches
the `validation_authority` the current intent's binding declares for that stage
(*Capability slots*). Validation authority is never inferred from execution
ownership: `simulation_engine` checkpoints are validated under the
`system_model_validation` slot by `model-validator`, not by the `model-builder`
who executed them, and an automated validator is authorized only when the
binding names it with a recorded identity and procedure version. Because the
authority is a declared field of the immutable intent, the same checkpoint is
accepted or rejected identically by every conforming implementation. Successful
file existence never implies validation.

Invalidation is explicit and downstream-transitive: when a checkpoint becomes
unreusable, every checkpoint whose `dependency_closure` reaches it becomes
unreusable in the same evaluation, and the artifacts they cover lose reusable
status together.

#### Identity, hashes, and namespaces

`run_id` is assigned once and never reused, even for identical intent.

##### Canonicalization is part of the schema

Canonicalization is **normative and versioned**, not a producer convention. Each
`schema_version` fixes exactly one canonicalization, named by
`canonicalization_id` in the intent record so a reader knows which rules apply
before it recomputes anything. For `schema_version` 1 the canonicalization is
`cst-canon/1`:

- **Canonical data model.** The JSON data model restricted to objects, arrays,
  strings, integers, booleans, and null. Serialization is RFC 8785 (JSON
  Canonicalization Scheme): UTF-8, no insignificant whitespace, object keys
  ordered by UTF-16 code unit.
- **Numbers.** Binary floating-point values are **forbidden** in hashed fields.
  Integers serialize as JSON integers; every non-integral quantity is a decimal
  **string** in a fixed, schema-declared precision. This removes the
  float-formatting divergence between Python, R, Julia, and hand-written YAML
  rather than trying to specify it away.
- **Strings.** Unicode NFC-normalized before serialization.
- **Paths and URIs.** Paths are POSIX-separated, relative to a declared root,
  with no `.` or `..` segments and no drive letters or backslashes. URIs are
  RFC 3986-normalized with uppercase percent-encoding. A path is an identifier
  for a location, never an identity for content.
- **Presence.** An absent optional field is an omitted key; explicit `null` is a
  distinct value meaning "known to be absent" and is never used interchangeably.
  Empty arrays and objects are serialized as such.
- **Collections.** Every array in the schema is declared either `ordered` (order
  is semantic; `attempts` is the canonical example) or `set` (order is not
  semantic; `inputs`, `shared_resources`, and stage-graph edges are). A `set`
  array is sorted by its schema-declared sort key before serialization.
- **Secrets.** Fields marked `secret` in the schema are excluded from every
  digest and must never be written into a manifest at all; credentials appear
  only as opaque reference identifiers.
- **Binding revisions.** A `revision` must be an immutable identifier — a commit
  SHA, a content digest, or an immutable registry digest. A mutable tag, branch
  name, or version range is not a revision and fails validation. Configuration
  includes are content-addressed and inlined by content before hashing.
- **Digest representation.** `sha256:` followed by lowercase hex.

Each `schema_version` ships **conformance vectors**: worked `run-intent` and
`run-state` fixtures with their expected `config_hash`,
`scientific_design_hash`, and `intent_hash`. An adopter that cannot reproduce the
vectors is non-conforming and must not exchange manifests. The vectors are the
executable definition of the canonicalization; this prose is its rationale.

##### Which fields enter which digest

Three digests, with explicitly disjoint purposes and explicitly stated inputs:

| Digest | Computed over | Explicitly excluded |
| --- | --- | --- |
| `config_hash` | The fully resolved configuration document — defaults expanded, includes inlined by content — canonicalized. Not the source file's bytes. | Comments, formatting, include paths, secrets |
| `scientific_design_hash` | The canonicalized `scientific_design` subtree (perturbation domain, realization design, indicator and threshold definitions, acceptance references, overlay specification, `stage_graph`), plus `config_hash`, plus the science-bearing `capability_bindings` with revisions (`decision_framing`, `data_adapter`, `ensemble_generator`, `simulation_engine`, `impact_model`, `performance_analysis`, `robustness_evaluation`, `projection_overlay`), plus the typed `inputs` with their roles and hashes | `run_id`, `created_at`, `parent_run_id`, `owner_id`, `conformance`, `output_namespace`, `resource_request`, `resume_policy`, and the `orchestrator` binding |
| `intent_hash` | The entire canonicalized `run-intent`, including `scientific_design_hash` | `run_id`, `created_at`, and `intent_hash` itself |

`intent_hash` is deliberately **not** narrowed: it remains the identity of the
full execution intent, and it is what `run-state` must match. `scientific_design_hash`
is the separate, stable answer to "are these two runs the same experiment?" Two
runs that differ only by owner, namespace, resource request, resume policy, or
orchestrator binding — a manual run, a Snakemake run, and a future service run of
the same experiment — share a `scientific_design_hash` while having different
`intent_hash` values. That is what makes reruns groupable and makes a scientific
change distinguishable from an operational relocation; `parent_run_id` continues
to record lineage but is not an equivalence key.

Each `inputs` entry identifies the logical input, its `input_role`, and a content
digest; an immutable upstream identifier may supplement but never replace the
checksum. Paths and modification times are never sufficient identities.

##### Namespace ownership is an atomic claim

An `output_namespace` is exclusively owned by one `run_id`, and ownership is
established by an **atomic claim**, not by an observation. Exclusion on the
exact key alone would be insufficient: concurrent claimants targeting
`basin/run` and `basin/run/output` would each find their own key unowned while
authorizing writes into one intersecting tree. Identity and overlap are
therefore both defined normatively.

**Canonical namespace identity.** A namespace is identified by its **canonical
key**: the segment sequence from the managed project root to the namespace,
canonicalized by the path rules of the declared `canonicalization_id`
(POSIX-separated, NFC-normalized, no `.` or `..` segments, no drive letters or
backslashes), with symbolic links resolved before canonicalization. That
deterministic form is what `output_namespace` stores and what enters
`intent_hash`, so it is identical across adopters and the conformance vectors
stay reproducible. A managed root whose medium folds case or Unicode
normalization must declare that folding in its managed-root declaration; the
declared folding governs **claim-time overlap comparison only**, never a hashed
value, so two canonical keys the medium would map onto one location cannot both
be claimed.

**Atomic exclusion over overlaps.** A candidate key K conflicts with a live
claim L when K equals L, when K is a proper prefix of L (K is L's ancestor), or
when L is a proper prefix of K (K is L's descendant). The claim is one
compare-and-set at the **project-root claim authority** over its live claim set:
it succeeds only if no live claim conflicts with K in any of those three senses,
evaluated atomically with respect to concurrent claimants, and on success it
durably records `run_id`, `owner_id`, `intent_hash`, and the claim time. Exactly
one concurrent claimant can succeed. Tombstoned claims (*Transition operations*)
count as live for this test. Sub-locations inside a claimed namespace — the
object store, attempt-private staging, and quarantine — belong to that claim and
are never separately claimable.

**A won claim is a precondition of `planned → ready`.** Two planners that both
observe an empty namespace can no longer both proceed: one CAS succeeds, the
other fails planning with `namespace_claimed` and must either target a different
namespace or abandon. Planning also fails if the namespace is unclaimed but
contains outputs with no matching manifest.

The contract specifies the semantics, not the mechanism, and a managed root
declares which of two conforming disciplines it uses. Under the **registry**
discipline the root holds a claim registry and evaluates the prefix test inside
one serialized operation — a unique-constraint insert over a normalized key set,
a conditional if-none-match write, a database transaction. Under the **flat
allocation** discipline the root declares a single allocation directory and
admits an `output_namespace` only as its immediate child, so every key shares
one depth, no prefix relation between two keys is possible, distinct keys are
disjoint by construction, and `O_EXCL` creation of a claim file at the exact key
is a complete realization — the cheap path that keeps a manual workspace
conforming. A root whose importable legacy outputs do not fit the flat grid
(*Objective adoption trigger*) declares the registry discipline or evicts them.
Under either discipline the operation must be atomic with respect to concurrent
claimants and durable before `ready` is recorded.

A claim is released only when the run reaches a terminal state, every published
and uncovered artifact in the namespace has been removed or quarantined under
verification, and its owner explicitly releases it — or when an authorized owner
reassigns it; expiry is never inferred from inactivity, and cancellation of a
run with surviving artifacts converts the claim to a tombstone rather than
releasing it (*Transition operations*). Resuming the same `run_id` retains its claim. Re-running
or forking creates a new `run_id` and a new namespace and records `parent_run_id`;
equality of scientific inputs — even an identical `scientific_design_hash` — does
not permit namespace sharing. Read-only input caches must be outside run output
namespaces and appear as inputs; mutable shared caches are shared resources
(above) and are claimed as such.

#### State, attempts, and resume

The only states are `planned`, `ready`, `running`, `succeeded`, `failed`, and
`cancelled`:

`planned → ready → running → succeeded | failed`, with `failed → ready` allowed
only when `resume_policy` is not `never` and `attempt < max_attempts`, and
`cancelled` reachable from any non-terminal state. `succeeded` and `cancelled`
are terminal; further work requires a new child run. This section defines the
`managed`-level lifecycle; a `provenance` run follows the reduced lifecycle
defined under *Conformance levels*.

##### Every transition is a single conditional write

`run-state` carries a monotonically increasing `state_revision`. Every transition
is one **atomic compare-and-set against the exact `state_revision` the writer
read**: all of the transition's field changes apply together or none do, and the
write fails if `state_revision` has advanced. A writer that loses the CAS
re-reads and re-evaluates its preconditions; it never retries blindly.

The transition, not its constituent field updates, is therefore the unit of
atomicity. This removes the partially-applied states the panel identified: there
is no observable moment in which `attempt` has been incremented but the attempt
record has not been appended, in which `state` is `running` with no executor, or
in which two executors have allocated the same next attempt number — the second
CAS fails. Adopters realize this with the same class of primitive as the
namespace claim.

##### Transition operations

| Transition | Preconditions | Postconditions, applied atomically |
| --- | --- | --- |
| `planned → ready` | every check in *Adoption and validation* passes; the namespace claim is held by this `run_id`; intent frozen and `intent_hash` computed | `state = ready`; intent immutable from here; `state_revision` incremented |
| `ready → running` | `state = ready`; `attempt < max_attempts`; required resource claims acquired | `attempt` incremented (it is `0` before the first attempt); a **new** `fencing_token` minted, strictly greater than every token previously issued for this run; an attempt record appended carrying `attempt`, `executor_id`, `started_at`, `resource_allocation`, `resume_mode`, that attempt's `fencing_token`, and — when resuming — `resumed_from_checkpoints`; `state = running` |
| `running → succeeded` | `state = running`; the writer presents the current `fencing_token`; all declared outputs present with recorded digests; every applicable slot's validation record present and passing | attempt closed with `outcome = succeeded` and `ended_at`; output inventory finalized; `state = succeeded`; fencing token retired |
| `running → failed` | `state = running`; the writer presents the current `fencing_token`, **or** an authorized `owner_id` closes an abandoned attempt | attempt closed with `outcome = failed`, `ended_at`, and structured `failure` (`reason`, `stage_id`, `detail`); fencing token retired; `state = failed` |
| `failed → ready` | `resume_policy ≠ never`; `attempt < max_attempts`; uncovered outputs quarantined | `state = ready`; `state_revision` incremented |
| any non-terminal `→ cancelled`, **no artifacts** | requested by an authorized `owner_id`; the output inventory is empty and the namespace is verified free of attempt products | any open attempt closed with `outcome = cancelled`; fencing token retired; resource claims released; namespace claim released; `state = cancelled` |
| any non-terminal `→ cancelled`, **artifacts exist** | requested by an authorized `owner_id` | any open attempt closed with `outcome = cancelled`; fencing token retired; resource claims released; namespace claim converted to a **tombstone** bound to this `run_id`; `state = cancelled` |

Attempt records are append-only; a closed attempt is never rewritten. Explicit
cancellation is available from `planned` and `ready` as well as `running`, so a
run abandoned before execution has a terminal state rather than lingering as an
un-releasable namespace claim.

Cancellation never leaves published or uncovered artifacts under a released
claim. Immediate release is available only when nothing was ever produced —
cancellation from `planned`, or from `ready` or `running` before any
publication. Otherwise the claim converts, in the same atomic transition that
retires the token, to a **tombstone**: a terminal claim that keeps the namespace
bound to the cancelled `run_id`, unclaimable by any new run, with its artifacts
still attributed to the cancelled manifest — so a later run can neither mistake
stale products for current outputs nor overwrite artifacts the cancelled
manifest still references. The owner may release a tombstone only after every
published and uncovered artifact has been removed or quarantined and that
disposition has been verified and recorded in the cancelled run's final state.

##### Fencing and active-writer exclusion

The `fencing_token` minted at `ready → running` is the run's single-writer
authorization. Every publication of an output artifact or checkpoint into the
output namespace, and every mutation of `run-state`, must present the current
token. A write carrying a retired or lower token is **rejected**, and because the
output inventory records the token that published each artifact, a rejected or
late write is auditable after the fact.

A token is only as strong as its check, and a plain filesystem checks nothing:
an `O_EXCL` claim file cannot stop a live, already-superseded process from
writing directly into an ordinary output directory. Separating *writing* from
*publication* is necessary but not sufficient, because an atomic rename and an
inventory CAS are still two operations: rename-then-CAS lets a superseded
executor overwrite active bytes before its CAS fails, and CAS-then-rename can
leave the inventory pointing at bytes that were never written, while token
retirement races the gap between them. The contract therefore removes the second
operation instead of ordering it. **Final artifacts are immutable and
content-addressed, and publication is the inventory compare-and-set alone.**

A conforming `managed` realization commits an artifact in exactly three steps,
in this order:

1. **Write** the bytes into an **attempt-private staging location** — a
   sub-location of the namespace keyed by attempt and token.
2. **Seal** them into the namespace's **object store**, a write-once
   sub-location addressed solely by content digest, and make them durable. An
   object is never overwritten: sealing bytes whose digest already exists is a
   no-op, so a superseded executor's seal cannot alter anything a live attempt
   resolves. Sealing needs no token check precisely because the name is the
   content.
3. **Publish** by one compare-and-set on `run-state` that adds the artifact's
   inventory entry — logical name, digest, `attempt`, `fencing_token`. The CAS
   predicate conjoins the observed `state_revision` with the presented token
   being the record's current, live token, so a retired or lower token fails the
   predicate and the entry is never written.

Token validation, promotion, inventory update, and token retirement are
therefore all predicates or effects of a compare-and-set on the single
`run-state` record, serialized against one another by `state_revision`. No
second storage mutation remains to race: the bytes are durable and immutable
before the CAS, and the CAS is the only act that makes them current. Readers,
resumers, and validators resolve *current* artifacts through the inventory and
verify their digests, never by listing the namespace; a materialized path view
of the inventory is a derived convenience, never authoritative. Committing an
inventory entry before its object is durable is **non-conforming**, as is any
realization in which publication mutates a location a concurrent reader resolves
as current.

Crash recovery follows from that prescribed commit order, which is why the order
is prescribed. A crash *before sealing completes* leaves staged bytes carrying no
digest name and no reference, quarantined at the next `failed → ready`. A crash
*between sealing and the CAS* leaves a durable unreferenced object that is not
current and cannot be read as a result; re-publishing after resume is idempotent,
because re-sealing the same bytes yields the same object name. A crash *during
the CAS* either committed or did not and is recovered by re-read (*Recovery from
an interrupted transition*): if it committed, step 2 guarantees the referenced
bytes are already durable, so the inventory can never point at missing or stale
content; if it did not, the previous case applies.

Objects that no inventory entry references are **unreferenced, not uncovered**:
they need no quarantine, because inventory resolution already makes them
non-current, and an adopter may collect them once no attempt can still reference
them. The *uncovered* status defined under *Recovery from an interrupted
transition* and the quarantine duty under *Resume* apply to materialized path
views and to any bytes in the namespace outside the object store. **Direct
executor writes into the active namespace are non-conforming** and leave exactly
that residue, so they stay detectable, and resume verifies digests before any
reuse.

This closes the superseded-executor hole. When an owner closes an abandoned
`running` attempt as `failed` with reason `interrupted`, the token is retired in
that same atomic transition, so a previous executor that is still alive can no
longer publish anything: its publication CAS fails the token predicate rather
than racing the new attempt, and whatever it sealed remains an unreferenced
object. Staleness *detection* — deciding an attempt is abandoned — remains an
adopter concern and may be a human judgement; staleness *consequences* are not,
because token retirement is contractual.

##### Recovery from an interrupted transition

Because each transition is a single CAS, an interrupted transition either
committed or did not, and recovery is a re-read: the reader observes
`state_revision` and takes the recorded state at face value. Two residual cases
are defined explicitly:

- **An open attempt whose executor is gone.** `state = running` with an unclosed
  attempt record. Only an authorized `owner_id` may close it, as `failed` with
  reason `interrupted`, which retires the fencing token. The contract never
  infers this from a timeout.
- **Artifacts with no live provenance.** Any artifact in the output namespace
  whose recorded publishing `fencing_token` is absent, retired, or lower than
  that of the most recent successful attempt is **uncovered**.

##### Resume

`failed → ready` requires that uncovered outputs, and every output not covered by
a reusable checkpoint, be **quarantined** — moved to a retained but non-active
sub-location of the namespace, or otherwise durably excluded from being read as
current — before the next attempt executes. Quarantine is retention, not
deletion: the failed attempt's products stay auditable.

The new attempt records `resume_mode` (`restart_attempt` or
`from_valid_checkpoint`) and, for the latter, `resumed_from_checkpoints`: the
canonically sorted set (a `set` array under the canonicalization) of checkpoint
IDs forming the **resume frontier**. The stage graph is a DAG, so several
independent branches may each contribute a reusable checkpoint; recording only
one would force a conforming implementation either to recompute reusable
branches or to reuse them without recording that fact — both wrong. The selected
frontier must be: **individually reusable** — every member satisfies every
condition in *Checkpoints*, including, by the transitive-invalidation rule, a
fully reusable upstream closure; **dependency-consistent** — where one member's
`dependency_closure` reaches a stage another member covers, that closure entry
must resolve to the selected member, so the frontier never mixes two different
checkpoints' versions of one stage's output; and **non-overlapping** — no stage
output is supplied by more than one member. Every artifact the resumed attempt
reuses must be covered by a frontier member or its dependency closure;
everything else is recomputed. What a resumed attempt actually reused therefore
remains a recorded fact rather than an inference drawn from the filesystem, and
resume never mutates intent and never reuses an artifact it cannot verify.

#### Adoption and validation

##### Objective adoption trigger

Applicability is **not** decided by whether an operator judges their run to be
"concurrently managed". That test is circular — an unmanaged manual run has
neither the states nor the enforcement point the test refers to — and it permits
a mixed estate in which legacy and managed runs collide unseen. The trigger is
therefore locational:

> **Every run whose `output_namespace` lies under a managed project root must
> hold a namespace claim — regardless of how it is launched, by whom, or whether
> any other run is active at the time.**

A project root becomes *managed* by an explicit recorded declaration from its
`project_id` owner. From that moment the rule is objective and checkable by
inspecting the root, not by inferring operator intent. Its consequences:

- A manual launch into a managed root is either a conforming run or a violation.
  There is no third category of "still isolated enough".
- Pre-existing outputs must be **imported or evicted before** a root is declared
  managed. An import registers a minimal `run-intent`/`run-state` pair at the
  `provenance` conformance level, marked as an import, and claims the namespace those outputs occupy,
  so legacy results stay readable and citable while their namespaces stop being
  claimable by new runs. Outputs that cannot be imported move out of the managed
  root.
- Runs outside every managed project root are unaffected and need no manifest.

##### Conformance levels

Two levels, so single-user provenance is not forced to carry concurrency
machinery it does not need, while a mixed estate stays collision-safe. The
intent's immutable `conformance` field declares the level, and each level has
its **own state schema and validity profile** — `provenance` is not the
`managed` schema with fields left blank, because the managed publication rules
(attempt numbers, fencing tokens, token-based coverage) cannot be satisfied by a
run that has none of those concepts, and requiring them of it would force
adopters to reject every provenance manifest or invent incompatible synthetic
token conventions:

| Level | Requires | Permits |
| --- | --- | --- |
| `provenance` | full `run-intent` with all three digests and the stage graph; an atomic namespace claim; a `run-state` recording the terminal outcome and the output inventory with provenance-level publication records | omitting attempts, checkpoints, fencing, resource claims, and resume; `resume_policy` must be `never` |
| `managed` | everything in `provenance`, plus CAS state transitions, fencing tokens, attempt records, managed publication records, resource claims, and checkpoint validation | resume, retries, and concurrent operation |

**Publication records are level-specific.** At `managed`, an inventory entry
records the artifact digest plus the `attempt` and `fencing_token` that
published it, and the fencing, staged-publication, and uncovered-artifact rules
of *State, attempts, and resume* apply in full. At `provenance` there are no
attempts and no tokens, and the schema does not require inventing them: an entry
records the artifact digest, the publishing `executor_id` (or `owner_id`), and
`published_at`, and **coverage is defined by the claim, not by a token** — an
artifact is covered when it appears in the terminal inventory written by the
holder of the namespace claim. The same validity sentence holds at both levels —
no artifact in the namespace may be uncovered — evaluated under the level's own
coverage definition.

**The lifecycle is level-specific.** A `provenance` run moves
`planned → ready → succeeded | failed | cancelled`: the same planning checks and
the same namespace-claim precondition gate `ready`; execution itself is
unrecorded; a single, final terminal write records the outcome and the complete
inventory. There is no `running` state, no attempt counter, and no
`failed → ready` — `failed` is terminal at this level. The transition machinery
of *State, attempts, and resume* is the `managed` lifecycle.

The **namespace claim is required at both levels**. That single requirement is
what makes the estate collision-safe even where provenance-only single runs
persist, because every namespace in a managed root has exactly one recorded
owner. A `provenance` run cannot resume; upgrading it to `managed` requires a new
`run_id`.

##### Adopters

A manual workspace may store one intent and one state YAML/JSON file beside its
exclusive output directory, claim the namespace by `O_EXCL` creation of a claim
file, and update transitions explicitly; at the `managed` level it writes each
attempt into an attempt-private staging directory, seals outputs into the
namespace object store under their digests, and publishes them only through the
token-checked inventory compare-and-set, never by writing directly into the
active namespace (*Fencing and active-writer exclusion*). Current Snakemake workflows may
implement the same contract through wrapper/rule adapters. A future service may
store the records in other media, but must preserve the same fields, digests,
immutability boundary, atomic-claim and CAS semantics, transition rules, and
exportable representation.

##### Validity

Validity is evaluated under the run's declared `conformance` level: a core
profile applies at both levels, and the concurrency profile applies additionally
at `managed`. A run is valid only when every rule of its profile holds.

**At both levels:**

- the `schema_version`, `canonicalization_id`, and `conformance` level are
  supported, identifiers are present, and the state's `run_id`/`intent_hash`
  match the immutable intent;
- every capability slot of the stage-capability model is bound or explicitly
  `not_applicable` **with a reason**, and every binding records an immutable
  revision, a delegated owner, and a `validation_authority`;
- `config_hash`, `scientific_design_hash`, `intent_hash`, and every input digest
  recompute under the declared canonicalization, and the validator reproduces
  that `schema_version`'s conformance vectors;
- the namespace claim is held by this `run_id` and was acquired by
  compare-and-set before `ready`;
- the `stage_graph` satisfies all six ordering rules **evaluated as
  reachability** over the declared graph, every input a stage consumes is
  declared as a typed edge, no `overlay_input` artifact is declared as consumed
  by anything other than `projection_overlay`, and no artifact carries two
  `input_role`s. `bottom_up: true` is required but is never sufficient, and this
  check is declarative — it audits the declaration, not the execution
  (*Scientific design and the typed stage graph*);
- every artifact in the output inventory carries its level's publication record
  (*Conformance levels*), and no artifact in the namespace is uncovered under
  that level's coverage definition.

**Additionally at `managed`:**

- no two concurrently held resource claims conflict under the access-mode
  matrix, every capacity-bearing claim was admitted by its `capacity_authority`'s
  atomic compare-and-set, the aggregate quantity of live claims for each
  `resource_id` remains within its declared capacity, and every claim an active
  attempt relies on is recorded;
- state and attempt transitions are legal, each was applied as a single CAS
  against the observed `state_revision`, attempts are monotonic and within
  policy, and an active attempt has an executor, an allocation record, and a live
  fencing token;
- every published artifact was promoted through the token-checked publication
  step — never written directly into the active namespace;
- every reused checkpoint satisfies all reusability conditions, including
  `environment_digest`, complete `dependency_closure`, a dependency-consistent
  and non-overlapping resume frontier, and a passing `validation` record from
  the `validation_authority` the intent's binding declares.

#### Role-contract changes

`cst-architect` remains one orchestration role with its current handoffs. Its
Scope, Rules, Workflow, Verification, and Output contract will:

- map each pipeline stage to a stable capability slot, then name the selected
  binding, its immutable revision, and the existing execution/validation owner;
- treat current HydroMT/Wflow/weathergenr/Snakemake/climate-projections
  components as conditional bindings, not the role's universal contract;
- emit and validate immutable intent, and win the namespace claim, before any
  run targeting a **managed project root** enters `ready` — the locational
  trigger above, not a judgement about whether the run feels concurrent — and
  require legal CAS state/attempt updates for sequencing and integration;
- retain per-run isolation while replacing directory separation alone with
  identity, digests, atomic namespace ownership, fenced writers, typed resource
  claims, and resume policy; and
- state explicitly that climate projections provide plausibility overlays
  occupying a terminal stage, while stochastic perturbations provide stress-test
  forcing.

No operational role is added. Role frontmatter/body skill and handoff lists
remain closed and consistent; a future concrete binding may add conditional
knowledge without changing the stage-capability contract.

##### The operational schema needs a skill, not a role body

`cst-architect` is not the right sole home for this contract. The records are
mutated by roles other than the architect: `model-builder` opens attempts, writes
outputs, and produces checkpoints; `model-validator` supplies the `validation`
record that makes a checkpoint reusable; `stress-test-analyst` publishes
`performance_analysis`, `robustness_evaluation`, and `projection_overlay`
products and declares their `input_role` typing; `python-engineer` implements the
Snakemake and manual adapters. If the protocol lives only in a role body or only
in this ADR, those roles can complete their contracts without ever writing a
conforming record, and adapters will diverge on transitions and checkpoint
validation. `role-design`'s multiplicity rule places expertise consulted by
several roles in a skill.

**Decision: a focused owned skill, `cst-run-control`, is the durable operational
home**, with `scientific-workflows` retaining general cross-engine provenance and
source/cache/output hygiene and cross-referencing it. A focused skill rather than
an extension of `scientific-workflows` because: the schema is normative and
versioned, and its conformance vectors are executable test data needing a
`references/` home and an independent version and history under ADR 0011; its
stage vocabulary is bound to the CST capability slots and the bottom-up ordering
rules, which are not general workflow hygiene; and folding it in would both widen
`scientific-workflows`' trigger surface beyond cross-engine hygiene and couple
its version to CST schema churn.

`cst-run-control` is bound **conditionally** to `cst-architect`, `model-builder`,
`model-validator`, `stress-test-analyst`, and `python-engineer`, with each
frontmatter skill entry mirrored in the role body for closure. This ADR remains
the rationale and the decision of record; the skill carries the operational
specification, the field schema, and the conformance vectors.

##### Affected artifacts and closeout

This ADR is a design record; the following is the required follow-on work,
tracked under `t260722c` and owned by its implementation task. **None of it is
done by this document.**

| Artifact | Change |
| --- | --- |
| `dev/decisions/0022-<slug>.md` | The landed ADR, at the next free number confirmed by the decision index |
| `dev/decisions/index.md` | New row for 0022 |
| `artifacts/agents/cst-architect.md` | Slot mapping, managed-root trigger, contract emission/validation, conditional `cst-run-control` binding |
| `artifacts/agents/_history/cst-architect.md` | Append-only row for the revision |
| `artifacts/agents/{model-builder,model-validator,stress-test-analyst,python-engineer}.md` and their `_history/` files | Conditional `cst-run-control` binding, frontmatter mirrored in body; append-only history rows |
| `artifacts/skills/cst-run-control/` | New owned skill: `SKILL.md`, `references/` schema and conformance vectors, version and `HISTORY.md` per ADR 0011 |
| `.claude/agent-manifest.yml` | Register the new skill and its theme |
| Generated activation | Regenerate for every project that already activates `cst-architect` |

Closeout checks, run in this order, content checks before activation:

1. `python artifacts/skills/role-maintenance/scripts/role-score.py --repo-root . --no-write`
2. `python brain.py status --agent-refs --detail`
3. `python brain.py status --agent-system --detail`
4. `python brain.py status --strict` — includes the decision-record lint that
   would flag a missing index row or a stray file in `dev/decisions/`
5. `python brain.py refresh --agent-system` — project-scope activation refresh,
   only after 1–4 pass

### Consequences

**Positive.**

- New engines and toolchains attach through named bindings inside a fixed
  stage-capability set, so the core architect contract remains stable.
- Every result-affecting stage — validation, indicator reduction, surface and
  vulnerability mapping, robustness evaluation, and the optional overlay — now
  carries a versioned binding and an accountable owner, so two valid runs that
  reach different scientific conclusions are diagnosable rather than merely
  puzzling.
- Manual and service-managed runs share auditable identity, provenance,
  collision, attempt, and resume semantics.
- Namespace exclusivity and single-writer exclusion are enforceable invariants
  rather than pre-execution assertions: the atomic claim gates `ready` and
  excludes ancestor, descendant, and exact overlaps in one operation, and
  publication collapses to a single token-checked inventory compare-and-set over
  immutable content-addressed objects, so a superseded executor cannot make
  anything current even if it is still alive.
- The intent/state boundary makes configuration drift and silent mutation
  detectable, and checkpoint reuse is falsifiable against environment digest,
  dependency closure, and a named validation authority.
- The projection-overlay boundary becomes machine-checkable through typed
  stage-graph reachability rather than a self-declared boolean.
- `scientific_design_hash` gives scientific equivalence a stable key independent
  of owner, namespace, resources, and orchestrator, so reruns group and an
  operational relocation is distinguishable from a scientific change.

**Negative.**

- Every run into a managed project root — including a manual single-user one —
  carries manifest, digest, and namespace-claim bookkeeping. The `provenance`
  conformance level relieves some of this but not the claim or the digests.
- Content hashing large inputs and validating checkpoints adds I/O cost, and
  environment digests add build-time cost.
- Adopters must implement a genuine compare-and-set and a fencing discipline in
  their own medium. The contract no longer leaves collision safety to
  coordination good intentions, which raises the floor for a conforming
  adapter: even a manual workspace needs an `O_EXCL` claim file, a monotonic
  token, and attempt-private staging with promote-on-publish at the `managed`
  level.
- The canonicalization must be maintained per `schema_version` with its
  conformance vectors kept in step, and the prohibition on binary floats
  constrains how non-integral scientific parameters are expressed in hashed
  fields.
- Authoring an explicit typed stage graph per run is real design effort, and the
  graph must track the workflow it describes. A stale graph fails validation
  rather than diverging silently — safer, but noisier.
- Declaring an existing project root managed requires importing or evicting its
  pre-existing outputs first.
- Binding versions must be immutable identifiers, so workflows currently pinned
  to mutable tags need repinning.

**Neutral.**

- Existing isolated single-user runs remain valid outside managed roots; they
  adopt the contract when their project root is declared managed or when they
  need resume or auditability.
- BlueEarth-CST code, scheduler selection, persistence, lock implementation,
  APIs, and concrete SFINCS/FIAT bindings remain separate implementation
  decisions; this ADR adds no engine binding.
- Existing implementation and validation handoffs do not change ownership; the
  slot table records the ownership that already exists.
- A new owned skill, `cst-run-control`, becomes the operational home of the
  schema. This ADR stays the rationale and decision of record.

**Known limitations.**

Review raised five further gaps that this record accepts as real and states here
rather than closing with mechanism, because specifying each would grow the
contract past what an architect can emit in a run plan. Each names a property the
contract does **not** deliver. An adopter needing one supplies it outside this
contract, and this ADR does not make such a supplement interoperable between
adopters.

- **Resource claims have admission semantics but not a complete lifecycle.**
  Admission of a capacity-bearing claim is an atomic compare-and-set at the
  `capacity_authority`, and both cancellation transitions release claims. But a
  claim carries no reservation identity binding it to the attempt it was acquired
  for; nothing rolls it back when the `ready → running` CAS it was acquired for
  loses, or when the acquiring process dies before that transition commits; and
  neither `running → succeeded` nor `running → failed` releases attempt- or
  stage-scoped claims. Live claims can therefore be orphaned, permanently
  consuming a licensed engine or a capacity allocation and causing later
  admissible runs to fail as oversubscribed. Detecting and reconciling orphaned
  claims is an operator action this contract neither defines nor authorizes.
- **Tombstone release requires a record no transition permits.** A tombstone may
  be released only after artifact disposition is verified and recorded in the
  cancelled run's final state — but `cancelled` is terminal and no legal
  transition writes that record. An implementation must therefore either mutate
  terminal state, which the lifecycle forbids, or retain cleaned tombstones
  indefinitely, which permanently blocks reuse of a namespace that is in fact
  empty. The general claim-release path for a succeeded run carries the same
  omission.
- **Bottom-up compliance is declared and structurally checked, not observed at
  execution time.** Validation reads the declared stage graph, never the bytes a
  component actually consumed. A run that reads a projection product it omitted
  from its graph, or that types an overlay artifact as `system_input`, presents a
  structurally valid graph and passes conformance, so a projection-conditioned
  response surface can be certified bottom-up. The violation is attributable
  after the fact — to a declaring role, at a named artifact on a named edge — but
  it is not prevented. This is a deliberate acceptance: requiring execution-time
  consumed-dependency attestation would raise the adapter floor past a manual
  workspace and exclude adopters the contract must keep conformant.
- **`scientific_design_hash` is not a pure scientific-equivalence key.** It
  ingests the entire resolved configuration through `config_hash`, and that
  document commonly carries operational-only fields — output paths, scheduler
  profiles, thread counts, logging, staging, runtime controls — which re-enter
  the digest even though their duplicated top-level counterparts and the
  `orchestrator` binding are excluded. The grouping property therefore holds only
  across the fields the digest table excludes: a manual, a Snakemake, and a
  service run of one experiment share a `scientific_design_hash` only when their
  resolved configurations agree outside those fields. Where they do not, reruns
  fail to group and an operational relocation is misread as a scientific change.
  This record does not partition configuration into science-bearing and
  operational subtrees.
- **Validation records have an authority but no normative collection.** Every
  binding declares a `validation_authority`, and `running → succeeded` requires a
  passing validation record for every applicable slot — but the contract defines
  no normative collection or serialization for those records, and no coverage
  rule tying them to slots and covered artifact or checkpoint digests, least of
  all for stages that produce no reusable checkpoint. Two conforming adopters can
  therefore store mutually unreadable records, and the same run may be provably
  successful under one implementation and not provable under another despite
  matching validation authorities.

### Alternatives considered

#### Minimal manifest for manually isolated workspaces

Record owner, paths, and hashes but omit state/attempt/checkpoint semantics. This
was not chosen because it cannot define safe resume or give future services a
shared execution contract. It would be preferable if runs were permanently
single-user, non-resumable, and manually isolated. Its useful core survives as
the `provenance` conformance level: a run may omit attempts, checkpoints,
fencing, resource claims, and resume, but it may **not** omit the digests, the
stage graph, or the atomic namespace claim, because those are what keep a mixed
estate safe.

#### Dedicated operational role and shared scheduler

Add an operational orchestrator responsible for queues, leases, retries, and
resource placement. This was not chosen because no scheduler or service boundary
has been selected, and it would mix an implementation decision into the portable
contract. It becomes preferable when operating scale requires continuous queue
ownership and service-level guarantees. Note that requiring compare-and-set and
fencing *semantics*, as this ADR now does, is not this alternative in disguise:
it names invariants an adopter must preserve, while this alternative would name a
component that owns them.

#### Keep the fixed HydroMT/Wflow/Snakemake contract

Strengthen only run isolation while retaining current tools as architectural
requirements. This was not chosen because every new engine would force a
role-contract revision and impact modeling remains structurally absent. It is
preferable only if CST is permanently defined as this exact toolchain.

### Related

Paths below resolve from this record's landed location, `dev/decisions/`. Only
durable artifacts are linked: the scoping intake's load-bearing content — problem
statement, constraints, decision criteria, non-goals, and the three candidate
alternatives — is inlined above in *Context*, *Decision*, and *Alternatives
considered*, and the design-run directory and the tracking T-item are
deliberately **not** linked because both are prunable lifecycle artifacts that
would leave this record with dangling references once the run closes.

- [`cst-architect` role](../../artifacts/agents/cst-architect.md) — the contract this ADR revises.
- [`climate-stress-testing` skill](../../artifacts/skills/climate-stress-testing/SKILL.md) — governing bottom-up sequencing and the projection-overlay boundary.
- [`robustness-metrics` skill](../../artifacts/skills/robustness-metrics/SKILL.md) — the metric and acceptance logic referenced by the `decision_framing` and `robustness_evaluation` slots.
- [`scientific-workflows` skill](../../artifacts/skills/scientific-workflows/SKILL.md) — general cross-engine provenance and source/cache/output hygiene, which `cst-run-control` cross-references rather than duplicates.
- [ADR 0011 — owned-skill versioning](0011-owned-skill-versioning.md) — governs the new `cst-run-control` skill's version and history.
- [Decision-record index](index.md) — confirms 0022 as the next free number and that no existing run-control ADR overlaps this subject.

### Review record

This design was produced under a `design-review-loop` run (`cst-run-control`,
started 2026-07-26, full variant). The run directory was pruned when this record
landed; the section below is the durable audit trail, and the verbatim reviews
remain recoverable from the commits named in the verdict table.

#### Verdicts

| Review | Lens / round | Verdict | `doc_version` | Verbatim source |
|---|---|---|---|---|
| Internal panel | risk & assumptions (`critical-thinker`) | `revise` | `design-v1.md` | commit `75c4262e` |
| Internal panel | architecture & internal consistency | `revise` | `design-v1.md` | commit `75c4262e` |
| Internal panel | repository fit & conventions | `revise` | `design-v1.md` | commit `75c4262e` |
| External round 1 | GPT, clean-room (document only) | `revise` | `design-v2.md` | commit `29eed794` |
| External round 2 | GPT, with ledger + index, regression duty | `revise` | `design-v3.md` | commit `08d44e6f` |

The internal panel raised 21 findings (7 blocking, 13 major, 1 minor) across ten
concern groups: capability and stage coverage; atomic claim and fencing
semantics; typed-dependency enforcement of the bottom-up and overlay rules;
canonical hashing and scientific identity; attempt and checkpoint semantics;
shared-resource identity and lifecycle; the manifest adoption trigger; ownership
of the cross-role mutation protocol; implementation and verification closure; and
durable-link hygiene for the landed record.

External round 1 returned 7 findings (1 blocking, 6 major). External round 2
returned 7 more (2 blocking, 5 major), six of which faulted the completeness of
resolutions already accepted rather than raising new ground.

#### Arbitration

The loop caps external review at two rounds. Round 2 did not converge, so the cap
triggered owner arbitration rather than a third round. On 2026-07-28 the owner
ruled on all seven surviving findings:

- **Mechanism fix required** — `ext2-1` (publication was not token-atomic in
  either commit order) and `ext2-2` (namespace exclusion covered an exact key but
  not overlapping namespaces). Both are closed in this record.
- **Accepted but scoped** — `ext2-3`, `ext2-4`, `ext2-5`, `ext2-6`, `ext2-7`.
  Each names a real consequence, recorded under *Consequences* → *Known
  limitations* rather than closed by specifying a mechanism, because specifying
  each would grow the contract past what an architect can emit in a run plan.
- **Framing ruling** — bottom-up compliance is **declaratively auditable, not
  enforced**. Execution-time consumed-dependency attestation was declined
  because it would raise the adapter floor past a manual workspace.

Under the loop's sequencing rule no version reaches acceptance without a reviewer
verdict naming it; the arbitration rulings are the logged exception the cap
creates, and the resulting revision was scope-checked against the arbitrated
finding IDs before acceptance.

#### Findings ledger

Append-only, one row per original finding ID.

| ID | Round | Severity | Disposition (accepted / rejected / deferred / withdrawn) | Resolution or rationale | Doc version |
|---|---|---|---|---|---|
| risk-3 | internal-panel | major | accepted | `#### Capability slots` replaced the five-slot table with a ten-slot stage-capability model derived from the full CST stage contract: `decision_framing`, `system_model_validation`, `performance_analysis`, `robustness_evaluation`, and `projection_overlay` were added alongside the original four plus `orchestrator`. `impact_model` stays but now carries an explicit `not_applicable` reason. The section also answers the finding's open question in prose: slots describe **both** executable components and human handoffs, and every row must supply a component identity with an immutable revision **and** a delegated owner role — neither half optional. | design-v2.md |
| architecture-1 | internal-panel | blocking | accepted | Same rewrite of `#### Capability slots`. The slot set now covers decision framing and acceptance criteria (`decision_framing`), system-model validation (`system_model_validation`), indicator reduction and surface/vulnerability mapping (`performance_analysis`), projection preparation and overlay (`projection_overlay`), and adaptation-robustness evaluation (`robustness_evaluation`). The current HydroMT/Wflow/weathergenr/Snakemake bindings and the `model-builder` / `model-validator` / `geospatial-data-analyst` / `stress-test-analyst` / `python-engineer` handoffs are mapped explicitly in the table; `impact_model` remains inapplicable-per-run-type with a stated reason rather than leaving a required transformation unbound, because its result transformation now belongs to `performance_analysis`. | design-v2.md |
| repo-fit-1 | internal-panel | blocking | accepted | Same rewrite of `#### Capability slots`. `performance_analysis`, `robustness_evaluation`, and `projection_overlay` are stable slots owned by `stress-test-analyst`, matching the live `cst-architect` handoff table, so the results-analysis and projection-overlay stages map without misclassifying overlays as forcing. Every slot row names both a component identity with an immutable revision and a delegated owner. Note: this finding's `suggested_fix` concerns slot coverage only; the `dev/decisions/0020-<slug>.md` path cited in the driver brief actually appears in `repo-fit-4` (and `repo-fit-5` references ADR 0020), and the 0022 renumber is resolved there. | design-v2.md |
| risk-1 | internal-panel | blocking | accepted | `#### Identity, hashes, and namespaces` § *Namespace ownership is an atomic claim* makes the claim a compare-and-set that succeeds only against a no-owner state, and makes a won claim a **precondition of `planned → ready`** — so two planners observing an empty namespace can no longer both proceed. `#### State, attempts, and resume` § *Fencing and active-writer exclusion* mints a strictly-increasing `fencing_token` at `ready → running`, requires it on every output/checkpoint publication and every `run-state` mutation, and retires it in the same atomic transition that closes an abandoned attempt, so a superseded executor's writes are rejected rather than merged. Storage, lock, and scheduler mechanisms stay adopter choices; the `#### Decision` opening now states explicitly that the contract prescribes semantics, not mechanism, and lists conforming realizations (`O_EXCL`, atomic rename, unique-constraint insert, conditional write). | design-v2.md |
| architecture-2 | internal-panel | blocking | accepted | Same two subsections, plus `#### State, attempts, and resume` § *Every transition is a single conditional write*: `run-state` gains a monotonic `state_revision`, and every transition is one atomic CAS against the exact revision the writer read, with the transition (not the field update) as the unit of atomicity. The `##### Transition operations` table gives each transition explicit preconditions and atomically-applied postconditions, and a losing writer must re-read and re-evaluate. Namespace claim is CAS-bound to `run_id`; the loser fails planning with `namespace_claimed`. | design-v2.md |
| risk-2 | internal-panel | blocking | accepted | `#### Manifest contract` § *Scientific design and the typed stage graph* replaces label-based checking with a typed `stage_graph`: stable `stage_id`s from the slot vocabulary, `stage_interface_version`, and a closed `input_role` vocabulary (`system_input`, `stress_test_driver`, `evaluation_reference`, `decision_parameter`, `overlay_input`) on every typed edge. Six ordering rules are checked as graph reachability: thresholds and perturbation domain fixed before execution (rule 1), `ensemble_generator` accepting only scenario-neutral inputs and being the sole producer of `stress_test_driver` artifacts (rule 2), surface construction before overlay (rule 4), `overlay_input` artifacts consumable **only** by `projection_overlay` — so `performance_analysis` cannot projection-condition the response surface (rule 5) — and no directed path from an overlay artifact into any driver-producing or executing stage (rule 6). `bottom_up: true` is retained as a declaration but is no longer what validation rests on. | design-v2.md |
| architecture-4 | internal-panel | blocking | accepted | Same subsection. The design now represents stable stage identifiers and typed dependency edges, separates stress-test driver inputs from overlay inputs by `input_role`, requires metrics and thresholds before perturbation (rule 1) and surface construction before overlay (rule 4), confines `overlay_input` artifacts to edges terminating at `projection_overlay` (rule 5), and rejects any dependency path from an overlay artifact into perturbation generation or system-model execution (rule 6). The config-routing evasion the finding named is closed because every input reaching an executed stage must appear as a typed edge, so a projection product routed through resolved configuration is still a graph edge and still fails rule 5. | design-v2.md |
| repo-fit-2 | internal-panel | blocking | accepted | `#### Identity, hashes, and namespaces` § *Canonicalization is part of the schema* binds one normative canonicalization (`cst-canon/1`) to `schema_version`, surfaced in the intent record as `canonicalization_id`. It fixes RFC 8785 JCS serialization, forbids binary floats in hashed fields (decimal strings at declared precision), NFC string normalization, path/URI normalization, omitted-vs-explicit-null semantics, ordered-vs-set array declaration with sort keys, secret exclusion, immutable-only binding revisions, and `sha256:<lowercase-hex>` digest representation. Each `schema_version` ships **conformance vectors** with expected `config_hash`, `scientific_design_hash`, and `intent_hash`; an adopter that cannot reproduce them is non-conforming. § *Which fields enter which digest* states field participation for all three digests as an explicit inclusion/exclusion table. | design-v2.md |
| risk-4 | internal-panel | major | accepted | Same canonicalization subsection. Each named gap is addressed: defaults are expanded before `config_hash` (which is over the resolved document, not file bytes); numeric normalization is solved by forbidding floats rather than specifying float formatting; path/URI normalization is explicit; every array is declared `ordered` or `set` with a sort key; `secret`-marked fields are excluded from digests and from manifests entirely; and a binding `revision` must be an immutable identifier — a mutable tag, branch, or version range fails validation. Conformance vectors per `schema_version` are required. | design-v2.md |
| architecture-7 | internal-panel | major | accepted | Same canonicalization subsection: canonicalization is now part of `schema_version` rather than a producer-recorded convention, and one cross-language canonical form (RFC 8785 JCS plus the float ban, NFC, path, presence, and ordering rules) governs `config_hash`, `scientific_design_hash`, and `intent_hash` alike. The float prohibition is the specific measure that makes Python, R, Julia, and hand-written YAML tooling agree; conformance vectors are the executable check. | design-v2.md |
| architecture-3 | internal-panel | major | accepted | `#### Identity, hashes, and namespaces` § *Which fields enter which digest* adds `scientific_design_hash` over the `scientific_design` subtree (perturbations, realizations, indicator and threshold definitions, acceptance references, overlay specification, `stage_graph`) plus `config_hash`, the science-bearing `capability_bindings` with revisions, and the typed `inputs`. It explicitly excludes `owner_id`, `output_namespace`, `resource_request`, `resume_policy`, `parent_run_id`, and the `orchestrator` binding, so the same experiment run manually, under Snakemake, or by a future service shares one `scientific_design_hash`. `run_id` and the full `intent_hash` are retained for operational identity; `scientific_design` is a nested separately-hashable record in `#### Manifest contract`. | design-v2.md |
| risk-9 | internal-panel | minor | accepted | Fixed, not deferred — the same `scientific_design_hash` that `architecture-3` requires. `#### Identity, hashes, and namespaces` § *Which fields enter which digest* retains `intent_hash` at full execution-intent scope exactly as this finding asked ("`intent_hash` is deliberately **not** narrowed") and adds the separate scientific identity, so a scientifically identical rerun in a mandatorily-new namespace is still recognizable as the same experiment. The section states the division of labour directly: `intent_hash` answers operational identity, `scientific_design_hash` answers "are these two runs the same experiment?", and `parent_run_id` records lineage without being an equivalence key. | design-v2.md |
| risk-5 | internal-panel | major | accepted | `#### State, attempts, and resume` was restructured into *Every transition is a single conditional write*, *Transition operations*, *Fencing and active-writer exclusion*, and *Recovery from an interrupted transition*. `state_revision` gives CAS semantics; the transition table gives every transition explicit preconditions and atomically-applied postconditions, including which fields close each outcome (`outcome`, `ended_at`, structured `failure` with `reason`/`stage_id`/`detail`) and the fencing token, which the attempt record itself carries alongside `attempt`, `executor_id`, `started_at`, `resource_allocation`, `resume_mode`, and `resumed_from_checkpoint_id` — so "retired or lower token" is auditable per attempt, not only against current state. Because a transition is one CAS, the crash-between-updates ambiguity is eliminated by construction and recovery is a re-read; the two residual cases (open attempt with a gone executor, uncovered artifacts) are defined explicitly. Cancellation is now permitted from any non-terminal state, including `planned` and `ready`. | design-v2.md |
| risk-6 | internal-panel | major | accepted | `#### Manifest contract` § *Checkpoints* replaces the digest-equality-plus-label rule. A checkpoint now carries `stage_interface_version`, `stage_graph_version`, `source_attempt`, the producing binding revision **and** an `environment_digest` over the resolved runtime and transitive dependencies, a complete `dependency_closure`, a `completeness` status, and a `validation` record naming `validator_id`, procedure, and version. Reuse requires all of these to match and the validation outcome to pass; a checkpoint may be marked validated only by its slot's delegated owner (`model-validator` for `simulation_engine` outputs) or a recorded automated validator — file existence never implies validation. Invalidation is explicit and downstream-transitive. | design-v2.md |
| architecture-5 | internal-panel | major | accepted | Same `#### Manifest contract` § *Checkpoints* (adding `checkpoint_id`, `stage_graph_version`, `source_attempt`, `dependency_closure`, `completeness`) plus `#### State, attempts, and resume` § *Resume*, where the new attempt records `resume_mode` and the single `resumed_from_checkpoint_id`, and `failed → ready` requires uncovered outputs and outputs not covered by a reusable checkpoint to be **quarantined** — retained but durably excluded from being read as current — before execution continues. The transitive-invalidation rule requires the selected checkpoint's whole upstream closure to be reusable, so manual, Snakemake, and service adopters cannot resume different work while each considers the run valid. | design-v2.md |
| risk-7 | internal-panel | major | accepted | `#### Manifest contract` § *Resources* replaces bare `shared_resource_keys` with structured `shared_resources` entries: namespaced `<authority>/<name>` `resource_id`, `access_mode` (`shared_read` / `shared_write` / `exclusive`), `quantity` and `unit` where capacity-limited, `capacity_authority` so oversubscription is decidable, and `claim_scope` (`run`, `attempt`, or a `stage_id`). A conflict predicate is stated so two manifests alone determine conflict without knowing placement policy. Read-only caches are inputs; mutable caches are `shared_write` resources that must be claimed — closing the concurrent-cache-mutation case. Claims held by the current attempt are recorded in `run-state.resource_claims` with the authorizing `fencing_token`. | design-v2.md |
| architecture-6 | internal-panel | major | accepted | Same `#### Manifest contract` § *Resources*. Each request now carries key, access mode, quantity and unit where capacity applies, and a `claim_scope` binding the claim to the run, the attempt, or a stage; `run-state.resource_claims` records what is actually held. Queueing and lock mechanisms are explicitly left to adopters while the conflict predicate makes single-writer caches, licensed engines, and capacity-bound nodes mechanically detectable even when output namespaces differ. | design-v2.md |
| risk-8 | internal-panel | major | accepted | `#### Adoption and validation` § *Objective adoption trigger* replaces the circular "concurrently managed" test with a **locational** one: every run whose `output_namespace` lies under a *managed project root* must hold a namespace claim, regardless of how or by whom it is launched or whether another run is active. A root becomes managed by an explicit recorded owner declaration, so the rule is checkable by inspecting the root rather than by inferring operator intent, and there is no "still isolated enough" third category. Migration is specified: pre-existing outputs must be imported (registering a minimal record pair marked `conformance: provenance_only` that claims their namespace) or evicted **before** the root is declared managed. § *Conformance levels* adds `provenance` and `managed`, with the namespace claim required at **both** — which is what keeps a mixed estate collision-safe. The `#### Role-contract changes` bullet that previously said "before any multi-user run enters `ready`" now cites the managed-root trigger. | design-v2.md |
| repo-fit-3 | internal-panel | major | accepted | `#### Role-contract changes` § *The operational schema needs a skill, not a role body* names the durable home: a focused owned skill **`cst-run-control`**, with `scientific-workflows` retaining general cross-engine provenance hygiene and cross-referencing it. The justification the finding asked for is stated — the schema is normative and versioned with executable conformance vectors needing a `references/` home and an independent version/history under ADR 0011; its stage vocabulary is bound to the CST capability slots and bottom-up ordering rules rather than general hygiene; and folding it into `scientific-workflows` would widen that skill's trigger surface and couple its version to CST schema churn. The skill is bound **conditionally** to `cst-architect`, `model-builder`, `model-validator`, `stress-test-analyst`, and `python-engineer` — the actual mutation points — with frontmatter entries mirrored in each role body, and the ADR is explicitly demoted to rationale rather than sole operational specification. Specified as required follow-on work; no skill or role file was created or edited by this document. | design-v2.md |
| repo-fit-4 | internal-panel | major | accepted | `#### Role-contract changes` § *Affected artifacts and closeout* adds the affected-artifact table (landed `dev/decisions/0022-<slug>.md` **and** its `dev/decisions/index.md` row; `artifacts/agents/cst-architect.md` plus its append-only `artifacts/agents/_history/cst-architect.md` row; the four newly-bound roles plus their history rows; the new `artifacts/skills/cst-run-control/` with version and `HISTORY.md` per ADR 0011; `.claude/agent-manifest.yml` registration; activation regeneration for every project already activating `cst-architect`) and the ordered check list: `role-score.py --repo-root . --no-write`, `brain.py status --agent-refs --detail`, `brain.py status --agent-system --detail`, `brain.py status --strict` for the decision lint, then `brain.py refresh --agent-system` only after the content checks pass. The ADR path is resolved to **0022**, not the 0020 this finding cited, per the driver's ADR-renumber amendment. Everything is framed as required follow-on owned by the `t260722c` implementation task; no bookkeeping was performed here, which is outside this stage's authority. | design-v2.md |
| repo-fit-5 | internal-panel | major | accepted | `### Related` was rewritten. The `intake.md` and T-item links are removed; the section states that the intake's load-bearing content (problem, constraints, decision criteria, non-goals, and the three alternatives) is inlined in *Context*, *Decision*, and *Alternatives considered*, and that the prunable design-run directory and T-item are deliberately not linked. Remaining links are durable artifacts only — the `cst-architect` role, the `climate-stress-testing`, `robustness-metrics`, and `scientific-workflows` skills, ADR 0011, and the decision index — and every path is rewritten to resolve from the record's landed location, `dev/decisions/`, so it complies with the `dev/decisions/` boundary (numbered ADRs plus `index.md` only). Title, body heading, and the index line now read ADR **0022**; the former "reserves ADR 0020" phrasing is gone. | design-v2.md |
| ext1-1 | external-r1 | blocking | accepted | The contradiction is removed by making the schema and validity **level-specific** rather than one schema with optional fields. `run-intent` gains an immutable `conformance` field (`#### Manifest contract`, excluded from `scientific_design_hash` in the digest table). `##### Conformance levels` now defines level-specific publication records — at `managed` an inventory entry carries `attempt` + `fencing_token`; at `provenance` it carries digest, publishing `executor_id`/`owner_id`, and `published_at`, with **coverage defined by the namespace claim, not a token** — and a level-specific reduced lifecycle (`planned → ready → succeeded \| failed \| cancelled`, no `running`, no attempts, `failed` terminal). The run-state inventory field and `##### Validity` are rewritten accordingly: Validity is split into a core profile (both levels, including "no artifact uncovered **under its level's coverage definition**") and a `managed`-only concurrency profile (CAS transitions, fencing, resource claims, checkpoints), and `#### State, attempts, and resume` is explicitly scoped as the `managed` lifecycle. The adoption-trigger import marker is harmonized from `conformance: provenance_only` to the `provenance` level marked as an import. No `provenance` run now needs fields its level omits. | design-v3.md |
| ext1-2 | external-r1 | major | accepted | The fencing mechanism is corrected, not restated: `##### Fencing and active-writer exclusion` now concedes that a claim file cannot stop a live superseded process and separates **writing from publication**. An artifact is *published* only when its inventory entry (digest, `attempt`, `fencing_token`) commits through the `run-state` CAS under a live token, and readers/resumers/validators must resolve current artifacts through the inventory with digest verification, never by directory listing. Media with conditional writes may reject stale writes at write time; otherwise a conforming `managed` realization **must** route executor writes into attempt-private staging locations and promote only through the token-checking publication step (atomic move/rename, inventory commit as the CAS gate), and **direct executor writes into the active namespace are declared non-conforming**. A still-running superseded executor thus writes only into its retired staging area (never promoted, quarantined at `failed → ready`), and any direct-write violation is detectable as an uncovered artifact whose digest matches no live-token inventory entry. `##### Adopters`, `##### Validity` (managed profile), and both Consequences bullets are updated to match. This constrains the conforming manual realization but names no scheduler or storage engine. | design-v3.md |
| ext1-3 | external-r1 | major | accepted | `##### Resources` now states that capacity is an **aggregate** property no pairwise predicate can decide (three claims can exceed capacity when no pair does). Admission of a capacity-bearing claim is redefined as **one atomic compare-and-set at the `capacity_authority`** over its current holder set and declared capacity — admitted only if the summed `quantity` of live claims plus the request stays within capacity, atomic with respect to concurrent admissions, same primitive class as the namespace claim. Validity (managed profile) now requires the aggregate quantity of all live claims per `resource_id` to remain within declared capacity and every capacity-bearing claim to have been admitted by the authority's CAS; the old "conflicts are detectable from two manifests alone" claim is narrowed to mode conflicts only, with capacity admission explicitly decidable only at the authority. | design-v3.md |
| ext1-4 | external-r1 | major | accepted | `##### Resources` replaces the incomplete conflict prose with a **complete 3×3 access-mode compatibility matrix**. `shared_write` now conflicts with `shared_read` (and with `shared_write`) by default — a mutable cache modified while another run reads it is a conflict, closing the nondeterministic-reader hole the finding named. The single carve-out follows the suggested fix: a `shared_read`×`shared_write` (or `shared_write`×`shared_write`) pair is compatible only when the resource's authority explicitly provides snapshot/transactional read (respectively transactional/serialized write) semantics **and each benefiting claim records the granted isolation and its authority reference**. `shared_read`×`shared_read` is the only unconditionally compatible pair; `exclusive` admits no exception. The Validity bullet now checks conflicts against this matrix. | design-v3.md |
| ext1-5 | external-r1 | major | accepted | The contradiction is resolved by **separating execution ownership from checkpoint-validation authority**, per the suggested fix. `#### Capability slots` adds a normative paragraph: the *Delegated owner* column names who executes and never implies who validates; every `capability_binding` declares a `validation_authority`, with the normative mapping that a slot covered by a declared validation stage takes that stage's owner as authority — `simulation_engine` → `system_model_validation` → `model-validator`, so `model-builder` never validates its own simulation — and uncovered slots name a role+procedure or a recorded automated validator. `##### Checkpoints` rewrites the contradictory sentence: a passing `validation` record is authorized iff its `validator_id` matches the intent's declared `validation_authority` for that stage, so every conforming implementation accepts and rejects the same checkpoints. The `run-intent` field list and Validity (both-levels profile) require `validation_authority` on every binding. | design-v3.md |
| ext1-6 | external-r1 | major | accepted | `##### Transition operations` splits cancellation into two rows: immediate namespace-claim release is available **only** when the output inventory is empty and the namespace is verified free of attempt products; otherwise the same atomic transition that retires the token converts the claim to a **tombstone** — a terminal claim keeping the namespace bound to the cancelled `run_id`, unclaimable by any new run, artifacts still attributed to the cancelled manifest. A new paragraph after the table defines tombstone release: only after every published and uncovered artifact is removed or quarantined and that disposition is verified and recorded. The claim-release paragraph in `##### Namespace ownership is an atomic claim` is aligned (release requires verified artifact disposition; cancellation with surviving artifacts converts rather than releases). A later run can no longer claim a namespace containing a cancelled run's artifacts. | design-v3.md |
| ext1-7 | external-r1 | major | accepted | `##### Resume` and the `ready → running` row replace the single `resumed_from_checkpoint_id` with `resumed_from_checkpoints`: a canonically sorted `set` array of checkpoint IDs forming the **resume frontier** across independent DAG branches. The selected frontier must be individually reusable (every member passes all *Checkpoints* conditions including a fully reusable upstream closure), **dependency-consistent** (a closure entry reaching a stage another member covers must resolve to that selected member — no mixing two checkpoints' versions of one stage output), and **non-overlapping** (no stage output supplied by more than one member); every reused artifact must be covered by a frontier member or its closure, everything else recomputed. Validity's checkpoint bullet checks the frontier conditions, so actual multi-checkpoint reuse is a recorded fact rather than an inference and reusable branches need not be recomputed. | design-v3.md |
| ext2-1 | external-r2 | blocking | accepted | Owner arbitration ruling, 2026-07-28 — **mechanism fix required**: the design must close the correctness hole. `##### Fencing and active-writer exclusion` removes the second storage mutation rather than ordering it: final artifacts are **immutable and content-addressed**, and publication is the inventory compare-and-set alone. A conforming `managed` realization commits in three prescribed steps — write into attempt-private staging keyed by attempt and token; **seal** into a write-once, digest-addressed object store (re-sealing identical bytes is a no-op, so a superseded executor's seal alters nothing); **publish** by one CAS on `run-state` whose predicate conjoins the observed `state_revision` with the presented token being current and live. Token validation, promotion, inventory update, and token retirement are therefore all predicates or effects of that single CAS, serialized by `state_revision`, so no rename/CAS race and no token-retirement gap remains. Crash recovery is defined for each of the three points in that order (before sealing → unreferenced staged bytes, quarantined at `failed → ready`; between seal and CAS → durable but non-current object, re-publication idempotent; during the CAS → re-read, with durability of referenced bytes guaranteed by step 2, so the inventory can never point at missing or stale content). Objects no entry references are reclassified **unreferenced, not uncovered**; committing an entry before its object is durable, publishing into a location a concurrent reader resolves as current, and direct executor writes into the active namespace are each declared non-conforming. `##### Adopters` and `##### Validity` are aligned. | design-v4.md |
| ext2-2 | external-r2 | blocking | accepted | Owner arbitration ruling, 2026-07-28 — **mechanism fix required**: the design must close the correctness hole. `##### Namespace ownership is an atomic claim` now defines identity and overlap normatively. **Canonical namespace identity**: the root-relative segment sequence canonicalized by the declared `canonicalization_id` path rules (POSIX separators, NFC, no `.`/`..`, no drive letters or backslashes) with symlinks resolved first — that deterministic form is what `output_namespace` stores and what enters `intent_hash`, so conformance vectors stay reproducible; a managed root on a case- or Unicode-folding medium must declare the folding, which governs **claim-time overlap comparison only**, never a hashed value. **Atomic exclusion over overlaps**: a candidate key conflicts with a live claim on equality, proper-prefix ancestor, or proper-prefix descendant, and the claim is one compare-and-set at the project-root claim authority over its live claim set, succeeding only if no live claim conflicts in any of those three senses, evaluated atomically against concurrent claimants. Tombstoned claims count as live; sub-locations inside a claimed namespace (object store, attempt-private staging, quarantine) belong to that claim and are never separately claimable. Two conforming disciplines are named (registry, flat) so the semantics stay mechanism-free. The `basin/run` vs `basin/run/output` case the finding raised now fails the CAS. | design-v4.md |
| ext2-3 | external-r2 | major | accepted | Owner arbitration ruling, 2026-07-28 — **accepted but scoped**: the consequence is real, and is resolved by stating it as an explicit known limitation rather than by specifying a claim-lifecycle mechanism, because a reservation-identity, compensation, and reconciler specification would grow the contract past the intake's criterion that it stay small enough for the architect to emit in a run plan. `### Consequences` § *Known limitations* records that resource claims have admission semantics but not a complete lifecycle: no reservation identity binds a claim to the attempt it was acquired for, nothing rolls a claim back when the `ready → running` CAS it was acquired for loses or when the acquiring process dies before that transition commits, and neither `running → succeeded` nor `running → failed` releases attempt- or stage-scoped claims (both cancellation rows do release). The stated consequence is the reviewer's: live claims can be orphaned, permanently consuming a licensed engine or capacity allocation and causing later admissible runs to fail as oversubscribed, with reconciliation an operator action the contract neither defines nor authorizes. | design-v4.md |
| ext2-4 | external-r2 | major | accepted | Owner arbitration ruling, 2026-07-28 — **accepted but scoped**: resolved by explicit known limitation, not by adding a post-terminal claim-maintenance operation, which would add a transition class and an append-only disposition record to a lifecycle the contract deliberately keeps emittable in a run plan. `### Consequences` § *Known limitations* records that tombstone release requires a record no transition permits: release is conditioned on artifact disposition being verified and recorded in the cancelled run's final state, yet `cancelled` is terminal and no legal transition writes that record. The consequence is stated in the reviewer's terms — an implementation must either mutate terminal state, which the lifecycle forbids, or retain cleaned tombstones indefinitely, permanently blocking reuse of a namespace that is in fact empty — and the general claim-release path for a succeeded run is noted as carrying the same omission. | design-v4.md |
| ext2-5 | external-r2 | major | accepted | Owner arbitration ruling, 2026-07-28 — **accepted but scoped, with a framing ruling**: the ADR claims bottom-up compliance is **declaratively auditable, not enforced**; execution-time consumed-dependency attestation is explicitly not required, because it would raise the adapter floor past a manual workspace and exclude adopters the contract must keep conformant. Two parts. (a) Claim narrowed in place: `##### Scientific design and the typed stage graph` now states that rules 5 and 6 are the machine-checkable form of the overlay boundary **as declared**, that validation checks the declared graph and not the bytes a component read, that a run consuming an undeclared projection product or mistyping an overlay artifact as `system_input` can still present a structurally valid graph carrying `bottom_up: true`, and that the stronger attestation alternative was weighed and rejected for the adapter-floor reason; `#### Capability slots` is aligned. (b) Residual exposure recorded rather than closed: `### Consequences` § *Known limitations* states that a projection-conditioned response surface can be certified bottom-up and that the violation is attributable after the fact — to a declaring role, at a named artifact on a named edge — but not prevented. | design-v4.md |
| ext2-6 | external-r2 | major | accepted | Owner arbitration ruling, 2026-07-28 — **accepted but scoped**: resolved by explicit known limitation, not by normatively partitioning configuration into science-bearing and operational subtrees with accompanying conformance vectors, which would enlarge the schema beyond what the intake's decision criteria admit. `### Consequences` § *Known limitations* records that `scientific_design_hash` is not a pure scientific-equivalence key: it ingests the entire resolved configuration through `config_hash`, and that document commonly carries operational-only fields — output paths, scheduler profiles, thread counts, logging, staging, runtime controls — which re-enter the digest even though their duplicated top-level counterparts and the `orchestrator` binding are excluded. The limitation also qualifies the Positive bullet's grouping claim rather than editing it: grouping holds only across the fields the digest table excludes, so a manual, a Snakemake, and a service run of one experiment share a hash only where their resolved configurations agree outside those fields; otherwise reruns fail to group and an operational relocation is misread as a scientific change. | design-v4.md |
| ext2-7 | external-r2 | major | accepted | Owner arbitration ruling, 2026-07-28 — **accepted but scoped**: resolved by explicit known limitation, not by adding a normative validation-record collection with required fields, cardinality, and a coverage rule, which is exactly the operational-schema detail the intake keeps out of the record. `### Consequences` § *Known limitations* records that validation records have an authority but no normative collection: every binding declares a `validation_authority` and `running → succeeded` requires a passing validation record for every applicable slot, but the contract defines no normative collection or serialization for those records and no coverage rule tying them to slots and covered artifact or checkpoint digests, least of all for stages producing no reusable checkpoint. The consequence is stated in the reviewer's terms — two conforming adopters can store mutually unreadable records, and the same run may be provably successful under one implementation and not provable under another despite matching validation authorities. | design-v4.md |
