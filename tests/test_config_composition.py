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

import os
import subprocess
import sys
import textwrap
from pathlib import Path

import pytest
import yaml

from blueearth_cst.shared import config_composition as cc

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
            "wflow_outvars": ["river discharge"],
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
        bodies={"build_model": {"wflow_outvars": ["q"]}},
        enabled={"build_model": False},
    )
    section = compose(t1_path)["workflows"]["build_model"]
    assert section == {"enabled": False, "wflow_outvars": ["q"]}
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


def test_reporting_is_hoisted_out_of_its_owning_section(tmp_path):
    """D-10.4. ``reporting:`` reaches ``config["reporting"]``, not the section.

    Hoisting rather than nesting is what keeps the key outside
    ``CONFIG_PROJECTION``, the effective-config digest and the experiment
    freeze — a deliberate exclusion that lets a caption be corrected without
    re-running the experiment. Nesting would silently revoke it.
    """
    t1_path = write_split(
        tmp_path / "cfg",
        bodies={
            "run_stress_test": {
                "realizations_num": 2,
                "reporting": {"title": "Gabon"},
            }
        },
    )
    composed = compose(t1_path, "run_stress_test")
    assert composed["reporting"] == {"title": "Gabon"}
    assert "reporting" not in composed["workflows"]["run_stress_test"]


def test_reporting_is_not_hoisted_when_its_owner_is_out_of_scope(tmp_path):
    """A WF1 run never loads the WF3 file, so nothing is hoisted from it."""
    t1_path = write_split(
        tmp_path / "cfg",
        bodies={"build_model": {"a": 1}, "run_stress_test": {"reporting": {"t": "x"}}},
    )
    assert "reporting" not in compose(t1_path, "build_model")


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
                "workflows": {"build_model": {"enabled": True, "wflow_outvars": ["q"]}},
            }
        ),
        encoding="utf-8",
    )
    with pytest.raises(ValueError) as excinfo:
        compose(t1_path)
    message = str(excinfo.value)
    assert "wflow_outvars" in message
    assert "split_project_config.py" in message


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


def test_reporting_in_a_non_owning_t2_file_is_refused(tmp_path):
    """D-9.2's final term, derived from the hoist map rather than a hand list.

    Without it a ``reporting:`` block written at the top of ``build_model``'s
    file would be accepted and merged into ``workflows.build_model``, which is a
    guarded section — so a caption edit in the wrong file would enter
    ``guarded_sections_digest`` and produce a *"your model was built under
    different settings"* refusal from rule 3.01, for a change to a figure
    caption.
    """
    t1_path = write_split(
        tmp_path / "cfg", bodies={"build_model": {"reporting": {"title": "wrong file"}}}
    )
    with pytest.raises(ValueError) as excinfo:
        compose(t1_path)
    message = str(excinfo.value)
    assert "reporting" in message
    assert "run_stress_test" in message


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
    assert value_reads == cc.CROSS_WORKFLOW_READS, (
        "cross-workflow VALUE reads drifted from the declared set. A new one is "
        "not an entry to add: promote the key to `shared:` (S4). A stale one "
        "means the read is gone and the entry must go with it."
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
        tmp_path / "cfg", bodies={"build_model": {"wflow_outvars": ["q"]}}
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
            assert LIVE == {{"enabled": True, "wflow_outvars": ["q"]}}, LIVE

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
