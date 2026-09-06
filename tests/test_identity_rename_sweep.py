"""`sweep_identity_renames` — the `X -> X` detector, and its falsification.

A green run on today's tree is worth nothing on its own: the tree is clean, so a
detector that matched nothing at all would pass identically. What makes the
check credible is that it fires on R14's real instances, which is what most of
this file is.

The seventh instance is the important one. It lived in
`t2608191733a`'s Overview from `51469c05` — the `C-85` rename commit itself —
until that note was closed on 2026-09-06, and its text is quoted verbatim below
from `t2609011315`. The FIRST draft of the prose form did not catch it: the
pattern excluded `.` to stay inside a sentence, and the spellings it compares
are filenames, so `.yml` put a dot inside the very token being matched. That is
the regression this file exists to prevent.
"""

from __future__ import annotations

import pytest

from dev.scripts.sweep_common import REPO_ROOT
from dev.scripts.sweep_identity_renames import (
    ALLOWANCES,
    FLOORS,
    SPECIMENS,
    check_specimens,
    sweep,
)

#: R14's seventh instance, verbatim. Two lines of a wrapped markdown callout,
#: with no arrow and no "is now" — the form that actually escaped.
SEVENTH_INSTANCE = """> [!note] Overview
> **What** — Rename every `project_config_*.yml` seed and template to
> `project_config_*.yml`, and update the `.gitignore` un-ignore glob, tests,
> docs, `AGENTS.md`, `pixi.toml` and every command line that names one.
"""

#: The same note's second decayed line: a sentence whose whole job was to
#: CONTRAST the two spellings, now contrasting a name with itself. Recorded
#: here as a known MISS — see the test at the bottom.
SEVENTH_INSTANCE_CONTRAST = (
    "experiment. `project_config_` says what the file *is*; `project_config_` "
    "says which program reads it."
)


def _tree(tmp_path, relative, text):
    path = tmp_path / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return tmp_path


# --- falsification against the real instances --------------------------------


def test_it_catches_R14s_seventh_instance(tmp_path):
    """The one that survived the milestone undetected, in the form it took."""
    root = _tree(tmp_path, "dev/tasks/t2608191733a-rename.md", SEVENTH_INSTANCE)
    defects, _allowed, observed = sweep(root)
    assert observed["prose_rename"] == 1
    assert len(defects) == 1
    assert defects[0][0].name == "t2608191733a-rename.md"


def test_a_dot_inside_the_spelling_does_not_hide_it(tmp_path):
    """The bug the first draft had, pinned as its own case.

    `project_config_*.yml` contains a dot, and a sentence-boundary class of
    `[^.]` cannot span it — so the pattern matched nothing at all against the
    instance it was written for, while still reporting a clean tree.
    """
    root = _tree(
        tmp_path,
        "docs/guide.md",
        "Rename every `a.yml` seed and template to `a.yml`, and update it.\n",
    )
    defects, _allowed, _observed = sweep(root)
    assert len(defects) == 1


@pytest.mark.parametrize(
    "text",
    [
        "The map keys `data/old` -> `data/old` for every artifact.\n",
        "The map keys `data/old` → `data/old` for every artifact.\n",
        "`snake_config_` is now `snake_config_`, which is the defect.\n",
        "`weagen` was retired in favour of `weagen` last milestone.\n",
    ],
)
def test_it_catches_the_arrow_and_verb_forms(tmp_path, text):
    root = _tree(tmp_path, "dev/reference/naming.md", text)
    defects, _allowed, _observed = sweep(root)
    assert len(defects) == 1, text


def test_it_catches_a_decayed_migration_row(tmp_path):
    """`C-85`'s own mapping row was one of the six."""
    root = _tree(
        tmp_path,
        "config/migrations/v1_to_v2.yml",
        "moves:\n"
        "      - old_path: T2.run_stress_test.spell_factors.dry\n"
        "        new_path: T2.run_stress_test.spell_factors.dry\n"
        "        op: rename\n",
    )
    defects, _allowed, observed = sweep(root)
    assert observed["yaml_move"] == 1
    assert len(defects) == 1


def test_it_catches_an_identity_in_a_rename_map(tmp_path):
    root = _tree(
        tmp_path,
        "dev/scripts/tool.py",
        'COPIED_CONFIG_PATH_MAP = {"config/a.yml": "config/a.yml"}\n',
    )
    defects, _allowed, _observed = sweep(root)
    assert len(defects) == 1


# --- what it must NOT report -------------------------------------------------


def test_a_retype_row_is_not_a_candidate_at_all(tmp_path):
    """`op: retype` keeps the key and changes only its value shape, so an
    identical pair under one is the record being CORRECT. Not an allowed hit —
    not a candidate, which is why `observed` stays at zero."""
    root = _tree(
        tmp_path,
        "config/migrations/v1_to_v2.yml",
        "moves:\n"
        "      - old_path: T2.analyze_projections.members\n"
        "        new_path: T2.analyze_projections.members\n"
        "        op: retype\n",
    )
    defects, _allowed, observed = sweep(root)
    assert observed["yaml_move"] == 0
    assert defects == []


def test_a_genuine_rename_record_is_not_reported(tmp_path):
    root = _tree(
        tmp_path,
        "dev/reference/naming.md",
        "`snake_config_` is now `project_config_`.\n"
        "Rename every `old.yml` seed to `new.yml` before running.\n",
    )
    defects, _allowed, observed = sweep(root)
    assert observed["verb"] + observed["prose_rename"] == 2
    assert defects == []


def test_the_live_tree_is_clean():
    """The weakest assertion here, and deliberately last: it is only meaningful
    because every test above shows the check can still fire."""
    defects, _allowed, _observed = sweep()
    assert defects == [], [(str(p), n, t) for p, n, t, _ in defects]


# --- failing closed ----------------------------------------------------------


def test_every_form_has_a_specimen_it_must_still_flag():
    """A population floor cannot be built for a form whose honest population is
    one record, and a floor of 1 passes a matcher that has gone blind."""
    assert not check_specimens(REPO_ROOT)
    assert set(SPECIMENS) == {
        "arrow",
        "verb",
        "prose_rename",
        "yaml_move",
        "python_rename_map",
    }


def test_a_floor_is_well_over_one_and_well_under_its_count():
    """The two numbers are separate on purpose: a floor at its measured count
    fails on honest churn, and a floor at 1 fails to fail."""
    for floor in FLOORS:
        assert floor.minimum > 1, floor.name
        assert floor.minimum < floor.count, floor.name
        assert floor.why.strip() and floor.measured.strip(), floor.name


def test_the_floors_still_hold_on_the_live_tree():
    from dev.scripts.sweep_common import check_floors

    _defects, _allowed, observed = sweep()
    assert not check_floors(FLOORS, observed)


def test_every_allowance_states_a_reason():
    """An allowlist entry without a reason is an exception nobody can review."""
    for allowance in ALLOWANCES:
        assert allowance.reason.strip(), allowance.name
        assert len(allowance.reason) > 40, allowance.name


def test_the_sealed_records_allowance_is_read_from_the_registry():
    """Hand-copying it would drift the moment a document is sealed, and the
    drift would surface as a defect report on a file a test forbids editing."""
    sealed = next(a for a in ALLOWANCES if a.name == "a sealed record")
    assert sealed.paths
    registry = (REPO_ROOT / "dev" / "reference" / "sealed-records.yml").read_text(
        encoding="utf-8"
    )
    for path in sealed.paths:
        assert path in registry


# --- the form that is deliberately NOT implemented ---------------------------


def test_the_contrast_form_is_a_known_MISS(tmp_path):
    """The seventh instance's OTHER decayed line, recorded as out of reach.

    "`X` says what the file *is*; `X` says which program reads it" is a rename
    record only by intent — there is no rename verb, no arrow, and no structural
    pair. Detecting it means recognising a repeated backticked token in a
    contrastive sentence, which fires on ordinary prose that mentions one
    spelling twice. Pinned as a MISS rather than left unstated, so a future
    reader knows the gap was measured rather than overlooked.
    """
    root = _tree(tmp_path, "dev/tasks/note.md", SEVENTH_INSTANCE_CONTRAST + "\n")
    defects, _allowed, _observed = sweep(root)
    assert defects == []
