"""R07 B8: experiment_name is SUGGESTED once, never generated at run time.

The helper slugifies because ``basename(project_dir)`` is not guaranteed to
satisfy the grammar the workflow enforces (repo-7): ``examples/Gabon`` was live
in six shipped configs, and production project_dir values routinely carry
uppercase, hyphens or spaces. The design's original evidence ("both
gabon260725 and gabon_20260726 already satisfy the grammar") only tested names
that already conformed.
"""

import subprocess
import sys
from pathlib import Path

import pytest
import yaml

from blueearth_cst.shared.config_composition import load_composed_config
from blueearth_cst.shared.snake_utils import (  # noqa: E402
    suggest_experiment_name,
    validate_experiment_name,
)

SNAKEDIR = Path(__file__).resolve().parents[1]
CLI = SNAKEDIR / "scripts" / "suggest_experiment_name.py"


@pytest.mark.parametrize(
    "project_dir, expected",
    [
        ("examples/Gabon", "gabon_20260728"),  # the live counterexample
        ("test_case/test_local", "test_local_20260728"),
        ("/mnt/data/My Basin-2024", "my_basin_2024_20260728"),
        (r"C:\runs\Rhine--Upper", "rhine_upper_20260728"),
        ("trailing/slash/", "slash_20260728"),
        ("__leading_junk", "leading_junk_20260728"),
    ],
)
def test_slugification(project_dir, expected):
    assert suggest_experiment_name(project_dir, "20260728") == expected


def test_suggestion_always_satisfies_the_validator():
    """The proposal is passed back through validate_experiment_name, so the
    suggester and the workflow's own gate can never disagree."""
    for pd in ("examples/Gabon", "/mnt/x/A B C", "UPPER", "9lives"):
        name = suggest_experiment_name(pd, "20260728")
        assert validate_experiment_name(name, "/tmp/proj") == name


def test_truncation_keeps_the_date_and_stays_valid():
    name = suggest_experiment_name("x/" + "a" * 200, "20260728")
    assert len(name) <= 64
    assert name.endswith("_20260728")
    assert validate_experiment_name(name, "/tmp/proj") == name


def test_basename_without_alphanumerics_raises():
    with pytest.raises(ValueError, match="no alphanumeric"):
        suggest_experiment_name("/data/---", "20260728")


def _run(cfg, *extra):
    return subprocess.run(
        [sys.executable, str(CLI), str(cfg), "--date", "20260728", *extra],
        capture_output=True,
        text=True,
    )


def _cfg(tmp_path, experiment_name=None):
    """A project config plus the run_stress_test settings file it points at.

    Returns the PROJECT config path, which is what the command takes; use
    ``_settings_of`` for the file it writes into. Two files rather than one
    since R13: `experiment_name` is a run_stress_test setting, so it lives in
    that workflow's own file and the project config only points at it.

    project_dir must be under tmp_path. Since R9 P4 the command RESERVES the
    name by creating experiments/<id>/, so a repo-relative project_dir here
    would write real directories into the working tree on every test run --
    it resurrected `examples/`, retired at R7, before this was caught. The
    basename still slugifies to `gabon`, which is what these cases are about.
    """
    project_dir = tmp_path / "Gabon"
    project_dir.mkdir(exist_ok=True)
    # An empty settings file is written EMPTY, not as `{}`: that is the shape a
    # real one has, and a flow-style `{}` is a file no line-wise editor can
    # append to (the command refuses it, correctly, which is not what these
    # cases are about).
    _settings_of(tmp_path).write_text(
        yaml.safe_dump({"experiment_name": experiment_name})
        if experiment_name is not None
        else "",
        encoding="utf-8",
    )
    doc = {
        "project": {"project_dir": str(project_dir).replace("\\", "/")},
        "workflows": {
            "run_stress_test": {
                "enabled": True,
                "config_path": _settings_of(tmp_path).name,
            }
        },
    }
    p = tmp_path / "cfg.yml"
    p.write_text(yaml.safe_dump(doc), encoding="utf-8")
    return p


def _settings_of(tmp_path):
    """The run_stress_test settings file `_cfg` writes beside the project config."""
    return tmp_path / "cfg_run_stress_test.yml"


def test_cli_writes_when_absent(tmp_path):
    cfg = _cfg(tmp_path)
    res = _run(cfg)
    assert res.returncode == 0, res.stderr
    settings = yaml.safe_load(_settings_of(tmp_path).read_text(encoding="utf-8"))
    assert settings["experiment_name"] == "gabon_20260728"


def test_cli_refuses_to_overwrite(tmp_path):
    """The experiment name is the directory every wf3 artifact hangs off;
    silently changing it would strand a completed experiment's outputs.

    The refusal reads the key from the SETTINGS file. Reading it from the
    project config, where the key no longer is, would make `existing` always
    None and the refusal never fire -- in the one command whose whole contract
    is refusing to overwrite.
    """
    cfg = _cfg(tmp_path, experiment_name="already_here")
    before = _settings_of(tmp_path).read_text(encoding="utf-8")
    res = _run(cfg)
    assert res.returncode != 0
    assert "already_here" in res.stderr
    assert _settings_of(tmp_path).read_text(encoding="utf-8") == before, (
        "settings must be untouched"
    )


def test_cli_dry_run_leaves_the_config_alone(tmp_path):
    cfg = _cfg(tmp_path)
    before = cfg.read_text(encoding="utf-8")
    res = _run(cfg, "--dry-run")
    assert res.returncode == 0, res.stderr
    assert res.stdout.strip() == "gabon_20260728"
    assert cfg.read_text(encoding="utf-8") == before


def test_cli_preserves_other_config_content(tmp_path):
    """Round-tripping the YAML must not drop or reorder unrelated keys."""
    cfg = _cfg(tmp_path)
    settings_path = _settings_of(tmp_path)
    settings_path.write_text(
        yaml.safe_dump({"realizations_num": 4}, sort_keys=False), encoding="utf-8"
    )
    project_before = cfg.read_text(encoding="utf-8")

    assert _run(cfg).returncode == 0
    out = yaml.safe_load(settings_path.read_text(encoding="utf-8"))
    assert out["realizations_num"] == 4
    assert out["experiment_name"] == "gabon_20260728"
    # The project config is not rewritten at all -- the command only ever reads
    # it, to find out which settings file to edit.
    assert cfg.read_text(encoding="utf-8") == project_before


def test_cli_dry_run_reports_even_when_a_value_is_set(tmp_path):
    """The point of inspecting first is to SEE what would be proposed; a
    dry-run that only says "refusing" tells you nothing you did not know."""
    cfg = _cfg(tmp_path, experiment_name="already_here")
    before = cfg.read_text(encoding="utf-8")
    res = _run(cfg, "--dry-run")
    assert res.returncode == 0, res.stderr
    assert res.stdout.strip() == "gabon_20260728"
    assert cfg.read_text(encoding="utf-8") == before


def test_cli_refusal_names_what_it_would_have_suggested(tmp_path):
    cfg = _cfg(tmp_path, experiment_name="already_here")
    res = _run(cfg)
    assert res.returncode != 0
    assert "already_here" in res.stderr and "gabon_20260728" in res.stderr


# --- the template must leave the key for this command to fill ------------------


def test_the_template_config_does_not_hardcode_an_experiment_name():
    """The template shipped ``experiment_name: experiment`` while this command
    refuses to overwrite any existing value — so every project copied from it
    landed in the same ``experiments/experiment/`` and the command that exists
    to name the directory could never run. The key must start out ABSENT."""
    template = load_composed_config(
        SNAKEDIR / "config/templates/snake_config.template.yml"
    )
    section = template["workflows"]["run_stress_test"]
    assert "experiment_name" not in section, (
        "snake_config.template.yml must not set experiment_name: a copied "
        "template would inherit the placeholder, and "
        "suggest_experiment_name.py refuses to overwrite an existing value"
    )


def test_the_test_fixtures_deliberately_KEEP_a_fixed_name():
    """The gate needs a fixed experiments/<name>/ path, so the seed configs
    keep theirs. Only the user-facing template drops the key."""
    # Both seeds now sit beside the projects they write into, under test_case/.
    for rel in (
        "test_case/snake_config_baseline.yml",
        "test_case/snake_config_wf2_fast.yml",
    ):
        doc = load_composed_config(SNAKEDIR / rel)
        assert doc["workflows"]["run_stress_test"]["experiment_name"]


# --- the write must not destroy the config it edits ----------------------------


def _annotated_cfg(tmp_path, body):
    """A project config plus its run_stress_test settings file, written as TEXT.

    ``body`` is the SETTINGS file's content, at column zero -- that file's top
    level is the workflow's own keys, which is where ``experiment_name`` now
    lives. Returns ``(project_config, settings_file)``: the command takes the
    first and edits the second.

    Text, not ``safe_dump``, because what these tests check is that the command
    does not destroy the layout and comments of the file it edits.
    """
    project_dir = tmp_path / "Gabon"
    project_dir.mkdir(exist_ok=True)
    settings = tmp_path / "cfg_run_stress_test.yml"
    settings.write_text(body, encoding="utf-8")
    p = tmp_path / "cfg.yml"
    p.write_text(
        "# top-of-file banner\n"
        "project:\n"
        "  project_dir: "
        + str(project_dir).replace("\\", "/")
        + "  # where output goes\n"
        "\n"
        "workflows:\n"
        "  run_stress_test:\n"
        "    enabled: true\n"
        "    config_path: cfg_run_stress_test.yml\n",
        encoding="utf-8",
    )
    return p, settings


#: A settings file with no `experiment_name`, which is the state a fresh project
#: is in: the shipped template leaves the key commented out for this command.
CE_BLOCK = (
    "realizations_num: 2  # trailing comment\nstress_test:\n  temp:\n    step_num: 1\n"
)


def test_cli_preserves_every_comment_in_the_config(tmp_path):
    """yaml.safe_dump discards comments. The shipped template carries ~110 of
    them and this command is the first thing a new user runs against their
    copy, so a dump would delete the annotations they were just handed."""
    cfg, settings = _annotated_cfg(tmp_path, CE_BLOCK)
    before = settings.read_text(encoding="utf-8")
    project_before = cfg.read_text(encoding="utf-8")
    assert _run(cfg).returncode == 0
    after = settings.read_text(encoding="utf-8")
    assert "# trailing comment" in after
    # Exactly one line added to the settings file, everything else identical.
    added = [ln for ln in after.splitlines() if ln not in before.splitlines()]
    assert added == ["experiment_name: gabon_20260728"]
    # And the PROJECT file is untouched -- the key does not live there any more.
    assert cfg.read_text(encoding="utf-8") == project_before


def test_cli_fills_a_bare_key_in_place_keeping_its_comment(tmp_path):
    """`experiment_name:` with no value parses to None, which this command
    treats as unset (its refusal test is `is not None`)."""
    cfg, settings = _annotated_cfg(
        tmp_path,
        "experiment_name:   # fill me in\nrealizations_num: 2\n",
    )
    assert _run(cfg).returncode == 0
    after = settings.read_text(encoding="utf-8")
    assert "experiment_name: gabon_20260728  # fill me in" in after
    assert after.count("experiment_name") == 1, "must fill in place, not duplicate"


def test_an_absent_key_is_appended_without_disturbing_what_documents_it(tmp_path):
    """An absent key is appended at the end of the settings file.

    It used to be anchored below a comment run that named it, because the key
    was buried inside a nested block where placement mattered. At the top level
    of a file holding nothing but this workflow's settings there is no block to
    land inside, so the anchoring machinery retires with the nesting -- and what
    still matters is that nothing already in the file moves.
    """
    body = (
        "# experiment_name is left unset on purpose; run the command\n"
        "realizations_num: 2\n"
    )
    cfg, settings = _annotated_cfg(tmp_path, body)
    assert _run(cfg).returncode == 0
    after = settings.read_text(encoding="utf-8")
    assert after.startswith(body)
    assert after.splitlines()[-1] == "experiment_name: gabon_20260728"


def test_cli_leaves_unrelated_structure_intact(tmp_path):
    """The reload check is the guarantee; this pins it end to end."""
    cfg, settings = _annotated_cfg(tmp_path, CE_BLOCK)
    before = yaml.safe_load(settings.read_text(encoding="utf-8"))
    assert _run(cfg).returncode == 0
    after = yaml.safe_load(settings.read_text(encoding="utf-8"))
    before["experiment_name"] = "gabon_20260728"
    assert after == before


def test_a_config_with_no_settings_file_reserves_nothing(tmp_path):
    """Failing after the reservation would strand an experiments/<id>/ for a
    config the command then could not write to anyway.

    The unwritable case changed shape with the layout: the command now resolves
    a settings file before it can edit anything, so a project config naming none
    is the state that has to fail before reserving.
    """
    project_dir = tmp_path / "Gabon"
    project_dir.mkdir()
    cfg = tmp_path / "cfg.yml"
    cfg.write_text(
        "project:\n"
        "  project_dir: " + str(project_dir).replace("\\", "/") + "\n"
        "workflows:\n"
        "  run_stress_test:\n"
        "    enabled: true\n",
        encoding="utf-8",
    )
    before = cfg.read_text(encoding="utf-8")

    res = _run(cfg)
    assert res.returncode == 2
    assert "config_path" in res.stderr and "nothing has been reserved" in res.stderr
    assert cfg.read_text(encoding="utf-8") == before
    assert not (project_dir / "experiments").exists(), "must reserve nothing"


def test_a_dangling_config_path_reserves_nothing(tmp_path):
    """A pointer at a file that is not there fails the same way, and as early."""
    cfg, settings = _annotated_cfg(tmp_path, CE_BLOCK)
    settings.unlink()
    res = _run(cfg)
    assert res.returncode == 2
    assert "does not exist" in res.stderr
    assert not (tmp_path / "Gabon" / "experiments").exists()


def test_the_shipped_template_is_editable_by_this_command(tmp_path):
    """The template is the file this command is documented against; a layout
    it cannot edit would break the one path a new user is told to take.

    The whole SET is copied, because that is what a user copies: the project
    file plus the per-workflow files it points at.
    """
    import shutil

    src = SNAKEDIR / "config/templates/snake_config.template.yml"
    cfg = tmp_path / "snake_config.template.yml"
    shutil.copy(src, cfg)
    for sibling in (SNAKEDIR / "config/templates").glob("snake_config.*.template.yml"):
        shutil.copy(sibling, tmp_path / sibling.name)
    settings = tmp_path / "snake_config.run_stress_test.template.yml"

    doc = yaml.safe_load(cfg.read_text(encoding="utf-8"))
    project_dir = tmp_path / "Gabon"
    project_dir.mkdir()
    cfg.write_text(
        cfg.read_text(encoding="utf-8").replace(
            doc["project"]["project_dir"], str(project_dir).replace("\\", "/"), 1
        ),
        encoding="utf-8",
    )
    n_comments_before = settings.read_text(encoding="utf-8").count("#")

    res = _run(cfg)
    assert res.returncode == 0, res.stderr
    after = settings.read_text(encoding="utf-8")
    assert after.count("#") == n_comments_before
    assert yaml.safe_load(after)["experiment_name"] == "gabon_20260728"


def test_an_empty_settings_file_gets_the_key(tmp_path):
    """A workflow whose settings file is empty still gets a name written.

    The `yaml.safe_dump` this replaced created absent structure via
    `setdefault`, and dropping that would break configs the command accepted.
    """
    cfg, settings = _annotated_cfg(tmp_path, "")
    assert _run(cfg).returncode == 0
    assert yaml.safe_load(settings.read_text(encoding="utf-8")) == {
        "experiment_name": "gabon_20260728"
    }
