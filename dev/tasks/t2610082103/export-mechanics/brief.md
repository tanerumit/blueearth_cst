# Task brief — Separate figure export from workflow logging

Task: t2610082103. Date: 2026-10-10. Status: authorized by the user's request to continue.
Source base: dbe6cbe6. Branch: refactor/t2610082103-shared-plotting, session-1.

## Context and decision

The first foundations increment is complete. The source inventory finds one small shared exporter:
`snake_utils.save_figure(path, module="plot", fig=None, **kwargs)`. It creates parents, saves, then
accumulates workflow log bundles. Its callers own export options, captions, figure lifetime and styles.

Continue the approved internal-core direction with an obvious mechanical extraction. This packet gets
an independent Python review; it does not reopen the architecture-design loop. There is no new output
contract, scientific choice or export policy. If implementation needs one, stop and scope it separately.

Add `plotting/export.py` with `export_figure(fig, path, **kwargs)`, requiring an explicit figure. It creates
missing parent directories and forwards to that figure's savefig, returning None. Keep all caller options
and errors visible. The core imports no workflow, configuration, logging, pyplot or geospatial modules;
use type-only Matplotlib imports if needed. It neither closes nor resizes the figure nor selects a backend.

The existing snake_utils function remains the compatibility/logging adapter. Preserve its signature,
current-figure fallback, lazy plotting imports, bundle order and success-only accounting. All existing
callers remain unchanged. Preserve destination-creation error behavior; report any unavoidable change
in implicit current-figure resolution order for coordinator judgment instead of inventing abstractions.

Alternative: migrate every direct savefig caller now. Rejected because it widens the packet without
helping separate the existing logging adapter. Direct-save families and legacy export policies stay put.

## Allowed scope and ownership

Implementation owns only these three tracked paths:

- New `blueearth_cst/plotting/export.py`.
- `blueearth_cst/shared/snake_utils.py`: save_figure body/docstring and its import only.
- `dev/reference/plot-style.md`: export ownership and one concise explicit-figure usage example.

No tests, rules, config, dependency changes, caption redesign, caller migration or run_log_core edits.
No files deleted. Coordinator handles canonical task records on main and scoped commits.
All disposable probes/logs/renders live under `.tmp/scratchpad/shared-rendering/export-mechanics/`.
Workers are not alone; preserve others' changes. No nested delegation, commits, merges or pushes.

## Allocation and sequence

Reuse the earlier frontier allocation's execution/review split; this is a bounded follow-on refactor.
No new frontier planning dispatch is warranted. Maximum two simultaneous workers; one source writer.

| Packet | Role/model/effort | Boundary |
|---|---|---|
| Baseline and renders | python-engineer, GPT-6.1 Sol/medium | Scratch only; reuse 42 existing PNGs |
| Implementation/probes | python-engineer, GPT-6.1 Sol/medium | Three tracked paths; baseline first |
| Independent review | Fresh python-engineer, GPT-6.1 Sol/medium | Read-only completed diff |
| Integration | Coordinator | Reconcile checks, inspect figures, commit |

Fallback for execution: GPT-6 Sol/medium; unresolved architecture returns to a frontier architect.
Effective in-process settings and token costs are unreported. Reopen only on failed acceptance or scope change.

## Validation and acceptance

Scope rapid, numerical unaffected; repository figure-only rules govern the shared helper. No full suite,
all-five execution or numerical baseline. No script signature, rule input or configuration changes.

| Claim | Check | Input/output and reuse |
|---|---|---|
| Wrapper/log compatibility | Six existing targeted pytest nodes | Existing fixtures; owned logs |
| Explicit figure, kwargs and lifetime | Temporary behavioral probes | Two figures; PNG/PDF; failed export |
| Import/backend independence | Fresh-process probe | SVG backend; no workflow/pyplot import |
| Values/layout/products preserved | Affected renders and inspection | Prior WF2 36 + WF1 6; added maps/legacy |
| Candidate identity | Source/input hashes and Git diff | Baseline dbe6cbe6; exact final commit |

Targeted existing tests (one final invocation; no permanent tests added):

```powershell
pixi run pytest tests/test_snake_utils.py::test_save_figure_writes_creates_parent_and_announces tests/test_snake_utils.py::test_save_figure_bundles_one_directory_into_one_row tests/test_snake_utils.py::test_save_figure_bundles_alternating_directories_separately tests/test_snake_utils.py::test_an_ordinary_row_flushes_the_bundle_first tests/test_snake_utils.py::test_a_closing_log_drains_pending_figures tests/test_snake_utils.py::test_a_new_log_starts_a_new_bundle
```

Check that explicit export saves the supplied figure while another figure is current, the figure stays
open, parent creation works with both string and Path inputs, kwargs are unchanged, core emits no logs,
and errors propagate without a successful bundle entry. Preserve PNG/PDF metadata and DPI at callers.
Narrow lint/format checks on touched Python files; final repository lint/format once after source stabilizes.

The render worker reuses prior candidate PNGs as a frozen baseline for the 42 affected retained outputs.
Capture previously uncovered spatial elevation/thematic and legacy cases before editing. Rerender only
affected families into separate roots; compare metadata and dimensions, inspect images, never use byte
equality as a visual oracle. WF0 direct diagnostics, WF1 direct forcing, WF3/R and WF4 are unaffected.

Record commands, results, input/environment identity, final commit and output roots in task evidence.
Source-ready notification lets rendering and review start without concurrent source edits.
Stop after the mapped checks pass; additional runs need a changed candidate or unresolved concern.
