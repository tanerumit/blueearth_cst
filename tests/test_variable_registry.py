"""The one record per variable, and the two facts that look like one.

R14 `C-57`, Gate 1(b). The registry unified two tables that described the same
three variables in different vocabularies. These tests pin the parts of that
unification that a later reader would otherwise be tempted to "clean up".
"""

from __future__ import annotations

import pytest

from blueearth_cst.climate_analysis import climate_figures
from blueearth_cst.projections.variable_spec import parse
from blueearth_cst.shared.variable_registry import (
    CLIMATE_VARS,
    VARIABLES,
    Presentation,
    ProjectionSpec,
)

#: The long form, exactly as every shipped `analyze_projections` config spells
#: it. Written out rather than read from the registry, so the equality test
#: below compares the registry against an INDEPENDENT statement of the same
#: values instead of against itself.
LONG_FORM = {
    "precip": {
        "source": "precip",
        "canonical": "rate",
        "units": "mm/day",
        "change": "relative",
    },
    "temp": {
        "source": "temp",
        "canonical": "state",
        "units": "degC",
        "change": "absolute",
    },
}


def test_the_short_form_resolves_to_exactly_the_long_form():
    """Falsifier 1: assert the parsed STRUCTURE, not that parsing succeeded.

    A short form that silently resolved to some default would pass any smoke
    test — it produces a valid spec map, just not the right one. Comparing
    against the long form written out above is what makes this an assertion
    about values.
    """
    assert parse({"precip": None, "temp": None}) == parse(LONG_FORM)


def test_the_long_form_still_works_and_still_wins():
    """The registry is a default, not a wall.

    No `RETIRED_KEYS` row covers `variables:`, the v2 probe fixture uses the
    long form, and a variable the registry has never heard of has nowhere else
    to be declared. A registry that forced its own values would make the last
    case impossible.
    """
    override = {
        "precip": {
            "source": "precip",
            "canonical": "rate",
            "units": "m/day",  # deliberately NOT the registry's mm/day
            "change": "relative",
        }
    }
    assert parse(override)["precip"].units == "m/day"


def test_a_variable_outside_the_registry_can_still_be_declared():
    """The escape hatch that makes a Python registry acceptable at all.

    Gate 1(a) chose Python over YAML on the grounds that a project never needs
    to edit the registry, and that argument holds only while this passes.
    """
    spec = parse(
        {
            "runoff": {
                "source": "runoff",
                "canonical": "rate",
                "units": "mm/day",
                "change": "relative",
            }
        }
    )
    assert spec["runoff"].change == "relative"


def test_an_unknown_short_form_variable_refuses_with_both_remedies():
    with pytest.raises(ValueError) as excinfo:
        parse({"runoff": None})
    message = str(excinfo.value)
    assert "not in it" in message
    assert "variable_registry.py" in message
    assert "declare it in full" in message


def test_a_registered_variable_with_no_projection_spec_refuses_differently():
    """`pet` is IN the registry, so "add it to the registry" would be false.

    Two faults need two remedies. Telling a user to add a variable that is
    already there sends them to a file where they will find it and conclude the
    error is wrong about something else.
    """
    with pytest.raises(ValueError) as excinfo:
        parse({"pet": None})
    message = str(excinfo.value)
    assert "IS in the variable registry" in message
    assert "does not difference" in message
    assert "variable_registry.py" not in message


def test_the_figure_unit_and_the_canonical_units_are_not_the_same_fact():
    """The trap Gate 1 found: two spellings of one word, two different facts.

    `precip` is drawn as a yearly TOTAL in mm and stored as a monthly mean RATE
    in mm/day. Collapsing them — the obvious cleanup on seeing `unit` beside
    `units` — mislabels every figure axis or every change factor depending on
    which direction the collapse went, and nothing downstream raises either way.
    """
    entry = VARIABLES["precip"]
    assert entry.presentation.unit == "mm"
    assert entry.projections.units == "mm/day"
    assert entry.presentation.unit != entry.projections.units


def test_climate_vars_is_unchanged_in_value_and_in_order():
    """22 call sites keep working, and two of them depend on the ORDER.

    `plot_map_forcing` selects the canonical climate set with
    `list(CLIMATE_VARS)` and `compare_sources` documents its panel order as
    "ordered as CLIMATE_VARS is", so a dict that merely holds the same entries
    is not sufficient.
    """
    assert list(CLIMATE_VARS) == ["precip", "temp", "pet"]
    assert CLIMATE_VARS["precip"] == {
        "label": "precipitation",
        "unit": "mm",
        "how": "sum",
        "style": "precip",
    }
    assert CLIMATE_VARS["temp"]["how"] == "mean"
    assert CLIMATE_VARS["pet"]["style"] == "pet"


def test_the_figures_module_still_exports_the_name_it_always_did():
    """The re-export is what keeps the 22 sites out of this phase's diff."""
    assert climate_figures.CLIMATE_VARS is CLIMATE_VARS


@pytest.mark.parametrize("name", sorted(VARIABLES))
def test_every_entry_is_well_formed(name):
    """Both groups validated at the registry, not only where they are read.

    A malformed entry would otherwise surface as a config error blaming the
    project's `variables:` block for a value the project never wrote.
    """
    entry = VARIABLES[name]
    assert isinstance(entry.presentation, Presentation)
    assert entry.presentation.how in {"sum", "mean"}
    assert entry.presentation.label and entry.presentation.unit

    if entry.projections is None:
        return
    assert isinstance(entry.projections, ProjectionSpec)
    assert entry.projections.canonical in {"rate", "state"}
    assert entry.projections.change in {"relative", "absolute"}
    assert entry.projections.source and entry.projections.units
