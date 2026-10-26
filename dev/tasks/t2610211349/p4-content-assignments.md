# P4A/P4B content assignments

Owner commission: 2026-10-26, after approval of pilot V9. Integration base: `8963f661` on main.
The execution plan owns stage dependencies; this packet fixes concurrent write ownership.

## Outcome

Produce the approved user-guide and technical-manual chapters, with one maintained source for each
detailed explanation. Use the reviewed boundary map, including its final reconciliation, and current
implementation evidence. P4A and P4B may run concurrently; cst-main alone reviews, commits and integrates.
P4C scientific-approach writing remains deferred. P5 whole-publication assembly and P6 fresh-reader review
are subsequent stages, not part of this commission.

## Shared scope and constraints

- Read `documentation-boundary-map.md`, `documentation-execution-plan.md`, the scoped inventory and
  `publishing-pilot-v9-return.md`. Inspect current sources, not historical excerpts in task records.
- Apply V9's reader level: short sentences, direct choices, numbered actions, concrete filenames and
  small examples. Explain what to do and what result to expect. Avoid parser terminology in user steps.
- User guides describe registry scripts briefly and link advanced details. Named implementation files,
  schemas and exact contracts belong in the technical manual/local reference. Do not restore development
  legacy-operation, release-transition or migration narratives removed by the owner.
- Preserve existing source/publication routes through small tracked wrappers or landing links where
  needed. That routing mechanism is distinct from obsolete-interface advice; do not add migration prose.
- `.ipynb` remains the sole editable notebook source. No notebook/model execution or data acquisition.
  Do not promise a self-contained dataset, fast runtime, assessed basin performance or response-surface
  construction. Table interpretation/selection/extension is the current promise; axis authority is deferred.
- Scientific-approach sources remain unchanged. Preserve their existing links and qualifications.
  Do not silently remove existing case-specific findings or move them into excluded evidence directories.
- Excluded review/write surfaces: `dev/reference/`, `dev/records/`, `docs/references/`, `.github/`,
  changelog/log/legal/agent-instruction files. Read governing rules and implementation as evidence only.
- Preserve public behavior, formula/units/missingness rules, safety checks and scientific qualifications.
  Do not change runtime defaults, workflow code, dependencies or locks. Report actual contract conflicts.
- Workers are not alone. Edit only the assigned lane/paths below; do not revert others' changes or edit
  another lane. Cross-packet source material may be read from the shared base but not edited.
- No nested agents, commits, merges, landing, push, deployment or shared task/board writes.
  Maintain your ignored lane `STATUS.md`. Return uncommitted work and lane-local evidence.
- Before the first edit, read each applicable SKILL.md completely, using consecutive bounded reads if
  truncated. Identify and load triggered references before their governed actions. Check role-bound
  skills under infrastructure `_external/<name>/SKILL.md` before `<name>/SKILL.md`. Reuse completed reads
  when still applicable. Report any incomplete governing read.

## P4A — user and local guidance, s1

Role: continuing technical-writer, full canonical contract, GPT-6.1-Sol / medium.
Read/apply `infrastructure:artifacts/agents/technical-writer.md`; native persona activation is not assumed.

Write ownership:

- `README.md`, `docs/README.md`, `scripts/README.md`.
- `docs/guide/`: existing sources plus approved `install.md`, `new-case.md`, `indicators.md`,
  `troubleshooting.md`, `notebooks.md`; retain `assets/shape-of-a-run.html` without redesign.
- `docs/site/index.qmd`, `docs/site/404.qmd`, `docs/site/setup/install.md`,
  `docs/site/setup/env-setup-notes.md`: orientation and setup-route wrappers only.
- `docs/notebooks/README.md` and Markdown-cell-only edits to the three inventoried notebooks.
  Preserve all code, outputs, metadata and execution state. Report stale code as a limitation/follow-up.
- Inventoried config-local Markdown: `config/basemap/README.md`, `config/catalogs/archive/README.md`,
  `config/defaults/README.md`, `config/plotting/README.md`, `config/templates/README.md`,
  `config/templates/archive/README.md`, `config/templates/example-basin/README.md`,
  `config/templates/example-basin/data/README.md`, `config/templates/example-basin/notes.md`.
  Unsupported archives stay out of normal supported-user routes. No config YAML edits.
- `dev/README.md`, `dev/scripts/README.md`, new `dev/scripts/environment-notes.md`, and inventoried
  `dev/templates/` guidance/templates. Retain operational purpose; no UI redesign or policy duplication.
- Bounded generated-case reconciliation: the generated `INSTRUCTIONS.md` template in
  `scripts/create_case.py` and its directly affected tests in `tests/test_create_case.py` if needed.
  Keep provisioning behavior and starter values unchanged. Give copied cases usable version-identifiable
  documentation references without inventing a deployed URL or shipping a second manual copy.

Work:

1. Follow the approved ten-chapter user-guide outline and quick-start journey. Carry the source-to-owner
   map forward; shorten duplicate reference detail into links to the P4B destination chapters below.
2. Preserve point-of-use prerequisites, external-data gates, output recognition, recovery and limits.
   Provide one run join and one group join at table level, grounded in actual schemas.
3. Move installation/maintenance procedures to their approved homes; keep old setup routes usable.
   Reconcile copied-case instructions and local relative-link behavior with the central guide.
4. Keep global navigation recommendations in your return for P5. Do not edit `_quarto.yml`, publishing
   scripts, pilot manifests or shared tests; report required assembly changes with exact destinations.

## P4B — technical reference, s2

Role: fresh api-documenter, full canonical contract, GPT-6.1-Sol / medium.
Read/apply `infrastructure:artifacts/agents/api-documenter.md`; native persona activation is not assumed.

Write ownership:

- `docs/technical-manual/`: `overview.md`, `environment.md`, `workflows.md`, `configuration.md`,
  `input-formats.md`, `datasets.md`, five `workflow-*.md` chapters, `retained-handoffs.md`,
  `execution-and-provenance.md`, `results-transfer.md`, `indicator-requests.md`,
  `indicator-extension.md`, and an explicit local-source appendix manifest if necessary.
- The inventoried `docs/site/toolbox-reference/*.qmd` pages, for source transfers and route wrappers.
- `blueearth_cst/indicators/README.md` and the five inventoried set READMEs
  (`default`, `flow_regime`, `eflow_erfa`, `crop_water`, `flood_risk`). No Python/R calculations.

Work:

1. Trace usage-affecting fields, defaults/precedence, paths, units, inputs/outputs, status/reason values,
   joins, refusals and examples to current executable owners/tests. Resolve stale path descriptions.
2. Extract shared technical detail from the base guide/setup/config sources into the approved central
   owners. P4A alone shortens those original guide/local files; give it precise anchors via your return.
3. Keep module/set READMEs canonical. Use explicit includes/assembly declarations for the offline manual,
   not independently editable copies. All five sets and the module extension contract must be accounted
   for. Label intentionally external evidence. Publishing support itself belongs to P5.
4. Preserve scientific qualifications and existing case findings while P4C is deferred. If a source mixes
   technical and scientific material, keep the scientific text unchanged at one reachable home and record
   its temporary placement; do not invent a new scientific chapter or discard evidence.
5. Preserve old toolbox-reference paths/important anchors with small tracked wrappers. Do not edit global
   site navigation, guide files, config-local guidance, notebooks, publisher scripts or shared tests.

## Acceptance and verification

Each packet returns: changed paths; every owned inventory disposition; source-to-destination/anchor map;
removed duplication; evidence owners for substantive claims; unresolved conflicts; exact checks and limits.
Name counterpart links that cannot resolve until the other packet is integrated. Do not create substitute
pages in another worker's ownership to make a local check pass.

Inspect source links and examples, scan incoming links to moved headings, and check prose/scientific fidelity.
Use `git diff --check` and applicable existing checks selected under `dev/reference/dev-validation.md`.
Notebook prose edits require JSON/nonprose preservation checks; generated-case template edits require
targeted scaffolder checks and generated instructions inspection, with Python discipline as applicable.
Full HTML/PDF assembly is P5: do not claim whole-publication completeness from source checks or the pilot.
Use the compatible main runtime through `dev/scripts/session_runtime.py`; no environment installation.

Return artifacts: s1 `.tmp/tasks/t2610211349/p4a-return.md`; s2 `.tmp/tasks/t2610211349/p4b-return.md`.
Check scratch ignore/ownership first. Artifact-first output is authorized; cst-main retains the reports.
Record start/end UTC, role, requested/observed model and effort, actual skills/references, checks/rework,
and available usage. Unknown measurements remain unknown. Report completion and stop for coordinator
acceptance; unresolved reader promises or scientific decisions go to the owner through cst-main.
