# Interactive figure comparison template

The tracked [HTML template](figure-comparison.html) provides side-by-side and draggable wipe comparison,
linked zoom and pan, captions inside the canvas, optional canvas boundaries, consistent physical font
scaling, and the selected source directory. It contains no production paths or session figure data.

Copy it into the owning task's temporary folder from the worktree root (replace `<id>`):

```powershell
New-Item -ItemType Directory -Force '.tmp/tasks/<id>/figure-review'
Copy-Item dev/templates/figure-comparison.html '.tmp/tasks/<id>/figure-review/comparison.html'
```

Edit the copy's `<title>` and `<h1>` for the active plot group. Replace `const items=[]` with a JSON array
of figure records. Use JSON serialization when generating the page programmatically; do not interpolate
unescaped filenames or captions into JavaScript. Escape `<` as `\u003c` in embedded JSON to prevent a
caption containing `</script>` from terminating the script element.

Example record (image URLs resolve relative to the copied HTML file):

```javascript
const items=[{
  "label": "CHIRPS · Spell",
  "existing_path": "C:/project/data/climate/historical/chirps/plots/spell.png",
  "before": "before/spell.png",
  "after": "revised/spell.png",
  "version": "revision-1",
  "dpi": 600,
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

The optional `dpi` field defaults to 600 and must be positive. Use the same export dpi for both versions
of a pair. The shared overview scale uses a 140 × 80 mm reference canvas, card width and viewport height,
keeping smaller figures smaller and text sizes proportional. Zoom 1× means this overview scale, not
actual screen millimetres. Zoom and pan affect both versions together; Reset view restores the overview.

Open the copied page in a browser. Keep only the current group's records. Caption toggling adds space
below the figure within its white canvas, leaving the figure dimensions unchanged. Pan to inspect content
outside the viewport. Wipe uses the revised caption; side-by-side mode shows each version's own caption.
For unequal canvas dimensions, the page defaults to side by side and requires explicitly allowing wipe.
Wipe aligns canvas top-left corners at a common scale and pads the smaller image without stretching it;
plotting areas may still differ in position. Drag its divider or use the revised-visible slider.

Previous/next buttons and the selector navigate the group. Navigation resets zoom, pan and comparison
mode, and waits for both images before revealing the pair. Failed loads name the missing image;
Reload current pair retries loading. Update `version` after rerendering to refresh the revised image.

Keyboard shortcuts apply when focus is outside controls: Left/Right navigate, W switches comparison
mode, +/− zoom, 0 resets, and holding E in wipe mode peeks at the existing image. The peek button also
supports holding Space or Enter. The focused wipe divider supports Left/Right and Home/End.
Review state is not persisted. The layout stacks the pair on narrow screens.

Keep figure images and populated pages untracked in scratch. Preserve approved interface improvements
in the template, and preserve scientific style decisions in [toolbox-plot-style.md](../reference/toolbox-plot-style.md). This template
is a development aid and is not part of workflow outputs.
