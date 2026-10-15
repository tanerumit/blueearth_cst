# Console wording implementation

Applies the WF0–WF4 emitter reviews dated 2026-10-14/15, in workflow order. The HTML reviews remain
proposal snapshots. Runtime calculation, selection, coverage, and failure policies remain authoritative.
Legacy helpers marked outside the active route are excluded; new summaries use existing retained records
and actual run counts. Publication means local artifact finalization, never an external upload.

## WF0 — complete

Shared spatial messages, extraction coverage, figure-write rows, completion wording, and target descriptions
also reach later workflows. Source diagnostics distinguish unavailable estimates from skipped output files;
comparison reports the configured period and common valid reporting-year count. Temperature and subbasin
coverage messages preserve their existing eligibility rules.

Verification: the initial focused batch had 467 passes and 21 wording assertion failures. The 21 affected
checks passed after updating their expectations. New unavailable-figure reporting: four checks passed.
`pytest tests/test_cli.py::test_snakefile_cli_analyze_climate -q`: passed. The dry-run needed normal
Snakemake cache access outside the Windows sandbox; a stack sample established that the restricted
attempt was retrying temporary-directory creation before workflow evaluation. Scoped Ruff passed.
No scientific calculations or workflow dependencies changed.

## WF1 — complete

Model and forcing starts describe their actual products. Waterbody setup reports recorded skipped-method
reasons; outlet/gauge identities and duplicate handling remain visible. Warm-up messages describe
postprocessing rather than a rerun. Simulation-only station figures are distinguished from observation-based
evaluation, and the performance-table summary counts actual evaluated columns without claiming finite metrics.

Verification: 165 focused model, waterbody, evaluation, export, map, gauge and forcing checks passed across
the focused batches and two wording rechecks. The WF1 DAG dry-run passed with normal Snakemake cache access.
Scoped Ruff passed. The historical Julia driver changes only text; exit status and progress remain unchanged.

## WF2 — complete

Acquisition and reference-period warnings explain their operation without fixed slowdown claims. Change
factors count ensemble combinations and combination–window pairs; partial coverage remains distinct from
fully resolved composition records. Figure eligibility uses readable product labels and recorded reasons.
Plot rows use `projection_plots`, with a shared reference stated once where applicable.

Verification: 145 focused acquisition, window, change-factor, preparation and basin-series checks passed
after two reference-warning expectation updates. Two render/manifest checks passed, preserving ordinary
and captioned artifacts and verifying the new messages. WF2 DAG dry-run and scoped Ruff passed.

## WF3 — complete

Realizations, perturbation points, baseline transformations, and retained scenario runs are named separately.
Ready-collection reuse is explicit; publication summaries appear only after successful publication.
R messages and lookup counts are translated in the excluded shared console renderer, leaving provider
source and stochastic seeds unchanged. Pre-DAG completion is distinguished from jobs scheduled in the DAG.

Verification: 404 focused launcher, seed, inventory-boundary and console checks passed after updating three
minimal launcher plan fixtures and one old slowdown assertion. The owned source-phase DAG dry-run passed.
The complete 18-file generation inventory was compared against the pre-implementation tree: no hashed
source changed. Scoped Ruff passed. R code and generation algorithms were not edited.

## Remaining sequence

WF4 simulation/metrics operation and retained response reporting.
