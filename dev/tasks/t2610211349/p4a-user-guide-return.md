# P4A return — user and local guidance

Task: `t2610211349`. Recipient: cst-main. State: completed for coordinator review; uncommitted.
Branch: `docs/t2610211349-user-guide`, session-1. Base/HEAD: `a4d79ea605dba05a5962d254271d775ebbba97a0`.
P4A only. P4B integration and P5 publication assembly remain necessary before whole-publication acceptance.

## Outcome and scope

Prepared the ten canonical user-guide chapters, shortened overlapping source guidance, retained old setup
routes, and reconciled generated external-case instructions with version-identifiable local documentation.
The chapters now lead through actions, prerequisites, expected products and interpretation limits.
Exact configuration, retained-product and implementation contracts link to P4B owners.

There are 31 delivery paths: 25 modified tracked files and six new Markdown sources. No deletions.
Of the 34 inventoried sources owned by P4A, 23 changed and 11 were retained unchanged.
Six new chapters/maintenance sources and two bounded code/test files account for the remaining eight paths.
The other 21 of the original 55 sources belong to P4B (17) or deferred scientific writing (4).
They were not edited here. This is a P4A coverage return, not another 55-file review.

No commits, Git configuration/index changes, landing, cross-lane writes, shared task-record writes,
dependency changes, builds, model/notebook runs or data acquisition. Local ignored STATUS was updated.
Scratch ignore was verified with `git check-ignore -v` before writing; no ignore-policy change was needed.

## Every owned inventory disposition

Paths below are repository-relative. UG = `docs/guide/`; TM = `docs/technical-manual/`.
Destinations in TM are counterpart contracts, not substitute pages created in this lane.

| # | Inventoried source | Disposition, ownership and concrete consequence |
|---|---|---|
| U1 | `docs/guide/assets/shape-of-a-run.html` | Retain unchanged as the interactive asset. Quick start adds a static workflow/dependency explanation; no redesign or new surface procedure. |
| U2 | `docs/guide/benchmarking.md` | Shorten to opening summaries, comparing measurements and WF4 sampling limits. Exact files/fields/lifecycle move to TM `execution-and-provenance.md`; the two-second sampling, shared RSS, allocation-versus-RAM and unavailable-value cautions remain local reader context. |
| U3 | `docs/guide/configuration.md` | Retain the user chapter; replace exhaustive field/path contracts with numbered choices and links to TM configuration/input formats/workflows. Keep outlet-box example, drainage safety, plotting controls, path-version warning and experiment choice at point of use. |
| U4 | `docs/guide/outputs.md` | Retain product recognition, status/reason, dictionary, Excel identifiers and return-level qualifications. Add actual run/group joins; shorten file inventories, WF2 transfer and attribution into TM links. Keep reference membership and expanding monthly-join warning. |
| U5 | `docs/guide/quick-start.md` | Retain rapid-case procedure/data gates/time qualification. Add static dependency context, status/value recognition and own-case next step. Link new canonical installation; do not promise supplied data or a fast assessment. |
| U6 | `docs/guide/running.md` | Retain user launch/recovery/experiment procedures. Move detailed manifests/namespaces/provenance to TM retained-handoffs and execution reference; preserve V9 recalculation, figure regeneration and destructive-rebuild safety sections. |
| U7 | `docs/notebooks/Climate projections.ipynb` | Edit two Markdown cells only: current-status gate and stale rule/interface guidance. Link maintained guide/reference. Preserve every code cell, output, execution count and metadata field. |
| U8 | `docs/notebooks/Climate Stress Test.ipynb` | Edit three Markdown cells only: status, table interpretation boundary and current next steps. Response-surface construction remains unqualified/deferred; existing code is preserved, not endorsed. |
| U9 | `docs/notebooks/Model building.ipynb` | Edit eight Markdown cells only: status, configuration/rule guidance, safe recovery, evidence qualification and current stage links. Keep existing case findings/KGE discussion with its historical qualification; preserve all nonprose data. |
| U10 | `docs/notebooks/README.md` | Shorten to optional advanced source orientation, status, source-only policy and execution prerequisites. UG notebooks owns reader journey; local README retains notebook-source/outputs handling. |
| U11 | `docs/README.md` | Retain documentation map, now route to ten guide chapters, TM and existing scientific explanation. Distinguish editable sources from staged copies and unassembled publication. |
| U12 | `docs/site/404.qmd` | Retain route; simplify recovery links to landing/setup/current guide sources. Global site routing remains P5. |
| U13 | `docs/site/index.qmd` | Retain landing route; replace duplicate execution/setup prose with reader-task routes and limitations. New source links need P5 staging/URL reconciliation. |
| U14 | `docs/site/setup/env-setup-notes.md` | Retain tracked compatibility page and major incoming section routes. Detailed workaround/staging/recovery recipes now live once in `dev/scripts/environment-notes.md`. User symptoms route to UG troubleshooting. |
| U15 | `docs/site/setup/install.md` | Retain tracked compatibility page, session-runtimes and troubleshooting headings. User install procedure lives in UG install; session isolation and diagnosed fixes live in developer environment notes. |
| U16 | `README.md` | Shorten root orientation into install/example/own-basin/table-reading routes. Retain scientific purpose, upstream/fork attribution and license. Detailed command/configuration prose has central owners. |
| U17 | `scripts/README.md` | Retain execution-entry inventory and local script purpose. Add canonical guide/indicator routes; do not duplicate argument contracts owned by scripts/TM. |
| C1 | `config/basemap/README.md` | Retain unchanged local asset purpose/use. It is not another installation or scientific-method chapter. |
| C2 | `config/catalogs/archive/README.md` | Retain unchanged unsupported/archive boundary. Do not put archived catalogs in the supported starter route. |
| C3 | `config/defaults/README.md` | Shorten to live consumer roles, editing consequence and central reference. Distinguish live defaults from copyable templates; no default/YAML changes. |
| C4 | `config/plotting/README.md` | Retain local YAML editing/cache behavior. Replace detailed adapter inventory with TM link; keep UG plot-annotations pointer and Python-versus-R applicability. |
| C5 | `config/templates/archive/README.md` | Retain unchanged archive warning. No supported route or restoration of old execution advice. |
| C6 | `config/templates/example-basin/data/README.md` | Shorten local input preparation; preserve header-only observation warning, units/identity gate and central exact-schema pointer. No CSV edits or invented measurements. |
| C7 | `config/templates/example-basin/notes.md` | Retain unchanged blank run-evidence scaffold; never inherit success or basin adequacy. Generated notes retain the existing configured/not-run behavior. |
| C8 | `config/templates/example-basin/README.md` | Retain local copying checklist, stage choices and source-file inventory. UG new-case owns full journey. Explicitly explain source-relative links after manual copying and recorded checkout identity. |
| C9 | `config/templates/README.md` | Shorten duplicated model lists, defaults and observation schemas to local inventory plus TM links. Preserve 16-year requirement, external inputs, distinct observation/location purpose and unsupported archive boundary. |
| D1 | `dev/README.md` | Retain maintainer orientation; add environment-maintenance owner pointer. No policy copy or restructuring. |
| D2 | `dev/scripts/README.md` | Retain maintenance-helper inventory; add new environment-notes pointer and clarify central execution-guide route. |
| D3 | `dev/templates/figure-comparison.html` | Retain unchanged reusable comparison interface. No UI redesign, scientific-style or acceptance-policy change. |
| D4 | `dev/templates/figure-comparison.md` | Retain unchanged local use instructions for that comparison artifact; not a user-guide chapter. |
| D5 | `dev/templates/lane-status.md` | Retain unchanged lane-local status scaffold; no coordination-policy duplication. |
| D6 | `dev/templates/README.md` | Retain unchanged developer-template inventory and local purposes. |
| D7 | `dev/templates/workflow-report.html` | Retain unchanged reusable report interface; no publication or response-surface construction work. |
| D8 | `dev/templates/workflow-report.md` | Retain unchanged report-template use instructions. Its local operational purpose differs from interpreting production indicator tables. |

All 34 rows identify unique sources; retained sources are intentional no-ops, not omitted coverage.

## New sources and bounded generated-case change

| New/extra path | Content and acceptance boundary |
|---|---|
| `docs/guide/install.md` | Windows tools, locked install, additional R/Julia install, wiring/data checks and diagnosed-help routes. External P-drive/CMIP6 prerequisites and optional E2E cost are explicit. |
| `docs/guide/new-case.md` | External scaffolding/manual-copy choice, basin/input review and staged WF0/WF1/WF3/WF4 actions. Generated coordinates/settings alone do not establish readiness. |
| `docs/guide/indicators.md` | Numbered selection/recalculation actions; five local set authorities, required responses, strict/partial limits, status interpretation and advanced extension routes. No file-by-file internals. |
| `docs/guide/troubleshooting.md` | Symptoms, evidence-first diagnosis, owned-runner recovery, stale-lock safety, external data and missing-indicator distinctions. |
| `docs/guide/notebooks.md` | Optional advanced notebooks, opening procedure and explicit stale-interface/unqualified-surface limits. |
| `dev/scripts/environment-notes.md` | Existing setup workarounds, local data staging, fresh-environment recovery, borrowed/isolated session runtimes and Julia lock remedy. Moved from base setup pages; operational detail remains developer material. |
| `scripts/create_case.py` | Only generated prose/document links and one reused version value. Adds five absolute local checkout links, creation version, relocation caveat, external-data gate, workflow prerequisites and completed-record recalculation reminder. Provisioning/defaults unchanged. |
| `tests/test_create_case.py` | Extend existing actual-scaffold assertion to check those generated instructions/links. Explicitly inject the existing template fixture; no new model execution or policy test. |

Generated links use `<absolute local checkout path/docs/guide/chapter.md>` so an external case does not
resolve them against its own directory. They deliberately depend on the retained checkout and identify
its creation version. They are not hosted URLs or a second manual copy. The existing version helper may
include `-dirty`; it is not a content archive. Manual copies retain their README and its explicit guidance
to use the matching checkout; generated cases receive INSTRUCTIONS instead.

## Source/section ownership map and duplication removed

The ten guide chapters, in proposed P5 reading order, are install → quick-start → new-case → configuration
→ running → indicators → outputs → benchmarking → troubleshooting → notebooks. Existing headings in
running/outputs that carry the approved pilot contracts remain stable.

| Base source material | Maintained destination / section | Deliberate local context retained |
|---|---|---|
| Setup install/tools and quick-start prerequisites | UG `install.md#install-the-tools`, `#install-this-checkout`, `#check-the-environment-and-data` | Quick start repeats its actual catalog/network/time gates at execution. |
| Setup environment recipes and install Session runtimes | `dev/scripts/environment-notes.md#session-runtimes`, `#live-workarounds-automated-via-pixi-activation`, `#local-data-staging-p-drive-bypass`, `#recovering-from-a-fresh-env-build`, `#julia-installation-file-locks` | Old setup pages keep short route wrappers; UG troubleshooting describes symptoms rather than copying fixes. |
| Running external-case creation and starter README | UG `new-case.md#create-an-external-case`, `#review-the-case`, `#run-in-stages` | Starter keeps immediate replacement checklist; generated instructions keep exact case-local commands. |
| Guide configuration exhaustive path/field behavior | TM `configuration.md`; UG `configuration.md#how-paths-are-read`, `#anatomy` | YAML/key names needed for a user's edit, drainage refusal and plotting consequences remain. |
| Template observation/dataset/model-list detail | TM `input-formats.md`, `datasets.md`, `configuration.md` | Header-only warning, actual catalog names, identity/coverage gates and 16-year requirement remain local. |
| Running handoff records, namespaces and exact attribution | TM `retained-handoffs.md`, `execution-and-provenance.md` | User commands, experiment choice, full rebuild safeguards and indicators-only prerequisite remain in UG running. |
| Output file inventories and WF2 transfer command contract | TM `retained-handoffs.md`, `results-transfer.md` | UG `outputs.md#the-layout`, `#moving-wf2-results-to-another-project` retain recognition and limits. |
| Benchmark exact resource files/fields/lifecycle | TM `execution-and-provenance.md` | UG benchmarking retains sampling, attribution and interpretation cautions at point of comparison. |
| Indicator selection detail versus implementation | UG `indicators.md#choose-a-set`; TM `indicator-requests.md`, `indicator-extension.md`; canonical local module/set READMEs | Required variables, partial-mode behavior and set scientific caveats stay visible; formulas/internal registration are not copied into user steps. |
| Notebook duplicated rule tables/config contracts | TM `workflow-build-model.md`, `workflow-analyze-projections.md`, `workflows.md` | Notebook Markdown reports stale code and retains historical findings with explicit qualification. |
| Indicator dictionary and run/group table reading | UG `outputs.md#reading-an-indicator-set`, `#join-an-indicator-to-its-climate-settings`, `#opening-an-indicator-table-in-excel` | V9 dictionary/coverage, string IDs, empty reference and return-level limitations preserved; no surface-construction claim. |

TM links currently target chapters rather than guessed counterpart anchors. P4B's return must confirm its
sections and preservation of the removed detailed contracts before the two packets are accepted together.
The base remains the evidence for extraction; this packet does not certify P4B's unpublished content.

## Evidence and semantic preservation

- Source identity: matching recorded lane/branch/base; `session-check` reported clean at entry. Main's one
  newer commit then changed only task/board records, so no source synchronization was required/performed.
- Configuration/path claims: `blueearth_cst/shared/config_composition.py`, shipped project/workflow starter
  YAML and current guide/base reference. No schema, parameter/default or YAML changes.
- Workflow routing/prerequisites and experiment/recovery commands: owned scripts `run_workflows.py`,
  `run_workflow.py`, `simulate_system.py`, current base running chapter and accepted V9.
- Generated-case behavior: `scripts/create_case.py::_prepare`, existing `_toolbox_version`, starter and
  `tests/test_create_case.py`. Existing tests exercise refusal, copying, output-tree preservation,
  annotations, schema resolution and shipped starter as well as the new instruction assertions.
- Joins: `blueearth_cst/experiment/generation_publication.py::SCENARIO_HEADER` declares `run_id`,
  `evaluate`, `type`, `rlz`, `st_id`; `indicator_plan.py` writes run/group table keys and
  `group_metadata.csv` (`group_id`, `st_id`, `is_reference`). Run join is many-to-one on `run_id`;
  group join is many-to-one on `group_id`. Empty reference `st_id` is retained; twelve monthly rows
  expand a later perturbation join. No new axis authority or aggregation policy is asserted.
- Scientific boundaries: WF2 remains independent projection plausibility context; WF1/WF3 independently
  supply WF4. No calibration, supplied external data, basin adequacy, supported fast run or completed new
  surface tutorial is promised. Existing return-level benchmark/GEV-shape/uncertainty qualifications,
  block coverage and annual depth caveats remain in outputs. Local set sources retain formula authority.
- Useful repeated context is intentional: data gates before execution; required retained responses before
  indicator selection; scientific caveats beside table reading. Detailed contracts have central owners.
- Notebook nonprose preservation is mechanically checked, including every code cell/output/execution
  state and all metadata. Historical model findings/KGE prose was retained with qualification.

## Conflicts, pending links and later-stage work

One actual source conflict is reported for P4B/cst-main: `climate.window` is implemented as inclusive
calendar years by `blueearth_cst/shared/wf3_science.py::historical_window_bounds` (January 1–December 31),
while starter comments use water-year wording. UG now describes that climate window as calendar years.
No YAML/comment/algorithm change was made. Historical model-window wording is kept distinct; P4B should
record the exact contract rather than infer equivalence. This is not a new scientific decision.

Twelve unresolved source destinations are explicitly owned by P4B:
`configuration.md`, `datasets.md`, `execution-and-provenance.md`, `indicator-extension.md`,
`indicator-requests.md`, `input-formats.md`, `overview.md`, `results-transfer.md`,
`retained-handoffs.md`, `workflow-analyze-projections.md`, `workflow-build-model.md`, `workflows.md`
under `docs/technical-manual/`. Do not treat these as resolved merely because other local links pass.

P5 recommendations (not implemented):

1. Stage all ten `docs/guide/*.md` chapters rather than the previous five, retain `guide/assets/`, and
   order site/book navigation using the sequence above. Keep quick start separately reachable.
2. Reconcile site-index/404 and setup-wrapper source links (`../guide/…`, `../../guide/…`) with the
   staged guide URLs; preserve current setup URLs and important incoming anchors. Source-relative links
   resolve in the repository; that does not prove published HTML/PDF links.
3. Include TM chapters plus canonical module/five-set README excerpts through the accepted assembly
   mechanism. Do not copy separately editable formulas or internal file inventories into UG indicators.
4. Handle developer environment notes as repository/advanced links with an intentional offline policy;
   do not make the developer maintenance recipes another user-guide chapter.
5. Carry the quick-start static text when iframe interactivity is unavailable. Asset remains unchanged;
   PDF rendering/link behavior still needs P5 verification. No new interactive/static surface is supplied.
6. Validate whole-manual source/public route rewrites, local-source includes, PDF composition and anchors
   after both content packets integrate. `_quarto.yml`, publishers, pilot manifests and shared tests were
   deliberately untouched here.

Notebook code remains stale in places (configuration reads, paths and indicator interfaces). Its repair,
execution and response-surface teaching are separate owner decisions. The Markdown gate makes this visible;
no code-cell repair or scientific requalification is claimed. Other content-accuracy questions outside the
scoped structural/user-guide work remain deferred, not silently investigated or answered.

## Checks, results and rework

All checks used the compatible main environment, without installation, while importing session-1 sources.
Borrowed-runtime prefix:

```powershell
& 'C:/Users/taner/workspace/blueearth_cst/.pixi/envs/default/python.exe' -B dev/scripts/session_runtime.py --runtime-root 'C:/Users/taner/workspace/blueearth_cst' -- <command>
```

| Check | Actual result / evidence |
|---|---|
| Branch/base/session identity; initial/final scope | Correct branch and `a4d79ea6` HEAD; 31 allowed delivery paths. No P4B/excluded/shared paths edited. |
| `python -m pytest tests/test_create_case.py tests/test_notebook_outputs.py -q` | Final normal-permission run: **44 passed in 7.76 s**; `p4a-tests-final.log`. No model/notebook execution. |
| `ruff check scripts/create_case.py tests/test_create_case.py` | Passed on final files; earlier log `p4a-ruff.log`, final command output also retained in conversation. |
| `ruff format --check scripts/create_case.py tests/test_create_case.py` | Final: two files already formatted. Initial added assertions required line wrapping; fixed. |
| `git diff --check` | Passed. Git emitted only LF→CRLF notices for the two Python files. |
| `.tmp/tasks/t2610211349/check-p4a.py` | Passed; `p4a-source-checks.json`: 241 file-link occurrences, no unexpected broken local targets, 12 named P4B pending destinations. Source-link check recognizes already configured staged guide copies, not a build. |
| Notebook JSON/nonprose comparison against HEAD | Passed: 8 model, 2 projections and 3 stress-test Markdown cells changed; all other cell data/metadata/top-level state identical. |
| `.tmp/tasks/t2610211349/check-p4a-anchors.py` | Passed; `p4a-anchor-checks.json`: no tracked Markdown/QMD/notebook incoming fragment links to removed source headings. This is a source-heading scan, not rendered-anchor certification. |
| Generated INSTRUCTIONS inspection | Read actual final-test fixture `run-300163f21d974e07b29e71e6c9174f01/test_create_preserves_template0/cases/applications/new-basin/INSTRUCTIONS.md`; version, five local links, prerequisite/record gates and existing recovery/rebuild commands present. Fixture toolbox is intentionally synthetic; real-source link existence was checked separately. |
| Reader journeys, source inspection | Example: installation→external catalog/network gate→rapid preview/run→summary/status. Own basin: scaffold→review settings→WF0 alone→WF1/WF3→WF4. Interpretation/extension: dictionary→run/group joins→local conventions→advanced module/TM. No execution or fresh-reader acceptance claim. |

Rework is visible rather than concealed:
- First sandbox pytest attempt: 9 failures/35 passes from Windows `WinError 5` private temporary-directory
  access, not failed product assertions. Retained `p4a-tests.log`; no ACL/tempfile production workaround.
- First normal-permission attempt: 43 passes/one failure in my added assertion because the template fixture
  function was referenced without injection. Fixed the test signature, then all 44 passed.
- Normal-permission test tempfiles could not be inspected from the restricted sandbox; the required read-only
  inspection was repeated with normal permissions. No automatic-approval rejection occurred.
- A scratch transformation initially stopped at a boundary renamed by V9; repaired to slice current base
  headings and reran. Final source reads/diffs/checks cover the result.
- One exploratory PowerShell recursive listing met those same temporary ACLs, and one `rg` wildcard was
  unsuitable on Windows; used the known literal file path and `rg -g '*.md'` instead. Neither changed sources.

No full documentation build, PDF render, external-link network check, numerical validation or workflow run
was performed; none is commissioned by P4A. This packet is ready for cst-main content review, not a claim
that the full website/offline manual has been assembled or accepted.

## Role, loaded guidance and measurements

Canonical role: full manually applied
`C:/Users/taner/workspace/brain-infrastructure/artifacts/agents/technical-writer.md`.
Native persona activation is not claimed. Owner/UI-reported model: GPT-6.1-Sol, medium.
Backend model/effort cannot be independently observed here; no attempted fallback is claimed effective.

Role-bound skill lookup used infrastructure `_external/<name>/SKILL.md` before `<name>/SKILL.md`.
Completed earlier reads were reused when still applicable. Newly triggered bodies/references were read
before their governed edits/checks; truncated aggregate reads were completed with consecutive bounded reads.
No governing skill/reference read remains incomplete.

Actual applied/reused skills and loaded references:

- `scientific-software-documentation`: full body; `readme-authoring`, `site-structure-and-lifecycle`,
  `task-guides-and-troubleshooting`, `documentation-review-and-accessibility`. Applied reader-task
  structure, central/local ownership, source routes and scientific qualifications.
- `project-reference-docs`: full body; `current-state-reference`, `audit-checklist`,
  `history-and-archaeology`. Applied current-source precedence and one-home detailed contracts.
- `tutorial-authoring`: full body and checklist. Applied prerequisite/actions/expected-product journeys.
- `writing-feedback-revision`: full body and `revision.md`. Applied accepted V9 reader level and owner
  corrections; no new scientific wording contract.
- `quarto`: full body. Applied source-versus-staging distinction and compatible wrappers; no advanced
  syntax/assembly reference was triggered because P5 construction was not performed.
- `project-system`: full body; layout, Python/hybrid layout, migration, workflow and phased-execution
  references. Applied lane-local STATUS, scratch retention and scoped handoff. No shared records.
- `git-workflow`: full body, repository configuration, configuration/options, session-slots, worktrees,
  branching and failure-handling references. Applied identity/read-only session check and preservation;
  explicit commission prohibits commits/landing despite ordinary configured lifecycle defaults.
- `testing-policy`: full body plus configuration and execution-checks. Applied focused scaffold/source
  checks and recorded sandbox limitation; no broad build/run gate invented.
- `python-discipline`: full body plus style-and-docs, python-validation and hazards. Applied bounded
  template change, existing-test extension, Ruff and focused tests; no runtime refactor.
- `task-brief`: full body and `references/task-brief.md`, reused for bounded coordinator handoff and
  explicit ownership/acceptance limits; no new worker or delegation.

Governing project reads included current `dev/reference/dev-documentation.md`, applicable validation,
layout/naming and task/session guidance, full P4 assignment, current execution plan, accepted boundary
map/final decisions, inventory and V9 return. Excluded guidance was evidence only. No nested agents used.

Start: **2026-10-26 20:47:09 UTC**. End: **2026-10-26 21:08:20 UTC** (final review checkpoint).
Elapsed to checkpoint: **21 min 11 s**. Test durations above are pytest-reported, not task elapsed time.
Input/output/cached tokens, cost and conversation identifier: **unknown/unavailable**.
Delivery: uncommitted s1 changes plus this ignored evidence packet, awaiting cst-main acceptance.

## Coordinator review correction — bounded follow-up

Follow-up start: **2026-10-26 21:16:15 UTC**. This section updates the initial return above.
Only `docs/guide/indicators.md` and `docs/guide/outputs.md` changed in this follow-up, plus local
STATUS/evidence. Delivery scope remains 31 paths; all 34 owned dispositions remain accounted for.

1. Replaced the author-facing instruction about copying preparation rules with a reader action:
   follow the selected set's instructions for required thresholds or historical inputs.
2. Both guides now distinguish absent responses from missing parameters at retained locations.
   In partial mode an absent response omits the whole calculation from value tables; its declaration
   and missing-input explanation remain in the dictionary/manifest. Missing location parameters can
   instead produce unavailable rows with no value. Malformed supplied parameters still fail.
   Both point advanced readers to TM `indicator-requests.md#inputs-evaluation-and-recovery`.
   Evidence: current s2 P4B chapter, read fully; no new implementation/accuracy audit.
3. Restored the approved V9 three-step Configuration excerpt verbatim in canonical
   `docs/guide/indicators.md#configuration`. It replaces the abbreviated selection steps rather than
   adding a second copy in the guide. The separate `#choose-a-set` heading remains as the existing
   scientific-convention link target. Exhaustive contracts remain with P4B.

Exact extraction contract sent to s2 api-documenter-p4b:

```json
{
  "source": "docs/guide/indicators.md",
  "start": "Edit `project_config_simulate_system.yml`,",
  "stop": "calendars, missingness or grain.",
  "include_stop": true,
  "heading": "## Configuration",
  "anchor": "configuration"
}
```

S2 acknowledged these boundaries and owns the manifest repair/isolated-overlay check. No manifest,
counterpart chapter or shared test was edited from s1. Existing running, outputs, default README and
annex extraction selectors remain unchanged. No extra duplicate reference section was introduced.

Checks on the corrected candidate:

- `check-p4a-review.py`: passed; `p4a-review-checks.json` confirms unique Configuration delimiters,
  byte-equal extracted text to approved base V9, four unchanged guide extraction ranges and corrected
  partial-mode wording. No build or execution.
- `check-p4a.py`: passed; updated `p4a-source-checks.json` records **243** file-link occurrences,
  no unexpected broken source links and the same twelve P4B destinations pending in s1.
  Notebook nonprose preservation remains unchanged.
- `check-p4a-anchors.py`: passed, no incoming source links to removed headings.
- `git diff --check`: passed, only existing LF→CRLF notices for the two Python files.
- The earlier 44-test scaffold/notebook pass remains applicable: this follow-up changes only prose,
  with no new code/configuration behavior. No redundant pytest run, build or model execution.

Role and skills: continuing full canonical technical-writer, owner-requested medium; reused completed
scientific-software-documentation, writing-feedback-revision, tutorial-authoring, testing-policy,
project-system and project-reference-docs reads/references. Quarto assembly remains s2's bounded repair;
no newly applicable skill body/reference was left unread. Canonical role reread completely.
No governing read is incomplete; token/cost measurements remain unknown. No commits or shared records.

Follow-up final source/check checkpoint: **2026-10-26 21:18:15 UTC**; elapsed **2 min 00 s**.
S2 subsequently confirmed its manifest now names the canonical guide with the exact delimiters above
and its partial-mode table separates absent responses from missing location parameters. Its combined
source-link/anchor check remains s2-owned; this packet does not preclaim that result.
