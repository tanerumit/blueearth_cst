# Current development and toolbox reference

Last updated: 2026-10-20

This is the shared source of current guidance for developers and agents: what applies in this checkout,
how the toolbox is organized, and where to check compliance. Use this map to find the owning document
before writing. Update that document for revisions; do not create a separate file per decision or task.

## Development practices

| When the change concerns | Update or consult |
|---|---|
| Task admission, sessions, board coordination or handoffs | [Development workflow](development-workflow.md) |
| Repository placement, config directories or local scratch | [Repository layout](repo-layout.md) |
| Documentation authority, promotion, retention or sealing | [Record lifecycle](record-lifecycle.md) |
| File, identifier or output naming | [Naming](naming.md) |
| Verification, evidence reuse, landing or CI | [Validation ladder](validation-ladder.md) |
| Git branch, tag or commit conventions | [Git conventions](git-conventions.md) |
| Release/version decisions | [Versioning](versioning.md) |
| User documentation structure and authoring | [Documentation guidelines](documentation-guidelines.md) |
| Project agent activation and diagnostics | [Agent activation](agent-activation.md) |

## Architecture and implementation

| When the change concerns | Update or consult |
|---|---|
| Workflow boundaries, configuration ownership or retained handoffs | [Toolbox architecture](toolbox-architecture.md) |
| Shared regions, spatial identities or map ownership | [Spatial foundation](spatial-foundation.md) |
| Wflow construction, constant parameters or model-root ordering | [Model construction](wf1-model-construction.md) |
| Forcing catalog admission and unit interpretation | [Forcing units](contracts/forcing-units.md) |
| Weather-generator or hydrological-model substitution | [Interchange contracts](contracts/README.md) |
| Rule definitions, dependencies and consumers | [Implementation map](workflow-implementation-map.md) |
| CMIP6 grid handling or source-version selection | [CMIP6 readability](wf2-cmip6-source-readability.md) |
| Output-variable names and indicator terminology | [Indicator glossary](indicator-glossary.md) |

## Plotting and presentation

| When the change concerns | Update or consult |
|---|---|
| Scientific figure appearance, export or review practice | [Plot style](plot-style.md) |
| WF0 diagnostic figure filename grammar | [WF0 figure filenames](wf0-figure-filename-rule.md) |
| A reusable report or comparison interface | [Templates and usage](../templates/README.md) |

## Find guidance by workflow

Use this lookup to reach the relevant topic owners; a workflow does not need its own reference file.
[Architecture](toolbox-architecture.md) owns shared boundaries, and the
[implementation map](workflow-implementation-map.md) explains how to inspect rules and consumers.

| Workflow | Development guidance | User guide | Rule definitions |
|---|---|---|---|
| WF0: historical climate | [Spatial][spatial], [figures][wf0-figures] | [WF0][guide0] | [WF0][rules0] |
| WF1: model construction | [Model][model], [forcing][forcing] | [WF1][guide1] | [WF1][rules1] |
| WF2: projections | [CMIP6 sources][cmip6], [spatial][spatial] | [WF2][guide2] | [WF2][rules2] |
| WF3: scenarios | [Interchange][interchange], [handoffs][handoffs] | [WF3][guide3] | [WF3][rules3] |
| WF4: simulation | [Interchange][interchange], [indicators][indicators] | [WF4][guide4] | [WF4][rules4] |

[spatial]: spatial-foundation.md
[wf0-figures]: wf0-figure-filename-rule.md
[model]: wf1-model-construction.md
[forcing]: contracts/forcing-units.md
[cmip6]: wf2-cmip6-source-readability.md
[interchange]: contracts/README.md
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

Keep the main folder flat; `contracts/` retains its coherent technical group.
Use `wfN-` prefixes for workflow-specific topics and subject names for shared concerns.
A new file needs a distinct reader question and maintenance boundary, not merely a new task or decision.
Add its ownership to this map and remove any duplicate account in the same change.

Exact defaults, schemas, inventories and checks remain with their executable owners. References explain
meaning and relationships and point to those owners. If code and guidance disagree, resolve the discrepancy
before claiming compliance; acceptance of a historical design does not prove implementation.

Proposals belong with `dev/tasks/`, reusable artifacts in `dev/templates/`, and dated evidence in
[records](../records/README.md). [sealed-records.yml](../records/sealed-records.yml) owns preservation metadata.
Keep revision histories, superseded specifications and session progress out of this folder.
The [record lifecycle](record-lifecycle.md) owns the detailed maintenance policy.
