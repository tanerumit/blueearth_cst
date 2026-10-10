# Task Brief — P4: Documentation and combined acceptance

### Context

Read root `AGENTS.md`, [master brief](task-brief.md), reviewed plan and P1–P3 evidence.
Folder removal and experiment numbering are separate user decisions that must work together.

### Goal

Deliver consistent live documentation and reproducible evidence for the complete combined change.

### Non-goals

No extra runtime redesign, historical-record rewrite, baseline re-record just for renamed paths, landing
or pushing. Route executable failures to the owning phase rather than patching them in this phase.

### Allowed scope

Permitted: `README.md`, `scripts/README.md`, `config/templates/README.md`,
`config/templates/project_config.simulate_system.template.yml`, live naming/runtime references in
`dev/reference/`, other live docs assigned at P0, both task notes and this task's evidence/index.
P1 owns `docs/site/guide/running.qmd` and case starter guidance; return defects there to P1.
Never edit generated catalogs, production outputs or sealed historical records.

### Required changes (checklist)

- Explain first run, continuation, explicit creation, older pin, mismatch recovery and scenario reuse.
- Document numeric suffix grammar, legacy behavior, helper changes, metrics-only and read-only previews.
- Execute the combined acceptance matrix; compare inventories, seed/run identities and retained data.
- Verify independent allocation under two chosen roots, including one explicitly named `active/`;
  new scaffold guidance must not turn this old valid path into a forbidden runtime name.
- Keep both task identities and report each one's verified acceptance; do not close either prematurely.

### Validation

Once after docs stabilize, search old live references and run link/documentation readers assigned at P0.
Run master final lint/format and batch integration gates at their named boundary, with logs in files.
Reuse fresh all-five rapid outputs; inspect compatible response/metric inventories against retained
identities. Execute one separate rapid interruption/recovery case and synthetic failure fixtures only
for distinct coverage. Use recorded wrapper commands from the execution fixture, not guessed flags.
Falsifiers: a documented command resolves another experiment, a completed run is overwritten, a seed
changes on resume, or `active/` removal breaks an explicitly selected existing root.

### Acceptance criteria

Every plan matrix row has a check, input case and result. Both tasks' user behavior agrees with the
implementation and docs. Required checks pass without required skips; blockers remain explicit.

### Output requirements

Return exact commands/results, tested commits, environment, input/config identities and evidence roots.
Include results delta: names/default paths change; numerical differences, if any, are explained and
validated rather than dismissed. List deletions (expected none) and closure/landing readiness separately.

### Task constraints

Do not repeat full/e2e gates per incremental edit or run a redundant fresh rapid tree. Missing external
starter edits mean the output-folder task remains partially complete, even if toolbox tests pass.
