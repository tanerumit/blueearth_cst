# Repository documentation inventory by audience

Date: 2026-10-26. Task: t2610211349. Snapshot: main checkout, before this inventory was added.
Source commit: `980d454dba50ce69d80b7b3b1a8dc0f15b2d2bf6`.

## Scope and method

This is a file-level inventory for the next boundary, purpose and redundancy review.
Audience assignments are provisional classifications from location, titles and collection entry points;
they do not certify the accuracy, currency, intended authority or uniqueness of every document.
No documentation consolidation, deletion or scientific correctness review has been performed.

The register contains **656 tracked files**, each listed exactly once under a primary audience group.
It includes Markdown, Quarto, notebooks, HTML documents/templates, retained plain-text evidence and LICENSE.
The selector also checked R Markdown, reStructuredText, PDF, Word, bibliography, AsciiDoc, TeX and Typst.
No additional files in those latter formats were found. Binary figures and data are not document entries.
The inventory itself is excluded from its source snapshot; its existing task note is included.

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
| Developer and maintainer guidance | 30 |
| Agent instructions | 2 |
| Scientific and upstream reference library | 57 |
| Validation evidence | 2 |
| Retained development records | 440 |
| Task coordination and handoffs | 76 |
| Legal and reuse | 1 |

## Collection roles and review boundaries

- User entry points: root README, docs index, setup pages, user guides and script index.
- Published explanation and reference: scientific-approach and toolbox-reference pages under docs/site.
- Copyable examples: config/templates; runtime settings: config/defaults. Their READMEs are distinct entries.
- Developer rules and architecture: dev/reference, indexed by its README; reusable forms: dev/templates.
- Agent authority: AGENTS.md; CLAUDE.md imports it. Shared role/skill libraries have external owners.
- Upstream library: docs/references includes original pages, numbered compilations and merged copies.
  These are retained representations, not yet findings of unintended duplication.
- Historical context and evidence: dev/records, baseline provenance and test-oracle notes.
  Record location alone does not establish frozen status; consult dev/records/sealed-records.yml.
- Work coordination: dev/tasks and board/ledger documents. Their audience overlaps with current guidance,
  but proposals and progress records do not by themselves establish current requirements.
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
| dev/records/sealed-records.yml | Maintainers | Preservation status and hashes |

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
references, executable contracts and historical evidence. Verify sealed status before editing records.
Start with the current user/developer/agent collections; use upstream and retained records as evidence.

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

### Developer and maintainer guidance (30)

Primary: contributors and maintainers. Secondary: coding agents.

- [.github/pull_request_template.md](../../../.github/pull_request_template.md)
  Label: pull_request_template (filename label)
- [dev/README.md](../../../dev/README.md)
  Label: Development workspace
- [dev/reference/dev-agent-activation.md](../../../dev/reference/dev-agent-activation.md)
  Label: Agent and skill activation
- [dev/reference/dev-documentation.md](../../../dev/reference/dev-documentation.md)
  Label: Documentation guidelines
- [dev/reference/dev-git-conventions.md](../../../dev/reference/dev-git-conventions.md)
  Label: Git conventions
- [dev/reference/dev-naming-conventions.md](../../../dev/reference/dev-naming-conventions.md)
  Label: Naming conventions
- [dev/reference/dev-record-lifecycle.md](../../../dev/reference/dev-record-lifecycle.md)
  Label: Development documentation lifecycle
- [dev/reference/dev-repository-layout.md](../../../dev/reference/dev-repository-layout.md)
  Label: Repository layout
- [dev/reference/dev-task-and-session-workflow.md](../../../dev/reference/dev-task-and-session-workflow.md)
  Label: Development workflow
- [dev/reference/dev-validation.md](../../../dev/reference/dev-validation.md)
  Label: Validation ladder — tiering, configs, and CI
- [dev/reference/dev-versioning.md](../../../dev/reference/dev-versioning.md)
  Label: Toolbox versioning policy
- [dev/reference/README.md](../../../dev/reference/README.md)
  Label: Current development and toolbox reference
- [dev/reference/toolbox-architecture.md](../../../dev/reference/toolbox-architecture.md)
  Label: Toolbox architecture
- [dev/reference/toolbox-forcing-units.md](../../../dev/reference/toolbox-forcing-units.md)
  Label: Forcing unit admission
- [dev/reference/toolbox-hydrological-model-interface.md](../../../dev/reference/toolbox-hydrological-model-interface.md)
  Label: Hydrological-model interface
- [dev/reference/toolbox-indicator-glossary.md](../../../dev/reference/toolbox-indicator-glossary.md)
  Label: Indicator glossary — every spelling of every WF4 output variable
- [dev/reference/toolbox-plot-style.md](../../../dev/reference/toolbox-plot-style.md)
  Label: Scientific plot style and visual review
- [dev/reference/toolbox-spatial-foundation.md](../../../dev/reference/toolbox-spatial-foundation.md)
  Label: Shared spatial foundation
- [dev/reference/toolbox-weather-generator-interface.md](../../../dev/reference/toolbox-weather-generator-interface.md)
  Label: Weather-generator interface
- [dev/reference/toolbox-workflow-map.md](../../../dev/reference/toolbox-workflow-map.md)
  Label: Workflow implementation map
- [dev/reference/wf0-figure-naming.md](../../../dev/reference/wf0-figure-naming.md)
  Label: WF0 figure filename rule
- [dev/reference/wf1-model-construction.md](../../../dev/reference/wf1-model-construction.md)
  Label: Model construction and historical simulation
- [dev/reference/wf2-cmip6-source-readability.md](../../../dev/reference/wf2-cmip6-source-readability.md)
  Label: CMIP6 source readability
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

### Scientific and upstream reference library (57)

Primary: scientific and technical developers. Secondary: coding agents and expert users.

- [docs/references/cst-toolbox-technical-note-2025.md](../../../docs/references/cst-toolbox-technical-note-2025.md)
  Label: Preface
- [docs/references/hydromt-architecture.md](../../../docs/references/hydromt-architecture.md)
  Label: HydroMT — Architecture and conventions
- [docs/references/hydromt-user-guide/_merged/data-catalog.md](../../../docs/references/hydromt-user-guide/_merged/data-catalog.md)
  Label: HydroMT user guide — Data Catalog
- [docs/references/hydromt-user-guide/_merged/migration-guide.md](../../../docs/references/hydromt-user-guide/_merged/migration-guide.md)
  Label: HydroMT user guide — Migration guide
- [docs/references/hydromt-user-guide/_merged/models.md](../../../docs/references/hydromt-user-guide/_merged/models.md)
  Label: HydroMT user guide — Working with models
- [docs/references/hydromt-user-guide/_merged/overview.md](../../../docs/references/hydromt-user-guide/_merged/overview.md)
  Label: HydroMT user guide — Overview
- [docs/references/hydromt-user-guide/_merged/reference.md](../../../docs/references/hydromt-user-guide/_merged/reference.md)
  Label: HydroMT user guide — Terminology and FAQ
- [docs/references/hydromt-user-guide/_merged/supporting-functions.md](../../../docs/references/hydromt-user-guide/_merged/supporting-functions.md)
  Label: HydroMT user guide — Supporting functionalities
- [docs/references/hydromt-user-guide/00-index.md](../../../docs/references/hydromt-user-guide/00-index.md)
  Label: HydroMT user guide
- [docs/references/hydromt-user-guide/01-intro.md](../../../docs/references/hydromt-user-guide/01-intro.md)
  Label: HydroMT user guide — Introduction
- [docs/references/hydromt-user-guide/02-overview.md](../../../docs/references/hydromt-user-guide/02-overview.md)
  Label: HydroMT user guide — Overview
- [docs/references/hydromt-user-guide/03-models.md](../../../docs/references/hydromt-user-guide/03-models.md)
  Label: HydroMT user guide — Working with models
- [docs/references/hydromt-user-guide/04-data-catalog.md](../../../docs/references/hydromt-user-guide/04-data-catalog.md)
  Label: HydroMT user guide — Data Catalog
- [docs/references/hydromt-user-guide/05-supporting-functions.md](../../../docs/references/hydromt-user-guide/05-supporting-functions.md)
  Label: HydroMT user guide — Supporting functionalities
- [docs/references/hydromt-user-guide/06-migration-guide.md](../../../docs/references/hydromt-user-guide/06-migration-guide.md)
  Label: HydroMT user guide — Migration guide
- [docs/references/hydromt-user-guide/07-terminology.md](../../../docs/references/hydromt-user-guide/07-terminology.md)
  Label: HydroMT user guide — Terminology
- [docs/references/hydromt-user-guide/08-faq.md](../../../docs/references/hydromt-user-guide/08-faq.md)
  Label: HydroMT user guide — Frequently asked questions
- [docs/references/hydromt-user-guide/data_catalog/data_cloud_storage.md](../../../docs/references/hydromt-user-guide/data_catalog/data_cloud_storage.md)
  Label: data_cloud_storage
- [docs/references/hydromt-user-guide/data_catalog/data_conventions.md](../../../docs/references/hydromt-user-guide/data_catalog/data_conventions.md)
  Label: data_conventions
- [docs/references/hydromt-user-guide/data_catalog/data_existing_cat.md](../../../docs/references/hydromt-user-guide/data_catalog/data_existing_cat.md)
  Label: data_existing_cat
- [docs/references/hydromt-user-guide/data_catalog/data_overview.md](../../../docs/references/hydromt-user-guide/data_catalog/data_overview.md)
  Label: data_overview
- [docs/references/hydromt-user-guide/data_catalog/data_prepare_cat.md](../../../docs/references/hydromt-user-guide/data_catalog/data_prepare_cat.md)
  Label: data_prepare_cat
- [docs/references/hydromt-user-guide/data_catalog/data_types.md](../../../docs/references/hydromt-user-guide/data_catalog/data_types.md)
  Label: data_types
- [docs/references/hydromt-user-guide/faq.md](../../../docs/references/hydromt-user-guide/faq.md)
  Label: faq
- [docs/references/hydromt-user-guide/intro.md](../../../docs/references/hydromt-user-guide/intro.md)
  Label: intro
- [docs/references/hydromt-user-guide/migration_guide/data_catalog.md](../../../docs/references/hydromt-user-guide/migration_guide/data_catalog.md)
  Label: data_catalog
- [docs/references/hydromt-user-guide/migration_guide/index.md](../../../docs/references/hydromt-user-guide/migration_guide/index.md)
  Label: index
- [docs/references/hydromt-user-guide/migration_guide/model_workflow.md](../../../docs/references/hydromt-user-guide/migration_guide/model_workflow.md)
  Label: model_workflow
- [docs/references/hydromt-user-guide/migration_guide/python_updates.md](../../../docs/references/hydromt-user-guide/migration_guide/python_updates.md)
  Label: python_updates
- [docs/references/hydromt-user-guide/models/model_build.md](../../../docs/references/hydromt-user-guide/models/model_build.md)
  Label: model_build
- [docs/references/hydromt-user-guide/models/model_components.md](../../../docs/references/hydromt-user-guide/models/model_components.md)
  Label: model_components
- [docs/references/hydromt-user-guide/models/model_overview.md](../../../docs/references/hydromt-user-guide/models/model_overview.md)
  Label: model_overview
- [docs/references/hydromt-user-guide/models/model_processes.md](../../../docs/references/hydromt-user-guide/models/model_processes.md)
  Label: model_processes
- [docs/references/hydromt-user-guide/models/model_region.md](../../../docs/references/hydromt-user-guide/models/model_region.md)
  Label: model_region
- [docs/references/hydromt-user-guide/models/model_update.md](../../../docs/references/hydromt-user-guide/models/model_update.md)
  Label: model_update
- [docs/references/hydromt-user-guide/models/model_workflow.md](../../../docs/references/hydromt-user-guide/models/model_workflow.md)
  Label: model_workflow
- [docs/references/hydromt-user-guide/overview/hydromt_cli.md](../../../docs/references/hydromt-user-guide/overview/hydromt_cli.md)
  Label: hydromt_cli
- [docs/references/hydromt-user-guide/overview/hydromt_intro.md](../../../docs/references/hydromt-user-guide/overview/hydromt_intro.md)
  Label: hydromt_intro
- [docs/references/hydromt-user-guide/overview/hydromt_python.md](../../../docs/references/hydromt-user-guide/overview/hydromt_python.md)
  Label: hydromt_python
- [docs/references/hydromt-user-guide/overview/index.md](../../../docs/references/hydromt-user-guide/overview/index.md)
  Label: index
- [docs/references/hydromt-user-guide/supporting_functions/methods_main.md](../../../docs/references/hydromt-user-guide/supporting_functions/methods_main.md)
  Label: methods_main
- [docs/references/hydromt-user-guide/terminology.md](../../../docs/references/hydromt-user-guide/terminology.md)
  Label: terminology
- [docs/references/hydromt-wflow/api.md](../../../docs/references/hydromt-wflow/api.md)
  Label: HydroMT-Wflow API reference
- [docs/references/hydromt-wflow/getting-started.md](../../../docs/references/hydromt-wflow/getting-started.md)
  Label: HydroMT-Wflow getting started
- [docs/references/hydromt-wflow/user-guide.md](../../../docs/references/hydromt-wflow/user-guide.md)
  Label: HydroMT-Wflow user guide
- [docs/references/README.md](../../../docs/references/README.md)
  Label: Offline reference documents
- [docs/references/wflow-user-guide/00-index.md](../../../docs/references/wflow-user-guide/00-index.md)
  Label: Wflow User Guide
- [docs/references/wflow-user-guide/01-overview.md](../../../docs/references/wflow-user-guide/01-overview.md)
  Label: Wflow documentation — overview
- [docs/references/wflow-user-guide/02-required-files.md](../../../docs/references/wflow-user-guide/02-required-files.md)
  Label: This is a TOML configuration file for Wflow.
- [docs/references/wflow-user-guide/03-toml-file.md](../../../docs/references/wflow-user-guide/03-toml-file.md)
  Label: Use \"forcing-year-*.nc\" if forcing files are split in time
- [docs/references/wflow-user-guide/04-warm-states.md](../../../docs/references/wflow-user-guide/04-warm-states.md)
  Label: Wflow documentation — warm states
- [docs/references/wflow-user-guide/05-model-config.md](../../../docs/references/wflow-user-guide/05-model-config.md)
  Label: specific for rating curve type 2 and 3 (weir flow)
- [docs/references/wflow-user-guide/06-multi-threading.md](../../../docs/references/wflow-user-guide/06-multi-threading.md)
  Label: Wflow documentation — multi threading
- [docs/references/wflow-user-guide/07-bmi.md](../../../docs/references/wflow-user-guide/07-bmi.md)
  Label: Wflow documentation — bmi
- [docs/references/wflow-user-guide/08-fews.md](../../../docs/references/wflow-user-guide/08-fews.md)
  Label: Wflow documentation — fews
- [docs/references/wflow-user-guide/09-zmq-server.md](../../../docs/references/wflow-user-guide/09-zmq-server.md)
  Label: Wflow documentation — zmq server
- [docs/references/wflow-user-guide/10-faq.md](../../../docs/references/wflow-user-guide/10-faq.md)
  Label: Wflow documentation — faq

### Validation evidence (2)

Primary: validators and maintainers. Secondary: scientific reviewers.

- [dev/baseline/provenance.md](../../../dev/baseline/provenance.md)
  Label: Baseline provenance
- [tests/data/eflow-erfa-r-oracle.md](../../../tests/data/eflow-erfa-r-oracle.md)
  Label: ERFA numerical reference

### Retained development records (440)

Primary: maintainers recovering rationale and evidence. Secondary: reviewers and agents.

- [dev/records/decision-history/0001-restore-wflow-constant-parameters.md](../../../dev/records/decision-history/0001-restore-wflow-constant-parameters.md)
  Label: ADR 0001 — Restore Wflow constants through two-sided equivalence evidence
- [dev/records/decision-history/0002-revive-subcatchment-climate-plots.md](../../../dev/records/decision-history/0002-revive-subcatchment-climate-plots.md)
  Label: ADR 0002 — Revive the subcatchment climate plots from the wflow forcing input
- [dev/records/decision-history/0003-one-shared-region-artifact.md](../../../dev/records/decision-history/0003-one-shared-region-artifact.md)
  Label: ADR 0003 — Share region and vector products without model-build dependencies
- [dev/records/decision-history/0004-order-model-readers-on-a-terminal-sentinel.md](../../../dev/records/decision-history/0004-order-model-readers-on-a-terminal-sentinel.md)
  Label: 0004-order-model-readers-on-a-terminal-sentinel (filename label)
- [dev/records/decision-history/0005-adopt-ruff-format-in-two-stages.md](../../../dev/records/decision-history/0005-adopt-ruff-format-in-two-stages.md)
  Label: 0005-adopt-ruff-format-in-two-stages (filename label)
- [dev/records/decision-history/0006-retire-subcatchment-climate-plots.md](../../../dev/records/decision-history/0006-retire-subcatchment-climate-plots.md)
  Label: ADR 0006 — Retire the subcatchment climate plots
- [dev/records/decision-history/0007-draw-basin-area-from-the-spatial-foundation.md](../../../dev/records/decision-history/0007-draw-basin-area-from-the-spatial-foundation.md)
  Label: ADR 0007 — Draw basin_area from the spatial foundation, not the model
- [dev/records/decision-history/0008-ship-blueearth-cst-unpackaged.md](../../../dev/records/decision-history/0008-ship-blueearth-cst-unpackaged.md)
  Label: 0008-ship-blueearth-cst-unpackaged (filename label)
- [dev/records/decision-history/0009-split-scenario-generation-and-system-simulation.md](../../../dev/records/decision-history/0009-split-scenario-generation-and-system-simulation.md)
  Label: ADR 0009 — Split scenario generation and system simulation
- [dev/records/decision-history/0010-check-the-reviewed-variables-not-the-catalog-shape.md](../../../dev/records/decision-history/0010-check-the-reviewed-variables-not-the-catalog-shape.md)
  Label: ADR 0010 — Check the reviewed variables, not the catalog's shape
- [dev/records/decision-history/0011-preserve-config-sources-with-run-records.md](../../../dev/records/decision-history/0011-preserve-config-sources-with-run-records.md)
  Label: ADR 0011 — Preserve exact config sources alongside one run record
- [dev/records/decision-history/0022-cst-capability-slots-and-run-contract.md](../../../dev/records/decision-history/0022-cst-capability-slots-and-run-contract.md)
  Label: ADR 0022 — Capability slots and a scheduler-neutral CST run contract
- [dev/records/decision-history/index.md](../../../dev/records/decision-history/index.md)
  Label: Decision history
- [dev/records/decision-history/task-lanes.md](../../../dev/records/decision-history/task-lanes.md)
  Label: Historical rationale for reusable task lanes
- [dev/records/migrations/decision-history-transition-2026-10-20.md](../../../dev/records/migrations/decision-history-transition-2026-10-20.md)
  Label: Decision-history transition — 2026-10-20
- [dev/records/migrations/dev-reference-transition-2026-10-20.md](../../../dev/records/migrations/dev-reference-transition-2026-10-20.md)
  Label: Current-reference transition — 2026-10-20
- [dev/records/migrations/legacy-development-migration-2026-10-09.md](../../../dev/records/migrations/legacy-development-migration-2026-10-09.md)
  Label: Legacy development migration: retained evidence context
- [dev/records/migrations/migration_spatial_map_names.md](../../../dev/records/migrations/migration_spatial_map_names.md)
  Label: Migration: rule 1.11 figure names
- [dev/records/migrations/review-retirement-2026-10-20.md](../../../dev/records/migrations/review-retirement-2026-10-20.md)
  Label: Review directory retirement — 2026-10-20
- [dev/records/milestones/git-ref-inventory.md](../../../dev/records/milestones/git-ref-inventory.md)
  Label: Historical Git reference inventory
- [dev/records/milestones/p31/baseline_diffs.md](../../../dev/records/milestones/p31/baseline_diffs.md)
  Label: P3-1 baseline re-record — milestone diff evidence (commit 6)
- [dev/records/milestones/p31/design-run-observations.md](../../../dev/records/milestones/p31/design-run-observations.md)
  Label: Process observations — p31-experiment-structure
- [dev/records/milestones/p31/experiment-structure-design-review-record.md](../../../dev/records/milestones/p31/experiment-structure-design-review-record.md)
  Label: P3-1 — Experiment structure — design review record
- [dev/records/milestones/p31/experiment-structure-design.md](../../../dev/records/milestones/p31/experiment-structure-design.md)
  Label: P3-1 — Project/experiment structure — design
- [dev/records/milestones/p31/experiment-structure-intake.md](../../../dev/records/milestones/p31/experiment-structure-intake.md)
  Label: P3-1 — Project/experiment structure — design-run intake
- [dev/records/milestones/p31/experiment-structure-task-brief.md](../../../dev/records/milestones/p31/experiment-structure-task-brief.md)
  Label: Task Brief — P3-1 Experiment structure (implementation)
- [dev/records/milestones/p31/migration_experiment-structure.md](../../../dev/records/milestones/p31/migration_experiment-structure.md)
  Label: Migration — P3-1 experiment structure (old → new wf3 output layout)
- [dev/records/milestones/p31/phase-a-report.md](../../../dev/records/milestones/p31/phase-a-report.md)
  Label: Phase A report — pre-P31 baseline capture + commit 1
- [dev/records/milestones/p31/phase-b-report.md](../../../dev/records/milestones/p31/phase-b-report.md)
  Label: Phase B report — commits 2–4
- [dev/records/milestones/p31/phase-c-report.md](../../../dev/records/milestones/p31/phase-c-report.md)
  Label: Phase C report — commits 5–7 + milestone gate
- [dev/records/milestones/p32a/baseline_diffs.md](../../../dev/records/milestones/p32a/baseline_diffs.md)
  Label: P3-2a baseline record — characterized diff (comparison ladder) + manifest confirm
- [dev/records/milestones/p32a/climate-analysis-design-review-record.md](../../../dev/records/milestones/p32a/climate-analysis-design-review-record.md)
  Label: P3-2a climate-analysis design — consolidated review record
- [dev/records/milestones/p32a/climate-analysis-design.md](../../../dev/records/milestones/p32a/climate-analysis-design.md)
  Label: P3-2a — Model-Independent Climate Analysis: Design (ACCEPTED)
- [dev/records/milestones/p32a/climate-analysis-intake.md](../../../dev/records/milestones/p32a/climate-analysis-intake.md)
  Label: P3-2a — Model-independent climate analysis — scoping intake
- [dev/records/milestones/p32a/climate-analysis-task-brief.md](../../../dev/records/milestones/p32a/climate-analysis-task-brief.md)
  Label: Task Brief — P3-2a Model-independent climate analysis (implementation)
- [dev/records/milestones/p32a/design-run-observations.md](../../../dev/records/milestones/p32a/design-run-observations.md)
  Label: Process observations — p32a-climate-analysis design run
- [dev/records/milestones/p32a/migration_climate-analysis.md](../../../dev/records/milestones/p32a/migration_climate-analysis.md)
  Label: P3-2a migration note — climate_analysis module map
- [dev/records/milestones/p32a/qa/ladder_tables.md](../../../dev/records/milestones/p32a/qa/ladder_tables.md)
  Label: P3-2a ladder tables (era5, era5_20000101_20201231)
- [dev/records/milestones/p32b/climate-interchange-intake.md](../../../dev/records/milestones/p32b/climate-interchange-intake.md)
  Label: P3-2b — Model-swap interchange contracts — scoping intake
- [dev/records/milestones/p32b/interchange-contracts-design-review-record.md](../../../dev/records/milestones/p32b/interchange-contracts-design-review-record.md)
  Label: P3-2b — Interchange contracts design: consolidated review record
- [dev/records/milestones/p32b/interchange-contracts-design.md](../../../dev/records/milestones/p32b/interchange-contracts-design.md)
  Label: P3-2b — Model-swap interchange contracts: Design (ACCEPTED)
- [dev/records/milestones/p32b/interchange-contracts-task-brief.md](../../../dev/records/milestones/p32b/interchange-contracts-task-brief.md)
  Label: Task Brief — P3-2b Model-swap interchange contracts (implementation)
- [dev/records/milestones/p33/batching-results.md](../../../dev/records/milestones/p33/batching-results.md)
  Label: P3-3 — batching results + GN-1..4 adjudication (commit 2)
- [dev/records/milestones/p33/performance-baseline.md](../../../dev/records/milestones/p33/performance-baseline.md)
  Label: P3-3 — wf3 performance baseline (commit 1)
- [dev/records/milestones/p33/performance-passes-design-review-record.md](../../../dev/records/milestones/p33/performance-passes-design-review-record.md)
  Label: P3-3 — Performance-passes design: consolidated review record
- [dev/records/milestones/p33/performance-passes-design.md](../../../dev/records/milestones/p33/performance-passes-design.md)
  Label: P3-3 — Performance passes: Design (ACCEPTED)
- [dev/records/milestones/p33/performance-passes-intake.md](../../../dev/records/milestones/p33/performance-passes-intake.md)
  Label: P3-3 — Performance passes — scoping intake
- [dev/records/milestones/p33/performance-passes-task-brief.md](../../../dev/records/milestones/p33/performance-passes-task-brief.md)
  Label: Task Brief — P3-3 Performance passes (implementation)
- [dev/records/milestones/p33/probes/_batch_dryrun_demo.txt](../../../dev/records/milestones/p33/probes/_batch_dryrun_demo.txt)
  Label: _batch_dryrun_demo (filename label)
- [dev/records/milestones/p33/probes/_batched_sweep_wall.txt](../../../dev/records/milestones/p33/probes/_batched_sweep_wall.txt)
  Label: P3-3 wf3 sweep wall measurements. Frozen §5.6 triple unless stated: -c 3 / --threads 4.
- [dev/records/milestones/p33/probes/_c2_batching/dryrun_demonstration.txt](../../../dev/records/milestones/p33/probes/_c2_batching/dryrun_demonstration.txt)
  Label: P3-3 commit-2 arbitration-mandated dry-run demonstration (design §9)
- [dev/records/milestones/p33/probes/_estimator_table.txt](../../../dev/records/milestones/p33/probes/_estimator_table.txt)
  Label: LPT makespan table (K=12, p=3, S_cold=208, S_warm=124)
- [dev/records/milestones/p33/probes/_forceall_dryrun.txt](../../../dev/records/milestones/p33/probes/_forceall_dryrun.txt)
  Label: _forceall_dryrun (filename label)
- [dev/records/milestones/p33/probes/_forcerun_dryrun.txt](../../../dev/records/milestones/p33/probes/_forcerun_dryrun.txt)
  Label: _forcerun_dryrun (filename label)
- [dev/records/milestones/p33/probes/PROBE_RESULTS.md](../../../dev/records/milestones/p33/probes/PROBE_RESULTS.md)
  Label: P3-3 probe results (raw record)
- [dev/records/milestones/phase-1/m01/setup.md](../../../dev/records/milestones/phase-1/m01/setup.md)
  Label: M1 setup
- [dev/records/milestones/phase-1/m01/warnings.md](../../../dev/records/milestones/phase-1/m01/warnings.md)
  Label: M1 warnings triage
- [dev/records/milestones/phase-1/m02/decisions.md](../../../dev/records/milestones/phase-1/m02/decisions.md)
  Label: M2 design decisions
- [dev/records/milestones/phase-1/m02b/audit.md](../../../dev/records/milestones/phase-1/m02b/audit.md)
  Label: M2b — Library upgrade audit
- [dev/records/milestones/phase-1/m02b/baseline_diffs.md](../../../dev/records/milestones/phase-1/m02b/baseline_diffs.md)
  Label: M2b — Baseline drift report
- [dev/records/milestones/phase-1/m02b/check_before_record.txt](../../../dev/records/milestones/phase-1/m02b/check_before_record.txt)
  Label: check_before_record (filename label)
- [dev/records/milestones/phase-1/m02b/handoff.md](../../../dev/records/milestones/phase-1/m02b/handoff.md)
  Label: M2b — Mid-flight handoff
- [dev/records/milestones/phase-1/m02b/package_inventory.md](../../../dev/records/milestones/phase-1/m02b/package_inventory.md)
  Label: Package inventory (M2b)
- [dev/records/milestones/phase-1/m02b/plan.md](../../../dev/records/milestones/phase-1/m02b/plan.md)
  Label: M2b — Library upgrade execution plan
- [dev/records/milestones/phase-1/m02c/test-coverage-design.md](../../../dev/records/milestones/phase-1/m02c/test-coverage-design.md)
  Label: M02c — Test coverage (pre-M3) — design
- [dev/records/milestones/phase-1/m02c/test-coverage-plan.md](../../../dev/records/milestones/phase-1/m02c/test-coverage-plan.md)
  Label: M02c Test Coverage Implementation Plan
- [dev/records/milestones/post-r12/migration_config-snapshots.md](../../../dev/records/milestones/post-r12/migration_config-snapshots.md)
  Label: Migration — config snapshots nest under their workflow, and WF3/WF4 gain one
- [dev/records/milestones/post-r12/migration_domain-rule-names.md](../../../dev/records/milestones/post-r12/migration_domain-rule-names.md)
  Label: Migration: domain rule names and contiguous numbers (2026-09-24)
- [dev/records/milestones/post-r12/migration_named-indicator-sets.md](../../../dev/records/milestones/post-r12/migration_named-indicator-sets.md)
  Label: Migration — named WF4 indicator sets and metric-set/4
- [dev/records/milestones/post-r12/migration_scenario-tree.md](../../../dev/records/milestones/post-r12/migration_scenario-tree.md)
  Label: Migration — the scenario tree, short digest path segments, and the WF0 plot scales
- [dev/records/milestones/post-r12/migration_wf3-generation-rules.md](../../../dev/records/milestones/post-r12/migration_wf3-generation-rules.md)
  Label: Migration: WF3 generation rule names (2026-09-24)
- [dev/records/milestones/post-r12/migration-project-tree.md](../../../dev/records/milestones/post-r12/migration-project-tree.md)
  Label: Migration — the scenario tree moves, and digest directories get shorter
- [dev/records/milestones/post-r12/migration-structured-metrics.md](../../../dev/records/milestones/post-r12/migration-structured-metrics.md)
  Label: Structured metric sets and historical inspection
- [dev/records/milestones/post-r12/output-schema/complete-run-output-schema.md](../../../dev/records/milestones/post-r12/output-schema/complete-run-output-schema.md)
  Label: Complete-run output tree and record schemas — accepted P0 contract
- [dev/records/milestones/post-r12/output-schema/implementation/master-brief.md](../../../dev/records/milestones/post-r12/output-schema/implementation/master-brief.md)
  Label: Master Brief — Complete-run output schema migration
- [dev/records/milestones/post-r12/output-schema/implementation/p1-archive-foundation.md](../../../dev/records/milestones/post-r12/output-schema/implementation/p1-archive-foundation.md)
  Label: Task Brief — P1 Archive foundation
- [dev/records/milestones/post-r12/output-schema/implementation/p2-workflow-archives.md](../../../dev/records/milestones/post-r12/output-schema/implementation/p2-workflow-archives.md)
  Label: Task Brief — P2 Workflow archives
- [dev/records/milestones/post-r12/output-schema/implementation/p3-invocation-history.md](../../../dev/records/milestones/post-r12/output-schema/implementation/p3-invocation-history.md)
  Label: Task Brief — P3 Invocation history
- [dev/records/milestones/post-r12/output-schema/implementation/p4-collection-contract.md](../../../dev/records/milestones/post-r12/output-schema/implementation/p4-collection-contract.md)
  Label: Task Brief — P4 Collection contract
- [dev/records/milestones/post-r12/output-schema/implementation/p4-handoff.md](../../../dev/records/milestones/post-r12/output-schema/implementation/p4-handoff.md)
  Label: P4 handoff — additive collection contract
- [dev/records/milestones/post-r12/output-schema/implementation/p5-wf3-static-generation.md](../../../dev/records/milestones/post-r12/output-schema/implementation/p5-wf3-static-generation.md)
  Label: Task Brief — P5 WF3 static generation
- [dev/records/milestones/post-r12/output-schema/implementation/p6-simulation-metrics.md](../../../dev/records/milestones/post-r12/output-schema/implementation/p6-simulation-metrics.md)
  Label: Task Brief — P6 Simulation and metrics
- [dev/records/milestones/post-r12/output-schema/implementation/p7-complete-run-evidence.md](../../../dev/records/milestones/post-r12/output-schema/implementation/p7-complete-run-evidence.md)
  Label: Task Brief — P7 Complete-run evidence
- [dev/records/milestones/post-r12/output-schema/README.md](../../../dev/records/milestones/post-r12/output-schema/README.md)
  Label: Complete-run output-schema evidence
- [dev/records/milestones/post-r12/output-schema/review/design-v1.md](../../../dev/records/milestones/post-r12/output-schema/review/design-v1.md)
  Label: Complete-run output tree and record schemas — P0 contract, design v1
- [dev/records/milestones/post-r12/output-schema/review/design-v2.md](../../../dev/records/milestones/post-r12/output-schema/review/design-v2.md)
  Label: Complete-run output tree and record schemas — P0 contract, design v2
- [dev/records/milestones/post-r12/output-schema/review/design-v3.md](../../../dev/records/milestones/post-r12/output-schema/review/design-v3.md)
  Label: Complete-run output tree and record schemas — P0 contract, design v3
- [dev/records/milestones/post-r12/output-schema/review/external-review-r1.md](../../../dev/records/milestones/post-r12/output-schema/review/external-review-r1.md)
  Label: external-review-r1 (filename label)
- [dev/records/milestones/post-r12/output-schema/review/intake.md](../../../dev/records/milestones/post-r12/output-schema/review/intake.md)
  Label: Output schema contract review — intake
- [dev/records/milestones/post-r12/output-schema/review/internal-review-architecture.md](../../../dev/records/milestones/post-r12/output-schema/review/internal-review-architecture.md)
  Label: internal-review-architecture (filename label)
- [dev/records/milestones/post-r12/output-schema/review/internal-review-domain.md](../../../dev/records/milestones/post-r12/output-schema/review/internal-review-domain.md)
  Label: internal-review-domain (filename label)
- [dev/records/milestones/post-r12/output-schema/review/internal-review-index.md](../../../dev/records/milestones/post-r12/output-schema/review/internal-review-index.md)
  Label: P0 internal review index — design-v1.md
- [dev/records/milestones/post-r12/output-schema/review/internal-review-repo-fit.md](../../../dev/records/milestones/post-r12/output-schema/review/internal-review-repo-fit.md)
  Label: internal-review-repo-fit (filename label)
- [dev/records/milestones/post-r12/output-schema/review/internal-review-risk.md](../../../dev/records/milestones/post-r12/output-schema/review/internal-review-risk.md)
  Label: internal-review-risk (filename label)
- [dev/records/milestones/post-r12/output-schema/review/ledger.md](../../../dev/records/milestones/post-r12/output-schema/review/ledger.md)
  Label: P0 revision ledger
- [dev/records/milestones/post-r12/output-schema/review/observations.md](../../../dev/records/milestones/post-r12/output-schema/review/observations.md)
  Label: Review process observations
- [dev/records/milestones/post-r12/output-schema/review/p1-review.md](../../../dev/records/milestones/post-r12/output-schema/review/p1-review.md)
  Label: P1 focused code review
- [dev/records/milestones/post-r12/output-schema/review/p5-exclusion-matrix.md](../../../dev/records/milestones/post-r12/output-schema/review/p5-exclusion-matrix.md)
  Label: P5 excluded-field empirical matrix
- [dev/records/milestones/post-r12/output-schema/review/p5-implementation-evidence.md](../../../dev/records/milestones/post-r12/output-schema/review/p5-implementation-evidence.md)
  Label: P5 WF3 static generation evidence
- [dev/records/milestones/post-r12/output-schema/review/p5-scientific-validation.md](../../../dev/records/milestones/post-r12/output-schema/review/p5-scientific-validation.md)
  Label: P5 scientific continuity — matched explicit seed
- [dev/records/milestones/post-r12/output-schema/review/prechange-reference-probes.md](../../../dev/records/milestones/post-r12/output-schema/review/prechange-reference-probes.md)
  Label: Pre-change WF3 reference: execution probes
- [dev/records/milestones/post-r12/output-schema/review/prechange-reference-retry.md](../../../dev/records/milestones/post-r12/output-schema/review/prechange-reference-retry.md)
  Label: Clean pre-change WF3 scientific reference
- [dev/records/milestones/post-r12/output-schema/review/prechange-zero-change-reference.md](../../../dev/records/milestones/post-r12/output-schema/review/prechange-zero-change-reference.md)
  Label: Pre-change zero-change perturbation reference
- [dev/records/milestones/post-r12/output-schema/review/predecessor-wf4-comparator.md](../../../dev/records/milestones/post-r12/output-schema/review/predecessor-wf4-comparator.md)
  Label: Independent predecessor WF1/WF4 comparator
- [dev/records/milestones/post-r12/output-schema/review/predecessor-wf4-pin.md](../../../dev/records/milestones/post-r12/output-schema/review/predecessor-wf4-pin.md)
  Label: Predecessor WF4 executable pin (before P1 runtime edits)
- [dev/records/milestones/post-r12/output-schema/review/review-brief.md](../../../dev/records/milestones/post-r12/output-schema/review/review-brief.md)
  Label: Independent headless review brief — P0 output schema
- [dev/records/milestones/post-r12/output-schema/review/scoped-review-v3.md](../../../dev/records/milestones/post-r12/output-schema/review/scoped-review-v3.md)
  Label: Scoped verification of design v3
- [dev/records/milestones/post-r12/output-schema/review/status.md](../../../dev/records/milestones/post-r12/output-schema/review/status.md)
  Label: status (filename label)
- [dev/records/milestones/post-r12/wf3-generation-bundle-plan.md](../../../dev/records/milestones/post-r12/wf3-generation-bundle-plan.md)
  Label: WF3 generation bundle — implementation plan
- [dev/records/milestones/r01/baseline_diffs.md](../../../dev/records/milestones/r01/baseline_diffs.md)
  Label: R01 baseline diffs
- [dev/records/milestones/r01/local-config-migration.md](../../../dev/records/milestones/r01/local-config-migration.md)
  Label: Migrating a local snake config to R01 sectioned schema
- [dev/records/milestones/r01/modularity-contracts-design.md](../../../dev/records/milestones/r01/modularity-contracts-design.md)
  Label: R01 — Modularity Contracts (pre-R3) — design
- [dev/records/milestones/r01/modularity-contracts-plan.md](../../../dev/records/milestones/r01/modularity-contracts-plan.md)
  Label: R01 Modularity Contracts Implementation Plan
- [dev/records/milestones/r01/modularity-contracts-review-gpt-20260717.md](../../../dev/records/milestones/r01/modularity-contracts-review-gpt-20260717.md)
  Label: R01 plan review — GPT-5.6 (2026-07-17)
- [dev/records/milestones/r01/modularity-contracts-review.md](../../../dev/records/milestones/r01/modularity-contracts-review.md)
  Label: Roadmap and R01 Review
- [dev/records/milestones/r02/naming-conventions-design.md](../../../dev/records/milestones/r02/naming-conventions-design.md)
  Label: R02 — Naming conventions (pre-R3) — design
- [dev/records/milestones/r02/naming-conventions-review-fable-20260719.md](../../../dev/records/milestones/r02/naming-conventions-review-fable-20260719.md)
  Label: R02 revised-design review — Fable (2026-07-19)
- [dev/records/milestones/r02/naming-conventions-review-gpt-20260718.md](../../../dev/records/milestones/r02/naming-conventions-review-gpt-20260718.md)
  Label: R02 design review — GPT-5.6 (2026-07-18)
- [dev/records/milestones/r02/naming-conventions-review.md](../../../dev/records/milestones/r02/naming-conventions-review.md)
  Label: R02 Naming Conventions Review
- [dev/records/milestones/r03/integration-verification.md](../../../dev/records/milestones/r03/integration-verification.md)
  Label: R3 — deferred integration verification (before seal)
- [dev/records/milestones/r03/model-builder-design-review-gpt-20260719.md](../../../dev/records/milestones/r03/model-builder-design-review-gpt-20260719.md)
  Label: R03 design review — GPT-5.6 (2026-07-19)
- [dev/records/milestones/r03/model-builder-design.md](../../../dev/records/milestones/r03/model-builder-design.md)
  Label: R03 — Workflow 1: model builder — design
- [dev/records/milestones/r04/baseline_diffs.md](../../../dev/records/milestones/r04/baseline_diffs.md)
  Label: R04 baseline diffs
- [dev/records/milestones/r04/chain-audit.md](../../../dev/records/milestones/r04/chain-audit.md)
  Label: R04 change-factor chain audit — findings
- [dev/records/milestones/r04/climate_projections.md](../../../dev/records/milestones/r04/climate_projections.md)
  Label: Workflow: climate_projections
- [dev/records/milestones/r04/climate-projections-design-reviews.md](../../../dev/records/milestones/r04/climate-projections-design-reviews.md)
  Label: R04 climate-projections design — review record
- [dev/records/milestones/r04/climate-projections-design.md](../../../dev/records/milestones/r04/climate-projections-design.md)
  Label: R04 — Workflow 2: climate projections — design
- [dev/records/milestones/r05/climate_experiment.md](../../../dev/records/milestones/r05/climate_experiment.md)
  Label: Workflow: climate_experiment
- [dev/records/milestones/r05/climate-experiment-design-reviews.md](../../../dev/records/milestones/r05/climate-experiment-design-reviews.md)
  Label: R05 climate-experiment design — review record
- [dev/records/milestones/r05/climate-experiment-design.md](../../../dev/records/milestones/r05/climate-experiment-design.md)
  Label: R05 — Workflow 3: climate experiment — design
- [dev/records/milestones/r06/migration_structural-refactor.md](../../../dev/records/milestones/r06/migration_structural-refactor.md)
  Label: R06 — structural refactor — internal rename record
- [dev/records/milestones/r06/structural-refactor-design-review-record.md](../../../dev/records/milestones/r06/structural-refactor-design-review-record.md)
  Label: R06 structural-refactor — consolidated design-review record
- [dev/records/milestones/r06/structural-refactor-design.md](../../../dev/records/milestones/r06/structural-refactor-design.md)
  Label: R06 — Structural refactor — design
- [dev/records/milestones/r06/structural-refactor-task-brief.md](../../../dev/records/milestones/r06/structural-refactor-task-brief.md)
  Label: Task Brief — R06 Structural refactor (implementation)
- [dev/records/milestones/r07/2026-07-26_project-output-layout.md](../../../dev/records/milestones/r07/2026-07-26_project-output-layout.md)
  Label: Project output layout — proposal for review
- [dev/records/milestones/r07/migration_project-layout.md](../../../dev/records/milestones/r07/migration_project-layout.md)
  Label: Migration — R07 project layout (old → new)
- [dev/records/milestones/r07/project-layout-design-review-record.md](../../../dev/records/milestones/r07/project-layout-design-review-record.md)
  Label: R07 — Project layout — design review record
- [dev/records/milestones/r07/project-layout-design.md](../../../dev/records/milestones/r07/project-layout-design.md)
  Label: R07 — Project layout — design
- [dev/records/milestones/r07/project-layout-intake.md](../../../dev/records/milestones/r07/project-layout-intake.md)
  Label: R07 — Project layout — design-review intake
- [dev/records/milestones/r07/project-layout-task-brief.md](../../../dev/records/milestones/r07/project-layout-task-brief.md)
  Label: project-layout-task-brief (filename label)
- [dev/records/milestones/r08/2026-07-29_wf2-step1-validation.md](../../../dev/records/milestones/r08/2026-07-29_wf2-step1-validation.md)
  Label: WF2 v2.0 step 1 — validation record
- [dev/records/milestones/r08/2026-07-29_wf2-v2-decouple-and-cache.md](../../../dev/records/milestones/r08/2026-07-29_wf2-v2-decouple-and-cache.md)
  Label: Task Brief — WF2 v2.0 steps 1 / 2a / 2b: model-free region + persistent series cache
- [dev/records/milestones/r08/2026-07-30_wf2-5a-falsifier.md](../../../dev/records/milestones/r08/2026-07-30_wf2-5a-falsifier.md)
  Label: Falsifier — step 5a, spherical cell-area weighting (D10)
- [dev/records/milestones/r08/2026-07-30_wf2-5b-calendar-blocker.md](../../../dev/records/milestones/r08/2026-07-30_wf2-5b-calendar-blocker.md)
  Label: BLOCKER — the pipeline replaces the model calendar with a false one
- [dev/records/milestones/r08/2026-07-30_wf2-5b-falsifier.md](../../../dev/records/milestones/r08/2026-07-30_wf2-5b-falsifier.md)
  Label: Falsifier — step 5b, calendar-aware month-length weighting
- [dev/records/milestones/r08/2026-07-30_wf2-5c-falsifier.md](../../../dev/records/milestones/r08/2026-07-30_wf2-5c-falsifier.md)
  Label: Falsifier — step 5c, drop the stage-A 2-decimal rounding
- [dev/records/milestones/r08/2026-07-30_wf2-5d-falsifier.md](../../../dev/records/milestones/r08/2026-07-30_wf2-5d-falsifier.md)
  Label: Falsifier — step 5d, default statistic set
- [dev/records/milestones/r08/2026-07-30_wf2-5e-falsifier.md](../../../dev/records/milestones/r08/2026-07-30_wf2-5e-falsifier.md)
  Label: Falsifier — step 5e (three changes, one migration row)
- [dev/records/milestones/r08/2026-07-30_wf2-5f-hydyear-offbyone.md](../../../dev/records/milestones/r08/2026-07-30_wf2-5f-hydyear-offbyone.md)
  Label: BLOCKER — the reference window is one hydrological year short (January starts)
- [dev/records/milestones/r08/2026-07-30_wf2-fetch-reduce-benchmark.md](../../../dev/records/milestones/r08/2026-07-30_wf2-fetch-reduce-benchmark.md)
  Label: Benchmark — fetch vs reduce, and the store-read asymmetry
- [dev/records/milestones/r08/2026-07-30_wf2-hydyear-fix-falsifier.md](../../../dev/records/milestones/r08/2026-07-30_wf2-hydyear-fix-falsifier.md)
  Label: Falsifier — the hydrological-year off-by-one fix (option A)
- [dev/records/milestones/r08/2026-07-30_wf2-kernel-hash-repair-validation.md](../../../dev/records/milestones/r08/2026-07-30_wf2-kernel-hash-repair-validation.md)
  Label: Validation record — cache-guard repair + the plot-job deadlock
- [dev/records/milestones/r08/2026-07-30_wf2-r8-handoff.md](../../../dev/records/milestones/r08/2026-07-30_wf2-r8-handoff.md)
  Label: Handoff — WF2 v2.0 (Phase 5 / R8), resume point
- [dev/records/milestones/r08/2026-07-30_wf2-step2b-validation.md](../../../dev/records/milestones/r08/2026-07-30_wf2-step2b-validation.md)
  Label: WF2 v2.0 step 2b — validation record
- [dev/records/milestones/r08/2026-07-31_wf2-6a-falsifier.md](../../../dev/records/milestones/r08/2026-07-31_wf2-6a-falsifier.md)
  Label: Falsifier — step 6a (three commits: tidy annual table, monthly table, provenance)
- [dev/records/milestones/r08/2026-07-31_wf2-6b-falsifier.md](../../../dev/records/milestones/r08/2026-07-31_wf2-6b-falsifier.md)
  Label: Falsifier — step 6b, the dry-month rule (A2)
- [dev/records/milestones/r08/2026-07-31_wf2-6c-falsifier.md](../../../dev/records/milestones/r08/2026-07-31_wf2-6c-falsifier.md)
  Label: Falsifier — step 6c, remove cross-combination statistics (R3′/R3″)
- [dev/records/milestones/r08/2026-07-31_wf2-7-falsifier.md](../../../dev/records/milestones/r08/2026-07-31_wf2-7-falsifier.md)
  Label: Falsifier — step 7, the report stage
- [dev/records/milestones/r08/cmip6-readability-measurements.md](../../../dev/records/milestones/r08/cmip6-readability-measurements.md)
  Label: WF2 — which CMIP6 stores this toolbox can read
- [dev/records/milestones/r08/migration-wf2.md](../../../dev/records/milestones/r08/migration-wf2.md)
  Label: Migration — workflow 2 (R8, `v2.0` of the climate-projections workflow)
- [dev/records/milestones/r08/wf2-climate-analysis-v2-design-review-record.md](../../../dev/records/milestones/r08/wf2-climate-analysis-v2-design-review-record.md)
  Label: WF2 v2.0 design — consolidated review record
- [dev/records/milestones/r08/wf2-climate-analysis-v2-design.md](../../../dev/records/milestones/r08/wf2-climate-analysis-v2-design.md)
  Label: WF2 v2.0 — GCM Projections Analysis: Design (ACCEPTED)
- [dev/records/milestones/r08/wf2-cmip6-store-inventory.md](../../../dev/records/milestones/r08/wf2-cmip6-store-inventory.md)
  Label: WF2 — inventory of the Google Cloud CMIP6 store
- [dev/records/milestones/r09/2026-08-04_p1-declared-tier-falsifier.md](../../../dev/records/milestones/r09/2026-08-04_p1-declared-tier-falsifier.md)
  Label: R9 P1 falsifier — the path map against the declared-tier inventory
- [dev/records/milestones/r09/closing-record.md](../../../dev/records/milestones/r09/closing-record.md)
  Label: R9 closing record — the generated project tree
- [dev/records/milestones/r09/declared_inventory.txt](../../../dev/records/milestones/r09/declared_inventory.txt)
  Label: R09 declared-tier inventory --- the paths the three Snakefiles' `output:`
- [dev/records/milestones/r09/followup-provenance-root-task-brief.md](../../../dev/records/milestones/r09/followup-provenance-root-task-brief.md)
  Label: followup-provenance-root-task-brief (filename label)
- [dev/records/milestones/r09/followup-stale-path-prose-task-brief.md](../../../dev/records/milestones/r09/followup-stale-path-prose-task-brief.md)
  Label: followup-stale-path-prose-task-brief (filename label)
- [dev/records/milestones/r09/gate-closure-run-plan.md](../../../dev/records/milestones/r09/gate-closure-run-plan.md)
  Label: gate-closure-run-plan (filename label)
- [dev/records/milestones/r09/landing-gate.md](../../../dev/records/milestones/r09/landing-gate.md)
  Label: R9 landing gate — presentation
- [dev/records/milestones/r09/migration_indicator-axis-columns.md](../../../dev/records/milestones/r09/migration_indicator-axis-columns.md)
  Label: Migration — indicator-table axis columns (R9 followup)
- [dev/records/milestones/r09/migration_project-tree.md](../../../dev/records/milestones/r09/migration_project-tree.md)
  Label: Migration — project tree (R9)
- [dev/records/milestones/r09/observed_inventory.txt](../../../dev/records/milestones/r09/observed_inventory.txt)
  Label: Project-tree snapshot --- a sorted list of project-relative paths.
- [dev/records/milestones/r09/observed-tier-runbook.md](../../../dev/records/milestones/r09/observed-tier-runbook.md)
  Label: Runbook — producing the R9 observed-tier snapshot
- [dev/records/milestones/r09/orphan-sweep-2026-08-05.txt](../../../dev/records/milestones/r09/orphan-sweep-2026-08-05.txt)
  Label: R9 orphan sweep of test_case/test_local -- 2026-08-05
- [dev/records/milestones/r09/phase-1-comparator-task-brief.md](../../../dev/records/milestones/r09/phase-1-comparator-task-brief.md)
  Label: phase-1-comparator-task-brief (filename label)
- [dev/records/milestones/r09/phase-1-report.md](../../../dev/records/milestones/r09/phase-1-report.md)
  Label: R9 P1 report — path-map comparator and orphan-store tooling
- [dev/records/milestones/r09/phase-2-report.md](../../../dev/records/milestones/r09/phase-2-report.md)
  Label: R9 P2 report — migrate the generated tree
- [dev/records/milestones/r09/phase-2-tree-migration-task-brief.md](../../../dev/records/milestones/r09/phase-2-tree-migration-task-brief.md)
  Label: phase-2-tree-migration-task-brief (filename label)
- [dev/records/milestones/r09/phase-3-report.md](../../../dev/records/milestones/r09/phase-3-report.md)
  Label: R9 P3 report — result tables, rule 3.11, and the single baseline re-record
- [dev/records/milestones/r09/phase-3-result-tables-task-brief.md](../../../dev/records/milestones/r09/phase-3-result-tables-task-brief.md)
  Label: phase-3-result-tables-task-brief (filename label)
- [dev/records/milestones/r09/phase-4-commit-4-task-brief.md](../../../dev/records/milestones/r09/phase-4-commit-4-task-brief.md)
  Label: phase-4-commit-4-task-brief (filename label)
- [dev/records/milestones/r09/phase-4-fingerprint-task-brief.md](../../../dev/records/milestones/r09/phase-4-fingerprint-task-brief.md)
  Label: phase-4-fingerprint-task-brief (filename label)
- [dev/records/milestones/r09/phase-4-report.md](../../../dev/records/milestones/r09/phase-4-report.md)
  Label: R9 P4 report — model fingerprint and experiment lifecycle
- [dev/records/milestones/r09/phase-5-conventions-docs-task-brief.md](../../../dev/records/milestones/r09/phase-5-conventions-docs-task-brief.md)
  Label: phase-5-conventions-docs-task-brief (filename label)
- [dev/records/milestones/r09/phase-5-report.md](../../../dev/records/milestones/r09/phase-5-report.md)
  Label: R9 P5 report — conventions and documentation
- [dev/records/milestones/r09/project-tree-design.md](../../../dev/records/milestones/r09/project-tree-design.md)
  Label: BlueEarth CST project folder tree — owner-accepted design proposal
- [dev/records/milestones/r09/project-tree-task-brief.md](../../../dev/records/milestones/r09/project-tree-task-brief.md)
  Label: project-tree-task-brief (filename label)
- [dev/records/milestones/r09/wf1-spatial-decoupling/master-task-brief.md](../../../dev/records/milestones/r09/wf1-spatial-decoupling/master-task-brief.md)
  Label: Master Brief — WF1 spatial foundation and Wflow build split
- [dev/records/milestones/r09/wf1-spatial-decoupling/phase-1-report.md](../../../dev/records/milestones/r09/wf1-spatial-decoupling/phase-1-report.md)
  Label: Phase 1 report — engine-neutral spatial foundation
- [dev/records/milestones/r09/wf1-spatial-decoupling/phase-1-spatial-maps-task-brief.md](../../../dev/records/milestones/r09/wf1-spatial-decoupling/phase-1-spatial-maps-task-brief.md)
  Label: Task Brief — P1 engine-neutral spatial maps
- [dev/records/milestones/r09/wf1-spatial-decoupling/phase-2-report.md](../../../dev/records/milestones/r09/wf1-spatial-decoupling/phase-2-report.md)
  Label: Phase 2 report — Wflow-SBM build from the spatial foundation
- [dev/records/milestones/r09/wf1-spatial-decoupling/phase-2-wflow-build-task-brief.md](../../../dev/records/milestones/r09/wf1-spatial-decoupling/phase-2-wflow-build-task-brief.md)
  Label: Task Brief — P2 Wflow-SBM model build from spatial products
- [dev/records/milestones/r09/wf3-change-requests.md](../../../dev/records/milestones/r09/wf3-change-requests.md)
  Label: WF3 change requests
- [dev/records/milestones/r09/wf3-changes-proposal.md](../../../dev/records/milestones/r09/wf3-changes-proposal.md)
  Label: Proposal: changes to Workflow 3 (the climate stress test)
- [dev/records/milestones/r10/migration_rule-names.md](../../../dev/records/milestones/r10/migration_rule-names.md)
  Label: Migration — Snakemake rule identifiers (R10)
- [dev/records/milestones/r10/rule-naming-design.md](../../../dev/records/milestones/r10/rule-naming-design.md)
  Label: Snakemake rule naming — R10 design
- [dev/records/milestones/r10/rule-numbering-crosswalks.md](../../../dev/records/milestones/r10/rule-numbering-crosswalks.md)
  Label: Historical rule-numbering crosswalks
- [dev/records/milestones/r10/spatial-units-split-task-brief.md](../../../dev/records/milestones/r10/spatial-units-split-task-brief.md)
  Label: Task Brief — split `prepare_spatial_maps` so WF2/WF3 can consume basin boundaries
- [dev/records/milestones/r10/step6-rule-surface-task-brief.md](../../../dev/records/milestones/r10/step6-rule-surface-task-brief.md)
  Label: Task Brief — R10 step 6: settle the rule identifier surface
- [dev/records/milestones/r11/c34-weathergenr-argument-decisions.md](../../../dev/records/milestones/r11/c34-weathergenr-argument-decisions.md)
  Label: C34 — one recorded decision per unpassed weathergenr argument
- [dev/records/milestones/r11/migration_indicator-tables.md](../../../dev/records/milestones/r11/migration_indicator-tables.md)
  Label: Migration — WF3 indicator tables, wide → long (R11 P1)
- [dev/records/milestones/r11/phase-1-result-tables-task-brief.md](../../../dev/records/milestones/r11/phase-1-result-tables-task-brief.md)
  Label: Task Brief — R11 P1: WF3 result tables, wide → long
- [dev/records/milestones/r11/phase-2-results-delta.md](../../../dev/records/milestones/r11/phase-2-results-delta.md)
  Label: R11 P2 — results delta, for P3's re-record
- [dev/records/milestones/r11/phase-2-run-identification-task-brief.md](../../../dev/records/milestones/r11/phase-2-run-identification-task-brief.md)
  Label: Task Brief — R11 P2: run identification, the design table, and `st_id`
- [dev/records/milestones/r11/phase-3-rerecord-task-brief.md](../../../dev/records/milestones/r11/phase-3-rerecord-task-brief.md)
  Label: Task Brief — R11 P3: the runbook, `[R10-13]`, and the single re-record
- [dev/records/milestones/r11/phase-3-run-report.md](../../../dev/records/milestones/r11/phase-3-run-report.md)
  Label: R11 P3 — run report
- [dev/records/milestones/r11/wf3-consolidation-scope.md](../../../dev/records/milestones/r11/wf3-consolidation-scope.md)
  Label: R11 — WF3 artifact and identification consolidation (SCOPE)
- [dev/records/milestones/r12/g2-assessment.md](../../../dev/records/milestones/r12/g2-assessment.md)
  Label: R12 — G2 gate assessment
- [dev/records/milestones/r12/gf15-alternative-estimator-design.md](../../../dev/records/milestones/r12/gf15-alternative-estimator-design.md)
  Label: Method Spec — GF15 alternative GEV estimator
- [dev/records/milestones/r12/gf15-alternative-estimator-review/design-v1.md](../../../dev/records/milestones/r12/gf15-alternative-estimator-review/design-v1.md)
  Label: Method Spec — GF15 alternative GEV estimator
- [dev/records/milestones/r12/gf15-alternative-estimator-review/design-v2.md](../../../dev/records/milestones/r12/gf15-alternative-estimator-review/design-v2.md)
  Label: Method Spec — GF15 alternative GEV estimator
- [dev/records/milestones/r12/gf15-alternative-estimator-review/design-v3.md](../../../dev/records/milestones/r12/gf15-alternative-estimator-review/design-v3.md)
  Label: Method Spec — GF15 alternative GEV estimator
- [dev/records/milestones/r12/gf15-alternative-estimator-review/design-v4.md](../../../dev/records/milestones/r12/gf15-alternative-estimator-review/design-v4.md)
  Label: Method Spec — GF15 alternative GEV estimator
- [dev/records/milestones/r12/gf15-alternative-estimator-review/external-review-r1.md](../../../dev/records/milestones/r12/gf15-alternative-estimator-review/external-review-r1.md)
  Label: external-review-r1 (filename label)
- [dev/records/milestones/r12/gf15-alternative-estimator-review/external-review-r2.md](../../../dev/records/milestones/r12/gf15-alternative-estimator-review/external-review-r2.md)
  Label: external-review-r2 (filename label)
- [dev/records/milestones/r12/gf15-alternative-estimator-review/intake.md](../../../dev/records/milestones/r12/gf15-alternative-estimator-review/intake.md)
  Label: GF15 alternative-estimator proposal intake
- [dev/records/milestones/r12/gf15-alternative-estimator-review/internal-review-architecture.md](../../../dev/records/milestones/r12/gf15-alternative-estimator-review/internal-review-architecture.md)
  Label: Architecture and internal-consistency review
- [dev/records/milestones/r12/gf15-alternative-estimator-review/internal-review-domain.md](../../../dev/records/milestones/r12/gf15-alternative-estimator-review/internal-review-domain.md)
  Label: Scientific review — design-v1.md
- [dev/records/milestones/r12/gf15-alternative-estimator-review/internal-review-index.md](../../../dev/records/milestones/r12/gf15-alternative-estimator-review/internal-review-index.md)
  Label: Internal review index — v1
- [dev/records/milestones/r12/gf15-alternative-estimator-review/internal-review-repo-fit.md](../../../dev/records/milestones/r12/gf15-alternative-estimator-review/internal-review-repo-fit.md)
  Label: Repo-fit review — frozen
- [dev/records/milestones/r12/gf15-alternative-estimator-review/internal-review-risk.md](../../../dev/records/milestones/r12/gf15-alternative-estimator-review/internal-review-risk.md)
  Label: internal-review-risk (filename label)
- [dev/records/milestones/r12/gf15-alternative-estimator-review/ledger.md](../../../dev/records/milestones/r12/gf15-alternative-estimator-review/ledger.md)
  Label: Findings ledger
- [dev/records/milestones/r12/gf15-alternative-estimator-review/observations.md](../../../dev/records/milestones/r12/gf15-alternative-estimator-review/observations.md)
  Label: Process observations
- [dev/records/milestones/r12/gf15-alternative-estimator-review/review-brief-r2.md](../../../dev/records/milestones/r12/gf15-alternative-estimator-review/review-brief-r2.md)
  Label: Independent external review — GF15 alternative estimator
- [dev/records/milestones/r12/gf15-alternative-estimator-review/review-brief.md](../../../dev/records/milestones/r12/gf15-alternative-estimator-review/review-brief.md)
  Label: Independent external review — GF15 alternative estimator
- [dev/records/milestones/r12/gf15-alternative-estimator-review/scoped-review-v4.md](../../../dev/records/milestones/r12/gf15-alternative-estimator-review/scoped-review-v4.md)
  Label: GF15 v4 scoped independent verification
- [dev/records/milestones/r12/gf15-alternative-estimator-review/status.md](../../../dev/records/milestones/r12/gf15-alternative-estimator-review/status.md)
  Label: status (filename label)
- [dev/records/milestones/r12/gf15-production-adapter-design.md](../../../dev/records/milestones/r12/gf15-production-adapter-design.md)
  Label: GF15 production adapter — decision record v3
- [dev/records/milestones/r12/gf15-production-adapter-review/design-v1.md](../../../dev/records/milestones/r12/gf15-production-adapter-review/design-v1.md)
  Label: GF15 production adapter — decision record v1
- [dev/records/milestones/r12/gf15-production-adapter-review/design-v2.md](../../../dev/records/milestones/r12/gf15-production-adapter-review/design-v2.md)
  Label: GF15 production adapter — decision record v2
- [dev/records/milestones/r12/gf15-production-adapter-review/design-v3.md](../../../dev/records/milestones/r12/gf15-production-adapter-review/design-v3.md)
  Label: GF15 production adapter — decision record v3
- [dev/records/milestones/r12/gf15-production-adapter-review/external-review-r1.md](../../../dev/records/milestones/r12/gf15-production-adapter-review/external-review-r1.md)
  Label: external-review-r1 (filename label)
- [dev/records/milestones/r12/gf15-production-adapter-review/intake.md](../../../dev/records/milestones/r12/gf15-production-adapter-review/intake.md)
  Label: GF15 production adapter — intake
- [dev/records/milestones/r12/gf15-production-adapter-review/internal-review-architecture.md](../../../dev/records/milestones/r12/gf15-production-adapter-review/internal-review-architecture.md)
  Label: internal-review-architecture (filename label)
- [dev/records/milestones/r12/gf15-production-adapter-review/internal-review-domain.md](../../../dev/records/milestones/r12/gf15-production-adapter-review/internal-review-domain.md)
  Label: internal-review-domain (filename label)
- [dev/records/milestones/r12/gf15-production-adapter-review/internal-review-index.md](../../../dev/records/milestones/r12/gf15-production-adapter-review/internal-review-index.md)
  Label: Internal review index
- [dev/records/milestones/r12/gf15-production-adapter-review/internal-review-repo-fit.md](../../../dev/records/milestones/r12/gf15-production-adapter-review/internal-review-repo-fit.md)
  Label: internal-review-repo-fit (filename label)
- [dev/records/milestones/r12/gf15-production-adapter-review/internal-review-risk.md](../../../dev/records/milestones/r12/gf15-production-adapter-review/internal-review-risk.md)
  Label: internal-review-risk (filename label)
- [dev/records/milestones/r12/gf15-production-adapter-review/ledger.md](../../../dev/records/milestones/r12/gf15-production-adapter-review/ledger.md)
  Label: GF15 production adapter findings ledger
- [dev/records/milestones/r12/gf15-production-adapter-review/observations.md](../../../dev/records/milestones/r12/gf15-production-adapter-review/observations.md)
  Label: Run observations
- [dev/records/milestones/r12/gf15-production-adapter-review/review-brief.md](../../../dev/records/milestones/r12/gf15-production-adapter-review/review-brief.md)
  Label: External review contract — GF15 production adapter
- [dev/records/milestones/r12/gf15-production-adapter-review/scoped-review-v3.md](../../../dev/records/milestones/r12/gf15-production-adapter-review/scoped-review-v3.md)
  Label: scoped-review-v3 (filename label)
- [dev/records/milestones/r12/gf15-production-adapter-review/status.md](../../../dev/records/milestones/r12/gf15-production-adapter-review/status.md)
  Label: status (filename label)
- [dev/records/milestones/r12/implementation/baseline-cli-check.txt](../../../dev/records/milestones/r12/implementation/baseline-cli-check.txt)
  Label: baseline-cli-check (filename label)
- [dev/records/milestones/r12/implementation/environment-check.txt](../../../dev/records/milestones/r12/implementation/environment-check.txt)
  Label: environment-check (filename label)
- [dev/records/milestones/r12/implementation/evidence/chirps-unit-verification-2026-09-27.md](../../../dev/records/milestones/r12/implementation/evidence/chirps-unit-verification-2026-09-27.md)
  Label: CHIRPS unit verification — 2026-09-27
- [dev/records/milestones/r12/implementation/evidence/gf15-accuracy-3x/README.md](../../../dev/records/milestones/r12/implementation/evidence/gf15-accuracy-3x/README.md)
  Label: GF15 accuracy policy — threefold error limits
- [dev/records/milestones/r12/implementation/evidence/gf15-accuracy-3x/scientific-handoff.md](../../../dev/records/milestones/r12/implementation/evidence/gf15-accuracy-3x/scientific-handoff.md)
  Label: GF15 threefold accuracy-policy assessment
- [dev/records/milestones/r12/implementation/evidence/gf15-accuracy-3x/verification/commands.md](../../../dev/records/milestones/r12/implementation/evidence/gf15-accuracy-3x/verification/commands.md)
  Label: Executed bounded verification
- [dev/records/milestones/r12/implementation/evidence/gf15-accuracy-8x/README.md](../../../dev/records/milestones/r12/implementation/evidence/gf15-accuracy-8x/README.md)
  Label: GF15 accuracy policy — eightfold error limits
- [dev/records/milestones/r12/implementation/evidence/gf15-accuracy-8x/scientific-handoff.md](../../../dev/records/milestones/r12/implementation/evidence/gf15-accuracy-8x/scientific-handoff.md)
  Label: GF15 eightfold accuracy-policy assessment
- [dev/records/milestones/r12/implementation/evidence/gf15-accuracy-8x/verification/commands.md](../../../dev/records/milestones/r12/implementation/evidence/gf15-accuracy-8x/verification/commands.md)
  Label: Bounded accuracy-policy verification
- [dev/records/milestones/r12/implementation/evidence/gf15-candidates/scientific-handoff.md](../../../dev/records/milestones/r12/implementation/evidence/gf15-candidates/scientific-handoff.md)
  Label: GF15 candidates: normalization merits full qualification testing
- [dev/records/milestones/r12/implementation/evidence/gf15-investigation/scientific-handoff.md](../../../dev/records/milestones/r12/implementation/evidence/gf15-investigation/scientific-handoff.md)
  Label: GF15 investigation: numerical instability and broad accuracy shortfall
- [dev/records/milestones/r12/implementation/evidence/gf15-lmoments-assessment/README.md](../../../dev/records/milestones/r12/implementation/evidence/gf15-lmoments-assessment/README.md)
  Label: GF15 L-moment independent assessment — Stage 3/3
- [dev/records/milestones/r12/implementation/evidence/gf15-lmoments-assessment/scientific-handoff.md](../../../dev/records/milestones/r12/implementation/evidence/gf15-lmoments-assessment/scientific-handoff.md)
  Label: Independent scientific qualification verdict — GF15 Stage 3/3
- [dev/records/milestones/r12/implementation/evidence/gf15-lmoments-qualification/execution-handoff.md](../../../dev/records/milestones/r12/implementation/evidence/gf15-lmoments-qualification/execution-handoff.md)
  Label: GF15 L-moment Stage 2 execution handoff
- [dev/records/milestones/r12/implementation/evidence/gf15-lmoments-qualification/execution-logs/mutation-probe-source.txt](../../../dev/records/milestones/r12/implementation/evidence/gf15-lmoments-qualification/execution-logs/mutation-probe-source.txt)
  Label: mutation-probe-source (filename label)
- [dev/records/milestones/r12/implementation/evidence/gf15-lmoments-qualification/README.md](../../../dev/records/milestones/r12/implementation/evidence/gf15-lmoments-qualification/README.md)
  Label: GF15 L-moment Stage 2 bounded qualification
- [dev/records/milestones/r12/implementation/evidence/gf15-lmoments-readiness/environment/README.md](../../../dev/records/milestones/r12/implementation/evidence/gf15-lmoments-readiness/environment/README.md)
  Label: Isolated Stage 1 environment
- [dev/records/milestones/r12/implementation/evidence/gf15-lmoments-readiness/environment/requirements.txt](../../../dev/records/milestones/r12/implementation/evidence/gf15-lmoments-readiness/environment/requirements.txt)
  Label: requirements (filename label)
- [dev/records/milestones/r12/implementation/evidence/gf15-lmoments-readiness/README.md](../../../dev/records/milestones/r12/implementation/evidence/gf15-lmoments-readiness/README.md)
  Label: GF15 L-moment Stage 1 implementation readiness
- [dev/records/milestones/r12/implementation/evidence/gf15-lmoments-readiness/results/attempt-1-sources/README.md](../../../dev/records/milestones/r12/implementation/evidence/gf15-lmoments-readiness/results/attempt-1-sources/README.md)
  Label: GF15 L-moment Stage 1 implementation readiness
- [dev/records/milestones/r12/implementation/evidence/gf15-lmoments-readiness/results/independent/scientific-handoff.md](../../../dev/records/milestones/r12/implementation/evidence/gf15-lmoments-readiness/results/independent/scientific-handoff.md)
  Label: Independent scientific readiness verdict — GF15 Stage 1
- [dev/records/milestones/r12/implementation/evidence/gf15-normalized-qualification/README.md](../../../dev/records/milestones/r12/implementation/evidence/gf15-normalized-qualification/README.md)
  Label: GF15 normalized candidate qualification
- [dev/records/milestones/r12/implementation/evidence/gf15-normalized-qualification/scientific-handoff.md](../../../dev/records/milestones/r12/implementation/evidence/gf15-normalized-qualification/scientific-handoff.md)
  Label: GF15 normalized candidate B: full qualification failed
- [dev/records/milestones/r12/implementation/evidence/gf15-production-applicability/integration-readiness.md](../../../dev/records/milestones/r12/implementation/evidence/gf15-production-applicability/integration-readiness.md)
  Label: GF15 production integration readiness
- [dev/records/milestones/r12/implementation/evidence/gf15-production-applicability/scientific-assessment.md](../../../dev/records/milestones/r12/implementation/evidence/gf15-production-applicability/scientific-assessment.md)
  Label: GF15 candidate C: production applicability assessment
- [dev/records/milestones/r12/implementation/evidence/gf15-production-integration/e7-parity-verdict.md](../../../dev/records/milestones/r12/implementation/evidence/gf15-production-integration/e7-parity-verdict.md)
  Label: E7 parity, refusal and diagnostic verdict — GF15 production Stage 2
- [dev/records/milestones/r12/implementation/evidence/gf15-production-integration/integration-verdict.md](../../../dev/records/milestones/r12/implementation/evidence/gf15-production-integration/integration-verdict.md)
  Label: GF15 production integration — Stage 4/4 verdict
- [dev/records/milestones/r12/implementation/evidence/gf15-production-integration/linux-qualification/execution-record.md](../../../dev/records/milestones/r12/implementation/evidence/gf15-production-integration/linux-qualification/execution-record.md)
  Label: Linux GF15 source and parity execution
- [dev/records/milestones/r12/implementation/evidence/gf15-production-integration/linux-qualification/independent-verdict.md](../../../dev/records/milestones/r12/implementation/evidence/gf15-production-integration/linux-qualification/independent-verdict.md)
  Label: Independent Linux GF15 parity verdict
- [dev/records/milestones/r12/implementation/evidence/gf15-production-integration/shape-coverage-options.md](../../../dev/records/milestones/r12/implementation/evidence/gf15-production-integration/shape-coverage-options.md)
  Label: Shape-domain coverage for `q_return_level_2yr_7day_min` — options for owner ruling
- [dev/records/milestones/r12/implementation/evidence/gf15-production-integration/snapshot-integrity-review.md](../../../dev/records/milestones/r12/implementation/evidence/gf15-production-integration/snapshot-integrity-review.md)
  Label: GF15 Stage 1 snapshot integrity review
- [dev/records/milestones/r12/implementation/evidence/gf15-production-integration/stage-1-readiness.md](../../../dev/records/milestones/r12/implementation/evidence/gf15-production-integration/stage-1-readiness.md)
  Label: GF15 production Stage 1 readiness discovery
- [dev/records/milestones/r12/implementation/evidence/gf15-production-integration/stage-2-record.md](../../../dev/records/milestones/r12/implementation/evidence/gf15-production-integration/stage-2-record.md)
  Label: GF15 production Stage 2 — adapter and report implementation record
- [dev/records/milestones/r12/implementation/evidence/gf15-production-integration/stage-2-test-full.txt](../../../dev/records/milestones/r12/implementation/evidence/gf15-production-integration/stage-2-test-full.txt)
  Label: stage-2-test-full (filename label)
- [dev/records/milestones/r12/implementation/evidence/gf15-production-integration/stage-3-record.md](../../../dev/records/milestones/r12/implementation/evidence/gf15-production-integration/stage-3-record.md)
  Label: GF15 production Stage 3 — metrics comparison record
- [dev/records/milestones/r12/implementation/evidence/gf15-production-integration/stage-3-rereview-verdict.md](../../../dev/records/milestones/r12/implementation/evidence/gf15-production-integration/stage-3-rereview-verdict.md)
  Label: Stage 3 re-review verdict — GF15 production integration, round 2
- [dev/records/milestones/r12/implementation/evidence/gf15-production-integration/stage-3-verdict.md](../../../dev/records/milestones/r12/implementation/evidence/gf15-production-integration/stage-3-verdict.md)
  Label: Stage 3 metrics-comparison verdict — GF15 production integration
- [dev/records/milestones/r12/implementation/evidence/gf15-production-integration/stage-3/metrics-run.txt](../../../dev/records/milestones/r12/implementation/evidence/gf15-production-integration/stage-3/metrics-run.txt)
  Label: metrics-run (filename label)
- [dev/records/milestones/r12/implementation/evidence/gf15-production-integration/stage-4-test-contract.txt](../../../dev/records/milestones/r12/implementation/evidence/gf15-production-integration/stage-4-test-contract.txt)
  Label: stage-4-test-contract (filename label)
- [dev/records/milestones/r12/implementation/evidence/gf15-production-integration/stage-4-test-fast.txt](../../../dev/records/milestones/r12/implementation/evidence/gf15-production-integration/stage-4-test-fast.txt)
  Label: stage-4-test-fast (filename label)
- [dev/records/milestones/r12/implementation/evidence/gf15-production-integration/windows-setup/install-output.txt](../../../dev/records/milestones/r12/implementation/evidence/gf15-production-integration/windows-setup/install-output.txt)
  Label: install-output (filename label)
- [dev/records/milestones/r12/implementation/evidence/gf15-production-integration/windows-setup/lock-solve.txt](../../../dev/records/milestones/r12/implementation/evidence/gf15-production-integration/windows-setup/lock-solve.txt)
  Label: lock-solve (filename label)
- [dev/records/milestones/r12/implementation/evidence/gf15-production-integration/windows-setup/setup-review.md](../../../dev/records/milestones/r12/implementation/evidence/gf15-production-integration/windows-setup/setup-review.md)
  Label: Independent review — GF15 production Stage 1, setup half
- [dev/records/milestones/r12/implementation/evidence/gf15-production-integration/windows-setup/stage-1-setup-record.md](../../../dev/records/milestones/r12/implementation/evidence/gf15-production-integration/windows-setup/stage-1-setup-record.md)
  Label: GF15 production Stage 1 — isolated Windows setup record
- [dev/records/milestones/r12/implementation/evidence/gf15/README.md](../../../dev/records/milestones/r12/implementation/evidence/gf15/README.md)
  Label: GF15 estimator benchmark evidence
- [dev/records/milestones/r12/implementation/evidence/gf15/scientific-handoff.md](../../../dev/records/milestones/r12/implementation/evidence/gf15/scientific-handoff.md)
  Label: GF15 scientific handoff: benchmark failed
- [dev/records/milestones/r12/implementation/evidence/p0/checkpoint-transcript.txt](../../../dev/records/milestones/r12/implementation/evidence/p0/checkpoint-transcript.txt)
  Label: checkpoint-transcript (filename label)
- [dev/records/milestones/r12/implementation/evidence/p0/operation-target-feasibility.md](../../../dev/records/milestones/r12/implementation/evidence/p0/operation-target-feasibility.md)
  Label: P0 operation/target feasibility — Master Gate 3
- [dev/records/milestones/r12/implementation/evidence/p0/operation-target-transcript.txt](../../../dev/records/milestones/r12/implementation/evidence/p0/operation-target-transcript.txt)
  Label: operation-target-transcript (filename label)
- [dev/records/milestones/r12/implementation/evidence/p0/p2b-feasibility.md](../../../dev/records/milestones/r12/implementation/evidence/p0/p2b-feasibility.md)
  Label: P0 P2b feasibility evidence
- [dev/records/milestones/r12/implementation/evidence/p0/p2b-missing-dry-run.txt](../../../dev/records/milestones/r12/implementation/evidence/p0/p2b-missing-dry-run.txt)
  Label: p2b-missing-dry-run (filename label)
- [dev/records/milestones/r12/implementation/evidence/p0/p2b-missing-execute.txt](../../../dev/records/milestones/r12/implementation/evidence/p0/p2b-missing-execute.txt)
  Label: p2b-missing-execute (filename label)
- [dev/records/milestones/r12/implementation/evidence/p0/p2b-mutation.txt](../../../dev/records/milestones/r12/implementation/evidence/p0/p2b-mutation.txt)
  Label: p2b-mutation (filename label)
- [dev/records/milestones/r12/implementation/evidence/p0/p2b-no-derived-dry-run.txt](../../../dev/records/milestones/r12/implementation/evidence/p0/p2b-no-derived-dry-run.txt)
  Label: p2b-no-derived-dry-run (filename label)
- [dev/records/milestones/r12/implementation/evidence/p0/p2b-no-derived-execute.txt](../../../dev/records/milestones/r12/implementation/evidence/p0/p2b-no-derived-execute.txt)
  Label: p2b-no-derived-execute (filename label)
- [dev/records/milestones/r12/implementation/evidence/p0/p2b-resolvable-dry-run.txt](../../../dev/records/milestones/r12/implementation/evidence/p0/p2b-resolvable-dry-run.txt)
  Label: p2b-resolvable-dry-run (filename label)
- [dev/records/milestones/r12/implementation/evidence/p0/p2b-resolvable-execute.txt](../../../dev/records/milestones/r12/implementation/evidence/p0/p2b-resolvable-execute.txt)
  Label: p2b-resolvable-execute (filename label)
- [dev/records/milestones/r12/implementation/evidence/p0/p2b-swapped.txt](../../../dev/records/milestones/r12/implementation/evidence/p0/p2b-swapped.txt)
  Label: p2b-swapped (filename label)
- [dev/records/milestones/r12/implementation/evidence/p0/prechange-snapshot.md](../../../dev/records/milestones/r12/implementation/evidence/p0/prechange-snapshot.md)
  Label: R12 P0 fresh pre-change snapshot
- [dev/records/milestones/r12/implementation/evidence/p0/runner-checkpoint-checks.txt](../../../dev/records/milestones/r12/implementation/evidence/p0/runner-checkpoint-checks.txt)
  Label: runner-checkpoint-checks (filename label)
- [dev/records/milestones/r12/implementation/evidence/p0/runner-checkpoint-feasibility.md](../../../dev/records/milestones/r12/implementation/evidence/p0/runner-checkpoint-feasibility.md)
  Label: P0 approved runner and checkpoint feasibility
- [dev/records/milestones/r12/implementation/evidence/p1-forcing-units.md](../../../dev/records/milestones/r12/implementation/evidence/p1-forcing-units.md)
  Label: P1 forcing-unit trace
- [dev/records/milestones/r12/implementation/evidence/p1-generation-handoff.md](../../../dev/records/milestones/r12/implementation/evidence/p1-generation-handoff.md)
  Label: P1 generation acceptance handoff
- [dev/records/milestones/r12/implementation/evidence/p1-response-metric-handoff.md](../../../dev/records/milestones/r12/implementation/evidence/p1-response-metric-handoff.md)
  Label: P1 response and metric handoff
- [dev/records/milestones/r12/implementation/evidence/p1-simulator-handoff.md](../../../dev/records/milestones/r12/implementation/evidence/p1-simulator-handoff.md)
  Label: P1 simulator preparation and execution handoff
- [dev/records/milestones/r12/implementation/evidence/p1-source-binding-review.md](../../../dev/records/milestones/r12/implementation/evidence/p1-source-binding-review.md)
  Label: P1 existing-source binding review
- [dev/records/milestones/r12/implementation/evidence/p2/acceptance.md](../../../dev/records/milestones/r12/implementation/evidence/p2/acceptance.md)
  Label: R12 P2 acceptance — durable handoffs in current WF3
- [dev/records/milestones/r12/implementation/evidence/p2/checkpoint-transcript.txt](../../../dev/records/milestones/r12/implementation/evidence/p2/checkpoint-transcript.txt)
  Label: checkpoint-transcript (filename label)
- [dev/records/milestones/r12/implementation/evidence/p2/collection-lifecycle.md](../../../dev/records/milestones/r12/implementation/evidence/p2/collection-lifecycle.md)
  Label: P2 adapter-backed collection lifecycle — 2026-09-11
- [dev/records/milestones/r12/implementation/evidence/p2/identity-foundation.md](../../../dev/records/milestones/r12/implementation/evidence/p2/identity-foundation.md)
  Label: P2 collection identity foundation — 2026-09-10
- [dev/records/milestones/r12/implementation/evidence/p2/portable-preparation-probe.txt](../../../dev/records/milestones/r12/implementation/evidence/p2/portable-preparation-probe.txt)
  Label: portable-preparation-probe (filename label)
- [dev/records/milestones/r12/implementation/evidence/p2/portable-preparation.md](../../../dev/records/milestones/r12/implementation/evidence/p2/portable-preparation.md)
  Label: P2 portable preparation handoff
- [dev/records/milestones/r12/implementation/evidence/p2/scientific-handoff.md](../../../dev/records/milestones/r12/implementation/evidence/p2/scientific-handoff.md)
  Label: P2 retained collection, native response and metric scientific handoff
- [dev/records/milestones/r12/implementation/evidence/p2/software-validation.txt](../../../dev/records/milestones/r12/implementation/evidence/p2/software-validation.txt)
  Label: software-validation (filename label)
- [dev/records/milestones/r12/implementation/evidence/p3/acceptance.md](../../../dev/records/milestones/r12/implementation/evidence/p3/acceptance.md)
  Label: R12 P3 acceptance — workflow extraction
- [dev/records/milestones/r12/implementation/evidence/p3/checkpoint-transcript.txt](../../../dev/records/milestones/r12/implementation/evidence/p3/checkpoint-transcript.txt)
  Label: checkpoint-transcript (filename label)
- [dev/records/milestones/r12/implementation/evidence/p3/direct-project-tree.txt](../../../dev/records/milestones/r12/implementation/evidence/p3/direct-project-tree.txt)
  Label: Project-tree snapshot --- a sorted list of project-relative paths.
- [dev/records/milestones/r12/implementation/evidence/p3/direct-scientific-handoff.md](../../../dev/records/milestones/r12/implementation/evidence/p3/direct-scientific-handoff.md)
  Label: P3 direct-run scientific handoff
- [dev/records/milestones/r12/implementation/evidence/p3/final-operations-probe-guide.md](../../../dev/records/milestones/r12/implementation/evidence/p3/final-operations-probe-guide.md)
  Label: GF30/GF32 final-interface follow-up
- [dev/records/milestones/r12/implementation/evidence/p3/gf27-acceptance.md](../../../dev/records/milestones/r12/implementation/evidence/p3/gf27-acceptance.md)
  Label: P3 GF27 seed and namespace preservation acceptance
- [dev/records/milestones/r12/implementation/evidence/p3/gf28-temporal-review.md](../../../dev/records/milestones/r12/implementation/evidence/p3/gf28-temporal-review.md)
  Label: P3 GF28 temporal preservation review
- [dev/records/milestones/r12/implementation/evidence/p3/gf31-acceptance.md](../../../dev/records/milestones/r12/implementation/evidence/p3/gf31-acceptance.md)
  Label: P3 GF31 portable preparation acceptance
- [dev/records/milestones/r12/implementation/evidence/p3/runner-project-tree.txt](../../../dev/records/milestones/r12/implementation/evidence/p3/runner-project-tree.txt)
  Label: Project-tree snapshot --- a sorted list of project-relative paths.
- [dev/records/milestones/r12/implementation/evidence/p3/scientific-orchestration-handoff.md](../../../dev/records/milestones/r12/implementation/evidence/p3/scientific-orchestration-handoff.md)
  Label: P3 consolidated scientific and orchestration handoff
- [dev/records/milestones/r12/implementation/evidence/p3/scientific-probe-commands.md](../../../dev/records/milestones/r12/implementation/evidence/p3/scientific-probe-commands.md)
  Label: Bounded P3 scientific probe commands
- [dev/records/milestones/r12/implementation/evidence/p3/scientific-review-preparation.md](../../../dev/records/milestones/r12/implementation/evidence/p3/scientific-review-preparation.md)
  Label: P3 scientific review preparation
- [dev/records/milestones/r12/implementation/evidence/p6/implementation-record.md](../../../dev/records/milestones/r12/implementation/evidence/p6/implementation-record.md)
  Label: P6 simulation and metric-set/2 implementation record
- [dev/records/milestones/r12/implementation/evidence/p7/complete-run-record.md](../../../dev/records/milestones/r12/implementation/evidence/p7/complete-run-record.md)
  Label: P7 complete-run acceptance record
- [dev/records/milestones/r12/implementation/evidence/seal-test-full.txt](../../../dev/records/milestones/r12/implementation/evidence/seal-test-full.txt)
  Label: seal-test-full (filename label)
- [dev/records/milestones/r12/implementation/evidence/standing-seal-status.md](../../../dev/records/milestones/r12/implementation/evidence/standing-seal-status.md)
  Label: R12 standing baseline and tree status
- [dev/records/milestones/r12/implementation/evidence/successor-baseline-record.md](../../../dev/records/milestones/r12/implementation/evidence/successor-baseline-record.md)
  Label: R12 successor baseline — execution record
- [dev/records/milestones/r12/implementation/gf15-lmoments-readiness-brief.md](../../../dev/records/milestones/r12/implementation/gf15-lmoments-readiness-brief.md)
  Label: Task Brief — GF15 L-moment Stage 1 readiness
- [dev/records/milestones/r12/implementation/gf15-production-integration-brief.md](../../../dev/records/milestones/r12/implementation/gf15-production-integration-brief.md)
  Label: GF15 production integration — master brief
- [dev/records/milestones/r12/implementation/gf15-production-stage-1.md](../../../dev/records/milestones/r12/implementation/gf15-production-stage-1.md)
  Label: Task Brief — GF15 snapshot and setup, Stage 1/4
- [dev/records/milestones/r12/implementation/gf15-production-stage-2.md](../../../dev/records/milestones/r12/implementation/gf15-production-stage-2.md)
  Label: Task Brief — GF15 adapter and report, Stage 2/4
- [dev/records/milestones/r12/implementation/gf15-production-stage-3.md](../../../dev/records/milestones/r12/implementation/gf15-production-stage-3.md)
  Label: Task Brief — GF15 metrics comparison, Stage 3/4
- [dev/records/milestones/r12/implementation/gf15-production-stage-4.md](../../../dev/records/milestones/r12/implementation/gf15-production-stage-4.md)
  Label: Task Brief — GF15 integration acceptance, Stage 4/4
- [dev/records/milestones/r12/implementation/master-brief.md](../../../dev/records/milestones/r12/implementation/master-brief.md)
  Label: Master Brief — Implement the accepted R12 WF3 successor
- [dev/records/milestones/r12/implementation/phase-0-feasibility-baseline.md](../../../dev/records/milestones/r12/implementation/phase-0-feasibility-baseline.md)
  Label: Task Brief — P0 feasibility and pre-change baseline preparation
- [dev/records/milestones/r12/implementation/phase-1-contract-extraction.md](../../../dev/records/milestones/r12/implementation/phase-1-contract-extraction.md)
  Label: Task Brief — P1 logical contract extraction in current WF3
- [dev/records/milestones/r12/implementation/phase-2-durable-handoffs.md](../../../dev/records/milestones/r12/implementation/phase-2-durable-handoffs.md)
  Label: Task Brief — P2 durable handoffs in current WF3
- [dev/records/milestones/r12/implementation/phase-3-workflow-extraction.md](../../../dev/records/milestones/r12/implementation/phase-3-workflow-extraction.md)
  Label: Task Brief — P3 reference-atomic workflow extraction
- [dev/records/milestones/r12/implementation/readiness.md](../../../dev/records/milestones/r12/implementation/readiness.md)
  Label: R12 implementation readiness
- [dev/records/milestones/r12/implementation/validation-map.md](../../../dev/records/milestones/r12/implementation/validation-map.md)
  Label: R12 GF-1..GF-32 validation map
- [dev/records/milestones/r12/migration_stress-test-lookup.md](../../../dev/records/milestones/r12/migration_stress-test-lookup.md)
  Label: Migration — the stress-test lookup
- [dev/records/milestones/r12/migration-workflow-names.md](../../../dev/records/milestones/r12/migration-workflow-names.md)
  Label: Migration — separate scenario generation and system simulation
- [dev/records/milestones/r12/premigration/README.md](../../../dev/records/milestones/r12/premigration/README.md)
  Label: Pre-migration artifacts — the WF3 stress-test lookup
- [dev/records/milestones/r12/simulation-identity-intake.md](../../../dev/records/milestones/r12/simulation-identity-intake.md)
  Label: Intake — WF3 in three stages: scenario space, simulation, metrics
- [dev/records/milestones/r12/stress-test-design-and-surface-axes-2026-08-15.md](../../../dev/records/milestones/r12/stress-test-design-and-surface-axes-2026-08-15.md)
  Label: Separating the experiment from the response surface
- [dev/records/milestones/r12/stress-test-lookup-design.md](../../../dev/records/milestones/r12/stress-test-lookup-design.md)
  Label: WF3 — stress-test lookup and derived response-surface axes: Design
- [dev/records/milestones/r12/stress-test-lookup-intake.md](../../../dev/records/milestones/r12/stress-test-lookup-intake.md)
  Label: Intake — WF3 stress-test lookup and surface axes
- [dev/records/milestones/r12/stress-test-lookup-review-record.md](../../../dev/records/milestones/r12/stress-test-lookup-review-record.md)
  Label: WF3 stress-test lookup — consolidated review record
- [dev/records/milestones/r12/stress-test-lookup-task-brief.md](../../../dev/records/milestones/r12/stress-test-lookup-task-brief.md)
  Label: Task Brief — implement the WF3 stress-test lookup and derived surface axes
- [dev/records/milestones/r12/wf3-experiment-v2-design-review-record.md](../../../dev/records/milestones/r12/wf3-experiment-v2-design-review-record.md)
  Label: WF3 v2.0 execution model — consolidated review record
- [dev/records/milestones/r12/wf3-simulation-identity-design.md](../../../dev/records/milestones/r12/wf3-simulation-identity-design.md)
  Label: Scenario generation and system behavior simulation: WF3 successor design
- [dev/records/milestones/r12/wf3-simulation-identity-review/candidate-family-schema.md](../../../dev/records/milestones/r12/wf3-simulation-identity-review/candidate-family-schema.md)
  Label: Candidate second scenario family — a paper schema, and what it does to E18
- [dev/records/milestones/r12/wf3-simulation-identity-review/design-v1.md](../../../dev/records/milestones/r12/wf3-simulation-identity-review/design-v1.md)
  Label: WF3 in three stages — scenario space, simulation, metrics: Design
- [dev/records/milestones/r12/wf3-simulation-identity-review/design-v2.md](../../../dev/records/milestones/r12/wf3-simulation-identity-review/design-v2.md)
  Label: WF3 in three stages — scenario space, simulation, metrics: Design
- [dev/records/milestones/r12/wf3-simulation-identity-review/design-v3.md](../../../dev/records/milestones/r12/wf3-simulation-identity-review/design-v3.md)
  Label: Scenario generation and system behavior simulation: WF3 successor design
- [dev/records/milestones/r12/wf3-simulation-identity-review/design-v4.md](../../../dev/records/milestones/r12/wf3-simulation-identity-review/design-v4.md)
  Label: Scenario generation and system behavior simulation: WF3 successor design
- [dev/records/milestones/r12/wf3-simulation-identity-review/design-v5.md](../../../dev/records/milestones/r12/wf3-simulation-identity-review/design-v5.md)
  Label: Scenario generation and system behavior simulation: WF3 successor design
- [dev/records/milestones/r12/wf3-simulation-identity-review/design-v6.md](../../../dev/records/milestones/r12/wf3-simulation-identity-review/design-v6.md)
  Label: Scenario generation and system behavior simulation: WF3 successor design
- [dev/records/milestones/r12/wf3-simulation-identity-review/external-review-r1-brief.md](../../../dev/records/milestones/r12/wf3-simulation-identity-review/external-review-r1-brief.md)
  Label: External review brief — WF3 simulation identity, round 1
- [dev/records/milestones/r12/wf3-simulation-identity-review/external-review-r1.md](../../../dev/records/milestones/r12/wf3-simulation-identity-review/external-review-r1.md)
  Label: external-review-r1 (filename label)
- [dev/records/milestones/r12/wf3-simulation-identity-review/external-sandbox-preflight.md](../../../dev/records/milestones/r12/wf3-simulation-identity-review/external-sandbox-preflight.md)
  Label: external-sandbox-preflight (filename label)
- [dev/records/milestones/r12/wf3-simulation-identity-review/internal-review-architecture.md](../../../dev/records/milestones/r12/wf3-simulation-identity-review/internal-review-architecture.md)
  Label: Internal review — architecture & internal consistency (stage 1b)
- [dev/records/milestones/r12/wf3-simulation-identity-review/internal-review-domain-v3.md](../../../dev/records/milestones/r12/wf3-simulation-identity-review/internal-review-domain-v3.md)
  Label: internal-review-domain-v3 (filename label)
- [dev/records/milestones/r12/wf3-simulation-identity-review/internal-review-domain.md](../../../dev/records/milestones/r12/wf3-simulation-identity-review/internal-review-domain.md)
  Label: Internal review — scientific & methodological soundness (stage 1b)
- [dev/records/milestones/r12/wf3-simulation-identity-review/internal-review-index-v3.md](../../../dev/records/milestones/r12/wf3-simulation-identity-review/internal-review-index-v3.md)
  Label: Internal review index — design v3
- [dev/records/milestones/r12/wf3-simulation-identity-review/internal-review-index.md](../../../dev/records/milestones/r12/wf3-simulation-identity-review/internal-review-index.md)
  Label: Internal review index — `design-v1.md`
- [dev/records/milestones/r12/wf3-simulation-identity-review/internal-review-risk.md](../../../dev/records/milestones/r12/wf3-simulation-identity-review/internal-review-risk.md)
  Label: Internal review — risk & assumptions (stage 1b)
- [dev/records/milestones/r12/wf3-simulation-identity-review/ledger.md](../../../dev/records/milestones/r12/wf3-simulation-identity-review/ledger.md)
  Label: Disposition ledger — wf3 simulation identity, revision r1
- [dev/records/milestones/r12/wf3-simulation-identity-review/observations.md](../../../dev/records/milestones/r12/wf3-simulation-identity-review/observations.md)
  Label: Process observations — wf3-simulation-identity
- [dev/records/milestones/r12/wf3-simulation-identity-review/probe-p1-p2.md](../../../dev/records/milestones/r12/wf3-simulation-identity-review/probe-p1-p2.md)
  Label: Framework-feasibility probes P1, P2 — wf3-simulation-identity
- [dev/records/milestones/r12/wf3-simulation-identity-review/probe-p3-p4-p5.md](../../../dev/records/milestones/r12/wf3-simulation-identity-review/probe-p3-p4-p5.md)
  Label: Framework-feasibility probes P3, P4, P5 — wf3-simulation-identity
- [dev/records/milestones/r12/wf3-simulation-identity-review/review-brief.md](../../../dev/records/milestones/r12/wf3-simulation-identity-review/review-brief.md)
  Label: External review brief — WF3 simulation identity, round ``
- [dev/records/milestones/r12/wf3-simulation-identity-review/scope-expansion-2026-09-09.md](../../../dev/records/milestones/r12/wf3-simulation-identity-review/scope-expansion-2026-09-09.md)
  Label: Scope expansion — explicit WF3 simulator boundary
- [dev/records/milestones/r12/wf3-simulation-identity-review/scoped-review-v5-brief.md](../../../dev/records/milestones/r12/wf3-simulation-identity-review/scoped-review-v5-brief.md)
  Label: Scoped verification of design v5
- [dev/records/milestones/r12/wf3-simulation-identity-review/scoped-review-v5.md](../../../dev/records/milestones/r12/wf3-simulation-identity-review/scoped-review-v5.md)
  Label: scoped-review-v5 (filename label)
- [dev/records/milestones/r12/wf3-simulation-identity-review/scoped-review-v6-brief.md](../../../dev/records/milestones/r12/wf3-simulation-identity-review/scoped-review-v6-brief.md)
  Label: Scoped verification of design v6
- [dev/records/milestones/r12/wf3-simulation-identity-review/scoped-review-v6.md](../../../dev/records/milestones/r12/wf3-simulation-identity-review/scoped-review-v6.md)
  Label: scoped-review-v6 (filename label)
- [dev/records/milestones/r12/wf3-simulation-identity-review/status.md](../../../dev/records/milestones/r12/wf3-simulation-identity-review/status.md)
  Label: status (filename label)
- [dev/records/milestones/r12/wf3-simulation-identity-task-brief.md](../../../dev/records/milestones/r12/wf3-simulation-identity-task-brief.md)
  Label: Task Brief — Prepare R12 implementation from the accepted design
- [dev/records/milestones/r13/baseline-pass-1-result.md](../../../dev/records/milestones/r13/baseline-pass-1-result.md)
  Label: R13 — pass 1 (split-only) result
- [dev/records/milestones/r13/baseline-pass-2-result.md](../../../dev/records/milestones/r13/baseline-pass-2-result.md)
  Label: R13 — pass 2 (hoisted state) result
- [dev/records/milestones/r13/baseline-pass-runbook.md](../../../dev/records/milestones/r13/baseline-pass-runbook.md)
  Label: R13 — the two baseline passes
- [dev/records/milestones/r13/config-tiers-design.md](../../../dev/records/milestones/r13/config-tiers-design.md)
  Label: R13 — Config modularization: Design (ACCEPTED)
- [dev/records/milestones/r13/config-tiers-intake.md](../../../dev/records/milestones/r13/config-tiers-intake.md)
  Label: Intake — config-modularization design run
- [dev/records/milestones/r13/config-tiers-review-record.md](../../../dev/records/milestones/r13/config-tiers-review-record.md)
  Label: R13 config tiers — consolidated review record
- [dev/records/milestones/r13/migration_config-tiers.md](../../../dev/records/milestones/r13/migration_config-tiers.md)
  Label: R13 — config tiers: what the migration actually did
- [dev/records/milestones/r13/migration-config-tiers.md](../../../dev/records/milestones/r13/migration-config-tiers.md)
  Label: Migrating a project config to the tiered layout
- [dev/records/milestones/r14/config-shape-design.md](../../../dev/records/milestones/r14/config-shape-design.md)
  Label: R14 — Config shape: Design (DRAFT — v9)
- [dev/records/milestones/r14/config-shape-external-review-1-brief.md](../../../dev/records/milestones/r14/config-shape-external-review-1-brief.md)
  Label: R14 — external review round 1, the brief as dispatched
- [dev/records/milestones/r14/config-shape-external-review-1.md](../../../dev/records/milestones/r14/config-shape-external-review-1.md)
  Label: R14 — external review round 1, verbatim
- [dev/records/milestones/r14/config-shape-gate5.md](../../../dev/records/milestones/r14/config-shape-gate5.md)
  Label: config-shape-gate5 (filename label)
- [dev/records/milestones/r14/config-shape-intake.md](../../../dev/records/milestones/r14/config-shape-intake.md)
  Label: Intake — R14 config shape design run
- [dev/records/milestones/r14/config-shape-master-brief.md](../../../dev/records/milestones/r14/config-shape-master-brief.md)
  Label: config-shape-master-brief (filename label)
- [dev/records/milestones/r14/config-shape-p0-baseline-provenance.task.md](../../../dev/records/milestones/r14/config-shape-p0-baseline-provenance.task.md)
  Label: config-shape-p0-baseline-provenance.task (filename label)
- [dev/records/milestones/r14/config-shape-p1-loader.task.md](../../../dev/records/milestones/r14/config-shape-p1-loader.task.md)
  Label: config-shape-p1-loader.task (filename label)
- [dev/records/milestones/r14/config-shape-p1b-readers.task.md](../../../dev/records/milestones/r14/config-shape-p1b-readers.task.md)
  Label: config-shape-p1b-readers.task (filename label)
- [dev/records/milestones/r14/config-shape-p1c-gate1.md](../../../dev/records/milestones/r14/config-shape-p1c-gate1.md)
  Label: R14 P1c — Gate 1, released 2026-08-29
- [dev/records/milestones/r14/config-shape-p1c-registry.task.md](../../../dev/records/milestones/r14/config-shape-p1c-registry.task.md)
  Label: config-shape-p1c-registry.task (filename label)
- [dev/records/milestones/r14/config-shape-p2-falsifiers.md](../../../dev/records/milestones/r14/config-shape-p2-falsifiers.md)
  Label: R14 P2 — the three rung-2 falsifiers, as observed
- [dev/records/milestones/r14/config-shape-p2-identity.task.md](../../../dev/records/milestones/r14/config-shape-p2-identity.task.md)
  Label: config-shape-p2-identity.task (filename label)
- [dev/records/milestones/r14/config-shape-p2-sequencing-decision.md](../../../dev/records/milestones/r14/config-shape-p2-sequencing-decision.md)
  Label: R14 — P2's blocking edge is P4, not P1b
- [dev/records/milestones/r14/config-shape-p3-rewriter.task.md](../../../dev/records/milestones/r14/config-shape-p3-rewriter.task.md)
  Label: config-shape-p3-rewriter.task (filename label)
- [dev/records/milestones/r14/config-shape-p4-configs.task.md](../../../dev/records/milestones/r14/config-shape-p4-configs.task.md)
  Label: config-shape-p4-configs.task (filename label)
- [dev/records/milestones/r14/config-shape-p5-rename.task.md](../../../dev/records/milestones/r14/config-shape-p5-rename.task.md)
  Label: config-shape-p5-rename.task (filename label)
- [dev/records/milestones/r14/config-shape-p6-docs.task.md](../../../dev/records/milestones/r14/config-shape-p6-docs.task.md)
  Label: config-shape-p6-docs.task (filename label)
- [dev/records/milestones/r14/config-shape-p7-independent.task.md](../../../dev/records/milestones/r14/config-shape-p7-independent.task.md)
  Label: config-shape-p7-independent.task (filename label)
- [dev/records/milestones/r14/config-shape-review-record.md](../../../dev/records/milestones/r14/config-shape-review-record.md)
  Label: R14 — Config shape: review record
- [dev/records/milestones/r14/config-shape-scoping.md](../../../dev/records/milestones/r14/config-shape-scoping.md)
  Label: Scoping — R14 config shape (naming, nesting, sections)
- [dev/records/milestones/r14/gate5-tree-diff.txt](../../../dev/records/milestones/r14/gate5-tree-diff.txt)
  Label: gate5-tree-diff (filename label)
- [dev/records/milestones/r14/migration-config-shape.md](../../../dev/records/milestones/r14/migration-config-shape.md)
  Label: Migrating a project config to `schema_version: 2`
- [dev/records/milestones/r14/parameter-placement.md](../../../dev/records/milestones/r14/parameter-placement.md)
  Label: Configuration surface — problem statement and inventory (DRAFT)
- [dev/records/milestones/README.md](../../../dev/records/milestones/README.md)
  Label: dev/records/milestones/
- [dev/records/milestones/roadmap.md](../../../dev/records/milestones/roadmap.md)
  Label: Fork Roadmap
- [dev/records/README.md](../../../dev/records/README.md)
  Label: Retained development records
- [dev/records/validation/climate-extraction-transfer-2026-09-18.md](../../../dev/records/validation/climate-extraction-transfer-2026-09-18.md)
  Label: Climate extraction transfer evidence — 2026-09-18
- [dev/records/validation/cmip6-per-variable-pinning-2026-10-22.md](../../../dev/records/validation/cmip6-per-variable-pinning-2026-10-22.md)
  Label: CMIP6 per-variable pinning verification
- [dev/records/validation/experiment-numbering-2026-10-10/implementation-evidence.md](../../../dev/records/validation/experiment-numbering-2026-10-10/implementation-evidence.md)
  Label: Experiment numbering implementation evidence
- [dev/records/validation/local-input-e2e-2026-10-15.md](../../../dev/records/validation/local-input-e2e-2026-10-15.md)
  Label: Local-input all-workflow E2E qualification — 2026-10-15
- [dev/records/validation/named-indicator-sets-walkthrough.md](../../../dev/records/validation/named-indicator-sets-walkthrough.md)
  Label: Walkthrough — add a named indicator set to an existing project
- [dev/records/validation/named-indicator-sets.md](../../../dev/records/validation/named-indicator-sets.md)
  Label: Named indicator sets — completion and evidence
- [dev/records/validation/plot-improvements/verification.md](../../../dev/records/validation/plot-improvements/verification.md)
  Label: Plot integration acceptance evidence — 2026-10-08–09
- [dev/records/validation/qcrit-temperature-outputs.md](../../../dev/records/validation/qcrit-temperature-outputs.md)
  Label: Historical Qcrit and temperature output verification
- [dev/records/validation/release-qualification-2026-10.md](../../../dev/records/validation/release-qualification-2026-10.md)
  Label: Release qualification evidence — October 2026
- [dev/records/validation/water-year-october-verification.md](../../../dev/records/validation/water-year-october-verification.md)
  Label: WF2 October water-year verification
- [dev/records/validation/wf2-plot-table-parity-2026-09-27.md](../../../dev/records/validation/wf2-plot-table-parity-2026-09-27.md)
  Label: Historical WF2 plot-to-table parity — retained 2026-09-27
- [dev/records/validation/wf2-suite-integration.md](../../../dev/records/validation/wf2-suite-integration.md)
  Label: WF2 suite integration evidence — 2026-10-07
- [dev/records/validation/wf2-wf3-performance.md](../../../dev/records/validation/wf2-wf3-performance.md)
  Label: WF2 and WF3 performance changes
- [dev/records/validation/wf3-preparation-cost-2026-08-15.md](../../../dev/records/validation/wf3-preparation-cost-2026-08-15.md)
  Label: Historical WF3 preparation cost — 2026-08-15
- [dev/records/validation/wf4-q90-preflight.md](../../../dev/records/validation/wf4-q90-preflight.md)
  Label: WF4 historical Qcrit preflight handoff
- [dev/records/validation/wflow-constant-restoration/baseline_diffs.md](../../../dev/records/validation/wflow-constant-restoration/baseline_diffs.md)
  Label: Baseline diffs — ADR 0001 constant-parameter restoration (t260719a)
- [dev/records/validation/wflow-constant-restoration/equivalence-gate-log.md](../../../dev/records/validation/wflow-constant-restoration/equivalence-gate-log.md)
  Label: Equivalence gate log — ADR 0001 constant-parameter restoration (t260719a)
- [dev/records/validation/wflow-constant-restoration/README.md](../../../dev/records/validation/wflow-constant-restoration/README.md)
  Label: Wflow constant-restoration evidence

### Task coordination and handoffs (76)

Primary: task owners, contributors and agents. Secondary: project maintainers.

- [dev/LOG.md](../../../dev/LOG.md)
  Label: LOG
- [dev/tasks/t2608071201-r10-12.md](../../../dev/tasks/t2608071201-r10-12.md)
  Label: WF1 rebuild always trips WF3 drift guard
- [dev/tasks/t2608071207-r7-8.md](../../../dev/tasks/t2608071207-r7-8.md)
  Label: Prove wflow log check fails without path_log
- [dev/tasks/t2608071221-r7-17.md](../../../dev/tasks/t2608071221-r7-17.md)
  Label: Docker and Linux end-to-end runs untested
- [dev/tasks/t2608091730-produce-waterbody-layers-data-side-so-basin-area-can-show-them-again.md](../../../dev/tasks/t2608091730-produce-waterbody-layers-data-side-so-basin-area-can-show-them-again.md)
  Label: Make waterbody layers for the basin map
- [dev/tasks/t2608121606-a-missing-catalog-source-is-logged-identically-to-an-empty-basin-so-1-08-can-silently-omit-a-real-reservoir.md](../../../dev/tasks/t2608121606-a-missing-catalog-source-is-logged-identically-to-an-empty-basin-so-1-08-can-silently-omit-a-real-reservoir.md)
  Label: Missing catalog source can hide a reservoir
- [dev/tasks/t2608191733-ship-a-sample-dataset-bundle-so-a-user-needs-no-deltares-p-drive.md](../../../dev/tasks/t2608191733-ship-a-sample-dataset-bundle-so-a-user-needs-no-deltares-p-drive.md)
  Label: Ship a sample dataset bundle
- [dev/tasks/t2608191733/build-sample-bundle-brief.md](../../../dev/tasks/t2608191733/build-sample-bundle-brief.md)
  Label: build-sample-bundle-brief (filename label)
- [dev/tasks/t2608191733/sample-dataset-design.md](../../../dev/tasks/t2608191733/sample-dataset-design.md)
  Label: Shipped sample dataset — scope
- [dev/tasks/t2608202351a-notebooks-on-the-site-via-committed-freeze.md](../../../dev/tasks/t2608202351a-notebooks-on-the-site-via-committed-freeze.md)
  Label: Publish pipeline notebooks on the docs site
- [dev/tasks/t2608202352-publish-the-docs-site-to-github-pages.md](../../../dev/tasks/t2608202352-publish-the-docs-site-to-github-pages.md)
  Label: Publish docs site to GitHub Pages
- [dev/tasks/t2608222252-derived-extraction-vars.md](../../../dev/tasks/t2608222252-derived-extraction-vars.md)
  Label: Make climate extraction variables configurable
- [dev/tasks/t2609181302-snakemake-s-six-line-preamble-is-not-suppressible-from-inside-a-workflow.md](../../../dev/tasks/t2609181302-snakemake-s-six-line-preamble-is-not-suppressible-from-inside-a-workflow.md)
  Label: Snakemake preamble cannot be suppressed
- [dev/tasks/t2609251025-wflow-sysimage-to-remove-per-batch-julia-startup.md](../../../dev/tasks/t2609251025-wflow-sysimage-to-remove-per-batch-julia-startup.md)
  Label: Wflow sysimage to cut Julia startup
- [dev/tasks/t2609251520-open-question-flat-hash-suffixed-names-for-generation-inputs-snapshots.md](../../../dev/tasks/t2609251520-open-question-flat-hash-suffixed-names-for-generation-inputs-snapshots.md)
  Label: Decide naming of generation_inputs snapshots
- [dev/tasks/t2609281102-complete-reviewed-expert-wflow-model-revisions-design.md](../../../dev/tasks/t2609281102-complete-reviewed-expert-wflow-model-revisions-design.md)
  Label: Finish Wflow model revisions design
- [dev/tasks/t2609281102/design-v1.md](../../../dev/tasks/t2609281102/design-v1.md)
  Label: Expert Wflow model revisions
- [dev/tasks/t2609281102/intake.md](../../../dev/tasks/t2609281102/intake.md)
  Label: Expert model revisions — intake
- [dev/tasks/t2609281102/internal-review-domain.md](../../../dev/tasks/t2609281102/internal-review-domain.md)
  Label: internal-review-domain (filename label)
- [dev/tasks/t2609281102/status.md](../../../dev/tasks/t2609281102/status.md)
  Label: status (filename label)
- [dev/tasks/t2610022259-conceptual-workflow-improvements.md](../../../dev/tasks/t2610022259-conceptual-workflow-improvements.md)
  Label: Scope conceptual workflow improvements
- [dev/tasks/t2610022259/wf0-climate-analysis-ideas.md](../../../dev/tasks/t2610022259/wf0-climate-analysis-ideas.md)
  Label: WF0 climate analysis and visualization ideas
- [dev/tasks/t2610022259/wf0-lab-setup-instructions.md](../../../dev/tasks/t2610022259/wf0-lab-setup-instructions.md)
  Label: WF0 lab setup instructions
- [dev/tasks/t2610022259/wf0-starter-suite-proposal.md](../../../dev/tasks/t2610022259/wf0-starter-suite-proposal.md)
  Label: WF0 starter suite proposal
- [dev/tasks/t2610022259/wf0-starter-suite-task-brief.md](../../../dev/tasks/t2610022259/wf0-starter-suite-task-brief.md)
  Label: WF0 starter suite implementation brief
- [dev/tasks/t2610022259/wf2-climate-projections-ideas.md](../../../dev/tasks/t2610022259/wf2-climate-projections-ideas.md)
  Label: WF2 climate projections analysis and uncertainty ideas
- [dev/tasks/t2610022259/wf2-figure-examples/02-communication/README.md](../../../dev/tasks/t2610022259/wf2-figure-examples/02-communication/README.md)
  Label: 2. Communication and explanatory graphics
- [dev/tasks/t2610022259/wf2-figure-examples/03-shared-foundation/README.md](../../../dev/tasks/t2610022259/wf2-figure-examples/03-shared-foundation/README.md)
  Label: 3. Shared operational foundation
- [dev/tasks/t2610022259/wf2-figure-examples/04-c0-evidence-coverage/README.md](../../../dev/tasks/t2610022259/wf2-figure-examples/04-c0-evidence-coverage/README.md)
  Label: 4. C0 — Evidence coverage
- [dev/tasks/t2610022259/wf2-figure-examples/04-c1-mean-changes/README.md](../../../dev/tasks/t2610022259/wf2-figure-examples/04-c1-mean-changes/README.md)
  Label: 4. C1 — Changes in mean conditions
- [dev/tasks/t2610022259/wf2-figure-examples/04-c2-seasonality/README.md](../../../dev/tasks/t2610022259/wf2-figure-examples/04-c2-seasonality/README.md)
  Label: 4. C2 — Seasonal conditions and redistribution
- [dev/tasks/t2610022259/wf2-figure-examples/04-c3-trajectories/README.md](../../../dev/tasks/t2610022259/wf2-figure-examples/04-c3-trajectories/README.md)
  Label: 4. C3 — Trajectories and calendar horizons
- [dev/tasks/t2610022259/wf2-figure-examples/04-c4-variability/README.md](../../../dev/tasks/t2610022259/wf2-figure-examples/04-c4-variability/README.md)
  Label: 4. C4 — Interannual variability and distributions
- [dev/tasks/t2610022259/wf2-figure-examples/04-c5-agreement-scenarios/README.md](../../../dev/tasks/t2610022259/wf2-figure-examples/04-c5-agreement-scenarios/README.md)
  Label: 4. C5 — Agreement and scenario contrasts
- [dev/tasks/t2610022259/wf2-figure-examples/04-c6-sensitivity/README.md](../../../dev/tasks/t2610022259/wf2-figure-examples/04-c6-sensitivity/README.md)
  Label: 4. C6 — Membership, family and window sensitivity
- [dev/tasks/t2610022259/wf2-figure-examples/04-paired-temperature-precipitation/README.md](../../../dev/tasks/t2610022259/wf2-figure-examples/04-paired-temperature-precipitation/README.md)
  Label: 4. Cross-component — Paired temperature and precipitation
- [dev/tasks/t2610022259/wf2-figure-examples/05-1-uncertainty-partition/README.md](../../../dev/tasks/t2610022259/wf2-figure-examples/05-1-uncertainty-partition/README.md)
  Label: 5.1 Uncertainty inventory and partitioning
- [dev/tasks/t2610022259/wf2-figure-examples/05-2-sampling-intervals/README.md](../../../dev/tasks/t2610022259/wf2-figure-examples/05-2-sampling-intervals/README.md)
  Label: 5.2 Sampling intervals
- [dev/tasks/t2610022259/wf2-figure-examples/05-3-weighting/README.md](../../../dev/tasks/t2610022259/wf2-figure-examples/05-3-weighting/README.md)
  Label: 5.3 Performance and independence weighting
- [dev/tasks/t2610022259/wf2-figure-examples/06-1-warming-levels/README.md](../../../dev/tasks/t2610022259/wf2-figure-examples/06-1-warming-levels/README.md)
  Label: 6.1 Global warming levels and pathway dependence
- [dev/tasks/t2610022259/wf2-figure-examples/06-2-map-robustness/README.md](../../../dev/tasks/t2610022259/wf2-figure-examples/06-2-map-robustness/README.md)
  Label: 6.2 Map robustness
- [dev/tasks/t2610022259/wf2-figure-examples/06-3-emergence/README.md](../../../dev/tasks/t2610022259/wf2-figure-examples/06-3-emergence/README.md)
  Label: 6.3 Time of emergence
- [dev/tasks/t2610022259/wf2-figure-examples/07-1-daily-extremes/README.md](../../../dev/tasks/t2610022259/wf2-figure-examples/07-1-daily-extremes/README.md)
  Label: 7.1 Daily extremes
- [dev/tasks/t2610022259/wf2-figure-examples/07-2-frequency-return-levels/README.md](../../../dev/tasks/t2610022259/wf2-figure-examples/07-2-frequency-return-levels/README.md)
  Label: 7.2 Extreme-event frequency and return levels
- [dev/tasks/t2610022259/wf2-figure-examples/07-3-drought-water-balance/README.md](../../../dev/tasks/t2610022259/wf2-figure-examples/07-3-drought-water-balance/README.md)
  Label: 7.3 Drought and climatic water balance
- [dev/tasks/t2610022259/wf2-figure-examples/07-4-compound-sequencing/README.md](../../../dev/tasks/t2610022259/wf2-figure-examples/07-4-compound-sequencing/README.md)
  Label: 7.4 Compound hazards, concurrence and sequencing
- [dev/tasks/t2610022259/wf2-figure-examples/07-5-season-timing/README.md](../../../dev/tasks/t2610022259/wf2-figure-examples/07-5-season-timing/README.md)
  Label: 7.5 Season timing
- [dev/tasks/t2610022259/wf2-figure-examples/07-6-modes-teleconnections/README.md](../../../dev/tasks/t2610022259/wf2-figure-examples/07-6-modes-teleconnections/README.md)
  Label: 7.6 Climate modes and teleconnections
- [dev/tasks/t2610022259/wf2-figure-examples/07-7-snow-evaporative-demand/README.md](../../../dev/tasks/t2610022259/wf2-figure-examples/07-7-snow-evaporative-demand/README.md)
  Label: 7.7 Snow and evaporative demand
- [dev/tasks/t2610022259/wf2-figure-examples/08-1-spatial-support/README.md](../../../dev/tasks/t2610022259/wf2-figure-examples/08-1-spatial-support/README.md)
  Label: 8.1 Catchments, subcatchments and national support
- [dev/tasks/t2610022259/wf2-figure-examples/08-2-processing-choices/README.md](../../../dev/tasks/t2610022259/wf2-figure-examples/08-2-processing-choices/README.md)
  Label: 8.2 Regridding, bias adjustment and downscaling
- [dev/tasks/t2610022259/wf2-figure-examples/09-vulnerability-overlays/README.md](../../../dev/tasks/t2610022259/wf2-figure-examples/09-vulnerability-overlays/README.md)
  Label: 9. Projection overlays, vulnerability and storylines
- [dev/tasks/t2610022259/wf2-figure-examples/10-summary-accessibility/README.md](../../../dev/tasks/t2610022259/wf2-figure-examples/10-summary-accessibility/README.md)
  Label: 10. Summary communication and accessibility
- [dev/tasks/t2610022259/wf2-figure-examples/gallery.html](../../../dev/tasks/t2610022259/wf2-figure-examples/gallery.html)
  Label: WF2 published figure examples
- [dev/tasks/t2610022259/wf2-figure-examples/README.md](../../../dev/tasks/t2610022259/wf2-figure-examples/README.md)
  Label: WF2 published figure examples
- [dev/tasks/t2610022259/wf2-figure-examples/SOURCES.md](../../../dev/tasks/t2610022259/wf2-figure-examples/SOURCES.md)
  Label: Publications behind the figure collection
- [dev/tasks/t2610022259/wf2-lab-suite-brief.md](../../../dev/tasks/t2610022259/wf2-lab-suite-brief.md)
  Label: WF2 starter suite lab brief
- [dev/tasks/t2610022259/wf2-projections-research-guide.md](../../../dev/tasks/t2610022259/wf2-projections-research-guide.md)
  Label: Regional climate projections — methods and communication research guide
- [dev/tasks/t2610022259/wf2-starter-suite-proposal.md](../../../dev/tasks/t2610022259/wf2-starter-suite-proposal.md)
  Label: WF2 starter suite proposal
- [dev/tasks/t2610091622-triage-unresolved-geographic-robustness-findings.md](../../../dev/tasks/t2610091622-triage-unresolved-geographic-robustness-findings.md)
  Label: Triage unresolved geographic robustness findings
- [dev/tasks/t2610091622/geographic-robustness-2026-09-28.md](../../../dev/tasks/t2610091622/geographic-robustness-2026-09-28.md)
  Label: Geographic robustness observations
- [dev/tasks/t2610091737-bounded-window-forcing.md](../../../dev/tasks/t2610091737-bounded-window-forcing.md)
  Label: Consider bounded-window forcing preparation for WF4
- [dev/tasks/t2610191323-ntoum-workflow-performance.md](../../../dev/tasks/t2610191323-ntoum-workflow-performance.md)
  Label: Investigate WF4 and WF2 performance from the Ntoum run
- [dev/tasks/t2610211349-improving-repo-wide-documentation-and-instructions.md](../../../dev/tasks/t2610211349-improving-repo-wide-documentation-and-instructions.md)
  Label: Improving repo-wide documentation and instructions
- [dev/tasks/t2610211349/documentation-review-2026-10-21.md](../../../dev/tasks/t2610211349/documentation-review-2026-10-21.md)
  Label: Documentation landscape review
- [dev/tasks/t2610241523a-isolate-snakemake-state-between-parallel-test-workers.md](../../../dev/tasks/t2610241523a-isolate-snakemake-state-between-parallel-test-workers.md)
  Label: Isolate Snakemake state between parallel test workers
- [dev/tasks/t2610241523b-extract-the-plotting-core-as-a-package.md](../../../dev/tasks/t2610241523b-extract-the-plotting-core-as-a-package.md)
  Label: Extract the plotting core as a package
- [dev/tasks/t2610241523b/packaging-scope.md](../../../dev/tasks/t2610241523b/packaging-scope.md)
  Label: Packaging scope for the plotting core
- [dev/tasks/t2610241523c-adopt-the-shared-plotting-style-in-r-wf3-figures.md](../../../dev/tasks/t2610241523c-adopt-the-shared-plotting-style-in-r-wf3-figures.md)
  Label: Adopt the shared plotting style in R/WF3 figures
- [dev/tasks/t2610241658-runner-dry-run-plans-a-full-wf1-rebuild-after-a-complete-run.md](../../../dev/tasks/t2610241658-runner-dry-run-plans-a-full-wf1-rebuild-after-a-complete-run.md)
  Label: Runner dry-run plans a full WF1 rebuild after a complete run
- [dev/tasks/tmp-cleanup/landing-evidence.md](../../../dev/tasks/tmp-cleanup/landing-evidence.md)
  Label: Session-2 landing evidence
- [dev/tasks/wf3-run-ids/implementation-evidence.md](../../../dev/tasks/wf3-run-ids/implementation-evidence.md)
  Label: Run and group identity implementation
- [dev/tasks/wf3-run-ids/task-brief.md](../../../dev/tasks/wf3-run-ids/task-brief.md)
  Label: Task Brief — Readable run IDs and separate run/group metric tables
- [dev/tasks/worktree-runtime/evidence.md](../../../dev/tasks/worktree-runtime/evidence.md)
  Label: Worktree footprint and session runtime evidence
- [dev/TODO.md](../../../dev/TODO.md)
  Label: TODO
- [DEVLOG.md](../../../DEVLOG.md)
  Label: DEVLOG: feat/wf2-cmip6-improvements

### Legal and reuse (1)

Primary: users and redistributors. Secondary: contributors.

- [LICENSE](../../../LICENSE)
  Label: LICENSE (filename label)

## Verification and limitations

- Enumerated 656 unique source paths and verified that every path exists.
- Register coverage was checked against the selector; every selected file occurs once.
- Relative links were checked against the main checkout; no site build or workflow execution was needed.
- Grouping is an inventory aid, not a completed purpose or authority audit.
- Contents of every historical record, notebook cell and upstream page were not read in full.
- This supersedes the earlier structural inventory for coverage, while preserving that dated record.
