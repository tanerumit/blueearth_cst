"""Contract tests for scripts/run_workflows.py (design §7(g) + ext1-03).

The six §7(g) assertions plus the ext1-03 enabled:false skip test. Every test
monkeypatches subprocess.run to capture the argv list -- no real snakemake runs.
"""

import json
import os
import re
import sys
from pathlib import Path

import pytest

from blueearth_cst.experiment import simulation_record

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
import run_workflows as rw  # noqa: E402


class FakeResult:
    def __init__(self, returncode, stdout=""):
        self.returncode = returncode
        self.stdout = stdout


def _write_cfg(path, flags, project_dir=None):
    """Write a full-orchestration config with the given enabled flags dict.

    ``flags`` values are inserted verbatim into YAML so a caller can pass a raw
    string (e.g. '"true"' or 'yes') to exercise the parsed-value contract."""
    if project_dir is None:
        project_dir = path.parent / "project"
    lines = [
        "project:",
        f"  project_dir: {project_dir}",
        "workflows:",
    ]
    for name in rw.WORKFLOW_ORDER:
        lines.append(f"  {name}:")
        lines.append(f"    enabled: {flags[name]}")
    # Each stanza is closed; only simulation needs settings for the shared validator.
    text = "\n".join(lines) + "\n"
    text = text.replace(
        "  simulate_system:\n",
        f"  simulate_system:\n    config_path: {path.stem}-simulation.yml\n",
    )
    path.write_text(text, encoding="utf-8")
    (path.parent / f"{path.stem}-simulation.yml").write_text(
        "operation: simulate-and-metrics\nexperiment_name: test\n", encoding="utf-8"
    )


@pytest.fixture()
def capture_runs(monkeypatch):
    """Patch subprocess.run to record argv lists; default success exit 0."""
    calls = []
    exits = {}  # index -> returncode override
    # These wrapper-only fixtures deliberately use minimal v1-shaped mappings.
    # Archive capture is exercised with a valid project set separately.
    from blueearth_cst.shared import workflow_archive_launch

    monkeypatch.setattr(
        workflow_archive_launch,
        "prepare_workflow",
        lambda _name, config, _root, **_kwargs: (Path(config), Path(config)),
    )
    monkeypatch.setattr(rw, "_bind_workflow_archive", lambda *_args: None)
    monkeypatch.setattr(rw, "_capture_legacy_wf3_attempt", lambda *_args: "a" * 64)

    def fake_run(cmd, cwd=None, **kwargs):
        if cmd[0] == "git":
            stdout = "abc123\n" if "rev-parse" in cmd else ""
            return FakeResult(0, stdout=stdout)
        idx = len(calls)
        calls.append(cmd)
        if (
            "-s" in cmd
            and Path(cmd[cmd.index("-s") + 1]).name == "build_model.smk"
            and exits.get(idx, 0) == 0
        ):
            import yaml

            cfg = yaml.safe_load(Path(cmd[cmd.index("--configfile") + 1]).read_text())
            for leaf in rw.LEAVES:
                artifact = Path(cfg["project"]["project_dir"]) / leaf
                artifact.parent.mkdir(parents=True, exist_ok=True)
                artifact.touch()
        return FakeResult(exits.get(idx, 0))

    monkeypatch.setattr(
        rw,
        "run_project_child",
        lambda cmd, **kwargs: fake_run(cmd, **kwargs).returncode,
    )
    from scripts import generate_scenarios

    monkeypatch.setattr(
        generate_scenarios,
        "run_owned",
        lambda config_path, _root, cores, extra, **_kwargs: (
            fake_run(generate_scenarios._command(config_path, cores, extra)).returncode
        ),
    )
    return calls, exits


def _snakefiles_invoked(calls):
    """Return the ordered list of Snakefile names across captured argv."""
    out = []
    for cmd in calls:
        i = cmd.index("-s")
        out.append(Path(cmd[i + 1]).name)
    return out


def _manifests(project_dir: Path) -> list[Path]:
    """Return only parent invocation records, excluding workflow children."""
    paths = (project_dir / "config" / "runs" / "_engine" / "invocations").glob("*.json")
    return sorted(
        path
        for path in paths
        if json.loads(path.read_text(encoding="utf-8"))["workflow"] is None
    )


def _read_only_manifest(project_dir: Path) -> dict:
    """Read the sole invocation manifest below a test project root."""
    manifests = _manifests(project_dir)
    assert len(manifests) == 1
    return json.loads(manifests[0].read_text(encoding="utf-8"))


# --- §7(g) assertion 1: all-true -> all five in fixed order ------------------


def test_all_true_invokes_five_in_fixed_order(tmp_path, capture_runs):
    calls, _ = capture_runs
    cfg = tmp_path / "c.yml"
    _write_cfg(cfg, {n: "true" for n in rw.WORKFLOW_ORDER})
    rc = rw.run(str(cfg), cores=3, extra=[])
    assert rc == 0
    assert _snakefiles_invoked(calls) == [
        "analyze_climate.smk",
        "build_model.smk",
        "analyze_projections.smk",
        "generate_scenarios.smk",
        "simulate_system.smk",
    ]


# --- §7(g) assertion 2: --keep-going on projections only (flag parity) -------


def test_keep_going_on_projections_only(tmp_path, capture_runs):
    calls, _ = capture_runs
    cfg = tmp_path / "c.yml"
    _write_cfg(cfg, {n: "true" for n in rw.WORKFLOW_ORDER})
    rw.run(str(cfg), cores=3, extra=[])
    by_sf = {Path(cmd[cmd.index("-s") + 1]).name: cmd for cmd in calls}
    assert "--keep-going" in by_sf["analyze_projections.smk"]
    assert "--keep-going" not in by_sf["build_model.smk"]
    assert "--keep-going" not in by_sf["simulate_system.smk"]
    assert "--keep-going" not in by_sf["analyze_climate.smk"]


# --- §7(g) assertion 3: missing enabled: key -> nonzero, named --------------


def test_missing_enabled_key_errors(tmp_path):
    cfg = tmp_path / "c.yml"
    cfg.write_text(
        "workflows:\n"
        # Every required section present but one: the closed set is all-or-
        # error, so an incomplete config would otherwise fail on whichever
        # section came first rather than on the one this test is about.
        "  analyze_climate:\n    enabled: true\n"
        "  generate_scenarios:\n    enabled: true\n"
        "  build_model:\n    enabled: true\n"
        "  analyze_projections:\n    enabled: true\n"
        "  simulate_system:\n    other: 1\n",  # no enabled:
        encoding="utf-8",
    )
    with pytest.raises(rw.ConfigError) as exc:
        rw.read_enabled_flags(str(cfg))
    assert "simulate_system.enabled" in str(exc.value)
    # And the CLI surfaces it as a nonzero exit.
    rc = rw.main(["--config", str(cfg)])
    assert rc != 0


def test_missing_workflows_section_errors(tmp_path):
    """A projections-only config (no workflows: section) is rejected (contract a/b)."""
    cfg = tmp_path / "proj.yml"
    cfg.write_text("data_sources: config/catalogs/cmip6_data.yml\n", encoding="utf-8")
    with pytest.raises(rw.ConfigError) as exc:
        rw.read_enabled_flags(str(cfg))
    assert "workflows" in str(exc.value)


# --- §7(g) assertion 4: parsed-value bool contract --------------------------


@pytest.mark.parametrize("bad", ['"true"', '"false"', "1", "0"])
def test_non_bool_enabled_rejected(tmp_path, bad):
    """Quoted strings and integers do NOT parse to bool -> rejected (contract c)."""
    cfg = tmp_path / "c.yml"
    flags = {n: "true" for n in rw.WORKFLOW_ORDER}
    flags["build_model"] = bad
    _write_cfg(cfg, flags)
    with pytest.raises(rw.ConfigError) as exc:
        rw.read_enabled_flags(str(cfg))
    assert "build_model.enabled" in str(exc.value)


@pytest.mark.parametrize("spelling", ["yes", "on", "true", "True"])
def test_unquoted_boolean_spellings_accepted(tmp_path, spelling):
    """Unquoted yes/on/true resolve to True under YAML 1.1 -> accepted (contract c)."""
    cfg = tmp_path / "c.yml"
    flags = {n: "true" for n in rw.WORKFLOW_ORDER}
    flags["build_model"] = spelling
    _write_cfg(cfg, flags)
    parsed = rw.read_enabled_flags(str(cfg))
    assert parsed["build_model"] is True


# --- §7(g) assertion 5: first nonzero -> stop, later not invoked, return code -


def test_first_nonzero_stops_and_returns_code(tmp_path, capture_runs):
    calls, exits = capture_runs
    exits[0] = 7  # first invoked workflow (analyze_climate) fails
    cfg = tmp_path / "c.yml"
    _write_cfg(cfg, {n: "true" for n in rw.WORKFLOW_ORDER})
    rc = rw.run(str(cfg), cores=3, extra=[])
    assert rc == 7
    # Only the first workflow was invoked; projections/experiment were not.
    assert _snakefiles_invoked(calls) == ["analyze_climate.smk"]


# --- §7(g) assertion 6: --cores / -- <extra> forwarded to EVERY invocation ---


def test_cores_and_extra_forwarded_to_every_invocation(tmp_path, capture_runs):
    calls, _ = capture_runs
    cfg = tmp_path / "c.yml"
    _write_cfg(cfg, {n: "true" for n in rw.WORKFLOW_ORDER})
    rw.run(str(cfg), cores=8, extra=["--dry-run", "--unlock"])
    assert len(calls) == 5
    for cmd in calls:
        assert cmd[cmd.index("-c") + 1] == "8"
        assert "--dry-run" in cmd
        assert "--unlock" in cmd


def test_cli_strips_double_dash_sentinel(tmp_path, capture_runs):
    """The leading `--` sentinel is stripped before forwarding (contract e)."""
    calls, _ = capture_runs
    cfg = tmp_path / "c.yml"
    _write_cfg(cfg, {n: "true" for n in rw.WORKFLOW_ORDER})
    rw.main(["--config", str(cfg), "--cores", "2", "--", "--dry-run"])
    for cmd in calls:
        assert "--" not in cmd or "--dry-run" in cmd  # no bare sentinel forwarded
        assert "--dry-run" in cmd


# --- ext1-03: enabled:false skip test, FRESH tmp_path, boundary assertion ----


def test_enabled_false_skips_at_subprocess_boundary(tmp_path, capture_runs):
    """Design §9 ext1-03: in a FRESH temp project_dir, disabling a workflow means
    the wrapper does NOT invoke its Snakefile, and DOES invoke the others.
    Asserted at the subprocess boundary (argv capture), not output presence --
    a reused dir could carry stale outputs."""
    calls, _ = capture_runs
    project_dir = tmp_path / "fresh_project"
    project_dir.mkdir()
    cfg = tmp_path / "c.yml"
    flags = {n: "true" for n in rw.WORKFLOW_ORDER}
    flags["analyze_projections"] = "false"
    _write_cfg(cfg, flags, project_dir=str(project_dir))

    rc = rw.run(str(cfg), cores=3, extra=[])
    assert rc == 0
    invoked = _snakefiles_invoked(calls)
    assert "analyze_projections.smk" not in invoked
    assert invoked == [
        "analyze_climate.smk",
        "build_model.smk",
        "generate_scenarios.smk",
        "simulate_system.smk",
    ]


def test_all_enabled_inverse_all_invoked(tmp_path, capture_runs):
    """The inverse of the skip test: all true -> all five invoked."""
    calls, _ = capture_runs
    cfg = tmp_path / "c.yml"
    _write_cfg(cfg, {n: "true" for n in rw.WORKFLOW_ORDER})
    rw.run(str(cfg), cores=3, extra=[])
    assert len(_snakefiles_invoked(calls)) == 5


def test_success_manifest_is_initialized_before_first_workflow_and_finalized(
    tmp_path, monkeypatch
):
    """The unique manifest exists as running before the child is launched."""
    project_dir = tmp_path / "project"
    cfg = tmp_path / "c.yml"
    _write_cfg(cfg, {n: "true" for n in rw.WORKFLOW_ORDER}, project_dir)
    calls = []

    def fake_run(cmd, cwd=None, **kwargs):
        if cmd[0] == "git":
            return FakeResult(0, stdout="abc123\n" if "rev-parse" in cmd else "")
        calls.append(cmd)
        running = _read_only_manifest(project_dir)
        assert running["status"] == "running"
        assert running["ended_at_utc"] is None
        if "build_model.smk" in cmd:
            _staged(project_dir, rw.LEAVES)
        return FakeResult(0)

    monkeypatch.setattr(
        rw,
        "run_project_child",
        lambda cmd, **kwargs: fake_run(cmd, **kwargs).returncode,
    )

    from scripts import generate_scenarios

    monkeypatch.setattr(
        generate_scenarios,
        "run_owned",
        lambda config_path, _root, cores, extra, **_kwargs: (
            fake_run(generate_scenarios._command(config_path, cores, extra)).returncode
        ),
    )

    assert rw.run(str(cfg), cores=5, extra=["--dry-run"]) == 0

    manifest = _read_only_manifest(project_dir)
    assert manifest["schema_version"] == "invocation/1"
    assert manifest["status"] == "succeeded"
    assert manifest["exit_code"] == 0
    assert manifest["ended_at_utc"].endswith("Z")
    assert manifest["mode"] == "dry_run"
    assert manifest["work_performed"] == "no"
    assert manifest["configuration"]["source_config_sha256"] == rw.file_sha256(cfg)
    assert manifest["configuration"]["effective_config_sha256"]
    # Derived from WORKFLOW_ORDER rather than restated: a literal list is what
    # made this the last of nine tests to fail when the set widened to four,
    # each for the same reason.
    assert [item["workflow"] for item in manifest["children"]] == list(
        rw.WORKFLOW_ORDER
    )
    assert len(calls) == len(rw.WORKFLOW_ORDER)


def test_no_op_invocations_each_get_an_immutable_manifest(tmp_path, capture_runs):
    """Repeated all-disabled calls create separate finalized records."""
    project_dir = tmp_path / "project"
    cfg = tmp_path / "c.yml"
    _write_cfg(cfg, {n: "false" for n in rw.WORKFLOW_ORDER}, project_dir)

    assert rw.run(str(cfg), cores=3, extra=[]) == 0
    assert rw.run(str(cfg), cores=3, extra=[]) == 0

    manifests = _manifests(project_dir)
    assert len(manifests) == 2
    for path in manifests:
        manifest = json.loads(path.read_text(encoding="utf-8"))
        assert manifest["status"] == "succeeded"
        assert manifest["work_performed"] == "no"
        assert manifest["requested_workflows"] == []
        assert manifest["children"] == []


def test_failure_manifest_records_stop_boundary(tmp_path, capture_runs):
    """A child failure finalizes its result and marks later work not run."""
    _, exits = capture_runs
    exits[0] = 9
    project_dir = tmp_path / "project"
    cfg = tmp_path / "c.yml"
    _write_cfg(cfg, {n: "true" for n in rw.WORKFLOW_ORDER}, project_dir)

    assert rw.run(str(cfg), cores=3, extra=[]) == 9

    manifest = _read_only_manifest(project_dir)
    # analyze_climate leads WORKFLOW_ORDER, so it is the one exits[0] hits.
    assert manifest["exit_code"] == 9
    assert [item["workflow"] for item in manifest["children"]] == ["analyze_climate"]
    child = json.loads(
        (
            _manifests(project_dir)[0].parent
            / f"{manifest['children'][0]['invocation_id']}.json"
        ).read_text(encoding="utf-8")
    )
    assert child["status"] == "failed"
    assert child["exit_code"] == 9


def test_subprocess_exception_finalizes_failure_manifest(
    tmp_path, monkeypatch, capture_runs
):
    """Launch errors leave a terminal record rather than a stale running one."""
    project_dir = tmp_path / "project"
    cfg = tmp_path / "c.yml"
    _write_cfg(cfg, {n: "true" for n in rw.WORKFLOW_ORDER}, project_dir)

    def fake_run(cmd, cwd=None, **kwargs):
        if cmd[0] == "git":
            return FakeResult(0, stdout="abc123\n" if "rev-parse" in cmd else "")
        raise OSError("snakemake executable missing")

    monkeypatch.setattr(
        rw,
        "run_project_child",
        lambda cmd, **kwargs: fake_run(cmd, **kwargs).returncode,
    )

    with pytest.raises(OSError, match="snakemake executable missing"):
        rw.run(str(cfg), cores=3, extra=[])

    manifest = _read_only_manifest(project_dir)
    assert manifest["status"] == "failed"
    assert manifest["exit_code"] is None
    assert manifest["error"]["type"] == "OSError"
    assert [item["workflow"] for item in manifest["children"]] == ["analyze_climate"]


def test_manifest_sanitizes_sensitive_extra_args(tmp_path, capture_runs):
    """Sensitive flag and --config assignment values never reach the record."""
    project_dir = tmp_path / "project"
    cfg = tmp_path / "c.yml"
    _write_cfg(cfg, {n: "false" for n in rw.WORKFLOW_ORDER}, project_dir)
    extra = [
        "--config",
        "threshold=4",
        "api_token=token-value",
        "clientSecret=camel-secret-value",
        "--password",
        "password-value",
    ]

    rw.run(str(cfg), cores=3, extra=extra)

    manifest_text = _manifests(project_dir)[0].read_text(encoding="utf-8")
    manifest = json.loads(manifest_text)
    assert "token-value" not in manifest_text
    assert "camel-secret-value" not in manifest_text
    assert "password-value" not in manifest_text
    assert "threshold=4" in manifest["command"]
    assert "api_token=<redacted>" in manifest["command"]


def test_sensitive_args_are_redacted_from_console(tmp_path, capture_runs, capsys):
    """The wrapper's command echo does not defeat manifest sanitization."""
    project_dir = tmp_path / "project"
    cfg = tmp_path / "c.yml"
    flags = {n: "false" for n in rw.WORKFLOW_ORDER}
    flags["build_model"] = "true"
    _write_cfg(cfg, flags, project_dir)

    rw.run(str(cfg), cores=3, extra=["--config", "api_token=visible-secret"])

    output = capsys.readouterr().out
    assert "visible-secret" not in output
    assert "api_token=<redacted>" in output


# --- contract (h): the wrapper's own console narration ----------------------


def _group_raw_lines(output, label):
    """The raw lines under one ``  <label>`` group, indentation intact."""
    lines = output.splitlines()
    start = lines.index(f"  {label}") + 1
    kept = []
    for line in lines[start:]:
        if not line.startswith("    "):
            break
        kept.append(line)
    return kept


def _group_lines(output, label):
    """The same lines, stripped -- for asserting on a continuation line."""
    return [line.strip() for line in _group_raw_lines(output, label)]


def _group_rows(output, label):
    """The ``key -> value`` rows under one ``  <label>`` group of a block."""
    rows = {}
    for line in _group_lines(output, label):
        key, value = line.split(maxsplit=1)
        rows[key] = value
    return rows


def _run_and_capture(tmp_path, capsys, flags, *, cores=3, extra=None):
    """Run the wrapper over a config with ``flags`` and return its stdout."""
    project_dir = tmp_path / "gabon_project"
    cfg = tmp_path / "c.yml"
    _write_cfg(cfg, flags, project_dir=str(project_dir))
    code = rw.run(str(cfg), cores=cores, extra=extra or [])
    return code, capsys.readouterr().out, project_dir


def test_opening_block_states_the_project_and_the_config_in_one_group(
    tmp_path, capture_runs, capsys
):
    """A console of four back-to-back Snakemake runs must say whose they are.

    Snakemake's own preamble names the host and the job counts and never the
    project, so before this block a scrolled-back or pasted console could not be
    attributed to a project or a config without asking.

    ONE group: what came from the command line and what came from the config
    were two, and that is a distinction the writer cares about rather than the
    reader. `cores` went with the split -- it is not a property of the project,
    and every hand-off band prints the `-c N` it forwarded.
    """
    _, out, project_dir = _run_and_capture(
        tmp_path, capsys, {n: "true" for n in rw.WORKFLOW_ORDER}, cores=7
    )
    assert "  run_workflows" in out.splitlines()  # the banner's head line
    assert "  run" not in out.splitlines()  # the old first group is gone
    rows = _group_rows(out, "settings")
    assert rows["project"] == "gabon_project"  # basename, no project_name key
    assert rows["folder"] == str(project_dir).replace(os.sep, "/")
    assert "c.yml" in rows["config"]
    assert "cores" not in rows


def test_opening_block_diagrams_the_sequence_and_marks_the_disabled(
    tmp_path, capture_runs, capsys
):
    """Every workflow appears; only the enabled ones are numbered.

    A disabled workflow silently absent from the list is indistinguishable from
    one the wrapper does not know about -- so it is shown, marked, and the
    positions count only what will actually be invoked.
    """
    flags = {n: "true" for n in rw.WORKFLOW_ORDER}
    flags["analyze_projections"] = "false"
    _, out, _ = _run_and_capture(tmp_path, capsys, flags)
    assert "sequence  (4 of 5 enabled, in order)" in out
    assert "[1/4]  wf0 analyze_climate" in out
    assert "[2/4]  wf1 build_model" in out
    assert "[3/4]  wf3 generate_scenarios" in out
    assert "[4/4]  wf4 simulate_system" in out
    # Present, marked, and NOT given a position.
    assert "wf2 analyze_projections  disabled" in out
    assert "[4/4]  wf2" not in out


def test_the_sequence_is_drawn_as_a_rail_of_nodes(tmp_path, capture_runs, capsys):
    """Keyed by node, and keyed DIFFERENTLY for what will not be invoked.

    The rows sat at the same indent as the `run` group's key/value pairs, so
    the diagram's shape did not say it was a diagram. A filled node for a
    workflow that will run and a hollow one for a workflow that will not is
    legible before any of the text is read -- and costs one character where the
    framed boxes this replaced cost three lines and forty columns each.
    """
    flags = {n: "true" for n in rw.WORKFLOW_ORDER}
    flags["analyze_projections"] = "false"
    _, out, _ = _run_and_capture(tmp_path, capsys, flags)
    lines = [line.strip() for line in out.splitlines()]

    enabled = lines.index(next(ln for ln in lines if "[1/4]  wf0" in ln))
    assert lines[enabled].startswith(rw._NODE_ON)

    disabled = lines.index(next(ln for ln in lines if "wf2 analyze_projections" in ln))
    assert lines[disabled].startswith(rw._NODE_OFF)
    # The nodes are threaded, not merely stacked.
    assert rw._RAIL in lines[enabled + 1 : disabled]


def test_the_opening_block_states_the_basin_settings(tmp_path, capture_runs, capsys):
    """What the run is ABOUT, next to where it is: bbox, extent, window.

    These are the values someone checks before letting a multi-hour run
    proceed, and reading them meant opening the config in another window.
    """
    project_dir = tmp_path / "gabon_project"
    region = project_dir / "data" / "spatial" / "geoms"
    region.mkdir(parents=True)
    (region / "region.geojson").write_text(
        json.dumps(
            {
                "type": "FeatureCollection",
                "features": [
                    {
                        "type": "Feature",
                        "geometry": {
                            "type": "Polygon",
                            "coordinates": [
                                [
                                    [9.6, 0.4],
                                    [9.8, 0.4],
                                    [9.8, 0.6],
                                    [9.6, 0.6],
                                    [9.6, 0.4],
                                ]
                            ],
                        },
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    cfg = tmp_path / "c.yml"
    _write_cfg(
        cfg, {n: "true" for n in rw.WORKFLOW_ORDER}, project_dir=str(project_dir)
    )
    cfg.write_text(
        cfg.read_text(encoding="utf-8") + "basin:\n"
        "  region: \"{'subbasin': [9.666, 0.4476], 'uparea': 100}\"\n"
        "  resolution: 0.00833\n",
        encoding="utf-8",
    )
    rw.run(str(cfg), cores=3, extra=[])
    out = capsys.readouterr().out
    rows = _group_rows(out, "settings")
    lines = _group_lines(out, "settings")

    assert rows["region"] == "{'subbasin': [9.666, 0.4476], 'uparea': 100}"
    assert rows["resolution"].startswith("0.00833 deg")
    # The delineated box is the region row CONTINUING -- one setting, stated and
    # then answered -- so it carries no key of its own and is aligned into the
    # value column (`~22 x 22 km` at this latitude; a scale, hence `approx`).
    region_at = next(i for i, line in enumerate(lines) if line.startswith("region"))
    assert lines[region_at + 1] == (
        "lon 9.6000 .. 9.8000, lat 0.4000 .. 0.6000  (approx 22 x 22 km)"
    )
    raw = _group_raw_lines(out, "settings")
    assert raw[region_at + 1].index("lon ") == raw[region_at].index("{'subbasin'")


def test_the_bbox_says_it_is_absent_rather_than_deriving_one(
    tmp_path, capture_runs, capsys
):
    """A box from `{'subbasin': [lon, lat], 'uparea': 100}` would be invented.

    The specification names an outlet and an upstream-area threshold; the extent
    of the basin they delineate is not knowable from them, and the bbox row is
    exactly where a reader has no way to check a fabricated number.
    """
    cfg = tmp_path / "c.yml"
    project_dir = tmp_path / "fresh_project"
    _write_cfg(
        cfg, {n: "true" for n in rw.WORKFLOW_ORDER}, project_dir=str(project_dir)
    )
    cfg.write_text(
        cfg.read_text(encoding="utf-8") + "basin:\n"
        "  region: \"{'subbasin': [9.666, 0.4476], 'uparea': 100}\"\n",
        encoding="utf-8",
    )
    rw.run(str(cfg), cores=3, extra=[])
    out = capsys.readouterr().out
    lines = _group_lines(out, "settings")

    region_at = next(i for i, line in enumerate(lines) if line.startswith("region"))
    assert "9.666" in lines[region_at]  # the specification is still stated
    assert lines[region_at + 1].startswith("not delineated yet")
    assert "approx" not in out  # and no extent, since there is no box


def test_the_basin_rows_are_omitted_when_the_config_declares_no_basin(
    tmp_path, capture_runs, capsys
):
    """The wrapper validates `workflows:` and nothing else, so both basin rows
    are optional -- but project, folder and config always answer."""
    _, out, _ = _run_and_capture(
        tmp_path, capsys, {n: "true" for n in rw.WORKFLOW_ORDER}
    )
    rows = _group_rows(out, "settings")
    assert set(rows) == {"project", "folder", "config"}
    # No orphaned continuation either: with no region asked for, there is
    # nothing whose absence is worth a line.
    assert "not delineated yet" not in out


def test_an_extent_is_withheld_when_the_geometry_is_not_in_degrees(tmp_path):
    """A projected polygon multiplied by 111 would print a confident wrong number.

    The bbox itself is still shown: it carries its units on its face, so a
    reader can see what it is. The km scale cannot.
    """
    projected = (500000.0, 4649776.0, 520000.0, 4669776.0)
    assert rw._bbox_extent_km(projected) is None
    assert rw._bbox_extent_km((9.6, 0.4, 9.8, 0.6)) is not None


def test_a_declared_bbox_member_is_preferred_over_walking_the_coordinates(tmp_path):
    """It is what every other reader of the artifact sees."""
    path = tmp_path / "region.geojson"
    path.write_text(
        json.dumps(
            {
                "type": "Feature",
                "bbox": [1.0, 2.0, 3.0, 4.0],
                "geometry": {"type": "Point", "coordinates": [99.0, 99.0]},
            }
        ),
        encoding="utf-8",
    )
    assert rw._geojson_bbox(path) == (1.0, 2.0, 3.0, 4.0)


def test_a_dry_run_says_so_in_the_opening_block(tmp_path, capture_runs, capsys):
    """A dry run's console is otherwise nearly identical to a real one's."""
    _, out, _ = _run_and_capture(
        tmp_path,
        capsys,
        {n: "true" for n in rw.WORKFLOW_ORDER},
        extra=["--dry-run"],
    )
    assert "mode" in out and "dry run -- nothing is executed" in out


def test_each_invoked_workflow_gets_a_hand_off_band_at_its_leading_edge(
    tmp_path, capture_runs, capsys
):
    """Position, identity and when it started -- but no closing band on success.

    Every workflow signs off with its own `wfN <name> done in <h:mm:ss>`, so a
    runner band repeating that was a second copy of one fact. The duration
    survives in the closing block's `ran` group.
    """
    flags = {n: "true" for n in rw.WORKFLOW_ORDER}
    flags["analyze_projections"] = "false"
    _, out, _ = _run_and_capture(tmp_path, capsys, flags)
    assert re.search(r"\[1/4]  wf0 analyze_climate  --  starting \d\d:\d\d:\d\d", out)
    assert re.search(r"\[4/4]  wf4 simulate_system  --  starting \d\d:\d\d:\d\d", out)
    assert "  --  done in " not in out
    # Flush left, title and command both. A band has no group label and no rows,
    # so an indent would only make the line a reader scans for start one column
    # later than the rule announcing it.
    lines = out.splitlines()
    title_at = next(
        i for i, line in enumerate(lines) if "wf0 analyze_climate  --" in line
    )
    assert lines[title_at].startswith("[1/4]")
    assert lines[title_at - 1] == rw._RULE  # the rule it hangs from
    assert lines[title_at + 1].startswith("snakemake ")
    # A disabled workflow gets NO band -- the sequence diagram above already
    # named it, once, before anything ran.
    assert "wf2 analyze_projections  --  starting" not in out


def test_every_wrapper_utterance_is_bounded_by_a_rule(tmp_path, capture_runs, capsys):
    """The rule is the wrapper's signature, and it is the whole point.

    Nested one inside the other, a wrapper block and a workflow's own block are
    the same label over the same-shaped rows — `run` over `project`/`config` in
    both — so a scrolled-back console could not be parsed into who said what.
    Every line the runner speaks first therefore sits under a rule, and nothing
    else in this console draws one.
    """
    flags = {n: "true" for n in rw.WORKFLOW_ORDER}
    flags["analyze_projections"] = "false"
    _, out, _ = _run_and_capture(tmp_path, capsys, flags)
    lines = out.splitlines()
    rule = "=" * 80
    # Opening banner (2), one per hand-off band (3 = 3 workflows, leading edge
    # only on a clean run), and the closing banner's pair. A bare count is the
    # assertion that would pass on any two extra rules, so check placement.
    assert lines[0] == rule and lines[1] == "  run_workflows" and lines[2] == rule
    assert lines[-1] == rule
    for index, line in enumerate(lines):
        if line.startswith("  [") and "  --  " in line:
            assert lines[index - 1] == rule, f"unruled hand-off at {index}: {line}"
    # And the workflow-internal grammar never appears at this level.
    assert " - run_workflows - " not in out


def test_the_console_is_not_muted_by_the_rule_log_level(
    tmp_path, capture_runs, capsys, monkeypatch
):
    """`CST_LOG_LEVEL` quietens rule logs; the frame around them is not one.

    The wrapper deliberately does not wear `log_row`'s
    `HH:MM:SS - <module> - ...`, which every line reported from INSIDE a
    workflow wears — so it is not governed by the floor that grammar carries,
    and setting it must not delete the only statement of which project and
    which config a run was.
    """
    monkeypatch.setenv("CST_LOG_LEVEL", "WARNING")
    _, out, _ = _run_and_capture(
        tmp_path, capsys, {n: "true" for n in rw.WORKFLOW_ORDER}
    )
    assert "  run_workflows" in out.splitlines()
    assert "  sequence  (5 of 5 enabled, in order)" in out
    assert re.search(r"\[1/5]  wf0 analyze_climate  --  starting \d\d:\d\d:\d\d", out)
    assert "run_workflows done in" in out


def test_closing_block_names_what_ran_how_long_and_where_it_landed(
    tmp_path, capture_runs, capsys
):
    """The three answers a finished run owes: what, how long, and where."""
    flags = {n: "true" for n in rw.WORKFLOW_ORDER}
    flags["analyze_projections"] = "false"
    _, out, project_dir = _run_and_capture(tmp_path, capsys, flags)
    root = str(project_dir).replace(os.sep, "/")
    assert "run_workflows done in 0:00:0" in out
    wrote = _group_rows(out, "wrote")
    assert wrote["project"] == root
    assert wrote["logs"] == f"{root}/logs/"
    assert wrote["invocation"].startswith(f"{root}/config/runs/_engine/invocations/")
    # `ran` lists what was invoked, in order, and nothing else -- a group headed
    # "ran" naming a workflow that did not is worse than not printing it.
    ran = out.split("\n  ran\n")[1].split("\n\n")[0].splitlines()
    assert [line.split()[0] for line in ran] == ["wf0", "wf1", "wf3", "wf4"]


def test_failure_console_carries_the_verdict_and_what_did_not_run(
    tmp_path, capture_runs, capsys
):
    """The stop boundary, stated: the exit code, and everything left behind."""
    _, exits = capture_runs
    exits[1] = 4  # build_model, the second invoked workflow
    code, out, _ = _run_and_capture(
        tmp_path, capsys, {n: "true" for n in rw.WORKFLOW_ORDER}
    )
    assert code == 4
    assert "[2/5]  wf1 build_model  --  FAILED (exit 4) after 0:00:0" in out
    assert "stopping; later workflows not invoked" in out
    assert "run_workflows FAILED in 0:00:0" in out
    assert (
        "not run: wf2 analyze_projections, wf3 generate_scenarios, "
        "wf4 simulate_system" in out
    )
    assert "the failing workflow's own output is printed above" in out


def test_a_launch_error_still_closes_with_a_report(
    tmp_path, monkeypatch, capsys, capture_runs
):
    """An OSError out of subprocess.run must not end in a bare traceback.

    The manifest is finalized on this path for the same reason; the console
    report is the half a person actually reads.
    """
    project_dir = tmp_path / "project"
    cfg = tmp_path / "c.yml"
    _write_cfg(cfg, {n: "true" for n in rw.WORKFLOW_ORDER}, project_dir)

    def fake_run(cmd, cwd=None, **kwargs):
        if cmd[0] == "git":
            return FakeResult(0, stdout="abc123\n" if "rev-parse" in cmd else "")
        raise OSError("snakemake executable missing")

    monkeypatch.setattr(
        rw,
        "run_project_child",
        lambda cmd, **kwargs: fake_run(cmd, **kwargs).returncode,
    )
    with pytest.raises(OSError):
        rw.run(str(cfg), cores=3, extra=[])

    out = capsys.readouterr().out
    assert "run_workflows FAILED in" in out
    assert "wf0 analyze_climate  FAILED (OSError)" in out
    assert "not run: wf1 build_model, wf2 analyze_projections" in out
    # Two claims that are FALSE when no child ever launched.
    assert "/logs/" not in out
    assert "printed above" not in out


def test_a_no_op_invocation_says_so_rather_than_printing_empty_groups(
    tmp_path, capture_runs, capsys
):
    """Nothing enabled: a sentence, never a group label with nothing under it."""
    _, out, _ = _run_and_capture(
        tmp_path, capsys, {n: "false" for n in rw.WORKFLOW_ORDER}
    )
    assert "nothing to invoke -- 0 of 5 workflows are enabled here" in out
    assert "nothing ran -- every workflow was disabled" in out
    assert "  ran" not in out.splitlines()
    assert "  sequence" not in out


def test_the_console_is_ascii_but_for_the_three_rail_glyphs(
    tmp_path, capture_runs, capsys
):
    """The non-ASCII budget is exactly `●`, `○` and `│`, and nothing else.

    A Windows locale is cp1252 and RAISES on the rest, so until 2026-09-17 this
    console was ASCII throughout. The rail spends three characters of that
    budget and `_enable_utf8_stdout` is what pays for them; every other line
    stays inside cp1252, which is what keeps a redirected run legible where the
    Snakemake children write through the locale codec into the same file.

    Pinned as a SET, not as a `.isascii()` flip: the cost of the reconfiguration
    is that nothing raises any more, so a stray glyph added later would reach a
    real console with no test between it and the user.
    """
    # One disabled workflow, so the sequence renders a hollow node as well as a
    # filled one. WHICH one is disabled is immaterial here; it is
    # `analyze_projections` rather than `build_model` only because disabling the
    # latter while `simulate_system` is enabled now trips the contract (i)
    # preflight, on a scratch project that has no wf1 leaves.
    flags = {n: "true" for n in rw.WORKFLOW_ORDER}
    flags["analyze_projections"] = "false"
    _, out, _ = _run_and_capture(tmp_path, capsys, flags)
    out.encode("utf-8")
    assert set(out) - set(map(chr, range(128))) == {
        rw._NODE_ON,
        rw._NODE_OFF,
        rw._RAIL,
    }
    # The rest of the console still clears the bar it cleared before the rail.
    for line in out.splitlines():
        if not {rw._NODE_ON, rw._NODE_OFF, rw._RAIL} & set(line):
            line.encode("cp1252")


def test_the_runner_tells_its_children_the_workflow_is_already_named(
    tmp_path, capsys, monkeypatch, capture_runs
):
    """Each hand-off band names the workflow, so the child's block need not.

    On the CHILD's environment, and asserted together with the parent's
    staying clean. Setting `os.environ` in the runner covered both spawn paths
    in one line and leaked: nothing unsets it, so inside one process a single
    `run()` silenced the title for everything afterwards -- nine tests in
    `test_snake_utils.py`, visible only to the full suite because each file
    passes on its own.
    """
    monkeypatch.delenv(rw.console_style.ANNOUNCED_ENV, raising=False)
    envs = []

    def fake_run(cmd, cwd=None, **kwargs):
        if cmd[0] == "git":
            return FakeResult(0, stdout="abc123\n" if "rev-parse" in cmd else "")
        envs.append(kwargs.get("env"))
        return FakeResult(0)

    monkeypatch.setattr(
        rw,
        "run_project_child",
        lambda cmd, **kwargs: fake_run(cmd, **kwargs).returncode,
    )
    project_dir = tmp_path / "gabon_project"
    cfg = tmp_path / "c.yml"
    # `build_model` alone: it is the plain `subprocess.run` path, and enabling
    # `simulate_system` would trip the contract (i) preflight on a scratch
    # project with no wf1 leaves.
    flags = {n: "false" for n in rw.WORKFLOW_ORDER}
    flags["build_model"] = "true"
    _write_cfg(cfg, flags, project_dir=str(project_dir))
    rw.run(str(cfg), cores=3, extra=[])
    capsys.readouterr()

    assert [env[rw.console_style.ANNOUNCED_ENV] for env in envs] == ["1"]
    assert rw.console_style.ANNOUNCED_ENV not in os.environ  # never leaked


def test_the_announcement_rides_on_the_simulation_runners_own_environment(
    tmp_path, capsys, monkeypatch
):
    """The other spawn path builds its own env, so the flag is added to it.

    Covered separately because this is the branch that MERGES: WF4 goes
    through `simulation_command`, whose environment carries the invocation id
    and the selected operation. Replacing it rather than adding to it would
    take those with it.
    """
    monkeypatch.delenv(rw.console_style.ANNOUNCED_ENV, raising=False)
    envs = []

    def fake_run(cmd, cwd=None, **kwargs):
        if cmd[0] == "git":
            return FakeResult(0, stdout="abc123\n" if "rev-parse" in cmd else "")
        envs.append(kwargs.get("env"))
        return FakeResult(0)

    monkeypatch.setattr(
        rw,
        "run_project_child",
        lambda cmd, **kwargs: fake_run(cmd, **kwargs).returncode,
    )
    captures = []
    monkeypatch.setattr(
        simulation_record,
        "capture_simulation_sources_v2",
        lambda config, root, invocation: (
            captures.append((Path(config), Path(root), invocation))
            or tmp_path / "capture.json"
        ),
    )
    project_dir = tmp_path / "gabon_project"
    # The wf1 leaves the contract (i) preflight requires, without running wf1.
    for leaf in rw.LEAVES:
        artifact = project_dir / leaf
        artifact.parent.mkdir(parents=True, exist_ok=True)
        artifact.touch()
    cfg = tmp_path / "c.yml"
    flags = {n: "false" for n in rw.WORKFLOW_ORDER}
    flags["simulate_system"] = "true"
    _write_cfg(cfg, flags, project_dir=str(project_dir))
    rw.run(str(cfg), cores=3, extra=[])
    capsys.readouterr()

    assert len(envs) == 1
    assert envs[0][rw.console_style.ANNOUNCED_ENV] == "1"
    # The runner's own keys survived the merge.
    assert envs[0]["CST_SIMULATION_OPERATION"] == "simulate-and-metrics"
    parent = _read_only_manifest(project_dir)
    assert (
        envs[0]["CST_SIMULATION_INVOCATION_ID"]
        == parent["children"][0]["invocation_id"]
    )
    assert captures == [
        (
            cfg.resolve(),
            project_dir.resolve(),
            parent["children"][0]["invocation_id"],
        )
    ]
    assert rw.console_style.ANNOUNCED_ENV not in os.environ


def test_the_runner_declares_utf8_on_its_own_stdout(monkeypatch):
    """`main` reconfigures before it prints, or the rail kills a redirected run.

    The glyphs are unreachable under a cp1252 locale without this call, and the
    failure is not a styling defect: `print` raises before the first workflow
    starts. Asserted on `main` rather than on a render, because that is the one
    entry point a user invokes and the only place the call can be forgotten.
    """
    seen: list[dict[str, str]] = []

    class _Stdout:
        def reconfigure(self, **kwargs):
            seen.append(kwargs)

        def write(self, _text):
            return 0

        def flush(self):
            pass

    monkeypatch.setattr(sys, "stdout", _Stdout())
    with pytest.raises(SystemExit):
        rw.main(["--help"])
    assert seen == [{"encoding": "utf-8"}]


def test_utf8_declaration_never_breaks_a_run_it_cannot_apply_to(monkeypatch):
    """A stdout without `reconfigure` costs the glyphs, never the run.

    pytest's own capture object is the common one, so this path is exercised by
    every other test in this file; it is pinned here because the alternative --
    letting the AttributeError out -- would trade a whole run for a banner.
    """

    class _Plain:
        def write(self, _text):
            return 0

        def flush(self):
            pass

    monkeypatch.setattr(sys, "stdout", _Plain())
    rw._enable_utf8_stdout()  # must not raise


def test_the_console_narration_never_leaks_a_secret(tmp_path, capture_runs, capsys):
    """Every new line that can carry `extra` goes through `sanitize_argv`."""
    # Exactly one enabled workflow, so `extra` reaches exactly one invocation.
    # `build_model` rather than `simulate_system`, for the contract (i) reason
    # given on the cp1252 test above -- the choice is immaterial to redaction.
    flags = {n: "false" for n in rw.WORKFLOW_ORDER}
    flags["build_model"] = "true"
    _, out, _ = _run_and_capture(
        tmp_path,
        capsys,
        flags,
        extra=["--config", "api_token=visible-secret", "--password", "pw-secret"],
    )
    assert "visible-secret" not in out
    assert "pw-secret" not in out
    assert "api_token=<redacted>" in out


# --- contract (i): the wf1 preflight -----------------------------------------


def _staged(project_dir: Path, leaves) -> None:
    """Create empty files at ``leaves`` under ``project_dir``."""
    for leaf in leaves:
        target = project_dir / leaf
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text("", encoding="utf-8")


def test_wf4_without_wf1_is_refused_before_simulation_is_invoked(
    tmp_path, capture_runs
):
    """Missing model artifacts fail immediately before the WF4 consumer."""
    calls, _ = capture_runs
    project_dir = tmp_path / "project"
    cfg = tmp_path / "c.yml"
    flags = {n: "true" for n in rw.WORKFLOW_ORDER}
    flags["build_model"] = "false"
    _write_cfg(cfg, flags, project_dir=str(project_dir))

    with pytest.raises(rw.PrerequisiteError) as excinfo:
        rw.run(str(cfg), cores=3, extra=[])

    assert _snakefiles_invoked(calls) == [
        "analyze_climate.smk",
        "analyze_projections.smk",
        "generate_scenarios.smk",
    ]
    assert _read_only_manifest(project_dir)["status"] == "failed"
    message = str(excinfo.value)
    for leaf in rw.LEAVES:
        assert leaf in message, f"the message hides the missing leaf {leaf}"
    assert "build_model" in message, "the message must name the producer"


def test_the_preflight_names_only_what_is_actually_absent(tmp_path, capture_runs):
    """A partially built project reports its own two gaps, not a generic three.

    Snakemake's own failure names one leaf because rule 3.01 is merely the
    earliest to declare one -- naming the real set is the reason this reads
    `LEAVES` rather than restating paths.
    """
    project_dir = tmp_path / "project"
    cfg = tmp_path / "c.yml"
    flags = {n: "true" for n in rw.WORKFLOW_ORDER}
    flags["build_model"] = "false"
    _write_cfg(cfg, flags, project_dir=str(project_dir))
    _staged(project_dir, rw.LEAVES[:1])

    with pytest.raises(rw.PrerequisiteError) as excinfo:
        rw.run(str(cfg), cores=3, extra=[])

    message = str(excinfo.value)
    assert rw.LEAVES[0] not in message, "a present leaf is reported as missing"
    for leaf in rw.LEAVES[1:]:
        assert leaf in message
    assert "1 of 2" in message


def test_a_complete_wf1_tree_lets_wf3_run_with_build_model_disabled(
    tmp_path, capture_runs
):
    """The check is EXISTENCE, not freshness -- clause (i) against the docstring.

    Staged leaves are empty files: nothing here reads their content, and a
    check that did would be the freshness comparison the wrapper refuses to
    make.
    """
    calls, _ = capture_runs
    project_dir = tmp_path / "project"
    cfg = tmp_path / "c.yml"
    flags = {n: "true" for n in rw.WORKFLOW_ORDER}
    flags["build_model"] = "false"
    _write_cfg(cfg, flags, project_dir=str(project_dir))
    _staged(project_dir, rw.LEAVES)

    assert rw.run(str(cfg), cores=3, extra=[]) == 0
    assert "simulate_system.smk" in _snakefiles_invoked(calls)


@pytest.mark.parametrize(
    ("build_model", "simulate_system"),
    [("true", "true"), ("true", "false"), ("false", "false")],
)
def test_the_preflight_is_silent_on_every_other_flag_pair(
    tmp_path, capture_runs, build_model, simulate_system
):
    """Only wf3-enabled-without-wf1 is checked; the run produces or ignores.

    All three leaves are wf3-only -- wf2 declares none -- so no other pair can
    need them.
    """
    project_dir = tmp_path / "project"
    cfg = tmp_path / "c.yml"
    flags = {n: "true" for n in rw.WORKFLOW_ORDER}
    flags["build_model"] = build_model
    flags["simulate_system"] = simulate_system
    _write_cfg(cfg, flags, project_dir=str(project_dir))

    assert rw.run(str(cfg), cores=3, extra=[]) == 0


def test_the_preflight_exits_two_through_main(tmp_path, capture_runs, capsys):
    """`main` catches PrerequisiteError beside ConfigError -- same exit 2."""
    project_dir = tmp_path / "project"
    cfg = tmp_path / "c.yml"
    flags = {n: "true" for n in rw.WORKFLOW_ORDER}
    flags["build_model"] = "false"
    _write_cfg(cfg, flags, project_dir=str(project_dir))

    assert rw.main(["--config", str(cfg)]) == 2
    assert "error:" in capsys.readouterr().err
