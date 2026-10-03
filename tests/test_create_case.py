"""Case scaffolding checks using isolated, representative case repositories."""

from datetime import datetime
from pathlib import Path

import pytest
import yaml

from scripts.create_case import main


@pytest.fixture
def cases(tmp_path: Path) -> Path:
    template = tmp_path / "templates" / "example-basin"
    (template / "data").mkdir(parents=True)
    (tmp_path / "applications").mkdir()
    (template / "project_config.yml").write_text(
        "# Keep scientific comments\nschema_version: 2\n"
        "project:\n  project_dir: old-output\n  catalog: config/catalogs/data.yml\n"
        "basin:\n  region: \"{'subbasin': [1, 2], 'uparea': 100}\"\n"
        "  output_locations: old-outlet\n  resolution: 0.00833\n"
        "climate:\n  selected: era5\n"
        "workflows:\n  analyze_climate:\n    enabled: true\n"
        "  build_model:\n    enabled: false\n"
        "    config_path: project_config_build_model.yml\n",
        encoding="utf-8",
    )
    (template / "project_config_build_model.yml").write_text(
        "observations:\n  river discharge: null\n", encoding="utf-8"
    )
    (template / "data" / "output_locations.csv").write_text(
        "station_name,x,y\noutlet,1,2\n", encoding="utf-8"
    )
    (template / "README.md").write_text("Old example\n", encoding="utf-8")
    (template / "notes.md").write_text("Old success\n", encoding="utf-8")
    (tmp_path / "cst-applications.md").write_bytes(
        b"Inventory\r\n\r\n"
        b"| application | project | date-created | cst-version | purpose |\r\n"
        b"|---|---|---|---|---|\r\n"
        b"| [old](applications/old/notes.md) | | 2020-01-01 | | Old |\r\n"
    )
    return tmp_path


def args(cases: Path) -> list[str]:
    return [
        "new-basin",
        "--cases-root",
        str(cases),
        "--longitude",
        "12.5",
        "--latitude",
        "-3",
        "--purpose",
        "Test | basin",
    ]


@pytest.mark.parametrize("dry_run", [False, True])
def test_create_preserves_template_and_leaves_inventory(
    cases: Path, dry_run: bool
) -> None:
    before = (cases / "cst-applications.md").read_bytes()
    assert main(args(cases) + (["--dry-run"] if dry_run else [])) == 0
    application = cases / "applications" / "new-basin"
    assert not (cases / "runs").exists()
    if dry_run:
        assert not application.exists()
        assert (cases / "cst-applications.md").read_bytes() == before
        return
    config_text = (application / "project_config.yml").read_text()
    config = yaml.safe_load(config_text)
    assert (
        config["project"]["project_dir"] == (cases / "runs/new-basin/active").as_posix()
    )
    assert (
        config["basin"]["output_locations"]
        == (application / "data/output_locations.csv").as_posix()
    )
    assert config["basin"]["region"] == "{'subbasin': [12.5, -3.0], 'uparea': 100}"
    assert config["climate"]["selected"] == "era5"
    assert config["workflows"]["build_model"]["enabled"] is False
    assert "# Keep scientific comments" in config_text
    assert "outlet,12.5,-3.0" in (application / "data/output_locations.csv").read_text()
    assert "configured; not run" in (application / "notes.md").read_text()
    assert not (application / "README.md").exists()
    instructions = (application / "INSTRUCTIONS.md").read_text(encoding="utf-8")
    created = next(line for line in instructions.splitlines() if "| Created |" in line)
    datetime.strptime(created.split("|")[2].strip(), "%Y-%m-%d %H:%M:%S")
    assert "| Status |" not in instructions
    assert instructions.rsplit("\n## ", 1)[1].startswith("Output folder and results")
    assert "Purpose: Test | basin" in (application / "notes.md").read_text()
    # Cases are registered by hand only after every workflow completes.
    assert (cases / "cst-applications.md").read_bytes() == before
    assert main(args(cases)) == 2


@pytest.mark.parametrize(
    "option,value",
    [
        ("slug", "../bad"),
        ("slug", "con"),
        ("--latitude", "nan"),
        ("--longitude", "181"),
        ("--purpose", " "),
    ],
)
def test_invalid_arguments_write_nothing(cases: Path, option: str, value: str) -> None:
    command = args(cases)
    command[0 if option == "slug" else command.index(option) + 1] = value
    before = (cases / "cst-applications.md").read_bytes()
    assert main(command) == 2
    assert not (cases / "applications/new-basin").exists()
    assert (cases / "cst-applications.md").read_bytes() == before


@pytest.mark.parametrize("fault", ["config", "observations", "write"])
def test_preflight_failure_leaves_no_partial_case(
    cases: Path, fault: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    template = cases / "templates/example-basin"
    if fault == "config":
        (template / "project_config.yml").write_text("project: [")
    elif fault == "observations":
        (template / "project_config_build_model.yml").write_text(
            "observations:\n  river discharge: /external/observations.csv\n"
        )
    else:

        def fail_move(*args: object) -> None:
            raise PermissionError("Case write rejected")

        monkeypatch.setattr("scripts.create_case.shutil.move", fail_move)
    before = (cases / "cst-applications.md").read_bytes()
    assert main(args(cases)) == 2
    assert not (cases / "applications/new-basin").exists()
    assert (cases / "cst-applications.md").read_bytes() == before
