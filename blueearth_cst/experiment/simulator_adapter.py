"""Scenario-neutral preparation and execution contracts for the P1 carrier.

Preparation context is transient in P1: it fingerprints the current catalogs and
physical ancillary files, rather than claiming P2's portable preparation package.
Collection identities are explicitly absent until that durable boundary exists.
"""

from collections.abc import Callable, Sequence
from dataclasses import dataclass
from pathlib import Path
from subprocess import CalledProcessError

from pyproj import CRS

from blueearth_cst.experiment.forcing_descriptor import ForcingDescriptor
from blueearth_cst.experiment.wflow_response_reader import (
    NativeRunArtifacts,
    ResponseRequest,
    open_responses,
)
from blueearth_cst.shared.provenance import file_sha256

__all__ = [
    "NativeRunArtifacts",
    "ResponseRequest",
    "open_responses",
    "requirements",
    "validate_forcing",
    "prepare",
    "execute",
]


class IncompatibleForcingError(ValueError):
    """Physical forcing or its preparation context cannot satisfy the model."""


@dataclass(frozen=True)
class ArtifactReference:
    """An explicitly selected physical input and its observed content digest."""

    path: Path
    sha256: str


@dataclass(frozen=True)
class PreparationContext:
    """Resolved physical inputs; no source-selection policy is evaluated here."""

    catalogs: tuple[ArtifactReference, ...]
    ancillary: tuple[ArtifactReference, ...]
    forcing_entry: str
    elevation_entry: str
    pet_method: str
    press_correction: bool
    temp_correction: bool
    conversions: tuple[str, ...]


@dataclass(frozen=True)
class ForcingRequirement:
    """Explicit physical compatibility contract of a model preparation binding."""

    variables: tuple[tuple[str, str], ...]
    crs: str
    dimensions: tuple[str, ...]
    calendars: tuple[str, ...]
    timestep_seconds: float
    time_label: str
    first_time: str
    last_time: str
    allow_missing: bool


@dataclass(frozen=True)
class ModelReference:
    """The existing built model and its declared forcing requirement."""

    root: Path
    forcing_requirement: ForcingRequirement


@dataclass(frozen=True)
class RunForcing:
    """One opaque run's physical forcing, independent of scenario semantics."""

    run_id: str
    forcing_path: Path
    forcing_sha256: str
    descriptor: ForcingDescriptor
    preparation_context: PreparationContext
    collection_id: str | None
    collection_revision: str | None


@dataclass(frozen=True)
class ValidatedForcing:
    """A forcing record checked against an explicit physical requirement."""

    forcing: RunForcing
    requirement: ForcingRequirement


@dataclass(frozen=True)
class PreparationSettings:
    """Declared existing output paths and simulation coverage; no layout inference."""

    toml_path: Path
    forcing_path: Path
    native_output_path: Path
    native_log_path: Path
    first_time: str
    last_time: str


@dataclass(frozen=True)
class PreparedRun:
    """One prepared execution and the existing physical preparation operations."""

    run_id: str
    toml_path: Path
    native_output_path: Path
    forcing_path: Path
    preparation_context: PreparationContext


def requirements(
    model_reference: ModelReference, response_request: ResponseRequest
) -> ForcingRequirement:
    """Return the built binding's requirement for a nonempty response request."""
    if not response_request.variables or any(
        not variable for variable in response_request.variables
    ):
        raise ValueError("response_request must name required response variables")
    if not model_reference.root.is_dir():
        raise FileNotFoundError(model_reference.root)
    return model_reference.forcing_requirement


def validate_forcing(
    run_forcing: RunForcing, requirement: ForcingRequirement
) -> ValidatedForcing:
    """Refuse incompatible or changed input before any HydroMT preparation."""
    artifact = run_forcing.forcing_path

    def refuse(field: str, required: object, observed: object) -> None:
        raise IncompatibleForcingError(
            f"run_id={run_forcing.run_id}: {field}; required={required!r}, "
            f"observed={observed!r}; artifact={artifact}"
        )

    if not run_forcing.run_id:
        refuse("run_id", "nonempty opaque id", run_forcing.run_id)
    if not artifact.is_file():
        refuse("forcing_path", "existing file", str(artifact))
    observed_digest = file_sha256(artifact)
    if observed_digest != run_forcing.forcing_sha256:
        refuse("forcing_sha256", run_forcing.forcing_sha256, observed_digest)
    descriptor = run_forcing.descriptor
    variables = {variable.name: variable for variable in descriptor.variables}
    for name, units in requirement.variables:
        if name not in variables:
            refuse(f"variables.{name}", units, "absent")
        variable = variables[name]
        if variable.units != units:
            refuse(f"units.{name}", units, variable.units)
        if set(variable.dimensions) != set(requirement.dimensions):
            refuse(f"dimensions.{name}", requirement.dimensions, variable.dimensions)
        if not requirement.allow_missing and variable.missing_count:
            refuse(f"missing_count.{name}", 0, variable.missing_count)
    if CRS.from_user_input(descriptor.crs) != CRS.from_user_input(requirement.crs):
        refuse("crs", requirement.crs, descriptor.crs)
    if descriptor.calendar not in requirement.calendars:
        refuse("calendar", requirement.calendars, descriptor.calendar)
    for field in ("timestep_seconds", "time_label"):
        if getattr(descriptor, field) != getattr(requirement, field):
            refuse(field, getattr(requirement, field), getattr(descriptor, field))
    # Both descriptors use ISO chronological timestamps; this avoids imposing
    # Gregorian arithmetic on the accepted noleap source coordinate.
    if descriptor.first_time.replace("T", " ") > requirement.first_time.replace(
        "T", " "
    ):
        refuse("first_time", requirement.first_time, descriptor.first_time)
    if descriptor.last_time.replace("T", " ") < requirement.last_time.replace("T", " "):
        refuse("last_time", requirement.last_time, descriptor.last_time)
    context = run_forcing.preparation_context
    if not context.catalogs or not context.ancillary:
        refuse("preparation_context", "catalog and ancillary closure", context)
    if context.pet_method not in {"makkink", "debruin"}:
        refuse("pet_method", "existing makkink or debruin binding", context.pet_method)
    if not context.forcing_entry or not context.elevation_entry:
        refuse("catalog_entries", "explicit forcing and elevation keys", context)
    for reference in (*context.catalogs, *context.ancillary):
        if not reference.path.is_file():
            refuse("preparation_input", str(reference.path), "absent")
        observed_digest = file_sha256(reference.path)
        if observed_digest != reference.sha256:
            refuse(
                f"preparation_sha256:{reference.path}",
                reference.sha256,
                observed_digest,
            )
    return ValidatedForcing(run_forcing, requirement)


def prepare(
    run_id: str,
    validated_forcing: ValidatedForcing,
    model_reference: ModelReference,
    settings: PreparationSettings,
) -> PreparedRun:
    """Apply the existing HydroMT preparation to one validated neutral record."""
    if run_id != validated_forcing.forcing.run_id:
        raise ValueError(f"run_id={run_id}: validated forcing belongs to another run")
    if model_reference.forcing_requirement != validated_forcing.requirement:
        raise ValueError(f"run_id={run_id}: model forcing requirement changed")
    if (settings.first_time, settings.last_time) != (
        validated_forcing.requirement.first_time,
        validated_forcing.requirement.last_time,
    ):
        raise ValueError(
            f"run_id={run_id}: preparation coverage differs from validation"
        )
    validate_forcing(validated_forcing.forcing, validated_forcing.requirement)
    from blueearth_cst.experiment.downscale_climate_forcing import prepare_model_forcing

    prepare_model_forcing(validated_forcing.forcing, model_reference, settings)
    return PreparedRun(
        run_id,
        settings.toml_path,
        settings.native_output_path,
        settings.forcing_path,
        validated_forcing.forcing.preparation_context,
    )


def validate_ancillary_grid(
    run_id: str, forcing_grid, elevation_grid, artifact: Path
) -> None:
    """Use HydroMT's grid predicate to refuse incompatible physical elevation."""
    if (
        forcing_grid.raster.crs is None
        or elevation_grid.raster.crs is None
        or forcing_grid.raster.crs != elevation_grid.raster.crs
        or not elevation_grid.raster.aligned_grid(forcing_grid)
    ):
        raise IncompatibleForcingError(
            f"run_id={run_id}: ancillary_grid; required=aligned covering elevation, "
            f"observed={elevation_grid.raster.crs}, {elevation_grid.raster.bounds}; artifact={artifact}"
        )


def batch_arguments(batch_id: str, runs: Sequence[PreparedRun]) -> list[str]:
    """Serialize explicit ordered records without inferring ids from filenames."""
    ids = [run.run_id for run in runs]
    if not ids or len(set(ids)) != len(ids):
        raise ValueError("batch requires nonempty, unique run ids")
    if any(not value.isdecimal() for value in ids) or list(map(int, ids)) != sorted(
        map(int, ids)
    ):
        raise ValueError("batch run ids must be in increasing numeric order")
    arguments = [batch_id]
    for run in runs:
        arguments.extend([run.run_id, str(run.toml_path), str(run.native_output_path)])
    return arguments


def execute(
    prepared_run: PreparedRun,
    *,
    julia_command: Sequence[str],
    log_path: Path,
    run_command: Callable[[list[str], Path], int] | None = None,
) -> NativeRunArtifacts:
    """Execute one explicitly identified prepared run through the batch driver."""
    if run_command is None:
        from blueearth_cst.shared.snake_utils import run_and_tee

        run_command = run_and_tee
    command = [
        *julia_command,
        str(Path(__file__).with_name("run_wflow_batch.jl")),
        *batch_arguments(prepared_run.run_id, [prepared_run]),
    ]
    code = run_command(command, log_path)
    if code:
        raise CalledProcessError(code, command)
    if not prepared_run.native_output_path.is_file():
        raise FileNotFoundError(
            f"run_id={prepared_run.run_id}: {prepared_run.native_output_path}"
        )
    return NativeRunArtifacts(prepared_run.native_output_path, prepared_run.toml_path)
