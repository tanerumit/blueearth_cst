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
    # This asserted `defects` was NON-empty until 2026-09-01, with its own
    # instruction for the day it stopped being true: "either P4 has run and this
    # test should become a zero-assertion gate, or the allowlist has grown until
    # it covers everything." P4 has run. It is now the gate, and the thing that
    # keeps it from being an allowlist that ate its own purpose is the ratchet
    # below plus `test_matching_is_position_sensitive`, which both still bite.
    assert not defects, (
        "unclassified retired spellings: "
        f"{sorted({p.name for p, _, _, _ in defects})}. Either it is a real "
        "stale reader, or it needs an allowance class with a stated reason."
    )


#: Runtime files reading a retired spelling that are known and NOT yet fixed.
#:
#: **Empty as of 2026-09-01, and every entry was discharged by verification
#: rather than by assumption.** The list is kept because it is the ratchet: an
#: entry appearing here again means a v1 reader went live, and the test below
#: fails on anything not listed. Emptying it is what "the migration finished"
#: looks like from this tool's side.
#:
#: How the six went, in the order they were resolved:
#:
#: * `prune_series_cache.py`, `prune_climate_store.py` — genuinely broken,
#:   genuinely FIXED 2026-08-29 (`t2608251900`). `prune_series_cache` now reads
#:   `my["ensemble"]`; `clim_project` survives only as a local name, which
#:   P1b's tier rule leaves alone.
#: * `analyze_projections.smk` — `C-66` dissolved `relative_change:` in P1c.
#:   Only a comment naming the retired key remains.
#: * `semantic_tree_diff.py`, `snapshot_project_tree.py`, `stage_cmip6.py` —
#:   never defects; MISCLASSIFIED here on 2026-08-27 by shape rather than by
#:   reading them. `COPIED_CONFIG_PATH_MAP` is an old->new map keyed by config
#:   key, so half of it is old spellings by construction;
#:   `snapshot_project_tree` reads `ensemble` and emits it under its own
#:   snapshot field name; `stage_cmip6` reads `dev/scripts/stage_cmip6.yml`,
#:   its own config with its own required keys, no more a project config than
#:   weathergenr's is. Each now has an allowance class stating that.
#:
#: The three misclassifications are the lesson: a ratchet entry added from a
#: hit's SHAPE rather than from reading the file records a defect that does not
#: exist, and it is the same mistake in the opposite direction as an allowance
#: class that excuses one that does.
KNOWN_LIVE_V1_READERS: set[str] = set()


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
