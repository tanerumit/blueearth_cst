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

1. Follow [Windows installation](docs/guide/install.md) for Pixi and juliaup-managed Julia.
2. Check your project's data catalogs. Installation does not supply the external datasets;
   the example expects Deltares P-drive access and CMIP6 network access.
3. Use the [quick start](docs/guide/quick-start.md) to preview/run the rapid example and find its results.
   It is an execution example, not a numerical assessment baseline or a promise of a short runtime.

## Run your own assessment

[Create an external case](docs/guide/new-case.md) from the single maintained starter.
Then [choose settings](docs/guide/configuration.md), [run/resume](docs/guide/running.md),
[select indicators](docs/guide/indicators.md) and [read the output tables](docs/guide/outputs.md).
Keep production cases and outputs outside this checkout.

WF0 compares historical forcing without a model. WF1 builds the model and WF3 generates independent
climate series; both supply WF4 simulation. WF2 provides projection plausibility context and never
selects or weights the scenario-neutral grid.

## Documentation and development

- [Documentation map](docs/README.md): user guide, technical manual and optional notebooks.
- [Scientific approach](docs/site/scientific-approach/overview.qmd): existing methods and interpretation.
- [Technical manual](docs/technical-manual/overview.md): workflow/retained-output contracts and extension.
- [Development reference](dev/reference/README.md): current maintainer practices and architecture.
- [Changelog](CHANGELOG.md): release history.

## License

Copyright (c) 2021, Deltares. Licensed under the
[GNU General Public License, version 3 or later](LICENSE).
