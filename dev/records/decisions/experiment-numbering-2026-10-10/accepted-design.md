# Numbered experiment reservation lifecycle — design v3

Status: proposed; G1 framing approved; G2 exact-byte approval pending. Date: 2026-10-10.
Lifecycle: task-owned review version; reviewed bytes become immutable. `status.md` owns acceptance.
Author: cst-architect. Requested model/effort: gpt-6-astra/high; effective settings are unverified.

## 1. Overview

Reserve `stress_test_01` before producers start, retain its scientific request, and continue that identity
on ordinary reruns. `--new-experiment` deliberately advances the family number. Once generation finishes,
bind the exact collection, run IDs and existing simulation intent before any native simulation response.
Verified retained responses remain immutable; supported staged reuse is bounded by section 8.4.
A different request cannot acquire an interrupted identity.

This supplements the existing collection and simulation contracts with allocation history and an early
request guard. It replaces dated default-name selection and the helper's config-editing allocator. It
does not version a project, copy its model, change stochastic algorithms, or add Wflow checkpoints.
The capability serves every WF4 project root, both public runners, and read-only DAG/validation tools.

The user receives a stable numbered experiment, readable creation metadata, retained creator inputs,
and diagnostics that distinguish continuation, incompatible inputs and interrupted publication.
Experiment numbers never select a stochastic draw. Explicit creation can reuse an existing collection.

```mermaid
flowchart LR
  A[Select or reserve name] --> B[Freeze effective request]
  B --> C[Prepare source inputs]
  C --> D[Pin existing WF3 seed and plan]
  D --> E[Resolve ready collection and exact runs]
  E --> F[Freeze existing simulation intent]
  F --> G[Simulate, retain responses, derive metrics]
```

G1 approved D1: the current automatic seed depends on prepared source bytes.
On a fresh root its numeric value cannot exist before source preparation. This design retains the early
request guard, records `seed: awaiting_sources`, then pins the existing deterministic seed before any
stochastic generation. Section 5.2 describes the constraint and alternatives. Implementation must not
silently change the seed algorithm to satisfy an impossible earlier timing requirement.

Contents: [Behavior](#2-user-facing-behavior), [Outputs](#3-proposed-outputs-and-placement),
[Records](#4-closed-record-contracts), [Lifecycle](#5-binding-and-publication-lifecycle),
[Integration](#6-integration-and-capability-map), [Alternatives](#7-alternatives-and-consequences),
[Verification](#8-evidence-and-verification), [Decisions](#9-migration-and-decisions).

## 2. User-facing behavior

### 2.1 Selection and commands

`experiment_name: null`, or its absence, means family `stress_test`. A new non-numbered value means a
custom family. An existing owned non-numbered legacy directory takes precedence on ordinary execution.
An empty string remains invalid; whitespace is never silently converted to the default.

Use the existing safe-name grammar, `^[a-z0-9][a-z0-9_]*$`, with its Windows-device exclusions and
64-character maximum. Parse the final underscore followed by digits as a numbered pin. Canonical numbers
are `_01` to `_99`, then `_100`, `_101`, and onward. Reject zero, `_1`, `_001` and other extra leading
zeros. No cap at 99 or 999. Validate the complete candidate before allocation; never truncate a base.
`seasonal_2026` pins number 2026; use `seasonal_2026_test` for a descriptive year in a base.

The resolver returns exactly one of `continue`, `create`, `legacy`, `missing`, or `refuse`, including
resolved absolute root, name, family/number when applicable, selection reason and reservation ID.
Preview adds `advisory: true` for a would-be creation. It never becomes execution authority by itself.

| Request | Result |
|---|---|
| Plain family, no allocations | Create `<base>_01`. |
| Plain family with allocations | Select highest numeric allocation, even if complete. |
| `--new-experiment` | Allocate above the family high-water mark. |
| Canonical numbered pin | Continue exactly it, or create it if never allocated. |
| Pin plus `--new-experiment` | Refuse before allocation. |
| `--note TEXT` without `--new-experiment` | Refuse; notes apply once to explicit creation. |
| Highest allocation missing/deleted | Report it; do not fall back or recreate. |
| Metrics-only | Select an existing complete experiment; never allocate. |
| WF4 disabled with creation/note/recovery flags | Refuse before producers. |

Both `scripts/run_workflows.py` and `scripts/simulate_system.py` accept `--new-experiment` and `--note`.
G1 additionally approved `--recover-reservation` for explicit repair of a verified interrupted
publication. It cannot combine with creation/note flags or metrics-only. Section 5.4 limits its authority.
The existing `--config`, `--project-dir`, `--target`, `--simulation-target` and resource controls retain
their current meaning. Source configuration files are never rewritten.

Example commands, with the family's value in the existing WF4 configuration:

```powershell
pixi run python scripts/run_workflows.py --config <project.yml> --project-dir <root>
pixi run python scripts/run_workflows.py --config <project.yml> --project-dir <root> --new-experiment --note "Alternative operating assumptions"
pixi run python scripts/simulate_system.py --config <project.yml> --new-experiment
pixi run python scripts/simulate_system.py --config <project.yml> --recover-reservation
```

The standalone simulation runner consumes a ready collection; it does not invoke generation. It still
uses the same selection and reservation service. Its unresolved project-generation request fails with
the existing command for producing the collection, without starting native simulation.

Before expensive producers, print the resolved root, experiment name, `new`/`continuing`/`legacy`, and
effective scenario request or exact ready selection. After generation print collection ID, revision and
selected run IDs, using the existing capped-list convention and reporting any omitted count. On failure
after explicit creation say: omit `--new-experiment` to continue the reserved experiment. Repeating that
flag intentionally consumes another number.

### 2.2 Compatibility and recovery

Compare normalized scientific values, not source YAML bytes. Comments, mapping order, resource counts,
notes, metric choices and figure-only settings do not change the reservation request. Source archives
retain the original bytes independently. Existing scientific code/environment fingerprint guards remain
authoritative; equal configuration alone does not establish simulation compatibility.

A changed pending request fails before any upstream producer. A bound experiment also compares exact
collection/run and simulation identities before native work. Identify field paths and old/new values;
offer the retained creator configuration plus verified input references, or explicit new creation.
Never restore inputs, refresh frozen references, remove native responses or rewrite current config
automatically. A configuration archive cannot restore missing external data or an overwritten model.

Compatibility follows the actual WF4 selection. If generation is disabled and an explicit selector
points to the original ready collection, unrelated WF3 edits do not invalidate continuation. If WF3 is
enabled, its effective request remains guarded because it will write upstream project artifacts, even
when WF4 explicitly selects another existing collection. Switching from project-generation to explicit
selection of the exact retained collection is allowed once resolution is frozen; compare resolved
identities rather than the selector spelling. It is not permitted for an unresolved reservation.
For an already frozen intent, retain its original `resolution_mode` and manifest reference when checking
the new selector's asserted identity. Do not rewrite the intent to the new spelling; the existing freeze
function compares complete canonical intent bytes, not only `simulation_id`.

For a complete experiment, no-op is conditional on intact, current requested products. Missing derived
metrics or figures may be regenerated from verified retained responses. Missing/corrupt native responses
fail integrity checks and require restoration of recorded bytes or a new experiment. Additional metrics
use existing immutable metric sets. An incomplete Wflow member restarts from original inputs unless the
engine already supports a checkpoint; this feature promises no time-step continuation.

A completed immutable response is validated by the existing retained-response inventory and readers.
An intermediate staged member has weaker evidence: its `.ok` marker checks input fingerprints, not CSV
integrity. Preservation without re-execution is claimed only for the tested interruption after a member
is fully staged and before restoration starts, with recorded pre-interruption response bytes. Section 8.4
requires independent byte and execution evidence. Interruptions during restoration and altered staged
CSVs remain diagnosed existing limitations; this feature adds no native-output repair authority.

### 2.3 Legacy precedence

Apply these steps in order, under execution ownership for a writing invocation:

1. Validate path grammar and reject aliases, reparse points, files in place of directories and unknown
   occupied targets. An empty directory is not proof of ownership.
2. If the exact requested name has valid pre-reservation ownership, select it explicitly. Recognized
   ownership is the existing readable simulation intent with its paired valid creator archive, or the
   existing readable complete simulation. Do not weaken their schema/identity checks.
3. An exact name matching the existing dated pattern `<base>_<8 digits>[_vN]` is legacy only when that
   ownership validates. It never contributes to a numbered family. A dated legacy name plus new flag
   is refused with instructions to choose a different base.
4. An exact owned unnumbered legacy name wins over family interpretation on a plain run. With the new
   flag it is interpreted as a base, creating `<legacy-name>_01` or the next recorded number.
5. Otherwise apply canonical numeric parsing and ledger selection. An owned canonical numbered legacy
   folder is adopted into history, using its existing records without adding new creation metadata.

Never infer readiness from a folder name or modify a legacy frozen schema. Unpaired or unsupported old
records fail with diagnosis; this task does not add a reader for previously unsupported formats.
Unset default selection does not search dated legacy experiments. Users must specify those names.

## 3. Proposed outputs and placement

The source plan's `config/experiments/` placement fits the project's engine/provenance home.
`experiment.yml` belongs at the experiment root because the user reads its note and creation identity.
Machine lifecycle records remain under `_engine`. Staging below the ledger home is necessary to publish
the creation pair together; it is generated transaction state, not user workflow configuration.

```text
<project_dir>/                                      # existing user-selected root; no required active/
├── config/experiments/                             # added allocator home
│   ├── allocation.json                            # added durable history and high-water marks
│   └── _engine/transactions/<reservation_id>/      # added retained creation transaction
│       ├── transaction.json                       # added immutable creation recipe and digests
│       ├── sources/                               # added captured creator config/dependency bytes
│       ├── simulation-freeze.json                 # conditional immutable paired-freeze redo recipe
│       ├── freeze-payloads/                       # conditional exact archive bytes for that recipe
│       └── experiment/                            # conditional unpublished staging, moved once
│           ├── experiment.yml                     # initial metadata bytes
│           └── _engine/reservation.json            # initial pending binding bytes
├── config/runs/_engine/                            # existing invocation/archive/lock machinery
├── scenarios/_engine/requests/<request_id>/        # existing WF3 request and pinned plan authority
├── experiments/
│   ├── stress_test_01/                             # changed default; custom families supported
│   │   ├── experiment.yml                         # added immutable readable creation metadata
│   │   ├── _engine/
│   │   │   ├── reservation.json                   # added monotonic request/seed/resolution binding
│   │   │   ├── simulation_intent.json             # existing immutable simulation contract
│   │   │   ├── simulation.json                    # existing complete-readiness marker
│   │   │   └── response_inventory.json            # existing retained-response authority
│   │   ├── config/                                # existing simulation creator archive
│   │   ├── hydrology/wflow/                       # existing native responses/preparation
│   │   └── results/                               # existing immutable metric sets and figures
│   └── <legacy-name>/                             # retained in place; no automatic metadata edits
└── logs/wf4_simulate_system_<name>.log              # existing pattern receives resolved name
```

Proposed repository changes, separate from generated outputs:

```text
blueearth_cst/experiment/
├── allocate.py                                    # replaced internals; shared pure selection/owned commit
├── reservation.py                                 # added closed schemas, request projection, transitions
├── simulation_runner.py                           # changed shared admission and handoff
├── simulation_record.py                           # changed recoverable freeze integration; schemas retained
└── rules/simulate_and_metrics.smk                  # changed to consume the runner's resolved identity
scripts/
├── run_workflows.py                               # changed early reservation, single ownership interval
├── simulate_system.py                             # changed same resolver, ready-collection admission
├── generate_scenarios.py                          # changed bound-plan branch and reservation callback
├── suggest_experiment_name.py                     # changed to preview only; editing/allocation retired
└── plot_workflow_dag.py                           # changed read-only shared resolver
tests/                                            # changed/add focused allocator and lifecycle coverage
config/templates/                                 # changed naming guidance; existing seed prefixes retained
docs/site/                                        # changed commands, continuation and recovery guidance
```

| Surface | Current | Proposed and migration |
|---|---|---|
| Default name | Project slug plus date | `stress_test_01`; explicit legacy names still readable |
| New custom name | Exact unnumbered directory | `<base>_01`; document this behavior change |
| Creation | Helper reserves and edits YAML | Runner flag; helper preview only |
| Allocation history | Directory occupancy | Durable ledger; deletions remain tombstones |
| Creation note | None | Immutable optional `experiment.yml` note |
| Early binding | No pre-WF3 experiment guard | Pending scientific request and seed/selection binding |
| Crash recovery | Existing archive diagnostics | Explicit verified reservation/freeze recovery |
| Logs/DAG captions | Parse-time name resolution | One resolved name carried from admission |
| Preview | Several dated-name paths | Shared read-only resolver; advisory would-be allocation |
| Scientific records | Existing collection/simulation schemas | Retained; reservation only references them |

No scientific output format, native filename, metric-set schema, or legacy directory is renamed.
See [consumer-inventory.md](consumer-inventory.md) for complete paths and phase assignments, subject to
section 6's unchanged-provider constraint; an inventory entry does not authorize editing that source.

## 4. Closed record contracts

### 4.1 Common types and canonicalization

All object keys listed below are exact: unknown or missing fields fail. Nullable fields are present.
JSON uses existing `collection-canon/1` bytes and `content_sha256`; reject duplicate keys, non-finite
numbers and implicit type coercions. `D` means 64 lowercase hexadecimal SHA-256; `U` means UUID4 lowercase
32 hexadecimal characters; `T` means UTC RFC3339 timestamp. Integer fields reject booleans.
`Name` obeys section 2; `N` is a positive integer. All generated paths are confined relative POSIX paths,
resolved against the project root, with no links/reparse traversal. `Ref` is the existing validated
`file_reference` schema; use `project_root` as base for new references. No generic arbitrary-key extension
object is introduced. Upstream-owned document values keep their upstream validator and schema.

Atomic replacement writes a sibling temporary file, flushes and fsyncs it, and replaces the target.
This is a process-crash contract on the existing supported local filesystems. Machine/power-loss durability
and network filesystems are not claimed. Revision comparisons occur while holding project ownership.

### 4.2 Allocation ledger and creation transaction

`allocation.json`:

```text
{schema_version: "experiment-allocation/1", revision: nonnegative integer,
 families: [Family]}
Family = {base: Name, high_water: N, allocations: [Allocation]}
Allocation = {number: N, name: Name, reservation_id: U|null,
 origin: "reservation"|"legacy", created_at: T,
 publication: "prepared"|"published", presence: "present"|"tombstone",
 transaction: Ref|null, legacy_owner: Ref|null, tombstoned_at: T|null}
```

Families sort by base; entries sort numerically, with unique names/numbers/reservation IDs. `high_water`
equals the greatest recorded allocation and never decreases. A pin may create a previously unused number
below the high-water mark; automatic creation never fills a gap. A tombstone is permanent, including if
someone later puts a directory at that path; restoration is manual verified-input recovery, not allocation.
Reservation-origin entries have a transaction and reservation ID, and null legacy owner. Legacy entries
have null transaction/ID, a validated existing owner reference, and `publication: published`.
`presence: present` includes a prepared allocation whose final directory has not yet appeared.

`transaction.json`, immutable after publication:

```text
{schema_version: "experiment-creation-transaction/1", reservation_id: U,
 name: Name, base: Name, number: N, creator_invocation_id: U, created_at: T,
 metadata: Creation, initial_reservation: Reservation,
 source_capture: [CapturedSource], metadata_sha256: D, initial_reservation_sha256: D}
CapturedSource = {role: string, original_path: absolute POSIX string, file: Ref}
```

`source_capture` contains the project and applicable workflow YAML, generator/build templates and selected
catalog files actually used to form the request. Roles are unique and deterministic (`project`,
`generate_scenarios`, `simulate_system`, `build_model`, `generator_template`, `build_template`,
`waterbodies_template`, and `catalog_<index>` for precedence-ordered catalogs). Capture additional local
configured region/output-location file bytes when used, with roles `region` and `output_locations`.
No role is optional silently: applicability follows request mode; missing required files fail preflight.
Ref checksums address exact archived bytes. Referenced external datasets remain outside this small capture.
The transaction preserves the initial request and original metadata even after binding advances.

`experiment.yml` is the YAML serialization of the closed `Creation` object:

```text
Creation = {schema_version: "experiment-creation/1", name: Name, family: Name,
 number: N, reservation_id: U, created_at: T, creator_invocation_id: U,
 note: string|null, toolbox: {commit: string|null,
 commit_source: "git"|"baked"|null, dirty: boolean|null}}
```

Use `toolbox_identity()` verbatim, including the source-checkout and baked-commit fallbacks. Do not require
`git describe` or invent a version when unavailable. YAML bytes are serialized once and their exact digest
retained in the transaction. The name/family/number fields must agree with the ledger and directory.

### 4.3 Reservation and early request

```text
Reservation = {schema_version: "experiment-reservation/1",
 canonicalization_id: "collection-canon/1", reservation_id: U, name: Name,
 revision: nonnegative integer, state: "pending"|"resolved"|"simulation_bound",
 request: Request, request_sha256: D,
 seed: Seed, resolution: Resolution|null, simulation: SimulationBinding|null}
Request = {schema_version: "experiment-request/1", generation: GenerationRequest|null,
 selection: {mode: "project-generation"|"explicit-manifest", manifest: Ref|null},
 input_catalogs: [semantic catalog document], simulation: DeclaredSimulation}
GenerationRequest = {schema_version: "reservation-generation-request/1",
 n_realizations: N, simulation_window: {start: integer, end: integer},
 climate_perturbations: upstream-normalized perturbation object,
 water_year_start: uppercase month, requested_seed: "auto"|integer,
 generator_settings: generator_seed_projection result,
 run_group_id_capacity: N, source_request: SourceRequest, provider_code: code-inventory}
SourceRequest = {region: upstream region value, climate_source: string,
 historical_window: {start: integer, end: integer},
 hydrography: string, basin_index: string,
 local_inputs: [SemanticInput]}
SemanticInput = {role: "region"|"output_locations", path: absolute POSIX string, sha256: D}
DeclaredSimulation = {climate_source: string, model_root: confined POSIX path,
 outvars: [existing canonical output-variable names], model_request: ModelRequest|null}
ModelRequest = {basin: upstream effective basin configuration,
 climate: {selected: string, window: {start: integer, end: integer}},
 engine: {build_config: parsed upstream build document,
 waterbodies_config: parsed upstream update document},
 simulation_window: {start: integer, end: integer}, local_inputs: [SemanticInput]}
```

These upstream objects are value projections, not raw source blobs: normalize defaults using the same
WF1/WF3 helpers as execution and validate against their existing grammar. Preserve ordered lists such
as catalogs; discard YAML comments and mapping order. Expand configured path anchors before comparing.
Use the actual effective generator settings builder, then `generator_seed_projection`; do not make a
second list of generator scientific keys. Normalize omitted spell factors using `validate_spell_factor`.
Include capacity because it changes retained run-ID spelling, although it does not enter seed material.
`input_catalogs` always contains the complete effective `project.catalog` documents in precedence order,
independently of WF3 enablement or selection mode. Use the existing upstream catalog parser and path
resolution, including catalog-relative roots, so equal parsed text at a different anchor cannot hide a
different resolved input. Keep complete semantic documents conservatively: unrelated entry changes can
refuse a pending reservation, but comments and mapping order do not. Raw catalog bytes are captured in
the creation transaction independently. This replaces the WF3-only `SourceRequest.catalogs` projection;
there is one request-level authority, with no duplicate catalog fields in generation or model requests.

Every executing scientific input consumer uses this binding: WF1 model construction and forcing reads;
WF3 basin/historical-source preparation; WF4 elevation, forcing readers and unit interpretation even
with a ready explicit collection and WF3 disabled. WF0/WF2 shared region/climate producers use the same
project catalogs and must pass this guard before writing shared inputs. WF2's separate CMIP catalog and
overlay settings stay excluded: projection values never select generation or simulation inputs.
No producer may read a different effective project catalog from the admitted capture. A future consumer
introducing another catalog dependency requires explicit classification before it can execute; narrowing
the conservative projection needs separate evidence. Metrics-only retains its existing admission path.

`generation` is non-null exactly when WF3 will execute for this invocation, or when admitting an unresolved
project-generation request on the simulation-only runner. `selection.manifest` is non-null exactly for
explicit selection; validate the ready collection before reserving that form. Current selectors accept
only `manifest_path`; no subset-of-runs selector is added. On the live contract all `collection.series`
run IDs are selected in validated numeric order, including each unperturbed realization.

`model_request` is non-null when WF1 will execute: guard its effective basin/source/build recipe before
that producer. Otherwise native model bytes, when present, are checked through existing model-reference
guards, with an exact final check at simulation binding. WF1 observations/evaluation figures and
WF0/WF2 analysis settings are excluded; their shared input catalog dependency is guarded above. Metrics,
operation spelling, experiment name, output-root location, note, threads/batching, logs and plotting are
excluded from scientific comparison. Metrics-only bypasses this new request comparison entirely and
uses existing retained-response admission.

The implementation must make field classification closed at the source schemas: a newly introduced
WF1/WF3/WF4 field with no include/exclude rule fails the reservation projection test. Do not silently
hash arbitrary future keys or silently discard them. Existing upstream schemas remain authoritative for
their nested physics/catalog formats; no CST substitute schema for HydroMT/Wflow internals is created.

### 4.4 Seed, selection and simulation binding

```text
Seed = {state: "not_applicable"|"awaiting_sources"|"bound",
 requested: "auto"|integer|null, resolved: integer|null,
 seed_resolution: existing WF3 seed-resolution document|null,
 plan: Ref|null, source_identity_sha256: D|null}
Resolution = {resolution_mode: "project-generation"|"explicit-manifest",
 manifest: Ref, collection_id: D, collection_revision: D, run_ids: [decimal string]}
SimulationBinding = {simulation_id: D, intent: Ref, creator_archive: Ref}
```

`not_applicable` has all other seed fields null and applies to explicit reuse with generation disabled.
`awaiting_sources` has the original request and all other fields null. `bound` has every field non-null;
it stores the exact existing WF3 seed-resolution object, pinned immutable plan, and source identity digest.
The plan and source inventory must reproduce that seed-resolution object. Explicit integer seeds can
be reported immediately, but the full binding awaits the same verified plan/source identity.

`resolution` is null until the ready collection passes existing validators. Run IDs are unique decimal
strings in the producer's spelling and numeric order; never renumber them from the experiment suffix.
`simulation` is null until both existing intent and creator archive validate and agree. Their schema
versions are unchanged (`simulation-intent/1` and existing archive schema), despite Python `_v2` names.

`pending` has null resolution/simulation; `resolved` has non-null resolution and null simulation;
`simulation_bound` has both non-null. Seed binding alone leaves the state pending.
Allowed monotonic transitions, each atomic with `revision + 1`, are: bind seed; bind resolution; bind
simulation. Multiple facts may be bound in one transition when already available. Once non-null/bound,
a value cannot change; an equal retry is a no-op. The initial request and its hash never change. Invocation
failure or cancellation does not reset them. Readiness still requires `simulation.json` and verified
response inventory; the reservation's simulation binding is not a completion marker.

## 5. Binding and publication lifecycle

### 5.1 Admission before producers

Validate flags, selected operation and requested targets before mutation. Resolve the supplied project
root and compose configuration once from captured source buffers. Hold `archive_lock(root,
"project-execution")` from allocation/admission through source preparation, generation, binding and
simulation. This deliberately serializes the whole project, including different families, because the
model and source caches are shared mutable inputs. No new experiment lock, PID lease, or lock-age expiry
is added. Never reacquire the same lock in an in-process child; use the existing `run_owned` pattern.

Snapshot available creator configuration into the immutable transaction. Run execution from the same
captured values or a staged execution config, preserving original path anchoring and provenance. Recheck
dependency bytes before using them; a user edit during an invocation cannot silently change its admitted
request. Derivable pending-request and retained-model conflicts fail before any expensive producer.
Resolve once and carry the selected name through every stage; never run a second post-generation lookup.
Compare request-level catalog semantics before WF1/WF3/WF4 or shared preparation can write, including
pending explicit-manifest retries with generation disabled. Recheck captured catalog dependencies before
each consumer uses them. A semantic change during the invocation refuses that consumer; a comment-only
edit does not redefine compatibility, and execution continues to use the admitted captured semantics.

### 5.2 Existing WF3 seed algorithm and exact handoff

`generation_configuration(..., stage=False)` can plan without prepared sources, but its existing
`generation-request/2` contains paths/raw settings and is not the new semantic early guard.
`build_candidate_intent` needs prepared basin cells and historical climate, snapshots their identities,
builds effective generator settings, and calls `automatic_seed_v2(material)` for `seed: auto`.
The seed is deterministic; it is not random on each retry. Changing that algorithm is out of scope.

Add an optional owned reservation context to `generate_scenarios.run_owned`. After prerequisite source
preparation, branch on its seed binding **before `_plan_quietly`, ordinary plan selection or
`initialize_generation`**. An unbound reservation uses normal candidate planning, then a callback rechecks
the early request and pins the existing seed resolution, source identity and immutable plan before any
stochastic child. A bound reservation loads that exact plan with `read_pinned_plan`, validates the current
scientific request and prepared source identities against its binding, and takes the states below.
Never replace a pinned `create` plan with a newly selected `reuse_ready` plan or follow a changed pointer.

- **Ready collection:** use existing collection, creator/archive and installed-generator validators;
  require its exact collection identity, creator intent and seed evidence to agree with the bound plan.
  Validate manifest/revision and producer-owned run IDs, matching any retained resolution. Skip create
  initialization and stochastic execution; bind or confirm resolution and continue WF4. The plan bytes,
  digest and seed binding stay unchanged, including `decision: create` after the first successful WF3.
- **No namespace yet:** only a bound `create` plan with no initialization evidence or later binding may
  enter existing initialization and generation. Missing data for an initialized, resolved or reused
  collection is loss/corruption, not permission to create again.
- **Initialized but incomplete:** a valid initialization receipt and matching creator evidence without
  a ready collection produce an explicit incomplete-WF3 diagnosis before ordinary planning/callbacks.
  Preserve the plan, receipt and namespace; this task does not resume partial WF3 execution.
- **Interrupted initialization:** an occupied namespace without complete matching initialization evidence
  produces a distinct partial-initialization diagnosis; preserve all evidence and refuse. Unknown or
  inconsistent occupants also refuse. `--recover-reservation` repairs neither WF3 partial state.

Keep the orchestration/publication adapter outside the unchanged provider inventory (sections 6 and 8.3).
Use existing canonical-byte/hash helpers and `atomic_record` to publish the immutable plan object, bind
its reference atomically, then call unchanged `publish_plan_pointer` with that exact plan. Do not split
or edit `generation_plan.py` to insert the callback. Verify immutable-path collisions byte-for-byte.
Before binding, an orphan plan is harmless and no stochastic work may start. After binding, reconcile
the discovery pointer from the validated pinned plan only for an admitted state above; pointer repair
does not grant namespace repair. Changed prepared sources refuse before generation. WF3's existing
immutable publisher remains the collection owner; the reservation records references only. Fresh normal
ready reuse obeys the same creator/seed checks and resolves exact collection/run identities before WF4.

**Decision D1, G1 approved 2026-10-10:** permit `awaiting_sources` at initial reservation and persist
the numeric automatic seed immediately after prerequisites, before stochastic production. This refines
the plan's phrase “resolved and persisted once ... at reservation”; it preserves its scientific intent
without changing the algorithm. Numerical equivalence remains the section 8.3 acceptance obligation.
An experiment-derived substitute seed is not an acceptable implementation shortcut.

### 5.3 Ledger commit and directory publication

Under the project lock, validate the entire ledger and scan direct experiment directories without
following links. On first adoption, reconcile every canonical numbered owned directory into history;
exclude valid dated legacy names. Unknown/corrupt numeric ownership fails adoption rather than lowering
the high-water mark. On later calls, reject newly appearing unledgered numbered directories; adoption
must not silently legitimize an interrupted foreign writer. Missing published allocations become
tombstones in a writing invocation, and are reported as missing in preview without writing.

Creation order:

1. Select/validate the candidate and allocate a new reservation UUID in memory. Capture sources, construct
   immutable metadata and the initial pending reservation, and write/fsync all transaction files in a
   unique transaction directory. Publish `transaction.json` last, with all payload digests.
2. Atomically replace the ledger with a new `prepared` allocation and incremented revision/high-water
   mark. **This is the allocation commit point.** From now on the number is never reusable.
3. Atomically rename the complete staged `experiment/` directory to the absent final experiment path on
   the same filesystem. Refuse any existing destination; never merge directory contents.
4. Validate the final pair against the transaction and atomically mark `publication: published`.
   Retain `transaction.json` and captured source bytes as creator/recovery evidence.
5. Only now print the committed creation and start producers. Later bindings atomically replace only
   `reservation.json`. They do not rewrite the transaction's original request or metadata.

Temporary files are never authoritative. Reader validation uses ledger/transaction IDs and digests,
not directory existence. There is no second general transaction journal: the prepared ledger entry and
immutable transaction are the redo recipe. Source capture before ledger commit is not an allocation.

### 5.4 Crash and recovery matrix

Ordinary retry automatically resumes a valid published reservation. Interrupted publication requires
`--recover-reservation` and the exact selected allocation. The parent first obtains the existing OS lock.
Lock acquisition alone does not establish descendant termination. Supported writing execution requires
the existing Windows job lifetime mechanism and the parent-death acceptance evidence in section 8.5.
Preserve the current refusal to launch writing children on unsupported platforms, including Linux;
Linux record-protocol fixtures do not qualify Linux workflow recovery. Age and recorded PID alone never
suffice. Recovery is repeatable; it completes the already-committed recipe, not current config.

| Durable boundary | Required action |
|---|---|
| Partial transaction, no ledger entry | Not allocated; ignore for selection, report orphan evidence. |
| Complete transaction, no ledger entry | Still not allocated; no producers allowed; no automatic promotion. |
| Prepared ledger; stage only | Explicit recovery verifies recipe, renames and commits. |
| Prepared ledger; valid matching final | Explicit recovery completes ledger publication only. |
| Prepared ledger; neither stage nor final | Refuse missing evidence; number stays consumed. |
| Prepared ledger; both stage and final | Refuse ambiguous state; never merge or delete either. |
| Prepared ledger; unknown final occupant | Refuse collision; preserve transaction and all occupants. |
| Published ledger; absent directory | Permanent tombstone; next new allocation exceeds high-water. |
| Published directory; bad metadata/reservation | Refuse corruption; no fresh record from current config. |
| Seed bound; pointer absent/stale | Validate section 5.2 state before pointer reconciliation. |
| Bound create plan; ready collection | Validate ready evidence; skip initialization/redraw; keep plan. |
| Bound create plan; no namespace/evidence | Existing initialization, only as allowed by section 5.2. |
| Valid initialization; collection incomplete | Diagnose incomplete WF3; preserve and refuse. |
| Partial initialization or inconsistent namespace | Diagnose initialization failure; preserve and refuse. |
| Resolution bound; no simulation | Verify collection and immutable inputs, then freeze. |
| Simulation intent only or archive transaction incomplete | Explicit paired-freeze recovery below. |
| Complete simulation with corrupt response | Refuse; no recovery flag authorizes replacement responses. |

The conditional immutable `simulation-freeze.json` is closed:

```text
{schema_version: "experiment-simulation-freeze/1", reservation_id: U,
 simulation_id: D, intent: existing simulation-intent/1 object,
 archive_record: existing run_record_document object, payloads: [FreezePayload]}
FreezePayload = {archive_path: confined relative POSIX path, file: Ref}
```

Store exact payload bytes under `freeze-payloads/`, then publish the recipe last. Payload paths are unique;
their set and checksums must match the archive record's complete inventory. All references use the project
root base. The recipe's reservation/experiment/simulation owners must agree with the existing binding.
No intent or archive write is allowed before this recipe validates; no native output before both publish.

Current `freeze_simulation_v2` writes intent before creator archive and cannot recover every interruption
between them: its existing-intent branch immediately reads the paired archive. P3 must make this boundary
recoverable for reservation-owned experiments without relaxing legacy validation. Retain the prepared
archive payload and intent as a verified redo recipe before writing either; use existing archive
transaction/recovery machinery for the archive. `--recover-reservation` may finish a missing paired
archive only when its payload is recoverable, owner/intent hashes match, and no unknown native responses
exist. It must never regenerate the creator archive from current user files. Unrecoverable legacy partial
freezes remain a diagnosed limitation. After both validate, atomically bind `reservation.simulation`.

Invocation history records cancelled/failed/successful attempts independently. No failure marks a pending
experiment complete. A dead process with a retained “running” invocation is historical evidence, not a
reason to steal ownership or rewrite scientific records.

## 6. Integration and capability map

Before P2/P3 runtime edits, capture the matched pre-change reference required by section 8.3.
P2 implements schemas, pure selection/preview, ledger adoption and recovery as an inactive library.
P3 activates them in both runners in one usable integration unit. `reservation.py` owns the early request
projection and binding checks; `allocate.py` owns naming/ledger semantics; existing modules own scientific
collection/simulation identity. Python-engineer implements these units and their tests. No R/Julia
algorithm change is planned; model-builder exercises interruption/reuse, and model-validator judges the
claimed retained-input/output equivalence. The requesting owner accepts compatibility behavior.

The inventory's P3 entries for `generation_plan.py` and other generation providers mean reuse and
exercise, not edit permission. Pin the complete provider inventory before runtime changes and keep its
membership and normalized source hashes unchanged. Place section 5.2's adapter in the existing planned
`reservation.py`/runner changes, outside that inventory, reusing canonical publication functions.
Verify the resulting import closure still excludes the adapter. A necessary inventoried edit blocks the
auto-seed no-drift claim: report the conflict to the owner before implementation; never change seed/hash
semantics, inventory exclusions or reference bytes to hide it.

Runner admission carries `{root, name, reservation_id, request_sha256, mode}` as an internal immutable
context. Proposed child environment fields are `CST_EXPERIMENT_NAME` and `CST_EXPERIMENT_RESERVATION_ID`;
they identify records, not authority by themselves. The DAG validates the parent-owned reservation and
current operation before using the name. It does not allocate. The all-workflow runner calls the owned
simulation path directly under its existing lock, rather than spawning a public runner that relocks.
The standalone runner acquires that lock itself. Invocation records record the resolved experiment in
their existing `plan` payload, including preview reason, without changing immutable source captures.

Metrics-only resolves a selected existing experiment once and passes it into `metrics_only_configuration`
and `cross_workflow_leaves`; it must not consult live generation/model data or reserve a name. Default
family selection is permitted only if a complete selected allocation exists. Existing retained simulation
and metric validators still govern admission.

Dry runs, `--unlock`, DAG rendering and validation use pure preview. They do not acquire an allocator
lock that creates allocation files, reconcile tombstones to disk, stage reservation sources, publish
metadata or mutate bindings. Existing inspection/invocation logs may still be written. A fresh root's
predicted number is advisory, and missing upstream sources are reported as unavailable preview detail.
Do not resolve an automatic numeric seed speculatively. Existing executor-side publication remains gated
off in every non-producing invocation, including passthrough `-n` and `--dry-run` forms.

Capability slots are an interface map, not a claim that this repository implements `cst-run-control`'s
full managed-root CAS/fencing/object-store profile. No managed root is declared by this change; the
existing local project lock remains its narrower contract. Any future managed adapter must supply that
contract separately and must not equate an experiment number with its opaque run ID.

| Slot | Binding/change | Implementer; validation authority |
|---|---|---|
| `decision_framing` | Case decisions unchanged | Case manager; case owner |
| `data_adapter` | HydroMT/WF3/WF4; guard all input catalogs | Python engineer; geospatial analyst |
| `ensemble_generator` | WF3/weathergenr; bind seed/plan | Python engineer; model validator |
| `simulation_engine` | Existing Wflow; guard name/intent handoff | Python engineer/model builder; validator |
| `system_model_validation` | Existing scientific assessment unchanged | Model validator; case authority |
| `impact_model` | Not applicable; no impact component introduced | Not applicable |
| `performance_analysis` | Metric sets; resolve retained experiment | Python engineer; model validator |
| `robustness_evaluation` | No metric/acceptance-rule change | Case manager/analyst; case authority |
| `projection_overlay` | WF2 unchanged; never used in request/seed | Existing analysis authority |
| `orchestrator` | Runners/Snakemake carry one reservation | Python engineer; contract tests/owner |

New record versions are `/1`; existing collection, seed, simulation and metric schema versions are
retained. Implementation records commit and lock/environment identity in existing provenance. The
request projection version must change when semantic include/exclude rules change; do not reinterpret
persisted `/1` bytes. The complete schema/consumer inventory determines any later migration, not tool
package names. No stage ordering or projection dependency changes here.

## 7. Alternatives and consequences

**Chosen: explicit creation plus durable allocation and two-stage binding.** It adds small durable
metadata and a recoverable publication protocol, but accidental reruns keep their identity and mismatches
surface before expensive work. Early source hashes cannot guarantee future immutable inputs; final
collection/model/adapter/environment checks remain mandatory.

**Folder scanning only.** Simpler and sufficient for disposable scratch runs, but cannot preserve deleted
allocation history. It fails the user's no-reuse requirement and is therefore rejected for this interface.

**Increment on completion or request change.** Convenient for a batch submission API whose commands always
mean new work. Here a harmless rerun could launch an expensive experiment or hide an accidental scientific
edit. The recorded continuation behavior rules it out.

**One atomic database instead of JSON ledger plus staged directory.** SQLite transactions could simplify
ledger mutation, but would not make native directory publication atomic with the database. It still needs
a redo protocol, adds a new storage surface, and offers little under the existing single-project lock.
It becomes preferable if concurrent independent project writers or substantial query needs are authorized.

**Resolve an automatic seed at first reservation.** Exact preservation is possible if source inputs already
exist, or if reservation is delayed until after preparation. Delaying reservation loses the early identity
guard; requiring pre-prepared sources removes fresh-root convenience. Changing to a name-derived/random
seed changes scientific results. D1 selects a pending seed with explicit pre-generation binding.

**Full run-control migration.** Managed CAS claims, fenced inventories and attempt-private object stores
would broaden safety beyond today's local lock but require a repository-wide namespace/output migration.
This task does not establish that authority or conformance. Keep the narrow existing execution ownership.

**Separate per-experiment locks.** They could increase throughput, but two experiments still share mutable
model/source production. They are unsafe without a separate shared-input concurrency design. The current
coarse lock is deliberately retained.

## 8. Evidence and verification

### 8.1 Evidence register

Code inspected at `6998d0fd1f460a78934bc79aeb546c5184ba3af8` in the session-1 worktree. Canonical task
plans were read from the primary checkout because the session's sparse checkout excludes tracked task
files. No other worktree's WF3 changes were read or assumed. Facts below are source inspection, not
runtime verification. The author ran no scientific jobs and makes no prototype-tested or scientific
qualification claim for the proposal.

| ID | Premise and source | Status; precision | Falsifier |
|---|---|---|---|
| E1 | `allocate.py`: dated defaults, no history | Source verified | Current allocator tests |
| E2 | `run_workflows.py:925`: lock spans children | Source verified | Two-process test |
| E3 | `workflow_config_snapshot.py:597`: OS lock | Source verified | Kill parent/child |
| E4 | `generation_plan.py:423`: source-derived seed | Exact call verified | Fresh-root probe |
| E5 | `generate_scenarios.py:run_owned`: prep before plan | Source verified | Callback ordering |
| E6 | `scenario_rows.py:validate_forest`: padded IDs | Source verified | Producer fixture |
| E7 | `collection_resolution.py`: manifest-only selector | Source verified | Extra-key rejection |
| E8 | `simulation_record.py:446`: intent before archive | Source verified | Crash between writes |
| E9 | `batch_staging.py`: TOML/simulation hash reuse | Source only | Interrupted multi-run |
| E10 | Completed staged member survives the section 8.4 boundary | Unverified | Bytes/execution probe |
| E11 | Request excludes execution-only edits | Proposed | Projection mutation tests |
| E12 | Windows parent death excludes later descendant writes | Open gate | Section 8.5 lifetime probe |
| E13 | No drift on declared matched population | Open gate | Section 8.3 value comparison |
| E14 | Local publication yields stated process-crash states | Open gate | Section 8.5 boundary faults |

E9 has a concrete limit: staging markers presently do not hash CSV contents, and restoration moves CSVs
one by one. Source inspection proves an intended reuse mechanism, not integrity across every kill point.
P3 must not label arbitrary staged files valid. The interrupted-run acceptance must inspect its actual
supported boundary; a newly demonstrated safety gap is a blocker to the relevant reuse claim, not license
to redesign native-output repair or silently delete final responses.

Domain review of v1 accepted the source-derived seed rationale and found the missing WF1/WF4 catalog
guard. V2 addresses it in section 4.3. The review and this revision provide no runtime evidence for
E10/E12/E13/E14. Their observations and acceptance outputs remain mandatory; ledger acceptance records
a resolved design requirement, never a passed implementation gate.

### 8.2 Claim-to-check plan

Use isolated roots under `.tmp/scratchpad/t2610032349/`, with no production writes. Every evidence row
records tested commit, command/result, environment, config/input identity and reusable output root.
Do not run the stale baseline manifest as a naming gate. Cross-revision no-drift is required acceptance
on the declared representative population: capture section 8.3 evidence before P2/P3 runtime edits.

| Claim | Check and input case | Root/reuse |
|---|---|---|
| Selection rows | Parametrize section 2 cases | `allocator/` synthetic |
| Growth/pin/deletion | `_99`, `_100`, pin 37, missing highest, unknown occupant | Same allocator cases |
| Legacy precedence | Valid dated/unnumbered/numbered owners and malformed twins | `legacy/` |
| Exclusive ownership | Two subprocess creators; competing same-name writers; parent kill | `ownership/` |
| Publication boundaries | Crash after each step; recover twice | `crashes/<boundary>/` |
| Seed/request binding | Auto pending, request/source edits, same integer seed | `binding/` |
| All catalog consumers | WF3-off WF4 and WF1 mutations; harmless edits | Same binding cases |
| Exact selection reuse | WF3 off, original manifest, changed unused WF3 config | Same binding cases |
| Preview purity | Before/after bytes/inventory at every preview entry | `preview/` |
| Runner parity | Both runners: name, invocation plan, DAG/log paths | `runner/` mocked producers |
| Bound create continuation | Completed WF3, interrupted WF4, retry; no redraw | Same runner cases |
| Partial native reuse | Section 8.4 byte equality and no re-execution | `rapid-interrupted/` |
| Complete/metrics-only | Same root, intact rerun and removed derived output | Reuse rapid execution |
| Native corruption refusal | Mutate copied native response; no replacement/deletion | `rapid-tampered/` |
| Scientific invariance | Section 8.3 matched forcing/native values | `reference/`; fresh e2e candidate |
| Full integration | Fresh all-five rapid at landing; required skips fail | Reuse e2e root |

Cheap falsifiers per new mechanism are respectively: duplicate number under concurrent creation; ledger
forgetting deleted maximum; accepted changed early field; stochastic child starting before seed binding;
different selected name after WF3; preview creating a record; recovery constructing metadata from current
config; and an owned crash state with no deterministic recovery/refusal rule.

Focused starting commands are `pixi run pytest tests/test_experiment_allocation.py`,
`pixi run pytest tests/test_simulation_runner_v2.py tests/test_run_workflows.py`, and the touched helper's
existing tests. Add proposed reservation tests to those focused checks when implemented. Run touched-file
Ruff checks; run `tests/test_cli.py` when DAG/signature inputs change. At approved batch landing, shared
runtime changes owe `pixi run test-full` and fresh all-five `pixi run test-e2e` under the live validation
ladder. A full-suite pass covers fast; reuse fresh e2e outputs instead of another redundant rapid run.
Redirect command output to files and inspect required skips. Execution success alone does not discharge
input identity, retained native-value, or visual acceptance.

In the cheap runner fixture, first create with WF3 enabled, publish a producer-derived ready collection,
interrupt WF4, then retry ordinarily with WF3 still enabled. Assert identical reservation ID, pinned plan
bytes/digest and seed; ready validation and resolution confirmation precede WF4, with no second create
initialization or stochastic launch. Repeat after completing the experiment. Separately exercise valid
initialized-but-incomplete and interrupted-initialization namespaces: each must give its distinct
section 5.2 diagnosis before `_plan_quietly` or the unbound callback, preserve evidence, and launch no
generation/WF4 child. Cover stale pointers and changed source/creator evidence in the same fixture.

The completed domain review informs this revision and G1's recorded rulings. Contract tests judge
record/protocol correctness; model-validator judges reproducibility claims from the representative run.
Case manager retains case thresholds, metric choices and run decisions. A failing scientific equivalence
check returns this contract for revision rather than updating reference results to obtain a pass.

Catalog cases must exercise a pending ready explicit-manifest reservation with WF3 disabled: change
the selected elevation entry and, separately, its forcing reader/unit interpretation; refuse before WF4
preparation. With WF1 enabled, change a selected model/forcing entry and refuse before model production.
Repeat with comments/mapping-order changes and require compatibility. Assert captured dependency coverage
for every active consumer in section 4.3, including shared preparation; mutate precedence order and
catalog-relative anchors as separate semantic cases. Compare before/after producer-call traces and
request bytes, not only return codes. No full workflow run is needed for these projection/refusal cases.

### 8.3 Mandatory matched reference and no-drift acceptance

The claim is exact same-environment numerical agreement for the declared rapid comparison population,
not scientific qualification of that basin or universal equality for every configuration. A reference
must exist before P2/P3 edit runtime code. Missing data, an unusable engine, nondeterminism or an incomplete
reference blocks that handoff; report the blocker rather than silently narrowing this required claim.
Do not use an existing output directory as evidence until its inputs, completion and inventory validate.

The model-builder captures the reference on the recorded pre-P2 commit into an isolated
`.tmp/scratchpad/t2610032349/reference/` root. Keep it outside every candidate write path. Use copies of
the rapid project/workflow configs with only the output root redirected and analysis-only WF0/WF2
disabled for this reference; retain the original rapid seed `123`, two realizations, full perturbation
grid, 2046–2054 simulation period and configured native output variables. WF1, WF3 and WF4 provide the
scientific comparison; WF0/WF2 remain covered by fresh all-five integration at landing. Record exact
commands, effective configs and all deviations before execution. Resolve data/engine access and available
disk space first; filesystem presence or an executable alias is not proof that a scientific run succeeds.

Capture the following evidence before permitting runtime edits:

1. Exact commit, clean/dirty state, commands, effective/source config bytes, catalog order and resolved
   dependencies, `pixi.lock`, Julia `Manifest.toml`, actual Python/R/Julia/Wflow/weathergenr versions and
   thread/batch settings. Retain inventories/digests of prepared basin cells, historical climate and
   native model inputs, including their coordinates, units, calendars and missing-value conventions.
   Pin the complete `repository_code_inventory` result from `GENERATION_CODE_ENTRIES` and
   `GENERATION_INVENTORY_EXCLUDED`: all members and normalized source hashes, including transitive
   imports and `generation_plan.py`. Compare it unchanged on the candidate before auto generation.
2. Successful generation and simulation with validated collection, exact ordered producer run IDs,
   effective seed/seed-resolution material, immutable plan, creator records and response inventory.
   Retain all realized forcing and native responses needed below; account for temporary-file cleanup
   before launch and use the existing supported retention control where needed. Preserve engine-ready
   downscaled forcing as well as collection series; do not substitute summaries for arrays.
3. A separate automatic-seed generation reference using the same prepared source snapshots and rapid
   generation settings with `seed: auto`, under a separate isolated root/request. Save its effective
   integer, source identities, seed material and full realized collection. This additional case tests
   D1's source-dependent path; explicit-seed rapid alone cannot do so. No additional native simulation
   is required for this auto case; that exclusion is reported with its generation-only claim.

On the final candidate, reuse the fresh all-five rapid e2e output for the explicit-seed comparison if
its effective scientific inputs, source/model content, environment and execution settings match the
reference. If they do not, that root cannot discharge no-drift: diagnose the mismatch, then use a matched
candidate run only for the uncovered claim. Regenerate the auto-seed collection from the retained
prepared sources under the candidate's owned reservation path, with no completed collection available
for shortcut reuse. This tests actual generation after binding, including a changed experiment number.
Record the candidate's new code identity; do not rewrite provenance to imitate the reference.

Pair all members by exact ordered run ID and perturbation/realization coordinates, not directory name.
For the explicit-seed case compare every realized collection series, every selected engine-ready forcing
array and every native response over its full emitted period and all configured variables. Require equal
dimensions, coordinates/timestamps, units/calendars, variable sets, missingness masks, infinity signs and
exact finite values after the same reader decoding. Require the same checks on all realized collection
series for the auto case, plus identical effective seed and scientific seed material. Source/model
inventory equality is an input gate; it is not a substitute for these value comparisons.

Accept zero unexplained finite-value differences and zero structural/missingness differences. Report
compared counts, any missing members, excluded products and the largest absolute/relative difference
(both zero on a pass). Archive/name/path/timestamp metadata and code fingerprints outside the generation
provider inventory may differ for documented reasons; list them without masking numerical fields.
Provider inventory/hash changes are not harmless provenance differences for automatic seeds and block
this claim under section 6. No opportunistic tolerance, refreshed
reference or stale baseline update can convert a mismatch to a pass. Model-validator must investigate
any difference and issue a verdict on the declared population. Derived metrics/figures retain their
existing gates; this no-drift oracle specifically covers realized inputs and native responses.

Retain the reusable reference until implementation acceptance. Preserve commands, identities, comparison
results and specialist verdict in existing task evidence, with the reference root and retention reason;
do not commit bulk outputs. Interruption equivalence below is a separate within-candidate comparison.

### 8.4 Bounded interruption evidence and staging limits

The supported probe interrupts after one member's complete CSV set and matching input `.ok` marker are
published to staging, before restoration starts, while at least one selected member remains unfinished.
Use the same candidate, sources, seed, run IDs, model, environment and execution settings as an
uninterrupted comparison. Preserve producer completion evidence, enumerate/hash every staged CSV before
interruption, and retain independently observed per-member engine launch/completion records. A valid
probe member needs complete expected files and reader validation plus those observed bytes; a matching
marker alone does not prove content integrity. These probe checks do not add a production checksum schema.

After supported retry, require byte-identical responses for that member at the final retained paths,
no second engine launch for its run ID, and complete validated immutable response inventory. Compare all
final native values to the matched uninterrupted candidate using section 8.3's exact comparison rule.
Verify that unfinished members restart from original inputs through existing supported controls. A pass
establishes only this interruption boundary; it does not establish preservation through every crash.

Test restoration interruption and staged tampering separately on copies as diagnostic probes: interrupt
between individual CSV moves; alter a readable staged CSV while keeping its input marker. Record observed
recovery/refusal/re-execution, inventories and byte changes. The current marker cannot prove untampered
content, and restoration consumes markers/files incrementally. These states remain outside the supported
reuse claim unless separate evidence establishes support; never label a marker-only reuse integrity-safe.
Any changed/deleted final immutable response or failure at the promised supported boundary blocks
acceptance. Broader staging safety gaps are reported as existing limitations for owner disposition, not
repaired silently in this task. `--recover-reservation` grants no authority over native staged responses.

### 8.5 Ownership and filesystem evidence by platform

E12 stays open until a Windows probe observes a live writing descendant through forced parent death.
Record parent/descendant identities, writes before termination, termination observations, and a competing
recovery owner's lock-acquisition event. Include a grandchild where the production launch path creates
one. Require all sanctioned writing descendants to terminate and no writes after recovery ownership;
monitor through recovery completion. Repeat with a slow-writing child so a normal early exit cannot
make the test pass vacuously. A failure blocks recovery support; source inspection of `archive_lock` or
Windows jobs is insufficient. Keep the existing unsupported-platform writing refusal and test it.

E14 stays open until process-fault injection covers each durable creation boundary in section 5.3, both
sides of seed binding/pointer update, and each paired intent/archive/binding boundary in section 5.4 on
the supported Windows local filesystem. Include partial payloads and unknown final occupants. Assert
exact ledger/record/inventory outcomes, consumed numbers and no producer before valid publication;
recover each recoverable case twice and require the second attempt to leave authoritative bytes intact.
Refusal cases preserve evidence and never reconstruct scientific records from current config.

Linux synthetic record/rename tests may check protocol logic separately. Label their platform, filesystem
and fixture-only scope; they neither launch supported writing workflows nor demonstrate Linux child
lifetime/recovery safety. This change preserves that existing platform limit. Power loss and network
filesystems remain excluded. Record Windows lifetime evidence separately from each platform's record
tests so neither is cited as a substitute for the other.

## 9. Migration and decisions

Existing experiment folders and schemas remain in place. First writing adoption imports only verifiable
canonical numbered ownership; dated legacy names never raise a high-water mark. No directories are moved,
deleted or auto-renamed. Existing unowned numbered/legacy folders require diagnosis. Tombstones remain
even after deletion; numbers are allocation history rather than a compact directory count.

P4 updates live config templates, scripts/README, root README, running/configuration guides, retained
handoff and WF4 reference pages. Retire helper mutation commands with a clear error pointing to the runner
flags; retain preview/advice. Keep old function symbols only where a documented compatibility adapter can
remain read-only; no old mutating allocator may bypass the ledger after P3 activation. Update all callers
together. No source config migration runs automatically.

G1 approved D1's pending-source timing, explicit `--recover-reservation`, engine transaction records and
the all-consumer catalog guard on 2026-10-10; it required bounded interruption evidence and a matched
pre-change reference. G2 exact-byte approval remains pending. The sole combined review found fast-1 and
fast-2; v3 supplies bounded fixes for owner ratification after the driver's source/delta check. No further
review round is authorized, and this revision claims neither reviewer convergence nor acceptance.
All prior selection/continuation decisions are preserved. No additional scientific parameter or case
choice is requested. Full managed-run conformance, Linux writing support and native partial-output repair
remain outside scope. Reference capture, numerical validation and Windows lifetime/filesystem evidence
are implementation obligations still unexecuted, not unresolved architecture decisions.

2026-10-10 — v1: preserved the behavioral plan; specified closed records, monotonic bindings, local-lock
publication/recovery, consumer ownership, source-evidence limits and runtime falsifiers. G1/G2 pending.

2026-10-10 — v2: applied G1 and domain-1 through domain-4; moved catalog semantics to the common request,
bounded staged reuse, made pre-P2/P3 matched reference/no-drift acceptance mandatory, and separated Windows
lifetime/publication gates from Linux fixture evidence. Finding dispositions are in `ledger.md`.

2026-10-10 — v3: addressed fast-1 with bound-plan dispatch, verified ready reuse and distinct partial-WF3
refusals; addressed fast-2 with an unchanged full provider inventory and external publication adapter.
Added focused retry/no-redraw cases and constrained auto-seed provenance differences. Owner ratification
remains pending; part-by-part dispositions and source premises are in `ledger.md`.
