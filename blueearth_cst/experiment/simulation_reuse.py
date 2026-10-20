"""Reuse frozen responses across changes confined to execution diagnostics."""

from typing import Any

from blueearth_cst.experiment.simulation_record import (
    SimulationFrozenError,
    _v2_simulation_id,
)

# Keep the original complete inventory as provenance. Only this observational
# module is ignored when comparing an existing simulation with current inputs.
_DIAGNOSTIC_CODE = {"blueearth_cst/shared/execution_outputs.py"}


def check_simulation_reuse(retained: dict[str, Any], current: dict[str, Any]) -> None:
    """Accept identical scientific inputs without rewriting the frozen intent.

    Older intents include execution diagnostics through static transitive
    imports. Compare the remaining inventory exactly, then use the existing
    identity calculation to check every other identity component unchanged.
    """
    if current["simulation_id"] == retained["simulation_id"]:
        return
    code_matches = [
        item
        for item in retained["documents"]["simulator_adapter_code"]
        if item["path"] not in _DIAGNOSTIC_CODE
    ] == [
        item
        for item in current["documents"]["simulator_adapter_code"]
        if item["path"] not in _DIAGNOSTIC_CODE
    ]
    comparable = {
        **current,
        "document_digests": {
            **current["document_digests"],
            "simulator_adapter_code": retained["document_digests"][
                "simulator_adapter_code"
            ],
        },
    }
    if code_matches and _v2_simulation_id(comparable) == retained["simulation_id"]:
        return
    raise SimulationFrozenError("simulation inputs changed; use a new experiment name")
