**Frozen P3 content specification — indicator selection**, based on current main `470fc7613b8fd2cf6b840b724b5b4a0d3f64505e`. This instruction supersedes the records’ pending-authorization wording. P3 produces a reviewable HTML/PDF sample; migration remains held.

**Reader outcome:** understand how to select indicators from completed simulations, locate their tables and consult the default set’s conventions. Commands are displayed examples, never executed by publication. Surface construction and scientific-approach writing remain deferred.

### Frozen source selection

Assemble these existing sections in the following order. Preserve their substantive wording; only heading levels, link destinations, source attribution and format handling may change.

| Order | Existing source | Exact inclusion |
|---|---|---|
| 1 | `docs/guide/running.md` | Complete `## Calculate different indicators from existing simulations` section, stopping before `## Next`. Includes completed-simulation prerequisite, command and named-result destination. |
| 2 | `docs/site/toolbox-reference/workflow-simulate-system.qmd` | Within `## Configuration`, include the paragraphs beginning “`operations` is a nonempty list…” through “…calendars, missingness or grain.” Exclude the preceding YAML example, which references an additional custom-set file. |
| 3 | `docs/guide/outputs.md` | Under `## Reading an indicator set`, include the opening paragraph beginning “For post-processing…” and ending “…under its own indicator key.” Then include `### Opening an indicator table in Excel`, stopping before `### Migrating existing outputs`. |
| 4 | `blueearth_cst/indicators/sets/default/README.md` | Include the complete README as the locally maintained conventions appendix. Preserve its module-authoring link, units, partial-block/missingness qualifications and pooled-return-level distinction. |
| 5 | `docs/guide/quick-start.md` and `docs/guide/assets/shape-of-a-run.html` | Separate presentation annex: complete `## The shape of a run`, stopping before `## Pick a configuration`, with the asset handling below. |

Orders 1 and 3 exercise existing central Markdown; order 4 exercises local-source inclusion. Order 2 tests selected reference material without relocating its live source.

Use a deterministic inclusion manifest with source paths, section boundaries and attribution. Fail clearly if an expected boundary is absent or ambiguous. Derived assembly must not become an independently editable prose copy.

### Links, notation and assets

- Preserve working internal navigation among the included sections in both formats.
- Mark links outside the sample explicitly as repository/online references. In particular, the default README’s `../../README.md` must resolve to the indicator-module README, not an accidentally rebased location. The pilot need not include that entire extension guide.
- **No new equation or bibliographic citation is needed for this selection.** Preserve existing inline expressions, including `max(ceil(T),10)`, as written. Report formal equation/citation rendering as outside this pilot’s demonstrated coverage.
- HTML may retain the existing interactive workflow diagram.
- PDF and noninteractive reading must provide the existing SVG diagram **plus all five workflow descriptions from the asset’s `details` object** and its order-versus-dependency legend. The initial “Select a workflow” view alone is inadequate. Derive this fallback from the same asset; do not invent another scientific explanation.
- The annex demonstrates workflow orientation only; it must not imply a supported response-surface construction tutorial.

### Old `.qmd` compatibility example

Exercise this real migration pair **inside a tracked, isolated pilot fixture**, without replacing or moving the live page:

- Old source address: `docs/site/toolbox-reference/workflow-simulate-system.qmd#configuration`.
- New canonical source destination represented by the fixture: `docs/technical-manual/indicator-requests.md#configuration`.
- Preserved rendered address: `toolbox-reference/workflow-simulate-system.html#configuration`.

The fixture’s old `.qmd` compatibility page must be tracked, contain a working relative link to the canonical Markdown, and preserve the selected anchor. Test source navigation **before rendering**, then test the corresponding rendered route. A generated staging copy alone does not satisfy source compatibility.

This demonstrates choice **2A** without beginning migration. Choice **1A**, generated-case instruction reconciliation, remains in the authorized later content scope; P3 must not modify the scaffolder merely to demonstrate publication.

### Pilot acceptance and handback

Produce HTML and PDF from the same manifest and source material using the existing publisher where feasible. The engineer selects available PDF tooling and records the actual commands.

Required evidence:

- Included text, code, units and local conventions remain complete and legible in both formats.
- Builds leave original sources unchanged.
- A temporary change to an isolated source copy refreshes both outputs; a missing required input fails clearly.
- Internal links and the old source/rendered compatibility example work.
- Static fallback conveys every essential interactive explanation.
- Rendering invokes no simulation, notebook execution or data acquisition.
- Report exact artifact paths, supported features, checks and limitations; return for pilot review before migration.

These are acceptance requirements, **not checks already passed**. No dataset, retained simulation or fast-run promise is introduced.

**Execution record:** UTC start `2026-10-26 14:18:27`; final source/specification check `14:20:15`. Reused canonical technical-writer role and previously loaded `scientific-software-documentation`, `project-reference-docs`, `testing-policy`, `project-system` and `tutorial-authoring`. Newly read completely: canonical `task-brief/SKILL.md` and triggered `references/task-brief.md`, applied to the bounded handoff. No newly applicable read remains incomplete. No edits, writes, runs, Git mutations or delegation; token usage unknown.
