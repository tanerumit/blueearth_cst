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
def test_wf0_owns_diagnostics_and_wf1_retains_source_plots(tmp_path, source):
    cfg = load_composed_config(CONFIG_FN)
    cfg["climate"]["selected"] = source
    cfg["climate"]["sources"] = [source]
    path = write_config(tmp_path, cfg)
    wf0 = _parse_workflow("analyze_climate.smk", path)
    wf1 = _parse_workflow("build_model.smk", path)
    canonical = wf0.get_rule(f"plot_climate_diagnostics_{source}")
    previous = wf1.get_rule("plot_climate_datasets")
    assert set(map(str, canonical.output)).isdisjoint(map(str, previous.output))
    assert all("/diagnostics/" in str(p).replace("\\", "/") for p in canonical.output)
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


def test_repeated_wf1_source_plots_preserve_provenance_but_detect_changes(tmp_path):
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
        ("build_model.smk", "plot_climate_datasets"),
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
