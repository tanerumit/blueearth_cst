"""Exact-byte and invalidation checks for R12 collection-canon/1."""

import hashlib
from copy import deepcopy
from dataclasses import replace

import pytest

from blueearth_cst.experiment.content_identity import (
    canonical_json_bytes,
    collection_id,
    collection_revision,
    confined_path,
    content_sha256,
    read_canonical_json,
    scenario_semantics_sha256,
)
from blueearth_cst.experiment.scenario_rows import stochastic_rows


def test_canonical_bytes_have_unicode_order_and_final_lf():
    expected = '{"a":[true,null,2,1.5],"é":"水"}\n'.encode()
    value = {"é": "水", "a": [True, None, 2, 1.5]}
    assert canonical_json_bytes(value) == expected
    assert content_sha256(value) == hashlib.sha256(expected).hexdigest()
    assert content_sha256({"a": 1, "b": 2}) == content_sha256({"b": 2, "a": 1})
    assert content_sha256([1, 2]) != content_sha256([2, 1])
    assert content_sha256(True) != content_sha256(1)
    assert canonical_json_bytes([1.0, -0.0, 1e-7]) == b"[1.0,-0.0,1e-07]\n"


@pytest.mark.parametrize(
    "raw",
    [
        b'{"a":1,"a":2}\n',
        b'{"a": 1}\n',
        b'{"a":1}',
        b'{"a":NaN}\n',
        b'{"a":1e999}\n',
        b'{"a":1}\r\n',
    ],
)
def test_persisted_documents_refuse_ambiguous_or_noncanonical_bytes(tmp_path, raw):
    path = tmp_path / "document.json"
    path.write_bytes(raw)
    with pytest.raises(ValueError):
        read_canonical_json(path)
    assert path.read_bytes() == raw


def test_persisted_canonical_document_round_trips(tmp_path):
    path = tmp_path / "document.json"
    value = {"source": "水", "items": [1, None, True]}
    path.write_bytes(canonical_json_bytes(value))
    assert read_canonical_json(path) == value


def test_semantics_strip_only_run_id_and_preserve_ancestry_and_order():
    rows = stochastic_rows(1, 2, unit_id_capacity=100)
    expected = [
        {
            "derived_from": "",
            "evaluated": "true",
            "scenario_type": "stochastic",
            "rlz": "1",
            "st_id": "",
        },
        {
            "derived_from": "001",
            "evaluated": "true",
            "scenario_type": "stochastic",
            "rlz": "1",
            "st_id": "1",
        },
        {
            "derived_from": "001",
            "evaluated": "true",
            "scenario_type": "stochastic",
            "rlz": "1",
            "st_id": "2",
        },
    ]
    digest = scenario_semantics_sha256(rows)
    assert digest == content_sha256(expected)
    assert (
        scenario_semantics_sha256([replace(row, run_id="other") for row in rows])
        == digest
    )
    assert scenario_semantics_sha256(list(reversed(rows))) != digest
    assert (
        scenario_semantics_sha256([rows[0], replace(rows[1], derived_from=""), rows[2]])
        != digest
    )


@pytest.mark.parametrize(
    "value",
    [
        float("nan"),
        float("inf"),
        -float("inf"),
        {1: "integer key"},
        (1, 2),
        {"nested": [object()]},
    ],
)
def test_non_json_values_are_refused(value):
    with pytest.raises((ValueError, TypeError)):
        canonical_json_bytes(value)


@pytest.mark.parametrize(
    "relative",
    [
        "",
        "/a",
        "C:/a",
        "C:a",
        "a//b",
        "a/",
        "../a",
        "a/../b",
        "./a",
        "a\\b",
        "a:stream",
    ],
)
def test_noncanonical_or_escaping_paths_are_refused(tmp_path, relative):
    with pytest.raises(ValueError, match="path"):
        confined_path(tmp_path, relative)


def test_paths_resolve_from_collection_not_cwd(tmp_path, monkeypatch):
    root = tmp_path / "collection"
    root.mkdir()
    monkeypatch.chdir(tmp_path.parent)
    assert confined_path(root, "forcing/run_001.nc") == root / "forcing/run_001.nc"


def test_resolved_escape_is_refused(tmp_path):
    root = tmp_path / "collection"
    root.mkdir()
    outside = tmp_path / "outside"
    outside.mkdir()
    try:
        (root / "link").symlink_to(outside, target_is_directory=True)
    except OSError as exc:
        pytest.skip(f"directory symlink unavailable: {exc}")
    with pytest.raises(ValueError, match="outside"):
        confined_path(root, "link/forcing.nc")


@pytest.mark.parametrize(
    "relative",
    ["collection.json.", "collection.json ", "dir./payload.nc", "NUL", "aux.nc"],
)
def test_windows_alias_spellings_are_not_portable_artifact_paths(tmp_path, relative):
    with pytest.raises(ValueError, match="path"):
        confined_path(tmp_path, relative)


@pytest.fixture
def intent():
    return {
        "schema_version": "scenario-collection/1",
        "canonicalization_id": "collection-canon/1",
        "scenario_spec": {"scenario_type": "fixture", "expected_run_count": 1},
        "scenario_semantics_sha256": "a" * 64,
        "provider": {"name": "fixture", "revision": "b" * 64},
        "unit_id_capacity": 100,
        **{
            name: {"path": f"{name}.json", "sha256": "c" * 64}
            for name in (
                "generation_config",
                "source_inventory",
                "provider_code",
                "environment",
                "preparation_context",
            )
        },
    }


def test_identity_projection_matches_independent_equation(intent):
    expected = {
        "schema_version": "scenario-collection/1",
        "scenario_spec": intent["scenario_spec"],
        "scenario_semantics_sha256": "a" * 64,
        "generation_config_sha256": "c" * 64,
        "source_inventory_sha256": "c" * 64,
        "provider_name_and_revision": intent["provider"],
        "provider_code_sha256": "c" * 64,
        "environment_sha256": "c" * 64,
        "preparation_context_sha256": "c" * 64,
        "unit_id_capacity": 100,
    }
    assert collection_id(intent) == content_sha256(expected)
    original = collection_id(intent)
    intent.update(collection_id="d" * 64, created_at_utc="display only")
    assert collection_id(intent) == original


@pytest.mark.parametrize(
    "field",
    [
        "scenario_spec",
        "scenario_semantics_sha256",
        "generation_config",
        "source_inventory",
        "provider",
        "provider_code",
        "environment",
        "preparation_context",
        "unit_id_capacity",
    ],
)
def test_every_intent_input_invalidates_identity(intent, field):
    changed = deepcopy(intent)
    if field == "scenario_spec":
        changed[field]["expected_run_count"] = 2
    elif field == "provider":
        changed[field]["revision"] = "d" * 64
    elif field == "unit_id_capacity":
        changed[field] = 1000
    elif field == "scenario_semantics_sha256":
        changed[field] = "d" * 64
    else:
        changed[field]["sha256"] = "d" * 64
    assert collection_id(changed) != collection_id(intent)


@pytest.mark.parametrize(
    "field,value",
    [
        ("schema_version", "unknown"),
        ("canonicalization_id", "unknown"),
        ("unit_id_capacity", True),
        ("unit_id_capacity", 0),
        ("scenario_semantics_sha256", "A" * 64),
    ],
)
def test_unsupported_identity_inputs_refuse(intent, field, value):
    intent[field] = value
    with pytest.raises(ValueError, match=field):
        collection_id(intent)


def test_revision_covers_ordered_bytes_and_descriptors():
    manifest = {
        "collection_id": "a" * 64,
        "intent_sha256": "b" * 64,
        "scenario_table": {"path": "scenario_table.csv", "sha256": "c" * 64},
        "scenario_type_artifacts": [],
        "preparation_context": {"path": "preparation_context.json", "sha256": "d" * 64},
        "forcing": [
            {"run_id": "001", "sha256": "e" * 64, "descriptor": {"units": "mm"}}
        ],
    }
    expected = {
        "collection_id": "a" * 64,
        "intent_sha256": "b" * 64,
        "scenario_table_sha256": "c" * 64,
        "scenario_type_artifact_inventory": [],
        "preparation_context_sha256": "d" * 64,
        "ordered_forcing_inventory_with_descriptors": manifest["forcing"],
    }
    revision = collection_revision(manifest)
    assert revision == content_sha256(expected)
    manifest["collection_revision"] = revision
    assert collection_revision(manifest) == revision
    manifest["forcing"][0]["descriptor"]["units"] = "m"
    assert collection_revision(manifest) != revision
