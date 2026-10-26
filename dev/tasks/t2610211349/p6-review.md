# P6 independent fresh-reader review

Task: t2610211349. Recipient: cst-main. Reviewer: fresh technical-writer context in session-2.

**Recommendation: hold acceptance for one bounded own-basin wording correction (P6-01, medium).**
No execution/navigation blocker was found in the three promised journeys. The remaining material issue
is contradictory period advice in the starter that those instructions tell readers to edit. P6-02 is
minor and can remain deferred. No repair was performed.

## Candidate and authority

- Fixed source: `C:/Users/taner/workspace/.worktrees/blueearth_cst/session-1`, clean at
  `e18d7316fb8b47fd40fcddc086963f08ab63bf4e`, confirmed at entry and final identity check.
- Runtime: session-2, `feat/t2610211349-publication-engine`. Its older documentation was not the review
  source. Existing lane STATUS was read for orientation only; no writer/engineer history was resumed.
- Full canonical role manually applied:
  `C:/Users/taner/workspace/brain-infrastructure/artifacts/agents/technical-writer.md`.
  Generic runtime; this does not claim registered-persona activation.
- Requested and owner-observed settings: GPT-6.1-Sol medium. Fresh own-pane footer inspection independently
  showed `GPT-6.1-Sol medium` during this review. Backend identity/effort are not independently observable.
- **PROCEDURAL source-read-only**, per explicit owner decision; no enforced isolation claim.
  Only this report and evidence beneath local `p6/` were written. No source, STATUS, shared task record,
  branch, index or commit changed. No nested agent, install, model/notebook execution, build, landing or push.

Main's current continuation/P6 plan, boundary map including its final reconciliation, and retained
`p5-return.md` / `p5-engine-return.md` were consulted. Current continuation and owner decisions supersede
their historical holds. New scientific writing and supported response-surface construction remain deferred.

## Findings

### P6-01 — Medium: starter calls calendar-year bounds water years

**Reader/action:** a practitioner follows Create your own case, opens the copied project YAML and chooses
historical coverage, particularly with a non-January `climate.water_year_start`.

**Reproduction and evidence, all relative to the fixed candidate:**

1. `docs/guide/configuration.md:10` directs readers to keep the commented parameter help beside their YAML.
   Its line 31 correctly calls `climate.window` inclusive calendar years.
2. `config/templates/example-basin/project_config.yml:87` instead says “Select inclusive historical water
   years”; lines 89 and 91 call the endpoints first/last historical water year. The adjacent line 94
   introduces the water-year month. The comments are copied into scaffolded cases.
3. `blueearth_cst/shared/wf3_science.py:84` defines `historical_window_bounds`; line 122 unconditionally
   returns January 1 of start through December 31 of end. Its documented 2000–2016 example states those
   exact calendar bounds. The function accepts no water-year month.
4. `docs/technical-manual/configuration.md:74` correctly distinguishes calendar-year extraction from
   `climate.water_year_start` reporting aggregation. The assembled technical-manual HTML was followed
   through its Configuration contract contents entry and independently displayed the same distinction.
   The assembled user guide also preserves the calendar-year instruction.

**Consequence:** the copying/editing route gives incompatible answers at the point of decision. A reader
using October water years could believe an endpoint denotes an October–September record while the parser
extracts January–December. Successful execution would not reveal the mistaken intended coverage. This is
a material interpretation error for that own-basin choice, although the shipped January example works.
The historical boundary map already identified this calendar disagreement; it remains in the candidate.

**Proposed resolution:** correct the three starter comments to “calendar years” / “calendar year,” and
clarify beside `water_year_start` that it controls reporting blocks rather than extraction bounds. Keep
all YAML values and computational behavior unchanged. This is a coordinator-assigned bounded repair:
the reviewer has no source-write authority. If template comments remain outside the repair scope, an
explicit point-of-edit warning in the own-case/configuration procedure must resolve the contradiction.

**Recheck:** inspect the corrected source and its copying path; verify no YAML values changed. Recheck
only affected rendered wording if a guide changes. Existing unchanged PDF/build evidence remains usable;
no model run or full publication audit is justified by comment-only correction.

### P6-02 — Minor: website appendix repeats its title

**Reader/action:** from Choose and recalculate indicators, follow Crop-water to the set-specific reference.

**Reproduction:** `docs/site/_site/technical-manual/appendices/indicator-crop-water.html` displays two
successive “Crop-water screening set” titles, one generated metadata title and one retained source H1.
I followed this actual link and inspected both the rendered text and screenshot. The formula/unit table
and preparation instructions remain readable and reachable. The complete technical-manual HTML shows
one appendix heading, and the retained PDF p.40 has one heading; volume reading is unaffected.

**Proposed resolution:** suppress only the website appendix title block while preserving its navigation
metadata and complete README body. Acceptable to defer as a cosmetic issue. Recheck one affected appendix
and its navigation after any metadata fix; preserve the canonical H1.

## Three reader journeys

| Journey | Independent walkthrough and source checks | Result |
|---|---|---|
| First example | Homepage → Install → Quick start → Reading the outputs. Inspected installation commands against Pixi tasks; rapid catalog/workflow settings, named experiment and retained-variable selection against actual seed files. Rendered commands use the owned runner and explain partial DAGs. Summary and indicator folder/table paths are concrete; dictionary, units, status and reference joins are discoverable. | No blocker found. P-drive/network/data access precedes execution; runtime estimate is qualified. Wiring tests, workflow completion, synthetic return-level qualification and basin adequacy remain distinct. No execution success was inferred from this review. |
| Own basin | Homepage route / guide navigation → Create your own case → configuration/input formats/running. Read scaffolder instruction producer, starter README/YAML and generated-instruction template. Checked external roots, copied versus scaffolded instructions, header-only observations, forcing selection and separate model/scenario periods. | Coherent staged route: WF0 forcing decision, WF1 and WF3 independent prerequisites, optional WF2 overlay, WF4 after ready products. Small grid/ensemble is explicitly not an assessment recommendation. P6-01 needs resolution at the copied YAML decision point. |
| Interpret/select/extend | Outputs → run/group/reference joins; indicator selection → Crop-water → extension guide → complete module contract. Complete UG HTML contents → outputs → default conventions in sibling TM HTML; TM contents → Configuration contract. Read canonical output/request/module/default/crop/flood contracts and selected executable field/identity owners. | Units come from dictionary; missing/undefined/unavailable remain distinct; missing response removes a calculation while missing parameters can yield unavailable rows. Reference IDs are preserved and monthly joins expand rows. Recalculation reuses completed compatible responses; absent variables require new simulation. Trusted registration and independent checks remain advanced TM/module material. |

The ten-chapter user guide is primarily action-oriented. Detailed registration, callable parameters,
identity traversal and independent checker contracts are in the technical manual's complete appendix.
Flood output remains discharge hazard with only 2-/10-year eligibility under shipped evidence; ERFA does
not claim ecological classification, and crop-water does not claim yield/damage adequacy. The promised
endpoint is table interpretation, selection and extension throughout the inspected entry routes.

## Actual artifacts, checks and evidence reuse

Artifact root: session-1 `docs/site/_site/`. Independently read landing `index.html`, `downloads.html`,
the journey chapters and both complete HTML volumes through connected Chrome/Umit. Followed actual local
links and contents entries, including the cross-volume default-conventions link. Download table points to
both HTML and PDF volumes. Each complete HTML volume shows one PDF alternate-format choice with its own
PDF filename; no Typst choice appeared. Reader-dependent sibling PDF jumps are visibly qualified on Downloads.

Fresh `p6/identity-proof.json` records candidate and SHA-256 for all four volumes. They exactly match P5:

| Artifact | SHA-256 |
|---|---|
| `manuals/user-guide.html` | `85DDEBEE526496056690A37F3AFFC67748624E6574BD6BB45C1B9B6FE1BA767B` |
| `manuals/user-guide.pdf` | `CC11F4AC57EC68D02D015C47796C1DF35E9B4BCC7DB3D0948512DC38ACAFF846` |
| `manuals/technical-manual.html` | `D1AEA734E9DEA2D5744DC113594E33041DA73E1C8E9F49827682DD282990CED9` |
| `manuals/technical-manual.pdf` | `745776C51725965CD1868AA47CAC18D1A6103A0C8F55B6CF1187B950A15A8BE0` |

Fresh comparison of all 63 P5 consumed-source hashes found zero mismatches. The volumes deliberately label
themselves a local source candidate based on 856bc47c, with hashes identifying consumed files; this is not
a claim that e18d7316 was the build's original source label or that unpushed repository links work online.

Reused attributable P5 evidence: full no-execute volume builds; 52-target website build; 55-source
disposition reconciliation; website local-link/old-anchor proof; 517 volume HTML links; 29 sibling PDF
destination names; complete all-63-page PDF visual proof; final format-menu repair. Reviewed the retained
repair's unchanged-body/PDF/source evidence before reuse. These are retained P5 checks, not fresh P6 runs.

Independent PDF visual samples used retained rasterizations tied to the unchanged PDF hashes:
UG contact sheets 1–2 (pp.1–18), TM contact sheet 5 (pp.37–42), full-size UG p.17 and TM p.40.
Commands, table joins, reference warning, units and crop formulas were legible with no observed clipping.
This is sampled independent inspection; P5 supplies the exhaustive all-page proof. No new rasterization,
PDF reader jump trial or exhaustive audit was performed.

Preview: verified w9:p7 at an interactive PowerShell prompt before use; no pane focus change. Task-local
`BRAIN_PREVIEW_STATE` under `p6/preview-state`; bounded server root was exactly session-1 `_site`.
URL recorded in `p6/preview-url.txt`. Own Chrome tab closed; same-root `local-preview --stop` sent through
the same watch pane. Final shutdown verification is recorded below. Initial restricted-token Herdr reads
failed with access denied; authorized normal-permission calls succeeded. No server or security setting
changed, no automatic approval rejection, and no browser denial/unavailable connection occurred.

Not checked: installations or command execution; current external catalogs/network/links; new numerical
results; scientific adequacy; formal accessibility, narrow/mobile layouts or all supported PDF readers.
No new HTTP probe is claimed separately from the actual browser navigation. Known sibling PDF URI named
destinations retain P5 verification; cross-reader section following remains dependent, with no GoToR fix.

## Role/skill loading and limits

Applied complete canonical skill bodies, resolving role bindings `_external` first:

- `scientific-software-documentation/SKILL.md`: site lifecycle, task guides, review/accessibility and
  README-authoring references completely read for the corresponding reader/sidecar review.
- `testing-policy/SKILL.md`: complete; `references/suite-cost.md` complete for evidence reuse. Repository
  `dev-validation.md` validation ladder and planning/reuse sections read in bounded continuations. Other
  execution/landing/CI sections were not governed actions; no suite or runtime was borrowed.
- `tutorial-authoring/SKILL.md` and `references/checklist.md`: complete; learning arc and output
  interpretation applied, clean-session execution explicitly unverified by commission.
- `project-system/SKILL.md` and `references/workflow.md`: complete; coordinator-retained review handoff,
  existing authorized scratch placement. No layout/migration/cleanup action was taken.
- `_external/pdf/SKILL.md`: complete; existing-artifact PDF inspection only. Advanced manipulation/forms
  references were not triggered.
- `_external/herdr/SKILL.md`: complete before control; installed CLI help, pane and agent group help read.
  HERDR_ENV=1 confirmed. No agent spawned/resumed, no layout/focus mutation.
- Bundled `computer-use/SKILL.md`: complete; browser-only CUA documentation read on initialization and
  browser selection. Native Windows-app guidance/API references were not triggered by browser-only work.
  Infrastructure machine-setup Local HTML previews section read before starting preview.

The initial aggregate read truncated; applicable bodies were recovered individually before the first
evidence edit. A README-specific reference was loaded later than the initial README inspection; the
relevant sidecar/extension reading was reconsidered under that reference before final judgment. This is
a loading-order deviation, not a claim of perfect preflight. No applicable skill body or triggered
reference remains incomplete. Repository documentation guidance was read; excluded maintainer references
were governing evidence, not editorial review targets. No citation audit, Quarto implementation, Python
example authoring, scientific writing, empirical validation or Git mutation was undertaken.

## Measurements and handoff

First recorded UTC: **2026-10-26 22:17:23**. Reader/source/artifact checks through **22:24:17**:
**6m 54s** observed wall interval, including instruction loading, inspection and tool latency.
Own footer observed at **22:23:57**. Final capture time follows below. No user-decision or agent wait was
initiated. Active compute, token/cached-token usage, cost, coordinator acceptance and total accepted lead
time are unknown; no estimates are substituted.

Allocation assessment: fresh reviewer separation enabled a point-of-edit contradiction to be found after
author assembly checks. P5 identities and retained proof avoided duplicate builds and exhaustive audits.
No causal model/effort or cost comparison is possible from these different packets. Repeated output
truncation required bounded recovery; avoid combining long records into one tool return.

No new shared skill change is proposed: existing skills already require source reconciliation and complete
loading. P5's separately retained alternate-format-menu proposal remains for owner disposition; this review
did not modify or independently validate shared-skill runtime adoption.

Next: cst-main retain this report, assign P6-01's bounded comment/wording repair and recheck that area.
P6-02 may stay an explicitly deferred minor. Acceptance should then use the unchanged retained proof and
affected recheck, without new model execution or a repeated whole-site audit.

Final verification UTC: **2026-10-26 22:26:19**; observed start-to-verification interval **8m 56s**.
Both source candidate and runtime tracked trees remained clean. Report ignore check again matched
`.gitignore:200:.tmp/`. Watch output explicitly confirmed `Preview stopped` and `P6_PREVIEW_STOPPED`;
the watch pane returned to its PowerShell prompt. Only the authorized report/evidence remains for retention.

## P6-01 independent correction recheck — accepted

**Decision: P6-01 resolved; P6 acceptance recommended for fixed candidate
`86085ea2dcd1eff2037dd5d40bf8e8d76f7972c2`.** This supersedes the initial hold above.
No unresolved blocker or material misstatement remains identified in the promised journeys.
P6-02 remains the explicitly deferred minor duplicate website appendix title.

Independently confirmed session-1 HEAD and clean status. The complete Git delta from the reviewed
`e18d7316fb8b47fd40fcddc086963f08ab63bf4e` touches only
`config/templates/example-basin/project_config.yml`, replacing exactly five comment lines. The comments
now state January 1 through December 31 calendar-year extraction, label both endpoints calendar years,
and distinguish `water_year_start` reporting aggregation from extraction bounds. This agrees with the
previously inspected parser and unchanged guide/manual. No guide, code, value or artifact change occurred.

Fresh independent verification, rather than reliance on writer Boolean results:

- Parsed old Git content and current YAML with `yaml.safe_load`: equal.
- Compared every noncomment line, preserving blank lines and normalizing text line endings: equal.
- Derived added/removed lines from the actual text delta: exactly five comment pairs, all comments.
- Inspected the actual `scripts/create_case.py::_prepare` path: reads the maintained starter bytes,
  applies existing case replacements, obtains help from that same starter and annotates the payload.
- Called that exact session-1 `_prepare` implementation with an authorized local scratch cases root.
  It prepared 11 payloads in memory. All five corrected comment lines survived in the prepared project
  YAML; parsed climate values matched the starter. No destination case or case files were written.
- `git diff --check e18d7316 86085ea2`: pass. Both session-1 and session-2 tracked trees remained clean.

Command: existing main environment's `python.exe -B .tmp/tasks/t2610211349/p6/recheck.py`, from session-2,
completed successfully (exit 0). Evidence: local `p6/recheck.py` and `p6/recheck-proof.json`; the JSON records
effective cwd, interpreter, exact candidate and loaded source path. No environment installation or model
execution. The writer's `p6-01-proof.json` and P5 return addendum were read as supporting evidence. Their
`candidate: e18d7316` identifies the pre-commit base, not the fixed committed HEAD; the independent proof
binds this acceptance to 86085ea2. Windows newline normalization explains the writer's initial raw-copy
failure; fresh normalized comparison passed without changing source or copying behavior.

Reused all unaffected P5/P6 publication evidence. The complete delta establishes that guides, assembled
HTML/PDF, build configuration and code are unchanged; no browser, build, full audit or model rerun needed.
Procedural source-read-only remains in force. Writes were confined to this append and local `p6/` evidence;
all paths remain ignored by `.gitignore:200:.tmp/`. No STATUS/shared-record write, commit, branch change,
nested agent, landing or push. Coordinator retains the report and owns final acceptance/integration.

Same manually applied full technical-writer role and medium allocation retained. Existing completed
documentation, tutorial, testing, lifecycle and Herdr guidance reused. Before the fresh Python evidence
check, completely loaded canonical `python-discipline/SKILL.md` and its style-and-docs, hazards and
python-validation references, plus testing-policy `execution-checks.md` for the borrowed interpreter.
No applicable governing read remains incomplete. No shared skill change is warranted by this correction.

UTC start **2026-10-26 22:31:08**; final verification **22:32:08**: **1m 00s** observed wall interval.
Report capture and notification follow that checkpoint. Requested/previously observed setting remains
GPT-6.1-Sol medium; no setting change. Fresh backend introspection, token usage, cost, active compute and
coordinator acceptance time remain unknown. Stop after notification; no further work commissioned.
