---
verdict: revise
doc_version: design-v1.md
findings:
  - id: domain-1
    severity: blocking
    section: "3.1 Project-owned historical reference settings; 4.1; 6; 9.1"
    finding: >-
      The accepted completeness domain permits an entirely missing amount field to become a finite
      zero reference. With max_missing_days_month=31 and max_missing_days_year=366, an all-NaN full
      year passes the existing valid_years predicate. dg.annual then sums the still-missing series
      to zero, and annual_fields counts that zero as an eligible year. Reusing this method unchanged
      contradicts the promised missing-is-not-zero and unavailable-reference behavior.
    rationale: >-
      The static path is diagnostics.py:83-107 followed by diagnostic_maps.py:38-43. Infilling a month
      with no observations cannot produce its monthly mean; the default amount sum nevertheless
      yields zero and the generous threshold does not invalidate it. The reference would therefore
      publish a numerical scale and positive valid-year count for an unobserved precipitation or
      PET cell. A wholly missing month can similarly depress a partially observed annual amount.
      This defect exists in the old WF0 calculation for permissive settings; introducing a shared
      reference configuration with the same unrestricted domain propagates it to both workflows.
      Ordinary 3/15 defaults are not implicated by this counterexample. The driver independently
      confirmed the all-missing full-year counterexample in intake E11 and all-missing-probe.log;
      the missing-month extension remains a source-derived deduction.
    suggested_fix: >-
      Make a G1 choice between explicitly narrowing the accepted reference-policy domain so it
      cannot admit a month with no observations, and an approved eligibility guard that marks such
      annual amounts unavailable. State the compatibility and scientific-preservation exception
      for the selected remedy. Add an independent full-year all-NaN case and a wholly missing-month
      case at the largest accepted thresholds; assert unavailable values and zero eligible counts,
      rather than parity with the old aggregator. Show that the check detects the old failure.
  - id: domain-2
    severity: minor
    section: "2.2 Proposed support; 4.1 Preparation; 9.1 Native science retained"
    finding: >-
      Distinguish preservation of retained source arrays from exclusion of borrowed CHIRPS
      temperature in the pool. The current selected-CHIRPS path can retain borrowed temperature in
      annual_climatology.nc, and the old pooled renderer tests variable presence rather than source
      role. The proposed honest-source exclusion is appropriate, but the preservation check does
      not explicitly name this case or whether those retained auxiliary arrays remain unchanged.
    rationale: >-
      compute_climate_diagnostics.py:39-56 leaves raw unchanged when carries_temp is false;
      annual_fields loops over every present precip/temp/pet variable. diagnostic_render.py:156-165
      can therefore pool the borrowed temperature. source_climate_vars explicitly says that selected
      precipitation-only stores borrow companions but must not claim them as source observations.
      This is a preexisting pooling leak corrected by the proposal, not a reason to retain it.
      An unqualified array-preservation oracle could confuse its intentional removal with a
      regression if the new helper filters retained arrays as well as reference contributions.
    suggested_fix: >-
      Add selected CHIRPS with enriched borrowed temperature, alongside extra CHIRPS without it,
      to the named real-preparation cases. Explicitly preserve auxiliary retained arrays while
      excluding them by role, or declare their removal as an intentional change. In both cases,
      require no CHIRPS temperature/PET reference contribution, unchanged native precipitation,
      and unchanged genuine ERA5 temperature/source-PET fields.
  - id: domain-3
    severity: minor
    section: "Intake E9; 8 Alternatives; 9.1 Cost E9"
    finding: >-
      E9, that WF1-only pooled reductions have acceptable cost, is untestable as stated because
      neither an acceptance threshold nor an owner decision criterion defines acceptable.
    rationale: >-
      Timing extraction, hashing and preparation and recording peak memory can measure cost,
      but cannot falsify acceptability without a bound or an explicit decision rule. The design
      correctly discloses this limitation and makes no demonstrated performance claim, so it
      does not presently invalidate the scientific method.
    suggested_fix: >-
      Before accepting E9, record an owner-selected time/memory budget for named source count,
      grid and historical-window cases, or reframe E9 as a measurement objective and remove
      acceptability as an asserted premise. Keep extraction, hashing and reduction measurements
      separate and disclose repeated WF0 reduction cost.
---

# Scientific review of design-v1

Reviewed SHA256: `b3b6510335d863cfac447d18b56c1c291a7da6bbeaa488afc0d41317c4fb8e2d`.
Source context: session-1 `22fbe441cef67db45130834eab87a31f8e3b6fc7`.
Review scope: complete frozen design, intake E1-E11, status, and relevant repository source.
Framing remains provisional; this report grants neither G1 nor implementation approval.
Verdict: **revise**, with **1 blocking, 0 major and 2 minor findings**.

## Intended inference and scientific judgment

The intended product is a common display reference for historical candidate maps and model-forcing QA.
The quantity supplying its limits is the minimum and maximum of eligible cellwise annual climatologies
over the specified source/frame support. It is not a pooled basin climate estimate, a historical
extreme-event distribution, a model-skill score or an uncertainty interval. This distinction makes
unweighted extrema across unequal native grids defensible for the stated purpose. Denser grids can
supply more extreme cell values, and short or different records can alter limits; shared colors do
not remove those differences. The design appropriately acknowledges this.

No calibration/validation split, naive predictive benchmark or ensemble interval is warranted for this
display-reference contract. Scientific validation here requires preservation of the underlying fields
and independent analytical checks of eligibility, pooling and classification. It cannot establish
hydrological adequacy, source accuracy or causal attribution of differences to downscaling.

The selected-source full extraction is a coherent viewport authority. It intentionally changes WF0
clipping and extrema support. The alternative padded-basin support is also defensible, but answers a
different display-support question and needs extensions for visible cells omitted from the pool.
Neither choice creates equal spatial support. The ordinary journey and shared producer boundary are
consistent with WF0 remaining optional; the extra WF1 candidate work requires a separate cost decision.

## Evidence-register dispositions

These dispositions separate static observations from prospective runtime outcomes.

| ID | Disposition | Basis and limit |
|---|---|---|
| E1 | supported | `analyze_climate.smk:104-121` constructs selected-first, deduplicated candidates. |
| E2 | supported | `diagnostic_render.py:156-179` pools, then replaces with all cells for <=1 grid. |
| E3 | supported | `build_model.smk:312` has one store; `forcing_figures.py:198` derives finite limits. |
| E4 | supported | `plot_map_forcing.py:89-96` gets selected precipitation edges and native resolution. |
| E5 | supported | `annual_fields` uses `dg.annual`, sum/mean by variable; domain-1 limits validity. |
| E6 | supported | `draw_map` derives classes and field-latitude aspect, with automatic tick locations. |
| E7 | supported | WF0 parses its settings; WF1 uses defaults. Optional WF0 cannot own shared policy. |
| E8 | supported | Supported as a testable hypothesis with a paired-root falsifier, not as a result. |
| E9 | untestable as stated | Measurement is specified, but acceptable has no threshold; domain-3. |
| E10 | supported | `workflow_archive_launch.py:650` encloses child execution in project-execution lock. |
| E11 | supported | Driver probe: all-NaN 2020 amounts give 0 at 31/366, NaN at 3/15; domain-1. |

E8 still needs genuinely matched project/source/settings identities, both route configurations and
fresh outputs. Any reference-byte or resolved frame/class difference refutes the specified property.
Its success cannot be inferred from source review or from two reviewers agreeing. E10 establishes a
static ownership boundary only; concurrent execution and failure behavior remain untested.

## Scientific contract checks

- **Native support:** no interpolation or area weighting is added. Basin-cell membership is used by
  the existing temperature gate, while the reference extrema use viewport intersection. Those are
  distinct operations and should remain explicit in lineage.
- **Intersection:** closed rectangles, including boundary-only touches, are a reproducible policy.
  Such a cell may have zero visible area yet change the scale. Reported pooling counts must not be
  described as counts of positive-area visible cells. This is a disclosed policy choice, not a
  mathematical error. The independent oracle should include a boundary-only extreme cell.
- **Source identity:** exclude CHIRPS borrowed temperature even when present in a selected forcing
  store. Genuine temperature eligibility comes through `daily_series`; source PET is derived via
  the existing source-grid orography/de Bruin path and is not an observed source variable. Domain-2
  isolates the old pooling leak. Temperature availability does not by itself prove PET inputs exist.
- **Units:** preserve the Celsius/legacy normalized-K gate without double conversion, and preserve
  annual amount units. The temperature gate operates on basin-mean values, not every viewport cell;
  preserving it is not a new guarantee of physically valid temperature at every cell.
- **Periods:** requested dates, actual extracted dates, full reporting years and cell eligibility are
  different. Source-period and forcing-period disclosure is essential; differences cannot be read
  solely as source bias or downscaling effects. Effective date ranges and positive count ranges are
  summaries, not proof that cells use identical sets of years.
- **Missingness:** defaults preserve the existing infilling policy. The source aggregation must not
  be treated as independently validated merely because it is reused; domain-1 is a counterexample.
  Infinity treatment also differs between source and forcing preparation and warrants preservation
  evidence, without silently changing either method in this display increment.
- **Classes:** outward rounding, raw extrema retention, a final upper-inclusive class and strict
  extensions are coherent. Probe every boundary, the exact outer endpoints and adjacent values;
  ordinary BoundaryNorm behavior must not be assumed to implement the specified final endpoint.
  Constant fields need their numerical working range distinguished from observed variability.
- **Unavailable reference:** a finite forcing field with no historical scale is scientifically
  available but unscaled. The neutral/hatch display and absent numerical bar are appropriate.
  Missing inside cells, white outside-basin cells and uncovered frame area have distinct meanings.
- **Configuration:** project ownership plus a WF0 equality guard avoids route-dependent policies.
  Retaining forcing completeness at 3/15 is scientifically conservative, provided captions state
  both policies. The enlarged accepted configuration domain needs domain-1 resolved first.

## Verification-plan adequacy and falsifiers

The plan is substantially falsifiable but needs the domain-1 cases to avoid certifying inherited wrong
results. An exact pre/post comparison is a preservation oracle, not an independent scientific oracle.
The native-field check should compare coordinates, values, eligible counts and NaN masks under matched
inputs; any difference needs classification as intended display change, approved method change, noise
or regression. No numerical tolerance should be widened solely to obtain a pass.

| Claim | Discriminating observation required |
|---|---|
| Native science retained | Same native arrays/counts/masks; explicit borrowed-variable disposition. |
| Valid eligibility | Hand-derived missing-month/full-year cases cannot produce false zero totals. |
| Honest variable roles | Selected and extra CHIRPS never enter temperature/PET source pools. |
| Unit and PET fidelity | Known Celsius/normalized-K and unresolved units exercise the real gate. |
| Pooled support | Unequal grids and a boundary-only extreme give independently derived extrema. |
| Year semantics | Leap/non-January/truncated records select the independently expected years. |
| Display classification | Exact boundary and adjacent values give specified classes/extensions. |
| Mask and empty semantics | In/outside missing cells and finite unscaled cells remain distinguishable. |
| Route independence | Matched fresh A/B outputs have identical record bytes and artist settings. |
| Identity and reuse | Changed data/settings/method inputs cannot pass stale record validation. |
| Availability/inventory | Conditional source maps and the nine forcing products follow declarations. |
| Temporal preservation | Existing chart inputs/metadata and matched renders remain unchanged. |
| Portable core | Standalone render works with its declared minimal imports and no workflow IO. |
| Publication/concurrency | Interruption or competing owned runs cannot yield accepted partial data. |
| Cost | Measurements against a defined budget, or an explicitly non-acceptance measurement objective. |

The proposed rapid renders, retained pre-change arrays, fresh paired roots, synthetic edge cases and
real preparation path add distinct coverage. The all-five gate is software/execution evidence and
cannot substitute for these numerical or visual checks. Orography input qualification and runtime
record identity remain prerequisites, not demonstrated facts. This reviewer performed no model runs,
numerical probes, rendering, tests or network requests. During review the driver supplied E11, a
successful isolated `dg.annual` probe whose retained log was read: `{2020: 0.0}` at 31/366 and
`{2020: nan}` at 3/15 for a full leap year of missing daily amounts. This confirms one inherited
failure, not the proposed producer's behavior. The design hash remained unchanged.

Testing-policy assessment: this review is read-only with numerical claims affected. For subsequent
implementation, shared configuration/DAG changes invoke the repository's broader software gates;
the scientific checks above remain focused. `.testing-policy.yml` and the validation-ladder planning
section were read. Searches traced `annual_fields`, `daily_series`, `source_grid_climate` and
`prepare_forcing` across repository callers and tests. No source files were changed or deleted.

## G1 decisions and limits

G1 should explicitly decide selected-frame versus padded-basin pooling, inclusive boundary support,
the completeness remedy and migration, honest-source filtering/preservation, unavailable-reference
appearance and the extra WF1 cost criterion. The proposed record location and shared producer serve
the stated journey; scientific evidence does not require another cache or mandatory WF0 diagnostics.

The display method is defensible after the missing-data defect is resolved. Its applicability remains
regular geographic native grids, supported source identities and disclosed source-specific records.
Common colors do not validate either source climate or Wflow forcing and do not quantify observational,
PET-method, spatial-support or sampling uncertainty. No numerical bounds on those uncertainties have
been estimated here; candidate counts are not independent ensemble size. Runtime equivalence, the
real orography path, visual readability and performance remain unverified.
