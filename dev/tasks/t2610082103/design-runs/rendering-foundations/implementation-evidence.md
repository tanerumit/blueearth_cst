# Shared rendering extraction — implementation evidence

Source-ready: 2026-10-10. One source writer; no commits, branch changes, landing or push.
Design-v2 SHA256: 80602fda7fae0ad1932eb4d618f98de148b950e0090093c0aa9652afd6b1ffaf.
Preflight matched the design identity and every baseline/evaluation source hash before editing.

## Scope and changes

Approved figure-only validation budget, numerical axis unaffected. Existing focused tests reused;
no persistent tests added. No full suite, numerical baseline gate or fresh workflow execution.

New files:
- `blueearth_cst/plotting/__init__.py`
- `blueearth_cst/plotting/fundamentals.py`

Updated files:
- `blueearth_cst/climate_analysis/diagnostic_figures.py`
- `blueearth_cst/climate_analysis/diagnostic_render.py`
- `blueearth_cst/climate_analysis/diagnostic_maps.py`
- `blueearth_cst/climate_analysis/diagnostic_subbasins.py`
- `blueearth_cst/model/forcing_figures.py`
- `blueearth_cst/model/plot_results.py`
- `blueearth_cst/projections/projection_suite_figures.py`
- `blueearth_cst/projections/plot_proj_timeseries.py`
- `blueearth_cst/shared/func_plot_signature.py`
- `blueearth_cst/shared/plot_evaluation.py`
- `dev/reference/plot-style.md`

Removed duplicate WF0 definitions: `new_fig`, `ygrid`, `year_ticks`, `five_year_ticks`,
`heatmap_frame`, `blank`, `top_legend`, `colourbar`, `inside_legend`, `add_caption`, and their
17 grouped token assignments. Replaced by exact shared implementations and explicit compatibility aliases.
No source files deleted. Scientific preparation, chart compositions, captions/exporters and the legacy
cartographic/evaluation style remain unchanged.

Call-site searches used `rg -n 'diagnostic_figures|matplotlib|textwrap' blueearth_cst/...` and a
the following post-change search:

```powershell
rg -n 'diagnostic_figures|artists\.(STYLE|new_fig|add_caption|H_SINGLE|LW_LINE|MS_LINE|ygrid|inside_legend)' blueearth_cst
```

Remaining WF0 imports own actual WF0 compositions, View, or scientific/caption helpers. Evaluation's
`artists` alias now names fundamentals. Scratch preview rebinding search found no matching edits in
readable paths; existing inaccessible pytest scratch directories prevent exhaustive preview-discovery claims.

## Backend ownership and probes

Before extraction, a fresh process selecting svg retained svg when importing evaluation's parse-time
constant, then switched to Agg when importing its original lazy drawing dependency, diagnostic_figures.
Consequently `model/plot_results.py` now selects Agg explicitly before importing pyplot.

`pixi run python .tmp/scratchpad/shared-rendering/candidate/implementation-probes.py` passed.
Its final log and structured results are `candidate/implementation-probes.log` and
`candidate/implementation-probe-results.json`.

- All ten moved function ASTs and seventeen token assignment ASTs match the original exactly.
- Every extracted WF0 alias has identical object identity; mutable STYLE/LABEL_BOX edits propagate.
- Fresh Agg and svg processes retain their selected backend when importing fundamentals.
- Core imports no WF0/domain, pandas, geospatial, config, Snakemake or logging modules.
- Package initialization is inert; evaluation's parse-time constant imports no Matplotlib or core.
- Cartographic FONT_SIZE_BASE rebinding changes `_publication_rc` at runtime; restored after probe.
- Legacy plot_style retains 8/7 pt font defaults.

An initial scratch probe lacked the checkout on sys.path; corrected in the probe only. Source was unaffected.

Caption geometry matches the original exactly for short and long captions. The existing algorithm
changes axes height from 2.593941 inches to 2.623403 (short) or 2.918023 (long), while width remains
4.910739 inches. This is the design's anticipated existing geometry defect, preserved rather than
redesigned. Record a follow-up; extraction introduces no geometry difference.

## Checks

Touched-file `pixi run ruff check <12 Python paths>`: PASS.
Touched-file `pixi run ruff format --check <12 Python paths>`: PASS, twelve files already formatted.
Logs: `candidate/implementation-ruff.log`, `candidate/implementation-format.log`.
`git diff --check`: PASS.

Initial focused test command (one run, retained after environmental abort):

```powershell
pixi run pytest tests/test_wf0_diagnostic_contracts.py tests/test_projection_suite_figures.py tests/test_wf1_plot_outputs.py tests/test_plot_evaluation.py tests/test_func_plot_signature.py tests/test_cli.py
```

Log: `candidate/focused-pytest.log`; Python 3.12.13, pytest 9.0.3, Windows Pixi environment.
81 tests collected; all 9 WF0 and 13 projection-suite tests passed. The run was stopped during the
first WF1 subprocess test because Snakemake entered a Windows cache-directory permission retry loop.
No source/test changes were made to unblock it; passed coverage was preserved and not repeated.
Final `pixi run lint`: PASS, all checks passed.
Final `pixi run format-check`: PASS, 437 files already formatted.
Logs: `candidate/implementation-repo-lint.log`, `candidate/implementation-repo-format.log`.
Both ran once on the final source while the focused subprocess contract checks continued, as directed
by the coordinator.

### Environmental diagnosis and remaining coverage

The owned WF1 child had one thread, stable memory and file-byte I/O, no sockets or descendants,
and millions of metadata operations with CPU dominated by kernel calls. A bounded import-only
Snakemake control passed in 1.2 seconds. A bounded dry-run control dumped a stack in
`tempfile.mkdtemp` called by `snakemake.sourcecache.SourceCache.__init__` (sourcecache.py:359).
Its cache location is the Windows shell AppData user cache, outside the permitted workspace.
Python 3.12's Windows PermissionError retry path loops when parent existence/access probes succeed.
Installed appdirs uses the Windows shell CSIDL location, so LOCALAPPDATA/XDG overrides cannot
reliably redirect this path. No upstream code or tracked profiles were modified.

Preserved diagnostics: `candidate/implementation-wf1-process-probe.log`,
`candidate/implementation-snakemake-startup-probe.log`, and
`candidate/implementation-snakemake-parse-probe.log`. The first parse diagnostic's timeout handler
had a scratch-only bytes/text mismatch; direct-to-file capture corrected that probe and preserved
the stack. Original test source was unaffected.

The coordinator authorized a narrow permission escalation. The exact owned pytest PID and its
three descendants were terminated after saving evidence; `implementation-stop-owned-test.log`
confirms no descendants remained. Remaining coverage is running once outside the sandbox:

```powershell
pixi run pytest tests/test_wf1_plot_outputs.py tests/test_plot_evaluation.py tests/test_func_plot_signature.py tests/test_cli.py
```

Log: `candidate/implementation-remaining-pytest.log`; PASS, 59 passed in 97.13 seconds, exit 0.
Together with the retained 22 passes, all 81 focused cases passed on the unchanged final source.
Each log contains exactly one pytest session header. No failures or skipped cases remain.
`git diff --check` passed again after completion; final source paths remain the approved thirteen files.

The render worker separately owns matching retained-input candidate renders and supplements.
Frozen baseline was preserved. Source edits are complete; visual/inventory acceptance remains with
the coordinator and render/review agents.
