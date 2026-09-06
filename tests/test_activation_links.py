"""The half of the activation check that holds on a bare checkout.

`dev/scripts/check_activation.py` compares the tracked activation record
against the agent symlink farms. Those farms are gitignored per-user state a
fresh clone does not have, so only two of its three checks can be a CI gate:
the Markdown links under `dev/reference/`, and the set parser itself.

The parser is tested on synthetic input rather than on the real record. The
2026-08-14 rename lesson applies directly: three tests globbed a pattern that
matched nothing after a rename and kept passing while checking an empty set. A
parser proven only against a document that currently happens to parse would do
the same the moment the document is reformatted.
"""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "dev" / "scripts"))
import check_activation as ca  # noqa: E402


def test_reference_docs_have_no_broken_relative_links():
    problems = ca.check_links()
    assert not problems, "\n".join(problems)


def test_the_record_still_names_the_sets_the_checker_looks_for():
    """A rename of the record's headings must not silently disable the check.

    Without this, reformatting the bullets would make `check_names` find no
    sets to compare and report "ok" while comparing nothing.
    """
    sets = ca._named_sets(ca.RECORD.read_text(encoding="utf-8"))
    assert "roles" in sets
    assert "manifest-explicit" in sets
    assert len(sets["roles"]) >= 9
    assert len(sets["manifest-explicit"]) >= 9


def test_wrapped_bullets_are_read_whole():
    """A set long enough to wrap must not be read as only its first line."""
    doc = (
        "- **Roles (3):** `alpha`, `beta`,\n"
        "  `gamma`.\n"
        "- **Manifest-explicit (1):** `delta`.\n"
    )
    sets = ca._named_sets(doc)
    assert sets["roles"] == ["alpha", "beta", "gamma"]
    assert sets["manifest-explicit"] == ["delta"]


def test_an_indented_block_after_a_list_is_not_absorbed_into_it():
    """Continuation stops at the first non-indented, non-bullet line.

    Otherwise a code block or wrapped paragraph placed after a list would have
    its backticked words read as members of the last bullet's set.
    """
    doc = (
        "- **Roles (1):** `alpha`.\n"
        "\n"
        "Prose in between.\n"
        "\n"
        "  `not-a-role` appears in an indented block.\n"
    )
    assert ca._named_sets(doc)["roles"] == ["alpha"]


def test_the_claude_scope_count_is_stated_and_matches_the_farm():
    """The one claim no name comparison covers.

    Claude scope is explicit + every promoting `always` binding, so it moves
    when a ROLE changes and the manifest does not. The record states it only
    as a count; if that count stops being parseable the check goes quiet.
    """
    counts = ca._stated_counts(ca.RECORD.read_text(encoding="utf-8"))
    assert "claude main-thread scope" in counts
    assert counts["claude main-thread scope"] >= counts["manifest-explicit"]


def test_a_broken_link_is_reported(tmp_path, monkeypatch):
    """The link check must fail on a bad link, not just pass on a good tree."""
    (tmp_path / "a.md").write_text("see [x](./nope.md)", encoding="utf-8")
    monkeypatch.setattr(ca, "REFERENCE_DIR", tmp_path)
    monkeypatch.setattr(ca, "REPO_ROOT", tmp_path)
    assert ca.check_links() == ["a.md: broken link -> ./nope.md"]
