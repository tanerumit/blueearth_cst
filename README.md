# BlueEarth Climate Stress Test toolbox

[![CI](https://github.com/tanerumit/blueearth_cst/actions/workflows/ci.yml/badge.svg)](https://github.com/tanerumit/blueearth_cst/actions/workflows/ci.yml)

BlueEarth Climate Stress Test (`blueearth_cst`) is a Python, R, and Julia workflow toolbox for
first-order climate vulnerability assessments of water systems. It builds a Wflow-SBM model from
global data, generates local climate series across a temperature × precipitation stress-test grid,
and calculates hydrological indicators. The experiment is scenario-neutral: CMIP6 projections
provide a plausibility overlay for the tested changes; they do not select or weight grid cells.

The toolbox uses [weathergenr](https://github.com/Deltares-research/weathergenr) for climate series
and [Wflow](https://github.com/Deltares/Wflow.jl) for hydrological simulation. This is a
[personal fork](https://github.com/Deltares/blueearth_cst) of the Deltares project.

## Get started

Install [Pixi](https://pixi.sh/) and Julia 1.11.7 through juliaup, clone this repository, then run
`pixi install` and `pixi run install`. Follow the [Windows installation guide](docs/site/setup/install.md)
for the supported setup sequence and verification. Julia must be on `PATH`; Pixi manages the Python
and R environment. The toolbox has no supported Docker image.

Workflow inputs are **not** included in the installation. The supplied test configs use HydroMT
catalogs that expect access to Deltares data, including `P:/wflow_global/hydromt`. Check catalog
coverage and data access before running the example. The [quick start](docs/guide/quick-start.md)
walks through that example and its results.

From the repository root, after installation and data-access checks, run the enabled rapid-case
workflows with:

```powershell
pixi run python scripts/run_workflows.py --config test_case/project_config_rapid.yml --project-dir test_case/test_rapid --cores 3
```

The rapid case exercises the pipeline and is not a numerical assessment baseline. A successful
run writes its summary under `test_case/test_rapid/logs/<timestamp>__all-workflows/`; the closing
console output links the exact `summary.md`. See [Reading the outputs](docs/guide/outputs.md) for
the model, climate series, responses, and indicator tables.

## Workflow map

| Stage | Entry point | Result |
|---|---|---|
| WF0, optional | `analyze_climate.smk` | Historical climate diagnostics for forcing selection |
| WF1 | `build_model.smk` | Wflow-SBM model and historical run |
| WF2 | `analyze_projections.smk` | CMIP6 change factors for a plausibility overlay |
| WF3 | `generate_scenarios.smk` | Retained, scenario-neutral climate series |
| WF4 | `scripts/simulate_system.py` | Model responses and retained indicator sets |

The all-workflow runner uses WF0 → WF1 → WF2 → WF3 → WF4 for enabled stages. WF1 and WF3 are
independent prerequisites of WF4. WF0 can run alone when selecting historical forcing; WF2 is
optional and never drives WF3. Use the [running guide](docs/guide/running.md) for single-workflow
commands, dry runs, experiment selection, logs, and recovery. WF3 and WF4 use their owned runners.

## Configure your own basin

The maintained starter is [`config/templates/example-basin/`](config/templates/example-basin/README.md).
Its project file and five workflow files are scaffolded by `scripts/create_case.py`; the
[configuration guide](docs/guide/configuration.md) explains path resolution and basin, climate,
model, and experiment settings. Keep production case configurations and output roots outside this
checkout. The [running guide](docs/guide/running.md#create-an-external-case) shows the scaffolder
and the order for enabling workflows.

## Documentation and development

- [Documentation map](docs/README.md) — guide, site, notebooks, and offline references.
- [Scientific approach](docs/site/scientific-approach/overview.qmd) — method and interpretation.
- [Toolbox reference](docs/site/toolbox-reference/overview.qmd) — workflow and retained-output contracts.
- [Development reference](dev/reference/README.md) — current maintainer practices and architecture.
- [Changelog](CHANGELOG.md) — release history.

## License

Copyright (c) 2021, Deltares. Licensed under the
[GNU General Public License, version 3 or later](LICENSE).
