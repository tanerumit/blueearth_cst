# WF2 scheduler stall diagnosis — 2026-10-07

Root cause remains unconfirmed. No concurrency default, benchmark, heartbeat, dependency, or installed
Snakemake code was changed. Do not treat serial recovery as proof of a fixed scheduler.

## Evidence and discrimination

- Original stalls: the retained [scheduler tails](stall-evidence.md) stop after job 116/256 and 121/140.
  Worker outputs/logs completed, with no scheduler children and no CPU accumulation over ten seconds.
- Third occurrence: session-1 scratch `wf2-suite-evidence/fresh-p0-run.log` ends at 20:54:12 on October 7,
  after job 179/257. Its last three fetches reused staged files; the following three reducers produced
  no scheduler DONE rows. The corresponding Snakemake file log
  `2026-10-07T202431.978396.snakemake.log` stops at `Select jobs to execute...` after 179/258 steps.
  Network fetching is therefore unnecessary for this symptom. This does not exclude local I/O stalls.
- `fresh-p0-resume.log` records a one-core recovery with 78 jobs, successful at 21:23:28. Recovery also
  changed the remaining DAG and restarted the process, so it is not a controlled concurrency bisect.
- Two bounded synthetic runs each completed 251 jobs (125 local shell fetch/reduce pairs plus `all`),
  three cores, benchmark/Windows psutil shim and console hook enabled, in approximately 31 and 28 seconds.
  They did not reproduce the reported stall. They omit WF2 script execution, netCDF work, long durations,
  archived-config setup and real input sizes; passing them does not establish production reliability.

The probes used session-1 commit `e1cc8cb4`, Windows, Python 3.12.13, Snakemake 9.6.2 and psutil 7.2.2.
Raw logs remain under session-1 `.tmp/scratchpad/wf2-scheduler-probe/`; the reproducible synthetic workflow
is retained as `Snakefile`. No remote fetch or large real ensemble was executed during this diagnosis.

## Ranked hypotheses

1. **Greedy selection/input inspection blocked.** Best fit to the last durable scheduler record.
   The installed CLI chooses greedy: `COIN_CMD` is unavailable and only `PULP_CBC_CMD` is available.
   Selection computes asynchronous job rewards under the scheduler lock.
2. **Postprocessing/DAG transition blocked.** These operations also hold the scheduler lock; completion
   callbacks then wait in `_proceed`. Complete outputs and absent children do not prove a lost callback.
3. **Executor callback/wait anomaly.** Requires worker and main-thread stacks to distinguish from (1)/(2).
4. **Console handler alone blocked.** Lower priority: the installed logger uses an unbounded queue, the
   file log stops too, and source inspection found no competing acquisition of `_emit_lock`.

These rankings are inferences from logs and installed source, not captured deadlock stacks. No upstream
defect has been established; no installed package was edited.

## Capture the next recurrence

The opt-in `capture/sitecustomize.py` is inherited by Python children of the owned launcher. It writes
per-PID metadata and UTC main-first snapshots, without recording frame locals or full command arguments.
It remains inactive without `CST_SCHEDULER_TRACE_DIR`. Use a fresh trace folder for each invocation.

Validated controls: a 122-thread process retained main first; synthetic scheduler snapshots included
actual `snakemake.scheduler.schedule` and worker/logging threads; an instrumented owned rapid dry-run
passed and recorded the child `snakemake.EXE` process and its workflow frames. An earlier direct-interpreter
owned dry-run exited -1 during imports; Pixi activation passed, so retain the documented Pixi invocation.
Helper lint (Ruff stdin), isolated format check and `py_compile` passed. Full suites and numerical gates
were omitted: this task changed only diagnostic evidence and an opt-in task helper, not runtime outputs.
The board check reported 67 errors and 26 warnings on other, unchanged task notes/folders; this task had
no reported findings. Its generated board row was reviewed as active with three of five steps complete.

`faulthandler` is a secondary C watchdog: Python documents a
[100-thread/100-frame limit](https://docs.python.org/3.12/library/faulthandler.html).
It omitted main in the first synthetic dump. The main-first Python monitor retains every enumerated
thread; if it cannot acquire the GIL, the watchdog remains useful but may truncate. Timer populations
grew during successful probes; their generic Timer stacks fit scheduler reevaluation timers, not
benchmark DaemonTimer stacks. That observation does not establish a leak or the cause of the stall.

From the occupied worktree, substitute the actual config, cached project and a fresh trace folder:

```powershell
$capture = 'C:/Users/taner/workspace/blueearth_cst/dev/tasks/t2610062309/capture'
$trace = Join-Path $PWD '.tmp/scratchpad/wf2-scheduler-capture-next'
$savedPythonPath = $env:PYTHONPATH
$env:PYTHONPATH = if ($savedPythonPath) { "$capture;$savedPythonPath" } else { $capture }
$env:CST_SCHEDULER_TRACE_DIR = $trace
$env:CST_SCHEDULER_TRACE_INTERVAL = '30'
try {
    pixi run python scripts/run_workflow.py analyze_projections `
        --config <project-config.yml> --project-dir <cached-project> --cores 3 `
        *> .tmp/scratchpad/wf2-scheduler-capture-next-run.log
} finally {
    $env:PYTHONPATH = $savedPythonPath
    Remove-Item Env:CST_SCHEDULER_TRACE_DIR -ErrorAction SilentlyContinue
    Remove-Item Env:CST_SCHEDULER_TRACE_INTERVAL -ErrorAction SilentlyContinue
}
```

For a DAG-only injection check, append `--dry-run`. For the retained synthetic workflow, use the same
capture environment and `pixi run python -m snakemake -s <task-folder>/Snakefile --cores 3 --scheduler greedy`.
Its outputs are fixed to the original session scratch root; use a fresh copy of the workflow with fresh
output/benchmark roots for repeat executions. Do not use raw Snakemake on a real project to bypass the
owned launcher. The helper shadows another `sitecustomize` if one is present; use it only for this
diagnostic invocation, and inspect which per-PID log belongs to the actual scheduler.

Before terminating any recurrence, retain at least two snapshots of the scheduler and its workers,
the scheduler log tail, child-process state and output/log timestamps. Classify the main blocking frame
first. Then change one factor at a time (one core, benchmark removed in a diagnostic workflow copy,
heartbeat removed in a diagnostic copy) using identical cached inputs and targets. No public switches
for disabling benchmarks/heartbeat were added or assumed.

## Improvement candidate

- Target: `python-discipline` (skill), hazards/debugging guidance.
- Gap: a nominal all-thread faulthandler dump can omit the process's main thread at high thread counts.
- Proposed rule: when diagnosing many-thread hangs, verify main-thread coverage; combine the C watchdog
  with main-first `sys._current_frames()` snapshots and report truncation/GIL limits.
- Evidence: the first successful 251-job probe exceeded 100 threads and omitted main; the revised capture
  retained actual scheduler frames and a separate 122-thread control passed.
- Scope: applies to Python concurrency diagnosis across projects, independent of WF2 or Windows.
- Suggested placement: `references/hazards.md`, a concurrency diagnostics subsection.
