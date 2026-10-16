## Verdict
verdict: revise
doc_version: design-v2.md

## Findings

### ext1-1 [major]
- **section:** Closed set schema and ownership (P2), the unit paragraph and partial-block semantics; Planning, identity and publication (P4), the dictionary header
- **finding:** The design treats the open unit question as a choice of label ("mm" vs "mm/yr"). It also says no bias has been quantified. For the annual-sum metrics (`aet/gwr/precip_annual_total`), though, the effect of partial blocks can be worked out exactly from the code, depends on configuration, and no unit label or one-row-per-metric description can show it.
- **rationale:**
  - **WF3/WF4 window:** `experiment/forcing_window.py:36` renders the simulation window as `{start}-01-01T00:00:00`–`{end}-12-31T00:00:00`. The design's own statement means the first label is 2 January.
  - **Anchor:** The anchor is `water_year_end_anchor(climate.water_year_start)`, which is `YE-<month before start>` (`shared/snake_utils.py:467-479`).
  - **January start:** A run of N inclusive years gives N blocks. The first block is short by one day, so the error is negligible.
  - **Any other start month:** The same run gives N−1 full water years plus two partial edge blocks, N+1 blocks in total. `reduce_run` computes `resample(anchor).sum().mean()` (`metric_registry.py:325`). The block sums add up to the total depth however the record is split, so the reported value equals total depth/(N+1). The mean annual depth is total depth/N.
  - **Size of the effect:** Every non-January water year therefore scales the sums by exactly N/(N+1), apart from day-count rounding. That is −4.5% for the template window 2040–2060 (N=21) and −12.5% for the build-model window 2010–2016 (N=7).
  - **The trigger is the recommended setting:** `metrics_definition.py:7-11` says basins should use their own water year. So the setting the code recommends is the one that triggers the effect.
  - **Missing data:** All-NaN blocks become a finite 0 (min_count=0). That 0 enters the mean as a zero-depth block and can't be told apart from a real zero.
  - **Prior ruling:** The design calls the existing mm/yr wording "source prose". In fact `shared/indicator_tables.py:214-224` records it as part of an owner ruling dated 2026-08-08.
  - **Consequence for users:** A user comparing `precip_annual_total` with a water balance or the literature can't tell from "mm, partial blocks included" whether a value is close to an annual depth or 4–13% low.
  - **Why this can't wait:** The dictionary header and the closed `named-metric-export/1` record are being fixed as public contracts now, and G2 needs this evidence to make the unit decision.
- **suggested_fix:**
  - Give the G2 unit decision the N/(N+1) result. State whether the decision supersedes or affirms the 2026-08-08 ruling.
  - Keep the arithmetic unchanged (settled framing). Publish readable per-run/per-location block coverage, for example as a companion CSV in each named folder. It would list block count, full-block count, shortest block length in days and all-missing block count.
  - Make the dictionary's quantity text say that the value is a mean annual depth only when every block is a full year.

### ext1-2 [major]
- **section:** Closed set schema and ownership (P2), the entry forms and method contracts; Planning, identity and publication (P4)
- **finding:** The parameter whitelists for the five methods allow exactly the 16 calculations already registered: 11 for q and 5 basin metrics, matching `Q_METRIC_SUFFIXES`/`BASIN_METRIC_SUFFIXES` and the fixed return periods 10 and 2 years. So the authored `{id, title, description, references, calculation}` form adds no numerical capability. What it adds is the ability to put an existing calculation under a new ID, title and citations.
- **rationale:**
  - **Conflicts with the design's own rule:** This undercuts "no metadata/parameter overrides on references".
  - **Enables the mislabel the design warns about:** An authored `annual_summary {variable: q, statistic: p95}` titled as a low-flow Q95 index would be valid. That is the non-exceedance/exceedance confusion that P2 and the decision section reserve for a separately commissioned scientific set.
  - **Identity is undefined:** The authored ID becomes the `metric` value written into the CSV bytes. But P4 excludes "display name/title" from numerical identity and "deduplicate[s] only identical numerical requests". The design doesn't say whether two authored IDs for the same calculation share one immutable result, or which ID labels it.
  - **Why this can't wait:** The behaviour belongs to schema_version 1 and the /4 identity contract.
- **suggested_fix:** Choose one of these:
  - **(a)** The smallest change: leave authored calculation entries out of schema v1 until a method whose parameter space goes beyond the registered definitions is commissioned. `{definition: …}` entries already resolve to registered methods, so the settled framing is still met.
  - **(b)** Reject authored entries whose resolved calculation equals a registered definition, and state that the authored ID is part of numerical identity.

### ext1-3 [minor]
- **section:** Pre-change oracle and C4 coverage; C3
- **finding:** The parity falsifier covers only the `default` preset. Each set gets its own plan and there is no cross-set cache, so the same definition is computed separately for each set that selects it. Nothing checks that `example_subset`'s `q_annual_mean` matches `default`'s byte for byte on the same responses. If ext1-2(b) is chosen, nothing checks that an authored entry matches its registered equivalent either.
- **rationale:** "Shared registered calculations / independent reuse" is the main promise for users, and the current C3 checks would not catch a difference between sets.
- **suggested_fix:** As an acceptance recommendation, add to C3/C4 a check that the rows two sets share are identical.

### ext1-4 [minor]
- **section:** Pre-change oracle and C4 coverage (O2); dictionary `block_assignment`
- **finding:** O2 names `YS-JAN`/`YS-OCT`, but production uses `YE-DEC`/`YE-SEP`, which are closed and labelled on the right.
- **rationale:** For daily data stamped at midnight the two split the days identically. They differ in bin labels and closure, though. A fixture or dictionary text written from the design's wording could describe, or test, a different rule from the one production runs.
- **suggested_fix:** Run the oracle by setting `climate.water_year_start` (Jan/Oct) so the production helper builds the anchor. Write `block_assignment` from the resolved anchor string.

### ext1-5 [minor]
- **section:** P2 (wet/dry semantics); dictionary
- **finding:** The reference month is chosen from pooled calendar-month **sums** (`metric_registry.py:281`). Sums aren't normalised for month length or record coverage, so 31-day months are favoured for "wettest" and February for "driest". February's sum is about 10% lower even when its daily flows are the same.
- **rationale:** The existing arithmetic is preserved, but "driest_month_mean" will be read as the month with the lowest flow rate. The design says "calendar-month sums" without spelling out this consequence.
- **suggested_fix:** State in the dictionary's temporal/validity cell that the month is chosen by total volume, not mean rate. Check this with the existing tie and monthly-sum fixture (O3).

### ext1-6 [minor]
- **section:** Planning, identity and publication (P4); Closed set schema and ownership (P2), registry placement
- **finding:**
  - **Identity coverage:** `implementation_revision` hashes three fixed modules: `metric_registry.py`, `metrics_definition.py` and `indicator_tables.py` (`metric_registry.py:147-150`). If the mapping from parameters to statistics (e.g. `p95`→`q95`) or its validation ends up in the new `indicator_sets.py`, editing that mapping won't change numerical identity, and stale results could be reused.
  - **Overloaded term:** "references" means three things: citations, the Class-C reference policy, and `{definition}` references. Line 257 keeps "references" in numerical identity while line 259 excludes citations.
- **rationale:** Both make the identity contract ambiguous for the implementer.
- **suggested_fix:** Require any module that affects numbers to be in the revision or code inventory, and add a C3 check that editing the mapping changes identity. Use three distinct terms.

## Supported conclusions

- **Operations and boundaries:** The operation and indicator-only boundary (P1), the closed set schema, the separation between registry and YAML authority, and the per-set publication, ownership and collision rules are coherent. They are specific enough to implement and consistent with the settled framing.
- **Default parity:** The parity plan can falsify default parity. It captures evidence before any edit and independently of the candidate code, compares bytes on float32-serialised outputs, captures legacy branches separately (O5), and gives model-validator acceptance authority. Its gaps are coverage of the non-default path (ext1-3) and the anchor wording (ext1-4), not the falsifier itself.
- **Units, read from the code:** `validate_requirement` enforces an 86400 s timestep, so summing daily `mm dt-1` values gives depth in mm. "mm" with "mean accumulated depth per water-year block (partial blocks included)" accurately describes the arithmetic. "mm/yr" is accurate only when every block is a full year. Under a January water year with the WF3 window that holds almost exactly, and under any other start it doesn't (ext1-1). Neither label repairs the N/(N+1) effect, so the label decision matters less than exposing block coverage.
- **Units, empirical validation:** This is still open and outside the design. It would mean checking the reported values on retained responses against total depth/N with the per-run block counts, plus the separate scientific unit decision at G2. The design is right that extreme-value and mean-flow effects have no unconditional direction; only the sums have a deterministic effect.
- **Missingness:** The descriptions of missing-data handling match the inspected code (`metric_registry.py`, `metrics_definition.py`, `response_series.py`).

## Inspection limits

- **Inspected:** The candidate, `metric_registry.py` (lines 1–620), `metrics_definition.py`, `indicator_tables.py` (constants), `snake_utils.water_year_end_anchor`, `forcing_window.py`, part of `downscale_climate_forcing.py`, `metric_plan.py` (lines 230–365), and a grep of `response_series.py`.
- **Not inspected:** `simulation_runner.py`, `metric_export.py`, `interchange_contracts.py`, the tests, or the import-closure behaviour of `repository_code_inventory`.
- **Not verified:** The file's SHA256, and whether the WF4 member window always equals the WF3 `forcing_window`. I also didn't check whether weathergen noleap forcing produces Gregorian-labelled responses without 29 February, which would affect the dictionary's `calendar` field.
- **No execution:** Nothing was run. The N/(N+1) result is analytic from the code and assumes no NaN.