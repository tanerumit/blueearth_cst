verdict: approve
doc_version: design-v1.md
findings: []

## Scope and conclusion

Pre-G1 scientific preservation review of `design-v1.md`, using `intake.md`, its directly cited
source, the retained-root inventories and `caption-layout/capture.py`. Applied `claim-evaluation`.
No implementation, simulation, numerical comparison or visual parity run was performed.

The proposed array and endpoint boundary can represent the current plotted scientific quantities
without changing their meaning. The design retains aggregation, completeness, availability, month
ordering, weights and trend fitting in workflow-owned preparation. Its acceptance checks can falsify
preservation of values, gaps, bands, trends and their displayed interpretation. This approves the
scientific framing and proposed verification contract; it does not demonstrate runtime equivalence
or authorize implementation before G2.

## Premise dispositions

| ID | Disposition | Inspection evidence and limits |
|---|---|---|
| E1 | supported | `forcing_figures.py:176–251` constructs View and calls annual/monthly artists. |
| E2 | supported | `func_plot_signature.py:308–368` constructs View and retains distinct ticks/legend. |
| E3 | supported | `diagnostic_figures.py:386–425` draws supplied mean/p10/p90, computing no quantiles. |
| E4 | supported | `diagnostic_figures.py:1010–1058` uses retained fit and first/last nonmissing years. |
| E5 | supported | `diagnostic_figures.py:772–805` calls `_annual_trends` inside each metric chart. |
| E6 | supported | Named roots contain WF0 PNGs/captions, nine forcing PNGs and hydrological summaries. |
| E7 | untestable as stated | Prospective hypothesis; no extracted implementation exists for comparison. |

E6 supports file presence, not complete case coverage or scientific equivalence. The inspected WF1
evaluation root includes basin-average AET and recharge annual/monthly PNGs; this does not establish
stock, optional-subbasin or every edge-case coverage. The design explicitly requires new matched
captures for missing coverage and blocks acceptance of uncaptured products.

E7 is testable after implementation by the proposed comparisons. “Untestable as stated” here means
unresolved by the present inspection-only evidence, not inherently unfalsifiable or contradicted.
The source supports plausibility: the current artists already receive summaries and retained fits.

## Scientific preservation and falsifiability

- Annual arrays preserve the plotted estimand when adapters retain `.reindex(years)`, source order
  and NaN positions. Matched preparation capture detects value or gap changes before rendering.
- Trend segments retain the existing finite-slope/nonempty-`dropna()` predicate, endpoint years,
  intercept and slope/10 arithmetic. The design correctly avoids substituting finite-value filtering,
  refitting or changing units. Endpoint, label and annotation comparisons expose a decade-scale
  error, changed eligible span or shifted interpretation; separated annotation positions remain
  drawing behavior rather than new trend estimates.
- Monthly arrays retain mean and empirical p10/p90 in their existing row order. Explicit ordered
  month labels and non-January cases can expose a month/value misalignment. Bands remain interannual
  spread, with their meaning carried by caller labels and captions rather than inferred by the core.
  Hydrological negative values remain visible because those callers retain unrestricted y-limits.
- The existing recorder cannot alone establish band or trend-label parity: it omits band vertices,
  axis legends and axis annotation content/positions. Section 6 explicitly requires extending it,
  comparing exact numeric values with aligned NaNs, and supplementing geometry with rendered pairs.
  This addresses the plausible alternative of unchanged appearance hiding changed numeric content.
- Matched before/after inputs and separate roots limit confounding by changed data or overwritten
  evidence. Available/unavailable trends, missing temperature, gaps, constants, negatives, multiple
  sources and hydrological amount/rate/stock cases address distinct failure regimes. Captions and
  inventories constrain changes to scientific interpretation and product availability.

The design is adequate for a rendering-preservation decision. It makes no claim that the underlying
hydrological model, fitted trends or observational inputs are scientifically validated by this
extraction. Confidence is high in the source-supported boundary and conditional in post-extraction
parity: implementation errors, uncaptured products and visual regressions remain unresolved until
the specified matched-input evidence and rendered-pair review are complete.
