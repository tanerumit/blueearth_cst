# Export/logging separation — implementation evidence

Task t2610082103, 2026-10-10. Baseline source dbe6cbe6; branch
`refactor/t2610082103-shared-plotting`. Source edits started only after the coordinator's baseline-ready
notice for prior 42 and added 7 PNG/2 PDF baselines. One source writer; no commits, branch changes,
board edits, landing or push.

## Exact change scope

- Added `blueearth_cst/plotting/export.py` with `export_figure(fig, path, **kwargs)`.
- Updated only `save_figure` body/docstring/local import in `blueearth_cst/shared/snake_utils.py`.
- Updated export ownership and an explicit-figure example in `dev/reference/plot-style.md`.

No files were deleted. Callers, styles, rules, configuration, dependencies and tests were unchanged.
No caption, scientific preparation, logging-bundle implementation or output contract changes.

The core uses stdlib and type-only Matplotlib imports; it creates destination parents and calls the
supplied figure's savefig. Return is None, kwargs and exceptions pass through, and no figure is closed,
resized, selected or styled. The existing adapter retains its signature, lazy pyplot import,
current-figure fallback and success-only bundle accounting.

## Compatibility ordering

Prechange temporary probe captured `mkdir -> gcf -> savefig`. On a failed mkdir, gcf was not called,
the exception propagated and no implicit figure appeared. Records:
`implementation-preflight.json` and `implementation-preflight.log`.

The coordinator approved keeping pre-mkdir only for the fig=None fallback. The exporter performs its
own mkdir for standalone explicit-figure callers, so fallback saves perform a second idempotent
exist_ok mkdir after resolving the current figure. This tiny duplication preserves the original
failed-parent side effect without callbacks, options or an extra helper framework. Explicit-figure
adapter calls perform one mkdir. A source comment records the compatibility reason.

## Validation budget and results

Scope rapid; numerical unaffected. No persistent tests added. No CLI, full suite, e2e or numerical
baseline gate, as specified by the brief. Callers were searched with
`rg -n 'save_figure\(' blueearth_cst --glob '*.py'`; all existing consumers remain unchanged.

Final focused command ran once:

```powershell
pixi run pytest tests/test_snake_utils.py::test_save_figure_writes_creates_parent_and_announces tests/test_snake_utils.py::test_save_figure_bundles_one_directory_into_one_row tests/test_snake_utils.py::test_save_figure_bundles_alternating_directories_separately tests/test_snake_utils.py::test_an_ordinary_row_flushes_the_bundle_first tests/test_snake_utils.py::test_a_closing_log_drains_pending_figures tests/test_snake_utils.py::test_a_new_log_starts_a_new_bundle
```

PASS: 6 passed in 2.04 seconds, exit 0. `implementation-pytest.log` contains one session header.
Environment: Windows, Pixi Python 3.12.13, pytest 9.0.3.

`pixi run python .tmp/scratchpad/shared-rendering/export-mechanics/implementation-probes.py`: PASS.
Results in `implementation-probes.log` and `implementation-probe-results.json` verify:

- Actual PNG/PDF exports save the supplied 2x1 inch figure while another 1x2 inch figure is current.
- PNG dimensions are independently expected 200x100 pixels at 100 DPI; metadata scrub is preserved.
- PDF Author metadata passes through; str and Path destinations create their parents.
- Current figure, figure size and open-figure inventory remain unchanged; exporter emits no output.
- Path object and nested kwargs identity pass through, and savefig return does not alter None return.
- Sentinel save errors propagate unchanged; failed saves do not enter the workflow's figure bundles.
- A failed adapter parent creation calls no gcf and creates no implicit figure.
- A fresh svg process retains svg and imports no pyplot, workflow, geospatial or logging adapter modules.

Probe products: `implementation-probe-output/nested/explicit.png` and
`implementation-probe-output/pdf/explicit.pdf` (scratch only).

Touched-file `pixi run ruff check blueearth_cst/plotting/export.py blueearth_cst/shared/snake_utils.py`:
PASS. `pixi run ruff format --check` on those two paths: PASS.
Logs: `implementation-ruff.log`, `implementation-format.log`.

Final repository `pixi run lint`: PASS. `pixi run format-check`: PASS, 438 files already formatted.
Both ran once on final executable source; logs `implementation-repo-lint.log` and
`implementation-repo-format.log`. `git diff --check`: PASS.
After these checks, one documentation-only correction expanded the logging adapter's ownership pointer
to its full repository path; executable source and tested candidate remain identical.

Source-ready notification was sent before candidate rendering/review. Render comparison and independent
review are coordinator-owned; no visual-acceptance claim is made by this implementation evidence.
