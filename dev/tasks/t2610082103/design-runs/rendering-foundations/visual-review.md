# Coordinator visual acceptance

Date: 2026-10-10. Candidate: extraction over 07288e94, before source commit.
Scope: appearance preservation for the approved rendering foundations packet.

Inspected all 167 baseline/candidate pairs on 21 labeled contact sheets, covering every ordinary and
captioned WF0 product for CHIRPS, ERA5 and their comparison; nine WF1 forcing products; six WF1
evaluation/basin products; and 36 WF2 ordinary/captioned products. No visible before/after change in
layout, plotted marks, color, legend arrangement, clipping or caption wrapping was found at overview
scale. Contact sheets are a layout review, not a claim of word-by-word proofreading at full resolution.

Also opened full individual PNGs for the captioned CHIRPS precipitation map (both revisions), candidate
station-1010 hydrograph, and captioned WF2 annual/monthly sign-agreement matrix. Labels, units, legend,
panels and caption are readable; no new clipping or overlap was found. These observations accompany
the separate inventory, prepared-value, metadata and geometry probes; they do not replace them.

The broad historical reference frame around the small WF1 model basin is preserved. The optional WF0
spatial overlays were omitted in both retained-input captures. These are existing choices, not changes
introduced by this extraction. Caption-induced axes growth is separately recorded as an existing defect.

Review artifacts remain in `.tmp/scratchpad/shared-rendering/` under session-1:

- `comparison.html`: index linking five groups and all 167 pairs, using the repository's existing
  side-by-side/wipe template. Image paths URL-encoded; embedded JSON escapes less-than signs.
- `compare-wf0-chirps_20000101_20161231.html`, `compare-wf0-era5_20000101_20161231.html`,
  `compare-wf0-comparison.html`, `compare-wf1.html`, `compare-wf2.html`.
- `visual-review/sheet-01.jpg` through `sheet-21.jpg`: inspected overview pairs.
- `baseline/` and `candidate/`: original full-resolution figures and technical evidence.

These local artifacts are retained for task t2610082103 and owner inspection. No production images
were overwritten, and no image-byte equality criterion was used.

Supplemental verification added `compare-supplemental.html` as a sixth group, bringing the viewer to
187 pairs. These 20 edge-case pairs were technically compared and visually inspected by the rendering
worker; its acceptance evidence records the inspected cases and limitations. Very long fixed-width
year axes retain their existing crowded labels; no change was made in this extraction.
