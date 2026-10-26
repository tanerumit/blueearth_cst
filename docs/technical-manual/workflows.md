---
title: "Workflow boundaries"
format: html
---

The usual execution order is WF0 → WF1 → WF2 → WF3 → WF4. WF1 and WF3 independently supply WF4.
WF2 is a projection plausibility overlay; its CMIP6 changes never determine WF3 forcing.
All products are written below `project.project_dir`.

| Workflow | Entry point | Principal product |
|---|---|---|
| [WF0](workflow-analyze-climate.md) | `analyze_climate.smk` | Historical source diagnostics and comparisons |
| [WF1](workflow-build-model.md) | `build_model.smk` | Completed model and historical simulation/evaluation |
| [WF2](workflow-analyze-projections.md) | `analyze_projections.smk` | Basin change factors and projection diagnostics |
| [WF3](workflow-generate-scenarios.md) | `generate_scenarios.smk` | Ready scenario collection |
| [WF4](workflow-simulate-system.md) | `simulate_system.smk` | Retained responses and named indicator sets |

## Historical reference and model setup

WF0 is optional and model-free. Run it first or alone when choosing forcing: it shares region and historical
climate producers with the other workflows. WF1 constructs the model from catalog data and runs historical
forcing. Observations enable evaluation where supplied; no local calibration is performed.

## Projection context and stress-test experiment

WF2 compares CMIP6 historical and future windows. WF3 conditions a weather generator on the selected
historical source, then perturbs generated realizations over the configured climate grid. WF3 needs no
Wflow model. WF4 needs a completed WF1 model and explicit runs from a ready collection. It consumes no WF2
product. An indicators-only request can reuse compatible retained WF4 responses.

Use `scripts/run_workflows.py` for the configured pipeline, including WF3 preparation and publication.
Use `scripts/simulate_system.py` for direct WF4. Bare Snakemake is not a supported WF3/WF4 execution route.
The [running guide](../guide/running.md) owns commands and recovery; [configuration](configuration.md)
owns composition and paths. Rule numbers are reference labels, not a serial schedule: independent branches
can run concurrently.

The runner's final verdict includes result publication. Progress or a completed simulation batch alone is
not confirmation that every requested indicator set is current. Exact records and console conventions are
described in [execution and provenance](execution-and-provenance.md).
