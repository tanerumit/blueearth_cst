---
verdict: revise
doc_version: design-v1.md
findings:
  - id: domain-1
    severity: major
    section: "10.9 Evidence, assumptions and acceptance; 11 Complete-run evidence"
    finding: >-
      The exact native-discharge and metric comparison promised for P7 has no
      identified predecessor comparator. The P0 capture is explicitly WF3 only
      (automatic seed and explicit seed 123); it cannot establish pre-change
      Wflow responses or metric values. Section 10.9 nonetheless expects exact
      native-discharge/metric fingerprints without naming the evidence source,
      matched model, response selectors, preparation inputs or comparison owner.
    rationale: >-
      A successful successor run and identical WF3 arrays cannot detect a change
      in WF4 elevation interpretation, temporal conversion, response selection
      or metric grouping. Comparing the successor with itself would pass those
      regressions. The accumulated local trees are expressly disallowed as an
      unqualified clean reference, and the baseline uses a different configuration.
    suggested_fix: >-
      Identify a separately pinned predecessor WF4 comparison before the relevant
      implementation changes, or specify a matched-forcing predecessor execution
      from immutable predecessor code/environment/model/preparation inputs that
      will provide the comparator. Name capture timing, owner, run/selector/group
      mapping and artifact coverage. Alternatively narrow P7's claim explicitly
      and take the uncovered WF4 numerical-continuity risk to the owner. Do not
      imply that the WF3 capture or rapid successor tree supplies this evidence.
  - id: domain-2
    severity: major
    section: "7 Shared elevation; 10.5 Static plan; 10.6 WF3-only seed material; 10.8 Elevation; 10.9 mutation cases"
    finding: >-
      The boundary does not explicitly classify elevation used by CHIRPS source
      preparation. Existing extraction consumes both hydrography elevation and
      ERA5 orography to lapse-correct temp/temp_min/temp_max before writing the
      historical climate consumed by WF3. These are scientific WF3 source
      dependencies even though the resulting sidecar also serves WF4. Section 7
      calls for removal of indirect elevation inputs, and section 10.8 says a
      missing elevation does not invalidate WF3, without stating this cold-source
      exception. The proposed elevation mutation cases therefore have an
      ambiguous scientific expectation for a supported source branch.
    rationale: >-
      Removing this preparation dependency changes generated climate values;
      insisting on seed invariance after changing it would conceal a real source
      change. Retaining its actual contribution through the historical-climate
      byte digest is consistent with strict independence from WF4-only work.
      The rapid ERA5 fixture does not exercise the CHIRPS lapse correction.
    suggested_fix: >-
      State that WF3 excludes WF4-only preparation but retains every dependency
      required to prepare its historical climate. Name the CHIRPS elevation
      correction as source preparation and distinguish consuming an already
      frozen climate store from producing a cold store. Split the falsifier:
      mutate only WF4 elevation while holding WF3 source bytes fixed and require
      seed/collection invariance; mutate a CHIRPS source-preparation elevation
      dependency and require changed source evidence or refusal, with no
      invariance claim. Preserve the existing correction and make only the
      unneeded sidecar publication optional where feasible.
  - id: domain-3
    severity: major
    section: "10.7 Collection, simulation and metric identity sketches"
    finding: >-
      The forcing-preparation identity projection retains generated_forcing_reader
      with locators replaced, but that existing payload contains
      metadata.cst_unit_interpretation.evidence. Its evidence string embeds raw
      catalog hashes, catalog locators and an extraction-code hash. Replacing
      locators does not remove the raw catalog hashes. A catalog comment edit can
      therefore change the simulation identity despite unchanged elevation,
      generated climate and resolved preparation semantics, contradicting the
      stated comment-invariance rule. Section 10.6 excludes this evidence from
      WF3 identity, but section 10.7 has no equivalent WF4 projection rule.
    rationale: >-
      This mixes provenance with physical interpretation precisely at the new
      simulation boundary. It produces different simulation and downstream metric
      identities for the same resolved experiment, and the stated replacement of
      URI fields cannot prevent it. The existing payload is a concrete input to
      the new contract, not a hypothetical future field.
    suggested_fix: >-
      Define the closed scientific projection of generated_forcing_reader,
      preserving all consumed reader/conversion semantics and the resolved unit
      interpretation revision/variables while retaining evidence-only metadata in
      the full document. Explicitly classify cst_unit_interpretation.evidence and
      other retained descriptive metadata. Add a P6 mutation case using this real
      nested payload: catalog comment/location changes alter evidence hashes but
      preserve simulation identity; a consumed reader or unit setting change
      changes identity or is refused.
  - id: domain-4
    severity: minor
    section: "Intake evidence register E2-E6; 10.9 Evidence, assumptions and acceptance"
    finding: >-
      E2-E6 record future acceptance properties and planned tests rather than
      observations. The design correctly disclaims implementation and completed
      reference evidence, so those rows must remain explicit hypotheses rather
      than being marked empirically supported by review agreement. Their current
      evidence register has no result or evidence-status field.
    rationale: >-
      Domain review can judge a falsifier's adequacy but cannot supply its missing
      result. Without a distinction between design acceptance and executed
      evidence, a later gate can silently turn the review into runtime assurance.
    suggested_fix: >-
      Annotate the register with observed versus hypothesis status, evidence
      artifact/result and closure phase. Keep the actual clean predecessor
      capture as a G2 prerequisite. Carry post-implementation properties to their
      P1/P4/P5/P6/P7 gates as unexecuted falsifiers; record any separately required
      pre-implementation feasibility probes by command and observed result.
---

## Premise disposition

| ID | Disposition | Evidence and settling observation |
|---|---|---|
| E1 | supported | `generation_plan.py` explicitly calls `resolve_preparation_payloads`, adds ancillary files to `sources`, includes them in `source_projection` under `forcing_elevation`, and inventories `prepare_climate_data_catalog.py`. That projection and code digest enter `generation-seed-material/1`. Read-only source inspection establishes the stated contamination. |
| E2 | contested — domain-2 | Plausible for genuinely WF4-only changes with fixed WF3 source bytes/code/environment; the shared elevation role is not fully classified. Settle the boundary with the two source-aware mutations in domain-2, plus the prescribed concrete uncontaminated code-closure manifest. Runtime v2 invariance remains unexecuted. |
| E3 | untestable as stated — domain-1, domain-4 | No completed pre-change reference or successor comparison was supplied to this review. Settle WF3 continuity with the actual clean explicit-seed reference, frozen environment and exact comparison of all retained arrays/coordinates/masks/units/calendars, date selections and lineage. Settle the additional P7 response/metric claim with the comparator required by domain-1. The automatic-seed fixture is separate and is not a parity test. |
| E4 | untestable as stated — domain-4 | Proposed archive writers do not yet exist. Settle with captured-buffer versus archived-byte evidence, duplicate-basename and unavailable-original cases, and race/crash injection proving supported readers never accept mixed generations. A prose transaction protocol is not an observed result. |
| E5 | untestable as stated — domain-4 | The pinned-plan workflow is prospective. Settle with cold/prepared/reuse and forced-target DAG evidence, pointer replacement during execution, unchanged-mtime source mutation, and competing initialization/refusal observations. Verify both checkpoints are absent from generation expansion. |
| E6 | untestable as stated — domain-4 | No relocated successor project or real HydroMT read was supplied. Settle with whole-project relocation, originals unavailable, successful checked resolution through the supported HydroMT reader, and refusal after one referenced-byte mutation. Identity invariance must also exercise the evidence-only nested payload in domain-3. |
| E7 | supported within the stated compatibility policy | Fresh output roots, version refusal, preserved predecessor artifacts and an explicit separately authorized baseline transition form a coherent selected policy. This supports dispensing with old-output readers for new projects; it does not establish that the non-exhaustive reader inventory is complete. P2/P5/P6 consumer sweeps and the eventual baseline transition remain implementation evidence. |

## Scientific assessment

The selected framing is appropriate for a schema migration: preserve the
generator's computations, distinguish new automatic-seed material from a change
in the stochastic algorithm, and preserve WF2 as a plausibility overlay. The
canonical SHA-256-to-integer formula is stated precisely, including zero and
possible modulo collisions. Testing changed material digests rather than
requiring every mutation to change the integer seed is correct.

The collection projection usefully separates full evidence from effective
settings and interpreted source semantics. It correctly allows explicit and
automatic requests with the same resolved inputs to select one collection.
The source byte hashes intentionally identify encoded inputs, not every
scientifically equivalent encoding; relocation tests should preserve the
captured bytes rather than silently assume that re-extraction yields identical
NetCDF containers. Complete static import closure and rejection of unclassified
consumed fields are strong proposed safeguards, still requiring the P4 manifest
and mutation evidence.

Lineage has a suitable falsifier: exactly one empty-`st_id` root per realization,
the complete realization/design-point product, stable row/allocation order, and
comparison of reconstructed parent IDs with the predecessor. A zero-change
design point correctly remains a distinct perturbed member. A cross-product
validator alone cannot prove that the new R member naming writes each correct
array to its declared run ID; the explicit-seed per-member comparison must
retain that association.

Absolute tolerance 0 and relative tolerance 0 are defensible for unchanged
deterministic execution under the same explicit seed, machine and environment.
The prescribed mask/coordinate/calendar/date checks avoid an aggregate score
hiding a shifted or misassigned series. Report the number of members and values
compared, any mismatch locations, maximum absolute differences and discrete
failures. An intentional comparator perturbation should demonstrate that the
comparison rejects a changed value or swapped member. Any nonzero tolerance
requires the stated scientific review before acceptance; no tolerance increase
is justified by a failed check alone.

The rapid configuration has 2 realizations over 2046-2054. This is a migration
reference, not evidence that the weather generator or Wflow is fit for a basin
decision, and it supplies no defensible tail-risk uncertainty interval. The
relevant uncertainty here is incomplete execution/comparator evidence and
coverage of supported source branches. Parameter, observational, structural,
scenario and internal-variability uncertainty are neither quantified nor reduced
by this migration review. No new hydrologic skill verdict is claimed.

## Evidence and verification limits

Read `AGENTS.md`, intake, design v1, status, the master brief's P0 requirements,
and relevant predecessor source. Applied `claim-evaluation`, its appraisal
references, `testing-policy` and its scientific-check guidance, and the
design-review-loop review/evidence/severity contracts. Source evidence includes
`generation_plan.py:122`, `generation_plan.py:181`,
`extract_historical_climate.py:684`, `prepare_climate_data_catalog.py:82`,
`prepare_climate_data_catalog.py:249`, `content_identity.py:141`, and the R
generation/perturbation/member-grid readers. The coordinator confirmed that the
concurrent P0 capture owns WF3 only; no native-response capture is claimed.

Verification is structural and traceability review of a prospective numerical
contract. No model run, numerical comparison, unit test, archive crash test,
filesystem feasibility probe or HydroMT relocation probe was executed here.
Shell startup failed; read-only file inspection succeeded through the Node
filesystem tool. This review modifies only its assigned review artifact and
does not change runtime code or the design.

The design can support a defensible migration comparison after the three major
findings are resolved and the specified evidence gates execute. Its limits are
the matched fixture, frozen environment and explicitly covered source branches;
the incomplete predecessor capture and missing WF4 comparator currently prevent
any scientific-continuity verdict, and no broader model-adequacy or uncertainty
claim follows from design approval.
