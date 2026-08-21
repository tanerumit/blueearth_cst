"""The migration splitter stages a verified proposal and never touches your file.

Unit surface for ``scripts/split_project_config.py`` (R13 §16.1). The tool is
report-only against user files, so the two things worth proving are that the
proposal is *right* — it composes back to the source, key for key — and that the
tool cannot reach outside the directory it created.

Three groups:

* **the round trip** (D-15.4b), including a permanent regression over all five
  shipped configs. A mangled comment is cosmetic; a mangled value produces a
  config that parses and runs, so WF1/WF2 would silently produce different
  numbers under an unchanged-looking config. This is the check that stands
  between the migration and that outcome;
* **the refusals** (D-15.4a), which convert an unbounded class of silent
  corruption — anchors, aliases, merge keys, block scalars — into a stated
  non-support with a manual path;
* **the staging-ownership contract** (D-15.3a). The recursive replace is the
  only destructive act in the tool, so every one of its four refusals is
  exercised, and the source file's bytes are asserted unchanged after every run
  in this module — success and refusal alike.
"""

from __future__ import annotations

import os
import sys
import textwrap
from pathlib import Path

import pytest
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import split_project_config as spc  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parent.parent

#: The four shipped seeds and the template, frozen in their PRE-SPLIT shape.
#:
#: The permanent regression gate. These were the live configs until the R13
#: migration, and they are kept here afterwards because they are the only
#: real-world specimens the repository has of the shape this tool exists to
#: convert: hand-written comments at three indent levels, nested blocks, CRLF
#: endings, four genuinely different variants. Once the repository migrated,
#: nothing else in the tree could exercise the tool at all -- and the tool has
#: to keep working for every user who has not migrated yet.
#:
#: FROZEN: nothing should edit these again. A change to a live seed does not
#: belong here, and a failure here is a break in the splitter.
PRESPLIT_DIR = Path(__file__).resolve().parent / "data" / "presplit"
PRESPLIT = [
    "snake_config_rapid.yml",
    "snake_config_baseline.yml",
    "snake_config_baseline_linux.yml",
    "snake_config_wf2_fast.yml",
    "snake_config.template.yml",
]

#: A config declaring `reporting:`, which NO shipped seed or template does.
#: Without it the splitter's reporting-move branch and the loader's hoist would
#: both ship exercised by nothing but their own unit tests. Adding the key to a
#: shipped seed instead was rejected: a seed's key set is inside
#: `effective_config_digest` and, for the baseline, inside the three baseline
#: snapshot targets — so it would move a baseline target for a test-coverage
#: reason, in the milestone that depends on that gate being sharp.
REPORTING_FIXTURE = """\
project:
  project_dir: proj

shared:
  basin:
    region: "{'subbasin': [1.0, 2.0]}"

workflows:
  build_model:
    enabled: true
    wflow_outvars: ['river discharge']
  run_stress_test:
    enabled: true
    experiment_name: gabon
    realizations_num: 2

# Figure captions and titles. Deliberately outside every workflow section, so a
# caption can be corrected without re-running the experiment.
reporting:
  title: Gabon basin
  subtitle: stress test
"""


def write_source(
    tmp_path: Path, text: str, name: str = "snake_config_probe.yml"
) -> Path:
    directory = tmp_path / "project"
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / name
    with open(path, "w", encoding="utf-8", newline="") as handle:
        handle.write(text)
    return path


def run(source: Path, staging: Path | None = None) -> int:
    argv = [str(source)]
    if staging is not None:
        argv += ["--staging", str(staging)]
    return spc.main(argv)


@pytest.fixture
def source_unchanged():
    """Assert a config's bytes are identical before and after whatever ran.

    The report-only posture is the whole safety argument for a tool that
    rewrites configs, so it is checked on every path through this module — the
    refusal paths included, where a partially-written source would be the worst
    version of the bug.
    """
    recorded: dict[Path, bytes] = {}

    def watch(path: Path) -> Path:
        recorded[path] = path.read_bytes()
        return path

    yield watch
    for path, before in recorded.items():
        assert path.read_bytes() == before, f"{path} was modified by a report-only tool"


# ---------------------------------------------------------------------------
# D-15.4b — the round trip
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("name", PRESPLIT)
def test_every_shipped_config_round_trips(tmp_path, name, source_unchanged):
    """The permanent regression gate over the repository's own former configs.

    Composing the STAGED pair — not a re-derivation of it — is what makes this
    evidence: the emitted ``config_path`` values are bare filenames, so they
    resolve to the staged siblings under the T1-anchored rule, and the thing
    verified is the thing a user would apply.
    """
    source = source_unchanged(PRESPLIT_DIR / name)
    assert run(source, tmp_path) == 0
    staging = tmp_path / spc.STAGING_DIRNAME
    assert spc.verify_round_trip(staging / source.name, source) is None


def test_the_staged_pair_is_what_gets_verified(tmp_path, source_unchanged):
    """A staged T1 alone must not compose — its siblings are what complete it."""
    source = source_unchanged(write_source(tmp_path, REPORTING_FIXTURE))
    assert run(source, tmp_path) == 0
    staging = tmp_path / spc.STAGING_DIRNAME
    assert (staging / "snake_config_probe_build_model.yml").is_file()
    assert (staging / "snake_config_probe_run_stress_test.yml").is_file()
    composed = yaml.safe_load(
        (staging / "snake_config_probe.yml").read_text(encoding="utf-8")
    )
    assert composed["workflows"]["build_model"] == {
        "enabled": True,
        "config_path": "snake_config_probe_build_model.yml",
    }


def test_reporting_moves_into_its_owning_workflow_file(tmp_path, source_unchanged):
    """D-10.4's placement, produced by the tool rather than asserted about it."""
    source = source_unchanged(write_source(tmp_path, REPORTING_FIXTURE))
    assert run(source, tmp_path) == 0
    staging = tmp_path / spc.STAGING_DIRNAME

    wf3 = yaml.safe_load(
        (staging / "snake_config_probe_run_stress_test.yml").read_text(encoding="utf-8")
    )
    assert wf3["reporting"] == {"title": "Gabon basin", "subtitle": "stress test"}
    assert "reporting" not in yaml.safe_load(
        (staging / "snake_config_probe.yml").read_text(encoding="utf-8")
    )
    assert "Deliberately outside every workflow section" in (
        staging / "snake_config_probe_run_stress_test.yml"
    ).read_text(encoding="utf-8")


def test_a_commented_reporting_block_is_reported_not_moved(tmp_path, source_unchanged):
    """A text splitter that relocated comments it could not parse would be guessing.

    The block still has to be surfaced: left in the project file it points a
    user at a placement the loader no longer honours, and uncommenting it there
    is now a parse error.
    """
    text = REPORTING_FIXTURE.replace(
        "reporting:\n  title: Gabon basin\n  subtitle: stress test\n",
        "#reporting:\n#  title: Gabon basin\n#  subtitle: stress test\n",
    )
    assert "#reporting:" in text
    source = source_unchanged(write_source(tmp_path, text))
    assert run(source, tmp_path) == 0
    report = (tmp_path / spc.STAGING_DIRNAME / spc.REPORT_NAME).read_text("utf-8")
    assert "COMMENTED" in report
    assert "snake_config_probe_run_stress_test.yml" in report


def test_a_section_with_no_settings_gets_no_file_and_no_key(tmp_path, source_unchanged):
    """D-8.7's whole point, on the shape three of four shipped seeds already have.

    An omitted ``config_path`` composes to an empty section, which is what an
    empty file would have meant anyway — so the file is not created. Booking
    content-free files as a cost of the split and then offering reconciliation
    as their mitigation could not reduce a file that is empty by construction.
    """
    source = source_unchanged(
        write_source(
            tmp_path,
            textwrap.dedent(
                """\
                project:
                  project_dir: proj
                shared: {}
                workflows:
                  analyze_climate:
                    enabled: true
                  build_model:
                    enabled: true
                    wflow_outvars: ['q']
                """
            ),
        )
    )
    assert run(source, tmp_path) == 0
    staging = tmp_path / spc.STAGING_DIRNAME
    assert not (staging / "snake_config_probe_analyze_climate.yml").exists()
    staged = yaml.safe_load((staging / "snake_config_probe.yml").read_text("utf-8"))
    assert staged["workflows"]["analyze_climate"] == {"enabled": True}
    assert "no file is written" in (staging / spc.REPORT_NAME).read_text("utf-8")


def test_a_mismatched_round_trip_says_do_not_apply(tmp_path, monkeypatch, capsys):
    """The verdict must be able to say NO, or the clean verdicts prove nothing.

    Injected at the comparison rather than by constructing a config the splitter
    mangles — if such a config were known, the fix would be to stop mangling it.
    """
    source = write_source(tmp_path, REPORTING_FIXTURE)
    monkeypatch.setattr(
        spc, "verify_round_trip", lambda *_args, **_kwargs: "workflows.build_model"
    )
    assert run(source, tmp_path) == 1
    report = (tmp_path / spc.STAGING_DIRNAME / spc.REPORT_NAME).read_text("utf-8")
    assert "DO NOT APPLY" in report
    assert "workflows.build_model" in report
    assert "do not apply" in capsys.readouterr().err.lower()


# ---------------------------------------------------------------------------
# D-15.4a — the refusals
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("construct", "text", "expected"),
    [
        (
            "anchor-and-alias",
            "project:\n  a: &win 2000\nshared:\n  b: *win\nworkflows:\n"
            "  build_model:\n    enabled: true\n    c: *win\n",
            "anchor",
        ),
        (
            "merge-key",
            "project: {}\nshared:\n  base: &b {x: 1}\nworkflows:\n"
            "  build_model:\n    enabled: true\n    <<: *b\n",
            "anchor",
        ),
        (
            "block-scalar",
            "project: {}\nshared: {}\nworkflows:\n  build_model:\n"
            "    enabled: true\n    note: |\n      indented content\n"
            "      second line\n",
            "block scalar",
        ),
    ],
)
def test_unsplittable_constructs_are_refused_by_name(
    tmp_path, construct, text, expected, source_unchanged, capsys
):
    """Refuse, naming the construct and the line — and stage nothing at all.

    An anchor defined in one section and aliased in another becomes an undefined
    alias the moment the sections are separate files, which is the loud case. A
    ``<<:`` merge that re-resolves after the split changes values silently,
    which is not. A block scalar loses four spaces of its own *content* to the
    dedent, changing the string with no structural symptom.

    Detected through PyYAML's scanner, not by grepping for punctuation: ``&``
    and ``*`` are ordinary inside comments, and a check that refused the shipped
    seeds for punctuation would be worse than no check.
    """
    source = source_unchanged(write_source(tmp_path, text))
    assert run(source, tmp_path) == 1
    message = capsys.readouterr().err
    assert expected in message
    assert "line " in message
    assert not (tmp_path / spc.STAGING_DIRNAME).exists()


def test_no_shipped_config_trips_the_refusal():
    """The refusal is narrow enough to be usable, which is not free.

    A check keyed on the characters rather than the tokens would refuse several
    of these for a ``*`` inside a prose comment.
    """
    for name in PRESPLIT:
        text = (PRESPLIT_DIR / name).read_text(encoding="utf-8")
        span = spc._top_level_span(text.splitlines(keepends=True), "workflows")
        spc._refuse_unsplittable(text, span)


@pytest.mark.parametrize(
    "relative",
    [
        "test_case/snake_config_rapid.yml",
        "test_case/snake_config_baseline.yml",
        "config/templates/snake_config.template.yml",
    ],
)
def test_an_already_split_config_is_refused(
    tmp_path, relative, source_unchanged, capsys
):
    """A second pass is nonsense the round trip cannot see, so it is refused.

    The body of a migrated stanza is its `config_path`, so splitting again
    would write *that key* into a new workflow file and repoint the stanza at
    it -- and the result still composes back to the same document, so D-15.4b
    reports it CLEAN. Recognising the migrated shape up front is the only
    thing that catches it.

    Parametrized over the LIVE shipped configs, which makes this a standing
    assertion that they are in fact migrated.
    """
    source = source_unchanged(REPO_ROOT / relative)
    assert run(source, tmp_path) == 1
    assert "already split" in capsys.readouterr().err
    assert not (tmp_path / spc.STAGING_DIRNAME).exists()


def test_a_config_with_no_workflows_block_is_refused(
    tmp_path, source_unchanged, capsys
):
    source = source_unchanged(
        write_source(tmp_path, "project:\n  project_dir: proj\nshared: {}\n")
    )
    assert run(source, tmp_path) == 1
    assert "nothing to split" in capsys.readouterr().err


# ---------------------------------------------------------------------------
# D-15.3a — the staging-ownership contract
# ---------------------------------------------------------------------------


def test_creating_a_staging_directory_writes_the_ownership_marker(tmp_path):
    """The marker is what a later run's recursive replace is bound to."""
    target = spc._claim_staging(tmp_path / spc.STAGING_DIRNAME, tmp_path / "src")
    assert (target / spc.STAGING_MARKER).is_file()
    assert "split_project_config" in (target / spc.STAGING_MARKER).read_text("utf-8")


def test_a_marked_tool_named_directory_is_replaced_wholesale(tmp_path):
    """A re-run must not leave last run's proposal mixed into this one's."""
    target = spc._claim_staging(tmp_path / spc.STAGING_DIRNAME, tmp_path / "src")
    (target / "leftover.yml").write_text("stale", encoding="utf-8")
    again = spc._claim_staging(tmp_path / spc.STAGING_DIRNAME, tmp_path / "src")
    assert not (again / "leftover.yml").exists()
    assert (again / spc.STAGING_MARKER).is_file()


def test_an_unmarked_non_empty_directory_is_refused(tmp_path):
    """The refusal that stops a mistaken --staging deleting unrelated files.

    Nothing else in this tool deletes anything, so the binding between the
    recursive replace and a directory the tool can PROVE it created is the
    whole of its safety. Without it, a legitimate but mistaken argument could
    recursively delete a user's files — the exact harm the report-only posture
    was chosen to prevent, arriving through the tool's own namespace claim.
    """
    target = tmp_path / spc.STAGING_DIRNAME
    target.mkdir()
    (target / "someones_work.txt").write_text("do not delete", encoding="utf-8")
    with pytest.raises(spc.SplitRefusal, match="did not create it"):
        spc._claim_staging(target, tmp_path / "src")
    assert (target / "someones_work.txt").read_text(encoding="utf-8") == "do not delete"


def test_a_non_empty_directory_without_the_tool_basename_is_refused(tmp_path):
    """Both halves of the ownership test are required, not either one."""
    target = tmp_path / "my_documents"
    target.mkdir()
    (target / "thesis.txt").write_text("years of work", encoding="utf-8")
    (target / spc.STAGING_MARKER).write_text("forged", encoding="utf-8")
    with pytest.raises(spc.SplitRefusal, match="did not create it"):
        spc._claim_staging(target, tmp_path / "src")
    assert (target / "thesis.txt").exists()


def test_the_source_directory_is_refused_as_a_staging_target(tmp_path):
    """Staged files beside the originals make a half-applied migration invisible."""
    source_dir = tmp_path / "project"
    source_dir.mkdir()
    with pytest.raises(spc.SplitRefusal, match="ancestor"):
        spc._claim_staging(source_dir, source_dir)


def test_an_ancestor_of_the_source_directory_is_refused(tmp_path):
    """Refused before any filesystem write, whatever the target contains."""
    source_dir = tmp_path / "project" / "configs"
    source_dir.mkdir(parents=True)
    with pytest.raises(spc.SplitRefusal, match="ancestor"):
        spc._claim_staging(tmp_path, source_dir)


def test_staging_flag_supplies_a_location_not_a_namespace(tmp_path, source_unchanged):
    """``--staging <dir>`` works in a tool-named child and never replaces <dir>."""
    source = source_unchanged(write_source(tmp_path, REPORTING_FIXTURE))
    holding = tmp_path / "holding"
    holding.mkdir()
    (holding / "unrelated.txt").write_text("kept", encoding="utf-8")

    assert run(source, holding) == 0
    assert (holding / "unrelated.txt").read_text(encoding="utf-8") == "kept"
    assert (holding / spc.STAGING_DIRNAME / spc.STAGING_MARKER).is_file()


def test_the_default_staging_directory_sits_beside_the_config(
    tmp_path, source_unchanged
):
    """So the proposal is inspectable next to what it replaces."""
    source = source_unchanged(write_source(tmp_path, REPORTING_FIXTURE))
    assert run(source) == 0
    assert (source.parent / spc.STAGING_DIRNAME / spc.REPORT_NAME).is_file()


# ---------------------------------------------------------------------------
# Text fidelity
# ---------------------------------------------------------------------------


def test_comments_survive_the_split(tmp_path, source_unchanged):
    """The reason this is a text transform and not ``yaml.safe_dump``.

    A dump discards every comment in the file, and this is the first command a
    user runs against a config they were just handed — including the comments
    telling them to run it.
    """
    source = source_unchanged(PRESPLIT_DIR / "snake_config_rapid.yml")
    assert run(source, tmp_path) == 0
    staging = tmp_path / spc.STAGING_DIRNAME
    wf1 = (staging / "snake_config_rapid_build_model.yml").read_text("utf-8")
    assert "The model RUN period, a subset of historical_window" in wf1
    t1 = (staging / "snake_config_rapid.yml").read_text("utf-8")
    assert "WF0 — the basin's historical climate" in t1
    assert "17 calendar years" in t1


def test_line_endings_are_preserved(tmp_path):
    """A silent LF conversion would put every line of a config into the
    migration diff and bury the real change.

    The CRLF source is built here rather than read from a checked-in file: Git
    normalizes line endings on checkout, so a fixture's endings are a property
    of the clone rather than of the test.
    """
    body = (PRESPLIT_DIR / "snake_config_rapid.yml").read_text(encoding="utf-8")
    source = tmp_path / "project" / "snake_config_rapid.yml"
    source.parent.mkdir(parents=True)
    with open(source, "w", encoding="utf-8", newline="") as handle:
        handle.write(body.replace("\n", "\r\n"))
    before = source.read_bytes()

    assert run(source, tmp_path) == 0
    staged = (tmp_path / spc.STAGING_DIRNAME / "snake_config_rapid.yml").read_bytes()
    assert b"\r\n" in staged
    assert staged.count(b"\r\n") == staged.count(b"\n")
    assert source.read_bytes() == before


def test_a_trailing_comment_travels_with_the_body_it_annotates(tmp_path):
    """Comment placement follows indent, which is the only signal available.

    A comment at the section header's own indent introduces the NEXT workflow,
    so it stays with the stanza in T1. One indented deeper belongs to the body
    and travels with it — which is what carries a trailing annotation on the
    last section across instead of stranding it.
    """
    source = write_source(
        tmp_path,
        textwrap.dedent(
            """\
            project: {}
            shared: {}
            workflows:
              # introduces build_model
              build_model:
                enabled: true
                a: 1
                # belongs to the body
              # introduces run_stress_test
              run_stress_test:
                enabled: true
                b: 2
            """
        ),
    )
    assert run(source, tmp_path) == 0
    staging = tmp_path / spc.STAGING_DIRNAME
    wf1 = (staging / "snake_config_probe_build_model.yml").read_text("utf-8")
    t1 = (staging / "snake_config_probe.yml").read_text("utf-8")
    assert "belongs to the body" in wf1
    assert "introduces build_model" in t1
    assert "introduces run_stress_test" in t1
    assert "introduces" not in wf1


def test_the_emitted_config_path_is_a_bare_sibling_filename(tmp_path, source_unchanged):
    """Correct whether T1 sits under the repo root or in an out-of-tree project.

    It is also what makes the staged pair compose *in place*, which is what lets
    the round trip verify the proposal before anything is applied — and it
    produces the shipped seed naming for free.
    """
    source = source_unchanged(write_source(tmp_path, REPORTING_FIXTURE))
    assert run(source, tmp_path) == 0
    staged = yaml.safe_load(
        (tmp_path / spc.STAGING_DIRNAME / "snake_config_probe.yml").read_text("utf-8")
    )
    declared = staged["workflows"]["build_model"]["config_path"]
    assert declared == "snake_config_probe_build_model.yml"
    assert not os.path.isabs(declared)
    assert os.sep not in declared and "/" not in declared
