# P3 plain-language return

COMPLETE for coordinator review. Changes remain uncommitted on
`feat/t2610211349-publishing-pilot`, base `bbf5fec60c88dcea7669f9b7d10134e196c51ecf`.

## Artifacts

Relative to session-2:

- HTML: `.tmp/tasks/t2610211349/p3/plain-language/build/index.html`.
- PDF: `.tmp/tasks/t2610211349/p3/plain-language/build/index.pdf` (4 pages).
- PDF images: `plain-language/visual/page-1.png` through `page-4.png`, under P3.
- Browser image: `plain-language/visual/html-configuration.png`, under P3.
- Logs: `plain-language/build.log`, `tests.log`, `audit.log`, `rendered.log`, under P3.
- Complete 22-file inventory: `plain-language/changed-files.txt`, under P3.
- Render input hashes: `plain-language/build/source-hashes.json`, under P3.

```text
SHA256 index.html 6AD9BF937288F04BB9EF8FD95659770094405616F7A27C8655D1BE52A8D8287D
SHA256 index.pdf  7C7102D64BAAFFE63660C01FF44EC3AA527183B3ED2E02C4505F9D0845699B34
```

## Changes

The pilot now says “select simulations, indicators, or both,” with separate short instructions for choosing
sets and reading tables. Scientific conventions, units, sample screening, group aggregation and missingness
qualifications remain. The private scalar-operation paragraph is deleted, not replaced with a historical note.
Useful notebook guidance now uses `operations: [indicators]` and the current runner, including the completed
simulation prerequisite. No notebook code cell, output, execution count or metadata changed.

Removed development migration/release narratives from maintained guide/reference/local documentation:
metrics terminology and old layout transitions, old-output migration instructions, audited source-transition
commit IDs, renamed-figure notices, obsolete config conversion advice, old imports/selector aliases and
superseded environment repair history. Supported current choices and integrity/refusal requirements are
stated directly. Historical dev records, root historical evidence, archived unmaintained material and upstream
vendored reference docs are untouched. The current `legacy-unattributed` output-status token remains because
it is a machine-readable attribution status, not advice to use an obsolete interface.

Affected source groups (exact inventory in `changed-files.txt`):

- `docs/guide/{running,outputs,configuration}.md`, `docs/README.md` and `docs/notebooks/Climate Stress Test.ipynb`.
- `docs/site/toolbox-reference/{workflow-simulate-system,retained-handoffs,workflow-analyze-climate,
  workflow-analyze-projections,workflow-generate-scenarios}.qmd`.
- `docs/site/setup/{env-setup-notes,install}.md`.
- `blueearth_cst/indicators/README.md` and `sets/{default,crop_water}/README.md`.
- `config/defaults/README.md`, `config/templates/README.md`, `config/templates/example-basin/README.md`
  and comments in its `project_config.yml` and `project_config_simulate_system.yml`.
- `docs/publishing-pilot/manifest.json` and `tests/test_docs_pilot.py`.

Coordinator corrections incorporated:

- Removed the fixed-calculation-owner historical sentence entirely; no broader fixed-owner claim remains.
- Checked `blueearth_cst/model/copy_config_files.py` and retained the current-role explanation of generated
  `config/templates/` snapshots, including the distinction between archived files and files recoverable
  from the toolbox. No move history remains there.
- Checked `blueearth_cst/experiment/baseline_qcrit.py`: explicit `model_root` resolves beside the set file;
  `source_id` labels provenance and is combined with historical CSV/TOML hashes. It does not select another
  dataset. The prose now states that distinction and the actual omitted defaults.
- Restored only this task's known edits to `config/defaults/weathergen_config.yml`. It has no Git diff and
  its bytes equal checkout-filtered HEAD. This run-read default is excluded from documentation cleanup
  because raw bytes can affect generation identity. No rerender followed: pilot inputs were unchanged.
  The remaining two YAML edits are scaffolding comments; parsed settings equal HEAD.

The removed Excel stop heading is replaced by the next stable heading, `## Return levels and their limits`.
Tests verify the complete selected excerpt is present and that this next section is excluded. All six pilot
anchors remain. Publishing fixture source/rendered routes and the publisher implementation are unchanged.
The subtitle identifies this working-tree candidate; external references retain the prior pinned revision
and do not claim to contain these edits. Online availability was not checked.

## Build and verification

Actual recipe from session-2, with normal user permissions for the established Quarto/Sass requirement:

```powershell
$runtime = 'C:/Users/taner/workspace/blueearth_cst'
& "$runtime/.pixi/envs/default/python.exe" -B dev/scripts/session_runtime.py --runtime-root $runtime -- python dev/scripts/build_docs_pilot.py --output .tmp/tasks/t2610211349/p3/plain-language/build
```

Build exits 0. The helper confirms compatible runtime contracts, this lane's cwd/source import, and main's
installed Python prefix. No dependencies, lockfiles, runtime code or publisher behavior changed.

Affected tests, through the same helper:

```text
python -m pytest tests/test_site_guides.py tests/test_docs_pilot.py tests/test_notebook_outputs.py -q -k "not staged and not strip and not there_are and not markdown_cells" -o cache_dir=.tmp/tasks/t2610211349/p3/plain-language/pytest-cache --basetemp=.tmp/tasks/t2610211349/p3/plain-language/pytest-run
```

**17 passed, 8 deselected in 0.46s**: pilot/site staging plus tracked-notebook output checks. Deselected checks
exercise unrelated Git-index/strip machinery. Scoped Ruff check/format check and compile pass for the changed
Python test file. `git diff --check` passes.

Bounded fresh evidence:

- Scan of 51 maintained document/config-comment files finds no obsolete scalar operation or targeted
  migration blocks. Runtime code, dev/upstream evidence and publishing fixtures are untouched.
- Notebook JSON parses, and all nonprose content equals HEAD. No notebook execution occurred.
- Both changed scaffold YAMLs have identical parsed settings to HEAD; the run-read weather config is restored.
- All 10 render input byte hashes match after rendering; no canonical source was changed by the build.
- All 40 selected prose/list/code blocks are present in actual HTML and extracted PDF. Two ordered lists,
  six anchors, affected HTML/PDF links and the advanced-reference destination pass. Internal details and
  the omitted advanced heading remain excluded from the pilot.
- Chrome visually inspected the simplified configuration and table-reading sections and followed their
  internal navigation. Other Formats still shows PDF. The loopback preview served the page; browser review
  is separate rendering/navigation evidence, not an inference from serving alone.
- Installed PyMuPDF rasterized the actual PDF; all four page PNGs were inspected. No clipping or missing
  text. List continuations are legible. The retained separate-annex break leaves whitespace on page 3 and
  starts the unchanged annex on page 4.

Unchanged diagram interaction/static derivation, actual two-format refresh, missing-input behavior and
old-path fixture mechanics reuse prior P3 evidence; no separate repeat campaign was run. No model/data
acquisition, notebook execution, broad suite, deployment or push occurred. Preview stopped and tab closed.

## Execution record

- Start recorded UTC: `2026-10-26 17:40:21.9799160Z`.
- Completion/restoration checkpoint UTC: `2026-10-26 17:51:05.9668259Z`; return writing follows.
- Continuing canonical python-engineer, manually applied, implement mode; no nested delegation.
  Requested GPT-6.1-Sol medium; prior owner/UI verification retained. Effective backend settings remain
  independently unobservable. No setting change. Tokens, cost and active-compute/tool-wait totals unknown.
- Reused complete role/skill reads: python-discipline (style/hazards/validation), testing-policy and execution
  checks, scientific-workflows/workflow contract, project-system lifecycle/phased execution, git-workflow
  identity/isolation, writing-feedback-revision/revision fidelity, Quarto, PDF and browser guidance.
  No newly applicable skill body or triggered reference was left incomplete; no new skill body was needed.
- Rework: coordinator review removed an overbroad fixed-owner sentence, refined source-label wording,
  restored the snapshot-role explanation and excluded the byte-sensitive runtime default. One trailing
  blank-line check was fixed. Several broad grep invocations were replaced with an explicit tracked-file
  scan to keep historical and upstream matches out of the cleanup. No failed build/test or user wait.

No blocker. Coordinator owns review/commits/landing. Stop before migration.
