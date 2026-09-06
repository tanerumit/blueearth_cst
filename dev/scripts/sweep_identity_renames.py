"""Find rename records whose two sides have become identical: `X -> X`.

The sibling of `sweep_stale_spellings.py`, and its opposite in every way that
matters. That sweep asks "is this spelling dead" and most of its hits are
legitimate, so its work is in the ALLOWANCES. This one asks "does this line
still say what it was written to say", and fires on lines where both sides are
live current spellings — invisible to a retired-key sweep by construction. Its
polarity is inverted too: an `X -> X` rename record is almost always a defect,
so its work is in recognising the record FORMS rather than in excusing hits.

**Why it exists.** R14 produced this defect six times, which made it the most
reliable defect of the milestone: a blanket token rename rewriting the OLD side
of a rename record along with everything else. It hit `C-85`'s own mapping row,
two board notes, `naming.md`, and two columns of `rule-index.md`. Every one was
caught by a test or by reading the diff — never by a tool. A seventh survived
undetected until 2026-09-06 and is quoted in `dev/tasks/`'s note for this check.

**Fail-closed** (design `D-14.5`). Each form declares how many candidate records
it saw when it was written and a floor it may not fall below. A matcher that
goes blind — a file renamed, a record format changed — otherwise reports a clean
tree while seeing nothing, which is the shape R14's own re-measure failed in:
its extraction returned zero and it reported MORE flags while knowing LESS.

Usage::

    python dev/scripts/sweep_identity_renames.py          # exit 1 on defects
    python dev/scripts/sweep_identity_renames.py --json   # machine-readable
"""

from __future__ import annotations

import argparse
import ast
import json
import re
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from dev.scripts.sweep_common import (  # noqa: E402
    EXCLUDED_DIRS,
    REPO_ROOT,
    Allowance,
    Floor,
    check_floors,
    classify,
    iter_lines,
)

#: Where a rename record can live. WIDER than the stale-spelling sweep in one
#: place and narrower in another, and both differences are deliberate:
#:
#: * `dev/reference/**` and `dev/tasks/**` are IN. That sweep excuses them under
#:   one "milestone records" class, which is right for `dev/milestones/**` —
#:   sealed baselines whose value is that they are not swept — and wrong here.
#:   A reference doc and a board note are live working material, and two board
#:   notes plus two reference docs were among R14's six instances.
#: * `dev/milestones/**` is OUT, for that same sealed-record reason. So are the
#:   four documents in `dev/reference/sealed-records.yml`, which a test forbids
#:   editing: reporting a defect nobody may repair is noise.
#: * `dev/TODO.md` and `dev/LOG.md` are OUT. `TODO.md` is GENERATED from the
#:   notes, so a hit there is a hit in the note behind it and would be reported
#:   twice; `LOG.md` is an append-only closure ledger.
SEARCHED = (
    "config/migrations/*.yml",
    "config/**/*.yml",
    "dev/reference/**/*.md",
    "dev/tasks/*.md",
    "dev/decisions/*.md",
    "docs/**/*.md",
    "docs/**/*.qmd",
    "README.md",
    "AGENTS.md",
    "blueearth_cst/**/*.py",
    "dev/scripts/**/*.py",
    "scripts/**/*.py",
    "tests/**/*.py",
    "*.smk",
)

#: A backticked identifier, path or glob — the shape a rename record's two sides
#: take in prose here. Backticks are load-bearing: matching bare words would
#: turn every sentence containing an arrow into a candidate.
_TICKED = r"`([^`\n]{1,120})`"

#: `->`, `-->` or a real arrow between two backticked spellings.
ARROW_RE = re.compile(_TICKED + r"\s*(?:-->|->|→)\s*" + _TICKED)

#: The prose forms that assert a rename in words. Kept to verbs that CLAIM a
#: move: "`X` is now `Y`" is a rename record, "`X` is like `Y`" is not.
#:
#: A bounded gap is allowed before the verb, because the sentence that actually
#: decayed in `naming.md` had one: "`weagen` was one and `C-83` retired it in
#: favour of `weathergen`". The gap forbids BACKTICKS, so a third spelling
#: cannot sit between the two sides and pair them across a clause boundary —
#: which is the false positive a plain `.{0,60}` would invent.
VERB_RE = re.compile(
    _TICKED
    + r"[^`\n]{0,60}?\b(?:is now|are now|became|becomes|renamed to|"
    + r"replaced by|in favou?r of)\s+"
    + _TICKED
)

#: "Rename `X` ... to `Y`" — the form that says a rename in a SENTENCE rather
#: than with an arrow, and the one that actually escaped. R14's seventh instance
#: was "Rename every `project_config_*.yml` seed and template to
#: `project_config_*.yml`" — wrapped across two lines, with no arrow and no
#: "is now", so neither per-line form above can see it.
#:
#: Matched over a normalized markdown BLOCK, not a line: the two sides of a
#: wrapped sentence are on different lines about as often as not, and a per-line
#: matcher that misses those misses the form's main population.

#: Any character that does not END a sentence. A bare ``[^.]`` cannot be used
#: here, and the first draft of this pattern proved it by matching nothing at
#: all against the instance it was written for: the spellings this form compares
#: are FILENAMES, so `.yml` puts a dot inside the very token being matched.
_MID_SENTENCE = r"(?:[^.;\n]|\.(?!\s|$))"

RENAME_SENTENCE_RE = re.compile(
    r"\brenam(?:e|es|ed|ing)\b"
    + _MID_SENTENCE
    + r"{0,140}?"
    + _TICKED
    + _MID_SENTENCE
    + r"{0,80}?"
    + r"\bto\b\s*"
    + _TICKED,
    re.IGNORECASE,
)

#: A migration mapping's pair, on consecutive lines. `old_path`/`new_path` is
#: what `config/migrations/v1_to_v2.yml` uses; the others are admitted so a
#: future mapping with a different noun is not silently unmatched.
_OLD_RE = re.compile(r"^\s*-?\s*old_(path|glob|key|name):\s*(\S.*?)\s*$")

#: Ops that do NOT claim a move, so an identical pair under one is correct by
#: construction rather than a defect. `retype` keeps the key and changes only
#: its value shape — `C-63`'s `members` list becoming a group, `C-71`'s
#: `simulation_window` becoming a year pair. This is the discriminator that
#: makes the YAML form usable at all: 12 of the mapping's 54 pairs are retypes,
#: and a form without it would report all 12 as defects on its first run.
_NON_MOVING_OPS = frozenset({"retype", "new", "delete"})

#: A module-level dict whose NAME says it maps old spellings onto new ones.
#: `RETIRED_KEYS` deliberately does not match and must not be added: it maps a
#: retired key to a prose DESCRIPTION of where it went, so a key equal to its
#: value there would not be an `X -> X` rename record at all.
_RENAME_MAP_NAME_RE = re.compile(r"(_MAP|_MAPPING|RENAMES?|_OLD_TO_NEW)$")

#: Forms deliberately NOT implemented, each with the evidence:
#:
#: * **A two-column markdown table.** `rule-index.md`'s live former-name table
#:   is `| new | rule | was |`, and rows like `| 1.00 | \`all\` | 1.00 |` hold
#:   equal new and was ON PURPOSE — a rule that kept its number while a
#:   neighbour moved. A table matcher fires on a correct record, in the very
#:   file this check was filed over. Recognising the table would take a header
#:   convention the repo does not have.
#: * **`--map old=new` arguments.** Every instance is inside `dev/milestones/**`,
#:   which is out of scope as a sealed record, so the form has no observable
#:   population to floor against. A floor of 1 is the fail-open shape `D-14.5`
#:   forbids, so the form is declared missing rather than implemented blind.

ALLOWANCES = (
    Allowance(
        name="an identity mapping named in order to be REJECTED",
        reason=(
            "prose arguing AGAINST a catch-all has to write the catch-all down. "
            "`semantic_tree_diff` and its inventory test both explain why the R9 "
            "path map is not a `data/` -> `data/` rule; the identity is the "
            "thing being refused, not a record that decayed into one. Named by "
            "PATH as well as by line, because the sentence carrying the "
            "refusal wraps and the giveaway word can land on the line before"
        ),
        paths=(
            "dev/scripts/semantic_tree_diff.py",
            "tests/test_project_tree_inventory.py",
        ),
        line_patterns=(
            r"rather than",
            r"\bnot\b.{0,40}(catch-all|identity)",
            r"would (make|be|read)",
        ),
    ),
    Allowance(
        name="this check's own specimens",
        reason=(
            "the specimens below are known-BAD by construction -- their whole "
            "job is to be flagged -- and the sweep would otherwise report its "
            "own fixtures as defects on every run. Same shape as the "
            "stale-spelling sweep excusing itself and its test"
        ),
        paths=(
            "dev/scripts/sweep_identity_renames.py",
            "tests/test_identity_rename_sweep.py",
        ),
    ),
    Allowance(
        name="a sealed record",
        reason=(
            "`dev/reference/sealed-records.yml` registers documents that must "
            "not be edited -- `tests/test_sealed_records.py` fails on a changed "
            "hash. Reporting a defect nobody is allowed to repair is noise, and "
            "the staleness is the point of the seal"
        ),
        paths=(),  # filled from the registry at import; see `_sealed_paths`
    ),
)


def _sealed_paths() -> tuple[str, ...]:
    """Registered sealed-record paths, read from the registry rather than listed.

    A hand-copied list would drift from the registry the moment a document is
    sealed, and the drift would show up as a defect report on a file a test
    already forbids editing.
    """
    import yaml

    registry = REPO_ROOT / "dev" / "reference" / "sealed-records.yml"
    doc = yaml.safe_load(registry.read_text(encoding="utf-8")) or {}
    return tuple(row["path"] for row in doc.get("sealed_records") or [])


ALLOWANCES = tuple(
    Allowance(
        name=a.name,
        reason=a.reason,
        paths=_sealed_paths() if a.name == "a sealed record" else a.paths,
        path_globs=a.path_globs,
        line_patterns=a.line_patterns,
    )
    for a in ALLOWANCES
)

#: What the tree held when each form was written. The floor is well under the
#: count so honest churn does not trip it, and well over 1 so a matcher that
#: has gone blind does — a form falling from 55 candidates to 1 still passes a
#: floor of 1, which is exactly the failure `D-14.5` is about.
#: `prose_rename` has NO floor here on purpose: the tree holds one candidate,
#: and a floor of 1 passes a matcher that has gone blind. Its fail-closed
#: device is its specimen below instead.
FLOORS = (
    Floor(
        name="arrow",
        minimum=30,
        count=63,
        measured="2026-09-07, at 629c803c",
        why=(
            "the backtick-arrow-backtick form is how this repo writes a rename "
            "in prose; a collapse means the pattern or the search scope broke"
        ),
    ),
    Floor(
        name="verb",
        minimum=15,
        count=33,
        measured="2026-09-07, at 629c803c",
        why="the prose form that bit hardest -- `naming.md` was one of the six",
    ),
    Floor(
        name="yaml_move",
        minimum=15,
        count=30,
        measured="2026-09-07, at 629c803c (54 pairs, 24 of them non-moving)",
        why=(
            "`config/migrations/v1_to_v2.yml` is the one structured mapping in "
            "the tree; zero here means the file moved or its keys were renamed"
        ),
    ),
    Floor(
        name="python_rename_map",
        minimum=10,
        count=24,
        measured="2026-09-07, at 629c803c",
        why=(
            "`COPIED_CONFIG_PATH_MAP` is most of this population, so a collapse "
            "means the AST walk stopped reaching module-level dict literals"
        ),
    ),
)


def _line_forms(root: Path):
    """Yield ``(form, path, lineno, line)`` for the two per-line prose forms."""
    for path, lineno, line in iter_lines(SEARCHED, root):
        for form, pattern in (("arrow", ARROW_RE), ("verb", VERB_RE)):
            for match in pattern.finditer(line):
                yield form, path, lineno, line, match.group(1) == match.group(2)


#: Leading markdown and docstring furniture stripped before a block is joined,
#: so a callout's `> ` and a comment's `#: ` do not break a wrapped sentence.
_BLOCK_PREFIX_RE = re.compile(r"^\s*(?:>+\s?|#:\s?|#\s?|\*\s|-\s)")


def _prose_rename_forms(root: Path):
    """Yield "rename `X` to `Y`" sentences, matched over normalized blocks.

    A block is a run of non-blank lines with its markdown furniture stripped and
    its newlines collapsed to spaces. The reported line number is the block's
    first line: the sentence spans several, and pointing at the one holding the
    second spelling would send a reader to the middle of it.
    """
    for glob in (
        "dev/reference/**/*.md",
        "dev/tasks/*.md",
        "dev/decisions/*.md",
        "docs/**/*.md",
        "docs/**/*.qmd",
        "README.md",
        "AGENTS.md",
    ):
        for path in sorted(root.glob(glob)):
            if any(part in EXCLUDED_DIRS for part in path.parts):
                continue
            try:
                lines = path.read_text(encoding="utf-8").splitlines()
            except (UnicodeDecodeError, OSError):
                continue
            start, buffer = None, []
            for lineno, line in enumerate(lines + [""], 1):
                if line.strip():
                    if start is None:
                        start = lineno
                    buffer.append(_BLOCK_PREFIX_RE.sub("", line).strip())
                    continue
                if buffer:
                    block = " ".join(buffer)
                    for match in RENAME_SENTENCE_RE.finditer(block):
                        yield (
                            "prose_rename",
                            path,
                            start,
                            block[max(0, match.start() - 10) : match.end() + 10],
                            match.group(1) == match.group(2),
                        )
                start, buffer = None, []


def _yaml_move_forms(root: Path):
    """Yield the migration mapping's ``old_/new_`` pairs on consecutive lines.

    Stateful across two lines, so it cannot ride the per-line walk. A pair whose
    ``op:`` is non-moving is not a candidate at all — not an allowed hit — because
    an identical pair under ``retype`` is the record being CORRECT.
    """
    for path in sorted(root.glob("config/migrations/*.yml")):
        lines = path.read_text(encoding="utf-8").splitlines()
        for index, line in enumerate(lines[:-1]):
            old = _OLD_RE.match(line)
            if not old:
                continue
            new = re.match(rf"^\s*new_{old.group(1)}:\s*(\S.*?)\s*$", lines[index + 1])
            if not new:
                continue
            op = None
            for follow in lines[index + 2 : index + 8]:
                found = re.match(r"^\s*op:\s*(\w+)", follow)
                if found:
                    op = found.group(1)
                    break
            if op in _NON_MOVING_OPS:
                continue
            yield (
                "yaml_move",
                path,
                index + 1,
                line.strip(),
                old.group(2) == new.group(1),
            )


def _python_map_forms(root: Path):
    """Yield ``str: str`` entries of module-level dicts whose name says "map"."""
    for glob in ("blueearth_cst/**/*.py", "dev/scripts/**/*.py", "tests/**/*.py"):
        for path in sorted(root.glob(glob)):
            if any(part in {".pixi", ".tmp", "__pycache__"} for part in path.parts):
                continue
            try:
                tree = ast.parse(path.read_text(encoding="utf-8"))
            except (SyntaxError, UnicodeDecodeError, OSError):
                continue
            for node in tree.body:
                if isinstance(node, ast.Assign):
                    targets = node.targets
                elif isinstance(node, ast.AnnAssign):
                    targets = [node.target]
                else:
                    continue
                if not any(
                    isinstance(t, ast.Name) and _RENAME_MAP_NAME_RE.search(t.id)
                    for t in targets
                ):
                    continue
                for sub in ast.walk(node):
                    if not isinstance(sub, ast.Dict):
                        continue
                    for key, value in zip(sub.keys, sub.values):
                        if not (
                            isinstance(key, ast.Constant)
                            and isinstance(value, ast.Constant)
                            and isinstance(key.value, str)
                            and isinstance(value.value, str)
                        ):
                            continue
                        yield (
                            "python_rename_map",
                            path,
                            key.lineno,
                            f"{key.value!r}: {value.value!r}",
                            key.value == value.value,
                        )


#: One known-bad specimen per form, and the second half of failing closed.
#:
#: A population floor catches a form whose SCOPE broke — a file moved out of
#: `SEARCHED`, a mapping renamed. It cannot catch a form whose MATCHER broke
#: while the records stayed put, and it cannot be built at all for a form whose
#: honest population is one or two records: a floor of 1 passes a matcher that
#: has gone blind, which is the fail-open shape `D-14.5` forbids.
#:
#: So every form also carries a specimen it MUST still flag. These are real
#: text, not invented: `prose_rename`'s is R14's seventh instance verbatim (the
#: note it lived in was closed on 2026-09-06 and its text quoted into
#: `t2609011315`), and `yaml_move`'s is the shape `C-85`'s own mapping row took.
#: If a specimen stops matching, the form is broken however many candidates it
#: still counts, and the check says so instead of reporting a clean tree.
SPECIMENS = {
    "arrow": "the map keys `data/old` -> `data/old` for every artifact",
    "verb": "`snake_config_` is now `snake_config_`, which is the defect",
    "prose_rename": (
        "**What** - Rename every `project_config_*.yml` seed and template to "
        "`project_config_*.yml`, and update the `.gitignore` un-ignore glob"
    ),
    "yaml_move": (
        "      - old_path: T2.run_stress_test.spell_factors.dry\n"
        "        new_path: T2.run_stress_test.spell_factors.dry\n"
        "        op: rename\n"
    ),
    "python_rename_map": (
        'COPIED_CONFIG_PATH_MAP = {"config/a.yml": "config/a.yml"}\n'
    ),
}


def check_specimens(root: Path) -> list[str]:
    """Return one message per form that no longer flags its known-bad specimen.

    Run against a throwaway tree rather than by calling the matchers directly,
    so a form whose GLOB stopped reaching its file fails here too — which is
    the failure a direct regex call would sail past.
    """
    import tempfile

    failures = []
    with tempfile.TemporaryDirectory() as scratch:
        tree = Path(scratch)
        (tree / "dev" / "reference").mkdir(parents=True)
        (tree / "config" / "migrations").mkdir(parents=True)
        (tree / "dev" / "scripts").mkdir(parents=True)
        (tree / "dev" / "reference" / "specimen.md").write_text(
            "\n\n".join(SPECIMENS[form] for form in ("arrow", "verb", "prose_rename")),
            encoding="utf-8",
        )
        (tree / "config" / "migrations" / "specimen.yml").write_text(
            SPECIMENS["yaml_move"], encoding="utf-8"
        )
        (tree / "dev" / "scripts" / "specimen.py").write_text(
            SPECIMENS["python_rename_map"], encoding="utf-8"
        )
        flagged = set()
        for generator in (
            _line_forms(tree),
            _prose_rename_forms(tree),
            _yaml_move_forms(tree),
            _python_map_forms(tree),
        ):
            for form, _path, _lineno, _text, is_identity in generator:
                if is_identity:
                    flagged.add(form)
    for form in SPECIMENS:
        if form not in flagged:
            failures.append(
                f"{form}: its known-bad specimen is no longer flagged, so the "
                f"form is broken whatever its candidate count says"
            )
    return failures


def sweep(root: Path = REPO_ROOT):
    """Return ``(defects, allowed, observed)``.

    ``observed`` counts CANDIDATE records per form — every rename record the
    form recognised, whether or not its two sides matched. That is the number
    the floors are held against: a form finding no defects is only meaningful
    if it found records at all.
    """
    observed = {floor.name: 0 for floor in FLOORS}
    identical = []
    generators = (
        _line_forms(root),
        _prose_rename_forms(root),
        _yaml_move_forms(root),
        _python_map_forms(root),
    )
    for generator in generators:
        for form, path, lineno, line, is_identity in generator:
            observed[form] = observed.get(form, 0) + 1
            if is_identity:
                identical.append((path, lineno, line))
    defects, allowed = classify(identical, ALLOWANCES)
    return defects, allowed, observed


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--json", action="store_true", help="machine-readable output")
    args = parser.parse_args(argv)

    defects, allowed, observed = sweep()
    blind = check_floors(FLOORS, observed) + check_specimens(REPO_ROOT)

    if args.json:
        print(
            json.dumps(
                {
                    "defects": [
                        {"path": str(p.relative_to(REPO_ROOT)), "line": n, "text": t}
                        for p, n, t, _ in defects
                    ],
                    "allowed": len(allowed),
                    "observed": observed,
                    "blind": blind,
                },
                indent=1,
            )
        )
    elif blind:
        # Reported BEFORE the defect count, and instead of a clean bill: a form
        # that cannot see its records has no opinion about whether they are
        # intact, and saying "no defects" here is the fail-open shape.
        print("THIS CHECK IS BLIND and its result means nothing:\n")
        for message in blind:
            print(f"  {message}")
    else:
        totals = ", ".join(f"{k}={v}" for k, v in sorted(observed.items()))
        print(f"{sum(observed.values())} rename record(s) read ({totals}).")
        print(f"{len(allowed)} identical pair(s) classified as legitimate.")
        if defects:
            print(f"\n{len(defects)} RENAME RECORD(S) whose two sides are equal:\n")
            for path, lineno, text, _ in defects:
                print(f"  {path.relative_to(REPO_ROOT)}:{lineno}")
                print(f"      {text[:110]}")
        else:
            print("No decayed rename records.")
    return 1 if (defects or blind) else 0


if __name__ == "__main__":
    raise SystemExit(main())
