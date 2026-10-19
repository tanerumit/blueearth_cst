"""Shared output paths must keep the same producer across workflow invocations."""

import asyncio
from collections import defaultdict
from itertools import combinations
from pathlib import Path
from types import SimpleNamespace

import pytest

from blueearth_cst.shared.config_composition import load_composed_config
from tests.conftest import write_config
from tests.test_climate_store_contract import _COMPARED, _parse_workflow

CONFIG_FN = Path(__file__).with_name("project_config_fixture.yml")
pytestmark = pytest.mark.workflow_contract


@pytest.mark.parametrize(
    "snakefile",
    [
        "analyze_climate.smk",
        "build_model.smk",
        "analyze_projections.smk",
        "generate_scenarios.smk",
    ],
)
def test_workflow_defers_header_and_summarizes_requested_outputs(
    snakefile, monkeypatch, capsys
):
    from blueearth_cst.shared import console_style

    if snakefile == "analyze_projections.smk":
        from blueearth_cst.projections import reference_window

        monkeypatch.setattr(reference_window, "SHORT_WINDOW_YEARS", 30)
    monkeypatch.setattr(console_style, "_DEFERRED_WARNINGS", [])
    capsys.readouterr()
    workflow = _parse_workflow(snakefile, CONFIG_FN)
    parsed = capsys.readouterr()
    if snakefile == "analyze_projections.smk":
        assert "Reference period is short" not in parsed.out + parsed.err
        assert any(
            "Reference period is short" in row[2]
            for row in console_style._DEFERRED_WARNINGS
        )
    monkeypatch.setattr(console_style, "_CONSOLE_STYLE_ACTIVE", True)
    monkeypatch.setattr(console_style, "_RUN_HEADER", None)
    capsys.readouterr()
    workflow.globals["_header"]()
    captured = capsys.readouterr()
    assert captured.out == captured.err == ""
    details = console_style._RUN_HEADER[3]
    if snakefile == "analyze_climate.smk":
        assert "forcing:" in details["sources"]
        assert details["extraction"]
        assert "reporting year starts in" in details["reference"]
    elif snakefile == "build_model.smk":
        assert details["forcing"]
        assert details["simulation"]
        assert details["resolution"]

    rule = workflow.get_rule("all")
    count = len(rule.input)
    assert rule.message == f"Requested outputs: {count}/{count} provided"


def _differences(left, right):
    """Compare the existing exhaustive directive contract, allowing fan-out names."""
    return [
        field
        for field, extract in _COMPARED.items()
        if field != "name" and extract(*left) != extract(*right)
    ]


def _resolved_annotation_params(rule):
    """Resolve WF2's series-key lambdas instead of comparing function addresses."""
    values = []
    for value in rule.params:
        if callable(value):
            series = value.__globals__["SERIES"]
            values.append(
                {key: value(SimpleNamespace(series_key=key)) for key in sorted(series)}
            )
        else:
            values.append(value)
    return values


@pytest.mark.parametrize(
    "snakefile,plot_rules",
    [
        (
            "analyze_climate.smk",
            {
                "plot_climate_diagnostics_era5",
                "plot_climate_diagnostics_chirps",
                "plot_climate_comparison",
            },
        ),
        (
            "build_model.smk",
            {
                "plot_basin_map",
                "plot_model_forcing",
                "plot_model_evaluation",
            },
        ),
        ("analyze_projections.smk", {"plot_climate_projections"}),
    ],
)
def test_annotation_changes_only_plot_rule_parameters(tmp_path, snakefile, plot_rules):
    """Presentation edits keep every upstream input/output/parameter unchanged."""
    cfg = load_composed_config(CONFIG_FN)
    cfg["climate"]["sources"] = ["era5", "chirps"]
    path = write_config(tmp_path, cfg)
    original = _parse_workflow(snakefile, path)
    originals = {rule.name: rule for rule in original.rules}
    for mode in ("caption", "title"):
        cfg["plotting"] = {"annotation": mode}
        write_config(tmp_path, cfg)
        changed = _parse_workflow(snakefile, path)
        changed_rules = set()
        for rule in changed.rules:
            differences = _differences(
                (original, originals[rule.name]), (changed, rule)
            )
            if "params" in differences and _resolved_annotation_params(
                originals[rule.name]
            ) == _resolved_annotation_params(rule):
                differences.remove("params")
            if differences:
                assert differences == ["params"], (rule.name, differences)
                assert rule.params.annotation == mode
                changed_rules.add(rule.name)
        assert changed_rules == plot_rules


@pytest.mark.parametrize("source", ["era5", "chirps", "chirps_global"])
def test_wf0_exclusively_owns_source_diagnostics_at_store_root(tmp_path, source):
    cfg = load_composed_config(CONFIG_FN)
    cfg["climate"]["selected"] = source
    cfg["climate"]["sources"] = [source]
    path = write_config(tmp_path, cfg)
    wf0 = _parse_workflow("analyze_climate.smk", path)
    wf1 = _parse_workflow("build_model.smk", path)
    canonical = wf0.get_rule(f"plot_climate_diagnostics_{source}")
    assert "plot_climate_datasets" not in {rule.name for rule in wf1.rules}
    store = Path(
        wf0.get_rule(f"extract_climate_datasets_{source}").output.climate_nc
    ).parent
    assert all(Path(p).is_relative_to(store) for p in canonical.output)
    assert not any(
        "diagnostics" in Path(p).relative_to(store).parts for p in canonical.output
    )
    assert all(
        Path(p).parent == store / "plots"
        for p in canonical.output
        if str(p).endswith(".png")
    )
    assert not any(
        Path(p).is_relative_to(store / "plots")
        for rule in wf1.rules
        for p in rule.output
    )
    assert not any(p.is_directory for p in canonical.output)


def test_all_shared_outputs_have_equivalent_producers():
    """Discover overlaps across WF0–WF3, including future plot rules.

    WF4 consumes a published collection and owns experiment-local outputs;
    parsing it requires that collection and is covered by its lifecycle tests.
    """
    owners = defaultdict(list)
    for snakefile in (
        "analyze_climate.smk",
        "build_model.smk",
        "analyze_projections.smk",
        "generate_scenarios.smk",
    ):
        workflow = _parse_workflow(snakefile, CONFIG_FN)
        for rule in workflow.rules:
            for output in rule.output:
                owners[str(output)].append((workflow, rule))
    shared = {path: entries for path, entries in owners.items() if len(entries) > 1}
    assert any(path.endswith("extract_historical.nc") for path in shared)
    failures = []
    for path, entries in shared.items():
        for left, right in combinations(entries, 2):
            differences = _differences(left, right)
            if differences:
                failures.append((path, left[1].name, right[1].name, differences))
    assert not failures, failures


def test_repeated_wf0_diagnostics_preserve_provenance_but_detect_changes(tmp_path):
    """Repeated source plotting preserves metadata; changed presentation invalidates."""
    from snakemake.api import DAGSettings, ExecutionSettings
    from snakemake.io import IOCache
    from snakemake.jobs import Job
    from snakemake.persistence import Persistence

    cfg = load_composed_config(CONFIG_FN)
    cfg["project"]["project_dir"] = (tmp_path / "project").as_posix()
    cfg["climate"]["water_year_start"] = "Jan"
    path = write_config(tmp_path, cfg)
    jobs = []
    for snakefile, name in (
        ("analyze_climate.smk", "plot_climate_diagnostics_era5"),
        ("analyze_climate.smk", "plot_climate_diagnostics_era5"),
    ):
        workflow = _parse_workflow(snakefile, path)
        workflow.execution_settings = ExecutionSettings()
        workflow.dag_settings = DAGSettings()
        workflow.iocache = IOCache(0)
        jobs.append(
            Job(workflow.get_rule(name), SimpleNamespace(workflow=workflow), {})
        )
    persistence = Persistence(path=tmp_path / "metadata", dag=jobs[0].dag)
    for previous, current in ((jobs[0], jobs[1]), (jobs[1], jobs[0])):
        asyncio.run(persistence.finished(previous))
        # Each invocation opens a fresh metadata reader; Snakemake caches reads
        # within an invocation, including the pre-completion empty record.
        persistence = Persistence(path=tmp_path / "metadata", dag=current.dag)
        assert persistence.record_format_version(previous.output[0]) is not None
        assert previous.params.m0 == 1
        assert not list(persistence.input_changed(current))
        assert not persistence.params_changed(current)
        assert not list(persistence.code_changed(current))
        assert not list(persistence.software_stack_changed(current))
    # A genuine presentation change must still invalidate the saved job.
    cfg["climate"]["water_year_start"] = "Oct"
    path = write_config(tmp_path / "changed", cfg)
    workflow = _parse_workflow("analyze_climate.smk", path)
    workflow.execution_settings = ExecutionSettings()
    workflow.dag_settings = DAGSettings()
    changed = Job(
        workflow.get_rule("plot_climate_diagnostics_era5"),
        SimpleNamespace(workflow=workflow),
        {},
    )
    assert changed.params.m0 == 10
    assert persistence.params_changed(changed), (
        persistence.params(changed.output[0]),
        list(changed.non_derived_params),
    )
