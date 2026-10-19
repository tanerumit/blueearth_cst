---
title: "Benchmarking WF4"
---

WF4 records resources automatically during execution through either supported runner.
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
Within Snakemake, correlate sample timestamps with rule logs and the existing job benchmarks under
`<project>/benchmarks/`. Those benchmark totals sum job durations: parallel job time is not workflow
wall time, and the table does not include all launcher overhead. Julia's first member includes its
cold compilation costs; later members provide a better comparison of sustained simulation speed.
Compilation and GC timings are components of wall time; do not add them to it. Allocated bytes measure
allocation traffic, not peak or retained RAM. A failed member records wall time with unavailable
allocation/GC/compilation fields left empty.

Treat these measurements as diagnostic evidence with explicit limits:

- Process CPU and I/O totals retain the last sample of exited processes, but miss children that start
  and exit between samples. Peaks are sampled. Summed RSS may count shared pages more than once.
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
