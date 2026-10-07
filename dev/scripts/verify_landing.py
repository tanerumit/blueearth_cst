"""Record gate evidence and verify its reuse without executing another gate.

Run from the checkout root. Evidence and logs should live in ignored scratch.
A successful command is not proof that required checks ran: the gate owner must
inspect skips and mark wholly skipped commands with --skipped.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
import subprocess
import sys
from pathlib import Path


class EvidenceError(ValueError):
    """Evidence cannot establish the requested gate."""


def _git(*args: str) -> str:
    return subprocess.run(
        ["git", *args], check=True, capture_output=True, text=True
    ).stdout.strip()


def _hash(path: Path) -> str:
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def _identity() -> dict:
    if _git("status", "--porcelain"):
        raise EvidenceError("Checkout has dirty or nonignored untracked files")
    return {
        "commit": _git("rev-parse", "HEAD"),
        "tree": _git("rev-parse", "HEAD^{tree}"),
        "environment": {
            "pixi_lock_sha256": _hash(Path("pixi.lock")),
            "python_executable": str(Path(sys.executable).resolve()),
            "python_version": platform.python_version(),
            "platform": platform.platform(),
        },
    }


def _inputs(paths: list[str]) -> dict[str, str]:
    return {str(Path(path).resolve()): _hash(Path(path)) for path in paths}


def _load(path: Path) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    if (
        not isinstance(data, dict)
        or type(data.get("version")) is not int
        or data.get("version") != 1
    ):
        raise EvidenceError("Unsupported evidence schema")
    for field in ("commit", "tree"):
        if not isinstance(data.get(field), str) or not data[field]:
            raise EvidenceError(f"Invalid {field}")
    for field in ("environment", "inputs"):
        values = data.get(field)
        if not isinstance(values, dict) or any(
            not isinstance(key, str) or not isinstance(value, str)
            for key, value in values.items()
        ):
            raise EvidenceError(f"Invalid {field}")
    if set(data["environment"]) != {
        "pixi_lock_sha256",
        "python_executable",
        "python_version",
        "platform",
    }:
        raise EvidenceError("Invalid environment fields")
    gates = data.get("gates")
    if not isinstance(gates, dict):
        raise EvidenceError("Invalid gates")
    for name, gate in gates.items():
        if not isinstance(name, str) or not name or not isinstance(gate, dict):
            raise EvidenceError("Invalid gate")
        if (
            type(gate.get("exit_code")) is not int
            or gate.get("status") not in ("passed", "failed", "skipped")
            or not isinstance(gate.get("command"), list)
            or not gate["command"]
            or any(not isinstance(arg, str) for arg in gate["command"])
            or not isinstance(gate.get("log"), str)
            or not isinstance(gate.get("log_sha256"), str)
        ):
            raise EvidenceError(f"Invalid gate {name}")
    return data


def _record(args: argparse.Namespace) -> int:
    identity = _identity()
    inputs = _inputs(args.input)
    evidence = Path(args.evidence).resolve()
    log = Path(args.log).resolve()
    command = args.command
    if command and command[0] == "--":
        command = command[1:]
    if not command:
        raise EvidenceError("Record needs an explicit command after --")
    if not args.gate.strip():
        raise EvidenceError("Gate name must not be empty")
    if evidence == log or str(log) in inputs or str(evidence) in inputs:
        raise EvidenceError("Evidence, log and inputs must be distinct")
    data = {"version": 1, **identity, "inputs": inputs, "gates": {}}
    if evidence.exists():
        data = _load(evidence)
        if any(
            data[key] != value for key, value in {**identity, "inputs": inputs}.items()
        ):
            raise EvidenceError("Existing evidence has a different identity")
    if log.exists():
        raise EvidenceError("Log already exists; use a fresh log path")
    evidence.parent.mkdir(parents=True, exist_ok=True)
    log.parent.mkdir(parents=True, exist_ok=True)
    with log.open("xb") as stream:
        result = subprocess.run(command, stdout=stream, stderr=subprocess.STDOUT)
    if _identity() != identity or _inputs(args.input) != inputs:
        raise EvidenceError("Checkout, environment or inputs changed during the gate")
    status = "failed" if result.returncode else "skipped" if args.skipped else "passed"
    data["gates"][args.gate] = {
        "command": command,
        "exit_code": result.returncode,
        "status": status,
        "log": str(log),
        "log_sha256": _hash(log),
    }
    evidence.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    print(f"Recorded {args.gate}: {status}")
    return int(result.returncode != 0)


def _verify(args: argparse.Namespace) -> int:
    data = _load(Path(args.evidence))
    current = _identity()
    if current["environment"] != data["environment"]:
        raise EvidenceError("Environment identity differs")
    if _inputs(list(data["inputs"])) != data["inputs"]:
        raise EvidenceError("Input identity differs")
    if _git("rev-parse", f"{data['commit']}^{{tree}}") != data["tree"]:
        raise EvidenceError("Recorded commit/tree disagree")
    allowed = set(args.allow_path)
    for path in allowed:
        if Path(path).suffix.lower() != ".md" or "*" in path or "?" in path:
            raise EvidenceError("Allowed changes must be exact Markdown paths")
    if current["tree"] != data["tree"]:
        changed = set(
            _git(
                "diff", "--name-only", "--no-renames", data["commit"], "HEAD"
            ).splitlines()
        )
        if not changed <= allowed:
            raise EvidenceError(
                f"Candidate changed unallowed paths: {sorted(changed - allowed)}"
            )
        # Deletion/rename loses evidence context even when its old path is allowed.
        if _git("diff", "--name-only", "--diff-filter=D", data["commit"], "HEAD"):
            raise EvidenceError("Documentation deletions are not reusable")
    for name in args.require_gate:
        gate = data["gates"].get(name)
        if name == "test-fast" and (
            gate is None or gate["status"] != "passed" or gate["exit_code"] != 0
        ):
            gate = data["gates"].get("test-full")
        if gate is None or gate["status"] != "passed" or gate["exit_code"] != 0:
            raise EvidenceError(f"Required gate did not pass: {name}")
        if _hash(Path(gate["log"])) != gate["log_sha256"]:
            raise EvidenceError(f"Gate log changed: {name}")
    print("Required evidence verified; no gates executed")
    return 0


def main(argv: list[str] | None = None) -> int:
    """Run the record or verify command, reporting refusals with exit status 1."""
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="operation", required=True)
    record = sub.add_parser("record")
    record.add_argument("--evidence", required=True)
    record.add_argument("--gate", required=True)
    record.add_argument("--log", required=True)
    record.add_argument("--input", action="append", default=[])
    record.add_argument("--skipped", action="store_true")
    record.add_argument("command", nargs=argparse.REMAINDER)
    verify = sub.add_parser("verify")
    verify.add_argument("--evidence", required=True)
    verify.add_argument("--require-gate", action="append", required=True)
    verify.add_argument("--allow-path", action="append", default=[])
    args = parser.parse_args(argv)
    try:
        return _record(args) if args.operation == "record" else _verify(args)
    except (
        EvidenceError,
        OSError,
        subprocess.CalledProcessError,
        json.JSONDecodeError,
    ) as error:
        print(f"Evidence refused: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
