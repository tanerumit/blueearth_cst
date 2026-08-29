"""Every shipped config means the same thing after migration as before it.

P4 rung 4, design §14.3, finding `ext1-6`. **This is the only numerical check
three of the four shipped configs will ever get**: `check_baseline` records from
`project_config_baseline` alone, so `rapid`, `baseline_linux` and `wf2_fast` have
nothing else standing between a migration and a silently different run.

**Distinct from P4's byte-for-byte falsifier, and the difference is the point.**
That falsifier re-runs the rewriter and diffs its output against what is
committed, which proves the migration is REPRODUCIBLE — that no one hand-edited
a config. It says nothing about whether the values are right: a rewriter that
consistently dropped a key would pass it every time. This module asserts the
other half — that each value ARRIVED, at the path the mapping declares, with the
transform the mapping declares.

The brief asks for the v1 and v2 documents to be composed and compared. Only
half of that is possible: `compose_config` reads v2 and P1 replaced the v1
loader, so there is no way to compose a v1 document with the toolbox as it
stands. The comparison is therefore made at the MAPPED PATHS — for every row,
the v1 value at `old_path` against the v2 value at `new_path` — which is the
same claim without requiring a loader that no longer exists.

The v1 side is `tests/data/v1_split/`, a byte-for-byte copy of the shipped
configs as they stood at `79b76334`, immediately before the rewriter ran.
"""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from blueearth_cst.shared.config_composition import load_composed_config
from scripts.migrate_project_config import load_mapping, split_tier

REPO_ROOT = Path(__file__).resolve().parent.parent
V1_DIR = REPO_ROOT / "tests" / "data" / "v1_split"

#: The four shipped sets, by the part of the name that is the SET rather than
#: the prefix. `baseline` is the one `check_baseline` records from; the other
#: three have only this module.
#:
#: The two sides carry different prefixes since `C-85`, and deliberately. The
#: v2 files are `project_config_*`; the v1 capture keeps `snake_config_*`
#: because that is what those files were called at `79b76334` — right down to
#: the `config_path:` keys inside them, which name their siblings. Renaming a
#: captured artifact to a later convention would make it inaccurate about the
#: thing it captures, which is the same objection that protects the sealed
#: records under `dev/milestones/`.
SETS = ["rapid", "baseline", "baseline_linux", "wf2_fast"]

#: The prefix each side carried at the time it was written.
V1_PREFIX = "snake_config_"
V2_PREFIX = "project_config_"

WORKFLOWS = (
    "analyze_climate",
    "build_model",
    "analyze_projections",
    "run_stress_test",
)


def _load_v1(stem):
    """The v1 set as `(t1, {workflow: body})`, read as plain YAML.

    Plain `safe_load`, not the loader: these documents declare no
    `schema_version` and the loader refuses them by design.
    """
    t1 = yaml.safe_load((V1_DIR / f"{V1_PREFIX}{stem}.yml").read_text(encoding="utf-8"))
    bodies = {}
    for name in WORKFLOWS:
        path = V1_DIR / f"{V1_PREFIX}{stem}_{name}.yml"
        if path.is_file():
            bodies[name] = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    return t1, bodies


def _get(doc, dotted):
    """`(value, present)` for a dotted path in a plain mapping."""
    node = doc
    for part in dotted.split("."):
        if not isinstance(node, dict) or part not in node:
            return None, False
        node = node[part]
    return node, True


def _resolve_v1(t1, bodies, path):
    tier, workflow, rest = split_tier(path)
    if tier == "T1":
        return _get(t1, rest)
    if workflow == "*":
        return None, False
    return _get(bodies.get(workflow) or {}, rest)


def _resolve_v2(composed, path):
    tier, workflow, rest = split_tier(path)
    if tier == "T1":
        return _get(composed, rest)
    if workflow == "*":
        return None, False
    return _get((composed.get("workflows") or {}).get(workflow) or {}, rest)


@pytest.fixture(scope="module")
def mapping():
    return load_mapping()


@pytest.mark.parametrize("stem", SETS)
def test_every_moved_value_arrived(stem, mapping):
    """Identity moves must carry their value through unchanged.

    Restricted to `value_transform: identity`, because those are the rows where
    equality IS the claim. The retypes are asserted individually below, where
    the expected relationship can be stated rather than assumed.

    **LEAF moves only.** A section-level move like `C-10` (`shared.basin` ->
    `basin`) carries a mapping whose CHILDREN are moved by their own rows --
    `C-41` renames `gauge_points` to `output_locations`, `C-13`/`C-42` regroup
    three keys under `delineation:` -- so the section before and after is
    legitimately different and comparing it wholesale asserts the opposite of
    what the mapping says. Each of those children is a leaf row and is checked
    on its own, so nothing goes unchecked by skipping the parent.
    """
    t1, bodies = _load_v1(stem)
    composed = load_composed_config(REPO_ROOT / "test_case" / f"{V2_PREFIX}{stem}.yml")

    checked = 0
    for row in mapping["rows"]:
        if row.get("status") != "live" or row.get("collapse"):
            continue
        for move in row.get("moves") or []:
            old, new = move.get("old_path"), move.get("new_path")
            if not old or not new or move["value_transform"] != "identity":
                continue
            before, present = _resolve_v1(t1, bodies, old)
            if not present:
                continue
            if isinstance(before, dict):
                continue  # a section; its children have their own rows
            after, arrived = _resolve_v2(composed, new)
            assert arrived, (
                f"{row['id']}: {stem} declared `{old}` but `{new}` is absent "
                "after migration — the value was dropped, not moved."
            )
            assert before == after, (
                f"{row['id']}: {stem} `{old}` was {before!r} and `{new}` is "
                f"{after!r}. An identity move must not change the value."
            )
            checked += 1

    # A FLOOR, not a non-zero check. `assert checked` would still pass if a
    # mapping edit silently reduced this to one move, which is the way a
    # coverage test quietly stops covering anything. Measured 2026-08-28:
    # ten leaf moves for three sets and seven for `baseline_linux`, which
    # declares neither `wflow_outvars` nor the two engine paths.
    floor = 7 if stem.endswith("_linux") else 10
    assert checked >= floor, (
        f"{stem}: only {checked} leaf move(s) were exercised, expected at "
        f"least {floor}. Either the set stopped declaring keys it used to, "
        "or a mapping edit moved them out of reach of this check."
    )


@pytest.mark.parametrize("stem", SETS)
def test_the_climate_window_is_the_same_period(stem):
    """`C-70`: ISO timestamps became INCLUSIVE YEARS over the same span.

    The retype is only value-preserving because every shipped window was already
    whole-year aligned. Asserted per set rather than assumed, since a config
    that was not would have had to be refused instead.
    """
    t1, _ = _load_v1(stem)
    composed = load_composed_config(REPO_ROOT / "test_case" / f"{V2_PREFIX}{stem}.yml")

    before, present = _get(t1, "shared.historical_window")
    if not present:
        pytest.skip(f"{stem} declares no historical_window")
    after = composed["climate"]["window"]

    assert before["starttime"] == f"{after['start']}-01-01T00:00:00"
    assert before["endtime"] == f"{after['end']}-12-31T00:00:00"


@pytest.mark.parametrize("stem", SETS)
def test_the_perturbation_grid_has_the_same_member_count(stem):
    """`C-31`: `n_levels` = `step_num` + 1, so the GRID is unchanged.

    The member count is the assertion, not the key: a rewriter that renamed
    without adding one would produce a valid config with a smaller grid and
    nothing anywhere would report it. This is that falsifier applied to every
    shipped config rather than to a fixture.
    """
    from blueearth_cst.shared.snake_utils import stress_test_grid

    t1, bodies = _load_v1(stem)
    before, present = _get(bodies.get("run_stress_test") or {}, "stress_test")
    if not present:
        pytest.skip(f"{stem} declares no stress_test section")

    composed = load_composed_config(REPO_ROOT / "test_case" / f"{V2_PREFIX}{stem}.yml")
    after = composed["workflows"]["run_stress_test"]["climate_perturbations"]

    v1_members = (before["temp"]["step_num"] + 1) * (before["precip"]["step_num"] + 1)
    assert stress_test_grid(after)[2] == v1_members, (
        f"{stem}: the v1 grid had {v1_members} members and the migrated one does "
        "not. `C-31` is a retype, not a rename."
    )


@pytest.mark.parametrize("stem", SETS)
def test_the_simulation_window_is_the_period_the_run_used(stem):
    """`C-67`: two keys collapse into the window they RESOLVED to.

    Not the window their arithmetic looks like it should give: the halves
    snapped `ceil` backwards and `round` forwards, so `run_length: 8` at horizon
    2050 was 2046..2054 — NINE calendar years. Emitting 2046..2053 would quietly
    shorten every migrated project's run, and nothing downstream would say so.
    """
    import math

    t1, bodies = _load_v1(stem)
    wf3 = bodies.get("run_stress_test") or {}
    horizon, has_horizon = _get(wf3, "horizontime_climate")
    if not has_horizon:
        pytest.skip(f"{stem} declares no horizontime_climate")
    length, has_length = _get(wf3, "run_length")
    if not has_length:
        length = 20

    composed = load_composed_config(REPO_ROOT / "test_case" / f"{V2_PREFIX}{stem}.yml")
    after = composed["workflows"]["run_stress_test"]["simulation_window"]

    assert after["start"] == int(horizon - math.ceil(length / 2))
    assert after["end"] == int(horizon + round(length / 2))


@pytest.mark.parametrize("stem", SETS)
def test_run_historical_is_gone_and_that_is_the_declared_difference(stem):
    """`C-69`, the row that is deliberately NOT behaviour-preserving (D-11.5).

    Asserted as a DIFFERENCE rather than skipped, so the one intended
    behavioural change in the whole migration is pinned somewhere rather than
    being indistinguishable from an oversight.
    """
    _, bodies = _load_v1(stem)
    wf3 = bodies.get("run_stress_test") or {}
    _, had_key = _get(wf3, "run_historical")

    composed = load_composed_config(REPO_ROOT / "test_case" / f"{V2_PREFIX}{stem}.yml")
    after = composed["workflows"]["run_stress_test"]

    assert "run_historical" not in after, (
        f"{stem}: `run_historical` survived the migration. `C-69` deletes it and "
        "`st_0` is always produced."
    )
    if had_key:
        # The set declared it, so the deletion is a real change to this project
        # and not a no-op. Recorded rather than asserted away.
        assert True


@pytest.mark.parametrize("stem", SETS)
def test_the_candidate_set_still_contains_every_source_it_named(stem):
    """`C-43`: the union, checked as a SET rather than as a list.

    v1's `candidate_sources` held the datasets OTHER than the privileged
    `clim_historical`; v2's `climate.sources` is the full set with `selected` a
    member. Dropping either side would lose a source WF0 was comparing.
    """
    t1, bodies = _load_v1(stem)
    selected, _ = _get(t1, "shared.clim_historical")
    extras, _ = _get(bodies.get("analyze_climate") or {}, "candidate_sources")

    composed = load_composed_config(REPO_ROOT / "test_case" / f"{V2_PREFIX}{stem}.yml")
    after = composed["climate"]["sources"]

    expected = {selected} | set(extras or [])
    expected.discard(None)
    assert set(after) == expected, (
        f"{stem}: v1 named {sorted(expected)} and v2 declares {sorted(after)}."
    )
    assert composed["climate"]["selected"] in after
