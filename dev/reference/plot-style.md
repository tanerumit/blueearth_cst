# Scientific plot style and visual review

This shared reference records the agreed WF0, WF1 and WF2 styles and defaults for subsequent figure
revisions. Apply relevant defaults across plot types; preserve the explicit exceptions below. New visual
decisions belong here, alongside changes to the plotting code. A style decision does not authorize changing
the underlying calculation or statistical interpretation.

## Output paths

Use `plots/` for generated graphics throughout the toolbox. Keep readable captions in
`plots/figure_captions.md`. Machine plot manifests and internal analysis records belong in the cohesive
output unit's single root `_engine/`, following [the output naming rule](naming.md#generated-outputs-under-project_dir).
WF2 uses the ensemble root's `_engine/`, with manifest figure paths relative to `plots/`.
Existing WF0 `plots/_engine/` paths await explicit migration. JSON containing user-facing data stays with
its owning data product. Generated filenames and directories use lowercase snake_case, including
`full_period/` and `period_<start>_<end>/`. WF2 adopts the WF0 dataset/variable/context/spatial grammar,
with canonical `precip` and `temp` stems. See `migration_plot_paths.md` for the rename mapping.

## Typography, axes and layout

- Design WF2 figures for 4–5 scenarios and 10–20+ models, potentially with multiple members per model.
  Small retained examples do not establish that labels, legends or panels remain readable at that scale.
  Wrap panels instead of indefinitely shrinking them; adapt trace opacity to member density and retain
  clear summaries. Never silently omit models or scenarios to make a figure fit.
- Keep font sizes consistent in physical units across different canvas sizes. Current scientific figures
  use 7 pt axis and panel titles, and 6 pt ticks and annotations. Scale every element together in previews,
  including captions, legends and labels; do not enlarge a compact figure to fill its HTML card.
- Use modest white padding around compact figures and adjust the exported canvas dimensions to avoid
  excessive empty space. Square plotting areas mean equal physical axis lengths, not equal data scales.
- Every labeled axis tick has a visible tick mark. Annual series have a tick for each year; reduce labeled
  year density on long records to avoid crowding. Retain annual minor ticks where appropriate.
- Anchor major and minor year ticks to the same calendar-year grid; do not distribute ticks from the
  record's first year or place them at inconsistent intervals near labels. Reviewed long WF2 records use
  20-year major ticks and 5-year minor ticks. Compare equivalent panels on shared limits and tick positions.
- Use units alone for axis titles unless a figure-specific exception needs the variable name.
- Exception: WF2 reference-relative axes retain `Relative to [reference-period] (symbol)`, for example
  `Relative to 1985–2014 (°C)` or `Relative to 1985–2014 (%)`. Use the actual analysis reference period;
  absolute-value axes still show units alone.
- Use `Precip.`, `Temp.` and `PET` when abbreviated variable names are needed. Display `CHIRPS` in legends
  and plot labels; retain version metadata in source records where relevant.
- Keep grid lines subtle and partly transparent. Avoid competing with the data or annotations.
- Always label multiple plotting panels `a)`, `b)`, etc.; explain panel contents in the caption.
- Do not display figure titles inside or above the plotting area. Identify the variable, spatial
  support and plot type in the caption and review-page heading. Preserve explicitly agreed panel labels.

## Legends, labels and points

- Default to a vertically stacked legend inside the upper-left or upper-right corner. Choose the corner
  with less underlying data and retain flexibility to move it for other input records.
- Use a white legend background with alpha 0.88 and no visible border. Use the same background for
  in-plot labels: white, alpha 0.88, no edge, padding 1.2.
- For the reviewed trend-interval, SPI fit, trend-sensitivity and monthly-coverage figures, place the
  stacked legend outside the panels on the right, with its top aligned to the panels' top border.
  Reduce panel widths as needed while retaining the intended overall canvas width.
- Place slope annotations far enough from their trend lines to avoid overlap. Position point labels to
  avoid overlaps with other labels and underlying map features; use the standard label background.
- Use contrasting point colors over map layers. For scatter plots, use partly transparent fills and
  darker outlines so points remain visible. The reviewed enlarged scatter points use area 36 pt²,
  alpha 0.7 and an approximately 0.7 pt dark edge; adapt where the plot density requires it.
- Keep dataset colors consistent: CHIRPS orange `#bf6a3c`, ERA5 blue `#236b8e`.

## Color scales and colorbars

- For independent color scales, use the full light-to-dark palette range, including its darkest or
  lightest endpoint at the high end. Keep comparable limits when plots share a scale.
- Use perceptually clear gradients that preserve visibility of intermediate values. For dataset-specific
  heatmaps, use the dataset hue with light-to-dark intensity encoding the displayed quantity.
- Use rectangular colorbar extension ends and consistent title spacing (current title pad: 10 pt).
- Do not force a zero midpoint tick into the reviewed anomaly colorbars; retain their approved ticks.
  This supersedes the earlier request to always label zero in anomaly plots.
- Remove missing/unavailable legend rows from anomaly plots and explain missing-value handling in captions.
- The reviewed SPI heatmaps use boundaries `-3, -2, -1, 1, 2, 3`, without a zero tick, and a colorbar
  height of 80% of the plotting area. Their final figure height is 56% of the original height.

## Figure-specific decisions

WF1 forcing QA uses the reviewed WF0 map, annual-series and monthly-climatology styles for precipitation,
temperature and PET. Read the actual model-grid forcing, mask to the model basin, and use equal-weight
cell means for temporal figures. Keep the nine `forcing_<variable>_<kind>.png` filenames for now.
Identify the data as Wflow forcing in legends and captions; use ERA5 blue for this forcing family.
Maps retain their model-grid footprint and basin mask, with the reviewed coordinate labels, palettes,
spatial overlays and gauge labels. Source and forcing maps retain independent color limits; identical
colors alone do not establish equal values.
Suppress individual model-cell outlines on the fine forcing grid so they do not obscure the field.
Show cells outside the model basin in white and unavailable summaries inside it in gray.

Use WF0's start-year reporting labels, completeness handling, Sen trends and monthly mean with a
10–90th percentile band. WF1 uses WF0's default tolerances of three missing days per month and fifteen
per reporting year, independently of whether WF0 runs. Temperature uses means; precipitation and PET
use totals. Keep model corrections and statistical caveats in separate captions, without plot footers.
These summaries describe forcing QA; they do not modify the forcing or simulation calculations.

WF1 station hydrographs retain the five-panel layout: daily discharge, annual means, seasonal cycle,
and linear/log flow-duration curves. Apply the common typography, frames, soft horizontal grids,
short panel titles and inside legend. Observations remain blue and dashed; simulation remains
vermillion and solid. Use discharge units alone on vertical axes, three-letter months and percentage
exceedance labels. Annual labels start at the preceding five-year grid mark (ten years for records
longer than 35 years), retaining annual minor ticks so the left edge has a nearby calendar label.
Station identity, dates, support and methods
belong in separate station captions, bounded by the plotting area's left and right edges in previews.

Annual means require full calendar-year bounds, at most three missing days in each month and fifteen
in total. Seasonal cycles average eligible monthly means equally across years; full calendar months
allow at most three missing days. Reindex to daily dates so absent timestamps count as missing.
Use finite, nonnegative discharge without infilling. With observations, summary panels use paired
valid dates; the daily panel retains the available series for context. Flow-duration ranks use only
valid values and positions `rank / (n + 1)`. Retain zeros on the linear panel, omit them from the log
axis without changing exceedance positions, and report their frequency. The log range includes all
positive values from both series, without percentile clipping. These choices affect hydrograph
summaries only; performance metrics and other evaluation sheets retain their own methods.

WF1 performance sheets use the same finite, nonnegative paired daily support for the scatter, sample
count, cumulative volumes and exported metrics. Align dates before pairing and retain gaps in the
cumulative curves. These volumes integrate paired days only and do not estimate missing-day flow.
Monthly metrics compare means over the same paired days within each month; hydrograph calendar
completeness thresholds do not gate metric rows. Undefined scores remain unavailable.
Keep squared Pearson correlation and sample counts in JSON metadata, without displaying them on the
performance plot. Label the scatter `a)` and cumulative volume `b)`, with the stacked observed/simulated
line legend inside the upper-left of the scatter, below its panel label. Keep table values identical to
`performance_metrics.csv`. Use common typography, soft frames/grids and a concise publication caption
that explains each labelled panel, without displayed titles or figure footers.

WF1 hydrological output figures default to two single-axis products per variable: a basin-average
annual series and seasonal cycle. Optional subbasin figures repeat both products individually, never
as panels. These figures have no displayed titles. Reconstruct the basin's native grid-cell mean from
daily zonal means using fixed cell-count
weights; missing zones invalidate that basin day rather than changing its spatial support.

Apply the same first-year warm-up exclusion and calendar completeness rules to all hydrological
variables. Eligible months allow three missing days; eligible years have full calendar bounds, all
months eligible and at most fifteen missing days. Flux amounts use monthly/annual totals, with eligible
missing days filled by that month's available-day mean. Rates and stored quantities use means without
infilling. Keep physically valid negative recharge. Seasonal cycles show equal-year monthly means and
10–90th percentile bands, describing interannual variability rather than uncertainty in the mean.
Annual series use Sen slopes per decade and the shared WF0 trend treatment. Snow plots represent the
native snowpack liquid-water depth, a stored quantity in mm, rather than an accumulated flux.
Captions use concise publication prose: quantity, support, period and visual encodings. Keep numerical
support counts, completeness thresholds and exclusion lists in the machine-readable methods metadata.

| Figure type | Agreed treatment |
|---|---|
| Historical climate maps | Extent exactly matches the native gridded layer's outer cell edges. |
| Wflow forcing maps | Use the selected historical grid's exact frame, with no added padding. |
| Map coordinates | Axis titles include degrees; tick labels are numeric, signed, without N/S/E/W. |
| Annual series | Trend line and slope annotation on every applicable series; y-axis shows units only. |
| WF2 annual overview | No legend; explain member traces, medians and ranges in the caption. |
| WF2 trajectories | Model median and range; distinct historical trace; stacked inside scenario legend. |
| WF2 change strips | Retain the newer original scenario legend, unlabeled x-axis, box and point styling. |
| WF2 seasonal cycle | Separate median climatology lines from monthly-change boxes; shade historical range only. |
| Monthly climatology | Stacked inside legend in the less crowded upper corner. |
| Cumulative timing | Bottom month axis; no top-axis title; y-axis `Cumulative (%)`, numeric ticks. |
| Timing boxes | Enlarged unfilled horizontal boxes, thin outlines, no mean dot. |
| Drought events | Dataset colors identify sources; legend distinguishes `Complete` and `Truncated`. |
| Truncated events | Dense diagonal hatching with thin hatch strokes, rather than dashed outlines. |
| Spell exceedance | Square plotting area; y-axis `Exceedance Pr. (log)`; compact padded canvas. |
| Autocorrelation | Dark point edges and approximately 95% confidence limits; qualify these in caption. |
| Trend intervals | Thicker horizontal intervals and caps, closely spaced rows, no dataset row labels. |
| Seasonal P–T | Square panels; `Temperature anomaly (°C)` and `Precipitation anomaly (%)` axes. |
| SPI fit checks | Dataset-hued p-value heatmaps; minimal panel titles; no x-axis title `Month`. |
| Trend sensitivity | Separate slope points with confidence error bars for each eligible starting year. |
| Monthly coverage | Compact dataset rows of monthly cells; complete, gapped and unusable states. |

For WF2 change strips, tighten the gap between the horizontal scenario legend and panel titles, add short
caps to the full-range lines, and make median bars slightly thicker than the box outlines.

WF2 monthly-change figures wrap scenarios in two columns (2 × 2 for four SSPs), with shared y-limits,
horizontal month labels, reference-period axis titles, capped ranges, outline IQR boxes and thicker median
bars. Review climatology and monthly changes as separate groups in the HTML page.

Keep WF2 scenario summaries subordinate to the data: reviewed annual-overview median lines use 1.0 pt,
trajectory median lines 1.5 pt. Retain annual values without smoothing and preserve gaps in missing years.

WF2 interannual variability shows temperature SD, precipitation SD and precipitation CV in separate figures.
Use the reviewed change-strip box, point and horizontal legend style, with a reference line at ratio 1.
Show descriptive model spread; retain numerical sampling-benchmark products separately without displaying
them or significance fills in this figure.

The annual member-ratio comparison shows all three metrics together. Its boxes, medians and capped
ranges summarize model ratios after geometric averaging of members within each model, with equal model
weight. Faint points retain individual members; their density does not set the weight of the summary.
Captions distinguish descriptive model spread from confidence intervals and note member dependence.

WF2 change clouds retain square plotting areas and circular points for all scenarios, distinguished by
color, with darker edges and slight transparency. Stack the inset legend in the less occupied upper
corner. Use “Mean precipitation change (%)” and “Mean temperature change (°C)” as axis titles; state
reference and future periods in the caption, alongside paired-model aggregation and spread semantics.

WF2 sign-agreement matrices use temperature and precipitation percentage-change panels, four discrete
agreement classes with paired blue/red swatches, and visible scenario and period ticks. Cell signs show
the median direction and k/n shows model agreement; choose text color by fill luminance. Captions explain
that directional agreement is neither probability nor significance and note shared model ancestry.

WF2 ensemble coverage uses a compact table with consistent numeric member counts, a historical-reference
column, family and institution metadata, and pale alternating rows. Historical counts deduplicate loaded
reference series. Distinguish availability from analysis eligibility in captions, explain family
provenance and provisional/unknown assignments, and avoid implying family independence.

## Scientific interpretation and methodological review

- State what a plotted point represents: member, model, scenario summary or observation. Distinguish
  within-model member variation from between-model spread and preserve paired variables from the same
  model, scenario and analysis window.
- For equal-model summaries, reduce members within models first; additional members must not increase
  a model's weight. For variability ratios, retain the approved geometric member reduction. Individual
  member points can coexist with model-summary boxes when their different meanings are explicit.
- Ensemble ranges and IQR boxes are descriptive spread, not confidence intervals. Members of one model
  are dependent; shared model ancestry can also limit independence between models.
- Changes compare matched reference and future aggregations. Monthly changes use each month's own
  reference, rather than a single annual reference. A historical change box collapses to zero by
  construction; use the zero reference line, with absolute climatologies in a separate companion figure.
- Use SD for temperature variability; Celsius CV depends on an arbitrary zero. For precipitation, SD
  expresses absolute variability and CV relative variability; label their aggregation and dry-mean
  exclusions. Do not imply SD/CV/mean ratio identities when they use different underlying series.

The retained calculations use detrended period mean rates for precipitation SD and detrended period totals
divided by their original mean for CV; keep this distinction explicit when comparing them. Unifying their
aggregation would be a separate numerical-method change, not a styling decision.

For drought events, reserve colored dot legend symbols for datasets; use a line for complete events and
a hatched sample for truncated events. The final reviewed hatch is eight diagonal strokes in Matplotlib's
hatch string, with hatch linewidth 0.5 pt. Timing boxes are 0.12 high in cumulative-fraction coordinates,
with approximately 0.6 pt outlines and whiskers.

Autocorrelation limits currently use the pointwise approximation ±1.96 / sqrt(pairs at lag). Label them
as 95% confidence limits and state the approximation and its limitations in the caption. Bartlett or
other serial-correlation-aware limits require a separate methodological decision; they were not adopted
in this visual review.

## Captions

- Store each figure's caption in its relevant figure-caption Markdown file, alongside the figure products.
- Write captions for publication or reports: describe variables, encoding, statistical meaning, source
  support, missing values and material caveats. Do not describe internal rules, review logic or gates.
- Move footer information from the plot into its caption. Keep captions left-aligned to the plotting
  area, slightly smaller than axis text, in gray.
- Include captions inside the preview canvas when enabled. Add space below the image without resizing
  the plotting area or changing its proportions. Keep caption-to-axis font proportions consistent.
- `plotting.fundamentals.add_caption(fig, text)` finalizes an already drawn figure for its captioned
  export. Set `savefig.dpi` to the intended export resolution first. It freezes the drawn axes and
  decorations, adds a measured bottom band, and restores the original figure DPI. Do not resume layout
  or resize the figure after this step. Caption wording and metadata remain workflow-owned.
- Wrap embedded captions to the span of the drawn axes, using measured text width and the existing
  note font. Keep 3 mm below the caption and 3 mm between its top and the original canvas bottom.
  Tight-cropped maps retain their original geometry and 2 mm export border; do not resize the map
  canvas to make room for a caption.

## Interactive review process

- Begin each new plot-group review with scientific, methodological and publication-readability
  suggestions before applying changes. Distinguish visual revisions from changes to calculations.
- Confirm the authoritative baseline and its data provenance before revising. Use the newer WF2 lab
  outputs and retained tables for this session; older production renders can carry superseded styles.
- Start from the tracked `dev/reference/figure-comparison.html` template. See
  `dev/reference/figure-comparison.md` for setup and figure-record fields. Keep session data in scratch;
  update the tracked template when improvements to the review interface are approved.
- Keep the disposable HTML review under the worktree's `.tmp/scratchpad/`; it is not durable storage.
- Show only the plot group currently under review, with existing and revised versions side by side.
  Preserve a baseline before revising the group.
- Keep the original page header. Put the selected figure name in each comparison heading, for example
  `CHIRPS – Spell (existing)` and `CHIRPS – Spell (revised)`.
- Put selectors, buttons, sliders and checkboxes on the second row. Remove descriptive header prose and
  repeated figure-name text beneath the plots.
- Include caption and canvas-boundary toggles, plus the overlay comparison control. Preserve consistent
  physical image scaling so fonts do not grow when the canvas gets smaller and both figures fit together.
- Use the explicit side-by-side/wipe modes and linked zoom/pan controls. Unequal canvases require opting
  into top-left-aligned wipe; pad at a common scale without stretching either image. The overview uses
  the pair's declared export dpi (600 by default); both images must use that dpi.
- Below the figures, display `Path:` followed on a new line by the original figure's parent directory.
  Keep the full selected file path in the page data so the source remains identifiable. Compact keyboard
  hints and collapsible control help may follow the path.
- Render from retained inputs and inspect the actual exported figures. Apply reusable decisions to other
  applicable plots, and render all affected callers when a shared figure helper changes.
- Keep figure-specific tests and plotting-only probes temporary under `.tmp/scratchpad/`, outside the
  persistent test suite. Verify figure changes by rendering and visual inspection. Retain tests for
  exported numerical metrics and workflow contracts separately from figure review checks.
- During an explicitly deferred-check visual session, do not run tests or gates at each revision. Run
  appropriate checks at the end of the session. Commit once the user approves a figure style/type, rather
  than after each incremental revision. Do not land or push without separate authorization.

## Implementation entry points

- Shared drawing fundamentals and reviewed CST preset: `blueearth_cst/plotting/fundamentals.py`.
- Prepared annual lines, trend segments and monthly bands: `blueearth_cst/plotting/prepared_charts.py`.
- Explicit-figure export without workflow logging: `blueearth_cst/plotting/export.py`.
- Workflow bundles and current-figure compatibility: `blueearth_cst/shared/snake_utils.py::save_figure`.
- WF0 artists and compatibility aliases: `blueearth_cst/climate_analysis/diagnostic_figures.py`.
- Legacy cartographic/evaluation preset and runtime overrides: `blueearth_cst/shared/plot_style.py`.
- WF0 maps: `blueearth_cst/climate_analysis/diagnostic_maps.py`.
- WF0 rendering and captions: `diagnostic_render.py` and `diagnostic_captions.py` in the same package.
- WF2 artists: `blueearth_cst/projections/projection_suite_figures.py`.

For export without workflow logging, pass the figure explicitly and retain the caller's save options:

```python
from blueearth_cst.plotting.export import export_figure

export_figure(fig, "plots/precip_annual_ts.png", dpi=600, metadata={"Software": None})
```

The caller closes the figure after its final export. Existing workflow callers keep using `save_figure`.

### Prepared annual and monthly charts

`prepared_charts.annual_series` and `monthly_cycle` draw supplied arrays and return a `Figure`.
Use `draw_annual_lines` and `draw_annual_trends` on an existing axis when a composition needs its own
ticks or legend, as WF1 hydrological summaries do. Call within the existing `rc_context(STYLE)` and
keep that context active through export. The module does not select a backend or install global styles.

Adapters own aggregation, completeness, source order, units, reporting-year alignment and fitted trends.
`AnnualLine` contains values aligned to the supplied years. `TrendSegment` contains already evaluated
endpoints and the formatted label; drawing never fits a trend. `MonthlyBand` contains the mean and
lower/upper arrays in the supplied twelve-month label order. Pass the band's statistical meaning through
`band_label`; the current adapters use `10–90th percentile` for interannual spread. Drawing neither
calculates quantiles nor rotates months. Missing values retain gaps; inputs are not mutated.

WF0 keeps its compatible `View` wrappers. WF1 forcing and basin/subbasin summaries prepare the small
records directly. Existing captions, export options, filenames and scientific calculations remain with
their workflow adapters. These are internal reusable interfaces; external distribution is a later step.

WF2 review uses the newer artists and retained tables in the `wf0-lab` ensemble outputs as its visual
baseline. The annual overview, trajectories, change strips, split seasonal products, variability ratios,
member-ratio comparison, change cloud, sign agreement and coverage table have been reviewed and their
approved styles implemented in the toolbox. Trajectories use the prepared model median, not the model mean.
Keep baseline selection separate from validation of the current toolbox. Final integration evidence lives
in [`../records/reviews/plot-improvements/verification.md`](../records/reviews/plot-improvements/verification.md).
