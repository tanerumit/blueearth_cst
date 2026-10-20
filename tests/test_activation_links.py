"""Check manifest-owned activation and current-reference navigation."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "dev" / "scripts"))
import check_activation as ca  # noqa: E402


def test_reference_docs_have_no_broken_relative_links():
    problems = ca.check_links()
    assert not problems, "\n".join(problems)


def test_manifest_is_the_only_declaration_source(tmp_path, monkeypatch):
    manifest = tmp_path / "manifest.yml"
    manifest.write_text("roles: [alpha]\nskills: [beta]\n", encoding="utf-8")
    monkeypatch.setattr(ca, "MANIFEST", manifest)
    assert ca._declared_sets() == {"roles": ["alpha"], "manifest-explicit": ["beta"]}
    manifest.write_text("roles: [gamma]\nskills: [delta]\n", encoding="utf-8")
    assert ca._declared_sets() == {"roles": ["gamma"], "manifest-explicit": ["delta"]}


@pytest.mark.parametrize(
    "document", ["[]", "roles: []\nskills: [beta]", "roles: [3]\nskills: [beta]"]
)
def test_malformed_manifest_is_not_an_empty_success(tmp_path, monkeypatch, document):
    manifest = tmp_path / "manifest.yml"
    manifest.write_text(document, encoding="utf-8")
    monkeypatch.setattr(ca, "MANIFEST", manifest)
    with pytest.raises(ValueError):
        ca._declared_sets()


def test_activation_reports_drift_from_manifest(tmp_path, monkeypatch):
    manifest = tmp_path / "manifest.yml"
    manifest.write_text("roles: [alpha]\nskills: [beta]\n", encoding="utf-8")
    for directory, names in {
        ".claude/agents": ["wrong.md"],
        ".claude/skills": ["role-only"],
        ".agents/skills": ["extra"],
    }.items():
        parent = tmp_path / directory
        parent.mkdir(parents=True)
        for name in names:
            (parent / name).touch()
    monkeypatch.setattr(ca, "MANIFEST", manifest)
    monkeypatch.setattr(ca, "REPO_ROOT", tmp_path)
    problems, checked = ca.check_names()
    assert checked
    assert any("alpha" in problem for problem in problems)
    assert any("beta" in problem for problem in problems)
    assert any("wrong" in problem for problem in problems)
    assert any("extra" in problem for problem in problems)


def test_activation_skips_absent_runtime_trees(tmp_path, monkeypatch):
    monkeypatch.setattr(ca, "REPO_ROOT", tmp_path)
    assert ca.check_names() == ([], False)


@pytest.mark.parametrize(
    ("home", "reason"),
    [("tasks", "transient"), ("records/reviews", "prunable")],
)
@pytest.mark.parametrize("exists", [False, True])
def test_reference_links_reject_unstable_homes(
    tmp_path, monkeypatch, home, reason, exists
):
    reference = tmp_path / "dev/reference"
    reference.mkdir(parents=True)
    target = tmp_path / "dev" / home / "evidence.md"
    if exists:
        target.parent.mkdir(parents=True)
        target.write_text("Evidence", encoding="utf-8")
    (reference / "guide.md").write_text(
        f"[evidence](../{home}/evidence.md)", encoding="utf-8"
    )
    monkeypatch.setattr(ca, "REFERENCE_DIR", reference)
    monkeypatch.setattr(ca, "REPO_ROOT", tmp_path)
    problems = ca.check_links()
    assert len(problems) == 1
    assert reason in problems[0]


def test_retained_review_citations_still_require_their_target(tmp_path, monkeypatch):
    reference = tmp_path / "dev/reference"
    reference.mkdir(parents=True)
    target = tmp_path / "dev/records/reviews/plot-improvements/verification.md"
    target.parent.mkdir(parents=True)
    target.write_text("Retained verification", encoding="utf-8")
    for name in ("toolbox-plot-style.md",):
        (reference / name).write_text(
            "[verification](../records/reviews/plot-improvements/verification.md)",
            encoding="utf-8",
        )
    monkeypatch.setattr(ca, "REFERENCE_DIR", reference)
    monkeypatch.setattr(ca, "REPO_ROOT", tmp_path)
    assert ca.check_links() == []
    target.unlink()
    assert len(ca.check_links()) == 1
    assert all("broken link" in problem for problem in ca.check_links())


def test_durable_links_and_similarly_named_homes_are_allowed(tmp_path, monkeypatch):
    reference = tmp_path / "dev/reference"
    reference.mkdir(parents=True)
    for home in ("records/decisions", "tasks-archive", "records/reviews-archive"):
        target = tmp_path / "dev" / home / "evidence.md"
        target.parent.mkdir(parents=True)
        target.write_text("Durable evidence", encoding="utf-8")
    (reference / "guide.md").write_text(
        "[decision](../records/decisions/evidence.md#claim)\n"
        "[archive](../tasks-archive/evidence.md)\n"
        "[review archive](../records/reviews-archive/evidence.md)\n"
        "[external](https://example.org/) [section](#claim)",
        encoding="utf-8",
    )
    monkeypatch.setattr(ca, "REFERENCE_DIR", reference)
    monkeypatch.setattr(ca, "REPO_ROOT", tmp_path)
    assert ca.check_links() == []
