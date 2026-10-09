# Caption/layout correction completed

Task t2610082103, 2026-10-10. Source commit:
`4d19a377e733fc5056c480981771889736841ae0`, branch `refactor/t2610082103-shared-plotting`.
Base: `480f9be58d948940e0d8db00f82e130e3fc22f8d`. No merge or push.

## Result and contract

The shared caption helper now implements the existing plotting-area preservation rule. It finalizes
drawn panels, locators and decorations at the configured export DPI, extends the canvas below them,
and wraps supplied caption text using measured width. It restores the original figure DPI and retains
the existing `add_caption(fig, text)` signature and None return. The current call sites already save
the ordinary product first and close the figure after its captioned export.

WF0 maps no longer resize their canvas before captioning. Their existing tight crop and 2 mm border
remain. Caption alignment, wrapping and total canvas height intentionally improve; data, fonts,
scientific text, filenames, optional-product settings and ordinary exports are preserved.

Source changes are confined to `plotting/fundamentals.py` and
`climate_analysis/diagnostic_render.py`. The plotting reference documents finalization, matching export
DPI and spacing. The delegation diagnostics record was added separately under `dev/reference/`.
No files were deleted. The replaced character-count wrapping and map-width resize were removed.

This was a bounded correction of an agreed rule, not a new layout architecture. The existing lifecycle
already ends with the captioned save. A new figure must be built for subsequent resizing or layout edits;
the helper is not a general interactive layout manager. PNG/Agg is the validated delivery contract.

## Evidence and verification

The [brief](brief.md) was saved before source editing. A planning-only frontier agent allocated two
execution roles: Python engineering and visual review. The coordinator reviewed the diff and integrated
the complete render evidence. Requested models, limits and observability are recorded in the brief and
the branch's `dev/reference/agent-routing-diagnostics.md`. Effective settings and token costs are unknown.

- [Engineering evidence](engineering-evidence.md) discriminates the old failure from the correction.
  Old single-axis short/long captions grew axes by approximately 0.748/5.987 mm. The synthetic candidate
  maximum was 0.00788 mm, below the declared 0.05 mm tolerance. Controls cover the 100-to-600 DPI path,
  `savefig.dpi="figure"`, no axes, long tokens, None return and DPI restoration.
- Full retained-input rendering produced 158 PNGs: 58 WF0 ordinary/caption pairs, 18 WF2 pairs and
  three optional-subbasin pairs. All three render commands passed. This covers every direct caller.
- [Verification summary](verification.json): all 79 caption variants preserve axes/decorations, with
  maximum shape drift 0.004075 mm and translation spread 0.004157 mm at saved 600-DPI geometry.
  No measured caption clipping. Plotted line arrays, collection arrays/offsets, limits and ticks match
  each ordinary figure. All 79 ordinary PNG dimensions and all 158 DPI values match the frozen baseline.
- Twelve caption, manifest, record and input artifacts match. All 60 WF0 retained input hashes match;
  WF2 input identity matches its prior record. Subbasin input fixtures are explicitly identified.
  [Source/environment identity](identity.json) records Python 3.12.13, Matplotlib 3.11.0, Windows Pixi,
  source hashes and lock identity. Each rendering driver explicitly selected Agg; the separately
  queried default backend was QtAgg. Source hashes still matched after the commit.
- [Independent visual review](visual-review.md) passed six representative ordinary/caption pairs.
  The coordinator inspected all 79 old/new caption pairs on ten sheets at matching physical scale,
  plus full optional-subbasin annual-series and WF2 eight-panel annual-overview PNGs. No new clipping,
  missing decorations or layout regression was visible at those inspection scales.
- Touched-file Ruff check/format passed. Final `pixi run lint` and `pixi run format-check` passed once
  on the final executable source; 438 files were already formatted. Whitespace checks passed.

Validation scope was rapid, scientific numbers unaffected. No pytest/full suite, all-five workflow
execution or numerical-baseline gate was run: repository figure-only policy prescribes affected
renders and temporary geometry probes. Scientific calculations, rules and configuration did not change.

## Commands and artifact roots

Commands below ran from session-1; each rendering command writes only its own scratch output family.

```powershell
pixi run python .tmp/scratchpad/shared-rendering/caption-layout/engineering/probe.py
pixi run python .tmp/scratchpad/shared-rendering/caption-layout/engineering/realistic.py
pixi run python .tmp/scratchpad/shared-rendering/caption-layout/render.py wf0
pixi run python .tmp/scratchpad/shared-rendering/caption-layout/render.py wf2
pixi run python .tmp/scratchpad/shared-rendering/caption-layout/render.py subbasins
pixi run python .tmp/scratchpad/shared-rendering/caption-layout/compare.py
pixi run python .tmp/scratchpad/shared-rendering/caption-layout/fingerprint.py
pixi run lint
pixi run format-check
```

Root `.tmp/scratchpad/shared-rendering/caption-layout/` retains candidate figures, three render logs,
save-time geometry JSON, comparison details, probes and lint logs. `comparison.html` links five scoped
review pages. `visual-sheets/sheet-01.jpg` through `sheet-10.jpg` contain all 79 caption comparisons.
Relative paths in the worker evidence resolve from this scratch root. Preserve it for t2610082103
review and later increments. The earlier foundations candidate and supplemental after tree are frozen
baselines; no historical outputs were overwritten.

The comparison harness initially used Windows default text decoding for Markdown and failed reading
a Unicode caption. Explicit UTF-8 fixed the harness. The comparison then passed without rerendering
figures or changing source. No implementation failure or source rework was hidden by that retry.

## Coverage limits and next increment

WF2 retained inputs have one future window: 18 products render and one multi-period product remains
unavailable, as before. Generic multipanel probes cover shared composition mechanics; no new retained
multi-period caption acceptance is claimed. WF0 unavailable-product placeholders are included.
WF1 direct-save figures, spatial exports, WF3/R and WF4 do not call this caption helper and were omitted.
PNG/Agg output was inspected; PDF/SVG captions, arbitrary backend canvases, nested subfigures and
oversized Mathtext tokens are not qualified. Do not infer universal Matplotlib support from this packet.

The initial shared rendering foundation now has style/geometry helpers, separate export mechanics and
a verified caption-finalization contract. Next is the prepared-input annual-series/monthly-cycle chart
interface shared by WF0 and WF1. Shared map references and external packaging remain later stages.
Existing long-record tick crowding, all-missing map interpretation and soil-clay title clipping remain
separate issues; this correction does not silently redesign them.
