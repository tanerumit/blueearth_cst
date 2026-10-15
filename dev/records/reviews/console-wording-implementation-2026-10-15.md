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

## Remaining sequence

WF2 projection acquisition and diagnostic products; WF3 generation and collection publication;
WF4 simulation/metrics operation and retained response reporting. WF3 source-file hashes participate in
stochastic identity: its R log strings will be translated in the excluded shared console renderer so wording
alone cannot re-key generation or change its random sequence.
