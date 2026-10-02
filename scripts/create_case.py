"""Create an external case from its repository's example-basin template."""

from __future__ import annotations

import argparse
import ast
import csv
import html
import io
import json
import math
import os
import re
import shutil
import sys
import tempfile
from datetime import date, datetime
from pathlib import Path

import yaml


def _replace(text: str, keys: tuple[str, ...], value: object) -> str:
    """Replace one YAML scalar using parser offsets, preserving comments."""
    node = yaml.compose(text)
    for key in keys:
        if not isinstance(node, yaml.MappingNode):
            raise ValueError(f"Expected YAML mapping at {'.'.join(keys)}")
        matches = [child for name, child in node.value if name.value == key]
        if len(matches) != 1:
            raise ValueError(f"Expected exactly one YAML key: {'.'.join(keys)}")
        node = matches[0]
    if not isinstance(node, yaml.ScalarNode):
        raise ValueError(f"Expected scalar at {'.'.join(keys)}")
    replacement = json.dumps(value, ensure_ascii=False)
    return text[: node.start_mark.index] + replacement + text[node.end_mark.index :]


def _confined(path: Path, root: Path) -> Path:
    """Resolve a path and reject links leading outside the repository."""
    resolved = path.resolve()
    if not resolved.is_relative_to(root):
        raise ValueError(f"Path escapes cases root: {path}")
    return resolved


def _cell(text: str) -> str:
    """Escape user text for a single Markdown table cell."""
    return (
        html.escape(text).replace("|", "&#124;").replace("\n", " ").replace("\r", " ")
    )


def _prepare(args: argparse.Namespace) -> tuple[Path, Path, bytes, dict[Path, bytes]]:
    """Validate inputs and build all new file contents without filesystem writes."""
    slug = args.case_slug
    reserved = {"con", "prn", "aux", "nul"} | {
        f"{prefix}{n}" for prefix in ("com", "lpt") for n in range(1, 10)
    }
    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", slug) or slug in reserved:
        raise ValueError(
            "Case slug must be lowercase kebab-case and not a reserved filename"
        )
    for name, low, high in (("longitude", -180, 180), ("latitude", -90, 90)):
        number = getattr(args, name)
        if not math.isfinite(number) or not low <= number <= high:
            raise ValueError(f"{name} must be finite and between {low} and {high}")
    if not args.purpose.strip():
        raise ValueError("Purpose must be nonempty")
    root = Path(args.cases_root)
    if not root.is_absolute() or not root.is_dir():
        raise ValueError("--cases-root must name an existing absolute directory")
    root = root.resolve()
    for relative in ("applications", "runs", f"runs/{slug}", f"runs/{slug}/active"):
        candidate = root / relative
        if candidate.is_symlink() or candidate.is_junction():
            raise ValueError(
                f"Destination must not be a symbolic link or junction: {candidate}"
            )
    template = _confined(root / "templates/example-basin", root)
    applications = _confined(root / "applications", root)
    if not applications.is_dir() or not template.is_dir():
        raise ValueError(
            "Cases root requires applications/ and templates/example-basin/"
        )
    destination = applications / slug
    if destination.exists() or destination.is_symlink():
        raise ValueError(f"Application already exists: {destination}")
    _confined(destination, root)
    outputs = _confined(root / "runs" / slug / "active", root)
    inventory = root / "cst-applications.md"
    if inventory.is_symlink() or inventory.is_junction():
        raise ValueError("Inventory must not be a symbolic link")
    original = inventory.read_bytes()
    inventory_text = original.decode("utf-8")
    header = "| application | country | project | date-created | date-completed | cst-version | purpose | status |"
    lines = inventory_text.splitlines()
    if lines.count(header) != 1:
        raise ValueError(
            "Inventory must contain the supported eight-column applications table"
        )
    index = lines.index(header)
    if index + 1 >= len(lines) or not re.fullmatch(
        r"\|(?:\s*:?-+:?\s*\|){8}", lines[index + 1]
    ):
        raise ValueError("Inventory table separator is malformed")
    if any(line.strip() for line in lines[index + 2 :] if not line.startswith("|")):
        raise ValueError("Inventory applications table must be the final content")
    for line in lines[index + 2 :]:
        if line and len(line.split("|")) != 10:
            raise ValueError("Inventory row must have eight columns")
    if re.search(rf"applications/{re.escape(slug)}(?:/|\))", inventory_text):
        raise ValueError(f"Application already registered: {slug}")
    files: dict[Path, bytes] = {}
    for source in template.rglob("*"):
        if source.is_symlink() or source.is_junction():
            raise ValueError(
                f"Template must not contain symbolic links or junctions: {source}"
            )
        if source.is_file():
            files[source.relative_to(template)] = source.read_bytes()
    config_path = Path("project_config.yml")
    text = files[config_path].decode("utf-8")
    config = yaml.safe_load(text)
    if not isinstance(config, dict) or config.get("schema_version") != 2:
        raise ValueError("Template requires project config schema_version: 2")
    workflows = config.get("workflows")
    if not isinstance(workflows, dict) or not workflows:
        raise ValueError("Template requires workflow stanzas")
    for name, stanza in workflows.items():
        if not isinstance(stanza, dict) or stanza.get("enabled") is not (
            name == "analyze_climate"
        ):
            raise ValueError("Template must enable analyze_climate alone")
        if stanza.get("config_path"):
            if not isinstance(stanza["config_path"], str):
                raise ValueError(f"Workflow config_path must be a string: {name}")
            target = Path(stanza["config_path"])
            if target.is_absolute() or ".." in target.parts or target not in files:
                raise ValueError(f"Workflow config must be inside template: {target}")
    text = _replace(text, ("project", "project_dir"), outputs.as_posix())
    text = _replace(
        text,
        ("basin", "output_locations"),
        (destination / "data/output_locations.csv").as_posix(),
    )
    region = config["basin"]["region"]
    if isinstance(region, str):
        try:
            region = ast.literal_eval(region)
        except (SyntaxError, ValueError) as error:
            raise ValueError(
                "Template basin.region must define a subbasin mapping"
            ) from error
    if not isinstance(region, dict) or "subbasin" not in region:
        raise ValueError("Template basin.region must define a subbasin mapping")
    region = {**region, "subbasin": [args.longitude, args.latitude]}
    text = _replace(text, ("basin", "region"), str(region))
    if args.catalog is not None:
        if not args.catalog.strip():
            raise ValueError("Catalog must be nonempty")
        text = _replace(text, ("project", "catalog"), args.catalog)
    expected = yaml.safe_load(files[config_path])
    expected["project"]["project_dir"] = outputs.as_posix()
    expected["basin"]["output_locations"] = (
        destination / "data/output_locations.csv"
    ).as_posix()
    expected["basin"]["region"] = str(region)
    if args.catalog is not None:
        expected["project"]["catalog"] = args.catalog
    if yaml.safe_load(text) != expected:
        raise ValueError("Template aliases affect fields outside the case identity")
    files[config_path] = text.encode("utf-8")
    for relative, content in list(files.items()):
        if relative.suffix not in {".yml", ".yaml"}:
            continue
        yaml_text = content.decode("utf-8")
        parsed = yaml.safe_load(yaml_text)
        if not isinstance(parsed, dict):
            raise ValueError(f"Template YAML must be a mapping: {relative}")
        observations = parsed.get("observations", {})
        if not isinstance(observations, dict):
            raise ValueError(f"observations must be a mapping: {relative}")
        for variable, raw in observations.items():
            if raw is None:
                continue
            if not isinstance(raw, str):
                raise ValueError(f"Observation path must be a string: {variable}")
            source = Path(raw)
            source = source if source.is_absolute() else template / source
            source = source.resolve()
            if not source.is_relative_to(template) or not source.is_file():
                raise ValueError(
                    f"Observation must be an existing template sidecar: {raw}"
                )
            sidecar = source.relative_to(template)
            yaml_text = _replace(
                yaml_text,
                ("observations", variable),
                (destination / sidecar).as_posix(),
            )
        files[relative] = yaml_text.encode("utf-8")
    outlet = Path("data/output_locations.csv")
    rows = list(csv.reader(io.StringIO(files[outlet].decode("utf-8"))))
    if len(rows) != 2 or rows[0] != ["station_name", "x", "y"] or len(rows[1]) != 3:
        raise ValueError(
            "Template outlet CSV must have station_name,x,y and one outlet row"
        )
    stream = io.StringIO(newline="")
    writer = csv.writer(stream, lineterminator="\n")
    writer.writerow(rows[0])
    writer.writerow(["outlet", args.longitude, args.latitude])
    files[outlet] = stream.getvalue().encode("utf-8")
    files.pop(Path("README.md"), None)
    files[Path("INSTRUCTIONS.md")] = (
        f"# {slug}: run instructions\n\n"
        "Use this guide to review your settings, run the assessment, and find its results.\n\n"
        "| Field | Value |\n|---|---|\n"
        f"| Project | {slug} |\n| Created | {datetime.now():%Y-%m-%d %H:%M:%S} |\n"
        f"| Coordinates (longitude, latitude) | {args.longitude}, {args.latitude} |\n"
        "\n"
        "## Setup\n\nOpen PowerShell in the toolbox root and set these paths:\n\n"
        f'```powershell\n$config = "{destination.as_posix()}/project_config.yml"\n'
        f'$projectDir = "{outputs.as_posix()}"\n```\n\n'
        "Review `project_config.yml` and the workflow configuration files beside it. "
        "Check that the data catalog covers your basin, choose the climate forcing, "
        "and review the inherited upstream-area threshold (`basin.region`'s `uparea`, in km²).\n\n"
        "## Run enabled workflows\n\n"
        "Edit `workflows.*.enabled` in the project config. Run WF0 alone; disable it "
        "before enabling downstream stages.\n\n"
        "```powershell\npixi run python scripts/run_workflows.py --config $config --project-dir $projectDir --cores 3\n```\n\n"
        "Append `-- --dry-run` to preview.\n\n"
        "## Individual workflows\n\n"
        "Enable the workflow in `project_config.yml` before running its command. "
        "WF4 requires a built model and a generated scenario collection. "
        "GCM projections provide context for the stress test; they do not drive scenario generation.\n\n"
        "```powershell\n"
        "# WF0: Analyze historical climate\n"
        "pixi run python scripts/run_workflow.py analyze_climate --config $config --project-dir $projectDir --cores 3\n\n"
        "# WF1: Build a hydrological model\n"
        "pixi run python scripts/run_workflow.py build_model --config $config --project-dir $projectDir --cores 3\n\n"
        "# WF2: Extract and analyze GCM projections\n"
        "pixi run python scripts/run_workflow.py analyze_projections --config $config --project-dir $projectDir --cores 3 --keep-going\n\n"
        "# WF3: Generate future climate scenarios\n"
        "pixi run python scripts/run_workflow.py generate_scenarios --config $config --project-dir $projectDir --cores 3\n\n"
        "# WF4: Stress test the system using climate scenarios\n"
        "pixi run python scripts/run_workflow.py simulate_system --config $config --project-dir $projectDir --target all --cores 3\n```\n\n"
        "## Snakemake DAG preview\n\n"
        "```powershell\npixi run snakemake all -c 3 -s build_model.smk --configfile $config --dry-run\n```\n\n"
        "Use `analyze_climate.smk` or `analyze_projections.smk` to preview WF0 or WF2. "
        "Record your configuration choices, commands, and checks in [notes.md](notes.md).\n\n"
        f"## Output folder and results\n\nResults are written to `{outputs.as_posix()}` "
        "as you run the workflows. Configuration files remain in this application folder.\n\n"
        "| Folder within the output directory | What you will find |\n|---|---|\n"
        "| `config/runs/` | Configuration snapshots and workflow attempt records |\n"
        "| `data/spatial/` | Basin geometry, output locations, and maps |\n"
        "| `data/climate/historical/` | Historical climate series, analysis plots, and source comparisons (WF0) |\n"
        "| `models/hydrology/wflow/` | Hydrological model, historical run, and evaluation (WF1) |\n"
        "| `data/climate/projections/` | GCM change-factor tables under `summary/` and figures under `plots/` (WF2) |\n"
        "| `scenarios/<collection_id>/` | Generated climate series under `series/`, scenario and perturbation lookup tables (WF3) |\n"
        "| `experiments/<name>/hydrology/wflow/output/` | Retained model responses to the climate scenarios (WF4) |\n"
        "| `experiments/<name>/results/metric_sets/<id>/` | Indicator tables and `metric_run_lookup.csv` (WF4) |\n"
        "| `logs/` | Workflow messages and failure details |\n"
        "| `benchmarks/` | Step timings and resource use |\n\n"
        "Collection inventories are in `scenarios/_engine/collections/<collection_id>/collection.json`. "
        "Indicator definitions and source records are in "
        "`experiments/<name>/_engine/metric_sets/<id>/metrics.json`. "
        "Check these records before treating results from an interrupted run as complete.\n"
    ).encode("utf-8")
    files[Path("notes.md")] = (
        f"# {slug} — run notes\n\nStatus: configured; not run.\n\n"
        "No run history or validation is inherited from the template.\n\n"
        "## Retained run record\n\n"
        "- Date:\n- Cases revision and dirty state:\n"
        "- Toolbox revision and dirty state:\n- Configuration choices:\n"
        "- Command:\n- Outcome:\n- Checks actually performed:\n"
        "- Evidence location:\n- Follow-up:\n"
    ).encode("utf-8")
    return destination, inventory, original, files


def main(argv: list[str] | None = None) -> int:
    """Validate and create a case; return 2 for actionable input or I/O failures."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("case_slug")
    parser.add_argument("--cases-root", required=True)
    for name in ("longitude", "latitude"):
        parser.add_argument(f"--{name}", required=True, type=float)
    parser.add_argument("--purpose", required=True)
    parser.add_argument("--catalog", help="Toolbox-relative or absolute data catalog")
    parser.add_argument(
        "--dry-run", action="store_true", help="Validate and preview without writing"
    )
    args = parser.parse_args(argv)
    try:
        destination, inventory, original, files = _prepare(args)
        if not args.dry_run:
            newline = b"\r\n" if b"\r\n" in original else b"\n"
            row = (
                f"| [{args.case_slug}](applications/{args.case_slug}/notes.md) | "
                f"| | {date.today().isoformat()} | | | "
                f"{_cell(args.purpose.strip())} | configured; not run |"
            ).encode("utf-8")
            updated = (
                original
                + (b"" if original.endswith(b"\n") else newline)
                + row
                + newline
            )
            with tempfile.TemporaryDirectory(
                prefix=".create-case-", dir=destination.parent
            ) as scratch:
                stage = Path(scratch) / "case"
                stage.mkdir()
                for relative, content in files.items():
                    target = stage / relative
                    target.parent.mkdir(parents=True, exist_ok=True)
                    target.write_bytes(content)
                if inventory.read_bytes() != original:
                    raise ValueError("Inventory changed during preparation; retry")
                # mkdir claims the destination without overwriting an existing case.
                destination.mkdir()
                try:
                    for child in stage.iterdir():
                        shutil.move(str(child), destination / child.name)
                    staged_inventory = Path(scratch) / "inventory.md"
                    staged_inventory.write_bytes(updated)
                    os.replace(staged_inventory, inventory)
                except OSError:
                    shutil.rmtree(destination)
                    raise
        verb = "Would create" if args.dry_run else "Created"
        print(f"{verb} {destination}; inventory: {inventory}")
        print(
            f"Outputs: {Path(args.cases_root).resolve() / 'runs' / args.case_slug / 'active'}"
        )
        print("Next: review settings and preview WF0 from the toolbox root:")
        print(
            f'pixi run python scripts/run_workflows.py --config "{destination.as_posix()}/project_config.yml" --cores 3 -- --dry-run'
        )
    except (OSError, ValueError, KeyError, yaml.YAMLError) as error:
        print(f"Cannot create case: {error}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
