"""Exercise the installed hook against real staged changes in disposable repositories."""

from __future__ import annotations

import os
import subprocess
from pathlib import Path

import pytest

HOOKS = Path(__file__).resolve().parents[1] / ".githooks"


@pytest.mark.parametrize("name", ["pre-commit", "pre-push"])
def test_installed_hooks_are_tracked_as_executable(name: str):
    environment = {
        key: value for key, value in os.environ.items() if not key.startswith("GIT_")
    }
    result = subprocess.run(
        ["git", "ls-files", "--stage", f".githooks/{name}"],
        cwd=HOOKS.parent,
        env=environment,
        text=True,
        capture_output=True,
        check=True,
    )
    assert result.stdout.split()[0] == "100755"


@pytest.fixture
def repository(tmp_path: Path):
    """Isolate Git context while preserving normal executable discovery."""
    environment = {
        key: value for key, value in os.environ.items() if not key.startswith("GIT_")
    }

    def git(*args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            ["git", *args],
            cwd=tmp_path,
            env=environment,
            text=True,
            capture_output=True,
            check=check,
        )

    git("init", "-b", "main")
    git("config", "user.name", "Hook Test")
    git("config", "user.email", "hook@example.invalid")
    git("config", "commit.gpgsign", "false")
    git("config", "core.hooksPath", HOOKS.as_posix())
    task = tmp_path / "dev/tasks/example/design.md"
    task.parent.mkdir(parents=True)
    task.write_text("Original design\n", encoding="utf-8")
    git("add", ".")
    git("commit", "-m", "Seed canonical task")
    return tmp_path, git, task


@pytest.mark.parametrize("change", ["add", "modify", "delete", "rename"])
def test_task_changes_rejected_outside_main(repository, change: str):
    root, git, task = repository
    git("switch", "-c", "feature")
    if change == "add":
        (task.parent / "another design.md").write_text("New\n", encoding="utf-8")
    elif change == "modify":
        task.write_text("Changed\n", encoding="utf-8")
    elif change == "delete":
        task.unlink()
    else:
        task.rename(root / "moved.md")
    git("add", "-A")
    before = git("rev-parse", "HEAD").stdout
    result = git("commit", "-m", "Wrong checkout", check=False)
    assert result.returncode != 0
    assert "Task documents and board state belong to main" in result.stderr
    assert git("rev-parse", "HEAD").stdout == before
    assert git("diff", "--cached", "--name-only").stdout


@pytest.mark.parametrize("path", ["dev/TODO.md", "dev/LOG.md"])
def test_board_changes_rejected_when_detached(repository, path: str):
    root, git, _ = repository
    git("switch", "--detach")
    (root / path).write_text("Board change\n", encoding="utf-8")
    git("add", path)
    result = git("commit", "-m", "Detached board change", check=False)
    assert result.returncode != 0
    assert "Task documents and board state belong to main" in result.stderr


def test_main_task_changes_and_feature_code_remain_allowed(repository):
    root, git, task = repository
    task.write_text("Canonical update\n", encoding="utf-8")
    git("add", ".")
    git("commit", "-m", "Update on main")
    git("switch", "-c", "feature")
    (root / "implementation.txt").write_text("Implementation\n", encoding="utf-8")
    git("add", ".")
    git("commit", "-m", "Implement on feature")


@pytest.mark.parametrize("edit_after_merge", [False, True])
def test_merge_imports_canonical_tasks_without_allowing_edits(
    repository, edit_after_merge
):
    root, git, task = repository
    git("switch", "-c", "feature")
    (root / "implementation.txt").write_text("Implementation\n", encoding="utf-8")
    git("add", ".")
    git("commit", "-m", "Implement on feature")
    git("switch", "main")
    task.write_text("Canonical update\n", encoding="utf-8")
    git("add", ".")
    git("commit", "-m", "Update on main")
    git("switch", "feature")
    git("merge", "--no-ff", "--no-commit", "main")
    if edit_after_merge:
        task.write_text("Unauthorized session edit\n", encoding="utf-8")
        git("add", ".")
    result = git("commit", "-m", "Synchronize main", check=False)
    assert (result.returncode != 0) == edit_after_merge
    if edit_after_merge:
        assert "Task documents and board state belong to main" in result.stderr
    else:
        assert task.read_text(encoding="utf-8") == "Canonical update\n"
