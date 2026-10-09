# Caption geometry engineering evidence

Task: `t2610082103`. This packet records focused probes; it does not replace the coordinator's affected
render inventory. Scope is figure geometry only; scientific calculations and captions remain supplied by
the existing workflows. Numerical claims are unaffected.

## Source changes

- `blueearth_cst/plotting/fundamentals.py`: finalize drawn geometry at configured `savefig.dpi`, freeze axes
  and locator results, extend the canvas below the image, translate legend anchors and figure-coordinate
  artists, and wrap the caption by measured rendered width. Preserve `add_caption(fig, text) -> None` and
  restore the original figure DPI in `finally`.
- `blueearth_cst/climate_analysis/diagnostic_render.py`: remove the map's pre-caption canvas-width resize.
  Keep its existing tight export with 2 mm padding.

## Commands completed

Run from the session-1 worktree root:

```powershell
pixi run python .tmp/scratchpad/shared-rendering/caption-layout/engineering/probe.py
pixi run python .tmp/scratchpad/shared-rendering/caption-layout/engineering/realistic.py
pixi run ruff check blueearth_cst/plotting/fundamentals.py blueearth_cst/climate_analysis/diagnostic_render.py
pixi run ruff format --check blueearth_cst/plotting/fundamentals.py blueearth_cst/climate_analysis/diagnostic_render.py
```

The final invocations passed. The first touched lint invocation found a missing import-group blank line;
it was corrected before the passing invocation. The first retained driver invocation failed because its
scratch path packet omitted `compute.metadata`; the packet was corrected before the passing render.
No permanent tests, full suites, workflow executions, dependencies or Git actions were added here.

## Independent geometry discrimination

`probe.py` renders single axes, an outside figure legend with figure text, multiple axes with a colorbar,
and a fixed-aspect map with a colorbar. Each uses short and long captions with both the previous helper
and the final source helper. The previous map path includes its pre-caption width resize.

The reference is the ordinary figure drawn and exported at 600 DPI. Caption helper entry uses figure
DPI 100. Physical axes bounds are compared after drawing at 100 DPI and 600 DPI, then after captioned
export. The tolerance is 0.05 mm for axes shape/position and common translation of measured decorations.
The scalar shape metric is the maximum absolute change in x position, width or height; vertical
translation spread detects decorations that do not move together.

| Case | Previous maximum drift | Final maximum drift |
|---|---:|---:|
| Single axes, short / long | 0.748 / 5.987 mm | < 0.000001 mm |
| Outside legend/text, short / long | 0.748 / 5.987 mm | < 0.000001 mm |
| Multiple axes/colorbar, short / long | 0.748 / 5.987 mm | 0.007876 mm |
| Map, short / long | 71.731 / 72.298 mm | 0.007876 mm |

The previous helper fails the tolerance in all eight cases. Its outside legend/text translation spread
reaches 5.987 mm. Its map export grows from 1614 pixels wide to 1988 / 2045 pixels and the caption extends
outside the figure canvas. The final helper retains the 1614-pixel map width, has translation spread
below 0.000001 mm, no 600-DPI export-redraw drift, and no canvas-clipped captions in these eight cases.
The map drift scalar includes x displacement from the prior canvas shrink; it is not solely axis-size
growth. Detailed individual values and output dimensions are in `geometry.json`.

Additional controls pass for a no-axes figure and a 360-character unbreakable token, with configured
save DPI `"figure"` and 600. They check all token characters survive wrapping, the caption lies within
the drawn canvas, the return is `None`, and the original figure DPI 100 is restored.

## Retained-input examples

`realistic.py` reads CHIRPS retained inputs under:

`C:/Users/taner/workspace/cst-cases/runs/sp2-liberia/active/data/climate/historical/chirps_20000101_20161231`

It uses the existing WF0 renderer, source metadata, captions and artists for four ordinary/captioned
pairs: `series`, `coverage`, `spi`, and `map-precip`. The ERA5 sibling supplies the existing pooled map
scale. It does not execute a workflow or alter retained inputs.

All four cases pass geometry at 100-DPI drawing and 600-DPI drawing. Maximum measured shape or
decoration-translation drift is 1.31e-12 mm. Individual results are in `realistic/geometry.json`.
All four captioned PNGs were opened and visually inspected: captions are legible and left-aligned,
panels and colorbars remain intact, and no new overlap or clipping was seen.

## Limits

- Geometry is finalized for the configured save DPI. Further resizing or artist edits require a fresh
  ordinary figure; repeated captioning and later layout changes were not verified.
- The general geometry probe covers the listed artist shapes, not every Matplotlib artist or nested
  subfigure structure. Retained examples cover four WF0 forms; the coordinator owns the complete WF0,
  WF2 and optional-subbasin inventory and scientific-artist preservation checks.
- The `"figure"` and long-token controls check text preservation and canvas containment at draw time;
  their PNGs were generated but were not individually opened for visual inspection.
- PNG is the workflow caption format inspected here. PDF, SVG and other backend output were not tested.
- The DPI `finally` path was inspected in source; an injected rendering failure was not exercised.
- Existing source captions do not establish arbitrary Mathtext behavior when an oversized mathematical
  expression must be split. No such expression was observed in these focused retained examples.
- Full suites, baseline numerical gates and workflow executions were omitted deliberately because this
  bounded change concerns terminal figure composition. Broader renders remain coordinator-owned.
