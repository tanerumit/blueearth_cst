# Master Brief — Experiment identity and user-selected output roots

Date: 2026-10-10.
Status: P0–P4 verified and landed; board closure awaits owner approval for review-copy removal.
Executor: repository contributor/agent using PowerShell and Pixi. Owner authorized this branch's work.

### Goal

Implement [the experiment-naming plan](experiment-naming-plan.md) and remove the mandatory `active/`
suffix from new case scaffolds. Plain runs continue a compatible experiment; explicit creation starts
another. Users control the assessment output root, independently of experiment numbering.

### Subsystem map

| Phase | Owner | Input | Expected output |
|---|---|---|---|
| P0 | Contributor | Plan and live contracts | Reviewed schema and consumer inventory |
| P1 | Contributor | Output-folder task | New scaffolds use `runs/<slug>/` |
| P2 | Contributor | P0 contract | Safe numbering and durable reservation |
| P3 | Contributor | P2 resolver | Both runners bind and resume consistently |
| P4 | Contributor | P1–P3 | Current docs and integrated evidence |

### Sequencing

P0 first: its inventory fixes ownership and resolves record/publication interfaces before code changes.
P1 and P2 are independent after P0, but this handoff authorizes no parallel agents. P3 depends on P2's
resolver and reservation contract. P4 depends on runnable P1–P3 for command examples and acceptance.
Keep every intermediate commit usable; P2 must not activate new resolution before P3 integrates it.

### Shared constraints

- Follow root `AGENTS.md`, the canonical naming plan and both existing tasks. Keep their identities:
  [naming](../t2610032349-number-experiments-and-add-a-new-experiment-flag.md) and
  [output folders](../../records/decisions/experiment-numbering-2026-10-10/implementation-evidence.md). Do not dissolve or duplicate them.
- Implementation is authorized. It grants no landing, push, release, output migration or deletion.
  Follow the assigned session/lane; commit verified units separately. Board maintenance stays on main.
- Reconcile the concurrent WF3 run-id work at P0; never silently absorb another session's unlanded work.
- Preserve scenario-neutral generation, immutable collections and existing frozen simulation schemas.
  No new dependencies, model revision subsystem, checkpoint engine or automatic output repair.
- No `active/` replacement convention: `runs/<slug>/` is a scaffold default, not a required runtime path.
  Existing `project.project_dir` and `--project-dir` choices remain valid, including old `active/` roots.
- Preserve all existing case outputs, application configs, historical evidence and sealed records.
  No automatic archiving, promotion, assessment version allocation or wholesale config rewrite.
- Paths below are an initial inventory measured 2026-10-10, not an exhaustive reader list. P0 must
  repeat searches and assign any discovered caller to one phase before changing it.
- Update this phase index when implementation state changes. Retain evidence in this task home;
  probes/logs use isolated worktree scratch. Follow global stop conditions and report verification gaps.

### Human gates

No additional human gate is introduced by packaging this brief. Before P2/P3, apply the repository's
`design-review-loop` procedure to the unresolved architecture recorded in P0; its actual review gates
govern acceptance. A conflicting live contract, changed scientific behavior or out-of-scope edit needs
an explicit decision. Complete authorized in-scope work without repeated confirmation.
Implementation completion does not authorize landing or pushing.

### Cross-cutting validation

Use `dev/reference/validation-ladder.md`; numerical algorithms are intended to remain unchanged.
Names, collection selection and seed recovery can nevertheless affect inputs: compare recorded input
identities and retained responses rather than inferring scientific equivalence from a successful run.

- Per edit: phase-local focused tests. Before commits: touched Python Ruff checks; CLI/DAG checks when
  workflow contracts change. Run `pixi run lint` and `pixi run format-check` once on the final Python batch.
- At approved batch landing: `pixi run test-full` once for shared runtime/configuration contracts;
  its pass covers `test-fast`. Run fresh all-five `pixi run test-e2e` once, without required skips.
- Reuse that execution root for compatible inventory and numerical acceptance. Separate synthetic
  roots add deletion/concurrency/crash/corruption coverage; one interrupted rapid case adds recovery.
- Redirect gates to files. Record commit, command/result, environment, config/input identities and
  output root. Never use the stale numerical baseline as proof; follow its documented prerequisites
  if the final diff introduces a numerical change. Report blockers rather than waive required checks.

### Phase brief index

| Phase | State | Last durable marker | Blocked on | Next action |
|---|---|---|---|---|
| [P0](phase-0-contract.md) | done | G2 `2111cae7`, v3 | — | Accepted capped review |
| [P1](phase-1-output-root.md) | done | `3bea47b9`; cases `cdaad63` | — | Await toolbox landing |
| [P2](phase-2-allocation.md) | done | `ea125361` | — | Await batch gates |
| [P3](phase-3-runner-binding.md) | done | `4e409685` | — | Await batch gates |
| [P4](phase-4-docs-acceptance.md) | done | `a83f5b12`, docs `12f43c00` | — | Await batch gates |

Implementation and evidence remain on `feat/minor-improvements`; no landing or push occurred.
Task-local evidence: `dev/tasks/t2610032349/implementation-evidence.md` in feature commit `a83f5b12`.
The final runtime candidate is `4e409685`; later commits add tested inspection/docs/evidence only.
One combined review round was used, as authorized; no further review or convergence claim was added.

Task-local acceptance passed: allocation/recovery/freeze/guard tests, 263 CLI/config/consumer tests,
259 inspection tests, 12 link checks, final lint/format, and matched explicit/automatic generation.
Fresh 02 and interrupted/resumed 03 each match all ten reference native tables and three metric tables.
Resume retained five completed checkpoints; completed rerun and preview preserve all 292 allocation/
experiment files. Changed complete/incomplete requests refuse before producers.

Existing native hard-stop/restoration limitations remain explicit in the retained evidence and live docs;
reservation recovery does not repair partial native outputs. Partial WF3 generation is not auto-resumed.
Three existing metric evidence leaves remain unmapped by the current tree inspector; new reservation
paths all map. No output migration, native repair or file deletion was performed.

Next boundary: user-approved landing, then the existing combined `test-full` and fresh all-five
`test-e2e` gates. Both task identities stay active on main until verified integration.
