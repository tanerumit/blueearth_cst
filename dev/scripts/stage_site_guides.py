"""Stage canonical Markdown guides for Quarto's site-local render tree.

Called by the Quarto pre-render hook for both render and preview. Canonical
links resolve from docs/guide; staged links resolve from docs/site/guide.
"""

from pathlib import Path
from shutil import copyfile

GUIDES = ("quick-start", "configuration", "running", "benchmarking", "outputs")


def stage_guides(docs_dir: Path) -> None:
    """Refresh the site copies and their self-contained diagram asset."""
    source_dir = docs_dir / "guide"
    target_dir = docs_dir / "site" / "guide"
    # Read every required source before writing, so missing inputs fail the build.
    sources = {
        name: (source_dir / f"{name}.md").read_text(encoding="utf-8") for name in GUIDES
    }
    asset = Path("assets/shape-of-a-run.html")
    if not (source_dir / asset).is_file():
        raise FileNotFoundError(source_dir / asset)
    (target_dir / "assets").mkdir(parents=True, exist_ok=True)
    for name, content in sources.items():
        content = content.replace("](../site/", "](../")
        (target_dir / f"{name}.md").write_text(content, encoding="utf-8")
    copyfile(source_dir / asset, target_dir / asset)


if __name__ == "__main__":
    stage_guides(Path(__file__).resolve().parents[2] / "docs")
