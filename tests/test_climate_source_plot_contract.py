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


def _differences(left, right):
    """Compare the existing exhaustive directive contract, allowing fan-out names."""
    return [
        field
        for field, extract in _COMPARED.items()
        if field != "name" and extract(*left) != extract(*right)
    ]


@pytest.mark.parametrize("source", ["era5", "chirps", "chirps_global"])
def test_selected_source_plot_declarations_are_identical(tmp_path, source):
    """Single and multi-source WF0 runs reuse WF1's complete figure contract."""
    cfg = load_composed_config(CONFIG_FN)
    cfg["climate"]["selected"] = source
    cfg["climate"]["sources"] = [source]
    single = write_config(tmp_path / "single", cfg)
    wf1 = _parse_workflow("build_model.smk", single)
    reference = (wf1, wf1.get_rule("plot_climate_datasets"))
    for sources in ([source], list(dict.fromkeys([source, "era5", "chirps"]))):
        cfg["climate"]["sources"] = sources
        path = write_config(tmp_path / f"sources_{len(sources)}", cfg)
        wf0 = _parse_workflow("analyze_climate.smk", path)
        rule = wf0.get_rule(f"plot_climate_datasets_{source}")
        assert not _differences((wf0, rule), reference)
        assert "scales_json" not in rule.input.keys()
        assert {str(p) for p in rule.output if p.is_directory} == {
            str(p) for p in reference[1].output if p.is_directory
        }


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
    assert any(path.endswith(".png") for path in shared)
    failures = []
    for path, entries in shared.items():
        for left, right in combinations(entries, 2):
            differences = _differences(left, right)
            if differences:
                failures.append((path, left[1].name, right[1].name, differences))
    assert not failures, failures


def test_alternating_workflows_preserves_provenance_but_detects_changes(tmp_path):
    """Exercise Snakemake's saved metadata through WF0 → WF1 → WF0."""
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
        ("analyze_climate.smk", "plot_climate_datasets_era5"),
        ("build_model.smk", "plot_climate_datasets"),
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
        assert previous.params.water_year_start == "Jan"
        assert not list(persistence.input_changed(current))
        assert not persistence.params_changed(current)
        assert not list(persistence.code_changed(current))
        assert not list(persistence.software_stack_changed(current))
    # A genuine presentation change must still invalidate the saved job.
    cfg["climate"]["water_year_start"] = "Oct"
    path = write_config(tmp_path / "changed", cfg)
    workflow = _parse_workflow("build_model.smk", path)
    workflow.execution_settings = ExecutionSettings()
    workflow.dag_settings = DAGSettings()
    changed = Job(
        workflow.get_rule("plot_climate_datasets"),
        SimpleNamespace(workflow=workflow),
        {},
    )
    assert changed.params.water_year_start == "Oct"
    assert persistence.params_changed(changed), (
        persistence.params(changed.output[0]),
        list(changed.non_derived_params),
    )
