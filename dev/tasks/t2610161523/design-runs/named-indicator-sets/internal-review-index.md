# Initial domain findings and driver triage

Date: 2026-10-16. Candidate: design-v1.md; raw review: internal-review-domain.md.
Raw verdict: revise. Three major, three minor findings. No risk or external review completed yet.
Original severity and wording remain authoritative in the immutable raw report.

## Triage

| ID | Raw severity | Driver classification | Consequence / next decision |
|---|---|---|---|
| domain-1 | major | Design issue | Name the default-parity evidence coverage before implementation. |
| domain-2 | major | Design issue; interpretation partly unresolved | Define truthful method metadata and units. |
| domain-3 | major | Design issue | Decide whether readable exports include a derived indicator dictionary. |
| domain-4 | minor | Implementation obligation | Use registry grain authority; remove or correct stale helpers. |
| domain-5 | minor | Preference with semantic benefit | Use example_subset until an actual second set is specified. |
| domain-6 | minor | Implementation obligation | Test refusal of legacy immutable-folder/name collisions. |

### Verified premises and proportional response

- domain-1: rapid config requests q/aet/gwr, not every supported variable. A rapid execution alone
  cannot establish the full C4 parity claim. Require a coverage map linking existing fixtures,
  targeted synthetic examples, and retained outputs to the promised policies. Capture reference
  evidence before implementation alters behavior. The reviewer's detailed proposed fixture list is
  a proposal, not a mandate to duplicate existing tests or add a new baseline/full-suite gate.
- domain-2: reduce_run resamples labels and applies the named statistic followed by a mean.
  The response reader labels records interval_end. Code comments call annual totals mm/yr while
  the candidate describes accumulated depth in mm. That wording discrepancy is real; neither a
  comment nor the review alone settles the physical reporting convention. Preserve arithmetic,
  expose period/partial-block/missingness/label policies, and resolve units explicitly before G2.
- domain-3: P4 limits readable folders to numerical CSVs and membership tables, while metadata
  remains internal. A derived, hash-free indicator dictionary is consistent with the user's YAML
  authoring and _engine machine-record separation. It would not become a second editable authority.
- domain-4: METRIC_CLASSES maps class C to pooled, while current declarations assign non-B metrics
  run grain. Specify authoritative declarations and test result keys rather than use stale helpers.
- domain-5: the candidate already disclaims a commissioned low-flow set. A neutral example name
  reduces ambiguity; no new low-flow formula is authorized by this review.
- domain-6: current /3 reader accepts results/metric_sets/<short-digest>. The new readable namespace
  must refuse an occupied legacy result directory. Prefer ownership/collision checks over refusing
  every existing directory, since legitimate named exports must remain refreshable.

## Conflicts and unresolved interpretation

No inter-reviewer conflicts exist yet: only the domain lens has returned.
The driver does not adopt the review's approximate 10% bias claim or unconditional direction of
extreme-value effects as measured evidence; no relevant computation was performed. The reviewer
itself reports static inspection and library knowledge. Retain the finding on explicit semantics,
but require any quantified effect to be demonstrated or omitted from the governing design.

The unit of a mean of annual accumulated depths versus a normalized annual rate needs precise
definition. The reviewer prefers mm yr-1 or a per-water-year label; candidate v1 proposes mm with
period metadata. This scientific interpretation remains open and is presented at G1, not silently
resolved by triage. The Opus external review should examine it before final design approval.

## Proposed G1 framing

Keep the agreed operations and named-set interface, shared simulations, YAML configuration, existing
calculations, and internal immutable records. Add three requirements to the framing:

1. A specific, proportionate pre-change parity evidence map; no reliance on rapid coverage alone.
2. Explicit label, period, partial-block and missingness semantics; no numerical policy changes.
   Unit wording remains an explicit scientific issue for review and resolution before G2.
3. A generated user-readable indicators.csv dictionary per named result folder, with no hashes or
   machine JSON. Authored YAML stays the source; the dictionary reflects the resolved publication.

For new configuration, recommend refusing ambiguous null output-variable selections instead of
copying the current inconsistent branches; preserve explicitly supported legacy behavior separately.
Use example_subset as the placeholder. Carry the two implementation obligations into acceptance.
These are proposals pending owner G1; they are not revisions to the frozen candidate.

## Owner direction, 2026-10-16

The owner approved the presented G1 framing and requested application of the Opus findings as v2.
The earlier triage above describes v1 and is retained. The ledger records v2 dispositions separately;
the original review and its severities remain unchanged. V2 requires independent review, including
the proposed depth-versus-rate reporting convention, before G2. No parity claim is yet demonstrated.
