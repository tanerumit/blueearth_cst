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
| Wflow construction, constant parameters or model-root ordering | [Model construction](workflows/model_creation.md) |
| Forcing catalog admission and unit interpretation | [Forcing units](contracts/forcing-units.md) |
| Weather-generator or hydrological-model substitution | [Interchange contracts](contracts/README.md) |
| A rule's inputs, outputs, ordering or consumers | [Rule index](workflows/rule-index.md) |
| CMIP6 grid handling or source-version selection | [CMIP6 readability](workflows/wf2-cmip6-store-readability.md) |
| Output-variable names and indicator terminology | [Indicator glossary](indicator-glossary.md) |

## Plotting and presentation

| When the change concerns | Update or consult |
|---|---|
| Scientific figure appearance, export or review practice | [Plot style](plot-style.md) |
| WF0 diagnostic figure filename grammar | [WF0 figure filenames](wf0-figure-filename-rule.md) |
| A reusable report or comparison interface | [Templates and usage](../templates/README.md) |

## How to maintain this collection

Keep the main folder flat; `contracts/` and `workflows/` retain their coherent technical groups.
A new file needs a distinct reader question and maintenance boundary, not merely a new task or decision.
Add its ownership to this map and remove any duplicate account in the same change.

Exact defaults, schemas, inventories and checks remain with their executable owners. References explain
meaning and relationships and point to those owners. If code and guidance disagree, resolve the discrepancy
before claiming compliance; acceptance of a historical design does not prove implementation.

Proposals belong with `dev/tasks/`, reusable artifacts in `dev/templates/`, and dated evidence in
[records](../records/README.md). [sealed-records.yml](../records/sealed-records.yml) owns preservation metadata.
Keep revision histories, superseded specifications and session progress out of this folder.
The [record lifecycle](record-lifecycle.md) owns the detailed maintenance policy.
