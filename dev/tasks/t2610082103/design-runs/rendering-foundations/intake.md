# Rendering foundations intake

Lifecycle: temporary task-owned review intake. Date: 2026-10-10.

## Request and agreed framing

User request: "Yes, I agree with your plan. Please make sure to save this extensive note first, then lets
start the work. Please delate the work to suitable roles/models with focused hand-offs that aims a good
balance between costs (token consumption) and effectiveness".

The agreed source assessment and complete roadmap are saved in the canonical main checkout at
`dev/tasks/t2610082103/landscape-and-plan.md`, commit `1d635c47`.
The user explicitly chose Python rendering first. An internal Matplotlib core precedes eventual external
packaging. This review covers the first fundamentals increment, not the entire roadmap.

## Scope and constraints

Extract existing common rendering fundamentals into a neutral `blueearth_cst/plotting/` package and
migrate active WF0–WF2 consumers. Preserve reviewed appearance, numerical preparation, filenames,
caption meaning, output inventory and specialist compositions. No R migration, new scientific method,
map-reference producer, full chart-interface migration, or independent distribution in this increment.
Resolve exact module boundaries and caller inventory in the draft. Small explicit functions first.
Do not mechanically move the entire WF0 module or introduce a broad framework.

Figure/layout helper extraction and export decoupling may be split into separately verifiable packets
within this first increment. Identify any export/caption behavior that cannot be moved without changing
behavior; preserve it initially and record the remaining work explicitly.

Implementation checkout: `C:/Users/taner/workspace/.worktrees/blueearth_cst/session-1`, pinned
`chore/minor-fixes`. No landing/push. Canonical task and planning files remain in the primary checkout's
`dev/tasks/t2610082103/` under repository instructions. Agent draft capture uses task scratch then copies
exact completed bytes into the canonical run. The primary checkout is not an implementation workspace.

## Journey and actor boundaries

The workflow prepares its existing values and caption text. A workflow-specific adapter passes prepared
values to its artist composition. That composition calls shared style/layout/axes/legend helpers and
returns a Matplotlib figure. Export mechanics save the explicit figure; CST owns paths, logging,
caption manifests and provenance. The current report consumes the same figure files and caption text.
The analyst invokes the same workflow command and obtains the same products.

No new user-visible layout choice is proposed. The existing plot-style reference and comparison viewer
are authoritative, so there is no new interactive UI sketch. The draft must include an affected source
tree and an explicit unchanged/generated-output inventory.

## Evidence register

| ID | Premise / exact observation | Reproduction | Confidence |
|---|---|---|---|
| E1 | WF1 imports WF0 artists and private climatology helpers | Read forcing_figures imports/calls | Source-verified |
| E2 | WF2 imports STYLE, sizing, ticks and legend helpers from WF0 | Read projection_suite_figures imports | Source-verified |
| E3 | WF0 View carries workflow-specific data | Read diagnostic_figures.View | Source-verified |
| E4 | save_figure also updates logging bundles | Read snake_utils.save_figure | Source-verified |
| E5 | Map-reference production is not neutral drawing | Read saved landscape sections 3/5 | Source-verified |
| E6 | Caption expansion preserves axes geometry | Must measure exported/drawn boxes | Unproven; not assumed |
| E7 | All affected real render inputs are available | Inventory retained local/rapid inputs | Pending preflight |

Domain-content flag: no for this bounded fundamentals review. No physical/statistical assumptions or
data treatments are chosen or changed. The validation concerns representation and dependency boundaries;
numerical methods remain owned by existing modules. If drafting changes that scope, return for domain
review rather than silently waiving it.

## Derived-artifact register and gates

- Saved landscape: agreed direction and inventory; not a reviewed implementation specification.
- intake.md/status.md: driver-owned state in design-runs/rendering-foundations/.
- design-vN.md: architect-authored contract, immutable after review capture.
- Reviews/ledger: create only when their stages execute; preserve originals and IDs.
- Implementation and evidence: follow exact approved first-slice contract and live validation ladder.

Runnable checks: targeted Ruff and pytest through Pixi, to be named after the caller inventory is fixed.
Pre-change artifacts needed: render baselines from retained matching inputs before any implementation.
Gate E7 must identify actual source paths/config/output roots rather than merely promise future checks.
No Snakemake rules or runtime configuration change is planned; if needed, escalate scope and gates.

## Approval state

The 2026-10-10 user message approves the overall framing and authorizes starting work. Reuse that
authorization; do not ask again about Python first, internal development or the deferred roadmap.
The detailed implementation design still needs the review loop's exact reviewed-revision G2 decision.
No permission to implement new unreviewed contracts is inferred from an absent answer.

## Author handoff

Produce a concise, self-contained foundations design (target 1,200–1,800 words, justify excess) grounded
in the existing code. Use design-document's software-system contract. Enumerate exact functions/tokens
and caller files, dependency rules, migration/compatibility, retirements, alternatives, validation cases
and commands. Existing legacy styles must not be silently replaced. Include explicit handling of
backend selection, mutable style dictionaries, runtime style overrides, caption geometry and logging.
Do not invent a universal API before a caller needs it. No source edits in this stage.
