# Interactive figure comparison template

The tracked [HTML template](figure-comparison.html) preserves the approved side-by-side review interface:
figure selection, overlay wipe, captions inside the canvas, optional canvas boundaries, consistent physical
font scaling, and the selected source directory. It contains no production paths or session figure data.

Copy it into a disposable review folder from the worktree root:

```powershell
New-Item -ItemType Directory -Force .tmp/scratchpad/figure-review
Copy-Item dev/reference/figure-comparison.html .tmp/scratchpad/figure-review/comparison.html
```

Edit the copy's `<title>` and `<h1>` for the active plot group. Replace `const items=[]` with a JSON array
of figure records. Use JSON serialization when generating the page programmatically; do not interpolate
unescaped filenames or captions into JavaScript. Escape `<` as `\u003c` in embedded JSON to prevent a
caption containing `</script>` from terminating the script element.

Example record (image URLs resolve relative to the copied HTML file):

```javascript
const items=[{
  "label": "CHIRPS · Spell",
  "existing_path": "C:/project/data/climate/historical/chirps/figures/spell.png",
  "before": "before/spell.png",
  "after": "revised/spell.png",
  "version": "revision-1",
  "before_caption": "Caption for the existing figure.",
  "after_caption": "Caption for the revised figure.",
  "before_edges": [0.12, 0.95],
  "after_edges": [0.14, 0.95]
}];
```

`existing_path` identifies the original selected file; the page displays its parent directory on a new
line below `Path:`. `version` refreshes the revised image after rerendering. Caption fields are optional.
The edge pairs are the plotting area's left and right positions as fractions of the full image width;
they align captions to the plotting area. Omitted edge pairs default to the full width.

The preserved sizing assumes 600 dpi exports. It uses a shared display scale based on a 140 × 80 mm
reference canvas, card width and viewport height, keeping smaller figures smaller and text sizes
proportional. If preparing images at another resolution, update the four `600` values in `sizeCanvases`
to that common export dpi. Use the same dpi for both versions and all entries in a review group.

Open the copied page in a browser. Keep only the current group's records. Caption toggling adds space
below the figure within its white canvas, leaving the figure dimensions unchanged. The overlay uses the
revised caption; side-by-side mode shows each version's own caption. For unequal canvas dimensions, use
side-by-side mode to assess physical size: the overlay stretches the revised layer to the existing layer's
width and is intended for comparisons with matching dimensions.

Keep figure images and populated pages untracked in scratch. Preserve approved interface improvements
in the template, and preserve scientific style decisions in [plot-style.md](plot-style.md). This template
is a development aid and is not part of workflow outputs.
