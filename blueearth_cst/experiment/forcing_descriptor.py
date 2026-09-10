"""Physical forcing metadata, separate from scenario meaning and native labels."""

from dataclasses import dataclass
from pathlib import Path

import numpy as np
import xarray as xr
from pyproj import CRS


@dataclass(frozen=True)
class ClimateArtifact:
    """A forcing artifact addressed by an opaque run id."""

    run_id: str
    path: Path


@dataclass(frozen=True)
class UnitInterpretation:
    """Explicit effective-unit binding justified by source/preparation provenance."""

    revision: str
    evidence: str
    variables: tuple[tuple[str, str], ...]

    def validate(self, observed: set[str]) -> None:
        """Require one evidenced physical interpretation per observed variable."""
        names = [name for name, _ in self.variables]
        if not self.revision or not self.evidence:
            raise ValueError(
                "forcing units require interpretation revision and evidence"
            )
        if len(set(names)) != len(names) or set(names) != observed:
            raise ValueError(
                f"unit interpretation variables {names} do not equal {sorted(observed)}"
            )
        if any(not units for _, units in self.variables):
            raise ValueError("effective forcing units must be explicit")


@dataclass(frozen=True)
class VariableDescriptor:
    """One variable's physical units and unmodified native metadata."""

    name: str
    units: str
    dimensions: tuple[str, ...]
    native_attributes: tuple[tuple[str, object], ...]
    missing_count: int


@dataclass(frozen=True)
class ForcingDescriptor:
    """Observed spatial/time axes and explicitly interpreted physical units."""

    variables: tuple[VariableDescriptor, ...]
    crs: str
    dimensions: tuple[tuple[str, int], ...]
    calendar: str
    timestep_seconds: float
    time_label: str
    first_time: str
    last_time: str
    unit_interpretation: UnitInterpretation


def describe_forcing(
    artifact: ClimateArtifact,
    interpretation: UnitInterpretation,
    *,
    time_label: str,
) -> ForcingDescriptor:
    """Inspect forcing without treating native unit labels as conversions.

    Args:
        artifact: Existing generated forcing; never modified by inspection.
        interpretation: Versioned, evidenced units for every physical variable.
        time_label: Explicit interval convention supplied by the provider binding.

    Raises:
        ValueError: Missing metadata, invalid axes or incomplete interpretation.
    """
    if time_label not in {"interval_end", "instant"}:
        raise ValueError(f"invalid forcing time_label {time_label!r}")
    with xr.open_dataset(artifact.path) as ds:
        if "time" not in ds.coords or ds.sizes["time"] < 2:
            raise ValueError(
                f"run_id={artifact.run_id}: forcing needs at least two times"
            )
        index = ds.indexes["time"]
        if not index.is_unique or not index.is_monotonic_increasing:
            raise ValueError(f"run_id={artifact.run_id}: time must increase uniquely")
        steps = np.array(
            [
                (right - left).total_seconds()
                for left, right in zip(index[:-1], index[1:])
            ]
        )
        if not np.all(steps == steps[0]) or steps[0] <= 0:
            raise ValueError(
                f"run_id={artifact.run_id}: forcing timestep is not uniform"
            )
        if "spatial_ref" not in ds:
            raise ValueError(f"run_id={artifact.run_id}: missing spatial_ref")
        spatial = ds["spatial_ref"].attrs
        wkt = spatial.get("crs_wkt") or spatial.get("spatial_ref")
        if not wkt:
            raise ValueError(f"run_id={artifact.run_id}: spatial_ref has no CRS WKT")
        crs = CRS.from_wkt(wkt).to_string()
        names = set(ds.data_vars) - {"spatial_ref"}
        interpretation.validate(names)
        units = dict(interpretation.variables)
        variables = tuple(
            VariableDescriptor(
                name=name,
                units=units[name],
                dimensions=tuple(ds[name].dims),
                native_attributes=tuple(sorted(ds[name].attrs.items())),
                missing_count=int((~np.isfinite(ds[name])).sum().item()),
            )
            for name in sorted(names)
        )
        return ForcingDescriptor(
            variables=variables,
            crs=crs,
            dimensions=tuple((str(name), int(size)) for name, size in ds.sizes.items()),
            calendar=str(ds.time.dt.calendar),
            timestep_seconds=float(steps[0]),
            time_label=time_label,
            first_time=str(index[0]),
            last_time=str(index[-1]),
            unit_interpretation=interpretation,
        )
