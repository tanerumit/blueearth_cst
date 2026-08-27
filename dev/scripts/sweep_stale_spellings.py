"""Find retired R14 config spellings that are still live somewhere.

`C-37`'s mechanical successor, and design D-14.4. Report-only; it never edits.

**It CLASSIFIES, it does not grep.** "Fail on any hit" is unsatisfiable: the
migration mapping must name every v1 spelling in order to migrate it, the
refusal messages must carry them in order to recognise them, and the `presplit/`
fixtures exist precisely to be v1. A sweep that flagged those would be turned
off within a day, which is the real failure mode.

So every hit is assigned a CLASS, and each class carries a reason it is
legitimate. A hit that matches no class is a defect — and an unknown class
FAILS CLOSED rather than being waved through, because the whole value of this
tool is that a new kind of hit stops the build instead of joining the noise.

Usage::

    python dev/scripts/sweep_stale_spellings.py          # report, exit 1 on defects
    python dev/scripts/sweep_stale_spellings.py --json   # machine-readable
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


@dataclass(frozen=True)
class Allowance:
    """One class of legitimate hit, with the reason it is legitimate."""

    name: str
    reason: str
    paths: tuple[str, ...] = ()
    path_globs: tuple[str, ...] = ()
    line_patterns: tuple[str, ...] = field(default=())

    def covers(self, path: Path, line: str) -> bool:
        rel = path.relative_to(REPO_ROOT).as_posix()
        if rel in self.paths:
            return True
        if any(Path(rel).match(glob) for glob in self.path_globs):
            return True
        return any(re.search(pattern, line) for pattern in self.line_patterns)


#: Ordered, and the order is the explanation: the first class that covers a hit
#: is the reason recorded for it.
ALLOWANCES = (
    Allowance(
        name="the mapping itself",
        reason=(
            "the v1->v2 mapping must NAME every retired spelling in order to "
            "migrate it; a sweep that flagged it would flag the cure"
        ),
        paths=("config/migrations/v1_to_v2.yml",),
    ),
    Allowance(
        name="the loader's refusal table",
        reason=(
            "`RETIRED_KEYS` carries the old spellings so it can RECOGNISE them "
            "and name their destination; without them a v1 config gets a "
            "KeyError instead of an explanation"
        ),
        paths=("blueearth_cst/shared/config_composition.py",),
    ),
    Allowance(
        name="the rewriter and its tests",
        reason=(
            "the migration tool reads, transforms and asserts on v1 spellings "
            "by construction"
        ),
        paths=(
            "scripts/migrate_project_config.py",
            "tests/test_migrate_project_config.py",
            "tests/test_migration_mapping.py",
            "dev/scripts/sweep_stale_spellings.py",
        ),
    ),
    Allowance(
        name="the v1 migration fixtures",
        reason="`tests/data/presplit/` exists precisely to hold v1 configs",
        path_globs=("tests/data/presplit/*",),
    ),
    Allowance(
        name="milestone records",
        reason=(
            "`dev/milestones/**` and `dev/tasks/**` are records of what was "
            "decided; their value is that they are NOT swept"
        ),
        path_globs=("dev/milestones/**", "dev/tasks/**", "dev/TODO.md", "dev/LOG.md"),
    ),
    Allowance(
        name="weathergenr's own vocabulary",
        reason=(
            "the weather generator's config keys are ITS vocabulary, not ours. "
            "K1 and S5 put the engine's spelling out of reach, so "
            "`transient_change` and the two spell factors stay as written INTO "
            "its config even though our keys for them moved"
        ),
        paths=(
            "blueearth_cst/experiment/prepare_weagen_config.py",
            "blueearth_cst/shared/interchange_contracts.py",
        ),
    ),
    Allowance(
        name="a Snakemake input or archive role name",
        reason=(
            "an input name is INTERNAL and need not track the config key it is "
            "fed from -- the precedent is `output_locations`, whose config "
            "source has been `basin.gauge_points` and is now "
            "`basin.output_locations`, while the input name never moved"
        ),
        paths=(
            "blueearth_cst/model/copy_config_files.py",
            "blueearth_cst/model/plot_results.py",
            "blueearth_cst/spatial/delineate_spatial_units.py",
            "blueearth_cst/shared/snake_utils.py",
            "build_model.smk",
        ),
    ),
    Allowance(
        name="an emitted provenance field",
        reason=(
            "`products.py` writes `automatic_subbasins` as a COUNT into the "
            "delineation summary -- an output field that happens to share a "
            "name with a retired config key, and renaming it would change an "
            "artifact no R14 row touches"
        ),
        paths=("blueearth_cst/spatial/products.py",),
    ),
    Allowance(
        name="a netCDF dimension or provenance field",
        reason=(
            "`clim_project` is a DIMENSION name in emitted netCDFs and a field "
            "in provenance records. Renaming it is an output-schema change and "
            "belongs to no R14 row"
        ),
        path_globs=("blueearth_cst/projections/*",),
    ),
    Allowance(
        name="a cross-era path normalization table",
        reason=(
            "`check_project_consistency` normalises paths from BOTH eras so a "
            "snapshot taken before a move still compares; it has to name the "
            "old spellings to recognise them"
        ),
        paths=("blueearth_cst/experiment/check_project_consistency.py",),
    ),
    Allowance(
        name="a refusal or migration message",
        reason=(
            "a message that tells a user which key to change has to say the "
            "old key's name"
        ),
        line_patterns=(r"renamed to", r"regrouped as", r"replaced by", r"folded"),
    ),
    Allowance(
        name="prose describing the change",
        reason=(
            "a comment or docstring explaining what a key USED to be is history, "
            "not a live reference"
        ),
        line_patterns=(r"^\s*#", r"was `", r"used to", r"`C-\d+`"),
    ),
)

#: Where a hit is a DEFECT. Everything else in the tree is out of scope for this
#: sweep: generated output, the environment, and the untracked project trees.
SEARCHED = (
    "blueearth_cst/**/*.py",
    "scripts/**/*.py",
    "dev/scripts/**/*.py",
    "tests/**/*.py",
    "*.smk",
    "config/**/*.yml",
    "test_case/*.yml",
    "docs/**/*.md",
    "docs/**/*.qmd",
    "README.md",
    "AGENTS.md",
)

EXCLUDED_DIRS = ("_site", ".quarto", ".pixi", "__pycache__", ".tmp", ".git")


def surviving_leaves() -> set[str]:
    """Leaf names that are ALSO valid v2 keys, and so cannot be swept by name.

    Three ways a leaf survives:

    * it is a v2 destination somewhere (``seed`` moves from `shared:` into the
      WF3 file but keeps its name, so the word is live);
    * it only ever retypes (``members``, ``simulation_window``);
    * it is a SUBSTRING of a live identifier — ``stress_test`` inside
      ``run_stress_test``, which names the workflow and is not going anywhere.

    Sweeping any of these by name produces hundreds of hits that are all
    correct, which is how a sweep gets switched off.
    """
    import yaml

    mapping = yaml.safe_load(
        (REPO_ROOT / "config" / "migrations" / "v1_to_v2.yml").read_text(
            encoding="utf-8"
        )
    )
    # `julia_threads` left the PROJECT config (`C-54`) but is the key name in
    # `advanced_settings.runtime` — the destination, not a dead spelling.
    survivors = {
        "seed",
        "reporting",
        "stress_test",
        "members",
        "simulation_window",
        "julia_threads",
    }
    for row in mapping["rows"]:
        for move in row.get("moves") or []:
            new_path = move.get("new_path")
            if new_path:
                survivors.add(new_path.split(".")[-1])
    return survivors


def retired_spellings() -> dict[str, str]:
    """``{v1 leaf name: where it went}``, from the loader's own table.

    Derived, never hand-listed: the sweep and the refusals must not be able to
    disagree about which spellings are dead. Leaves that survive into v2 are
    dropped, because no name-based sweep can distinguish their two uses.
    """
    from blueearth_cst.shared.config_composition import RETIRED_KEYS

    survivors = surviving_leaves()
    out = {}
    for dotted, destination in RETIRED_KEYS.items():
        leaf = dotted.split(".")[-1]
        if leaf in {"*", "shared"} or leaf in survivors:
            continue
        out[leaf] = destination if isinstance(destination, str) else str(destination)
    return out


def sweep(root: Path = REPO_ROOT):
    """Return ``(defects, allowed)``, each a list of ``(path, lineno, line, why)``."""
    spellings = retired_spellings()
    if not spellings:
        return [], []
    names = "|".join(sorted(spellings, key=len, reverse=True))
    # **Key POSITION, not free text.** A retired key is a defect when something
    # declares or reads it — `key:` in YAML, `"key"` in Python — and is not a
    # defect when prose happens to contain the word. Matching the bare token
    # produced 1371 hits, nearly all of them correct usage, which is a sweep
    # nobody would keep.
    # In YAML a DECLARATION is a key at line start; in code a config READ is
    # a quoted key. Nothing else counts, and the exclusions are exactly the
    # tier rule P1b settled: `sm.params.data_sources` is a Snakemake params
    # NAME and `data_sources : str | Path` is a docstring — neither is a
    # config key. Sweeping them produced 429 hits that were all correct
    # usage, and a sweep that cries wolf 429 times gets switched off.
    yaml_key = re.compile(rf"^\s*({names})\s*:")
    quoted_key = re.compile(rf"""['"]({names})['"]""")

    def matches(path: Path, line: str) -> bool:
        if path.suffix in {".py", ".smk"}:
            return bool(quoted_key.search(line))
        # YAML, and docs — where a fenced example is what misleads a reader.
        return bool(yaml_key.match(line))

    defects, allowed = [], []
    seen: set[Path] = set()
    for glob in SEARCHED:
        for path in root.glob(glob):
            if path in seen or not path.is_file():
                continue
            if any(part in EXCLUDED_DIRS for part in path.parts):
                continue
            seen.add(path)
            try:
                text = path.read_text(encoding="utf-8")
            except (UnicodeDecodeError, OSError):
                continue
            for lineno, line in enumerate(text.splitlines(), 1):
                if not matches(path, line):
                    continue
                for allowance in ALLOWANCES:
                    if allowance.covers(path, line):
                        allowed.append((path, lineno, line.strip(), allowance.name))
                        break
                else:
                    defects.append((path, lineno, line.strip(), "UNCLASSIFIED"))
    return defects, allowed


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--json", action="store_true", help="machine-readable output")
    args = parser.parse_args(argv)

    defects, allowed = sweep()

    if args.json:
        print(
            json.dumps(
                {
                    "defects": [
                        {
                            "path": str(p.relative_to(REPO_ROOT)),
                            "line": n,
                            "text": t,
                        }
                        for p, n, t, _ in defects
                    ],
                    "allowed": len(allowed),
                },
                indent=1,
            )
        )
    else:
        print(f"{len(allowed)} hit(s) classified as legitimate.")
        if defects:
            print(f"\n{len(defects)} STALE SPELLING(S) with no classification:\n")
            for path, lineno, text, _ in defects:
                print(f"  {path.relative_to(REPO_ROOT)}:{lineno}")
                print(f"      {text[:110]}")
        else:
            print("No unclassified retired spellings.")
    return 1 if defects else 0


if __name__ == "__main__":
    raise SystemExit(main())
