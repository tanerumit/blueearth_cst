# Documentation streamlining execution plan

Date: 2026-10-26. Task: t2610211349. Status: V9 and P4A/P4B accepted and landed.

Current authority: owner approved V9 and instructed cst-main to integrate s2 and commission P4A/P4B.
P3 landed at `8963f661`. [P4 assignments](p4-content-assignments.md) fix disjoint s1/s2 ownership and
supersede earlier holds on those packets. P4C remains deferred; P5/P6 are subsequent, uncommissioned stages.
P4A/P4B landed at `1e0cbd71`; returns are retained in `p4a-user-guide-return.md` and
`p4b-technical-manual-return.md`. Source links and affected consumers pass. Full publication assembly,
offline inclusion and rendered-route verification remain P5; fresh reader review remains P6.
V9's direct wording, concrete filenames/examples and PDF alignment are the accepted editorial baseline.
Do not restore obsolete-interface or development-migration narratives from the historical map below.

Execution boundary: the owner's 2026-10-26 instruction commissions P1 in s1 and independent P2 in s2,
both at medium effort. cst-main retains all commit and integration authority. Return the reviewed
structure and owner decisions before P3 or migration; later-stage descriptions below remain proposals.
P1–P2 inspect current main and return evidence to the coordinator without editing lane source files.
Their detached lanes therefore require no implementation branch or landing operation.

Reviewed output: [boundary map and reconciliation](documentation-boundary-map.md), challenged by the
[independent critique](documentation-boundary-critique.md). Three major findings and one minor finding
were accepted and dispositioned. The map's final addendum owns the refined recommendations and explicit
deferrals; P3 is now commissioned, with P4–P6 held. The owner's decisions below settle source-link
compatibility, generated case instructions and the response-surface publication promise.

## Outcome

Owner decision, 2026-10-26: the user-guide, technical-manual and scientific-approach structure is
approved. Prioritize writing the user guide and technical manual; defer scientific-approach writing
(P4C). Preserve its outline and existing material for later work. P5/P6 acceptance for this tranche
covers the user guide and technical manual, without claiming a completed scientific-approach volume.
The owner subsequently selected 1A, 2A and 3A:

- Include bounded reconciliation of the scaffolder's generated `INSTRUCTIONS.md` with the central guide.
- Retain small tracked compatibility pages at moved source paths initially.
- Promise indicator-table interpretation, selection and extension in the first publication; defer
  supported response-surface construction pending axis-authority reconciliation and a checked example.

These decisions supersede broader future-stage descriptions below. The owner subsequently authorized
P3 in s2 at medium effort, returning the pilot for review before migration. P4–P6 remain held.
Version-identifiable documentation access remains an implementation detail
to make concrete in the bounded generated-instruction packet; no bundle or deployed URL is assumed.

Provide coherent quick-start, user-guide, technical-manual and scientific-approach collections from
canonical Markdown, while keeping necessary component instructions in their home directories.
Publish HTML and PDF from shared sources, with a clear treatment of interactive assets and notebooks.

Inputs:

- [Scoped inventory](documentation-inventory-2026-10-26.md): 55 files, five audience groups.
- [Landscape assessment](documentation-landscape-assessment-2026-10-26.md): findings and recommendations.
- [Execution observations](workflow-execution-log.md): timing, allocation, skills, checks and rework evidence.

The flat task note owns progress and the next action. This plan owns assignments and dependencies;
the observations log owns measurements, not a competing task status board.

## Scope and constraints

The user's exclusions remain: dev/tasks, dev/reference (requested as dev/references), dev/records,
docs/references, .github, CHANGELOG.md and LOG.md are outside the documentation review. Only the five
inventory groups are included. Task evidence is retained in this task folder despite its review exclusion.
Agent instructions, validation evidence, task coordination and legal documents are not review targets.

Read governing instructions as required without bringing them into the editorial revision scope.
Preserve scientific meaning, qualification limits, public behavior and executable contracts.
No model runs, scientific recalibration, dependency upgrades, deployment or push are implied by this plan.

Likely publication implementation surfaces, additional to the prose inventory, are
`dev/scripts/stage_site_guides.py`, `tests/test_site_guides.py`, `docs/site/_quarto.yml`, and docs-related
tasks in `pixi.toml`. Approving full implementation would include necessary changes to these consumers;
the present planning request does not authorize their modification. Excluded .github files remain untouched.
New Markdown destinations and exact ownership are resolved in P1, not assumed to be approved here.

Recommended execution agreement: first commission P1–P2, then review the concrete layout and scope before
commissioning P3–P6. This is a proposed decision point, not an extra skill-mandated approval gate.
The owner may authorize the full execution scope; routine stages then continue under settled decisions.
User-facing and human decisions remain with the owner. Parallel lanes and coordinator commit/landing
authority are selected; worker dispatch awaits the execution instruction.

## Roles and allocations

Use one continuing technical writer as editorial lead. The coordinator owns scope, acceptance, task records,
Git integration and measurement. Specialists own bounded work; they do not independently redefine the manual.

| Work | Registered role | Proposed model / effort |
|---|---|---|
| P1 boundaries and outline | technical_writer | gpt-6.1-sol / medium |
| P2 independent boundary critique | critical_thinker | gpt-6-astra / medium |
| P3 publication pilot | python_engineer | gpt-6.1-sol / medium |
| P4A user/local guidance | technical_writer | gpt-6.1-sol / medium |
| P4B technical reference | api_documenter | gpt-6.1-sol / medium |
| P4C scientific explanation — deferred | academic_writer | gpt-6-astra / medium |
| P5 assembly and integration | technical_writer + coordinator | gpt-6.1-sol / medium |
| P6 fresh reader review | technical_writer, fresh context | gpt-6.1-sol / medium |

Owner preference: medium effort is the default for every stage, including planning and independent review.
Use high only for an exceptional, specific problem that remains unresolved at medium after checking the
brief, evidence and tools, or for a clearly identified consequential reasoning problem. Record the reason,
bounded scope and result in the execution log; return to medium when that problem is resolved.
Scientific content or a reviewer role alone does not justify high. Do not use xhigh/max under this plan.
These are starting allocations, not measured performance rankings or guaranteed token savings.
Do not split off a mechanical worker merely to use a smaller model.

Fallbacks: GPT-6 Sol at the same effort for GPT-6.1 Sol, and GPT-6.1 Sol/medium for Astra, only after checking
availability, governing role pins and adequacy for the packet. If those checks fail, hold the affected packet.
Missing evidence or a broken tool should be resolved directly, not treated as a model-capacity problem.

The current native tool catalog lists these roles/models and effort settings. The execution runtime's
effective settings are not yet verified; recheck at launch. An older task record's model-availability result
does not establish present availability. Role-specific skills and model pins must be loaded before dispatch.

Allocation guidance consulted on 2026-10-26:
[OpenAI model selection](https://developers.openai.com/api/docs/guides/model-selection) and
[reasoning effort](https://developers.openai.com/api/docs/guides/reasoning).
Our stage allocations are judgments for this task; no cost, latency or quality advantage is yet measured.

## Work and handoffs

### P1 — Purpose, ownership and chapter map

Owner: technical writer. Predecessor: execution authorization and current inventory reconciliation.
Authority: inspect all 55 files; return task evidence only. No prose migration or source edits.

Deliver a proposed `documentation-boundary-map.md` with one row per inventoried file: reader question,
current role, proposed central/local owner, retain/split/shorten/incorporate/retire action, destination,
overlap evidence and migration/link consequences. Add chapter outlines for the four central collections.
Distinguish confirmed duplicate claims from useful context repeated for different readers.

Resolve or expose: quick-start placement; installation placement; technical-versus-scientific ownership;
local-source inclusion; notebook editable source; interactive/static assets; PDF composition and URLs.
Do not promise a self-contained sample dataset or fast model execution that the repository does not supply.

Acceptance: exactly 55 source dispositions, no excluded additions, no orphaned reader need, and one
authoritative home for every identified detailed contract. Coordinator checks coverage and decisions.
Handoff to P2: map, outlines, unresolved choices and evidence links.

### P2 — Independent challenge and settled boundaries

Owner: critical thinker, fresh context. Predecessor: P1 deliverable.
Authority: read-only review; return findings to coordinator for retention under this task.

Challenge ownership gaps, unnecessary fragmentation, duplication, offline completeness and migration risks.
Check three journeys: first example, own-basin assessment, and indicator interpretation/extension.
Return ranked findings with concrete counterexamples and suggested fixes, not a competing full design.
The editorial lead resolves findings in the same map; coordinator records dispositions and owner decisions.

Acceptance: all blocking boundary decisions resolved or explicitly deferred outside the first migration.
Handoff to P3/P4: versioned map and outlines, source ownership, decisions and unresolved out-of-scope items.

### P3 — Prove one publication path

Owner: Python engineer for publishing mechanics; technical writer supplies a frozen content specification.
Predecessor: settled P2 map and authorization for implementation surfaces.
Default: one writer at a time; writer prepares the pilot content before the engineer changes the build.

Use indicator selection as the proposed topic, subject to P1. Exercise canonical central Markdown plus a
local indicator README, links, an equation/citation where relevant, and a static/interactive figure fallback.
Generate an HTML sample and PDF sample from the same authoritative material. Inspect available PDF tooling
before choosing commands or proposing dependencies. Keep the existing publisher unless evidence rejects it.

The engineer owns publication code/configuration and targeted tests. The editorial lead owns prose and
navigation decisions. Resolve exact pilot paths in the packet to avoid shared writes.
Preserve existing published URLs where feasible; record source moves and redirects/link replacements.

Acceptance: both formats are visually usable; source content is unchanged by rendering; modifying a source
refreshes both outputs; missing inputs fail clearly; no simulation or data acquisition is launched.
Handoff: tested build recipe, supported Markdown features, asset policy, path mapping, checks and limitations.

### P4 — Revise content in three bounded packets

Predecessor: P2 ownership map and accepted P3 publishing contract.
Write targets below are collection ownership; exact file lists come from the settled map before dispatch.

- **P4A, technical writer:** quick start, user guide, installation, root/docs orientation, scripts index,
  configuration-local guidance and developer-template instructions. Keep local operational help local.
- **P4B, API documenter:** technical-manual chapters and indicator module/set interface material assigned
  by P1. Trace fields, units, inputs, outputs, failures and examples to executable owners.
- **P4C, academic writer:** scientific-approach chapters, citations, assumptions and interpretation.
  Separate implementation claims from evaluated behavior; flag evidence gaps rather than invent support.

An indicator README gets one writer only. If assigned to P4B, P4C returns proposed scientific corrections
as findings rather than editing it concurrently. Similarly, P4A owns global navigation and shared indexes.
Each packet returns changed paths, source-to-destination mapping, removed duplications, unresolved claims
and its checks. Specialist findings outside the 55-file scope are reported, not silently repaired.

Acceptance: content follows the agreed map; substantive claims have identified sources; cross-links replace
duplicated detailed explanations; examples agree with implementation; no new empirical adequacy claims.
Conditional specialists only: academic_researcher for a material literature gap, dataviz_designer for a
substantial figure redesign, model_validator for commissioned empirical claims. None is preauthorized here.

### P5 — Integrate and verify the complete publications

Owner: editorial lead and coordinator. Predecessors: all P4 packets accepted.
Complete navigation, links, local inclusions, terminology, migrations and generated-output handling.
Reconcile all 55 source dispositions with final artifacts; retired material must have a justified destination.
Coordinator alone integrates branches and updates task evidence. Engineer handles publication defects only
within a newly explicit repair packet; do not let multiple workers fix the same integration issue.

Acceptance: clean HTML/PDF builds, usable Markdown, complete required content, working links, readable
figures/equations and no accidentally published internal or excluded material. See checks below.
Handoff to P6: candidate commit, publications, map, known limitations and actual verification results.

### P6 — Fresh reader review and closeout

Owner: fresh technical writer, read-only; coordinator accepts the return and assigns bounded fixes.
Review the three P2 reader journeys against source and rendered artifacts. Do not run the hydrological
workflow merely to review instructions. Refer unresolved scientific judgments to the appropriate specialist.
Return defects with severity, affected reader/action, reproducible evidence and proposed resolution.

Acceptance: no unresolved defects that block a promised journey or materially misstate supported behavior.
Minor deferred improvements must be named. Recheck changed areas only after fixes; reuse valid evidence.
Record final accepted coverage, limitations, metrics and process-improvement proposals. Apply repository
commit/landing policy. Pushing, publishing and task closure follow existing authorization and retention rules.

## Scheduling and ownership

Owner-selected topology: coordinate from `cst-main` (the primary checkout on `main`) and execute work
through `session-1` and `session-2`, referred to as s1 and s2. The owner's 2026-10-26 follow-up reserves
session-3 for unrelated work: this task must not claim its worktree or pane. This selects the execution
layout; the subsequent owner decision authorizes P3 only beyond completed P1–P2.

| Location | Responsibility | Proposed stage assignments |
|---|---|---|
| cst-main / main | Coordinator, task evidence, acceptance, metrics and integration | All stage handoffs |
| s1 / session-1 | Editorial lead and documentation assembly | P1, P4A, P5 |
| s2 / session-2 | Critique, publishing, interface packets and fresh final review | P2, P3, P4B, P6 |

These are reusable execution slots, not permanent role identities. Reuse a worker only for related work;
role changes require a fresh agent context. In s2, P2 and P6 are independent fresh reviewers, separate from
the P4B author. In s2, finish each packet and release its worker ownership before changing roles.
Retain the medium-effort default and exceptional-high policy for every location.

Current-tranche dependencies: P1 → P2 → P3 → {P4A, P4B} → P5 → P6. P4C is deferred.
Early stages are sequential because they settle boundaries and publication behavior. After P3 acceptance,
parallel work across the lanes is owner-authorized when exact write ownership is disjoint and the shared
base is current. P4A in s1 may overlap P4B in s2. Do not dispatch P4C in this tranche.
Use at most two workers plus the coordinator; leave lanes idle when there is no independent ready packet.
Shared navigation, bibliography and style assets have one assigned owner; other workers submit suggestions.
Keep the task evidence and execution observations coordinator-owned in main throughout.

The Git snapshot on 2026-10-26 showed all three execution slots detached. A detached slot is not proof that
its pane is available or that its tree is clean. Recheck Git state, pane occupancy and task ownership before
claiming it. At execution, resolve `cst-main` and each lane to the actual checkout/workspace, then discover
live workspace and pane IDs. Never infer or persist an ID from a name or an earlier task.

The environment reports HERDR_ENV=1. Follow agent-routing and the Herdr skill at dispatch: use the designated
agents pane for each owning workspace, preserve user focus, and verify effective role/model/effort.
Do not infer pane availability from idle state or silently fall back to native subagents.
Claim implementation sessions through task-start before source edits; do not create branches by hand.
Allocate from current main so workers receive the latest plan and accepted predecessor work.

Each worker owns source changes in its assigned lane, its local STATUS.md and qualified return evidence.
Workers return uncommitted changes, changed paths, checks, limitations and measurement data to cst-main.
Workers do not commit, merge, land, push or mutate another lane. The coordinator reviews each lane's diff,
isolates task-owned changes, and performs the verified commit in that lane before merging/landing from main.
For read-only stages, return findings to the coordinator, who saves them in the canonical task folder.
Only cst-main accepts results, updates shared records, commits and integrates branches.
Serialize integrations.
Follow repository landing/parking rules; never move or replace another task's active agent or branch.
Publishing and pushing still require their existing authorization.

Consult the user for user-facing or human decisions: document structure and navigation, changed reader
promises or scientific interpretation, meaningful publication/compatibility tradeoffs, and unresolved scope.
Present concrete options and a recommendation before dependent edits. Proceed independently with routine
implementation and editorial mechanics inside settled decisions. Preserve independent work while awaiting
an answer; record the question, blocked dependency and waiting time in the execution observations.
An approved layout or approach remains settled across follow-ups; do not repeatedly seek the same decision.

### Coordinator handoff

The planning conversation is attached to session-1; this plan does not relocate that live conversation.
Begin execution in cst-main with the existing task note, this plan, the inventory, assessment and observations
log. Reconcile the latest main commit and live lane/pane state before dispatch. Once the owner starts the
agreed execution scope, assign P1 to s1 at medium effort and start prospective timing/usage collection.
Present the P1–P2 user-facing layout decisions to the owner before dependent migration work.
Do not create an additional coordinator or worker in an occupied pane merely to reproduce this topology.


## Common worker packet

Every dispatch receives: objective; predecessor artifact/commit; exact owned paths; read-only/write authority;
coordinator-only commit/merge authority; user-decision boundaries;
relevant decisions and exclusions; output contract; checks; return destination; and no nested delegation.
Workers are not alone in the codebase: preserve others' edits and report ownership conflicts before writing.
Use fresh context with a compact packet for explicit model/effort overrides; verify runtime behavior.

Include this skill-loading instruction in every packet:

> Before the first edit, read each applicable SKILL.md body completely. Use consecutive bounded reads when
> output is truncated; selecting headings or initial lines does not complete the read. For each applicable
> skill, identify its linked-reference load conditions and the task phases they govern. Before each governed
> action, including verification, read the references whose conditions apply and follow further triggered
> links. Keep unrelated references unloaded. Report any governing body or triggered reference left incomplete.

Expected skills: technical writing uses applicable role-bound documentation skills and repository guidance;
interface writing uses API-reference guidance; scientific writing uses its role-bound scientific skills;
Python/build changes use python-discipline and testing-policy. Load PDF tooling when creating/reviewing PDFs,
and plotting/diagram skills only if the actual asset work requires them. Check role contracts before dispatch,
including uncatalogued skill paths; this list is a forecast, not proof of skill loading.

## Acceptance and verification

Existing commands available as starting points:

```powershell
pixi run pytest tests/test_site_guides.py
pixi run pytest tests/test_notebook_outputs.py
pixi run docs-build
git diff --check
```

Use notebook checks only when notebook sources or their handling change. Select Python checks and affected
consumer tests under dev/reference/dev-validation.md. PDF build commands are unresolved until P3; do not
claim the existing HTML build establishes PDF support. No broad scientific suite is required for prose alone.

Material falsifiers to exercise during P3/P5:

- Source drift: a build changes a canonical source or a generated edit survives source regeneration.
- Incomplete publication: a required local-source section is absent from the offline manual.
- Unsafe execution: rendering invokes model/data-generation commands or requires a production project.
- Broken migration: an agreed preserved URL, anchor or internal link no longer resolves.
- Meaning drift: formulas, units, qualification limits or supported behavior differ across presentations.

Inspect rendered HTML and PDF, not just successful exit codes. Follow local-preview lifecycle and browser
availability rules for HTML; distinguish HTTP availability from an actual browser/interaction review.
Avoid rerunning models; new numerical claims need their own evidence and may require a separate assignment.

## Efficiency and effectiveness tracking

Use the linked observations log at dispatch, return and acceptance. Record roles, actual skills, model/effort,
attempts, timing, available usage and checks. Separate planning, execution, review, rework, integration and
measurement overhead. Keep missing quantities unknown; do not guess values or expose private transcripts.

After P2, P3 and P6, summarize whether allocations and handoffs helped, where work repeated, and what caused
failures. Compare only sufficiently similar packets; different scope and difficulty confound comparisons.
No extra duplicate agent run or model benchmark is authorized solely for measurement.
Propose reusable role/skill changes only from concrete evidence; do not edit shared guidance automatically.
