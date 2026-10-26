# P5 publication assembly return

Task `t2610211349`; continuing technical-writer editorial lead; recipient cst-main.
Status: **P5 complete for coordinator acceptance and P6**. One minor duplicate-title finding is retained.
Lane: session-1, `docs/t2610211349-publication-assembly`; starting HEAD `856bc47c0d20e84acd34554e3f72cdc97dff8538`.
Start UTC: **2026-10-26 21:29:55**. This packet will be completed after rendered checks.

## Settled contract and ownership

P4 sources are accepted. Publish the ten user-guide and sixteen technical-manual chapters as complete
HTML/PDF volumes, include all six complete canonical module/set sources in the technical manual,
preserve V9 wording/visual conventions, retain old routes/anchors and existing scientific text.
Promised endpoint remains indicator-table interpretation, selection and extension; supported
response-surface construction and new scientific writing remain deferred.

S1 owns documentation manifests, Quarto navigation/configuration, editorial integration and rendered review.
Explicitly authorized root `.gitignore` entries cover only generated publication trees.
S2 python-engineer-p5 owns the publisher/stager, Lua link filter and affected software tests.
Coordinator alone transfers/integrates code, commits/lands and writes shared records.
No nested agents, scientific/runtime edits, model/notebook execution, dependency install, push or deployment.
No retained P3/P4 evidence was deleted or overwritten.

## Frozen source and builder interface

`docs/publication/manifest.json`, schema 1, fixes both chapter lists and reading order.
Its fields are `schema_version`, `source_revision`, `repository_url`, `format`, `asset`,
`appendix_manifest`, and `publications` containing `id`, `title`, `chapters`, `include_appendices`.
The existing `docs/technical-manual/local-source-appendix.yml` owns six-source order/anchors and exclusions.
`docs/publication/format.yml` retains V9 Cosmo, left-aligned Typst, A4/11pt, 20mm horizontal and 18mm vertical
margins, and disabled computation. No second editable prose copy is created.

Agreed engineer API: `stage_publications(source_root, output)` returns consumed source hashes;
`build_publications.py --source-root PATH --output PATH [--stage-only]` stages and renders full volumes.
Generated chapter routes use `.qmd`, while canonical sources remain `.md`.
Site filter `../../dev/scripts/publication_links.lua` uses the generated publication link map to rebase
tracked wrappers during rendering without changing their working source links.
Maps/hashes live under ignored `docs/site/technical-manual/`.

Generated volume routes: `manuals/user-guide.html|pdf`, `manuals/technical-manual.html|pdf`.
Site chapter routes: `guide/*.html`, `technical-manual/*.html`,
`technical-manual/appendices/<declared-anchor>.html`.
Build complete volumes in task scratch, copy HTML/PDF download resources, then render the website.
`docs/publication/README.md` owns exact full/borrowed-runtime commands and generated-output handling.

The source label identifies a local candidate based on `856bc47c`; input hashes identify actual consumed
files. The repository locator does not claim new/unpushed files exist online. No network availability
claim is made. External repository evidence remains labelled and separate from the offline content.

## All 55 inventoried source dispositions

UG = `docs/guide/`; TM = `docs/technical-manual/`. These are final placement/inclusion dispositions,
not a fresh scientific/content-accuracy audit. Each original source appears exactly once.

| ID | Original source | Final home, inclusion and compatibility |
|---|---|---|
| 01 | `docs/guide/assets/shape-of-a-run.html` | Retain canonical interactive asset unchanged; guide/volume uses derived SVG, legend and all five descriptions as the static alternative. |
| 02 | `docs/guide/benchmarking.md` | Complete UG chapter in HTML/PDF; detailed lifecycle contract remains in TM execution/provenance. |
| 03 | `docs/guide/configuration.md` | Complete UG chapter; numbered user choices retained; TM configuration/input formats own exhaustive contracts. |
| 04 | `docs/guide/outputs.md` | Complete UG chapter, including run/group joins, dictionary/status, reference IDs and return-level qualifications; no surface-construction claim. |
| 05 | `docs/guide/quick-start.md` | Complete UG chapter and direct navigation route; external-data/time qualifications and rapid-case purpose retained. |
| 06 | `docs/guide/running.md` | Complete UG chapter; V9 recalculation, experiment/recovery and rebuild-safety procedures preserved. |
| 07 | `docs/notebooks/Climate projections.ipynb` | Retain source-only, unexecuted, outside volumes/site render; UG notebooks routes advanced readers to source with stale-interface qualification. |
| 08 | `docs/notebooks/Climate Stress Test.ipynb` | Retain source-only, unexecuted; no supported response-surface tutorial promised. No P5 cell changes. |
| 09 | `docs/notebooks/Model building.ipynb` | Retain source-only, including P4-qualified historical findings; no P5 code/prose/metadata changes. |
| 10 | `docs/notebooks/README.md` | Retain local notebook-source/outputs policy, repository-only; central optional notebook chapter supplies user entry. |
| 11 | `docs/README.md` | Retain source orientation and canonical owner map; update full publication/build pointers, outside book content. |
| 12 | `docs/site/404.qmd` | Retain rendered 404 route, point to current chapters/manuals/downloads. No duplicate substantive content. |
| 13 | `docs/site/index.qmd` | Retain website landing; point to canonical staged chapters, complete manuals and unchanged existing science. Remove task-stage wording. |
| 14 | `docs/site/setup/env-setup-notes.md` | Retain old source/rendered route and anchors; user help routes centrally, detailed maintenance stays repository-only. |
| 15 | `docs/site/setup/install.md` | Retain old source/rendered route and headings; canonical UG install supplies full setup procedure. |
| 16 | `docs/site/toolbox-reference/assessment-workflow.qmd` | Retain compatibility route/anchors; TM workflows supplies maintained content in both volumes/site. |
| 17 | `docs/site/toolbox-reference/datasets.qmd` | Retain compatibility route/anchors; complete TM datasets chapter is canonical. |
| 18 | `docs/site/toolbox-reference/modeling-tools.qmd` | Retain route to TM overview/components. |
| 19 | `docs/site/toolbox-reference/overview.qmd` | Retain route/sections anchor; canonical TM overview is the main navigation entry. |
| 20 | `docs/site/toolbox-reference/retained-handoffs.qmd` | Retain route/all former anchors; canonical complete TM handoff chapter. |
| 21 | `docs/site/toolbox-reference/workflow-analyze-climate.qmd` | Retain old WF0 route/anchors; complete TM WF0 includes unchanged scientific interpretation/Ntoum findings and qualifications. |
| 22 | `docs/site/toolbox-reference/workflow-analyze-projections.qmd` | Retain old WF2 route/anchors; canonical complete TM WF2 and shared transfer/provenance owners. |
| 23 | `docs/site/toolbox-reference/workflow-build-model.qmd` | Retain old WF1 route/anchors; canonical complete TM WF1. |
| 24 | `docs/site/toolbox-reference/workflow-generate-scenarios.qmd` | Retain old WF3 route/anchors; canonical complete TM WF3. |
| 25 | `docs/site/toolbox-reference/workflow-simulate-system.qmd` | Retain old WF4 route/anchors; complete TM WF4, generic request reference and local set authorities. V9 simple Configuration remains in canonical UG indicators. |
| 26 | `docs/site/toolbox-reference/workflows.qmd` | Retain old route/anchors; one maintained workflow overview in complete TM workflows. |
| 27 | `README.md` | Retain repository orientation, supported journey/data gates and canonical links; no duplicate full manual or P5 prose rewrite. |
| 28 | `scripts/README.md` | Retain local execution-entry inventory, central guide links and exact contract owners; repository reference only. |
| 29 | `docs/site/scientific-approach/climate-information.qmd` | Scientific writing deferred. Existing source/text and website route retained unchanged; not included in either newly assembled volume. |
| 30 | `docs/site/scientific-approach/conventions-and-interpretation.qmd` | Scientific writing deferred; unchanged existing website material, no new scientific/axis authority claim. |
| 31 | `docs/site/scientific-approach/models-and-methods.qmd` | Scientific writing deferred; unchanged existing website material, no new method/qualification writing. |
| 32 | `docs/site/scientific-approach/overview.qmd` | Scientific writing deferred; retain existing linked overview and website route, no claim of a completed new science volume. |
| 33 | `blueearth_cst/indicators/README.md` | Retain canonical module contract; complete offline TM appendix `indicator-module`, with source-relative links rebased and advanced details preserved. |
| 34 | `blueearth_cst/indicators/sets/crop_water/README.md` | Retain complete canonical preparation/convention contract; complete offline appendix `indicator-crop-water`, including Qcrit prerequisites/provenance. |
| 35 | `blueearth_cst/indicators/sets/default/README.md` | Retain canonical default conventions and advanced section; complete offline appendix `indicator-default`. V9 reader wording/formulas/limits preserved. |
| 36 | `blueearth_cst/indicators/sets/eflow_erfa/README.md` | Retain complete canonical appendix `indicator-eflow-erfa`; oracle/test evidence remains explicitly external. |
| 37 | `blueearth_cst/indicators/sets/flood_risk/README.md` | Retain complete canonical appendix `indicator-flood-risk`; supported-probability/sample qualifications preserved. |
| 38 | `blueearth_cst/indicators/sets/flow_regime/README.md` | Retain complete canonical appendix `indicator-flow-regime`; formulas, inputs and missingness preserved. |
| 39 | `config/basemap/README.md` | Retain local asset instructions, unchanged and repository-only; no redundant book chapter. |
| 40 | `config/catalogs/archive/README.md` | Retain archive warning, unchanged/outside supported publication routes. |
| 41 | `config/defaults/README.md` | Retain local live-default consumer/pointer role; TM owns central contracts. No YAML/default changes. |
| 42 | `config/plotting/README.md` | Retain local appearance edit/cache notes; UG plotting and TM contracts remain authoritative. Repository resource, no additional appendix. |
| 43 | `config/templates/archive/README.md` | Retain unsupported archive boundary, unchanged; no normal user navigation. |
| 44 | `config/templates/example-basin/data/README.md` | Retain point-of-use input provenance/header-only observation warning; exact schema in complete TM input formats. |
| 45 | `config/templates/example-basin/notes.md` | Retain blank run-evidence scaffold; no inherited success claims or publication copy. |
| 46 | `config/templates/example-basin/README.md` | Retain local/manual-copy checklist and matching-checkout guidance; UG new-case chapter supplies full journey. Generated INSTRUCTIONS reconciliation accepted in P4, unchanged here. |
| 47 | `config/templates/README.md` | Retain starter inventory/local preparation gates; central full configuration/input-format references replace detail duplication. |
| 48 | `dev/README.md` | Retain developer orientation, unchanged/outside site/volumes; not silently published by a broad source glob. |
| 49 | `dev/scripts/README.md` | Retain maintenance-helper orientation, unchanged/outside volumes. Detailed environment recipes remain developer material. |
| 50 | `dev/templates/figure-comparison.html` | Retain unchanged reusable developer comparison interface; not included or redesigned. |
| 51 | `dev/templates/figure-comparison.md` | Retain unchanged local use guidance; not a central user procedure. |
| 52 | `dev/templates/lane-status.md` | Retain unchanged developer scaffold; not published. |
| 53 | `dev/templates/README.md` | Retain unchanged developer template inventory; not published. |
| 54 | `dev/templates/workflow-report.html` | Retain unchanged developer report interface; not included/redesigned. |
| 55 | `dev/templates/workflow-report.md` | Retain unchanged local report-template guidance; not published. |

## Checks and rendered evidence

Coordinator transferred the accepted five-file engineering commit into s1, advancing HEAD to
`872b8075ecb523032be03270afb354286d69c1b8`, preserving the editorial diff. Source writes were paused for
that integration. I did not copy/edit/commit the engine. Its retained return is
`session-2/.tmp/tasks/t2610211349/p5-engine-return.md`.

All **63** consumed input hashes from the engineer's final build match current s1. The full-volume build
and its 26-test/Ruff/format/compile evidence were reused on that equivalence, not described as new s1
execution. The actual engineering build completed at **21:53:03 UTC**, exit 0, **16.86 s**.
Only the four rendered HTML/PDF downloads were copied into ignored s1 `docs/site/manuals/`.
After the complete website render, all 63 hashes still matched and all four published downloads were
byte-identical to the reused originals. No canonical source drift or model/notebook execution occurred.

The main runtime helper confirmed session-1 source imports and Quarto **1.9.38**. No environment install.
PDF review reused existing infrastructure PyMuPDF **1.27.2.3**, as retained P3 evidence prescribes.

| Check | Actual result and evidence |
|---|---|
| Complete volumes, reused attributable engineering build | UG **21 pages**, TM **42 pages**. Ten guide chapters, sixteen manual chapters, six complete appendix pages/roots. `session-2/.tmp/tasks/t2610211349/p5-engine/artifact-proof.json`. |
| Full-volume HTML/PDF links/resources, reused | **517** HTML links resolve; sources/resources are embedded data URIs. All **29** sibling PDF URI names exist in the other PDF; **301** native named links and **183** named destinations across both PDFs. Cross-reader jumping remains qualified. |
| Full website build, fresh s1 | Main runtime helper → `quarto render docs/site --no-execute`, in visible unfocused Herdr watch pane `w8:p5`; **52/52 render targets**, exit **0**. `.tmp/tasks/t2610211349/p5/site-build.log`; terminal marker `P5_SITE_BUILD_EXIT=0`. |
| All rendered website files/links | Scratch `p5/check-site.ps1`: **55 HTML files** (52 pages, two complete volumes, interactive asset), **3,329** local href/src occurrences, zero missing files/fragments; all **37** old reference anchors retained. `p5/site-link-proof.json`. No external availability claim. |
| HTTP serving | `local-preview` served the bounded `_site` directory at `http://127.0.0.1:56457/`; landing, downloads, indicators, crop appendix, old WF4 route and both PDFs returned **200**, with expected artifact sizes. HTTP checks establish serving, separately from browser review. |
| Actual browser review | Connected Chrome/Umit, normal viewport. Inspected landing, download table/qualification, complete UG Configuration, cross-volume Default link, default conventions/advanced boundary, quick start, old WF4 Configuration route and maintained destination, search results and crop appendix/formula table. Actual local links followed; not inferred from HTTP. |
| Search and interaction | Searching **Qcrit** found five matching documents including complete crop-water appendix; followed that result. Diagram click **WF3** updated title to `generate_scenarios`; keyboard **Enter** on focusable **WF1** control updated it to `build_model`. Static legend/SVG/all five descriptions remain present in the rendered reading route. |
| PDF all-page visual review | Rasterized all **63** pages; inspected **eight labelled contact sheets** covering every page. Detailed full-size checks: UG pp. **6, 14, 17** (diagram, V9 Configuration/partial mode, join code), TM pp. **8, 38, 40** (input-format table/units, default return-level conventions, crop equations/table). No clipping, overlap, missing glyph or lost essential content observed. Files in `p5/visual/`. |
| Source/scope/whitespace | All63 consumed hashes unchanged after render; no edits to scientific pages, notebook data/code, runtime configuration/defaults or excluded guidance. `git diff --check` passes. Root ignores cover only generated TM/download trees. |
| Coverage reconciliation | Return contains exactly **55 unique inventory IDs/sources**, including four explicitly deferred scientific revisions. Every source retained or mapped to its canonical publication/local owner; no silent deletion. |

Browser review used supported CUA APIs, not shell browser automation. One heading text read timed out after
a successful navigation; a screenshot confirmed the correct section. An initial keyboard probe targeted an
SVG text child that cannot receive focus; inspecting live DOM attributes identified its role-button parent,
and Enter on that parent passed. These were observation/selector corrections, not product repairs.
Formal accessibility certification, mobile/responsive-device coverage, external-link availability,
scientific adequacy and numerical reproduction were not claimed.

Preview lifecycle: task-local `BRAIN_PREVIEW_STATE`, task-owned visible watch tab; review tab closed and
`local-preview <same-directory> --stop` invoked after the completed browser review. No browser denial or
unavailable connection occurred. No global setting/server/permission policy was changed.

### Reported rendered issues

1. **Alternate-format label regression, subsequently corrected below.** Complete HTML volumes initially showed
   both **PDF** and an unwanted automatic **Typst** entry. V9 requires only the labelled PDF entry.
   Generated metadata in `build_publications.py` uses a mapping for the HTML format; the successful V9
   metadata used a literal `html` entry plus the labelled Typst/PDF mapping. The builder overwrites the
   format file's field, so this cannot be repaired in writer-owned metadata alone. Reported concrete file,
   consumer and screenshot to cst-main; the same engineer was resumed. No engine edit by this writer.
2. **Minor duplicate appendix titles.** Website appendix pages show both the generated metadata title and
   the complete README's H1. Example: crop-water shows two identical titles. Full-volume HTML/PDF is
   unaffected. Reported to cst-main for disposition; a metadata-only suppression of the appendix title block
   would preserve source body/navigation title. No unassigned engine or source-body change made.

The format-label correction invalidates only affected HTML metadata/UI evidence if PDF/source consumer
hashes remain equivalent. Reuse full website/PDF evidence and recheck the corrected alternate-format UI;
do not repeat the whole suite or all-page visual review without an invalidated claim.

## Role, skills and measurements

Canonical technical-writer role applied manually, generic/degraded runtime. Full role reread.
Requested GPT-6.1-Sol/medium; actual UI footer observed through Herdr in this lane reports
**GPT-6.1-Sol medium**. No setting change or fallback is claimed. Backend identity is not independently
introspected. Conversation ID observed through the thread surface: `01a17846-bf43-7420-aea9-623ae9f3b811`.
Input/output/cached tokens, cost and active-compute time remain unknown.

Applied complete skill bodies: canonical `scientific-software-documentation`, `quarto`, `testing-policy`,
`project-system`, `writing-feedback-revision`; role-bound PDF resolves first to
`brain-infrastructure/artifacts/skills/_external/pdf/SKILL.md`, read completely and applied to PDF review.
Herdr body read completely before its controls; computer-use body read before browser review, with native
Windows guidance loaded but no native-app automation performed. Browser actions use the supplied CUA API.
Earlier applicable completed task-brief/project-reference guidance is reused for the bounded handoff.

Triggered/reused references: scientific README/site lifecycle/task guide/accessibility guidance;
Quarto reference map and current official navigation/project/Typst documentation; project lifecycle,
layout/migration/phased-execution; revision fidelity; testing configuration/execution checks; governing
repository documentation/validation/session-runtime/preview guidance. Native-app-only API/confirmation
references are not governing because review uses browser surfaces, not Windows app automation.
Any additional triggered references will be recorded before their governed actions.

Reads: current continuation authority/P5/P6/check sections, retained P4 returns including correction
addenda, accepted boundary-map final reconciliation and current accepted sources. Truncated aggregate
reads were completed with bounded reads; complete earlier verified reads were reused where applicable.
No known governing read remains incomplete at this checkpoint.

Coordination/rework: two shared-server engineer sends failed with active-writer errors. They were not
interpreted as agent termination; owner supplied Herdr channel. Restricted-token Herdr access failed,
then the same authorized control succeeded with normal permissions. No server/policy change.
Herdr messages preserve focus. Engineer implementation remains disjoint from editorial writes.

Completion time, final changed paths, builds, rendered findings and remaining limitations follow below.

## Settled cross-format navigation qualification

Coordinator chose format-specific sibling links: HTML → sibling HTML; PDF → sibling
`.pdf#nameddest=<namespace>` URI. Two PDFs suffice for the PDF reading route; no HTML companion is required.
Engineer verifies emitted sibling named destinations. Downloads and maintained build guidance state:
“Links between PDFs may open the volume without jumping to the section, depending on your PDF reader.
Use the contents if needed.” This does not claim native GoToR actions or universal viewer behavior.
No workaround dependency or new reader promise was added; final verification is recorded below.

## Final bounded correction and acceptance

Coordinator transferred the two-file engineer repair, advancing s1 to final HEAD
`ccd79230726c67abbe0a6151ee58a9bf63b16d36`; the writer's documentation diff was preserved.
Source writes were paused during both coordinator integrations. No commit, merge or engineer-file edit
was performed by this writer.

Only the two corrected HTML volume outputs were refreshed in `docs/site/manuals/` and
`docs/site/_site/manuals/`. The engineer's `format-links-proof.json` records two HTML renders in
**10.688 s**, unchanged source bodies, all **63** consumed hashes unchanged, and unchanged PDF bytes.
It also caught/corrected the old UG format-menu target pointing at the technical-manual PDF.
No full website build or PDF render was repeated after this metadata/menu-only correction.

Fresh Chrome inspection of the actual final served HTML confirmed:

| Volume | PDF-labelled links | Exact href | Typst-labelled links |
|---|---:|---|---:|
| User guide | 1 | `user-guide.pdf` | 0 |
| Technical manual | 1 | `technical-manual.pdf` | 0 |

Both menus were visually inspected. An exact accessible-name locator initially missed the added PDF icon;
the observed icon+PDF label was matched correctly and the href/count verified. This was a selector
correction, not a product defect. The repaired HTML was served in a short second bounded preview at
`http://127.0.0.1:50772/`; its review tab was closed and that preview stopped as well.
This final check was limited to the affected menus. Earlier full website/PDF proof remains applicable;
the original whole-site link counts describe the pre-menu-correction scan, not an invented repeat.

Local PDF hash checks independently confirmed unchanged final bytes:

- UG: `cc11f4ac57ec68d02d015c47796c1df35e9b4bcc7db3d0948512dc38acaff846`.
- TM: `745776c51725965cd1868aa47cac18d1a6103a0c8f55b6cf1187b950a15a8be0`.

The 37 old reference anchors plus **five** retained setup-section anchors were checked in rendered HTML.
Final `git diff --check` passes. No source/consumer change invalidates the all-page PDF visual review,
website navigation/search/diagram review or unchanged chapter/appendix source/body evidence.

**Remaining minor finding for P6:** website appendix pages can repeat their title, because the page title
and retained source H1 both render; crop-water was directly observed. It does not hide content or block
navigation. Coordinator explicitly retained it as a minor finding rather than expanding the repair.
Full-volume HTML/PDF is unaffected by this appendix-page duplication. No other unresolved rendered defect
was identified in the commissioned checks. This is author verification, not P6 fresh-reader acceptance.

## Exact writer delivery — 11 uncommitted paths

| Path | Change |
|---|---|
| `.gitignore` | Ignore only generated site TM and complete-volume download trees. Explicitly authorized. |
| `docs/README.md` | Canonical full-publication source/build pointers; remove obsolete pending-assembly wording. |
| `docs/publication/README.md` | Reusable exact locked/borrowed-runtime build, four-file copy and site-render recipe; no personal runtime path/task-specific output path. Source identity, exclusions and PDF-reader caveat. |
| `docs/publication/manifest.json` | Frozen complete chapter order, appendix declaration, asset/format inputs and truthful local-candidate metadata. |
| `docs/publication/format.yml` | V9-compatible shared HTML/Typst appearance and disabled computation. |
| `docs/site/_quarto.yml` | Ten-guide/16-manual/six-appendix navigation and render targets; retained old routes, downloads, Lua rebaser and disabled execution. Existing science/style preserved. |
| `docs/site/index.qmd` | Direct supported reader journeys/current manual links, full downloads and plain surface-construction limitation. |
| `docs/site/404.qmd` | Current manual/download recovery pointers; retained 404 route. |
| `docs/site/downloads.qmd` | Complete HTML/PDF volume links, contents/external-resource limits and approved reader-dependent PDF-link qualification. |
| `docs/technical-manual/overview.md` | Replace future assembly instruction with reader-facing complete-volume/source-owner explanation. No interface/scientific contract change. |
| `docs/technical-manual/indicator-extension.md` | Remove assembler/task-stage instructions from the reader page; retain complete-source ownership, order, evidence limits and source declaration. |

The coordinator's already-committed engine files are not part of this uncommitted writer delivery.
No tracked Python, Lua, tests, scientific pages, notebook cells, runtime/default/config YAML, locks,
shared task records or excluded guidance was edited by this writer.

## Artifact handoff and measurements

Final website: `C:/Users/taner/workspace/.worktrees/blueearth_cst/session-1/docs/site/_site/index.html`.
Downloads page: same root, `downloads.html`.
Four final complete volumes: same root, `manuals/{user-guide,technical-manual}.{html,pdf}`.
They are also staged under `docs/site/manuals/`. Keep both volumes of the selected format together.
The two PDFs contain all required local material without HTML companions; section-jump behavior across
PDF files remains viewer dependent as stated to the reader.

Evidence beneath session-1 `.tmp/tasks/t2610211349/p5/`:

- `site-build.log`, `site-link-proof.json`, `check-site.ps1`.
- `reused-source-hashes.json` and `reused-artifact-proof.json`.
- `format-links-proof.json`, `pdf-hashes-before-label.json`, `final-artifact-hashes.json`.
- `visual/*-page-*.png` (63 pages), `visual/*-contact-*.png` (eight sheets).
- Both preview URL records. Browser screenshots/observations remain in this conversation; no screenshot
  file is claimed when the browser tool only emitted it in the review surface.

Existing P3/P4 artifacts and canonical retained task returns remain intact. No cleanup/deletion or separate
progress system was introduced. Local STATUS records this lane's handoff only.

Final source/check checkpoint: **2026-10-26 22:12:33 UTC**.
Start-to-checkpoint wall interval: **42 min 38 s** from 21:29:55 UTC. This includes governing reads,
editorial work, engineering dependency waits, coordinator integration pauses and rendered inspection;
it is not active compute or build time. Final packet writing/handoff follows that checkpoint.
Input/output/cached tokens, cost and active compute remain **unknown**. Model/effort remains observed
**GPT-6.1-Sol medium** in the own-lane UI; no escalation or fallback. No incomplete governing read remains.

P5's supported publication promise is met by the inspected candidate, with the named minor title issue
and explicit external-resource/viewer/scientific limits. **Next owner action:** cst-main retains this return
and fixes the candidate for the already-authorized P6 fresh-reader review. Worker stops; no commits,
landing, push, deployment, model execution or new scientific writing is authorized/performed here.

Final delivery check/end UTC: **2026-10-26 22:14:29**; total observed wall interval **44 min 34 s**.
All55 unique source dispositions were compared with the retained inventory and matched exactly.
Both preview-stop terminal markers were observed. Final packet handoff follows this check.

Reusable guidance candidate (already raised in retained P3, not applied here): canonical
`brain-infrastructure/artifacts/skills/quarto/SKILL.md`, Verification. P3 and P5 both caught unwanted
alternate-format labels; P5 also caught a wrong volume target that a file-existence scan could not detect.
Add a proportionate check that each alternate-format menu has exactly the intended labels and that each
href targets that document's emitted format. This generalizes to books and partial-format publication.
Coordinator/owner: retain the existing proposal for a separately authorized skill update, or apply it there?
No shared guidance change or runtime adoption is claimed in P5.

## P6-01 bounded starter-comment repair

Coordinator commissioned this correction after independent P6 review. Candidate/unchanged HEAD:
`e18d7316fb8b47fd40fcddc086963f08ab63bf4e`, branch `docs/t2610211349-publication-assembly`, clean at entry.
Read retained main `p6-review.md` finding P6-01 and its recheck requirements. Existing P6-02 remains minor
and deferred; no additional scope was taken.

**Only tracked change:** five comment lines in
`config/templates/example-basin/project_config.yml`. No YAML value, runtime code, guide, generated
publication, PDF, shared record, dependency or test source changed. This append-only return evidence and
ignored copying-proof scratch are the only additional writes. No commit/landing or nested agent.

Exact comment diff:

```diff
-  # Years of record to extract, inclusive. At least 16. This is not the model
+  # Calendar years to extract, January 1 through December 31 inclusive. At least 16. This is not the model
-  # Select inclusive historical water years. Input: year mapping spanning at least 16 years.
+  # Select inclusive historical calendar years. Input: year mapping spanning at least 16 years.
-    # First historical water year. Input: integer year, <= end.
+    # First historical calendar year. Input: integer year, <= end.
-    # Last historical water year. Input: integer year, >= start.
+    # Last historical calendar year. Input: integer year, >= start.
-  # First month of the water year. Changes every annual statistic.
+  # First month of the water year for reporting aggregation; it does not change extraction bounds.
```

The neighboring model-run-period warning, `start: 2000`, `end: 2016` and commented optional
`water_year_start: Jan` remain unchanged. Wording distinguishes calendar extraction from reporting
aggregation without asserting that the setting changes every statistic.

Evidence owners inspected, without edits: `shared/wf3_science.py::historical_window_bounds` returns
January 1 / December 31; current TM configuration already describes calendar-year bounds and the
reporting-year month; `scripts/create_case.py::_prepare` reads the maintained starter and preserves its
comments while making the existing case-identity/header changes.

Checks through compatible main runtime via `session_runtime.py`:

- `yaml.safe_load(git show HEAD:<source>) == yaml.safe_load(current source)`: **pass**.
- Every noncomment line, including blank lines, compared before/after: **identical**.
- Existing `_annotate_config(current, _template_comments(source)) == current`: **pass**; no extra
  annotation or source help change is introduced.
- Called actual `_prepare` against an ignored empty scratch cases root: **11 file payloads prepared
  in memory**, no case files written. The entire corrected climate-window/water-year comment and value
  section is preserved after normalizing Windows carriage returns. Existing case headers/identity fields
  still change as designed; this is not a claim that the whole generated project file is byte-identical
  to the starter. Proof: `.tmp/tasks/t2610211349/p6-01-proof.json`.
- `git diff --check -- config/templates/example-basin/project_config.yml`: **pass**.
  Edited comments are within the 110-character line convention. Final Git status contains only the
  authorized YAML path.

The first raw section-copy assertion failed on existing Windows newline conversion; parsed YAML,
noncomment equality and annotation identity already passed. A bounded diagnostic isolated carriage
returns; the newline-normalized section comparison passed. No copying code, newline policy or runtime
behavior was changed to satisfy this check.

No model/notebook execution, installation, publication/artifact regeneration, full render, broad audit
or new permanent test was needed. Existing publication/PDF evidence is retained; the unchanged guides
already carry the corrected period advice. The same independent reviewer owns the P6 recheck.

Role/skills: continuing full manually applied canonical technical-writer, GPT-6.1-Sol / medium allocation
retained. Reused completed scientific-software-documentation (configuration help/source authority),
writing-feedback-revision (fidelity), testing-policy and execution-checks (bounded borrowed-runtime proof),
project-system (ignored evidence/handoff), and existing Python verification guidance. No newly triggered
skill body/reference was required; no governing read remains incomplete. Backend/tokens/cost unavailable.

Start UTC **2026-10-26 22:27:29**; final repair-check checkpoint **2026-10-26 22:29:42**;
observed interval **2 min 13 s**, excluding subsequent packet append/handoff. Source writes stopped.
Next: cst-main reviews/commits the single YAML-comment diff; the same independent s2 reviewer rechecks.
