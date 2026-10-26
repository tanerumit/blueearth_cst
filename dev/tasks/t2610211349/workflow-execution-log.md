# Documentation workflow execution observations

Task: t2610211349. Created: 2026-10-26.
Contract: [execution plan](documentation-execution-plan.md).

This log records efficiency and effectiveness evidence. The flat task note remains the progress authority.
P1–P2 execution started on 2026-10-26. Earlier inventory and assessment work is historical context,
not a measured execution baseline. Unknown values are not zero.

## Collection protocol

The coordinator appends one record per independently handed-off packet attempt. Continue the same packet
for repairs; identify retries separately from related continuation calls and new assignments.
Record input/candidate commit or artifact revision so results remain attributable after changes.

Capture UTC dispatch, return and acceptance timestamps. Record explicit wait intervals when observable.
Report elapsed turnaround and accepted-deliverable lead time; label elapsed time after recorded waits as
an approximation, not model compute time. Unobserved wait time means active duration remains unknown.
For parallel work, report both end-to-end wall time and summed worker elapsed time without adding them.

Record runtime-reported input, output and cached tokens separately when available. Keep root/planning usage
separate and avoid double-counting parent aggregates with child totals. Cost stays unknown unless actual
usage, model/rate basis and cache treatment are available. Do not infer cash cost from subscription usage.

Roles and models are recorded as requested versus observed. A launch label is not proof of activation.
Skill use has three evidence levels: requested, worker-reported loaded/applied, and independently verified.
Record exact skill names/paths and the relevant action; do not equate every suggested skill with actual use.

Update at meaningful handoffs, not every tool call. Keep full transcripts and sensitive machine details out
of this record. Separate time spent on measurement where observable; avoid a custom telemetry service.

## Packet record template

Copy this section for a real attempt; do not prefill planned attempts as executed.

- Packet / attempt / predecessor:
- Objective and owned paths:
- Input revision / returned candidate / accepted revision:
- Worker identity; new dispatch or continuation:
- Requested role / model / effort (medium default):
- Exceptional high effort: specific reason, bounded scope, outcome and return to medium, or not used:
- Observed role / model / effort; evidence or unknown:
- Coordinator: cst-main; assigned execution lane s1/s2 (s3 excluded by owner):
- Context mode and isolation/worktree; runtime identity verified:
- Skills requested:
- Skills actually used; evidence level and actions:
- Incomplete governing reads, capability gaps or degraded execution:
- Dispatch / return / acceptance UTC:
- Explicit waiting intervals and reason; user-facing decision and dependent packet:
- Turnaround / acceptance lead time / active elapsed estimate or unknown:
- Usage source; input / output / cached tokens; cost or unknown:
- Deliverable and coverage denominator:
- Checks run / passed / failed / not run; evidence paths:
- First-return disposition: accepted, repairs needed, blocked, or cancelled:
- Reviewer findings by severity; materiality defined below:
- Repair effort / retries / continuation count; attributable cause:
- Handoff gaps, repeated investigation or scope changes:
- Coordinator commit/landing evidence; worker changes accepted or returned:
- Accepted outcome, remaining limitations and next handoff:
- Allocation/skill lesson; evidence and proposed adjustment:

## Effectiveness measures

- **Coverage:** dispositions accepted out of 55 original files; new chapters are tracked separately.
- **First-return acceptance:** accepted without substantive repair / packets with completed review.
  Exclude blocked and cancelled packets from that denominator, but report their counts separately.
- **Defects:** blockers prevent a promised journey, corrupt meaning or break publication; major defects
  materially mislead or obstruct readers; minor defects are local presentation/editorial issues.
- **Rework:** time/tokens where observable, repair attempts, and cause: missing context, bad allocation,
  unclear boundary, technical failure, evidence gap, or changed owner requirement.
- **Handoff quality:** missing prerequisites, ownership collisions and repeated investigation needed by
  the next worker. Do not classify normal verification or justified challenge as wasted duplication.
- **Reader outcomes:** three agreed journeys checked; HTML/PDF/Markdown completeness and usability.
- **Source consistency:** one authoring home per topic, unchanged sources after build, and working links.

Word counts, number of files edited and number of skills loaded are not quality measures.
A rendering pass alone does not establish scientific accuracy or usability.

## Efficiency summaries

At P2, P3 and P6 report accepted packets, worker count, retries, measured elapsed time, available usage,
review/rework burden and measurement overhead. Keep observations separate from interpretations.
No baseline exists yet, so comparative savings and model superiority are undetermined.
Small samples and different packet difficulty prevent causal claims about role/model effectiveness.
Use observations to improve later allocations, not to construct unsupported rankings.

## Planning observation — 2026-10-26

- Work: prepared the execution plan and this log; incorporated the owner's tracking request.
- Executor: root coordinator inline. New worker dispatches: 0.
- Effective model/effort: unknown in the available execution evidence; no override was requested.
- Guidance used: agent-routing (allocation and handoff), task-brief (phase contracts), OpenAI Docs
  (official model guidance), project-system (retention), and existing Git/task-maintenance guidance.
  workflow-driver was consulted for scope; a declared run was not started.
- Verification: local file links and prose wrapping passed; Git whitespace checks passed.
  Stage acceptance/build checks remain planned, not executed. One long line was corrected before saving.
- Start time, active duration, token usage and cost: unknown; not reconstructed retrospectively.
- Process observation: user requested measurement before dispatch, allowing prospective capture.
- Baseline limitation: earlier uninstrumented inventory/review turns are not a valid efficiency comparison.

## Coordinator preflight — 2026-10-26

- Authorized scope: P1–P2 only; owner decision before publishing pilot or migration.
- Coordination-plan commit: `58efe411` on main; reviewed all three pending task-owned diffs;
  `git diff --check` passed. No software behavior changed; no software/build gate was warranted.
- Herdr discovery required an approved outside-sandbox read because the sandbox client could not
  access the server. No server restart, pane creation or focus change occurred.
- Live ownership: cst-main workspace w7; s1 w8, agents pane w8:p1; s2 w9, agents pane w9:p1.
  Git trees were clean/detached; preflight-only conversations confirmed no earlier user task.
- Fresh context IDs: s1 `01a17846-bf43-7420-aea9-623ae9f3b811`;
  s2 `01a17846-e4ca-7f32-8cc5-9af9c099eeec`. Shared-server discovery confirmed their cwd.
- UI verified GPT-6.1-Sol/medium for s1 and GPT-6-Astra/medium for s2. Roles are instructed through
  full canonical contracts in generic interactive runtimes, not native role activation.
- No implementation branches claimed: workers read current main and return task evidence only.
  `todoboard.py worktrees` reports the three detached slots as untracked and two pre-existing missing
  branches (`feat/model-upgrading`, `feat/scope-shipped-sample-dataset`); none is a P1–P2 branch.
- Coordinator guidance applied: agent-routing (ownership/allocation), Herdr (visible dispatch),
  workflow-driver (stage/isolation gates), git-workflow (scoped commit), project-system (continuity),
  testing-policy (prose-only inspection), todo-board (task-note maintenance).
- Root token usage, compute time, cost and measurement overhead: unknown; no retrospective estimates.
- Task-note check: `pixi run python dev/scripts/todoboard.py check` reported eight pre-existing errors
  elsewhere (missing overview fields and invalid/orphan task folders), plus length warnings including
  this existing long note. These do not originate in P1–P2. Board rendering passed outside the sandbox
  after its common-Git lock was inaccessible inside; generated `dev/TODO.md` remained unchanged.
- Owner permission-boundary wait ended by 2026-10-26 13:02:37 UTC. P1 continued during that wait;
  exact waiting duration and measurement overhead were not captured separately.

## P1 / attempt 1 — boundary map and outlines

- Input revision: main `58efe411`; predecessor: owner execution authorization and retained inventory.
- Worker: `technical-writer-p1`, s1/w8:p1; fresh assignment after preflight, no nested delegation.
- Requested/observed allocation: GPT-6.1-Sol/medium, confirmed in UI before dispatch; high not used.
- Role requested: technical-writer; full canonical role instructed, worker confirmation pending.
- Authority: inspect current main; return proposal in conversation. No source/task-record edits,
  commits, branches, builds, migration or model runs by worker. cst-main retains the returned artifact.
- Skills requested: applicable technical-writer bindings and complete skill/reference reads;
  actual loading/application remains pending worker report.
- Dispatch accepted by runtime: 2026-10-26 13:00:09 UTC (local task-start event).
  Final return: 13:24:54 UTC; coordinator structural acceptance for P2: 13:25:11 UTC.
  Turnaround: 24m 45s; acceptance lead time: 25m 02s. Active compute duration remains unknown.
- Acceptance denominator: exactly 55 unique inventoried source dispositions plus four chapter outlines.
- Runtime usage recovered from the worker's local Codex rollout after completion, taking only the last
  `turn_token_usage` record per turn (not summing cumulative records):
  initial P1 turn 2,478,256 input / 2,324,480 cached input / 3,695 output tokens;
  resumed/capture turn 4,683,160 input / 4,631,296 cached input / 27,593 output tokens.
  P1 total: 7,161,416 input / 6,955,776 cached input / 31,288 output tokens.
  Cached input is a subset of input. Preflight is separate: 50,746 input / 32,384 cached / 241 output.
  Cost unknown; no rate/subscription conversion. Root usage is not included in these worker totals.
  Runtime turn-context records independently confirm GPT-6.1-Sol/medium for both substantive turns.
- At 2026-10-26 13:05:49 UTC the coordinator observed a terminal capacity error from GPT-6.1-Sol
  after source inspection, before a deliverable. No source edits occurred. The plan-authorized
  GPT-6-Sol/medium fallback was attempted in the same context; no replacement worker was started.
  The model-command text resumed work, but the UI still showed GPT-6.1-Sol/medium. Therefore the fallback
  is not established as effective; record the resumed allocation as GPT-6.1-Sol/medium, not the worker's
  acknowledgement of the requested model. One continuation followed the interrupted attempt.
  This is not an accepted first return or a reasoning failure.
- A coordinator scope checkpoint stopped expansion into an implementation/content-accuracy audit once
  the worker reported all 55 source inspections complete. Remaining accuracy questions are deferred.
- Large-return capture required the Herdr fallback: worker was asked to save the full response to
  s1 `.tmp/tasks/t2610211349/p1-boundary-map.md`. This narrow scratch write is authorized; shared
  task records and source files remain coordinator-only. The transcript reader did not expose a full
  final response, and an idle pane alone was not accepted as proof of a completed deliverable.
- Capture preflight at 13:15:19 UTC reached file verification at 13:24:34 UTC: 9m 15s wall time.
  Capture delay is handoff overhead, not proven model compute time. The final runtime completion event
  at 13:24:54 establishes the turn finished; the earlier idle detection did not.
- Retained first return: `documentation-boundary-map.md`, SHA-256
  `F2B4EA3164958156EADFD90F1D92AFF03543E0D12A17173DA9BCEC98E78F8739`.
  Source/saved hashes match. Coordinator checked all 55 unique paths against inventory: no differences;
  inspected all disposition groups, four outlines, proposed choices and evidence limits.
- First complete artifact accepted for P2 without substantive repair, not approved for implementation.
  One capacity interruption/continuation, one scope steering message, one return-capture follow-up;
  no replacement agent. Scope steering and capture were delivered within the resumed turn.
- Worker reports full canonical role plus scientific-software-documentation, project-reference-docs,
  project-system, testing-policy and tutorial-authoring applied; exact paths/references and actions are
  retained in the map. Skill loading is worker-reported, with transcript read activity observed; not an
  independent audit of every loaded reference. No incomplete governing reads reported.
- Checks: worker 55-file tracked coverage and source-based journeys; 196 relative-link occurrences
  resolved after accounting for generated guides. Coordinator independently matched inventory and hash.
  No rendering, execution, empirical accuracy or external citation validation claimed.
- P2 prerequisite: accepted P1 artifact. Separately, owner input requested on the s2 permission boundary:
  switch to Read Only or explicitly allow review under current permissions. Owner explicitly authorized
  current permissions before P2; retain read-only instructions and before/after Git checks, but do not
  claim enforced read-only isolation. No permission setting changed. P2 subsequently started below.

## P2 / attempt 1 — independent boundary critique

- Input: frozen P1 map hash above; main base `58efe411` plus coordinator-owned retained evidence.
- Worker: `critical-thinker-p2`, s2/w9:p1; fresh review context after preflight only.
- Requested/observed UI allocation: GPT-6-Astra/medium; high not used. Full canonical critical-thinker
  role instructed through generic runtime; actual role/skill application pending return.
- Runtime dispatch UTC: 2026-10-26 13:25:53; final return 13:30:40; coordinator accepted critique
  for editorial reconciliation at 13:31:50. Turnaround 4m 47s; acceptance lead time 5m 57s.
- Authority: read-only task under current permissions, explicitly authorized by owner. No permission
  change or enforced-read-only claim. Before-review s2 tree clean/detached; source checks repeated on return.
- Deliverable: ranked critique of ownership, fragmentation, offline completeness, migration and the
  three reader journeys; no competing full design or accuracy audit.
- P2 readiness wait: preflight finished before P1; no critique started until the accepted artifact existed.
  The owner permission decision resolved while P1 was running and did not delay the dependent dispatch.
- First return accepted without reviewer repair: three major findings (one conditional blocker for a
  broader response-surface promise) and one minor clarification. No unconditional structural blocker.
  Full critique retained in `documentation-boundary-critique.md` from the completed response.
- Findings: generated `INSTRUCTIONS.md` consumer missing; old source-path compatibility unresolved;
  offline response-surface endpoint ambiguous; set-specific crop-water preparation needs one owner.
- Worker-reported loaded/applied: full canonical critical-thinker role, design-exploration,
  scientific-software-documentation (four triggered references), testing-policy. No incomplete reads.
  Exact role/skill identities and actions retained in the critique. Runtime independently confirms
  GPT-6-Astra/medium. No model fallback, retry, replacement, or permission change.
- Local rollout final per-turn usage: 833,543 input / 768,640 cached input / 5,037 output tokens.
  Separate preflight: 334,907 input / 307,072 cached / 743 output. Cached input is included in input;
  cost unknown. Root usage and P1 usage are not counted here.
- Reviewer verified input hash before/after and targeted three journeys. Coordinator checked terminal
  task-complete event and clean detached s2 status. No source edits, build, execution or numerical claims.
- Retained P1 commit: `6570242c` on main. The reviewer read the same frozen artifact while cst-main
  committed its evidence; the source-content base remained `58efe411` and the map hash did not change.

## P2 editorial reconciliation — P1 worker continuation

- Dispatched 2026-10-26 13:32:15 UTC to the continuing technical writer in s1, medium effort.
  Same role and context; no new agent. Input: retained P2 critique and fixed P1 map.
- Requested a compact addendum resolving all four findings in the same map, with owner decisions
  exposed and external consumer dispositions separate from the 55-source register. No new audit.
- Used the existing thread's background continuation to preserve text visibly drafted in the worker
  pane. Worker remains visible in Herdr; no replacement/native subagent or new workspace was created.
- Final runtime return: 13:33:34 UTC; coordinator acceptance: 13:34:22 UTC. Turnaround 1m 19s;
  acceptance lead time 2m 07s. All four findings accepted and dispositioned in the same map addendum.
- Runtime independently confirms GPT-6.1-Sol/medium. Final per-turn usage: 758,368 input /
  755,456 cached input / 1,720 output tokens. Cost and active compute time unknown.
- Reused the P1 role and five reported skills; no additional investigation or incomplete reads reported.
  Clean detached s1/s2 trees reconfirmed. The coordinator appended the returned text; no source edits.
- P3 and migration remain held. Three user-facing choices remain explicit; the minor crop-water
  ownership clarification is resolved editorially. No second critic is required by this bounded plan.

## P2 checkpoint summary — 2026-10-26

- Completed stages: P1 and P2; two unique workers, one editorial reconciliation continuation.
  Both complete substantive first returns were accepted; P1 needed a capacity recovery and capture
  follow-up before its artifact was complete. This is 2/2 complete returns, not uninterrupted success.
- Coverage: 55/55 source dispositions, four collection outlines, three source-based reader journeys.
  Findings: three major (one conditional blocker for a broader promise), one minor; all dispositioned.
  The owner choices are deferred before dependent work, not silently approved.
- End-to-end: first P1 runtime start 13:00:09 to final reconciliation return 13:33:34 = 33m 25s;
  to coordinator acceptance 13:34:22 = 34m 13s. Summed packet turnaround is 30m 51s
  (24m 45s + 4m 47s + 1m 19s); it is not added to end-to-end wall time or called compute time.
- Attributable substantive worker totals, excluding both preflights and root coordination:
  8,753,327 input / 8,479,872 cached input / 38,045 output tokens. Cached input is included in input.
  Source: final per-turn usage records from the two named local Codex rollouts. No transcript retained.
  No cash-cost estimate, comparative savings or model ranking is warranted.
- Measured capture overhead was 9m 15s. The broad role/skill/source context and repeated output capture
  consumed substantial input; this is an observation, not proof that any particular skill was wasteful.
  Root usage and measurement-only overhead remain unseparated/unknown.
- Commit authority remained cst-main: plan `58efe411`, accepted P1 evidence `6570242c`, final reviewed
  structure committed separately after checks. No worker commit, merge, landing, push or publishing.
- Verification limits: no scientific accuracy audit, rendered/offline usability test, execution or PDF
  build. Board-wide baseline errors remain unrelated; affected links, inventory and whitespace checked.
- Final coordinator checks: exact inventory comparison 55/55 unique with no omissions/additions;
  18 local file links resolved; `git diff --check` passed after removing four Markdown hard-break
  trailing-space pairs in the returned addendum. Reflowed returned prose without changing dispositions.
  Board check still reports the same eight unrelated errors; this task has only its existing length
  warning. Board CLI marked the task blocked for owner decisions and regenerated the view; its other
  row changes are column-width formatting, not task-state changes.
- Reusable proposal for owner consideration: Herdr currently forbids requesting file output in the
  initial prompt. Permit an explicit exception for an already-authorized durable structured artifact,
  with exact owned output path and coordinator retention. Evidence: the 55-row return required a second
  capture request and 9m 15s to save. This could reduce repeat generation in large maps/reviews; no shared
  skill change or fresh-session adoption is claimed here.

## Owner follow-up — 2026-10-26

The owner approved applying the artifact-first improvement separately. Herdr resolves to a vendored
upstream body; implemented a narrow override in owned agent-routing guidance. Infrastructure commit
`ad78554` was integrated by its primary owner as `7166fd6`; the worker lane is detached again.
The exception requires an authorized durable deliverable, exact output path, write authority,
artifact ownership and retention destination. Acceptance requires a completed return and inspection.
Vendored Herdr was unchanged. Whitespace and agent-routing conformance checks passed; four static
routing cases were added. Infrastructure health still reports unrelated dashboard/assessment issues.
Fresh-session behavioral adoption remains unverified. No push was requested or performed by this task.
The owner also reserved CST session-3 for unrelated work. Remaining proposed packets use only cst-main,
s1 and s2; P3/P4B/P4C/P6 share s2 sequentially, with fresh contexts at role changes. No s3 pane or worktree
was claimed, stopped, cleared or modified by this task. P3/migration decisions remain pending.

## Owner structure and scope decisions — 2026-10-26

The owner approved the three central document structures, prioritizing the user guide and technical
manual and deferring scientific-approach writing (P4C). Then selected 1A, 2A, 3A: include bounded
generated-case instruction reconciliation; retain small tracked compatibility pages at moved source
paths initially; promise table-level indicator interpretation, selection and extension, with supported
surface construction deferred. Updated the map, plan and task progress to reflect these decisions.
P3 authorization remains pending; no pilot, writing worker or migration was started. Only main, s1
and s2 remain allocated to this task. Future decisions should use numbered choices in the console,
because the interactive-question tool did not produce selectable controls for the owner.

## P3 dispatch — 2026-10-26

Owner chose A: start the pilot in s2 at medium effort, return for review before migration.
Reused s1 technical-writer context for the frozen content specification only; completed return read
through the thread API after terminal capture exposed only its first portion. Source check interval
14:18:27–14:20:15 UTC; full return retained in `publishing-pilot-content-specification.md`.
This continuation added task-brief and its triggered reference; other skills remain as reported there.

Live discovery found s2 clean/detached with this task's completed P2 critic in w9:p1. The critic was
idle with a completed substantive return; exited its UI and verified shell before replacement.
Claimed s2 from local main `470fc761` with the advisory task-start helper, no reseed (docs-only scope).
Branch: `feat/t2610211349-publishing-pilot`. No s3 control or writes.

Fresh engineer: `python-engineer-p3`, Herdr w9:p1, thread `01a17894-57b3-7131-ad6c-78e54fed6043`.
Freshness/cwd preflight completed; shared-server discovery confirms the new thread and s2 cwd.
Initial preflight ran at default low effort (52.167 seconds); before implementation the model picker
was set to GPT-6.1-Sol medium for this session only and the UI confirmed it. Backend settings unknown.
Role: python-engineer implement mode, manually instructed full-contract generic runtime; loading is
not yet verified. Full packet: `publishing-pilot-assignment.md`; initial substantive activity observed.
Coordinator owns commits, integration, shared records and acceptance. Worker returns lane-local evidence.
P3 acceptance covers HTML/PDF visual quality, shared-source integrity/refresh, clear missing-input
failure, source/rendered compatibility and complete static fallback. No P4 writing or migration.
Worker usage, total turnaround and final verification remain pending until completion.

## P3 coordinator acceptance — 2026-10-26

Engineer completed substantive turn `01a17897-3b0c-74b0-9042-6c26c3792175` without an error and is idle.
The full return is retained in `publishing-pilot-return.md`; transfer SHA256 matched the lane original
(`06d70bf1ed35cd2b57e0121fed5de3927497c4e97e0c484e5c2c9e522fe914ce`). Delivery HTML/PDF hashes matched
the return. Inspected implementation, tests, both HTML screenshots and all three PDF pages. Reused
attributable 14-test/Ruff/compile/build/refresh/link/source-integrity evidence; staged whitespace passes.
All P3 acceptance claims pass, with full-manual, citation/equation and portability limits as recorded.

Coordinator committed seven new pilot files in s2 as `bed0ae1e`; no preexisting source was changed.
The branch is clean and retained for owner pilot review. No landing, push, deployment, migration or P4.
Production publication configuration is unchanged. Preview stopped; artifacts/evidence stay in s2.
Board check retains eight unrelated baseline errors; this task has a length warning only. Worktree
mapping identifies the pilot correctly; detached s1 and two older missing branches are unrelated.

P3 used one continuing technical writer for its frozen specification and one fresh engineer. Engineer
substantive turn ran 14:22:19 to 14:46:25 UTC, approximately 24m 06s, including renders and review fixes.
UI settings remained GPT-6.1-Sol medium. Full manual role/skill application is confirmed by the worker
return; no native-role activation is claimed. Coordinator additionally applied python-discipline,
testing-policy and PDF visual-review guidance to acceptance.

Local rollout counters, excluding the preflight: 9,128,234 input / 8,928,384 cached input / 35,926 output
tokens. Cached input is included in input; output includes reasoning. Source is this engineer's final
token-count event minus its completed preflight event. Root and s1 follow-up usage are unseparated here;
active compute, process-wait totals and cash cost are unknown. No comparative efficiency claim.

Rework included one real broken alternate-format link, Windows Sass process permissions, local preview
state placement, annex pagination, cache confinement, portable recipe and the user-facing PDF label.
The last label-only HTML rerender reused unchanged PDF checks; no broad suite was added.
Owner review is the next gate. The worker proposed a separate Quarto skill check for alternate-format
links; current skill verification does not name that case. No shared skill edit is authorized or applied.

## P3 editorial revision — 2026-10-26

Owner found content mostly acceptable but requested simpler user-centric wording, with numbered steps
or bullets, especially Configuration and Default indicators. This commissions a bounded P3 revision,
not migration or scientific-approach writing. Primary audience clarified in conversation: a practitioner
selecting indicators from completed simulations and interpreting their tables; author details are secondary.

Rechecked live lane/pane ownership: s1 still holds technical-writer-p1 (w8:p1), s2 still holds
python-engineer-p3 (w9:p1), clean at `bed0ae1e`. No s3 control/writes. Continued both workers sequentially
at UI-observed GPT-6.1-Sol medium. No fresh agents or nested delegation.

Writer turn `01a178b4-f0dd-7e81-93b9-1fc8c531a5ff` completed in 241.120 seconds. New applicable skills:
writing-feedback-revision with revision reference, and Quarto; other completed reads reused. Full loading
and semantic checklist are recorded in `publishing-pilot-editorial-draft.md`. Coordinator reviewed five
replacement blocks, requested a more accurate summary label and shorter return-level sentences, then
retained the completed draft with matching transfer hash
`345b9370af0b0dd6cef108d35fd9aa5121fec222ae120beb0fcfff7076a0da65`.

Engineer continuation applies the approved draft to four canonical sources, plus necessary selectors
and wording-sensitive checks, under `publishing-pilot-editorial-revision.md`. Rendered-output and source
integrity checks cover revised prose; unchanged interaction/failure evidence may be reused. No new prose
copy, runtime behavior, model execution, source relocation or scaffold change is authorized.
Engineer duration/usage and final acceptance remain pending.

Owner further clarified the audience boundary: named implementation files belong to advanced material,
not the user-facing pilot. Writer revised E to retain unique details under an excluded advanced heading,
with a brief script-ownership statement and link to the existing module authoring contract for readers.
Coordinator reviewed the replacement and retained matching SHA256
`8740f5b4c8a0cfd4ca25348c52dbdf4f96a8603a7e16944cf026624a89ae4a71`.
This supersedes the earlier draft hash and full-default-README inclusion. Engineer held E while applying
A–D, then received the reviewed revision. No new manual page or duplicate prose home is commissioned.

Writer follow-up turn `01a178be-00db-7c22-803d-92230f5970b0` reports 7,963.470 seconds elapsed;
this is wall-clock turnaround, not active compute. Its retained artifact records final verification at
17:17:06 UTC. Role/skills were reused, no new reads were triggered, and s1 remained clean/detached.

### Editorial acceptance

Engineer turn `01a178b9-22fa-7c43-ad89-2e144390ddef` completed and is idle. Reported wall-clock duration:
8,780.361 seconds, including an uninstrumented gap and the E hold; active compute and cash cost are unknown.
Role remains python-engineer implement mode, full manual application, requested/UI medium. Newly applied
writing-feedback-revision and its revision reference; other completed guidance reused. Detailed skill and
timing evidence is retained in `publishing-pilot-editorial-return.md`, transfer SHA256
`d2d1603eff4c4585c04adbacaf41924ae4c619cb59b088adc6fee3eca98e21cf`.

Coordinator reviewed all eight changed files, all four PDF pages and the revised HTML conventions view.
Reused 14 passing affected tests, scoped Ruff/compile checks, exact five-block replacement comparison,
10-input render integrity, 41 rendered content checks and affected navigation/link evidence. Staged
whitespace check passed. External online availability is not claimed; the advanced target resolves in
the pinned repository content. The separate annex retains extra whitespace on PDF page 3.

Committed in s2 as `bbf5fec6`; branch is clean and retained for owner review, without landing or pushing.
Current artifacts are under s2 `.tmp/tasks/t2610211349/p3/editorial/build/`; the earlier pilot is separate.
Owner reviews wording and audience separation next. Migration and scientific-approach writing remain held.
No s3 activity occurred. Unrelated primary task-board additions are preserved.

## P3 plain-language follow-up — 2026-10-26

Owner requested direct option wording (select simulations, indicators, or both) instead of list-schema
language, and removal of legacy-operation compatibility advice: those interfaces were private development
steps, not public interfaces requiring migration guidance. This supersedes the editorial draft's requirement
to preserve that legacy paragraph. Current examples should use `operations`; historical dev evidence and
actual runtime compatibility conditions are outside this prose cleanup.

Live discovery confirmed python-engineer-p3 idle in s2 w9:p1 on its clean pilot branch at `bbf5fec6`.
Continued the same full-contract engineer at requested medium effort to apply this bounded revision,
including maintained guide/reference/notebook occurrences, then rebuild and inspect the pilot. No new
agent, s3 work, runtime behavior change, notebook execution, migration or landing is authorized.
Worker returns lane-local `p3/plain-language-return.md`; coordinator retains commit authority.
New checks, measurements and final acceptance pending.

Clarified the cleanup boundary to include development migration/layout and source-transition history
in maintained toolbox guides. Preserve current integrity/refusal requirements stated directly, and
preserve historical dev evidence and upstream reference material. The publishing fixture still checks
old-path routing; it does not document the removed legacy operation. No runtime support is being removed.

### Plain-language acceptance

Engineer completed turn `01a1794c-6207-76a2-9d2c-4cd893747577` in 764.598 seconds wall-clock and is idle.
Retained return: `publishing-pilot-plain-language-return.md`, SHA256
`b5550c15feae2b796661ea399b09e6540f67396041f32622c2b673a0c9035d89`.
Same full manual python-engineer role and medium allocation; completed applicable skills reused, no new
skill reads required. Tokens, active compute, tool-wait totals and cost are unknown.

Coordinator reviewed the 22-file diff and affected PDF pages. Seventeen affected tests pass (eight unrelated
notebook Git-index/strip tests deselected); scoped Ruff, compile, whitespace, notebook nonprose identity,
scaffold parsed-setting identity, 51-document scan, 40 rendered-block checks and HTML/PDF inspection pass.
The pre-commit notebook-output check passes. Search found no maintained links to the removed headings.
Current operation examples replace the obsolete syntax; development migration/history prose is removed.

Review corrections preserved snapshot-role guidance, corrected source-label wording and avoided a broader
fixed-owner claim. The run-read weather-generator default was restored byte-for-byte to avoid identity
effects from comment changes; only scaffold YAML comments remain changed. Runtime behavior is unchanged.

Coordinator committed `865803b2` in s2; branch is clean and retained for owner review. Latest artifacts:
s2 `.tmp/tasks/t2610211349/p3/plain-language/build/index.html` and `index.pdf`. No landing, push, migration,
scientific-approach writing or s3 work. Historical dev/upstream evidence remains intact.

## V9 acceptance, landing and P4 commission — 2026-10-26

Owner explicitly approved V9, integration and P4A/P4B. Live s2 had six uncommitted follow-up paths beyond
`865803b2`, with completed returns for concrete filenames/YAML, plain-language IDs, output-folder tree,
highlighting, flush-left PDF contents and ragged-right body. Coordinator reviewed the exact diff and
retained `publishing-pilot-v9-return.md`. Reused 14 source/pilot checks for content, 12 final pilot tests,
46 rendered-block/link/hash checks and worker visual inspection; staged whitespace passed.
These worker follow-ups reused the full manual engineer role/skills at medium. Detailed wall time/usage
for the intervening turns is not consolidated; no estimate is claimed.

Committed V9 as `fb9aca81`. Fetched origin: main was 20 ahead/0 behind. Synchronized main into s2 without
rewriting reviewed commits, then guarded `task-land` verified equality to `fb9aca81` outside coordinator
task/board records. Landed at `8963f661`; ancestry/tree assertions passed and the pilot branch was deleted.
Session-2 parked clean. Unrelated unstaged primary board/task additions were preserved. No push.
Retain all P3 review artifacts in s2 while the central review index links them; no scratch deletion.

Revalidated allocation: continuing technical-writer in s1, fresh api-documenter in s2, both GPT-6.1-Sol
medium; at most two workers. cst-main owns commits/integration; s3 remains unrelated and untouched.
Disjoint scope and checks are in `p4-content-assignments.md`. Role change requires ending the completed
P3 engineer and checking fresh P4B context. Scientific writing remains deferred; P5/P6 are not dispatched.
