"""Check activation links against the tracked manifest and reference navigation.

The manifest owns role/skill declarations. Reference prose explains their use,
without repeating an inventory. Runtime link checks are report-only and skip
when local activation trees are absent; Markdown links also hold on bare clones.
Role-derived skill expansion remains the infrastructure activation check's job.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
MANIFEST = REPO_ROOT / ".agent-system" / "agent-manifest.yml"
REFERENCE_DIR = REPO_ROOT / "dev" / "reference"

# Inline links only; reference-style and bare URLs are out of scope.
_MD_LINK = re.compile(r"(?<!!)\[[^\]]*\]\(([^)]+)\)")

_RETIRED_REVIEW_DIRS = ("dev/records/reviews", "dev/records/review")


def _declared_sets() -> dict[str, list[str]]:
    """Read nonempty role/skill lists from the authoritative manifest."""
    document = yaml.safe_load(MANIFEST.read_text(encoding="utf-8"))
    if not isinstance(document, dict):
        raise ValueError("activation manifest must be a mapping")
    result = {}
    for key, label in (("roles", "roles"), ("skills", "manifest-explicit")):
        entries = document.get(key)
        if (
            not isinstance(entries, list)
            or not entries
            or any(not isinstance(entry, str) or not entry.strip() for entry in entries)
        ):
            raise ValueError(
                f"activation manifest {key} must be a nonempty list of names"
            )
        result[label] = sorted(entries)
    return result


def _linked(directory: Path) -> list[str]:
    if not directory.is_dir():
        return []
    return sorted(p.name.removesuffix(".md") for p in directory.iterdir())


def check_names() -> tuple[list[str], bool]:
    """Compare manifest declarations with the locally materialized trees."""
    roles_dir = REPO_ROOT / ".claude" / "agents"
    skills_dir = REPO_ROOT / ".claude" / "skills"
    codex_dir = REPO_ROOT / ".agents" / "skills"
    if not roles_dir.is_dir() or not skills_dir.is_dir():
        return [], False
    try:
        sets = _declared_sets()
    except (OSError, ValueError, yaml.YAMLError) as error:
        return [f"cannot read activation manifest: {error}"], True
    problems = []
    for label, directory in (("roles", roles_dir), ("manifest-explicit", codex_dir)):
        if not directory.is_dir():
            continue
        expected, actual = set(sets[label]), set(_linked(directory))
        missing, extra = expected - actual, actual - expected
        if missing:
            problems.append(
                f"{label}: manifest entries missing under {directory.relative_to(REPO_ROOT)}: "
                + ", ".join(sorted(missing))
            )
        if extra:
            problems.append(
                f"{label}: links absent from the manifest under {directory.relative_to(REPO_ROOT)}: "
                + ", ".join(sorted(extra))
            )
    missing = set(sets["manifest-explicit"]) - set(_linked(skills_dir))
    if missing:
        problems.append(
            "manifest-explicit skills missing from .claude/skills/: "
            + ", ".join(sorted(missing))
        )
    return problems, True


def check_links() -> list[str]:
    """Relative reference links must resolve and avoid transient/prunable homes.

    Holds on a bare checkout, which is why it is the half a test can pin.
    """
    problems: list[str] = []
    for retired in _RETIRED_REVIEW_DIRS:
        if (REPO_ROOT / retired).exists():
            problems.append(
                f"retired review directory: {retired}; keep reviews with their task"
            )
    for doc in sorted(REFERENCE_DIR.rglob("*.md")):
        for target in _MD_LINK.findall(doc.read_text(encoding="utf-8")):
            target = target.split("#", 1)[0].strip()
            if not target or "://" in target or target.startswith("<"):
                continue
            resolved = (doc.parent / target).resolve()
            source = doc.relative_to(REPO_ROOT).as_posix()
            if resolved.is_relative_to(REPO_ROOT / "dev/tasks"):
                problems.append(
                    f"{source}: link to transient task material -> {target}; "
                    "promote cited evidence before linking from a reference"
                )
                continue
            if any(
                resolved.is_relative_to(REPO_ROOT / retired)
                for retired in _RETIRED_REVIEW_DIRS
            ):
                problems.append(
                    f"{source}: link to retired review material -> {target}; "
                    "use a durable evidence home"
                )
                continue
            if not resolved.exists():
                problems.append(
                    f"{doc.relative_to(REPO_ROOT)}: broken link -> {target}"
                )
    return problems


def check_dangling() -> tuple[list[str], bool]:
    """A symlink farm entry pointing at nothing is a silent activation gap."""
    problems: list[str] = []
    checked = False
    for root in (REPO_ROOT / ".claude", REPO_ROOT / ".agents"):
        if not root.is_dir():
            continue
        checked = True
        for path in root.rglob("*"):
            if path.is_symlink() and not path.exists():
                problems.append(
                    f"{path.relative_to(REPO_ROOT)} -> {path.readlink()} (dangling)"
                )
    return problems, checked


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--json", action="store_true", help="machine-readable output")
    args = ap.parse_args(argv)

    name_problems, activated = check_names()
    link_problems = check_links()
    dangling, farms_present = check_dangling()

    results = {
        "names": {
            "skipped": not activated,
            "problems": name_problems,
        },
        "links": {"skipped": False, "problems": link_problems},
        "dangling": {"skipped": not farms_present, "problems": dangling},
    }
    failed = any(r["problems"] for r in results.values())

    if args.json:
        print(json.dumps({"ok": not failed, "checks": results}, indent=1))
        return 1 if failed else 0

    for name, result in results.items():
        if result["skipped"] and not result["problems"]:
            print(
                f"{name}: SKIPPED - the agent symlink farms are not present. "
                "Run `brain refresh --agent-system --project .` to activate."
            )
            continue
        if not result["problems"]:
            print(f"{name}: ok")
            continue
        print(f"{name}: {len(result['problems'])} problem(s)", file=sys.stderr)
        for problem in result["problems"]:
            print(f"  {problem}", file=sys.stderr)

    if failed:
        print(
            "\nDeclarations live in .agent-system/agent-manifest.yml. Resolve "
            "manifest/tree drift through activation setup; see "
            "dev/reference/dev-agent-activation.md.",
            file=sys.stderr,
        )
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
