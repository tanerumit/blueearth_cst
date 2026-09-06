"""Report drift between the activation record and what is actually on disk.

`dev/reference/agent-activation.md` is the TRACKED record of which agent roles
and skills are active here; `.claude/agent-manifest.yml` is the untracked
source that `brain refresh --agent-system` materializes into symlink farms
(`.claude/agents/`, `.claude/skills/`, `.agents/skills/`). Because the manifest
is gitignored, nothing but that document preserves the decision -- and nothing
but this script notices when the document stops describing the machine. It was
written after an audit found the record naming 14 explicit skills where 9 were
linked, and the wrong frontmatter key besides.

Three checks, all report-only:

  names       the roles and skills the record NAMES, against the linked trees
  links       every relative Markdown link in dev/reference/*.md resolves
  dangling    no symlink under .claude/ or .agents/ points at nothing

Deliberately NOT a test. The trees are gitignored per-user state that a bare
checkout does not have, so a CI gate on them would fail on every fresh clone
for the wrong reason. `links` is the one check that holds on a bare checkout,
and it is the one `tests/test_activation_links.py` pins.

    python dev/scripts/check_activation.py [--json]

Exit 0 when clean, 1 when something drifted, and 0 with a SKIPPED line when the
symlink farms are simply absent -- the bare-checkout case, which is not a
defect. The role-binding side (a bound skill that resolves neither in the
catalog nor under the brain's skills root) is already covered upstream by
`claude_fallback_gaps`; this does not duplicate it.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
RECORD = REPO_ROOT / "dev" / "reference" / "agent-activation.md"
REFERENCE_DIR = REPO_ROOT / "dev" / "reference"

# The record states each set as a bulleted `- **<Label> (n):** `a`, `b`, ...`
# line. Parsing the NAMES rather than the count is deliberate: a swap that keeps
# the total the same is exactly the drift that goes unnoticed.
_SET_LINE = re.compile(
    r"^- \*\*(?P<label>[^*(]+?)\s*\((?P<count>\d+)\)[:*]*\*?\*?:?\s*(?P<body>.+)$",
    re.M,
)
_BACKTICKED = re.compile(r"`([^`]+)`")
# Inline links only; reference-style and bare URLs are out of scope.
_MD_LINK = re.compile(r"(?<!!)\[[^\]]*\]\(([^)]+)\)")


def _bullets(text: str) -> list[str]:
    """Markdown bullets, each rejoined from its wrapped continuation lines.

    The sets are long enough to wrap, and a per-line regex silently reads only
    the first line -- which looks like a set that shrank.
    """
    joined: list[str] = []
    for line in text.splitlines():
        if line.startswith("- "):
            joined.append(line)
        elif joined and line.startswith("  ") and line.strip():
            joined[-1] += " " + line.strip()
        elif not line.strip():
            joined.append("")
    return [b for b in joined if b]


def _named_sets(text: str) -> dict[str, list[str]]:
    """Map each `- **Label (n):** ...` bullet to the backticked names in it."""
    found: dict[str, list[str]] = {}
    for bullet in _bullets(text):
        m = _SET_LINE.match(bullet)
        if not m:
            continue
        label = m.group("label").strip().lower()
        names = _BACKTICKED.findall(m.group("body"))
        if names:
            found[label] = sorted(names)
    return found


def _linked(directory: Path) -> list[str]:
    if not directory.is_dir():
        return []
    return sorted(p.name.removesuffix(".md") for p in directory.iterdir())


def check_names() -> tuple[list[str], bool]:
    """Compare the record's named sets against the materialized trees."""
    problems: list[str] = []
    roles_dir = REPO_ROOT / ".claude" / "agents"
    skills_dir = REPO_ROOT / ".claude" / "skills"
    codex_dir = REPO_ROOT / ".agents" / "skills"
    if not roles_dir.is_dir() or not skills_dir.is_dir():
        return problems, False  # not activated on this machine; not a defect

    sets = _named_sets(RECORD.read_text(encoding="utf-8"))
    # Only the two sets the record enumerates by name are checked exactly. The
    # Codex root catalog is the manifest-explicit set by definition, and the
    # Claude scope bullet states a delta ("those N + `x`") rather than a list;
    # the latter is checked as a superset below.
    expectations = [
        ("roles", roles_dir, _linked(roles_dir)),
        ("manifest-explicit", codex_dir, _linked(codex_dir)),
    ]
    for label, directory, actual in expectations:
        stated = sets.get(label)
        if stated is None:
            problems.append(
                f"the record names no '{label}' set -- has it been renamed?"
            )
            continue
        if not directory.is_dir():
            continue
        missing = sorted(set(stated) - set(actual))
        extra = sorted(set(actual) - set(stated))
        if missing:
            problems.append(
                f"{label}: the record names {', '.join(missing)}, "
                f"not linked under {directory.relative_to(REPO_ROOT)}"
            )
        if extra:
            problems.append(
                f"{label}: {', '.join(extra)} is linked under "
                f"{directory.relative_to(REPO_ROOT)} but the record does not name it"
            )

    claude = set(_linked(skills_dir))
    stated_explicit = set(sets.get("manifest-explicit", []))
    if stated_explicit and not stated_explicit <= claude:
        problems.append(
            "manifest-explicit skills missing from .claude/skills/: "
            + ", ".join(sorted(stated_explicit - claude))
        )
    return problems, True


def check_links() -> list[str]:
    """Every relative Markdown link under dev/reference/ must resolve.

    Holds on a bare checkout, which is why it is the half a test can pin.
    """
    problems: list[str] = []
    for doc in sorted(REFERENCE_DIR.rglob("*.md")):
        for target in _MD_LINK.findall(doc.read_text(encoding="utf-8")):
            target = target.split("#", 1)[0].strip()
            if not target or "://" in target or target.startswith("<"):
                continue
            if not (doc.parent / target).resolve().exists():
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
            "\nThe record is dev/reference/agent-activation.md. If the trees are "
            "right and the record is stale, fix the record -- the manifest is "
            "gitignored, so the record is the only thing that survives a clone.",
            file=sys.stderr,
        )
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
