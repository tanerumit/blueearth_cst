"""Run a Windows child in a job that dies with its supervising parent.

The project lock is owned by the parent. A suspended child is assigned before
it can launch descendants, and closing the sole job handle kills the tree.
"""

import ctypes
import os
import shutil
import subprocess
from ctypes import wintypes
from pathlib import Path
from typing import Mapping, Sequence


class _BasicLimit(ctypes.Structure):
    _fields_ = [
        ("PerProcessUserTimeLimit", ctypes.c_longlong),
        ("PerJobUserTimeLimit", ctypes.c_longlong),
        ("LimitFlags", wintypes.DWORD),
        ("MinimumWorkingSetSize", ctypes.c_size_t),
        ("MaximumWorkingSetSize", ctypes.c_size_t),
        ("ActiveProcessLimit", wintypes.DWORD),
        ("Affinity", ctypes.c_size_t),
        ("PriorityClass", wintypes.DWORD),
        ("SchedulingClass", wintypes.DWORD),
    ]


class _IoCounters(ctypes.Structure):
    _fields_ = [
        (name, ctypes.c_ulonglong)
        for name in (
            "ReadOperationCount",
            "WriteOperationCount",
            "OtherOperationCount",
            "ReadTransferCount",
            "WriteTransferCount",
            "OtherTransferCount",
        )
    ]


class _ExtendedLimit(ctypes.Structure):
    _fields_ = [
        ("BasicLimitInformation", _BasicLimit),
        ("IoInfo", _IoCounters),
        ("ProcessMemoryLimit", ctypes.c_size_t),
        ("JobMemoryLimit", ctypes.c_size_t),
        ("PeakProcessMemoryUsed", ctypes.c_size_t),
        ("PeakJobMemoryUsed", ctypes.c_size_t),
    ]


def run_owned_child(
    command: Sequence[str], *, cwd: Path, env: Mapping[str, str]
) -> int:
    """Return child exit code; refuse if atomic job assignment is unavailable."""
    if os.name != "nt":
        raise OSError("Windows process-tree ownership is required for this launcher")
    import _winapi

    executable = shutil.which(command[0], path=env.get("PATH"))
    if executable is None:
        raise FileNotFoundError(f"project child executable not found: {command[0]}")

    kernel = ctypes.WinDLL("kernel32", use_last_error=True)
    kernel.CreateJobObjectW.argtypes = [ctypes.c_void_p, wintypes.LPCWSTR]
    kernel.CreateJobObjectW.restype = wintypes.HANDLE
    kernel.SetInformationJobObject.argtypes = [
        wintypes.HANDLE,
        ctypes.c_int,
        ctypes.c_void_p,
        wintypes.DWORD,
    ]
    kernel.SetInformationJobObject.restype = wintypes.BOOL
    kernel.AssignProcessToJobObject.argtypes = [wintypes.HANDLE, wintypes.HANDLE]
    kernel.AssignProcessToJobObject.restype = wintypes.BOOL
    kernel.CloseHandle.argtypes = [wintypes.HANDLE]
    kernel.CloseHandle.restype = wintypes.BOOL
    kernel.ResumeThread.argtypes = [wintypes.HANDLE]
    kernel.ResumeThread.restype = wintypes.DWORD
    job = kernel.CreateJobObjectW(None, None)
    if not job:
        raise ctypes.WinError(ctypes.get_last_error())
    try:
        limits = _ExtendedLimit()
        limits.BasicLimitInformation.LimitFlags = 0x00002000  # KILL_ON_JOB_CLOSE
        if not kernel.SetInformationJobObject(
            job, 9, ctypes.byref(limits), ctypes.sizeof(limits)
        ):
            raise ctypes.WinError(ctypes.get_last_error())
        process = thread = None
        try:
            process, thread, _, _ = _winapi.CreateProcess(
                executable,
                subprocess.list2cmdline(list(command)),
                None,
                None,
                False,
                0x00000004 | 0x00000400,  # SUSPENDED | UNICODE_ENVIRONMENT
                dict(env),
                str(cwd),
                subprocess.STARTUPINFO(),
            )
            if not kernel.AssignProcessToJobObject(job, int(process)):
                raise ctypes.WinError(ctypes.get_last_error())
            if kernel.ResumeThread(int(thread)) == 0xFFFFFFFF:
                raise ctypes.WinError(ctypes.get_last_error())
            _winapi.WaitForSingleObject(process, _winapi.INFINITE)
            return _winapi.GetExitCodeProcess(process)
        finally:
            if thread is not None:
                _winapi.CloseHandle(thread)
            if process is not None:
                _winapi.CloseHandle(process)
    finally:
        kernel.CloseHandle(job)


def run_project_child(
    command: Sequence[str], *, cwd: Path, env: Mapping[str, str], writing: bool = True
) -> int:
    """Run a project child, refusing unsupported writer lifetime semantics."""
    if os.name == "nt":
        return run_owned_child(command, cwd=cwd, env=env)
    if writing:
        raise OSError(
            "project writer descendants lack a verified lifetime guarantee on this platform"
        )
    return subprocess.run(command, cwd=cwd, env=env, check=False).returncode
