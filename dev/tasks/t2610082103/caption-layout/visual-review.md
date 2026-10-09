# Caption/layout visual review

Result: **PASS for the six inspected PNG pairs.** No actionable regression attributable to the bounded
caption correction was visible. Reviewed on 2026-10-10 for t2610082103; no source edits, new renders,
tests, Git operations or nested delegation were performed.

## Contract and method

Audience: readers of CST scientific figures in reports and publication previews. Review question:
does embedding the supplied caption preserve the original visual comparison while keeping the caption,
labels, legends and colorbars readable and unclipped?

Applied the Python plotting skill's saved-artifact/layout inspection guidance, the data-visualization
skill's caption/readability principles, and `dev/reference/plot-style.md` Captions. The existing chart
forms, palettes, supplied prose and scientific values were outside this corrective review.

Opened all twelve saved PNGs using `view_image`. Both variants use the declared 600 dpi. Tool previews
fit unequal canvases independently; apparent preview shrinkage is not evidence of physical axes
shrinkage. Visual inspection evaluates relative geometry, content preservation and clipping; physical
preservation relies additionally on the engineer's recorded geometry measurements. Read the real WF0
`engineering/realistic/geometry.json`: maximum recorded shape drift is 1.3074e-12 mm. The coordinator
supplied synthetic maximum drift 0.00788 mm against the declared 0.05 mm tolerance; this reviewer did
not rerun that measurement.

## Inspected pairs

Paths below resolve from `.tmp/scratchpad/shared-rendering/caption-layout/engineering/`.

1. `realistic/series.png` and `realistic/captioned/series.png`: actual WF0 single-axis annual series.
   Trend annotation, year ticks, units, markers and line geometry remain readable. Caption has two clean
   lines, aligns with the plot's left edge, and clears the year labels with visible bottom padding.
2. `realistic/coverage.png` and `realistic/captioned/coverage.png`: actual WF0 compact coverage row with
   outside legend. All three legend entries remain visible; caption wraps beneath the plotting area
   rather than extending beneath the right legend. Six lines are readable with clear interline spacing.
3. `realistic/spi.png` and `realistic/captioned/spi.png`: actual WF0 stacked SPI rows and discrete
   colorbar. Row labels, colorbar heading/ticks and year ticks remain intact. Three-line caption is clean,
   with no collision against the plot or colorbar. The final text line has visible canvas clearance.
4. `realistic/map-precip.png` and `realistic/captioned/map-precip.png`: actual WF0 fixed-aspect map with
   colorbar. Cell proportions, coordinate frame and colorbar relationship are preserved visually. Axis
   units and precipitation title are complete. Four-line caption clears the longitude title and wraps
   without touching the right border. No map width reduction is inferred from fit-to-preview scaling.
5. `outside-long-candidate-ordinary.png` and `outside-long-candidate.png`: synthetic outside legend and
   figure-level annotation with long caption. Both top decorations remain visible and keep their
   relationship to the plot. Eight caption lines wrap cleanly, with clear separation from the x-axis
   title and visible bottom clearance.
6. `multiaxis-long-candidate-ordinary.png` and `multiaxis-long-candidate.png`: synthetic two-panel figure,
   fixed-aspect heatmap and extended colorbar. Both panels keep their proportions and alignment; all
   axis titles/ticks and colorbar extensions remain intact. Long caption spans the drawn axes and wraps
   cleanly into eight lines without covering either panel or the colorbar.

Caption text is gray, left-aligned and subordinate to axis titles throughout. Caption fonts do not
visibly change relative to tick labels between cases. The added band creates usable caption clearance;
no clipping, overlap, broken glyphs, unexpectedly split words or blank caption lines were observed.

## Inherited observations and limitations

The compact coverage figure naturally devotes substantial height to its long supplied caption; its
text length and scientific thresholds were not changed by this correction. Synthetic captions repeat
prose and describe shading absent from the synthetic line chart: these are deliberate layout fixtures,
not publication caption recommendations or helper regressions. The synthetic outside-legend figure's
large top gap already exists in the ordinary export. No redesign is requested for these observations.

This is bounded representative review, not acceptance of every affected product. No separate retained
WF2 or optional-subbasin image was opened because the six-pair allocation was exhausted; the coordinator
owns their full affected-product inspection. PNG only was inspected. No PDF/SVG acceptance, independent
exact 3 mm gap measurement, printed final-size readability, palette/CVD assessment, scientific numerical
validation or caption-wording audit is claimed. Display previews alone cannot establish submillimetre
geometry preservation. Effective runtime model settings and token costs were not reported.
