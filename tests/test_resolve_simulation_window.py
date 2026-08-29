"""`workflows.build_model.simulation_window` — the model RUN period.

Split from `climate.window` on 2026-08-10. The record a project
extracts for analysis and the period it simulates are different questions.

They are not independent, though — the simulation window must sit INSIDE the
record, because rule 1.10 builds its forcing from the extracted store. The key
shipped unconstrained, correctly at the time: the forcing then came from the
data catalog and the extraction was not in its path at all.

The load-bearing property here is the passthrough. Every config written before
this key existed carries only `historical_window`, so "absent" has to mean
exactly that window — not a default that happens to look like it.
"""

import pytest

from blueearth_cst.shared.snake_utils import resolve_simulation_window


def _window(start, end):
    """R14 `C-71`: inclusive YEARS on this side too, so the two windows a user
    compares are written in one unit (`C-70` did the same for the record)."""
    return {"start": start, "end": end}


def _shared(start=2000, end=2020):
    """The `climate:` section, which is where the record lives since R14."""
    return {"window": _window(start, end)}


# --- the default path: what every pre-existing config takes --------------------


def test_absent_key_passes_the_historical_window_through():
    shared = _shared()
    assert resolve_simulation_window(shared, {}) == shared["window"]


def test_passthrough_is_the_same_object_not_a_reconstruction():
    """A rebuilt-but-equal mapping would drift the moment either side gains a
    field. Identity makes 'unchanged behaviour' structural rather than asserted."""
    shared = _shared()
    assert resolve_simulation_window(shared, {}) is shared["window"]


def test_an_explicit_null_is_still_passthrough():
    """A commented-out key that gets uncommented empty is a plausible edit, and
    it should behave as absent rather than crash."""
    shared = _shared()
    got = resolve_simulation_window(shared, {"simulation_window": None})
    assert got == shared["window"]


# --- the override path ---------------------------------------------------------


def test_an_explicit_window_wins_over_the_historical_one():
    sim = _window(2010, 2015)
    got = resolve_simulation_window(_shared(), {"simulation_window": sim})
    assert got == sim


def test_the_simulation_window_must_sit_inside_the_record():
    """Constrained since rule 1.10 began building forcing FROM the store.

    This asserted the opposite when the key shipped, and that was right then:
    the forcing came from the data catalog, so the two windows were independent.
    Sourcing the forcing from the extraction couples them — a simulation period
    outside the record now has no data behind it.
    """
    sim = _window(2021, 2023)  # entirely after the record
    with pytest.raises(ValueError, match="not inside climate.window"):
        resolve_simulation_window(_shared(2000, 2020), {"simulation_window": sim})


def test_the_refusal_names_both_files_when_it_is_told_them():
    """The two windows are authored in DIFFERENT files since R13.

    The simulation window lives in the build_model settings file and the record
    in the project file, so a user with both open should not have to work out
    which one the message means. Additive: the source arguments default to None
    and every case above, which passes neither, keeps its message verbatim.
    """
    sim = _window(2021, 2023)
    with pytest.raises(ValueError) as excinfo:
        resolve_simulation_window(
            _shared(2000, 2020),
            {"simulation_window": sim},
            shared_source="project_config_gabon.yml",
            model_source="project_config_gabon_build_model.yml",
        )
    message = str(excinfo.value)
    assert "in project_config_gabon_build_model.yml" in message
    assert "in project_config_gabon.yml" in message


def test_the_message_is_unchanged_when_no_source_is_given():
    """What makes the signature change additive rather than a break."""
    sim = _window(2021, 2023)
    record = _shared(2000, 2020)
    with pytest.raises(ValueError) as excinfo:
        resolve_simulation_window(record, {"simulation_window": sim})
    assert " (in " not in str(excinfo.value)


def test_a_window_overhanging_either_end_is_rejected():
    record = _shared(2000, 2020)
    for sim in (
        _window(1999, 2010),
        _window(2010, 2021),
    ):
        with pytest.raises(ValueError, match="not inside"):
            resolve_simulation_window(record, {"simulation_window": sim})


def test_a_window_equal_to_the_record_is_accepted():
    """Inside is inclusive — the default case is exactly this window."""
    record = _shared(2000, 2020)
    sim = _window(2000, 2020)
    assert resolve_simulation_window(record, {"simulation_window": sim}) == sim


def test_a_short_simulation_window_is_allowed():
    """MIN_HISTORICAL_YEARS is weathergenr's floor on the RECORD. Applying it
    here would forbid the short run the split exists to make possible."""
    sim = _window(2000, 2000)
    got = resolve_simulation_window(_shared(), {"simulation_window": sim})
    assert got == sim


# --- malformed input fails loudly, naming the key ------------------------------


@pytest.mark.parametrize("bad", [[], "2000-01-01", 2000])
def test_a_non_mapping_is_rejected(bad):
    with pytest.raises(ValueError, match="must be a mapping"):
        resolve_simulation_window(_shared(), {"simulation_window": bad})


@pytest.mark.parametrize("missing", ["start", "end"])
def test_a_missing_endpoint_is_rejected(missing):
    sim = _window(2000, 2010)
    del sim[missing]
    with pytest.raises(ValueError, match=f"missing '{missing}'"):
        resolve_simulation_window(_shared(), {"simulation_window": sim})


def test_a_non_year_endpoint_names_the_offending_key():
    sim = {"start": "01/01/2000", "end": 2010}
    with pytest.raises(ValueError) as excinfo:
        resolve_simulation_window(_shared(), {"simulation_window": sim})
    message = str(excinfo.value)
    assert "simulation_window" in message and "climate.window.start" in message
    assert "INCLUSIVE YEARS" in message, "say what the spelling is now"


def test_a_reversed_window_says_so_rather_than_failing_later():
    """Unlike the record, this has no length floor to trip, so a swapped pair
    would otherwise reach wflow as an empty run period."""
    sim = _window(2015, 2010)
    with pytest.raises(ValueError, match="check the order"):
        resolve_simulation_window(_shared(), {"simulation_window": sim})


def test_an_inverted_pair_is_rejected_too():
    """R14 note: an EQUAL pair used to be rejected and now is not, deliberately.

    Under ISO endpoints ``2010-01-01 .. 2010-01-01`` was a zero-length run
    period and could only be a mistake. Under inclusive YEARS (`C-71`)
    ``{start: 2010, end: 2010}`` is a legitimate one-year simulation --
    2010-01-01 to 2010-12-31 -- so the case that must still be refused is an
    inverted pair, which this asserts.
    """
    sim = _window(2015, 2010)
    with pytest.raises(ValueError, match="check the order"):
        resolve_simulation_window(_shared(), {"simulation_window": sim})


def test_an_equal_pair_is_a_legal_one_year_window():
    """The other half of the retype, so the change above is not silent."""
    got = resolve_simulation_window(
        _shared(), {"simulation_window": _window(2010, 2010)}
    )
    assert got == {"start": 2010, "end": 2010}
