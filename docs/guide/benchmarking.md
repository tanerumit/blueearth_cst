---
title: "Run summaries and WF4 benchmarking"
---

## Open the execution summary

1. Follow the runner's link to `logs/<UTC timestamp>__<workflow scope>/summary.md`.
   An all-workflow summary links its children; standalone workflows have their own summaries.
2. Check whether the attempt executed, previewed, failed or remained unfinished.
   A successful attempt may reuse outputs and collect no new job samples.
3. Use the linked `wfN-benchmarks.md` for the rule overview and `.tsv` for precise samples.
   A missing measurement is unavailable, not zero. A running snapshot is not a completed timing.

## Compare measurements correctly

- Workflow elapsed time covers the recorded launcher attempt; parallel job durations overlap.
  Do not sum job times and label the result workflow elapsed time.
- Rule summaries group jobs/samples and report median, slowest job and peak individual-job RAM.
  Peak job RAM is not peak concurrent workflow memory.
- WF4 Julia timings distinguish loading/first-member compilation from later-member wall time.
  Compilation and garbage collection are components of wall time, not additional elapsed time.
- Allocated bytes are allocation traffic, not retained or peak RAM.
- Old records without measured elapsed seconds remain unavailable; timestamp subtraction is not substituted.
- Partial attempts retain partial evidence; exit zero alone does not establish output completeness or skill.

## WF4 resource diagnostics

Only WF4 samples process resources. Dry runs do not start monitoring.
The WF4 child invocation's `resources` field links its diagnostic files; use the child, not the parent ID.
Read the trace with its workflow logs to distinguish preparation, simulation and indicator work.

Samples are approximately two seconds apart. Short-lived processes and unsampled peaks can be missed;
summed process RSS can count shared pages more than once. System counters include other applications,
and logical I/O can include cached operations. Reported CPU frequency does not establish thermal
throttling or effective speed. Missing values/errors stay explicit rather than becoming zero usage.
Historical runs cannot acquire resource evidence retroactively.

The [execution/provenance reference](../technical-manual/execution-and-provenance.md) owns exact files,
fields, collection limits and lifecycle. Use [running](running.md#execution-logs-and-benchmarks) to find logs.
