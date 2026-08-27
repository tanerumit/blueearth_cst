"""The v1→v2 mapping is complete, traceable, and agrees with the loader.

`config/migrations/v1_to_v2.yml` is the NORMATIVE artifact the rewriter
executes (design D-11.2a). The register in `config-shape-scoping.md` is the
argument behind each row; 85 rows of markdown cannot be executed and cannot be
checked for completeness, which is what these tests do instead.

**Why three directions and not the one D-11.2a asks for.** The design requires
register ↔ mapping completeness. That alone would not have caught what R14 has
actually produced six times: two records of the same fact drifting apart. So
the mapping is also checked against `RETIRED_KEYS`, which is the loader's own
record of which v1 spellings are dead and where they went. A key that is
refused at parse time but absent from the mapping is a key the rewriter will
not migrate and the loader will then reject — a config the toolbox has made
unmigratable, which is the worst outcome available here.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest
import yaml

from blueearth_cst.shared.config_composition import RETIRED_KEYS, T1_TOP_LEVEL

REPO_ROOT = Path(__file__).resolve().parent.parent
MAPPING_PATH = REPO_ROOT / "config" / "migrations" / "v1_to_v2.yml"
REGISTER_PATH = REPO_ROOT / "dev" / "milestones" / "r14" / "config-shape-scoping.md"

#: Every transform the rewriter must implement. A mapping naming one outside
#: this set is a row nothing can execute.
KNOWN_TRANSFORMS = frozenset(
    {
        "identity",
        "iso_to_year",
        "bool_to_enum",
        "step_num_to_n_levels",
        "pair_to_window",
        "list_to_named_windows",
        "scalar_to_var_mapping",
        "list_to_preference_group",
    }
)

KNOWN_HOOKS = frozenset({None, "warn_st0", "refuse_water_year"})
KNOWN_OPS = frozenset({"rename", "regroup", "delete", "retype", "new"})
KNOWN_STATUS = frozenset({"live", "withdrawn", "superseded"})
KNOWN_APPLIES = frozenset({"config", "code", "doc", "decision", "file", "none"})


@pytest.fixture(scope="module")
def mapping():
    return yaml.safe_load(MAPPING_PATH.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def register_ids():
    """Every `C-nn` the register declares, from its table's first column."""
    pat = re.compile(r"^\|\s*`?(C-\d+)`?\s*\|")
    ids = set()
    for line in REGISTER_PATH.read_text(encoding="utf-8").splitlines():
        m = pat.match(line)
        if m:
            ids.add(m.group(1))
    return ids


def _rows(mapping):
    return {row["id"]: row for row in mapping["rows"]}


def test_every_register_row_has_a_mapping_entry(mapping, register_ids):
    """D-11.2a, direction 1. A row with no entry is work nothing will do."""
    missing = sorted(register_ids - set(_rows(mapping)))
    assert not missing, (
        f"{len(missing)} register row(s) have no mapping entry: {missing}. "
        "Every C-nn needs one, even if it moves no config key — use "
        "`moves: []` with `applies:` saying what it does change instead."
    )


def test_every_mapping_entry_names_a_register_row(mapping, register_ids):
    """D-11.2a, direction 1, the other way. An invented row has no argument."""
    stray = sorted(set(_rows(mapping)) - register_ids)
    assert not stray, (
        f"mapping entries name no register row: {stray}. The register is the "
        "argument; a mapping row without one cannot be reviewed."
    )


def test_the_mapping_covers_every_retired_key(mapping):
    """Direction 2: the loader refuses these, so the rewriter must move them.

    A key in `RETIRED_KEYS` but not in the mapping is the bad case: the loader
    rejects the v1 spelling and the rewriter does not produce the v2 one, so
    the config cannot be migrated by the tool that exists to migrate it.
    """
    mapped = {
        move["old_path"]
        for row in mapping["rows"]
        for move in (row.get("moves") or [])
        if move.get("old_path")
    }
    unmapped = sorted(set(RETIRED_KEYS) - mapped)
    assert not unmapped, (
        f"{len(unmapped)} key(s) are refused by the loader but absent from the "
        f"mapping, so no migration path exists for them: {unmapped}"
    )


def test_every_mapped_source_is_refused_by_the_loader(mapping):
    """Direction 2, the other way: a v1 path the mapping moves must be dead.

    Otherwise a user who never migrates gets no error AND no migration — the
    key keeps working under its old spelling while the rewriter claims to have
    moved it. That is how five keys were found silently accepted on 2026-08-27
    (`basin.river_uparea_km2`, `basin.spatial_sources`, `basin.hydrography`,
    `basin.basin_index`, `basin.gauge_snap_tolerance_m`), each of which had
    stopped being read after its regroup.

    **Three mechanisms count as protection, and only these three:**

    1. ``RETIRED_KEYS``, or any ANCESTOR of the path — the loader refuses
       ``T1.shared`` wholesale rather than naming each of its children.
    2. The CLOSED T1 top level (``T1_TOP_LEVEL``) — a section that is not a
       declared top-level key is refused by name whether or not it is retired,
       which is what covers ``method:`` and T1 ``compute:``.
    3. The key KEEPS its name and only its VALUE retypes — ``members:`` (list to
       mapping, `C-63`) and ``simulation_window:`` (ISO to years, `C-71`). No
       name-based refusal is possible for these, because the v2 name is the v1
       name; the loader catches them by SHAPE instead.

    Mechanism 3 is an allowlist, so it is enumerated rather than inferred: a
    path added to it silently would be the exact hole this test exists to find.
    """
    retype_in_place = {
        "T2.analyze_projections.members",
        "T2.build_model.simulation_window",
    }

    for row in mapping["rows"]:
        for move in row.get("moves") or []:
            old = move.get("old_path")
            if not old or not old.startswith(("T1.", "T2.")):
                continue
            if old in retype_in_place:
                assert (
                    move["op"] == "retype" or move["value_transform"] != "identity"
                ), (
                    f"{row['id']} lists `{old}` as a retype-in-place, but the move "
                    "neither retypes nor transforms — so nothing would catch a "
                    "config that kept the v1 shape."
                )
                continue

            parts = old.split(".")
            by_retired = any(
                ".".join(parts[:n]) in RETIRED_KEYS for n in range(len(parts), 1, -1)
            )
            # `T1.<section>` — the closed top level refuses an undeclared one.
            by_closed_t1 = len(parts) == 2 and parts[1] not in T1_TOP_LEVEL

            assert by_retired or by_closed_t1, (
                f"{row['id']} maps `{old}`, which is not refused by "
                "`RETIRED_KEYS` (nor any ancestor), is not caught by the closed "
                "T1 top level, and is not a declared retype-in-place. A user who "
                "leaves this key in place gets no error and no migration."
            )


def test_every_row_is_well_formed(mapping):
    """Direction 3: vocabulary. An unknown op or transform is unexecutable."""
    for row in mapping["rows"]:
        assert row["status"] in KNOWN_STATUS, row
        assert row["applies"] in KNOWN_APPLIES, row
        for move in row.get("moves") or []:
            assert move["op"] in KNOWN_OPS, (row["id"], move)
            assert move["value_transform"] in KNOWN_TRANSFORMS, (row["id"], move)
            assert move["exception_hook"] in KNOWN_HOOKS, (row["id"], move)
            assert move["on_collision"] in {
                "refuse",
                "overwrite",
                "keep_existing",
            }, (row["id"], move)


def test_a_withdrawn_row_moves_nothing(mapping):
    """A withdrawn row that still carried a move would migrate a dead decision."""
    for row in mapping["rows"]:
        if row["status"] in {"withdrawn", "superseded"}:
            assert not (row.get("moves") or []), (
                f"{row['id']} is {row['status']} but still declares moves"
            )
            assert row["applies"] == "none", row["id"]


def test_a_delete_has_no_destination(mapping):
    """`op: delete` with a `new_path` is a contradiction the rewriter would obey."""
    for row in mapping["rows"]:
        for move in row.get("moves") or []:
            if move["op"] == "delete":
                assert move["new_path"] is None, (row["id"], move)
            if move["op"] == "new":
                assert move["old_path"] is None, (row["id"], move)


def test_the_trajectory_enum_agrees_with_the_code(mapping):
    """`C-32`: the mapping's enum must be what the loader will accept.

    **This is expected to FAIL until P1c Gate 1 rules.** The register row is
    ruled and says `transient | constant`; shipped code says `transient | step`.
    Emitting the register's value would produce configs the loader refuses, and
    emitting the code's value would contradict a ruled row — so the mapping
    states the ruled one and this names the gap rather than letting the
    rewriter be built on an unresolved spelling.

    Declared in `tests/data/r14_expected_red.txt` with that reason.
    """
    from blueearth_cst.experiment.prepare_weagen_config import TRAJECTORY_KINDS

    row = _rows(mapping)["C-32"]
    declared = set(row["enum"])
    assert declared == set(TRAJECTORY_KINDS), (
        f"the mapping emits {sorted(declared)} for `trajectory` but the loader "
        f"accepts {sorted(TRAJECTORY_KINDS)}. A rewriter run against this "
        "mapping would produce configs the toolbox then refuses. See "
        "`open_questions` in the mapping and P1c Gate 1."
    )
