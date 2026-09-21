# P5 WF3 static generation evidence

Status: implementation evidence for review. All paths below are relative to the session-2 worktree. Scratch fixtures are disposable and are not committed.

## Frozen implementation and focused checks

The final WF3 provider revision is `cc821a2dc421af9b4e9f3d12e6632454edae0743657893e73f78c48f0c32aa05` (recorded in J's `collection_intent.json`). The selected collection has 14 runs with explicit seed 123. Its retained path is `.tmp/scratchpad/2026-09-21_1541/p5-final-zero-change-j/project/scenarios/ecdcafc35b59/`.

- `pixi run -x -- python -m pytest tests/test_generation_plan_v2.py tests/test_generation_publication.py tests/test_generate_scenarios_launcher.py tests/test_scenario_collection_v2.py`: 32 passed (`.tmp/scratchpad/2026-09-21_1541/p5-postformat-focused.log`). These cover pinned candidate/plan identity, source and catalog exclusions, seed resolution, WF4 code exclusion, disabled WF3, strict installed YAML/provider arguments, receipt and publication failure boundaries.
- `pixi run -x -- python -m pytest tests/test_cli.py`: passed (`p5-postformat-cli.log`).
- Parent integration check: `pixi run -x -- python -m pytest tests/test_snake_utils.py tests/test_wf3_helper_boundary.py tests/test_windows_job.py tests/test_run_workflows.py tests/test_generation_snapshot.py tests/test_workflow_archive_launch.py`: 406 passed (`p5-parent-integration-default-temp.log`).
- `pixi run lint` and `pixi run format-check`: passed (`p5-postformat-lint.log`, `p5-postformat-format.log`).
- Real R provider execution wrote direct `run_01.nc` and `run_08.nc` roots; the WF3 transform produced the other named temporary members and retained the 14 v2 series. The generation log is `p5-final-j-create.log`.

## Final fixture J

The predecessor is `.tmp/scratchpad/2026-09-21_1541/prechange-zero-change-reference/project/scenarios/collections/4ca4e0d41582/`. The fresh successor J was prepared from equivalent source inputs/config and generated through the owned WF3 launcher. `.tmp/scratchpad/2026-09-21_1541/p5-final-j-scientific-comparison.log` records decoded equality for all 14 matched run series (dimensions, variables, attributes, time/calendar, and values) and byte equality of both date CSVs. The predecessor and successor netCDF serializations may differ; the scientific comparison is decoded.

Plain reuse (`p5-final-j-reuse.log`) left all 41 original ready files byte-identical: `p5-final-j-before.json` equals `p5-final-j-after_reuse.json`. A forced ready-target rerun with `--forcerun all --rerun-incomplete` executed only each phase's `all` rule and no creator (`p5-final-j-force-ready-repeat.log`). After the `--forceall` source regeneration described below, this selected the new ready collection `95333a7f09eb`; all 41 of its ready files were byte-identical before and after: `p5-final-j-forceall-before_force_ready.json` equals `p5-final-j-forceall-after_force_ready.json`.

An earlier `--forceall` on J intentionally reran source producers, changed the source inventory projection, and created a separate valid collection `95333a7f09eb` (`p5-final-j-force-reuse.log`). It did not alter any of the 41 original J ready bytes (`p5-final-j-before.json` equals `p5-final-j-after_force.json`). This is a new identity due to regenerated source bytes, not reuse of the first identity.

The real fixture uses a fresh scratch project; it does not update the standing project tree or baseline manifest. The independent scientific continuity and exclusion reports are `p5-scientific-validation.md` and `p5-exclusion-matrix.md`.
