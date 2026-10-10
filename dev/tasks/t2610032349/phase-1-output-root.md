# Task Brief — P1: Remove the active output suffix

### Context

Read root `AGENTS.md` and [master brief](task-brief.md). The output-folder task is `t2610101521`.
`create_case.py` currently emits `runs/<slug>/active/`; the new scaffold default is `runs/<slug>/`.
Output roots remain user-selected; existing paths require no migration.

### Goal

Make scaffolds, previews and starter guidance agree on an output root without the `active/` suffix.

### Non-goals

No output movement, existing case-config rewrites, automatic versions or mandatory replacement layout.

### Allowed scope

Permitted toolbox paths: `scripts/create_case.py`, `tests/test_create_case.py`,
`docs/site/guide/running.qmd` and generated starter text produced by that script.
Coordinated case-repository paths: `cst-cases/README.md`,
`cst-cases/templates/example-basin/README.md` and `project_config.yml` in that template.
Read that repository's instructions first; commit its edits independently in its permitted workspace.
If external write access is unavailable, prepare its exact patch and report that acceptance is pending.
Existing `cst-cases/applications/`, `runs/`, inventory and historical records are forbidden to modify.

### Required changes (checklist)

- Remove `active` from default path construction, preview output and newly generated guidance.
- Preserve boundary/symlink/junction checks for the actual output root; do not weaken confinement.
- Update focused assertions and guidance; users can choose another root through configuration/runner.
- Coordinate the three case-repository starter files; retain references to real historical output paths.

### Commit plan

Commit scaffold behavior, its tests and toolbox guidance together so advertised paths match generated
paths. Commit case-repository starter changes separately, identifying the paired toolbox commit.

### Validation

Per edit: `pixi run python -m pytest tests/test_create_case.py -q`.
Before commit: touched-file Ruff lint/format checks. Check case guidance independently once after edits.
Falsifiers: default/preview still contains `/active`; scaffold execution creates output directories;
an existing tree changes; symlink escape is accepted. Add focused fixture cases asserting these facts.
Search live guidance with `rg -n 'active/|/active' scripts docs/site tests` and the scoped external files;
classify historical/explicit-user examples rather than deleting every match. No full suite for P1 alone.

### Acceptance criteria

New scaffolds point to `runs/<slug>/`; previews agree and remain read-only. Existing explicit `active/`
roots remain legal. No existing outputs/configs are changed. Both repositories' starter guidance agrees.

### Output requirements

Report exact paths, commands/results, paired commits and any external-access blocker. No deletions.

### Task constraints

Do not modify case data. The 2026-10-10 broad inventory could not read `data/` under applications
`wrt-egypt-test1`, `ntoum-test`, `gabon-v2`, `sp2-liberia` and `wrt-egypt-alexandria`; those paths are
outside this starter-file scope and remain uninspected. Future inventory searches must stay scoped.
