# Export mechanics increment completed

Task t2610082103, 2026-10-10. Source commit:
`480f9be58d948940e0d8db00f82e130e3fc22f8d`, on `refactor/t2610082103-shared-plotting`.
Parent and prechange baseline: `dbe6cbe69739c697a9c6e585acc3c92bf30cf202`.

## Outcome

The neutral `plotting/export.py::export_figure` creates parents and saves an explicit figure without
workflow logging or runtime plotting imports. The existing `snake_utils.save_figure` delegates export
and retains lazy pyplot, current-figure fallback, options, error behavior and successful-save bundles.
The fallback retains pre-mkdir to preserve failure before implicit figure creation. Its second mkdir
is deliberately idempotent. Existing callers and scientific preparation remain unchanged.

Only the new exporter, the adapter and `dev/reference/plot-style.md` changed. No files were deleted.
This mechanical continuation received independent Python review; no architecture decision was reopened.
The [brief](brief.md) was saved before source editing. No merge or push was performed.

## Acceptance and retained evidence

- [Implementation checks](implementation-evidence.md): six targeted export/log tests passed, plus
  explicit-figure, options, lifetime, failure, import and SVG backend probes. Touched-file Ruff and
  final repository lint/format passed. Windows Pixi Python 3.12.13, Matplotlib 3.11.0, Agg for renders.
- [Independent review](code-review.md): no actionable findings. No duplicate test execution.
- [Render evidence](render-evidence.md) and [comparison](render-comparison.json): 49 PNG pairs and
  two PDF pairs preserve inventory, geometry and metadata; eight caption/record/metric artifacts,
  prepared values, input hashes and normalized production log rows match.
- Coordinator inspected all 49 PNG pairs using nine labeled sheets, plus the full clay map and
  captioned WF2 change cloud. No visible export regression at these inspection scales.
- PDFs passed structural, geometry and metadata checks. No PDF rasterizer was available; independent
  visual parity of the PDFs is unverified. Paired production PNGs were inspected.
- [Source hashes](source-hashes.json) matched the committed working files after commit; no executable
  edits intervened between checks, renders and commit. Documentation-only pointer cleanup did not
  affect the tested source. Full suite, all-five execution and numerical baseline gates were not owed
  for this figure-only extraction; no rules, script signatures or runtime/configuration contracts changed.

The 42 WF1/WF2 baseline PNGs were reused from the preceding foundations candidate. Seven new PNGs and
two PDFs covered spatial elevation, categorical/continuous thematic maps, legacy model elevation and
legacy climate exports. WF0 direct diagnostics, WF1 direct forcing, WF3/R and WF4 were unaffected.

Worker execution and review requested GPT-6.1 Sol/medium with at most two concurrent workers and one
source writer; the coordinator reconciled results and inspected figures. Effective runtime settings
and token usage were not reported. No quantified cost-saving claim is made.

## Artifacts and remaining work

Paths in the worker evidence resolve from the retained session-1 scratch directory
`.tmp/scratchpad/shared-rendering/export-mechanics/`, not this durable evidence directory.
It contains `comparison.html` (all 49 PNG pairs), `visual-review/sheet-01.jpg` through `sheet-09.jpg`,
the baseline/candidate trees, source/input manifests, probe scripts and full command logs.
The prior `.tmp/scratchpad/shared-rendering/candidate/` remains the frozen 42-image baseline.
Retain these roots for t2610082103 review and subsequent increments; do not overwrite or clean them yet.

The soil-clay colourbar title clips the top edge before and after this change. Track this existing
composition defect with the existing caption axes-growth, crowded long-record ticks and all-missing
map interpretation issues. Fixing these requires an explicit appearance/layout increment.

Stage 1 remains in progress: establish the caption/layout contract next. Prepared-input chart interfaces,
the map-reference producer and external reuse/packaging remain later stages in the agreed plan.
