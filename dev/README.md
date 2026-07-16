# dev/

Development process and project record. Everything here supports building the
project; none of it ships. The lifecycle that fills these folders is the
`project-system` skill's workflow.

## Layout

| Path | Holds |
|---|---|
| `TODO.md` | Live task board -- unfinished work only (`backlog` / `active` / `blocked`) |
| `working/` | Ephemeral working & handoff notes; deleted at task closure |
| `tasks/` | One brief record per closed tracked task |
| `decisions/` | Decision records (context, alternatives, consequences) |
| `reviews/` | Periodic and milestone review summaries |
| `workflows/` | Reusable multi-stage process definitions |
| `scripts/` | Runnable developer scripts -- build, lint, profile, and exploratory one-offs |
| `tmp/` | Disposable machine-local outputs (gitignored) |

Shard `tasks/` or `reviews/` into `<year>/` subfolders only if a flat folder
ever grows unwieldy. Generated results, figures, and model outputs go in the
project-root `output/` (gitignored), not `dev/`.

## Historical archive (pre-`project-system` convention)

This project predates the type-folder grammar above. Sealed milestone artifacts
keep their original roadmap-driven, milestone-grouped layout and are **not**
refactored:

| Path | Holds |
|---|---|
| `roadmap.md` | Source-of-truth fork roadmap: phases, milestones, branching/tagging |
| `followups.md` | Milestone-scoped backlog (R3/R5 items) with reproducible context; referenced by live tests |
| `baseline/manifest.json` | M1 replication baseline fingerprints (read by `scripts/check_baseline.py`) |
| `phase-1/m0x/` | Phase 1 (Foundation, sealed 2026-05-08) milestone records |
| `r01/`, `r02/` | Phase 2 (Refactor) milestone design/plan/review docs |

The type-folder grammar governs **new** work; these records stay as-is.

## Working rules

- **Admit before you track.** Small work fully explained by its diff and Git
  history creates no task ID or record. Track only work that must stay visible
  beyond the current session.
- **The board holds live work only.** Move closed tasks to `tasks/` and
  delete their working notes.
- **Handoffs are self-contained.** A note handed to another session or runtime
  states objective, state, decisions, location, validation, next action, and
  blockers.
- **Record exact validation** -- the commands run and their outcomes.
- **Log shipped features in the root changelog** (`CHANGELOG.md`) -- feature-level
  entries only, linking `decisions/` or `tasks/` for the detail. It lives at the
  project root, not in `dev/`.

Create optional folders only when first needed.
