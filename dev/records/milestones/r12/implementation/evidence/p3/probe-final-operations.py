"""Sequential GF30/GF32 checks against explicit, completed scratch artifacts.

Run only after the coordinator releases the project and repository Snakemake
lock. No identity is selected by directory scanning. --case selection requires
at least one explicitly named alternate ready manifest from the GF27 run.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
import subprocess
import sys
from contextlib import contextmanager
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parents[6]
sys.path.insert(0, str(REPO))


def require(condition, message):
    if not condition:
        raise ValueError(message)


def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def digest(path):
    with Path(path).open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def scratch(path):
    path = Path(path).resolve()
    require(path.is_relative_to(REPO / ".tmp"), f"outside scratch: {path}")
    return path


def inventory(roots):
    """Enumerate preservation coverage, never select an identity by recency."""
    return {
        str(path): {"sha256": digest(path), "mtime_ns": path.stat().st_mtime_ns}
        for root in roots
        for path in sorted(root.rglob("*"))
        if path.is_file()
    }


@contextmanager
def damaged_plan(path):
    """Corrupt only rebuildable scratch state; restore exact bytes and times."""
    from blueearth_cst.experiment.content_identity import canonical_json_bytes

    path = scratch(path)
    require(
        "scenario_plans" in path.parts or "metric_plans" in path.parts,
        "only scheduling plans may be perturbed",
    )
    original, stat = path.read_bytes(), path.stat()
    changed = json.loads(original)
    changed["plan_sha256"] = "0" * 64
    try:
        path.write_bytes(canonical_json_bytes(changed))
        yield
    finally:
        path.write_bytes(original)
        os.utime(path, ns=(stat.st_atime_ns, stat.st_mtime_ns))
        require(path.read_bytes() == original, "plan restoration failed")


@contextmanager
def absent_plan(path):
    """Temporarily remove one exact scheduling leaf, without touching its collection."""
    path = scratch(path)
    require("scenario_plans" in path.parts, "only scenario plans may be withheld")
    backup = path.with_name(path.name + ".gf32-backup")
    require(not backup.exists(), "prior restoration backup exists")
    path.rename(backup)
    try:
        yield
    finally:
        backup.replace(path)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--scenario-plan", type=Path, required=True)
    parser.add_argument("--metric-plan", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--other-manifest", type=Path, action="append", default=[])
    parser.add_argument("--source-inventory", type=Path, required=True)
    parser.add_argument("--work", type=Path, required=True)
    parser.add_argument("--interface", choices=["dedicated", "all"], required=True)
    parser.add_argument(
        "--case", choices=["reuse", "targets", "stale", "selection"], required=True
    )
    args = parser.parse_args()
    config = args.config.resolve()
    work = scratch(args.work)
    require(not work.exists(), "use a new work directory to preserve prior evidence")
    project = yaml.safe_load(config.read_text(encoding="utf-8"))
    root = scratch(project["project"]["project_dir"])
    simulation_file = (
        config.parent / project["workflows"]["simulate_system"]["config_path"]
    ).resolve()
    settings = yaml.safe_load(simulation_file.read_text(encoding="utf-8"))
    experiment = root / "experiments" / settings["experiment_name"]
    simulation = read(experiment / "config/simulation.json")
    manifest_path = scratch(args.manifest)
    manifest = read(manifest_path)
    metric = read(args.metric_plan)
    source = read(args.scenario_plan)
    require(simulation["response_inventory_sha256"] is not None, "responses incomplete")
    require(
        simulation["collection"]["collection_id"] == manifest["collection_id"],
        "wrong collection",
    )
    require(
        simulation["collection"]["collection_revision"]
        == manifest["collection_revision"],
        "wrong revision",
    )
    require(
        Path(simulation["collection"]["manifest_path"]).resolve() == manifest_path,
        "wrong manifest path",
    )
    require(
        Path(source["manifest_path"]).resolve() == manifest_path, "wrong scenario plan"
    )
    require(
        metric["request"]["simulation_id"] == simulation["simulation_id"],
        "wrong metric plan",
    )
    metric_root = Path(metric["targets"]["manifest"]).parent.resolve()
    require(metric_root.is_relative_to(experiment), "metric set outside experiment")
    require(
        read(metric["targets"]["manifest"])["metric_set_id"] == metric["metric_set_id"],
        "metric set missing or wrong",
    )
    for relative, expected in read(args.source_inventory)["files"].items():
        require(digest(REPO / relative) == expected, f"source drift: {relative}")
    roots = [
        manifest_path.parent,
        experiment / "config",
        experiment / "responses",
        experiment / "hydrology",
        metric_root.parent,
    ]
    before = inventory(roots)
    work.mkdir(parents=True)
    report = {
        "scope": "GF30/GF32 final-interface follow-up; not fresh GF30 or GF15",
        "interface": args.interface,
        "case": args.case,
        "config": str(config),
        "config_sha256": digest(config),
        "simulation_settings_sha256": digest(simulation_file),
        "source_inventory_sha256": digest(args.source_inventory),
        "probe_sha256": digest(Path(__file__)),
        "simulation_id": simulation["simulation_id"],
        "simulation_manifest_sha256": digest(experiment / "config/simulation.json"),
        "response_inventory_sha256": simulation["response_inventory_sha256"],
        "collection_id": manifest["collection_id"],
        "collection_revision": manifest["collection_revision"],
        "collection_manifest_sha256": digest(manifest_path),
        "metric_set_id": metric["metric_set_id"],
        "scenario_plan": str(args.scenario_plan.resolve()),
        "scenario_plan_sha256": digest(args.scenario_plan),
        "metric_plan": str(args.metric_plan.resolve()),
        "metric_plan_sha256": digest(args.metric_plan),
        "commands": [],
        "preserved_files": len(before),
        "status": "running",
        "retained_artifact_sha256": {
            path: record["sha256"] for path, record in before.items()
        },
    }

    def variant(name, *, metrics=False, explicit=None, missing_generation=False):
        document, workflow = copy.deepcopy(project), copy.deepcopy(settings)
        for key, stanza in document["workflows"].items():
            stanza["enabled"] = key == "simulate_system"
            if stanza.get("config_path"):
                stanza["config_path"] = str(
                    (config.parent / stanza["config_path"]).resolve()
                )
        workflow["operation"] = "metrics-only" if metrics else "simulate-and-metrics"
        workflow.pop("scenario_collection", None)
        if metrics:
            workflow["metrics"] = metric["request"]["tokens"]
        if explicit:
            workflow["scenario_collection"] = {"manifest_path": str(explicit)}
        if missing_generation:
            document["workflows"]["generate_scenarios"]["config_path"] = str(
                work / "absent-generation.yml"
            )
        wf_path, path = (
            work / f"{name}-simulation.yml",
            work / f"project_config_{name}.yml",
        )
        wf_path.write_text(yaml.safe_dump(workflow), encoding="utf-8")
        document["workflows"]["simulate_system"]["config_path"] = str(wf_path)
        path.write_text(yaml.safe_dump(document), encoding="utf-8")
        return path

    def run(label, cfg, target, *, force=False, expected_error=None):
        program = (
            "simulate_system.py"
            if args.interface == "dedicated"
            else "run_workflows.py"
        )
        target_flag = (
            "--target" if args.interface == "dedicated" else "--simulation-target"
        )
        command = [
            sys.executable,
            str(REPO / "scripts" / program),
            "--config",
            str(cfg),
            "--cores",
            "3",
            target_flag,
            str(target),
        ]
        if force:
            command += ["--", "--forceall"]
        log = work / f"{label}.log"
        with log.open("w", encoding="utf-8") as handle:
            result = subprocess.run(
                command, cwd=REPO, stdout=handle, stderr=subprocess.STDOUT, check=False
            )
        text = log.read_text(encoding="utf-8")
        item = {
            "label": label,
            "argv": command,
            "exit_code": result.returncode,
            "log": str(log),
            "log_sha256": digest(log),
            "config_sha256": digest(cfg),
        }
        invoked = yaml.safe_load(cfg.read_text(encoding="utf-8"))
        item["simulation_settings_sha256"] = digest(
            invoked["workflows"]["simulate_system"]["config_path"]
        )
        report["commands"].append(item)
        after = inventory(roots)
        require(
            {p: v["sha256"] for p, v in before.items()}
            == {p: v["sha256"] for p, v in after.items()},
            f"retained bytes changed: {label}",
        )
        item["mtime_only_changes"] = [p for p in before if before[p] != after[p]]
        if expected_error:
            require(
                result.returncode != 0 and expected_error in text,
                f"wrong refusal: {label}; see {log}",
            )
        else:
            require(result.returncode == 0, f"command failed: {label}; see {log}")

    try:
        routine = variant("routine")
        explicit = variant(
            "metrics", metrics=True, explicit=manifest_path, missing_generation=True
        )
        selected = metric["targets"][metric["request"]["tokens"][0]]
        if args.case == "reuse":
            run("simulation-reuse", routine, "all")
            run("simulation-force", routine, "all", force=True)
            run("metrics-reuse", explicit, "metrics")
            run("metrics-force", explicit, "metrics", force=True)
        elif args.case == "targets":
            run("valid-selected-file", explicit, selected)
            run(
                "forbidden-native-file",
                routine,
                experiment / "hydrology/wflow/output/run_01.csv",
                expected_error="UnsupportedOperationTarget",
            )
            run(
                "wrong-metric-set",
                explicit,
                experiment / "results/metric_sets" / ("0" * 64) / Path(selected).name,
                expected_error="UnsupportedOperationTarget",
            )
            run(
                "forbidden-metric-plan-repair",
                explicit,
                args.metric_plan.resolve(),
                expected_error="UnsupportedOperationTarget",
            )
        elif args.case == "stale":
            with absent_plan(args.scenario_plan):
                run(
                    "missing-source-plan-refusal",
                    routine,
                    "all",
                    expected_error="run snakemake all -s generate_scenarios.smk",
                )
            with damaged_plan(args.scenario_plan):
                run(
                    "stale-source-refusal",
                    routine,
                    "all",
                    expected_error="plan digest expected=",
                )
                run(
                    "forbidden-source-plan-repair",
                    routine,
                    args.scenario_plan.resolve(),
                    expected_error="UnsupportedOperationTarget",
                )
            with damaged_plan(args.metric_plan):
                run(
                    "stale-metric-refusal",
                    explicit,
                    "metrics",
                    expected_error="metric plan expected=",
                )
                run(
                    "forbidden-metric-plan-repair",
                    explicit,
                    args.metric_plan.resolve(),
                    expected_error="UnsupportedOperationTarget",
                )
        else:
            require(
                args.other_manifest, "selection needs explicit alternate manifest paths"
            )
            from blueearth_cst.experiment.simulation_runner import (
                resolve_selected_collection,
            )

            others = []
            for other in args.other_manifest:
                alternate = read(other)
                require(
                    alternate["collection_id"] != manifest["collection_id"],
                    "alternate is selected collection",
                )
                selection, _ = resolve_selected_collection(
                    variant(f"alternate-{len(others)}", explicit=other.resolve()), REPO
                )
                others.append(selection)
            selection, _ = resolve_selected_collection(routine, REPO)
            require(
                selection["collection_id"] == manifest["collection_id"],
                "routine selection drifted",
            )
            report["exact_default_selection"] = selection
            report["other_retained_collections"] = others
            run("default-among-several", routine, "all")
            run("explicit-retained-metrics", explicit, selected)
            mismatch = variant(
                "mismatch", metrics=True, explicit=args.other_manifest[0].resolve()
            )
            run(
                "explicit-mismatch", mismatch, "metrics", expected_error="collection_id"
            )
        report["status"] = "passed"
    except BaseException as exc:
        report.update(status="failed", error=f"{type(exc).__name__}: {exc}")
        raise
    finally:
        (work / "result.json").write_text(
            json.dumps(report, indent=2) + "\n", encoding="utf-8"
        )
    print(work / "result.json")


if __name__ == "__main__":
    main()
