# Finding ledger

Initial rows are pending, not closure dispositions. G1 framing and subsequent author revision will
append resolutions without changing raw findings or these initial entries. No finding is waived.

| ID | Review | Severity | Disposition | Resolution or rationale | Doc version |
|---|---|---|---|---|---|
| domain-1 | domain | major | pending | G1: explicit parity coverage map and pre-change evidence. | v1 |
| domain-2 | domain | major | pending | G1: explicit semantics; resolve unit interpretation before G2. | v1 |
| domain-3 | domain | major | pending | G1: proposed derived readable indicator dictionary. | v1 |
| domain-4 | domain | minor | pending | Proposed declaration-authority/key-coverage obligation. | v1 |
| domain-5 | domain | minor | pending | Proposed neutral example name; no second method commissioned. | v1 |
| domain-6 | domain | minor | pending | Proposed legacy-folder collision/refusal acceptance case. | v1 |

## V2 dispositions, 2026-10-16

Owner approved G1 and directed this revision. Accepted means incorporated into the proposed design;
it does not claim implementation verification or an independent approval of v2.

| ID | Review | Severity | Disposition | Resolution or rationale | Doc version |
|---|---|---|---|---|---|
| domain-1 | domain | major | accepted | Pre-change oracle O1-O6 and C4. | v2 |
| domain-2 | domain | major | accepted | P2/P3 policies; unit assessment still open before G2. | v2 |
| domain-3 | domain | major | accepted | P4 dictionary, inventory and recovery; C6. | v2 |
| domain-4 | domain | minor | accepted | P2 registry authority and helper correction; C6. | v2 |
| domain-5 | domain | minor | accepted | Neutral examples and explicit p95 non-exceedance meaning. | v2 |
| domain-6 | domain | minor | accepted | P4 ownership-aware collision refusal and refresh; C6. | v2 |

- **domain-1:** Capture references before implementation edits. Reuse retained rapid responses and
  existing tests, adding only missing cases; cover all variables, groups, anchors, missingness,
  reference ties, BFI zero, GEV refusals and legacy selection branches. Independent known answers
  supplement parity. No new baseline suite or simulations are required solely for this design.
- **domain-2:** Declare interval-end label binning, retained partial blocks, weighting and method-specific
  missingness. Propose mm with an explicit accumulated-depth-per-block description, distinguishing it
  from a duration-normalized rate. Independent scientific assessment remains required before G2.
  The review's unmeasured bias magnitude/direction claims are not adopted. This finding is not yet
  scientifically closed; positive policy fixtures and the unit decision remain outstanding.
- **domain-3:** Generated indicators.csv exposes resolved metadata and policies without machine hashes
  or JSON; include it in publication inventories, recovery and metadata-only refresh. YAML and registry
  remain the respective authoring and calculation authorities.
- **domain-4:** Registry declarations own grain/group policy. Correct or retire stale shared helpers
  during implementation and exercise wet/dry run/group keys; no code was changed in this revision.
- **domain-5:** example_subset avoids implying a commissioned low-flow method; q p95 remains a high-flow
  non-exceedance statistic. No second scientific set is accepted by this document.
- **domain-6:** Preserve occupied legacy /3 and unowned folders; refuse collisions while allowing a
  verified same-set refresh. C6 requires both refusal-with-byte-preservation and valid refresh cases.

Coordinator checked the whole v1-to-v2 diff against all six IDs. Remaining Opus reviews must examine
v2; neither this check nor the owner revision request supplies a whole-document reviewer verdict.

## External round 1 findings on v2

Raw report retained verbatim. These are pending decisions, not accepted changes to the design.

| ID | Review | Severity | Disposition | Resolution or rationale | Doc version |
|---|---|---|---|---|---|
| ext1-1 | external r1 | major | pending | Unit ruling and readable coverage need owner resolution. | v2 |
| ext1-2 | external r1 | major | pending | Resolve authored aliases and metric-ID identity. | v2 |
| ext1-3 | external r1 | minor | pending | Shared-row equality acceptance recommendation. | v2 |
| ext1-4 | external r1 | minor | pending | Use production anchor helper instead of YS examples. | v2 |
| ext1-5 | external r1 | minor | pending | Explain month selection by sums and duration coverage. | v2 |
| ext1-6 | external r1 | minor | pending | Verify import inventory and clarify reference vocabulary. | v2 |

Domain-2 remains open for the unit/coverage ruling. External support for the dimension mm does not
approve annual-rate interpretation, actual coverage, or a change to the recorded 2026-08-08 ruling.

## Focused follow-up dispositions

External-review-r2.md reuses ext1-1 through ext1-6; it raises no new finding IDs.
Ext1-1/2 remain pending design decisions; ext1-3/4 remain confirmed implementation/wording items;
ext1-5/6 remain qualified as recorded in the index. No original severity is downgraded or finding closed.
Concrete coverage and authored-ID alternatives are now available for a bounded revision.
Reviewer-proposed wording is not design authority until adopted in a new version and checked.

## Owner-directed final resolution in v3

Owner requested application of the final points and sealing. The selected authored-entry option is
2B, preserving the intended template; reference-only 2A is retained as an alternative, not adopted.
These dispositions resolve design requirements. Runtime validation remains required during delivery.

| ID | Review | Severity | Disposition | Resolution / acceptance location | Doc version |
|---|---|---|---|---|---|
| domain-1 | domain | major | accepted | Pre-change O1-O6 oracle and C4 retained. | v3 |
| domain-2 | domain | major | accepted | P2 block-depth units, ruling reconciliation and coverage. | v3 |
| domain-3 | domain | major | accepted | P4 readable dictionary, inventory and recovery. | v3 |
| domain-4 | domain | minor | accepted | Registry grain authority and key coverage. | v3 |
| domain-5 | domain | minor | accepted | Neutral subset; non-exceedance p95 semantics. | v3 |
| domain-6 | domain | minor | accepted | Ownership-aware collision refusal and valid refresh. | v3 |
| ext1-1 | external r1/r2 | major | accepted | P2/P4 immutable coverage, units; independent example. | v3 |
| ext1-2 | external r1/r2 | major | accepted | P2/P4 authored-ID identity and alias option 2B. | v3 |
| ext1-3 | external r1/r2 | minor | accepted | C3 shared-definition rows and alias values agree. | v3 |
| ext1-4 | external r1/r2 | minor | accepted | Resolved anchor truthfulness and pre-change parity. | v3 |
| ext1-5 | external r1/r2 | minor | accepted | Month sums depend on length/coverage; no fixed bias. | v3 |
| ext1-6 | external r1/r2 | minor | accepted | Numeric code inventory; distinct reference meanings. | v3 |

No additional ext2 IDs exist. All original IDs retain their raw severities in immutable reports.
Unit closure concerns the stated block-depth estimand; it does not validate actual runs or establish
equivalence to normalized annual rates. The original sum, names and no-mm/day-rescaling decision
remain; the earlier mm/yr interpretation is explicitly restricted. Location-specific missingness
must remain visible. Source qualification of current YS callers versus the YE helper is in the index.
There is no whole-document independent verdict on v3: finalization uses the two reviews' concrete
resolutions, owner authorization, author reconciliation and the coordinator's full-diff check.
