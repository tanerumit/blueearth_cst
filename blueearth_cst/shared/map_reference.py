"""Declared historical map dependencies, preparation identities and common display.

All identities use current bytes and logical roles. Executable paths belong only
to source specs and rule declarations; retained WF0 fields are never producer inputs.
"""

import hashlib
import importlib
import json
import math
import os
import platform
import sys
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from uuid import uuid4

import numpy as np
import pandas as pd
import xarray as xr
import yaml
from matplotlib.colors import LinearSegmentedColormap

from blueearth_cst.climate_analysis.source_map_fields import (
    SourceMapSpec,
    prepare_source_map_fields,
)
from blueearth_cst.plotting.prepared_maps import MapFrame, MapScale
from blueearth_cst.shared.output_capture import captured_output
from blueearth_cst.shared.wf3_science import (
    DEFAULT_BASIN_INDEX,
    DEFAULT_HYDROGRAPHY,
    climate_store_rule,
)

SCHEMA_VERSION = 1
POLICIES = {
    "preparation": 1,
    "units_availability": 1,
    "source_pet": 1,
    "frame_support": 1,
    "ticks": 1,
    "palette": 1,
    "classes": 1,
}
PREPARATION_FILES = (
    "blueearth_cst/climate_analysis/source_map_fields.py",
    "blueearth_cst/climate_analysis/diagnostic_maps.py",
    "blueearth_cst/climate_analysis/diagnostics.py",
    "blueearth_cst/climate_analysis/diagnostic_tables.py",
    "blueearth_cst/climate_analysis/diagnostic_settings.py",
    "blueearth_cst/climate_analysis/plot_climate_source.py",
    "blueearth_cst/climate_analysis/climate_figures.py",
    "blueearth_cst/climate_analysis/figure_naming.py",
    "blueearth_cst/shared/climate_parity.py",
    "blueearth_cst/shared/grid_cells.py",
    "blueearth_cst/shared/map_reference.py",
    "blueearth_cst/shared/snake_utils.py",
    "blueearth_cst/shared/variable_registry.py",
    "blueearth_cst/shared/advanced_settings.py",
    "blueearth_cst/shared/run_log_core.py",
    "blueearth_cst/shared/wf3_science.py",
    "blueearth_cst/shared/plot_style.py",
    "blueearth_cst/plotting/fundamentals.py",
    "blueearth_cst/plotting/prepared_maps.py",
    "blueearth_cst/__init__.py",
    "blueearth_cst/climate_analysis/__init__.py",
    "blueearth_cst/shared/__init__.py",
    "blueearth_cst/plotting/__init__.py",
)
REFERENCE_FILES = (
    *PREPARATION_FILES,
    "blueearth_cst/shared/produce_map_reference.py",
)
LOCK_FILES = ("pixi.lock", "Manifest.toml")
VARIABLES = ("precip", "temp", "pet")
SCIENTIFIC_ATTRS = (
    "units",
    "latitude_resolution",
    "longitude_resolution",
    "reporting_year_label",
    "period_start",
    "period_end",
)


def canonical_json(value: Any) -> str:
    """Strict sorted JSON; preserve integer types and normalize negative zero."""

    def normalize(item: Any) -> Any:
        if isinstance(item, Mapping):
            if not all(isinstance(key, str) for key in item):
                raise TypeError("Identity JSON requires string object keys")
            return {key: normalize(val) for key, val in item.items()}
        if isinstance(item, (list, tuple)):
            return [normalize(val) for val in item]
        if isinstance(item, np.generic):
            return normalize(item.item())
        if isinstance(item, float):
            if not math.isfinite(item):
                raise ValueError("Identity JSON forbids nonfinite numbers")
            return 0.0 if item == 0 else item
        if item is None or isinstance(item, (str, int, bool)):
            return item
        raise TypeError(f"Unsupported identity JSON type: {type(item).__name__}")

    return json.dumps(
        normalize(value), sort_keys=True, separators=(",", ":"), allow_nan=False
    )


def json_digest(value: Any) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def file_digest(path: str | Path) -> str:
    """Stream every byte; sizes and modification times are never identities."""
    result = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            result.update(chunk)
    return result.hexdigest()


def resolve_map_completeness(value: Any = None) -> dict[str, int]:
    """Resolve the closed project ``climate.map_reference`` policy."""
    defaults = {"max_missing_days_month": 3, "max_missing_days_year": 15}
    if value is None:
        return defaults
    if not isinstance(value, Mapping):
        raise ValueError("climate.map_reference must be a mapping")
    if set(value) - set(defaults):
        raise ValueError(
            f"climate.map_reference has unknown keys: {sorted(set(value) - set(defaults))}"
        )
    result = {**defaults, **value}
    for key, number in result.items():
        if (
            type(number) is not int
            or number < 0
            or (key.endswith("month") and number > 27)
        ):
            bound = (
                "an integer in [0, 27]"
                if key.endswith("month")
                else "a nonnegative integer"
            )
            raise ValueError(
                f"climate.map_reference.{key} must be {bound}; got {number!r}"
            )
    return result


def require_wf0_completeness(
    settings: Mapping[str, Any], reference: Mapping[str, int]
) -> None:
    """Fail DAG construction on differing WF0 and historical-reference policies."""
    for key, value in resolve_map_completeness(reference).items():
        if type(settings.get(key)) is not int or settings.get(key) != value:
            raise ValueError(
                f"workflows.analyze_climate.diagnostics.{key}={settings.get(key)!r} "
                f"must equal climate.map_reference.{key}={value}"
            )


def source_role(source: str) -> str:
    if source not in {"era5", "chirps", "chirps_global"}:
        raise ValueError(f"Historical map source is unsupported: {source!r}")
    return "temperature-carrier" if source == "era5" else "precipitation-only"


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _code_identity(paths: Sequence[str]) -> list[dict[str, str]]:
    return [
        {"path": path, "sha256": file_digest(_repo_root() / path)} for path in paths
    ]


def environment_identity() -> dict[str, Any]:
    """Qualify actual imported versions and relevant Conda builds against Pixi v7."""
    root = _repo_root()
    lock = yaml.safe_load((root / "pixi.lock").read_text(encoding="utf-8"))
    if lock.get("version") != 7:
        raise ValueError("Map environment qualification requires Pixi lock schema 7")
    active_platform = (
        "win-64"
        if sys.platform == "win32"
        else "linux-64"
        if sys.platform.startswith("linux")
        else None
    )
    if active_platform is None:
        raise ValueError(f"Unsupported map environment platform: {sys.platform}")
    urls = {
        entry["conda"]
        for entry in lock["environments"]["default"]["packages"][active_platform]
        if "conda" in entry
    }
    expected = {}
    for url in urls:
        archive = url.rsplit("/", 1)[-1].removesuffix(".conda").removesuffix(".tar.bz2")
        name, version, build = archive.rsplit("-", 2)
        expected[name] = (version, build)
    modules = {
        "hydromt": "hydromt",
        "numpy": "numpy",
        "pandas": "pandas",
        "xarray": "xarray",
        "scipy": "scipy",
        "rasterio": "rasterio",
        "pyproj": "pyproj",
        "dask-core": "dask",
        "netcdf4": "netCDF4",
        "matplotlib-base": "matplotlib",
        "pyyaml": "yaml",
        "shapely": "shapely",
        "geopandas-base": "geopandas",
    }
    loaded = {
        name: str(importlib.import_module(module).__version__)
        for name, module in modules.items()
    }
    loaded["python"] = platform.python_version()
    rasterio = importlib.import_module("rasterio")
    pyproj = importlib.import_module("pyproj")
    netcdf = importlib.import_module("netCDF4")
    loaded.update(
        {
            "libgdal-core": rasterio.__gdal_version__,
            "proj": pyproj.__proj_version__,
            "libnetcdf": netcdf.__netcdf4libversion__.split()[0],
        }
    )
    packages = {}
    for name, version in sorted(loaded.items()):
        locked = expected.get(name)
        installed = None
        if locked is not None:
            metadata = (
                Path(sys.prefix) / "conda-meta" / f"{name}-{locked[0]}-{locked[1]}.json"
            )
            if metadata.is_file():
                entry = json.loads(metadata.read_text(encoding="utf-8"))
                installed = (entry["version"], entry["build"])
        if locked is None or version != locked[0] or installed != locked:
            raise ValueError(
                f"Map environment inconsistent with Pixi lock: {name}, loaded {version}, locked {locked}, installed {installed}"
            )
        packages[name] = {"version": version, "build": expected[name][1]}
    return {
        "environment": "default",
        "platform": active_platform,
        "packages": packages,
        "locks": _code_identity(LOCK_FILES),
    }


def _orography_descriptor(catalogs: Sequence[Path]) -> Any:
    """Qualify HydroMT's descriptor; preserve its root-relative logical URI."""
    import hydromt

    # Planning runs before rule-log capture, including runner preflights and DAG
    # parsing. Hide routine catalog chatter while retaining warnings and failures.
    with captured_output():
        source = hydromt.DataCatalog(
            data_libs=[str(path) for path in catalogs]
        ).get_source("era5_orography")
    if (
        source.data_type != "RasterDataset"
        or source.driver.name != "raster_xarray"
        or source.uri_resolver.name != "convention"
        or source.driver.filesystem.protocol != "file"
        or source.uri_resolver.filesystem.protocol != "file"
        or source.driver.options.preprocess is not None
        or source.driver.options.ext_override is not None
        or "://" in source.full_uri
        or Path(source.uri).is_absolute()
        or any(character in source.uri for character in "{}*?[")
        or Path(source.full_uri).suffix.lower() not in {".nc", ".netcdf"}
    ):
        raise ValueError(
            "era5_orography: unqualified concrete local input closure; return source/driver interface gap to G1"
        )
    return source


def resolve_source_orography(catalogs: Sequence[Path]) -> tuple[Path, ...]:
    """Resolve the qualified static local ERA5 NetCDF descriptor without reading it."""
    source = _orography_descriptor(catalogs)
    uris = source.uri_resolver.resolve(
        source.full_uri, variables=["z"], metadata=source.metadata
    )
    if len(uris) != 1 or not Path(uris[0]).is_file():
        raise ValueError(
            "era5_orography must resolve to one existing local NetCDF file"
        )
    return (Path(uris[0]),)


def source_spec_dict(spec: SourceMapSpec) -> dict[str, Any]:
    """Executable params only; absolute paths never enter semantic identities."""
    return {
        "source": spec.source,
        "climate_nc": spec.climate_nc.as_posix(),
        "basin_cells": spec.basin_cells.as_posix(),
        "catalogs": [path.as_posix() for path in spec.catalogs],
        "requested_window": list(spec.requested_window),
        "orography_nc": spec.orography_nc.as_posix()
        if spec.orography_nc is not None
        else None,
        "orography_inputs": [path.as_posix() for path in spec.orography_inputs],
    }


def source_spec_from_dict(value: Mapping[str, Any]) -> SourceMapSpec:
    return SourceMapSpec(
        value["source"],
        Path(value["climate_nc"]),
        Path(value["basin_cells"]),
        tuple(Path(path) for path in value["catalogs"]),
        tuple(value["requested_window"]),
        Path(value["orography_nc"]) if value["orography_nc"] is not None else None,
        tuple(Path(path) for path in value["orography_inputs"]),
    )


def reference_arguments(params: Mapping[str, Any]) -> dict[str, Any]:
    """Translate shared executable rule params for producer and both adapters."""
    return {
        "specs": tuple(
            source_spec_from_dict(value) for value in params["source_specs"]
        ),
        "selected": params["selected"],
        "m0": params["m0"],
        "completeness": dict(params["completeness"]),
        "shared_inputs": dict(params["shared_inputs"]),
    }


def source_map_inputs(spec: SourceMapSpec) -> dict[str, Any]:
    """Use identically on WF0 compute and the reference/renderer dependency sets."""
    result = {
        "climate_nc": spec.climate_nc.as_posix(),
        "basin_cells": spec.basin_cells.as_posix(),
        "catalogs": [path.as_posix() for path in spec.catalogs],
        "orography_inputs": [path.as_posix() for path in spec.orography_inputs],
        "preparation_code": [
            (_repo_root() / path).as_posix() for path in PREPARATION_FILES
        ],
        "environment_locks": [(_repo_root() / path).as_posix() for path in LOCK_FILES],
    }
    if spec.orography_nc is not None:
        result["oro_nc"] = spec.orography_nc.as_posix()
    return result


@dataclass(frozen=True)
class HistoricalMapReferenceRule:
    script: str
    inputs: Mapping[str, Any]
    outputs: Mapping[str, str]
    params: Mapping[str, Any]
    source_specs: tuple[SourceMapSpec, ...]


def historical_map_reference_rule(
    *,
    project_dir: str | Path,
    model_region: Any,
    climate: Mapping[str, Any],
    data_sources: str | Sequence[str],
    region_geojson: str | Path,
    basin_geojson: str | Path,
    m0: int,
    hydrography: str = DEFAULT_HYDROGRAPHY,
    basin_index: str = DEFAULT_BASIN_INDEX,
) -> HistoricalMapReferenceRule:
    """Resolve both DAGs' identical producer without reading not-yet-built stores."""
    if type(m0) is not int or not 1 <= m0 <= 12:
        raise ValueError("Map reporting month must be an integer in [1, 12]")
    selected = climate["selected"]
    declared = climate["sources"]
    if (
        not isinstance(declared, (list, tuple))
        or not declared
        or selected not in declared
    ):
        raise ValueError(
            "climate.sources must be a nonempty list containing climate.selected"
        )
    names = tuple(dict.fromkeys([selected, *declared]))
    catalogs = tuple(
        Path(path)
        for path in ([data_sources] if isinstance(data_sources, str) else data_sources)
    )
    completeness = resolve_map_completeness(climate.get("map_reference"))
    orography = resolve_source_orography(catalogs) if "era5" in names else ()
    specs = []
    for name in names:
        source_role(name)
        store = climate_store_rule(
            project_dir,
            model_region,
            name,
            climate["window"],
            [str(path) for path in catalogs],
            hydrography=hydrography,
            basin_index=basin_index,
            enforce_min_years=name == selected,
            forcing_required=name == selected
            or name not in {"chirps", "chirps_global"},
        )
        specs.append(
            SourceMapSpec(
                name,
                Path(store.outputs["climate_nc"]),
                Path(store.outputs["basin_cells"]),
                catalogs,
                (store.params["starttime"][:10], store.params["endtime"][:10]),
                Path(store.outputs["oro_nc"]) if "oro_nc" in store.outputs else None,
                orography if name == "era5" else (),
            )
        )
    shared = {
        "region": Path(region_geojson).as_posix(),
        "basins": Path(basin_geojson).as_posix(),
    }
    inputs = {
        "climate_nc": [spec.climate_nc.as_posix() for spec in specs],
        "basin_cells": [spec.basin_cells.as_posix() for spec in specs],
        "catalogs": [path.as_posix() for path in catalogs],
        "orography": [
            path.as_posix()
            for spec in specs
            for path in (
                *spec.orography_inputs,
                *((spec.orography_nc,) if spec.orography_nc is not None else ()),
            )
        ],
        "reference_code": [
            (_repo_root() / path).as_posix() for path in REFERENCE_FILES
        ],
        "environment_locks": [(_repo_root() / path).as_posix() for path in LOCK_FILES],
        **shared,
    }
    params = {
        "source_specs": [source_spec_dict(spec) for spec in specs],
        "selected": selected,
        "m0": m0,
        "completeness": completeness,
        "shared_inputs": shared,
        "preparation_code_digest": json_digest(_code_identity(PREPARATION_FILES)),
        "reference_code_digest": json_digest(_code_identity(REFERENCE_FILES)),
        "environment": environment_identity(),
        "policies": dict(POLICIES),
    }
    return HistoricalMapReferenceRule(
        "blueearth_cst/shared/produce_map_reference.py",
        inputs,
        {
            "reference": (
                Path(project_dir) / "data/climate/historical/_engine/map_reference.json"
            ).as_posix()
        },
        params,
        tuple(specs),
    )


def _input_identity(spec: SourceMapSpec) -> list[dict[str, str]]:
    files = [
        (
            "climate",
            f"{spec.climate_nc.parent.name}/{spec.climate_nc.name}",
            spec.climate_nc,
        ),
        (
            "basin_cells",
            f"{spec.basin_cells.parent.name}/{spec.basin_cells.name}",
            spec.basin_cells,
        ),
    ]
    if spec.orography_nc is not None:
        files.append(
            (
                "orography_sidecar",
                f"{spec.orography_nc.parent.name}/{spec.orography_nc.name}",
                spec.orography_nc,
            )
        )
    for index, path in enumerate(spec.orography_inputs):
        descriptor = _orography_descriptor(spec.catalogs)
        resolved = resolve_source_orography(spec.catalogs)
        if tuple(item.resolve() for item in resolved) != tuple(
            item.resolve() for item in spec.orography_inputs
        ):
            raise ValueError(
                f"{spec.source}: catalog-backed orography dependency mismatch"
            )
        files.append((f"era5_orography:{index}", Path(descriptor.uri).as_posix(), path))
    return [
        {"role": role, "path": logical, "sha256": file_digest(path)}
        for role, logical, path in files
    ]


def preparation_identity(
    spec: SourceMapSpec, m0: int, completeness: Mapping[str, int]
) -> dict[str, Any]:
    """Expected current-byte identity, independent of candidate order or frame."""
    import hydromt  # noqa: F401 -- registers the raster CRS accessor

    if type(m0) is not int or not 1 <= m0 <= 12:
        raise ValueError("Map reporting month must be an integer in [1, 12]")
    if (
        source_role(spec.source) == "temperature-carrier"
        and spec.orography_nc is None
        and not spec.orography_inputs
    ):
        raise ValueError(
            f"{spec.source}: concrete source PET orography inputs are required"
        )
    with xr.open_dataset(spec.climate_nc) as raw:
        if raw.raster.crs is None or raw.raster.crs.to_epsg() != 4326:
            raise ValueError(
                f"{spec.source}: source-map preparation requires EPSG:4326"
            )
        index = pd.DatetimeIndex(raw.time.values)
        if (
            index.empty
            or index.has_duplicates
            or not index.is_monotonic_increasing
            or (index != index.normalize()).any()
        ):
            raise ValueError(
                f"{spec.source}: ordered unique midnight daily Gregorian dates required"
            )
        first, last = index.min(), index.max()
        labels = [
            year
            for year in range(first.year - 1, last.year + 1)
            if pd.Timestamp(year, m0, 1) >= first
            and pd.Timestamp(year + 1, m0, 1) - pd.Timedelta(days=1) <= last
        ]
        present = [variable for variable in VARIABLES if variable in raw]
        units_original = {
            variable: raw[variable].attrs.get("units") for variable in present
        }
    return {
        "schema_version": SCHEMA_VERSION,
        "source": spec.source,
        "role": source_role(spec.source),
        "scientific_variables": ["precip"]
        if source_role(spec.source) == "precipitation-only"
        else ["precip", "temp", "pet"],
        "extracted_variables": present,
        "units_original": units_original,
        "crs": "EPSG:4326",
        "requested_window": list(spec.requested_window),
        "extraction_span": [str(first.date()), str(last.date())],
        "full_reporting_years": labels,
        "reporting_month": m0,
        "completeness": resolve_map_completeness(completeness),
        "policies": {
            key: POLICIES[key]
            for key in ("preparation", "units_availability", "source_pet")
        },
        "catalogs": [
            {"role": f"catalog:{i}", "name": path.name, "sha256": file_digest(path)}
            for i, path in enumerate(spec.catalogs)
        ],
        "inputs": _input_identity(spec),
        "code": _code_identity(PREPARATION_FILES),
        "environment": environment_identity(),
    }


def _array_digest(values: Any, kind: str) -> str:
    array_input = np.asanyarray(values)
    if np.iscomplexobj(array_input) or np.ma.getmaskarray(array_input).any():
        raise ValueError(
            "Payload arrays must be real and explicitly represent missing values"
        )
    values = np.asarray(array_input)
    if not (np.issubdtype(values.dtype, np.number) or values.dtype == np.dtype(bool)):
        raise ValueError("Payload arrays must be numeric or boolean")
    if kind == "float":
        array = np.array(values, dtype="<f8", order="C", copy=True)
        array[array == 0] = 0.0
        array.view("<u8")[np.isnan(array)] = np.uint64(0x7FF8000000000000)
    elif kind == "count":
        if (
            not np.isfinite(values).all()
            or not np.equal(values, values.astype("<i8")).all()
            or (values < 0).any()
        ):
            raise ValueError("Eligible-year counts must be finite nonnegative integers")
        array = np.ascontiguousarray(values, dtype="<i8")
    else:
        if not np.isin(values, [0, 1]).all():
            raise ValueError("Unavailable masks must contain only boolean values")
        array = np.ascontiguousarray(values, dtype="u1")
    return hashlib.sha256(array.tobytes(order="C")).hexdigest()


def fields_digest(fields: xr.Dataset) -> str:
    """Actual payload digest includes every retained auxiliary value/count/mask."""
    inventory = {}
    allowed = {
        f"{variable}{suffix}"
        for variable in VARIABLES
        for suffix in ("", "_valid_years", "_unavailable")
    }
    if set(fields.data_vars) - allowed:
        raise ValueError(
            f"Unknown source-map payload variables: {sorted(set(fields.data_vars) - allowed)}"
        )
    for variable in VARIABLES:
        group = {variable, f"{variable}_valid_years", f"{variable}_unavailable"}
        if group & set(fields.data_vars) and not group <= set(fields.data_vars):
            raise ValueError(
                f"{variable}: map values require matching counts and unavailable mask"
            )
        if variable in fields:
            expected_units = "degC" if variable == "temp" else "mm/year"
            if fields[variable].attrs.get("units") != expected_units:
                raise ValueError(
                    f"{variable}: source-map payload units must be {expected_units}"
                )
    for name in sorted(fields.variables):
        array = fields[name]
        if name in fields.data_vars:
            if set(array.dims) != {"latitude", "longitude"}:
                raise ValueError(
                    f"{name}: annual map dimensions must be latitude/longitude"
                )
            array = array.transpose("latitude", "longitude")
        kind = (
            "count"
            if name.endswith("_valid_years")
            else "mask"
            if name.endswith("_unavailable")
            else "float"
        )
        inventory[name] = {
            "dims": list(array.dims),
            "shape": list(array.shape),
            "sha256": _array_digest(array.values, kind),
            "attrs": {
                key: array.attrs[key] for key in SCIENTIFIC_ATTRS if key in array.attrs
            },
        }
    return json_digest(
        {
            "arrays": inventory,
            "attrs": {
                key: fields.attrs[key]
                for key in SCIENTIFIC_ATTRS
                if key in fields.attrs
            },
        }
    )


def seal_fields(fields: xr.Dataset, expected: Mapping[str, Any]) -> dict[str, Any]:
    """Attach computed preparation and actual payload identity to existing fields."""
    entry = {
        "preparation_identity": dict(expected),
        "preparation_id": json_digest(expected),
        "fields_digest": fields_digest(fields),
    }
    fields.attrs.update(
        map_preparation_schema=SCHEMA_VERSION,
        map_preparation_identity=canonical_json(expected),
        map_preparation_id=entry["preparation_id"],
        map_fields_digest=entry["fields_digest"],
    )
    return entry


def validate_fields(
    fields: xr.Dataset,
    expected: Mapping[str, Any],
    reference_entry: Mapping[str, Any],
    *,
    source: str,
    target: str | Path = "annual_climatology.nc",
) -> dict[str, Any]:
    """Reject missing/stale/tampered fields before the adapter publishes figures."""
    prefix = f"{source}: {target}"
    attrs = fields.attrs
    if (
        type(attrs.get("map_preparation_schema")) not in (int, np.int32, np.int64)
        or attrs.get("map_preparation_schema") != SCHEMA_VERSION
    ):
        raise ValueError(
            f"{prefix}: missing or unsupported map preparation schema; regenerate WF0 compute"
        )
    identity_text = attrs.get("map_preparation_identity")
    if not isinstance(identity_text, str):
        raise ValueError(
            f"{prefix}: missing preparation identity; regenerate WF0 compute"
        )
    identity = json.loads(identity_text)
    entry = {
        "preparation_identity": identity,
        "preparation_id": attrs.get("map_preparation_id"),
        "fields_digest": attrs.get("map_fields_digest"),
    }
    if canonical_json(identity) != canonical_json(expected) or entry[
        "preparation_id"
    ] != json_digest(expected):
        raise ValueError(
            f"{prefix}: stale preparation identity; regenerate WF0 compute and reference"
        )
    if canonical_json(entry) != canonical_json(reference_entry):
        raise ValueError(f"{prefix}: fields/reference preparation mismatch")
    if entry["fields_digest"] != fields_digest(fields):
        raise ValueError(f"{prefix}: source-map payload corruption")
    return entry


def publish_source_fields(
    path: str | Path,
    fields: xr.Dataset,
    spec: SourceMapSpec,
    m0: int,
    completeness: Mapping[str, int],
    expected: Mapping[str, Any],
) -> dict[str, Any]:
    """Seal, reopen and validate a private sibling before atomic publication."""
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    temporary = target.with_name(f".{target.name}.{uuid4().hex}.nc")
    entry = seal_fields(fields, expected)
    try:
        fields.to_netcdf(temporary)
        with xr.open_dataset(temporary) as reopened:
            validate_fields(
                reopened, expected, entry, source=spec.source, target=target
            )
        if canonical_json(
            preparation_identity(spec, m0, completeness)
        ) != canonical_json(expected):
            raise ValueError(
                f"{spec.source}: inputs changed during preparation; publication aborted"
            )
        os.replace(temporary, target)
    finally:
        if temporary.exists():
            temporary.unlink()
    return entry


def native_edges(coordinates: Any, resolution: Any = None) -> np.ndarray:
    """Regular monotonic native edges, including explicit one-cell resolution."""
    original = np.asanyarray(coordinates)
    if (
        not np.issubdtype(original.dtype, np.number)
        or np.iscomplexobj(original)
        or np.ma.getmaskarray(original).any()
    ):
        raise ValueError("Native coordinates must be real and unmasked")
    values = np.asarray(original)
    if not np.issubdtype(values.dtype, np.floating):
        values = values.astype(float)
    if values.ndim != 1 or not len(values) or not np.isfinite(values).all():
        raise ValueError("Native grid coordinates must be a finite nonempty vector")
    if len(values) == 1:
        if (
            isinstance(resolution, bool)
            or resolution is None
            or not np.isfinite(resolution)
            or resolution <= 0
        ):
            raise ValueError("One-cell maps require positive finite native resolution")
        step = float(resolution)
    else:
        steps = np.diff(values.astype(np.float64))
        precision = 2 * float(np.max(np.abs(np.spacing(values))))
        if not (np.all(steps > 0) or np.all(steps < 0)) or not np.allclose(
            steps, steps[0], rtol=0, atol=precision
        ):
            raise ValueError(
                "Maps require regular monotonic rectilinear native coordinates"
            )
        step = values[1] - values[0]
    return np.r_[
        values[0] - step / 2, (values[:-1] + values[1:]) / 2, values[-1] + step / 2
    ]


def field_edges(field: xr.DataArray) -> tuple[np.ndarray, np.ndarray]:
    return (
        native_edges(field.longitude.values, field.attrs.get("longitude_resolution")),
        native_edges(field.latitude.values, field.attrs.get("latitude_resolution")),
    )


def geographic_ticks(low: float, high: float) -> list[float]:
    target = (high - low) / 4
    if not math.isfinite(target) or target <= 0:
        raise ValueError("Geographic tick span must be positive and finite")
    power = 10 ** math.floor(math.log10(target))
    step = next(
        factor * power for factor in (1, 2, 2.5, 5, 10) if factor * power >= target
    )
    return [
        0.0 if (value := round(index * step, 12)) == 0 else value
        for index in range(math.ceil(low / step), math.floor(high / step) + 1)
    ]


def frame_record(field: xr.DataArray, source: str) -> dict[str, Any]:
    x, y = field_edges(field)
    west, east, south, north = (
        float(x.min()),
        float(x.max()),
        float(y.min()),
        float(y.max()),
    )
    if not (-180 <= west < east <= 180 and -90 <= south < north <= 90):
        raise ValueError(
            "Historical reference frame must be geographic without antimeridian crossing"
        )
    cosine = math.cos(math.radians((south + north) / 2))
    if cosine <= 1e-12:
        raise ValueError("Historical reference frame is singular at the poles")
    return {
        "selected_source": source,
        "extent": [west, east, south, north],
        "longitude_ticks": geographic_ticks(west, east),
        "latitude_ticks": geographic_ticks(south, north),
        "aspect": 1 / cosine,
        "crs": "EPSG:4326",
    }


def frame_intersection(field: xr.DataArray, extent: Sequence[float]) -> np.ndarray:
    """Closed cell/frame intersection includes boundary-only touching cells."""
    x, y = field_edges(field)
    west, east, south, north = extent
    columns = (np.minimum(x[:-1], x[1:]) <= east) & (np.maximum(x[:-1], x[1:]) >= west)
    rows = (np.minimum(y[:-1], y[1:]) <= north) & (np.maximum(y[:-1], y[1:]) >= south)
    return rows[:, None] & columns[None, :]


def scale_record(
    variable: str, low: float | None, high: float | None
) -> dict[str, Any]:
    """Approved increments, outward integer-index rounding and resolved palette."""
    if variable not in VARIABLES:
        raise ValueError(f"Unknown map variable: {variable}")
    temperature = variable == "temp"
    result = {
        "units": "degC" if temperature else "mm/year",
        "status": "unavailable" if low is None else "available",
        "reason": "No finite historical reference cells" if low is None else None,
        "extrema": [low, high],
        "boundaries": [],
        "ticks": [],
        "colors": [],
        "under_color": "#fffbe6" if temperature else "#f7fbff",
        "over_color": "#a50f15" if temperature else "#041f4a",
        "missing_color": "#a0a0a0",
    }
    if low is None:
        if high is not None:
            raise ValueError("Unavailable reference extrema must both be null")
        return result
    if high is None or not math.isfinite(low) or not math.isfinite(high) or high < low:
        raise ValueError("Reference extrema must be finite and ordered")
    working_high = high if high > low else low + (0.2 if temperature else 1)
    span = working_high - low

    def within(threshold):
        # Subtraction can widen a translated decimal interval by a few ULPs.
        # Comparing its endpoint keeps the next representable wider span strict.
        return working_high <= low + threshold and (
            span <= threshold
            or math.isclose(
                span,
                threshold,
                rel_tol=0,
                abs_tol=math.ulp(low) + math.ulp(working_high),
            )
        )

    step = 100 if not temperature else 0.2 if within(1.6) else 0.5 if within(4) else 1
    first, last = math.floor(low / step), math.ceil(working_high / step)
    boundaries = [round(index * step, 12) for index in range(first, last + 1)]
    ramp = (
        ("#ffffcc", "#ffe895", "#fec45f", "#fd953f", "#fa4a29")
        if temperature
        else (
            "#deebf7",
            "#c6dbef",
            "#9ecae1",
            "#6baed6",
            "#4292c6",
            "#2171b5",
            "#08519c",
        )
    )
    classes = len(boundaries) - 1
    colors = (
        [ramp[-1]]
        if classes == 1
        else LinearSegmentedColormap.from_list("historical", ramp)
        .resampled(classes)(np.arange(classes))
        .tolist()
    )
    result.update(boundaries=boundaries, ticks=list(boundaries), colors=colors)
    return result


def current_reference_identity(
    specs: Sequence[SourceMapSpec],
    selected: str,
    m0: int,
    completeness: Mapping[str, int],
    shared_inputs: Mapping[str, str],
) -> dict[str, Any]:
    if (
        not specs
        or specs[0].source != selected
        or len({spec.source for spec in specs}) != len(specs)
    ):
        raise ValueError("Reference sources must be unique and selected-first")
    preparations = {
        spec.source: preparation_identity(spec, m0, completeness) for spec in specs
    }
    return {
        "sources": [
            {"source": spec.source, "role": source_role(spec.source)} for spec in specs
        ],
        "selected": selected,
        "reporting_month": m0,
        "completeness": resolve_map_completeness(completeness),
        "policies": dict(POLICIES),
        "inputs": [
            {"role": role, "sha256": file_digest(path)}
            for role, path in sorted(shared_inputs.items())
        ],
        "code": _code_identity(REFERENCE_FILES),
        "environment": environment_identity(),
        "source_preparations": {
            source: {
                "preparation_identity": identity,
                "preparation_id": json_digest(identity),
            }
            for source, identity in preparations.items()
        },
    }


def build_reference(
    specs: Sequence[SourceMapSpec],
    selected: str,
    m0: int,
    completeness: Mapping[str, int],
    shared_inputs: Mapping[str, str],
) -> dict[str, Any]:
    """Prepare one source at a time; never reuse WF0 retained diagnostic fields."""
    identity = current_reference_identity(
        specs, selected, m0, completeness, shared_inputs
    )
    expected = json.loads(canonical_json(identity))
    pooled = {
        variable: {"low": None, "high": None, "count": 0, "sources": [], "excluded": []}
        for variable in VARIABLES
    }
    frame = None
    for spec in specs:
        prepared = prepare_source_map_fields(spec, m0, completeness)
        fields = prepared.fields
        if (
            prepared.preparation_identity
            != identity["source_preparations"][spec.source]["preparation_identity"]
        ):
            raise ValueError(
                f"{spec.source}: source inputs changed during reference preparation"
            )
        entry = seal_fields(fields, prepared.preparation_identity)
        identity["source_preparations"][spec.source] = entry
        if frame is None:
            frame = frame_record(fields.precip, selected)
        prep = entry["preparation_identity"]
        grid = fields.precip.transpose("latitude", "longitude")
        x, y = field_edges(grid)
        support = frame_intersection(grid, frame["extent"])
        grid_summary = {
            "grid_dimensions": {
                "latitude": grid.sizes["latitude"],
                "longitude": grid.sizes["longitude"],
            },
            "cell_edges_digest": json_digest(
                {
                    "longitude": _array_digest(x, "float"),
                    "latitude": _array_digest(y, "float"),
                }
            ),
            "intersecting_cells": int(support.sum()),
            "finite_cells": 0,
            "unavailable_cells": int(support.sum()),
            "eligible_year_counts": None,
        }
        scientific = [
            variable
            for variable in VARIABLES
            if variable in fields
            and (
                variable == "precip"
                or source_role(spec.source) == "temperature-carrier"
            )
        ]
        for variable in VARIABLES:
            pool = pooled[variable]
            summary = {
                **grid_summary,
                "source": spec.source,
                "role": source_role(spec.source),
                "effective_dates": prep["extraction_span"],
                "scientific_variables": scientific,
                "full_reporting_years": prep["full_reporting_years"],
                "preparation_id": entry["preparation_id"],
                "fields_digest": entry["fields_digest"],
            }
            if variable not in scientific:
                pool["excluded"].append(
                    {
                        **summary,
                        "reason": "Precipitation-only source role"
                        if variable != "precip"
                        and source_role(spec.source) == "precipitation-only"
                        else "Variable absent",
                    }
                )
                continue
            field = fields[variable].transpose("latitude", "longitude")
            support = frame_intersection(field, frame["extent"])
            finite = support & np.isfinite(field.values)
            values = field.values[finite]
            x, y = field_edges(field)
            counts = (
                fields[f"{variable}_valid_years"]
                .transpose("latitude", "longitude")
                .values[finite]
            )
            summary.update(
                grid_dimensions={
                    "latitude": field.sizes["latitude"],
                    "longitude": field.sizes["longitude"],
                },
                cell_edges_digest=json_digest(
                    {
                        "longitude": _array_digest(x, "float"),
                        "latitude": _array_digest(y, "float"),
                    }
                ),
                intersecting_cells=int(support.sum()),
                finite_cells=int(finite.sum()),
                unavailable_cells=int((support & ~np.isfinite(field.values)).sum()),
                eligible_year_counts=[int(counts.min()), int(counts.max())]
                if len(counts)
                else None,
            )
            if not len(values):
                pool["excluded"].append(
                    {**summary, "reason": "No finite cells intersect reference frame"}
                )
                continue
            low, high = float(values.min()), float(values.max())
            pool["low"] = low if pool["low"] is None else min(pool["low"], low)
            pool["high"] = high if pool["high"] is None else max(pool["high"], high)
            pool["count"] += len(values)
            pool["sources"].append(summary)
        fields.close()
        del prepared, fields
    if canonical_json(
        current_reference_identity(specs, selected, m0, completeness, shared_inputs)
    ) != canonical_json(expected):
        raise ValueError(
            "Historical reference inputs changed during preparation; publication aborted"
        )
    record = {
        "schema_version": SCHEMA_VERSION,
        "identity": identity,
        "frame": frame,
        "variables": {
            variable: {
                **scale_record(variable, pool["low"], pool["high"]),
                "finite_pool_count": pool["count"],
                "sources": pool["sources"],
                "excluded_sources": pool["excluded"],
            }
            for variable, pool in pooled.items()
        },
        "provenance": {
            "method": "Native source fields; raw precipitation/temperature; de Bruin source-grid PET",
            "policies": dict(POLICIES),
            "source_inputs": {
                source: entry["preparation_identity"]["inputs"]
                for source, entry in identity["source_preparations"].items()
            },
            "environment": identity["environment"],
        },
    }
    record["reference_id"] = json_digest(record)
    return record


def validate_reference(
    record: Mapping[str, Any],
    specs: Sequence[SourceMapSpec],
    selected: str,
    m0: int,
    completeness: Mapping[str, int],
    shared_inputs: Mapping[str, str],
) -> None:
    """Reject unknown schema, corrupt payload and current-byte identity drift."""
    if not isinstance(record, Mapping):
        raise ValueError("Historical map reference must be a JSON object")
    if (
        set(record)
        != {
            "schema_version",
            "reference_id",
            "identity",
            "frame",
            "variables",
            "provenance",
        }
        or type(record.get("schema_version")) is not int
        or record["schema_version"] != SCHEMA_VERSION
    ):
        raise ValueError("Unknown historical map reference schema")
    if record["reference_id"] != json_digest(
        {key: value for key, value in record.items() if key != "reference_id"}
    ):
        raise ValueError("Historical map reference payload corruption")
    if set(record["variables"]) != set(VARIABLES):
        raise ValueError(
            "Historical reference variables must be exactly precip/temp/pet"
        )
    if (
        set(record["frame"])
        != {
            "selected_source",
            "extent",
            "longitude_ticks",
            "latitude_ticks",
            "aspect",
            "crs",
        }
        or record["frame"]["crs"] != "EPSG:4326"
    ):
        raise ValueError("Unknown historical reference frame schema/CRS")
    frame = record["frame"]
    extent = frame["extent"]
    if (
        not isinstance(extent, list)
        or len(extent) != 4
        or any(
            type(value) not in (int, float) or not math.isfinite(value)
            for value in extent
        )
    ):
        raise ValueError("Historical reference frame has invalid extent")
    west, east, south, north = extent
    if (
        not (-180 <= west < east <= 180 and -90 <= south < north <= 90)
        or frame["selected_source"] != selected
    ):
        raise ValueError(
            "Historical reference has an incompatible geographic frame authority"
        )
    expected_frame = {
        "longitude_ticks": geographic_ticks(west, east),
        "latitude_ticks": geographic_ticks(south, north),
        "aspect": 1 / math.cos(math.radians((south + north) / 2)),
    }
    for key, value in expected_frame.items():
        if canonical_json(frame[key]) != canonical_json(value):
            raise ValueError(f"Historical reference has inconsistent frame {key}")
    expected = current_reference_identity(
        specs, selected, m0, completeness, shared_inputs
    )
    actual = dict(record["identity"])
    entries = actual["source_preparations"]
    actual["source_preparations"] = {}
    for source, entry in entries.items():
        if (
            set(entry) != {"preparation_identity", "preparation_id", "fields_digest"}
            or not isinstance(entry["fields_digest"], str)
            or len(entry["fields_digest"]) != 64
        ):
            raise ValueError(f"{source}: unknown source-preparation schema")
        actual["source_preparations"][source] = {
            key: value for key, value in entry.items() if key != "fields_digest"
        }
    if canonical_json(actual) != canonical_json(expected):
        raise ValueError(
            "Historical reference is stale: current inputs/code/environment/settings differ"
        )
    provenance = record["provenance"]
    expected_provenance = {
        "method": "Native source fields; raw precipitation/temperature; de Bruin source-grid PET",
        "policies": dict(POLICIES),
        "source_inputs": {
            source: entry["preparation_identity"]["inputs"]
            for source, entry in entries.items()
        },
        "environment": expected["environment"],
    }
    if canonical_json(provenance) != canonical_json(expected_provenance):
        raise ValueError("Historical reference has inconsistent provenance")
    variable_keys = set(scale_record("precip", None, None)) | {
        "finite_pool_count",
        "sources",
        "excluded_sources",
    }
    for variable, scale in record["variables"].items():
        if set(scale) != variable_keys:
            raise ValueError(
                f"{variable}: unknown historical reference variable schema"
            )
        for key, value in scale_record(variable, *scale["extrema"]).items():
            if canonical_json(scale[key]) != canonical_json(value):
                raise ValueError(f"{variable}: inconsistent historical scale {key}")
        if (
            type(scale["finite_pool_count"]) is not int
            or scale["finite_pool_count"] < 0
        ):
            raise ValueError(f"{variable}: invalid finite cell count")
        if (scale["status"] == "available") != (scale["finite_pool_count"] > 0):
            raise ValueError(
                f"{variable}: reference status disagrees with finite pool count"
            )
        source_names = [
            summary["source"]
            for summary in [*scale["sources"], *scale["excluded_sources"]]
        ]
        if len(set(source_names)) != len(source_names) or set(source_names) != set(
            entries
        ):
            raise ValueError(f"{variable}: source contribution inventory mismatch")
        if (
            sum(summary["finite_cells"] for summary in scale["sources"])
            != scale["finite_pool_count"]
        ):
            raise ValueError(f"{variable}: source counts disagree with pool")
        for summary in [*scale["sources"], *scale["excluded_sources"]]:
            required = {
                "source",
                "role",
                "effective_dates",
                "scientific_variables",
                "full_reporting_years",
                "preparation_id",
                "fields_digest",
                "grid_dimensions",
                "cell_edges_digest",
                "intersecting_cells",
                "finite_cells",
                "unavailable_cells",
                "eligible_year_counts",
            }
            excluded = summary in scale["excluded_sources"]
            if set(summary) != required | ({"reason"} if excluded else set()):
                raise ValueError(f"{variable}: unknown source summary schema")
            entry = entries.get(summary["source"])
            if (
                entry is None
                or summary["preparation_id"] != entry["preparation_id"]
                or summary["fields_digest"] != entry["fields_digest"]
            ):
                raise ValueError(f"{variable}: source summary identity mismatch")
            if (
                summary["role"] != source_role(summary["source"])
                or any(
                    type(summary[key]) is not int or summary[key] < 0
                    for key in (
                        "intersecting_cells",
                        "finite_cells",
                        "unavailable_cells",
                    )
                )
                or summary["intersecting_cells"]
                != summary["finite_cells"] + summary["unavailable_cells"]
            ):
                raise ValueError(f"{variable}: invalid source role/cell counts")
            if (
                summary["role"] == "precipitation-only"
                and variable != "precip"
                and not excluded
            ):
                raise ValueError(
                    f"{variable}: precipitation-only source cannot contribute"
                )
            if (
                excluded
                and summary["finite_cells"] != 0
                or not excluded
                and summary["finite_cells"] == 0
            ):
                raise ValueError(f"{variable}: invalid contribution status")
            bounds = summary["eligible_year_counts"]
            if bounds is None:
                if summary["finite_cells"]:
                    raise ValueError(
                        f"{variable}: finite source needs eligible-year count range"
                    )
            elif (
                not isinstance(bounds, list)
                or len(bounds) != 2
                or any(type(value) is not int or value < 0 for value in bounds)
                or bounds[1] < bounds[0]
            ):
                raise ValueError(f"{variable}: invalid eligible-year count range")


def load_reference(path: str | Path, **expected: Any) -> dict[str, Any]:
    record = json.loads(Path(path).read_text(encoding="utf-8"))
    validate_reference(record, **expected)
    return record


def publish_reference(
    path: str | Path, record: Mapping[str, Any], **expected: Any
) -> None:
    """Validate current inputs then atomically replace from a private sibling."""
    validate_reference(record, **expected)
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    temporary = target.with_name(f".{target.name}.{uuid4().hex}.tmp")
    try:
        with temporary.open("xb") as stream:
            stream.write((canonical_json(record) + "\n").encode("utf-8"))
            stream.flush()
            os.fsync(stream.fileno())
        validate_reference(
            json.loads(temporary.read_text(encoding="utf-8")), **expected
        )
        os.replace(temporary, target)
    finally:
        if temporary.exists():
            temporary.unlink()


def drawing_frame(record: Mapping[str, Any]) -> MapFrame:
    frame = record["frame"]
    return MapFrame(
        tuple(frame["extent"]),
        frame["longitude_ticks"],
        frame["latitude_ticks"],
        frame["aspect"],
    )


def drawing_scale(record: Mapping[str, Any], variable: str) -> MapScale:
    scale = record["variables"][variable]
    return MapScale(
        **{
            key: scale[key]
            for key in (
                "units",
                "boundaries",
                "ticks",
                "colors",
                "under_color",
                "over_color",
                "missing_color",
                "status",
            )
        }
    )
