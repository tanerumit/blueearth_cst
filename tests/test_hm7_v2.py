"""HM-7 for metric-set/2 (`interchange_contracts.validate_hm7_v2`, t2609241852)."""

from __future__ import annotations

import pandas as pd
import pytest

from blueearth_cst.shared import interchange_contracts as ic

RUNS = ["01", "02"]
GROUPS = [
    {"run_group_id": "01", "grain": "run", "run_id": "01"},
    {"run_group_id": "02", "grain": "run", "run_id": "02"},
    {"run_group_id": "", "grain": "bundle", "run_id": "01"},
    {"run_group_id": "", "grain": "bundle", "run_id": "02"},
]
SERIES = [{"variable": "q", "location_id": loc} for loc in ("101", "102")]


def _contract():
    rows = [("q_mean", loc, g, "1.5") for loc in ("101", "102") for g in ("01", "02")]
    rows += [("q_rl", loc, "", "2.0") for loc in ("101", "102")]
    table = pd.DataFrame(rows, columns=list(ic.HM7_V2_COLUMNS))
    manifest = {
        "schema_version": "metric-set/2",
        "run_groups": GROUPS,
        "tables": [{"token": "q"}],
    }
    lookup = pd.DataFrame(GROUPS)[list(ic.HM7_V2_LOOKUP_COLUMNS)]
    return manifest, {"q": table}, lookup


def _check(manifest, tables, lookup):
    return ic.validate_hm7_v2(
        manifest, tables, lookup=lookup, series=SERIES, collection_run_ids=RUNS
    )


def test_a_complete_metric_set_passes():
    assert _check(*_contract()) == []


@pytest.mark.parametrize(
    ("break_it", "expected"),
    [
        (
            lambda m, t, lk: t.__setitem__("q", t["q"].iloc[1:]),
            "every location x run group",
        ),
        (
            lambda m, t, lk: t.__setitem__("q", pd.concat([t["q"], t["q"].iloc[:1]])),
            "duplicate keys",
        ),
        (
            lambda m, t, lk: t["q"].__setitem__(
                "location", t["q"]["location"].replace("102", "103")
            ),
            "locations differ",
        ),
        (
            lambda m, t, lk: t["q"].__setitem__(
                "value", t["q"]["value"].replace("1.5", "x")
            ),
            "non-numeric",
        ),
        (lambda m, t, lk: m.__setitem__("run_groups", GROUPS[:3]), "lookup differs"),
        (lambda m, t, lk: m.__setitem__("tables", [{"token": "gwr"}]), "tables differ"),
    ],
)
def test_each_break_is_named(break_it, expected):
    manifest, tables, lookup = _contract()
    break_it(manifest, tables, lookup)
    assert any(expected in diff for diff in _check(manifest, tables, lookup))


def test_a_run_outside_the_collection_is_refused():
    manifest, tables, lookup = _contract()
    assert any(
        "outside the collection" in diff
        for diff in ic.validate_hm7_v2(
            manifest, tables, lookup=lookup, series=SERIES, collection_run_ids=["01"]
        )
    )


def test_a_metric_set_1_marker_is_not_accepted():
    manifest, tables, lookup = _contract()
    manifest["schema_version"] = "metric-set/1"
    assert _check(manifest, tables, lookup) == ["HM-7: not a metric-set/2 marker"]
