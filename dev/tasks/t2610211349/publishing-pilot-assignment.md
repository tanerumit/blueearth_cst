# P3 publishing pilot assignment

Authorized by the owner on 2026-10-26. Return the pilot for review before migration.

## Allocation and authority

- Worker: python-engineer, implement mode; GPT-6.1-Sol medium, fresh s2 context.
- Checkout: session-2; branch `feat/t2610211349-publishing-pilot`, based on main `470fc761`.
- Coordinator cst-main alone owns commits, landing and shared task records. No push or deployment.
- One implementation writer. You are not alone in the repository; preserve other agents' edits.
- No nested delegation. Do not use session-3. Do not edit main through shared task junctions.
- Read and apply the full canonical role at
  `C:/Users/taner/workspace/brain-infrastructure/artifacts/agents/python-engineer.md`.
  This is manual role application in a generic Codex runtime, not native role activation.

Before the first edit, read each applicable SKILL.md body completely. Use consecutive bounded reads
when output is truncated; selecting headings or initial lines does not complete the read. For each
applicable skill, identify its linked-reference load conditions and the task phases they govern.
Before each governed action, including verification, read references whose conditions apply and
follow further triggered links. Keep unrelated references unloaded. Report any incomplete reads.

## Inputs and scope

Read the task's `publishing-pilot-content-specification.md`, `documentation-execution-plan.md`, and
the current owner-decision paragraph in `documentation-boundary-map.md` from canonical main task records.
The frozen content specification is the editorial contract; do not independently rewrite the prose.
Read repository documentation and validation references before changing publishing mechanics.

Implement the smallest isolated pilot using the existing Quarto/staging approach where feasible.
Authorized tracked write targets in s2:

- `dev/scripts/stage_site_guides.py` and a separate `dev/scripts/build_docs_pilot.py` if needed.
- `tests/test_site_guides.py`, `tests/test_docs_pilot.py`, and `tests/fixtures/docs-pilot/`.
- `docs/publishing-pilot/` for a manifest, pilot configuration and build instructions only.
- `docs/site/_quarto.yml` and docs-related `pixi.toml` tasks only if essential to the pilot; prefer
  isolated configuration so production publication stays unchanged.

Do not move or rewrite live guide/reference/local README sources, change the scaffolder, change
dependencies/lockfiles, write scientific-approach chapters or implement migration. Demonstrate the old
source-path compatibility rule in the tracked isolated fixture specified by the editorial lead.
If essential work falls outside these targets, report the exact need before broadening.

Keep caches, copied test sources, generated HTML/PDF and visual-check evidence in the session-local
ignored `.tmp/tasks/t2610211349/p3/`; verify ignore status before writing. Maintain your lane STATUS.md.
Use a compatible runtime through the repository's documented session-runtime helper; do not mutate
another lane's runtime. Inspect installed PDF tooling before choosing it; report a missing tool
instead of silently installing dependencies. No model runs, notebook execution or data acquisition.

## Acceptance and return

Complete the frozen specification's HTML/PDF, unchanged-source, refresh, missing-input, link,
compatibility and static-fallback checks. Use affected tests and scoped Ruff for Python changes.
Visually inspect both formats; distinguish HTTP/link checks from rendering and interaction checks.
Use available browser/PDF tools under their skills; do not claim visual acceptance from text checks.
Do not change permissions or global defaults. Coordinate any long-running visible watch command.

Write your durable return to the authorized session-local path
`.tmp/tasks/t2610211349/p3/worker-return.md`. You own this evidence file; cst-main will inspect and
retain its relevant contents under the canonical task folder. Include changed paths, build recipe,
HTML/PDF paths, checks/results, supported features, limitations, source-integrity evidence and blockers.
Record UTC start/end, actual roles/skills, requested versus observed model/effort, waits, retries and
available usage; unknown measurements stay unknown. Reply with the file path, completion status and
concise checks. File existence alone is not completion. Leave all implementation changes uncommitted
for cst-main review and stop after P3. Do not proceed to P4 or migration.
