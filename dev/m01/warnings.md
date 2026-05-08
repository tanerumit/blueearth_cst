# M1 warnings triage

Per the roadmap, M1 exit criteria require buckets 2 (config / data-catalog)
and 3 (our-code) to be empty. This document records the M1 triage as
actually performed and is **not exhaustive** — see "Coverage gap" below.

## Bucket 1 — upstream (accept)

Frame originates inside `site-packages/`, vendored third-party paths, or
external tools (hydromt, xarray, R packages, Julia, Wflow.jl).

- **`hydromt model_api`: "Model dir already exists and files might be
  overwritten: ...staticgeoms"**. Emitted on every `hydromt update wflow`
  invocation that runs after the initial build. Source:
  `examples/test_local/hydrology_model/hydromt.log:134`. Hydromt's
  `update` mode is intentionally permissive about overwriting; the
  warning is informational and unavoidable in the current pipeline shape.
  Accept.

## Bucket 2 — config / data-catalog (fix in M1 if cheap)

*No entries captured.* See coverage gap below — this should not be read
as "no such warnings exist."

## Bucket 3 — our-code (fix in M1)

*No entries captured.* Same caveat as bucket 2.

## Coverage gap

This triage relied on log files written to disk by the workflow rules.
Only `hydromt`'s build/update steps produce a persistent `.log` file
(`examples/test_local/hydrology_model/hydromt.log` and
`.../run_climate_experiment/hydromt.log`). Every other rule —
`run_wflow`, `generate_weather_realization`, the `src/*.py` scripts
invoked via `script:`, the R weathergen scripts invoked via `shell:` —
emits stderr to the terminal and is not captured anywhere reusable.
Snakemake's own logs (`.snakemake/log/*.snakemake.log`) record rule
orchestration only, not rule stderr.

The roadmap-defined remedy is the M3 cross-cutting deliverable
"per-rule `log:` and `benchmark:` directives on every non-trivial rule"
— once that lands, every rule's stderr is captured to a file under
`logs/` (or wherever the convention puts it), and a comprehensive
triage becomes mechanical.

## Decision and follow-up

- Accept the M1 closure with this incomplete triage rather than
  blocking on the M3 prerequisite. The risk is that real bucket 2 or
  3 warnings exist and aren't being addressed at M1. That risk is
  judged acceptable because M2 (env swap) and M3 (workflow-1 cleanup)
  will both surface and capture warnings as part of their own work.
- A follow-up entry is added under M3 in `dev/followups.md` to
  redo this triage exhaustively once `log:` directives are in place,
  and to fix any bucket 2/3 entries that surface then.
