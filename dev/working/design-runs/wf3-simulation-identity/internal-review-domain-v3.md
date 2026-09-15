---
verdict: revise
doc_version: design-v3.md
reviewer: model-validator
runtime_model: gpt-6-astra
review_date: 2026-09-09
reviewed_commit: 7e4f5031ea2354b523b64fec5648072fe517e3dd
reviewed_sha256: 19C28793BDC52CB25FC678D414C05A64F2C9D1D11E1539D9E58C8098C61D2F01
severity_counts:
  blocking: 0
  major: 5
  minor: 2
findings:
  - id: domain-v3-1
    severity: major
    section: "5.1 Scenario table; 7.3 Metric bundles; GF-18"
    finding: >-
      The stochastic pairing validator has no explicit same-realization ancestry
      invariant. A forest, complete configured cross-product, and at least one
      non-empty derived_from edge do not establish the declared common-random-number
      design. A perturbed row for realization 2 may point to realization 1's root,
      or one design point may use a different root from the other points carrying
      the same rlz, while passing every concretely specified structural check.
    rationale: >-
      Current rule 3.12 encodes the stronger condition directly: the input baseline
      uses the output's same rlz_num. Moving that dependency into data removes this
      guarantee unless the stochastic provider validates it. Wrong edges change
      the actual forcing used by transform, confound design-point contrasts with
      a changed draw, and can duplicate draws in a pooled bundle. This is a risk
      introduced by the new data contract, not evidence of a current production
      pairing failure. R-3 already authorizes the stronger check.
    suggested_fix: >-
      For the production stochastic provider, require each non-empty-st_id row
      to derive directly from the unique empty-st_id root with the same rlz;
      require those roots to have no ancestor and distinct realizations to have
      distinct root identities. Retain the general forest rule for the universal
      interface. Extend GF-18 with cross-realization ancestry, a missing edge on
      one perturbed row, and a perturbed-parent chain, all refused before
      generation. Validate that transform consumes the declared ancestor. Do not
      treat distinct root IDs alone as empirical proof of independent draws.
  - id: domain-v3-2
    severity: major
    section: "6.6 Response-series protocol; 6.7 Response inventory; 7.2 Class C"
    finding: >-
      Q5's first-gauge reference is still specified in terms of a native table
      column, but no neutral response field or metric declaration identifies that
      reference location. The inventory sorts series by location, and the protocol
      does not preserve native column order. Therefore conforming readers or
      response iteration orders can choose different reference gauges and thus
      different wettest/driest months from identical response values.
    rationale: >-
      export_wflow_results._category_month explicitly selects chosen.iloc[0],
      following the first CSV gauge column. Two gauges with different seasonal
      peaks are sufficient for a location-order change to move every Class-C
      result. The first-gauge convention is pre-existing and owner-preserved;
      loss of the information needed to reproduce it is introduced at the new
      native-reader/metric boundary. An ordered response request does not itself
      specify which location is the scientific reference or require it to match
      the old first column.
    suggested_fix: >-
      Resolve and persist an explicit Class-C reference_location_id using the
      current first-gauge convention during migration. Include the reference
      members, selection statistic, tie rule, analysis coverage and resolved wet
      and dry months in the metric-set provenance; changing reference semantics
      must change metric identity. Test two gauges with opposite seasonal peaks
      and reverse their native/neutral iteration order: the persisted reference
      and selected months must stay unchanged, and GF-9 must still hold. This
      preserves R-1/R-2 and does not introduce per-location month selection.
  - id: domain-v3-3
    severity: major
    section: "7.5 Return-level estimator precondition; 7.6 Fit uncertainty; 12.1 GF-15"
    finding: >-
      The proposed ratio 1.0 and ten-block floor have no stated scientific
      acceptance criterion, and the count gate has no companion fit-validity
      contract. GF-15 tests refusal below the chosen count, not whether that
      count supports the intended estimate. A long constant or repeated block
      sample passes the formula without establishing an identifiable GEV fit;
      finite block counts can also differ by location within the same bundle.
      Calling the floor GEV_IDENTIFIABILITY_FLOOR and the resulting point
      estimates admissible overstates what this check establishes.
    rationale: >-
      Both current periods, 10 and 2 years, reduce to the same ten-block minimum;
      the 18 nominal pooled years in the rapid/current baseline configs merely
      pass that chosen rule. The current reducer drops non-finite values separately
      for each column and delegates fitting to xclim/SciPy; neither block count
      nor a returned optimization result certifies scientific precision. Short
      samples, transient forcing and absent fit intervals are pre-existing
      limitations, not newly discovered production regressions. However R-4
      explicitly made the estimator precondition a milestone obligation. V3
      acknowledges the unvalidated numbers but leaves no falsifier that could
      settle that obligation before scientific acceptance.
    suggested_fix: >-
      Separate a minimum-sample policy from fit validity and from uncertainty.
      Count and record usable blocks per metric, bundle and location, with member
      counts, temporal coverage and the preserved partial-block/missingness rule.
      Specify named refusal for degenerate samples, failed/non-finite fits and
      invalid output parameters or quantiles using the existing estimator's
      supported outputs. Add constant-block, location-specific missingness and
      fit-failure fixtures. Supply a bounded methodological validation criterion
      for the selected ratio/floor, or obtain an explicit owner ruling that these
      are screening heuristics with limited applicability rather than validated
      precision/identifiability thresholds. Do not silently switch to ratio 2.0,
      change the estimator, remove partial years, or add fit intervals under the
      identity migration. The separate interval-deferral ruling remains for G2.
  - id: domain-v3-4
    severity: major
    section: "8.4 Metric-set identity and provenance; 8.5 Invalidation matrix"
    finding: >-
      Metric-set identity omits the environment actually used for stage-3
      recomputation. The stored simulation environment describes a past stage-2
      execution, while metric_definition_sha256 covers declarations and reducer
      code. A metrics-only run with unchanged retained responses and repository
      code but changed xclim, SciPy, pandas or other numerical dependencies can
      therefore reuse the same metric_set_id despite using a different estimator
      implementation or aggregation behavior.
    rationale: >-
      The current reducer directly relies on xclim statistical fitting, pandas
      resampling and rolling, and NumPy numerical behavior. V3 deliberately
      permits metrics to outlive the original simulation environment and puts
      immutable results under a content-derived metric-set identity. Without a
      stage-3 environment input, that identity cannot distinguish scientifically
      different recomputations, and metrics.json cannot fully explain which
      implementation produced a value. This is an omission introduced in the
      new freshness contract; no dependency-induced numeric drift was measured
      in this review.
    suggested_fix: >-
      Persist a stage-3 environment/dependency descriptor and include its digest
      in metric-set identity, or explicitly require and verify the exact recorded
      metric execution environment before recomputation. Cover the numerical
      dependencies used by the response reader and reducer, not only repository
      source bytes. Add a falsifier where changing this descriptor creates a new
      metric set while collection and simulation identities remain unchanged.
  - id: domain-v3-5
    severity: major
    section: "8.1 One mixed sequence; 9.4 Acyclic seed resolution; GF-27"
    finding: >-
      The automatic seed material includes unit_id_capacity because it includes
      generation configuration except seed and execution-only fields. Capacity
      is a required generation setting and is not listed among the exclusions.
      Thus changing only identifier headroom can reseed the stochastic forcing,
      instead of merely creating a differently named collection of the same
      climate draws.
    rationale: >-
      Capacity has no climatic meaning; it exists to reconcile the mixed sequence
      with independent generation. Its currently stated cost is regeneration and
      possibly wider IDs, but the seed equation adds a scientific change: a user
      increasing capacity for a later metric bundle can obtain different weather
      and hydrological values. This concerns newly authored auto configurations;
      the proposed migration to explicit old integers correctly protects existing
      projects. The dependency is a consequence of the specified input set, not
      a measured seed collision or a claim about an implemented resolver.
    suggested_fix: >-
      Define the seed-material projection explicitly and exclude namespace-only
      capacity and other storage/identity choices. Capacity may remain in
      collection_id as approved, but must not choose the random draw. Extend
      GF-27 so capacity-only and ID-width-only changes preserve resolved_seed
      and scenario forcing values under a run crosswalk, while still creating
      the required new collection namespace. Retain explicit-integer migration.
  - id: domain-v3-6
    severity: minor
    section: "5.3 Generator adapter; 6.4 Forcing compatibility; 7.5 Temporal reduction"
    finding: >-
      The preservation obligation would be clearer if it named the existing
      calendar and endpoint handling as an explicit adapter acceptance case.
      Current preparation converts a noleap CFTimeIndex to datetime64, sets the
      Wflow calendar to standard, clips to the forcing window, and rewrites TOML
      endpoints from the remaining axis. These are repository adapter operations,
      not merely metadata labels supplied by an upstream model requirement.
    rationale: >-
      V3 correctly requires explicit calendars and retention of the existing
      numeric path. Its separate restriction to existing upstream conversions
      could nevertheless be read as forbidding this already-present adapter
      handling. Also, regular daily intervals on a noleap calendar do not by
      themselves establish a gap-free standard-calendar axis across leap day.
      No observed temporal defect is asserted; the ambiguity matters when the
      new compatibility validator is bound to actual files.
    suggested_fix: >-
      Name source, prepared-forcing and response calendars separately; record the
      existing conversion/clip operations and actual endpoints. Include leap-year,
      right-labelled endpoint and non-January water-year cases in the bounded
      preservation gate. Report any existing mismatch for a separate method
      decision rather than silently repairing calendar or annual-block semantics
      during this migration.
  - id: domain-v3-7
    severity: minor
    section: "14.1 Decision-to-section map; frozen evidence premises E6, E13, E17, E19"
    finding: >-
      The frozen evidence register requires qualified dispositions when carried
      into the successor: E6 overstates expiry of failure-identification needs;
      E13 attributes a current WG-4 clause to WG-2; E17 overstates inevitable
      renumbering; and E19 has no operational coordinate-comparability evidence.
      These are historical premise limitations, not four new production defects.
    rationale: >-
      V3 already preserves per-run failure association, maps the naming clause
      to WG-4, scopes IDs to collections and excludes the future GCM provider.
      Those bounded resolutions should not turn the original claims into blanket
      factual endorsements. In particular, a paper schema carrying delta columns
      establishes representability, not scientific coordinate comparability.
    suggested_fix: >-
      Retain the individual qualifications and settling observations in this
      review's premise table when recording evidence closure. No edit to the
      frozen intake is required. Treat E19 as outside current production scope;
      its future settling observation is a provider example with explicit
      reference period, aggregation, units and comparable surface coordinates,
      not a new production provider in this milestone. No extra scientific run
      is required to settle the source attribution or E17's arithmetic.
---

# Independent domain review of design v3

The two-workflow, three-stage framing is scientifically coherent for the approved
stochastic/Wflow scope. **Revise the contracts before accepting v3.** Five major
findings concern pairing, the Class-C reference, return-level acceptance, metric
reproducibility and automatic seed semantics. None requires another production
provider, another simulator, a third workflow, CMIP-driven forcing or calibration.

This is a design and premise review, not a validation of generated climate or
hydrological performance. It cannot establish numerical equivalence or
fit-for-purpose model skill from a specification. The interrupted reviewer wrote
only the invalid `IN_PROGRESS` placeholder; this report supplies a fresh verdict.
Earlier reviews and the ledger were not used to seed findings. References to them
inside v3 were treated as author traceability, not independent evidence.

## Review basis and coverage

The complete 1,892-line v3 was read and its SHA-256 was verified against the
dispatch. The inspected checkout HEAD was `7e4f5031ea2354b523b64fec5648072fe517e3dd`.
Scope came from the frozen intake, the owner-ruling and current-scope portions of
`status.md`, and `scope-expansion-2026-09-09.md`. The paper candidate schema was
read to understand the accepted R-6 interpretation; it is not an executed second
provider. P1/P2 and P3/P4/P5 were read, including P4's real-rule addendum.

The model-validator persona and `claim-evaluation` were applied. Conditional
method references were `time-series`, `hydro-indicators` and
`climate-stress-testing`; the review-loop findings and artifact schemas governed
the verdict. No simulation, scientific experiment, package mutation or test suite
was run. Verification consisted of source/document inspection, hash/HEAD checks,
and analytic counterexamples. Existing probe measurements remain attributed to
their authors and recorded environments.

The principal current-code evidence is:

- `blueearth_cst/experiment/export_wflow_results.py`: identity parsing, native
  gauge ordering, Class A/B/C reductions, finite-block filtering and output
  precision.
- `run_stress_test.smk`: same-realization forcing ancestry, current wildcard
  rules, flat ordered batches and temporary forcing outputs.
- `blueearth_cst/experiment/downscale_climate_forcing.py`, `forcing_window.py`
  and `run_wflow_batch.jl`: preparation boundaries, calendar/endpoints, PET
  source choice and per-member failure visibility.
- `blueearth_cst/shared/indicator_tables.py`: vocabulary, five-column shape,
  pooled sentinel and the reserved but currently unemitted basin scalar.
- `dev/reference/contracts/weather-generator-seam.md` and
  `dev/milestones/r09/wf3-change-requests.md`: live interchange and historical
  identity rulings.
- Current rapid and baseline WF3 configs: two realizations and the 2046–2054
  simulation window. Their comments describe 18 nominal pooled years; this
  review did not count actual valid blocks from a new run.

## Method fit and claims that survive review

The forcing collection, simulation response inventory and metric-unit index
represent different scientific objects. Separating them removes the need to
pretend a pooled extreme-value estimate is one realization. Declaring `grain:
run` for Class C preserves useful between-realization variation while selecting
one common reference month, as R-1/R-2 require. Neither move changes the intended
bottom-up question.

The simulator's boundary is appropriately independent of scenario type. It may
depend on model state, forcing compatibility and result-affecting settings, while
the provider owns perturbation semantics. A completed collection can support
multiple simulations; native Wflow output can remain the retained persistence
format if the neutral reader satisfies the complete response contract. Fixture
substitution is a boundary test, not evidence that a second simulator gives
equivalent hydrology.

CMIP products remain terminal plausibility information, with no generation or
simulation dependency. Reordering the convenience runner so projection analysis
is last is consistent with that constraint. No local calibration is proposed;
equivalence to the existing global-data Wflow model remains the relevant
migration claim, distinct from observational adequacy.

The revised GF-9 is necessary and well scoped: use fresh pre/post outputs under
the same current composed config, account for all rows, preserve A/B, and compare
old pooled C to the mean of its new run-grain counterparts. The standing stale
baseline is correctly excluded as the causal comparator. The Class-C equality
also requires equal effective year/month weights after missingness, not merely
identical calendar names and nominal year counts. The comparator must expose a
failure of that condition rather than normalize it away.

## Premise disposition: frozen E1–E20

`supported` means supported within the stated historical/current scope, not
scientifically proven by an execution in this review. `contested` identifies a
false or overbroad statement as written. `untestable as stated` means the asserted empirical
conclusion cannot be settled from the available records. Every contested or
`untestable as stated` row below names a finding and a settling observation or an
explicit scope limit.

| Premise | Disposition | Evidence and consequence / settling observation |
|---|---|---|
| E1 | supported | Current `member_from_run_csv` uses `_MEMBER_IN_STEM` and refuses a nonmatching stem. Explicit run records remove a real undeclared interface. |
| E2 | supported | Current `_k_members`, `_batches` and dynamically named batch rules have static member lists and batch-keyed log/benchmark paths. This statement applies to the batch rule. |
| E3 | supported | Current rules 3.12 and 3.14 retain `rlz_num`/`st_num` wildcard paths. Flat execution batching never implied the preparation/generation graph was already neutral. |
| E4 | supported | Historical C24 explicitly retains `(rlz, st)` and lists pooling, renumbering, realization batching and failure-log legibility. The record is historical authority, not a current-code description. |
| E5 | supported | C24's specific realization-wildcard batching premise is contradicted by the current flat batch shape. Its stated implementation reason has expired. |
| E6 | contested | Batch log filenames no longer encode the member, but `run_wflow_batch.jl` still reports the per-member TOML-derived tag in success/failure messages. Thus the original operational need to identify what failed has not expired wholesale. Read log identity and message identity separately; v3 §6.5 already preserves explicit run association. Domain-v3-7 records this historical qualification, with no additional production fix required. |
| E7 | supported | `INDICATOR_COLUMNS` is exactly `metric,location,st_id,rlz_id,value`. The proposed four-column shape is an intentional migration. |
| E8 | supported | `POOLED_REALIZATION = 0` occupies the realization key column, with the documented single-grain-per-metric restriction. Explicit unit grain removes this ambiguity. |
| E9 | supported | The current emitter writes A per realization, B from pooled blocks and C from pooled fixed-month responses. This supports separating metric membership from the scenario table; R-2 intentionally changes C storage. |
| E10 | supported | Both the reducer docstring and code extract rolling seven-observation minima inside each realization, then concatenate scalar annual blocks. V3 §7.5 preserves the scientifically relevant ordering. |
| E11 | supported | At `st == 0`, current code pools unperturbed responses, selects wet/dry months once and carries them through subsequent design points. It selects using the first gauge. Domain-v3-2 addresses loss of that reference location at the new seam. |
| E12 | untestable as stated | The code documents pooling to enlarge a short GEV block sample, and concatenation increases its nominal size. The stronger precision/conditioning claim is not established by those statements or by a nominal count. Independence, degeneracy, temporal homogeneity and the estimator matter. A specified fit-validity/precision diagnostic across declared sample sizes would settle its intended use; domain-v3-3 identifies the missing acceptance criterion. No such experiment was run here. |
| E13 | contested | The naming pattern and pinned-surface wording are present, but in current **WG-4**, not WG-2. WG-2 now describes the perturbation lookup. Reading the live headings settles the source attribution. V3 §9.2 maps WG-4 correctly, so this is a pre-existing frozen-register citation error, not a new design defect. Domain-v3-7 records the qualification. |
| E14 | supported | WG-5 requires a per-member catalog entry including `st_0`; current rule 3.14 declares the catalog `temp()`. The live seam prose also contains a contradictory old `not temp()` bullet. The rule settles the current lifecycle, and v3's explicit successor clause avoids inheriting that prose contradiction. |
| E15 | supported | Historical C28 was explicitly provisional and named a third-dimension revisit. Current indicator axes have since left the result table; v3 correctly supersedes the historical ruling instead of treating it as today's seven-column contract. |
| E16 | supported | `dev/LOG.md`'s 2026-08-18 row explicitly drops the item, enumerates eight surviving references and distinguishes that decision from abandoning the work. This is historical traceability, not scientific evidence for the chosen architecture. |
| E17 | contested | Renumbering is conditional, not inevitable for every realization-count change. With v3 order, unpadded run position is `(r-1)*(S+1)+(s+1)` for `s=0..S`. Increasing R appends realizations and preserves existing positions; changing S shifts later realizations. V3 capacity fixes width independently. This algebra settles the universal claim without a run; immutable collection scoping remains justified even when old positions happen to survive. Domain-v3-7 records the qualification. |
| E18 | supported | Supported under the owner-approved R-6 **semantic** interpretation: the existing `st_id` is a perturbation-lookup foreign key and `rlz` encodes a paired draw, so relabelling arbitrary GCM/supplied cases with those existing meanings is not an honest substitution. The candidate paper schema demonstrates that distinction. It does not prove that pairs of integers cannot mathematically encode a list, or establish a production second-provider need. Neither stronger claim is required by v3. |
| E19 | untestable as stated | A point on a specified T × P plane requires coordinates in that plane, but no production GCM-derived run, reference-period contract or comparable coordinate artifact exists here to validate the proposed transport. The paper schema can carry columns; it cannot establish their scientific comparability. A future provider would need declared reference period, temporal aggregation, units and a coordinate-comparability example. V3 excludes that provider and any CMIP execution edge, so this is an explicit deferred scope limit, not a blocker for the approved stochastic implementation. Domain-v3-7 records the qualification. |
| E20 | supported | The archived `archive/wf3-experiment-v2` design's `member_hash` covers a canonical member/config/seed/input tuple. A sequential handle and such a freshness digest answer different questions. V3's layered identities preserve that distinction, subject to the missing metric environment in domain-v3-4. |

## Validation and uncertainty boundaries

The strongest acceptance gates are the bidirectional numerical crosswalk, the
configured-axis completeness check, explicit reference refusal, and the tests
that remove producers from metrics-only operation. The unexecuted P2b and
conditional-target probes are correctly labelled as future feasibility gates.
P3 proves catalog lookup on its recorded synthetic raster; it does not prove
hydrological equivalence. P5 proves prefix classification; it does not validate
an entire successor output tree. P4's real-rule addendum supports the corrected
distinction between config-triggered reruns and imported-code blindness.

Pairing uncertainty and sample size need careful interpretation. A correct
`derived_from` forest establishes construction provenance; it does not estimate
the effective independent information in annual extrema. A/C run-level spread
is conditional on the selected generator, forcing source, model and perturbation
design. With the current two-realization fixtures it is two values, not a
calibrated uncertainty interval. Structural, parameter and observational
uncertainties are not covered by that spread. Class-B fit uncertainty remains
absent, and reference-month selection uncertainty is shared across all C values.
These are limits of the inference, not requests to add an uncertainty platform.

The current fixtures use transient perturbations. Pooling their annual blocks
preserves the existing statistic, but the fitted level is conditional on that
window and construction; preservation alone does not establish a stationary
future recurrence probability. Similarly, unchanged Wflow outputs do not
establish observational skill or validity for a new basin. No observation-based
benchmark, holdout comparison, numeric uncertainty bound or hydrological
adequacy score was available or computed in this design review.

The external checks were limited to primary estimator documentation. Xclim's
frequency-analysis documentation describes block extraction and fitting through
SciPy distributions, including alternative estimation methods. That confirms
why the numerical dependency environment belongs in provenance; it does not
validate a ten-block threshold. [Xclim frequency analysis](https://xclim.readthedocs.io/en/stable/notebooks/frequency_analysis.html).
SciPy documents that a fit may fail or find a local rather than global optimum.
This supports a distinct fit-validity condition rather than treating a count as
the acceptance result. [SciPy fit contract](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.rv_continuous.fit.html).
These documentation checks are not evidence that the repository's current fit
has failed.

## Framing decisions and bounded corrections

**Owner framing decisions:** the two-workflow split, three contracts, production
stochastic/Wflow bindings, terminal CMIP overlay and approved names can stand.
The outstanding scientific choice is what evidence or explicitly limited
screening interpretation accepts the proposed return-level ratio/floor before
landing. Separately retain the recorded G2 owner decision on deferring Class-B
fit intervals. This review does not ratify that deferral by calling the design
scientifically validated.

**Corrections within approved scope:** enforce same-realization ancestry;
persist the existing Class-C reference location and resolved months; define
location-specific block counts and fit-failure handling; fingerprint the metric
execution environment; remove namespace capacity from automatic seed material;
and make legacy calendar preservation an explicit acceptance case. These close
contracts already authorized by R-1–R-4 and the scope addendum. They do not
require reopening `run_id`/`unit_id` naming, implementing another backend,
changing the perturbation method or launching a scientific run during design.
