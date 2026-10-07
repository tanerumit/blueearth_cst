"""Exercise landing evidence through its public command line."""

import json
import subprocess
import sys
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parents[1] / "dev/scripts/verify_landing.py"


def _git(root, *args):
    return subprocess.run(["git", *args], cwd=root, check=True, capture_output=True)


@pytest.fixture
def repo(tmp_path):
    _git(tmp_path, "init")
    _git(tmp_path, "config", "user.email", "test@example.invalid")
    _git(tmp_path, "config", "user.name", "Test")
    (tmp_path / ".gitignore").write_text("evidence.json\n*.log\n", encoding="utf-8")
    for name in ("pixi.lock", "code.py", "guide.md", "input.txt"):
        (tmp_path / name).write_text("original\n", encoding="utf-8")
    _git(tmp_path, "add", ".")
    _git(tmp_path, "commit", "-m", "initial")
    return tmp_path


def _cli(root, *args):
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args], cwd=root, capture_output=True, text=True
    )


def _record(root, *extra, command=None):
    return _cli(
        root,
        "record",
        "--evidence",
        "evidence.json",
        "--gate",
        "suite",
        "--log",
        "gate.log",
        "--input",
        "input.txt",
        *extra,
        "--",
        *(command or [sys.executable, "-c", "print('passed')"]),
    )


@pytest.mark.parametrize(
    "fault",
    [
        None,
        "missing",
        "failed",
        "skipped",
        "schema",
        "log",
        "input",
        "environment",
        "full",
        "append",
    ],
)
def test_evidence_integrity(repo, fault):
    extra = ["--skipped"] if fault == "skipped" else []
    command = (
        [sys.executable, "-c", "raise SystemExit(2)"] if fault == "failed" else None
    )
    result = _record(repo, *extra, command=command)
    assert result.returncode == (1 if fault == "failed" else 0), result.stderr
    evidence = repo / "evidence.json"
    if fault in {"schema", "environment"}:
        data = json.loads(evidence.read_text())
        if fault == "schema":
            data["version"] = "invalid"
        else:
            data["environment"]["python_version"] = "other"
        evidence.write_text(json.dumps(data))
    if fault in {"log", "input"}:
        (repo / ("gate.log" if fault == "log" else "input.txt")).write_text("changed")
    if fault in {"full", "append"}:
        result = _cli(
            repo,
            "record",
            "--evidence",
            "evidence.json",
            "--gate",
            "test-full",
            "--log",
            "full.log",
            "--input",
            "input.txt",
            "--",
            sys.executable,
            "-c",
            "print(123)",
        )
        assert result.returncode == 0, result.stderr
    gate = (
        "absent" if fault == "missing" else "test-fast" if fault == "full" else "suite"
    )
    result = _cli(repo, "verify", "--evidence", "evidence.json", "--require-gate", gate)
    assert result.returncode == (0 if fault in {None, "full", "append"} else 1), (
        result.stderr
    )


@pytest.mark.parametrize(
    "change,allow,expected",
    [
        ("guide.md", True, 0),
        ("guide.md", False, 1),
        ("code.py", True, 1),
        ("dirty", False, 1),
    ],
)
def test_candidate_tree_boundaries(repo, change, allow, expected):
    assert _record(repo).returncode == 0
    name = "code.py" if change == "dirty" else change
    (repo / name).write_text("changed")
    if change != "dirty":
        _git(repo, "add", name)
        _git(repo, "commit", "-m", "change")
    args = ["--allow-path", name] if allow else []
    result = _cli(
        repo, "verify", "--evidence", "evidence.json", "--require-gate", "suite", *args
    )
    assert result.returncode == expected, result.stderr


@pytest.mark.parametrize("fault", ["dirty", "untracked", "during", "append-mismatch"])
def test_record_refuses_unstable_identity(repo, fault):
    if fault == "untracked":
        (repo / "untracked.py").write_text("pass")
    if fault == "dirty":
        (repo / "code.py").write_text("changed")
    if fault == "append-mismatch":
        assert _record(repo).returncode == 0
        (repo / "guide.md").write_text("changed")
        _git(repo, "add", "guide.md")
        _git(repo, "commit", "-m", "changed")
    command = (
        [
            sys.executable,
            "-c",
            "from pathlib import Path; Path('code.py').write_text('changed')",
        ]
        if fault == "during"
        else None
    )
    assert _record(repo, command=command).returncode == 1
