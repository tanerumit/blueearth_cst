# Documentation landscape review

Date: 2026-10-21

Scope: BlueEarth Climate Stress Test toolbox, inspected in worktree `session-2`, branch
`chore/fix-live-console-flush`. This is a structural inventory, not a page-by-page accuracy audit.
Paths below are relative to the repository root. No documentation changes were made during the inventory.

The documentation serves four broad audiences: toolbox users, scientific readers, developers, and coding
agents. Task records and historical evidence form additional collections with different authority.

## User-facing and scientific documentation

| Collection | Location | Contents and role |
|---|---|---|
| Repository introduction | `README.md` | Purpose, installation, workflows, execution, and entry points. |
| User guide | `docs/guide/` | Canonical quick start, configuration, running, benchmarking, and outputs guides. |
| Guide assets | `docs/guide/assets/` | Diagrams and other supporting guide assets. |
| Installation and troubleshooting | `docs/site/setup/` | Installation and Pixi/R/Julia environment notes. |
| Scientific approach | `docs/site/scientific-approach/` | Methods, climate information, and interpretation. |
| Toolbox reference | `docs/site/toolbox-reference/` | WF0–WF4, handoffs, tools, datasets, and assessment workflow. |
| Executable tutorials | `docs/notebooks/` | Model building, climate projections, and climate stress test. |
| Case starter | `config/templates/example-basin/` | README, notes, data examples, and annotated configurations. |
| Configuration guidance | READMEs under `config/` | Defaults, plotting, basemap, and archive guidance. |
| Execution reference | `scripts/README.md`, CLI help, docstrings | User execution commands and their contracts. |
| Indicator documentation | `blueearth_cst/indicators/` READMEs | Interfaces, definitions, assumptions, and limits. |

The main documentation entry point is `docs/README.md`.

The scientific approach contains four pages: overview, models and methods, climate information, and
conventions and interpretation. The toolbox reference includes an overview, workflow overview, individual
WF0–WF4 pages, retained handoffs, modeling tools, datasets, and assessment workflow.

The three notebooks are stored without execution outputs and remain outside the site render scope.
The case starter is the maintained configuration set that users copy or scaffold. Indicator documentation
includes the module README and `sets/*/README.md`, serving users and extension authors.

## Developer-facing documentation

The authoritative index is `dev/reference/README.md`.

| Area | Documents or topics |
|---|---|
| Development practices | Task/session workflow, layout, record lifecycle, naming, validation, and Git. |
| Maintenance policy | Versioning, documentation authoring, and agent activation. |
| Architecture | Toolbox architecture, spatial foundation, forcing units, and workflow map. |
| Interfaces | Weather-generator interface, hydrological-model interface, and indicator glossary. |
| Workflow implementation | WF0 figure naming, WF1 model construction, and WF2 CMIP6 source readability. |
| Scientific presentation | Plot style, figure export, and review conventions. |
| Maintenance tools | `dev/scripts/README.md` and individual script help/docstrings. |
| Reusable templates | `dev/templates/`: workflow reports, figure comparisons, and lane status. |
| Verification evidence | `dev/baseline/` and `dev/records/validation/`. |
| Contribution workflow | `.github/pull_request_template.md`, CI configuration, and hooks. |

## Agent instructions and operational state

| Source | Role and authority |
|---|---|
| `AGENTS.md` | Canonical repository instructions, boundaries, conventions, and required reading. |
| `CLAUDE.md` | Thin import of `AGENTS.md`, rather than a separate instruction source. |
| `.agent-system/agent-manifest.yml` | Tracked project role and skill declarations. |
| `.agents/`, `.claude/`, `.codex/` | Local provider projections, linked into this worktree. |
| User/global instructions | Cross-project defaults supplied outside the repository. |
| `STATUS.md` | Ignored, worktree-local focus, next actions, and handoff state. |
| `dev/tasks/` | Task briefs, proposals, reviews, and supporting task records. |
| `dev/TODO.md` | Generated task board view. |
| `dev/LOG.md` | Closure ledger pointing to retained outcomes. |

Shared skill and role definitions are owned by brain-infrastructure. The project manifest declares their
activation; provider projections are not the canonical editing destination for shared guidance.
In this worktree, `dev/tasks/` and `dev/TODO.md` link to the primary checkout.

## Reference sources and historical material

| Collection | Purpose |
|---|---|
| `docs/references/cst-toolbox-technical-note-2025.md` | Original scientific method and platform design. |
| `docs/references/hydromt-user-guide/` | Offline original pages, numbered compilations, and merged copies. |
| `docs/references/hydromt-architecture.md` | Offline upstream architecture and conventions. |
| `docs/references/hydromt-wflow/` | Offline plugin API and usage reference. |
| `docs/references/wflow-user-guide/` | Offline Wflow configuration and usage reference. |
| `dev/records/decision-history/` | Historical choices and rationale. |
| `dev/records/milestones/` | Earlier designs, briefs, reviews, migrations, and milestone evidence. |
| `dev/records/validation/` | Retained measurements and qualification evidence. |
| `dev/records/migrations/` | Relocation maps and historical citation recovery. |
| `dev/records/sealed-records.yml` | Preservation metadata for explicitly sealed records. |
| `CHANGELOG.md` | Release history and migration information. |
| `DEVLOG.md` | Historical WF2 task handoff, explicitly marked as such. |

Some workflow details, commands, and artifact names in the 2025 technical note are superseded.
Offline upstream documentation describes upstream tools, not necessarily the current toolbox behavior.

## Distinctions to preserve during revision

- Edit `docs/guide/`, not `docs/site/guide/`. The latter contains generated copies staged for Quarto.
- Site content and repository documentation have different scopes. `docs/site/_quarto.yml` selects the
  rendered pages; notebooks, upstream references, and the 2025 note remain outside that scope.
- Current developer rules belong in `dev/reference/`. Historical acceptance and design records do not
  establish current requirements.
- Documentation extends into code and configuration. CLI help, docstrings, schemas, annotated YAML,
  tests, and CI must agree with the prose.
- The maintained case starter is under `config/templates/example-basin/`; runtime defaults have a
  separate home under `config/defaults/`.

## Initial cleanup candidates

These observations were made during inventory; they are not an exhaustive findings list.

1. The changelog introduction points to old paths, including `dev/reference/versioning.md` and
   `dev/roadmap.md`. Current owners are `dev/reference/dev-versioning.md` and the historical roadmap under
   `dev/records/milestones/roadmap.md`.
2. The PR template still mentions API/dashboard impacts despite the repository instructions describing
   this project as a workflow engine with no API or frontend code.

## Review limits

The inventory used repository file listings, documentation indexes, site configuration, selected READMEs,
agent activation declarations, and link-target inspection. It did not render the site, execute notebooks,
verify every command or link, or assess scientific claims against implementation and evidence.
