---
title: "WF2 — Analyze projections"
format: html
---

`analyze_projections.smk` reduces CMIP6 projections to basin monthly temperature and precipitation change
factors. These factors position the stress-test grid against projection space; they do not determine WF3
perturbations.

Console summaries report resolved/requested ensemble coverage and available/skipped results. Skipped
windows retain their source, dates, reason, and report location so coverage gaps can be investigated.

The run settings list the reference period, future periods, emissions scenarios, climate models, and
water-year start. These are the requested projection-analysis settings; the coverage summaries report
which combinations were available.

## Rules

| Rule | Operation |
|---|---|
| `all` (target) | Collect change factors, plots, and records. |
| 2.01 `delineate_region` | Define the shared basin region. |
| 2.02 `delineate_subbasins_and_rivers` | Build shared vectors. |
| 2.03 `fetch_cmip6_projections` | Fetch raw slices for configured model, scenario, member, and variable keys. |
| 2.04 `reduce_to_basin_averages` | Reduce each local slice to a monthly basin series. |
| 2.05 `derive_change_factors` | Compare future and reference windows and write tables and report. |
| 2.05b `prepare_projection_analysis` | Compute analysis-window diagnostic tables and availability. |
| 2.06 `plot_climate_projections` | Render projection figures. |
| 2.07 `gather_benchmarks` | Merge benchmark parts. |
| 2.08 `gather_logs` | Merge log parts. |

The `all` target collects these products. Rule 2.03 is the remote data read; subsequent reduction uses the
acquired slices.

## Rule flow

Fetching fans out by configured model, scenario, member, and variable before monthly reduction.

## Configuration

The project file supplies `project.catalog`, `basin.region`, and `basin.resolution`. Its
`workflows.analyze_projections` stanza enables the workflow and points to its YAML file through `config_path`.

The workflow file, `test_case/project_config_rapid_analyze_projections.yml`, sets `catalog` (the CMIP6
catalog), `ensemble` (output namespace), `models` and `scenarios` (the ensemble subset), `members.preference`
(member selection order), and `variables` (source mapping, canonical rate or state, units, and relative or
absolute change). `reference_window` supplies historical years; each `future_windows` entry supplies years and
an output `name`. The template at `config/templates/example-basin/project_config_analyze_projections.yml` also
documents optional `members.selection`, `members.overrides`, and `stats`.

```yaml
catalog: toolbox:config/catalogs/cmip6_data.yml
ensemble: cmip6
models: [NOAA-GFDL/GFDL-ESM4, INM/INM-CM4-8]
scenarios: [ssp245]
members: {preference: [r1i1p1f1]}
variables:
  precip: {source: precip, canonical: rate, units: mm/day, change: relative}
  temp: {source: temp, canonical: state, units: degC, change: absolute}
reference_window: {start: 2000, end: 2014}
future_windows:
  - {start: 2046, end: 2054, name: mid}
```

## Inputs

Inputs are the basin polygon, cataloged CMIP6 data, and the selected model/scenario/member/variable
combinations. The reference and future windows define the compared periods. WF2 does not read a scenario
collection or model responses.

WF2 excludes CMIP6 `THU/CIESM` completely, across all variables, experiments and members, because its
published precipitation has an invalid scale. Excluding the whole model keeps the ensemble consistent
across variables; it does not establish a defect in temperature. Requested CIESM combinations remain in
coverage and composition records as `source_quality_excluded`, with the reason and counts, but create no
acquisition jobs and contribute to no analysis or change-factor products. Member overrides cannot restore
the model. Existing source caches are preserved; rerunning WF2 rebuilds affected derived products using
the reduced ensemble. No speculative rescaling is applied. See
[Monerie (2026), section 4](https://doi.org/10.1088/2515-7620/ae661c) for independent evidence of the
precipitation problem. A request containing only excluded models fails with no resolved combinations.

The GCM `reference_window` is independent of the ERA5 or other observed `climate.window`; the periods
need not match and WF2 does not compare them. Calendar years are inclusive: 1985–2004 is 20 years.
If a reference or horizon has no overlap or no complete water year, WF2 warns and continues with usable
combinations. It never substitutes the observed climate record or changes the requested horizon.
`summary/provenance.json` and `report.md` list unavailable model/scenario/member/horizon combinations,
requested windows, available dates, and reasons. `summary/composition.csv` distinguishes fully derived,
partially derived, and unavailable combinations. If none are usable, change-factor CSVs contain headers
only and the report states that no factors could be derived. Corrupt inputs and identity or calendar
mismatches remain errors. The independent analysis tables also retain explicit unavailable rows.

Annual and monthly change-factor merges remove the source-only `height` coordinate, which can differ
between models. Factor values and model/scenario/member identities are preserved; other coordinate
conflicts remain errors.

## Outputs

WF2 retains the acquired slices and basin monthly series, a change-factor product by model, scenario, and
horizon, projection figures, and merged logs and benchmarks. Interpret these as plausibility context alongside
the response surface, not as forcing for its simulations.

Launcher runs record per-file production attribution. See
[execution and provenance](execution-and-provenance.md#wf2-product-attribution) for its exact semantics,
and [results transfer](results-transfer.md) for portable export/import, checks and limits.

The `analysis/` tables use the configured `reference_window` and `future_windows`, retaining complete water
years inside their calendar bounds. January 2041–2060 uses all 20 years; an October start uses WY 2041–2059
(October 2041–September 2060). Windows are never recentered, extended or replaced by a reference fallback.
Bounds outside CMIP6 acquisition coverage, or without a complete water year, are rejected.
The `_engine/analysis_record.json` records configured bounds, effective dates/counts, eligibility, reductions
and product availability. Seasonal precipitation changes use weighted mean rates; this differs from the lab's
total-based percentages. Precipitation CV uses period integrals. Analysis arithmetic uses float64 inputs;
the aligned change-factor arithmetic retains its existing precision and dry-reference rule.

Seasonal diagnostics require at least 90% of each owned window's water-year count, rounded up,
with a minimum of three complete seasons. Reference and future thresholds are separate: 30- and 20-year
windows require 27 and 18 observations respectively. Each season still needs three finite months inside
its window; partial boundary seasons are excluded. Missing months never reduce the thresholds.
The analysis record retains both thresholds per window. Insufficient coverage remains explicit as
`insufficient_observations`, including in variability diagnostics.
`methods.season_min_years` maps each window ID to its `reference`/`future` thresholds.

Rule 2.06 reads only the analysis tables and record. Figures live in `plots/full_period/` and one
`plots/period_<start>_<end>/` folder per distinct analysis window. Availability determines the PNGs:
coverage, annual member overviews and anomaly trajectories, annual/seasonal change and variability
strips, monthly cycles, sign agreement and change-factor clouds. A combined cloud is written only when
at least two distinct windows have paired changes. Missing products carry reasons rather than blank PNGs.

`plots/figure_captions.md` describes every produced figure and lists unavailable and retired products;
`_engine/figure_captions.json` maps ordinary PNG paths to captions and counts. Set
`plotting.annotation: caption` or `title` in the project YAML to annotate those PNGs in place.
The default `none` leaves them unannotated. Spread describes the ensemble, not a confidence interval; sign
counts are diagnostic agreement, not likelihood.

Executable owners: `analyze_projections.smk`, `projections/derive_change_factors.py`,
`projections/prepare_projection_analysis.py`, `projections/projection_figures.py` and
`shared/product_record.py`. The annotated projection starter owns the complete member/statistic options.
