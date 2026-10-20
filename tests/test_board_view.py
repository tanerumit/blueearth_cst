"""Verify canonical Windows board links against real Git worktrees."""

from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path

import pytest

pytestmark = pytest.mark.skipif(
    os.name != "nt" or not shutil.which("pwsh"), reason="Windows board setup"
)
SCRIPT = Path(__file__).resolve().parents[1] / "dev/scripts/setup-board-view.ps1"


@pytest.fixture
def board(tmp_path: Path):
    """Create independent main/session checkouts using the working helper."""
    env = {
        key: value for key, value in os.environ.items() if not key.startswith("GIT_")
    }
    main = tmp_path / "main"
    lane = tmp_path / "session"
    main.mkdir()

    def git(root: Path, *args: str) -> str:
        return subprocess.run(
            ["git", "-C", str(root), *args],
            env=env,
            check=True,
            capture_output=True,
            text=True,
        ).stdout

    git(main, "init", "-b", "main")
    git(main, "config", "user.name", "Board Test")
    git(main, "config", "user.email", "board@example.invalid")
    git(main, "config", "commit.gpgsign", "false")
    git(main, "config", "core.hooksPath", str(tmp_path / "no-hooks"))
    (main / ".gitignore").write_text(".tmp/\n", encoding="utf-8")
    (main / "dev/tasks").mkdir(parents=True)
    (main / "dev/scripts").mkdir()
    shutil.copyfile(SCRIPT, main / "dev/scripts/setup-board-view.ps1")
    (main / "dev/TODO.md").write_text("original", encoding="utf-8")
    (main / "dev/tasks/item.md").write_text("original", encoding="utf-8")
    git(main, "add", ".")
    git(main, "commit", "-m", "seed")
    git(main, "worktree", "add", "-b", "session", str(lane))

    def setup(*args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [
                "pwsh",
                "-NoProfile",
                "-File",
                str(main / "dev/scripts/setup-board-view.ps1"),
                "-WorktreeRoot",
                str(lane),
                *args,
            ],
            env=env,
            check=check,
            capture_output=True,
            text=True,
        )

    setup("-ExcludeSnapshots")
    return main, lane, git, setup


def test_shared_board_preserves_scratch_and_survives_merge(board):
    main, lane, git, setup = board
    scratch = lane / "dev/tasks/work/.tmp/evidence.txt"
    scratch.parent.mkdir(parents=True)
    scratch.write_text("retain me", encoding="utf-8")
    setup("-LinkCanonicalBoard", "-CheckOnly")
    assert scratch.read_text() == "retain me"
    assert not (lane / "dev/TODO.md").exists()
    setup("-LinkCanonicalBoard")
    setup("-LinkCanonicalBoard")
    assert (lane / ".tmp/tasks/work/.tmp/evidence.txt").read_text() == "retain me"
    assert (lane / "dev/tasks").resolve() == (main / "dev/tasks").resolve()
    assert (lane / "dev/TODO.md").is_symlink()

    replacement = main / "dev/replacement.md"
    replacement.write_text("rendered", encoding="utf-8")
    replacement.replace(main / "dev/TODO.md")
    (main / "dev/tasks/new.md").write_text("new task", encoding="utf-8")
    assert (lane / "dev/TODO.md").read_text() == "rendered"
    assert (lane / "dev/tasks/new.md").read_text() == "new task"
    git(lane, "add", "-A")
    assert not git(lane, "status", "--porcelain")
    git(main, "add", "-A")
    git(main, "commit", "-m", "update board")
    # Main has newer uncommitted content when the session merges its commit.
    (main / "dev/tasks/item.md").write_text("live edit", encoding="utf-8")
    git(lane, "merge", "main")
    assert (lane / "dev/tasks/item.md").read_text() == "live edit"
    assert (lane / "dev/TODO.md").is_symlink()
    assert not git(lane, "status", "--porcelain")


@pytest.mark.parametrize("conflict", ["scratch", "ignore", "todo", "custom-sparse"])
def test_setup_refuses_conflicts_without_relocating_scratch(board, conflict: str):
    _, lane, git, setup = board
    scratch = lane / "dev/tasks/work/.tmp/evidence.txt"
    scratch.parent.mkdir(parents=True)
    scratch.write_text("retain me", encoding="utf-8")
    if conflict == "scratch":
        (lane / ".tmp/tasks").mkdir(parents=True)
    elif conflict == "ignore":
        (lane / "dev/.gitignore").write_text("user rules\n", encoding="utf-8")
    elif conflict == "todo":
        (lane / "dev/TODO.md").write_text("local copy", encoding="utf-8")
    else:
        git(lane, "sparse-checkout", "set", "--no-cone", "/*", "!/dev/tasks/")
    result = setup("-LinkCanonicalBoard", check=False)
    assert result.returncode != 0
    assert scratch.read_text() == "retain me"
    assert not (lane / "dev/tasks").is_junction()
