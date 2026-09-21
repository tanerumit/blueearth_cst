"""Atomic, common history for supported workflow launcher attempts."""

from __future__ import annotations

import json
import os
import re
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

PARENT_ENV = "CST_PARENT_INVOCATION_ID"
INVOCATION_ENV = "CST_INVOCATION_ID"
_SENSITIVE = re.compile(
    r"api[-_]?key|auth|credential|pass(?:word|wd)?|private[-_]?key|secret|token",
    re.IGNORECASE,
)


def sanitize_command(command: list[str]) -> list[str]:
    """Remove credential-like argument values from durable history."""
    result = []
    redact_next = False
    for token in command:
        if redact_next:
            result.append("<redacted>")
            redact_next = False
            continue
        key, separator, _ = token.partition("=")
        if _SENSITIVE.search(key.lstrip("-")):
            if separator:
                result.append(f"{key}=<redacted>")
            elif token.startswith("-"):
                result.append(token)
                redact_next = True
            else:
                result.append("<redacted>")
            continue
        result.append(token)
    return result


def _now() -> str:
    return (
        datetime.now(timezone.utc)
        .isoformat(timespec="milliseconds")
        .replace("+00:00", "Z")
    )


def _write(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.{uuid.uuid4().hex}.tmp")
    try:
        with temporary.open("x", encoding="utf-8", newline="\n") as handle:
            json.dump(value, handle, indent=2, sort_keys=True, ensure_ascii=False)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        for attempt in range(10):
            try:
                os.replace(temporary, path)
                break
            except PermissionError as error:
                # Windows readers and indexers can momentarily hold the old
                # file without delete sharing during a record refresh.
                if os.name != "nt" or error.winerror != 5 or attempt == 9:
                    raise
                time.sleep(0.02)
    finally:
        temporary.unlink(missing_ok=True)


def start(
    project_root: Path,
    *,
    workflow: str | None,
    entry_point: str,
    command: list[str],
    targets: list[str],
    mode: str,
    contract_mode: str,
    invocation_id: str | None = None,
    parent_invocation_id: str | None = None,
    requested_workflows: list[str] | None = None,
) -> tuple[Path, dict[str, Any]]:
    """Publish a running record before configuration validation or launch."""
    identity = invocation_id or uuid.uuid4().hex
    path = (
        project_root.resolve() / "config/runs/_engine/invocations" / f"{identity}.json"
    )
    if path.exists():
        raise ValueError(f"invocation already exists: {identity}")
    record: dict[str, Any] = {
        "schema_version": "invocation/1",
        "invocation_id": identity,
        "parent_invocation_id": parent_invocation_id,
        "workflow": workflow,
        "entry_point": entry_point,
        "command": sanitize_command(command),
        "targets": targets,
        "working_directory": str(Path.cwd()),
        "mode": mode,
        "contract_mode": contract_mode,
        "work_performed": "no" if mode == "dry_run" else "unknown",
        "status": "running",
        "exit_code": None,
        "started_at_utc": _now(),
        "ended_at_utc": None,
        "configuration": {
            "source_config_sha256": None,
            "effective_config_sha256": None,
            "configuration_inputs_sha256": None,
            "run_record": None,
            "archive_state": "unavailable",
        },
        "plan": None,
        "artifacts": [],
        "children": [],
        "requested_workflows": requested_workflows or [],
        "launch_failures": [],
        "error": None,
    }
    _write(path, record)
    return path, record


def update(path: Path, record: dict[str, Any]) -> None:
    """Atomically refresh a running record, including child linkage."""
    _write(path, record)


def finish(
    path: Path,
    record: dict[str, Any],
    *,
    exit_code: int | None,
    error: BaseException | None = None,
) -> None:
    """Finish only when a launcher observes an outcome, not on hard kill."""
    record["status"] = "succeeded" if error is None and exit_code == 0 else "failed"
    record["exit_code"] = exit_code
    record["ended_at_utc"] = _now()
    if error is not None:
        record["error"] = {
            "phase": "launch",
            "type": type(error).__name__,
            "message": str(error),
        }
    _write(path, record)
