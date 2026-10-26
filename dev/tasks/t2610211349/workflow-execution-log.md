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
- Coordinator: cst-main; assigned execution lane s1/s2/s3:
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
  claim enforced read-only isolation. No permission setting changed. No P2 assignment sent yet.

## P2 / attempt 1 — independent boundary critique

- Input: frozen P1 map hash above; main base `58efe411` plus coordinator-owned retained evidence.
- Worker: `critical-thinker-p2`, s2/w9:p1; fresh review context after preflight only.
- Requested/observed UI allocation: GPT-6-Astra/medium; high not used. Full canonical critical-thinker
  role instructed through generic runtime; actual role/skill application pending return.
- Dispatch UTC: 2026-10-26 13:25:46 (coordinator observation); runtime timestamp to reconcile on return.
- Authority: read-only task under current permissions, explicitly authorized by owner. No permission
  change or enforced-read-only claim. Before-review s2 tree clean/detached; source checks repeated on return.
- Deliverable: ranked critique of ownership, fragmentation, offline completeness, migration and the
  three reader journeys; no competing full design or accuracy audit. Return/acceptance/usage pending.
- P2 readiness wait: preflight finished before P1; no critique started until the accepted artifact existed.
  The owner permission decision resolved while P1 was running and did not delay the dependent dispatch.
