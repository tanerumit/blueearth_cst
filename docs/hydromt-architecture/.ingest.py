#!/usr/bin/env python3
"""One-off: convert hydromt's docs/dev/architecture/*.rst to markdown.

Run from the repo root:

    python _raw/hydromt-architecture/.ingest.py

Same pattern as `_raw/hydromt-user-guide/.ingest.py` — pandoc converts
each RST to GFM markdown, mirroring the upstream tree under
`_raw/hydromt-architecture/`. Then merges the 3 pages into a single
`architecture-merged.md` for convenience.

Idempotent.
"""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
SRC_ROOT = REPO_ROOT / "_raw" / ".hydromt-clone" / "docs" / "dev" / "architecture"
DST_ROOT = REPO_ROOT / "_raw" / "hydromt-architecture"
PIN_FILE = REPO_ROOT / "_raw" / ".hydromt-clone-pin.txt"
PANDOC = Path(r"C:\Users\taner\AppData\Local\Pandoc\pandoc.exe")

UPSTREAM_HTML_BASE = "https://deltares.github.io/hydromt/latest/dev/architecture"
UPSTREAM_REPO = "Deltares/hydromt"

# Upstream toctree order — index first, then the two body pages.
PAGE_ORDER = ["index.rst", "architecture.rst", "conventions.rst"]


def load_pin() -> tuple[str, str]:
    raw = PIN_FILE.read_text(encoding="utf-8").strip()
    sha, date = raw.split("\t")
    return sha, date


def convert_one(src: Path, dst: Path, sha: str, pulled: str) -> None:
    rel = src.stem  # e.g. architecture
    html_url = f"{UPSTREAM_HTML_BASE}/{rel}.html"
    rst_url = f"https://github.com/{UPSTREAM_REPO}/blob/{sha}/docs/dev/architecture/{rel}.rst"

    out = subprocess.run(
        [str(PANDOC), "-f", "rst", "-t", "gfm", "--wrap=none", str(src)],
        check=True, capture_output=True, text=True, encoding="utf-8",
    )
    body = out.stdout

    fm_lines = [
        "---",
        f"title: {rel}",
        "ingest-source: hydromt-architecture",
        f"source: {html_url}",
        f"repo-source: {rst_url}",
        f"upstream-repo: {UPSTREAM_REPO}",
        f"upstream-commit: {sha}",
        f"pulled: {pulled}",
        "doc-type: architecture",
        "license: MIT",
        "---",
        "",
    ]
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text("\n".join(fm_lines) + body, encoding="utf-8")


FM_RE = re.compile(r"\A---\n(.*?)\n---\n?", re.DOTALL)


def parse_page(path: Path) -> tuple[dict, str]:
    text = path.read_text(encoding="utf-8")
    m = FM_RE.match(text)
    if not m:
        return {}, text
    fm = {}
    for line in m.group(1).splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            fm[k.strip()] = v.strip()
    body = text[m.end():]
    body = re.sub(r"\A#\s+[^\n]+\n+", "", body)  # drop original H1
    return fm, body.strip()


def merge_section(sha: str, pulled: str) -> Path:
    pages = []
    for stem in [Path(p).stem for p in PAGE_ORDER]:
        page = DST_ROOT / f"{stem}.md"
        fm, body = parse_page(page)
        pages.append((stem, fm, body))

    fm_lines = [
        "---",
        "title: HydroMT — Architecture and conventions",
        "ingest-source: hydromt-architecture",
        f"upstream-repo: {UPSTREAM_REPO}",
        f"upstream-commit: {sha}",
        f"pulled: {pulled}",
        "section: architecture",
        "doc-type: architecture",
        "license: MIT",
        "sources:",
    ]
    for _, fm, _ in pages:
        fm_lines.append(f"  - {fm.get('source', '')}")
    fm_lines.append("---")
    fm_lines.append("")

    out_lines = ["\n".join(fm_lines)]
    out_lines.append("# HydroMT — Architecture and conventions\n")
    out_lines.append(
        f"_Merged from {len(pages)} upstream page(s) at commit `{sha[:8]}`, "
        f"pulled {pulled}. Page boundaries are preserved as `## ` headings._\n"
    )

    for stem, fm, body in pages:
        page_title = stem.replace("_", " ")
        out_lines.append("\n---\n")
        out_lines.append(f"## {page_title}\n")
        out_lines.append(
            f"> **Source:** [{stem}.md]({fm.get('source', '')}) · "
            f"[upstream `.rst`]({fm.get('repo-source', '')})\n"
        )
        out_lines.append(body)
        out_lines.append("")

    dst = DST_ROOT / "architecture-merged.md"
    dst.write_text("\n".join(out_lines).rstrip() + "\n", encoding="utf-8")
    return dst


def main() -> None:
    if not PANDOC.exists():
        sys.exit(f"pandoc not found at {PANDOC}")
    if not SRC_ROOT.exists():
        sys.exit(f"clone tree missing: {SRC_ROOT}")
    sha, pulled = load_pin()

    print(f"converting {len(PAGE_ORDER)} RST files (commit {sha[:8]}, pulled {pulled})")
    for fname in PAGE_ORDER:
        src = SRC_ROOT / fname
        dst = DST_ROOT / Path(fname).with_suffix(".md")
        convert_one(src, dst, sha, pulled)
        print(f"  {fname} -> {dst.relative_to(REPO_ROOT).as_posix()}")

    merged = merge_section(sha, pulled)
    print(f"\nmerged into {merged.relative_to(REPO_ROOT).as_posix()}")


if __name__ == "__main__":
    main()
