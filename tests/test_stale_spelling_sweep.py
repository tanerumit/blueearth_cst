"""The stale-spelling sweep classifies, and is honest about the tree it sees.

`C-37`'s successor (`dev/scripts/sweep_stale_spellings.py`). These tests cover
the sweep's OWN behaviour — its classification, and its refusal to wave an
unknown hit through. They deliberately do NOT assert it finds zero.

**It is expected to be non-zero until P4.** The tree is mixed today: the code
reads v2 spellings and every shipped config is still v1, because P4 migrates
those with the rewriter P3 just built. A test demanding zero would be demanding
that P4 had already run, and the only way to make it pass would be to widen the
allowlist until it covered the configs — which is the sweep switched off.

What it turns into after P4 is a real gate. Until then it is a measurement.
"""

from __future__ import annotations

import pytest

from dev.scripts.sweep_stale_spellings import (
    ALLOWANCES,
    retired_spellings,
    surviving_leaves,
    sweep,
)


def test_the_vocabulary_comes_from_the_loader_not_a_hand_list():
    """The sweep and the refusals must not be able to disagree.

    A hand-maintained list of dead spellings is a second record of the same
    fact, and R14 has produced six of those drifting apart already.
    """
    spellings = retired_spellings()
    assert spellings
    assert "clim_project" in spellings
    assert "horizontime_climate" in spellings


def test_a_leaf_that_survives_into_v2_is_not_swept():
    """`seed` moves between files but keeps its name, so the word stays live.

    Sweeping it by name flags every correct use. `stress_test` is worse: it is a
    substring of `run_stress_test`, which names the workflow itself.
    """
    survivors = surviving_leaves()
    assert {"seed", "stress_test", "simulation_window"} <= survivors
    spellings = retired_spellings()
    assert not ({"seed", "stress_test"} & set(spellings))


def test_every_allowance_states_a_reason():
    """An allowlist entry without a reason is an exception nobody can review."""
    for allowance in ALLOWANCES:
        assert allowance.reason.strip(), allowance.name
        assert len(allowance.reason) > 40, allowance.name


def test_it_classifies_rather_than_greps():
    """Both outcomes are populated, which is the property the design asks for.

    A sweep with no allowances is a grep; one with nothing left over is an
    allowlist that has eaten its own purpose.
    """
    defects, allowed = sweep()
    assert allowed, "nothing was classified — the allowances are not matching"
    assert defects, (
        "no unclassified hits at all. Either P4 has run and this test should "
        "become a zero-assertion gate, or the allowlist has grown until it "
        "covers everything."
    )


#: Runtime files where a retired spelling is still LIVE, found by this sweep on
#: 2026-08-27 and not yet fixed. Each is a real defect, not an allowance:
#: `spatial/config.py` reads `basin.gauge_points` and `basin.automatic_subbasins`,
#: both of which the loader REFUSES in v2 — so a v2 project's gauge points and
#: delineation settings are read by nothing and silently fall back to defaults.
#:
#: Listed rather than allowed, so the set can only SHRINK. A new entry fails the
#: test below; removing one is the fix landing.
KNOWN_LIVE_V1_READERS = {
    # Dev tooling, in NO phase's permitted scope. Not a run path, so these break
    # at P4 when the shipped configs actually migrate rather than at runtime.
    # Boarded on `t2608251900`.
    "dev/scripts/prune_climate_store.py",
    "dev/scripts/prune_series_cache.py",
    "dev/scripts/semantic_tree_diff.py",
    "dev/scripts/snapshot_project_tree.py",
    "dev/scripts/stage_cmip6.py",
    # `analyze_projections.smk:315` reads `relative_change`, which `C-66`
    # retires. OWNED and deferred: P1c dissolves it once the variable
    # registry exists, and until then the reader falls back to the shipped
    # defaults rather than losing a configured value outright.
    "analyze_projections.smk",
}
#
# `blueearth_cst/spatial/config.py` and `analyze_climate.smk` were here when
# this sweep first ran on 2026-08-27, and are the reason it exists: both read a
# key the loader REFUSES, so a v2 project lost its gauge points, its delineation
# settings and its candidate source list, silently. Both fixed the same day, and
# removing them from this list is what "fixed" means.


def test_no_NEW_runtime_file_reads_a_retired_spelling():
    """A ratchet on the real defects, while the config debt is still P4's.

    The TOTAL is expected to be non-zero until P4 migrates the shipped configs.
    What must not grow is the set of RUNTIME files reading a dead key, because
    those fail silently: the loader refuses the v1 spelling, the reader sees an
    absent key, and a default takes over with nothing said.

    The list above can only shrink. A new entry fails here; removing one is a
    fix landing.
    """
    from dev.scripts.sweep_stale_spellings import REPO_ROOT

    defects, _ = sweep()
    offenders = {
        path.relative_to(REPO_ROOT).as_posix()
        for path, _, _, _ in defects
        if path.suffix in {".py", ".smk"} and "tests" not in path.parts
    }
    new = offenders - KNOWN_LIVE_V1_READERS
    assert not new, (
        "a retired spelling went live in a runtime file that was clean: "
        f"{sorted(new)}. The loader refuses the v1 key, so this read gets an "
        "absent value and falls back silently."
    )


@pytest.mark.parametrize("suffix", [".yml", ".py", ".md"])
def test_matching_is_position_sensitive(tmp_path, suffix):
    """A key DECLARATION counts; the same word in prose does not.

    The bare-token version of this sweep produced 1371 hits, almost all of them
    correct usage — a signal-to-noise ratio that guarantees the tool is ignored.
    """
    from dev.scripts.sweep_stale_spellings import sweep as run_sweep

    # Not a behavioural assertion about tmp files — the sweep walks the repo —
    # but a statement of the rule the implementation encodes.
    defects, allowed = run_sweep()
    prose_hits = [t for _, _, t, _ in defects if t.startswith("#")]
    assert not prose_hits, "a comment line was treated as a declaration"
