---
title: "Run summaries and WF4 benchmarking"
---

Every supported workflow launcher writes a readable summary at
`<project>/logs/<UTC timestamp>__<workflow scope>/summary.md`. An all-workflow run has one parent summary
covering its explicitly linked children; a standalone workflow has its own summary.
Different attempts keep separate folders. The runner's closing output links to the report.
See [execution logs and benchmarks](running.md#execution-logs-and-benchmarks) for the folder layout.

The source is `<project>/config/_engine/invocations/<id>.json`, not console output or
per-rule benchmark tables. Records retain numeric `elapsed_seconds` measured with a monotonic
clock, alongside UTC timestamps for chronology. The timer belongs to the launcher process;
a supervisor may supply an observed child duration, including preparation before child-record creation.
The total covers the recorded launcher attempt and is not the sum of parallel job durations.
No raw monotonic clock origin is stored. Time before invocation-record creation is not measured.

Reports distinguish execution from dry runs, disabled workflows, workflows not invoked, launch
failures and unfinished attempts. Warning counts appear only when recorded. Exit zero does not prove
that computation ran, outputs are complete or scientific results are adequate; `work_performed`
remains unknown unless the launcher has evidence. A no-op with every workflow disabled records no work.
Old records without elapsed seconds retain an unavailable duration; UTC differences are not substituted.

A report starts as a running snapshot and refreshes as the launcher observes children and completion.
A hard-killed attempt retains its last snapshot without a fabricated end time. Report-writing failures
are reported separately and preserve the original execution outcome. Structured invocation records
remain authoritative, including when a report is missing or stale.
Startup failures can be recorded once the project root is known. Supply `--project-dir` to
the all-workflow runner or WF4 runner to retain failures that occur while reading configuration.

## Workflow benchmark reports

Each invoked workflow writes `wfN-benchmarks.md` and `wfN-benchmarks.tsv` in its execution folder
when measurements are available. The Markdown report shows the recorded workflow elapsed time,
followed by a rule overview: distinct jobs, collected samples, summed job time, median and slowest
job, and peak individual-job RSS. Wildcard jobs are grouped under their rule. Repeated measurements
count as samples; per-job medians determine job-duration statistics so repeats do not inflate the sum.
Expand the detailed table for job identifiers and individual measurements, or use the adjacent TSV
for further analysis.

Summed job time is not workflow elapsed time: parallel jobs overlap and launcher overhead is separate.
Peak job RSS is not peak concurrent workflow memory. Missing or invalid measurements are unavailable,
never zero. Coverage remains unknown unless explicitly recorded; a successful attempt can reuse existing
outputs and collect few or no new benchmark samples. Partial failures retain the collected measurements
without claiming complete workflow coverage. Each retry starts with its own parts and reports.

WF4 reports also summarize available Julia timings: Wflow loading, compilation in the first observed
member of each Julia process, and later member wall times. These observations help distinguish startup
cost from sustained simulation speed. Missing phases remain unmeasured, and failed observations are
counted separately. First and later members refer to observations within each process.

## WF4 resource diagnostics

Resource sampling remains limited to WF4, automatically through either supported runner.
Dry runs do not start resource monitoring. No external monitoring service is used.

Find the WF4 child invocation in `<project>/config/_engine/invocations/<id>.json`.
Its `resources` field links to `<id>/diagnostics/` and summarizes elapsed time,
sampled CPU core use, peak process-tree RAM, minimum available system RAM and launcher phases.
Use the WF4 child ID, rather than the all-workflow parent ID.

| File | Evidence |
|---|---|
| `resources.jsonl` | Host context, timestamped resource samples, phase boundaries and final summary |
| `batch-*.json` | Batch selection, memory/core/disk constraints, requested threads and run membership |
| `julia-<pid>.tsv` | Package loading and per-member wall time, allocations, GC and compilation |

Resource samples are taken approximately every two seconds. They include the WF4 launcher and its
descendants, with process identities, CPU seconds, RSS, logical read/write counters, available
system RAM, swap counters, system CPU load, reported CPU frequency and power-source status.
Julia records its actual thread count; Snakemake can reduce the rule's requested count to fit its cores.
Process affinity and priority are recorded when first observed. Host context includes processor
information, physical/logical CPU counts, RAM capacity, free output-volume space and the Windows
power plan at startup. No process command lines or environment dumps are collected.

The launcher phases distinguish preparation, Snakemake execution, finalization and indicator exports.
Within Snakemake, correlate sample timestamps with rule logs and `wf4-benchmarks.md` in the execution
folder. Summed job durations are not workflow
wall time, and the table does not include all launcher overhead. Julia's first member includes its
cold compilation costs; later members provide a better comparison of sustained simulation speed.
Compilation and GC timings are components of wall time; do not add them to it. Allocated bytes measure
allocation traffic, not peak or retained RAM. A failed member records wall time with unavailable
allocation/GC/compilation fields left empty.

Treat these measurements as diagnostic evidence with explicit limits:

- Process CPU and I/O totals retain the last sample of exited processes, but miss children that start
  and exit between samples. Peaks are sampled. Summed RSS may count shared pages more than once.
- The initial process census excludes prior usage of existing processes. Descendants discovered later
  contribute their observed lifetime counters, without comparing process creation and wall-clock times.
  If the initial census is incomplete, first-observed counters are subtracted for all processes;
  this conservatively omits some work, with read failures recorded in the measurement errors.
- System CPU, swap and disk counters include other applications. Process I/O can include cached I/O;
  it does not directly measure physical storage throughput or I/O wait.
- Reported CPU MHz can be nominal on Windows. The trace cannot prove effective clock speed, thermal
  throttling or CPU temperature; those require platform-specific hardware profiling.
- Unavailable measurements appear as `null`; failed reads are counted, rather than reported as zero usage.
  Swap-in/out counters may remain zero on platforms that do not expose them.
- Samples are flushed during execution. A hard termination can leave a partial trace and a running
  invocation record. Only an observed completion produces a final summary.

The summary records sampler collection time so its cost can be inspected. Diagnostic failures emit
a warning and do not change the workflow result. Records belong to the invocation and do not modify
retained responses or indicator outputs. Existing runs cannot acquire historical resource evidence
retroactively. Instrumented simulation code remains subject to the normal code-identity guard; use
a new experiment when rerunning simulations after a code change.
