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

## Remaining sequence

WF1 model construction and simulation review; WF2 projection acquisition and diagnostic products;
WF3 generation and collection publication; WF4 simulation/metrics operation and retained response reporting.
