"""The path-byte provider inventory must not include WF4-only helpers."""

import sys
from pathlib import Path

from blueearth_cst.experiment.content_identity import repository_code_inventory
from blueearth_cst.shared import run_log_core, snake_utils

ROOTS = (
    "blueearth_cst/experiment/scenario_provider.py",
    "blueearth_cst/experiment/generation_plan.py",
    "blueearth_cst/experiment/prepare_weathergen_config.py",
    "blueearth_cst/experiment/prepare_cst_parameters.py",
)


def test_wf3_provider_helper_closure_excludes_mixed_snake_utils():
    repo = Path(__file__).resolve().parents[1]
    inventory = repository_code_inventory(repo, ROOTS)
    paths = {entry["path"] for entry in inventory}
    assert "blueearth_cst/shared/wf3_science.py" in paths
    assert "blueearth_cst/shared/run_log_core.py" in paths
    assert "blueearth_cst/shared/snake_utils.py" not in paths


def test_wf3_helper_inventory_ignores_wf4_adapter_edit(tmp_path):
    repo = Path(__file__).resolve().parents[1]
    source = repo / "blueearth_cst" / "shared"
    target = tmp_path / "blueearth_cst" / "shared"
    target.mkdir(parents=True)
    for name in ("wf3_science.py", "run_log_core.py", "snake_utils.py"):
        (target / name).write_bytes((source / name).read_bytes())
    roots = [
        "blueearth_cst/shared/wf3_science.py",
        "blueearth_cst/shared/run_log_core.py",
    ]
    before = repository_code_inventory(tmp_path, roots)
    (target / "snake_utils.py").write_bytes(b"# WF4-only edit\n")
    assert repository_code_inventory(tmp_path, roots) == before


def test_legacy_runner_injects_relay_but_wf3_runner_uses_neutral_core(
    tmp_path, monkeypatch
):
    class Relay:
        def __init__(self):
            self.seen = []

        def tick(self):
            return None

        def feed(self, raw, *, stream):
            self.seen.append(raw)
            return raw

        def close(self):
            return None

    relay = Relay()
    monkeypatch.setattr(snake_utils, "_wflow_frame_relay", lambda: relay)
    command = [sys.executable, "-c", "print('helper boundary probe')"]
    legacy = tmp_path / "legacy.log"
    neutral = tmp_path / "neutral.log"
    assert snake_utils.run_and_tee(command, legacy) == 0
    assert run_log_core.run_and_tee(command, neutral) == 0
    assert relay.seen
    assert "helper boundary probe" in legacy.read_text(encoding="utf-8")
    assert "helper boundary probe" in neutral.read_text(encoding="utf-8")
