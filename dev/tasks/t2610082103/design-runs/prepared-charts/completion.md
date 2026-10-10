# Prepared annual and monthly charts — completion

Implemented the owner-approved design-v2 in source commit `22fbe441` on
`refactor/t2610082103-shared-plotting`, based on `4d19a377`. No merge or push.
The reviewed design SHA256 remains
`ed2f9691aff7886698883a6087c13ab1cf78abff10e706d89924baa78fd6186e`.

## Delivered boundary

`plotting/prepared_charts.py` owns annual lines, prepared trend segments and monthly envelopes,
with typed records and validation before drawing. WF0 compatibility wrappers remain; WF1 forcing
and hydrological summaries call the shared renderer directly. Scientific preparation, source order,
units, fitted statistics, reporting-year rules, captions and export remain with their owners.
The core has no pandas, workflow, configuration, IO or backend-selection dependency.
`dev/reference/plot-style.md` documents the interface and caller responsibilities.

## Verification and acceptance

All commands ran in session-1 with its Pixi environment, Python 3.12.13 and Matplotlib 3.11.0.
The baseline was captured at `4d19a377` before source changes. The final source candidate is
`22fbe441`; no executable edits followed the passing gates. Exact source, environment-lock,
harness and input fingerprints are retained in `validation-manifest.json`.

The reusable output root is `.tmp/scratchpad/shared-rendering/prepared-charts/verification/`.
The `before/` and `after/` roots contain figures, artist records, prepared-value captures and input
hashes. `comparison.html` exposes all before/after PNG pairs; `visual-sheets/` holds 14 contact sheets.
These scratch outputs remain retained for this active task and later batch acceptance.

| Claim | Cases and evidence | Result |
|---|---|---|
| Prepared values and fits preserved | Full-precision table hashes and array captures | Exact match |
| Lines, bands, labels and legends preserved | 109 matched render pairs; artist comparisons | Pass |
| Saved geometry preserved | Bounds, limits, ticks, canvas dimensions and DPI | Zero drift |
| Inventory and captions preserved | Exact product inventory; 18 metadata/caption files | Pass |
| Visual appearance preserved | All 14 paired contact sheets and three full-size figures | No new regression |
| Checks detect regressions | Injected line, band and one-pixel geometry differences | All rejected |
| Core is inert and validates shapes | Backend/style import probe; six invalid-input controls | Pass |
| Masks, gaps and inputs preserved | Masked annual/monthly inputs; no mutation; empty sources | Pass |
| Scientific functions unchanged | AST equality for four preparation/metric functions | Pass |
| Active adapters migrated | No WF1 View construction; WF0 wrappers retained | Pass |

Coverage: WF0 real source/comparison charts (42), WF1 forcing including unchanged map neighbors (9),
synthetic WF0 October/gapped/missing-temperature/all-missing/constant-negative cases (14), optional WF0
subbasin charts (6), real hydrological AET/GWR basin and subbasin charts (20), and synthetic hydrological
rate/stock/negative-value basin and subbasin charts (18). Total: 109 PNG pairs.
Real inputs reuse retained Liberia outputs; the manifest identifies their files. Synthetic inputs are
defined in the fingerprinted harness. This is matched figure rendering, not a fresh model execution.

Commands used the paths below, with output redirected to the listed logs.
Log paths are relative to the verification output root.

```powershell
pixi run python .tmp/scratchpad/shared-rendering/prepared-charts/verification/render.py before
pixi run python .tmp/scratchpad/shared-rendering/prepared-charts/verification/render.py after
pixi run python .tmp/scratchpad/shared-rendering/prepared-charts/verification/compare.py
pixi run python .tmp/scratchpad/shared-rendering/prepared-charts/verification/api-probe.py
pixi run lint
pixi run format-check
git diff --check
```

| Check | Log | Result |
|---|---|---|
| Baseline render | `before-verified.log` | Exit 0; 109 captures |
| Candidate render | `after.log` | Exit 0; 109 captures |
| Matched comparison | `compare.log` | Exit 0; no failures |
| API probe | `api-probe.log` | Exit 0 |
| `pixi run lint` | `lint.log` | All checks passed |
| `pixi run format-check` | `format.log` | 439 files formatted |
| `git diff --check` | Console | Pass |

No persistent tests, deletions, numerical baseline check, full suite or fresh workflows were added/run.
Only terminal rendering changed; WF2, WF3 and WF4 have no callers of the new API. Broader batch gates
remain a landing decision under the repository validation ladder.

## Limits and execution diagnostics

Independent scientific, risk and external design reviews all approved the immutable design.
The implementation worker (python-engineer, requested Sol/medium) produced a partial capture harness
then stopped at its service usage limit, before source edits. The owner directed continuation.
Root completed implementation and verification inline; no independent post-implementation review is
claimed. Actual worker settings, implementation token cost and cost savings are not measured.

Harness rework before source edits corrected an integer-fixture NaN assignment, NumPy JSON encoding
and an overwritten capture dictionary; a coverage assertion then proved every PNG was captured.
The API probe initially tried rendering on SVG, exposing the existing inside-legend dependency on
`get_renderer`. The corrected probe verifies import is backend-inert, then renders with Agg.
Arbitrary vector canvases and vector-export parity are not qualified by this packet.

An earlier automatic approval service usage limit prevented saving approval metadata; it was not a
safety rejection. The later authorized continuation successfully committed the verified source.
Existing long-record tick crowding and map issues remain outside this appearance-preserving packet.

Next planned increment: separately design the shared historical map-reference producer and its
workflow boundaries. External packaging and R/WF3 remain later increments.
