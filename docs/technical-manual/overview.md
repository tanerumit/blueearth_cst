---
title: "Technical manual"
format: html
---

This manual describes the supported configuration, execution and retained-result interfaces of BlueEarth CST.
The reference was reconciled against toolbox commit `a4d79ea6`. Source files, schemas and tests named in each
chapter own the exact machine contracts. A successful run establishes execution, not basin-model adequacy.

The toolbox produces indicator tables for analyst interpretation. Supported response-surface construction
instructions are deferred pending reconciliation of axis authority and a checked worked example.
The existing [scientific approach](../site/scientific-approach/overview.qmd) explains assessment reasoning
and its limits.

## Components

| Component | Responsibility |
|---|---|
| HydroMT and HydroMT-Wflow | Catalog access, spatial/climate preparation and Wflow model construction |
| Wflow-SBM | Historical hydrology in WF1 and generated-forcing hydrology in WF4 |
| `weathergenr` | Stochastic weather generation conditioned on historical climate |
| Snakemake | Dependency scheduling and execution within the five workflows |
| Owned Python runners | Configuration capture, admission, WF3 preparation and final result publication |
| Independent indicator module | In-memory reductions and independent numerical checks |

The runners in `scripts/` are user entry points. Modules under `blueearth_cst/` implement workflow steps;
most are invoked by Snakemake rather than as standalone commands. The indicator module also supports plain
Python calls. Configurations describe a project; external data and generated products belong to that project.

## Sections

- [Environment](environment.md): runtime ownership and provenance.
- [Workflows](workflows.md): dependencies and the five workflow contracts.
- [Configuration](configuration.md): composition, paths, defaults and validation.
- [Input formats](input-formats.md) and [datasets](datasets.md): local tables and cataloged sources.
- [Retained handoffs](retained-handoffs.md): identities, publication, tables and joins.
- [Execution and provenance](execution-and-provenance.md): attempts, records and measurement limits.
- [Results transfer](results-transfer.md): portable WF2 products and destination checks.
- [Indicator requests](indicator-requests.md): selections, missing inputs and rechecking.
- [Indicator extension](indicator-extension.md): the canonical module contract and all five set appendices.

Installation and operating procedures start in the [user guide](../guide/quick-start.md).
The [local-source manifest](local-source-appendix.yml) declares the canonical module/set material to include
in the offline manual. Those sources remain editable beside their implementations.
