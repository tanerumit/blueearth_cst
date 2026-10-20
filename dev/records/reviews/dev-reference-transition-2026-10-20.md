# Current-reference transition — 2026-10-20

Implemented for review on session-3. Main and its shared task board were not edited.
The reference index is the current topic-ownership map. Templates are reusable starting artifacts;
records preserve evidence and cannot establish today's requirements from an old acceptance label.

## Relocated files

This table resolves old paths in immutable evidence and shared board/ledger citations.
Editable branch-owned consumers were updated. Sealed specifications moved without body or hash changes.

| Former path | Retained destination |
|---|---|
| `dev/reference/sealed-records.yml` | `dev/records/sealed-records.yml` |
| `dev/reference/contracts/README.md` | `dev/reference/README.md` (interface topic rows) |
| `dev/reference/contracts/weather-generator-seam.md` | `dev/reference/weather-generator-interface.md` |
| `dev/reference/contracts/hydrological-model-seam.md` | `dev/reference/hydrological-model-interface.md` |
| `dev/reference/contracts/forcing-units.md` | `dev/reference/forcing-units.md` |
| `dev/reference/workflows/model_creation.md` | `dev/reference/wf1-model-construction.md` |
| `dev/reference/workflows/rule-index.md` | `dev/reference/workflow-implementation-map.md` |
| `dev/reference/workflows/wf2-cmip6-store-readability.md` | `dev/reference/wf2-cmip6-source-readability.md` |
| `dev/reference/workflows/wf3-stage-flow.html` | `dev/assets/diagrams/scenario-response-handoffs.html` |
| `dev/reference/workflows/wf3-stage-flow.svg` | `dev/assets/diagrams/scenario-response-handoffs.svg` |
| `dev/reference/roadmap.md` | `dev/records/milestones/roadmap.md` |
| `dev/reference/task-lanes.md` | `dev/records/decisions/task-lanes.md` |
| `dev/reference/agent-routing-diagnostics.md` | `dev/records/reviews/agent-routing-diagnostics.md` |
| `dev/reference/wf2-wf3-performance.md` | `dev/records/reviews/wf2-wf3-performance.md` |
| `dev/reference/migration_plot_paths.md` | `dev/records/reviews/plot-improvements/migration_plot_paths.md` |
| `dev/reference/workflows/water-year-october-verification.md` | `dev/records/reviews/water-year-october-verification.md` |
| `dev/reference/workflows/wf2-cmip6-store-inventory.md` | `dev/records/milestones/r08/wf2-cmip6-store-inventory.md` |
| `dev/reference/workflows/wf2-cmip6-monthly-members.csv` | `dev/records/milestones/r08/wf2-cmip6-monthly-members.csv` |
| `dev/reference/workflows/wf2-cmip6-daily-members.csv` | `dev/records/milestones/r08/wf2-cmip6-daily-members.csv` |
| `dev/reference/workflows/climate_projections.md` | `dev/records/milestones/r04/climate_projections.md` |
| `dev/reference/workflows/climate_experiment.md` | `dev/records/milestones/r05/climate_experiment.md` |
| `dev/reference/figure-comparison.html` | `dev/templates/figure-comparison.html` |
| `dev/reference/figure-comparison.md` | `dev/templates/figure-comparison.md` |
| `dev/reference/workflow-report.html` | `dev/templates/workflow-report.html` |
| `dev/reference/workflow-report.md` | `dev/templates/workflow-report.md` |

## Mixed documents

- WG/HM identifiers remain in the current interface references. Their old section headings are historical;
  use the contract ID to find the current account. The CHIRPS closure witness is retained in
  `dev/records/milestones/r12/implementation/evidence/chirps-unit-verification-2026-09-27.md`; other removed interface narrative is
  recoverable from commit `ed406a81`. Current descriptions distinguish adapter requirements and validator limits.
- Git branch/tag inventory moved to `dev/records/milestones/git-ref-inventory.md`; conventions stay current.
- Historical rule-numbering maps moved to `dev/records/milestones/r10/rule-numbering-crosswalks.md`.
- CMIP6 measured readability history moved to `dev/records/milestones/r08/cmip6-readability-measurements.md`;
  current source-selection behavior remains in the original reference topic.
- Existing ADRs remain at their cited paths, with a current-reference map and historical-status notices.
  No current requirements are maintained in parallel in those records.
- Workflow-report session preview narrative and incidental reference chronology remain recoverable in Git.

## Current guidance and limits

The architecture, spatial-foundation, forcing-unit and model-construction topics route current requirements
to code/configuration and existing verification. Historical ADR 0011's pending label is not reused as a
current assessment: the present tree contains archive/launch implementation. ADR 0022 remains a design
record; no universal run-contract adoption is claimed.

Last-updated fields mean content revision, not correctness certification. Dates introduced on otherwise
unchanged topics use their latest Git revision. This migration checks ownership, navigation, source-backed
claims that were rewritten, and preserved seals; it is not a whole-toolbox scientific revalidation.

The activation checker now compares materialized names to the tracked manifest, removing the duplicated
inventory from reference prose. Infrastructure tooling retains ownership of role-derived scope checks.

## Integration boundary

Shared `dev/tasks/`, `dev/TODO.md` and `dev/LOG.md` were deliberately untouched. Before landing, update
their editable citations to any paths in the move table through a separate main board-maintenance commit.
This is navigation maintenance, not authority to advance or close tasks.
The eight preexisting review-file deletions in session-3 were not part of this transition.

## Verification

- `pytest tests/test_activation_links.py tests/test_sealed_records.py tests/test_indicator_glossary.py -q`:
  61 passed using session-2's runtime against session-3 sources.
- Reference/template/index navigation: 133 relative links and fragments checked; no missing targets.
- Relocated HTML templates and CSV inventories match their previous text content; sealed-record tests
  confirm preserved bodies and hashes.
- Repository `ruff check .` and `ruff format --check .` passed; changed Python modules compiled.
- Shared board paths have no session diff. Main retains only its preexisting task changes.

No workflow execution or numerical revalidation was needed: runtime scientific code and inputs are
unchanged. The only executable behavior change is the developer activation check's declaration source.
