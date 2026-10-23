# Step 7 implementation evidence

Design: [design-v2](design-v2.md) (owner-approved, blob `61afa94a`). Branch `refactor/t2610082103`
in session-1, base main `a860d6da`. Not landed or pushed.

| Commit | Lands |
|---|---|
| `26fd59d7` | `plotting/preset.py`, `shared/plot_preset.py`; the core reads `active()`; 10 scopes, token imports and alias reads migrated; 2 token-only caption scopes; `REFERENCE_FILES` extended; pandas-free `location_labels` |
| `93ed89ef` | `dev/scripts/plotting_standalone_demo.py` and its README row |
| `f4c06321` | Presets section in `dev/reference/toolbox-plot-style.md`; `config/plotting/README.md` |

Scratch root: `session-1 :: .tmp/scratchpad/t2610082103-step7/` (harness, probes, logs, renders).

## Matched render harness

- **Input:** the retained internal-v1 all-five root,
  `session-1 :: .tmp/pytest/run-4bf42bbc57744ddb8ec629e34230630c/test_all_five_workflows_run_en0`.
  It was copied to `verification/base` and touched current with `snakemake --touch`. One rapid WF1
  simulation then ran, because the output contract changed in `26287429` and `run_default/output.csv`
  was missing.
- **Procedure:** `verification/run.sh <state>` clones base three times. Each clone gets plotting
  annotation `none`, `caption` or `title`. All `plots/` directories, the historical map reference and
  `performance_indicators.csv` are deleted, then WF0, WF1 and WF2 are re-run through
  `scripts/run_workflow.py`. The comparison is `verification/compare.py`, using decoded PNG pixels,
  structural JSON and exact text.
- **States:**
  - `before`: rendered at `a860d6da` (clean) before any code edit.
  - `control`: the same unchanged code, rendered again.
  - `after`: rendered from the commit-1 tree, with a temporary `active()` that raises outside any
    scope.
- **Coverage, per variant:** 146 files, made up of 112 PNGs, 15 JSON, 16 text files and 3 other files.
  - WF0 ERA5 (21), CHIRPS (17) and comparison (17).
  - WF1 forcing (9), evaluation (20) and spatial maps including `elevation_basin.png` (11).
  - WF2 (17).
  - WF3 weathergenr figures are R-owned and out of scope.

| Check | Result |
|---|---|
| `control` vs `before` (none) | 146 files compared, 0 differences: harness is deterministic |
| `after` vs `before`, none/caption/title | 336 PNGs pixel-identical; 0 failures; 4 identity-only files per variant |
| Identity-only content | `map_reference.json`: code-file list (+2 files) and `reference_id`; WF0 ERA5/CHIRPS and WF1 forcing captions: `map_reference.reference_id` only. Frame, scale, palette and class fields are unchanged. |
| Raising probe during `after` | No hits in any of 9 workflow runs |
| Raising probe over affected tests (27 files) | 1601 passed, 11 skipped. 1 intentional neutral call: `test_wf0_diagnostic_contracts.py::test_short_record_acf_confidence_limits_fit_inside_axes` calls the WF0 `acf` chart directly and asserts data-driven limits only |

## Equality and boundary probes

- **`STYLE`:** the new value equals the old one key for key, in the same order, with equal values.
- **Tokens:** all 35 old tokens in `fundamentals` equal their new homes in `shared/plot_preset` and
  `CST_PRESET` (`MM` and `MONTH_ABBR` stay in the core).
- **Missing-value test:** `location_labels._missing` agrees with `pandas.isna` on 24 scalar kinds,
  covering None, float/numpy/complex/`Decimal` NaN, `pd.NA`, NaT, strings and numbers.
- **Code identities:** generation, simulation and indicator inventories are unchanged (18, 22 and 47
  files) with no plotting or style path.
- **Standalone demo:** an isolated copy imports and renders under `python -I` in Pixi and in a scratch
  venv with only numpy 2.5.4 and matplotlib 3.11.2 (pandas absent). Six figures were inspected. Bytes
  differ between the two environments, and no cross-environment equality is claimed.

## Software checks

- **Affected tests, without the probe:** 1663 passed, 11 skipped, 5 failed.
  - The 5 failures are in `tests/test_simulation_reuse.py` (boundary-bridge audit).
  - The same 5 fail on an exported, unmodified `a860d6da`, and the inventories they hash contain none
    of the changed files. They are a pre-existing baseline failure, unrelated to this change.
- **`pixi run lint`:** pass.
- **`pixi run format-check`:** 553 files formatted.
- **`git diff --check`:** pass.
- **Reference rebuild, partly shown:** every `after` run rebuilt the deleted historical reference with
  the new code, and WF1 forcing then passed its `validate_current()` check before export.
- **Owed at the batch gate:** a fresh rapid WF0→WF1 run from a new project directory (design §4), plus
  the validation-reference landing gate.
