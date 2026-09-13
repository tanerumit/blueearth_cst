# GF15 production integration — master brief

Date: 2026-09-14. Governed by AGENTS.md and the owner-approved
[adapter design](../gf15-production-adapter-design.md), G2 approved 2026-09-14.
The design controls every numerical and identity decision; these briefs assign
its execution, without adding scientific claims or relaxing its gates.

Current execution boundary, 2026-09-14: [snapshot integrity](evidence/gf15-production-integration/snapshot-integrity-review.md)
passed, conditional on preserving the original absolute collection anchor.
[Setup discovery](evidence/gf15-production-integration/stage-1-readiness.md)
could not establish Pixi or a Linux execution route. Stage1 remains incomplete;
owner chooses local Linux provisioning or an identified existing Linux runner.

## Subsystems and sequence

| Stage | Brief / responsibility | Blocking edge |
|---|---|---|
| 1/4 | [Snapshot and setup](gf15-production-stage-1.md), python-engineer | Complete retained comparison and isolated setup; independent integrity review before implementation |
| 2/4 | [Adapter and evidence](gf15-production-stage-2.md), python-engineer | Stage1; model-validator source-qualified parity on every supported platform before integration |
| 3/4 | [Metrics comparison](gf15-production-stage-3.md), python-engineer then model-validator | Stage2 parity; complete metrics-only comparison, no accepted abort |
| 4/4 | [Integration acceptance](gf15-production-stage-4.md), cst-architect | Stage3 and all per-platform evidence; named independent acceptance |

Continue authorized preparation and execution through these verification gates.
Pause only for a missing complete comparison, unavailable required environment,
failed acceptance, or a material scope/method decision. A gate is not satisfied
by the passage of time or design approval. No generation/Wflow rerun, successor
baseline, milestone seal, upstream package patch, merge or push is authorized
by this brief. Preserve the session's pinned branch.

## Change surface and commit order

Stage1 owns new evidence and isolated setup; stage2 owns
`blueearth_cst/experiment/{metric_registry,metric_plan,gev_lmoments,return_level_validation}.py`,
the proposed `data/gf15-accuracy-8x-v1.json`, `pixi.toml`, solver-produced
`pixi.lock`, owning tests and discovered user metric documentation. Stage3 owns
new comparison evidence and distinct metric outputs; stage4 owns acceptance
and R12 tracking. Re-measure callers and documentation references before edits.
`content_identity.py` is conditional only if its existing projection cannot
represent D7; this broadens validation. Export code, Snakefiles, simulation and
generation identity remain preservation surfaces.

Freeze the pre-change snapshot before the first implementation commit. Commit
dependency support, candidate consumers, report/schema and writer changes only
in runnable groupings; no consumer may precede its dependency or evidence.
Documentation-only design finalization may commit before the snapshot.

## Validation and evidence

The design's full **Validation plan and falsifiable consequences** table is
incorporated as the claim-to-falsifier contract. Each phase below maps its rows
to commands/artifacts. New test commands are materialized after inspecting the
owning modules; never claim an unexecuted test passed. Use owning tests during
iteration, lint/format before Python commits, test-fast once before integration,
and test-full only if shared/signature scope triggers it. Redirect logs to files.
Baseline checks remain the separate milestone-seal gate.

Retain source/environment hashes, exact argv, platform, failures and coverage.
Report original and 3x failures alongside the development-only 8x pass; it
establishes neither actual-bundle adequacy nor independent validation.
