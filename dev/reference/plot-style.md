# Scientific plot style and visual review

This reference records the agreed WF0 styles and the defaults to carry into WF2 and subsequent figure
revisions. Apply relevant defaults across plot types; preserve the explicit exceptions below. New visual
decisions belong here, alongside changes to the plotting code. A style decision does not authorize changing
the underlying calculation or statistical interpretation.

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
- Use units alone for axis titles unless a figure-specific exception needs the variable name.
- Use `Precip.`, `Temp.` and `PET` when abbreviated variable names are needed. Display `CHIRPS` in legends
  and plot labels; retain version metadata in source records where relevant.
- Keep grid lines subtle and partly transparent. Avoid competing with the data or annotations.
- Use short panel titles prefixed `a)`, `b)`, etc.; explain methodological details in the caption.
- Align panel labels and titles with the plotting pane's left border in all multi-panel figures.
  For labels above a Matplotlib pane, use axes-relative x = 0 and left horizontal alignment.

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

| Figure type | Agreed treatment |
|---|---|
| Climate maps | Extent exactly matches the gridded layer; no surrounding blank map area. |
| Map coordinates | Axis titles include degrees; tick labels are numeric, signed, without N/S/E/W. |
| Annual series | Trend line and slope annotation on every applicable series; y-axis shows units only. |
| WF2 annual overview | No legend; explain member traces, medians and ranges in the caption. |
| WF2 trajectories | Model median and range; distinct historical trace; stacked inside scenario legend. |
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

## Interactive review process

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
- Below the figures, display only `Path:` followed on a new line by the original figure's parent directory.
  Keep the full selected file path in the page data so the source remains identifiable.
- Render from retained inputs and inspect the actual exported figures. Apply reusable decisions to other
  applicable plots, and render all affected callers when a shared figure helper changes.
- During an explicitly deferred-check visual session, do not run tests or gates at each revision. Run
  appropriate checks at the end of the session. Commit once the user approves a figure style/type, rather
  than after each incremental revision. Do not land or push without separate authorization.

## Implementation entry points

- WF0 artists and shared styles: `blueearth_cst/climate_analysis/diagnostic_figures.py`.
- WF0 maps: `blueearth_cst/climate_analysis/diagnostic_maps.py`.
- WF0 rendering and captions: `diagnostic_render.py` and `diagnostic_captions.py` in the same package.
- WF2 artists: `blueearth_cst/projections/projection_suite_figures.py`.

WF2 review uses the newer artists and retained tables in the `wf0-lab` ensemble outputs as its visual
baseline. Annual overviews and trajectories have been reviewed; inspect other forms before assuming that
every default is already implemented there. Trajectories use the prepared model median, not the model mean.
