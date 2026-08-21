"""Propose a T1 + per-workflow T2 split of a project config, into a staging dir.

R13 migration tool. Run once, deliberately, against a pre-split project config::

    python scripts/split_project_config.py test_case/snake_config_rapid.yml
    python scripts/split_project_config.py <config.yml> --staging <dir>

**Report-only against your files.** The script never edits, moves or deletes the
config you point it at. It writes a *proposal* — the T1 file it would leave
behind, the T2 siblings it would create, and ``migration-report.md`` — into a
staging directory, and applying that proposal is an explicit step you take with
ordinary file operations you can diff. There is no ``--write`` and no in-place
mode. See ``docs/migration-config-tiers.md`` for the application step.

The config is split as **TEXT**, not round-tripped through ``yaml.safe_dump``.
A dump discards every comment in the file: the shipped template carries ~110 of
them and a real project's config carries the ones its author wrote, so dumping
would delete the annotations at exactly the moment a user is being asked to read
them. Same reasoning, and same mechanism, as ``suggest_experiment_name.py``.

Splitting text is also how this tool can corrupt a value rather than a comment,
which is why two checks bracket the transform:

* **it refuses documents it cannot split safely** (D-15.4a) — YAML anchors,
  aliases and merge keys become undefined or silently re-resolved once sections
  live in separate files, and a block scalar inside a workflow section loses
  four spaces of its own *content* to the dedent, changing a string with no
  structural symptom;
* **it verifies the staged pair against your file** before reporting it
  applicable (D-15.4b) — every run composes the staged T1 and asserts
  ``compose_config(staged_t1) == yaml.safe_load(source)``. On any mismatch the
  report says *do not apply*, names the first differing path, and the script
  exits nonzero.

A mangled comment is cosmetic. A mangled value produces a config that parses and
runs, so WF1 and WF2 would silently produce different numbers under an
unchanged-looking config and only WF3 would fail loudly, via the experiment
freeze. The whole output-neutrality claim of the migration rests on the pair of
checks above.
"""

from __future__ import annotations

import argparse
import os
import shutil
import sys
from collections.abc import Mapping
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from blueearth_cst.shared.config_composition import (  # noqa: E402
    HOISTED_SECTIONS,
    MIGRATION_DOC,
    load_composed_config,
)

#: The tool-owned staging directory name, and the sentinel that proves the tool
#: created it. Recursive replacement happens ONLY inside a directory passing
#: both tests — see `_claim_staging`.
STAGING_DIRNAME = "config-split-staged"
STAGING_MARKER = ".split-staging-owned"
STAGING_MARKER_TEXT = "created by scripts/split_project_config.py -- safe to delete\n"

REPORT_NAME = "migration-report.md"

#: The workflow whose T2 file owns each hoisted top-level section (D-10.4).
_HOIST_OWNER = {
    section: owner
    for owner, sections in HOISTED_SECTIONS.items()
    for section in sections
}


class SplitRefusal(Exception):
    """The document cannot be split safely, or the staging target is not ours."""


# ---------------------------------------------------------------------------
# Line helpers. Every function here works on lines WITH their endings, so a
# CRLF file stays CRLF -- the shipped seeds are CRLF and a silent conversion
# would put every line of every config into the migration diff.
# ---------------------------------------------------------------------------


def _is_blank(line: str) -> bool:
    return not line.strip()


def _is_comment(line: str) -> bool:
    return line.lstrip().startswith("#")


def _indent(line: str) -> int:
    return len(line) - len(line.lstrip(" "))


def _newline_of(lines: list[str]) -> str:
    """The line ending the source uses, for lines this tool adds itself."""
    for line in lines:
        if line.endswith("\r\n"):
            return "\r\n"
        if line.endswith("\n"):
            return "\n"
    return os.linesep


# ---------------------------------------------------------------------------
# D-15.4a -- refuse what a text split would corrupt
# ---------------------------------------------------------------------------


def _refuse_unsplittable(text: str, workflow_span: tuple[int, int] | None) -> None:
    """Raise if the document carries a construct a text split would break.

    Detected through PyYAML's own scanner rather than by grepping for ``&`` and
    ``*``: those characters are ordinary inside comments and strings, and a
    check that refused the shipped seeds for punctuation would be worse than no
    check. The scanner reports the real tokens, with real line numbers.

    Anchors, aliases and merge keys are refused **anywhere in the document** —
    an anchor in ``shared:`` aliased inside a workflow section becomes an
    undefined alias the moment the two land in different files, and a ``<<:``
    merge that re-resolves after the split changes values with no symptom at
    all. Block scalars are refused only **inside the workflows block**, because
    that is the only region this tool dedents.
    """
    try:
        tokens = list(yaml.scan(text))
    except yaml.YAMLError as exc:
        raise SplitRefusal(f"the source config is not valid YAML: {exc}") from exc

    found: list[str] = []
    for token in tokens:
        line = token.start_mark.line + 1
        if isinstance(token, yaml.tokens.AnchorToken):
            found.append(f"line {line}: YAML anchor `&{token.value}`")
        elif isinstance(token, yaml.tokens.AliasToken):
            found.append(f"line {line}: YAML alias `*{token.value}`")
        elif isinstance(token, yaml.tokens.ScalarToken):
            if token.value == "<<" and token.style is None:
                found.append(f"line {line}: YAML merge key `<<:`")
            elif token.style in ("|", ">") and workflow_span is not None:
                start, end = workflow_span
                if start <= token.start_mark.line < end:
                    found.append(
                        f"line {line}: block scalar `{token.style}` inside the "
                        "workflows block"
                    )
    if found:
        raise SplitRefusal(
            "this config uses YAML constructs a text split cannot carry across "
            "files safely, so nothing was staged:\n  "
            + "\n  ".join(found)
            + "\n\nSplit these sections by hand, or inline the construct first. "
            "An anchor defined in one section and aliased in another becomes an "
            "undefined alias once the sections are separate files; a block "
            "scalar loses four spaces of its own content to the dedent, which "
            f"changes the string with no structural symptom. See {MIGRATION_DOC}."
        )


def _refuse_already_split(source: Path, text: str) -> None:
    """Raise if every workflow stanza is already the closed two-key shape.

    Splitting a split config is not a no-op and not an error the round trip can
    see: the body of an already-migrated stanza is its ``config_path``, so a
    second pass would write *that key* into a new workflow file and repoint the
    stanza at it. The result composes back to the same document — the round trip
    passes — while the proposal is nonsense. The only thing that can catch it is
    recognising the migrated shape up front, which is the same closed-stanza
    test the loader uses as its migration detector.
    """
    doc = yaml.safe_load(text)
    workflows = (doc or {}).get("workflows") or {}
    stanzas = [s for s in workflows.values() if isinstance(s, Mapping)]
    if stanzas and all(set(s) <= {"enabled", "config_path"} for s in stanzas):
        raise SplitRefusal(
            f"{source} is already split: every workflow stanza carries only "
            "`enabled` and `config_path`, which is the migrated shape. There is "
            "nothing to propose — the settings are already in the per-workflow "
            f"files this file points at. See {MIGRATION_DOC}."
        )


# ---------------------------------------------------------------------------
# The text transform
# ---------------------------------------------------------------------------


def _top_level_span(
    lines: list[str], key: str, with_leading_comments: bool = False
) -> tuple[int, int] | None:
    """Return ``[start, end)`` line indices of a column-zero ``key:`` block.

    ``with_leading_comments`` absorbs the contiguous comment run directly above
    the key. It is set for a block that MOVES in its entirety — leaving the
    comment behind would put an explanation of a section into a file that no
    longer has it — and left off for ``workflows:``, whose stanzas stay put and
    keep their annotations with them.
    """
    start = None
    for index, line in enumerate(lines):
        if line.rstrip("\r\n") == f"{key}:" or line.startswith(f"{key}:"):
            if _indent(line) == 0 and not _is_comment(line):
                start = index
                break
    if start is None:
        return None
    end = len(lines)
    for index in range(start + 1, len(lines)):
        line = lines[index]
        if _is_blank(line) or _is_comment(line):
            continue
        if _indent(line) == 0:
            end = index
            break
    if with_leading_comments:
        while (
            start > 0
            and _is_comment(lines[start - 1])
            and _indent(lines[start - 1]) == 0
        ):
            start -= 1
    return start, end


def _section_spans(
    lines: list[str], workflow_span: tuple[int, int]
) -> dict[str, tuple[int, int, int]]:
    """Map each ``workflows.<name>`` to ``(header, body_start, body_end)``.

    A body line is blank, a comment, or indented at least four spaces. The body
    then gives back its trailing blank lines and any trailing comment run at the
    **header's own indent**: a comment sitting at two spaces immediately above
    the next ``<name>:`` introduces that next workflow, so it belongs to the
    stanza that stays in T1. A comment indented deeper is part of this body and
    travels with it — which is what carries a trailing annotation on the last
    section across, instead of stranding it.
    """
    start, end = workflow_span
    headers: list[tuple[str, int, int]] = []
    for index in range(start + 1, end):
        line = lines[index]
        if _is_blank(line) or _is_comment(line):
            continue
        stripped = line.strip()
        if _indent(line) == 2 and stripped.endswith(":"):
            headers.append((stripped[:-1].strip(), index, _indent(line)))

    spans: dict[str, tuple[int, int, int]] = {}
    for position, (name, header, header_indent) in enumerate(headers):
        limit = headers[position + 1][1] if position + 1 < len(headers) else end
        body_end = limit
        while body_end > header + 1:
            line = lines[body_end - 1]
            if _is_blank(line):
                body_end -= 1
            elif _is_comment(line) and _indent(line) <= header_indent:
                body_end -= 1
            else:
                break
        spans[name] = (header, header + 1, body_end)
    return spans


def _dedent(lines: list[str], amount: int = 4) -> list[str]:
    """Strip up to ``amount`` leading spaces, leaving blank lines untouched."""
    out = []
    for line in lines:
        if _is_blank(line):
            out.append(line.lstrip(" "))
        else:
            out.append(line[min(amount, _indent(line)) :])
    return out


def _drop_enabled(lines: list[str]) -> list[str]:
    """Remove the (already dedented) ``enabled:`` line. It is T1-owned."""
    return [
        line
        for line in lines
        if not (_indent(line) == 0 and line.lstrip().startswith("enabled:"))
    ]


def _has_content(lines: list[str]) -> bool:
    return any(not _is_blank(line) and not _is_comment(line) for line in lines)


class Proposal:
    """What the split would produce, before anything touches the filesystem."""

    def __init__(self, source: Path) -> None:
        self.source = source
        self.t1_text = ""
        self.t2_texts: dict[str, str] = {}
        self.dispositions: list[str] = []
        self.notes: list[str] = []
        self.stem = source.stem

    def t2_name(self, workflow: str) -> str:
        return f"{self.stem}_{workflow}.yml"


def build_proposal(source: Path) -> Proposal:
    """Compute the staged T1 and T2 contents. Pure: reads ``source`` and nothing else."""
    with open(source, encoding="utf-8", newline="") as handle:
        text = handle.read()
    lines = text.splitlines(keepends=True)
    newline = _newline_of(lines)
    proposal = Proposal(source)

    workflow_span = _top_level_span(lines, "workflows")
    _refuse_unsplittable(text, workflow_span)
    if workflow_span is None:
        raise SplitRefusal(
            f"{source}: no top-level `workflows:` section — this is not a "
            "full-orchestration project config, and there is nothing to split."
        )

    spans = _section_spans(lines, workflow_span)
    if not spans:
        raise SplitRefusal(f"{source}: the `workflows:` block declares no workflow.")
    _refuse_already_split(source, text)

    # `reporting:` moves into its owning workflow's file, verbatim and undedented
    # (it is already at column zero). A COMMENTED block is reported, never moved:
    # a text splitter that relocated comments it could not parse would be
    # guessing, and the template's commented example is rewritten by hand.
    hoist_texts: dict[str, str] = {}
    hoist_spans: list[tuple[int, int]] = []
    for section, owner in _HOIST_OWNER.items():
        span = _top_level_span(lines, section, with_leading_comments=True)
        if span is not None:
            hoist_texts[owner] = "".join(lines[span[0] : span[1]])
            hoist_spans.append(span)
            proposal.dispositions.append(
                f"- `{section}:` moved from the project file's top level into "
                f"`{proposal.t2_name(owner)}` (the loader hoists it back, so "
                '`config["{0}"]` is unchanged)'.format(section)
            )
        elif any(
            line.lstrip().startswith(f"#{section}:")
            or line.lstrip().startswith(f"# {section}:")
            for line in lines
        ):
            proposal.notes.append(
                f"- a COMMENTED `#{section}:` block is present and was NOT "
                f"moved. Uncommenting it in the project file is now a parse "
                f"error: it belongs at the top level of "
                f"`{proposal.t2_name(owner)}`. Move it by hand if you want it."
            )

    # T2 bodies.
    emitted: dict[str, str] = {}
    for name, (_, body_start, body_end) in spans.items():
        body = _drop_enabled(_dedent(lines[body_start:body_end]))
        while body and _is_blank(body[0]):
            body.pop(0)
        while body and _is_blank(body[-1]):
            body.pop()
        extra = hoist_texts.get(name, "")
        if not _has_content(body) and not extra:
            proposal.dispositions.append(
                f"- `workflows.{name}` has no settings once `enabled:` is "
                "removed, so **no file is written and no `config_path` key is "
                "added** — an omitted key composes to an empty section, which "
                "is what an empty file would have meant anyway"
            )
            if body:
                proposal.notes.append(
                    f"- `workflows.{name}` carried only comments; they are not "
                    "carried into a file that is not created"
                )
            continue
        chunk = "".join(body)
        if chunk and not chunk.endswith(("\n", "\r")):
            chunk += newline
        if extra:
            if chunk:
                chunk += newline
            chunk += extra
            if not chunk.endswith(("\n", "\r")):
                chunk += newline
        emitted[name] = chunk
        proposal.dispositions.append(
            f"- `workflows.{name}` → `{proposal.t2_name(name)}`"
        )
    proposal.t2_texts = emitted

    # The staged T1: each section body replaced by its `config_path`, and any
    # hoisted top-level block removed.
    drop: set[int] = set()
    inserts: dict[int, str] = {}
    for name, (header, body_start, body_end) in spans.items():
        keep = [
            line
            for line in lines[body_start:body_end]
            if _indent(line) == 4 and line.lstrip().startswith("enabled:")
        ]
        drop.update(range(body_start, body_end))
        replacement = "".join(keep)
        if name in emitted:
            replacement += f"    config_path: {proposal.t2_name(name)}{newline}"
        inserts[header] = replacement
    for start, end in hoist_spans:
        drop.update(range(start, end))

    out: list[str] = []
    for index, line in enumerate(lines):
        if index in drop:
            continue
        out.append(line)
        if index in inserts:
            out.append(inserts[index])
    proposal.t1_text = "".join(out)
    return proposal


# ---------------------------------------------------------------------------
# D-15.3a -- the staging-ownership contract
# ---------------------------------------------------------------------------


def _is_ancestor(candidate: Path, of: Path) -> bool:
    """True when ``candidate`` is ``of`` or contains it, compared normcase-abspath."""
    a = os.path.normcase(os.path.abspath(candidate))
    b = os.path.normcase(os.path.abspath(of))
    return a == b or b.startswith(a + os.sep)


def _claim_staging(target: Path, source_dir: Path) -> Path:
    """Return a staging directory this tool owns, creating or replacing it.

    The recursive replacement below is the only destructive act in a tool whose
    whole posture is report-only, so it is bound to a directory the tool can
    PROVE it created: the right basename **and** the sentinel at its root.
    Nothing else is replaced. An existing, non-empty, unmarked target is a
    refusal — without that binding, a mistaken ``--staging`` argument could
    recursively delete unrelated files, which is precisely the harm the
    report-only posture exists to prevent.
    """
    if _is_ancestor(target, source_dir):
        raise SplitRefusal(
            f"refusing to stage into {target} — it is the config's own "
            "directory or an ancestor of it. Staging there would put proposed "
            "files beside the originals they replace, where a half-applied "
            "migration is indistinguishable from a finished one."
        )
    if target.exists():
        if not target.is_dir():
            raise SplitRefusal(f"refusing to stage into {target} — not a directory.")
        entries = list(target.iterdir())
        if entries:
            owned = (
                target.name == STAGING_DIRNAME and (target / STAGING_MARKER).is_file()
            )
            if not owned:
                raise SplitRefusal(
                    f"refusing to replace {target} — it is not empty and this "
                    f"tool did not create it. A directory is replaceable only "
                    f"when its name is {STAGING_DIRNAME!r} AND it carries the "
                    f"{STAGING_MARKER!r} marker at its root. Point --staging "
                    "somewhere else, or delete that directory yourself."
                )
            shutil.rmtree(target)
    target.mkdir(parents=True, exist_ok=True)
    (target / STAGING_MARKER).write_text(STAGING_MARKER_TEXT, encoding="utf-8")
    return target


# ---------------------------------------------------------------------------
# D-15.4b -- verify the staged pair against the source
# ---------------------------------------------------------------------------


def _first_difference(left: object, right: object, path: str = "") -> str | None:
    """Return a dotted path to the first difference, or ``None`` if equal."""
    if isinstance(left, dict) and isinstance(right, dict):
        for key in sorted(set(left) | set(right)):
            where = f"{path}.{key}" if path else str(key)
            if key not in left:
                return f"{where} (missing after the split)"
            if key not in right:
                return f"{where} (added by the split)"
            deeper = _first_difference(left[key], right[key], where)
            if deeper:
                return deeper
        return None
    if left != right:
        return f"{path or '<document>'}: {left!r} != {right!r}"
    return None


def verify_round_trip(staged_t1: Path, source: Path) -> str | None:
    """Compose the staged pair and compare it to the source. ``None`` means clean.

    This is the check that makes a proposal applicable. It composes the STAGED
    T1 — whose emitted ``config_path`` values are bare filenames and therefore
    resolve to the staged siblings under the T1-anchored rule — so the thing
    verified is the thing you would apply, not a re-derivation of it.
    """
    with open(source, encoding="utf-8", newline="") as handle:
        original = yaml.safe_load(handle.read())
    try:
        composed = load_composed_config(staged_t1)
    except ValueError as exc:
        return f"the staged proposal does not compose: {exc}"
    return _first_difference(composed, original)


# ---------------------------------------------------------------------------
# Report and entry point
# ---------------------------------------------------------------------------


def _report(proposal: Proposal, staging: Path, verdict: str | None) -> str:
    lines = [
        f"# Config split proposal for `{proposal.source.name}`",
        "",
        "Nothing in your project was changed. Everything below is a proposal "
        f"staged in `{staging}`.",
        "",
        "## Per-section disposition",
        "",
        *proposal.dispositions,
        "",
    ]
    if proposal.notes:
        lines += ["## Notes", "", *proposal.notes, ""]
    if verdict is None:
        lines += [
            "## Verification — CLEAN",
            "",
            "The staged project file plus its workflow files compose back to "
            "exactly the document you started from, key for key. Safe to apply.",
            "",
            "## To apply",
            "",
            "1. Read the staged files and diff the project file against your own.",
            f"2. Move the workflow files beside `{proposal.source.name}`.",
            f"3. Replace `{proposal.source.name}` with the staged project file.",
            "4. Dry-run any enabled workflow — that runs every composition and "
            "seam check, so a mis-applied proposal fails loudly before anything "
            "executes.",
            "",
            f"See `{MIGRATION_DOC}`.",
        ]
    else:
        lines += [
            "## Verification — DO NOT APPLY",
            "",
            "The staged proposal does not compose back to your config. The "
            "staged files are kept so you can diagnose it, but applying them "
            "would change what your workflows read.",
            "",
            f"First difference: `{verdict}`",
            "",
            f"Please report this with your config, and see `{MIGRATION_DOC}`.",
        ]
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Propose a T1 + per-workflow T2 split of a project config."
    )
    parser.add_argument("config", help="path to the project config YAML to split")
    parser.add_argument(
        "--staging",
        default=None,
        help=(
            "directory to stage the proposal UNDER; the tool always works in a "
            f"{STAGING_DIRNAME!r} child of it. Default: beside the config."
        ),
    )
    args = parser.parse_args(argv)

    source = Path(args.config)
    if not source.is_file():
        print(f"error: no such config file: {source}", file=sys.stderr)
        return 1
    source_dir = source.resolve().parent
    parent = Path(args.staging) if args.staging else source_dir
    staging = parent / STAGING_DIRNAME

    try:
        proposal = build_proposal(source)
        staging = _claim_staging(staging, source_dir)
    except SplitRefusal as exc:
        print(f"refused: {exc}", file=sys.stderr)
        return 1

    staged_t1 = staging / source.name
    with open(staged_t1, "w", encoding="utf-8", newline="") as handle:
        handle.write(proposal.t1_text)
    for name, chunk in proposal.t2_texts.items():
        with open(
            staging / proposal.t2_name(name), "w", encoding="utf-8", newline=""
        ) as handle:
            handle.write(chunk)

    verdict = verify_round_trip(staged_t1, source)
    (staging / REPORT_NAME).write_text(
        _report(proposal, staging, verdict), encoding="utf-8"
    )

    print(f"staged a proposal in {staging}")
    print(f"  read {REPORT_NAME} before applying anything")
    if verdict is not None:
        print(f"  VERIFICATION FAILED — do not apply: {verdict}", file=sys.stderr)
        return 1
    print("  verification clean: the staged pair composes back to your config")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
