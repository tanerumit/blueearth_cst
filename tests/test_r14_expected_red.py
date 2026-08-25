"""The R14 bundle's declared-red set, checked rather than described.

**Why this file exists.** P1 flips the loader to `schema_version: 2`, so every
shipped `test_case/*.yml` — still v1 until P4 migrates them with the rewriter —
is now refused. That is the bundle working as designed (`K3`: the digest moves
ONCE, so nothing merges until the whole set is green together), but between P1
and P4 it leaves a suite with dozens of failures, and P2 runs in that gap.

A blanket red is not a gate. P2 touches the drift guard and
``CONFIG_PROJECTION`` — exactly what ``tests/test_cli.py`` catches — and with
the suite already red it would have no way to tell its own breakage from P1's
inheritance. So the red set is DECLARED here, as data, and this module asserts
the actual failures are exactly that set:

* a failure NOT in the list is a real regression, named;
* a listed case that PASSES is stale and must be removed, so the list cannot
  quietly grow into a permanent excuse.

**Delete this module in P4.** Once the shipped configs are v2 the list is empty
and the check is noise. P4's rung 1 is `pytest tests/test_cli.py`; when that is
green against the migrated sets, this file and
``tests/data/r14_expected_red.txt`` go with it. `test_the_list_is_not_empty`
below fails once P4 lands, which is the reminder.

Marked ``workflow_contract``: it runs a nested pytest over ~10 modules, so it
belongs in the tier that is run at gates rather than in ``test-fast``.
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
EXPECTED_RED = REPO_ROOT / "tests" / "data" / "r14_expected_red.txt"

#: Matches pytest's short-summary lines, from which the node id is the whole
#: first field. ERROR lines are collected too: a module that fails at COLLECT
#: time reports as an error and would otherwise slip past a FAILED-only filter.
_SUMMARY = re.compile(r"^(?:FAILED|ERROR)\s+(\S+)", re.MULTILINE)


def _declared() -> tuple[set[str], dict[str, str]]:
    """Return the declared node ids and the reason recorded against each."""
    nodes: set[str] = set()
    reasons: dict[str, str] = {}
    for line in EXPECTED_RED.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        node, _, reason = line.partition("  # ")
        nodes.add(node.strip())
        reasons[node.strip()] = reason.strip()
    return nodes, reasons


def _modules(nodes: set[str]) -> list[str]:
    """The distinct test modules the declared nodes live in."""
    return sorted({node.split("::", 1)[0] for node in nodes})


def test_every_declared_node_records_a_reason():
    """A bare node id is an excuse; a node id with a reason is a record.

    Cheap, and it runs without the nested pytest below, so a malformed list is
    diagnosed in milliseconds rather than after a three-minute run.
    """
    nodes, reasons = _declared()
    assert nodes, "the declared-red list is empty — see this module's docstring"
    missing = sorted(node for node in nodes if not reasons.get(node))
    assert not missing, (
        f"declared-red entries with no reason: {missing}. Write `<node id>  # "
        "<why it is red>` so a reader can tell an inherited failure from one "
        "that was waved through."
    )


def test_the_list_is_not_empty():
    """The reminder to DELETE this module, which fires when P4 lands.

    Once the shipped configs are v2 nothing here is red, the list empties, and
    this file becomes a check with nothing to check. Failing at that moment is
    the cheapest way to make sure it is removed rather than left behind as
    permanent scaffolding.
    """
    nodes, _ = _declared()
    assert nodes, (
        "the declared-red list is empty, which means the shipped configs are "
        "migrated. Delete tests/test_r14_expected_red.py and "
        "tests/data/r14_expected_red.txt — see this module's docstring."
    )


@pytest.mark.workflow_contract
def test_the_actual_red_set_is_exactly_the_declared_one():
    """The gate P2 inherits: fails EXACTLY the declared set, nothing more."""
    nodes, _ = _declared()
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "pytest",
            *_modules(nodes),
            "-q",
            "-p",
            "no:randomly",
            "--no-header",
            "-m",
            "not workflow_contract and not process_isolation",
        ],
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
    )
    combined = (result.stdout or "") + (result.stderr or "")
    actual = set(_SUMMARY.findall(combined))

    unexpected = sorted(actual - nodes)
    assert not unexpected, (
        "these failed and are NOT declared as inherited from P1's v2 flip — "
        f"treat them as regressions in the change you just made:\n  "
        + "\n  ".join(unexpected)
        + f"\n\n{combined[-3000:]}"
    )

    stale = sorted(nodes - actual)
    assert not stale, (
        "these are declared red but PASS now, so the declaration is stale — "
        "remove them from tests/data/r14_expected_red.txt rather than leaving "
        "the list as a growing allowance:\n  " + "\n  ".join(stale)
    )
