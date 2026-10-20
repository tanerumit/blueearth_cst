# Current development and toolbox reference

Last updated: 2026-10-20

This is the shared source of current guidance for developers and agents: what applies in this checkout,
how the toolbox is organized, and where to check compliance. Use this map to find the owning document
before writing. Update that document for revisions; do not create a separate file per decision or task.

## Development practices

| When the change concerns | Update or consult |
|---|---|
| Task admission, sessions, board coordination or handoffs | [development-workflow.md](development-workflow.md) |
| Repository placement, config directories or local scratch | [repo-layout.md](repo-layout.md) |
| Documentation authority, promotion, retention or sealing | [record-lifecycle.md](record-lifecycle.md) |
| File, identifier or output naming | [naming.md](naming.md) |
| Verification, evidence reuse, landing or CI | [validation-ladder.md](validation-ladder.md) |
| Git branch, tag or commit conventions | [git-conventions.md](git-conventions.md) |
| Release/version decisions | [versioning.md](versioning.md) |
| User documentation structure and authoring | [documentation-guidelines.md](documentation-guidelines.md) |
| Project agent activation and diagnostics | [agent-activation.md](agent-activation.md) |

## Architecture and implementation

| When the change concerns | Update or consult |
|---|---|
| Workflow boundaries, configuration ownership or retained handoffs | [toolbox-architecture.md](toolbox-architecture.md) |
| Shared regions, spatial identities or map ownership | [spatial-foundation.md](spatial-foundation.md) |
| Wflow construction, constant parameters or model-root ordering | [wf1-model-construction.md](wf1-model-construction.md) |
| Forcing catalog admission and unit interpretation | [forcing-units.md](forcing-units.md) |
| Generation inputs, outputs or replacement engines | [weather-generator-interface.md][generator] |
| Simulator preparation, responses or replacement engines | [hydrological-model-interface.md][simulator] |
| Rule definitions, dependencies and consumers | [workflow-implementation-map.md](workflow-implementation-map.md) |
| CMIP6 grid handling or source-version selection | [wf2-cmip6-source-readability.md](wf2-cmip6-source-readability.md) |
| Output-variable names and indicator terminology | [indicator-glossary.md](indicator-glossary.md) |

## Plotting and presentation

| When the change concerns | Update or consult |
|---|---|
| Scientific figure appearance, export or review practice | [plot-style.md](plot-style.md) |
| WF0 diagnostic figure filename grammar | [wf0-figure-filename-rule.md](wf0-figure-filename-rule.md) |
| A reusable report or comparison interface | [templates/README.md](../templates/README.md) |

## Find guidance by workflow

Use this lookup to reach the relevant topic owners; a workflow does not need its own reference file.
[toolbox-architecture.md](toolbox-architecture.md) owns shared boundaries, and the
[workflow-implementation-map.md](workflow-implementation-map.md) explains how to inspect rules and consumers.

| Workflow | Development guidance | User guide | Rule definitions |
|---|---|---|---|
| WF0: historical climate | [spatial-foundation.md][spatial], [wf0-figure-filename-rule.md][wf0-figures] | [workflow-analyze-climate.qmd][guide0] | [analyze_climate.smk][rules0] |
| WF1: model construction | [wf1-model-construction.md][model], [forcing-units.md][forcing] | [workflow-build-model.qmd][guide1] | [build_model.smk][rules1] |
| WF2: projections | [wf2-cmip6-source-readability.md][cmip6], [spatial-foundation.md][spatial] | [workflow-analyze-projections.qmd][guide2] | [analyze_projections.smk][rules2] |
| WF3: scenarios | [weather-generator-interface.md][generator], [retained-handoffs.qmd][handoffs] | [workflow-generate-scenarios.qmd][guide3] | [generate_scenarios.smk][rules3] |
| WF4: simulation | [hydrological-model-interface.md][simulator], [indicator-glossary.md][indicators] | [workflow-simulate-system.qmd][guide4] | [simulate_system.smk][rules4] |

[spatial]: spatial-foundation.md
[wf0-figures]: wf0-figure-filename-rule.md
[model]: wf1-model-construction.md
[forcing]: forcing-units.md
[cmip6]: wf2-cmip6-source-readability.md
[generator]: weather-generator-interface.md
[simulator]: hydrological-model-interface.md
[handoffs]: ../../docs/site/toolbox-reference/retained-handoffs.qmd
[indicators]: indicator-glossary.md
[guide0]: ../../docs/site/toolbox-reference/workflow-analyze-climate.qmd
[guide1]: ../../docs/site/toolbox-reference/workflow-build-model.qmd
[guide2]: ../../docs/site/toolbox-reference/workflow-analyze-projections.qmd
[guide3]: ../../docs/site/toolbox-reference/workflow-generate-scenarios.qmd
[guide4]: ../../docs/site/toolbox-reference/workflow-simulate-system.qmd
[rules0]: ../../analyze_climate.smk
[rules1]: ../../build_model.smk
[rules2]: ../../analyze_projections.smk
[rules3]: ../../generate_scenarios.smk
[rules4]: ../../simulate_system.smk

## How to maintain this collection

Keep this collection flat and organize navigation here by reader question.
Use `wfN-` prefixes for workflow-specific topics and subject names for shared concerns.
A new file needs a distinct reader question and maintenance boundary, not merely a new task or decision.
Add its ownership to this map and remove any duplicate account in the same change.

Exact defaults, schemas, inventories and checks remain with their executable owners. References explain
meaning and relationships and point to those owners. If code and guidance disagree, resolve the discrepancy
before claiming compliance; acceptance of a historical design does not prove implementation.

Proposals belong with `dev/tasks/`, reusable artifacts in `dev/templates/`, and dated evidence in
[records/README.md](../records/README.md). [sealed-records.yml](../records/sealed-records.yml) owns preservation metadata.
Keep revision histories, superseded specifications and session progress out of this folder.
The [record-lifecycle.md](record-lifecycle.md) owns the detailed maintenance policy.
