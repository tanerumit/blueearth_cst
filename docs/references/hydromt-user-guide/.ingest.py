#!/usr/bin/env python3
"""One-off: convert hydromt's docs/user_guide/*.rst to markdown.

Run from the repo root:

    python _raw/hydromt-user-guide/.ingest.py

Reads RST files from `_raw/.hydromt-clone/docs/user_guide/`, runs pandoc
(`rst -> gfm`), and writes mirrored `.md` files under
`_raw/hydromt-user-guide/`. Each output gets a frontmatter block with
`source:` (rendered HTML URL), `repo-source:` (GitHub blob URL pinned to
the cloned commit), and `pulled:` (clone date). After this lands, the
clone tree can be deleted.

Idempotent: re-running overwrites every output file.
"""
from __future__ import annotations

import datetime
import shutil
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
SRC_ROOT = REPO_ROOT / "_raw" / ".hydromt-clone" / "docs" / "user_guide"
DST_ROOT = REPO_ROOT / "_raw" / "hydromt-user-guide"
PIN_FILE = REPO_ROOT / "_raw" / ".hydromt-clone-pin.txt"
PANDOC = Path(r"C:\Users\taner\AppData\Local\Pandoc\pandoc.exe")

UPSTREAM_HTML_BASE = "https://deltares.github.io/hydromt/latest/user_guide"
UPSTREAM_REPO = "Deltares/hydromt"


def load_pin() -> tuple[str, str]:
    raw = PIN_FILE.read_text(encoding="utf-8").strip()
    sha, date = raw.split("\t")
    return sha, date


def ensure_pandoc() -> None:
    if not PANDOC.exists():
        sys.exit(f"pandoc not found at {PANDOC}")


def convert(src: Path, dst: Path, sha: str, pulled: str) -> None:
    rel = src.relative_to(SRC_ROOT).with_suffix("")  # e.g. models/model_build
    rel_posix = rel.as_posix()
    html_url = f"{UPSTREAM_HTML_BASE}/{rel_posix}.html"
    rst_url = f"https://github.com/{UPSTREAM_REPO}/blob/{sha}/docs/user_guide/{rel_posix}.rst"

    out = subprocess.run(
        [str(PANDOC), "-f", "rst", "-t", "gfm", "--wrap=none", str(src)],
        check=True, capture_output=True, text=True, encoding="utf-8",
    )
    body = out.stdout

    fm_lines = [
        "---",
        f"title: {src.stem}",
        "ingest-source: hydromt-user-guide",
        f"source: {html_url}",
        f"repo-source: {rst_url}",
        f"upstream-repo: {UPSTREAM_REPO}",
        f"upstream-commit: {sha}",
        f"pulled: {pulled}",
        "doc-type: user-guide",
        "license: MIT",
        "---",
        "",
    ]
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text("\n".join(fm_lines) + body, encoding="utf-8")


def main() -> None:
    ensure_pandoc()
    if not SRC_ROOT.exists():
        sys.exit(f"clone tree missing: {SRC_ROOT}")
    sha, pulled = load_pin()

    rst_files = sorted(SRC_ROOT.rglob("*.rst"))
    print(f"converting {len(rst_files)} RST files (commit {sha[:8]}, pulled {pulled})")

    for src in rst_files:
        rel = src.relative_to(SRC_ROOT)
        dst = DST_ROOT / rel.with_suffix(".md")
        convert(src, dst, sha, pulled)
        print(f"  {rel.as_posix()} -> {dst.relative_to(REPO_ROOT).as_posix()}")

    print(f"\ndone. {len(rst_files)} files written under _raw/hydromt-user-guide/")
    print("clone tree retained at _raw/.hydromt-clone/ — delete with:")
    print("  rm -rf _raw/.hydromt-clone _raw/.hydromt-clone-pin.txt")


if __name__ == "__main__":
    main()
