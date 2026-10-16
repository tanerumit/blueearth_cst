## Verdict
verdict: revise
doc_version: design-v2.md
scope: annual coverage and authored-ID decisions only

## Finding dispositions

**ext1-1 [major]: confirmed, with qualified wording. v2 must change.**
- **What the code shows.** I checked the source myself:
  - `reduce_run` computes `getattr(frame.resample(anchor), "sum")().mean()` (`metric_registry.py:325`).
  - The anchor is `YE-<month before start>` (`snake_utils.py:467-479`).
  - The WF3 window renders as `{start}-01-01T00`–`{end}-12-31T00` (`forcing_window.py:36`).
  - v2 says the first label is starttime+step.
- **The exact identity.** With no missing values, every block sum adds into the total retained depth D. So the reported value is D/B, where B is the number of blocks. The record-normalized annual depth is D/L, where L is the labelled record length in years. Their ratio is L/B. This identity is exact and does not depend on seasonality.
- **Where N/(N+1) comes from.** It is only the special case where L≈N whole years and the anchor is misaligned, so B=N+1.
- **What I qualify in ext1-1:**
  - Its comparison target is D/L. Relative to the mean of complete water years, the edge blocks match only approximately (stationary seasonality, low interannual variability). The ratio is not a measured bias.
  - It assumes the WF4 member window equals `forcing_window`. That is not verified.
  - It assumes no NaN. Under `min_count=0`, missing days and all-missing blocks lower D but still count toward B.
- **The prior ruling.** The 2026-08-08 ruling is real (`indicator_tables.py:214-224`). v2 line 173 calls it "source's mm/yr prose", which is inaccurate. It must be reconciled explicitly.
- **Why this is still major.** The dictionary header and `named-metric-export/1` would freeze a public contract. That contract has no way to tell the user whether a value is an annual depth or D/B with B>L.

**ext1-2 [major]: confirmed. v2 must change.**
- The five method whitelists allow exactly 16 calculations: q has 4 annual_summary, 2 rolling, BFI, 2 month and 2 return levels (11). The basin variables have 5 annual_summary. That equals `Q_METRIC_SUFFIXES` (11) plus `BASIN_METRIC_SUFFIXES` (5).
- So an authored entry can only rename an existing calculation.
- v2 never says whether the authored ID, which is written into the CSV `metric` key, belongs to numerical identity. P4's "deduplicate only identical numerical requests" therefore has two possible readings.

**ext1-3 [minor]: confirmed, as an acceptance check only.**
- Per-set plans with no cross-set cache can diverge without detection.
- Under resolution 2A, a shared definition's rows must be byte-identical across sets.
- Under 2B, an alias's values must equal the registered definition's values, with only the metric key differing.

**ext1-4 [minor]: confirmed. Wording change in O2 and in `block_assignment`.**
- Production uses `YE-DEC`/`YE-SEP`, which are right-closed and right-labelled.
- I checked that for midnight interval-end labels this gives the same split as `YS-JAN`/`YS-OCT`. For example, 2000-09-30T00 falls in the bin ending 2000-09-30 under both.
- Text and fixtures should therefore come from `water_year_end_anchor(climate.water_year_start)`. Resolution 1's coverage cell depends on this.

**ext1-5 [minor]: qualified.**
- Month selection really does use pooled calendar-month sums (`metric_registry.py:281`). Disclosing that belongs in the dictionary.
- The "about 10%" February figure is conditional algebra: 28/31 under equal daily flows and equal coverage. It is not a general effect.
- Pooled sums also depend on edge-label coverage. Under the WF3 window, January loses one label per member.
- The wording should describe the dependence on month length and coverage, not a percentage.

**ext1-6 [minor]: qualified.**
- `metric_plan.metric_request` inventories the transitive static import closure from `metric_plan.py` (`content_identity.py:84-124`; `metric_plan.py:258`). A resolver imported by `metric_plan` or `metric_registry` is therefore already covered.
- Stale reuse can only happen if both of these hold:
  - the mapping from method and parameters to a reducer lives in a module reached only by the runner;
  - the identity records only `(method, parameters)` rather than the resolved reducer statistic.
- The future check: put that mapping inside the closure, or record the resolved statistic by value.
- The ambiguity in "references" is real. Under 2A, `definition` already names entries, so only citation and Class-C policy wording need separating.

**Must change in v2:** ext1-1 and ext1-2. **Acceptance or wording only:** ext1-3 through ext1-6.

## Proposed resolutions

### 1. Units and coverage (ext1-1 / domain-2)

**Recommendation.** Keep the arithmetic and the metric IDs. Declare `output_units = mm`, with a block-depth estimand. Add one dictionary column, `block_coverage`, whose values are taken from immutable result evidence. No coverage CSV is needed.

**Estimands.**
- The code computes the block-depth estimand: the mean over water-year blocks of accumulated depth, equal to D/B.
- The normalized annual depth (D/L, mm yr⁻¹) or the complete-year mean differs whenever B≠L or values are missing.

**Alternatives considered:**
- **(a) Declare `mm yr-1` with explanatory text.** The unit would be false in the common case: any non-January water year.
- **(b) Keep "mm" with static text only (v2 as written).** Truthful, but the user cannot tell how large the effect is.
- **(c) Add a per-run coverage CSV.** Exact even when members differ, but it adds a public artifact plus inventory, recovery and C6 reader cost.
- **(d) Change the arithmetic, or exclude partial blocks.** Ruled out by the settled framing. It would be a separately commissioned new definition.

Option (c) becomes worth its cost only if member windows commonly differ. That is unverified.

**Ruling reconciliation.** This affirms the operative parts of the 2026-08-08 ruling:
- the sum reduction;
- the `annual_total` names;
- the refusal to rescale to mm/day.

It limits the ruling's "mm/yr" reading to the complete-block, no-missing case. This is a scientific unit decision for the owner to record at G2, not a silent override.

**Insertion-ready wording.**

*P2: replace lines 170-175:*
> For aet/gwr/precip annual_summary(sum), output_units=mm. Quantity: "mean water-year block depth: daily mm dt-1 values (dt=86400 s) summed within each block of the resolved anchor, then averaged with equal block weight; partial first/last blocks included without duration normalization; missing days add 0 and an all-missing block enters as 0 mm." Without missing values, this equals D/B (total retained depth over block count). It equals mean annual depth (mm per water year) only when every block is complete and no value is missing. It is not D/L, the duration-normalized annual rate. This affirms the 2026-08-08 ruling's sum reduction, metric names and refusal of mm/day rescaling, and limits its "mm/yr" reading to that complete-block condition. The owner records this unit decision at G2. No bias magnitude is asserted; the user judges applicability from block_coverage.

*P2: append after line 194:*
> At reduction time, each immutable result records per (variable, run) coverage evidence from the retained time index and missing mask, following the MonthReference.counts precedent. The evidence is: resolved anchor; first and last label; block count B; complete blocks (label count equals the days between consecutive anchors); label counts and expected days for the first and last blocks; missing daily values; and all-missing blocks. This adds no numerical identity input, because responses are already digested.

*P4: add `block_coverage` after `partial_blocks` in the header, and change "resolved from captured YAML, registry and plan" to "…, plan and immutable result evidence". Add:*
> block_coverage lists, for the metric's variable, each distinct coverage pattern with its run count, in this format: `anchor YE-SEP; 50 runs: 4 blocks (2 complete; first 273/366 d; last 92/365 d), labels 2000-01-02..2002-12-31; missing values 0; all-missing blocks 0`. Patterns are sorted by first label, then by run count. The cell describes coverage; it does not state a bias.

**Hand-checkable example.**
- Input: one run, precip constant at 1 mm/day, window 2000–2002, so labels run 2000-01-02..2002-12-31 (1095 labels).
- **October start (`YE-SEP`):**
  - Block sums are 273, 365, 365 and 92, so the value is 1095/4 = 273.75 mm.
  - D/L = 1095 / (1095/365.25) = 365.25 mm/yr. The complete-block mean is 365.
  - Coverage cell: `4 blocks (2 complete; first 273/366 d; last 92/365 d)`.
- **January start (`YE-DEC`):**
  - Blocks are 365 (of 366), 365 and 365, so the value is 365.0 mm.
  - The cell shows a 1-day partial first block, which the reader can see is immaterial.
- **Missing data:** if the 2001 block were all NaN under `YE-DEC`, the value would be (365+0+365)/3 ≈ 243.3 mm, with `all-missing blocks 1`.

**Where this applies.**
- The D/B identity holds only for sum reductions with no missing values.
- For mean, max, min, rolling extremes, BFI, the reference month and GEV, `block_coverage` is disclosure only; no algebra follows from it.
- Reference-month edge months are not described at block level.
- "Complete" assumes Gregorian daily labels. Behaviour under noleap-generated forcing, or with gaps in the label sequence, is not established.

### 2. Authored calculation entries (ext1-2)

**Recommendation: 2A, defer authored entries from schema v1.** This is the smallest coherent change.
- The seed's authoring template (`indicator-sets-design.md:133-191`) is satisfied at the level of the set file: users write reusable named sets of `{definition: …}` entries.
- Each definition binds one registered method and fixed parameters, and the dictionary shows the method and its parameters.
- **Cost:**
  - No custom metric names in v1.
  - A schema v2 when a method or parameter space beyond the registered definitions is commissioned. That commission needs registry work anyway, so the extra cost is small.
- **Framing check:** if the owner meant users to write `{method, parameters}` in v1, choose 2B.

*2A wording, P2: replace lines 135-139:*
> In schema version 1, an entry is exactly `{definition: <registered definition ID>}`. Every method/parameter combination the v1 method contracts admit is already a registered definition. An authored calculation entry could therefore only rename an existing calculation, so it is refused with migration guidance. A later schema version may add authored entries once a commissioned method or parameter space exceeds the registered definitions. That version must define authored-ID identity and alias rules. Method IDs and parameters remain registry vocabulary, shown in the dictionary.

*2A wording, P4: add:*
> Metric keys are registry definition IDs. A definition selected by several sets yields byte-identical rows over the same responses.

*2B wording, if the owner keeps authored entries. P2:*
> - An authored entry binds a registered method and validated parameters under an authored metric ID.
> - The authored ID is the metric key in the result rows, so it is part of numerical result identity. Changing the ID creates a new numerical result.
> - Title, description and authored citations are presentation only. Edits to them only refresh the publication.
> - An authored ID may not equal any registered definition ID.
> - If the resolved calculation contract (method, normalized parameters, implementation revision, registry policies) equals a registered definition, the dictionary names it in `equivalent_definition`.
> - `quantity`, `output_units`, `method`, `parameters`, the temporal/missingness/validity columns and `references` come from the registry only. Authored citations appear only in `authored_references`.
> - Within one set, refuse two entries that resolve to the same calculation contract.
> - Validators never interpret titles. A title cannot establish scientific meaning.

2B costs two dictionary columns, alias detection, and extra C3/C6 cases.

## Remaining findings

None beyond ext1-1 and ext1-2, as dispositioned above.

## Acceptance and limits

**Checks that could falsify resolution 1:**
- Run the example fixture on the pre-change source (add it to O2/O3). Expected values are 273.75, 365.0 and 243.3. Any other result falsifies the description.
- Rendering the cell for a fixture with two member windows must show exactly two patterns.
- On retained rapid responses, for each run, the value × B must equal the summed daily depth, before float32 conversion. This needs no new simulation. It shows the actual windows and B, and tests the identity against real data.
- Owner and domain record the unit decision at G2.

**Checks that could falsify resolution 2:**
- **Under 2A:**
  - An authored entry is refused with guidance.
  - A shared definition gives byte-equal rows in `default` and `example_subset` (ext1-3).
  - Dictionary method and parameters match the registry.
- **Under 2B:**
  - An alias of `q_mean_annual_p95` names its `equivalent_definition` and has equal values.
  - A duplicate in the same set is refused.
  - Changing an ID changes numerical identity; changing a title does not.
- **For ext1-6:** editing the parameter-to-statistic mapping must change identity.

**What is established by reading the code:**
- the D/B identity, together with the `min_count=0` path;
- the anchor helper;
- the forcing-window format;
- the import-closure boundary;
- the count of 16 admissible calculations.

**What is untested:**
- the actual WF4 member windows, and whether they differ between members;
- calendar and noleap labelling;
- whether NaN occurs in real responses;
- the reader's first-label behaviour;
- pandas version semantics.

No code was run.

**Next steps.** These are proposals; the design is not yet revised or approved. If v3 applies the proposed wording faithfully, the coordinator can check the diff and the owner records the G2 unit decision; no further reviewer call is needed. A focused re-review is needed only if v3 does any of these:
- chooses 2B with different identity rules;
- sources coverage from somewhere other than immutable evidence;
- declares `mm yr-1`.