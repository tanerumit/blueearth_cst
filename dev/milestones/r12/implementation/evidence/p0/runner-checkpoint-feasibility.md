# P0 approved runner and checkpoint feasibility

Lifecycle: frozen execution evidence; supersede if a later mechanism changes it.
Date: 2026-09-10. Environment: Windows, Python 3.12.13, Snakemake 9.6.2.
Status: synthetic operation and checkpoint mechanisms passed. Production
GF-22/GF-29/GF-30 acceptance remains outstanding.

## Approved runner

The [synthetic runner](../../feasibility/simulation-runner.py) parses its own
arguments and rejects an unsupported actual target list before launching
Snakemake. It selects two fixed [simulation](../../feasibility/simulate-and-metrics.smk)
and [metrics-only](../../feasibility/metrics-only.smk) rule modules through the
[router](../../feasibility/simulation-router.smk). Each accepted command launches
Snakemake exactly once. Bare simulation Snakefile target enforcement is not
claimed; the mandatory-runner ruling is recorded in the accepted design.

| Operation | Accepted requests | Refused requests |
|---|---|---|
| `simulate-and-metrics` | omitted target; `all` | `metrics`; selected or mismatched metric filename; Wflow filename; mixed targets; unknown target |
| `metrics-only` | `metrics`; exact selected metric filename | omitted target (defaults to `all`); `all`; mismatched metric filename; Wflow filename; mixed targets; unknown target |

All 16 combinations ran as both dry-run and real invocation. Assertions compare
the complete observed producer-rule sets and require exactly one launch for
accepted requests, none for rejected requests. Three additional cases remove
the retained inventory, required `q` variable or native response artifact;
each refuses without admitting simulation. Generation inputs and live model
artifacts are absent from these metrics-only fixtures.

This is a synthetic mechanics probe. Production configuration composition,
simulation identity, arbitrary path normalization and the production response
schema remain assigned to P1/P2/P3; no fixture hash is a shipped identity format.

## One-invocation checkpoints

The [source checkpoint](../../feasibility/source-checkpoint.smk) starts without
extracted data, plan or collection. One invocation extracts synthetic source
bytes, computes the content-derived collection target and publishes it.
The [metric checkpoint](../../feasibility/metric-checkpoint.smk) starts without
responses, inventory, plan or metrics. One invocation simulates, inventories,
resolves the response-derived metric target and publishes it.

For each lifecycle, tests establish:

- Fresh dry-run explicitly reports the unresolved identity and `<TBD>` inputs,
  schedules only the pre-checkpoint producers and writes no plan.
- Real execution completes the exact expected producer set and final target
  within that invocation, using public checkpoint `.get()` and input functions.
- Forced same-content reuse preserves published bytes and reports reuse.
- Corrupt publications refuse and retain their bytes, both with an existing
  plan and after the rebuildable plan is removed.
- Corrupt plan identity refuses before job execution.
- Changed source/response bytes refuse in dry-run and execution even when their
  filesystem timestamps are restored, so a no-job DAG cannot hide staleness.

## Failures that changed the fixture

The first forced-reuse assertion also required unchanged mtime. Snakemake
refreshes timestamps after successful reuse, so that assumption was removed;
the accepted byte-preservation requirement was not relaxed.

`update(...)` protects existing output from pre-job removal but does not protect
it from failed-job cleanup. A deliberate corrupt-publication refusal inside
the job removed the existing file. Read-only invocation preflight now catches
that mismatch before scheduling. A further red case removed the rebuildable
plan: its callback initially reached the failing publisher and again lost the
file. Both post-checkpoint input callbacks now validate an existing publication
before returning its target, and the two lifecycle tests pass that case too.

These checks prove the tested invocation and callback boundaries. They do not
establish general rollback or preservation after concurrent mutation following
validation. No private API or upstream package was modified. Installed
`snakemake/jobs.py` corroborates the distinction: `remove_existing_output`
skips update-flagged outputs, whereas failed-job `cleanup` removes outputs.

## Verification and reproduction

Run from the existing Pixi environment, with a fresh scratch basetemp:

```powershell
pixi run --as-is python -m pytest tests/test_r12_wf3_feasibility.py -q --basetemp .tmp/scratchpad/<session>/p0-feasibility
```

The complete file passed **29 tests in 97.55 s**. After the final missing-plan
callback correction, the affected lifecycle cases were rerun with
`-k checkpoint_fresh_reuse_and_refusal`: **2 passed, 27 deselected in 39.09 s**.
The final check retains all prior lifecycle assertions plus the added red case.
Raw commands and complete per-case outputs remain in the session scratch
directories `p0-feasibility-final/` and `plan-loss-fixed/`; the latter is the
final checkpoint evidence. Earlier red logs are `runner-checkpoints.log` and
`plan-loss-red.log`. Retained evidence: [checkpoint transcript](checkpoint-transcript.txt) and
[test summaries](runner-checkpoint-checks.txt).

Verification budget: rapid / numerical unaffected for fixture code. Lint and
format-check passed (294 formatted files). The final repository CLI gate
`pixi run --as-is pytest tests/test_cli.py` passed **20 tests in 38.94 s**. No full suite was run: production code is unchanged.
