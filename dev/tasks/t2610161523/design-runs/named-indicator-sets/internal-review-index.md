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

## Independent external review of v2

Raw report: external-review-r1.md. Verdict revise; two major and four minor findings.
The fresh Claude reviewer did not receive the earlier review or ledger. Original severities retained.

| ID | Severity | Driver classification | Consequence |
|---|---|---|---|
| ext1-1 | major | Scientific/design issue | Decide coverage reporting and reconcile prior unit ruling. |
| ext1-2 | major | Design issue | Define authored-ID identity or simplify schema v1. |
| ext1-3 | minor | Implementation obligation | Check equal rows for shared definitions across sets. |
| ext1-4 | minor | Design correction | Use production water-year helper in oracle/metadata. |
| ext1-5 | minor | Metadata clarification | Explain reference-month selection by sums, not rate. |
| ext1-6 | minor | Qualified implementation obligation | Cover numerical code and distinguish references. |

Source checks and limits:
- ext1-1: forcing_window renders Jan 1 through Dec 31 midnight; reduce_run uses annual sum then mean.
  The N/(N+1) ratio is conditional algebra relative to total/N when there are N+1 nonempty bins,
  not an observed bias estimate or universal hydrological truth. Actual member windows, calendar,
  missingness and block counts still need verification. The dated 2026-08-08 unit ruling really is
  recorded in indicator_tables.py; v2 must explicitly reconcile it before G2. Coverage diagnostics
  are the reviewer's proposed remedy, not an automatically approved additional public artifact.
- ext1-2: v2 admits authored aliases for the fixed existing calculations but does not explicitly
  state whether authored IDs enter numerical identity. Resolve that ambiguity before implementation.
  Prose titles alone cannot establish scientific meaning; dictionary method semantics remain important.
- ext1-3: C3 checks identity/reuse but lacks a direct shared-row equality check. Add to existing coverage.
- ext1-4: water_year_end_anchor returns YE-DEC/YE-SEP, confirming the YS-JAN/YS-OCT mismatch in O2.
- ext1-5: registry reference selection uses calendar-month sums. Describe duration/coverage dependence
  without asserting any fixed percentage for arbitrary data or month pairs.
- ext1-6: the three-file declaration revision is real, but metric_plan also hashes a transitive static
  Python import inventory through repository_code_inventory. A newly imported resolver can already be
  covered. Stale reuse is therefore a conditional risk, not a demonstrated defect in the current code.
  Require coverage of numeric mappings and a focused identity check, not a second hashing framework.

### Conflicts and convergence

The external reviewer supports mm as the dimension of the existing mean block-depth arithmetic.
This qualifies the original domain review's preference for mm/yr: physical dimensional correctness
does not settle annual-rate interpretation with partial blocks. Both reviews agree that users need
explicit period/missingness semantics. The external analysis supplies a conditional block-count
argument, not empirical validation of the actual run windows. Keep the unit/coverage decision open
for the owner; do not silently overturn the earlier dated ruling or adopt a new numerical policy.

The external review supports the operation boundary, registry/YAML separation, publication ownership,
collision rules and pre-change parity approach. It did not inspect exporter/runner/tests or inventory
closure; the coordinator's ext1-6 source check narrows that concern. No v3 was commissioned here.

## Focused independent follow-up on unchanged v2

Raw report: external-review-r2.md. Verdict revise, confined to annual coverage and authored IDs.
The fresh Opus reviewer confirms ext1-1/2 as major, confirms ext1-3/4, and qualifies ext1-5/6.
No additional finding IDs were raised. It proposes wording; no candidate was revised or approved.

- **Coverage proposal:** Keep mm and the existing arithmetic; add block_coverage to indicators.csv,
  sourced from immutable evidence. Report block counts/completeness and missingness rather than claim
  measured bias. D/B versus D/L is conditional estimand algebra; the year-duration convention for L
  must be explicit. The reviewer prefers this over a new per-run CSV unless differing windows justify it.
- **Authored-entry proposal:** Its preferred 2A defers authored entries, keeping definition references.
  Alternative 2B retains them, includes authored IDs in numerical identity, keeps presentation edits
  publication-only, exposes equivalent definitions and rejects duplicate calculations within a set.
  These are alternatives for owner selection, not accepted scope changes.
- **Minor changes:** Use the production anchor helper; compare shared rows across sets; explain month
  selection by sums; test numeric mapping identity through the existing import closure/value contract.

### Coordinator qualifications before adopting proposed wording

The seed actually includes authored per-indicator metadata, method parameters and calculation bindings.
The claim that reference-only sets fully satisfy that template is therefore a framing interpretation,
not established equivalence. Prefer preserving the intended capability unless the owner narrows v1.

Coverage also needs the existing location dimension: ResponseSeries.key is (run, variable, location),
with a missing mask per series. The proposed per-(variable, run) evidence cannot silently collapse
location-specific missingness. A future revision must preserve location distinctions or explicitly
define a truthful summary with traceable evidence. Pattern ordering must use a total stable key;
sorting only by first label and run count can leave ties. These are checks on the proposed remedy,
not new raw reviewer findings. No percentages or hand examples were empirically executed.

The reviewer considers another call unnecessary after a faithful revision with the stated checks,
subject to its listed exceptions. That opinion is scoped to these decisions and does not constitute
approval of an unwritten v3, waiver of unresolved scientific issues or completion of the whole loop.
