"""Wrap existing weathergenr operations behind the stochastic provider seam.

The transitional carrier keeps native filenames. Only this binding translates
provider payload into R arguments; it never changes the R numerical operations.
"""

from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from subprocess import CalledProcessError

from blueearth_cst.experiment.forcing_descriptor import (
    ClimateArtifact,
    ForcingDescriptor,
    UnitInterpretation,
    describe_forcing,
)
from blueearth_cst.experiment.scenario_rows import (
    ScenarioRow,
    enumerate_stochastic,
)
from blueearth_cst.shared.snake_utils import log_row, plural


@dataclass(frozen=True)
class SourceInputs:
    """Current R generation inputs, including its explicit filename widths."""

    historical_climate: Path
    weathergen_config: Path
    basin_cells: Path
    output_dir: Path
    rlz_width: int
    st_width: int


def enumerate_scenarios(
    generation_spec: Mapping, *, unit_id_capacity: int
) -> tuple[ScenarioRow, ...]:
    """Enumerate the production stochastic binding without source I/O."""
    return enumerate_stochastic(generation_spec, unit_id_capacity=unit_id_capacity)


def _execute(command: list[str], log_path: Path) -> None:
    """Preserve the existing live log and child exit-status behavior."""
    from blueearth_cst.shared.snake_utils import run_and_tee

    result = run_and_tee(command, log_path)
    if result:
        raise CalledProcessError(result, command)


def legacy_member_name(row: ScenarioRow, *, st_width: int) -> str:
    """Address a row in the unchanged P1 output tree; never parse a path."""
    payload = dict(row.payload)
    return f"rlz_{payload['rlz']}_st_{payload['st_id'] or f'{0:0{st_width}d}'}"


def generate_roots(
    root_rows: Sequence[ScenarioRow],
    source_inputs: SourceInputs,
    *,
    log_path: Path,
    execute: Callable[[list[str], Path], None] = _execute,
) -> tuple[ClimateArtifact, ...]:
    """Generate the declared roots with exactly the predecessor R arguments."""
    if not root_rows:
        raise ValueError("generate_roots needs nonempty root rows")
    expected_draws = [
        f"{i:0{source_inputs.rlz_width}d}" for i in range(1, len(root_rows) + 1)
    ]
    if [dict(row.payload).get("rlz") for row in root_rows] != expected_draws:
        raise ValueError("root rows must cover the configured realization order")
    if any(
        row.scenario_type != "stochastic"
        or row.derived_from
        or dict(row.payload).get("st_id") != ""
        for row in root_rows
    ):
        raise ValueError("generate_roots accepts stochastic roots only")
    command = [
        "Rscript",
        "--vanilla",
        "blueearth_cst/weathergen/generate_weather.R",
        str(source_inputs.historical_climate),
        str(source_inputs.weathergen_config),
        str(source_inputs.rlz_width),
        str(source_inputs.st_width),
        str(source_inputs.basin_cells),
    ]
    execute(command, log_path)
    artifacts = tuple(
        ClimateArtifact(
            row.run_id,
            source_inputs.output_dir
            / f"{legacy_member_name(row, st_width=source_inputs.st_width)}.nc",
        )
        for row in root_rows
    )
    for artifact in artifacts:
        if not artifact.path.is_file():
            raise FileNotFoundError(
                f"run_id={artifact.run_id}: root missing {artifact.path}"
            )
    return artifacts


def transform(
    derived_row: ScenarioRow,
    ancestor_artifact: ClimateArtifact,
    *,
    weathergen_config: Path,
    lookup_csv: Path,
    output_path: Path,
    log_path: Path,
    execute: Callable[[list[str], Path], None] = _execute,
) -> ClimateArtifact:
    """Consume the exact ancestor selected by the validated row's edge."""
    payload = dict(derived_row.payload)
    if derived_row.scenario_type != "stochastic" or not payload.get("st_id"):
        raise ValueError("transform requires a stochastic design-point row")
    if derived_row.derived_from != ancestor_artifact.run_id:
        raise ValueError(f"run_id={derived_row.run_id}: ancestor id mismatch")
    if not ancestor_artifact.path.is_file():
        raise FileNotFoundError(ancestor_artifact.path)
    if output_path.resolve() == ancestor_artifact.path.resolve():
        raise ValueError("transform cannot overwrite its ancestor")
    command = [
        "Rscript",
        "--vanilla",
        "blueearth_cst/weathergen/impose_climate_change.R",
        str(ancestor_artifact.path),
        str(weathergen_config),
        str(lookup_csv),
        str(output_path),
        payload["st_id"],
    ]
    execute(command, log_path)
    if not output_path.is_file():
        raise FileNotFoundError(
            f"run_id={derived_row.run_id}: transform missing {output_path}"
        )
    return ClimateArtifact(derived_row.run_id, output_path)


def describe(
    artifact: ClimateArtifact, interpretation: UnitInterpretation
) -> ForcingDescriptor:
    """Describe the provider's right-labelled daily forcing without conversion."""
    return describe_forcing(artifact, interpretation, time_label="interval_end")


def plan_collection(
    project_dir,
    request,
    *,
    generation_config,
    scenario_spec,
    source_inputs,
    provider_code,
    environment,
    preparation_context,
):
    """Resolve collection identity only after every declared source exists.

    ``source_inputs`` maps a scientific role to a resolved local path. Generated
    execution paths belong to scheduling state, never this source inventory.
    This planner performs no collection writes and does not resolve random seeds.
    """
    from blueearth_cst.experiment.collection_resolution import scenario_request
    from blueearth_cst.experiment.content_identity import (
        collection_id,
        content_sha256,
        scenario_semantics_sha256,
    )
    from blueearth_cst.experiment.scenario_rows import stochastic_rows
    from blueearth_cst.shared.provenance import file_sha256

    capacity = generation_config["unit_id_capacity"]
    rows = stochastic_rows(
        scenario_spec["n_realizations"],
        scenario_spec["n_design_points"],
        unit_id_capacity=capacity,
    )
    inventory = []
    for role, source in sorted(source_inputs.items()):
        path = Path(source).resolve(strict=True)
        inventory.append(
            {
                "role": role,
                "path": path.as_posix(),
                "sha256": file_sha256(path),
                "size_bytes": path.stat().st_size,
                "metadata": {},
            }
        )
    documents = {
        "generation_config": generation_config,
        "source_inventory": inventory,
        "provider_code": provider_code,
        "environment": environment,
        "preparation_context": preparation_context,
    }
    names = {
        "generation_config": "generation_config.json",
        "source_inventory": "source_inventory.json",
        "provider_code": "provider_code_inventory.json",
        "environment": "generation_environment.json",
        "preparation_context": "preparation_context.json",
    }
    intent = {
        "schema_version": "scenario-collection/1",
        "canonicalization_id": "collection-canon/1",
        "scenario_type": "stochastic",
        "provider": {"name": "weathergenr", "revision": content_sha256(provider_code)},
        "scenario_spec": scenario_spec,
        "scenario_semantics_sha256": scenario_semantics_sha256(rows),
        "unit_id_capacity": capacity,
        "unit_id_width": len(str(capacity)),
        "run_count": len(rows),
        **{
            key: {"path": names[key], "sha256": content_sha256(value)}
            for key, value in documents.items()
        },
    }
    intent["collection_id"] = collection_id(intent)
    return scenario_request(project_dir, request, intent, inventory, documents)


def initialize_planned_collection(
    project_dir,
    plan,
    invocation_id,
    *,
    lookup_path,
    catalog_bytes,
    ancillary_sources,
    config_snapshot=None,
):
    """Write reviewed portable inputs before authorizing row-generation jobs.

    ``config_snapshot`` is the rendered ``composed_config.yml`` bytes. It is
    written here rather than at publication because
    :func:`write_collection_payload` refuses every write once ``collection.json``
    exists -- the collection is sealed, and the snapshot has to be inside the
    seal or it could be added to a retained collection afterwards.

    It joins ``payloads`` beside ``scenario_table.csv`` and the lookup, which
    are likewise written into the collection without being named in
    ``collection_intent.json``. That is what keeps it out of ``collection_id``.
    """
    import csv
    import io

    from blueearth_cst.experiment.content_identity import (
        canonical_json_bytes,
        content_sha256,
        identity_segment,
    )
    from blueearth_cst.experiment.scenario_collection import initialize_collection_jobs
    from blueearth_cst.experiment.scenario_rows import stochastic_rows

    intent = plan["intent"]
    documents = plan["documents"]
    payloads = {
        intent[key]["path"]: canonical_json_bytes(value)
        for key, value in documents.items()
    }
    if set(documents) != {
        "generation_config",
        "source_inventory",
        "provider_code",
        "environment",
        "preparation_context",
    }:
        raise ValueError("source plan lacks the complete initialization documents")
    for key, value in documents.items():
        if content_sha256(value) != intent[key]["sha256"]:
            raise ValueError(f"source plan {key} differs from intent")
    context = documents["preparation_context"]
    import hashlib

    if hashlib.sha256(catalog_bytes).hexdigest() != context["catalog"]["sha256"]:
        raise ValueError("planned preparation catalog changed")
    from blueearth_cst.shared.provenance import file_sha256

    if set(ancillary_sources) != {entry["path"] for entry in context["ancillary"]}:
        raise ValueError("planned ancillary inventory changed")
    for entry in context["ancillary"]:
        path = Path(ancillary_sources[entry["path"]])
        if (
            file_sha256(path) != entry["sha256"]
            or path.stat().st_size != entry["size_bytes"]
        ):
            raise ValueError("planned ancillary bytes changed")
        payloads[entry["path"]] = path
    spec = intent["scenario_spec"]
    rows = stochastic_rows(
        spec["n_realizations"],
        spec["n_design_points"],
        unit_id_capacity=intent["unit_id_capacity"],
    )
    table = io.StringIO(newline="")
    writer = csv.DictWriter(
        table, fieldnames=list(rows[0].as_record()), lineterminator="\n"
    )
    writer.writeheader()
    writer.writerows(row.as_record() for row in rows)
    payloads["scenario_table.csv"] = table.getvalue().encode("utf-8")
    payloads["stress_test_lookup.csv"] = Path(lookup_path)
    payloads[context["catalog"]["path"]] = catalog_bytes
    if config_snapshot is not None:
        from blueearth_cst.shared.workflow_config_snapshot import SNAPSHOT_NAME

        payloads[SNAPSHOT_NAME] = config_snapshot
    log_row(
        f"{identity_segment(intent['collection_id'], 'collection_id')}: "
        f"claiming {plural(len(rows), 'scenario row')}, {plural(len(payloads), 'portable input')}",
        module="collection",
    )
    return initialize_collection_jobs(project_dir, plan, invocation_id, payloads)


def publish_planned_collection(project_dir, plan, invocation_id):
    """Reopen every declared row and publish the immutable ready marker last."""
    from blueearth_cst.experiment.content_identity import (
        collection_revision,
        confined_path,
        identity_segment,
    )
    from blueearth_cst.experiment.forcing_descriptor import (
        collection_forcing_descriptor,
        describe_ancillary,
    )
    from blueearth_cst.experiment.scenario_collection import (
        _job_collection_claim,
        publish_collection,
    )
    from blueearth_cst.experiment.scenario_rows import stochastic_rows
    from blueearth_cst.shared.provenance import file_sha256

    claim = _job_collection_claim(project_dir, plan, invocation_id)
    intent = plan["intent"]
    spec = intent["scenario_spec"]
    rows = stochastic_rows(
        spec["n_realizations"],
        spec["n_design_points"],
        unit_id_capacity=intent["unit_id_capacity"],
    )

    def reference(relative):
        return {
            "path": relative,
            "sha256": file_sha256(confined_path(claim.root, relative)),
        }

    reader = plan["documents"]["preparation_context"]["generated_forcing_reader"]
    forcing = []
    for row in rows:
        relative = f"forcing/run_{row.run_id}.nc"
        path = confined_path(claim.root, relative)
        forcing.append(
            {
                "run_id": row.run_id,
                **reference(relative),
                "size_bytes": path.stat().st_size,
                "descriptor": collection_forcing_descriptor(path, reader),
            }
        )
    manifest = {
        "schema_version": "scenario-collection/1",
        "status": "ready",
        "collection_id": intent["collection_id"],
        "intent_path": "collection_intent.json",
        "intent_sha256": plan["intent_sha256"],
        "scenario_table": reference("scenario_table.csv"),
        "scenario_type_artifacts": [
            {"role": "perturbation_lookup", **reference("stress_test_lookup.csv")}
        ],
        "preparation_context": intent["preparation_context"],
        "forcing": forcing,
    }
    manifest["collection_revision"] = collection_revision(manifest)
    log_row(
        f"{identity_segment(intent['collection_id'], 'collection_id')}: "
        f"sealing {plural(len(forcing), 'forcing file')} as immutable",
        module="collection",
    )
    return publish_collection(
        claim,
        manifest,
        describe_forcing=collection_forcing_descriptor,
        describe_ancillary=describe_ancillary,
    )


if __name__ == "__main__" and "snakemake" in globals():
    sm = globals()["snakemake"]
    from blueearth_cst.experiment.content_identity import read_canonical_json
    from blueearth_cst.experiment.scenario_collection import _job_collection_claim

    if read_canonical_json(Path(sm.input.source_plan)) != sm.params.collection_plan:
        raise ValueError("source plan changed before provider execution")
    _job_collection_claim(
        sm.params.project_dir, sm.params.collection_plan, sm.params.invocation_id
    )
    if sm.params.operation == "generate_roots":
        generate_roots(
            tuple(ScenarioRow.from_record(record) for record in sm.params.rows),
            SourceInputs(
                Path(sm.input.climate_nc),
                Path(sm.input.weathergen_config),
                Path(sm.input.basin_cells),
                Path(sm.params.output_dir),
                sm.params.rlz_width,
                sm.params.st_width,
            ),
            log_path=Path(sm.log[0]),
        )
    elif sm.params.operation == "transform":
        row = ScenarioRow.from_record(sm.params.row)
        transform(
            row,
            ClimateArtifact(row.derived_from, Path(sm.input.rlz_nc)),
            weathergen_config=Path(sm.input.weathergen_config),
            lookup_csv=Path(sm.input.lookup_csv),
            output_path=Path(sm.output.rlz_st_nc),
            log_path=Path(sm.log[0]),
        )
    else:
        raise ValueError(f"unknown provider operation {sm.params.operation!r}")
