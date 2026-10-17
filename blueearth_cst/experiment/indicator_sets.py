"""Named WF4 indicator sets: operation selection, closed set files and resolution.

A set file selects registered calculations; it never defines arithmetic. Each
selected entry resolves to an existing ``metric_registry`` declaration, either
by its registered definition id or as an authored alias whose calculation
contract equals one registered definition (``equivalent_definition``).
Titles, descriptions and authored citations are presentation only.
"""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass, replace
from pathlib import Path

import yaml

from blueearth_cst.experiment import metric_registry as registry

OPERATIONS = ("simulations", "indicators")
DEFAULT_SET = "default"
DEFAULT_PRESET = "current_default"
SET_SCHEMA_VERSION = 1
SET_ID_PATTERN = re.compile(r"[a-z][a-z0-9_]*")
SET_ID_MAX_LENGTH = 64
_WINDOWS_RESERVED = {"con", "prn", "aux", "nul"} | {
    f"{stem}{n}" for stem in ("com", "lpt") for n in range(1, 10)
}
#: Toolbox-shipped sets, anchored to the installed repository, never the cwd.
BUNDLED_ROOT = Path(__file__).resolve().parents[2] / "config" / "indicator_sets"
SELECTION_KEYS = ("operations", "indicator_sets", "indicator_set_definitions")


class IndicatorSetError(ValueError):
    """A named indicator-set selection or set file is invalid."""


class _UniqueKeyLoader(yaml.SafeLoader):
    """Safe YAML loader that refuses duplicate mapping keys."""


def _unique_mapping(loader, node, deep=False):
    keys = set()
    for key_node, _ in node.value:
        key = loader.construct_object(key_node, deep=deep)
        if key in keys:
            raise IndicatorSetError(
                f"duplicate YAML key {key!r} at line {key_node.start_mark.line + 1}"
            )
        keys.add(key)
    return loader.construct_mapping(node, deep=deep)


_UniqueKeyLoader.add_constructor(
    yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, _unique_mapping
)


def load_unique_yaml(text: str):
    """Parse YAML safely, refusing duplicate keys and arbitrary objects."""
    return yaml.load(text, Loader=_UniqueKeyLoader)  # noqa: S506 - SafeLoader subclass


def validate_id(value, label: str) -> str:
    """Return a safe set or authored indicator id, or refuse it."""
    if (
        not isinstance(value, str)
        or len(value) > SET_ID_MAX_LENGTH
        or not SET_ID_PATTERN.fullmatch(value)
        or value in _WINDOWS_RESERVED
    ):
        raise IndicatorSetError(
            f"{label} {value!r} must match [a-z][a-z0-9_]*, be at most "
            f"{SET_ID_MAX_LENGTH} characters and not be a Windows reserved name"
        )
    return value


def _string_list(value, label: str, *, allow_empty: bool) -> list[str]:
    if not isinstance(value, list) or (not value and not allow_empty):
        raise IndicatorSetError(
            f"{label} must be a {'list' if allow_empty else 'nonempty list'}"
        )
    if any(not isinstance(item, str) for item in value):
        raise IndicatorSetError(f"{label} entries must be strings")
    if len(set(value)) != len(value):
        raise IndicatorSetError(f"{label} has duplicate entries")
    return list(value)


@dataclass(frozen=True)
class SetSource:
    """A selected set's resolved YAML source, read once per invocation."""

    set_id: str
    path: Path
    bundled: bool
    text: str

    @property
    def sha256(self) -> str:
        return hashlib.sha256(self.text.encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class Selection:
    """Normalized WF4 operation and indicator-set selection."""

    operations: tuple[str, ...]
    sets: tuple[SetSource, ...]
    legacy: bool

    @property
    def simulations(self) -> bool:
        return "simulations" in self.operations

    @property
    def indicators(self) -> bool:
        return "indicators" in self.operations


def uses_named_selection(settings: dict) -> bool:
    """Whether a WF4 config uses the named-set interface rather than ``operation``."""
    return any(key in settings for key in SELECTION_KEYS)


def parse_selection(settings: dict, workflow_path) -> Selection:
    """Validate the named-set interface and capture selected set sources once.

    Relative custom ``config_path`` values resolve against the WF4 YAML that
    declares them; bundled names resolve against :data:`BUNDLED_ROOT`. With
    simulations alone, structure is validated but no set file is opened.
    """
    for key in ("operation", "metrics"):
        if key in settings:
            raise IndicatorSetError(
                f"simulate_system.{key} is the legacy interface and cannot be mixed "
                "with operations/indicator_sets; replace operation with "
                "operations: [simulations, indicators] and metrics with an explicit "
                "indicator set"
            )
    operations = settings.get("operations", list(OPERATIONS))
    operations = _string_list(operations, "operations", allow_empty=False)
    unknown = sorted(set(operations) - set(OPERATIONS))
    if unknown:
        raise IndicatorSetError(
            f"operations has unknown entries {unknown}; allowed: {list(OPERATIONS)}"
        )
    indicators = "indicators" in operations
    names = settings.get("indicator_sets", [DEFAULT_SET])
    names = _string_list(names, "indicator_sets", allow_empty=not indicators)
    for name in names:
        validate_id(name, "indicator set")
    definitions = settings.get("indicator_set_definitions", {})
    if not isinstance(definitions, dict):
        raise IndicatorSetError("indicator_set_definitions must be a mapping")
    for name, entry in definitions.items():
        validate_id(name, "indicator_set_definitions key")
        if name == DEFAULT_SET or (BUNDLED_ROOT / f"{name}.yml").is_file():
            raise IndicatorSetError(
                f"custom indicator set {name!r} collides with a bundled set"
            )
        if (
            not isinstance(entry, dict)
            or set(entry) != {"config_path"}
            or not isinstance(entry["config_path"], str)
            or not entry["config_path"]
        ):
            raise IndicatorSetError(
                f"indicator_set_definitions.{name} must be exactly {{config_path: <nonempty string>}}"
            )
    ordered = tuple(item for item in OPERATIONS if item in operations)
    if not indicators:
        return Selection(ordered, (), legacy=False)
    base = Path(workflow_path).resolve().parent
    sources = []
    for name in names:
        if name in definitions:
            path = Path(definitions[name]["config_path"])
            path = (path if path.is_absolute() else base / path).resolve()
            bundled = False
        else:
            path = BUNDLED_ROOT / f"{name}.yml"
            bundled = True
            if not path.is_file():
                raise IndicatorSetError(
                    f"unknown indicator set {name!r}: not bundled under "
                    f"{BUNDLED_ROOT.as_posix()} and not in indicator_set_definitions"
                )
        try:
            text = path.read_text(encoding="utf-8")
        except OSError as exc:
            raise IndicatorSetError(
                f"indicator set {name!r}: cannot read {path}: {exc}"
            ) from exc
        sources.append(SetSource(name, path, bundled, text))
    return Selection(ordered, tuple(sources), legacy=False)


def legacy_selection(settings: dict) -> Selection:
    """Map the scalar ``operation`` interface onto operations and the default set."""
    operation = settings.get("operation")
    if operation == "simulate-and-metrics":
        operations = ("simulations", "indicators")
    elif operation in ("metrics-only", None):
        # Absent only in metrics-only projections that never read it.
        operations = ("indicators",)
    else:
        raise IndicatorSetError(f"unsupported legacy operation {operation!r}")
    path = BUNDLED_ROOT / f"{DEFAULT_SET}.yml"
    return Selection(
        operations,
        (SetSource(DEFAULT_SET, path, True, path.read_text(encoding="utf-8")),),
        legacy=True,
    )


@dataclass(frozen=True)
class ResolvedIndicator:
    """One selected indicator: numerical declaration plus presentation."""

    declaration: registry.MetricDeclaration
    definition: str
    method: str
    parameters: dict
    title: str
    description: str
    references: tuple[str, ...]
    authored_references: tuple[str, ...]
    equivalent_definition: str

    @property
    def metric(self) -> str:
        return self.declaration.name


@dataclass(frozen=True)
class ResolvedSet:
    """A validated set: identity-relevant declarations and publication metadata."""

    set_id: str
    title: str
    description: str
    source: SetSource
    indicators: tuple[ResolvedIndicator, ...]

    @property
    def declarations(self) -> tuple[registry.MetricDeclaration, ...]:
        return tuple(item.declaration for item in self.indicators)


def _registered(definition: str) -> ResolvedIndicator:
    method, parameters, _ = registry.DEFINITIONS[definition]
    title, description = registry.DEFINITION_TEXT[definition]
    return ResolvedIndicator(
        declaration=registry.declaration_for(definition),
        definition=definition,
        method=method,
        parameters=dict(sorted(parameters.items())),
        title=title,
        description=description,
        references=registry.DEFINITION_REFERENCES.get(definition, ()),
        authored_references=(),
        equivalent_definition="",
    )


def _authored(entry: dict, label: str) -> ResolvedIndicator:
    expected = {"id", "title", "description", "references", "calculation"}
    if set(entry) != expected:
        raise IndicatorSetError(
            f"{label}: an authored entry has exactly {sorted(expected)}; "
            f"got {sorted(entry)}"
        )
    metric = validate_id(entry["id"], f"{label} id")
    if metric in registry.DEFINITIONS:
        raise IndicatorSetError(
            f"{label}: authored id {metric!r} equals a registered definition; "
            "select it with {definition: ...} instead"
        )
    for field in ("title", "description"):
        if not isinstance(entry[field], str):
            raise IndicatorSetError(f"{label}: {field} must be a string")
    references = entry["references"]
    if not isinstance(references, list) or any(
        not isinstance(item, str) or not item for item in references
    ):
        raise IndicatorSetError(
            f"{label}: references must be a list of nonempty strings"
        )
    calculation = entry["calculation"]
    if not isinstance(calculation, dict) or set(calculation) != {
        "method",
        "parameters",
    }:
        raise IndicatorSetError(
            f"{label}: calculation is exactly {{method, parameters}}"
        )
    try:
        definition, parameters = registry.validate_calculation(
            calculation["method"], calculation["parameters"]
        )
    except ValueError as exc:
        raise IndicatorSetError(f"{label}: {exc}") from exc
    return ResolvedIndicator(
        declaration=replace(registry.declaration_for(definition), name=metric),
        definition=definition,
        method=calculation["method"],
        parameters=parameters,
        title=entry["title"],
        description=entry["description"],
        references=registry.DEFINITION_REFERENCES.get(definition, ()),
        authored_references=tuple(references),
        equivalent_definition=definition,
    )


def resolve_set(
    source: SetSource, default_tokens=None, *, legacy: bool = False
) -> ResolvedSet:
    """Validate one captured set file and resolve its entries.

    ``default_tokens`` are the response variables the ``current_default``
    preset expands; they are required only by a set using the preset. Legacy
    mode keeps the old ``metrics: []`` behaviour of an empty selection.
    """
    label = f"indicator set {source.set_id!r} ({source.path.as_posix()})"
    try:
        document = load_unique_yaml(source.text)
    except yaml.YAMLError as exc:
        raise IndicatorSetError(f"{label}: invalid YAML: {exc}") from exc
    expected = {"schema_version", "id", "title", "description", "selection"}
    if not isinstance(document, dict) or set(document) != expected:
        raise IndicatorSetError(
            f"{label}: a set file has exactly {sorted(expected)}"
            + ("" if not isinstance(document, dict) else f"; got {sorted(document)}")
        )
    if (
        document["schema_version"] != SET_SCHEMA_VERSION
        or type(document["schema_version"]) is not int
    ):
        raise IndicatorSetError(f"{label}: schema_version must be {SET_SCHEMA_VERSION}")
    if document["id"] != source.set_id:
        raise IndicatorSetError(
            f"{label}: id {document['id']!r} differs from its selected name"
        )
    if not isinstance(document["title"], str) or not document["title"]:
        raise IndicatorSetError(f"{label}: title must be a nonempty string")
    if not isinstance(document["description"], str):
        raise IndicatorSetError(f"{label}: description must be a string")
    selection = document["selection"]
    if not isinstance(selection, dict) or len(selection) != 1:
        raise IndicatorSetError(
            f"{label}: selection is exactly one of preset or indicators"
        )
    ((kind, value),) = selection.items()
    if kind == "preset":
        if value != DEFAULT_PRESET or not (
            source.bundled and source.set_id == DEFAULT_SET
        ):
            raise IndicatorSetError(
                f"{label}: only the bundled default set may use preset {DEFAULT_PRESET}"
            )
        if default_tokens is None or (not default_tokens and not legacy):
            raise IndicatorSetError(
                f"{label}: the default preset expanded to no response variables"
            )
        indicators = [
            _registered(item.name) for item in registry.declarations(default_tokens)
        ]
    elif kind == "indicators":
        if not isinstance(value, list) or not value:
            raise IndicatorSetError(f"{label}: indicators must be a nonempty list")
        indicators = []
        for number, entry in enumerate(value, 1):
            entry_label = f"{label} entry {number}"
            if not isinstance(entry, dict):
                raise IndicatorSetError(f"{entry_label}: must be a mapping")
            if "definition" in entry:
                if set(entry) != {"definition"}:
                    raise IndicatorSetError(
                        f"{entry_label}: a definition selector has no overrides; got {sorted(entry)}"
                    )
                if entry["definition"] not in registry.DEFINITIONS:
                    raise IndicatorSetError(
                        f"{entry_label}: unknown registered definition {entry['definition']!r}"
                    )
                indicators.append(_registered(entry["definition"]))
            else:
                indicators.append(_authored(entry, entry_label))
    else:
        raise IndicatorSetError(f"{label}: unknown selection kind {kind!r}")
    metrics, contracts = {}, {}
    for item in indicators:
        if item.metric in metrics:
            raise IndicatorSetError(f"{label}: repeats metric {item.metric!r}")
        metrics[item.metric] = item
        if item.definition in contracts:
            raise IndicatorSetError(
                f"{label}: {contracts[item.definition]!r} and {item.metric!r} share one "
                f"calculation contract ({item.definition})"
            )
        contracts[item.definition] = item.metric
    return ResolvedSet(
        source.set_id,
        document["title"],
        document["description"],
        source,
        tuple(indicators),
    )


def default_tokens(
    project: dict, *, simulation_path: bool, retained_variables
) -> list[str]:
    """Response variables the new-mode ``current_default`` preset expands.

    ``model.outvars`` when it is a nonempty list; absent, the toolbox defaults on
    a simulation path or the retained response variables on indicator-only.
    Explicit null or an empty list is refused rather than normalized.
    ``retained_variables`` is a callable, read only when consulted.
    """
    from blueearth_cst.shared.indicator_tables import indicator_tables
    from blueearth_cst.shared.snake_utils import DEFAULT_WFLOW_OUTVARS

    model = project.get("model") or {}
    if "outvars" in model:
        outvars = model["outvars"]
        if not isinstance(outvars, list) or not outvars:
            raise IndicatorSetError(
                "the default indicator set needs model.outvars as a nonempty list "
                f"(got {outvars!r}); remove the key to use the defaults"
            )
        return list(indicator_tables(outvars))
    if simulation_path:
        return list(indicator_tables(DEFAULT_WFLOW_OUTVARS))
    return list(retained_variables())


def legacy_tokens(
    project: dict, settings: dict, context: str, retained_variables
) -> list[str]:
    """Legacy ``metrics``/``outvars`` precedence, preserved per observed branch.

    The three pre-named-set branches disagree on null/absent values; each
    expression is kept verbatim rather than normalized (design v3, P3/O5).
    ``context`` is ``simulation_rule``, ``metrics_only`` or ``export``.
    """
    from blueearth_cst.shared.indicator_tables import indicator_tables
    from blueearth_cst.shared.snake_utils import DEFAULT_WFLOW_OUTVARS

    model = project.get("model") or {}
    if context == "simulation_rule":
        return list(
            settings.get(
                "metrics", indicator_tables(model.get("outvars", DEFAULT_WFLOW_OUTVARS))
            )
        )
    tokens = settings.get("metrics")
    if tokens is not None:
        return list(tokens)
    outvars = model.get("outvars")
    if context == "metrics_only":
        if outvars is not None:
            return list(indicator_tables(outvars))
        return list(retained_variables())
    if context == "export":
        if outvars is not None or settings["operation"] == "simulate-and-metrics":
            return list(
                indicator_tables(DEFAULT_WFLOW_OUTVARS if outvars is None else outvars)
            )
        return list(retained_variables())
    raise ValueError(f"unknown legacy token context {context!r}")


#: Environment variable naming the runner's captured selection snapshot, so
#: every Snakemake parse/job process uses the bytes admitted at start.
SNAPSHOT_ENV = "CST_INDICATOR_SELECTION"


def write_selection_snapshot(selection: Selection, path: Path) -> Path:
    """Persist the admitted set sources (paths and exact text) for this invocation."""
    import json

    payload = {
        "schema_version": "indicator-selection/1",
        "operations": list(selection.operations),
        "legacy": selection.legacy,
        "sets": [
            {
                "set_id": item.set_id,
                "path": item.path.as_posix(),
                "bundled": item.bundled,
                "text": item.text,
            }
            for item in selection.sets
        ],
    }
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=1, sort_keys=True), encoding="utf-8")
    return path


def read_selection_snapshot(path) -> Selection:
    """Read a snapshot written by :func:`write_selection_snapshot`."""
    import json

    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if payload.get("schema_version") != "indicator-selection/1":
        raise IndicatorSetError(f"unsupported indicator selection snapshot {path}")
    return Selection(
        tuple(payload["operations"]),
        tuple(
            SetSource(item["set_id"], Path(item["path"]), item["bundled"], item["text"])
            for item in payload["sets"]
        ),
        legacy=payload["legacy"],
    )


def workflow_selection(settings: dict, workflow_path) -> Selection:
    """The invocation's selection: the runner snapshot when present, else live."""
    import os

    snapshot = os.environ.get(SNAPSHOT_ENV)
    if snapshot:
        return read_selection_snapshot(snapshot)
    if uses_named_selection(settings):
        return parse_selection(settings, workflow_path)
    return legacy_selection(settings)


def selected_sets(
    project: dict,
    settings: dict,
    selection: Selection,
    *,
    simulation_path: bool,
    retained_variables,
    legacy_context: str,
) -> tuple[ResolvedSet, ...]:
    """Resolve every selected set, expanding the default preset by mode.

    ``retained_variables`` is a callable; ``legacy_context`` names the legacy
    branch (see :func:`legacy_tokens`) whose precedence applies.
    """
    resolved = []
    for source in selection.sets:
        tokens = None
        if source.bundled and source.set_id == DEFAULT_SET:
            tokens = (
                legacy_tokens(project, settings, legacy_context, retained_variables)
                if selection.legacy
                else default_tokens(
                    project,
                    simulation_path=simulation_path,
                    retained_variables=retained_variables,
                )
            )
        resolved.append(resolve_set(source, tokens, legacy=selection.legacy))
    return tuple(resolved)


def calculation_records(indicators) -> list[dict]:
    """Identity-relevant calculation records, canonically sorted by metric key.

    Presentation (titles, descriptions, citations), set id, source path and
    selection order are excluded; the metric key, method, normalized parameters
    and resolved registered calculation are retained by value.
    """
    return sorted(
        (
            {
                "metric": item.metric,
                "definition": item.definition,
                "method": item.method,
                "parameters": dict(sorted(item.parameters.items())),
            }
            for item in indicators
        ),
        key=lambda record: record["metric"],
    )


def default_calculations(tokens) -> list[dict]:
    """Calculation records of the registered default suite for ``tokens``."""
    return calculation_records(
        _registered(item.name) for item in registry.declarations(tokens)
    )


def declarations_for_calculations(records) -> tuple[registry.MetricDeclaration, ...]:
    """Re-derive declarations from retained calculation records against live code.

    Each record's method and parameters are re-validated, so a changed
    parameter-to-reducer mapping is observed rather than trusted.
    """
    result = []
    for record in records:
        if set(record) != {"metric", "definition", "method", "parameters"}:
            raise IndicatorSetError(f"invalid calculation record {record!r}")
        definition, _ = registry.validate_calculation(
            record["method"], record["parameters"]
        )
        if definition != record["definition"]:
            raise IndicatorSetError(
                f"{record['metric']}: calculation now resolves to {definition!r}, "
                f"not the recorded {record['definition']!r}"
            )
        result.append(
            replace(registry.declaration_for(definition), name=record["metric"])
        )
    return tuple(result)


def required_variables(sets) -> list[str]:
    """Union of response variables the resolved sets need, in first-use order."""
    seen = {}
    for item in sets:
        for declaration in item.declarations:
            seen.setdefault(declaration.required_responses.variable, None)
    return list(seen)
