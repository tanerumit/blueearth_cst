"""The T1+T2 loader composes to today's shape, and refuses what breaks the seam.

Unit surface for ``blueearth_cst/shared/config_composition.py`` (R13 §16.1).
Every case here is one row of the design's gate table, and the module is
deliberately self-contained: it builds its configs in ``tmp_path`` rather than
reading a shipped seed, so it keeps meaning while the seeds migrate in a later
commit and cannot be made green by a config edit.

Three groups carry most of the weight:

* **the composition invariant** — what comes out is what the pre-split config
  held, key for key. `enabled` merged, `config_path` not, an omitted
  `config_path` adding nothing at all;
* **the seam checks** — the four parse-time refusals, including the pair that is
  easy to invert: a broken workflow file *outside* this entry point's scope is
  skipped, and the identical file *inside* it is a hard error. Getting that
  backwards lets a broken WF3 config break a WF1 run, which is the inverse of
  what the milestone is for;
* **the static read scan** (D-9.6), which is checked in both directions and
  against a planted violation, so a green result means the scan looked rather
  than that it could not see.
"""

from __future__ import annotations

import copy
import hashlib
import json
import os
import subprocess
import sys
import textwrap
from pathlib import Path

import pytest
import yaml

from blueearth_cst.shared import config_composition as cc
from blueearth_cst.shared.provenance import effective_config_digest
from blueearth_cst.shared.snake_utils import ADVANCED_SETTINGS

REPO_ROOT = Path(__file__).resolve().parent.parent

#: The real ``CONFIG_PROJECTION`` of each entry point, and the ``R(entry)`` it
#: must produce (§8.3). Restated here rather than imported because a Snakefile
#: is not importable — which is exactly why the design passes the projection in
#: as an argument instead of restating it inside the loader.
PROJECTIONS = {
    "analyze_climate": (
        ("project", "shared", "workflows.analyze_climate"),
        {"analyze_climate"},
    ),
    "build_model": (
        ("project", "shared", "workflows.build_model"),
        {"build_model"},
    ),
    "analyze_projections": (
        ("project", "shared", "workflows.analyze_projections"),
        {"analyze_projections"},
    ),
    "run_stress_test": (
        (
            "project",
            "shared",
            "workflows.analyze_projections",
            "workflows.build_model",
            "workflows.run_stress_test",
        ),
        {"run_stress_test", "build_model", "analyze_projections"},
    ),
}


# ---------------------------------------------------------------------------
# Fixture builders
# ---------------------------------------------------------------------------


def write_split(
    directory: Path,
    stem: str = "snake_config_test",
    shared: dict | None = None,
    bodies: dict[str, dict] | None = None,
    enabled: dict[str, bool] | None = None,
    omit_path: tuple[str, ...] = (),
) -> Path:
    """Write a T1 file plus one T2 file per workflow body; return the T1 path.

    ``omit_path`` names workflows whose stanza gets no ``config_path`` even
    though a body was given — the shape D-8.7 accepts and the migration never
    produces.
    """
    directory.mkdir(parents=True, exist_ok=True)
    bodies = {} if bodies is None else bodies
    enabled = {} if enabled is None else enabled
    t1 = {
        "project": {"project_dir": (directory / "proj").as_posix()},
        "shared": {"basin": {"region": "x"}} if shared is None else shared,
        "workflows": {},
    }
    for name, body in bodies.items():
        stanza: dict[str, object] = {"enabled": enabled.get(name, True)}
        if name not in omit_path:
            t2_name = f"{stem}_{name}.yml"
            (directory / t2_name).write_text(
                yaml.safe_dump(body, sort_keys=False), encoding="utf-8"
            )
            stanza["config_path"] = t2_name
        t1["workflows"][name] = stanza
    t1_path = directory / f"{stem}.yml"
    t1_path.write_text(yaml.safe_dump(t1, sort_keys=False), encoding="utf-8")
    return t1_path


def compose(t1_path: Path, entry: str | None = "build_model") -> dict:
    """Compose ``t1_path`` for one entry point, using that entry's projection."""
    projection = PROJECTIONS[entry][0] if entry is not None else None
    return cc.load_composed_config(t1_path, entry, projection)


# ---------------------------------------------------------------------------
# The composition invariant (D-8.1, D-10.1, D-8.7, D-10.4)
# ---------------------------------------------------------------------------


def test_composed_document_equals_the_monolith_it_was_split_from(tmp_path):
    """D-8.1 in its plainest form: split then compose is the identity.

    The permanent digest-equality property test over the shipped seeds lands
    with the migration, once composed seeds exist to compare. This is the same
    claim on a config the test owns, so it holds from this commit on.
    """
    bodies = {
        "build_model": {
            "model_build_config": "config/defaults/wflow_build_model.yml",
            "observations": "obs.csv",
        },
        "analyze_projections": {"clim_project": "cmip6", "scenarios": ["ssp245"]},
    }
    t1_path = write_split(tmp_path / "cfg", bodies=bodies)
    composed = compose(t1_path, "run_stress_test")

    monolith = yaml.safe_load(t1_path.read_text(encoding="utf-8"))
    for name, body in bodies.items():
        monolith["workflows"][name].pop("config_path")
        monolith["workflows"][name].update(body)
    assert composed == monolith


def test_enabled_is_merged_and_config_path_is_not(tmp_path):
    """D-10.1, both halves.

    Dropping ``enabled`` would refuse every already-run experiment in every
    migrating project, because ``_frozen_differences`` is a key-union diff and a
    key present in a recorded ``experiment.yml`` but absent from the new
    document reads as *changed*. Adding ``config_path`` would do the mirror-image
    damage and make run identity depend on where a project stores its files.
    """
    t1_path = write_split(
        tmp_path / "cfg",
        bodies={"build_model": {"model_build_config": "wflow.yml"}},
        enabled={"build_model": False},
    )
    section = compose(t1_path)["workflows"]["build_model"]
    assert section == {"enabled": False, "model_build_config": "wflow.yml"}
    assert "config_path" not in section


def test_enabled_comes_first_so_recorded_bytes_are_stable(tmp_path):
    """``experiment.yml`` is dumped with ``sort_keys=False``, so order is bytes.

    Value-identity across migration is the guarantee; byte-identity holds
    whenever ``enabled`` was the block's first key, which this construction
    fixes by putting it there.
    """
    t1_path = write_split(
        tmp_path / "cfg", bodies={"run_stress_test": {"realizations_num": 2}}
    )
    section = compose(t1_path, "run_stress_test")["workflows"]["run_stress_test"]
    assert list(section) == ["enabled", "realizations_num"]


def test_omitted_config_path_composes_to_an_empty_body(tmp_path):
    """D-8.7. An omitted key adds nothing — not an empty mapping, nothing.

    ``effective_config_document`` digests the config *mapping*, so a key that is
    present rather than absent moves ``effective_config_digest`` even when the
    resolved value is identical. This is what keeps the projections overlay
    optional: a project that never runs WF2 needs no WF2 file on disk.
    """
    t1_path = write_split(
        tmp_path / "cfg",
        bodies={"build_model": {}, "analyze_projections": {}},
        omit_path=("build_model", "analyze_projections"),
    )
    composed, paths = cc.compose_config(
        yaml.safe_load(t1_path.read_text(encoding="utf-8")),
        t1_path,
        "run_stress_test",
        PROJECTIONS["run_stress_test"][0],
    )
    assert composed["workflows"]["build_model"] == {"enabled": True}
    assert composed["workflows"]["analyze_projections"] == {"enabled": True}
    assert paths == {}


def test_empty_t2_file_is_accepted_as_no_settings(tmp_path):
    """A file that parses to ``None`` is a workflow with no settings, not an error."""
    directory = tmp_path / "cfg"
    t1_path = write_split(directory, bodies={"build_model": {"a": 1}})
    (directory / "snake_config_test_build_model.yml").write_text("", encoding="utf-8")
    assert compose(t1_path)["workflows"]["build_model"] == {"enabled": True}


def test_no_section_is_hoisted_out_of_its_workflow(tmp_path):
    """R14 D-10.1. A T2 file's top-level section stays in that workflow.

    R13 D-10.4 carried `reporting:` OUT of ``workflows.run_stress_test`` so a
    figure caption sat outside ``CONFIG_PROJECTION``, the effective-config
    digest and the experiment freeze. `C-77` removes `reporting:` from the
    config surface, which empties the map, and R14 retires the mechanism rather
    than leaving it empty.

    The generic claim is what matters, so this asserts on an arbitrary section
    name rather than on `reporting:` — a hoist reinstated for some OTHER
    section would pass a test written about the one that left.
    """
    t1_path = write_split(
        tmp_path / "cfg",
        bodies={
            "run_stress_test": {
                "realizations_num": 2,
                "reporting": {"title": "Gabon"},
                "anything_else": {"k": "v"},
            }
        },
    )
    composed = compose(t1_path, "run_stress_test")
    section = composed["workflows"]["run_stress_test"]
    assert section["reporting"] == {"title": "Gabon"}
    assert section["anything_else"] == {"k": "v"}
    assert "reporting" not in composed
    assert "anything_else" not in composed


def test_the_hoist_registry_is_retired_not_emptied(tmp_path):
    """The falsifier for R14 D-10.1, and the reason it is a `hasattr` check.

    An empty registry that can be refilled cannot enforce shrink-only: adding a
    section plus a matching entry keeps every other test green. Same mechanism,
    and the same reason, as the ``CROSS_WORKFLOW_READS`` assertion below —
    which is also why this asserts on the BINDING rather than on the absence of
    the string. The module names both retired constants in prose, deliberately,
    so that a reader meets the argument for their absence; a grep-for-the-name
    test would forbid the record of the decision along with the decision.
    """
    assert not hasattr(cc, "HOISTED_SECTIONS"), (
        "the hoist registry is retired (R14 D-10.1, amending R13 D-10.4); a "
        "reinstated one -- even empty -- would let a section be carried out of "
        "run identity by adding an entry beside it"
    )


# ---------------------------------------------------------------------------
# R(entry) and the narrowing (§8.3, §8.1, §10.7)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("entry", sorted(PROJECTIONS))
def test_r_entry_is_derived_from_the_declared_projection(tmp_path, entry):
    """§8.3's table, as executable form.

    ``R(entry)`` is derived from the Snakefile's own ``CONFIG_PROJECTION``, never
    restated inside the loader. WF3's three-workflow scope follows because its
    projection is itself derived from ``guarded_sections`` — the drift
    protection is preserved end to end, with the loader as one more consumer of
    the same literal rather than a second copy of it.
    """
    projection, expected = PROJECTIONS[entry]
    bodies = {name: {f"{name}_key": 1} for name in cc.WORKFLOW_NAMES}
    t1_path = write_split(tmp_path / "cfg", bodies=bodies)
    composed, paths = cc.compose_config(
        yaml.safe_load(t1_path.read_text(encoding="utf-8")),
        t1_path,
        entry,
        projection,
    )
    populated = {
        name
        for name, section in composed["workflows"].items()
        if set(section) - {"enabled"}
    }
    assert populated == expected
    assert set(paths) == expected


def test_a_section_outside_scope_is_present_but_unpopulated(tmp_path):
    """The narrowing (§8.1), and why nothing is affected by it.

    A section outside ``R(entry)`` keeps its stanza — so
    ``provenance.project_config`` finds the path and raises no ``KeyError`` —
    but carries no body. Every reader of another workflow's section is already
    declared, so a reader added later that reaches into an unloaded section gets
    a loud parse-time ``KeyError`` gated by ``test_cli``, which is the correct
    outcome: the fix is to declare the dependency in ``CONFIG_PROJECTION``.
    """
    t1_path = write_split(
        tmp_path / "cfg",
        bodies={"build_model": {"a": 1}, "analyze_climate": {"b": 2}},
    )
    composed = compose(t1_path, "build_model")
    assert composed["workflows"]["analyze_climate"] == {"enabled": True}


def test_an_absent_stanza_is_not_created(tmp_path):
    """D-9.1's last sentence: absence is not this check's business.

    ``tests/test_cli.py`` pops ``workflows.analyze_climate`` entirely and asserts
    a WF1 dry-run still succeeds with identical job counts — the additive-carve
    regression. A popped stanza is absent, not malformed, so nothing fires and
    composition must not invent one.
    """
    t1_path = write_split(tmp_path / "cfg", bodies={"build_model": {"a": 1}})
    composed = compose(t1_path, "build_model")
    assert set(composed["workflows"]) == {"build_model"}


# ---------------------------------------------------------------------------
# Path resolution (D-8.4)
# ---------------------------------------------------------------------------


def test_relative_config_path_is_anchored_at_t1_not_the_cwd(tmp_path, monkeypatch):
    """The reversal, on the case that distinguishes the two rules.

    Two files of the same name exist — one beside T1, one in the working
    directory — with different contents. CWD anchoring is what the migration
    could not implement for a production ``project_dir`` outside the repository
    tree, so this is the discriminating assertion, not a formality.
    """
    beside_t1 = tmp_path / "project"
    t1_path = write_split(beside_t1, bodies={"build_model": {"marker": "beside_t1"}})

    elsewhere = tmp_path / "cwd"
    elsewhere.mkdir()
    (elsewhere / "snake_config_test_build_model.yml").write_text(
        yaml.safe_dump({"marker": "cwd"}), encoding="utf-8"
    )
    monkeypatch.chdir(elsewhere)

    assert compose(t1_path)["workflows"]["build_model"]["marker"] == "beside_t1"


def test_absolute_config_path_is_used_as_given(tmp_path):
    """An absolute path is never re-anchored."""
    directory = tmp_path / "cfg"
    directory.mkdir()
    t2 = tmp_path / "somewhere_else.yml"
    t2.write_text(yaml.safe_dump({"marker": "absolute"}), encoding="utf-8")
    t1_path = directory / "t1.yml"
    t1_path.write_text(
        yaml.safe_dump(
            {
                "project": {"project_dir": "p"},
                "shared": {},
                "workflows": {"build_model": {"enabled": True, "config_path": str(t2)}},
            }
        ),
        encoding="utf-8",
    )
    assert compose(t1_path)["workflows"]["build_model"]["marker"] == "absolute"


def test_tilde_in_config_path_is_expanded(tmp_path, monkeypatch):
    """``~`` is expanded before the relative test, so a home path is absolute."""
    home = tmp_path / "home"
    home.mkdir()
    (home / "wf1.yml").write_text(yaml.safe_dump({"marker": "home"}), encoding="utf-8")
    monkeypatch.setenv("HOME", str(home))
    monkeypatch.setenv("USERPROFILE", str(home))

    directory = tmp_path / "cfg"
    directory.mkdir()
    t1_path = directory / "t1.yml"
    t1_path.write_text(
        yaml.safe_dump(
            {
                "project": {"project_dir": "p"},
                "shared": {},
                "workflows": {
                    "build_model": {"enabled": True, "config_path": "~/wf1.yml"}
                },
            }
        ),
        encoding="utf-8",
    )
    assert compose(t1_path)["workflows"]["build_model"]["marker"] == "home"


def test_declared_path_is_cwd_relative_when_one_is_computable(tmp_path, monkeypatch):
    """``workflow_config_paths`` becomes rule inputs, so Snakemake must resolve it."""
    t1_path = write_split(tmp_path / "cfg", bodies={"build_model": {"a": 1}})
    monkeypatch.chdir(tmp_path)
    _, paths = cc.compose_config(
        yaml.safe_load(t1_path.read_text(encoding="utf-8")),
        t1_path,
        "build_model",
        PROJECTIONS["build_model"][0],
    )
    declared = paths["build_model"]
    assert not os.path.isabs(declared)
    assert os.path.isfile(declared)


def test_cross_drive_path_falls_back_to_absolute(tmp_path, monkeypatch):
    """On Windows ``os.path.relpath`` RAISES across drives — a caught error.

    A project on ``D:`` driven from a checkout on ``C:`` is an ordinary case
    here, and it is not reproducible by picking a path, so the failure is
    injected at the call the platform would fail at. An implementation that
    assumed a relative form always exists would raise instead of falling back.
    """
    t1_path = write_split(tmp_path / "cfg", bodies={"build_model": {"a": 1}})

    def _no_relative(*_args, **_kwargs):
        raise ValueError("path is on mount 'D:', start on mount 'C:'")

    monkeypatch.setattr(cc.os.path, "relpath", _no_relative)
    _, paths = cc.compose_config(
        yaml.safe_load(t1_path.read_text(encoding="utf-8")),
        t1_path,
        "build_model",
        PROJECTIONS["build_model"][0],
    )
    assert os.path.isabs(paths["build_model"])


# ---------------------------------------------------------------------------
# §8.4's failure table
# ---------------------------------------------------------------------------


def test_missing_t2_file_names_the_path_the_anchor_and_the_doc(tmp_path):
    """A dangling ``config_path`` is a hard error — a typo cannot pass.

    That is the distinction D-8.7 leans on: deleting the *file* while leaving
    the key fails loudly, while deleting the *key* is a two-step edit that says
    what it means.
    """
    directory = tmp_path / "cfg"
    t1_path = write_split(directory, bodies={"build_model": {"a": 1}})
    (directory / "snake_config_test_build_model.yml").unlink()

    with pytest.raises(ValueError) as excinfo:
        compose(t1_path)
    message = str(excinfo.value)
    assert "snake_config_test_build_model.yml" in message
    assert str(directory) in message
    assert cc.MIGRATION_DOC in message


def test_t2_file_that_is_not_a_mapping_is_refused(tmp_path):
    directory = tmp_path / "cfg"
    t1_path = write_split(directory, bodies={"build_model": {"a": 1}})
    (directory / "snake_config_test_build_model.yml").write_text(
        "- one\n- two\n", encoding="utf-8"
    )
    with pytest.raises(ValueError, match="not a mapping|list"):
        compose(t1_path)


def test_unparseable_t2_file_is_refused_with_the_parser_reason(tmp_path):
    directory = tmp_path / "cfg"
    t1_path = write_split(directory, bodies={"build_model": {"a": 1}})
    (directory / "snake_config_test_build_model.yml").write_text(
        "a: [1, 2\nb: {\n", encoding="utf-8"
    )
    with pytest.raises(ValueError, match="not valid YAML"):
        compose(t1_path)


@pytest.mark.parametrize("value", [42, ["a"], {"a": 1}, None])
def test_non_string_config_path_is_refused(tmp_path, value):
    directory = tmp_path / "cfg"
    directory.mkdir()
    t1_path = directory / "t1.yml"
    t1_path.write_text(
        yaml.safe_dump(
            {
                "project": {},
                "shared": {},
                "workflows": {"build_model": {"enabled": True, "config_path": value}},
            }
        ),
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="must be a path string"):
        compose(t1_path)


def test_empty_config_path_says_to_omit_the_key(tmp_path):
    """An empty string is a half-finished edit, and the fix is the D-8.7 shape."""
    directory = tmp_path / "cfg"
    directory.mkdir()
    t1_path = directory / "t1.yml"
    t1_path.write_text(
        yaml.safe_dump(
            {
                "project": {},
                "shared": {},
                "workflows": {"build_model": {"enabled": True, "config_path": "  "}},
            }
        ),
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="Omit the key"):
        compose(t1_path)


@pytest.mark.parametrize(
    "second",
    ["wf.yml", "./wf.yml", "WF.yml", ".\\wf.yml"],
    ids=["identical", "dot-prefixed", "case-only", "backslash-dot"],
)
def test_two_stanzas_sharing_one_file_are_refused(tmp_path, second):
    """The duplicate check compares ``normcase(abspath(...))``, not the raw string.

    A raw-string comparison is evaded by every spelling parametrized here, and
    no name-level check can substitute: with one file on disk there is only one
    file to compare. The repo has already paid for this bug class one layer
    down, in ``copy_config_files``' destination collision check — same
    comparison key, same reason.

    The case-only spelling only collides on a case-insensitive filesystem, which
    is where the silent-overwrite version of this bug lives.
    """
    if second == "WF.yml" and os.path.normcase("A") != "a":
        pytest.skip("case-only collision needs a case-insensitive filesystem")
    if second == ".\\wf.yml" and os.sep != "\\":
        pytest.skip("backslash separators are only a path on Windows")

    directory = tmp_path / "cfg"
    directory.mkdir()
    (directory / "wf.yml").write_text(yaml.safe_dump({"a": 1}), encoding="utf-8")
    t1_path = directory / "t1.yml"
    t1_path.write_text(
        yaml.safe_dump(
            {
                "project": {},
                "shared": {},
                "workflows": {
                    "build_model": {"enabled": True, "config_path": "wf.yml"},
                    "analyze_projections": {"enabled": True, "config_path": second},
                },
            }
        ),
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="resolve to the same file"):
        compose(t1_path, "run_stress_test")


# ---------------------------------------------------------------------------
# The seam checks (D-9.1, D-9.2, D-9.3, D-9.5)
# ---------------------------------------------------------------------------


def test_a_third_stanza_key_is_refused_and_names_the_key(tmp_path):
    """D-9.1. The closure is the migration detector as well as the seam check."""
    directory = tmp_path / "cfg"
    directory.mkdir()
    t1_path = directory / "t1.yml"
    t1_path.write_text(
        yaml.safe_dump(
            {
                "project": {},
                "shared": {},
                "workflows": {
                    "build_model": {"enabled": True, "model_build_config": "x.yml"}
                },
            }
        ),
        encoding="utf-8",
    )
    with pytest.raises(ValueError) as excinfo:
        compose(t1_path)
    message = str(excinfo.value)
    assert "model_build_config" in message
    # Asserted through the constant, not as a literal: `MIGRATION_COMMAND` is a
    # cross-phase pin (R14 Gate A) and a second spelling of it here would be a
    # second place to forget when P3 ships the script.
    assert cc.MIGRATION_COMMAND in message


def test_stanza_closure_is_checked_outside_this_entry_points_scope(tmp_path):
    """D-9.1's scope, which the two readings answer oppositely.

    Checking closure only for ``R(entry)`` would make a half-split config legal:
    a project that split ``build_model`` and left the other three inline would
    run WF1 clean — the very defect the clean-break posture rejects, arriving
    through this design's own door.
    """
    directory = tmp_path / "cfg"
    directory.mkdir()
    t1_path = directory / "t1.yml"
    t1_path.write_text(
        yaml.safe_dump(
            {
                "project": {},
                "shared": {},
                "workflows": {
                    "build_model": {"enabled": True},
                    "run_stress_test": {"enabled": True, "realizations_num": 2},
                },
            }
        ),
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="realizations_num"):
        compose(t1_path, "build_model")


def test_a_stray_t1_top_level_key_is_refused(tmp_path):
    """D-9.5, which is what makes the migration detector complete.

    A config whose only unmigrated element is a top-level ``reporting:``
    produces no extra key under any ``workflows.<name>``, so the stanza check
    alone sees nothing. Closing the top level also turns the hoist-collision
    question into a non-question: there is no precedence rule to define because
    a collision cannot be constructed.
    """
    directory = tmp_path / "cfg"
    directory.mkdir()
    t1_path = directory / "t1.yml"
    t1_path.write_text(
        yaml.safe_dump(
            {
                "project": {},
                "shared": {},
                "workflows": {"build_model": {"enabled": True}},
                "reporting": {"title": "left behind"},
            }
        ),
        encoding="utf-8",
    )
    with pytest.raises(ValueError) as excinfo:
        compose(t1_path)
    assert "reporting" in str(excinfo.value)


def test_a_shared_key_planted_in_a_t2_file_is_refused(tmp_path):
    """D-9.2. A key read by more than one workflow lives in T1, never in a T2."""
    t1_path = write_split(
        tmp_path / "cfg",
        shared={"basin": {"region": "x"}, "clim_historical": "era5"},
        bodies={"build_model": {"clim_historical": "chirps"}},
    )
    with pytest.raises(ValueError) as excinfo:
        compose(t1_path)
    message = str(excinfo.value)
    assert "clim_historical" in message
    assert "`shared:`" in message


def test_a_frozen_seam_key_absent_from_this_t1_is_still_refused(tmp_path):
    """Why ``SHARED_SEAM_KEYS`` exists rather than deriving from T1 alone.

    A T1 that omits the optional ``shared.seed`` would not reject a ``seed:``
    planted in a T2 file — the exact failure the rule is written against.
    """
    t1_path = write_split(
        tmp_path / "cfg",
        shared={"basin": {"region": "x"}},
        bodies={"build_model": {"seed": 99}},
    )
    assert "seed" not in yaml.safe_load(t1_path.read_text(encoding="utf-8"))["shared"]
    with pytest.raises(ValueError, match="seed"):
        compose(t1_path)


def test_a_formerly_hoisted_name_is_now_an_ordinary_workflow_key(tmp_path):
    """What the retirement gives up, asserted rather than left implicit.

    D-9.2 carried a final term — every hoisted section except the ones this
    workflow owns — so a ``reporting:`` block written at the top of
    ``build_model``'s file was REFUSED. With the map retired the name is
    ordinary: it merges into ``workflows.build_model`` like any other key that
    workflow declares.

    That is a real reduction in what parse time catches, and it is sound only
    because the section it protected no longer exists on the config surface
    (`C-77`). The general seam rule is untouched — a name owned outside one
    workflow is still refused — so what is lost is exactly the special case,
    and nothing more.
    """
    t1_path = write_split(
        tmp_path / "cfg", bodies={"build_model": {"reporting": {"title": "own file"}}}
    )
    composed = compose(t1_path)
    assert composed["workflows"]["build_model"]["reporting"] == {"title": "own file"}


def test_an_independent_same_named_pair_across_two_t2_files_parses(tmp_path):
    """The r3 restriction: the seam is defined by CONSUMPTION, not spelling.

    Two workflows can legitimately own unrelated settings that happen to share a
    local name; their workflow namespaces distinguish them and neither reads the
    other's. Rejecting the pair would force artificial names or needless hoists,
    degrading the modular boundary this design exists to build. What the earlier
    unconditional rejection bought — first-symptom detection of a genuinely new
    cross-workflow key — is carried by the static scan instead.
    """
    t1_path = write_split(
        tmp_path / "cfg",
        bodies={
            "build_model": {"output_dir": "models/wflow"},
            "analyze_projections": {"output_dir": "climate/cmip6"},
        },
    )
    composed = compose(t1_path, "run_stress_test")
    assert composed["workflows"]["build_model"]["output_dir"] == "models/wflow"
    assert composed["workflows"]["analyze_projections"]["output_dir"] == "climate/cmip6"


def test_a_shared_key_is_refused_in_a_file_outside_this_entry_points_scope(tmp_path):
    """D-9.3's every-file reach, which is what distinguishes it from D-9.2.

    Three of the four entry points have a singleton ``R(entry)``, so a check
    confined to the composed set has exactly one file to look at and could never
    see a shared name planted in another workflow's file.
    """
    t1_path = write_split(
        tmp_path / "cfg",
        shared={"basin": {"region": "x"}},
        bodies={
            "build_model": {"a": 1},
            "run_stress_test": {"basin": {"region": "planted"}},
        },
    )
    with pytest.raises(ValueError, match="basin"):
        compose(t1_path, "build_model")


@pytest.mark.parametrize(
    "breakage",
    ["missing", "unparseable", "not_mapping"],
)
def test_a_broken_file_outside_scope_is_skipped_and_inside_scope_is_fatal(
    tmp_path, breakage, capsys
):
    """The tolerance clause and its boundary, as one paired assertion.

    Load-bearing and easy to invert: without the clause a broken WF3 config
    would break a WF1 run, which is the inverse of this milestone's goal — a
    workflow's own file must not be able to fail another workflow's parse. With
    the clause applied too widely, a genuinely missing file this entry point
    needs would pass silently.
    """
    directory = tmp_path / "cfg"
    t1_path = write_split(
        directory,
        bodies={"build_model": {"a": 1}, "run_stress_test": {"b": 2}},
    )
    wf3_file = directory / "snake_config_test_run_stress_test.yml"
    if breakage == "missing":
        wf3_file.unlink()
    elif breakage == "unparseable":
        wf3_file.write_text("a: [1, 2\n", encoding="utf-8")
    else:
        wf3_file.write_text("- a\n- b\n", encoding="utf-8")

    # WF1 does not load the WF3 file: skipped, logged, and the run proceeds.
    composed = compose(t1_path, "build_model")
    assert composed["workflows"]["build_model"]["a"] == 1
    assert "run_stress_test" in capsys.readouterr().out

    # WF3 does load it, so the identical file is a hard error.
    with pytest.raises(ValueError):
        compose(t1_path, "run_stress_test")


# ---------------------------------------------------------------------------
# The static cross-workflow read scan (D-9.6)
# ---------------------------------------------------------------------------


def test_scan_surfaces_cover_the_run_path_and_stop_at_dev_scripts():
    """The scan reads every authorized runtime-consumer surface, and only those.

    ``dev/scripts/`` stays outside on the repository's own invocation-model
    rule: it is never part of a run, and a ``dev/scripts/`` tool that acquires a
    run-path caller must move into the shipped package — where the scan sees it.
    """
    surfaces = cc.scan_surfaces(REPO_ROOT)
    for name in cc.WORKFLOW_NAMES:
        assert f"{name}.smk" in surfaces
    assert any(s.startswith("blueearth_cst/") for s in surfaces)
    assert any(s.startswith("scripts/") for s in surfaces)
    assert not any(s.startswith("dev/") for s in surfaces)
    assert not any("__pycache__" in s for s in surfaces)


def test_cross_workflow_reads_are_complete_and_minimal():
    """D-9.6, both directions, over the real tree.

    A grep sweep is a snapshot; this is the thing that keeps the inventory
    honest. **Completeness**: an undeclared cross-workflow read anywhere on the
    scanned surfaces turns this red — and the fix is to promote the key to
    ``shared:``, never to add an entry here. **Minimality**: a declared entry
    with no live site is equally a failure, so no enumeration can drift stale.

    The three enumerations are compared separately rather than merged, so that
    retiring ``CROSS_WORKFLOW_READS`` in the hoist commit cannot silently absorb
    an identity comparison into a value read.
    """
    value_reads, identity, ownerless = cc.partition_hits(
        cc.scan_cross_workflow_reads(REPO_ROOT)
    )
    assert value_reads == frozenset(), (
        "a cross-workflow VALUE read exists. There is no registry to add it to, "
        "on purpose: promote the key to `shared:` instead. An expandable "
        "allowlist cannot enforce shrink-only -- a read plus a matching entry "
        "keeps the test green -- so the assertion is a literal zero."
    )
    assert identity == cc.IDENTITY_COMPARISONS
    assert ownerless == cc.OWNERLESS_SECTION_READS


def test_the_scan_detects_a_planted_cross_workflow_read(tmp_path):
    """The scan can FAIL, which is what makes the assertion above evidence.

    A test that only ever ran against a clean tree would pass forever whether or
    not the patterns matched anything. This plants the violation the rule
    exists to catch — a stage module reading another workflow's settings — in a
    synthetic tree shaped like the real one.
    """
    for name in cc.WORKFLOW_NAMES:
        (tmp_path / f"{name}.smk").write_text("rule all:\n    input: []\n", "utf-8")
    stage = tmp_path / "blueearth_cst" / "projections"
    stage.mkdir(parents=True)
    (tmp_path / "scripts").mkdir()
    (stage / "sneaky.py").write_text(
        textwrap.dedent(
            '''
            """A stage module reaching across the section boundary."""
            from blueearth_cst.shared.snake_utils import get_config


            def horizons(config):
                return get_config(config["workflows"]["build_model"], "simulation_window")
            '''
        ).lstrip(),
        encoding="utf-8",
    )
    hits = cc.scan_cross_workflow_reads(tmp_path)
    value_reads, _, _ = cc.partition_hits(hits)
    assert ("analyze_projections", "build_model", "simulation_window") in value_reads


def test_the_scan_ignores_prose_that_quotes_a_projection(tmp_path):
    """A docstring or comment naming a section is prose about a read, not a read.

    ``provenance.project_config``'s docstring quotes ``"workflows.build_model"``
    verbatim to explain what a projection is. A scan that could not tell them
    apart would force a prose sentence into a contract enumeration — which is
    how an allowlist starts absorbing things nobody reviewed.
    """
    for name in cc.WORKFLOW_NAMES:
        (tmp_path / f"{name}.smk").write_text("rule all:\n    input: []\n", "utf-8")
    stage = tmp_path / "blueearth_cst" / "shared"
    stage.mkdir(parents=True)
    (tmp_path / "scripts").mkdir()
    (stage / "prose.py").write_text(
        textwrap.dedent(
            '''
            """A projection is a list of dotted paths -- "workflows.build_model"
            for WF1, for instance.
            """


            def helper(config):
                # config["workflows"]["build_model"] used to be read here
                return config
            '''
        ).lstrip(),
        encoding="utf-8",
    )
    assert cc.scan_cross_workflow_reads(tmp_path) == ()


# ---------------------------------------------------------------------------
# The binding invariant (D-8.6a)
# ---------------------------------------------------------------------------


@pytest.mark.workflow_contract
def test_the_composed_shape_is_visible_through_snakemake_workflow_config(tmp_path):
    """The rebinding is load-bearing, and nothing in the loader can enforce it.

    ``check_project_consistency`` takes its live config from ``sm.config`` —
    Snakemake's ``workflow.config`` — not from the Snakefile's local name. A
    ``composed = compose_config(...)`` refactor would leave the drift guard
    comparing ``{enabled, config_path}`` against the snapshot's full section and
    fail every WF3 run at rule 3.01, **after WF1 and WF2 have already run**,
    with a message blaming project drift rather than the binding.

    Checked here against a synthetic Snakefile rather than a shipped one, so the
    invariant is pinned from the commit that introduces the loader — before the
    four entry points are wired to call it.
    """
    t1_path = write_split(
        tmp_path / "cfg", bodies={"build_model": {"model_build_config": "x.yml"}}
    )
    snakefile = tmp_path / "probe.smk"
    snakefile.write_text(
        textwrap.dedent(
            f"""
            import sys
            sys.path.insert(0, {str(REPO_ROOT)!r})
            from blueearth_cst.shared.config_composition import compose_config

            config, WORKFLOW_CONFIG_PATHS = compose_config(
                config, workflow.configfiles[0], entry="build_model",
                declared_sections=("project", "shared", "workflows.build_model"),
            )
            LIVE = workflow.config["workflows"]["build_model"]
            assert LIVE == {{"enabled": True, "model_build_config": "x.yml"}}, LIVE

            rule all:
                run:
                    pass
            """
        ).lstrip(),
        encoding="utf-8",
    )
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "snakemake",
            "all",
            "-c",
            "1",
            "-s",
            str(snakefile),
            "--configfile",
            str(t1_path),
            "--dry-run",
        ],
        capture_output=True,
        text=True,
        cwd=str(tmp_path),
    )
    assert result.returncode == 0, (result.stdout or "") + (result.stderr or "")


# ---------------------------------------------------------------------------
# The tool-facing wrapper (D-12.0)
# ---------------------------------------------------------------------------


def test_load_composed_config_without_an_entry_loads_every_resolvable_file(tmp_path):
    """ "Whatever section I index" is the right scope for a caller that is not
    an entry point — the ``tree-check`` snapshot tool, the cache pruners, the
    DAG renderer. Each becomes a two-line change: import this, call it instead
    of ``yaml.safe_load``.
    """
    t1_path = write_split(
        tmp_path / "cfg",
        bodies={
            "build_model": {"a": 1},
            "analyze_projections": {"b": 2},
            "run_stress_test": {"experiment_name": "gabon"},
        },
    )
    composed = cc.load_composed_config(t1_path)
    assert composed["workflows"]["run_stress_test"]["experiment_name"] == "gabon"
    assert composed["workflows"]["build_model"]["a"] == 1
    assert composed["workflows"]["analyze_projections"]["b"] == 2


def test_a_broken_workflow_file_does_not_break_a_tool(tmp_path, capsys):
    """The tolerance clause is what keeps ``tree-check`` reporting on a project
    whose WF3 config is mid-edit, instead of reporting nothing at all."""
    directory = tmp_path / "cfg"
    t1_path = write_split(
        directory, bodies={"build_model": {"a": 1}, "run_stress_test": {"b": 2}}
    )
    (directory / "snake_config_test_run_stress_test.yml").write_text(
        "a: [1, 2\n", encoding="utf-8"
    )
    composed = cc.load_composed_config(t1_path)
    assert composed["workflows"]["build_model"]["a"] == 1
    assert composed["workflows"]["run_stress_test"] == {"enabled": True}
    assert "run_stress_test" in capsys.readouterr().out


# ---------------------------------------------------------------------------
# Digest equality across the migration (D-10.2, §16.1)
# ---------------------------------------------------------------------------

#: Each shipped config, as (frozen pre-split specimen, live post-split project
#: file, entry point). The pre-split side is the file that WAS live until the
#: R13 migration, kept under tests/data/presplit/ precisely so this comparison
#: stays possible after the tree moved.
MIGRATED = [
    ("snake_config_rapid.yml", "test_case/snake_config_rapid.yml"),
    ("snake_config_baseline.yml", "test_case/snake_config_baseline.yml"),
    ("snake_config_baseline_linux.yml", "test_case/snake_config_baseline_linux.yml"),
    ("snake_config_wf2_fast.yml", "test_case/snake_config_wf2_fast.yml"),
    ("snake_config.template.yml", "config/templates/snake_config.template.yml"),
]

PRESPLIT_DIR = REPO_ROOT / "tests" / "data" / "presplit"


def _relocated(doc):
    """A pre-split document with the declared R13 relocations applied.

    ``wflow_outvars`` was hoisted from ``workflows.build_model`` to ``shared:``
    inside R13 (D-9.7), so the digest comparison below is exact **up to that
    one declared row** rather than exact. Normalizing here rather than
    loosening the assertion keeps every other key held to equality: a second
    key that moved would still fail, which is the whole value of the check.

    The hoist DOES shift both digests on a real project, deliberately and
    expectedly, and that shift has its own falsifier pass. What this test
    rules out is an *unattributed* shift.
    """
    doc = copy.deepcopy(doc)
    for source_path, dest_path in cc.RELOCATED_KEYS.items():
        node = doc
        for key in source_path[:-1]:
            node = node.get(key) if isinstance(node, dict) else None
            if node is None:
                break
        if not isinstance(node, dict) or source_path[-1] not in node:
            continue
        value = node.pop(source_path[-1])
        target = doc
        for key in dest_path[:-1]:
            target = target.setdefault(key, {})
        target[dest_path[-1]] = value
    return doc


def _guarded_digest(cfg):
    """WF3's guarded-sections digest, computed exactly as the Snakefile does.

    Restated here rather than imported because a Snakefile is not importable.
    It is the rerun trigger for rule 3.01, so a shift in it is a shift in when
    the drift guard fires.
    """
    return hashlib.sha256(
        json.dumps(
            {
                "project": cfg.get("project"),
                "shared.basin": cfg.get("shared", {}).get("basin"),
                "workflows.build_model": cfg.get("workflows", {}).get("build_model"),
                "workflows.analyze_projections": cfg.get("workflows", {}).get(
                    "analyze_projections"
                ),
            },
            sort_keys=True,
            ensure_ascii=False,
            default=str,
        ).encode("utf-8")
    ).hexdigest()


@pytest.mark.parametrize(("presplit", "live"), MIGRATED, ids=[p for p, _ in MIGRATED])
@pytest.mark.parametrize("entry", sorted(PROJECTIONS))
def test_effective_config_digest_survives_the_migration(presplit, live, entry):
    """D-10.2 in executable form, and the reason §16.3's falsifier can be read.

    ``effective_config_digest`` is threaded through rule x.01's params, so if the
    split moved it, every workflow's record would re-fire on every migrated
    project and the baseline comparison could not distinguish "the split changed
    a number" from "the split changed where a number is written". It does not
    move, by construction — same projection paths, same values, same canonical
    JSON — and this is what holds that construction to account.

    ``ADVANCED_SETTINGS`` is held fixed on both sides deliberately.
    ``effective_config_document`` folds that whole mapping in UNPROJECTED, so a
    change to its *shape* moves this digest for all four entry points. R13 moves
    no advanced-settings key; stating the invariant here keeps the test from
    silently depending on it.
    """
    projection = PROJECTIONS[entry][0]
    before = _relocated(
        yaml.safe_load((PRESPLIT_DIR / presplit).read_text(encoding="utf-8"))
    )
    after = cc.load_composed_config(REPO_ROOT / live, entry, projection)
    assert effective_config_digest(
        before, ADVANCED_SETTINGS, projection
    ) == effective_config_digest(after, ADVANCED_SETTINGS, projection)


@pytest.mark.parametrize(("presplit", "live"), MIGRATED, ids=[p for p, _ in MIGRATED])
def test_guarded_sections_digest_survives_the_migration(presplit, live):
    """The WF3 drift guard's rerun trigger does not move either.

    Separate from the effective-config digest because it is built by hand in the
    Snakefile from four specific sections rather than from the projection, and
    because it is what decides whether rule 3.01 re-fires against an
    already-built model. A shift here would refuse every already-run experiment
    in every migrating project.
    """
    before = _relocated(
        yaml.safe_load((PRESPLIT_DIR / presplit).read_text(encoding="utf-8"))
    )
    after = cc.load_composed_config(
        REPO_ROOT / live, "run_stress_test", PROJECTIONS["run_stress_test"][0]
    )
    assert _guarded_digest(before) == _guarded_digest(after)


def test_write_config_round_trips_through_compose(tmp_path):
    """``compose_config(write_config(cfg)) == cfg`` — D-12.6's gate.

    ``tests/conftest.write_config`` is what let the suite's dominant config
    idiom survive the split unchanged: tests keep mutating one whole mapping and
    the helper writes it back as a T1 + T2 set. Without this property the helper
    would be a second, unchecked way to build a config, and every test that used
    it would be asserting against a shape no run can have.
    """
    from tests.conftest import write_config

    cfg = cc.load_composed_config(REPO_ROOT / "test_case/snake_config_rapid.yml")
    # A workflow-owned section, not a top-level one: with the hoist retired
    # (R14 D-10.1) a top-level key outside `T1_TOP_LEVEL` is a parse error, so
    # the round trip is exercised where a section can actually live.
    cfg["workflows"]["run_stress_test"]["reporting"] = {"title": "round trip"}
    assert cc.load_composed_config(write_config(tmp_path, cfg)) == cfg


def test_the_hoisted_key_is_refused_inside_a_workflow_file(tmp_path):
    """D-9.7's placement, enforced by construction rather than by a new check.

    Adding ``wflow_outvars`` to ``SHARED_SEAM_KEYS`` is the whole mechanism: a
    copy planted in any workflow file is then refused by D-9.2/D-9.3 with no
    rule written for this key specifically. That is what the frozen set is for,
    and it is why the hoist is a two-line contract change rather than a feature.
    """
    t1_path = write_split(
        tmp_path / "cfg",
        shared={"basin": {"region": "x"}, "wflow_outvars": ["river discharge"]},
        bodies={"build_model": {"wflow_outvars": ["snow"]}},
    )
    with pytest.raises(ValueError) as excinfo:
        compose(t1_path)
    message = str(excinfo.value)
    assert "wflow_outvars" in message
    assert "`shared:`" in message


def test_the_hoisted_key_reaches_both_readers_from_shared(tmp_path):
    """Both workflows read the same value from one place, which is the point.

    WF1 builds the model with it and WF3 derives its indicator tables from it.
    Before the hoist that was the repository's ONE cross-workflow value read,
    and the registry existed to sanction it; now there is one authoring site and
    no registry.
    """
    t1_path = write_split(
        tmp_path / "cfg",
        shared={"basin": {"region": "x"}, "wflow_outvars": ["river discharge"]},
        bodies={"build_model": {"model_build_config": "x.yml"}, "run_stress_test": {}},
    )
    for entry in ("build_model", "run_stress_test"):
        composed = compose(t1_path, entry)
        assert composed["shared"]["wflow_outvars"] == ["river discharge"]


def test_the_relocation_map_is_one_declared_row(tmp_path):
    """`RELOCATED_KEYS` records a move; it sanctions no read.

    It is deliberately not a successor to the retired registry. A reader who
    treated it as one would reintroduce exactly the expandable allowlist D-9.7
    removed, so this pins both its content and its shape.
    """
    assert cc.RELOCATED_KEYS == {
        ("workflows", "build_model", "wflow_outvars"): ("shared", "wflow_outvars")
    }
    assert not hasattr(cc, "CROSS_WORKFLOW_READS"), (
        "the cross-workflow read registry is retired; a reinstated one would let "
        "a new read be sanctioned by adding a tuple beside it"
    )
    for _, dest in cc.RELOCATED_KEYS.items():
        assert dest[0] == "shared" and dest[1] in cc.SHARED_SEAM_KEYS, (
            "a relocated key must land in `shared:` AND be in the frozen seam set, "
            "or a copy planted in a workflow file would still parse"
        )
