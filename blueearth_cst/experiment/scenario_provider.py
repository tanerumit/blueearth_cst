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
