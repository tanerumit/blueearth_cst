# Repository documentation inventory by audience

Date: 2026-10-26. Task: t2610211349. Revised scope: main checkout before this update.
Source commit: `fb4366c3bfd709d56da9d77a2a0b7b1675b3a8e3`.

## Scope and method

This is a file-level inventory for the next boundary, purpose and redundancy review.
Audience assignments are provisional classifications from location, titles and collection entry points;
they do not certify the accuracy, currency, intended authority or uniqueness of every document.
No documentation consolidation, deletion or scientific correctness review has been performed.

The register contains **64 tracked files**, each listed exactly once under a primary audience group.
It includes Markdown, Quarto, notebooks, HTML documents/templates, and LICENSE.
The selector also checked R Markdown, reStructuredText, PDF, Word, bibliography, AsciiDoc, TeX and Typst.
No additional files in those latter formats were found. Binary figures and data are not document entries.
Excluded from review: `dev/tasks/`, `dev/reference/`, `dev/references/`, `dev/records/`,
`docs/references/` and `dev/LOG.md` (the repository LOG.md).
`dev/reference/` is the existing directory corresponding to the requested `dev/references/`.
This inventory remains saved under the task directory, which is excluded from its own review scope.
Other dev documents, including dev/README.md, dev/scripts, dev/templates and dev/TODO.md, remain in scope.

Enumeration used `git ls-files` in the canonical main checkout, including hidden tracked directories.
File headings/frontmatter were sampled for labels; collection indexes and site configuration were read.
Labels marked "filename label" have no extracted heading and should not be read as inferred purpose.
No untracked, nonignored files were present at enumeration. Ignored outputs and external linked agent
libraries are described separately below rather than silently counted as repository-owned documents.
All register links are relative to this task directory and resolve to files in the same checkout.

## Audience summary

| Group | Files |
|---|---:|
| Toolbox users and practitioners | 29 |
| Scientific explanation | 4 |
| Indicator users and extension authors | 6 |
| Configuration users and maintainers | 9 |
| Developer and maintainer guidance | 9 |
| Agent instructions | 2 |
| Validation evidence | 2 |
| Task coordination and handoffs | 2 |
| Legal and reuse | 1 |

## Collection roles and review boundaries

- User entry points: root README, docs index, setup pages, user guides and script index.
- Published explanation and reference: scientific-approach and toolbox-reference pages under docs/site.
- Copyable examples: config/templates; runtime settings: config/defaults. Their READMEs are distinct entries.
- Developer entry points and tools: dev/README.md and dev/scripts; reusable forms: dev/templates.
- Agent authority: AGENTS.md; CLAUDE.md imports it. Shared role/skill libraries have external owners.
- In-scope evidence: baseline provenance and test-oracle notes. Retained dev/records are excluded.
- Work coordination: dev/TODO.md and DEVLOG.md remain listed; task records and dev/LOG.md are excluded.
- Legal text: LICENSE is included for completeness, outside the editorial consolidation review.

## Documentation surfaces beyond standalone documents

These surfaces need consideration in the next review; they are not included in the file-register total.
This inventory does not enumerate or assess every individual comment, docstring or help string.

| Surface | Primary audience | Review relevance |
|---|---|---|
| scripts/ CLI help and module docstrings | Users | Execution arguments and examples |
| blueearth_cst/ docstrings and R comments | Developers | Interfaces, units and assumptions |
| Root *.smk and workflow rule comments | Developers | Workflow contracts and dependencies |
| config/ YAML and TOML comments | Case authors | Defaults, choices and configuration examples |
| test_case/ configuration examples | Developers | Verification examples and provenance |
| tests/ assertions and fixtures | Developers | Executable contract evidence |
| dev/scripts/ help and docstrings | Maintainers | Repository maintenance procedures |
| pixi.toml and pyproject.toml | Users, maintainers | Commands, environment and tooling |
| .git-workflow.yml and .testing-policy.yml | Agents, maintainers | Machine-readable policy |
| .agent-system/agent-manifest.yml and .agent-env.yml | Agents | Activation and environment |
| .github/workflows/ and profiles/ | Maintainers | CI and execution settings |
| docs/site/_quarto.yml | Documentation authors | Navigation and publication scope |

### Generated and external surfaces

- docs/site/guide is staged from docs/guide by dev/scripts/stage_site_guides.py; edit the source.
- docs/site/_site is rendered output. Generated copies are not independent documentation authorities.
- dev/TODO.md is a tracked generated view and is counted; its task notes are the editable sources.
- STATUS.md is ignored lane-local state. It is outside this reproducible tracked-file inventory.
- .agents, .claude and .codex expose local roles, skills and runtime settings, including linked sources.
  Their bodies are outside repository ownership and this register; dev-agent-activation.md and the
  tracked agent manifest are the project-facing entry points. No external library was copied here.
- Run-generated reports, caches, local environments and external basin outputs are excluded.
- Figures and interactive assets are supporting material: tracked HTML is included; images are excluded.

## Next review

For each current document, record its primary reader, reader question, authoritative scope, inputs,
outputs, overlaps and required links. Compare overlapping claims before deciding whether to consolidate,
shorten or cross-link. Preserve purposeful differences between tutorials, procedures, explanations,
references and executable contracts. Apply this review only to the in-scope files and surfaces above.
Start with the user/developer/agent collections; docs/references is excluded from this review.

## Complete file register

### Toolbox users and practitioners (29)

Primary: users running assessments. Secondary: trainers and support maintainers.

- [CHANGELOG.md](../../../CHANGELOG.md)
  Label: Changelog
- [docs/guide/assets/shape-of-a-run.html](../../../docs/guide/assets/shape-of-a-run.html)
  Label: The shape of a run · BlueEarth CST
- [docs/guide/benchmarking.md](../../../docs/guide/benchmarking.md)
  Label: Run summaries and WF4 benchmarking
- [docs/guide/configuration.md](../../../docs/guide/configuration.md)
  Label: Configuring a project
- [docs/guide/outputs.md](../../../docs/guide/outputs.md)
  Label: Reading the outputs
- [docs/guide/quick-start.md](../../../docs/guide/quick-start.md)
  Label: Quick start
- [docs/guide/running.md](../../../docs/guide/running.md)
  Label: Running the workflows
- [docs/notebooks/Climate projections.ipynb](../../../docs/notebooks/Climate%20projections.ipynb)
  Label: Climate projections (filename label)
- [docs/notebooks/Climate Stress Test.ipynb](../../../docs/notebooks/Climate%20Stress%20Test.ipynb)
  Label: Climate Stress Test (filename label)
- [docs/notebooks/Model building.ipynb](../../../docs/notebooks/Model%20building.ipynb)
  Label: Model building (filename label)
- [docs/notebooks/README.md](../../../docs/notebooks/README.md)
  Label: Workflow notebooks
- [docs/README.md](../../../docs/README.md)
  Label: Documentation
- [docs/site/404.qmd](../../../docs/site/404.qmd)
  Label: Page not found
- [docs/site/index.qmd](../../../docs/site/index.qmd)
  Label: BlueEarth Climate Stress Test
- [docs/site/setup/env-setup-notes.md](../../../docs/site/setup/env-setup-notes.md)
  Label: Environment setup notes
- [docs/site/setup/install.md](../../../docs/site/setup/install.md)
  Label: Installing BlueEarth-CST (Windows)
- [docs/site/toolbox-reference/assessment-workflow.qmd](../../../docs/site/toolbox-reference/assessment-workflow.qmd)
  Label: Assessment workflow
- [docs/site/toolbox-reference/datasets.qmd](../../../docs/site/toolbox-reference/datasets.qmd)
  Label: Datasets
- [docs/site/toolbox-reference/modeling-tools.qmd](../../../docs/site/toolbox-reference/modeling-tools.qmd)
  Label: Modeling Tools
- [docs/site/toolbox-reference/overview.qmd](../../../docs/site/toolbox-reference/overview.qmd)
  Label: Toolbox reference
- [docs/site/toolbox-reference/retained-handoffs.qmd](../../../docs/site/toolbox-reference/retained-handoffs.qmd)
  Label: Retained scenario and simulation handoffs
- [docs/site/toolbox-reference/workflow-analyze-climate.qmd](../../../docs/site/toolbox-reference/workflow-analyze-climate.qmd)
  Label: WF0 — Analyze climate
- [docs/site/toolbox-reference/workflow-analyze-projections.qmd](../../../docs/site/toolbox-reference/workflow-analyze-projections.qmd)
  Label: WF2 — Analyze projections
- [docs/site/toolbox-reference/workflow-build-model.qmd](../../../docs/site/toolbox-reference/workflow-build-model.qmd)
  Label: WF1 — Build model
- [docs/site/toolbox-reference/workflow-generate-scenarios.qmd](../../../docs/site/toolbox-reference/workflow-generate-scenarios.qmd)
  Label: WF3 — Generate scenarios
- [docs/site/toolbox-reference/workflow-simulate-system.qmd](../../../docs/site/toolbox-reference/workflow-simulate-system.qmd)
  Label: WF4 — Simulate system
- [docs/site/toolbox-reference/workflows.qmd](../../../docs/site/toolbox-reference/workflows.qmd)
  Label: Workflows
- [README.md](../../../README.md)
  Label: BlueEarth Climate Stress Test toolbox
- [scripts/README.md](../../../scripts/README.md)
  Label: scripts/

### Scientific explanation (4)

Primary: scientific readers and analysts. Secondary: users interpreting results.

- [docs/site/scientific-approach/climate-information.qmd](../../../docs/site/scientific-approach/climate-information.qmd)
  Label: Climate information
- [docs/site/scientific-approach/conventions-and-interpretation.qmd](../../../docs/site/scientific-approach/conventions-and-interpretation.qmd)
  Label: Conventions and interpretation
- [docs/site/scientific-approach/models-and-methods.qmd](../../../docs/site/scientific-approach/models-and-methods.qmd)
  Label: Models and methods
- [docs/site/scientific-approach/overview.qmd](../../../docs/site/scientific-approach/overview.qmd)
  Label: Scientific approach

### Indicator users and extension authors (6)

Primary: indicator users and developers. Secondary: scientific reviewers.

- [blueearth_cst/indicators/README.md](../../../blueearth_cst/indicators/README.md)
  Label: Independent indicator module
- [blueearth_cst/indicators/sets/crop_water/README.md](../../../blueearth_cst/indicators/sets/crop_water/README.md)
  Label: Crop-water screening set
- [blueearth_cst/indicators/sets/default/README.md](../../../blueearth_cst/indicators/sets/default/README.md)
  Label: Default indicators
- [blueearth_cst/indicators/sets/eflow_erfa/README.md](../../../blueearth_cst/indicators/sets/eflow_erfa/README.md)
  Label: eflow-erfa
- [blueearth_cst/indicators/sets/flood_risk/README.md](../../../blueearth_cst/indicators/sets/flood_risk/README.md)
  Label: Flood discharge hazards (opt-in)
- [blueearth_cst/indicators/sets/flow_regime/README.md](../../../blueearth_cst/indicators/sets/flow_regime/README.md)
  Label: Flow regime

### Configuration users and maintainers (9)

Primary: case authors. Secondary: developers maintaining configuration contracts.

- [config/basemap/README.md](../../../config/basemap/README.md)
  Label: config/basemap/
- [config/catalogs/archive/README.md](../../../config/catalogs/archive/README.md)
  Label: Archived data catalogs
- [config/defaults/README.md](../../../config/defaults/README.md)
  Label: Rule-read configs
- [config/plotting/README.md](../../../config/plotting/README.md)
  Label: Plotting setup
- [config/templates/archive/README.md](../../../config/templates/archive/README.md)
  Label: Archived workflow configs
- [config/templates/example-basin/data/README.md](../../../config/templates/example-basin/data/README.md)
  Label: Case data
- [config/templates/example-basin/notes.md](../../../config/templates/example-basin/notes.md)
  Label: Retained run records
- [config/templates/example-basin/README.md](../../../config/templates/example-basin/README.md)
  Label: Example basin starter
- [config/templates/README.md](../../../config/templates/README.md)
  Label: Config templates

### Developer and maintainer guidance (9)

Primary: contributors and maintainers. Secondary: coding agents.

- [.github/pull_request_template.md](../../../.github/pull_request_template.md)
  Label: pull_request_template (filename label)
- [dev/README.md](../../../dev/README.md)
  Label: Development workspace
- [dev/scripts/README.md](../../../dev/scripts/README.md)
  Label: dev/scripts/
- [dev/templates/figure-comparison.html](../../../dev/templates/figure-comparison.html)
  Label: Scientific figure comparison
- [dev/templates/figure-comparison.md](../../../dev/templates/figure-comparison.md)
  Label: Interactive figure comparison template
- [dev/templates/lane-status.md](../../../dev/templates/lane-status.md)
  Label: Lane Status
- [dev/templates/README.md](../../../dev/templates/README.md)
  Label: Developer templates
- [dev/templates/workflow-report.html](../../../dev/templates/workflow-report.html)
  Label: BlueEarth · Workflow report
- [dev/templates/workflow-report.md](../../../dev/templates/workflow-report.md)
  Label: Workflow report template

### Agent instructions (2)

Primary: coding agents. Secondary: maintainers of repository instructions.

- [AGENTS.md](../../../AGENTS.md)
  Label: AGENTS.md
- [CLAUDE.md](../../../CLAUDE.md)
  Label: CLAUDE.md

### Validation evidence (2)

Primary: validators and maintainers. Secondary: scientific reviewers.

- [dev/baseline/provenance.md](../../../dev/baseline/provenance.md)
  Label: Baseline provenance
- [tests/data/eflow-erfa-r-oracle.md](../../../tests/data/eflow-erfa-r-oracle.md)
  Label: ERFA numerical reference

### Task coordination and handoffs (2)

Primary: task owners, contributors and agents. Secondary: project maintainers.

- [dev/TODO.md](../../../dev/TODO.md)
  Label: TODO
- [DEVLOG.md](../../../DEVLOG.md)
  Label: DEVLOG: feat/wf2-cmip6-improvements

### Legal and reuse (1)

Primary: users and redistributors. Secondary: contributors.

- [LICENSE](../../../LICENSE)
  Label: LICENSE (filename label)

## Verification and limitations

- Enumerated 64 unique source paths and verified that every path exists.
- Register coverage was checked against the selector; every selected file occurs once.
- Relative links were checked against the main checkout; no site build or workflow execution was needed.
- Grouping is an inventory aid, not a completed purpose or authority audit.
- Contents of every notebook cell were not read in full.
- This supersedes the earlier structural inventory for coverage, while preserving that dated record.
