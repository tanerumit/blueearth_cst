"""Execution diagnostics cannot invalidate otherwise identical frozen responses."""

from copy import deepcopy

import pytest

from blueearth_cst.experiment.simulation_record import (
    SimulationFrozenError,
    read_simulation_intent_v2,
    simulation_intent_v2,
)
from blueearth_cst.experiment.simulation_reuse import check_simulation_reuse
from tests._v2_experiment import build_v2_experiment


def _rebuild(intent):
    return simulation_intent_v2(
        intent["experiment_name"],
        intent["collection"],
        intent["simulator"],
        intent["documents"],
        intent["identity_projections"]["preparation"],
    )


@pytest.fixture(scope="module")
def retained(tmp_path_factory):
    experiment = build_v2_experiment(tmp_path_factory.mktemp("reuse"), publish=False)
    intent = read_simulation_intent_v2(experiment.root)
    intent["documents"]["simulator_adapter_code"] = [
        {"path": "blueearth_cst/experiment/simulator_adapter.py", "sha256": "a" * 64},
        {"path": "blueearth_cst/shared/execution_outputs.py", "sha256": "b" * 64},
    ]
    return _rebuild(intent)


def test_identical_repeat_reuses_the_frozen_simulation(retained):
    check_simulation_reuse(retained, deepcopy(retained))


def test_diagnostic_edit_reuses_original_identity_without_mutating_intents(retained):
    current = deepcopy(retained)
    current["documents"]["simulator_adapter_code"][1]["sha256"] = "c" * 64
    current = _rebuild(current)
    assert current["simulation_id"] != retained["simulation_id"]
    before = deepcopy((retained, current))
    check_simulation_reuse(retained, current)
    assert (retained, current) == before


@pytest.mark.parametrize(
    "component",
    [
        "code",
        "settings",
        "environment",
        "preparation",
        "collection",
        "simulator",
        "model",
        "response",
    ],
)
def test_diagnostic_edit_cannot_hide_changed_scientific_inputs(retained, component):
    current = deepcopy(retained)
    current["documents"]["simulator_adapter_code"][1]["sha256"] = "c" * 64
    if component == "code":
        current["documents"]["simulator_adapter_code"][0]["sha256"] = "d" * 64
    elif component == "settings":
        current["documents"]["settings"]["simulation_window"]["end"] += 1
    elif component == "environment":
        current["documents"]["environment"]["packages"]["changed"] = "1"
    elif component == "preparation":
        current["identity_projections"]["preparation"]["pet_method"] = "changed"
    elif component == "collection":
        current["collection"]["collection_revision"] = "d" * 64
    elif component == "model":
        from blueearth_cst.shared.model_digest import model_digest_from_entries

        model = current["documents"]["model_reference"]
        model["inputs"][model["model_toml"]] = "d" * 64
        model["digest"] = model_digest_from_entries(sorted(model["inputs"].items()))
    elif component == "response":
        current["documents"]["response_request"]["variables"][0]["units"] = "m"
    else:
        current["simulator"]["revision"] = "d" * 64
    with pytest.raises(SimulationFrozenError, match="simulation inputs changed"):
        check_simulation_reuse(retained, _rebuild(current))
