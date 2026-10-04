"""The project board wrapper always resolves the canonical main worktree."""

import importlib.util
import subprocess
import sys
from pathlib import Path

import pytest

_SCRIPT = Path(__file__).resolve().parents[1] / "dev/scripts/todoboard.py"
_SPEC = importlib.util.spec_from_file_location("todoboard_wrapper", _SCRIPT)
assert _SPEC and _SPEC.loader
wrapper = importlib.util.module_from_spec(_SPEC)
sys.modules[_SPEC.name] = wrapper
_SPEC.loader.exec_module(wrapper)


def test_board_root_is_main_even_when_another_worktree_is_first(monkeypatch, tmp_path):
    # A fake `main` worktree, not this checkout: session worktrees sparse-exclude
    # `dev/tasks/` (the board lives only in the primary), so the test's own root
    # would fail the wrapper's dev/tasks/ check wherever the suite runs from one.
    main = tmp_path / "primary"
    (main / "dev" / "tasks").mkdir(parents=True)
    output = (
        "worktree C:/other/session-1\n"
        "branch refs/heads/feat/example\n\n"
        f"worktree {main}\n"
        "branch refs/heads/main\n\n"
    )
    monkeypatch.setattr(
        wrapper.subprocess,
        "run",
        lambda *args, **kwargs: subprocess.CompletedProcess(args, 0, output, ""),
    )
    assert wrapper.main_board_root() == main


def test_board_root_fails_closed_without_a_main_worktree(monkeypatch):
    output = "worktree C:/other/session-1\nbranch refs/heads/feat/example\n\n"
    monkeypatch.setattr(
        wrapper.subprocess,
        "run",
        lambda *args, **kwargs: subprocess.CompletedProcess(args, 0, output, ""),
    )
    with pytest.raises(SystemExit, match="exactly one `main` worktree"):
        wrapper.main_board_root()


@pytest.mark.parametrize("arg", ["--root", "--root=elsewhere"])
def test_explicit_root_cannot_redirect_the_project_board(monkeypatch, arg):
    monkeypatch.setattr(sys, "argv", ["todoboard.py", arg, "list"])
    with pytest.raises(SystemExit, match="board root is the `main` worktree"):
        wrapper.main()
