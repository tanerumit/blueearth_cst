# Windows socket-pair completion stall: bounded workaround

Date: 2026-10-30. Task: t2610291628. Implementation and checks belong to session-2,
branch `refactor/t2610241523c`; the commit containing this record identifies the candidate.

## Observed incident

The original task recorded a remote Windows 11 case, `wrt-egypt-v3`, at revision `20f62c8b`:
Python 3.12.13, six cores, `run_workflows.py` with `--rerun-incomplete`. Other workflows finished,
but WF2 repeatedly stopped advancing at 132/211 completed jobs. Fetch logs reported successful
basin-slice writes without scheduler completion messages; no separate Python fetch processes remained.

The main-thread stack was `_finish_jobs` → `async_run` → asyncio runner/event-loop creation →
Proactor `_make_self_pipe` → `socket._fallback_socketpair` → blocking `accept`. All six executor
callbacks waited for the scheduler lock in `report_job_success` → `_proceed`. The outer toolbox
runner waited for its Snakemake child. A TCP snapshot showed a listener at `127.0.0.1:60297` and an
unconnected bound socket at port 60298, without an established pair. A fresh process in the same
environment passed `socket.socketpair()`. Main `04c50f56` contained no launcher or lock-file fix
relative to the incident revision.

This evidence identifies the blocking operation, not the cause of the failed local connection.
Filtering, resource pressure and Python/Windows defects remain hypotheses. The suggested one-core
resume has no recorded outcome and is not an established fix.

## Implementation and upstream comparison

The installed Python 3.12.13 fallback and the inspected upstream
[Python 3.12 implementation](https://github.com/python/cpython/blob/3.12/Lib/socket.py)
start a nonblocking connect, ignore its in-progress exception, then call blocking `accept`.
The inspected [upstream main implementation](https://github.com/python/cpython/blob/main/Lib/socket.py)
retains that sequence. These sources did not establish an available upstream fix for this incident.

`blueearth_cst/shared/windows_socketpair.py` uses a synchronous connect with a five-second
connect/accept budget and three attempts for setup timeouts. Every failed attempt closes its
sockets. Peer-address authentication is preserved; unexpected peers and other socket errors are
not retried. Successful sockets leave setup with normal timeout semantics, without changing the
process-wide default or CMIP6 network timeouts.

`snakemake_console.main` installs the replacement temporarily only on Windows when Python's
fallback is the active `socket.socketpair`. CLI exit restores the original, including on errors.
This covers the owned runners' scheduler process, including verbose and dry-run modes. Native
implementations, direct `snakemake` launches and separate job processes are outside this workaround.
No installed dependency was edited.

## Verification

Environment: Windows, Pixi Python 3.12.13, Snakemake 9.6.2. Commands ran from session-2 with
`pixi run --frozen --no-install`; checks invoking Snakemake used normal user permissions in a
separate Herdr watch tab. All workflow inputs and outputs were test-owned temporary paths.

- `python -m pytest tests/test_windows_socketpair.py tests/test_snakemake_console.py -q`:
  27 passed in 28.12 seconds before adding the two completion/resume cases. Covers IPv4/IPv6
  exchange, connect/accept timeouts, transient recovery, persistent failure, socket cleanup,
  unexpected-peer rejection, platform/native scoping, restoration, 120 asyncio loops across six
  threads, terminal/file diagnostics, error statuses and existing launcher routing.
- `python -m pytest tests/test_snakemake_console.py -k parallel_completion -q`:
  two passed in 15.25 seconds. A synthetic 13-output DAG ran with six cores. Dropped connections
  were injected specifically during `_finish_jobs`, exercising the recorded scheduler-lock path.
  A single drop recovered; persistent drops exited with the three-attempt error. Both subsequent
  `--rerun-incomplete` invocations finished, preserving an existing output's bytes and mtime.
- `.tmp/tasks/t2610291628/reproduce.py`: the same dropped-connect injection left the original
  fallback blocked beyond the two-second subprocess limit; the test terminated that child.
  The workaround raised the expected three-attempt timeout and exited. This reproduces the
  failure mechanism deterministically, not the remote machine's unknown environmental trigger.
- Scoped `ruff check` and `ruff format --check` on the two implementation and two test modules
  passed; `git diff --check` passed.

- `python -m pytest tests/test_run_workflows.py tests/test_windows_job.py -q`:
  95 passed in 116.53 seconds. Covers all-workflow argument routing, workflow ordering,
  diagnostic/error handling and Windows child-process ownership. An earlier run was interrupted
  when its watch tab disappeared and supplied no completed result; this completed run replaces it.

The 27 socket/launcher cases, two subsequently added completion/resume cases and 95 consumer cases
total 124 passing tests. Logs and the standalone reproducer remain under
`.tmp/tasks/t2610291628/` in session-2; this record retains the results needed after scratch cleanup.

## Scope and remaining confirmation

Production outputs and the CMIP6 cache were untouched. No scientific calculation or workflow rule
changed. Focused engine execution exercises the shared launcher's failure and resume behavior;
no fresh basin computation or all-workflow scientific comparison was run.

Confirmation on the original remote machine remains outstanding. After its old process stops,
resume its preserved case through the owned runner with `--rerun-incomplete`. Retain fresh logs
and process stacks if another stall occurs. A different blocking operation requires fresh diagnosis.
Landing and push are held; the task remains open for integration and remote confirmation.
