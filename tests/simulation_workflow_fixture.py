"""Parse successor rule declarations with collection validation isolated."""

import uuid
from pathlib import Path

import yaml


def parse_simulation_workflow(tmp_path, monkeypatch, *, config=None):
    """Supply an already-validated collection to test scheduling declarations.

    Physical artifact validation is exercised by the collection/response suites;
    this fixture deliberately substitutes only that external boundary.
    """
    import snakemake.api as api

    from blueearth_cst.experiment import simulation_runner
    from blueearth_cst.experiment.content_identity import atomic_record

    repo = Path(__file__).resolve().parents[1]
    project = tmp_path / "project"
    project.mkdir(exist_ok=True)
    collection = tmp_path / "collection"
    collection.mkdir(exist_ok=True)
    atomic_record(
        collection / "collection_intent.json",
        {"scenario_spec": {"simulation_window": {"start": 2046, "end": 2054}}},
    )
    selection = {
        "manifest_path": (collection / "collection.json").as_posix(),
        "resolution_mode": "explicit-manifest",
    }
    manifest = {"forcing": [{"run_id": run} for run in ("01", "02", "03")]}
    monkeypatch.setattr(
        simulation_runner,
        "resolve_selected_collection",
        lambda *args: (selection, manifest),
    )
    monkeypatch.setenv("CST_SIMULATION_OPERATION", "simulate-and-metrics")
    monkeypatch.setenv("CST_SIMULATION_INVOCATION_ID", uuid.uuid4().hex)
    settings = tmp_path / "simulation.yml"
    settings.write_text(
        "experiment_name: fixture\noperation: simulate-and-metrics\n", encoding="utf-8"
    )
    document = config or {
        "schema_version": 2,
        "model": {"outvars": ["river discharge"]},
    }
    document["project"] = {"project_dir": project.as_posix()}
    document["workflows"] = {
        "simulate_system": {"enabled": True, "config_path": settings.name}
    }
    path = tmp_path / "project.yml"
    path.write_text(yaml.safe_dump(document), encoding="utf-8")
    with api.SnakemakeApi() as sa:
        wf_api = sa.workflow(
            resource_settings=api.ResourceSettings(cores=1),
            config_settings=api.ConfigSettings(configfiles=[path]),
            storage_settings=api.StorageSettings(),
            workflow_settings=api.WorkflowSettings(),
            snakefile=repo / "simulate_system.smk",
            workdir=repo,
        )
        workflow = wf_api._workflow
        workflow.include(workflow.main_snakefile, overwrite_default_target=True)
        return workflow
