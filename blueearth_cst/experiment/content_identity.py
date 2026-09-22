"""Canonical bytes and identity projections for R12 durable collections.

Implements collection-canon/1 and the two equations in the accepted R12 design,
section 8.2. These helpers do not establish collection readiness: persisted
schema, inventory, ordering, and physical descriptors require collection
validation before publication or consumption.
"""

import ast
import hashlib
import json
import os
import re
import tempfile
from collections.abc import Callable, Mapping, Sequence
from pathlib import Path, PureWindowsPath
from typing import Any

from blueearth_cst.experiment.scenario_rows import ScenarioRow
from blueearth_cst.shared.provenance import short_digest


def _check_json(value: Any) -> None:
    """Refuse implicit JSON conversions that would erase input distinctions."""
    if type(value) is dict:
        for key, item in value.items():
            if type(key) is not str:
                raise TypeError("canonical JSON object keys must be strings")
            _check_json(item)
    elif type(value) is list:
        for item in value:
            _check_json(item)
    elif value is not None and type(value) not in (str, bool, int, float):
        raise TypeError(f"unsupported canonical JSON type: {type(value).__name__}")


def canonical_json_bytes(value: Any) -> bytes:
    """Encode plain JSON using collection-canon/1, including its final LF.

    Paths must already be normalized by the caller. Arrays retain their order;
    finite floats use Python's JSON representation (including 1.0 and -0.0).
    Non-JSON types and nonfinite numbers raise rather than being coerced.
    """
    _check_json(value)
    return (
        json.dumps(
            value,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        )
        + "\n"
    ).encode("utf-8")


def content_sha256(value: Any) -> str:
    """Hash collection-canon/1 bytes, without provenance type tags."""
    return hashlib.sha256(canonical_json_bytes(value)).hexdigest()


def atomic_record(path: Path, document: Any, *, replace: bool = False) -> None:
    """Atomically publish canonical bytes at a caller-validated path.

    Exclusive publication refuses an existing path. Replacement is reserved for
    explicitly mutable plans or completion facts; callers own their state checks.
    """
    path = Path(path)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(dir=path.parent, delete=False) as handle:
            temporary = Path(handle.name)
            handle.write(canonical_json_bytes(document))
            handle.flush()
            os.fsync(handle.fileno())
        if replace:
            os.replace(temporary, path)
        else:
            os.link(temporary, path)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def repository_code_inventory(
    repo_root: Path, entry_paths: Sequence[str]
) -> list[dict[str, str]]:
    """Inventory declared executables and their static repository Python imports.

    R/Julia include files are supplied explicitly as entry paths. No top-N bound
    or sampling applies. Imported external packages belong in the stage's
    environment descriptor, rather than this repository source inventory.
    """
    root = Path(repo_root).resolve()
    pending = [confined_path(root, name) for name in entry_paths]
    observed = set()
    while pending:
        path = pending.pop()
        if path in observed:
            continue
        if not path.is_file():
            raise FileNotFoundError(f"invoked repository code is missing: {path}")
        observed.add(path)
        if path.suffix != ".py":
            continue
        module_parts = list(path.relative_to(root).with_suffix("").parts)
        package_parts = module_parts[:-1]
        for depth in range(1, len(package_parts) + 1):
            initializer = root.joinpath(*package_parts[:depth], "__init__.py")
            if initializer.is_file():
                pending.append(initializer)
        for node in ast.walk(ast.parse(path.read_text(encoding="utf-8-sig"))):
            names = []
            if isinstance(node, ast.Import):
                names = [item.name for item in node.names]
            elif isinstance(node, ast.ImportFrom):
                prefix = (
                    package_parts[: len(package_parts) - node.level + 1]
                    if node.level
                    else []
                )
                base = ".".join([*prefix, *([node.module] if node.module else [])])
                names = [base, *(f"{base}.{item.name}" for item in node.names)]
            for name in names:
                if not name.startswith("blueearth_cst"):
                    continue
                relative = name.replace(".", "/")
                for candidate in (f"{relative}.py", f"{relative}/__init__.py"):
                    target = confined_path(root, candidate)
                    if target.is_file():
                        pending.append(target)
    return [
        {
            "path": path.relative_to(root).as_posix(),
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        }
        for path in sorted(observed)
    ]


def stage_environment(
    python_roots: Sequence[str],
    *,
    include_weathergen: bool = False,
    julia_manifest: Path | None = None,
    julia_command: Sequence[str] = ("julia",),
) -> dict[str, Any]:
    """Record resolved stage dependencies and installed native package revisions.

    Stage projections avoid making an unrelated package installation invalidate
    every scientific stage. Active Python dependency markers/extras and installed
    Conda native dependencies are followed without truncation. R's generator
    dependencies are read from the library R actually resolves.
    """
    import importlib.metadata as metadata
    import platform
    import subprocess
    import sys

    from packaging.requirements import Requirement
    from packaging.utils import canonicalize_name

    packages = {"python": platform.python_version(), "platform": platform.platform()}
    distributions = {}
    pending = [(name, "") for name in python_roots]
    visited = set()
    while pending:
        name, extra = pending.pop()
        key = (canonicalize_name(name), extra)
        if key in visited:
            continue
        visited.add(key)
        try:
            distribution = metadata.distribution(name)
        except metadata.PackageNotFoundError:
            if key[0] in {canonicalize_name(root) for root in python_roots}:
                raise
            # Conda's dependency recipe may differ from wheel METADATA. Retain
            # that observed absence explicitly; never install or invent a version.
            packages[f"python:{key[0]}"] = "not-installed"
            distributions[key[0]] = {"status": "not-installed"}
            continue
        canonical = canonicalize_name(distribution.metadata["Name"])
        packages[f"python:{canonical}"] = distribution.version
        distributions[canonical] = {
            "version": distribution.version,
            "metadata_sha256": hashlib.sha256(
                (distribution.read_text("METADATA") or "").encode()
            ).hexdigest(),
        }
        for requirement_text in distribution.requires or []:
            requirement = Requirement(requirement_text)
            if requirement.marker is not None and not requirement.marker.evaluate(
                {"extra": extra}
            ):
                continue
            pending.append((requirement.name, ""))
            pending.extend((requirement.name, item) for item in requirement.extras)
    conda = {}
    for path in (Path(sys.prefix) / "conda-meta").glob("*.json"):
        record = json.loads(path.read_text(encoding="utf-8"))
        conda[canonicalize_name(record["name"])] = record
    native_pending = ["python", *distributions]
    if include_weathergen:
        program = """db <- installed.packages()
roots <- c("weathergenr", "ncdf4", "yaml")
deps <- unique(c(roots, unlist(tools::package_dependencies(roots, db=db, which=c("Depends","Imports","LinkingTo"), recursive=TRUE))))
cat("R\\t", as.character(getRversion()), "\\n", sep="")
for (name in sort(setdiff(deps, "R"))) {
  d <- packageDescription(name)
  revision <- if (is.null(d$RemoteSha)) "" else paste0("+", d$RemoteSha)
  cat(name, "\\t", d$Version, revision, "\\n", sep="")
}
"""
        result = subprocess.run(
            ["Rscript", "--vanilla", "-e", program],
            check=True,
            capture_output=True,
            text=True,
        )
        for line in result.stdout.splitlines():
            name, revision = line.split("\t")
            if not name or not revision:
                raise ValueError(
                    "R dependency resolution returned an incomplete revision"
                )
            packages[f"R:{name}"] = revision
            native_pending.append("r-base" if name == "R" else f"r-{name.lower()}")
    native = {}
    while native_pending:
        name = canonicalize_name(native_pending.pop())
        if name in native or name not in conda:
            continue
        record = conda[name]
        native[name] = {
            key: record.get(key)
            for key in ("name", "version", "build", "sha256", "md5", "depends")
        }
        packages[f"conda:{name}"] = f"{record['version']}+{record['build']}"
        native_pending.extend(
            dependency.split()[0] for dependency in record.get("depends", [])
        )
    locks = {
        "installed-python-distribution-metadata": content_sha256(distributions),
        "installed-conda-dependency-records": content_sha256(native),
    }
    if julia_manifest is not None:
        import tomllib

        manifest = tomllib.loads(Path(julia_manifest).read_text(encoding="utf-8"))
        actual = subprocess.run(
            [*julia_command, "--startup-file=no", "-e", "print(VERSION)"],
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
        if actual.split(".")[:2] != manifest["julia_version"].split(".")[:2]:
            raise ValueError(
                "executing Julia major/minor differs from the locked manifest"
            )
        packages["julia"] = actual
        packages["julia-manifest-version"] = manifest["julia_version"]
        for name, entries in manifest["deps"].items():
            packages[f"julia:{name}"] = ";".join(
                str(entry.get("version", "stdlib"))
                + ":"
                + entry.get("git-tree-sha1", entry["uuid"])
                for entry in entries
            )
        locks["Manifest.toml"] = hashlib.sha256(
            Path(julia_manifest).read_bytes()
        ).hexdigest()
    return {
        "packages": dict(sorted(packages.items())),
        "locks": dict(sorted(locks.items())),
    }


def _unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    """Reject duplicate JSON keys before a decoder can discard their values."""
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate canonical JSON key: {key!r}")
        result[key] = value
    return result


def read_canonical_json(path: Path) -> Any:
    """Read a persisted canonical document, refusing ambiguous or altered bytes.

    This verifies encoding, not the document's application schema or digest.
    """
    raw = path.read_bytes()
    value = json.loads(raw.decode("utf-8"), object_pairs_hook=_unique_object)
    if raw != canonical_json_bytes(value):
        raise ValueError(f"{path}: expected collection-canon/1 bytes")
    return value


def confined_path(root: Path, relative: str) -> Path:
    """Resolve a canonical POSIX artifact path inside its collection root.

    Refuse ambiguous Windows spellings as well as lexical and symlink escapes.
    File existence is checked separately by inventory validation.
    """
    if (
        not isinstance(relative, str)
        or not relative
        or any(character in relative for character in ("\\", ":", "\x00"))
        or any(segment in ("", ".", "..") for segment in relative.split("/"))
        or any(
            segment.rstrip(" .") != segment or PureWindowsPath(segment).is_reserved()
            for segment in relative.split("/")
        )
    ):
        raise ValueError(f"expected a confined relative POSIX path, got {relative!r}")
    resolved_root = root.resolve()
    target = (resolved_root / relative).resolve()
    if not target.is_relative_to(resolved_root) or target == resolved_root:
        raise ValueError(
            f"path {relative!r} resolves outside collection {resolved_root}"
        )
    return target


def _digest(value: Any, field: str) -> str:
    """Require the complete, lowercase identity rather than a display handle."""
    if not isinstance(value, str) or re.fullmatch(r"[0-9a-f]{64}", value) is None:
        raise ValueError(f"{field}: expected lowercase SHA-256, got {value!r}")
    return value


class SegmentCollision(ValueError):
    """A directory segment is already held by a DIFFERENT full identity."""


def identity_segment(value: Any, field: str) -> str:
    """Name a directory after the leading characters of a complete identity.

    A stored identity field is always the whole digest -- :func:`_digest` keeps
    refusing anything shorter. This is the *path* form, and only the path form:
    sixty-four hex characters per directory is what makes a project tree read as
    machine output. ``SHORT_DIGEST_CHARS`` is imported rather than restated so
    that the scenario trees, the metric trees and the config-snapshot bundles
    that already use it cannot drift to different lengths.

    Truncation costs one property, and it is worth naming: a discovered
    directory is no longer self-describing, because a prefix cannot be checked
    against anything on its own. :func:`claim_identity_segment` is what replaces
    that property, and the two are meant to be used together.
    """
    return short_digest(_digest(value, field))


def claim_identity_segment(
    parent: Path,
    value: Any,
    occupant: Callable[[Path], str | None],
    *,
    field: str = "identity",
) -> Path:
    """Resolve an identity's directory, refusing to share it with another.

    Because the segment is a deterministic prefix, exactly one sibling can ever
    collide -- the one at that path -- so this is a single lookup rather than a
    scan of the parent.

    Args:
        parent: Directory the segment is minted in.
        value: The complete identity the directory stands for.
        occupant: Reads the complete identity an EXISTING directory stands for,
            returning ``None`` when it cannot be established. A partially
            written claim returns ``None`` and is left to the caller's own
            exclusivity rules, which already refuse to resume one.
        field: Identity name, for the error message.

    Raises:
        SegmentCollision: The path is held by a different complete identity.
            Loud, never a silent merge into another identity's directory.
    """
    target = Path(parent) / identity_segment(value, field)
    if target.exists():
        held = occupant(target)
        if held is not None and held != value:
            raise SegmentCollision(
                f"{field}: {target} already holds {held}, not {value}"
            )
    return target


def scenario_semantics_sha256(rows: Sequence[ScenarioRow]) -> str:
    """Hash ordered semantic rows, stripping only run_id as required by R12."""
    return content_sha256(
        [
            {key: value for key, value in row.as_record().items() if key != "run_id"}
            for row in rows
        ]
    )


def collection_id(intent: Mapping[str, Any]) -> str:
    """Recompute the generation identity from the persisted intent projection.

    Required identity fields raise on absence; the collection validator owns
    full scenario-spec consistency and referenced-document verification.
    """
    for field, expected in (
        ("schema_version", "scenario-collection/1"),
        ("canonicalization_id", "collection-canon/1"),
    ):
        if intent[field] != expected:
            raise ValueError(f"{field}: expected {expected!r}, got {intent[field]!r}")
    capacity = intent["unit_id_capacity"]
    if type(capacity) is not int or capacity < 1:
        raise ValueError(
            f"unit_id_capacity: expected positive integer, got {capacity!r}"
        )
    provider = intent["provider"]
    if not isinstance(provider["name"], str) or not provider["name"]:
        raise ValueError("provider.name: expected nonempty string")
    projection = {
        "schema_version": intent["schema_version"],
        "scenario_spec": intent["scenario_spec"],
        "scenario_semantics_sha256": _digest(
            intent["scenario_semantics_sha256"], "scenario_semantics_sha256"
        ),
        "provider_name_and_revision": {
            "name": provider["name"],
            "revision": _digest(provider["revision"], "provider.revision"),
        },
        "unit_id_capacity": capacity,
    }
    for field in (
        "generation_config",
        "source_inventory",
        "provider_code",
        "environment",
        "preparation_context",
    ):
        projection[f"{field}_sha256"] = _digest(intent[field]["sha256"], field)
    return content_sha256(projection)


def collection_revision(manifest: Mapping[str, Any]) -> str:
    """Hash the produced-byte inventory in its declared order, excluding itself.

    No sorting or normalization repairs a malformed inventory here; readiness
    validation must reject wrong ordering, missing entries, and descriptors.
    """
    return content_sha256(
        {
            "collection_id": _digest(manifest["collection_id"], "collection_id"),
            "intent_sha256": _digest(manifest["intent_sha256"], "intent_sha256"),
            "scenario_table_sha256": _digest(
                manifest["scenario_table"]["sha256"], "scenario_table.sha256"
            ),
            "scenario_type_artifact_inventory": manifest["scenario_type_artifacts"],
            "preparation_context_sha256": _digest(
                manifest["preparation_context"]["sha256"], "preparation_context.sha256"
            ),
            "ordered_forcing_inventory_with_descriptors": manifest["forcing"],
        }
    )


def generation_seed_material_v2(
    *,
    n_realizations: int,
    simulation_window: Mapping[str, int],
    climate_perturbations: Mapping[str, Any],
    water_year_start: str,
    provider_revision: str,
    sources: Sequence[Mapping[str, Any]],
    generator_settings: Mapping[str, Any],
) -> dict[str, Any]:
    """Build the WF3-only automatic seed preimage from pinned source bytes."""
    if type(n_realizations) is not int or n_realizations < 1:
        raise ValueError("n_realizations must be a positive integer")
    _digest(provider_revision, "provider_revision")
    selected = []
    for role in ("basin_cells", "historical_climate"):
        matches = [item for item in sources if item.get("role") == role]
        if len(matches) != 1:
            raise ValueError(f"expected one pinned {role} source")
        item = matches[0]
        size = item["size_bytes"]
        if type(size) is not int or size < 0:
            raise ValueError(f"{role}.size_bytes must be nonnegative")
        selected.append(
            {"role": role, "sha256": _digest(item["sha256"], role), "size_bytes": size}
        )
    return {
        "schema_version": "generation-seed-material/2",
        "scenario_type": "stochastic",
        "n_realizations": n_realizations,
        "simulation_window": dict(simulation_window),
        "climate_perturbations": dict(climate_perturbations),
        "water_year_start": water_year_start,
        "provider_revision": provider_revision,
        "source_inventory_sha256": content_sha256(selected),
        "generator_settings": dict(generator_settings),
    }


def automatic_seed_v2(material: Mapping[str, Any]) -> int:
    """Resolve collection-canon/1 digest to the accepted 31-bit seed."""
    if material.get("schema_version") != "generation-seed-material/2":
        raise ValueError("expected generation-seed-material/2")
    return int(content_sha256(dict(material)), 16) % (2**31 - 1)


def collection_id_v2(intent: Mapping[str, Any]) -> str:
    """Hash only the declared scenario-collection/2 scientific dependencies."""
    if intent.get("schema_version") != "scenario-collection-intent/2":
        raise ValueError("expected scenario-collection-intent/2")
    if intent.get("canonicalization_id") != "collection-canon/1":
        raise ValueError("expected collection-canon/1")
    capacity = intent["run_group_id_capacity"]
    if type(capacity) is not int or capacity < 1:
        raise ValueError("run_group_id_capacity must be positive")
    digests = intent["identity_digests"]
    if set(digests) != {
        "generation_config",
        "source_inventory",
        "provider_code",
        "environment",
    }:
        raise ValueError("collection identity_digests has unexpected fields")
    return content_sha256(
        {
            "schema_version": "scenario-collection-identity/2",
            "scenario_spec": intent["scenario_spec"],
            "scenario_semantics_sha256": _digest(
                intent["scenario_semantics_sha256"], "scenario_semantics_sha256"
            ),
            "provider_name_and_revision": intent["provider"],
            "run_group_id_capacity": capacity,
            **{
                f"{name}_sha256": _digest(value, name)
                for name, value in digests.items()
            },
        }
    )


def collection_revision_v2(marker: Mapping[str, Any], intent: Mapping[str, Any]) -> str:
    """Hash checked scientific products in declared scenario order."""
    dates = [
        {
            "role": entry["role"],
            "sha256": entry["file"]["sha256"],
            "size_bytes": entry["file"]["size_bytes"],
        }
        for entry in marker["provider_products"]
        if entry["role"] in ("sim_dates", "resampled_dates")
    ]
    if [entry["role"] for entry in dates] != ["sim_dates", "resampled_dates"]:
        raise ValueError("provider date products must have fixed order")
    return content_sha256(
        {
            "schema_version": "collection-revision/2",
            "collection_id": _digest(marker["collection_id"], "collection_id"),
            "scenario_semantics_sha256": _digest(
                intent["scenario_semantics_sha256"], "scenario_semantics_sha256"
            ),
            "scenario_run_lookup_sha256": _digest(
                marker["scenario_run_lookup"]["sha256"], "scenario_run_lookup"
            ),
            "perturbation_lookup_sha256": _digest(
                marker["perturbation_lookup"]["sha256"], "perturbation_lookup"
            ),
            "series": [
                {
                    "run_id": entry["run_id"],
                    "sha256": entry["file"]["sha256"],
                    "size_bytes": entry["file"]["size_bytes"],
                    "descriptor": entry["descriptor"],
                }
                for entry in marker["series"]
            ],
            "date_products": dates,
        }
    )
