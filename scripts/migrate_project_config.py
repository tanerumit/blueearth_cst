"""Rewrite a v1 project config SET to v2, preserving comments.

The command every R14 refusal message names
(``config_composition.MIGRATION_COMMAND``). Point it at a project's T1 file and
it migrates that file and every workflow file it declares.

**Driven by data, not by code.** Every key move lives in
``config/migrations/v1_to_v2.yml`` (design D-11.2a), which
``tests/test_migration_mapping.py`` holds against the register and against the
loader's own ``RETIRED_KEYS``. Adding a row here means editing that file, never
this one — and a row this module cannot execute fails that test rather than
failing a user's project.

**Comments survive** (D-11.8). ``ruamel.yaml``'s round-trip loader is the whole
reason this is not fifteen lines of ``safe_load`` + ``safe_dump``: a dump-based
rewriter deletes 86 of the 109 lines in the shipped template and every
annotation a user ever wrote. The round-trip is confined to this tool; nothing
else in the toolbox imports it.

**Not a sibling of R13's splitter, which no longer exists.** P3's brief says to
build this beside ``scripts/split_project_config.py`` and not to modify it. P1
retired that script (``068b81dd``) when the hoist mechanism went, so there is
nothing to sit beside and nothing to avoid modifying.

**The transaction is D-11.2b**, and its order is the point: `N8`'s refusal
can fire on the THIRD file of a set, so nothing is written until every file has
been read, every move resolved and every hook evaluated. Then stage beside the
project, validate the staged set through the loader a real run uses, and only
then commit — keeping the originals as ``*.v1.bak``, because a migration a user
wants to undo is a migration they can undo.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

MAPPING_PATH = REPO_ROOT / "config" / "migrations" / "v1_to_v2.yml"

#: The v2 the mapping targets. Stamped by `C-05`.
SCHEMA_VERSION = 2


class MigrationError(Exception):
    """A refusal. Carries a message a user can act on, never a traceback."""


# ---------------------------------------------------------------------------
# Value transforms — one per `value_transform` the mapping may name
# ---------------------------------------------------------------------------
#
# Each takes the v1 value and returns the v2 value. They are pure and take no
# document context, with one exception (`scalar_to_var_mapping`) that needs the
# declared outvars; that one takes them explicitly rather than reaching for a
# global, so a caller cannot forget to supply them.


def identity(value, **_):
    return value


def iso_to_year(value, **_):
    """``{starttime, endtime}`` ISO strings → ``{start, end}`` INCLUSIVE years.

    Refuses a value that is not whole-year aligned rather than truncating it.
    Truncating would move the window silently, which is the one outcome a
    migration must never produce: the user would get a run over a different
    period than the one they configured, with nothing said.
    """
    if not isinstance(value, dict):
        raise MigrationError(
            f"expected a mapping with starttime/endtime, got {value!r}"
        )
    out = {}
    for old, new, expected_suffix in (
        ("starttime", "start", "-01-01T00:00:00"),
        ("endtime", "end", "-12-31T00:00:00"),
    ):
        if old not in value:
            raise MigrationError(f"window is missing `{old}`: {value!r}")
        raw = str(value[old])
        year, _, rest = raw.partition("-")
        if not year.isdigit() or f"-{rest}" != expected_suffix:
            raise MigrationError(
                f"`{old}: {raw}` is not whole-year aligned. The v2 form is "
                f"INCLUSIVE YEARS, and this window does not start or end on a "
                f"year boundary, so no year pair reproduces it. Expected "
                f"`YYYY{expected_suffix}`."
            )
        out[new] = int(year)
    return out


def bool_to_enum(value, *, enum, **_):
    """``transient_change: true|false`` → the `C-32` trajectory enum.

    ``enum`` comes from the MAPPING, not from this module. `C-32`'s two
    spellings are unresolved (the register says ``transient | constant``,
    shipped code says ``transient | step``), and putting the pair in data means
    ruling it is a one-line change to the mapping rather than an edit here.
    """
    if not isinstance(value, bool):
        raise MigrationError(
            f"`transient_change` must be a boolean, got {value!r}. A config "
            "that already carries the enum is not a v1 config."
        )
    ramped, stepped = sorted(enum, key=lambda v: v != "transient")
    return ramped if value else stepped


def step_num_to_n_levels(value, **_):
    """`C-31`: INTERVALS → LEVELS, which is the count plus one.

    The `+ 1` is the entire row. A migration that renamed the key without it
    would halve every axis, and the resulting config is valid, so nothing
    downstream would notice.
    """
    if isinstance(value, bool) or not isinstance(value, int):
        raise MigrationError(f"`step_num` must be a whole number, got {value!r}")
    if value < 0:
        raise MigrationError(f"`step_num` must be non-negative, got {value}")
    return value + 1


def pair_to_window(value, **_):
    """``[a, b]`` → ``{start: a, end: b}`` (`C-59`)."""
    if not isinstance(value, (list, tuple)) or len(value) != 2:
        raise MigrationError(f"expected a two-element [start, end] list, got {value!r}")
    return {"start": value[0], "end": value[1]}


def list_to_named_windows(value, **_):
    """``{name: [a, b]}`` → ``[{start, end, name}]`` (`C-60`, `C-61`).

    The name is CARRIED, never dropped: it becomes a figure directory, so a
    project that named its windows keeps the directories it already has.
    """
    if not isinstance(value, dict):
        raise MigrationError(
            f"expected a mapping of name -> [start, end], got {value!r}"
        )
    out = []
    for name, pair in value.items():
        window = pair_to_window(pair)
        window["name"] = name
        out.append(window)
    return out


def list_to_preference_group(value, **_):
    """``members: [m, ...]`` → ``members: {preference: [m, ...]}`` (`C-63`)."""
    if not isinstance(value, (list, tuple)):
        raise MigrationError(f"expected a list of members, got {value!r}")
    return {"preference": list(value)}


def scalar_to_var_mapping(value, *, outvars=None, **_):
    """One path → ``{<variable>: path}``, keyed by variable (`C-56`, D-7.3).

    The variable is ``river discharge`` because that is the only one rule 1.15
    consumes; the key must nonetheless come from ``model.outvars``, so a project
    whose outvars do not include it is refused rather than given a mapping the
    loader will reject.
    """
    if value is None:
        return None
    discharge = "river discharge"
    if outvars is not None and discharge not in outvars:
        raise MigrationError(
            f"`observations_timeseries` is set, but `{discharge}` is not in "
            f"`model.outvars` ({sorted(outvars)}). `C-56` keys observations by "
            "variable, and the loader refuses a key that is not a declared "
            "outvar — so this project must declare the outvar or drop the "
            "observations."
        )
    return {discharge: value}


def horizon_length_to_window(values, **_):
    """`C-67`: ``horizontime_climate`` + ``run_length`` → ``{start, end}``.

    A ROW-LEVEL transform: it takes both v1 keys at once, because neither alone
    determines the window. That is why `C-67`'s row carries ``collapse: true``
    and why the mapping's flat one-key-per-move shape could not express it.

    **This reproduces the arithmetic `C-72` deleted, on purpose.** The run path
    no longer derives a window from a horizon and a length — the config declares
    it. But a v1 config only says ``2050`` and ``8``, and the window that run
    ACTUALLY used was ``ceil`` backwards and ``round`` forwards from the centre,
    giving 2046..2054 — NINE calendar years for a length of eight. Emitting
    ``2046..2054`` is what makes the migration value-preserving; emitting
    ``2046..2053`` would quietly shorten every migrated project's run.

    Half-to-even on the forward half, matching ``np.round``, because that is
    what the landed window used. Implemented here rather than imported: this is
    the MIGRATION's knowledge of a retired behaviour, and the run path is
    entitled to forget it.
    """
    horizon = values.get("horizontime_climate")
    length = values.get("run_length")
    if horizon is None:
        raise MigrationError(
            "`horizontime_climate` is required to build `simulation_window`; "
            "without it there is no centre to place the window around."
        )
    if length is None:
        length = 20  # the shipped default the Snakefile applied
    if not isinstance(horizon, (int, float)) or not isinstance(length, (int, float)):
        raise MigrationError(
            f"expected numbers, got horizon={horizon!r} length={length!r}"
        )
    import math

    half = length / 2
    start = int(horizon - math.ceil(half))
    # half-to-even, as `np.round` does — `round()` in Python 3 already is.
    end = int(horizon + round(half))
    return {"start": start, "end": end}


def union_with_selected(values, **_):
    """`C-43`: the candidate list absorbs the source that used to be privileged.

    v1 had TWO keys with an asymmetry between them: ``shared.clim_historical``
    named the dataset the model was built and run on, and
    ``analyze_climate.candidate_sources`` listed the OTHERS, to compare it
    against. v2's ``climate.sources`` is "the full candidate set with no
    privileged element", and ``climate.selected`` names one MEMBER of it.

    So a straight copy produces a config the loader refuses — ``selected: era5``
    against ``sources: [chirps]`` — which is exactly what happened, and what the
    staged-set validation caught before anything was written. The union is the
    only reading that preserves what the project meant: every dataset it named,
    with the one it ran on still identified.

    ``clim_historical`` is READ here and consumed by `C-44`, which is why this
    row declares it under ``collapse_reads`` rather than as a move: two rows
    need the value and only one may remove it.
    """
    candidates = values.get("candidate_sources") or []
    selected = values.get("clim_historical")
    if not isinstance(candidates, (list, tuple)):
        raise MigrationError(f"`candidate_sources` must be a list, got {candidates!r}")
    ordered = [selected] if selected is not None else []
    for entry in candidates:
        if entry not in ordered:
            ordered.append(entry)
    if not ordered:
        raise MigrationError(
            "neither `clim_historical` nor `candidate_sources` is set, so there "
            "is no climate source to carry into `climate.sources`."
        )
    return ordered


TRANSFORMS = {
    "identity": identity,
    "iso_to_year": iso_to_year,
    "bool_to_enum": bool_to_enum,
    "step_num_to_n_levels": step_num_to_n_levels,
    "pair_to_window": pair_to_window,
    "list_to_named_windows": list_to_named_windows,
    "list_to_preference_group": list_to_preference_group,
    "scalar_to_var_mapping": scalar_to_var_mapping,
    "horizon_length_to_window": horizon_length_to_window,
    "union_with_selected": union_with_selected,
}


# ---------------------------------------------------------------------------
# Path helpers — dotted paths against a round-trip document
# ---------------------------------------------------------------------------


def _walk(doc: Any, parts: list[str]):
    """Return the container holding ``parts[-1]``, or None if the path is absent."""
    node = doc
    for part in parts[:-1]:
        if not isinstance(node, dict) or part not in node:
            return None
        node = node[part]
    return node if isinstance(node, dict) else None


def get_path(doc, dotted: str):
    parts = dotted.split(".")
    holder = _walk(doc, parts)
    if holder is None or parts[-1] not in holder:
        return None, False
    return holder[parts[-1]], True


def pop_path(doc, dotted: str):
    """Remove a key and return ``(value, present)``.

    The key's COMMENT is detached here and handed to :func:`take_comment`
    separately, rather than being dropped: see D-14.9.
    """
    parts = dotted.split(".")
    holder = _walk(doc, parts)
    if holder is None or parts[-1] not in holder:
        return None, False
    return holder.pop(parts[-1]), True


def take_comment(doc, dotted: str):
    """Detach and return the ruamel comment token attached to a key, if any.

    ``ruamel`` hangs a key's comment off its PARENT mapping's ``.ca.items``,
    keyed by the key's own name — so moving a value between mappings loses the
    comment unless it is carried across explicitly. That is why
    `analyze_projections`' whole comment block disappeared on the first run of
    this tool: every key in that file is renamed, and every rename dropped its
    annotation.

    Returns None for a plain dict (the unit tests) or a key with no comment.
    """
    parts = dotted.split(".")
    holder = _walk(doc, parts)
    if holder is None:
        return None
    comments = getattr(holder, "ca", None)
    if comments is None:
        return None
    return comments.items.pop(parts[-1], None)


def give_comment(doc, dotted: str, token) -> None:
    """Re-attach a comment token to a key at its new home."""
    if token is None:
        return
    parts = dotted.split(".")
    holder = _walk(doc, parts)
    comments = getattr(holder, "ca", None)
    if comments is None:
        return
    comments.items[parts[-1]] = token


def set_path(doc, dotted: str, value, *, on_collision: str, row_id: str):
    """Create intermediate mappings as needed, honouring ``on_collision``."""
    parts = dotted.split(".")
    node = doc
    for part in parts[:-1]:
        if part not in node or not isinstance(node[part], dict):
            # Same TYPE as the parent, so a round-trip document keeps building
            # round-trip containers and the dump stays formatted.
            node[part] = type(node)() if hasattr(node, "ca") else {}
        node = node[part]
    leaf = parts[-1]
    if leaf in node:
        if on_collision == "refuse":
            raise MigrationError(
                f"{row_id}: `{dotted}` already exists. A destination that is "
                "already present means the set is partly migrated, which is a "
                "state to look at rather than write over."
            )
        if on_collision == "keep_existing":
            return
    node[leaf] = value


def load_mapping(path: Path = MAPPING_PATH) -> dict:
    """The mapping, as data. Uses safe_load: nothing writes this file back."""
    import yaml

    return yaml.safe_load(path.read_text(encoding="utf-8"))


def live_moves(mapping: dict):
    """``(row, move)`` for every executable move, in register order."""
    for row in mapping["rows"]:
        if row.get("status") != "live":
            continue
        for move in row.get("moves") or []:
            yield row, move


def split_tier(dotted: str):
    """``T1.a.b`` → ``("T1", None, "a.b")``; ``T2.wf.a`` → ``("T2", "wf", "a")``.

    The tier prefix is part of the mapping's vocabulary, not of any document, so
    it is stripped here rather than being carried into the path helpers.
    """
    parts = dotted.split(".")
    if parts[0] == "T1":
        return "T1", None, ".".join(parts[1:])
    if parts[0] == "T2":
        return "T2", parts[1], ".".join(parts[2:])
    raise MigrationError(f"path `{dotted}` names neither T1 nor T2")


def _depth(move) -> int:
    """Sort key. Three bands, and the middle one is the whole point.

    * **Renames and regroups, shallowest first** (band 0-49). A section must
      move before the keys inside it, so `C-68` renames `stress_test:` before
      `C-31` reaches into it.
    * **Collapse rows** (90). They read several keys at once and cannot be a
      parent of anything, so they are safe to run after the ordinary moves.
    * **Deletes, LAST** (95). This is the band that matters. `C-01` deletes the
      `shared:` SECTION, and six other rows (`C-10`, `C-19`, `C-44`, `C-51`,
      `C-53`, `C-70`) move keys OUT of it. Sorted by depth alone, `C-01` is the
      shallowest live move in the whole mapping and runs first — deleting the
      section before anything is extracted, so a migrated project silently loses
      its basin, its climate window, its outvars and its seed. The config that
      comes out is VALID, which is what makes it dangerous.

    A delete has nothing to hand to a later row, so running it last costs
    nothing and removes the whole class of ordering hazard.
    """
    if move is None:
        return 90
    old = move.get("old_path")
    if old is None:
        return 0
    if move.get("new_path") is None:
        return 95
    return old.count(".")


def _follow(dotted: str, renames: dict[str, str]) -> str:
    """Rewrite a v1 path through the renames already applied.

    `C-31`'s source is `...stress_test.temp.step_num`, but by the time it runs
    `C-68` has renamed that section. Without this the lookup misses and the row
    silently does nothing, which is the worst available outcome: a valid config
    that kept a v1 spelling nothing reads.
    """
    for old_prefix, new_prefix in renames.items():
        if dotted == old_prefix or dotted.startswith(old_prefix + "."):
            return new_prefix + dotted[len(old_prefix) :]
    return dotted


def migrate_set(t1, t2_by_workflow, mapping, *, outvars=None):
    """Apply every live move to one config set, in register order.

    Returns ``(t1, t2_by_workflow, report)``; the documents are mutated in
    place, which is what lets a round-trip loader keep its comments.

    ``report`` lists what happened, one line per applied move. It is the
    material Gate 3 asks to see and the material `C-69`'s warning is drawn
    from, so it is built here rather than printed.

    **A move whose source is absent is skipped, not defaulted.** An optional key
    the project never declared must stay undeclared: writing the default would
    turn a config that inherited a value into one that pins it, and the two
    behave differently the next time the default moves.
    """
    report = []
    wildcard_workflows = tuple(t2_by_workflow)
    renames: dict[str, str] = {}

    # **Shallowest path first, and it is not cosmetic.** `C-68` renames the
    # `stress_test:` SECTION while `C-31` and `C-32` move keys INSIDE it. In
    # register order the nested rows run first, create `climate_perturbations`
    # as a side effect of writing into it, and `C-68` then collides with a
    # destination the migration itself just made. Applying parents first, and
    # rewriting each child's path through the renames already performed, is
    # what makes a section rename and its contents one coherent operation.
    #
    # Depth is a partial order and a stable sort keeps register order within
    # each depth, so the report still reads in register order for every row
    # that has no parent/child relationship — which is all but two of them.
    ordered = []
    for row in mapping["rows"]:
        if row.get("status") != "live":
            continue
        if row.get("collapse"):
            ordered.append((row, None))
            continue
        for move in row.get("moves") or []:
            ordered.append((row, move))
    ordered.sort(key=lambda pair: _depth(pair[1]))

    for row, move in ordered:
        if move is None:
            _apply_collapse(row, t1, t2_by_workflow, report, renames)
            continue
        _apply_move(
            row,
            move,
            t1,
            t2_by_workflow,
            report,
            outvars,
            wildcard_workflows,
            renames,
        )

    t1["schema_version"] = SCHEMA_VERSION
    report.append(f"C-05: stamped `schema_version: {SCHEMA_VERSION}`")
    return t1, t2_by_workflow, report


def _apply_collapse(row, t1, t2_by_workflow, report, renames):
    """A row whose moves share ONE destination and must be read together.

    `C-67` is the only such row today. Handled as its own path rather than as a
    special case inside the per-move loop, because the per-move loop's contract
    — read one key, transform it, write it — is not true of these and pretending
    otherwise is how a collapse silently drops half its input.
    """
    moves = row["moves"]
    destinations = {m["new_path"] for m in moves}
    if len(destinations) != 1:
        raise MigrationError(
            f"{row['id']} is marked `collapse` but its moves name "
            f"{len(destinations)} destinations: {sorted(destinations)}"
        )
    dest_dotted = destinations.pop()

    values, sources = {}, []
    for move in moves:
        tier, workflow, path = split_tier(_follow(move["old_path"], renames))
        doc = t1 if tier == "T1" else t2_by_workflow.get(workflow)
        if doc is None:
            continue
        value, present = get_path(doc, path)
        if present:
            # Keyed by the ORIGINAL v1 leaf, not the followed one. A
            # transform is written against the mapping it appears in, so
            # it must not have to know which other rows have already
            # relocated its inputs.
            values[move["old_path"].split(".")[-1]] = value
            sources.append(move["old_path"])

    # Paths this row READS but does not consume, because another row owns the
    # removal. `C-43` needs `clim_historical`'s value; `C-44` is what moves it.
    for dotted in row.get("collapse_reads") or []:
        tier, workflow, path = split_tier(_follow(dotted, renames))
        doc = t1 if tier == "T1" else t2_by_workflow.get(workflow)
        if doc is None:
            continue
        value, present = get_path(doc, path)
        if present:
            values[dotted.split(".")[-1]] = value

    if not values:
        return

    transform = TRANSFORMS[row["collapse_transform"]]
    try:
        converted = transform(values)
    except MigrationError as exc:
        raise MigrationError(f"{row['id']} on {sources}: {exc}") from None

    for move in moves:
        tier, workflow, path = split_tier(_follow(move["old_path"], renames))
        target = t1 if tier == "T1" else t2_by_workflow.get(workflow)
        if target is not None:
            pop_path(target, path)

    new_tier, new_workflow, new_path = split_tier(dest_dotted)
    dest = t1 if new_tier == "T1" else t2_by_workflow[new_workflow]
    set_path(
        dest,
        new_path,
        converted,
        on_collision=moves[0]["on_collision"],
        row_id=row["id"],
    )
    report.append(f"{row['id']}: {sources} -> `{dest_dotted}` = {converted}")


def _apply_move(
    row, move, t1, t2_by_workflow, report, outvars, wildcard_workflows, renames
):
    """One key: read it, transform it, write it where the mapping says.

    A move whose source is ABSENT is skipped, not defaulted. An optional key the
    project never declared must stay undeclared — writing the default would turn
    a config that inherits a value into one that pins it, and those two behave
    differently the next time the default moves.
    """
    old = move.get("old_path")
    new = move.get("new_path")
    if old is None:
        return  # `op: new` — the transactional wrapper stamps these

    tier, workflow, path = split_tier(_follow(old, renames))
    if tier == "T1":
        targets = [(None, t1)]
    elif workflow == "*":
        # `T2.*.reporting` (C-77) applies to every workflow file in the set.
        targets = [(name, t2_by_workflow[name]) for name in wildcard_workflows]
    else:
        targets = [(workflow, t2_by_workflow.get(workflow))]

    for name, doc in targets:
        if doc is None:
            continue
        value, present = get_path(doc, path)
        if not present:
            continue

        if new is None:
            # **A deleted key takes its comment with it** (D-14.9). The
            # alternative — reattaching it to the next key — is worse: the
            # comment explains a setting that no longer exists, and it would now
            # appear to describe an unrelated one. `static_dir` and
            # `run_historical` are the two this rule is written for.
            take_comment(doc, path)
            pop_path(doc, path)
            where = f" from {name}" if name else ""
            report.append(f"{row['id']}: removed `{path}`{where}")
            continue

        transform = TRANSFORMS[move["value_transform"]]
        try:
            converted = transform(value, enum=row.get("enum"), outvars=outvars)
        except MigrationError as exc:
            raise MigrationError(f"{row['id']} on `{old}`: {exc}") from None

        new_tier, new_workflow, new_path = split_tier(new)
        if new_tier == "T1":
            dest = t1
        else:
            dest = t2_by_workflow.get(name if new_workflow == "*" else new_workflow)
        if dest is None:
            raise MigrationError(
                f"{row['id']}: `{new}` names workflow file `{new_workflow}`, "
                "which this set does not declare."
            )

        comment = take_comment(doc, path)
        pop_path(doc, path)
        set_path(
            dest,
            new_path,
            converted,
            on_collision=move["on_collision"],
            row_id=row["id"],
        )
        give_comment(dest, new_path, comment)
        # EVERY move is recorded, not only section moves. A later row may
        # still name the v1 path — either because it reaches INSIDE a
        # renamed section (`C-31` after `C-68`), or because it READS a
        # scalar another row has already moved (`C-43` reads
        # `clim_historical`, which `C-44` relocates). Recorded against the
        # original v1 spelling, because that is what the mapping names.
        renames[old] = new
        report.append(f"{row['id']}: `{old}` -> `{new}`")


# ---------------------------------------------------------------------------
# The transaction (D-11.2b)
# ---------------------------------------------------------------------------


def _yaml():
    """A round-trip YAML handler. **The reason comments survive** (D-11.8).

    A `safe_load` + `safe_dump` rewriter deletes 86 of the 109 lines in the
    shipped template and every annotation a user ever wrote, while passing every
    other check in this file. Confined to this tool; nothing else in the toolbox
    imports ruamel.
    """
    from ruamel.yaml import YAML

    handler = YAML()
    handler.preserve_quotes = True
    # The shipped configs are hand-written and wrap wide; keeping the width
    # large stops the dump from re-flowing lines nobody asked it to touch.
    handler.width = 4096
    return handler


def discover_set(t1_path: Path):
    """Return ``(t1_path, {workflow: path})`` for a project's complete set.

    A ``config_path`` resolves against the T1 file's OWN directory, which is the
    rule the loader uses; resolving it against the working directory would find
    a different file depending on where the command was run from.
    """
    handler = _yaml()
    with t1_path.open(encoding="utf-8") as handle:
        t1 = handler.load(handle)
    if not isinstance(t1, dict):
        raise MigrationError(f"{t1_path}: not a mapping, so not a project config")

    files = {}
    for name, stanza in (t1.get("workflows") or {}).items():
        declared = (stanza or {}).get("config_path")
        if not declared:
            continue
        candidate = t1_path.parent / declared
        if not candidate.is_file():
            raise MigrationError(
                f"{t1_path}: `workflows.{name}.config_path` names `{declared}`, "
                f"which is not beside it. Expected {candidate}."
            )
        files[name] = candidate
    return t1, files


def classify(t1) -> str:
    """``v1`` | ``v2`` | ``partial`` — idempotence, D-11.2b item 5.

    A PARTIAL set is refused rather than finished, because it is a state a human
    should look at: something stopped part-way, and this tool cannot know
    whether the half that moved was the half that was supposed to.
    """
    declared = t1.get("schema_version")
    if declared == SCHEMA_VERSION:
        return "v2"
    if declared is None:
        return "v1"
    return "partial"


def migrate_project(t1_path: Path, *, write: bool = False):
    """Migrate one complete set. Returns the report; raises on any refusal.

    The five steps are D-11.2b's, in its order, and the ordering is the whole
    point: `N8`'s refusal can fire on the THIRD file of a set, and a mixed v1/v2
    tree is one the loader then rejects wholesale. So nothing is written until
    every file has been read, every move resolved and every hook evaluated.
    """
    handler = _yaml()
    t1, workflow_files = discover_set(t1_path)

    state = classify(t1)
    if state == "v2":
        return [f"{t1_path}: already `schema_version: {SCHEMA_VERSION}`; nothing to do"]
    if state == "partial":
        raise MigrationError(
            f"{t1_path}: declares `schema_version: {t1.get('schema_version')}`, "
            f"which is neither v1 (no key) nor v2 ({SCHEMA_VERSION}). This set "
            "is in a state no migration produced; look at it rather than "
            "letting this tool guess which half is current."
        )

    t2 = {}
    for name, path in workflow_files.items():
        with path.open(encoding="utf-8") as handle:
            t2[name] = handler.load(handle) or {}

    # 1. PREFLIGHT — in memory, over the complete set. Raises before any write.
    outvars = ((t1.get("shared") or {}).get("wflow_outvars")) or (
        (t1.get("model") or {}).get("outvars")
    )
    t1, t2, report = migrate_set(t1, t2, load_mapping(), outvars=outvars)

    if not write:
        return report

    # 2. STAGE beside the project, so the rename in step 4 stays on one volume.
    staged = {}
    stage_dir = t1_path.parent / ".migrate_staging"
    stage_dir.mkdir(exist_ok=True)
    try:
        staged[t1_path] = stage_dir / t1_path.name
        with staged[t1_path].open("w", encoding="utf-8") as handle:
            handler.dump(t1, handle)
        for name, path in workflow_files.items():
            staged[path] = stage_dir / path.name
            with staged[path].open("w", encoding="utf-8") as handle:
                handler.dump(t2[name], handle)

        # 3. VALIDATE the staged set through the loader itself, not a second
        #    reader — the only check that means anything is the one a run does.
        _validate_staged(staged[t1_path])

        # 4. COMMIT. Originals move to `*.v1.bak` rather than being deleted:
        #    a migration a user wants to undo is a migration they can undo.
        for original, temp in staged.items():
            backup = original.with_suffix(original.suffix + ".v1.bak")
            original.replace(backup)
            temp.replace(original)
            report.append(f"wrote {original.name}, kept {backup.name}")
    finally:
        for leftover in stage_dir.glob("*"):
            leftover.unlink()
        stage_dir.rmdir()

    return report


def _validate_staged(staged_t1: Path) -> None:
    """The staged set must compose, or nothing is committed.

    Uses the loader a real run uses. A rewriter that validated with its own
    reader would be checking its own opinion of the shape.
    """
    from blueearth_cst.shared.config_composition import load_composed_config

    try:
        load_composed_config(staged_t1)
    except Exception as exc:  # the loader raises several types
        raise MigrationError(
            "the migrated set does not compose, so nothing was written:"
            f"{chr(10)}  {exc}"
        ) from None


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        description="Rewrite a v1 project config set to v2, preserving comments.",
    )
    parser.add_argument("config", help="the project's T1 config file")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="report what would change and write nothing (the only mode today)",
    )
    args = parser.parse_args(argv)
    try:
        report = migrate_project(Path(args.config), write=not args.dry_run)
    except MigrationError as exc:
        print(f"REFUSED: {exc}", file=sys.stderr)
        return 1

    for line in report:
        print(line)
    if args.dry_run:
        print("(--dry-run: nothing was written)", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
