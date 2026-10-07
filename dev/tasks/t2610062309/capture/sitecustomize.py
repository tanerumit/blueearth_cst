"""Opt-in scheduler diagnostics, inherited by the owned launcher's children."""

import os


def _start_capture() -> None:
    """Write main-first snapshots without changing scheduler or job behavior."""
    import atexit
    import datetime
    import faulthandler
    import json
    import sys
    import threading
    import traceback
    from pathlib import Path

    directory = Path(os.environ["CST_SCHEDULER_TRACE_DIR"])
    directory.mkdir(parents=True, exist_ok=True)
    interval = float(os.environ.get("CST_SCHEDULER_TRACE_INTERVAL", "30"))
    if interval <= 0:
        raise ValueError("CST_SCHEDULER_TRACE_INTERVAL must be positive")
    handle = (directory / f"python-{os.getpid()}.log").open("x", encoding="utf-8")
    handle.write(
        json.dumps(
            {
                "pid": os.getpid(),
                "parent_pid": os.getppid(),
                "executable": sys.executable,
                "python": sys.version,
                "entry_point": sys.argv[0],
                "started": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            }
        )
        + "\n"
    )
    handle.flush()
    stop = threading.Event()

    def snapshot() -> None:
        while not stop.wait(interval):
            frames = sys._current_frames()
            names = {thread.ident: thread.name for thread in threading.enumerate()}
            main = threading.main_thread().ident
            stamp = datetime.datetime.now(datetime.timezone.utc).isoformat()
            handle.write(f"\nSNAPSHOT {stamp} threads={len(frames)}\n")
            for ident in sorted(frames, key=lambda ident: (ident != main, ident)):
                handle.write(f"\nTHREAD {ident} {names.get(ident, 'unknown')}\n")
                traceback.print_stack(frames[ident], file=handle)
            handle.flush()

    monitor = threading.Thread(
        target=snapshot, name="cst-scheduler-stack-monitor", daemon=True
    )
    monitor.start()
    # Independent C watchdog if the Python monitor cannot acquire the GIL.
    # Its output may omit main above 100 threads; main-first snapshots are primary.
    faulthandler.dump_traceback_later(interval * 4, repeat=True, file=handle)

    def close() -> None:
        stop.set()
        faulthandler.cancel_dump_traceback_later()
        monitor.join(timeout=1)
        if not monitor.is_alive():
            handle.close()

    atexit.register(close)


if os.environ.get("CST_SCHEDULER_TRACE_DIR"):
    try:
        _start_capture()
    except Exception as error:  # diagnostic setup must not prevent execution
        import sys

        print(f"Scheduler stack capture could not start: {error}", file=sys.stderr)
