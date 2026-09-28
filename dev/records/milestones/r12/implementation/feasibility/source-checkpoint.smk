"""P0 generation-owned extraction -> source plan -> exact collection target."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(workflow.source_path("fixture_contracts.py")).parent))
from fixture_contracts import preserve_json, read_json, source_plan, write_json

plan_path = Path("planning/source.json")
if plan_path.exists() and Path("prepared/source.txt").exists():
    existing_plan = read_json(plan_path)
    if existing_plan != source_plan():
        raise ValueError("StaleSourcePlan: raw/source.txt or prepared/source.txt; rebuild plan")
    ready = Path(existing_plan["target"])
    if ready.exists() and read_json(ready) != existing_plan:
        raise ValueError(f"ImmutablePublicationMismatch: {ready}")
if not plan_path.exists():
    print("P0_UNRESOLVED collection identity awaits source checkpoint", flush=True)


rule all:
    input:
        ready=lambda wc: selected_collection(wc),
    default_target: True


rule extract_source:
    input:
        "raw/source.txt",
    output:
        "prepared/source.txt",
    run:
        Path(output[0]).write_bytes(Path(input[0]).read_bytes())


checkpoint prepare_collection_sources:
    input:
        raw="raw/source.txt",
        prepared="prepared/source.txt",
    output:
        "planning/source.json",
    run:
        write_json(output[0], source_plan())


def selected_collection(wc):
    plan = read_json(checkpoints.prepare_collection_sources.get().output[0])
    return plan["target"]


def selected_source(wc):
    plan = checkpoints.prepare_collection_sources.get().output[0]
    state = read_json(plan)
    if wc.collection_id != state["id"]:
        raise ValueError(f"CollectionIdentityMismatch: {wc.collection_id}")
    if state != source_plan():
        raise ValueError("StaleSourcePlan: prepared/source.txt")
    ready = Path(state["target"])
    if ready.exists() and read_json(ready) != state:
        raise ValueError(f"ImmutablePublicationMismatch: {ready}")
    return str(plan)


rule publish_collection:
    input:
        selected_source,
    output:
        update("collections/{collection_id}/manifest.json"),
    wildcard_constraints:
        collection_id="[a-f0-9]{64}",
    run:
        preserve_json(output[0], read_json(input[0]))
