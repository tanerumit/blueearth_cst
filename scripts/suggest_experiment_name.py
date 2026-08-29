"""Write a suggested ``experiment_name`` into a config, only if absent.

R07 B8. Run once, deliberately, before the first climate-experiment run::

    python scripts/suggest_experiment_name.py test_case/project_config_baseline.yml

Reads ``project.project_dir``, slugifies its basename, appends today's date,
validates the result through the same grammar the workflow enforces, and writes
it to ``workflows.run_stress_test.experiment_name``.

**An existing value is never overwritten** — the command exits nonzero naming
the value already present. The experiment name is the directory every wf3
artifact hangs off, so silently changing it would strand a completed
experiment's outputs under a name nothing points at any more.

The name is NEVER generated at run time. A runtime timestamp would make every
invocation target a fresh ``experiments/<id>/``: nothing would ever be up to
date, incremental reruns would be impossible, ``--dry-run`` would mislead, and
the baseline gate would have no fixed path to check.

The config is edited as TEXT, one line, not round-tripped through
``yaml.safe_dump``. A dump discards every comment in the file: the shipped
template carries ~110 of them, and this command is the first thing a new user
runs against their copy, so dumping would delete the annotations they had just
been handed — including the ones telling them to run this. PyYAML cannot
preserve comments and a round-tripping parser is not worth a dependency here,
so the write is a targeted insertion whose result is verified by reloading it.
"""

from __future__ import annotations

import argparse
import os
import re
import sys
from collections.abc import Callable
from datetime import date
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from blueearth_cst.experiment.allocate import (  # noqa: E402
    ExperimentCollisionError,
    allocate_experiment_name,
)
from blueearth_cst.shared.snake_utils import (  # noqa: E402
    suggest_experiment_name,
    validate_experiment_name,
)

_KEY_RE = re.compile(r"^(\s*)experiment_name\s*:(.*)$")


def _is_skippable(line: str) -> bool:
    """A blank or comment line, which carries no indentation information."""
    stripped = line.strip()
    return not stripped or stripped.startswith("#")


def _indent_of(line: str) -> int:
    return len(line) - len(line.lstrip(" "))


def _target_config(cfg_path: Path, doc: dict) -> Path:
    """Return the run_stress_test settings file the project config points at.

    The command still TAKES the project config on the command line -- that is
    the file a user knows the name of, and the one they pass to Snakemake --
    but the key it writes belongs to the run_stress_test workflow, so it lands
    in that workflow's own file.

    A missing or unresolvable pointer fails with the same nothing-has-been-
    reserved posture the command already takes for an unwritable config.
    """
    stanza = (doc.get("workflows") or {}).get("run_stress_test") or {}
    declared = stanza.get("config_path")
    if not declared:
        raise ValueError(
            f"{cfg_path} declares no workflows.run_stress_test.config_path, so "
            "there is no settings file to write the name into. Create one and "
            "point the stanza at it; nothing has been reserved"
        )
    resolved = Path(os.path.expanduser(str(declared)))
    if not resolved.is_absolute():
        resolved = cfg_path.resolve().parent / resolved
    if not resolved.is_file():
        raise ValueError(
            f"workflows.run_stress_test.config_path names a file that does not "
            f"exist: {resolved} (resolved against {cfg_path.resolve().parent}). "
            "Nothing has been reserved"
        )
    return resolved


def _plan_edit(text: str) -> tuple[int, int, Callable[[str], list[str]]]:
    """Plan where a TOP-LEVEL ``experiment_name`` goes in the raw config text.

    Returns ``(index, n_replaced, render)``: replace ``n_replaced`` lines from
    ``index`` (0 to insert) with ``render(name)``. Deferring the name to a
    callable lets the plan be computed BEFORE the name is reserved, so a config
    this cannot edit leaves no orphaned ``experiments/<id>/`` behind.

    **Top-level since R13.** The key used to be spliced at
    ``workflows.run_stress_test.experiment_name`` inside the one project config.
    The command now edits that workflow's OWN settings file, where the key sits
    at column zero -- so the whole nested machinery is gone: finding the parent
    blocks, creating them when absent, matching the block's existing indent, and
    anchoring on a comment run inside it.

    That machinery would not merely have been dead. A workflow settings file has
    no ``workflows:`` key, so the old planner took its append-whole-path branch
    and wrote a THREE-LEVEL block into a file whose top level is already the
    workflow -- and the verifier, which built its expectation the same nested
    way, would have confirmed it. The command would have reported success while
    the composed config had no ``experiment_name`` at all.

    A *missing* key is not an error: it is appended at EOF, which is the
    behaviour ``tests/test_experiment_allocation.py`` pins.
    """
    lines = text.splitlines(keepends=True)
    nl = "\r\n" if "\r\n" in text else "\n"

    for i, line in enumerate(lines):
        if _is_skippable(line) or _indent_of(line) != 0:
            continue
        match = _KEY_RE.match(line)
        if not match:
            continue
        trailing = match.group(2)
        # Keep any trailing comment on the line being filled in.
        comment = (
            "  " + trailing[trailing.index("#") :].rstrip() if "#" in trailing else ""
        )
        eol = line[len(line.rstrip("\r\n")) :] or nl
        return i, 1, lambda name: [f"experiment_name: {name}{comment}{eol}"]

    pad = [] if not lines or lines[-1].endswith(("\n", "\r")) else [nl]
    return len(lines), 0, lambda name: pad + [f"experiment_name: {name}{nl}"]


def _write_experiment_name(path: Path, name: str) -> None:
    """Set ``experiment_name`` to ``name`` by editing the text of ``path``.

    Verifies by reloading: the edited text must parse to the original config
    with exactly this one key added. A text edit that produced anything else —
    invalid YAML, a key at the wrong depth, a clobbered neighbour — raises
    instead of writing, so the config is never left worse than it was found.
    """
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines(keepends=True)
    idx, n_replaced, render = _plan_edit(text)
    lines[idx : idx + n_replaced] = render(name)
    new_text = "".join(lines)

    # The expectation is the TOP-LEVEL key (R13 §12.3). Built the same way
    # the edit is planned, so a verifier that agreed with a wrong-depth write
    # cannot exist: the old `setdefault("workflows", ...)` chain reloaded a
    # bogus three-level block to exactly itself and passed.
    expected = yaml.safe_load(text) or {}
    expected["experiment_name"] = name
    if yaml.safe_load(new_text) != expected:
        raise ValueError(
            f"the edit to {path} did not reload to the expected config; "
            f"nothing was written. Set experiment_name: {name} by hand in "
            f"{path}"
        )
    path.write_text(new_text, encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "config",
        help="path to the PROJECT config YAML (the --configfile target). The "
        "name is written into the run_stress_test settings file this one "
        "points at, which is where that workflow's keys live",
    )
    ap.add_argument(
        "--date",
        default=None,
        metavar="YYYYMMDD",
        help="date stamp to append (default: today). Explicit values keep the "
        "command reproducible in tests and scripted setups",
    )
    ap.add_argument(
        "--name",
        default=None,
        metavar="NAME",
        help="use this experiment name instead of the generated suggestion. A "
        "name you choose is NEVER silently versioned: if it is already "
        "taken the command fails, where a generated one would become "
        "_v2. Validated by the same grammar the workflow enforces",
    )
    ap.add_argument(
        "--dry-run",
        action="store_true",
        help="print the suggestion and leave the config untouched. Reserves "
        "nothing, so the name it prints may be taken by the time you use "
        "it",
    )
    args = ap.parse_args(argv)

    cfg_path = Path(args.config)
    if not cfg_path.is_file():
        print(f"error: no such config: {cfg_path}", file=sys.stderr)
        return 2
    doc = yaml.safe_load(cfg_path.read_text(encoding="utf-8")) or {}

    try:
        project_dir = doc["project"]["project_dir"]
    except (KeyError, TypeError):
        print("error: config has no project.project_dir", file=sys.stderr)
        return 2

    stamp = args.date or date.today().strftime("%Y%m%d")
    try:
        if args.name is not None:
            name = validate_experiment_name(args.name, project_dir)
        else:
            name = suggest_experiment_name(project_dir, stamp)
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    # --dry-run reports the suggestion even when a value is already set: the
    # point of inspecting first is to SEE what would be proposed. It still
    # writes nothing.
    if args.dry_run:
        print(name)
        return 0

    # The file this command actually edits: the run_stress_test settings file
    # the project config points at. Resolved the same way the loader resolves
    # it -- relative to the project file's own directory (R13 D-8.4).
    try:
        target = _target_config(cfg_path, doc)
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    target_doc = yaml.safe_load(target.read_text(encoding="utf-8")) or {}
    if not isinstance(target_doc, dict):
        print(f"error: {target} does not parse to a mapping", file=sys.stderr)
        return 2
    existing = target_doc.get("experiment_name")
    if existing is not None:
        print(
            f"error: experiment_name is already set to {existing!r}; refusing "
            f"to overwrite (would have suggested {name!r}). Remove the key "
            f"first if you really want a new experiment directory.",
            file=sys.stderr,
        )
        return 1

    # Confirm the config is EDITABLE before reserving anything. Reservation is
    # a side effect on disk; failing after it would leave an experiments/<id>/
    # nothing points at, for a config we then could not write to anyway.
    try:
        _plan_edit(target.read_text(encoding="utf-8"))
    except ValueError as exc:
        print(
            f"error: cannot edit {target}: {exc}. Nothing was reserved or "
            f"written; add experiment_name to {target} by hand",
            file=sys.stderr,
        )
        return 2

    # Reserve BEFORE writing the config: an atomic mkdir claims the name, so
    # two sessions creating experiments at the same moment cannot both believe
    # they own it. A user-supplied collision is an error; a generated one is
    # versioned to _v2, _v3 (R9 P4 commit 4).
    try:
        name = allocate_experiment_name(
            project_dir, name, user_supplied=args.name is not None
        )
    except ExperimentCollisionError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    try:
        _write_experiment_name(target, name)
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    print(f"wrote experiment_name: {name} to {target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
