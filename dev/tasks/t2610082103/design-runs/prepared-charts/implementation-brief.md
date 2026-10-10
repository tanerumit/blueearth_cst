# Task Brief — implement prepared annual and monthly charts

### Context

Follow AGENTS.md and the live validation ladder. User approved exact design-v2 on 2026-10-10:
SHA256 `ed2f9691aff7886698883a6087c13ab1cf78abff10e706d89924baa78fd6186e`.
All three reviews approved, zero findings. Run status records acceptance; original proposed header
is intentionally unchanged. Read design-v2.md for the exact API and caller obligations.
Source baseline: `4d19a377e733fc5056c480981771889736841ae0`, clean pinned session-1 branch.

### Goal

Implement the approved four-source-file extraction and demonstrate unchanged prepared values,
artist contents, appearance, metadata and output inventories. Remove WF1 View construction.

### Non-goals

No scientific algorithms, new dependencies, maps/reference changes, caption changes, tick crowding
fixes, CLI/config/rule changes, external packaging, WF2/R changes or persistent figure-only tests.

### Allowed scope

Python-engineer is sole writer of:

- `blueearth_cst/plotting/prepared_charts.py` (new).
- `blueearth_cst/climate_analysis/diagnostic_figures.py`.
- `blueearth_cst/model/forcing_figures.py`.
- `blueearth_cst/shared/func_plot_signature.py`.
- Disposable harness/output/evidence beneath this run's `verification/` scratch directory.

Root owns nearby docs, task state, canonical records and commit. Other files are read-only. Re-measure
callers with `rg -n '_annual_trends\(|_climatology\(|artists.series\(' blueearth_cst` before starting.
No nested agents. You are not alone in the workspace; preserve others' edits. No commits, branching,
landing or pushing. Report a needed additional source file or changed interface to root first.

### Required changes (checklist)

1. Build a reusable narrow before/after harness and capture baseline BEFORE any source edits.
   Preserve frozen existing evidence; do not blindly execute old scripts with their fixed output roots.
2. Implement the accepted frozen records and five functions. Validate structural shapes before artists,
   preserve masked values/NaNs/order, and retain ordinary Figure/artist return behavior.
3. Migrate all named callers while retaining WF0 wrappers and hydrological composition exceptions.
   Keep arithmetic, selection, formatting and workflow preparation unchanged. No core workflow imports.
4. Re-run the same harness after source edits and classify every difference. Do not widen tolerances.
5. Run touched-file Ruff checks. Write a concise evidence report with exact commands and output roots.
   Notify root after baseline capture and after final source edits; do not wait for new human approval.

### Commit plan

Root commits the new module and every caller migration together after acceptance; no intermediate
commit may leave callers depending on absent code. Documentation joins that bounded source commit.

### Validation

Repository-specific figure-only policy overrides generic broad-suite escalation. Scope: rapid,
scientific algorithms unaffected; exact preservation of supplied scientific values is still required.
Use existing rapid/retained data. No new model run, baseline-manifest gate, full suite or WF2 rerender.
Root runs final repository lint/format once after executable edits settle.

Let V be `.tmp/scratchpad/shared-rendering/prepared-charts/verification/`. Keep before/after separate.
Develop a small command interface such as `pixi run python <V>/render.py before|after <family>` and
`pixi run python <V>/compare.py`; record the actual commands, not these placeholders, in evidence.

| Claim | Falsifier / check | Case |
|---|---|---|
| Preparation preserved | Different exact values, masks, labels or endpoints | Matched retained inputs |
| Drawing preserved | Changed lines, band vertices, annotations or legend content | Same before/after charts |
| Geometry preserved | Drift exceeding 0.5 export pixel | Same inputs and DPI |
| Products preserved | Missing/extra paths or changed captions/metadata | Adapter output inventories |
| Core independent | Forbidden imports or WF1 View construction | Source/import probe |
| Validation useful | Injected band/line change escapes comparison | Disposable negative control |

Extend the previous recorder to include collection PATH VERTICES, axes legends and annotation text/
positions, in addition to line arrays, ticks/limits, dimensions and styles. Compare numerical arrays
exactly with aligned NaNs; export geometry allows only the design's subpixel tolerance. Preserve
plots for visual inspection; no PNG byte equality requirement. Root arranges independent acceptance.

Required coverage: all affected WF0 source/comparison annual, monthly, temperature, four extreme
families and their caption variants; optional WF0 subbasins; all three forcing annual/monthly figures;
WF1 hydrological amount/rate/stock summaries, optional individual subbasins. Retain forcing-map
inventory and confirm unchanged outputs where the adapter runs them anyway. Add distinct synthetic
cases only for non-January ordering, missing temperature, gapped/all-missing/constant/negative values,
multiple sources and available/unavailable trends. Test malformed shapes, masked inputs, no mutation
and empty source sequences via disposable probes once the new API exists. No permanent tests added.

Reusable recipes and inputs (inspect/adapt, never overwrite):

- `.tmp/scratchpad/shared-rendering/candidate/render-baseline.py`: WF0 and real WF1 forcing adapters.
- `.../caption-layout/render.py` and `capture.py`: WF0/subbasin rendering and saved-geometry capture.
- `.../export-mechanics/render-evaluation.py`: real rapid AET/GWR basin summary recipe.
- `.../candidate/supplemental.py`: edge-case and optional subbasin recipes.
- `.../candidate/wf1/prepared/`: existing prepared forcing arrays/tables (not all trends retained).
- WF0 retained source: `C:/Users/taner/workspace/cst-cases/runs/sp2-liberia/active/data/climate/historical`.
- WF1 model root: `test_case/test_rapid/models/hydrology/wflow/`; retained outputs/staticmaps/forcing.
- WF0 synthetic subbasin tables: `.../candidate/supplemental/fixtures/subbasin_1/`.

Use selected affected WF0 forms instead of re-rendering the whole suite. Explicitly label synthetic
stock/rate or optional support fixtures if no real retained output exists; do not present them as
observations or qualified model results. Keep input hashes, environment/lock identity and source hashes.

### Acceptance criteria

All accepted design contracts implemented; no scientific calculations changed. Matched numerical and
artist checks pass; all affected images exist for independent inspection. Every difference classified,
no missing acceptance case hidden. Relevant lint/format passes; scope remains four source files.

### Output requirements

Return changed paths, exact commands/results, before/after image inventory, input identities, numerical
and geometry outcomes, any limitations, plus `verification/engineering-evidence.md`. Provide a pairing
manifest for root's visual reviewer. Keep disposable render/probe code in scratch.

### Task constraints

One source writer, at most two workers. Bounded implementation model: gpt-6.1-sol/medium; unresolved
conceptual decisions return to root rather than silently redesigning. Start with baseline evidence,
then implement without another permission gate. Existing framework/source bugs stay out of scope.
