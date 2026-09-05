"""The plan block: the run's rules, one per line, keyed on rule id.

What this pins, and why each case is here rather than left to a real run:
`onstart:` does NOT fire on `--dry-run` (probed 2026-09-05), so
`tests/test_cli.py` -- the cheap check that dry-runs all four entry points --
cannot see this block at all. Everything below is therefore the only automated
cover it has short of executing a workflow.
"""

from __future__ import annotations

import pytest

from blueearth_cst.shared import snake_utils as su

WF1_STATS = """Job stats:
job                             count
----------------------------  -------
all                                 1
snapshot_config                     1
write_outlet_index                  1
total                               3
"""


@pytest.fixture
def rules(monkeypatch):
    """Install a rule-number registry, as `rule_banner` would at parse time."""

    def install(mapping):
        monkeypatch.setattr(su, "_RULE_NUMBERS", dict(mapping))

    return install


# --- the table parser -------------------------------------------------------


def test_the_stats_table_parses_to_counts():
    assert su._run_info_counts(WF1_STATS) == {
        "all": 1,
        "snapshot_config": 1,
        "write_outlet_index": 1,
    }


def test_a_table_that_is_not_one_yields_nothing():
    """Fail open: an unparsable message must fall back, never guess."""
    assert su._run_info_counts("Nothing resembling a table here.") == {}


# --- grouping ---------------------------------------------------------------


def test_the_target_rule_is_excluded(rules):
    """`all` does no work, but Snakemake counts it as a job.

    The block's rule count and Snakemake's job count differ by exactly this
    rule, on purpose -- so the exclusion has to be deliberate and pinned.
    """
    rules({"all": "1.00", "snapshot_config": "1.01"})
    assert [row[0] for row in su._plan_rows({"all": 1})] == ["1.01"]


def test_rules_sharing_a_number_collapse_to_one_row(rules):
    """WF0 builds one rule per climate source in a Python loop.

    Three rule objects, one number, one row -- with the jobs summed, not the
    first one taken.
    """
    rules(
        {
            "extract_historical_climate_era5": "0.04",
            "extract_historical_climate_chirps": "0.04",
            "extract_historical_climate_eobs": "0.04",
        }
    )
    (row,) = su._plan_rows(
        {
            "extract_historical_climate_era5": 1,
            "extract_historical_climate_chirps": 1,
            "extract_historical_climate_eobs": 1,
        }
    )
    assert row == ("0.04", "extract_historical_climate", 3)


def test_a_shared_number_with_no_common_prefix_keeps_a_real_name(rules):
    """Better a real rule name from the Snakefile than an empty truncation."""
    rules({"alpha": "9.01", "beta": "9.01"})
    (row,) = su._plan_rows({})
    assert row[1] == "alpha"


def test_numbers_sort_lexicographically(rules):
    """`1.14` < `1.14b` < `1.15` as plain strings -- no version parser."""
    rules(
        {
            "run_wflow": "1.14",
            "export_wflow_tables": "1.14b",
            "plot_wflow_evaluation": "1.15",
            "write_run_metadata": "1.15b",
            "snapshot_config": "1.01",
        }
    )
    assert [row[0] for row in su._plan_rows({})] == [
        "1.01",
        "1.14",
        "1.14b",
        "1.15",
        "1.15b",
    ]


# --- the head line ----------------------------------------------------------


def test_head_says_all_to_run_when_nothing_is_up_to_date(rules):
    rules({"a": "1.01", "b": "1.02"})
    head, _ = su._plan_lines({"a": 1, "b": 1})
    assert head == "  plan -- 2 rules, all to run"


def test_head_names_both_halves_on_a_partial_run(rules):
    rules({"a": "1.01", "b": "1.02", "c": "1.03"})
    head, _ = su._plan_lines({"a": 1})
    assert head == "  plan -- 1 of 3 rules to run, 2 up to date"


def test_head_carries_the_job_count_only_when_something_fans_out(rules):
    """The line this replaced always carried it; here it is only news."""
    rules({"a": "1.01", "b": "1.02"})
    plain, _ = su._plan_lines({"a": 1, "b": 1})
    assert "jobs" not in plain

    fanned, _ = su._plan_lines({"a": 1, "b": 8})
    assert fanned.endswith(", 9 jobs")


def test_a_single_rule_is_not_pluralized(rules):
    rules({"a": "1.01"})
    head, _ = su._plan_lines({"a": 1})
    assert head == "  plan -- 1 rule, all to run"


# --- the rows ---------------------------------------------------------------


def test_the_gutter_marks_what_will_run(rules):
    rules({"a": "1.01", "b": "1.02"})
    _, rows = su._plan_lines({"b": 1})
    texts = [text for text, _ in rows]
    assert texts[0].startswith("     1.01")
    assert texts[1].startswith("  >  1.02")


def test_no_gutter_when_every_rule_runs(rules):
    """A mark on every line carries no information; the head line says it."""
    rules({"a": "1.01", "b": "1.02"})
    _, rows = su._plan_lines({"a": 1, "b": 1})
    assert not any(">" in text for text, _ in rows)


def test_fanned_rules_carry_their_count(rules):
    rules({"perturb": "3.12", "seed": "3.11"})
    _, rows = su._plan_lines({"perturb": 8, "seed": 1})
    assert [text.split()[-1] for text, _ in rows] == ["seed", "x8"]


def test_rows_report_whether_they_run(rules):
    """The caller colours whole lines from this flag; `_paint` never fields."""
    rules({"a": "1.01", "b": "1.02"})
    _, rows = su._plan_lines({"b": 1})
    assert [running for _, running in rows] == [False, True]


def test_no_row_carries_trailing_whitespace(rules):
    """A workflow without fan-out has no name column to pad."""
    rules({"a": "1.01", "bbbbbbbb": "1.02"})
    _, rows = su._plan_lines({"a": 1})
    assert all(text == text.rstrip() for text, _ in rows)


def test_the_block_is_ascii(rules):
    """A Windows console is cp1252 and raises on typographic characters."""
    rules({"perturb": "3.12", "seed": "3.11"})
    head, rows = su._plan_lines({"perturb": 8})
    ("\n".join([head] + [text for text, _ in rows])).encode("cp1252")


def test_an_empty_registry_falls_back(rules):
    """A workflow whose rules never called `rule_banner` gets Snakemake's line."""
    rules({})
    assert su._plan_lines({"whatever": 1}) is None


def test_every_rule_up_to_date_still_renders(rules):
    """Reachable when only the excluded `all` job remains."""
    rules({"all": "1.00", "a": "1.01"})
    head, rows = su._plan_lines({"all": 1})
    assert head == "  plan -- 1 rule, all up to date"
    assert not any(">" in text for text, _ in rows)


def test_a_rule_missing_from_the_ledger_is_declared(rules):
    """No silent caps.

    Every rule in all four Snakefiles calls `rule_banner` today, so this
    should never fire -- but a block that listed 18 of 19 rules and said
    nothing would be worse than one that admits the gap.
    """
    rules({"a": "1.01"})
    head, rows = su._plan_lines({"a": 1, "undeclared_rule": 1})
    assert head.endswith(", 1 unlisted")
    assert len(rows) == 1


def test_nothing_is_declared_when_the_ledger_is_complete(rules):
    rules({"all": "1.00", "a": "1.01"})
    head, _ = su._plan_lines({"all": 1, "a": 1})
    assert "unlisted" not in head
