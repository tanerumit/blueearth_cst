"""Reservation-aware WF3 orchestration, outside the generator code inventory."""

import hashlib
from pathlib import Path

from blueearth_cst.experiment.content_identity import (
    atomic_record,
    canonical_json_bytes,
    confined_path,
    read_canonical_json,
)
from blueearth_cst.experiment.generation_plan import (
    build_candidate_intent,
    generation_configuration,
    publish_plan_pointer,
    read_pinned_plan,
    select_generation_plan,
)
from blueearth_cst.experiment.generation_publication import validate_installed_generator
from blueearth_cst.experiment.scenario_collection_v2 import read_collection_v2
from blueearth_cst.shared.workflow_config_snapshot import file_reference


def bind_ready_collection_owned(
    root, name, marker_path, *, resolution_mode="project-generation"
):
    from blueearth_cst.experiment.reservation import bind_reservation_owned

    root = Path(root).resolve()
    marker_path = confined_path(
        root, Path(marker_path).resolve().relative_to(root).as_posix()
    )
    marker = read_collection_v2(marker_path)
    resolution = {
        "resolution_mode": resolution_mode,
        "manifest": file_reference(marker_path, "project_root", root),
        "collection_id": marker["collection_id"],
        "collection_revision": marker["collection_revision"],
        "run_ids": [entry["run_id"] for entry in marker["series"]],
    }
    bind_reservation_owned(root, name, resolution=resolution)
    return marker


def select_reserved_plan_owned(config, repository, root, name):
    """Return (settings, plan, path, sha256, ready) before ordinary plan selection."""
    from blueearth_cst.experiment.reservation import (
        bind_reservation_owned,
        compare_request,
        read_reservation,
    )

    root = Path(root).resolve()
    reservation = read_reservation(root, name)
    settings = generation_configuration(config, repository)
    candidate = build_candidate_intent(settings)
    seed = reservation["seed"]
    if seed["state"] == "bound":
        plan_path = confined_path(root, seed["plan"]["path"])
        plan = read_pinned_plan(plan_path, seed["plan"]["sha256"], root)
        compare_request(plan["request"], settings["request"])
        compare_request(
            plan["candidate_identity_digests"], candidate["identity_digests"]
        )
        compare_request(
            seed["seed_resolution"],
            candidate["documents"]["generation_config"]["seed_resolution"],
        )
        marker_path = confined_path(
            root, plan["outputs"]["record_root"] + "/collection.json"
        )
        if marker_path.exists():
            marker = read_collection_v2(marker_path)
            actual = read_canonical_json(
                marker_path.with_name("collection_intent.json")
            )
            compare_request(plan["intent"], actual)
            if marker["collection_id"] != plan["collection_id"]:
                raise ValueError("ready collection differs from bound generation plan")
            if (
                plan["collection_revision"] is not None
                and marker["collection_revision"] != plan["collection_revision"]
            ):
                raise ValueError(
                    "ready collection revision differs from bound reuse plan"
                )
            validate_installed_generator(plan, root, relocatable=True)
            if reservation["request"]["selection"]["mode"] == "project-generation":
                bind_ready_collection_owned(root, name, marker_path)
            publish_plan_pointer(settings, plan)
            return settings, plan, plan_path, seed["plan"]["sha256"], True
        record_root = marker_path.parent
        data_root = confined_path(root, plan["outputs"]["data_root"])
        receipts = plan_path.parent / "initializations"
        related = []
        if receipts.exists():
            for receipt_path in receipts.glob("*.json"):
                receipt = read_canonical_json(receipt_path)
                if receipt.get("plan_sha256") == seed["plan"]["sha256"]:
                    related.append(receipt)
        if related or record_root.exists() or data_root.exists():
            if related:
                raise ValueError(
                    "IncompleteWF3: initialized collection is incomplete; partial generation cannot resume. "
                    "Preserve its inputs and use a fresh generation request/project; reservation recovery cannot repair it."
                )
            raise ValueError(
                "PartialWF3Initialization: collection namespace lacks complete initialization evidence; "
                "preserve it for diagnosis. Reservation recovery cannot repair it."
            )
        if plan["decision"] != "create" or reservation["resolution"] is not None:
            raise ValueError(
                "MissingWF3Collection: bound collection is missing; no recreation is authorized"
            )
        publish_plan_pointer(settings, plan)
        return settings, plan, plan_path, seed["plan"]["sha256"], False
    if seed["state"] != "awaiting_sources":
        raise ValueError("reservation does not admit generation")
    plan = select_generation_plan(settings, candidate)
    plan_bytes = canonical_json_bytes(plan)
    sha256 = hashlib.sha256(plan_bytes).hexdigest()
    plan_path = Path(settings["request_path"]).with_name(f"{sha256}.json")
    confined_path(root, plan_path.relative_to(root).as_posix())
    plan_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        atomic_record(plan_path, plan)
    except FileExistsError:
        if plan_path.read_bytes() != plan_bytes:
            raise ValueError("generation plan digest collision") from None
    config_document = plan["candidate_intent"]["documents"]["generation_config"]
    seed = {
        "state": "bound",
        "requested": config_document["seed"]["requested"],
        "resolved": config_document["seed"]["resolved"],
        "seed_resolution": config_document["seed_resolution"],
        "plan": file_reference(plan_path, "project_root", root),
        "source_identity_sha256": plan["candidate_identity_digests"][
            "source_inventory"
        ],
    }
    bind_reservation_owned(root, name, seed=seed)
    publish_plan_pointer(settings, plan)
    return settings, plan, plan_path, sha256, False
