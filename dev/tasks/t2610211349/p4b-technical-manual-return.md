# P4B return — technical manual

Task: t2610211349. Lane: session-2. Branch: `docs/t2610211349-technical-manual`.
Base and unchanged HEAD: `a4d79ea605dba05a5962d254271d775ebbba97a0`, including V9 `8963f661`.
Status: source work ready for coordinator review; uncommitted. P5 integration dependency remains below.
No commits, staging, merges, landing, pushes, shared-record writes or nested agents.

## Delivered sources

Created all 16 assigned Markdown chapters in `docs/technical-manual/`:

`overview.md`, `environment.md`, `workflows.md`, `configuration.md`, `input-formats.md`, `datasets.md`,
`workflow-analyze-climate.md`, `workflow-build-model.md`, `workflow-analyze-projections.md`,
`workflow-generate-scenarios.md`, `workflow-simulate-system.md`, `retained-handoffs.md`,
`execution-and-provenance.md`, `results-transfer.md`, `indicator-requests.md`, `indicator-extension.md`.

Also added `local-source-appendix.yml`: complete-source assembly declaration for the module and all five
set READMEs, with source-relative link bases and intentionally external repository evidence.
It is a declaration for P5, not a claim that the publisher already consumes it.

Changed all 11 inventoried toolbox-reference QMD sources into small route wrappers. Existing source paths
and all 37 old H2 anchors remain. Modeling tools routes directly to `overview.md#components`.
Changed the module README and five set READMEs additively; original formulas, examples, fixed scientific
conventions and qualifications remain. Root `STATUS.md` was refreshed from stale P3 state.
No guide, navigation, config YAML, notebook, scientific-approach source, runtime or publisher source changed.

Total authored delivery: 34 files (17 modified inventory sources, 16 new chapters, one new declaration).
`p4b-changed-paths.txt` records Git status; its untracked manual-directory entry expands to the 17 files above.

## Every owned inventory disposition

Paths under `toolbox-reference/` below mean `docs/site/toolbox-reference/`.
TM means `docs/technical-manual/`. Existing `.qmd` paths remain tracked wrappers, not deleted files.

| Inventory ID/source | Disposition and maintained destination |
|---|---|
| 16 `assessment-workflow.qmd` | Incorporated into TM `workflows.md`; both prior section anchors retained |
| 17 `datasets.qmd` | Transferred to TM `datasets.md`; source-role science retained; current starter clarified |
| 18 `modeling-tools.qmd` | Incorporated into TM `overview.md#components` |
| 19 `overview.qmd` | Replaced planned-architecture placeholder with TM `overview.md#sections` and components |
| 20 `retained-handoffs.qmd` | Reconciled into TM `retained-handoffs.md`, including `#startup-input-checks` |
| 21 `workflow-analyze-climate.qmd` | TM same basename; scientific interpretation/case findings kept there |
| 22 `workflow-analyze-projections.qmd` | TM same basename; attribution and transfer link to shared owners |
| 23 `workflow-build-model.qmd` | TM same basename; current paths, shared map branches and discharge boundary |
| 24 `workflow-generate-scenarios.qmd` | TM same basename; wrapper/DAG distinction, corrected data-root path |
| 25 `workflow-simulate-system.qmd` | TM same basename; generic selection to `indicator-requests.md` |
| 26 `workflows.qmd` | Incorporated into TM `workflows.md`; one principal workflow overview table |
| 33 `indicators/README.md` | Retained canonical; additive neutral-input detail and manual/request links |
| 34 `sets/crop_water/README.md` | Retained canonical complete preparation contract; declared for inclusion |
| 35 `sets/default/README.md` | Retained canonical; request/inclusion pointers added |
| 36 `sets/eflow_erfa/README.md` | Retained canonical; selector/link and external-oracle disclosure added |
| 37 `sets/flood_risk/README.md` | Retained canonical; confined selection link; qualification warning retained |
| 38 `sets/flow_regime/README.md` | Retained canonical; selector/link and inclusion pointer added |

Exact old-path/destination/37-anchor inventory: `p4b-route-map.json`.
All old workflow `rules`, `rule-flow`, `configuration`, `inputs`, `outputs` anchors remain where present.
WF0 `interpretation` and `remaining-scientific-limitations`, WF4 `local-calculation-sets` and
`integrity-and-numerical-rechecking`, datasets' four headings, overview `sections` and handoff
`startup-input-checks` also remain. New destinations resolve those anchors in source.
Existing Mermaid flow blocks were removed during transfer: rule tables and adjacent prose retain the
static dependency/branch account. No new diagram or scientific figure was designed or rendered.

## Shared-source extraction and P4A anchors

P4A alone edits/shortens the original guides and local config prose. Source extraction here used the
unchanged lane base; no counterpart file was changed to make a local check pass.

| Base source/detail | Central destination/anchor for P4A links |
|---|---|
| `guide/configuration.md`, starter/config indexes: composition and paths | `configuration.md#composition-and-precedence`, `#how-paths-are-read` |
| Shared field/default ownership and plotting distinctions | `configuration.md#shared-fields`, `#workflow-settings`, `#plotting-resources` |
| `config/templates/README.md`: exact locations/observations formats | `input-formats.md#output-locations`, `#observed-time-series` |
| Local native variable/token/unit and response boundary | `input-formats.md#retained-daily-responses` |
| `guide/outputs.md`: retained layout, lookup fields and joins | `retained-handoffs.md#identities-and-reuse`, `#scenario-exports-and-lookups`, `#joins-and-reference-membership` |
| Named tables/dictionary/status and publication | `retained-handoffs.md#indicator-tables-and-dictionary`, `#named-publication-and-inspection` |
| `guide/running.md`, `benchmarking.md`: exact attempt/diagnostic semantics | `execution-and-provenance.md#invocation-hierarchy-and-configuration-captures`, `#timing-and-attempt-lifecycle` |
| Runner arguments, reset/unlock and identity constraints | `execution-and-provenance.md#launcher-arguments-and-safety-boundaries` |
| Benchmark/resource interpretation | `execution-and-provenance.md#workflow-benchmark-reports`, `#wf4-resource-diagnostics` |
| `guide/outputs.md`: WF2 producer attribution and transfer | `execution-and-provenance.md#wf2-product-attribution`, `results-transfer.md` |
| Setup runtime ownership | `environment.md#language-boundaries`, `#availability-and-provenance` |
| WF4 generic selection, inline/file definitions and missingness | `indicator-requests.md#operations-and-sets`, `#inline-parameters-and-selection`, `#standalone-definitions`, `#inputs-evaluation-and-recovery` |
| Integrity versus numerical recheck | `indicator-requests.md#integrity-and-numerical-rechecking` |
| Extension and every local set | `indicator-extension.md#canonical-sources` plus appendix declaration |

Removed duplication within P4B: assessment/workflow overview and modeling-tools independent accounts;
WF4 copies of ERFA/default/flow/crop/flood detailed conventions; shared named-publication/lookup detail
from WF3/WF4; WF2 transfer and producer semantics from its workflow page.
The local set READMEs remain the complete calculation/preparation owners. Short reminders remain beside
the relevant interfaces. Detailed duplication in P4A-owned base guides remains until its packet integrates.

Two source links intentionally await P4A integration:

- `environment.md` → `../guide/install.md`.
- `environment.md` → `../../dev/scripts/environment-notes.md` (repository-only maintenance).

## Substantive claims and executable evidence

Executable paths in this table are relative to `blueearth_cst/` unless `scripts/` or `tests/` is shown.
Source inspection is fresh. Preserved scientific prose is not a new literature or empirical validation.

| Claim | Source/test owners inspected |
|---|---|
| Schema 2/3, closed sections, composition/read scopes | `shared/config_composition.py`, `config_paths.py`; `tests/test_config_composition.py`, `test_config_paths.py` |
| Inclusive calendar years and historical/model windows | `shared/wf3_science.py:historical_window_bounds`, `snake_utils.py:resolve_simulation_window`, `climate_window.py` |
| Data sources/defaults/runtime ownership | Starter/project/workflow YAML, `config/defaults/` recipes, `advanced_settings.py`, Pixi/Julia contract locations |
| Location identity, observed header matching and discharge-only evaluation | `spatial/delineate_spatial_units.py`, `model/build_wflow_model.py`, `observation_validation.py`, `plot_results.py`, `shared/native_locations.py`; `test_observation_validation.py`, `test_native_locations.py` |
| Native variables/units and neutral daily metadata | `shared/indicator_tables.py`, `experiment/wflow_response_reader.py`, `indicators/contract.py`, `series.py`; `test_response_series.py`, `test_indicators_module.py` |
| Immutable collection root, snapshots, lookup fields and percentage units | `experiment/generation_plan.py`, `generation_publication.py`, `scenario_collection_v2.py`, `scenario_export.py`; `weathergen/read_member_grid.R`, `impose_climate_change.R` |
| Explicit manifest-only selector and project confinement | `experiment/collection_resolution.py`, `reservation_request.py` |
| Ready response/table publication, keys and named export identity | `experiment/response_inventory.py`, `indicator_plan.py`, `indicator_artifacts.py`, `named_export.py`, `indicator_export.py` |
| Request defaults, IDs, inline overrides, include/exclude and refusals | `experiment/indicator_sets.py`, `simulation_runner.py`; `tests/test_indicator_sets.py` |
| Whole-calculation versus location-level unavailability | `indicator_plan.py:split_availability` and reduction/publication code; `tests/test_partial_indicators.py` |
| Independent module extension, identities and set limits | Module and five READMEs; `indicators/contract.py`, `series.py`, default/crop registries and loader boundaries; existing module/request tests |
| Attempts, monotonic timing, benchmark/resource limits | `shared/invocation_history.py`, `invocation_summary.py`, `execution_outputs.py`, `merge_benchmarks.py`, `resource_tracking.py`, `resource_timing.jl` |
| WF2 production and ZIP transfer/refusals | `shared/product_record.py`, `result_bundle.py`; `scripts/transfer_results.py`; `tests/test_result_bundle.py` |
| Workflow rule and wrapper maps | Five entry Snakefiles, included simulation rules and generation-plan/publication owners |

## Reconciled discrepancies and limits

1. Old reference prose put collections at `scenarios/<id>/`. Current immutable data are
   `scenarios/_engine/data/<id>/`, with markers under `_engine/collections/`; `scenarios/` is the export.
2. Template/local prose calls `climate.window` water years. The executable parser returns January 1 through
   December 31 of inclusive calendar years. The manual states executable behavior; config YAML is untouched.
3. Precipitation settings are multipliers, but lookup columns store percentages: `(factor - 1) * 100`.
   Temperature is additive degC. Monthly lookup facts do not settle annual response-surface axes.
4. Saved value CSVs already use split run/group headers; `run_group_id` is validator-internal normalization.
   An early draft conflated these; corrected against `indicator_plan.py` before handback.
5. The old WF4 prose generalized unavailable rows. Completely absent responses produce unavailable
   calculation declarations with no invented value rows. Location-level absent parameters produce statused
   rows. A request with no calculable declarations can publish an empty table inventory. P4A should retain
   this distinction when simplifying the guide.
6. A declared unreadable workflow file can be skipped outside a compositor entry's read scope, with a
   diagnostic. The blanket base-guide statement that every supplied file always fails was too broad.
   Launcher capture/admission and enabled-workflow input requirements still apply.
7. Current starter sources are P-drive/GlobCover. Dataset source roles are illustrative, not availability
   claims or a second generated CMIP6 model/member inventory. WF1 evaluates observed discharge only;
   configured observations for other outvars are warned as unused.

No executable contract was changed. No unresolved scientific choice was silently decided.
WF0's entire `## Interpretation` through final limitations text is byte-equivalent after newline
normalization to the base source, including all Ntoum findings and qualifications. Its temporary reachable
home is `docs/technical-manual/workflow-analyze-climate.md`; the old route links it. P4C remains deferred.
All scientific-approach files are unchanged. Set README edits add orientation/input detail only.
No self-contained data, runtime, basin performance or supported surface-construction promise was added.

## Checks and observed results

Compatible main runtime was invoked through `dev/scripts/session_runtime.py`; no install/update occurred.
Probe confirmed cwd/source imports in session-2 and executable in main `.pixi/envs/default/python.exe`.
The checkout/lock compatibility guard passed. Commands used the following prefix:

```powershell
& C:/Users/taner/workspace/blueearth_cst/.pixi/envs/default/python.exe `
  dev/scripts/session_runtime.py --runtime-root C:/Users/taner/workspace/blueearth_cst --
```

- `python -m pytest tests/test_indicator_sets.py tests/test_response_series.py -q`:
  **101 passed**, one cleanup warning, 24.10 s. Log: `p4b-contract-tests.log`.
- `python -m pytest tests/test_site_guides.py tests/test_docs_pilot.py -q`:
  **13 passed, one failed**, one cleanup warning, 18.06 s. Log: `p4b-doc-tests.log`.
  The failure is `test_staging_preserves_sources_and_refreshes`: frozen pilot manifest searches the old
  WF4 source for `Edit project_config_simulate_system.yml,` (with backticks); that text now belongs to
  central request documentation and the old file is a wrapper. This is change-induced, expected from the
  commissioned source transfer, and unresolved within P4B's no-publisher/no-shared-test ownership.
  It is **not** classified as an unrelated baseline failure or a whole-suite pass.
- Both pytest invocations warned that retention cleanup could not remove an older pre-existing pytest
  scratch path. Tests themselves completed; no deletion/permission repair was attempted.
- `pwsh -NoProfile -File .tmp/tasks/t2610211349/check-p4b.ps1`: 33 Markdown/QMD sources, 127 local
  link occurrences, 11 route files, 37 old section anchors; no unresolved anchors. Only the two named P4A
  destination files are absent. Scientific-fidelity assertion passes. Evidence: `p4b-source-checks.json`.
  Scanner initially gave two false anchor failures from CRLF heading whitespace; its local parser was
  corrected and rerun. No source change was made to satisfy those false positives.
- Main-runtime YAML syntax/source-declaration check: seven YAML examples parse; six appendix sources are
  unique and exist. Evidence: `p4b-yaml-check.log`. This checks syntax and inventory, not data availability.
- Incoming-link scan across docs/config/package/excluded reference consumers retained in
  `p4b-incoming-links.txt`; original source paths still exist. No excluded consumer was edited.
- `git diff --check`: pass (Git reports normal LF/CRLF conversion notices).
  A repeat with process-local `git -c core.safecrlf=false diff --check` also exits zero.
  New-file source inspection completed separately; no executable or protected-source changes appear.

No HTML/PDF build, browser/render inspection, notebook/model execution, data acquisition, external-link
availability check, new numerical qualification, broad software suite or new permanent tests.
P5 owns publication assembly and visual/offline/URL proof; source anchor checks do not establish those.
Existing diagrams were replaced by their text/table accounts, so no figure render is claimed.

## P5/coordinator acceptance dependencies

- Repoint the frozen pilot extraction in `docs/publishing-pilot/manifest.json` to the central owner and
  update its boundaries/tests deliberately. Do not restore a second detailed WF4 account in the wrapper.
  Suggested source: `docs/technical-manual/indicator-requests.md`, sections `operations-and-sets` and
  `inline-parameters-and-selection`. Preserve the V9 plain-language reading/selection goals.
- Stage the 16 central chapters, map source-relative links to the published routes, and prove wrappers'
  old HTML URLs/anchors in both formats. `_quarto.yml` is unchanged and still routes to wrappers.
- Implement/translate `local-source-appendix.yml` into the publisher's owning manifest rather than
  editing included README copies. Include all six complete sources, rebase their links, namespace/preserve
  source heading links, and label repository evidence external. No renderer support is asserted here.
- Integrate P4A's two pending files and replace detailed guide/local duplicates using the anchor table.
- Owner/P4C retains the scientific and axis-authority decisions; existing case findings remain reachable.

## Role, skills, reads and measurements

Requested role: API-documenter, degraded generic. Full canonical role read/applied manually:
`C:/Users/taner/workspace/brain-infrastructure/artifacts/agents/api-documenter.md`.
No native persona activation or nested delegation is claimed.
Requested and user/UI-verified model/effort: **GPT-6.1-Sol / medium**.
Exact backend identity, reasoning setting, conversation ID and token/cost counters are not tool-observable.

Applicable skill bodies read completely:

- `C:/Users/taner/.agents/skills/project-system/SKILL.md`: status/handoff;
  `references/workflow.md` and `phased-execution.md` read completely.
- `C:/Users/taner/.agents/skills/testing-policy/SKILL.md`: proportionate source/consumer verification;
  `references/execution-checks.md` read for borrowed-runtime attribution.
- Infrastructure `artifacts/skills/quarto/SKILL.md`: role-bound QMD/reference policy and source wrappers.
  `_external/quarto` was absent. No new chunk, citation, render or advanced-format feature was authored.
- Infrastructure `artifacts/skills/scientific-software-documentation/SKILL.md`: canonical local README
  scope and preserved scientific limits; `readme-authoring.md` and
  `documentation-review-and-accessibility.md` read completely before governed editing/review.
- Infrastructure `artifacts/skills/_external/markdown-mermaid-writing/SKILL.md`: Markdown mechanics;
  `references/markdown_style_guide.md` completed through bounded reads. Project conventions supersede its
  optional template/emoji style. No Mermaid diagram was authored; Mermaid creation/render branches were
  not applied. The generic project-documentation template was inspected and does not fit this fixed packet.

Infrastructure `_external` precedence checked for role-bound/applicable infrastructure skills;
no external project-system/testing-policy override was found. `project-reference-docs/SKILL.md` was also
read for routing but excludes API reference; its maintainer-reference workflow was not applied.
Python/R docstring/roxygen skills were not triggered: no calculation, source-code or docstring edit occurred.
No governing skill body or triggered reference remains known incomplete. Initial combined reads were
truncated; individual/consecutive bounded reads supplied the missing applicable material before use.
Task records were read from main explicitly when this lane's non-shared task path was absent.

Assignment/boundary map including reconciliation, execution plan, inventory and V9 return were read fully.
Repository documentation, validation, lane-status, layout/scratch and naming guidance was consulted.
Excluded governing/implementation sources were evidence only. No excluded guidance was rewritten.

First recorded UTC: **2026-10-26 20:47:16 UTC**, after initial role/assignment/orientation reads.
Final handoff checkpoint is recorded below. True start time, active compute, usage/cost, coordinator
acceptance time and accepted lead time remain unknown. Two existing pytest runs were made, without repeats.
Routine rework included three malformed patch contexts (corrected before edits), initial task-path/read
truncation recovery, the local scanner correction and source-led corrections listed above.
No user-decision wait, explicit sleep, model escalation, external service or benchmark run occurred.
The canonical guidance already requires the source tracing that found these discrepancies; no reusable
skill/role amendment is proposed from this packet.

Next action: cst-main reviews this packet and the uncommitted P4B sources; accept or assign a bounded repair.
Worker stops here. No commit/landing authority is inferred from completion.

Final checked handoff UTC: **2026-10-26 21:11:14 UTC**. Interval from first recorded checkpoint:
**23m 58s**, not true-start execution time. Branch/HEAD remain unchanged. Final source scan still records
127 local links, 37 preserved anchors and only the two declared P4A destinations missing.
All 17 new manual/declaration files have zero trailing-whitespace findings; final diff whitespace check passes.

## Accepted bounded repair handback — 2026-10-26

This addendum supersedes the earlier unresolved pilot failure and pending counterpart-link findings.
Coordinator authorized only the manifest extraction repair, a necessary test-fixture adjustment, the
partial-mode summary correction, and combined source verification. No full P5 work was performed.

### Changes and coordination

- `docs/publishing-pilot/manifest.json`: Configuration now extracts from `docs/guide/indicators.md`.
  Existing start/stop markers, `include_stop`, heading and anchor remain unchanged.
- `tests/test_docs_pilot.py`: one fixture input added, `docs/technical-manual/indicator-requests.md`.
  The updated default README links to this target; the minimal test repository must contain it for the
  existing link-resolution check. No assertion or publisher behavior was weakened.
- `docs/technical-manual/indicator-requests.md`: the summary table now separates strict refusal,
  partial-mode omission of an entire calculation for an absent response, and unavailable rows for
  missing location parameters. It agrees with the following detailed explanation.

Coordinated directly with existing s1 technical-writer-p1. Its confirmed source is
`docs/guide/indicators.md#configuration`. Exact extraction boundaries:

```text
start: Edit `project_config_simulate_system.yml`,
stop: calendars, missingness or grain.
include_stop: true
heading: ## Configuration
anchor: configuration
```

The three numbered V9 instructions are verbatim. No dense technical-manual prose replaces them, and no
content was restored to a wrapper. Other pilot boundaries were unchanged. No s1 file was written here.

### Final verification and candidate attribution

Evidence lives under `.tmp/tasks/t2610211349/p4b-repair/` in session-2.
All runtime commands used the previously verified compatible main runtime through `session_runtime.py`.

- `python check_combined.py` (full relative path in this directory): isolated verbatim snapshot plus
  read-only fallback resolution. Inventory derives from all 55 registered sources, P4A's accepted
  `git diff --name-only a4d79ea6 fb06979e`, and P4B's complete working-tree additions/modifications.
  Result: **77 documentation sources, 405 relative links/fragments, zero missing files or anchors**.
  All **12** distinct P4A-to-TM destinations and both previously absent P4A destinations resolve.
  Markdown inline/reference links, literal HTML href/src, heading/explicit IDs, and notebook Markdown
  cells were checked. Sixteen external-scheme links were recorded but not availability-checked.
  Evidence: `combined-links.json`, `combined-links.log`; consumed source hashes are retained there.
- `python -m pytest .tmp/tasks/t2610211349/p4b-repair/overlay/tests/test_docs_pilot.py
  tests/test_site_guides.py -q`: **14 passed, one warning, 0.43 s**.
  The copied test is byte-identical to this lane's changed test; its repository root is the isolated
  combined overlay. Publisher imports remain session-2's unchanged code. Evidence: `doc-tests.log`.
- Existing tests continue to verify boundaries, missing-input refusals, refresh/source preservation,
  advanced-detail exclusion, plain-reader instructions, source compatibility and static fallback.
  The warning is the same pre-existing pytest retention-cleanup permission warning; no cleanup attempted.
- Extracted Configuration was compared to the accepted V9 body in base `a4d79ea6`: **identical**.
  SHA-256 of normalized selected body:
  `53244ad90ab6852101867262caf182dde7e6149627fcb3f1ffa0db8aab3575dc`.
  All **82** overlay source/input hashes remained unchanged after tests. Evidence: `fidelity.log`.
- `ruff check tests/test_docs_pilot.py`: pass.
- `ruff format --check tests/test_docs_pilot.py`: pass, one file already formatted.
- `python -m py_compile tests/test_docs_pilot.py
  .tmp/tasks/t2610211349/p4b-repair/check_combined.py`: pass.
- `git -c core.safecrlf=false diff --check`: pass. S2 branch and HEAD remain unchanged at `a4d79ea6`.

S1 later advanced to landed `fdf36b7b`; its difference from `fb06979e` contains only coordinator task/board
records. Its source content remains identical to the combined snapshot. No rerun is required or claimed.
The coordinator explicitly accepted this evidence as sufficient and requested no further checks.

Python discipline was loaded completely before editing the test, from the project's activated skill;
`style-and-docs.md`, `python-validation.md` and `hazards.md` were also read completely.
Infrastructure `_external/python-discipline` was checked and absent. Existing role/documentation,
testing-policy and runtime guidance was reused. No incomplete governing read is known.

First repair measurement: **2026-10-26 21:16:28 UTC**; final checked checkpoint:
**2026-10-26 21:21:49 UTC**, **5m 21s** between observed checkpoints. Actual turn start, active compute,
token/cost totals and final acceptance latency remain unknown. Model/effort remains user-verified
GPT-6.1-Sol / medium. One combined scan and one affected test run; no repeated or expanded suite.

### Exact final uncommitted delivery paths — 36

Also saved verbatim as `p4b-repair/changed-paths.txt`. This list includes the original P4B work and the
two newly authorized tracked paths. STATUS and ignored evidence are excluded from delivery/staging.

```text
blueearth_cst/indicators/README.md
blueearth_cst/indicators/sets/crop_water/README.md
blueearth_cst/indicators/sets/default/README.md
blueearth_cst/indicators/sets/eflow_erfa/README.md
blueearth_cst/indicators/sets/flood_risk/README.md
blueearth_cst/indicators/sets/flow_regime/README.md
docs/publishing-pilot/manifest.json
docs/site/toolbox-reference/assessment-workflow.qmd
docs/site/toolbox-reference/datasets.qmd
docs/site/toolbox-reference/modeling-tools.qmd
docs/site/toolbox-reference/overview.qmd
docs/site/toolbox-reference/retained-handoffs.qmd
docs/site/toolbox-reference/workflow-analyze-climate.qmd
docs/site/toolbox-reference/workflow-analyze-projections.qmd
docs/site/toolbox-reference/workflow-build-model.qmd
docs/site/toolbox-reference/workflow-generate-scenarios.qmd
docs/site/toolbox-reference/workflow-simulate-system.qmd
docs/site/toolbox-reference/workflows.qmd
docs/technical-manual/configuration.md
docs/technical-manual/datasets.md
docs/technical-manual/environment.md
docs/technical-manual/execution-and-provenance.md
docs/technical-manual/indicator-extension.md
docs/technical-manual/indicator-requests.md
docs/technical-manual/input-formats.md
docs/technical-manual/local-source-appendix.yml
docs/technical-manual/overview.md
docs/technical-manual/results-transfer.md
docs/technical-manual/retained-handoffs.md
docs/technical-manual/workflow-analyze-climate.md
docs/technical-manual/workflow-analyze-projections.md
docs/technical-manual/workflow-build-model.md
docs/technical-manual/workflow-generate-scenarios.md
docs/technical-manual/workflow-simulate-system.md
docs/technical-manual/workflows.md
tests/test_docs_pilot.py
```

Outstanding limits: source-link/fragment proof only; published routes, full HTML/PDF assembly, visual/offline
publication verification and external-link availability remain P5. Scientific/axis-authority decisions
remain deferred. No model/notebook execution, new agents, commits, landing, push or shared records.
The source repair is complete. **Source writes stopped for cst-main to commit.**
