# Repository documentation inventory by audience

Date: 2026-10-26. Task: t2610211349. Revised scope: main checkout before this update.
Source commit: `145d23e6c765e5b10341cfc50eccb4bca2af4eea`.

## Scope and method

This file-level inventory supports the next boundary, purpose and redundancy review.
The scope is limited to the five audience groups below, excluding `.github/` and `CHANGELOG.md`.
The register contains **55 tracked files**, with each file listed exactly once.

Earlier exclusions remain: `dev/tasks/`, `dev/reference/`, `dev/records/`, `docs/references/`
and `dev/LOG.md`. The requested `dev/references/` corresponds to the actual `dev/reference/` directory.
Agent instructions, validation evidence, task coordination/handoffs and legal/reuse documents are also
excluded. The inventory remains saved under the task directory as evidence, outside its own review scope.

Audience assignments are provisional classifications from location, titles and collection entry points.
They do not certify accuracy, currency, authority or uniqueness. No consolidation or content review has
been performed. File headings/frontmatter were sampled for labels; collection indexes and site configuration
were read. A "filename label" indicates that no heading was extracted.

Enumeration uses `git ls-files` in main, including hidden tracked directories, filtered to the agreed scope.
The register covers Markdown, Quarto, notebooks and HTML documents/templates. Binary figures, generated
site copies, external linked libraries, local state and run outputs are excluded. All register links are
relative to this task directory and resolve within the same checkout.

## Audience summary

| Group | Files |
|---|---:|
| Toolbox users and practitioners | 28 |
| Scientific explanation | 4 |
| Indicator users and extension authors | 6 |
| Configuration users and maintainers | 9 |
| Developer and maintainer guidance | 8 |

## Collection roles and review boundaries

- User entry points: root README, docs index, setup pages, user guides and script index.
- Published explanation and reference: scientific-approach and toolbox-reference pages under docs/site.
- Indicator guidance: indicator-module and individual indicator-set READMEs.
- Configuration guidance: config READMEs, example-basin notes and template guidance.
- Developer guidance: dev/README.md, dev/scripts/README.md and dev/templates documents.

The review targets only the files in this register. Source code, CLI help, configuration comments and
publication settings may be consulted to verify claims; they are not additional review deliverables.
The generated docs/site/guide copies come from docs/guide, and docs/site/_site is rendered output.
Review and edit the registered sources rather than their generated copies.

## Next review

For each registered document, record its primary reader, reader question, authoritative scope, overlaps
and required links. Compare overlapping claims before deciding whether to consolidate, shorten or cross-link.
Preserve purposeful differences between tutorials, procedures, explanations and references.

## Complete file register

### Toolbox users and practitioners (28)

Primary: users running assessments. Secondary: trainers and support maintainers.

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

### Developer and maintainer guidance (8)

Primary: contributors and maintainers. Secondary: coding agents.

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

## Verification and limitations

- Verified 55 unique entries against the scoped tracked-file selection and checked all relative links.
- Confirmed that only the five selected audience groups remain; no excluded paths are listed.
- Grouping is an inventory aid, not a completed purpose, authority or content-accuracy audit.
- Notebook cells were not read in full. No site build or workflow execution was needed.
- Earlier broader inventory revisions remain recoverable through Git history.
