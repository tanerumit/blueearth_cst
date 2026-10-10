# Numbered experiments and explicit creation

Status: planning decisions recorded; implementation pending contract review.
Date: 2026-10-10. Lifecycle: task-owned working plan; revision record append-only.

## 1. Overview

Default to `stress_test_01`, then `stress_test_02`, and so on. A plain run selects the highest allocated
number in the chosen family, even when complete. Only `--new-experiment` deliberately advances it.
An explicit numbered name selects that exact experiment. Changed scientific inputs cannot silently
retarget an existing experiment, including one interrupted before simulation started.

Creation reserves an identity and records intent; generation resolves the requested collection;
simulation binds exact selected runs and immutable inputs; execution retains completed work.
The user receives an explicit selection message, a creation note and actionable mismatch diagnostics.
An experiment is a WF4 simulation identity, not a version of the entire project or its upstream outputs.

This expands the original naming task. It specifies behavior for implementation, rather than claiming
the new records or flags already exist. Contract review must reconcile the active WF3 run-id work and
the existing simulation schemas before executable changes; do not duplicate collection ownership.

Contents: [Selection](#2-selection-and-entry-points), [Binding](#3-binding-and-recovery),
[Ownership](#4-allocation-and-ownership), [Outputs](#5-outputs-and-compatibility),
[Acceptance](#6-acceptance-and-implementation), [Tradeoffs](#7-tradeoffs-and-revisions).

## 2. Selection and entry points

- Unset/null `experiment_name` means base `stress_test`. A non-numbered value supplies another base.
- Plain execution continues the highest allocated number for that base; if none exists, create `_01`.
  Highest means numeric allocation order, not modification time or completion status.
- `--new-experiment` allocates the next number even with identical scientific inputs. It does not imply
  a fresh stochastic realization; use the existing generation/seed controls for that separate intention.
- A canonical suffix is `_01` through `_99`, then `_100`, `_101`, etc. Numbers are positive and use at
  least two digits, without extra leading zeros. Reject `_00` and noncanonical numeric suffixes.
  A trailing numeric suffix is reserved for selection: `seasonal_2026` pins number 2026; use a base such
  as `seasonal_2026_test` when the year is descriptive. Preserve the existing overall name constraints;
  refuse length overflow explicitly before allocation. Never truncate or silently cap coverage.
- A numbered name pins exactly that identity. If never allocated, execution may create that number;
  update the family high-water mark. A deleted/tombstoned identity cannot be recreated by this route.
- A pinned name plus `--new-experiment` is an error. `--note` is accepted only for creation requested
  through `--new-experiment`; record it once. Reject notes on continuation and do not amend old notes.
- Support the same creation flags and resolver in `scripts/run_workflows.py` and
  `scripts/simulate_system.py`. Carry the resolved name unchanged to the DAG and invocation record;
  never resolve again after upstream producers. Do not rewrite the user's source configuration.
- Reject creation flags when WF4 is disabled, or for metrics-only operation. Metrics-only requires a
  selected existing experiment with complete retained responses; it never allocates a new experiment.
- Dry runs, DAG rendering and validation preview selection without reserving numbers or publishing
  experiment records. A predicted new number is advisory and can change before execution. Existing
  inspection logs are allowed; zero mutation applies to allocation, binding and experiment state.
- Retire `suggest_experiment_name.py` as an allocator: keep a read-only preview/advice role using the
  shared resolver, and reject former creation/config-edit behavior with replacement instructions.

Before expensive work, display output root, resolved name, new/continuing status and scenario request
or exact selection when known. Print a second handoff once generation resolves the collection/runs.
Repeating `--new-experiment` after failure creates another identity; diagnostics say to omit it to resume.

## 3. Binding and recovery

**Two stages of binding.** At reservation, record the effective scientific generation request (when
generation is enabled) or explicit collection/run selection, plus declared simulation settings.
Once producers finish, resolve and freeze the exact collection/run selection and existing immutable
simulation intent before simulation work. Neither binding is inferred from completion status.
Store pending/resolved state explicitly; a pending record is not a ready simulation.

Compare effective scientific settings and selected inputs, not raw YAML bytes. Comments, formatting,
core counts and notes do not redefine scientific identity. Preserve source archives for provenance.
An automatic seed must be resolved and persisted once for the reserved generation request; resume
must recover it, not draw another. Reusing a ready collection must not imply a seed redraw.
Compatibility follows the actual resolved selection: changing WF3 settings does not necessarily change
WF4 when WF4 explicitly selects the original collection and generation is disabled.

Check conflicts derivable from retained intent before expensive producers. Recheck exact input identity
after producers, since changed model bytes or regenerated collections may only then be observable.
Do not claim numbering preserves the mutable WF1 model: existing model-drift guards remain necessary.
This task adds no model-copy or revision-management subsystem.

If intent differs, stop and identify changed fields. Offer two actionable routes: use the retained
creator configuration and verified collection/run references to resume, or use `--new-experiment`.
Do not automatically restore files, overwrite the current config, or refresh the frozen reference.
Retained snapshots are recovery evidence; missing external inputs require verified restoration and
cannot be repaired merely by pointing at a config archive.

**Resumption scope.** Preserve valid completed runs. Restart an interrupted Wflow run from its original
inputs when no supported checkpoint exists; do not promise continuation from the last simulated step.
Use existing supported incomplete-job recovery controls, exposing their required command in the
diagnosis. Never delete native responses or bypass immutable guards automatically to force a rerun.

For a completed experiment, a plain run is a no-op only when requested outputs are intact and current.
Missing derived metrics/figures may be regenerated from verified retained responses. Missing/corrupt
native responses must fail integrity checks and require restoration of recorded bytes, or a new
experiment; no silent replacement under the old identity. Changed simulation inputs require a new
experiment. Additional metrics use existing immutable metric sets; figure-only edits do not allocate.
Toolbox/environment changes follow existing fingerprint and compatibility contracts, not a blanket
promise that equal configuration permits reuse.

## 4. Allocation and ownership

Keep a persistent per-family high-water mark and allocated identity history under the project engine
root. Reconcile recognized existing numbered experiment ownership before first adoption; ambiguous
or corrupt entries fail rather than being ignored. Legacy dated folders never participate in numbering.
Deletion leaves an allocation tombstone: plain selection of a missing highest identity reports it,
does not fall back to an older experiment, and offers a new allocation above the high-water mark.
Abandoned reservations retain their number. Gaps are valid and never filled automatically.

Serialize ledger updates and publish records atomically using existing project ownership facilities.
Two creators obtain distinct names; two writers targeting one experiment cannot mutate it concurrently.
Hold ownership across generation/binding/simulation for one invocation. Scope is one machine; no new
multi-user network-filesystem lock protocol. Never reclaim a lock on age alone.

Crash recovery must distinguish a committed reservation, a recoverable owned transaction and an
unrecognized directory. A directory without valid ownership is never treated as empty. Verify an
interrupted writer is inactive before explicit recovery; never reuse a number exposed by a durable
reservation. Exact journal/record schemas and publication sequence belong to implementation review.
Keep cancellation/failure separate from scientific readiness; record invocation outcome using existing
history rather than declaring an incomplete experiment complete.

## 5. Outputs and compatibility

Proposed generated paths, relative to the chosen project output root:

```text
config/                                         # existing project engine/provenance home
  experiments/                                  # added allocation state, not user workflow configuration
    allocation.json                             # added history, high-water marks and tombstones
experiments/
  stress_test_01/                                # changed default naming; custom bases supported
    experiment.yml                              # added immutable creation metadata and note
    _engine/
      reservation.json                          # added early intent and resolution binding
      simulation_intent.json                    # existing immutable simulation contract
      simulation.json                           # existing readiness record; present only when ready
    ...                                         # existing responses, metric sets and figure layout
```

The path proposal must be checked against current engine placement and schemas before implementation.
`experiment.yml` records name, family/number, creation time, optional note and toolbox identity using
existing version machinery (including a source-checkout fallback when `git describe` is unavailable).
Machine allocation/binding records use versioned closed schemas and reference existing provenance.
Do not hand-edit generated records. Keep existing config archives and simulation records authoritative
for the inputs they already own; creation metadata is not a replacement scientific fingerprint.

Repository changes are expected in the shared allocator/resolver, both public runners, their consumers
and focused tests; templates and live docs explain the new commands and numeric suffix grammar.
Keep seed config prefixes. Search all naming/DAG/log consumers and update live references together.

Preserve existing folders. Explicit existing dated or unnumbered legacy names resume using validated
legacy ownership before applying new numeric parsing. For a non-numbered name, an exact legacy folder
takes precedence over interpreting it as a new base; `--new-experiment` uses it as a base explicitly.
Report the legacy selection. A dated legacy name plus creation flag is rejected; select a new base.
Unknown/malformed folders require diagnosis. New numbered experiments begin alongside dated ones.
No folder migration, output deletion or replacement of old frozen schemas is authorized by this plan.
Users who previously used a new explicit non-numbered name now receive `<base>_01`; document this change.

## 6. Acceptance and implementation

Implement in three reviewable parts: allocation/ownership and tests; runner binding/recovery and tests;
then live docs and execution acceptance. The former two-small-commits estimate no longer fits.
Review the cross-workflow contract before implementation, including the WF3 run-id interface.

Acceptance matrix (C = complete, I = incomplete, P = reserved before resolved binding):

| Case | Required result |
|---|---|
| No experiments; plain run | Create `_01`. |
| Highest is C; same selection | Select it; no-op only with valid current outputs. |
| Highest is I; same selection | Preserve valid runs; recover/restart unfinished work safely. |
| Highest is C or I; changed selection | Refuse; name differences and recovery choices. |
| Highest is P; changed request | Refuse before generation; never silently retarget. |
| P with automatic seed; retry | Recover original seed/request and number. |
| New flag; same or changed inputs | Allocate next number; scenario reuse remains possible. |
| Older numbered pin | Select exactly it; check compatibility. |
| Never-allocated numbered pin | Create it and advance history; refuse tombstone reuse. |
| Pin plus new flag; note on continuation | Reject before mutation. |
| Different base or output root | Independent allocation; print resolved root/family. |
| Legacy dated/unnumbered selection | Explicit continuation; no automatic migration. |
| `_99`, gaps, deleted highest | `_100`; no gap filling or deleted-number reuse/fallback. |
| Numeric suffix, zero, extra leading zero | Canonical pin or explicit validation error. |
| Two creators or same-name writers | Distinct reservations or exclusive-writer refusal. |
| Crash at each publication boundary | Recover verified owned state; refuse unknown state. |
| Dry run/DAG/validation | Preview only; allocation/binding/experiment state unchanged. |
| WF4 disabled or metrics-only plus new flag | Reject; no allocation. |
| Missing derived outputs | Regenerate only from verified retained responses. |
| Corrupt/missing native responses | Refuse; restoration or new experiment required. |
| Resource/comment/metric/figure changes | Apply correct compatibility scope; no needless allocation. |

Map verification to claims under `dev/reference/validation-ladder.md`:

- Selection, parsing, deletion and concurrency: focused allocator/runner tests with synthetic roots;
  preserve records for assertions and inject failures at publication boundaries.
- Early binding and reproducibility: pending request with automatic seed, changed-request retry and
  explicitly reused collection; assert identity and input equality, not only command success.
- Interrupted simulation: rapid multi-run fixture interrupted after one completed run; verify its
  retained identity and completion evidence survive, and unfinished work follows supported recovery.
- Complete/metrics-only/corrupt cases: reuse that rapid root; inspect immutable response inventories,
  metric-set ownership and mismatch diagnostics. Tampered cases use separate fixture roots.
- Both entry points and previews: same configured root and mocked/real supported calls as appropriate;
  compare resolved names and before/after allocation, binding and experiment trees.
- Integration: shared orchestration/config contracts require the ladder's batch full and all-five
  fresh rapid execution gates at landing. Reuse those outputs for applicable inventory/numeric checks;
  no extra fresh rapid run just to repeat evidence. Name-only changes do not prove numerical stability.

Use unique roots below `.tmp/scratchpad/t2610032349/` for future execution evidence, not production
outputs. Record tested commit, exact command/result, environment, config/input identities and output
root in this task's evidence. The present planning-only edit needs board check, links and diff review;
it does not discharge future executable acceptance.

## 7. Tradeoffs and revisions

Automatic increment on completion would save a flag, but a harmless rerun could trigger another
expensive experiment. Incrementing on input change could hide accidental edits. Keep explicit creation
and loud mismatches; automatic creation would be preferable only for an explicitly different batch API.
Folder scanning alone is simpler but cannot prevent deleted-number reuse; persistent allocation history
adds small durable state and recovery duties. Rejecting at `_99` adds an arbitrary limit; minimum-width
numbering grows naturally, with numeric rather than lexicographic ordering.

Early binding broadens this task into runner coordination. It prevents scientifically different work
sharing an interrupted identity, but needs reviewed schema and ownership integration. It does not add
Wflow checkpoints, native-output repair, model revision storage or assessment-folder versioning.

2026-10-03: recorded explicit creation, latest-number continuation and preservation of dated folders.
2026-10-10: expanded the user-authorized plan with selection grammar, growth, early binding, recovery,
ownership, entry-point parity, read-only previews and acceptance cases. Exact schemas/publication
mechanics await contract review; behavior decisions above replace the prior loose ends.
