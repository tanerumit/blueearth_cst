"""Exact request plans cannot select nearby collections or certify stale inputs."""

from copy import deepcopy

import pytest

from blueearth_cst.experiment.collection_resolution import (
    GeneratedCollectionStale,
    GeneratedCollectionUnavailable,
    resolve_explicit_collection,
    resolve_project_collection,
    scenario_request,
    verify_scenario_request,
    write_scenario_request,
)
from blueearth_cst.experiment.content_identity import (
    content_sha256,
    read_canonical_json,
)
from blueearth_cst.experiment.scenario_collection import publish_collection
from tests.test_scenario_collection import CHECKS, planned  # noqa: F401


@pytest.fixture
def ready_plan(planned):  # noqa: F811 - imported fixture
    claim, intent, manifest, sources, code, environment = planned
    publish_collection(claim, manifest, **CHECKS)
    project = claim.root.parent.parent.parent
    request = {"generation": {"seed": 42}, "provider_revision": "fixture/1"}
    inventory = read_canonical_json(claim.root / "source_inventory.json")
    plan = scenario_request(project, request, intent, inventory)
    write_scenario_request(project, plan)
    kwargs = dict(
        live_sources=sources,
        expected_intent=intent,
        generation_command="snakemake all -s generate_scenarios.smk",
    )
    return project, request, plan, kwargs, code, environment


def test_exact_project_plan_and_source_free_explicit_resolution(ready_plan):
    project, request, plan, kwargs, code, env = ready_plan
    selection, manifest = resolve_project_collection(
        project, request, **kwargs, live_code=code, live_environment=env, **CHECKS
    )
    assert selection["resolution_mode"] == "project-generation"
    for path in kwargs["live_sources"].values():
        path.unlink()
    explicit, retained = resolve_explicit_collection(
        {"manifest_path": plan["manifest_path"]}, **CHECKS
    )
    assert explicit["resolution_mode"] == "explicit-manifest"
    assert retained == manifest
    with pytest.raises(GeneratedCollectionStale):
        verify_scenario_request(project, request, **kwargs)


def test_missing_request_never_falls_back_to_ready_collection(ready_plan):
    project, request, _, kwargs, _, _ = ready_plan
    with pytest.raises(GeneratedCollectionUnavailable, match="generate_scenarios"):
        verify_scenario_request(project, {**request, "different": True}, **kwargs)


def test_stale_source_refuses_even_with_matching_plan_hash(ready_plan):
    project, request, _, kwargs, _, _ = ready_plan
    next(iter(kwargs["live_sources"].values())).write_bytes(b"changed source")
    with pytest.raises(GeneratedCollectionStale, match="expected=.*observed="):
        verify_scenario_request(project, request, **kwargs)


def test_plan_cannot_redirect_to_another_collection(ready_plan):
    project, request, plan, kwargs, _, _ = ready_plan
    changed = deepcopy(plan)
    changed["manifest_path"] = str(project / "other" / "collection.json")
    changed["request_sha256"] = content_sha256(
        {k: v for k, v in changed.items() if k != "request_sha256"}
    )
    with pytest.raises(ValueError, match="canonical inputs"):
        write_scenario_request(project, changed)
    assert verify_scenario_request(project, request, **kwargs) == plan


@pytest.mark.parametrize("extra", ["collection_id", "collection_revision", "latest"])
def test_explicit_selector_refuses_config_id_or_fallback(extra):
    with pytest.raises(ValueError, match="only manifest_path"):
        resolve_explicit_collection(
            {"manifest_path": "absent", extra: "anything"}, **CHECKS
        )


def test_plan_directory_alias_cannot_mutate_collection(ready_plan):
    project, request, plan, kwargs, _, _ = ready_plan
    target = project / "scenarios" / "requests" / content_sha256(request)
    (target / "request.json").unlink()
    target.rmdir()
    collection = project / "scenarios" / "collections" / plan["collection_id"]
    before = {
        p.relative_to(collection).as_posix(): p.read_bytes()
        for p in collection.rglob("*")
        if p.is_file()
    }
    try:
        target.symlink_to(collection, target_is_directory=True)
    except OSError as exc:
        pytest.skip(f"symlink unavailable: {exc}")
    with pytest.raises(ValueError, match="aliased"):
        write_scenario_request(project, plan)
    assert before == {
        p.relative_to(collection).as_posix(): p.read_bytes()
        for p in collection.rglob("*")
        if p.is_file()
    }


def test_routine_resolution_refuses_aliased_store(ready_plan, tmp_path):
    original, request, plan, kwargs, code, env = ready_plan
    project = tmp_path / "aliased-project"
    project.mkdir()
    replacement = scenario_request(
        project, request, plan["intent"], plan["source_inventory"]
    )
    write_scenario_request(project, replacement)
    store = project / "scenarios" / "collections"
    try:
        store.symlink_to(
            original / "scenarios" / "collections", target_is_directory=True
        )
    except OSError as exc:
        pytest.skip(f"symlink unavailable: {exc}")
    with pytest.raises(GeneratedCollectionStale, match="aliased"):
        resolve_project_collection(
            project, request, **kwargs, live_code=code, live_environment=env, **CHECKS
        )
