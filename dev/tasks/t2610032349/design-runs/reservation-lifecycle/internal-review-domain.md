---
verdict: revise
doc_version: design-v1.md
findings:
  - id: domain-1
    severity: major
    section: "4.3 Reservation and early request; 5.1 Admission before producers"
    finding: >-
      Catalog semantics are guarded only inside GenerationRequest.source_request. When WF3 is disabled,
      a pending explicit-collection reservation has no semantic catalog field, although WF4 still uses
      those catalogs for elevation, forcing readers and unit interpretation. ModelRequest also omits
      catalog semantics despite WF1 consuming them.
    rationale: >-
      After reservation but before first simulation freeze, editing a catalog's selected elevation or
      reader entry can leave the specified request unchanged. Retry can therefore bind different
      preparation inputs under the same pending identity. When WF1 is enabled, catalog edits can also
      escape the promised refusal before model production. Exact final intent validation protects an
      already-frozen experiment; it does not compare an unfrozen experiment against absent early fields.
      This is a gap in the new early-refusal guarantee, not evidence that existing frozen runs drift.
    suggested_fix: >-
      Give every executing input consumer a catalog-semantic binding independent of WF3 enablement.
      Reuse the stated conservative ordered catalog projection or specify consumer-specific projections.
      Capture those dependencies and include a pending explicit-manifest/WF3-disabled retry that changes
      a selected elevation or reader entry, plus a WF1-enabled catalog-change case. Both must refuse
      before the affected producer; comment-only changes must remain compatible.
  - id: domain-2
    severity: minor
    section: "2.2 Compatibility and recovery; 8.1 E9/E10; 8.2 Partial native reuse"
    finding: >-
      E10's all-crash-boundaries premise is broader than the retained-member mechanism and the proposed
      interruption test. A matching .ok file proves matching input fingerprints, not CSV integrity;
      restoration also moves CSVs individually and removes their staging markers.
    rationale: >-
      The draft correctly acknowledges these existing limitations. Keep that qualification attached to
      the user-facing preservation claim: a probe interrupted after one staged completion cannot
      establish preservation through restoration or detect a modified but readable staged CSV.
    suggested_fix: >-
      Define the supported interruption boundary and the evidence that makes a completed member valid.
      Record pre-interruption response bytes and confirm both preservation and absence of re-execution.
      Disposition restoration interruptions and staged tampering explicitly as tested support or a
      diagnosed existing limitation. Do not silently expand this task into native-output repair.
  - id: domain-3
    severity: minor
    section: "8.1 E13; 8.2 Scientific invariance"
    finding: >-
      Numerical invariance remains untestable from the supplied evidence. The matched-reference capture
      is conditional, while the task brief requires a results delta; the precise comparison population
      and acceptance rule should be settled before runtime implementation.
    rationale: >-
      Equal reservation, seed or simulation digests establish attribution only to their covered inputs.
      They do not establish equality of realized forcing or native response values. Reuse of retained
      responses and cross-revision numerical equivalence are different claims requiring different checks.
    suggested_fix: >-
      State whether cross-revision no-drift is an acceptance claim. If it is, retain a pre-change
      reference with matched prepared inputs, effective seed, ordered run IDs, model and environment.
      Compare realized forcing and native timestamps, variables, missingness and values on the declared
      representative runs; report all exclusions. Separately check interrupted versus uninterrupted
      execution. Require exact same-environment value agreement or investigation, not an opportunistic
      tolerance or a refreshed baseline. If no reference is captured, narrow the reported claim.
  - id: domain-4
    severity: minor
    section: "5.4 Recovery; 8.1 E12/E14; 8.2 Ownership and publication checks"
    finding: >-
      Parent-death exclusion and filesystem crash-state coverage are empirical acceptance obligations,
      not consequences established by the existence of archive_lock. The current writer-lifetime helper
      supports Windows jobs and explicitly refuses writing children on other platforms.
    rationale: >-
      Source inspection supports the intended Windows mechanism, but cannot establish that all writing
      descendants stop before recovery acquires ownership. Linux filesystem fault tests must not be
      presented as evidence of supported Linux workflow recovery. This is a pre-existing platform limit.
    suggested_fix: >-
      Retain E12/E14 as open implementation gates. Observe a writing descendant during forced parent
      death and verify it cannot write after recovery ownership. Exercise each publication boundary and
      repeated recovery on supported local filesystems. Record Windows writer evidence separately from
      Linux record-protocol fixtures and preserve the existing unsupported-writer refusal.
---

# Scientific and reproducibility review

Reviewed 2026-10-10. Requested configuration: `gpt-6-astra/high`; effective model and reasoning settings
are not independently observable. The runtime identifies the GPT-6 family only. No nested delegation,
scientific execution, source modification or commits were performed. Only this review artifact was written.
The findings above are the immutable review of `design-v1.md`.

The design supports the intended framing: experiment numbering is allocation history, while WF3 and WF4
retain scientific identity authority. It preserves scenario-neutral generation, exact producer-owned run
IDs, original frozen selection spelling, and independent immutable metric sets. No physical or statistical
method change is proposed. The major issue is completeness of early input attribution, not the hydrological
method. The catalog gap must be resolved before claiming complete early refusal.

D1 is supported. `generation_plan.py:335` snapshots historical climate and basin cells; lines 423–437
derive the automatic seed from their scientific identities and effective generator/code projections.
`generate_scenarios.py:79` prepares sources before planning and stochastic launch. Pending source status
followed by immutable seed/plan binding before stochastic work preserves this dependency. Requiring a
numeric seed before those inputs exist would require earlier preparation or a different algorithm.
An explicit experiment number must never enter that seed material.

Source verification used HEAD `3bea47b933035a25841b8f97c2022799ae111af1`. The documented P1 scaffold
change explains its difference from the design's `6998d0fd` inspection point. Intake, status, design and
inventory were read from absolute session paths; original plan/briefs were read from the primary checkout.
The intake's old scaffold observation was also checked with `git show 6998d0fd:scripts/create_case.py`.

For domain-1, the live chain is `rules/simulate_and_metrics.smk:75` →
`wf4_ancillary_descriptor.py:332` → `climate_analysis/prepare_climate_data_catalog.py:191`.
It resolves selected catalog entries, native elevation adapters and unit interpretation even with an
explicit ready collection. WF1 consumes `DATA_SOURCES` at `build_model.smk:90`, 637 and 685.
For domain-2, `batch_staging.py:62–110` establishes the input-only marker and individual restoration.
These are direct source observations; no failure injection is represented as executed.

## Premise dispositions

Each disposition concerns the precise premise, not acceptance of the proposed implementation.
“Untestable as stated” below means the requested runtime conclusion cannot be settled by this source-only
review; its observation and finding remain explicit implementation obligations.

- **E1 — supported.** `allocate.py:68–125` uses occupancy and dated selection, without allocation history.
  Falsifier: allocator behavior retaining a deleted highest allocation.
- **E2 — supported.** `run_workflows.py:925` encloses `_run_owned`; lines 1204–1228 launch its children.
  Falsifier: a sanctioned writing child launched outside that ownership interval.
- **E3 — supported.** `workflow_config_snapshot.py:597` uses `msvcrt.locking`/`fcntl.flock`.
  Falsifier: concurrent owners acquire the same local lock. Child lifetime is separately E12.
- **E4 — supported.** `generation_plan.py:335–450` resolves auto seeds from prepared source identities.
  Falsifier: fresh-root numeric binding before preparation using the unchanged algorithm.
- **E5 — supported.** `generate_scenarios.py:79–132` prepares sources before planning/initialization.
  Falsifier: a generation child starts before the proposed binding callback.
- **E6 — supported.** `scenario_rows.py:72–91,149–172` requires capacity-padded, ordered producer IDs.
  Falsifier: producer-derived rows accepted with altered spelling or omitted unperturbed members.
- **E7 — supported.** `collection_resolution.py:32–40` accepts exactly `manifest_path`.
  Falsifier: an additional run-subset selector key accepted by the live reader.
- **E8 — supported.** `simulation_record.py:446–534` writes intent before archive publication and reads
  the paired archive on retry. Falsifier: source/runtime evidence of atomic paired publication.
- **E9 — supported, narrowly.** `batch_staging.py:62–90` compares TOML/simulation hashes for staged reuse.
  It does not assert CSV integrity. Falsifier: a mismatched marker reused; domain-2 covers stronger claims.
- **E10 — contested; domain-2.** `restore_staged:96–110` consumes staging one member at a time.
  Settle bounded preservation with restoration-boundary interrupts and retained-byte/execution evidence.
- **E11 — contested; domain-1.** Execution-only exclusions are plausible, but the scientific projection
  is incomplete with WF3 disabled. Settle with selected-catalog mutation and harmless-edit cases.
- **E12 — untestable as stated; domain-4.** `windows_job.py:55–118` supplies the intended Windows mechanism;
  lines 121–135 refuse other writing platforms. Settle with parent-kill/descendant-write observation.
- **E13 — untestable as stated; domain-3.** No paired numerical evidence exists in this review packet.
  Settle with the matched realized-input/native-value comparison, not identity hashes alone.
- **E14 — untestable as stated; domain-4.** The publication protocol is proposed and not executed.
  Settle with platform-specific crash-boundary and repeat-recovery observations.
- **Intake: simulation intent guards reuse — supported.** `simulation_record.py:464–472` compares canonical
  intent and archive ownership. Falsifier: changed canonical intent accepted under the old experiment.
- **Intake: project ownership — supported.** Same source and falsifier as E2/E3; not independent evidence.
- **Intake: closed seed projection — supported.** `generation_plan.py:45–140` classifies generator fields
  and rejects unknowns. Falsifier: an unclassified effective scientific field silently accepted.
- **Intake: scaffold output separate — supported historically.** `git show 6998d0fd:scripts/create_case.py`
  confirms `runs/slug/active`; current P1 intentionally removes that suffix. Falsifier: runtime experiment
  selection depending on the scaffold suffix. No reservation regression inferred from the P1 difference.
- **Intake: partial-run safe reuse — untestable as stated; domain-2.** No interruption probe is supplied;
  settle with the bounded completion/restoration observations, including whether members reran.

## Framing decisions for G1

Accept D1's pending-source timing as the scientifically faithful alternative. Preserve exact collection
and run selection, and keep complete simulation readiness separate from reservation state. Require an
early guard for every active scientific input consumer (domain-1). Decide the bounded interruption claim
and cross-revision no-drift claim explicitly (domain-2/domain-3); the latter needs a reference captured
before runtime edits. Existing native repair and platform limitations need not expand this task's scope.

Model-validator remains the authority for representative numerical equivalence. Contract tests establish
publication, attribution and refusal behavior; neither they nor this review scientifically qualify a basin
assessment. Case-specific metrics, thresholds and run decisions remain outside this change.
