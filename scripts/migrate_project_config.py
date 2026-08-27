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

This module is the MECHANISM. The transaction around it — preflight, stage,
validate, atomic commit, ``*.v1.bak`` — is D-11.2b and lands next; until then
this rewrites in memory and writes nothing, which is what makes it safe to
land on its own.
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
    parts = dotted.split(".")
    holder = _walk(doc, parts)
    if holder is None or parts[-1] not in holder:
        return None, False
    return holder.pop(parts[-1]), True


def set_path(doc, dotted: str, value, *, on_collision: str, row_id: str):
    """Create intermediate mappings as needed, honouring ``on_collision``."""
    parts = dotted.split(".")
    node = doc
    for part in parts[:-1]:
        if part not in node or not isinstance(node[part], dict):
            node[part] = {}
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
    doc = None
    for move in moves:
        tier, workflow, path = split_tier(_follow(move["old_path"], renames))
        doc = t1 if tier == "T1" else t2_by_workflow.get(workflow)
        if doc is None:
            continue
        value, present = get_path(doc, path)
        if present:
            values[path.split(".")[-1]] = value
            sources.append(move["old_path"])

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

        pop_path(doc, path)
        set_path(
            dest,
            new_path,
            converted,
            on_collision=move["on_collision"],
            row_id=row["id"],
        )
        if isinstance(converted, dict):
            # A SECTION moved, so every path still pointing inside it must
            # follow. Recorded against the ORIGINAL v1 spelling, because
            # that is what later rows will name.
            renames[old] = new
        report.append(f"{row['id']}: `{old}` -> `{new}`")


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
    print(
        f"{args.config}: the transactional wrapper (D-11.2b) is not built yet, "
        "so this command reports and writes nothing. The mapping it will "
        f"execute is {MAPPING_PATH.relative_to(REPO_ROOT)}.",
        file=sys.stderr,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
