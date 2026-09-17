"""Static contracts for the three configuration snapshot rules.

The content-addressed bundle these once pinned was removed on 2026-08-13
(config-snapshot redesign): it had no readers, and its directory name was a
digest over the WHOLE config, so an edit to any other workflow's section minted
a fresh one. What each rule writes now is a current-only ``run_record.yml``.
"""

import re
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]

SNAKEFILES = [
    "build_model.smk",
    "analyze_projections.smk",
]


def _rule_block(snakefile: Path, name: str) -> str:
    """Return one rule body from a Snakefile."""
    text = snakefile.read_text(encoding="utf-8")
    match = re.search(
        rf"^[ \t]*rule {name}:\n(.*?)(?=^[ \t]*(?:rule|checkpoint) |\Z)",
        text,
        re.S | re.M,
    )
    assert match, f"rule {name} not found in {snakefile.name}"
    return match.group(1)


@pytest.mark.parametrize(
    ("snakefile_name", "stable_output", "record_path"),
    [
        (
            "build_model.smk",
            "config/runs/build_model/composed_config.yml",
            "config/runs/build_model/run_record.yml",
        ),
        (
            "analyze_projections.smk",
            "config/runs/analyze_projections/composed_config.yml",
            "config/runs/analyze_projections/run_record.yml",
        ),
    ],
)
def test_snapshot_rule_keeps_current_copy_and_writes_a_run_record(
    snakefile_name, stable_output, record_path
):
    """Every workflow keeps its guard-compatible copy and adds a run record.

    The snapshot's path is load-bearing: two of them are baseline-fingerprinted
    targets, so a rule that moves one silently turns the gate red. Pinned here
    rather than left to the rule.
    """
    snakefile = REPO / snakefile_name
    text = snakefile.read_text(encoding="utf-8")
    block = _rule_block(snakefile, "snapshot_config")

    assert "rule copy_config:" not in text
    assert stable_output in block
    assert "effective_config = config" in block
    assert "advanced_settings = ADVANCED_SETTINGS" in block
    assert "run_record = RUN_RECORD" in block
    assert record_path in text


@pytest.mark.parametrize("snakefile_name", SNAKEFILES)
def test_the_content_addressed_bundle_is_gone(snakefile_name):
    """No workflow may reintroduce the bundle under any of its old names.

    An absence needs its own test: nothing else fails when a digest-named
    directory quietly comes back, because it was write-only in the first place.
    """
    text = (REPO / snakefile_name).read_text(encoding="utf-8")

    assert "snapshot_bundle" not in text
    assert "CONFIG_SNAPSHOT_DIR" not in text
    assert "CONFIG_SNAPSHOT_DIGEST" not in text
    assert "snapshot_bundle_digest(" not in text


@pytest.mark.parametrize("snakefile_name", SNAKEFILES)
def test_the_run_record_is_one_file_per_workflow(snakefile_name):
    """One record, replaced in place -- not a directory that accumulates.

    The bundle's defect was that every distinct config minted another
    directory nobody ever read. A record named after the workflow rather than
    after a digest is what keeps that from returning.
    """
    text = (REPO / snakefile_name).read_text(encoding="utf-8")

    assert "RUN_RECORD = " in text
    assert text.count("RUN_RECORD = ") == 1
    assert "run_record.yml" in text


# --------------------------------------------------------------------------- #
# Projections, digests, and the journal's declaration semantics
# --------------------------------------------------------------------------- #


@pytest.mark.parametrize(
    ("snakefile_name", "expected"),
    [
        (
            "build_model.smk",
            '("project", "basin", "climate", "model", "workflows.build_model")',
        ),
        (
            "analyze_projections.smk",
            '("project", "basin", "climate", "model", "workflows.analyze_projections")',
        ),
    ],
)
def test_each_workflow_declares_its_consumed_key_projection(snakefile_name, expected):
    """Scoping by consumed keys is what stops one workflow re-firing another."""
    text = (REPO / snakefile_name).read_text(encoding="utf-8")

    assert f"CONFIG_PROJECTION = {expected}" in text


def test_successors_use_typed_retained_records_instead_of_snapshot_guard():
    generation = (REPO / "generate_scenarios.smk").read_text(encoding="utf-8")
    simulation = (
        REPO / "blueearth_cst/experiment/rules/simulate_and_metrics.smk"
    ).read_text(encoding="utf-8")
    assert "resolve_generation_plan" in generation
    assert "freeze_simulation" in simulation
    assert "response_request.json" in simulation
    for text in (generation, simulation):
        assert "check_project_consistency" not in text
        assert "snapshot_config" not in text


@pytest.mark.parametrize("snakefile_name", SNAKEFILES)
def test_the_wide_digest_is_threaded_through_the_snapshot_rule(snakefile_name):
    """Params threading is what keeps the record fresh when the CHECKOUT moves.

    Without it a code-only commit leaves the record stamped with the previous
    one and writes no journal line -- the defect both design reviewers found
    independently. It must be a STRING digest: the params trigger compares
    values, and a nested structure is not what the repo's probe verified.
    """
    snakefile = REPO / snakefile_name
    block = _rule_block(snakefile, "snapshot_config")
    text = snakefile.read_text(encoding="utf-8")

    assert "configuration_inputs_sha256 = CONFIGURATION_INPUTS_DIGEST" in block
    assert "config_projection = CONFIG_PROJECTION" in block
    assert "CONFIGURATION_INPUTS_DIGEST = configuration_inputs_digest(" in text


@pytest.mark.parametrize("snakefile_name", SNAKEFILES)
def test_the_journal_is_never_a_declared_output(snakefile_name):
    """The silent-truncation trap, pinned as an absence.

    Snakemake deletes a rule's declared outputs BEFORE the job runs, so a
    declared journal would be truncated to one line on every re-execution --
    silently, because a one-line journal is indistinguishable from a young one.
    Emission lives in workflow-level handlers, which have no outputs at all.
    """
    text = (REPO / snakefile_name).read_text(encoding="utf-8")

    assert "JOURNAL_PATH" in text, "the workflow must define a journal path"
    for line in text.splitlines():
        stripped = line.strip()
        if "journal.jsonl" in stripped or "JOURNAL_PATH" in stripped:
            assert not stripped.startswith(("output:", "run_metadata =")), stripped
            assert "output" not in stripped.split("=")[0], stripped


@pytest.mark.parametrize("snakefile_name", SNAKEFILES)
def test_every_workflow_registers_all_three_lifecycle_handlers(snakefile_name):
    """The terminal line is the contract; onstart is best-effort tracing."""
    text = (REPO / snakefile_name).read_text(encoding="utf-8")

    for handler in ("onstart:", "onsuccess:", "onerror:"):
        assert re.search(rf"^[ \t]*{handler}$", text, re.M), (
            f"{snakefile_name} lacks {handler}"
        )
    assert '_journal("success")' in text
    assert '_journal("failed")' in text


def test_the_sidecar_rules_take_letter_suffixes():
    """`1.16`/`3.17` were already taken, and renumbering is forbidden.

    naming.md §9: DO NOT RENUMBER TO INSERT A RULE. The design proposed the
    taken numbers, so this pins the correction rather than leaving it to a
    reader to rediscover that gather_benchmarks owns them.
    """
    wf1 = (REPO / "build_model.smk").read_text(encoding="utf-8")

    assert 'rule_banner("1.15b", "write_run_metadata")' in wf1
    assert 'rule_banner("1.16", "gather_benchmarks")' in wf1
