# Internal review index — design v3

Driver index, 2026-09-09. This supplements the historical v1 index; it does not
replace earlier reviews or ledger entries. The authoritative finding text is
`internal-review-domain-v3.md`, produced by Astra under the model-validator
persona against `design-v3.md` at `7e4f5031`. Verdict: **revise**, 0 blocking,
5 major, 2 minor. Every original finding ID and severity is retained below.

| ID | Severity | Concern | Driver premise check / proposed routing |
|---|---|---|---|
| domain-v3-1 | major | Same-realization forcing ancestry | Current rule 3.12 uses the same `rlz_num` in its unperturbed input and perturbed output. V3 §5.1 names a forest and supporting edges but omits that exact stochastic constraint. Bounded correction under R-3. |
| domain-v3-2 | major | Class-C reference location | `_category_month` selects `chosen.iloc[0]`; v3 §6.6 has no explicit reference-location identity. Preserve Q5/R-1/R-2 through explicit provenance, not a new per-location method. |
| domain-v3-3 | major | Return-level sample policy and fit validity | V3 §7.5 labels ratio 1.0 and floor 10 proposed/untested; GF-15 checks count refusal. A valid scientific acceptance criterion is absent. Location-specific counts and fit refusals are bounded corrections; threshold interpretation needs an owner ruling. No current fit failure was measured. |
| domain-v3-4 | major | Metric execution environment | V3 §8.4 hashes simulation identity, response inventory and metric definition, but no current stage-3 environment descriptor. Bounded freshness/provenance correction. |
| domain-v3-5 | major | Capacity enters automatic seed material | V3 §9.3 places `unit_id_capacity` in generation config; §9.4 excludes seed and execution-only fields without excluding capacity. Bounded correction separating namespace headroom from climate draws. |
| domain-v3-6 | minor | Existing calendar/endpoint handling | Reviewer cites the current noleap-to-datetime conversion and standard-calendar TOML setting. Make preservation acceptance explicit; no observed temporal failure or silent method repair is authorized. |
| domain-v3-7 | minor | Frozen evidence qualifications | Preserve the review's separate E6/E13/E17/E19 qualifications and settling observations. The frozen intake stays intact; no second scenario provider or new scientific run follows from these historical limitations. |

## Conflicts and scope

Only the refreshed domain lens has reviewed v3; no fresh cross-lens agreement
is claimed. Historical architecture/risk reviews concern their named versions.
The domain reviewer found no need to reverse the two-workflow/three-stage framing.

The historical `domain-7` fit-interval deferral remains a major finding requiring
the recorded G2 ratification. New `domain-v3-3` separates screening counts and
fit validity from precision/uncertainty; neither resolving it nor receiving this
review ratifies the interval deferral. Keep both findings at their filed severity.

## Proposed G1 correction package — pending owner ruling

Retain the approved scope and names. Have a fresh author produce v4 addressing
each of the seven findings and append part-by-part dispositions to `ledger.md`.
For domain-v3-3, the driver's recommendation is to distinguish minimum-sample
screening from fit validity, keep 1.0/10 provisional, and specify a bounded
methodological validation plan with explicit acceptance criteria before calling
the threshold scientifically validated. Do not automatically substitute 2.0,
change the estimator, remove partial years, or add intervals in this revision.

This is a gate proposal, not an accepted design change. The alternative is an
explicit owner ruling accepting 1.0/10 as screening heuristics with limited
applicability, without a scientific precision or identifiability claim.

New findings await G1 and author dispositions; ledger closure and convergence
are not claimed. External round 1 remains unstarted. Scientific/methodological
evaluations use Astra for the rest of this run under the owner's latest ruling.
