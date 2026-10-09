# Rendering foundations completion

Completed 2026-10-10. Tested and committed source: `dbe6cbe69739c697a9c6e585acc3c92bf30cf202` on
`chore/minor-fixes` in session-1.
Baseline source: `07288e94`. The verified source was unchanged from testing/rendering through commit.
Approved design: design-v2.md, SHA256 80602fda7fae0ad1932eb4d618f98de148b950e0090093c0aa9652afd6b1ffaf.

The first increment creates `blueearth_cst/plotting/fundamentals.py` with ten unchanged helpers and the
reviewed CST style tokens. All active consumers migrated; old imports, mutable style identity and lazy
evaluation imports are preserved. The WF1 script now owns Agg selection. No source files were deleted.

Evidence and commands:

- [Implementation and focused checks](implementation-evidence.md).
- [Independent code review](code-review.md): no findings.
- [Rendering acceptance](render-acceptance.md) and [structured comparisons](render-comparison.json).
- [Coordinator visual review](visual-review.md): all 167 normal pairs plus representative full images.
- [Baseline provenance and omissions](baseline-evidence.md).

All required packet checks passed. Numerical methods are unchanged; no full suite, numerical baseline
or fresh all-workflow run is claimed or owed for this figure-only extraction. Landing gates remain for
the eventual combined branch batch. Source branch retained; no landing or push performed.

Environment: Windows Pixi default, Python 3.12.13, Matplotlib 3.11.0; nominal production exports 600 dpi.
Pixi lock SHA256: 797afdad5a8f8c37dd62b2f1e2f88f3fea120c3fc53b7e7c792b860700a6782b.

Input/config identity is recorded in the baseline and rendering evidence. Same retained Liberia WF0,
rapid WF1 and Gabon WF2 inputs were reused read-only. Frozen fingerprints and commands remain under
`.tmp/scratchpad/shared-rendering/` in session-1, alongside `baseline/` and `candidate/` output roots.
Review entry point: `.tmp/scratchpad/shared-rendering/comparison.html` (187 pairs in six groups).

Limits: WF2 retained data uses an adapter; genuine multi-period retained data was unavailable, so that
renderer used a deterministic synthetic fixture. Optional subbasins use relabelled retained tables for
layout coverage. This is appearance/preparation preservation, not independent model validation.

The broad task remains active. Export/logging separation is next; caption geometry and very-long-year
label density are documented pre-existing issues for later layout work. External packaging and WF3/R
alignment remain later steps in the saved landscape plan.
