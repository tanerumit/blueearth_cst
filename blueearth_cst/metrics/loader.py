"""Discover trusted installed sets and orchestrate their local callables."""

import hashlib
import importlib
import inspect
import pkgutil
from dataclasses import replace
from functools import lru_cache
from pathlib import Path

import numpy as np
import pandas as pd

from blueearth_cst.metrics import sets
from blueearth_cst.metrics.contract import (
    EvaluationContext,
    MetricDeclaration,
    MetricResult,
)
from blueearth_cst.metrics.temporal import validate_requirement
from blueearth_cst.metrics.validation import validate_parameters, validate_result


def available_sets() -> tuple[str, ...]:
    """List installed trusted packages; YAML cannot name an arbitrary import path."""
    return tuple(
        sorted(item.name for item in pkgutil.iter_modules(sets.__path__) if item.ispkg)
    )


def load(set_id: str):
    """Load one discovered package's set-owned registration module."""
    if set_id not in available_sets():
        raise ValueError(
            f"unknown metric set {set_id!r}; discoverable sets: {list(available_sets())}"
        )
    return importlib.import_module(f"{sets.__name__}.{set_id}.registry")


load_set = load


def execution_sources(set_ids=None) -> tuple[Path, ...]:
    """Return execution-only sources; optional checking code has its own identity."""
    root = Path(__file__).parent
    selected = available_sets() if set_ids is None else set_ids
    paths = list(root.glob("*.py"))
    paths += [root / "sets" / "__init__.py"]
    for set_id in selected:
        registry = load(set_id)
        paths += list(Path(registry.__file__).parent.glob("*.py"))
        pending, visited = [registry], set()
        while pending:
            module = pending.pop()
            if module.__name__ in visited:
                continue
            visited.add(module.__name__)
            if module.__file__:
                paths.append(Path(module.__file__))
            pending.extend(
                value
                for value in vars(module).values()
                if inspect.ismodule(value)
                and value.__name__.startswith(f"{sets.__name__}.")
            )
        for metric in registry.METRICS:
            path = inspect.getsourcefile(metric.calculate)
            if path:
                paths.append(Path(path))
    return tuple(
        sorted(
            {p.resolve() for p in paths if p.name not in {"checks.py", "checking.py"}}
        )
    )


def implementation_revision(set_id: str) -> str:
    """Content identity of the contributing execution sources, without checkers."""
    paths = execution_sources([set_id])
    signature = tuple(
        (str(path), path.stat().st_mtime_ns, path.stat().st_size) for path in paths
    )
    return _source_revision(signature)


@lru_cache(maxsize=32)
def _source_revision(signature) -> str:
    """Reuse source-byte hashing while the actual file identities remain unchanged."""
    digest = hashlib.sha256()
    root = Path(__file__).parent
    for name, _, _ in signature:
        path = Path(name)
        try:
            relative = path.relative_to(root)
        except ValueError:
            relative = Path(*path.parts[-2:])
        digest.update(str(relative).replace("\\", "/").encode())
        digest.update(path.read_text(encoding="utf-8").encode("utf-8"))
    return digest.hexdigest()


def _declaration(set_id, metric, *, name=None, parameters=None) -> MetricDeclaration:
    params = dict(metric.parameters if parameters is None else parameters)
    module = importlib.import_module(metric.calculate.__module__)
    try:
        params = validate_parameters(metric.calculate, params, module.PARAMETERS)
        if hasattr(module, "validate"):
            module.validate(metric.calculate, params)
    except (ValueError, TypeError) as error:
        raise ValueError(f"{set_id}/{name or metric.id}: {error}") from error
    methods = load(set_id).METHODS
    method = metric.method or next(
        (key for key, fn in methods.items() if fn is metric.calculate),
        metric.calculate.__name__,
    )
    period = params.get("return_period", metric.return_period)
    return MetricDeclaration(
        name=name or metric.id,
        statistic=metric.statistic,
        grain=metric.grain,
        required_responses=metric.input,
        bundle_by="same_design_point" if metric.grain == "bundle" else None,
        reference=metric.reference,
        reference_location=metric.reference_location,
        return_period=period,
        blocks_per_return_period=metric.blocks_per_return_period,
        implementation_revision=implementation_revision(set_id),
        value_validity="finite required; reject invalid GEV fit; no clipping"
        if metric.grain == "bundle"
        else "finite or native-reduction NaN; refuse infinity; no clipping",
        group_reduction=metric.group_reduction,
        calculation_set=set_id,
        calculation_method=method,
        calculation_parameters=params,
    )


def declarations(set_id: str) -> tuple[MetricDeclaration, ...]:
    """Resolve all registrations without central calculation inventory edits."""
    return tuple(_declaration(set_id, item) for item in load(set_id).METRICS)


def resolve(
    set_id: str, method: str, parameters, *, metric_name=None
) -> MetricDeclaration:
    """Validate a local callable and return its resolved declaration."""
    identity = f"{set_id}/{metric_name or method}"
    registry = load(set_id)
    functions = dict(registry.METHODS)
    functions.update(
        {item.calculate.__name__: item.calculate for item in registry.METRICS}
    )
    if method not in functions:
        raise ValueError(
            f"{identity}: unknown calculation {method!r}; accepted calculations: {sorted(functions)}"
        )
    function = functions[method]
    module = importlib.import_module(function.__module__)
    try:
        if hasattr(module, "normalize_parameters"):
            parameters = module.normalize_parameters(function, parameters)
        normalized = validate_parameters(function, parameters, module.PARAMETERS)
        if hasattr(module, "validate"):
            module.validate(function, normalized)
        candidates = [item for item in registry.METRICS if item.calculate is function]
        exact = [item for item in candidates if dict(item.parameters) == normalized]
        if exact:
            template = exact[0]
        elif len(candidates) == 1:
            template = candidates[0]
        elif hasattr(registry, "resolve_metric"):
            template = registry.resolve_metric(function, normalized)
        else:
            raise ValueError(
                f"no unambiguous declaration matches parameters {normalized!r}"
            )
        return _declaration(set_id, template, name=metric_name, parameters=normalized)
    except (ValueError, TypeError) as error:
        raise ValueError(f"{identity}: {error}") from error


def local_declaration(metric: MetricDeclaration) -> MetricDeclaration:
    """Adapt the legacy registry's vocabulary without making it a dependency."""
    if metric.calculation_set:
        return metric
    for set_id in available_sets():
        for item in load(set_id).METRICS:
            if (item.statistic, item.input.variable) == (
                metric.statistic,
                metric.required_responses.variable,
            ):
                candidate = _declaration(set_id, item)
                return replace(
                    candidate,
                    name=metric.name,
                    implementation_revision=metric.implementation_revision,
                    reference=metric.reference,
                    reference_location=metric.reference_location,
                    group_reduction=metric.group_reduction,
                    return_period=metric.return_period,
                    blocks_per_return_period=metric.blocks_per_return_period,
                )
    raise ValueError(
        f"legacy/{metric.name}: no set-local calculation for statistic {metric.statistic!r}"
    )


def registration(metric: MetricDeclaration):
    """Return the set-owned registration supplying units and descriptive text."""
    metric = local_declaration(metric)
    entries = load(metric.calculation_set).METRICS
    matches = [item for item in entries if item.id == metric.name]
    if not matches:
        matches = [
            item
            for item in entries
            if dict(item.parameters) == metric.calculation_parameters
            and (item.method or item.calculate.__name__)
            in {metric.calculation_method, metric.calculation_method.split("/")[0]}
        ]
    if not matches:
        matches = [
            item
            for item in entries
            if (item.method or item.calculate.__name__)
            in {metric.calculation_method, metric.calculation_method.split("/")[0]}
        ]
    if not matches:
        raise ValueError(
            f"{metric.calculation_set}/{metric.name}: no local registration"
        )
    return matches[0]


def evaluate(
    metric,
    series,
    *,
    anchor,
    reference=None,
    expected_run_ids=None,
    validation=None,
    group=False,
) -> MetricResult:
    """Evaluate locations or member groups; unexpected calculation faults propagate."""
    metric = local_declaration(metric)
    identity = f"{metric.calculation_set}/{metric.name}"
    registry = load(metric.calculation_set)
    function = registry.METHODS.get(metric.calculation_method)
    if function is None:
        function = next(
            item.calculate
            for item in registry.METRICS
            if item.calculate.__name__ == metric.calculation_method
        )
    members = tuple(
        sorted({item.run_id for item in series})
        if expected_run_ids is None
        else expected_run_ids
    )
    context = EvaluationContext(anchor, reference, members, validation)
    try:
        offset = pd.tseries.frequencies.to_offset(anchor)
        if not offset.freqstr.startswith(("YE-", "YS-")) or offset.n != 1:
            raise ValueError(
                "anchor: expected a one-year water-year frequency such as YE-DEC or YE-SEP"
            )
        validate_requirement(metric, series)
        if group and metric.grain == "run":
            if metric.group_reduction != "equal-weight-run-reductions-propagate-nan/1":
                raise ValueError("no reviewed group mean policy")
            if (
                not members
                or len(set(members)) != len(members)
                or set(members) != {item.run_id for item in series}
            ):
                raise ValueError(
                    "group membership requires unique evaluated members matching the declaration"
                )
            results = [
                evaluate(
                    metric,
                    [item for item in series if item.run_id == run],
                    anchor=anchor,
                    reference=reference,
                    validation=validation,
                )
                for run in members
            ]
            if any(
                set(item.values.index) != set(results[0].values.index)
                for item in results
            ):
                raise ValueError("group location sets differ")
            values = pd.Series(
                np.mean(
                    np.stack(
                        [
                            item.values.reindex(results[0].values.index).to_numpy()
                            for item in results
                        ]
                    ),
                    axis=0,
                ),
                index=results[0].values.index,
            )
            result = MetricResult(values, metadata={"member_run_ids": members})
        else:
            result = function(metric, series, context)
        validate_result(result)
    except Exception as error:
        locations = sorted({item.location_id for item in series})
        # Preserve exception type, evidence attributes, cause and traceback.
        error.args = (f"{identity}/location={locations}: {error}", *error.args[1:])
        raise
    statuses = result.statuses or {
        str(location): "undefined" if pd.isna(value) else "available"
        for location, value in result.values.items()
    }
    return replace(result, statuses=statuses)


def check(
    metric,
    series,
    result,
    *,
    anchor,
    reference=None,
    expected_run_ids=None,
    validation=None,
    group=False,
) -> dict:
    """Delegate numerical checking lazily, outside execution source identity."""
    from blueearth_cst.metrics.checking import check as numerical_check

    return numerical_check(
        metric,
        series,
        result,
        anchor=anchor,
        reference=reference,
        expected_run_ids=expected_run_ids,
        validation=validation,
        group=group,
    )
