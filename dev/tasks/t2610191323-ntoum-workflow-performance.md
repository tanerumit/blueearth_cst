---
title: Investigate WF4 and WF2 performance from the Ntoum run
type: todo-item
status: backlog
effort: 2
area: runtime
queue:
created: 2026-10-19
updated: 2026-10-19
---

> [!note] Overview
> **What changes** — Identify WF4 and WF2 bottlenecks and propose measured optimizations.
> **Why it matters** — These workflows account for about 87% of the 85-minute Ntoum batch.
> **What it takes** — Inspect retained traces first, then test scheduling, compilation and remote I/O causes.

## Progress

- [x] Confirm evidence sufficiency — invocation timings, benchmarks and WF4 resource/Julia traces exist.
- [ ] Check WF4 memory-policy limits, batch scheduling and available-memory conditions.
- [ ] Separate Julia compilation, steady member runtime and indicator-export costs.
- [ ] Separate WF2 remote-read waits, process startup and concurrency costs.
- [ ] Run focused controlled comparisons and rank optimizations by measured gains and output equivalence.

## Evidence and limits

Run root: `C:/Users/taner/workspace/cst-cases/runs/gabon-ntoum-v2`.
Successful invocation: `1568406955d34bef83db4bc297402304`; report: `benchmarks/run-<id>.md`.
WF4 diagnostics: `config/_engine/invocations/97a4b7b1c1a24476b0903b6e2814c0f1/diagnostics/`.

Measured on 2026-10-19:

- Batch: 5,115 s; WF4: 2,873 s; WF2: 1,588 s. WF4 indicator exports: 124 s.
- WF4: one thread, one 14-run batch; memory policy limited parallelism with 2.4 GB available.
  Actual memory exhaustion is unproven.
- First Julia member: 345 s, including 212 s compilation; later members: roughly two minutes.
- WF2: 25 fetch jobs accumulated 2,708 wall-clock job-seconds and 739 CPU-seconds.
  Waiting is inferred; its cause remains unseparated.

Limits: resumed batch with WF0 reuse, not a cold baseline; work-performed fields unknown.
Verify reuse from logs/artifacts. Summed job durations differ from workflow elapsed time.
Detailed resource sampling covers WF4 only. Establish speedups through controlled repeats;
preserve scientific outputs and record power/background load.

## Related work

- [Julia startup/sysimage assessment](t2609251025-wflow-sysimage-to-remove-per-batch-julia-startup.md).
- [Bounded-window WF4 forcing](t2610091737-bounded-window-forcing.md).
- [WF2 scheduler stalls](t2610062309-snakemake-scheduler-stalls-mid-run-on-long-wf2-fetch-batches.md)
  remain a separate unresolved failure.
